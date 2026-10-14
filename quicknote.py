"""Quicknote: a shorthand for transcribing a page by eye, one line per bar, into MusicXML.

    # comment
    @title Interstellar - Main Theme
    @composer Hans Zimmer
    @time 3/4
    @tempo 100
    @key 0
    38 | A4/s E4 C5 E4 B4 E4 D5 E4 C5 E4 A4 E4 | - | A3/q B3 C4
    41 | ...                                    | - | B3/dh~

Each bar line is `number | upper voice | lower voice | left hand`; a `-` layer is a rest for the
whole bar. Tokens: `C5/q` (pitch/duration), `r/h` (rest), `F2+F3/dh` (chord), and a trailing `~`
ties into the next bar. A duration carries forward until the next one is given. Durations:
s=16th, e=8th, q=quarter, h=half, w=whole; a `.` after the letter dots it (q. h.); dh = h.
A layer may start with `8va `, `15ma ` or `8vb ` to shift it, as the page marks it.
Between bars, `@time 12/8`, `@lhclef treble`, `@rhclef bass`, `@tempo 90` apply from the next bar.
Bars missing from the file are whole-bar rests in every layer.

    python quicknote.py piece.qn out.musicxml
"""
import re
import sys

import music21 as m

DUR = {"s": 0.25, "e": 0.5, "q": 1.0, "h": 2.0, "w": 4.0, "dh": 3.0}


def parse_dur(code: str) -> float:
    dotted = code.endswith(".")
    base = DUR[code.rstrip(".")]
    return base * 1.5 if dotted else base


def shift(pitch: str, octaves: int) -> str:
    mt = re.fullmatch(r"([A-G][#b]?)(-?\d)", pitch)
    if not mt:
        raise ValueError(f"bad pitch {pitch!r}")
    return f"{mt.group(1)}{int(mt.group(2)) + octaves}"


def parse_layer(text: str, bar_len: float):
    text = text.strip()
    if text in ("", "-"):
        return [(None, bar_len, False)]
    octaves = 0
    for prefix, k in (("8va ", 1), ("15ma ", 2), ("8vb ", -1)):
        if text.startswith(prefix):
            octaves, text = k, text[len(prefix):]
    out, dur = [], None
    for tok in text.split():
        tie = tok.endswith("~")
        tok = tok.rstrip("~")
        if "/" in tok:
            tok, d = tok.split("/")
            dur = parse_dur(d)
        if dur is None:
            raise ValueError(f"no duration yet for {tok!r} in {text!r}")
        pitches = None if tok == "r" else [shift(p, octaves) for p in tok.split("+")]
        out.append((pitches, dur, tie))
    total = sum(d for _, d, _ in out)
    if abs(total - bar_len) > 1e-6:
        raise ValueError(f"layer adds to {total}, bar is {bar_len}: {text!r}")
    return out


def element(pitches, dur):
    if pitches is None:
        return m.note.Rest(quarterLength=dur)
    if len(pitches) == 1:
        return m.note.Note(pitches[0], quarterLength=dur)
    return m.chord.Chord(pitches, quarterLength=dur)


def build(path: str) -> m.stream.Score:
    meta = {"time": "4/4", "tempo": "90", "key": "0", "title": "Untitled", "composer": ""}
    bars = {}
    changes = {}  # bar number -> {"time": "12/8", "lhclef": "treble", ...}, from @ lines between bars
    pending = {}
    for raw in open(path, encoding="utf-8"):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("@"):
            k, _, v = line[1:].partition(" ")
            if bars:
                pending[k] = v.strip()   # a change: applies from the next bar line
            else:
                meta[k] = v.strip()
            continue
        num, *layers = [p.strip() for p in line.split("|")]
        if len(layers) != 3:
            raise ValueError(f"bar line needs 3 layers: {line!r}")
        bars[int(num)] = layers
        if pending:
            changes[int(num)] = pending
            pending = {}
    time_sig = meta["time"]
    score = m.stream.Score()
    score.insert(0, m.metadata.Metadata(title=meta["title"], composer=meta["composer"]))
    rh, lh = m.stream.Part(id="RH"), m.stream.Part(id="LH")
    tied_open = {0: set(), 1: set(), 2: set()}  # layer -> pitches tied from the previous bar
    for b in range(1, max(bars) + 1):
        layers = bars.get(b, ["-", "-", "-"])
        mr, ml = m.stream.Measure(number=b), m.stream.Measure(number=b)
        ch = changes.get(b, {})
        if "time" in ch:
            time_sig = ch["time"]
            for mm in (mr, ml):
                mm.insert(0, m.meter.TimeSignature(time_sig))
        for side, mm in (("rhclef", mr), ("lhclef", ml)):
            if side in ch:
                mm.insert(0, m.clef.TrebleClef() if ch[side] == "treble" else m.clef.BassClef())
        if "tempo" in ch:
            mr.insert(0, m.tempo.MetronomeMark(number=float(ch["tempo"])))
        n, d = (int(x) for x in time_sig.split("/"))
        bar_len = n * 4.0 / d
        if b == 1:
            mr.insert(0, m.clef.TrebleClef()); ml.insert(0, m.clef.BassClef())
            for mm in (mr, ml):
                mm.insert(0, m.key.KeySignature(int(meta["key"])))
                mm.insert(0, m.meter.TimeSignature(meta["time"]))
            mr.insert(0, m.tempo.MetronomeMark(number=float(meta["tempo"])))
        for li, text in enumerate(layers):
            seq = parse_layer(text, bar_len)
            if li == 2:
                target = ml
            else:
                if li == 1 and text.strip() == "-":
                    continue  # no lower voice this bar
                target = m.stream.Voice(id=str(li + 1))
            incoming, outgoing = tied_open[li], set()
            for i, (pitches, dur, tie) in enumerate(seq):
                el = element(pitches, dur)
                key = tuple(pitches) if pitches else None
                starts, stops = tie, (i == 0 and key in incoming)
                if starts and stops:
                    el.tie = m.tie.Tie("continue")
                elif starts:
                    el.tie = m.tie.Tie("start")
                elif stops:
                    el.tie = m.tie.Tie("stop")
                if tie and key:
                    outgoing.add(key)
                target.append(el)
            tied_open[li] = outgoing
            if li < 2:
                mr.insert(0, target)
        rh.append(mr); lh.append(ml)
    score.insert(0, rh); score.insert(0, lh)
    return score


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    build(src).write("musicxml", fp=dst)
    print("wrote", dst)

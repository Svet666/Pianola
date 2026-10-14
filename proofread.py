"""Proofread oemer's MusicXML: keep its pitches, repair its rhythm.

oemer (the eyes) finds notes and pitches well on clean engraving, but its rhythm drifts:
missed dots, phantom rests, voices that don't fill the bar, no time signature. This pass
trusts the page's facts that Andrew reads by eye (time signature, tempo) and makes every
voice of every bar add up to exactly one bar.

    python proofread.py in.musicxml out.musicxml --time 3/4 --tempo 100 --title "..."

Rules, per voice per bar: an all-rest voice becomes one whole-bar rest; durations snap to
real note values; a short voice stretches its longest note, a long one trims it; offsets
are laid out again in order. Pitches are never changed here: fixing those is a by-eye job.
"""
import argparse
import copy

import music21 as m

SNAP = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]


def snap(q: float) -> float:
    return min(SNAP, key=lambda s: abs(s - q))


def fix_voice(elems, bar: float):
    elems = sorted(elems, key=lambda e: e.offset)
    if not elems or all(e.isRest for e in elems):
        return [m.note.Rest(quarterLength=bar)]
    out = []
    for e in elems:
        c = copy.deepcopy(e)
        c.quarterLength = min(snap(float(e.quarterLength)), bar)
        out.append(c)
    total = sum(float(c.quarterLength) for c in out)
    while abs(total - bar) > 1e-6:
        notes = [c for c in out if not c.isRest] or out
        longest = max(notes, key=lambda c: float(c.quarterLength))
        if total < bar:
            longest.quarterLength = float(longest.quarterLength) + (bar - total)
        else:
            excess = total - bar
            if float(longest.quarterLength) > excess:
                longest.quarterLength = float(longest.quarterLength) - excess
            else:
                out.remove(longest)
        total = sum(float(c.quarterLength) for c in out)
    return out


def proofread(src: str, dst: str, time: str, tempo: int, title: str | None):
    s = m.converter.parse(src)
    num, den = (int(x) for x in time.split("/"))
    bar = num * 4.0 / den
    score = m.stream.Score()
    if title:
        score.insert(0, m.metadata.Metadata(title=title))
    for pi, part in enumerate(s.parts):
        newp = m.stream.Part(id=f"P{pi + 1}")
        for i, meas in enumerate(part.getElementsByClass("Measure")):
            nm = m.stream.Measure(number=i + 1)
            if i == 0:
                clef = meas.getContextByClass(m.clef.Clef) or (m.clef.TrebleClef() if pi == 0 else m.clef.BassClef())
                nm.insert(0, copy.deepcopy(clef))
                key = meas.getContextByClass(m.key.KeySignature)
                nm.insert(0, copy.deepcopy(key) if key else m.key.KeySignature(0))
                nm.insert(0, m.meter.TimeSignature(time))
                if pi == 0:
                    nm.insert(0, m.tempo.MetronomeMark(number=tempo))
            voices = list(meas.voices) or [meas]
            for vi, v in enumerate(voices):
                fixed = fix_voice(list(v.notesAndRests), bar)
                nv = m.stream.Voice(id=str(vi + 1))
                off = 0.0
                for e in fixed:
                    nv.insert(off, e)
                    off += float(e.quarterLength)
                nm.insert(0, nv)
            newp.append(nm)
        score.insert(0, newp)
    score.write("musicxml", fp=dst)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--time", default="4/4"); ap.add_argument("--tempo", type=int, default=90)
    ap.add_argument("--title")
    a = ap.parse_args()
    proofread(a.src, a.dst, a.time, a.tempo, a.title)
    print("wrote", a.dst)

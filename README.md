# The Pianola

A player piano for sheet music. It started (2026-10-12) as a way to hear a family collection
of sheet music again: Lana's late father-in-law's. Photograph a page, turn it into MusicXML,
and the Pianola plays it.

## The player

- `template.html` is the player: it reads MusicXML (parts, voices, chords, ties, tempo) and plays it
  with real piano samples.
- `build.py [score.musicxml] [out.html]` bakes the samples and a score into one self-contained HTML
  file. With no arguments, it builds the demo.
- `make_prelude.py` writes the demo: Bach's Prelude in C, BWV 846 (public domain).

## The eyes: a page goes in, MusicXML comes out

1. **Draft:** [oemer](https://github.com/BreezeWhite/oemer) (optical music recognition) reads a page
   image: `oemer page.png -o .`
2. **Repair the rhythm:** `proofread.py draft.musicxml out.musicxml --time 3/4 --tempo 100` makes every
   voice of every bar add up to exactly one bar (oemer's rhythm drifts).
3. **Proofread by eye** against the page, then play it.

What oemer does well and badly, measured on 2026-10-14: on clean engraving (Bach) it found every
note (252/252) and 92% of pitches; it misses accidentals, drifts on rhythm, and on a real
arrangement it read most bass half notes as rests. So it drafts, and a reader checks.

Setup notes (Windows, Python 3.12): `pip install oemer music21 verovio`, then pin
`onnxruntime==1.20.1` (the GPU build and newer versions reject oemer's model). Newer OpenCV returns
Hough lines as `(N, 4)`, so oemer's `bbox.find_lines` needs `line = np.asarray(line).reshape(-1)[:4]`.

## Taking page photos

Flat page, even light without glare, phone straight overhead and parallel to the page, the whole
staff system in frame. A scan at 200-300 dpi is ideal.

## Credits

- Grand piano: [Salamander Grand Piano](https://archive.org/details/SalamanderGrandPianoV3) by
  Alexander Holm, [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/). The files in
  `samples/` are a subset of it, as mp3.
- Engraving checks: [Verovio](https://www.verovio.org). Analysis: [music21](https://web.mit.edu/music21/).

Scores you photograph stay in `scans/`, which git ignores: copyrighted arrangements and family pages
never belong in this repo.

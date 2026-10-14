# The Pianola

A player piano for sheet music, made for Lana's late father-in-law's collection (2026-10-12).

- `template.html` is the player: it reads MusicXML and plays it with the piano samples in `samples/`.
- `build.py` bakes the samples and a demo score into one self-contained `pianola.html` (not committed, since it's generated).
- `make_prelude.py` writes the demo, Bach's Prelude in C (public domain), as MusicXML.

Next: **the eyes**. A page photo goes in and MusicXML comes out (optical music recognition), then Andrew checks it against the page and the Pianola plays it.

Pages from the collection live in `scans/` (git-ignored): they're family, not repo material.

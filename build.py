import base64, json, pathlib
here = pathlib.Path(__file__).parent
names = "A0 C1 Ds1 Fs1 A1 C2 Ds2 Fs2 A2 C3 Ds3 Fs3 A3 C4 Ds4 Fs4 A4 C5 Ds5 Fs5 A5 C6 Ds6 Fs6 A6 C7 Ds7 Fs7 A7 C8".split()
pc = {"C":0,"Ds":3,"Fs":6,"A":9}
def midi(n): return (int(n[-1]) + 1) * 12 + pc[n[:-1]]
samples = {midi(n): base64.b64encode((here/"samples"/f"{n}.mp3").read_bytes()).decode() for n in names}
html = (here/"template.html").read_text(encoding="utf-8")
html = html.replace("__SAMPLES__", json.dumps(samples)).replace("__DEMO__", json.dumps((here/"bach-prelude-c.musicxml").read_text(encoding="utf-8")))
(here/"pianola.html").write_text(html, encoding="utf-8"); print(round(len(html)/1e6,2), "MB")

# Bach, Prelude in C major BWV 846, measures 1-19 + a closing chord, as MusicXML (public domain).
M = """C4 E4 G4 C5 E5|C4 D4 A4 D5 F5|B3 D4 G4 D5 F5|C4 E4 G4 C5 E5|C4 E4 A4 E5 A5|C4 D4 F#4 A4 D5|B3 D4 G4 D5 G5|B3 C4 E4 G4 C5|A3 C4 E4 G4 C5|D3 A3 D4 F#4 C5|G3 B3 D4 G4 B4|G3 Bb3 E4 G4 C#5|F3 A3 D4 A4 D5|F3 Ab3 D4 F4 B4|E3 G3 C4 G4 C5|E3 F3 A3 C4 F4|D3 F3 A3 C4 F4|G2 D3 G3 B3 F4|C3 E3 G3 C4 E4""".split("|")
def pitch(n):
    step, rest = n[0], n[1:]; alter = 0
    if rest[0] == '#': alter, rest = 1, rest[1:]
    elif rest[0] == 'b': alter, rest = -1, rest[1:]
    a = f"<alter>{alter}</alter>" if alter else ""
    return f"<pitch><step>{step}</step>{a}<octave>{rest}</octave></pitch>"
TYPES = {1:"16th",2:"eighth",3:"eighth",4:"quarter",8:"half",16:"whole"}
def note(n, dur, voice, staff, chord=False, tie=None, rest=False):
    dot = "<dot/>" if dur == 3 else ""
    t = ""
    if tie: t = "".join(f'<tie type="{x}"/>' for x in tie)
    nt = "".join(f'<tied type="{x}"/>' for x in tie) if tie else ""
    body = "<rest/>" if rest else pitch(n)
    return (f"<note>{'<chord/>' if chord else ''}{body}<duration>{dur}</duration>{t}<voice>{voice}</voice>"
            f"<type>{TYPES[dur]}</type>{dot}<staff>{staff}</staff>{'<notations>'+nt+'</notations>' if nt else ''}</note>")
def staff_of(n): return 1 if int(n[-1]) >= 4 and n[:1] != 'B' or int(n[-1]) >= 5 else 2
out = []
for i, m in enumerate(M, 1):
    n1, n2, n3, n4, n5 = m.split()
    x = [f'<measure number="{i}">']
    if i == 1:
        x.append('<attributes><divisions>4</divisions><key><fifths>0</fifths></key><time><beats>4</beats><beat-type>4</beat-type></time>'
                 '<staves>2</staves><clef number="1"><sign>G</sign><line>2</line></clef><clef number="2"><sign>F</sign><line>4</line></clef></attributes>'
                 '<direction placement="above"><direction-type><words>Moderato</words></direction-type><sound tempo="66"/></direction>')
    for half in range(2):
        x.append(note(n1, 8, 1, 2))
        x.append('<backup><duration>8</duration></backup>')
        x.append(note(None, 1, 2, 2, rest=True)); x.append(note(n2, 3, 2, 2, tie=["start"])); x.append(note(n2, 4, 2, 2, tie=["stop"]))
        x.append('<backup><duration>8</duration></backup>')
        x.append(note(None, 2, 3, 1, rest=True))
        for n in (n3, n4, n5, n3, n4, n5): x.append(note(n, 1, 3, 1))
    x.append('</measure>'); out.append("".join(x))
out.append('<measure number="20">' + note("C3", 16, 1, 2) + note("C4", 16, 1, 2, chord=True) + '<backup><duration>16</duration></backup>'
           + note("E4", 16, 3, 1) + note("G4", 16, 3, 1, chord=True) + note("C5", 16, 3, 1, chord=True) + '<barline location="right"><bar-style>light-heavy</bar-style></barline></measure>')
xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n'
       '<score-partwise version="4.0"><work><work-title>Prelude in C major, BWV 846</work-title></work>'
       '<identification><creator type="composer">Johann Sebastian Bach</creator></identification>'
       '<part-list><score-part id="P1"><part-name>Piano</part-name></score-part></part-list><part id="P1">' + "".join(out) + '</part></score-partwise>\n')
open("bach-prelude-c.musicxml", "w", encoding="utf-8").write(xml); print(len(xml), "bytes")

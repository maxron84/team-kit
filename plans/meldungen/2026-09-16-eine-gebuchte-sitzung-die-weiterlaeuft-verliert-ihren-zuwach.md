# Eine gebuchte Sitzung, die weiterlaeuft, verliert ihren Zuwachs lautlos - und wird zur teuersten Zeile des Projekts

- **Bezug**: BL-80
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst
  plus Electron-Oberfläche, rund 1000 Tests, 23 gebaute Kaskaden, Ledger mit
  79 Zeilen über acht Wochen. Auth durchgehend Abo, Modelle `sonnet` für die
  Loop-Rollen und `opus` für Architekt und Forensiker.

## Was passiert ist

Der Kostenabschluss misst eine Sitzung **an ihrem Transkript**, und das
Transkript kennt keinen Schnitt: Es wächst weiter, solange das Fenster offen
ist. Wer am Ende eines Closeouts bucht und danach **im selben Fenster**
weiterarbeitet, erzeugt eine Lücke, die kein Werkzeug meldet.

**Vier gemessene Fälle aus diesem Projekt, alle nach demselben Muster:**

| Kaskade | gemessen | bereits gebucht | **nie im Ledger** |
|---|---|---|---|
| K23 | 76,3394 | 9,4989 | **66,8405** |
| K18 (a) | 39,4740 | 12,8224 | **26,6516** |
| K18 (b) | 20,7386 | 17,4638 | **3,2748** |
| Feld (`BL-165`) | — | — | **43,90** (zwei Sitzungen) |

Der größte Fall ist zugleich der lehrreichste: Die Aushärtung von K23 lief in
**derselben** Sitzung wie der Closeout von K22. Die Sitzung war beim
K22-Closeout mit 9,4989 gebucht und lief danach noch stundenlang weiter — die
gesamte Planungsarbeit einer Kaskade, **66,84 USD**, stand nie im Ledger.

**Nichts zeigt darauf hin.** Das Ledger ist in sich stimmig,
`--ledger-pruefen` schweigt (für eine interaktive Sitzung gibt es keinen
Rohlog), `--budget` zeigt eine plausible Summe. Sichtbar wird die Lücke nur,
wenn jemand von sich aus die Transkript-Ablage gegen das Ledger hält — eine
Gegenprobe, die keine Regel verlangt.

**Die zweite Hälfte derselben Lage: Diese Sitzungen sind die teuersten des
Projekts.** Eine einzige lange Architekten-Sitzung hat hier **118,99 USD**
gekostet — 539 Antworten, 152,3 Mio. Cache-Read-Token. Sie hatte den
K16-Closeout gebucht (7,2269) und danach weitergearbeitet: K17-Aushärtung,
Begleitung von fünf Vollautomatik-Anläufen, Nacharbeit. Zusammen **111,77 USD**
für eine Kaskade, deren Bau plus Rollen **40,07 USD** kostete — **Faktor 2,8**.

## Wo es steckt

- `team/tools/kosten.py`, Verb `sitzung-messen` — misst den **Ist-Stand** des
  Transkripts, ohne zu wissen, dass daraus schon einmal gebucht wurde.
- `team/tools/kosten.py`, Verben `architekt-abschluss`/`akteur-abschluss` —
  schreiben den Betrag, halten aber **nicht fest, aus welchem Transkript** er
  stammt. Die Zuordnung existiert nur als Prosa in der Notiz, von Hand
  geschrieben.
- `team/prompts/rolle-architekt.md` — trägt die Regel *„nach einem gebuchten
  Closeout eine NEUE Sitzung für die nächste Kaskade"*. Sie ist richtig und
  reicht nicht.

## Warum das jede Installation trifft

Die Regel ist genau gegen diesen Fall geschrieben — und sie hat im Feld an
**einem Tag zweimal** nicht gegriffen, bei jemandem, der sie kannte und
wörtlich zitieren konnte. Das ist kein Nachlässigkeitsproblem, sondern ein
Bauformproblem: **Ein Closeout hat einen Auslöser, das Weiterarbeiten hat
keinen.** In dem Moment, in dem gerade gebucht wurde und die nächste Frage
schon dasteht, liest niemand mehr eine Regel.

Jede Installation, die den dokumentierten Weg geht — Closeout buchen, dann
weitermachen —, erzeugt diese Lücke. Sie trifft ausgerechnet die **teuerste**
Rolle und wächst still über Kaskaden hinweg.

## Was vorgeschlagen wird

**Drei Bausteine. Der dritte ist der eigentliche Fix, die ersten beiden sind
billig und wirken sofort.**

1. **Der Kostenabschluss sagt am Ende selbst, was jetzt gilt.** Nach einer
   erfolgreichen Buchung eine Zeile: *„Diese Sitzung ist abgerechnet — für die
   nächste Kaskade eine neue öffnen. Wird hier weitergearbeitet, ist der
   Zuwachs nachzubuchen."* Die Regel steht damit an der Stelle, an der sie
   gebraucht wird, statt in einem Briefing, das in diesem Moment niemand liest.
2. **`sitzung-messen` warnt, wenn eine Sitzung groß geworden ist** — etwa ab
   300 Antworten oder 50 Mio. Cache-Read-Token. Beide Zahlen liegen in der
   Messung ohnehin vor; der 118,99-USD-Fall hätte die Schwelle deutlich
   gerissen.
3. **Das Werkzeug merkt sich, aus welchem Transkript eine Buchung stammt, und
   bietet die Differenz von sich aus an.** Heute steht die Zuordnung nur als
   Prosa in der Notiz (*„Sitzung 9afe0f45 misst jetzt 76,3394 gegen 9,4989
   bereits gebucht"*) — von Hand geschrieben, von keinem Werkzeug lesbar.
   Steht die Transkript-Kennung als **Feld** in der Ledger-Zeile, kann
   `sitzung-messen` beim nächsten Lauf über dasselbe Transkript sagen:
   *„Aus diesem Transkript sind bereits 9,4989 gebucht (Kaskade 22). Differenz:
   66,8405. Mit `--addieren` nachbuchen."*

**Damit wird aus einer Gewissenhaftigkeitsregel eine Rechnung**, und die Lücke
kann nicht mehr unbemerkt entstehen — das Werkzeug kennt beide Zahlen bereits,
es legt sie nur nicht nebeneinander.

> **Zur Reihenfolge:** Baustein 3 braucht ein neues Feld im Ledger-Format.
> Falls die Meldung *„Der Ledger bucht Dollar, gemessen werden Token"* (selbes
> Projekt, 2026-09-16) aufgegriffen wird, gehören beide Feldergänzungen in
> **einen** Formatschritt — und dann trägt die Format-/Versionsmarke je Zeile,
> die dort vorgeschlagen ist, auch diese hier.

## Was ich schon versucht habe

Lokal ist nichts gebaut; der Fehler sitzt in `team/` und würde beim nächsten
`--update` überbügelt.

Gearbeitet wird hier bis auf Weiteres mit einem **Handverfahren**, und das ist
der Beleg dafür, wie teuer der fehlende Baustein ist: Vor jedem Buchen die
Transkript-Ablage nach Änderungszeit sortieren, jedes Transkript im Zeitfenster
der Kaskade **einzeln** messen, gegen alles halten, was daraus schon gebucht
wurde, und die Differenz mit `--addieren` nachbuchen. `--alle` ist die
Abkürzung, nennt aber keine Einzelwerte — für die Differenzrechnung braucht es
die Einzelmessung.

Gefunden wurden die 3,2748 USD des kleinsten Falls **nur** durch diese
Gegenprobe. Niemand schreibt sie vor.

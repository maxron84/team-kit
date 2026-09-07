# zitat_lint.py kennt nur BL-Nummern - Fund- und Aktenzitate (HM-, AX-) veralten unsichtbar

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python plus
  Electron-Oberfläche; elf gebaute Kaskaden, rund 460 Tests, knapp 50 Funde im
  Beutebuch.

## Was passiert ist

Im Closeout einer Kaskade fand ich eine Skizze in der Roadmap, die eine
**harte Vorbedingung** mit drei Fund-Nummern begründet:

```
- **Vorbedingung, hart**: `HM-44`, `HM-45` und `HM-46` müssen erledigt sein.
  Solange sie offen sind, ist jeder parallele Lauf rot, und ein roter
  Verifikationsbefehl legt den ganzen Loop still.
```

Alle drei Funde waren in der Fixphase derselben Kaskade erledigt worden, wenige
Stunden zuvor. Die Skizze beschrieb also eine Sperre, die es nicht mehr gab —
genau der Fehlermodus, gegen den `zitat_lint.py` gebaut wurde.

`python3 team/tools/zitat_lint.py` meldete diesen Fall **nicht**. Es meldete
fünf andere Befunde, alle korrekt erkannt und alle mit `BL-`Nummern.

## Wo es steckt

`team/tools/zitat_lint.py`, das Referenzmuster:

```python
REFERENZ_RE = re.compile(r"(?<!Kit-)\bBL-(\d+)\b")
```

Das Werkzeug liest ausschließlich den Backlog als Statusquelle und erkennt
ausschließlich `BL-<N>` als Zitat. Das **Beutebuch** (`HM-<N>`) und die
**Ermittlungsakten** (`AX-<N>`) sind ihm unbekannt, obwohl beide dieselbe
Statuskette führen (`offen → an Frank übergeben → … → erledigt`), im selben
Plan-Ordner liegen und in Plänen und Skizzen genauso als offene Frage zitiert
werden. Für das Beutebuch existiert mit `team/tools/beutebuch.py` sogar bereits
ein Statusleser, den der Lint benutzen könnte.

## Warum das jede Installation trifft

Der Fehler steckt in `team/tools/`, also im Kit selbst, und die Rollenverteilung
macht ihn systematisch: Das Kit trennt Aufgaben (Backlog) von Funden
(Beutebuch), lässt aber nur die eine Hälfte prüfen. **Ein Fund ist dabei die
wahrscheinlichere Sperre**, weil er den Loop stilllegt (roter
Verifikationsbefehl), während ein Backlog-Eintrag meist nur eine Idee ist — und
Fund-Zitate veralten schneller, weil eine einzige Fixphase mehrere Funde in
einer Nacht erledigt. Die Pflichtzeile der Closeout-Regel („Welche offenen
Punkte hat dieser Lauf nebenbei eingelöst — und wer zitiert sie?") zielt
ausdrücklich auf beides; das Werkzeug, das sie maschinell gegenprüft, deckt nur
den Backlog ab.

Dass der Lint absichtlich schmal gehalten ist („meldet lieber einen Fall zu
wenig"), spricht nicht dagegen: Hier fehlt keine Heuristik, sondern eine ganze
Quelle.

## Was ich schon versucht habe

Nichts lokal gepatcht — ein Patch am Kit-Code hätte hier eine Verfallszeit bis
zum nächsten Update, und die Ursache ist kein Konfigurationswert, sondern eine
fehlende Quelle.

Vorschlag, falls er hilft: dasselbe Muster wie beim Backlog, nur mit einem
zweiten Präfix-Paar und dem vorhandenen Beutebuch-Leser als Statusquelle —
`HM-<N>` gegen das Beutebuch, `AX-<N>` gegen den Aktenordner, `Kit-HM-`
analog zu `Kit-BL-` ausgeschlossen. Die bestehende Zurückhaltung des Werkzeugs
(nur Zukunftsform, Rückblicke fallen heraus) trägt dabei unverändert.

# Eine planmaessig abgebrochene Stufe ist vom vierten Ausgang nicht zu unterscheiden

- **Bezug**: BL-78
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst
  plus Electron-Oberfläche, rund 1000 Tests, 23 gebaute Kaskaden.

## Was passiert ist

Eine Stufe dieses Projekts trug eine im Plan **ausgeschriebene
Abbruchbedingung**: Bleibt nach den Vorstufen auch nur eine rote Stelle, wird
die Umstellung des Verifikationsbefehls **nicht** genommen.

Genau das trat ein. Ralph hat sich vorbildlich verhalten:

- gemessen (drei Läufe, zwei davon rot),
- die Konfiguration **unangetastet** gelassen,
- den Befund in den `[Unreleased]`-Block eingetragen,
- committet,
- und **regelkonform kein Promise gegeben** — die Stufe wurde ja nicht
  abgeschlossen, sondern planmäßig abgebrochen.

**Die Schleife druckt daraufhin den vollen Bericht des vierten Ausgangs**
(Exit 43): die Prüfkette für den Menschen, die Warnung, ein Neulauf werfe
bezahlte Arbeit weg, die Frage, ob der Baum grün sei. **Kein einziger dieser
Sätze trifft zu.** Die Stufe ist nicht *„fertig, nur die Quittung fehlt"* —
sie ist *„planmäßig nicht genommen"*, und diese Lage kennt das Werkzeug nicht.

**Der Nebenbefund ist derselbe Fehler eine Ebene tiefer:** Die von der Schleife
vorgeschlagene Abhilfe — die nächste Stufennummer von Hand in die Zustandsdatei
schreiben — war hier zufällig richtig, aber aus dem falschen Grund. Sie führt
über den gesetzten Cap hinaus und macht die Bauphase damit zum No-Op. Wer dem
Vorschlag folgt, bekommt ein Ergebnis, das aussieht wie ein sauberer
Durchlauf.

## Wo es steckt

- `pwsh/entry/ralph.ps1`:121 — die Quittungsprüfung kennt genau **eine**
  gültige Quittung: `STUFE_<n>_COMPLETE`.
- `pwsh/entry/ralph.ps1`:183 — der Exit-43-Zweig, der jede fehlende Quittung
  als vierten Ausgang deutet.
- `pwsh/lib.psm1`, `team_quittung_selbstpruefung` — die Selbstprüfung, die seit
  `BL-110` vor dem Exit 43 läuft.
- dieselbe Stelle auf der bash-Bahn.

**Die Selbstprüfung macht die Lage inzwischen nicht besser, sondern
zweideutig** (gelesen an 2.13.1, nicht in einem Lauf nachgestellt):

| Prüfung | bei einer planmäßig abgebrochenen Stufe |
|---|---|
| (1) *Hat die Sitzung Arbeit hinterlassen?* | **ja** — es gibt einen Commit der Stufe |
| (2) *Gibt es eine Zusicherung, also eine berührte Testdatei?* | **in der Regel nein** — die Stufe hat gemessen und dokumentiert, nicht gebaut |

Damit fällt die Selbstprüfung durch und der Lauf landet im Exit 43 — mit einer
Begründung (*„Produktivcode ohne Zusicherung"*), die ebenfalls nicht zutrifft.
**Der Mensch bekommt also in beiden Zweigen eine falsche Diagnose.** Und eine
abgebrochene Stufe, die zufällig doch eine Testdatei angefasst hat, würde von
der Selbstprüfung sogar **still als abgeschlossen durchgewunken** — dann wandert
der Zustand weiter, obwohl die Stufe ihre Arbeit bewusst nicht getan hat.

## Warum das jede Installation trifft

**Abbruchbedingungen sind ein reguläres Planungsmittel**, kein Sonderfall
dieses Projekts: *„Stelle nur um, wenn der Vorlauf sauber ist"*, *„nimm die
Optimierung nur, wenn die Messung sie trägt"*. Das Architekten-Briefing
ermutigt genau dazu, indem es verlangt, vor jedem Stufenschnitt zu fragen,
womit die Zusicherung rot wird.

Dem Loop fehlt für das Ergebnis dieser Frage aber die Vokabel. Es gibt
**Promise** oder **kein Promise** — und *kein Promise* ist mit dem teuersten
Bericht des Werkzeugs belegt.

**Und dadurch stumpft der Bericht ab.** Der vierte Ausgang ist die Meldung, die
den Menschen zu einer Prüfkette auffordert und ihn warnt, bezahlte Arbeit nicht
wegzuwerfen. Wird sie bei einem **geordneten** Abschluss gedruckt, lernt der
Leser, sie wegzuklicken — und beim nächsten echten Fall tut er es auch.

## Was vorgeschlagen wird

**Eine zweite Quittungsform für „planmäßig nicht genommen".**

```
<promise>STUFE_<n>_UEBERSPRUNGEN</promise>
```

Sie verhält sich wie die bestehende Quittung — Zustand weiterschalten, weiter
mit der nächsten Stufe —, druckt aber einen eigenen, **ruhigen** Abschlusstext:
*„Stufe n planmäßig nicht genommen; Grund siehe Commit."* Kein Prüfkatalog,
keine Warnung, kein Exit 43.

Dazu drei Kleinigkeiten, die verhindern, dass die neue Form zum Schlupfloch
wird:

1. **Sie gilt nur, wenn der Plan sie vorsieht.** Die Rolle darf sie nicht aus
   eigenem Ermessen geben — das Briefing formuliert sie als *„wenn die im
   Plan ausgeschriebene Abbruchbedingung eingetreten ist"*.
2. **Sie verlangt einen Commit mit Begründung.** Ohne Arbeitsspur ist es kein
   geordneter Abbruch, sondern eine Stufe, die nie angefangen hat — und dafür
   gibt es die bestehende Meldung.
3. **Der Abschlussbericht zählt sie getrennt.** *„5 Stufen: 4 genommen, 1
   planmäßig übersprungen"* — sonst liest sich ein Bogen mit Abbruch wie ein
   vollständiger.

**Die Abhilfe-Zeile im Exit-43-Bericht gehört bei der Gelegenheit mitgeprüft:**
Sie schlägt heute die nächste Stufennummer vor, ohne den Cap zu kennen. Liegt
die vorgeschlagene Nummer über `RALPH_CAP`, gehört das dazugesagt — sonst
erzeugt der Rat einen stillen No-Op.

## Was ich schon versucht habe

Lokal nichts gebaut: Der Fund sitzt in `pwsh/entry/ralph.ps1` und im
Rollen-Briefing, also im Kit. Ein Patch hier hätte sein Verfallsdatum beim
nächsten `--update` (`BL-42`/`BL-58`).

Behelf im Feld war, den Zustand von Hand weiterzuschalten und den Bericht zu
ignorieren — also genau das Verhalten einzuüben, das bei einem echten vierten
Ausgang teuer wird.

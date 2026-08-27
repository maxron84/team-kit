# Kaskaden-Plandateien heissen ralph-kaskade-N, obwohl sie das ganze Team binden

- **Art**: Verbesserungsvorschlag (Semantik, keine Dringlichkeit)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkuerzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, vierte
  gebaute Kaskade

## Was passiert ist

Kein Fehlverhalten — eine Fehlbenennung, die beim Schreiben der fuenften
Kaskade auffiel. Das Kit gibt der ausgehaerteten Kaskade den Dateinamen
`plans/ralph-kaskade-N-<thema>.md`. Der Name nennt **eine** Rolle, das
Dokument bindet aber **alle**:

- Ralph liest die `## Stufe N`-Bloecke,
- Harry und Marv bekommen ihren Sweep-Fokus aus dem Plankopf,
- Frank arbeitet gegen die Zusicherungen derselben Stufen,
- der Architekt schreibt das Abschluss-Doc gegen den Stufenbogen,
- und der Mensch entscheidet an diesem Dokument, was ueberhaupt gebaut wird.

Der Loop ist der prominenteste Verbraucher, aber nicht der einzige und auch
nicht der, der den Plan definiert.

## Wo es steckt

Der Name steht in den Vorlagen und in den Anleitungen, nicht in der Mechanik —
kein Werkzeug leitet aus dem Praefix etwas ab. Vorkommen im Kit:
`bootstrap/CLAUDE.md.vorlage`, `bootstrap/TEAM.md`,
`bootstrap/roadmap-skizzen.md`, `geteilt/prompts/rolle-architekt.md`,
`bash/entry/ralph.sh`, `bash/entry/team-status.sh`, `bash/install.sh`,
`bash/lib.sh` (jeweils mit pwsh-Gegenstueck) sowie eine Reihe von
`geteilt/tests/test_*`, die den Namen als Beispielwert fuehren.

**Vorschlag:** `plans/team-kaskade-N-<thema>.md`.

## Warum das jede Installation trifft

Der Name steht in `bootstrap/` und in den Rollen-Briefings — jedes neu
angelegte Projekt uebernimmt ihn, und der Architekt jedes Projekts schreibt
ihn bei jeder Aushaertung fort. Es ist keine Wirkung, sondern eine
Bedeutungsverschiebung: Wer den Ordner `plans/` zum ersten Mal sieht, liest
"das ist Ralphs Ablage" statt "das ist der Bauplan des Teams".

## Was ich schon versucht habe

Nichts, bewusst. Die Umbenennung soll **nicht** rueckwirkend in bestehende
Feldprojekte greifen — der Zeiger `.ralph-plan` zeigt dort auf gewachsene
Dateien, und ein Umbenennen im Bestand kostet Aufwand ohne jeden Gegenwert.
Sinnvoll ist der neue Name nur fuer **kuenftige** Projekte, also in
`bootstrap/` und in den Briefings. Bestandsprojekte behalten ihre Dateinamen;
beide Formen duerfen nebeneinander existieren, weil keine Mechanik am Praefix
haengt.

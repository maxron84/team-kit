# Ralphs Added-Eintraege landen nach einem Versionsschnitt unter der alten Version

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-19-ralphs-added-eintraege-landen-nach-einem-versionsschnitt-unt.md
      .\kit-melden.cmd ablegen  2026-11-19-ralphs-added-eintraege-landen-nach-einem-versionsschnitt-unt.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-19-ralphs-added-eintraege-landen-nach-einem-versionsschnitt-unt.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: keins eingetragen — bitte vergeben (dasselbe Projekt wie die Meldung vom 2026-11-02 zu Franks CHANGELOG-Eintrag)
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn; Workflow-XML mit Prüfkette in Python, rund 900 Tests; sechste Kaskade, die vierte nach einer veröffentlichten Version

## Was passiert ist

Dieselbe Bauart wie in der Meldung `2026-11-02-franks-quittung-prueft-den-changelog-eintrag-nicht-drei-von.md`,
diesmal bei Ralph und bei `### Added`. Nach dem Schnitt der Vorversion trug der
`[Unreleased]`-Block nur eine leere Überschrift `### Fixes` — so, wie die
Lehre aus der ersten Meldung es verlangt. Eine Überschrift `### Added` gab es
dort nicht; die erste der Datei stand unter der gerade veröffentlichten
Version.

Eine Vollautomatik mit sieben Baustufen, jede im ersten Versuch, jede mit
„Promise erhalten". Beim Closeout:

- **sechs von sieben** Stufen hatten ihren Added-Eintrag unter
  `## [<Vorversion>]` → `### Added` geschrieben, über die Einträge der
  Vorversion;
- **eine** Stufe hatte gar keinen Eintrag;
- der `[Unreleased]`-Block, den Ralph vor jeder Stufe liest, kannte von den
  sieben Stufen keine.

Kein Werkzeug hat es gemeldet: Ralphs Erfolgsprüfung sieht den CHANGELOG nicht
an, die Vollautomatik meldete sieben abgeschlossene Stufen, und die
Versionsnotizen der Vorversion trugen sechs Funktionen, die es in ihr nicht gibt.
Aufgefallen ist es erst beim Abgleich `[Unreleased]` gegen die Commits im
Closeout.

## Wo es steckt

- `ralph.ps1` (Prompt, Punkt 1) sagt nur, Ralph lese den `[Unreleased]`-Block.
  Dass und wo er einen Added-Eintrag schreibt, sagt weder der Prompt noch
  `team/prompts/rolle-ralph.md`; Ralph tut es aus der Gewohnheit der Datei —
  und sucht dafür die erste Überschrift `### Added`.
- Die Vorlage in `doku/anhang-a.md` (Kopf + leerer `## [Unreleased]`-Block)
  und die Lehre aus der ersten Meldung nennen nur `### Fixes`.
- Ralphs Erfolgsprüfung prüft den CHANGELOG nicht (bei Frank ebenso, erste
  Meldung).

## Warum das jede Installation trifft

Jedes Projekt, das eine Version schneidet und danach weiterbaut, kommt in genau
diese Lage; je sauberer der Schnitt (leerer `[Unreleased]`-Block), desto
sicherer. Der Fehler steckt im Prompt und in der Prüfung des Kits, nicht im
Projekt.

## Was ich schon versucht habe

Im Projekt von Hand behoben: die sechs Einträge zurück in den
`[Unreleased]`-Block unter `### Added`, den fehlenden nachgetragen; beim
nächsten Schnitt bleiben `### Added` und `### Fixes` leer im neuen
`[Unreleased]`-Block stehen. Vorschläge an das Kit:

1. **Prompt:** Ralph schreibt je Stufe genau einen Eintrag unter
   `## [Unreleased]` → `### Added` und legt die Überschrift dort an, wenn sie
   fehlt — nie unter einer Versionsüberschrift.
2. **Prüfung:** Nach jeder Stufe (und nach jedem Frank-Fix) muss der Diff am
   CHANGELOG oberhalb der ersten Versionsüberschrift liegen; sonst Hinweis im
   Lauf und im Abschlussbericht.
3. **Vorlage und Doku:** Der leere `[Unreleased]`-Block trägt beide
   Überschriften, `### Added` und `### Fixes`.

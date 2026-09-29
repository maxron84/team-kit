# Die Scharfschalt-Sequenz bucht die Planungssitzung erst nach dem Start des Laufs - gemessen wird dann ein Rollen-Transkript

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-29-die-scharfschalt-sequenz-bucht-die-planungssitzung-erst-nach.md
      .\kit-melden.cmd ablegen  2026-09-29-die-scharfschalt-sequenz-bucht-die-planungssitzung-erst-nach.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-29-die-scharfschalt-sequenz-bucht-die-planungssitzung-erst-nach.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-11)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Drei Kaskaden sind gelaufen, die vierte ist gerade ausgehärtet.

## Was passiert ist

Noch nichts. Der Fehler fiel beim Schreiben der Scharfschalt-Sequenz für die vierte Kaskade auf,
bevor sie jemand ausgeführt hat.

Das Architekten-Briefing gibt die Sequenz in dieser Reihenfolge vor:
1. Zeiger umlegen
2. Konsistenz-Check
3. Budget
4. Red-Team-Fokus
5. Start
6. als letzter Schritt der Kostenabschluss dieser Sitzung (`sitzung-messen --projekt .`, dann
   `--architekt-abschluss … --kaskade N+1`)

Führt der Mensch die Sequenz von oben nach unten aus, läuft die Vollautomatik in Schritt 5 für
Stunden. In dieser Zeit schreibt jeder headless gefahrene Rollen-Lauf sein Transkript in dieselbe
Ablage wie die Planungssitzung. Das steht im Kommentar zu `BL-251` in `kosten.py`.
`sitzung-messen --projekt .` nimmt danach das **zuletzt geänderte** Transkript, also den letzten
Rollen-Lauf und nicht die Planung.

`BL-251` fängt den Fall ab, aber nur als Warnung: Das Transkript hat genau einen echten
Nutzer-Prompt, und das Werkzeug rät, das Transkript ausdrücklich zu benennen. Gebucht wird dann nicht
falsch, aber auch nicht richtig. Der Mensch muss das Transkript der Planung aus der Ablage heraussuchen,
oder die Planungskosten fallen weg. Genau diesen Verlust soll die Sequenz seit `BL-197` verhindern.

## Wo es steckt

`team/prompts/rolle-architekt.md`, Dreisatz Punkt 3, Absatz „Letzter Schritt der Sequenz,
kopierfertig: der Kostenabschluss DIESER Sitzung" (`BL-197`). Er trifft auf die Auswahl in
`team/tools/kosten.py sitzung-messen --projekt` (das zuletzt geänderte Transkript, `BL-186`).

## Warum das jede Installation trifft

Die Reihenfolge steht im Briefing, das das Kit ausliefert. Jede Architekten-Instanz, die es wörtlich
befolgt, gibt die Buchung hinter dem Start aus. Die Rollen-Läufe schreiben in jeder Installation in
dieselbe Ablage.

## Was ich schon versucht habe

Lokal gibt der Architekt die beiden Buchungsbefehle **vor** dem Zeiger aus, direkt nach dem Commit
des Plans. Zu diesem Zeitpunkt ist die Planungssitzung das zuletzt geänderte Transkript.

Vorschläge fürs Kit, in dieser Reihenfolge:
1. Im Briefing die Buchung an den Anfang der Sequenz stellen, nach dem Commit des Plans und vor dem
   Start, mit dem Grund aus dieser Meldung.
2. `sitzung-messen --projekt .` wählt das jüngste **interaktive** Transkript statt des jüngsten
   überhaupt. Die Unterscheidung dafür gibt es seit `BL-251` schon (Zahl der echten
   Nutzer-Prompts). Dann ist die Reihenfolge egal.

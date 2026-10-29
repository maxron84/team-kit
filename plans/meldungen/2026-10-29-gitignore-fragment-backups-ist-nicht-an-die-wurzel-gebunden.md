# gitignore-Fragment: backups/ ist nicht an die Wurzel gebunden und verschluckt src/**/backups/

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-29-gitignore-fragment-backups-ist-nicht-an-die-wurzel-gebunden.md
      .\kit-melden.cmd ablegen  2026-10-29-gitignore-fragment-backups-ist-nicht-an-die-wurzel-gebunden.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-29-gitignore-fragment-backups-ist-nicht-an-die-wurzel-gebunden.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-1
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1 (installiert vom Stand nach 2.13.1, Kit-Commit `1ca387e`)
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, nur pwsh-Bahn; deploybare Projekte als Unterordner `src/<projekt>/` (XML-Workflows einer Dateitransfer-Software plus Skripte), dazu ein kleines Python-Prüfwerkzeug. Klein, erste Kaskade gelaufen.

## Was passiert ist

Jedes deploybare Projekt liegt als Ordner `src/<projekt>/` und wird so, wie es
im Arbeitsbaum liegt, auf den Zielserver kopiert. Im ersten Sweep fand das Red
Team (Fund HM-1, Schwere „hoch"): Die Zeile `backups/` aus dem
`.gitignore`-Fragment des Kits gilt in **jeder** Tiefe. Ein Unterordner
`backups/` eines Projekts wird damit nie versioniert:

```
$ git check-ignore -v --no-index src/projekt/backups/stand.xml
.gitignore:52:backups/	src/projekt/backups/stand.xml
```

Die Datei liegt lokal, die Prüfung des Projekts sieht sie, aber kein Klon und
kein Kollege hat sie je. `git status` zeigt sie nicht, und der Guard sieht sie
auch nicht. Dieselbe Bauart steckte vorher in einer fremden Python-Vorlage im
selben `.gitignore` (`lib/`, `env/`, `build/` …); die ist im Projekt entfernt.
Das Kit-Fragment ist die Stelle, die bleibt.

## Wo es steckt

`bootstrap/gitignore.fragment`, Zeile 22: `backups/` ohne führenden
Schrägstrich. Gemeint ist der Sicherungsordner, den `install … --update` in der
**Wurzel** anlegt (`backups/update-<zeit>/`). Die anderen ungebundenen Zeilen
des Fragments (`.ralph-logs/`, `.team-logs/`, `.team-protokolle/`, die
Zustandsdateien) beginnen mit einem Punkt und kollidieren kaum mit
Produktivcode. `backups/` ist der eine Name, den ein Projekt selbst haben kann.

## Warum das jede Installation trifft

Das Fragment wird in jedes Zielprojekt geschrieben. Jedes Projekt, dessen
Produktivcode irgendwo einen Ordner `backups/` hat — Sicherungen,
Archivablagen, ein Projekt-Unterordner —, verliert ihn still aus der
Versionierung. Kein Werkzeug des Kits meldet das.

## Was ich schon versucht habe

Im Projekt lokal gefixt: `backups/` → `/backups/` (mit einem Regressionstest,
der `src/<x>/backups/…` gegen `git check-ignore` prüft). Das nächste `--update`
überschreibt den Fix nicht, sondern meldet die fehlende Fragment-Zeile nur
(`Kit-BL-311`). Der Fix hält also hier, aber jede andere Installation hat die
Lücke weiter.

Vorschlag: im Fragment `/backups/` schreiben, denn der Sicherungsordner liegt
immer in der Wurzel. Dazu ein Test, der jede Ordnerzeile des Fragments gegen
einen Pfad `src/<x>/<zeile>` hält und rot wird, wenn eine davon dort greift.

# smoke_warten.py warten ohne Kennung nimmt den Lauf mit dem groessten Namen - ein fremder smoke-Log haelt es endlos bei 75

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-26-smoke-warten-py-warten-ohne-kennung-nimmt-den-lauf-mit-dem-g.md
      .\kit-melden.cmd ablegen  2026-10-26-smoke-warten-py-warten-ohne-kennung-nimmt-den-lauf-mit-dem-g.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-26-smoke-warten-py-warten-ohne-kennung-nimmt-den-lauf-mit-dem-g.md   # sonst: Pull Request

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
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn. `.team-logs/` enthält gut hundert Logs aus
  zwei Monaten Kaskaden, darunter zwei `smoke-*.log` mit eigenem Namensschema aus der Zeit vor
  `smoke_warten.py`. Gefunden beim Probelauf vom 2026-10-26, im selben Zug wie die Meldung zu
  `start` unter cmd.exe.

## Was passiert ist

`start` druckte die Kennung `20261026-121601-817710`. Das anschließende `warten` ohne Kennung
meldete:

    [smoke_warten] Laeuft noch (stufe158-1790169213) — `warten` erneut IM VORDERGRUND aufrufen (Exit 75 heisst nicht rot).

Gemeint war ein Lauf vom 2026-09-23. Seine Logdatei heißt `smoke-stufe158-1790169213.log`. Eine
Rolle unseres eigenen Verfahrens hat sie damals so benannt, eine `.rc` hat sie nie bekommen. Bei
jedem weiteren `warten` kommt deshalb wieder 75.

## Wo es steckt

`geteilt/tools/smoke_warten.py`, `_juengster()`. Die Funktion sortiert `smoke-*.log` nach dem
Namen und nimmt den letzten. Das stimmt nur, solange jeder Name eine Kennung von `start` ist.
`stufe…` sortiert hinter jede Kennung, die mit `2026…` beginnt, und bleibt damit für immer „der
jüngste Lauf".

## Warum das jede Installation trifft

`.team-logs/` ist der gemeinsame Log-Ordner des Kits. Dort liegen auch Vollautomatik-Logs und
Logs, die Rollen selbst benennen. Ein einziger fremder `smoke-*.log` genügt. Rot wird dabei
nichts, denn 75 heißt „läuft noch". Die Rolle ruft `warten` deshalb immer wieder auf, bis Frist
oder Budget erschöpft sind. Das ist der teure Ausgang, gegen den `BL-281` gebaut ist. Der
Nachsatz der Rollen nennt `warten` ohne Kennung.

## Was ich schon versucht habe

Am Kit nichts. Mit Kennung (`warten <kennung>`) läuft es richtig, gemessen am selben Tag.

Vorschlag: Nur Namen im eigenen Kennungsformat berücksichtigen (`\d{8}-\d{6}-\d{6}`) oder nach
Änderungszeit wählen. Zusätzlich die Kennung, die `start` druckt, im Nachsatz an `warten`
weitergeben lassen. Dazu ein Testfall mit einem fremden `smoke-*.log`.

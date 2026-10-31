# Rollenaufrufe aus einer Claude-Code-Sitzung erben deren CLAUDE-Variablen

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-31-rollenaufrufe-aus-einer-claude-code-sitzung-erben-deren-clau.md
      .\kit-melden.cmd ablegen  2026-10-31-rollenaufrufe-aus-einer-claude-code-sitzung-erben-deren-clau.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-31-rollenaufrufe-aus-einer-claude-code-sitzung-erben-deren-clau.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit (Vorschlag; ein Schaden ist nicht beobachtet)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; siebte und achte Kaskade. Claude Code läuft IDE-gebündelt in VS Code

## Was passiert ist

Auf Wort des Stakeholders hat der Architekt die Vollautomatik aus seiner interaktiven
Claude-Code-Sitzung gestartet. Die Rollen liefen dann mit den Umgebungsvariablen der Sitzung:
gut ein Dutzend Namen mit `CLAUDE`-Präfix, darunter `CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`,
`CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_CHILD_SESSION`, `CLAUDE_CODE_MESSAGING_SOCKET`,
`CLAUDE_CODE_MESSAGING_TOKEN`, `CLAUDE_EFFORT` und `CLAUDE_PID`.

Im PowerShell-Werkzeug der Sitzung ließen sie sich nicht entfernen: Nach
`[Environment]::SetEnvironmentVariable($name, $null)` blieben 14 stehen, auch im Kindprozess.
Über Git Bash mit `env -u <name>` je Variable sah das Kind keine mehr. Harry lief einmal mit den
geerbten Variablen (Kosten unauffällig, Transkript trotzdem `entrypoint: sdk-cli`); Marv wurde
nach einer Minute angehalten und ohne sie neu gestartet.

Ein Schaden ist nicht beobachtet. Das Risiko liegt in der Bauart: Eine headless Rolle bekommt
Kennung, Nachrichtenkanal samt Token und Einstellungen (z. B. den Denkaufwand) der interaktiven
Sitzung. Was die CLI daraus macht, hängt an ihrer Version. Aus der Einrichtung des Kits auf
derselben Maschine bekannt: Eine Sitzung vererbt auch `PSExecutionPolicyPreference=Bypass`, und
ein verschachteltes `claude -p` verhält sich dann nicht wie im Feld.

## Wo es steckt

`team_claude_schreiben` in `team/lib.sh` und `Team-ClaudeSchreiben` in `team/lib.psm1` starten
die Agenten-CLI mit der vollen geerbten Umgebung. Eine Folge fängt das Kit schon an anderer
Stelle ab: `kosten.py` erkennt Rollen-Läufe zuerst am Briefing-Kopf, weil ein aus einer Sitzung
gestarteter Lauf deren `entrypoint` erben kann (`Kit-BL-272`, `Kit-BL-291`). Abgefangen wird dort
die Folge, nicht die Ursache.

## Warum das jede Installation trifft

Jeder Rollenaufruf läuft über diese zwei Funktionen. Wer die Vollautomatik oder eine einzelne
Rolle aus einer Claude-Code-Sitzung heraus startet, trifft es in jedem Projekt. Mit einer
IDE-gebündelten CLI (`Kit-BL-173`) ist die Sitzung die naheliegende Konsole.

## Was ich schon versucht habe

Am Kit nichts geändert. Umgangen: Die Sitzung startet Rollen nur noch über Git Bash, mit
`env -u` für jede `CLAUDE*`-Variable.

Vorschlag, ohne Anspruch:

- Beide Funktionen entfernen für den CLI-Aufruf die Variablen, die eine Sitzung setzt — als
  feste Liste oder nur, wenn `CLAUDECODE` gesetzt ist. Blind alle `CLAUDE*` zu entfernen nähme
  gewollte Einstellungen mit (z. B. `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_USE_BEDROCK`).
- `team-status` warnt, wenn `CLAUDECODE` gesetzt ist („Aufruf aus einer Claude-Code-Sitzung“).

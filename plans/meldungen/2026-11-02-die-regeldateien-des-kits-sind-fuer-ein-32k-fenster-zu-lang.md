# Die Regeldateien des Kits sind für ein 32K-Fenster zu lang

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-02-die-regeldateien-des-kits-sind-fuer-ein-32k-fenster-zu-lang.md
      .\kit-melden.cmd ablegen  2026-11-02-die-regeldateien-des-kits-sind-fuer-ein-32k-fenster-zu-lang.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-02-die-regeldateien-des-kits-sind-fuer-ein-32k-fenster-zu-lang.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Lücke in der Doku
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; lokale Modelle mit 32K- und 64K-Fenster auf einer 16-GB-Karte

## Was passiert ist

Das Projekt misst sein Wissen mit einem eigenen Werkzeug: Token je Markdown-Datei (Bytes durch 3),
Grenze ein Viertel des 32K-Fensters (8.192 Token), dazu höchstens 20 Wörter je Satz. Die Dateien
des Kits liegen deutlich darüber:

| Datei | Token (geschätzt) | Wörter je Satz |
|---|---:|---:|
| `CLAUDE.md` (Kit-Teil) | 14.864 | 18,0 |
| `TEAM.md` | 13.209 | 16,2 |
| `team/prompts/rolle-architekt.md` | 9.395 | 21,0 |
| `team/prompts/rolle-ralph.md` | 944 | 20,2 |

`CLAUDE.md` steht im Systemprompt jeder Rolle. In einem 32K-Fenster belegt sie damit fast die
Hälfte, bevor der Auftrag beginnt; mit dem Briefing des Architekten sind es rund drei Viertel.

## Wo es steckt

Die Regeldatei `CLAUDE.md`, die Bedienanleitung `TEAM.md` und die Briefings unter `team/prompts/`.
Die Doku-Hygiene der Regeldatei sagt selbst, warum die Länge zählt (sie wird in jedem Rollenaufruf
mitbezahlt), nennt aber keine Grenze.

## Warum das jede Installation trifft

Jede Installation trägt dieselben Dateien. Für eine Rolle mit gehostetem Modell kostet die Länge
Geld je Aufruf; für eine Rolle mit lokalem Modell auf einer 16-GB-Karte entscheidet sie, ob Regeln
und Auftrag zusammen ins Fenster passen.

## Was ich schon versucht habe

- Am Kit nichts geändert; die Dateien gehören dem Kit. Im Projekt nur gemessen und gemeldet.
- Vorschlag, ohne Anspruch: eine Grenze je Dateiart festlegen (etwa ein Viertel des kleinsten
  Fensters, das eine Rolle nutzen soll) und im Kit-Test prüfen; Herleitung und Historie aus
  `CLAUDE.md` wörtlich in ein Historien-Doc verschieben, wie es die Doku-Hygiene schon verlangt.

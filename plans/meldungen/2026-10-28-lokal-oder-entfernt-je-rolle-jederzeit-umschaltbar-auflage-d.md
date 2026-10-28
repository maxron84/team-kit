# Lokal oder entfernt je Rolle, jederzeit umschaltbar - Auflage des Owners an die Programm-Stufe

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-28-lokal-oder-entfernt-je-rolle-jederzeit-umschaltbar-auflage-d.md
      .\kit-melden.cmd ablegen  2026-10-28-lokal-oder-entfernt-je-rolle-jederzeit-umschaltbar-auflage-d.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-28-lokal-oder-entfernt-je-rolle-jederzeit-umschaltbar-auflage-d.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: Meldung vom 2026-10-28 („Lokale Stufen im Team …“), Vorschlag „Programm-Stufe“
- **Art**: Idee / Verbesserung — Auflage des Owners
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: wie in der Meldung vom 2026-10-28 — Greenfield, Windows 11, pwsh-Bahn, Python; ein Programm lässt ein lokales Sprachmodell (32K-Fenster) Bauschritte machen

## Was passiert ist

Nach der ersten Stufe, die das lokale Modell gebaut hat, hat der Owner die Endform entschieden:
Die lokale Werkbank wird ein lokaler Teil des Kits. Seine Auflage dazu, wörtlich:

> „Wird ein lokaler Teil des Kits, das Kit soll skalierbar sein für den Benutzer und zwar
> jederzeit, im Sinne von welche Rolle wird 100% lokal und umgekehrt, oder auch nur 50% nach
> ermessen des Architekten, oder auch auf Zuruf des Benutzers spontan“

Im Feld hat der Architekt die Wahl schon einmal getroffen: eine Stufe mit Bauauftrag für das
lokale Modell, alles Übrige der Kaskade mit der Agenten-CLI.

## Wo es steckt

Die Wahl, welcher Weg eine Rolle oder Stufe bedient, gibt es heute nicht: Jede Rolle ruft
`team_claude()`. Betroffen wären die Rollen-Skripte (welcher Weg), `team.config.*` (Vorgabe je
Rolle), das Briefing des Architekten (Wahl je Stufe im Plan) und die Startbefehle (Zuruf für
einen Lauf).

## Warum das jede Installation trifft

Ohne eine solche Einstellung bleibt „lokal“ eine Bastelei je Projekt. Mit ihr wählt jede
Installation je Rolle nach Karte, Aufgabe und Budget — und kann jederzeit zurück.

## Was ich schon versucht habe

Nichts am Kit. Vorschlag, ohne Anspruch — drei Ebenen derselben Wahl:

- **Vorgabe je Rolle** in `team.config.*`: lokal, entfernt oder gemischt.
- **Je Stufe im Plan**, nach Ermessen des Architekten (im Feld: der Bauauftrag-Block).
- **Auf Zuruf** beim Start, nur für diesen Lauf.

Offen aus dem Feld: Scheitert eine lokale Rolle, gibt es im Zielbild des Owners keinen stillen
Rückfall auf ein entferntes Modell; sie übergibt an den Menschen. „Umgekehrt“ wäre dann eine
ausdrückliche Wahl, kein Rückfall — das sollte das Kit so unterscheiden.

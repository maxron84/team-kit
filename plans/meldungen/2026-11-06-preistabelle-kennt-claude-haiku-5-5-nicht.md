# Preistabelle kennt claude-haiku-5-5 nicht

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-06-preistabelle-kennt-claude-haiku-5-5-nicht.md
      .\kit-melden.cmd ablegen  2026-11-06-preistabelle-kennt-claude-haiku-5-5-nicht.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-06-preistabelle-kennt-claude-haiku-5-5-nicht.md   # sonst: Pull Request

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
- **Feldkürzel**: keins eingetragen — bitte vergeben
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn; Architekt interaktiv in der IDE

## Was passiert ist

Eine interaktive Architekten-Sitzung startete einen Hilfsleser (Subagent) auf
`claude-haiku-5-5`. `kosten.py sitzungen-pruefen` und `sitzung-messen`
melden dazu „ohne Preis, nicht im Betrag: claude-haiku-5-5"; die gebuchte
Zeile enthält den Anteil also nicht. Er war klein (10 Antworten,
dedupliziert: 583.289 Token Cache-Lesen, 75.864 Cache-Schreiben, 7.419
Ausgabe — mit den Preisen von `claude-haiku-4-5` rund 0,2 USD), aber er fehlt
still im Ledger: `--ledger-pruefen` sieht interaktive Sitzungen nicht.

## Wo es steckt

`team/tools/kosten.py`, Preistabelle: Sie führt `claude-haiku-4-5`, nicht
`claude-haiku-5-5`.

## Warum das jede Installation trifft

Die CLI wählt für Hilfsleser oft das kleine Modell der aktuellen Familie.
Jede Installation, deren Architekt Subagenten nutzt (`Kit-BL-305` zählt sie
ausdrücklich mit), bucht dann zu wenig, und die Warnung steht nur in der
Messausgabe, die beim Buchen übernommen, aber selten gelesen wird.

## Was ich schon versucht habe

Lokal nichts geändert; der Anteil ist im Abschluss-Protokoll des Projekts als
Lücke vermerkt. Vorschlag: `claude-haiku-5-5` mit belegtem Preis in die
Tabelle aufnehmen; hilfsweise bricht `sitzung-messen` bei einem unbekannten
Modell mit eigenem Exit-Code ab wie bei einer ungeeichten Tabelle (Exit 2),
statt eine Buchungszeile zu drucken.

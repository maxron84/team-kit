# Ein abgebrochener Lauf hinterlaesst die laufende Stufe halb gebaut und ohne Kostenlog

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-10-ein-abgebrochener-lauf-hinterlaesst-die-laufende-stufe-halb.md
      .\kit-melden.cmd ablegen  2026-10-10-ein-abgebrochener-lauf-hinterlaesst-die-laufende-stufe-halb.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-10-ein-abgebrochener-lauf-hinterlaesst-die-laufende-stufe-halb.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-63)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1 (mit späteren Ständen aus `[Unreleased]`)
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Zwölf Kaskaden sind gelaufen, ein Lauf der Vollautomatik baut acht bis elf Stufen.

## Was passiert ist

Ein Lauf der Vollautomatik wurde am Abend beendet, während Ralph mitten in einer Stufe war. Das Log
der Vollautomatik endet nach „Auth-Modus: abo“ dieser Stufe, ohne Schlusszeile. Am Morgen startete der
Mensch dieselbe Startzeile noch einmal, wie es das Team für einen Abbruch vorsieht. Der Lauf nahm die
Stufe wieder auf und lief sauber durch, mit Red Team und Fixphase.

Zwei Folgen, keine davon wird gemeldet:

1. **Die halbe Arbeit des abgebrochenen Aufrufs blieb im Arbeitsbaum, und der neue Aufruf baute
   darauf weiter.** Der abgebrochene Ralph hatte schon zwei Dateien geändert, eine Datendatei und
   einen Test. Der zweite Ralph schrieb in sein `result`: „… waren beim Start bereits geändert; ich
   habe das übernommen und die Tests, Mutationen und den Changelog dazu ergänzt.“ Er committete
   beides mit. Hier war das Ergebnis richtig, aber nur, weil der erste Aufruf zufällig richtig
   angefangen hatte. Geprüft hat es kein Guard: Der Guard des abgebrochenen Aufrufs lief nie, und der
   neue rechnet ihm unveränderte schmutzige Pfade nicht an und veränderte als seine Sache. Im Log der
   Vollautomatik steht keine Warnung dazu.
2. **Der abgebrochene Aufruf hat kein Kostenlog.** In `.ralph-logs/` fehlt die Datei des ersten
   Anlaufs. Seine Kosten fehlen im Ledger und in „Dieser Lauf“ des Abschlussberichts. Gemessen über
   das Transkript der Sitzung mit `kosten.py sitzung-messen <transkript>`: 0,3661 USD (Sonnet). In
   der Liste von `kosten.py sitzungen-pruefen` taucht die Sitzung nicht auf.

## Wo es steckt

- `team/lib.psm1`, `Team-ClaudeSchreiben`: `$roh = & $Claude -p … --output-format json`, erst danach
  `WriteAllText($Out, …)`. Endet der Prozess während des Aufrufs, wird nichts geschrieben. Anders als
  im 429-Pfad entsteht auch kein Stub.
- `team/lib.psm1`, `team_guard_begin`: Ein schmutziger Arbeitsbaum beim Rollenstart erzeugt nur die
  Warnung „[guard] WARNUNG: Der Arbeitsbaum ist beim Rollenstart NICHT sauber“ auf stderr, und die
  Rolle läuft weiter. Unveränderte Pfade gelten als fremd, veränderte als Sache der Rolle und gehen
  in ihren Commit.
- Beim Wiederanlauf erkennt die Vollautomatik nicht, dass die letzte Rolle abgebrochen ist, und
  verlangt nicht, die liegengebliebenen Änderungen zu sichten.

## Warum das jede Installation trifft

Jeder Lauf kann abbrechen: Fenster zu, Neustart, Ctrl+C. Das Team ist darauf gebaut, dass man dann
dieselbe Zeile noch einmal startet. Danach setzt die nächste Rolle auf der Arbeit eines Aufrufs auf,
dessen Guard nie lief, und die Kosten des abgebrochenen Aufrufs fehlen im Ledger. Weder
`--ledger-pruefen` noch `sitzungen-pruefen` zeigt das. Bei einem teuren Aufruf, etwa Axel oder einer
großen Stufe, ist das kein Kleingeld.

## Was ich schon versucht habe

Im Kit nichts geändert. Im Feldprojekt sind die Kosten des abgebrochenen Aufrufs über das Transkript
gemessen und in der Notiz der Bau-Zeile genannt, aber nicht gebucht. Eine Buchung ohne Rohlog ließe
`--ledger-pruefen` dauerhaft warnen.

Vorschläge:
- **Stub vor dem Aufruf:** `Team-ClaudeSchreiben` schreibt vor dem Aufruf einen Stub (Rolle, Stufe,
  Start, `abgebrochen`) und überschreibt ihn am Ende. Nimmt die CLI eine vorab vergebene
  Sitzungskennung an, steht sie im Stub, und das Transkript lässt sich später messen und buchen.
- **Sichten beim Wiederanlauf:** Liegt beim Start ein Stub ohne Ergebnis, nennt der Lauf die Rolle als
  abgebrochen und hält an, bis der Mensch die liegengebliebenen Änderungen gesichtet hat (committen
  oder verwerfen). Er übernimmt sie nicht still.

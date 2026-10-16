# Nach Franks Docs-Commit läuft kein Test mehr, die Vollautomatik endet auf einem roten HEAD

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-16-nach-franks-docs-commit-laeuft-kein-test-mehr-die-vollautoma.md
      .\kit-melden.cmd ablegen  2026-10-16-nach-franks-docs-commit-laeuft-kein-test-mehr-die-vollautoma.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-16-nach-franks-docs-commit-laeuft-kein-test-mehr-die-vollautoma.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-77); Feldbeleg zur Meldung vom 2026-10-11 („Ein
  Regex-Escape im Testcode wird auf dem Weg in die Datei zum Steuerzeichen“)
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in Python. Fünfzehn
  Kaskaden sind gelaufen, die Suite hat rund 2700 Tests, darunter einer, der CHANGELOG und Pläne auf Steuerzeichen
  prüft.

## Was passiert ist

In der Fix-Phase einer Vollautomatik (drei Funde, je ein Versuch) hat Frank zweimal ein BEL (0x07) ins CHANGELOG
geschrieben. Im Eintrag stand `.\abnahme.cmd`, und aus `\a` wurde auf dem Weg über einen Python-String das
Steuerzeichen, dieselbe Bauart wie in der Meldung vom 2026-10-11. In derselben Kaskade traf es auch Ralph, der es
aber vor seinem Commit fand.

- Das erste BEL kam mit dem Docs-Commit des ersten Fundes. Frank fand es im zweiten Fund, weil er dort die volle Suite
  fuhr, und entfernte es.
- Das zweite kam mit dem letzten Docs-Commit der Fix-Phase. Frank hatte die Suite vor diesem Commit gefahren („Die
  Suite ist grün“), danach nicht mehr. `frank.ps1` meldete „Dreisatz verifiziert“. Die Fix-Phase endete mit „nichts
  mehr zu tun“, und die Vollautomatik meldete „beendet“. Der HEAD war rot.
- Bemerkt hat es erst die Abnahme, die 4 s später auf diesem Stand startete. Ihre Gegenlesung lief in jeder
  Mutationsreihe auf eine rote Grundprobe, und ihr Ergebnis wurde nach 2,5 Stunden verworfen (zweite Meldung von
  heute zum Abnahme-Loop).

## Wo es steckt

- `frank.ps1`: Als Erfolg zählen Promise, Fix-Commit, Status, Diff am Fund und Reproducer. Einen Test nach dem letzten
  Commit des Fixes verlangt es nicht.
- `vollautomatik.ps1`: Die volle Suite am Ende von Bau- und Fix-Phase läuft nur, wenn `TEAM_SMOKE_TEST_SCHNELL`
  gesetzt ist (`Kit-BL-232`). Ohne zweistufigen Smoke-Test läuft am Ende gar keiner.
- Franks Auftrag erlaubt den CHANGELOG- und Status-Eintrag ausdrücklich in einem `docs:`-Folgecommit, also nach dem
  letzten Smoke-Test.

## Warum das jede Installation trifft

Es trifft jede Installation ohne zweistufigen Smoke-Test, sobald die Suite Doku-Dateien prüft (Steuerzeichen,
Verweise, Zitate) oder Frank im Folgecommit mehr als Prosa ändert. Die Vollautomatik meldet Erfolg, und die nächste
Rolle startet auf einem roten Stand: der nächste Lauf, der Architekt oder eine Abnahme.

## Was ich schon versucht habe

Im Feldprojekt hat der Architekt das Zeichen im Abschluss ersetzt, ohne Änderung am Kit. Erwogen, aber noch nicht
entschieden: `TEAM_SMOKE_TEST_SCHNELL` gleich `TEAM_SMOKE_TEST` setzen. Dann fährt die Vollautomatik am Ende beider
Phasen die volle Suite, und rot setzt das Gate. Das kostet zwei Suitenläufe mehr je Lauf.

Vorschläge fürs Kit:

- Die Vollautomatik fährt den Smoke-Test am Ende der Fix-Phase immer, nicht nur im zweistufigen Betrieb, und rot setzt
  das Gate.
- Oder `frank.ps1` fährt ihn nach dem letzten Commit eines Fixes, bevor es „Dreisatz verifiziert“ meldet; rot zählt als
  Fehlversuch.

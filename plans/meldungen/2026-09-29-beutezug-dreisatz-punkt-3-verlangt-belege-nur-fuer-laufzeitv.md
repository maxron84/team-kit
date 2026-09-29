# Beutezug-Dreisatz Punkt 3 verlangt Belege nur fuer Laufzeitverhalten - ein Fund behauptete einen roten Test, ohne ihn auszufuehren

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-29-beutezug-dreisatz-punkt-3-verlangt-belege-nur-fuer-laufzeitv.md
      .\kit-melden.cmd ablegen  2026-09-29-beutezug-dreisatz-punkt-3-verlangt-belege-nur-fuer-laufzeitv.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-29-beutezug-dreisatz-punkt-3-verlangt-belege-nur-fuer-laufzeitv.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-17)
- **Art**: Lücke in einer Regel des Kits
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Vier Kaskaden sind gelaufen.

## Was passiert ist

In der vierten Kaskade meldete Harry einen Fund der Schwere „kritisch" gegen eine neue Regel des
Prüfwerkzeugs. Nach seinem Befund widerspreche ein Testfall der Implementierung, und im letzten
Reproschritt stand: „`python -m pytest <testdatei> -q` zeigt den roten Fall." Ausgeführt hatte er
den Befehl nicht. Die Behauptung war aus dem Python-Kontrollfluss hergeleitet, und die Herleitung
übersah eine Datendatei, die das Ergebnis bestimmt.

Der Test war grün. Frank stellte das in seiner Gegenprobe fest und baute trotzdem eine harmlose
Absicherung, damit der Lauf eine Quittung hatte: 1,42 USD, 44 Turns, fast 7 Minuten. Das war der
teuerste Fix-Lauf dieser Fix-Phase. Beim Gegenlesen musste der Architekt den Fund anschließend
widerlegen und den CHANGELOG-Text berichtigen, denn Frank hatte die Begründung des Fehlalarms
übernommen.

## Wo es steckt

`team/prompts/rolle-harry.md` und `rolle-marv.md`, Beutezug-Dreisatz Punkt 3 (`Kit-BL-215`), und
dieselbe Zeile im Regeltext von `CLAUDE.md`. Die Regel verlangt einen Beleg nur für „Laufzeitverhalten
einer Sprachkonstruktion". Eine Behauptung über das Ergebnis eines Befehls, den der Finder selbst
ausführen kann (ein bestehender Test ist rot, das Werkzeug meldet X, der Smoke-Test scheitert),
fällt dem Wortlaut nach nicht darunter. Für sie gilt „Lesen ist die richtige Methode", und dort
versagt Lesen genauso.

## Warum das jede Installation trifft

Die Regel steht in den ausgelieferten Briefings. Jeder Red-Team-Lauf, der einen roten Test aus dem
Code herleitet, statt ihn auszuführen, kann denselben Fehlalarm erzeugen. Für den Fixer ist er
nicht billiger als ein echter Fund, denn er muss die Ursache erst widerlegen. Das ist genau die
Rechnung aus `Kit-BL-215`.

## Was ich schon versucht habe

Lokal nichts, der Fund ist erledigt. Vorschlag fürs Kit: Punkt 3 um einen Satz erweitern.
„Behauptet ein Fund das Ergebnis eines Befehls, den ich im Loop ausführen kann (ein Test ist rot,
das Werkzeug meldet X), führe ich ihn aus und zitiere die Ausgabe im Fundblock." Das kostet
Sekunden. Die Gegenprobe wäre ein Lint im Beutebuch-Werkzeug: Ein Reproschritt mit einem
Testbefehl ohne zitierte Ausgabe ergibt einen Hinweis.

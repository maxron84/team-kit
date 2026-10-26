# Die Kostenbuchung in der Scharfschalt-Sequenz verlangt Werte zum Abschreiben - in pwsh bricht schon der Platzhalter den ganzen Block ab

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-26-die-kostenbuchung-in-der-scharfschalt-sequenz-verlangt-werte.md
      .\kit-melden.cmd ablegen  2026-10-26-die-kostenbuchung-in-der-scharfschalt-sequenz-verlangt-werte.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-26-die-kostenbuchung-in-der-scharfschalt-sequenz-verlangt-werte.md   # sonst: Pull Request

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
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Architekt im Abo, rund vierzig Kaskaden.
  Gefunden beim Scharfschalten einer frisch ausgehärteten Kaskade am 2026-10-26.

## Was passiert ist

Der Architekt gab die Scharfschalt-Sequenz so aus, wie das Briefing sie vorschreibt: Schritt 0 misst
die eigene Sitzung und bucht sie, mit `<USD>` und `<zeit>` als Platzhaltern aus der gedruckten
Buchungszeile. Der Mensch hat den Block in pwsh eingefügt:

    ParserError:
    Line |
       3 |  .\team-status.ps1 --akteur-abschluss architekt abo <USD> produkt 'Kas …
         |                                                     ~
         | The '<' operator is reserved for future use.

pwsh parst einen eingefügten Block als Ganzes. **Nichts davon lief** — auch nicht Zeigerwechsel,
Konsistenz-Check und Start, die im selben Block standen.

Der zweite Befund wiegt schwerer als der Parser: Der Mensch **kennt die Werte nicht** und will sie
nicht abschreiben. Wörtlich: *„Ich habe schon öfter angemerkt, dass ich diese Werte nicht kenne und
bitte automatisch ermittelt und eingesetzt werden sollen."* Er hat das in diesem Projekt mehrfach
gesagt; die Vorlage bringt den Platzhalter mit jeder Aushärtung zurück.

## Wo es steckt

- `geteilt/prompts/rolle-architekt.md`, Mein Dreisatz, Punkt 3 („Erster Schritt der Sequenz,
  kopierfertig: der Kostenabschluss DIESER Sitzung"): *„Zwei Befehle, weil der Betrag erst
  gemessen werden muss; … `<USD>`, `<kennung>` und `<zeit>` stehen in der Buchungszeile, die der
  erste Befehl druckt"*, darunter der Block mit `--architekt-abschluss <USD> <domaene> … --kaskade
  <N+1> --transkript <kennung> --bis <zeit>`. Dieselbe Form im Closeout-Abschnitt
  (`--architekt-abschluss <USD> <domaene> "<notiz>"`, *„Woher `<USD>` kommt"*).
- `bootstrap/TEAM.md`, Abschnitt 4 *Closeout*: `--architekt-abschluss <USD> <domaene> "Kaskade N
  geplant"` und *„Woher `<USD>` kommt"*.
- `geteilt/tools/kosten.py`, `sitzung-messen`: druckt
  `Buchen: team-status --akteur-abschluss architekt abo <betrag> <domaene> "<notiz>" --transkript …
  --bis …` — eine Zeile **zum Abschreiben**. Eine Option, die misst **und** bucht, gibt es nicht.

Die Vorlage macht damit den Menschen zum Boten zwischen zwei Befehlen, für Werte, die nur das
Werkzeug kennt.

## Warum das jede Installation trifft

Jede Installation bekommt dieselbe Vorlage, und beide Bahnen scheitern an ihr — verschieden laut:

- **pwsh:** `<` außerhalb von Anführungszeichen ist ein reservierter Operator. Der eingefügte Block
  bricht als Ganzes ab, kein Schritt läuft (oben zitiert).
- **bash:** `<USD>` ist eine Eingabeumleitung. Gemessen mit einem Probeskript aus drei Zeilen, die
  mittlere mit `<USD>`:

      eins
      probe.sh: line 2: USD: No such file or directory
      drei

  Exit 0. **Nur die Buchungszeile scheitert; die Zeilen danach laufen weiter.** In einer
  Scharfschalt-Sequenz heißt das: Zeiger umgelegt, Lauf gestartet, Sitzung nicht gebucht — genau
  der Ausgang, gegen den `Kit-BL-165`, `Kit-BL-197` und `Kit-BL-291` die Reihenfolge festgelegt
  haben. (Die bash-Folge ist aus dem Probeskript abgeleitet, eine echte Sequenz lief so nicht.)

Und unabhängig vom Parser: Kein Mensch kennt Betrag, Transkript-Kennung und Fensterende seiner
Architektensitzung. Wer abschreibt, kann sich verschreiben, und `--addieren` auf eine bestehende
Zeile verlangt zusätzlich eine Notiz, die die frühere Sitzung mit nennt.

## Was ich schon versucht habe

Lokal, ohne Änderung am Kit:

1. **Der Architekt bucht seine Sitzung selbst**, als letzten Schritt vor der Schlussnachricht:
   `sitzung-messen <pfad>` fahren, Betrag, `--transkript`, `--von`/`--bis` per Regex aus der
   `Buchen:`-Zeile lesen, `--akteur-abschluss` aufrufen, die Ledgerzeile zählen. Was danach noch
   anfällt (Commit der Buchung, Schlussnachricht), bucht der Closeout über `--von` nach — das kann
   `sitzung-messen` seit `Kit-BL-252` schon.
2. **Die Sequenz an den Menschen trägt keine Platzhalter mehr** und beginnt mit dem Wegräumen der
   Altlasten.

Vorschlag für das Kit:

- **`sitzung-messen … --buchen`** (oder `team-status --architekt-abschluss --messen <transkript>`):
  misst und bucht in einem Aufruf, mit Domäne, Kaskade und Notiz als Argumenten. Die Werte
  verlassen das Werkzeug nie. Verweigert wie bisher bei ungeeichter Preistabelle (Exit 2) und bei
  einem schon gebuchten Fenster (`Kit-BL-116`).
- **Briefing:** Schritt 0 der Sequenz entfällt — der Architekt bucht sich am Ende der Aushärtung
  selbst; die Sequenz beginnt mit dem Wegräumen der Altlasten. Muss der Mensch doch etwas
  ausführen, dessen Wert erst beim Ausführen feststeht, ermittelt die Sequenz ihn selbst (Ausgabe
  in eine Variable), nie „aus der gedruckten Zeile übernehmen".
- **Regel für jede ausgegebene Sequenz:** kein `<…>` außerhalb von Anführungszeichen. Dasselbe gilt
  für die Vorlagen in `bootstrap/TEAM.md`, sobald sie kopierfertig gemeint sind.
- Testfall: eine Sequenz aus dem Briefing-Generator (oder der Vorlagentext selbst) enthält kein
  `<` außerhalb von Anführungszeichen.

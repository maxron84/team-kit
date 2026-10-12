# Vollautomatik startet trotz ungebuchter Planungssitzung der Kaskade

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-12-vollautomatik-startet-trotz-ungebuchter-planungssitzung-der.md
      ./kit-melden.sh ablegen  2026-10-12-vollautomatik-startet-trotz-ungebuchter-planungssitzung-der.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-12-vollautomatik-startet-trotz-ungebuchter-planungssitzung-der.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-3
- **Art**: Lücke im Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; erste Kaskade

## Was passiert ist

Die Scharfschalt-Sequenz des Architekten begann, wie es sein Briefing seit
`Kit-BL-197`/`Kit-BL-291` verlangt, mit dem Kostenabschluss der
Aushärtungs-Sitzung (`sitzung-messen` → `--architekt-abschluss … --addieren`).
Danach kamen der Commit, der Zeiger und der Start.

Gebucht wurde nichts. Das Ledger trägt nach dem Lauf nur die Zeile der
Skizzen-Sitzung. Der Commit davor trägt trotzdem „Architekten-Sitzung
gebucht", weil die Commit-Vorlage der Sequenz das voraussetzte. Die
Vollautomatik startete ohne jeden Hinweis. Im Closeout zeigte
`kosten.py sitzungen-pruefen` die Lücke: die Aushärtung ungebucht, dazu der
Nachlauf der Skizzen-Sitzung.

Das ist dasselbe Muster, das `Kit-BL-197` beschreibt (im Feld zweimal an
einem Tag, 43,90 USD). Die Antwort darauf war, den Schritt an ein Ereignis zu
binden statt an eine Erinnerung. Ereignis ist aber eine Zeile, die ein Mensch
kopieren muss, und das Ereignis, an dem das Kit wirklich sitzt — der Start
der Vollautomatik —, prüft es nicht.

## Wo es steckt

`vollautomatik.sh` (beide Bahnen), Startphase: Dort wird die
`BUDGET_EMPFEHLUNG_USD` des Plans gelesen. Dieselbe Stelle kennt die
Kaskadennummer des Plans und könnte `kosten.py sitzungen-pruefen` fragen.

## Warum das jede Installation trifft

Jede Aushärtung endet mit einer Sequenz, deren erster Schritt Handarbeit ist.
Wird er übersprungen, fällt die Planungsarbeit aus dem Ledger, und nichts im
Lauf meldet es — erst ein Closeout, der `sitzungen-pruefen` fährt.

## Was ich schon versucht habe

Projektseitig: Die Commit-Vorlage der Sequenz behauptet künftig keine
Buchung mehr, die sie nicht geprüft hat; vor dem Commit steht
`sitzungen-pruefen` mit der Erwartung „nichts offen". Vorschlag fürs Kit:
Die Vollautomatik ruft beim Start `sitzungen-pruefen` und meldet ungebuchte
Sitzungen (Warnung, kein Abbruch — die laufende Sitzung des Architekten ist
legitim offen, `sitzungen-pruefen` erkennt sie schon als „läuft noch").

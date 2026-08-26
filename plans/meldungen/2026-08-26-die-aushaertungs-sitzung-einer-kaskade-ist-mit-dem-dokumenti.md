# Die Aushaertungs-Sitzung einer Kaskade ist mit dem dokumentierten Kostenabschluss strukturell nicht buchbar

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Flutter/Dart, sechste
  gebaute Kaskade, Abo-Auth für alle Rollen

## Was passiert ist

Beim Kostenabschluss der sechsten Kaskade ist aufgefallen, dass für die
**Aushärtungs-Sitzung** dieser Kaskade keine Ledger-Zeile existiert. Der
Architekt hatte sie in einer eigenen, abgeschlossenen Sitzung geplant
(Plan-Dokument, Fokus-String, zwei Commits), unmittelbar danach lief die
Vollautomatik, und der Closeout fand in einer **dritten** Sitzung statt.

Der dokumentierte Ablauf lautet:

```
./team-status.sh --rollen-abschluss <N> <domaene> "<notiz-rollen>" "<notiz-bau>"
python3 team/tools/kosten.py sitzung-messen --projekt .
./team-status.sh --architekt-abschluss <USD> <domaene> "<notiz>"
```

`sitzung-messen --projekt .` liest **immer nur das zuletzt geänderte
Transkript**. Zum Zeitpunkt des Closeouts ist das die Closeout-Sitzung selbst.
Die Aushärtungs-Sitzung liegt zwei Sitzungen zurück und wird nie gelesen — ihr
Betrag taucht in keiner Ausgabe auf, und es gibt **keine Meldung**, die auf sie
hinweist.

In diesem Projekt waren das **10,65 USD Abo-Gegenwert** — 39 % der gesamten
Architektenkosten dieser Kaskade. Sie wurden nur deshalb gebucht, weil der
Architekt die Transkript-Ablage von Hand nach der passenden Datei durchsucht
und `sitzung-messen` mit einem **ausdrücklich benannten Pfad** aufgerufen hat.
Das steht in keinem Briefing.

Die Größenordnung ist kein Einzelfall dieses Laufs: In derselben Installation
liegen die Aushärtungen früherer Kaskaden zwischen 8,7 und 34,8 USD.

## Wo es steckt

`team/prompts/rolle-architekt.md`, Abschnitt „Nach jedem Lauf (Closeout,
Pflicht)", Punkt 2. Er beschreibt zwei Quellen: die Laufkosten
(`--rollen-abschluss`) und **„meine eigene Sitzung"** (`--architekt-abschluss`).
„Meine eigene Sitzung" ist im Closeout-Kontext eindeutig die Closeout-Sitzung —
die Aushärtungs-Sitzung derselben Kaskade wird an keiner Stelle erwähnt.

Der Abschnitt kennt und benennt die verwandte Falle bereits, aber nur in der
anderen Richtung: **„Ein Closeout je Sitzung"** warnt davor, dass zwei
Closeouts in **einer** Sitzung denselben Betrag doppelt buchen (`BL-116`), und
verlangt dann die Rechnung „Rohwert minus bereits gebucht". Der umgekehrte Fall
— **eine** Kaskade über **mehrere** Sitzungen, von denen nur die letzte
gemessen wird — steht nicht da.

## Warum das jede Installation trifft

Der Ablauf ist derselbe in jeder Installation, die die Planungsregeln des Kits
befolgt:

1. Der Architekt härtet die nächste Kaskade aus (Planungsregel 2). Das ist
   laut Kit ausdrücklich **eigene Handarbeit** und laut Briefing das Teuerste,
   was der Architekt tut.
2. Der Stakeholder legt den Zeiger um und startet den Lauf. Zwischen Schritt 1
   und 2 gibt es **keinen** Buchungsschritt — das Briefing verbietet den
   Kostenabschluss in einer Loop-Stufe ausdrücklich und verweist auf den
   Closeout.
3. Der Closeout läuft nach dem Lauf, in einer neuen Sitzung (so verlangt es
   „Ein Closeout je Sitzung").

Damit ist die Aushärtungs-Sitzung zum Buchungszeitpunkt **niemals** die zuletzt
geänderte. Wer sich an den dokumentierten Ablauf hält, verliert sie — und zwar
lautlos: Das Ledger ist in sich konsistent, `--ledger-pruefen` meldet nichts
(es hält die archivierten Rohlogs gegen das Ledger, und für eine interaktive
Sitzung gibt es keinen Rohlog), und `--budget` zeigt eine plausible Summe. Der
Fehlbetrag ist nur sichtbar, wenn jemand die Transkript-Ablage von Hand mit dem
Ledger vergleicht.

Verwandt mit `BL-165` (`sitzung-messen` liest nur das zuletzt geänderte
Transkript und fasst es nie wieder an) und `BL-116` (zwei Buchungen aus einer
Sitzung). Beide beschreiben Symptome derselben Ursache: Die Messung ist an
„zuletzt geändert" gebunden, die Buchhaltung aber an „Kaskade".

Ob eine Installation überhaupt betroffen ist, hängt allein daran, ob die
Aushärtung zufällig in derselben Sitzung lag wie der vorige Closeout. In
diesem Projekt war das bei zwei Kaskaden so (dort wurde die Aushärtung
miterfasst) und bei dieser nicht.

## Was ich schon versucht habe

Nachträglich gebucht, indem `sitzung-messen` der Transkript-Pfad als
Positionsargument übergeben wurde:

```
python3 team/tools/kosten.py sitzung-messen <pfad-zum-transkript>.jsonl
```

Das funktioniert und ist die Grundlage jedes Vorschlags unten — die Fähigkeit
ist also schon da, sie hat nur keinen Aufrufer im Ablauf.

Drei Vorschläge, vom billigsten zum gründlichsten:

1. **Briefing-Zeile** (kostet nichts): In Punkt 2 des Closeout-Abschnitts
   ergänzen, dass **zwei** Architekten-Sitzungen zu einer Kaskade gehören —
   die Aushärtung und der Closeout — und dass die Aushärtungs-Sitzung über
   ihren Pfad gemessen und per `--addieren` gebucht wird. Bereits die
   bestehende Formulierung „Teil 1 von 2 / Teil 2 von 2" aus den Ledger-Notizen
   dieses Projekts zeigt, dass das Muster gemeint war; es steht nur nicht in
   der Anleitung.
2. **Ein Verb**, das die Lücke selbst findet, z. B.
   `kosten.py sitzung-lueckenpruefung --projekt .`: alle Transkripte auflisten,
   die jünger sind als die älteste Ledger-Zeile und in keiner Buchung
   vorkommen. Dafür müsste `--akteur-abschluss` die gemessene Transkript-ID in
   der Zeile ablegen — heute steht sie nur, wenn der Architekt sie von Hand in
   die Notiz schreibt.
3. **Die Aushärtung buchen, wo sie entsteht**: Am Ende der Aushärtung gibt der
   Architekt ohnehin die Scharfschalt-Sequenz aus (Planungsregel 4). Ein
   Buchungsschritt an dieser Stelle träfe die Sitzung, solange sie die zuletzt
   geänderte ist — dann greift auch die Regel „Ein Closeout je Sitzung"
   sauber, weil pro Sitzung genau einmal gebucht wird.

Vorschlag 1 ist die Sofortmaßnahme, 3 die eigentliche Reparatur: Sie bringt den
Buchungszeitpunkt dorthin, wo die Messgrundlage noch stimmt, statt ihn später
gegen die Mechanik von `sitzung-messen` zu erzwingen.

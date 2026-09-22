# Die Architektenkosten sind strukturell unerfasst, und kein Werkzeug zeigt die Luecke

- **Bezug**: BL-121
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, 29 gebaute Kaskaden

## Was passiert ist

In **einem** Closeout kamen **273,83 USD** unerfasster Architektenkosten
zusammen — aus **drei verschiedenen Ursachen**, von denen keine gemeldet wurde.

Zum Größenvergleich: Die Baukosten der abgeschlossenen Kaskade betrugen
**32,33 USD**. Die unerfassten Architektenkosten waren also das **Achtfache
des gesamten Laufs**, den sie abschlossen.

**Ursache 1 — eine nie gebuchte Aushärtungssitzung (22,36 USD).**
Das Architekten-Briefing sagt wörtlich, *„meine eigene Sitzung sind ZWEI"* —
die Aushärtung der Kaskade und der Closeout. Gebucht worden war nur der
Closeout. Die Aushärtungssitzung lag zwei Kaskaden zurück und war seitdem
unsichtbar.

**Ursache 2 — eine nach ihrer Buchung weitergewachsene Sitzung (+0,90 USD).**
Bekannt als `Kit-BL-116`; hier zum wiederholten Mal eingetreten.

**Ursache 3 — eine Sitzung über zwei Kaskaden (218,71 USD).**
Ein Transkript von 18 MB, laufend über vier Kalendertage, das die Aushärtung
**zweier** Kaskaden und die Begleitung beider Läufe enthielt. Komplett
ungebucht. `sitzung-messen` warnt hier korrekt (`Kit-BL-252`):

```
! Lange Sitzung: … Antworten, … Mio. Cache-Read-Token. Gemessene Faelle
  dieser Groesse waren regelmaessig MEHRERE Kaskaden in EINEM Fenster.
```

**Was keines der Werkzeuge zeigt:** `--ledger-pruefen` meldet 0 Warnungen (für
interaktive Sitzungen gibt es keinen Rohlog, gegen den es prüfen könnte),
`--budget` zeigt eine plausible Summe, und das Ledger ist in sich vollständig
stimmig. Sichtbar wird die Lücke **nur**, wenn jemand die Transkript-Ablage
gegen das Ledger hält.

**Genau das steht im Briefing — und genau das ist dreimal ausgefallen.**

## Wo es steckt

Zwei Stellen, und sie hängen zusammen:

1. **`team/tools/kosten.py`, Verb `sitzung-messen`.** Es misst **ein**
   Transkript und misst es **ganz**. Es kann weder sagen, welche Transkripte
   es im fraglichen Zeitfenster sonst noch gibt, noch ob eines davon schon
   gebucht ist — obwohl das Ledger in derselben Ablage liegt.
2. **Das Architekten-Briefing** (`team/prompts/rolle-architekt.md`). Dort steht
   das Verfahren vollständig und richtig beschrieben. Es ist aber eine
   **Gedächtnisleistung ohne Mechanik**: Wer es vergisst, bekommt keinen
   Hinweis, sondern ein stimmiges Ledger.

## Warum das jede Installation trifft

Das Kostenmodell des Kits misst die **automatisierten** Rollen zuverlässig —
sie schreiben Rohlogs, die Rohlogs werden gebucht und archiviert, und
`--ledger-pruefen` hält beide gegeneinander. Für die **interaktive** Rolle
existiert diese Kette nicht: kein Rohlog, keine Archivierung, keine
Gegenprobe.

**Die Folge ist keine Ungenauigkeit, sondern eine Schieflage.** Wer die
Wirtschaftlichkeit des Verfahrens an den Lauf-Deckeln misst — und dazu laden
die Deckel ein, weil sie pro Lauf durchgesetzt werden —, misst in diesem Feld
die **kleinere Hälfte**. Bei uns stand ein Lauf-Deckel von 85 USD einer
tatsächlichen Kaskadensumme von über 200 USD gegenüber, und das war kein
Regelbruch: Die Architektenkosten unterliegen keinem Lauf-Deckel.

Das trifft jede Installation, in der ein Mensch plant und ein Loop baut — also
die vorgesehene Betriebsart.

## Vorschlag

**Ein Verb, das die Gegenprobe macht, statt sie zu beschreiben.** Etwa
`sitzungen-pruefen`:

- listet die Transkripte der Projekt-Ablage im gewählten Fenster (nach
  Änderungszeit),
- nennt je Transkript die gemessene Summe,
- markiert, was im Ledger **nicht** vorkommt,
- und markiert, was dort mit einem **kleineren** Betrag vorkommt (das ist der
  `Kit-BL-116`-Fall, und er ist genau so erkennbar).

**Zwei Dinge, die die Umsetzung kennen muss**, beide bei uns aufgetreten:

**(a) Die Rollenläufe müssen ausgenommen werden.** Auch Ralph, Harry, Marv und
Frank schreiben Transkripte in dieselbe Ablage. Deren Kosten hängen an den
Rohlogs und sind über `--rollen-abschluss` bereits gebucht — wer sie
mitzählt, bucht doppelt. Bei uns waren das 34 der 47 Transkripte im Fenster;
sie sind über ihre Zeitstempel eins zu eins den Rollenlogs zuzuordnen.

**(b) `sitzung-messen` braucht ein Zeitfenster.** Eine Sitzung, die zwei
Kaskaden umspannt, lässt sich heute nicht aufteilen — das Werkzeug warnt
davor (`Kit-BL-252`), bietet aber kein Mittel. Ich habe das Transkript von
Hand nach dem Zeitstempelfeld zerlegt und die Hälften einzeln gemessen; die
Summe der Hälften traf die Gesamtmessung auf 0,0001 USD. Ein Paar
`--von`/`--bis` an `sitzung-messen` wäre die ganze Arbeit und macht die
Warnung erst handlungsfähig.

## Was ich schon versucht habe

- **`--ledger-pruefen`**: 0 Warnungen, vor und nach den Buchungen.
- **`--budget`**: plausibel, zeigt die Lücke nicht.
- **Von Hand**: Transkript-Ablage nach Änderungszeit sortiert, die
  Rollenläufe über ihre Zeitstempel ausgenommen, die verbleibenden
  Transkripte **einzeln über ihren Pfad** gemessen und gegen die
  Ledger-Notizen gehalten. Das funktioniert und hat die drei Ursachen
  gefunden — es ist aber Handarbeit, sie dauert, und sie fällt genau dann
  aus, wenn viel los ist.
- **Lokaler Fix: keiner.** Ein Verfahren, das dreimal ausgefallen ist, ist
  kein Aufmerksamkeitsproblem; es gehört ins Werkzeug.

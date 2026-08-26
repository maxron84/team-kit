# Eine Sitzung ohne Closeout hat keinen Ausloeser, der sie zum Buchen zwingt

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-08-26-eine-sitzung-ohne-closeout-hat-keinen-ausloeser-der-sie-zum.md
      ./kit-melden.sh ablegen  2026-08-26-eine-sitzung-ohne-closeout-hat-keinen-ausloeser-der-sie-zum.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-08-26-eine-sitzung-ohne-closeout-hat-keinen-ausloeser-der-sie-zum.md   # sonst: Pull Request

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
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Flutter/Dart mit SQLite;
  sieben gebaute Kaskaden, Abo-Auth, Ledger seit der ersten Kaskade lückenlos
  geführt.

## Was passiert ist

Beim Öffnen des Closeouts der siebten Kaskade hatte das Ledger **keine**
`architekt`-Zeile für diese Kaskade — obwohl der Plan zwei Tage zuvor
ausgehärtet und committet worden war. Die Suche nach dem Grund förderte einen
zweiten Fall desselben Tages zutage:

| Sitzung | Was darin entstand | nachgemessen |
|---|---|---|
| A | Nachlauf zur **vorigen** Kaskade: zwei offene Handprüfungen am Gerät bestanden, ein Hilfsskript auf echte Exit-Codes umgebaut, zwei Backlog-Einträge ans Kit gemeldet | **36,22 USD** |
| B | Aushärtung der **nächsten** Kaskade: Prototyp-Abgleich und Plandokument | **7,68 USD** |

Zusammen **43,90 USD Abo-Gegenwert**, die nie im Ledger standen. Beide
Sitzungen waren regulär, produktiv und haben committet — keine hat gebucht.

Gerettet wurde der Betrag nur, weil `kosten.py sitzung-messen` benannte
Transkripte liest und die zwei Dateien noch dalagen. Der Regelfall ist ein
anderer: Das Werkzeug liest ohne Argument das **zuletzt geänderte**
Transkript, und das ist beim nächsten Closeout ein drittes.

## Wo es steckt

In `team/prompts/rolle-architekt.md`. Die Regel ist dort vorhanden und
ausdrücklich begründet (Abschnitt zum Kostenabschluss, Absatz „Eine Sitzung
ohne Closeout bucht ihre Kosten selbst", mit Verweis auf `BL-165`):

> Ich buche deshalb am Ende einer reinen Planungssitzung selbst:
> `--architekt-abschluss <USD> <domaene> "Kaskade N+1 geplant" --kaskade <N+1>`.

Sie steht also da, sie ist verstanden, und sie hat trotzdem zweimal an einem
Tag nicht gegriffen.

## Warum das jede Installation trifft

**Der Unterschied ist nicht Disziplin, sondern Auslöser.** Ein Closeout hat
einen: Die Kaskade ist fertig, der Loop meldet „Ralph hat Feierabend", das
Briefing verlangt ein Abschluss-Doc, und der Kostenabschluss steht als Schritt
2 in derselben Liste. Eine reine Planungs- oder Nachbesserungssitzung hat
keinen. Sie **endet einfach** — der Mensch schließt das Fenster, sobald der
Plan committet ist, und in diesem Moment ist die Regel schon nicht mehr
lesbar, weil niemand mehr da ist, der sie liest.

Das trifft jede Installation, und zwar umso härter, je besser das Kit
funktioniert: Genau die Sitzungen ohne Closeout sind die, die das Briefing
selbst empfiehlt („nach einem gebuchten Closeout eine **neue** Sitzung für die
nächste Kaskade"). Die Empfehlung erzeugt den Fall, den die Regel abfangen
soll, und beide stehen im selben Dokument.

Erschwerend: Der Verlust ist **still**. `--ledger-pruefen` meldet für eine
Kaskade ohne `architekt`-Zeile nur einen *Hinweis*, keine Warnung („Legitim,
wenn der Architekt für diese Kaskade nichts abzurechnen hatte"), und dieser
Hinweis erscheint erst, wenn ohnehin jemand prüft. Der Statusbericht zeigt
stattdessen eine Zeile „Architekt K7 (Churn-Proxy, nicht im Gesamt enthalten)"
— eine Schätzung, die aussieht wie eine Erfassung.

## Was ich schon versucht habe

Nachgemessen und beide Sitzungen benannt gebucht (`--kaskade` explizit,
`--addieren` für die schon geschlossene Kaskade), Rechnung und Grund je im
Notiztext der Ledger-Zeile. `--ledger-pruefen` danach ohne Warnung.

**Lokal nichts gepatcht** — der Fund steckt im Briefing, also im Kit; ein
lokaler Eingriff hätte die bekannte Verfallszeit beim nächsten `--update`.

**Zwei Richtungen, die aus Feldsicht tragen würden** (Vorschlag, nicht
Anspruch):

1. **Den Auslöser dorthin legen, wo er entsteht.** Eine Aushärtung endet
   ohnehin mit einer Pflicht-Ausgabe, der Scharfschalt-Sequenz. Wenn der
   Kostenabschluss der Sitzung **Teil dieser Sequenz** wäre — als letzter,
   kopierfertiger Befehl mit vorausgefüllter Kaskadennummer —, hinge er an
   einem Ereignis statt an Erinnerung.
2. **Den stillen Fall laut machen.** Eine Kaskade, für die eine `ralph`-Zeile
   existiert, aber keine `architekt`-Zeile, hat mit Sicherheit einen
   ungebuchten Plan: Ohne Aushärtung gäbe es nichts zu bauen. Das ist als
   Warnung prüfbar, nicht nur als Hinweis.

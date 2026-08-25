# Die Ledger-Zeile traegt den kumulierten Wert, die Kit-BL-116-Rueckrechnung braucht den Zuwachs je Aufruf

- **Art**: Fehler am Kit (Doku/Verfahren, mit Geldfolge)
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter, fuenfte
  gebaute Kaskade, Abo-Betrieb (alle Rollen `auth abo`)

## Was passiert ist

Beim Kostenabschluss einer Kaskade wollte ich das Verfahren aus `Kit-BL-116`
anwenden, das das Architekten-Briefing so beschreibt:

> Geht das ausnahmsweise nicht, buche ich **Rohwert minus bereits gebucht**
> und schreibe die Rechnung in den Notiztext der Ledger-Zeile.

Die Lage war genau die vorgesehene: Eine Architekten-Sitzung hatte den Closeout
der Kaskade N gemacht **und danach in derselben Sitzung** die Kaskade N+1
ausgehaertet. Der Closeout war gebucht, die Aushaertung nicht.

Rohwert der Sitzung heute:

```
$ python3 team/tools/kosten.py sitzung-messen <transkript-der-sitzung>.jsonl
  ✓ Preistabelle geeicht an 61 abgerechneten Laeufen dieses Projekts
  GESAMT: 17.1695 USD
```

Bereits gebucht laut Ledger-Zeile derselben Kaskade: **44.2372**.
Rueckrechnung: 17.1695 − 44.2372 = **−27.07**.

Eine negative Buchung ist offensichtlich falsch, aber die naheliegende
Schlussfolgerung war es auch: „die Messung eines Transkripts ist nicht
reproduzierbar". Waere ich dabei geblieben, haette ich fuer die Aushaertung
**0.00** gebucht und rund 7.70 USD dauerhaft aus dem Ledger verloren — genau
der Schaden, gegen den `Kit-BL-116` gebaut wurde.

Die Gegenprobe an einem **zweiten**, ebenfalls doppelt gebuchten Transkript hat
es aufgeklaert:

```
$ python3 team/tools/kosten.py sitzung-messen <zweites-transkript>.jsonl
  GESAMT: 40.6713 USD
```

und im Ledger stehen dazu zwei Zeilen mit den Zuwaechsen 5.9094 und 34.7619 —
Summe **40.6713**, auf vier Nachkommastellen. **Die Messung ist also exakt
reproduzierbar.** Falsch war die Lesart der Ledger-Zeile.

## Wo es steckt

Nicht im Code, sondern an der Naht zwischen zwei Stellen, die beide fuer sich
richtig sind:

1. `team/tools/kosten.py`, `akteur-abschluss --addieren` schreibt in das
   USD-Feld den **kumulierten Zeilenwert**. Der bei diesem Aufruf gebuchte
   **Zuwachs** steht nur noch als Prosa im Notiztext (`… (addiert auf Bestand
   34.7619 USD, auth abo)`) — also als Differenz, die der Mensch selbst bilden
   muss, und nur, wenn genau diese Formulierung erhalten geblieben ist.
2. `team/prompts/rolle-architekt.md` formuliert die `Kit-BL-116`-Rueckrechnung
   als „Rohwert minus **bereits gebucht**". Das Feld, das man im Ledger
   ablesen kann, heisst faktisch „bereits gebucht **auf diese Zeile**" — nicht
   „bereits gebucht **aus diesem Transkript**". Solange eine Zeile nur eine
   Quelle hat, sind beide gleich; sobald zwei Sitzungen auf dieselbe
   Rolle+Kaskade addiert werden, laufen sie auseinander.

In meinem Fall trug die Zeile 44.2372 aus **zwei** Transkripten (34.7619 aus
dem einen, 9.4753 aus dem anderen). Der richtige Subtrahend war 9.4753, und
17.1695 − 9.4753 = **7.6942** ist der Betrag, der zu buchen war.

## Warum das jede Installation trifft

Die Regel steht im Briefing jeder Architekten-Instanz, und der Fall, den sie
regelt, ist der **Normalfall** eines produktiven Projekts: Closeout und
Aushaertung der naechsten Kaskade passieren gern in einer Sitzung — das
Briefing selbst empfiehlt zwar getrennte Sitzungen, nennt aber ausdruecklich
den Ausnahmefall und gibt die Formel dafuer.

Der Fehler ist zusaetzlich **still**: Es entsteht eine plausible Zahl, kein
Exit-Code, kein Warnbefund. `ledger-pruefen` haelt die archivierten Rohlogs
gegen das Ledger und sieht Architekten-Zeilen dabei nicht — sie haben keine
Rohlogs. Wer zu wenig bucht, merkt es nie; wer bei negativer Differenz nicht
stutzig wird, bucht null.

Und der Fehler wird **groesser, je laenger ein Projekt laeuft**: Je mehr
Kaskaden, desto mehr Zeilen mit `--addieren`, desto haeufiger die Lage, in der
die abgelesene Zahl der falsche Subtrahend ist.

## Was ich schon versucht habe

Nichts lokal gefixt — die Kit-Dateien sind unveraendert.

Aufgeklaert habe ich es durch die Gegenprobe an einem zweiten Transkript, das
seine gebuchten Zuwaechse exakt reproduziert. Das ist zugleich der Vorschlag,
wie sich der Fall billig entschaerfen liesse:

1. **Kleinster Eingriff (Doku)**: Im Architekten-Briefing „bereits gebucht"
   praezisieren zu „bereits **aus diesem Transkript** gebucht", mit dem
   Hinweis, dass das USD-Feld einer `--addieren`-Zeile der Summenwert ist und
   der Zuwachs nur im Notiztext steht.
2. **Belastbarer (Werkzeug)**: `akteur-abschluss` koennte den Zuwachs und —
   wo bekannt — den Basisnamen des gemessenen Transkripts als eigenes,
   maschinenlesbares Feld mitschreiben, statt ihn der Prosa zu ueberlassen.
   Dann ist die Rueckrechnung ablesbar statt rekonstruierbar.
3. **Billiger Airbag**: Ergibt „Rohwert minus bereits gebucht" einen
   **negativen** Wert, ist das nie eine gueltige Buchung, sondern immer ein
   Hinweis auf genau diese Verwechslung. Ein Satz an der Stelle der Formel
   haette mir die Forensik erspart.

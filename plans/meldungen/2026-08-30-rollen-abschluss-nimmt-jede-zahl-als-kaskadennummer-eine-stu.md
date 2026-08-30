# rollen-abschluss nimmt jede Zahl als Kaskadennummer — eine Stufennummer bucht plausibel und falsch

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, kompilierte Sprache mit
  eigenem Test-Runner (nicht Python), elf Kaskaden gebaut, rund 475 Tests

## Was passiert ist

Nach einem Vollautomatik-Lauf wurde der Kostenabschluss gefahren:

```
./team-status.sh --rollen-abschluss <N> <domaene> "<notiz>"
```

Für `<N>` wurde die **Stufennummer** eingesetzt (der `RALPH_CAP` der Kaskade,
hier 59) statt der **Kaskadennummer** (hier 11). Beide Zahlen stehen im
Plankopf direkt untereinander, beide sind zweistellig, und die Bedienung nennt
den Parameter nur `<kaskade>`.

Das Werkzeug hat anstandslos gebucht. Es entstanden zwei Ledger-Zeilen
(`roles` und `ralph`) mit `59` im Kaskadenfeld — Beträge korrekt, Summe
korrekt, Auth korrekt, nur unter einer Kaskade, die es nicht gibt.

**Nichts hat das gemeldet.** Das Ledger blieb in sich stimmig,
`--ledger-pruefen` lief ohne Befund zu dieser Sache, `--budget` zeigte eine
plausible Gesamtsumme. Aufgefallen ist es erst beim Closeout, als jemand die
Zeilen zur Kaskade sehen wollte und `kosten.py ledger --kaskade 11` **nichts**
zurückgab.

Der Beweis, dass die Diagnose stimmt, kam vom Prüfer selbst: Nach der
Handkorrektur des Feldes (`59` → `11`) meldete `--ledger-pruefen` sofort die
beiden echten Lücken —

```
[WARNUNG] 1 nummerierte Kaskade(n) mit ralph-Zeile und ohne architekt-Zeile: 11.
[WARNUNG] Kaskade 11 ist bereits gebucht (2 Zeile(n)), aber es liegen 3
          unarchivierte Log(s) in .ralph-logs/.team-logs.
```

Beide Befunde waren die ganze Zeit wahr. Unter `59` hat der Prüfer zu
Kaskade 11 vollständig geschwiegen, weil es zu Kaskade 11 nichts gab.

## Wo es steckt

- `team/tools/kosten.py`, Verb `rollen-abschluss` (und `ralph-abschluss`,
  das denselben Mechanismus teilt), Parameter `--kaskade`
- `team-status.sh`, `status_rollen_abschluss()` — die Oberfläche, die beide
  Verben nacheinander ruft und `<kaskade>` als ersten Stellungsparameter nimmt

Das Feld ist bewusst freitextfähig: Im selben Ledger stehen legitime
nicht-numerische Werte wie `vor-10` für Out-of-Loop-Fixserien. Eine reine
Zahlenprüfung würde also nichts helfen — `59` ist eine gültige Zahl.

## Warum das jede Installation trifft

Der Fehler steckt in `team/tools/` und in einem Entrypoint, nicht im
Produktivcode eines Projekts. Jede Installation hat dieselbe Bedienung,
dieselbe Zweideutigkeit zwischen Stufen- und Kaskadennummer und dieselbe
Stille danach.

Die Folgen sind still und dauerhaft: Das Ledger ist die einzige Quelle, die
einen frischen Clone überlebt (die Rohlogs liegen unter `.gitignore` und
werden beim Abschluss zusätzlich wegarchiviert). Eine falsch einsortierte
Zeile ist damit kein Anzeigefehler, sondern der endgültige Zustand — und sie
macht ausgerechnet den Prüfer blind, der die Lücke sonst gefunden hätte.

Verschärfend: Der Abschluss ist die **letzte** Handlung einer Kaskade, oft
nach einem langen Lauf, und die Zahl kommt aus demselben Plankopf wie der Cap.
Es ist genau die Stelle, an der ein Zahlendreher wahrscheinlich ist und am
längsten unentdeckt bleibt.

## Was ich schon versucht habe

Im Projekt von Hand korrigiert: Feld 2 der beiden Zeilen von `59` auf `11`
gestellt, Beträge unberührt, Vorzustand vorher gesichert. Danach die fehlenden
Buchungen normal nachgetragen; `--ledger-pruefen` meldet jetzt 0 Warnungen.

**Vorschlag, in der Reihenfolge meiner Vorliebe:**

1. **Rückfrage statt Annahme.** Beide Verben kennen `.ralph-plan` bereits —
   `architekt-abschluss` leitet die Nummer daraus ab, wenn `--kaskade` fehlt.
   Passt die **übergebene** Nummer nicht zu der aus `.ralph-plan`, sollte das
   Werkzeug abbrechen und beide Zahlen nennen („Plan sagt Kaskade 11, du hast
   59 übergeben — `--trotzdem` erzwingt die Buchung"). Das trifft genau den
   Fall und lässt `vor-10` & Co. unangetastet, weil eine benannte Kaskade
   bewusst übergeben wird.
2. **Plausibilitätsschranke.** Eine Nummer, die weit über der höchsten je
   gebuchten liegt, ist verdächtig — sie sprang hier von 10 auf 59. Billiger
   zu bauen, aber schwächer: Sie greift nicht bei einem Dreher wie `12` statt
   `11`.
3. **Nur Doku.** Den Parameter in Nutzung und Fehlermeldung `<kaskade-nr,
   NICHT stufe>` nennen. Kostet nichts, verhindert aber nichts — der Bediener
   liest die Nutzung genau dann nicht, wenn er die Zahl schon zu kennen glaubt.

Nicht empfohlen: das Feld auf Zahlen einzuschränken. Es würde diesen Fall
nicht fangen und die legitimen benannten Kaskaden kaputtmachen.

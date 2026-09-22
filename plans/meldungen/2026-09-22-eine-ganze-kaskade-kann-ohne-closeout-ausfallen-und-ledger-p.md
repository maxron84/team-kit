# Eine ganze Kaskade kann ohne Closeout ausfallen, und ledger-pruefen meldet 0 Warnungen

- **Bezug**: BL-120
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, ~1375 Tests, 29 gebaute Kaskaden

## Was passiert ist

Beim Closeout der Kaskade **29** kam heraus, dass Kaskade **28** nie
abgeschlossen worden war. Der Befund im Einzelnen:

- **keine** `roles`-Zeile, **keine** `ralph`-Zeile, **keine** `architekt`-Zeile
  im Ledger — die Kaskadennummer kam dort schlicht nicht vor;
- das Abschluss-Protokoll (`plans/kaskade-28-abschluss.md`) fehlte;
- ihre Rohlogs lagen **vier Tage unarchiviert** in `.ralph-logs/` und
  `.team-logs/` — fünf Stufenlogs und sechs Rollenlogs, zusammen 31,19 USD.

Gebaut war die Kaskade vollständig: Plandatei vorhanden, fünf Stufen
committet, `.ralph-state` weitergeschaltet, Red-Team-Sweeps gelaufen, vier
Funde gefixt. Es fehlte **ausschließlich** der Closeout.

**Die Lücke war im Begriff, sich selbst zu schließen — falsch.** Hätte ich
`--rollen-abschluss 29` ohne Nachsehen aufgerufen, wären die Logs der
Kaskade 28 **stillschweigend unter Kaskade 29 gebucht** und danach archiviert
worden. Die Fehlzuordnung wäre dauerhaft und der Beleg weg gewesen.

**`--ledger-pruefen` hat währenddessen nichts gemeldet** — weder vorher noch
nachher. Die Ausgabe nach allen Buchungen, wörtlich:

```
-- 0 Warnung(en), 4 Hinweis(e).
```

Die vier Hinweise betreffen `vor-12`, `vor-13`, `vor-17`, `vor-20` und lauten
jeweils *„keine architekt-Zeile. Legitim, wenn der Architekt für diese Kaskade
nichts abzurechnen hatte"*. Für die **komplett fehlende** Kaskade 28 gab es
**keinen einzigen** Hinweis.

Gefunden habe ich es nur, weil ich vor dem Buchen aus eigenem Antrieb das
Ledger gegen die Logordner gehalten habe. Ohne diesen Schritt wäre es nie
aufgefallen.

## Wo es steckt

`team/tools/kosten.py`, Verb `ledger-pruefen`.

Die Prüfung hält die **archivierten Rohlogs gegen das Ledger** — also eine
zweite Quelle, und das ist richtig gedacht. Sie kann aber konstruktiv nur
Kaskaden sehen, die im Ledger **vorkommen**. Eine Kaskade, die dort gar keine
Zeile hat, liegt außerhalb ihres Sichtfelds; für sie gibt es auch nichts
Archiviertes, gegen das man halten könnte. Der Prüfling definiert die
Prüfmenge — das ist dieselbe Bauform, die das Kit an anderer Stelle selbst als
Feld-Lehre führt (`Kit-BL-1`: *ein Bericht, der seine Kennzahl aus derselben
Quelle zieht wie das Geprüfte, bestätigt einen Fehler, statt ihn zu zeigen*).

## Warum das jede Installation trifft

Der Closeout ist **menschlich ausgelöst**. Das Kit hält dazu bereits fest, dass
eine Sitzung ohne Closeout ihre Kosten selbst bucht (`Kit-BL-165`) — aber
genau dieser Auslöser kann ausbleiben, wenn eine Sitzung einfach endet. Dann
fehlt nicht eine Zahl, sondern der **gesamte** Abschluss einer Kaskade: Kosten,
Protokoll und Archivierung.

Jede Installation baut Kaskade auf Kaskade, und die Lücke wächst still:
Solange die nächste Kaskade gebaut wird, verschiebt sich die Fehlzuordnung
weiter, und jede Buchung macht den ursprünglichen Zustand unwiederbringlicher
(die Rohlogs werden beim Buchen archiviert).

## Vorschlag

Die drei Quellen liegen in **jeder** Installation vor und sind maschinell
lesbar:

1. **Die Kaskaden-Plandateien** (`<planordner>/ralph-kaskade-*.md`,
   `<planordner>/team-kaskade-*.md`). Sie entstehen bei jeder Scharfschaltung
   genau einmal — das Kit benutzt sie in `Status-Altlast` bereits als *„die
   einzige maschinell lesbare Kaskadengrenze im Repo"*.
2. **Die Stufenlogs** (`.ralph-logs/stufe-*.json`) bzw. das Stufenarchiv.
3. **Die Kaskadennummern im Ledger.**

Eine Nummer, die (1) **und** (2) kennen, die aber in (3) fehlt, ist ein
Befund — und zwar eine **Warnung**, kein Hinweis. Vorschlag für den Wortlaut:

```
WARNUNG: Kaskade 28 hat eine Plandatei und gelaufene Stufen, aber KEINE
  Ledger-Zeile. Entweder fehlt ihr Closeout, oder ihre Kosten sind unter
  einer anderen Nummer gebucht.
```

**Die Gegenprobe zu diesem Vorschlag sollte in beide Richtungen laufen** —
sonst wird die Prüfung grün, indem sie nichts mehr findet: ein Fall mit
fehlender Ledger-Zeile muss **rot** werden, und ein regulär abgeschlossener
Satz von Kaskaden muss **still** bleiben.

**Eine Abgrenzung, die in die Umsetzung gehört:** Eine Kaskade, die gerade
läuft, hat naturgemäß noch keine Ledger-Zeile. Die Prüfung darf deshalb nur
auf Nummern anschlagen, die **kleiner** sind als die aktuell aktive (aus
`.ralph-plan` bzw. `.ralph-state` ableitbar) — sonst meldet sie bei jedem
zweiten Aufruf einen Fehlalarm und wird nicht mehr gelesen.

## Was ich schon versucht habe

- **`--ledger-pruefen` vor und nach den Buchungen**: beide Male 0 Warnungen.
- **`--budget`**: zeigt eine plausible Summe; die fehlende Kaskade ist dort
  nicht zu sehen, weil eine Summe über vorhandene Zeilen keine fehlende Zeile
  kennt.
- **Von Hand repariert**: Logs der neueren Kaskade beiseitegelegt, die ältere
  mit `--rollen-abschluss 28 … --trotzdem` gebucht (der `BL-220`-Wächter
  schlug korrekt an, weil `.ralph-plan` schon auf 29 zeigte), Logs
  zurückgelegt, dann die neuere gebucht. Das funktioniert, ist aber
  Handarbeit und setzt voraus, dass man das Problem **vorher** kennt.
- **Lokaler Fix: keiner.** Der gehört ins Kit, nicht in eine Kopie.

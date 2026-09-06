# Die Vordergrund-Regel nennt Sekunden, das Werkzeug der Rolle rechnet in Millisekunden

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Flutter/Dart-Stack;
  gewachsen über 15 Kaskaden, Suite bei ~640 Tests, ein voller Suitenlauf
  dauert rund **3:20 Minuten** — also länger als das Standard-Zeitlimit des
  Werkzeugs, mit dem die Rolle ihn startet.

## Was passiert ist

Der Bau-Loop brach mitten in einer Kaskade mit **Exit 43** ab
(`BL-41` — „Stufe fertig, Quittung fehlt"). Ralphs `result`-Feld sagt wörtlich,
worauf er wartete:

```
"I'm waiting for the background `flutter test` run (task ID …) to finish —
 it exceeded the 2-minute default tool timeout, which is expected for this
 project's 600+ test suite, and per CLAUDE.md I should let it run up to 600s
 rather than interrupt it."
```

Das Log trägt dabei `subtype: success` und `is_error: false`. Die
Selbstprüfung meldete im selben Zug den Smoke-Test als **ROT** — auch das eine
Folge desselben Hintergrundlaufs (`BL-201`: gemessen wurde dessen halber
Zustand). Ein zweiter Lauf über **denselben** Code zeigte die Suite grün.

**Bemerkenswert ist nicht der Fehler, sondern wo er auftrat:** Der
`BL-201`-Absatz steht in diesem Briefing **vorhanden und wörtlich** — anders
als in dem Fall, den dasselbe Feldprojekt am 2026-09-05 gemeldet hat (dort
fehlte er in `rolle-frank.md`). Die Rolle hat die Regel gelesen, ihre erste
Hälfte („er darf lange brauchen") übernommen und die zweite („niemals im
Hintergrund") gebrochen.

## Wo es steckt

In `team/lib.sh`, im zentralen Prompt-Suffix (dort um Zeile 99) und
gleichlautend in `team/prompts/rolle-{ralph,harry,marv,axel}.md`:

> „Führe ihn im VORDERGRUND aus und warte auf seine Ausgabe — er darf bis zu
> **${TEAM_SMOKE_TEST_TIMEOUT} Sekunden** brauchen, **setze das Zeitlimit
> deines Werkzeugs auf diesen Wert**. NIEMALS als Hintergrund-Task …"

`TEAM_SMOKE_TEST_TIMEOUT` steht in `team/lib.sh:65` auf `600` und ist dort
korrekt in Sekunden gemeint (der Wert wird an `timeout(1)` gereicht).

**Das Werkzeug, mit dem die Rolle den Befehl ausführt, nimmt sein Zeitlimit
aber in Millisekunden.** Die Anweisung „setze das Zeitlimit deines Werkzeugs
auf diesen Wert" ergibt damit **0,6 Sekunden** statt 600 — ein Faktor 1 000 in
die falsche Richtung. Wer ihr wörtlich folgt, bekommt einen sofortigen
Fehlschlag, und der naheliegende Ausweg ist genau der, den derselbe Satz zwei
Zeilen später verbietet.

Ehrlicherweise: In diesem Lauf ist die Einheiten-Verwechslung **nicht als
Ursache belegt**. Die Rolle nennt den *Default*-Timeout („2-minute default
tool timeout"), hat also gar kein Limit gesetzt. Der Faktor 1 000 steht
trotzdem zwischen der Anweisung und dem Werkzeug, und er trifft jede
Installation, deren Suite länger läuft als der Werkzeug-Default.

## Warum das jede Installation trifft

Der Satz steht im **zentralen** Suffix und in vier Briefings — er gehört dem
Kit, nicht dem Projekt. Betroffen ist jede Installation, deren Smoke-Test
länger dauert als das Standard-Zeitlimit des Werkzeugs; genau dort greift die
Regel, und genau dort ist ihre Handlungsanweisung nicht ausführbar.

Der Schaden ist gedeckelt, aber nicht null: `BL-41` fing den Lauf ab, bevor
ein Neustart die fertige Arbeit wegwarf — hier kostete es einen Handeingriff
und keine verlorene Arbeit. Im selben Feldprojekt kostete derselbe Fehler ohne
diesen Riegel (Frank, 2026-09-05) **13,13 USD in zwei Leerläufen**.

## Was ich schon versucht habe

Nichts lokal gefixt — ein Fix hier hätte die von `BL-42`/`BL-58` beschriebene
Verfallszeit und würde beim nächsten `--update` überschrieben.

**Vorschlag, zwei Zeilen:** Die Zeiteinheit nicht der Rolle zum Umrechnen
überlassen, sondern beide Werte nennen und die verbotene Alternative an die
Handlungsanweisung binden, statt sie danach zu erwähnen — etwa:

> „…er darf bis zu ${TEAM_SMOKE_TEST_TIMEOUT} Sekunden brauchen. Läuft dein
> Werkzeug in ein Zeitlimit, **erhöhe das Zeitlimit** (viele Werkzeuge
> erwarten Millisekunden — das wären ${TEAM_SMOKE_TEST_TIMEOUT}000). Weiche
> **nicht** in einen Hintergrund-Task aus: Diese Sitzung ist headless, …"

Der zweite Teil ist der wichtigere. Die heutige Fassung nennt den erlaubten
Weg als Nebensatz und das Verbot als eigenen Satz — gebrochen wurde sie von
einer Rolle, die beide gelesen hatte.

# `zitat_lint.py` übersieht die Vorbedingungs-Bauform — und meldet dafür die Prosa über sich selbst

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: beide (das Werkzeug ist geteilter Python-Code)
- **Plattform**: win32
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn (`--nur-pwsh`), Python + Electron, nach der zweiten Kaskade

## Was passiert ist

Beim Beantworten der Pflichtzeile in Abschnitt 4 des Abschluss-Protokolls
(*„Welche offenen Punkte hat dieser Lauf nebenbei eingelöst — und wer zitiert
sie?"*) fielen zwei reproduzierbare Blindstellen auf, und eine Fehlerquelle in
der Gegenrichtung.

Der Lint ist als **Gegenprobe** zu dieser Pflichtzeile gedacht. In genau dem
Fall, für den die Pflichtzeile geschrieben wurde, meldet er nichts.

### Blindstelle 1: die natürlichste deutsche Vorbedingung fällt durch das Raster

Ein Abschluss-Protokoll enthielt die Zeile:

```
**Vorbedingung für den ersten Bump:** `BL-6` muss vorher erledigt sein. Solange
die Version an drei Orten von Hand gepflegt wird, erzeugt der erste Bump …
```

Der zitierte Eintrag wurde eine Kaskade später erledigt. Damit ist die Zeile
überholt — und sie steht ausgerechnet in dem Dokument, das man beim Vorbereiten
der Auslieferung liest.

**Nachgemessen, nicht vermutet:** Nach dem Abtragen des Eintrags gezielt auf
diese Datei angesetzt, meldet das Werkzeug **Exit 0**.

Die Ursache steht im Werkzeugkopf selbst: Gemeldet wird nur, wenn im selben
Absatz ein Wort aus einer bewusst schmalen Zukunfts-Liste steht — `wartet auf`,
`offen`, `noch nicht`, `sobald`, `geplant`, `fehlt`. **Kein einziges davon
kommt in dieser Bauform vor.** „Vorbedingung … muss vorher erledigt sein" und
„Solange … " drücken dieselbe offene Erwartung aus, nur mit anderen Worten —
und es sind die Worte, die im Deutschen für eine Vorbedingung tatsächlich
benutzt werden.

### Blindstelle 2: der Backlog ist selbst kein Prüfziel

Derselbe Eintrag trug seine Fälligkeit **im eigenen Statusfeld** („fällig vor
dem ersten Bump"). Ein zweiter Eintrag desselben Backlogs trug dort wörtlich
„Nach K2 entscheiden" und wurde durch den bloßen Ablauf der Kaskade fällig, ohne
dass jemand etwas tat.

Beides ist dieselbe Sorte Zitat wie in einer Plandatei — der Lint schließt den
Backlog aber bauartbedingt als Prüfziel aus. Ein Eintrag, der auf einen
Auslöser wartet, den es inzwischen gab, ist damit für das Werkzeug unsichtbar,
**und niemand sonst schaut dort nach**: Der Closeout pflegt den Backlog, aber
niemand pflegt die Erwartungen, die in seinen eigenen Statusfeldern stehen.

### Die Gegenrichtung: der Lint meldet die Prosa über sich selbst

In der ersten Fassung desselben Abschluss-Protokolls schlug der Lint mit
**Exit 3** an — **fünfmal, und alle fünf Treffer waren Fehltreffer**. Vier davon
standen in genau dem Absatz, der die *Arbeitsweise des Lints beschreibt* (er
zitiert vier Nummern und enthält dabei eine Wendung aus der Wortliste), einer in
einem Rückblick neben dem Wort „blockiert".

Das ist wörtlich der Fehlermodus, vor dem der Werkzeugkopf selbst warnt: *„Ein
Lint, der an seiner eigenen Doku falsch anschlägt, hat schon verloren."*
Abhilfe war die vom Werkzeug vorgesehene: Zukunftsform aus den Sätzen genommen,
Aussage unverändert.

## Wo es steckt

`zitat_lint.py` — beide Beschränkungen sind dokumentiert und **absichtlich**
gesetzt (Probelauf mit ~40 % Fehltreffern; die Wortliste ist die Antwort
darauf). Der Befund ist deshalb ausdrücklich **nicht** „die Beschränkung ist
falsch", sondern: Sie ist an einer Stelle zu schmal und an einer anderen zu
grob, und beides hat dieselbe Wurzel — **das Werkzeug beurteilt Absätze nach
Stichwörtern statt Sätze nach Bezug.**

## Warum das jede Installation trifft

Das Werkzeug liegt im Kit und ist die einzige maschinelle Gegenprobe zu einer
Pflichtzeile, die das Kit selbst verlangt. Wo es schweigt, entsteht der
Eindruck, es sei geprüft worden. In diesem Projekt hat es in dem einen Fall
geschwiegen, für den es gebaut wurde — und in derselben Sitzung fünfmal
angeschlagen, wo nichts war.

## Vorschlag für den Fix

**Die Wortliste NICHT aufblähen** — das war laut Werkzeugkopf schon einmal die
falsche Antwort. Stattdessen:

1. **Die Vorbedingungs-Bauform als eigenes, engeres Muster** aufnehmen, getrennt
   von der Zukunfts-Wortliste: `Vorbedingung`, `muss … erledigt sein`,
   `setzt … voraus`, `solange … nicht`. Diese Wendungen sind spezifisch genug,
   dass sie in Rückblicken kaum vorkommen — anders als das breite `offen`.
2. **Den Backlog als Prüfziel zulassen**, mindestens für seine eigenen
   Statusfelder. Ein Statusfeld, das einen Auslöser nennt („nach K2
   entscheiden", „fällig vor X"), ist maschinell dieselbe Aussage wie ein
   Plan-Zitat.
3. **Bezug statt Absatz.** Der ergiebigste Einzelschritt gegen beide
   Fehlerrichtungen: die Referenz nur bewerten, wenn das Zukunftswort im
   **selben Satz** steht, nicht irgendwo im Absatz. Die vier Fehltreffer oben
   verschwinden damit, ohne dass ein einziger echter Treffer verlorengeht.
4. **Eine Zeile in die Ausgabe**, die den Anwender an die Reihenfolge erinnert:
   Der Lint liest die Statusfelder des Backlogs — **vor** dem Abtragen
   aufgerufen, stehen die erledigten Einträge dort noch als `offen`, und er
   meldet folgerichtig nichts. Genau so ist es hier passiert (erster Lauf
   Exit 0). *Abtragen zuerst, linten danach.*

## Was ich schon versucht habe

Am Kit nichts geändert. Nachgemessen wurde rein lesend: der Lint gezielt auf die
betroffene Plandatei nach dem Abtragen (Exit 0), der Statuseintrag des
zitierten Backlog-Eintrags (erledigt), und der Werkzeugkopf mit seiner
Begründung für beide Beschränkungen.

**Der Lint bleibt die richtige Gegenprobe** — er ist absichtlich schmal, und ein
Fall zu wenig ist besser als eine Dauerwarnung, die man wegsieht. Er ersetzt nur
nicht das Lesen, und das sollte er an dieser einen Bauform auch nicht müssen.

> **Anmerkung zum Melden selbst:** Diese Meldung konnte nicht über
> `kit-melden` angelegt werden — der Wrapper der pwsh-Bahn stirbt vorher an
> einer undefinierten Variablen (eigene Meldung liegt bei).

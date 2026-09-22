# zitat_lint meldet abgeschlossene Dokumente und entwertet sich damit selbst

- **Bezug**: BL-123
- **Art**: Fehler
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, 29 gebaute Kaskaden, ~30 Plandateien

## Was passiert ist

`team/tools/zitat_lint.py` im Closeout aufgerufen, wie das
Architekten-Briefing es verlangt. Ergebnis: **10 veraltete Zitate, Exit 3.**

**Alle zehn liegen in abgeschlossenen Dokumenten:**

| Datei | Treffer |
|---|---|
| Abschluss-Protokolle der Kaskaden 1, 2, 8, 12, 17 | 7 |
| ein Beleg-Dokument zu einer abgeschlossenen Kaskade | 1 |
| das Beutebuch-**Archiv** | 2 |

**Null** Treffer in den Dateien, für die der Lint gedacht ist: der
Skizzen-/Roadmap-Datei, dem Backlog, dem aktiven Plan.

Die ältesten Treffer sind über zwanzig Kaskaden alt. Einer meldet ein
Abschluss-Protokoll, das ausdrücklich festhält, der Punkt sei *„vom
`zitat_lint` gemeldet, bewusster Rückblick, kein Befund"* — der Lint meldet
also seine eigene, bereits dokumentierte Fehlmeldung ein weiteres Mal.

## Wo es steckt

`team/tools/zitat_lint.py`, in der Auswahl der geprüften Dateien.

Der Lint prüft alle Plandateien gleich. Das Briefing hält seine Absicht klar
fest — er soll Dateien finden, *„die einen erledigten Eintrag noch als offene
Frage zitieren"*, damit beim **Vorlegen der Kandidaten** keine Option
auftaucht, die es nicht mehr gibt. Diese Absicht zielt auf **vorwärts
gerichtete** Dokumente.

Ein Abschluss-Protokoll ist das Gegenteil: ein **Rückblick**, der festhält,
was zu seinem Zeitpunkt offen war. Dass ein darin zitierter Eintrag später
erledigt wurde, ist kein Mangel des Protokolls, sondern Fortschritt — und
nachträglich umzuformulieren wäre Geschichtsfälschung.

## Warum das jede Installation trifft

**Die Trefferzahl wächst monoton mit der Zahl der Kaskaden.** Jedes neue
Abschluss-Protokoll zitiert offene Einträge; jeder dieser Einträge wird
irgendwann erledigt; ab da meldet der Lint ihn für immer.

Das Briefing sagt, Exit 3 sei *„kein Blocker, der Lint urteilt über Prosa"* —
richtig, und genau deshalb ist das Rauschen gefährlich statt bloß lästig: Ein
Werkzeug, dessen Ausgabe zu 100 % aus Nicht-Befunden besteht, wird nicht mehr
gelesen. **Bei uns war das in diesem Closeout genau so:** Hätte in den zehn
Zeilen ein echter Befund gestanden, hätte ich ihn im Rauschen mitabgehakt.

Der Lint ist ausdrücklich *„absichtlich schmal gehalten und meldet lieber
einen Fall zu wenig als dauernd das Falsche"*. Dieser Anspruch ist an dieser
Stelle nicht eingelöst.

## Vorschlag

**Abschlussdokumente und Archive aus der Prüfmenge nehmen.** Beide sind an
ihrem Namensmuster erkennbar und in jeder Installation gleich benannt, weil
das Kit sie selbst so anlegen lässt:

- `<planordner>/kaskade-*-abschluss.md`
- `*-archiv.md`

**Eine Alternative, falls ein Pfadausschluss zu grob erscheint** — und dieser
Einwand ist berechtigt, ein ausgeschlossener Pfad ist dauerhaft blind: statt
auszuschließen, die Treffer in **zwei Gruppen** drucken und nur die erste
zählen. Etwa:

```
-- 0 Befund(e) in aktiven Planungsdateien.
   (10 weitere in Abschlussprotokollen und Archiven — Rueckblicke,
    nicht mitgezaehlt. Mit --auch-rueckblicke anzeigen.)
```

Das hält die Zahl ehrlich, macht den Exit-Code brauchbar und nimmt dem
Maintainer die Entscheidung nicht ab. **Diese Variante würde ich vorziehen**,
weil sie die Fundstellen nicht verschwinden lässt — die Erfahrung dieses
Projekts mit Pfadausschlüssen ist schlecht: Sie kaufen Ruhe und machen ein
ganzes Verzeichnis blind.

**Gegenprobe in beide Richtungen, damit der Fix nicht grün wird, indem er
nichts mehr findet:** ein erledigter Eintrag, der in einer **aktiven**
Plandatei als offene Frage zitiert wird, muss weiterhin **gemeldet** werden;
derselbe Satz in einem Abschlussprotokoll darf die gezählte Summe **nicht**
erhöhen.

## Was ich schon versucht habe

- **Alle zehn Treffer einzeln gelesen** und als bewusste Rückblicke bewertet;
  die Bewertung steht im Abschluss-Protokoll dieser Kaskade, damit sie nicht
  jeder Closeout neu vornimmt.
- **Lokaler Fix: keiner.** Der Lint liegt in `team/`, ein Eingriff hier
  verfiele beim nächsten `--update`.

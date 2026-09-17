# Der Fremdfilter hat zwei blinde Flecken - und im Rollback kosten sie uncommittete fremde Arbeit

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1 plus Unreleased-Stand
- **Bahn**: pwsh (der Befund gilt für beide Bahnen)
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python und Electron, 25
  Kaskaden gebaut, rund 240 Testdateien. Ein Mensch und mehrere Rollen
  arbeiten in **einem** Arbeitsbaum.

> **Nachtrag zur Meldung *„Drei von vier Commit-Stellen umgehen den
> Fremdfilter, den das Kit dafür hat"*** (gleicher Tag, gleiches Feld). Dort
> ging es darum, dass drei Commit-Stellen `team_eigene_pfade` nicht benutzen.
> Hier geht es um den Filter **selbst**: Auch wo er benutzt wird, trennt er
> zwei Fälle nicht — und einer davon **löscht** fremde Arbeit, statt sie nur
> falsch zuzuordnen. **Diese Meldung wiegt schwerer als die erste.** Sie steht
> getrennt, weil sie einen eigenen Fix braucht: Die erste ist eine Zeile je
> Aufrufstelle, diese ist eine Frage des Verfahrens.

## Was passiert ist

Ein Mensch arbeitete neben einem laufenden Loop. Die Frage war, was passiert,
wenn beide **dieselbe** Datei anfassen. Die Antwort am Quelltext ist: Der
Filter merkt es nicht, und der Rollback räumt anschließend auf.

`team_guard_fremdpfade` definiert „fremd" als: *stand beim Rollenstart im
Schnappschuss* **und** *ist seither byte-identisch* (`git hash-object`
unverändert). Daraus folgen zwei blinde Flecken:

| Lage | Hash gegen Schnappschuss | gilt als | Folge |
|---|---|---|---|
| Nur der Mensch fasst die Datei an | unverändert | **fremd** | nicht gestagt, nicht zurückgesetzt — **korrekt** |
| **Beide** fassen dieselbe Datei an | verändert | **eigen** | voll gestagt inkl. fremder Hunks; im Rollback zurückgesetzt |
| Der Mensch fasst sie **während** des Laufs erstmals an | steht gar nicht im Schnappschuss | **eigen** | dito — **auch wenn die Rolle sie nie berührt hat** |

**Die dritte Zeile ist die breitere Lücke.** `team_guard_schnappschuss` läuft
**einmal**, in `team_guard_begin`, und hält nur fest, was in **diesem Moment**
schmutzig ist. `team_guard_fremdpfade` iteriert ausschließlich über diesen
Schnappschuss. Was danach entsteht, kann per Konstruktion nie als fremd
erkannt werden.

**Und die scharfe Kante ist der Rollback, nicht der Commit.**
`team_rollback_rolle` sammelt `git diff --name-only <StartHash> HEAD` plus
`git status --porcelain`, filtert mit `team_fremd_ausfiltern` — beide blinden
Flecken passieren diesen Filter — und übergibt an `team_pfade_zuruecksetzen`.
Dort steht:

    git checkout <StartHash> -- <pfad>

`StartHash` ist **HEAD bei Rollenstart**, also ein **Commit**, nicht der
Arbeitsbaumstand. Die Datei wird damit auf ihren *committeten* Inhalt gesetzt.
Uncommittete fremde Arbeit an dieser Datei ist danach **weg** — nicht bloß
falsch zugeordnet, sondern nicht wiederherstellbar.

**Ein fehlkommittierter Hunk ist sichtbar und behebbar. Dieser Verlust ist
beides nicht.**

## Wo es steckt

`lib` (pwsh: `lib.psm1`, bash: `lib.sh`), drei Funktionen:

- `team_guard_schnappschuss` — wird nur in `team_guard_begin` gerufen, also
  einmal je Rollenlauf.
- `team_guard_fremdpfade` — iteriert nur den Schnappschuss; Byte-Gleichheit
  ist das einzige Kriterium.
- `team_pfade_zuruecksetzen` / `team_rollback_rolle` — setzen pfadweise auf
  einen **Commit** zurück.

**Der Docstring von `team_rollback_rolle` benennt den Geschädigten selbst.** Er
sagt, `BL-114` sei geschrieben worden, weil ein blankes `reset --hard` *„eine
parallele Sitzung, eine Handänderung, eine noch nicht committete
Closeout-Ausgabe des Architekten"* traf. Genau diese Closeout-Ausgabe entsteht
**während** eines Laufs — blinder Fleck 3. Der namentlich genannte Geschädigte
von `BL-114` ist über den heutigen Filter weiterhin erreichbar.

## Warum das jede Installation trifft

Der Befund sitzt vollständig in `lib` und gilt für beide Bahnen. Jede
Installation, in der ein Mensch neben dem Loop arbeitet, hat ihn — und das ist
der Normalfall, nicht die Ausnahme.

**Das Kit ahnt die Lage bereits, kann sie mit dem heutigen Mittel aber nicht
abdecken:** `team_guard_begin` warnt laut, wenn der Baum beim Rollenstart
schmutzig ist, ausdrücklich damit *„der Mensch am Terminal weiß, dass hier zwei
Schreiber unterwegs sein könnten"*. Diese Warnung sieht nur den Zustand **bei
Start**. Blinder Fleck 3 liegt per Definition dahinter.

**Wichtig für die Erwartungshaltung, und deshalb hier ausdrücklich:** Kein
Pfadfilter kann Fall 2 lösen. Git stagt **Dateien**, nicht Urheberschaft;
hunk-genaues Stagen gibt es nur interaktiv, und headless kann niemand
zuverlässig sagen, welche Hunks seine sind. Ein Filter, der das verspricht,
verkauft mehr Sicherheit, als er hat.

## Was ich schon versucht habe

**Lokal nichts gefixt** — der Befund sitzt in `lib` und verfällt beim nächsten
`--update`; in diesem Projekt dreimal nachgewiesen.

Behelf im Feld: die Regel *„nicht committen, während eine Rolle läuft"*. Sie
deckt den Commit ab, **nicht** den Rollback: Der greift auch dann, wenn der
Mensch gar nichts committet, sondern nur eine Datei offen liegen hat.

**Vorschläge, nach Wirkung geordnet:**

1. **Sofort und billig: den Schnappschuss ein zweites Mal ziehen**, unmittelbar
   vor Commit und Rollback, und gegen den ersten halten. Weicht etwas ab, das
   die Rolle nicht selbst angefasst hat, **abbrechen und melden** statt raten.
   Das löst Fall 2 nicht, verwandelt aber einen stillen Datenverlust in eine
   laute Meldung — und deckt Fall 3 vollständig ab.
2. **Zurücksetzen auf den Arbeitsbaumstand, nicht auf den Commit.** Der
   Schnappschuss hält bereits `git hash-object` je schmutzigem Pfad, die Blobs
   liegen also in der Objektdatenbank und lassen sich zurückschreiben. Damit
   verlöre der Rollback seine Schärfe gegen uncommittete fremde Arbeit, ohne
   dass sich sonst etwas ändert.
3. **Den Menschen unter denselben Lock stellen.** Der Loop-Lock ist
   OS-durchgesetzt und schließt zwei Schreiber wirklich aus — bisher aber nur
   zwei *Pipelines*. Nebenläufigkeit vermeiden schlägt Nachsortieren.
4. **Geteilte Dateien feldgenau schreiben.** Das Kit macht es beim Fundbuch
   schon vor: Ein Werkzeug setzt den Feldwert *„und sonst nichts"*. Läuft jeder
   Zugriff auf gemeinsame Dateien so, ist eine gemeinsam berührte Datei kein
   Konflikt mehr, sondern zwei disjunkte Feldänderungen.
5. **Die Grenze dokumentieren.** Solange 1–4 nicht stehen, gehört in die
   Bedienanleitung, dass der Filter **ganze Dateien** trennt und bei
   gemeinsamer Berührung blind ist. Heute liest sich die Zusicherung
   *„verwirft den gesamten Beitrag eines Rollenlaufs, aber NUR seinen"*
   stärker, als sie ist.

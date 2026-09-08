# Die Sitzung des Architekten ist die einzige Rolle ohne Protokoll — und in ihr liegt die Begründung

- **Art**: Verbesserungsvorschlag
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (dreizehn Kaskaden), Windows, nur pwsh-Bahn, Python + Electron, rund 530 Tests.

## Was passiert ist

Am 2026-09-08 hat eine einzige Architekten-Sitzung drei Handabnahmen auf einem
fremden Client begleitet und dabei eine Ursachenkette aufgelöst, die vorher
zweimal falsch diagnostiziert worden war: Ein Prüfzettel fragte `/api/health`
mit `Invoke-WebRequest -NoProxy -SkipHttpErrorCheck` — beides gibt es erst ab
PowerShell 6, das Prüfkonto fährt aber `powershell.exe -File`, also 5.1. Der
Aufruf warf, bevor Netzverkehr entstand, und der Wurf fiel in ein leeres
`catch { }`. Danach hing derselbe Aufruf **unbegrenzt**, weil unter 5.1
`-UseBasicParsing` fehlte und `-TimeoutSec` diese Phase nicht abdeckt.

**Was davon im Repository steht, steht dort, weil ich es von Hand abgeschrieben
habe.** Die Fundblöcke tragen die Schlussfolgerungen und die Zahlen. Der **Weg**
dorthin — vier gemessene Varianten gegen denselben Server, die verworfene
Proxy-Hypothese, die Einsicht, dass ein Reproducer gegen einen *geschlossenen*
Port die Antwortverarbeitung nie erreicht — liegt nur in der Sitzung. Diese
Sitzung ist an diesem Tag **zweimal durch `/compact` gegangen**; eine
Verdichtungs-Zusammenfassung ist konstruktionsbedingt verlustbehaftet.

**Das Kit protokolliert bereits — nur die falsche Hälfte.** Für jeden
Rollenaufruf liegt eine Datei in `.team-logs/`
(`frank-HM-63-v1-20260908-190614.json`). Die interaktive Architekten-Sitzung,
in der geplant, diagnostiziert und **entschieden** wird, hat kein Gegenstück.

## Wo es steckt

**Die Quelle existiert und ist vollständig.** Die Agenten-CLI schreibt je
Sitzung ein Vollprotokoll nach
`~/.claude/projects/<projekt-slug>/<session-id>.jsonl` — mit Werkzeugaufrufen,
deren Ergebnissen und Anhängen. In diesem Feldprojekt liegen dort **209
Sitzungen, 133 MB**. Kein einziges Byte davon ist im Projekt greifbar.

Es fehlt nicht die Erzeugung, sondern:

- ein Verb, das die Protokolle **dieses** Projekts in den Projektordner holt,
- die `.gitignore`-Zeile dafür,
- der `--update`-Pfad, damit bestehende Feldprojekte es bekommen,
- und die ausdrückliche Regel, dass sie **nicht** in einen Kontext geladen werden.

## Warum das jede Installation trifft

**Das Kit hat für genau diese Lücke bereits eine Regel — eine, die auf
Gewissenhaftigkeit statt auf Mechanik steht.** Planungsregel 6 (der
Übergabezettel) verlangt, dass alles, was eine spätere Instanz braucht, im
selben Zug in eine Datei wandert, und begründet das wörtlich damit, dass
zwischen Lauf und Closeout ein **Sitzungswechsel** liegt: *„Was in dieser Lücke
nur gesagt wurde, ist weg, und niemandem fällt es auf."*

Der Sitzungswechsel ist dabei **erzwungen**, nicht zufällig — die Kostenmessung
schreibt einen Closeout je Sitzung vor. Die Regel ist also die manuelle Abhilfe
für ein fehlendes Werkzeug. Mit dem Export bliebe sie richtig, würde aber
billig: Der Übergabezettel trüge weiter die **Deutung**, das Protokoll trüge
den **Beleg**.

Dazu kommt der Fall, den keine Regel abdeckt: Was ich beim Abschreiben nicht
für wichtig hielt, ist weg. In diesem Projekt sind das mit Sicherheit
Messreihen, verworfene Hypothesen und Zwischenstände, deren Wert sich erst drei
Kaskaden später zeigt — genau die Sorte Material, das die Pflichtzeile in
Abschnitt 4 des Abschluss-Docs sucht.

## Was ich schon versucht habe

- **Von Hand abschreiben** ins Beutebuch, den Backlog und das Abschluss-Doc.
  Das funktioniert und ist der heutige Weg. Es ist aber exakt so vollständig
  wie die Sorgfalt des Architekten, und es kostet Token in der **teuersten**
  Sitzung — das starke Modell schreibt Fließtext über etwas, das eine
  Dateikopie wäre.
- **Auf die `/compact`-Zusammenfassung verlassen.** Sie ist eine
  Zusammenfassung; sie soll verlustbehaftet sein.

**Vorschlag, zwei Größen:**

- **Klein:** Ein Verb (`kit-protokoll ablegen` bzw. `team-protokoll.cmd`), das
  die Sitzungsprotokolle **dieses** Projekts nach `.team-protokolle/` kopiert —
  eine Datei je Sitzung, dazu ein `index.md` mit Datum, Dauer, Anzahl der
  Züge und, falls ermittelbar, den Kosten. **Rückwirkend als Vorgabe**: Der
  erste Lauf nimmt alle vorhandenen Sitzungen mit (hier 209), nicht nur
  künftige. Idempotent, damit er beliebig oft laufen darf.
- **Größer:** Zusätzlich eine **lesbare** Fassung je Sitzung (Markdown:
  Nutzerzüge und Antworttext ausgeschrieben, Werkzeugaufrufe eingeklappt),
  Anhänge in einen Unterordner ausgepackt, und der Export als **letzter Schritt
  von `--rollen-abschluss`** — dann geschieht er, ohne dass jemand daran denken
  muss, und genau dort, wo die Roh-Kostenlogs ohnehin wegarchiviert werden.

**Drei Auflagen, die der Strippenzieher ausdrücklich gesetzt hat:**

1. **Unkommittiert.** Die `.gitignore`-Zeile muss mit `--update` **mitkommen**,
   sonst committet das erste Feldprojekt seine eigenen Sitzungsprotokolle.
   **Das ist eine Sicherheitsauflage, keine Ordnungsliebe:** In einem Protokoll
   steht alles, was ein Mensch je in die Sitzung eingefügt hat — Token,
   Kennwörter, Kundennamen, Screenshots. 133 MB davon in einem Repository, das
   jemand klont, ist ein Vorfall, kein Schönheitsfehler.
2. **Nie automatisch in einen Kontext geladen.** Kein Rollen-Briefing, kein
   Prompt, kein Werkzeug liest den Ordner von sich aus. Nur auf ausdrückliche
   Nachfrage. Sonst zahlt jedes Feldprojekt seine eigene Historie in jedem
   Rollenaufruf mit.
3. **Rückwirkend.** Der erste Lauf schließt alle bereits vorhandenen Verläufe
   ein — sie sind das wertvollste Material, das der Export je haben wird, weil
   sie aus der Zeit stammen, in der noch niemand mitgeschrieben hat.

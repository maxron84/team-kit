# Ein Rollen-Anhang kann einen fremden Fundblock zerschneiden, und kein Guard kann es sehen

- **Bezug**: BL-54
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst
  plus Electron-Oberfläche, rund 1000 Tests, 23 gebaute Kaskaden, Beutebuch mit
  141 Funden über offenen Stand und Archiv.

## Was passiert ist

Frank fand beim Fixen eines Fundes denselben Fehler in einer weiteren Datei und
legte dafür regelkonform einen Beifang-Fund an. **Seinen Block schrieb er aber
nicht ans Ende des Beutebuchs, sondern mitten in den Block des Vorgängers** —
zwischen dessen vorletzten Absatz und seine `Reproducer-Test`-Zeile.

Ergebnis:

- der **fremde** Fund endete ohne seine Pflichtzeile,
- der **neue** Fund trug am Ende eine fremde,
- **kein Zeichen ging verloren**, die Datei sah unauffällig aus. Es war reine
  Reihenfolge.

**Der Read-Only-Guard kann das prinzipiell nicht sehen.** Er urteilt über
**Schreibzonen** — welche Pfade eine Rolle anfassen darf. Das Beutebuch ist für
Frank eine erlaubte Datei; dass sein Anhang mitten in einen fremden Block
fällt, ist eine Frage der **Struktur**, nicht des Pfades. Der Guard ist hier
also nicht zu lasch, sondern schlicht zuständigkeitsfremd.

**Und der Diff sah aus wie Routine.** Das ist dieselbe Bauform wie ein zweiter
Fall in diesem Projekt, bei dem eine Rolle drei Zeichen in einer **fremden**
Datei zerstörte — auch dort war der Diff unauffällig. Der Unterschied: Dort
traf es eine Projektdatei, hier die Datei, die **das Team selbst führt**.

## Wo es steckt

- `geteilt/tools/beutebuch.py`, Verb `lint` — kann die Pflichtfelder eines
  Blocks prüfen, aber nur für **einen** Fund je Aufruf.
- Die Aufrufkette der Rollen (`pwsh/entry/frank.ps1`, `bash/entry/frank.sh` und
  die Red-Team-Läufe) — sie ruft nach dem Rollenlauf **keinen** Strukturcheck
  über das Beutebuch auf.
- `CLAUDE.md`, Beutezug-Dreisatz — verlangt die Pflichtfelder, benennt aber
  nicht, dass ein Anhang **ans Ende** gehört.

## Warum das jede Installation trifft

Das Beutebuch ist eine **gemeinsam beschriebene Datei**: Harry und Marv tragen
Funde ein, Frank quittiert Status, Axel setzt `Fix-Plan liegt vor`. Jede dieser
Rollen hängt Text an eine Datei an, die eine andere Rolle gerade erst
geschrieben hat, und **keine von ihnen sieht die Datei als Ganzes**. Das ist
die Bauform des Werkzeugs, nicht eine Eigenheit dieses Projekts.

Der Schaden ist still: Ein Fund ohne `Reproducer-Test`-Zeile bricht den
Substanz-Anker `team_diff_beruehrt_fund` — Franks regelkonformer Fix würde
stillschweigend zurückgerollt, und zwar an einem Fund, den niemand verdächtigt.

## Was vorgeschlagen wird

**Die Prüfung existiert bereits — es fehlt der Lauf über alle und der Aufruf an
der richtigen Stelle.** Drei Teile:

1. **`lint` über alle Blöcke**, ohne Fundnummer aufgerufen: jeder `### HM-`Block
   gegen die Pflichtfelder, Exit ungleich null mit der Liste der beschädigten.
   Die Zerlegung in Blöcke macht `beutebuch.py` bereits für `list`.
2. **`lint --alle`, also mit dem Archiv** — siehe den gemessenen Nebenbefund
   unten. Ohne das prüft der Lauf aus Punkt 1 nur die Spitze des Bestands.
3. **Aufruf nach jedem Rollenlauf**, der das Beutebuch anfassen durfte. Ein
   Befund gehört in den Abschlussbericht des Laufs; er ist kein Grund, den Lauf
   abzubrechen, aber einer, ihn nicht als sauber zu melden.

**Zusätzlich, billig und wirksamer als jede Prüfung: die Regel in den
Briefings.** *„Ein neuer Fundblock wird ans ENDE des Beutebuchs geschrieben,
nie zwischen zwei bestehende."* Der Satz fehlt heute in allen Briefings, die das
Beutebuch beschreiben — und er hätte diesen Fall verhindert, ohne dass ein
Werkzeug hätte laufen müssen.

**Gegenprobe für die Reparatur, die sich hier bewährt hat:** die **Multimenge**
der Zeilen vorher und nachher vergleichen. Sie zeigt, dass beim Zurücksortieren
kein Zeichen verlorengegangen ist — ein Diff allein zeigt das nicht, weil ein
verschobener Block wie ein gelöschter plus ein neuer aussieht.

## Was ich schon versucht habe

**Gemessen statt vermutet — und dabei ein zweiter Befund, der die Meldung
größer macht, als sie sein sollte:**

`beutebuch.py lint <HM-Nr>` über **jeden** Fund dieses Projekts laufen lassen
(141 Nummern aus `list --alle`):

| | |
|---|---|
| **15** offene Blöcke | linten sauber durch |
| **126** archivierte Blöcke | `FEHLER: HM-n nicht im Beutebuch gefunden.` |

**`lint` kennt kein `--alle` und sucht deshalb nie im Archiv** — anders als
`list`, `dateien` und `reproducer`, die es alle haben. Damit sind **89 % des
Fundbestands für den Linter unerreichbar**, und zwar genau die Blöcke, die
niemand mehr ansieht. Eine Beschädigung im Archiv bliebe dauerhaft unentdeckt;
rotiert wird mit `archiviere`, das die Blöcke **wörtlich** verschiebt — also
auch einen bereits zerschnittenen.

Der lokale Schaden aus dem Ausgangsfall ist von Hand repariert (Blöcke
zurücksortiert, Multimengen-Gegenprobe gefahren). **Gebaut ist lokal nichts** —
`beutebuch.py` liegt in `geteilt/`, ein Patch dort hätte sein Verfallsdatum
beim nächsten `--update`.

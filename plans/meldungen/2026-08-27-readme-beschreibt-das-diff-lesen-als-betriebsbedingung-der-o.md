# README beschreibt das Diff-Lesen als Betriebsbedingung — der Owner selbst betreibt es anders

- **Art**: Doku-Fehler (falsch benannte Betriebsbedingung)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkuerzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, vierte
  gebaute Kaskade, ~19 Red-Team-Funde abgearbeitet

## Was passiert ist

`README.md` Zeile 44 ff. beschreibt, fuer wen das Kit gedacht ist:

> **Fuer wen.** Fuer **erfahrene Entwickler**, die ihren eigenen Code lesen und
> verstehen und ihr KI-Team Schritt fuer Schritt anleiten wollen […] Das ist
> keine Hoeflichkeitsformel, sondern eine **Betriebsbedingung**. […] Wer den
> Diff nicht liest, kann diese Fragen nicht beantworten — dann wird das
> Beutebuch zur Ablage statt zur Entscheidung […]

Der Betreiber dieses Feldprojekts liest den Diff **kaum bis gar nicht**. Nach
dem Wortlaut des README betreibt er das Kit damit ausserhalb seiner
Betriebsbedingung — waehrend vier Kaskaden gebaut, ~19 Funde abgearbeitet und
alle Abnahmen erteilt wurden. Die Bedingung ist also nicht verletzt, sondern
**falsch benannt**.

Beurteilt wird sehr wohl, nur an anderen Stellen — und das Kit stellt sie
selbst bereit:

| Frage aus dem README | Wo sie tatsaechlich entschieden wird |
|---|---|
| Ist der Red-Team-Fund echt oder Rauschen? | An den **Reproschritten** des Fundblocks — sie sind die Beweisform, nicht der Code |
| Behebt Franks Fix die Ursache oder das Symptom? | Am **Reproducer-Test** (ohne Fix rot) und an der Fix-Beschreibung |
| Ist die Stufe abnahmereif? | An der **Zusicherung** der Stufe und am laufenden Produkt (UAT) |
| War es das wert? | An der **Kostenbuchfuehrung** je Stufe und Rolle |

Der Betreiber formuliert es als Architekturaussage: Das T.E.A.M. mit
hinreichend faehigen Modellen ist eine **weitere Abstraktionsschicht**, keine
Ergaenzung zum Selbertippen. Das README beschreibt es aber wie eine Ergaenzung
— und macht die Taetigkeit `Diff lesen` zur Bedingung, obwohl in Wahrheit die
**Faehigkeit** dazu die Bedingung ist.

## Wo es steckt

`README.md`, Abschnitt „Fuer wen" (Zeilen 44–53).

**Formulierungsvorschlag** (Struktur des Originals bleibt, die Begruendung
wechselt von der Taetigkeit zur Faehigkeit):

> **Fuer wen.** Fuer **erfahrene Entwickler** — nicht, damit sie mehr Code
> lesen, sondern damit sie weniger muessen. Das T.E.A.M. ist eine
> **Abstraktionsschicht**, kein Beiwerk zum Selbertippen: Du entscheidest,
> **was** gebaut wird, und urteilst am **Ergebnis** — traegt die Stufe ihre
> Zusicherung, ist der Red-Team-Fund echt oder Rauschen, behebt Franks Fix die
> Ursache oder das Symptom, stimmt der Preis? Die Rolle dabei ist die eines
> **fachlich orientierten Stakeholders**: Product Owner, Chefentwickler, Tech
> Lead.
>
> **Warum trotzdem „erfahren"?** Weil jede Abstraktionsschicht irgendwann
> klemmt. Wer den Diff nie lesen **koennte**, kann einen Fehler des Teams nicht
> von einem Fehler der eigenen Vorgabe unterscheiden — und beurteilt dann nur
> noch, ob es sich gut anhoert. Der Unterschied ist der zwischen *„ich lese den
> Diff nicht"* (Normalbetrieb, voellig in Ordnung) und *„ich koennte ihn nicht
> lesen"* (die eigentliche Betriebsbedingung). Das tragende Prinzip
> **Finder != Fixer** endet bei einem Menschen, der den Fund *beurteilen* muss;
> kann er das nicht, wird das Beutebuch zur Ablage statt zur Entscheidung, und
> das Team baut zuverlaessig, ausdauernd und teuer am Ziel vorbei.

## Warum das jede Installation trifft

Der Absatz ist das erste, was ein Interessent liest, und er entscheidet ueber
Selbstauswahl in beide Richtungen. Nach der heutigen Fassung haelt sich jemand
fuer ungeeignet, weil er nicht jeden Diff lesen will — und jemand anderes haelt
sich fuer geeignet, weil er gern Code liest, ohne fachlich urteilen zu koennen.
Die zweite Fehlauswahl ist die teurere: Sie fuehrt genau zu dem Betrieb, den
der Absatz verhindern will.

Der Satz wirkt ausserdem nach innen. Er ist die Begruendung dafuer, dass es
ueberhaupt einen Menschen im Loop gibt; wird er falsch begruendet, wandert die
Rechtfertigung fuer die menschlichen Halte- und Abnahmepunkte auf eine
Taetigkeit, die im Normalbetrieb gar nicht stattfindet.

## Was ich schon versucht habe

Nichts geaendert — die Formulierung des oeffentlichen README ist eine
inhaltliche Entscheidung des Owners, kein lokaler Fix. Der Vorschlag oben ist
ein Vorschlag; belegt ist nur der Widerspruch zwischen Wortlaut und
tatsaechlichem Betrieb.

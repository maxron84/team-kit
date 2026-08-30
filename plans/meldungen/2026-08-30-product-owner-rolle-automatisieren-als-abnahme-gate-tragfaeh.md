# Product-Owner-Rolle automatisieren: als Abnahme-Gate tragfaehig, als Bindeglied riskant

- **Art**: Idee / Verbesserung
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Bestandsprojekt, Linux, bash-Bahn, Dart/Flutter-Mobilanwendung,
  zwölf Kaskaden gebaut, ein menschlicher Stakeholder als einzige nicht automatisierte
  Rolle. Spezifikationen und ein lauffähiger Vorgänger in einer anderen Sprache liegen
  als Wahrheitsquelle vor.

## Was passiert ist

Kein Fehlschlag, sondern eine Beobachtung aus dem Betrieb: Der menschliche
Stakeholder trägt in Wahrheit **drei** Hüte, und das Rollenmodell des Kits
kennt nur den Sammelbegriff.

| Hut | Beispiele | automatisierbar? |
|---|---|---|
| **Prinzipal** (Auftraggeber) | Produktentscheide, Budgetgrenzen, Veröffentlichen nach außen | **nein, per Definition** — wer das Risiko trägt, entscheidet |
| **Product Owner** | Welcher Strang wird die nächste Kaskade? Ist das Gebaute gut genug? | **ja** — die Arbeit ist *abgeleitet*, nicht schöpferisch |
| **Operator** | Zeiger auf den nächsten Plan umlegen, Lauf starten, Gerät anschließen | ja, aber als Skript-Schalter, nicht als Modellrolle |

Weil alle drei in einer Person liegen, fällt nicht auf, dass die mittlere
Schicht ableitbar ist: Ein Product Owner leitet aus Ziel, Lage und
Spezifikation ab. Der Prinzipal liefert das Ziel.

Beim Ausarbeiten kam der eigentliche Fund zum Vorschein — siehe unten. Die
Rollenidee ist der Anlass, die Gate-Lücke ist der Grund.

## Wo es steckt

Keine einzelne Datei, sondern eine Lücke im Rollenmodell: der Rollentabelle in
`CLAUDE.md`, den Briefings unter `team/prompts/rolle-*.md` und der Statuskette
des Beutebuchs.

**Der Fund dahinter ist konkreter und wiegt schwerer: Die Plan-Seite ist das
einzige Artefakt des Kits ohne Netz.**

| Rolle | Ausgabe | wird geprüft durch |
|---|---|---|
| Ralph | Produktivcode | Smoke-Test der Stufe |
| Frank | Fix | Gegenprobe + Reproducer-Test |
| Harry / Marv | Fund | Reproschritte, danach Franks Nachprüfung |
| Axel | Ermittlungsakte | Franks Umsetzung |
| **Der Architekt** | **Kaskadenplan** | **nichts** |

Die Stufen-`Verifikation` im Plan prüft *„funktioniert es"* — geschrieben vom
Architekten selbst, für seinen eigenen Entwurf. Die Frage *„ist es das
Richtige"* stellt im ganzen Kit **niemand** außer dem Menschen, und der stellt
sie am Ende, aus dem Gedächtnis. Ein falscher Plan wird von Ralph treu
ausgeführt und kostet eine ganze Kaskade.

## Warum das jede Installation trifft

Rollenmodell und Gate-Lücke sind Eigenschaften des Kits, nicht dieses
Projekts. Jede Installation hat dieselben sechs Rollen unter einem Menschen,
und in jeder ist der Kaskadenplan das einzige Artefakt, das ungeprüft in die
Ausführung geht. Ein Feld, das die Rolle selbst nachbaut, baut sie in jeder
Installation neu und anders.

## Was gegen die naive Fassung spricht

Die erste Fassung — „der PO ist das Bindeglied zwischen Mensch und Team" — hat
das Feld im Gespräch selbst verworfen. Vier Einwände, alle vom Stakeholder
angestoßen:

1. **Ein Zwischenglied verliert Information nicht, es ersetzt sie.** Heute kann
   der Architekt beim Menschen zurückfragen. Mit einem PO dazwischen fragt er
   den PO — und ein Modell **antwortet immer**. Das ist dieselbe Bauart wie ein
   Smoke-Test, der sich still die Umgebung passend setzt: Es sieht geprüft aus,
   weil jemand geantwortet hat. Wird die Rolle gebaut, muss *„das steht
   nirgends, hier ist die eine Frage"* ihr **Normalfall** sein, nicht ihre
   Notbremse.
2. **Abstraktion ist Rauschunterdrückung — und im Feld war das Rauschen die
   Information.** Die teuersten Funde dieses Projekts kamen daher, dass ein
   Mensch das Produkt angefasst hat, nicht aus einem Bericht. Ein PO liefert ein
   *kohärentes Bild*; dabei fällt zuerst das schiefe Detail weg, das stutzig
   gemacht hätte.
3. **Rubber-Stamp-Falle.** Das Entscheidungsrecht bleibt beim Menschen, die
   Entscheidungs*fähigkeit* wandert weg, weil ihm die Grundlage fehlt. Formell
   verantwortlich, praktisch nicht mehr urteilsfähig — es fällt erst auf, wenn
   es schiefgeht.
4. **Das Bindeglied existiert schon: der Architekt.** Er übersetzt einen
   Wunsch in einen Stufenbogen. Ein PO wäre die *zweite* Übersetzungsschicht
   und muss sich fragen lassen, ob sie etwas hinzufügt oder überwiegend
   isoliert.

**Die veraltende Zielurkunde ist der schwerste Einwand.** Ein Zieldokument, das
niemanden zwingt, es wieder anzusehen, verrottet lautlos — der Kit-Backlog
kennt dieselbe Bauart bereits von Skizzen, die auf einer längst widerlegten
Prämisse standen. Ein Verfallsdatum hilft nicht: Wer „gilt das noch?" vorgelegt
bekommt, sagt ja, ohne zu lesen, und danach steht ein Datum daran. Was tragen
könnte:

- **Bestätigung durch Auswahl statt Häkchen** — der PO legt zwei bis drei
  konkrete Kandidaten mit Begründung vor; die Wahl erzwingt Kontakt mit dem
  Ziel, das Häkchen nicht. Das Ziel wird als *Nebenwirkung* fortgeschrieben.
- **Das Ziel muss falsifizierbar sein** — eine Vision kann nie veralten, weil
  sie nie falsch sein kann, und lenkt darum auch nichts. Was nützlich veraltet,
  sind Nicht-Ziele und Abnahmekriterien: Sätze, die das gebaute Produkt
  **widerlegen kann**.
- **Zwei Quellen, nie eine** — Ziel *und* das Frischeste, was das Projekt hat:
  worüber sich der Mensch zuletzt geärgert hat. Wo beide sich widersprechen,
  wird der Widerspruch **berichtet**, nicht aufgelöst.

## Wann die Rolle taugt — und wann nicht

**Kernsatz des Stakeholders:** Die Eignung steigt, je eindeutiger und fester
die Ziele sind — am besten hart aus einem bereits etablierten **Vorbild**
abgeleitet.

Das ist mehr als eine Vorbedingung, es ist der Riegel gegen beide Einwände
oben. Ein extern verankertes Ziel ändert die Natur des Zieldokuments: Es ist
dann keine *erinnerte Absicht* mehr, sondern eine **Liste von Abweichungen
gegenüber etwas, das noch existiert**. Es kann weiter veralten — aber man
**merkt** es, weil das Vorbild nachschlagbar danebenliegt. Und das
Bindeglied-Problem schrumpft mit: Der PO übersetzt keinen Kopf, sondern ein
Dokument, **das der Architekt selbst lesen kann**.

**Die Deckung ist keine Eigenschaft des Projekts, sondern jeder einzelnen
Frage.** Auch ein Projekt mit starkem Vorbild weicht bewusst ab, und genau dort
hört das Vorbild auf zu antworten — ohne es anzusagen. Daraus wird eine
nachprüfbare Bedingung statt eines Ermessens:

> Kann ich auf eine Stelle im Vorbild zeigen? → entscheiden.
> Nein? → **das** ist die eine Frage an den Menschen.

**Die gefährliche Richtung gehört mitgeschrieben:** Am wenigsten geeignet ist
die Rolle im Greenfield ohne Vorbild — also genau dort, wo ein Team sie am
dringendsten haben will („wir wissen noch nicht, was wir bauen, lass die KI
entscheiden"). Ein Kit, das die Rolle anbietet, ohne diese Bedingung zu nennen,
lädt zur Anwendung im untauglichsten Fall ein.

## Der Schnitt, den das Feld empfiehlt

Nicht das Bindeglied bauen, sondern das fehlende Gate. Die beiden Hälften der
Rolle tragen das Risiko völlig ungleich:

| Hälfte | Frequenz | Kosten eines Fehlers | Risiko durch veraltetes Ziel |
|---|---|---|---|
| **Abnahme** (ist das Fertige gut?) | jede Kaskade | eine Backlog-Zeile | gering — der Mensch prüft ohnehin von Hand |
| **Priorisierung** (was als Nächstes?) | jede Kaskade | eine **ganze Kaskade** | **hoch** |

Also: **Abnahme voll automatisieren, Priorisierung nur als Vorschlag mit
Begründung.** Die Ratifikation durch den Menschen ist dann keine Höflichkeit,
sondern die **einzige** Stelle, an der ein veraltetes Ziel auffallen kann — und
der beste Moment dafür existiert schon: die Handprüfung am Gerät, wenn der
Mensch das Produkt in der Hand hält.

**Und falls das Bindeglied doch gebaut wird: Werkzeug neben dem Weg, nicht
Schicht im Weg.** Der Unterschied ist, ob man an ihm vorbeigehen kann. Das löst
nebenbei das ursprüngliche Ziel besser — der weniger technische Nutzer lehnt
sich an, der erfahrene geht vorbei. Ein System, zwei Bedienweisen, kein
gegabelter Entwurf.

**Keine neuen Dokumentformate.** Der Auftrag passt in den Plankopf, die Abnahme
in einen Abschnitt des Abschluss-Docs. Ein vierter Nummernraum neben Backlog,
Beutebuch und Ermittlungsakten wäre der falsche Weg.

## Was das für die Modellwahl hieße

Eine Regel, die das Kit heute nicht hat und die unabhängig von dieser Idee
nützlich wäre:

> **Die Modellstärke folgt der Frage „hat die Ausgabe dieser Rolle ein
> maschinelles Netz?" — nicht der Frage „ist die Rolle senior?"**

Rollen mit Netz (Bau, Fix) dürfen günstig laufen, weil eine falsche Antwort
auffällt. Rollen ohne Netz (Planung, Priorisierung, Forensik) müssen stark
laufen, weil nichts sie auffängt. Daraus folgt ausdrücklich: **den Architekten
nicht herunterstufen**, nur weil er klarere Vorgaben bekommt — sein
Kostentreiber ist nicht das Verstehen des Auftrags, sondern das Überblicken der
gewachsenen Codebasis. Gespart wird, indem er **kürzer** läuft, nicht schwächer.

Für die neue Rolle selbst genügt die mittlere starke Stufe: Ihr Aufrufvolumen
ist klein (zwei Aufrufe je Kaskade, reiner Prosa-Kontext), und wer im Vorbild
**nachschlägt**, statt zu erfinden, braucht weniger Modell, nicht mehr. Ein
teureres Spitzenmodell wäre hier vor allem eines: kreativer — in genau der
Rolle, in der Kreativität das Problem ist.

## Woran man merken würde, dass es trägt

Falsifizierbar, ab der ersten Kaskade messbar: **Trägt das Bindeglied, sind die
Korrekturen des Menschen beim Ratifizieren selten und klein.** Schreibt er den
Auftrag regelmäßig um, kostet die Rolle mehr, als sie spart — dann bleibt vom
Vorschlag nur die Abnahme übrig, und das ist in Ordnung, denn sie war ohnehin
der Teil mit dem echten Loch.

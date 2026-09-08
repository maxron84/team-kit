# Es gibt kein lesbares Projektgedächtnis — die Artefakte sind vollständig, und niemand kann sie lesen

- **Art**: Verbesserungsvorschlag
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (dreizehn Kaskaden), Windows, nur pwsh-Bahn, Python + Electron, rund 530 Tests.

## Was passiert ist

Nach dreizehn Kaskaden trägt dieses Feldprojekt folgendes Gedächtnis:

| Artefakt | Umfang |
|---|---|
| `plans/beutebuch.md` | 3.755 Zeilen, 67 Funde |
| `plans/backlog.md` | 56 Einträge — als **Tabelle**, einzelne Zellen über 2.000 Zeichen |
| `plans/kaskade-N-abschluss.md` | 12 Stück, zusammen 4.635 Zeilen |
| `plans/ralph-kaskade-N-*.md` | 13 Stück, zusammen 4.449 Zeilen |
| `CHANGELOG.md` | 1.220 Zeilen |
| `plans/kit-meldungen/` | 27 Meldungen |

**Rund 14.000 Zeilen förmlicher Dokumente. Alles korrekt, alles vollständig,
alles maschinennah.** Und die einfachste Frage, die ein Mensch an ein Projekt
stellt — *„Was ist hier passiert, in welcher Reihenfolge, und was haben wir
dabei gelernt?"* — ist daraus in vertretbarer Zeit **nicht** zu beantworten.
Auch nicht vom Architekten selbst, der das meiste davon geschrieben hat.

Jedes einzelne Artefakt ist für seinen Zweck richtig gebaut. Das Beutebuch ist
eine Zustandsmaschine für Funde und muss maschinenlesbar sein. Der Backlog ist
eine Tabelle, weil `beutebuch.py` und `zitat-lint.py` darauf laufen. Das
Abschluss-Doc ist ein Protokoll und beweist einen Lauf. **Keines davon ist eine
Erzählung, und die Summe ist erst recht keine.**

## Wo es steckt

Es fehlt keine Datei — es fehlt eine **Schicht**. Das Kit erzeugt heute
lückenlos die formale Ebene (Plan → Protokoll → Fund → Backlog → CHANGELOG) und
lässt die lesbare Ebene ungebaut. Betroffen sind:

- **Planungsregel 5** (Abschluss-Doc): Sie schreibt sieben Pflichtabschnitte
  vor, alle sieben adressieren Nachweisbarkeit. Kein Abschnitt richtet sich an
  einen Menschen, der das Projekt **nicht** kennt.
- **Die Doku-Hygiene**: Sie verlangt richtigerweise, Herleitung und Historie aus
  der `CLAUDE.md` in ein Historien-Doc zu verschieben — sagt aber nicht, wie
  dieses Doc aussieht. Im Feld wird daraus eine Ablage, kein Text.
- **Das Archivieren** (Doku-Hygiene 3): Fund- und Aufgabenlisten werden rotiert,
  sobald sie überwiegend abgeschlossen sind. Damit verschwindet die Historie
  aus dem Blick — richtig für die Arbeitsdateien, aber es gibt nichts, wohin
  die **Erkenntnis** daraus gerettet würde.

## Warum das jede Installation trifft

**Die Kosten fallen an drei Stellen an, und alle drei sind im Feld belegbar:**

1. **Beim Wiedereinstieg.** Jede neue Architekten-Sitzung beginnt damit, sich
   den Stand zu erarbeiten — aus Dateien, die dafür nicht gebaut sind. Das ist
   Arbeit des **starken Modells** und wird pro Sitzung neu bezahlt.
2. **Bei der Übergabe an Menschen.** Ein Kollege, ein Vorgesetzter oder der
   Betrieb bekommt heute entweder 14.000 Zeilen oder eine mündliche
   Zusammenfassung. In diesem Projekt musste der Architekt denselben Sachverhalt
   an einem Tag **dreimal** neu formulieren — einmal fachlich, einmal kurz,
   einmal „für Uneingeweihte". Jedes Mal von Hand, jedes Mal flüchtig.
3. **Bei der Wiederholung von Fehlern.** Die Lehren stehen verstreut in
   Fundblöcken und Backlog-Zellen. Dass eine Zusicherung *„grün war, WEIL das
   Produkt nicht funktionierte"*, ist eine Erkenntnis, die in jedem Projekt
   dieser Art wieder gebraucht wird — auffindbar ist sie heute nur, wenn man
   weiß, dass man sie sucht.

## Was ich schon versucht habe

- **Das Abschluss-Doc als Erzählung schreiben.** Geht nicht weit: Seine
  Gliederung ist vorgegeben und dient dem Nachweis. Erzählende Passagen machen
  es länger, ohne es lesbar zu machen.
- **Die Antwort an den Menschen ausführlich halten.** Genau das ist der Fehler,
  den Planungsregel 6 benennt — was nur in der Antwort steht, ist beim
  Sitzungswechsel weg.

**Vorschlag, zwei Größen:**

- **Klein:** Ein **Pflichtabschnitt** im Abschluss-Doc, ganz oben, vor Abschnitt
  1: *„In zehn Sätzen, für Menschen"* — was war die Frage, was wurde gebaut, was
  hat überrascht, was hat es gekostet, was ist offen. Kostet nichts, entsteht
  ohnehin im Closeout, und macht aus jedem Abschluss-Doc einen lesbaren
  Einstieg. **Das ist die Fassung, die ich zuerst bauen würde.**
- **Größer und der eigentliche Vorschlag:** Ein **Entwicklertagebuch** unter
  `doku/tagebuch/` — je Kaskade eine Seite plus ein `index.md`, aus der
  Perspektive des Architekten, ausdrücklich **für Menschen**:
  - je Kaskade: Anlass, Entscheidung, was gebaut wurde, **was schiefging**, was
    es kostete, was offen blieb;
  - Querverweise statt Wiederholung: auf Funde, Akten, Abschluss-Docs;
  - ein **Register nach Thema**, nicht nur nach Zeit — „Auslieferung",
    „Prüfstände", „Kosten" —, damit die Lehre auffindbar ist, ohne dass man
    weiß, in welcher Kaskade sie entstand;
  - eine Zeile **„was wir daraus gelernt haben"** je Kaskade, die genau die
    Sorte Satz aufnimmt, die heute in Fundblöcken versackt.

**Zwei Auflagen, die ich für tragend halte:**

1. **Vom Architekten geschrieben, nicht generiert.** Ein aus Git oder CHANGELOG
   erzeugtes Tagebuch ist ein zweites CHANGELOG — es zählt Änderungen auf und
   erklärt keine. Der Wert liegt in der **Deutung**, und die hat nur, wer den
   Lauf begleitet hat.
2. **Im Closeout, nicht danach.** Sonst trifft es dieselbe Lücke wie der
   Übergabezettel: Was auf „später" vertagt wird, überlebt den Sitzungswechsel
   nicht.

**Bezug zur Schwestermeldung:** Ein Sitzungsprotokoll-Export (`Kit-BL-242`)
liefert das Rohmaterial, aus dem ein Tagebuch überhaupt geschrieben werden
kann — auch rückwirkend. Die beiden Meldungen sind unabhängig umsetzbar,
entfalten zusammen aber deutlich mehr Wirkung: das eine bewahrt den **Beleg**,
das andere die **Deutung**.

---

## Wer schreibt es — der Vorschlag einer siebten Rolle

**Die Frage „wer schreibt das Tagebuch" hat eine eigene Antwort verdient, und
sie lautet: nicht der Architekt.** Nicht, weil er es nicht könnte, sondern
weil es die falsche Sitzung und das falsche Modell ist:

- **Modell.** Erzählen aus vorhandenem Material ist keine Urteilsarbeit. Das
  kann das günstige Modell. Im Closeout liegt die Arbeit beim **starken**.
- **Kosten.** Eine eigene Rolle bekommt eine eigene Ledger-Zeile, ein eigenes
  Log und einen eigenen Cap. Im Closeout versteckt sich der Aufwand in der
  Architektensumme und ist nicht mehr auffindbar.
- **Rückwirkend.** Zwölf Kaskaden und 209 Sitzungen nachzutragen ist kein
  Closeout-Schritt, sondern ein eigener Auftrag — und einer, der sich in
  Häppchen fahren lässt, eine Kaskade je Aufruf.

**Vorschlag: `Raoul` — der Reporter im Feld.** Der Name reiht sich in die
Vornamen der bestehenden Rollen ein (Ralph, Frank, Harry, Marv, Axel).

**Sein Ton ist Absicht, keine Marotte.** Die formalen Artefakte schleifen
genau das weg, was ein Tagebuch merkfähig macht. Im Beutebuch steht, dass ein
Fund falsch diagnostiziert war. Dort steht **nicht**, dass zwei Handabnahmen
auf einem fremden Konto dafür verbrannt wurden, weil ein Aufrufparameter unter
Windows PowerShell 5.1 schlicht nicht existiert. Ein Ich-Erzähler, der
schreiben darf *„das habe ich falsch beurteilt"*, hält die Fehler drin — und
die Fehler sind der brauchbare Teil. Eine neutrale Chronik sandet sie ab, und
die abgesandete Fassung merkt sich niemand.

**Rückblickend, nicht mitlaufend.** Ein Reporter, der live mitfährt, kollidiert
mit der Bauform des Kits — die Rollen laufen nacheinander in **einem**
Arbeitsbaum — und kostet Token je Stufe für Material, das ohnehin
mitgeschrieben wird. Der Protokoll-Export aus `Kit-BL-242` **ist** die
Feldaufnahme; Raoul schreibt daraus hinterher. (Das ist auch das historische
Verhältnis: Thompson hat Las Vegas aus Notizbüchern und Tonbändern
zusammengeschrieben, nicht live getippt.)

**Sein Dreisatz:**

1. **Lesen** — Abschluss-Doc, Fundblöcke und Sitzungsprotokolle **einer**
   Kaskade.
2. **Schreiben** — `doku/tagebuch/kaskade-N.md` plus die Registerzeile im
   `index.md`.
3. **Vorlegen** — der Architekt liest gegen und quittiert. Erst dann gilt der
   Eintrag.

**Zwei eiserne Regeln:**

1. **Er schreibt ausschließlich in `doku/tagebuch/`.** Die Subjektivität darf
   nie in Beutebuch, Backlog oder Plan lecken — dort gilt Nachweisbarkeit.
   Dieselbe Bauform wie die Read-Only-Regel bei Harry und Marv, nur mit einer
   erlaubten Schreibzone statt gar keiner.
2. **Die Quittung des Architekten prüft TATSACHEN, nicht den Ton.** Stimmen die
   Zahlen, stimmt die Reihenfolge, ist keine Behauptung erfunden — mehr nicht.
   Wer dort anfängt, Formulierungen zu glätten, bekommt wieder das neutrale
   Protokoll, das es schon gibt. **Ohne Schritt 3 hat man dagegen eine Rolle,
   die plausibel klingende Geschichte erfindet — das wäre schlechter als kein
   Tagebuch.**

**Ein ehrlicher Einwand, der im Kit-Backlog stehen sollte:** Die bestehenden
Rollen sind nach ihrer **Befugnis am Code** geschnitten — bauen, planen, fixen,
angreifen, ermitteln. Raoul hat mit dem Code gar nichts zu tun; er liegt auf
einer anderen Achse. Das ist ein Grund, zweimal hinzusehen, ob es eine Rolle
sein muss oder ein Closeout-Schritt reicht. Den Ausschlag gibt der Nachtrag:
Zwölf Kaskaden aufzuarbeiten sprengt jeden Closeout, und ohne den Nachtrag ist
das Tagebuch für die halbe Projektgeschichte blind.

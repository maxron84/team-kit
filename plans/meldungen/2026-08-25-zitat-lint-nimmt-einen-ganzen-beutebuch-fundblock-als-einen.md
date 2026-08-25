# zitat_lint nimmt einen ganzen Beutebuch-Fundblock als EINEN Absatz und meldet unabtragbar

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter. Sechs
  Kaskaden gebaut, 22 Beutebuch-Funde, 35 Backlog-Einträge — also ein
  Beutebuch, das lange genug gewachsen ist, damit die Sache auffällt.

## Was passiert ist

`python3 team/tools/zitat_lint.py` steht in diesem Projekt seit zwei
Closeouts auf **Exit 3 mit genau einem Befund**, und dieser Befund lässt
sich nicht abtragen:

```
plans/beutebuch.md:549: zitiert BL-28 als offene Frage, Status ist aber
'**erledigt (Kaskaden 4 und 5, Stufen 19-27, Commits `6bda78a'
    … ### HM-11 — Auf dem Leitformat Handy ist „Senden" nicht antippbar …
```

Der gemeldete Fundblock ist rund 35 Zeilen lang. Die Referenz auf den
erledigten Eintrag steht in **Zeile 582**:

> Der Zwei-Spalten-Entwurf des Lehrerpults als Ganzes war eine
> **Kaskaden**-Aufgabe und stand als `BL-28` im Backlog (dort inzwischen
> **erledigt**, Kaskaden 4 und 5).

Das ist bereits Vergangenheitsform — der Satz war zuvor im Präsens, und das
Nachziehen hat den Befund **nicht** zum Verschwinden gebracht. Die
Zukunftswendung, die ihn auslöst, steht nämlich **27 Zeilen weiter oben**, in
Zeile 576, und hat mit dem zitierten Eintrag nichts zu tun:

> … ist kaputt, nicht „**noch nicht** optimiert".

Das ist ein **wörtliches Zitat aus der `CLAUDE.md`** des Projekts, in dem der
Mobile-First-Entscheid festgehalten ist. Es umzuformulieren hieße, ein Zitat
zu fälschen, dessen ganze Pointe der Wortlaut ist.

## Wo es steckt

`team/tools/zitat_lint.py`, Funktion `absaetze()`:

```python
def absaetze(text):
    """(startzeile, text) je Absatz — die Einheit, in der 'Zukunftsform'
    beurteilt wird. Ein Absatz endet an einer Leerzeile."""
```

`pruefe_datei()` prüft je Absatz erst `ZUKUNFT_RE.search(absatz)` und sucht
dann **im selben Absatz** nach Backlog-Referenzen. Die Absatz-Einheit ist die
einzige Nähe-Bedingung, die es gibt.

Diese Heuristik passt zu Roadmap und Skizzen, aus denen sie stammt: Dort sind
Absätze kurz, und „Zukunftswendung plus Nummer im selben Absatz" ist ein
brauchbares Signal. Ein Fundblock im **Beutebuch** ist dagegen eine
Markdown-Liste **ohne** Leerzeile — der ganze Fund, von der Überschrift bis
zur `Reproducer-Test`-Zeile, ist per Definition **ein** Absatz. Das Fenster
ist damit nicht ein Satz, sondern ein Dokumentabschnitt.

Das Fund-Format, das diesen Aufbau erzeugt, steht im Kit selbst — in der
`## Vorlage` im Beutebuch-Kopf und in `CLAUDE.md` („Fund-Format"). Es ist also
kein Sonderweg dieses Projekts, sondern die vorgesehene Schreibweise.

## Warum das jede Installation trifft

`zitat_lint.py` liegt in `team/tools/`, und das Fund-Format, das die
Fehlmeldung auslöst, ist die Kit-Vorlage. **Jede** Installation, deren
Beutebuch einen Fund enthält, der (a) irgendwo eine Backlog-Nummer nennt und
(b) irgendwo im selben Block eine der Wendungen aus `ZUKUNFT` trägt, bekommt
denselben unabtragbaren Befund, sobald dieser Eintrag erledigt wird. Beides
ist in einem gewachsenen Beutebuch der Normalfall: Fundblöcke sind lang, sie
grenzen sich gern gegen Backlog-Aufgaben ab („das ist eine Kaskaden-Aufgabe,
hier geht es um …"), und sie zitieren Regeltexte.

**Der Schaden ist nicht die eine Zeile, sondern die Gewöhnung.** Der
Docstring des Werkzeugs nimmt sich ausdrücklich vor, „lieber einen Fall zu
wenig als dauernd das Falsche" zu melden — hier tut es das Gegenteil, und
zwar dauerhaft: Der Befund ist durch Umformulieren nicht wegzubekommen. In
diesem Projekt hat ihn ein Closeout als „erklärt" durchgewunken, der nächste
stand vor demselben. Ein Lint, der bei jedem Lauf denselben unbehebbaren
Befund meldet, erzieht dazu, seinen Exit-Code zu überlesen — und dann fällt
der **echte** Befund daneben nicht mehr auf. Genau dafür ist das Werkzeug
gebaut worden.

## Was ich schon versucht habe

1. **Den zitierenden Satz nachgezogen** (Präsens → Vergangenheit, plus den
   Vermerk, dass der Eintrag erledigt ist). Das ist die im Werkzeug
   vorgeschlagene Abhilfe — *„dann die Zukunftsform aus dem Satz nehmen"*.
   Wirkungslos: Die auslösende Wendung steht in einem **anderen** Satz, 27
   Zeilen entfernt.
2. **Die auslösende Wendung entschärfen** — verworfen. Sie ist ein wörtliches
   Regelzitat.
3. **Kein lokaler Fix am Werkzeug.** Der Befund ist im Backlog dieses
   Projekts als bekannter Sockel vermerkt: Exit 3 mit genau einem Befund ist
   der Normalzustand, ein **zweiter** Befund ist echt. Das ist eine Krücke und
   als solche benannt — sie macht das Werkzeug nicht schärfer, sie merkt sich
   nur seine Unschärfe.

**Vorschlag** (beides ohne neue Datenquelle, beides schmal):

- **Listenpunkte als Absatzeinheit.** In `absaetze()` zusätzlich zur
  Leerzeile eine Zeile trennen lassen, die einen neuen Markdown-Listenpunkt
  öffnet (`-`, `*`, `1.`). Fundblöcke zerfielen damit in ihre Punkte, und die
  Nähe-Bedingung wäre wieder das, wofür sie gedacht war. Für Roadmap und
  Skizzen ändert sich wenig — dort stehen Zukunftswendung und Nummer
  typischerweise im selben Punkt.
- **Oder ein Zeilenabstands-Deckel.** Referenz und Wendung müssen innerhalb
  von N Zeilen zueinander liegen (N klein, etwa 5). Das ist unabhängig vom
  Markdown-Aufbau und würde denselben Fall greifen.

Die erste Variante trifft die Ursache genauer, die zweite ist robuster gegen
Formate, die es noch nicht gibt.

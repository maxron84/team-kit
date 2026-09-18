# Ein Fundblock waechst nach unten, gelesen wird er von oben - der Beutebuch-Vorlage fehlt eine Stand-Zeile am Kopf

- **Art**: Lücke in der Doku
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python und Electron,
  27 Kaskaden gebaut, rund 250 Testdateien.

## Was passiert ist

**Eine ganze Kaskade ist auf einer veralteten Lesung geplant worden — und der
Fehler war nicht Nachlässigkeit, sondern die Form des Dokuments.**

Beim Aushärten einer Kaskade band die zugrunde liegende Skizze zwei Funde
zusammen. Erst die Aushärtung selbst hat gemerkt, dass die eine Hälfte davon
**seit neun Tagen vollständig gebaut** war — in einer früheren Kaskade, drei
Stufen lang, mit Commits.

**Der Hergang ist banal und deshalb wiederholbar:** Der Fundblock ist **183
Zeilen** lang und trägt **fünf Nachträge**. Oben stehen Reproschritte,
Erwartung und Realität — der Stand des Entstehungstags. Unten stehen die
Nachträge, in denen der Bau protokolliert ist. Die Skizze zitierte den
**Kopf**. Wer einen langen Block aufschlägt, liest oben.

**Die Statuszeile hat es nicht aufgefangen.** Sie stand auf `offen` — was
formal richtig war (an dem Fund bleibt eine *Messung* offen, die der
Auftraggeber für undurchführbar erklärt hat), aber im Kopf des Blocks nicht
von *„hier ist nichts gebaut"* zu unterscheiden ist.

**Der Schaden war hier gering** — die Aushärtung hat den Fehler gefunden,
bevor gebaut wurde, und die Kaskade wurde von zehn auf fünf Stufen
zugeschnitten. **Teuer war die Stelle, an der es auffiel:** beim Vorlegen der
Kandidaten, also nachdem eine Option formuliert war, die es nicht mehr gab.

## Wo es steckt

In der **Fund-Vorlage** — dem `## Vorlage`-Block, den das Werkzeug oben ins
Beutebuch schreibt, und damit in jedem Fundblock, der danach entsteht:

    ### HM-<Nr> — <Kurztitel>
    - **Angreifer**: …
    - **Schweregrad**: …
    - **Status**: offen
    - **Reproschritte**: …

**Der Kopf sagt, was am Entstehungstag galt. Nichts darin sagt, wann zuletzt
jemand etwas hinzugefügt hat.**

## Warum das jede Installation trifft

**Die Vorlage kommt vom Kit, und die Bauform, die das Problem erzeugt, ist die
vom Kit vorgeschriebene:** Funde werden **nachgetragen**, nicht überschrieben —
das ist richtig so, denn die Historie eines Funds ist oft der interessanteste
Teil. Genau dadurch wächst jeder wichtige Fund **nach unten**, während jede
Vorlage, jede Verlinkung und jede Leserichtung **oben** beginnt.

**Je wichtiger ein Fund, desto länger sein Block, desto größer der Abstand
zwischen dem, was oben steht, und dem, was gilt.** Der Fehler wächst also mit
der Bedeutung des Eintrags — und trifft zuerst die Rolle, deren Arbeit am
teuersten ist: die planende.

**Das Archiv verschiebt Blöcke wörtlich** und ändert daran nichts; ein langer
Fund bleibt lang.

## Was ich schon versucht habe

**Nichts lokal gefixt** — eine Änderung an der Vorlage hätte beim nächsten
Update ohnehin eine Verfallszeit, und die Nummernvergabe hängt mit daran.

**Vorschlag, der die bestehende Form nicht bricht:** eine **Stand-Zeile** am
Kopf, die der letzte Schreibende mitzieht:

    ### HM-<Nr> — <Kurztitel>
    - **Angreifer**: …
    - **Schweregrad**: …
    - **Status**: offen
    - **Stand**: 2026-09-18 — zuletzt ergaenzt: Bau durch Kaskade 13 belegt
    - **Reproschritte**: …

**Zwei Eigenschaften, auf die es ankommt:**

1. **Sie trägt ein Datum UND einen Halbsatz.** Ein Datum allein sagt nur
   *„hier ist etwas passiert"*, nicht *„was oben steht, gilt nicht mehr"*.
   Der Halbsatz ist das, was die Skizze gebraucht hätte.
2. **Sie ist maschinell prüfbar.** Das Beutebuch-Werkzeug hat bereits ein
   `lint`, das eine Statuszeile meldet, die auf keinen Wert der Kette passt.
   Dieselbe Prüfung kann melden, wenn ein Block **Nachträge unterhalb der
   Reproschritte** hat, dessen Stand-Zeile aber **älter** ist als der jüngste
   davon — das ist genau der Zustand, der hier zugeschlagen hat.

**Ob das Werkzeug die Zeile beim Schreiben selbst mitzieht** (statt sie der
Rolle aufzuerlegen), ist die bessere, aber teurere Lösung. Als Prompt-Auflage
wäre sie eine weitere Regel, die von Gewissenhaftigkeit abhängt — und die
Erfahrung hier ist, dass genau diese Sorte still zurückfällt.

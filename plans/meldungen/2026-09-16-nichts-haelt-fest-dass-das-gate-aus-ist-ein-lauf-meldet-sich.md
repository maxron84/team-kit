# Nichts haelt fest, dass das Gate AUS ist - ein Lauf meldet sich als fertig, waehrend der Baum rot ist

- **Bezug**: BL-79
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst
  plus Electron-Oberfläche, rund 1000 Tests, 23 gebaute Kaskaden.

## Was passiert ist

In der Fixphase einer Kaskade aktivierte ein **korrekter** Frank-Fix einen
latenten Defekt in einem älteren Wächter. Der Baum wurde rot — und blieb es
über eine Stunde und mehrere Rollen-Läufe hinweg, **ohne dass irgendeine Stelle
das festgehalten hätte.**

**Jede beteiligte Rolle hat sich dabei regelkonform verhalten:**

- Frank trug den Beifang als eigenen Fund ein (Finder ≠ Fixer), klebte den
  fremden Test **nicht** mit einer Marke zu und belegte nach der geltenden
  Regel, dass **sein** Fix keinen **neuen** Fehlschlag erzeugt.
- Der neue Fund bekam Status `offen`. Die Fixphase fragt aber nach
  `an Frank übergeben` — und meldete folgerichtig *„nichts zu tun"*.
- Die beiden folgenden Frank-Läufe maßen denselben roten Baum, verglichen ihn
  gegen denselben roten Ausgangszustand und kamen jeweils korrekt zu dem
  Schluss, nichts verschlimmert zu haben.
- Der Abschlussbericht des Laufs meldete den Lauf als **fertig**.

**Der Regelapparat funktioniert hier genau wie gebaut, und das Ergebnis ist
trotzdem falsch:** Ein Lauf hat sich als abgeschlossen gemeldet, während das
Qualitäts-Gate aus war.

## Wo es steckt

- Die Regel *„ein Fix scheitert nicht an fremdem Flackern"* (Vergleich gegen
  den Ausgangszustand) — **sie ist richtig und darf nicht zurückgedreht
  werden.** Was fehlt, ist ihre Gegenrichtung.
- Die Fixphase (`pwsh/redteam.ps1` bzw. die Fix-Kette) — sie fragt nach
  Fund-Status, nicht nach Suitenstand.
- Der Abschlussbericht der Vollautomatik — er kennt Stufen, Funde, Kosten und
  Caps, aber **keinen Suitenstand**.

## Warum das jede Installation trifft

Die Bauform ist strukturell: **Jede Rolle misst den Suitenstand einzeln, und
keine gibt ihn weiter.** Ralph misst vor dem Promise, Frank misst vor und nach
seinem Fix — und beide werfen die Messung weg, sobald sie ihre eigene Frage
beantwortet hat. Es gibt keinen Ort, an dem der Satz *„das Gate ist seit HH:MM
rot"* stehen könnte, und deshalb kann auch keine Zusammenfassung ihn lesen.

Das ist die **zweite Wiederholung** derselben Lage in diesem Projekt: Schon ein
früherer Fall (Beifang bleibt auf `offen`, die Fixphase sieht ihn nie) ist als
eigene Meldung eingereicht worden. Damals war der Preis ein liegengebliebener
Fund. Diesmal war es das Gate.

## Was vorgeschlagen wird

**Eine Lauf-Datei, die den roten Ausgangszustand trägt, und ein
Abschlussbericht, der sie liest.**

1. **Schreiben:** Stellt eine Rolle fest, dass der Baum **schon vor ihrer
   Arbeit** rot war — genau der Fall, für den die Regel gegen fremdes Flackern
   existiert —, schreibt sie das in eine Lauf-Datei: Zeitpunkt, Rolle, die
   Namen der roten Tests. Die Messung liegt in diesem Moment ohnehin vor; es
   ist ein zusätzliches Schreiben, keine zusätzliche Messung.
2. **Lesen:** Der Abschlussbericht prüft die Datei. Ist sie belegt, druckt er
   **nicht** *„Bau abgeschlossen"*, sondern eine eigene Zeile: *„Lauf beendet,
   Gate ROT seit HH:MM — rote Tests: …"*, und beendet sich mit einem eigenen
   Code.
3. **Löschen:** Meldet eine spätere Rolle den Baum wieder grün, wird die Datei
   geleert. Damit bleibt kein Grabstein stehen, der beim nächsten Lauf
   fälschlich alarmiert.

**Das ist ausdrücklich keine Verschärfung für die einzelne Rolle.** Frank soll
weiterhin an fremdem Flackern nicht scheitern — er soll es nur nicht mehr
**für sich behalten**. Die Regel bleibt, was ihr fehlt, ist die Buchführung.

> **Warum die Fund-Ebene dafür nicht reicht:** Man könnte die Fixphase auch
> nach Funden im Status `offen` fragen lassen. Das hilft in diesem Fall, löst
> aber die falsche Hälfte — ein rotes Gate kann auch ohne Fundeintrag
> entstehen, und ein offener Fund bedeutet umgekehrt nicht, dass die Suite rot
> ist. Der Suitenstand gehört an den Suitenstand gebunden.

## Was ich schon versucht habe

Lokal nichts gebaut — der Fund sitzt in der Rollen-Kette und im
Abschlussbericht, also im Kit.

Der Behelf, mit dem hier gearbeitet wird, ist eine **Handprüfung im Closeout**:
Der Architekt fährt das Gate nach jedem Lauf selbst und nimmt den gedruckten
Abschlussbericht ausdrücklich **nicht** als Beleg für einen grünen Baum. Genau
so ist der Fall überhaupt aufgefallen — und genau so ist er beim nächsten Mal
wieder nur dann auffindbar, wenn jemand daran denkt.

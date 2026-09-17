# Der Vordergrund-Rat setzt voraus dass die Werkzeugfrist erhoehbar ist

- **Bezug**: BL-68
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst plus
  Electron-Oberfläche, rund 1165 Tests, 24 gebaute Kaskaden. Testsuite läuft
  parallel (`-n auto --dist loadgroup`).

## Was passiert ist

Das Update hat den Rat zum Smoke-Test umformuliert. Er lautet jetzt sinngemäß:
*Führe ihn im Vordergrund aus, er darf bis zu `TEAM_SMOKE_TEST_TIMEOUT` Sekunden
brauchen — erhöhe das Zeitlimit deines Werkzeugs entsprechend, viele Werkzeuge
erwarten MILLISEKUNDEN.* Derselbe Text steht in der Bibliothek (Smoke-Zeile und
Fixer-Nachsatz) und sinngemäß in allen vier Rollen-Briefings.

**Die Ergänzung um die Einheit ist richtig und hilfreich.** Der Fehler steckt in
der Voraussetzung dahinter: *„erhöhe das Zeitlimit"* setzt voraus, dass es
erhöhbar ist.

**In diesem Projekt ist es das nicht.** Die Höchstfrist des Agenten-Werkzeugs
beträgt 600000 ms und ist zugleich ihr **Maximum** — kein Vorgabewert, den man
anhebt, sondern eine Obergrenze. Der Default `TEAM_SMOKE_TEST_TIMEOUT=600`
trifft sie exakt; jeder Lauf darüber ist nicht mehr abzudecken.

**Und die Suite liegt regelmäßig darüber.** Sieben Messpunkte auf praktisch
demselben Stand, alle mit derselben Parallelisierung:

    417,90 · 488,18 · 526,68 · 634,97 · 651,49 · 672,03 · 947,26 s

**Vier von sieben liegen über der Grenze**, der höchste um 58 %. Die Streuung
ist Maschinenzustand, nicht Testmenge — der zweitschnellste Lauf hatte mehr
Tests als die langsamen.

**Was dann passiert, ist der eigentliche Schaden.** Wer dem Rat folgt und im
Vordergrund startet, wird vom Werkzeug **automatisch in den Hintergrund
verschoben**, sobald die Frist reißt. Damit ist genau der Zustand hergestellt,
vor dem derselbe Absatz warnt: Die Arbeit läuft weiter, das Promise fehlt, das
Log meldet trotzdem Erfolg — der vierte Ausgang (`BL-41`). **Dieses Projekt ist
daran fünfmal gescheitert**, bevor es sich eine Ausnahme gab.

## Wo es steckt

- `geteilt/lib.*`, in der Smoke-Zeile des Rollen-Prompts und im Nachsatz für den
  Fixer — beide Texte raten zum Erhöhen, ohne einen Ausweg für den Fall zu
  nennen, dass die Frist eine Obergrenze ist.
- `geteilt/prompts/rolle-*.md` — dieselbe Aussage in allen vier Briefings.
- Zusätzlich: Das Update hat aus dem Briefing der bauenden Rolle die
  **Projektausnahme entfernt**, die diesen Fall abfing (eigene Meldung, dort
  geht es um das Überschreiben an sich).

## Warum das jede Installation trifft

Der Rat steht in `geteilt/`, erreicht also jede Rolle jeder Installation. Er ist
für den Normalfall richtig — eine Suite, die unter die Werkzeugfrist passt,
gehört in den Vordergrund, und die Millisekunden-Ergänzung verhindert einen
realen Fehlgriff.

**Er wird nur dort falsch, wo die Frist eine Obergrenze ist statt eines
Vorgabewerts, und das ist keine Eigenschaft des Projekts, sondern des
Werkzeugs.** Jede Installation mit einer langen Suite trifft es, und sie merkt
es genau einmal: beim ersten Lauf, der über die Grenze geht — also wenn die
Arbeit schon bezahlt ist.

**Vorschlag, in der Reihenfolge der Eingriffstiefe:**

1. **Den Rat um seinen Vorbehalt ergänzen.** Ein Halbsatz genügt: *„…soweit
   dein Werkzeug das zulässt; ist seine Frist eine Obergrenze und die Suite
   länger, siehe unten."* Damit wird aus einer Anweisung eine Anweisung mit
   benanntem Geltungsbereich.
2. **Den Ausweg mitliefern**, statt ihn jedem Feldprojekt zu überlassen: ein
   Hintergrundlauf mit Ausgabe in eine Datei plus eine **Vordergrund**-Warteschleife,
   die unterhalb der Frist pollt und so oft wiederholt wird wie nötig. Das
   verletzt den Sinn der Regel nicht — es wird nicht auf eine Benachrichtigung
   gewartet, die headless nie kommt, sondern auf einen Dateiinhalt. Dieses
   Projekt fährt so seit einem halben Jahr und hat seither keinen Fall des
   vierten Ausgangs mehr gehabt.
3. **Erkennen statt raten:** Das Kit kennt `TEAM_SMOKE_TEST_TIMEOUT`. Läge
   daneben ein Wert für die tatsächliche Werkzeugfrist, könnte die Smoke-Zeile
   den passenden der beiden Wege selbst nennen, statt in beiden Fällen denselben
   zu empfehlen.

## Was ich schon versucht habe

Die Projektausnahme lokal in den Briefings der bauenden Rolle und des Fixers
wiederhergestellt, mit Begründung und Messwerten im Text, damit die nächste
Instanz den Vorrang erkennt. **Der Fixer brauchte einen eigenen Absatz**: Er
fährt den Smoke-Test häufiger als die bauende Rolle, hat aber keinen eigenen
Smoke-Abschnitt im Briefing und wird sonst allein vom Bibliothekstext erreicht.

Beides hat die bekannte Verfallszeit und steht beim nächsten `--update` wieder
zur Debatte — deshalb diese Meldung.

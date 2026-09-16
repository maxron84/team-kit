# sitzung-messen --projekt . trifft im Closeout mit hoher Wahrscheinlichkeit einen bereits gebuchten Rollen-Lauf

- **Bezug**: BL-88
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst
  plus Electron-Oberfläche, rund 1000 Tests, 23 gebaute Kaskaden, Ledger mit
  79 Zeilen über acht Wochen. Auth durchgehend Abo, Modelle `sonnet` für die
  Loop-Rollen und `opus` für Architekt und Forensiker.

## Was passiert ist

Das Architekten-Briefing nennt im Closeout genau diesen Aufruf:

```
python team/tools/kosten.py sitzung-messen --projekt .
```

`--projekt .` wählt das **zuletzt geänderte** Transkript in der Ablage des
Projekts. **In dieser Ablage liegen aber nicht nur interaktive Sitzungen,
sondern auch die Transkripte jedes headless-Rollen-Laufs** — jede Ralph-Stufe,
jeder Harry-/Marv-Sweep, jeder Frank-Fix schreibt eines.

Diese Rollen-Läufe sind zu diesem Zeitpunkt **längst gebucht**: Der Closeout
ruft unmittelbar davor `--rollen-abschluss` auf, das sie aus den Roh-Logs in
die Zeilen `roles` und `ralph` schreibt. Wer danach `sitzung-messen --projekt .`
nimmt und das Ergebnis als Architektenkosten bucht, **bucht denselben Lauf ein
zweites Mal** — diesmal unter `architekt`.

**Auffallen kann das an keiner Stelle.** Es entstehen zwei für sich plausible
Zeilen mit **verschiedener** Rolle; der Kollisionsschutz von
`--akteur-abschluss` schlägt nur bei **derselben** Rolle plus Kaskade an.
`--ledger-pruefen` schweigt, weil für eine interaktive Sitzung ohnehin kein
Rohlog existiert, gegen den es prüfen könnte. `--budget` zeigt eine plausible
Summe.

**Wie wahrscheinlich der Fehlgriff ist, lässt sich beziffern.** In der
Transkript-Ablage dieses Projekts liegen **379** Transkripte. Davon sind

| | |
|---|---|
| **324** | Rollen-Läufe (genau **ein** echter Nutzer-Prompt) |
| **55** | interaktive Sitzungen (mehr als einer) |

**85 % der Kandidaten sind also die falschen** — und zeitlich ist es eher
schlimmer als das: Ein Closeout folgt unmittelbar auf einen Lauf, und die
jüngsten Transkripte sind dann genau dessen Rollen. Im Fenster der letzten
Kaskade dieses Projekts standen **14 Rollen-Transkripte gegen 2 interaktive**.

## Wo es steckt

- `team/tools/kosten.py`, Verb `sitzung-messen`, Zweig `--projekt` — er
  sortiert nach Änderungszeit und nimmt das erste, ohne die Art des
  Transkripts zu prüfen.
- `team/prompts/rolle-architekt.md` — nennt den Aufruf als den
  Standardweg des Closeouts, ohne Warnung.

## Warum das jede Installation trifft

Die Ablage, aus der `--projekt` wählt, ist dieselbe, in die **jede** Rolle
schreibt — das ist keine Eigenheit dieses Projekts, sondern die Bauform des
Werkzeugs. Jede Installation mit automatisierten Rollen hat dasselbe
Verhältnis: Je fleißiger der Loop, desto mehr Rollen-Transkripte, desto
unwahrscheinlicher ist es, dass `--projekt .` das Richtige trifft.

Und der Schaden ist still und dauerhaft: eine zu hohe Architektenzeile, die
niemand mehr auseinanderrechnen kann, weil die Notiz sie als Architektenarbeit
ausweist.

## Was vorgeschlagen wird

**Die Unterscheidung ist maschinell trivial und in dieser Meldung an 379
Transkripten gemessen: Ein Rollen-Lauf hat genau EINEN echten Nutzer-Prompt,
eine interaktive Sitzung mehrere.**

Beim Zählen sind Sätze mit `type: "user"` zu überspringen, deren `content` ein
`tool_result` enthält — Tool-Ergebnisse tragen ebenfalls die Rolle `user`. Ohne
diesen Abzug zählt dieselbe Messung 26 bis 194 statt 1 bis 7, und die Trennung
verschwindet.

Drei Stufen, aufsteigend im Aufwand, jede für sich schon wirksam:

1. **Warnen.** Trifft `--projekt .` ein Transkript mit genau einem echten
   Nutzer-Prompt, druckt `sitzung-messen` eine Zeile: *„Das sieht nach einem
   Rollen-Lauf aus — der ist über `--rollen-abschluss` vermutlich schon
   gebucht."* Kein Abbruch, nur der Satz an der Stelle, an der er gelesen wird.
2. **Auswählen statt raten.** `--projekt .` überspringt Rollen-Transkripte und
   nimmt das zuletzt geänderte **interaktive**. Ein Schalter
   (`--auch-rollen`) stellt das alte Verhalten her, für den Fall, dass jemand
   bewusst einen Rollen-Lauf nachmessen will.
3. **Zeigen, was zur Wahl stand.** `--projekt .` nennt in einer Zeile, wie
   viele Kandidaten es gab und welchen es genommen hat. Das ist auch gegen den
   Nachbarfehler gut: die Sitzung, die nach ihrer Buchung weitergelaufen ist
   (eigene Meldung vom selben Tag).

**Stufe 1 allein würde diesen Fehler im Feld verhindern** und ist ein Zähler
über eine Datei, die ohnehin schon zeilenweise gelesen wird.

## Was ich schon versucht habe

Lokal ist **nichts** gebaut — der Fehler sitzt in `team/tools/kosten.py`, und
ein Patch dort hätte ein Verfallsdatum beim nächsten `--update`
(`BL-42`/`BL-58`; in diesem Projekt genau so passiert mit dem Preis-Patch).

Was dieses Projekt beisteuern kann, ist die **Messung** oben: 379 Transkripte,
324 gegen 55, die Trennung sauber und ohne Grenzfall — kein Transkript lag
zwischen den beiden Klassen. Der Zähler ist damit als Kriterium belegt, nicht
nur plausibel.

Behelf bis dahin: im Closeout **nicht** `--projekt .` nehmen, sondern das
eigene Transkript über seinen **Pfad** messen. Das setzt voraus, dass man es
kennt — und genau deshalb ist es ein Behelf und keine Lösung.

# Exit 43 hat eine Spielart, die das Zwei-Schritt-Verfahren offen laesst: die Warteschleife selbst im Hintergrund

- **Bezug**: BL-118
- **Art**: Lücke
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, Suite ~1375 Tests, Laufzeit 331–973 s

## Was passiert ist

Ein Frank-Aufruf endete in **Exit 43** — sechster Fall in diesem Projekt.
Neu daran: Es war der **erste mit dem Zwei-Schritt-Verfahren im Briefing**.
Die fünf vorigen Fälle hatten es nicht; deshalb war es nachgetragen worden.

Das Log der Rolle: `subtype: success`, 37 Turns, 443 s, kein Commit, der Fund
danach unverändert auf `an Frank übergeben`. Das `result`-Feld sagt wörtlich:

```
I'll pause here and wait for the background wait-loop task to notify me
when the pytest run finishes, instead of continuing to poll manually.
```

**Frank hat beide Schritte gebaut.** Den Testlauf im Hintergrund mit
Umleitung in eine Datei — richtig. Die Warteschleife
(`timeout … bash -c 'until grep -qE …'`) — ebenfalls richtig. Und dann hat er
**die Warteschleife selbst** in den Hintergrund geschoben und auf deren
Fertigmeldung gewartet.

Kosten: **2,01 USD für null Fortschritt.** Der Wiederholungslauf hat denselben
Fund in einem Anlauf sauber gefixt.

## Wo es steckt

Im Wortlaut des Zwei-Schritt-Verfahrens, wie es in den Vorlagen und in den
Rollen-Briefings steht.

Die Regel verbietet ausdrücklich, **auf eine Benachrichtigung zu warten** —
headless kommt keine. Sie sagt aber **nirgends**, dass der **Warteruf selbst**
im Vordergrund stehen muss. Genau durch diese Breite ist die Rolle gegangen,
und von innen sieht es wie Regeltreue aus: Beide vorgeschriebenen Schritte
sind ausgeführt, in der vorgeschriebenen Reihenfolge, mit den
vorgeschriebenen Befehlen.

Auch der Satz *„Exit 124 heißt erneut warten"* schließt die Lücke nicht — wer
die Schleife als Hintergrundaufgabe startet, bekommt gar keinen Exit-Code zu
sehen, auf den er reagieren könnte.

## Warum das jede Installation trifft

Das Verfahren steht in den Vorlagen des Kits und erreicht damit jede
Installation, deren Suite über der Vordergrundfrist des Agenten-Werkzeugs
liegt — und das ist der Regelfall, sobald ein Projekt eine nennenswerte Suite
hat. Die Frist ist zugleich das Maximum und lässt sich nicht anheben.

**Der Ausgang ist der teuerste, den das Werkzeug kennt:** Die Arbeit ist
getan, das Promise fehlt, der Lauf meldet „Stufe fertig, Quittung fehlt", und
bezahlt ist alles.

**Die Lücke ist nicht durch Sorgfalt zu schließen**, weil die Rolle sie nicht
als Regelverstoß erlebt. Sie hat im Gegenteil eine plausible Begründung dafür
(*„instead of continuing to poll manually"*) — Hintergrundaufgaben sind im
Werkzeugkasten der Rolle der gute Stil.

## Vorschlag

**Zwei Sätze in die Vorlage, beide explizit:**

1. *Nur der **Testlauf** gehört in den Hintergrund. Der **Warteruf** wird im
   Vordergrund aufgerufen, nicht als Aufgabe angelegt, und sein Exit-Code wird
   gelesen.*
2. *„Ich warte, bis sich der Wartelauf meldet" ist derselbe Fehler wie „ich
   warte auf die Benachrichtigung", nur eine Ebene höher.*

Der zweite Satz ist der wichtigere: Er benennt **den Griff**, statt die Regel
zu wiederholen. Eine Rolle, die den ersten Satz liest, kann ihn noch als
Formalie abtun; der zweite nimmt ihr die Begründung.

**Wenn eine Mechanik gewünscht ist:** Der Rollen-Wrapper kennt den Exit-Code
und das Log. Ein fehlendes Promise bei gleichzeitig `subtype: success` ist
bereits die Erkennung für Exit 43 — dort ließe sich zusätzlich prüfen, ob das
Log überhaupt eine vollständige Ergebniszeile des Testlaufs enthält, und die
Meldung entsprechend schärfen (*„der Testlauf war beim Sitzungsende noch nicht
fertig"* statt nur *„Quittung fehlt"*). Das ist Diagnose, kein Fix — aber es
würde den Fall beim nächsten Mal in einer Zeile erklären, statt ihn suchen zu
lassen.

## Was ich schon versucht habe

- **Lokal nachgezogen**: Das Rollen-Briefing dieses Projekts trägt jetzt beide
  Sätze oben. Das hat die bekannte Verfallszeit — beim nächsten `--update`
  ist es weg (`BL-42`/`BL-58`), deshalb diese Meldung.
- **Wiederholungslauf**: derselbe Fund, ein Anlauf, sauber gefixt. Die Rolle
  ist also nicht überfordert; es war die Formulierung.

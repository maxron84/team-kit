# Exit 43 trotz Zwei-Schritt-Verfahren: die Warteschleife selbst lief im Hintergrund

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-25-exit-43-trotz-zwei-schritt-verfahren-die-warteschleife-selbs.md
      .\kit-melden.cmd ablegen  2026-09-25-exit-43-trotz-zwei-schritt-verfahren-die-warteschleife-selbs.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-25-exit-43-trotz-zwei-schritt-verfahren-die-warteschleife-selbs.md   # sonst: Pull Request
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python mit Electron-Oberfläche; Suite rund 1600 Tests, parallel 290–700 s, also um die 600-s-Vordergrundgrenze des Agenten-Werkzeugs

## Was passiert ist

Das Feldprojekt schreibt in seiner `CLAUDE.md` ein verbindliches
Zwei-Schritt-Verfahren für den Smoke-Test vor, genau gegen Exit 43:

1. Testlauf mit `nohup … > "$LOG" 2>&1 &` im Hintergrund starten.
2. **Im Vordergrund** mit `timeout 500 bash -c 'until grep -qE … "$LOG"; do sleep 5; done'`
   warten, bei Exit 124 erneut.

Eine Ralph-Stufe hat Schritt 1 richtig gemacht und dann **Schritt 2 selbst
mit `run_in_background` gestartet**. Danach endete die Sitzung. Das
`result`-Feld sagt es wörtlich:

> The background wait-loop for the smoke test is still running (up to ~500 s
> per the project's documented gate variance). I'll wait for its completion
> notification before proceeding — no further action needed from me right now.

Der Loop meldete korrekt Exit 43 (Arbeit uncommittet vorhanden, Promise
fehlt, BL-207: ein Verifikationslauf läuft noch). Der verwaiste Testlauf war
danach grün; die Stufe wurde von Hand quittiert.

**Neu daran:** Bisher lag in allen Exit-43-Fällen der *Testlauf* ohne
Warteschleife im Hintergrund. Hier hielt sich die Rolle an das Verfahren und
verschob die *Warteschleife* — also genau den Teil, der das Warten auf eine
Benachrichtigung ersetzen soll. Die Regel „im Vordergrund warten" steht im
Text, hat aber nicht gereicht: Das Modell hat „Vordergrund" offenbar nicht
als Verbot des Hintergrund-Schalters seines Werkzeugs gelesen.

## Wo es steckt

In der Regel, die das Kit für bauende Rollen gegen Exit 43 vorgibt
(`CLAUDE.md`, Abschnitt Loop-Mechanik, „Vierte Fehlerklasse"), und in den
Rollen-Briefings der bauenden Rollen (`team/prompts/rolle-ralph.md`,
`rolle-frank.md`). Beide beschreiben das **Was** (im Vordergrund warten),
nennen aber nicht das **Werkzeugmerkmal**, das es bricht: den Parameter
`run_in_background` (bzw. jede Hintergrund-Option) am Aufruf der
Warteschleife.

## Warum das jede Installation trifft

Jedes Projekt, dessen Suite länger als die Vordergrundgrenze läuft, braucht
das Verfahren, und jedes übernimmt den Wortlaut aus den Kit-Vorlagen.
Headless kommt keine Benachrichtigung — die Sitzung endet in jedem Fall ohne
Promise, egal ob der Testlauf oder die Warteschleife im Hintergrund liegt.

**Vorschlag:** In Briefing und Regel ausdrücklich: *„Die Warteschleife
(Schritt 2) NIE mit `run_in_background` oder einer anderen
Hintergrund-Option starten. Sie endet von selbst nach höchstens 500 s; bei
Exit 124 denselben Befehl erneut im Vordergrund aufrufen."* Ergänzend könnte
die Exit-43-Selbstprüfung das `result`-Feld auf „wait-loop" bzw.
„Warteschleife" + „background" durchsuchen und diese Spielart eigens
benennen.

## Was ich schon versucht habe

Nichts lokal geändert: Die Regel steht in einer vom Kit gepflegten Datei und
würde beim nächsten Update überschrieben. Die Stufe wurde nach dem
Exit-43-Merkzettel des Loops von Hand quittiert (Suite nachgemessen, grün,
Stufen-Commit, `.ralph-state` weiter), der Neustart lief danach durch.

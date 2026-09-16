# Die Vollautomatik hängt endlos, wenn eine Rolle einen GUI-Enkel hinterlässt

**Gemeldet:** 2026-09-13, Feld B, Kit 2.13.1, pwsh/win32, neunzehnte Kaskade.
Lage: gewachsenes Projekt, Windows, nur pwsh-Bahn, Python + Electron.
**Betrifft:** `vollautomatik.ps1`, Funktion `Rolle-Starten` (die pwsh-Bahn;
die Bash-Bahn ist vermutlich genauso betroffen, hier nicht geprüft).
**Schwere:** hoch — der Lauf steht still, ohne Fehler, ohne Logzeile, ohne
Zeitgrenze. Er sieht von außen aus wie „arbeitet noch".

## Was passiert ist

Kaskade 19 baute sechs Stufen sauber durch. Um 02:07 loggte Ralph
`Stufe 95 liegt über RALPH_CAP=94 — Feierabend.` **Danach neun Stunden
nichts.** Kein Phase-2-Log, kein Abbruchbericht, kein Exit.

Der Befund am laufenden System:

- `vollautomatik.ps1` lief noch (PID 44020, seit 22:06 des Vortags).
- Es hatte **keinen einzigen Kindprozess.** `ralph.ps1` war längst beendet.
- Es hielt weiterhin `.team-loop.lock` (die Datei war für Fremdzugriffe
  gesperrt — `Device or resource busy`).
- `.vollautomatik-state` existierte **nicht**: `Phasen-Naechste 2` war nie
  erreicht worden. Der Lauf hing also **zwischen** dem Ende von Phase 1 und
  der ersten Anweisung danach.
- Drei `electron.exe`-Bäume liefen seit 01:36, 01:39 und 01:40 — also
  **innerhalb** der Laufzeit von Stufe 94 (01:19–02:07) gestartet, über
  `env.exe` als Ad-hoc-Prüfstände der bauenden Rolle. Einer davon zeigte
  einen **modalen Fehlerdialog** („A JavaScript error occurred in the main
  process") und wartete auf einen Klick, den es headless nie gibt.

## Die Ursache

`Rolle-Starten` streamt die Ausgabe des Rollen-Skripts über eine **Pipeline**:

```powershell
& pwsh -NoProfile -File $Skript @Argumente 2>&1 | ForEach-Object { … }
```

Eine Pipeline endet erst bei **EOF** auf dem Leseende. EOF kommt aber erst,
wenn **jeder** Prozess das geerbte Schreibende losgelassen hat — nicht nur
das direkte Kind, sondern auch **Enkel und Urenkel**. Startet eine Rolle
(oder der Agent in ihr) einen Prozess, der das Rollen-Skript überlebt, wartet
der Orchestrator auf ein EOF, das niemals kommt.

**Das ist kein Sonderfall bei GUI-Prozessen, sondern ihr Normalfall:** Ein
Electron-Fenster, ein hängender Dienst, ein vergessener `--watch`-Prozess
halten das Handle beliebig lange. Der Fehlerdialog machte es hier nur
unübersehbar.

Bemerkenswert: `Rolle-Starten` streamt aus gutem Grund — `BL-181` beschreibt
ausführlich, warum die sammelnde Fassung (`$ausgabe = & pwsh …`) durch die
streamende ersetzt wurde. **Die sammelnde Fassung hatte dasselbe Problem**
(sie wartet ebenfalls auf EOF). Der Umbau hat es also weder verursacht noch
behoben; es war die ganze Zeit da und ist nur nie aufgetreten, weil bis
dahin keine Rolle einen überlebenden Prozess hinterließ.

## Was besonders teuer daran ist

1. **Es gibt keine Zeitgrenze.** Alle anderen Fehlklassen des Kits sind
   benannt und haben einen Ausgang: 42 (Session-Limit), 43 (`BL-41`, Promise
   fehlt), 1 (echter Fehler). Dieser Zustand hat **keinen** — er ist kein
   Fehler, er ist Stillstand.
2. **Die Anzeige lügt in Richtung „läuft".** `team-status.ps1` zeigt die
   letzten drei Zeilen des Lauf-Logs; die lauteten hier „Stufe 94
   abgeschlossen … Feierabend". Das liest sich wie ein Lauf kurz vor dem
   Ziel, nicht wie ein toter.
3. **Die Kaskade blieb ungeprüft.** Phase 2 wurde nie erreicht — und ein
   leeres Beutebuch heißt dann „niemand hat gesucht", nicht „nichts
   gefunden". `BL-212` hat genau diesen Irrtum für den Deckel-Abbruch schon
   entschärft; hier greift der Abbruchbericht gar nicht erst, weil es keinen
   Abbruch gibt.

## Vorschläge

Der erste ist der wichtigste; die anderen sind Zugabe.

1. **Auf das Kind warten, nicht auf die Pipe.** Den Prozess mit
   `Start-Process -PassThru` (bzw. `System.Diagnostics.Process`) starten,
   Ausgabe asynchron mitlesen und mit `WaitForExit()` auf **das Kind**
   warten. Dann ist das Ende des Rollen-Skripts das Ende des Wartens,
   unabhängig davon, was es hinterlässt. Das ist zugleich die Achse
   **Trennschärfe** aus der Feldregel: Der gesuchte Zustand ist *„das Kind
   ist fertig"*, und `WaitForExit` misst genau ihn, während EOF etwas anderes
   misst, das meistens damit zusammenfällt.
2. **Nach jeder Rolle die überlebenden Enkel melden.** Eine Zeile im Log
   („Rolle X hinterließ 3 laufende Prozesse: electron.exe …") macht den
   Zustand sichtbar, noch bevor er schadet — und liefert der nächsten
   Fixphase den Hinweis, ohne den man ihn nur durch Prozess-Forensik findet.
3. **Eine Obergrenze je Rollenaufruf** wäre der naheliegende Griff, ist aber
   der schwächere: Der gesuchte Fehlerzustand ist **unbegrenzt** (ein
   Hängen), und eine Frist müsste dann so großzügig sein, dass sie lange
   nutzlos bleibt — Vorschlag 1 braucht sie nicht.

## Wie es im Feld aufgelöst wurde

Die drei verwaisten Electron-Bäume beenden. Damit schloss die Pipe, der alte
Lauf lief weiter und schrieb `.vollautomatik-state` = 2; der Neustart setzte
über den Phasen-Zeiger (`BL-217`) direkt bei Phase 2 auf. **`BL-217` hat den
Schaden begrenzt** — ohne den Zeiger wäre Phase 1 samt ihrer 37,05 USD ein
zweites Mal gelaufen.

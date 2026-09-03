# frank.ps1 kennt die vierte Fehlerklasse nicht, ralph.ps1 schon

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt im neunten Kaskadenlauf, Windows,
  pwsh-Bahn, Python + Electron, rund 390 Tests, Suitenlaufzeit gut vier
  Minuten.

## Was passiert ist

In der Fixphase eines Vollautomatik-Laufs endete Franks erster Versuch an einem
Fund so (Rollenlog, gekürzt auf die Zeilen zur Sache):

```
subtype    : success
is_error   : false
num_turns  : 31
duration_ms: 673465
total_cost_usd: 1.4315091
result: "I'll pause here and resume once the background baseline run
         completes or the scheduled check-in fires."
```

Die Rolle hat den Smoke-Test also als **Hintergrund-Task** gestartet und auf
eine Benachrichtigung gewartet, die es headless nicht gibt. Das Log erklärt
sich selbst für erfolgreich, gibt aber kein Promise. Das ist **wörtlich** die
vierte Fehlerklasse, die die `CLAUDE.md`-Vorlage des Kits beschreibt
(„Sitzung beendet, Auftrag unquittiert").

**Behandelt wurde es als inhaltlicher Fehlversuch:**

```
[frank] <fund> Versuch 1 gescheitert
        (Budget/Promise/Commit/Dreisatz/Substanzbezug unvollständig) — Rollback.
Runde 2: Frank-Fehlversuch (ggf. Eskalation an Axel).
```

Der Zähler landete in `.frank-attempts`. Nach drei solchen Ausgängen stünde der
Fund auf `an Axel übergeben` — die teuerste Rolle des Teams, für ein Problem,
das die Rolle inhaltlich nie hatte.

## Wo es steckt

**`ralph.ps1` kennt diesen Ausgang, `frank.ps1` nicht.**

- `ralph.ps1` hat dafür einen eigenen Exit-Code: `exit 43` (Zeile 179),
  dokumentiert im Kopfkommentar (Zeile 14): *„43 = Stufe fertig, Quittung fehlt
  (BL-41): Das Log meldet Erfolg, …"*. Kein State-Fortschritt, aber auch keine
  Verbuchung als echter Fehler.
- `frank.ps1` prüft den Erfolg über Promise + Fix-Commit + Status (Zeilen
  149/163) und hat **genau einen** Fehlerpfad (Zeile 189) — generisch, mit
  Rollback und Zählerinkrement. Die Klasse „das Log meldet Erfolg, das Promise
  fehlt" ist dort nicht vorgesehen.

Der Rollback selbst ist richtig: Die Arbeitskopie ist unfertig. Falsch ist die
**Verbuchung als inhaltlicher Fehlversuch**, weil sie den Fund auf den
Eskalationspfad schiebt.

## Warum das jede Installation trifft

Die vierte Fehlerklasse ist in der Regelquelle des Kits für **jede bauende
Rolle** formuliert; implementiert ist sie nur in einer. Dieselbe Ursache führt
damit zu zwei verschiedenen Ergebnissen, je nachdem, welche Rolle
hineinläuft — und die Rolle, die es teurer macht, ist die ohne Behandlung.

Der Auslöser ist nicht exotisch: Er tritt auf, sobald die Projektsuite lange
genug läuft, dass das Modell sie in den Hintergrund legen möchte. In diesem
Feld ist es der **dritte** Fall in fünf Kaskaden (verworfene Arbeit: 2,59 USD,
1,84 USD, jetzt 1,43 USD — zusammen rund 5,90 USD), zweimal bei Frank, einmal
bei der bauenden Rolle. Nur beim letzteren war er im Lauf-Log als eigene Klasse
erkennbar.

**Verwandter Fall derselben Bauart, hier bereits als Feldbefund notiert:** Ein
Netzfehler **vor** dem ersten Token (Abo und API-Fallback beide
`ConnectionRefused`, 0 Turns, 0.0000 USD) zählt bei Frank ebenfalls als
inhaltlicher Fehlversuch. `frank.ps1` nimmt den Zähler beim Session-Limit
(Exit 42) ausdrücklich aus — die Unterscheidung existiert also, sie ist nur zu
eng gezogen.

## Was ich schon versucht habe

**Kein lokaler Eingriff in `frank.ps1`** — der Fund sitzt im Kit, ein lokaler
Fix hätte Verfallszeit bis zum nächsten `--update`. Lokal blieb es bei der
Datenreparatur des Zählers.

**Vorschlag (drei Zeilen Wirkung, eine Entscheidung):** `frank.ps1` bewertet
denselben Fall wie `ralph.ps1` — Log meldet Erfolg **und** Promise fehlt →
eigener Ausgang statt generischem Fehlerpfad: Rollback **ja** (die Arbeitskopie
ist unfertig), Fehlversuchszähler **nein**. Sinnvoll wäre, die Prüfung dort
abzulegen, wo beide Rollen sie sehen (Bibliothek statt Entrypoint), damit die
nächste bauende Rolle sie nicht ein drittes Mal fehlen lässt.

**Nicht zu verwechseln mit der Meldung vom 2026-08-27** („Die Vorsorge gegen
den vierten Ausgang fehlt im Briefing der bauenden Rolle"). Die betrifft die
**Prosa** des Briefings und gilt unverändert: `team/prompts/rolle-frank.md` und
`rolle-ralph.md` enthalten bis heute kein Wort zu „Smoke-Test im Vordergrund".
Diese Meldung hier betrifft die **Auswertung** des Ergebnisses — sie greift
auch dann, wenn die Rolle die Regel kennt und trotzdem hineinläuft.

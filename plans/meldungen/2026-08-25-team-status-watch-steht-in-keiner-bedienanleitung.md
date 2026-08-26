# `team-status --watch` steht in keiner Bedienanleitung — und ist der einzige Weg, der während eines Laufs überhaupt etwas zeigt

- **Art**: Fehler am Kit (Doku; kleiner Anteil Bedienung)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn (`--nur-pwsh`), Python + Electron, dritte Kaskade

## Was passiert ist

Der Stakeholder startete die Vollautomatik und fragte nach zwei Kaskaden
Erfahrung wörtlich: *„Ich sehe wieder kein Monitoring, das ist weil ich noch
kein Update vom Kit herausgefahren habe über dieses Projekt, korrekt?"*

Die Vermutung war falsch, und das ist der eigentliche Befund: **Das
Monitoring-Dashboard ist installiert und läuft.** `team-status.ps1` bezeichnet
sich im eigenen Kopf als *„Monitoring-Dashboard der T.E.A.M.-Vollautomatik"* und
bietet `--watch` mit Refresh alle 5 s. Es fehlte nichts — es war nur nicht
auffindbar.

## Wo es steckt

**`TEAM.md` nennt `--watch` an keiner Stelle.** Gesucht wurde in der
ausgelieferten Bedienanleitung nach allen Nennungen von `team-status`:

| Fundstelle in `TEAM.md` | Was dort steht |
|---|---|
| Kosten-Abschnitt | `team-status --budget` |
| Abschluss-Sequenz | `--rollen-abschluss`, `--architekt-abschluss` |
| Ledger-Prüfung | `--ledger-pruefen` |
| Werkzeugtabelle | „Pipeline, Beutebuch, Kaskadenstand" |

`--watch` kommt in **keiner** dieser Zeilen vor. Die Werkzeugtabelle beschreibt
den Momentaufnahme-Modus und lässt offen, dass es einen Live-Modus gibt. Der
Schalter steht ausschließlich im Kommentarkopf von `team-status.ps1` — also
dort, wo ein Anwender nicht nachschlägt.

**Warum das mehr wiegt als ein fehlender Doku-Eintrag:** Auf dieser Bahn ist die
Konsole während des gesamten Laufs stumm (eigene Meldung, gleiche Ablage:
`…-die-pwsh-bahn-puffert-die-ausgabe-jedes-kindprozesses-die-ba.md`).
`--watch` ist damit **der einzige mitgelieferte Weg**, einen laufenden Lauf zu
beobachten — und genau dieser Weg ist undokumentiert. Die beiden Fehler
verstärken sich: Wer nichts sieht, sucht in der Anleitung und findet nichts,
das ihm hilft.

## Zweiter, kleinerer Teil: das dokumentierte Beenden führt in eine Rückfrage, deren naheliegende Antwort die falsche ist

`team-status.ps1` schreibt im Live-Modus selbst die Zeile:

```
  (--watch: Refresh 5 s · Strg+C beendet)
```

Auf der pwsh-Bahn läuft der Einstieg über einen `.cmd`-Aufrufer
(`"%TEAM_PWSH%" -NoProfile -File "%~dp0team-status.ps1" %*`). Strg+C erreicht
die ganze Konsolen-Prozessgruppe: Die Schleife endet sofort, und **danach**
fragt `cmd.exe`:

```
Terminate batch job (Y/N)?
```

Beobachtet wurde genau die naheliegende Fehlreaktion — der Anwender antwortete
`N` („nein, bitte nichts abbrechen") und meldete anschließend ratlos zurück.
Richtig ist `Y`: Das Dashboard ist zu diesem Zeitpunkt bereits beendet, gefragt
wird nur noch nach der leeren Batch-Hülle.

**Das ist Windows-Standardverhalten und kein Defekt des Kits** — die
ausgelieferte Zeile „Strg+C beendet" ist auf dieser Bahn trotzdem unvollständig,
weil sie den sichtbaren Teil des Vorgangs verschweigt. Auf der Bash-Bahn gibt es
diese Rückfrage nicht; es ist also erneut eine **Bahn-Asymmetrie in einem Text,
der für beide Bahnen gilt**.

## Warum das jede Installation trifft

`TEAM.md` und `team-status.ps1` kommen beide aus dem Kit. Jede pwsh-Installation
bekommt damit dasselbe Paar: ein Live-Dashboard, das nirgends erwähnt wird, und
eine Beendigungszeile, die auf dieser Bahn zu einer unerklärten Rückfrage führt.
Beides ist billig zu beheben und spart genau die Ratlosigkeit, die hier zwei
Kaskaden lang bestand.

## Vorschlag für den Fix

1. **`--watch` in `TEAM.md` aufnehmen**, in der Werkzeugtabelle und im
   Abschnitt über den laufenden Betrieb — mit dem Satz, der ihn wirklich
   verkauft: *Auf der pwsh-Bahn ist dies während eines Laufs die einzige
   Ansicht, die etwas zeigt.*
2. **Die Beendigungszeile bahnspezifisch ergänzen**, z. B.:
   `(--watch: Refresh 5 s · Strg+C beendet · danach fragt cmd „Terminate batch
   job (Y/N)?" — Y ist richtig)`.
3. **Optional, aber wirksamer:** Beim Start der Vollautomatik einmal die Zeile
   ausgeben, mit der man den Lauf beobachten kann. Genau dort steht der Anwender
   und genau dort fehlt ihm die Information. Solange die Konsole stumm ist, ist
   das die einzige Zeile, die ihn überhaupt noch erreicht.

## Was ich schon versucht habe

Am Kit nichts geändert — der Lauf war aktiv, und die bauende Rolle committet mit
`git add -A`; jede angelegte Datei wäre in den nächsten Stufen-Commit gewandert.
Nachgesehen wurde rein lesend: alle `team-status`-Nennungen in `TEAM.md`, der
Kommentarkopf und der `--watch`-Zweig von `team-status.ps1` sowie der
`.cmd`-Aufrufer.

Behelf im Projekt: `--watch` in einem zweiten Fenster, plus der Hinweis, dass
`.ralph-state`, die Sperrprobe und die Commit-Liste die belastbaren
Lebenszeichen sind — nicht der Log-Block, der während des Laufs leer bleibt.

> **Anmerkung zum Melden selbst:** Diese Meldung konnte nicht über
> `kit-melden` angelegt werden — der Wrapper der pwsh-Bahn stirbt vorher an
> einer undefinierten Variablen (eigene Meldung liegt bei).

# Laufzeit-Ausgaben nennen Kit-Backlog-Nummern blank (BL-41), obwohl CLAUDE.md und TEAM.md Kit-BL- schreiben

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python plus
  Electron-Oberfläche; elf gebaute Kaskaden, eigener Backlog mit 48 Einträgen.

## Was passiert ist

Eine Stufe endete im vierten Ausgang. Der Abbruchbericht sagte wörtlich:

```
[ralph] STUFE FERTIG, QUITTUNG FEHLT (BL-41) — Stufe 55 hat kein <promise>…
    ✗ Keine Datei unter tests/ berührt (BL-135).
```

Beide Nummern meinen den **Kit**-Backlog. Im Feldprojekt ist `BL-41` aber
ebenfalls vergeben, für ein völlig anderes Thema (inerte Altlasten eines
Fund-Fixes). Wer der gedruckten Nummer im eigenen Backlog nachschlägt — und
das ist die naheliegende Handlung, weil der eigene Backlog der ist, den man
offen hat —, landet in einem unverwandten Eintrag, ohne dass irgendetwas auf
die Verwechslung hinweist.

## Wo es steckt

Die Laufzeit-Ausgaben der Bibliothek und der Entrypoints, insbesondere der
Block zum vierten Ausgang und die Selbstprüfung davor (`team/lib.psm1` bzw.
`team/lib.sh`, aufgerufen aus `ralph.ps1`/`ralph.sh`). Ein Rundblick über
`BL-<N>` in den ausgegebenen Texten dürfte weitere Stellen zeigen — die
Fehlerklasse ist der blanke Nummernraum in **jeder** Ausgabe, die ein Mensch
liest, nicht die einzelne Zeile.

## Warum das jede Installation trifft

Die Regel dagegen existiert bereits und ist im Kit als `BL-140` abgetragen:
Verweise auf den Kit-Backlog werden `Kit-BL-<N>` geschrieben, weil der
Nummernraum zwischen Kit und Feldprojekt doppelt belegt ist. `CLAUDE.md` und
`TEAM.md` halten sich seither daran, `zitat_lint.py` respektiert die
Unterscheidung sogar im Regex (`(?<!Kit-)`). **Nur die Laufzeit-Ausgaben nicht**
— also ausgerechnet die Stelle, an der ein Mensch die Nummer unter Zeitdruck
liest: im Abbruchbericht, wenn gerade eine Stufe gescheitert ist.

Jedes Feldprojekt mit eigenem Backlog ist betroffen, und je länger es läuft,
desto wahrscheinlicher kollidiert seine Nummer mit der zitierten: Der
Kit-Backlog ist im zweihundertsten Bereich, ein Feldprojekt beginnt bei 1 —
die niedrigen Kit-Nummern, die in den Ausgaben stehen (`BL-41`, `BL-135`,
`BL-205`, `BL-207`), liegen genau im Bereich, den ein gewachsenes Feldprojekt
selbst vergeben hat.

## Was ich schon versucht habe

Nichts gepatcht — ein Patch am Kit-Code hätte hier eine Verfallszeit bis zum
nächsten Update. Im Abschlussprotokoll des Feldprojekts steht die
Richtigstellung stattdessen als Fußnote am Zitat („im Lauflog als `BL-41`
ausgewiesen, gemeint ist `Kit-BL-41`"), was das Problem für diesen einen Fall
löst und für den nächsten nicht.

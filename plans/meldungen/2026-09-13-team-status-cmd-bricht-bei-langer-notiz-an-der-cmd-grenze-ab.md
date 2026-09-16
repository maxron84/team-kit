# `team-status.cmd` bricht bei einer langen Notiz an der cmd.exe-Grenze ab

**Gemeldet:** 2026-09-13, Feld B, Kit 2.13.1, pwsh/win32, neunzehnte Kaskade
(Nachlauf-Closeout). Lage: gewachsenes Projekt, Windows, nur pwsh-Bahn,
Python + Electron.
**Betrifft:** `team-status.cmd` — und damit alle `.cmd`-Aufrufer der pwsh-Bahn,
die einen langen Textparameter durchreichen (`--akteur-abschluss`,
`--architekt-abschluss`, `--rollen-abschluss`).
**Schwere:** mittel — der Abbruch ist sauber (es wird **nichts** gebucht), aber
er trifft ausgerechnet den Closeout, und die Meldung erklärt nichts.

## Was passiert ist

Der Architekten-Anteil einer Kaskade sollte mit `--akteur-abschluss` gebucht
werden. Die Notiz war 8256 Zeichen lang — nicht ungewöhnlich: Sie muss bei
`--addieren` den **vollständigen** bisherigen Text mitbringen, weil der Schalter
die Notiz **ersetzt**, und sie wächst deshalb mit jedem Nachlauf.

```
& .\team-status.cmd --akteur-abschluss architekt abo 38.9524 produkt $notiz --kaskade 19 --addieren
The command line is too long.
EXIT=1
```

Gebucht wurde nichts, das Ledger blieb unverändert (nachgezählt: 64 Zeilen vor
und nach dem Versuch). Der Abbruch ist also **nicht** halb — das ist die gute
Nachricht.

## Die Ursache

`team-status.cmd` ist ausweislich seines eigenen Inhalts nur ein
pwsh-Auflöser: Er sucht `pwsh.exe` und ruft damit `team-status.ps1 %*` auf. Die
gesamte Zeile läuft dabei durch **cmd.exe**, und dessen Kommandozeile ist auf
**8191 Zeichen** begrenzt. Der aufgelöste `pwsh.exe` hätte mit 32767 kein
Problem — die Grenze stammt allein aus dem Zwischenschritt.

Damit ist die Grenze an die **Bahn** gebunden, nicht an die Aufgabe: Dieselbe
Notiz ist über `team-status.ps1` anstandslos buchbar. Genau so wurde sie dann
auch gebucht.

## Warum die Meldung irreführt

`The command line is too long.` ist eine Meldung **von cmd.exe über cmd.exe** —
dieselbe Bauform wie `'pwsh' is not recognized`, die in `BL-123` bereits
behandelt wurde. Sie nennt weder das Werkzeug noch den Parameter noch die
Grenze, und sie legt nahe, die **Notiz** sei das Problem. Das ist sie nicht:
Der Text ist genau so lang, wie die `--addieren`-Semantik ihn erzwingt.

Wer die Meldung wörtlich nimmt, kürzt die Notiz — und wirft damit Ledger-Text
weg, den `--addieren` gerade deshalb vollständig verlangt.

## Vorschlag

Zwei Möglichkeiten, die erste ist die kleinere:

1. **Die Grenze abfangen, wo sie entsteht.** `team-status.cmd` kann die Länge
   seiner eigenen Argumentzeile prüfen und bei Überschreitung eine Meldung im
   Ton der `BL-123`-Behandlung ausgeben: *„Die Argumentzeile ist länger als die
   cmd.exe-Grenze von 8191 Zeichen. Das ist keine Grenze des Kits und kein
   Problem deiner Notiz — ruf denselben Befehl über `team-status.ps1` auf."*
2. **Den Zwischenschritt vermeiden.** Lange Textparameter aus einer Datei
   lesen, etwa `--notiz-datei <pfad>`. Das löst das Problem für alle
   `.cmd`-Aufrufer auf einmal und macht nebenbei das Zitieren langer Notizen
   in Skripten robuster (Anführungszeichen, Zeilenumbrüche).

Die zweite Möglichkeit hat einen zweiten Nutzen: Ein doppeltes
Anführungszeichen im Notiztext zerlegt den Aufruf heute ebenfalls (eigene
Meldung vom 2026-09-09). Beide Fälle verschwinden, wenn der Text nicht mehr
durch die Kommandozeile muss.

## Noch offen

Die `Kit-BL-<N>`-Zeile im Kit-Backlog, die auf diese Meldung zeigt, ist **noch
nicht geschrieben** — sie gehört ins Kit-Repo, das hier nicht liegt.

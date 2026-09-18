# Alle zehn .cmd-Wrapper geben UTF-8 in eine cp850-Konsole - BL-135 hat die dritte Haelfte nicht erreicht

- **Bezug**: BL-135 (archiviert, erledigt 2026-08-21)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1 plus Unreleased-Stand
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python und Electron,
  26 Kaskaden gebaut, rund 250 Testdateien.

## Was passiert ist

Ein Vollautomatik-Lauf, gestartet als `.\vollautomatik.cmd` aus einer
pwsh-Sitzung — der in `TEAM.md` dokumentierte Weg. Der Statusblock kam so an:

    ÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉ
      T.E.A.M.-Status ÔÇö 2026-09-18 10:07:52
    ÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉÔòÉ
      Kaskade : n├ñchste Stufe 132 / Cap 136
      Pipeline: ÔÜ¬ idle

Erwartet waren `═══`, `—`, `nächste`, `⚪`.

**Die Dateien sind dabei in Ordnung.** In der Logdatei desselben Laufs steht
für den Geviertstrich die Bytefolge `E2 80 94` — korrektes UTF-8 für U+2014.
Es ist die **Anzeige**, nicht die Ablage.

## Wo es steckt

Die Zeichen sind richtig kodiert und werden mit der falschen Tabelle gemalt.
Gegenprobe, ausgeführt:

    $ printf '\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90' | iconv -f cp850 -t utf-8
    ÔòÉÔòÉÔòÉ

`E2 95 90` ist U+2550 (`═`). Als cp850 gelesen ergibt es Zeichen für Zeichen
das Bild aus dem Statusblock oben.

**Die Kette:** pwsh-Eingabeaufforderung → `.cmd` → `cmd.exe` →
`pwsh -NoProfile -File …`. `cmd.exe` bringt die OEM-Codepage mit (hier 850).
`lib.psm1` setzt danach `[Console]::OutputEncoding` auf UTF-8 — das ist
richtig und es wirkt, aber es ändert nur, wie .NET **kodiert**, nicht, wie das
Terminal **dekodiert**.

**Es ist eine Gattung, kein Einzelfall.** Alle zehn Wrapper haben dieselbe
Bauform — `axel.cmd`, `frank.cmd`, `halbautomatik.cmd`, `harry.cmd`,
`kit-melden.cmd`, `marv.cmd`, `ralph.cmd`, `team-status.cmd`, `team-test.cmd`,
`vollautomatik.cmd`: je eine Zeile

    "%TEAM_PWSH%" -NoProfile -File "%~dp0<name>.ps1" %*

und keiner stellt eine Codepage.

**Warum `BL-135` das nicht erwischt hat — und das ist kein Versäumnis.** Sein
Fix sitzt bewusst in `lib.psm1`, *„weil sie die eine Stelle ist, die JEDE
Rolle durchlaeuft"*. Für die Prozessgrenze ist das genau die richtige Stelle.
Die Konsolen-Codepage lässt sich dort aber **nicht mehr** stellen: Wenn
`lib.psm1` geladen wird, steht das Fenster längst auf 850. Sie kann nur im
Wrapper oder in der Elternshell gesetzt werden — also an genau der Stelle, die
`BL-135` aus gutem Grund gemieden hat. Die dritte Hälfte fiel damit zwischen
zwei richtige Entscheidungen.

## Warum das jede Installation trifft

Betroffen ist jede Windows-Installation mit einer nicht-englischen
OEM-Codepage (850 in Westeuropa, 852, 866 …), sobald sie über die `.cmd`-Bahn
startet — der dokumentierte Weg.

**Und der Schaden ist nicht nur Kosmetik.** Der Abschlussbericht ist die
Stelle, an der das Kit dem Menschen sagt, was zu tun ist; bei rotem Gate steht
dort die Handlungsanweisung. Eine Meldung, die wie Zeichensalat aussieht, wird
überflogen — dasselbe Argument, mit dem `BL-256` die Gate-Meldung überhaupt
eingeführt hat. Rahmen, Umlaute, Geviertstriche und die Statussymbole sind
genau die Zeichen, die betroffen sind.

## Was ich schon versucht habe

- **Nachgemessen, dass die Dateien sauber sind** (Bytes oben). Der Fix gehört
  an die Anzeige, nicht an die Schreibseite — ein zweiter Eingriff an der
  Kodierung der Logs wäre die falsche Antwort und würde `BL-135` beschädigen.
- **Zwei Umgehungen im Feld, beide wirken:** einmalig `chcp 65001` in der
  cmd-Sitzung vor dem Aufruf, oder die `.ps1` direkt aus pwsh starten und
  `cmd.exe` ganz umgehen. Letzteres geht nur, wenn `pwsh` im PATH steht — der
  Wrapper existiert ja gerade wegen der Auflösung aus `BL-123`.
- **Kein lokaler Fix.** Er läge in einem Entrypoint und wäre beim nächsten
  `--update` weg (`BL-42`/`BL-58`).

**Zum Fix eine Einschränkung, die dazugehört:** Ein blankes `chcp 65001` im
Wrapper wirkt auf die ganze Konsole und überlebt `setlocal` — der Anwender
behält nach dem Lauf eine umgestellte Shell. Sauberer wäre, die alte Codepage
zu merken und am Ende zurückzusetzen, und die Umstellung nur dann, wenn
überhaupt eine Konsole am Prozess hängt (umgeleitete Ausgabe braucht sie
nicht). Beides ist im Wrapper machbar, aber es ist mehr als eine Zeile — was
vermutlich der Grund ist, warum es bisher niemand nebenbei erledigt hat.

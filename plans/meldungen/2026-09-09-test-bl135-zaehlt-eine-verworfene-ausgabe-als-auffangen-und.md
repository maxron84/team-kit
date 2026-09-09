# test_bl135 zaehlt eine verworfene Ausgabe als Auffangen und faerbt die Suite rot

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (dreizehn Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 550 Tests.

## Was passiert ist

`.\team-test.cmd` ist rot, an genau einer Stelle:

```
FAILED team/tests/test_bl135_kodierung_an_der_prozessgrenze.py::test_wer_prozessausgabe_auffaengt_liest_sie_als_utf8
AssertionError: Diese Dateien fangen Prozessausgabe auf, ohne sie als UTF-8 zu
lesen, und importieren auch lib.psm1 nicht. […]
    scripts/<projekteigenes-skript>.ps1
1 failed, 476 passed, 838 skipped
```

Die gemeldete Datei ist ein **projekteigenes** Hilfsskript. Es enthält genau
eine Stelle, auf die `_FAENGT_AUF` passt:

```powershell
& $python team/tools/beutebuch.py first 'an Axel übergeben' *> $null
$axelFallDa = ($LASTEXITCODE -eq 0)
```

**Die Ausgabe wird nach `$null` geworfen.** Ausgewertet wird ausschließlich
`$LASTEXITCODE`. Es gibt keinen Vergleich, kein Muster, keinen Text — nichts,
was falsch dekodiert werden könnte.

## Was ich nachgemessen habe, bevor ich das melde

Drei Proben, alle drei negativ — es gibt keinen Schaden hinter dem roten Test:

| Probe | Ergebnis |
|---|---|
| Kommt das Argument mit Umlaut beim Kindprozess an? `chcp 850`, dann `& python -c "print(repr(sys.argv[1]))" 'an Axel übergeben'` | **ja, unversehrt** — PowerShell 7 reicht native Argumente als UTF-16 weiter |
| Dasselbe mit gesetztem `[Console]::OutputEncoding` | identisch |
| Druckt das Skript seine eigenen Umlaute und Geviertstriche richtig, `chcp 850`, ohne die Einstellung? | **ja** |

Die aufgefangene Hälfte kann nicht kippen, weil sie verworfen wird; die
Argument-Hälfte kippt nicht, weil PowerShell 7 sie gar nicht über eine
Codepage schickt.

## Wo es steckt

`team/tests/test_bl135_kodierung_an_der_prozessgrenze.py`, im Ausdruck

```python
_FAENGT_AUF = re.compile(r"^\s*\$\w+\s*=\s*&\s|\*>\s*\$|2>&1")
```

Der mittlere Zweig `\*>\s*\$` trifft **jede** Umlenkung in eine Variable —
und damit auch `*> $null`, das die Ausgabe gerade **wegwirft**. Der
Docstring des Tests beschreibt den echten Fund präzise (*„faengt einen
kompletten Vollautomatik-Lauf auf und vergleicht ihn mit Mustern"*); der
Ausdruck darunter ist weiter.

## Warum das jede Installation trifft

`*> $null` ist die idiomatische Art, in PowerShell einen Befehl nur wegen
seines Exit-Codes aufzurufen. Jedes Projekt, das ein eigenes Skript neben die
Entrypoints legt und darin einmal `*> $null` schreibt, bekommt eine **rote
Team-Suite ohne Defekt dahinter** — und die zwei Auswege sind beide schlecht:

- Die Prüfung dauerhaft rot lassen. Dann ist `team-test` als Gate wertlos,
  weil niemand mehr hinsieht.
- `Import-Module lib.psm1` einbauen, damit es grün wird. Das ist genau die
  Krücke, vor der `CLAUDE.md` warnt (*„Wer eine Krücke in die Verifikation
  einbaut, damit sie grün wird, hat die Verifikation abgeschafft"*) — und sie
  zieht in ein schmales Hilfsskript die volle Konfigurationsmechanik.

Das Feldprojekt hat sich für **keinen** von beiden entschieden und wartet auf
diese Meldung.

## Was ich vorschlage

**`*> $null` (und `2>&1 | Out-Null`) aus `_FAENGT_AUF` herausnehmen.** Wer
verwirft, vergleicht nicht. Zwei Zweige bleiben und decken den ursprünglichen
Fund weiterhin ab: die Zuweisung an eine Variable und die Umlenkung in eine
Datei, die danach gelesen wird.

**Die Bauform als solche ist bekannt und hat im meldenden Projekt gerade eine
eigene Regel bekommen:** eine Prüfung, die das gesuchte Phänomen nicht von
einer harmlosen Ursache trennen kann (dort **Trennschärfe**-Achse genannt).
Hier trennt der Ausdruck „fängt auf **und** liest" nicht von „fängt auf und
**wirft weg**". Falls das Kit die Prüfung streng halten will, wäre die
schärfere Fassung: melden, wenn die aufgefangene Variable danach **gelesen**
wird — das ist teurer zu implementieren, aber es ist die Aussage, die der
Docstring ohnehin schon macht.

## Was ich schon versucht habe

Nichts gepatcht — weder am Kit noch am eigenen Skript. Die drei Proben oben
sind der ganze Aufwand; sie haben zusammen unter einer Minute gekostet und die
Frage entschieden.

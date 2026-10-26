# smoke_warten.py start scheitert unter Windows an einem relativen Interpreterpfad mit Schraegstrichen - cmd.exe meldet ein falsches ROT

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-26-smoke-warten-py-start-scheitert-unter-windows-an-einem-relat.md
      .\kit-melden.cmd ablegen  2026-10-26-smoke-warten-py-start-scheitert-unter-windows-an-einem-relat.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-26-smoke-warten-py-start-scheitert-unter-windows-an-einem-relat.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python-Projekt mit venv. Die volle Suite
  läuft 7 bis 17 Minuten, also über der Höchstfrist des Werkzeugs. `TEAM_SMOKE_TEST` ist
  `.venv/Scripts/python.exe -m pytest -q -n auto --dist loadgroup`. Gefunden beim Umstieg auf
  den Zwei-Schritt-Weg nach dem Update vom 2026-10-26.

## Was passiert ist

Den Umstieg auf `smoke_warten.py` (`BL-273`) haben wir erst nach einem Probelauf freigegeben. Der
Probelauf scheiterte sofort. Der Befehl ist genau der, den der Nachsatz jeder Rolle vorgibt, nur
mit `--version` statt der Suite:

    python team/tools/smoke_warten.py start --befehl ".venv/Scripts/python.exe -m pytest --version"
    python team/tools/smoke_warten.py warten <kennung>

`warten` endete mit Exit 1, „Fertig: Exit 1 (ROT)". Im Log stand:

    '.venv' is not recognized as an internal or external command,
    operable program or batch file.

Gegenprobe mit drei Schreibweisen, sonst gleich:

| `--befehl` | Exit |
|---|---|
| `.venv/Scripts/python.exe -m pytest --version` | 1, Meldung oben |
| `".venv/Scripts/python.exe" -m pytest --version` | 0 |
| `.venv\Scripts\python.exe -m pytest --version` | 0 |

## Wo es steckt

`geteilt/tools/smoke_warten.py`, `_lauf()`: `subprocess.run(befehl, shell=True)`. Unter Windows
heißt das `cmd.exe /c`. cmd.exe liest den Schrägstrich im ungequoteten Programmnamen als
Schalter: `.venv` ist das Programm, `/Scripts/python.exe` der Rest. In Git-Bash und PowerShell
läuft derselbe Befehl, deshalb fällt es nirgends sonst auf. Die Kit-Tests fahren
`sys.executable`, einen absoluten Pfad mit Backslashes in Anführungszeichen. Den Fall decken sie
nicht ab.

## Warum das jede Installation trifft

Ein venv-Interpreter mit relativem Pfad und Schrägstrichen ist unter Windows die naheliegende Form
für `TEAM_SMOKE_TEST`: Sie läuft auf beiden Bahnen. Der Nachsatz in `lib.psm1`/`lib.sh` gibt jeder
Rolle genau diesen Befehl hinter `--befehl` mit. Wer ihm folgt, bekommt ein ROT, ohne dass ein
einziger Test gelaufen ist. Damit schickt der Weg, der den vierten Ausgang verhindern soll, die
Rolle in den Produktivcode. Das ist dieselbe Fehlerklasse wie `BL-320`, nur am anderen Ende.

## Was ich schon versucht habe

Am Kit nichts. Das Projekt bleibt bis zum Fix bei seiner eigenen Warteschleife, der Umstieg ist
entschieden und wartet.

Vorschlag: Unter Windows den ersten Token vor dem Start normalisieren, als Pfad mit Backslashes
oder in Anführungszeichen. `umgebung` zerlegt den Befehl ohnehin schon (`_teile`). Dazu ein
Testfall in der Feldform, mit relativem Pfad, Schrägstrichen und ohne Anführungszeichen. Sonst
nennt die Doku die Einschränkung, und `start` warnt, bevor es losläuft.

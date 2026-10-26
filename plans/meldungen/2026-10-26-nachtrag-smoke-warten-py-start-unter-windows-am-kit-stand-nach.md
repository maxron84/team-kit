# Nachtrag: smoke_warten.py start unter Windows am Kit-Stand nachgestellt - der relative Interpreterpfad mit Schraegstrichen meldet ROT

- **Bezug**: Meldung vom 2026-10-26 (`2026-10-26-smoke-warten-py-start-scheitert-unter-windows-an-einem-relat.md`), BL-273
- **Art**: Nachtrag (Bestätigung am Kit-Stand)
- **Kit-Version**: 2.13.1 (Quellstand `530e942`)
- **Bahn**: beide (das Werkzeug ist geteilt); geprüft unter Windows
- **Plattform**: win32
- **Feldkürzel**: — (kein Feldprojekt)
- **Lage des Projekts**: kein Projekt — `geteilt/tools/smoke_warten.py` direkt aus dem Kit-Repo, in einem leeren Ordner mit frischem venv, auf der Windows-11-Maschine mit Python 3.12

## Was passiert ist

Dies ist ein Nachtrag zur Meldung aus `Feld B` vom selben Tag. Sie ist auf der Linux-Maschine
nicht nachstellbar, weil es dort kein `cmd.exe` gibt. Hier ist sie mit dem Werkzeug des Kits
nachgestellt, nicht mit der installierten Fassung des Feldprojekts:

    smoke_warten.py start --befehl "<befehl>"
    smoke_warten.py warten <kennung>

| `--befehl` | `warten` |
|---|---|
| `.venv/Scripts/python.exe --version` | Exit 1, „Fertig: Exit 1 (ROT)“, im Log: `'.venv' is not recognized as an internal or external command` |
| `".venv/Scripts/python.exe" --version` | Exit 0, „Python 3.12.10“ |
| `.venv\Scripts\python.exe --version` | Exit 0, „Python 3.12.10“ |

Das deckt sich Zeile für Zeile mit der Tabelle der Meldung. Die Ursache steht dort: `_lauf()` ruft
`subprocess.run(befehl, shell=True)`, und `cmd.exe` liest den Schrägstrich im ungequoteten
Programmnamen als Schalter.

## Was ich schon versucht habe

Nur nachgestellt, am Kit nichts geändert. Gebaut wird auf der Linux-Maschine. Dem Vorschlag der
Meldung ist nichts hinzuzufügen.

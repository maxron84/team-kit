#!/usr/bin/env python3
"""BL-24: Der chirurgische Guard-Rollback konnte keine Verzeichnisse entfernen
— und meldete trotzdem Vollzug.

`team_guard_verify` entfernte neu entstandene Pfade mit `rm -f` (ohne `-r`).
`git status --porcelain` meldet ein untracked Verzeichnis, in dem nichts
getrackt ist, als EINEN Eintrag mit Schraegstrich (`raw/`), nicht als Liste
seiner Dateien. `rm -f` scheiterte daran mit "Is a directory", die Schleife lief
weiter, und die Meldung "chirurgischer Rollback" stand elf Zeilen vorher bereits
auf dem Schirm.

Im Feld an einem Harry-Sweep beobachtet (`raw/`, ein manueller Input-Ordner) —
dort ein Gluecksfall, weil die Dateien erhalten bleiben sollten. Legt eine Rolle
aber selbst ein Verzeichnis an (Wegwerf-Skripte, `__pycache__` unter einem neuen
Pfad), bleibt es samt Inhalt liegen, waehrend der Lauf Vollzug protokolliert.

Bauart BL-15/BL-17 ("Pfad existiert, wird aber nie wirklich ausgefuehrt") in der
Variante "Meldung existiert, deckt aber die Ausfuehrung nicht".
"""
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEAM_LIB = REPO_ROOT / "team" / "lib.sh"


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "team").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "plans").mkdir()
    (TEAM_LIB).read_text(encoding="utf-8")
    (repo / "team" / "lib.sh").write_text(
        TEAM_LIB.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "team.config.sh").write_text(
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n'
        'TEAM_PRODUKTIVCODE="src/"\nTEAM_TEST_ORDNER="tests/"\n'
        'TEAM_PLAN_ORDNER="plans/"\n'
        'TEAM_KOSTEN_TOOL="python3 team/tools/kosten.py"\n'
        'TEAM_BEUTEBUCH_TOOL="python3 team/tools/beutebuch.py"\n',
        encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo


def _guard(repo, skript):
    """Faehrt eine Guard-Runde: Schnappschuss, dann <skript> als 'Rolle',
    dann team_guard_verify mit der Whitelist der Read-Only-Rollen."""
    return subprocess.run(
        ["bash", "-c",
         'set -e; source ./team/lib.sh; team_guard_begin; '
         + skript
         + '; team_guard_verify marv "^(tests/|plans/)" && echo GUARD_OK'],
        cwd=repo, capture_output=True, text=True)


def test_neu_angelegtes_verzeichnis_wird_wirklich_entfernt(tmp_path):
    """Der Fund selbst: Die Rolle legt ein Verzeichnis ausserhalb ihrer
    Whitelist an."""
    repo = _repo(tmp_path)
    ergebnis = _guard(repo, 'mkdir -p raw/unter && echo daten > raw/unter/a.txt')
    assert "GUARD_OK" not in ergebnis.stdout, "der Uebergriff muss gemeldet werden"
    assert not (repo / "raw").exists(), \
        "das Verzeichnis liegt nach dem 'chirurgischen Rollback' immer noch da"


def test_vollzug_wird_erst_nach_dem_aufraeumen_gemeldet(tmp_path):
    repo = _repo(tmp_path)
    ergebnis = _guard(repo, 'mkdir -p raw && echo daten > raw/a.txt')
    assert "chirurgischer Rollback vollzogen" in ergebnis.stderr
    assert "ROLLBACK UNVOLLSTÄNDIG" not in ergebnis.stderr


def test_einzelne_datei_wird_weiterhin_entfernt(tmp_path):
    """Gegenprobe: Der bisherige Fall darf nicht kaputtgehen."""
    repo = _repo(tmp_path)
    _guard(repo, 'echo boese > src/neu.py')
    assert not (repo / "src" / "neu.py").exists()


def test_geaenderte_bestandsdatei_wird_zurueckgeholt(tmp_path):
    """Zweite Gegenprobe: getrackte Dateien laufen ueber git checkout, nicht
    ueber rm — `-r` darf daran nichts aendern."""
    repo = _repo(tmp_path)
    _guard(repo, 'echo "x = 999" > src/app.py')
    assert (repo / "src" / "app.py").read_text() == "x = 1\n"


def test_whitelist_pfade_bleiben_unangetastet(tmp_path):
    repo = _repo(tmp_path)
    ergebnis = _guard(repo, 'mkdir -p tests/neu && echo t > tests/neu/test_x.py')
    assert "GUARD_OK" in ergebnis.stdout
    assert (repo / "tests" / "neu" / "test_x.py").exists()

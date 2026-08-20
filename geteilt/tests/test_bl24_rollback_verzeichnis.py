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

from conftest import Ordner, Ruf, RufMarke, Schreib, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]
TEAM_LIB = kit_pfad("lib.sh")

WHITELIST = "^(tests/|plans/)"


def _repo(tmp_path, schale):
    repo = tmp_path / "repo"
    (repo / "team").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "plans").mkdir()
    schale.lib_kopieren(repo)
    schale.config_schreiben(repo, {
        "TEAM_DOMAENEN": "produkt",
        "TEAM_PRODUKTIVCODE": "src/",
        "TEAM_TEST_ORDNER": "tests/",
        "TEAM_PLAN_ORDNER": "plans/",
        "TEAM_KOSTEN_TOOL": "python3 team/tools/kosten.py",
        "TEAM_BEUTEBUCH_TOOL": "python3 team/tools/beutebuch.py",
    })
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo


def _guard(schale, repo, mutation):
    """Faehrt eine Guard-Runde: Schnappschuss, dann <mutation> als 'Rolle',
    dann team_guard_verify mit der Whitelist der Read-Only-Rollen.

    Die Mutation MUSS ein Schritt in derselben Shell sein und darf nicht aus
    Python vorweggenommen werden: team_guard_begin legt den Schnappschuss in
    einer Shell-Variablen ab. Ein verify in einem zweiten Prozess saehe einen
    leeren Schnappschuss und spraeche die Rolle frei — gruen und wertlos.
    """
    return schale.lauf(
        [Ruf("team_guard_begin"), *mutation,
         RufMarke("team_guard_verify", "marv", WHITELIST, marke="GUARD_OK")],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)


def test_neu_angelegtes_verzeichnis_wird_wirklich_entfernt(tmp_path, schale):
    """Der Fund selbst: Die Rolle legt ein Verzeichnis ausserhalb ihrer
    Whitelist an."""
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Ordner("raw/unter"),
                                     Schreib("raw/unter/a.txt", "daten\n")])
    assert "GUARD_OK" not in ergebnis.stdout, "der Uebergriff muss gemeldet werden"
    assert not (repo / "raw").exists(), \
        "das Verzeichnis liegt nach dem 'chirurgischen Rollback' immer noch da"


def test_vollzug_wird_erst_nach_dem_aufraeumen_gemeldet(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Schreib("raw/a.txt", "daten\n")])
    assert "chirurgischer Rollback vollzogen" in ergebnis.stderr
    assert "ROLLBACK UNVOLLSTÄNDIG" not in ergebnis.stderr


def test_einzelne_datei_wird_weiterhin_entfernt(tmp_path, schale):
    """Gegenprobe: Der bisherige Fall darf nicht kaputtgehen."""
    repo = _repo(tmp_path, schale)
    _guard(schale, repo, [Schreib("src/neu.py", "boese\n")])
    assert not (repo / "src" / "neu.py").exists()


def test_geaenderte_bestandsdatei_wird_zurueckgeholt(tmp_path, schale):
    """Zweite Gegenprobe: getrackte Dateien laufen ueber git checkout, nicht
    ueber rm — `-r` darf daran nichts aendern."""
    repo = _repo(tmp_path, schale)
    _guard(schale, repo, [Schreib("src/app.py", "x = 999\n")])
    assert (repo / "src" / "app.py").read_text() == "x = 1\n"


def test_whitelist_pfade_bleiben_unangetastet(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Schreib("tests/neu/test_x.py", "t\n")])
    assert "GUARD_OK" in ergebnis.stdout
    assert (repo / "tests" / "neu" / "test_x.py").exists()

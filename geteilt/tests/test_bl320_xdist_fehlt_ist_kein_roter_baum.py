#!/usr/bin/env python3
"""BL-320: Die Selbstpruefung des vierten Ausgangs hielt eine fehlende
pytest-xdist-Installation fuer einen roten Baum.

WAS GEMELDET WURDE (`Feld B`, 2026-10-08)
    `TEAM_SMOKE_TEST` traegt `-n auto --dist loadgroup`. Fehlt pytest-xdist im
    Interpreter des Befehls, bricht pytest schon am Kommandozeilenparser ab
    (`unrecognized arguments: -n`). `team_quittung_selbstpruefung` meldete
    *„ROT, auch der zweite Lauf war rot — kein Flackern"* und schickte den
    Menschen auf Fehlersuche im Produktivcode, obwohl nur ein Paket fehlte.
    Das Feld hat die Pruefung dreimal lokal nachgetragen — und jedes Update hat
    sie wieder entfernt: Sie gehoert an den zentralen Aufrufer.

WAS DABEI GEMESSEN WURDE UND DIE BAUFORM BESTIMMT
    `pytest -n 0 --version` endet auch OHNE xdist mit 0 — die Versionsabfrage
    kommt vor dem Parser, an dem der Feldfall scheitert. Geprueft wird deshalb
    im Interpreter des Befehls (`find_spec('xdist')`), wie die Meldung es
    vorschlaegt, und zwar im geteilten Werkzeug `smoke_warten.py umgebung`,
    damit beide Bahnen dieselbe Pruefung fahren.

DETERMINISTISCH AUF JEDEM WIRT
    Ob xdist auf dem Wirt liegt, entscheidet dieser Test nicht selbst: Ein
    Interpreter mit `-S` sieht keine site-packages — dort FEHLT xdist sicher;
    ein Ordner mit einem Platzhalter-Paket `xdist` im PYTHONPATH laesst es
    sicher DA sein.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import Ruf, Schreib, kit_pfad  # noqa: E402
import test_bl207_vordergrund_zeitlimit_und_paralleler_lauf as h  # noqa: E402

SMOKE_WARTEN = kit_pfad("tools", "smoke_warten.py")
PY = f'"{sys.executable}"'


def _werkzeug():
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    spec = importlib.util.spec_from_file_location("smoke_warten_bl320",
                                                  SMOKE_WARTEN)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _umgebung(befehl, env=None):
    return subprocess.run([sys.executable, str(SMOKE_WARTEN), "umgebung",
                           "--befehl", befehl], capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=env, timeout=120)


# --- Das Werkzeug ------------------------------------------------------------

def test_ohne_xdist_meldet_das_werkzeug_einen_befund():
    """Der Feldfall: xdist-Optionen, aber kein xdist im Interpreter."""
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    r = _umgebung(f"{PY} -S -m pytest tests -q -n auto --dist loadgroup")
    assert r.returncode == 3, r.stdout + r.stderr
    assert "pytest-xdist" in r.stdout and "UMGEBUNG" in r.stdout, r.stdout
    assert "Kit-BL-320" in r.stdout


def test_mit_xdist_schweigt_es(tmp_path):
    """Gegenrichtung: Liegt xdist im Interpreter, ist nichts zu melden."""
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    (tmp_path / "xdist").mkdir()
    (tmp_path / "xdist" / "__init__.py").write_text("", encoding="utf-8")
    env = dict(os.environ, PYTHONPATH=str(tmp_path))
    r = _umgebung(f"{PY} -m pytest tests -q -n auto", env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == ""


@pytest.mark.parametrize("befehl", [
    f"{PY} -S -m pytest tests -q",          # keine xdist-Option
    "./run-tests.sh -n 3",                  # kein pytest erkennbar
    "unbekannter-starter pytest -n 2",      # Interpreter nicht startbar
    "",
])
def test_ohne_eindeutigen_befund_wird_nichts_behauptet(befehl):
    """Im Zweifel nichts behaupten — eine Pruefung, die falsch Alarm schlaegt,
    schickt den Menschen genauso in die Irre wie die, die sie ersetzt."""
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    r = _umgebung(befehl)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip() == ""


@pytest.mark.parametrize("wort,xdist", [
    ("-n", True), ("-nauto", True), ("-n4", True), ("--dist", True),
    ("--dist=loadgroup", True), ("--numprocesses=4", True),
    ("-x", False), ("--durations=30", False), ("-q", False),
])
def test_welche_optionen_xdist_brauchen(wort, xdist):
    assert bool(_werkzeug().XDIST_OPTION.match(wort)) is xdist


@pytest.mark.parametrize("befehl,interpreter", [
    ("python -m pytest -n auto", ["python"]),
    ("py -3.12 -m pytest -n 2", ["py", "-3.12"]),
    ("uv run pytest -n 2", ["uv", "run", "python"]),
    ("poetry run pytest -n 2", ["poetry", "run", "python"]),
    ("./run-tests.sh -n 3", None),
])
def test_der_interpreter_wird_aus_dem_befehl_gelesen(befehl, interpreter):
    w = _werkzeug()
    assert w._interpreter(w._teile(befehl)) == interpreter


# --- Die Selbstpruefung, beide Bahnen ----------------------------------------

def _projekt_mit_werkzeug(tmp_path, schale, smoke):
    repo = h._projekt(tmp_path, schale)
    (repo / "team" / "tools").mkdir()
    shutil.copy(SMOKE_WARTEN, repo / "team" / "tools" / "smoke_warten.py")
    return repo, smoke


def _pruefung(repo, schale, smoke):
    return schale.lauf(
        [Schreib("src/modul.py", "y = 2\n"),
         Schreib("tests/test_stufe1_sache.py", "def test_x(): pass\n"),
         Ruf("team_quittung_selbstpruefung", "ralph", "1")],
        cwd=repo, lib=repo / "team" / schale.lib_name,
        env={"TEAM_SMOKE_TEST": smoke, "TEAM_TEST_ORDNER": "tests/",
             "TEAM_SELBSTPRUEFUNG_WARTEN": "0"})


def test_die_selbstpruefung_nennt_die_umgebung_statt_rot(tmp_path, schale):
    """Der Feldfall am lebenden Objekt. Gegen den alten Stand gemessen: 'ist
    ROT … kein Flackern' samt BL-61-Rat, den Testaufbau zu verdaechtigen."""
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    repo, smoke = _projekt_mit_werkzeug(
        tmp_path, schale, f"{PY} -S -m pytest tests -q -n auto")
    r = _pruefung(repo, schale, smoke)
    assert r.returncode != 0, "ungeprueft darf nicht quittiert werden"
    assert "pytest-xdist" in r.stderr and "Kit-BL-320" in r.stderr, r.stderr
    assert "ist ROT" not in r.stderr and "BL-61" not in r.stderr, (
        "Die Selbstpruefung behauptet weiter einen roten Baum und schickt den "
        f"Menschen in den Produktivcode.\n{r.stderr}")
    assert "ungeprüft" in r.stderr, r.stderr


def test_der_schnelle_stufenbefehl_wird_geprueft(tmp_path, schale):
    """Seit BL-232 laeuft in der Selbstpruefung TEAM_SMOKE_TEST_SCHNELL —
    geprueft wird der Befehl, der dort wirklich laeuft."""
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    repo, _ = _projekt_mit_werkzeug(tmp_path, schale, "")
    r = schale.lauf(
        [Schreib("src/modul.py", "y = 2\n"),
         Schreib("tests/test_stufe1_sache.py", "def test_x(): pass\n"),
         Ruf("team_quittung_selbstpruefung", "ralph", "1")],
        cwd=repo, lib=repo / "team" / schale.lib_name,
        env={"TEAM_SMOKE_TEST": h._smoke_befehl(schale),
             "TEAM_SMOKE_TEST_SCHNELL": f"{PY} -S -m pytest tests -x -n 2",
             "TEAM_TEST_ORDNER": "tests/", "TEAM_SELBSTPRUEFUNG_WARTEN": "0"})
    assert r.returncode != 0
    assert "Kit-BL-320" in r.stderr, r.stderr


def test_ohne_befund_wird_weiter_gemessen_und_quittiert(tmp_path, schale):
    """Gegenrichtung: Ein Smoke-Test ohne xdist-Optionen laeuft wie bisher —
    die neue Pruefung darf die Automatik aus BL-110 nicht abschalten."""
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    repo, _ = _projekt_mit_werkzeug(tmp_path, schale, "")
    r = _pruefung(repo, schale, h._smoke_befehl(schale))
    assert r.returncode == 0, r.stderr
    assert "Alle drei Prüfungen bestanden" in r.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

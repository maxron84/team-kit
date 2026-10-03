#!/usr/bin/env python3
"""BL-232, BL-273, BL-281: Die Verifikation waechst mit der Suite mit.

BL-232 (`Feld B`, 2026-09-05)
    Virenschutz, Suite-Laufzeit und der vierte Ausgang sind EINE Kette: Der
    Loop faehrt den Verifikationsbefehl bis zu zweimal je Stufe (Rolle, dann
    Selbstpruefung), ein rotes Ergebnis war oft Last statt Code (16 rote
    Faelle, allein gefahren gruen), und der Riss der Frist kam ohne Warnung.
    Gebaut: (1) die zweite Messung wird benannt und gemessen, (2) ein
    schneller Stufen-Befehl `TEAM_SMOKE_TEST_SCHNELL` mit verbindlicher
    voller Suite am Phasenende, (3) ein roter Lauf wird einmal wiederholt —
    gruen heisst „flackernd", nicht quittiert, (4) Fruehwarnung ab 75 % der
    Frist.

BL-273 / BL-281 (`Feld B`, 2026-09-17 und 2026-09-22)
    Die Werkzeugfrist ist eine OBERGRENZE; darueber schiebt das Werkzeug den
    Befehl selbst in den Hintergrund. Der Ausweg wird mitgeliefert
    (`team/tools/smoke_warten.py`): nur der Testlauf im Hintergrund, der
    Warteruf im Vordergrund — und wer auf den Warteruf wartet, macht
    denselben Fehler eine Ebene hoeher.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

import test_bl207_vordergrund_zeitlimit_und_paralleler_lauf as h
import test_bl241_fixphase_hat_einen_eigenen_einstieg as v
from conftest import Schreib, Variable, kit_pfad, verlange_bash, verlange_pwsh

SMOKE_WARTEN = kit_pfad("tools", "smoke_warten.py")


# --- smoke_warten.py ----------------------------------------------------------

def _werkzeug(tmp_path, *argv):
    return subprocess.run([sys.executable, str(SMOKE_WARTEN), *argv],
                          cwd=tmp_path, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)


def test_warten_meldet_laeuft_noch_dann_den_exitcode(tmp_path):
    befehl = (f'"{sys.executable}" -c "import time,sys; print(\'SUITE\'); '
              f'time.sleep(3); sys.exit(4)"')
    r = _werkzeug(tmp_path, "start", "--befehl", befehl)
    assert r.returncode == 0, r.stderr
    zwischen = _werkzeug(tmp_path, "warten", "--max", "0.5")
    assert zwischen.returncode == 75, zwischen.stderr
    assert "nicht rot" in zwischen.stderr
    ende = _werkzeug(tmp_path, "warten", "--max", "30")
    assert ende.returncode == 4, ende.stdout + ende.stderr
    assert "SUITE" in ende.stdout


def test_warten_ohne_lauf_ist_ein_bedienfehler(tmp_path):
    r = _werkzeug(tmp_path, "warten", "--max", "1")
    assert r.returncode == 2 and "start" in r.stderr


def test_start_kehrt_sofort_zurueck(tmp_path):
    t0 = time.monotonic()
    r = _werkzeug(tmp_path, "start", "--befehl",
                  f'"{sys.executable}" -c "import time; time.sleep(20)"')
    assert r.returncode == 0
    assert time.monotonic() - t0 < 10, "start hat auf den Testlauf gewartet"


# --- Die Bausteine nennen den Weg (beide Bahnen) ----------------------------

def _bausteine(tmp_path, schale, **env):
    lib = schale.lib_kopieren(tmp_path)
    umgebung = {"TEAM_SMOKE_TEST": "./smoke.sh", "TEAM_SMOKE_TEST_TIMEOUT": "900"}
    umgebung.update(env)
    r = schale.lauf([Variable("SMOKE_ZEILE"), Variable("SMOKE_SUFFIX")],
                    cwd=tmp_path, lib=lib, env=umgebung)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_die_bausteine_liefern_den_zwei_schritt_weg(tmp_path, schale):
    text = _bausteine(tmp_path, schale)
    assert text.count("smoke_warten.py start") == 2, text
    assert text.count("smoke_warten.py warten") == 2, text
    assert "soweit es das zulässt" in text and "Kit-BL-281" in text, text


def test_der_schnelle_stufen_befehl_ersetzt_den_vollen(tmp_path, schale):
    text = _bausteine(tmp_path, schale, TEAM_SMOKE_TEST_SCHNELL="./schnell.sh")
    assert "Smoke-Test ausführen: ./schnell.sh" in text, text
    assert "Smoke-Test grün: ./schnell.sh" in text, text
    assert "Kit-BL-232" in text and "./smoke.sh" in text, text


# --- Die Selbstpruefung (beide Bahnen) ----------------------------------------

def _projekt_flackernd(tmp_path, schale):
    """Erster Lauf rot, jeder weitere gruen — die Lage aus dem Feld."""
    repo = h._projekt(tmp_path, schale)
    marke = repo / ".einmal-rot"
    if schale.ist_bash:
        (repo / "smoke.sh").write_text(
            "#!/usr/bin/env bash\n"
            "if [ ! -f .einmal-rot ]; then : > .einmal-rot; exit 1; fi\nexit 0\n",
            encoding="utf-8")
    else:
        (repo / "smoke.ps1").write_text(
            "if (-not (Test-Path .einmal-rot)) { New-Item .einmal-rot | Out-Null; exit 1 }\nexit 0\n",
            encoding="utf-8")
    h._git(repo, "add", "-A")
    h._git(repo, "commit", "-q", "-m", "flackernd")
    assert not marke.exists()
    return repo


def test_ein_flackernder_baum_wird_benannt_und_nicht_quittiert(tmp_path, schale):
    repo = _projekt_flackernd(tmp_path, schale)
    r = h._selbstpruefung(repo, schale)
    assert r.returncode != 0, r.stderr
    assert "flackernd" in r.stderr and "Kit-BL-232" in r.stderr, r.stderr
    assert "ist ROT." not in r.stderr, r.stderr


def test_die_zweite_messung_wird_benannt_und_gemessen(tmp_path, schale):
    repo = h._projekt(tmp_path, schale, smoke_rc=0)
    r = h._selbstpruefung(repo, schale)
    assert r.returncode == 0, r.stderr
    assert "zweite Messung desselben Stands" in r.stderr, r.stderr
    assert " s)." in r.stderr, "die Dauer fehlt"


def test_fruehwarnung_ab_drei_vierteln_der_frist(tmp_path, schale):
    repo = h._projekt(tmp_path, schale, smoke_rc=0, dauer=2)
    r = schale.lauf(
        [Schreib("src/modul.py", "y = 2\n"),
         Schreib("tests/test_stufe1_sache.py", "def test_x(): pass\n"),
         h.Ruf("team_quittung_selbstpruefung", "ralph", "1")],
        cwd=repo, lib=repo / "team" / schale.lib_name,
        env={"TEAM_SMOKE_TEST": h._smoke_befehl(schale),
             "TEAM_TEST_ORDNER": "tests/", "TEAM_SMOKE_TEST_TIMEOUT": "2"})
    assert r.returncode == 0, r.stderr
    assert "75 %" in r.stderr and "Kit-BL-232" in r.stderr, r.stderr


# --- Die volle Suite am Phasenende ---------------------------------------------

def _suite_rot(repo, bahn):
    if bahn == "bash":
        (repo / "voll.sh").write_text("#!/usr/bin/env bash\necho voll\nexit 1\n",
                                      encoding="utf-8")
        (repo / "voll.sh").chmod(0o755)
        return "./voll.sh"
    (repo / "voll.ps1").write_text("[Console]::Out.WriteLine('voll')\nexit 1\n",
                                   encoding="utf-8-sig")
    return "./voll.ps1"


def test_bash_die_volle_suite_am_phasenende_setzt_das_gate(tmp_path):
    verlange_bash()
    repo = v._bash_projekt(tmp_path)
    voll = _suite_rot(repo, "bash")
    r = v._bash(repo, "vollautomatik.sh", TEAM_SMOKE_TEST=voll,
                TEAM_SMOKE_TEST_SCHNELL="true")
    aus = r.stdout + r.stderr
    assert r.returncode == 44, aus
    assert "Volle Suite ROT am Ende der Bauphase" in aus, aus
    assert "volle Suite rot" in (repo / ".team-gate-rot").read_text(encoding="utf-8")


def test_pwsh_die_volle_suite_am_phasenende_setzt_das_gate(tmp_path):
    verlange_pwsh()
    repo = v._pwsh_projekt(tmp_path)
    voll = _suite_rot(repo, "pwsh")
    r = v._pwsh(repo, "vollautomatik.ps1", TEAM_SMOKE_TEST=voll,
                TEAM_SMOKE_TEST_SCHNELL="./voll.ps1")
    aus = r.stdout + r.stderr
    assert r.returncode == 44, aus
    assert "Volle Suite ROT am Ende der Bauphase" in aus, aus


def test_ohne_schnellen_befehl_keine_zusatzrunde(tmp_path):
    verlange_bash()
    repo = v._bash_projekt(tmp_path)
    voll = _suite_rot(repo, "bash")
    r = v._bash(repo, "vollautomatik.sh", TEAM_SMOKE_TEST=voll)
    aus = r.stdout + r.stderr
    assert "Volle Suite" not in aus, aus

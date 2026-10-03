#!/usr/bin/env python3
"""BL-241 und BL-204: Die Fix-Phase hat einen eigenen Einstieg — und
`TEAM_VOLLAUTOMATIK_AB_PHASE` haelt, was sein Name verspricht.

BL-204 (`Feld B`, 2026-08-27)
    Acht Funde ausserhalb eines Laufs: 17 Handstarts von `.\\frank.cmd`. Die
    fertige Automatik (Rundendeckel, Axel nur bei Bedarf, Auslauf-Bremse,
    Budget je Runde) war nur als Innenteil der Vollautomatik erreichbar — und
    deren Abbruchbericht riet woertlich zur Handkurbel.

BL-241 (`Feld B`, 2026-09-08)
    Wer nur fixen wollte, zahlte zwei Sweeps oder fuhr Frank ohne Axel. Und
    `TEAM_VOLLAUTOMATIK_AB_PHASE=4` wurde STILL ignoriert — der Code pruefte
    nur auf `1`; der naheliegende Griff fuehrte lautlos zum teuersten
    Ergebnis.

GEPRUEFT AM LAUF (Stub-Rollen, beide Bahnen)
    `fixphase` startet weder Ralph noch das Red Team, faehrt Frank und Axel
    und endet mit dem Abschlussbericht; ein unbekannter Phasenwert startet
    nichts.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import test_bl217_phasen_zeiger as h
from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      verlange_pwsh, werkzeug_wert)

ROLLEN = ("ralph", "harry", "marv", "frank", "axel", "team-status")


# --- bash ---------------------------------------------------------------------

def _bash_projekt(tmp_path):
    repo = h._projekt(tmp_path)
    shutil.copy(entrypoint_pfad("fixphase.sh"), repo / "fixphase.sh")
    return repo


def _bash(repo, skript, **env):
    return subprocess.run([BASH, f"./{skript}"], cwd=repo, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=dict(os.environ, TEAM_BUDGET_USD="99", **env))


def test_bash_fixphase_faehrt_nur_die_fixphase(tmp_path):
    verlange_bash()
    repo = _bash_projekt(tmp_path)
    r = _bash(repo, "fixphase.sh")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    assert "STUB frank" in aus, aus
    for fremd in ("STUB ralph", "STUB harry", "STUB marv"):
        assert fremd not in aus, f"{fremd} lief in der Fix-Phase mit:\n{aus}"
    assert "auf Ansage" in aus and "ABSCHLUSSBERICHT" in aus, aus


@pytest.mark.parametrize("wert", ("4x", "0", "5", "vier"))
def test_bash_ein_unbekannter_phasenwert_startet_nichts(tmp_path, wert):
    verlange_bash()
    repo = _bash_projekt(tmp_path)
    r = _bash(repo, "vollautomatik.sh", TEAM_VOLLAUTOMATIK_AB_PHASE=wert)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "Kit-BL-241" in r.stderr, r.stderr
    assert "STUB" not in r.stdout, r.stdout


def test_bash_phase_2_ueberspringt_nur_den_bau(tmp_path):
    verlange_bash()
    repo = _bash_projekt(tmp_path)
    r = _bash(repo, "vollautomatik.sh", TEAM_VOLLAUTOMATIK_AB_PHASE="2")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    assert "STUB ralph" not in aus and "STUB harry" in aus, aus


def test_bash_fixphase_nimmt_keine_argumente(tmp_path):
    verlange_bash()
    repo = _bash_projekt(tmp_path)
    r = subprocess.run([BASH, "./fixphase.sh", "--von-vorn"], cwd=repo,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode == 2 and "--von-vorn" in r.stderr, r.stderr


# --- pwsh ---------------------------------------------------------------------

def _pwsh_projekt(tmp_path):
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"]):
        subprocess.run(["git", "-C", str(tmp_path), *befehl], check=True,
                       capture_output=True)
    (tmp_path / "team" / "tools").mkdir(parents=True)
    (tmp_path / "plans").mkdir()
    (tmp_path / ".ralph-logs").mkdir()
    (tmp_path / ".team-logs").mkdir()
    shutil.copy(kit_pfad("lib.psm1"), tmp_path / "team" / "lib.psm1")
    for werkzeug in ("kosten.py", "beutebuch.py"):
        shutil.copy(kit_pfad("tools", werkzeug),
                    tmp_path / "team" / "tools" / werkzeug)
    for name in ("vollautomatik.ps1", "fixphase.ps1"):
        shutil.copy(entrypoint_pfad(name), tmp_path / name)
    (tmp_path / "team.config.ps1").write_text(
        '$TEAM_KOSTEN_TOOL = "' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        '$TEAM_BEUTEBUCH_TOOL = "' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        '$TEAM_DOMAENEN = "produkt"\n$env:TEAM_DOMAENEN = "produkt"\n',
        encoding="utf-8-sig")
    for rolle in ROLLEN:
        code = 3 if rolle in ("harry", "marv", "frank") else 0
        (tmp_path / f"{rolle}.ps1").write_text(
            f"[Console]::Out.WriteLine('STUB {rolle}')\nexit {code}\n",
            encoding="utf-8-sig")
    (tmp_path / ".ralph-plan").write_text("plans/ralph-kaskade-1-produkt.md\n",
                                          encoding="utf-8")
    (tmp_path / ".ralph-state").write_text("5\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "init"],
                   check=True, capture_output=True)
    return tmp_path


def _pwsh(repo, skript, *args, **env):
    umgebung = dict(os.environ, TEAM_BUDGET_USD="99", **env)
    if "TEAM_VOLLAUTOMATIK_AB_PHASE" not in env:
        umgebung.pop("TEAM_VOLLAUTOMATIK_AB_PHASE", None)
    return subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File",
                           f"./{skript}", *args], cwd=repo, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=umgebung, timeout=300)


def test_pwsh_fixphase_faehrt_nur_die_fixphase(tmp_path):
    verlange_pwsh()
    repo = _pwsh_projekt(tmp_path)
    r = _pwsh(repo, "fixphase.ps1")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    assert "STUB frank" in aus, aus
    for fremd in ("STUB ralph", "STUB harry", "STUB marv"):
        assert fremd not in aus, f"{fremd} lief in der Fix-Phase mit:\n{aus}"
    assert "auf Ansage" in aus and "ABSCHLUSSBERICHT" in aus, aus


def test_pwsh_ein_unbekannter_phasenwert_startet_nichts(tmp_path):
    verlange_pwsh()
    repo = _pwsh_projekt(tmp_path)
    r = _pwsh(repo, "vollautomatik.ps1", TEAM_VOLLAUTOMATIK_AB_PHASE="4x")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "Kit-BL-241" in r.stderr, r.stderr
    assert "STUB" not in r.stdout, r.stdout


def test_der_abbruchbericht_nennt_den_einstieg():
    """BL-204: Der Bericht riet zur Handkurbel, zwanzig Zeilen unter der
    Schleife, die dasselbe selbststaendig faehrt."""
    for datei, einstieg in (("vollautomatik.sh", "./fixphase.sh"),
                            ("vollautomatik.ps1", ".\\fixphase.cmd")):
        pfad = Path(entrypoint_pfad(datei))
        if not pfad.is_file():
            continue
        text = pfad.read_text(encoding="utf-8-sig")
        assert f"Fixphase fortsetzen:  {einstieg}" in text, datei


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))

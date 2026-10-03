#!/usr/bin/env python3
"""BL-233 (2): `--update` meldet Laufzeitdateien, die schon im Git-Index
liegen — fuer sie greift die `.gitignore` nicht.

DER FELDBEFUND (`Feld B`, 2026-09-05)
    `.vollautomatik-state` stand nicht in der Vorlage. Ab dem ersten
    Phasenwechsel war der Baum dreckig, und der Guard forderte bei JEDEM
    Rollenstart „bitte committen" — die Warnung verlor ihren Wert, und eine
    echte Fremdaenderung ging daneben unter. Die Vorlage und der Guard sind
    seit `BL-269` nachgezogen; eine reine Vorlagenaenderung erreicht ein
    Bestandsprojekt aber nicht, wenn die Datei dort schon GETRACKT ist.

DIE PROBE
    Eine frische Installation, in der `.vollautomatik-state` mitcommittet
    wurde, und danach ein `--update`: Es muss die Datei nennen und den Befehl
    zum Austragen — ohne den Index selbst anzufassen.
"""
import subprocess
from pathlib import Path

import pytest

from conftest import BASH, verlange_bash, verlange_pwsh

REPO_ROOT = Path(__file__).resolve().parents[2]


def _git(ziel, *args):
    return subprocess.run(["git", "-C", str(ziel), *args], check=True,
                          capture_output=True, text=True, encoding="utf-8")


def _projekt(tmp_path):
    ziel = tmp_path / "projekt"
    ziel.mkdir()
    _git(ziel, "init", "-q")
    _git(ziel, "config", "user.email", "t@l")
    _git(ziel, "config", "user.name", "T")
    return ziel


def _getrackt(ziel):
    (ziel / ".vollautomatik-state").write_text("2\n-|-\n", encoding="utf-8")
    _git(ziel, "add", "-A")
    _git(ziel, "add", "-f", ".vollautomatik-state")
    _git(ziel, "commit", "-q", "-m", "eingezogen, samt Laufzeitdatei")


def test_bash_update_meldet_die_getrackte_laufzeitdatei(tmp_path):
    verlange_bash()
    installer = REPO_ROOT / "bash" / "install.sh"
    if not installer.is_file():
        pytest.skip("install.sh liegt nur im Kit")
    ziel = _projekt(tmp_path)
    erst = subprocess.run([BASH, str(installer), str(ziel), "--nicht-interaktiv",
                           "--nur-bash", "--ohne-selbsttest"], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    assert erst.returncode == 0, erst.stdout[-800:] + erst.stderr[-800:]
    _getrackt(ziel)
    r = subprocess.run([BASH, str(installer), str(ziel), "--update",
                        "--nicht-interaktiv", "--ohne-selbsttest"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    aus = r.stdout + r.stderr
    assert "Kit-BL-233" in aus and ".vollautomatik-state" in aus, aus[-2000:]
    assert "rm --cached" in aus, aus[-2000:]
    assert ".vollautomatik-state" in _git(ziel, "ls-files").stdout, (
        "--update hat den Index angefasst — es soll nur melden.")


def test_pwsh_update_meldet_die_getrackte_laufzeitdatei(tmp_path):
    verlange_pwsh()
    installer = REPO_ROOT / "pwsh" / "install.ps1"
    if not installer.is_file():
        pytest.skip("install.ps1 liegt nur im Kit")
    ziel = _projekt(tmp_path)
    erst = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File",
                           str(installer), str(ziel), "-NichtInteraktiv",
                           "-NurPwsh", "-OhneSelbsttest"], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    assert erst.returncode == 0, erst.stdout[-800:] + erst.stderr[-800:]
    _getrackt(ziel)
    r = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File",
                        str(installer), str(ziel), "-Update", "-NichtInteraktiv",
                        "-OhneSelbsttest"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    aus = r.stdout + r.stderr
    assert "Kit-BL-233" in aus and ".vollautomatik-state" in aus, aus[-2000:]


def test_ohne_getrackte_laufzeitdatei_schweigt_das_update(tmp_path):
    """Gegenrichtung: Eine Meldung, die immer kommt, ist keine (BL-14)."""
    verlange_bash()
    installer = REPO_ROOT / "bash" / "install.sh"
    if not installer.is_file():
        pytest.skip("install.sh liegt nur im Kit")
    ziel = _projekt(tmp_path)
    subprocess.run([BASH, str(installer), str(ziel), "--nicht-interaktiv",
                    "--nur-bash", "--ohne-selbsttest"], capture_output=True,
                   text=True, encoding="utf-8", errors="replace", check=True)
    _git(ziel, "add", "-A")
    _git(ziel, "commit", "-q", "-m", "eingezogen")
    r = subprocess.run([BASH, str(installer), str(ziel), "--update",
                        "--nicht-interaktiv", "--ohne-selbsttest"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert "Kit-BL-233" not in r.stdout + r.stderr

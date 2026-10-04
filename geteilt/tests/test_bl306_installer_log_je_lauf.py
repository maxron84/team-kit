#!/usr/bin/env python3
"""BL-306: Der Selbsttest des Installers schreibt sein Log je Lauf in eine
EIGENE Datei.

DER BEFUND (Kit, 2026-10-03)
    Beide Installer schrieben das Log ihres Selbsttests unter einem festen
    Namen in den Temp-Ordner (`team-init-pytest.log`). Laufen zwei
    Installationen gleichzeitig — beim Bauen die Selbsttests beider Bahnen
    nebeneinander —, schreiben sie in dieselbe Datei. Unter Windows brach die
    zweite mit "wird von einem anderen Prozess verwendet" ab, und ihr
    Selbsttest galt als nicht gefahren (BL-127): ein roter Lauf ohne Defekt.

DIE PROBE
    Am Quelltext beider Installer: kein fester Logname mehr, sondern einer je
    Lauf (`mktemp` bzw. Prozess-ID und Zeit) — seit BL-309 auch im Update,
    das seinen festen Namen behalten hatte.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _code(pfad):
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt nur im Kit")
    return "\n".join(z for z in pfad.read_text(encoding="utf-8-sig").splitlines()
                     if not z.lstrip().startswith("#"))


def test_bash_installer_nimmt_einen_eigenen_lognamen():
    code = _code(REPO_ROOT / "bash" / "install.sh")
    assert "/tmp/team-init-pytest.log" not in code, (
        "install.sh schreibt das Selbsttest-Log wieder unter festem Namen "
        "(Kit-BL-306)")
    assert re.search(r'INIT_LOG="\$\(mktemp ', code), code[-200:]


def test_pwsh_installer_nimmt_einen_eigenen_lognamen():
    code = _code(REPO_ROOT / "pwsh" / "install.ps1")
    assert "'team-init-pytest.log'" not in code, (
        "install.ps1 schreibt das Selbsttest-Log wieder unter festem Namen "
        "(Kit-BL-306)")
    assert re.search(r'team-init-pytest-\$PID-', code)


# --- BL-309: dieselbe Regel im Update ----------------------------------------
# BL-306 hatte nur die Erstinstallation umgestellt. Das Update schrieb weiter
# nach `team-update-pytest.log` — und wer mehrere Projekte nebeneinander hebt,
# oder der Selbsttest mit seinem Bestandsprojekt (BL-307), liess zwei Laeufe
# in dieselbe Datei schreiben.

def test_bash_update_nimmt_einen_eigenen_lognamen():
    code = _code(REPO_ROOT / "bash" / "install.sh")
    assert "/tmp/team-update-pytest.log" not in code, (
        "install.sh --update schreibt das Selbsttest-Log unter festem Namen "
        "(Kit-BL-309)")
    assert re.search(r'UPDATE_LOG="\$\(mktemp ', code)


def test_pwsh_update_nimmt_einen_eigenen_lognamen():
    code = _code(REPO_ROOT / "pwsh" / "install.ps1")
    assert "'team-update-pytest.log'" not in code, (
        "install.ps1 -Update schreibt das Selbsttest-Log unter festem Namen "
        "(Kit-BL-309)")
    assert re.search(r'team-update-pytest-\$PID-', code)

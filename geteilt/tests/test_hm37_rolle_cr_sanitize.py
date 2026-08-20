#!/usr/bin/env python3
"""Fixture-Test fuer HM-37 (Frank-Fix): akteur_abschluss() muss `rolle` genau
wie `kaskade` auch gegen ein rohes Carriage-Return (`\\r`) sanitisieren --
sonst schreibt ein `\\r` in `--rolle` ein rohes CR-Byte in die `.budget-ledger`,
das beim naechsten Einlesen (universal newlines) als Zeilenumbruch interpretiert
wird und dieselbe Ledger-Korruption wie HM-36 erzeugt.

Netz-/CLI-frei bis auf subprocess-Aufrufe von team/tools/kosten.py gegen ein
temporaeres Fixture-Ledger (kein Bezug zur echten .budget-ledger).
"""
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = kit_pfad("tools", "kosten.py")

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

import os as _os
_dom = _os.environ.get("TEAM_DOMAENEN", "").replace(",", " ").split()
DOMAENE = _dom[0] if _dom else "produkt"   # Starterkit: projektneutral



def _run(*args):
    result = subprocess.run(
        [sys.executable, str(KOSTEN_PY), *args],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _fixture_ledger(tmp_path, inhalt="# datum | kaskade | usd | auth | domaene | rolle | notiz\n"):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(inhalt)
    return pfad


def test_cr_in_rolle_erzeugt_keine_zweite_zeile(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, out, err = _run("akteur-abschluss", "--rolle", "frank\rBOESE",
                         "--kaskade", "16", "--auth", "abo",
                         "--domaene", DOMAENE, "--usd", "1.0",
                         "--pfad", str(ledger))
    assert rc == 0, err

    rohbytes = ledger.read_bytes()
    assert b"\r" not in rohbytes

    datenzeilen = [z for z in ledger.read_text().splitlines() if z.strip()
                   and not z.startswith("#")]
    assert len(datenzeilen) == 1

    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    assert len(zeilen) == 1
    assert "\r" not in zeilen[0]["rolle"]
    assert zeilen[0]["rolle"] == "frank BOESE"

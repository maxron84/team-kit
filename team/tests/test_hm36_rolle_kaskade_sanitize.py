#!/usr/bin/env python3
"""Fixture-Test fuer HM-36 (Kaskade 16/Stufe 55): akteur_abschluss() muss
`rolle`/`kaskade` genau wie `notiz` gegen das Pipe-Trennzeichen und
Zeilenumbrueche sanitisieren, bevor eine Ledger-Zeile gebaut/gematcht wird --
sonst zerschiesst ein `|`/`\n` in `--rolle`/`--kaskade` das 7-Feld-Schema der
`.budget-ledger`.

Netz-/CLI-frei bis auf subprocess-Aufrufe von team/tools/kosten.py gegen ein
temporaeres Fixture-Ledger (kein Bezug zur echten .budget-ledger).
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = REPO_ROOT / "team" / "tools" / "kosten.py"

sys.path.insert(0, str(REPO_ROOT / "team" / "tools"))
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


def test_pipe_in_rolle_und_kaskade_wird_saniert(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, out, err = _run("akteur-abschluss", "--rolle", "frank|X|Y",
                         "--kaskade", "16|Z", "--auth", "abo",
                         "--domaene", DOMAENE, "--usd", "1.23",
                         "--pfad", str(ledger))
    assert rc == 0, err
    assert "angelegt" in out

    rohzeilen = [z for z in ledger.read_text().splitlines() if z.strip()
                 and not z.startswith("#")]
    assert len(rohzeilen) == 1
    felder = [f.strip() for f in rohzeilen[0].split("|")]
    assert len(felder) == 7

    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    assert len(zeilen) == 1
    assert "|" not in zeilen[0]["rolle"]
    assert "|" not in zeilen[0]["kaskade"]
    assert zeilen[0]["rolle"] == "frank/X/Y"
    assert zeilen[0]["kaskade"] == "16/Z"


def test_newline_in_rolle_erzeugt_keine_zweite_zeile(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, out, err = _run("akteur-abschluss", "--rolle", "frank\nBOESE",
                         "--kaskade", "16", "--auth", "abo",
                         "--domaene", DOMAENE, "--usd", "1.0",
                         "--pfad", str(ledger))
    assert rc == 0, err

    datenzeilen = [z for z in ledger.read_text().splitlines() if z.strip()
                   and not z.startswith("#")]
    assert len(datenzeilen) == 1

    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    assert len(zeilen) == 1
    assert "\n" not in zeilen[0]["rolle"]
    assert zeilen[0]["rolle"] == "frank BOESE"


def test_idempotenz_greift_auf_saniertem_wert(tmp_path):
    # --ersetzen seit BL-25: Der Zweitaufruf bricht sonst ab (Default
    # "abbrechen"). Geprueft wird hier die TREFFERSUCHE auf dem sanierten
    # Wert, nicht der Umgang mit dem Bestand — dafuer muss der Ersetzungsweg
    # ausdruecklich gewaehlt werden.
    ledger = _fixture_ledger(tmp_path)
    _run("akteur-abschluss", "--rolle", "frank|X", "--kaskade", "16",
         "--auth", "abo", "--domaene", DOMAENE, "--usd", "1.0",
         "--pfad", str(ledger))
    rc, out, err = _run("akteur-abschluss", "--rolle", "frank|X",
                         "--kaskade", "16", "--auth", "abo",
                         "--domaene", DOMAENE, "--usd", "2.0",
                         "--ersetzen", "--pfad", str(ledger))
    assert rc == 0, err
    assert "ersetzt" in out

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger))
              if z["rolle"] == "frank/X"]
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == 2.0

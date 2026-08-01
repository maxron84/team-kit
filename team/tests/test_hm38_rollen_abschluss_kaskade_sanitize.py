#!/usr/bin/env python3
"""Fixture-Test fuer HM-38 (Kaskade 16, Frank-Fix): rollen_abschluss() muss
`kaskade` genau wie akteur_abschluss() (HM-36) gegen das Pipe-Trennzeichen
und Zeilenumbrueche sanitisieren, bevor eine roles-Ledger-Zeile gebaut/
gematcht wird -- sonst zerschiesst ein `|`/`\n` in `--kaskade` bei
`rollen-abschluss` das 7-Feld-Schema der `.budget-ledger` (der HM-36-Fix
haertete nur akteur_abschluss(), nicht die Schwesterfunktion).

Netz-/CLI-frei bis auf subprocess-Aufrufe von scripts/kosten.py gegen ein
temporaeres Fixture-Ledger (kein Bezug zur echten .budget-ledger).
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = REPO_ROOT / "team" / "tools" / "kosten.py"

sys.path.insert(0, str(REPO_ROOT / "team" / "tools"))
import kosten  # noqa: E402


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


def _fixture_team_logs(tmp_path, abo_usd=1.0):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    (logs / "harry-20260712-100000.json").write_text(
        json.dumps({"total_cost_usd": abo_usd}))
    return logs


def test_pipe_in_kaskade_wird_saniert(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _fixture_team_logs(tmp_path)
    rc, out, err = _run("rollen-abschluss", "--kaskade",
                         "16 | 999.9999 | api | team | architekt | GEFAELSCHT",
                         "--domaene", "team", "--logs", str(logs),
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
    assert "|" not in zeilen[0]["kaskade"]
    assert zeilen[0]["rolle"] == "roles"
    assert zeilen[0]["usd"] == 1.0


def test_newline_in_kaskade_erzeugt_keine_zweite_zeile(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _fixture_team_logs(tmp_path)
    rc, out, err = _run("rollen-abschluss", "--kaskade", "16\nBOESE",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger))
    assert rc == 0, err

    datenzeilen = [z for z in ledger.read_text().splitlines() if z.strip()
                   and not z.startswith("#")]
    assert len(datenzeilen) == 1

    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    assert len(zeilen) == 1
    assert "\n" not in zeilen[0]["kaskade"]
    assert zeilen[0]["kaskade"] == "16 BOESE"


def test_idempotenz_greift_auf_saniertem_wert(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _fixture_team_logs(tmp_path, abo_usd=1.0)
    _run("rollen-abschluss", "--kaskade", "16|X", "--domaene", "team",
         "--logs", str(logs), "--pfad", str(ledger))
    rc, out, err = _run("rollen-abschluss", "--kaskade", "16|X",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger))
    assert rc == 0, err
    assert "ersetzt" in out

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["kaskade"] == "16/X"]
    assert len(zeilen) == 1


def test_python_funktion_direkt_saniert_kaskade(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    ersetzt = kosten.rollen_abschluss("16|Z\n", 1.0, 0.0, domaene="team",
                                       pfad=str(ledger))
    assert ersetzt is False
    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    assert len(zeilen) == 1
    assert zeilen[0]["kaskade"] == "16/Z"

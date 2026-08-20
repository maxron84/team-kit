#!/usr/bin/env python3
"""Fixture-Test für HM-46 (Frank-Fix).

`team_architekt_stand()` unterschied "echt" von "geschätzt" bisher über
`[ "$echt" != "0.0000" ]` — ein reiner Wertevergleich der Summe. Eine ECHTE,
per `architekt-abschluss`/`akteur-abschluss` gebuchte Ledger-Zeile mit
usd=0.0000 (z. B. eine Kaskade, in der der Architekt nachweislich 0 USD
kostete) sah damit identisch aus wie "keine Zeile vorhanden" und fiel
fälschlich auf den A2-Schätzungs-Zweig durch.

Der Fix prüft die Existenz jetzt über `kosten.py ledger --anzahl`
(Trefferanzahl) statt über den Summenwert. Dieser Test belegt den bisher
kaputten Randfall (echte 0.0000-Zeile -> "echt") UND die drei bestehenden
Fälle aus test_stufe44_domaenen_status.py bleiben unangetastet grün.

Netz-/CLI-frei über `bash -c` + `subprocess` gegen ein Fixture-Ledger im
temporären Verzeichnis — rührt NIE die echte .budget-ledger an.
"""
import subprocess
import sys
from pathlib import Path

from conftest import BASH, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = kit_pfad("lib.sh")

FIXTURE_LEDGER_ECHTE_NULL = """\
# datum | kaskade | usd | auth | domaene | rolle | notiz
2026-07-12 | 20 | 4.1680 | abo/api | team | ralph | Bau-Kosten K20
2026-07-13 | 20 | 0.0000 | api | team | architekt | Echter Konsolenwert K20 -- 0 USD
"""


def _run(bash_script, cwd=REPO_ROOT):
    return subprocess.run(
        [BASH, "-c", bash_script],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_ledger_anzahl_zaehlt_treffer_statt_summe(tmp_path):
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER_ECHTE_NULL)
    result = subprocess.run(
        [sys.executable, str(kit_pfad("tools", "kosten.py")), "ledger", str(ledger),
         "--rolle", "architekt", "--kaskade", "20", "--anzahl"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "1"


def test_ledger_anzahl_ist_null_ohne_treffer(tmp_path):
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER_ECHTE_NULL)
    result = subprocess.run(
        [sys.executable, str(kit_pfad("tools", "kosten.py")), "ledger", str(ledger),
         "--rolle", "architekt", "--kaskade", "21", "--anzahl"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0"


def test_architekt_stand_echt_bei_echter_null_usd_zeile(tmp_path):
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER_ECHTE_NULL)
    plan = "plans/ralph-kaskade-20-irgendwas.md"
    result = _run(
        f'source "{TEAM_LIB}"; team_architekt_stand "{ledger}" "{plan}"'
    )
    assert result.returncode == 0, result.stderr
    usd, status = result.stdout.strip().split("\t")
    assert float(usd) == 0.0
    assert status == "echt", (
        "eine echte 0.0000-USD-Ledger-Zeile darf nicht als 'geschaetzt' "
        "durchfallen (HM-46)"
    )

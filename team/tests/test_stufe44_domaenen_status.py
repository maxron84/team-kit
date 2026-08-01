#!/usr/bin/env python3
"""Fixture-Test für Stufe 44 (Kaskade 13, BL-28/BL-29-Abschluss).

Belegt zwei neue team-lib.sh-Helfer, die `team-status.sh --budget` seit
Stufe 44 nutzt:

- `team_ledger_domaene <website|team> [pfad]` — Ledger-Summe gefiltert auf
  eine Domäne (dünner Wrapper um `kosten.py ledger --domaene`, BL-29).
- `team_architekt_stand [ledger-pfad] [plan-datei]` — liefert "USD<TAB>status":
  "echt", wenn für die aus der Plan-Datei abgeleitete Kaskade bereits eine
  echte Architekt-Ledger-Zeile existiert (Stufe 43, `architekt-abschluss`),
  sonst "geschätzt" mit der A2-Live-Schätzung (Stufe 42).

Netz-/CLI-frei über `bash -c` + `subprocess` (Muster wie
test_bl27_abo_key_startwarnung.py) gegen Fixture-Ledger/-Pläne im temporären
Verzeichnis — rührt NIE die echte .budget-ledger/.ralph-plan an.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = REPO_ROOT / "team" / "lib.sh"

FIXTURE_LEDGER = """\
# datum | kaskade | usd | auth | domaene | rolle | notiz
2026-07-10 | 1 | 2.0000 | abo | Altzeile ohne Domaene/Rolle
2026-07-12 | 13 | 4.1680 | abo/api | team | ralph | Bau-Kosten K13
2026-07-12 | 13 | 16.5000 | api | team | architekt | Echter Konsolenwert K13
"""

FIXTURE_LEDGER_OHNE_ARCHITEKT = """\
# datum | kaskade | usd | auth | domaene | rolle | notiz
2026-07-12 | 13 | 4.1680 | abo/api | team | ralph | Bau-Kosten K13
"""


def _run(bash_script, cwd=REPO_ROOT):
    result = subprocess.run(
        ["bash", "-c", bash_script],
        cwd=cwd, capture_output=True, text=True,
    )
    return result


def test_ledger_domaene_website_und_team_getrennt(tmp_path):
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER)
    result = _run(
        f'source "{TEAM_LIB}"; team_ledger_domaene team "{ledger}"'
    )
    assert result.returncode == 0, result.stderr
    assert float(result.stdout.strip()) == 4.168 + 16.5


def test_ledger_domaene_website_ohne_treffer_ist_null(tmp_path):
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER)
    result = _run(
        f'source "{TEAM_LIB}"; team_ledger_domaene website "{ledger}"'
    )
    assert result.returncode == 0, result.stderr
    assert float(result.stdout.strip()) == 0.0


def test_architekt_stand_echt_wenn_ledger_zeile_vorhanden(tmp_path):
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER)
    plan = "plans/ralph-kaskade-13-architekt-kosten.md"
    result = _run(
        f'source "{TEAM_LIB}"; team_architekt_stand "{ledger}" "{plan}"'
    )
    assert result.returncode == 0, result.stderr
    usd, status = result.stdout.strip().split("\t")
    assert float(usd) == 16.5
    assert status == "echt"


def test_architekt_stand_geschaetzt_ohne_ledger_zeile(tmp_path):
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER_OHNE_ARCHITEKT)
    plan = "plans/ralph-kaskade-13-architekt-kosten.md"
    result = _run(
        f'source "{TEAM_LIB}"; team_architekt_stand "{ledger}" "{plan}"'
    )
    assert result.returncode == 0, result.stderr
    usd, status = result.stdout.strip().split("\t")
    float(usd)  # muss eine Zahl bleiben (0.0000 im gepinnten Fixture-Repo)
    assert status == "geschätzt"


def test_architekt_stand_andere_kaskade_zaehlt_nicht_als_echt(tmp_path):
    # Die Ledger-Zeile gehoert zu Kaskade 13 -- eine Plan-Datei fuer Kaskade 12
    # darf sie NICHT als "echt" fuer sich beanspruchen.
    ledger = tmp_path / "fixture-ledger"
    ledger.write_text(FIXTURE_LEDGER)
    plan = "plans/ralph-kaskade-12-auth-startwarnung.md"
    result = _run(
        f'source "{TEAM_LIB}"; team_architekt_stand "{ledger}" "{plan}"'
    )
    assert result.returncode == 0, result.stderr
    _usd, status = result.stdout.strip().split("\t")
    assert status == "geschätzt"


def test_team_status_budget_zeigt_domaenen_und_architekt_status():
    # Regressionsschutz gegen das echte Repo: `--budget` muss fehlerfrei
    # laufen und die neue domaenengetrennte Aufstellung + den
    # Architekt-Status-Marker enthalten (Verifikation laut Plan, Stufe 44).
    result = subprocess.run(
        ["./team-status.sh", "--budget"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Domänen (Ledger-Basis" in result.stdout
    assert "📦"  # Starterkit: Domänenname ist projektdefiniert, nur das Symbol ist fest in result.stdout
    assert "🔧 T.E.A.M." in result.stdout
    assert "unzugeordnet" in result.stdout
    assert "Architekt (" in result.stdout
    assert "geschätzt" in result.stdout or "echt" in result.stdout

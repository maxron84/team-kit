#!/usr/bin/env python3
"""Fixture-Test fuer die kaskadenscharfen Rollenkosten (BL-17-Restpunkt/
BL-29-"1b", Kaskade 16/Stufe 54).

`kosten.py rollen-abschluss` summiert ein .team-logs-Fixture-Verzeichnis
abo/api-getrennt und haengt EINE rolle=roles-Zeile fuer die angegebene
Kaskade an (usd=abo+api, auth je nach Split). Ein zweiter Aufruf fuer
dieselbe Kaskade erzeugt KEINE zweite roles-Zeile, sondern fasst die
bestehende an -- seit BL-5 nur noch auf ausdrueckliche Ansage
(--ersetzen/--addieren), ohne Modus bricht er ab; Zeilen anderer Rollen
derselben Kaskade bleiben unangetastet. Die Bash-Oberflaeche
(team-status.sh --rollen-abschluss) archiviert .team-logs danach ueber
team_logs_archivieren -- separat geprueft gegen ein Fixture-Verzeichnis
(nie das echte .team-logs).

Netz-/CLI-frei gegen temporaere Fixture-Ledger/-Log-Verzeichnisse -- Muster
wie test_stufe50_akteur_abschluss.py/test_stufe53_ledger_split.py.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = REPO_ROOT / "team" / "tools" / "kosten.py"
TEAM_LIB = REPO_ROOT / "team" / "lib.sh"

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


def _fixture_team_logs(tmp_path, name="team-logs", abo_usd=None, api_usd=None):
    logs = tmp_path / name
    logs.mkdir()
    if abo_usd is not None:
        (logs / "harry-20260712-100000.json").write_text(
            json.dumps({"total_cost_usd": abo_usd}))
    if api_usd is not None:
        (logs / "frank-20260712-110000-api-fallback.json").write_text(
            json.dumps({"total_cost_usd": api_usd}))
    return logs


def test_gemischte_kosten_ergeben_eine_roles_zeile_mit_korrektem_split(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _fixture_team_logs(tmp_path, abo_usd=1.5, api_usd=0.75)
    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger))
    assert rc == 0, err
    assert "angelegt" in out

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == 2.25
    assert zeilen[0]["auth"] == "abo/api"
    assert zeilen[0]["domaene"] == "team"
    assert "abo 1.5000" in zeilen[0]["notiz"]
    assert "api 0.7500" in zeilen[0]["notiz"]


def test_zweiter_aufruf_gleiche_kaskade_ersetzt(tmp_path):
    """Zweiter Aufruf erzeugt KEINE zweite roles-Zeile, sondern fasst die
    bestehende an. Seit BL-5 verlangt das ein ausdrueckliches --ersetzen —
    ohne Modus bricht der Aufruf ab (siehe test_bl5_rollen_abschluss_bestand)."""
    ledger = _fixture_ledger(tmp_path)
    logs1 = _fixture_team_logs(tmp_path, name="logs1", abo_usd=1.0)
    logs2 = _fixture_team_logs(tmp_path, name="logs2", abo_usd=3.0, api_usd=2.0)
    _run("rollen-abschluss", "--kaskade", "16", "--domaene", "team",
         "--logs", str(logs1), "--pfad", str(ledger))
    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs2),
                         "--pfad", str(ledger), "--ersetzen")
    assert rc == 0, err
    assert "ersetzt" in out

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == 5.0
    assert zeilen[0]["auth"] == "abo/api"


def test_bestehende_ralph_zeile_derselben_kaskade_bleibt_unangetastet(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    _run("akteur-abschluss", "--rolle", "ralph", "--auth", "abo",
         "--usd", "4.0", "--domaene", "team", "--kaskade", "16",
         "--pfad", str(ledger))
    logs = _fixture_team_logs(tmp_path, abo_usd=1.0)
    _run("rollen-abschluss", "--kaskade", "16", "--domaene", "team",
         "--logs", str(logs), "--pfad", str(ledger))

    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    ralph_zeilen = [z for z in zeilen if z["rolle"] == "ralph"]
    roles_zeilen = [z for z in zeilen if z["rolle"] == "roles"]
    assert len(ralph_zeilen) == 1
    assert ralph_zeilen[0]["usd"] == 4.0
    assert len(roles_zeilen) == 1
    assert roles_zeilen[0]["usd"] == 1.0


def test_nur_abo_ergibt_auth_abo(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _fixture_team_logs(tmp_path, abo_usd=2.0)
    _run("rollen-abschluss", "--kaskade", "16", "--domaene", "team",
         "--logs", str(logs), "--pfad", str(ledger))
    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert zeilen[0]["auth"] == "abo"


def test_nur_api_ergibt_auth_api(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _fixture_team_logs(tmp_path, api_usd=2.0)
    _run("rollen-abschluss", "--kaskade", "16", "--domaene", "team",
         "--logs", str(logs), "--pfad", str(ledger))
    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert zeilen[0]["auth"] == "api"


def test_python_funktion_direkt_wirft_bei_ungueltiger_domaene(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    try:
        kosten.rollen_abschluss("16", 1.0, 0.0, domaene="falsch", pfad=str(ledger))
        assert False, "haette ValueError werfen muessen"
    except ValueError as exc:
        assert "domaene" in str(exc)
    assert ledger.read_text() == "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def test_archivierung_verschiebt_json_und_kosten_py_zaehlt_sie_nicht_mehr(tmp_path):
    logs = _fixture_team_logs(tmp_path, abo_usd=1.0, api_usd=2.0)
    result = subprocess.run(
        ["bash", "-c", f'source "{TEAM_LIB}"; team_logs_archivieren "{logs}"'],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    archiv = logs / "archiv"
    assert sorted(p.name for p in archiv.glob("*.json")) == [
        "frank-20260712-110000-api-fallback.json",
        "harry-20260712-100000.json",
    ]
    assert list(logs.glob("*.json")) == []

    rc, out, err = _run("summe", str(logs))
    assert rc == 0, err
    assert out == "0.0000"

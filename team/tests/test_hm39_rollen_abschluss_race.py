#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer den Zaehl-/Archivier-Race in
`rollen-abschluss` (HM-39, Root-Cause + Fix-Plan: AX-4).

Vorher lief der Kaskaden-Abschluss der Rollenkosten in zwei getrennten
Schritten (T1: Python zaehlt .team-logs/*.json per glob, T2: Bash archiviert
den DANN aktuellen Ordnerinhalt). Eine zwischen T1 und T2 neu entstandene
Log-Datei wurde bei T1 nie gezaehlt, aber bei T2 trotzdem wegarchiviert —
und war danach aus JEDER kuenftigen Kostenrechnung spurlos verschwunden
(nicht-rekursiver glob() erfasst archiv/ nie wieder).

Der Fix (kosten.py: team_log_dateien()/log_kosten(files=)/
_archiviere_dateien(), CLI-Flag --archivieren) fasst die Dateiliste EINMAL
und verwendet sie fuer Zaehlen UND Archivieren im selben Prozess. Dieser Test
simuliert den Race, indem er ZWISCHEN dem Fassen der Liste und dem
Archivieren eine zweite Datei in denselben Ordner schreibt.

Netz-/CLI-frei gegen temporaere Fixture-Verzeichnisse, nie gegen die echte
.budget-ledger/.team-logs — Muster wie test_stufe54_rollen_abschluss.py.
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


def _fixture_ledger(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text("# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    return pfad


def test_archiviert_exakt_die_gezaehlte_menge_zwischenankoemmling_bleibt_liegen(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    a = logs / "harry-20260712-100000.json"
    a.write_text(json.dumps({"total_cost_usd": 0.10}))

    # T1: die Kandidatenliste EINMAL fassen (wie kosten.py es jetzt fuer
    # Zaehlen UND Archivieren gemeinsam tut).
    files = kosten.team_log_dateien([str(logs)])
    assert files == [str(a)]

    # Zwischenankoemmling: entsteht ERST NACHDEM die Liste gefasst wurde —
    # simuliert einen parallelen team_claude-Schreiber im alten Race-Fenster.
    b = logs / "frank-20260712-110000-api-fallback.json"
    b.write_text(json.dumps({"total_cost_usd": 0.99}))

    abo, api = kosten.log_kosten([str(logs)], split=True, files=files)
    ledger = _fixture_ledger(tmp_path)
    kosten.rollen_abschluss("16", abo, api, domaene="team", pfad=str(ledger))
    kosten._archiviere_dateien(files)

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert len(zeilen) == 1
    # Kern-Invariante (Architekt-Addendum, Punkt A): die Ledger-Zeile traegt
    # NUR den bei T1 gezaehlten Betrag (a), NICHT a+b — der Beweis, dass b
    # NIE in die Summe floss.
    assert zeilen[0]["usd"] == 0.10

    # a ist archiviert, b liegt UNVERAENDERT im aktiven Ordner (nicht
    # mitgerissen) — im Gegensatz zum Alt-Verhalten (team_logs_archivieren
    # haette pauschal den kompletten Ordnerinhalt zum T2-Zeitpunkt verschoben).
    archiv = logs / "archiv"
    assert sorted(p.name for p in archiv.glob("*.json")) == [a.name]
    assert sorted(p.name for p in logs.glob("*.json")) == [b.name]


def test_naechster_abschluss_zaehlt_den_nachzuegler(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    a = logs / "harry-20260712-100000.json"
    a.write_text(json.dumps({"total_cost_usd": 0.10}))
    files = kosten.team_log_dateien([str(logs)])
    b = logs / "frank-20260712-110000-api-fallback.json"
    b.write_text(json.dumps({"total_cost_usd": 0.99}))

    ledger = _fixture_ledger(tmp_path)
    abo, api = kosten.log_kosten([str(logs)], split=True, files=files)
    kosten.rollen_abschluss("16", abo, api, domaene="team", pfad=str(ledger))
    kosten._archiviere_dateien(files)

    # Zweiter Abschluss (naechste Kaskade) ueber denselben Ordner: sieht b,
    # zaehlt dessen Kosten korrekt in eine ERSETZENDE roles-Zeile — b ging
    # trotz des Race-Fensters nicht verloren.
    files2 = kosten.team_log_dateien([str(logs)])
    assert files2 == [str(b)]
    abo2, api2 = kosten.log_kosten([str(logs)], split=True, files=files2)
    kosten.rollen_abschluss("17", abo2, api2, domaene="team", pfad=str(ledger))
    kosten._archiviere_dateien(files2)

    zeilen = {z["kaskade"]: z for z in kosten.ledger_zeilen(str(ledger))
              if z["rolle"] == "roles"}
    assert zeilen["16"]["usd"] == 0.10
    assert zeilen["17"]["usd"] == 0.99


def test_cli_archivieren_flag_atomar_ueber_eine_liste(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    a = logs / "harry-20260712-100000.json"
    a.write_text(json.dumps({"total_cost_usd": 0.10}))
    ledger = _fixture_ledger(tmp_path)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren")
    assert rc == 0, err
    assert "archiviert" in out

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert zeilen[0]["usd"] == 0.10
    archiv = logs / "archiv"
    assert sorted(p.name for p in archiv.glob("*.json")) == [a.name]
    assert list(logs.glob("*.json")) == []


def test_cli_ohne_archivieren_flag_verschiebt_nichts():
    """Regressionsschutz: Default (kein --archivieren) bleibt wie bisher
    fuer reine Test-/Auswertungslaeufe folgenlos (siehe bestehende
    test_stufe54_rollen_abschluss.py-Tests, die ohne das Flag aufrufen)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        logs = tmp_path / "team-logs"
        logs.mkdir()
        a = logs / "harry-20260712-100000.json"
        a.write_text(json.dumps({"total_cost_usd": 0.10}))
        ledger = _fixture_ledger(tmp_path)

        rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                             "--domaene", "team", "--logs", str(logs),
                             "--pfad", str(ledger))
        assert rc == 0, err
        assert "archiviert" not in out
        assert list(logs.glob("*.json")) == [a]

#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer HM-41 (Marv-Fund, Kaskade 16).

Vorher archivierte `rollen-abschluss --archivieren` bedingungslos die
GESAMTE T1-Dateiliste (HM-39-Fix), auch Dateien, die `log_kosten()` wegen
eines Parse-Fehlers (abgeschnittenes/kaputtes JSON) STILL mit 0.0 gezaehlt
hatte -- ein realer, bereits bezahlter Claude-Aufruf verschwand dadurch
spurlos im Archiv, ohne Fehler, ohne Warnung.

Der Fix (kosten.py: log_kosten(..., return_geparst=True) liefert die
Teilmenge der tatsaechlich erfolgreich geparsten Dateien; die
rollen-abschluss-CLI archiviert NUR diese Teilmenge und warnt auf stderr
fuer jede nicht-parsebare Datei, die liegen bleibt.

Netz-/CLI-frei gegen temporaere Fixture-Verzeichnisse, nie gegen die echte
.budget-ledger/.team-logs -- Muster wie test_hm39_rollen_abschluss_race.py.
"""
import json
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


def test_log_kosten_return_geparst_schliesst_kaputte_datei_aus(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    gut = logs / "harry-20260713-100000.json"
    gut.write_text(json.dumps({"total_cost_usd": 2.50}))
    kaputt = logs / "frank-20260713-120000.json"
    kaputt.write_text('{"total_cost_usd":')  # abgeschnitten

    files = kosten.team_log_dateien([str(logs)])
    (abo, api), geparst = kosten.log_kosten(
        [str(logs)], split=True, files=files, return_geparst=True)

    assert abo == 2.50
    assert api == 0.0
    assert geparst == [str(gut)]
    assert str(kaputt) not in geparst


def test_cli_archivieren_laesst_kaputte_datei_liegen_und_warnt(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    gut = logs / "harry-20260713-100000.json"
    gut.write_text(json.dumps({"total_cost_usd": 2.50}))
    kaputt = logs / "frank-20260713-120000.json"
    kaputt.write_text('{"total_cost_usd":')
    ledger = _fixture_ledger(tmp_path)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren")
    assert rc == 0, err
    assert "1 Log(s) archiviert" in out
    assert "1 nicht-parsebare Log(s) NICHT archiviert" in out
    assert str(kaputt) in err
    assert "Warnung" in err

    # Nur die gute Datei wandert ins Archiv, die kaputte bleibt aktiv liegen.
    archiv = logs / "archiv"
    assert sorted(p.name for p in archiv.glob("*.json")) == [gut.name]
    assert sorted(p.name for p in logs.glob("*.json")) == [kaputt.name]

    # Die Ledger-Zeile traegt nur den Betrag der geparsten Datei.
    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == 2.50


def test_cli_ohne_archivieren_flag_warnt_aber_verschiebt_nichts(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    kaputt = logs / "frank-20260713-120000.json"
    kaputt.write_text('{"total_cost_usd":')
    ledger = _fixture_ledger(tmp_path)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger))
    assert rc == 0, err
    assert "archiviert" not in out
    assert str(kaputt) in err
    assert list(logs.glob("*.json")) == [kaputt]
    assert not (logs / "archiv").exists()

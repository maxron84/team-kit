#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer HM-44 (Marv-Fund, Kaskade 16).

Vorher validierten _datei_kosten()/log_kosten() total_cost_usd NUR auf
Summenebene, nicht pro Datei -- ein einzelnes .team-logs/.ralph-logs-JSON mit
negativem (oder nicht-endlichem) total_cost_usd saldierte unbemerkt echte
Kosten aus einer anderen Datei weg, solange die Gesamtsumme selbst
nicht-negativ blieb. Weder rollen_abschluss()/akteur_abschluss() (die nur die
fertige Summe pruefen) noch die ungeprueften Aufrufer team_kosten_summe/
-split/-seit (und damit vollautomatik.sh:budget_ok()) bemerkten das.

Der Fix (kosten.py: _datei_kosten()) behandelt einen negativen oder
nicht-endlichen (NaN/Infinity) total_cost_usd-Wert jetzt genauso wie einen
Parse-Fehler -- ok=False, Datei faellt aus der Summe UND bleibt beim
rollen-abschluss --archivieren unarchiviert liegen (nutzt die HM-41-Warnung
mit).

Netz-/CLI-frei gegen temporaere Fixture-Verzeichnisse, nie gegen die echte
.budget-ledger/.team-logs -- Muster wie test_hm41_kaputte_datei_nicht_archiviert.py.
"""
import json
import math
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
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _fixture_ledger(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text("# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    return pfad


def test_datei_kosten_lehnt_negativen_wert_ab(tmp_path):
    datei = tmp_path / "marv-negativ.json"
    datei.write_text(json.dumps({"total_cost_usd": -2.00}))

    kosten_wert, ok = kosten._datei_kosten(str(datei))

    assert ok is False
    assert kosten_wert == 0.0


def test_datei_kosten_lehnt_nan_und_infinity_ab(tmp_path):
    nan_datei = tmp_path / "nan.json"
    nan_datei.write_text('{"total_cost_usd": NaN}')
    inf_datei = tmp_path / "inf.json"
    inf_datei.write_text('{"total_cost_usd": Infinity}')

    assert kosten._datei_kosten(str(nan_datei)) == (0.0, False)
    assert kosten._datei_kosten(str(inf_datei)) == (0.0, False)


def test_log_kosten_negative_datei_saldiert_echte_kosten_nicht_mehr_weg(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    echt = logs / "harry-20260713-100000.json"
    echt.write_text(json.dumps({"total_cost_usd": 2.50}))
    manipuliert = logs / "marv-20260713-120000.json"
    manipuliert.write_text(json.dumps({"total_cost_usd": -2.00}))

    (abo, api), geparst = kosten.log_kosten(
        [str(logs)], split=True, return_geparst=True)

    # Vor dem Fix: abo == 0.50 (2.50 + -2.00), die manipulierte Datei
    # verschwand unbemerkt in der Summe. Jetzt zaehlt nur die echte Datei.
    assert abo == 2.50
    assert api == 0.0
    assert geparst == [str(echt)]
    assert str(manipuliert) not in geparst


def test_cli_archivieren_laesst_negative_datei_liegen_und_warnt(tmp_path):
    logs = tmp_path / "team-logs"
    logs.mkdir()
    echt = logs / "harry-20260713-100000.json"
    echt.write_text(json.dumps({"total_cost_usd": 2.50}))
    manipuliert = logs / "marv-20260713-120000.json"
    manipuliert.write_text(json.dumps({"total_cost_usd": -2.00}))
    ledger = _fixture_ledger(tmp_path)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren")
    assert rc == 0, err
    assert "1 Log(s) archiviert" in out
    assert str(manipuliert) in err
    assert "Warnung" in err

    archiv = logs / "archiv"
    assert sorted(p.name for p in archiv.glob("*.json")) == [echt.name]
    assert sorted(p.name for p in logs.glob("*.json")) == [manipuliert.name]

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]
    assert len(zeilen) == 1
    assert math.isclose(zeilen[0]["usd"], 2.50)

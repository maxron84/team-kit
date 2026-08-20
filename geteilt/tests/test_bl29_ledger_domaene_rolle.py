#!/usr/bin/env python3
"""Fixture-Test fuer das erweiterte Ledger-Schema (BL-29, Kaskade 13/Stufe 41).

Bisheriges Schema: datum | kaskade | usd | auth | notiz (5 Felder).
Neues, rueckwaertskompatibles Schema: datum | kaskade | usd | auth | domaene |
rolle | notiz (7 Felder). Altzeilen bleiben gueltig und werden NICHT
umgeschrieben; `kosten.py ledger --domaene ...`/`--rolle ...` summiert nur
Zeilen im neuen Schema, Altzeilen zaehlen als "unzugeordnet" (nie
stillschweigend einer Domaene zugeschlagen). Der ungefilterte Gesamtwert
bleibt unveraendert korrekt (ledger_summe() ohne Filter, verifiziert).

Netz-/CLI-frei: ruft team/tools/kosten.py per subprocess gegen ein Fixture-
Ledger im temporaeren Verzeichnis auf.
"""
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = kit_pfad("tools", "kosten.py")

FIXTURE_LEDGER = """\
# datum | kaskade | usd | auth | notiz
2026-07-10 | 1 | 2.0000 | abo | Altzeile ohne Domaene/Rolle
2026-07-10 | 2 | 3.0000 | abo | Noch eine Altzeile
2026-07-12 | 13 | 4.0000 | abo | website | ralph | Neue Zeile, Website-Domaene
2026-07-12 | 13 | 5.0000 | api | team | ralph | Neue Zeile, Team-Domaene
2026-07-12 | 13 | 1.5000 | api | team | architekt | Architekt-Schaetzung, Team
"""


def _run_ledger(pfad, *extra_args):
    result = subprocess.run(
        [sys.executable, str(KOSTEN_PY), "ledger", str(pfad), *extra_args],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _write_fixture(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(FIXTURE_LEDGER)
    return pfad


def test_gesamtsumme_bleibt_unveraendert(tmp_path):
    pfad = _write_fixture(tmp_path)
    rc, out, _ = _run_ledger(pfad)
    assert rc == 0
    assert float(out) == 15.5  # 2 + 3 + 4 + 5 + 1.5


def test_domaene_website_summiert_nur_passende_neue_zeilen(tmp_path):
    pfad = _write_fixture(tmp_path)
    rc, out, _ = _run_ledger(pfad, "--domaene", "website")
    assert rc == 0
    assert float(out) == 4.0


def test_domaene_team_summiert_nur_passende_neue_zeilen(tmp_path):
    pfad = _write_fixture(tmp_path)
    rc, out, _ = _run_ledger(pfad, "--domaene", "team")
    assert rc == 0
    assert float(out) == 6.5  # 5.0 + 1.5


def test_altzeilen_zaehlen_bei_domaenen_filter_nicht_mit(tmp_path):
    # Ungefiltert 15.5, gefiltert nach website+team nur 10.5 -> die beiden
    # 5-Feld-Altzeilen (2 + 3 = 5.0) bleiben bei JEDEM Domaenen-Filter aussen
    # vor -- sie werden nie stillschweigend zugeschlagen.
    pfad = _write_fixture(tmp_path)
    _, out_website, _ = _run_ledger(pfad, "--domaene", "website")
    _, out_team, _ = _run_ledger(pfad, "--domaene", "team")
    assert float(out_website) + float(out_team) == 10.5


def test_rolle_filter_summiert_nur_passende_rolle(tmp_path):
    pfad = _write_fixture(tmp_path)
    rc, out, _ = _run_ledger(pfad, "--rolle", "architekt")
    assert rc == 0
    assert float(out) == 1.5


def test_domaene_und_rolle_kombiniert(tmp_path):
    pfad = _write_fixture(tmp_path)
    rc, out, _ = _run_ledger(pfad, "--domaene", "team", "--rolle", "ralph")
    assert rc == 0
    assert float(out) == 5.0


def test_ungueltige_domaene_bricht_sauber_ab(tmp_path):
    """Starterkit-Vertrag: Beim LESEN wird die Domaene NICHT validiert — ein
    Ledger kann historische Zeilen mit heute nicht mehr konfigurierten Domaenen
    enthalten, die muss man weiter filtern koennen. Ein unbekannter Filter
    liefert schlicht 0. Validiert wird nur beim SCHREIBEN (siehe
    test_stufe51_akteur_cli)."""
    pfad = tmp_path / "ledger"
    pfad.write_text(FIXTURE_LEDGER)
    rc, out, _ = _run_ledger(pfad, "--domaene", "gibt-es-nicht")
    assert rc == 0
    assert float(out) == 0.0


def test_fehlende_datei_ergibt_null():
    rc, out, _ = _run_ledger("/nicht/vorhanden/ledger")
    assert rc == 0
    assert float(out) == 0.0


def test_echtes_budget_ledger_bleibt_parsebar():
    # Regressionsschutz: das committete .budget-ledger (Mischung aus
    # historischen Zeilen) muss weiterhin fehlerfrei summiert werden.
    #
    # T.E.A.M.-Starterkit: In einem frisch eingerichteten Projekt ist das
    # Ledger noch leer — dann ist nur die FEHLERFREIHEIT pruefbar, nicht eine
    # Summe > 0. Sobald die erste Kaskade geledgert ist, greift die volle
    # Pruefung automatisch.
    ledger = REPO_ROOT / ".budget-ledger"
    rc, out, _ = _run_ledger(ledger)
    assert rc == 0
    if not ledger.exists() or not ledger.read_text(encoding="utf-8").strip():
        assert float(out) == 0.0
        return
    assert float(out) > 0

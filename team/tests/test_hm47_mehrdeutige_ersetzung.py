#!/usr/bin/env python3
"""Fixture-Test fuer HM-47 (Kaskade-Frank-Fix): akteur_abschluss()/
rollen_abschluss() duerfen bei einem erneuten Aufruf NICHT kommentarlos
ALLE bestehenden Zeilen derselben Kaskade/Rolle loeschen -- .budget-ledger
enthaelt real bereits mehrere eigenstaendige Zeilen derselben Kaskade/Rolle
(z. B. spaeter nachgetragene Restlogs, siehe Beutebuch HM-47). Ein Aufruf,
der auf zwei oder mehr bestehende Zeilen matcht, muss stattdessen mit einem
Fehler abbrechen, OHNE die Datei anzufassen.

Netz-/CLI-frei bis auf subprocess-Aufrufe von scripts/kosten.py gegen ein
temporaeres Fixture-Ledger (kein Bezug zur echten .budget-ledger).
"""
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


ZWEI_ZEILEN_RALPH_K13 = (
    "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"
    "2026-07-12 | 13 | 4.1680 | abo/api | team | ralph | erste Buchung\n"
    "2026-07-12 | 13 | 3.7785 | api | team | ralph | Restlog nachgetragen\n"
)


def test_akteur_abschluss_bricht_bei_mehreren_treffern_ab(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(ZWEI_ZEILEN_RALPH_K13)

    try:
        kosten.akteur_abschluss(
            1.2345, "team", "13", "ralph", "api", notiz="Tippfehler-Korrektur",
            pfad=str(pfad),
        )
        assert False, "erwartete ValueError bei mehrdeutiger Ersetzung"
    except ValueError as exc:
        assert "mehrdeutig" in str(exc)

    # Datei bleibt unangetastet -- kein Datenverlust.
    assert pfad.read_text() == ZWEI_ZEILEN_RALPH_K13


def test_akteur_abschluss_cli_bricht_ab_und_schreibt_nichts(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(ZWEI_ZEILEN_RALPH_K13)

    rc, out, err = _run(
        "akteur-abschluss", "--usd", "1.2345", "--domaene", "team",
        "--kaskade", "13", "--rolle", "ralph", "--auth", "api",
        "--pfad", str(pfad),
    )
    assert rc == 1
    assert "mehrdeutig" in err
    assert pfad.read_text() == ZWEI_ZEILEN_RALPH_K13


def test_akteur_abschluss_ersetzt_weiterhin_genau_eine_zeile(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(
        "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"
        "2026-07-12 | 13 | 4.1680 | api | team | ralph | erste Buchung\n"
        "2026-07-12 | 13 | 1.0000 | api | team | architekt | andere Rolle\n"
    )

    ersetzt = kosten.akteur_abschluss(
        9.9999, "team", "13", "ralph", "api", notiz="Korrektur", pfad=str(pfad),
    )
    assert ersetzt is True
    inhalt = pfad.read_text()
    assert "9.9999" in inhalt
    assert "4.1680" not in inhalt
    assert "andere Rolle" in inhalt


def test_rollen_abschluss_bricht_bei_mehreren_treffern_ab(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    inhalt = (
        "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"
        "2026-07-12 | 16 | 1.0000 | abo | team | roles | erste Buchung\n"
        "2026-07-12 | 16 | 2.0000 | api | team | roles | Restlog nachgetragen\n"
    )
    pfad.write_text(inhalt)

    try:
        kosten.rollen_abschluss(
            "16", abo=0.5, api=0.5, domaene="team", notiz="Korrektur",
            pfad=str(pfad),
        )
        assert False, "erwartete ValueError bei mehrdeutiger Ersetzung"
    except ValueError as exc:
        assert "mehrdeutig" in str(exc)
    assert pfad.read_text() == inhalt

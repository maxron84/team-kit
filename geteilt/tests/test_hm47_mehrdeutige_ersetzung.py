#!/usr/bin/env python3
"""Fixture-Test fuer HM-47 (Kaskade-Frank-Fix): akteur_abschluss()/
rollen_abschluss() duerfen bei einem erneuten Aufruf NICHT kommentarlos
ALLE bestehenden Zeilen derselben Kaskade/Rolle loeschen -- .budget-ledger
enthaelt real bereits mehrere eigenstaendige Zeilen derselben Kaskade/Rolle
(z. B. spaeter nachgetragene Restlogs, siehe Beutebuch HM-47). Ein Aufruf,
der auf zwei oder mehr bestehende Zeilen matcht, muss stattdessen mit einem
Fehler abbrechen, OHNE die Datei anzufassen.

Netz-/CLI-frei bis auf subprocess-Aufrufe von team/tools/kosten.py gegen ein
temporaeres Fixture-Ledger (kein Bezug zur echten .budget-ledger).
"""
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

    # bestand="ersetzen" seit BL-25 (Default ist "abbrechen"): Dieser Test
    # prueft die EINDEUTIGKEIT der Ersetzung — genau eine Zeile, die richtige —,
    # nicht die Frage, ob ersetzt werden darf.
    ersetzt = kosten.akteur_abschluss(
        9.9999, "team", "13", "ralph", "api", notiz="Korrektur", pfad=str(pfad),
        bestand="ersetzen",
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

#!/usr/bin/env python3
"""BL-295: Pruefung P2 der Ledger-Konsistenz uebersah die Rolle — und warnte
bei JEDEM Closeout falsch, mit einer Abhilfe, die Geld loescht.

WAS IM FELD PASSIERT IST (`Feld E`, 2026-08-24, dritte Kaskade)
    `--budget` und `--ledger-pruefen` meldeten: *„Kaskade 3 ist bereits
    gebucht (1 Zeile(n)), aber es liegen 13 unarchivierte Log(s) … (dann
    `--rollen-abschluss … --addieren`) … ein `--ersetzen` hier verliert den
    Altwert"*. Keine der Ursachen traf zu: Die eine gebuchte Zeile war die
    `architekt`-Zeile der AUSHAERTUNG, die dreizehn Logs die des Laufs, der
    gerade abgeschlossen werden sollte. Der normale Zustand „gebaut,
    Closeout beginnt jetzt" sah aus wie ein Doppelbuchungsrisiko.

WARUM
    P2 pruefte `aktuelle_kaskade in je_kaskade` — eine einzige Zeile JEDER
    Rolle genuegte. Die Nachbarpruefungen P1 und P1b machen die Ausnahme
    ausdruecklich; `LEDGER_OHNE_ROHLOG = ("architekt",)` benennt die Trennung
    im selben Modul. Gemeldet am 2026-08-24, triagiert erst am 2026-10-03
    (`BL-268`).
"""
import json
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

KOSTEN = kit_pfad("tools", "kosten.py")


def _log(ordner, name, usd):
    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / name).write_text(json.dumps({"is_error": False,
                                           "subtype": "success",
                                           "total_cost_usd": usd}),
                               encoding="utf-8")


def _pruefen(tmp_path, ledger_text):
    ledger = tmp_path / ".budget-ledger"
    ledger.write_text(ledger_text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(KOSTEN), "ledger-pruefen", "--pfad", str(ledger),
         "--kaskade", "3", "--ralph-logs", str(tmp_path / ".ralph-logs"),
         "--team-logs", str(tmp_path / ".team-logs")],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        errors="replace")


def test_nur_die_aushaertung_gebucht_ist_kein_doppelbuchungsrisiko(tmp_path):
    """Der Feldfall: nur die `architekt`-Zeile, dazu die Logs des Laufs."""
    for i in range(3):
        _log(tmp_path / ".ralph-logs", f"stufe-{i}.json", 2.0)
    _log(tmp_path / ".team-logs", "harry-1.json", 1.5)
    r = _pruefen(tmp_path,
                 "2026-08-24 | 3 | 4.0000 | abo | produkt | architekt | Plan\n")
    assert "bereits gebucht" not in r.stdout, (
        "P2 haelt die gebuchte Aushaertung fuer einen Rollenabschluss und "
        f"raet zu --addieren/--ersetzen (BL-295).\n{r.stdout}")
    assert "--ersetzen" not in r.stdout, r.stdout


def test_ein_gebuchter_rollenabschluss_mit_neuen_logs_warnt_weiter(tmp_path):
    """Gegenrichtung, und die wichtigere: Der BL-5-Fall bleibt scharf."""
    _log(tmp_path / ".ralph-logs", "stufe-9.json", 2.0)
    r = _pruefen(tmp_path,
                 "2026-08-24 | 3 | 12.0000 | abo | produkt | ralph | Bau\n"
                 "2026-08-24 | 3 | 4.0000 | abo | produkt | architekt | Plan\n")
    assert r.returncode == 4 and "unarchivierte Log(s)" in r.stdout, r.stdout


def test_auch_eine_roles_zeile_zaehlt_als_gebucht(tmp_path):
    _log(tmp_path / ".team-logs", "frank-HM-1-v1.json", 0.8)
    r = _pruefen(tmp_path,
                 "2026-08-24 | 3 | 3.0000 | abo | produkt | roles | Rollen\n"
                 "2026-08-24 | 3 | 4.0000 | abo | produkt | architekt | Plan\n")
    assert "unarchivierte Log(s)" in r.stdout, r.stdout


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))

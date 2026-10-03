#!/usr/bin/env python3
"""BL-280: Eine ganze Kaskade kann ohne Closeout ausfallen — und
`--ledger-pruefen` meldete 0 Warnungen.

DER FELDBEFUND (`Feld B`, 2026-09-22)
    Beim Closeout der Kaskade 29 kam heraus, dass 28 nie abgeschlossen war:
    keine Ledger-Zeile, elf Rohlogs ueber 31,19 USD vier Tage unarchiviert.
    Die Pruefung konnte das konstruktiv nicht sehen — sie kennt nur Kaskaden,
    die im Ledger VORKOMMEN (`Kit-BL-1`: der Pruefling definiert die
    Pruefmenge). P4 nimmt die Menge aus den Plandateien.

GEGENPROBE IN BEIDE RICHTUNGEN
    Gebucht: kein Befund. Nie gelaufen: kein Befund. Die aktive Kaskade
    selbst: kein Befund (ihr Closeout steht regulaer aus, P1b).
"""
import os
import subprocess
import sys

import test_bl266_vor_n_bucht_nur_sein_zeitfenster as h

STUNDE = h.STUNDE


def _pruefe(repo, kaskade="29"):
    r = subprocess.run(
        [sys.executable, str(h.KOSTEN_PY), "ledger-pruefen",
         "--kaskade", kaskade],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=dict(os.environ, TEAM_DOMAENEN="produkt"))
    return r.returncode, r.stdout + r.stderr


def _lage(tmp_path, logs_28=True):
    repo = h._repo(tmp_path, plan_nummer=None)
    t28 = os.path.getmtime(repo / ".budget-ledger") - 20 * STUNDE
    h._plan_um(repo, 28, t28)
    h._plan_um(repo, 29, t28 + 10 * STUNDE)
    (repo / ".ralph-logs" / "archiv").mkdir(parents=True)
    if logs_28:
        for i in range(3):
            datei = repo / ".ralph-logs" / f"stufe-{i}.json"
            datei.write_text('{"total_cost_usd": 2.0}', encoding="utf-8")
            os.utime(datei, (t28 + STUNDE + i,) * 2)
    return repo


def _bucht(repo, kaskade, rolle="ralph"):
    with open(repo / ".budget-ledger", "a", encoding="utf-8") as fh:
        fh.write(f"2026-09-22 | {kaskade} | 5.0000 | abo | produkt | {rolle} | x\n")


def test_eine_ausgefallene_kaskade_ist_eine_warnung(tmp_path):
    repo = _lage(tmp_path)
    _bucht(repo, "29")
    rc, aus = _pruefe(repo)
    assert rc == 4, aus
    assert "Kaskade 28" in aus and "BL-280" in aus, aus
    assert "--rollen-abschluss 28" in aus, aus


def test_eine_gebuchte_kaskade_schweigt(tmp_path):
    repo = _lage(tmp_path)
    _bucht(repo, "28")
    _bucht(repo, "29")
    rc, aus = _pruefe(repo)
    assert "BL-280" not in aus, aus


def test_ein_plan_der_nie_lief_ist_kein_befund(tmp_path):
    repo = _lage(tmp_path, logs_28=False)
    _bucht(repo, "29")
    rc, aus = _pruefe(repo)
    assert "BL-280" not in aus, aus


def test_die_aktive_kaskade_selbst_ist_kein_befund(tmp_path):
    """Ihr Closeout steht regulaer noch aus — dafuer gibt es P1b."""
    repo = _lage(tmp_path)
    _bucht(repo, "28")
    rc, aus = _pruefe(repo, kaskade="29")
    assert "Kaskade 29" not in aus or "BL-280" not in aus, aus


def test_archivierte_logs_zaehlen_als_gelaufen(tmp_path):
    repo = _lage(tmp_path, logs_28=False)
    t28 = h.kosten.kaskade_beginn("28", str(repo))
    datei = repo / ".ralph-logs" / "archiv" / "stufe-1.json"
    datei.write_text('{"total_cost_usd": 2.0}', encoding="utf-8")
    os.utime(datei, (t28 + STUNDE,) * 2)
    _bucht(repo, "29")
    rc, aus = _pruefe(repo)
    assert "Kaskade 28" in aus and "BL-280" in aus, aus


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))

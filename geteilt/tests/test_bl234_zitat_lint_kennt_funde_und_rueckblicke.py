#!/usr/bin/env python3
"""BL-234 und BL-282: `zitat_lint.py` kennt Fund- und Aktenzitate — und
zaehlt Rueckblicke, statt sie zu melden.

BL-234 (`Feld B`, 2026-09-07)
    Der Lint las ausschliesslich den Backlog. Eine Roadmap-Skizze begruendete
    ihre harte Vorbedingung mit drei Fund-Nummern, die eine Fixphase derselben
    Kaskade Stunden zuvor erledigt hatte; gemeldet wurden fuenf andere Faelle,
    dieser nicht.

BL-282 (`Feld B`, 2026-09-22)
    Im Closeout: zehn veraltete Zitate, Exit 3 — alle zehn in Rueckblicken
    (Abschluss-Protokolle, Archive), null in den vorwaerts gerichteten Dateien.
    Eine Ausgabe aus 100 % Nicht-Befunden wird nicht mehr gelesen.
"""
import os
import subprocess
import sys

import pytest

from conftest import kit_pfad

WERKZEUG = kit_pfad("tools", "zitat_lint.py")
pytestmark = pytest.mark.skipif(
    not WERKZEUG.is_file(), reason="zitat_lint.py liegt in dieser Ablage nicht")

BACKLOG = ("| Nr | Was | Woher | Status |\n|---|---|---|---|\n"
           "| BL-6 | Etwas | Feld | **erledigt (Stufe 5).** |\n")

BEUTEBUCH = """# Beutebuch

## Funde

### HM-7 — Der Knopf liegt unter der Tastatur

- **Status**: erledigt (Frank-Fix, abc1234)
- **Fundstelle**: `src/pult.py`

### HM-8 — Noch nicht gefixt

- **Status**: an Frank übergeben
- **Fundstelle**: `src/pult.py`
"""

SKIZZE = """# Roadmap

Die Kaskade wartet auf HM-7 und HM-8, beide muessen erledigt sein.

Die Folgestufe wartet auf AX-1.
"""


def _projekt(tmp_path):
    plans = tmp_path / "plans"
    (plans / "ermittlungsakten").mkdir(parents=True)
    (plans / "backlog.md").write_text(BACKLOG, encoding="utf-8")
    (plans / "beutebuch.md").write_text(BEUTEBUCH, encoding="utf-8")
    (plans / "ermittlungsakten" / "AX-1.md").write_text(
        "# AX-1 — Root-Cause des Knopfes (Bezug: HM-7)\n\n## Root-Cause\nx\n",
        encoding="utf-8")
    return plans


def _lint(plans, *zusatz):
    return subprocess.run(
        [sys.executable, str(WERKZEUG), "--backlog", str(plans / "backlog.md"),
         *zusatz], capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))


def test_ein_erledigter_fund_als_vorbedingung_wird_gemeldet(tmp_path):
    plans = _projekt(tmp_path)
    (plans / "roadmap-skizzen.md").write_text(SKIZZE, encoding="utf-8")
    r = _lint(plans)
    assert r.returncode == 3, r.stdout + r.stderr
    assert "zitiert HM-7" in r.stderr, r.stderr
    assert "zitiert HM-8" not in r.stderr, (
        "HM-8 ist nicht erledigt — ein Zitat darauf ist aktuell.")


def test_eine_akte_gilt_ueber_ihren_fund(tmp_path):
    plans = _projekt(tmp_path)
    (plans / "roadmap-skizzen.md").write_text(SKIZZE, encoding="utf-8")
    r = _lint(plans)
    assert "zitiert AX-1" in r.stderr and "HM-7" in r.stderr, r.stderr


def test_kit_fundnummern_sind_ein_fremder_nummernraum(tmp_path):
    plans = _projekt(tmp_path)
    (plans / "roadmap-skizzen.md").write_text(
        "# Roadmap\n\nDas wartet auf `Kit-HM-7` aus dem Kit.\n", encoding="utf-8")
    r = _lint(plans)
    assert r.returncode == 0, r.stderr


def test_das_beutebuch_selbst_ist_keine_plandatei(tmp_path):
    """Die Statusquelle wird nicht als Prosa gelesen — sonst meldet ein
    Fundblock, der auf einen erledigten Vorgaenger verweist."""
    plans = _projekt(tmp_path)
    with open(plans / "beutebuch.md", "a", encoding="utf-8") as fh:
        fh.write("\n### HM-9 — Folge\n\n- **Status**: offen\n"
                 "- **Abgrenzung**: wartet auf HM-7.\n")
    r = _lint(plans)
    assert r.returncode == 0, r.stderr


# --- BL-282 -------------------------------------------------------------------

def test_ein_rueckblick_wird_gezaehlt_nicht_gemeldet(tmp_path):
    plans = _projekt(tmp_path)
    (plans / "kaskade-3-abschluss.md").write_text(
        "# Abschluss\n\nDie Stufe wartet auf `BL-6`, das noch offen ist.\n",
        encoding="utf-8")
    r = _lint(plans)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "1 weitere in Abschlussprotokollen" in r.stdout, r.stdout


def test_rueckblicke_zeigt_die_einzelnen_treffer(tmp_path):
    plans = _projekt(tmp_path)
    (plans / "kaskade-3-abschluss.md").write_text(
        "# Abschluss\n\nDie Stufe wartet auf `BL-6`, das noch offen ist.\n",
        encoding="utf-8")
    r = _lint(plans, "--rueckblicke")
    assert r.returncode == 0
    assert "Rueckblick, nicht mitgezaehlt" in r.stderr, r.stderr


def test_ein_aktiver_befund_neben_rueckblicken_bleibt_ein_befund(tmp_path):
    plans = _projekt(tmp_path)
    (plans / "kaskade-3-abschluss.md").write_text(
        "# Abschluss\n\nDie Stufe wartet auf `BL-6`, das noch offen ist.\n",
        encoding="utf-8")
    (plans / "roadmap-skizzen.md").write_text(SKIZZE, encoding="utf-8")
    r = _lint(plans)
    assert r.returncode == 3
    assert "in aktiven Planungsdateien" in r.stderr
    assert "1 weitere in Abschlussprotokollen" in r.stderr, r.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

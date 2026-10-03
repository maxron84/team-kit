#!/usr/bin/env python3
"""BL-277: Ein Fundblock waechst nach unten, gelesen wird er von oben — die
Vorlage traegt jetzt eine `Stand`-Zeile am Kopf, `set` zieht sie mit, und
`lint` weist auf eine veraltete hin.

DER FELDBEFUND (`Feld B`, 2026-09-18)
    Eine Kaskade wurde auf einer veralteten Lesung geplant: Die Skizze
    zitierte den KOPF eines 183 Zeilen langen Fundblocks mit fuenf
    Nachtraegen; dass die Haelfte davon seit neun Tagen gebaut war, stand
    unten. Die Statuszeile stand formal richtig auf `offen` (eine Messung blieb
    offen) und war damit von „hier ist nichts gebaut" nicht zu unterscheiden.
"""
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from conftest import kit_pfad

BEUTEBUCH_PY = kit_pfad("tools", "beutebuch.py")
VORLAGE = Path(__file__).resolve().parents[2] / "bootstrap" / "beutebuch.md"

BLOCK = """# Beutebuch

## Funde

### HM-4 — Der Export rechnet falsch

- **Status**: offen
{stand}- **Fundstelle**: `src/export.py`
- **Reproducer-Test**: `tests/test_hm4_export.py`

**Nachtrag 2026-09-09:** Rundung gebaut, die Messung bleibt offen.
"""


def _cli(*args):
    r = subprocess.run([sys.executable, str(BEUTEBUCH_PY), *args],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout, r.stderr


def _buch(tmp_path, stand=""):
    pfad = tmp_path / "beutebuch.md"
    pfad.write_text(BLOCK.format(stand=stand), encoding="utf-8")
    return pfad


def test_die_vorlage_traegt_die_stand_zeile():
    if not VORLAGE.is_file():
        pytest.skip("Kit-Wurzel: die Vorlage liegt nur im Kit")
    text = VORLAGE.read_text(encoding="utf-8")
    assert "- **Stand**:" in text and "Kit-BL-277" in text


def test_ohne_stand_zeile_weist_lint_hin(tmp_path):
    buch = _buch(tmp_path)
    rc, _, err = _cli("--pfad", str(buch), "lint", "HM-4")
    assert rc == 0, err
    assert "Kit-BL-277" in err and "keine `- **Stand**:`" in err, err


def test_eine_aeltere_stand_zeile_weist_hin(tmp_path):
    buch = _buch(tmp_path, "- **Stand**: 2026-09-01 — nichts gebaut\n")
    rc, _, err = _cli("--pfad", str(buch), "lint", "HM-4")
    assert rc == 0, err
    assert "2026-09-01" in err and "2026-09-09" in err, err


def test_eine_aktuelle_stand_zeile_schweigt(tmp_path):
    buch = _buch(tmp_path, "- **Stand**: 2026-09-09 — Rundung gebaut, Messung offen\n")
    rc, _, err = _cli("--pfad", str(buch), "lint", "HM-4")
    assert rc == 0 and "Kit-BL-277" not in err, err


def test_set_zieht_die_stand_zeile_mit(tmp_path):
    buch = _buch(tmp_path, "- **Stand**: 2026-09-01 — nichts gebaut\n")
    rc, _, err = _cli("--pfad", str(buch), "set", "HM-4", "an Frank übergeben")
    assert rc == 0, err
    text = buch.read_text(encoding="utf-8")
    heute = date.today().isoformat()
    assert f"- **Stand**: {heute} — Status auf 'an Frank übergeben' gesetzt" in text
    assert text.count("- **Stand**:") == 1, text


def test_set_legt_eine_fehlende_stand_zeile_an(tmp_path):
    buch = _buch(tmp_path)
    rc, _, err = _cli("--pfad", str(buch), "set", "HM-4", "erledigt (Frank-Fix, abc)")
    assert rc == 0, err
    zeilen = buch.read_text(encoding="utf-8").splitlines()
    i = zeilen.index("- **Status**: erledigt (Frank-Fix, abc)")
    assert zeilen[i + 1].startswith("- **Stand**: "), zeilen[i:i + 2]
    rc, out, err = _cli("--pfad", str(buch), "list")
    assert "HM-4\terledigt (Frank-Fix, abc)" in out, out


def test_set_auf_der_letzten_zeile_ohne_zeilenende(tmp_path):
    pfad = tmp_path / "beutebuch.md"
    pfad.write_text("# B\n\n## Funde\n\n### HM-1 — x\n- **Status**: offen",
                    encoding="utf-8")
    rc, _, err = _cli("--pfad", str(pfad), "set", "HM-1", "an Frank übergeben")
    assert rc == 0, err
    zeilen = pfad.read_text(encoding="utf-8").splitlines()
    assert zeilen[-2] == "- **Status**: an Frank übergeben", zeilen
    assert zeilen[-1].startswith("- **Stand**: "), zeilen


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

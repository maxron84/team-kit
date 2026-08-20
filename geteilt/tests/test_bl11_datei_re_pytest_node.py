"""BL-11: DATEI_RE verschluckte per Pytest-Node-ID referenzierte Dateien.

Aus dem Feld zurueckgespielt (dort BL-6, team-kit_project_platformer,
Kaskade 2 — real 12,00 USD an HM-4 verbrannt).

Eine im Fund-Block als `datei.py::test_x` referenzierte Datei wurde vom
Extraktor NICHT erkannt — der Doppelpunkt steht nicht in der Zeichenklasse, und
weil DATEI_RE Backticks an beiden Enden verlangt, scheiterte der Match
vollstaendig statt nur den Suffix wegzulassen. Folge: `beutebuch.py dateien`
meldete die Datei nicht, der Substanz-Anker `team_diff_beruehrt_fund` sah in
Franks Diff keine referenzierte Datei und rollte jeden Fix zurueck.

Real eingetreten an HM-4: neun Frank-Versuche und drei Axel-Akten fuer 12,00 USD,
ohne dass je eine Zeile Code ueberlebte — Axel schickte Frank in
`test_app_headless.py`, die nur als `test_app_headless.py::test_run_...`
referenziert war und deshalb nie in der Anker-Liste stand.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

WURZEL = Path(__file__).resolve().parent.parent.parent
TOOL = kit_pfad("tools", "beutebuch.py")


def _lade_modul():
    spec = importlib.util.spec_from_file_location("beutebuch_bl6", TOOL)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.mark.parametrize(
    "text, erwartet",
    [
        # Der eigentliche BL-6-Fall: Node-ID mit Methodenteil.
        ("siehe `tests/test_app_headless.py::test_run_beendet_bei_quit_event`",
         "tests/test_app_headless.py"),
        # Parametrisierte Node-ID (eckige Klammern im Suffix).
        ("siehe `tests/test_spieler.py::test_lauf[links]`", "tests/test_spieler.py"),
        # Doppelpunkt ohne Methodenteil.
        ("siehe `tests/test_welt.py::`", "tests/test_welt.py"),
        # Regression: der schlichte Fall darf sich NICHT veraendert haben.
        ("siehe `tests/test_spieler.py`", "tests/test_spieler.py"),
        ("siehe `src/platformer/app.py`", "src/platformer/app.py"),
        ("siehe `./smoke.sh`", "./smoke.sh"),
    ],
)
def test_datei_re_extrahiert_pfad_ohne_node_suffix(text, erwartet):
    modul = _lade_modul()
    assert modul.DATEI_RE.findall(text) == [erwartet]


def test_dateien_liefert_node_referenzierte_datei(tmp_path):
    """Ende-zu-Ende ueber die CLI: `dateien` muss den Pfad ausgeben.

    Der Unit-Test oben prueft den Regex; dieser prueft, dass der Pfad auch
    wirklich durch `block_text` -> `findall` -> stdout durchkommt. BL-1 hat
    gezeigt, dass genau diese Verdrahtung eigenstaendig kaputtgehen kann.
    """
    projekt = tmp_path / "projekt"
    (projekt / "team" / "tools").mkdir(parents=True)
    (projekt / "plans").mkdir()
    (projekt / "team" / "tools" / "beutebuch.py").write_text(
        TOOL.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (projekt / "plans" / "beutebuch.md").write_text(
        "# Beutebuch\n\n"
        "### HM-1 — Testfund\n"
        "- **Angreifer**: Harry\n"
        "- **Status**: an Frank uebergeben\n"
        "- **Realitaet**: siehe `tests/test_app_headless.py::test_irgendwas`\n",
        encoding="utf-8",
    )

    ergebnis = subprocess.run(
        [sys.executable, "team/tools/beutebuch.py", "dateien", "HM-1"],
        cwd=projekt, capture_output=True, text=True, check=True,
    )
    assert "tests/test_app_headless.py" in ergebnis.stdout.split()

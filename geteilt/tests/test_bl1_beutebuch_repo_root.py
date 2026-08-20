"""BL-1 — beutebuch.py muss die Projektwurzel aufloesen, nicht team/.

Das Werkzeug liegt in team/tools/, also ZWEI Ebenen unter der Wurzel. Mit einem
.parent zu wenig zeigte BEUTEBUCH auf team/plans/beutebuch.md — eine Datei, die
es nie gibt. `_lies_zeilen` liefert fuer eine fehlende Datei eine leere Liste,
also meldete das Werkzeug still "keine Funde" statt zu scheitern: `first` gab
Exit 1 zurueck, frank.sh schloss daraus "nichts zu tun", und die Vollautomatik
beendete die Fixphase in Runde 1 — obwohl drei Funde mit Status
'an Frank uebergeben' im Buch standen (Kaskade 1, 2026-08-01).

Der stille Pfad ist das Gefaehrliche: Die vorhandenen Werkzeug-Tests arbeiten
alle mit --pfad auf Fixtures und waren deshalb gruen, waehrend der Default-Pfad
— der einzige, den die Rollen-Skripte benutzen — ins Leere zeigte.

Laeuft im Kit-Repo UND im installierten Projekt: die ersten beiden Tests
brauchen kein echtes plans/, der dritte ueberspringt sich im Kit selbst.
"""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

WURZEL = Path(__file__).resolve().parent.parent.parent
TOOL = kit_pfad("tools", "beutebuch.py")

BEISPIEL_BUCH = """# Beutebuch

## Funde

### HM-1 — Beispielfund
- **Angreifer**: Harry
- **Status**: an Frank uebergeben
"""


def _lade_modul():
    spec = importlib.util.spec_from_file_location("beutebuch_bl1", TOOL)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_default_pfade_zeigen_auf_die_projektwurzel():
    modul = _lade_modul()
    assert modul.REPO_ROOT == WURZEL
    assert modul.BEUTEBUCH == WURZEL / "plans" / "beutebuch.md"
    assert modul.ARCHIV == WURZEL / "plans" / "beutebuch-archiv.md"


def test_default_pfad_findet_das_buch_unabhaengig_vom_arbeitsverzeichnis(tmp_path):
    """Miniatur-Projekt bauen und das Werkzeug OHNE --pfad aufrufen.

    Genau der Aufrufweg von frank.sh/axel.sh. Der Aufruf laeuft aus einem
    fremden Arbeitsverzeichnis, damit ein versehentlich cwd-relativer Default
    ebenfalls auffliegt.
    """
    projekt = tmp_path / "projekt"
    (projekt / "team" / "tools").mkdir(parents=True)
    (projekt / "plans").mkdir()
    shutil.copy(TOOL, projekt / "team" / "tools" / "beutebuch.py")
    (projekt / "plans" / "beutebuch.md").write_text(BEISPIEL_BUCH, encoding="utf-8")

    fremdes_cwd = tmp_path / "woanders"
    fremdes_cwd.mkdir()

    ergebnis = subprocess.run(
        [sys.executable, str(projekt / "team" / "tools" / "beutebuch.py"), "list"],
        cwd=fremdes_cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    )
    assert ergebnis.stdout.strip() == "HM-1\tan Frank uebergeben"


@pytest.mark.skipif(
    not (WURZEL / "plans" / "beutebuch.md").is_file(),
    reason="Kit-Repo selbst hat kein plans/ — gilt nur im installierten Projekt",
)
def test_im_projekt_zeigt_der_default_auf_eine_existierende_datei():
    """Im installierten Projekt muss der Default-Pfad eine echte Datei treffen.

    Faengt den Fall ab, dass Werkzeug und Beutebuch auseinanderlaufen (etwa
    weil TEAM_PLAN_ORDNER umgezogen wurde, ohne die Werkzeuge nachzuziehen).
    """
    modul = _lade_modul()
    assert modul.BEUTEBUCH.is_file()

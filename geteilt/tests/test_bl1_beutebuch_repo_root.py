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

BL-342: Dieselbe Gattung eine Ebene hoeher. Der Default-Pfad war `plans/`,
verdrahtet — mit einem anderen `TEAM_PLAN_ORDNER` zeigte er wieder ins Leere,
und der dritte Fall hier uebersprang sich genau dann, weil er
`plans/beutebuch.md` als Bedingung hatte. Die Pfade kommen jetzt aus dem
Planordner (Rueckfall `plans`, wie `plan_ordner()` in kosten.py); die Tests
setzen ihn ausdruecklich oder entfernen ihn, statt ihn aus der Sitzung zu erben
(Kit-BL-328).

Laeuft im Kit-Repo UND im installierten Projekt: die ersten drei Tests
brauchen kein echtes Planverzeichnis, der vierte ueberspringt sich im Kit.
"""
import importlib.util
import os
import re
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


def test_default_pfade_zeigen_auf_die_projektwurzel(monkeypatch):
    monkeypatch.delenv("TEAM_PLAN_ORDNER", raising=False)
    modul = _lade_modul()
    assert modul.REPO_ROOT == WURZEL
    assert modul.BEUTEBUCH == WURZEL / "plans" / "beutebuch.md"
    assert modul.ARCHIV == WURZEL / "plans" / "beutebuch-archiv.md"


def test_der_planordner_verschiebt_beide_pfade(monkeypatch):
    """BL-342: Buch UND Archiv folgen dem Planordner — so, wie die
    Konfiguration ihn exportiert, mit abschliessendem Schraegstrich."""
    monkeypatch.setenv("TEAM_PLAN_ORDNER", "docs/plans/")
    modul = _lade_modul()
    assert modul.BEUTEBUCH == WURZEL / "docs" / "plans" / "beutebuch.md"
    assert modul.ARCHIV == WURZEL / "docs" / "plans" / "beutebuch-archiv.md"


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

    umgebung = {k: v for k, v in os.environ.items() if k != "TEAM_PLAN_ORDNER"}
    ergebnis = subprocess.run(
        [sys.executable, str(projekt / "team" / "tools" / "beutebuch.py"), "list"],
        cwd=fremdes_cwd, env=umgebung, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True,
    )
    assert ergebnis.stdout.strip() == "HM-1\tan Frank uebergeben"


def _konfigurierter_planordner():
    """Der Planordner, den die Installation eingetragen hat — statisch gelesen,
    denn `team-test.*` laedt die Konfiguration bewusst nicht. Beide Formen,
    damit auch eine `--nur-pwsh`-Ablage geprueft wird."""
    for name, muster in (
            ("team.config.sh",
             r'^TEAM_PLAN_ORDNER="\$\{TEAM_PLAN_ORDNER:-([^}]*)\}"'),
            ("team.config.ps1",
             r"^\$TEAM_PLAN_ORDNER\s*=\s*Team-Wert\s+'TEAM_PLAN_ORDNER'\s+'([^']*)'")):
        konfig = WURZEL / name
        if konfig.is_file():
            treffer = re.search(muster, konfig.read_text(encoding="utf-8-sig"),
                                re.MULTILINE)
            if treffer:
                return treffer.group(1)
    return None


def test_im_projekt_zeigt_der_default_auf_eine_existierende_datei(monkeypatch):
    """Im installierten Projekt muss der Default-Pfad eine echte Datei treffen.

    Faengt den Fall ab, dass Werkzeug und Beutebuch auseinanderlaufen (etwa
    weil TEAM_PLAN_ORDNER umgezogen wurde, ohne die Werkzeuge nachzuziehen).

    BL-342: Bis hierher war die Bedingung `plans/beutebuch.md existiert` — in
    einem Projekt mit anderem Planordner sprang der Waechter also genau dann
    ab, wenn er gebraucht wurde. Jetzt gilt der eingetragene Planordner.
    """
    if (WURZEL / "bootstrap" / "CLAUDE.md.vorlage").is_file():
        pytest.skip("Kit-Repo selbst hat kein Planverzeichnis — gilt nur im "
                    "installierten Projekt")
    ordner = _konfigurierter_planordner()
    if ordner is None:
        pytest.skip("keine Konfiguration mit lesbarem TEAM_PLAN_ORDNER in "
                    "dieser Ablage")
    monkeypatch.setenv("TEAM_PLAN_ORDNER", ordner)
    modul = _lade_modul()
    assert modul.BEUTEBUCH.is_file(), (
        f"Mit dem eingetragenen Planordner {ordner!r} zeigt beutebuch.py auf "
        f"{modul.BEUTEBUCH} — dort liegt kein Beutebuch. Die Rollen meldeten "
        f"'nichts zu tun' (Kit-BL-1, Kit-BL-342).")

#!/usr/bin/env python3
"""BL-28/BL-29/BL-22: Ein quittierter Fund ohne wirksamen Regressionstest.

Drei Funde, eine Luecke an drei Stellen:

BL-28 — Der Substanz-Anker `team_diff_beruehrt_fund` prueft "irgendeine im
Fund genannte Datei" statt "die reservierte". Im Feld reservierte HM-30
`tests/test_hm30_….py`, Franks Fix beruehrte CHANGELOG und Produktivdatei, die
Testdatei entstand NIE — der Anker war erfuellt, weil die Produktivdatei im
Fundblock steht. Damit ist die Absicherung genau dort wirkungslos, wo BL-15 sie
einfuehren wollte.

BL-29 — Es gab keine Vorpruefung des Fundblocks, bevor Frank gerufen wird. Im
Feld nannte ein Block die Fundstelle als `pfad::testname`; der Anker erkannte
keine Datei, Franks inhaltlich KORREKTER Fix wurde zurueckgesetzt und als
Fehlversuch gezaehlt. Ein vollstaendiger Frank-Lauf fuer einen Formfehler im
Auftrag.

BL-22 — Ein Reproducer unter `xfail(strict=False)` kann die Suite nie rot
machen, und keine Regel verpflichtete Frank, ihn beim Fixen zu entschaerfen.
Gemessen im Feld: Fix zurueckgedreht ⇒ Suite byte-identisch gruen.

Geprueft wird hier die MECHANIK (lint/reproducer/Anker) und die AUSGELIEFERTE
Regel — beide Haelften, denn eine ohne die andere traegt nicht.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import Ruf, kit_pfad, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]
TEAM_LIB = kit_pfad("lib.sh")
BEUTEBUCH_PY = kit_pfad("tools", "beutebuch.py")

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import beutebuch  # noqa: E402


def _buch(tmp_path, block):
    pfad = tmp_path / "beutebuch.md"
    pfad.write_text("# Beutebuch\n\n" + block, encoding="utf-8")
    return pfad


VOLLSTAENDIG = """### HM-30 — Parser verschluckt Zeilen
- **Status**: an Frank übergeben
- **Angreifer**: Harry
- **Fundstelle**: `src/parser.py`
- **Reproducer-Test**: `tests/test_hm30_parser.py`
"""


# --- BL-29: der Lint --------------------------------------------------------

def test_vollstaendiger_block_ist_sauber(tmp_path):
    assert beutebuch.lint("HM-30", _buch(tmp_path, VOLLSTAENDIG)) == []


def test_block_ohne_jeden_dateipfad_wird_gemeldet(tmp_path):
    """Der Feldfall aus BL-29: Der Block nennt keine Datei, die der
    Substanz-Anker fassen koennte — der Anker haette JEDEN Fix
    zurueckgenommen, und Frank haette den Fehlversuch getragen. Der Lint
    faengt es, BEVOR der Aufruf Geld kostet."""
    block = ("### HM-64 — Flaky\n"
             "- **Status**: an Frank übergeben\n"
             "- **Fundstelle**: die Suite flackert beim zweiten Durchlauf\n"
             "- **Reproducer-Test**: tests/test_hm64.py\n")
    maengel = beutebuch.lint("HM-64", _buch(tmp_path, block))
    assert any("Substanz-Anker" in m for m in maengel), maengel
    assert any("Backticks" in m for m in maengel), maengel


def test_fehlende_reproducer_zeile_wird_gemeldet(tmp_path):
    block = ("### HM-31 — X\n"
             "- **Status**: an Frank übergeben\n"
             "- **Fundstelle**: `src/a.py`\n")
    maengel = beutebuch.lint("HM-31", _buch(tmp_path, block))
    assert any("Reproducer-Test" in m for m in maengel)


def test_reproducer_ohne_backticks_wird_gemeldet(tmp_path):
    block = ("### HM-32 — X\n"
             "- **Status**: an Frank übergeben\n"
             "- **Fundstelle**: `src/a.py`\n"
             "- **Reproducer-Test**: tests/test_hm32.py\n")
    maengel = beutebuch.lint("HM-32", _buch(tmp_path, block))
    assert any("Backticks" in m for m in maengel)


def test_fehlende_statuszeile_wird_gemeldet(tmp_path):
    block = ("### HM-33 — X\n"
             "- **Fundstelle**: `src/a.py`\n"
             "- **Reproducer-Test**: `tests/test_hm33.py`\n")
    maengel = beutebuch.lint("HM-33", _buch(tmp_path, block))
    assert any("Status" in m for m in maengel)


def test_cli_liefert_exit_3_und_meldet_nach_stderr(tmp_path):
    block = ("### HM-31 — X\n"
             "- **Status**: an Frank übergeben\n"
             "- **Fundstelle**: `src/a.py`\n")
    pfad = _buch(tmp_path, block)
    ergebnis = subprocess.run(
        [sys.executable, str(BEUTEBUCH_PY), "--pfad", str(pfad), "lint", "HM-31"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert ergebnis.returncode == 3
    assert "Reproducer-Test" in ergebnis.stderr
    assert ergebnis.stdout == ""


def test_cli_ist_still_und_null_bei_sauberem_block(tmp_path):
    pfad = _buch(tmp_path, VOLLSTAENDIG)
    ergebnis = subprocess.run(
        [sys.executable, str(BEUTEBUCH_PY), "--pfad", str(pfad), "lint", "HM-30"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert ergebnis.returncode == 0
    assert ergebnis.stderr == ""


# --- BL-28: der Anker auf der reservierten Datei ----------------------------

def test_reproducer_verb_liefert_genau_den_reservierten_pfad(tmp_path):
    pfad = _buch(tmp_path, VOLLSTAENDIG)
    ergebnis = subprocess.run(
        [sys.executable, str(BEUTEBUCH_PY), "--pfad", str(pfad),
         "reproducer", "HM-30"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert ergebnis.returncode == 0
    assert ergebnis.stdout.strip() == "tests/test_hm30_parser.py", \
        "nicht die Produktivdatei, sondern die reservierte Testdatei"


def _lib_repo(tmp_path, schale):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "plans").mkdir()
    schale.lib_kopieren(repo)
    shutil.copy(BEUTEBUCH_PY, repo / "team" / "tools" / "beutebuch.py")
    schale.config_schreiben(repo, {
        "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
        "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
        "TEAM_DOMAENEN": "produkt",
    })
    (repo / "plans" / "beutebuch.md").write_text(
        "# Beutebuch\n\n" + VOLLSTAENDIG, encoding="utf-8")
    return repo


def _reproducer_liegt_vor(schale, repo, hm="HM-30"):
    """Nur der Exit-Code zaehlt — der Anker meldet nichts, er urteilt."""
    return schale.lauf(Ruf("team_reproducer_liegt_vor", hm), cwd=repo,
                       lib=repo / "team" / schale.lib_name).returncode


def test_anker_faellt_wenn_die_reservierte_datei_fehlt(tmp_path, schale):
    """Der Feldfall: Der Fix beruehrte Produktivdatei und CHANGELOG, die
    reservierte Testdatei entstand nie."""
    repo = _lib_repo(tmp_path, schale)
    assert _reproducer_liegt_vor(schale, repo) == 1


def test_anker_besteht_wenn_sie_angelegt_wurde(tmp_path, schale):
    repo = _lib_repo(tmp_path, schale)
    (repo / "tests" / "test_hm30_parser.py").write_text("def test_x(): pass\n")
    assert _reproducer_liegt_vor(schale, repo) == 0


def test_fund_ohne_reproducer_zeile_blockiert_nicht(tmp_path, schale):
    """Kein falscher Blocker: Ohne Zeile ist der Lint zustaendig (vor dem
    Lauf), nicht dieser Anker (nach dem Lauf)."""
    repo = _lib_repo(tmp_path, schale)
    (repo / "plans" / "beutebuch.md").write_text(
        "# Beutebuch\n\n### HM-40 — X\n- **Status**: an Frank übergeben\n"
        "- **Fundstelle**: `src/a.py`\n", encoding="utf-8")
    assert _reproducer_liegt_vor(schale, repo, "HM-40") == 0


# --- BL-22: die ausgelieferte Regel -----------------------------------------

def _quelle(*kandidaten):
    """Kit-Ablage und installierte Ablage — die Regeldatei heisst hier
    bootstrap/CLAUDE.md.vorlage und dort CLAUDE.md."""
    for kandidat in kandidaten:
        pfad = REPO_ROOT / kandidat
        if pfad.is_file():
            return pfad
    raise AssertionError(f"keine der Quellen existiert: {kandidaten}")


@pytest.mark.parametrize("traeger", [
    ("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md"),
    ("geteilt/prompts/rolle-harry.md", "team/prompts/rolle-harry.md",),
    ("geteilt/prompts/rolle-marv.md", "team/prompts/rolle-marv.md",),
], ids=["Regeldatei", "rolle-harry", "rolle-marv"])
def test_briefings_verlangen_strict(traeger):
    """Ohne `strict` sind BEIDE Ausgaenge stumm — der Fehlschlag zaehlt als
    erwartet, der Erfolg als xpass, die Suite bleibt gruen."""
    quelle = _quelle(*traeger)
    text = quelle.read_text(encoding="utf-8")
    assert "strict=True" in text, f"{quelle.name} nennt keinen strict-Wert"


def test_franks_dreisatz_nennt_die_gegenprobe():
    """Die zweite Haelfte, ohne die die erste sogar SCHAEDLICH ist: Wird der
    Test nach dem Fix erwartungsgemaess gruen, faerbt er als xpass unter
    strict=True die Suite rot — Frank entfernt den Marker dann AUS NOT, ohne
    je die Gegenprobe zu fahren. Die Gegenprobe ist der Kern, nicht der
    Marker."""
    text = _quelle("geteilt/prompts/rolle-frank.md", "team/prompts/rolle-frank.md").read_text(encoding="utf-8")
    assert "Reproducer" in text, "Franks Dreisatz nennt den Reproducer nicht"
    assert "rot" in text and "Gegenprobe" in text, \
        "die Pflicht zur Gegenprobe (ohne Fix muss der Test rot sein) fehlt"

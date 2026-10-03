#!/usr/bin/env python3
"""BL-289: Ein Fund behauptete das Ergebnis eines Befehls, ohne ihn
auszufuehren — und Punkt 3 des Beutezug-Dreisatzes deckte das dem Wortlaut
nach nicht.

DER FELDBEFUND (`Feld F`, 2026-09-29)
    Harry meldete einen kritischen Fund, letzter Reproschritt: *„`python -m
    pytest <testdatei> -q` zeigt den roten Fall."* Ausgefuehrt hatte er ihn
    nicht; die Herleitung aus dem Kontrollfluss uebersah eine Datendatei. Der
    Test war gruen. Frank baute trotzdem eine harmlose Absicherung (1,42 USD,
    44 Turns, der teuerste Fix-Lauf dieser Fixphase), der Architekt musste
    den Fund widerlegen und den CHANGELOG berichtigen.

    Punkt 3 verlangte Belege nur fuer das Laufzeitverhalten einer
    SPRACHKONSTRUKTION (BL-215). Beim Ergebnis eines Befehls versagt Lesen
    genauso — und den Befehl auszufuehren kostet Sekunden.

WAS DIESER TEST PRUEFT
    1. Die Regel steht in beiden Red-Team-Briefings und in der Regeldatei.
    2. Die Gegenprobe aus der Meldung: `beutebuch.py lint` gibt einen
       HINWEIS, wenn ein Fund VOR dem Fix einen Testbefehl nennt, aber keine
       Ausgabe zitiert. Ein Hinweis, kein Mangel: Er sperrt Frank nicht
       (Exit 0). Die Heuristik kann irren, und ein gesperrter echter Fund
       waere teurer als ein ueberlesener Hinweis.
"""
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if Path(_tools).is_dir():
        sys.path.insert(0, str(_tools))
        break
import beutebuch  # noqa: E402

BEUTEBUCH_PY = kit_pfad("tools", "beutebuch.py")

KOPF = "# Beutebuch\n\n## Funde\n\n"

# Der Feldfall, auf seine Form gebracht.
BEHAUPTET = """### HM-1 — Roter Fall behauptet

- **Status**: {status}
- **Fundstelle**: `src/modul.py`
- **Repro**: `python -m pytest tests/test_modul.py -q` zeigt den roten Fall.
- **Reproducer-Test**: `tests/test_hm1_roter_fall.py`

"""

BELEGT = """### HM-1 — Roter Fall belegt

- **Status**: an Frank übergeben
- **Fundstelle**: `src/modul.py`
- **Repro**: `python -m pytest tests/test_modul.py -q` zeigt den roten Fall:

```
FAILED tests/test_modul.py::test_grenze - AssertionError: 3 != 4
1 failed in 0.12s
```
- **Reproducer-Test**: `tests/test_hm1_roter_fall.py`

"""


def _buch(pfad, inhalt):
    pfad.write_text(KOPF + inhalt, encoding="utf-8")
    return pfad


def _cli(*args):
    r = subprocess.run([sys.executable, str(BEUTEBUCH_PY), *args],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout, r.stderr


# --- Die Regel --------------------------------------------------------------

@pytest.mark.parametrize("rolle", ["harry", "marv"])
def test_das_briefing_verlangt_den_beleg(rolle):
    text = kit_pfad("prompts", f"rolle-{rolle}.md").read_text(encoding="utf-8")
    assert ("Kit-BL-289" in text and "ausgeführt habe" in text
            and "Erwartung" in text), (
        f"rolle-{rolle}.md verlangt fuer ein behauptetes Befehlsergebnis "
        f"keinen Beleg (BL-289).")


def test_die_regeldatei_verlangt_den_beleg():
    vorlage = REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage"
    if not vorlage.exists():
        pytest.skip("Kit-Wurzel: die Regeldatei-Vorlage liegt nur im Kit")
    text = vorlage.read_text(encoding="utf-8")
    assert "führt er ihn aus und zitiert die Ausgabe" in text
    assert "Kit-BL-289" in text


# --- Die Gegenprobe -----------------------------------------------------------

@pytest.mark.parametrize("status", ["offen", "an Frank übergeben"])
def test_lint_weist_auf_den_unbelegten_befehl_hin(tmp_path, status):
    """Der Feldfall: ein Testbefehl, keine Ausgabe."""
    buch = _buch(tmp_path / "beutebuch.md", BEHAUPTET.format(status=status))
    rc, _, err = _cli("--pfad", str(buch), "lint", "HM-1")
    assert "Kit-BL-289" in err and "[HM-1]" in err, (
        f"Kein Hinweis auf den unbelegten Testbefehl (BL-289):\n{err}")
    assert rc == 0, (
        f"Der Hinweis SPERRT den Fund (rc={rc}) — Frank bekaeme Exit 5, "
        f"obwohl der Block formal brauchbar ist.\n{err}")


def test_lint_ohne_nummer_weist_ebenfalls_hin(tmp_path):
    buch = _buch(tmp_path / "beutebuch.md", BEHAUPTET.format(status="offen"))
    rc, _, err = _cli("--pfad", str(buch), "lint")
    assert rc == 0, err
    assert "[HM-1]" in err and "Kit-BL-289" in err, err


def test_eine_zitierte_ausgabe_schweigt(tmp_path):
    """Gegenrichtung: Eine Meldung, die immer kommt, ist keine (BL-14)."""
    buch = _buch(tmp_path / "beutebuch.md", BELEGT)
    rc, _, err = _cli("--pfad", str(buch), "lint", "HM-1")
    assert rc == 0, err
    assert "Kit-BL-289" not in err, f"Hinweis trotz zitierter Ausgabe:\n{err}"


def test_ein_erledigter_fund_schweigt(tmp_path):
    """Nach dem Fix ist der Hinweis nichts mehr wert — und ueber `--alle`
    liefe er sonst ueber den ganzen Bestand."""
    buch = _buch(tmp_path / "beutebuch.md", BEHAUPTET.format(
        status="erledigt (Frank-Fix, abc1234)"))
    rc, _, err = _cli("--pfad", str(buch), "lint")
    assert rc == 0, err
    assert "Kit-BL-289" not in err, err


@pytest.mark.parametrize("erwaehnung", [
    "`pytest.raises` faengt die Ausnahme nicht",   # ein Name, kein Befehl
    "die Konfiguration in `pytest.ini`",
    "`tests/test_pytest_grenze.py` deckt das ab",
])
def test_eine_blosse_erwaehnung_ist_kein_befehl(erwaehnung):
    text = BEHAUPTET.format(status="offen").replace(
        "`python -m pytest tests/test_modul.py -q` zeigt den roten Fall.",
        erwaehnung)
    assert beutebuch.hinweise_text(text) == [], erwaehnung


@pytest.mark.parametrize("befehl", [
    "`python -m pytest tests/test_modul.py -q`",
    "`python3 -m pytest -x`",
    "`pytest tests/`",
    "`npm test`",
    "`dotnet test`",
    "`go test ./...`",
    "`cargo test grenze`",
    "`Invoke-Pester ./tests`",
])
def test_gaengige_testbefehle_werden_erkannt(befehl):
    text = BEHAUPTET.format(status="offen").replace(
        "`python -m pytest tests/test_modul.py -q`", befehl)
    assert beutebuch.hinweise_text(text), befehl


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

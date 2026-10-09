#!/usr/bin/env python3
"""BL-324: Mit Red-Team-Fokus verlangte Franks Auftrag die Suite nur fuer
`TEAM_PRODUKTIVCODE` — ein Fix unter `TEAM_WEITERER_CODE` lief ohne Gate.

WAS GEMELDET WURDE (`Feld B`, 2026-10-09)
    Ohne Fokus heisst Schritt 1 *„Code-Fix unter <Produktivcode> (oder …
    <weiterer Code>) umsetzen"*, und der Smoke-Test gilt unbedingt. Mit Fokus
    haengt er an *„Betrifft der Fix <Produktivcode>, zusaetzlich: …"*. Frank
    fixte einen Fund im zweiten Produktteil, fuhr nur den Reproducer und
    quittierte woertlich nach dieser Bedingung. Die volle Suite haette gezeigt,
    dass der Fund ein Fehlalarm war.

WARUM DER FOKUS-FALL DER NORMALFALL IST
    Die Vollautomatik setzt den Fokus fuer den ganzen Lauf — die Fassung mit
    Fokus ist also die jeder Fixphase, die ohne nur der Einzelaufruf von Hand.
    Die Rolle sieht nur eine der beiden Fassungen und kann den Widerspruch
    nicht bemerken.

WIE HIER GEMESSEN WIRD
    Am abgesetzten PROMPT, nicht am Quelltext: Ein Stub tritt an die Stelle
    der CLI und faengt sein `-p`-Argument (Bauart aus `BL-117`). Beide
    Fassungen auf jeder vorhandenen Bahn — die Achse ist die MENGE der Zweige,
    ein Test fuer nur einen haette die Luecke nicht gesehen.
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (entrypoint_aufruf, ueberspringe_ohne_bahn,  # noqa: E402
                      verlange_bash, verlange_pwsh)
import test_bl117_prompt_gleichstand_am_lauf as lauf  # noqa: E402

WURZEL = Path(__file__).resolve().parents[2]
WEITERER = "werkzeuge/ start.py"
FOKUS = "Die Exportsperre der Kaskade 9"
# Als Tupel: Eine Liste, die mit "bash" beginnt, haelt der Waechter aus
# BL-130 zu Recht fuer einen Aufruf ueber den WSL-Launcher.
BAHNEN = ("bash", "pwsh")


def _verlange_ablage(bahn):
    endung = ".sh" if bahn == "bash" else ".ps1"
    for name in (f"frank{endung}", f"team.config{endung}"):
        if not (WURZEL / name).is_file():
            pytest.skip(f"{name} liegt nur in der INSTALLIERTEN Ablage")
    ueberspringe_ohne_bahn(bahn)
    (verlange_bash if bahn == "bash" else verlange_pwsh)()


def _prompt(tmp_path, bahn, fokus):
    """Faehrt Frank einmal mit Stub-CLI und gibt den gefangenen Prompt."""
    repo = lauf._projekt(tmp_path)
    fang = tmp_path / f"prompt-{bahn}-{'fokus' if fokus else 'ohne'}.txt"
    if bahn == "bash":
        stub = tmp_path / "claude-stub.sh"
        stub.write_text(lauf.BASH_STUB.format(antwort=lauf.ANTWORT),
                        encoding="utf-8", newline="\n")
        stub.chmod(0o755)
        befehl = entrypoint_aufruf(repo / "frank.sh")
    else:
        stub = tmp_path / "claude-stub.ps1"
        stub.write_text(lauf.PWSH_STUB.format(antwort=lauf.ANTWORT),
                        encoding="utf-8-sig", newline="\n")
        befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                  str(repo / "frank.ps1")]
    umgebung = lauf._umgebung(repo, fang)
    umgebung["TEAM_CLAUDE_BIN"] = str(stub)
    umgebung["TEAM_WEITERER_CODE"] = WEITERER
    # Ohne Smoke-Test ist der Nachsatz leer, und die Bedingung haette nichts,
    # woran sie haengt — eine frische Installation hat noch keinen.
    umgebung["TEAM_SMOKE_TEST"] = "python -m pytest tests -q"
    if fokus:
        umgebung["TEAM_REDTEAM_FOCUS"] = FOKUS
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    if not fang.is_file():
        pytest.fail(f"Frank hat auf der {bahn}-Bahn keinen Prompt abgesetzt "
                    f"(Exit {r.returncode}).\n{r.stdout}\n{r.stderr}")
    return fang.read_text(encoding="utf-8")


def _schritt1(prompt):
    """Die Zeile `1. Code-Fix …` des Dreisatzes. Das Briefing davor hat eigene
    nummerierte Listen — gesucht wird deshalb der Schritt, nicht die Nummer."""
    for zeile in prompt.splitlines():
        if zeile.startswith("1. Code-Fix"):
            return zeile
    pytest.fail("Der Prompt hat keinen Schritt 1 'Code-Fix':\n" + prompt[-3000:])


@pytest.mark.parametrize("bahn", BAHNEN)
def test_mit_fokus_gilt_der_smoke_test_auch_fuer_weiteren_code(tmp_path, bahn):
    """Der Feldfall. Gegen den alten Stand gemessen: Die Bedingung nannte nur
    den Produktivcode."""
    _verlange_ablage(bahn)
    schritt = _schritt1(_prompt(tmp_path, bahn, fokus=True))
    assert FOKUS in schritt, "die Fokus-Fassung wurde gar nicht gewaehlt"
    bedingung = schritt.split("Betrifft der Fix", 1)
    assert len(bedingung) == 2, f"keine Bedingung im Schritt 1: {schritt}"
    bedingung = bedingung[1].split("zusätzlich:", 1)[0]
    assert WEITERER in bedingung, (
        "Mit Fokus haengt der Smoke-Test an einer Bedingung, die "
        "TEAM_WEITERER_CODE nicht nennt — ein Fix dort laeuft im Normalfall "
        f"der Fixphase ohne Suite (Kit-BL-324).\nSchritt 1: {schritt[:400]}")
    assert "Smoke-Test grün" in schritt


@pytest.mark.parametrize("bahn", BAHNEN)
def test_ohne_fokus_gilt_er_weiter_unbedingt(tmp_path, bahn):
    """Die andere Fassung derselben Achse: unveraendert unbedingt, und sie
    nennt dieselben Orte."""
    _verlange_ablage(bahn)
    schritt = _schritt1(_prompt(tmp_path, bahn, fokus=False))
    assert "Betrifft der Fix" not in schritt, schritt[:400]
    assert WEITERER in schritt and "Smoke-Test grün" in schritt, schritt[:400]


@pytest.mark.parametrize("bahn", BAHNEN)
def test_ohne_weiteren_code_bleibt_die_bedingung_schlicht(tmp_path, bahn,
                                                          monkeypatch):
    """Gegenprobe: Ein leeres TEAM_WEITERER_CODE darf keine leere Klammer
    hinterlassen ("src/ (oder )")."""
    _verlange_ablage(bahn)
    monkeypatch.setattr(sys.modules[__name__], "WEITERER", "")
    schritt = _schritt1(_prompt(tmp_path, bahn, fokus=True))
    assert "(oder )" not in schritt and "(oder)" not in schritt, schritt[:400]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

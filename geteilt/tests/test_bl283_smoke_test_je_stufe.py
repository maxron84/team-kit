#!/usr/bin/env python3
"""BL-283: Erste Kaskade — Ralph berechnete die Smoke-Zeile einmal je LAUF;
die Stufen nach Stufe 1 bauten ohne Smoke-Test.

WAS IM FELD AUFFIEL (`Feld F`, 2026-09-26, beim Aushaerten der ersten Kaskade)
    Das Architekten-Briefing verlangt, dass Stufe 1 der ersten Kaskade den
    Smoke-Test baut und in `team.config.*` eintraegt. `SMOKE_ZEILE` und
    `SMOKE_SUFFIX` entstanden aber beim LADEN der Bibliothek, und Ralph laedt
    sie einmal und faehrt dann alle Stufen. Die Stufen 2…N desselben Laufs
    bekamen „Kein Smoke-Test konfiguriert — Schritt entfaellt"; dieselbe
    Ladezeit traf die BL-41-Selbstpruefung, und Ralphs Briefing trug den beim
    Installieren gerenderten Satz „noch KEIN Smoke-Test" — im selben Prompt
    wie die Konfiguration, der er widersprach. Deterministisch in der ersten
    Kaskade jedes Projekts, und danach unsichtbar.

WAS GEBAUT IST
    `team_smoke_bausteine` baut die Zeilen (beim Laden wie bisher),
    `team_smoke_auffrischen` liest TEAM_SMOKE_TEST je Stufe nach, solange
    noch keiner bekannt ist, und `team_briefing ralph` ersetzt den
    Installationssatz zur Laufzeit. Ein schon bekannter Wert bleibt — ein
    Lauf wechselt ein laufendes Sicherheitsnetz nicht still aus.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (REPO_ROOT, Ausgabe, Ruf, Schreib, Variable,  # noqa: E402
                      entrypoint_pfad, nur_code)

FEHLT = ("Fuer dieses Projekt ist noch KEIN Smoke-Test konfiguriert. Ihn zu "
         "bauen ist Aufgabe von Stufe 1 dieser Kaskade; bis dahin entfaellt "
         "der Schritt, und ich erfinde keinen Befehl.")


def _konfig_text(schale, smoke):
    if schale.name == "bash":
        return f'TEAM_SMOKE_TEST="{smoke}"\n' if smoke else ""
    return f'$TEAM_SMOKE_TEST = "{smoke}"\n' if smoke else ""


def _projekt(tmp_path, schale, smoke=""):
    (tmp_path / "team").mkdir()
    lib = schale.lib_kopieren(tmp_path)
    (tmp_path / f"team.config{schale.endung}").write_text(
        _konfig_text(schale, smoke), encoding="utf-8")
    return lib


def test_eine_in_stufe_1_eingetragene_konfiguration_kommt_an(tmp_path, schale):
    """Der Feldfall: Beim Laden ist kein Smoke-Test da, dann traegt Stufe 1
    ihn ein — die Bausteine der naechsten Stufe muessen ihn nennen."""
    lib = _projekt(tmp_path, schale)
    r = schale.lauf([
        Variable("SMOKE_ZEILE"),
        Schreib(f"team.config{schale.endung}",
                _konfig_text(schale, "./smoke.sh")),
        Ruf("team_smoke_auffrischen"),
        Variable("SMOKE_ZEILE", "SMOKE_SUFFIX", trenner="\n---\n"),
    ], cwd=tmp_path, lib=lib, env={"TEAM_SMOKE_TEST": ""})
    assert r.returncode == 0, r.stderr
    vorher, _, nachher = r.stdout.partition("Smoke-Test ausführen")
    assert "Kein Smoke-Test konfiguriert" in vorher, (
        f"Vorbedingung: beim Laden ist noch keiner da.\n{r.stdout}")
    assert "./smoke.sh" in nachher, (
        f"{schale.name}: Die Smoke-Zeile nennt den in Stufe 1 eingetragenen "
        f"Befehl nicht — die Folgestufen bauen ohne Sicherheitsnetz "
        f"(BL-283).\n{r.stdout}")
    assert "BL-283" in r.stderr, "Das Auffrischen soll im Log stehen."


def test_ein_bekannter_wert_wird_nicht_still_ausgewechselt(tmp_path, schale):
    lib = _projekt(tmp_path, schale, smoke="./a.sh")
    r = schale.lauf([
        Schreib(f"team.config{schale.endung}", _konfig_text(schale, "./b.sh")),
        Ruf("team_smoke_auffrischen"),
        Variable("SMOKE_ZEILE"),
    ], cwd=tmp_path, lib=lib)
    assert r.returncode == 0, r.stderr
    assert "./a.sh" in r.stdout and "./b.sh" not in r.stdout, r.stdout


def test_das_briefing_widerspricht_der_konfiguration_nicht(tmp_path, schale):
    lib = _projekt(tmp_path, schale, smoke="./smoke.sh")
    (tmp_path / "team" / "prompts").mkdir()
    (tmp_path / "team" / "prompts" / "rolle-ralph.md").write_text(
        f"# Ralph\n\n- {FEHLT}\n- eine andere Grenze\n", encoding="utf-8")
    r = schale.lauf([Ausgabe("team_briefing", "ralph")], cwd=tmp_path, lib=lib)
    assert r.returncode == 0, r.stderr
    assert "KEIN Smoke-Test" not in r.stdout, (
        f"{schale.name}: Ralphs Briefing behauptet weiter, es gebe keinen "
        f"Smoke-Test — im selben Prompt, der ihn nennt (BL-283).\n{r.stdout}")
    assert "- Der Smoke-Test (`./smoke.sh`) muss gruen sein" in r.stdout
    assert "- eine andere Grenze" in r.stdout, "der Rest bleibt, wie er ist"


def test_ohne_smoke_test_bleibt_das_briefing_wie_installiert(tmp_path, schale):
    lib = _projekt(tmp_path, schale)
    (tmp_path / "team" / "prompts").mkdir()
    (tmp_path / "team" / "prompts" / "rolle-ralph.md").write_text(
        f"# Ralph\n\n- {FEHLT}\n", encoding="utf-8")
    r = schale.lauf([Ausgabe("team_briefing", "ralph")], cwd=tmp_path, lib=lib,
                    env={"TEAM_SMOKE_TEST": ""})
    assert FEHLT in r.stdout, r.stdout


@pytest.mark.parametrize("datei", ["bash/install.sh", "pwsh/install.ps1"])
def test_der_installer_rendert_den_satz_den_das_briefing_sucht(datei):
    """Die Ersetzung haengt am Wortlaut des Installers. Aendert ihn jemand,
    muss dieser Fall rot werden statt die Ersetzung still ins Leere laufen."""
    pfad = REPO_ROOT / datei
    if not pfad.is_file():
        pytest.skip("die Installer liegen nur im Kit")
    assert "Fuer dieses Projekt ist noch KEIN Smoke-Test konfiguriert." in \
        pfad.read_text(encoding="utf-8-sig")


@pytest.mark.parametrize("datei", ["ralph.sh", "ralph.ps1"])
def test_ralph_frischt_je_stufe_auf(datei):
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    code = nur_code(pfad.read_text(encoding="utf-8-sig"))
    schleife = code.index("while true" if datei.endswith(".sh") else "while ($true)")
    prompt = code.index("team_briefing", schleife)
    assert "team_smoke_auffrischen" in code[schleife:prompt], (
        f"{datei}: Die Stufenschleife frischt den Smoke-Test nicht vor dem "
        f"Prompt auf (BL-283).")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

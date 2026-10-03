#!/usr/bin/env python3
"""BL-264: Fahren die Rollen das neueste Modell ihrer Familie? Im Feld lief
jeder Loop-Lauf auf einer aelteren Sonnet-Version — und nichts zeigte es an.

WAS IM FELD PASSIERT IST (`Feld F`, 2026-09-27 bis 2026-09-30)
    Alle 126 Rollenlaeufe ueber fuenf Kaskaden nennen in `modelUsage` nur
    `claude-sonnet-5`, obwohl das Abo `claude-sonnet-5-5` hatte. Die CLI im
    PATH (2.1.283), die der Loop ruft, loeste `sonnet` anders auf als die
    IDE-gebuendelte daneben (2.1.285). Eine Feldprobe hat es am selben Tag
    geklaert: Die ALIAS-TABELLE DER CLI-VERSION entscheidet, nicht das Abo.
    Das Modell stand nur in den Rohlogs — weder im Bericht noch im Ledger, und
    die Kosten sahen plausibel aus.

WAS GEBAUT IST
    `kosten.py modelle [DIR...] [--cli BEFEHL]` nennt je Rolle das Hauptmodell
    der Logs, WARNT, wenn die Preistabelle eine neuere Version derselben
    Familie kennt, und vergleicht mit --cli die Version der CLI des Loops mit
    der neuesten IDE-gebuendelten. `team-status` zeigt das im Abschnitt
    „Modell & CLI" auf beiden Bahnen — und damit auch der Abschlussbericht,
    der `team-status` aufruft.

WARUM DIE PREISTABELLE DIE QUELLE IST
    Sie ist die eine Liste, die das Kit fuer ein neues Modell ohnehin
    nachziehen muss (sonst rechnet es falsch, BL-302). Eine zweite Liste nur
    fuer „was ist das neueste" wuerde lautlos veralten — die Bauart, gegen
    die das halbe Kit steht.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import entrypoint_pfad, kit_pfad

for _tools in (Path(__file__).resolve().parents[2] / "geteilt" / "tools",
               kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")


def _log(ordner, name, modelle):
    """Ein Rollenlog mit `modelUsage` {modell: (costUSD, outputTokens)}."""
    ordner.mkdir(parents=True, exist_ok=True)
    nutzung = {m: {"costUSD": c, "outputTokens": o, "inputTokens": 1}
               for m, (c, o) in modelle.items()}
    (ordner / name).write_text(json.dumps({
        "total_cost_usd": sum(c for c, _ in modelle.values()),
        "num_turns": 3, "modelUsage": nutzung}), encoding="utf-8")


def _cli(ordner, version):
    """Eine CLI, die nur ihre Version sagt — ohne Netz, ohne Kosten."""
    ordner.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        pfad = ordner / "claude.cmd"
        pfad.write_text(f"@echo {version} (Claude Code)\r\n", encoding="utf-8")
    else:
        pfad = ordner / "claude"
        pfad.write_text(f"#!/bin/sh\necho '{version} (Claude Code)'\n",
                        encoding="utf-8")
        pfad.chmod(0o755)
    return str(pfad)


def _ide(heim, *versionen):
    for v in versionen:
        binaer = (heim / ".vscode" / "extensions"
                  / f"anthropic.claude-code-{v}-win32-x64" / "resources"
                  / "native-binary" / "claude.exe")
        binaer.parent.mkdir(parents=True, exist_ok=True)
        binaer.write_bytes(b"")


# --- Lesen: Familie und Version -----------------------------------------------

@pytest.mark.parametrize("modell,erwartet", [
    ("claude-sonnet-5-5", ("sonnet", (5, 5))),
    ("claude-sonnet-5", ("sonnet", (5, 0))),
    ("claude-opus-5-20260101", ("opus", (5, 0))),
    ("claude-haiku-4-5-20251001", ("haiku", (4, 5))),
    ("anthropic.claude-opus-5-5", ("opus", (5, 5))),
    ("gpt-5", None),
])
def test_modell_version(modell, erwartet):
    assert kosten.modell_version(modell) == erwartet


def test_die_neueste_bekannte_sonnet_ist_5_5():
    assert kosten.neueste_bekannte_version("sonnet")[0] == "claude-sonnet-5-5"
    assert kosten.neueste_bekannte_version("opus")[0] == "claude-opus-5-5"


def test_das_hauptmodell_ist_nicht_das_hilfsmodell():
    """Die CLI ruft fuer Nebenarbeit ein kleines Modell mit; im Feld stand
    neben dem Rollenmodell regelmaessig Haiku im Log."""
    nutzung = {"claude-haiku-4-5": {"costUSD": 0.002, "outputTokens": 40},
               "claude-sonnet-5": {"costUSD": 0.80, "outputTokens": 900}}
    assert kosten.hauptmodell(nutzung) == "claude-sonnet-5"


# --- Der Fall aus dem Feld ----------------------------------------------------

def test_eine_aeltere_version_wird_gewarnt(tmp_path):
    _log(tmp_path / ".ralph-logs", "stufe-3-20260927-100000.json",
         {"claude-sonnet-5": (1.2, 500), "claude-haiku-4-5": (0.01, 5)})
    _log(tmp_path / ".team-logs", "frank-HM-4-v1-20260927-110000.json",
         {"claude-sonnet-5": (0.7, 300)})
    zeilen, warnungen = kosten.modell_bericht(
        kosten.team_log_dateien([tmp_path / ".ralph-logs", tmp_path / ".team-logs"]))
    assert "ralph claude-sonnet-5 (1)" in zeilen[0], zeilen
    assert "frank claude-sonnet-5 (1)" in zeilen[0], zeilen
    assert len(warnungen) == 2, warnungen
    assert all("claude-sonnet-5-5" in w and "BL-264" in w for w in warnungen)


def test_die_neueste_version_bleibt_still(tmp_path):
    """Gegenrichtung: Ein Bericht, der auch beim richtigen Modell warnt,
    wird nicht mehr gelesen (BL-14)."""
    _log(tmp_path / ".team-logs", "harry-20261001-100000.json",
         {"claude-sonnet-5-5": (0.4, 200)})
    _, warnungen = kosten.modell_bericht(
        kosten.team_log_dateien([tmp_path / ".team-logs"]))
    assert warnungen == []


def test_eine_neuere_version_aus_TEAM_PREISE_zaehlt_mit(tmp_path, monkeypatch):
    """Kommt ein Modell heraus, bevor das Kit es kennt, traegt ein Projekt
    es in TEAM_PREISE ein (BL-211) — und genau dann soll die Warnung auch
    greifen."""
    monkeypatch.setenv("TEAM_PREISE", "claude-sonnet-6=2.00")
    _log(tmp_path / ".team-logs", "marv-20261001-100000.json",
         {"claude-sonnet-5-5": (0.4, 200)})
    _, warnungen = kosten.modell_bericht(
        kosten.team_log_dateien([tmp_path / ".team-logs"]))
    assert len(warnungen) == 1 and "claude-sonnet-6" in warnungen[0], warnungen


# --- Die CLI des Loops gegen die der IDE -------------------------------------

def test_eine_aeltere_cli_im_loop_wird_gewarnt(tmp_path):
    _ide(tmp_path / "heim", "2.1.285")
    cli = _cli(tmp_path / "bin", "2.1.283")
    zeilen, warnungen = kosten.modell_bericht([], cli=cli,
                                              heim=str(tmp_path / "heim"))
    assert any("2.1.283" in z and "2.1.285" in z for z in zeilen), zeilen
    assert len(warnungen) == 1 and "aelter" in warnungen[0], warnungen


def test_dieselbe_oder_neuere_cli_bleibt_still(tmp_path):
    _ide(tmp_path / "heim", "2.1.285")
    cli = _cli(tmp_path / "bin", "2.1.285")
    _, warnungen = kosten.modell_bericht([], cli=cli,
                                         heim=str(tmp_path / "heim"))
    assert warnungen == []


def test_die_ide_version_wird_numerisch_verglichen(tmp_path):
    """`sort` auf Ordnernamen haelt 2.1.99 fuer neuer als 2.1.288."""
    _ide(tmp_path / "heim", "2.1.99", "2.1.288")
    version, _ = kosten.ide_cli_version(str(tmp_path / "heim"))
    assert version == (2, 1, 288)


def test_eine_unlesbare_cli_wird_benannt_nicht_verschwiegen(tmp_path):
    zeilen, warnungen = kosten.modell_bericht(
        [], cli=str(tmp_path / "gibt-es-nicht"), heim=str(tmp_path))
    assert any("nicht lesbar" in z for z in zeilen), zeilen
    assert warnungen == []


# --- Das Verb und die Anzeige ---------------------------------------------------

def test_das_verb_endet_mit_3_bei_einer_warnung(tmp_path):
    _log(tmp_path / ".team-logs", "frank-HM-1-v1-20260927-110000.json",
         {"claude-sonnet-5": (0.7, 300)})
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "modelle",
                        str(tmp_path / ".team-logs")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode == 3, r.stdout + r.stderr
    assert "WARNUNG" in r.stdout


@pytest.mark.parametrize("datei", ["team-status.sh", "team-status.ps1"])
def test_team_status_zeigt_modell_und_cli(datei):
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "Modell & CLI" in text and "modelle" in text and "--cli" in text, (
        f"{datei} zeigt nicht an, welches Modell lief und welche CLI der Loop "
        f"ruft (BL-264).")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

#!/usr/bin/env python3
"""BL-296: Die Pruefdichte des Red Teams laesst sich ans Bauvolumen koppeln —
mit einem zweiten Durchgang, der die Sperre gegen Doppelzahlung bewusst und
benannt uebersteuert.

DER FELDBEFUND (`Feld E`, 2026-08-24)
    57, 19, 20 Sweep-Turns je 1 000 gebauter Zeilen: Der Sweep lief einmal je
    Lauf, egal wie viel gebaut war. Der Stakeholder wollte die Tiefe ans
    Volumen koppeln — und es ging nicht: Die Vollautomatik ruft die Sweeps in
    fester Schleife, und `redteam` sperrt einen zweiten Durchgang am selben
    HEAD (`exit 3`, richtig gegen Doppelzahlung, `BL-30`).

DIE LOESUNG
    `TEAM_REDTEAM_FOCUS_2` bestellt einen zweiten Durchgang je Angreifer mit
    EIGENEM Fokus. Die Vollautomatik reicht den Stand VOR dem ersten
    Durchgang als `TEAM_REDTEAM_ZWEITER_DURCHGANG` weiter — beide pruefen
    denselben Bereich, und die Uebersteuerung steht im Log.
"""
import json
import os
import subprocess
from pathlib import Path

import test_bl241_fixphase_hat_einen_eigenen_einstieg as v
import test_bl285_grundauftrag_aus_der_konfiguration as h
from conftest import verlange_bash, verlange_pwsh


# --- Die Vollautomatik bestellt den zweiten Durchgang -------------------------

def _stubs(repo, bahn):
    for rolle in ("harry", "marv"):
        if bahn == "bash":
            text = (f'#!/usr/bin/env bash\n'
                    f'echo "STUB {rolle} fokus=${{TEAM_REDTEAM_FOCUS:-}} '
                    f'zweit=${{TEAM_REDTEAM_ZWEITER_DURCHGANG:-}}"\nexit 0\n')
            (repo / f"{rolle}.sh").write_text(text, encoding="utf-8")
            (repo / f"{rolle}.sh").chmod(0o755)
        else:
            text = (f"[Console]::Out.WriteLine(\"STUB {rolle} "
                    f"fokus=$env:TEAM_REDTEAM_FOCUS "
                    f"zweit=$env:TEAM_REDTEAM_ZWEITER_DURCHGANG\")\nexit 0\n")
            (repo / f"{rolle}.ps1").write_text(text, encoding="utf-8-sig")


def _pruefe(aus):
    assert "STUB harry fokus=ERST zweit=" in aus, aus
    assert "STUB harry fokus=ZWEIT zweit=-" in aus, (
        f"Der zweite Durchgang bekam nicht den zweiten Fokus und den Stand "
        f"vor dem ersten (BL-296).\n{aus}")
    assert "STUB marv fokus=ZWEIT zweit=-" in aus, aus
    assert "zweiter Durchgang (eigener Fokus, Kit-BL-296)" in aus, aus


def test_bash_zweiter_durchgang_auf_ansage(tmp_path):
    verlange_bash()
    repo = v._bash_projekt(tmp_path)
    _stubs(repo, "bash")
    r = v._bash(repo, "vollautomatik.sh", TEAM_REDTEAM_FOCUS="ERST",
                TEAM_REDTEAM_FOCUS_2="ZWEIT")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    _pruefe(aus)


def test_pwsh_zweiter_durchgang_auf_ansage(tmp_path):
    verlange_pwsh()
    repo = v._pwsh_projekt(tmp_path)
    _stubs(repo, "pwsh")
    r = v._pwsh(repo, "vollautomatik.ps1", TEAM_REDTEAM_FOCUS="ERST",
                TEAM_REDTEAM_FOCUS_2="ZWEIT")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    _pruefe(aus)


def test_ohne_zweiten_fokus_ein_durchgang(tmp_path):
    verlange_bash()
    repo = v._bash_projekt(tmp_path)
    _stubs(repo, "bash")
    r = v._bash(repo, "vollautomatik.sh", TEAM_REDTEAM_FOCUS="ERST")
    aus = r.stdout + r.stderr
    assert aus.count("STUB harry") == 1, aus
    assert "Kit-BL-296" not in aus, aus


# --- Der Sweep laesst sich bewusst uebersteuern ---------------------------------

def _sweep(repo, schale, stub_wert, falle, **env):
    befehl = (h.entrypoint_aufruf(repo / "harry.sh") if schale.name == "bash"
              else ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                    str(repo / "harry.ps1")])
    umgebung = dict(os.environ)
    umgebung["PATH"] = h.pfad_voran(falle, umgebung)
    for weg in ("ANTHROPIC_API_KEY", "AUTH_MODE", "TEAM_REDTEAM_FOCUS",
                "TEAM_REDTEAM_ZWEITER_DURCHGANG"):
        umgebung.pop(weg, None)
    umgebung.update(TEAM_AUTH_MODE="abo", TEAM_LOCK_HELD="1",
                    TEAM_CLAUDE_BIN=stub_wert,
                    TEAM_PROMPT_FANG=str(Path(stub_wert).parent / "fang.txt"),
                    **env)
    return subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          stdin=subprocess.DEVNULL, timeout=300)


def test_der_sweep_uebersteuert_die_sperre_nur_auf_ansage(tmp_path, schale):
    stub_wert = h._stub(tmp_path, schale)
    stub = Path(stub_wert)
    antwort = json.dumps({
        "subtype": "success", "is_error": False, "stop_reason": "end_turn",
        "result": "Nichts. <promise>REDTEAM_SWEEP_COMPLETE</promise>",
        "total_cost_usd": 0.0}, ensure_ascii=False)
    stub.write_text(stub.read_text(encoding="utf-8-sig").replace(h.ANTWORT, antwort),
                    encoding="utf-8-sig" if schale.name == "pwsh" else "utf-8",
                    newline="\n")
    repo = h._projekt(tmp_path, schale, "harry", stub_wert)
    falle = h._falle(tmp_path)
    erst = _sweep(repo, schale, stub_wert, falle)
    assert erst.returncode == 0, erst.stdout + erst.stderr
    gesperrt = _sweep(repo, schale, stub_wert, falle)
    assert gesperrt.returncode == 3, (
        "Ohne Ansage muss die Sperre gegen Doppelzahlung greifen (BL-30).\n"
        + gesperrt.stdout + gesperrt.stderr)
    zweit = _sweep(repo, schale, stub_wert, falle,
                   TEAM_REDTEAM_ZWEITER_DURCHGANG="-",
                   TEAM_REDTEAM_FOCUS="ZWEITER FOKUS")
    aus = zweit.stdout + zweit.stderr
    assert zweit.returncode == 0, aus
    assert "Kit-BL-296" in aus and "gesamte bisherige Historie" in aus, aus

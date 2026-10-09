#!/usr/bin/env python3
"""BL-319: Das Red Team gab bei abgelehnten LESEbefehlen auf und meldete die
Stelle trotzdem als geprueft.

WAS GEMELDET WURDE (`Feld F`, 2026-10-05, Nachtraege 2026-10-05/-07)
    Marv wollte die Diffs zweier Werkzeugdateien lesen; `cd … &&`,
    `Set-Location …;` und `git -C … diff` lehnte die CLI ab (freigegeben ist
    `git diff:*`). Die erlaubte Form versuchte er nicht — das Ausweichverbot
    des Prompts galt nur Edit/Write und wurde auf jeden abgelehnten Aufruf
    uebertragen. Seine Abdeckungszeile meldete den Punkt als „geprueft, ohne
    Befund", der Sweep „Sauber". Nachtraege: Ein durchgelassenes `cd`
    verschiebt die Shell fuer alle folgenden Befehle; der Smoke-Test ist nur
    woertlich und nur im BASH-Werkzeug freigegeben — im PowerShell-Werkzeug
    lehnte die CLI ihn ab, und in einem Lauf lief er in keinem Sweep.

WAS DAS KIT SELBST UEBERNIMMT (Programm statt Prompt)
    - Jede Shell-Freigabe gilt fuer beide Shell-Werkzeuge der CLI
      (`Bash(…)` UND `PowerShell(…)`).
    - Abgelehnte Lesebefehle werden gezaehlt: Der Sweep nennt sie, und der
      Abschlussbericht stellt sie neben die Abdeckungszeilen. Welche Zeile sie
      betreffen, steht nirgends — es ist ein Hinweis zum Gegenlesen.
    - Der Bericht hebt „nicht geprueft" und „teilweise geprueft" hervor.
WAS IM PROMPT STEHT
    Die erlaubten Lese-Formen, kein `cd`/`Set-Location`, der Smoke-Test in
    genau der freigegebenen Form, und eine vierte Form der Abdeckungszeile
    („teilweise geprueft — ungelesen: …").
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import Ausgabe, kit_pfad  # noqa: E402

for _tools in (Path(__file__).resolve().parents[2] / "geteilt" / "tools",
               kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")
SMOKE = "python -m pytest tests -q"
LESEN = [
    {"tool_name": "Bash", "tool_input": {
        "command": "cd /projekt && git diff abc..HEAD -- werkzeug/a.py"}},
    {"tool_name": "PowerShell", "tool_input": {
        "command": "Set-Location C:\\projekt; git diff abc..HEAD -- werkzeug/b.py"}},
    {"tool_name": "Bash", "tool_input": {
        "command": "git -C /projekt diff abc..HEAD -- werkzeug/a.py"}},
]


# --- Die Allowlist: beide Shell-Werkzeuge -----------------------------------

def test_jede_shell_freigabe_gilt_auch_fuer_powershell(tmp_path, schale):
    lib = schale.lib_kopieren(tmp_path)
    schale.config_schreiben(tmp_path, {"TEAM_PLAN_ORDNER": "plans/",
                                       "TEAM_TEST_ORDNER": "tests/",
                                       "TEAM_BEUTEBUCH_TOOL": "x"})
    r = schale.lauf([Ausgabe("team_allowed_tools", "redteam")], cwd=tmp_path,
                    lib=lib, env={"TEAM_SMOKE_TEST": SMOKE})
    assert r.returncode == 0, r.stderr
    regeln = r.stdout
    for befehl in ("git diff:*", "git log:*", "git show:*", "x:*", SMOKE):
        assert f"Bash({befehl})" in regeln, (befehl, regeln)
        assert f"PowerShell({befehl})" in regeln, (
            f"{schale.name}: PowerShell({befehl}) fehlt — im PowerShell-Werkzeug "
            f"der CLI lehnte sie den woertlich gestarteten Smoke-Test ab "
            f"(Kit-BL-319).\n{regeln}")


def test_die_schreibregeln_bleiben_wie_sie_sind(tmp_path, schale):
    """Gegenrichtung: Die Freigabe fuer PowerShell betrifft Shell-Befehle,
    nicht Edit/Write — die Schreibgrenze aus BL-292 bleibt unberuehrt."""
    lib = schale.lib_kopieren(tmp_path)
    schale.config_schreiben(tmp_path, {"TEAM_PLAN_ORDNER": "plans/",
                                       "TEAM_TEST_ORDNER": "tests/",
                                       "TEAM_BEUTEBUCH_TOOL": "x"})
    r = schale.lauf([Ausgabe("team_allowed_tools", "axel")], cwd=tmp_path,
                    lib=lib)
    assert "Edit(plans/**)" in r.stdout and "tests/**" not in r.stdout
    assert "PowerShell(Edit" not in r.stdout and "PowerShell(Write" not in r.stdout


# --- Abgelehnte Lesebefehle --------------------------------------------------

def _log(tmp_path, ablehnungen, result="Geprueft.\nABDECKUNG 1: geprüft, ohne Befund"):
    log = tmp_path / "marv-20261005-100000.json"
    log.write_text(json.dumps({
        "subtype": "success", "is_error": False, "result": result,
        "total_cost_usd": 0.5, "permission_denials": ablehnungen},
        ensure_ascii=False), encoding="utf-8")
    return log


def test_lesebefehle_werden_gezaehlt_schreibversuche_nicht(tmp_path):
    log = _log(tmp_path, LESEN + [
        {"tool_name": "Write", "tool_input": {"file_path": "plans/beutebuch.md"}}])
    funde = kosten.abgelehnte_lesebefehle(str(log))
    assert [w for w, _ in funde] == ["Bash", "PowerShell", "Bash"], funde
    assert "git diff abc..HEAD" in funde[0][1]


def test_das_verb_nennt_sie(tmp_path):
    log = _log(tmp_path, LESEN)
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "lesen-verweigert",
                        str(log)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 0
    assert len(r.stdout.strip().splitlines()) == 3, r.stdout
    assert "Set-Location" in r.stdout


def test_der_bericht_stellt_sie_neben_die_abdeckung(tmp_path):
    """Der Feldfall im Abschlussbericht: 'geprueft, ohne Befund' neben drei
    abgelehnten Lesebefehlen — und die Hervorhebung der offenen Punkte."""
    logs = tmp_path / ".team-logs"
    logs.mkdir()
    _log(logs, LESEN, result=(
        "ABDECKUNG 1: geprüft, ohne Befund\n"
        "ABDECKUNG 2: teilweise geprüft — ungelesen: werkzeug/b.py\n"
        "ABDECKUNG 3: nicht geprüft — keine Zeit"))
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "abdeckung",
                        str(logs)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    zeilen = r.stdout.splitlines()
    assert any(z.strip().startswith("ABDECKUNG 1") for z in zeilen), r.stdout
    assert "⚠ ABDECKUNG 2: teilweise geprüft" in r.stdout, r.stdout
    assert "⚠ ABDECKUNG 3: nicht geprüft" in r.stdout, r.stdout
    assert "3 Lesebefehl(e) abgelehnt" in r.stdout and "Kit-BL-319" in r.stdout


# --- Der Sweep, als Lauf -----------------------------------------------------

def _sweep(tmp_path, schale, ablehnungen):
    import test_bl285_grundauftrag_aus_der_konfiguration as h
    antwort = json.dumps({
        "subtype": "success", "is_error": False, "stop_reason": "end_turn",
        "result": "ABDECKUNG 1: geprüft, ohne Befund "
                  "<promise>REDTEAM_SWEEP_COMPLETE</promise>",
        "total_cost_usd": 0.0, "permission_denials": ablehnungen,
    }, ensure_ascii=False)
    stub_wert = h._stub(tmp_path, schale)
    stub = Path(stub_wert)
    stub.write_text(stub.read_text(encoding="utf-8-sig").replace(h.ANTWORT, antwort),
                    encoding="utf-8-sig" if schale.name == "pwsh" else "utf-8",
                    newline="\n")
    repo = h._projekt(tmp_path, schale, "marv", stub_wert)
    befehl = (h.entrypoint_aufruf(repo / "marv.sh") if schale.name == "bash"
              else ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                    str(repo / "marv.ps1")])
    umgebung = dict(os.environ)
    umgebung["PATH"] = h.pfad_voran(h._falle(tmp_path), umgebung)
    for weg in ("TEAM_REDTEAM_FOCUS", "ANTHROPIC_API_KEY", "AUTH_MODE"):
        umgebung.pop(weg, None)
    fang = tmp_path / "fang.txt"
    umgebung.update(TEAM_PROMPT_FANG=str(fang), TEAM_AUTH_MODE="abo",
                    TEAM_LOCK_HELD="1", TEAM_CLAUDE_BIN=stub_wert,
                    TEAM_SMOKE_TEST=SMOKE)
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    assert h.FALLE not in r.stdout + r.stderr, "die echte CLI wurde gesucht"
    return r, fang


def test_der_sweep_nennt_abgelehnte_lesebefehle(tmp_path, schale):
    """Gegen den alten Stand gemessen: Exit 0, „Sauber", kein Wort ueber die
    drei Ablehnungen."""
    r, _fang = _sweep(tmp_path, schale, LESEN)
    assert r.returncode == 0, (
        "Abgelehnte LESEbefehle machen den Sweep nicht unsauber — sie sind ein "
        f"Hinweis, kein Urteil.\n{r.stdout}\n{r.stderr}")
    assert "3 Lesebefehl(e) abgelehnt" in r.stderr and "Kit-BL-319" in r.stderr, (
        f"{schale.name}: Der Sweep schweigt zu den abgelehnten Lesebefehlen.\n"
        f"{r.stderr}")
    assert "git diff abc..HEAD" in r.stderr


def test_ohne_ablehnung_schweigt_er(tmp_path, schale):
    r, _fang = _sweep(tmp_path, schale, [])
    assert r.returncode == 0, r.stderr
    assert "Lesebefehl" not in r.stderr, r.stderr


def test_der_prompt_nennt_die_erlaubten_formen(tmp_path, schale):
    r, fang = _sweep(tmp_path, schale, [])
    assert fang.is_file(), f"kein Prompt gefangen\n{r.stdout}\n{r.stderr}"
    prompt = fang.read_text(encoding="utf-8")
    for teil in ("LESEbefehl", "ohne -C", "Set-Location",
                 "teilweise geprüft — ungelesen",
                 f"nur wörtlich so zu: {SMOKE}"):
        assert teil in prompt, f"{schale.name}: '{teil}' fehlt im Sweep-Prompt"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

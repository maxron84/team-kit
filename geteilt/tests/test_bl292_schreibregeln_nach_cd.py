#!/usr/bin/env python3
"""BL-292: Die relativen Schreibregeln des Red Teams griffen nach einem `cd`
nicht mehr — und der Sweep meldete trotzdem „sauber, keine Funde".

WAS IM FELD PASSIERT IST (`Feld F`, 2026-10-02)
    Harry und Marv laufen mit `--permission-mode default` und der Allowlist
    aus `team_allowed_tools`; die Schreibregeln waren relativ (`Edit(plans/**)`,
    `Write(tests/**)`). Die CLI loest sie gegen das AKTUELLE Arbeitsverzeichnis
    der Shell auf: Nach einem erlaubten `cd <Unterordner> && cat …` lehnte sie
    jeden Schreibversuch nach plans/ und tests/ ab (fuenf Haiku-Proben, CLI
    2.1.285). Beide Rollen legten ihre vier Funde deshalb nur im `result` ab.
    `redteam` urteilte nach dem Diff des Beutebuchs: „Geprueft, keine neuen
    Funde", die Fixphase „nichts zu tun", der Bericht „(keine Funde)". Die
    Ablehnungen standen in `permission_denials` — gelesen hat sie niemand.

WAS GEBAUT IST
    (1) Jede Schreibregel steht zusaetzlich ABSOLUT in der Allowlist
        (`//c/Users/…/plans/**`) — die Form, die im Feld trug. Ein Leerzeichen
        im Projektpfad bekommt eine Meldung statt einer zerlegten Liste.
    (2) `kosten.py verweigert` liest `permission_denials`; ein abgelehnter
        Schreibversuch IM erlaubten Bereich macht den Sweep NICHT sauber:
        Zeiger bleibt stehen, Exit 1, der Log-Pfad steht in der Meldung.
    (3) Der Sweep-Prompt sagt, was bei einer Ablehnung zu tun ist: den
        Fundblock vollstaendig in die Abschlussantwort, nicht auf Bash
        ausweichen.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import Ausgabe, entrypoint_pfad, kit_pfad  # noqa: E402

for _tools in (Path(__file__).resolve().parents[2] / "geteilt" / "tools",
               kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")


def _wurzel_form(pfad):
    """Was die Allowlist nach `//` fuer diesen Ordner erwartet."""
    p = str(pfad).replace("\\", "/")
    if len(p) > 1 and p[1] == ":":
        return p[0].lower() + "/" + p[3:]
    return p.lstrip("/")


def _allowlist(schale, ordner, rolle="redteam"):
    lib = schale.lib_kopieren(ordner)
    schale.config_schreiben(ordner, {"TEAM_PLAN_ORDNER": "plans/",
                                     "TEAM_TEST_ORDNER": "tests/",
                                     "TEAM_BEUTEBUCH_TOOL": "x"})
    r = schale.lauf([Ausgabe("team_allowed_tools", rolle)], cwd=ordner, lib=lib)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip(), r.stderr


# --- (1) Die Allowlist traegt beide Formen -----------------------------------

def test_die_schreibregeln_stehen_relativ_UND_absolut(tmp_path, schale):
    regeln, _ = _allowlist(schale, tmp_path)
    w = _wurzel_form(tmp_path.resolve())
    for erwartet in ("Edit(plans/**)", "Write(tests/**)",
                     f"Edit(//{w}/plans/**)", f"Write(//{w}/tests/**)"):
        assert erwartet in regeln, (
            f"{schale.name}: {erwartet} fehlt — nach einem cd in einen "
            f"Unterordner lehnt die CLI sonst jeden Schreibversuch ab "
            f"(BL-292).\n{regeln}")


def test_axel_bekommt_nur_den_plan_ordner(tmp_path, schale):
    regeln, _ = _allowlist(schale, tmp_path, rolle="axel")
    assert "/plans/**)" in regeln and "tests/**" not in regeln, regeln


def test_ein_leerzeichen_im_pfad_bekommt_eine_meldung(tmp_path, schale):
    ordner = tmp_path / "mit leerzeichen"
    ordner.mkdir()
    regeln, fehler = _allowlist(schale, ordner)
    assert "//" not in regeln, (
        "Mit Leerzeichen im Pfad zerlegt die absolute Form die Liste — sie "
        f"darf dann nicht drinstehen.\n{regeln}")
    assert "Leerzeichen" in fehler and "BL-292" in fehler, fehler


# --- (2) Abgelehnte Schreibversuche werden gelesen ---------------------------

def _log(tmp_path, ablehnungen):
    log = tmp_path / "harry-20261002-100000.json"
    log.write_text(json.dumps({
        "subtype": "success", "is_error": False, "result": "zwei Funde ...",
        "total_cost_usd": 0.5, "permission_denials": ablehnungen}),
        encoding="utf-8")
    return log


def test_nur_ablehnungen_im_erlaubten_bereich_zaehlen(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    absolut = str((tmp_path / "plans" / "beutebuch.md").resolve())
    log = _log(tmp_path, [
        {"tool_name": "Write", "tool_input": {"file_path": "tests/test_hm7.py"}},
        {"tool_name": "Edit", "tool_input": {"file_path": absolut}},
        {"tool_name": "Edit", "tool_input": {"file_path": "src/app.py"}},
        {"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}},
    ])
    funde = kosten.abgelehnte_schreibversuche(str(log), ["plans/", "tests/"])
    assert sorted(p for _, p in funde) == ["plans/beutebuch.md",
                                           "tests/test_hm7.py"], funde


def test_ein_msys_pfad_wird_erkannt(tmp_path, monkeypatch):
    if os.name != "nt":
        pytest.skip("MSYS-Pfade gibt es nur unter Windows")
    monkeypatch.chdir(tmp_path)
    w = str(tmp_path.resolve()).replace("\\", "/")
    msys = "/" + w[0].lower() + w[2:] + "/plans/beutebuch.md"
    log = _log(tmp_path, [{"tool_name": "Edit",
                           "tool_input": {"file_path": msys}}])
    assert kosten.abgelehnte_schreibversuche(str(log), ["plans/"]) == [
        ("Edit", "plans/beutebuch.md")]


def test_das_verb_endet_mit_3_nur_bei_einem_befund(tmp_path):
    mit = _log(tmp_path, [{"tool_name": "Write",
                           "tool_input": {"file_path": "plans/beutebuch.md"}}])
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "verweigert", str(mit),
                        "--ordner", "plans/", "tests/"], cwd=tmp_path,
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 3 and "plans/beutebuch.md" in r.stdout, r.stdout
    ohne = tmp_path / "leer.json"
    ohne.write_text(json.dumps({"result": "x"}), encoding="utf-8")
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "verweigert", str(ohne),
                        "--ordner", "plans/"], cwd=tmp_path,
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and not r.stdout.strip()


# --- Der Fall aus dem Feld, als Lauf ------------------------------------------

def test_ein_sweep_mit_abgelehntem_schreibversuch_ist_nicht_sauber(tmp_path,
                                                                 schale):
    """Die Attrappe der CLI meldet, was die echte im Feld meldete: Erfolg,
    zwei Funde im `result` — und einen abgelehnten Write ins Beutebuch."""
    import test_bl285_grundauftrag_aus_der_konfiguration as h
    antwort = json.dumps({
        "subtype": "success", "is_error": False, "stop_reason": "end_turn",
        "result": "Zwei Funde, Beutebuch nicht schreibbar. "
                  "<promise>REDTEAM_SWEEP_COMPLETE</promise>",
        "total_cost_usd": 0.0,
        "permission_denials": [{"tool_name": "Write",
                                "tool_input": {"file_path": "plans/beutebuch.md"}}],
    }, ensure_ascii=False)
    stub_wert = h._stub(tmp_path, schale)
    stub = Path(stub_wert)
    stub.write_text(stub.read_text(encoding="utf-8-sig").replace(h.ANTWORT, antwort),
                    encoding="utf-8-sig" if schale.name == "pwsh" else "utf-8",
                    newline="\n")
    repo = h._projekt(tmp_path, schale, "harry", stub_wert)
    befehl = (h.entrypoint_aufruf(repo / "harry.sh") if schale.name == "bash"
              else ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                    str(repo / "harry.ps1")])
    umgebung = dict(os.environ)
    umgebung["PATH"] = h.pfad_voran(h._falle(tmp_path), umgebung)
    for weg in ("TEAM_REDTEAM_FOCUS", "ANTHROPIC_API_KEY", "AUTH_MODE"):
        umgebung.pop(weg, None)
    umgebung.update(TEAM_PROMPT_FANG=str(tmp_path / "fang.txt"),
                    TEAM_AUTH_MODE="abo", TEAM_LOCK_HELD="1",
                    TEAM_CLAUDE_BIN=stub_wert)
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    assert h.FALLE not in r.stdout + r.stderr, "die echte CLI wurde gesucht"
    assert r.returncode == 1, (
        f"{schale.name}: Ein Sweep mit abgelehntem Schreibversuch im "
        f"erlaubten Bereich galt als sauber (BL-292).\n{r.stdout}\n{r.stderr}")
    assert "NICHT SAUBER" in r.stderr and "plans/beutebuch.md" in r.stderr
    assert not (repo / ".harry-state").exists(), (
        "Der Zeiger darf nicht weiterlaufen — der Bereich gilt als ungeprueft.")


# --- (3) Der Prompt ----------------------------------------------------------

@pytest.mark.parametrize("datei", ["redteam.sh", "redteam.ps1"])
def test_der_prompt_sagt_was_bei_einer_ablehnung_zu_tun_ist(datei):
    pfad = kit_pfad(datei)
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "in deine Abschlussantwort" in text and "BL-292" in text, (
        f"{datei}: Der Sweep-Prompt sagt nicht, wohin ein Fund geht, wenn die "
        f"CLI das Schreiben ablehnt.")


# --- (2) sinngemaess fuer Axel ------------------------------------------------

def test_axel_nennt_den_abgelehnten_schreibversuch(tmp_path, schale):
    """Axel scheiterte schon vorher laut — ohne Akte kein Ergebnis. Aber die
    Meldung lautete nur `Akte vorhanden: nein`, und die Akte stand womoeglich
    vollstaendig im `result` des Logs. Jetzt nennt der Lauf die Ursache und
    den Fundort."""
    import test_bl285_grundauftrag_aus_der_konfiguration as h
    antwort = json.dumps({
        "subtype": "success", "is_error": False, "stop_reason": "end_turn",
        "result": "Akte geschrieben. <promise>AXEL_CASE_COMPLETE</promise>",
        "total_cost_usd": 0.0,
        "permission_denials": [{"tool_name": "Write", "tool_input": {
            "file_path": "plans/ermittlungsakten/AX-1.md"}}],
    }, ensure_ascii=False)
    stub_wert = h._stub(tmp_path, schale)
    stub = Path(stub_wert)
    stub.write_text(stub.read_text(encoding="utf-8-sig").replace(h.ANTWORT, antwort),
                    encoding="utf-8-sig" if schale.name == "pwsh" else "utf-8",
                    newline="\n")
    repo = h._projekt(tmp_path, schale, "axel", stub_wert)
    zeile = ('TEAM_ERMITTLUNGSAKTEN="plans/ermittlungsakten"' if schale.ist_bash
             else '$TEAM_ERMITTLUNGSAKTEN = "plans/ermittlungsakten"')
    with (repo / f"team.config{schale.endung}").open("a", encoding="utf-8") as f:
        f.write(zeile + "\n")
    (repo / "plans" / "beutebuch.md").write_text(
        "# Beutebuch\n\n## Funde\n\n### HM-1 — Ein grosser Fall\n\n"
        "- **Status**: an Axel übergeben\n- **Fundstelle**: `src/app.py`\n"
        "- **Reproducer-Test**: `tests/test_hm1_fall.py`\n",
        encoding="utf-8", newline="\n")
    subprocess.run(["git", "commit", "-qam", "fund"], cwd=repo, check=True,
                   capture_output=True)
    befehl = (h.entrypoint_aufruf(repo / "axel.sh") if schale.name == "bash"
              else ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                    str(repo / "axel.ps1")])
    umgebung = dict(os.environ)
    umgebung["PATH"] = h.pfad_voran(h._falle(tmp_path), umgebung)
    for weg in ("ANTHROPIC_API_KEY", "AUTH_MODE"):
        umgebung.pop(weg, None)
    umgebung.update(TEAM_PROMPT_FANG=str(tmp_path / "fang.txt"),
                    TEAM_AUTH_MODE="abo", TEAM_LOCK_HELD="1",
                    TEAM_CLAUDE_BIN=stub_wert)
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    assert h.FALLE not in r.stdout + r.stderr, "die echte CLI wurde gesucht"
    assert (tmp_path / "fang.txt").is_file(), (
        f"{schale.name}: Axel hat keinen Prompt abgesetzt (Exit "
        f"{r.returncode}) — der Test prueft sonst nichts.\n{r.stdout}\n{r.stderr}")
    assert r.returncode == 1, f"{r.stdout}\n{r.stderr}"
    assert "BL-292" in r.stderr and "AX-1.md" in r.stderr, (
        f"{schale.name}: Axel nennt den abgelehnten Schreibversuch nicht.\n"
        f"{r.stderr}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

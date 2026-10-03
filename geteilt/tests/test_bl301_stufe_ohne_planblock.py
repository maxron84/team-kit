#!/usr/bin/env python3
"""BL-301: Eine Stufennummer ohne Plan-Block war ein bezahlter No-Op — und die
Selbstpruefung empfahl danach, eine nie gebaute Stufe zu quittieren.

WAS IM FELD PASSIERT IST (`Feld E`, 2026-08-26, sechste Kaskade)
    `.ralph-state` stand nach einem Closeout versehentlich auf 17; der aktive
    Plan definiert nur die Stufen 28–33. Ralph startete trotzdem einen
    bezahlten Aufruf (0,33 USD). Das Modell erkannte die Lage und baute
    nichts — dann widersprach sich die BL-41-Selbstpruefung: „das ist NICHT
    der vierte Ausgang", und darunter der Handlungsplan des vierten Ausgangs
    mit dem einzigen konkreten Befehl `echo 18 > .ralph-state`. Wer ihm
    folgt, quittiert eine nie gebaute Stufe und laeuft in denselben No-Op,
    eine Nummer weiter — sechzehn Mal.

WAS GEBAUT IST
    Vor dem ersten Token: Hat der Plan `## Stufe N`-Bloecke, aber keinen fuer
    die Nummer aus `.ralph-state`, endet Ralph mit benannter Ursache und der
    Spanne des Plans — kein Aufruf, keine Kosten, und der Rat lautet
    ausdruecklich NICHT „eins weiterzaehlen". Ein Plan ganz ohne solche
    Bloecke wird nicht beurteilt: Ein fremdes Format ist kein Befund.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (Ausgabe, entrypoint_aufruf, entrypoint_pfad,  # noqa: E402
                      kopiere_team_namensraum, pfad_voran, werkzeug_wert)

PLAN = """# Plan: Kaskade 6

**Stufen:** 28–33
RALPH_CAP=33
BUDGET_EMPFEHLUNG_USD=20

## Stufe 28 — Erstens
## Stufe 29
### Stufe 30: Drittens
## Stufe 31 — x
## Stufe 32 — y
## Stufe 33 — z
"""

FALLE = "ECHTE-CLI-GESUCHT-BL301"


def _falle(ordner):
    ordner.mkdir(parents=True, exist_ok=True)
    sh = ordner / "claude"
    sh.write_text(f"#!/usr/bin/env bash\necho {FALLE} >&2\nexit 99\n",
                  encoding="utf-8", newline="\n")
    sh.chmod(0o755)
    (ordner / "claude.cmd").write_text(
        f"@echo off\r\necho {FALLE} 1>&2\r\nexit /b 99\r\n", encoding="utf-8")
    return ordner


def test_die_stufen_eines_plans(tmp_path, schale):
    lib = schale.lib_kopieren(tmp_path)
    (tmp_path / "plan.md").write_text(PLAN, encoding="utf-8")
    (tmp_path / "leer.md").write_text("# Plan ohne Bloecke\n", encoding="utf-8")
    r = schale.lauf([Ausgabe("team_plan_stufen", "plan.md"),
                     Ausgabe("team_plan_stufen", "leer.md")],
                    cwd=tmp_path, lib=lib)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["28", "29", "30", "31", "32", "33"], r.stdout


def _projekt(tmp_path, schale, stufe, cli=None):
    repo = tmp_path / "repo"
    for ordner in ("src", "tests", "plans"):
        (repo / ordner).mkdir(parents=True)
    wrapper = entrypoint_pfad(f"ralph{schale.endung}")
    if not wrapper.is_file():
        pytest.skip(f"{wrapper.name} liegt in dieser Ablage nicht")
    shutil.copy(wrapper, repo / wrapper.name)
    kopiere_team_namensraum(repo / "team")
    falle = _falle(tmp_path / "falle")
    if cli is None:
        cli = (falle / "claude").as_posix() if schale.name == "bash" \
            else str(falle / "claude.cmd")
    schale.config_schreiben(repo, {
        "TEAM_DOMAENEN": "produkt", "TEAM_PRODUKTIVCODE": "src/",
        "TEAM_TEST_ORDNER": "tests/", "TEAM_PLAN_ORDNER": "plans/",
        "TEAM_BEUTEBUCH": "plans/beutebuch.md",
        "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
        "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
        "TEAM_CLAUDE_BIN": cli,
        # Was die installierte team.config.sh sonst mitbringt und Ralphs
        # Prompt auf der bash-Bahn unter `set -u` verlangt.
        "TEAM_CHANGELOG": "CHANGELOG.md", "TEAM_BACKLOG": "plans/backlog.md",
        "TEAM_ROADMAP": "plans/roadmap.md",
        "TEAM_ERMITTLUNGSAKTEN": "plans/ermittlungsakten",
        "TEAM_FEAT_PRAEFIX": "feat", "TEAM_FIX_PRAEFIX": "fix",
    })
    (repo / "plans" / "ralph-kaskade-6-x.md").write_text(PLAN, encoding="utf-8")
    (repo / ".ralph-plan").write_text("plans/ralph-kaskade-6-x.md\n",
                                      encoding="utf-8")
    (repo / ".ralph-state").write_text(f"{stufe}\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo, falle


def _ralph(repo, schale, falle):
    befehl = (entrypoint_aufruf(repo / "ralph.sh") if schale.name == "bash"
              else ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                    str(repo / "ralph.ps1")])
    umgebung = dict(os.environ)
    umgebung["PATH"] = pfad_voran(falle, umgebung)
    umgebung.update(TEAM_LOCK_HELD="1", TEAM_AUTH_MODE="abo")
    umgebung.pop("ANTHROPIC_API_KEY", None)
    return subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          stdin=subprocess.DEVNULL, timeout=300)


def test_eine_stufe_ohne_block_kostet_keinen_aufruf(tmp_path, schale):
    """Der Feldfall: .ralph-state auf 17, der Plan kennt 28–33."""
    repo, falle = _projekt(tmp_path, schale, 17)
    r = _ralph(repo, schale, falle)
    ausgabe = r.stdout + r.stderr
    assert FALLE not in ausgabe, (
        f"{schale.name}: Ralph hat fuer eine Stufe ohne Plan-Block die CLI "
        f"gerufen — ein bezahlter No-Op (BL-301).\n{ausgabe}")
    assert r.returncode == 1, ausgabe
    assert "Stufe 17 steht nicht in" in ausgabe and "28–33" in ausgabe, ausgabe
    assert "NICHT einfach eins weiterzählen" in ausgabe, ausgabe
    assert not (repo / ".ralph-logs").is_dir() or \
        not any((repo / ".ralph-logs").glob("*.json")), "kein Log, kein Aufruf"


def test_eine_stufe_mit_block_laeuft_bis_zum_aufruf(tmp_path, schale):
    """Gegenrichtung: Mit gueltiger Stufe kommt Ralph bis zum Aufruf — hier
    die Falle, die laut scheitert. Ohne diesen Fall waere die Pruefung oben
    auch dann gruen, wenn Ralph JEDE Stufe abwiese."""
    repo, falle = _projekt(tmp_path, schale, 29)
    r = _ralph(repo, schale, falle)
    assert "steht nicht in" not in r.stdout + r.stderr, r.stderr


def test_nichts_hinterlassen_ist_kein_vierter_ausgang(tmp_path, schale,
                                                     monkeypatch):
    """Befund 2: Die Stufe steht im Plan, die Sitzung meldet Erfolg, gibt kein
    Promise und hinterlaesst NICHTS. Dann darf Ralph nicht den Plan des
    vierten Ausgangs drucken — sein einziger konkreter Befehl quittierte eine
    nie gebaute Stufe. Stattdessen steht da, was die Rolle selbst sagt."""
    import json
    import test_bl285_grundauftrag_aus_der_konfiguration as h
    grund = "Stufe 29 ist schon gebaut, .ralph-state muss auf 34."
    antwort = json.dumps({"subtype": "success", "is_error": False,
                          "stop_reason": "end_turn", "result": grund,
                          "total_cost_usd": 0.0}, ensure_ascii=False)
    stub_wert = h._stub(tmp_path, schale)
    stub = Path(stub_wert)
    stub.write_text(stub.read_text(encoding="utf-8-sig").replace(h.ANTWORT, antwort),
                    encoding="utf-8-sig" if schale.name == "pwsh" else "utf-8",
                    newline="\n")
    repo, falle = _projekt(tmp_path, schale, 29, cli=stub_wert)
    monkeypatch.setenv("TEAM_PROMPT_FANG", str(tmp_path / "fang.txt"))
    r = _ralph(repo, schale, falle)
    ausgabe = r.stdout + r.stderr
    assert FALLE not in ausgabe, ausgabe
    assert r.returncode == 1, ausgabe
    assert "NICHTS hinterlassen" in ausgabe, ausgabe
    assert "Beides ja" not in ausgabe and "30 >" not in ausgabe, (
        f"{schale.name}: Ralph druckt den Plan des vierten Ausgangs und raet, "
        f"eine nie gebaute Stufe zu quittieren (BL-301, Befund 2).\n{ausgabe}")
    assert "34" in ausgabe, (
        f"Der Grund, den die Rolle selbst nennt, steht nicht in der "
        f"Konsole.\n{ausgabe}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

#!/usr/bin/env python3
"""BL-284 (3): Ein Fokus, der wortgleich zu einem ANDEREN Plan gehoert, wird
laut — statt als frisch gesetzt durchzugehen.

DER FELDBEFUND (`Feld F`, 2026-09-27)
    In pwsh bleibt eine `$env:`-Variable in der Sitzung stehen. Der naechste
    Lauf fuhr still mit dem Fokus der VORIGEN Kaskade: Die Verfallsmechanik
    aus `Kit-BL-31` bindet nur den GESPEICHERTEN Fokus an den Stand — ein in
    der Umgebung gesetzter gilt immer als frisch.

DIE PROBE
    Harry laeuft zweimal mit demselben Fokus, dazwischen wird der Plan
    umgelegt und ein Commit gemacht. Der zweite Sweep muss warnen und die Lage
    im Fokus-Protokoll fuer den Abschlussbericht festhalten (`Kit-BL-250`).
    Gegenprobe: Bleibt der Plan derselbe, schweigt er.
"""
import json
import os
import subprocess
from pathlib import Path

import test_bl285_grundauftrag_aus_der_konfiguration as h

FOKUS = "Pruefe die Spielstaende und das Speichern"


def _sweep(repo, schale, stub_wert, tmp_path, falle):
    befehl = (h.entrypoint_aufruf(repo / "harry.sh") if schale.name == "bash"
              else ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                    str(repo / "harry.ps1")])
    umgebung = dict(os.environ)
    umgebung["PATH"] = h.pfad_voran(falle, umgebung)
    for weg in ("ANTHROPIC_API_KEY", "AUTH_MODE", "TEAM_REDTEAM_AUFTRAG_HARRY"):
        umgebung.pop(weg, None)
    umgebung.update(TEAM_REDTEAM_FOCUS=FOKUS, TEAM_AUTH_MODE="abo",
                    TEAM_LOCK_HELD="1", TEAM_CLAUDE_BIN=stub_wert,
                    TEAM_PROMPT_FANG=str(tmp_path / "fang.txt"))
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    assert h.FALLE not in r.stdout + r.stderr, "die echte CLI wurde gesucht"
    return r


def _plan(repo, name):
    (repo / ".ralph-plan").write_text(f"plans/{name}\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text(f"print('{name}')\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "commit", "-qam", name], check=True,
                   capture_output=True)


def _lage(repo):
    return (repo / ".team-logs" / "fokus-harry.txt").read_text(
        encoding="utf-8-sig").splitlines()[0]


def _projekt(tmp_path, schale):
    stub_wert = h._stub(tmp_path, schale)
    # Ein sauberer Sweep: Die Attrappe quittiert, sonst endet der Lauf mit 1
    # und der zweite Sweep fiele auf "kein Promise" statt auf den Fokus.
    stub = Path(stub_wert)
    antwort = json.dumps({
        "subtype": "success", "is_error": False, "stop_reason": "end_turn",
        "result": "Nichts gefunden. <promise>REDTEAM_SWEEP_COMPLETE</promise>",
        "total_cost_usd": 0.0}, ensure_ascii=False)
    stub.write_text(stub.read_text(encoding="utf-8-sig").replace(h.ANTWORT, antwort),
                    encoding="utf-8-sig" if schale.name == "pwsh" else "utf-8",
                    newline="\n")
    repo = h._projekt(tmp_path, schale, "harry", stub_wert)
    return repo, stub_wert, h._falle(tmp_path)


def test_ein_wortgleicher_fokus_unter_neuem_plan_wird_laut(tmp_path, schale):
    repo, stub, falle = _projekt(tmp_path, schale)
    _plan(repo, "ralph-kaskade-7-alt.md")
    erst = _sweep(repo, schale, stub, tmp_path, falle)
    assert erst.returncode == 0, erst.stdout + erst.stderr
    assert _lage(repo) == "gesetzt"
    _plan(repo, "ralph-kaskade-8-neu.md")
    zweit = _sweep(repo, schale, stub, tmp_path, falle)
    assert zweit.returncode == 0, zweit.stdout + zweit.stderr
    assert "Kit-BL-284" in zweit.stderr, (
        f"{schale.name}: Der Fokus der vorigen Kaskade ging still als frisch "
        f"durch.\n{zweit.stderr}")
    assert "stehengeblieben" in _lage(repo), _lage(repo)


def test_derselbe_plan_schweigt(tmp_path, schale):
    repo, stub, falle = _projekt(tmp_path, schale)
    _plan(repo, "ralph-kaskade-7-alt.md")
    assert _sweep(repo, schale, stub, tmp_path, falle).returncode == 0
    (repo / "src" / "app.py").write_text("print('weiter')\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "commit", "-qam", "weiter"],
                   check=True, capture_output=True)
    zweit = _sweep(repo, schale, stub, tmp_path, falle)
    assert zweit.returncode == 0, zweit.stdout + zweit.stderr
    assert "Kit-BL-284" not in zweit.stderr, zweit.stderr
    assert _lage(repo) == "gesetzt"

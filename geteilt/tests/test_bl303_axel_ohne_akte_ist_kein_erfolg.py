#!/usr/bin/env python3
"""BL-303: Axel meldete eine Ermittlung, die es nicht gab — und die bash-Bahn
starb ohne Akten-Ordner, ohne ein Wort zu sagen.

BEIFANG beim Bau des Axel-Falls von BL-292 (2026-10-03), beide Befunde an
einer CLI-Attrappe ausgefuehrt, nicht hergeleitet:

1. `team_guard_urteil` entscheidet nur ueber einen UEBERGRIFF. Ohne einen
   liess es jede Runde zaehlen — auch eine, die weder Akte noch
   Statuswechsel hinterliess. Auf beiden Bahnen stand dann
   *„Ermittlungsakte AX-1 erstellt, HM-1 zurück an Frank"*, Exit 0. Der Fall
   blieb aber bei Axel, und die Vollautomatik rief Axel erneut — bezahlt, mit
   dem staerksten Modell. Genau das passiert, wenn die CLI das Schreiben
   ablehnt (BL-292): Die Akte steht dann nur im `result` des Logs.

2. `axel.sh` zaehlte die Akten mit `find | wc -l` unter `pipefail` und `-e`.
   Fehlt der Akten-Ordner, endet `find` mit 1 — und das Skript an dieser
   Zuweisung, mit Exit 1 und ohne Meldung. Der Installer legt den Ordner an
   (BL-121); ein Projekt kann ihn trotzdem verlieren. Die pwsh-Bahn prueft
   den Ordner seit jeher mit `Test-Path`.

Die Gegenrichtung gehoert dazu: Eine Runde MIT Akte und Statuswechsel endet
weiter mit Exit 0 und committet beides. Den Erfolgsweg hat bis hierher kein
Test gefahren.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_bl285_grundauftrag_aus_der_konfiguration as h  # noqa: E402

ANTWORT = json.dumps({
    "subtype": "success", "is_error": False, "stop_reason": "end_turn",
    "result": "Akte geschrieben. <promise>AXEL_CASE_COMPLETE</promise>",
    "total_cost_usd": 0.0,
}, ensure_ascii=False)

FUND = ("# Beutebuch\n\n## Funde\n\n### HM-1 — Ein grosser Fall\n\n"
        "- **Status**: an Axel übergeben\n- **Fundstelle**: `src/app.py`\n"
        "- **Reproducer-Test**: `tests/test_hm1_fall.py`\n")


def _stub(tmp_path, schale, liefert):
    """Eine Attrappe, die — wenn `liefert` — tut, was Axel tun soll: die Akte
    anlegen und den Fall an Frank zurueckgeben."""
    python = Path(sys.executable)
    if schale.name == "bash":
        arbeit = ""
        if liefert:
            arbeit = ("mkdir -p plans/ermittlungsakten\n"
                      "printf '# AX-1 — Fall\\n' > plans/ermittlungsakten/AX-1.md\n"
                      f"'{python.as_posix()}' team/tools/beutebuch.py set HM-1 "
                      "'Fix-Plan liegt vor'\n")
        stub = tmp_path / "claude-stub.sh"
        stub.write_text("#!/usr/bin/env bash\n" + arbeit
                        + "cat <<'TEAMJSON'\n" + ANTWORT + "\nTEAMJSON\n",
                        encoding="utf-8", newline="\n")
        stub.chmod(0o755)
        return stub.as_posix()
    arbeit = ""
    if liefert:
        arbeit = ("New-Item -ItemType Directory -Force plans/ermittlungsakten | Out-Null\n"
                  "Set-Content -Path plans/ermittlungsakten/AX-1.md -Value '# AX-1 — Fall'\n"
                  f"& '{python}' team/tools/beutebuch.py set HM-1 'Fix-Plan liegt vor'\n")
    stub = tmp_path / "claude-stub.ps1"
    stub.write_text("param()\n" + arbeit + "Write-Output @'\n" + ANTWORT
                    + "\n'@\nexit 0\n", encoding="utf-8-sig", newline="\n")
    return str(stub)


def _axel(tmp_path, schale, liefert):
    stub_wert = _stub(tmp_path, schale, liefert)
    repo = h._projekt(tmp_path, schale, "axel", stub_wert)
    # Den Akten-Ordner gibt es hier NICHT (Befund 2).
    zeile = ('TEAM_ERMITTLUNGSAKTEN="plans/ermittlungsakten"' if schale.ist_bash
             else '$TEAM_ERMITTLUNGSAKTEN = "plans/ermittlungsakten"')
    with (repo / f"team.config{schale.endung}").open("a", encoding="utf-8") as f:
        f.write(zeile + "\n")
    (repo / "plans" / "beutebuch.md").write_text(FUND, encoding="utf-8",
                                                newline="\n")
    subprocess.run(["git", "commit", "-qam", "fund"], cwd=repo, check=True,
                   capture_output=True)
    befehl = (h.entrypoint_aufruf(repo / "axel.sh") if schale.name == "bash"
              else ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                    str(repo / "axel.ps1")])
    umgebung = dict(os.environ)
    umgebung["PATH"] = h.pfad_voran(h._falle(tmp_path), umgebung)
    for weg in ("ANTHROPIC_API_KEY", "AUTH_MODE"):
        umgebung.pop(weg, None)
    umgebung.update(TEAM_AUTH_MODE="abo", TEAM_LOCK_HELD="1",
                    TEAM_CLAUDE_BIN=stub_wert)
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    assert h.FALLE not in r.stdout + r.stderr, "die echte CLI wurde gesucht"
    return repo, r


def test_eine_runde_ohne_akte_ist_kein_erfolg(tmp_path, schale):
    repo, r = _axel(tmp_path, schale, liefert=False)
    ausgabe = f"{schale.name}:\n{r.stdout}\n{r.stderr}"
    assert "Axel: HM-1 kostete" in r.stdout, (
        f"Axel kam nicht bis zum Aufruf — ohne Akten-Ordner starb die "
        f"bash-Bahn hier still (BL-303, Befund 2).\n{ausgabe}")
    assert r.returncode == 1, (
        f"Eine Runde ohne Akte endete mit Exit {r.returncode} (BL-303).\n{ausgabe}")
    assert "erstellt" not in r.stdout, ausgabe
    assert "KEINE Ermittlung geliefert" in r.stderr, ausgabe


def test_eine_runde_mit_akte_bleibt_ein_erfolg(tmp_path, schale):
    repo, r = _axel(tmp_path, schale, liefert=True)
    ausgabe = f"{schale.name}:\n{r.stdout}\n{r.stderr}"
    assert r.returncode == 0, ausgabe
    assert "Ermittlungsakte AX-1 erstellt" in r.stdout, ausgabe
    log = subprocess.run(["git", "log", "-1", "--name-only", "--pretty=%s"],
                         cwd=repo, capture_output=True, text=True,
                         encoding="utf-8").stdout
    assert "docs(akte): AX-1 zu HM-1" in log, log
    assert "plans/ermittlungsakten/AX-1.md" in log, log


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

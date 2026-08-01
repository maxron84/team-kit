#!/usr/bin/env python3
"""Fixture-Test für HM-20 (Beutebuch) — belegt Stufe 35 (Kaskade 11).

Root-Cause: team-lib.sh benennt die Log-Datei bei API-Fallback/429-Retry auf
eine NEUE lokale Variable um (out="${out%.json}-api-fallback.json") und setzt
am Ende korrekt TEAM_LAST_OUT="$out" — die Aufrufer (frank.sh/axel.sh/
redteam.sh) prüften vor Stufe 35 aber ihre eigene, unveränderte $OUT-Variable,
die weiterhin auf die erste (leere) Datei zeigt.

Dieser Test simuliert genau diese Situation rein über team_promise_in()
(Bash-Funktion + JSON-Fixtures, netz-/CLI-frei) und belegt: $OUT findet das
Promise NICHT, $TEAM_LAST_OUT (die tatsächlich beschriebene Fallback-Datei)
findet es.
"""
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = REPO_ROOT / "team" / "lib.sh"


def _team_promise_in(var_name, out_datei, fallback_datei, promise_text):
    cmd = (
        f'set -euo pipefail; source "{TEAM_LIB}"; '
        f'OUT="{out_datei}"; TEAM_LAST_OUT="{fallback_datei}"; '
        f'team_promise_in "${var_name}" "{promise_text}"'
    )
    result = subprocess.run(["bash", "-c", cmd], cwd=REPO_ROOT)
    return result.returncode == 0


def test_out_misses_promise_but_team_last_out_finds_it(tmp_path):
    out_datei = tmp_path / "frank-HM-20-v1-20260101-000000.json"
    out_datei.write_text(json.dumps({"result": "Abo-Aufruf fehlgeschlagen, API-Fallback wird versucht."}))

    fallback_datei = tmp_path / "frank-HM-20-v1-20260101-000000-api-fallback.json"
    fallback_datei.write_text(json.dumps({"result": "Fix umgesetzt. <promise>FRANK_FIX_COMPLETE</promise>"}))

    assert not _team_promise_in("OUT", out_datei, fallback_datei, "FRANK_FIX_COMPLETE"), (
        "team_promise_in \"$OUT\" sollte das Promise NICHT finden (veraltete Datei)"
    )

    assert _team_promise_in("TEAM_LAST_OUT", out_datei, fallback_datei, "FRANK_FIX_COMPLETE"), (
        "team_promise_in \"$TEAM_LAST_OUT\" muss das Promise in der tatsächlich "
        "beschriebenen Fallback-Datei finden — sonst gilt jeder Fallback-Aufruf "
        "fälschlich als gescheitert (HM-20)."
    )


if __name__ == "__main__":
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        test_out_misses_promise_but_team_last_out_finds_it(Path(d))
    print("gruen — HM-20 (Stufe 35) verifiziert: $TEAM_LAST_OUT wird geprüft, nicht $OUT.")
    sys.exit(0)

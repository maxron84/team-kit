#!/usr/bin/env python3
"""Fixture-Test für HM-33 (Beutebuch) — Frank-Fix in team-lib.sh.

Root-Cause: team_claude() ließ den reinen Prozess-Exit-Code der `claude`-CLI
über ein bereits geschriebenes Erfolgs-JSON (is_error:false) entscheiden.
Endete die CLI mit Exit≠0 (z. B. reine "connectors disabled"-Warnung bei
gesetztem ANTHROPIC_API_KEY), wertete team_claude einen inhaltlich
erfolgreichen, bereits bezahlten Aufruf als Totalfehler.

Rein netz-/CLI-frei (Muster wie test_bl27_abo_key_startwarnung.py): eine
Bash-Funktion `claude` überschreibt die echte CLI und schreibt ein
Stub-Ergebnis auf stdout (landet über die `> "$out"`-Umleitung des
Aufrufers in der Log-Datei) mit konfigurierbarem Exit-Code.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEAM_LIB = REPO_ROOT / "team-lib.sh"


def _run(stub_json, stub_exit, out_path):
    script = f'''
set -uo pipefail
source "{TEAM_LIB}"
claude() {{
    printf '%s' "$STUB_JSON"
    return "$STUB_EXIT"
}}
team_claude "testrolle" "sonnet" "{out_path}" "testprompt"
echo "EXITCODE:$?"
echo "TEAM_LAST_OUT:$TEAM_LAST_OUT"
'''
    env = {
        "HOME": str(Path.home()),
        "PATH": "/usr/bin:/bin",
        "AUTH_MODE": "api",
        "ANTHROPIC_API_KEY": "sk-ant-dummy-test-key",
        "STUB_JSON": stub_json,
        "STUB_EXIT": str(stub_exit),
    }
    return subprocess.run(
        ["bash", "-c", script],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def _exitcode(result):
    for line in result.stdout.splitlines():
        if line.startswith("EXITCODE:"):
            return int(line.split(":", 1)[1])
    raise AssertionError(f"keine EXITCODE-Zeile in stdout:\n{result.stdout}")


def test_erfolgs_json_trotz_exit_ungleich_null_zaehlt_als_erfolg(tmp_path):
    out = tmp_path / "testrolle-20260101-000000.json"
    stub_json = json.dumps({
        "is_error": False,
        "result": "Fix umgesetzt. <promise>STUFE_X_COMPLETE</promise>",
        "total_cost_usd": 0.01,
    })

    result = _run(stub_json, 1, out)

    assert _exitcode(result) == 0, (
        f"team_claude muss bei is_error:false Exit 0 liefern, auch wenn die CLI "
        f"selbst mit Exit≠0 endete (HM-33). stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert f"TEAM_LAST_OUT:{out}" in result.stdout, (
        "TEAM_LAST_OUT muss auf die Datei mit dem Erfolgs-JSON zeigen"
    )
    assert out.exists() and json.loads(out.read_text()).get("is_error") is False
    assert "CLI-Exit≠0 trotz gültigem Erfolgs-JSON" in result.stderr, (
        "ein Exit≠0 trotz Erfolgs-JSON muss sichtbar auf stderr geloggt werden (Fix-Spez. Punkt 3)"
    )


def test_is_error_true_bleibt_fehler(tmp_path):
    out = tmp_path / "testrolle-20260101-000001.json"
    stub_json = json.dumps({"is_error": True, "result": "echter Fehler"})

    result = _run(stub_json, 1, out)

    assert _exitcode(result) == 1, (
        "ein echtes is_error:true MUSS weiterhin als Fehler gelten (kein Kaschieren)"
    )


def test_ungueltiges_json_bleibt_fehler(tmp_path):
    out = tmp_path / "testrolle-20260101-000002.json"

    result = _run("das ist kein JSON", 1, out)

    assert _exitcode(result) == 1, (
        "nicht parsebares Ergebnis bei Exit≠0 muss weiterhin ein Fehler bleiben"
    )


def test_erfolgs_json_bei_exit_null_keine_warnzeile(tmp_path):
    out = tmp_path / "testrolle-20260101-000003.json"
    stub_json = json.dumps({"is_error": False, "result": "ok <promise>X</promise>"})

    result = _run(stub_json, 0, out)

    assert _exitcode(result) == 0
    assert "CLI-Exit≠0 trotz gültigem Erfolgs-JSON" not in result.stderr, (
        "bei sauberem Exit 0 darf keine HM-33-Warnzeile erscheinen"
    )


if __name__ == "__main__":
    import tempfile

    failures = []
    tests = [
        test_erfolgs_json_trotz_exit_ungleich_null_zaehlt_als_erfolg,
        test_is_error_true_bleibt_fehler,
        test_ungueltiges_json_bleibt_fehler,
        test_erfolgs_json_bei_exit_null_keine_warnzeile,
    ]
    for fn in tests:
        with tempfile.TemporaryDirectory() as d:
            try:
                fn(Path(d))
                print(f"OK   {fn.__name__}")
            except AssertionError as e:
                failures.append(fn.__name__)
                print(f"FAIL {fn.__name__}: {e}")
    if failures:
        sys.exit(1)
    print("gruen — HM-33 verifiziert: CLI-Exit-Code überstimmt kein Erfolgs-JSON mehr.")

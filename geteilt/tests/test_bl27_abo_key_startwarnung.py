#!/usr/bin/env python3
"""Fixture-Test für BL-27 (Kaskade 12, Stufe 40) — Auth-Startwarnung.

Belegt Stufe 39 (team/lib.sh): team_resolve_auth_mode warnt einmalig auf
stderr, wenn AUTH_MODE=abo gilt, aber ANTHROPIC_API_KEY in der
Prozess-Umgebung liegt (die Claude-CLI kann dann den teuren API-Weg dem Abo
vorziehen). Rein netz-/CLI-frei über `bash -c` + `subprocess` (Muster wie
test_hm20_promise_reads_last_out.py) — kein echter Claude-Aufruf.
"""
import subprocess
import sys
from pathlib import Path

from conftest import BASH, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = kit_pfad("lib.sh")

DUMMY_KEY = "sk-ant-dummy-test-key-value-should-never-leak"


def _run(bash_script, env_overrides):
    env = {"HOME": str(Path.home()), "PATH": "/usr/bin:/bin"}
    env.update(env_overrides)
    result = subprocess.run(
        [BASH, "-c", bash_script],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    return result


def test_abo_mit_key_warnt_und_leakt_key_nicht():
    result = _run(
        f'source "{TEAM_LIB}"; team_resolve_auth_mode abo',
        {"AUTH_MODE": "abo", "ANTHROPIC_API_KEY": DUMMY_KEY},
    )
    assert "ANTHROPIC_API_KEY" in result.stderr, (
        "abo + gesetzter ANTHROPIC_API_KEY muss auf stderr warnen (BL-27)"
    )
    assert DUMMY_KEY not in result.stderr and DUMMY_KEY not in result.stdout, (
        "Die Warnung darf den Key-Wert NIEMALS ausgeben (Datenleck-Regressionsschutz)"
    )


def test_abo_ohne_key_keine_warnung():
    result = _run(
        f'source "{TEAM_LIB}"; team_resolve_auth_mode abo',
        {"AUTH_MODE": "abo"},
    )
    assert "ANTHROPIC_API_KEY" not in result.stderr, (
        "abo ohne gesetzten Key darf keine Warnung zeigen"
    )


def test_api_modus_mit_key_keine_warnung():
    result = _run(
        f'source "{TEAM_LIB}"; team_resolve_auth_mode',
        {"AUTH_MODE": "api", "ANTHROPIC_API_KEY": DUMMY_KEY},
    )
    assert "ANTHROPIC_API_KEY" not in result.stderr, (
        "im api-Modus ist der Key legitim — keine Warnung erwartet"
    )


def test_warnung_erscheint_nur_einmal_pro_prozessbaum():
    result = _run(
        f'source "{TEAM_LIB}"; team_resolve_auth_mode abo >/dev/null; '
        f'ANTHROPIC_API_KEY="{DUMMY_KEY}" team_resolve_auth_mode abo',
        {"AUTH_MODE": "abo", "ANTHROPIC_API_KEY": DUMMY_KEY},
    )
    assert result.stderr.count("ANTHROPIC_API_KEY liegt in der Prozess-Umgebung") == 1, (
        "der Einmal-Guard TEAM_ABO_KEY_WARNUNG_GEZEIGT muss eine zweite Warnung "
        "im selben Prozessbaum unterdrücken"
    )


if __name__ == "__main__":
    failures = []
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as e:
                failures.append(name)
                print(f"FAIL {name}: {e}")
    if failures:
        sys.exit(1)
    print("gruen — BL-27 (Stufe 40) verifiziert: Startwarnung korrekt, kein Key-Leak, einmalig.")

#!/usr/bin/env python3
"""Fixture-Test für HM-32 (Kaskade 12, Axel-Fall AX-3) — Abo-Key-Warnung über
Sibling-Prozessgrenzen.

Belegt: TEAM_ABO_KEY_WARNUNG_GEZEIGT ist eine Umgebungsvariable und vererbt
sich nur Eltern → Kind, nie Geschwister → Geschwister. vollautomatik.sh/
halbautomatik.sh forken jede Rolle als eigenständigen Sibling-Subprozess, nicht
als verschachtelte Kette — ein in einer Rolle gesetzter Guard erreicht die
nächste Rolle nie. Der Fix seedet den Guard im gemeinsamen Ahnen (analog
team_lock/TEAM_LOCK_HELD), BEVOR die erste Rolle geforkt wird.

Rein netz-/CLI-frei über `bash -c` + `subprocess` (Muster wie
test_bl27_abo_key_startwarnung.py) — kein echter Claude-Aufruf.
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
        text=True, encoding="utf-8", errors="replace",
    )
    return result


def test_ahnen_seed_unterdrueckt_warnung_bei_sibling_kindern():
    # Ahne seedet den Guard EINMAL im eigenen Prozess (wie vollautomatik.sh/
    # halbautomatik.sh es jetzt vor der ersten Rolle tun), danach erben zwei
    # Sibling-Subprozesse (analog ralph.sh, harry.sh) den Guard und schweigen.
    script = (
        f'source "{TEAM_LIB}"; '
        f'team_warnung_abo_key; '
        f'bash -c \'source "{TEAM_LIB}"; team_resolve_auth_mode abo >/dev/null\'; '
        f'bash -c \'source "{TEAM_LIB}"; team_resolve_auth_mode abo >/dev/null\''
    )
    result = _run(script, {"AUTH_MODE": "abo", "ANTHROPIC_API_KEY": DUMMY_KEY})
    count = result.stderr.count("ANTHROPIC_API_KEY liegt in der Prozess-Umgebung")
    assert count == 1, (
        f"Ahnen-Seed muss die Warnung ueber Sibling-Kinder hinweg auf genau 1 "
        f"begrenzen (HM-32-Fix), gezaehlt: {count}\nstderr:\n{result.stderr}"
    )
    assert DUMMY_KEY not in result.stderr and DUMMY_KEY not in result.stdout, (
        "Die Warnung darf den Key-Wert NIEMALS ausgeben"
    )


def test_ohne_ahnen_seed_warnt_jedes_sibling_erneut():
    # Regressions-/Bug-Beleg: OHNE Ahnen-Seed (bewusst kein team_warnung_abo_key
    # im Elternprozess) warnt jedes Sibling erneut, weil der jeweils andere
    # Kindprozess-Guard nie sichtbar wird. Bleibt nach dem Fix wahr — belegt,
    # dass die Unterdrueckung im ersten Test wirklich vom Ahnen-Seed kommt.
    script = (
        f'source "{TEAM_LIB}"; '
        f'bash -c \'source "{TEAM_LIB}"; team_resolve_auth_mode abo >/dev/null\'; '
        f'bash -c \'source "{TEAM_LIB}"; team_resolve_auth_mode abo >/dev/null\''
    )
    result = _run(script, {"AUTH_MODE": "abo", "ANTHROPIC_API_KEY": DUMMY_KEY})
    count = result.stderr.count("ANTHROPIC_API_KEY liegt in der Prozess-Umgebung")
    assert count == 2, (
        f"ohne Ahnen-Seed muss jedes der beiden Sibling-Kinder eigenstaendig "
        f"warnen (dokumentiert HM-32), gezaehlt: {count}\nstderr:\n{result.stderr}"
    )


def test_api_modus_seedet_nicht_trotz_orchestrator_block():
    # Mini-Nachbau des Orchestrator-Seed-Blocks: im reinen api-Modus loest
    # team_auth_mode_effektiv "api" auf, der Seed-Aufruf feuert nicht.
    script = (
        f'source "{TEAM_LIB}"; '
        f'if [ "$(team_auth_mode_effektiv abo)" = "abo" ]; then team_warnung_abo_key; fi; '
        f'bash -c \'source "{TEAM_LIB}"; team_resolve_auth_mode >/dev/null\''
    )
    result = _run(script, {"AUTH_MODE": "api", "ANTHROPIC_API_KEY": DUMMY_KEY})
    count = result.stderr.count("ANTHROPIC_API_KEY liegt in der Prozess-Umgebung")
    assert count == 0, (
        f"im api-Modus ist der Key legitim, der Orchestrator-Seed-Block darf "
        f"nicht feuern, gezaehlt: {count}\nstderr:\n{result.stderr}"
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
    print("gruen — HM-32 verifiziert: Abo-Key-Warnung ueber Sibling-Prozesse korrekt unterdrueckt.")

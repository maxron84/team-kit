#!/usr/bin/env python3
"""BL-48: Die Abo-Key-Startwarnung zeigte nach einem API-Fallback auf die
falsche Ursache — und verbrauchte dabei das Warnfenster des echten Falls.

Feld K29/136 (2026-08-10): Die Warnung "AUTH_MODE=abo, aber ANTHROPIC_API_KEY
liegt in der Prozess-Umgebung" erschien mit der Empfehlung, den Key "aus
.bashrc/der Shell-Env" zu nehmen. In .bashrc lag keiner, und die Umgebung von
vollautomatik.sh enthielt beim Start keinen (per /proc/<pid>/environ waehrend
des Laufs geprueft). Gesetzt hatte ihn der API-Fallback der VORIGEN Stufe:
team_resolve_auth_mode exportiert ihn, und dort steht er fuer die Folgestufe
noch.

Das Verhalten war korrekt (der unset griff, 136-138 liefen im Abo), die
DIAGNOSE war irrefuehrend — sie schickte den Leser in eine Datei, in der nichts
steht. Und weil die Warnung nur EINMAL pro Prozessbaum feuert (BL-27/HM-32),
verbrauchte der Fehlalarm genau das eine Mal, das dem echten Fall zustand:
Dort waren es real ~13,8 USD Leerlauf ueber API.
"""

import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

WURZEL = Path(__file__).resolve().parents[2]
TEAM_LIB = kit_pfad("lib.sh")
DUMMY_KEY = "sk-ant-dummy-test-key-value-should-never-leak"
BASHRC_SATZ = "den Key aus .bashrc/der Shell-Env nehmen"


def _run(script, env_extra):
    env = {"HOME": str(Path.home()), "PATH": "/usr/bin:/bin"}
    env.update(env_extra)
    return subprocess.run(["bash", "-c", f'source "{TEAM_LIB}"\n{script}'],
                          cwd=WURZEL, env=env, capture_output=True, text=True)


def test_selbst_gesetzter_key_bekommt_die_richtige_diagnose():
    ergebnis = _run("team_resolve_auth_mode abo",
                    {"AUTH_MODE": "abo", "ANTHROPIC_API_KEY": DUMMY_KEY,
                     "TEAM_KEY_AUS_FALLBACK": "1"})
    assert "API-Fallback" in ergebnis.stderr, (
        "die Meldung muss die wirkliche Ursache nennen")
    assert BASHRC_SATZ not in ergebnis.stderr, (
        "die .bashrc-Empfehlung zeigt hier auf eine Datei, in der nichts steht")
    assert "BL-48" in ergebnis.stderr
    assert DUMMY_KEY not in ergebnis.stderr + ergebnis.stdout, (
        "der Key-Wert darf nie ausgegeben werden (Regressionsschutz BL-27)")


def test_fehlalarm_verbraucht_das_warnfenster_nicht():
    """Der teure Teil des Fundes: Nach dem Fehlalarm muss der ECHTE Fall im
    selben Prozessbaum noch warnen koennen."""
    ergebnis = _run(
        "team_resolve_auth_mode abo >/dev/null; "
        f'TEAM_KEY_AUS_FALLBACK=0 ANTHROPIC_API_KEY="{DUMMY_KEY}" '
        "team_resolve_auth_mode abo",
        {"AUTH_MODE": "abo", "ANTHROPIC_API_KEY": DUMMY_KEY,
         "TEAM_KEY_AUS_FALLBACK": "1"})
    assert BASHRC_SATZ in ergebnis.stderr, (
        "der echte Fall muss danach noch warnen duerfen — der Fehlalarm darf "
        "TEAM_ABO_KEY_WARNUNG_GEZEIGT nicht setzen")


def test_geerbter_key_warnt_unveraendert():
    """Gegenprobe: Ohne die Fallback-Marke bleibt die BL-27-Warnung
    unangetastet scharf. Sie ist die teurere der beiden Lagen."""
    ergebnis = _run("team_resolve_auth_mode abo",
                    {"AUTH_MODE": "abo", "ANTHROPIC_API_KEY": DUMMY_KEY})
    assert BASHRC_SATZ in ergebnis.stderr
    assert "API-Fallback" not in ergebnis.stderr


def test_marke_wird_beim_laden_aus_der_keydatei_gesetzt(tmp_path):
    """Die Marke muss dort entstehen, wo der Key wirklich exportiert wird —
    sonst haengt der Fix an einer Stelle, die eine spaetere Aenderung uebersieht."""
    heim = tmp_path / "heim"
    (heim / ".config" / "claude-team").mkdir(parents=True)
    (heim / ".config" / "claude-team" / "api-key").write_text(DUMMY_KEY + "\n")
    ergebnis = _run(
        'team_resolve_auth_mode >/dev/null; printf "MARKE:%s" "${TEAM_KEY_AUS_FALLBACK:-0}"',
        {"AUTH_MODE": "api", "HOME": str(heim)})
    assert "MARKE:1" in ergebnis.stdout, (
        f"team_resolve_auth_mode markiert den selbst geladenen Key nicht:\n"
        f"{ergebnis.stdout}\n{ergebnis.stderr}")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))

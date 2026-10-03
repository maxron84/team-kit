#!/usr/bin/env python3
"""BL-238: `kosten.py` liest `TEAM_PREISE` aus der Projektkonfiguration, wenn
die Umgebung den Wert nicht kennt.

DER FELDBEFUND (`Feld B`, 2026-09-07)
    Das Architekten-Briefing nennt fuer den Kostenabschluss den DIREKTaufruf
    `python3 team/tools/kosten.py sitzung-messen --projekt .`. `TEAM_PREISE`
    exportiert aber nur die Shell-Konfiguration. Ergebnis: *„159 von 161
    nachgerechneten Laeufen weichen ab"*, alle um 33,3 % — mit vorangestelltem
    `TEAM_PREISE=…` war dieselbe Sitzung *„geeicht an 161 Laeufen"*. Die
    Diagnose zeigte auf die Preistabelle; der Fehler sass im Aufrufweg.

WAS DIESER TEST PRUEFT
    Beide Schreibweisen der Vorlagen werden gelesen, `--projekt` zeigt auf die
    Wurzel, und die Umgebung gewinnt — auch eine LEERE: Wer die Konfiguration
    geladen hat, hat entschieden.
"""
import os
import subprocess
import sys

import pytest

from conftest import kit_pfad

TOOLS = kit_pfad("tools")


def _uebersteuerung(cwd, *argv, env_preise=None):
    umgebung = {k: v for k, v in os.environ.items() if k != "TEAM_PREISE"}
    if env_preise is not None:
        umgebung["TEAM_PREISE"] = env_preise
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import kosten; "
            "kosten._KONFIG_WURZEL = sys.argv[2]; "
            "print(sorted(kosten.preis_uebersteuerung().items()))")
    wurzel = argv[0] if argv else "."
    r = subprocess.run([sys.executable, "-c", code, str(TOOLS), str(wurzel)],
                       cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", env=umgebung)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


@pytest.mark.parametrize("datei,zeile", [
    ("team.config.sh", 'TEAM_PREISE="${TEAM_PREISE:-claude-sonnet-5=3.00}"'),
    ("team.config.sh", 'TEAM_PREISE="claude-sonnet-5=3.00"'),
    ("team.config.ps1", "$TEAM_PREISE = Team-Wert 'TEAM_PREISE' 'claude-sonnet-5=3.00'"),
    ("team.config.ps1", "$TEAM_PREISE = 'claude-sonnet-5=3.00'"),
])
def test_beide_schreibweisen_werden_gelesen(tmp_path, datei, zeile):
    (tmp_path / datei).write_text(f"# Konfiguration\n{zeile}\n",
                                  encoding="utf-8")
    assert _uebersteuerung(tmp_path) == "[('claude-sonnet-5', 3.0)]"


def test_der_auslieferungswert_ist_leer(tmp_path):
    (tmp_path / "team.config.sh").write_text(
        'TEAM_PREISE="${TEAM_PREISE:-}"\nexport TEAM_PREISE\n', encoding="utf-8")
    assert _uebersteuerung(tmp_path) == "[]"


def test_die_umgebung_gewinnt_auch_leer(tmp_path):
    """Wer die Konfiguration geladen hat, hat entschieden — eine zweite
    Quelle darf das nicht ueberstimmen."""
    (tmp_path / "team.config.sh").write_text(
        'TEAM_PREISE="claude-sonnet-5=3.00"\n', encoding="utf-8")
    assert _uebersteuerung(tmp_path, env_preise="") == "[]"
    assert _uebersteuerung(tmp_path, env_preise="claude-opus-5=4.00") == \
        "[('claude-opus-5', 4.0)]"


def test_projekt_zeigt_auf_die_wurzel(tmp_path):
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    (projekt / "team.config.sh").write_text(
        'TEAM_PREISE="claude-sonnet-5=3.00"\n', encoding="utf-8")
    anderswo = tmp_path / "anderswo"
    anderswo.mkdir()
    assert _uebersteuerung(anderswo) == "[]"
    assert _uebersteuerung(anderswo, str(projekt)) == "[('claude-sonnet-5', 3.0)]"


def test_main_setzt_die_wurzel_aus_projekt(tmp_path):
    """Der Weg des Feldes: `sitzung-messen --projekt <pfad>` von woanders."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import kosten; "
            "kosten._main(['turns', '--projekt', sys.argv[2]]); "
            "print(kosten._KONFIG_WURZEL)")
    r = subprocess.run([sys.executable, "-c", code, str(TOOLS), "PROJEKT-X"],
                       cwd=tmp_path, capture_output=True, text=True,
                       encoding="utf-8")
    assert r.stdout.strip().endswith("PROJEKT-X"), r.stdout + r.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

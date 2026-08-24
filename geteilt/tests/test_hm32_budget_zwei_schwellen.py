#!/usr/bin/env python3
"""Fixture-Test für das Zwei-Schwellen-Budget-Modell (HM-32).

Stakeholder-Entscheid 2026-07-12: Der alte 1-USD-Frank-Cap griff ERST NACH
dem (bereits bezahlten) Claude-Aufruf und warf über den Rollback die schon
bezahlte Arbeit weg — der Cap "sparte" nichts, sondern vervielfachte die Kosten
und blockierte den Fund (realer Auslöser: HM-32, Frank Versuch 2 kostete
1,44 USD >= 1 USD → Fehlversuch trotz plausiblem Fix).

Neues Modell in team/lib.sh:
  - Zentrale Basiszahlen TEAM_ROLE_BUDGET_USD=5 (Soft, alle Rollen) und
    TEAM_ROLE_HARDCAP_USD=10 (Hard, Frank/Axel).
  - team_budget_check <kosten> <soft> <label> [hard] gibt vier Zustände zurück:
      0 = ok, 1 = Warnschwelle (80 % soft), 2 = Soft-Cap überschritten,
      3 = Hard-Cap überschritten (nur mit hard>soft).

Dieser Test ruft team_budget_check rein über die Bash-Funktion auf
(subprocess, netz-/CLI-frei) und belegt alle Übergänge sowie die zentralen
Defaults.
"""
import re
import subprocess
from pathlib import Path

from conftest import RufCode, Variable, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = kit_pfad("lib.sh")


def _budget_check(schale, kosten, soft, hard=None):
    """Ruft team_budget_check auf und gibt (returncode, stdout) zurück.

    RufCode statt Ruf: Die Funktion staffelt 0/1/2/3 (ok, Warnschwelle,
    Soft-Cap, Hard-Cap). Ein auf 0/1 eingedampfter Code waere hier still
    falsch — Soft- und Hard-Cap saehen gleich aus.
    """
    args = [kosten, soft, "test"] + ([hard] if hard is not None else [])
    ergebnis = schale.lauf(RufCode("team_budget_check", *args), cwd=REPO_ROOT)
    return ergebnis.returncode, ergebnis.stdout


def _lib_default(schale, name):
    """Liest den BIBLIOTHEKS-Default aus team/lib.sh — die Zeile
    `NAME="${NAME:-wert}"` statt des aufgeloesten Wertes.

    Warum statisch und nicht per `source`: team/lib.sh laedt in ihren ersten
    Zeilen selbst die team.config.sh des Projekts, und die setzt dieselben
    Variablen. Ein `source team/lib.sh; echo $NAME` liefert deshalb NICHT den
    Bibliotheks-Default, sondern den PROJEKTWERT — obwohl team.config.sh
    genau die Datei ist, in der ein Projekt seine Caps anpassen soll und die
    `install.sh --update` bewusst ueberlebt.

    Gefunden am 2026-08-09 (Feld A, Untersuchung BL-100): Das
    Projekt hob seinen Soft-Cap regelkonform in team.config.sh von 5 auf 10 —
    und brach damit diesen Kit-Test, der eine Kit-Zusicherung zu pruefen
    behauptete. Die Zusicherung selbst bleibt richtig und wird hier
    unveraendert weitergefuehrt; nur die Messstelle war die falsche.
    """
    quelle = schale.kit_lib.read_text(encoding="utf-8")
    treffer = re.search(schale.default_muster(name), quelle, re.M)
    assert treffer, \
        f"{name} nicht als Default-Zeile in {schale.lib_name} gefunden"
    return treffer.group(1)


# --- Zentrale Defaults --------------------------------------------------------

def test_zentrale_defaults(schale):
    assert _lib_default(schale, "TEAM_ROLE_BUDGET_USD") == "5", "Soft-Cap-Default muss 5 sein"
    assert _lib_default(schale, "TEAM_ROLE_HARDCAP_USD") == "10", "Hard-Cap-Default muss 10 sein"


def test_projektwert_haelt_das_hard_groesser_soft_verhaeltnis(schale):
    """Der Hard-Cap MUSS ueber dem Soft-Cap liegen — sonst prueft
    team_budget_check ihn nie (`hard > soft`) und Frank/Axel verlieren ihren
    harten Abbruch still. Diese Pruefung gilt fuer die AUFGELOESTEN Werte,
    also inklusive der Projektanpassung in team.config.sh — anders als
    test_zentrale_defaults, das den Bibliotheks-Default prueft."""
    ergebnis = schale.lauf(
        Variable("TEAM_ROLE_BUDGET_USD", "TEAM_ROLE_HARDCAP_USD"),
        cwd=REPO_ROOT)
    soft, hard = (float(v) for v in ergebnis.stdout.split())
    assert hard > soft, (
        f"Hard-Cap {hard} muss groesser als Soft-Cap {soft} sein — bei "
        f"hard == soft ist der harte Abbruch fuer Frank/Axel wirkungslos")


# --- Zwei-Zustand-Modus (ohne hard-limit): Ralph/Harry/Marv -------------------

def test_ok_unter_warnschwelle(schale):
    rc, _ = _budget_check(schale, "2.00", "5")
    assert rc == 0


def test_warnschwelle_80_prozent(schale):
    rc, out = _budget_check(schale, "4.00", "5")  # 4 >= 0.8*5
    assert rc == 1
    assert "WARNSCHWELLE" in out


def test_soft_ueberschritten_ohne_hard_ist_rc2(schale):
    # Ohne hard-limit ist RC 2 der "harte" Fall für Ralph/Harry/Marv.
    rc, out = _budget_check(schale, "5.50", "5")
    assert rc == 2
    assert "SOFT-CAP" in out


# --- Drei-Zustand-Modus (mit hard-limit): Frank/Axel --------------------------

def test_soft_ueberschritten_mit_hard_bleibt_rc2(schale):
    # HM-32-Fall: 5,50 USD zwischen Soft (5) und Hard (10) → nur Hinweis (RC 2),
    # KEIN Abbruch. Genau das, was den 1,44-USD-Fehlversuch verhindert hätte.
    rc, out = _budget_check(schale, "5.50", "5", "10")
    assert rc == 2
    assert "SOFT-CAP" in out


def test_der_reale_hm32_fall_unter_neuem_soft_ist_ok(schale):
    # Der konkrete Auslöser: 1,44 USD ist unter dem neuen Soft-Cap 5 → RC 0.
    rc, _ = _budget_check(schale, "1.44", "5", "10")
    assert rc == 0


def test_hard_ueberschritten_ist_rc3(schale):
    rc, out = _budget_check(schale, "10.50", "5", "10")
    assert rc == 3
    assert "HARD-CAP" in out


def test_genau_am_hard_cap_ist_rc3(schale):
    rc, _ = _budget_check(schale, "10.00", "5", "10")
    assert rc == 3


if __name__ == "__main__":
    test_zentrale_defaults()
    test_ok_unter_warnschwelle()
    test_warnschwelle_80_prozent()
    test_soft_ueberschritten_ohne_hard_ist_rc2()
    test_soft_ueberschritten_mit_hard_bleibt_rc2()
    test_der_reale_hm32_fall_unter_neuem_soft_ist_ok()
    test_hard_ueberschritten_ist_rc3()
    test_genau_am_hard_cap_ist_rc3()
    print("gruen — HM-32 Zwei-Schwellen-Budget verifiziert (Soft 5 / Hard 10, RC 0/1/2/3).")

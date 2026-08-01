#!/usr/bin/env python3
"""Fixture-Test für das Zwei-Schwellen-Budget-Modell (HM-32).

Strippenzieher-Entscheid 2026-07-12: Der alte 1-USD-Frank-Cap griff ERST NACH
dem (bereits bezahlten) Claude-Aufruf und warf über den Rollback die schon
bezahlte Arbeit weg — der Cap "sparte" nichts, sondern vervielfachte die Kosten
und blockierte den Fund (realer Auslöser: HM-32, Frank Versuch 2 kostete
1,44 USD >= 1 USD → Fehlversuch trotz plausiblem Fix).

Neues Modell in team-lib.sh:
  - Zentrale Basiszahlen TEAM_ROLE_BUDGET_USD=5 (Soft, alle Rollen) und
    TEAM_ROLE_HARDCAP_USD=10 (Hard, Frank/Axel).
  - team_budget_check <kosten> <soft> <label> [hard] gibt vier Zustände zurück:
      0 = ok, 1 = Warnschwelle (80 % soft), 2 = Soft-Cap überschritten,
      3 = Hard-Cap überschritten (nur mit hard>soft).

Dieser Test ruft team_budget_check rein über die Bash-Funktion auf
(subprocess, netz-/CLI-frei) und belegt alle Übergänge sowie die zentralen
Defaults.
"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEAM_LIB = REPO_ROOT / "team-lib.sh"


def _budget_check(kosten, soft, hard=None):
    """Ruft team_budget_check auf und gibt (returncode, stdout) zurück."""
    args = f'"{kosten}" "{soft}" "test"'
    if hard is not None:
        args += f' "{hard}"'
    cmd = f'source "{TEAM_LIB}"; team_budget_check {args}'
    result = subprocess.run(
        ["bash", "-c", cmd], cwd=REPO_ROOT,
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout


def _var(name):
    """Liest den Default-Wert einer team-lib.sh-Variable (ohne Env-Override)."""
    cmd = f'source "{TEAM_LIB}"; printf "%s" "${{{name}}}"'
    result = subprocess.run(
        ["bash", "-c", cmd], cwd=REPO_ROOT,
        capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"},
    )
    return result.stdout.strip()


# --- Zentrale Defaults --------------------------------------------------------

def test_zentrale_defaults():
    assert _var("TEAM_ROLE_BUDGET_USD") == "5", "Soft-Cap-Default muss 5 sein"
    assert _var("TEAM_ROLE_HARDCAP_USD") == "10", "Hard-Cap-Default muss 10 sein"


# --- Zwei-Zustand-Modus (ohne hard-limit): Ralph/Harry/Marv -------------------

def test_ok_unter_warnschwelle():
    rc, _ = _budget_check("2.00", "5")
    assert rc == 0


def test_warnschwelle_80_prozent():
    rc, out = _budget_check("4.00", "5")  # 4 >= 0.8*5
    assert rc == 1
    assert "WARNSCHWELLE" in out


def test_soft_ueberschritten_ohne_hard_ist_rc2():
    # Ohne hard-limit ist RC 2 der "harte" Fall für Ralph/Harry/Marv.
    rc, out = _budget_check("5.50", "5")
    assert rc == 2
    assert "SOFT-CAP" in out


# --- Drei-Zustand-Modus (mit hard-limit): Frank/Axel --------------------------

def test_soft_ueberschritten_mit_hard_bleibt_rc2():
    # HM-32-Fall: 5,50 USD zwischen Soft (5) und Hard (10) → nur Hinweis (RC 2),
    # KEIN Abbruch. Genau das, was den 1,44-USD-Fehlversuch verhindert hätte.
    rc, out = _budget_check("5.50", "5", "10")
    assert rc == 2
    assert "SOFT-CAP" in out


def test_der_reale_hm32_fall_unter_neuem_soft_ist_ok():
    # Der konkrete Auslöser: 1,44 USD ist unter dem neuen Soft-Cap 5 → RC 0.
    rc, _ = _budget_check("1.44", "5", "10")
    assert rc == 0


def test_hard_ueberschritten_ist_rc3():
    rc, out = _budget_check("10.50", "5", "10")
    assert rc == 3
    assert "HARD-CAP" in out


def test_genau_am_hard_cap_ist_rc3():
    rc, _ = _budget_check("10.00", "5", "10")
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

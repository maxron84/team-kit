#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer zwei Funde am Selbsttest der
Erstinstallation, beide am selben Trockenlauf aufgefallen:

BL-127 — `team_pytest()` war INNERHALB des `--update`-Blocks definiert.
    Bash definiert eine Funktion erst, wenn die Definition ausgefuehrt
    wird. Auf dem Erstinstallations-Pfad wurde der Block nie betreten, der
    Selbsttest rief eine Funktion auf, die es nicht gab
    ("team_pytest: command not found"), fing den Fehlschlag im `if` ab und
    meldete "pytest nicht gefunden — Regressionstests uebersprungen".
    Jede frische Installation hat damit ihre Regressionstests
    UEBERSPRUNGEN — genau die Pruefung, fuer die `BL-124` gebaut wurde, tot
    auf dem Weg, auf dem sie am meisten zaehlt. Die Einrueckung tarnte es:
    Die Funktion stand in Spalte 0 und sah nach oberster Ebene aus.
    Die pwsh-Bahn war NICHT betroffen (dort steht `Finde-Pytest` oben) —
    also stille Drift zwischen zwei Fassungen derselben Lehre.

BL-128 — der Selbsttest lief mit einem UNGEPRUEFTEN Glob.
    `for f in "$ZIEL"/*.sh` reicht bei null Treffern das MUSTER selbst
    durch; `bash -n "$ZIEL/*.sh"` scheitert dann an einer Datei namens
    "*.sh", und der Installer meldet "Syntaxfehler: *.sh" samt Exit 1. Das
    trifft jede mit `--nur-pwsh` installierte Ablage: Dort GIBT es keine
    .sh, und das ist kein Defekt, sondern die Abwahl (`BL-119`). Ein
    Installer, der eine gelungene Installation als kaputt meldet,
    verbrennt das Vertrauen in jede weitere Meldung.

Den LAUF fuehrt `kit-test.sh` (Stufe 2: der Selbsttest muss seine Tests
wirklich gefahren haben; Stufe 8: eine nur-pwsh-Installation meldet keinen
Syntaxfehler). Hier steht die Zusicherung am Quelltext — sie laeuft auch
dort, wo keine Installation gefahren werden kann.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO_ROOT / "bash" / "install.sh"


def _quelle():
    if not INSTALL_SH.is_file():
        pytest.skip("bash/install.sh liegt hier nicht (installiertes Projekt)")
    return INSTALL_SH.read_text(encoding="utf-8")


def test_team_pytest_ist_vor_dem_update_block_definiert():
    quelle = _quelle()
    zeilen = quelle.splitlines()
    def zeile_von(muster):
        for i, z in enumerate(zeilen):
            if re.match(muster, z):
                return i
        return None

    definition = zeile_von(r"^team_pytest\(\) \{")
    update_block = zeile_von(r'^if \[ "\$UPDATE" -eq 1 \]; then')
    assert definition is not None, "team_pytest() gibt es nicht mehr"
    assert update_block is not None, "Der --update-Block ist nicht mehr auffindbar"
    assert definition < update_block, (
        f"team_pytest() steht in Zeile {definition + 1}, der --update-Block "
        f"beginnt in Zeile {update_block + 1}. Damit ist die Funktion auf dem "
        "Erstinstallations-Pfad nicht definiert, und der Selbsttest "
        "ueberspringt seine Regressionstests (BL-127).")


def test_beide_selbsttests_pruefen_den_glob_vor_dem_syntaxcheck():
    """Nicht nur EINER der beiden Selbsttests — der Update-Pfad hat einen
    eigenen, und ein Fix an nur einer Stelle ist genau die halbe Arbeit,
    die BL-128 ueberhaupt erst entstehen liess."""
    quelle = _quelle()
    schleifen = re.findall(
        r'for f in "\$ZIEL"/\*\.sh; do\n(.*?)\n\s*done', quelle, re.S)
    assert len(schleifen) == 2, (
        f"Erwartet werden zwei .sh-Selbsttestschleifen (Erstinstallation und "
        f"Update), gefunden: {len(schleifen)}")
    for i, koerper in enumerate(schleifen, 1):
        assert re.search(r'\[ -e "\$f" \] \|\| continue', koerper), (
            f"Schleife {i} prueft nicht, ob der Glob ueberhaupt getroffen hat. "
            "In einer nur-pwsh-Ablage meldet der Installer dann "
            "'Syntaxfehler: *.sh' und Exit 1 ueber eine gelungene "
            "Installation (BL-128).")


def test_die_leere_ablage_wird_als_abwahl_gemeldet_nicht_als_fehler():
    """Ein stiller Uebersprung waere die andere Haelfte des Fehlers: Wer
    nichts liest, glaubt, die Skripte seien geprueft worden."""
    quelle = _quelle()
    assert quelle.count("keine .sh zu pruefen (Bash-Bahn abgewaehlt)") == 2, (
        "Beide Selbsttests muessen die leere Ablage BENENNEN — einmal die "
        "Erstinstallation, einmal das Update (BL-128).")

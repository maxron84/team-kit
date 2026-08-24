#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer BL-126: Der Update-Pfad beider
Installer erkannte eine Installation NUR an `team.config.sh`.

Ein mit `--nur-pwsh` installiertes Projekt hat diese Datei nicht. Der
Installer erklaerte es fuer keine Installation ("sieht nicht nach einer
T.E.A.M.-Installation aus") und stieg mit Exit 2 aus — BEVOR er die
fehlende Bahn nachziehen konnte. Damit war der Rueckweg, den `BL-119`
ausdruecklich verspricht ("ein Update holt eine fehlende Bahn zurueck"
— seit `BL-147` auf ausdrueckliche Anforderung, `--beide-bahnen`), in
dieser Richtung versperrt: Die Abwahl war die
Einbahnstrasse, die sie nicht sein darf.

Warum es durchrutschte, ist in `kit-test.sh` Stufe 8 ablesbar: Der
Rueckweg war bewiesen — fuer `--nur-bash`. Also fuer die Richtung, in der
die Datei, an der alles haengt, zufaellig vorhanden ist.

DIE ARBEITSTEILUNG DIESER DATEI
    Den LAUF fuehrt `kit-test.sh` Stufe 8 (installieren, aktualisieren,
    nachsehen) — dort ist er hingehoert, weil er zwei echte Installationen
    braucht. Hier steht die Zusicherung am QUELLTEXT, und zwar fuer BEIDE
    Bahnen: Der Lauf kann die pwsh-Fassung auf einer Maschine ohne
    PowerShell nicht pruefen, und genau dort ist der Fehler aufgetreten
    (`BL-117`-Lage). Ein statischer Vergleich laeuft ueberall.
"""
import re
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]


def _installer(name):
    """Der Installer beider Bahnen liegt im KIT, nicht im Projekt — ein
    installiertes Projekt traegt ihn gar nicht. Fehlt er, wird
    uebersprungen statt falsch gruen gemeldet."""
    for kandidat in (REPO_ROOT / "bash" / "install.sh", REPO_ROOT / "pwsh" / "install.ps1"):
        if kandidat.name == name and kandidat.is_file():
            return kandidat.read_text(encoding="utf-8-sig")
    pytest.skip(f"{name} liegt hier nicht (installiertes Projekt statt Kit-Ablage)")


def test_bash_installer_erkennt_auch_eine_reine_pwsh_installation():
    quelle = _installer("install.sh")
    # Die Abbruchbedingung muss BEIDE Fassungen verlangen, nicht eine.
    assert re.search(
        r'if \[ ! -f "\$ZIEL/team\.config\.sh" \] && \[ ! -f "\$ZIEL/team\.config\.ps1" \]',
        quelle), (
        "Der --update-Pfad bricht ab, sobald team.config.sh fehlt. Ein mit "
        "--nur-pwsh installiertes Projekt ist damit nicht mehr "
        "aktualisierbar — der BL-119-Rueckweg ist versperrt (BL-126).")


def test_bash_installer_liest_die_werte_notfalls_aus_der_ps1():
    quelle = _installer("install.sh")
    assert "team.config.ps1" in quelle and "Team-Wert" in quelle, (
        "Fehlt team.config.sh, stehen die Projektwerte NUR in der .ps1. Ohne "
        "einen Weg, sie dort zu lesen, faellt das Update auf die "
        "Auslieferungswerte zurueck — die zurueckgeholte Bahn bekaeme eine "
        "andere Guard-Grenze als die, die schon laeuft (BL-126).")


def test_pwsh_installer_erkennt_auch_eine_reine_pwsh_installation():
    """Dieselbe Zusicherung auf der Bahn, auf der der Fehler zuschlug. Sie
    wiegt dort schwerer: Ein Windows-Projekt OHNE bash ist der Normalfall,
    fuer den die pwsh-Bahn gebaut ist."""
    quelle = _installer("install.ps1")
    assert re.search(
        r'if \(-not \(Test-Path \$configSh\) -and -not \(Test-Path \$configPs1\)\)',
        quelle), (
        "Der -Update-Pfad bricht ab, sobald team.config.sh fehlt (BL-126).")
    assert "$konfQuelle = 'team.config.ps1'" in quelle, (
        "Ohne Lesepfad fuer team.config.ps1 kennt das Update die Projektwerte "
        "nicht und faellt auf die Auslieferungswerte zurueck (BL-126).")


def test_beide_bahnen_nennen_die_quelle_der_werte():
    """Aus WELCHER Konfiguration die Werte stammen, entscheidet, welche
    Guard-Grenze die Briefings bekommen. Das gehoert in die Ausgabe — sonst
    ist ein Rueckfall auf die Auslieferungswerte nicht zu bemerken."""
    for name, muster in (("install.sh", r'Projektwerte aus \$KONF_QUELLE gelesen'),
                         ("install.ps1", r'Projektwerte aus \$konfQuelle gelesen')):
        quelle = _installer(name)
        assert re.search(muster, quelle), (
            f"{name} nennt die Quelle der Projektwerte nicht (BL-126).")

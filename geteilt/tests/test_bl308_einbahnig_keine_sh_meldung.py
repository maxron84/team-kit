#!/usr/bin/env python3
"""BL-308: Der Selbsttest des pwsh-Installers behauptete in einer einbahnigen
Ablage, die .sh-Entrypoints seien "mitinstalliert".

DER BEFUND (`Feld F`, 2026-10-04)
    Ein mit `-NurPwsh` gefuehrtes Projekt bekam beim Update — zwei Zeilen
    unter "Einbahnige Ablage erkannt: nur die pwsh-Bahn" — den Satz "Die
    .sh-Entrypoints wurden NICHT geprueft — hier liegt keine bash. Sie sind
    mitinstalliert und gelten unveraendert aus dem Kit." Es gab keine einzige
    .sh-Datei. install.sh kennt die Lage seit BL-128 und sagt "keine .sh zu
    pruefen (Bash-Bahn abgewaehlt)"; der pwsh-Installer sagte den Satz
    unbedingt, in der Erstinstallation wie im Update.

DIE PROBE
    Am Quelltext, wie test_bl127 fuer install.sh: Beide Selbsttests des
    pwsh-Installers benennen die leere Ablage, und der Satz ueber die
    mitinstallierten Entrypoints steht nur noch im Zweig, in dem es sie gibt.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _quelle():
    pfad = REPO_ROOT / "pwsh" / "install.ps1"
    if not pfad.is_file():
        pytest.skip("install.ps1 liegt nur im Kit")
    return pfad.read_text(encoding="utf-8-sig")


def test_beide_selbsttests_benennen_die_leere_ablage():
    quelle = _quelle()
    assert quelle.count("keine .sh zu pruefen (Bash-Bahn abgewaehlt)") == 2, (
        "Erstinstallation UND Update muessen eine Ablage ohne .sh als Abwahl "
        "benennen — wie install.sh seit BL-128 (Kit-BL-308).")


def test_der_satz_ueber_die_entrypoints_steht_nur_im_zweig_mit_sh():
    """Jede Stelle, die 'mitinstalliert' sagt, steht im else-Zweig einer
    Abfrage nach *.sh in der Ablage."""
    zeilen = _quelle().splitlines()
    stellen = [i for i, z in enumerate(zeilen) if "Sie sind mitinstalliert" in z]
    assert len(stellen) == 2, stellen
    for i in stellen:
        davor = "\n".join(zeilen[max(0, i - 6):i])
        assert re.search(r"Filter '\*\.sh'", davor) and "} else {" in davor, (
            f"install.ps1:{i + 1} sagt 'mitinstalliert', ohne vorher nach .sh "
            f"in der Ablage gefragt zu haben (Kit-BL-308):\n{davor}")

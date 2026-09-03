#!/usr/bin/env python3
"""BL-223: Die Rollen-Skripte lasen ihre Argumente ueberhaupt nicht — `--hilfe`
startete einen bezahlten Rollenlauf.

WIE DER FUND ENTSTAND
    Beim Abtragen von BL-222 (`team-status` nimmt jede unbekannte Flagge und
    meldet Erfolg) kam die Frage auf, ob die uebrigen Einstiegspunkte eine
    Hilfe haben. Nachgemessen: Von vierzehn hatten DREI eine — install.sh,
    kit-einrichten.sh und (seit BL-222) team-status.sh.

    Der schwerere Teil lag darunter: `ralph.sh`, `harry.sh`, `marv.sh`,
    `frank.sh` und `axel.sh` lesen `$@`/`$args` an keiner Stelle. Sie werfen
    Argumente nicht weg — sie sehen sie nie. `./ralph.sh --hilfe` zeigte also
    keine Hilfe, wies nichts zurueck und **startete einen bezahlten
    Rollenlauf**.

WARUM DAS SCHWERER WIEGT ALS BL-222
    Dort war die Folge eine falsche Statusausgabe und ein nicht gebuchter
    Kostenposten; hier ist es ein Modellaufruf, den niemand bestellt hat. Und
    es trifft genau den Moment, in dem jemand das Kit zum ersten Mal anfasst:
    `--hilfe` ist das Erste, was ein Mensch tippt.

WAS DIESER TEST PRUEFT
    Die GATTUNG, nicht die Liste (Lehre aus BL-198/BL-208): Jeder
    ausgelieferte Entrypoint muss auf `--hilfe` mit Exit 0 und einer nicht
    leeren Ausgabe antworten. Neue Entrypoints fallen damit automatisch auf,
    statt still ohne Bedienung zu bleiben.

    Dazu die zwei Gegenproben, ohne die der Riegel Schaden anrichtet: Der
    ARGUMENTLOSE Aufruf bleibt unangetastet (davon haengt jede Automatik ab),
    und die beiden pytest-Durchreichen duerfen ihre Argumente weiterhin
    durchreichen.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import BASH, entrypoint_pfad, kit_pfad, verlange_bash

REPO_ROOT = Path(__file__).resolve().parents[2]

# Die Rollen kennen KEINE Argumente — bei ihnen ist jedes uebergebene Wort ein
# Irrtum, und der Irrtum kostet einen Modellaufruf.
OHNE_ARGUMENTE = ["ralph", "harry", "marv", "frank", "axel"]
# Diese kennen Argumente, brauchen aber dieselbe Hilfe.
MIT_ARGUMENTEN = ["vollautomatik", "halbautomatik", "team-status"]
# Diese reichen an pytest durch: nur `--hilfe`, kein Riegel.
DURCHREICHEN = ["team-test"]

ALLE = OHNE_ARGUMENTE + MIT_ARGUMENTEN + DURCHREICHEN


def _sh(name):
    pfad = Path(entrypoint_pfad(f"{name}.sh"))
    if not pfad.is_file():
        pytest.skip(f"{name}.sh liegt in dieser Ablage nicht (einbahnig installiert)")
    return pfad


@pytest.fixture(scope="module")
def projekt(tmp_path_factory):
    """Eine echte, einbahnige Installation — die Hilfe wird GEFAHREN, nicht
    aus dem Quelltext gelesen. Ein statischer Test haette den Fund nicht
    gefunden: Der Kopf stand ja da, gelesen hat ihn nur niemand."""
    verlange_bash()
    installer = REPO_ROOT / "bash" / "install.sh"
    if not installer.is_file():
        pytest.skip("install.sh liegt in dieser Ablage nicht")
    ziel = tmp_path_factory.mktemp("bl223")
    subprocess.run(["git", "-C", str(ziel), "init", "-q"], check=True,
                   capture_output=True)
    r = subprocess.run([BASH, str(installer), str(ziel), "--nicht-interaktiv",
                        "--nur-bash", "--ohne-selbsttest"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if r.returncode != 0:
        pytest.skip(f"Installation fuer das Fixture schlug fehl: {r.stderr[-400:]}")
    return ziel


def _lauf(projekt, skript, *args):
    return subprocess.run([BASH, f"./{skript}.sh", *args], cwd=projekt,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


# --- Der Fall aus dem Fund ---------------------------------------------------

@pytest.mark.parametrize("skript", ALLE)
def test_jeder_entrypoint_antwortet_auf_hilfe(projekt, skript):
    _sh(skript)
    r = _lauf(projekt, skript, "--hilfe")
    assert r.returncode == 0, (
        f"./{skript}.sh --hilfe endet mit {r.returncode} statt 0.\n"
        f"{r.stdout[-400:]}{r.stderr[-400:]}")
    assert r.stdout.strip(), f"./{skript}.sh --hilfe druckt nichts"


@pytest.mark.parametrize("skript", OHNE_ARGUMENTE + MIT_ARGUMENTEN)
def test_hilfe_kommt_aus_dem_dateikopf(projekt, skript):
    """Keine zweite Fassung daneben — sonst laeuft sie auseinander (BL-154).
    Die Probe: Die erste Zeile der Hilfe nennt die Datei selbst."""
    _sh(skript)
    r = _lauf(projekt, skript, "--hilfe")
    assert r.stdout.lstrip().startswith(f"{skript}.sh"), (
        f"die Hilfe von {skript}.sh beginnt nicht mit ihrem eigenen Dateikopf:\n"
        f"{r.stdout[:200]}")


@pytest.mark.parametrize("skript", OHNE_ARGUMENTE)
def test_ein_unbekanntes_argument_startet_keinen_rollenlauf(projekt, skript):
    """DER Fund. Vor dem Fix lief hier ein bezahlter Modellaufruf an."""
    r = _lauf(projekt, skript, "--voelliger-unsinn-xyz")
    assert r.returncode == 2, (
        f"./{skript}.sh nimmt ein unbekanntes Argument entgegen "
        f"(Exit {r.returncode}) — das ist ein Rollenlauf, den niemand "
        f"bestellt hat.\n{r.stdout[-400:]}")
    assert "--voelliger-unsinn-xyz" in r.stderr, \
        "die Meldung muss nennen, WAS nicht erkannt wurde"


@pytest.mark.parametrize("schalter", ["--hilfe", "--help", "-h"])
def test_alle_drei_schreibweisen_tragen(projekt, schalter):
    """`--help` und `-h` sind das, was ein englischsprachiger Anwender tippt."""
    _sh("ralph")
    r = _lauf(projekt, "ralph", schalter)
    assert r.returncode == 0, f"ralph.sh {schalter}: Exit {r.returncode}"
    assert r.stdout.strip()


# --- Die Gegenproben, ohne die der Riegel Schaden anrichtet ------------------

def test_die_durchreiche_an_pytest_bleibt_offen(projekt):
    """`team-test.sh` reicht seine Argumente an pytest durch. Ein Riegel
    gegen unbekannte Argumente faenge hier genau das, wofuer es die
    Durchreiche gibt — deshalb faengt sie NUR `--hilfe` ab."""
    _sh("team-test")
    r = _lauf(projekt, "team-test", "-k", "zzz_gibt_es_nicht")
    assert "deselected" in (r.stdout + r.stderr), (
        "die pytest-Argumente kommen nicht mehr an:\n"
        f"{r.stdout[-500:]}{r.stderr[-500:]}")


def test_help_und_h_gehoeren_bei_der_durchreiche_pytest(projekt):
    """Bewusst NICHT abgefangen: pytest hat dafuer eine eigene, bessere
    Hilfe. Abgefangen wird nur die deutsche Schreibweise, die pytest nicht
    kennt — die Aufteilung steht so im Dateikopf."""
    _sh("team-test")
    r = _lauf(projekt, "team-test", "--help")
    assert "usage: pytest" in (r.stdout + r.stderr).lower() or r.returncode == 0, (
        "team-test.sh --help erreicht pytest nicht mehr:\n"
        f"{r.stdout[:300]}")


def test_argumentloser_aufruf_bleibt_unberuehrt():
    """Die wichtigste Gegenprobe, und sie wird an der BIBLIOTHEK gefahren
    statt an den Rollen: Ein argumentloser `./ralph.sh` waere ein echter,
    bezahlter Lauf. Geprueft wird die Weiche selbst."""
    verlange_bash()
    lib = kit_pfad("lib.sh")
    if not lib.is_file():
        pytest.skip("team/lib.sh liegt in dieser Ablage nicht")
    skript = (f'source "{lib}" >/dev/null 2>&1\n'
              'team_argumente_pruefen\n'
              'echo WEITER\n')
    r = subprocess.run([BASH, "-c", skript], capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       cwd=str(lib.parent.parent))
    assert r.returncode == 0 and "WEITER" in r.stdout, (
        "team_argumente_pruefen bricht ohne Argument ab — damit stuende jede "
        f"Automatik still.\n{r.stdout}{r.stderr}")


# --- Gleichstand der Bahnen --------------------------------------------------

@pytest.mark.parametrize("skript", OHNE_ARGUMENTE)
def test_die_pwsh_bahn_traegt_denselben_riegel(skript):
    """`BL-155`/`BL-156`/`BL-178` waren alle dieselbe Gattung: eine fehlende
    Haelfte. Auf Windows ist die einbahnige pwsh-Ablage der Normalfall."""
    pfad = Path(entrypoint_pfad(f"{skript}.ps1"))
    if not pfad.is_file():
        pytest.skip(f"{skript}.ps1 liegt in dieser Ablage nicht")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "Team-BedienungPruefen" in text, (
        f"{skript}.ps1 prueft seine Argumente nicht (BL-223)")
    assert "BL-223" in text, (
        f"{skript}.ps1 nennt die Herkunft des Riegels nicht — ohne sie ist er "
        "beim naechsten Umbau eine unmotivierte Zeile")

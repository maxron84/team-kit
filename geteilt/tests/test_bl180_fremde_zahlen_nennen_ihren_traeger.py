#!/usr/bin/env python3
"""BL-180: Der README-Zahlenwächter konnte die Testzahl des KITS nicht von der
eines FELDPROJEKTS unterscheiden.

DIE STRENGE IST BEGRÜNDET, DIE BLINDE STELLE WAR ES NICHT
    `kit-readme-pruefen.py` prüft absichtlich die GATTUNG: jede Zahl vor
    `Tests`/`Testfälle`/`Fälle`/`Regressionstests` gegen die an einer frischen
    Installation gemessene Fallzahl. Ein drittes „369 Regressionstests" in
    freier Prosa war wochenlang unbemerkt veraltet — daher die Strenge.

    Die Herkunftstabelle des README beschreibt aber **fremde** Projekte, und
    deren Zahlen sind völlig legitime **andere** Zahlen. Der Eintrag zu einem
    Feldprojekt nannte „86 Tests" — die Tests jenes Projekts. Der Wächter las
    sie als Behauptung über das Kit und schlug rot an.

    **Kein Schönheitsfehler:** `kit-test.sh` Stufe 3 bricht daran ab, nach
    rund 45 Minuten Laufzeit. Ein Selbsttest, der an einer **richtigen**
    Angabe stirbt, ist teurer als einer, der gar nicht prüft.

WARUM NICHT DIE TABELLE AUSNEHMEN
    Das wäre die naheliegende Lösung und die schlechtere: Sie blendet aus,
    statt zu schärfen, und die nächste fremde Zahl außerhalb der Tabelle fällt
    wieder durch. Stattdessen muss eine Zahl über ein fremdes Projekt ihren
    **Träger** nennen. Der Wächter prüft dann weiter **jede** unqualifizierte
    Zahl — und eine unqualifizierte Zahl **ist** eine Aussage über das Kit.

DIE GEGENPROBE, DIE DER EINTRAG VERLANGT
    Eine Herkunftszeile mit blanker Zahl muss rot schlagen, dieselbe Zeile mit
    benanntem Träger grün — **und eine veraltete Kit-Zahl muss weiterhin rot
    schlagen**, sonst ist der Wächter mit dem Fix stumpf geworden.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WERKZEUG = REPO_ROOT / "geteilt" / "kit-readme-pruefen.py"

pytestmark = pytest.mark.skipif(
    not WERKZEUG.is_file(),
    reason="kit-readme-pruefen.py liegt in dieser Ablage nicht (kein Kit)")


def _lauf(tmp_path, text, faelle=100):
    p = tmp_path / "readme.md"
    p.write_text(text, encoding="utf-8", newline="\n")
    return subprocess.run(
        [sys.executable, str(WERKZEUG), "--readme", str(p),
         "--faelle", str(faelle)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})


KIT_ZEILE = "Das Kit hat 100 Tests.\n"


@pytest.mark.parametrize("fremde", [
    "Feld E lief mit 86 Tests in Feld E.",
    "Feld E lief mit 86 Projekt-Tests.",
    "Ein Projekt mit 86 Tests des Projekts.",
    "Gemessen: 86 Fälle in jenem Projekt.",
])
def test_eine_zahl_mit_benanntem_traeger_ist_gruen(tmp_path, fremde):
    """Der Weg, den der Fix eröffnet — und der nächste Autor muss ihn finden."""
    r = _lauf(tmp_path, KIT_ZEILE + fremde + "\n")
    assert r.returncode == 0, (
        f"Eine Zahl mit benanntem Träger schlägt an:\n{r.stdout}{r.stderr}")


def test_eine_blanke_fremde_zahl_schlaegt_rot(tmp_path):
    """Die Strenge bleibt: Ohne Träger IST es eine Aussage über das Kit."""
    r = _lauf(tmp_path, KIT_ZEILE + "Feld E lief mit 86 Tests.\n")
    assert r.returncode != 0, (
        f"Eine blanke fremde Zahl geht durch — dann ist die Regel keine:\n"
        f"{r.stdout}{r.stderr}")


def test_der_befund_nennt_den_ausweg(tmp_path):
    """Ein Wächter, der eine Formregel erzwingt, muss die Form auch zeigen.

    Sonst formuliert der nächste Autor die Zahl weg, statt sie zu
    qualifizieren — und genau das war die Sofortmaßnahme, die BL-180 als
    „Vermeidung, keine Lösung" bezeichnet.
    """
    r = _lauf(tmp_path, KIT_ZEILE + "Feld E lief mit 86 Tests.\n")
    assert "Träger" in r.stdout + r.stderr, (
        f"Der Befund sagt nicht, wie man es richtig schreibt:\n"
        f"{r.stdout}{r.stderr}")


def test_eine_veraltete_kit_zahl_schlaegt_weiter_rot(tmp_path):
    """Die wichtigste Gegenprobe: Der Fix darf den Wächter nicht stumpf machen.

    Genau dafür war er gebaut — ein drittes „369 Regressionstests" in freier
    Prosa stand wochenlang falsch da.
    """
    r = _lauf(tmp_path, "Das Kit hat 99 Tests.\n")
    assert r.returncode != 0, (
        f"Eine veraltete Kit-Zahl geht durch:\n{r.stdout}{r.stderr}")


def test_des_kits_ist_kein_fremder_traeger(tmp_path):
    """Sonst ließe sich der Wächter mit drei Wörtern abschalten."""
    r = _lauf(tmp_path, KIT_ZEILE + "Früher waren es 99 Tests des Kits.\n")
    assert r.returncode != 0, (
        f"»des Kits« hat die Prüfung abgeschaltet:\n{r.stdout}{r.stderr}")


def test_das_echte_readme_ist_gruen():
    """Die Zusicherung am lebenden Objekt — sie ist der Grund für den Eintrag.

    `kit-test.sh` Stufe 3 fährt genau diesen Aufruf, und ein roter Lauf kostet
    dort rund 45 Minuten, bevor er auffällt.
    """
    r = subprocess.run(
        [sys.executable, str(WERKZEUG)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO_ROOT),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"

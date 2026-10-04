#!/usr/bin/env python3
"""BL-313: Die Desktop-Meldung sagt den AUSGANG, nicht den Zwischenstand.

DER HERGANG (am Quelltext belegt, 2026-10-04, beim Bau von `BL-312`)
    Der Benachrichtigungsblock stand VOR der Gate-Pruefung aus `BL-256`. Ein
    Lauf mit rotem Gate setzte deshalb *„T.E.A.M. Vollautomatik fertig —
    Kaskade durch"* ab und endete zwei Bloecke weiter mit
    `=== LAUF BEENDET — GATE ROT ===` und Exit 44.

WARUM DAS MEHR IST ALS EIN SCHOENHEITSFEHLER
    Die Benachrichtigung ist fuer den ABWESENDEN gebaut — sie erreicht genau
    den Menschen, der den Abschlussbericht nicht liest, weil er nicht am
    Schirm sass. `BL-256` wurde eingefuehrt, damit ein Lauf sich nicht als
    fertig meldet, waehrend das Gate aus ist. Der eine Kanal, der den
    Abwesenden erreicht, tat genau das weiter — an der leisesten Stelle.

GEPRUEFT AM LAUF (Stub-Rollen, `notify-send` als Stub im PATH)
    Rotes Gate -> die Meldung nennt GATE ROT und NICHT "Kaskade durch".
    Gruenes Gate -> unveraendert "Kaskade durch".
"""
import os
import subprocess

import pytest

import test_bl217_phasen_zeiger as h
from conftest import BASH, pfad_voran, verlange_bash

GATE = ".team-gate-rot"
NOTIFY_STUB = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "{log}"
"""


def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    return h._projekt(repo)


def _notify_stub(tmp_path):
    bin_dir = tmp_path / "stubbin"
    bin_dir.mkdir()
    log = tmp_path / "notify.log"
    stub = bin_dir / "notify-send"
    stub.write_text(NOTIFY_STUB.format(log=log.as_posix()), encoding="utf-8")
    stub.chmod(0o755)
    return bin_dir, log


def _lauf(repo, bin_dir):
    """Der Lauf meldet hier BEWUSST — geprueft wird ja der Wortlaut.

    `TEAM_BENACHRICHTIGUNG=1` hebt den Riegel aus `BL-312` fuer genau diesen
    Prozess auf; der Stub im PATH haelt die Meldung vom echten Desktop fern.
    """
    return subprocess.run(
        [BASH, "./vollautomatik.sh"], cwd=repo, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_BUDGET_USD="99",
                 TEAM_BENACHRICHTIGUNG="1", PATH=pfad_voran(bin_dir)))


@pytest.mark.nur_bash(
    "Die Desktop-Meldung gibt es nur im bash-Entrypoint; die pwsh-Bahn "
    "kennt keine Benachrichtigung.")
def test_ein_rotes_gate_meldet_nicht_kaskade_durch(tmp_path):
    """Der Fund: derselbe Lauf, zwei Aussagen — eine davon falsch."""
    verlange_bash()
    repo = _repo(tmp_path)
    bin_dir, log = _notify_stub(tmp_path)
    (repo / GATE).write_text(
        "2026-09-10T14:03:00 | frank | test_alt_waechter\n", encoding="utf-8")

    r = _lauf(repo, bin_dir)

    assert r.returncode == 44, (r.stdout + r.stderr)
    assert log.exists(), (
        "Ein Lauf mit rotem Gate meldet sich gar nicht mehr — der Abwesende "
        "erfaehrt dann NICHTS, und das ist die schlechtere Haelfte des "
        f"Fundes.\n{r.stdout}")
    gemeldet = log.read_text(encoding="utf-8")
    assert "Kaskade durch" not in gemeldet, (
        "Der Lauf endete mit Exit 44 und GATE ROT, die Meldung sagt trotzdem "
        f"'Kaskade durch':\n{gemeldet}")
    assert "GATE ROT" in gemeldet, gemeldet
    assert "14:03" in gemeldet, (
        "Die Meldung nennt den Zeitpunkt nicht — *seit wann* ist die halbe "
        f"Aussage (wie im Bericht, BL-256):\n{gemeldet}")


@pytest.mark.nur_bash("Gegenrichtung zum Fall oben — dieselbe Begruendung.")
def test_ohne_gate_bleibt_die_meldung_wie_sie_war(tmp_path):
    """Gegenrichtung: Der Normalfall darf sich nicht veraendert haben.

    Eine Meldung, die jeden Lauf als Problem ausweist, ist so wertlos wie
    eine, die jeden als fertig ausweist (BL-14).
    """
    verlange_bash()
    repo = _repo(tmp_path)
    bin_dir, log = _notify_stub(tmp_path)

    r = _lauf(repo, bin_dir)

    assert r.returncode == 0, (r.stdout + r.stderr)
    gemeldet = log.read_text(encoding="utf-8")
    assert "Kaskade durch" in gemeldet, gemeldet
    assert "GATE ROT" not in gemeldet, gemeldet

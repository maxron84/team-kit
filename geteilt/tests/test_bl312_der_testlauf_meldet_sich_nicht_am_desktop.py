#!/usr/bin/env python3
"""BL-312: Ein Testlauf meldet sich nicht am Desktop des Menschen.

DER HERGANG (`Feld F`, 2026-10-04, Debian/GNOME, bash-Bahn)
    Der Benachrichtigungsfeed der Sitzung stand voll mit identischen
    Meldungen *„T.E.A.M. Vollautomatik fertig — Kaskade durch. Dieser Lauf:
    0.0000 USD"*, alle mit Zeitstempel *Just now*. Es lief kein Lauf. Was
    lief, war `pytest geteilt/tests`.

    Der Abschlussblock von `vollautomatik.sh` rief `notify-send`
    ungefiltert. Die Kaskadentests starten den Entrypoint aber mit der
    ECHTEN Umgebung des Wirts (`env=dict(os.environ, …)`, z. B.
    `test_bl217_phasen_zeiger`, `test_bl241_…`), also samt `PATH` und
    D-Bus-Adresse — fuer die Desktop-Sitzung ist jede Stub-Kaskade ein
    fertiger Lauf.

    GEMESSEN, nicht geschaetzt: Ein Durchgang `pytest geteilt/tests` setzte
    **20** Benachrichtigungen ab (19 ueber `0.0000 USD`, eine ueber
    `1.0000 USD` aus der Kostenmessung). `kit-test.sh` faehrt die Suite
    fuenfmal, macht 100 je Selbsttest.

WARUM DAS JEDE INSTALLATION TRIFFT
    `team/tests/` wird mitinstalliert. Jedes Feldprojekt auf einem Linux-
    Desktop bekommt dieselbe Flut, sobald jemand `./team-test.sh` aufruft —
    der Befehl, zu dem die Doku als Gegenprobe ausdruecklich raet.

    Auf der pwsh-Bahn gibt es die Meldung nicht; der Mangel ist deshalb
    bash-eigen, nicht Drift.

DER RIEGEL
    `TEAM_BENACHRICHTIGUNG` — Default `1`, damit ein echter Lauf weiter
    meldet. Der Harnisch setzt in `conftest.py` hart `0`, auf BEIDEN Wegen,
    ueber die ein Test seine Umgebung baut (`os.environ` und
    `basis_umgebung()`).
"""
import os
import subprocess

import pytest

import test_bl217_phasen_zeiger as h
from conftest import BASH, basis_umgebung, pfad_voran, verlange_bash

NOTIFY_STUB = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "{log}"
"""


def _repo(tmp_path):
    """`h._projekt` erwartet einen vorhandenen Ordner — es ruft `git init`
    darin, nicht darauf."""
    repo = tmp_path / "repo"
    repo.mkdir()
    return h._projekt(repo)


def _notify_stub(tmp_path):
    """Ein `notify-send`, das statt des Desktops eine Datei beschreibt.

    Der echte Befehl darf im Test nicht laufen — sonst prueft der Test den
    Mangel, indem er ihn begeht.
    """
    bin_dir = tmp_path / "stubbin"
    bin_dir.mkdir()
    log = tmp_path / "notify.log"
    stub = bin_dir / "notify-send"
    stub.write_text(NOTIFY_STUB.format(log=log.as_posix()), encoding="utf-8")
    stub.chmod(0o755)
    return bin_dir, log


def _lauf(repo, bin_dir, **env):
    return subprocess.run(
        [BASH, "./vollautomatik.sh"], cwd=repo, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_BUDGET_USD="99",
                 PATH=pfad_voran(bin_dir), **env))


@pytest.mark.nur_bash(
    "Die Desktop-Meldung gibt es nur im bash-Entrypoint; die pwsh-Bahn "
    "kennt keine Benachrichtigung, es gibt dort nichts zu unterdruecken.")
def test_der_harnisch_laesst_keine_benachrichtigung_durch(tmp_path):
    """Der Feldfall: ein Testlauf, gestartet wie die Kaskadentests starten."""
    verlange_bash()
    repo = _repo(tmp_path)
    bin_dir, log = _notify_stub(tmp_path)

    r = _lauf(repo, bin_dir)

    assert "ABSCHLUSSBERICHT" in r.stdout + r.stderr, r.stdout + r.stderr
    assert not log.exists(), (
        "Der Lauf hat sich am Desktop gemeldet, obwohl conftest.py "
        "TEAM_BENACHRICHTIGUNG=0 setzt — gemeldet wurde:\n"
        + log.read_text(encoding="utf-8"))


@pytest.mark.nur_bash(
    "Gegenprobe zum Riegel oben — dieselbe Begruendung.")
def test_ohne_den_riegel_meldet_der_lauf_sehr_wohl(tmp_path):
    """Die Gegenprobe: Der Schalter unterdrueckt, er zerstoert nicht.

    Ohne sie bliebe offen, ob der Test oben die Benachrichtigung abschaltet
    oder bloss das Messen — ein Riegel, der die Meldung fuer JEDEN Lauf
    killt, waere kein Fix, sondern ein zweiter Mangel.
    """
    verlange_bash()
    repo = _repo(tmp_path)
    bin_dir, log = _notify_stub(tmp_path)

    r = _lauf(repo, bin_dir, TEAM_BENACHRICHTIGUNG="1")

    assert "ABSCHLUSSBERICHT" in r.stdout + r.stderr, r.stdout + r.stderr
    assert log.exists(), (
        "Mit TEAM_BENACHRICHTIGUNG=1 kam keine Meldung — der Riegel hat die "
        "Benachrichtigung nicht unterdrueckt, sondern abgeschafft.")
    assert "Vollautomatik fertig" in log.read_text(encoding="utf-8")


def test_beide_umgebungswege_tragen_den_riegel():
    """Zwei Wege bauen die Umgebung eines Tests — beide muessen ihn tragen.

    `basis_umgebung()` erbt `os.environ` BEWUSST nicht (sie haelt TEAM_*-Werte
    der Wirtssitzung heraus). Ein Riegel in nur einem der beiden Wege laesst
    die Haelfte der Tests weiter melden.
    """
    assert os.environ.get("TEAM_BENACHRICHTIGUNG") == "0", (
        "conftest.py setzt TEAM_BENACHRICHTIGUNG nicht auf 0 — jede "
        "Testkaskade meldet sich dann am Desktop des Menschen.")
    assert basis_umgebung().get("TEAM_BENACHRICHTIGUNG") == "0", (
        "basis_umgebung() nennt TEAM_BENACHRICHTIGUNG nicht — der Entrypoint "
        "faellt dort auf seinen Default 1 zurueck.")

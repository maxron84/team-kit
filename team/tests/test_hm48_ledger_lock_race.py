#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer HM-48: `_ledger_zeile_setzen()`
(team/tools/kosten.py) machte ein Read-Modify-Write ohne jede Sperre. Zwei
ueberlappende Kaskaden-Abschluss-Aufrufe (akteur-abschluss/rollen-abschluss)
konnten sich gegenseitig eine gerade erst geschriebene Zeile kommentarlos
wieder herausreissen (Lost Update), weil der zweite Aufruf noch die alte
Datei-Version im Speicher hatte, als er schrieb.

Der Fix (`_ledger_lock()`) haelt fuer die gesamte Lesen+Schreiben-Spanne
einen exklusiven `flock` auf eine feste Lock-Datei neben dem Ledger, sodass
ein zweiter Aufruf blockiert statt mit einem veralteten Snapshot zu
ueberschreiben.

Simuliert die Race durch einen verlangsamten `tempfile.mkstemp()` (haelt den
kritischen Bereich laenger offen) und zwei echte Threads, die konkurrierend
schreiben. Netz-/CLI-frei gegen ein temporaeres Fixture-Ledger, nie gegen die
echte .budget-ledger — Muster wie test_hm47_mehrdeutige_ersetzung.py/
test_hm39_rollen_abschluss_race.py.
"""
import sys
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
sys.path.insert(0, str(REPO_ROOT / "team" / "tools"))
import kosten  # noqa: E402


def _fixture_ledger(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text("# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    return pfad


def test_akteur_abschluss_race_verliert_keine_zeile(tmp_path, monkeypatch):
    pfad = _fixture_ledger(tmp_path)

    orig_mkstemp = kosten.tempfile.mkstemp

    def langsamer_mkstemp(*args, **kwargs):
        time.sleep(0.2)
        return orig_mkstemp(*args, **kwargs)

    monkeypatch.setattr(kosten.tempfile, "mkstemp", langsamer_mkstemp)

    fehler = []

    def schreiber(rolle):
        try:
            kosten.akteur_abschluss(
                1.0, "team", "19", rolle, "api", notiz="race-test",
                pfad=str(pfad))
        except Exception as exc:  # pragma: no cover - nur bei echtem Bug
            fehler.append(exc)

    t1 = threading.Thread(target=schreiber, args=("architekt",))
    t2 = threading.Thread(target=schreiber, args=("frank",))
    t1.start()
    time.sleep(0.05)  # sicherstellen, dass t1 bereits im kritischen Bereich haengt
    t2.start()
    t1.join()
    t2.join()

    assert not fehler, fehler
    rollen = {z["rolle"] for z in kosten.ledger_zeilen(str(pfad))}
    # Kern-Invariante: BEIDE Zeilen ueberleben -- ohne die Sperre reisst der
    # zweite (spaeter schreibende) Aufruf die Zeile des ersten heraus.
    assert rollen == {"architekt", "frank"}


def test_rollen_abschluss_race_gegen_akteur_abschluss_verliert_keine_zeile(
        tmp_path, monkeypatch):
    """Die Sperre gilt kaskaden-/rollen-uebergreifend: auch ein
    akteur-abschluss (Architekt) und ein rollen-abschluss (Roles) fuer
    dieselbe Kaskade duerfen sich nicht gegenseitig verschlucken (siehe
    Beutebuch-Szenario: architekt-Aufruf vs. rollen-abschluss-Aufruf)."""
    pfad = _fixture_ledger(tmp_path)

    orig_mkstemp = kosten.tempfile.mkstemp

    def langsamer_mkstemp(*args, **kwargs):
        time.sleep(0.2)
        return orig_mkstemp(*args, **kwargs)

    monkeypatch.setattr(kosten.tempfile, "mkstemp", langsamer_mkstemp)

    fehler = []

    def architekt_schreiber():
        try:
            kosten.akteur_abschluss(
                2.5, "team", "19", "architekt", "abo", notiz="race-test",
                pfad=str(pfad))
        except Exception as exc:  # pragma: no cover
            fehler.append(exc)

    def rollen_schreiber():
        try:
            kosten.rollen_abschluss(
                "19", abo=0.3, api=0.2, domaene="team", notiz="race-test",
                pfad=str(pfad))
        except Exception as exc:  # pragma: no cover
            fehler.append(exc)

    t1 = threading.Thread(target=architekt_schreiber)
    t2 = threading.Thread(target=rollen_schreiber)
    t1.start()
    time.sleep(0.05)
    t2.start()
    t1.join()
    t2.join()

    assert not fehler, fehler
    rollen = {z["rolle"] for z in kosten.ledger_zeilen(str(pfad))}
    assert rollen == {"architekt", "roles"}

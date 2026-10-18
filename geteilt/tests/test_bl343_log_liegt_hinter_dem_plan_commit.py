#!/usr/bin/env python3
"""BL-343: `test_bl220::test_passende_nummer_bucht_ohne_murren` flackerte — die
mtime eines Logs kann VOR dem Commit-Zeitstempel liegen, obwohl das Log danach
geschrieben wurde, und dann gilt es als "aelter als die Kaskade".

WAS PASSIERT IST (Kit, 2026-10-17, Nachweislauf der Triage)
    Der Lauf war an genau diesem Fall rot (`1 Log(s) sind AELTER als der
    Beginn der Kaskade 11 … es wird NICHTS gebucht`); zwoelf Wiederholungen
    waren gruen, und die Aenderungen davor fassten keinen Code an.

WARUM
    Die Fixture committet den Plan und schreibt das Log gleich danach.
    `logs_vor_kaskadenbeginn` vergleicht `mtime < beginn`, und `beginn` ist
    die Commit-Zeit in GANZEN Sekunden (`%ct`). Der Kernel stempelt die mtime
    mit einer groben Uhr, die der Systemzeit um Millisekunden nachlaufen kann.
    Faellt der Commit knapp hinter eine Sekundengrenze, liegt die mtime des
    spaeteren Logs davor. Auf der Triage-Maschine gemessen: 973 von 366724
    Versuchen "Zeit nehmen, dann Datei schreiben".

WAS BLEIBT, UND WAS SICH AENDERT
    Die Produktivlogik bleibt streng: Ein Log aus der Sekunde vor dem
    Plan-Commit gehoert wirklich nicht zur Kaskade (BL-45), und im Betrieb
    liegen Minuten dazwischen. Die FIXTURE setzt die mtime ihres Logs
    ausdruecklich hinter den Commit (`log_nach_dem_plan_commit` in
    `conftest.py`), statt der Uhr zu vertrauen.

WIE DIESER TEST DIE LAGE HERSTELLT, statt auf das Flackern zu warten
    Er gibt dem Log beim Schreiben die mtime, die die grobe Uhr ihm geben
    KANN — eine Millisekunde vor der Commit-Sekunde — und prueft zuerst, dass
    `kosten.py` es damit wirklich fuer aelter haelt. Dann muss die Fixture
    die Lage aufheben, und die Buchung geht durch.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

import test_bl220_kaskadennummer_gegen_den_plan as bl220
import test_bl321_kaskade_aus_plan_kennt_beide_praefixe as bl321

kosten = bl220.kosten


def _commit_sekunde(repo):
    r = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%ct"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", check=True)
    return int(r.stdout.strip())


@pytest.fixture
def grobe_uhr(monkeypatch):
    """Jedes Log, das eine Fixture schreibt, bekommt die mtime eine
    Millisekunde vor der Commit-Sekunde — die Lage aus BL-343, ohne Zufall.

    Rueckgabe: je gestempeltem Log, ob `kosten.py` es mit dieser mtime fuer
    aelter als die Kaskade hielt."""
    schreiben = Path.write_text
    befunde = []

    def mit_grober_uhr(pfad, *args, **kwargs):
        ergebnis = schreiben(pfad, *args, **kwargs)
        if pfad.suffix == ".json" and pfad.parent.name in (".team-logs",
                                                           ".ralph-logs"):
            repo = pfad.parent.parent
            zeit = _commit_sekunde(repo) - 0.001
            os.utime(pfad, (zeit, zeit))
            kaskade = kosten.kaskade_aus_plan(str(repo))
            _, zu_alt = kosten.logs_vor_kaskadenbeginn([str(pfad)], kaskade,
                                                       str(repo))
            befunde.append(bool(zu_alt))
        return ergebnis

    monkeypatch.setattr(Path, "write_text", mit_grober_uhr)
    return befunde


FIXTUREN = {
    "test_bl220": (lambda p: bl220._repo(p, plan_nummer="11"),
                   lambda repo: bl220._buche(repo, kaskade="11")),
    "test_bl321": (lambda p: bl321._projekt(p, "team-kaskade-11-produkt.md"),
                   lambda repo: bl321._buche(repo, "11")),
}


@pytest.mark.parametrize("modul", sorted(FIXTUREN))
def test_die_fixture_haelt_ihr_log_hinter_dem_plan_commit(tmp_path, grobe_uhr,
                                                          modul):
    anlegen, buchen = FIXTUREN[modul]
    repo = anlegen(tmp_path)
    assert grobe_uhr and all(grobe_uhr), (
        "Vorbedingung: Mit einer mtime eine Millisekunde vor der "
        "Commit-Sekunde muss kosten.py das Log fuer aelter halten — sonst "
        "stellt dieser Fall die Lage aus BL-343 nicht her (oder der "
        f"Produktivvergleich ist aufgeweicht, BL-45). Befunde: {grobe_uhr}")
    r = buchen(repo)
    assert r.returncode == 0, (
        f"Die Fixture aus {modul} laesst ihr Log vor dem Plan-Commit liegen — "
        "die passende Kaskadennummer bucht nicht, und der Fall flackert "
        f"(Kit-BL-343):\n{r.stdout}{r.stderr}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

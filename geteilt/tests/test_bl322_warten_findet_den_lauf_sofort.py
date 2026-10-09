#!/usr/bin/env python3
"""BL-322: `smoke_warten.py warten` direkt nach `start` fand den Lauf nicht —
die Logdatei legte erst das abgekoppelte Kind an.

WAS GEMELDET WURDE (`Feld B`, 2026-10-08)
    `test_bl232::test_warten_meldet_laeuft_noch_dann_den_exitcode` war mit
    dem Interpreter eines venv reproduzierbar rot (2 von 2) und mit dem
    System-Python gruen: `start` endete mit 0, das sofort folgende `warten`
    mit 2 und *„kein Smoke-Lauf gefunden — zuerst `smoke_warten.py start`"*.
    Unter Windows ist das `python.exe` eines venv ein Starter, der den
    Basis-Interpreter als weiteren Prozess startet; das Kind braucht deshalb
    spuerbar laenger, bis es `smoke-<id>.log` anlegt.

WARUM DAS MEHR IST ALS EIN FLACKERNDER TEST
    Briefings und Regeldatei nennen `start`, dann sofort `warten` als den
    Zwei-Schritt-Weg (`BL-273`/`BL-281`). Rät `warten` „zuerst `start`", liegt
    einer Rolle ein zweites `start` nahe — dann laufen zwei Suiten
    nebeneinander, und es kommt genau zu der Kollision, vor der `BL-207`
    warnt.

WIE HIER GEMESSEN WIRD
    Der Wettlauf ist auf keinem Wirt verlässlich zu verlieren — also wird er
    ausgeschaltet: `start` läuft im Prozess, und das Starten des Kindes ist
    durch einen Platzhalter ersetzt, der NICHTS startet. Das ist die Lage im
    ungünstigsten Augenblick: `start` ist zurück, das Kind hat noch keine
    Zeile geschrieben. Gegen den alten Stand gemessen: `warten` endete mit 2.
"""
import importlib.util
import os
import sys

import pytest

from conftest import kit_pfad

SMOKE_WARTEN = kit_pfad("tools", "smoke_warten.py")


@pytest.fixture
def werkzeug(tmp_path, monkeypatch):
    if not SMOKE_WARTEN.is_file():
        pytest.skip("smoke_warten.py liegt hier nicht")
    spec = importlib.util.spec_from_file_location("smoke_warten_bl322",
                                                  SMOKE_WARTEN)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    monkeypatch.chdir(tmp_path)
    gestartet = []

    class KindKommtSpaeter:
        """Nimmt den Start entgegen und tut nichts — das Kind ist noch nicht
        so weit, eine Datei anzulegen."""
        def __init__(self, argv, **_optionen):
            gestartet.append(argv)

    monkeypatch.setattr(modul.subprocess, "Popen", KindKommtSpaeter)
    modul.gestartet = gestartet
    return modul


def _kennung(capsys):
    return capsys.readouterr().out.strip().splitlines()[0]


def test_warten_ohne_kennung_sieht_den_eben_gestarteten_lauf(werkzeug, capsys):
    assert werkzeug.start("python -m pytest -q") == 0
    assert werkzeug.gestartet, "der Platzhalter wurde nie gerufen"
    rc = werkzeug.warten(None, 0.3)
    assert rc == werkzeug.LAEUFT_NOCH, (
        f"warten endete mit {rc} statt {werkzeug.LAEUFT_NOCH} (laeuft noch). "
        "Mit 2 raet es 'zuerst start' — und ein zweites start stellt zwei "
        "Suiten nebeneinander (Kit-BL-207).")
    assert "zuerst" not in capsys.readouterr().err


def test_warten_mit_kennung_sieht_den_eben_gestarteten_lauf(werkzeug, capsys):
    assert werkzeug.start("python -m pytest -q") == 0
    kennung = _kennung(capsys)
    rc = werkzeug.warten(kennung, 0.3)
    assert rc == werkzeug.LAEUFT_NOCH, (
        f"warten {kennung} endete mit {rc} — 'kein Lauf mit der Kennung', "
        "obwohl start sie eben gedruckt hat.")


def test_die_logdatei_liegt_vor_dem_start_des_kindes(werkzeug, capsys):
    """Die Zusicherung selbst: Wenn das Kind gestartet wird, gibt es die
    Datei schon — und sie ist leer, das Kind schreibt sie voll."""
    assert werkzeug.start("python -m pytest -q") == 0
    kennung = _kennung(capsys)
    log = os.path.join(".team-logs", f"smoke-{kennung}.log")
    assert os.path.isfile(log)
    assert os.path.getsize(log) == 0
    assert werkzeug.gestartet[0][3] == os.path.join(".team-logs",
                                                    f"smoke-{kennung}.log")


def test_ohne_start_bleibt_es_ein_bedienfehler(werkzeug, capsys):
    """Die Gegenrichtung: Ohne jeden Lauf ist 2 weiter die richtige Antwort —
    sonst wartete `warten` auf etwas, das nie kommt."""
    assert werkzeug.warten(None, 0.3) == 2
    assert "start" in capsys.readouterr().err


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

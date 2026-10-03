#!/usr/bin/env python3
"""BL-239, BL-244, BL-245, BL-249: Der Rollen-Abschluss bucht nur ganz oder
gar nicht, ersetzt nie durch Null, und eine Notiz muss durch keine Shell.

BL-239 (`Feld B`, 2026-09-07)
    `--rollen-abschluss` ist EINE Bedienhandlung mit ZWEI Verben (BL-4). Der
    BL-221-Riegel hielt die Rollen-Haelfte an und meldete *„es wird NICHTS
    gebucht und NICHTS archiviert"* — die Bau-Haelfte war da bereits gebucht
    und `.ralph-logs` archiviert. Jetzt prueft der Wrapper BEIDE Haelften mit
    `--nur-pruefen`, bevor er eine davon bucht.

BL-244 (`Feld B`, 2026-09-09)
    Der korrigierende Zweitaufruf mit `--ersetzen` fand `.ralph-logs` leer,
    warnte — und ersetzte 6,7523 USD durch 0.0000. Ersetzt wird nie durch Null.

BL-245 / BL-249 (`Feld B`, 2026-09-09 und 2026-09-13)
    Ein Anfuehrungszeichen im Notiztext zerlegte den Aufruf in Schalter; eine
    lange Notiz scheiterte an der 8191-Zeichen-Grenze von cmd.exe — und
    `--addieren` verlangt den ganzen, wachsenden Text. `--notiz-datei` loest
    beides: Der Text muss durch keine Shell.
"""
import json
import os
import subprocess
import sys

import pytest

import test_bl266_vor_n_bucht_nur_sein_zeitfenster as h
from conftest import BASH, verlange_bash, verlange_pwsh

STUNDE = h.STUNDE


def _wrapper(repo, bahn, *argumente):
    if bahn == "bash":
        verlange_bash()
        befehl = [BASH, "./team-status.sh", *argumente]
    else:
        verlange_pwsh()
        befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                  "./team-status.ps1", *argumente]
    return subprocess.run(befehl, cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _halbe_lage(tmp_path, bahn):
    """Die Feldlage: Die Rollen-Haelfte hat Altlogs (BL-221 haelt sie an),
    die Bau-Haelfte ist einwandfrei buchbar."""
    # ZUERST die Bahn fragen: Das Fixture kopiert die Entrypoints der Bahn,
    # und in einer einbahnigen Installation fehlt der der anderen — der Fall
    # starb dann an FileNotFoundError, statt sich zu ueberspringen (kit-test.sh
    # Schritt 8, BL-129).
    (verlange_bash if bahn == "bash" else verlange_pwsh)()
    repo = h._fixture_bahn(tmp_path, bahn)
    # _fixture_bahn legt 3 Alt- und 11 Neu-Logs in .team-logs und 5 Baulogs
    # NACH dem Beginn in .ralph-logs an.
    return repo


@pytest.mark.parametrize("bahn", ("bash", "pwsh"))
def test_eine_angehaltene_haelfte_haelt_beide_an(tmp_path, bahn):
    repo = _halbe_lage(tmp_path, bahn)
    r = _wrapper(repo, bahn, "--rollen-abschluss", "15", "produkt",
                 "Rollen", "Bau")
    ausgabe = r.stdout + r.stderr
    assert r.returncode != 0, ausgabe
    assert not h._zeilen(repo), (
        f"{bahn}: Eine Haelfte wurde gebucht, obwohl die andere angehalten "
        f"wurde — der halbe Zustand aus BL-239.\n{ausgabe}")
    assert sorted(p.name for p in (repo / ".ralph-logs").glob("*.json")), (
        f"{bahn}: Die Baulogs wurden archiviert, obwohl nichts gebucht ist.")
    assert "Kit-BL-239" in ausgabe and "Rollen-Haelfte" in ausgabe, ausgabe


@pytest.mark.parametrize("bahn", ("bash", "pwsh"))
def test_mit_ansage_werden_beide_haelften_gebucht(tmp_path, bahn):
    """Gegenrichtung: Die Vorpruefung sperrt nicht, was gebucht werden darf."""
    repo = _halbe_lage(tmp_path, bahn)
    r = _wrapper(repo, bahn, "--rollen-abschluss", "15", "produkt",
                 "Rollen", "Bau", "--auch-aeltere")
    assert r.returncode == 0, r.stdout + r.stderr
    rollen = sorted(z["rolle"] for z in h._zeilen(repo))
    assert rollen == ["ralph", "roles"], rollen


# --- BL-244 -------------------------------------------------------------------

def test_ersetzen_ohne_logs_ersetzt_nie_durch_null(tmp_path):
    repo = h._repo(tmp_path)
    beginn = h._beginn(repo)
    h._log(repo, "neu.json", 6.7523, beginn + STUNDE)
    assert h._buche(repo, "15").returncode == 0
    assert (repo / ".team-logs").glob("*.json") is not None
    r = h._buche(repo, "15", "--ersetzen")
    assert r.returncode == 0, r.stderr
    zeilen = h._zeilen(repo)
    assert len(zeilen) == 1 and zeilen[0]["usd"] == pytest.approx(6.7523), (
        f"Die Zeile wurde durch {zeilen[0]['usd']} ersetzt (BL-244).")
    assert "BL-244" in r.stderr and "UNVERAENDERT" in r.stderr, r.stderr


def test_der_erstaufruf_ohne_logs_bucht_weiter_null(tmp_path):
    """Beim ERSTaufruf kann 0.0000 richtig sein (eine Runde ohne Bau)."""
    repo = h._repo(tmp_path)
    r = h._buche(repo, "15")
    assert r.returncode == 0, r.stderr
    assert [z["usd"] for z in h._zeilen(repo)] == [0.0]


# --- BL-245 / BL-249 ----------------------------------------------------------

NOTIZ = ('Stufe endete im vierten Ausgang: "warte auf den Monitor" — '
         'danach von Hand quittiert. ' + "Nachlauf. " * 900)


def test_die_notiz_kommt_aus_einer_datei(tmp_path):
    repo = h._repo(tmp_path)
    beginn = h._beginn(repo)
    h._log(repo, "neu.json", 1.25, beginn + STUNDE)
    datei = tmp_path / "notiz.txt"
    datei.write_text(NOTIZ + "\nzweite Zeile | mit Pipe", encoding="utf-8")
    assert len(NOTIZ) > 8191
    r = h._buche(repo, "15", "--notiz-datei", str(datei))
    assert r.returncode == 0, r.stderr
    notiz = h._zeilen(repo)[0]["notiz"]
    assert '"warte auf den Monitor"' in notiz
    assert "zweite Zeile / mit Pipe" in notiz, (
        "Zeilenumbruch und Pipe muessen das Ein-Zeilen-Schema ueberleben.")


def test_eine_fehlende_notiz_datei_bucht_nichts(tmp_path):
    repo = h._repo(tmp_path)
    beginn = h._beginn(repo)
    h._log(repo, "neu.json", 1.25, beginn + STUNDE)
    r = h._buche(repo, "15", "--notiz-datei", str(tmp_path / "fehlt.txt"))
    assert r.returncode == 1 and "nicht lesbar" in r.stderr, r.stderr
    assert not h._zeilen(repo)


@pytest.mark.parametrize("bahn", ("bash", "pwsh"))
def test_der_wrapper_reicht_beide_notiz_dateien_durch(tmp_path, bahn):
    repo = _halbe_lage(tmp_path, bahn)
    rollen = tmp_path / "rollen.txt"
    rollen.write_text('Frank "HM-3" und Marv', encoding="utf-8")
    bau = tmp_path / "bau.txt"
    bau.write_text("Bau: K15 in vier Stufen", encoding="utf-8")
    r = _wrapper(repo, bahn, "--rollen-abschluss", "15", "produkt",
                 "--notiz-datei", str(rollen), "--bau-notiz-datei", str(bau),
                 "--auch-aeltere")
    assert r.returncode == 0, r.stdout + r.stderr
    notizen = {z["rolle"]: z["notiz"] for z in h._zeilen(repo)}
    assert 'Frank "HM-3" und Marv' in notizen["roles"], notizen
    assert "K15 in vier Stufen" in notizen["ralph"], notizen


@pytest.mark.parametrize("bahn", ("bash", "pwsh"))
def test_ein_unbekanntes_wort_nennt_den_weg(tmp_path, bahn):
    """BL-245: Das Wort hinter dem Anfuehrungszeichen landete in der
    Schalterpruefung — und die Meldung erklaerte nicht, woher."""
    repo = _halbe_lage(tmp_path, bahn)
    r = _wrapper(repo, bahn, "--rollen-abschluss", "15", "produkt",
                 "Rollen", "Bau", "warte")
    assert r.returncode != 0
    assert "--notiz-datei" in r.stderr and "Kit-BL-245" in r.stderr, r.stderr
    assert not h._zeilen(repo)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

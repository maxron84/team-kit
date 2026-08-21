#!/usr/bin/env python3
"""BL-46: Eine Quittung ueber null ist von "hat nichts gekostet" nicht zu
unterscheiden.

Feld K29/135 (2026-08-10): Der `claude -p`-Aufruf im Abomodus lief 47 Minuten
und schrieb 0 Byte. Der Mechanismus funktionierte (Fehler erkannt, API-Fallback
griff, Stufe gebaut und committet) — die BUCHHALTUNG nicht: Ein leeres Log
summiert zu 0.0000, und damit fiel der Abo-Gegenwert von 47 Minuten aus jedem
Kostenabschluss heraus. Die Stufe erschien als die BILLIGSTE der Kaskade,
obwohl sie als teuerste angesetzt war.

Der Kern des Fundes sind die DREI Pfade, die sich unterschiedlich verhielten —
dieser Test faehrt alle drei:
  (1) `kosten.py summe`  war voellig still (Live-Kontostand, --budget, Deckel),
  (2) `--rollen-abschluss` warnte vorbildlich, liess die Datei aber ohne
      dokumentierten Weg heraus liegen,
  (3) `ledger-pruefen` schlug danach DAUERHAFT falschen Alarm und empfahl
      `--ersetzen`, das nach BL-5 den Altwert vernichtet.

Nicht geschaetzt wird nirgends. Sichtbar gemacht ueberall.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, basis_umgebung, kit_pfad

WURZEL = Path(__file__).resolve().parents[2]
TEAM_LIB = kit_pfad("lib.sh")
KOSTEN = kit_pfad("tools", "kosten.py")


def _kosten(*args, cwd=None):
    return subprocess.run([sys.executable, str(KOSTEN), *args],
                          cwd=str(cwd or WURZEL), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def _zettel(ordner, name="stufe-135-20260810-164800.json", dauer=2820):
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / name
    pfad.write_text(json.dumps({"is_error": True, "result": "",
                                "total_cost_usd": None,
                                "team_versuch": "verworfen",
                                "team_dauer_s": dauer}), encoding="utf-8")
    return pfad


def _echtes_log(ordner, name, usd):
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / name
    pfad.write_text(json.dumps({"is_error": False, "subtype": "success",
                                "total_cost_usd": usd}), encoding="utf-8")
    return pfad


# --- lib.sh: der Ersatzzettel entsteht ueberhaupt ---------------------------

def test_leeres_log_wird_zum_ersatzzettel(tmp_path):
    """Die 0-Byte-Datei aus dem Feld. Der Zettel haelt die DAUER fest — das
    ist das Einzige, was belegbar ist — und behauptet keine Kosten."""
    leer = tmp_path / "stufe-135.json"
    leer.write_text("", encoding="utf-8")
    ergebnis = subprocess.run(
        [BASH, "-c", f'source "{TEAM_LIB}"; '
                       f'team_versuch_melden ralph "{leer}" $(( $(date +%s) - 2820 ))'],
        cwd=WURZEL, env=basis_umgebung(),
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    daten = json.loads(leer.read_text(encoding="utf-8"))
    assert daten["team_versuch"] == "verworfen"
    assert daten["total_cost_usd"] is None, (
        "der Zettel darf KEINE Zahl behaupten — nicht schaetzen, nur "
        "sichtbar machen")
    assert daten["team_dauer_s"] >= 2820
    assert daten["is_error"] is True, (
        "der Aufruf muss weiter als Fehler gelten, sonst faellt der "
        "API-Fallback aus (das war vorher die Wirkung der unlesbaren Datei)")
    assert "VERWORFENER VERSUCH" in ergebnis.stderr


def test_brauchbares_log_bleibt_unangetastet(tmp_path):
    """Gegenprobe: Ein gueltiges Log darf niemals ueberschrieben werden."""
    gut = tmp_path / "stufe-136.json"
    original = json.dumps({"is_error": False, "subtype": "success",
                           "total_cost_usd": 1.1835})
    gut.write_text(original, encoding="utf-8")
    ergebnis = subprocess.run(
        [BASH, "-c", f'source "{TEAM_LIB}"; team_versuch_melden ralph "{gut}" 0'],
        cwd=WURZEL, env=basis_umgebung(),
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert gut.read_text(encoding="utf-8") == original
    assert "VERWORFENER VERSUCH" not in ergebnis.stderr


# --- Pfad 1: der stille -----------------------------------------------------

def test_summe_zaehlt_den_zettel_nicht_als_null(tmp_path):
    logs = tmp_path / ".ralph-logs"
    _zettel(logs)
    _echtes_log(logs, "stufe-135-api-fallback.json", 1.1835)
    ergebnis = _kosten("summe", str(logs))
    assert ergebnis.stdout.strip() == "1.1835", (
        "die Summe selbst bleibt unveraendert — Aufrufer parsen sie")
    assert "verworfener Versuch" in ergebnis.stderr, (
        "der stille Pfad war der Fund: Live-Kontostand, --budget und die "
        "Deckel lesen hier und sahen nur 0.0000")
    assert "47 min" in ergebnis.stderr, (
        "die belegte Dauer gehoert in den Hinweis — sie ist das Einzige, was "
        "von den 47 Minuten uebrig ist")
    assert "UNBEKANNT" in ergebnis.stderr


def test_summe_ohne_zettel_schweigt(tmp_path):
    """Gegenprobe: Kein Zettel, kein Hinweis — sonst erzieht die Meldung zum
    Wegsehen (die Falle aus BL-14)."""
    logs = tmp_path / ".ralph-logs"
    _echtes_log(logs, "stufe-136.json", 2.0)
    ergebnis = _kosten("summe", str(logs))
    assert ergebnis.stdout.strip() == "2.0000"
    assert "verworfen" not in ergebnis.stderr


# --- Pfad 2: der Abschluss --------------------------------------------------

def _ledger_fixture(tmp_path):
    (tmp_path / "plans").mkdir(exist_ok=True)
    ledger = tmp_path / ".budget-ledger"
    ledger.write_text("", encoding="utf-8")
    return ledger


def test_abschluss_archiviert_den_zettel_mit(tmp_path):
    """Der Zettel ist gerade KEIN Kostenbeleg — er kann nicht doppelt zaehlen.
    Liegen zu bleiben half ihm nicht: Genau das erzeugte im Feld den
    Dauer-Fehlalarm von ledger-pruefen, ohne dokumentierten Weg heraus."""
    logs = tmp_path / ".ralph-logs"
    zettel = _zettel(logs)
    _echtes_log(logs, "stufe-135-api-fallback.json", 1.1835)
    ledger = _ledger_fixture(tmp_path)
    ergebnis = _kosten("ralph-abschluss", "--kaskade", "29", "--domaene",
                       "produkt", "--archivieren", "--pfad", str(ledger),
                       cwd=tmp_path)
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert not zettel.exists(), "der Zettel muss mit archiviert werden"
    assert (logs / "archiv" / zettel.name).is_file()
    assert "verworfene" in ergebnis.stdout
    assert "UNVOLLSTAENDIG" in ergebnis.stderr, (
        "der Abschluss muss sagen, dass sein Betrag nachweislich unvollstaendig "
        "ist — sonst liest ihn der naechste Closeout als Vergleichsband")


def test_kaputte_datei_bleibt_liegen_und_bekommt_einen_weg_heraus(tmp_path):
    """Abgrenzung: In einer unlesbaren Datei KANN echtes Geld stehen. Sie
    bleibt liegen — aber die Meldung laesst den Menschen nicht mehr damit
    allein."""
    logs = tmp_path / ".team-logs"
    logs.mkdir(parents=True)
    kaputt = logs / "harry-20260810.json"
    kaputt.write_text("{ abgeschnitten", encoding="utf-8")
    _echtes_log(logs, "marv-20260810.json", 3.1418)
    ledger = _ledger_fixture(tmp_path)
    ergebnis = _kosten("rollen-abschluss", "--kaskade", "29", "--domaene",
                       "produkt", "--archivieren", "--pfad", str(ledger),
                       cwd=tmp_path)
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert kaputt.exists(), "eine unlesbare Datei bleibt liegen"
    assert "akteur-abschluss" in ergebnis.stderr, (
        "die Warnung muss den Weg heraus nennen — im Feld gab es keinen")


# --- Pfad 3: der Waechter ---------------------------------------------------

def test_ledger_pruefen_alarmiert_nicht_wegen_eines_zettels(tmp_path):
    """Der eigentliche Schaden: P2 meldete Kaskade 29 dauerhaft als verdaechtig
    und empfahl `--ersetzen` — eine Handlung, die nach BL-5 den Altwert
    vernichtet. Der Waechter empfahl also, Geld zu verlieren."""
    logs = tmp_path / ".ralph-logs"
    _zettel(logs)
    ledger = tmp_path / ".budget-ledger"
    ledger.write_text(
        "2026-08-10 | 29 | 12.0000 | abo | produkt | ralph | Bau: K29\n",
        encoding="utf-8")
    ergebnis = _kosten("ledger-pruefen", "--pfad", str(ledger), "--kaskade",
                       "29", "--ralph-logs", str(logs), "--team-logs",
                       str(tmp_path / ".team-logs"), cwd=tmp_path)
    assert ergebnis.returncode == 0, (
        f"ein Ersatzzettel darf keine WARNUNG ausloesen:\n{ergebnis.stdout}")
    assert "KEIN Kostenbeleg" in ergebnis.stdout
    assert "--ersetzen" not in ergebnis.stdout, (
        "die schaedliche Abhilfe darf fuer diesen Fall nicht mehr vorgeschlagen "
        "werden")


def test_ledger_pruefen_warnt_weiter_bei_echtem_log(tmp_path):
    """Gegenprobe, und die wichtigere: Der BL-5-Fall bleibt scharf. Ein
    unarchiviertes ECHTES Log nach gebuchter Kaskade ist weiterhin eine
    Warnung — sonst haette dieser Fix den Waechter entschaerft."""
    logs = tmp_path / ".ralph-logs"
    _echtes_log(logs, "stufe-140.json", 2.5)
    ledger = tmp_path / ".budget-ledger"
    ledger.write_text(
        "2026-08-10 | 29 | 12.0000 | abo | produkt | ralph | Bau: K29\n",
        encoding="utf-8")
    ergebnis = _kosten("ledger-pruefen", "--pfad", str(ledger), "--kaskade",
                       "29", "--ralph-logs", str(logs), "--team-logs",
                       str(tmp_path / ".team-logs"), cwd=tmp_path)
    assert ergebnis.returncode == 4, (
        f"echte unarchivierte Logs muessen weiter warnen:\n{ergebnis.stdout}")
    assert "unarchivierte Log(s)" in ergebnis.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

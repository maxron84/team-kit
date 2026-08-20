#!/usr/bin/env python3
"""Fixture-Test für BL-32 — 429-Session-Limit mit voller-Stunden-Reset ("resets 3pm").

Realer Auslöser (2026-07-12, .ralph-logs/archiv/stufe-49-20260712-134536.json):
Die Claude-CLI meldete das Session-Limit als
    "You've hit your session limit · resets 3pm (Europe/Berlin)"
— also mit voller Stunde OHNE ":MM". Die 429-Parser in team/lib.sh verlangten
zuvor zwingend Minuten (\\d{1,2}:\\d{2}), wodurch:
  * team_429_reset_epoch die Reset-Zeit NICHT parsen konnte → "Reset unbekannt"
    → die Auto-Warte-/Retry-Logik (Strategie A) wurde übersprungen;
  * team_result_is_429 im Text-Zweig scheiterte (nur das api_error_status-Feld
    rettete die Erkennung; ohne dieses Feld wäre ein 429 fälschlich als harter
    Fehler / Exit 1 behandelt worden statt als saubere Pause / Exit 42).

Dieser Test belegt den Fix (Minuten optional, Default 0) rein netz-/CLI-frei
über `bash -c` + `source team/lib.sh` (Muster wie test_bl27_abo_key_startwarnung.py).
Kein echter Claude-Aufruf.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from conftest import Ausgabe, Ruf, Schale, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = kit_pfad("lib.sh")


def _write_log(payload):
    fh = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, dir=REPO_ROOT
    )
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _is_429(schale, logpath):
    """Urteil ohne Nutzlast — nur der Exit-Code zaehlt."""
    return schale.lauf(Ruf("team_result_is_429", logpath),
                       cwd=REPO_ROOT).returncode == 0


def _reset_epoch(schale, logpath):
    """Nutzlast auf stdout (die Epoch) plus Exit-Code."""
    r = schale.lauf(Ausgabe("team_429_reset_epoch", logpath), cwd=REPO_ROOT)
    return r.returncode, r.stdout.strip()


def test_volle_stunde_wird_als_429_erkannt(schale):
    p = _write_log(
        {"result": "You've hit your session limit · resets 3pm (Europe/Berlin)"}
    )
    try:
        assert _is_429(schale, p), (
            "'resets 3pm' (volle Stunde ohne :MM) muss als 429 erkannt werden (BL-32)"
        )
    finally:
        p.unlink()


def test_volle_stunde_reset_epoch_parst_und_ist_15_uhr(schale):
    p = _write_log(
        {"result": "You've hit your session limit · resets 3pm (Europe/Berlin)"}
    )
    try:
        rc, out = _reset_epoch(schale, p)
        assert rc == 0 and out.isdigit(), (
            "team_429_reset_epoch muss 'resets 3pm' parsen (Epoch ausgeben), "
            "nicht mit 'Reset unbekannt' scheitern (BL-32)"
        )
        # Verifizieren: geparste Zeit ist 15:00 lokaler Zeit (Minute 0).
        check = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys,datetime; "
                "t=datetime.datetime.fromtimestamp(int(sys.argv[1])); "
                "sys.exit(0 if (t.hour==15 and t.minute==0) else 1)",
                out,
            ],
            capture_output=True,
        )
        assert check.returncode == 0, (
            f"'resets 3pm' muss auf 15:00:00 (Minute 0) parsen, Epoch={out}"
        )
    finally:
        p.unlink()


def test_mit_minuten_weiter_korrekt(schale):
    p = _write_log(
        {"result": "You've hit your session limit · resets 3:30pm (Europe/Berlin)"}
    )
    try:
        assert _is_429(schale, p), "'resets 3:30pm' (mit Minuten) muss weiter als 429 gelten"
        rc, out = _reset_epoch(schale, p)
        assert rc == 0 and out.isdigit(), "'resets 3:30pm' muss weiter parsen"
        check = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys,datetime; "
                "t=datetime.datetime.fromtimestamp(int(sys.argv[1])); "
                "sys.exit(0 if (t.hour==15 and t.minute==30) else 1)",
                out,
            ],
            capture_output=True,
        )
        assert check.returncode == 0, f"'resets 3:30pm' muss 15:30 ergeben, Epoch={out}"
    finally:
        p.unlink()


def test_api_error_status_feld_erkannt(schale):
    p = _write_log(
        {"api_error_status": 429, "result": "irgendein anderer text ohne muster"}
    )
    try:
        assert _is_429(schale, p), (
            "das starke Feld api_error_status==429 muss unabhängig vom Text greifen"
        )
    finally:
        p.unlink()


def test_fliesstext_zitat_bleibt_negativ(schale):
    # HM-21-Schutz: ein bloßes Zitat der CLI-Meldung MITTEN in längerem Text
    # (z. B. Doku-/Beutebuch-Zitat) darf NICHT als echtes 429 durchgehen.
    p = _write_log(
        {
            "result": "Der Test prüft, dass die Meldung You've hit your session "
            "limit · resets 3pm hier nur zitiert wird und kein echtes Limit ist."
        }
    )
    try:
        assert not _is_429(schale, p), (
            "ein eingebettetes Zitat (Fließtext drumherum) darf NICHT als 429 "
            "gelten — re.fullmatch-Schutz aus HM-21 muss erhalten bleiben"
        )
    finally:
        p.unlink()


if __name__ == "__main__":
    failures = []
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(Schale("bash"))
                print(f"OK   {name}")
            except AssertionError as e:
                failures.append(name)
                print(f"FAIL {name}: {e}")
    if failures:
        sys.exit(1)
    print("gruen — BL-32 verifiziert: 'resets 3pm' (volle Stunde) wird erkannt "
          "und geparst, Minuten weiter korrekt, HM-21-Schutz erhalten.")

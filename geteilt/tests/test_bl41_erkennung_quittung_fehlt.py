#!/usr/bin/env python3
"""BL-41, zweite Haelfte: Erkennung des vierten Ausgangs.

Die erste Haelfte (Vordergrund-Auflage in SMOKE_ZEILE, siehe
test_bl41_smoke_zeile_vordergrund.py) ist PRAEVENTION. Sie hat im Feld nicht
gehalten: In K33/154 war die Auflage wortgleich mit der Kit-Fassung installiert
und der Regressionstest gruen — die Rolle hat sie trotzdem uebergangen, nach 65
Turns und 8,86 Mio Cache-Read-Tokens. Ein Satz aus dem ersten Turn konkurriert
dort mit dem gesamten seither gewachsenen Kontext; Praevention per Prompt
skaliert also GEGENLAEUFIG zur Stufenlaenge. Vier Vorfaelle, 19,47 USD.

Diese Datei haelt die zweite Haelfte fest: Wenn es doch passiert, muss der Loop
den Fall BENENNEN statt "KEIN Promise — Log pruefen" zu sagen. Die generische
Meldung schickte den Menschen in ein Log, das Erfolg meldet, und von dort in den
PLAN statt in den Fehlermodus.

WARUM NICHT AUF VOKABELN GEPRUEFT WIRD: Die drei Vorfaelle formulierten es
dreimal anders ("background pytest run and monitor", "fallback check / wakeup",
"set up a monitor to catch its completion"). Geprueft wird die STRUKTUR — kein
Promise, aber das Log erklaert sich selbst fuer erfolgreich. Der Testfall
`test_dritte_feldvariante_wird_erkannt` faehrt genau den K33-Wortlaut, um zu
belegen, dass die Erkennung nicht an der Formulierung haengt.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_aufruf, kit_pfad,
                      kopiere_team_namensraum, pfad_voran)

WURZEL = Path(__file__).resolve().parents[2]
TEAM_LIB = kit_pfad("lib.sh")

# Der Wortlaut aus dem Feld, K33/154 (2026-08-11) — dritte Formulierungsvariante.
K33_RESULT = ("The smoke test (compileall + full pytest suite, headless) is "
              "running in the background; I've set up a monitor to catch its "
              "completion. I'll report results once it finishes.")


def _lib(script, env_extra=None):
    env = {"HOME": str(Path.home()), "PATH": "/usr/bin:/bin"}
    env.update(env_extra or {})
    return subprocess.run([BASH, "-c", f'source "{TEAM_LIB}"\n{script}'],
                          cwd=WURZEL, env=env, capture_output=True, text=True)


def _log(tmp_path, name, daten):
    pfad = tmp_path / name
    pfad.write_text(json.dumps(daten), encoding="utf-8")
    return pfad


# --- Die Erkennung selbst ---------------------------------------------------

def test_erfolgs_log_ohne_promise_wird_als_erfolg_gemeldet(tmp_path):
    """Genau die Feldlage: subtype=success, is_error=false, kein Promise."""
    pfad = _log(tmp_path, "k33.json", {
        "subtype": "success", "is_error": False, "num_turns": 65,
        "total_cost_usd": 6.2228, "result": K33_RESULT})
    assert _lib(f'team_result_meldet_erfolg "{pfad}"').returncode == 0


def test_echter_fehler_ist_kein_erfolg(tmp_path):
    """Gegenrichtung: is_error schlaegt den subtype."""
    pfad = _log(tmp_path, "fehler.json", {"subtype": "success",
                                          "is_error": True, "result": ""})
    assert _lib(f'team_result_meldet_erfolg "{pfad}"').returncode != 0


def test_abbruch_subtype_ist_kein_erfolg(tmp_path):
    """Ein Log, das sich NICHT selbst fuer erfolgreich erklaert, faellt in den
    gewoehnlichen Fehlerpfad — sonst waere jeder Fehlschlag ploetzlich ein
    'fertig, nur unquittiert' und die Meldung damit wertlos."""
    pfad = _log(tmp_path, "abbruch.json", {"subtype": "error_during_execution",
                                           "is_error": False, "result": ""})
    assert _lib(f'team_result_meldet_erfolg "{pfad}"').returncode != 0


def test_unlesbares_log_ist_kein_erfolg(tmp_path):
    """0 Byte (BL-46) darf hier nichts behaupten."""
    pfad = tmp_path / "leer.json"
    pfad.write_text("", encoding="utf-8")
    assert _lib(f'team_result_meldet_erfolg "{pfad}"').returncode != 0


def test_meldung_nennt_den_fall_und_den_weg(tmp_path):
    """Die Meldung ist der eigentliche Fix: Sie muss den Menschen zum
    Fehlermodus fuehren, nicht zum Plan — und ausdruecklich davon abhalten,
    die bezahlte Arbeit durch einen Neulauf wegzuwerfen."""
    pfad = _log(tmp_path, "k33.json", {"subtype": "success", "is_error": False,
                                       "result": K33_RESULT})
    ergebnis = _lib(f'team_quittung_fehlt_melden ralph "{pfad}" "Stufe 154" '
                    f'"git log -1" "von Hand quittieren"')
    assert ergebnis.returncode == 0
    text = ergebnis.stderr
    assert "QUITTUNG FEHLT" in text
    assert "BL-41" in text, "ohne Fundnummer findet niemand die Vorgeschichte"
    assert "von Hand quittieren" in text, "der Weg heraus fehlt"
    assert "wirft die bezahlte Arbeit weg" in text, (
        "die Meldung muss vor dem Neulauf warnen — genau der hat im Feld "
        "6,22 USD vernichtet")


def test_dritte_feldvariante_wird_erkannt(tmp_path):
    """Die Erkennung darf nicht an der Formulierung haengen: 'Monitor' ist die
    tragende Vokabel in K33, waehrend die Praevention woertlich nur
    'Hintergrund-Task' und 'Wakeup' verbietet. Alle drei Feldwortlaute muessen
    zum selben Ergebnis fuehren."""
    for i, wortlaut in enumerate([
            "I'll pause here and wait for the background pytest run and "
            "monitor to report back before continuing.",
            "I've scheduled a fallback check and am now waiting for either "
            "the smoke-test background task notification or the scheduled "
            "wakeup.",
            K33_RESULT]):
        pfad = _log(tmp_path, f"variante{i}.json", {
            "subtype": "success", "is_error": False, "result": wortlaut})
        assert _lib(f'team_result_meldet_erfolg "{pfad}"').returncode == 0, (
            f"Variante {i} nicht erkannt: {wortlaut[:40]}…")


# --- Der Loop-Pfad: ralph.sh muss 43 liefern, nicht 1 -----------------------
# Der Wert der Erkennung entsteht erst dort, wo der Mensch sie liest. Deshalb
# wird hier die WIRKLICHE Bedienoberfläche gefahren (ralph.sh mit gestubbter
# CLI), nicht nur die Bibliotheksfunktion — dieselbe Lehre wie in BL-19.

RALPH = WURZEL / "ralph.sh"


def _fixture_repo(tmp_path, stub_json):
    if not RALPH.is_file():
        pytest.skip("ralph.sh liegt nur in der INSTALLIERTEN Ablage "
                    "(im Kit unter bash/entry/ bzw. pwsh/entry/) — geprueft wird via kit-test.sh")
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(RALPH, repo / "ralph.sh")
    shutil.copy(WURZEL / "team.config.sh", repo / "team.config.sh")
    kopiere_team_namensraum(repo / "team")
    (repo / "plans").mkdir(exist_ok=True)
    (repo / "plans" / "ralph-kaskade-1-test.md").write_text(
        "RALPH_CAP=1\n\n## Stufe 1\nNichts.\n", encoding="utf-8")
    (repo / ".ralph-plan").write_text("plans/ralph-kaskade-1-test.md\n")
    (repo / ".ralph-state").write_text("1\n")
    for befehl in (["init", "-q"], ["config", "user.email", "t@localhost"],
                   ["config", "user.name", "Test"], ["add", "-A"],
                   ["commit", "-qm", "fixture"]):
        subprocess.run(["git", "-C", str(repo)] + befehl, check=True)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "claude"
    stub.write_text("#!/usr/bin/env bash\ncat <<'JSON'\n"
                    + json.dumps(stub_json) + "\nJSON\n", encoding="utf-8")
    stub.chmod(0o755)
    return repo, bin_dir


def _ralph(tmp_path, stub_json):
    repo, bin_dir = _fixture_repo(tmp_path, stub_json)
    env = dict(os.environ)
    env.update({"PATH": pfad_voran(bin_dir, env), "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    return subprocess.run(entrypoint_aufruf("./ralph.sh"), cwd=repo, env=env,
                          capture_output=True, text=True)


def test_ralph_meldet_43_statt_generischem_fehler(tmp_path):
    ergebnis = _ralph(tmp_path, {"subtype": "success", "is_error": False,
                                 "total_cost_usd": 0.5, "result": K33_RESULT})
    assert ergebnis.returncode == 43, (
        f"erwartet Exit 43 (Stufe fertig, Quittung fehlt), war "
        f"{ergebnis.returncode}\nstdout:\n{ergebnis.stdout}\n"
        f"stderr:\n{ergebnis.stderr}")
    assert "QUITTUNG FEHLT" in ergebnis.stderr
    assert ".ralph-state" in ergebnis.stderr, (
        "die Meldung muss den konkreten Weiterschalt-Befehl nennen")


def test_gewoehnlicher_fehlschlag_bleibt_exit_1(tmp_path):
    """Gegenprobe: Ein Log, das sich nicht selbst fuer erfolgreich erklaert,
    laeuft unveraendert in den alten Pfad. Ohne diese Haelfte waere aus jedem
    Fehlschlag ein 'fertig, nur unquittiert' geworden."""
    ergebnis = _ralph(tmp_path, {"subtype": "error_during_execution",
                                 "is_error": False, "total_cost_usd": 0.5,
                                 "result": "abgebrochen"})
    assert ergebnis.returncode == 1, (
        f"erwartet Exit 1, war {ergebnis.returncode}\n{ergebnis.stderr}")
    assert "KEIN Promise" in ergebnis.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

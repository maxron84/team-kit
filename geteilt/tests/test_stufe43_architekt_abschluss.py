#!/usr/bin/env python3
"""Fixture-Test fuer die A1-Ersetzung der Architekt-Kosten (BL-28, Kaskade
13/Stufe 43).

Die A2-Live-Schaetzung (Stufe 42) wird NIE in .budget-ledger persistiert --
sie ist eine reine Laufzeit-Berechnung (Churn seit dem letzten Ledger-Commit).
Das Abschluss-Tool haengt stattdessen den ECHTEN, vom Strippenzieher aus der
Anthropic-Konsole abgelesenen Wert an. Ein zweiter Aufruf fuer dieselbe
Kaskade ERSETZT die vorhandene Architekt-Zeile statt sie zu verdoppeln, damit
Schaetzung und echter Wert nie beide zaehlen.

Netz-/CLI-frei bis auf subprocess-Aufrufe von team/tools/kosten.py gegen ein
temporaeres Fixture-Ledger (kein Bezug zur echten .budget-ledger).
"""
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = kit_pfad("tools", "kosten.py")

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402


def _run(*args):
    result = subprocess.run(
        [sys.executable, str(KOSTEN_PY), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _fixture_ledger(tmp_path, inhalt="# datum | kaskade | usd | auth | domaene | rolle | notiz\n"):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(inhalt)
    return pfad


def test_erster_aufruf_legt_genau_eine_architekt_zeile_an(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, out, err = _run("architekt-abschluss", "--usd", "16.50",
                         "--domaene", "team", "--kaskade", "13",
                         "--pfad", str(ledger))
    assert rc == 0, err
    assert "angelegt" in out

    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    architekt_zeilen = [z for z in zeilen if z["rolle"] == "architekt"]
    assert len(architekt_zeilen) == 1
    assert architekt_zeilen[0]["usd"] == 16.50
    assert architekt_zeilen[0]["domaene"] == "team"
    assert architekt_zeilen[0]["auth"] == "api"

    summe = kosten.ledger_summe(str(ledger), rolle="architekt")
    assert summe == 16.50


def test_zweiter_aufruf_gleiche_kaskade_ersetzt_statt_verdoppelt(tmp_path):
    # --ersetzen seit BL-25: Der Zweitaufruf bricht ohne Schalter ab, damit
    # eine Folgesitzung keine fremde Messung mehr wortlos loescht. Die
    # Zusicherung DIESES Tests ist unveraendert — wird ersetzt, entsteht
    # KEINE zweite Zeile.
    ledger = _fixture_ledger(tmp_path)
    rc1, _out1, err1 = _run("architekt-abschluss", "--usd", "16.00",
                             "--domaene", "team", "--kaskade", "13",
                             "--pfad", str(ledger))
    assert rc1 == 0, err1

    rc2, out2, err2 = _run("architekt-abschluss", "--usd", "18.25",
                            "--domaene", "team", "--kaskade", "13",
                            "--ersetzen", "--pfad", str(ledger))
    assert rc2 == 0, err2
    assert "ersetzt" in out2

    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    architekt_zeilen = [z for z in zeilen if z["rolle"] == "architekt"
                         and z["notiz"] is not None]
    # genau eine Architekt-Zeile fuer Kaskade 13, mit dem NEUEN Wert
    assert len(architekt_zeilen) == 1
    assert architekt_zeilen[0]["usd"] == 18.25

    summe = kosten.ledger_summe(str(ledger), rolle="architekt")
    assert summe == 18.25


def test_verschiedene_kaskaden_bleiben_getrennt(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    _run("architekt-abschluss", "--usd", "10", "--domaene", "team",
         "--kaskade", "12", "--pfad", str(ledger))
    _run("architekt-abschluss", "--usd", "16", "--domaene", "team",
         "--kaskade", "13", "--pfad", str(ledger))

    zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "architekt"]
    assert len(zeilen) == 2
    assert kosten.ledger_summe(str(ledger), rolle="architekt") == 26.0


def test_bestehende_nicht_architekt_zeilen_bleiben_unangetastet(tmp_path):
    ledger = _fixture_ledger(
        tmp_path,
        "2026-07-10 | 1 | 2.4800 | abo | Grundgeruest\n"
        "2026-07-12 | 13 | 3.0000 | abo | team | ralph | Bau-Kosten\n",
    )
    rc, _out, err = _run("architekt-abschluss", "--usd", "16", "--domaene",
                          "team", "--kaskade", "13", "--pfad", str(ledger))
    assert rc == 0, err

    gesamt = kosten.ledger_summe(str(ledger))
    assert gesamt == 2.48 + 3.0 + 16.0
    ralph_zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "ralph"]
    assert len(ralph_zeilen) == 1
    assert ralph_zeilen[0]["usd"] == 3.0


def test_negativer_usd_bricht_sauber_ab_ohne_ledger_aenderung(tmp_path):
    inhalt = "# leer\n"
    ledger = _fixture_ledger(tmp_path, inhalt)
    rc, _out, err = _run("architekt-abschluss", "--usd", "-5", "--domaene",
                          "team", "--kaskade", "13", "--pfad", str(ledger))
    assert rc == 1
    assert "nicht-negativ" in err.lower()
    assert ledger.read_text() == inhalt


def test_text_statt_zahl_bricht_sauber_ab(tmp_path):
    inhalt = "# leer\n"
    ledger = _fixture_ledger(tmp_path, inhalt)
    rc, _out, err = _run("architekt-abschluss", "--usd", "nicht-numerisch",
                          "--domaene", "team", "--kaskade", "13",
                          "--pfad", str(ledger))
    assert rc == 1
    assert "keine zahl" in err.lower()
    assert ledger.read_text() == inhalt


def test_fehlender_usd_bricht_sauber_ab(tmp_path):
    inhalt = "# leer\n"
    ledger = _fixture_ledger(tmp_path, inhalt)
    rc, _out, err = _run("architekt-abschluss", "--domaene", "team",
                          "--kaskade", "13", "--pfad", str(ledger))
    assert rc == 1
    assert "--usd" in err
    assert ledger.read_text() == inhalt


def test_ungueltige_domaene_bricht_sauber_ab(tmp_path):
    inhalt = "# leer\n"
    ledger = _fixture_ledger(tmp_path, inhalt)
    rc, _out, err = _run("architekt-abschluss", "--usd", "16", "--domaene",
                          "sonstwo", "--kaskade", "13", "--pfad", str(ledger))
    assert rc == 1
    assert "domaene" in err.lower()
    assert ledger.read_text() == inhalt


def test_kaskade_ohne_ralph_plan_bricht_sauber_ab(tmp_path):
    inhalt = "# leer\n"
    ledger = _fixture_ledger(tmp_path, inhalt)
    rc, _out, err = _run("architekt-abschluss", "--usd", "16", "--domaene",
                          "team", "--pfad", str(ledger), "--repo", str(tmp_path))
    assert rc == 1
    assert "kaskade" in err.lower()
    assert ledger.read_text() == inhalt


def test_kaskade_aus_ralph_plan_abgeleitet(tmp_path):
    (tmp_path / ".ralph-plan").write_text(
        "plans/ralph-kaskade-13-architekt-kosten.md\n")
    inhalt = "# leer\n"
    ledger_name = "fixture-ledger"
    (tmp_path / ledger_name).write_text(inhalt)

    rc, out, err = _run("architekt-abschluss", "--usd", "16", "--domaene",
                         "team", "--pfad", ledger_name, "--repo", str(tmp_path))
    assert rc == 0, err
    assert "Kaskade 13" in out

    zeilen = list(kosten.ledger_zeilen(str(tmp_path / ledger_name)))
    architekt_zeilen = [z for z in zeilen if z["rolle"] == "architekt"]
    assert len(architekt_zeilen) == 1


def test_notiz_mit_pipe_wird_sauber_escaped(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, _out, err = _run("architekt-abschluss", "--usd", "16", "--domaene",
                          "team", "--kaskade", "13", "--pfad", str(ledger),
                          "--notiz", "Konsole zeigt 16 | tatsaechlich 16,02")
    assert rc == 0, err
    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    architekt_zeilen = [z for z in zeilen if z["rolle"] == "architekt"]
    assert len(architekt_zeilen) == 1
    assert "|" not in architekt_zeilen[0]["notiz"]
    # keine zusaetzlichen Felder durch die eingeschleuste Pipe entstanden
    assert kosten.ledger_summe(str(ledger), rolle="architekt") == 16.0

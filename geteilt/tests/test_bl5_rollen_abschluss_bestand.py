#!/usr/bin/env python3
"""Regressionstest fuer BL-5: `rollen-abschluss` darf einen bestehenden
Kostenwert NIE stillschweigend ueberschreiben.

Realer Ausloeser (Feldprojekt team-kit_project_platformer, Kaskade 1,
2026-08-01): Nach dem Kostenabschluss lief Frank noch drei Fixes. Ein
zweiter `--rollen-abschluss 1 produkt` zaehlte nur die seither
entstandenen Logs (2,4114 USD) und ERSETZTE damit die Zeile ueber 1,0969
USD -- der alte Wert war weg, ohne Warnung, ohne Spur. Der Sollwert waere
die SUMME (3,5083) gewesen; korrigiert wurde von Hand.

Ursache ist die Kombination zweier je fuer sich richtiger Entscheidungen:
Der Wert wird aus den NOCH NICHT ARCHIVIERTEN Logs gezaehlt, und der
Abschluss archiviert die gezaehlten Logs anschliessend. Aufeinanderfolgende
Aufrufe sehen deshalb DISJUNKTE Mengen -- fuer die ist Addieren die
richtige Verknuepfung, nicht Ersetzen. Das Ersetzen stammte aus
akteur_abschluss(), wo der Aufrufer einen absoluten, extern gemessenen
Wert uebergibt.

Netz-/CLI-frei gegen temporaere Fixture-Ledger/-Log-Verzeichnisse -- Muster
wie test_stufe54_rollen_abschluss.py (nie das echte .team-logs).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

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
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _fixture_ledger(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text("# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    return pfad


def _log_schreiben(verzeichnis, name, usd):
    verzeichnis.mkdir(exist_ok=True)
    (verzeichnis / name).write_text(json.dumps({"total_cost_usd": usd}))
    return verzeichnis


def _roles_zeilen(ledger):
    return [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "roles"]


def test_zweiter_aufruf_bricht_ab_und_laesst_ledger_unangetastet(tmp_path):
    """Der Kern von BL-5: ohne ausdruecklichen Modus wird NICHTS geschrieben."""
    ledger = _fixture_ledger(tmp_path)
    logs1 = _log_schreiben(tmp_path / "logs1", "harry.json", 1.0)
    logs2 = _log_schreiben(tmp_path / "logs2", "frank.json", 5.0)
    _run("rollen-abschluss", "--kaskade", "16", "--domaene", "team",
         "--logs", str(logs1), "--pfad", str(ledger))
    vorher = ledger.read_text()

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs2),
                         "--pfad", str(ledger))

    assert rc != 0
    assert ledger.read_text() == vorher, "Ledger wurde trotz Abbruch veraendert"
    # Die Meldung muss handlungsfaehig machen: Alt-, Neu- UND Summenwert.
    assert "1.0000" in err and "5.0000" in err and "6.0000" in err
    assert "--addieren" in err and "--ersetzen" in err


def test_addieren_summiert_statt_zu_verlieren(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs1 = _log_schreiben(tmp_path / "logs1", "harry.json", 1.0)
    logs2 = _log_schreiben(tmp_path / "logs2", "frank.json", 5.0)
    _run("rollen-abschluss", "--kaskade", "16", "--domaene", "team",
         "--logs", str(logs1), "--pfad", str(ledger))

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs2),
                         "--pfad", str(ledger), "--addieren")

    assert rc == 0, err
    assert "addiert" in out
    assert "+5.0000" in out, "Der Zugang muss als Zugang erkennbar sein, nicht als Zeilenwert"
    zeilen = _roles_zeilen(ledger)
    assert len(zeilen) == 1, "Addieren darf keine zweite Zeile erzeugen"
    assert zeilen[0]["usd"] == pytest.approx(6.0)
    assert "Bestand 1.0000 USD" in zeilen[0]["notiz"]


def test_ersetzen_bleibt_moeglich(tmp_path):
    """Der Korrekturfall (Altzeile war falsch) muss erreichbar bleiben."""
    ledger = _fixture_ledger(tmp_path)
    logs1 = _log_schreiben(tmp_path / "logs1", "harry.json", 1.0)
    logs2 = _log_schreiben(tmp_path / "logs2", "frank.json", 5.0)
    _run("rollen-abschluss", "--kaskade", "16", "--domaene", "team",
         "--logs", str(logs1), "--pfad", str(ledger))

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs2),
                         "--pfad", str(ledger), "--ersetzen")

    assert rc == 0, err
    zeilen = _roles_zeilen(ledger)
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == pytest.approx(5.0)


def test_feldszenario_kaskade_1_nachlauf_von_frank(tmp_path):
    """Das reale BL-5-Szenario mit den echten Zahlen, inklusive Archivierung:
    Abschluss (Harry+Marv, 1,0969) -> Frank laeuft nach (2,4114) -> zweiter
    Abschluss. Vorher verschwanden 1,0969 USD; jetzt bleibt der Wert stehen,
    und --addieren ergibt exakt den von Hand ermittelten Sollwert 3,5083."""
    ledger = _fixture_ledger(tmp_path)
    logs = _log_schreiben(tmp_path / "team-logs", "harry.json", 1.0969)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "1",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren")
    assert rc == 0, err
    assert not list(logs.glob("*.json")), "Der erste Abschluss muss archiviert haben"

    # Frank laeuft NACH dem Kostenabschluss — neues Log im geleerten Ordner.
    _log_schreiben(logs, "frank.json", 2.4114)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "1",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren")
    assert rc != 0, "Der Nachlauf haette die Altbuchung stillschweigend geloescht"
    assert _roles_zeilen(ledger)[0]["usd"] == pytest.approx(1.0969)
    assert list(logs.glob("*.json")), \
        "Bei Abbruch darf NICHT archiviert werden — sonst waere das Log weg"

    rc, out, err = _run("rollen-abschluss", "--kaskade", "1",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren", "--addieren")
    assert rc == 0, err
    zeilen = _roles_zeilen(ledger)
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == pytest.approx(3.5083)
    assert not list(logs.glob("*.json"))


def test_unlesbarer_altwert_bricht_ab_ohne_zu_schreiben(tmp_path):
    """Von Hand korrigierte Zeilen gibt es real (Feld-Kaskade 1). Ist der
    Altwert nicht lesbar, wird nicht geraten, sondern abgebrochen."""
    ledger = _fixture_ledger(tmp_path)
    ledger.write_text(ledger.read_text() +
                      "2026-08-01 | 16 | ca. 1,10 | abo | team | roles | von Hand\n")
    vorher = ledger.read_text()
    logs = _log_schreiben(tmp_path / "logs", "harry.json", 5.0)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger), "--addieren")

    assert rc != 0
    assert ledger.read_text() == vorher
    assert "von Hand" in err or "lesbares USD-Feld" in err


def test_unbekannter_modus_wird_abgelehnt(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    with pytest.raises(ValueError, match="bestand"):
        kosten.rollen_abschluss("16", 1.0, 0.0, domaene="team",
                                 pfad=str(ledger), bestand="ueberschreiben")


def test_erster_aufruf_bleibt_unveraendert_einfach(tmp_path):
    """Ohne Altzeile darf der Default nichts erschweren — der Normalfall
    (ein Closeout je Kaskade) muss ohne jedes Flag durchlaufen."""
    ledger = _fixture_ledger(tmp_path)
    logs = _log_schreiben(tmp_path / "logs", "harry.json", 2.0)

    rc, out, err = _run("rollen-abschluss", "--kaskade", "16",
                         "--domaene", "team", "--logs", str(logs),
                         "--pfad", str(ledger))

    assert rc == 0, err
    assert "angelegt" in out
    assert _roles_zeilen(ledger)[0]["usd"] == pytest.approx(2.0)

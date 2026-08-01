#!/usr/bin/env python3
"""Regressionstest fuer BL-4: Ralphs BAUKOSTEN muessen im committeten Ledger
landen.

Realer Ausloeser (Feldprojekt team-kit_project_platformer, Kaskade 1,
2026-08-01): Nach vollstaendigem Closeout standen 2,1621 USD Baukosten in
KEINER Ledger-Zeile. `--rollen-abschluss` ledgert per Definition nur
.team-logs (Harry/Marv/Frank/Axel); fuer .ralph-logs existierte zwar der
Bash-Helfer team_logs_archivieren(), aber im gesamten Kit kein Aufrufer.
Der Gesamtstand stimmte nur, solange .ralph-logs/ liegen blieb — und der
Ordner steht in .gitignore. Ein frischer Clone verlor damit die gesamte
Bau-Kostenhistorie, also genau das, wogegen die Ledger gebaut wurde.

Geprueft wird beides:
  * das kosten.py-Verb `ralph-abschluss` (Zeile, Rolle, Archivierung),
  * die EINE Bedienhandlung `team-status.sh --rollen-abschluss`, die beide
    Verben nacheinander aufruft — denn der Fehler war nicht, dass man Ralph
    nicht haette buchen KOENNEN, sondern dass kein Befehl und keine Regel es
    verlangte.

Netz-/CLI-frei gegen temporaere Fixture-Verzeichnisse -- nie das echte
.ralph-logs (Muster wie test_stufe54_rollen_abschluss.py).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = REPO_ROOT / "team" / "tools" / "kosten.py"
TEAM_STATUS = REPO_ROOT / "team-status.sh"


def _run(*args):
    result = subprocess.run(
        [sys.executable, str(KOSTEN_PY), *args],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


sys.path.insert(0, str(REPO_ROOT / "team" / "tools"))
import kosten  # noqa: E402


def _log_schreiben(verzeichnis, name, usd):
    verzeichnis.mkdir(parents=True, exist_ok=True)
    (verzeichnis / name).write_text(json.dumps({"total_cost_usd": usd}))
    return verzeichnis


def _fixture_ledger(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text("# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    return pfad


def _zeilen(ledger, rolle):
    return [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == rolle]


def test_ralph_abschluss_legt_eigene_ralph_zeile_an(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _log_schreiben(tmp_path / "ralph-logs", "stufe-1.json", 2.1621)

    rc, out, err = _run("ralph-abschluss", "--kaskade", "1",
                         "--domaene", "produkt", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren")

    assert rc == 0, err
    zeilen = _zeilen(ledger, "ralph")
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == pytest.approx(2.1621)
    assert zeilen[0]["domaene"] == "produkt"
    assert not list(logs.glob("*.json")), "gezaehlte Logs muessen archiviert sein"
    assert (logs / "archiv" / "stufe-1.json").is_file()


def test_ralph_zeile_und_roles_zeile_koexistieren(tmp_path):
    """Die Trennung Bau <-> Sweep/Fix ist der Grund fuer zwei Zeilen statt
    einer Sammelzeile — genau an ihr fiel im Feld auf, dass Ralph fehlte."""
    ledger = _fixture_ledger(tmp_path)
    team_logs = _log_schreiben(tmp_path / "team-logs", "harry.json", 1.0969)
    ralph_logs = _log_schreiben(tmp_path / "ralph-logs", "stufe-1.json", 2.1621)

    _run("rollen-abschluss", "--kaskade", "1", "--domaene", "produkt",
         "--logs", str(team_logs), "--pfad", str(ledger), "--archivieren")
    _run("ralph-abschluss", "--kaskade", "1", "--domaene", "produkt",
         "--logs", str(ralph_logs), "--pfad", str(ledger), "--archivieren")

    assert len(_zeilen(ledger, "roles")) == 1
    assert len(_zeilen(ledger, "ralph")) == 1
    assert _zeilen(ledger, "roles")[0]["usd"] == pytest.approx(1.0969)
    assert _zeilen(ledger, "ralph")[0]["usd"] == pytest.approx(2.1621)
    gesamt = kosten.ledger_summe(str(ledger), kaskade="1")
    assert gesamt == pytest.approx(3.2590)


def test_bl5_schutz_gilt_auch_fuer_die_ralph_zeile(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    logs = _log_schreiben(tmp_path / "ralph-logs", "stufe-1.json", 2.0)
    _run("ralph-abschluss", "--kaskade", "1", "--domaene", "produkt",
         "--logs", str(logs), "--pfad", str(ledger))
    vorher = ledger.read_text()

    _log_schreiben(logs, "stufe-2.json", 0.5)
    rc, out, err = _run("ralph-abschluss", "--kaskade", "1",
                         "--domaene", "produkt", "--logs", str(logs),
                         "--pfad", str(ledger))

    assert rc != 0
    assert ledger.read_text() == vorher
    assert "ralph-Zeile" in err


def test_addieren_behaelt_die_rolle_der_zeile(tmp_path):
    """Beim manuellen Durchlauf aufgefallen: merge_fn schrieb die Rolle hart
    als "roles" — ein --addieren verwandelte Ralphs Zeile in eine ZWEITE
    roles-Zeile und machte die Baukosten wieder unsichtbar. Also der
    BL-4-Fehler eine Ebene tiefer, erzeugt vom BL-5-Fix."""
    ledger = _fixture_ledger(tmp_path)
    logs = _log_schreiben(tmp_path / "ralph-logs", "stufe-1.json", 2.0)
    _run("ralph-abschluss", "--kaskade", "1", "--domaene", "produkt",
         "--logs", str(logs), "--pfad", str(ledger), "--archivieren")

    _log_schreiben(logs, "stufe-2.json", 0.5)
    rc, out, err = _run("ralph-abschluss", "--kaskade", "1",
                         "--domaene", "produkt", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren", "--addieren")

    assert rc == 0, err
    assert len(_zeilen(ledger, "ralph")) == 1
    assert _zeilen(ledger, "ralph")[0]["usd"] == pytest.approx(2.5)
    assert _zeilen(ledger, "roles") == [], \
        "Die ralph-Zeile darf beim Addieren nicht zur roles-Zeile werden"


def test_addieren_ohne_neue_logs_laesst_die_zeile_in_ruhe(tmp_path):
    """Beim Nachlauf EINER Rolle ist die andere Quelle regulaer leer. Dann
    darf --addieren die bestehende Zeile nicht mit "+0.0000" anfassen und
    dabei Datum und Notiz des fremden Nachlaufs hineinschreiben."""
    ledger = _fixture_ledger(tmp_path)
    logs = _log_schreiben(tmp_path / "ralph-logs", "stufe-1.json", 2.1621)
    _run("ralph-abschluss", "--kaskade", "1", "--domaene", "produkt",
         "--logs", str(logs), "--pfad", str(ledger), "--archivieren",
         "--notiz", "Bau")
    vorher = ledger.read_text()

    rc, out, err = _run("ralph-abschluss", "--kaskade", "1",
                         "--domaene", "produkt", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren",
                         "--addieren", "--notiz", "Frank-Nachlauf")

    assert rc == 0, err
    assert ledger.read_text() == vorher, \
        "Ohne neue Logs darf die Zeile byte-identisch bleiben"
    assert "unveraendert" in out
    assert "Frank-Nachlauf" not in ledger.read_text()


@pytest.mark.skipif(not TEAM_STATUS.is_file(),
                    reason="team-status.sh liegt nur in der Installation in "
                           "der Wurzel (im Kit-Repo unter entry/)")
def test_ein_befehl_schliesst_beide_quellen_ab(tmp_path):
    """Der Kern von BL-4: Es ging nie darum, dass man Ralph nicht buchen
    KONNTE — sondern dass kein Befehl es tat. Ein --rollen-abschluss muss
    beide Zeilen erzeugen, sonst passiert im naechsten Closeout dasselbe."""
    repo = tmp_path / "repo"
    (repo / ".ralph-logs").mkdir(parents=True)
    (repo / ".team-logs").mkdir(parents=True)
    _log_schreiben(repo / ".ralph-logs", "stufe-1.json", 2.1621)
    _log_schreiben(repo / ".team-logs", "harry.json", 1.0969)
    (repo / ".budget-ledger").write_text(
        "# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    # Minimalkonfiguration, damit team-status.sh die Werkzeuge findet.
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "team" / "tools" / "kosten.py").write_bytes(KOSTEN_PY.read_bytes())
    (repo / "team" / "lib.sh").write_bytes((REPO_ROOT / "team" / "lib.sh").read_bytes())
    (repo / "team.config.sh").write_bytes(
        (REPO_ROOT / "team.config.sh").read_bytes())
    ziel = repo / "team-status.sh"
    ziel.write_bytes(TEAM_STATUS.read_bytes())
    ziel.chmod(0o755)

    umgebung = dict(os.environ, TEAM_DOMAENEN="produkt team")
    ergebnis = subprocess.run(
        ["bash", str(ziel), "--rollen-abschluss", "1", "produkt"],
        capture_output=True, text=True, cwd=str(repo), env=umgebung)

    assert ergebnis.returncode == 0, ergebnis.stderr
    ledger = repo / ".budget-ledger"
    assert len(_zeilen(ledger, "roles")) == 1, "Sweep-/Fix-Kosten fehlen"
    assert len(_zeilen(ledger, "ralph")) == 1, \
        "BL-4: Ralphs Baukosten fehlen im Ledger — genau der Feldfehler"
    assert _zeilen(ledger, "ralph")[0]["usd"] == pytest.approx(2.1621)
    # Und beide Rohlog-Ordner sind rotiert, sonst zaehlt die naechste
    # Kontostandsabfrage dieselben Kosten doppelt (BL-17).
    assert not list((repo / ".ralph-logs").glob("*.json"))
    assert not list((repo / ".team-logs").glob("*.json"))

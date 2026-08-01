#!/usr/bin/env python3
"""Regressionstest fuer Roadmap-Skizze D: das Ledger prueft seine eigene
Vollstaendigkeit.

Warum es das Werkzeug gibt: BL-1, BL-4 und BL-5 sind alle drei NICHT durch
einen Test oder ein Werkzeug aufgefallen, sondern dadurch, dass ein Mensch den
gedruckten Bericht neben das Ledger hielt. Dreimal dasselbe Muster -- ein
Bericht, der seine Kennzahl aus derselben Quelle zieht wie das, was er pruefen
soll, bestaetigt einen Fehler, statt ihn zu zeigen. `ledger-pruefen` zieht
seine Gegenkennzahl deshalb aus den archivierten ROHLOGS.

Die beiden schwersten Faelle werden mit den ECHTEN Feldzahlen nachgestellt
(Feldprojekt team-kit_project_platformer, Kaskade 1, 2026-08-01):
  * BL-4: 2,1621 USD Baukosten in KEINER Ledger-Zeile,
  * BL-5: eine roles-Zeile ueber 2,4114 USD, die 1,0969 USD ueberschrieben hat.
Beide muessen als WARNUNG anschlagen und Exit 4 ergeben.

Netz-/CLI-frei gegen temporaere Fixture-Verzeichnisse -- nie das echte
.ralph-logs/.team-logs (Muster wie test_bl4_ralph_abschluss.py).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = REPO_ROOT / "team" / "tools" / "kosten.py"
TEAM_STATUS = REPO_ROOT / "team-status.sh"

KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _run(*args):
    result = subprocess.run(
        [sys.executable, str(KOSTEN_PY), "ledger-pruefen", *args],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _ledger(tmp_path, *zeilen):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(KOPF + "".join(z if z.endswith("\n") else z + "\n"
                                    for z in zeilen))
    return pfad


def _zeile(kaskade, usd, rolle, domaene="produkt", auth="abo"):
    return (f"2026-08-01 | {kaskade} | {usd:.4f} | {auth} | {domaene} | "
            f"{rolle} | Testzeile")


def _log(verzeichnis, name, usd):
    verzeichnis.mkdir(parents=True, exist_ok=True)
    (verzeichnis / name).write_text(json.dumps({"total_cost_usd": usd}))


def _leere_logs(tmp_path):
    """Zwei Log-Ordner OHNE archiv/ -- so bleibt P3 stumm und ein Test sieht
    genau die Pruefung, die er meint."""
    ralph = tmp_path / ".ralph-logs"
    team = tmp_path / ".team-logs"
    ralph.mkdir()
    team.mkdir()
    return ["--ralph-logs", str(ralph), "--team-logs", str(team)]


# --- P1: Vollstaendigkeit je Kaskade -----------------------------------------

def test_vollstaendige_kaskade_ist_sauber(tmp_path):
    """Alle drei Quellen gebucht, kein Archiv -> keine Befunde, Exit 0."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 2.1621, "ralph"),
                    _zeile("1", 1.0969, "roles"),
                    _zeile("1", 6.1614, "architekt"))
    rc, out, _ = _run("--pfad", str(pfad), *_leere_logs(tmp_path))
    assert rc == 0, out
    assert "keine Befunde" in out


def test_bl4_fehlende_ralph_zeile_ist_warnung(tmp_path):
    """DER BL-4-Fall: roles gebucht, ralph nicht. Muss WARNUNG + Exit 4 sein --
    wer gesweept hat, hat vorher gebaut."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 1.0969, "roles"),
                    _zeile("1", 6.1614, "architekt"))
    rc, out, _ = _run("--pfad", str(pfad), *_leere_logs(tmp_path))
    assert rc == 4, out
    assert "[WARNUNG]" in out
    assert "keine ralph-Zeile" in out
    assert "BL-4" in out


def test_fehlende_roles_zeile_ist_nur_hinweis(tmp_path):
    """Ein Lauf ohne Red Team ist moeglich -- Hinweis, aber Exit 0. Sonst
    wuerde das Werkzeug zu Rauschen erziehen, das man wegklickt."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 2.1621, "ralph"),
                    _zeile("1", 6.1614, "architekt"))
    rc, out, _ = _run("--pfad", str(pfad), *_leere_logs(tmp_path))
    assert rc == 0, out
    assert "[Hinweis]" in out
    assert "keine roles-Zeile" in out
    assert "[WARNUNG]" not in out


def test_fehlende_architekt_zeile_ist_nur_hinweis(tmp_path):
    pfad = _ledger(tmp_path,
                    _zeile("1", 2.1621, "ralph"),
                    _zeile("1", 1.0969, "roles"))
    rc, out, _ = _run("--pfad", str(pfad), *_leere_logs(tmp_path))
    assert rc == 0, out
    assert "keine architekt-Zeile" in out


def test_geplante_kaskade_ohne_lauf_wird_nicht_bemaengelt(tmp_path):
    """Nur eine architekt-Zeile = geplant, aber nie gelaufen. Dafuer fehlt
    nichts -- sonst meldet das Werkzeug jede frisch geplante Kaskade."""
    pfad = _ledger(tmp_path, _zeile("2", 6.1614, "architekt"))
    rc, out, _ = _run("--pfad", str(pfad), *_leere_logs(tmp_path))
    assert rc == 0, out
    assert "keine Befunde" in out


def test_altzeilen_ohne_rolle_werden_gemeldet_nicht_bewertet(tmp_path):
    """BL-29-Altschema (5 Felder): keine Rolle, also nicht pruefbar. Gezaehlt
    melden statt stillschweigend einer Quelle zuschlagen."""
    pfad = _ledger(tmp_path, "2026-07-11 | 6 | 3.5000 | abo | Altzeile")
    rc, out, _ = _run("--pfad", str(pfad), *_leere_logs(tmp_path))
    assert rc == 0, out
    assert "1 Ledger-Zeile(n) im alten 5-Feld-Schema" in out


def test_kaskaden_numerisch_sortiert(tmp_path):
    """10 darf nicht vor 2 stehen -- eine Befundliste, die man nicht der Reihe
    nach lesen kann, wird nicht gelesen."""
    pfad = _ledger(tmp_path,
                    _zeile("10", 1.0, "roles"),
                    _zeile("2", 1.0, "roles"))
    _, out, _ = _run("--pfad", str(pfad), *_leere_logs(tmp_path))
    assert out.index("Kaskade 2:") < out.index("Kaskade 10:")


# --- P2: abgeschlossen, aber unarchiviert ------------------------------------

def test_bl5_unarchivierte_logs_bei_gebuchter_kaskade(tmp_path):
    """DER BL-5-Fall: Kaskade gebucht, danach lief noch eine Rolle. Genau hier
    hat ein zweiter --rollen-abschluss im Feld den Altwert ueberschrieben."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 2.1621, "ralph"),
                    _zeile("1", 1.0969, "roles"))
    ralph = tmp_path / ".ralph-logs"
    team = tmp_path / ".team-logs"
    ralph.mkdir()
    _log(team, "frank-HM-4-v1-20260801-120000.json", 1.3145)
    rc, out, _ = _run("--pfad", str(pfad), "--kaskade", "1",
                       "--ralph-logs", str(ralph), "--team-logs", str(team))
    assert rc == 4, out
    assert "unarchivierte Log(s)" in out
    assert "--addieren" in out


def test_offene_kaskade_mit_logs_ist_kein_befund(tmp_path):
    """Unarchivierte Logs waehrend eines LAUFENDEN Baus sind der Normalzustand
    -- die Kaskade ist noch nicht gebucht. Kein Befund."""
    pfad = _ledger(tmp_path, _zeile("1", 2.1621, "ralph"))
    ralph = tmp_path / ".ralph-logs"
    team = tmp_path / ".team-logs"
    team.mkdir()
    _log(ralph, "stufe-4-20260801-120000.json", 0.7)
    rc, out, _ = _run("--pfad", str(pfad), "--kaskade", "2",
                       "--ralph-logs", str(ralph), "--team-logs", str(team))
    assert rc == 0, out
    assert "unarchivierte" not in out


# --- P3: Gegenprobe gegen die archivierten Rohlogs ---------------------------

def test_bl4_rohlogs_ohne_ledger_zeile_schlagen_an(tmp_path):
    """Die eigentliche Skizze-D-Pruefung, mit der echten Feldzahl: 2,1621 USD
    liegen archiviert in .ralph-logs/archiv, im Ledger steht dazu nichts. Das
    ist BL-4, gesehen aus einer ANDEREN Quelle als der Ledger selbst.

    Die ralph-Zeile steht hier bewusst MIT 0.0000 im Ledger: So schweigt P1
    (die Zeile existiert ja), und der Befund kann NUR aus der Gegenprobe
    stammen. Das ist zugleich der haerteste Fall -- ein Abschluss, der auf
    leere Log-Ordner lief und brav 0.0000 gebucht hat (HM-43)."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 0.0, "ralph"),
                    _zeile("1", 1.0969, "roles"),
                    _zeile("1", 6.1614, "architekt"))
    ralph = tmp_path / ".ralph-logs"
    team = tmp_path / ".team-logs"
    team.mkdir()
    _log(ralph / "archiv", "stufe-1-20260801-100000.json", 0.7207)
    _log(ralph / "archiv", "stufe-2-20260801-110000.json", 0.7207)
    _log(ralph / "archiv", "stufe-3-20260801-120000.json", 0.7207)
    rc, out, _ = _run("--pfad", str(pfad),
                       "--ralph-logs", str(ralph), "--team-logs", str(team))
    assert rc == 4, out
    assert "ralph-untergebucht" not in out      # Code ist intern, Text zaehlt
    assert "2.1621 USD" in out
    assert "nie gebucht" in out


def test_bl5_ueberschriebener_altwert_schlaegt_an(tmp_path):
    """BL-5 mit den echten Zahlen: archiviert sind 1,0969 + 2,4114 = 3,5083
    USD, im Ledger steht nur die ueberschreibende 2,4114er-Zeile. Die
    Differenz von 1,0969 USD ist genau der verlorene Altwert. ralph- und
    architekt-Zeile stehen mit, damit P1 schweigt und der Befund NUR aus der
    Gegenprobe stammen kann."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 2.4114, "roles"),
                    _zeile("1", 2.1621, "ralph"),
                    _zeile("1", 6.1614, "architekt"))
    ralph = tmp_path / ".ralph-logs"
    team = tmp_path / ".team-logs"
    ralph.mkdir()
    _log(team / "archiv", "harry-20260801-100000.json", 1.0969)
    _log(team / "archiv", "frank-HM-1-v1-20260801-110000.json", 2.4114)
    rc, out, _ = _run("--pfad", str(pfad),
                       "--ralph-logs", str(ralph), "--team-logs", str(team))
    assert rc == 4, out
    assert "1.0969 USD sind archiviert" in out


def test_ledger_groesser_als_rohlogs_ist_kein_befund(tmp_path):
    """Frischer Clone: Die Log-Ordner sind gitignoriert, das Ledger ist die
    einzige Quelle. Nur die Richtung "Rohlogs > Ledger" ist ein Verlust --
    die Gegenrichtung ist der Sinn des Ledgers."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 9.4204, "ralph"),
                    _zeile("1", 1.0969, "roles"))
    ralph = tmp_path / ".ralph-logs"
    team = tmp_path / ".team-logs"
    team.mkdir()
    _log(ralph / "archiv", "stufe-1-20260801-100000.json", 0.7207)
    rc, out, _ = _run("--pfad", str(pfad),
                       "--ralph-logs", str(ralph), "--team-logs", str(team))
    assert rc == 0, out
    assert "untergebucht" not in out
    assert "nie gebucht" not in out


def test_rundungsdifferenz_schlaegt_nicht_an(tmp_path):
    """Jede Zeile ist auf 4 Stellen gerundet. Ein Cent Differenz darf keinen
    Alarm ausloesen, sonst ist das Werkzeug nach zwei Kaskaden wertlos."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 1.0000, "roles"),
                    _zeile("1", 2.1621, "ralph"),
                    _zeile("1", 6.1614, "architekt"))
    ralph = tmp_path / ".ralph-logs"
    team = tmp_path / ".team-logs"
    ralph.mkdir()
    _log(team / "archiv", "harry-20260801-100000.json", 1.005)
    rc, out, _ = _run("--pfad", str(pfad),
                       "--ralph-logs", str(ralph), "--team-logs", str(team))
    assert rc == 0, out


# --- Bedienoberflaeche -------------------------------------------------------

def test_fehlendes_ledger_ist_hinweis_kein_fehler(tmp_path):
    rc, out, _ = _run("--pfad", str(tmp_path / "gibt-es-nicht"),
                       *_leere_logs(tmp_path))
    assert rc == 0, out
    assert "nie ein Abschluss gebucht" in out


def test_unbekanntes_argument_ist_bedienfehler_exit_1(tmp_path):
    """Exit 1 bleibt dem Bedienfehler vorbehalten, 4 dem Befund -- sonst kann
    ein Aufrufer 'Werkzeug falsch benutzt' nicht von 'Ledger unvollstaendig'
    unterscheiden."""
    rc, _, err = _run("--pfad", str(_ledger(tmp_path)), "--quatsch")
    assert rc == 1
    assert "unbekanntes Argument" in err


def test_team_status_reicht_durch(tmp_path):
    """Der Fehler war nie, dass man nicht haette pruefen KOENNEN, sondern dass
    kein Befehl es tat -- also wird die Bedienhandlung selbst geprueft."""
    if not TEAM_STATUS.exists():
        pytest.skip("team-status.sh liegt erst in der Installation in der Wurzel")
    pfad = _ledger(tmp_path, _zeile("1", 1.0969, "roles"))
    result = subprocess.run(
        ["bash", str(TEAM_STATUS), "--ledger-pruefen", "--pfad", str(pfad),
         *_leere_logs(tmp_path)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 4, result.stdout + result.stderr
    assert "keine ralph-Zeile" in result.stdout

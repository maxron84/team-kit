#!/usr/bin/env python3
"""BL-27/BL-45: Der Waechter war fuer die vergessene Buchung blind, und der
Buchungsbefehl fuer den falschen Zeitraum.

BL-27 (Feld A, Closeout K13): Kaskade 12 war vollstaendig gebaut und
abgeschlossen, aber `--rollen-abschluss 12 …` lief nie. 33,89 USD lagen
ungebucht in den gitignorierten Logordnern, im Ledger stand nur die
architekt-Zeile — `ledger-pruefen` meldete NULL Warnungen. Grund: P1
ueberspringt jede Kaskade ohne ralph/roles-Zeile als "geplant, aber nie
gelaufen". Das Unterscheidungsmerkmal lag daneben: Eine geplante Kaskade hat
keine unarchivierten Rohlogs, eine vergessene hat welche.

BL-45 (Feld A, Closeout K28): Im .team-logs lag ein Axel-Lauf ueber
4,2560 USD aus einer Out-of-Loop-Fixrunde, die NACH dem Abschluss der Kaskade
27 und VOR dem ersten Commit der Kaskade 28 stattfand. `--rollen-abschluss`
bucht schlicht alles, was im Ordner liegt, unter der genannten Nummer. Auffallen
konnte das nur einem Menschen, der die Zeitstempel von Hand gegen den
Kaskadenbeginn haelt — der Befehl selbst schwieg.

Beide Male dieselbe Klasse: Das Werkzeug kennt eine Groesse (Rohlogs bzw. ihren
Zeitpunkt), wertet sie aber an der Stelle nicht aus, an der sie etwas beweisen
wuerde.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _log(ordner, name, usd, mtime=None):
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / name
    pfad.write_text(json.dumps({"total_cost_usd": usd}), encoding="utf-8")
    if mtime is not None:
        os.utime(pfad, (mtime, mtime))
    return pfad


# --- BL-27 -------------------------------------------------------------------

def _repo_mit_geplanter_kaskade(tmp_path, alte_logs=False, frische_logs=False):
    """Nachgestellte Feldlage: Kaskade 13 ist scharfgeschaltet (Plandatei
    committet), im Ledger steht fuer sie nur die architekt-Zeile. Die
    Kaskade 12 davor wurde gebaut, aber nie abgeschlossen — ihre Logs liegen
    noch da und sind AELTER als der Beginn der 13."""
    repo = _git_repo(tmp_path)
    _kaskade_anlegen(repo, "13", "aktuell")
    beginn = kosten.kaskade_beginn("13", str(repo))
    (repo / ".ralph-logs").mkdir(exist_ok=True)
    (repo / ".team-logs").mkdir(exist_ok=True)
    (repo / ".budget-ledger").write_text(
        KOPF + "2026-08-08 | 13 | 9.0000 | api | produkt | architekt | K13 geplant\n",
        encoding="utf-8")
    if alte_logs:
        _log(repo / ".team-logs", "harry-k12.json", 20.0, mtime=beginn - 7200)
        _log(repo / ".ralph-logs", "stufe-1-k12.json", 13.89, mtime=beginn - 7200)
    if frische_logs:
        _log(repo / ".ralph-logs", "stufe-4.json", 0.7, mtime=beginn + 600)
    return repo


def _befunde(repo, kaskade="13"):
    return kosten.ledger_pruefen(
        str(repo / ".budget-ledger"),
        ralph_logs=str(repo / ".ralph-logs"),
        team_logs=str(repo / ".team-logs"),
        aktuelle_kaskade=kaskade, repo=str(repo))


def test_gebaute_aber_unbebuchte_kaskade_wird_zur_warnung(tmp_path):
    """Der Feldfall: Die Logs des vorigen Durchgangs liegen noch da, im
    Ledger steht fuer ihn kein Rollenabschluss."""
    repo = _repo_mit_geplanter_kaskade(tmp_path, alte_logs=True)
    treffer = [b for b in _befunde(repo) if b["code"] == "abschluss-fehlt"]
    assert len(treffer) == 1, [b["code"] for b in _befunde(repo)]
    assert treffer[0]["schwere"] == "warnung"
    assert "33.8900" in treffer[0]["text"], \
        "die Meldung muss den ungebuchten Betrag nennen"
    assert "--rollen-abschluss" in treffer[0]["text"]


def test_wirklich_geplante_kaskade_bleibt_still(tmp_path):
    """Gegenprobe — ohne Rohlogs ist 'geplant, nie gelaufen' die richtige
    Lesart, und eine Warnung waere die Falle aus BL-14."""
    repo = _repo_mit_geplanter_kaskade(tmp_path)
    assert not [b for b in _befunde(repo) if b["code"] == "abschluss-fehlt"]


def test_frische_logs_eines_laufenden_baus_bleiben_still(tmp_path):
    """DIE Gegenprobe zu diesem Fund: Waehrend gebaut wird, liegen
    unarchivierte Logs — das ist der Normalzustand (test_bl13). Eine Warnung
    darauf erschiene bei jedem --budget mitten im Lauf."""
    repo = _repo_mit_geplanter_kaskade(tmp_path, frische_logs=True)
    assert not [b for b in _befunde(repo) if b["code"] == "abschluss-fehlt"]


def test_ersatzzettel_allein_loest_keine_warnung_aus(tmp_path):
    """BL-46: Ein verworfener Versuch ist kein Kostenbeleg — er darf den
    Dauer-Fehlalarm nicht durch die Hintertuer zurueckbringen."""
    repo = _repo_mit_geplanter_kaskade(tmp_path)
    beginn = kosten.kaskade_beginn("13", str(repo))
    zettel = repo / ".team-logs" / "verworfen.json"
    zettel.write_text(
        json.dumps({"team_versuch": "verworfen", "total_cost_usd": None}),
        encoding="utf-8")
    os.utime(zettel, (beginn - 7200, beginn - 7200))
    assert not [b for b in _befunde(repo) if b["code"] == "abschluss-fehlt"]


def test_abgeschlossene_kaskade_meldet_nicht_doppelt(tmp_path):
    """Ist die Kaskade gebucht, ist P2 zustaendig — nicht P1b."""
    repo = _repo_mit_geplanter_kaskade(tmp_path, alte_logs=True)
    with open(repo / ".budget-ledger", "a", encoding="utf-8") as f:
        f.write("2026-08-08 | 13 | 20.0000 | abo | produkt | roles | Rollen\n")
        f.write("2026-08-08 | 13 | 13.8900 | abo | produkt | ralph | Bau\n")
    codes = [b["code"] for b in _befunde(repo)]
    assert "abschluss-fehlt" not in codes
    assert "unarchiviert" in codes


def test_ohne_git_wird_nicht_geraten(tmp_path):
    """Kein ermittelbarer Beginn -> kein Befund, statt Verdacht auf Verdacht."""
    (tmp_path / ".ralph-logs").mkdir()
    (tmp_path / ".team-logs").mkdir()
    _log(tmp_path / ".team-logs", "harry.json", 20.0, mtime=1000)
    (tmp_path / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    befunde = kosten.ledger_pruefen(
        str(tmp_path / ".budget-ledger"),
        ralph_logs=str(tmp_path / ".ralph-logs"),
        team_logs=str(tmp_path / ".team-logs"),
        aktuelle_kaskade="13", repo=str(tmp_path))
    assert not [b for b in befunde if b["code"] == "abschluss-fehlt"]


# --- BL-45 -------------------------------------------------------------------

def _git_repo(tmp_path):
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"]):
        subprocess.run(["git", "-C", str(tmp_path), *befehl], check=True,
                       capture_output=True)
    (tmp_path / "plans").mkdir()
    (tmp_path / "team" / "tools").mkdir(parents=True)
    (tmp_path / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    return tmp_path


def _kaskade_anlegen(repo, nummer, thema="thema"):
    plan = repo / "plans" / f"ralph-kaskade-{nummer}-{thema}.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m",
                    f"K{nummer} scharf"], check=True, capture_output=True)
    return plan


def test_kaskade_beginn_kommt_aus_dem_plan_commit(tmp_path):
    repo = _git_repo(tmp_path)
    vorher = time.time()
    _kaskade_anlegen(repo, "28")
    beginn = kosten.kaskade_beginn("28", str(repo))
    assert beginn is not None
    assert beginn >= int(vorher) - 5


def test_log_von_vor_dem_kaskadenbeginn_wird_gemeldet(tmp_path):
    """Der Feldfall: ein Out-of-Loop-Lauf zwischen zwei Kaskaden."""
    repo = _git_repo(tmp_path)
    _kaskade_anlegen(repo, "28")
    beginn = kosten.kaskade_beginn("28", str(repo))
    alt = _log(repo / ".team-logs", "axel-out-of-loop.json", 4.2560,
               mtime=beginn - 3600)
    neu = _log(repo / ".team-logs", "harry.json", 1.0, mtime=beginn + 60)

    _, zu_alt = kosten.logs_vor_kaskadenbeginn([str(alt), str(neu)], "28",
                                                str(repo))
    assert [Path(d).name for d, _ in zu_alt] == ["axel-out-of-loop.json"]


def test_cli_nennt_das_zu_alte_log_beim_buchen(tmp_path):
    repo = _git_repo(tmp_path)
    _kaskade_anlegen(repo, "28")
    beginn = kosten.kaskade_beginn("28", str(repo))
    _log(repo / ".team-logs", "axel-out-of-loop.json", 4.2560,
         mtime=beginn - 3600)
    _log(repo / ".team-logs", "harry.json", 1.0, mtime=beginn + 60)

    ergebnis = subprocess.run(
        [sys.executable, str(kit_pfad("tools", "kosten.py")),
         "rollen-abschluss", "--kaskade", "28", "--domaene", "produkt",
         "--logs", str(repo / ".team-logs"),
         "--pfad", str(repo / ".budget-ledger"), "--repo", str(repo)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "AELTER als der Beginn" in ergebnis.stderr
    assert "axel-out-of-loop.json" in ergebnis.stderr
    assert "vor-N" in ergebnis.stderr, \
        "die Meldung muss den Ausweg nennen, nicht nur das Problem"
    # Kein Abbruch: gebucht wird trotzdem, der Mensch entscheidet.
    zeilen = [z for z in kosten.ledger_zeilen(str(repo / ".budget-ledger"))
              if z["rolle"] == "roles"]
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == pytest.approx(5.2560)


def test_ohne_plandatei_wird_nicht_geraten(tmp_path):
    """Kein Beginn ermittelbar -> kein Hinweis. Ein Werkzeug, das bei
    fehlender Information warnt, warnt immer."""
    repo = _git_repo(tmp_path)
    alt = _log(repo / ".team-logs", "irgendwas.json", 1.0, mtime=1000)
    beginn, zu_alt = kosten.logs_vor_kaskadenbeginn([str(alt)], "28", str(repo))
    assert beginn is None and zu_alt == []

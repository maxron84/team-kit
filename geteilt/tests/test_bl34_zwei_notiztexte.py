#!/usr/bin/env python3
"""BL-34: Ein Notiztext kann nicht zwei Ledger-Zeilen beschreiben.

`--rollen-abschluss` schreibt ZWEI Zeilen (BL-4): `roles` fuer die Sweeps und
Fixes, `ralph` fuer den Bau. Bis hierher trugen beide DENSELBEN, von Hand
getippten Text. BL-19 hat je Zielrolle einen Vorspann eingefuehrt ("Rollen: …"
/ "Bau: …") — damit sind die Zeilen unterscheidbar, aber nicht richtig
beschriftet: Der Mensch tippt beim Abschluss, woran er gerade denkt, und das
ist das Red Team.

Zwei Feldinstanzen, beide beim selben Architekten:
  * K4: Ralphs Zeile ueber vier Baustufen trug "Harry/Marv-Sweeps + Frank
    HM-9/HM-10" — von jemandem, der BL-19 eine halbe Stunde vorher gelesen
    hatte.
  * K28: Die Notiz "enthaelt zusaetzlich den Axel-Lauf zu HM-74" landete auch
    auf der Ralph-Zeile — von jemandem, der die Regel im selben
    Closeout-Dokument zitiert hatte.

Damit steht "die Disziplinloesung traegt hier nicht" auf zwei Beinen. Der Fix
ist Variante (2) der Fix-Skizze: Die Bau-Notiz wird aus dem Plannamen
ABGELEITET, wenn der Mensch keine eigene angibt — die Information liegt in
.ralph-plan vor und ist fuer eine Bau-Zeile die richtige.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, kit_pfad, werkzeug_wert

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

import os as _os
_dom = _os.environ.get("TEAM_DOMAENEN", "").replace(",", " ").split()
DOMAENE = _dom[0] if _dom else "produkt"

KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _entrypoint(name):
    for kandidat in (REPO_ROOT / name,
                     REPO_ROOT / "bash" / "entry" / name,
                     REPO_ROOT / "pwsh" / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


TEAM_STATUS = _entrypoint("team-status.sh")
pytestmark = pytest.mark.skipif(TEAM_STATUS is None,
                                 reason="team-status.sh nicht gefunden")


def _repo(tmp_path, plan="plans/ralph-kaskade-4-kamera.md"):
    (tmp_path / "team" / "tools").mkdir(parents=True)
    (tmp_path / "plans").mkdir()
    (tmp_path / ".team-logs").mkdir()
    (tmp_path / ".ralph-logs").mkdir()
    shutil.copy(TEAM_STATUS, tmp_path / "team-status.sh")
    shutil.copy(kit_pfad("lib.sh"), tmp_path / "team" / "lib.sh")
    shutil.copy(kit_pfad("tools", "kosten.py"),
                tmp_path / "team" / "tools" / "kosten.py")
    (tmp_path / "team.config.sh").write_text(
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        f'TEAM_DOMAENEN="{DOMAENE} team"\nexport TEAM_DOMAENEN\n',
        encoding="utf-8")
    (tmp_path / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    (tmp_path / ".ralph-plan").write_text(plan + "\n", encoding="utf-8")
    (tmp_path / plan).write_text("# Plan\n", encoding="utf-8")
    return tmp_path


def _abschluss(repo, *args):
    return subprocess.run([BASH, "./team-status.sh", "--rollen-abschluss",
                           *args], cwd=repo, capture_output=True, text=True)


def _notiz(repo, rolle):
    zeilen = [z for z in kosten.ledger_zeilen(str(repo / ".budget-ledger"))
              if z["rolle"] == rolle]
    assert len(zeilen) == 1, f"genau eine {rolle}-Zeile erwartet: {zeilen}"
    return zeilen[0]["notiz"]


def test_rollentext_landet_nicht_auf_der_bauzeile(tmp_path):
    """Der Feldfehler selbst."""
    repo = _repo(tmp_path)
    ergebnis = _abschluss(repo, "4", DOMAENE, "Harry/Marv-Sweeps + Frank HM-9")
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "Harry/Marv-Sweeps" in _notiz(repo, "roles")
    assert "Harry" not in _notiz(repo, "ralph"), \
        "die Bau-Zeile behauptet, die Arbeit des Red Teams zu enthalten"


def test_bauzeile_wird_aus_dem_plannamen_abgeleitet(tmp_path):
    repo = _repo(tmp_path)
    _abschluss(repo, "4", DOMAENE, "Sweeps")
    notiz = _notiz(repo, "ralph")
    assert "K4" in notiz and "kamera" in notiz, \
        f"Bau-Notiz sollte aus dem Plannamen kommen, ist: {notiz}"


def test_zweiter_text_schlaegt_die_ableitung(tmp_path):
    repo = _repo(tmp_path)
    _abschluss(repo, "4", DOMAENE, "Sweeps", "vier Baustufen Kameraführung")
    assert "vier Baustufen" in _notiz(repo, "ralph")
    assert "Sweeps" in _notiz(repo, "roles")
    assert "Sweeps" not in _notiz(repo, "ralph")


def _log(repo, ordner, name, usd):
    (repo / ordner / name).write_text(
        '{"total_cost_usd": %s}' % usd, encoding="utf-8")


def test_modus_bleibt_hinter_beiden_texten_erkennbar(tmp_path):
    """--addieren darf nicht als Notiztext gelesen werden — weder als erster
    noch als zweiter. Mit echten Logs, weil ein Nachlauf ohne neue Logs
    regulaer gar nichts bucht (HM-43)."""
    repo = _repo(tmp_path)
    _log(repo, ".team-logs", "lauf1.json", 1.0)
    _abschluss(repo, "4", DOMAENE, "Sweeps", "Bau K4")
    _log(repo, ".team-logs", "lauf2.json", 0.5)
    ergebnis = _abschluss(repo, "4", DOMAENE, "Nachlauf Frank", "Bau K4",
                          "--addieren")
    assert ergebnis.returncode == 0, ergebnis.stderr
    notiz = _notiz(repo, "roles")
    assert "addiert auf Bestand" in notiz
    assert "--addieren" not in notiz


def test_ohne_notiz_bleibt_die_bauzeile_trotzdem_abgeleitet(tmp_path):
    repo = _repo(tmp_path)
    ergebnis = _abschluss(repo, "4", DOMAENE)
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "K4" in _notiz(repo, "ralph")


def test_ohne_erkennbaren_plannamen_bleibt_die_zeile_ehrlich_unbeschriftet(
        tmp_path):
    """Lieber gar keine Beschriftung als eine erfundene."""
    repo = _repo(tmp_path, plan="plans/sonderlauf.md")
    ergebnis = _abschluss(repo, "4", DOMAENE, "Sweeps")
    assert ergebnis.returncode == 0, ergebnis.stderr
    notiz = _notiz(repo, "ralph")
    assert "Sweeps" not in notiz
    assert notiz.startswith("Bau"), notiz

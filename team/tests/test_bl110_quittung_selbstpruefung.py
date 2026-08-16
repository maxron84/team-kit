#!/usr/bin/env python3
"""BL-110: Der vierte Ausgang (BL-41) prueft sich selbst.

Die Erkennung aus BL-41 ist richtig, aber sie haelt den Lauf an und legt einem
Menschen eine Pruefliste vor, deren Schritte IMMER dieselben sind. Im Feld
(Projekt platformer) ist der Fall in neun Kaskaden aufgetreten - K27, K28,
K29, K33, K34, K35 (dort dreimal), K36, K37 - und jedes Mal lautete das
Ergebnis "Arbeit fertig, nur die Quittung fehlt". Eine Pruefliste, die neunmal
dasselbe ergibt, ist eine Funktion, die noch niemand geschrieben hat.

Der teure Fehler waere die Gegenrichtung: eine HALB gebaute Stufe
durchzuwinken. Genau davor war die Pruefliste blind (BL-135, Feld platformer):
Sie fragt nach Commit und gruenem Baum, nicht nach der Existenz der
Zusicherungen. Die Selbstpruefung schliesst diese Luecke und ist deshalb ein
UND ueber drei Bedingungen - faellt eine durch, meldet der Loop unveraendert
an den Menschen.

Diese Datei sichert BEIDE Richtungen: dass automatisch quittiert wird, wenn
alles stimmt, und dass es bei jeder einzelnen offenen Bedingung NICHT
geschieht.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _entrypoint(name):
    for kandidat in (REPO_ROOT / name, REPO_ROOT / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


RALPH = _entrypoint("ralph.sh")
pytestmark = pytest.mark.skipif(RALPH is None, reason="ralph.sh nicht gefunden")


def _repo(tmp_path, smoke_rc=0):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "team" / "prompts").mkdir()
    (repo / "plans").mkdir()
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    shutil.copy(REPO_ROOT / "team" / "lib.sh", repo / "team" / "lib.sh")
    shutil.copy(RALPH, repo / "ralph.sh")
    for werkzeug in ("beutebuch.py", "kosten.py"):
        shutil.copy(REPO_ROOT / "team" / "tools" / werkzeug,
                    repo / "team" / "tools" / werkzeug)
    for briefing in (REPO_ROOT / "team" / "prompts").glob("*.md"):
        shutil.copy(briefing, repo / "team" / "prompts" / briefing.name)
    (repo / "team.config.sh").write_text(
        'TEAM_PROJEKT="fixture"\n'
        'TEAM_PRODUKTIVCODE="src/"\nTEAM_TEST_ORDNER="tests/"\n'
        'TEAM_PLAN_ORDNER="plans/"\n'
        'TEAM_BEUTEBUCH="plans/beutebuch.md"\n'
        'TEAM_BEUTEBUCH_TOOL="python3 team/tools/beutebuch.py"\n'
        'TEAM_KOSTEN_TOOL="python3 team/tools/kosten.py"\n'
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n'
        'TEAM_SMOKE_TEST="./smoke.sh"\n'
        'TEAM_CHANGELOG="CHANGELOG.md"\n'
        'TEAM_ERMITTLUNGSAKTEN="plans/ermittlungsakten"\n'
        'TEAM_ROADMAP="plans/roadmap-skizzen.md"\n'
        'TEAM_BACKLOG="plans/backlog.md"\n'
        'TEAM_FIX_PRAEFIX="fix(uat)"\nTEAM_FEAT_PRAEFIX="feat"\n'
        'TEAM_ROLE_BUDGET_USD="5"\nTEAM_ROLE_HARDCAP_USD="10"\n',
        encoding="utf-8")
    (repo / "plans" / "ralph-kaskade-1-fixture.md").write_text(
        "RALPH_CAP=1\n\n## Stufe 1\nBau etwas.\n", encoding="utf-8")
    (repo / ".ralph-plan").write_text(
        "plans/ralph-kaskade-1-fixture.md\n", encoding="utf-8")
    (repo / ".ralph-state").write_text("1\n", encoding="utf-8")
    (repo / "smoke.sh").write_text(
        f"#!/usr/bin/env bash\nexit {smoke_rc}\n", encoding="utf-8")
    (repo / "smoke.sh").chmod(0o755)
    (repo / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n",
                                        encoding="utf-8")
    (repo / ".gitignore").write_text(
        ".ralph-logs/\n.ralph-state\n.ralph-plan\nbin/\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo


def _lauf(repo, kosten=1.20, baut=None, auto=None):
    """Faehrt ralph.sh gegen eine CLI-Attrappe ohne Quittung.

    `baut` ist eine Liste von Pfaden, die die Attrappe anlegt - so bildet der
    Test nach, was eine echte Stufe im Arbeitsbaum hinterlaesst.
    """
    bin_dir = repo / "bin"
    bin_dir.mkdir(exist_ok=True)
    ergebnis = json.dumps({
        "subtype": "success", "is_error": False, "num_turns": 65,
        "total_cost_usd": kosten,
        "result": ("Waiting for the ./smoke.sh background run to finish "
                   "before proceeding to commit.")})
    zeilen = ["#!/usr/bin/env bash"]
    for pfad in (baut or []):
        zeilen.append(f"mkdir -p \"$(dirname '{pfad}')\"")
        zeilen.append(f"echo 'def test_x(): pass' > '{pfad}'")
    zeilen.append("cat <<'JSON'")
    zeilen.append(ergebnis)
    zeilen.append("JSON")
    stub = bin_dir / "claude"
    stub.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    stub.chmod(0o755)
    env = dict(os.environ)
    env.update({"PATH": f"{bin_dir}:{env['PATH']}", "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    if auto is not None:
        env["TEAM_QUITTUNG_AUTO"] = auto
    return subprocess.run(["./ralph.sh"], cwd=repo, env=env,
                          capture_output=True, text=True)


# --- Die Richtung, für die es die Automatik gibt -----------------------------

def test_fertige_stufe_ohne_quittung_wird_selbst_quittiert(tmp_path):
    """Der Feldfall neunmal: Arbeit da, Zusicherung da, Baum gruen - nur die
    Quittung fehlt. Vorher Exit 43 und ein angehaltener Lauf."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, baut=["src/modul.py", "tests/test_stufe1_sache.py"])
    assert lauf.returncode == 0, \
        (f"erwartet Exit 0 (selbst quittiert, dann Feierabend am CAP), war "
         f"{lauf.returncode}\nSTDERR:\n{lauf.stderr}")
    assert "Selbstprüfung bestanden" in lauf.stdout, \
        "der Lauf muss sagen, dass und warum er selbst quittiert hat"
    assert (repo / ".ralph-state").read_text().strip() == "2", \
        "der Zeiger MUSS weitergeschaltet sein - sonst war die Automatik wirkungslos"


def test_uncommittete_arbeit_wird_dabei_gesichert(tmp_path):
    """Ohne Commit liefe die naechste Stufe auf einem schmutzigen Baum, und der
    Read-Only-Guard der Sweep-Phase saehe fremde Aenderungen."""
    repo = _repo(tmp_path)
    _lauf(repo, baut=["src/modul.py", "tests/test_stufe1_sache.py"])
    offen = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    assert offen == "", f"der Baum muss sauber sein, offen war:\n{offen}"
    betreff = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--pretty=%s"],
        capture_output=True, text=True).stdout.strip()
    assert "stufe1" in betreff, \
        f"der Sicherungs-Commit muss die Stufe nennen, war: {betreff}"


# --- Die Gegenrichtung: jede einzelne offene Bedingung haelt an --------------

def test_ohne_zusicherung_wird_NICHT_quittiert(tmp_path):
    """BL-135, der Punkt, an dem die Pruefliste fuer den Menschen blind war:
    Produktivcode gebaut, kein Test angefasst. Gruener Baum beweist hier
    nichts - der Bestand prueft das Neue nicht."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, baut=["src/modul.py"])
    assert lauf.returncode == 43, \
        f"erwartet Exit 43 (an den Menschen), war {lauf.returncode}"
    assert "BL-135" in lauf.stderr, \
        "der Grund muss die Fundnummer nennen, sonst sucht der Mensch die Vorgeschichte"
    assert (repo / ".ralph-state").read_text().strip() == "1", \
        "der Zeiger darf NICHT weitergeschaltet werden"


def test_roter_baum_wird_NICHT_quittiert(tmp_path):
    repo = _repo(tmp_path, smoke_rc=1)
    lauf = _lauf(repo, baut=["src/modul.py", "tests/test_stufe1_sache.py"])
    assert lauf.returncode == 43, \
        f"erwartet Exit 43 (an den Menschen), war {lauf.returncode}"
    assert (repo / ".ralph-state").read_text().strip() == "1"


def test_ohne_jede_arbeit_wird_NICHT_quittiert(tmp_path):
    """Kein Commit, keine Aenderung: Das ist kein 'fertig ohne Quittung',
    sondern eine Stufe, die nie angefangen hat."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, baut=[])
    assert lauf.returncode == 43
    assert (repo / ".ralph-state").read_text().strip() == "1"


def test_gesprengter_cap_schliesst_die_automatik_aus(tmp_path):
    """Die Budget-Entscheidung des Menschen darf die Automatik nicht
    ueberschreiben - dort gilt unveraendert 'Stopp VOR dem Weiterschalten'."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, kosten=11.0941,
                 baut=["src/modul.py", "tests/test_stufe1_sache.py"])
    assert lauf.returncode == 43, \
        f"erwartet Exit 43 trotz bestehender Arbeit, war {lauf.returncode}"
    assert "Soft-Cap ebenfalls überschritten" in lauf.stderr
    assert (repo / ".ralph-state").read_text().strip() == "1"


def test_abschaltbar(tmp_path):
    """TEAM_QUITTUNG_AUTO=0 stellt das alte Verhalten wieder her - vollstaendig,
    inklusive der Pruefliste."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, baut=["src/modul.py", "tests/test_stufe1_sache.py"],
                 auto="0")
    assert lauf.returncode == 43
    assert "STUFE FERTIG, QUITTUNG FEHLT" in lauf.stderr
    assert (repo / ".ralph-state").read_text().strip() == "1"

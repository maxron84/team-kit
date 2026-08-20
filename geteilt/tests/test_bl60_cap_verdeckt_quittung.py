#!/usr/bin/env python3
"""BL-60/BL-61: Der Cap verdeckte die Quittungs-Erkennung, und die Anleitung
kannte den dritten Ausgang nicht.

BL-60 (Feld K35, Stufe 167, 11,0941 USD): `team_budget_check` stieg mit
`exit 1` aus, BEVOR `team_quittung_fehlt_melden` zum Zug kam. Eine Stufe, die
BEIDES tut — Soft-Cap sprengen und ohne Quittung enden —, meldete sich als
generischer "Ralph endete mit Fehler (1)": ein Log, das sich selbst fuer
erfolgreich erklaert, und keine Anleitung. Genau die Lage, die Release 2.5.0
beseitigt hatte.

Das ist kein Randfall: Eine lange Stufe ist teurer UND wartet eher auf einen
Hintergrund-Smoke-Test — dieselbe Korrelation, die BL-41 schon belegt hat. Die
Verdeckung trifft deshalb bevorzugt die teuren Stufen. In derselben Kaskade
trat BL-41 dreimal auf (7,46 + 8,88 + 11,09 USD); zweimal griff die Erkennung
vorbildlich, beim dritten Mal verdeckte sie der Cap.

BL-61 (dieselbe Kaskade, Stufe 165, 7,4601 USD): Die Anleitung kannte zwei
Ausgaenge — "beides ja: quittieren" und "sonst: neu bauen". Der Baum war rot,
aber die zwei Fehlschlaege lagen in der NEUEN Testdatei der Stufe; das
330-Zeilen-Produktivmodul war vollstaendig und planungskonform. Ein Neubau
haette fertige, korrekte Arbeit weggeworfen — und bei gleichem Modell,
gleichem Prompt und gleicher Stufe dieselben Aufbaufehler mit hoher
Wahrscheinlichkeit erneut erzeugt.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import entrypoint_aufruf, kit_pfad, pfad_voran, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]


def _entrypoint(name):
    for kandidat in (REPO_ROOT / name,
                     REPO_ROOT / "bash" / "entry" / name,
                     REPO_ROOT / "pwsh" / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


RALPH = _entrypoint("ralph.sh")
pytestmark = pytest.mark.skipif(RALPH is None, reason="ralph.sh nicht gefunden")


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "team" / "prompts").mkdir()
    (repo / "plans").mkdir()
    (repo / "src").mkdir()
    shutil.copy(kit_pfad("lib.sh"), repo / "team" / "lib.sh")
    shutil.copy(RALPH, repo / "ralph.sh")
    for werkzeug in ("beutebuch.py", "kosten.py"):
        shutil.copy(kit_pfad("tools", werkzeug),
                    repo / "team" / "tools" / werkzeug)
    for briefing in (kit_pfad("prompts")).glob("*.md"):
        shutil.copy(briefing, repo / "team" / "prompts" / briefing.name)
    (repo / "team.config.sh").write_text(
        'TEAM_PROJEKT="fixture"\n'
        'TEAM_PRODUKTIVCODE="src/"\nTEAM_TEST_ORDNER="tests/"\n'
        'TEAM_PLAN_ORDNER="plans/"\n'
        'TEAM_BEUTEBUCH="plans/beutebuch.md"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
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
        "RALPH_CAP=3\n\n## Stufe 1\nBau etwas.\n", encoding="utf-8")
    (repo / ".ralph-plan").write_text(
        "plans/ralph-kaskade-1-fixture.md\n", encoding="utf-8")
    (repo / ".ralph-state").write_text("1\n", encoding="utf-8")
    (repo / "smoke.sh").write_text("#!/usr/bin/env bash\nexit 0\n",
                                    encoding="utf-8")
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


def _lauf(repo, kosten, mit_promise):
    """Faehrt ralph.sh gegen eine CLI-Attrappe mit vorgegebenen Kosten."""
    bin_dir = repo / "bin"
    bin_dir.mkdir(exist_ok=True)
    ergebnis = json.dumps({
        "subtype": "success", "is_error": False, "num_turns": 65,
        "total_cost_usd": kosten,
        "result": ("fertig <promise>STUFE_1_COMPLETE</promise>" if mit_promise
                   else "Waiting for the ./smoke.sh background run to finish "
                        "before proceeding to commit.")})
    stub = bin_dir / "claude"
    stub.write_text("#!/usr/bin/env bash\ncat <<'JSON'\n" + ergebnis + "\nJSON\n",
                    encoding="utf-8")
    stub.chmod(0o755)
    env = dict(os.environ)
    env.update({"PATH": pfad_voran(bin_dir, env), "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    return subprocess.run(entrypoint_aufruf("./ralph.sh"), cwd=repo, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_fehlende_quittung_UND_gesprengter_cap_meldet_den_benannten_fall(tmp_path):
    """Der Feldfall: beides zugleich. Vorher generischer Exit 1 ohne Anleitung."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, kosten=11.0941, mit_promise=False)
    assert lauf.returncode == 43, \
        f"erwartet Exit 43 (Stufe fertig, Quittung fehlt), war {lauf.returncode}"
    assert "STUFE FERTIG, QUITTUNG FEHLT" in lauf.stderr
    assert "Soft-Cap ebenfalls überschritten" in lauf.stderr, \
        "die Cap-Überschreitung darf nicht verschwinden, nur weil sie später kommt"
    assert (repo / ".ralph-state").read_text().strip() == "1", \
        "der Zeiger darf NICHT weitergeschaltet werden"


def test_fehlende_quittung_ohne_cap_bleibt_wie_gehabt(tmp_path):
    repo = _repo(tmp_path)
    lauf = _lauf(repo, kosten=1.20, mit_promise=False)
    assert lauf.returncode == 43
    assert "Soft-Cap ebenfalls" not in lauf.stderr, \
        "ohne Überschreitung darf keine Cap-Meldung erscheinen (BL-14)"


def test_quittung_mit_gesprengtem_cap_stoppt_weiterhin(tmp_path):
    """Die Abgrenzung: Der EFFEKT des Caps bleibt unverändert. Liegt die
    Quittung vor und war der Cap gesprengt, stoppt der Lauf ohne
    Weiterschalten — der Commit der Stufe bleibt."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, kosten=11.0941, mit_promise=True)
    assert lauf.returncode == 1
    assert (repo / ".ralph-state").read_text().strip() == "1"


def test_quittung_unter_cap_schaltet_weiter(tmp_path):
    repo = _repo(tmp_path)
    lauf = _lauf(repo, kosten=1.20, mit_promise=True)
    assert (repo / ".ralph-state").read_text().strip() != "1", \
        "der Normalfall muss weiterschalten"


def test_anleitung_kennt_den_dritten_ausgang(tmp_path):
    """BL-61: Rot in NEUEN Testdateien ist etwas anderes als Rot im Bestand."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, kosten=1.20, mit_promise=False)
    text = lauf.stderr
    assert "neu angelegten Testdateien" in text
    assert "ohne eine Zusicherung abzuschwächen" in text.lower() \
        or "OHNE eine Zusicherung abzuschwächen" in text
    assert "BESTEHENDER Testbestand" in text, \
        "die Gegenrichtung fehlt — sonst wird nie mehr neu gebaut"

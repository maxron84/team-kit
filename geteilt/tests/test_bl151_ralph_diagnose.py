#!/usr/bin/env python3
"""BL-151: ralph.sh starb still, bevor die eigene Fehlermeldung lief.

DER FELDFALL
    Feld D, allererster Vollautomatik-Start. Der Mensch sah genau einen Satz:
    "Ralph endete mit Fehler (1) — Vollautomatik stoppt". Das Lauf-Log trug
    denselben einen Satz, obwohl vollautomatik.sh stderr korrekt mitschreibt.
    Die Diagnose, die ralph.sh selbst kennt ("Keine gueltige RALPH_CAP=-Zeile
    in <Plan>"), wurde nie ausgegeben — die Fehlerlage war in 30 Sekunden
    behoben, sie zu FINDEN kostete Log, Skriptlektuere und eine eigene Messung.

DIE MECHANIK
    Unter `set -euo pipefail` reisst eine Kommandosubstitution mit leerem
    `grep` oder fehlgeschlagenem `head` den Aufrufer sofort weg. Das
    `if [ -z … ]` darunter wird NIE erreicht; die Meldung ist toter Text.
    Zwei Stellen: die RALPH_CAP-Zeile und die Stufennummer aus .ralph-state.

DER EIGENTLICHE BEFUND IST DIE DOPPELPFLEGE
    Der Fix war im Kit laengst erfunden. `team_ralph_cap` in lib.sh liest
    denselben Wert und hat mit BL-111 die Schutzform `{ … || true; }`
    bekommen, ausfuehrlich begruendet. ralph.sh hatte die Funktion aber nicht
    aufgerufen, sondern die grep-Kette danebengestellt — und die Kopie hat die
    Haertung nicht mitbekommen. Die pwsh-Bahn hatte den Fehler nie: ralph.ps1
    ruft team_ralph_cap auf und erreicht seine Meldung.

    Deshalb prueft dieser Test BEIDES: dass die Meldungen erscheinen (der
    Feldfall) und dass ralph.sh die Ableitung nicht erneut selbst fuehrt (die
    Klasse). Ohne die zweite Haelfte kaeme die naechste Kopie ungehaertet
    zurueck, und der Test bliebe gruen.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import entrypoint_aufruf, kit_pfad, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]


def _entrypoint(name):
    for kandidat in (REPO_ROOT / name, REPO_ROOT / "bash" / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


RALPH = _entrypoint("ralph.sh")

pytestmark = [
    pytest.mark.skipif(RALPH is None, reason="ralph.sh nicht gefunden"),
    pytest.mark.nur_bash(
        "Die Fehlerklasse gibt es nur unter `set -euo pipefail`. ralph.ps1 hat "
        "sie nie gehabt, weil die pwsh-Bahn team_ralph_cap von Anfang an "
        "aufgerufen hat — genau das ist der Befund von BL-151."),
]

PLAN_MIT_CAP = """# Plan: Testkaskade

**Stufen:** 1
RALPH_CAP=1
BUDGET_EMPFEHLUNG_USD=5

## Stufe 1 — nichts
"""

PLAN_OHNE_CAP = """# Plan: Testkaskade

**Stufen:** 1

## Stufe 1 — nichts
"""


def _repo(tmp_path, plan_text):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "team" / "prompts").mkdir()
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "plans").mkdir()
    shutil.copy(kit_pfad("lib.sh"), repo / "team" / "lib.sh")
    shutil.copy(RALPH, repo / "ralph.sh")
    for werkzeug in ("beutebuch.py", "kosten.py"):
        shutil.copy(kit_pfad("tools", werkzeug), repo / "team" / "tools" / werkzeug)
    for briefing in (kit_pfad("prompts")).glob("*.md"):
        shutil.copy(briefing, repo / "team" / "prompts" / briefing.name)
    (repo / "team.config.sh").write_text(
        'TEAM_PROJEKT="fixture"\n'
        'TEAM_PRODUKTIVCODE="src/"\nTEAM_TEST_ORDNER="tests/"\n'
        'TEAM_PLAN_ORDNER="plans/"\n'
        'TEAM_BEUTEBUCH="plans/beutebuch.md"\n'
        'TEAM_ERMITTLUNGSAKTEN="plans/ermittlungsakten"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n'
        'TEAM_ROLE_BUDGET_USD="5"\nTEAM_ROLE_HARDCAP_USD="10"\n',
        encoding="utf-8")
    (repo / "plans" / "plan.md").write_text(plan_text, encoding="utf-8")
    (repo / ".ralph-plan").write_text("plans/plan.md\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo


def _lauf(repo):
    """Faehrt ralph.sh. Kein CLI-Stub noetig: Beide Fehlerlagen schlagen zu,
    BEVOR der erste Agentenaufruf faellig waere — das ist der Punkt."""
    env = dict(os.environ)
    env.update({"AUTH_MODE": "api", "ANTHROPIC_API_KEY": "sk-ant-dummy",
                "TEAM_LOCK_HELD": "1"})
    return subprocess.run(entrypoint_aufruf("./ralph.sh"), cwd=repo, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def test_plan_ohne_ralph_cap_nennt_den_grund(tmp_path):
    """Der Feldfall selbst. Nicht der Exit-Code ist der Befund — der war schon
    vorher 1 —, sondern dass der Mensch erfaehrt, WORAN es lag."""
    repo = _repo(tmp_path, PLAN_OHNE_CAP)
    (repo / ".ralph-state").write_text("1\n", encoding="utf-8")
    lauf = _lauf(repo)
    assert lauf.returncode == 1, \
        f"erwartet Exit 1, war {lauf.returncode}\nSTDERR:\n{lauf.stderr}"
    assert "RALPH_CAP" in lauf.stderr and "plans/plan.md" in lauf.stderr, (
        "ralph.sh ist ohne seine eigene Diagnose gestorben — genau BL-151. "
        "Der Mensch sieht dann nur 'Ralph endete mit Fehler (1)'.\n"
        f"STDERR war:\n{lauf.stderr}")


def test_fehlendes_ralph_state_nennt_den_grund(tmp_path):
    """Die zweite Stelle. Beim allerersten Start ist die fehlende Datei der
    NORMALFALL, nicht die Ausnahme."""
    repo = _repo(tmp_path, PLAN_MIT_CAP)
    assert not (repo / ".ralph-state").exists()
    lauf = _lauf(repo)
    assert lauf.returncode == 1, \
        f"erwartet Exit 1, war {lauf.returncode}\nSTDERR:\n{lauf.stderr}"
    assert "Stufennummer" in lauf.stderr, (
        "Die Klartextmeldung zum fehlenden .ralph-state ist toter Text — "
        "`head` hat den Loop vorher weggerissen (BL-151).\n"
        f"STDERR war:\n{lauf.stderr}")


def test_ralph_sh_leitet_den_cap_nicht_selbst_ab(tmp_path):
    """Die Klasse statt des Falls.

    Der Fehler war nicht das fehlende `|| true`, sondern die zweite Fassung
    derselben Ableitung. Faende jemand sie wieder daneben, waeren die beiden
    Tests oben noch eine Weile gruen — bis die naechste Haertung wieder nur
    an einer der beiden Stellen ankommt.
    """
    text = RALPH.read_text(encoding="utf-8-sig")
    code = "\n".join(z for z in text.splitlines()
                     if not z.lstrip().startswith("#"))
    assert "team_ralph_cap" in code, (
        "ralph.sh liest RALPH_CAP nicht ueber team_ralph_cap — die Lib-Funktion "
        "ist die einzige Quelle, ralph.ps1 macht es so (BL-151).")
    # Gesucht wird die ABLEITUNG, nicht der Name: `RALPH_CAP="$(…)"` und
    # `$RALPH_CAP` in einer Meldung sind richtig, eine zweite Suche nach der
    # Zeile im Plan ist es nicht.
    eigen = [z for z in code.splitlines()
             if "RALPH_CAP" in z
             and any(w in z for w in ("grep", "sed ", "awk", "cut "))]
    assert not eigen, (
        "In ralph.sh steht wieder eine eigene Ableitung von RALPH_CAP. Genau "
        "diese Doppelpflege war BL-151: Die Kopie bekam die BL-111-Haertung "
        "nicht mit.\n  " + "\n  ".join(z.strip() for z in eigen))

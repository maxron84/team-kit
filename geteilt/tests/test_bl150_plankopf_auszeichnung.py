#!/usr/bin/env python3
"""BL-150: Der Plankopf ist Markdown — die Leser lasen ihn wie Konfiguration.

DER FELDFALL
    Feld D, allererster Vollautomatik-Start. Der Architekt legte den Plankopf
    an als:

        **Plan:** Kaskade 1 — …
        **Stufen:** 1–5
        **RALPH_CAP=5**
        **BUDGET_EMPFEHLUNG_USD=18**

    Beide Bahnen ankerten auf `^\\s*RALPH_CAP=` — die fuehrenden `**`
    verhinderten den Treffer. Selbst BEI Treffer haette `cut -d= -f2` den
    ungueltigen Wert `5**` geliefert (die pwsh-Fassung faengt ihn mit `(.*)`
    genauso ein). Folgen: Ralph stieg mit Exit 1 aus, `team-status` zeigte
    `Cap ?`, und BUDGET_EMPFEHLUNG_USD waere nie in die Deckel-Anhebung der
    Vollautomatik eingegangen — ein Wert, den niemand vermisst, weil sein
    Fehlen wie ein bewusst niedriger Deckel aussieht.

DER FEHLER WAR EINGEBAUT, NICHT ZUFAELLIG
    `rolle-architekt.md` verlangte "die Zeilen `RALPH_CAP=<hoechste Stufe>` und
    `BUDGET_EMPFEHLUNG_USD=<zahl>` im Plankopf" — ohne ein Wort darueber, dass
    sie blank stehen muessen, waehrend der uebrige Plankopf (`**Plan:**`,
    `**Stufen:**`, `**Typ:**`) durchgehend fett ist. Ein Architekt, der sich
    exakt an sein Briefing haelt und dem Stil des eigenen Dokuments folgt,
    blockierte damit den Bau.

    Deshalb haelt dieser Test BEIDE Haelften des Fixes fest: dass die Leser
    Auszeichnung dulden (Klasse) und dass das Briefing die Blank-Pflicht
    ausspricht (Ursache). Nur zusammen wirken sie — eine geduldete Auszeichnung
    ohne Briefing-Satz laedt zum Weiterschreiben ein, ein Briefing-Satz ohne
    geduldenden Leser trifft den naechsten Architekten, der ihn ueberliest.

DAS ZEITFENSTER
    Wie bei BL-149 genau ein Plan pro Projekt: Sobald der erste Plankopf steht,
    wird seine Schreibweise abgeschrieben und der Fehler ist fuer immer
    unsichtbar. Getroffen wird die Situation mit der geringsten
    Projekterfahrung. Die Selbsttests bauen ihren Plankopf bisher selbst und
    immer blank — sie pruefen also genau den Fall nie, der im Feld eintritt.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import FangUndMelde, entrypoint_aufruf, kit_pfad, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]

PLAN = "plans/ralph-kaskade-7-thema.md"

# Die Schreibweisen, die ein Architekt tatsaechlich produziert. `fett` ist der
# Feldfall; die uebrigen sind dieselbe Klasse und kosten nichts extra.
NOTATIONEN = {
    "blank":      "RALPH_CAP={cap}\nBUDGET_EMPFEHLUNG_USD={budget}\n",
    "fett":       "**RALPH_CAP={cap}**\n**BUDGET_EMPFEHLUNG_USD={budget}**\n",
    "code":       "`RALPH_CAP={cap}`\n`BUDGET_EMPFEHLUNG_USD={budget}`\n",
    "liste":      "- RALPH_CAP={cap}\n- BUDGET_EMPFEHLUNG_USD={budget}\n",
    "liste_fett": "- **RALPH_CAP={cap}**\n- **BUDGET_EMPFEHLUNG_USD={budget}**\n",
}

KOPF = "**Plan:** Kaskade 7 — Thema\n**Typ:** Bau\n**Stufen:** 1–5\n"


def _repo(tmp_path, schale, plankopf):
    repo = tmp_path / "repo"
    (repo / "team").mkdir(parents=True)
    (repo / "plans").mkdir()
    shutil.copy(schale.kit_lib, repo / "team" / schale.lib_name)
    (repo / PLAN).write_text(KOPF + plankopf, encoding="utf-8")
    (repo / ".ralph-plan").write_text(PLAN + "\n", encoding="utf-8")
    return repo


def _lib(schale, repo):
    return repo / "team" / schale.lib_name


@pytest.mark.parametrize("notation", sorted(NOTATIONEN))
@pytest.mark.parametrize("funktion,erwartet", [
    ("team_ralph_cap", "5"),
    ("team_budget_empfehlung", "18"),
])
def test_ausgezeichneter_plankopf_wird_gelesen(tmp_path, schale, notation,
                                               funktion, erwartet):
    """Der Feldfall und seine Klasse. Unter voller Strenge gefahren, weil Ralph
    unter `set -euo pipefail` laeuft — das ist die Stufe, auf der es zaehlt."""
    repo = _repo(tmp_path, schale,
                 NOTATIONEN[notation].format(cap="5", budget="18"))
    ergebnis = schale.lauf(FangUndMelde(funktion), cwd=repo,
                           lib=_lib(schale, repo), strikt=True)
    assert ergebnis.returncode == 0, (
        f"{funktion} reisst den Aufrufer bei Notation '{notation}' weg:\n"
        f"{ergebnis.stderr}")
    assert f"rc=0 wert=[{erwartet}]" in ergebnis.stdout, (
        f"{funktion} liest den Plankopf in der Notation '{notation}' nicht — "
        f"genau BL-150. Ralph steigt dann mit Exit 1 aus, ohne dass jemand "
        f"sieht, warum.\n  gelesen: {ergebnis.stdout!r}")


def test_ohne_die_zeile_bleibt_es_leer_und_still(tmp_path, schale):
    """Die Gegenprobe zur Duldung: Ein Leser, der jetzt alles frisst, waere
    schlimmer als der strenge davor. Ein Plan OHNE die Zeile muss weiterhin
    leer und ohne Abbruch zurueckkommen (die Zusicherung aus BL-111)."""
    repo = _repo(tmp_path, schale, "**Stand:** noch nichts entschieden\n")
    for funktion in ("team_ralph_cap", "team_budget_empfehlung"):
        ergebnis = schale.lauf(FangUndMelde(funktion), cwd=repo,
                               lib=_lib(schale, repo), strikt=True)
        assert ergebnis.returncode == 0, ergebnis.stderr
        assert "rc=0 wert=[]" in ergebnis.stdout, (
            f"{funktion} meldet nicht mehr 'leer und still': "
            f"{ergebnis.stdout!r}")


def test_ein_wort_das_nur_so_endet_wird_nicht_gelesen(tmp_path, schale):
    """Die zweite Gegenprobe. Die Duldung darf den Anker nicht aufweichen —
    sonst liest der Parser Fliesstext, in dem die Zeile nur ERWAEHNT wird."""
    repo = _repo(tmp_path, schale,
                 "Der Architekt traegt hier RALPH_CAP=99 ein.\n"
                 "Siehe auch XRALPH_CAP=98.\n")
    ergebnis = schale.lauf(FangUndMelde("team_ralph_cap"), cwd=repo,
                           lib=_lib(schale, repo), strikt=True)
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "rc=0 wert=[]" in ergebnis.stdout, (
        "Ein blosser Prosa-Verweis wurde als Plankopf-Zeile gelesen — die "
        "Duldung hat den Anker mitgerissen.\n  gelesen: "
        f"{ergebnis.stdout!r}")


def test_das_briefing_verlangt_die_blanke_schreibweise():
    """Die Ursache, nicht die Folge.

    Der Fix an den Lesern allein liesse das Briefing stehen, das den Feldfall
    erzeugt hat — und die naechste Auszeichnungsform (etwa eine Tabellenzeile)
    faende wieder keinen Leser. Das Briefing ist die Stelle, an der die Regel
    ueberhaupt entsteht.
    """
    briefing = kit_pfad("prompts", "rolle-architekt.md")
    if not briefing.is_file():
        pytest.skip("rolle-architekt.md nicht in dieser Ablage")
    text = briefing.read_text(encoding="utf-8-sig")
    assert "BLANK" in text or "blank" in text, (
        "Das Architekten-Briefing sagt nichts ueber die Schreibweise der "
        "Plankopf-Zeilen — genau diese Luecke war BL-150.")
    kopf = text[text.find("RALPH_CAP"):]
    assert "```" in kopf, (
        "Das Briefing zeigt den Plankopf nicht als Block. Eine Regel ohne "
        "Muster wird nach dem Stil des umgebenden Dokuments ausgelegt — und "
        "der ist fett.")


# --------------------------------------------------------------- end-to-end
# Die Funktionstests oben messen den Leser. Der Feldfall war aber ein LAUF, und
# genau daran hat BL-113 gezeigt, dass die beiden nicht dasselbe sind. Hier
# faehrt der echte Entrypoint gegen einen fett gesetzten Plankopf.
#
# Kein CLI-Stub noetig, und das ist kein Kniff: .ralph-state steht UEBER dem
# Cap, also meldet Ralph "Feierabend" und endet mit 0, bevor ein Agent faellig
# waere. Das beweist beides auf einmal — die Zeile wurde gefunden UND als Zahl
# verstanden. Vor dem Fix stirbt derselbe Lauf mit Exit 1.


def _ralph():
    for kandidat in (REPO_ROOT / "ralph.sh", REPO_ROOT / "bash" / "entry" / "ralph.sh"):
        if kandidat.is_file():
            return kandidat
    return None


RALPH = _ralph()


def _projekt(tmp_path, plankopf):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "team" / "prompts").mkdir()
    (repo / "src").mkdir()
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
    (repo / PLAN).write_text(KOPF + plankopf, encoding="utf-8")
    (repo / ".ralph-plan").write_text(PLAN + "\n", encoding="utf-8")
    (repo / ".ralph-state").write_text("2\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo


@pytest.mark.nur_bash(
    "Faehrt den bash-Entrypoint. Das pwsh-Gegenstueck faehrt kit-test.ps1 "
    "im Trockenlauf, mit demselben fett gesetzten Plankopf (BL-150).")
@pytest.mark.skipif(RALPH is None, reason="ralph.sh nicht gefunden")
def test_ralph_startet_mit_fettem_plankopf(tmp_path):
    """Der Feldfall als Lauf: `**RALPH_CAP=1**` darf den Start nicht mehr
    blockieren."""
    repo = _projekt(tmp_path, "**RALPH_CAP=1**\n**BUDGET_EMPFEHLUNG_USD=18**\n")
    env = dict(os.environ)
    env.update({"AUTH_MODE": "api", "ANTHROPIC_API_KEY": "sk-ant-dummy",
                "TEAM_LOCK_HELD": "1"})
    lauf = subprocess.run(entrypoint_aufruf("./ralph.sh"), cwd=repo, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    assert lauf.returncode == 0, (
        "ralph.sh startet nicht gegen einen fett gesetzten Plankopf — genau "
        f"der Feldfall aus BL-150.\nSTDOUT:\n{lauf.stdout}\n"
        f"STDERR:\n{lauf.stderr}")
    assert "RALPH_CAP=1" in lauf.stdout, (
        "Der Cap wurde nicht als 1 gelesen. Erwartet war die "
        "Feierabend-Meldung, die den Wert nennt.\n"
        f"STDOUT:\n{lauf.stdout}")

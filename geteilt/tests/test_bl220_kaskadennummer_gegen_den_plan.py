#!/usr/bin/env python3
"""BL-220: `--rollen-abschluss` nahm jede Zahl als Kaskadennummer — eine
versehentlich uebergebene STUFENnummer buchte plausibel und falsch.

WAS IM FELD PASSIERT IST
    `Feld E`, elfte Kaskade. Fuer `<kaskade>` wurde der RALPH_CAP der Kaskade
    eingesetzt (59) statt der Kaskadennummer (11). Beide Zahlen stehen im
    Plankopf direkt untereinander, beide sind zweistellig, und die Bedienung
    nennt den Parameter nur `<kaskade>`.

    Es entstanden zwei Ledger-Zeilen (roles und ralph) mit `59` im
    Kaskadenfeld. Betraege korrekt, Summe korrekt, Auth korrekt — nur unter
    einer Kaskade, die es nicht gibt.

WARUM NICHTS ANSCHLUG
    Das Ledger blieb in sich stimmig, `--ledger-pruefen` lief ohne Befund zu
    dieser Sache, `--budget` zeigte eine plausible Summe. Aufgefallen ist es
    erst, als jemand `ledger --kaskade 11` rief und NICHTS zurueckbekam.

    Der Beweis kam vom Pruefer selbst: Nach der Handkorrektur (59 -> 11)
    meldete er sofort BEIDE echten Luecken. Sie waren die ganze Zeit wahr —
    unter `59` hat er zu Kaskade 11 vollstaendig geschwiegen, weil es zu
    Kaskade 11 nichts gab.

WARUM DIE PRUEFUNG NICHT AM ZAHLENFORMAT HAENGEN DARF
    Das Feld ist bewusst freitextfaehig: `vor-10` ist eine legitime benannte
    Kaskade fuer Out-of-Loop-Fixserien. Eine reine Zahlenpruefung haette
    diesen Fall nicht gefangen (59 IST eine gueltige Zahl) und die benannten
    Kaskaden kaputtgemacht. Geprueft wird deshalb gegen `.ralph-plan` — die
    Quelle, die `architekt-abschluss` ohnehin schon liest —, und NUR bei einer
    rein numerischen Uebergabe.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      verlange_pwsh, werkzeug_wert)

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _repo(tmp_path, plan_nummer="11"):
    """Minimalprojekt mit scharfgeschalteter Kaskade: Plandatei committet,
    `.ralph-plan` zeigt darauf, ein frisches Log liegt im .team-logs."""
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"]):
        subprocess.run(["git", "-C", str(tmp_path), *befehl], check=True,
                       capture_output=True)
    (tmp_path / "plans").mkdir()
    plan = tmp_path / "plans" / f"ralph-kaskade-{plan_nummer}-produkt.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "scharf"],
                   check=True, capture_output=True)
    (tmp_path / ".ralph-plan").write_text(
        f"plans/ralph-kaskade-{plan_nummer}-produkt.md\n", encoding="utf-8")
    (tmp_path / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    logs = tmp_path / ".team-logs"
    logs.mkdir()
    (logs / "frank.json").write_text(json.dumps({"total_cost_usd": 3.7260}),
                                     encoding="utf-8")
    return tmp_path


def _buche(repo, *zusatz, kaskade="59"):
    return subprocess.run(
        [sys.executable, str(KOSTEN_PY), "rollen-abschluss",
         "--kaskade", kaskade, "--domaene", "produkt",
         "--logs", str(repo / ".team-logs"),
         "--pfad", str(repo / ".budget-ledger"), "--repo", str(repo), *zusatz],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))


def _rollenzeilen(repo):
    return [z for z in kosten.ledger_zeilen(str(repo / ".budget-ledger"))
            if z["rolle"] == "roles"]


# --- Der Fall aus dem Feld ---------------------------------------------------

def test_stufennummer_statt_kaskadennummer_bricht_ab(tmp_path):
    repo = _repo(tmp_path, plan_nummer="11")
    r = _buche(repo, kaskade="59")
    assert r.returncode != 0, (
        "BL-220 ist zurueck: Die Stufennummer wurde anstandslos gebucht. "
        f"stdout={r.stdout}")
    assert not _rollenzeilen(repo), \
        "eine abgebrochene Buchung darf keine Zeile hinterlassen"


def test_die_meldung_nennt_BEIDE_zahlen(tmp_path):
    """Ohne beide Zahlen ist die Meldung nicht handhabbar — der Bediener
    glaubt die Nummer ja zu kennen, sonst haette er sie nicht getippt."""
    repo = _repo(tmp_path, plan_nummer="11")
    r = _buche(repo, kaskade="59")
    assert "11" in r.stderr and "59" in r.stderr, r.stderr
    assert "--trotzdem" in r.stderr, \
        "die Meldung muss den Weg heraus nennen, nicht nur das Problem"


def test_trotzdem_erzwingt_die_buchung(tmp_path):
    """Die Gegenrichtung: Ein Riegel ohne benannte Uebersteuerung ist eine
    Sackgasse — es gibt legitime Faelle (Nachbuchung einer alten Kaskade)."""
    repo = _repo(tmp_path, plan_nummer="11")
    r = _buche(repo, "--trotzdem", kaskade="59")
    assert r.returncode == 0, r.stderr
    zeilen = _rollenzeilen(repo)
    assert len(zeilen) == 1 and zeilen[0]["kaskade"] == "59"


# --- Die drei Gegenproben: kein Fehlalarm -------------------------------------

def test_passende_nummer_bucht_ohne_murren(tmp_path):
    repo = _repo(tmp_path, plan_nummer="11")
    r = _buche(repo, kaskade="11")
    assert r.returncode == 0, r.stderr
    assert len(_rollenzeilen(repo)) == 1


def test_benannte_kaskade_wird_nie_gegen_den_plan_gehalten(tmp_path):
    """`vor-10` ist der dokumentierte Weg fuer Out-of-Loop-Runden (BL-45).
    Wer ihn tippt, meint ihn — eine Rueckfrage waere hier der Fehlalarm, vor
    dem BL-14 warnt."""
    repo = _repo(tmp_path, plan_nummer="11")
    r = _buche(repo, kaskade="vor-10")
    assert r.returncode == 0, r.stderr
    zeilen = _rollenzeilen(repo)
    assert len(zeilen) == 1 and zeilen[0]["kaskade"] == "vor-10"


def test_ohne_plan_zeiger_wird_nicht_geraten(tmp_path):
    """Fehlt `.ralph-plan` oder passt sein Muster nicht, gibt es keine zweite
    Quelle — dann wird gebucht statt gewarnt. Ein Werkzeug, das bei fehlender
    Information warnt, warnt immer."""
    repo = _repo(tmp_path, plan_nummer="11")
    (repo / ".ralph-plan").unlink()
    r = _buche(repo, kaskade="59")
    assert r.returncode == 0, r.stderr
    assert len(_rollenzeilen(repo)) == 1


def test_ralph_abschluss_traegt_denselben_riegel(tmp_path):
    """Die Bedienhandlung ruft BEIDE Verben. Ein Riegel, der nur an einem
    haengt, laesst die Haelfte der Fehlbuchung durch (Bauart BL-4)."""
    repo = _repo(tmp_path, plan_nummer="11")
    (repo / ".ralph-logs").mkdir()
    (repo / ".ralph-logs" / "stufe-59.json").write_text(
        json.dumps({"total_cost_usd": 1.0}), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(KOSTEN_PY), "ralph-abschluss",
         "--kaskade", "59", "--domaene", "produkt",
         "--logs", str(repo / ".ralph-logs"),
         "--pfad", str(repo / ".budget-ledger"), "--repo", str(repo)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))
    assert r.returncode != 0, r.stdout
    assert not list(kosten.ledger_zeilen(str(repo / ".budget-ledger")))


# --- Die Durchreiche, ohne die der Fix nicht ankommt (Lehre aus BL-143) -------

def _fixture_bahn(tmp_path, bahn):
    repo = _repo(tmp_path, plan_nummer="11")
    (repo / "team" / "tools").mkdir(parents=True)
    shutil.copy(kit_pfad("tools", "kosten.py"),
                repo / "team" / "tools" / "kosten.py")
    if bahn == "bash":
        shutil.copy(entrypoint_pfad("team-status.sh"), repo / "team-status.sh")
        shutil.copy(kit_pfad("lib.sh"), repo / "team" / "lib.sh")
        (repo / "team.config.sh").write_text(
            'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n', encoding="utf-8")
    else:
        shutil.copy(entrypoint_pfad("team-status.ps1"), repo / "team-status.ps1")
        shutil.copy(kit_pfad("lib.psm1"), repo / "team" / "lib.psm1")
        # BL-113/BL-134: PowerShell-Quelltext traegt ein BOM, auch als Fixture.
        (repo / "team.config.ps1").write_text(
            '$TEAM_BEUTEBUCH_TOOL = "' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            '$TEAM_KOSTEN_TOOL = "' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            '$TEAM_DOMAENEN = "produkt"\n', encoding="utf-8-sig")
    return repo


def _pruefe_wrapper(repo, r_ohne, r_mit):
    assert r_ohne.returncode != 0, (
        "der Wrapper hat den Riegel nicht erreicht — er ruft kosten.py mit "
        f"einer Nummer, die der Plan nicht kennt.\n{r_ohne.stdout}{r_ohne.stderr}")
    assert r_mit.returncode == 0, (
        "`--trotzdem` ist unterwegs verlorengegangen. Ein Schalter, den der "
        "Alias erbt, aber der Wrapper wegwirft, ist der Fehler aus BL-143.\n"
        f"{r_mit.stdout}{r_mit.stderr}")
    zeilen = [z for z in kosten.ledger_zeilen(str(repo / ".budget-ledger"))
              if z["kaskade"] == "59"]
    assert zeilen, "nach --trotzdem muss die Zeile unter 59 stehen"


def test_bash_wrapper_reicht_trotzdem_durch(tmp_path):
    verlange_bash()
    repo = _fixture_bahn(tmp_path, "bash")
    ohne = subprocess.run(
        [BASH, "./team-status.sh", "--rollen-abschluss", "59", "produkt"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    mit = subprocess.run(
        [BASH, "./team-status.sh", "--rollen-abschluss", "59", "produkt",
         "Rollen", "Bau", "--trotzdem"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    _pruefe_wrapper(repo, ohne, mit)


def test_pwsh_wrapper_reicht_trotzdem_durch(tmp_path):
    verlange_pwsh()
    repo = _fixture_bahn(tmp_path, "pwsh")
    ohne = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./team-status.ps1",
         "--rollen-abschluss", "59", "produkt"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    mit = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./team-status.ps1",
         "--rollen-abschluss", "59", "produkt", "Rollen", "Bau", "--trotzdem"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    _pruefe_wrapper(repo, ohne, mit)


# --- Die Bedienung darf die Zweideutigkeit nicht mehr verschweigen -----------

@pytest.mark.parametrize("datei", ["team-status.sh", "team-status.ps1"])
def test_nutzungszeile_nennt_die_verwechslung(datei):
    """Der billigste Teil des Fixes, und der einzige, der auch dort wirkt, wo
    kein `.ralph-plan` liegt: Der Parameter heisst nicht mehr blank
    `<kaskade>`.

    Fehlt die Datei, wird UEBERSPRUNGEN statt rot: In einer einbahnig
    installierten Ablage (`--nur-bash`/`--nur-pwsh`) gibt es das Gegenstueck
    nicht, und ein roter Fall dort beweist nichts ueber das Kit — genau der
    Ausrutscher, vor dem der Backlog-Kopf warnt.
    """
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht (einbahnig installiert)")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "NICHT stufe" in text, (
        f"{datei} nennt den Parameter weiter nur `<kaskade>` — genau die "
        "Zweideutigkeit, an der BL-220 haengt")

#!/usr/bin/env python3
"""BL-256: Nichts hielt fest, dass das Gate AUS ist — ein Lauf meldete sich als
fertig, waehrend der Baum seit einer Stunde rot war, und jede beteiligte Rolle
hatte sich regelkonform verhalten.

WAS IM FELD PASSIERT IST
    Ein KORREKTER Frank-Fix aktivierte einen latenten Defekt in einem aelteren
    Waechter. Frank trug den Beifang als eigenen Fund ein (Finder != Fixer),
    klebte den fremden Test NICHT mit einer Marke zu und belegte regelkonform,
    dass SEIN Fix keinen NEUEN Fehlschlag erzeugt (`BL-205`). Der Fund bekam
    Status `offen`; die Fixphase fragt nach `an Frank uebergeben` und meldete
    folgerichtig *nichts zu tun*. Die zwei folgenden Frank-Laeufe massen
    denselben roten Baum gegen denselben roten Ausgangszustand und kamen
    jeweils korrekt zu dem Schluss, nichts verschlimmert zu haben.

    **Der Abschlussbericht meldete den Lauf als fertig.** Der Regelapparat
    funktioniert wie gebaut, und das Ergebnis ist trotzdem falsch.

DIE STRUKTURELLE URSACHE
    Jede Rolle misst den Suitenstand einzeln und KEINE gibt ihn weiter. Es gibt
    keinen Ort, an dem *das Gate ist seit HH:MM rot* stehen koennte — also kann
    keine Zusammenfassung ihn lesen.

WAS BEWUSST NICHT GEAENDERT WIRD
    Die Regel *ein Fix scheitert nicht an fremdem Flackern* (`BL-205`) ist
    richtig und wird NICHT zurueckgedreht. Was fehlte, ist ihre
    Gegenrichtung: Der Lauf darf weiterlaufen — er darf sich nur nicht als
    fertig melden.

WARUM DIE FUND-EBENE NICHT REICHT
    Ein rotes Gate kann ohne Fundeintrag entstehen, und ein offener Fund heisst
    umgekehrt nicht, dass die Suite rot ist. Der Suitenstand gehoert an den
    Suitenstand gebunden — deshalb eine eigene Datei und nicht das Beutebuch.

WAS DIESER TEST PRUEFT
    Beide Richtungen am VERHALTEN des Orchestrators: Eine belegte Gate-Datei
    macht aus dem Abschluss einen eigenen Ausgang (Exit 44), eine leere oder
    fehlende laesst den Lauf unveraendert. Dazu die Schreibseite — die Rollen
    erfahren im Prompt, dass und wohin sie schreiben sollen.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      werkzeug_wert)

WURZEL = Path(__file__).resolve().parents[2]

BIBLIOTHEKEN = ("bash/lib.sh", "pwsh/lib.psm1")
VOLLAUTOMATIK = {"bash": "bash/entry/vollautomatik.sh",
                 "pwsh": "pwsh/entry/vollautomatik.ps1"}
GATE = ".team-gate-rot"
ROLLEN = ("ralph", "harry", "marv", "frank", "axel", "team-status")


def _quelle(rel):
    pfad = WURZEL / rel
    if not pfad.is_file():
        pytest.skip(f"{rel} liegt in dieser Ablage nicht")
    return pfad.read_text(encoding="utf-8")


# --- (1) Die Schreibseite: die Rollen erfahren es im Prompt ------------------

@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_die_bauende_rolle_wird_zum_schreiben_aufgefordert(rel):
    """Die Messung liegt ohnehin vor — es ist ein zusaetzliches SCHREIBEN,
    keine zusaetzliche Messung."""
    text = _quelle(rel)
    assert "BL-256" in text, (
        f"{rel}: Keine Rolle erfaehrt, dass ein vorher roter Baum irgendwo "
        "festgehalten gehoert (BL-256).")
    assert "VOR deiner Arbeit rot" in text, (
        f"{rel}: Die Auflage nennt den Fall nicht, fuer den sie gebaut ist.")


@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_auch_frank_schreibt(rel):
    """Frank ist der Fall aus dem Feld — er misst beide Staende ohnehin
    (BL-205) und war der Einzige, der den roten Baum gesehen hat."""
    text = _quelle(rel)
    zeile = [z for z in text.splitlines() if "BL-205" in z and "SMOKE_SUFFIX" in z]
    assert zeile, f"{rel}: die gefuellte SMOKE_SUFFIX-Zeile ist nicht zu finden"
    assert "BL-256" in zeile[0], (
        f"{rel}: Frank misst den vorher roten Baum, haelt ihn aber nirgends "
        "fest — genau der Fall aus dem Feld (BL-256).")


@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_die_regel_aus_bl205_bleibt_stehen(rel):
    """Die Gegenrichtung, und sie ist die wichtigere: Ein Fix darf weiterhin
    nicht an fremdem Flackern scheitern."""
    text = _quelle(rel)
    assert "brich nicht ab" in text, (
        f"{rel}: Die Regel aus BL-205 ist verschwunden — BL-256 sollte ihre "
        "Gegenrichtung ergaenzen, nicht sie ersetzen.")


@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_das_loeschen_steht_daneben(rel):
    """Richtung (3): Meldet eine spaetere Rolle gruen, wird die Datei geleert.
    Ohne das bliebe ein einmal rotes Gate fuer immer rot."""
    text = _quelle(rel)
    assert "lösche die Datei" in text or "loesche die Datei" in text, (
        f"{rel}: Nichts sagt, wann die Gate-Datei wieder weggehoert (BL-256).")


def test_die_gate_datei_steht_in_der_gitignore_vorlage():
    text = _quelle("bootstrap/gitignore.fragment")
    assert GATE in text, (
        "Die Vorlage ignoriert die Gate-Datei nicht — ab der ersten Meldung "
        "ist der Arbeitsbaum dreckig und der Guard warnt bei jedem Rollenstart "
        "(BL-233/BL-256).")


@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_die_gate_datei_ist_definiert_bevor_der_prompt_sie_nennt(rel):
    """Beim Bauen von BL-256 selbst passiert — und die zwei Bahnen verhalten
    sich dabei GEGENSAETZLICH.

    Der Prompt-Baustein nennt `TEAM_GATE_DATEI`; definiert war sie zunaechst
    weiter unten bei den Funktionen. Auf der bash-Bahn faellt das sofort auf:
    `set -u` macht daraus ein `unbound variable`, elf Faelle wurden rot. Auf der
    pwsh-Bahn waere es STILL geblieben — PowerShell interpoliert eine
    undefinierte Variable als Leerstring, und die Rolle haette gelesen
    *haenge eine Zeile ... an  an*: eine Auflage ohne Ziel, in jedem Prompt,
    ohne einen einzigen roten Test.

    Das ist `BL-229` in neuer Gestalt — nicht ein Fix, der die andere Bahn
    totlegt, sondern einer, der auf der anderen Bahn LAUTLOS halb wirkt.
    Geprueft wird deshalb die Reihenfolge, nicht das Ergebnis.
    """
    text = _quelle(rel)
    definition = min((text.index(m) for m in
                      ('TEAM_GATE_DATEI="${TEAM_GATE_DATEI',
                       "$TEAM_GATE_DATEI = Team-Default")
                      if m in text), default=None)
    assert definition is not None, (
        f"{rel}: Die Gate-Datei setzt ihren Default nicht in der greppbaren "
        "Form (Vertrag Punkt 6 in conftest.py).")
    nennungen = [i for i in range(len(text))
                 if text.startswith("TEAM_GATE_DATEI", i)
                 and i != definition and not text.startswith(
                     "TEAM_GATE_DATEI=", i)]
    erste_nennung = min((i for i in nennungen if i > 0), default=None)
    assert erste_nennung is None or erste_nennung > definition, (
        f"{rel}: Die Gate-Datei wird benutzt, bevor sie definiert ist. Auf der "
        "bash-Bahn ist das ein Abbruch unter `set -u`, auf der pwsh-Bahn ein "
        "stiller Leerstring — eine Auflage ohne Ziel (BL-256).")


# --- (2) Die Leseseite, am Verhalten -----------------------------------------

def _projekt(tmp_path):
    """Minimalprojekt mit Stub-Rollen — dieselbe Bauform wie in BL-217.
    Geprueft wird der Orchestrator, nicht die Rollen."""
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"]):
        subprocess.run(["git", "-C", str(tmp_path), *befehl], check=True,
                       capture_output=True)
    (tmp_path / "team" / "tools").mkdir(parents=True)
    (tmp_path / "plans").mkdir()
    (tmp_path / ".ralph-logs").mkdir()
    (tmp_path / ".team-logs").mkdir()
    shutil.copy(kit_pfad("lib.sh"), tmp_path / "team" / "lib.sh")
    for werkzeug in ("kosten.py", "beutebuch.py"):
        shutil.copy(kit_pfad("tools", werkzeug),
                    tmp_path / "team" / "tools" / werkzeug)
    shutil.copy(entrypoint_pfad("vollautomatik.sh"),
                tmp_path / "vollautomatik.sh")
    (tmp_path / "team.config.sh").write_text(
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n', encoding="utf-8")
    for rolle in ROLLEN:
        code = 3 if rolle in ("harry", "marv", "frank") else 0
        pfad = tmp_path / f"{rolle}.sh"
        pfad.write_text(f'#!/usr/bin/env bash\necho "STUB {rolle}"\nexit {code}\n',
                        encoding="utf-8")
        pfad.chmod(0o755)
    (tmp_path / ".ralph-plan").write_text("plans/ralph-kaskade-1-produkt.md\n",
                                          encoding="utf-8")
    (tmp_path / ".ralph-state").write_text("5\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "init"],
                   check=True, capture_output=True)
    return tmp_path


def _lauf(repo):
    return subprocess.run([BASH, "./vollautomatik.sh"], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace",
                          env=dict(os.environ, TEAM_BUDGET_USD="99"))


def test_ein_belegtes_gate_beendet_den_lauf_mit_eigenem_ausgang(tmp_path):
    """Der Fall aus dem Feld: Alles gelaufen, Baum rot, Bericht meldet fertig."""
    verlange_bash()
    repo = _projekt(tmp_path)
    (repo / GATE).write_text(
        "2026-09-10T14:03:00 | frank | test_alt_waechter, test_alt_zweitens\n",
        encoding="utf-8")
    ergebnis = _lauf(repo)
    assert ergebnis.returncode == 44, (
        "Ein Lauf mit rotem Gate meldet sich weiter als fertig "
        f"(Exit {ergebnis.returncode}) — genau der Fall aus dem Feld "
        f"(BL-256).\n{ergebnis.stdout}\n{ergebnis.stderr}")
    assert "GATE ROT" in ergebnis.stdout, ergebnis.stdout
    assert "14:03" in ergebnis.stdout, (
        "Der Bericht nennt den Zeitpunkt nicht — *seit wann* ist die halbe "
        f"Aussage.\n{ergebnis.stdout}")
    assert "test_alt_waechter" in ergebnis.stdout, (
        "Die Namen der roten Tests fehlen — ohne sie beginnt die Reparatur "
        f"mit einer Suche.\n{ergebnis.stdout}")


def test_ohne_gate_datei_bleibt_alles_wie_es_war(tmp_path):
    """Gegenrichtung: Eine Meldung, die immer kommt, ist keine (BL-14)."""
    verlange_bash()
    repo = _projekt(tmp_path)
    ergebnis = _lauf(repo)
    assert ergebnis.returncode == 0, (
        f"Der Normalfall endet nicht mehr sauber:\n{ergebnis.stdout}\n"
        f"{ergebnis.stderr}")
    assert "GATE ROT" not in ergebnis.stdout, ergebnis.stdout
    assert "Vollautomatik beendet." in ergebnis.stdout


def test_eine_geleerte_gate_datei_zaehlt_nicht(tmp_path):
    """Richtung (3): Meldet eine spaetere Rolle gruen, wird die Datei geleert —
    und eine geleerte Datei darf den Lauf nicht weiter rot faerben."""
    verlange_bash()
    repo = _projekt(tmp_path)
    (repo / GATE).write_text("", encoding="utf-8")
    ergebnis = _lauf(repo)
    assert ergebnis.returncode == 0, (
        "Eine geleerte Gate-Datei haelt den Lauf weiter an — dann kann ihn "
        f"niemand wieder gruen bekommen (BL-256).\n{ergebnis.stdout}")
    assert "GATE ROT" not in ergebnis.stdout


def test_der_bericht_kommt_trotzdem(tmp_path):
    """Der Ausgang ersetzt den Abschlussbericht NICHT — wer das Gate repariert,
    braucht die Zahlen des Laufs genauso."""
    verlange_bash()
    repo = _projekt(tmp_path)
    (repo / GATE).write_text("2026-09-10T14:03:00 | frank | test_alt\n",
                             encoding="utf-8")
    ergebnis = _lauf(repo)
    assert "=== ABSCHLUSSBERICHT ===" in ergebnis.stdout, (
        "Der Gate-Ausgang hat den Bericht verschluckt — dann kostet die "
        f"Diagnose einen zweiten Lauf.\n{ergebnis.stdout}")


# --- (3) Beide Bahnen --------------------------------------------------------

@pytest.mark.parametrize("bahn", sorted(VOLLAUTOMATIK))
def test_beide_orchestratoren_lesen_das_gate(bahn):
    text = _quelle(VOLLAUTOMATIK[bahn])
    assert "team_gate_rot_seit" in text, (
        f"{VOLLAUTOMATIK[bahn]} liest die Gate-Datei nicht (BL-256).")
    assert "exit 44" in text, (
        f"{VOLLAUTOMATIK[bahn]} endet nicht mit eigenem Code — dann ist der "
        "Fall von einem sauberen Abschluss nicht zu unterscheiden (BL-256).")


def test_beide_bahnen_sagen_dasselbe():
    bash, pwsh = _quelle(VOLLAUTOMATIK["bash"]), _quelle(VOLLAUTOMATIK["pwsh"])
    for merkmal in ("team_gate_rot_seit", "GATE ROT", "exit 44", "BL-256"):
        assert (merkmal in bash) == (merkmal in pwsh), (
            f"'{merkmal}' steht nur auf einer Bahn (BL-229).")

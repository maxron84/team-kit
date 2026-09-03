#!/usr/bin/env python3
"""BL-217: Der Orchestrator nahm nach einem Abbruch nicht die abgebrochene
Phase auf, sondern fing die Phasenkette von vorn an — und der Abbruchbericht
versprach woertlich das Gegenteil.

WAS IM FELD PASSIERT IST
    `Feld E`, Abbruch in Phase 4 am Pro-Lauf-Deckel. Der Bericht bot an:
    „Ganzen Lauf fortsetzen: ./vollautomatik.sh (nimmt den Faden am
    Zeigerstand auf)". Einen Zeiger gab es nur fuer Ralph (`.ralph-state`);
    fuer die PHASENKETTE gab es keinen. Der Fortsetzungslauf begann bei
    Phase 1 und kaufte **zwei volle Red-Team-Sweeps ueber Franks eigene
    Fix-Commits** — seit dem letzten Sweep lagen neue Commits vor, also hatten
    Harry und Marv „etwas zu tun".

    Nachgemessen im Closeout desselben Tages: **2,2653 USD, null Funde** —
    **27 %** der gesamten Fixphasen-Kosten dieser Kaskade (8,3047 USD). Die
    Restarbeit, wegen der fortgesetzt wurde, war eine leere Frank-Runde und
    der Abschlussbericht, beides kostenlos.

    Verschaerfend: Der Fortsetzungslauf setzt `LAUF_START` neu (fuer sich
    richtig, `BL-18`) — das ganze frische Budget kann in einen Sweep laufen,
    den niemand bestellt hat, und die Fixphase steht danach vor demselben
    Deckel wie vorher.

WARUM DAS EINE ZUSAGE-FRAGE IST, NICHT NUR EINE KOSTENFRAGE
    Der Mensch handelt nach der Zusage, nicht nach dem Code — dieselbe Bauart
    wie ein Smoke-Test, der gruen meldet, weil er sich die Umgebung passend
    setzt. Betroffen war JEDER Abbruchpfad, der den Weiterweg anbietet:
    Budget-Deckel, Stagnation (Exit 1), Session-Pause (Exit 42).

WAS HIER GEPRUEFT WIRD
    Nicht nur der Text, sondern das VERHALTEN: Der Orchestrator laeuft gegen
    Stub-Rollen, wird in Phase 4 abgebrochen und muss beim zweiten Aufruf dort
    weitermachen. Dazu die drei Gegenproben, ohne die der Zeiger gefaehrlich
    waere — ein veralteter Zeiger darf **niemals** einen Bau ueberspringen.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      werkzeug_wert)

REPO_ROOT = Path(__file__).resolve().parents[2]
ROLLEN = ("ralph", "harry", "marv", "frank", "axel", "team-status")


def _projekt(tmp_path, frank_exit=3):
    """Minimalprojekt mit Stub-Rollen. Die Rollen kosten hier nichts und
    liefern feste Exit-Codes — geprueft wird der Orchestrator, nicht sie."""
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
    # BL-130: kein blankes `python3` im Fixture — unter Windows ist das der
    # Store-Alias. werkzeug_wert() setzt den Interpreter dieses Wirts ein.
    (tmp_path / "team.config.sh").write_text(
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n', encoding="utf-8")
    for rolle in ROLLEN:
        code = frank_exit if rolle == "frank" else (3 if rolle in ("harry", "marv") else 0)
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


def _frank(repo, exit_code):
    (repo / "frank.sh").write_text(
        f'#!/usr/bin/env bash\necho "STUB frank"\nexit {exit_code}\n',
        encoding="utf-8")
    (repo / "frank.sh").chmod(0o755)


def _lauf(repo, *args):
    return subprocess.run([BASH, "./vollautomatik.sh", *args], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace",
                          env=dict(os.environ, TEAM_BUDGET_USD="99"))


STATE = ".vollautomatik-state"


# --- Der Fall aus dem Feld ---------------------------------------------------

def test_ein_abbruch_in_phase_4_wird_bei_phase_4_fortgesetzt(tmp_path):
    verlange_bash()
    repo = _projekt(tmp_path)
    _frank(repo, 42)                       # Session-Limit mitten in Phase 4
    erst = _lauf(repo)
    assert erst.returncode == 42, erst.stdout + erst.stderr
    assert (repo / STATE).is_file(), \
        "der Zeiger muss den Abbruch ueberleben — sonst gibt es nichts aufzunehmen"

    _frank(repo, 3)
    zweit = _lauf(repo)
    assert zweit.returncode == 0, zweit.stdout + zweit.stderr
    assert "Faden aufgenommen bei Phase 4" in zweit.stdout, zweit.stdout
    assert "=== PHASE Red Team: harry ===" not in zweit.stdout, (
        "BL-217 ist zurueck: Der Fortsetzungslauf kauft wieder einen "
        f"Red-Team-Sweep ueber Franks eigene Fix-Commits.\n{zweit.stdout}")
    assert "=== PHASE Red Team: marv ===" not in zweit.stdout
    assert "STUB ralph" not in zweit.stdout


def test_der_zeiger_faellt_am_regulaeren_ende_weg(tmp_path):
    """Sonst wuerde der naechste Aufruf dauerhaft bei Phase 4 einsteigen und
    nie wieder bauen — der Zeiger ueberlebt genau die Abbrueche."""
    verlange_bash()
    repo = _projekt(tmp_path)
    ergebnis = _lauf(repo)
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    assert not (repo / STATE).exists()


# --- Die drei Gegenproben, ohne die der Zeiger gefaehrlich waere -------------

def test_ein_veralteter_zeiger_ueberspringt_keinen_bau(tmp_path):
    """DIE wichtigste Gegenprobe. Aendert sich der Stufenstand (neue Kaskade,
    von Hand gefahrener Ralph), ist der Zeiger wertlos — und ein wertloser
    Zeiger, der eine Bauphase ueberspringt, waere teurer als der Fund."""
    verlange_bash()
    repo = _projekt(tmp_path)
    _frank(repo, 42)
    _lauf(repo)
    (repo / ".ralph-state").write_text("6\n", encoding="utf-8")

    _frank(repo, 3)
    zweit = _lauf(repo)
    assert "Phasen-Zeiger verworfen" in zweit.stdout, zweit.stdout
    assert "STUB ralph" in zweit.stdout, \
        "nach einem verworfenen Zeiger muss wieder bei Phase 1 begonnen werden"
    assert "=== PHASE Red Team: harry ===" in zweit.stdout


def test_ein_umgelegter_plan_verwirft_den_zeiger_ebenso(tmp_path):
    verlange_bash()
    repo = _projekt(tmp_path)
    _frank(repo, 42)
    _lauf(repo)
    (repo / ".ralph-plan").write_text("plans/ralph-kaskade-2-produkt.md\n",
                                      encoding="utf-8")

    _frank(repo, 3)
    zweit = _lauf(repo)
    assert "Phasen-Zeiger verworfen" in zweit.stdout, zweit.stdout
    assert "STUB ralph" in zweit.stdout


def test_von_vorn_erzwingt_die_ganze_kette(tmp_path):
    """Der benannte Weg zurueck auf Anfang — fuer den Fall, dass der Mensch
    die Sweeps ausdruecklich will."""
    verlange_bash()
    repo = _projekt(tmp_path)
    _frank(repo, 42)
    _lauf(repo)

    _frank(repo, 3)
    zweit = _lauf(repo, "--von-vorn")
    assert "--von-vorn" in zweit.stdout and "verworfen" in zweit.stdout
    assert "STUB ralph" in zweit.stdout
    assert "=== PHASE Red Team: harry ===" in zweit.stdout


def test_eine_unbekannte_option_endet_rot(tmp_path):
    """Dieselbe Lehre wie BL-222, gleich mitgenommen: Ein neuer Schalter darf
    keinen stillen Nachbarn erzeugen, der wie ein normaler Lauf aussieht."""
    verlange_bash()
    repo = _projekt(tmp_path)
    ergebnis = _lauf(repo, "--quatsch")
    assert ergebnis.returncode == 2, ergebnis.stdout + ergebnis.stderr
    assert "STUB ralph" not in ergebnis.stdout


# --- Die falsche Zusage, die den Fund ausgeloest hat -------------------------

@pytest.mark.parametrize("datei", ["vollautomatik.sh", "vollautomatik.ps1"])
def test_der_abbruchbericht_verspricht_keinen_zeigerstand_mehr(datei):
    """Der Satz „nimmt den Faden am Zeigerstand auf" beschrieb eine Semantik,
    die es nicht gab. Fehlt die Datei (einbahnige Ablage), wird
    uebersprungen statt rot."""
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht (einbahnig installiert)")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "nimmt den Faden am Zeigerstand auf" not in text, (
        f"{datei} verspricht weiter eine Semantik, die an nichts haengt")
    assert "vollautomatik-state" in text, \
        f"{datei} fuehrt keinen Phasen-Zeiger (BL-217)"
    assert "--von-vorn" in text, \
        f"{datei} kennt keinen benannten Weg zurueck auf Phase 1"


def test_der_zeiger_ist_gitignoriert():
    """Er entsteht WAEHREND eines Laufs im Arbeitsbaum. Ohne diesen Eintrag
    liefe er in denselben Fall wie BL-206 (Befund 2): ein Pfad, den es beim
    Rollenstart nicht gab."""
    fragment = (REPO_ROOT / "bootstrap" / "gitignore.fragment")
    if not fragment.is_file():
        pytest.skip("gitignore.fragment liegt in dieser Ablage nicht")
    assert ".vollautomatik-state" in fragment.read_text(encoding="utf-8")

#!/usr/bin/env python3
"""BL-210/BL-212/BL-214: Drei Meldungen aus `Feld B`, die alle dasselbe tun —
sie lassen einen Lauf wie einen sauberen Abschluss aussehen, der keiner war.

BL-210 — EIN UNBRAUCHBARER FUND AM KOPF DER WARTESCHLANGE BEENDET DIE FIXPHASE
    `frank.*` holt seinen Auftrag ueber `beutebuch first <status>` — das
    liefert IMMER den ersten Treffer der Datei. Faellt der Lint darauf durch,
    endete die Rolle mit `exit 3`. Denselben Code benutzt sie fuer "nichts zu
    tun", und die Schleife der Vollautomatik konnte beide nicht trennen: Sie
    brach ab und meldete "nichts mehr zu tun".

    Im Feld blieb dahinter ein formal einwandfreier zweiter Fund liegen, der
    sofort fixbar gewesen waere. Er wurde nie betrachtet — und beim naechsten
    Lauf wieder nicht, denn `first` liefert erneut denselben defekten Kopf.
    Waere er kritisch gewesen, haette der Lauf einen kritischen Fund
    stillschweigend uebersprungen und trotzdem "Fix-Phase beendet" gemeldet.

BL-212 — DER ABBRUCHBERICHT SCHLAEGT DEN CLOSEOUT EINER UNGEPRUEFTEN KASKADE VOR
    Faellt der Pro-Lauf-Deckel zwischen Ralphs Feierabend und der Red-Team-
    Phase, ist das Beutebuch leer — WEIL niemand gesucht hat. Der Bericht las
    das als "keine offenen Funde" und schlug den Closeout vor. Das Feld ist dem
    Rat NICHT gefolgt: Die nachgeholte Phase brachte einen echten Fund. Bei
    Befolgung waere er nie gefunden und die Kaskade als `geprueft`
    protokolliert worden.

    Der Irrtum zeigt in Richtung `fertig`, und das ist die teure Richtung: Ein
    Werkzeug, das falsch "noch nicht fertig" meldet, kostet eine Rueckfrage;
    eines, das falsch "fertig" meldet, beendet den Vorgang.

BL-214 — DIESELBE FEHLERKLASSE, ZWEI BEHANDLUNGEN
    `ralph.*` faengt den vierten Ausgang (Log meldet Erfolg, Promise fehlt)
    seit BL-41 mit einem eigenen Exit 43 ab. `frank.*` hatte fuer denselben
    Ausgang keinen Pfad: Der Versuch wurde als INHALTLICHER Fehlversuch
    gewertet, zurueckgerollt und gezaehlt — nach drei davon steht der Fund auf
    `an Axel uebergeben`, also die teuerste Rolle des Teams fuer ein Problem,
    das die Rolle inhaltlich nie hatte. Dritter Beleg in EINEM Projekt,
    zusammen 5,86 USD reiner Werkzeugverlust.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import BASH, entrypoint_pfad, kit_pfad, verlange_bash, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE = ".vollautomatik-state"


# --- BL-210 (4): der Lint prueft Eindeutigkeit -------------------------------

def _beutebuch():
    for kandidat in (REPO_ROOT / "geteilt" / "tools" / "beutebuch.py",
                     kit_pfad("tools", "beutebuch.py")):
        if Path(kandidat).is_file():
            return Path(kandidat)
    return None


BLOCK = """### HM-7 — Beispielfund
- **Angreifer**: Harry
- **Schweregrad**: mittel
- **Status**: an Frank übergeben
- **Reproschritte**:
  1. tun
- **Erwartung**: a
- **Realität**: b
- **Reproducer-Test**: `test/hm7_beispiel_test.dart`
"""


def _lint(tmp_path, block, nr="HM-7"):
    pfad = tmp_path / "beutebuch.md"
    pfad.write_text("# Beutebuch\n\n## Funde\n\n" + block, encoding="utf-8")
    bb = _beutebuch()
    if bb is None:
        pytest.skip("beutebuch.py liegt in dieser Ablage nicht")
    import sys
    return subprocess.run([sys.executable, str(bb), "lint", nr,
                           "--pfad", str(pfad)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def test_ein_sauberer_block_bleibt_sauber(tmp_path):
    """Die Gegenprobe zuerst — ein Lint mit Fehlalarmen wird abgeschaltet."""
    r = _lint(tmp_path, BLOCK)
    assert r.returncode == 0, r.stdout + r.stderr


def test_zwei_reproducer_zeilen_in_einem_block_sind_ein_mangel(tmp_path):
    """Der zweite Befund von BL-210: Im Feld hat ein Sweep die fehlende Zeile
    eines FREMDEN Fundes ans Ende SEINES EIGENEN Blocks getragen. Der Lint
    meldete daraufhin beide Funde falsch."""
    doppelt = BLOCK + "- **Reproducer-Test**: `test/hm9_fremder_test.dart`\n"
    r = _lint(tmp_path, doppelt)
    assert r.returncode != 0, (
        "BL-210: zwei Reproducer-Zeilen in einem Block gelten weiter als "
        f"sauber — die zweite ist unsichtbar.\n{r.stdout}")
    assert "es gilt die erste" in (r.stdout + r.stderr)


# --- BL-210 (1) + BL-214: die Exit-Codes stehen getrennt ---------------------

@pytest.mark.parametrize("datei,codes", [
    ("frank.sh", ("exit 5", "exit 43")),
    ("frank.ps1", ("exit 5", "exit 43")),
])
def test_frank_trennt_die_ausgaenge(datei, codes):
    """`exit 3` trug ZWEI Bedeutungen — "nichts zu tun" und "Auftrag
    unbrauchbar" —, und die Schleife sah nur den Code."""
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = pfad.read_text(encoding="utf-8-sig")
    for code in codes:
        assert code in text, f"{datei} kennt '{code}' nicht (BL-210/BL-214)"
    assert "BL-210" in text and "BL-214" in text, (
        f"{datei} nennt die Herkunft der Ausgaenge nicht")


@pytest.mark.parametrize("datei", ["vollautomatik.sh", "vollautomatik.ps1"])
def test_die_schleife_wertet_beide_ausgaenge_aus(datei):
    """Ein eigener Exit-Code nuetzt nichts, wenn ihn niemand liest — das ist
    die Lehre aus BL-143 in dieser Familie."""
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "BL-210" in text, f"{datei} behandelt den unbrauchbaren Auftrag nicht"
    assert "BL-214" in text, f"{datei} behandelt den vierten Ausgang Franks nicht"


# --- BL-212: der Bericht richtet sich am Phasenstand aus ---------------------

def _projekt(tmp_path, frank_exit=3, ralph_kosten=0.0, frank_kosten=0.0):
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"]):
        subprocess.run(["git", "-C", str(tmp_path), *befehl], check=True,
                       capture_output=True)
    (tmp_path / "team" / "tools").mkdir(parents=True)
    (tmp_path / "plans").mkdir()
    (tmp_path / ".ralph-logs").mkdir()
    (tmp_path / ".team-logs").mkdir()
    shutil.copy(kit_pfad("lib.sh"), tmp_path / "team" / "lib.sh")
    for w in ("kosten.py", "beutebuch.py"):
        shutil.copy(kit_pfad("tools", w), tmp_path / "team" / "tools" / w)
    shutil.copy(entrypoint_pfad("vollautomatik.sh"), tmp_path / "vollautomatik.sh")
    (tmp_path / "team.config.sh").write_text(
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n', encoding="utf-8")
    # Die Stubs schreiben Kosten-Logs: Damit faellt der Pro-Lauf-Deckel an
    # einer STEUERBAREN Stelle, und der Abbruchbericht laeuft wirklich — statt
    # dass der Test seine Funktionen einzeln nachbaut.
    kosten = {"ralph": ralph_kosten, "frank": frank_kosten}
    ordner = {"ralph": ".ralph-logs", "frank": ".team-logs"}
    for rolle, code in (("ralph", 0), ("harry", 3), ("marv", 3),
                        ("frank", frank_exit), ("axel", 0), ("team-status", 0)):
        p = tmp_path / f"{rolle}.sh"
        zeilen = ["#!/usr/bin/env bash", f'echo "STUB {rolle}"']
        if kosten.get(rolle):
            zeilen.append(
                f'printf \'{{"total_cost_usd": {kosten[rolle]}, "num_turns": 1}}\' '
                f'> {ordner[rolle]}/{rolle}-stub.json')
        zeilen.append(f"exit {code}")
        p.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
        p.chmod(0o755)
    (tmp_path / ".ralph-plan").write_text(
        "plans/ralph-kaskade-13-produkt.md\n", encoding="utf-8")
    (tmp_path / ".ralph-state").write_text("5\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "init"],
                   check=True, capture_output=True)
    return tmp_path


def _lauf(repo, *args, budget="99"):
    return subprocess.run([BASH, "./vollautomatik.sh", *args], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace",
                          env=dict(os.environ, TEAM_BUDGET_USD=budget))


def test_ein_abbruch_vor_dem_red_team_schlaegt_keinen_closeout_vor(tmp_path):
    """DER Feldfall, gefahren statt nachgestellt: Der Pro-Lauf-Deckel faellt
    NACH Ralph und VOR dem Red Team. Das Beutebuch ist leer — weil niemand
    gesucht hat —, und genau daraus hat der Bericht "keine offenen Funde"
    gemacht."""
    verlange_bash()
    repo = _projekt(tmp_path, ralph_kosten=5.0)
    r = _lauf(repo, budget="1")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "WIE ES WEITERGEHT" in r.stdout, r.stdout
    assert "UNGEPRUEFT" in r.stdout, (
        "BL-212: Der Bericht schlaegt weiter den Closeout einer Kaskade vor, "
        f"deren Red-Team-Phase nie erreicht wurde.\n{r.stdout}")
    assert "nur der Closeout fehlt" not in r.stdout, \
        "und er darf den Closeout in diesem Zustand nicht als einzigen Rest nennen"


def test_nach_dem_red_team_bleibt_der_closeout_der_richtige_rat(tmp_path):
    """Die Gegenprobe, ohne die der Riegel schadet: Ist der Sweep gelaufen und
    das Beutebuch leer, IST der Closeout der richtige naechste Schritt."""
    verlange_bash()
    repo = _projekt(tmp_path, ralph_kosten=5.0, frank_kosten=50.0)
    r = _lauf(repo, budget="20")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "UNGEPRUEFT" not in r.stdout, (
        "der Riegel schlaegt an, obwohl beide Sweeps gelaufen sind:\n"
        f"{r.stdout}")
    assert "--rollen-abschluss 13" in r.stdout, (
        "BL-212 (2): die Kaskadennummer aus .ralph-plan kommt nicht im Bericht "
        f"an — der Mensch tippt weiter '<N>' ab.\n{r.stdout}")
    assert "<N>" not in r.stdout


def test_ohne_plan_bleibt_der_platzhalter_stehen(tmp_path):
    """Geraten wird nicht: Ein falscher Vorschlag waere schlimmer als ein
    sichtbarer Platzhalter."""
    verlange_bash()
    repo = _projekt(tmp_path, ralph_kosten=5.0, frank_kosten=50.0)
    (repo / ".ralph-plan").unlink()
    r = _lauf(repo, budget="20")
    assert "<N>" in r.stdout, r.stdout + r.stderr


# --- BL-214: die Abgrenzung, die ein anderer Test erzwungen hat --------------

@pytest.mark.parametrize("datei", ["frank.sh", "frank.ps1"])
def test_der_vierte_ausgang_verlangt_einen_gelandeten_fix_commit(datei):
    """Beim Bauen wurde die Bedingung ENGER, und zwar weil
    `test_bl114_rollback_verschont_fremde_arbeit` sie erzwungen hat.

    „Log meldet Erfolg UND Promise fehlt" ist NICHT das Kennzeichen des
    vierten Ausgangs — es ist das Kennzeichen JEDES inhaltlichen
    Fehlversuchs: Ein Modell, das den Dreisatz nicht schafft, beendet seine
    Sitzung ebenfalls mit `subtype=success` und ohne Promise. Ein Riegel auf
    dieser Bedingung haette Franks ganze Fehlerbehandlung stillgelegt — kein
    Rollback, kein Zaehler, keine Eskalation, nie mehr.

    Ralph darf sich das leisten, weil er zusaetzlich eine Selbstpruefung
    fahren kann. Franks Entsprechung ist der FIX-COMMIT: Liegt einer im
    Bereich, ist bezahlte Arbeit gelandet, und genau die wirft ein Rollback
    weg. Liegt keiner vor, hat die Rolle nichts hinterlassen.
    """
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = pfad.read_text(encoding="utf-8-sig")
    block = text[text.index("BL-214"):]
    block = block[:block.index("exit 43") + 20]
    assert "TEAM_FIX_PRAEFIX" in block or "hatFixCommit" in block, (
        f"{datei} nimmt den vierten Ausgang, ohne zu pruefen, ob ueberhaupt "
        "ein Fix-Commit gelandet ist — damit wird JEDER Fehlversuch zu Exit 43 "
        "und Frank verliert Rollback, Zaehler und Eskalation.")

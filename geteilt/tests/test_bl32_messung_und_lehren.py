#!/usr/bin/env python3
"""BL-32/BL-33/BL-35/BL-36/BL-37/BL-38: Die Kostenmessung und die
Planungslehren, die sie erzwungen hat.

BL-32 — Der A2-Schaetzer misst BEWEGTEN TEXT, der Treiber ist aber die
Kontext-Wiedervorlage. Solange ueberwiegend geschrieben wird, traegt der
Stellvertreter (+13…+28 % im Feld, daher die Regel `A2 / 1,25`); sobald ein
nennenswerter Teil LESEN ist, bricht das Verhaeltnis in beide Richtungen
(−49 % in einer Beschaffungssitzung, +96 % in einer gemischten). Der schaerfste
Einzelfall war eine reine DATEIROTATION: 2.456 Zeilen Beutebuch ins Archiv, ein
Werkzeugaufruf, kein Gedanke — der Schaetzer sprang auf 43,68 USD.

BL-33 — Das Messwerkzeug fuer den Abo-Betrieb liegt ausserhalb des Kits, aber
die A1-Regel verlaesst sich darauf. Also muss die Doku sagen, welche
EIGENSCHAFTEN ein tauglicher Messweg hat (Modell je Antwort, Deduplikation,
Cache-Write getrennt, ein Transkript je Aufruf) statt einen Namen zu nennen.

BL-35/36/37/38 — Vier Betriebs- und Planungslehren, die nur als Doku existieren
koennen. Geprueft wird, dass sie in ihrem TRAEGER stehen: Eine Lehre, die
nirgends steht, ist keine.
"""
import json
import subprocess
import sys
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


def _quelle(*kandidaten):
    for kandidat in kandidaten:
        pfad = REPO_ROOT / kandidat
        if pfad.is_file():
            return pfad
    raise AssertionError(f"keine der Quellen existiert: {kandidaten}")


ANHANG_A = ("doku/anhang-a.md",)
REGELDATEI = ("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md")
ARCHITEKT = ("geteilt/prompts/rolle-architekt.md", "team/prompts/rolle-architekt.md",)


# --- BL-32: Dateirotation ist kein Churn ------------------------------------

def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "plans").mkdir(parents=True)
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    (repo / "plans" / "beutebuch.md").write_text(
        "\n".join(f"Zeile {i}" for i in range(200)) + "\n", encoding="utf-8")
    (repo / "plans" / "beutebuch-archiv.md").write_text("# Archiv\n",
                                                         encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "start"],
                   check=True, capture_output=True)
    return repo


def test_rotation_ins_archiv_zaehlt_nicht_als_churn(tmp_path):
    """Der Feldfall: Zeilen wandern aus dem aktiven Buch ins Archiv. Das ist
    ein Werkzeugaufruf, kein Gedanke — und trotzdem sprang der Schaetzer."""
    repo = _repo(tmp_path)
    zeilen = (repo / "plans" / "beutebuch.md").read_text().splitlines()
    (repo / "plans" / "beutebuch.md").write_text("\n".join(zeilen[:20]) + "\n")
    (repo / "plans" / "beutebuch-archiv.md").write_text(
        "# Archiv\n" + "\n".join(zeilen[20:]) + "\n")
    churn = kosten.git_churn("HEAD", ["plans"], repo=str(repo))
    # Die 180 GELOESCHTEN Zeilen im Aktivdokument bleiben drin (von einer echten
    # Streichung nicht unterscheidbar); die 180 ANGEKOMMENEN im Archiv nicht.
    assert churn == 180, f"Archivzuwachs wird mitgezaehlt: churn={churn}"


def test_gewoehnliche_arbeit_zaehlt_weiterhin(tmp_path):
    """Gegenprobe: Der Schaetzer darf nicht generell blind werden."""
    repo = _repo(tmp_path)
    (repo / "plans" / "ralph-kaskade-1-x.md").write_text(
        "\n".join(f"neu {i}" for i in range(30)) + "\n", encoding="utf-8")
    # git diff sieht nur GETRACKTE Dateien — im echten Ablauf ist der Plan
    # committet, bevor der Schaetzer laeuft.
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                   capture_output=True)
    assert kosten.git_churn("HEAD", ["plans"], repo=str(repo)) == 30


# --- BL-37 (c): das Turn-Profil ---------------------------------------------

def test_turn_profil_liest_die_zahl_die_schon_da_ist(tmp_path):
    logs = tmp_path / ".ralph-logs"
    logs.mkdir()
    (logs / "stufe-1.json").write_text(
        json.dumps({"num_turns": 87, "total_cost_usd": 5.90}), encoding="utf-8")
    (logs / "stufe-2.json").write_text(
        json.dumps({"num_turns": 47, "total_cost_usd": 3.31}), encoding="utf-8")
    (logs / "kaputt.json").write_text("{nicht json", encoding="utf-8")
    anzahl, gesamt, zeilen = kosten.turn_profil([str(logs)])
    assert anzahl == 2 and gesamt == 134
    assert zeilen[0][1] == 87, "absteigend sortiert — der Ausreisser zuerst"


def test_turns_cli_meldet_das_profil(tmp_path):
    logs = tmp_path / ".ralph-logs"
    logs.mkdir()
    (logs / "stufe-1.json").write_text(
        json.dumps({"num_turns": 87, "total_cost_usd": 5.90}), encoding="utf-8")
    ergebnis = subprocess.run(
        [sys.executable, str(kit_pfad("tools", "kosten.py")),
         "turns", str(logs)], capture_output=True, text=True)
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "87 Turns" in ergebnis.stdout


# --- Die Lehren stehen in ihrem Traeger -------------------------------------

# Die Lehren aus BL-32/33/35/37 tragen `doku/anhang-a.md` — eine Kit-Datei, die
# NICHT installiert wird. Ihre Pruefung liegt deshalb im Regel-Inventar
# (kit-regelinventar.py, Stufe 8 von kit-test.sh): Dort steht jedes Zitat samt
# Traeger und wird woertlich gegen die Datei gehalten. Ein zweiter, hier
# uebersprungener Test waere in der Installation dauerhaft blind — genau die
# Bauart aus BL-58.


def test_uebergaberegel_schliesst_messreihen_aus():
    """BL-36: Die Regel bindet Harry und Marv — sie gehoert in die Regeldatei,
    nicht nur in die Betriebslehre."""
    text = _quelle(*REGELDATEI).read_text(encoding="utf-8")
    assert "Messreihe" in text
    assert "Uhrzeit statt Denken" in text, \
        "das Kriterium muss benannt sein, sonst wird 'schwer' daraus gelesen"


def test_aushaertung_fragt_nach_der_beweisbarkeit():
    """BL-38: vor dem Stufenschnitt, nicht danach."""
    text = _quelle(*ARCHITEKT).read_text(encoding="utf-8")
    assert "ROT" in text and "Umgebung, in der" in text

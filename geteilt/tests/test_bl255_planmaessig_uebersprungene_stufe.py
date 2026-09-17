#!/usr/bin/env python3
"""BL-255: Eine planmaessig abgebrochene Stufe war vom vierten Ausgang nicht zu
unterscheiden — die Schleife druckte Exit 43 und einen Grund, der nachweislich
nicht zutraf.

DER FELDBEFUND
    Eine Stufe mit im Plan ausgeschriebener ABBRUCHBEDINGUNG trat ein: Ralph
    hat gemessen, die Konfiguration unangetastet gelassen, den Befund in den
    `[Unreleased]`-Block eingetragen, committet — und REGELKONFORM kein Promise
    gegeben, weil die Stufe nicht abgeschlossen, sondern abgebrochen wurde.

    Fuer diese Lage gab es keine Vokabel. Es gab Promise oder kein Promise, und
    *kein Promise* ist mit dem teuersten Bericht des Werkzeugs belegt.

WARUM DIE SELBSTPRUEFUNG (BL-110) ES NICHT BESSER, SONDERN ZWEIDEUTIG MACHTE
    Pruefung 1 (*hat die Sitzung Arbeit hinterlassen*) trifft zu, Pruefung 2
    (*gibt es eine beruehrte Testdatei*) in der Regel nicht — also faellt sie
    durch, und der Lauf landet im Exit 43 mit der Begruendung *Produktivcode
    ohne Zusicherung*, die ebenfalls nicht zutrifft. **Der Mensch bekommt in
    beiden Zweigen eine falsche Diagnose**, und eine abgebrochene Stufe, die
    zufaellig doch eine Testdatei angefasst hat, wuerde sogar still als
    abgeschlossen durchgewunken.

WARUM DAS MEHR IST ALS KOSMETIK
    Der vierte Ausgang ist die teuerste Meldung des Werkzeugs. Wird sie bei
    einem GEORDNETEN Abschluss gedruckt, stumpft sie ab und wird beim naechsten
    echten Fall weggeklickt.

WAS DIESER TEST PRUEFT
    Die zweite Quittungsform gibt es, sie ist auf beiden Bahnen gleich, und sie
    ist KEIN Schlupfloch: Sie gilt nur, wenn der Plan sie fuer genau diese
    Stufe ausschreibt, und nur mit Commit. Dazu der Nebenbefund — die
    Abhilfe-Zeile kennt jetzt den Cap, statt eine Stufennummer vorzuschlagen,
    die einen stillen No-Op erzeugt.
"""
import re
from pathlib import Path

import pytest

from conftest import RufMarke, Schreib

WURZEL = Path(__file__).resolve().parents[2]

BIBLIOTHEKEN = ("bash/lib.sh", "pwsh/lib.psm1")
RALPH = {"bash": "bash/entry/ralph.sh", "pwsh": "pwsh/entry/ralph.ps1"}
VOLLAUTOMATIK = {"bash": "bash/entry/vollautomatik.sh",
                 "pwsh": "pwsh/entry/vollautomatik.ps1"}


def _quelle(rel):
    pfad = WURZEL / rel
    if not pfad.is_file():
        pytest.skip(f"{rel} liegt in dieser Ablage nicht")
    return pfad.read_text(encoding="utf-8")


# --- (1) Die Vokabel existiert, auf beiden Bahnen ----------------------------

@pytest.mark.parametrize("bahn", sorted(RALPH))
def test_ralph_kennt_die_zweite_quittungsform(bahn):
    """Der Fund selbst: Es gab nur COMPLETE."""
    text = _quelle(RALPH[bahn])
    assert "_UEBERSPRUNGEN" in text, (
        f"{RALPH[bahn]} kennt nur eine Quittungsform — eine planmaessig "
        "abgebrochene Stufe landet damit im vierten Ausgang (BL-255).")


@pytest.mark.parametrize("bahn", sorted(RALPH))
def test_die_rolle_erfaehrt_die_vokabel_im_prompt(bahn):
    """Eine Vokabel, die nur der Loop kennt, benutzt niemand."""
    text = _quelle(RALPH[bahn])
    assert "_UEBERSPRUNGEN</promise>" in text, (
        f"{RALPH[bahn]} nennt die zweite Form nicht im Auftrag der Rolle "
        "(BL-255).")
    assert "Abbruchbedingung" in text, (
        f"{RALPH[bahn]} sagt der Rolle nicht, WANN die zweite Form gilt.")


@pytest.mark.parametrize("bahn", sorted(RALPH))
def test_der_abschlusstext_ist_ruhig(bahn):
    """Kein Pruefkatalog, keine Warnung — der Punkt des ganzen Eintrags."""
    text = _quelle(RALPH[bahn])
    assert "planmäßig übersprungen" in text, (
        f"{RALPH[bahn]} druckt fuer den geordneten Ausgang keinen eigenen "
        "Text (BL-255).")


# --- (2) Die drei Riegel ----------------------------------------------------

@pytest.mark.parametrize("bahn", sorted(RALPH))
def test_riegel_a_der_plan_muss_sie_ausschreiben(bahn):
    text = _quelle(RALPH[bahn])
    assert "team_plan_erlaubt_uebersprung" in text, (
        f"{RALPH[bahn]} prueft nicht, ob der PLAN die zweite Form vorsieht — "
        "dann waere sie ein Weg, eine Stufe ohne Arbeit abzuhaken (BL-255).")


@pytest.mark.parametrize("bahn", sorted(RALPH))
def test_riegel_b_ohne_commit_gilt_sie_nicht(bahn):
    text = _quelle(RALPH[bahn])
    assert re.search(r"head[_ ]?vorher", text, re.I), (
        f"{RALPH[bahn]} vergleicht den Stand vor und nach der Stufe nicht — "
        "ein Uebersprung ohne Spur ist von 'nicht gelaufen' nicht zu "
        "unterscheiden (BL-255).")
    assert "status --porcelain" in text, (
        f"{RALPH[bahn]} laesst Uncommittetes durchgehen (BL-255).")


@pytest.mark.parametrize("bahn", sorted(BIBLIOTHEKEN))
def test_die_pruefung_liest_die_stufennummer_mit(bahn):
    """Die Zeichenkette traegt die Nummer — sonst wuerde der Block einer
    ANDEREN Stufe die Erlaubnis erteilen."""
    text = _quelle(bahn)
    assert "STUFE_${stufe}_UEBERSPRUNGEN" in text or \
           "STUFE_${Stufe}_UEBERSPRUNGEN" in text, (
        f"{bahn}: Die Pruefung kennt die Stufennummer nicht (BL-255).")


# --- (3) Das Verhalten der Pruefung, auf beiden Bahnen -----------------------

PLAN_MIT = """# Kaskade 1
RALPH_CAP=3

## Stufe 2 — Die Messung
**Abbruchbedingung.** Ergibt die Messung, dass der Wert schon stimmt, wird
diese Stufe NICHT gebaut.
**Promise.** `<promise>STUFE_2_COMPLETE</promise>` — trifft die
Abbruchbedingung zu: `<promise>STUFE_2_UEBERSPRUNGEN</promise>`
"""

PLAN_OHNE = """# Kaskade 1
RALPH_CAP=3

## Stufe 2 — Die Messung
**Promise.** `<promise>STUFE_2_COMPLETE</promise>`
"""


def test_die_erlaubnis_haengt_am_plan(schale, tmp_path):
    """Der Riegel selbst, am Verhalten: dieselbe Stufe, zwei Plaene."""
    ergebnis = schale.lauf([
        Schreib("plan-mit.md", PLAN_MIT),
        RufMarke("team_plan_erlaubt_uebersprung", "2", "plan-mit.md",
                 marke="ERLAUBT"),
    ], cwd=tmp_path)
    assert "ERLAUBT" in ergebnis.stdout, ergebnis.stdout + ergebnis.stderr


def test_ohne_abbruchbedingung_keine_erlaubnis(schale, tmp_path):
    """Gegenrichtung — ohne sie waere die Vokabel ein Freifahrtschein."""
    ergebnis = schale.lauf([
        Schreib("plan-ohne.md", PLAN_OHNE),
        RufMarke("team_plan_erlaubt_uebersprung", "2", "plan-ohne.md",
                 marke="ERLAUBT"),
    ], cwd=tmp_path)
    assert "ERLAUBT" not in ergebnis.stdout, (
        "Ein Plan ohne Abbruchbedingung erlaubt den Uebersprung — damit ist "
        f"die Vokabel ein Schlupfloch (BL-255).\n{ergebnis.stdout}")


def test_die_erlaubnis_gilt_nur_der_genannten_stufe(schale, tmp_path):
    """Der Plan nennt Stufe 2 — Stufe 3 darf davon nicht profitieren."""
    ergebnis = schale.lauf([
        Schreib("plan-mit.md", PLAN_MIT),
        RufMarke("team_plan_erlaubt_uebersprung", "3", "plan-mit.md",
                 marke="ERLAUBT"),
    ], cwd=tmp_path)
    assert "ERLAUBT" not in ergebnis.stdout, (
        "Die Erlaubnis einer Stufe gilt fuer eine andere mit — dann ist die "
        f"Stufennummer in der Vokabel wertlos (BL-255).\n{ergebnis.stdout}")


def test_ohne_plan_keine_erlaubnis(schale, tmp_path):
    """Im Zweifel gilt 'nicht erlaubt' — dieselbe Richtung wie BL-110."""
    ergebnis = schale.lauf([
        RufMarke("team_plan_erlaubt_uebersprung", "2", "gibt-es-nicht.md",
                 marke="ERLAUBT"),
    ], cwd=tmp_path)
    assert "ERLAUBT" not in ergebnis.stdout, ergebnis.stdout


# --- (4) Getrennt gezaehlt (Riegel c) ---------------------------------------

@pytest.mark.parametrize("bahn", sorted(VOLLAUTOMATIK))
def test_der_abschlussbericht_zaehlt_sie_getrennt(bahn):
    """Ein Lauf mit ausgelassener Stufe darf nicht wie ein vollstaendiger
    aussehen."""
    text = _quelle(VOLLAUTOMATIK[bahn])
    assert "ralph-uebersprungen" in text, (
        f"{VOLLAUTOMATIK[bahn]} liest die ausgelassenen Stufen nicht — dann "
        "steht nirgends, dass eine Stufe ausgelassen wurde (BL-255).")
    assert "Planmäßig übersprungen" in text


def test_die_zustandsdatei_steht_in_der_gitignore_vorlage():
    """Sonst warnt der Guard bei jedem Rollenstart — die Lage aus BL-233."""
    text = _quelle("bootstrap/gitignore.fragment")
    assert ".ralph-uebersprungen" in text, (
        "Die Vorlage ignoriert den neuen Lauf-Zustand nicht; ab der ersten "
        "ausgelassenen Stufe ist der Arbeitsbaum dreckig (BL-233/BL-255).")


# --- (5) Der Nebenbefund: die Abhilfe-Zeile kennt den Cap --------------------

@pytest.mark.parametrize("bahn", sorted(RALPH))
def test_die_abhilfe_zeile_kennt_den_cap(bahn):
    """Sie schlug die naechste Stufennummer vor, ohne den Cap zu kennen —
    liegt sie darueber, erzeugt der Rat einen stillen No-Op."""
    text = _quelle(RALPH[bahn])
    assert "WAR die letzte" in text, (
        f"{RALPH[bahn]}: Die Abhilfe-Zeile schlaegt weiter eine Stufennummer "
        "vor, ohne den Cap zu kennen (BL-255, Nebenbefund).")


# --- (6) Das Briefing, das die Form ueberhaupt freischaltet ------------------

def test_der_architekt_weiss_wie_eine_abbruchbedingung_aussieht():
    """Der Architekt ist der EINZIGE, der die zweite Form freischalten kann —
    Ralph prueft nur, ob sie im Plan steht."""
    text = _quelle("geteilt/prompts/rolle-architekt.md")
    assert "_UEBERSPRUNGEN" in text, (
        "Das Architekten-Briefing kennt die zweite Quittungsform nicht — dann "
        "schreibt sie niemand in einen Plan, und der Riegel macht sie "
        "unerreichbar (BL-255).")
    assert "Abbruchbedingung" in text


def test_beide_bahnen_sagen_dasselbe():
    """Drift ist der Fehler, den die Doppelbahn sichtbar machen soll."""
    bash, pwsh = _quelle(RALPH["bash"]), _quelle(RALPH["pwsh"])
    for merkmal in ("_UEBERSPRUNGEN", "team_plan_erlaubt_uebersprung",
                    "planmäßig übersprungen", "WAR die letzte", "BL-255"):
        assert (merkmal in bash) == (merkmal in pwsh), (
            f"'{merkmal}' steht nur auf einer Bahn (BL-229).")

#!/usr/bin/env python3
"""BL-227: Der Hilfetext von `kit-melden` kannte `ablegen` nicht — also genau
den Weg, den der Owner gehen soll.

WIE DER FUND ENTSTAND
    Beim Einreihen zweier fertiger Meldungen sollte `kit-melden … ablegen`
    benutzt werden; die Projektregel nennt es ausdruecklich. Im Kopfkommentar
    des Werkzeugs stand es nicht. Fuenf Verben dort, SECHS in `kit_meldung.py`
    — `ablegen` war vorhanden, funktionierte und hatte einen ausfuehrlichen
    Docstring. Nur die Hilfe, die ein Mensch zuerst liest, wusste nichts davon.

WARUM DAS MEHR IST ALS EINE FEHLENDE ZEILE
    Es ist der Rest einer bereits abgetragenen Aufgabe. `BL-187` hielt fest,
    dass der Rueckkanal nur einen Weg kannte — den Pull Request — und dass der
    fuer den Owner der falsche ist: Er legt ihn gegen sein eigenes Repo an,
    reviewt und merged seine eigene Meldung. Nachgezogen wurden damals
    Rollen-Briefing, `bootstrap/TEAM.md` und `bootstrap/CLAUDE.md.vorlage`;
    der Hilfetext des Werkzeugs selbst blieb stehen. Wer sich das Werkzeug
    ueber seine EIGENE Hilfe erschliesst, fand deshalb weiter nur `senden`.

WAS DIESER TEST PRUEFT
    Die GATTUNG, nicht die eine fehlende Zeile (Lehre aus BL-198/BL-208/
    BL-224): Die Verbliste im Kopfkommentar JEDER Bahn muss deckungsgleich mit
    den Unterbefehlen von `kit_meldung.py` sein — in beide Richtungen. Ein
    kuenftiges siebtes Verb faellt damit auf, statt still ohne Bedienung zu
    bleiben; ein geloeschtes ebenso.

    Die Quelle der Wahrheit ist das Python-Werkzeug, weil dort das VERHALTEN
    liegt. Ein Wrapper, der ein Verb nennt, das es nicht gibt, waere derselbe
    Fehler mit umgekehrtem Vorzeichen — auch den meldet der Test.
"""
import re
from pathlib import Path

import pytest

from conftest import entrypoint_pfad, kit_pfad

# Die Wrapper nennen ihre Verben im Kopfkommentar unter "Aufruf:" — pwsh im
# Block-Kommentar `<# … #>`, bash in `#`-Zeilen. Beide Zeilen haben dieselbe
# Form: <aufrufname> <verb> [<argumente>]  <erklaerung>.
BAHNEN = {
    "bash": ("kit-melden.sh",
             re.compile(r"^#\s+\./kit-melden\.sh\s+([a-z][a-z-]*)", re.M)),
    "pwsh": ("kit-melden.ps1",
             re.compile(r"^\s+\.\\kit-melden\.cmd\s+([a-z][a-z-]*)", re.M)),
}


def _verben_des_werkzeugs():
    """Die Unterbefehle von kit_meldung.py — die Quelle der Wahrheit."""
    pfad = Path(kit_pfad("tools", "kit_meldung.py"))
    if not pfad.is_file():
        pytest.skip("kit_meldung.py liegt in dieser Ablage nicht")
    text = pfad.read_text(encoding="utf-8")
    verben = set(re.findall(r"""sub\.add_parser\(\s*["']([a-z][a-z-]*)["']""", text))
    assert verben, "keine Unterbefehle in kit_meldung.py gefunden — Muster veraltet?"
    return verben


def _verben_des_wrappers(bahn):
    name, muster = BAHNEN[bahn]
    pfad = Path(entrypoint_pfad(name))
    if not pfad.is_file():
        pytest.skip(f"{name} liegt in dieser Ablage nicht (einbahnig installiert)")
    text = pfad.read_text(encoding="utf-8-sig")
    # Nur der KOPF bis zum ersten Code — der Hilfetext, nicht der Rumpf.
    kopf = text.split("set -uo pipefail")[0].split("$ErrorActionPreference")[0]
    verben = set(muster.findall(kopf))
    assert verben, f"keine Verbliste im Kopf von {name} gefunden — Muster veraltet?"
    return verben


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_hilfetext_nennt_jedes_verb_des_werkzeugs(bahn):
    """Der Fund selbst: `ablegen` fehlte in beiden Hilfetexten."""
    werkzeug = _verben_des_werkzeugs()
    wrapper = _verben_des_wrappers(bahn)
    fehlend = sorted(werkzeug - wrapper)
    assert not fehlend, (
        f"kit-melden ({bahn}) kennt {fehlend} nicht — kit_meldung.py schon. "
        "Wer das Werkzeug ueber seine eigene Hilfe erschliesst, findet den "
        "Weg nicht (BL-227).")


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_hilfetext_erfindet_kein_verb(bahn):
    """Gegenprobe: derselbe Fehler mit umgekehrtem Vorzeichen."""
    werkzeug = _verben_des_werkzeugs()
    wrapper = _verben_des_wrappers(bahn)
    erfunden = sorted(wrapper - werkzeug)
    assert not erfunden, (
        f"kit-melden ({bahn}) nennt {erfunden}, kit_meldung.py kennt das nicht.")


def test_beide_bahnen_nennen_dieselben_verben():
    """Drift zwischen den Bahnen ist der Fehler, den die Doppelbahn sichtbar
    machen soll — hier wird er zusaetzlich benannt."""
    bash = _verben_des_wrappers("bash")
    pwsh = _verben_des_wrappers("pwsh")
    assert bash == pwsh, (
        f"nur bash: {sorted(bash - pwsh)} · nur pwsh: {sorted(pwsh - bash)}")


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_hilfetext_sagt_wann_ablegen_der_weg_ist(bahn):
    """Eine Zeile mehr in der Liste haette den Fund halb abgetragen: Der
    Melder muss WAEHLEN koennen. BL-187 sagt, wonach — liegt das Kit lokal
    daneben, ist `ablegen` der Weg, `senden` ist fuer Melder ohne Kit-Repo.
    """
    name, _ = BAHNEN[bahn]
    pfad = Path(entrypoint_pfad(name))
    if not pfad.is_file():
        pytest.skip(f"{name} liegt in dieser Ablage nicht")
    kopf = pfad.read_text(encoding="utf-8-sig")[:6000]
    assert "TEAM_KIT_PFAD" in kopf, (
        f"{name} nennt `ablegen`, sagt aber nicht, woran der Melder erkennt, "
        "dass es sein Weg ist (BL-227).")
    assert "BL-187" in kopf, (
        f"{name} begruendet die Wahl nicht — BL-187 ist der Grund, aus dem es "
        "`ablegen` ueberhaupt gibt.")

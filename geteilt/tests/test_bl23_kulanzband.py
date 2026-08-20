#!/usr/bin/env python3
"""BL-23: Der harte Budget-Stopp kannte die Restarbeit nicht — und stoppte
deshalb im teuersten Moment.

Der Deckel greift NACH dem bereits bezahlten Aufruf und rechnet den Fortschritt
nicht mit: Er kann eine Fixphase mitten zwischen "Fund an Frank uebergeben" und
"Fix liegt vor" kappen. Im Feld eingetreten — Lauf bei 19,96 von 19 USD
gestoppt, ein Fund vom Schweregrad HOCH im Status "an Frank uebergeben"
zurueckgelassen. Die fehlende Restarbeit kostete 1,52 USD; dagegen standen der
Handstart der Rolle, ein zweiter Kontextaufbau, eine Architekten-Nachfrage samt
Lageaufnahme und ein ueber zwei Sitzungen zerfallener Closeout. Der Stopp hat
weniger gespart, als sein eigenes Aufraeumen kostete.

Gebaut sind die empfohlenen Varianten (1) und (3):
  (1) Kulanzband — die angefangene Runde laeuft zu Ende, solange der Lauf unter
      Deckel + X % liegt UND ein Fund in Bearbeitung ist. EINMAL, dann hart.
  (3) Abbruch-Bericht mit Fortsetzungsbefehl — hilft bei jedem Abbruchgrund.

Variante (2), die Deckel-Prognose vor der Phase, ist bewusst NICHT gebaut: Sie
waere eine neue Schaetzung und damit eine neue Fehlerquelle.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _entrypoint(name):
    for kandidat in (REPO_ROOT / name,
                     REPO_ROOT / "bash" / "entry" / name,
                     REPO_ROOT / "pwsh" / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


VOLLAUTOMATIK = _entrypoint("vollautomatik.sh")
pytestmark = pytest.mark.skipif(VOLLAUTOMATIK is None,
                                 reason="vollautomatik.sh nicht gefunden")


@pytest.fixture(scope="module")
def text():
    return VOLLAUTOMATIK.read_text(encoding="utf-8")


def test_kulanzband_ist_eine_benannte_zahl(text):
    """Die Obergrenze muss ein konfigurierter Wert sein, kein Gefuehl."""
    assert "TEAM_BUDGET_KULANZ_PROZENT" in text
    assert re.search(r'TEAM_BUDGET_KULANZ_PROZENT:-\d+', text), \
        "das Kulanzband braucht einen sichtbaren Default"


def test_kulanz_gilt_nur_bei_einem_fund_in_bearbeitung(text):
    """Ohne diese Bedingung waere es schlicht ein hoeherer Deckel."""
    kulanz_block = text[text.index("budget_ok() {"):text.index("abbruch_bericht")]
    assert "an Frank übergeben" in kulanz_block, \
        "das Kulanzband muss an den Fund-Status gebunden sein"


def test_kulanz_wird_nur_einmal_gewaehrt(text):
    """Sonst laeuft der Lauf im Kulanzband weiter, statt darin zu enden."""
    assert "KULANZ_GEWAEHRT" in text
    kulanz_block = text[text.index("budget_ok() {"):text.index("abbruch_bericht")]
    assert 'KULANZ_GEWAEHRT" -eq 0' in kulanz_block


def test_bauphase_bekommt_keine_kulanz(text):
    """Die Kulanz gilt nur der Fixphase: Nur dort gibt es einen halbfertigen
    Zwischenzustand, den ein Stopp beschaedigt. Phase 1-3 rufen budget_ok OHNE
    Argument."""
    phase1 = text[text.index("PHASE 1: Ralph"):text.index("PHASE 4")]
    assert "budget_ok kulanz" not in phase1


def test_jeder_budget_abbruch_druckt_den_weiterweg(text):
    for treffer in re.finditer(r'budget_ok[^\n]*\|\|([^\n]*)', text):
        assert "abbruch_bericht" in treffer.group(1), \
            f"Abbruch ohne Fortsetzungsbefehl: {treffer.group(0)}"


def test_auch_die_stagnationsbremse_druckt_ihn(text):
    stagnation = text[text.index("Fix-Phase stagniert"):]
    assert "abbruch_bericht" in stagnation[:400]


def test_bericht_nennt_die_offenen_funde_und_den_befehl(text):
    bericht = text[text.index("abbruch_bericht() {"):]
    bericht = bericht[:bericht.index("\n}\n")]
    assert "./frank.sh" in bericht, "der Fortsetzungsbefehl fehlt"
    assert "rollen-abschluss" in bericht, "der Closeout-Hinweis fehlt"
    assert "list" in bericht, "die offenen Funde werden nicht aufgezaehlt"

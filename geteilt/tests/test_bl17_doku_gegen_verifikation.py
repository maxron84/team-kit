#!/usr/bin/env python3
"""BL-17: Die Verifikationskette darf sich den Erfolg nicht selbst einrichten.

Aus dem Feld zurueckgespielt (dort BL-10, Feld A). Der
dokumentierte Startbefehl war kaputt, waehrend der Smoke-Test GRUEN meldete —
weil Smoke-Test und pytest.ini still ein PYTHONPATH dazusetzten, das es beim
Anwender nie gibt. Verifiziert wurde damit eine Umgebung, die nur auf dem
Entwicklerrechner existiert.

Das Bemerkenswerte ist nicht der Einzelfall, sondern die blinde Stelle: Fuenf
Red-Team-Funde derselben Kaskade hatten exakt diese Bauart ("Pfad existiert,
wird aber nie wirklich ausgefuehrt"), und KEINER der Sweeps hat diesen
gefunden. Harry und Marv lesen den Code; die Luecke klafft aber zwischen Doku
und Testaufruf, und dorthin schaute kein Auftrag.

Entscheid (Stakeholder, 2026-08-02): Regel in den Vorlagen PLUS benannter
Sweep-Schwerpunkt in den Briefings. Kein maschineller Diff — der waere
stackagnostisch schwer und mit hoher Falschmelderate zu erwarten; er kommt
erst, wenn ein zweiter Fall dieser Bauart auftritt.

Dieser Test haelt beide Haelften fest. Eine Regel, die niemand liest, und ein
Auftrag ohne Regel wirken je fuer sich nicht.
"""

import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

WURZEL = Path(__file__).resolve().parents[2]


def _quelle(*kandidaten):
    """Kit-Vorlage oder installierte Zieldatei — je nachdem, wo wir laufen."""
    for kandidat in kandidaten:
        pfad = WURZEL / kandidat
        if pfad.is_file():
            return pfad
    raise AssertionError(f"keine der Quellen existiert: {kandidaten}")


REGELTRAEGER = {
    "Regeldatei": ("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md"),
    "Bedienanleitung": ("bootstrap/TEAM.md", "TEAM.md"),
}


@pytest.mark.parametrize("name", sorted(REGELTRAEGER))
def test_regel_steht_in_der_doku(name):
    """Die normative Haelfte: Der Smoke-Test darf keine stille Umgebung setzen."""
    text = _quelle(*REGELTRAEGER[name]).read_text(encoding="utf-8")
    assert "buchstabengetreu" in text, (
        f"{name} nennt die Regel nicht — der Doku-Befehl muss buchstabengetreu "
        f"in der Verifikation vorkommen."
    )
    assert "keine Umgebung setzen, die die Doku nicht nennt" in text, (
        f"{name} nennt die konkrete Grenze fuer den Smoke-Test nicht."
    )
    assert "PYTHONPATH" in text, (
        f"{name} nennt das reale Beispiel nicht — abstrakte Regeln werden "
        f"nicht angewandt."
    )


@pytest.mark.parametrize("rolle", ["harry", "marv"])
def test_briefing_traegt_den_sweep_schwerpunkt(rolle):
    """Die operative Haelfte: Ohne Auftrag schaut niemand dorthin.

    Genau das ist der Befund — fuenf Sweeps derselben Bauart, kein Treffer,
    weil der Auftrag den Code meinte und nicht die Luecke daneben.
    """
    text = kit_pfad("prompts", f"rolle-{rolle}.md").read_text(encoding="utf-8")
    assert "Doku gegen Verifikation diffen" in text, (
        f"rolle-{rolle}.md kennt den Sweep-Schwerpunkt nicht"
    )
    assert "PYTHONPATH" in text, f"rolle-{rolle}.md nennt das konkrete Muster nicht"
    assert "zwischen" in text and "Testaufruf" in text, (
        f"rolle-{rolle}.md sagt nicht, WO die Luecke liegt — genau das war die "
        f"blinde Stelle der bisherigen Sweeps."
    )


if __name__ == "__main__":
    fehler = []
    for name in sorted(REGELTRAEGER):
        try:
            test_regel_steht_in_der_doku(name)
            print(f"OK   test_regel_steht_in_der_doku[{name}]")
        except AssertionError as e:
            fehler.append(name)
            print(f"FAIL test_regel_steht_in_der_doku[{name}]: {e}")
    for rolle in ("harry", "marv"):
        try:
            test_briefing_traegt_den_sweep_schwerpunkt(rolle)
            print(f"OK   test_briefing_traegt_den_sweep_schwerpunkt[{rolle}]")
        except AssertionError as e:
            fehler.append(rolle)
            print(f"FAIL test_briefing_traegt_den_sweep_schwerpunkt[{rolle}]: {e}")
    if fehler:
        sys.exit(1)
    print("gruen — BL-17 verifiziert: Regel und Auftrag stehen beide.")

#!/usr/bin/env python3
"""BL-49: Die Kopplung eines Tests an einen zentralen Wert ist per Textsuche
nicht auffindbar — nur das probeweise Verstellen findet sie.

Feld (2026-08-10/11): Nach einem Tweak an einer Balancing-Konstante suchte der
Aufraeumlauf ueber die Schwesterkonstante nach dem naheliegenden Muster — nach
dem NAMEN der Konstante und nach ihrem alten WERT. `grep` fand fuenf Stellen
(`== 100`, `== 100 - 8`, `== 100 - 15`). Die Gegenprobe — Regler probeweise auf
einen fremden Wert, Suite laufen lassen — fand SIEBEN. Die zwei zusaetzlichen
standen als nacktes `abziehen(40)` in zwei HUD-Tests, deren Erwartung auf
`HUD_BREITE * 0.6` verdrahtet war: 40 ist kein Vorkommen von 100, und 0.6
keines von 60. Ohne die Gegenprobe waere die Umstellung als "vollstaendig"
gemeldet worden und beim naechsten Tweak an zwei unerklaerlichen Stellen rot
geworden.

Entscheid analog BL-17 (Regel + Auftrag, kein maschineller Pruefer): Die Regel
steht in den BAUENDEN Briefings (Ralph, Frank) und in der
Aushaertungs-Checkliste. Ein Test, der selbst Regler verstellt, kollidiert mit
parallelen Laeufen — die billige Fassung ist die Regel.

Dieser Test haelt beide Traeger fest, inklusive des Halbsatzes, der am
ehesten wegfaellt: dem nachweislichen ZURUECKSETZEN. Die Probe veraendert
Produktivcode; ihr Rueckbau gehoert in dieselbe Bearbeitung.
"""

import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]


def _quelle(*kandidaten):
    for kandidat in kandidaten:
        pfad = WURZEL / kandidat
        if pfad.is_file():
            return pfad
    raise AssertionError(f"keine der Quellen existiert: {kandidaten}")


TRAEGER = {
    "rolle-ralph": ("geteilt/prompts/rolle-ralph.md", "team/prompts/rolle-ralph.md",),
    "rolle-frank": ("geteilt/prompts/rolle-frank.md", "team/prompts/rolle-frank.md",),
    "Regeldatei": ("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md"),
}


@pytest.mark.parametrize("name", sorted(TRAEGER))
def test_regel_steht_beim_bauenden(name):
    text = _quelle(*TRAEGER[name]).read_text(encoding="utf-8")
    assert "zwei fremde Werte" in text, (
        f"{name} verlangt die Gegenprobe nicht — eine Richtung allein findet "
        f"asymmetrische Kopplungen nicht")
    assert "zurück" in text, (
        f"{name} nennt den Rueckbau nicht. Die Probe veraendert Produktivcode; "
        f"ohne diesen Halbsatz bleibt ein fremder Wert stehen")
    assert "Suite" in text, f"{name} sagt nicht, WAS die Probe beweist"


@pytest.mark.parametrize("name", sorted(TRAEGER))
def test_begruendung_steht_dabei(name):
    """Ohne die Zahlen liest sich die Regel als Bueroaufwand — und wird
    weggelassen. Dieselbe Lehre wie bei der SMOKE_ZEILE (BL-41): Die
    Begruendung gehoert in den Prompt, nicht in den Commit."""
    text = _quelle(*TRAEGER[name]).read_text(encoding="utf-8")
    # Bewusst am WORTLAUT des Belegs, nicht an "fuenf"/"sieben" allein: Die
    # Regeldatei enthaelt beide Zahlwoerter laengst an anderer Stelle (BL-17),
    # womit die Gegenprobe dort gruen geblieben waere, ohne dass die Regel
    # steht. Genau die Sorte Zusicherung, die nichts zusichert.
    assert "das Verstellen" in text or "das probeweise Verstellen" in text, (
        f"{name} nennt den Feld-Beleg nicht (grep fand 5, das Verstellen 7)")
    assert "sieben" in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

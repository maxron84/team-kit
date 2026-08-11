#!/usr/bin/env python3
"""BL-50: Der Closeout pflegt den Backlog — aber nichts pflegt die Stellen, die
den Backlog ZITIEREN.

Die Abschlussregel verlangt, erledigte Eintraege abzutragen, und das
funktioniert. Kein Schritt verlangt die Gegenrichtung: *Wer verweist auf den
Punkt, den ich gerade abgetragen habe?* Die Kandidaten-/Skizzenliste, aus der
die naechste Kaskade gewaehlt wird, begruendet ihre offenen Fragen mit
Backlog-Nummern — und veraltet still in dem Moment, in dem der zitierte Eintrag
erledigt wird.

Der Fehler schlaegt an der teuersten Stelle zu: beim VORLEGEN der Kandidaten,
also nachdem der Architekt eine Option formuliert hat, die es nicht mehr gibt.
Feld-Beleg: Eine Skizze stand drei Kaskaden lang auf der Praemisse "wartet auf
einen Ausloeser (BL-80)" — der Ausloeser war seit Kaskade 28 gebaut, und der
zitierte Eintrag lag laengst im Archiv. Zweiter Beleg im selben Projekt:
ein Skizzenblock stand auf "Umbau offen", obwohl eine Kaskade jeden genannten
Punkt gebaut hatte.

Gebaut ist Stufe 1 des Vorschlags — die Pflichtfrage im Abschluss-Doc, plus die
Schreibweise `Kit-BL-<N>`, ohne die jeder spaetere Lint im falschen Dokument
nachschlaegt (der doppelt belegte Nummernraum war der erste Befund des
Feld-Probelaufs). Stufe 2 (der Lint) bleibt offen: Roh gemessen lag seine
Trefferquote bei ~40 % — sechs von zehn Markierungen waren legitime
Rueckblicke. Roh ausgeliefert waere das die Falle aus BL-14, eine Warnung, die
bei jedem Aufruf erscheint und zum Wegsehen erzieht.
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


REGELDATEI = ("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md")
BRIEFING = ("team/prompts/rolle-architekt.md",)


@pytest.mark.parametrize("traeger", [REGELDATEI, BRIEFING],
                         ids=["Regeldatei", "rolle-architekt"])
def test_pflichtfrage_steht_im_abschluss(traeger):
    """Beide Traeger, nicht einer: Die Gliederung sagt, WAS im Doc steht, das
    Briefing sagt der Rolle, dass sie es beantworten muss. Eine Haelfte ohne
    die andere wirkt nicht."""
    text = _quelle(*traeger).read_text(encoding="utf-8")
    assert "nebenbei" in text.lower(), (
        "die Pflichtfrage fehlt — 'nebenbei eingeloest' ist der Regelfall, "
        "den der Bauplan der Kaskade nirgends nennt")
    assert "zitier" in text.lower(), (
        "die Gegenrichtung fehlt: WER zitiert den abgetragenen Punkt?")


@pytest.mark.parametrize("traeger", [REGELDATEI, BRIEFING],
                         ids=["Regeldatei", "rolle-architekt"])
def test_fremde_backlog_nummern_haben_eine_schreibweise(traeger):
    """Ohne diese Konvention schlaegt jeder Verweis — und jeder spaetere
    Lint — im falschen Dokument nach: `BL-<N>` bedeutet im Kit etwas anderes
    als im Projekt."""
    text = _quelle(*traeger).read_text(encoding="utf-8")
    assert "Kit-BL-" in text, (
        "die Schreibweise fuer fremde Backlog-Nummern fehlt")


def test_abschnitt_vier_traegt_die_zeile_in_der_gliederung():
    """Die Gliederung ist das, was ein kalt startendes Architekt-Ich kopiert.
    Steht die Frage nur in der Prosa daneben, faellt sie beim Kopieren weg —
    genau die Bauart, die BL-44 beschreibt (angekuendigt, aber nicht am
    wirksamen Ort geschrieben)."""
    text = _quelle(*REGELDATEI).read_text(encoding="utf-8")
    block = text.split("## 4. Closeout-Funde", 1)
    assert len(block) == 2, "Abschnitt 4 fehlt in der Gliederung"
    kopf = block[1].split("## 5.", 1)[0]
    assert "PFLICHTZEILE" in kopf, (
        "die Pflichtzeile steht nicht IM Gliederungsblock, sondern nur "
        "daneben — beim Kopieren der Gliederung faellt sie damit weg")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

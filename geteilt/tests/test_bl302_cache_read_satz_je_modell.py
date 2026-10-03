#!/usr/bin/env python3
"""BL-302: Die Preistabelle kannte die 5.5er-Generation nicht — und der
Cache-Read-Satz galt als modelluebergreifend. Er ist es nicht mehr.

WAS FALSCH GERECHNET WURDE
    `claude-opus-5-5` lief ueber den laengsten Praefix als `claude-opus-5`:
    Input 5,00 statt 4,00 USD je Mio Token (+25 %), Output entsprechend, und
    Cache-Reads zum 0,1-Fachen von 5,00 = 0,50 statt 0,20 USD (+150 %). Claude
    Opus 5.5 liest zum 0,05-Fachen, Claude Fable 5.1 und Mythos 5.1 zum
    0,025-Fachen; die anderen Modelle zum 0,1-Fachen.

WARUM DAS SCHWER WIEGT
    Interaktive Architekten-Sitzungen laufen auf dem starken Modell, und in
    einer langen Sitzung sind Cache-Reads die mit Abstand groesste Menge
    (`BL-252`: 152,3 Mio in EINER Sitzung). `sitzung-messen` rechnete eine
    Sitzung auf Opus 5.5 damit um ein Mehrfaches zu teuer. Und es gibt fuer
    interaktive Sitzungen KEIN abgerechnetes Log, an dem die Selbsteichung den
    Fehler haette sehen koennen — die Rollen laufen auf Sonnet, wo Satz und
    Faktor zufaellig stimmten.

GEFUNDEN beim Bauen von BL-264: Die Modell-Anzeige liest an der Preistabelle
ab, welche Version einer Familie die neueste ist — und dort fehlte sie.
"""
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

for _tools in (Path(__file__).resolve().parents[2] / "geteilt" / "tools",
               kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

MIO = 1_000_000


def _kuebel(**werte):
    k = kosten._tokenkuebel()
    k.update(werte)
    return k


@pytest.mark.parametrize("modell,preis", [
    ("claude-opus-5-5", 4.00),
    ("claude-opus-5-5-20261001", 4.00),
    ("anthropic.claude-opus-5-5", 4.00),
    ("claude-opus-5", 5.00),
    ("claude-sonnet-5-5", 2.00),
    ("claude-sonnet-5", 2.00),
    ("claude-fable-5-1", 10.00),
    ("claude-haiku-4-5", 1.00),
])
def test_der_basispreis(modell, preis):
    assert kosten.modell_basispreis(modell) == preis


@pytest.mark.parametrize("modell,usd", [
    ("claude-opus-5-5", 0.20),    # 0,05 x 4,00
    ("claude-fable-5-1", 0.25),   # 0,025 x 10,00
    ("claude-mythos-5-1", 0.25),
    ("claude-opus-5", 0.50),      # 0,1 x 5,00 — unveraendert
    ("claude-sonnet-5-5", 0.20),  # 0,1 x 2,00
    ("claude-fable-5", 1.00),     # Fable 5 liest zum 0,1-Fachen
])
def test_eine_mio_cache_reads(modell, usd):
    k = _kuebel(cache_read=MIO)
    assert kosten.kosten_aus_tokens(k, kosten.modell_basispreis(modell),
                                    modell) == pytest.approx(usd)


def test_ohne_modell_gilt_der_allgemeine_satz():
    """Die Aufrufer ohne Modell (Eichrechnungen mit Basispreis 1,0 in alten
    Tests) behalten ihr Ergebnis."""
    k = _kuebel(cache_read=MIO)
    assert kosten.kosten_aus_tokens(k, 1.0) == pytest.approx(0.10)


def test_eine_lange_opus_5_5_sitzung(tmp_path):
    """Die Groessenordnung des Fehlers an einer Sitzung wie im Feld: wenig
    Input und Output, 150 Mio Cache-Reads."""
    k = _kuebel(input=200_000, output=400_000, cache_read=150 * MIO,
                cache_write_1h=2 * MIO)
    gesamt, _, unbekannt = kosten.sitzung_kosten({"claude-opus-5-5": k})
    assert not unbekannt
    erwartet = (0.2 * 4.00 + 0.4 * 20.00 + 150 * 0.20 + 2 * 8.00)
    assert gesamt == pytest.approx(erwartet)
    alt = (0.2 * 5.00 + 0.4 * 25.00 + 150 * 0.50 + 2 * 10.00)
    assert alt > 1.9 * gesamt, (
        "Vorbedingung des Belegs: der alte Satz lag bei einer solchen Sitzung "
        "beim knapp Doppelten (106,00 gegen 54,80 USD)")


def test_die_eichung_reproduziert_einen_opus_5_5_lauf(tmp_path):
    """Ein headless-Lauf auf Opus 5.5 mit dem abgerechneten Betrag, den die
    richtigen Saetze ergeben, darf die Selbsteichung nicht anschlagen — und
    der implizite Satz muss 4,00 sein, nicht 2,4 oder 5,0."""
    nutzung = {"inputTokens": 1000, "outputTokens": 20000,
               "cacheReadInputTokens": 3_000_000,
               "cacheCreationInputTokens": 100_000}
    import json
    gemeldet = (1000 * 4.00 + 20000 * 20.00 + 3_000_000 * 0.20
                + 100_000 * 5.00) / MIO      # Cache-Write als 5m
    log = tmp_path / "axel-HM-1-20261003-100000.json"
    log.write_text(json.dumps({"total_cost_usd": gemeldet,
                               "modelUsage": {"claude-opus-5-5": nutzung}}),
                   encoding="utf-8")
    saetze = kosten.preis_diagnose([str(log)])
    lo, hi, tabelle, _ = saetze["claude-opus-5-5"]
    assert tabelle == 4.00
    assert lo == pytest.approx(4.00, rel=1e-6) or hi == pytest.approx(4.00, rel=1e-6)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

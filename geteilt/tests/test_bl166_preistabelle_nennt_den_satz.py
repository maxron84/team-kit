#!/usr/bin/env python3
"""BL-166: `claude-sonnet-5` stand mit 3.00 USD/Mio Input in der Tabelle —
dem Satz der Vorgänger-Generation.

WARUM DAS DIE MEHRHEIT ALLER TOKEN TRAF
    `sonnet` ist der Default aller Loop-Rollen (`TEAM_MODEL_LOOP`). Der
    falsche Satz betraf damit die **Mehrheit aller gemessenen Token** jeder
    Installation. Die Selbsteichung von `sitzung-messen` schlug daraufhin fehl
    — im meldenden Projekt in **9 von 9** abgerechneten Läufen, 25–33 %
    daneben — und das Werkzeug verweigerte mit Exit 2 regelkonform jede
    Buchung.

    **Das ist kein stiller Fehler**: Die Eichung tat genau, was sie soll. Der
    Schaden war, dass sie einen Betreiber im Abo vollständig blockierte, bis
    er den Preis von Hand nachzog.

DER WICHTIGERE TEIL IST NICHT DER WERT
    Die Preistabelle veraltet **strukturell** — sie beschreibt fremde Preise
    und ist der einzige Ort, an dem das Kit eine Zahl führt, die außerhalb
    seiner Kontrolle veraltet. Ein Kit, das sie als Konstante führt, verlangt
    von jedem Betreiber, sie zu pflegen, ohne ihm zu sagen, wann — und ohne zu
    sagen, welche Zeile.

    Die Eichung weiß bereits, dass etwas nicht stimmt. Jetzt sagt sie auch,
    **welcher** Satz wie weit danebenliegt. Ein Werkzeug, das einen Fehler
    erkennt und ihn nicht benennen kann, verschiebt die Arbeit nur.

WARUM DIE DIAGNOSE NUR EINMODELL-LÄUFE LIEST
    Trägt ein Log zwei Modelle, ist die Aufteilung des abgerechneten Betrags
    auf die beiden Sätze unterbestimmt — jede Zuweisung wäre geraten. Eine
    geratene Zahl ist hier genau der Fehler, den `BL-141` abträgt: Sie sieht
    aus wie eine Messung.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import kit_pfad  # noqa: E402

WERKZEUG = kit_pfad("tools", "kosten.py")

pytestmark = pytest.mark.skipif(
    not WERKZEUG.is_file(), reason="kosten.py liegt in dieser Ablage nicht")

sys.path.insert(0, str(WERKZEUG.parent))


def _kosten():
    import importlib
    return importlib.reload(importlib.import_module("kosten"))


# Die Sätze, wie der Anbieter sie führt (USD je 1 Mio Input-Token). Diese
# Zahlen sind der einzige Grund, warum die Eichung überhaupt urteilen kann —
# sie stehen hier als Zweitmeinung neben der Tabelle im Werkzeug.
SAETZE = {
    "claude-opus-5":    5.00,
    "claude-sonnet-5":  2.00,
    "claude-haiku-4-5": 1.00,
    "claude-fable-5":  10.00,
}


@pytest.mark.parametrize("modell,soll", sorted(SAETZE.items()))
def test_der_basispreis_stimmt(modell, soll):
    ist = _kosten().modell_basispreis(modell)
    assert ist == soll, (
        f"BL-166: {modell} steht mit {ist} in der Tabelle, abgerechnet wird "
        f"{soll}. Weil `sonnet` der Default aller Loop-Rollen ist, betrifft "
        "ein falscher Satz dort die Mehrheit aller gemessenen Token — und die "
        "Selbsteichung blockiert dann JEDE Buchung.")


def test_datierte_und_plattform_varianten_treffen_denselben_satz():
    """Längster Präfix gewinnt — sonst fällt eine Bedrock- oder datierte ID
    durch und die Eichung meldet 'unbekanntes Modell' statt eines Preises."""
    k = _kosten()
    for variante in ("claude-sonnet-5-20260101", "anthropic.claude-sonnet-5"):
        assert k.modell_basispreis(variante) == 2.00, variante


# --- Die Diagnose ------------------------------------------------------------


def _log(pfad, modell, gemeldet, input_tokens=1_000_000, output_tokens=0,
         cache_read=0, cache_write=0):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps({
        "total_cost_usd": gemeldet,
        "modelUsage": {modell: {
            "inputTokens": input_tokens, "outputTokens": output_tokens,
            "cacheReadInputTokens": cache_read,
            "cacheCreationInputTokens": cache_write}}}),
        encoding="utf-8", newline="\n")
    return pfad


def test_die_diagnose_nennt_modell_und_impliziten_satz(tmp_path):
    """Eine Million reine Input-Token für 2 USD heißen: 2 USD je Mio.

    Bewusst ohne Cache-Token: Dann ist die 5m/1h-Frage gegenstandslos, und die
    Spanne fällt auf einen Punkt zusammen — der Fall, an dem sich die Rechnung
    prüfen lässt, ohne über die Annahme zu streiten.
    """
    k = _kosten()
    _log(tmp_path / "a.json", "claude-sonnet-5", 2.00)
    d = k.preis_diagnose([str(tmp_path / "a.json")])
    assert "claude-sonnet-5" in d, d
    lo, hi, tabelle, n = d["claude-sonnet-5"]
    assert round(lo, 4) == round(hi, 4) == 2.00, (lo, hi)
    assert tabelle == 2.00 and n == 1


def test_die_diagnose_zeigt_auf_die_richtige_zeile(tmp_path):
    """Der eigentliche Ertrag: Bei zwei Modellen im Projekt muss die Diagnose
    das EINE nennen, dessen Satz veraltet ist — nicht beide."""
    k = _kosten()
    _log(tmp_path / "gut.json", "claude-opus-5", 5.00)
    _log(tmp_path / "schief.json", "claude-sonnet-5", 3.00)   # alter Satz
    d = k.preis_diagnose([str(tmp_path / "gut.json"),
                          str(tmp_path / "schief.json")])
    daneben = [m for m, (lo, hi, tab, _) in d.items()
               if tab is not None and not (lo <= tab <= hi)]
    assert daneben == ["claude-sonnet-5"], (
        f"Die Diagnose zeigt auf {daneben} statt auf claude-sonnet-5:\n{d}")


def test_zwei_modelle_in_EINEM_lauf_werden_nicht_geraten(tmp_path):
    """Die Zurückhaltung ist die Zusicherung.

    Trägt ein Log zwei Modelle, ist die Aufteilung des abgerechneten Betrags
    unterbestimmt. Eine geratene Zahl sähe aus wie eine Messung (`BL-141`).
    """
    k = _kosten()
    p = tmp_path / "gemischt.json"
    p.write_text(json.dumps({
        "total_cost_usd": 7.00,
        "modelUsage": {
            "claude-opus-5": {"inputTokens": 1_000_000, "outputTokens": 0,
                              "cacheReadInputTokens": 0,
                              "cacheCreationInputTokens": 0},
            "claude-sonnet-5": {"inputTokens": 1_000_000, "outputTokens": 0,
                                "cacheReadInputTokens": 0,
                                "cacheCreationInputTokens": 0}}}),
        encoding="utf-8", newline="\n")
    assert k.preis_diagnose([str(p)]) == {}, (
        "Aus einem Zweimodell-Lauf wurde ein Satz abgeleitet — das ist Raten.")


def test_ein_unbekanntes_modell_erzeugt_keine_falsche_gewissheit(tmp_path):
    """`modell_basispreis` gibt dort None, und None ist ein Ergebnis, kein
    Fehler — die Diagnose darf daraus keine Abweichung machen."""
    k = _kosten()
    _log(tmp_path / "neu.json", "claude-irgendwas-9", 4.00)
    d = k.preis_diagnose([str(tmp_path / "neu.json")])
    assert d["claude-irgendwas-9"][2] is None


def test_die_eichung_ist_mit_dem_richtigen_satz_gruen(tmp_path):
    """Die Gegenprobe, die BL-166 verlangt: ein Lauf mit abgerechnetem
    `sonnet` muss die Tabelle bestätigen, nicht widerlegen."""
    k = _kosten()
    _log(tmp_path / "a.json", "claude-sonnet-5", 2.00)
    befunde = k.preise_nachrechnen([str(tmp_path / "a.json")])
    assert befunde, "kein Eichpunkt erkannt"
    _, gemeldet, gerechnet, rel = befunde[0]
    assert rel <= k.PREIS_TOLERANZ, (
        f"Die Eichung schlägt an, obwohl der Satz stimmt: gemeldet "
        f"{gemeldet}, gerechnet {gerechnet}, {rel * 100:.1f} % daneben")


def test_der_alte_satz_wuerde_die_eichung_reissen(tmp_path):
    """Ohne diesen Fall bliebe offen, ob die Eichung überhaupt etwas absichert.

    Er stellt den Zustand von vor dem Fix nach — dieselbe Rechnung mit 3.00.
    """
    k = _kosten()
    _log(tmp_path / "a.json", "claude-sonnet-5", 2.00)
    k.PREIS_INPUT_USD_PRO_MTOK["claude-sonnet-5"] = 3.00
    try:
        _, _, _, rel = k.preise_nachrechnen([str(tmp_path / "a.json")])[0]
    finally:
        k.PREIS_INPUT_USD_PRO_MTOK["claude-sonnet-5"] = 2.00
    assert rel > k.PREIS_TOLERANZ, (
        "Der alte Satz geht durch die Eichung — dann sichert sie nichts.")
    assert round(rel, 2) == 0.50, (
        f"Erwartet sind 50 % Abweichung (3.00 statt 2.00), gemessen "
        f"{rel * 100:.1f} %")

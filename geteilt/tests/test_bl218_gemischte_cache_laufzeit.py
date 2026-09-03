#!/usr/bin/env python3
"""BL-218/BL-213: Der Eichwaechter meldete "Preistabelle stimmt nicht mehr" fuer
Laeufe, an denen die Preistabelle unschuldig war — und verbot damit RICHTIGE
Buchungen.

ZWEI MELDUNGEN, EINE STELLE, DIESELBE FEHLERRICHTUNG

    `Feld E`, 2026-08-30: "2 von 140 nachgerechneten Laeufen weichen ab"
    (1,2 % und 3,2 %), Exit 2, nach dem Briefing ein Buchungsverbot. Nach dem
    1h-Anteil aufgeloest ging beides exakt auf — 367 375 von 477 228 Token
    (77 %) bzw. 96 626 von 129 880 (74 %). Der Grund: `modelUsage` fuehrt die
    Cache-Erstellung als EINE Summe ohne 5m/1h-Aufteilung, die beiden Saetze
    unterscheiden sich (Faktor 2,00 gegen 1,25), und `preise_nachrechnen` nahm
    die bessere der beiden REINFORMEN. Ein Lauf mit GEMISCHTER Zusammensetzung
    liegt zwischen beiden und traf keine.

    `Feld B`, 2026-09-01: 103 von 104 Laeufen reproduzierten sich exakt, einer
    nicht — gemeldet wurde trotzdem eine Aussage ueber die TABELLE, und ihr
    Rat ("Tabelle nachziehen") haette 103 richtige Laeufe falsch gemacht.

    Beide Male dasselbe: Aus dem Verhalten einzelner Laeufe wurde auf die
    Tabelle geschlossen, und der Betrag, der verworfen wurde, stammt gar nicht
    aus dem Log, sondern aus dem TRANSKRIPT — das die Aufteilung getrennt
    fuehrt. Der Waechter hatte schlechtere Daten als die Zahl, die er verwarf.

WARUM DAS NICHT EIN SCHOENHEITSFEHLER IST
    Die Zahl waechst monoton: `logs_einsammeln()` liest auch das Archiv, ein
    einmal abweichender Altlauf bleibt fuer immer im Nenner. Aus "2 von 140"
    wird ueber die Zeit "10 von 300" — und irgendwann ist der Waechter
    dauerhaft rot. Dann verbietet er nicht mehr falsche Buchungen, sondern
    richtige, und wer ihn nicht abschaltet, hat die Wahl zwischen "gegen die
    Regel buchen" und "gar nicht buchen". Bauart BL-14.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

MODELL = "claude-sonnet-5"

# Ein Lauf in der Groessenordnung des Feldfalls: viel Cache-Erstellung, also
# genau die Gattung, bei der die 5m/1h-Frage ueberhaupt Gewicht hat.
NUTZUNG = {"inputTokens": 12_000, "outputTokens": 34_000,
           "cacheReadInputTokens": 2_900_000,
           "cacheCreationInputTokens": 477_228}


def _grenzen(nutzung=NUTZUNG, modell=MODELL):
    """(alles-5m, alles-1h) — die beiden Reinformen desselben Laufs."""
    preis = kosten.modell_basispreis(modell)
    return tuple(
        kosten.kosten_aus_tokens(kosten._modelusage_kuebel(nutzung, art), preis)
        for art in ("cache_write_5m", "cache_write_1h"))


def _gemischt(anteil_1h, nutzung=NUTZUNG, modell=MODELL):
    """Der abgerechnete Betrag eines Laufs, dessen Cache-Erstellung zu
    `anteil_1h` mit dem 1h-Satz gebucht wurde. Die Kosten sind im Anteil
    linear, also ist jede Mischung eine Konvexkombination."""
    lo, hi = _grenzen(nutzung, modell)
    return lo + anteil_1h * (hi - lo)


def _log(tmp_path, name, usd, nutzung=NUTZUNG, modell=MODELL):
    ordner = tmp_path / ".ralph-logs"
    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / name).write_text(
        json.dumps({"total_cost_usd": usd, "modelUsage": {modell: nutzung}}),
        encoding="utf-8")
    return ordner / name


def _rel(tmp_path):
    befunde = kosten.preise_nachrechnen(kosten.logs_einsammeln(str(tmp_path)))
    assert befunde, "der Lauf wurde gar nicht als Eichpunkt erkannt"
    return [b[3] for b in befunde]


# --- Der Fall aus dem Feld ---------------------------------------------------

@pytest.mark.parametrize("anteil", [0.74, 0.77, 0.25, 0.5])
def test_gemischter_lauf_ist_kein_befund(tmp_path, anteil):
    """Der Kern von BL-218. Vor dem Fix meldete jeder dieser Laeufe eine
    Abweichung, obwohl die Tabelle exakt stimmt."""
    _log(tmp_path, "stufe-57.json", _gemischt(anteil))
    schlimmste = max(_rel(tmp_path))
    assert schlimmste <= kosten.PREIS_TOLERANZ, (
        f"ein Lauf mit {anteil:.0%} 1h-Anteil wird als Abweichung gemeldet "
        f"({schlimmste * 100:.1f} %) — die Preistabelle ist dabei richtig. "
        "Geprueft werden muss das INTERVALL zwischen den beiden Reinformen, "
        "nicht die bessere von beiden.")


@pytest.mark.parametrize("anteil", [0.0, 1.0])
def test_die_reinformen_bleiben_exakt(tmp_path, anteil):
    """Gegenprobe nach unten: Das Intervall darf die scharfen Faelle nicht
    weicher machen — sie liegen auf seinem Rand."""
    _log(tmp_path, "stufe-1.json", _gemischt(anteil))
    assert max(_rel(tmp_path)) < 1e-9


def test_betrag_ausserhalb_des_intervalls_bleibt_ein_befund(tmp_path):
    """DIE Gegenprobe: Ein Waechter, der nichts mehr faengt, ist kein Fix.
    Ein um 20 % zu hoher Betrag liegt ausserhalb beider Grenzen."""
    _, hi = _grenzen()
    _log(tmp_path, "stufe-2.json", hi * 1.20)
    assert max(_rel(tmp_path)) > kosten.PREIS_TOLERANZ


def test_die_abweichung_misst_bis_zur_naechsten_grenze(tmp_path):
    """Nicht bis zur besseren Reinform, sondern bis zum Rand des Erklaerbaren
    — sonst uebertreibt die gemeldete Prozentzahl den Befund."""
    lo, _hi = _grenzen()
    _log(tmp_path, "stufe-3.json", lo * 0.90)
    befund = kosten.preise_nachrechnen(kosten.logs_einsammeln(str(tmp_path)))[0]
    assert befund[2] == pytest.approx(lo), \
        "gemeldet werden muss die naechstgelegene Grenze"
    assert befund[3] == pytest.approx(0.1 / 0.9, rel=1e-6)


# --- Streuung oder Versatz (BL-213) ------------------------------------------

def _messen(tmp_path):
    """`sitzung-messen` gegen ein Minimalprojekt, mit echtem Transkript."""
    transkript = tmp_path / "sitzung.jsonl"
    transkript.write_text(json.dumps({
        "type": "assistant", "uuid": "u1",
        "message": {"model": MODELL, "usage": {
            "input_tokens": 100, "output_tokens": 200,
            "cache_read_input_tokens": 0,
            "cache_creation": {"ephemeral_5m_input_tokens": 0,
                               "ephemeral_1h_input_tokens": 1000}}}}) + "\n",
        encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(kit_pfad("tools", "kosten.py")),
         "sitzung-messen", str(transkript)],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        errors="replace")


def test_ein_einzelner_ausreisser_verbietet_die_buchung_nicht(tmp_path):
    """Der Feldfall aus `Feld B`: 103 von 104 Laeufen reproduzieren sich
    exakt. Ein falscher Tabellensatz traefe ALLE 104 — also ist die Tabelle
    nicht die Ursache, und die Zahl unten stammt ohnehin aus dem Transkript."""
    for i in range(20):
        _log(tmp_path, f"gut-{i}.json", _gemischt(0.5))
    _log(tmp_path, "kaputt.json", _grenzen()[1] * 1.33)

    r = _messen(tmp_path)
    assert "Preistabelle stimmt nicht mehr" not in r.stderr, (
        "BL-213: aus EINEM widerspruechlichen Log wird eine Aussage ueber die "
        f"TABELLE — und ihr Rat macht 20 richtige Laeufe falsch.\n{r.stderr}")
    assert "kaputt.json" in r.stderr, \
        "der verdaechtige Lauf muss trotzdem benannt werden"
    assert r.returncode == 0, (
        "eine Buchung, die mit der Tabelle nichts zu tun hat, darf nicht "
        f"blockiert werden.\n{r.stderr}")


def test_ein_durchgaengiger_versatz_verbietet_die_buchung_weiter(tmp_path):
    """Die Gegenrichtung, und der Fall aus BL-166/BL-211: Liegt die Tabelle
    wirklich daneben, weicht JEDER Lauf ab — dann ist das Buchungsverbot
    richtig und muss bleiben."""
    for i in range(20):
        _log(tmp_path, f"schief-{i}.json", _gemischt(0.5) * 1.33)

    r = _messen(tmp_path)
    assert "Preistabelle stimmt nicht mehr" in r.stderr, (
        "ein durchgaengiger Versatz muss weiter als Tabellenfehler gemeldet "
        f"werden.\n{r.stderr}")
    assert r.returncode == 2, "und die Zahl bleibt UNGEEICHT"


def test_saubere_laeufe_melden_weiter_geeicht(tmp_path):
    """Dritte Gegenprobe: Ohne Abweichung bleibt die Erfolgsmeldung."""
    for i in range(5):
        _log(tmp_path, f"gut-{i}.json", _gemischt(0.3))
    r = _messen(tmp_path)
    assert "Preistabelle geeicht" in r.stdout, r.stdout + r.stderr
    assert r.returncode == 0


# --- Der Widerspruch, der bisher stumm in der Ausgabe stand ------------------

def test_preis_versatz_folgt_der_rueckrechnung_nicht_der_zahl(tmp_path):
    """`preis_diagnose` rechnet den impliziten Satz aus den Einmodell-Laeufen
    zurueck. Deckt die belegte Spanne den Tabellenwert, ist die Tabelle nicht
    die Ursache — genau dieser Widerspruch stand im Feld stumm neben der
    Behauptung 'Preistabelle stimmt nicht mehr'."""
    for i in range(20):
        _log(tmp_path, f"gut-{i}.json", _gemischt(0.5))
    _log(tmp_path, "kaputt.json", _grenzen()[1] * 1.33)
    logs = kosten.logs_einsammeln(str(tmp_path))
    befunde = kosten.preise_nachrechnen(logs)
    abweichend = [b for b in befunde if b[3] > kosten.PREIS_TOLERANZ]
    assert len(abweichend) == 1
    versatz, modelle = kosten.preis_versatz(logs, abweichend, len(befunde))
    assert versatz is False and modelle == []

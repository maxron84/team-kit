#!/usr/bin/env python3
"""BL-211: Ein zentraler Preis fuer alle Installationen — und im Feld war er
fuer zwei Projekte gleichzeitig nicht richtig.

WAS IM FELD PASSIERT IST
    `BL-166` hat den `claude-sonnet-5`-Satz von 3.00 auf 2.00 gesenkt, weil
    die Selbsteichung in einem Projekt in 9 von 9 Laeufen fehlschlug. In einem
    ZWEITEN Projekt weichen mit demselben Satz **78 von 79** abgerechneten
    Laeufen um **33,3 %** ab — die Selbsteichung verweigert dort regelkonform
    JEDE Architekten-Buchung.

    Die Abweichung ist nicht gestreut, sondern ein konstanter Faktor: Beide
    Felder rechnen gegen verschiedene Vertraege ab, und beide haben recht. Wer
    den Satz im Kit zurueckdreht, dreht ihn dem ersten Projekt kaputt.

    Eine zentrale Zahl kann das nicht aufloesen. `TEAM_PREISE` ist die einzige
    der drei vorgeschlagenen Richtungen, die beide Felder gleichzeitig bedient,
    ohne dass eines auf den naechsten Kit-Entscheid wartet.

ABGRENZUNG, DIE MITGEPRUEFT WIRD
    `TEAM_PREISE` ist fuer einen durchgaengigen VERSATZ da, nicht fuer einen
    Ausreisser. Ein einzelnes widerspruechliches Log sagt nichts ueber die
    Tabelle (`BL-213`/`BL-218`) und wird hier nicht ausgeglichen — sonst waere
    der Schalter ein leiser Weg, einen Waechter stumm zu stellen.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if Path(_tools).is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402


def _mit(wert, aufruf):
    alt = os.environ.get("TEAM_PREISE")
    os.environ["TEAM_PREISE"] = wert
    try:
        return aufruf()
    finally:
        if alt is None:
            os.environ.pop("TEAM_PREISE", None)
        else:
            os.environ["TEAM_PREISE"] = alt


def test_ohne_uebersteuerung_gilt_die_kit_tabelle():
    """Die Gegenprobe zuerst: Der Schalter darf nichts aendern, solange er
    leer ist — sonst waere er ein stiller Eingriff in jede Installation."""
    assert kosten.modell_basispreis("claude-sonnet-5") == 2.00
    assert _mit("", lambda: kosten.modell_basispreis("claude-sonnet-5")) == 2.00


def test_die_uebersteuerung_schlaegt_die_tabelle():
    """Der Feldfall: 3.00 statt der 2.00 aus BL-166."""
    assert _mit("claude-sonnet-5=3.00",
                lambda: kosten.modell_basispreis("claude-sonnet-5")) == 3.00


def test_sie_gilt_auch_fuer_datierte_und_bedrock_ids():
    """Dieselbe Praefix-Regel wie die Tabelle — sonst traegt sie genau bei den
    IDs nicht, die im Feld wirklich in den Logs stehen."""
    for mid in ("claude-sonnet-5-20260101", "anthropic.claude-sonnet-5"):
        assert _mit("claude-sonnet-5=3.00",
                    lambda: kosten.modell_basispreis(mid)) == 3.00, mid


def test_mehrere_eintraege_und_beide_trennzeichen():
    def probe():
        return (kosten.modell_basispreis("claude-sonnet-5"),
                kosten.modell_basispreis("claude-opus-5"))
    assert _mit("claude-sonnet-5=3.00 claude-opus-5=7.50", probe) == (3.00, 7.50)
    assert _mit("claude-sonnet-5=3.00,claude-opus-5=7.50", probe) == (3.00, 7.50)


def test_ein_fremdes_modell_bleibt_unbekannt():
    """None ist ein Ergebnis, kein Fehler — der Schalter darf daraus keinen
    geratenen Preis machen (BL-141)."""
    assert _mit("claude-sonnet-5=3.00",
                lambda: kosten.modell_basispreis("gibt-es-nicht")) is None


@pytest.mark.parametrize("murks", ["claude-sonnet-5", "claude-sonnet-5=",
                                   "=3.00", "claude-sonnet-5=abc",
                                   "claude-sonnet-5=-1", "claude-sonnet-5=0"])
def test_ein_unlesbarer_eintrag_wird_gemeldet_statt_still_ignoriert(murks, capsys):
    """Still ignorieren waere die Fehlerrichtung von BL-160: Der Betreiber
    glaubt, sein Preis gelte, und die Eichung sagt ihm etwas ueber eine Zahl,
    die nie angekommen ist."""
    wert = _mit(murks, lambda: kosten.modell_basispreis("claude-sonnet-5"))
    assert wert == 2.00, "ein unlesbarer Eintrag darf NICHT gelten"
    assert "TEAM_PREISE" in capsys.readouterr().err, \
        "und er muss namentlich gemeldet werden"


def test_beide_konfigurationen_kennen_den_schalter():
    """Gleichstand der Bahnen: Ein Schalter, den nur eine Bahn kennt, ist
    dieselbe Gattung wie BL-155/BL-178."""
    for name in ("bash/entry/team.config.sh", "pwsh/entry/team.config.ps1"):
        pfad = REPO_ROOT / name
        if not pfad.is_file():
            continue
        text = pfad.read_text(encoding="utf-8-sig")
        assert "TEAM_PREISE" in text, f"{name} kennt TEAM_PREISE nicht"
        assert "BL-211" in text, f"{name} nennt die Herkunft nicht"


def test_die_eichung_nennt_den_satz_zum_eintragen(tmp_path):
    """BL-211, Richtung (3): Der Waechter sagt nicht nur, DASS die Tabelle
    danebenliegt, sondern welchen Wert der Bestand trifft — und wo er
    hingehoert."""
    import json
    ordner = tmp_path / ".ralph-logs"
    ordner.mkdir()
    nutzung = {"claude-sonnet-5": {"inputTokens": 1_000_000, "outputTokens": 0,
                                   "cacheReadInputTokens": 0,
                                   "cacheCreationInputTokens": 0}}
    for i in range(20):
        (ordner / f"lauf-{i}.json").write_text(
            json.dumps({"total_cost_usd": 3.00, "modelUsage": nutzung}),
            encoding="utf-8")
    transkript = tmp_path / "sitzung.jsonl"
    transkript.write_text(json.dumps({
        "type": "assistant", "uuid": "u1",
        "message": {"model": "claude-sonnet-5", "usage": {
            "input_tokens": 100, "output_tokens": 0,
            "cache_read_input_tokens": 0}}}) + "\n", encoding="utf-8")

    r = subprocess.run(
        [sys.executable, str(kit_pfad("tools", "kosten.py")),
         "sitzung-messen", str(transkript)],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env={k: v for k, v in os.environ.items()
                               if k != "TEAM_PREISE"})
    assert "Preistabelle stimmt nicht mehr" in r.stderr, (
        "ein durchgaengiger Versatz muss weiter als Tabellenfehler gelten:\n"
        f"{r.stderr}")
    assert "TEAM_PREISE=" in r.stderr, (
        "BL-211 (3): der Waechter nennt den Satz nicht, den der Bestand "
        f"trifft.\n{r.stderr}")
    assert "claude-sonnet-5=3.00" in r.stderr, r.stderr

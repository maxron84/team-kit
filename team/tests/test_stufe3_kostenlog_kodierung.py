"""Stufe 3: Die Kostenlogs muessen fuer Python lesbar bleiben — auf BEIDEN Bahnen.

WARUM DIESER TEST EXISTIERT
    Der PowerShell-Zweig schreibt die Kostenlogs, die anschliessend
    team/tools/kosten.py mit `json.load` liest. Damit haengen zwei
    Implementierungen an EINER Datei, und ihre Kodierung ist die Naht.

    Die naheliegende Schreibweise waere `& claude … > $Out` gewesen. Die
    Umlenkung schreibt aber mit der Standardkodierung der Sitzung: unter
    pwsh 7 heute UTF8NoBOM, unter Windows PowerShell 5.1 UTF-16LE, und ein
    `$PSDefaultParameterValues` im Benutzerprofil kann es jederzeit umstellen.

    Was daran teuer ist, ist nicht der Abbruch — es gibt keinen. Python bricht
    an einem BOM ab ("Unexpected UTF-8 BOM"), kosten.py FAENGT das ab und
    zaehlt die Datei still als 0.0000. Das ist exakt die Fehlerklasse aus
    BL-46 (Log von 0 Byte nach 47 Minuten Laufzeit) und BL-55 (Pro-Stufe-Cap
    umgehbar, weil ein teurer Fehlversuch nicht mitzaehlte): Eine bezahlte
    Stufe erscheint als die billigste der Kaskade, der Deckel bekommt auf sie
    keinen Griff, und niemand merkt es — bis jemand die Kostentabelle als
    Vergleichsband liest und eine Zahl fortschreibt, die eine halbe Stufe
    beschreibt.

    Deshalb wird die Kodierung in team/lib.psm1 ausdruecklich gesetzt
    (Team-ClaudeSchreiben) statt einer Voreinstellung ueberlassen — und
    deshalb steht sie hier unter Test.

WARUM UEBER DEN DRY-RUN GEPRUEFT WIRD
    TEAM_DRY_RUN=1 schreibt dasselbe JSON-Format ohne CLI-Aufruf und ohne
    Kosten. Der echte Pfad ist damit nicht abgedeckt — aber die Kodierung
    entsteht in beiden Zweigen an derselben Stelle, und ein Test, der Geld
    kostet, wird nicht gefahren.
"""
import json
from pathlib import Path

from conftest import RufCode

WURZEL = Path(__file__).resolve().parents[2]


def _dry_run_log(schale, tmp_path, ergebnis="fertig"):
    """Faehrt team_claude im Dry-Run und liefert den Pfad des Logs."""
    out = tmp_path / "stufe-1.json"
    lauf = schale.lauf(
        RufCode("team_claude", "ralph", "sonnet", str(out), "egal"),
        cwd=WURZEL,
        env={"TEAM_DRY_RUN": "1", "TEAM_DRY_RESULT": ergebnis},
    )
    assert lauf.returncode == 0, (
        f"team_claude endete mit {lauf.returncode}\n"
        f"stdout: {lauf.stdout}\nstderr: {lauf.stderr}")
    assert out.is_file(), f"kein Log geschrieben: {lauf.stderr}"
    return out


def test_kostenlog_traegt_kein_bom(schale, tmp_path):
    """Der Fund selbst. Ein BOM ist unsichtbar und kostet erst spaeter."""
    out = _dry_run_log(schale, tmp_path)
    roh = out.read_bytes()
    assert not roh.startswith(b"\xef\xbb\xbf"), (
        "UTF-8-BOM am Dateianfang — kosten.py bricht daran ab und zaehlt die "
        "Datei still als 0.0000 (Fehlerklasse BL-46/BL-55)")
    assert not roh.startswith(b"\xff\xfe") and not roh.startswith(b"\xfe\xff"), (
        "UTF-16-BOM — dieselbe Klasse, nur auffaelliger")


def test_kostenlog_ist_fuer_python_lesbar(schale, tmp_path):
    """Die Zusicherung, um die es wirklich geht: kosten.py liest genau so."""
    out = _dry_run_log(schale, tmp_path)
    with open(out, encoding="utf-8") as fh:
        daten = json.load(fh)
    assert daten["total_cost_usd"] == 0.01
    assert daten["is_error"] is False


def test_dry_result_kommt_unveraendert_an(schale, tmp_path):
    """Gegenprobe: Der Inhalt darf durch die Kodierung nicht verstuemmelt
    werden. Umlaute sind der Fall, an dem eine falsche Kodierung auffliegt —
    reines ASCII saehe in UTF-8 und Latin-1 gleich aus und bewiese nichts."""
    out = _dry_run_log(schale, tmp_path, ergebnis="Stufe grün, Prüfung erfüllt")
    with open(out, encoding="utf-8") as fh:
        daten = json.load(fh)
    assert daten["result"] == "Stufe grün, Prüfung erfüllt"

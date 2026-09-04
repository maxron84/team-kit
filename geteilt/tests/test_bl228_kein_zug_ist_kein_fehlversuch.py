#!/usr/bin/env python3
"""BL-228: Ein Netzfehler VOR dem ersten Token zaehlte als inhaltlicher
Fehlversuch — und schob den Fund Richtung Axel.

WIE DER FUND ENTSTAND
    Die Fixer-Rolle lief ohne gesetzten Firmenproxy. Abo-Aufruf UND
    API-Fallback endeten beide mit `Connection refused`, `num_turns: 0`,
    `total_cost_usd: 0.0000` — kein Modell hat den Fund je gesehen. Die Rolle
    wertete es trotzdem als inhaltlichen Fehlversuch: Rollback, und der
    Zaehler bekam einen Eintrag. Nach drei solchen Aussetzern staende der Fund
    auf „an Axel uebergeben" — die teuerste Rolle des Teams, angesetzt auf ein
    Problem, das nie ein Modell erreicht hat.

WARUM DIE UNTERSCHEIDUNG SCHON DA WAR, ABER ZU ENG
    Der Zweig fuer das Session-Limit (Exit 42) nimmt den Zaehler ausdruecklich
    aus, mit genau der richtigen Begruendung: „kein inhaltlicher Fehlversuch,
    die Rolle kam nie zum Zug." Ein `ConnectionRefused` mit 0 Turns und
    0.0000 USD ist dieselbe Klasse — er fiel nur in den generischen Exit 1.

WAS DIESER TEST PRUEFT
    Den gemeinsamen BEGRIFF statt eines dritten Textzweigs: `team_kein_zug`
    entscheidet an den beiden ZAHLEN, nicht am Fehlertext der CLI. Geprueft
    werden beide Richtungen — der Netzfehler wird erkannt, und ein Lauf, in
    dem ein Modell zum Zug kam, wird NICHT erkannt (sonst waere der Riegel ein
    Freibrief fuer jeden Fehlversuch, die Bauform, die BL-214 beim Abtragen
    eng ziehen musste).

    Dazu die Beweislast: Fehlt eine der beiden Zahlen, sind die Kosten
    unbekannt — dann bleibt es ein gewoehnlicher Fehlversuch (BL-46/BL-160).
"""
import json

from pathlib import Path

import pytest

from conftest import Ruf, Schreib, entrypoint_pfad, werkzeug_wert


def _repo(tmp_path, schale):
    repo = tmp_path / "repo"
    (repo / "team").mkdir(parents=True)
    schale.lib_kopieren(repo)
    schale.config_schreiben(repo, {
        "TEAM_DOMAENEN": "produkt",
        "TEAM_PRODUKTIVCODE": "src/",
        "TEAM_TEST_ORDNER": "tests/",
        "TEAM_PLAN_ORDNER": "plans/",
        "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
        "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
    })
    return repo


def _urteil(schale, repo, logs):
    """Schreibt die Logs und fragt team_kein_zug — Rueckgabe: Exit des Laufs.

    0 = „kein Modell kam zum Zug", 1 = gewoehnlicher Fehlversuch.
    """
    schritte = [Schreib(name, inhalt) for name, inhalt in logs]
    schritte.append(Ruf("team_kein_zug", *[name for name, _ in logs]))
    ergebnis = schale.lauf(schritte, cwd=repo,
                           lib=repo / "team" / schale.lib_name)
    return ergebnis.returncode


NETZFEHLER = json.dumps({"is_error": True, "num_turns": 0,
                         "total_cost_usd": 0.0,
                         "result": "API Error: Connection refused"}) + "\n"
GELAUFEN = json.dumps({"is_error": True, "num_turns": 12,
                       "total_cost_usd": 0.7431,
                       "result": "kein Promise"}) + "\n"


def test_netzfehler_vor_dem_ersten_token_ist_kein_zug(tmp_path, schale):
    """Der Fund selbst — 0 Turns, 0.0000 USD."""
    repo = _repo(tmp_path, schale)
    assert _urteil(schale, repo, [("abo.json", NETZFEHLER)]) == 0


def test_beide_versuche_ohne_zug(tmp_path, schale):
    """Der Feldfall: Abo-Aufruf UND API-Fallback endeten beide so."""
    repo = _repo(tmp_path, schale)
    assert _urteil(schale, repo, [("abo.json", NETZFEHLER),
                                  ("abo-api-fallback.json", NETZFEHLER)]) == 0


def test_ein_versuch_mit_zug_zaehlt_normal(tmp_path, schale):
    """Die wichtigste Gegenprobe: Kam in EINEM der Versuche ein Modell zum
    Zug, ist der Fehlversuch ein Fehlversuch. Sonst waere der Riegel ein
    Freibrief — genau die Bauform, die BL-214 eng ziehen musste."""
    repo = _repo(tmp_path, schale)
    assert _urteil(schale, repo, [("abo.json", NETZFEHLER),
                                  ("abo-api-fallback.json", GELAUFEN)]) == 1


def test_gewoehnlicher_fehlversuch_bleibt_einer(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    assert _urteil(schale, repo, [("abo.json", GELAUFEN)]) == 1


def test_fehlende_turns_zahl_bleibt_fehlversuch(tmp_path, schale):
    """Beweislast statt Vermutung: Der Ersatzzettel eines abgeschnittenen Logs
    (BL-46) kennt die Kosten NICHT. Unbekannt ist nicht null."""
    repo = _repo(tmp_path, schale)
    ohne = json.dumps({"is_error": True, "total_cost_usd": 0.0}) + "\n"
    assert _urteil(schale, repo, [("abo.json", ohne)]) == 1


def test_kaputtes_log_bleibt_fehlversuch(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    assert _urteil(schale, repo, [("abo.json", "{abgeschnitten")]) == 1


def test_ohne_logs_kein_freibrief(tmp_path, schale):
    """Kein Log heisst kein Beleg — und damit kein Freispruch."""
    repo = _repo(tmp_path, schale)
    ergebnis = schale.lauf([Ruf("team_kein_zug")], cwd=repo,
                           lib=repo / "team" / schale.lib_name)
    assert ergebnis.returncode == 1


# --- Die Auswertung in der Rolle ------------------------------------------
# Der Begriff allein traegt nichts, solange frank ihn nicht liest. Geprueft
# wird an der QUELLE, weil ein echter Frank-Lauf einen bezahlten Modellaufruf
# braucht — dieselbe Bauart wie die Quelltextpruefungen in BL-208/BL-224.

FRANK = {"bash": ("frank.sh", '> "$ATTEMPTS_FILE"'),
         "pwsh": ("frank.ps1", "Set-Content -Path $attemptsFile")}


def _frank(bahn):
    name, _ = FRANK[bahn]
    pfad = Path(entrypoint_pfad(name))
    if not pfad.is_file():
        pytest.skip(f"{name} liegt in dieser Ablage nicht")
    return pfad.read_text(encoding="utf-8-sig")


@pytest.mark.parametrize("bahn", sorted(FRANK))
def test_frank_kennt_den_vierten_ausgang(bahn):
    name, _ = FRANK[bahn]
    assert "TEAM_LAST_KEIN_ZUG" in _frank(bahn), (
        f"{name} kennt den vierten Ausgang nicht — ein Netzfehler vor dem "
        "ersten Token zaehlt dort als inhaltlicher Fehlversuch (BL-228).")


@pytest.mark.parametrize("bahn", sorted(FRANK))
def test_der_riegel_steht_vor_dem_zaehler(bahn):
    """Die Reihenfolge ist der halbe Fix: Ein Riegel HINTER der Zeile, die den
    Zaehler fortschreibt, waere wirkungslos."""
    name, zaehlerzeile = FRANK[bahn]
    text = _frank(bahn)
    assert zaehlerzeile in text, (
        f"{name}: die Zeile, die den Versuchszaehler schreibt, sieht nicht "
        "mehr aus wie erwartet — dieser Test misst sonst nichts.")
    assert text.index("TEAM_LAST_KEIN_ZUG") < text.index(zaehlerzeile), (
        f"{name} fragt erst nach dem Zaehler, ob ueberhaupt ein Modell zum "
        "Zug kam (BL-228).")


@pytest.mark.parametrize("bahn", sorted(FRANK))
def test_der_netzfehler_zweig_zaehlt_nicht_und_eskaliert_nicht(bahn):
    """Im Zweig selbst darf nichts stehen, was den Zaehler doch schreibt oder
    an Axel uebergibt — und er muss die Rolle mit Exit 1 verlassen."""
    name, zaehlerzeile = FRANK[bahn]
    text = _frank(bahn)
    zweig = text[text.index("TEAM_LAST_KEIN_ZUG"):text.index(zaehlerzeile)]
    assert "exit 1" in zweig, (
        f"{name} verlaesst den Netzfehler-Zweig nicht mit Exit 1. Exit 0 waere "
        "ein gemeldeter Erfolg ohne Fix; ein eigener Ausgang, den die "
        "Vollautomatik nicht kennt, naehme der Stagnations-Bremse ihren Griff "
        "— bei totem Netz drehte sich die Fix-Phase dann endlos.")
    vor_exit = zweig[:zweig.index("exit 1")]
    assert zaehlerzeile not in vor_exit, (
        f"{name} schreibt den Versuchszaehler, obwohl kein Modell zum Zug kam.")
    assert "an Axel übergeben" not in vor_exit, (
        f"{name} eskaliert an Axel, obwohl kein Modell zum Zug kam.")

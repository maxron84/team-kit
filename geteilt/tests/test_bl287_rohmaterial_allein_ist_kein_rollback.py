#!/usr/bin/env python3
"""BL-287: Eine Aenderung NUR in der Rohmaterial-Zone meldete „zurueckgerollt
wurde nur der Grenzuebertritt" — zurueckgerollt wurde nichts.

WAS IM FELD PASSIERT IST (`Feld F`, 2026-09-27)
    Der Stakeholder legte waehrend eines Vollautomatik-Laufs, wie vorgesehen,
    ein Web-Clipping und eine Notiz in die Rohmaterial-Zone. Die Zonen-Pruefung
    aus `BL-263` erkannte das richtig und fasste nichts an. Bei Harry folgte
    trotzdem *„Guard-Uebergriff kassiert, Ergebnis zaehlt — … zurueckgerollt
    wurde nur der Grenzuebertritt"* — eine Zeile, die der Zeile davor
    (*„Nichts davon wurde angefasst"*) widerspricht. Genau das hat `BL-24` fuer
    die Vollzugsmeldung des Guards abgestellt: Sie darf nicht mehr behaupten,
    als geschehen ist. Fuenf solche Bloecke in einem Lauf, alle vom
    Stakeholder — eine Warnung, die bei normalem Gebrauch kommt, erzieht zum
    Ueberlesen. Und bei Axel wurde die Notiz des Stakeholders zur Haelfte der
    Begruendung eines gescheiterten Aufrufs.

WARUM
    `team_guard_verify` meldete „Pfad zurueckgerollt" und „nur die Zone hat
    sich geaendert" mit DEMSELBEN Rueckgabewert, und `team_guard_urteil` kannte
    fuer beides nur den Rollback-Text. Der Guard merkt sich jetzt, WAS er
    gefunden hat (`TEAM_GUARD_BEFUND`); der Rueckgabevertrag bleibt, weil eine
    Zahl statt eines Wahrheitswerts auf der pwsh-Bahn still gekippt waere
    (`if (-not 2)` ist falsch).
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import Ruf, RufMarke, Schreib, werkzeug_wert  # noqa: E402

WHITELIST = "^(tests/|plans/)"
ROLLBACK_TEXT = "zurückgerollt wurde nur der Grenzübertritt"
ZONEN_TEXT = "Rohmaterial-Zone verändert"


def _git(repo, *befehl):
    return subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout.strip()


def _repo(tmp_path, schale):
    repo = tmp_path / "repo"
    for ordner in ("team", "src", "tests", "plans", "raw"):
        (repo / ordner).mkdir(parents=True, exist_ok=True)
    schale.lib_kopieren(repo)
    schale.config_schreiben(repo, {
        "TEAM_DOMAENEN": "produkt", "TEAM_PRODUKTIVCODE": "src/",
        "TEAM_TEST_ORDNER": "tests/", "TEAM_PLAN_ORDNER": "plans/",
        "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
        "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
    })
    (repo / ".gitignore").write_text("/raw/\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "raw" / "notiz.md").write_text("Mitschrift\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        _git(repo, *befehl)
    return repo


def _runde(schale, repo, mutation, ergebnis="1"):
    """Guard-Runde wie in redteam.* und axel.*: Schnappschuss, Mutation,
    Abgleich, Urteil — in EINER Shell, weil der Befund dort lebt."""
    return schale.lauf(
        [Ruf("team_guard_begin"), *mutation,
         RufMarke("team_guard_verify", "harry", WHITELIST, marke="GUARD_OK"),
         RufMarke("team_guard_urteil", "harry", "1", ergebnis,
                  marke="RUNDE_ZAEHLT")],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)


def test_nur_die_zone_meldet_keinen_rollback(tmp_path, schale):
    """Der Fall aus dem Feld."""
    repo = _repo(tmp_path, schale)
    r = _runde(schale, repo, [Schreib("raw/notiz.md", "Mitschrift, weiter\n")])
    ausgabe = r.stdout + r.stderr
    assert "GUARD_OK" not in r.stdout, "Vorbedingung: die Zone wurde gemeldet"
    assert ROLLBACK_TEXT not in ausgabe, (
        f"{schale.name}: Das Urteil behauptet einen Rollback, den es nicht gab "
        f"(BL-287).\n{ausgabe}")
    assert ZONEN_TEXT in ausgabe, ausgabe
    assert "RUNDE_ZAEHLT" in r.stdout, (
        "Eine Aenderung des Stakeholders in seiner Zone darf die Runde nicht "
        "kosten.")
    assert (repo / "raw" / "notiz.md").read_text(encoding="utf-8") == \
        "Mitschrift, weiter\n", "Die Zone wird nie angefasst (BL-263)"


def test_auch_ohne_ergebnis_kostet_die_zone_die_runde_nicht(tmp_path, schale):
    """Axel: Fehlt das Ergebnis, ist das ein eigener Befund — die Notiz des
    Stakeholders darf nicht seine Begruendung werden."""
    repo = _repo(tmp_path, schale)
    r = _runde(schale, repo, [Schreib("raw/neu.md", "x\n")], ergebnis="0")
    assert "UND kein vollständiges Ergebnis" not in r.stdout + r.stderr, (
        r.stdout + r.stderr)


def test_ein_echter_uebergriff_meldet_weiter_den_rollback(tmp_path, schale):
    """Gegenrichtung: Wo wirklich zurueckgerollt wurde, bleibt der Text."""
    repo = _repo(tmp_path, schale)
    r = _runde(schale, repo, [Schreib("src/app.py", "x = 2\n")])
    assert ROLLBACK_TEXT in r.stdout + r.stderr, r.stdout + r.stderr
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "x = 1\n"


def test_zone_UND_uebergriff_meldet_den_rollback(tmp_path, schale):
    """Gemischt: Der Pfad wurde zurueckgerollt — dann stimmt der Rollback-Text,
    und die Zone steht im Guard-Text darueber als ausgenommen."""
    repo = _repo(tmp_path, schale)
    r = _runde(schale, repo, [Schreib("raw/notiz.md", "y\n"),
                              Schreib("src/app.py", "x = 3\n")])
    assert ROLLBACK_TEXT in r.stdout + r.stderr, r.stdout + r.stderr


def test_ohne_jede_aenderung_kein_befund(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    r = _runde(schale, repo, [])
    assert "GUARD_OK" in r.stdout and "RUNDE_ZAEHLT" in r.stdout, r.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

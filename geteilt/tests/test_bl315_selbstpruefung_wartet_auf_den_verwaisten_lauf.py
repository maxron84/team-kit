#!/usr/bin/env python3
"""BL-315: Exit 43 trotz Zwei-Schritt-Verfahren — und die Selbstpruefung gab
am verwaisten Testlauf auf, statt auf ihn zu warten.

WAS GEMELDET WURDE (`Feld B`, 2026-09-25, im Kit seit 2026-10-08)
    Ralph startete den Testlauf regelkonform im Hintergrund und dann die
    Warteschleife SELBST mit `run_in_background`; die Sitzung endete mit
    *„I'll wait for its completion notification"*. Der Loop meldete Exit 43,
    die Selbstpruefung sah den noch laufenden Test (`BL-207`) und meldete
    UNBEKANNT. Der verwaiste Lauf war danach gruen; quittiert hat ein Mensch.

PROGRAMM STATT PROMPT
    Die Meldung schlug vor, das Verbot im Briefing zu verschaerfen. Das steht
    jetzt auch da (`run_in_background` beim Namen) — aber das Warten ist genau
    der Schritt, den die Rolle nicht geschafft hat, und den kann der Loop
    selbst: Die Selbstpruefung wartet bis zur Frist auf das Ende des laufenden
    Verifikationslaufs und misst danach selbst. Erst wenn er dann noch laeuft,
    bleibt es bei UNBEKANNT.

    Dazu ein Beifang derselben Wurzel: Seit `BL-232` verifizieren die Stufen
    mit `TEAM_SMOKE_TEST_SCHNELL` — gesucht wurde aber nur nach
    `TEAM_SMOKE_TEST`. Der verwaiste Lauf einer Stufe blieb damit unsichtbar,
    und die Selbstpruefung stellte ihren eigenen daneben.
"""
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import Ruf, Schreib, Variable  # noqa: E402
import test_bl207_vordergrund_zeitlimit_und_paralleler_lauf as h  # noqa: E402

WURZEL = Path(__file__).resolve().parents[2]


def _warte_bis_er_laeuft(prozess):
    for _ in range(50):
        if prozess.poll() is None:
            return
        time.sleep(0.1)


def _pruefung(repo, schale, **env):
    umgebung = {"TEAM_SMOKE_TEST": h._smoke_befehl(schale),
                "TEAM_TEST_ORDNER": "tests/"}
    umgebung.update(env)
    return schale.lauf(
        [Schreib("src/modul.py", "y = 2\n"),
         Schreib("tests/test_stufe1_sache.py", "def test_x(): pass\n"),
         Ruf("team_quittung_selbstpruefung", "ralph", "1")],
        cwd=repo, lib=repo / "team" / schale.lib_name, env=umgebung)


def test_der_verwaiste_lauf_wird_abgewartet_und_dann_gemessen(tmp_path,
                                                               schale):
    """Der Feldfall, aufgeloest. Gegen den alten Stand gemessen: UNBEKANNT,
    nicht quittiert — obwohl der Baum gruen war."""
    h._verlange_prozesstabelle_mit_argumenten(schale)
    repo = h._projekt(tmp_path, schale, smoke_rc=0, dauer=6)
    prozess = h._hintergrundlauf(repo, schale)
    try:
        _warte_bis_er_laeuft(prozess)
        t0 = time.monotonic()
        r = _pruefung(repo, schale, TEAM_SELBSTPRUEFUNG_WARTEN="120")
        dauer = time.monotonic() - t0
    finally:
        prozess.kill()
        prozess.wait()
    assert r.returncode == 0, (
        "Die Selbstpruefung hat nicht auf den laufenden Verifikationslauf "
        f"gewartet und danach selbst gemessen.\n{r.stderr}")
    assert "Kit-BL-315" in r.stderr and "beendet" in r.stderr, r.stderr
    assert "UNBEKANNT" not in r.stderr, r.stderr
    assert dauer < 100, f"Gewartet wurde bis zur Frist statt bis zum Ende ({dauer:.0f} s)"


def test_nach_der_frist_bleibt_es_unbekannt(tmp_path, schale):
    """Die Grenze: Laeuft er nach der Frist noch, wird weiter nichts
    behauptet — ein Dauerlaeufer mit dem Befehl in der Kommandozeile darf die
    Selbstpruefung nicht endlos festhalten."""
    h._verlange_prozesstabelle_mit_argumenten(schale)
    repo = h._projekt(tmp_path, schale, smoke_rc=0, dauer=60)
    prozess = h._hintergrundlauf(repo, schale)
    try:
        _warte_bis_er_laeuft(prozess)
        r = _pruefung(repo, schale, TEAM_SELBSTPRUEFUNG_WARTEN="3")
    finally:
        prozess.kill()
        prozess.wait()
    assert r.returncode != 0
    assert "UNBEKANNT" in r.stderr and "Wartezeit immer noch" in r.stderr, r.stderr
    assert "ist ROT" not in r.stderr


def test_auch_der_schnelle_stufenbefehl_wird_erkannt(tmp_path, schale):
    """Beifang: Der verwaiste Lauf einer Stufe traegt seit BL-232 den
    SCHNELLEN Befehl. Gegen den alten Stand gemessen: nicht erkannt, die
    Selbstpruefung stellte ihren eigenen Lauf daneben und quittierte."""
    h._verlange_prozesstabelle_mit_argumenten(schale)
    repo = h._projekt(tmp_path, schale, smoke_rc=0, dauer=60)
    prozess = h._hintergrundlauf(repo, schale)
    try:
        _warte_bis_er_laeuft(prozess)
        r = _pruefung(repo, schale,
                      TEAM_SMOKE_TEST="ein-anderer-voller-befehl --alle",
                      TEAM_SMOKE_TEST_SCHNELL=h._smoke_befehl(schale),
                      TEAM_SELBSTPRUEFUNG_WARTEN="0")
    finally:
        prozess.kill()
        prozess.wait()
    assert r.returncode != 0, (
        "Der laufende Stufen-Befehl wurde nicht erkannt — die Selbstpruefung "
        f"hat einen zweiten Lauf danebengestellt.\n{r.stderr}")
    assert "UNBEKANNT" in r.stderr, r.stderr


# --- Der Wortlaut, beide Bahnen und die Vorlage ------------------------------

def test_der_baustein_nennt_das_werkzeugmerkmal(tmp_path, schale):
    """Was die Rolle liest. „Im Vordergrund" hat im Feld nicht gereicht: Das
    Modell hat es nicht als Verbot des Hintergrund-Schalters seines Werkzeugs
    gelesen."""
    lib = schale.lib_kopieren(tmp_path)
    r = schale.lauf([Variable("SMOKE_ZEILE"), Variable("SMOKE_SUFFIX")],
                    cwd=tmp_path, lib=lib,
                    env={"TEAM_SMOKE_TEST": "./smoke.sh"})
    assert r.returncode == 0, r.stderr
    assert r.stdout.count("run_in_background") == 2, (
        "SMOKE_ZEILE und SMOKE_SUFFIX nennen den Hintergrund-Schalter nicht "
        f"beim Namen:\n{r.stdout}")


def test_die_vorlage_nennt_es_auch():
    vorlage = WURZEL / "bootstrap" / "CLAUDE.md.vorlage"
    if not vorlage.is_file():
        pytest.skip("Die Regeldatei-VORLAGE liegt nur im Kit.")
    text = vorlage.read_text(encoding="utf-8")
    assert "run_in_background" in text and "Kit-BL-315" in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

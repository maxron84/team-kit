#!/usr/bin/env python3
"""BL-321: `kaskade_aus_plan` erkannte nur `ralph-kaskade-` — die Benennung
der Vorlage (`team-kaskade-`) fiel durch.

WAS GEMELDET WURDE (`Feld B`, 2026-10-08)
    Seit `BL-202` nennt die Regeldatei-Vorlage Pläne `team-kaskade-N-….md`.
    `PLAN_PRAEFIXE`, die Plan-Erkennung der Bibliotheken und `team-status`
    kennen beide Formen; `kosten.py kaskade_aus_plan()` suchte nur
    `ralph-kaskade-(\\d+)-` und lieferte für einen Plan nach neuer Benennung
    `None`. Der Kostenabschluss verlangte dann `--kaskade` von Hand.

WAS DARAN STILL WAR
    Nicht der Abschluss selbst — der fragt laut nach `--kaskade`. Still war
    die Gegenprobe aus `BL-220`: Sie hält eine übergebene Kaskadennummer gegen
    den Plan, und ohne Nummer aus dem Plan gibt es keinen Sollwert. Mit einem
    `team-kaskade-`-Plan buchte eine versehentlich übergebene STUFENnummer
    wieder anstandslos — genau der Feldfall, gegen den `BL-220` gebaut ist.
    Der letzte Fall unten hält das am lebenden Verb fest.
"""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

from conftest import kit_pfad

KOSTEN_PY = kit_pfad("tools", "kosten.py")
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _kosten():
    if not KOSTEN_PY.is_file():
        pytest.skip("kosten.py liegt hier nicht")
    spec = importlib.util.spec_from_file_location("kosten_bl321", KOSTEN_PY)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.mark.parametrize("zeiger", [
    "plans/ralph-kaskade-7-produkt.md",
    "plans/team-kaskade-7-produkt.md",
    "team-plans/team-kaskade-7-produkt.md",
])
def test_beide_praefixe_liefern_die_nummer(tmp_path, zeiger):
    """Gegen den alten Stand gemessen: Die zweite und dritte Zeile gaben
    None."""
    kosten = _kosten()
    (tmp_path / ".ralph-plan").write_text(zeiger + "\n", encoding="utf-8")
    assert kosten.kaskade_aus_plan(str(tmp_path)) == "7", (
        f"Aus {zeiger} wird keine Kaskadennummer abgeleitet — der "
        "Kostenabschluss verlangt dann --kaskade von Hand, und die Gegenprobe "
        "aus BL-220 hat keinen Sollwert.")


def test_die_praefixe_kommen_aus_einer_liste():
    """Die Ursache war eine zweite, verstreute Fassung der Liste. Wer den
    nächsten Präfix in PLAN_PRAEFIXE einträgt, muss ihn hier mitbekommen."""
    kosten = _kosten()
    assert "team-kaskade-" in kosten.PLAN_PRAEFIXE
    quelle = KOSTEN_PY.read_text(encoding="utf-8")
    rumpf = quelle.split("def kaskade_aus_plan", 1)[1].split("\ndef ", 1)[0]
    assert "PLAN_PRAEFIXE" in rumpf, (
        "kaskade_aus_plan baut seinen Regex nicht aus PLAN_PRAEFIXE — beim "
        "nächsten Präfix fällt es wieder durch.")
    assert '"ralph-kaskade-' not in rumpf and "'ralph-kaskade-" not in rumpf


@pytest.mark.parametrize("zeiger", [
    "plans/post-20-fixserie.md",     # benannte Kaskade: keine Nummer
    "plans/team-kaskade-x-ohne-nummer.md",
    "",
])
def test_ohne_nummer_wird_nicht_geraten(tmp_path, zeiger):
    """Die Gegenrichtung: Ein Fix, der immer etwas findet, wäre schlimmer als
    der Fehler — `None` ist hier die richtige Antwort, der Aufrufer fragt dann
    nach `--kaskade`."""
    kosten = _kosten()
    (tmp_path / ".ralph-plan").write_text(zeiger + "\n", encoding="utf-8")
    assert kosten.kaskade_aus_plan(str(tmp_path)) is None


def _projekt(tmp_path, planname):
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"]):
        subprocess.run(["git", "-C", str(tmp_path), *befehl], check=True,
                       capture_output=True)
    (tmp_path / "plans").mkdir()
    (tmp_path / "plans" / planname).write_text("# Plan\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "scharf"],
                   check=True, capture_output=True)
    (tmp_path / ".ralph-plan").write_text(f"plans/{planname}\n",
                                          encoding="utf-8")
    (tmp_path / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    logs = tmp_path / ".team-logs"
    logs.mkdir()
    (logs / "frank.json").write_text(json.dumps({"total_cost_usd": 1.25}),
                                     encoding="utf-8")
    return tmp_path


def _buche(repo, kaskade):
    return subprocess.run(
        [sys.executable, str(KOSTEN_PY), "rollen-abschluss",
         "--kaskade", kaskade, "--domaene", "produkt",
         "--logs", str(repo / ".team-logs"),
         "--pfad", str(repo / ".budget-ledger"), "--repo", str(repo)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))


def test_die_gegenprobe_aus_bl220_greift_auch_bei_neuer_benennung(tmp_path):
    """Der stille Teil des Fundes, am lebenden Verb: Plan 11, gebucht wird
    die Stufennummer 59. Gegen den alten Stand gemessen: Exit 0, zwei Zeilen
    unter einer Kaskade, die es nicht gibt."""
    if not KOSTEN_PY.is_file():
        pytest.skip("kosten.py liegt hier nicht")
    repo = _projekt(tmp_path, "team-kaskade-11-produkt.md")
    r = _buche(repo, "59")
    assert r.returncode != 0, (
        "Mit einem team-kaskade-Plan bucht eine falsche Kaskadennummer "
        f"anstandslos — die Gegenprobe aus BL-220 ist aus.\nstdout={r.stdout}")
    assert "Kit-BL-220" in r.stderr, r.stderr
    zeilen = [z for z in (repo / ".budget-ledger").read_text(
        encoding="utf-8").splitlines() if z and not z.startswith("#")]
    assert not zeilen, "eine abgebrochene Buchung darf keine Zeile hinterlassen"


def test_die_richtige_nummer_bucht_weiter(tmp_path):
    """Gegenprobe zur Gegenprobe: Die passende Nummer bucht wie bisher."""
    if not KOSTEN_PY.is_file():
        pytest.skip("kosten.py liegt hier nicht")
    repo = _projekt(tmp_path, "team-kaskade-11-produkt.md")
    r = _buche(repo, "11")
    assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

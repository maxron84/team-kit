#!/usr/bin/env python3
"""BL-325: Was ein Programm erst im LAUF zeigt, kannte das Kit nicht.

DER WUNSCH (Owner, geaeussert in `Feld F` am 2026-10-09)
    *„Debuglog-orientiertes Development … soll in Zukunft fuer alle Projekte
    dieser Art hervorgehoben werden … Handabnahmen durch den Stakeholder sollen
    moeglichst breitflaechig und effizient unterstuetzt werden … Der Mensch soll
    beobachten und bei Look and Feel … beratend taetig sein."* Und:
    Handabnahmen automatisieren, wo es geht (auch Android mit Emulator).

WAS GEBAUT IST
    - `TEAM_LAUFZEIT_BELEG` in beiden Konfigurationen (ein Wert statt einer
      zehnten Interviewfrage; ein Update traegt ihn leer nach, BL-311).
    - Gesetzt, bekommen Ralph und Frank zur Laufzeit die Auflage, Logzeilen
      samt Auswerteregel (Testdatei im ECHTEN Format, Mutation) mitzuliefern —
      ueber dieselben Bausteine wie die Zielstand-Pruefung (BL-300), weil ihre
      Briefings am 45-Zeilen-Limit liegen. Das Red Team bekommt eine eigene
      Fundklasse in seinen Auftrag.
    - Der Architekt: Belege je Stufe, Probe vor einer tragenden Annahme,
      Proben ohne den Menschen, Abnahme aus dem Log, Vorlage fuer
      Handabnahmen. Das Verfahren mit Feldbeispiel in doku/laufzeit-belege.md.

Leer bleibt alles, wie es war — die Gegenproben unten halten das fest.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import Ausgabe, Variable, kit_pfad  # noqa: E402

WURZEL = Path(__file__).resolve().parents[2]
BELEG = "Log der Engine unter logs/engine.log"


def _bausteine(tmp_path, schale, belege):
    lib = schale.lib_kopieren(tmp_path)
    env = {"TEAM_SMOKE_TEST": "./smoke.sh"}
    if belege:
        env["TEAM_LAUFZEIT_BELEG"] = belege
    r = schale.lauf([Variable("SMOKE_ZEILE"), Variable("SMOKE_SUFFIX")],
                    cwd=tmp_path, lib=lib, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _auftrag(tmp_path, schale, belege):
    lib = schale.lib_kopieren(tmp_path)
    env = {"TEAM_LAUFZEIT_BELEG": belege} if belege else {}
    r = schale.lauf([Ausgabe("team_redteam_auftrag", "Pruefe den Code.", "")],
                    cwd=tmp_path, lib=lib, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout


# --- Die bauenden Rollen ----------------------------------------------------

def test_gesetzt_bekommen_ralph_und_frank_die_auflage(tmp_path, schale):
    text = _bausteine(tmp_path, schale, BELEG)
    assert text.count("Kit-BL-325") == 2, (
        "SMOKE_ZEILE (Ralph) und SMOKE_SUFFIX (Frank) tragen die Auflage nicht "
        f"beide:\n{text}")
    for teil in (BELEG, "ECHTEN Logformat", "Mutation", "Look and Feel"):
        assert teil in text, f"'{teil}' fehlt:\n{text}"


def test_leer_bleibt_alles_wie_es_war(tmp_path, schale):
    assert "Kit-BL-325" not in _bausteine(tmp_path, schale, "")


def test_beide_bahnen_sagen_dasselbe(tmp_path):
    """Dieselbe Auflage auf beiden Bahnen — der Quelltext-Vergleich aus BL-112
    sieht nur Platzhalter, nicht den eingesetzten Text."""
    from conftest import (Schale, ueberspringe_ohne_beide_bahnen,
                          verlange_bash, verlange_pwsh)
    # Ein VERGLEICH: In einer einbahnigen Ablage gehoert der Uebersprung in
    # die Zeile "einbahnige Ablage", nicht unter "<bahn>-Bahn nicht
    # installiert" — die zaehlt Tests, die EINE Bahn fahren (BL-129). Mit dem
    # falschen Helfer stand der Rueckweg im nur-pwsh-Lauf dreimal statt
    # zweimal, und kit-test.sh Stufe 8 wurde rot.
    ueberspringe_ohne_beide_bahnen()
    verlange_bash()
    verlange_pwsh()
    texte = []
    for bahn in ("bash", "pwsh"):
        schale = Schale(bahn)
        if not schale.kit_lib.is_file():
            pytest.skip(f"{schale.lib_name} liegt hier nicht")
        ordner = tmp_path / bahn
        ordner.mkdir()
        texte.append(_auftrag(ordner, schale, BELEG).strip()
                     + "\n" + _bausteine(ordner, schale, BELEG))
    # Verglichen werden nur die Saetze aus BL-325 — der Rest der Bausteine
    # nennt den Interpreter der jeweiligen Bahn, und das ist dort richtig.
    muster = re.compile(r"(?:Laufzeit-Belege|LAUFZEIT-BELEGE) \(Kit-BL-325\):"
                        r".*?(?:nicht als erledigt\.|im echten Format\.)", re.S)
    saetze = [[re.sub(r"\s+", " ", s) for s in muster.findall(t)] for t in texte]
    assert len(saetze[0]) == 3, saetze[0]
    assert saetze[0] == saetze[1], f"bash:\n{texte[0]}\n\npwsh:\n{texte[1]}"


# --- Das Red Team -----------------------------------------------------------

def test_das_red_team_bekommt_die_fundklasse(tmp_path, schale):
    text = _auftrag(tmp_path, schale, BELEG)
    assert text.startswith("Pruefe den Code."), text
    for teil in ("Kit-BL-325", BELEG, "Eigene Fundklasse",
                 "nachgeahmte Testdatei"):
        assert teil in text, f"'{teil}' fehlt im Auftrag:\n{text}"


def test_ohne_wert_bleibt_der_auftrag_wie_er_war(tmp_path, schale):
    assert _auftrag(tmp_path, schale, "").strip() == "Pruefe den Code."


# --- Konfiguration, Briefing, Doku ------------------------------------------

@pytest.mark.parametrize("datei,muster", [
    ("bash/entry/team.config.sh", r'^TEAM_LAUFZEIT_BELEG="\$\{TEAM_LAUFZEIT_BELEG:-\}"$'),
    ("pwsh/entry/team.config.ps1", r"^\$TEAM_LAUFZEIT_BELEG = Team-Wert 'TEAM_LAUFZEIT_BELEG' ''$"),
])
def test_beide_vorlagen_tragen_den_wert_leer(datei, muster):
    pfad = WURZEL / datei
    if not pfad.is_file():
        pytest.skip("Die Konfigurations-VORLAGEN liegen nur im Kit.")
    assert re.search(muster, pfad.read_text(encoding="utf-8-sig"), re.M), (
        f"{datei}: TEAM_LAUFZEIT_BELEG fehlt oder ist vorbelegt — leer muss "
        "alles bleiben, wie es war.")


def test_der_architekt_plant_aus_dem_log():
    pfad = kit_pfad("prompts", "rolle-architekt.md")
    if not pfad.is_file():
        pytest.skip("rolle-architekt.md liegt hier nicht")
    text = pfad.read_text(encoding="utf-8")
    for teil in ("Kit-BL-325", "TEAM_LAUFZEIT_BELEG",
                 "**Die Abnahme belegt jeden Punkt aus dem Log**",
                 "**Was ohne den Menschen laufen kann, läuft ohne ihn:**",
                 "**Vorbereitung**", "**Schritte**", "**Worauf du schaust**",
                 "**Fragen**", "**Auswertung**", "höchstens zwei Nachproben"):
        assert teil in text, f"Das Architekten-Briefing nennt '{teil}' nicht."


def test_das_verfahren_steht_in_der_doku():
    pfad = WURZEL / "doku" / "laufzeit-belege.md"
    if not pfad.is_file():
        pytest.skip("doku/ liegt nur im Kit")
    text = pfad.read_text(encoding="utf-8")
    for teil in ("TEAM_LAUFZEIT_BELEG", "Vorlage: Handabnahme", "Feld F",
                 "Android", "adb logcat", "echten"):
        assert teil in text, f"doku/laufzeit-belege.md nennt '{teil}' nicht."
    readme = (WURZEL / "README.md").read_text(encoding="utf-8")
    assert "doku/laufzeit-belege.md" in readme, "Das README verlinkt das Kapitel nicht."


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

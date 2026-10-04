#!/usr/bin/env python3
"""BL-219, BL-243, BL-288, BL-300: Was bis hierher niemand pruefte — den Plan,
die Lesbarkeit, den Fix ausserhalb des Loops und das Ziel der Handpruefung.

BL-219 (`Feld E`, 2026-08-30)
    Den Plan des Architekten pruefte nichts: Die Stufen-Verifikation fragt
    "funktioniert es?", "ist es das Richtige?" fragte nur der Mensch, am Ende
    und aus dem Gedaechtnis. Jetzt traegt der Plankopf `Auftrag:` und
    `Vorbild:`, und Abschnitt 1 des Abschluss-Docs nimmt daran ab.

BL-243 (`Feld B`, der kleine Vorschlag)
    Rund 14.000 Zeilen korrekter Dokumente, und keiner konnte sie lesen. Jedes
    Abschluss-Doc beginnt jetzt mit zehn Saetzen fuer Menschen.

BL-288 (`Feld F`)
    6 von 45 Fixen ausserhalb des Loops hatten trotz gruenem Reproducer eine
    Luecke. Der Architekt liest jetzt mit drei Proben gegen.

BL-300 (`Feld E`)
    Vor einer Handpruefung lag noch der alte Bau auf dem Emulator. Der neue
    Platz `TEAM_ZIELSTAND_PRUEFUNG` haengt an einer Handlung: Die bauende Rolle
    ruft ihn nach dem Bauen, die Vollautomatik meldet ihn am Ende des Laufs.
"""
import re
from pathlib import Path

import pytest

import test_bl241_fixphase_hat_einen_eigenen_einstieg as v
from conftest import (Variable, kit_pfad, quelle, verlange_bash,
                      verlange_pwsh)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _lies(pfad):
    p = Path(pfad)
    if not p.is_file():
        pytest.skip(f"{p.name} liegt in dieser Ablage nicht")
    return p.read_text(encoding="utf-8-sig")


def _architekt():
    return _lies(kit_pfad("prompts", "rolle-architekt.md"))


def _erste(*kandidaten):
    """Die Vorlage im Kit, die gerenderte Datei im Projekt — nur fuer Dateien,
    die das Update mitnimmt (TEAM.md). Eine Projektdatei wie die CLAUDE.md
    laeuft ueber `conftest.quelle` (Kit-BL-307)."""
    for teile in kandidaten:
        p = REPO_ROOT.joinpath(*teile)
        if p.is_file():
            return p.read_text(encoding="utf-8-sig")
    pytest.skip(f"keine von {kandidaten} in dieser Ablage")


# --- BL-219: Auftrag, Vorbild, Abnahme ------------------------------------------

def test_der_plankopf_traegt_auftrag_und_vorbild():
    t = _architekt()
    kopf = t[t.index("So sieht der Kopf aus:"):]
    kopf = kopf[:kopf.index("```", kopf.index("```") + 3)]
    assert "**Auftrag:**" in kopf and "**Vorbild:**" in kopf, kopf
    assert re.search(r"^\s*RALPH_CAP=5$", kopf, re.M), (
        "Die Deckelzeile muss im Beispiel blank bleiben")


def test_die_abnahme_misst_am_auftrag_nicht_an_der_verifikation():
    t = _architekt()
    assert "Die Abnahme steht in Abschnitt 1" in t, (
        "BL-219: Das Briefing sagt nicht, wo und woran abgenommen wird")
    absatz = t[t.index("Die Abnahme steht in Abschnitt 1"):][:600]
    assert "Kit-BL-219" in absatz and "Frage an den Stakeholder" in absatz, absatz
    assert "ein Modell antwortet" in t.replace("\n   ", " "), (
        "Der Grund fuer die Frage vor dem Start fehlt")


def test_die_vorlage_des_abschluss_docs_hat_beide_stellen():
    # Die Vorlage, nicht die CLAUDE.md des Projekts: die ist Projektdatei und
    # bekommt neue Abschnitte von Hand (Kit-BL-307). Genau hier war der erste
    # Update-Selbsttest nach BL-243 im Feld rot.
    t = quelle("bootstrap/CLAUDE.md.vorlage").read_text(encoding="utf-8-sig")
    assert "## 0. Für Menschen" in t, "BL-243: Abschnitt 0 fehlt in der Vorlage"
    assert "ABNAHME" in t and "Kit-BL-219" in t, "BL-219: die Abnahme fehlt"


def test_die_modellstufe_folgt_dem_maschinellen_netz():
    t = _erste(("bootstrap", "TEAM.md"), ("TEAM.md",))
    assert "maschinelles Netz" in t, (
        "BL-219: Die Regel fuer die Modellstufe steht nicht in der "
        "Bedienanleitung")


# --- BL-243 (klein) ---------------------------------------------------------------

def test_fuer_menschen_steht_vorneweg():
    t = _architekt()
    assert re.search(r"vorneweg \*\*Für\s+Menschen\*\*", t), (
        "BL-243: Das Abschluss-Doc beginnt nicht mit dem Einstieg fuer Menschen")
    assert "zehn Sätze ohne Fachkürzel" in t and "Kit-BL-243" in t


# --- BL-288 -----------------------------------------------------------------------

def test_der_architekt_liest_mit_drei_proben_gegen():
    t = _architekt()
    for probe in ("**Gegenprobe**", "**Mutationsprobe**",
                  "**Probe an der Wirklichkeit**"):
        assert probe in t, f"BL-288: {probe} fehlt im Architekten-Briefing"
    assert "Kit-BL-288" in t
    assert re.search(r"\*\*jede\*\*\s+sichtbare\s+Zusage", t), (
        "BL-288: Die Anforderung ans Fundschreiben fehlt")


def test_frank_prueft_mit_echten_eingaben_und_bleibt_kurz():
    p = Path(kit_pfad("prompts", "rolle-frank.md"))
    t = _lies(p)
    assert "Eingaben aus echter Quelle" in t and "wie dokumentiert" in t, t
    assert len(t.splitlines()) <= 45, "Franks Briefing reisst das Limit (BL-265)"


# --- BL-300: die Zielstand-Pruefung ----------------------------------------------

def _bausteine(tmp_path, schale, **env):
    lib = schale.lib_kopieren(tmp_path)
    umgebung = {"TEAM_SMOKE_TEST": "./smoke.sh"}
    umgebung.update(env)
    r = schale.lauf([Variable("SMOKE_ZEILE"), Variable("SMOKE_SUFFIX")],
                    cwd=tmp_path, lib=lib, env=umgebung)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_die_bauenden_rollen_bekommen_die_zielstand_pruefung(tmp_path, schale):
    text = _bausteine(tmp_path, schale, TEAM_ZIELSTAND_PRUEFUNG="./ziel.sh")
    assert text.count("Zielstand-Prüfung nach jeder Änderung an baubarem "
                      "Code: ./ziel.sh") == 2, (
        f"{schale.name}: Ralph (SMOKE_ZEILE) und Frank (SMOKE_SUFFIX) muessen "
        f"die Pruefung beide bekommen (Kit-BL-300):\n{text}")
    assert "Kit-BL-300" in text


def test_ohne_zielstand_kein_satz(tmp_path, schale):
    """Gegenrichtung: Leer heisst aus — kein Satz ueber einen Befehl, den es
    nicht gibt."""
    assert "Zielstand" not in _bausteine(tmp_path, schale)


def test_beide_konfigurationen_kennen_den_platz():
    # Die Vorlagen: Die Konfiguration eines Projekts waechst von Hand nach —
    # das Update meldet den fehlenden Wert (BL-200), es traegt ihn nicht ein
    # (Kit-BL-307).
    for rel in ("bash/entry/team.config.sh", "pwsh/entry/team.config.ps1"):
        t = quelle(rel).read_text(encoding="utf-8-sig")
        assert "TEAM_ZIELSTAND_PRUEFUNG" in t, f"{rel} kennt den Platz nicht"


def _ziel(repo, bahn, code):
    if bahn == "bash":
        (repo / "ziel.sh").write_text(
            f"#!/usr/bin/env bash\necho ziel\nexit {code}\n", encoding="utf-8")
        (repo / "ziel.sh").chmod(0o755)
        return "./ziel.sh"
    (repo / "ziel.ps1").write_text(
        f"[Console]::Out.WriteLine('ziel')\nexit {code}\n", encoding="utf-8-sig")
    return "./ziel.ps1"


@pytest.mark.parametrize("code,erwartet", ((1, "Zielstand ROT"),
                                           (0, "✓ Zielstand")))
def test_bash_der_lauf_meldet_den_zielstand_am_ende(tmp_path, code, erwartet):
    verlange_bash()
    repo = v._bash_projekt(tmp_path)
    r = v._bash(repo, "fixphase.sh",
                TEAM_ZIELSTAND_PRUEFUNG=_ziel(repo, "bash", code))
    aus = r.stdout + r.stderr
    assert erwartet in aus, aus
    assert r.returncode == 0, (
        f"Ein roter Zielstand ist ein Befund, kein Gate:\n{aus}")


def test_pwsh_der_lauf_meldet_den_zielstand_am_ende(tmp_path):
    verlange_pwsh()
    repo = v._pwsh_projekt(tmp_path)
    r = v._pwsh(repo, "fixphase.ps1",
                TEAM_ZIELSTAND_PRUEFUNG=_ziel(repo, "pwsh", 1))
    aus = r.stdout + r.stderr
    assert "Zielstand ROT" in aus and "Kit-BL-300" in aus, aus
    assert r.returncode == 0, aus


def test_ohne_zielstand_meldet_der_lauf_nichts(tmp_path):
    verlange_bash()
    repo = v._bash_projekt(tmp_path)
    r = v._bash(repo, "fixphase.sh")
    assert "Zielstand" not in r.stdout + r.stderr

#!/usr/bin/env python3
"""BL-172 und BL-185 — zwei Werte, die still das Falsche taten.

BL-172: DER FOKUS VERDRÄNGTE DEN GRUNDAUFTRAG
    `harry`/`marv` setzten den Auftrag über die Kette
    `${TEAM_REDTEAM_FOCUS:-${TEAM_REDTEAM_AUFTRAG_*:-<default>}}`. Ein
    gesetzter Fokus **ersetzte** den Grundauftrag also, er trat nicht neben
    ihn.

    Das kollidiert mit einer normativen Aussage der Regeldatei: Der Fokus wird
    bei **jeder** Kaskade gesetzt, auch bei reinen Produktivcode-Läufen, und
    er hat kein Verfallsdatum. Wird er pflichtgemäß immer gesetzt, greift der
    Grundauftrag **nie** — `TEAM_REDTEAM_AUFTRAG_*` war strukturell tot, und
    zwar genau die Werte, deren Ausfüllen der Kommentar in `team.config.*`
    ausdrücklich empfiehlt und mit einem Feldfall belegt.

    **Die beiden tragen verschiedene Zeiträume**, und darum brauchen beide
    Platz: Der Grundauftrag trägt, was sich *nicht* pro Kaskade ändert (etwa,
    dass in diesem Projekt personenbezogene Daten Minderjähriger in einer
    lokalen Datenbank liegen); der Fokus das, was *diese* Kaskade berührt.
    Beides zugleich zu brauchen ist der Normalfall, nicht die Ausnahme.

    **Der Schaden war leise:** Der Sweep läuft, findet etwas, und niemand
    sieht, dass die dauerhafte Kenntnis der Angriffsfläche in diesem Lauf gar
    nicht im Prompt stand.

    **Der Fix gehört an EINE der zwei Stellen, nicht an beide.**
    `TEAM_REDTEAM_FOCUS` steuert zweierlei: die Scope-Zeile (**wo** geprüft
    wird — dort ist Ersetzen richtig, ein Fokus schneidet den Umfang bewusst
    zu) und den Auftrag (**worauf** geachtet wird — dort war es falsch).

BL-185: EIN ÜBERSTEUERTES `TEAM_BUDGET_USD` VERWARF DIE EMPFEHLUNG STILL
    Gemeldet wurde nur, wenn eine Empfehlung den Deckel **anhebt**. Im Feld
    empfahl der Plan 34, gefahren wurde mit **26** — dem Wert der Vorkaskade,
    der in derselben interaktiven Shell weiterlebte. **Die falsche Zahl war
    nirgends zu sehen.** Folgenlos blieb es nur, weil der Lauf mit 18,20 unter
    beiden Deckeln blieb; ein 8 USD zu tiefer Deckel bricht mitten in der
    Fixphase ab und rollt bezahlte Arbeit zurück (`BL-32`-Muster).

    Der Mensch behält den Vorrang — er erfährt jetzt nur, dass er ihn ausübt.
    Der Unterschied der beiden Werte ist ihre **Lebensdauer**:
    `BUDGET_EMPFEHLUNG_USD` hängt am Plan und altert mit ihm, `TEAM_BUDGET_USD`
    ist eine Umgebungsvariable ohne Verfallsdatum.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (BASH, kit_pfad, ueberspringe_ohne_bahn,  # noqa: E402
                      verlange_pwsh)

REPO_ROOT = Path(__file__).resolve().parents[2]

GRUND = "Grundauftrag: personenbezogene Daten Minderjaehriger liegen lokal"
FOKUS = "Fokus dieser Kaskade: der neue Import-Pfad"
STANDARD = "Stackneutraler Default"


# --- Die Funktion, auf beiden Bahnen gefahren --------------------------------


def _bash_auftrag(grund, standard, fokus):
    if not BASH:
        pytest.skip("keine bash auf diesem Wirt")
    lib = kit_pfad("lib.sh")
    if not lib.is_file():
        pytest.skip("lib.sh liegt in dieser Ablage nicht")
    umgebung = dict(os.environ)
    umgebung["TEAM_PYTHON"] = umgebung.get("TEAM_PYTHON", sys.executable)
    if fokus is None:
        umgebung.pop("TEAM_REDTEAM_FOCUS", None)
    else:
        umgebung["TEAM_REDTEAM_FOCUS"] = fokus
    r = subprocess.run(
        [BASH, "-c",
         f'source "{lib.as_posix()}" 2>/dev/null; '
         f'team_redteam_auftrag "$1" "$2"', "_", grund, standard],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=umgebung)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _pwsh_auftrag(grund, standard, fokus):
    verlange_pwsh()
    lib = kit_pfad("lib.psm1")
    if not lib.is_file():
        pytest.skip("lib.psm1 liegt in dieser Ablage nicht")
    # Ueber den Syntaxbaum aus der ECHTEN Datei — kein nachgebauter Zwilling
    # (Lehre BL-142).
    setzen = ("$env:TEAM_REDTEAM_FOCUS = $null" if fokus is None
              else f"$env:TEAM_REDTEAM_FOCUS = '{fokus}'")
    skript = f"""
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           '{lib.as_posix()}', [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq 'team_redteam_auftrag' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw 'team_redteam_auftrag nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text
{setzen}
team_redteam_auftrag '{grund}' '{standard}'
"""
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", skript],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"
    return r.stdout


BAHNEN = {"bash": _bash_auftrag, "pwsh": _pwsh_auftrag}


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_fokus_und_grundauftrag_stehen_BEIDE_im_auftrag(bahn):
    """Die tragende Zusicherung — und die Gegenprobe, die der Eintrag verlangt.

    Beides zugleich zu brauchen ist der Normalfall: der Grundauftrag als
    stehender Rahmen, der Fokus als Schwerpunkt dieses Laufs.
    """
    ueberspringe_ohne_bahn(bahn)
    aus = BAHNEN[bahn](GRUND, STANDARD, FOKUS)
    assert GRUND in aus, (
        f"BL-172 ({bahn}): Der Grundauftrag fehlt — ein gesetzter Fokus "
        "verdrängt ihn wieder. Weil die Regel einen Fokus bei JEDER Kaskade "
        f"verlangt, wäre TEAM_REDTEAM_AUFTRAG_* damit tot.\n{aus}")
    assert FOKUS in aus, f"Der Fokus fehlt:\n{aus}"


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_ohne_fokus_steht_der_grundauftrag_allein_da(bahn):
    """Kein Zusatztext, wo nichts zuzusetzen ist — sonst trägt jeder Prompt
    eine leere Überschrift mit."""
    ueberspringe_ohne_bahn(bahn)
    aus = BAHNEN[bahn](GRUND, STANDARD, None)
    assert GRUND in aus and "SCHWERPUNKT" not in aus, aus


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_ohne_grundauftrag_traegt_der_stackneutrale_default(bahn):
    """Die dritte Stufe der Kette darf nicht verlorengehen."""
    ueberspringe_ohne_bahn(bahn)
    aus = BAHNEN[bahn]("", STANDARD, None)
    assert STANDARD in aus, aus


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_der_zusatz_sagt_dass_er_ZUSAETZLICH_gilt(bahn):
    """Ein angehängter Satz ohne diese Ansage liest sich wie eine Korrektur
    des Vorstehenden — und dann ersetzt der Fokus den Grundauftrag im Kopf der
    Instanz, auch wenn beide im Prompt stehen."""
    ueberspringe_ohne_bahn(bahn)
    aus = BAHNEN[bahn](GRUND, STANDARD, FOKUS)
    # `ae` mitgeprüft: Die Kit-Quelltexte schreiben Umlaute in Kommentaren und
    # Zeichenketten bewusst umschrieben (BL-113/BL-135), und diese Zeile geht
    # durch eine Prozessgrenze.
    assert re.search(r"zus(?:ä|ae|a)tzlich", aus, re.I), aus


# --- Die Scope-Zeile bleibt ERSETZEND ----------------------------------------


@pytest.mark.parametrize("datei", ["bash/redteam.sh", "pwsh/redteam.ps1"])
def test_die_scope_zeile_ersetzt_weiterhin(datei):
    """Der Fix gehört an EINE der zwei Stellen.

    Beim Umfang ist Ersetzen richtig: Ein Fokus schneidet den Prüfbereich
    bewusst zu, das ist seine Aufgabe. Wer hier auch verkettet, macht den
    Fokus wirkungslos.
    """
    p = REPO_ROOT / datei
    if not p.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    t = p.read_text(encoding="utf-8-sig")
    assert re.search(r"Fokus-Bereich", t), (
        f"{datei} baut die Scope-Zeile nicht mehr aus dem Fokus.")
    assert "team_redteam_auftrag" in t, (
        f"{datei} verkettet den Auftrag nicht — dann ist BL-172 zurück.")


@pytest.mark.parametrize("datei,var", [
    ("bash/entry/harry.sh", "TEAM_REDTEAM_AUFTRAG_HARRY"),
    ("bash/entry/marv.sh", "TEAM_REDTEAM_AUFTRAG_MARV"),
    ("pwsh/entry/harry.ps1", "TEAM_REDTEAM_AUFTRAG_HARRY"),
    ("pwsh/entry/marv.ps1", "TEAM_REDTEAM_AUFTRAG_MARV"),
])
def test_die_entrypoints_spielen_die_werte_nicht_mehr_gegeneinander(datei, var):
    """Der Riegel gegen den Rückbau: In den Entrypoints darf der Fokus nicht
    mehr VOR dem Grundauftrag stehen."""
    p = REPO_ROOT / datei
    if not p.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    ohne_kommentar = "\n".join(
        z for z in p.read_text(encoding="utf-8-sig").splitlines()
        if not z.lstrip().startswith("#"))
    assert "TEAM_REDTEAM_FOCUS" not in ohne_kommentar, (
        f"BL-172: {datei} liest den Fokus wieder selbst — dann ersetzt er den "
        "Grundauftrag, statt ihn zu ergänzen. Die Verkettung gehört in "
        "redteam.sh/.ps1, wo auch die Scope-Zeile steht.")
    assert var in ohne_kommentar, f"{datei} liest {var} nicht mehr."


# --- BL-185: der verworfene Deckel -------------------------------------------


def _bash_hinweis(gefahren, user_gesetzt, empfehlung):
    if not BASH:
        pytest.skip("keine bash auf diesem Wirt")
    lib = kit_pfad("lib.sh")
    if not lib.is_file():
        pytest.skip("lib.sh liegt in dieser Ablage nicht")
    r = subprocess.run(
        [BASH, "-c", f'source "{lib.as_posix()}" 2>/dev/null; '
                     f'team_budget_cap_hinweis "$1" "$2" "$3"',
         "_", str(gefahren), str(user_gesetzt), str(empfehlung)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "TEAM_PYTHON": os.environ.get("TEAM_PYTHON",
                                                         sys.executable)})
    assert r.returncode == 0, r.stderr
    return r.stdout


def _pwsh_hinweis(gefahren, user_gesetzt, empfehlung):
    verlange_pwsh()
    lib = kit_pfad("lib.psm1")
    if not lib.is_file():
        pytest.skip("lib.psm1 liegt in dieser Ablage nicht")
    skript = f"""
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           '{lib.as_posix()}', [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq 'team_budget_cap_hinweis' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw 'team_budget_cap_hinweis nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text
team_budget_cap_hinweis '{gefahren}' '{user_gesetzt}' '{empfehlung}'
"""
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", skript],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"
    return r.stdout


HINWEIS = {"bash": _bash_hinweis, "pwsh": _pwsh_hinweis}


@pytest.mark.parametrize("bahn", sorted(HINWEIS))
def test_der_feldfall_wird_gemeldet(bahn):
    """Plan empfiehlt 34, gefahren wird mit 26, weil TEAM_BUDGET_USD gesetzt
    ist — die Lage, in der die falsche Zahl nirgends zu sehen war."""
    ueberspringe_ohne_bahn(bahn)
    aus = HINWEIS[bahn](26, 1, 34)
    assert "34" in aus and "26" in aus, (
        f"BL-185 ({bahn}): Die verworfene Empfehlung wird nicht gemeldet.\n{aus}")
    assert "TEAM_BUDGET_USD" in aus, (
        f"Der Grund wird nicht genannt — dann sucht der Mensch ihn im Plan.\n{aus}")


@pytest.mark.parametrize("bahn", sorted(HINWEIS))
def test_auch_die_harmlose_richtung_wird_benannt(bahn):
    """Eine niedrigere Empfehlung ohne User-Wert ist kein Fehler, aber eine
    Abweichung — und wer sie nicht erklärt bekommt, hält sie für einen."""
    ueberspringe_ohne_bahn(bahn)
    aus = HINWEIS[bahn](26, 0, 20)
    assert "20" in aus and "senkt" in aus, aus


@pytest.mark.parametrize("bahn", sorted(HINWEIS))
@pytest.mark.parametrize("empfehlung", ["26", ""])
def test_ohne_abweichung_bleibt_es_still(bahn, empfehlung):
    """Ein Hinweis bei jedem Lauf erzieht zum Wegsehen (`BL-14`)."""
    ueberspringe_ohne_bahn(bahn)
    assert HINWEIS[bahn](26, 1, empfehlung).strip() == "", (
        "Gemeldet wird, wo nichts abweicht.")


@pytest.mark.parametrize("datei", ["bash/entry/vollautomatik.sh",
                                   "pwsh/entry/vollautomatik.ps1"])
def test_die_vollautomatik_ruft_den_hinweis_auch_auf(datei):
    """Ohne diese Zusicherung ließe sich der Test oben grün halten, während
    der Lauf weiter schweigt."""
    p = REPO_ROOT / datei
    if not p.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    assert "team_budget_cap_hinweis" in p.read_text(encoding="utf-8-sig"), (
        f"{datei} ruft den Hinweis nicht auf.")

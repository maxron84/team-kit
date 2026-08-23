#!/usr/bin/env python3
"""BL-149: Der Platzhalter war nicht leer — und alle Weichen pruefen nur auf leer.

WAS DAS IM FELD BEDEUTETE
    `team.config.*` kam mit der Vorbelegung
    `TEAM_SMOKE_TEST="TODO: noch keiner — Stufe 1 der ersten Kaskade"` aus dem
    Installer. Die Bibliothek unterscheidet "konfiguriert" von "nicht
    konfiguriert" aber ausschliesslich ueber leer/nicht-leer — fuer sie war
    der Satz ein KONFIGURIERTER BEFEHL. Drei Folgen, alle in Kaskade 1:

      1. SMOKE_ZEILE schrieb jeder bauenden Rolle in den Prompt: "Smoke-Test
         ausfuehren: TODO: noch keiner — Stufe 1 der ersten Kaskade — muss
         gruen sein", samt dem Nachsatz, ihn ja im Vordergrund auszufuehren.
      2. team_allowed_tools haengte `Bash(TODO: noch keiner — …)` in die
         Werkzeug-Allowlist des Red Teams.
      3. team_quittung_selbstpruefung fuehrte den Wert WOERTLICH aus. `TODO:`
         ist kein Befehl — Exit 127 — und die Selbstpruefung meldete
         "✗ … ist ROT". Der vierte Ausgang (BL-41) konnte in Stufe 1 damit NIE
         automatisch quittieren, obwohl genau diese Stufe die Aufgabe hat, den
         Smoke-Test ueberhaupt erst zu bauen.

    Der Kommentar unmittelbar ueber der Zeile sagte selbst: "Ist er LEER,
    lassen die Rollen den Smoke-Test-Schritt aus" — die Vorbelegung
    widersprach ihrer eigenen Dokumentation.

WARUM DAS NIEMANDEM AUFFIEL
    Der Fehler hat ein Zeitfenster von genau einer Kaskade pro Projekt. Sobald
    Stufe 1 einen echten Befehl eintraegt, ist er fuer immer unsichtbar; in
    einem laufenden Feldprojekt kann er gar nicht mehr auftreten. Getroffen
    wird ausschliesslich der Erstlauf — die Lage, in der am wenigsten
    Erfahrung im Projekt steckt, um eine unsinnige Prompt-Zeile als
    Werkzeugfehler zu erkennen.

    Dazu kam eine zweite Blindstelle, und sie steht schwarz auf weiss in
    `test_bl41_smoke_zeile_vordergrund.py`: Dessen Schlusskommentar erklaert
    den else-Zweig ("Kein Smoke-Test konfiguriert") fuer NICHT PRUEFBAR, weil
    eine Installation TEAM_SMOKE_TEST immer selbst setze. Das stimmte — und
    zwar genau WEGEN dieses Fehlers. Der Zweig, in dem der Fund sass, war der
    einzige, den niemand fuhr. Dieser Test faehrt ihn, in einer Ablage ohne
    team.config, also unabhaengig davon, was ein Projekt eingetragen hat.

WAS GEPRUEFT WIRD, UND WARUM IN DIESER AUFTEILUNG
    Der Fix hat zwei Haelften, und sie fangen verschiedene Rueckfaelle:

      * Die Vorbelegung ist leer (die Konfiguration bekommt eine EIGENE
        Platzhalter-Marke, SMOKE_TEST_KONFIG, statt der Prosa-Marke
        SMOKE_TEST). Das behebt den FALL.
      * Die Bibliothek behandelt einen mit `TODO` beginnenden Wert wie leer.
        Das behebt die KLASSE — ein Mensch traegt in eine leere Zeile gern
        selbst ein "TODO" ein, und Platzhalter dieser Sorte werden im Kit
        erfahrungsgemaess an anderer Stelle wieder eingefuehrt.

    Ohne die Gegenprobe waere beides gefaehrlich: Eine Weiche, die zu viel
    schluckt, macht aus einem konfigurierten Projekt ein unbewachtes. Deshalb
    faehrt jeder Fall auch mit einem ECHTEN Befehl.
"""
import re
import shutil
from pathlib import Path

import pytest

from conftest import Ausgabe, Variable, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

# Genau der Satz, der im Feld in den Prompts stand.
PLATZHALTER = "TODO: noch keiner — Stufe 1 der ersten Kaskade"
ECHT = "./smoke.sh"

# Zusammengesetzt, nicht geschrieben — dieselbe Vorsichtsmassnahme wie in
# test_bl131 und aus demselben Grund: kit-test.sh Schritt 3 durchsucht den
# AUSGELIEFERTEN Baum nach ungefuellten Platzhaltern, und dieser Test wird
# mitinstalliert. Stuenden die Marken hier woertlich, meldete der Selbsttest
# ihn als Fund — und haette recht.
#
# `"".join(...)` und nicht `"{" + "{" + …`: Die Addition von Literalen faltet
# der Compiler zu EINER Konstanten zusammen, und die steht dann woertlich im
# .pyc. Ein Methodenaufruf wird nicht gefaltet. (Genau daran ist der erste
# Versuch in test_bl131 gescheitert: im Quelltext sauber, im Bytecode nicht.)
MARKE_PROSA = "".join(("{{", "SMOKE_TEST", "}}"))
MARKE_KONFIG = "".join(("{{", "SMOKE_TEST_KONFIG", "}}"))


def _ablage_ohne_konfig(tmp_path, schale):
    """Wegwerf-Ablage mit der Bibliothek und OHNE team.config.

    Ohne Konfiguration entscheidet allein die Umgebung, was TEAM_SMOKE_TEST
    ist — der else-Zweig laesst sich damit erzwingen, egal ob dieser Test im
    Kit-Repo oder in einer Installation laeuft. Genau daran war der Versuch in
    test_bl41 gescheitert.
    """
    repo = tmp_path / "repo"
    (repo / "team").mkdir(parents=True)
    shutil.copy(schale.kit_lib, repo / "team" / schale.lib_name)
    return repo


def _lib(schale, repo):
    return repo / "team" / schale.lib_name


# ----------------------------------------------------------- die Prompt-Zeile
@pytest.mark.parametrize("wert,warum", [
    ("", "der else-Zweig selbst — bis BL-149 von keinem Test gefahren"),
    (PLATZHALTER, "der Feldfall: der Platzhalter aus dem Installer"),
    ("TODO", "die knappste Form, die ein Mensch selbst eintraegt"),
])
def test_ohne_befehl_meldet_die_prompt_zeile_den_offenen_punkt(
        tmp_path, schale, wert, warum):
    repo = _ablage_ohne_konfig(tmp_path, schale)
    fertig = schale.lauf(Variable("SMOKE_ZEILE"), cwd=repo,
                         lib=_lib(schale, repo),
                         env={"TEAM_SMOKE_TEST": wert})
    assert fertig.returncode == 0, fertig.stderr
    assert "Kein Smoke-Test konfiguriert" in fertig.stdout, (
        f"SMOKE_ZEILE meldet den offenen Punkt nicht ({warum}). Stattdessen "
        f"bekommt jede bauende Rolle diesen Satz in den Prompt:\n"
        f"{fertig.stdout}")
    assert "TODO" not in fertig.stdout, (
        "Der Platzhalter steht woertlich im Prompt der Rollen — genau BL-149.")


def test_ein_echter_befehl_kommt_weiterhin_in_die_prompt_zeile(tmp_path, schale):
    """Die Gegenprobe. Eine Weiche, die zu viel schluckt, macht aus einem
    konfigurierten Projekt ein unbewachtes — das waere schlimmer als der
    Fund."""
    repo = _ablage_ohne_konfig(tmp_path, schale)
    fertig = schale.lauf(Variable("SMOKE_ZEILE"), cwd=repo,
                         lib=_lib(schale, repo),
                         env={"TEAM_SMOKE_TEST": ECHT})
    assert fertig.returncode == 0, fertig.stderr
    assert ECHT in fertig.stdout and "Kein Smoke-Test" not in fertig.stdout, (
        f"Der konfigurierte Befehl kommt nicht mehr im Prompt an:\n"
        f"{fertig.stdout}")


def test_ein_befehl_der_nur_so_heisst_wird_nicht_geschluckt(tmp_path, schale):
    """Die zweite Gegenprobe: Die Weiche greift am PRAEFIX und
    grossgeschrieben. `./todo.sh` ist ein zulaessiger Pruefbefehl."""
    repo = _ablage_ohne_konfig(tmp_path, schale)
    fertig = schale.lauf(Variable("SMOKE_ZEILE"), cwd=repo,
                         lib=_lib(schale, repo),
                         env={"TEAM_SMOKE_TEST": "./todo.sh"})
    assert fertig.returncode == 0, fertig.stderr
    assert "./todo.sh" in fertig.stdout, (
        "Die Weiche hat einen echten Befehl geschluckt, weil sein Name mit "
        f"'todo' beginnt:\n{fertig.stdout}")


# ------------------------------------------------------ die Werkzeug-Allowlist
@pytest.mark.parametrize("wert", ["", PLATZHALTER, "TODO"])
def test_ohne_befehl_bleibt_die_allowlist_ohne_platzhalter(tmp_path, schale, wert):
    repo = _ablage_ohne_konfig(tmp_path, schale)
    fertig = schale.lauf(Ausgabe("team_allowed_tools", "redteam"), cwd=repo,
                         lib=_lib(schale, repo),
                         env={"TEAM_SMOKE_TEST": wert})
    assert fertig.returncode == 0, fertig.stderr
    assert "TODO" not in fertig.stdout, (
        "Das Red Team bekommt einen Platzhalter als erlaubtes Werkzeug — "
        f"genau BL-149:\n{fertig.stdout}")


def test_ein_echter_befehl_steht_weiterhin_in_der_allowlist(tmp_path, schale):
    repo = _ablage_ohne_konfig(tmp_path, schale)
    fertig = schale.lauf(Ausgabe("team_allowed_tools", "redteam"), cwd=repo,
                         lib=_lib(schale, repo),
                         env={"TEAM_SMOKE_TEST": ECHT})
    assert fertig.returncode == 0, fertig.stderr
    assert f"Bash({ECHT})" in fertig.stdout, (
        "Der konfigurierte Smoke-Test fehlt in der Allowlist — das Red Team "
        f"koennte ihn nicht mehr ausfuehren:\n{fertig.stdout}")


# ----------------------------------------------- die Vorbelegung des Installers
# Die Verhaltenstests oben pruefen die Bibliothek. Der FALL sass aber eine
# Ebene darueber, in dem, was der Installer in team.config.* schreibt — und
# eine Bibliothek, die TODO abfaengt, macht eine falsche Vorbelegung nur
# unsichtbar, nicht richtig.

KONFIG_VORLAGEN = ("bash/entry/team.config.sh", "pwsh/entry/team.config.ps1")
PROSA_VORLAGEN = ("bootstrap/CLAUDE.md.vorlage", "bootstrap/TEAM.md",
                  "bootstrap/roadmap-skizzen.md")


@pytest.mark.parametrize("rel", KONFIG_VORLAGEN)
def test_die_konfiguration_traegt_den_leeren_platzhalter(rel):
    datei = REPO_ROOT / rel
    if not datei.is_file():
        pytest.skip(f"{rel} nicht in dieser Ablage")
    text = datei.read_text(encoding="utf-8-sig")
    assert MARKE_KONFIG in text, (
        f"{rel} fuellt TEAM_SMOKE_TEST nicht aus {MARKE_KONFIG}. Damit haengt "
        f"die Vorbelegung wieder an {MARKE_PROSA}, und der traegt den "
        "TODO-Satz fuer die Prosa — genau BL-149.")
    assert MARKE_PROSA not in text, (
        f"{rel} benutzt noch {MARKE_PROSA}. Er wird mit dem TODO-Satz "
        "gefuellt, und der ist fuer jede Weiche ein konfigurierter Befehl.")


@pytest.mark.parametrize("rel", PROSA_VORLAGEN)
def test_die_prosa_behaelt_ihren_hinweis(rel):
    """Die Gegenrichtung: Der TODO-Satz ist nicht falsch, er stand nur am
    falschen Ort. In Regeltexten sagt er einem Menschen, was noch fehlt — wer
    ihn dort mitloescht, nimmt dem Erstlauf den einzigen Hinweis."""
    datei = REPO_ROOT / rel
    if not datei.is_file():
        pytest.skip(f"{rel} nicht in dieser Ablage")
    text = datei.read_text(encoding="utf-8-sig")
    assert MARKE_PROSA in text, (
        f"{rel} nennt den Smoke-Test nicht mehr ({MARKE_PROSA} fehlt). Der "
        "Hinweis fuer den Menschen ist damit weg.")


@pytest.mark.parametrize("rel,muster", [
    ("bash/install.sh", r'\("\{\{SMOKE_TEST_KONFIG\}\}", smoke\)'),
    ("pwsh/install.ps1", r"'\{\{SMOKE_TEST_KONFIG\}\}'\s*=\s*\$SmokeTest"),
])
def test_der_installer_fuellt_den_konfig_platzhalter_roh(rel, muster):
    """Der Konfig-Platzhalter darf keinen Ersatzwert bekommen.

    Ohne diese Zusicherung waere ein `or "TODO…"` an dieser Stelle ein
    stiller Rueckfall in den Feldfall — und er saehe im Diff aus wie eine
    Vereinheitlichung.
    """
    datei = REPO_ROOT / rel
    if not datei.is_file():
        pytest.skip(f"{rel} nicht in dieser Ablage")
    text = datei.read_text(encoding="utf-8-sig")
    treffer = re.findall(muster, text)
    assert treffer, (
        f"{rel} fuellt {MARKE_KONFIG} nicht mit dem ROHEN Wert. Ein "
        "Ersatzwert an dieser Stelle ist der Rueckfall in BL-149.")


def test_beide_bahnen_fuellen_gleich_oft():
    """install.sh hat ZWEI Fuell-Routinen (Erstinstallation und Update). BL-119
    hat gezeigt, wie teuer es ist, wenn nur eine davon einen Platzhalter
    kennt: Der Update-Pfad liess vier Platzhalter stehen, und die Datei war da
    und trotzdem halb fertig."""
    datei = REPO_ROOT / "bash/install.sh"
    if not datei.is_file():
        pytest.skip("install.sh nicht in dieser Ablage")
    text = datei.read_text(encoding="utf-8")
    fuellungen = len(re.findall(r'\("\{\{SMOKE_TEST_KONFIG\}\}", smoke\)', text))
    prosa = len(re.findall(r'\("\{\{SMOKE_TEST\}\}", smoke or ', text))
    assert fuellungen == prosa, (
        f"install.sh fuellt {MARKE_PROSA} {prosa}-mal, "
        f"{MARKE_KONFIG} aber {fuellungen}-mal. Eine der beiden "
        "Fuell-Routinen kennt den neuen Platzhalter nicht — sie laesst ihn "
        "stehen, und die Konfiguration ist da und trotzdem halb fertig "
        "(Bauart BL-119).")

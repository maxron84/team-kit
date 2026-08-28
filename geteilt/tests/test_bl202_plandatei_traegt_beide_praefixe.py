#!/usr/bin/env python3
"""Regressionstest fuer BL-202 — und fuer die Korrektur seiner Praemisse
(BL-209).

DER EINTRAG SAGT: Kaskaden-Plandateien heissen `ralph-kaskade-N-<thema>.md`,
obwohl sie das ganze Team binden. Ralph liest die Stufenbloecke, Harry/Marv
beziehen ihren Sweep-Fokus aus dem Plankopf, Frank arbeitet gegen dieselben
Zusicherungen, der Architekt schreibt das Abschluss-Doc gegen den Stufenbogen.
Der Name nennt EINE Rolle; das Dokument bindet alle.

DER EINTRAG SAGT AUCH: *„Keine Mechanik haengt am Praefix — es steht nur in
Vorlagen und Anleitungen."* **Das stimmt nicht.** Beim Bauen gefunden, an
SECHS Stellen ueber beide Bahnen:

  * `geteilt/tools/kosten.py` `kaskade_beginn()` — globt die Plandatei; daran
    haengen der Zeitraum-Abgleich aus `BL-45` und die P1b-Pruefung aus `BL-27`.
  * `bash/lib.sh` `team_kaskaden_nummer` — liest die Nummer aus dem Dateinamen.
  * `bash/lib.sh` `team_bau_notiz` — leitet den Ledger-Notiztext daraus ab
    (`BL-34`).
  * `bash/entry/team-status.sh` — Altlast-Kennzahl ueber `git log` auf die
    Plandateien.
  * `pwsh/lib.psm1` — die beiden Gegenstuecke der bash-Funktionen.
  * `pwsh/entry/team-status.ps1` — dasselbe `git log`.

WARUM DAS SCHLIMMER IST ALS EIN FEHLER: In allen sechs Faellen ist „nichts
gefunden" ein GUELTIGER Wert — eine benannte Kaskade hat keine Nummer, ein
frisches Projekt keine Plandatei. Eine Umbenennung haette die Ableitungen
deshalb nicht kaputt gemacht, sondern **stumm** gestellt. Der Ledger-Notiztext
waere leer geblieben, die Altlast-Kennzahl haette „noch keine Aussage moeglich"
gemeldet, und `kaskade_beginn` haette None geliefert — was `BL-45` und `BL-27`
zum Schweigen bringt.

DESHALB IST DER FIX NICHT DIE UMBENENNUNG, SONDERN DIE TOLERANZ: Beide Formen
werden ueberall erkannt. Erst danach ist die Umbenennung in den VORLAGEN
gefahrlos — Bestandsprojekte behalten ihre Dateinamen, ihr `.ralph-plan` zeigt
auf gewachsene Dateien, und beide Formen duerfen nebeneinander bestehen. Genau
das verlangt der Eintrag; er hielt es nur faelschlich fuer geschenkt.
"""
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]

# Die sechs Stellen, an denen Mechanik am Praefix haengt.
MECHANIK = [
    ("geteilt/tools/kosten.py", "kaskade_beginn (BL-45/BL-27)"),
    ("bash/lib.sh", "team_kaskaden_nummer + team_bau_notiz (BL-34)"),
    ("bash/entry/team-status.sh", "Altlast-Kennzahl"),
    ("pwsh/lib.psm1", "die pwsh-Gegenstuecke"),
    ("pwsh/entry/team-status.ps1", "Altlast-Kennzahl, pwsh"),
]

# Die Traeger der Konvention: Vorlagen und Briefings, also das, was eine NEUE
# Installation bekommt. Bestandsprojekte stehen hier ausdruecklich nicht.
VORLAGEN = [
    "bootstrap/TEAM.md",
    "bootstrap/CLAUDE.md.vorlage",
    "bootstrap/roadmap-skizzen.md",
    "geteilt/prompts/rolle-architekt.md",
]


def _lies(rel):
    pfad = WURZEL / rel
    if not pfad.is_file():
        pytest.skip(f"{rel} liegt hier nicht (Bahn abgewaehlt oder "
                    f"installierte Ablage statt Kit-Ablage)")
    return pfad.read_text(encoding="utf-8")


# --- Die Praemissen-Korrektur: beide Formen werden ueberall erkannt ---------

@pytest.mark.parametrize("rel,was", MECHANIK)
def test_jede_mechanik_erkennt_beide_praefixe(rel, was):
    """Der eigentliche Fix. Ohne ihn stellt die Umbenennung sechs Ableitungen
    stumm — und stumm heisst hier: sie liefern einen gueltig aussehenden
    Leerwert, keinen Fehler."""
    text = _lies(rel)
    assert "ralph-kaskade" in text or "ralph|team" in text or \
           "ralph)-kaskade" in text or "PLAN_PRAEFIXE" in text, (
        f"{rel}: die alte Form wird nicht mehr erkannt — Bestandsprojekte "
        f"({was}) fallen damit stumm aus.")
    assert "team-kaskade" in text or "team)-kaskade" in text or \
           "PLAN_PRAEFIXE" in text, (
        f"{rel}: die neue Form wird nicht erkannt ({was}). Ein Projekt, das "
        f"der Vorlage folgt, bekommt dann einen still leeren Wert.")


def test_kosten_py_haelt_beide_praefixe_an_einer_stelle():
    """Eine Liste statt zweier verstreuter Literale.

    Der naechste Praefix — und der Eintrag zeigt, dass es einen geben kann —
    gehoert an EINE Stelle. Dieselbe Lehre wie `BL-154`: eine zweite Liste
    ist ab der naechsten Aenderung falsch.
    """
    text = _lies("geteilt/tools/kosten.py")
    assert "PLAN_PRAEFIXE" in text, (
        "kosten.py haelt die Praefixe nicht an einer benannten Stelle.")
    assert "team-kaskade-" in text and "ralph-kaskade-" in text, (
        "kosten.py kennt nicht beide Formen.")


def test_kosten_py_liest_den_planordner_aus_der_konfiguration():
    """Die zweite Haelfte desselben Fundes, und sie trifft SCHON HEUTE.

    `kaskade_beginn` hatte den Ordner als Literal `plans` — obwohl
    `TEAM_PLAN_ORDNER` im Interview abgefragt und konfigurierbar ist. In jedem
    Projekt, das dort etwas anderes geantwortet hat, fand die Suche NIE eine
    Plandatei und gab None zurueck: der Zeitraum-Abgleich aus `BL-45` und die
    P1b-Pruefung aus `BL-27` schweigen dort seither.
    """
    text = _lies("geteilt/tools/kosten.py")
    assert "def plan_ordner" in text, (
        "kosten.py leitet den Planordner nicht ab — er steht wieder als "
        "Literal da und ist damit in jedem abweichend konfigurierten Projekt "
        "falsch.")
    assert 'os.environ.get("TEAM_PLAN_ORDNER"' in text, (
        "kosten.py liest TEAM_PLAN_ORDNER nicht aus der Umgebung.")


@pytest.mark.parametrize("rel", ["bash/entry/team.config.sh",
                                 "pwsh/entry/team.config.ps1"])
def test_beide_konfigurationen_exportieren_den_planordner(rel):
    """Ohne den Export nuetzt das Ableiten nichts — dieselbe Bauart wie bei
    `TEAM_DOMAENEN` eine Zeile darueber, aus demselben Grund."""
    text = _lies(rel)
    assert "TEAM_PLAN_ORDNER" in text and (
        "export TEAM_PLAN_ORDNER" in text
        or "$env:TEAM_PLAN_ORDNER" in text), (
        f"{rel} exportiert TEAM_PLAN_ORDNER nicht — die Python-Werkzeuge "
        f"sehen den konfigurierten Ordner dann nicht.")


# --- Erst danach: die Umbenennung in den Vorlagen ---------------------------

@pytest.mark.parametrize("rel", VORLAGEN)
def test_die_vorlagen_nennen_die_neue_form(rel):
    """Was eine NEUE Installation bekommt.

    Der Name nennt sonst eine Rolle, waehrend das Dokument alle bindet — und
    der Mensch entscheidet an genau dieser Datei, was ueberhaupt gebaut wird.
    """
    text = _lies(rel)
    assert "team-kaskade-" in text, (
        f"{rel} nennt weiter die alte Form. Neue Projekte bekommen dann einen "
        f"Dateinamen, der eine Rolle nennt, obwohl er das Team bindet.")


@pytest.mark.parametrize("rel", VORLAGEN)
def test_die_vorlagen_nennen_die_alte_form_NICHT_mehr(rel):
    """Die Gegenrichtung: Stuenden beide in derselben Vorlage, waere unklar,
    welche gilt — und der Architekt muesste raten."""
    text = _lies(rel)
    assert "ralph-kaskade-" not in text, (
        f"{rel} nennt noch die alte Form. Zwei Konventionen in einer Vorlage "
        f"sind keine Konvention.")


def test_bestandsprojekte_werden_NICHT_umbenannt():
    """Die wichtigste Grenze des Eintrags, und sie steht im Kit selbst.

    Der Backlog des Kits verweist an vielen Stellen auf gewachsene Plandateien
    unter ihrem alten Namen. Wer diese Belege mit umbenennt, faelscht die Spur
    — und die Spur ist in diesem Repo das Produkt.
    """
    backlog = WURZEL / "plans" / "backlog-archiv.md"
    if not backlog.is_file():
        pytest.skip("Kit-Archiv liegt hier nicht")
    text = backlog.read_text(encoding="utf-8")
    assert "ralph-kaskade" in text, (
        "Die historischen Verweise auf gewachsene Plandateien sind mit "
        "umbenannt worden — das faelscht die Spur rueckwirkend.")


# --- Der Nachweis am VERHALTEN, nicht am Quelltext ---------------------------
#
# Die Faelle oben lesen den Quelltext — das faengt eine Umbenennung, aber nicht
# einen Denkfehler. Diese hier starten die Ableitungen wirklich. Gegen den
# alten Stand gemessen: `team-kaskade-…` und ein abweichender Planordner gaben
# BEIDE None, und None ist hier ein gueltig aussehender Leerwert, kein Fehler.

def _mini_repo(tmp_path, ordner, name):
    import subprocess
    d = tmp_path / "repo"
    (d / ordner).mkdir(parents=True)
    (d / ordner / name).write_text("# Plan\n", encoding="utf-8")
    for befehl in (["git", "init", "-q", "."],
                   ["git", "config", "user.email", "t@t"],
                   ["git", "config", "user.name", "t"],
                   ["git", "add", "-A"],
                   ["git", "commit", "-qm", "plan"]):
        r = subprocess.run(befehl, cwd=d, capture_output=True)
        if r.returncode != 0:
            pytest.skip(f"git nicht benutzbar: {r.stderr!r}")
    return d


@pytest.mark.parametrize("ordner,name", [
    ("plans", "ralph-kaskade-7-x.md"),
    ("plans", "team-kaskade-7-x.md"),
    ("team-plans", "team-kaskade-7-x.md"),
    ("team-plans", "ralph-kaskade-7-x.md"),
])
def test_kaskade_beginn_findet_die_plandatei_wirklich(tmp_path, ordner, name,
                                                      monkeypatch):
    """Beide Praefixe UND der konfigurierte Ordner — am lebenden Objekt.

    Gemessen gegen den alten Stand: Von diesen vier Faellen lieferte genau
    EINER einen Zeitstempel (`plans/ralph-kaskade-…`), die anderen drei None.
    Daran haengen der Zeitraum-Abgleich aus `BL-45` und die P1b-Pruefung aus
    `BL-27` — beide hoerten in den drei Faellen still auf zu arbeiten.
    """
    import importlib.util
    pfad = WURZEL / "geteilt" / "tools" / "kosten.py"
    if not pfad.is_file():
        pfad = WURZEL / "team" / "tools" / "kosten.py"
    if not pfad.is_file():
        pytest.skip("kosten.py liegt hier nicht")
    spec = importlib.util.spec_from_file_location("kosten_bl202", pfad)
    kosten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kosten)

    repo = _mini_repo(tmp_path, ordner, name)
    monkeypatch.setenv("TEAM_PLAN_ORDNER", ordner + "/")
    beginn = kosten.kaskade_beginn("7", str(repo))
    assert beginn is not None, (
        f"kaskade_beginn findet {ordner}/{name} nicht. None ist hier KEIN "
        f"Fehler, sondern Schweigen — BL-45 und BL-27 haengen daran und "
        f"melden dann nichts mehr.")
    assert isinstance(beginn, int) and beginn > 0


def test_kaskade_beginn_schweigt_weiter_wo_es_soll(tmp_path, monkeypatch):
    """Die Gegenrichtung, ohne die der Fix wertlos waere.

    Eine BENANNTE Kaskade (`post-20`) hat keine nummerierte Plandatei — dort
    ist None richtig. Ein Fix, der einfach immer etwas findet, waere
    schlimmer als der Fehler.
    """
    import importlib.util
    pfad = WURZEL / "geteilt" / "tools" / "kosten.py"
    if not pfad.is_file():
        pfad = WURZEL / "team" / "tools" / "kosten.py"
    if not pfad.is_file():
        pytest.skip("kosten.py liegt hier nicht")
    spec = importlib.util.spec_from_file_location("kosten_bl202b", pfad)
    kosten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kosten)

    repo = _mini_repo(tmp_path, "plans", "post-20-fixserie.md")
    monkeypatch.setenv("TEAM_PLAN_ORDNER", "plans/")
    assert kosten.kaskade_beginn("20", str(repo)) is None, (
        "Eine benannte Kaskade hat keine nummerierte Plandatei — hier muss "
        "None herauskommen, sonst datiert der Zeitraum-Abgleich auf eine "
        "Datei, die gar nicht die Kaskade eroeffnet hat.")

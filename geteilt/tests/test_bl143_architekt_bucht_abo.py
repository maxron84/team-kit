#!/usr/bin/env python3
"""BL-143: Der Alias `--architekt-abschluss` buchte fest `auth=api` — gegen die
eigene Regel, und mit sichtbarer Geldwirkung.

WAS IM FELD PASSIERT IST
    `Feld B`, Closeout der ersten Kaskade. Das Werkzeug meldete

        Architekt-Zeile Kaskade 1 (produkt) angelegt: 16.3990 USD

    und schrieb dabei `auth = api`. Im Kontostand landeten die 16,3990 USD
    damit in der Zeile **"real via API abgerechnet"** — echtes Geld, das nie
    geflossen ist. Der Architekt lief im Abo.

WARUM DAS EIN REGELBRUCH IST, KEIN SCHOENHEITSFEHLER
    `CLAUDE.md` und das Architekten-Briefing sagen seit der Abo-Umstellung
    ausdruecklich: "Auch Axel und Der Architekt laufen Abo-first — KEINE Rolle
    ist mehr fest api", und der Architektenwert sei "als Abo-Gegenwert zu buchen
    und NIE stillschweigend als abgerechneter Betrag auszugeben". Der Alias tat
    genau Letzteres, und zwar an der einen Stelle, die TEAM.md und das Briefing
    als den NORMALEN Weg nennen.

WARUM ES NIEMANDEM AUFFIEL
    Weil die Erfolgsmeldung die Auth-Achse nicht nannte. Der Satz oben ist wahr
    und verschweigt genau das Feld, in dem der Fehler sass. Gemerkt wurde es
    erst beim LESEN der geschriebenen Ledger-Zeile — also nicht durch das
    Werkzeug, sondern trotz seiner Meldung. Die Roles- und Ralph-Zeilen nennen
    ihre Achse laengst ("abo 4.5571 / api 0.0000"); ausgerechnet diese nicht.

DER ZWEITE FUND, OHNE DEN DER FIX WIRKUNGSLOS WAERE
    Beide Wrapper (`status_architekt_abschluss` in bash,
    `Status-ArchitektAbschluss` in pwsh) lasen ausschliesslich die ersten DREI
    Argumente — jedes weitere fiel kommentarlos weg. Das ist zeichengleich der
    Fehler, den BL-26 fuer `--akteur-abschluss` abgetragen hat; fuer den
    Architekten-Alias hat ihn nie jemand nachgezogen. Verschaerfend: Das
    Briefing behauptet woertlich, der Wrapper reiche die Schalter durch.

    Ein `--auth`, das das Werkzeug erbt, aber nie erreicht, waere ein Fix, der
    sich nur im Unit-Test beweist. Deshalb steht die Durchreiche hier mit unter
    Test — auf BEIDEN Bahnen.

WAS DIESER TEST PRUEFT
    Am VERHALTEN, gegen das echte Werkzeug und ein echtes Fixture-Ledger:
      * ohne --auth wird `abo` geschrieben (der Fall aus dem Feld),
      * die Erfolgsmeldung NENNT die Achse,
      * --auth api bleibt moeglich (der Architekt mit echtem Key),
      * ein unsinniges --auth bricht ab, OHNE das Ledger anzufassen,
      * der bash-Wrapper reicht --auth und --kaskade durch,
      * der pwsh-Wrapper tut dasselbe (uebersprungen ohne pwsh),
      * und die Vorlagen nennen den Weg, der jetzt der richtige ist.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      verlange_pwsh, werkzeug_wert)

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _ledger(tmp_path):
    p = tmp_path / ".budget-ledger"
    p.write_text(KOPF, encoding="utf-8")
    (tmp_path / ".ralph-plan").write_text("plans/ralph-kaskade-1-produkt.md\n",
                                          encoding="utf-8")
    return p


def _kosten(tmp_path, *args):
    r = subprocess.run([sys.executable, str(KOSTEN_PY), *args],
                       cwd=tmp_path, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def _architekt_zeilen(ledger):
    return [z for z in kosten.ledger_zeilen(str(ledger))
            if z["rolle"] == "architekt"]


# --- Der Fall aus dem Feld ---------------------------------------------------

def test_ohne_auth_wird_abo_gebucht(tmp_path):
    """Genau der Aufruf, der im Feld 16,3990 USD in die API-Spalte trug."""
    ledger = _ledger(tmp_path)
    rc, out, err = _kosten(tmp_path, "architekt-abschluss",
                           "--usd", "16.3990", "--domaene", "produkt")
    assert rc == 0, err
    zeilen = _architekt_zeilen(ledger)
    assert len(zeilen) == 1, f"erwartet EINE Architekt-Zeile, ist: {zeilen}"
    assert zeilen[0]["auth"] == "abo", (
        "BL-143 ist zurueck: Der Alias bucht wieder fest api. Im Kontostand "
        "landet der Betrag dann unter 'real via API abgerechnet' — Geld, das "
        f"nie geflossen ist. Zeile: {zeilen[0]}")


def test_die_meldung_nennt_die_achse(tmp_path):
    """Ohne diese Zeile liest sich ein Fehlgriff nicht — genau das war der Fall.

    Der Fehler wurde im Feld NICHT durch das Werkzeug entdeckt, sondern beim
    Nachlesen der Ledger-Zeile. Eine Meldung, die das entscheidende Feld
    verschweigt, ist der Grund, warum eine Fehlbuchung ueberhaupt stehen bleibt.
    """
    _ledger(tmp_path)
    rc, out, err = _kosten(tmp_path, "architekt-abschluss",
                           "--usd", "16.3990", "--domaene", "produkt")
    assert rc == 0, err
    assert "(abo)" in out, (
        f"die Erfolgsmeldung nennt die Auth-Achse nicht: {out!r}")
    assert "16.3990" in out, out


def test_auth_api_bleibt_moeglich(tmp_path):
    """Vorbelegung, nicht Festlegung: Wer wirklich ueber einen Key gearbeitet
    hat, muss das sagen koennen. Sonst waere der Fix nur die andere Haelfte
    desselben Fehlers."""
    ledger = _ledger(tmp_path)
    rc, out, err = _kosten(tmp_path, "architekt-abschluss", "--usd", "2.50",
                           "--domaene", "produkt", "--auth", "api")
    assert rc == 0, err
    assert _architekt_zeilen(ledger)[0]["auth"] == "api", err
    assert "(api)" in out, out


def test_unsinniges_auth_bricht_ab_und_laesst_das_ledger_in_ruhe(tmp_path):
    """Die Gegenrichtung: `--auth` durchreichen darf nicht heissen, jeden Wert
    zu akzeptieren."""
    ledger = _ledger(tmp_path)
    vorher = ledger.read_text(encoding="utf-8")
    rc, out, err = _kosten(tmp_path, "architekt-abschluss", "--usd", "1",
                           "--domaene", "produkt", "--auth", "quatsch")
    assert rc != 0, "ein unbekannter auth-Wert muss abbrechen"
    assert "abo" in err and "api" in err, f"die Meldung nennt die Werte nicht: {err}"
    assert ledger.read_text(encoding="utf-8") == vorher, (
        "das Ledger wurde trotz Abbruch angefasst")


# --- Die Durchreiche, ohne die der Fix nicht ankommt -------------------------

def _fixture_bahn(tmp_path, bahn):
    """Minimalprojekt fuer einen Entrypoint-Lauf, wie test_stufe51 es baut."""
    (tmp_path / "team" / "tools").mkdir(parents=True)
    shutil.copy(kit_pfad("tools", "kosten.py"),
                tmp_path / "team" / "tools" / "kosten.py")
    if bahn == "bash":
        shutil.copy(entrypoint_pfad("team-status.sh"), tmp_path / "team-status.sh")
        shutil.copy(kit_pfad("lib.sh"), tmp_path / "team" / "lib.sh")
        (tmp_path / "team.config.sh").write_text(
            'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n', encoding="utf-8")
    else:
        shutil.copy(entrypoint_pfad("team-status.ps1"), tmp_path / "team-status.ps1")
        shutil.copy(kit_pfad("lib.psm1"), tmp_path / "team" / "lib.psm1")
        # BL-113: PowerShell-Quelltext traegt ein BOM, auch als Fixture (BL-134).
        (tmp_path / "team.config.ps1").write_text(
            '$TEAM_BEUTEBUCH_TOOL = "' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            '$TEAM_KOSTEN_TOOL = "' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            '$TEAM_DOMAENEN = "produkt"\n', encoding="utf-8-sig")
    _ledger(tmp_path)
    return tmp_path


def _pruefe_durchreiche(repo, ledger):
    """Gemeinsame Zusicherung beider Bahnen: --kaskade und --auth kommen an."""
    zeilen = _architekt_zeilen(ledger)
    assert len(zeilen) == 1, f"erwartet EINE Architekt-Zeile, ist: {zeilen}"
    assert zeilen[0]["kaskade"] == "7", (
        "BL-143/BL-26: `--kaskade 7` hat das Werkzeug nicht erreicht — der "
        "Wrapper hat es fallen lassen und die Nummer aus .ralph-plan "
        f"abgeleitet (dort steht 1). Zeile: {zeilen[0]}")
    assert zeilen[0]["auth"] == "api", (
        "BL-143: `--auth api` hat das Werkzeug nicht erreicht. Ein --auth, das "
        "der Alias erbt, aber der Wrapper wegwirft, ist ein Fix, der sich nur "
        f"im Unit-Test beweist. Zeile: {zeilen[0]}")
    assert zeilen[0]["notiz"].startswith("Sitzung A"), (
        f"die Notiz ist verlorengegangen oder verrutscht: {zeilen[0]}")


def test_bash_wrapper_reicht_schalter_durch(tmp_path):
    verlange_bash()
    repo = _fixture_bahn(tmp_path, "bash")
    r = subprocess.run(
        [BASH, "./team-status.sh", "--architekt-abschluss", "9.99", "produkt",
         "Sitzung A", "--kaskade", "7", "--auth", "api"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
    _pruefe_durchreiche(repo, repo / ".budget-ledger")


def test_pwsh_wrapper_reicht_schalter_durch(tmp_path):
    verlange_pwsh()
    repo = _fixture_bahn(tmp_path, "pwsh")
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./team-status.ps1",
         "--architekt-abschluss", "9.99", "produkt", "Sitzung A",
         "--kaskade", "7", "--auth", "api"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
    _pruefe_durchreiche(repo, repo / ".budget-ledger")


# --- Die Vorlagen muessen den Weg nennen, der jetzt der richtige ist ---------

def _vorlage(name):
    for kandidat in (REPO_ROOT / "bootstrap" / name, REPO_ROOT / name):
        if kandidat.is_file():
            return kandidat
    return None


def test_kein_regeltext_verspricht_mehr_auth_api():
    """Die Doku ist Teil des Fixes: Solange sie `auth=api` behauptet, ist die
    Regel im selben Repo zweimal verschieden aufgeschrieben — und der stille
    Fehlermodus kehrt beim naechsten Textumbau zurueck (Bauart BL-139)."""
    schuldig = []
    for pfad in (_vorlage("TEAM.md"), REPO_ROOT / "geteilt" / "prompts" / "rolle-architekt.md",
                 KOSTEN_PY):
        if pfad is None or not pfad.is_file():
            continue
        text = pfad.read_text(encoding="utf-8-sig")
        # "auth=api" bzw. "--auth api" im Zusammenhang mit dem Alias.
        for m in re.finditer(r"architekt-abschluss", text):
            fenster = text[max(0, m.start() - 400): m.start() + 400]
            if re.search(r"auth\s*=\s*api|--auth\s+api\s+vorbelegt", fenster):
                schuldig.append(f"{pfad.name}:{text.count(chr(10), 0, m.start()) + 1}")
    assert not schuldig, (
        "BL-143: Diese Stellen versprechen fuer --architekt-abschluss weiter "
        "die API-Achse:\n  " + "\n  ".join(sorted(set(schuldig))))


def test_teamd_md_nennt_die_abo_vorbelegung():
    """Gegenrichtung: Der Text darf nicht einfach schweigen. Wer den Alias
    benutzt, muss wissen, WAS gebucht wird — sonst ist die stille Vorbelegung
    nur die freundlichere Fassung desselben Problems."""
    team_md = _vorlage("TEAM.md")
    if team_md is None:
        pytest.skip("TEAM.md nicht in dieser Ablage")
    text = team_md.read_text(encoding="utf-8-sig")
    m = re.search(r"architekt-abschluss", text)
    assert m, "TEAM.md nennt --architekt-abschluss gar nicht mehr"
    fenster = text[m.start(): m.start() + 1200]
    assert "abo" in fenster.lower(), (
        "TEAM.md nennt den Alias, sagt aber nicht, dass er als Abo-Gegenwert "
        "bucht. Genau diese Auskunft fehlte im Feld.")

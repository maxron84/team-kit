#!/usr/bin/env python3
"""BL-269: Zwei Laufzeitartefakte standen nicht in `TEAM_GUARD_LAUFZEIT` —
und der Loop stellte sich damit zweimal selbst ein Bein.

WAS IM FELD PASSIERT IST (`Feld B`, 2026-09-17, zwei Meldungen)
    * `.team-gate-rot` (`BL-256`): Frank haengt dort eine Zeile an, wenn die
      Suite schon vor ihm rot war. Scheitert sein Versuch, endet er in
      `team_rollback_rolle` — und der filterte nur `TEAM_GUARD_LAUFZEIT`
      heraus. Die Gate-Datei war weg, der Abschlussbericht fand nichts, und der
      Lauf meldete sich als fertig, WAEHREND DAS GATE AUS WAR. Wortlich der
      Zustand, den `BL-256` verhindern soll.
    * `.ralph-uebersprungen` (`BL-255`): entsteht nach dem ersten
      planmaessigen Uebersprung als nicht ignorierte Datei. Beim ZWEITEN
      Uebersprung desselben Laufs schlug Ralphs eigener Sauberkeits-Riegel an
      (*„laesst Uncommittetes liegen"*) — gemeint war das eigene
      Buchhaltungsartefakt.

WARUM DAS GITIGNORE-FRAGMENT NICHT GENUEGT
    Im Kit-Fragment standen beide Dateien schon. Aber `--update` fasst die
    `.gitignore` eines Projekts nicht an — ein Projekt, das vor `BL-255`
    einzog, kennt sie dort nicht. Was JEDES Projekt erreicht, ist die
    Bibliothek: `TEAM_GUARD_LAUFZEIT` und der Riegel, der sie benutzt.

DIE GATTUNG, und sie ist der Grund fuer diese Datei
    Jede neue Zustandsdatei musste an drei Stellen nachgetragen werden —
    Fragment, Guard-Muster, (bei Bedarf) Riegel —, und keine meldete sich,
    wenn sie vergessen wurde. Hier werden die drei gegeneinander gehalten:
      (1) jeder Punkt-Dateiname, den der CODE beider Bahnen schreibt, steht
          im Fragment — oder in AUSNAHMEN, mit Grund;
      (2) jeder Laufzeit-Eintrag des Fragments trifft das GERENDERTE
          `TEAM_GUARD_LAUFZEIT` beider Bahnen — oder steht in AUSNAHMEN;
      (3) beide Bahnen rendern dasselbe Muster, auch fuer einen
          konfigurierten Gate-Dateinamen;
    und der Fall aus dem Feld wird AUSGEFUEHRT: Rollback mit Gate-Datei und
    einer gewoehnlichen neuen Datei als Gegenprobe.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT, Git, Ruf, Schreib, Variable, nur_code

FRAGMENT = REPO_ROOT / "bootstrap" / "gitignore.fragment"

# Was der Code schreibt und trotzdem NICHT ins Laufzeit-Muster gehoert — mit
# Grund, damit die Liste nicht still waechst (dieselbe Pflicht wie die
# Ausnahmeliste aus BL-112).
AUSNAHMEN = {
    ".budget-ledger": "das Ledger IST Projektdaten und wird versioniert",
    ".ralph-plan": "setzt der Mensch vor dem Lauf, nicht die Shell waehrend "
                   "eines Rollenlaufs — sie im Muster zu verstecken, machte "
                   "den Guard blind, falls eine Rolle den Zeiger verstellt",
    "backups/": "legt der Installer an, nicht der Loop",
}

# Punkt-Dateinamen, die einer Variablen ZUGEWIESEN werden — beide Bahnen,
# beide Schreibweisen (`X=".datei"`, `${X:-.datei}`, `$x = '.datei'`,
# `Team-Default 'X' '.datei'`). Der Name endet am Anfuehrungszeichen.
ZUWEISUNG = re.compile(
    r"""(?:=\s*["']|:-|Team-Default\s+'[A-Z_]+'\s+')(\.[a-z][a-z0-9.-]*)""")


def _code_dateien():
    muster = ("bash/lib.sh", "bash/redteam.sh", "bash/entry/*.sh",
              "pwsh/lib.psm1", "pwsh/redteam.ps1", "pwsh/entry/*.ps1")
    for m in muster:
        for p in sorted(REPO_ROOT.glob(m)):
            if not p.name.startswith("team.config"):
                yield p


def geschriebene_punktdateien():
    namen = set()
    for p in _code_dateien():
        namen |= set(ZUWEISUNG.findall(nur_code(p.read_text(encoding="utf-8-sig"))))
    # `.team-focus-<rolle>` wird zusammengesetzt; der Praefix allein ist kein
    # Dateiname.
    return {n for n in namen if not n.endswith("-")}


def laufzeit_eintraege(text):
    """Die Eintraege des ERSTEN Blocks im Fragment — der Laufzeitartefakte.
    Er endet an der ersten Leerzeile."""
    block = text.split("\n\n", 1)[0]
    return [z.strip() for z in block.splitlines()
            if z.strip() and not z.lstrip().startswith("#")]


def _verlange_fragment():
    if not FRAGMENT.is_file():
        pytest.skip("Das gitignore-Fragment liegt nur im Kit")
    return FRAGMENT.read_text(encoding="utf-8")


def _muster(schale, tmp_path, **env):
    lib = schale.lib_kopieren(tmp_path)
    r = schale.lauf([Variable("TEAM_GUARD_LAUFZEIT")], cwd=tmp_path, lib=lib,
                    env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _beispielpfad(eintrag):
    """Ein Pfad, wie ihn `git status --porcelain` fuer den Eintrag meldet."""
    if eintrag.endswith("/"):
        return eintrag + "x.json"
    return eintrag


# --- (1) Was der Code schreibt, steht im Fragment ---------------------------

def test_jede_geschriebene_punktdatei_steht_im_fragment():
    fragment = _verlange_fragment()
    eintraege = {e.rstrip("/") for e in laufzeit_eintraege(fragment)}
    namen = geschriebene_punktdateien()
    assert {".ralph-uebersprungen", ".team-gate-rot", ".ralph-state"} <= namen, (
        f"Vorbedingung: der Scan findet die bekannten Namen nicht ({sorted(namen)}) "
        "— dann prueft dieser Fall nichts.")
    fehlend = sorted(n for n in namen
                     if n not in eintraege and n not in AUSNAHMEN)
    assert not fehlend, (
        "Diese Dateien schreibt der Code, aber das gitignore-Fragment kennt "
        f"sie nicht: {fehlend}. Ein neues Projekt bekaeme sie als Uebergriff "
        "gemeldet oder committet (BL-269).")


# --- (2) Was im Fragment steht, schuetzt der Guard ---------------------------

def test_jeder_laufzeiteintrag_trifft_das_guard_muster(schale, tmp_path):
    fragment = _verlange_fragment()
    muster = re.compile(_muster(schale, tmp_path))
    fehlend = [e for e in laufzeit_eintraege(fragment)
               if e not in AUSNAHMEN and not muster.search(_beispielpfad(e))]
    assert not fehlend, (
        f"Diese Laufzeitartefakte trifft TEAM_GUARD_LAUFZEIT ({schale.name}) "
        f"nicht: {fehlend}. Fehlt die Zeile im .gitignore eines Projekts — und "
        "das Update traegt sie dort nicht nach —, raeumt der Rollback sie weg "
        "oder ein Riegel haelt sie fuer liegengelassene Arbeit (BL-269).")


def test_das_muster_trifft_keine_fremde_datei(schale, tmp_path):
    """Gegenrichtung: Ein Muster, das zu viel trifft, macht den Guard blind."""
    muster = re.compile(_muster(schale, tmp_path))
    for pfad in ("src/app.py", "plans/beutebuch.md", ".team-gate-rot.bak",
                 "docs/.ralph-state", ".budget-ledger"):
        assert not muster.search(pfad), f"{pfad} gilt als Laufzeitartefakt"


# --- (3) Der konfigurierte Name, und beide Bahnen gleich ---------------------

def test_ein_konfigurierter_gate_name_wird_geschuetzt(schale, tmp_path):
    muster = re.compile(_muster(schale, tmp_path, TEAM_GATE_DATEI=".mein-gate"))
    assert muster.search(".mein-gate"), (
        "TEAM_GATE_DATEI ist konfigurierbar — das Muster muss den NAMEN "
        f"schuetzen, nicht den Default.\n{muster.pattern}")


def test_beide_bahnen_rendern_dasselbe_muster(tmp_path):
    from conftest import _bash_bereit, _pwsh_bereit, Schale
    if not (_bash_bereit()[0] and _pwsh_bereit()[0]):
        pytest.skip("braucht beide Bahnen auf diesem Wirt")
    ergebnisse = {}
    for bahn in ("bash", "pwsh"):
        ziel = tmp_path / bahn
        ziel.mkdir()
        ergebnisse[bahn] = _muster(Schale(bahn), ziel,
                                   TEAM_GATE_DATEI=".team-gate-rot")
    assert ergebnisse["bash"] == ergebnisse["pwsh"], ergebnisse


# --- Der Fall aus dem Feld, ausgefuehrt --------------------------------------

def _git(repo, *befehl):
    return subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout.strip()


def test_der_rollback_verschont_die_gate_datei(tmp_path, schale):
    """Der Reproducer der Meldung: Gate-Datei plus eine gewoehnliche neue
    Datei als Gegenprobe. Ohne Eintrag ist die Gate-Datei danach weg; die
    Gegenprobe beweist, dass der Rollback ueberhaupt gearbeitet hat."""
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "team").mkdir()
    schale.lib_kopieren(repo)
    schale.config_schreiben(repo, {"TEAM_DOMAENEN": "produkt",
                                   "TEAM_PRODUKTIVCODE": "src/"})
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        _git(repo, *befehl)
    start = _git(repo, "rev-parse", "HEAD")
    ergebnis = schale.lauf(
        [Ruf("team_guard_begin"),
         Schreib(".team-gate-rot", "2026-09-17T10:00 | frank | test_x\n"),
         Schreib("src/neu.py", "y = 1\n"),
         Ruf("team_rollback_rolle", "frank", start)],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)
    assert not (repo / "src" / "neu.py").exists(), (
        "Gegenprobe: der Rollback hat gar nicht gearbeitet.\n" + ergebnis.stderr)
    assert (repo / ".team-gate-rot").is_file(), (
        "team_rollback_rolle hat die Gate-Datei geloescht — der Lauf meldet "
        "sich danach als fertig, waehrend das Gate aus ist (BL-269/BL-256).\n"
        + ergebnis.stderr)


# --- Der Riegel des Uebersprungs ---------------------------------------------

@pytest.mark.parametrize("datei", ["bash/entry/ralph.sh", "pwsh/entry/ralph.ps1"])
def test_ralphs_uebersprung_riegel_filtert_laufzeitartefakte(datei):
    """Der zweite Fall aus dem Feld, am Quelltext: Der Riegel (b) der
    zweiten Quittungsform darf `git status` nicht roh lesen."""
    pfad = REPO_ROOT / datei
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt nur im Kit")
    code = nur_code(pfad.read_text(encoding="utf-8-sig"))
    anfang = code.index("STUFE_${STUFE}_UEBERSPRUNGEN" if datei.endswith(".sh")
                        else "STUFE_${stufe}_UEBERSPRUNGEN")
    block = code[anfang:anfang + 3000]
    i = block.index("Uncommittetes liegen")
    vor_dem_riegel = block[:i]
    assert "TEAM_GUARD_LAUFZEIT" in vor_dem_riegel[-900:], (
        f"{datei}: Der Uebersprung-Riegel liest `git status` ohne die "
        "Laufzeitartefakte herauszufiltern — die erste .ralph-uebersprungen "
        "blockiert dann den zweiten Uebersprung desselben Laufs (BL-269).")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

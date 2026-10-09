#!/usr/bin/env python3
"""BL-318: Die Commit-Zeile am Ende des Updates nahm mit `add -A` fremde
Aenderungen im Arbeitsbaum mit.

WAS GEMELDET WURDE (`Feld F`, 2026-10-04)
    Das Update endete mit `git -C <ziel> add -A; git -C <ziel> commit -m
    "chore: T.E.A.M. aktualisiert"`. Der Mensch hatte eine Szenarioaenderung
    uncommittet im Produktivcode liegen und uebernahm die Zeile woertlich —
    die halbe Produktaenderung landete im Update-Commit. Wer die Geschichte
    nach Produktaenderungen durchsieht, ueberspringt `chore: T.E.A.M. …`, und
    ein Sweep liest den Commit als Infrastruktur. Dieselbe Zeile stand am Ende
    der Einrichtung.

WAS DAS KIT JETZT TUT (Programm statt Rat)
    `kit_stand.py vorher` haelt den Arbeitsbaum fest, BEVOR der Installer
    schreibt; `commit-vorschlag` vergleicht danach und druckt die Commit-Zeilen
    ueber genau die eigenen Pfade (Liste im Git-Verzeichnis, NUL-getrennt,
    woertlich). Was vorher schon dalag, nennt es — und `git commit` mit
    Pfadliste nimmt auch dann nichts Fremdes mit, wenn vorher etwas gestaged
    war.

Die Faelle unten fuehren die gedruckten Zeilen WOERTLICH aus: Ein Vorschlag,
den niemand ausprobiert, beweist nichts ueber den Commit, den er erzeugt.
"""
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

KIT_STAND = kit_pfad("tools", "kit_stand.py")
WURZEL = Path(__file__).resolve().parents[2]


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def _repo(tmp_path):
    repo = tmp_path / "projekt"
    (repo / "src").mkdir(parents=True)
    (repo / "team").mkdir()
    for befehl in (("init", "-q"), ("config", "user.email", "t@l"),
                   ("config", "user.name", "T"),
                   ("config", "core.autocrlf", "false")):
        _git(repo, *befehl)
    (repo / "src" / "szene.sqf").write_text("a\n", encoding="utf-8")
    (repo / "team" / "lib.sh").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "start")
    return repo


def _werkzeug(*args):
    if not KIT_STAND.is_file():
        pytest.skip("kit_stand.py liegt hier nicht")
    return subprocess.run([sys.executable, str(KIT_STAND), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def _vorschlag_ausfuehren(repo, nachricht="chore: T.E.A.M. aktualisiert"):
    r = _werkzeug("commit-vorschlag", "--ziel", str(repo),
                  "--nachricht", nachricht)
    assert r.returncode == 0, r.stderr
    befehle = [z.strip() for z in r.stdout.splitlines()
               if z.strip().startswith("git -C ")]
    for befehl in befehle:
        # Wie eine Shell: Anfuehrungszeichen gruppieren und fallen weg — unter
        # Windows ohne POSIX-Modus, sonst fraessen die Rueckstriche sich selbst.
        teile = shlex.split(befehl, posix=(os.name != "nt"))
        teile = [t.replace('"', "") for t in teile]
        e = subprocess.run(teile, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        assert e.returncode == 0, (befehl, e.stdout, e.stderr)
    return r.stdout, befehle


def _im_commit(repo):
    return sorted(z for z in _git(repo, "show", "--name-only", "--format=",
                                  "HEAD").stdout.splitlines() if z)


def test_fremde_arbeit_bleibt_draussen_und_wird_genannt(tmp_path):
    """Der Feldfall: geaendertes Produkt, eine neue Datei des Menschen."""
    repo = _repo(tmp_path)
    with open(repo / "src" / "szene.sqf", "a", encoding="utf-8") as fh:
        fh.write("vom Menschen\n")
    (repo / "src" / "neu.txt").write_text("notiz\n", encoding="utf-8")
    _werkzeug("vorher", "--ziel", str(repo))
    with open(repo / "team" / "lib.sh", "a", encoding="utf-8") as fh:
        fh.write("vom Update\n")
    (repo / "team" / "neu datei.py").write_text("y\n", encoding="utf-8")
    ausgabe, befehle = _vorschlag_ausfuehren(repo)
    assert len(befehle) == 2 and "add -A" not in ausgabe, ausgabe
    assert _im_commit(repo) == ["team/lib.sh", "team/neu datei.py"], (
        "Der Commit traegt fremde Arbeit oder verliert eigene.\n" + ausgabe)
    offen = _git(repo, "status", "--porcelain").stdout
    assert "src/szene.sqf" in offen and "src/neu.txt" in offen, offen
    assert "src/szene.sqf" in ausgabe and "src/neu.txt" in ausgabe, (
        "Die fremde Arbeit wird nicht genannt — der Mensch weiss dann nicht, "
        f"dass sie noch zu committen ist.\n{ausgabe}")


def test_vorher_gestaged_wird_trotzdem_nicht_mitgenommen(tmp_path):
    """`git commit` mit Pfadliste nimmt nur diese Pfade — auch wenn vorher
    schon etwas im Index lag."""
    repo = _repo(tmp_path)
    (repo / "fremd.txt").write_text("staged\n", encoding="utf-8")
    _git(repo, "add", "fremd.txt")
    _werkzeug("vorher", "--ziel", str(repo))
    with open(repo / "team" / "lib.sh", "a", encoding="utf-8") as fh:
        fh.write("vom Update\n")
    _vorschlag_ausfuehren(repo)
    assert _im_commit(repo) == ["team/lib.sh"]
    assert "A  fremd.txt" in _git(repo, "status", "--porcelain").stdout


def test_eine_auch_vorher_geaenderte_datei_wird_benannt(tmp_path):
    """Hat der Mensch dieselbe Datei geaendert wie der Installer, gehoert sie
    in den Commit — aber er erfaehrt, dass seine Aenderung mitgeht."""
    repo = _repo(tmp_path)
    with open(repo / "team" / "lib.sh", "a", encoding="utf-8") as fh:
        fh.write("vom Menschen\n")
    _werkzeug("vorher", "--ziel", str(repo))
    with open(repo / "team" / "lib.sh", "a", encoding="utf-8") as fh:
        fh.write("vom Update\n")
    ausgabe, _ = _vorschlag_ausfuehren(repo)
    assert _im_commit(repo) == ["team/lib.sh"]
    assert "VORHER geändert" in ausgabe and "team/lib.sh" in ausgabe, ausgabe


def test_ohne_vorher_stand_wird_gewarnt(tmp_path):
    """Gegenrichtung: Fehlt der Schnappschuss, behauptet das Werkzeug keine
    Trennung, die es nicht kennt."""
    repo = _repo(tmp_path)
    with open(repo / "team" / "lib.sh", "a", encoding="utf-8") as fh:
        fh.write("vom Update\n")
    ausgabe, _ = _vorschlag_ausfuehren(repo)
    assert "Kein Vorher-Stand" in ausgabe, ausgabe


def test_die_einrichtung_in_ein_repo_ohne_commit(tmp_path):
    """Die erste Installation kann das erste Commit eines Repos sein."""
    repo = tmp_path / "leer"
    repo.mkdir()
    for befehl in (("init", "-q"), ("config", "user.email", "t@l"),
                   ("config", "user.name", "T")):
        _git(repo, *befehl)
    (repo / "app.py").write_text("mein code\n", encoding="utf-8")
    _werkzeug("vorher", "--ziel", str(repo))
    (repo / "TEAM.md").write_text("t\n", encoding="utf-8")
    _vorschlag_ausfuehren(repo, "chore: T.E.A.M. eingerichtet")
    assert _im_commit(repo) == ["TEAM.md"]


def test_nichts_geaendert_nichts_zu_committen(tmp_path):
    repo = _repo(tmp_path)
    _werkzeug("vorher", "--ziel", str(repo))
    ausgabe, befehle = _vorschlag_ausfuehren(repo)
    assert not befehle and "Nichts zu committen" in ausgabe, ausgabe


# --- Die Installer --------------------------------------------------------------

@pytest.mark.parametrize("datei", ["bash/install.sh", "pwsh/install.ps1"])
def test_beide_installer_halten_den_vorher_stand_fest(datei):
    pfad = WURZEL / datei
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt nur im Kit")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "kit_stand.py" in text and " vorher --ziel" in text, (
        f"{datei} haelt den Arbeitsbaum vor dem Schreiben nicht fest.")
    assert text.count("ommit-Vorschlag") + text.count("commit_vorschlag") >= 3, (
        f"{datei}: Update UND Einrichtung muessen den Vorschlag drucken.")
    for zeile in text.splitlines():
        if zeile.lstrip().startswith("#"):
            continue
        assert "add -A" not in zeile, (
            f"{datei} schlaegt wieder `add -A` vor (Kit-BL-318):\n{zeile}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

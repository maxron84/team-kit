#!/usr/bin/env python3
"""BL-131: Die Bash-Bahn verdrahtete `python3` — auch unter Windows.

⚠️ Feldbefund, dieselbe Windows-Maschine wie BL-113 und BL-122…BL-130.

An drei Stellen stand der Name des Interpreters fest im Text, jedes Mal mit
derselben Begruendung: „dieser Installer/diese Bahn laeuft unter Linux".

  * `bash/lib.sh` — DREIZEHN Aufrufe (`python3 -c '…'`, `python3 - "$out"`).
  * `bash/entry/team.config.sh` — `TEAM_KOSTEN_TOOL` und
    `TEAM_BEUTEBUCH_TOOL` mit eingebautem `python3`, ohne Platzhalter.
  * `bash/install.sh` — der Installer selbst und der Wert, den er in BEIDE
    Konfigurationen schreibt.

Die Annahme ist falsch: Unter **Git for Windows** laeuft die Bash-Bahn auf
Windows. Und dort ist `python3` nicht abwesend, sondern BELEGT —
`%LOCALAPPDATA%\\Microsoft\\WindowsApps\\python3.exe` ist der
App-Execution-Alias aus dem Microsoft Store. `command -v` findet ihn, der
Aufruf startet den Store und meldet „Python was not found"; der Exit-Code ist
49. Jeder der dreizehn Aufrufe war damit tot, und mit ihnen `team_promise_in`,
`team_result_meldet_erfolg`, `team_429_reset_epoch` und die Budget-Summen —
also die Funktionen, an denen Geld und Abbruchentscheidungen haengen.

WARUM ES SO LANGE UNBEMERKT BLIEB
    Der Fund ist zeichengleich mit BL-122/BL-125, und `Finde-Python` in
    `install.ps1` loest ihn auf der pwsh-Bahn seit Langem. Die pwsh-Bahn hat
    die dreizehn `python3 -c`-Bloecke sogar ganz ersetzt (native Ausdruecke,
    siehe `pwsh/lib.psm1`). Die Bash-Bahn hat es nie nachgezogen, weil niemand
    sie unter Windows gefahren hat — sie galt als „die Linux-Bahn". Das ist
    die Doppelbahn-Drift, gegen die der gemeinsame Harnisch gebaut wurde, nur
    an einer Stelle, die kein Test beruehrte.

    Bitter dabei: Ein Windows-Projekt bekam eine KORREKTE `team.config.ps1`
    (der pwsh-Installer loeste auf) und eine KAPUTTE `team.config.sh`
    daneben — der `python3` darin war fest eingebaut, es gab gar keinen
    Platzhalter zu fuellen. Beide Installer schreiben beide Konfigurationen
    (BL-126); die eine war seit jeher halb blind.

WARUM DIE ZUSICHERUNGEN AM QUELLTEXT HAENGEN
    Wie bei BL-126, BL-129 und BL-130: Unter Linux ist `python3` richtig. Ein
    verhaltensbasierter Test waere auf der Maschine, auf der er meistens
    laeuft, auch ohne den Fix gruen.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, kit_pfad, verlange_bash

WURZEL = Path(__file__).resolve().parents[2]
LIB_SH = kit_pfad("lib.sh")

# Zusammengesetzt, nicht geschrieben: `kit-test.sh` Schritt 3 durchsucht den
# ausgelieferten Baum nach UNGEFUELLTEN Platzhaltern. Stuende die Marke hier
# woertlich, meldete der Selbsttest diesen Test als Fund — und der Waechter
# haette recht. Ein Test darf die Zusicherung, die er prueft, nicht selbst
# verletzen.
#
# `"".join(...)` und nicht `"{{" + "PYTHON" + "}}"`: Die Addition von
# Literalen faltet der Compiler zu EINER Konstanten zusammen, und die steht
# dann woertlich im .pyc — der erste Versuch war im Quelltext sauber und im
# Bytecode nicht. Ein Methodenaufruf wird nicht gefaltet.
MARKE = "".join(("{{", "PYTHON", "}}"))


def _quelle(*kandidaten):
    for kandidat in kandidaten:
        pfad = WURZEL / kandidat
        if pfad.is_file():
            return pfad
    pytest.skip(f"keine der Quellen liegt in dieser Ablage: {kandidaten}")


# --- Die Bibliothek ---------------------------------------------------------

def test_lib_sh_ruft_python_nicht_mehr_unter_festem_namen():
    """Der Kern des Fundes: dreizehn Aufrufstellen."""
    funde = []
    for nummer, zeile in enumerate(
            LIB_SH.read_text(encoding="utf-8").splitlines(), 1):
        ohne_kommentar = zeile.split("#", 1)[0]
        # Der Default-Zeile selbst ist der feste Name erlaubt — sie ist der
        # eine Ort, an dem er stehen SOLL (Vertrag Punkt 6).
        if "TEAM_PYTHON=" in ohne_kommentar:
            continue
        if re.search(r"(?<![\w./-])python3?(?=\s+(?:-c|-m|-\s|-\b|\S))",
                     ohne_kommentar):
            funde.append(f"{nummer}: {zeile.strip()}")
    assert not funde, (
        "Diese Stellen in lib.sh rufen Python unter einem festen Namen auf. "
        "Unter Windows ist `python3` der Store-Alias (BL-131) — der Aufruf "
        'endet mit 49 und "Python was not found".\n  ' + "\n  ".join(funde))


def test_lib_sh_setzt_den_default_greppbar():
    """Vertrag Punkt 6: Der eigene Default der Bibliothek steht in einer Zeile,
    die ein Test statisch lesen kann."""
    quelle = LIB_SH.read_text(encoding="utf-8")
    assert re.search(r'^TEAM_PYTHON="\$\{TEAM_PYTHON:-python3\}"$',
                     quelle, re.M), \
        "lib.sh muss TEAM_PYTHON als eigenen Default setzen (POSIX: python3)"


def test_die_werkzeuge_folgen_dem_aufgeloesten_namen(tmp_path):
    """Die Wirkung: Wer TEAM_PYTHON setzt, verschiebt BEIDE Werkzeugzeilen mit.
    Sonst zeigt der Name an einer Stelle woanders hin als an der anderen."""
    verlange_bash()
    config = tmp_path / "team.config.sh"
    config.write_text(
        'TEAM_PYTHON="pythonXY"\n'
        'TEAM_BEUTEBUCH_TOOL="${TEAM_BEUTEBUCH_TOOL:-$TEAM_PYTHON team/tools/beutebuch.py}"\n'
        'TEAM_KOSTEN_TOOL="${TEAM_KOSTEN_TOOL:-$TEAM_PYTHON team/tools/kosten.py}"\n',
        encoding="utf-8")
    ergebnis = subprocess.run(
        [BASH, "-c", f'source "{config}"; printf "%s|%s" '
                     f'"$TEAM_KOSTEN_TOOL" "$TEAM_BEUTEBUCH_TOOL"'],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert ergebnis.returncode == 0, ergebnis.stderr
    kosten, beutebuch = ergebnis.stdout.split("|")
    assert kosten == "pythonXY team/tools/kosten.py"
    assert beutebuch == "pythonXY team/tools/beutebuch.py"


# --- Die Konfiguration ------------------------------------------------------

def test_beide_config_vorlagen_tragen_den_platzhalter():
    """Der Grund, warum ein Windows-Projekt eine halb kaputte Konfiguration
    bekam: Die .ps1 hatte den Platzhalter, die .sh nicht."""
    for kandidat, praefix in (("bash/entry/team.config.sh", "TEAM_PYTHON="),
                              ("pwsh/entry/team.config.ps1", "")):
        vorlage = WURZEL / kandidat
        if not vorlage.is_file():
            continue
        text = vorlage.read_text(encoding="utf-8-sig")
        assert MARKE in text, (
            f"{kandidat} traegt keinen {MARKE}-Platzhalter — der Installer "
            "kann dort nichts einsetzen, und der Name bleibt der der Bauzeit "
            "statt der der Maschine (BL-131).")
        if praefix:
            assert re.search(praefix + r'.*' + re.escape(MARKE), text), (
                f"{kandidat} fuellt den Platzhalter nicht in TEAM_PYTHON — "
                "dann haengen die Werkzeugzeilen wieder an einem festen Namen")


# --- Der Installer ----------------------------------------------------------

def test_beide_installer_fragen_plattformgerecht():
    """Die Reihenfolge muss unter Windows `python` VOR `python3` stellen —
    sonst greift der Store-Alias, bevor der echte Interpreter drankommt.
    Gefordert wird beides: die Reihenfolge und eine Plattformabfrage."""
    faelle = [
        (_quelle("bash/install.sh"), r"python\s+python3\s+py", "uname"),
        (_quelle("pwsh/install.ps1"), r"'python',\s*'python3',\s*'py'",
         r"\$IsWindows"),
    ]
    for quelle, reihenfolge, plattform in faelle:
        text = quelle.read_text(encoding="utf-8-sig")
        assert re.search(reihenfolge, text), (
            f"{quelle.name} stellt unter Windows nicht `python` vor "
            "`python3` (BL-131/BL-122)")
        assert re.search(plattform, text), (
            f"{quelle.name} entscheidet die Reihenfolge nicht an der "
            "Plattform — dann gilt sie ueberall gleich und ist irgendwo falsch")


def test_installer_prueft_start_und_version():
    """Ein blosses `command -v` findet den Store-Alias. Die Probe muss den
    Interpreter WIRKLICH starten — das ist der Unterschied, an dem BL-122
    haengt, und er gilt auf beiden Bahnen."""
    quelle = _quelle("bash/install.sh")
    text = quelle.read_text(encoding="utf-8")
    block = re.search(r"finde_python\(\)\s*\{.*?\n\}", text, re.S)
    assert block, "finde_python() ist in install.sh nicht mehr auffindbar"
    assert "version_info" in block.group(0), (
        "finde_python() prueft nicht die Version — `command -v` allein findet "
        "auch den Store-Alias und ein Python 2 (BL-131)")


def test_resolver_ueberspringt_einen_store_alias(tmp_path):
    """Der Nachweis am Verhalten statt am Text — und er laeuft auf JEDEM Wirt.

    Der Store-Alias laesst sich nachstellen: eine Datei namens `python3`, die
    existiert, startet, die Store-Meldung schreibt und mit 49 endet. Genau
    daran scheitert ein `command -v`-Test, und genau das ist der Grund, warum
    `finde_python()` START UND VERSION prueft (Lehre BL-122).

    Gefahren wird die Funktion ISOLIERT aus install.sh — der Installer selbst
    wuerde ein Zielprojekt anlegen wollen.
    """
    verlange_bash()
    quelle = _quelle("bash/install.sh").read_text(encoding="utf-8")
    block = re.search(r"finde_python\(\)\s*\{.*?\n\}", quelle, re.S)
    assert block, "finde_python() ist in install.sh nicht mehr auffindbar"

    fake = tmp_path / "bin"
    fake.mkdir()
    alias = fake / "python3"
    alias.write_text(
        "#!/bin/sh\n"
        "echo 'Python was not found; run without arguments to install from "
        "the Microsoft Store' >&2\n"
        "exit 49\n", encoding="utf-8")
    alias.chmod(0o755)
    (fake / "python").symlink_to(sys.executable)

    ergebnis = subprocess.run(
        [BASH, "-c", block.group(0) + "\nfinde_python\n"],
        env={"PATH": f"{fake}", "HOME": str(tmp_path)},
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert ergebnis.returncode == 0, (
        "finde_python() hat gar nichts gefunden, obwohl ein lauffaehiges "
        f"`python` liegt.\nSTDERR:\n{ergebnis.stderr}")
    assert ergebnis.stdout.strip() == "python", (
        "finde_python() hat den Store-Alias genommen. `command -v` findet ihn "
        "— nur ein echter Start entlarvt ihn (BL-122/BL-131).\n"
        f"Gewaehlt wurde: {ergebnis.stdout.strip()!r}")


def test_installer_verdrahtet_python3_nicht_mehr_in_die_ersetzung():
    quelle = _quelle("bash/install.sh")
    funde = [
        f"{n}: {z.strip()}"
        for n, z in enumerate(quelle.read_text(encoding="utf-8").splitlines(), 1)
        if f'("{MARKE}"' in z and "python_name" not in z
    ]
    assert not funde, (
        f"Der Installer setzt fuer {MARKE} einen festen Namen statt des "
        "gefundenen ein (BL-131):\n  " + "\n  ".join(funde))

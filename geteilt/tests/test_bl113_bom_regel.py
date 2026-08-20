"""BL-113: Die Kodierungsregel — PowerShell-Quelltext MIT BOM, alles andere OHNE.

WARUM DIESER TEST EXISTIERT
    Auf der ersten echten Windows-Maschine startete keine einzige Datei der
    pwsh-Bahn. `kit-einrichten.ps1` brach mit zehn Syntaxfehlern ab:

        Unexpected token 'wird' in expression or statement.
        Missing argument in parameter list.
        Missing closing ')' in subexpression.

    Kein Syntaxfehler war echt. Windows PowerShell 5.1 liest eine Datei OHNE
    BOM nicht als UTF-8, sondern in der ANSI-Codepage der Maschine (bei uns
    1252). Der Geviertstrich U+2014 steht in UTF-8 als E2 80 94; in 1252
    gelesen sind das drei Zeichen, und das letzte ist U+201D — ein
    typografisches Anfuehrungszeichen. PowerShell akzeptiert die als echte
    Stringgrenze. Jeder Gedankenstrich in einer Zeichenkette SCHLIESST sie
    also mitten im Satz, der Rest der Zeile zerfaellt in nackte Bezeichner.

    Das Kit hat 443 Geviertstriche in seinen PowerShell-Dateien.

WAS DARAN DIE EIGENTLICHE LEHRE IST
    Der Fehler tritt VOR der ersten Zeile Code auf. `kit-einrichten.ps1`
    enthaelt eine Versionspruefung, die genau diesen Fall erklaeren wuerde
    ("PowerShell 5.1 ist zu alt — nimm pwsh 7"). Sie wird nie erreicht: Die
    Datei stirbt beim Parsen. Der Anwender bekommt statt eines Hinweises einen
    Wall aus Folgefehlern, die alle auf harmlose deutsche Prosa zeigen.

    Und er war unter Linux nicht messbar. pwsh 7 liest UTF-8 ohne BOM korrekt,
    auf jeder Plattform. Die gesamte pwsh-Bahn ist gegen pwsh 7 gefahren
    worden, kit-test.sh war gruen, die Doppelbahn lief — waehrend auf dem
    Ziel nichts startete. Ein Test, der nur die eigene Maschine kennt, kann
    das nicht finden. Ein Test, der die BYTES prueft, findet es ueberall.

DIE KEHRSEITE GEHOERT DAZU
    Die Regel ist nicht "BOM ist gut". Vor einer Shebang-Zeile macht ein BOM
    aus `#!/usr/bin/env bash` Zeichensalat, und Pythons `json.load` bricht
    darueber ab — kosten.py hat eine so verdorbene Datei stillschweigend als
    0.0000 gezaehlt (siehe test_stufe3_kostenlog_kodierung.py). Deshalb
    prueft dieser Test BEIDE Haelften: Waere nur die eine unter Test, koennte
    sie jemand "vereinheitlichen" und dabei die andere brechen.

WARUM HIER UND NICHT NUR IN kit-test.sh
    kit-test.sh prueft das Kit. Dieser Test laeuft im INSTALLIERTEN Projekt
    und prueft, was dort tatsaechlich liegt — also auch das, was ein
    Installer beim Fuellen der Platzhalter neu geschrieben hat. Genau dort
    ist die Kodierung schon einmal verloren gegangen.
"""
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]
BOM = b"\xef\xbb\xbf"

# Bewusst aufgezaehlt statt rekursiv gesucht: Ein installiertes Projekt hat
# eigenen Code, virtuelle Umgebungen und fremde Abhaengigkeiten. Geprueft wird,
# was das Kit ausliefert — fuer alles andere ist dieser Test nicht zustaendig.
# Beide Ablagen in einer Liste: die installierte (Wurzel, team/) und die
# des Kits (bash/, pwsh/, geteilt/). Ein nicht passendes Muster liefert
# einfach nichts — geprueft wird, was da ist.
MIT_BOM = ("*.ps1", "team/*.ps1", "team/*.psm1", "scripts/*.ps1",
           "entry/*.ps1",
           "pwsh/*.ps1", "pwsh/*.psm1", "pwsh/entry/*.ps1",
           "pwsh/scripts/*.ps1")
OHNE_BOM = ("*.sh", "team/*.sh", "scripts/*.sh", "entry/*.sh",
            "team/tools/*.py", "team/tests/*.py",
            "bash/*.sh", "bash/entry/*.sh", "bash/scripts/*.sh",
            "geteilt/*.py", "geteilt/tools/*.py", "geteilt/tests/*.py")


def _dateien(muster):
    treffer = []
    for m in muster:
        treffer.extend(sorted(p for p in WURZEL.glob(m) if p.is_file()))
    return treffer


def test_powershell_quelltext_traegt_bom():
    dateien = _dateien(MIT_BOM)
    assert dateien, "keine PowerShell-Dateien gefunden — Muster stimmt nicht mehr"
    ohne = [p.relative_to(WURZEL).as_posix()
            for p in dateien if not p.read_bytes().startswith(BOM)]
    assert not ohne, (
        "Ohne BOM liest Windows PowerShell 5.1 diese Dateien in der "
        "ANSI-Codepage. Jeder Gedankenstrich wird dann zu einer "
        "Stringgrenze und die Datei stirbt beim Parsen: " + ", ".join(ohne))


def test_shell_und_python_tragen_kein_bom():
    dateien = _dateien(OHNE_BOM)
    assert dateien, "keine Shell-/Python-Dateien gefunden — Muster stimmt nicht mehr"
    mit = [p.relative_to(WURZEL).as_posix()
           for p in dateien if p.read_bytes().startswith(BOM)]
    assert not mit, (
        "Ein BOM macht aus der Shebang-Zeile Zeichensalat und laesst "
        "json.load abbrechen — kosten.py zaehlt eine solche Datei still als "
        "0.0000: " + ", ".join(mit))


def test_batchdateien_sind_reines_ascii():
    """`.cmd` liest der Kommandozeileninterpreter in der OEM-Codepage.

    Nicht 1252, nicht UTF-8, sondern 850 oder 437 — je nach Maschine. Reines
    ASCII ist das einzige, was dort ueberall dasselbe bedeutet. Ein BOM waere
    hier sogar schaedlich: Er stuende vor `@echo off` und wuerde als Befehl
    gelesen.
    """
    dateien = _dateien(("*.cmd", "entry/*.cmd", "pwsh/entry/*.cmd"))
    if not dateien:
        return  # Bash-only-Installation: nichts zu pruefen
    schlecht = []
    for p in dateien:
        roh = p.read_bytes().replace(b"\r", b"")
        if any(b > 0x7F for b in roh) or roh.startswith(BOM):
            schlecht.append(p.relative_to(WURZEL).as_posix())
    assert not schlecht, (
        "Nicht-ASCII in einer Batch-Datei bedeutet je nach Codepage der "
        "Maschine etwas anderes: " + ", ".join(schlecht))

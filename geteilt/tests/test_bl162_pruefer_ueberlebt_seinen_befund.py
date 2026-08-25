#!/usr/bin/env python3
"""BL-161 und BL-162: Zwei Fehler in Stufe 11, die nur ein Windows-Lauf zeigt.

Beide stammen aus dem dritten `kit-test.sh`-Lauf auf einer echten
Windows-Maschine (2026-08-24, `BL-146`) — der erste, der Stufe 11 ueberhaupt
erreicht hat. Sie ist die Stufe, auf der "die ganze pwsh-Bahn ruht", und sie
war auf dieser Maschine nie gefahren worden.

BL-162 — DER PRUEFER STARB AN SEINEM EIGENEN BEFUND
    Der Gleichstand der Installer wird so gemessen:

        W_DIFF="$(diff -r --exclude=.git "$W_A" "$W_B" | head -20)"
        w_pruefe "… erzeugen denselben Baum" "${W_DIFF:-identisch}" "identisch"

    `diff` endet mit **1**, wenn es Unterschiede gibt — also genau in dem Fall,
    fuer den diese Pruefung existiert. Unter `set -euo pipefail` reisst das die
    Zuweisung und damit den ganzen Lauf weg, **still und ohne Meldung**: Nach
    sechs Stunden endete der Selbsttest mit Exit 1 und ohne ein Wort darueber,
    was er gefunden hatte.

    Auf Linux ist es nie aufgefallen, weil die Baeume dort immer gleich waren
    und `diff` 0 lieferte. **Ein Pruefer, der nur ueberlebt, solange er nichts
    findet, ist keiner** — dieselbe Gattung wie `BL-111`, nur eine Ebene hoeher:
    dort starb eine Ableitung an ihrem leeren Normalfall, hier ein Test an
    seinem Fund.

BL-161 — DER PFAD UEBER DIE BAHNGRENZE
    Dieselbe Stufe reicht `$KIT` in ein `pwsh -Command` hinein. Als ARGUMENT
    wandelt die MSYS-Schicht von Git-Bash einen Pfad selbst um (deshalb laufen
    die `-File`-Aufrufe unveraendert); INNERHALB eines `-Command`-Strings ist er
    blosser TEXT. PowerShell las `/c/Users/...` als `C:\\c\\Users\\...` und
    meldete "Cannot find path". Die Folge war nicht nur eine rote Zeile: Die
    Syntaxpruefung sah damit **null** PowerShell-Dateien statt achtzehn — sie
    war auf dieser Bahn wirkungslos, und der Fehlertext stand an der Stelle,
    an der sonst die Liste der kaputten Dateien steht.

WARUM DIESE DATEI DIE GATTUNG PRUEFT UND NICHT DIE ZWEI STELLEN
    Eine Liste der bekannten Fundstellen veraltet mit der naechsten neuen —
    dieselbe Lehre wie `BL-154`. Gesucht wird deshalb nach der BAUART in allen
    Skripten der bash-Bahn.
"""
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _bash_skripte():
    ordner = REPO_ROOT / "bash"
    if not ordner.is_dir():
        pytest.skip("die bash-Bahn des Kits liegt hier nicht "
                    "(installiertes Projekt statt Kit-Ablage)")
    return sorted(ordner.rglob("*.sh"))


# --- BL-162: Befehle, die "nichts gefunden" als Fehler melden ---------------
#
# Die Gattung sind Befehle, deren Exit-Code eine AUSSAGE ist und kein Fehler:
# `diff` meldet mit 1 einen Unterschied, `grep` mit 1 "kein Treffer", `cmp` mit
# 1 "ungleich". Steht so einer in einer Zuweisung `VAR="$( … )"`, entscheidet
# sein Status ueber das Leben des Skripts — unter `set -e` ist das der Tod, und
# unter `pipefail` rettet auch ein nachgeschaltetes `head` nicht (BL-111).
AUSSAGE_STATT_FEHLER = ("diff", "cmp")

ZUWEISUNG = re.compile(
    r'^\s*(?:local\s+)?[A-Za-z_][A-Za-z0-9_]*="\$\((?P<rumpf>.*)\)"\s*$')


def _ungeschuetzte_zuweisungen(text):
    funde = []
    for nummer, zeile in enumerate(text.splitlines(), 1):
        treffer = ZUWEISUNG.match(zeile)
        if not treffer:
            continue
        rumpf = treffer.group("rumpf")
        befehl = rumpf.lstrip().split(" ", 1)[0]
        if befehl not in AUSSAGE_STATT_FEHLER:
            continue
        if "|| true" in rumpf or "|| echo" in rumpf:
            continue
        funde.append((nummer, zeile.strip()))
    return funde


def test_kein_pruefer_stirbt_an_seinem_eigenen_befund():
    """Die Zusicherung von BL-162, als Gattung.

    Faellt dieser Fall, gibt es wieder eine Stelle, an der ein Selbsttest
    ABBRICHT statt zu melden — und zwar genau dann, wenn er etwas gefunden hat.
    Der Lauf endet dann nach Stunden mit Exit 1 und ohne Befund.
    """
    funde = []
    for datei in _bash_skripte():
        for nummer, zeile in _ungeschuetzte_zuweisungen(
                datei.read_text(encoding="utf-8")):
            funde.append(f"{datei.relative_to(REPO_ROOT)}:{nummer} — {zeile}")
    assert not funde, (
        "Diese Zuweisungen sterben an einem Befund statt ihn zu melden "
        "(BL-162). `diff`/`cmp` enden mit 1, WENN sie etwas finden; unter "
        "`set -euo pipefail` reisst das den Lauf weg.\n  Abhilfe: `|| true` "
        "in die Ersetzung, die Auswertung macht danach die Pruefung.\n  "
        + "\n  ".join(funde))


def test_der_waechter_wuerde_die_alte_fassung_fangen():
    """Gegenprobe: Ein Waechter, der nie rot wird, sichert nichts ab.

    Die Zeile ist die WOERTLICHE Fassung von vor dem Fix — sie hat den
    sechsstuendigen Lauf umgebracht.
    """
    alt = 'W_DIFF="$(diff -r --exclude=.git "$W_A/projekt" "$W_B/projekt" 2>&1 | head -20)"'
    assert _ungeschuetzte_zuweisungen(alt), (
        "Der Waechter erkennt die Fassung nicht mehr, an der BL-162 gefunden "
        "wurde — dann fängt er auch die naechste nicht.")
    neu = alt[:-1] + ' || true)"'
    assert not _ungeschuetzte_zuweisungen(neu), (
        "Der Waechter schlaegt auch bei der reparierten Fassung an — ein "
        "Fehlalarm, und Waechter mit Fehlalarmen werden abgeschaltet "
        "(BL-143).")


# --- BL-161: Pfade ueber die Bahngrenze -------------------------------------

PWSH_COMMAND = re.compile(r'pwsh[^\n]*-Command\s+"(?P<rumpf>(?:[^"\\]|\\.)*)"',
                          re.S)


def test_kein_msys_pfad_wandert_roh_in_ein_pwsh_command():
    """Die Zusicherung von BL-161, als Gattung.

    Ein Pfad im `-Command`-String ist Text und wird von der MSYS-Schicht nicht
    umgeschrieben. Wer `$KIT` oder `$ZIEL` dort direkt einsetzt, uebergibt
    PowerShell `/c/Users/...` — und das liest es als `C:\\c\\Users\\...`.
    """
    funde = []
    for datei in _bash_skripte():
        text = datei.read_text(encoding="utf-8")
        for treffer in PWSH_COMMAND.finditer(text):
            rumpf = treffer.group("rumpf")
            for name in ("$KIT", "$ZIEL", "$BAHN", "$W_A", "$W_B"):
                if name in rumpf and f'pwsh_pfad "{name}"' not in rumpf:
                    nummer = text.count("\n", 0, treffer.start()) + 1
                    funde.append(
                        f"{datei.relative_to(REPO_ROOT)}:{nummer} — {name}")
    assert not funde, (
        "Diese Stellen reichen einen MSYS-Pfad roh in ein `pwsh -Command` "
        "(BL-161). PowerShell liest '/c/Users/…' als 'C:\\c\\Users\\…' und "
        "meldet 'Cannot find path' — die Pruefung dahinter ist dann "
        "wirkungslos, nicht nur rot.\n  Abhilfe: pwsh_pfad \"$X\" "
        "(cygpath -w, auf POSIX unveraendert).\n  " + "\n  ".join(funde))


def test_die_umrechnung_ist_da_und_faellt_auf_posix_nicht_um():
    """Der Helfer selbst: Er darf auf einem Wirt ohne `cygpath` nichts tun.

    Sonst waere der Fix fuer Windows ein Defekt fuer Linux — und der faellt
    dort erst auf, wenn jemand ihn faehrt.
    """
    # Ueber dieselbe Tuer wie die Faelle darueber: `kit-test.sh` liegt NUR in
    # der Kit-Ablage. Ein installiertes Projekt bekommt den Selbsttest des Kits
    # nicht mitgeliefert, und ein Test, der ihn dort trotzdem oeffnet, ist rot
    # ohne Befund. Genau daran ist Lauf 4 in Stufe 2 gestorben.
    kit_test = REPO_ROOT / "bash" / "kit-test.sh"
    if not kit_test.is_file():
        pytest.skip("kit-test.sh liegt nur in der Kit-Ablage "
                    "(installiertes Projekt statt Kit-Ablage)")
    text = kit_test.read_text(encoding="utf-8")
    assert "pwsh_pfad()" in text, "Die Umrechnung fehlt (BL-161)."
    stelle = text.index("pwsh_pfad()")
    block = text[stelle:stelle + 300]
    assert "command -v cygpath" in block, (
        "pwsh_pfad prueft nicht, ob es cygpath ueberhaupt gibt — auf einem "
        "Linux-Wirt bricht der Aufruf dann ab.")
    assert "printf '%s' \"$1\"" in block, (
        "Ohne cygpath muss der Pfad UNVERAENDERT durchgereicht werden; auf "
        "POSIX ist er bereits richtig.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

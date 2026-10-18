#!/usr/bin/env python3
"""BL-328: Im Rollenlauf war die Kit-Suite rot und ausserhalb gruen — die
Rolle erbte die exportierten Projektwerte, und der Harnisch neutralisierte nur
`TEAM_PREISE`.

WAS IM FELD PASSIERT IST (`Feld G`, 2026-10-12, erste Kaskade)
    Stufe 1 verlangte "`./team-test.sh` gruen". Ralph fuhr den Befehl im
    Rollenlauf und meldete 42 von 1221 Faellen als "schon vor dieser Stufe
    rot". Ausserhalb des Loops war dieselbe Suite auf demselben Stand gruen.
    `team.config.sh` exportiert `TEAM_DOMAENEN` fuer die Werkzeuge, die
    Fixtures buchen auf die Domaene `team`, und `kosten.py` wies sie bei
    `TEAM_DOMAENEN=produkt` ab: 39 Fehlschlaege in zehn Dateien. Bei der
    Triage kamen `TEAM_PLAN_ORDNER` (33 Faelle) und das vom Sperrinhaber
    exportierte `TEAM_LOCK_HELD` (der flock-Fall aus `test_bl190`) dazu.

WARUM ES NIE AUFFIEL
    `team-test.*` laedt die Konfiguration bewusst nicht und reicht die
    geerbte Umgebung durch. Ausserhalb eines Rollenlaufs steht darin nichts,
    und genau dort liefen alle Nachweise. Die Rolle dagegen erbt die Umgebung
    des Entrypoints, der die Konfiguration gesourct hat.

DIE ANTWORT STEHT IM HARNISCH, nicht in `team-test.*`
    `conftest.py` loescht beim Laden jedes `TEAM_*` ausser `TEAM_PYTHON` und
    setzt danach die Harnischwerte. Das schuetzt `./team-test.sh`,
    `team-test.ps1` und den direkten Aufruf von pytest gleichermassen. Die
    Exporte der Konfigurationen bleiben (`BL-209`, `BL-238`) — die Werkzeuge
    brauchen sie im Betrieb.

DIE GATTUNG
    Ein Fall fuer `TEAM_DOMAENEN` sagt ueber den naechsten exportierten Namen
    nichts. Der zweite Teil liest deshalb, was `team.config.*` und die
    Bibliothek je Bahn in die Umgebung legen, und haelt jeden Namen gegen den
    GELADENEN Harnisch (Bauart `test_bl275`): Ein neuer Export ist rot, bis
    der Harnisch ihn neutralisiert oder er hier mit Grund steht.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT, kit_pfad, nur_code, quelle, ueberspringe_ohne_bahn

HIER = Path(__file__).resolve().parent

# --- Der Feldfall, gefahren --------------------------------------------------

# Die Werte, mit denen die Triage den Feldfall nachgestellt hat: eine eigene
# Domaenenliste ohne `team`, ein anderer Planordner, eine gehaltene Sperre.
ROLLENWERTE = {"TEAM_DOMAENEN": "produkt",
               "TEAM_PLAN_ORDNER": "docs/plans/",
               "TEAM_LOCK_HELD": "1"}

# Gegen den alten Stand gemessen: 8 + 8 + 1 rote Faelle. Vom flock-Paar laeuft
# je Maschine genau einer — mit flock der erste, ohne (Git for Windows) der
# zweite —, der andere ueberspringt sich selbst.
ZIELE = (
    "test_stufe43_architekt_abschluss.py",
    "test_bl27_vergessener_abschluss.py",
    "test_bl190_sperre_ohne_flock.py::test_team_lock_mit_flock_nimmt_weiter_flock",
    "test_bl190_sperre_ohne_flock.py::test_team_lock_ohne_flock_sperrt_trotzdem",
)


def test_die_rollenumgebung_macht_die_suite_nicht_rot(tmp_path):
    """Dieselben Dateien in einem eigenen pytest-Lauf, mit der Umgebung einer
    Rolle — so, wie `./team-test.sh` sie im Rollenlauf bekommt."""
    for ziel in ZIELE:
        assert (HIER / ziel.split("::")[0]).is_file(), (
            f"{ziel} fehlt in dieser Ablage — dann prueft dieser Fall nichts")
    umgebung = dict(os.environ, **ROLLENWERTE)
    # Ein PYTEST_ADDOPTS des Wirts (etwa `-k …`) wuerde den inneren Lauf
    # filtern; er soll genau die Ziele fahren, nicht mehr und nicht weniger.
    umgebung.pop("PYTEST_ADDOPTS", None)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         f"--basetemp={tmp_path / 'innen'}", *(str(HIER / z) for z in ZIELE)],
        cwd=REPO_ROOT, env=umgebung, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600)
    ausgabe = r.stdout + r.stderr
    assert r.returncode == 0, (
        "Mit der Umgebung einer Rolle ist die Suite rot — der Harnisch laesst "
        "Projektwerte der Sitzung an die Fixtures (Kit-BL-328):\n"
        + ausgabe[-3000:])
    bestanden = re.search(r"(\d+) passed", r.stdout)
    assert bestanden and int(bestanden.group(1)) >= 20, (
        "Der innere Lauf ist gruen, hat aber kaum etwas gefahren — gruen "
        "hiesse hier nur: nichts gesehen.\n" + ausgabe[-3000:])


# --- Die Gattung: was eine Bahn in die Umgebung legt -------------------------

EXPORT_BASH = re.compile(r"(?:^|[;&|(]|\s)export\s+([A-Za-z_][A-Za-z0-9_]*)",
                         re.M)
EXPORT_PWSH = re.compile(r"\$env:([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)", re.I)
# Die Schreibweisen, die der Parser NICHT liest. Das Kit benutzt sie heute
# nicht; kaeme eine dazu, saehe der Fall ihren Export nicht und bliebe still
# gruen. Deshalb ein Stolperdraht statt eines stillen Lochs.
ANDERE_SCHREIBWEISEN = {
    "bash": re.compile(r"\b(?:declare|typeset)\s+-[A-Za-z]*x"),
    "pwsh": re.compile(r"SetEnvironmentVariable|(?:Set|New)-Item\s+[^\n]*Env:",
                       re.I),
}

# Die Werte, die der Harnisch nach dem Loeschen SELBST setzt (BL-312, BL-323).
# Steht ein Name danach mit genau diesem Wert da, ist er neutral.
HARNISCHWERTE = {"TEAM_BENACHRICHTIGUNG": "0", "TEAM_PREISE": ""}

# Was der Harnisch BEWUSST stehen laesst, mit Grund — damit ein neuer Export
# nicht still dazukommt. Beide Namen liegen ausserhalb von TEAM_*: Sie sind
# kein Projektwert, sondern der Anmeldeweg der Sitzung.
BEWUSST_STEHEN_GELASSEN = {
    "ANTHROPIC_API_KEY": (
        "der Schluessel der Sitzung; die Bibliothek exportiert ihn im "
        "API-Fallback. Tests, die von ihm abhaengen, setzen oder entfernen ihn "
        "selbst (test_bl27_abo_key_startwarnung, test_bl48, test_hm33, "
        "test_bl173, test_bl301). Bei BL-328 gemessen: Mit AUTH_MODE=api und "
        "einem Schluessel in der Umgebung bleibt die Kit-Suite auf der "
        "bash-Bahn unveraendert."),
    "AUTH_MODE": (
        "der Anmeldeweg der Sitzung; ausdruecklich exportiert nur lib.psm1. "
        "Die Triage zu BL-328 fand keine Wirkung auf die Suite; auf der "
        "bash-Bahn gemessen wie oben, auf der pwsh-Bahn ungeprueft."),
}

QUELLEN = {
    ("bash", "konfiguration"): lambda: quelle("bash/entry/team.config.sh"),
    ("bash", "bibliothek"): lambda: kit_pfad("lib.sh"),
    ("pwsh", "konfiguration"): lambda: quelle("pwsh/entry/team.config.ps1"),
    ("pwsh", "bibliothek"): lambda: kit_pfad("lib.psm1"),
}

# Ein Name, den die Datei sicher exportiert. Fehlt er im Ergebnis, liest der
# Parser die Datei nicht mehr — und gruen hiesse nur: nichts gesehen.
ANKER = {"konfiguration": "TEAM_DOMAENEN", "bibliothek": "TEAM_LOCK_HELD"}


def exporte(text, bahn):
    """Die Namen, die eine Datei der Bahn in die Umgebung legt — ohne die
    Erwaehnungen in Kommentaren (`nur_code`)."""
    muster = EXPORT_BASH if bahn == "bash" else EXPORT_PWSH
    return set(muster.findall(nur_code(text)))


def nach_dem_harnisch(namen, marke="bl328-sitzungswert"):
    """{name: wert oder None} — was von einer Sitzung, in der jeder Name mit
    `marke` gesetzt ist, nach dem LADEN des Harnischs uebrig bleibt.

    Gefragt wird der echte Harnisch in einem eigenen Prozess: Die Regel ist
    eine Eigenschaft des Ladens, und ein zweiter Import im laufenden Prozess
    laese nur den Modul-Zwischenspeicher."""
    namen = sorted(namen)
    sonde = ("import json, os, sys; sys.path.insert(0, sys.argv[1]); "
             "import conftest; "
             "print(json.dumps({n: os.environ.get(n) "
             "for n in sys.argv[2].split(',')}))")
    umgebung = dict(os.environ, **{n: marke for n in namen})
    r = subprocess.run([sys.executable, "-c", sonde, str(HIER), ",".join(namen)],
                       env=umgebung, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def nicht_neutral(zustand, marke="bl328-sitzungswert"):
    """Die Namen, die nach dem Harnisch noch einen Wert der Sitzung tragen —
    oder geleert statt geloescht sind. Geleert ist nicht neutral: Fuer
    `kit_meldung.py` und `schreibzone.py` ist ein leerer `TEAM_PLAN_ORDNER`
    die Projektwurzel."""
    falsch = {}
    for name, wert in zustand.items():
        if wert is None or HARNISCHWERTE.get(name) == wert:
            continue
        if name in BEWUSST_STEHEN_GELASSEN:
            continue
        falsch[name] = "Sitzungswert" if wert == marke else f"Wert {wert!r}"
    return falsch


@pytest.mark.parametrize("bahn,art", sorted(QUELLEN))
def test_kein_exportierter_name_ueberlebt_den_harnisch(bahn, art):
    ueberspringe_ohne_bahn(bahn)
    datei = QUELLEN[(bahn, art)]()
    if not datei.is_file():
        pytest.skip(f"{datei.name} liegt in dieser Ablage nicht")
    text = datei.read_text(encoding="utf-8-sig")
    andere = ANDERE_SCHREIBWEISEN[bahn].search(nur_code(text))
    assert not andere, (
        f"{datei.name} setzt eine Umgebungsvariable mit "
        f"`{andere.group(0)}` — diese Schreibweise liest exporte() nicht. "
        f"Erst den Parser ergaenzen, sonst prueft dieser Fall den Export nicht.")
    namen = exporte(text, bahn)
    assert ANKER[art] in namen, (
        f"Vorbedingung: {datei.name} exportiert {ANKER[art]} — der Parser "
        f"findet ihn nicht, also prueft dieser Fall nichts. Gefunden: "
        f"{sorted(namen)}")
    falsch = nicht_neutral(nach_dem_harnisch(namen))
    assert not falsch, (
        f"{datei.name} ({bahn}) legt diese Namen in die Umgebung, und der "
        f"Harnisch laesst sie stehen — im Rollenlauf erreichen sie jeden "
        f"Test, der os.environ erbt:\n  "
        + "\n  ".join(f"{n}: {w}" for n, w in sorted(falsch.items()))
        + "\nLoeschen in conftest.py (Kit-BL-328) oder hier mit Grund in "
          "BEWUSST_STEHEN_GELASSEN eintragen.")


def test_ein_neuer_team_name_ist_ohne_nachtrag_neutral():
    """Die Regel gilt fuer den Praefix, nicht fuer eine Liste — ein Export,
    den es heute noch nicht gibt, ist ohne Nachtrag im Harnisch neutral.

    Zugleich die Gegenprobe zum Parser: Eine Erwaehnung im Kommentar und ein
    blosser Vergleich sind kein Export (die Falle aus `test_bl275`)."""
    bash = ("# export TEAM_NUR_IM_KOMMENTAR\n"
            "export TEAM_ERFUNDEN_BL328=1\n"
            '[ -n "$TEAM_NUR_GELESEN" ] && echo ja\n')
    pwsh = ("<# $env:TEAM_NUR_IM_BLOCK = 1 #>\n"
            "$env:TEAM_ERFUNDEN_PWSH = 'x'\n"
            "if ($env:TEAM_NUR_VERGLICHEN -eq '1') { }\n")
    assert exporte(bash, "bash") == {"TEAM_ERFUNDEN_BL328"}
    assert exporte(pwsh, "pwsh") == {"TEAM_ERFUNDEN_PWSH"}
    # Der Stolperdraht schlaegt an, wo der Parser blind waere — und nur dort.
    assert ANDERE_SCHREIBWEISEN["bash"].search("declare -gx TEAM_X=1")
    assert not ANDERE_SCHREIBWEISEN["bash"].search("declare -a liste=()")
    assert ANDERE_SCHREIBWEISEN["pwsh"].search(
        "[Environment]::SetEnvironmentVariable('TEAM_X', '1')")
    zustand = nach_dem_harnisch({"TEAM_ERFUNDEN_BL328", "TEAM_ERFUNDEN_PWSH",
                                 "TEAM_PLAN_ORDNER", "TEAM_PYTHON"})
    assert not nicht_neutral({n: w for n, w in zustand.items()
                              if n != "TEAM_PYTHON"}), zustand
    # TEAM_PYTHON ist die Ausnahme mit Grund (BL-133): eine Angabe ueber die
    # MASCHINE, kein Projektwert. Der Harnisch laesst den Wert der Sitzung.
    assert zustand["TEAM_PYTHON"] == "bl328-sitzungswert", zustand


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

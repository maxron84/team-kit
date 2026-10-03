#!/usr/bin/env python3
"""BL-275: `TEAM_GATE_DATEI` wurde aus `lib.psm1` nicht exportiert — und der
Bericht ueber ein rotes Gate stuerzte genau dann ab, wenn er gebraucht wurde.

WAS IM FELD PASSIERT IST (`Feld B`, 2026-09-17 und 2026-09-22)
    `BL-256` fuehrte die Gate-Datei ein. Geschrieben und geprueft wird sie in
    der Bibliothek, vorgelesen in `vollautomatik.ps1` — also AUSSERHALB des
    Moduls, und dort war die Variable `$null`. Im roten Fall kam statt der
    Liste der roten Tests `Cannot bind argument to parameter 'Path' because it
    is null`, und die Handlungsanweisung hatte ein Loch, wo der Dateiname
    stehen sollte. Dreimal aufgetreten (Ende der Kaskaden 25, 26 und 30). Die
    Gate-Datei trug elf Zeilen, die alle sagten *„vorbestehend, unberuehrt von
    dieser Stufe"* — genau die Zeile, die `BL-256` kostbar macht, verschluckte
    der Absturz.

DIE GATTUNG, und sie ist der Grund fuer diese Datei
    `BL-182` hat dieselbe Bauform schon einmal abgestellt, fuer
    `TEAM_KIT_PFAD`, drei Zeilen ueber der Luecke kommentiert. Die Gattung blieb
    offen und kam ueber `BL-256` zurueck — LAUTLOS, weil PowerShell eine nicht
    exportierte Variable zu `$null` aufloest, statt zu klagen. Ein Test, der
    nur `TEAM_GATE_DATEI` prueft, sagt ueber die naechste Variable nichts.
    Gebaut ist deshalb die Pruefung, die die Meldung ausformuliert und in
    beide Richtungen gemessen mitgebracht hat.

ZWEI FALLEN, beide im Feld beim Bauen aufgelaufen und hier uebernommen
    * `rindex`, nicht `index`: `lib.psm1` erwaehnt `Export-ModuleMember` schon
      im Kopfkommentar. Die erste Fassung im Feld las den halben Modulkopf als
      Exportliste, kam auf 81 statt 47 Namen — und meldete GRUEN.
    * Kommentare ausblenden: Sonst wird die Pruefung an der Dokumentation
      ihres eigenen Anlasses rot (`kit-melden.ps1` beschreibt `BL-182` mit
      `$TEAM_PYTHON` im Kommentar).
    Dazu eine dritte, hier gefunden: Nur Dateien zaehlen, die das Modul
    wirklich IMPORTIEREN. `install.ps1` nennt `$TEAM_PYTHON` in Ausgabetexten
    und importiert die Bibliothek nie — dort gibt es keine Modulgrenze.
"""
import re
import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT, kit_pfad, nur_code

IMPORT = re.compile(r"Import-Module\s+[^\n]*lib\.psm1")
GELESEN = re.compile(r"\$(TEAM_[A-Z0-9_]+)")
ZUWEISUNG = re.compile(r"^\s*\$(TEAM_[A-Z0-9_]+)\s*=", re.M)


def exportliste(text):
    """Die Namen aus dem LETZTEN `Export-ModuleMember` — `rindex`, weil der
    Kopfkommentar das Wort schon einmal nennt (die erste Falle)."""
    anfang = text.rindex("Export-ModuleMember")
    ende = text.index("\n)", anfang)
    return set(re.findall(r"'([A-Za-z0-9_]+)'", nur_code(text[anfang:ende])))


def fehlende_exporte(lesende, exportiert):
    """Die eigentliche Pruefung als reine Funktion — damit die Gegenproben
    synthetisch laufen koennen, ohne das echte Modul zu veraendern.

    `lesende`: {dateiname: quelltext}. Gemeldet wird je Datei, was sie als
    `$TEAM_*` liest, ohne es selbst zuzuweisen, und was das Modul nicht
    exportiert. `$env:TEAM_*` ist eine Umgebungsvariable und faellt durch das
    Muster nicht hinein.
    """
    fehlend = []
    for name, text in sorted(lesende.items()):
        code = nur_code(text)
        if not IMPORT.search(code):
            continue
        lokal = set(ZUWEISUNG.findall(code))
        for v in sorted(set(GELESEN.findall(code)) - lokal - exportiert):
            fehlend.append((name, v))
    return fehlend


def _modul():
    pfad = kit_pfad("lib.psm1")
    if not pfad.is_file():
        pytest.skip("lib.psm1 liegt in dieser Ablage nicht (pwsh-Bahn "
                    "abgewaehlt)")
    return pfad.read_text(encoding="utf-8-sig")


def _lesende_dateien():
    """Alles, was das Modul importiert: Entrypoints und `redteam.ps1`, in
    beiden Ablagen (Kit: `pwsh/entry/`, Installation: Wurzel und `team/`)."""
    kandidaten = set(REPO_ROOT.glob("pwsh/entry/*.ps1"))
    kandidaten |= set(REPO_ROOT.glob("*.ps1"))
    kandidaten.add(kit_pfad("redteam.ps1"))
    return {p.name: p.read_text(encoding="utf-8-sig")
            for p in sorted(kandidaten)
            if p.is_file() and not p.name.startswith("team.config")}


# --- Der Fall aus dem Feld, und die Gattung ---------------------------------

def test_die_gate_datei_ist_exportiert():
    """Der Einzelfall — der Fall, an dem das Feld dreimal abgestuerzt ist."""
    assert "TEAM_GATE_DATEI" in exportliste(_modul()), (
        "TEAM_GATE_DATEI fehlt in der Exportliste von lib.psm1 — "
        "vollautomatik.ps1 liest sie und bekommt $null (BL-275).")


def test_jede_gelesene_modulvariable_ist_exportiert():
    """Die Gattung: Jede `$TEAM_*`-Variable, die eine Datei liest, die das
    Modul importiert, muss in der Exportliste stehen."""
    exportiert = exportliste(_modul())
    lesende = _lesende_dateien()
    assert any(IMPORT.search(nur_code(t)) for t in lesende.values()), (
        "Keine Datei dieser Ablage importiert lib.psm1 — dann prueft dieser "
        "Fall nichts, und gruen hiesse nur: nichts gesehen.")
    fehlend = fehlende_exporte(lesende, exportiert)
    assert not fehlend, (
        "Diese Variablen liest ein Entrypoint, aber lib.psm1 exportiert sie "
        "nicht — PowerShell loest sie dort zu $null auf, ohne zu klagen:\n  "
        + "\n  ".join(f"{d}: ${v}" for d, v in fehlend)
        + "\nNachtragen in `Export-ModuleMember -Variable @(...)` am Ende von "
          "lib.psm1 (BL-182, BL-275).")


def test_die_exportliste_ist_die_am_ende_und_nicht_der_kopfkommentar():
    """Die erste Falle als eigener Fall: Mit `index` statt `rindex` laese die
    Pruefung den Kopfkommentar als Liste und wuerde gruen, weil sie zu VIEL
    fuer exportiert haelt."""
    text = _modul()
    assert text.count("Export-ModuleMember") >= 2, (
        "Vorbedingung: der Kopfkommentar nennt Export-ModuleMember — sonst "
        "prueft dieser Fall seine Falle nicht mehr.")
    liste = exportliste(text)
    assert "TEAM_SMOKE_TEST" in liste and len(liste) < 80, (
        f"{len(liste)} Namen — das ist nicht die Exportliste am Ende.")


# --- Gegenproben: der Waechter wird rot, und nur dann ------------------------

def test_eine_vergessene_variable_wird_gemeldet():
    """Ohne diesen Fall bliebe der Waechter gruen, sobald die Menge leer ist
    — die BL-22-Falle."""
    datei = {"vollautomatik.ps1": "Import-Module ./team/lib.psm1\n"
                                  "Get-Content $TEAM_GATE_DATEI\n"}
    assert fehlende_exporte(datei, {"TEAM_SMOKE_TEST"}) == [
        ("vollautomatik.ps1", "TEAM_GATE_DATEI")]


def test_eine_erwaehnung_im_kommentar_wird_nicht_gemeldet():
    """Die zweite Falle: Eine Pruefung, die an der Beschreibung ihres
    eigenen Anlasses rot wird, wird abgeschaltet (BL-14)."""
    datei = {"kit-melden.ps1": "Import-Module ./team/lib.psm1\n"
                               "# BL-182: $TEAM_PYTHON kam nie an\n"
                               "<# und hier $TEAM_KIT_PFAD #>\n"}
    assert fehlende_exporte(datei, set()) == []


def test_eine_datei_ohne_import_wird_nicht_gemeldet():
    """Die dritte Falle: Ohne Import gibt es keine Modulgrenze — ein
    Ausgabetext mit `$TEAM_PYTHON` im Installer ist kein Lesezugriff auf das
    Modul."""
    datei = {"install.ps1": 'Write-Host "TEAM_PYTHON=`$TEAM_PYTHON"\n'}
    assert fehlende_exporte(datei, set()) == []


def test_eine_lokal_zugewiesene_variable_wird_nicht_gemeldet():
    datei = {"x.ps1": "Import-Module ./team/lib.psm1\n"
                      "$TEAM_EIGENES = 'a'\nWrite-Host $TEAM_EIGENES\n"}
    assert fehlende_exporte(datei, set()) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

#!/usr/bin/env python3
"""BL-261: Der rote Ausgang des Updates sagt nicht, WESSEN Datei gescheitert ist
— und liest sich deshalb wie ein gescheitertes Update.

DER FELDBEFUND
    `install.ps1 --update` lief durch, die Infrastruktur kam an, und am Ende
    stand `[x] Regressionstests NICHT gruen` plus drei Zeilen Log. Der rote
    Fall war `test_bl135_kodierung_an_der_prozessgrenze.py` — und die Datei,
    die er meinte, war `scripts/ga-projekt-export-messung.ps1`: ein
    **Messwerkzeug des PROJEKTS**, das das Update nie angefasst hat. Der Befund
    war sachlich richtig (das Skript faengt die Ausgabe von `curl.exe` auf,
    ohne die Kodierung zu setzen); nur hatte er mit dem Update nichts zu tun.

WARUM DAS EIN KIT-FEHLER IST UND NICHT NUR EINE UNGLUECKLICHE LAGE
    In einer INSTALLATION prueft die Suite bewusst auch den Code des Projekts
    — `scripts/*.ps1` und die Entrypoints in der Wurzel stehen in den Globs von
    `test_bl135`, und das ist richtig so: Die Kodierungsfalle trifft
    Projektskripte genauso. Die MELDUNG des Installers kennt diese
    Unterscheidung aber nicht. Sie nennt einen Testnamen — und Testnamen liegen
    IMMER unter `team/tests/`, also sieht jeder roten Fall wie einen Fehler des
    Kits aus.

    Der Schaden ist eine falsche Schlussfolgerung an der teuersten Stelle: Wer
    glaubt, das Update sei gescheitert, faehrt es erneut oder rollt es zurueck
    — und beides ist falsch. Die Dateien LIEGEN bereits, und genau davor warnt
    der naechste Absatz derselben Ausgabe (`BL-10`: uncommittete Update-Dateien
    raeumt der naechste Read-Only-Lauf weg).

WAS DIESER TEST PRUEFT
    Dass beide Bahnen an dieser Stelle drei Dinge sagen: (1) die Dateien sind
    installiert, (2) der Ausgang bewertet den Suitenstand, (3) ein roter Fall
    kann eine Datei des PROJEKTS meinen. Geprueft wird die Zusicherung, nicht
    der Wortlaut — und auf beiden Bahnen, weil eine Meldung, die nur eine Bahn
    kennt, die andere im Dunkeln laesst (`BL-229`).
"""
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]

INSTALLER = {
    "bash": WURZEL / "bash" / "install.sh",
    "pwsh": WURZEL / "pwsh" / "install.ps1",
}

# Der Block, um den es geht: die Stelle, an der das Update seinen roten Ausgang
# meldet. Gesucht wird die Umgebung, nicht die Zeile — sie darf umformuliert
# werden, solange die Zusicherung bleibt.
ROTES_GATE = re.compile(r"Regressionstests NICHT gr[uü]e?n.{0,1600}",
                        re.S)


def _block(bahn):
    pfad = INSTALLER[bahn]
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt in dieser Ablage nicht")
    treffer = ROTES_GATE.search(pfad.read_text(encoding="utf-8"))
    assert treffer, (
        f"In {pfad.name} gibt es die Stelle nicht mehr, an der das Update "
        "seinen roten Ausgang meldet — dann ist dieses Muster veraltet.")
    return treffer.group(0)


@pytest.mark.parametrize("bahn", sorted(INSTALLER))
def test_sagt_dass_die_dateien_installiert_sind(bahn):
    """Der teuerste Fehlschluss: Das Update sei gescheitert, man muesse es
    wiederholen oder zuruecknehmen."""
    assert "SIND installiert" in _block(bahn), (
        f"{INSTALLER[bahn].name} sagt beim roten Gate nicht, dass die Dateien "
        "bereits liegen (BL-261).")


@pytest.mark.parametrize("bahn", sorted(INSTALLER))
def test_trennt_suitenstand_vom_update(bahn):
    assert "SUITENSTAND" in _block(bahn), (
        f"{INSTALLER[bahn].name} sagt nicht, WORUEBER der rote Ausgang etwas "
        "aussagt (BL-261).")


@pytest.mark.parametrize("bahn", sorted(INSTALLER))
def test_nennt_den_eigentuemer_des_roten_falls(bahn):
    """Der Kern: Ein roter Fall kann eine Datei des PROJEKTS meinen, obwohl der
    Testname immer unter `team/tests/` steht."""
    block = _block(bahn)
    assert "DEINEN Code" in block, (
        f"{INSTALLER[bahn].name} sagt nicht, dass die Suite in einer "
        "Installation auch den Code des Projekts prueft (BL-261).")
    assert "BL-261" in block, (
        f"{INSTALLER[bahn].name} nennt den Eintrag nicht, aus dem die Zeilen "
        "stammen — dann ist die Begruendung nicht nachschlagbar.")


def test_beide_bahnen_sagen_dasselbe():
    """Drift zwischen den Bahnen ist der Fehler, den die Doppelbahn sichtbar
    machen soll."""
    bash, pwsh = _block("bash"), _block("pwsh")
    for merkmal in ("SIND installiert", "SUITENSTAND", "DEINEN Code", "BL-261"):
        assert (merkmal in bash) == (merkmal in pwsh), (
            f"'{merkmal}' steht nur auf einer Bahn (BL-229).")


@pytest.mark.parametrize("bahn", sorted(INSTALLER))
def test_der_rote_ausgang_bleibt_rot(bahn):
    """Gegenrichtung, und sie ist die wichtigere: Die Erklaerung darf den
    Befund nicht ENTSCHAERFEN. Ein rotes Gate bleibt ein rotes Gate — sonst
    waere aus einer unklaren Meldung eine folgenlose geworden, und das ist der
    teurere Fehler (`BL-14`)."""
    block = _block(bahn)
    setzt_fehler = ("FEHLER=1" if bahn == "bash" else "$fehler = 1")
    assert setzt_fehler in block, (
        f"{INSTALLER[bahn].name} setzt den Fehlerstand am roten Gate nicht "
        "mehr — die Erklaerung hat den Befund verschluckt (BL-261).")

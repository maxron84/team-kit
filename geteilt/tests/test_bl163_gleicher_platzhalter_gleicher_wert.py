#!/usr/bin/env python3
"""BL-163: Dieselbe Marke, zwei Werte — der Fall, den BL-117 vorhergesagt hat.

WAS GEMESSEN WURDE
    Der erste Gleichstands-Vergleich der beiden Installer auf einer echten
    Windows-Maschine (2026-08-25, aus `BL-146`) fand genau einen inhaltlichen
    Unterschied:

        install.sh   TEAM_KIT_PFAD = C:/Users/.../team-kit
        install.ps1  TEAM_KIT_PFAD = C:\\Users\\...\\team-kit

    Beide Installer schreiben BEIDE Konfigurationen. In einer mit `install.ps1`
    erzeugten Ablage stand die Rueckstrich-Form also auch in `team.config.sh`.

WARUM DAS TROTZDEM KEIN DEFEKT WAR — UND WARUM ES TROTZDEM WEG MUSS
    Nachgemessen sind BEIDE Formen funktionsfaehig: in bash (auch nach dem
    Sourcen der Konfiguration), in Python und in PowerShell. Der Pfad wurde
    also nie falsch aufgeloest.

    Die Wirkung lag woanders: `kit-test.sh` Stufe 11 prueft "beide Installer
    erzeugen denselben Baum", und diese Pruefung war damit auf Windows
    DAUERHAFT rot. Eine Pruefung, die immer rot steht, wird nicht gelesen
    (`BL-14`) — und sie ist die einzige, die einen ECHTEN Auseinanderlauf der
    beiden Installer faende. Der harmlose Unterschied haette den schaedlichen
    verdeckt.

DER ZUSAMMENHANG MIT BL-117
    `BL-117` haelt fest, dass der Prompt-Gleichstand am QUELLTEXT bewiesen ist
    und nicht am LAUF, und benennt die Luecke woertlich: "Setzen die beiden
    Bahnen in denselben Platzhalter VERSCHIEDENE WERTE ein ... sind die Prompts
    verschieden und der Test bleibt gruen."

    Das hier ist der erste GEMESSENE Fall dieser Gattung. Er traf nicht einen
    Rollen-Prompt, sondern `team.config.*` — dieselbe Mechanik, anderer
    Adressat. Solange `BL-117` offen ist, ist diese Datei der einzige Ort, an
    dem die Gattung ueberhaupt bewacht wird.

DIE ARBEITSTEILUNG DIESER DATEI
    Den LAUF fuehrt `kit-test.sh` Stufe 11 (zwei echte Installationen, ein
    `diff -r`). Hier steht die Zusicherung am QUELLTEXT — sie laeuft auf jedem
    Wirt und faellt auch dort, wo kein pwsh liegt.
"""
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Die Marke wird ZUSAMMENGESETZT und nicht hingeschrieben. Grund: Schritt 3 von
# `kit-test.sh` durchsucht die INSTALLIERTE Ablage nach ungefuellten
# Platzhaltern (`{{...}}` mit Grossbuchstaben darin) und meldet jede Datei, in
# der einer steht — auch eine Testdatei, die ihn nur ZITIERT. Dieselbe Loesung
# steht aus demselben Grund in test_bl153_rueckkanal_meldung.py.
MARKE = "".join(("{{", "KIT_PFAD", "}}"))


def _installer(name):
    pfad = REPO_ROOT / ("bash" if name.endswith(".sh") else "pwsh") / name
    if not pfad.is_file():
        pytest.skip(f"{name} liegt hier nicht (installiertes Projekt statt Kit-Ablage)")
    return pfad.read_text(encoding="utf-8-sig")


def test_die_pwsh_bahn_normalisiert_den_kit_pfad():
    """Der Fix selbst: Schraegstriche, nicht Rueckstriche.

    Genommen wird die Schraegstrich-Form, weil sie in allen drei Sprachen
    (bash, Python, PowerShell) ohne Maskierung durch jeden Kontext geht — ein
    Rueckstrich tut das in bash ausdruecklich nicht.
    """
    quelle = _installer("install.ps1")
    assert f"'{MARKE}'" in quelle, "Der Platzhalter wird gar nicht mehr gefuellt."
    stelle = quelle.index(f"'{MARKE}'")
    zeile = quelle[stelle:quelle.index("\n", stelle)]
    assert ".Replace(" in zeile, (
        "install.ps1 setzt den Kit-Pfad wieder unveraendert ein. Unter Windows "
        "ist das die Rueckstrich-Form, und die bash-Fassung schreibt "
        "Schraegstriche — Stufe 11 des Selbsttests steht dann dauerhaft rot "
        "(BL-163).")
    assert "'/'" in zeile or '"/"' in zeile, (
        "Die Umschreibung zielt nicht auf Schraegstriche.")


def test_die_bash_bahn_setzt_ihren_wert_unveraendert_ein():
    """Die Gegenseite — sie soll NICHT auch noch umschreiben.

    Unter Git-Bash liefert die MSYS-Schicht bereits die Schraegstrich-Form
    (`C:/Users/...`), auf Linux ohnehin. Eine zweite Umschreibung waere eine
    Stelle mehr, die auseinanderlaufen kann.
    """
    quelle = _installer("install.sh")
    treffer = re.findall(r'\("\{\{KIT_PFAD\}\}", ([a-z_]+)\)', quelle)
    assert treffer, "Der Platzhalter wird in install.sh nicht mehr gefuellt."
    assert set(treffer) == {"kit_pfad"}, (
        f"Unerwartete Quelle fuer den Kit-Pfad: {set(treffer)}")


def test_beide_fuell_routinen_der_bash_bahn_sind_gemeint():
    """`install.sh` hat ZWEI Fuell-Routinen — Erstinstallation und Update.

    `BL-119` hat teuer belegt, was passiert, wenn eine davon einen Platzhalter
    nicht kennt: Er bleibt woertlich in der ausgelieferten Konfiguration
    stehen. Beide muessen den Kit-Pfad fuellen.
    """
    quelle = _installer("install.sh")
    assert quelle.count(f'("{MARKE}", kit_pfad)') == 2, (
        "Nicht beide Fuell-Routinen von install.sh setzen den Kit-Pfad ein. "
        "Die andere liefert dann eine Konfiguration mit stehen gebliebener "
        "Marke aus — der Zustand aus BL-119.")


def test_der_wert_traegt_keine_rueckstriche_mehr():
    """Die Zusicherung, wie ein Leser sie formulieren wuerde.

    Geprueft wird die Absicht, nicht die Schreibweise des Fixes: Nirgends im
    Fuell-Block von install.ps1 darf der Kit-Pfad roh landen.
    """
    quelle = _installer("install.ps1")
    stelle = quelle.index(f"'{MARKE}'")
    zeile = quelle[stelle:quelle.index("\n", stelle)]
    assert not re.search(r"=\s*\$KIT\s*$", zeile), (
        "Der Kit-Pfad wird wieder roh eingesetzt (BL-163).")


def test_keine_testdatei_schreibt_eine_marke_aus():
    """Der Riegel für die **Gattung**, nicht für diese Stelle (`BL-154`).

    Schritt 3 von `kit-test.sh` durchsucht die **installierte** Ablage nach
    ungefüllten Platzhaltern und meldet jede Datei, in der einer steht — auch
    eine Testdatei, die ihn nur **zitiert**. Die Tests werden mitinstalliert
    (`team/tests/`), also gilt das für sie.

    Der Kopf dieser Datei nennt die Lösung seit `BL-163`: Marke
    **zusammensetzen**. Sie stand dort als Kommentar, und ein Kommentar hält
    niemanden auf — am 2026-08-26 ist die Falle **zweimal** zugeschnappt, in
    `test_bl131` (dort schon vorher) und in `test_bl165`. Beide Male wäre der
    Selbsttest an Schritt 3 gestorben, nicht an der Sache.

    `__pycache__` ist ausgenommen — aus demselben Grund wie in `kit-test.sh`:
    Der Compiler faltet benachbarte Literale zusammen, so dass die zerlegte
    Schreibweise im `.pyc` wieder als Fund erscheint.
    """
    tests = Path(__file__).resolve().parent
    muster = re.compile(r"\{\{[A-Z_]+\}\}")
    funde = []
    for datei in sorted(tests.glob("test_*.py")):
        text = datei.read_text(encoding="utf-8")
        for treffer in muster.finditer(text):
            nummer = text.count("\n", 0, treffer.start()) + 1
            funde.append(f"{datei.name}:{nummer} — {treffer.group(0)}")
    assert not funde, (
        "Diese Stellen schreiben eine Platzhalter-Marke aus. Schritt 3 von "
        "kit-test.sh meldet die Datei dann als 'ungefuellter Platzhalter', "
        "und der Selbsttest stirbt an der Testdatei statt an der Sache. "
        "Zusammensetzen: MARKE = ''.join(('{{', 'NAME', '}}')).\n  "
        + "\n  ".join(funde))


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

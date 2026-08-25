#!/usr/bin/env python3
"""BL-156: Beide Installer beantworten die Frage "welche Optionen gibt es?"
selbst — und die Antwort IST der Dateikopf, keine zweite Fassung daneben.

DER ANLASS WAR BEDIENUNG, NICHT SYMMETRIE
    Bis zum 2026-08-23 gab es keinen Weg, die Optionen von `install.sh`
    abzufragen, ohne die Datei zu oeffnen. Beim Schreiben der Liste fiel der
    schwerere Teil auf: `--nur-bash`, `--nur-pwsh` und `--beide-bahnen` waren
    auf BEIDEN Bahnen undokumentiert — in `install.sh` standen sie nur in der
    `Aufruf:`-Zeile, in `install.ps1` nur in `param()`. Wer unter Windows eine
    Bahn abwaehlen oder mit `BL-147` zurueckholen wollte, fand im Skript
    selbst keinen Hinweis darauf, dass das ueberhaupt geht.

WARUM DER KOPF UND NICHT EINE ZWEITE FASSUNG
    Dieselbe Lehre wie `BL-154`: Eine Abschrift laeuft auseinander, und dann
    sagt `--hilfe` etwas anderes als die Datei. Deshalb prueft dieser Test
    nicht, ob die Hilfe die Schalter NENNT (das koennte ein abgeschriebener
    Text auch), sondern ob sie mit dem Kopf DECKUNGSGLEICH ist. Waechst der
    Kopf, waechst die Hilfe mit — oder dieser Test faellt.

WARUM NICHT `Get-Help` AUF DER PWSH-BAHN
    Comment-based help waere der pwsh-uebliche Weg und braechte `-?`
    geschenkt. Auf der Windows-Maschine gemessen (pwsh 7.6.5): `Get-Help`
    findet den `<# … #>`-Block NICHT, wenn die Zeile
    `# Bahn: pwsh | Gegenstueck: install.sh` davorsteht — die Ausgabe
    schrumpft auf die blosse Syntaxzeile. Ohne die Bahn-Zeile funktioniert es.
    Die Bahn-Zeile ist aber nicht verhandelbar (`test_bahn_kopfzeile.py`
    verlangt sie in den ersten drei Zeilen). Also liest die Hilfe die eigene
    Datei, statt den Kopf fuer ein Werkzeug umzubauen. Der Test haelt diese
    Entscheidung fest, damit sie nicht spaeter still zurueckgedreht wird.

DIE ARBEITSTEILUNG DIESER DATEI
    Hier steht der LAUF: Beide Installer werden wirklich gestartet. Das geht
    ohne Zielprojekt und ohne Installation — `--hilfe`/`-Hilfe` gibt aus und
    endet mit 0. Genau deshalb gehoert der Fall hierher und nicht in
    `kit-test.sh`: Er ist billig und deckt trotzdem den ganzen Weg ab.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, verlange_bash, verlange_pwsh

REPO_ROOT = Path(__file__).resolve().parents[2]

# Die drei Schalter, die den Anlass gaben. Sie stehen hier als LISTE und nicht
# als drei Zeilen, weil beide Bahnen dieselbe Zusicherung tragen und ein
# vierter Bahn-Schalter genau eine Stelle zu aendern haette.
BAHN_SCHALTER = {
    "bash": ("--nur-bash", "--nur-pwsh", "--beide-bahnen"),
    "pwsh": ("-NurBash", "-NurPwsh", "-BeideBahnen"),
}

# Die Bahnen werden aus der Tabelle darueber abgeleitet, nicht ein zweites Mal
# hingeschrieben. Zwei Gruende, und der zweite ist der wichtigere:
#   1. Eine dritte Bahn waere dann genau EINE Aenderung.
#   2. Ein Listenliteral, das mit dem Namen der bash-Bahn als Zeichenkette
#      beginnt, verbietet der BL-130-Waechter in jeder Testdatei: An dieser
#      Stelle steht sonst ueberall ein argv, und unter Windows ist ein
#      blankes `bash` der WSL-Launcher aus System32. `conftest.py` ist
#      ausdruecklich die EINE Stelle, die die Bahnen ausschreiben darf; eine
#      Testdatei holt sie sich. (Das Muster steht hier bewusst NICHT als
#      Beispiel — der Waechter liest den Rohtext und faengt sonst diesen
#      Kommentar. Genau so ist die BL-140-Notationstabelle durch die eigene
#      Pruefung gefallen.)
BAHNEN = tuple(BAHN_SCHALTER)


def _installer(bahn):
    pfad = (REPO_ROOT / "bash" / "install.sh" if bahn == "bash"
            else REPO_ROOT / "pwsh" / "install.ps1")
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt hier nicht "
                    "(installiertes Projekt statt Kit-Ablage)")
    return pfad


def _kopf(bahn):
    """Der Dateikopf als Text — die Quelle, gegen die die Hilfe stehen muss.

    Beide Bahnen lassen dieselben zwei Sorten Zeile weg: die Maschinensache
    ganz oben (Shebang, `# Bahn:`) und die Rahmenzeichen des Kommentars. Was
    uebrig bleibt, ist der Text, den ein Mensch liest.
    """
    text = _installer(bahn).read_text(encoding="utf-8-sig")
    zeilen = text.splitlines()
    raus = []
    if bahn == "bash":
        for zeile in zeilen[2:]:            # 1 Shebang, 2 Bahn-Kopfzeile
            if not zeile.startswith("#"):
                break
            raus.append(re.sub(r"^# ?", "", zeile))
    else:
        drin = False
        for zeile in zeilen[1:]:            # 1 Bahn-Kopfzeile
            if not drin:
                if zeile.strip() == "<#":
                    drin = True
                continue
            if zeile.strip() == "#>":
                break
            raus.append(re.sub(r"^  ", "", zeile))
    return "\n".join(raus).rstrip()


def _hilfe(bahn, schalter):
    """Faehrt den Installer mit dem Hilfe-Schalter und liefert seine Ausgabe."""
    pfad = _installer(bahn)
    if bahn == "bash":
        verlange_bash()
        aufruf = [BASH, str(pfad), schalter]
    else:
        verlange_pwsh()
        aufruf = ["pwsh", "-NoProfile", "-File", str(pfad), schalter]
    lauf = subprocess.run(aufruf, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    assert lauf.returncode == 0, (
        f"{pfad.name} {schalter} endete mit {lauf.returncode} statt 0 — ein "
        f"Hilfe-Schalter darf nichts tun und nichts melden:\n{lauf.stderr}")
    assert not lauf.stderr.strip(), (
        f"{pfad.name} {schalter} schreibt nach stderr:\n{lauf.stderr}")
    return lauf.stdout


@pytest.mark.parametrize("bahn,schalter", [
    ("bash", "-h"), ("bash", "--hilfe"), ("bash", "--help"),
    ("pwsh", "-h"), ("pwsh", "-Help"), ("pwsh", "-Hilfe"),
])
def test_alle_drei_schreibweisen_geben_dieselbe_hilfe(bahn, schalter):
    """Ein Wechsel der Bahn soll kein Wechsel der Gewohnheit sein.

    Die bash-Fassung kennt `-h`/`--hilfe`/`--help`; die pwsh-Fassung bildet
    das ueber Aliasse nach. Wer `-h` tippt, weil er es von drueben kennt,
    bekommt die Hilfe und keine Fehlermeldung.
    """
    ausgabe = _hilfe(bahn, schalter)
    assert ausgabe.strip(), f"{schalter} gab nichts aus"
    assert "Aufruf:" in ausgabe, (
        f"{schalter} gibt etwas aus, aber nicht den Kopf:\n{ausgabe}")


@pytest.mark.parametrize("bahn,schalter", [("bash", "--hilfe"), ("pwsh", "-Hilfe")])
def test_die_hilfe_ist_der_kopf(bahn, schalter):
    """Die tragende Zusicherung: keine zweite Fassung neben dem Kopf.

    Faellt dieser Fall, ist die Hilfe zu einer Abschrift geworden — und ab da
    ist es eine Frage der Zeit, bis sie etwas anderes sagt als die Datei
    (`BL-154`).
    """
    assert _hilfe(bahn, schalter).rstrip() == _kopf(bahn), (
        "Die Hilfe ist nicht mehr deckungsgleich mit dem Dateikopf. Entweder "
        "wurde der Kopf umgebaut, ohne die Ausgabe nachzuziehen, oder es ist "
        "ein zweiter Hilfetext entstanden — beides ist der Anfang der Drift, "
        "die BL-154 abgeschafft hat.")


@pytest.mark.parametrize("bahn", BAHNEN)
def test_der_kopf_erklaert_die_bahn_schalter(bahn):
    """Der schwerere Teil von BL-156: Die drei Bahn-Schalter waren auf BEIDEN
    Bahnen undokumentiert — in `install.sh` standen sie nur in der
    `Aufruf:`-Zeile, in `install.ps1` nur in `param()`.

    Geprueft wird nicht die blosse Erwaehnung, sondern die ERKLAERUNG: Der
    Schalter muss am Zeilenanfang stehen und Text hinter sich haben. Eine
    Nennung in der `Aufruf:`-Zeile war genau der Zustand, den dieser Eintrag
    als unzureichend befunden hat.
    """
    kopf = _kopf(bahn)
    for schalter in BAHN_SCHALTER[bahn]:
        muster = re.compile(r"^\s*" + re.escape(schalter) + r"\s+\S", re.M)
        assert muster.search(kopf), (
            f"{schalter} wird im Kopf von install.{'sh' if bahn == 'bash' else 'ps1'} "
            "nicht erklaert. Eine Erwaehnung in der Aufruf-Zeile reicht "
            "nicht — wer eine Bahn abwaehlen oder mit BL-147 zurueckholen "
            "will, findet dann im Skript keinen Hinweis darauf, dass das geht.")


@pytest.mark.parametrize("bahn", BAHNEN)
def test_ohne_zielpfad_verweist_der_fehler_auf_die_hilfe(bahn):
    """Der Moment, in dem jemand die Optionen braucht, ist der Fehlerfall.

    Beide Bahnen brechen ohne Zielpfad mit 2 ab — und beide muessen dort
    sagen, wie man die vollstaendige Liste bekommt. Sonst ist der Schalter
    zwar da, aber niemand erfaehrt davon.
    """
    pfad = _installer(bahn)
    if bahn == "bash":
        verlange_bash()
        aufruf = [BASH, str(pfad)]
        erwartet = "--hilfe"
    else:
        verlange_pwsh()
        aufruf = ["pwsh", "-NoProfile", "-File", str(pfad)]
        erwartet = "-Hilfe"
    lauf = subprocess.run(aufruf, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    assert lauf.returncode == 2, (
        f"ohne Zielpfad erwartet Exit 2, ist {lauf.returncode}")
    alles = lauf.stdout + lauf.stderr
    assert erwartet in alles, (
        f"Die Fehlermeldung nennt {erwartet} nicht:\n{alles}")


def test_pwsh_liest_den_eigenen_kopf_statt_get_help():
    """Die gemessene Entscheidung festhalten (siehe Modulkopf).

    Ein spaeterer Umbau auf comment-based help wuerde `-Hilfe` still leer
    laufen lassen, solange die `# Bahn:`-Zeile davorsteht — der Fall oben
    faenge das zwar, aber ohne diesen hier waere nicht zu sehen, WARUM der
    Weg so gewaehlt wurde.
    """
    quelle = _installer("pwsh").read_text(encoding="utf-8-sig")
    assert "$PSCommandPath" in quelle and "ReadAllLines" in quelle, (
        "install.ps1 liest seinen Kopf nicht mehr aus der eigenen Datei")
    assert ".SYNOPSIS" not in quelle, (
        "install.ps1 ist auf comment-based help umgebaut worden. Gemessen "
        "(pwsh 7.6.5): Get-Help findet den Block nicht, solange die "
        "'# Bahn:'-Kopfzeile davorsteht — und die verlangt "
        "test_bahn_kopfzeile.py in den ersten drei Zeilen.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

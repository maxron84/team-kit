#!/usr/bin/env python3
"""BL-129: Das Ledger bekam unter Windows in JEDER Zeile ein CR-Byte.

`_ledger_zeile_ersetzen()` schrieb die Datei mit

    with os.fdopen(fd, "w") as fh:

also im Textmodus mit `newline=None`. Der uebersetzt beim Schreiben jedes
`"\\n"` in `os.linesep` — unter Windows in `"\\r\\n"`. Betroffen war nicht die
neue Zeile allein, sondern der GESAMTE Inhalt: Die Funktion schreibt die Datei
vollstaendig neu, also bekamen Kopfzeile und alle Bestandszeilen bei jedem
`akteur-abschluss` ein CR-Byte dazu.

WARUM DAS MEHR IST ALS EINE KOSMETIKFRAGE
    Genau dieses Byte ist der Schaden, gegen den HM-36, HM-37 und HM-38 die
    Feldwerte sanitisieren: Ein rohes CR wird beim naechsten Einlesen unter
    universal newlines als Zeilenumbruch gelesen und zerlegt die Zeile. Drei
    Funde, drei Tests, eine Sanitisierungsfunktion — und die Plattform hat das
    Byte hinterher wieder eingesetzt.

    Die Sanitisierung konnte den Fall nicht fangen. Sie greift auf die
    FELDWERTE, eine Schicht ueber dem Schreibvorgang. Das CR aus BL-129 kommt
    nicht aus einem Feldwert, sondern aus der Kodierungsschicht darunter. Eine
    Absicherung, die eine Schicht zu frueh sitzt, sieht aus wie eine
    Absicherung und ist keine — dieselbe Bauart wie BL-15/BL-17.

DIE ZWEITE HAELFTE: DIE KODIERUNG
    Dieselben Aufrufe nannten keine Kodierung, galten also in der Locale des
    Wirts. Auf einem deutschen Windows ist das cp1252. Ein Umlaut in einer
    Notiz — `--notiz "Kaskade 3 geprüft"` — wird dann als cp1252 geschrieben
    und beim naechsten Lesen als cp1252 gelesen, solange die Maschine gleich
    bleibt. Wandert die Datei (Repo, Backup, zweiter Rechner), ist sie
    Mojibake, und `kosten.py ledger` auf einem UTF-8-Wirt bricht mit
    UnicodeDecodeError ab. Das ist die Bauart von BL-125, nur an der
    Ledger-Datei statt am Modulimport.

WARUM HIER EINE QUELLTEXT-ZUSICHERUNG STEHT
    Der Fehler ist plattformabhaengig: Unter Linux ist `os.linesep` bereits
    `"\\n"`, und die Locale ist praktisch immer UTF-8. Ein rein verhaltens-
    basierter Test waere auf der Maschine, auf der er meistens laeuft, auch
    OHNE den Fix gruen — er wuerde den Rueckfall also genau dort nicht
    melden, wo er gebaut wird. Deshalb steht neben den Verhaltenstests eine
    Zusicherung am Quelltext. Dieselbe Ueberlegung wie bei BL-126, wo die
    pwsh-Fassung auf einer Maschine ohne PowerShell festgenagelt wird.
"""
import re
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

KOSTEN_PY = kit_pfad("tools", "kosten.py")
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _ledger(tmp_path, inhalt=KOPF, zeilenende="\n"):
    """Legt ein Fixture-Ledger BYTEGENAU an.

    Bewusst `write_bytes` und nicht `write_text`: Letzteres uebersetzt unter
    Windows selbst nach CRLF (`newline=None`) und schriebe in der Locale des
    Wirts. Der Test wuerde dann seinen eigenen Ausgangszustand verfaelschen und
    haette am Ende nichts ueber `kosten.py` gesagt.
    """
    pfad = tmp_path / "fixture-ledger"
    pfad.write_bytes(inhalt.replace("\n", zeilenende).encode("utf-8"))
    return pfad


def _abschluss(ledger, *extra):
    return subprocess.run(
        [sys.executable, str(KOSTEN_PY), "akteur-abschluss",
         "--rolle", "frank", "--kaskade", "16", "--auth", "abo",
         "--domaene", "produkt", "--usd", "1.0", "--pfad", str(ledger),
         *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace")


# --- Das Verhalten: auf Windows der eigentliche Nachweis --------------------

def test_geschriebenes_ledger_traegt_kein_cr(tmp_path):
    """Der Fund selbst. Unter Linux gruen, weil os.linesep dort "\\n" ist —
    auf der Zielplattform war er es nicht."""
    ledger = _ledger(tmp_path)
    ergebnis = _abschluss(ledger)
    assert ergebnis.returncode == 0, ergebnis.stderr

    rohbytes = ledger.read_bytes()
    assert b"\r" not in rohbytes, (
        "Das Ledger traegt CR-Bytes. Sie kommen nicht aus einem Feldwert (das "
        "faengt die Sanitisierung aus HM-36/37/38 ab), sondern aus dem "
        "Textmodus des Schreibvorgangs — os.fdopen(fd, 'w') ohne newline=''.\n"
        f"Ist: {rohbytes!r}")


def test_bestehendes_crlf_ledger_wird_beim_schreiben_geheilt(tmp_path):
    """Eine Datei, die vor dem Fix entstanden ist, muss sich beim naechsten
    Schreibzugriff normalisieren — sonst traegt das Projekt den Schaden
    weiter, bis jemand die Datei von Hand anfasst."""
    ledger = _ledger(tmp_path, zeilenende="\r\n")
    ergebnis = _abschluss(ledger)
    assert ergebnis.returncode == 0, ergebnis.stderr

    rohbytes = ledger.read_bytes()
    assert b"\r" not in rohbytes, \
        f"Das Alt-CR hat den Schreibzugriff ueberlebt: {rohbytes!r}"
    assert rohbytes.startswith(b"# datum |"), \
        "die Kopfzeile muss die Heilung ueberleben"


def test_umlaut_in_der_notiz_bleibt_utf8(tmp_path):
    """Ohne `encoding=` gilt die Locale des Wirts — auf einem deutschen
    Windows cp1252. Die Datei ist dann nur auf DIESER Maschine lesbar."""
    ledger = _ledger(tmp_path)
    ergebnis = _abschluss(ledger, "--notiz", "Kaskade 16 geprüft (Größe)")
    assert ergebnis.returncode == 0, ergebnis.stderr

    rohbytes = ledger.read_bytes()
    assert "geprüft (Größe)".encode("utf-8") in rohbytes, (
        "Die Notiz steht nicht als UTF-8 in der Datei — dann wurde sie in der "
        f"Locale des Wirts geschrieben.\nIst: {rohbytes!r}")
    # Die Gegenprobe zum LESEN, und zwar ueber `--addieren`: Der Zweig liest
    # den Altwert aus der Zeile und rechnet ihn hinzu, muss die Datei also
    # wirklich verstehen. Ohne encoding= faellt genau das um, sobald die
    # Zeile einmal in einer anderen Kodierung geschrieben wurde.
    zweiter = _abschluss(ledger, "--notiz", "zweiter Lauf", "--addieren")
    assert zweiter.returncode == 0, zweiter.stderr
    assert "2.0000" in ledger.read_text(encoding="utf-8"), \
        "der Altwert wurde beim Addieren nicht korrekt gelesen"


# --- Die Quelltext-Zusicherung: greift auf JEDER Plattform ------------------

def test_der_ledger_schreibvorgang_nennt_newline_und_kodierung():
    quelle = KOSTEN_PY.read_text(encoding="utf-8")
    treffer = re.search(r"os\.fdopen\(fd,\s*\"w\"[^)]*\)", quelle)
    assert treffer, \
        "der Ledger-Schreibvorgang (os.fdopen) ist nicht mehr auffindbar"
    aufruf = treffer.group(0)
    assert 'newline=""' in aufruf, (
        "os.fdopen ohne newline='' uebersetzt \\n nach os.linesep — unter "
        f"Windows also nach \\r\\n.\nIst: {aufruf}")
    assert "encoding=" in aufruf, (
        "os.fdopen ohne encoding= schreibt in der Locale des Wirts.\n"
        f"Ist: {aufruf}")


def test_keine_lesestelle_ohne_kodierung():
    """Die Gegenseite: Was in UTF-8 geschrieben wird, muss auch als UTF-8
    gelesen werden. Ein einziges `open(pfad)` ohne Kodierung reicht, um die
    Datei auf einem cp1252-Wirt unlesbar zu machen."""
    ohne = []
    for nummer, zeile in enumerate(
            KOSTEN_PY.read_text(encoding="utf-8").splitlines(), 1):
        for aufruf in re.findall(r"(?<!os\.)\bopen\([^)]*\)", zeile):
            if aufruf.startswith("open(lock_pfad") or "encoding=" in aufruf:
                continue
            ohne.append(f"{nummer}: {aufruf}")
    assert not ohne, (
        "Diese open()-Aufrufe in kosten.py nennen keine Kodierung und gelten "
        "damit in der Locale des Wirts (BL-129):\n  " + "\n  ".join(ohne))

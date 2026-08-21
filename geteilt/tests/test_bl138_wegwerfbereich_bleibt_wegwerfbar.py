#!/usr/bin/env python3
r"""BL-138: Ein gruener Lauf, der als roter endet — am Aufraeumen.

⚠️ Feldbefund, dieselbe Windows-Maschine wie BL-113 und BL-122…BL-137.
Aufgefallen beim ersten Testlauf des Anwenders im Feldprojekt. Das
Fortschrittsband war makellos:

    542 Zeichen, davon 228 Punkte und 314 s — kein F, kein E, kein x

Und unmittelbar hinter `[100%]` begann eine Wand aus Traceback, die in

    PermissionError: [WinError 5] Access is denied:
        …\pytest-of-…\garbage-8ed10858-…\repo\.git\objects\48\54f1a4…

endete und schliesslich in einem `KeyboardInterrupt` — der Anwender hat
abgebrochen. Er hat damit einen bestandenen Lauf als gescheitert gesehen.

DIE KETTE, NACHGEMESSEN STATT VERMUTET
    1. Die Kit-Tests legen echte Git-Repos in `tmp_path` an. Sie muessen es:
       Ein Guard, der gegen einen erfundenen Git-Zustand prueft, prueft
       nichts (dieselbe Ueberlegung wie in BL-51).
    2. Git schreibt lose Objekte schreibgeschuetzt. Gezaehlt in einem
       liegengebliebenen Ordner: 989 von 5622 Dateien, und AUSNAHMSLOS
       unter `.git/objects`. Objekte sind unveraenderlich; das ist Absicht.
    3. pytest hebt die letzten drei Laufordner auf und loescht am
       Sitzungsende die aelteren.
    4. Dort trennen sich die Plattformen:

           POSIX    unlink() prueft das Schreibrecht am VERZEICHNIS; der
                    Modus der Datei ist gleichgueltig. Es geht.
           Windows  DeleteFile scheitert mit ERROR_ACCESS_DENIED (5),
                    sobald FILE_ATTRIBUTE_READONLY gesetzt ist.

    5. pytest faengt den Fehler ab und versucht es erneut — chmod plus
       Retry, EINZELN pro Datei. Bei 989 Objekten auf NTFS dauert das
       minutenlang, und zwar schweigend.

WARUM DAS EIN KIT-FEHLER IST UND KEIN pytest-FEHLER
    pytest raeumt auf, was ihm uebergeben wird. Uebergeben hat es das Kit —
    mit einem Schreibschutz, den das Kit selbst verursacht hat, indem es Git
    in den Wegwerfbereich laufen liess. Wer einen Bereich als wegwerfbar
    deklariert, schuldet ihm auch, dass er wegwerfbar bleibt.

    Es ist derselbe Zuschnitt wie BL-130: eine Annahme des PRUEFSTANDS ueber
    die Plattform, nicht ueber den Prueflung. Unter Linux ist sie richtig,
    unter Windows nicht, und die Diagnose kostet jedes Mal von vorn.

WARUM DER SCHADEN MIT DER ZEIT WAECHST
    Der Fehler tritt NICHT beim Lauf auf, der ihn verursacht. Er tritt drei
    Laeufe spaeter auf, wenn pytest den alten Ordner wegraeumen will —
    also zu einem Zeitpunkt, an dem niemand mehr an den Lauf denkt, der ihn
    hinterlassen hat. Zwischen Ursache und Wirkung liegen Stunden und zwei
    andere Testlaeufe. Genau deshalb sah es nach einem Fehler DIESES Laufs
    aus (BL-136 hatte dieselbe Verzoegerungsbauart, dort ueber den Klon).

WARUM HIER `_basetemp` UND NICHT `getbasetemp()` STEHT
    `getbasetemp()` legt den Ordner an, wenn es ihn nicht gibt. Ein Lauf, in
    dem kein Test `tmp_path` gebraucht hat, hinterliesse dann einen leeren
    Ordner — das Aufraeumen wuerde selbst Muell erzeugen. `_basetemp` ist
    `None`, solange nichts entstanden ist.

WARUM `tryfirst` NICHT VERHANDELBAR IST
    `_pytest.tmpdir` raeumt im SELBEN Hook auf. Ohne `tryfirst` ist die
    Reihenfolge dem Zufall ueberlassen, und in der falschen Haelfte der
    Faelle loest das Kit den Schreibschutz, nachdem pytest schon gescheitert
    ist. Ein Fix, der zur Haelfte greift, ist im Fehlerbild nicht von einem
    kaputten zu unterscheiden — deshalb steht dazu unten eine
    Quelltext-Zusicherung: Auf einem POSIX-Wirt ist die Reihenfolge nicht
    beobachtbar, die Anforderung gilt trotzdem.
"""
import ast
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import IST_WINDOWS, REPO_ROOT, schreibschutz_loesen


def _lege_schreibgeschuetztes_objekt_an(wurzel):
    """Baut nach, was Git in `.git/objects` hinterlaesst."""
    ordner = wurzel / ".git" / "objects" / "48"
    ordner.mkdir(parents=True)
    datei = ordner / "54f1a449ccfeb02f9a72ed7302b0696084967a"
    datei.write_bytes(b"x\x9c\x4b\xca\xc9\x4f\x52\x30\x34\x65\x00\x00")
    os.chmod(datei, stat.S_IRUSR)
    return datei


# ------------------------------------------------------------- Verhalten
def test_der_wegwerfbereich_laesst_sich_hinterher_wegwerfen(tmp_path):
    """Die Zusicherung, um die es geht — auf beiden Plattformen dieselbe.

    Unter POSIX ist sie auch ohne den Fix erfuellt; unter Windows nur mit.
    Genau deshalb steht sie so und nicht als Modus-Vergleich: Der Satz
    "danach ist der Bereich loeschbar" ist auf jedem Wirt wahr oder falsch,
    und er ist das, worauf pytest sich verlaesst.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _lege_schreibgeschuetztes_objekt_an(repo)
    schreibschutz_loesen(tmp_path)
    shutil.rmtree(repo)
    assert not repo.exists()


def test_ohne_den_fix_scheitert_genau_diese_loeschung(tmp_path):
    """Der Gegenbeweis: Ohne das Loesen ist es unter Windows nicht loeschbar.

    Ohne diesen Test bliebe offen, ob die Zusicherung oben ueberhaupt etwas
    absichert oder nur beschreibt, was ohnehin gilt.
    """
    if not IST_WINDOWS:
        pytest.skip("unter POSIX prueft unlink() das Verzeichnis, nicht die "
                    "Datei — der Fall entsteht dort gar nicht")
    repo = tmp_path / "repo"
    repo.mkdir()
    _lege_schreibgeschuetztes_objekt_an(repo)
    with pytest.raises(PermissionError):
        shutil.rmtree(repo)


def test_das_loesen_meldet_wie_viele_dateien_es_betraf(tmp_path):
    if not IST_WINDOWS:
        pytest.skip("das Loesen ist unter POSIX ein bewusster Leerlauf")
    for nr in range(3):
        ordner = tmp_path / ".git" / "objects" / f"{nr:02d}"
        ordner.mkdir(parents=True)
        datei = ordner / "abcdef"
        datei.write_bytes(b"x")
        os.chmod(datei, stat.S_IRUSR)
    assert schreibschutz_loesen(tmp_path) == 3
    # Idempotent: Ein zweiter Lauf findet nichts mehr zu tun.
    assert schreibschutz_loesen(tmp_path) == 0


def test_das_loesen_stolpert_nicht_ueber_einen_leeren_bereich(tmp_path):
    """Nach dem letzten Test — da darf nichts mehr scheitern duerfen."""
    assert schreibschutz_loesen(tmp_path) == 0
    assert schreibschutz_loesen(tmp_path / "gibtsnicht") == 0


def test_eine_sitzung_ohne_tmp_path_hinterlaesst_keinen_ordner(tmp_path):
    """Der Hook darf den Wegwerfbereich nicht selbst ins Leben rufen.

    Gefahren wird eine ECHTE pytest-Sitzung als Unterprozess: Die Frage ist
    eine ueber pytests Innenleben (`_basetemp` bleibt `None`), und die
    beantwortet nur pytest selbst glaubwuerdig.
    """
    (tmp_path / "test_leer.py").write_bytes(
        b"def test_nichts():\n    assert True\n")
    basis = tmp_path / "tmpbereich"
    ergebnis = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q",
         str(tmp_path / "test_leer.py"), f"--basetemp={basis}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(tmp_path),
    )
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    assert not basis.exists(), (
        "pytest hat einen Wegwerfbereich angelegt, obwohl kein Test ihn "
        "gebraucht hat — dann ruft der Hook getbasetemp() statt _basetemp."
    )


# ------------------------------------------------------------- Quelltext
def _conftest_quelle():
    pfad = REPO_ROOT / "geteilt" / "tests" / "conftest.py"
    if not pfad.is_file():
        pfad = REPO_ROOT / "team" / "tests" / "conftest.py"
    if not pfad.is_file():
        pytest.skip("conftest.py in dieser Ablage nicht gefunden")
    return pfad.read_text(encoding="utf-8")


def test_der_hook_laeuft_vor_dem_aufraeumen_von_pytest():
    """`tryfirst` ist die halbe Wirkung — auf POSIX nicht beobachtbar."""
    text = _conftest_quelle()
    treffer = re.search(
        r"@pytest\.hookimpl\(([^)]*)\)\s*\ndef pytest_sessionfinish", text)
    assert treffer, (
        "pytest_sessionfinish in conftest.py traegt keinen hookimpl-Dekorator "
        "mehr. Ohne tryfirst raeumt _pytest.tmpdir moeglicherweise zuerst auf "
        "— und scheitert an genau dem Schreibschutz, den dieser Hook loesen "
        "soll."
    )
    assert "tryfirst=True" in treffer.group(1), treffer.group(0)


def _hook_rumpf_ohne_docstring():
    """Die Anweisungen von `pytest_sessionfinish` — ohne seine Begruendung.

    Der erste Entwurf verglich den Text ab `def pytest_sessionfinish`. Der
    schlug fehl, weil im Docstring steht, warum `getbasetemp()` hier NICHT
    benutzt wird: Der Waechter hielt seine eigene Erklaerung fuer den
    Verstoss. Ueber Zeilennummern aus dem Syntaxbaum ist die Trennung
    eindeutig.

    Bewusst ohne `ast.unparse` — das gibt es erst ab Python 3.9, und das Kit
    verlangt 3.8 (dieselbe Schranke wie bei `newline=""` in BL-137).
    """
    text = _conftest_quelle()
    baum = ast.parse(text)
    fn = next((k for k in ast.walk(baum)
               if isinstance(k, ast.FunctionDef)
               and k.name == "pytest_sessionfinish"), None)
    assert fn is not None, "pytest_sessionfinish fehlt in conftest.py"
    erste = fn.body[0]
    ab = erste.end_lineno if (isinstance(erste, ast.Expr)
                              and isinstance(erste.value, ast.Constant)
                              and isinstance(erste.value.value, str)) else fn.lineno
    return "\n".join(text.splitlines()[ab:fn.end_lineno])


def test_der_hook_greift_nur_auf_den_bereich_dieser_sitzung():
    rumpf = _hook_rumpf_ohne_docstring()
    assert "_basetemp" in rumpf, (
        "Erwartet wird _basetemp. getbasetemp() LEGT den Ordner an — der "
        "Hook wuerde dann in einem Lauf ohne tmp_path selbst Muell erzeugen."
    )
    assert "getbasetemp()" not in rumpf, rumpf
    assert "schreibschutz_loesen" in rumpf

#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer BL-125: `team/tools/kosten.py`
importierte `fcntl` UNGESCHUETZT auf Modulebene. Unter Windows gibt es dieses
Modul nicht — und weil der Import ganz oben steht, fiel nicht die Sperre aus,
sondern die GANZE Datei. Feldbefund von einer Windows-Maschine: `team-test.cmd`
brach mit 21 Sammelfehlern ab ("ModuleNotFoundError: No module named 'fcntl'"),
und derselbe Fehler traf jeden Kostenpfad der pwsh-Bahn
(--akteur-abschluss, --rollen-abschluss, --ralph-abschluss).

Der Fix laedt `fcntl` und `msvcrt` WEICH und entscheidet erst beim Sperren,
welcher Mechanismus greift. Diese Datei prueft beide Haelften:

  1. Ohne `fcntl` muss kosten.py IMPORTIERBAR bleiben (der Windows-Fall,
     hier durch einen Import-Blocker nachgestellt, damit er auf jeder
     Maschine faellt statt nur auf der einen, auf der er auftrat).
  2. Der Windows-Sperrweg muss dieselbe Zusicherung tragen wie `flock`:
     Zwei ueberlappende Schreiber verlieren keine Zeile (die Invariante aus
     test_hm48_ledger_lock_race.py, hier gegen ein msvcrt-Doppel gefahren).
  3. Gibt es GAR KEINEN Sperrmechanismus, wird nichts geschrieben — eine
     stille Schreiboperation ohne Sperre waere die Rueckkehr von HM-48.
  4. Kein Werkzeug unter team/tools/ darf wieder ein plattformgebundenes
     Modul ungeschuetzt auf Modulebene importieren (die Klasse, nicht der
     Fall).

Netz-/CLI-frei gegen ein temporaeres Fixture-Ledger, nie gegen die echte
.budget-ledger — Muster wie test_hm48_ledger_lock_race.py.
"""
import ast
import importlib.util
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools (Muster aus test_hm48).
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        TOOLS = Path(_tools)
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

# Plattformgebundene Standardmodule. Wer eines davon ungeschuetzt auf
# Modulebene importiert, macht sein Werkzeug auf der anderen Bahn
# unbenutzbar — und zwar nicht an der Stelle, an der es gebraucht wird,
# sondern beim Programmstart.
PLATTFORM_MODULE = {
    "fcntl", "grp", "posix", "pwd", "resource", "syslog", "termios", "tty",
    "msvcrt", "winreg", "winsound", "_winapi",
}


class _ImportBlocker:
    """Stellt ein fehlendes Standardmodul nach — genau so, wie Windows es
    zeigt: `ModuleNotFoundError` aus dem Importsystem."""

    def __init__(self, namen):
        self.namen = set(namen)

    def find_spec(self, name, path=None, target=None):
        if name in self.namen:
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return None


def _kosten_frisch_laden(ohne):
    """Laedt kosten.py ein zweites Mal unter eigenem Namen, waehrend die
    genannten Module unauffindbar sind. Ein bereits importiertes Modul liegt
    in sys.modules und wuerde den Blocker umgehen, deshalb wird es fuer die
    Dauer des Ladens ausgehaengt und danach zurueckgestellt."""
    gesichert = {n: sys.modules.pop(n) for n in ohne if n in sys.modules}
    blocker = _ImportBlocker(ohne)
    sys.meta_path.insert(0, blocker)
    try:
        spec = importlib.util.spec_from_file_location(
            "kosten_bl125", TOOLS / "kosten.py")
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    finally:
        sys.meta_path.remove(blocker)
        sys.modules.update(gesichert)
        sys.modules.pop("kosten_bl125", None)


def test_import_gelingt_ohne_fcntl():
    """Der Feldfehler selbst: ohne fcntl war kosten.py nicht ladbar."""
    modul = _kosten_frisch_laden({"fcntl"})
    assert modul.fcntl is None, (
        "Ohne fcntl muss das Modul mit fcntl=None laden, damit die "
        "Sperrwahl zur Laufzeit stattfinden kann.")
    # Stichprobe, dass wirklich das ganze Modul da ist und nicht nur der Kopf:
    assert callable(modul.akteur_abschluss)


def test_import_gelingt_auch_ohne_beide_module():
    """Weder fcntl noch msvcrt: importierbar bleibt es trotzdem. Der Fehler
    gehoert an die Sperre (Test unten), nicht an den Programmstart."""
    modul = _kosten_frisch_laden({"fcntl", "msvcrt"})
    assert modul.fcntl is None and modul.msvcrt is None


class _MsvcrtDoppel:
    """Doppel fuer die Windows-Bytebereichssperre. Bildet die Eigenschaft
    nach, auf die sich der Fix stuetzt: Die Sperre haengt an der DATEI (hier
    ueber Geraet+Inode des Deskriptors), nicht am Thread — ein zweiter
    Deskriptor auf dieselbe Lock-Datei prallt ab, auch im selben Prozess.
    Genau das tut LockFile() unter Windows."""

    LK_NBLCK = 3
    LK_UNLCK = 0

    def __init__(self):
        self.spur = []
        self._gehalten = set()
        self._mutex = threading.Lock()

    def locking(self, fd, mode, nbytes):
        st = os.fstat(fd)
        schluessel = (st.st_dev, st.st_ino)
        with self._mutex:
            if mode == self.LK_UNLCK:
                self._gehalten.discard(schluessel)
                self.spur.append("frei")
                return
            if schluessel in self._gehalten:
                raise OSError(36, "Resource deadlock avoided")
            self._gehalten.add(schluessel)
            self.spur.append("belegt")


def _fixture_ledger(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text("# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    return pfad


def _mkstemp_verlangsamen(monkeypatch):
    """Haelt den kritischen Bereich lange genug offen, dass sich zwei
    Schreiber ueberhaupt begegnen koennen (Muster aus test_hm48)."""
    orig = kosten.tempfile.mkstemp

    def langsam(*args, **kwargs):
        time.sleep(0.2)
        return orig(*args, **kwargs)

    monkeypatch.setattr(kosten.tempfile, "mkstemp", langsam)


def test_windows_sperrweg_verliert_keine_zeile(tmp_path, monkeypatch):
    """Die HM-48-Invariante, gefahren auf dem Windows-Zweig: Ein Fix, der
    die Datei nur wieder importierbar macht, aber die Sperre fallen laesst,
    faellt hier."""
    pfad = _fixture_ledger(tmp_path)
    doppel = _MsvcrtDoppel()
    monkeypatch.setattr(kosten, "fcntl", None)
    monkeypatch.setattr(kosten, "msvcrt", doppel)
    monkeypatch.setattr(kosten, "_LEDGER_LOCK_FRIST_S", 10.0)
    _mkstemp_verlangsamen(monkeypatch)

    fehler = []

    def schreiber(rolle):
        try:
            kosten.akteur_abschluss(
                1.0, "team", "19", rolle, "api", notiz="bl125", pfad=str(pfad))
        except Exception as exc:  # pragma: no cover - nur bei echtem Bug
            fehler.append(exc)

    t1 = threading.Thread(target=schreiber, args=("architekt",))
    t2 = threading.Thread(target=schreiber, args=("frank",))
    t1.start()
    time.sleep(0.05)  # t1 haengt sicher im kritischen Bereich
    t2.start()
    t1.join()
    t2.join()

    assert not fehler, fehler
    rollen = {z["rolle"] for z in kosten.ledger_zeilen(str(pfad))}
    assert rollen == {"architekt", "frank"}
    # Die Sperre wurde benutzt UND wieder freigegeben, abwechselnd — kein
    # zweiter Schreiber war je gleichzeitig drin, keine Sperre blieb liegen.
    assert doppel.spur == ["belegt", "frei", "belegt", "frei"], doppel.spur


def test_ohne_sperrmechanismus_wird_nichts_geschrieben(tmp_path, monkeypatch):
    """Weder fcntl noch msvcrt: Der Ledger bleibt unangetastet, und der
    Fehler nennt den Grund. Ungesichert zu schreiben waere HM-48 zurueck."""
    pfad = _fixture_ledger(tmp_path)
    vorher = pfad.read_text()
    monkeypatch.setattr(kosten, "fcntl", None)
    monkeypatch.setattr(kosten, "msvcrt", None)

    with pytest.raises(OSError) as fehler:
        kosten.akteur_abschluss(
            1.0, "team", "19", "architekt", "api", notiz="bl125",
            pfad=str(pfad))

    assert "Sperrmechanismus" in str(fehler.value)
    assert pfad.read_text() == vorher


def test_kein_werkzeug_importiert_plattformmodule_ungeschuetzt():
    """Die Klasse statt des Falls: Ein `import fcntl` (oder `msvcrt`, `pwd`,
    …) auf Modulebene ist nur dann zulaessig, wenn er in einem try-Block
    steht und damit einen Ausfall verkraftet."""
    verstoesse = []
    for datei in sorted(TOOLS.glob("*.py")):
        baum = ast.parse(datei.read_text(encoding="utf-8"))
        # Nur die DIREKTEN Kinder des Moduls. Alles Tiefere ist damit
        # automatisch erlaubt und zwar aus gutem Grund: Ein Import in einem
        # try-Block, in einem `if os.name == "nt":` oder in einer Funktion
        # kann ausfallen, ohne die Datei mitzureissen — und genau das ist
        # die Eigenschaft, um die es hier geht.
        for knoten in baum.body:
            if not isinstance(knoten, (ast.Import, ast.ImportFrom)):
                continue
            namen = ([a.name.split(".")[0] for a in knoten.names]
                     if isinstance(knoten, ast.Import)
                     else [(knoten.module or "").split(".")[0]])
            for name in namen:
                if name in PLATTFORM_MODULE:
                    verstoesse.append(f"{datei.name}:{knoten.lineno} {name}")
    assert not verstoesse, (
        "Plattformgebundene Module ungeschuetzt auf Modulebene importiert — "
        "das Werkzeug ist damit auf der anderen Bahn nicht einmal "
        f"ladbar (BL-125): {verstoesse}")

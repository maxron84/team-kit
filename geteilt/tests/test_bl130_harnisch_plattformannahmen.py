#!/usr/bin/env python3
"""BL-130: Der Testharnisch war fuer einen POSIX-Wirt geschrieben — und das
stand nirgends.

Der erste Lauf der Suite unter nativem Windows meldete 160 Fehlschlaege. Kein
einziger davon kam aus dem Kit. Vier Annahmen des Harnischs trugen dort nicht:

  1. `bash` im PATH ist eine Bash. Unter Windows ist es fast immer
     `C:\\Windows\\System32\\bash.exe`, der WSL-Launcher. Ohne installierte
     Distro schreibt der eine UTF-16-Diagnose nach stdout und endet mit 1. Ein
     Test, der damit einen Konfigwert liest, bekommt eine Zeichenkette voller
     NUL-Bytes, und der naechste `Path.mkdir()` meldet "embedded null
     character in path". Zwoelf Tests scheiterten mit dieser Meldung — keine
     davon nennt die Ursache.
  2. Ein Skript ist ausfuehrbar, weil das x-Bit gesetzt ist. `["./ralph.sh"]`
     verlaesst sich auf den Shebang; Windows liest keinen. 24 Tests endeten
     mit `OSError: [WinError 193] %1 is not a valid Win32 application`.
  3. Der PATH wird mit ":" zusammengesetzt. Unter Windows mit ";". Der
     `claude`-Stub, den ein Test gerade gelegt hat, wird dann nie gefunden.
  4. Ein Kindprozess braucht nur HOME und PATH. Unter Windows braucht er
     `SystemRoot` (sonst antwortet jeder Prozessstart mit einem
     COM+-Registry-Fehler) und `PATHEXT` (sonst findet PowerShell kein
     einziges `.exe` — `git` ist dann "not recognized", und jeder Test, der
     ein Wegwerf-Repo baut, faellt).

WARUM DAS EIN EIGENER FUND IST UND KEINE FUSSNOTE
    Ein roter Lauf, dessen Fehler nicht vom Prueflisten-Gegenstand kommen,
    ist schlimmer als ein ausgelassener Lauf: Er kostet dieselbe Zeit und
    liefert eine Zahl, der niemand mehr glaubt. 160 rote Tests verdecken jeden
    echten Befund, der darunter liegt — BL-129 lag darunter und war in der
    Liste nicht von den 159 anderen zu unterscheiden.

WARUM DIE ZUSICHERUNGEN AM QUELLTEXT HAENGEN
    Dieselbe Ueberlegung wie in BL-126 und BL-129: Auf einem Linux-Wirt ist
    jede der vier Annahmen wahr. Ein verhaltensbasierter Test waere dort auch
    ohne den Fix gruen und meldete den Rueckfall genau da nicht, wo er
    entsteht. Der Sammeltest unten faellt deshalb auf JEDEM Wirt, sobald eine
    Testdatei wieder `["bash", …]` oder `"python3 team/tools/…"` schreibt.
"""
import os
import re
from pathlib import Path

import conftest
from conftest import (BASH, basis_umgebung, entrypoint_aufruf, pfad_voran,
                      werkzeug_wert)

TESTS = Path(__file__).resolve().parent


# --- Die Aufloesung der Bash ------------------------------------------------
# Der Zweig, an dem haengt, ob 223 Tests laufen oder mit Grund uebersprungen
# werden. Er ist nur unter Windows erreichbar, also wird die Plattform hier
# gestellt — sonst waere er genau die Bauart "Zweig, der nie gefahren wurde",
# gegen die BL-126 bis BL-128 stehen.

def _windows_stellen(monkeypatch, kandidaten_wurzel, which):
    monkeypatch.setattr(conftest, "IST_WINDOWS", True)
    monkeypatch.setattr(conftest.shutil, "which", which)
    for var in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)",
                "LOCALAPPDATA"):
        monkeypatch.delenv(var, raising=False)
    if kandidaten_wurzel is not None:
        monkeypatch.setenv("ProgramFiles", str(kandidaten_wurzel))


def test_wsl_stub_wird_nicht_als_bash_akzeptiert(tmp_path, monkeypatch):
    """Der Anlassfall. Der Stub ist DA und ausfuehrbar — er ist nur keine
    Bash. Ihn als Rueckfall zu nehmen ist schlimmer als nichts zu finden:
    Er antwortet, und zwar falsch."""
    system32 = tmp_path / "Windows" / "System32"
    system32.mkdir(parents=True)
    stub = system32 / "bash.exe"
    stub.write_text("wsl", encoding="utf-8")

    _windows_stellen(monkeypatch, None,
                     lambda name: str(stub) if name == "bash" else None)
    assert conftest._finde_bash() is None, (
        "Der WSL-Launcher aus System32 wurde als Bash akzeptiert. Er liefert "
        "ohne Distro UTF-16-Muell auf stdout — das erzeugt Fehlermeldungen "
        "ueber NUL-Bytes in Pfaden statt der Aussage 'hier gibt es keine "
        "Bash'.")


def test_git_for_windows_wird_gefunden(tmp_path, monkeypatch):
    """Die Gegenprobe: Liegt eine echte Bash, muss die Bahn auch fahren.
    Ein Harnisch, der unter Windows grundsaetzlich ueberspringt, waere
    bequem und wertlos."""
    echte = tmp_path / "Git" / "bin" / "bash.exe"
    echte.parent.mkdir(parents=True)
    echte.write_text("bash", encoding="utf-8")

    _windows_stellen(monkeypatch, tmp_path, lambda name: None)
    assert conftest._finde_bash() == str(echte)


def test_bash_neben_dem_git_im_pfad_wird_gefunden(tmp_path, monkeypatch):
    """Installationen, die keinen der Standardorte benutzen: git.exe liegt im
    PATH unter <wurzel>/cmd/, die Bash unter <wurzel>/bin/."""
    wurzel = tmp_path / "Werkzeuge" / "Git"
    (wurzel / "cmd").mkdir(parents=True)
    (wurzel / "bin").mkdir()
    git = wurzel / "cmd" / "git.exe"
    git.write_text("git", encoding="utf-8")
    echte = wurzel / "bin" / "bash.exe"
    echte.write_text("bash", encoding="utf-8")

    _windows_stellen(monkeypatch, None,
                     lambda name: str(git) if name == "git" else None)
    assert conftest._finde_bash() == str(echte)


# --- Die drei uebrigen Annahmen ---------------------------------------------

def test_pfad_voran_nutzt_den_trenner_dieser_plattform(tmp_path):
    ergebnis = pfad_voran(tmp_path / "bin", {"PATH": "/bestand"})
    assert ergebnis == f"{tmp_path / 'bin'}{os.pathsep}/bestand"
    assert ergebnis.count(os.pathsep) == 1


def test_entrypoint_aufruf_nennt_den_interpreter():
    """Ohne genannten Interpreter meldet Windows WinError 193 — der Shebang
    wird dort nicht gelesen."""
    vektor = entrypoint_aufruf("./ralph.sh")
    assert len(vektor) == 2 and vektor[1] == "./ralph.sh"
    assert "bash" in vektor[0].lower(), \
        f"das erste Element muss der Interpreter sein, war: {vektor[0]!r}"


def test_basis_umgebung_traegt_die_grundausstattung_des_wirts(monkeypatch):
    """Die Minimal-Umgebung bleibt minimal — sie haelt TEAM_*-Werte der
    Wirtssitzung heraus —, aber das, was die Plattform selbst braucht, muss
    durch."""
    monkeypatch.setattr(conftest, "IST_WINDOWS", True)
    monkeypatch.setenv("SystemRoot", "C:\\Windows")
    monkeypatch.setenv("PATHEXT", ".COM;.EXE;.BAT")
    monkeypatch.setenv("TEAM_BUDGET_USD", "999")

    umgebung = basis_umgebung()
    assert umgebung["SystemRoot"] == "C:\\Windows", \
        "ohne SystemRoot antwortet jeder Prozessstart mit einem COM+-Fehler"
    assert umgebung["PATHEXT"] == ".COM;.EXE;.BAT", \
        "ohne PATHEXT findet PowerShell kein .exe — 'git' ist dann unbekannt"
    assert "TEAM_BUDGET_USD" not in umgebung, \
        "die Isolation gegen TEAM_*-Werte der Wirtssitzung darf nicht fallen"


def test_werkzeug_wert_nennt_einen_lauffaehigen_interpreter():
    wert = werkzeug_wert("team/tools/kosten.py")
    befehl, _, rest = wert.partition(" ")
    assert rest == "team/tools/kosten.py"
    assert conftest.shutil.which(befehl) or Path(befehl).is_file(), (
        f"'{befehl}' ist auf diesem Wirt nicht startbar. Unter Windows ist "
        "'python3' der App-Execution-Alias aus dem Microsoft Store: Er "
        "startet den Store und endet mit 'Python was not found'.")


# --- Der Sammeltest: die vier Annahmen duerfen nicht zurueckkommen ----------

VERBOTEN = (
    # Die Muster greifen auf das LISTENLITERAL, nicht auf `subprocess.run(`:
    # Der Aufruf steht regelmaessig ueber zwei Zeilen, und eine zeilenweise
    # Suche nach dem Aufrufnamen findet ihn dann nicht. Genau so ist der erste
    # Entwurf dieses Tests an bl16 vorbeigelaufen.
    (re.compile(r'\[\s*"bash"\s*,'),
     '["bash", …] — unter Windows der WSL-Launcher. '
     'Stattdessen: [BASH, …] aus conftest.'),
    (re.compile(r'\[\s*"\./[a-z-]+\.sh"\s*\]'),
     '["./x.sh"] — Windows liest keinen Shebang (WinError 193). '
     'Stattdessen: entrypoint_aufruf("./x.sh").'),
    (re.compile(r'"python3 team/tools/'),
     '"python3 team/tools/…" — unter Windows der Store-Alias. '
     'Stattdessen: werkzeug_wert("team/tools/…").'),
    (re.compile(r"""\}:\{env\['PATH'\]\}"""),
     'PATH mit ":" zusammengesetzt — unter Windows trennt ";". '
     'Stattdessen: pfad_voran(bin_dir, env).'),
)

# conftest.py loest diese vier Annahmen auf und muss sie dafuer nennen duerfen;
# bl122 zitiert die Kandidatenliste des Installers als Quelltext.
AUSGENOMMEN = {"conftest.py", "test_bl122_native_exitcode.py",
               Path(__file__).name}


def test_keine_testdatei_faellt_in_die_vier_annahmen_zurueck():
    funde = []
    for datei in sorted(TESTS.glob("test_*.py")):
        if datei.name in AUSGENOMMEN:
            continue
        for nummer, zeile in enumerate(
                datei.read_text(encoding="utf-8").splitlines(), 1):
            for muster, warum in VERBOTEN:
                if muster.search(zeile):
                    funde.append(f"{datei.name}:{nummer} — {warum}")
    assert not funde, (
        "Diese Stellen setzen einen POSIX-Wirt voraus (BL-130):\n  "
        + "\n  ".join(funde))

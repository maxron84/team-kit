#!/usr/bin/env python3
"""BL-199 — die Sperre gilt bahnübergreifend, oder sie gilt nicht.

Beide Bahnen liegen nach einer Installation im SELBEN Arbeitsbaum (`BL-126`:
jeder Installer schreibt beide Konfigurationen), und die Zusicherung heisst
*„eine Pipeline zur Zeit"*, nicht *„eine je Bahn"*. Seit `BL-190` gibt es
jedoch ZWEI Sperrartefakte: `.team-loop.lock` (pwsh, `FileShare::None`) und
`.team-loop.lock.d` (bash ohne `flock`). Die pwsh-Seite kannte den Ordner
nicht — an drei Stellen: `lib.psm1`, `entry/team-status.ps1` und
`install.ps1`. Ein bash-Lauf auf einer Windows-Maschine war fuer alle drei
unsichtbar: Der Kontostand meldete `idle`, und `install.ps1 --update` legte
uncommittete Dateien in `team/` ab — genau der Schaden, gegen den `BL-10`
gebaut wurde.

DER NAHELIEGENDE FIX TRAEGT NICHT, und das war der eigentliche Inhalt des
Eintrags: Die hinterlegte `pid` ist eine **MSYS-PID** aus einem eigenen
Prozessraum. Gemessen am 2026-08-27: Git-Bash meldete `$$` = 15946,
`Get-Process -Id 15946` fand zeitgleich nichts. Ein `Get-Process` darauf
stufte JEDE gehaltene bash-Sperre als verwaist ein — die Zusicherung waere
nicht wiederhergestellt, sondern schriftlich abgeschafft.

GEBAUT IST DESHALB VARIANTE (a) DES EINTRAGS, nachdem sie nachgemessen wurde
(2026-08-28, Hin- und Rueckweg): Die bash-Bahn legt zusaetzlich `winpid` ab
(`/proc/<pid>/winpid`), und die pwsh-Seite liest die. Fehlt sie — eine
aeltere Sperre, ein Linux-Wirt —, ist die Antwort **UNBEKANNT** und nicht
`idle`; `team_pipeline_laeuft` hat dafuer auf beiden Bahnen einen dritten
Rueckgabewert.

DIE GEGENRICHTUNG IST DER TEIL, OHNE DEN ES KEINE MELDUNG IST: Derselbe Baum
ohne Sperre muss beide Wege schweigen lassen, und eine VERWAISTE Sperre darf
den anderen Weg nicht dauerhaft blockieren — sonst tauscht dieser Eintrag
denselben Fehlalarm ein, den `BL-190` gerade abgestellt hat.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, RufCode, kit_pfad, ueberspringe_ohne_bahn

WURZEL = Path(__file__).resolve().parents[2]
ORDNER = ".team-loop.lock.d"
DATEI = ".team-loop.lock"


# --- Die Messung, auf der der ganze Eintrag ruht -----------------------------


def _winpid_verfuegbar():
    """Hat die Bash dieses Wirts eine Windows-PID im Angebot?"""
    if not BASH:
        return False
    ergebnis = subprocess.run(
        [BASH, "-c", 'cat "/proc/$$/winpid" 2>/dev/null || true'],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return ergebnis.stdout.strip().isdigit()


def test_die_msys_pid_ist_fuer_powershell_keine_pid():
    """Der Befund, der Variante (b) des Eintrags ausgeschlossen hat.

    Er wird hier GEMESSEN und nicht zitiert: Wuerde eine kuenftige Git-Version
    die PID-Raeume zusammenlegen, waere `winpid` ueberfluessig — und dieser
    Fall der erste, der es sagt.
    """
    ueberspringe_ohne_bahn("pwsh")
    if os.name != "nt":
        pytest.skip("Der PID-Namensraum von MSYS gibt es nur unter Windows.")
    if not BASH:
        pytest.skip("keine Bash auf diesem Wirt")
    msys = subprocess.run(
        [BASH, "-c", 'echo $$'], capture_output=True, text=True,
        encoding="utf-8", errors="replace").stdout.strip()
    win = subprocess.run(
        [BASH, "-c", 'cat "/proc/$$/winpid" 2>/dev/null || true'],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace").stdout.strip()
    if not win.isdigit():
        pytest.skip("diese Bash legt kein /proc/<pid>/winpid an")
    assert msys != win, (
        "MSYS-PID und Windows-PID sind identisch — dann braucht die pwsh-Seite "
        "kein `winpid`, und BL-199 waere anders zu bauen als geschehen.")


# --- (1) Die bash-Bahn hinterlegt das Merkmal, das die andere lesen kann -----


@pytest.mark.nur_bash(
    "Prueft, WAS die bash-Bahn ablegt. Die Gegenprobe — dass die pwsh-Bahn es "
    "liest — steht unten und laeuft auf der pwsh-Bahn.")
def test_der_sperrordner_traegt_die_windows_pid(tmp_path):
    """Ohne dieses Merkmal ist der Ordner fuer die andere Bahn stumm."""
    if not _winpid_verfuegbar():
        pytest.skip("Dieser Wirt hat kein /proc/<pid>/winpid (kein Git for "
                    "Windows) — dort bleibt es bei `pid`, und die pwsh-Seite "
                    "meldet ehrlich UNBEKANNT statt zu raten.")
    # Gelesen wird WAEHREND die Sperre gehalten wird, nicht danach: Der
    # EXIT-Trap von team_lock_aufraeumen_anmelden raeumt den Ordner beim
    # Prozessende wieder weg — ein Blick von aussen sieht also nichts, und der
    # Test pruefte dann das Aufraeumen statt das Ablegen.
    lib = kit_pfad("lib.sh")
    skript = (f'cd "{tmp_path.as_posix()}"\n'
              f'source "{lib.as_posix()}"\n'
              'team_lock_ordner_nehmen test >/dev/null 2>&1\n'
              'echo "PID=[$(cat .team-loop.lock.d/pid 2>/dev/null)]"\n'
              'echo "WINPID=[$(cat .team-loop.lock.d/winpid 2>/dev/null)]"\n')
    ergebnis = subprocess.run([BASH, "-c", skript], capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
    werte = dict(z.split("=", 1) for z in ergebnis.stdout.split() if "=" in z)
    winpid = werte.get("WINPID", "").strip("[]")
    assert winpid.isdigit(), (
        "Der Sperrordner traegt keine Windows-PID — die pwsh-Bahn kann dann "
        f"nur raten (BL-199).\nAusgabe:\n{ergebnis.stdout}\n{ergebnis.stderr}")
    assert werte.get("PID", "").strip("[]").isdigit(), (
        "Die MSYS-PID muss bleiben — die bash-Bahn wertet weiter sie aus.")


# --- (2) Beide Bahnen beantworten dieselbe Frage gleich ----------------------


def _laeuft(schale, wurzel):
    """`team_pipeline_laeuft <wurzel>` — 0 laeuft, 1 nicht, 2 unklar."""
    ergebnis = schale.lauf([RufCode("team_pipeline_laeuft", str(wurzel))],
                           cwd=wurzel)
    return ergebnis.returncode, ergebnis


def test_ein_sauberer_baum_laesst_beide_wege_schweigen(tmp_path, schale):
    """Die Gegenrichtung, ohne die es keine Meldung ist."""
    rc, ergebnis = _laeuft(schale, tmp_path)
    assert rc == 1, (
        f"erwartet 1 (laeuft nicht), war {rc}\n{ergebnis.stderr}")


def test_eine_verwaiste_sperre_blockiert_nicht_dauerhaft(tmp_path, schale):
    """Sonst taeuscht dieser Eintrag denselben Fehlalarm ein, den `BL-190`
    gerade abgestellt hat: Ein abgestuerzter Lauf blockierte jeden folgenden,
    und niemand koennte den Unterschied zu einem echten Doppellauf sehen."""
    ordner = tmp_path / ORDNER
    ordner.mkdir()
    # Eine PID, die es sicher nicht gibt — auf beiden Bahnen dieselbe Angabe.
    (ordner / "pid").write_text("999999999\n", encoding="utf-8")
    (ordner / "winpid").write_text("999999999\n", encoding="utf-8")
    rc, ergebnis = _laeuft(schale, tmp_path)
    assert rc == 1, (
        f"Eine verwaiste Sperre gilt als gehalten (rc={rc}) — das ist der "
        f"Dauer-Fehlalarm aus BL-190.\n{ergebnis.stderr}")


def test_ein_sperrordner_ohne_auswertbares_merkmal_ist_UNBEKANNT(tmp_path, schale):
    """Der dritte Zustand, und der Kern des Eintrags.

    Auf der pwsh-Bahn: `winpid` fehlt, nur die MSYS-`pid` liegt da — sie ist
    dort keine PID. Auf der bash-Bahn spiegelbildlich: `pid` fehlt, nur
    `winpid` liegt da — eine Windows-PID liegt ausserhalb des
    MSYS-Prozessraums. Beide Male ist weder `idle` noch `laeuft` eine Messung.
    """
    ordner = tmp_path / ORDNER
    ordner.mkdir()
    if schale.ist_bash:
        (ordner / "winpid").write_text("4711\n", encoding="utf-8")
    else:
        (ordner / "pid").write_text("4711\n", encoding="utf-8")
    rc, ergebnis = _laeuft(schale, tmp_path)
    assert rc == 2, (
        f"erwartet 2 (UNBEKANNT), war {rc}. Weder 'idle' noch 'laeuft' ist "
        f"hier eine Messung — beides waere eine Behauptung.\n{ergebnis.stderr}")


def test_eine_gehaltene_sperre_der_anderen_bahn_wird_erkannt(tmp_path, schale):
    """Der Anlassfall, an der lebenden Sperre statt an einer Attrappe."""
    ueberspringe_ohne_bahn("bash")
    if not _winpid_verfuegbar():
        pytest.skip("Ohne /proc/<pid>/winpid kann die pwsh-Seite die "
                    "bash-Sperre nicht auswerten — sie meldet dann UNBEKANNT, "
                    "und genau das prueft der Fall darueber.")
    halter = subprocess.Popen(
        [BASH, "-c",
         f'cd "{tmp_path.as_posix()}"; '
         f'source "{kit_pfad("lib.sh").as_posix()}"; '
         'team_lock_ordner_nehmen test >/dev/null 2>&1; sleep 30'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if (tmp_path / ORDNER / "winpid").is_file():
                break
            import time
            time.sleep(0.1)
        assert (tmp_path / ORDNER / "winpid").is_file(), (
            "der Halter hat die Sperre nicht genommen")
        rc, ergebnis = _laeuft(schale, tmp_path)
    finally:
        halter.kill()
        halter.wait()
    assert rc == 0, (
        f"Eine GEHALTENE Sperre der bash-Bahn wird nicht erkannt (rc={rc}) — "
        f"der Kontostand meldet dann idle, und ein Update laeuft in einen "
        f"laufenden Lauf hinein (BL-10).\n{ergebnis.stderr}")


# --- (3) Dieselbe Frage, dieselbe Antwort — auch im Installer ----------------
# Beide Installer schreiben die Pruefung AUSGESCHRIEBEN aus (sie sourcen bzw.
# importieren bewusst nichts). Die Zusicherung, dass alle Stellen dieselbe
# Frage gleich beantworten, haengt deshalb an diesem Fall und nicht am
# Vertrauen — dieselbe Erwaegung wie bei `BL-190`.


INSTALLER = {
    "bash": WURZEL / "bash" / "install.sh",
    "pwsh": WURZEL / "pwsh" / "install.ps1",
}


def test_beide_installer_kennen_beide_sperrartefakte(schale):
    datei = INSTALLER[schale.name]
    if not datei.is_file():
        pytest.skip(f"{datei.name} liegt nur im Kit")
    text = datei.read_text(encoding="utf-8")
    assert ".team-loop.lock.d" in text, (
        f"{datei.name} kennt den Sperrordner der bash-Bahn nicht — ein "
        "bash-Lauf ist fuer den BL-10-Schutz damit unsichtbar (BL-199).")
    assert ".team-loop.lock" in text
    assert "winpid" in text, (
        f"{datei.name} wertet das einzige bahnuebergreifend lesbare Merkmal "
        "nicht aus (BL-199).")


def test_beide_statusberichte_kennen_den_dritten_zustand(schale):
    datei = WURZEL / schale.name / "entry" / schale.entrypoint("team-status")
    if not datei.is_file():
        datei = WURZEL / schale.entrypoint("team-status")
    if not datei.is_file():
        pytest.skip("team-status dieser Bahn liegt hier nicht")
    text = datei.read_text(encoding="utf-8")
    assert "team_pipeline_laeuft" in text, (
        "Der Bericht fragt nicht die gemeinsame Funktion — dann driften die "
        "Bahnen wieder auseinander (die Lehre von BL-190).")
    assert "unbekannt" in text, (
        "Der Bericht kennt nur laeuft/idle. Eine Sperre der anderen Bahn ohne "
        "auswertbares Merkmal wuerde damit als eines von beiden behauptet "
        "(BL-199).")


def test_die_reichweite_der_sperre_steht_geschrieben():
    """Die stillste Haelfte des Problems war die falsche Erwartung."""
    anhang = WURZEL / "doku" / "anhang-a.md"
    if not anhang.is_file():
        pytest.skip("doku/anhang-a.md liegt nur im Kit")
    text = anhang.read_text(encoding="utf-8")
    assert "BL-199" in text and "bahnübergreifend" in text, (
        "Anhang A sagt nicht, wie weit die Sperre reicht.")
    assert "Wo sie NICHT gilt" in text, (
        "Die Grenzen fehlen — und die sind der ehrliche Teil: Unter Linux "
        "haelt bahnuebergreifend keine der beiden Proben.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

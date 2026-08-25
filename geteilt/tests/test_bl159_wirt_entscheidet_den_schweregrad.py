#!/usr/bin/env python3
"""BL-159 und BL-160: Was `kit-einrichten.sh` auf einem Windows-Wirt meldet.

BEIDE FUNDE STAMMEN AUS DEMSELBEN LAUF
    Der erste vollstaendige `kit-test.sh` auf einer echten Windows-Maschine
    (2026-08-24, `BL-146`) fiel in Stufe 10 mit vier roten Pruefungen. Sie
    hatten genau zwei Ursachen, und beide sind Windows.

BL-159 — DAS POSIX-URTEIL AUF EINEM WINDOWS-WIRT
    `kit-einrichten.sh` meldete dort drei FEHLER: `flock` fehlt, `chmod +x`
    wirkt nicht, `flock` greift nicht. Alle drei sind wahr — Git for Windows
    liefert kein `flock`, und NTFS traegt unter Git-Bash kein Exec-Bit.

    Falsch war der SCHWEREGRAD. Die Zwei-Bahnen-Tabelle im README sagt
    "Bash-Bahn (Linux · WSL)" gegen "pwsh-Bahn (Windows ohne WSL)": Nativ unter
    Windows ist die bash-Bahn die zweite Wahl. Das Kit erklaerte also eine
    Maschine fuer unbereit, auf der seine NATIVE Bahn tadellos laeuft — und
    schickte den Anwender an `sudo apt install util-linux`, ein Paket, das es
    fuer Git-Bash nicht gibt. Eine Abhilfe, die auf dieser Maschine nicht
    ausfuehrbar ist, ist keine; dieselbe Erwaegung wie bei `BL-144`.

    Dazu ein zweiter, kleinerer Fund derselben Sorte: Fehlt `flock` als
    WERKZEUG, meldete das Skript den Befund ZWEIMAL — einmal in 2/5 (Werkzeug
    fehlt) und einmal in 3/5 (Sperre greift nicht). Zwei Meldungen fuer EINE
    Ursache lesen sich wie zwei Probleme, und `kit-test.sh` zaehlte deshalb
    zwei Nennungen, wo es eine erwartete.

BL-160 — DIE REPARATUR ERZEUGTE DEN SCHADEN
    `--verknuepfen` meldete `✓ Verknuepft: … → …` — mit Pfeil — und hatte eine
    regulaere KOPIE hingelegt: Unter MSYS legt `ln -s` ohne Symlink-Recht keine
    Verknuepfung an und meldet trotzdem Erfolg.

    Das wiegt schwerer als es klingt. `~/.claude/scripts/team-init.sh` ist laut
    `kit-test.sh` "das einzige Stueck des Kits, von dem eine Kopie ausserhalb
    des Repos liegen kann" — das Kit hat eine eigene Erkennung dafuer gebaut,
    weil so eine Kopie veraltet und dann stillsteht. Ausgerechnet die
    REPARATUR erzeugte sie, und der Satz daneben ("Eine Verknuepfung kann nicht
    veralten — die Kopie konnte es") war damit eine Falschaussage.

DIE ARBEITSTEILUNG DIESER DATEI
    Den LAUF fuehrt `kit-test.sh` Stufe 10 — dort steht ein echtes HOME mit
    einer alten Kit-Kopie darin. Hier steht die Zusicherung am QUELLTEXT, damit
    sie auch auf einem Linux-Wirt faellt, wenn jemand sie zurueckdreht. Dazu
    EIN Verhaltensfall, der nur auf einem Windows-Wirt etwas beweisen kann und
    anderswo sichtbar uebersprungen wird.
"""
import platform
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, verlange_bash

REPO_ROOT = Path(__file__).resolve().parents[2]


def _quelle():
    pfad = REPO_ROOT / "bash" / "kit-einrichten.sh"
    if not pfad.is_file():
        pytest.skip("kit-einrichten.sh liegt nur in der Kit-Ablage")
    return pfad.read_text(encoding="utf-8")


def _auf_windows():
    """Der Wirt, um den es geht: nativ Windows, bash ueber Git for Windows."""
    return platform.system() == "Windows" or sys.platform.startswith("win")


# --- BL-159: der Schweregrad haengt am Wirt ---------------------------------

def test_der_wirt_wird_ueberhaupt_erkannt():
    """Ohne die Unterscheidung gibt es keinen Schweregrad, nur ein Urteil."""
    quelle = _quelle()
    assert "MINGW*|MSYS*|CYGWIN*" in quelle, (
        "kit-einrichten.sh unterscheidet Windows nicht mehr von einem "
        "POSIX-Wirt. Damit faellt es wieder ein POSIX-Urteil ueber eine "
        "Maschine, auf der die pwsh-Bahn die native ist (BL-159).")
    assert 'WIRT="windows"' in quelle


@pytest.mark.parametrize("befund,warum", [
    ("flock fehlt — Git for Windows liefert keines",
     "Der alte Text nannte 'sudo apt install util-linux' — auf einer "
     "Windows-Maschine ein Rat ins Leere"),
    ("chmod +x wirkt hier nicht",
     "NTFS traegt unter Git-Bash kein Exec-Bit; das ist das Dateisystem "
     "und keine kaputte Maschine"),
])
def test_die_zwei_windows_befunde_sind_warnungen(befund, warum):
    """Sie verschwinden NICHT — sie wechseln den Schweregrad.

    Geprueft wird deshalb beides: dass der Befund noch dasteht, und dass er
    ueber `warnung` laeuft. Ein Befund, der still wird, waere schlimmer als
    einer mit falschem Schweregrad.
    """
    quelle = _quelle()
    assert befund in quelle, f"Der Befund ist verschwunden statt milder: {warum}"
    stelle = quelle.index(befund)
    # Rueckwaerts bis zum Aufruf, der ihn ausgibt.
    kopf = quelle.rfind("\n", 0, stelle)
    zeile = quelle[kopf + 1:stelle]
    assert "warnung" in zeile, (
        f"'{befund}' wird nicht als Warnung ausgegeben (BL-159). {warum}. "
        "Als Fehler erklaert das Kit eine Maschine fuer unbereit, auf der "
        "seine native Bahn laeuft.")


def test_die_windows_befunde_nennen_die_bahn_die_es_besser_kann():
    """Eine Warnung ohne Ausweg ist eine, die man wegklickt (BL-14).

    Beide Befunde muessen sagen, wo das Problem nicht besteht — sonst bleibt
    dem Leser nur die Erkenntnis, dass etwas fehlt.
    """
    quelle = _quelle()
    stelle = quelle.index("flock fehlt — Git for Windows liefert keines")
    block = quelle[stelle:stelle + 900]
    assert "pwsh-Bahn" in block, (
        "Der flock-Befund nennt die Bahn nicht, auf der es die Folge nicht "
        "gibt. Damit steht dort ein Mangel ohne Ausweg.")
    stelle = quelle.index("chmod +x wirkt hier nicht")
    block = quelle[stelle:stelle + 700]
    assert "bash ./ralph.sh" in block, (
        "Der Exec-Bit-Befund nennt den Aufruf ueber den Interpreter nicht — "
        "und das ist die Abhilfe, die auf dieser Maschine wirklich geht.")


def test_flock_wird_nicht_zweimal_gemeldet():
    """Zwei Meldungen fuer EINE Ursache lesen sich wie zwei Probleme.

    Die Sperrprobe in 3/5 setzt das Werkzeug voraus. Fehlt es, steht der
    Befund schon in 2/5 — dann hat die Probe nichts beizutragen.
    """
    quelle = _quelle()
    assert "if ! command -v flock >/dev/null 2>&1; then" in quelle, (
        "Die Sperrprobe laeuft wieder auch ohne flock. Sie meldet dann "
        "'flock greift nicht' als zweiten Befund neben 'flock fehlt' — "
        "und kit-test.sh zaehlt zwei Nennungen, wo es eine erwartet "
        "(BL-159).")


# --- BL-160: keine Verknuepfung behaupten, die es nicht gibt ----------------

def test_verknuepfen_prueft_das_ergebnis_statt_es_zu_glauben():
    """Die tragende Zusicherung von BL-160.

    Unter MSYS legt `ln -s` ohne Symlink-Recht eine Kopie an und meldet
    Erfolg. Wer danach nicht nachsieht, behauptet eine Verknuepfung, die es
    nicht gibt — und erzeugt genau die veraltete Launcher-Kopie, gegen die
    dieser Schritt gebaut ist.
    """
    quelle = _quelle()
    assert "verknuepfung_bestaetigen" in quelle, (
        "kit-einrichten.sh meldet den Erfolg von 'ln -s' wieder ungeprueft "
        "(BL-160).")
    assert 'if [ -L "$1" ]; then ok "$3"; return 0; fi' in quelle, (
        "Die Bestaetigung prueft nicht mehr mit -L, ob wirklich eine "
        "Verknuepfung entstanden ist.")
    # Und kein zweiter Weg daran vorbei: Beide ln-Aufrufe muessen durch die
    # Bestaetigung laufen, sonst ist die Zusicherung an einer Stelle offen.
    assert quelle.count("verknuepfung_bestaetigen") >= 3, (
        "Nicht beide Verknuepfungs-Pfade (neu anlegen / Kit-Kopie ersetzen) "
        "gehen durch die Bestaetigung. Der ungepruefte Pfad behauptet dann "
        "weiter Erfolg (BL-160).")


def test_die_kopie_meldung_nennt_folge_und_abhilfe():
    """Der Unterschied zwischen einem Befund und einem Achselzucken."""
    quelle = _quelle()
    stelle = quelle.index("Kopie statt Verknüpfung")
    block = quelle[stelle:stelle + 1400]
    assert "veraltet" in block, "Die Folge fehlt — warum ist eine Kopie schlimm?"
    assert "winsymlinks:nativestrict" in block, "Die erste Abhilfe fehlt."
    assert "vollem Pfad" in block, (
        "Der Weg, der ohne Sonderrechte funktioniert, fehlt — und genau der "
        "ist auf einer verwalteten Maschine der einzige.")


# --- Der Verhaltensfall, der nur hier etwas beweist -------------------------

@pytest.mark.skipif(not _auf_windows(),
                    reason="belegt nur auf einem nativen Windows-Wirt etwas "
                           "(dort fehlt flock und das Exec-Bit haelt nicht)")
def test_auf_windows_endet_die_pruefung_mit_null():
    """Der Fall, der den Fund ausgeloest hat — jetzt als Zusicherung.

    Vor BL-159 endete `--nur-pruefen` hier mit 1 und der Zeile "3 Fehler …
    die Maschine ist noch nicht bereit". Sie ist bereit; nur nicht fuer die
    Bahn, die dieses Skript prueft.

    Bewusst NICHT gegen "0 Warnungen" geprueft: Die Befunde sollen stehen
    bleiben. Geprueft wird, dass sie den Lauf nicht mehr als gescheitert
    ausweisen.
    """
    verlange_bash()
    pfad = REPO_ROOT / "bash" / "kit-einrichten.sh"
    if not pfad.is_file():
        pytest.skip("kit-einrichten.sh liegt nur in der Kit-Ablage")
    lauf = subprocess.run(
        [BASH, str(pfad), "--nur-pruefen", "--nicht-interaktiv"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert lauf.returncode == 0, (
        "kit-einrichten.sh meldet diese Windows-Maschine als nicht bereit. "
        "Wenn darunter nur flock und das Exec-Bit stehen, ist BL-159 "
        f"zurueckgedreht:\n{lauf.stdout[-2000:]}")
    assert "Warnung" in lauf.stdout or "! " in lauf.stdout, (
        "Der Lauf ist gruen OHNE Warnungen — dann sind die Befunde nicht "
        "milder geworden, sondern verschwunden. Das waere schlimmer als der "
        "falsche Schweregrad.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

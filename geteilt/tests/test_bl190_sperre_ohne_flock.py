#!/usr/bin/env python3
"""BL-190: Fehlt `flock`, meldete das Kit einen Sperrkonflikt, den es nicht gab.

⚠️ Feldbefund vom Kit selbst (2026-08-26, Git for Windows).

`team_lock()` entschied an EINER Bedingung ueber ZWEI Fehlerklassen:

    exec 9>.team-loop.lock
    if ! flock -n 9; then
        echo "… Eine andere T.E.A.M.-Pipeline laeuft bereits …"

Ein FEHLENDES PROGRAMM liefert dort denselben Nicht-Null-Status wie eine
BELEGTE SPERRE. Unter Git for Windows gibt es `flock` nicht — es gehoert nicht
zum MSYS2-Kern, den Git mitliefert. Also brach dort JEDE Rolle der bash-Bahn
sofort ab, und zwar mit einer Meldung, die auf einen Nebenlaeufigkeitskonflikt
zeigte. Wer ihr folgte, suchte einen zweiten Lauf, killte Prozesse oder
loeschte die Lock-Datei; nichts davon half, weil die Datei nie das Problem war.
Der wahre Grund (`flock: command not found`) scrollte eine Zeile vorher vorbei.

DER ENTSCHEID DES BETREIBERS (2026-08-27) war nicht "laut ohne Sperre
weiterlaufen" und nicht "abbrechen", sondern ein ERSATZVERFAHREN: ein
Sperrordner per `mkdir`. `mkdir` ist auf jedem POSIX-Dateisystem und unter MSYS
atomar — Pruefen und Anlegen sind EIN Schritt. Damit bleibt die Zusicherung
"eine Pipeline zur Zeit" ERHALTEN, statt gegen eine Meldung getauscht zu
werden; zwei Rollen gleichzeitig im selben Arbeitsbaum sind der Schaden, den
BL-12 teuer belegt hat.

WARUM DIE FAELLE AN DEN EINZELFUNKTIONEN HAENGEN UND NICHT AN `team_lock`
    Ob `flock` da ist, ist eine Eigenschaft der MASCHINE. Ein Test, der nur
    `team_lock` faehrt, prueft auf einer Linux-Maschine ausschliesslich den
    flock-Zweig und auf dieser Windows-Maschine ausschliesslich den
    Ordner-Zweig — auf beiden waere er gruen, und die jeweils andere Haelfte
    bliebe unbelegt. Genau diese Doppelbahn-Drift hat BL-131 und BL-145 teuer
    bezahlt. Deshalb ist der Ersatzweg in EIGENE Funktionen zerlegt, und die
    Faelle unten fahren sie einzeln; der Zweig, den die Wirtsmaschine gerade
    verkoerpert, wird zusaetzlich end-to-end gefahren.

    Gefahren wird dabei der ECHTE Abschnitt aus der ECHTEN Datei: Der Test
    schneidet ihn heraus und sourct ihn. Eine Kopie im Test waere eine zweite
    Wahrheit — dieselbe Erwaegung wie bei der AST-Sonde der pwsh-Bahn
    (BL-142).
"""
import re
import subprocess
from pathlib import Path

import pytest

from conftest import BASH, kit_pfad, nur_code, verlange_bash

WURZEL = Path(__file__).resolve().parents[2]
LIB_SH = kit_pfad("lib.sh")

ORDNER = ".team-loop.lock.d"
DATEI = ".team-loop.lock"
FREMDE_PIPELINE = "andere T.E.A.M.-Pipeline"


# --- Der Abschnitt aus der echten Datei -------------------------------------

def _lock_abschnitt():
    """Schneidet den Lock-Abschnitt aus `lib.sh` — Kopf bis zum naechsten Kopf.

    Der Abschnitt ist absichtlich in sich geschlossen (er ruft nichts aus dem
    Rest der Bibliothek), damit genau das hier moeglich ist, ohne die halbe
    Umgebung eines Zielprojekts nachzubauen.
    """
    if not LIB_SH.is_file():
        pytest.skip(f"{LIB_SH} liegt in dieser Ablage nicht")
    zeilen = LIB_SH.read_text(encoding="utf-8").splitlines()
    start = None
    for i, zeile in enumerate(zeilen):
        if zeile.startswith("# --- Lock ("):
            start = i
            break
    if start is None:
        pytest.fail("lib.sh hat keinen Abschnittskopf '# --- Lock ('")
    ende = len(zeilen)
    for i in range(start + 1, len(zeilen)):
        if zeilen[i].startswith("# --- "):
            ende = i
            break
    return "\n".join(zeilen[start:ende]) + "\n"


@pytest.fixture
def sonde(tmp_path):
    """Eine Ablage mit dem echten Lock-Abschnitt daneben.

    Rueckgabe: eine Funktion, die ein Bash-Schnipsel in dieser Ablage faehrt.
    """
    verlange_bash()
    quelle = tmp_path / "lock.sh"
    # newline="\n" ist Pflicht, nicht Kosmetik: Unter Windows uebersetzt Python
    # beim Schreiben nach CRLF, und eine Bash-Datei mit CR am Zeilenende
    # zerbricht an jedem Wort (BL-137).
    quelle.write_text(_lock_abschnitt(), encoding="utf-8", newline="\n")

    def fahre(schnipsel):
        return subprocess.run(
            [BASH, "-c", "set -u; source ./lock.sh\n" + schnipsel],
            cwd=tmp_path, capture_output=True, text=True,
            encoding="utf-8", errors="replace")

    fahre.ablage = tmp_path
    return fahre


# --- Teil (1): die Fehlerklasse ist getrennt --------------------------------

def test_die_meldung_nennt_das_werkzeug_und_keine_fremde_pipeline(sonde):
    """Die zweite Gegenprobe des Eintrags, woertlich.

    Ein Lauf ohne `flock` und ohne gehaltene Sperre muss genau EINE Meldung
    erzeugen, die das Werkzeug NENNT — und KEINE ueber eine fremde Pipeline.
    Das ist der ganze Fund: Vorher stand hier die falsche Fehlerklasse.
    """
    lauf = sonde("team_flock_fehlt_melden harry")
    assert lauf.returncode == 0
    assert "flock" in lauf.stderr, (
        "die Meldung nennt das fehlende Werkzeug nicht — genau daran ist der "
        f"Feldfall gescheitert:\n{lauf.stderr}")
    assert FREMDE_PIPELINE not in lauf.stderr, (
        "die Meldung zeigt weiter auf einen Nebenlaeufigkeitskonflikt, den es "
        f"nicht gibt:\n{lauf.stderr}")
    assert "[harry]" in lauf.stderr, "die Rolle steht nicht davor"


def test_team_lock_fragt_erst_nach_dem_werkzeug_und_dann_nach_der_sperre():
    """Die GATTUNG des Fundes, maschinenunabhaengig (BL-154).

    Der Defekt war nicht eine schlechte Meldung, sondern EINE Bedingung fuer
    ZWEI Klassen. Deshalb haengt die Zusicherung an der Reihenfolge im
    Quelltext: Die Abfrage nach dem Werkzeug muss VOR dem ersten `flock`
    stehen. Ein Fix, der nur die Meldung umschreibt, ist hier rot.
    """
    code = nur_code(LIB_SH.read_text(encoding="utf-8"))
    treffer = re.search(r"team_lock\(\)\s*\{(.*?)\n\}", code, re.S)
    assert treffer, "team_lock() ist in lib.sh nicht auffindbar"
    rumpf = treffer.group(1)
    probe = rumpf.find("team_flock_vorhanden")
    ruf = rumpf.find("flock -n")
    assert probe != -1, "team_lock fragt nicht, ob flock ueberhaupt da ist"
    assert ruf != -1, "team_lock ruft flock gar nicht mehr auf"
    assert probe < ruf, (
        "team_lock ruft flock, BEVOR es fragt, ob es flock gibt — genau die "
        "Bauart, an der BL-190 haengt")


def test_der_ersatzweg_bleibt_der_ersatz_und_nicht_der_normalfall():
    """Wo `flock` da ist, bleibt es.

    Zwei Sperrmechaniken gleichzeitig im Feld waeren schlimmer als eine
    kaputte: Bei einem Vorfall wuesste niemand, welche gegriffen hat. Der
    Ordner darf deshalb nur im ELSE-Zweig stehen.
    """
    code = nur_code(LIB_SH.read_text(encoding="utf-8"))
    treffer = re.search(r"team_lock\(\)\s*\{(.*?)\n\}", code, re.S)
    rumpf = treffer.group(1)
    assert "team_lock_ordner_nehmen" in rumpf, "der Ersatzweg wird nie genommen"
    assert rumpf.index("flock -n") < rumpf.index("team_lock_ordner_nehmen"), (
        "der Ordner-Weg steht vor dem flock-Weg — dann ist er der Normalfall")


# --- Teil (2): die Zusicherung bleibt erhalten ------------------------------

def test_zwei_laeufe_in_derselben_ablage_der_zweite_wird_abgewiesen(sonde):
    """Die ERSTE Gegenprobe des Eintrags — der eigentliche Punkt des Fixes.

    Der Ersatz darf die Zusicherung "eine Pipeline zur Zeit" nicht aufgeben.
    Gefahren wird das mit einem echten zweiten Prozess: Der erste haelt die
    Sperre und LEBT noch, waehrend der zweite sie zu nehmen versucht.
    """
    lauf = sonde(
        "team_lock_ordner_nehmen erster || exit 9\n"
        "bash -c 'source ./lock.sh; team_lock_ordner_nehmen zweiter'\n"
        "echo \"zweiter-rc=$?\"\n")
    assert "zweiter-rc=1" in lauf.stdout, (
        "der zweite Lauf wurde NICHT abgewiesen — die Sperre ist gegen eine "
        f"Meldung eingetauscht worden:\nSTDOUT {lauf.stdout}\n"
        f"STDERR {lauf.stderr}")
    assert FREMDE_PIPELINE in lauf.stderr, (
        "der abgewiesene Lauf sagt nicht, dass eine andere Pipeline laeuft — "
        f"hier waere die Meldung richtig:\n{lauf.stderr}")


def test_die_erste_sperre_wird_ueberhaupt_genommen(sonde):
    """Gegenrichtung. Ohne sie belegt der Fall darueber nichts.

    Eine Sperre, die IMMER abweist, wiese den zweiten Lauf auch ab — und der
    Test daneben bliebe gruen, waehrend das Kit unbenutzbar waere. Dieselbe
    Erwaegung wie bei BL-14.

    Geprueft wird WAEHREND des Laufs, nicht danach: Beim Prozessende gibt der
    EXIT-Trap die Sperre frei. Ein Blick von aussen sieht deshalb immer eine
    leere Ablage — und saehe sie auch dann, wenn nie gesperrt worden waere.
    """
    lauf = sonde(
        "team_lock_ordner_nehmen erster; echo \"rc=$?\"\n"
        "[ -d " + ORDNER + " ] && echo ordner-da\n"
        "[ -f " + ORDNER + "/pid ] && echo pid-da\n")
    assert "rc=0" in lauf.stdout, f"schon der erste Lauf scheitert:\n{lauf.stderr}"
    assert "ordner-da" in lauf.stdout, "kein Sperrordner angelegt"
    assert "pid-da" in lauf.stdout, (
        "keine PID hinterlegt — dann ist eine verwaiste Sperre nicht von einer "
        "gehaltenen zu unterscheiden")


def test_die_sperre_faellt_beim_prozessende_weg(sonde):
    """Was beim flock-Weg der Kernel tut, muss der Ordner-Weg selbst tun.

    Ein Deskriptor faellt beim Exit weg, ein Ordner nicht. Ohne die Freigabe
    sammelte jede Ablage nach jedem Lauf ein Verzeichnis an — dieselbe Gattung
    wie BL-196, nur diesmal im Arbeitsbaum des Anwenders statt in %TEMP%.
    """
    lauf = sonde("team_lock_ordner_nehmen erster\n[ -d " + ORDNER + " ] && echo drin\n")
    assert "drin" in lauf.stdout, "waehrend des Laufs gab es gar keine Sperre"
    assert not (sonde.ablage / ORDNER).exists(), (
        "der Sperrordner ueberlebt den Prozess — der naechste Lauf muss ihn "
        "erst als Leiche erkennen, und in der Ablage liegt Muell")


# --- Die Leiche: eine verwaiste Sperre darf nicht dauerhaft blockieren ------

def test_eine_verwaiste_sperre_wird_uebernommen(sonde):
    """Ohne diesen Teil tauscht der Fix einen Fehlalarm gegen einen dauerhaften.

    Ein abgestuerzter Lauf hinterlaesst den Ordner. Waere er damit fuer immer
    belegt, waere die Ablage unbrauchbar — und der Anwender saesse wieder vor
    einer Meldung ueber eine Pipeline, die es nicht gibt.
    """
    lauf = sonde(
        "mkdir " + ORDNER + "\n"
        # Ein Kind, das sofort endet: seine PID ist danach mit Sicherheit tot,
        # und sie stammt aus DEMSELBEN Prozessraum wie die Pruefung. Eine
        # ausgedachte Nummer waere unter MSYS die falsche Namensordnung.
        "tot=\"$(bash -c 'echo $$')\"\n"
        "printf '%s\\n' \"$tot\" > " + ORDNER + "/pid\n"
        "team_lock_ordner_nehmen nachfolger; echo \"rc=$?\"\n"
        "cat " + ORDNER + "/pid\n")
    assert "rc=0" in lauf.stdout, (
        "die verwaiste Sperre blockiert dauerhaft:\n"
        f"STDOUT {lauf.stdout}\nSTDERR {lauf.stderr}")
    assert FREMDE_PIPELINE not in lauf.stderr, (
        "die Uebernahme meldet einen Konflikt — ein toter Prozess haelt nichts")


def test_die_uebernahme_bleibt_still(sonde):
    """Sie erschiene sonst nach JEDEM regulaeren Lauf (BL-14).

    Der Vorlauf laesst absichtlich eine Leiche liegen, wie es ein Abbruch tut.
    Meldete das Kit sie, waere die Meldung der Normalzustand — und damit keine.
    """
    lauf = sonde(
        "mkdir " + ORDNER + "\n"
        "tot=\"$(bash -c 'echo $$')\"\n"
        "printf '%s\\n' \"$tot\" > " + ORDNER + "/pid\n"
        "team_lock_ordner_nehmen nachfolger\n")
    assert lauf.stderr.strip() == "", (
        f"die stille Uebernahme meldet doch etwas:\n{lauf.stderr}")


def test_eine_gehaltene_sperre_gilt_nicht_als_verwaist(sonde):
    """Die Gegenrichtung zur Leiche.

    Ein Fix, der JEDE Sperre fuer verwaist haelt, macht beide Faelle darueber
    gruen und schafft die Zusicherung ab.
    """
    lauf = sonde(
        "mkdir " + ORDNER + "\n"
        "printf '%s\\n' \"$$\" > " + ORDNER + "/pid\n"
        "team_lock_ordner_verwaist; echo \"rc=$?\"\n")
    assert "rc=1" in lauf.stdout, (
        "die Sperre eines LEBENDEN Prozesses gilt als verwaist:\n"
        f"{lauf.stdout}{lauf.stderr}")


def test_ohne_lesbare_pid_gilt_die_sperre_als_verwaist(sonde):
    """Der bewusst gewaehlte Ausgang, damit er nicht still umkippt.

    Steht der Ordner ohne PID-Datei, ist der Lauf zwischen `mkdir` und dem
    Schreiben gestorben. Ihn als "gehalten" zu werten machte die Ablage
    dauerhaft unbrauchbar — durch genau den Fehlalarm, den BL-190 abstellt.
    """
    lauf = sonde("mkdir " + ORDNER + "\nteam_lock_ordner_verwaist; echo \"rc=$?\"")
    assert "rc=0" in lauf.stdout, (
        f"ein Ordner ohne PID blockiert dauerhaft:\n{lauf.stdout}{lauf.stderr}")


# --- Freigeben: nur die eigene Sperre ---------------------------------------

def test_team_unlock_gibt_die_eigene_sperre_frei(sonde):
    """Ausdruecklich, nicht nur ueber den Trap.

    Der Trap greift erst beim Prozessende. Eine langlebige Sitzung — der
    Selbsttest ist eine — braucht den Weg von Hand; genau dafuer hat die
    pwsh-Bahn ihr `team_unlock` seit jeher.
    """
    lauf = sonde(
        "team_lock_ordner_nehmen a\n"
        "[ -d " + ORDNER + " ] && echo vorher-da\n"
        "team_unlock; echo \"rc=$?\"\n"
        "[ -d " + ORDNER + " ] || echo nachher-weg\n")
    assert "vorher-da" in lauf.stdout, "es gab nie eine Sperre"
    assert "rc=0" in lauf.stdout
    assert "nachher-weg" in lauf.stdout, (
        "die eigene Sperre bleibt liegen — dann sammelt jede Ablage nach jedem "
        "Lauf ein Verzeichnis an (Gattung BL-196)")


def test_team_unlock_gibt_auch_den_flock_deskriptor_frei():
    """Sonst gibt dieselbe Funktion auf dem einen Weg frei und auf dem anderen
    nur den Anschein.

    Maschinenunabhaengig am Quelltext geprueft: Ob der Deskriptor ueberhaupt
    offen war, haengt daran, ob diese Maschine `flock` hat — genau die
    Doppelbahn-Drift, gegen die die Faelle oben zerlegt sind.
    """
    code = nur_code(LIB_SH.read_text(encoding="utf-8"))
    treffer = re.search(r"team_unlock\(\)\s*\{(.*?)\n\}", code, re.S)
    assert treffer, "team_unlock() ist in lib.sh nicht auffindbar"
    assert "9>&-" in treffer.group(1), (
        "team_unlock schliesst den flock-Deskriptor nicht — auf einer Maschine "
        "MIT flock bleibt die Sperre nach dem Aufruf gehalten")


def test_team_unlock_raeumt_keine_fremde_sperre_weg(sonde):
    """Ohne diese Richtung macht der Fix aus der Zusicherung ihr Gegenteil.

    Ein `team_unlock`, das blind loescht, gibt die Sperre eines LAUFENDEN
    zweiten Prozesses frei — und dann committen zwei Rollen in denselben
    Arbeitsbaum (BL-12).
    """
    lauf = sonde(
        "mkdir " + ORDNER + "\n"
        "printf '%s\\n' 999999 > " + ORDNER + "/pid\n"
        "team_unlock; echo \"rc=$?\"\n")
    assert "rc=0" in lauf.stdout
    assert (sonde.ablage / ORDNER).is_dir(), (
        "team_unlock hat eine FREMDE Sperre weggeraeumt")


# --- End-to-end auf dem Zweig, den diese Maschine verkoerpert ---------------

def _hat_flock():
    verlange_bash()
    lauf = subprocess.run([BASH, "-c", "command -v flock >/dev/null 2>&1"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    return lauf.returncode == 0


def test_team_lock_ohne_flock_sperrt_trotzdem(sonde):
    """Der Feldfall selbst, ungekuerzt — auf einer Maschine ohne `flock`.

    Genau hier starb im Feld jede Rolle der bash-Bahn, bevor ein einziger
    Prompt entstand. Auf einer Maschine MIT `flock` ist dieser Weg nicht
    erreichbar; dort uebernimmt der Fall darunter.
    """
    if _hat_flock():
        pytest.skip("diese Maschine hat flock — der Ersatzweg ist hier nicht "
                    "erreichbar; die Einzelfunktionen oben decken ihn ab")
    lauf = sonde(
        "team_lock harry; echo \"rc=$?\"\n"
        "[ -d " + ORDNER + " ] && echo ordner-da\n"
        "[ -e " + DATEI + " ] && echo datei-da\n"
        "echo \"held=${TEAM_LOCK_HELD:-0}\"\n")
    assert "rc=0" in lauf.stdout, (
        "team_lock bricht ohne flock weiter ab — der Feldfall steht:\n"
        f"STDOUT {lauf.stdout}\nSTDERR {lauf.stderr}")
    assert "flock" in lauf.stderr and FREMDE_PIPELINE not in lauf.stderr, (
        f"die falsche Fehlerklasse steht wieder da:\n{lauf.stderr}")
    assert "ordner-da" in lauf.stdout, "ohne flock wurde nicht gesperrt"
    assert "datei-da" not in lauf.stdout, (
        "der Ersatzweg legt zusaetzlich die flock-Datei an — dann liegen zwei "
        "Sperrmechaniken nebeneinander")
    assert "held=1" in lauf.stdout, (
        "TEAM_LOCK_HELD bleibt ungesetzt — die Kind-Skripte der Vollautomatik "
        "versuchten dann jedes fuer sich erneut zu sperren")


def test_team_lock_mit_flock_nimmt_weiter_flock(sonde):
    """Die Gegenrichtung — auf einer Maschine MIT `flock`.

    Der Ersatz darf den Normalfall nicht verdraengen: Wo `flock` da ist, muss
    die Datei entstehen und der Ordner ausbleiben.
    """
    if not _hat_flock():
        pytest.skip("diese Maschine hat kein flock — genau der Fall aus BL-190; "
                    "der flock-Zweig ist hier nicht erreichbar")
    lauf = sonde(
        "team_lock harry; echo \"rc=$?\"\n"
        "[ -e " + DATEI + " ] && echo datei-da\n"
        "[ -d " + ORDNER + " ] && echo ordner-da\n")
    assert "rc=0" in lauf.stdout, f"{lauf.stdout}{lauf.stderr}"
    assert lauf.stderr.strip() == "", (
        f"der Normalfall meldet etwas — dann meldet er es immer:\n{lauf.stderr}")
    assert "datei-da" in lauf.stdout, "der flock-Weg wurde nicht genommen"
    assert "ordner-da" not in lauf.stdout, (
        "der Ersatzweg lief zusaetzlich zum Normalfall")


# --- Die GATTUNG: dieselbe Frage steht an drei Stellen ----------------------
# BL-154. „Läuft gerade eine Pipeline?" wird in `lib.sh`, in `team-status.sh`
# und in `install.sh` gefragt. Alle drei fragten `flock`, und alle drei gaben
# ohne `flock` die falsche Antwort — in ENTGEGENGESETZTE Richtungen, was den
# Fund erst vollstaendig macht.

def test_die_pipeline_frage_haengt_nirgends_allein_an_flock():
    """Der Kern der Gattung. Ein Fix nur in `team_lock` waere unvollstaendig.

    Geprueft wird die Bauart, nicht die Stelle: Wo `flock` in einer
    Sperr-Abfrage steht, muss entweder `command -v` davorstehen (sonst liest
    ein fehlendes Programm sich als gehaltene Sperre) ODER der Ordner-Weg
    daneben (sonst meldet die Stelle „idle", waehrend der Ersatz sperrt).
    """
    stellen = {
        "lib.sh": kit_pfad("lib.sh"),
        "team-status.sh": WURZEL / "bash" / "entry" / "team-status.sh",
        "install.sh": WURZEL / "bash" / "install.sh",
    }
    for name, pfad in stellen.items():
        if not pfad.is_file():
            pytest.skip(f"{name} liegt in dieser Ablage nicht")
    for name, pfad in stellen.items():
        code = nur_code(pfad.read_text(encoding="utf-8"))
        for zeile in code.splitlines():
            if "flock -n" not in zeile:
                continue
            umfeld = code[max(0, code.index(zeile) - 400):
                          code.index(zeile) + len(zeile)]
            # Beide Schreibweisen zaehlen: die Abfrage von Hand und die
            # benannte Funktion aus lib.sh. Geprueft wird, DASS gefragt wird.
            assert ("command -v flock" in umfeld
                    or "team_flock_vorhanden" in umfeld), (
                f"{name}: `flock -n` ohne vorherige Abfrage, ob es flock gibt "
                f"— ein fehlendes Programm liest sich dort als gehaltene "
                f"Sperre (BL-190):\n{zeile.strip()}")


def test_beide_aufrufstellen_kennen_den_sperrordner():
    """`team-status.sh` und `install.sh` muessen den Ersatz mitfragen.

    Sonst meldet der Kontostand „idle", waehrend eine Pipeline laeuft, und der
    Installer aktualisiert in einen laufenden Lauf hinein — der Schaden aus
    `BL-10`, und er waere durch den Fix zu `BL-190` erst entstanden.
    """
    status = WURZEL / "bash" / "entry" / "team-status.sh"
    install = WURZEL / "bash" / "install.sh"
    if not status.is_file() or not install.is_file():
        pytest.skip("die bash-Bahn liegt in dieser Ablage nicht vollstaendig")
    st = nur_code(status.read_text(encoding="utf-8"))
    assert "team_pipeline_laeuft" in st, (
        "team-status.sh fragt nicht ueber team_pipeline_laeuft — die Zeile "
        "'Pipeline: idle' kennt den Ersatzweg dann nicht")
    ins = nur_code(install.read_text(encoding="utf-8"))
    assert ORDNER in ins, (
        "install.sh kennt den Sperrordner nicht und aktualisiert damit in "
        "einen laufenden Lauf hinein (BL-10)")


def test_team_pipeline_laeuft_beantwortet_beide_mechaniken(sonde):
    """Gefahren, nicht nur gelesen — in beide Richtungen.

    Der Abschnitt ist in sich geschlossen, also faehrt der Fall die echte
    Funktion. Die Gegenrichtung (leere Ablage schweigt) ist Pflicht: Eine
    Antwort, die immer „laeuft" sagt, legte jedes Update still still.
    """
    lauf = sonde(
        "team_pipeline_laeuft; echo \"leer=$?\"\n"
        "team_lock_ordner_nehmen a\n"
        "team_pipeline_laeuft; echo \"gesperrt=$?\"\n"
        "team_unlock\n"
        "team_pipeline_laeuft; echo \"frei=$?\"\n")
    assert "leer=1" in lauf.stdout, (
        f"eine leere Ablage gilt als belegt:\n{lauf.stdout}{lauf.stderr}")
    assert "gesperrt=0" in lauf.stdout, (
        f"eine gehaltene Sperre wird nicht erkannt:\n{lauf.stdout}{lauf.stderr}")
    assert "frei=1" in lauf.stdout, (
        f"nach team_unlock gilt die Ablage weiter als belegt:\n{lauf.stdout}")


def test_eine_verwaiste_sperre_gilt_nicht_als_laufende_pipeline(sonde):
    """Sonst blockierte eine Leiche jedes `--update` dauerhaft.

    Genau der Fehlalarm, den `BL-190` abstellt — nur an der zweiten Stelle.
    """
    lauf = sonde(
        "mkdir " + ORDNER + "\n"
        "tot=\"$(bash -c 'echo $$')\"\n"
        "printf '%s\\n' \"$tot\" > " + ORDNER + "/pid\n"
        "team_pipeline_laeuft; echo \"rc=$?\"\n")
    assert "rc=1" in lauf.stdout, (
        f"eine verwaiste Sperre gilt als laufende Pipeline:\n{lauf.stdout}")


# --- Die Folge in der Ablage des Anwenders ----------------------------------

def test_der_sperrordner_steht_im_gitignore_fragment():
    """Sonst meldet `git status` in jedem Feldprojekt einen fremden Ordner.

    Das Muster `.team-loop.lock` deckt `.team-loop.lock.d/` NICHT ab — es ist
    ein eigener Eintrag, und ohne ihn liegt die Sperre eines jeden Laufs im
    Blickfeld des Anwenders.
    """
    fragment = WURZEL / "bootstrap" / "gitignore.fragment"
    if not fragment.is_file():
        pytest.skip("bootstrap/gitignore.fragment liegt nur in der Kit-Ablage")
    zeilen = [z.strip() for z in
              fragment.read_text(encoding="utf-8").splitlines()]
    assert ORDNER + "/" in zeilen or ORDNER in zeilen, (
        f"'{ORDNER}' fehlt im Fragment — vorhanden: "
        f"{[z for z in zeilen if 'team-loop' in z]}")

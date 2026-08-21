"""Die Doppelbahn: eine Testsuite, zwei Shells (bash und pwsh).

WARUM ES DIESE DATEI GIBT
    Das Kit bekommt eine native pwsh-Bahn in PowerShell, waehrend Bash
    die Linux-Implementierung bleibt (`plans/windows-nativ.md`). Der nahe
    liegende Weg waere eine zweite Testsuite gewesen. Das waere der Fehler:
    Zwei Suiten driften genauso auseinander wie zwei Implementierungen, nur
    unbemerkt — und im Kit wird jede Feldlehre ein Test, also waere jede
    kuenftige Lehre eine Gelegenheit zur Drift.

    Stattdessen: DIESELBE Testdatei, der Harnisch waehlt die Shell, die
    Assertions sind identisch. Eine neue Lehre wird damit auf der anderen Bahn
    automatisch rot, bis sie nachgezogen ist. Drift ist nicht verboten —
    sie ist sichtbar.

WARUM DIE TESTS KEINE SHELL-SYNTAX MEHR ENTHALTEN DUERFEN
    Bis hierher stand in den Testkoerpern Bash-Syntax, nicht nur ein
    Funktionsaufruf — `set -euo pipefail`, `if …; then echo URTEIL=sauber`,
    `k="$(…)"`. Das ist nicht parametrisierbar. Ein Test formuliert deshalb
    nur noch SCHRITTE (unten); wie ein Schritt in der jeweiligen Shell
    ausgesprochen wird, weiss allein die Schale.

    Braucht ein Test einen Schritt, den es hier nicht gibt, wird er hier
    ergaenzt — nicht im Testkoerper umgangen.

WARUM DIE SCHRITTE EINER FOLGE IN EINEM PROZESS BLEIBEN
    `team_guard_begin` legt seinen Schnappschuss in SHELL-VARIABLEN ab
    (`TEAM_GUARD_VORHER`, `TEAM_GUARD_HASH`), nicht in Dateien. Ein
    `team_guard_verify` in einem zweiten Prozess saehe einen leeren
    Schnappschuss und spraeche jede Rolle frei — der Test waere gruen und
    wertlos. `Schale.lauf()` rendert deshalb ALLE Schritte in EIN Skript.
    Deshalb gibt es auch `Schreib`: eine Mutation zwischen zwei Aufrufen muss
    in derselben Shell passieren, nicht in Python davor.

DIE AUFRUFKONVENTION FUER DEN POWERSHELL-ZWEIG (Vertrag fuer Stufe 3)
    Sie wird hier festgelegt, weil der Harnisch sie kodiert:

    1. Eine Bash-Funktion mit `return 0`/`return 1` wird in PowerShell zu
       einer Funktion, die `$true`/`$false` zurueckgibt. Kein `exit`, kein
       `$LASTEXITCODE` — die Funktionen laufen im selben Prozess.
    2. Eine Bash-Funktion, die Text auf stdout schreibt, benutzt in
       PowerShell `Write-Output`. Sie gibt NICHTS zusaetzlich zurueck, sonst
       vermischen sich Nutzlast und Statussignal im Ausgabestrom.
    3. Eine Funktion tut entweder das eine oder das andere, nie beides.
       `lib.sh` haelt sich heute schon daran; der Vertrag schreibt es fest.
    4. Diagnose geht nach stderr (`Write-Error` bzw. `[Console]::Error`),
       damit `Ausgabe`-Schritte sie nicht einsammeln.
    5. Eine Funktion mit ABGESTUFTEM Exit-Code (`team_budget_check`: 0 ok,
       1 Warnschwelle, 2 Soft-Cap, 3 Hard-Cap) gibt in PowerShell einen
       `[int]` zurueck und schreibt ihre Meldung mit
       `[Console]::Out.WriteLine(…)` — nicht mit `Write-Output`, sonst
       landen Meldung und Code gemeinsam im Ausgabestrom und der Aufrufer
       kann sie nicht trennen. Das ist die einzige erlaubte Ausnahme von
       Punkt 3, und sie betrifft die Budget-Durchsetzung, also die Stelle,
       an der ein verschluckter Code Geld kostet.
    6. Setzt die Bibliothek ihren EIGENEN Default (nicht den des Projekts),
       geschieht das in einer greppbaren Zeile:
       Bash `NAME="${NAME:-wert}"`, PowerShell
       `$NAME = Team-Default 'NAME' 'wert'`. Tests lesen diesen Wert
       statisch aus der Quelle (siehe `Schale.default_muster`), weil ein
       `source` den PROJEKTWERT liefern wuerde und nicht den Default —
       die Lehre aus BL-100.
    7. Abgeleitete Bausteine, die heute als Bibliotheks-Variablen entstehen
       (`SMOKE_ZEILE`, `TEAM_ROLE_BUDGET_USD`), muessen aus dem Modul
       exportiert werden (`Export-ModuleMember -Variable`). Sonst sind sie
       vom Aufrufer nicht lesbar, und der `Variable`-Schritt unten geht ins
       Leere — still, mit einer leeren Zeichenkette.

WAS PASSIERT, SOLANGE ES `team/lib.psm1` NOCH NICHT GIBT
    Die pwsh-Bahn wird uebersprungen, nicht rot. Stufe 1 darf den
    Linux-Betrieb nicht anfassen. Sobald Stufe 3 die Datei liefert, laufen
    dieselben Tests ohne eine weitere Zeile Testcode auch dort.

DIE DOPPELBAHN-QUOTE
    Am Ende jedes Laufs steht, wie viele Tests auf beiden Bahnen liefen und
    wie viele nur auf einer. Gleichwertigkeit laesst sich nicht zusichern,
    ohne sie zu messen; eine Schwelle waere willkuerlich, die Zahl ist es
    nicht. Wer einen Test bewusst nur fuer eine Bahn fuehrt, markiert ihn mit
    `@pytest.mark.nur_bash` und begruendet es — die Markierung taucht in
    jedem Lauf auf, statt still zu bleiben.
"""
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
IST_WINDOWS = os.name == "nt"


# --- Die Wirtsplattform ------------------------------------------------------
# BL-130. Bis hierher war der Harnisch fuer einen POSIX-Wirt geschrieben, und
# das stand nirgends — es war einfach so. Der erste Lauf unter nativem Windows
# hat 160 Tests rot gemacht, keinen einzigen davon wegen des Kits.
#
# Vier Annahmen trugen nicht:
#
#   1. `bash` im PATH ist eine Bash. Unter Windows ist es fast immer
#      C:\Windows\System32\bash.exe — der WSL-Launcher. Ohne installierte
#      Distro schreibt der eine UTF-16-Diagnose und endet mit 1. Als stdout
#      gelesen wird daraus ein Konfigwert voller NUL-Bytes, und der naechste
#      Path.mkdir() meldet "embedded null character in path" statt "hier gibt
#      es keine Bash". Die teuerste Bauart von Fehlermeldung.
#   2. Ein Skript ist ausfuehrbar, weil das x-Bit gesetzt ist. Unter Windows
#      ist `./ralph.sh` keine ausfuehrbare Datei, sondern Text —
#      WinError 193.
#   3. Der PATH wird mit ":" zusammengesetzt. Unter Windows mit ";".
#   4. Ein Kindprozess braucht nur HOME und PATH. Unter Windows braucht er
#      SystemRoot (sonst COM+-Registry-Fehler) und PATHEXT (sonst findet
#      PowerShell kein einziges .exe — `git` ist dann "not recognized").
#
# Die Antwort steht hier und nicht in 21 Testdateien: Wer eine dieser vier
# Annahmen braucht, holt sie sich von hier.


def _bash_kandidaten():
    """Die Fundorte einer ECHTEN Bash unter Windows, in Suchreihenfolge.

    Git for Windows ist laut doku/faq.md ohnehin Voraussetzung fuer die
    pwsh-Bahn — sein bash.exe ist damit der Kandidat, der auf einer
    eingerichteten Zielmaschine wirklich liegt.
    """
    for var in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)",
                "LOCALAPPDATA"):
        wurzel = os.environ.get(var)
        if wurzel:
            yield Path(wurzel) / "Git" / "bin" / "bash.exe"
            yield Path(wurzel) / "Git" / "usr" / "bin" / "bash.exe"
    # Git liegt im PATH als <wurzel>/cmd/git.exe; die Bash ist sein Geschwister
    # unter <wurzel>/bin/. Das faengt die Installationen ab, die keinen der
    # Standardorte oben benutzen.
    git = shutil.which("git")
    if git:
        wurzel = Path(git).resolve().parent.parent
        yield wurzel / "bin" / "bash.exe"
        yield wurzel / "usr" / "bin" / "bash.exe"


def _finde_bash():
    """Der bash, mit dem die Bash-Bahn gefahren wird — oder None.

    Unter POSIX ist das schlicht der aus dem PATH. Unter Windows wird der
    WSL-Launcher in System32 AUSGESCHLOSSEN: Er ist kein Rueckfall, sondern
    eine Fehlerquelle mit falscher Diagnose (siehe Kopf). Wer WSL benutzen
    will, faehrt die Suite IN der Distro — dann ist os.name "posix" und diese
    Verzweigung existiert gar nicht.
    """
    if not IST_WINDOWS:
        return shutil.which("bash")
    for kandidat in _bash_kandidaten():
        if kandidat.is_file():
            return str(kandidat)
    gefunden = shutil.which("bash")
    if gefunden and "system32" not in gefunden.lower():
        return gefunden
    return None


BASH = _finde_bash()


def _finde_python_befehl():
    r"""Der NAME, unter dem Python fuer team.config.<endung> erreichbar ist.

    Bewusst ein Name und kein Pfad: `lib.sh` ruft `$TEAM_KOSTEN_TOOL summe`
    OHNE Anfuehrungszeichen auf — der Wert wird wortgetrennt. Ein
    sys.executable wie "C:\Program Files\Python312\python.exe" zerfiele
    dort in zwei Woerter.

    Die Kandidatenreihenfolge ist dieselbe wie in `Finde-Python`
    (pwsh/install.ps1) und aus demselben Grund: Unter Windows legen weder
    python.org noch winget ein python3.exe an. Was `where python3` dort
    findet, ist der App-Execution-Alias aus dem Microsoft Store — er startet
    den Store und endet mit "Python was not found". Die Tests wuerden also
    einen Namen in ihre Fixture-Konfiguration schreiben, den es auf der
    Maschine nachweislich nicht gibt (BL-125 in gruen).
    """
    kandidaten = (("python", "python3", "py") if IST_WINDOWS
                  else ("python3", "python", "py"))
    for kandidat in kandidaten:
        if shutil.which(kandidat) is None:
            continue
        try:
            probe = subprocess.run(
                [kandidat, "-c", "import sys; print(sys.version_info[0])"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        except (OSError, subprocess.SubprocessError):
            continue
        if probe.returncode == 0 and probe.stdout.strip() == "3":
            return kandidat
    # Letzter Ausweg: der Interpreter, unter dem pytest gerade laeuft. Er ist
    # nachweislich da; nur die Wortgrenze oben ist nicht mehr zugesichert.
    return sys.executable


PYTHON_BEFEHL = _finde_python_befehl()


def werkzeug_wert(relativer_pfad):
    """Der Wert fuer TEAM_KOSTEN_TOOL / TEAM_BEUTEBUCH_TOOL in einer Fixture.

        werkzeug_wert("team/tools/kosten.py")
            ->  "python3 team/tools/kosten.py"   (POSIX)
            ->  "python team/tools/kosten.py"    (Windows)

    Ein hartkodiertes "python3 …" in einer Fixture ist unter Windows ein
    stiller Fehlschlag: Der Aufruf endet mit 1, die Bibliothek sieht eine
    leere Antwort, und der Test urteilt ueber etwas, das nie gelaufen ist.
    """
    return f"{PYTHON_BEFEHL} {relativer_pfad}"


# BL-133: TEAM_PYTHON ist eine Angabe ueber die MASCHINE, kein Testwert.
#
# BL-131 hat den festen `python3` aus `lib.sh` entfernt und durch
# `"$TEAM_PYTHON"` ersetzt — dreizehnmal. Den WERT traegt seither
# `team.config.sh`, gefuellt vom Installer aus dem, was er auf der Maschine
# wirklich gefunden hat. Nur: Der Harnisch ist kein installiertes Projekt. Er
# sourct `lib.sh` direkt, und dann greift deren eigener POSIX-Default
# `python3` — unter Windows der App-Execution-Alias aus dem Microsoft Store.
#
# Die Folge war ein Lauf, in dem 65 Fehlschlaege dieselbe Zeile trugen
# ("Python was not found") und kein einziger davon aus dem Kit kam: BL-130
# in neuer Gestalt. Der Harnisch nimmt hier deshalb dieselbe Rolle ein wie
# `team.config.sh` im Feld — er sagt, wie der Interpreter auf DIESER Maschine
# heisst. `werkzeug_wert()` tut fuer die beiden Werkzeugzeilen laengst
# dasselbe; die dreizehn Aufrufe in `lib.sh` hatte niemand nachgezogen.
os.environ.setdefault("TEAM_PYTHON", PYTHON_BEFEHL)


# Die Variablen, ohne die ein Windows-Kindprozess nicht arbeiten kann. Die
# Minimal-Umgebung in `Schale.lauf` ist Absicht — sie haelt TEAM_*-Werte der
# Wirtssitzung aus dem Test heraus. Diese Liste erweitert sie um genau das,
# was die Plattform selbst braucht, und um nichts anderes.
_WINDOWS_GRUNDAUSSTATTUNG = (
    "SystemRoot", "SystemDrive", "windir", "PATHEXT", "COMSPEC",
    "TEMP", "TMP", "USERPROFILE", "HOMEDRIVE", "HOMEPATH",
    "APPDATA", "LOCALAPPDATA", "PROGRAMDATA",
    "ProgramFiles", "ProgramFiles(x86)", "ProgramW6432",
    "PSModulePath", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE",
)


def basis_umgebung(**zusatz):
    """Die Minimal-Umgebung eines Testlaufs, plattformrichtig.

    POSIX: HOME und PATH, wie bisher. Windows: dazu die Grundausstattung
    oben — ohne SystemRoot beantwortet jeder Prozessstart mit einem
    COM+-Registry-Fehler, ohne PATHEXT findet PowerShell `git` nicht und
    meldet "The term 'git' is not recognized".
    """
    umgebung = {"HOME": str(Path.home()),
                "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
                # BL-133: kein TEAM_*-Wert der Wirtssitzung, sondern eine
                # Angabe ueber die Maschine — dieselbe, die im Feld der
                # Installer in team.config.sh schreibt. Ohne sie faellt
                # `lib.sh` auf ihren POSIX-Default `python3` zurueck, und der
                # ist unter Windows der Store-Alias (BL-131).
                "TEAM_PYTHON": os.environ.get("TEAM_PYTHON", PYTHON_BEFEHL)}
    if IST_WINDOWS:
        for name in _WINDOWS_GRUNDAUSSTATTUNG:
            wert = os.environ.get(name)
            if wert is not None:
                umgebung[name] = wert
    umgebung.update(zusatz)
    return umgebung


def pfad_voran(bin_dir, umgebung=None):
    """Stellt <bin_dir> dem PATH voran — mit dem Trenner DIESER Plattform.

    `f"{bin_dir}:{env['PATH']}"` ergibt unter Windows EINEN unbrauchbaren
    Eintrag, und der `claude`-Stub, den der Test gerade gelegt hat, wird nie
    gefunden. Der Lauf ruft dann die echte CLI oder gar nichts.
    """
    bestand = (umgebung or os.environ).get("PATH", "")
    return f"{bin_dir}{os.pathsep}{bestand}" if bestand else str(bin_dir)


def entrypoint_aufruf(skript):
    """Der Befehlsvektor, mit dem ein Entrypoint gestartet wird.

    `["./ralph.sh"]` verlaesst sich darauf, dass der Kernel den Shebang liest.
    Windows liest keinen Shebang — dort ist eine .sh eine Textdatei, und
    subprocess meldet WinError 193. Der Interpreter wird deshalb genannt
    statt vorausgesetzt; unter POSIX aendert das nichts am Verhalten.
    """
    return [BASH or "bash", str(skript)]


# --- Die zwei Ablagen ---------------------------------------------------------
# Seit der Bahn-Trennung sieht das KIT anders aus als ein installiertes
# PROJEKT, und die Tests laufen in beiden:
#
#     Kit                     installiertes Projekt
#     bash/lib.sh             team/lib.sh
#     pwsh/lib.psm1           team/lib.psm1
#     geteilt/tools/…         team/tools/…
#     geteilt/prompts/…       team/prompts/…
#
# Gesprochen wird hier in der Sprache des ZIELPROJEKTS — `kit_pfad("lib.sh")`
# —, weil das die Ablage ist, fuer die die Tests geschrieben sind. Die
# Uebersetzung steht an dieser einen Stelle statt in 105 Einzelzeilen; genau
# das war der Grund, sie ueberhaupt zu bauen.

_BAHN_DATEI = {
    "lib.sh":      "bash", "redteam.sh":  "bash",
    "lib.psm1":    "pwsh", "redteam.ps1": "pwsh",
}
_GETEILTE_ORDNER = ("tools", "prompts", "tests")


def kit_pfad(*teile):
    """Loest einen Pfad der Team-Infrastruktur in BEIDER Ablage auf.

    Gibt den Pfad der Kit-Ablage zurueck, wenn es ihn dort gibt, sonst den
    der installierten Ablage — auch dann, wenn er nicht existiert, damit
    Fehlermeldungen den Pfad nennen, den der Leser erwartet.
    """
    kopf = teile[0]
    projekt = REPO_ROOT.joinpath("team", *teile)
    if kopf in _BAHN_DATEI:
        kit = REPO_ROOT / _BAHN_DATEI[kopf] / kopf
    elif kopf in _GETEILTE_ORDNER:
        kit = REPO_ROOT.joinpath("geteilt", *teile)
    else:
        return projekt
    return kit if kit.exists() else projekt


def entrypoint_pfad(name):
    """Loest einen ENTRYPOINT in beiden Ablagen auf ('team-status.sh').

    kit_pfad() kann das nicht und soll es auch nicht: Es kennt die
    Team-INFRASTRUKTUR (lib, tools, prompts, tests), und die liegt in der
    Installation geschlossen unter team/. Die Entrypoints liegen dort in der
    WURZEL und im Kit nach Bahn getrennt unter bash/entry/ bzw. pwsh/entry/ —
    eine andere Regel, die kit_pfad() nur verwaschen wuerde.

    Rueckgabe ist der Pfad der Ablage, die gerade vorliegt; existiert er
    nirgends, der Pfad der INSTALLATION — damit eine Fehlermeldung den Ort
    nennt, an dem der Leser die Datei erwartet.
    """
    installiert = REPO_ROOT / name
    if installiert.is_file():
        return installiert
    for bahn in ("bash", "pwsh"):
        kit = REPO_ROOT / bahn / "entry" / name
        if kit.is_file():
            return kit
    return installiert


def bahnen_in_der_ablage():
    """Welche Bahnen liegen hier ueberhaupt? — Rueckgabe z. B. {"bash"}.

    Der Installer kennt seit BL-119 `--nur-bash` / `--nur-pwsh`: eine
    ausdrueckliche ABWAHL durch den Anwender. Ein so installiertes Projekt
    hat die andere Bahn nicht, und das ist kein Defekt. Tests, die beide
    Bahnen brauchen, sollen dort UEBERSPRINGEN — aber sichtbar, mit einem
    Grund, der die Abwahl nennt. Ein stiller Uebersprung liest sich am Ende
    wie ein bestandener Nachweis.
    """
    gefunden = set()
    for muster, bahn in (("*.sh", "bash"), ("bash/entry/*.sh", "bash"),
                         ("*.ps1", "pwsh"), ("pwsh/entry/*.ps1", "pwsh")):
        if any(REPO_ROOT.glob(muster)):
            gefunden.add(bahn)
    return gefunden


def ueberspringe_ohne_beide_bahnen():
    """Skip mit Begruendung, wenn eine Bahn abgewaehlt wurde."""
    bahnen = bahnen_in_der_ablage()
    if {"bash", "pwsh"} <= bahnen:
        return
    da = ", ".join(sorted(bahnen)) or "keine"
    _QUOTE["einbahnig"].add(da)
    pytest.skip(
        f"einbahnige Ablage (vorhanden: {da}) — die andere Bahn ist mit "
        f"--nur-bash/--nur-pwsh abgewaehlt worden. Zurueckholen: "
        f"install mit --update ohne Schalter.")


def ueberspringe_ohne_bahn(bahn):
    """Skip mit Begruendung, wenn GENAU DIESE Bahn nicht in der Ablage liegt.

    BL-129: `ueberspringe_ohne_beide_bahnen()` gab es schon, aber es trifft nur
    Tests, die BEIDE Bahnen VERGLEICHEN. Ein Test, der EINE Bahn FAEHRT, hatte
    keinen Uebersprung fuer IHR Fehlen — er lief los und scheiterte an einer
    Datei, die es in dieser Ablage nicht gibt. In einer mit `--nur-pwsh`
    installierten Ablage waren so 109 von 487 Faellen rot, ohne dass irgendetwas
    kaputt war.

    Der Unterschied ist die Frage, die der Test stellt:

        vergleicht beide Bahnen  -> ueberspringe_ohne_beide_bahnen()
        faehrt EINE Bahn         -> ueberspringe_ohne_bahn("<bahn>")

    Der Uebersprung ist ABSICHTLICH sichtbar (Zusammenfassung unten): Ein
    stiller Uebersprung von 109 Faellen liest sich am Ende wie ein bestandener
    Nachweis, und das waere schlimmer als das rote Bild, das er ersetzt.
    """
    if bahn in bahnen_in_der_ablage():
        return
    da = ", ".join(sorted(bahnen_in_der_ablage())) or "keine"
    # Die ZAHL ist der Punkt: BL-129 wurde entdeckt, weil 109 Faelle rot waren.
    # Waeren sie still uebersprungen worden, haette niemand hingesehen. pytest
    # legt die laufende Kennung in die Umgebung — das ist der einzige Weg, sie
    # ohne Fixture zu erfahren, und ein Fixture waere ein Zwang fuer jeden
    # Aufrufer.
    kennung = os.environ.get("PYTEST_CURRENT_TEST", "unbekannt").split(" ")[0]
    _QUOTE["fehlende_bahn"].setdefault(bahn, {"wo": set(), "faelle": set()})
    _QUOTE["fehlende_bahn"][bahn]["wo"].add(da)
    _QUOTE["fehlende_bahn"][bahn]["faelle"].add(kennung.split("[")[0])
    pytest.skip(
        f"die {bahn}-Bahn liegt nicht in dieser Ablage (vorhanden: {da}) — "
        f"mit --nur-bash/--nur-pwsh abgewaehlt. Zurueckholen: install mit "
        f"--update ohne Schalter.")


def kopiere_team_namensraum(ziel):
    """Baut ein PROJEKTfoermiges team/ aus der Ablage, die gerade vorliegt.

    Ersetzt `shutil.copytree(REPO_ROOT / "team", repo / "team")`: Im Kit gibt
    es diesen einen Ordner nicht mehr, seine Teile liegen in drei Ablagen.
    """
    ziel = Path(ziel)
    ziel.mkdir(parents=True, exist_ok=True)
    for name in _BAHN_DATEI:
        quelle = kit_pfad(name)
        if quelle.is_file():
            shutil.copy(quelle, ziel / name)
    for ordner in _GETEILTE_ORDNER:
        quelle = kit_pfad(ordner)
        if quelle.is_dir():
            shutil.copytree(quelle, ziel / ordner, dirs_exist_ok=True)
    return ziel

# --- Zitierung ---------------------------------------------------------------
# Bewusst hier und nicht per shlex: shlex.quote kennt nur POSIX. Beide Shells
# brauchen dieselbe Zusicherung — ein Argument kommt unveraendert an, egal was
# darin steht.


def _zitat_bash(wert):
    return "'" + str(wert).replace("'", "'\\''") + "'"


def _zitat_pwsh(wert):
    return "'" + str(wert).replace("'", "''") + "'"


# --- Schritte ----------------------------------------------------------------
# Jeder Schritt weiss, wie er in beiden Shells ausgesprochen wird. Ein Test
# formuliert nur noch, WAS passieren soll.


class _Schritt:
    def bash(self):
        raise NotImplementedError

    def pwsh(self):
        raise NotImplementedError


class Ruf(_Schritt):
    """Funktionsaufruf, bei dem nur der Erfolg zaehlt (Bash: `return 0/1`).

    Der Exit-Code des Gesamtlaufs ist der des LETZTEN `Ruf`. Das entspricht
    dem Bash-Verhalten und ist der Grund, warum Tests wie bl28 unveraendert
    auf `returncode` pruefen koennen.
    """

    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def bash(self):
        teile = " ".join(_zitat_bash(a) for a in self.args)
        return f"{self.name} {teile}".rstrip() + "\n_team_rc=$?\n"

    def pwsh(self):
        teile = " ".join(_zitat_pwsh(a) for a in self.args)
        return (f"if ({self.name} {teile}) {{ $script:TeamRc = 0 }}"
                f" else {{ $script:TeamRc = 1 }}\n")


class RufMarke(_Schritt):
    """Aufruf, dessen Erfolg als Marke in stdout sichtbar wird.

    Loest das Muster `team_guard_verify marv '…' && echo GUARD_OK` ab. Die
    Marke ist die Assertion-Oberflaeche; sie steht im Test, nicht in der
    Shell.
    """

    def __init__(self, name, *args, marke="MARKE_OK"):
        self.name = name
        self.args = args
        self.marke = marke

    def bash(self):
        teile = " ".join(_zitat_bash(a) for a in self.args)
        return (f"if {self.name} {teile}; then echo {_zitat_bash(self.marke)};"
                f" fi\n_team_rc=0\n")

    def pwsh(self):
        teile = " ".join(_zitat_pwsh(a) for a in self.args)
        return (f"if ({self.name} {teile}) {{ Write-Output "
                f"{_zitat_pwsh(self.marke)} }}\n$script:TeamRc = 0\n")


class RufCode(_Schritt):
    """Aufruf mit ABGESTUFTEM Exit-Code plus Meldung (Vertrag Punkt 5).

    `Ruf` wuerde in PowerShell jeden Fehlschlag auf 1 abbilden und damit
    Soft-Cap (2) und Hard-Cap (3) ununterscheidbar machen — genau die
    Unterscheidung, an der die Budget-Durchsetzung haengt.
    """

    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def bash(self):
        teile = " ".join(_zitat_bash(a) for a in self.args)
        return f"{self.name} {teile}".rstrip() + "\n_team_rc=$?\n"

    def pwsh(self):
        teile = " ".join(_zitat_pwsh(a) for a in self.args)
        return f"$script:TeamRc = [int]({self.name} {teile})\n"


class Ausgabe(_Schritt):
    """Funktionsaufruf, dessen stdout die Nutzlast ist (Vertrag Punkt 2)."""

    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def bash(self):
        teile = " ".join(_zitat_bash(a) for a in self.args)
        return f"{self.name} {teile}".rstrip() + "\n_team_rc=$?\n"

    def pwsh(self):
        teile = " ".join(_zitat_pwsh(a) for a in self.args)
        return f"{self.name} {teile}".rstrip() + "\n$script:TeamRc = 0\n"


class FangUndMelde(_Schritt):
    """Wert einfangen und als kanonische Zeile `rc=<n> wert=[<v>]` melden.

    Fuer den Nachweis, dass eine Funktion unter strikten Optionen leer
    zurueckkommen DARF, ohne den Aufrufer wegzureissen (bl18). Die Zeile ist
    die Assertion-Oberflaeche und in beiden Shells identisch — anders als das
    `k="$(…)"; echo "rc=$? wert=[$k]"`, das sie frueher erzeugte.
    """

    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def bash(self):
        teile = " ".join(_zitat_bash(a) for a in self.args)
        return (f"_wert=\"$({self.name} {teile})\"; _rc=$?\n"
                f"echo \"rc=$_rc wert=[$_wert]\"\n_team_rc=0\n")

    def pwsh(self):
        teile = " ".join(_zitat_pwsh(a) for a in self.args)
        return (f"$wert = ({self.name} {teile}) -join ''\n"
                f"Write-Output \"rc=0 wert=[$wert]\"\n$script:TeamRc = 0\n")


class Variable(_Schritt):
    """Den Wert einer Bibliotheks-Variablen ausgeben — ohne Zeilenumbruch.

    Fuer Zusicherungen ueber abgeleitete Prompt-Bausteine (SMOKE_ZEILE) und
    aufgeloeste Caps.
    """

    def __init__(self, *namen, trenner=" "):
        self.namen = namen
        self.trenner = trenner

    def bash(self):
        muster = self.trenner.join("%s" for _ in self.namen)
        werte = " ".join(f'"${n}"' for n in self.namen)
        return f'printf {_zitat_bash(muster)} {werte}\n_team_rc=0\n'

    def pwsh(self):
        # [Console]::Out.Write statt Write-Host: Write-Host schreibt in den
        # Informationsstrom, nicht auf stdout — die Ausgabe waere je nach
        # Aufrufart da oder nicht. Hier muss sie immer da sein.
        werte = self.trenner.join(f"${n}" for n in self.namen)
        return f'[Console]::Out.Write("{werte}")\n$script:TeamRc = 0\n'


class Schreib(_Schritt):
    """Datei schreiben, Elternordner anlegen — als Schritt IN der Shell.

    Nicht aus Bequemlichkeit: Die Mutation muss zwischen `team_guard_begin`
    und `team_guard_verify` fallen, und die beiden teilen sich einen Prozess
    (siehe Kopf). Fuer alles, was VOR dem Lauf passieren kann, ist Python der
    richtige Ort — dann gehoert es nicht hierher.
    """

    def __init__(self, pfad, inhalt=""):
        self.pfad = str(pfad)
        self.inhalt = inhalt

    def bash(self):
        ordner = os.path.dirname(self.pfad)
        vor = f"mkdir -p {_zitat_bash(ordner)}\n" if ordner else ""
        return (vor + f"printf '%s' {_zitat_bash(self.inhalt)} > "
                      f"{_zitat_bash(self.pfad)}\n_team_rc=0\n")

    def pwsh(self):
        ordner = os.path.dirname(self.pfad)
        vor = (f"New-Item -ItemType Directory -Force -Path "
               f"{_zitat_pwsh(ordner)} | Out-Null\n") if ordner else ""
        return (vor + f"Set-Content -NoNewline -Encoding utf8 -Path "
                      f"{_zitat_pwsh(self.pfad)} -Value "
                      f"{_zitat_pwsh(self.inhalt)}\n$script:TeamRc = 0\n")


class Git(_Schritt):
    """Ein git-Aufruf als Schritt IN der Shell.

    Gebraucht seit BL-114: Der Rollback eines Rollenlaufs muss auch gegen
    einen COMMIT der Rolle geprueft werden, und der muss zwischen
    Schnappschuss und Rollback fallen — beides teilt sich einen Prozess
    (siehe Kopf). Was VOR dem Lauf passieren kann, gehoert weiterhin nach
    Python.
    """

    def __init__(self, *args):
        self.args = args

    def bash(self):
        teile = " ".join(_zitat_bash(a) for a in self.args)
        return f"git {teile} >/dev/null 2>&1\n_team_rc=0\n"

    def pwsh(self):
        teile = " ".join(_zitat_pwsh(a) for a in self.args)
        return f"& git {teile} 2>$null | Out-Null\n$script:TeamRc = 0\n"


class Loeschen(_Schritt):
    """Datei entfernen — der Fall "die Rolle loescht etwas, das ihr nicht
    gehoert". Ohne ihn liesse sich nicht pruefen, dass ein Rollback auch
    WIEDERHERSTELLT und nicht nur wegnimmt."""

    def __init__(self, pfad):
        self.pfad = str(pfad)

    def bash(self):
        return f"rm -f -- {_zitat_bash(self.pfad)}\n_team_rc=0\n"

    def pwsh(self):
        return (f"Remove-Item -LiteralPath {_zitat_pwsh(self.pfad)} -Force "
                f"-ErrorAction SilentlyContinue\n$script:TeamRc = 0\n")


class Ordner(_Schritt):
    """Verzeichnis anlegen — der Fall BL-24 (untracked Ordner als EIN Eintrag)."""

    def __init__(self, pfad):
        self.pfad = str(pfad)

    def bash(self):
        return f"mkdir -p {_zitat_bash(self.pfad)}\n_team_rc=0\n"

    def pwsh(self):
        return (f"New-Item -ItemType Directory -Force -Path "
                f"{_zitat_pwsh(self.pfad)} | Out-Null\n$script:TeamRc = 0\n")


# --- Die Schale --------------------------------------------------------------


class Schale:
    """Eine Shell-Bahn: kennt Dateiendungen, Aufrufform und Konfigformat."""

    def __init__(self, name):
        self.name = name
        self.ist_bash = name == "bash"

    # -- Ablage --------------------------------------------------------------

    @property
    def lib_name(self):
        return "lib.sh" if self.ist_bash else "lib.psm1"

    @property
    def endung(self):
        return ".sh" if self.ist_bash else ".ps1"

    @property
    def kit_lib(self):
        return kit_pfad(self.lib_name)

    def entrypoint(self, rumpf):
        """'ralph' -> 'ralph.sh' bzw. 'ralph.ps1'."""
        return rumpf + self.endung

    @property
    def wechsel_ins_skriptverzeichnis(self):
        """Das Idiom, mit dem ein Entrypoint ins eigene Verzeichnis wechselt.

        Die BL-3-Invariante, auf der ALLE relativen Werkzeugpfade ruhen: Ohne
        sie haengt jede Kostenzahl davon ab, aus welchem Verzeichnis der Mensch
        das Skript gestartet hat, und `kosten.py` meldet still 0.0000 statt zu
        scheitern. Beide Bahnen sichern dasselbe zu, nur anders geschrieben —
        das ist die Idiom-Tabelle aus plans/windows-nativ.md in ihrer
        einfachsten Form.
        """
        return 'cd "$(dirname "$0")"' if self.ist_bash else 'Set-Location $PSScriptRoot'

    def default_muster(self, name):
        """Regex fuer die Zeile, in der die Bibliothek ihren EIGENEN Default setzt.

        Die Idiom-Tabelle in einer Zeile: Beide Bahnen sagen dasselbe, nur
        anders. Ein Test prueft damit dieselbe Zusicherung auf beiden Bahnen,
        statt sich an eine Schreibweise zu binden (Vertrag Punkt 6).
        """
        if self.ist_bash:
            return rf'^{name}="\$\{{{name}:-([^}}]*)\}}"'
        return rf"^\${name} = Team-Default '{name}' '([^']*)'"

    def lib_kopieren(self, ziel_repo):
        """Legt die Bibliothek dieser Bahn in <ziel_repo>/team/ ab."""
        ziel = Path(ziel_repo) / "team"
        ziel.mkdir(parents=True, exist_ok=True)
        shutil.copy(self.kit_lib, ziel / self.lib_name)
        return ziel / self.lib_name

    def config_schreiben(self, ziel_repo, werte, exportiert=("TEAM_DOMAENEN",)):
        """Schreibt team.config.<endung> aus einem Wertebuch.

        Beide Bahnen bekommen ihre Konfiguration aus DERSELBEN Quelle — im
        Betrieb aus den neun Installer-Antworten, hier aus einem dict. Das ist
        der Grund, warum die Konfiguration nicht driften kann: Sie wird
        erzeugt, nicht gepflegt.
        """
        ziel = Path(ziel_repo) / ("team.config" + self.endung)
        zeilen = []
        for name, wert in werte.items():
            if self.ist_bash:
                zeilen.append(f'{name}="{wert}"')
                if name in exportiert:
                    zeilen.append(f"export {name}")
            else:
                zeilen.append(f'${name} = "{wert}"')
                if name in exportiert:
                    zeilen.append(f'$env:{name} = "{wert}"')
        # BL-113: dieselbe Kodierungsregel wie in beiden Installern — die
        # Testbahn soll erzeugen, was im Feld erzeugt wird, nicht etwas
        # Aehnliches. Unter pwsh 7 macht es keinen Unterschied; unter Windows
        # PowerShell 5.1 entscheidet es darueber, ob die Datei ueberhaupt
        # parst.
        ziel.write_text("\n".join(zeilen) + "\n",
                        encoding="utf-8" if self.ist_bash else "utf-8-sig")
        return ziel

    def claude_stub(self, ordner, ausgabe):
        """Ein `claude`, das eine feste Antwort liefert — ohne Netz und Kosten.

        Unter Windows muss der Stub ein `.cmd` sein: `claude` ist dort selbst
        ein Shim, kein Programm. `chmod` entfaellt dabei ersatzlos.
        """
        ordner = Path(ordner)
        ordner.mkdir(parents=True, exist_ok=True)
        if self.ist_bash:
            stub = ordner / "claude"
            stub.write_text("#!/usr/bin/env bash\ncat <<'TEAMJSON'\n"
                            + ausgabe + "\nTEAMJSON\n", encoding="utf-8")
            stub.chmod(0o755)
        else:
            stub = ordner / "claude.cmd"
            zeilen = ["@echo off"] + [
                "echo " + z.replace("^", "^^").replace("&", "^&")
                          .replace("<", "^<").replace(">", "^>")
                          .replace("|", "^|")
                for z in ausgabe.splitlines()
            ]
            stub.write_text("\r\n".join(zeilen) + "\r\n", encoding="utf-8")
        return stub

    # -- Ausfuehrung ---------------------------------------------------------

    def lauf(self, schritte, cwd, lib=None, env=None, strikt=False):
        """Rendert die Schritte in EIN Skript und fuehrt es aus.

        `strikt` hat DREI Stufen, nicht zwei:

            False       keine Optionen
            "abbruch"   bash `set -e`  /  pwsh $ErrorActionPreference='Stop'
            True|"voll" bash `set -euo pipefail`  /  pwsh zusaetzlich
                        Set-StrictMode -Version Latest

        Warum die mittlere Stufe existiert: Sie ist nicht Bequemlichkeit,
        sondern eine Messstelle. Sie entstand an `team_architekt_kaskade`,
        deren Absicherung (`| head -1`) gegen `set -e` trug, aber NICHT gegen
        `set -o pipefail` — dort schlaegt der leere `grep` durch und reisst
        den Aufrufer weg. Der Test nannte deshalb die Stufe, fuer die die
        Zusicherung wirklich galt, statt eine breitere zu behaupten: Sonst
        prueft er etwas anderes als das Zugesicherte, und der Befund
        verschwindet in einem roten Test, den jemand "anpasst".

        Seit BL-111 ist genau dieser Fall gefixt (`{ … ; } || true` in
        team_architekt_kaskade, team_ralph_cap, team_budget_empfehlung), und
        der zugehoerige Test faehrt `strikt=True`. Die mittlere Stufe bleibt
        trotzdem: Sie ist die Sprache, in der eine Zusicherung ihre Reichweite
        nennen kann — und der naechste Fund dieser Bauart braucht sie wieder.

        Nebenbei mit BL-111 berichtigt: Hier stand, `team-status.sh` setze
        "keine strikten Optionen". Sie setzt `set -uo pipefail`, und zwar seit
        2026-08-01. Latent war der Fall allein wegen des fehlenden `-e`.
        """
        if isinstance(schritte, _Schritt):
            schritte = [schritte]
        lib = Path(lib) if lib else self.kit_lib
        umgebung = basis_umgebung(**(env or {}))
        voll = strikt is True or strikt == "voll"

        if self.ist_bash:
            kopf = "set -euo pipefail\n" if voll else (
                "set -e\n" if strikt else "")
            skript = (kopf + f"source {_zitat_bash(lib)}\n_team_rc=0\n"
                      + "".join(s.bash() for s in schritte)
                      + "exit $_team_rc\n")
            befehl = [BASH or "bash", "-c", skript]
        else:
            kopf = ""
            if strikt:
                kopf = "$ErrorActionPreference = 'Stop'\n"
            if voll:
                kopf += "Set-StrictMode -Version Latest\n"
            # -DisableNameChecking: Die Bibliothek fuehrt die Funktionsnamen der
            # Bash-Bahn weiter (team_guard_verify statt Verify-TeamGuard).
            # PowerShell warnt darueber bei JEDEM Import. Die Namensgleichheit
            # ist Absicht — sie ist es, was EINE Testsuite fuer beide Bahnen
            # ueberhaupt moeglich macht; also wird die Warnung abgestellt und
            # nicht der Name geaendert.
            skript = (kopf + f"Import-Module {_zitat_pwsh(lib)} -Force -DisableNameChecking\n"
                      + "$script:TeamRc = 0\n"
                      + "".join(s.pwsh() for s in schritte)
                      + "exit $script:TeamRc\n")
            befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-Command", skript]

        return subprocess.run(befehl, cwd=str(cwd), env=umgebung,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")


# --- Verfuegbarkeit ----------------------------------------------------------


def _fehlt_oder_abgewaehlt(bahn, datei):
    """Warum eine fehlende Bibliothek ZWEI verschiedene Lagen sein kann.

    BL-129: Der Grund stand vorher als "team/lib.sh fehlt in dieser Ablage" —
    ein Satz, der nach Defekt klingt. In einem mit `--nur-pwsh` installierten
    Projekt ist er aber die WAHRHEIT ueber eine bewusste Abwahl des Anwenders
    (BL-119), und die ist kein Fehler. Wer den Unterschied nicht liest, sucht
    nach einer kaputten Installation, die es nicht gibt.

    Unterschieden wird an der ANDEREN Bahn: Liegt sie da, war es eine Abwahl.
    Liegt keine von beiden, ist die Ablage wirklich unvollstaendig — dann soll
    der Satz auch so klingen.
    """
    andere = {"bash": "pwsh", "pwsh": "bash"}[bahn]
    if andere in bahnen_in_der_ablage():
        # Kurz genug fuer die Zusammenfassungszeile: Sie steht neben einer Zahl
        # und wird ueberflogen, nicht studiert. Der Rueckweg gehoert trotzdem
        # hinein — ohne ihn liest sich die Abwahl wie eine Sackgasse.
        return (f"in dieser Ablage abgewaehlt (--nur-{andere}) — "
                f"--update ohne Schalter holt sie zurueck")
    return f"{datei} fehlt in dieser Ablage"


def _bash_bereit():
    """Warum das eine eigene Frage ist: Auf einem POSIX-Wirt ist sie immer mit
    Ja beantwortet, unter nativem Windows nicht zwingend.

    Die Bash-Bahn ist laut README die Bahn fuer Linux und WSL; nativ Windows
    faehrt pwsh. Sie laesst sich unter Windows trotzdem fahren, wenn Git for
    Windows liegt — und das tut es dort meistens, weil das Kit git ohnehin
    braucht. Fehlt sie, wird UEBERSPRUNGEN und nicht rot: Ein WSL-Stub, der
    UTF-16-Muell liefert, beweist nichts ueber das Kit, und 110 rote Tests
    verdecken den einen echten Befund, der darunter liegen koennte.
    """
    if BASH is None:
        return False, ("keine echte bash gefunden (der `bash` im PATH ist "
                       "unter Windows der WSL-Launcher aus System32 und wird "
                       "bewusst nicht benutzt) — Git for Windows installieren "
                       "oder die Suite in einer WSL-Distro fahren")
    if not kit_pfad("lib.sh").is_file():
        return False, _fehlt_oder_abgewaehlt("bash", "team/lib.sh")
    return True, ""


def _pwsh_bereit():
    """Warum zwei Bedingungen: `pwsh` kann da sein, bevor es lib.psm1 gibt.

    Stufe 1 baut den Harnisch, Stufe 3 die Bibliothek. In der Zwischenzeit
    soll die pwsh-Bahn UEBERSPRUNGEN werden und nicht rot sein — sonst waere
    der Linux-Betrieb ab Stufe 1 kaputt, und genau das darf nicht passieren.
    """
    if shutil.which("pwsh") is None:
        return False, "pwsh nicht installiert"
    if not kit_pfad("lib.psm1").is_file():
        return False, _fehlt_oder_abgewaehlt("pwsh", "team/lib.psm1")
    return True, ""


# --- Fixtures und Bericht ----------------------------------------------------

_QUOTE = {"beide": set(), "nur_bash": set(), "uebersprungen": set(),
          "einbahnig": set(), "ohne_bash": set(), "fehlende_bahn": {}}


@pytest.fixture(params=["bash", "pwsh"])
def schale(request):
    """Die parametrisierte Bahn. Ein Test, der sie nimmt, laeuft doppelt."""
    kennung = request.node.nodeid.split("[")[0]
    if request.param == "pwsh":
        bereit, grund = _pwsh_bereit()
        if not bereit:
            _QUOTE["uebersprungen"].add(kennung)
            pytest.skip(f"pwsh-Bahn nicht verfuegbar: {grund}")
    else:
        bereit, grund = _bash_bereit()
        if not bereit:
            _QUOTE["ohne_bash"].add(kennung)
            pytest.skip(f"bash-Bahn nicht verfuegbar: {grund}")
    _QUOTE["beide"].add(kennung)
    return Schale(request.param)


@pytest.fixture
def bash_schale():
    """Fuer Tests, die (noch) an Bash gebunden sind — ausdruecklich gezaehlt."""
    verlange_bash()
    return Schale("bash")


def verlange_pwsh():
    """Skip mit Begruendung, wenn auf diesem Wirt kein PowerShell 7 liegt.

    Das Gegenstueck zu verlange_bash(), fuer Tests, die ausserhalb der
    `schale`-Fixture selbst ein pwsh starten. Es gab es bisher nicht, weil die
    pwsh-Bahn ihre Faelle ueber die parametrisierte Fixture fuhr — ein Test,
    der NUR pwsh braucht (BL-142: ein Fehler, den es auf der bash-Bahn gar
    nicht geben kann), hatte keinen Uebersprung mit Grund.
    """
    bereit, grund = _pwsh_bereit()
    if not bereit:
        _QUOTE["uebersprungen"].add("nur-pwsh")
        pytest.skip(f"pwsh-Bahn nicht verfuegbar: {grund}")


def verlange_bash():
    """Skip mit Begruendung, wenn auf diesem Wirt keine echte Bash liegt.

    Fuer die Tests, die ausserhalb der `schale`-Fixture selbst eine Bash
    starten (Entrypoints, `bash -c`-Sonden). Ohne sie faellt dort WinError 193
    oder UTF-16-Muell an, und beides liest sich wie ein Kit-Defekt.
    """
    bereit, grund = _bash_bereit()
    if not bereit:
        pytest.skip(f"bash-Bahn nicht verfuegbar: {grund}")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "nur_bash(grund): Test laeuft bewusst nur auf der Bash-Bahn. Der Grund "
        "gehoert in den Marker und der Punkt in den Backlog.",
    )


# Die Symbole, deren blosser Import "dieser Test startet eine Bash" bedeutet.
# `BASH` ist dann None und `entrypoint_aufruf` liefert einen Vektor, dessen
# erstes Element es nicht gibt — beides endet in einem TypeError bzw.
# FileNotFoundError mitten im Testkoerper. Das liest sich wie ein Kit-Defekt
# und ist eine Aussage ueber den Wirt.
_BRAUCHT_BASH = ("BASH", "entrypoint_aufruf")


def pytest_collection_modifyitems(items):
    bash_bereit, bash_grund = _bash_bereit()
    for item in items:
        if item.get_closest_marker("nur_bash"):
            _QUOTE["nur_bash"].add(item.nodeid.split("[")[0])
        if bash_bereit:
            continue
        modul = getattr(item, "module", None)
        if modul is None:
            continue
        # hasattr statt getattr(...) is None: Ein Modul, das das Symbol gar
        # nicht importiert hat, soll nicht mitgeschleift werden.
        if any(hasattr(modul, name) for name in _BRAUCHT_BASH):
            _QUOTE["ohne_bash"].add(item.nodeid.split("[")[0])
            item.add_marker(pytest.mark.skip(
                reason=f"bash-Bahn nicht verfuegbar: {bash_grund}"))


def pytest_terminal_summary(terminalreporter):
    """Die Doppelbahn-Quote — sichtbar in jedem Lauf, nicht auf Nachfrage."""
    beide = len(_QUOTE["beide"] - _QUOTE["uebersprungen"])
    offen = len(_QUOTE["uebersprungen"])
    markiert = len(_QUOTE["nur_bash"])
    if not (beide or offen or markiert):
        return
    terminalreporter.write_sep("-", "Doppelbahn")
    terminalreporter.write_line(f"  auf beiden Bahnen gelaufen : {beide}")
    if offen:
        terminalreporter.write_line(
            f"  pwsh-Bahn uebersprungen    : {offen}  "
            f"({_pwsh_bereit()[1]})")
    if markiert:
        terminalreporter.write_line(
            f"  bewusst nur bash           : {markiert}  "
            f"(jede Markierung gehoert in den Backlog)")
    if _QUOTE["ohne_bash"]:
        terminalreporter.write_line(
            f"  bash-Bahn uebersprungen    : {len(_QUOTE['ohne_bash'])}  "
            f"({_bash_bereit()[1]})")
    for bahn, stand in sorted(_QUOTE["fehlende_bahn"].items()):
        terminalreporter.write_line(
            f"  {bahn}-Bahn nicht installiert: {len(stand['faelle'])}  "
            f"(vorhanden: {', '.join(sorted(stand['wo']))} — "
            f"--update ohne Schalter holt sie zurueck)")
    if _QUOTE["einbahnig"]:
        terminalreporter.write_line(
            f"  einbahnige Ablage          : nur "
            f"{', '.join(sorted(_QUOTE['einbahnig']))} installiert — die "
            f"andere Bahn ist abgewaehlt")
        terminalreporter.write_line(
            "                               (--update ohne Schalter holt sie "
            "zurueck)")


def schreibschutz_loesen(wurzel):
    """Nimmt unterhalb von `wurzel` jeder Datei den Schreibschutz.

    BL-138. Die Kit-Tests legen echte Git-Repos in `tmp_path` an. Git schreibt
    lose Objekte SCHREIBGESCHUETZT — nachgemessen an einem liegengebliebenen
    Lauf: 989 von 5622 Dateien, ausnahmslos unter `.git/objects`. Das ist kein
    Versehen, sondern Absicht: Ein Objekt ist unveraenderlich.

    Und genau hier laufen die Plattformen auseinander:

        POSIX    unlink() prueft das Schreibrecht am VERZEICHNIS.
                 Der Modus der Datei selbst ist gleichgueltig — es geht.
        Windows  DeleteFile scheitert mit ERROR_ACCESS_DENIED (5), sobald
                 FILE_ATTRIBUTE_READONLY gesetzt ist.

    pytest hebt die letzten drei Laufordner auf und raeumt am Sitzungsende die
    aelteren weg. Unter Windows scheitert dieses Aufraeumen an jedem einzelnen
    Git-Objekt. pytest faengt das ab und versucht es erneut — chmod plus
    Retry, EINZELN fuer jede der 989 Dateien. Auf NTFS dauert das minutenlang.

    Das Fehlerbild im Feld war entsprechend irrefuehrend: Ein Lauf meldete
    542 Faelle, 228 bestanden, 314 uebersprungen, KEINEN Fehlschlag — und
    danach eine Wand aus Traceback, endend in `PermissionError: [WinError 5]`.
    Wer da abbricht (der Anwender tat es), sieht einen gruenen Lauf als roten.
    Wer nicht abbricht, wartet. Beides falsch, und beides erst auf Windows.

    Deshalb steht das Aufraeumen hier und nicht in einem einzelnen Test: Es
    ist eine Eigenschaft des PRUEFSTANDS, dass sein Wegwerfbereich wegwerfbar
    bleiben muss. Dieselbe Ueberlegung wie in BL-130.

    Fehler werden geschluckt: Diese Funktion laeuft NACH dem letzten Test.
    Sie darf ein Ergebnis aufraeumen, aber niemals eines erzeugen.
    """
    if not IST_WINDOWS:
        return 0
    geaendert = 0
    for pfad in wurzel.rglob("*"):
        try:
            if not pfad.is_file():
                continue
            modus = pfad.stat().st_mode
            if modus & stat.S_IWRITE:
                continue
            os.chmod(pfad, modus | stat.S_IWRITE)
            geaendert += 1
        except OSError:
            pass
    return geaendert


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session):
    """Den Wegwerfbereich dieser Sitzung wegwerfbar hinterlassen (BL-138).

    `tryfirst`, weil `_pytest.tmpdir` im selben Hook aufraeumt: Der
    Schreibschutz muss weg sein, BEVOR dort jemand loeschen will.

    Angefasst wird nur der Bereich DIESER Sitzung, und nur, wenn er ueberhaupt
    entstanden ist — `_basetemp` statt `getbasetemp()`, denn Letzteres legt
    den Ordner an. Ein Lauf, in dem kein Test `tmp_path` gebraucht hat, soll
    keinen hinterlassen.

    Aeltere Ordner bleiben unberuehrt. Sie aufzuraeumen ist pytests Aufgabe,
    und nach dieser Fassung kann pytest das auch: Was diese Sitzung anlegt,
    ist in drei Sitzungen loeschbar.
    """
    fabrik = getattr(session.config, "_tmp_path_factory", None)
    basis = getattr(fabrik, "_basetemp", None)
    if basis is None:
        return
    schreibschutz_loesen(basis)

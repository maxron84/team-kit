"""Die Doppelbahn: eine Testsuite, zwei Shells (bash und pwsh).

WARUM ES DIESE DATEI GIBT
    Das Kit bekommt einen nativen Windows-Zweig in PowerShell, waehrend Bash
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
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

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
        return REPO_ROOT / "team" / self.lib_name

    def entrypoint(self, rumpf):
        """'ralph' -> 'ralph.sh' bzw. 'ralph.ps1'."""
        return rumpf + self.endung

    def default_muster(self, name):
        """Regex fuer die Zeile, in der die Bibliothek ihren EIGENEN Default setzt.

        Die Idiom-Tabelle in einer Zeile: Beide Zweige sagen dasselbe, nur
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

        Beide Zweige bekommen ihre Konfiguration aus DERSELBEN Quelle — im
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
        ziel.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
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
        sondern eine Messstelle. `team_architekt_kaskade` haelt seinen
        Rueckgabewert mit `| head -1` auf 0 — der Kommentar in lib.sh nennt
        ausdruecklich `set -e` als den Fall, den das abdeckt. Unter
        `set -o pipefail` traegt die Absicherung NICHT: Der leere `grep`
        schlaegt durch, und der Aufrufer wird weggerissen. Heute latent
        (einziger Aufrufer ist team-status.sh, und die setzt keine strikten
        Optionen), aber alle Rollen laufen mit `set -euo pipefail`.

        Ein Test, der die dokumentierte Zusicherung prueft, muss deshalb die
        Stufe nennen, fuer die sie behauptet wird — sonst prueft er etwas
        anderes als das, was zugesichert ist, und der Befund verschwindet in
        einem roten Test, den jemand "anpasst".
        """
        if isinstance(schritte, _Schritt):
            schritte = [schritte]
        lib = Path(lib) if lib else self.kit_lib
        umgebung = {"HOME": str(Path.home()),
                    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}
        umgebung.update(env or {})
        voll = strikt is True or strikt == "voll"

        if self.ist_bash:
            kopf = "set -euo pipefail\n" if voll else (
                "set -e\n" if strikt else "")
            skript = (kopf + f"source {_zitat_bash(lib)}\n_team_rc=0\n"
                      + "".join(s.bash() for s in schritte)
                      + "exit $_team_rc\n")
            befehl = ["bash", "-c", skript]
        else:
            kopf = ""
            if strikt:
                kopf = "$ErrorActionPreference = 'Stop'\n"
            if voll:
                kopf += "Set-StrictMode -Version Latest\n"
            # -DisableNameChecking: Die Bibliothek fuehrt die Funktionsnamen des
            # Bash-Zweigs weiter (team_guard_verify statt Verify-TeamGuard).
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
                              capture_output=True, text=True)


# --- Verfuegbarkeit ----------------------------------------------------------


def _pwsh_bereit():
    """Warum zwei Bedingungen: `pwsh` kann da sein, bevor es lib.psm1 gibt.

    Stufe 1 baut den Harnisch, Stufe 3 die Bibliothek. In der Zwischenzeit
    soll die pwsh-Bahn UEBERSPRUNGEN werden und nicht rot sein — sonst waere
    der Linux-Betrieb ab Stufe 1 kaputt, und genau das darf nicht passieren.
    """
    if shutil.which("pwsh") is None:
        return False, "pwsh nicht installiert"
    if not (REPO_ROOT / "team" / "lib.psm1").is_file():
        return False, "team/lib.psm1 fehlt noch (Stufe 3)"
    return True, ""


# --- Fixtures und Bericht ----------------------------------------------------

_QUOTE = {"beide": set(), "nur_bash": set(), "uebersprungen": set()}


@pytest.fixture(params=["bash", "pwsh"])
def schale(request):
    """Die parametrisierte Bahn. Ein Test, der sie nimmt, laeuft doppelt."""
    kennung = request.node.nodeid.split("[")[0]
    if request.param == "pwsh":
        bereit, grund = _pwsh_bereit()
        if not bereit:
            _QUOTE["uebersprungen"].add(kennung)
            pytest.skip(f"pwsh-Bahn nicht verfuegbar: {grund}")
    _QUOTE["beide"].add(kennung)
    return Schale(request.param)


@pytest.fixture
def bash_schale():
    """Fuer Tests, die (noch) an Bash gebunden sind — ausdruecklich gezaehlt."""
    return Schale("bash")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "nur_bash(grund): Test laeuft bewusst nur auf der Bash-Bahn. Der Grund "
        "gehoert in den Marker und der Punkt in den Backlog.",
    )


def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_closest_marker("nur_bash"):
            _QUOTE["nur_bash"].add(item.nodeid.split("[")[0])


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

#!/usr/bin/env python3
"""BL-173 und BL-174 — zwei Fehler in `team_claude()`, die beide erst nach
Stunden Laufzeit auffallen.

BL-173: DIE CLI ALS BLANKER KOMMANDONAME — UND EINE DIAGNOSE, DIE IN DIE IRRE
FÜHRT
    `lib.sh` rief schlicht `claude -p …` auf. Es gab dafür **keine**
    Konfigurationsvariable. Das Kit hatte diese Lehre für Python längst
    gezogen (`BL-131`: „Wie der Interpreter **heißt**, entscheidet die
    Maschine, nicht diese Datei") und für die CLI nicht angewandt — dabei
    wiegt sie hier schwerer: Claude Code wird legitim **IDE-gebündelt**
    ausgeliefert, und eine Maschine kann eine vollständig eingerichtete,
    **angemeldete** Installation haben, ohne dass `claude` in irgendeinem
    `PATH` auflösbar ist. Genau diese Lage lag im Feld vor.

    **Die zweite Hälfte wiegt schwerer, weil sie in die Irre führt.** Der
    Ablauf war: `claude: command not found` (eine Zeile, scrollt vorbei) → ein
    0-Byte-Log → `team_bewerte_ergebnis` schreibt einen **Ersatzzettel** für
    einen Aufruf, der nie stattgefunden hat → der Abo-Fehler löst planmäßig
    den **API-Fallback** aus → und der bricht mit der Meldung ab, die stehen
    bleibt und die der Mensch liest: *„FEHLER: AUTH_MODE=api, aber weder
    ANTHROPIC_API_KEY gesetzt noch …/api-key lesbar."*

    **Diagnostiziert wird ein Auth-Problem; vorliegt ein PATH-Problem.** Wer
    dieser Meldung folgt, besorgt einen API-Schlüssel — und scheitert ein
    zweites Mal an derselben Stelle, weil auch der API-Weg dasselbe `claude`
    aufruft. Eine fehlende Programmdatei ist **keine** Fehlerklasse, die ein
    Auth-Fallback heilen kann.

BL-174: DER PAUSEN-EXIT 42 WAR IN EINER ABO-INSTALLATION UNERREICHBAR
    Der Fallback lautete `team_resolve_auth_mode || return 1`. Für
    `AUTH_MODE=api` ohne Schlüssel gibt die Funktion 1 zurück — das
    `|| return 1` verließ `team_claude` also **sofort**, und die gesamte
    429-Sonderbehandlung darunter wurde nie erreicht.

    Ein Session-Limit — die Klasse, für die `BL-20`/`BL-25` eigens den Exit
    `42` eingeführt haben — kam damit als **Exit 1** heraus: „ECHTER Fehler,
    Mensch gefragt". Kein Warten bis zum Reset, kein Pausen-Signal, keine der
    drei dokumentierten Zusicherungen.

    **Getroffen wird der empfohlene Normalfall.** Seit dem Entscheid „keine
    Rolle ist fest `api`" ist eine Installation ganz ohne API-Schlüssel eine
    voll unterstützte Lage. Genau dort war der Airbag ausgebaut, und zwar
    unsichtbar: Der Fehler zeigt sich erst, wenn das Kontingent voll ist — an
    der teuersten Stelle.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (BASH, kit_pfad, nur_code,  # noqa: E402
                      ueberspringe_ohne_bahn, verlange_pwsh)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _lies(*teile):
    p = REPO_ROOT.joinpath(*teile)
    if not p.is_file():
        pytest.skip(f"{p.name} liegt in dieser Ablage nicht")
    return p.read_text(encoding="utf-8-sig")


# --- BL-173, Teil 1: der Override existiert auf beiden Bahnen ----------------


@pytest.mark.parametrize("datei", ["bash/entry/team.config.sh",
                                   "pwsh/entry/team.config.ps1"])
def test_beide_konfigurationen_kennen_die_cli_variable(datei):
    """Dieselbe Bauart wie `TEAM_PYTHON` — und aus demselben Grund."""
    assert "TEAM_CLAUDE_BIN" in _lies(*datei.split("/")), (
        f"BL-173: {datei} kennt TEAM_CLAUDE_BIN nicht. Dann laeuft das Team "
        "auf einer Maschine mit IDE-gebuendelter CLI gar nicht an, ohne dass "
        "jemand am PATH dreht.")


@pytest.mark.parametrize("datei", ["bash/lib.sh", "pwsh/lib.psm1"])
def test_keine_bahn_ruft_die_cli_mehr_blank_auf(datei):
    """Der Riegel gegen den Rückbau."""
    ohne_kommentar = "\n".join(
        z for z in _lies(*datei.split("/")).splitlines()
        if not z.lstrip().startswith("#"))
    assert "TEAM_CLAUDE_BIN" in ohne_kommentar, (
        f"{datei} benutzt TEAM_CLAUDE_BIN nicht.")
    assert "claude -p " not in ohne_kommentar, (
        f"BL-173: {datei} ruft die CLI wieder als blanken Kommandonamen auf.")


# --- BL-173, Teil 1b: der Installer FÜLLT den Wert ---------------------------
#
# Die erste Hälfte des Eintrags verlangt mehr als die Variable: Sie soll „vom
# Installer mit dem gefüllt [werden], was er auf dieser Maschine wirklich
# gefunden hat — und die Suche kennt dann auch den IDE-Ort." Eine Variable, die
# überall auf `claude` steht, hilft der IDE-Maschine nicht; sie verlangt
# weiterhin, dass jemand von Hand nachträgt. Genau das ist die Bauart von
# `BL-131` für Python, und der Riegel hier ist derselbe.

# Die Marke wird ZUSAMMENGESETZT und nicht hingeschrieben. Grund: Schritt 3
# von `kit-test.sh` durchsucht die INSTALLIERTE Ablage nach ungefuellten
# Platzhaltern und meldet jede Datei, in der einer steht — auch eine
# Testdatei, die ihn nur ZITIERT. Dieselbe Loesung aus demselben Grund in
# test_bl163_gleicher_platzhalter_gleicher_wert.py.
MARKE = "".join(("{{", "CLAUDE_BIN", "}}"))


# Kommentare raus, bevor geprüft wird — sonst hält die **Begründung** den Test
# grün, während der Code fehlt. Beim ersten Entwurf dieser Datei genau so
# passiert: Der Platzhalter stand noch im Kommentar, die Zuweisung war weg, und
# die Gegenprobe blieb grün. Der Handgriff steht in `conftest.py`, weil er zur
# Gattung gehört und nicht zu dieser Stelle (`BL-154`) — beim Bauen von
# `BL-189` ist dieselbe Falle ein zweites Mal zugeschnappt, in die andere
# Richtung.


@pytest.mark.parametrize("datei", ["bash/entry/team.config.sh",
                                   "pwsh/entry/team.config.ps1"])
def test_beide_konfigurationen_tragen_den_platzhalter(datei):
    """Ein fester Vorgabewert wäre wieder die Annahme, die `BL-131` verworfen
    hat: dass diese Datei weiß, wie das Programm auf der Zielmaschine heißt."""
    text = _lies(*datei.split("/"))
    assert MARKE in text, (
        f"BL-173: {datei} traegt keinen {MARKE}-Platzhalter — dann steht dort "
        "wieder ein fester Name, und der Installer kann nicht eintragen, was "
        "er gefunden hat.")
    zeile = [z for z in text.splitlines()
             if "TEAM_CLAUDE_BIN" in z and not z.lstrip().startswith("#")]
    assert zeile and MARKE in zeile[0], (
        f"BL-173: {datei} fuellt den Platzhalter nicht in TEAM_CLAUDE_BIN — "
        f"er steht woanders. Gefunden: {zeile!r}")


@pytest.mark.parametrize("datei", ["bash/install.sh", "pwsh/install.ps1"])
def test_beide_installer_fuellen_den_platzhalter(datei):
    """Beide Installer schreiben **beide** Konfigurationen. Füllt einer den
    Platzhalter nicht, bleibt er in der Datei stehen — und `TEAM_CLAUDE_BIN`
    ist dann buchstäblich die Marke selbst."""
    assert MARKE in nur_code(_lies(*datei.split("/"))), (
        f"BL-173: {datei} fuellt {MARKE} nicht (im CODE, nicht im Kommentar). "
        "Der von diesem Installer geschriebene Baum traegt dann einen "
        "ungefuellten Platzhalter.")


@pytest.mark.parametrize("datei", ["bash/install.sh", "pwsh/install.ps1"])
def test_beide_installer_suchen_auch_den_ide_ort(datei):
    """Der Kern des Feldfalls: Die CLI **war** da, angemeldet, lauffähig — nur
    nicht im `PATH`. Ein Installer, der ausschließlich den `PATH` befragt,
    trägt auf genau dieser Maschine `claude` ein und ändert nichts."""
    text = nur_code(_lies(*datei.split("/")))
    assert "native-binary" in text, (
        f"BL-173: {datei} sucht die CLI nicht am IDE-Ort "
        "(<erweiterung>/resources/native-binary/). Damit findet er sie genau "
        "in der Lage nicht, in der der Eintrag entstanden ist.")
    assert ".vscode" in text, (
        f"BL-173: {datei} kennt kein Erweiterungsverzeichnis, in dem eine "
        "IDE-gebuendelte CLI liegen koennte.")


# --- BL-173, Teil 2: die Fehlerklasse, end-to-end ----------------------------

STUB_LIB = """
team_lock() { return 0; }
"""


def _bash_team_claude(tmp_path, *, pfad_leer, key=None, ergebnis=None):
    """Faehrt `team_claude` aus der ECHTEN lib.sh in einer gestellten Lage.

    `pfad_leer` heisst: kein `claude` auffindbar — die Lage aus dem Feld.
    """
    if not BASH:
        pytest.skip("keine bash auf diesem Wirt")
    lib = kit_pfad("lib.sh")
    if not lib.is_file():
        pytest.skip("lib.sh liegt in dieser Ablage nicht")

    heim = tmp_path / "heim"
    (heim / ".config" / "claude-team").mkdir(parents=True)
    if key:
        (heim / ".config" / "claude-team" / "api-key").write_text(
            key + "\n", encoding="utf-8", newline="\n")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    # Die CLI wird AUSDRUECKLICH benannt statt ueber den PATH gesucht.
    #
    # Der erste Entwurf stellte die Lage "keine CLI" ueber einen leeren PATH
    # her — und war damit vom WIRT abhaengig: Diese Maschine hat ein echtes
    # `claude` im PATH, der Fall war also gar keiner, und der Test lief in den
    # echten Aufruf. Ein gestellter Name, den es sicher nicht gibt, prueft
    # dieselbe Weiche und haengt an nichts.
    if pfad_leer:
        cli = "claude-gibt-es-auf-dieser-maschine-nicht"
    else:
        stub = bin_dir / "claude-stub"
        stub.write_text(
            "#!/bin/sh\n"
            f"cat <<'JSON'\n{json.dumps(ergebnis)}\nJSON\n",
            encoding="utf-8", newline="\n")
        stub.chmod(0o755)
        cli = str(stub)

    skript = tmp_path / "probe.sh"
    skript.write_text(
        f'source "{lib.as_posix()}" 2>/dev/null\n'
        'team_claude probe sonnet "$1" "prompt"\n'
        'echo "EXIT=$?"\n', encoding="utf-8", newline="\n")

    return _lauf(skript, tmp_path, heim, bin_dir, TEAM_CLAUDE_BIN=cli)


def _lauf(skript, tmp_path, heim, bin_dir, **zusatz):
    """Startet die Sonde — von der ECHTEN Umgebung aus, nicht von einer leeren.

    Zwei Dinge, die beim ersten Entwurf je einen Aufhaenger gekostet haben:

    1. NICHT von einer Minimal-Umgebung ausgehen. `lib.sh` braucht die
       MSYS-Werkzeuge (`date`, `tr`, `head`); ein PATH, der nur den Stub-Ordner
       enthaelt, laesst sie ins Leere laufen. Der Stub-Ordner kommt deshalb
       VORNE dazu, statt den Rest zu ersetzen.
    2. `stdin=DEVNULL`. Sonst erbt die Sonde das Terminal von pytest, und eine
       Rueckfrage im Kit blockiert den Lauf bis zum Timeout — derselbe Griff,
       den die BL-153-Tests fuer `senden` schon benutzen.
    """
    umgebung = dict(os.environ)
    umgebung.pop("ANTHROPIC_API_KEY", None)
    umgebung.pop("TEAM_CLAUDE_BIN", None)
    umgebung.update({
        "HOME": str(heim), "USERPROFILE": str(heim),
        "PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", ""),
        "TEAM_PYTHON": os.environ.get("TEAM_PYTHON", sys.executable),
        "TEAM_AUTH_USER": "abo", "AUTH_MODE": "abo",
        # Kein Warten im Test: Die 429-Behandlung soll ERREICHT werden, sie
        # soll nicht schlafen.
        "TEAM_429_MAX_WARTEN": "0", "TEAM_429_MAX_RETRIES": "0",
    })
    umgebung.update(zusatz)
    return subprocess.run(
        [BASH, str(skript), str(tmp_path / "out.json")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=umgebung, stdin=subprocess.DEVNULL, timeout=120)


def test_ohne_cli_nennt_die_meldung_den_wahren_grund(tmp_path):
    """DIE Gegenprobe, die BL-173 verlangt: genau EINE Meldung — „CLI nicht
    gefunden" — und **keine** über einen fehlenden API-Schlüssel."""
    ueberspringe_ohne_bahn("bash")
    r = _bash_team_claude(tmp_path, pfad_leer=True)
    aus = r.stdout + r.stderr
    assert "nicht auffindbar" in aus or "nicht gefunden" in aus, (
        f"Die CLI-Meldung fehlt:\n{aus}")
    assert "ANTHROPIC_API_KEY" not in aus, (
        "BL-173: Gemeldet wird weiterhin ein Auth-Problem, obwohl ein "
        f"PATH-Problem vorliegt. Wer dem folgt, besorgt einen Schluessel und "
        f"scheitert ein zweites Mal an derselben Stelle.\n{aus}")


def test_ohne_cli_entsteht_kein_ersatzzettel(tmp_path):
    """Ein Ersatzzettel für einen Aufruf, der nie stattgefunden hat, ist eine
    Messung über nichts — und er verdeckt, dass gar nichts lief."""
    ueberspringe_ohne_bahn("bash")
    r = _bash_team_claude(tmp_path, pfad_leer=True)
    assert "Dauer ist belegt" not in (r.stdout + r.stderr), (
        f"Es wurde ein Ersatzzettel geschrieben:\n{r.stdout}{r.stderr}")
    assert not (tmp_path / "out.json").exists() or \
        (tmp_path / "out.json").stat().st_size == 0, (
        "Fuer einen nie stattgefundenen Aufruf liegt ein Ergebnis-Log vor.")


def test_ein_voller_pfad_ausserhalb_des_PATH_laeuft_durch(tmp_path):
    """Die zweite Gegenprobe aus dem Eintrag: Mit gesetztem `TEAM_CLAUDE_BIN`
    auf einen Pfad außerhalb des `PATH` muss der Lauf normal durchlaufen —
    das ist die Lage der IDE-gebündelten Installation."""
    ueberspringe_ohne_bahn("bash")
    if not BASH:
        pytest.skip("keine bash auf diesem Wirt")
    lib = kit_pfad("lib.sh")
    if not lib.is_file():
        pytest.skip("lib.sh liegt in dieser Ablage nicht")
    versteckt = tmp_path / "ide" / "resources" / "native-binary"
    versteckt.mkdir(parents=True)
    cli = versteckt / "claude"
    ergebnis = {"result": "ok", "total_cost_usd": 0.01, "is_error": False}
    cli.write_text("#!/bin/sh\n" + f"cat <<'JSON'\n{json.dumps(ergebnis)}\nJSON\n",
                   encoding="utf-8", newline="\n")
    cli.chmod(0o755)
    heim = tmp_path / "heim"
    (heim / ".config" / "claude-team").mkdir(parents=True)
    skript = tmp_path / "probe.sh"
    skript.write_text(
        f'source "{lib.as_posix()}" 2>/dev/null\n'
        'team_claude probe sonnet "$1" "prompt"\n'
        'echo "EXIT=$?"\n', encoding="utf-8", newline="\n")
    leer = tmp_path / "leer"
    leer.mkdir()
    r = _lauf(skript, tmp_path, heim, leer, TEAM_CLAUDE_BIN=str(cli))
    aus = r.stdout + r.stderr
    assert "EXIT=0" in aus, (
        f"Mit vollem Pfad ausserhalb des PATH laeuft es nicht durch:\n{aus}")
    assert "nicht auffindbar" not in aus, aus


# --- BL-174: der Pausen-Exit ohne API-Schlüssel ------------------------------


ERGEBNIS_429 = {
    "result": "", "total_cost_usd": 0.0, "is_error": True,
    "error": {"type": "rate_limit_error",
              "message": "Session limit reached, resets at 2030-01-01T00:00:00Z"},
}


def test_ein_429_ohne_api_schluessel_erreicht_die_limit_behandlung(tmp_path):
    """Die Gegenprobe, die den Fix erst gültig macht.

    Ein Lauf **ohne jeden API-Schlüssel**, dessen Abo-Aufruf einen 429
    liefert, darf nicht mehr an der Auth-Weiche abbrechen — die
    429-Behandlung steht im Quelltext **darunter** und wurde nie erreicht.

    Geprüft wird an der WIRKUNG: Die Meldung über den fehlenden Schlüssel
    (`AUTH_MODE=api, aber weder …`) darf nicht mehr kommen, und der Lauf muss
    sichtbar in die Limit-Behandlung laufen.
    """
    ueberspringe_ohne_bahn("bash")
    r = _bash_team_claude(tmp_path, pfad_leer=False, ergebnis=ERGEBNIS_429)
    aus = r.stdout + r.stderr
    assert "AUTH_MODE=api, aber weder" not in aus, (
        "BL-174: Der Lauf bricht weiterhin an der Auth-Weiche ab, bevor die "
        f"429-Behandlung ueberhaupt beginnt.\n{aus}")
    assert "429" in aus or "Limit" in aus, (
        f"Die Limit-Behandlung wurde nicht erreicht:\n{aus}")


def test_mit_api_schluessel_bleibt_der_fallback_erhalten(tmp_path):
    """Die Gegenrichtung: Wo ein Schlüssel liegt, muss der Fallback weiter
    laufen — sonst hätte der Fix eine Zusicherung gegen eine andere getauscht."""
    ueberspringe_ohne_bahn("bash")
    r = _bash_team_claude(tmp_path, pfad_leer=False, key="sk-test",
                          ergebnis=ERGEBNIS_429)
    aus = r.stdout + r.stderr
    assert "API-Fallback" in aus, (
        f"Mit hinterlegtem Schluessel wird der Fallback nicht mehr versucht:\n{aus}")


@pytest.mark.parametrize("datei", ["bash/lib.sh", "pwsh/lib.psm1"])
def test_beide_bahnen_fragen_vor_dem_fallback(datei):
    """Der Riegel: Die Abfrage muss VOR dem Moduswechsel stehen, nicht als
    Nebenwirkung von `team_resolve_auth_mode`."""
    t = _lies(*datei.split("/"))
    assert "team_api_weg_vorhanden" in t, (
        f"BL-174: {datei} fragt nicht, ob ueberhaupt ein API-Weg existiert — "
        "dann schneidet ein fehlender Schluessel die 429-Behandlung wieder ab.")


# --- BL-173, Teil 1c: die IDE-Suche, GEFAHREN --------------------------------
#
# Die Tests oben lesen den Quelltext. Sie zeigen, dass die Suche DASTEHT — ob
# sie den Fall auch TRIFFT, zeigt nur ein Lauf. Deshalb hier die echte Funktion
# aus der echten Installer-Datei, in einer gestellten Lage: eine IDE-gebündelte
# CLI unter einem falschen `HOME`, und ein `PATH`, der `claude` nicht kennt.
#
# Der PATH muss ausdrücklich geleert werden: Diese Entwicklungsmaschine HAT ein
# echtes `claude` im PATH, und eine Probe, die das nicht wegnimmt, liefe in den
# PATH-Zweig und würde die IDE-Suche nie erreichen.

INSTALL_SH = REPO_ROOT / "bash" / "install.sh"
INSTALL_PS1 = REPO_ROOT / "pwsh" / "install.ps1"


def _ide_ablage(tmp_path, ordner="anthropic.claude-code-1.2.3", datei="claude"):
    """Eine Erweiterung, wie eine IDE sie ablegt."""
    heim = tmp_path / "heim"
    ziel = (heim / ".vscode" / "extensions" / ordner
            / "resources" / "native-binary")
    ziel.mkdir(parents=True)
    binaer = ziel / datei
    binaer.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8", newline="\n")
    binaer.chmod(0o755)
    return heim, binaer


def _sonde_pwsh(tmp_path, heim):
    if not INSTALL_PS1.is_file():
        pytest.skip("install.ps1 liegt in dieser Ablage nicht (nur im Kit)")
    verlange_pwsh()
    skript = f"""
$ErrorActionPreference = 'Stop'
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           '{INSTALL_PS1.as_posix()}', [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq 'Finde-ClaudeCli' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw 'Finde-ClaudeCli nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text
$env:PATH = ''
$env:HOME = '{heim.as_posix()}'
$env:USERPROFILE = '{heim.as_posix()}'
$r = Finde-ClaudeCli
Write-Output ("FUND=" + $(if ($null -eq $r) {{ '<null>' }} else {{ $r }}))
"""
    p = tmp_path / "sonde-cli.ps1"
    p.write_text(skript, encoding="utf-8-sig", newline="\n")
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"
    m = re.search(r"FUND=(.*)", r.stdout)
    assert m, f"Sonde gab nichts aus:\n{r.stdout}{r.stderr}"
    return m.group(1).strip()


def _sonde_bash(tmp_path, heim):
    if not INSTALL_SH.is_file():
        pytest.skip("install.sh liegt in dieser Ablage nicht (nur im Kit)")
    ueberspringe_ohne_bahn("bash")
    # Die ECHTE Funktion aus der ECHTEN Datei — install.sh laesst sich nicht
    # sourcen, es wuerde eine Installation starten.
    quelle = INSTALL_SH.read_text(encoding="utf-8")
    anfang = quelle.index("finde_claude_cli() {")
    ende = quelle.index("\n}\n", anfang) + 3
    skript = tmp_path / "sonde-cli.sh"
    skript.write_text(
        "#!/bin/sh\n" + quelle[anfang:ende]
        + '\nif r="$(finde_claude_cli)"; then printf "FUND=%s\n" "$r";'
          ' else printf "FUND=<null>\n"; fi\n',
        encoding="utf-8", newline="\n")
    umgebung = dict(os.environ)
    umgebung["PATH"] = str(tmp_path / "leer")
    umgebung["HOME"] = str(heim)
    (tmp_path / "leer").mkdir(exist_ok=True)
    r = subprocess.run([BASH, str(skript)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       env=umgebung, stdin=subprocess.DEVNULL, timeout=60)
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"
    m = re.search(r"FUND=(.*)", r.stdout)
    assert m, f"Sonde gab nichts aus:\n{r.stdout}{r.stderr}"
    return m.group(1).strip()


def test_pwsh_installer_findet_die_ide_gebuendelte_cli(tmp_path):
    """Der Feldfall selbst: angemeldet, lauffähig — und nicht im `PATH`."""
    heim, binaer = _ide_ablage(tmp_path)
    fund = _sonde_pwsh(tmp_path, heim)
    assert fund != "<null>", (
        "BL-173: Der Installer findet die IDE-gebuendelte CLI nicht. Genau "
        "diese Lage lag im Feld vor, und der Erstlauf starb daran.")
    assert fund.replace("\\", "/").lower() == binaer.as_posix().lower(), (
        f"BL-173: gefunden wurde '{fund}', erwartet '{binaer.as_posix()}'.")
    assert "\\" not in fund, (
        "BL-163: Der Wert landet auch in team.config.sh — dort liest ihn eine "
        f"bash. Rueckstriche gehoeren da nicht hin: '{fund}'")


def test_bash_installer_findet_die_ide_gebuendelte_cli(tmp_path):
    """Dieselbe Zusicherung auf der anderen Bahn — beide Installer schreiben
    beide Konfigurationen, also muss auch die Suche auf beiden tragen."""
    heim, binaer = _ide_ablage(tmp_path)
    fund = _sonde_bash(tmp_path, heim)
    assert fund != "<null>", (
        "BL-173: Der bash-Installer findet die IDE-gebuendelte CLI nicht.")
    # Unter Git for Windows uebersetzt die Shell den Laufwerksbuchstaben
    # (C:/... -> /c/...). Das ist kein Unterschied in der Sache; verglichen
    # wird deshalb der Teil unterhalb des Heimatordners.
    schwanz = ".vscode/extensions/anthropic.claude-code-1.2.3/resources/native-binary/claude"
    assert fund.endswith(schwanz), (
        f"BL-173: gefunden wurde '{fund}', erwartet ein Pfad auf "
        f"'{schwanz}'.")


@pytest.mark.parametrize("sonde", ["pwsh", "bash"])
def test_ohne_jede_cli_meldet_die_suche_eine_luecke(tmp_path, sonde):
    """Die Gegenrichtung. Findet die Suche nichts, darf sie nichts erfinden —
    der Aufrufer setzt dann den Vorgabenamen und **nennt** die Lücke, statt sie
    zu verdecken. Ein geratener Pfad wäre schlimmer als gar keiner: Er sähe
    nach einer Antwort aus."""
    heim = tmp_path / "heim"
    heim.mkdir()
    fund = (_sonde_pwsh if sonde == "pwsh" else _sonde_bash)(tmp_path, heim)
    assert fund == "<null>", (
        f"BL-173: Die Suche ({sonde}) meldet einen Fund, wo keiner ist: "
        f"'{fund}'. Dann traegt der Installer einen Pfad ein, hinter dem "
        "nichts liegt — und die Fehlermeldung nennt wieder das Falsche.")

#!/usr/bin/env python3
"""BL-181: Die pwsh-Bahn sammelte die Ausgabe jeder Rolle ein, statt sie zu
streamen — Konsole UND Lauf-Log blieben waehrend des Laufs stumm.

WAS IM FELD PASSIERT IST
    `Feld B`, Windows 11, einbahnig pwsh, zweite Kaskade. Nach

        [16:28:05] === PHASE 1: Ralph (Bau der Kaskade) ===

    kam 36 Minuten lang keine weitere Zeile — weder auf der Konsole noch im
    Lauf-Log, das bei 53 Bytes stehen blieb. In dieser Zeit liefen fuenf Stufen
    durch und wurden committet. Die Frage des Stakeholders lautete woertlich:
    „Stimmt hier irgendwas nicht? Es kommt keine weitere Zeile."

    Auf der bash-Bahn erscheint dieselbe Ausgabe live. Dort steht ganz oben
    `exec > >(tee -a "$LAUF_LOG") 2>&1` — die Shell leitet ihren eigenen Strom
    um, und jeder Kindprozess erbt ihn.

DIE URSACHE IST DIE ZUWEISUNG, NICHT DER KINDPROZESS
    In `Rolle-Starten` stand

        $ausgabe = & pwsh -NoProfile -File $Skript @Argumente 2>&1
        foreach ($z in $ausgabe) { … Console … ; … Add-Content … }

    Die Zuweisung sammelt den KOMPLETTEN Kindprozess ein, bevor die erste Zeile
    herauskommt. Weil Konsole und `Add-Content` in derselben Schleife hingen,
    schwiegen beide Haelften gemeinsam.

DIE MESSREIHE AUS DEM FELD BEZIFFERT ES
        20:18:35  logbytes=53     state=10
        20:44:46  logbytes=53     state=16   ← SIEBEN Stufen gebaut, Log unveraendert
        20:53:19  logbytes=1672   state=17   ← Bau-Rolle endet: 31 Zeilen auf einen Schlag
        20:59:18  logbytes=2082              ← Red-Team-Rolle endet
        21:19:19  logbytes=6086              ← Abschlussbericht

    Jeder Sprung liegt exakt auf einem Rollenende: Die Puffergrenze ist der
    KINDPROZESS. Die Bau-Rolle ist EIN Aufruf fuer ALLE Stufen und belegte 40
    der 66 Laufminuten — 61 % des Laufs in einem stummen Block.

DIE ZWEITE HAELFTE DES SCHADENS
    `team-status` zeigt „Vollautomatik (letzte 3 Zeilen: …)". Diese Zeilen
    existierten waehrend des Laufs nicht. Das mitgelieferte Monitoring-Werkzeug
    war genau in dem Zeitraum blind, fuer den man es aufruft — und zeigte dabei
    keinen Fehler, sondern eine stundenalte Zeile, die aussah wie die aktuelle.

WAS DIESER TEST PRUEFT — UND WAS ER AUSDRUECKLICH NICHT PRUEFT
    Er prueft NICHT, dass am Ende Zeilen im Log stehen. Das taten sie auch
    vorher; genau daran ist der Fehler so lange vorbeigelaufen. Er prueft, dass
    sie VOR dem Ende des Kindprozesses dort stehen — mit einer Wegwerf-Rolle,
    die eine Zeile schreibt, dann wartet, und deren Log waehrenddessen gelesen
    wird. Die Vorlage dafuer ist die Feldmessung selbst.

    Gefahren wird die ECHTE Funktion, ueber den Syntaxbaum aus der echten
    Datei geholt — kein nachgebauter Zwilling: Ein Test gegen eine Kopie
    beweist etwas ueber die Kopie (Lehre aus BL-142).
"""
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (entrypoint_pfad, ueberspringe_ohne_bahn,  # noqa: E402
                      verlange_pwsh)

VOLL_PS1 = entrypoint_pfad("vollautomatik.ps1")

# Die Wegwerf-Rolle wartet so lange zwischen ihren zwei Zeilen.
#
# WARUM DAS URTEIL AN DIESER ZAHL HAENGT UND NICHT AN EINEM MESSFENSTER: Der
# erste Entwurf las das Log nach festen 2 s und war damit FLATTERIG — ein Lauf
# von zehn fiel, weil der pwsh-Start gelegentlich laenger braucht. Ein Test,
# der ohne Defekt rot wird, wird abgeschaltet statt befolgt (`BL-143`), und
# dieser hier soll Jahre halten.
#
# Der Schluss ist deshalb rein logisch statt zeitlich gestimmt: Die Rolle
# startet zum Zeitpunkt ts >= t0 (t0 = Start der Sonde) und ist fruehestens bei
# ts + WARTEN_S fertig, also fruehestens bei t0 + WARTEN_S. Steht VOR dieser
# Grenze eine Zeile im Log, kann die Rolle unmoeglich schon fertig gewesen
# sein — unabhaengig davon, wie lange der Interpreterstart gedauert hat.
WARTEN_S = 6


def _quelltext():
    return VOLL_PS1.read_text(encoding="utf-8-sig")


# --- (1) Quelltext: laeuft auf JEDEM Wirt, auch ohne pwsh --------------------


def test_die_rolle_wird_nicht_mehr_eingesammelt():
    """Der Riegel gegen den Rueckbau.

    Er sitzt bewusst NUR auf dem Start einer Rolle und nicht auf jeder
    Zuweisung eines nativen Aufrufs: `$ref = & git log -1 …` ist voellig in
    Ordnung — dort IST die Ausgabe der Rueckgabewert, sie ist kurz, und
    niemand liest sie live mit. Ein Riegel ueber alle `$x = & …` waere ein
    halbes Dutzend Fehlalarme lang, und ein Riegel mit Fehlalarmen wird
    stillgelegt statt befolgt (`BL-143`).
    """
    ueberspringe_ohne_bahn("pwsh")
    assert VOLL_PS1.is_file(), f"vollautomatik.ps1 nicht gefunden ({VOLL_PS1})"
    ohne_kommentar = [z for z in _quelltext().splitlines()
                      if not z.lstrip().startswith("#")]
    starts = [z for z in ohne_kommentar if re.search(r"&\s*pwsh\b.*-File\s+\$Skript", z)]
    assert starts, (
        "Der Start der Rolle ist nicht mehr zu finden — wurde er umbenannt, "
        "gehoert dieser Riegel nachgezogen, nicht geloescht.")
    for zeile in starts:
        assert not re.match(r"\s*\$\w+\s*=", zeile), (
            "BL-181: Die Ausgabe der Rolle wird wieder in eine Variable "
            "gesammelt. Das haelt den KOMPLETTEN Kindprozess zurueck, bevor "
            "die erste Zeile herauskommt — Konsole und Lauf-Log schweigen "
            f"beide, bis die Rolle fertig ist:\n    {zeile.strip()}")
        assert "|" in zeile, (
            "Der Start der Rolle fuehrt nicht mehr in eine Pipeline — dann "
            f"wird wieder gesammelt statt gestreamt:\n    {zeile.strip()}")


def test_der_rueckgabewert_kommt_aus_lastexitcode():
    """Hinter einer Pipeline ist `$LASTEXITCODE` der einzige Weg zum Code.

    Ein Rueckbau auf eine Zwischenvariable VOR der Schleife wuerde genau hier
    scheitern — deshalb steht die Zeile unter Test und nicht nur im Kommentar.
    """
    ueberspringe_ohne_bahn("pwsh")
    text = _quelltext()
    block = text[text.index("function Rolle-Starten"):]
    block = block[:block.index("\n}\n") + 3]
    assert "return $LASTEXITCODE" in block, (
        "Rolle-Starten gibt nicht mehr $LASTEXITCODE zurueck. Hinter einer "
        "Pipeline gibt es keinen anderen Weg an den Exit-Code der Rolle — "
        "und an ihm haengt die gesamte Fehlerbehandlung der Vollautomatik.")


# --- Die Sonde: die ECHTE Funktion gegen eine Wegwerf-Rolle ------------------


def _pwsh(*args, **kwargs):
    return ["pwsh", "-NoProfile", "-NonInteractive", *args]


def _wegwerf_rolle(tmp_path):
    """Schreibt eine Zeile, wartet, schreibt die zweite, endet mit 7.

    `[Console]::Out.WriteLine` und nicht `Write-Output`: Genau so schreiben die
    Rollen des Kits, und genau deshalb startet die Vollautomatik sie ueberhaupt
    als eigenen Prozess (die Begruendung steht im Kopf von Rolle-Starten).
    Die 7 ist frei gewaehlt und nur dazu da, unterscheidbar zu sein.
    """
    p = tmp_path / "wegwerf-rolle.ps1"
    p.write_text(
        "[Console]::Out.WriteLine('ERSTE ZEILE')\n"
        f"Start-Sleep -Seconds {WARTEN_S}\n"
        "[Console]::Out.WriteLine('ZWEITE ZEILE')\n"
        "exit 7\n", encoding="utf-8-sig", newline="\n")
    return p


def _zeilen(log):
    if not log.exists():
        return 0
    text = log.read_text(encoding="utf-8", errors="replace")
    return len([z for z in text.splitlines() if z.strip()])


def _messen(tmp_path, sonde_text):
    """Faehrt die Sonde und wartet, bis die erste Zeile im Lauf-Log steht.

    Rueckgabe: (frueh, zeilen_am_ende, stdout+stderr) — `frueh` ist True, wenn
    die erste Zeile VOR `t0 + WARTEN_S` erschien, die Rolle also unmoeglich
    schon fertig war. Siehe die Begruendung bei WARTEN_S.
    """
    sonde = tmp_path / "sonde.ps1"
    sonde.write_text(sonde_text, encoding="utf-8-sig", newline="\n")
    log = tmp_path / "lauf.log"
    t0 = time.monotonic()
    lauf = subprocess.Popen(
        _pwsh("-File", str(sonde)), stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    grenze = t0 + WARTEN_S
    # Notbremse, damit ein haengender Kindprozess den Lauf nicht festhaelt —
    # grosszuegig, weil sie NIE das Urteil traegt, nur den Abbruch.
    frist = t0 + 120
    frueh = False
    while True:
        if _zeilen(log):
            frueh = time.monotonic() < grenze
            break
        if lauf.poll() is not None:
            break                      # fertig, ohne dass je etwas dastand
        if time.monotonic() > frist:
            break
        time.sleep(0.05)
    aus = lauf.communicate(timeout=120)[0]
    return frueh, _zeilen(log), aus


def _sonde_echte_funktion(tmp_path):
    """Holt `Rolle-Starten` ueber den SYNTAXBAUM aus der echten Datei.

    Nicht per Textsuche: Ein Regex, der eine Funktion aus einer Datei
    schneidet, bricht am naechsten Kommentar mit geschweifter Klammer — und
    zwar so, dass es wie ein Kit-Defekt aussieht (Lehre aus BL-142).
    """
    rolle = _wegwerf_rolle(tmp_path)
    return f"""
$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $false
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           '{VOLL_PS1.as_posix()}', [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq 'Rolle-Starten' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw 'Rolle-Starten nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text
$laufLog = '{(tmp_path / "lauf.log").as_posix()}'
$code = Rolle-Starten -Skript '{rolle.as_posix()}'
[Console]::Out.WriteLine("EXITCODE=$code")
"""


def test_das_lauf_log_waechst_waehrend_die_rolle_noch_laeuft(tmp_path):
    """DIE tragende Zusicherung — und sie prueft ausdruecklich nicht das Ende.

    Am Ende standen die Zeilen auch vorher im Log. Der Unterschied, den ein
    Mensch vor der Konsole erlebt, ist der Zeitpunkt.
    """
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    frueh, ende, aus = _messen(tmp_path, _sonde_echte_funktion(tmp_path))
    assert frueh, (
        "BL-181: Die erste Zeile stand nicht vor dem fruehestmoeglichen Ende "
        f"der Rolle im Lauf-Log, obwohl die Rolle sie sofort geschrieben und "
        f"danach {WARTEN_S} s gewartet hat. Die Ausgabe wird wieder "
        f"eingesammelt statt gestreamt.\nAusgabe der Sonde:\n{aus}")
    assert ende == 2, (
        f"Am Ende stehen {ende} statt 2 Zeilen im Log — gestreamt schon, "
        f"aber nicht vollstaendig.\n{aus}")


def test_der_exitcode_ueberlebt_die_pipeline(tmp_path):
    """Daran haengt die gesamte Fehlerbehandlung der Vollautomatik.

    `$LASTEXITCODE` hinter einer Pipeline ist die Stelle, an der ein Rueckbau
    still kaputtgehen wuerde: Der Lauf liefe weiter und hielte jede
    gescheiterte Rolle fuer erfolgreich.
    """
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    _, _, aus = _messen(tmp_path, _sonde_echte_funktion(tmp_path))
    assert "EXITCODE=7" in aus, (
        "Rolle-Starten gibt den Exit-Code der Rolle nicht mehr durch — "
        f"erwartet war 7.\nAusgabe der Sonde:\n{aus}")


def test_gegenprobe_das_einsammeln_puffert_wirklich(tmp_path):
    """Ohne diesen Fall wuesste niemand, ob die Zusicherung oben etwas
    absichert oder nur beschreibt, was in PowerShell ohnehin gilt (BL-14).

    Hier steht die ALTE Fassung woertlich — sie MUSS stumm bleiben.
    """
    verlange_pwsh()
    rolle = _wegwerf_rolle(tmp_path)
    alt = f"""
$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $false
$laufLog = '{(tmp_path / "lauf.log").as_posix()}'
$ausgabe = & pwsh -NoProfile -File '{rolle.as_posix()}' 2>&1
$code = $LASTEXITCODE
foreach ($z in $ausgabe) {{
    $text = [string]$z
    [Console]::Out.WriteLine($text)
    Add-Content -LiteralPath $laufLog -Value $text -Encoding utf8
}}
[Console]::Out.WriteLine("EXITCODE=$code")
"""
    frueh, ende, aus = _messen(tmp_path, alt)
    assert not frueh, (
        "Der Gegenbeweis greift nicht mehr: Die alte Fassung streamt hier "
        "schon von selbst. Entweder hat sich PowerShell geaendert oder die "
        f"Sonde trifft den Fall nicht.\n{aus}")
    assert ende == 2, f"Die alte Fassung hat am Ende nicht alles geschrieben:\n{aus}"

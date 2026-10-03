#!/usr/bin/env python3
"""BL-248: Die Vollautomatik hing endlos, wenn eine Rolle einen GUI-Enkel
hinterliess — kein Fehler, kein Exit, keine Zeitgrenze, nur Stillstand.

DER FELDBEFUND (`Feld B`, 2026-09-13)
    `Rolle-Starten` streamte die Ausgabe ueber eine Pipeline, und eine
    Pipeline endet erst bei EOF — wenn JEDER Prozess das geerbte Schreibende
    losgelassen hat, auch Enkel. Eine Bau-Rolle hinterliess ein `electron.exe`
    mit modalem Fehlerdialog: Ralph loggte „Feierabend", danach stand der
    Orchestrator NEUN STUNDEN ohne einen Kindprozess, hielt die Sperre, und
    `team-status` zeigte „Feierabend" — die Anzeige log in Richtung „laeuft".

DIE PROBE
    Eine Wegwerf-Rolle startet einen Enkel, der die geerbte Ausgabe 20 s lang
    offenhaelt, und endet sofort mit 5. Die ECHTE Funktion (ueber den
    Syntaxbaum geholt) muss deutlich vor den 20 s zurueckkehren, den
    Exit-Code durchreichen und den Fall melden. Die Gegenprobe faehrt die alte
    Pipeline-Fassung woertlich — sie MUSS die 20 s abwarten, sonst prueft
    dieser Test nichts (BL-14).

Die bash-Bahn ist nicht betroffen: `./ralph.sh; rc=$?` wartet per waitpid auf
das Kind; die Leitung zu `tee` bleibt dabei unbeachtet offen.
"""
import re
import subprocess
from pathlib import Path

import pytest

from conftest import entrypoint_pfad, ueberspringe_ohne_bahn, verlange_pwsh

ENKEL_S = 20

ROLLE = f"""[Console]::Out.WriteLine('ROLLE FERTIG')
Start-Process -NoNewWindow -FilePath ([System.Environment]::ProcessPath) `
    -ArgumentList '-NoProfile','-Command','Start-Sleep -Seconds {ENKEL_S}'
exit 5
"""


def _sonde(tmp_path, funktion_text=None):
    voll = Path(entrypoint_pfad("vollautomatik.ps1"))
    rolle = tmp_path / "rolle.ps1"
    rolle.write_text(ROLLE, encoding="utf-8-sig", newline="\n")
    log = tmp_path / "lauf.log"
    if funktion_text is None:
        funktion_text = f"""
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           '{voll.as_posix()}', [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq 'Rolle-Starten' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw 'Rolle-Starten nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text
"""
    sonde = tmp_path / "sonde.ps1"
    sonde.write_text(f"""
$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $false
{funktion_text}
$laufLog = '{log.as_posix()}'
$t0 = [DateTime]::UtcNow
$code = Rolle-Starten -Skript '{rolle.as_posix()}'
$dauer = ([DateTime]::UtcNow - $t0).TotalSeconds
[Console]::Out.WriteLine("EXITCODE=$code")
[Console]::Out.WriteLine(("DAUER=" + [int]$dauer))
""", encoding="utf-8-sig", newline="\n")
    # Gemessen wird IN der Sonde: Der Enkel erbt auch die Leitung zu diesem
    # Test, und subprocess wartet auf deren EOF — die Gesamtdauer sagt deshalb
    # nichts darueber, wann Rolle-Starten zurueckkehrte.
    r = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File",
                        str(sonde)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    aus = r.stdout + r.stderr
    treffer = re.search(r"DAUER=(\d+)", aus)
    assert treffer, f"Die Sonde hat keine Dauer gemeldet:\n{aus}"
    return int(treffer.group(1)), aus, log


def test_die_rolle_endet_und_der_lauf_geht_weiter(tmp_path):
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    dauer, aus, log = _sonde(tmp_path)
    assert "EXITCODE=5" in aus, f"Der Exit-Code der Rolle fehlt:\n{aus}"
    assert dauer < ENKEL_S - 5, (
        f"Rolle-Starten hat {dauer:.0f} s gewartet — auf den Enkel statt auf "
        f"die Rolle (BL-248).\n{aus}")
    assert "Kit-BL-248" in aus, f"Der haengende Nachfahre wird nicht gemeldet:\n{aus}"
    text = log.read_text(encoding="utf-8")
    assert "ROLLE FERTIG" in text and "Kit-BL-248" in text, text


def test_gegenprobe_die_pipeline_wartet_auf_den_enkel(tmp_path):
    verlange_pwsh()
    alt = """
function Rolle-Starten {
    param([string]$Skript, [string[]]$Argumente = @())
    & pwsh -NoProfile -File $Skript @Argumente 2>&1 | ForEach-Object {
        $text = [string]$_
        [Console]::Out.WriteLine($text)
        Add-Content -LiteralPath $laufLog -Value $text -Encoding utf8
    }
    return $LASTEXITCODE
}
"""
    dauer, aus, _ = _sonde(tmp_path, alt)
    assert dauer >= ENKEL_S - 2, (
        "Die Gegenprobe greift nicht mehr: Die alte Pipeline-Fassung wartet "
        f"hier nicht auf den Enkel ({dauer:.0f} s). Dann prueft der Test oben "
        f"nichts.\n{aus}")


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))

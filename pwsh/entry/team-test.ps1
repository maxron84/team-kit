# Bahn: pwsh | Gegenstueck: team-test.sh
<#
  team-test.ps1 — fuehrt die Regressionstests der TEAM-INFRASTRUKTUR aus.

  Bewusst getrennt vom Testlauf des Projekts: Die Team-Tests sind pytest und
  pruefen team/lib.sh, team/lib.psm1, team/tools/*.py und die Briefings —
  nicht deinen Code. Dein Projekt behaelt seinen eigenen Test-Befehl
  (siehe TEAM_SMOKE_TEST).

  Aufruf:  .\team-test.cmd [weitere pytest-Argumente]
#>
$ErrorActionPreference = 'Stop'
# BL-122: Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
# standardmaessig $true — ein Exit-Code != 0 aus einem NATIVEN Befehl ist damit
# ein TERMINIERENDER Fehler und nicht mehr nur ein Wert in $LASTEXITCODE. Diese
# Bahn ist durchgehend fuer den klassischen Vertrag geschrieben: aufrufen,
# $LASTEXITCODE lesen, entscheiden. Ohne diese Zeile ist jede dieser
# Entscheidungen unerreichbar — der Abbruch kommt vorher.
$PSNativeCommandUseErrorActionPreference = $false
Set-Location $PSScriptRoot

# BL-124: pytest wird AUFGELOEST, nicht vorausgesetzt.
#
# Unter Windows legt `pip install pytest` die pytest.exe in ein
# Scripts-Verzeichnis, das oft NICHT im PATH steht — bei `--user` warnt pip
# beim Installieren sogar davor. Das Modul ist dann installiert, und
# Get-Command findet trotzdem nichts. Diese Datei meldete daraufhin "pytest
# nicht gefunden" und empfahl genau die Installation, die den Zustand
# erzeugt hatte.
#
# Der Weg ueber den Interpreter findet es in beiden Faellen — und benutzt
# garantiert DASSELBE Python wie die uebrigen Team-Werkzeuge. Ein pytest im
# PATH kann zu einer anderen Installation gehoeren als das Python, unter dem
# team/tools/ laeuft; dann testet man etwas anderes, als man betreibt.
$kandidaten = if ($IsWindows) { @('python', 'python3', 'py') }
              else            { @('python3', 'python', 'py') }
foreach ($k in $kandidaten) {
    if (-not (Get-Command $k -ErrorAction SilentlyContinue)) { continue }
    try { & $k -m pytest --version 2>$null | Out-Null } catch { continue }
    if ($LASTEXITCODE -eq 0) {
        & $k -m pytest -q team/tests @args
        exit $LASTEXITCODE
    }
}
# Letzter Versuch: ein pytest im PATH, dessen Interpreter wir nicht kennen.
if (Get-Command pytest -ErrorAction SilentlyContinue) {
    & pytest -q team/tests @args
    exit $LASTEXITCODE
}
[Console]::Error.WriteLine('pytest nicht gefunden — die Team-Tests brauchen es.')
[Console]::Error.WriteLine('  Gesucht wurde als MODUL (python/python3/py -m pytest) und als Befehl.')
[Console]::Error.WriteLine('  Installation: python -m pip install pytest')
[Console]::Error.WriteLine('  Steht pytest schon da, fehlt nur sein Scripts-Ordner im PATH —')
[Console]::Error.WriteLine('  der Modulaufruf oben braucht ihn nicht, also fehlt hier das Modul.')
[Console]::Error.WriteLine('  (Abhaengigkeit der Team-Infrastruktur, nicht deines Projekts.)')
exit 2

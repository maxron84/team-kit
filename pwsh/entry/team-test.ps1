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

if (-not (Get-Command pytest -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine('pytest nicht gefunden — die Team-Tests brauchen es.')
    [Console]::Error.WriteLine('  Installation: python -m pip install pytest')
    [Console]::Error.WriteLine('  (Abhaengigkeit der Team-Infrastruktur, nicht deines Projekts.)')
    exit 2
}
& pytest -q team/tests @args
exit $LASTEXITCODE

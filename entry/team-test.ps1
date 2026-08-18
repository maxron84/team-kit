<#
  team-test.ps1 — fuehrt die Regressionstests der TEAM-INFRASTRUKTUR aus.

  Bewusst getrennt vom Testlauf des Projekts: Die Team-Tests sind pytest und
  pruefen team/lib.sh, team/lib.psm1, team/tools/*.py und die Briefings —
  nicht deinen Code. Dein Projekt behaelt seinen eigenen Test-Befehl
  (siehe TEAM_SMOKE_TEST).

  Aufruf:  .\team-test.cmd [weitere pytest-Argumente]
#>
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Get-Command pytest -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine('pytest nicht gefunden — die Team-Tests brauchen es.')
    [Console]::Error.WriteLine('  Installation: python -m pip install pytest')
    [Console]::Error.WriteLine('  (Abhaengigkeit der Team-Infrastruktur, nicht deines Projekts.)')
    exit 2
}
& pytest -q team/tests @args
exit $LASTEXITCODE

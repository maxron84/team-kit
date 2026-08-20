# Bahn: pwsh | Gegenstueck: team-init.sh
<#
  team-init.ps1 — Starter fuer das T.E.A.M.-Starterkit (Windows-Zweig).

  Duenner Launcher: findet das Kit-Repo und reicht alle Argumente durch.
  Der eigentliche Installer lebt versioniert im Kit (<kit>\install.ps1).

  Aufruf:  pwsh -File <kit>\scripts\team-init.ps1 <zielpfad> [-NichtInteraktiv] [-Update|-Force]

  Der Sinn des Skripts ist der KURZBEFEHL: `kit-einrichten.ps1 -Verknuepfen`
  legt daneben einen Aufrufer unter %USERPROFILE%\.claude\scripts\ ab, danach
  ist der Installer von ueberall erreichbar, ohne dass eine zweite Kopie
  entsteht, die auseinanderlaeuft. Deshalb leitet das Skript den Kit-Ort aus
  seinem EIGENEN Ort ab, statt ihn zu raten.

  Warum hier keine Symlink-Kette aufgeloest wird wie in team-init.sh: Unter
  Windows braucht ein Symlink Administratorrechte oder den Entwicklermodus.
  kit-einrichten.ps1 legt deshalb einen .cmd-Aufrufer an, der auf DIESE Datei
  an ihrem Platz im Kit zeigt — es gibt keine Kette, die man aufloesen
  muesste, und keine zweite Kopie, die veralten kann.

  Reihenfolge der Kit-Suche:
    1. $env:TEAM_KIT_PFAD          (ausdruecklich gesetzt gewinnt immer)
    2. Elternordner dieses Skripts (der Normalfall)
    3. %USERPROFILE%\Source\team-kit
#>
$ErrorActionPreference = 'Stop'

$hier = Split-Path -Parent $PSCommandPath
$kandidaten = @(
    $env:TEAM_KIT_PFAD
    (Split-Path -Parent $hier)
    (Join-Path $env:USERPROFILE 'Source\team-kit')
) | Where-Object { $_ }

foreach ($kandidat in $kandidaten) {
    $installer = Join-Path $kandidat 'install.ps1'
    if (Test-Path $installer) {
        & $installer @args
        exit $LASTEXITCODE
    }
}

Write-Host "FEHLER: T.E.A.M.-Starterkit nicht gefunden." -ForegroundColor Red
Write-Host "  Gesucht in: $($kandidaten -join ', ')"
Write-Host "  Anderer Ort? `$env:TEAM_KIT_PFAD = 'C:\pfad\zum\kit'; pwsh -File $PSCommandPath ..."
exit 2

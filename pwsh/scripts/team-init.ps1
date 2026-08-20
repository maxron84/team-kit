# Bahn: pwsh | Gegenstueck: team-init.sh
<#
  team-init.ps1 — Starter fuer das T.E.A.M.-Starterkit (pwsh-Bahn).

  Duenner Launcher: findet das Kit-Repo und reicht alle Argumente durch.
  Der eigentliche Installer lebt versioniert im Kit (<kit>\pwsh\install.ps1).

  Aufruf:  pwsh -File <kit>\pwsh\scripts\team-init.ps1 <zielpfad> [-NichtInteraktiv] [-Update|-Force]

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
# BL-122: Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
# standardmaessig $true — ein Exit-Code != 0 aus einem NATIVEN Befehl ist damit
# ein TERMINIERENDER Fehler und nicht mehr nur ein Wert in $LASTEXITCODE. Diese
# Bahn ist durchgehend fuer den klassischen Vertrag geschrieben: aufrufen,
# $LASTEXITCODE lesen, entscheiden. Ohne diese Zeile ist jede dieser
# Entscheidungen unerreichbar — der Abbruch kommt vorher.
$PSNativeCommandUseErrorActionPreference = $false

$hier = Split-Path -Parent $PSCommandPath
# Zwei Elternebenen, weil dieses Skript vor der Bahn-Trennung unter
# <kit>\scripts\ lag und heute unter <kit>\pwsh\scripts\ — eine Kopie aus
# der Zeit davor liegt entsprechend anders.
$kandidaten = @(
    $env:TEAM_KIT_PFAD
    (Split-Path -Parent (Split-Path -Parent $hier))
    (Split-Path -Parent $hier)
    (Join-Path $env:USERPROFILE 'Source\team-kit')
) | Where-Object { $_ }

# Ablagen des Installers, neueste zuerst. Dieses Skript ist das EINZIGE
# Stueck des Kits, von dem eine Kopie ausserhalb des Repos liegen kann
# (unter %USERPROFILE%\.claude\scripts\). Eine solche Kopie wird nicht
# mitgezogen, wenn sich im Kit etwas verschiebt — der Umzug auf bash\ und
# pwsh\ hat jede aeltere Kopie stillgelegt, weil sie <kit>\install.ps1
# suchte. Deshalb wird nicht EIN Ort geraten, sondern die Liste durchgegangen.
$installerOrte = @('pwsh\install.ps1', 'install.ps1')
$gesucht = @()

foreach ($kandidat in $kandidaten) {
    foreach ($ort in $installerOrte) {
        $installer = Join-Path $kandidat $ort
        $gesucht += $installer
        if (Test-Path $installer) {
            & $installer @args
            exit $LASTEXITCODE
        }
    }
}

Write-Host "FEHLER: T.E.A.M.-Starterkit nicht gefunden." -ForegroundColor Red
Write-Host "  Gesucht in:"; $gesucht | ForEach-Object { Write-Host "    $_" }
Write-Host "  Anderer Ort? `$env:TEAM_KIT_PFAD = 'C:\pfad\zum\kit'; pwsh -File $PSCommandPath ..."
exit 2

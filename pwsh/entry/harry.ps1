# Bahn: pwsh | Gegenstueck: harry.sh
<#
  harry.ps1 — Read-Only Red Team, Schwerpunkt Security/Angriffsflaeche.
  Duenner Wrapper: setzt Rolle + Auftrag, Rest macht team/redteam.ps1.

  BL-20: Der ausgelieferte Default beschrieb bis 2.8.1 eine statische Website.
  In jedem anderen Stack zielte er nicht bloss daneben, sondern behauptete
  etwas SACHLICH FALSCHES ueber das Zielprojekt — und ein Modell uebernimmt
  das als Tatsache. Feld-Beleg (pygame-Spiel, K3): Harrys Sweep ueber vier
  neue Baustufen, darunter ein pfadnehmender Datei-Leser, kostete 0,4567 USD
  und meldete NULL Funde; derselbe Code mit passendem Fokus: 1,0247 USD, ein
  Fund. Der leere Sweep war kein Beleg fuer Fehlerfreiheit, sondern fuer einen
  Auftrag, der am Projekt vorbeisah.

  Der Default beschreibt deshalb die METHODE, nicht die Technologie. Projekte,
  die es genauer sagen koennen, setzen TEAM_REDTEAM_AUFTRAG_HARRY in
  team.config.ps1 — dort, weil `install.ps1 -Update` diese Datei ueberleben
  laesst; eine Anpassung hier waere beim naechsten Update weg.
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
Import-Module ./team/lib.psm1 -Force -DisableNameChecking
# BL-223: Dieses Skript kennt keine Argumente — bis 2.13.1 hat es sie deshalb
# NIE GELESEN, und `--hilfe` startete einen bezahlten Rollenlauf.
$bedienung = Team-BedienungPruefen $args $PSCommandPath
if ($bedienung -ge 0) { exit $bedienung }

# BL-172: Hier steht nur noch der GRUNDAUFTRAG (oder der stackneutrale
# Default). Den Fokus haengt team/redteam.ps1 an — dort liegt die
# Bibliothek, und dort steht auch die Scope-Zeile, bei der Ersetzen
# richtig ist. Die beiden Faelle sollen nebeneinander sichtbar sein.
$auftrag = $TEAM_REDTEAM_AUFTRAG_HARRY
if (-not $auftrag) {
    $auftrag = 'Security/Angriffsflaeche — versuche das Programm auszuhebeln. Frage dich: Was gelangt von AUSSEN in diesen Prozess (Eingaben, Dateien, Argumente, Umgebung, Netz, Zwischenablage), und was passiert bei Werten, mit denen niemand gerechnet hat — zu gross, leer, fremdes Encoding, boesartig geformte Pfade? Wo verlaesst sich Code auf eine Zusicherung, die der Aufrufer gar nicht geben muss? Wo werden Rechte, Geheimnisse oder Ressourcen weitergereicht, ohne dass jemand sie prueft? Belege jeden Fund an der Fundstelle im Code.'
}
& ./team/redteam.ps1 -Rolle 'harry' -Auftrag $auftrag
exit $LASTEXITCODE

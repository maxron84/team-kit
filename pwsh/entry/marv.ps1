# Bahn: pwsh | Gegenstueck: marv.sh
<#
  marv.ps1 — Read-Only Red Team, Schwerpunkt Chaos/Regression.
  Duenner Wrapper: setzt Rolle + Auftrag, Rest macht team/redteam.ps1.

  BL-20: siehe harry.ps1 — der Default nennt keine Technologie mehr, sondern
  die Methode. Projektseitige Uebersteuerung: TEAM_REDTEAM_AUFTRAG_MARV in
  team.config.ps1.

  BL-21: Der zweite Absatz schliesst eine DIMENSION, nicht eine Stack-Luecke.
  Alle Rollenauftraege des Kits waren adversarisch (was kann ein Angreifer, was
  bricht bei Missbrauch); was der GEWOEHNLICHE Pfad kostet, fragte keiner.
  Feld-Beleg: ein Spiel zog 42 % CPU-Last bei 103 gruenen Tests — eine
  @property berechnete einen invarianten Wert ~600x je Frame neu. Harry hatte
  dieselbe Datei kurz zuvor gelesen und drei Zeilen darueber einen Fund
  gelandet; seine Frage zeigte auf Einlese-Robustheit, nicht auf Dauerkosten.
  Die Schwelle im Text ist Absicht: "das ginge schneller" ist unbegrenzt.
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

# BL-172: Hier steht nur noch der GRUNDAUFTRAG (oder der stackneutrale
# Default). Den Fokus haengt team/redteam.ps1 an — dort liegt die
# Bibliothek, und dort steht auch die Scope-Zeile, bei der Ersetzen
# richtig ist. Die beiden Faelle sollen nebeneinander sichtbar sein.
$auftrag = $TEAM_REDTEAM_AUFTRAG_MARV
if (-not $auftrag) {
    $auftrag = 'Chaos/Regression — wirf dem Programm Steine in den Weg: kaputte, leere, riesige oder widerspruechliche Daten; Sonderzeichen und Encoding-Fallen; Zustaende in falscher Reihenfolge; abgebrochene Vorgaenge; alles, was ein ungeduldiger Anwender dreimal hintereinander tut. Pruefe ausserdem, was der GEWOEHNLICHE Pfad kostet: Wird Invariantes bei jedem Aufruf neu berechnet, waechst Arbeit mit einer Groesse, die nicht wachsen muesste? Melde das NUR, wenn der normale Betrieb asymptotisch mehr kostet als noetig — kein Feintuning. Diese Luecke liegt zwischen Korrektheit und Kosten und ist bei gruener Suite unsichtbar.'
}
& ./team/redteam.ps1 -Rolle 'marv' -Auftrag $auftrag
exit $LASTEXITCODE

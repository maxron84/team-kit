# Bahn: pwsh | Gegenstueck: fixphase.sh
<#
  fixphase.ps1 — NUR die Fix-Phase: Frank fixt, Axel knackt die harten Faelle,
  mit Lauf-Deckel, Auslauf-Bremse und Abschlussbericht. Ohne Bau und ohne
  Red-Team-Sweeps (Kit-BL-241, Kit-BL-204).

  Fuer Funde ausserhalb einer Kaskade: nach einer Handabnahme, zwischen zwei
  Kaskaden, nach einem Abbruch in der Fix-Phase. `frank.cmd` in einer Schleife
  waere eine Fix-Phase OHNE Axel: Nach drei Fehlversuchen setzt Frank den Fund
  auf 'an Axel übergeben', findet ihn danach nicht mehr, und die Schleife
  meldet 'nichts zu tun', waehrend ein Fall auf Axel wartet. Die volle
  Vollautomatik faehrt davor zwei bezahlte Sweeps, die neue Funde erzeugen.

  Derselbe Code wie Phase 4 der Vollautomatik — eine zweite Tuer, kein
  zweites Verhalten. Bricht der Lauf ab (Deckel, Bremse, Session-Pause), nimmt
  .\fixphase.cmd oder .\vollautomatik.cmd ihn bei Phase 4 wieder auf.

  Aufruf:  .\fixphase.cmd        (keine Argumente; --hilfe zeigt diesen Kopf)
  Env:     wie vollautomatik.ps1 — TEAM_BUDGET_USD, TEAM_MAX_RUNDEN,
           TEAM_FIX_MAX_STAGNATION.
  Exit:    wie vollautomatik.ps1 — 0 durch · 1 Fehler/Stagnation/Deckel ·
           42 Session-Pause · 43 Fix fertig, Quittung fehlt · 44 Gate rot.
#>
$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $false
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking
# BL-223: Dieses Skript kennt keine Argumente.
$bedienung = Team-BedienungPruefen $args $PSCommandPath
if ($bedienung -ge 0) { exit $bedienung }

# Die Variable gilt nur fuer diesen einen Aufruf. In einer interaktiven
# pwsh-Sitzung bliebe sie sonst stehen, und der naechste Vollautomatik-Lauf
# begaenne still bei Phase 4 (dieselbe Falle wie Kit-BL-284).
$env:TEAM_VOLLAUTOMATIK_AB_PHASE = '4'
try {
    & ./vollautomatik.ps1
    $rc = $LASTEXITCODE
} finally {
    Remove-Item Env:TEAM_VOLLAUTOMATIK_AB_PHASE -ErrorAction SilentlyContinue
}
exit $rc

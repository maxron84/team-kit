<#
  axel.ps1 — Axel Foley, Read-Only Forensiker, automatisch gerufen.
  Nimmt EINEN Fall mit Status 'an Axel übergeben', erstellt eine
  Ermittlungsakte (Root-Cause + Fix-Plan) und gibt an Frank zurueck
  (Status -> 'Fix-Plan liegt vor'). Ein Fall pro Aufruf.

  Read-Only wie das Red Team: darf NUR den Plan-Ordner schreiben (Guard
  Linie 3). Axel denkt, Frank tippt. Startet NIE von selbst im Dauer-Loop.

  Modell: TEAM_MODEL_STRONG (Default opus). Auth auch bei Axel Abo-first mit
  API-Fallback.
  Exit: 0 = Akte erstellt · 3 = kein Axel-Fall · 1 = Fehler/Guard-Bruch
        42 = Session-Limit
#>
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

if (-not (team_lock 'axel')) { exit 1 }

# Zwei-Schwellen-Modell (HM-32): Axel ist wie Frank ein iterierendes
# "Sorgenkind". Soft-Cap = nur Hinweis (die Akte bleibt gueltig, wenn sie
# bereits bezahlt ist); erst der Hard-Cap bricht ab.
$axelBudget = if ($env:AXEL_BUDGET_USD) { $env:AXEL_BUDGET_USD } else { $TEAM_ROLE_BUDGET_USD }
$axelHardcap = if ($env:AXEL_HARDCAP_USD) { $env:AXEL_HARDCAP_USD } else { $TEAM_ROLE_HARDCAP_USD }
$logDir = '.team-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$whitelist = $TEAM_WHITELIST_AXEL

$hm = (Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', 'an Axel übergeben') 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $hm) {
    [Console]::Out.WriteLine("[axel] Kein Fall mit Status 'an Axel übergeben' — nichts zu tun.")
    exit 3
}
$hm = ([string]$hm).Trim()

[Console]::Out.WriteLine("=== Axel: Ermittlung zu $hm (Modell $TEAM_MODEL_STRONG, Budget $axelBudget USD) ===")
$out = Join-Path $logDir "axel-$hm-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$axNr = 1
if (Test-Path $TEAM_ERMITTLUNGSAKTEN) {
    $axNr = @(Get-ChildItem -Path $TEAM_ERMITTLUNGSAKTEN -Filter 'AX-*.md' -Recurse -File -ErrorAction SilentlyContinue).Count + 1
}
$startHash = (& git rev-parse HEAD).Trim()

# BL-52: derselbe Pruefumfang wie beim Red Team — was Harry und Marv angreifen
# duerfen, muss Axel lesen duerfen und trotzdem tabu bleiben.
$axelTabu = "$TEAM_PRODUKTIVCODE**"
if ($TEAM_WEITERER_CODE) { $axelTabu = "$TEAM_PRODUKTIVCODE** und $TEAM_WEITERER_CODE" }

# BL-51: Der Plan-Ordner ist Axels EINZIGE Schreibzone; in einer gewachsenen
# Codebasis liegt dort fremdes Eigentum, auf das der Guard nicht anschlaegt.
$axelBestand = ''
if ($TEAM_PLAN_ORDNER_BESTAND) {
    $axelBestand = @"

BESTAND — NICHT DEIN EIGENTUM: In $TEAM_PLAN_ORDNER lagen beim Einzug des Teams
schon fremde Dateien ($TEAM_PLAN_ORDNER_BESTAND). Du legst dort NUR NEUE Dateien an
und änderst oder löschst nichts, was du nicht selbst angelegt hast — auch nicht,
was in dieser Aufzählung fehlt. Der Guard lässt dich hier gewähren.

"@
}

$prompt = @"
$(team_briefing 'axel')

Knacke den Fall $hm aus $TEAM_BEUTEBUCH, an dem Frank gescheitert ist.

EISERNE REGEL: Read-only. Du änderst NUR $TEAM_PLAN_ORDNER — NIEMALS $axelTabu. Du fixst NICHTS
und committest NICHT. Du lieferst eine Ermittlungsakte, Frank setzt sie um.
$axelBestand

Lege $TEAM_ERMITTLUNGSAKTEN/AX-$axNr.md an:
# AX-$axNr — <Titel> (Bezug: $hm)
## Root-Cause
<tiefe Ursachenanalyse — warum tritt der Fehler wirklich auf>
## Warum Franks Versuche scheiterten
<konkret>
## Schrittweiser Fix-Plan
1. … 2. … (so präzise, dass Frank es 1:1 umsetzen kann)

Setze danach den Status zurück an Frank:
$TEAM_BEUTEBUCH_TOOL set $hm 'Fix-Plan liegt vor'

Beende mit exakt: <promise>AXEL_CASE_COMPLETE</promise>
"@.TrimEnd()

$allowedTools = team_allowed_tools 'axel'
team_guard_begin | Out-Null
$rc = team_claude 'axel' $TEAM_MODEL_STRONG $out $prompt `
        '--permission-mode' 'default' '--allowedTools' $allowedTools

# Linie 3: harte Durchsetzung der Read-Only-Grenze (chirurgisch). Laeuft AUF
# JEDEM Pfad — auch 42-Pause und generischer Fehler (HM-18/HM-23). BL-16
# Ebene 2: Das Urteil faellt unten, wenn feststeht, ob die Ermittlung geliefert
# wurde. Zurueckgerollt und gemeldet hat team_guard_verify bereits.
$guardUebergriff = 0
if (-not (team_guard_verify 'axel' $whitelist)) { $guardUebergriff = 1 }

if ($rc -eq 42) {
    # HM-27: Der Guard oben resettet nur Pfade AUSSERHALB der Whitelist — eine
    # bereits geschriebene, nie committete Akte INNERHALB des Plan-Ordners
    # bliebe sonst als impliziter, nie verifizierter Fortschritt liegen.
    Team-Fehler "[axel] Session-Limit — Ermittlung pausiert (Reset: $(if ($TEAM_LAST_RESET) { $TEAM_LAST_RESET } else { 'unbekannt' })). Halbfertige $TEAM_PLAN_ORDNER-Seiteneffekte werden verworfen."
    & git reset --hard $startHash | Out-Null
    & git clean -fd -- $TEAM_PLAN_ORDNER | Out-Null
    exit 42
} elseif ($rc -ne 0) {
    Team-Fehler '[axel] Aufruf fehlgeschlagen.'
    exit 1
}

[Console]::Out.WriteLine("Axel: $hm kostete $TEAM_LAST_COST USD.")
# Zwei-Schwellen-Pruefung: 2 = Soft-Cap (nur Hinweis, die Akte bleibt gueltig
# und wird normal auf ihr Promise geprueft), 3 = Hard-Cap (Abbruch). Der Guard
# lief bereits oben auf JEDEM Pfad (HM-23), daher hier nur die Auswertung.
$budgetRc = team_budget_check $TEAM_LAST_COST $axelBudget "Axel $hm" $axelHardcap
if ($budgetRc -eq 2) {
    Team-Fehler "[axel] Soft-Cap überschritten ($TEAM_LAST_COST USD ≥ $axelBudget USD) — kein Abbruch, Akte wird normal geprüft (Hard-Cap $axelHardcap USD)."
} elseif ($budgetRc -ge 3) {
    Team-Fehler "[axel] HARD-Cap gesprengt ($TEAM_LAST_COST USD ≥ $axelHardcap USD) — Abbruch."
    exit 1
}

if (-not (team_promise_in $TEAM_LAST_OUT 'AXEL_CASE_COMPLETE')) {
    Team-Fehler "[axel] Kein Akten-Promise — Log prüfen: $TEAM_LAST_OUT"
    exit 1
}

# BL-16 Ebene 2: Das Ergebnis der Rolle ist die Akte UND der Statuswechsel.
# Liegen beide vor, zaehlt die Runde auch dann, wenn der Guard einen Uebergriff
# kassieren musste — die Ermittlung ist geleistet.
$akte = Join-Path $TEAM_ERMITTLUNGSAKTEN "AX-$axNr.md"
$statusJetzt = ''
foreach ($z in @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list'))) {
    $sp = $z -split "`t"
    if ($sp.Count -ge 2 -and $sp[0] -eq $hm) { $statusJetzt = $sp[1] }
}
$ergebnis = 0
if ((Test-Path $akte) -and $statusJetzt -eq 'Fix-Plan liegt vor') { $ergebnis = 1 }
if (-not (team_guard_urteil 'axel' $guardUebergriff $ergebnis)) {
    Team-Fehler "[axel] Akte vorhanden: $(if (Test-Path $akte) { 'ja' } else { 'nein' }) · Status ${hm}: $(if ($statusJetzt) { $statusJetzt } else { 'unbekannt' })"
    exit 1
}

# Akte + Status-Update deterministisch committen (Axel selbst darf nicht).
if (@(& git status --porcelain -- $TEAM_PLAN_ORDNER | Where-Object { $_ }).Count) {
    & git add $TEAM_PLAN_ORDNER | Out-Null
    & git commit -q -m "docs(akte): AX-$axNr zu $hm — Root-Cause + Fix-Plan für Frank" | Out-Null
}
[Console]::Out.WriteLine("[axel] Ermittlungsakte AX-$axNr erstellt, $hm zurück an Frank ('Fix-Plan liegt vor').")
exit 0

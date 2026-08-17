<#
  frank.ps1 — Frank der Fixer als Event-Loop am Beutebuch.
  Greift EINEN Fund mit Status 'an Frank übergeben', fixt ihn nach Franks
  Dreisatz (Commit fix(uat) -> CHANGELOG -> Beutebuch-Status). Ein Fund pro
  Aufruf.

  Frank DARF Produktivcode aendern (kein Read-Only-Guard) — stattdessen
  Dreisatz-Verifikation nach dem Aufruf.

  Versuchszaehler .frank-attempts (transient): ab TEAM_FRANK_MAX_VERSUCHE (3)
  Fehlversuchen wird der Fund auf 'an Axel übergeben' gesetzt.
  Exit: 0 = gefixt · 3 = kein offener Fund fuer Frank · 1 = Fehlversuch
        42 = Session-Limit (kein Fehlversuch)
#>
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

if (-not (team_lock 'frank')) { exit 1 }

# Zwei-Schwellen-Modell (HM-32): Frank ist ein iterierendes "Sorgenkind" — ein
# Soft-Cap-Ueberlauf ist bei einem normalen Fix NICHT ungewoehnlich und darf
# NICHT die bereits bezahlte Arbeit per Rollback wegwerfen (der alte 1-USD-Cap
# tat genau das und war oekonomisch absurd). Erst der HARD-Cap bricht ab.
$frankBudget = if ($env:ROLE_BUDGET_USD) { $env:ROLE_BUDGET_USD } else { $TEAM_ROLE_BUDGET_USD }
$frankHardcap = if ($env:ROLE_HARDCAP_USD) { $env:ROLE_HARDCAP_USD } else { $TEAM_ROLE_HARDCAP_USD }
$maxVersuche = if ($env:TEAM_FRANK_MAX_VERSUCHE) { [int]$env:TEAM_FRANK_MAX_VERSUCHE } else { 3 }
$logDir = '.team-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$attemptsFile = '.frank-attempts'

# Frank arbeitet Funde ab, die entweder frisch an ihn gingen ODER von Axel mit
# Fix-Plan zurueckkamen. 'Fix-Plan liegt vor' hat Vorrang (Axel hat vorgedacht).
$hm = (Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', 'Fix-Plan liegt vor') 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $hm) {
    $hm = (Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', 'an Frank übergeben') 2>$null)
}
if ($LASTEXITCODE -ne 0 -or -not $hm) {
    [Console]::Out.WriteLine("[frank] Kein Fund mit Status 'an Frank übergeben' / 'Fix-Plan liegt vor' — nichts zu tun.")
    exit 3
}
$hm = ([string]$hm).Trim()

# BL-29: Der Fundblock wird geprueft, BEVOR er Geld kostet. Er ist ein
# maschinenlesbares Dokument, wird aber wie Prosa geschrieben — im Feld nannte
# ein Block die Fundstelle als `pfad::testname`, der Substanz-Anker erkannte
# keine Datei, und Franks inhaltlich KORREKTER Fix wurde zurueckgesetzt und als
# Fehlversuch gezaehlt. Kostenpunkt: ein vollstaendiger Frank-Lauf, fuer einen
# Formfehler im Auftrag. Pruefungen VOR dem bezahlten Aufruf sind die einzigen,
# die den Aufruf noch sparen koennen.
#
# Exit 3 statt 1: Das ist kein Fehlversuch der ROLLE. Der Zaehler bleibt
# unangetastet, der Fund behaelt seinen Status.
Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('lint', $hm)
if ($LASTEXITCODE -ne 0) {
    Team-Fehler "[frank] $hm ist als Auftrag unbrauchbar (siehe oben) — KEIN Aufruf, kein Fehlversuch."
    Team-Fehler '  Der Fundblock gehört nachgebessert (Harry/Marv/Architekt), dann erneut starten.'
    exit 3
}

# Versuchszaehler fuer genau diesen Fund fuehren (Format: "HM-N COUNT").
$versuch = 1
if (Test-Path $attemptsFile) {
    $teile = @((Get-Content -TotalCount 1 $attemptsFile) -split '\s+' | Where-Object { $_ })
    if ($teile.Count -ge 2 -and $teile[0] -eq $hm) { $versuch = [int]$teile[1] + 1 }
}

[Console]::Out.WriteLine("=== Frank: $hm (Versuch $versuch/$maxVersuche, Budget $frankBudget USD) ===")
$out = Join-Path $logDir "frank-$hm-v$versuch-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$startHash = (& git rev-parse HEAD).Trim()

# HM-29/BL-52: Fest "Code-Fix unter site/" vorzuschreiben ist fuer
# Infra-Kaskaden sachlich falsch. Findet das Red Team etwas ausserhalb des
# Produktivcode-Ordners, muss Franks Auftrag den Ort auch nennen duerfen —
# sonst repariert er den Fund am falschen Platz oder gar nicht.
$fixOrte = $TEAM_PRODUKTIVCODE
if ($TEAM_WEITERER_CODE) {
    $fixOrte = "$TEAM_PRODUKTIVCODE (oder, wenn der Fund dort liegt: $TEAM_WEITERER_CODE)"
}
$schritt1 = "Code-Fix unter $fixOrte umsetzen.$SMOKE_SUFFIX"
if ($env:TEAM_REDTEAM_FOCUS) {
    $schritt1 = "Code-Fix im Fokus-Bereich dieser Kaskade umsetzen ($($env:TEAM_REDTEAM_FOCUS)). Betrifft der Fix ${TEAM_PRODUKTIVCODE}, zusätzlich:$SMOKE_SUFFIX"
}

$prompt = @"
$(team_briefing 'frank')

Behebe GENAU den Fund $hm aus $TEAM_BEUTEBUCH (lies dessen Reproschritte).
Falls zu $hm eine Ermittlungsakte unter $TEAM_ERMITTLUNGSAKTEN/ existiert (Axel
hat einen Fix-Plan hinterlegt), folge diesem Plan.

Franks Dreisatz — alle Schritte sind PFLICHT:
0. Reproducer scharfstellen: Die 'Reproducer-Test'-Zeile von $hm nennt eine
   Datei. Fehlt sie, lege sie an; trägt sie einen xfail/Skip-Marker, nimm ihn
   heraus. Gegenprobe: OHNE deinen Fix muss dieser Test ROT sein — fahre ihn
   einmal in diesem Zustand. Ein Fund ohne wirksamen Regressionstest gilt
   nicht als erledigt (BL-22/BL-28).
1. $schritt1
2. Genau EIN Commit: '${TEAM_FIX_PRAEFIX}: <was+warum> ($hm)'.
3. $TEAM_CHANGELOG unter '## [Unreleased]' → '### Fixes' den Fix eintragen (Was+Warum)
   UND den Beutebuch-Status setzen:
   $TEAM_BEUTEBUCH_TOOL set $hm 'erledigt (Frank-Fix, <commit-kurzhash>)'
   (Den CHANGELOG-/Status-Edit im selben oder einem Folge-Commit 'docs: …' sichern.)

Schaffst du einen sauberen Fix inkl. Dreisatz, beende mit exakt:
<promise>FRANK_FIX_COMPLETE</promise>
Sonst gib das Promise NICHT aus und beschreibe das Hindernis.
"@.TrimEnd()

$rcClaude = team_claude 'frank' $TEAM_MODEL_LOOP $out $prompt '--permission-mode' 'bypassPermissions'

[Console]::Out.WriteLine("Frank: $hm Versuch $versuch kostete $TEAM_LAST_COST USD.")

# Session-Pause (HM-24): kein inhaltlicher Fehlversuch — Frank kam nie zum Zug,
# also weder Rollback noch Versuchszaehler noch Axel-Eskalation.
if ($rcClaude -eq 42) {
    Team-Fehler "[frank] Session-Limit — Fix pausiert (Reset: $(if ($TEAM_LAST_RESET) { $TEAM_LAST_RESET } else { 'unbekannt' })). Kein Fehlversuch, Zähler unverändert."
    & git reset --hard $startHash | Out-Null
    & git clean -fd | Out-Null
    exit 42
}

# Zwei-Schwellen-Pruefung (mit hard-limit): 0/1 = ok/Warnschwelle,
# 2 = SOFT-Cap (nur Hinweis, Fix bleibt gueltig — KEIN Rollback, KEIN
# Fehlversuch), 3 = HARD-Cap (echter Ausreisser -> Rollback+Cleanup+Zaehler).
$budgetRc = team_budget_check $TEAM_LAST_COST $frankBudget "Frank $hm" $frankHardcap
$budgetGesprengt = 0
if ($budgetRc -eq 2) {
    Team-Fehler "[frank] Soft-Cap überschritten ($TEAM_LAST_COST USD ≥ $frankBudget USD) — kein Abbruch, Fix wird normal geprüft (Hard-Cap $frankHardcap USD)."
} elseif ($budgetRc -ge 3) {
    Team-Fehler "[frank] HARD-Cap gesprengt ($TEAM_LAST_COST USD ≥ $frankHardcap USD) — Abbruch mit Rollback."
    $budgetGesprengt = 1
}

# Erfolg = Promise + IRGENDEIN neuer fix-Commit im Bereich + Status erledigt.
# Frank darf den CHANGELOG-/Status-Edit laut Prompt in einen 'docs:'-Folgecommit
# legen — deshalb NICHT verlangen, dass HEAD selbst der Fix-Commit ist.
# Ein gesprengtes Budget (HM-30) pruefen wir gar nicht erst auf Erfolg.
if ($budgetGesprengt -eq 0) {
    $neuerStatus = ''
    foreach ($z in @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list'))) {
        $sp = $z -split "`t"
        if ($sp.Count -ge 2 -and $sp[0] -eq $hm) { $neuerStatus = $sp[1] }
    }
    $headJetzt = (& git rev-parse HEAD).Trim()
    $betreffe = @(& git log "$startHash..HEAD" --pretty=%s 2>$null)
    $hatFixCommit = @($betreffe | Where-Object { $_ -and $_.Contains($TEAM_FIX_PRAEFIX) }).Count -gt 0

    if ((team_promise_in $TEAM_LAST_OUT 'FRANK_FIX_COMPLETE') -and
        $headJetzt -ne $startHash -and $hatFixCommit -and
        $neuerStatus -like '*erledigt*' -and
        (team_diff_beruehrt_fund $hm $startHash) -and
        (team_reproducer_liegt_vor $hm)) {
        Remove-Item -Force $attemptsFile -ErrorAction SilentlyContinue
        [Console]::Out.WriteLine("[frank] $hm erledigt (Dreisatz verifiziert).")
        exit 0
    }
    # BL-28: Der Substanz-Anker allein besteht schon, wenn die Produktivdatei im
    # Diff liegt — die reservierte Testdatei muss dafuer nie entstehen. Genau so
    # ging im Feld ein Fix ohne seinen Reproducer als "erledigt" durch. Die
    # Meldung nennt den Fall getrennt, sonst liest er sich wie ein beliebiger
    # Dreisatz-Fehler.
    if (-not (team_reproducer_liegt_vor $hm)) {
        Team-Fehler "[frank] ${hm}: die im Fundblock reservierte Reproducer-Datei existiert nach dem Fix NICHT."
        Team-Fehler '  Ein quittierter Fund ohne wirksamen Regressionstest ist kein erledigter Fund (BL-28).'
    }
}

# Fehlversuch: aufraeumen, zaehlen, ggf. an Axel eskalieren. git clean OHNE
# Pfad-Einschraenkung (HM-29): Frank laeuft mit bypassPermissions und kann auch
# AUSSERHALB des Produktivcode-Ordners neue Dateien anlegen — ein verengter
# Cleanup liess solche Altlasten einen gescheiterten Versuch ueberleben.
Team-Fehler "[frank] $hm Versuch $versuch gescheitert (Budget/Promise/Commit/Dreisatz/Substanzbezug unvollständig) — Rollback."
& git reset --hard $startHash | Out-Null
& git clean -fd | Out-Null
Set-Content -Path $attemptsFile -Value "$hm $versuch" -Encoding ascii

if ($versuch -ge $maxVersuche) {
    Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('set', $hm, 'an Axel übergeben') | Out-Null
    & git add $TEAM_BEUTEBUCH | Out-Null
    & git commit -q -m "docs(beute): $hm nach $versuch Frank-Versuchen an Axel übergeben" | Out-Null
    Remove-Item -Force $attemptsFile -ErrorAction SilentlyContinue
    [Console]::Out.WriteLine("[frank] $hm nach $maxVersuche Versuchen an Axel eskaliert.")
}
exit 1

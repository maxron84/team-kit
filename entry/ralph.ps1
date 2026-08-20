# Bahn: pwsh | Gegenstueck: ralph.sh
<#
  ralph.ps1 — der headless Bau-Loop (Rolle "Ralph", siehe CLAUDE.md).
  Arbeitet den aktiven Kaskaden-Plan Stufe fuer Stufe ab, ein Commit pro Stufe.

  Aufruf:   .\ralph.cmd   (oder ueber .\vollautomatik.cmd als Phase 1)
  Env:      RALPH_BUDGET_USD  Budget pro Stufe (Default TEAM_ROLE_BUDGET_USD=5,
                              sofortiger Hard-Cap — Ralph committet als letzten
                              Schritt und hat danach ohnehin Feierabend)
            TEAM_MODEL_LOOP   Modell (Default sonnet)
            AUTH_MODE         api|abo (siehe team/lib.psm1)
  Exit:     0 = Kaskade fertig/Cap erreicht · 1 = Fehler
            42 = Session-Limit — Stufe pausiert (kein Fehler, State steht)
            43 = Stufe fertig, Quittung fehlt (BL-41): Das Log meldet Erfolg,
                 das Promise fehlt. Arbeit meist FERTIG — nicht neu bauen,
                 sondern pruefen und von Hand quittieren
#>
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

if (-not (team_lock 'ralph')) { exit 1 }

# PLAN_DATEI: der aktive, ausgehaertete Kaskaden-Plan. Zeigt der Strippenzieher
# per Zeiger-Datei .ralph-plan auf den jeweils freigegebenen Plan — Umschalten
# auf die naechste Kaskade ist damit ein Einzeiler.
$planZeiger = '.ralph-plan'
$planDatei = ''
if (Test-Path $planZeiger) {
    $planDatei = ((Get-Content -TotalCount 1 $planZeiger) -replace '\s', '')
}
if (-not $planDatei -or -not (Test-Path $planDatei)) {
    Team-Fehler "FEHLER: Kein aktiver Plan gesetzt: `"$TEAM_PLAN_ORDNER…`" > $planZeiger"
    exit 1
}

# RALPH_CAP: hoechste freigegebene Stufe. Steht als 'RALPH_CAP=<zahl>'-Zeile im
# Kopf des aktiven Plans (setzt DER ARCHITEKT bei der Aushaertung) — einzige
# Quelle, keine Doppelpflege in diesem Skript.
$ralphCap = team_ralph_cap $planDatei
if (-not ($ralphCap -match '^\d+$')) {
    Team-Fehler "FEHLER: Keine gültige RALPH_CAP=-Zeile in $planDatei."
    exit 1
}
$ralphCap = [int]$ralphCap

# Sofortiger Hard-Cap beim zentralen Soft-Cap-Wert (kein Soft-Fenster fuer
# Ralph): team_budget_check wird OHNE hard-limit aufgerufen, ein
# ueberschrittenes Limit liefert 2 und stoppt VOR dem State-Weiterschalten
# (kein Rollback, der Commit der Stufe bleibt — der Mensch schaltet weiter).
$ralphBudget = if ($env:RALPH_BUDGET_USD) { $env:RALPH_BUDGET_USD } else { $TEAM_ROLE_BUDGET_USD }
$stateFile = '.ralph-state'
$logDir = '.ralph-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

while ($true) {
    $stufe = ''
    if (Test-Path $stateFile) { $stufe = ((Get-Content -TotalCount 1 $stateFile) -replace '\s', '') }
    if (-not ($stufe -match '^\d+$')) {
        Team-Fehler "FEHLER: $stateFile enthält keine gültige Stufennummer."
        exit 1
    }
    $stufe = [int]$stufe
    if ($stufe -gt $ralphCap) {
        [Console]::Out.WriteLine("Ralph: Stufe $stufe liegt über RALPH_CAP=$ralphCap — Feierabend.")
        exit 0
    }

    [Console]::Out.WriteLine("=== Ralph: Stufe $stufe (Plan: $planDatei, Budget: $ralphBudget USD) ===")
    $out = Join-Path $logDir "stufe-$stufe-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"

    $prompt = @"
$(team_briefing 'ralph')

Aufgabe: Setze AUSSCHLIESSLICH Stufe $stufe aus $planDatei um.

Regeln:
1. Lies vor Beginn den [Unreleased]-Block in $TEAM_CHANGELOG — dort gelistete
   Fixes NICHT erneut bauen.
2. Keine Features aus späteren Stufen vorwegnehmen.
3. $SMOKE_ZEILE
4. Genau EIN Commit: '$TEAM_FEAT_PRAEFIX(stufe$stufe): <kurzbeschreibung>'.
5. NUR wenn Umsetzung + Verifikation der Stufe vollständig erfüllt sind,
   beende deine Antwort mit exakt: <promise>STUFE_${stufe}_COMPLETE</promise>
   Andernfalls beschreibe, was fehlt, und gib das Promise NICHT aus.
"@.TrimEnd()

    $rc = team_claude 'ralph' $TEAM_MODEL_LOOP $out $prompt '--permission-mode' 'bypassPermissions'
    if ($rc -eq 42) {
        Team-Fehler "Ralph: Session-Limit — Stufe $stufe pausiert (Reset: $(if ($TEAM_LAST_RESET) { $TEAM_LAST_RESET } else { 'unbekannt' })). Kein Fehler, $stateFile bleibt auf $stufe. Bitte später erneut starten."
        exit 42
    } elseif ($rc -ne 0) {
        exit 1
    }

    [Console]::Out.WriteLine("Ralph: Stufe $stufe hat $TEAM_LAST_COST USD gekostet.")

    # BL-60: Der EFFEKT des Caps bleibt unveraendert — die MELDUNG kommt erst
    # nach der Quittungspruefung. Vorher stieg der Cap mit Exit 1 aus, BEVOR die
    # BL-41-Erkennung ueberhaupt lief; eine Stufe, die beides tut (Cap sprengen
    # UND ohne Quittung enden), meldete sich als generischer "Fehler". Das ist
    # kein Randfall: Eine lange Stufe ist teurer UND wartet eher auf einen
    # Hintergrund-Smoke-Test — die Verdeckung trifft bevorzugt die teuren
    # Stufen, bei denen ein unnoetiger Neubau am meisten kostet. Im Feld (K35)
    # trat BL-41 dreimal in einer Kaskade auf; beim dritten Mal (11,09 USD)
    # verdeckte der Cap die Erkennung.
    $budgetRc = team_budget_check $TEAM_LAST_COST $ralphBudget "Ralph Stufe $stufe"
    $capGesprengt = if ($budgetRc -ge 2) { 1 } else { 0 }

    if (team_promise_in $TEAM_LAST_OUT "STUFE_${stufe}_COMPLETE") {
        # Quittung liegt vor: Beim gesprengten Cap bleibt es beim heutigen
        # Verhalten — Stopp OHNE Weiterschalten, der Commit der Stufe bleibt.
        if ($capGesprengt -eq 1) { exit 1 }
        $next = $stufe + 1
        Set-Content -Path $stateFile -Value $next -Encoding ascii
        [Console]::Out.WriteLine("Ralph: Promise erhalten — Stufe $stufe abgeschlossen, weiter mit $next.")
        continue
    }

    # BL-41: Erst pruefen, ob der BENANNTE vierte Ausgang vorliegt (Sitzung
    # beendet, Log meldet Erfolg, Quittung fehlt) — sonst fuehrt die generische
    # Meldung den Menschen in den Plan statt in den Fehlermodus.
    $capZeile = '(Soft-Cap eingehalten.)'
    if ($capGesprengt -eq 1) {
        $capZeile = "ACHTUNG: Soft-Cap ebenfalls überschritten ($TEAM_LAST_COST USD ≥ $ralphBudget USD) — beim Neustart RALPH_BUDGET_USD anheben, sonst stoppt die nächste Stufe genauso."
    }

    # BL-61: Der dritte Ausgang. "Sonst neu bauen" warf zwei sehr verschiedene
    # Lagen zusammen — im Feld haette der Neubau 330 Zeilen fertigen, korrekten
    # Produktivcode weggeworfen (7,46 USD), weil die von der Stufe SELBST
    # geschriebenen Tests drei Aufbaufehler hatten. Gleiches Modell, gleicher
    # Prompt, gleiche Stufe: Der Neubau haette sie erneut erzeugt.
    #
    # Vor der Meldung an den Menschen: die Pruefliste SELBST fahren. Sie ist
    # neunmal im Feld mit demselben Ergebnis ausgegangen. Der gesprengte Cap
    # schliesst das aus — die Automatik darf eine Budget-Entscheidung des
    # Menschen nicht ueberschreiben.
    if ($capGesprengt -eq 0 -and (team_result_meldet_erfolg $TEAM_LAST_OUT) -and
        (team_quittung_selbstpruefung 'ralph' $stufe)) {
        # Committen, falls die Stufe ihre Arbeit uncommittet liegen liess: Ohne
        # Commit liefe die naechste Stufe auf einem schmutzigen Baum, und der
        # Read-Only-Guard der Sweep-Phase saehe fremde Aenderungen.
        if (@(& git status --porcelain | Where-Object { $_ }).Count) {
            & git add -A | Out-Null
            $botschaft = @"
$TEAM_FEAT_PRAEFIX(stufe$stufe): Arbeit der Stufe $stufe, automatisch gesichert

Die Sitzung endete als subtype=success ohne <promise> (BL-41, vierter
Ausgang) und ohne eigenen Commit. Die Selbstpruefung des Loops hat
Arbeit, Zusicherung (BL-135) und gruenen Smoke-Test bestaetigt und
quittiert die Stufe deshalb selbst. Betreff bewusst generisch: Der
Loop kennt den Inhalt der Stufe nicht - der Plan tut es.
"@
            & git commit -q -m $botschaft | Out-Null
            [Console]::Out.WriteLine("Ralph: Stufe $stufe war uncommittet — automatisch gesichert.")
        }
        $next = $stufe + 1
        Set-Content -Path $stateFile -Value $next -Encoding ascii
        [Console]::Out.WriteLine("Ralph: Quittung fehlte (BL-41), Selbstprüfung bestanden — Stufe $stufe abgeschlossen, weiter mit $next.")
        continue
    }

    $smokeHinweis = if ($TEAM_SMOKE_TEST) { $TEAM_SMOKE_TEST } else { '(kein Smoke-Test konfiguriert)' }
    if (team_quittung_fehlt_melden 'ralph' $TEAM_LAST_OUT `
            "Stufe $stufe hat kein <promise>STUFE_${stufe}_COMPLETE</promise> gegeben." `
            'git log -1 && git status — hat Ralph committet?' `
            "$smokeHinweis — ist der Baum grün?" `
            "Beides ja: von Hand quittieren — `"$($stufe + 1)`" > $stateFile, dann erneut starten." `
            "Baum ROT? Erst prüfen, WO: Sind ausschließlich die von DIESER Stufe neu angelegten Testdateien rot (git status zeigt sie als '??'), ist der Testaufbau der wahrscheinlichere Schuldige als der Produktivcode — dann den Aufbau von Hand reparieren, OHNE eine Zusicherung abzuschwächen, statt die Stufe neu zu bauen." `
            'Ist BESTEHENDER Testbestand rot, hat die Stufe etwas gebrochen: dann neu bauen.' `
            $capZeile) {
        exit 43
    }
    Team-Fehler "Ralph: KEIN Promise für Stufe $stufe — Loop stoppt. Log prüfen: $TEAM_LAST_OUT"
    exit 1
}

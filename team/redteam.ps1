# Bahn: pwsh | Gegenstueck: redteam.sh
<#
  redteam.ps1 — gemeinsame Sweep-Logik fuer Harry & Marv (Read-Only Red Team).
  Gegenstueck zu team/redteam.sh. Wird NICHT direkt aufgerufen, sondern von
  harry.ps1 / marv.ps1 mit -Rolle und -Auftrag.

  Eiserne Regel (siehe CLAUDE.md): kein Produktivcode. Schreibrechte nur auf
  Test- und Plan-Ordner — dreifach abgesichert (Prompt, --allowedTools,
  Post-Guard). Der Angreifer committet NICHT selbst; dieses Skript committet
  die Beutebuch-/Test-Aenderungen deterministisch als docs(beute): …

  State: .<rolle>-state = zuletzt gepruefter Commit-Hash. Angriff nur auf
  STABILEN Code (neue Commits seit State).

  Exit: 0 = gearbeitet · 3 = nichts Neues zu pruefen · 1 = Fehler/Guard-Bruch
        42 = Session-Limit — Sweep pausiert (kein Fehler, State steht)

  WARUM -Rolle/-Auftrag STATT DOT-SOURCING: In Bash sourcen harry.sh/marv.sh
  diese Datei, nachdem sie ROLLE und AUFTRAG als Umgebungsvariablen gesetzt
  haben. Das ginge hier auch, ist aber die schlechtere Uebersetzung: Ein
  Aufrufparameter ist eine geprueft vorhandene Zusicherung, eine geerbte
  Variable nur eine Hoffnung — und ein Tippfehler im Namen faellt erst im
  Prompt auf, also nachdem er Geld gekostet hat.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Rolle,
    [Parameter(Mandatory = $true)][string]$Auftrag
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot/..
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

function Gross($s) { if (-not $s) { return $s }; return $s.Substring(0,1).ToUpper() + $s.Substring(1) }

if (-not (team_lock $Rolle)) { exit 1 }

$stateFile = ".$Rolle-state"
$logDir = '.team-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$whitelist = $TEAM_WHITELIST_REDTEAM

$headHash = (& git rev-parse HEAD).Trim()
$last = ''
if (Test-Path $stateFile) { $last = ((Get-Content -Raw $stateFile) -replace '\s', '') }
if ($last -eq $headHash) {
    [Console]::Out.WriteLine("[$Rolle] Kein neuer Commit seit letztem Sweep ($headHash) — nichts zu tun.")
    exit 3
}

$rangeDesc = if ($last) { "Commits $last..$headHash" } else { 'gesamte bisherige Historie' }
[Console]::Out.WriteLine("=== ${Rolle}: Sweep über $rangeDesc ===")
$out = Join-Path $logDir "$Rolle-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$nextId = (Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('next-id')).Trim()

# BL-52: Der Pruefumfang endete bis 2.6.0 an TEAM_PRODUKTIVCODE — einem
# EINZELNEN Ordner. In einer gewachsenen Codebasis liegen Einstiegspunkt und
# Build-Skripte daneben; genau der Code, der als erstes laeuft, wurde nie
# angegriffen, und ein sauberer Sweep las sich trotzdem wie ein sauberes
# Projekt.
$pruefumfang = $TEAM_PRODUKTIVCODE
$tabu = "$TEAM_PRODUKTIVCODE**"
if ($TEAM_WEITERER_CODE) {
    $pruefumfang = "$TEAM_PRODUKTIVCODE sowie $TEAM_WEITERER_CODE"
    $tabu = "$TEAM_PRODUKTIVCODE** und $TEAM_WEITERER_CODE"
}

# BL-31: TEAM_REDTEAM_FOCUS ist eine Umgebungsvariable ohne Verfallsdatum. Im
# Feld lief der erste Sweep der Kaskade 11 mit dem Fokus aus Kaskade 10 und
# pruefte pflichtgemaess Leveldesign, waehrend der Commit-Bereich etwas ganz
# anderes enthielt; beide Funde betrafen alte Level, keiner den tatsaechlichen
# Bau. Die Kaskade war formal abgehakt und inhaltlich ungeprueft.
#
# Der Fokus wird deshalb an den LAUF gebunden statt an die Prozessumgebung.
$focusState = ".team-focus-$Rolle"
$fokus = $env:TEAM_REDTEAM_FOCUS
if ($fokus) {
    Set-Content -Path $focusState -Value "$headHash`n$fokus" -NoNewline -Encoding utf8
} elseif (Test-Path $focusState) {
    $zeilen = @(Get-Content $focusState)
    if ($zeilen.Count -ge 1 -and $zeilen[0] -eq $headHash) {
        $fokus = ($zeilen | Select-Object -Skip 1) -join "`n"
    } else {
        Team-Fehler "[$Rolle] Der zuletzt gesetzte Fokus gehört zu einem anderen Stand ($($zeilen[0])) — VERFALLEN (BL-31)."
        Team-Fehler "  Dieser Sweep läuft mit dem Grundauftrag. Für eine gezielte Prüfung TEAM_REDTEAM_FOCUS neu setzen."
        Remove-Item -Force $focusState -ErrorAction SilentlyContinue
    }
}

if ($fokus) {
    $scopeLine = "Prüfe den STABILEN Code im folgenden Fokus-Bereich ($rangeDesc): $fokus"
} else {
    $scopeLine = "Prüfe den STABILEN Code der App unter $pruefumfang ($rangeDesc)."
}

# BL-39: Zwei Fragen, die im Feld getragen haetten und in keinem Auftrag standen.
$kontrollflussZeile = @"
Zwei Fragen, die zum Auftrag gehören und die ein Verhaltensvergleich NICHT beantwortet:
- Welche Zeilen LIEFEN vorher und laufen jetzt nicht mehr? Vergleiche den
  Kontrollfluss, nicht nur die Rümpfe — ein 'return', das zu einem 'break'
  wurde, sieht Zeile für Zeile harmlos aus und überspringt trotzdem alles, was
  nach der Schleife stand.
- Was hängt SONST NOCH an einer Bedingung, die dieser Lauf mitbenutzt? Zähle
  die Nutzer eines mitbenutzten Guards durch, statt es dir vorzunehmen: Eine
  Kopplung, die vorher nur eine Bedeutung hatte, ist im Bestand unsichtbar.
"@.TrimEnd()

# BL-51: Test- und Plan-Ordner sind die einzigen Pfade, die diese Rolle
# schreiben darf — zog das Team in eine gewachsene Codebasis ein, liegt dort
# fremdes Eigentum, auf das der Guard NICHT anschlaegt. Der Prompt ist die
# einzige Stelle, an der die Grenze ueberhaupt gezogen werden kann.
$bestandZeile = ''
if ($TEAM_PLAN_ORDNER_BESTAND -or $TEAM_TEST_ORDNER_BESTAND) {
    $planTeil = if ($TEAM_PLAN_ORDNER_BESTAND) { " (${TEAM_PLAN_ORDNER}: $TEAM_PLAN_ORDNER_BESTAND)" } else { '' }
    $testTeil = if ($TEAM_TEST_ORDNER_BESTAND) { " (${TEAM_TEST_ORDNER}: $TEAM_TEST_ORDNER_BESTAND)" } else { '' }
    $bestandZeile = @"

BESTAND — NICHT DEIN EIGENTUM: In deinen Schreibordnern lagen beim Einzug des Teams
schon fremde Dateien$planTeil$testTeil.
Du legst dort NUR NEUE Dateien an. Du änderst und löschst nichts, was du nicht
selbst angelegt hast — auch nicht, was in dieser Aufzählung fehlt. Der Guard
lässt dich hier gewähren; die Grenze hältst du selbst.

"@
}

$prompt = @"
$(team_briefing $Rolle)

Auftrag: $Auftrag
$scopeLine

$kontrollflussZeile

EISERNE REGEL: Du änderst NIEMALS Produktivcode ($tabu). Schreiben NUR unter
$TEAM_TEST_ORDNER (Reproducer, klar als xfail/Skip markiert) und $TEAM_PLAN_ORDNER. Du committest NICHT.
$bestandZeile

Führe KEINE Reproducer/Skripte aus und stelle KEINE Rückfrage zum Ausführen —
du bist strikt read-only (der Guard erzwingt das ohnehin). Dokumentiere
Reproschritte ALS TEXT, statt sie laufen zu lassen.

Jeder Fund kommt ins Beutebuch $TEAM_BEUTEBUCH — hänge unter '## Funde' einen
Block an (nächste freie Nummer beginnt bei $nextId):
### HM-<Nr> — <Kurztitel>
- **Angreifer**: $(Gross $Rolle)
- **Schweregrad**: kritisch|hoch|mittel|klein
- **Status**: an Frank übergeben
- **Reproschritte**: 1. … 2. …
- **Erwartung**: …
- **Realität**: …

Was in $TEAM_TEST_ORDNER liegen bleibt, braucht einen Namen und einen Fund
(BL-47): Ein Hilfs-/Sondenskript ohne zugehörigen Fund LÖSCHST du wieder,
bevor du fertig meldest — oder du benennst es als Reproducer nach seinem Fund
(test_hm<Nr>_<stichwort>). Eine namenlose Datei im Test-Ordner wird nie wieder
gelesen, ist von keinem Fundblock referenziert und fällt trotzdem unter die
Zusicherungen des Projekts.

Findest du NICHTS, ändere keine Datei.
Beende IMMER mit exakt: <promise>REDTEAM_SWEEP_COMPLETE</promise> — AUCH WENN
du einen Fund ins Beutebuch geschrieben hast; das Promise ist die
Sweep-Quittung, nicht der Fund-Beleg.
"@.TrimEnd()

$allowedTools = team_allowed_tools 'redteam'
team_guard_begin | Out-Null
$rc = team_claude $Rolle $TEAM_MODEL_LOOP $out $prompt `
        '--permission-mode' 'default' '--allowedTools' $allowedTools

# Linie 3: harte Durchsetzung der Read-Only-Grenze (chirurgisch). Laeuft AUF
# JEDEM Pfad — auch 42-Pause und generischer Fehler (HM-18): team_claude ist
# kein atomarer Vorgang, Teil-Session-Seiteneffekte koennen bereits VOR einem
# Abbruch im Arbeitsverzeichnis liegen. BL-16 Ebene 2: Das Urteil faellt unten.
$guardUebergriff = 0
if (-not (team_guard_verify $Rolle $whitelist)) { $guardUebergriff = 1 }

if ($rc -eq 42) {
    # HM-27: Der Guard oben resettet nur Pfade AUSSERHALB der Whitelist — ein
    # bereits geschriebener Beutebuch-Eintrag INNERHALB der Schreibzone bliebe
    # sonst als impliziter, nie verifizierter Fortschritt liegen.
    Team-Fehler "[$Rolle] Session-Limit — Sweep pausiert (Reset: $(if ($TEAM_LAST_RESET) { $TEAM_LAST_RESET } else { 'unbekannt' })). Kein Fehler, $stateFile bleibt unverändert; halbfertige $TEAM_TEST_ORDNER/$TEAM_PLAN_ORDNER-Seiteneffekte werden verworfen."
    # BL-114: wie in axel.ps1 — der `git clean` war eingeschraenkt, das
    # `git reset --hard` daneben nicht. Jetzt derselbe chirurgische Weg.
    team_rollback_rolle $Rolle $headHash | Out-Null
    exit 42
} elseif ($rc -ne 0) {
    Team-Fehler "[$Rolle] Aufruf fehlgeschlagen."
    exit 1
}

# Budget: Harry/Marv sind read-only → sofortiger Hard-Cap beim zentralen
# Soft-Cap-Wert, KEIN Soft-Fenster (team_budget_check ohne hard-limit, HM-32).
$rolleBudget = if ($env:ROLE_BUDGET_USD) { $env:ROLE_BUDGET_USD } else { $TEAM_ROLE_BUDGET_USD }
$budgetRc = team_budget_check $TEAM_LAST_COST $rolleBudget "$(Gross $Rolle) Sweep"

# BL-30: Der Deckel vernichtete die QUITTUNG, nicht die Arbeit — und liess damit
# genau das Einzige fallen, was er beschaedigen kann. "read-only, es geht nichts
# Bezahltes verloren" stimmt fuer die FUNDE (die liegen uncommittet im Baum),
# nicht fuer den Zustandszeiger: Im Feld meldete Marvs Sweep is_error=false,
# Promise gesetzt und zwei sauber formatierte Funde — und wurde wegen
# 6,52 >= 5,00 abgebrochen. Der State blieb stehen, ein Neustart haette dieselben
# 22 Commits ein zweites Mal geprueft und ein zweites Mal bezahlt.
$budgetUeberschritten = 0
if ($budgetRc -ge 2) {
    if ((team_result_meldet_erfolg $TEAM_LAST_OUT) -and
        (team_promise_in $TEAM_LAST_OUT 'REDTEAM_SWEEP_COMPLETE')) {
        $budgetUeberschritten = 1
        Team-Fehler "[$Rolle] Budget-Cap überschritten ($TEAM_LAST_COST USD ≥ $rolleBudget USD) — der Aufruf war aber nachweislich erfolgreich (Promise + sauberes Log)."
        Team-Fehler "  Der Fortschritt wird gebucht; der Deckel verhindert den NÄCHSTEN Aufruf, nicht diesen (BL-30)."
    } else {
        Team-Fehler "[$Rolle] Budget-Hard-Cap überschritten — Abbruch (kein vollständiges Ergebnis; $stateFile bleibt unverändert)."
        exit 1
    }
}

if (-not (team_promise_in $TEAM_LAST_OUT 'REDTEAM_SWEEP_COMPLETE')) {
    # Defensiv (BL-16): Fehlt das Promise, zaehlt ein sauberer NEUER
    # Beutebuch-Eintrag als erfolgreicher Sweep — der Dreisatz (Fund im
    # Beutebuch) ist die eigentliche Quittung, das Promise nur eine
    # (hier fehlende) Zusatzbestaetigung.
    $neuerFund = 0
    if (@(& git status --porcelain -- $TEAM_BEUTEBUCH | Where-Object { $_ }).Count) { $neuerFund = 1 }
    if ((Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('next-id')).Trim() -ne $nextId) { $neuerFund = 1 }
    if ($neuerFund -eq 0) {
        Team-Fehler "[$Rolle] Kein Sweep-Promise und kein neuer Fund — Log prüfen: $TEAM_LAST_OUT"
        exit 1
    }
    Team-Fehler "[$Rolle] WARNUNG: Sweep ohne Promise, aber sauberer Fund übergeben — als Erfolg gewertet. Log: $TEAM_LAST_OUT"
}

# BL-16 Ebene 2: Das Ergebnis des Sweeps ist die Quittung. Wer hier ankommt, hat
# sie geliefert; ein Guard-Uebergriff kassiert dann den Uebergriff, nicht den Sweep.
if (-not (team_guard_urteil $Rolle $guardUebergriff 1)) { exit 1 }

# BL-47 (Feld K29): Das ERGEBNIS zaehlen, nicht die Absicht behaupten. Ein
# Marv-Sweep ueber 9 Minuten und 3,14 USD committete eine einzige Sondendatei
# und keine Beutebuch-Zeile — Commit-Botschaft trotzdem "neue Funde/Reproducer".
# Damit ist "geprueft, nichts gefunden" von "nie fertig geworden" nicht mehr zu
# unterscheiden: Beides kostet gleich viel und sieht identisch aus.
$nextIdNachher = (Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('next-id')).Trim()
$neueFunde = [int]($nextIdNachher -replace '^HM-') - [int]($nextId -replace '^HM-')
if ($neueFunde -lt 0) { $neueFunde = 0 }
$fundText = if ($neueFunde -eq 1) { '1 neuer Fund' }
            elseif ($neueFunde -gt 1) { "$neueFunde neue Funde" }
            else { 'keine neuen Funde' }

# Whitelist-Aenderungen deterministisch committen (der Angreifer darf nicht).
Set-Content -Path $stateFile -Value $headHash -Encoding ascii
if (@(& git status --porcelain -- $TEAM_BEUTEBUCH $TEAM_TEST_ORDNER | Where-Object { $_ }).Count) {
    & git add $TEAM_BEUTEBUCH $TEAM_TEST_ORDNER | Out-Null
    & git commit -q -m "docs(beute): $(Gross $Rolle)-Sweep über $rangeDesc — $fundText" 2>&1 | Out-Null
    if ($neueFunde -eq 0) {
        # Der benannte Fall: geprueft, nichts gefunden — committet sind nur
        # Testdateien. Nicht "Funde committet", das war die Luege im Feld.
        [Console]::Out.WriteLine("[$Rolle] Geprüft, KEINE neuen Funde ($TEAM_LAST_COST USD) — committet sind nur $TEAM_TEST_ORDNER-Dateien. Keine Übergabe an Frank.")
    } else {
        [Console]::Out.WriteLine("[$Rolle] $fundText committet ($TEAM_LAST_COST USD). Übergabe an Frank.")
    }
} else {
    [Console]::Out.WriteLine("[$Rolle] Geprüft, keine neuen Funde ($TEAM_LAST_COST USD). Sauber, nichts zu committen.")
}
# BL-30: Die Ueberschreitung bleibt die letzte Zeile des Laufs.
if ($budgetUeberschritten -eq 1) {
    Team-Fehler "[$Rolle] ERINNERUNG: Dieser Sweep lag über dem Cap ($TEAM_LAST_COST USD ≥ $rolleBudget USD). Fortschritt ist gebucht, der nächste Aufruf ist gedeckelt."
}
exit 0

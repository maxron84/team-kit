# Bahn: pwsh | Gegenstueck: vollautomatik.sh
<#
  vollautomatik.ps1 — der Vollautomatik-Orchestrator: faehrt eine komplette
  Kaskade durch. Ralph baut -> Red Team greift an -> Frank fixt -> Axel knackt
  die harten Faelle -> Abschlussbericht.

  Aufruf:  .\vollautomatik.cmd            (nimmt einen abgebrochenen Lauf bei
                                         der abgebrochenen PHASE wieder auf,
                                         BL-217)
           .\vollautomatik.cmd --von-vorn (verwirft den Phasen-Zeiger und
                                         beginnt bei Phase 1)
           .\vollautomatik.cmd --hilfe    (diesen Kopf ausgeben; auch --help, -h)
  Env:     TEAM_MAX_RUNDEN   Fix-Runden Frank/Axel (Default 12).
           TEAM_REDTEAM_FOCUS_2  bestellt einen ZWEITEN Sweep-Durchgang je
                                        Angreifer mit eigenem Fokus ueber
                                        denselben Bau (BL-296) — fuer eine
                                        grosse Kaskade; ohne ihn ein Durchgang.
           TEAM_VOLLAUTOMATIK_AB_PHASE  1 wirkt wie --von-vorn (BL-217);
                                        2, 3 oder 4 startet dort (4 = nur die
                                        Fix-Phase, wie fixphase); alles andere
                                        bricht ab (BL-241).
           TEAM_FIX_MAX_STAGNATION  Auslauf-Bremse (Default =
                             TEAM_FRANK_MAX_VERSUCHE, sonst 3): bricht Phase 4
                             ab, sobald so viele Runden IN FOLGE weder einen
                             Frank-Fix noch eine neue Axel-Akte noch eine
                             Beutebuch-Statusaenderung gebracht haben.
                             Muss >= TEAM_FRANK_MAX_VERSUCHE bleiben, sonst
                             greift die Bremse VOR Franks eigener Eskalation
                             an Axel.
           TEAM_BUDGET_USD   Deckel fuer DIESEN Lauf (Default 50, BL-304) — die harte
                             Durchsetzung misst nur die Kosten dieses einen
                             Laufs (A), nicht den lebenslangen Kontostand.
  Exit:    0 = Lauf durch · 1 = echter Fehler (inkl. Stagnation)
           43 = Stufe/Fix fertig, Quittung fehlt (BL-41, von ralph.ps1 und —
                seit BL-214 — von frank.ps1 durchgereicht): kein Neubau, kein
                Neustart — pruefen und von Hand quittieren
           42 = Session-Limit oder Abo-Anmeldung abgelaufen — Lauf pausiert (kein Fehler, State steht)

  Sequenziell und sperrgesichert. Haelt die Sperre ueber den ganzen Lauf und
  gibt sie an die Kind-Skripte weiter (TEAM_LOCK_HELD=1), damit die sich nicht
  selbst aussperren.
#>
# Bewusst KEIN 'Stop': Ein Rollen-Exit 3 ("nichts zu tun") ist der Normalfall
# und darf den Orchestrator nicht wegreissen — das Gegenstueck zu `set -uo
# pipefail` OHNE -e in der Bash-Fassung.
$ErrorActionPreference = 'Continue'
# BL-122: Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
# standardmaessig $true — ein Exit-Code != 0 aus einem NATIVEN Befehl ist damit
# ein TERMINIERENDER Fehler und nicht mehr nur ein Wert in $LASTEXITCODE. Diese
# Bahn ist durchgehend fuer den klassischen Vertrag geschrieben: aufrufen,
# $LASTEXITCODE lesen, entscheiden. Ohne diese Zeile ist jede dieser
# Entscheidungen unerreichbar — der Abbruch kommt vorher.
$PSNativeCommandUseErrorActionPreference = $false
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

if (-not (team_lock 'vollautomatik')) { exit 1 }

# HM-32: Warn-Guard im EIGENEN Prozess seeden, BEVOR die erste Rolle startet —
# die Rollen laufen als GESCHWISTER-Prozesse, ein im Kind gesetzter Guard
# erreicht sie nie (analog team_lock/TEAM_LOCK_HELD). Nur im Abo-Modus
# relevant; im reinen api-Modus ist der Key legitim.
if ((team_auth_mode_effektiv 'abo') -eq 'abo') { team_warnung_abo_key | Out-Null }

$vonVorn = $false
foreach ($arg in $args) {
    if ($arg -eq '--von-vorn') { $vonVorn = $true }
    elseif ($arg -in @('--hilfe', '--help', '-h')) {   # BL-223
        Team-HilfeKopf $PSCommandPath
        exit 0
    }
    else {
        [Console]::Error.WriteLine("Unbekannte Option: $arg — erlaubt: --von-vorn, --hilfe")
        exit 2
    }
}
# BL-241: Der Name verspricht "ab Phase N" — bis hierher galt nur '1', und
# '4' wurde STILL ignoriert: Der naheliegende Griff fuer "nur fixen" fuehrte
# lautlos zum teuersten Ergebnis, einem vollen Lauf samt zwei Sweeps. Jetzt
# gelten 1 bis 4 (4 = nur die Fix-Phase, so startet fixphase.ps1), und ein
# unbekannter Wert bricht ab, statt bei Phase 1 zu beginnen.
$abPhaseAnsage = 0
switch ("$env:TEAM_VOLLAUTOMATIK_AB_PHASE") {
    '' { break }
    '1' { $vonVorn = $true; break }
    { $_ -in @('2', '3', '4') } { $abPhaseAnsage = [int]$_; break }
    default {
        [Console]::Error.WriteLine("TEAM_VOLLAUTOMATIK_AB_PHASE='$env:TEAM_VOLLAUTOMATIK_AB_PHASE' — erlaubt sind 1 bis 4 (1 = von vorn, 4 = nur die Fix-Phase, wie .\fixphase.cmd). Kein Lauf gestartet (Kit-BL-241).")
        exit 2
    }
}

$maxRunden = if ($env:TEAM_MAX_RUNDEN) { [int]$env:TEAM_MAX_RUNDEN } else { 12 }
# HM-31: Default an TEAM_FRANK_MAX_VERSUCHE koppeln (statt fest 2), sonst
# bricht die Bremse regelmaessig VOR Franks eigener Eskalation an Axel ab.
$stagnationMax = if ($env:TEAM_FIX_MAX_STAGNATION) { [int]$env:TEAM_FIX_MAX_STAGNATION }
                 elseif ($env:TEAM_FRANK_MAX_VERSUCHE) { [int]$env:TEAM_FRANK_MAX_VERSUCHE }
                 else { 3 }
$budgetUserGesetzt = if ($env:TEAM_BUDGET_USD) { '1' } else { '0' }
$budgetUsd = if ($env:TEAM_BUDGET_USD) { $env:TEAM_BUDGET_USD } else { '50' }
$logDir = '.team-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$laufLog = Join-Path $logDir "vollautomatik-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
# Startzeitpunkt dieses Laufs — die Pro-Lauf-Durchsetzung zaehlt nur Logs, die
# seither entstanden sind (BL-18). 1 s Puffer gegen Sekunden-Rundung.
$laufStart = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - 1

function Log {
    # Alles doppelt: Konsole + Lauf-Log (team-status liest die letzten Zeilen).
    # In Bash macht das ein `exec > >(tee …)`; PowerShell kennt keine
    # Prozess-Substitution, also schreibt der Helfer selbst zweimal.
    param([string]$Text)
    $zeile = "[$(Get-Date -Format 'HH:mm:ss')] $Text"
    [Console]::Out.WriteLine($zeile)
    Add-Content -LiteralPath $laufLog -Value $zeile -Encoding utf8
}

function Rolle-Starten {
    <#
      Startet ein Rollen-Skript in einem EIGENEN PROZESS und spiegelt seine
      Ausgabe ins Lauf-Log. Gibt den Exit-Code zurueck.

      WARUM EIN EIGENER PROZESS UND NICHT `& ./ralph.ps1`:
      Zwei Gruende, und der zweite ist der zwingende.

      1. Es ist die treue Uebersetzung. In Bash ist `./ralph.sh` ein
         Subprozess; TEAM_LOCK_HELD wird ueber die Umgebung vererbt, und genau
         darauf beruht, dass die Rollen sich unter der Vollautomatik nicht
         selbst aussperren.
      2. Die Rollen schreiben ihre Meldungen mit [Console]::Out.WriteLine —
         das muss so sein, weil eine Bibliotheksfunktion sonst ihre Diagnose in
         den eigenen Rueckgabewert schreibt. Diese Ausgabe geht am
         PowerShell-Ausgabestrom VORBEI, direkt auf den Prozess-Stdout, und ist
         mit `&` und `2>&1` NICHT einzufangen. Das Lauf-Log haette dann nur die
         Zeilen des Orchestrators enthalten — und team-status.ps1 zeigt genau
         dessen letzte drei Zeilen an. Bei einem externen Prozess faengt
         PowerShell den Stdout dagegen vollstaendig.
    #>
    param([string]$Skript, [string[]]$Argumente = @())
    # BL-181: STREAMEN statt SAMMELN — und das ist keine Feinheit.
    #
    # Die Fassung davor lautete `$ausgabe = & pwsh … 2>&1` mit einer
    # foreach-Schleife danach. Die Zuweisung sammelt den KOMPLETTEN
    # Kindprozess ein, bevor die erste Zeile herauskommt; Konsole UND Lauf-Log
    # hingen in derselben Schleife und blieben deshalb beide stumm.
    #
    # Gemessen im Feld (`Feld B`, 66-Minuten-Lauf, Takt 15 s gegen die Spuren
    # auf der Platte): Das Lauf-Log stand 26 Minuten lang bei 53 Bytes — der
    # einen Zeile, die der Orchestrator VOR dem ersten Kindprozess geschrieben
    # hat — waehrend .ralph-state von 10 auf 16 lief, sieben Stufen gebaut,
    # verifiziert und committet wurden. Dann sprang es auf 1672 Bytes: 31
    # Zeilen auf einen Schlag. Jeder Sprung lag exakt auf einem Rollenende.
    #
    # Die Puffergrenze ist also der KINDPROZESS. Die Bau-Rolle ist ein Aufruf
    # fuer alle Stufen und belegte 40 der 66 Laufminuten — 61 % des Laufs in
    # einem einzigen stummen Block. Ein Lauf ohne Lebenszeichen ist von einem
    # haengenden nicht zu unterscheiden, und die naheliegende Reaktion darauf
    # ist die teuerste: Der Abbruch wirft bezahlte Stufen weg. Dieselbe Lehre
    # wie BL-176/BL-179, hier an der Stelle, die am laengsten schweigt.
    #
    # Die zweite Haelfte des Schadens war team-status.ps1: Es zeigt "die
    # letzten 3 Zeilen" des Lauf-Logs — waehrend des Laufs gab es sie nicht.
    # Das Monitoring-Werkzeug war genau in dem Zeitraum blind, fuer den man es
    # aufruft, und zeigte dabei keinen Fehler, sondern eine stundenalte Zeile,
    # die aussah wie die aktuelle.
    #
    # BL-248: Auf das KIND warten, nicht auf die Leitung. Die Fassung davor
    # streamte ueber eine Pipeline — und eine Pipeline endet erst bei EOF, also
    # wenn JEDER Prozess das geerbte Schreibende losgelassen hat, auch Enkel.
    # Im Feld hinterliess eine Bau-Rolle ein electron.exe mit modalem
    # Fehlerdialog: Ralph loggte "Feierabend", danach stand der Orchestrator
    # NEUN STUNDEN ohne einen einzigen Kindprozess, hielt die Sperre, und
    # team-status zeigte "Feierabend" — die Anzeige log in Richtung "laeuft".
    # Der Zustand hatte als einziger keinen Ausgang.
    #
    # Jetzt liest diese Funktion beide Stroeme zeilenweise und asynchron mit
    # (gestreamt wie seit BL-181) und misst, was gesucht ist: ob das KIND
    # fertig ist. Liefert die Leitung nach dem Ende des Kindes drei Sekunden
    # lang nichts mehr und ist doch nicht zu, haelt ein Nachfahre sie offen —
    # dann wird das gemeldet und NICHT weiter gewartet.
    $psi = [System.Diagnostics.ProcessStartInfo]::new([System.Environment]::ProcessPath)
    foreach ($a in @('-NoProfile', '-File', $Skript) + @($Argumente)) {
        $psi.ArgumentList.Add([string]$a)
    }
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $utf8 = [System.Text.UTF8Encoding]::new($false)
    $psi.StandardOutputEncoding = $utf8
    $psi.StandardErrorEncoding = $utf8
    $psi.WorkingDirectory = (Get-Location).ProviderPath
    $kind = [System.Diagnostics.Process]::Start($psi)
    $leser = @($kind.StandardOutput, $kind.StandardError)
    $offen = @($leser[0].ReadLineAsync(), $leser[1].ReadLineAsync())
    $kindEnde = $null
    $leitungHaengt = $false
    while ($offen[0] -or $offen[1]) {
        $etwas = $false
        for ($k = 0; $k -lt 2; $k++) {
            $aufgabe = $offen[$k]
            if ($aufgabe -and ($aufgabe.IsFaulted -or $aufgabe.IsCanceled)) {
                $offen[$k] = $null      # Leitung abgerissen: wie EOF behandeln
                $etwas = $true
                continue
            }
            if ($aufgabe -and $aufgabe.IsCompleted) {
                $text = $aufgabe.Result
                if ($null -eq $text) {
                    $offen[$k] = $null
                } else {
                    [Console]::Out.WriteLine($text)
                    Add-Content -LiteralPath $laufLog -Value $text -Encoding utf8
                    $offen[$k] = $leser[$k].ReadLineAsync()
                }
                $etwas = $true
            }
        }
        if ($etwas) { continue }
        if ($kind.HasExited) {
            if (-not $kindEnde) { $kindEnde = [DateTime]::UtcNow }
            elseif (([DateTime]::UtcNow - $kindEnde).TotalSeconds -ge 3) {
                $leitungHaengt = $true
                break
            }
        }
        Start-Sleep -Milliseconds 50
    }
    $kind.WaitForExit()
    $code = $kind.ExitCode
    if ($leitungHaengt) {
        $text = "[vollautomatik] $(Split-Path -Leaf $Skript) ist beendet (Exit $code), aber ein Prozess, den die Rolle gestartet hat, haelt ihre Ausgabe noch offen — etwa ein Fenster mit Fehlerdialog. Der Lauf wartet NICHT darauf (Kit-BL-248); den Prozess bitte von Hand pruefen."
        [Console]::Out.WriteLine($text)
        Add-Content -LiteralPath $laufLog -Value $text -Encoding utf8
    }
    return $code
}

# --- Zwei bewusst getrennte Kennzahlen (BL-18) --------------------------------
# A) Lauf-Kosten — NUR DIESER Lauf. Das ist die operative Grenze, gegen die der
#    Pro-Lauf-Deckel durchgesetzt wird. Vorher (BL-17) mass die Durchsetzung
#    faelschlich den lebenslangen Kontostand — dadurch stoppte die Automatik,
#    sobald die Lebenssumme die Empfehlung ueberstieg, noch bevor der aktuelle
#    Lauf ueberhaupt etwas gekostet hatte.
# B) Kontostand — lebenslange Summe. Reine ANZEIGE, NIE Durchsetzung.
#
# Die Archiv-Unterordner zaehlen bei A BEWUSST mit: Eine Abschluss-Stufe
# INNERHALB des Laufs kann die Logs nach archiv/ wegraeumen. Ohne die
# Archivpfade fiele das bereits ausgegebene Geld mitten im Lauf aus der Messung
# — real erlebt (Kaskade 22): nach Stufe 93 sank der gemessene Lauf von 26.42
# auf 6.16 USD, also GENAU bevor die offene Fix-Phase startete.
function Lauf-Kosten {
    team_kosten_seit $laufStart @('.ralph-logs', '.team-logs', '.ralph-logs/archiv', '.team-logs/archiv')
}
function Kontostand-Gesamt { team_kontostand_gesamt }

# --- Deckel-Governance: Empfehlung nur ANHEBEN, nie senken --------------------
# Eine explizite TEAM_BUDGET_USD-Uebersteuerung durch den Menschen hat immer
# Vorrang. team_resolve_budget_cap kapselt die Regel isoliert testbar.
$empfehlung = team_budget_empfehlung
$neuerDeckel = team_resolve_budget_cap $budgetUsd $budgetUserGesetzt $empfehlung
if ($neuerDeckel -ne $budgetUsd) {
    Log "Deckel-Anhebung: Architekten-Empfehlung $empfehlung USD > bisheriger Deckel $budgetUsd USD — automatisch übernommen. Gesamt-Kontostand $(Kontostand-Gesamt) USD -> neuer Lauf-Deckel $neuerDeckel USD."
    $budgetUsd = $neuerDeckel
}
# BL-185: Die Gegenrichtung. Die Entscheidung selbst liegt in
# team_budget_cap_hinweis (team/lib.psm1) — isoliert testbar, aus demselben
# Grund wie team_resolve_budget_cap daneben.
else {
    foreach ($zeile in @(team_budget_cap_hinweis $budgetUsd $budgetUserGesetzt $empfehlung)) {
        if ($zeile) { Log $zeile }
    }
}

# BL-23: Das KULANZBAND der Fixphase. Der Deckel greift NACH dem bereits
# bezahlten Aufruf und kennt die Restarbeit nicht — er kann eine Fixphase
# mitten zwischen "Fund an Frank uebergeben" und "Fix liegt vor" kappen. Genau
# das ist im Feld eingetreten: Lauf bei 19,96 von 19 USD gestoppt, ein Fund vom
# Schweregrad HOCH offen zurueckgelassen. Die fehlende Restarbeit kostete
# 1,52 USD; dagegen standen Handstart, zweiter Kontextaufbau,
# Architekten-Nachfrage und ein ueber zwei Sitzungen zerfallener Closeout. Der
# Stopp hat weniger gespart, als sein eigenes Aufraeumen kostete.
$kulanzProzent = if ($env:TEAM_BUDGET_KULANZ_PROZENT) { [double]$env:TEAM_BUDGET_KULANZ_PROZENT } else { 15.0 }
$script:KulanzGewaehrt = 0

function Budget-Ok {
    param([switch]$Kulanz)
    $jetzt = [double](Lauf-Kosten)
    $deckel = [double]::Parse($budgetUsd, [cultureinfo]::InvariantCulture)
    if ($jetzt -lt $deckel) { return $true }

    if ($Kulanz -and $script:KulanzGewaehrt -eq 0) {
        Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', 'an Frank übergeben') 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $deckelKulant = $deckel * (1 + $kulanzProzent / 100)
            if ($jetzt -lt $deckelKulant) {
                $script:KulanzGewaehrt = 1
                Log "LAUF-BUDGET erreicht ($jetzt USD >= $budgetUsd USD), aber ein Fund ist in Bearbeitung — die angefangene Runde laeuft im Kulanzband bis $deckelKulant USD zu Ende (+$kulanzProzent %, Kit-BL-23). DANACH harter Stopp."
                return $true
            }
        }
    }
    Log "LAUF-BUDGET erreicht: dieser Lauf $jetzt USD >= Deckel $budgetUsd USD — harter Stopp (Gesamt-Kontostand $(Kontostand-Gesamt) USD, nur Anzeige)."
    return $false
}

# --- Phasen-Zeiger (BL-217) ---------------------------------------------------
# Wortgleiche Bauart wie in der bash-Fassung; die Begruendung steht dort
# ausfuehrlich. Kurz: Das Skript war phasen-ZUSTANDSLOS, ein in Phase 4
# abgebrochener Lauf begann beim Fortsetzen wieder bei Phase 1 und kaufte zwei
# Red-Team-Sweeps ueber Franks eigene Fix-Commits (im Feld 2,2653 USD, null
# Funde, 27 % der Fixphasen-Kosten) — waehrend der Abbruchbericht woertlich das
# Gegenteil versprach. Der Zeiger gilt nur, solange Plan-Zeiger UND Ralphs
# Stufenstand unveraendert sind, und faellt sonst auf Phase 1 zurueck: Ein
# veralteter Zeiger darf niemals einen Bau ueberspringen.
$phasenState = '.vollautomatik-state'
$abPhase = 1

function Phasen-Lage {
    # .Trim() ist Pflicht, nicht Kosmetik: `-Raw` liefert den abschliessenden
    # Zeilenumbruch mit, und der wuerde den ZWEIZEILIGEN Zustand sprengen —
    # die Lage stuende dann ueber drei Zeilen und passte nie wieder.
    $plan = if (Test-Path -LiteralPath '.ralph-plan') {
        (Get-Content -LiteralPath '.ralph-plan' -Raw).Trim() } else { '-' }
    $stand = if (Test-Path -LiteralPath '.ralph-state') {
        (Get-Content -LiteralPath '.ralph-state' -Raw).Trim() } else { '-' }
    return "$plan|$stand"
}

function Phasen-Name {
    param([int]$Nr)
    switch ($Nr) {
        1 { 'Phase 1 (Ralph)' }
        2 { 'Phase Red Team (harry)' }
        3 { 'Phase Red Team (marv)' }
        4 { 'Phase 4 (Fix-Runden)' }
        default { "Phase $Nr" }
    }
}

function Phasen-Naechste {
    param([int]$Nr)
    Set-Content -LiteralPath $phasenState -Encoding UTF8 `
        -Value @("$Nr", (Phasen-Lage))
}

function Phasen-Faellig {
    param([int]$Nr)
    return ($Nr -ge $script:abPhase)
}

function Phasen-Zeiger-Lesen {
    if ($abPhaseAnsage -gt 0) {
        $script:abPhase = $abPhaseAnsage
        Log ("Start bei " + (Phasen-Name $script:abPhase) + " auf Ansage (TEAM_VOLLAUTOMATIK_AB_PHASE=$abPhaseAnsage, Kit-BL-241) — die Phasen davor laufen NICHT.")
        return
    }
    if (-not (Test-Path -LiteralPath $phasenState)) { return }
    if ($vonVorn) {
        Log 'Phasen-Zeiger verworfen (--von-vorn) — der Lauf beginnt bei Phase 1.'
        Remove-Item -LiteralPath $phasenState -Force -ErrorAction SilentlyContinue
        return
    }
    $zeilen = @(Get-Content -LiteralPath $phasenState -ErrorAction SilentlyContinue)
    $vermerkt = if ($zeilen.Count -ge 1) { $zeilen[0] } else { '' }
    $lage = if ($zeilen.Count -ge 2) { $zeilen[1] } else { '' }
    if ($vermerkt -notin @('2', '3', '4')) {
        Remove-Item -LiteralPath $phasenState -Force -ErrorAction SilentlyContinue
        return
    }
    if ($lage -ne (Phasen-Lage)) {
        Log 'Phasen-Zeiger verworfen: Plan oder Stufenstand haben sich seither geaendert — der Lauf beginnt bei Phase 1.'
        Remove-Item -LiteralPath $phasenState -Force -ErrorAction SilentlyContinue
        return
    }
    $script:abPhase = [int]$vermerkt
    Log ("Faden aufgenommen bei " + (Phasen-Name $script:abPhase) + " — die Phasen davor werden uebersprungen (Kit-BL-217). .\vollautomatik.cmd --von-vorn beginnt stattdessen bei Phase 1.")
}

# BL-23 (3): Ein Abbruch endet nie ohne Weiterweg. Der Bericht kostet nichts,
# loest die Kostenfrage nicht — aber die Reibung, und er hilft bei JEDEM
# Abbruchgrund, nicht nur beim Deckel.
# BL-212: Die Kaskadennummer wird EINGESETZT statt als "<N>" gedruckt — der
# Bericht war der Absender genau der Zahl, die der Mensch danach abtippt, und
# BL-220 ist der Fund darueber, was ein Vertippen kostet. Findet sich nichts,
# bleibt der Platzhalter stehen statt zu raten.
function Kaskaden-Nummer {
    if (-not (Test-Path -LiteralPath '.ralph-plan')) { return '<N>' }
    $m = [regex]::Match((Get-Content -LiteralPath '.ralph-plan' -Raw), 'kaskade-(\d+)-')
    if ($m.Success) { return $m.Groups[1].Value }
    return '<N>'
}

# BL-259 (3): Ein Fund auf `offen` ist fuer die Fix-Phase unsichtbar — sie
# fragt nach 'an Frank übergeben'. Im Feld trug Frank regelkonform einen
# Beifang ein (Finder ≠ Fixer), der Lauf endete mit "nichts zu tun", und der
# Bericht meldete fertig. Am Ablauf aendert das nichts; die Luecke wird
# sichtbar, wo der Mensch hinsieht.
function Offene-Funde-Melden {
    $n = @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list') 2>$null |
           Where-Object { ($_ -split "`t", 2)[1] -match '^offen' }).Count
    if ($n -gt 0) {
        Log "⚠ $n Fund(e) stehen auf 'offen' und sind NIEMANDEM übergeben — die Fix-Phase sieht sie nicht (Kit-BL-259). Sichten, dann übergeben: $TEAM_BEUTEBUCH_TOOL set <HM-Nr> 'an Frank übergeben'"
    }
}

# BL-254 (3): Nach jedem Rollenlauf, der das Beutebuch anfassen durfte, wird
# es geprueft — OHNE Abbruch, der Befund landet im Abschlussbericht. Ein
# Anhang, der einen fremden Fundblock zerschneidet, ist fuer keinen Guard
# sichtbar (er urteilt ueber Schreibzonen, nicht ueber Struktur).
$script:lintBefunde = @()
function Beutebuch-Lint-Nach {
    param([string]$Rolle)
    $aus = @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('lint') 2>&1 | ForEach-Object { [string]$_ })
    if ($LASTEXITCODE -ne 3) { return }
    $erste = @($aus | Where-Object { $_ -match '^\[HM-' } | Select-Object -First 1)
    $text = if ($erste.Count) { $erste[0] } else { 'siehe beutebuch.py lint' }
    Log "⚠ Beutebuch nach ${Rolle}: Mängel gefunden (Kit-BL-254) — $text"
    $script:lintBefunde += "nach ${Rolle}: $text"
}

# BL-232 (2): Die volle Suite am Phasenende — verbindlich, sobald die Stufen
# mit dem schnellen Befehl (TEAM_SMOKE_TEST_SCHNELL) verifiziert haben. Rot
# setzt sie das Gate (BL-256), und der Lauf endet mit Exit 44.
function Voller-Smoke-Am-Phasenende {
    param([string]$Phase)
    if (-not $TEAM_SMOKE_TEST_SCHNELL -or -not $TEAM_SMOKE_TEST) { return }
    $ausgabe = Join-Path $logDir "volle-suite-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
    Log "Volle Suite am Ende der ${Phase}: $TEAM_SMOKE_TEST (die Stufen liefen mit $TEAM_SMOKE_TEST_SCHNELL, Kit-BL-232) …"
    Team-Werkzeug $TEAM_SMOKE_TEST @() *> $ausgabe
    if ($LASTEXITCODE -eq 0) {
        Log '✓ Volle Suite grün.'
    } else {
        Log "✗ Volle Suite ROT am Ende der $Phase — das Gate wird gesetzt (Kit-BL-232, Kit-BL-256). Ausgabe: $ausgabe"
        Add-Content -LiteralPath $TEAM_GATE_DATEI -Encoding utf8 -Value ("$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss') | vollautomatik | volle Suite rot am Ende der $Phase ($TEAM_SMOKE_TEST)")
        # BL-320: siehe vollautomatik.sh — ungeprueft ist nicht gruen, aber
        # die Ursache liegt dann an der Umgebung, und der Bericht sagt das.
        $befund = @(team_smoke_umgebung_befund $TEAM_SMOKE_TEST)
        if ($befund.Count) {
            Log '  Ursache ist die Umgebung, nicht der Code (Kit-BL-320):'
            foreach ($zeile in $befund) { Log "  $zeile" }
        }
    }
}

function Zielstand-Am-Ende {
    # BL-300: Am Ende des Laufs, vor jeder Handpruefung: Ist das, woran der
    # Mensch gleich prueft, der Stand, der eben gebaut wurde? Ein Befund, kein
    # Gate — rot heisst nicht "der Code ist falsch", sondern "das Ziel ist alt".
    if (-not $TEAM_ZIELSTAND_PRUEFUNG) { return }
    $ausgabe = Join-Path $logDir "zielstand-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
    Team-Werkzeug $TEAM_ZIELSTAND_PRUEFUNG @() *> $ausgabe
    if ($LASTEXITCODE -eq 0) {
        Log '✓ Zielstand: Das Geprüfte ist das Gebaute (Kit-BL-300).'
    } else {
        Log "✗ Zielstand ROT — vor der Handprüfung den gebauten Stand aufs Ziel bringen (Kit-BL-300). Ausgabe: $ausgabe"
    }
}

function Abbruch-Bericht {
    param([string]$Grund)
    $nr = Kaskaden-Nummer
    Log "--- WIE ES WEITERGEHT ($Grund) ---"
    $offen = @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list') 2>$null |
               Where-Object { $_ -and $_ -notmatch 'erledigt|überholt' })
    # BL-212: Der Satz richtet sich am PHASENSTAND aus, nicht am Beutebuch.
    # Ein leeres Beutebuch heisst "keine Funde", nicht "geprueft" — faellt der
    # Deckel zwischen Ralphs Feierabend und der Red-Team-Phase, ist es leer,
    # WEIL niemand gesucht hat. Der alte Satz schlug in genau diesem Zustand
    # den Closeout einer UNGEPRUEFTEN Kaskade vor. Der Irrtum zeigt in Richtung
    # `fertig`, und das ist die teure Richtung. Fehlt der Zeiger ganz, ist auch
    # Phase 1 nicht durch — der Default 1 ist die sichere Seite.
    $stand = 1
    if (Test-Path -LiteralPath $phasenState) {
        $roh = @(Get-Content -LiteralPath $phasenState)[0]
        if ($roh -match '^\d+$') { $stand = [int]$roh }
    }
    if ($stand -lt 4) {
        Log 'ACHTUNG: Die Phase Red Team wurde NICHT erreicht — diese Kaskade ist UNGEPRUEFT.'
        Log "  Ein leeres Beutebuch heisst hier 'niemand hat gesucht', nicht 'nichts gefunden'."
        Log ("  Kein Closeout, bevor der Sweep gelaufen ist:  .\vollautomatik.cmd (setzt bei " +
             (Phasen-Name $stand) + " fort)")
    } elseif ($offen.Count) {
        Log 'Offene Funde:'
        foreach ($z in $offen) { Log "    $z" }
        Log 'Fixphase fortsetzen:  .\fixphase.cmd   (Frank und Axel, mit Deckel und Bremse — Kit-BL-204)'
        Log "Danach der Closeout:  .\team-status.cmd --rollen-abschluss $nr <domaene>"
    } else {
        Log 'Keine offenen Funde — nur der Closeout fehlt:'
        Log "  .\team-status.cmd --rollen-abschluss $nr <domaene>"
    }
    # BL-217: phasengenau statt pauschal. Die alte Zeile versprach eine
    # Semantik, die das Skript nicht hatte.
    if (Test-Path -LiteralPath $phasenState) {
        $vermerkt = @(Get-Content -LiteralPath $phasenState)[0]
        Log ("Ganzen Lauf fortsetzen: .\vollautomatik.cmd (setzt bei " +
             (Phasen-Name ([int]$vermerkt)) + " fort; --von-vorn beginnt bei Phase 1)")
    } else {
        Log 'Ganzen Lauf fortsetzen: .\vollautomatik.cmd (beginnt bei Phase 1)'
    }
}

Phasen-Zeiger-Lesen

# --- Phase 1: Ralph baut die Kaskade ------------------------------------------
if (Phasen-Faellig 1) {
Log '=== PHASE 1: Ralph (Bau der Kaskade) ==='
$rc = Rolle-Starten './ralph.ps1'
if ($rc -eq 42) {
    Log '⏸ Lauf pausiert (Ralph) — Session-Limit oder abgelaufene Abo-Anmeldung; der Grund steht in der Zeile der Rolle darüber (Kit-BL-316). Danach .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht).'
    exit 42
}
if ($rc -eq 43) {
    # BL-41: Eigener Ausgang neben 0/1/42 — Ralphs Meldung nennt bereits den
    # Pruefweg. Hier NICHT als "Fehler" protokollieren: Der Lauf stoppt, aber
    # die bezahlte Arbeit ist mit hoher Wahrscheinlichkeit fertig, und ein
    # generisches "endete mit Fehler" hat im Feld viermal zum Neubau statt zum
    # Nachsehen gefuehrt (19,47 USD).
    Log '⚠ Stufe fertig, Quittung fehlt (Kit-BL-41) — Lauf gestoppt. NICHT neu bauen, bevor die von Ralph genannten zwei Prüfungen gelaufen sind.'
    exit 43
}
if ($rc -ne 0) {
    Log "Ralph endete mit Fehler ($rc) — Vollautomatik stoppt, Mensch gefragt."
    exit 1
}
# Erst JETZT ist Phase 1 durch — der Zeiger nennt immer die naechste Phase,
# nie die laufende. Ein Abbruch mittendrin faellt damit auf Phase 1 zurueck.
Phasen-Naechste 2
Voller-Smoke-Am-Phasenende 'Bauphase'
if (-not (Budget-Ok)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }
} else {
    Log '=== PHASE 1: Ralph — uebersprungen (Faden aufgenommen, Kit-BL-217) ==='
}

# --- Phase 2+3: Red-Team-Sweeps -----------------------------------------------
# BL-296: Der Stand VOR dem ersten Durchgang — ein zweiter Durchgang mit
# eigenem Fokus prueft denselben Bereich (siehe unten).
$vorherStand = @{}
foreach ($rolle in @('harry', 'marv')) {
    $vorherStand[$rolle] = if (Test-Path ".$rolle-state") { ((Get-Content -Raw ".$rolle-state") -replace '\s', '') } else { '-' }
    if (-not $vorherStand[$rolle]) { $vorherStand[$rolle] = '-' }
}
$phaseNr = 1
foreach ($rolle in @('harry', 'marv')) {
    $phaseNr++
    if (-not (Phasen-Faellig $phaseNr)) {
        Log "=== PHASE Red Team: $rolle — uebersprungen (Faden aufgenommen, Kit-BL-217) ==="
        continue
    }
    Log "=== PHASE Red Team: $rolle ==="
    $rc = Rolle-Starten "./$rolle.ps1"
    switch ($rc) {
        0 { Log "$rolle hat einen Sweep abgeschlossen."; Beutebuch-Lint-Nach $rolle }
        3 { Log "${rolle}: nichts Neues zu prüfen." }
        42 {
            Log "⏸ Lauf pausiert ($rolle) — Session-Limit oder abgelaufene Abo-Anmeldung; der Grund steht in der Zeile der Rolle darüber (Kit-BL-316). Danach .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht)."
            exit 42
        }
        default {
            Log "$rolle endete mit ECHTEM Fehler (${rc}: is_error/Guard-Verletzung/Aufruf-Fehlschlag — ein bloß fehlendes Promise bei sauberem Fund liefert bereits 0) — Vollautomatik stoppt."
            exit 1
        }
    }
    Phasen-Naechste ($phaseNr + 1)
    if (-not (Budget-Ok)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }
}

# BL-296: Die Pruefdichte an das Bauvolumen koppeln. Ein zweiter Durchgang je
# Angreifer, mit EIGENEM Fokus (TEAM_REDTEAM_FOCUS_2) ueber denselben Bereich
# — nur auf Ansage, und nur wenn die Sweeps in DIESEM Lauf gelaufen sind.
if ($env:TEAM_REDTEAM_FOCUS_2 -and (Phasen-Faellig 3)) {
    $fokusErst = $env:TEAM_REDTEAM_FOCUS
    foreach ($rolle in @('harry', 'marv')) {
        Log "=== PHASE Red Team: $rolle — zweiter Durchgang (eigener Fokus, Kit-BL-296) ==="
        $env:TEAM_REDTEAM_FOCUS = $env:TEAM_REDTEAM_FOCUS_2
        $env:TEAM_REDTEAM_ZWEITER_DURCHGANG = $vorherStand[$rolle]
        try {
            $rc = Rolle-Starten "./$rolle.ps1"
        } finally {
            $env:TEAM_REDTEAM_FOCUS = $fokusErst
            Remove-Item Env:TEAM_REDTEAM_ZWEITER_DURCHGANG -ErrorAction SilentlyContinue
        }
        switch ($rc) {
            0 { Log "$rolle hat den zweiten Durchgang abgeschlossen."; Beutebuch-Lint-Nach "$rolle (2. Durchgang)" }
            3 { Log "${rolle}: im zweiten Durchgang nichts zu prüfen." }
            42 {
                Log "⏸ Lauf pausiert ($rolle, 2. Durchgang) — Session-Limit oder abgelaufene Abo-Anmeldung; der Grund steht in der Zeile der Rolle darüber (Kit-BL-316). Danach .\vollautomatik.cmd erneut starten."
                exit 42
            }
            default {
                Log "$rolle endete im zweiten Durchgang mit ECHTEM Fehler ($rc) — Vollautomatik stoppt."
                exit 1
            }
        }
        if (-not (Budget-Ok)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }
    }
}
Phasen-Naechste 4

# --- Phase 4: Fix-Runden (Frank <-> Axel) -------------------------------------
# Auslauf-Bremse: Ein Fund kann ueber viele Runden hinweg IMMER WIEDER einen
# Fehlversuch produzieren (getan=1, aber kein echter Fortschritt) —
# TEAM_MAX_RUNDEN allein deckelt das nur grob (bis zu 12 teure Runden).
# STAGNATION zaehlt Runden OHNE Fortschritt und bricht frueh und benannt ab.
Log "=== PHASE 4: Fix-Runden (max $maxRunden, Auslauf-Bremse ab $stagnationMax Leerlauf-Runden in Folge) ==="
$runde = 0
$stagnation = 0
while ($runde -lt $maxRunden) {
    $runde++
    $getan = 0
    $fortschritt = 0
    $vorher = (@(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list')) -join "`n")

    $rc = Rolle-Starten './frank.ps1'
    switch ($rc) {
        0 { $getan = 1; $fortschritt = 1; Log "Runde ${runde}: Frank hat einen Fund gefixt." }
        3 { }
        # BL-210: Ein unbrauchbarer Auftrag ist NICHT dasselbe wie "nichts zu
        # tun". Er zaehlt wie ein Fehlversuch (kein break) und laeuft in die
        # Stagnations-Bremse, statt die Fix-Phase stumm zu beenden.
        5 {
            $getan = 1
            Log "Runde ${runde}: Franks Auftrag am Kopf der Warteschlange ist unbrauchbar (Kit-BL-210) — der Fundblock gehoert nachgebessert. Dahinter liegende Funde bleiben ungesehen, solange er dort steht."
        }
        42 {
            Log '⏸ Lauf pausiert (Frank) — Session-Limit oder abgelaufene Abo-Anmeldung; der Grund steht in der Zeile der Rolle darüber (Kit-BL-316). Danach .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht).'
            exit 42
        }
        # BL-214: derselbe vierte Ausgang wie bei Ralph, dieselbe Behandlung.
        43 {
            Log '⚠ Fix fertig, Quittung fehlt (Kit-BL-41/Kit-BL-214) — Lauf gestoppt. NICHT neu starten, bevor die von Frank genannten Prüfungen gelaufen sind.'
            exit 43
        }
        default { $getan = 1; Log "Runde ${runde}: Frank-Fehlversuch (ggf. Eskalation an Axel)." }
    }
    if ($getan -eq 1) { Beutebuch-Lint-Nach "Frank (Runde $runde)" }
    if (-not (Budget-Ok -Kulanz)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }

    # Axel nur rufen, wenn ein Fall auf ihn wartet.
    Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', 'an Axel übergeben') 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $rc = Rolle-Starten './axel.ps1'
        switch ($rc) {
            0 { $getan = 1; $fortschritt = 1; Log "Runde ${runde}: Axel hat eine Ermittlungsakte geliefert." }
            3 { }
            42 {
                Log '⏸ Lauf pausiert (Axel) — Session-Limit oder abgelaufene Abo-Anmeldung; der Grund steht in der Zeile der Rolle darüber (Kit-BL-316). Danach .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht).'
                exit 42
            }
            default { $getan = 1; Log "Runde ${runde}: Axel-Fehler ($rc) — Fall bleibt offen." }
        }
        Beutebuch-Lint-Nach "Axel (Runde $runde)"
        if (-not (Budget-Ok -Kulanz)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }
    }

    if ($getan -eq 0) {
        Log "Runde ${runde}: nichts mehr zu tun — Fix-Phase beendet."
        Offene-Funde-Melden
        break
    }

    $nachher = (@(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list')) -join "`n")
    if ($fortschritt -eq 0 -and $vorher -eq $nachher) {
        $stagnation++
        Log "Runde ${runde}: kein Fix/keine neue Akte/kein Statuswechsel — Stagnation $stagnation/$stagnationMax."
    } else {
        $stagnation = 0
    }

    if ($stagnation -ge $stagnationMax) {
        $stuck = '?'
        foreach ($status in @('an Frank übergeben', 'Fix-Plan liegt vor', 'an Axel übergeben')) {
            $kandidat = Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', $status) 2>$null
            if ($LASTEXITCODE -eq 0 -and $kandidat) { $stuck = ([string]$kandidat).Trim(); break }
        }
        Log "⛔ Fix-Phase stagniert: $stuck macht seit $stagnation Runden keinen Fortschritt — Mensch prüfen. Lauf gestoppt, um Leerlaufkosten zu vermeiden."
        Abbruch-Bericht 'Stagnation'
        exit 1
    }
}
if ($runde -ge $maxRunden) {
    Log "WARNUNG: Rundenlimit ($maxRunden) erreicht — evtl. offene Funde, Mensch prüfen."
}

# --- Abschluss ----------------------------------------------------------------
# Der Zeiger ueberlebt genau die Abbrueche: Hier, am regulaeren Ende, faellt er
# weg, damit der naechste Aufruf wieder eine ganze Kaskadenrunde faehrt.
# BL-210 (3): Der Bericht wird ehrlich. Endet die Fix-Phase mit Funden, die
# weiter auf Frank warten, ist das eine ANDERE Aussage als "nichts mehr zu
# tun" — im Feld hat sich der Lauf genau deshalb wie ein sauberer Abschluss
# gelesen.
$frankRest = @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list') 2>$null |
               Where-Object { $_ -match 'an Frank übergeben|Fix-Plan liegt vor' }).Count
if ($frankRest -gt 0) {
    Log "WARNUNG: $frankRest Fund(e) warten weiter auf Frank — die Fix-Phase ist NICHT leergelaufen."
    Log '  Steht ein unbrauchbarer Fundblock am Kopf der Warteschlange, bleibt alles dahinter ungesehen (Kit-BL-210).'
    Log '  Naechster Schritt:  .\frank.cmd   (nennt den Block, der nachgebessert gehoert)'
}

Voller-Smoke-Am-Phasenende 'Fix-Phase'
Zielstand-Am-Ende
Remove-Item -LiteralPath $phasenState -Force -ErrorAction SilentlyContinue
Log '=== ABSCHLUSSBERICHT ==='
Rolle-Starten './team-status.ps1' | Out-Null
# BL-240: Betrag und Aufzaehlung darunter beschreiben jetzt DIESELBE Menge —
# alle Rollen dieses Laufs. Vorher stand ueber einer Liste aus dem Ralph-
# Ordner (egal aus welchem Lauf) ein Betrag ueber alle Rollen dieses Laufs; im
# Feld 18,86 USD ueber Logs, die 15,40 ergaben, waehrend die Kaskade 21,91
# gekostet hatte. Wer die falsche Zahl nahm, buchte falsch.
Log "Dieser Lauf: $(Lauf-Kosten) USD — alle Rollen DIESES Laufs (Deckel $budgetUsd). Gesamt-Kontostand: $(Kontostand-Gesamt) USD."
# BL-37: Das Turn-Profil ist die Diagnose des Stufenschnitts und steht bereits
# in jedem Log — viele kurze Turns heissen Nacharbeit (Planfehler), wenige lange
# Urteilsarbeit (richtig geschnitten). Im Feld lief eine als "einfacher"
# angesetzte Stufe mit 87 Turns in 13 Minuten auf das Doppelte ihres Ansatzes,
# waehrend die teureren Nachbarstufen 47/57 Turns ueber 17 Minuten brauchten.
foreach ($z in @(Team-Werkzeug $TEAM_KOSTEN_TOOL @('turns', '.ralph-logs', '.team-logs', '.ralph-logs/archiv', '.team-logs/archiv', '--since', "$laufStart") 2>$null)) {
    if ($z) { Log "  $z" }
}
# BL-240 (c): Eine Kaskade kann ueber ZWEI Laeufe gebaut sein (vierter
# Ausgang, Deckel) — dann ist keine der Zahlen oben die ganze Kaskade.
if (Test-Path .ralph-plan) {
    $planPfad = ((Get-Content -Raw .ralph-plan) -replace '\s+$', '')
    $beginn = @(& git log --diff-filter=A --format=%ct -- $planPfad 2>$null | Where-Object { $_ }) | Select-Object -Last 1
    if ($beginn) {
        $bisher = team_kosten_seit $beginn @('.ralph-logs', '.team-logs', '.ralph-logs/archiv', '.team-logs/archiv')
        Log "Kaskade $(Kaskaden-Nummer) bisher: $bisher USD — alle Rohlogs seit ihrem Beginn, über alle Läufe (Kit-BL-240)."
    }
}
# BL-250: Mit welchem Auftrag die Sweeps liefen. Ein verfallener Fokus war bis
# hierher eine Logzeile mitten im Lauf — und ein Sweep ohne Auftrag sieht aus
# wie ein gegluekter.
foreach ($rolle in @('harry', 'marv')) {
    $datei = ".team-logs/fokus-$rolle.txt"
    if (-not (Test-Path $datei)) { continue }
    $mtime = [DateTimeOffset]::new((Get-Item $datei).LastWriteTimeUtc).ToUnixTimeSeconds()
    if ($mtime -lt $laufStart) { continue }
    Log "Red Team: $rolle — Fokus $(@(Get-Content $datei)[0])"
}
# BL-299: Die Abdeckungszeilen der Sweeps — was geprueft wurde, auch ohne Fund.
$abdeckung = @(Team-Werkzeug $TEAM_KOSTEN_TOOL @('abdeckung', '.team-logs', '--since', "$laufStart") 2>$null | Where-Object { $_ })
if ($abdeckung.Count) {
    Log 'Red Team — Abdeckung je Fokus-Punkt (Kit-BL-299):'
    foreach ($z in $abdeckung) { Log "  $z" }
}
# BL-316: Was ueber die API lief, steht danach unter `api` — mit Grund, sonst
# verrutscht die Kostenachse still.
$fallbacks = @(Team-Werkzeug $TEAM_KOSTEN_TOOL @('fallbacks', '.ralph-logs', '.team-logs', '.ralph-logs/archiv', '.team-logs/archiv', '--since', "$laufStart") 2>$null | Where-Object { $_ })
if ($fallbacks.Count) {
    Log 'API-Fallbacks dieses Laufs — echt abgerechnet, nicht im Abo (Kit-BL-316):'
    foreach ($z in $fallbacks) { Log "  $z" }
}
if ($script:lintBefunde.Count) {
    Log "Beutebuch-Lint meldete im Lauf Mängel (Kit-BL-254) — vor dem Closeout ansehen: $TEAM_BEUTEBUCH_TOOL lint"
    foreach ($z in $script:lintBefunde) { Log "  $z" }
}
Offene-Funde-Melden
# BL-255 (c): Eine planmaessig ausgelassene Stufe wird GETRENNT gezaehlt.
# "4 genommen, 1 planmaessig uebersprungen" ist eine andere Aussage als
# "5 genommen" - und ohne diese Zeile stuende nirgends, dass eine Stufe
# ueberhaupt ausgelassen wurde.
if (Test-Path '.ralph-uebersprungen') {
    $ausgelassen = @(Get-Content '.ralph-uebersprungen' |
                     Where-Object { $_ -match '^\d+$' } |
                     ForEach-Object { [int]$_ } | Sort-Object -Unique)
    if ($ausgelassen.Count) {
        Log ("Planmäßig übersprungen: Stufe $($ausgelassen -join ', ') (Kit-BL-255) — " +
             "Abbruchbedingung des Plans, jeweils committet. Der vierte Ausgang " +
             "wurde dafür NICHT gemeldet.")
    }
}

# BL-256: Der Lauf darf sich nicht als fertig melden, solange das Gate aus ist.
#
# Im Feld hat jede beteiligte Rolle sich regelkonform verhalten - der Fix
# scheiterte nicht an fremdem Flackern (BL-205), der Beifang wurde als eigener
# Fund erfasst (Finder != Fixer), die Fixphase fragte nach 'an Frank
# uebergeben' und fand nichts. Der Abschlussbericht meldete den Lauf als
# fertig, waehrend der Baum seit einer Stunde rot war.
#
# Die Regel bleibt unangetastet; was fehlte, ist ihre GEGENRICHTUNG. Gelesen
# wird hier, geschrieben haben es die Rollen (BL-256 im Prompt-Baustein).
$gateZeile = team_gate_rot_seit
if ($gateZeile) {
    Log '=== LAUF BEENDET — GATE ROT ==='
    Log "  Erste Meldung: $gateZeile"
    foreach ($z in @(Get-Content $TEAM_GATE_DATEI | Where-Object { $_.Trim() })) {
        Log "    $z"
    }
    Log '  Der Bau ist gelaufen, aber die Suite war es nicht — ein Lauf, der'
    Log '  sich hier als fertig meldete, hätte ein rotes Gate überdeckt (Kit-BL-256).'
    Log '  Nächster Schritt: den roten Baum reparieren. Ist er grün, gehört'
    Log "  $TEAM_GATE_DATEI gelöscht — dann meldet sich der nächste Lauf wieder normal."
    Log 'Vollautomatik beendet — Gate ROT.'
    exit 44
}

Log 'Vollautomatik beendet.'

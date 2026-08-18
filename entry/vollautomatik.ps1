<#
  vollautomatik.ps1 — der Vollautomatik-Orchestrator: faehrt eine komplette
  Kaskade durch. Ralph baut -> Red Team greift an -> Frank fixt -> Axel knackt
  die harten Faelle -> Abschlussbericht.

  Aufruf:  .\vollautomatik.cmd
  Env:     TEAM_MAX_RUNDEN   Fix-Runden Frank/Axel (Default 12).
           TEAM_FIX_MAX_STAGNATION  Auslauf-Bremse (Default =
                             TEAM_FRANK_MAX_VERSUCHE, sonst 3): bricht Phase 4
                             ab, sobald so viele Runden IN FOLGE weder einen
                             Frank-Fix noch eine neue Axel-Akte noch eine
                             Beutebuch-Statusaenderung gebracht haben.
                             Muss >= TEAM_FRANK_MAX_VERSUCHE bleiben, sonst
                             greift die Bremse VOR Franks eigener Eskalation
                             an Axel.
           TEAM_BUDGET_USD   Deckel fuer DIESEN Lauf (Default 15) — die harte
                             Durchsetzung misst nur die Kosten dieses einen
                             Laufs (A), nicht den lebenslangen Kontostand.
  Exit:    0 = Lauf durch · 1 = echter Fehler (inkl. Stagnation)
           43 = Stufe fertig, Quittung fehlt (BL-41, von ralph.ps1
                durchgereicht): kein Neubau — pruefen und von Hand quittieren
           42 = Session-Limit — Lauf pausiert (kein Fehler, State steht)

  Sequenziell und sperrgesichert. Haelt die Sperre ueber den ganzen Lauf und
  gibt sie an die Kind-Skripte weiter (TEAM_LOCK_HELD=1), damit die sich nicht
  selbst aussperren.
#>
# Bewusst KEIN 'Stop': Ein Rollen-Exit 3 ("nichts zu tun") ist der Normalfall
# und darf den Orchestrator nicht wegreissen — das Gegenstueck zu `set -uo
# pipefail` OHNE -e in der Bash-Fassung.
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

if (-not (team_lock 'vollautomatik')) { exit 1 }

# HM-32: Warn-Guard im EIGENEN Prozess seeden, BEVOR die erste Rolle startet —
# die Rollen laufen als GESCHWISTER-Prozesse, ein im Kind gesetzter Guard
# erreicht sie nie (analog team_lock/TEAM_LOCK_HELD). Nur im Abo-Modus
# relevant; im reinen api-Modus ist der Key legitim.
if ((team_auth_mode_effektiv 'abo') -eq 'abo') { team_warnung_abo_key | Out-Null }

$maxRunden = if ($env:TEAM_MAX_RUNDEN) { [int]$env:TEAM_MAX_RUNDEN } else { 12 }
# HM-31: Default an TEAM_FRANK_MAX_VERSUCHE koppeln (statt fest 2), sonst
# bricht die Bremse regelmaessig VOR Franks eigener Eskalation an Axel ab.
$stagnationMax = if ($env:TEAM_FIX_MAX_STAGNATION) { [int]$env:TEAM_FIX_MAX_STAGNATION }
                 elseif ($env:TEAM_FRANK_MAX_VERSUCHE) { [int]$env:TEAM_FRANK_MAX_VERSUCHE }
                 else { 3 }
$budgetUserGesetzt = if ($env:TEAM_BUDGET_USD) { '1' } else { '0' }
$budgetUsd = if ($env:TEAM_BUDGET_USD) { $env:TEAM_BUDGET_USD } else { '15' }
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
    $ausgabe = & pwsh -NoProfile -File $Skript @Argumente 2>&1
    $code = $LASTEXITCODE
    foreach ($z in $ausgabe) {
        $text = [string]$z
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
                Log "LAUF-BUDGET erreicht ($jetzt USD >= $budgetUsd USD), aber ein Fund ist in Bearbeitung — die angefangene Runde laeuft im Kulanzband bis $deckelKulant USD zu Ende (+$kulanzProzent %, BL-23). DANACH harter Stopp."
                return $true
            }
        }
    }
    Log "LAUF-BUDGET erreicht: dieser Lauf $jetzt USD >= Deckel $budgetUsd USD — harter Stopp (Gesamt-Kontostand $(Kontostand-Gesamt) USD, nur Anzeige)."
    return $false
}

# BL-23 (3): Ein Abbruch endet nie ohne Weiterweg. Der Bericht kostet nichts,
# loest die Kostenfrage nicht — aber die Reibung, und er hilft bei JEDEM
# Abbruchgrund, nicht nur beim Deckel.
function Abbruch-Bericht {
    param([string]$Grund)
    Log "--- WIE ES WEITERGEHT ($Grund) ---"
    $offen = @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('list') 2>$null |
               Where-Object { $_ -and $_ -notmatch 'erledigt|überholt' })
    if ($offen.Count) {
        Log 'Offene Funde:'
        foreach ($z in $offen) { Log "    $z" }
        Log 'Fixphase fortsetzen:  .\frank.cmd   (ein Fund je Aufruf)'
        Log 'Danach der Closeout:  .\team-status.cmd --rollen-abschluss <N> <domaene>'
    } else {
        Log 'Keine offenen Funde — nur der Closeout fehlt:'
        Log '  .\team-status.cmd --rollen-abschluss <N> <domaene>'
    }
    Log 'Ganzen Lauf fortsetzen: .\vollautomatik.cmd (nimmt den Faden am Zeigerstand auf)'
}

# --- Phase 1: Ralph baut die Kaskade ------------------------------------------
Log '=== PHASE 1: Ralph (Bau der Kaskade) ==='
$rc = Rolle-Starten './ralph.ps1'
if ($rc -eq 42) {
    Log '⏸ Session-Limit erreicht — Lauf pausiert (Ralph). Bitte später .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht).'
    exit 42
}
if ($rc -eq 43) {
    # BL-41: Eigener Ausgang neben 0/1/42 — Ralphs Meldung nennt bereits den
    # Pruefweg. Hier NICHT als "Fehler" protokollieren: Der Lauf stoppt, aber
    # die bezahlte Arbeit ist mit hoher Wahrscheinlichkeit fertig, und ein
    # generisches "endete mit Fehler" hat im Feld viermal zum Neubau statt zum
    # Nachsehen gefuehrt (19,47 USD).
    Log '⚠ Stufe fertig, Quittung fehlt (BL-41) — Lauf gestoppt. NICHT neu bauen, bevor die von Ralph genannten zwei Prüfungen gelaufen sind.'
    exit 43
}
if ($rc -ne 0) {
    Log "Ralph endete mit Fehler ($rc) — Vollautomatik stoppt, Mensch gefragt."
    exit 1
}
if (-not (Budget-Ok)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }

# --- Phase 2+3: Red-Team-Sweeps -----------------------------------------------
foreach ($rolle in @('harry', 'marv')) {
    Log "=== PHASE Red Team: $rolle ==="
    $rc = Rolle-Starten "./$rolle.ps1"
    switch ($rc) {
        0 { Log "$rolle hat einen Sweep abgeschlossen." }
        3 { Log "${rolle}: nichts Neues zu prüfen." }
        42 {
            Log "⏸ Session-Limit erreicht — Lauf pausiert ($rolle). Bitte später .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht)."
            exit 42
        }
        default {
            Log "$rolle endete mit ECHTEM Fehler (${rc}: is_error/Guard-Verletzung/Aufruf-Fehlschlag — ein bloß fehlendes Promise bei sauberem Fund liefert bereits 0) — Vollautomatik stoppt."
            exit 1
        }
    }
    if (-not (Budget-Ok)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }
}

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
        42 {
            Log '⏸ Session-Limit erreicht — Lauf pausiert (Frank). Bitte später .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht).'
            exit 42
        }
        default { $getan = 1; Log "Runde ${runde}: Frank-Fehlversuch (ggf. Eskalation an Axel)." }
    }
    if (-not (Budget-Ok -Kulanz)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }

    # Axel nur rufen, wenn ein Fall auf ihn wartet.
    Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', 'an Axel übergeben') 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $rc = Rolle-Starten './axel.ps1'
        switch ($rc) {
            0 { $getan = 1; $fortschritt = 1; Log "Runde ${runde}: Axel hat eine Ermittlungsakte geliefert." }
            3 { }
            42 {
                Log '⏸ Session-Limit erreicht — Lauf pausiert (Axel). Bitte später .\vollautomatik.cmd erneut starten. Kein Fehler, kein Datenverlust (State steht).'
                exit 42
            }
            default { $getan = 1; Log "Runde ${runde}: Axel-Fehler ($rc) — Fall bleibt offen." }
        }
        if (-not (Budget-Ok -Kulanz)) { Abbruch-Bericht 'Budget-Deckel'; exit 1 }
    }

    if ($getan -eq 0) {
        Log "Runde ${runde}: nichts mehr zu tun — Fix-Phase beendet."
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
Log '=== ABSCHLUSSBERICHT ==='
Rolle-Starten './team-status.ps1' | Out-Null
Log "Dieser Lauf: $(Lauf-Kosten) USD (Deckel $budgetUsd). Gesamt-Kontostand: $(Kontostand-Gesamt) USD."
# BL-37: Das Turn-Profil ist die Diagnose des Stufenschnitts und steht bereits
# in jedem Log — viele kurze Turns heissen Nacharbeit (Planfehler), wenige lange
# Urteilsarbeit (richtig geschnitten). Im Feld lief eine als "einfacher"
# angesetzte Stufe mit 87 Turns in 13 Minuten auf das Doppelte ihres Ansatzes,
# waehrend die teureren Nachbarstufen 47/57 Turns ueber 17 Minuten brauchten.
foreach ($z in @(Team-Werkzeug $TEAM_KOSTEN_TOOL @('turns', '.ralph-logs') 2>$null)) {
    if ($z) { Log "  $z" }
}
Log 'Vollautomatik beendet.'

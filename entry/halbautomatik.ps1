<#
  halbautomatik.ps1 — die T.E.A.M.-HALBAUTOMATIK.
  Wie die Vollautomatik, aber der Strippenzieher entscheidet zwischen JEDEM
  Schritt selbst. Nutzt dieselben Rollen-Skripte, haelt die Sperre ueber die
  Sitzung und reicht sie an die Kinder weiter.

  Zwei Betriebsarten:
    .\halbautomatik.cmd            interaktiv: zeigt den empfohlenen naechsten
                                   Schritt, wartet auf deine Taste, fuehrt EINEN
                                   Schritt aus, fragt wieder.
    .\halbautomatik.cmd <schritt>  Einzelschritt ohne Menue (fuer Skripte/Tests):
                                   ralph | harry | marv | frank | axel | status | next

  Env wie bei der Vollautomatik. Kein Gesamt-Deckel-Zwang: Hier siehst du die
  Kosten nach jedem Schritt selbst.
#>
# Bewusst kein 'Stop': Rollen-Exit 3 ist der Normalfall.
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

# HM-32: Warn-Guard im EIGENEN Prozess seeden, BEVOR die erste Rolle startet —
# die Rollen laufen als GESCHWISTER-Prozesse, ein im Kind gesetzter Guard
# erreicht sie nie. Nur im Abo-Modus relevant.
if ((team_auth_mode_effektiv 'abo') -eq 'abo') { team_warnung_abo_key | Out-Null }

$ralphCapWert = team_ralph_cap

function Naechster-Schritt {
    $stufe = 1
    if (Test-Path '.ralph-state') {
        $roh = (Get-Content -TotalCount 1 '.ralph-state') -replace '\s', ''
        if ($roh -match '^\d+$') { $stufe = [int]$roh }
    }
    if ($ralphCapWert -match '^\d+$' -and [int]$ralphCapWert -ne 0 -and $stufe -le [int]$ralphCapWert) {
        return 'ralph'
    }
    $head = (& git rev-parse HEAD).Trim()
    foreach ($paar in @(@('.harry-state', 'harry'), @('.marv-state', 'marv'))) {
        $stand = 'x'
        if (Test-Path $paar[0]) { $stand = ((Get-Content -Raw $paar[0]) -replace '\s', '') }
        if ($stand -ne $head) { return $paar[1] }
    }
    foreach ($status in @('Fix-Plan liegt vor', 'an Frank übergeben')) {
        Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', $status) 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { return 'frank' }
    }
    Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('first', 'an Axel übergeben') 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { return 'axel' }
    return 'fertig'
}

function Schritt-Ausfuehren {
    # Eigener Prozess je Rolle — dieselbe Begruendung wie in
    # vollautomatik.ps1 (Rolle-Starten): treue Uebersetzung des Bash-Subprozesses,
    # und TEAM_LOCK_HELD wird ueber die Umgebung vererbt.
    param([string]$Schritt)
    if ($Schritt -notin @('ralph', 'harry', 'marv', 'frank', 'axel')) {
        Team-Fehler "Unbekannter Schritt: $Schritt"
        return 2
    }
    & pwsh -NoProfile -File "./$Schritt.ps1"
    return $LASTEXITCODE
}

function Deute-Exit {
    param([string]$Schritt, [int]$Rc)
    switch ($Rc) {
        0 { [Console]::Out.WriteLine("  → $Schritt hat gearbeitet (Exit 0).") }
        3 { [Console]::Out.WriteLine("  → ${Schritt}: nichts zu tun (Exit 3).") }
        # BL-41: kein Fehler im gewohnten Sinn — die Arbeit ist meist fertig,
        # nur unquittiert. Die Rolle hat den Pruefweg bereits gedruckt.
        43 { [Console]::Out.WriteLine("  → ${Schritt}: Stufe fertig, Quittung fehlt (Exit 43, BL-41) — NICHT neu bauen, erst die oben genannten zwei Prüfungen fahren.") }
        default { [Console]::Out.WriteLine("  → $Schritt endete mit Fehler (Exit $Rc) — Logs prüfen (.team-logs\, .ralph-logs\).") }
    }
}

function Deckel-Dialog-Ralph {
    # Nur beim ralph-Schritt relevant (Bau kostet am meisten) — Read-Only-Rollen
    # brauchen keinen Dialog. Der Einzelschritt-Modus ruft ihn NICHT auf und
    # bleibt damit ohne Dialog lauffaehig.
    [Console]::Out.WriteLine('  ── Deckel-Check vor dem Bau-Schritt ──')
    foreach ($z in @(& pwsh -NoProfile -File ./team-status.ps1 --budget)) { [Console]::Out.WriteLine("  $z") }
    $empfehlung = team_budget_empfehlung
    if ($empfehlung) {
        $eingabe = Read-Host "  Architekten-Empfehlung: $empfehlung USD. [Enter]=übernehmen, oder Zahl eingeben"
    } else {
        $empfehlung = '15'
        $eingabe = Read-Host "  Keine Architekten-Empfehlung im aktiven Plan — Default $empfehlung USD. [Enter]=übernehmen, oder Zahl eingeben"
    }
    $env:TEAM_BUDGET_USD = if ($eingabe) { $eingabe } else { $empfehlung }
    [Console]::Out.WriteLine("  → Deckel für diesen Lauf: $($env:TEAM_BUDGET_USD) USD.")
}

# --- Einzelschritt-Modus (nicht-interaktiv) -----------------------------------
if ($args.Count -ge 1) {
    switch ($args[0]) {
        'status' { & pwsh -NoProfile -File ./team-status.ps1; exit $LASTEXITCODE }
        'next'   { [Console]::Out.WriteLine((Naechster-Schritt)); exit 0 }
        { $_ -in @('ralph', 'harry', 'marv', 'frank', 'axel') } {
            if (-not (team_lock 'halbautomatik')) { exit 1 }
            $rc = Schritt-Ausfuehren $args[0]
            Deute-Exit $args[0] $rc
            exit $rc
        }
        default {
            Team-Fehler 'Aufruf: .\halbautomatik.cmd [ralph|harry|marv|frank|axel|status|next]'
            exit 2
        }
    }
}

# --- Interaktiver Modus -------------------------------------------------------
if ([Console]::IsInputRedirected) {
    [Console]::Out.WriteLine('halbautomatik.ps1 ohne Terminal aufgerufen — hier ist der empfohlene nächste Schritt:')
    [Console]::Out.WriteLine("  $(Naechster-Schritt)")
    [Console]::Out.WriteLine('Für einen konkreten Schritt: .\halbautomatik.cmd <ralph|harry|marv|frank|axel>')
    exit 0
}

if (-not (team_lock 'halbautomatik')) { exit 1 }
[Console]::Out.WriteLine('═══ T.E.A.M. Halbautomatik — Schritt für Schritt ═══')
[Console]::Out.WriteLine('Du entscheidest jeden Schritt. [Enter]=Empfehlung · [q]=Schluss · [?]=Hilfe')

while ($true) {
    $empfohlen = Naechster-Schritt
    [Console]::Out.WriteLine('')
    [Console]::Out.WriteLine('──────────────────────────────────────────────')
    [Console]::Out.WriteLine("  Empfohlener nächster Schritt: $empfohlen")
    if ($empfohlen -eq 'fertig') {
        [Console]::Out.WriteLine('  (Kaskade gebaut, Red Team durch, Beutebuch abgearbeitet.)')
    }
    $taste = Read-Host "  [Enter]=$empfohlen  [r]alph [h]arry [m]arv [f]rank [a]xel  [s]tatus  [q]uit"

    switch -Regex ($taste) {
        '^$' {
            if ($empfohlen -eq 'fertig') {
                [Console]::Out.WriteLine('  Nichts zu tun — nutze [q] zum Beenden.')
                break
            }
            if ($empfohlen -eq 'ralph') { Deckel-Dialog-Ralph }
            $rc = Schritt-Ausfuehren $empfohlen; Deute-Exit $empfohlen $rc
            break
        }
        '^(r|ralph)$' { Deckel-Dialog-Ralph; $rc = Schritt-Ausfuehren 'ralph'; Deute-Exit 'ralph' $rc; break }
        '^(h|harry)$' { $rc = Schritt-Ausfuehren 'harry'; Deute-Exit 'harry' $rc; break }
        '^(m|marv)$'  { $rc = Schritt-Ausfuehren 'marv';  Deute-Exit 'marv'  $rc; break }
        '^(f|frank)$' { $rc = Schritt-Ausfuehren 'frank'; Deute-Exit 'frank' $rc; break }
        '^(a|axel)$'  { $rc = Schritt-Ausfuehren 'axel';  Deute-Exit 'axel'  $rc; break }
        '^(s|status)$' { & pwsh -NoProfile -File ./team-status.ps1; break }
        '^(q|quit|exit)$' {
            [Console]::Out.WriteLine('  Halbautomatik beendet. Der Rest wartet geduldig.')
            return
        }
        '^(\?|help)$' {
            [Console]::Out.WriteLine('  Enter=empfohlenen Schritt · r/h/m/f/a=bestimmte Rolle erzwingen')
            [Console]::Out.WriteLine('  s=Status-Dashboard · q=beenden. Ein Tastendruck = ein Schritt.')
            break
        }
        default { [Console]::Out.WriteLine("  Unbekannt: '$taste' — [?] für Hilfe."); break }
    }
}

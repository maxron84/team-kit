# Bahn: pwsh | Gegenstueck: team-auth-setup.sh
<#
  team-auth-setup.ps1 — Maschinen-Einrichtung fuer die pwsh-Bahn:
  Abo als Prio 1, API-Key nur als geschuetzter Fallback.

  Gegenstueck zu scripts/team-auth-setup.sh. Gleiche Aufgabe, gleiche
  Reihenfolge, gleiche Idempotenz — aber drei Dinge sind unter Windows
  anders, und alle drei sind der Grund, warum es dieses Skript ueberhaupt
  gibt und nicht nur eine Pfadanpassung:

  1. ABLAGE. Nicht ~/.config/claude-team, sondern %APPDATA%\claude-team.
     Beide Dateien heissen wie unter Linux (auth-mode, api-key), damit die
     Doku eine bleibt und lib.psm1 in Stufe 3 dieselbe Semantik bekommt.

  2. SCHUTZ. `chmod 600` ist unter Windows wirkungslos — es laeuft ohne
     Fehler durch und bewirkt NICHTS. Der Key laege danach fuer jeden
     lesbar da, und zwar mit einem gruenen Haken daneben. Stattdessen:
     Vererbung abschalten und exakt einen Berechtigten eintragen (den
     Besitzer). Das wird hier nach dem Setzen NACHGEPRUEFT statt geglaubt.

  3. MIGRATION. Unter Linux steht ein verdraengender Key in .bashrc & Co.
     Unter Windows steht er fast nie in einem Profil, sondern als
     BENUTZER-UMGEBUNGSVARIABLE (setx, Systemsteuerung). Wer nur Profile
     durchsucht, findet ihn nicht, meldet "sauber" — und das Abo bleibt
     verdraengt. Deshalb wird beides geprueft, die Umgebungsvariable zuerst.

  Aufruf:  pwsh -File <kit>\scripts\team-auth-setup.ps1
#>
[CmdletBinding()]
param(
    [switch]$NichtInteraktiv
)

$ErrorActionPreference = 'Stop'

function Team-CfgDir {
    # %APPDATA% ist der richtige Ort unter Windows. Der Rueckfall haelt das
    # Skript auf Nicht-Windows lauffaehig und zeigt dort auf DIESELBE Ablage,
    # die die Bash-Bahn benutzt — eine Maschine, eine Auth-Konfiguration.
    # Bewusst in jedem Bootstrap-Skript einzeln: Sie duerfen von team/lib.psm1
    # nicht abhaengen, denn sie laufen, BEVOR es die Bibliothek gibt.
    if ($env:APPDATA) { return (Join-Path $env:APPDATA 'claude-team') }
    return (Join-Path $HOME '.config/claude-team')
}

$CfgDir    = Team-CfgDir
$ModeFile  = Join-Path $CfgDir 'auth-mode'
$KeyFile   = Join-Path $CfgDir 'api-key'
$Stempel   = Get-Date -Format 'yyyy-MM-dd'
$Interaktiv = -not $NichtInteraktiv -and -not [Console]::IsInputRedirected

function Sag($t)  { Write-Host $t }
function Ok($t)   { Write-Host "  [ok] $t" -ForegroundColor Green }
function Warn($t) { Write-Host "  [!]  $t" -ForegroundColor Yellow }

Sag "=== T.E.A.M. Auth-Einrichtung (Windows) — Abo als Prio 1, API nur als Fallback ==="
Sag ""

# --- 1. CLI vorhanden? -------------------------------------------------------
$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($claude) {
    Ok "claude-CLI gefunden: $($claude.Source)"
} else {
    Warn "'claude' nicht im PATH — erst Claude Code installieren, dann erneut ausfuehren."
    exit 1
}

# --- 2. Maschinen-Default: abo -----------------------------------------------
New-Item -ItemType Directory -Force -Path $CfgDir | Out-Null
if (Test-Path $ModeFile) {
    $modus = (Get-Content -TotalCount 1 $ModeFile).Trim()
    Ok "auth-mode existiert bereits: '$modus' (bleibt unangetastet)"
} else {
    Set-Content -Path $ModeFile -Value 'abo' -Encoding ascii -NoNewline
    Ok "auth-mode angelegt: abo ($ModeFile)"
}

# --- Schutz der Schluesseldatei ----------------------------------------------
function Schuetze-Datei($pfad) {
    <#
      Der Ersatz fuer `chmod 600`. Vererbung AUS und genau ein Eintrag —
      sonst erbt die Datei die Rechte von %APPDATA% und ist fuer mehr
      Konten lesbar, als hier je gemeint war.
    #>
    $acl = Get-Acl $pfad
    $acl.SetAccessRuleProtection($true, $false)   # Vererbung aus, nichts uebernehmen
    foreach ($regel in @($acl.Access)) { $acl.RemoveAccessRule($regel) | Out-Null }
    $ich = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule(
        $ich, 'FullControl', 'Allow')))
    Set-Acl -Path $pfad -AclObject $acl
    return $ich
}

function Pruefe-Schutz($pfad, $ich) {
    # Nachpruefen statt glauben: Ein stiller Fehlschlag beim Setzen der ACL
    # sieht genauso aus wie ein Erfolg — und der Key laege lesbar da.
    $acl = Get-Acl $pfad
    $fremde = @($acl.Access | Where-Object { $_.IdentityReference.Value -ne $ich })
    if ($acl.AreAccessRulesProtected -and $fremde.Count -eq 0) { return $true }
    return $false
}

function Schreibe-Key($wert) {
    Set-Content -Path $KeyFile -Value $wert -Encoding ascii -NoNewline
    $ich = Schuetze-Datei $KeyFile
    if (Pruefe-Schutz $KeyFile $ich) {
        Ok "Zugriff auf $KeyFile beschraenkt auf $ich (nachgeprueft)"
    } else {
        Warn "Die Rechte auf $KeyFile liessen sich NICHT einschraenken."
        Warn "Der Key liegt dort lesbar. Von Hand pruefen:  icacls `"$KeyFile`""
    }
}

# --- 3. API-Key fuer den Fallback --------------------------------------------
$keyQuelle = ""
if ((Test-Path $KeyFile) -and (Get-Item $KeyFile).Length -gt 0) {
    $keyQuelle = "vorhandene Datei"
} else {
    # 3a) Benutzer-Umgebungsvariable — der Windows-Normalfall, den ein reiner
    #     Profil-Scan uebersieht.
    $ausEnv = [Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY', 'User')
    if ($ausEnv) {
        Schreibe-Key $ausEnv
        [Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', $null, 'User')
        $keyQuelle = "Benutzer-Umgebungsvariable (dort entfernt — sie verdraengte das Abo)"
    }

    # 3b) PowerShell-Profile
    if (-not $keyQuelle) {
        $profile_kandidaten = @(
            $PROFILE.CurrentUserAllHosts, $PROFILE.CurrentUserCurrentHost,
            $PROFILE.AllUsersAllHosts
        ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
        foreach ($prof in $profile_kandidaten) {
            $inhalt = Get-Content -Raw $prof
            $treffer = [regex]::Match($inhalt,
                '(?m)^\s*\$env:ANTHROPIC_API_KEY\s*=\s*[''"]?([^''"\s]+)[''"]?\s*$')
            if ($treffer.Success) {
                Copy-Item $prof "$prof.bak-teamauth-$Stempel"
                Schreibe-Key $treffer.Groups[1].Value
                $ersatz = "# ANTHROPIC_API_KEY umgezogen nach $KeyFile — Abo ist Prio 1 (team-auth-setup.ps1, $Stempel)"
                Set-Content -Path $prof -Value ([regex]::Replace($inhalt,
                    '(?m)^\s*\$env:ANTHROPIC_API_KEY\s*=.*$', $ersatz))
                $keyQuelle = "Migration aus $prof (Backup: $prof.bak-teamauth-$Stempel — nach erfolgreichem Test loeschen, enthaelt den Key!)"
                break
            }
        }
    }

    # 3c) Interaktive Eingabe
    if (-not $keyQuelle -and $Interaktiv) {
        Sag ""
        Sag "  Kein API-Key gefunden. Fuer den Fallback einen Key von console.anthropic.com"
        $sicher = Read-Host -AsSecureString -Prompt "  hier einfuegen (unsichtbar, leer = ohne Fallback fortfahren)"
        $klar = [System.Net.NetworkCredential]::new('', $sicher).Password
        if ($klar) { Schreibe-Key $klar; $keyQuelle = "manuelle Eingabe" }
    }
}

if ((Test-Path $KeyFile) -and (Get-Item $KeyFile).Length -gt 0) {
    Ok "API-Fallback-Key liegt in $KeyFile (Quelle: $(if ($keyQuelle) { $keyQuelle } else { 'vorhandene Datei' }))"
} else {
    Warn "Kein API-Key hinterlegt — Abo funktioniert trotzdem, aber es gibt keinen Fallback."
    Warn "Nachholen: den Key in $KeyFile schreiben, danach dieses Skript erneut fahren (setzt die Rechte)."
}

# --- 4. Aktuelle Sitzung pruefen ---------------------------------------------
Sag ""
if ($env:ANTHROPIC_API_KEY) {
    Warn "In DIESER Sitzung ist ANTHROPIC_API_KEY noch gesetzt!"
    Warn "Der Key verdraengt dein Abo — bitte jetzt ausfuehren:  `$env:ANTHROPIC_API_KEY = `$null"
    Warn "(Neue Sitzungen sind sauber, sofern die Benutzervariable entfernt wurde.)"
} else {
    Ok "Kein ANTHROPIC_API_KEY in dieser Sitzung — Abo hat freie Bahn."
}

# --- 5. Optionaler Abo-Test ---------------------------------------------------
if ($Interaktiv) {
    $antwort = Read-Host "Abo-Login jetzt headless testen? (kostet einen Mini-Abo-Anteil) [j/N]"
    if ($antwort -and $antwort.ToLower() -eq 'j') {
        Sag "  Teste: claude -p (ohne API-Key in der Umgebung) ..."
        $gemerkt = $env:ANTHROPIC_API_KEY
        $gemerktToken = $env:ANTHROPIC_AUTH_TOKEN
        $env:ANTHROPIC_API_KEY = $null
        $env:ANTHROPIC_AUTH_TOKEN = $null
        try {
            $ausgabe = @(& claude -p 'Antworte nur mit: pong' 2>&1)
            $rc = $LASTEXITCODE
            $text = $ausgabe -join "`n"
            if ($rc -ne 0) {
                Warn "Test fehlgeschlagen — vermutlich fehlt der Abo-Login."
                Warn "Einmalig nachholen: 'claude' starten -> /login -> Claude-Konto waehlen -> /exit"
                Sag ""
                Sag $text
                exit 1
            }
            if ($text -match '(?i)takes precedence') {
                Warn "Antwort kam, aber eine andere Auth-Quelle verdraengt das Abo — Ausgabe pruefen:"
                Sag $text
            } else {
                Ok "Abo-Login funktioniert headless: $($ausgabe[-1])"
            }
        } finally {
            $env:ANTHROPIC_API_KEY = $gemerkt
            $env:ANTHROPIC_AUTH_TOKEN = $gemerktToken
        }
    }
}

# --- Zusammenfassung ----------------------------------------------------------
Sag ""
Sag "=== Fertig. So sprichst du die Modi an: ==="
Sag "  .\ralph.cmd                        -> Abo zuerst, API-Fallback pro Stufe automatisch"
Sag "  `$env:AUTH_MODE='api'; .\ralph.cmd  -> API fuer diesen Lauf erzwingen"
Sag "  `$env:AUTH_MODE='abo'; ...          -> Abo erzwingen (falls Config mal anders steht)"
Sag ""
Sag "Merke: Der Key gehoert NIE in die Benutzer-Umgebungsvariablen — sonst"
Sag "verdraengt er das Abo, und zwar dauerhaft und unsichtbar."

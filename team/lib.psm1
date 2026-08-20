# Bahn: pwsh | Gegenstueck: lib.sh
<#
  team/lib.psm1 — gemeinsame Bibliothek der T.E.A.M.-Rollen, PowerShell-Zweig.

  Gegenstueck zu team/lib.sh. Wird per `Import-Module` eingebunden, nicht
  direkt ausgefuehrt.

  DIE AUFRUFKONVENTION IST EIN VERTRAG, KEIN STIL
  Sie steht im Kopf von team/tests/conftest.py und wird hier eingehalten:
    1. Bash `return 0`/`return 1`      -> $true / $false
    2. Bash-Ausgabe auf stdout          -> Write-Output
    3. Eine Funktion tut das eine ODER das andere, nie beides
    4. Diagnose nach stderr             -> [Console]::Error.WriteLine
    5. Abgestufte Exit-Codes            -> [int] + [Console]::Out.WriteLine
    6. Bibliotheks-Defaults             -> $NAME = Team-Default 'NAME' 'wert'
    7. Abgeleitete Bausteine exportiert -> Export-ModuleMember -Variable

  DIE FALLE, DIE ES IN BASH NICHT GIBT
  In PowerShell wird JEDE nicht abgefangene Ausgabe einer Funktion Teil ihres
  Rueckgabewerts. Ein `git checkout ...` ohne `| Out-Null` verwandelt ein
  sauberes $true in ein Array aus git-Zeilen plus $true — und `if (funktion)`
  ist dann IMMER wahr, weil ein nicht-leeres Array wahr ist. Der Guard wuerde
  jeden Uebergriff durchwinken und dabei gruen melden. Deshalb: jeder externe
  Aufruf in einer urteilenden Funktion geht nach Out-Null, und jeder Ausgang
  ist ein ausdrueckliches `return $true`/`return $false`.

  WAS HIER BESSER IST ALS IN DER BASH-FASSUNG
    * Die 13 eingebetteten `python3 -c`-Bloecke entfallen ersatzlos
      (ConvertFrom-Json, [regex], [DateTimeOffset]).
    * team_lock nimmt eine vom Betriebssystem DURCHGESETZTE Sperre
      (FileShare::None) statt des kooperativen flock.

  WAS GLEICH BLEIBT, UND ZWAR ABSICHTLICH
  Die Werkzeuge unter team/tools/ werden NICHT portiert. Ledger, Beutebuch und
  Kostenrechnung — der gesamte Zustand — liegen hier wie dort in denselben
  Python-Dateien. Der PowerShell-Zweig ist eine zweite ORCHESTRIERUNG, kein
  zweiter Zustandscode.
#>

# --- Projekt-Konfiguration ----------------------------------------------------
# Zuerst gelesen, damit die Team-Default-Zuweisungen unten sie stehen lassen.
# Fehlt die Datei, laufen die Rollen mit den Defaults dieser Bibliothek weiter —
# so bricht ein Lauf nie an einer fehlenden Konfigdatei ab.
# Position und Arbeitsverzeichnis beim Laden angleichen (siehe Team-Pfad).
# Die Entrypoints setzen ihre Position VOR dem Import, hier stimmt sie also
# schon. Das ist der Guertel; Team-Pfad ist der Hosentraeger.
[Environment]::CurrentDirectory = (Get-Location).ProviderPath

$_konfig = Join-Path (Split-Path -Parent $PSScriptRoot) 'team.config.ps1'
if (Test-Path $_konfig) {
    . $_konfig
} else {
    [Console]::Error.WriteLine("[team-lib] WARNUNG: team.config.ps1 fehlt — Bibliotheks-Defaults aktiv.")
}

function Team-Default {
    <#
      Der Ersatz fuer Bashs `NAME="${NAME:-vorgabe}"`. Reihenfolge wie dort:
      Was die Konfiguration (oder die Umgebung ueber sie) gesetzt hat, gewinnt;
      sonst gilt der Bibliotheks-Default.

      Die Zeile, die diese Funktion aufruft, ist greppbar — Tests lesen den
      Default statisch aus der Quelle, weil ein Laden die PROJEKTWERTE
      liefern wuerde und nicht den Default (Lehre aus BL-100).
    #>
    param([string]$Name, [string]$Vorgabe)
    $vorhanden = Get-Variable -Name $Name -Scope Script -ErrorAction SilentlyContinue
    if ($vorhanden -and $vorhanden.Value) { return $vorhanden.Value }
    $ausEnv = [Environment]::GetEnvironmentVariable($Name)
    if ($ausEnv) { return $ausEnv }
    return $Vorgabe
}

function Team-Fehler {
    # Diagnose geht nach stderr (Vertrag Punkt 4). Write-Error scheidet aus: Es
    # formatiert, faerbt und kann unter $ErrorActionPreference='Stop' den Lauf
    # abbrechen — eine Warnung darf keinen Abbruch ausloesen.
    param([string]$Text)
    [Console]::Error.WriteLine($Text)
}

function Team-Werkzeug {
    <#
      Ruft eine als ZEICHENKETTE konfigurierte Werkzeugzeile auf
      ("python3 team/tools/kosten.py"). In Bash erledigt das die Wortzerlegung
      der Shell; PowerShell uebergibt eine Zeichenkette sonst als EIN Argument,
      und der Aufruf scheitert an einer Datei namens "python3 team/tools/…".
    #>
    param([string]$Zeile, [string[]]$Argumente = @())
    $teile = @($Zeile -split '\s+' | Where-Object { $_ })
    $befehl = $teile[0]
    $rest = @()
    if ($teile.Count -gt 1) { $rest = $teile[1..($teile.Count - 1)] }
    & $befehl @($rest + $Argumente)
}

function Team-Pfad {
    <#
      Macht einen relativen Pfad absolut — gegen die POWERSHELL-Position, nicht
      gegen das .NET-Arbeitsverzeichnis.

      WARUM ES DIESE FUNKTION GIBT: `Set-Location` (das Gegenstueck zu `cd`,
      und die BL-3-Invariante jedes Entrypoints) aendert NUR die Position der
      PowerShell-Sitzung. Das Arbeitsverzeichnis des Prozesses bleibt, wo es
      war. Cmdlets wie Get-Content und Test-Path folgen der Position;
      [System.IO.File] folgt dem Prozess. Beide nebeneinander zu benutzen
      heisst: `Test-Path 'plans/x.md'` sagt ja, und `ReadAllText('plans/x.md')`
      im naechsten Ausdruck wirft "Could not find file".

      Der Fehler faellt nur auf, wenn Position und Arbeitsverzeichnis
      auseinanderliegen — also NICHT, wenn man das Skript aus seinem eigenen
      Ordner startet, und GENAU DANN, wenn ein anderes Skript es aufruft. Er
      wartet also auf den Selbsttest und auf die Vollautomatik, nicht auf den
      Handstart.
    #>
    param([string]$Pfad)
    if (-not $Pfad) { return $Pfad }
    if ([System.IO.Path]::IsPathRooted($Pfad)) { return $Pfad }
    return (Join-Path (Get-Location).ProviderPath $Pfad)
}

function Team-JsonLesen {
    # Der Ersatz fuer die 13 `python3 -c`-Bloecke. Nicht lesbar -> $null, und
    # JEDE aufrufende Funktion behandelt $null ausdruecklich: Eine unlesbare
    # Datei ist im Kit nie "leer", sondern immer ein Fehlerfall.
    param([string]$Pfad)
    if (-not (Test-Path $Pfad -PathType Leaf)) { return $null }
    try { return (Get-Content -Raw -LiteralPath $Pfad | ConvertFrom-Json) }
    catch { return $null }
}

# --- Abgeleitete Prompt-Bausteine ---------------------------------------------
$TEAM_SMOKE_TEST = Team-Default 'TEAM_SMOKE_TEST' ''
if ($TEAM_SMOKE_TEST) {
    # Der Nachsatz ist eine Notbremse gegen einen teuren Fehlermodus, nicht
    # Ausschmueckung (BL-41, Feld platformer K27/K28): Eine bauende Rolle
    # startete den Smoke-Test als HINTERGRUND-Task und wartete danach auf eine
    # Benachrichtigung, die in einer headless-Sitzung nie eintrifft. Der Lauf
    # endet mit subtype=success und is_error=false — er SIEHT AUS WIE EIN
    # ERFOLG —, gibt aber kein Promise und committet nicht. Dreimal passiert,
    # zusammen 13,25 USD, jedes Mal fuer Arbeit, die bereits fertig und gruen
    # war. Der Satz steht hier statt in den Rollen-Briefings, weil er hier
    # JEDE bauende Rolle trifft statt nur eine.
    $SMOKE_ZEILE = @"
Smoke-Test ausführen: $TEAM_SMOKE_TEST — muss grün sein.
   Führe ihn im VORDERGRUND aus und warte auf seine Ausgabe. Starte ihn
   NIEMALS als Hintergrund-Task und plane keinen Wakeup darauf: Diese Sitzung
   ist headless, es kommt keine Benachrichtigung, und du wartest bis zum
   Zeitlimit auf ein Ereignis, das nicht eintreten kann.
"@.TrimEnd()
    $SMOKE_SUFFIX = " Smoke-Test grün: $TEAM_SMOKE_TEST."
} else {
    $SMOKE_ZEILE = "(Kein Smoke-Test konfiguriert — Schritt entfällt. Das Team arbeitet ohne Sicherheitsnetz; TEAM_SMOKE_TEST in team.config.ps1 nachtragen.)"
    $SMOKE_SUFFIX = ""
}

function team_allowed_tools {
    # Werkzeug-Allowlist fuer Guard-Linie 2. Axel bekommt NUR den Plan-Ordner,
    # das Red Team zusaetzlich den Test-Ordner.
    param([string]$Rolle)
    $basis = "Read Grep Glob Bash(${TEAM_BEUTEBUCH_TOOL}:*) Bash(git log:*) Bash(git diff:*) Bash(git show:*)"
    if ($TEAM_SMOKE_TEST) { $basis = "$basis Bash($TEAM_SMOKE_TEST)" }
    $plan = "Edit($($TEAM_PLAN_ORDNER.TrimEnd('/'))/**) Write($($TEAM_PLAN_ORDNER.TrimEnd('/'))/**)"
    if ($Rolle -eq 'axel') { return "$basis $plan" }
    return "$basis $plan Edit($($TEAM_TEST_ORDNER.TrimEnd('/'))/**) Write($($TEAM_TEST_ORDNER.TrimEnd('/'))/**)"
}

# --- Modelle ------------------------------------------------------------------
# Loop-Rollen (Ralph, Harry, Marv, Frank): guenstiges Modell.
# Axel & Der Architekt: starkes Modell.
$TEAM_MODEL_LOOP = Team-Default 'TEAM_MODEL_LOOP' 'sonnet'
$TEAM_MODEL_STRONG = Team-Default 'TEAM_MODEL_STRONG' 'opus'

# --- Budget -------------------------------------------------------------------
$TEAM_ROLE_BUDGET_USD = Team-Default 'TEAM_ROLE_BUDGET_USD' '5'
$TEAM_ROLE_HARDCAP_USD = Team-Default 'TEAM_ROLE_HARDCAP_USD' '10'

# --- Auth ---------------------------------------------------------------------
function Team-CfgDir {
    # Unter Windows %APPDATA%\claude-team, sonst ~/.config/claude-team — dort
    # liegt die Ablage des Bash-Zweigs, und eine Maschine hat EINE
    # Auth-Konfiguration, nicht zwei.
    if ($env:APPDATA) { return (Join-Path $env:APPDATA 'claude-team') }
    return (Join-Path $HOME '.config/claude-team')
}

function team_auth_mode_effektiv {
    <#
      Loest NUR den Modus auf (Env AUTH_MODE -> auth-mode-Datei ->
      Rollen-Default) und gibt ihn aus. KEINE Seiteneffekte. Erlaubt
      Orchestratoren, den effektiven Modus zu pruefen, ohne die
      Prozess-Umgebung anzufassen.
    #>
    param([string]$RollenDefault = 'api')
    if ($env:AUTH_MODE) { Write-Output $env:AUTH_MODE; return }
    $cfg = Join-Path (Team-CfgDir) 'auth-mode'
    if (Test-Path $cfg) {
        $wert = (Get-Content -TotalCount 1 -LiteralPath $cfg) -replace '\s', ''
        if ($wert) { Write-Output $wert; return }
    }
    Write-Output $RollenDefault
}

function team_warnung_abo_key {
    <#
      Warnt EINMAL pro Prozessbaum, wenn im Abo-Modus ein ANTHROPIC_API_KEY in
      der Umgebung liegt (das Abo-first-Design still aushebelt). Idempotent
      ueber TEAM_ABO_KEY_WARNUNG_GEZEIGT.
    #>
    if (-not $env:ANTHROPIC_API_KEY) { return $true }
    if ($env:TEAM_ABO_KEY_WARNUNG -eq '0') { return $true }
    if ($env:TEAM_ABO_KEY_WARNUNG_GEZEIGT -eq '1') { return $true }

    if ($env:TEAM_KEY_AUS_FALLBACK -eq '1') {
        # BL-48 (Feld K29/136): Der Key stammt NICHT aus der Umgebung des
        # Menschen, sondern aus einem API-Fallback derselben Prozesskette. Die
        # Profil-Empfehlung zeigte dann auf eine Datei, in der nichts steht,
        # und beschrieb eine Ursache, die nicht vorlag. Deshalb: eigener Satz —
        # und KEIN Setzen der Gezeigt-Marke. Das eine Warnfenster pro
        # Prozessbaum gehoert dem echten Fall (~13,8 USD Leerlauf ueber API).
        Team-Fehler "Hinweis: ANTHROPIC_API_KEY liegt in der Prozess-Umgebung, gesetzt vom API-Fallback"
        Team-Fehler "  eines vorigen Aufrufs (nicht aus dem Profil). Er wird für diesen Abo-Aufruf"
        Team-Fehler "  unmittelbar entfernt — kein Handlungsbedarf (BL-48)."
        return $true
    }

    $keyfile = Join-Path (Team-CfgDir) 'api-key'
    Team-Fehler "WARNUNG: AUTH_MODE=abo, aber ANTHROPIC_API_KEY liegt in der Prozess-Umgebung —"
    Team-Fehler "  die Claude-CLI kann dann den (teuren) API-Weg dem Abo vorziehen."
    Team-Fehler "  Empfohlen: den Key aus den Benutzer-Umgebungsvariablen nehmen und stattdessen in"
    Team-Fehler "  $keyfile (nur fuer dich lesbar) ablegen — siehe CLAUDE.md 'Auth-Modi'."
    $env:TEAM_ABO_KEY_WARNUNG_GEZEIGT = '1'
    return $true
}

function team_resolve_auth_mode {
    param([string]$RollenDefault = 'api')
    $env:AUTH_MODE = (team_auth_mode_effektiv $RollenDefault)
    $keyfile = Join-Path (Team-CfgDir) 'api-key'

    switch ($env:AUTH_MODE) {
        'api' {
            if (-not $env:ANTHROPIC_API_KEY) {
                if (Test-Path $keyfile) {
                    $env:ANTHROPIC_API_KEY = (Get-Content -TotalCount 1 -LiteralPath $keyfile) -replace '\s', ''
                    # BL-48: Merken, dass DIESE Kette den Key gesetzt hat.
                    $env:TEAM_KEY_AUS_FALLBACK = '1'
                } else {
                    Team-Fehler "FEHLER: AUTH_MODE=api, aber weder ANTHROPIC_API_KEY gesetzt noch $keyfile lesbar."
                    return $false
                }
            }
        }
        'abo' {
            team_warnung_abo_key | Out-Null
            # Abo-Abrechnung erzwingen: API-Key aus der Umgebung nehmen.
            $env:ANTHROPIC_API_KEY = $null
        }
        default {
            Team-Fehler "FEHLER: Unbekannter AUTH_MODE '$($env:AUTH_MODE)' (erlaubt: api|abo)."
            return $false
        }
    }
    [Console]::Out.WriteLine("Auth-Modus: $($env:AUTH_MODE)")
    return $true
}

function Team-ClaudeBefehl {
    <#
      R2 aus plans/windows-nativ.md, hier eingeloest: `claude` ist unter Windows
      ein .cmd-Shim, kein Programm. Der Aufrufoperator `&` kommt damit zurecht,
      wenn der Befehl ueber Get-Command aufgeloest wurde; ein roher Aufruf ueber
      System.Diagnostics.Process ohne UseShellExecute nicht.

      Faellt die Aufloesung aus, SIEHT DAS ERGEBNIS AUS WIE EIN AUTH-FEHLER und
      ist keiner — deshalb hier eine eigene, benannte Meldung.
    #>
    $cmd = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Team-Fehler "FEHLER: 'claude' ist ueber PATH nicht auffindbar."
        Team-Fehler "  Das ist KEIN Auth-Fehler. Unter Windows ist claude ein .cmd-Shim;"
        Team-Fehler "  nach der Installation braucht es eine NEUE Sitzung, damit PATH greift."
        return $null
    }
    return $cmd.Source
}

# --- 429-Konfiguration --------------------------------------------------------
$TEAM_429_MAX_RETRIES = Team-Default 'TEAM_429_MAX_RETRIES' '2'
$TEAM_429_MAX_WARTEN = Team-Default 'TEAM_429_MAX_WARTEN' '1800'
$TEAM_429_PUFFER = Team-Default 'TEAM_429_PUFFER' '30'

function Team-429Int {
    <#
      Erzwingt eine reine, nicht-negative Ganzzahl. In Bash ist das ein Riegel
      gegen Command-Injection (HM-17): "$(befehl)" wuerde in einer
      Arithmetik-Expansion ausgefuehrt. PowerShell rechnet nicht so, aber der
      ZWEITE Grund gilt unveraendert: Ein nicht-numerischer Wert liesse den
      TEAM_429_MAX_WARTEN-Deckel fail-open statt fail-safe wirkungslos werden.
    #>
    param([string]$Name, [string]$Wert, [int]$Default)
    if ($Wert -match '^\d+$') { return [int]$Wert }
    Team-Fehler "[team_claude] Ungültiger Wert für $Name=`"$Wert`" (muss eine nicht-negative Ganzzahl sein) — falle auf Default $Default zurück."
    return $Default
}
$TEAM_429_MAX_RETRIES = Team-429Int 'TEAM_429_MAX_RETRIES' $TEAM_429_MAX_RETRIES 2
$TEAM_429_MAX_WARTEN = Team-429Int 'TEAM_429_MAX_WARTEN' $TEAM_429_MAX_WARTEN 1800
$TEAM_429_PUFFER = Team-429Int 'TEAM_429_PUFFER' $TEAM_429_PUFFER 30

function team_429_sleep {
    # TEAM_DRY_RUN=1 oder TEAM_429_SKIP_SLEEP=1 ueberspringen das echte Warten —
    # ein Test darf niemals real bis zu 30 Minuten blockieren.
    param([int]$Sekunden)
    if ($env:TEAM_DRY_RUN -eq '1' -or $env:TEAM_429_SKIP_SLEEP -eq '1') {
        Team-Fehler "[429] (Test) sleep ${Sekunden}s übersprungen."
        return $true
    }
    Start-Sleep -Seconds $Sekunden
    return $true
}

# --- Ergebnis-Pruefung --------------------------------------------------------
function team_result_is_error {
    # $true, wenn die JSON-Ausgabe einen Fehler meldet ODER gar nicht lesbar
    # ist — dann greift z. B. Ralphs API-Fallback.
    param([string]$Datei)
    $daten = Team-JsonLesen $Datei
    if ($null -eq $daten) { return $true }
    if ($daten.PSObject.Properties.Name -contains 'is_error' -and $daten.is_error) { return $true }
    return $false
}

function team_bewerte_ergebnis {
    <#
      HM-33: Der reine Prozess-Exit-Code der CLI darf ein geschriebenes
      Erfolgs-JSON (is_error:false) nicht ueberstimmen — die CLI endet bei
      gesetztem Key mit einer reinen "connectors disabled"-Warnung und Exit != 0,
      obwohl das Ergebnis inhaltlich erfolgreich ist. Das geschriebene JSON ist
      die letzte Instanz.
    #>
    param([string]$Rolle, [string]$Datei, [int]$CliExit)
    if (team_result_is_error $Datei) { return $false }
    if ($CliExit -ne 0) {
        Team-Fehler "[$Rolle] CLI-Exit≠0 trotz gültigem Erfolgs-JSON — werte als Erfolg (vermutlich reine CLI-Warnung, siehe HM-33)."
    }
    return $true
}

function team_promise_in {
    # $true, wenn das Ergebnis <promise>TEXT</promise> enthaelt.
    param([string]$Datei, [string]$Promise)
    $daten = Team-JsonLesen $Datei
    if ($null -eq $daten) { return $false }
    $text = [string]$daten.result
    return $text.Contains("<promise>$Promise</promise>")
}

function team_result_meldet_erfolg {
    # $true, wenn das Log sich selbst fuer erfolgreich erklaert (lesbar,
    # is_error falsch UND subtype "success" — beides muss zutreffen, sonst
    # waere jedes lesbare Log ohne is_error-Feld schon ein "Erfolg").
    param([string]$Datei)
    $daten = Team-JsonLesen $Datei
    if ($null -eq $daten) { return $false }
    if ($daten.PSObject.Properties.Name -contains 'is_error' -and $daten.is_error) { return $false }
    return ($daten.subtype -eq 'success')
}

# --- Session-Limit (429) ------------------------------------------------------
# BL-32: Minuten OPTIONAL — die CLI schreibt bei vollen Stunden nur "resets 3pm"
# ohne ":00" (echter Vorfall, stufe-49-20260712-134536.json). Ohne diese
# Optionalitaet wurde ein Doppel-429 faelschlich als harter Fehler gewertet und
# die Auto-Warte-/Retry-Logik uebersprungen.
#
# HM-21: VOLLSTAENDIGER Abgleich, keine Teilstring-Suche. Ein Claude-generierter
# Erklaertext, der die CLI-Meldung woertlich zitiert, hat immer zusaetzliche
# Woerter davor/danach und besteht den Abgleich deshalb nicht.
$TEAM_429_MUSTER = "you.ve hit your session limit\s*[·\-–:]\s*resets\s+\d{1,2}(:\d{2})?\s*[ap]m(\s*\([^)]*\))?\.?"

function team_result_is_429 {
    param([string]$Datei)
    $daten = Team-JsonLesen $Datei
    if ($null -eq $daten) { return $false }
    if ($daten.PSObject.Properties.Name -contains 'api_error_status' -and
        $daten.api_error_status -eq 429) { return $true }
    $text = ([string]$daten.result).Trim()
    return [regex]::IsMatch($text, "^(?:$TEAM_429_MUSTER)$",
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
}

function team_429_reset_epoch {
    <#
      Liest die Reset-Uhrzeit aus dem freien Ergebnistext ("resets HH:MMpm",
      12h-Format, lokale Zeitzone) und gibt einen Epoch-Zeitpunkt in der Zukunft
      aus. Liegt die Uhrzeit heute schon in der Vergangenheit, gilt sie fuer
      morgen (Reset ueber Mitternacht). Kein/unlesbares Datum -> keine Ausgabe.

      HM-22: durchsucht NUR das Feld "result" und verlangt Wortgrenzen — sonst
      liefert ein Doku-Zitat an anderer Stelle einen falschen Zeitpunkt.
    #>
    param([string]$Datei)
    $daten = Team-JsonLesen $Datei
    if ($null -eq $daten) { return }
    $text = [string]$daten.result
    $m = [regex]::Match($text, '\bresets\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m)\b',
         [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    if (-not $m.Success) { return }

    $stunde = [int]$m.Groups[1].Value % 12
    if ($m.Groups[3].Value.ToLower() -eq 'pm') { $stunde += 12 }
    $minute = 0
    if ($m.Groups[2].Success) { $minute = [int]$m.Groups[2].Value }
    if ($minute -gt 59) { return }

    $jetzt = Get-Date
    $reset = Get-Date -Year $jetzt.Year -Month $jetzt.Month -Day $jetzt.Day `
                      -Hour $stunde -Minute $minute -Second 0 -Millisecond 0
    if ($reset -le $jetzt) { $reset = $reset.AddDays(1) }
    Write-Output ([DateTimeOffset]::new($reset).ToUnixTimeSeconds())
}

# --- Verworfener Versuch (BL-46) ----------------------------------------------
function team_versuch_sichern {
    <#
      BL-46 (Feld K29/135): Ein gescheiterter Abo-Anlauf hinterliess ein Log von
      0 Byte — nach 47 Minuten Laufzeit. Eine Quittung ueber null ist von "hat
      nichts gekostet" nicht zu unterscheiden: Die Summe addierte still 0.0000,
      der Pro-Stufe-Deckel bekam auf diese Haelfte keinen Griff, und die Stufe
      erschien als die BILLIGSTE der Kaskade, obwohl sie als teuerste angesetzt
      war.

      Deshalb ein ERSATZZETTEL mit dem, was belegbar ist — Dauer und die
      ausdrueckliche Aussage "Kosten unbekannt". NICHT geschaetzt: Der Zettel
      behauptet keine Zahl, er macht die Luecke sichtbar. is_error bleibt
      gesetzt, damit der bestehende Fehlerpfad unveraendert greift.

      $true, wenn ein Zettel geschrieben wurde.
    #>
    param([string]$Rolle, [string]$Datei, [int]$Dauer)
    if ($null -ne (Team-JsonLesen $Datei)) { return $false }
    $zettel = [ordered]@{
        is_error = $true; result = ""; total_cost_usd = $null
        team_versuch = "verworfen"; team_dauer_s = $Dauer
    }
    [System.IO.File]::WriteAllText((Team-Pfad $Datei), ($zettel | ConvertTo-Json -Compress),
        (New-Object System.Text.UTF8Encoding($false)))
    return $true
}

function team_versuch_melden {
    # Die Meldung ist der eigentliche Zweck — im Feld fiel die 0-Byte-Datei nur
    # auf, weil ein Mensch den Ordner ansah (BL-46).
    param([string]$Rolle, [string]$Datei, [long]$StartEpoch)
    $dauer = [int]([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - $StartEpoch)
    if (team_versuch_sichern $Rolle $Datei $dauer) {
        Team-Fehler "[$Rolle] VERWORFENER VERSUCH: '$Datei' war nach ${dauer}s nicht als JSON lesbar (0 Byte/abgeschnitten)."
        Team-Fehler "  Ersatzzettel geschrieben — die Dauer ist belegt, die Kosten sind UNBEKANNT und werden"
        Team-Fehler "  in keiner Summe geschätzt. Der Aufruf gilt weiter als Fehler (API-Fallback greift)."
    }
    return $true
}

# --- Kosten -------------------------------------------------------------------
function team_summe_cost_usd {
    <#
      Summe von total_cost_usd ueber MEHRERE Logs — die Kosten EINES
      team_claude-Aufrufs inklusive aller gescheiterten Vorversuche.
      Fehlende/kaputte Dateien zaehlen als 0.

      BL-55 (Kaskade 22 Stufe 93): Der Abo-Versuch scheiterte NACH 1.6806 USD,
      der API-Fallback kostete 0.3984 — gemeldet und gegen den Pro-Stufe-Cap
      geprueft wurden nur die 0.3984. Damit war der Cap umgehbar.
    #>
    param([string[]]$Dateien)
    $gesamt = 0.0
    foreach ($p in $Dateien) {
        $daten = Team-JsonLesen $p
        if ($null -eq $daten) { continue }
        $wert = $daten.total_cost_usd
        if ($null -ne $wert) { $gesamt += [double]$wert }
    }
    Write-Output ($gesamt.ToString('F10', [cultureinfo]::InvariantCulture))
}

function team_extract_cost_usd {
    param([string]$Datei)
    $daten = Team-JsonLesen $Datei
    if ($null -eq $daten -or $null -eq $daten.total_cost_usd) { Write-Output '0'; return }
    Write-Output ([string]$daten.total_cost_usd)
}

# --- Werkzeug-Huellen ---------------------------------------------------------
# Duenne Huellen ueber team/tools/*.py. Sie sind der Grund, warum der
# PowerShell-Zweig kein zweiter Zustandscode ist: Ledger und Beutebuch liegen
# hier wie im Bash-Zweig in denselben Python-Dateien.

function team_kosten_summe { param([string[]]$Ordner)
    Team-Werkzeug $TEAM_KOSTEN_TOOL (@('summe') + $Ordner) }

function team_kosten_seit { param([string]$Seit, [string[]]$Ordner)
    Team-Werkzeug $TEAM_KOSTEN_TOOL (@('summe', '--since', $Seit) + $Ordner) }

function team_kosten_split { param([string[]]$Ordner)
    Team-Werkzeug $TEAM_KOSTEN_TOOL (@('summe', '--split') + $Ordner) }

function team_ledger_summe { param([string]$Pfad = '.budget-ledger')
    Team-Werkzeug $TEAM_KOSTEN_TOOL @('ledger', $Pfad) }

function team_ledger_domaene { param([string]$Domaene, [string]$Pfad = '.budget-ledger')
    Team-Werkzeug $TEAM_KOSTEN_TOOL @('ledger', $Pfad, '--domaene', $Domaene) }

function team_ledger_split { param([string]$Pfad = '.budget-ledger')
    Team-Werkzeug $TEAM_KOSTEN_TOOL @('ledger', $Pfad, '--split') }

function team_akteur_abschluss {
    <#
      Rollen-agnostischer A1-Abschluss (BL-33) fuer JEDE interaktiv arbeitende
      Rolle. BL-26: Alles nach `repo` sind Schalter des WERKZEUGS (--kaskade,
      --addieren, --ersetzen) und werden UNVERAENDERT durchgereicht. Vorher
      liess der Wrapper sie kommentarlos fallen — im Feld buchte ein Aufruf mit
      `--kaskade vor-23` dadurch auf die falsche Kaskade und ersetzte dort eine
      abgeschlossene Zeile ueber 8,4678 USD. Ein Wrapper, der Schalter still
      verschluckt, ist bei JEDER Erweiterung des Werkzeugs eine neue Falle.
    #>
    param([string]$Rolle, [string]$Auth, [string]$Usd, [string]$Domaene,
          [string]$Notiz = '', [string]$Pfad = '.budget-ledger', [string]$Repo = '.',
          [Parameter(ValueFromRemainingArguments = $true)][string[]]$Weitere = @())
    $argumente = @('akteur-abschluss', '--usd', $Usd, '--domaene', $Domaene,
                   '--rolle', $Rolle, '--auth', $Auth)
    if ($Notiz) { $argumente += @('--notiz', $Notiz) }
    $argumente += @('--pfad', $Pfad, '--repo', $Repo)
    Team-Werkzeug $TEAM_KOSTEN_TOOL ($argumente + $Weitere)
}

# --- Plan und Kaskade ---------------------------------------------------------
function team_plan_datei {
    # Aktive Plan-Datei aus der Zeiger-Datei .ralph-plan. Fehlt sie, ist die
    # Ausgabe leer — der Aufrufer faellt auf seinen Default zurueck (kein
    # Abbruch hier; ralph selbst bricht beim Bau ab).
    if (-not (Test-Path '.ralph-plan')) { return }
    $zeile = Get-Content -TotalCount 1 -LiteralPath '.ralph-plan' -ErrorAction SilentlyContinue
    if ($null -eq $zeile) { return }
    Write-Output ($zeile -replace '\s', '')
}

function team_architekt_kaskade {
    <#
      Nummer der AKTIVEN Kaskade, aus dem Namen der Plan-Datei gelesen
      ("plans/ralph-kaskade-13-…" -> "13"). Leer, wenn keine Nummer erkennbar
      ist (frisches Projekt, benannte Kaskade, fehlende .ralph-plan).

      Diese Fassung reisst den Aufrufer unter keiner Strenge weg: Es gibt
      keine Pipeline, deren Zwischenschritt durchschlagen koennte. Der
      Bash-Zweig hatte hier BL-111 — `| head -1` hielt den Rueckgabewert nur
      gegen `set -e`, nicht gegen `set -o pipefail`; seit dem Fix haelt ihn
      dort `{ … ; } || true` unter jeder Stufe. Beide Zweige sagen damit
      dasselbe zu, und der Doppelbahn-Test faehrt beide unter voller Strenge.
    #>
    param([string]$PlanDatei = $null)
    if (-not $PlanDatei) { $PlanDatei = (team_plan_datei) }
    if (-not $PlanDatei) { return }
    $m = [regex]::Match([string]$PlanDatei, 'ralph-kaskade-(\d+)')
    if (-not $m.Success) { return }
    Write-Output $m.Groups[1].Value
}

function team_bau_notiz {
    # Notiztext fuer die ralph-(Bau-)Ledgerzeile, ABGELEITET aus dem Namen der
    # Plandatei statt vom Menschen abgeschrieben (BL-34): Der Mensch denkt beim
    # Abschluss an das Red Team, also stand ueber Ralphs vier Baustufen die
    # Notiz "Harry/Marv-Sweeps + Frank HM-9/HM-10". Zweimal im Feld passiert,
    # beide Male von jemandem, der die Regel kurz vorher zitiert hatte — die
    # Disziplinloesung traegt hier nachweislich nicht.
    param([string]$PlanDatei = $null)
    if (-not $PlanDatei) { $PlanDatei = (team_plan_datei) }
    if (-not $PlanDatei) { return }
    $name = [System.IO.Path]::GetFileNameWithoutExtension($PlanDatei)
    $m = [regex]::Match($name, '^ralph-kaskade-(\d+)-?(.*)$')
    if (-not $m.Success) { return }
    $nummer = $m.Groups[1].Value
    $thema = $m.Groups[2].Value
    if ($thema) { Write-Output "K$nummer $thema" } else { Write-Output "K$nummer" }
}

function team_ralph_cap {
    param([string]$PlanDatei = $null)
    if (-not $PlanDatei) { $PlanDatei = (team_plan_datei) }
    if (-not $PlanDatei -or -not (Test-Path $PlanDatei)) { return }
    $m = [regex]::Match([System.IO.File]::ReadAllText((Team-Pfad $PlanDatei)), '(?m)^\s*RALPH_CAP=(.*)$')
    if (-not $m.Success) { return }
    Write-Output ($m.Groups[1].Value -replace '\s', '')
}

function team_budget_empfehlung {
    # Liest BUDGET_EMPFEHLUNG_USD aus der Plan-Datei. Fehlt Datei/Zeile, ist die
    # Ausgabe leer — der Aufrufer faellt auf seinen Default zurueck (kein
    # Abbruch, keine Raterei).
    param([string]$PlanDatei = $null)
    if (-not $PlanDatei) { $PlanDatei = (team_plan_datei) }
    if (-not $PlanDatei -or -not (Test-Path $PlanDatei)) { return }
    $m = [regex]::Match([System.IO.File]::ReadAllText((Team-Pfad $PlanDatei)), '(?m)^\s*BUDGET_EMPFEHLUNG_USD=(.*)$')
    if (-not $m.Success) { return }
    Write-Output ($m.Groups[1].Value -replace '\s', '')
}

function team_architekt_schaetzung {
    # A2-Live-Schaetzung der Architekt-Kosten (BL-28) — der Architekt laeuft
    # interaktiv ausserhalb von team_claude und schreibt keine Kosten-JSONs.
    # Ohne bisherigen Ledger-Commit (frisches Repo) ist die Ausgabe 0.0000
    # statt eines Abbruchs.
    $ref = & git log -1 --format=%H -- .budget-ledger 2>$null
    if (-not $ref) { Write-Output '0.0000'; return }
    $wert = Team-Werkzeug $TEAM_KOSTEN_TOOL @('architekt-schaetzung', '--since', $ref) 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $wert) { Write-Output '0.0000'; return }
    Write-Output $wert
}

function team_architekt_stand {
    <#
      "USD<TAB>status" fuer die Architekt-Kosten der AKTIVEN Kaskade.

      HM-46: Die Existenz einer echten Zeile wird ueber die TREFFERANZAHL
      geprueft, nicht ueber einen Wertevergleich der Summe gegen "0.0000" —
      eine echte Zeile mit usd=0.0000 ist am Summenwert allein nicht von
      "keine Zeile vorhanden" zu unterscheiden.
    #>
    param([string]$LedgerPfad = '.budget-ledger', [string]$PlanDatei = $null)
    if (-not $PlanDatei) { $PlanDatei = (team_plan_datei) }
    $kaskade = team_architekt_kaskade $PlanDatei
    if ($kaskade) {
        $anzahl = Team-Werkzeug $TEAM_KOSTEN_TOOL @('ledger', $LedgerPfad,
                  '--rolle', 'architekt', '--kaskade', $kaskade, '--anzahl') 2>$null
        if ($anzahl -match '^\d+$' -and [int]$anzahl -gt 0) {
            $echt = Team-Werkzeug $TEAM_KOSTEN_TOOL @('ledger', $LedgerPfad,
                    '--rolle', 'architekt', '--kaskade', $kaskade) 2>$null
            Write-Output "$echt`techt"
            return
        }
    }
    Write-Output "$(team_architekt_schaetzung)`tgeschätzt"
}

function team_kontostand_gesamt {
    # Kumulierter Kontostand = historische Ledger-Basis + aktuelle lokale Logs.
    $basis = [double](team_ledger_summe)
    $split = (team_kosten_split @('.ralph-logs', '.team-logs')) -split "`t"
    $abo = 0.0; $api = 0.0
    if ($split.Count -ge 1 -and $split[0]) { $abo = [double]$split[0] }
    if ($split.Count -ge 2 -and $split[1]) { $api = [double]$split[1] }
    Write-Output (($basis + $abo + $api).ToString('F4', [cultureinfo]::InvariantCulture))
}

function team_logs_archivieren {
    # Manuelles Werkzeug fuer Sonderfaelle. BL-4/2026-08-01: Der regulaere Weg
    # laeuft NICHT mehr hierueber — die kosten.py-Verben archivieren INTERN, im
    # selben Prozess und auf demselben Snapshot, mit dem gezaehlt wurde
    # (HM-39: ein Zwei-Schritt-Ablauf aus Zaehlen hier und Archivieren dort war
    # genau der Race). Wer sie aufruft, archiviert OHNE zu ledgern.
    param([string]$Ordner)
    if (-not (Test-Path $Ordner -PathType Container)) { return $true }
    $archiv = Join-Path $Ordner 'archiv'
    New-Item -ItemType Directory -Force -Path $archiv | Out-Null
    Get-ChildItem -LiteralPath $Ordner -Filter '*.json' -File -ErrorAction SilentlyContinue |
        Move-Item -Destination $archiv -Force
    return $true
}

# --- Budget -------------------------------------------------------------------
function team_resolve_budget_cap {
    # "Nur anheben, nie senken": Hat der Mensch TEAM_BUDGET_USD explizit
    # gesetzt, gewinnt IMMER der aktuelle Wert; sonst gewinnt die Empfehlung,
    # aber nur wenn sie groesser ist.
    param([string]$Aktuell, [string]$UserGesetzt, [string]$Empfehlung)
    if ($UserGesetzt -eq '1') { Write-Output $Aktuell; return }
    if ($Empfehlung) {
        $e = 0.0; $a = 0.0
        if ([double]::TryParse($Empfehlung, [ref]$e) -and [double]::TryParse($Aktuell, [ref]$a)) {
            if ($e -gt $a) { Write-Output $Empfehlung; return }
        }
    }
    Write-Output $Aktuell
}

function team_budget_check {
    <#
      Zwei-Schwellen-Modell (HM-32). ABGESTUFTER Rueckgabewert — Vertrag Punkt 5:
        0 = ok · 1 = Warnschwelle (80 %) · 2 = Soft-Cap · 3 = Hard-Cap

      Die Meldung geht ueber [Console]::Out.WriteLine und NICHT ueber
      Write-Output: Sonst landeten Meldung und Code gemeinsam im Ausgabestrom,
      und der Aufrufer koennte sie nicht trennen. Genau an dieser Stelle kostet
      ein verschluckter Code Geld.
    #>
    param([string]$Kosten, [string]$Soft, [string]$Label, [string]$Hard = '')
    $c = [double]::Parse($Kosten, [cultureinfo]::InvariantCulture)
    $s = [double]::Parse($Soft, [cultureinfo]::InvariantCulture)
    $h = $null
    if ($Hard) { $h = [double]::Parse($Hard, [cultureinfo]::InvariantCulture) }

    if ($null -ne $h -and $h -gt $s -and $c -ge $h) {
        [Console]::Out.WriteLine("HARD-CAP ÜBERSCHRITTEN ($Label): $($c.ToString('F2',[cultureinfo]::InvariantCulture)) USD >= Hard-Cap $($h.ToString('F2',[cultureinfo]::InvariantCulture)) USD — harter Abbruch.")
        return 3
    }
    if ($c -ge $s) {
        [Console]::Out.WriteLine("SOFT-CAP ÜBERSCHRITTEN ($Label): $($c.ToString('F2',[cultureinfo]::InvariantCulture)) USD >= Soft-Cap $($s.ToString('F2',[cultureinfo]::InvariantCulture)) USD.")
        return 2
    }
    if ($c -ge 0.8 * $s) {
        [Console]::Out.WriteLine("WARNSCHWELLE ($Label): $($c.ToString('F2',[cultureinfo]::InvariantCulture)) USD >= 80 % von $($s.ToString('F2',[cultureinfo]::InvariantCulture)) USD — Strippenzieher informieren.")
        return 1
    }
    return 0
}

# --- Lock ---------------------------------------------------------------------
$script:TeamLockStrom = $null

function team_lock {
    <#
      Eine Pipeline zur Zeit. Laeuft das Skript unterhalb der Vollautomatik
      (TEAM_LOCK_HELD=1), wird nicht erneut gelockt.

      HIER IST DER WINDOWS-ZWEIG BESSER ALS DER BASH-ZWEIG: FileShare::None
      wird vom Betriebssystem DURCHGESETZT. flock ist kooperativ — es wirkt nur,
      solange alle Beteiligten mitspielen, und unter WSL 1 gab es dafuer gar
      keine Zusicherung. Genau diese Problemklasse hat den Windows-Zweig
      ausgeloest.

      Der Strom bleibt im Modulzustand offen, solange der Prozess laeuft — das
      ist die Sperre. Ihn zu schliessen gibt sie frei (team_unlock).
    #>
    param([string]$Label)
    if ($env:TEAM_LOCK_HELD -eq '1') { return $true }
    try {
        $script:TeamLockStrom = [System.IO.File]::Open('.team-loop.lock',
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None)
    } catch {
        Team-Fehler "[$Label] Eine andere T.E.A.M.-Pipeline läuft bereits (.team-loop.lock) — Abbruch."
        return $false
    }
    $env:TEAM_LOCK_HELD = '1'
    return $true
}

function team_unlock {
    # Gegenstueck zu team_lock. In Bash gibt der Prozessexit den Deskriptor
    # frei; hier ebenso, aber ein ausdruecklicher Weg erspart langlebigen
    # Sitzungen (Tests!) das Warten auf den Prozessexit.
    if ($script:TeamLockStrom) {
        $script:TeamLockStrom.Close()
        $script:TeamLockStrom = $null
    }
    $env:TEAM_LOCK_HELD = $null
    return $true
}

# --- Briefings ----------------------------------------------------------------
function team_briefing {
    # Fallback (Pflicht): fehlt die Datei oder ist sie leer, kommt exakt die
    # alte Zeile zurueck — kein Abbruch, keine Fehlermeldung, damit ein Fehler
    # hier nie einen Lauf lahmlegt.
    param([string]$Rolle)
    $datei = "team/prompts/rolle-$Rolle.md"
    if ((Test-Path $datei -PathType Leaf) -and (Get-Item $datei).Length -gt 0) {
        Write-Output ([System.IO.File]::ReadAllText((Team-Pfad $datei)))
    } else {
        Write-Output "Rolle siehe CLAUDE.md — lies sie zuerst."
    }
}

# --- Read-Only-Guard (Linie 3 — deterministisch, CHIRURGISCH) -----------------
# Laufzeitartefakte, die die SHELL um den Rollenaufruf herum schreibt — nicht
# die Rolle. BL-24 macht diese Liste zur Pflicht statt zur Kosmetik: Seit der
# Rollback Verzeichnisse wirklich entfernen kann, wuerde er hier die Kostenlogs
# DES LAUFENDEN AUFRUFS loeschen — ein selbstverschuldeter BL-4, ausgeloest
# ausgerechnet vom Waechter.
$TEAM_GUARD_LAUFZEIT = '^(\.team-logs/|\.ralph-logs/|\.team-loop\.lock$|\.ralph-state$|\.harry-state$|\.marv-state$|\.frank-attempts$|\.team-focus-[a-z]+$)'

$script:TEAM_GUARD_HASH = ''
$script:TEAM_GUARD_VORHER = @()

function team_guard_schnappschuss {
    # Je schmutzigem Pfad eine Zeile "<blob-hash> <pfad>". Was sich nicht als
    # Datei lesen laesst (Loeschung, Umbenennung, untracked Verzeichnis)
    # bekommt "-" und gilt nur dann als fremd, wenn es das auch bleibt.
    $zeilen = @()
    foreach ($z in @(& git status --porcelain 2>$null)) {
        if (-not $z -or $z.Length -lt 4) { continue }
        $pfad = $z.Substring(3)
        if (Test-Path -LiteralPath $pfad -PathType Leaf) {
            $hash = & git hash-object -- $pfad 2>$null
            if (-not $hash) { $hash = '-' }
        } else { $hash = '-' }
        $zeilen += "$hash $pfad"
    }
    Write-Output $zeilen
}

function team_guard_begin {
    <#
      Merkt sich HEAD als Rollback-Punkt UND den Ausgangszustand des
      Arbeitsbaums (BL-16).

      WARUM ES DEN SCHNAPPSCHUSS GIBT (Feld K2, 2026-08-01): Der Guard hatte
      KEINEN Ausgangszustand. Er las nur "welche Pfade sind jetzt schmutzig" und
      schrieb jeden davon der laufenden Rolle zu — jeder fremde Schreiber wurde
      angelastet UND hart zurueckgesetzt. Real eingetreten: Axels korrekte
      Ermittlung zaehlte als Fehlschlag (dritte Stagnation -> Lauf gestoppt),
      und die zurueckgerollten Pfade waren die Arbeit einer parallel laufenden
      Sitzung.

      Der Schnappschuss haelt BLOB-HASHES, nicht nur Pfade: Ein reiner
      Pfadabgleich wuerde eine Rolle freisprechen, die eine ohnehin schon
      schmutzige Datei zusaetzlich veraendert. Unveraendert => fremd.
      Veraendert => ihre Sache.
    #>
    $script:TEAM_GUARD_HASH = (& git rev-parse HEAD 2>$null)
    $script:TEAM_GUARD_VORHER = @(team_guard_schnappschuss)
    if ($script:TEAM_GUARD_VORHER.Count) {
        # Laut warnen, statt still weiterzulaufen: Der Lauf soll gar nicht erst
        # blind starten, und der Mensch am Terminal soll wissen, dass hier zwei
        # Schreiber unterwegs sein koennten.
        Team-Fehler "[guard] WARNUNG: Der Arbeitsbaum ist beim Rollenstart NICHT sauber:"
        foreach ($e in $script:TEAM_GUARD_VORHER) {
            Team-Fehler ("  " + ($e -replace '^\S+\s', ''))
        }
        Team-Fehler "[guard] Diese Pfade werden der Rolle nicht angelastet, solange sie unverändert bleiben."
        Team-Fehler "[guard] Zwei schreibende Instanzen auf einem Arbeitsbaum sind trotzdem unzulässig — bitte committen."
    }
    return $true
}

function team_guard_fremdpfade {
    # Pfade aus dem Schnappschuss, die sich seit dem Rollenstart NICHT
    # veraendert haben. Sie gehoeren nicht dieser Rolle.
    $treffer = @()
    foreach ($eintrag in $script:TEAM_GUARD_VORHER) {
        if (-not $eintrag) { continue }
        $trenn = $eintrag.IndexOf(' ')
        if ($trenn -lt 0) { continue }
        $hash = $eintrag.Substring(0, $trenn)
        $pfad = $eintrag.Substring($trenn + 1)
        if (Test-Path -LiteralPath $pfad -PathType Leaf) {
            $jetzt = & git hash-object -- $pfad 2>$null
            if (-not $jetzt) { $jetzt = '-' }
        } else { $jetzt = '-' }
        if ($jetzt -eq $hash) { $treffer += $pfad }
    }
    Write-Output $treffer
}

function team_fremd_ausfiltern {
    <#
      Entfernt aus der Pfadliste alles, was team_guard_fremdpfade als fremd
      ausweist — mit einer Feinheit, die beim Bau von BL-114 aufgefallen ist
      und die auch den Guard betraf:

      `git status --porcelain` meldet ein untracked VERZEICHNIS als EINEN
      Eintrag mit Schraegstrich (`plans/`), nicht als Liste seiner Dateien —
      dieselbe Eigenheit, an der BL-24 haengt. Der Startschnappschuss haelt
      deshalb `plans/` fest. Committet eine Rolle eine fremde Datei aus so
      einem Ordner versehentlich mit (`git add -A` ist bei bypassPermissions
      der Normalfall), taucht sie danach als `plans/closeout.md` auf und passt
      auf KEINEN Eintrag der Fremdliste mehr. Ein reiner Zeichenvergleich
      haette sie geloescht — also genau die uncommittete Closeout-Ausgabe,
      wegen der BL-114 geschrieben wurde. Deshalb gilt ein Pfad auch dann als
      fremd, wenn er UNTER einem fremden Ordnereintrag liegt.

      Bewusst in diese Richtung konservativ: Legt die Rolle eine eigene Datei
      in einen bereits fremden Ordner, bleibt sie liegen. Ein Rest, der liegen
      bleibt, ist sichtbar und behebbar; fremde Arbeit, die geloescht wurde,
      ist weg.
    #>
    param([string[]]$Pfade)

    $fremd = @(team_guard_fremdpfade)
    if (-not $fremd.Count) { return @($Pfade) }
    return @(@($Pfade) | Where-Object {
        $p = $_
        $treffer = @($fremd | Where-Object {
            $p -eq $_ -or ($_.EndsWith('/') -and $p.StartsWith($_))
        })
        -not $treffer.Count
    })
}

function team_pfade_zuruecksetzen {
    <#
      Setzt JEDEN uebergebenen Pfad EINZELN auf den Stand von <Hash> zurueck:
      beim Start getrackt -> `git checkout <Hash> -- <Pfad>`, neu entstanden ->
      gezielt entfernen. Gibt die Pfade zurueck, die danach WEITERHIN abweichen
      (leer = vollzogen).

      Herausgeloest aus team_guard_verify (BL-114). Der Grund ist nicht
      Aufraeumen: Die Einstiegsskripte rollten bis dahin mit einem blanken
      `git reset --hard` + `git clean -fd` zurueck — also mit genau dem, was
      der Kopf dieses Abschnitts sich seit dem 2026-07-10 verbietet. Die Lehre
      war am Guard angewandt und am Aufrufer nicht. Eine gemeinsame Funktion
      macht das Auseinanderlaufen unmoeglich, statt es nur zu verbieten.
    #>
    param([string]$Rolle, [string]$Hash, [string[]]$Pfade)

    $rest = @()
    foreach ($pfad in @($Pfade)) {
        if (-not $pfad) { continue }
        & git cat-file -e "$($Hash):$pfad" 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            # War beim Start getrackt -> auf Startstand zurueckholen.
            & git checkout $Hash -- $pfad 2>$null | Out-Null
        } else {
            # Neu entstanden -> gezielt entfernen. Die Plausibilitaetspruefung
            # steht davor, weil ein rekursives Entfernen auf einem Pfad aus
            # `git status` genau die Zeile ist, die man einmal richtig schreibt
            # und nie wieder ansieht. Der Pfad kommt ausschliesslich aus
            # `git status --porcelain` innerhalb des Repos, ist also relativ und
            # ohne fuehrenden Schraegstrich. Alles andere wird NICHT entfernt.
            if ($pfad.StartsWith('/') -or $pfad.StartsWith('\') -or
                $pfad.Contains('..') -or $pfad -match '^[A-Za-z]:') {
                Team-Fehler "[$Rolle] Guard: '$pfad' sieht nicht nach einem Repo-Pfad aus — NICHT entfernt."
                $rest += $pfad
                continue
            }
            & git rm -rf --cached -- $pfad 2>$null | Out-Null
            # BL-24: rekursiv. `git status --porcelain` meldet ein untracked
            # Verzeichnis als EINEN Eintrag mit Schraegstrich (`raw/`), nicht
            # als Liste seiner Dateien; ein nicht-rekursives Entfernen
            # scheiterte daran still, waehrend elf Zeilen vorher schon
            # "chirurgischer Rollback" gedruckt stand.
            Remove-Item -LiteralPath $pfad -Recurse -Force -ErrorAction SilentlyContinue
        }
        # Der Erfolg wird GEPRUEFT, nicht angenommen. Sonst wiederholt sich die
        # eigentliche Lehre dieses Fundes bei der naechsten Ursache.
        if (Test-Path -LiteralPath $pfad) {
            & git diff --quiet $Hash -- $pfad 2>$null | Out-Null
            if ($LASTEXITCODE -ne 0) { $rest += $pfad }
        }
    }
    return $rest
}

function team_rollback_rolle {
    <#
      Verwirft den GESAMTEN Beitrag eines Rollenlaufs — Commits, Aenderungen an
      getrackten Dateien und neu angelegte Dateien —, aber NUR seinen.

      BL-114: Hier stand in frank.ps1, axel.ps1 und redteam.ps1 ein blankes
      `git reset --hard $startHash` (in frank zusaetzlich `git clean -fd` ohne
      Pfadeinschraenkung). Das trifft JEDE uncommittete Arbeit im Zielprojekt,
      nicht nur die der Rolle: eine parallele Sitzung, eine Handaenderung, eine
      noch nicht committete Closeout-Ausgabe des Architekten.

      Drei Dinge bleiben ausdruecklich unangetastet:
        * Pfade aus dem Startschnappschuss, die sich seither nicht veraendert
          haben (team_guard_fremdpfade) — fremde Arbeit.
        * Laufzeitartefakte (TEAM_GUARD_LAUFZEIT) — dort liegen die Kostenlogs
          DIESES Aufrufs; sie zu loeschen waere ein selbstverschuldeter BL-4.
        * Gestagte fremde Aenderungen: HEAD wandert mit `--soft` zurueck, der
          Arbeitsbaum bleibt dabei unberuehrt.

      `git clean -fd` deckte den Fall ab, dass Frank mit bypassPermissions auch
      AUSSERHALB des Produktivordners Dateien anlegt (HM-29). Das leistet die
      Pfadliste weiter: `git status --porcelain` meldet jede nicht ignorierte
      neue Datei im ganzen Repo — nur eben namentlich statt pauschal.

      $true = vollzogen · $false = Reste geblieben (gemeldet)
    #>
    param([string]$Rolle, [string]$StartHash)

    $pfade = @()
    foreach ($p in @(& git diff --name-only $StartHash HEAD 2>$null)) {
        if ($p) { $pfade += $p }
    }
    foreach ($z in @(& git status --porcelain 2>$null)) {
        if ($z -and $z.Length -ge 4) { $pfade += $z.Substring(3) }
    }
    $pfade = @($pfade | Sort-Object -Unique |
               Where-Object { $_ -notmatch $TEAM_GUARD_LAUFZEIT })
    $pfade = @(team_fremd_ausfiltern $pfade)
    if ((& git rev-parse HEAD 2>$null) -ne $StartHash) {
        & git reset --soft $StartHash 2>$null | Out-Null
    }
    $rest = @(team_pfade_zuruecksetzen $Rolle $StartHash $pfade)
    if ($rest.Count) {
        Team-Fehler "[$Rolle] ROLLBACK UNVOLLSTÄNDIG — diese Pfade stehen weiterhin abweichend im Baum:"
        foreach ($p in $rest) { Team-Fehler "  $p" }
        Team-Fehler "  Von Hand prüfen und zurücknehmen."
        return $false
    }
    return $true
}

function team_guard_verify {
    <#
      Ermittelt geaenderte Pfade (committet seit Start + Arbeitsverzeichnis),
      die NICHT auf die Whitelist passen. Bei Verletzung wird NUR jeder
      einzelne Verletzer-Pfad zurueckgesetzt — NIEMALS blanko
      `git reset --hard`/`clean -fd`. (Lektion 2026-07-10: ein blindes
      reset+clean loeschte einmal die gesamte uncommittete Team-Infrastruktur.
      Nie wieder.)

      $true = sauber · $false = Uebergriff
    #>
    param([string]$Rolle, [string]$Whitelist)

    $roh = @()
    foreach ($p in @(& git diff --name-only $script:TEAM_GUARD_HASH HEAD 2>$null)) {
        if ($p) { $roh += $p }
    }
    foreach ($z in @(& git status --porcelain 2>$null)) {
        if ($z -and $z.Length -ge 4) { $roh += $z.Substring(3) }
    }
    $roh = @($roh | Sort-Object -Unique |
             Where-Object { $_ -notmatch $Whitelist -and $_ -notmatch $TEAM_GUARD_LAUFZEIT })
    if (-not $roh.Count) { return $true }

    # BL-114: derselbe Filter wie im Rollback — er kennt auch den Fall, dass
    # eine fremde Datei aus einem untracked ORDNER mitcommittet wurde und
    # danach unter ihrem vollen Pfad auftaucht.
    $verletzungen = @(team_fremd_ausfiltern $roh)
    $nichtAngelastet = @($roh | Where-Object { $verletzungen -notcontains $_ })

    if (-not $verletzungen.Count) {
        # Der Verdacht loest sich auf. Genau dieser Fall wurde im Feld einer
        # Rolle angelastet, die ihn nicht verursacht hatte.
        Team-Fehler "[$Rolle] Guard: Pfade außerhalb der Whitelist geändert, aber ALLE waren beim Rollenstart bereits geändert und sind es unverändert — nicht dieser Rolle zugeschrieben, kein Rollback:"
        foreach ($p in $nichtAngelastet) { Team-Fehler "  $p" }
        return $true
    }

    # Die Meldung trennt die beiden Faelle ausdruecklich sprachlich. Im Feld
    # wurde der Uebergriff zunaechst der falschen Rolle zugeschrieben, weil die
    # Pfadliste im Log neben ihrem Namen stand — belegt war das nirgends.
    Team-Fehler "[$Rolle] GUARD-VERLETZUNG — DIESE ROLLE hat die folgenden Pfade geändert:"
    foreach ($p in $verletzungen) { Team-Fehler $p }
    if ($nichtAngelastet.Count) {
        Team-Fehler "[$Rolle] NICHT angelastet (beim Rollenstart bereits geändert, seither unverändert):"
        foreach ($p in $nichtAngelastet) { Team-Fehler "  $p" }
    }

    $rest = @(team_pfade_zuruecksetzen $Rolle $script:TEAM_GUARD_HASH $verletzungen)

    if ($rest.Count) {
        Team-Fehler "[$Rolle] Guard: ROLLBACK UNVOLLSTÄNDIG — diese Pfade stehen weiterhin abweichend im Baum:"
        foreach ($p in $rest) { Team-Fehler "  $p" }
        Team-Fehler "  Von Hand prüfen und zurücknehmen; der Lauf gilt als Übergriff."
    } else {
        Team-Fehler "[$Rolle] Guard: chirurgischer Rollback vollzogen."
    }
    return $false
}

function team_guard_urteil {
    <#
      BL-16 Ebene 2: Ein Guard-Uebergriff kassiert den UEBERGRIFF, nicht die
      Arbeit. Liegt das eigentliche Ergebnis der Rolle vor, ist die Leistung
      erbracht — der Grenzuebertritt ist bereits chirurgisch zurueckgerollt und
      laut gemeldet, und ein zusaetzlicher Fehlschlag bestraft nur noch das
      Falsche: Er speist den Stagnationszaehler und stoppt den Lauf. Genau so
      ging im Feld ein fertiger, korrekter Ermittlungsbericht als "Aufruf
      fehlgeschlagen" durch.
    #>
    param([string]$Rolle, [int]$Uebergriff, [int]$Ergebnis)
    if ($Uebergriff -eq 0) { return $true }
    if ($Ergebnis -eq 1) {
        Team-Fehler "[$Rolle] Guard-Übergriff kassiert, Ergebnis zählt — die Arbeit ist geleistet, zurückgerollt wurde nur der Grenzübertritt."
        return $true
    }
    Team-Fehler "[$Rolle] Guard-Übergriff UND kein vollständiges Ergebnis — Aufruf gilt als gescheitert."
    return $false
}

# --- Substanz-Anker fuer Frank ------------------------------------------------
function team_diff_beruehrt_fund {
    # HM-29: Franks Dreisatz prueft sonst nur FORM (Promise, Commit-Muster,
    # Beutebuch-Status), nie ob der committete Diff mit dem gemeldeten Fund zu
    # tun hat. Nennt der Fund KEINE Datei, gilt die Pruefung als bestanden —
    # kein falscher Blocker bei rein beschreibenden Funden.
    param([string]$Hm, [string]$Start)
    $fundDateien = @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('dateien', $Hm) 2>$null)
    $fundDateien = @($fundDateien | Where-Object { $_ })
    if (-not $fundDateien.Count) { return $true }
    $diffDateien = @(& git diff --name-only $Start HEAD 2>$null)
    foreach ($f in $fundDateien) {
        foreach ($d in $diffDateien) {
            if ($d -and $d.EndsWith($f)) { return $true }
        }
    }
    return $false
}

function team_reproducer_liegt_vor {
    <#
      BL-28: Der Substanz-Anker oben besteht, sobald IRGENDEINE im Fundblock
      referenzierte Datei im Diff liegt — und das ist regelmaessig die
      Produktivdatei, die der Fix ohnehin anfasst. Im Feld reservierte HM-30
      einen Reproducer-Pfad, Franks Fix beruehrte CHANGELOG und Produktivdatei,
      die Testdatei entstand NIE, und der Anker war zufrieden.

      Diese Funktion prueft die EINE Datei, deren Zweck die Absicherung ist.
      $true, wenn sie existiert ODER der Fund keine lesbare Reproducer-Zeile
      traegt (dafuer ist der Lint VOR dem Lauf zustaendig, BL-29 — nicht diese
      Pruefung nach dem Lauf). $false nur im benannten Fall: Pfad reserviert,
      Datei nicht angelegt.
    #>
    param([string]$Hm)
    $pfad = Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('reproducer', $Hm) 2>$null
    if (-not $pfad) { return $true }
    $pfad = ([string]$pfad).Trim()
    if (-not $pfad) { return $true }
    if (Test-Path -LiteralPath $pfad) { return $true }
    return $false
}

# --- Vierter Ausgang: Sitzung beendet, Auftrag unquittiert (BL-41) ------------
function team_quittung_fehlt_melden {
    <#
      Neben Erfolg, echtem Fehler und Session-Limit gibt es einen vierten
      Ausgang: Die Rolle beendet ihre Antwort freiwillig, ohne den Auftrag zu
      quittieren — typischerweise, weil sie einen Hintergrund-Task/Wakeup
      gestartet hat und auf eine Benachrichtigung wartet, die headless nie
      eintrifft. Das JSON traegt dann subtype=success, is_error=false — fuer
      team_result_is_error ein sauberer Erfolg. Nur das fehlende Promise
      verraet den Fall.

      NICHT auf Vokabeln geprueft: Die Vorfaelle formulierten es jedes Mal
      anders; die naechste Variante schreibt jemand morgen. Geprueft wird die
      STRUKTUR — kein Promise, aber das Log erklaert sich selbst fuer
      erfolgreich.

      $true = benannter Fall erkannt und gemeldet · $false = gewoehnlicher
      Fehlschlag (der Aufrufer meldet dann wie bisher).
    #>
    param([string]$Rolle, [string]$Datei, [string]$Was,
          [Parameter(ValueFromRemainingArguments = $true)][string[]]$Schritte = @())
    if (-not (team_result_meldet_erfolg $Datei)) { return $false }
    Team-Fehler "[$Rolle] STUFE FERTIG, QUITTUNG FEHLT (BL-41) — $Was"
    Team-Fehler "  Das Log meldet sich selbst als Erfolg (subtype=success, is_error=false), gibt aber"
    Team-Fehler "  keine Quittung. Das ist der benannte vierte Ausgang: Die Sitzung hat sich beendet,"
    Team-Fehler "  meist im Warten auf einen Hintergrund-Task/Monitor/Wakeup, den es headless nicht gibt."
    Team-Fehler "  Die Arbeit ist in diesem Fall meist FERTIG — viermal im Feld, 19,47 USD. Prüfe in"
    Team-Fehler "  dieser Reihenfolge, BEVOR du neu startest (ein Neulauf wirft die bezahlte Arbeit weg):"
    foreach ($s in $Schritte) { Team-Fehler "    - $s" }
    Team-Fehler "  Log: $Datei"
    return $true
}

function team_quittung_selbstpruefung {
    <#
      BL-110: Die Erkennung oben ist richtig, aber sie haelt den Lauf an und
      legt einem Menschen eine Pruefliste vor, deren Schritte IMMER dieselben
      sind. Im Feld ist der Fall in NEUN Kaskaden aufgetreten und JEDES Mal
      lautete das Ergebnis "Arbeit fertig, nur die Quittung fehlt". Eine
      Pruefliste, die neunmal dasselbe ergibt, ist eine Funktion, die noch
      niemand geschrieben hat.

      WAS SIE NICHT TUT: auf Verdacht quittieren. Faellt auch nur eine Pruefung
      durch, gibt sie $false zurueck und der Aufrufer meldet unveraendert an
      den Menschen. Der teure Fehler waere, eine unfertige Stufe
      durchzuwinken — deshalb ist jede Pruefung ein UND, keine Mehrheit, und im
      Zweifel gilt "nicht bestanden".
    #>
    param([string]$Rolle, [string]$Stufe)
    if ($env:TEAM_QUITTUNG_AUTO -eq '0') { return $false }
    $testOrdner = if ($TEAM_TEST_ORDNER) { $TEAM_TEST_ORDNER } else { 'tests/' }

    Team-Fehler "[$Rolle] Selbstprüfung des vierten Ausgangs (BL-41) für Stufe ${Stufe}:"

    # (1) Hat die Sitzung ueberhaupt etwas hinterlassen? Ohne Arbeit gibt es
    #     nichts zu quittieren — dann ist es kein "fertig ohne Quittung",
    #     sondern eine Stufe, die nie angefangen hat.
    $uncommittet = @(& git status --porcelain 2>$null | Where-Object { $_ })
    $betreff = & git log -1 --pretty=%s 2>$null
    $hatArbeit = $uncommittet.Count -gt 0 -or
                 ($betreff -and ($betreff -like "*stufe$Stufe*" -or $betreff -like "*Stufe $Stufe*"))
    if (-not $hatArbeit) {
        Team-Fehler "    ✗ Kein Commit für Stufe $Stufe und keine uncommitteten Änderungen."
        Team-Fehler "      Die Sitzung hat nichts hinterlassen — das ist NICHT der vierte Ausgang."
        return $false
    }
    Team-Fehler "    ✓ Arbeit vorhanden (uncommittet und/oder Commit der Stufe)."

    # (2) BL-135: Gibt es eine ZUSICHERUNG? Genau der Punkt, an dem die
    #     Pruefliste fuer den Menschen blind war. Eine Stufe, die Produktivcode
    #     baut und keine einzige Testdatei beruehrt, ist nicht fertig — egal wie
    #     gruen der Baum ist, denn der Bestand deckt das Neue nicht ab.
    if ($uncommittet.Count) {
        $dateien = @($uncommittet | ForEach-Object { $_.Substring(3) })
    } else {
        $dateien = @(& git show --name-only --pretty=format: HEAD 2>$null | Where-Object { $_ })
    }
    $hatZusicherung = @($dateien | Where-Object { $_ -match "^`"?$([regex]::Escape($testOrdner))" }).Count -gt 0
    if (-not $hatZusicherung) {
        Team-Fehler "    ✗ Keine Datei unter $testOrdner berührt (BL-135)."
        Team-Fehler "      Die Stufe hat keine nachweisbare Zusicherung — grüner Baum beweist hier"
        Team-Fehler "      nichts, weil der Bestand das Neue nicht prüft. Das gehört an den Menschen."
        return $false
    }
    Team-Fehler "    ✓ Zusicherung vorhanden — mindestens eine Datei unter $testOrdner berührt (BL-135)."

    # (3) Ist der Baum gruen? Der teuerste, aber unverzichtbare Schritt.
    if (-not $TEAM_SMOKE_TEST) {
        Team-Fehler "    ✗ Kein TEAM_SMOKE_TEST konfiguriert — ohne Verifikationsbefehl wird nicht"
        Team-Fehler "      automatisch quittiert."
        return $false
    }
    Team-Fehler "    … Smoke-Test läuft ($TEAM_SMOKE_TEST) …"
    Team-Werkzeug $TEAM_SMOKE_TEST @() 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Team-Fehler "    ✗ $TEAM_SMOKE_TEST ist ROT."
        Team-Fehler "      Das gehört an den Menschen: Erst prüfen, WO — sind ausschließlich die von"
        Team-Fehler "      DIESER Stufe neu angelegten Testdateien rot, ist der Testaufbau der"
        Team-Fehler "      wahrscheinlichere Schuldige als der Produktivcode (BL-61)."
        return $false
    }
    Team-Fehler "    ✓ $TEAM_SMOKE_TEST ist grün."
    Team-Fehler "[$Rolle] Alle drei Prüfungen bestanden — Stufe $Stufe wird automatisch quittiert."
    return $true
}

function Team-ClaudeSchreiben {
    <#
      Ruft die CLI und schreibt ihre Ausgabe als UTF-8 OHNE BOM. Gibt den
      Exit-Code der CLI zurueck.

      WARUM NICHT EINFACH `> $Out`: Die Umlenkung schreibt mit der
      Standardkodierung der Sitzung. Unter pwsh 7 ist das heute UTF8NoBOM, unter
      Windows PowerShell 5.1 war es UTF-16LE, und ein `$PSDefaultParameterValues`
      im Benutzerprofil kann es jederzeit umstellen.

      Was daran teuer ist: Diese Datei liest anschliessend team/tools/kosten.py
      mit `json.load`, und Python bricht an einem BOM ab
      ("Unexpected UTF-8 BOM"). kosten.py faengt solche Fehler ab und zaehlt die
      Datei still als 0.0000 — also genau die Fehlerklasse aus BL-46 und BL-55:
      eine bezahlte Stufe erscheint als die billigste der Kaskade, der
      Pro-Stufe-Deckel bekommt keinen Griff, und niemand merkt es.

      Die Kodierung der Kostenlogs darf deshalb nicht an einer Voreinstellung
      haengen. Sie wird hier festgelegt.
    #>
    param([string]$Claude, [string]$Prompt, [string]$Modell, [string]$Out,
          [string[]]$Weitere = @())
    $roh = & $Claude -p $Prompt --model $Modell --output-format json @Weitere
    $code = $LASTEXITCODE
    [System.IO.File]::WriteAllText((Team-Pfad $Out), (($roh -join "`n")),
        (New-Object System.Text.UTF8Encoding($false)))
    return $code
}

# --- Zentraler Claude-Aufruf --------------------------------------------------
function team_claude {
    <#
      Abo-first mit automatischem API-Fallback: Auth wird pro Aufruf frisch
      aufgeloest; scheitert der Abo-Aufruf, folgt genau EIN API-Retry. Danach
      stehen $TEAM_LAST_COST (USD) und $TEAM_LAST_OUT (Log-Datei).

      TEAM_LAST_COST ist die Summe ALLER Versuche dieses Aufrufs — sonst waere
      der Pro-Stufe-Cap durch einen teuren Fehlversuch umgehbar (BL-55: 4,9 USD
      Abo-Fehlversuch + 4,9 USD API meldeten 4,9 gegen einen 5-USD-Deckel).

      Der API-Key wird dem Aufruf AUFRUF-LOKAL vorangestellt: Ein blosses
      Setzen der Prozessvariablen reichte im Bash-Zweig nicht — die CLI
      bevorzugte im selben Prozess weiterhin die limitierte Abo-Session und
      der Fallback lief real erneut ins Abo-429.

      Rueckgabe: 0 = Erfolg · 1 = Fehler · 42 = Pausen-Signal (429)
      Das ist ein ABGESTUFTER Code (Vertrag Punkt 5).
    #>
    param([string]$Rolle, [string]$Modell, [string]$Out, [string]$Prompt,
          [Parameter(ValueFromRemainingArguments = $true)][string[]]$Weitere = @())

    $script:TEAM_LAST_PAUSE = 0
    $script:TEAM_LAST_RESET = ''

    if ($env:TEAM_DRY_RUN -eq '1') {
        $stub = [ordered]@{ result = [string]$env:TEAM_DRY_RESULT
                            total_cost_usd = 0.01; is_error = $false }
        [System.IO.File]::WriteAllText((Team-Pfad $Out), ($stub | ConvertTo-Json -Compress),
            (New-Object System.Text.UTF8Encoding($false)))
        $script:TEAM_LAST_COST = '0.01'
        $script:TEAM_LAST_OUT = $Out
        [Console]::Out.WriteLine("[$Rolle] DRY-RUN — kein Claude-Aufruf.")
        return 0
    }

    $env:AUTH_MODE = $script:TEAM_AUTH_USER
    if (-not (team_resolve_auth_mode 'abo')) { return 1 }
    $claude = Team-ClaudeBefehl
    if (-not $claude) { return 1 }

    $versuchLogs = @()
    $fehler = $false

    $t0 = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $cliExit = Team-ClaudeSchreiben $claude $Prompt $Modell $Out $Weitere
    team_versuch_melden $Rolle $Out $t0 | Out-Null
    $versuchLogs += $Out
    $fehler = -not (team_bewerte_ergebnis $Rolle $Out $cliExit)

    # Bei JEDEM Abo-Fehler — Timeout, normaler Fehler ODER 429 — SOFORT den
    # API-Fallback versuchen: Der Key hat ein eigenes, separates Kontingent
    # (bewiesen 2026-07-11), hilft also auch bei einem Abo-429.
    if ($fehler -and $env:AUTH_MODE -eq 'abo') {
        [Console]::Out.WriteLine("[$Rolle] Abo-Aufruf fehlgeschlagen (Timeout/Limit/429?) — einmaliger API-Fallback. Log: $Out")
        $env:AUTH_MODE = 'api'
        if (-not (team_resolve_auth_mode)) { return 1 }
        $Out = ($Out -replace '\.json$', '') + '-api-fallback.json'
        $t0 = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        $cliExit = Team-ClaudeSchreiben $claude $Prompt $Modell $Out $Weitere
        team_versuch_melden $Rolle $Out $t0 | Out-Null
        $versuchLogs += $Out
        $fehler = -not (team_bewerte_ergebnis $Rolle $Out $cliExit)
    }

    # 429-Sonderbehandlung auf dem FINALEN Ergebnis: nur wenn auch der API-Weg
    # noch einen 429 liefert, wird gewartet/gepausiert.
    if ($fehler -and (team_result_is_429 $Out)) {
        $versuch = 1
        $pausieren = $true
        $resetHhmm = ''
        while ($versuch -le $TEAM_429_MAX_RETRIES) {
            $resetEpoch = team_429_reset_epoch $Out
            if (-not $resetEpoch) {
                Team-Fehler "[$Rolle] 429 erkannt, Reset-Zeit unbekannt — kein Warten, Pausen-Signal."
                break
            }
            $jetzt = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
            $warten = [int]($resetEpoch - $jetzt + $TEAM_429_PUFFER)
            $resetHhmm = [DateTimeOffset]::FromUnixTimeSeconds([long]$resetEpoch).LocalDateTime.ToString('HH:mm')
            if ($TEAM_429_MAX_WARTEN -le 0 -or $warten -gt $TEAM_429_MAX_WARTEN) {
                Team-Fehler "[$Rolle] 429 erkannt, Reset erst in ${warten}s (> TEAM_429_MAX_WARTEN=${TEAM_429_MAX_WARTEN}s) — kein Warten, Pausen-Signal."
                break
            }
            Team-Fehler "[$Rolle] 429/Session-Limit erkannt (Versuch $versuch/$TEAM_429_MAX_RETRIES) — warte ${warten}s bis Reset (${resetHhmm}) + Puffer."
            team_429_sleep $warten | Out-Null

            $Out = ($Out -replace '\.json$', '') + "-429-retry$versuch.json"
            $t0 = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
            $cliExit = Team-ClaudeSchreiben $claude $Prompt $Modell $Out $Weitere
            team_versuch_melden $Rolle $Out $t0 | Out-Null
            $versuchLogs += $Out
            $fehler = -not (team_bewerte_ergebnis $Rolle $Out $cliExit)

            if (-not $fehler) {
                Team-Fehler "[$Rolle] Retry nach 429 erfolgreich. Log: $Out"
                $pausieren = $false
                break
            }
            if (-not (team_result_is_429 $Out)) {
                Team-Fehler "[$Rolle] Retry lieferte einen normalen (nicht-429) Fehler — weiter im normalen Fehlerpfad."
                $pausieren = $false
                break
            }
            $versuch++
        }

        if ($fehler -and $pausieren) {
            $script:TEAM_LAST_PAUSE = 1
            $script:TEAM_LAST_RESET = if ($resetHhmm) { $resetHhmm } else { 'unbekannt' }
            $script:TEAM_LAST_COST = team_summe_cost_usd $versuchLogs
            $script:TEAM_LAST_OUT = $Out
            Team-Fehler "[$Rolle] 429/Session-Limit — Retries erschöpft oder Reset zu weit entfernt. Pausen-Signal (Reset: $($script:TEAM_LAST_RESET))."
            return 42
        }
    }

    $script:TEAM_LAST_COST = team_summe_cost_usd $versuchLogs
    $script:TEAM_LAST_OUT = $Out
    if ($fehler) {
        Team-Fehler "[$Rolle] Claude-Aufruf endgültig fehlgeschlagen, Log: $Out"
        return 1
    }
    return 0
}

$script:TEAM_AUTH_USER = if ($env:AUTH_MODE) { $env:AUTH_MODE } else { '' }
$script:TEAM_LAST_COST = ''
$script:TEAM_LAST_OUT = ''
$script:TEAM_LAST_PAUSE = 0
$script:TEAM_LAST_RESET = ''

Export-ModuleMember -Function * -Variable @(
    'SMOKE_ZEILE', 'SMOKE_SUFFIX',
    'TEAM_MODEL_LOOP', 'TEAM_MODEL_STRONG',
    'TEAM_ROLE_BUDGET_USD', 'TEAM_ROLE_HARDCAP_USD',
    'TEAM_429_MAX_RETRIES', 'TEAM_429_MAX_WARTEN', 'TEAM_429_PUFFER',
    'TEAM_GUARD_LAUFZEIT',
    'TEAM_LAST_COST', 'TEAM_LAST_OUT', 'TEAM_LAST_PAUSE', 'TEAM_LAST_RESET',
    'TEAM_PROJEKT', 'TEAM_PRODUKTIVCODE', 'TEAM_TEST_ORDNER', 'TEAM_PLAN_ORDNER',
    'TEAM_WEITERER_CODE', 'TEAM_TEST_ORDNER_BESTAND', 'TEAM_PLAN_ORDNER_BESTAND',
    'TEAM_BEUTEBUCH', 'TEAM_ERMITTLUNGSAKTEN', 'TEAM_ROADMAP', 'TEAM_BACKLOG',
    'TEAM_CHANGELOG', 'TEAM_SMOKE_TEST', 'TEAM_FIX_PRAEFIX', 'TEAM_FEAT_PRAEFIX',
    'TEAM_BEUTEBUCH_TOOL', 'TEAM_KOSTEN_TOOL', 'TEAM_DOMAENEN', 'TEAM_LEDGER',
    'TEAM_REDTEAM_AUFTRAG_HARRY', 'TEAM_REDTEAM_AUFTRAG_MARV',
    'TEAM_WHITELIST_REDTEAM', 'TEAM_WHITELIST_AXEL'
)

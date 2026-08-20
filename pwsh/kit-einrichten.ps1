# Bahn: pwsh | Gegenstueck: kit-einrichten.sh
<#
  kit-einrichten.ps1 — die Vorflug-Pruefung zwischen `git clone` und
  `install.ps1`, fuer die pwsh-Bahn.

  Gegenstueck zu kit-einrichten.sh. Fuenf Abschnitte, dieselbe Reihenfolge,
  dieselbe Haltung: PROBEN STATT VORAUSSETZEN. Die Heuristik erklaert den
  Regelfall, die Probe entscheidet den Einzelfall.

  DREI DINGE SIND HIER ANDERS ALS IN DER BASH-FASSUNG — und keines davon ist
  eine Pfadanpassung:

  1. KEIN flock. Unter Windows gibt es das nicht. An seine Stelle tritt eine
     ZWEI-PROZESS-PROBE auf [System.IO.FileStream] mit FileShare::None. Das
     ist strenger als die Bash-Bahn prueft: Dort wird `flock -n` einmal im
     eigenen Prozess versucht, was eine kooperative Sperre kaum belasten kann.

  2. STATT /mnt/c: Netzlaufwerke und Synchronisationsordner. Der teuerste
     stille Fehler unter WSL war ein Klon im Windows-Dateisystem. Nativ ist
     das Gegenstueck ein Klon auf einem gemappten Netzlaufwerk oder unter
     OneDrive — dort ist die Dateisperre nicht zugesichert, und ein
     Sync-Client schreibt in Dateien, waehrend eine Rolle sie liest. Erkannt
     wird es heuristisch UND geprobt.

  3. KEIN Exec-Bit. Windows kennt es nicht; `chmod +x` gibt es nicht zu
     pruefen. Stattdessen wird die AUSFUEHRUNGSRICHTLINIE geprueft — sie ist
     das, was unter Windows verhindert, dass ein Skript startet.

  Das Skript ruft KEINE Agenten-CLI auf und kostet daher nichts.

  Aufruf:
    pwsh -File .\kit-einrichten.ps1 [<zielpfad>] [-NurPruefen] [-Verknuepfen]
                                    [-Auth] [-NichtInteraktiv]

  DAS ERFOLGSKRITERIUM IST DER EXIT-CODE, NICHT DIE SCHLUSSZEILE.
    pwsh -File .\kit-einrichten.ps1 -NurPruefen; if ($LASTEXITCODE -eq 0) { "BEREIT" }
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$Ziel = "",
    [switch]$NurPruefen,
    [switch]$Verknuepfen,
    [switch]$Auth,
    [switch]$NichtInteraktiv
)

$ErrorActionPreference = 'Continue'
# BL-122: Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
# standardmaessig $true — ein Exit-Code != 0 aus einem NATIVEN Befehl ist damit
# ein TERMINIERENDER Fehler und nicht mehr nur ein Wert in $LASTEXITCODE. Diese
# Bahn ist durchgehend fuer den klassischen Vertrag geschrieben: aufrufen,
# $LASTEXITCODE lesen, entscheiden. Ohne diese Zeile ist jede dieser
# Entscheidungen unerreichbar — der Abbruch kommt vorher.
$PSNativeCommandUseErrorActionPreference = $false

# Seit der Bahn-Trennung: BAHN ist <kit>\pwsh, KIT die Wurzel des Kits.
$BAHN = Split-Path -Parent $PSCommandPath
$KIT  = Split-Path -Parent $BAHN
$Interaktiv = -not $NichtInteraktiv -and -not [Console]::IsInputRedirected

$script:Fehler = 0
$script:Warnungen = 0

function Team-CfgDir {
    # %APPDATA% ist der richtige Ort unter Windows. Der Rueckfall haelt das
    # Skript auf Nicht-Windows lauffaehig und zeigt dort auf DIESELBE Ablage,
    # die die Bash-Bahn benutzt — eine Maschine, eine Auth-Konfiguration.
    # Bewusst in jedem Bootstrap-Skript einzeln: Sie duerfen von pwsh/lib.psm1
    # nicht abhaengen, denn sie laufen, BEVOR es die Bibliothek gibt.
    if ($env:APPDATA) { return (Join-Path $env:APPDATA 'claude-team') }
    return (Join-Path $HOME '.config/claude-team')
}

function Kopf($t) { Write-Host ""; Write-Host $t -ForegroundColor White }
function Ok($t)   { Write-Host "  [ok] $t" -ForegroundColor Green }
function Zeile($t) { Write-Host "       $t" }
function Warnung {
    param([string]$Text, [string[]]$Mehr)
    Write-Host "  [!]  $Text" -ForegroundColor Yellow
    foreach ($z in $Mehr) { Zeile $z }
    $script:Warnungen++
}
function Fehler {
    param([string]$Text, [string[]]$Mehr)
    Write-Host "  [x]  $Text" -ForegroundColor Red
    foreach ($z in $Mehr) { Zeile $z }
    $script:Fehler++
}
function Ja($frage) {
    if (-not $Interaktiv) { return $false }
    $a = Read-Host "  $frage [j/N]"
    return ($a -and $a.ToLower() -in @('j', 'ja', 'y', 'yes'))
}

Write-Host "=== T.E.A.M.-Starterkit — Maschine einrichten (Windows, nativ) ===" -ForegroundColor White
Write-Host "  Kit: $KIT"

# ---------------------------------------------------------------- 1/5 Umgebung
Kopf "1/5 — Umgebung"

if ($IsWindows -eq $false) {
    # Kein Abbruch: Die Pruefung selbst ist nuetzlich (Syntax, Werkzeuge), und
    # ein irrtuemlicher Aufruf unter Linux soll erklaert werden, nicht
    # abgewiesen. Der Bash-Weg ist dort der richtige.
    Warnung "Das hier ist nicht Windows." @(
        "Dieses Skript richtet die pwsh-Bahn ein (Windows ohne WSL).",
        "Unter Linux ist bash kit-einrichten.sh der richtige Weg."
    )
} else {
    try {
        $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
        Ok "$($os.Caption) — Build $($os.BuildNumber), $env:PROCESSOR_ARCHITECTURE"
    } catch {
        Warnung "Betriebssystem nicht ermittelbar" @($_.Exception.Message)
    }
}

$psv = $PSVersionTable.PSVersion
if ($psv.Major -ge 7) {
    Ok "PowerShell $psv"
} else {
    Fehler "PowerShell $psv ist zu alt (gebraucht wird 7 oder neuer)." @(
        "Windows 11 bringt 5.1 mit; 7 wird DANEBEN installiert, nicht darueber.",
        "  winget install --id Microsoft.PowerShell --source winget",
        "Danach mit `pwsh` fahren, nicht mit `powershell`."
    )
}

# Die Ausfuehrungsrichtlinie ist unter Windows das, was ein Skript am Starten
# hindert — das Gegenstueck zum fehlenden Exec-Bit unter Linux. Geprueft wird
# der EFFEKTIVE Wert, nicht der eines einzelnen Bereichs.
$policy = Get-ExecutionPolicy
if ($policy -in @('Restricted', 'AllSigned')) {
    Fehler "Ausfuehrungsrichtlinie ist '$policy' — .ps1-Dateien starten so nicht." @(
        "Fuer den eigenen Benutzer lockern (kein Administrator noetig):",
        "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned",
        "RemoteSigned laesst lokale Skripte zu und verlangt fuer",
        "heruntergeladene eine Signatur. Das Kit klonst du selbst."
    )
} else {
    Ok "Ausfuehrungsrichtlinie: $policy"
}

# ------------------------------------------------------------- 2/5 Werkzeuge
Kopf "2/5 — Werkzeuge"

if (Get-Command git -ErrorAction SilentlyContinue) {
    Ok "git $((git --version) -replace '^git version ')"
} else {
    Fehler "git fehlt." @(
        "Die Rollen committen, rollen zurueck und pruefen Commit-Bereiche.",
        "  winget install --id Git.Git --source winget"
    )
}

# python: Abhaengigkeit der TEAM-Infrastruktur (geteilt/tools/), nicht des
# Projekts. Unter Windows heisst der Interpreter je nach Installation anders —
# gesucht wird in der Reihenfolge, in der er am ehesten der richtige ist.
# REIHENFOLGE NACH PLATTFORM (BL-122): Unter Windows legen python.org und
# winget python.exe und den py-Launcher an, KEIN python3.exe — was dort als
# python3 gefunden wird, ist meist der Store-Platzhalter aus WindowsApps.
# Unter Linux ist es umgekehrt: python fehlt oder zeigt auf Python 2.
$script:PythonBefehl = ""
$script:PythonKandidaten = if ($IsWindows) { @('python', 'python3', 'py') }
                           else            { @('python3', 'python', 'py') }
foreach ($kandidat in $script:PythonKandidaten) {
    $cmd = Get-Command $kandidat -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    # Der Windows-Store legt Platzhalter namens python.exe und python3.exe ab,
    # die nur den Store oeffnen und mit 9009 enden. Ein echter Interpreter
    # beantwortet die Versionsfrage. Das try/catch haelt den Platzhalter davon
    # ab, den Kandidatenlauf zu beenden, statt nur diesen Kandidaten.
    $v = $null
    try { $v = & $kandidat -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>$null }
    catch { continue }
    if ($LASTEXITCODE -ne 0 -or -not $v) { continue }
    $script:PythonBefehl = $kandidat
    $teile = $v.Trim().Split('.')
    if ([int]$teile[0] -gt 3 -or ([int]$teile[0] -eq 3 -and [int]$teile[1] -ge 8)) {
        Ok "$kandidat $($v.Trim())"
    } else {
        Fehler "$kandidat $($v.Trim()) ist zu alt (gebraucht wird 3.8 oder neuer)." @(
            "geteilt/tools/kosten.py und beutebuch.py setzen es voraus."
        )
    }
    break
}
if (-not $script:PythonBefehl) {
    Fehler "Kein brauchbarer Python-Interpreter gefunden ($($script:PythonKandidaten -join ', '))." @(
        "Die Team-Werkzeuge (Kosten, Beutebuch) sind Python — das ist eine",
        "Abhaengigkeit der Infrastruktur, nicht deines Projekts.",
        "  winget install --id Python.Python.3.12 --source winget",
        "Achtung: Der Windows-Store legt Platzhalter ab, die nur den Store",
        "oeffnen. Gegenprobe:  python -c `"print(1)`""
    )
}

# KEIN flock-Check — es gibt das unter Windows nicht. Die Zusicherung, die es
# auf der Bash-Bahn traegt, wird in 3/5 geprobt statt hier abgehakt.

# BL-124: als MODUL suchen, nicht nur als Befehl. Unter Windows legt
# `pip install pytest` die pytest.exe in ein Scripts-Verzeichnis, das oft nicht
# im PATH steht — bei `--user` warnt pip beim Installieren sogar davor. Wer nur
# den Befehl sucht, meldet "fehlt" und empfiehlt danach genau die Installation,
# die es schon gibt. Der Modulaufruf braucht den PATH-Eintrag nicht.
$script:PytestAufruf = $null
foreach ($k in $script:PythonKandidaten) {
    if (-not (Get-Command $k -ErrorAction SilentlyContinue)) { continue }
    try { & $k -m pytest --version 2>$null | Out-Null } catch { continue }
    if ($LASTEXITCODE -eq 0) { $script:PytestAufruf = $k; break }
}
if ($script:PytestAufruf) {
    $pv = (& $script:PytestAufruf -m pytest --version 2>&1 | Select-Object -First 1)
    Ok "$pv (via: $script:PytestAufruf -m pytest)"
} elseif (Get-Command pytest -ErrorAction SilentlyContinue) {
    Ok "pytest $((pytest --version 2>&1 | Select-Object -First 1))"
} else {
    Warnung "pytest fehlt." @(
        ".\team-test.cmd im Zielprojekt und die Kit-Selbstpruefung brauchen es;",
        "die Rollen selbst nicht.",
        "  $(if ($script:PythonBefehl) { $script:PythonBefehl } else { 'python' }) -m pip install pytest"
    )
}

# Agenten-CLI: BEISPIEL. Das Kit spricht zwei Modellstufen an, keine Namen.
$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($claude) {
    $ver = @(& claude --version 2>&1)
    Ok "Agenten-CLI (Beispiel Claude Code): $($ver[0])"
    if ($claude.Source -match '\.(cmd|bat)$') {
        Zeile "Aufgeloest als Shim: $($claude.Source)"
    }
} else {
    Warnung "Keine 'claude'-CLI im PATH." @(
        "Das ist kein Fehler: Das Kit ist modell- und werkzeugagnostisch.",
        "Erprobt ist heute genau ein Weg — Claude Code. Wer ihn nimmt:",
        "  npm install -g @anthropic-ai/claude-code",
        "Danach eine NEUE Sitzung oeffnen: PATH-Aenderungen erreichen",
        "laufende Shells nicht."
    )
}

# --------------------------------------------------------- 3/5 Lage des Klons
Kopf "3/5 — Lage des Klons"

# a) Zeilenenden. Fuer die pwsh-Bahn zaehlen .cmd (muessen CRLF sein) und
#    .ps1 (LF ist richtig und schadet nicht). Geprueft wird der Fall, der
#    wirklich weh tut: ein .cmd mit reinem LF verhaelt sich sporadisch falsch.
$cmdLf = @()
foreach ($f in (Get-ChildItem -Path $KIT -Filter *.cmd -Recurse -File -ErrorAction SilentlyContinue)) {
    $roh = [System.IO.File]::ReadAllBytes($f.FullName)
    $hatLf = $false
    for ($i = 0; $i -lt $roh.Length; $i++) {
        if ($roh[$i] -eq 10 -and ($i -eq 0 -or $roh[$i - 1] -ne 13)) { $hatLf = $true; break }
    }
    if ($hatLf) { $cmdLf += $f.Name }
}
if ($cmdLf.Count) {
    Fehler "Batch-Dateien mit reinem LF: $($cmdLf -join ', ')" @(
        "Der Kommandozeileninterpreter liest .cmd waehrend der Ausfuehrung;",
        "bei LF verhalten sich Labels und goto unzuverlaessig — sporadisch,",
        "also besonders schwer zuzuordnen.",
        "Das Kit erzwingt CRLF ueber .gitattributes. Ein Klon von VOR dieser",
        "Regel traegt den Fehler weiter:  git -C `"$KIT`" rm --cached -r . ; git -C `"$KIT`" reset --hard"
    )
} else {
    Ok "Zeilenenden der Batch-Dateien in Ordnung"
}

# b) Dateisystem. Das Windows-Gegenstueck zum /mnt/c-Fehler unter WSL.
$wurzel = [System.IO.Path]::GetPathRoot($KIT)
$verdacht = @()
if ($KIT -match '^\\\\') { $verdacht += "UNC-Pfad (Netzfreigabe)" }
try {
    $laufwerk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($wurzel.TrimEnd('\'))'" -ErrorAction Stop
    if ($laufwerk.DriveType -eq 4) { $verdacht += "gemapptes Netzlaufwerk" }
} catch { }
foreach ($muster in @('OneDrive', 'Dropbox', 'Google Drive', 'iCloud')) {
    if ($KIT -like "*$muster*") { $verdacht += "Synchronisationsordner ($muster)" }
}
if ($verdacht.Count) {
    Warnung "Das Kit liegt auf: $($verdacht -join ', ')" @(
        "Dort ist die Dateisperre nicht zugesichert, und ein Sync-Client",
        "schreibt in Dateien, waehrend eine Rolle sie liest. Richtig ist ein",
        "lokales Laufwerk, z. B. C:\Source\...",
        "Kein Abbruch — die Probe unten entscheidet den Einzelfall."
    )
} else {
    Ok "Kit liegt auf einem lokalen Laufwerk"
}

# c) Und haelt eine Dateisperre? Danach haengt die Serialisierung von Ledger
#    und Kaskadenstand. Zwei Prozesse, nicht einer: Eine Sperre, die nur der
#    eigene Prozess je anfasst, hat nichts bewiesen.
$probe = Join-Path $KIT ".einrichten-probe-$([guid]::NewGuid()).tmp"
try {
    $strom = [System.IO.File]::Open($probe, [System.IO.FileMode]::CreateNew,
             [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    $gegenprobe = @"
try {
  `$s = [System.IO.File]::Open('$probe', [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
  `$s.Close(); exit 0
} catch { exit 42 }
"@
    $zweiter = Start-Process -FilePath (Get-Process -Id $PID).Path `
        -ArgumentList @("-NoProfile", "-NonInteractive", "-Command", $gegenprobe) `
        -Wait -PassThru -NoNewWindow
    if ($zweiter.ExitCode -eq 42) {
        Ok "Dateisperren funktionieren hier (Zwei-Prozess-Gegenprobe bestanden)"
    } elseif ($zweiter.ExitCode -eq 0) {
        Fehler "Der zweite Prozess bekam die gesperrte Datei." @(
            "Ohne Sperre koennen zwei Rollen gleichzeitig auf Ledger und",
            "Kaskadenstand schreiben. Typische Ursache: Netzlaufwerk oder",
            "Synchronisationsordner — siehe die Meldung darueber."
        )
    } else {
        Warnung "Sperrprobe unklar (Exit $($zweiter.ExitCode))" @(
            "Weder bestaetigt noch widerlegt — von Hand nachsehen."
        )
    }
    $strom.Close()
} catch {
    Fehler "Sperrprobe nicht durchfuehrbar" @($_.Exception.Message)
} finally {
    Remove-Item -Force $probe -ErrorAction SilentlyContinue
}

# d) Und dasselbe fuer das Zielprojekt, falls eines genannt wurde.
if ($Ziel) {
    $zielAbs = $null
    try { $zielAbs = (Resolve-Path $Ziel -ErrorAction Stop).Path } catch { }
    if ($zielAbs) {
        $Ziel = $zielAbs
        & git -C $Ziel rev-parse --is-inside-work-tree 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Ok "Zielprojekt ist ein Git-Repository: $Ziel"
        } else {
            Fehler "Zielprojekt ist kein Git-Repository: $Ziel" @("Zuerst:  git -C `"$Ziel`" init")
        }
    } else {
        Fehler "Zielpfad existiert nicht: $Ziel"
        $Ziel = ""
    }
}

# ------------------------------------------------------------------ 4/5 Auth
Kopf "4/5 — Auth des Agenten-Werkzeugs (Beispiel Claude Code)"

$cfgDir = Team-CfgDir
$authSetup = Join-Path $KIT 'pwsh\scripts\team-auth-setup.ps1'
if ((Test-Path (Join-Path $cfgDir 'auth-mode')) -or (Test-Path (Join-Path $cfgDir 'api-key'))) {
    Ok "Auth-Konfiguration vorhanden: $cfgDir"
} elseif ($NurPruefen) {
    Warnung "Keine Auth-Konfiguration unter $cfgDir." @("Nachholen:  pwsh -File `"$authSetup`"")
} elseif ($Auth -or (Ja "Auth jetzt einrichten (Abo als Prio 1, API-Key nur als Fallback)?")) {
    & $authSetup
    if ($LASTEXITCODE -ne 0) { Warnung "Auth-Einrichtung abgebrochen — nachholbar, siehe oben." }
} else {
    Warnung "Keine Auth-Konfiguration unter $cfgDir." @(
        "Ohne sie laeuft keine Rolle. Nachholen:",
        "  pwsh -File `"$authSetup`"",
        "Merke: Der API-Key gehoert NIE in die Benutzer-Umgebungsvariablen —",
        "er hat Vorrang vor dem Abo-Login und schaltet die Abrechnung still um."
    )
}

# ----------------------------------------------------------- 5/5 Verknuepfung
Kopf "5/5 — Kurzbefehl von ueberall (optional)"

function Verknuepfe {
    <#
      Kein Symlink: Der braucht unter Windows Administratorrechte oder den
      Entwicklermodus, und ein Einrichtungsskript, das an Rechten scheitert,
      hat sein Versprechen gebrochen. Ein .cmd-Aufrufer erreicht dasselbe —
      er zeigt auf die Datei IM KIT, es entsteht also keine zweite Kopie, die
      auseinanderlaufen koennte. Genau das war der Sinn des Symlinks.
    #>
    param([string]$Quelle, [string]$Zielname)
    $ordner = Join-Path $env:USERPROFILE '.claude\scripts'
    New-Item -ItemType Directory -Force -Path $ordner | Out-Null
    $ziel = Join-Path $ordner $Zielname
    # BL-123: Auch dieser Aufrufer loest pwsh auf, statt es vorauszusetzen. Er
    # liegt AUSSERHALB des Kits und wird von ueberall gestartet — also aus
    # cmd-Sitzungen, deren PATH niemand kennt. Ein blankes `pwsh` meldete dort
    # nur "is not recognized" und sah aus, als sei das Kit kaputt.
    $zeilen = @(
        '@echo off'
        'setlocal'
        'set "TEAM_PWSH="'
        'for %%P in (pwsh.exe) do if not defined TEAM_PWSH set "TEAM_PWSH=%%~$PATH:P"'
        'if not defined TEAM_PWSH if exist "%ProgramFiles%\PowerShell\7\pwsh.exe" set "TEAM_PWSH=%ProgramFiles%\PowerShell\7\pwsh.exe"'
        'if not defined TEAM_PWSH if exist "%ProgramW6432%\PowerShell\7\pwsh.exe" set "TEAM_PWSH=%ProgramW6432%\PowerShell\7\pwsh.exe"'
        'if not defined TEAM_PWSH if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe" set "TEAM_PWSH=%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe"'
        'if not defined TEAM_PWSH goto :keinpwsh'
        ('"%TEAM_PWSH%" -NoProfile -File "' + $Quelle + '" %*')
        'exit /b %ERRORLEVEL%'
        ''
        ':keinpwsh'
        'echo FEHLER: PowerShell 7 ^(pwsh^) ist nicht auffindbar.'
        'echo   Windows PowerShell 5.1 genuegt NICHT. Das Kit braucht pwsh 7:'
        'echo     winget install --id Microsoft.PowerShell --source winget'
        'echo   Danach eine NEUE Sitzung oeffnen - PATH erreicht laufende Shells nicht.'
        'exit /b 127'
    )
    $inhalt = ($zeilen -join "`r`n") + "`r`n"
    if (Test-Path $ziel) {
        $alt = Get-Content -Raw $ziel
        if ($alt -eq $inhalt) { Ok "Verknuepft: $ziel"; return }
        # BL-123, dieselbe Lehre wie A.12.1: Ein veralteter Aufrufer meldet sich
        # nicht, er behauptet eines Tages, das Kit sei nicht da. Genau so ist der
        # Umzug auf bash/ aufgefallen. Erkennbar an der Quelle, auf die er zeigt:
        # Wer auf DIESE Kit-Datei zeigt, ist unsere eigene alte Fassung und wird
        # nachgezogen — mit Sicherung daneben. Alles andere bleibt unberuehrt,
        # denn ein fremdes Skript unter fremdem Namen gehoert uns nicht.
        if ($alt -like "*$Quelle*") {
            $sicherung = "$ziel.bak"
            Set-Content -Path $sicherung -Value $alt -NoNewline -Encoding ascii
            Set-Content -Path $ziel -Value $inhalt -NoNewline -Encoding ascii
            Ok "Verknuepft: $ziel (veraltete Fassung nachgezogen, Sicherung: $sicherung)"
            return
        }
        Warnung "$ziel zeigt woandershin — nicht angefasst." @(
            "Sie laeuft dem Kit hinterher, sobald sich hier etwas aendert.",
            "Ersetzen: Datei loeschen und dieses Skript erneut fahren."
        )
        return
    }
    Set-Content -Path $ziel -Value $inhalt -NoNewline -Encoding ascii
    Ok "Verknuepft: $ziel -> $Quelle"
}

if ($NurPruefen) {
    Zeile "(uebersprungen wegen -NurPruefen)"
} elseif ($Verknuepfen -or (Ja "team-init.ps1 und team-auth-setup.ps1 nach ~\.claude\scripts\ verknuepfen?")) {
    Verknuepfe (Join-Path $KIT 'pwsh\scripts\team-init.ps1')       'team-init.cmd'
    Verknuepfe (Join-Path $KIT 'pwsh\scripts\team-auth-setup.ps1') 'team-auth-setup.cmd'
    Zeile "Danach von ueberall:  %USERPROFILE%\.claude\scripts\team-init.cmd <zielpfad>"
} else {
    Zeile "Uebersprungen. Der lange Weg tut es genauso:"
    Zeile "    pwsh -File `"$KIT\pwsh\install.ps1`" <zielpfad>"
}

# --------------------------------------------------------------- Abschluss
Kopf "Ergebnis"

if ($script:Fehler -gt 0) {
    Write-Host "  $($script:Fehler) Fehler, $($script:Warnungen) Warnungen — die Maschine ist noch nicht bereit." -ForegroundColor Red
    Zeile "Erst die Fehler oben abarbeiten, dann dieses Skript erneut fahren."
    Zeile "Die ausfuehrliche Fassung mit Begruendungen: doku\einrichtung.md"
    exit 1
}
if ($script:Warnungen -gt 0) {
    Write-Host "  0 Fehler, $($script:Warnungen) Warnungen — lauffaehig, aber lies sie." -ForegroundColor Yellow
} else {
    Write-Host "  Alles gruen." -ForegroundColor Green
}

if ($Ziel -and -not $NurPruefen) {
    Kopf "Weiter: Einbinden in $Ziel"
    $installer = Join-Path $KIT 'pwsh\install.ps1'
    if (-not $Interaktiv) {
        Zeile "(nicht-interaktiv — Werte aus TEAM_INIT_* bzw. Defaults)"
        & $installer $Ziel -NichtInteraktiv
        exit $LASTEXITCODE
    }
    if (Ja "install.ps1 jetzt starten?") {
        & $installer $Ziel
        exit $LASTEXITCODE
    }
    Zeile "Spaeter:  pwsh -File `"$installer`" `"$Ziel`""
} else {
    Kopf "Weiter"
    Zeile "Einbinden in ein Projekt:  pwsh -File `"$KIT\pwsh\install.ps1`" <zielpfad>"
    Zeile "Die ganze Routine:         doku\einrichtung.md"
}
exit 0

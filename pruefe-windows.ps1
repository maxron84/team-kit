# Bahn: pwsh | Gegenstueck: keines (eigenstaendige Vorflug-Probe, laeuft allein auf der Zielmaschine)
<#
  pruefe-windows.ps1 — Vorflug-Probe fuer den nativen Windows-Zweig.

  WAS DAS HIER IST
    Eigenstaendige Probe, die BEANTWORTET, was der Bauplan
    plans/windows-nativ.md nur ANNIMMT. Sie haengt an keiner Kit-Datei und
    laesst sich einzeln auf die Zielmaschine kopieren — genau dafuer ist sie
    gebaut. Sie installiert nichts, aendert nichts und schreibt nur in ein
    temporaeres Verzeichnis, das sie danach wieder raeumt.

  DIE DREI FRAGEN (R1-R3 aus plans/windows-nativ.md)
    R1  Laeuft `claude -p --output-format json` unter nativem Windows
        HEADLESS mit dem Abo? Das ist die tragende Annahme: Faellt sie, sind
        die Stufen 3-5 des Bauplans wirkungslos, und es ist eine Auth-Frage
        statt einer Plattformfrage.
    R2  Findet und startet PowerShell die Agenten-CLI? Sie ist unter Windows
        selbst ein `.cmd`-Shim, kein Programm. Fehlt die Aufloesung ueber
        PATHEXT, sieht das Ergebnis AUS WIE EIN AUTH-FEHLER und ist keiner —
        das ist der teuerste Fehlschluss dieser Probe, deshalb steht er
        VOR R1.
    R3  Sperrt [System.IO.FileStream] mit FileShare::None ueber
        Prozessgrenzen? Das ist der Ersatz fuer `flock`, das es unter Windows
        nicht gibt.

  KOSTEN
    Der Standardlauf ruft KEINE kostenpflichtige Arbeit auf. R1 wird dabei
    nur so weit beantwortet, wie es ohne Abrechnung geht (CLI vorhanden,
    Anmeldelage, verdraengender API-Key). Die abschliessende Antwort auf R1
    braucht einen echten Aufruf; der kostet Bruchteile eines Cent und ist
    deshalb ein eigener Schalter:

        pwsh -File .\pruefe-windows.ps1 -MitEchtemAufruf

  DAS ERFOLGSKRITERIUM IST DER EXIT-CODE, NICHT DIE SCHLUSSZEILE
    0 = keine Fehler (Warnungen moeglich), 1 = mindestens ein Fehler.
    Pruefbare Form:   pwsh -File .\pruefe-windows.ps1; if ($LASTEXITCODE -eq 0) { "BEREIT" }
#>
[CmdletBinding()]
param(
    [switch]$MitEchtemAufruf,
    [switch]$Hilfe
)

if ($Hilfe) {
    Get-Content -Path $PSCommandPath -TotalCount 40 |
        ForEach-Object { $_ -replace '^\s*<#|^\s*#>', '' }
    exit 0
}

$ErrorActionPreference = 'Continue'

$script:Fehler = 0
$script:Warnungen = 0

function Kopf($text) { Write-Host ""; Write-Host $text -ForegroundColor White }
function Ok($text) { Write-Host "  [ok]  $text" -ForegroundColor Green }
function Warnung {
    param([string]$text, [string[]]$zeilen)
    Write-Host "  [!]   $text" -ForegroundColor Yellow
    foreach ($z in $zeilen) { Write-Host "        $z" }
    $script:Warnungen++
}
function Fehler {
    param([string]$text, [string[]]$zeilen)
    Write-Host "  [x]   $text" -ForegroundColor Red
    foreach ($z in $zeilen) { Write-Host "        $z" }
    $script:Fehler++
}
function Info($text) { Write-Host "        $text" -ForegroundColor DarkGray }

Write-Host "=== T.E.A.M. — Probe fuer den nativen Windows-Zweig ===" -ForegroundColor White

# ---------------------------------------------------------------- 1/5 Umgebung
Kopf "1/5 — Umgebung"

$psv = $PSVersionTable.PSVersion
if ($psv.Major -ge 7) {
    Ok "PowerShell $psv"
} else {
    # Kein Abbruch: Die Probe selbst laeuft auch unter 5.1, und ihr Befund ist
    # dann besonders interessant — er sagt, was die Maschine OHNE Nachruesten
    # kann. Der Bauplan setzt pwsh 7 voraus.
    Fehler "PowerShell $psv — der Windows-Zweig setzt pwsh 7 voraus." @(
        "Windows 11 bringt 5.1 mit; 7 wird daneben installiert, nicht darueber.",
        "  winget install --id Microsoft.PowerShell --source winget",
        "Danach diese Probe mit `pwsh` erneut fahren, nicht mit `powershell`."
    )
}

try {
    $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    Ok "$($os.Caption) — Build $($os.BuildNumber), $($env:PROCESSOR_ARCHITECTURE)"
} catch {
    Warnung "Betriebssystem nicht ermittelbar" @($_.Exception.Message)
}

# Nur Information: Ob WSL da ist, aendert am nativen Zweig nichts. Es steht
# hier, damit der Bericht die Maschine vollstaendig beschreibt.
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($wsl) { Info "wsl.exe vorhanden (fuer den nativen Zweig ohne Belang)" }
else { Info "kein wsl.exe — der native Zweig braucht auch keines" }

# ------------------------------------------------------------- 2/5 Bordmittel
Kopf "2/5 — Bordmittel"

function Pruefe-Werkzeug {
    param([string]$Name, [string[]]$Kandidaten, [string]$Versionsschalter,
          [switch]$Pflicht)
    foreach ($k in $Kandidaten) {
        $cmd = Get-Command $k -ErrorAction SilentlyContinue
        if ($cmd) {
            $version = ""
            try { $version = (& $k $Versionsschalter 2>&1 | Select-Object -First 1) } catch { }
            Ok "$Name — $k $version"
            return $cmd
        }
    }
    if ($Pflicht) {
        Fehler "$Name fehlt (gesucht: $($Kandidaten -join ', '))" @(
            "Ohne dieses Werkzeug laeuft die Mechanik nicht."
        )
    } else {
        Warnung "$Name fehlt (gesucht: $($Kandidaten -join ', '))"
    }
    return $null
}

Pruefe-Werkzeug -Name "git" -Kandidaten @("git") -Versionsschalter "--version" -Pflicht | Out-Null
$python = Pruefe-Werkzeug -Name "Python" -Kandidaten @("python3", "python", "py") `
                          -Versionsschalter "--version" -Pflicht

# --------------------------------------------------- 3/5 R2: die Agenten-CLI
Kopf "3/5 — R2: findet und startet PowerShell die Agenten-CLI?"

$claude = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claude) {
    Fehler "`claude` ist ueber PATH nicht auffindbar." @(
        "Ohne die CLI sind R1 und die Stufen 3-5 des Bauplans nicht pruefbar.",
        "Installation: siehe Anthropic-Doku; danach eine NEUE Shell oeffnen",
        "(PATH-Aenderungen erreichen laufende Sitzungen nicht)."
    )
} else {
    Ok "gefunden als $($claude.CommandType): $($claude.Source)"

    # Der eigentliche Punkt von R2. Ein `.cmd` ist kein Programm, sondern wird
    # vom Kommandozeileninterpreter gelesen. Der Aufrufoperator `&` kommt
    # damit zurecht, `System.Diagnostics.Process` ohne UseShellExecute NICHT —
    # und genau dieser Unterschied traegt spaeter team_claude.
    if ($claude.Source -match '\.(cmd|bat)$') {
        Info "Shim erkannt (.cmd) — genau der Fall, den der Bauplan als R2 fuehrt"
    }
    try {
        # Erst vollstaendig einsammeln, DANN $LASTEXITCODE lesen. Ein
        # `… | Select-Object -First 1` beendet die Pipeline vorzeitig, und
        # $LASTEXITCODE ist dann noch nicht gesetzt — der Aufruf war
        # erfolgreich und wird als Fehler gemeldet. Beim ersten Lauf dieser
        # Probe genau so passiert (claude 2.1.206 lief, Meldung war rot).
        $ver = @(& claude --version 2>&1)
        $rc = $LASTEXITCODE
        $verZeile = if ($ver.Count) { $ver[0] } else { "(keine Ausgabe)" }
        if ($rc -eq 0) {
            Ok "Aufruf ueber `&` funktioniert — $verZeile"
        } else {
            Fehler "`claude --version` endete mit Exit $rc" @("$verZeile")
        }
    } catch {
        Fehler "Aufruf ueber `&` scheiterte" @(
            $_.Exception.Message,
            "Das ist R2 und NICHT ein Auth-Fehler — nicht verwechseln."
        )
    }
}

# ------------------------------------------------------------ 4/5 R3: Sperre
Kopf "4/5 — R3: sperrt FileStream ueber Prozessgrenzen?"

# Proben statt glauben (dieselbe Haltung wie A.5 und kit-einrichten.sh): Die
# Erwartung ist gut — FileShare::None ist vom Betriebssystem durchgesetzt und
# nicht kooperativ wie flock —, aber entschieden wird der Einzelfall an der
# Maschine, nicht an der Erwartung.
$sperrOrdner = Join-Path ([System.IO.Path]::GetTempPath()) ("team-probe-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $sperrOrdner -Force | Out-Null
$sperrDatei = Join-Path $sperrOrdner ".team-loop.lock"
try {
    $strom = [System.IO.File]::Open(
        $sperrDatei, [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Ok "Sperre genommen: $sperrDatei"

    # Zweiter Prozess, dieselbe Datei. Er MUSS scheitern — genau das ist die
    # Zusicherung, auf der "eine Pipeline zur Zeit" ruht.
    $gegenprobe = @"
try {
  `$s = [System.IO.File]::Open('$sperrDatei',
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None)
  `$s.Close(); exit 0
} catch { exit 42 }
"@
    $zweiter = Start-Process -FilePath (Get-Process -Id $PID).Path `
        -ArgumentList @("-NoProfile", "-NonInteractive", "-Command", $gegenprobe) `
        -Wait -PassThru -NoNewWindow
    if ($zweiter.ExitCode -eq 42) {
        Ok "Zwei-Prozess-Gegenprobe bestanden — der zweite Prozess wurde abgewiesen"
    } elseif ($zweiter.ExitCode -eq 0) {
        Fehler "Der zweite Prozess bekam die Datei TROTZ gehaltener Sperre." @(
            "Damit gibt es unter Windows keine belastbare Sperre, und die",
            "Vollautomatik duerfte dort nur einzeln laufen (R3 im Bauplan).",
            "Dateisystem pruefen: Netzlaufwerk oder Sync-Ordner (OneDrive)?"
        )
    } else {
        Warnung "Gegenprobe unklar (Exit $($zweiter.ExitCode))" @(
            "Weder Sperre bestaetigt noch widerlegt — von Hand nachsehen."
        )
    }
    $strom.Close()
} catch {
    Fehler "Sperre liess sich nicht nehmen" @($_.Exception.Message)
} finally {
    Remove-Item -Recurse -Force $sperrOrdner -ErrorAction SilentlyContinue
}

# -------------------------------------------------------------- 5/5 R1: Auth
Kopf "5/5 — R1: laeuft die CLI headless mit dem Abo?"

# Der verdraengende API-Key ist der haeufigste stille Auth-Fehler: Er ist
# gesetzt, die CLI nimmt ihn, und die Rechnung landet auf der API statt im
# Abo. Unter Windows kommt er aus der Benutzerumgebung oder aus WSLENV.
if ($env:ANTHROPIC_API_KEY) {
    Warnung "ANTHROPIC_API_KEY ist gesetzt — er VERDRAENGT das Abo." @(
        "Laenge: $($env:ANTHROPIC_API_KEY.Length) Zeichen (Wert wird nicht ausgegeben).",
        "Fuer eine Abo-Probe in dieser Sitzung leeren:",
        "  `$env:ANTHROPIC_API_KEY = `$null",
        "Dauerhaft gehoert er nicht in die Umgebung, sondern in die geschuetzte",
        "Ablage des Kits (Stufe 2: %APPDATA%\\claude-team\\api-key mit ACL)."
    )
} else {
    Ok "kein ANTHROPIC_API_KEY in der Umgebung — das Abo kann greifen"
}

# $env:USERPROFILE existiert nur unter Windows. Der Rueckfall auf $HOME ist
# nicht Kosmetik: Ohne ihn stirbt die Probe an dieser Zeile, statt ihren
# Bericht zu Ende zu schreiben — und ein Bericht, der abbricht, beantwortet
# gar nichts.
$profilPfad = if ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }
$anmeldung = if ($profilPfad) { Join-Path $profilPfad ".claude" } else { $null }
if ($anmeldung -and (Test-Path $anmeldung)) {
    Ok "Anmeldeablage vorhanden: $anmeldung"
} else {
    Warnung "keine Anmeldeablage unter '$anmeldung' gefunden" @(
        "Moeglicherweise noch nie interaktiv angemeldet. Einmal `claude` ohne",
        "Argumente starten und die Anmeldung durchlaufen, DANN diese Probe",
        "mit -MitEchtemAufruf wiederholen."
    )
}

if (-not $claude) {
    Warnung "R1 nicht pruefbar — die CLI fehlt (siehe 3/5)"
} elseif (-not $MitEchtemAufruf) {
    Info "R1 bleibt hier UNBEANTWORTET — der Standardlauf kostet nichts."
    Info "Die abschliessende Antwort braucht einen echten Aufruf:"
    Info "  pwsh -File .\pruefe-windows.ps1 -MitEchtemAufruf"
    Warnung "R1 unbeantwortet (bewusst)" @(
        "Solange R1 offen ist, stehen die Stufen 3-5 des Bauplans auf einer",
        "Annahme. Das ist der einzige Punkt, der den Plan kippen kann."
    )
} else {
    Info "echter Aufruf — kostet Bruchteile eines Cent"
    $ausgabeDatei = Join-Path ([System.IO.Path]::GetTempPath()) ("team-r1-" + [guid]::NewGuid() + ".json")
    try {
        & claude -p "Antworte mit genau einem Wort: bereit" `
                 --output-format json 2>&1 | Set-Content -Path $ausgabeDatei -Encoding utf8
        $rc = $LASTEXITCODE
        $roh = Get-Content -Raw -Path $ausgabeDatei -ErrorAction SilentlyContinue

        $daten = $null
        try { $daten = $roh | ConvertFrom-Json } catch { }

        if ($null -eq $daten) {
            Fehler "Die Ausgabe ist kein lesbares JSON (Exit $rc)." @(
                "Genau darauf ruht team_result_is_error und der ganze",
                "Bewertungszweig des Kits.",
                "Erste 200 Zeichen:",
                ($roh -replace '\s+', ' ').Substring(0, [Math]::Min(200, $roh.Length))
            )
        } else {
            Ok "JSON gelesen — ConvertFrom-Json ersetzt die python3-Einbettungen"
            if ($daten.PSObject.Properties.Name -contains 'is_error' -and $daten.is_error) {
                Fehler "Die CLI meldet is_error=true (Exit $rc)." @(
                    "R1 ist damit NICHT bestaetigt. Text der Antwort:",
                    "$($daten.result)"
                )
            } else {
                Ok "headless-Aufruf durchgelaufen (Exit $rc)"
                # Die entscheidende Unterscheidung: Abo oder API? Ein Lauf ueber
                # das Abo weist keine Kosten aus; die API tut es.
                $kosten = $daten.total_cost_usd
                if ($null -ne $kosten -and $kosten -gt 0) {
                    Warnung "Der Lauf weist Kosten aus ($kosten USD) — das spricht fuer API, nicht Abo." @(
                        "R1 im engeren Sinn (headless MIT ABO) ist damit offen.",
                        "Steht oben ein gesetzter ANTHROPIC_API_KEY, ist das die Ursache."
                    )
                } else {
                    Ok "keine Kosten ausgewiesen — konsistent mit Abo-Betrieb. R1 bestaetigt."
                }
            }
        }
    } catch {
        Fehler "Der Aufruf scheiterte" @($_.Exception.Message)
    } finally {
        Remove-Item -Force $ausgabeDatei -ErrorAction SilentlyContinue
    }
}

# ------------------------------------------------------------------- Ergebnis
Kopf "Ergebnis"

if ($script:Fehler -gt 0) {
    Write-Host "  $($script:Fehler) Fehler, $($script:Warnungen) Warnungen — die Maschine ist noch nicht bereit." -ForegroundColor Red
    Write-Host "  Das Erfolgskriterium ist der Exit-Code, nicht diese Zeile."
    exit 1
}
if ($script:Warnungen -gt 0) {
    Write-Host "  0 Fehler, $($script:Warnungen) Warnungen — lauffaehig, aber lies sie." -ForegroundColor Yellow
} else {
    Write-Host "  Alles gruen." -ForegroundColor Green
}
Write-Host "  Berichte diesen Lauf vollstaendig zurueck — er beantwortet R1-R3"
Write-Host "  aus plans/windows-nativ.md und entscheidet ueber die Stufen 2-5."
exit 0

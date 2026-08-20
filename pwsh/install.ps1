# Bahn: pwsh | Gegenstueck: install.sh
<#
  install.ps1 — installiert das T.E.A.M. in ein Zielprojekt (Windows, nativ).

  Aufruf:  pwsh -File install.ps1 <zielpfad> [-NichtInteraktiv] [-Force|-Update]

    -NichtInteraktiv  Keine Rueckfragen; Werte aus den TEAM_INIT_*-Umgebungs-
                      variablen oder den Defaults. Fuer Skripte und Tests.
    -Update           Nur die Team-INFRASTRUKTUR aktualisieren. Ruehrt KEINE
                      Projektdaten an. Der richtige Weg, um ein bestehendes
                      Projekt auf eine neue Kit-Version zu heben.
    -Force            Vorhandene Dateien ueberschreiben (Standard: ueberspringen).

    ACHTUNG  -Force ist NUR fuer eine kaputte Erstinstallation gedacht, NIE fuer
             ein gelebtes Projekt: Es ueberschreibt auch .budget-ledger
             (Kostenhistorie weg), .ralph-state (Kaskadenstand zurueck auf 1),
             das Beutebuch (alle Funde weg), CHANGELOG.md, plans\*.md und die
             Konfiguration (Smoke-Test weg). Empirisch nachgestellt, BL-8.
             Fuer Updates: -Update.

  Umgebungsvariablen fuer den nicht-interaktiven Betrieb:
    TEAM_INIT_PROJEKT TEAM_INIT_PRODUKTIVCODE TEAM_INIT_TEST_ORDNER
    TEAM_INIT_PLAN_ORDNER TEAM_INIT_SMOKE_TEST TEAM_INIT_TECH_STACK
    TEAM_INIT_WEITERER_CODE TEAM_INIT_DOMAENEN TEAM_INIT_COMMIT_MODUS

  Der Installer ist idempotent: ein zweiter Lauf ueberschreibt nichts, sondern
  meldet, was bereits vorhanden ist.

  ZWEI DINGE SIND HIER BESSER ALS IM BASH-ORIGINAL, nicht nur anders:
    * Die Platzhalter-Ersetzung braucht kein eingebettetes Python mehr. In
      install.sh steckt dafuer ein Here-Doc mit einem Python-Skript darin —
      ein Fremdkoerper, den hier .NET-Bordmittel ersetzen.
    * Die Sperrpruefung vor einem Update ist eine ECHTE, vom Betriebssystem
      durchgesetzte Sperre (FileShare::None) statt des kooperativen flock.

  UND EINES IST SCHLECHTER, ausdruecklich benannt: Der Selbsttest kann die
  .sh-Entrypoints nicht syntaktisch pruefen, weil unter Windows keine bash
  vorliegt. Er prueft die .ps1-Dateien und SAGT, was er nicht geprueft hat.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$Ziel = "",
    [switch]$NichtInteraktiv,
    [switch]$Force,
    [switch]$Update,
    # Ausdrueckliche Abwahl einer Bahn durch den Anwender (BL-119). Default
    # ist BEIDES — die Begruendung steht am Kopierblock: Die zwei
    # Konfigurationen sind zwei Generate EINER Quelle, und wer nur eine Bahn
    # bekommt, schreibt die andere irgendwann von Hand. Genau dort faengt
    # Drift an. Zurueckgeholt wird mit -Update ohne Schalter.
    [switch]$NurBash,
    [switch]$NurPwsh
)

$ErrorActionPreference = 'Stop'
# BL-122: Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
# standardmaessig $true — ein Exit-Code != 0 aus einem NATIVEN Befehl ist damit
# ein TERMINIERENDER Fehler und nicht mehr nur ein Wert in $LASTEXITCODE. Diese
# Bahn ist durchgehend fuer den klassischen Vertrag geschrieben: aufrufen,
# $LASTEXITCODE lesen, entscheiden. Ohne diese Zeile ist jede dieser
# Entscheidungen unerreichbar — der Abbruch kommt vorher.
$PSNativeCommandUseErrorActionPreference = $false

if ($NurBash -and $NurPwsh) {
    Write-Host "FEHLER: -NurBash und -NurPwsh schliessen einander aus." -ForegroundColor Red
    exit 2
}
$NurBahn = if ($NurBash) { 'bash' } elseif ($NurPwsh) { 'pwsh' } else { '' }

function Test-BahnAbgewaehlt {
    <#
      Gehoert die Datei zu einer abgewaehlten Bahn? Entschieden wird ueber die
      ENDUNG, weil der Installer hier Kit-Pfade (bash\entry\…) auf
      Projekt-Pfade (ralph.sh in der Wurzel) abbildet — der Bahn-Ordner ist an
      dieser Stelle schon weg.
    #>
    param([string]$Pfad)
    switch ($script:NurBahn) {
        'bash' { return $Pfad -match '\.(ps1|psm1|cmd)$' }
        'pwsh' { return $Pfad -match '\.sh$' }
    }
    return $false
}

# Zwei Anker seit der Bahn-Trennung: BAHN ist <kit>\pwsh (hier liegt dieses
# Skript), KIT die Wurzel des Kits. Der Installer liest aus BEIDEN Bahnen —
# er installiert bewusst auch die Bash-Seite (Begruendung weiter unten).
$BAHN = Split-Path -Parent $PSCommandPath
$KIT  = Split-Path -Parent $BAHN
$Interaktiv = -not $NichtInteraktiv -and -not [Console]::IsInputRedirected

function Team-CfgDir {
    # %APPDATA% ist der richtige Ort unter Windows. Der Rueckfall haelt das
    # Skript auf Nicht-Windows lauffaehig und zeigt dort auf DIESELBE Ablage,
    # die die Bash-Bahn benutzt — eine Maschine, eine Auth-Konfiguration.
    # Bewusst in jedem Bootstrap-Skript einzeln: Sie duerfen von team/lib.psm1
    # nicht abhaengen, denn sie laufen, BEVOR es die Bibliothek gibt.
    if ($env:APPDATA) { return (Join-Path $env:APPDATA 'claude-team') }
    return (Join-Path $HOME '.config/claude-team')
}

function Rot($t)   { Write-Host $t -ForegroundColor Red }
function Gruen($t) { Write-Host $t -ForegroundColor Green }
function Gelb($t)  { Write-Host $t -ForegroundColor Yellow }
function Kopf($t)  { Write-Host ""; Write-Host $t -ForegroundColor White }

if (-not $Ziel) {
    Rot "FEHLER: Kein Zielpfad angegeben."
    Write-Host "Aufruf: pwsh -File install.ps1 <zielpfad>"
    exit 2
}
try { $Ziel = (Resolve-Path $Ziel -ErrorAction Stop).Path }
catch { Rot "FEHLER: Zielpfad existiert nicht: $Ziel"; exit 2 }

if ($Update -and $Force) {
    Rot "FEHLER: -Update und -Force schliessen sich aus."
    Write-Host "  -Update hebt ein gelebtes Projekt sicher auf eine neue Kit-Version."
    Write-Host "  -Force ueberschreibt ALLES, auch Ledger, State und Beutebuch."
    exit 2
}

# --- Platzhalter ---------------------------------------------------------------
# Die Werte, die das Aufnahme-Interview sammelt. Ein Buch statt vieler
# Einzelvariablen: Es wandert als Ganzes in Fuelle-Datei und laesst sich damit
# nicht versehentlich halb weitergeben.
$script:Werte = @{}

function Team-Kodierung {
    <#
      BL-113 — die Kodierungsregel des Kits, an EINER Stelle:

          .ps1 / .psm1  ->  UTF-8 MIT BOM
          alles andere  ->  UTF-8 OHNE BOM

      Beide Haelften sind aus dem Feld bezahlt, und sie widersprechen sich nur
      scheinbar.

      OHNE BOM, weil ein BOM am Anfang einer .sh-Datei aus der Shebang-Zeile
      Zeichensalat macht — dasselbe Fehlerbild wie CRLF, nur seltener und
      deshalb schwerer zuzuordnen. Und weil Pythons json.load ueber einem BOM
      abbricht: kosten.py hat eine so verdorbene Datei stillschweigend als
      0.0000 gezaehlt.

      MIT BOM fuer PowerShell-Quelltext, weil Windows PowerShell 5.1 eine Datei
      ohne BOM NICHT als UTF-8 liest, sondern in der ANSI-Codepage (bei uns
      1252). Ein Geviertstrich (U+2014, in UTF-8 E2 80 94) wird dabei zu
      `â€"` — und das letzte Zeichen davon ist U+201D, ein typografisches
      Anfuehrungszeichen. PowerShell akzeptiert die als echte Stringgrenze.
      Jeder Gedankenstrich in einer Zeichenkette SCHLIESST sie also mitten im
      Satz, der Rest der Zeile zerfaellt in nackte Bezeichner, und die Datei
      stirbt beim Parsen:

          Unexpected token 'wird' in expression or statement.
          Missing argument in parameter list.

      Das Fehlerbild ist besonders teuer, weil es VOR jeder Zeile Code
      auftritt: Die Versionspruefung in kit-einrichten.ps1, die genau diesen
      Fall erklaeren wuerde ("PowerShell 5.1 ist zu alt, nimm pwsh"), wird nie
      erreicht. Der Anwender sieht zehn Syntaxfehler statt eines Hinweises.

      Unter Linux ist das nicht messbar: pwsh 7 liest UTF-8 ohne BOM korrekt.
      Die ganze pwsh-Bahn ist gegen pwsh 7 gefahren worden und blieb
      trotzdem gruen. Deshalb ist die Regel jetzt eine Pruefung (kit-test.sh
      Schritt 10) und nicht nur ein Kommentar.
    #>
    param([string]$Pfad)
    $mitBom = [System.IO.Path]::GetExtension($Pfad) -in @('.ps1', '.psm1')
    return (New-Object System.Text.UTF8Encoding($mitBom))
}

function Fuelle-Datei {
    <#
      Ersetzt die {{PLATZHALTER}} in einer Datei. In install.sh macht das ein
      eingebettetes Python-Here-Doc; hier reichen Bordmittel.
    #>
    param([string]$Pfad)
    if (-not (Test-Path $Pfad -PathType Leaf)) { return }
    # ReadAllText erkennt ein vorhandenes BOM und entfernt es aus dem Text;
    # welche Kodierung beim Schreiben gilt, entscheidet allein Team-Kodierung.
    $text = [System.IO.File]::ReadAllText($Pfad)
    foreach ($schluessel in $script:Werte.Keys) {
        $text = $text.Replace($schluessel, [string]$script:Werte[$schluessel])
    }
    [System.IO.File]::WriteAllText($Pfad, $text, (Team-Kodierung $Pfad))
}

function Setze-Werte {
    <#
      Baut das Platzhalter-Buch. Die Liste ist zeichengleich mit der in
      install.sh — wer hier etwas ergaenzt, ergaenzt es dort auch, sonst
      bekommt eine der beiden Konfigurationen einen ungefuellten Platzhalter
      und niemand merkt es, bis eine Rolle laeuft.
    #>
    param($Projekt, $Produktivcode, $TestOrdner, $PlanOrdner, $SmokeTest,
          $TechStack, $Deploy, $DeployAusnahmen, $Domaenen, $CommitEntscheid,
          $WeitererCode, $TestBestand, $PlanBestand, $Python)
    $planKurz = $PlanOrdner.TrimEnd('/')
    $script:Werte = [ordered]@{
        '{{PROJEKTNAME}}'      = $Projekt
        '{{PRODUKTIVCODE}}'    = $Produktivcode
        '{{TEST_ORDNER}}'      = $TestOrdner
        '{{PLAN_ORDNER}}'      = $planKurz
        '{{BEUTEBUCH}}'        = "$planKurz/beutebuch.md"
        '{{CHANGELOG}}'        = 'CHANGELOG.md'
        '{{FIX_PRAEFIX}}'      = 'fix(uat)'
        '{{FEAT_PRAEFIX}}'     = 'feat'
        '{{SMOKE_TEST}}'       = $(if ($SmokeTest) { $SmokeTest } else { 'TODO: noch keiner — Stufe 1 der ersten Kaskade' })
        '{{TECH_STACK}}'       = $TechStack
        '{{DEPLOY}}'           = $Deploy
        '{{DEPLOY_AUSNAHMEN}}' = $DeployAusnahmen
        '{{DOMAENEN}}'         = $Domaenen
        '{{COMMIT_ENTSCHEID}}' = $CommitEntscheid
        '{{PYTHON}}'           = $Python
        '{{WEITERER_CODE}}'    = $WeitererCode
        '{{TEST_BESTAND}}'     = $TestBestand
        '{{PLAN_BESTAND}}'     = $PlanBestand
    }
}

function Finde-Python {
    <#
      BL-122. Drei Dinge, die diese Fassung anders macht als die alte:

      1. REIHENFOLGE NACH PLATTFORM. Der Windows-Installer von python.org und
         `winget install Python.Python.3.x` legen python.exe und den
         py-Launcher an — KEIN python3.exe. Was Get-Command unter Windows als
         python3 findet, ist deshalb meist der App-Execution-Alias aus
         %LOCALAPPDATA%\Microsoft\WindowsApps: ein Platzhalter, der keinen
         Interpreter startet, sondern den Microsoft Store oeffnet und mit 9009
         endet. Unter Linux ist es genau umgekehrt — dort kann `python`
         fehlen oder auf Python 2 zeigen. Also fragt jede Plattform zuerst
         nach dem Namen, der bei ihr der richtige ist.

      2. try/catch UM DIE PROBE. Der Platzhalter endet mit Exit-Code != 0, und
         dieses Skript laeuft unter $ErrorActionPreference = 'Stop'. Auch mit
         dem Pin oben ist der Griff hier billig und die Absicht steht dabei:
         Ein Kandidat, der nicht laeuft, wird UEBERSPRUNGEN, nie zum Abbruch.

      3. VERSION STATT LEBENSZEICHEN. `print(1)` beantwortet auch ein Python 2
         klaglos. Gefragt wird deshalb nach der Version, und 3.8 ist die
         Untergrenze — dieselbe wie in kit-einrichten.ps1.

      Rueckgabe: der Befehlsname, oder $null. KEIN stiller Rueckfall mehr auf
      'python3': Der trug sich unter Windows in team.config.ps1 ein und liess
      Kosten und Beutebuch dort auf einen Namen zeigen, den es auf der
      Maschine nachweislich nicht gibt.
    #>
    if (Get-Variable -Name GefundenesPython -Scope Script -ErrorAction SilentlyContinue) {
        if ($script:GefundenesPython) { return $script:GefundenesPython }
    }
    $kandidaten = if ($IsWindows) { @('python', 'python3', 'py') }
                  else            { @('python3', 'python', 'py') }
    foreach ($kandidat in $kandidaten) {
        if (-not (Get-Command $kandidat -ErrorAction SilentlyContinue)) { continue }
        $v = $null
        try { $v = & $kandidat -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>$null }
        catch { continue }
        if ($LASTEXITCODE -ne 0 -or -not $v) { continue }
        # Bewusst -match statt -notmatch: Ob -notmatch $Matches fuellt, ist eine
        # Feinheit, die man nachschlaegt statt sie zu wissen. Hier wird nichts
        # gelesen, was nicht sichtbar gesetzt wurde.
        if ("$v".Trim() -match '^(\d+)\.(\d+)$') {
            $gross = [int]$Matches[1]; $klein = [int]$Matches[2]
            if ($gross -gt 3 -or ($gross -eq 3 -and $klein -ge 8)) {
                $script:GefundenesPython = $kandidat
                return $kandidat
            }
        }
    }
    return $null
}

function Finde-Pytest {
    <#
      BL-124. Bevorzugt wird der MODULAUFRUF ueber denselben Interpreter, unter
      dem auch team/tools/ laeuft. Zwei Gruende, und der zweite ist der, der im
      Feld zuschlug:

      1. Eine pytest.exe im PATH kann zu einer ANDEREN Python-Installation
         gehoeren. Dann testet man etwas anderes, als man betreibt.
      2. Unter Windows legt `pip install pytest` die ausfuehrbare Datei in ein
         Scripts-Verzeichnis, das oft NICHT im PATH steht — bei `--user` warnt
         pip beim Installieren sogar davor. Get-Command findet dann nichts,
         waehrend das Modul laengst installiert ist, und der Installer meldete
         "pytest nicht installiert — Regressionstests uebersprungen".

      Rueckgabe: @{ Befehl = ...; Vorab = @(...) } oder $null.
    #>
    $py = Finde-Python
    if ($py) {
        $ok = $false
        try { & $py -m pytest --version 2>$null | Out-Null; $ok = ($LASTEXITCODE -eq 0) } catch { $ok = $false }
        if ($ok) { return @{ Befehl = $py; Vorab = @('-m', 'pytest') } }
    }
    if (Get-Command pytest -ErrorAction SilentlyContinue) {
        return @{ Befehl = 'pytest'; Vorab = @() }
    }
    return $null
}

function Python-Fuer-Config {
    # Was als {{PYTHON}} in team.config.ps1 landet. Faellt die Probe aus, wird
    # der Wert trotzdem gesetzt — aber die Luecke wird GENANNT statt verdeckt.
    $p = Finde-Python
    if ($p) { return $p }
    $vorgabe = if ($IsWindows) { 'python' } else { 'python3' }
    Gelb "  [!] Kein lauffaehiger Python 3.8+ gefunden (geprueft: Start UND Version)."
    Gelb "      team.config.ps1 bekommt '$vorgabe' — Kosten und Beutebuch laufen"
    Gelb "      erst, wenn ein Interpreter unter diesem Namen im PATH steht."
    return $vorgabe
}

# --- .gitignore ----------------------------------------------------------------
function Gitignore-Abgleich {
    <#
      BL-109: "Der Block ist da" heisst NICHT "der Block ist vollstaendig". Das
      Fragment waechst mit dem Kit; wer frueh installiert und seither brav
      -Update gefahren hat, bliebe sonst dauerhaft auf dem Fragmentstand seines
      Installationstages — waehrend der Installer Erfolg meldet.

      Ergaenzt wird nur bei der ERSTINSTALLATION und nur der ganze Block.
      Fehlende Einzelzeilen werden ausschliesslich GEMELDET: Eine fehlende
      Zeile kann eine bewusst entfernte sein, und -Update fasst Projektdateien
      grundsaetzlich nicht an.
    #>
    param([ValidateSet('ergaenzen', 'melden')][string]$Modus)
    $fragment = Join-Path $KIT 'bootstrap\gitignore.fragment'
    $datei = Join-Path $Ziel '.gitignore'
    $vorhanden = if (Test-Path $datei) { [System.IO.File]::ReadAllText($datei) } else { "" }

    if ($Modus -eq 'ergaenzen' -and $vorhanden -notmatch 'T\.E\.A\.M\.-Loop-Laufzeitartefakte') {
        Add-Content -Path $datei -Value ([System.IO.File]::ReadAllText($fragment)) -NoNewline
        Gruen "  [ok] .gitignore ergaenzt"
        return
    }
    # Zeile fuer Zeile, nicht der Block als Ganzes: Der Block kann seit Jahren
    # dastehen und trotzdem die Haelfte der Vorlage vermissen.
    $bestand = @($vorhanden -split "`r?`n")
    $fehlende = @()
    foreach ($zeile in ([System.IO.File]::ReadAllLines($fragment))) {
        if (-not $zeile.Trim() -or $zeile.TrimStart().StartsWith('#')) { continue }
        if ($bestand -notcontains $zeile) { $fehlende += $zeile }
    }
    if ($fehlende.Count -eq 0) {
        Gruen "  [ok] .gitignore enthaelt den Block vollstaendig"
        return
    }
    Gelb "  [!] .gitignore liegt $($fehlende.Count) Zeile(n) hinter der Vorlage — es fehlen:"
    foreach ($z in $fehlende) { Gelb "        $z" }
    Gelb "    Nicht automatisch ergaenzt (eine fehlende Zeile kann eine bewusst"
    Gelb "    entfernte sein) — nachtragen mit:"
    Gelb "      `"$($fehlende -join "``n")`" | Add-Content `"$datei`""
}

# --- Kopieren -------------------------------------------------------------------
$script:Geschrieben = 0
$script:Uebersprungen = 0
$script:Abweichend = @()

function Kopiere {
    param([string]$Quelle, [string]$Rel, [switch]$Immer)
    $zielDatei = Join-Path $Ziel $Rel
    $ordner = Split-Path -Parent $zielDatei
    if ($ordner) { New-Item -ItemType Directory -Force -Path $ordner | Out-Null }
    if ((Test-Path $zielDatei) -and -not $Force -and -not $Immer) {
        $script:Uebersprungen++
        return
    }
    # BL-12: Wich die installierte Fassung vom Kit ab, kann darin ein LOKALER
    # Fix stecken, den noch niemand ans Kit zurueckgemeldet hat. Genau so ging
    # im Feld ein 12-USD-Fix an beutebuch.py verloren. Briefings sind
    # ausgenommen: Sie werden ohnehin neu gerendert und weichen durch die
    # gefuellten Platzhalter immer ab.
    if ($Immer -and (Test-Path $zielDatei) -and $Rel -notlike 'team/prompts/*') {
        $a = [System.IO.File]::ReadAllBytes($Quelle)
        $b = [System.IO.File]::ReadAllBytes($zielDatei)
        if ($a.Length -ne $b.Length -or [System.Convert]::ToBase64String($a) -ne [System.Convert]::ToBase64String($b)) {
            $script:Abweichend += $Rel
        }
    }
    Copy-Item -Path $Quelle -Destination $zielDatei -Force
    $script:Geschrieben++
}

function Schreibe {
    param([string]$Rel, [string]$Inhalt)
    $zielDatei = Join-Path $Ziel $Rel
    $ordner = Split-Path -Parent $zielDatei
    if ($ordner) { New-Item -ItemType Directory -Force -Path $ordner | Out-Null }
    if ((Test-Path $zielDatei) -and -not $Force) { $script:Uebersprungen++; return }
    [System.IO.File]::WriteAllText($zielDatei, $Inhalt, (Team-Kodierung $zielDatei))
    $script:Geschrieben++
}

function Kopiere-Infrastruktur {
    <#
      Die Dateien, die BEIDE Bahnen ausmachen. Aufgerufen von Erstinstallation
      und Update — damit kann keiner der beiden Wege eine Datei vergessen, die
      der andere kennt.
    #>
    param([switch]$Immer, [switch]$OhneConfig)
    # Je Bahn ein eigener Ordner, seit die Ablage getrennt ist. Die Paarung
    # Ordner/Muster steht ausdruecklich da: Ein Glob ueber beide Ordner wuerde
    # sonst wieder zusammenwerfen, was hier gerade getrennt wurde.
    foreach ($quelle in @(
            @{ Ordner = 'bash\entry'; Muster = '*.sh'  },
            @{ Ordner = 'pwsh\entry'; Muster = '*.ps1' },
            @{ Ordner = 'pwsh\entry'; Muster = '*.cmd' })) {
        foreach ($f in (Get-ChildItem (Join-Path $KIT $quelle.Ordner) -Filter $quelle.Muster -File -ErrorAction SilentlyContinue)) {
            if ($OhneConfig -and $f.Name -in @('team.config.sh', 'team.config.ps1')) { continue }
            if (Test-BahnAbgewaehlt $f.Name) { continue }
            Kopiere $f.FullName $f.Name -Immer:$Immer
        }
    }
    foreach ($f in @('bash\lib.sh', 'bash\redteam.sh')) {
        if (Test-BahnAbgewaehlt $f) { continue }
        Kopiere (Join-Path $KIT $f) "team/$(Split-Path -Leaf $f)" -Immer:$Immer
    }
    # *.psm1 UND *.ps1: team/redteam.ps1 ist die gemeinsame Sweep-Logik von
    # Harry und Marv. Sie fiel zuerst durch das Raster, weil unter team/ nur
    # nach lib-Modulen gesucht wurde — die Rollen starteten dann mit
    # "term './team/redteam.ps1' is not recognized". Die Gleichstandspruefung
    # in kit-test.sh sieht so etwas NICHT: Beide Installer waren gleich falsch.
    # Gefunden hat es der Trockenlauf, und genau dafuer steht er im Plan.
    # Ausdruecklich aufgezaehlt statt per Glob: pwsh\ enthaelt seit der
    # Bahn-Trennung AUCH install.ps1, kit-test.ps1, kit-einrichten.ps1 und
    # pruefe-windows.ps1. Ein '*.ps1' ueber den Ordner kopierte die vier
    # Kit-Werkzeuge in das team/ des Zielprojekts.
    foreach ($f in @('pwsh\lib.psm1', 'pwsh\redteam.ps1')) {
        if (Test-BahnAbgewaehlt $f) { continue }
        $voll = Join-Path $KIT $f
        if (Test-Path $voll) { Kopiere $voll "team/$(Split-Path -Leaf $f)" -Immer:$Immer }
    }
    foreach ($f in (Get-ChildItem (Join-Path $KIT 'geteilt\tools') -Filter '*.py' -File)) {
        Kopiere $f.FullName "team/tools/$($f.Name)" -Immer:$Immer
    }
    foreach ($f in (Get-ChildItem (Join-Path $KIT 'geteilt\prompts') -Filter '*.md' -File)) {
        Kopiere $f.FullName "team/prompts/$($f.Name)" -Immer:$Immer
    }
    foreach ($f in (Get-ChildItem (Join-Path $KIT 'geteilt\tests') -Filter 'test_*.py' -File)) {
        Kopiere $f.FullName "team/tests/$($f.Name)" -Immer:$Immer
    }
    # conftest.py ist KEIN Test, aber ohne sie laeuft keiner der Tests, die den
    # Doppelbahn-Harnisch nehmen. Sie faellt durch das test_*.py-Muster.
    Kopiere (Join-Path $KIT 'geteilt\tests\conftest.py') 'team/tests/conftest.py' -Immer:$Immer
}

# ================================================================ Update-Pfad
if ($Update) {
    Kopf "Update — nur Team-Infrastruktur"
    # BL-126: Als Merkmal einer Installation zaehlt JEDE der beiden
    # Konfigurationen. Bis hierher zaehlte nur die Bash-Fassung — und damit
    # war der Rueckweg, den BL-119 ausdruecklich verspricht ("ein Update ohne
    # Schalter macht das Projekt wieder vollstaendig"), fuer ein mit -NurPwsh
    # installiertes Projekt versperrt: Der Installer erklaerte es fuer keine
    # Installation und stieg aus, bevor er die fehlende Bahn nachziehen
    # konnte. Auf dieser Bahn wiegt es schwerer als auf der anderen — ein
    # Windows-Projekt OHNE bash ist der Normalfall, fuer den sie gebaut ist.
    $configSh  = Join-Path $Ziel 'team.config.sh'
    $configPs1 = Join-Path $Ziel 'team.config.ps1'
    if (-not (Test-Path $configSh) -and -not (Test-Path $configPs1)) {
        Rot "FEHLER: $Ziel sieht nicht nach einer T.E.A.M.-Installation aus"
        Write-Host "  (weder team.config.sh noch team.config.ps1). Fuer eine"
        Write-Host "  Erstinstallation ohne -Update aufrufen."
        exit 2
    }

    # BL-10: NIEMALS in einen laufenden Lauf hinein aktualisieren. Real
    # passiert: Ein Update waehrend eines aktiven Laufs legte frische,
    # uncommittete Dateien in team/ ab; der naechste Read-Only-Lauf wertete sie
    # als Guard-Verletzung, rollte sie zurueck und buchte seine Runde als
    # Fehlschlag — dritte Stagnation in Folge, Lauf gestoppt.
    #
    # Hier steht eine ECHTE Sperrpruefung: FileShare::None wird vom
    # Betriebssystem durchgesetzt, anders als das kooperative flock.
    $lock = Join-Path $Ziel '.team-loop.lock'
    if (Test-Path $lock) {
        $frei = $false
        try {
            $s = [System.IO.File]::Open($lock, [System.IO.FileMode]::Open,
                 [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
            $s.Close(); $frei = $true
        } catch { $frei = $false }
        if (-not $frei) {
            Rot "FEHLER: In $Ziel laeuft gerade ein Team-Lauf (.team-loop.lock ist gehalten)."
            Write-Host "  Ein Update wuerde uncommittete Dateien in team\ ablegen. Der naechste"
            Write-Host "  Read-Only-Lauf (Harry/Marv/Axel) wertet die als Guard-Verletzung,"
            Write-Host "  raeumt sie weg und bucht seine Runde als Fehlschlag — im Feld hat das"
            Write-Host "  einen laufenden Lauf gestoppt (BL-10)."
            Write-Host "  Erst den Lauf beenden lassen, dann erneut aufrufen."
            exit 2
        }
    }

    $dreckig = & git -C $Ziel status --porcelain 2>$null
    if ($dreckig) {
        Gelb "  [!] Der Arbeitsbaum ist nicht sauber. Das Update mischt seine Dateien"
        Gelb "      unter deine. Empfehlung: abbrechen (Strg+C), erst committen."
        Gelb "      Weiter in 5 s ..."
        Start-Sleep -Seconds 5
    }

    # Projektwerte aus der INSTALLIERTEN Konfiguration lesen, nicht aus den
    # Defaults — sonst bekaemen die Rollen-Briefings die falschen Pfade und
    # damit eine falsche Guard-Grenze.
    #
    # Bevorzugt die .sh-Fassung: Sie liegt in jeder zweibahnigen Ablage, auch
    # in einer, die vor der pwsh-Bahn entstanden ist. Sie liegt aber NICHT in
    # einem mit -NurPwsh installierten Projekt (BL-126) — dort stehen die
    # Werte nur in der .ps1, und die hat eine eigene, ebenso feste Form:
    # $TEAM_X = Team-Wert 'TEAM_X' 'wert'. Gelesen statt gesourct, wie auf der
    # anderen Bahn: Ein Dot-Sourcing wuerde die Konfiguration des ZIELS in
    # den Installer laden und dessen eigene Variablen ueberschreiben.
    $konf = @{}
    if (Test-Path $configSh) {
        $konfQuelle = 'team.config.sh'
        foreach ($zeile in [System.IO.File]::ReadAllLines($configSh)) {
            $m = [regex]::Match($zeile, '^(TEAM_[A-Z_]+)="\$\{\1:-(.*)\}"\s*$')
            if ($m.Success) { $konf[$m.Groups[1].Value] = $m.Groups[2].Value }
        }
    } else {
        $konfQuelle = 'team.config.ps1'
        foreach ($zeile in [System.IO.File]::ReadAllLines($configPs1)) {
            $m = [regex]::Match($zeile, '^\$(TEAM_[A-Z_]+)\s*=\s*Team-Wert\s+''\1''\s+''(.*)''\s*$')
            if ($m.Success) { $konf[$m.Groups[1].Value] = $m.Groups[2].Value }
        }
    }
    function Konf($name, $vorgabe) {
        if ($konf.ContainsKey($name) -and $konf[$name]) { return $konf[$name] }
        return $vorgabe
    }
    $Projekt       = Konf 'TEAM_PROJEKT' (Split-Path -Leaf $Ziel)
    $Produktivcode = Konf 'TEAM_PRODUKTIVCODE' 'src/'
    $TestOrdner    = Konf 'TEAM_TEST_ORDNER' 'tests/'
    $PlanOrdner    = Konf 'TEAM_PLAN_ORDNER' 'plans/'
    $SmokeTest     = Konf 'TEAM_SMOKE_TEST' ''
    $Domaenen      = Konf 'TEAM_DOMAENEN' 'produkt'
    Gruen "  [ok] Projektwerte aus $konfQuelle gelesen (Projekt: $Projekt)"

    # BL-51: -Update ist der einzige Zeitpunkt, zu dem jemand von aussen auf die
    # Installation schaut. Gemeldet wird NUR, was in der Config steht — keine
    # Heuristik ueber den Ordnerinhalt. Eine Warnung, die bei jedem Aufruf
    # erscheint, erzieht zum Wegsehen (BL-14).
    $planBestand = Konf 'TEAM_PLAN_ORDNER_BESTAND' ''
    $testBestand = Konf 'TEAM_TEST_ORDNER_BESTAND' ''
    if ($planBestand -or $testBestand) {
        Kopf "Bestand in der Schreibzone (BL-51)"
        if ($planBestand) { Write-Host "  - ${PlanOrdner}: $planBestand" }
        if ($testBestand) { Write-Host "  - ${TestOrdner}: $testBestand" }
        Gelb "  Diese Dateien lagen beim Einzug des Teams schon da und stehen"
        Gelb "  auf der Guard-Whitelist — die Read-Only-Rollen duerfen sie"
        Gelb "  aendern und loeschen. Die Rollen-Prompts nennen sie als fremdes"
        Gelb "  Eigentum; erzwingen kann der Guard es nicht."
    }

    # Der Commit-Entscheid steht NUR im Architekten-Briefing, nicht in der
    # Config. Aus der bestehenden Datei retten, statt ihn stillschweigend auf
    # den Default zurueckzusetzen.
    $architektAlt = Join-Path $Ziel 'team\prompts\rolle-architekt.md'
    $commitEntscheid = ""
    if (Test-Path $architektAlt) {
        $t = [regex]::Match([System.IO.File]::ReadAllText($architektAlt),
                            '(?m)^\*\*Committen:\*\* (.+)$')
        if ($t.Success) { $commitEntscheid = $t.Groups[1].Value }
    }
    if ($commitEntscheid) {
        Gruen "  [ok] Commit-Entscheid aus dem bisherigen Briefing uebernommen"
    } else {
        $commitEntscheid = 'Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Strippenzieher führt sie aus.'
        Gelb "  [!] Commit-Entscheid nicht lesbar — Default (nicht selbst committen) gesetzt."
    }

    Setze-Werte $Projekt $Produktivcode $TestOrdner $PlanOrdner $SmokeTest `
                'TODO: in CLAUDE.md nachtragen' 'TODO: in CLAUDE.md nachtragen' 'keine' `
                $Domaenen $commitEntscheid '' $testBestand $planBestand (Python-Fuer-Config)

    Kopiere-Infrastruktur -Immer -OhneConfig

    # BL-119, die Gegenprobe zum Abwahl-Schalter: Ein Update OHNE Schalter
    # macht das Projekt wieder vollstaendig. Der Haken sitzt an einer Stelle,
    # die man leicht uebersieht — die Entrypoints kommen zurueck, die
    # KONFIGURATION nicht: -OhneConfig oben schliesst team.config.* aus, weil
    # sie Projektdaten traegt. Richtig, solange sie DA ist. Fehlt sie, ist
    # "nicht anfassen" kein Schutz mehr, sondern eine halbe Bahn — ralph.sh
    # laege da und faende keine Werte.
    foreach ($paar in @(
            @{ Quelle = 'bash\entry\team.config.sh';  Name = 'team.config.sh'  },
            @{ Quelle = 'pwsh\entry\team.config.ps1'; Name = 'team.config.ps1' })) {
        $quelle = Join-Path $KIT $paar.Quelle
        if (-not (Test-Path $quelle))                { continue }
        if (Test-BahnAbgewaehlt $paar.Name)          { continue }
        if (Test-Path (Join-Path $Ziel $paar.Name))  { continue }
        Kopiere $quelle $paar.Name -Immer
        Fuelle-Datei (Join-Path $Ziel $paar.Name)
        Gelb "  [!] $($paar.Name) fehlte und ist neu erzeugt worden — aus den Werten"
        Write-Host "      der vorhandenen Konfiguration, nicht aus den Auslieferungswerten."
        Write-Host "      Bitte gegenlesen: $(Join-Path $Ziel $paar.Name)"
    }

    $fremdeTests = @()
    $zielTests = Join-Path $Ziel 'team\tests'
    if (Test-Path $zielTests) {
        foreach ($f in (Get-ChildItem $zielTests -Filter 'test_*.py' -File)) {
            if (-not (Test-Path (Join-Path $KIT "geteilt\tests\$($f.Name)"))) { $fremdeTests += $f.Name }
        }
    }
    foreach ($f in (Get-ChildItem (Join-Path $Ziel 'team\prompts') -Filter '*.md' -File)) {
        Fuelle-Datei $f.FullName
    }
    Gruen "  [ok] $($script:Geschrieben) Infrastruktur-Dateien aktualisiert"

    if ($script:Abweichend.Count) {
        Kopf "Ersetzt, obwohl abweichend — bitte gegenlesen"
        foreach ($f in $script:Abweichend) { Write-Host "  ! $f" }
        Gelb "  Diese Dateien wichen von der Kit-Fassung ab. Meist ist das nur"
        Gelb "  eine aeltere Version — es kann aber ein LOKALER Fix sein, den"
        Gelb "  niemand ans Kit zurueckgemeldet hat. Im Feld ging so ein Fix"
        Gelb "  ueber 12,00 USD verloren (BL-12)."
        Gelb "  Pruefen mit:  git -C $Ziel diff -- $($script:Abweichend -join ' ')"
    }
    if ($fremdeTests.Count) {
        Kopf "Unbekannte Tests in team\tests (unangetastet gelassen)"
        foreach ($f in $fremdeTests) { Write-Host "  - $f" }
        Write-Host "  Kennt das Kit nicht — entweder vom Projekt ergaenzt (dann ans Kit"
        Write-Host "  melden) oder Rest einer Altversion (dann loeschen)."
    }

    Kopf "Unangetastet geblieben (Projektdaten)"
    foreach ($d in @('team.config.sh', 'team.config.ps1', 'CLAUDE.md', 'CHANGELOG.md',
                     '.budget-ledger', '.ralph-state', '.gitignore', $PlanOrdner)) {
        if (Test-Path (Join-Path $Ziel $d)) { Write-Host "  - $d" }
    }

    Kopf ".gitignore gegen die Vorlage (BL-109)"
    Gitignore-Abgleich melden

    Kopf "Selbsttest"
    $fehler = 0
    foreach ($f in (Get-ChildItem $Ziel -Filter '*.ps1' -File)) {
        $syntax = $null
        [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$syntax) | Out-Null
        if ($syntax) { Rot "  [x] Syntaxfehler: $($f.Name)"; $fehler = 1 }
    }
    if ($fehler -eq 0) { Gruen "  [ok] Alle PowerShell-Skripte syntaktisch korrekt" }
    Gelb "  [!] Die .sh-Entrypoints wurden NICHT geprueft — hier liegt keine bash."
    Gelb "      Sie sind mitinstalliert und gelten unveraendert aus dem Kit."

    $pt = Finde-Pytest
    if ($pt) {
        # OHNE die TEAM_*-Variablen, die dieser Prozess geerbt haben koennte:
        # Sonst gilt z. B. TEAM_DOMAENEN des Projekts auch fuer die Fixtures.
        $gemerkt = @{}
        foreach ($v in (Get-ChildItem Env: | Where-Object { $_.Name -like 'TEAM_*' })) {
            $gemerkt[$v.Name] = $v.Value
            Remove-Item "Env:$($v.Name)"
        }
        try {
            Push-Location $Ziel
            $log = Join-Path ([System.IO.Path]::GetTempPath()) 'team-update-pytest.log'
            $vorab = $pt.Vorab
            & $pt.Befehl @vorab -q team/tests *> $log
            if ($LASTEXITCODE -eq 0) {
                $zeile = (Select-String -Path $log -Pattern '\d+ passed' | Select-Object -First 1)
                Gruen "  [ok] Regressionstests gruen ($($zeile.Matches[0].Value))"
            } else {
                Rot "  [x] Regressionstests NICHT gruen — Log: $log"
                Get-Content -Tail 3 $log | ForEach-Object { Write-Host "      $_" }
                $fehler = 1
            }
        } finally {
            Pop-Location
            foreach ($k in $gemerkt.Keys) { Set-Item "Env:$k" $gemerkt[$k] }
        }
    }

    Kopf "Update fertig"
    Rot  "  JETZT COMMITTEN — vor dem naechsten Lauf, nicht danach."
    Write-Host "    git -C `"$Ziel`" add -A; git -C `"$Ziel`" commit -m `"chore: T.E.A.M. aktualisiert`""
    Write-Host ""
    Write-Host "  Warum das keine Formalie ist: Die neuen Dateien liegen uncommittet in"
    Write-Host "  team\. Der naechste Read-Only-Lauf sieht sie ausserhalb seiner Whitelist,"
    Write-Host "  wertet sie als Guard-Verletzung und raeumt sie weg — das Update waere"
    Write-Host "  still wieder verschwunden (BL-10)."
    exit $fehler
}

# ========================================================= A.1 Vorbedingungen
Kopf "A.1 — Vorbedingungen"
& git -C $Ziel rev-parse --is-inside-work-tree 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Rot "FEHLER: $Ziel ist kein Git-Repository."
    Write-Host "  Die Rollen committen, rollen zurueck und pruefen Commit-Bereiche —"
    Write-Host "  ohne Git funktioniert davon nichts. Zuerst: git -C `"$Ziel`" init"
    exit 2
}
Gruen "  [ok] Git-Repository"

$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($claude) {
    Gruen "  [ok] Claude-CLI: $(@(& claude --version 2>&1)[0])"
} else {
    Gelb "  [!] Claude-CLI nicht gefunden — die Dateien werden trotzdem installiert,"
    Gelb "      aber kein Loop kann laufen, bis 'claude' im PATH ist."
}

$cfgDir = Team-CfgDir
if ((Test-Path (Join-Path $cfgDir 'api-key')) -or (Test-Path (Join-Path $cfgDir 'auth-mode'))) {
    Gruen "  [ok] Auth-Konfiguration unter $cfgDir"
} else {
    Gelb "  [!] Keine Auth-Konfiguration gefunden. Vor dem ersten Lauf:"
    Gelb "      pwsh -File `"$KIT\pwsh\scripts\team-auth-setup.ps1`""
    Gelb "      (oder gleich die ganze Maschine: pwsh -File `"$KIT\pwsh\kit-einrichten.ps1`")"
}

# ==================================================== Aufnahme-Interview
function Frage {
    param([string]$Name, [string]$Text, [string]$Vorgabe)
    $ausEnv = [Environment]::GetEnvironmentVariable("TEAM_INIT_$Name")
    if ($ausEnv) { return $ausEnv }
    if (-not $Interaktiv) { return $Vorgabe }
    $eingabe = if ($Vorgabe) { Read-Host "  $Text [$Vorgabe]" } else { Read-Host "  $Text" }
    if ($eingabe) { return $eingabe }
    return $Vorgabe
}

function Erklaerung {
    # Leerzeile davor, damit Frage und Erklaerung im Terminal nicht zu einer
    # Wand verschwimmen — wer die Frage nicht findet, liest sie nicht (BL-53).
    param([string[]]$Zeilen)
    if (-not $Interaktiv) { return }
    Write-Host ""
    foreach ($z in $Zeilen) { Write-Host "  $z" }
}

function Kandidaten-Ausserhalb {
    # Eine Liste zum Abschreiben schlaegt jede Erklaerung — die BL-52-Frage
    # wird sonst verneint, weil dem Anwender im Moment der Frage nicht
    # einfaellt, was er hat.
    param([string]$Prod, [string]$Test, [string]$Plan)
    $ignorieren = @('team', 'node_modules', '__pycache__', 'venv', '.venv', 'dist',
                    'build', 'target', 'docs', 'doku', 'data', 'assets', 'static', 'media')
    $namen = @()
    foreach ($e in (Get-ChildItem $Ziel -Force -ErrorAction SilentlyContinue)) {
        $n = $e.Name
        if ($n.StartsWith('.')) { continue }
        if ($n -in @($Prod.TrimEnd('/'), $Test.TrimEnd('/'), $Plan.TrimEnd('/'))) { continue }
        if ($n -in $ignorieren) { continue }
        if ($n -match '^(ralph|frank|harry|marv|axel|vollautomatik|halbautomatik|install)\.(sh|ps1|cmd)$') { continue }
        if ($n -match '^team[-.].*\.(sh|ps1|cmd)$') { continue }
        if ($n -match '\.(md|txt|json|toml|yaml|yml|cfg|ini|lock)$') { continue }
        if ($n -match '^(LICENSE|Makefile)') { continue }
        if ($n -match '^test_|_test\.') { continue }
        $namen += $(if ($e.PSIsContainer) { "$n/" } else { $n })
    }
    if ($namen.Count -gt 10) { return (($namen | Select-Object -First 10) -join ' ') + ' ...' }
    return ($namen -join ' ')
}

function Wurzel-Ordner {
    # Abschreibhilfe fuer den Tippfehler-Fall (BL-121). Dieselbe Erwaegung wie
    # bei Kandidaten-Ausserhalb: Eine Liste zum Abschreiben schlaegt jede
    # Erklaerung.
    $namen = @()
    foreach ($e in (Get-ChildItem -LiteralPath $Ziel -Directory -Force -ErrorAction SilentlyContinue)) {
        $n = $e.Name
        if ($n.StartsWith('.')) { continue }
        if ($n -in @('team', 'node_modules', '__pycache__', 'venv', 'dist', 'build', 'target')) { continue }
        $namen += "$n/"
    }
    if ($namen.Count -gt 12) { return (($namen | Select-Object -First 12) -join ' ') + ' ...' }
    return ($namen -join ' ')
}

function Produktivcode-Anlegen {
    # Legt den Ordner an und sichert ihn gegen den naechsten Commit ab. Ein
    # LEERER Ordner ist fuer Git nicht vorhanden — und der Schritt direkt nach
    # der Installation heisst "Committen, VOR dem ersten Guard-Lauf". Ohne
    # Platzhalter waere der Ordner nach dem naechsten Klon wieder weg und der
    # Fehler von vorn da. Dieselbe Loesung wie bei ermittlungsakten/.
    param([string]$Pfad)
    $voll = Join-Path $Ziel $Pfad.TrimEnd('/', '\')
    New-Item -ItemType Directory -Force -Path $voll | Out-Null
    if (-not (Get-ChildItem -LiteralPath $voll -Force -ErrorAction SilentlyContinue)) {
        New-Item -ItemType File -Force -Path (Join-Path $voll '.gitkeep') | Out-Null
        return $true
    }
    return $false
}

function Produktivcode-Sichern {
    <#
      Guard-Grenze, Pruefumfang und die Briefings der drei Read-Only-Rollen
      zeigen ab hier auf den Produktivcode-Ordner. Ein Name, den es nicht gibt,
      ist deshalb kein Schoenheitsfehler: Das Red Team prueft dann einen leeren
      Suchraum, und der erste Bericht meldet "sauber" ueber nichts. Vorher wurde
      der Name nur eingesetzt, nie geprueft und nie angelegt (BL-121).

      Im BESTAND ist ein nicht vorhandener Ordner eher ein Tippfehler als ein
      neues Projekt. Deshalb wird nicht wortlos angelegt, sondern erst gezeigt,
      was da ist — und angelegt wird trotzdem, wenn der Name so gewollt war.

      Rueckgabe: der (moeglicherweise korrigierte) Ordnername.
    #>
    param([string]$Pfad)
    while ($true) {
        $voll = Join-Path $Ziel $Pfad.TrimEnd('/', '\')
        if (Test-Path -LiteralPath $voll -PathType Container) {
            Gruen "  [ok] Produktivcode-Ordner $Pfad ist vorhanden."
            return $Pfad
        }
        if (-not $Interaktiv) {
            if (Produktivcode-Anlegen $Pfad) {
                Gelb "  [!] $Pfad gab es nicht — angelegt, mit .gitkeep."
            } else {
                Gelb "  [!] $Pfad gab es nicht — angelegt."
            }
            Gelb "      Nicht-interaktiv: ohne Rueckfrage, aber nicht ohne Ansage."
            return $Pfad
        }
        Gelb "  [!] Den Ordner '$Pfad' gibt es in diesem Projekt nicht."
        $vorhandene = Wurzel-Ordner
        if ($vorhandene) {
            Write-Host "      Hier liegen: $vorhandene"
            Write-Host "      Ist der gesuchte dabei, tipp ihn ab — ein Tippfehler faellt"
            Write-Host "      sonst erst auf, wenn das Red Team `"sauber`" ueber einen leeren"
            Write-Host "      Ordner meldet."
        } else {
            Write-Host "      Das Projekt ist noch leer. Bei einem neuen Projekt ist das der Normalfall."
        }
        $neu = Read-Host "      Enter = '$Pfad' anlegen, oder anderen Namen eingeben"
        if ([string]::IsNullOrWhiteSpace($neu)) {
            if (Produktivcode-Anlegen $Pfad) {
                Gruen "  [ok] $Pfad angelegt — mit .gitkeep, sonst faellt der leere Ordner"
                Gruen "       bei dem Commit weg, den der naechste Schritt verlangt."
            } else {
                Gruen "  [ok] $Pfad angelegt."
            }
            return $Pfad
        }
        $Pfad = $neu.TrimEnd('/', '\') + '/'
    }
}

Kopf "Aufnahme-Interview — neun Fragen"
if ($Interaktiv) {
    Write-Host "  Hinter jeder Frage steht in [Klammern] eine Vorgabe. Enter nimmt sie an."
    Write-Host "  Nichts davon ist endgueltig: Alle Antworten landen in team.config.sh"
    Write-Host "  und team.config.ps1 und lassen sich dort jederzeit aendern."
}

Erklaerung @("Unter welchem Namen soll das Projekt in Berichten und in der",
             "Kostenabrechnung auftauchen?")
$Projekt = Frage 'PROJEKT' 'Projektname' (Split-Path -Leaf $Ziel)

Erklaerung @("In welchem Ordner liegt dein Programmcode?",
             "Harry, Marv und Axel — die drei pruefenden Rollen — lesen ihn und",
             "suchen dort Fehler. Aendern duerfen sie ihn nie; das macht allein",
             "Frank, der Reparateur. Ein Waechter setzt das durch: Fasst eine der",
             "drei den Ordner doch an, wird die Aenderung automatisch zurueckgenommen.")
$Produktivcode = (Frage 'PRODUKTIVCODE' 'Ordner mit dem Programmcode' 'src/').TrimEnd('/', '\') + '/'
$Produktivcode = Produktivcode-Sichern $Produktivcode

Erklaerung @("Wohin duerfen die pruefenden Rollen Testdateien schreiben?",
             "Findet Harry einen Fehler, legt er hier den Test ab, der ihn zeigt.",
             "Das ist einer von zwei Ordnern, in denen die drei schreiben UND",
             "loeschen duerfen — der Waechter greift hier nicht. Dein eigener",
             "Testbefehl bleibt davon unberuehrt.")
$TestOrdner = (Frage 'TEST_ORDNER' 'Ordner fuer Tests' 'tests/').TrimEnd('/', '\') + '/'

Erklaerung @("Wohin schreiben die Rollen ihre Plaene, Berichte und Fundlisten?",
             "Der zweite Ordner mit Schreib- und Loeschrecht. Am saubersten ist ein",
             "eigener, leerer Ordner (z. B. team-plans/): Dann kommen die Rollen",
             "mit deinen vorhandenen Dokumenten gar nicht erst in Beruehrung.")
$PlanOrdner = (Frage 'PLAN_ORDNER' 'Ordner fuer Plaene und Berichte' 'plans/').TrimEnd('/', '\') + '/'

$hinweis = @("Liegt weiterer Programmcode AUSSERHALB von ${Produktivcode}?",
             "Gemeint ist Code, der beim Benutzen wirklich laeuft: der Startpunkt in",
             "der Wurzel (main.py), Build- und Deploy-Skripte (bin/, deploy/).",
             "Was hier nicht steht, sieht sich nie jemand an — der Bericht meldet",
             "dann `"sauber`" und meint bloss `"${Produktivcode} ist sauber`".",
             "NICHT eintragen: ${TestOrdner} und ${PlanOrdner}. Die hast du gerade",
             "als Schreibordner vergeben, beides zugleich geht nicht.",
             "Neues Projekt oder alles unter ${Produktivcode}: einfach Enter.")
$kandidaten = Kandidaten-Ausserhalb $Produktivcode $TestOrdner $PlanOrdner
if ($kandidaten) {
    $hinweis += @("", "Neben ${Produktivcode} liegt hier: $kandidaten",
                  "Uebernimm davon, was echter Programmcode ist.")
}
Erklaerung $hinweis
$WeitererCode = Frage 'WEITERER_CODE' 'Weiterer Code, mit Leerzeichen getrennt (leer = keiner)' ''

Erklaerung @("Gibt es EINEN Befehl, der zeigt, ob das Projekt noch heil ist?",
             "Beispiele: 'pytest -q', 'npm test'.",
             "Die Rollen rufen ihn nach jeder Aenderung auf. Schlaegt er fehl, wird",
             "die Aenderung zurueckgenommen — er ist das Sicherheitsnetz des Teams.",
             "Kennst du keinen: leer lassen. Dann ist es die erste Aufgabe des",
             "Teams, einen zu bauen, und bis dahin sagt jede Rolle offen, dass sie",
             "ohne Netz arbeitet.")
$SmokeTest = Frage 'SMOKE_TEST' 'Pruefbefehl (leer = gibt es noch nicht)' ''

Erklaerung @("Womit ist das Projekt gebaut? Eine Zeile, die den Rollen sagt,",
             "worauf sie sich einstellen muessen. Reine Beschreibung, nichts wird",
             "davon ausgefuehrt.")
$TechStack = Frage 'TECH_STACK' 'Technik in einer Zeile' 'TODO: in CLAUDE.md nachtragen'

Erklaerung @("Auf welches Konto sollen die Kosten gebucht werden?",
             "EIN Konto ist fast immer richtig: Dann landet jeder Lauf auf",
             "'produkt' und du musst nie ueberlegen, wohin er gehoert.",
             "Mehrere Konten nur, wenn du die Ausgaben wirklich getrennt sehen",
             "willst.")
$Domaenen = Frage 'DOMAENEN' 'Kostenkonten, mit Leerzeichen getrennt' 'produkt'

Erklaerung @("Der Architekt plant im Gespraech mit dir die naechste Runde und legt",
             "den Plan in ${PlanOrdner} ab. Soll er ihn selbst ins Git eintragen (j),",
             "oder dir die fertigen Befehle zum Kopieren geben (n)?")
$CommitModus = Frage 'COMMIT_MODUS' 'Architekt committet selbst? (j/n)' 'n'

# Kollision Pruefumfang/Schreibzone: Derselbe Ordner kann nicht beides sein.
# Stand er in beiden Antworten, sagte der Rollen-Prompt in EINEM Absatz "tabu"
# und "schreib hierhin".
if ($WeitererCode) {
    $bereinigt = @(); $entfernt = @()
    foreach ($e in ($WeitererCode -split '\s+' | Where-Object { $_ })) {
        if (($e.TrimEnd('/', '\') + '/') -in @($TestOrdner, $PlanOrdner)) { $entfernt += $e }
        else { $bereinigt += $e }
    }
    if ($entfernt.Count) {
        Write-Host ""
        Gelb "  [!] Wieder aus dem Pruefumfang genommen: $($entfernt -join ' ')"
        Gelb "      Das hast du eben schon als Schreibordner der Rollen vergeben."
        Gelb "      Beides zugleich ginge nicht: Ihr Auftrag wuerde `"nicht anfassen`""
        Gelb "      und `"hier ablegen`" im selben Absatz sagen."
        $WeitererCode = $bereinigt -join ' '
    }
}

# ---------------------------------------------------------------------- BL-51
function Bestand-Eintraege {
    param([string]$Ordner)
    $d = Join-Path $Ziel $Ordner.TrimEnd('/', '\')
    if (-not (Test-Path $d)) { return "" }
    $namen = @(Get-ChildItem $d -Force -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
    if ($namen.Count -gt 12) { return (($namen | Select-Object -First 12) -join ' ') + ' ...' }
    return ($namen -join ' ')
}

function Bestand-Pruefen {
    <#
      Test- und Plan-Ordner sind die Schreibzone der drei Read-Only-Rollen: Die
      Guard-Whitelist ist POSITIV, dort schlaegt er nicht an. In einem neuen
      Projekt ist das folgenlos. In einer gewachsenen Codebasis bekommen Harry,
      Marv und Axel stillschweigend Schreib- und Loeschrecht auf
      Bestandsdokumente.

      Gewarnt wird, nicht verboten: Ein bewusst geteilter Ordner kann legitim
      sein. Wer den Vorschlag annimmt, bekommt die Mechanik (eigener leerer
      Ordner); wer ihn ablehnt, bekommt den Bestand in die Konfiguration und
      damit in die Rollen-Prompts.
    #>
    param([string]$Ordner, [string]$Text, [string]$Rollen)
    while ($true) {
        $eintraege = Bestand-Eintraege $Ordner
        if (-not $eintraege) { return @($Ordner, "") }
        Gelb "  [!] Der $Text '$Ordner' ist nicht leer:"
        foreach ($e in ($eintraege -split ' ')) { Write-Host "        - $e" }
        Gelb "      Hier duerfen $Rollen schreiben und loeschen. Der Waechter, der sie"
        Gelb "      von deinem Code fernhaelt, greift in diesem Ordner NICHT (BL-51)."
        Gelb "      Deine Dateien verschwinden nicht einfach: Der Installer merkt sie"
        Gelb "      sich und nennt sie den Rollen ausdruecklich als fremdes Eigentum."
        Gelb "      Das ist aber eine Auflage an die KI, keine Sperre. Wirklich sicher"
        Gelb "      ist nur ein eigener, leerer Ordner — z. B. team-$Ordner"
        if (-not $Interaktiv) {
            Gelb "      Nicht-interaktiv: Ordner bleibt. Der Bestand wird vermerkt und"
            Gelb "      den Rollen als fremdes Eigentum genannt."
            return @($Ordner, $eintraege)
        }
        $neu = Read-Host "      Anderen, leeren Ordner nehmen? (Name, Enter = '$Ordner' behalten)"
        if (-not $neu) { return @($Ordner, $eintraege) }
        $Ordner = $neu.TrimEnd('/', '\') + '/'
    }
}

Kopf "Liegt in den Schreibordnern der Rollen schon etwas? (BL-51)"
$r = Bestand-Pruefen $PlanOrdner 'Plan-Ordner' 'Harry, Marv und Axel'
$PlanOrdner = $r[0]; $PlanBestand = $r[1]
$r = Bestand-Pruefen $TestOrdner 'Test-Ordner' 'Harry und Marv'
$TestOrdner = $r[0]; $TestBestand = $r[1]
if (-not $PlanBestand -and -not $TestBestand) {
    Gruen "  [ok] beide Ordner leer oder neu — nichts fremdes in der Schreibzone"
}

$CommitEntscheid = if ($CommitModus.ToLower() -in @('j', 'ja', 'y', 'yes')) {
    'Ich committe Plan-/Doku-Änderungen selbst (docs(plan): …).'
} else {
    'Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Strippenzieher führt sie aus.'
}

Setze-Werte $Projekt $Produktivcode $TestOrdner $PlanOrdner $SmokeTest `
            $TechStack 'TODO: in CLAUDE.md nachtragen' 'keine' `
            $Domaenen $CommitEntscheid $WeitererCode $TestBestand $PlanBestand (Python-Fuer-Config)

# ------------------------------------------------------------------ Kopieren
Kopf "A.2 — Dateien installieren"
Kopiere-Infrastruktur
$anzahlTests = @(Get-ChildItem (Join-Path $KIT 'geteilt\tests') -Filter 'test_*.py' -File).Count
Gruen "  [ok] Entrypoints (Wurzel$(if ($NurBahn) { ", nur $NurBahn" } else { ", beide Bahnen" })) + team/ (lib, tools, prompts, $anzahlTests Tests)"
if ($NurBahn) {
    $andere = if ($NurBahn -eq 'pwsh') { 'bash' } else { 'pwsh' }
    Gelb   "  [!] Nur die $NurBahn-Bahn installiert — die $andere-Bahn fehlt in"
    Write-Host "    diesem Projekt, samt ihrer Konfiguration. Das ist deine Abwahl,"
    Write-Host "    kein Versehen des Installers."
    Write-Host "    Zurueckholen (macht das Projekt wieder vollstaendig):"
    Write-Host "      pwsh -File `"$KIT\pwsh\install.ps1`" `"$Ziel`" -Update"
}

# ------------------------------------------------------------- A.0 Bootstrap
Kopf "A.0 — Bootstrap-Dateien"
Kopiere (Join-Path $KIT 'bootstrap\CLAUDE.md.vorlage') 'CLAUDE.md'
Kopiere (Join-Path $KIT 'bootstrap\TEAM.md')           'TEAM.md'
Kopiere (Join-Path $KIT 'bootstrap\CHANGELOG.md')      'CHANGELOG.md'
Kopiere (Join-Path $KIT 'bootstrap\beutebuch.md')      "${PlanOrdner}beutebuch.md"
Kopiere (Join-Path $KIT 'bootstrap\roadmap-skizzen.md') "${PlanOrdner}roadmap-skizzen.md"
Kopiere (Join-Path $KIT 'bootstrap\backlog.md')        "${PlanOrdner}backlog.md"
Schreibe "${PlanOrdner}ermittlungsakten/.gitkeep" ""
Schreibe '.budget-ledger' ""
Schreibe '.ralph-state' "1`n"
New-Item -ItemType Directory -Force -Path (Join-Path $Ziel $TestOrdner) | Out-Null
Gruen "  [ok] CLAUDE.md, CHANGELOG, Beutebuch, Roadmap, Backlog, Ledger, State"

# Platzhalter fuellen — auch in den Briefings: sie sind selbst Prompts und
# nennen sonst die Pfade des Ursprungsprojekts (falsche Guard-Grenze!).
foreach ($d in @('CLAUDE.md', 'TEAM.md', 'team.config.sh', 'team.config.ps1', 'CHANGELOG.md',
                 "${PlanOrdner}roadmap-skizzen.md", "${PlanOrdner}backlog.md",
                 "${PlanOrdner}beutebuch.md")) {
    Fuelle-Datei (Join-Path $Ziel $d)
}
foreach ($f in (Get-ChildItem (Join-Path $Ziel 'team\prompts') -Filter '*.md' -File)) {
    Fuelle-Datei $f.FullName
}

# ----------------------------------------------------------------- .gitignore
Gitignore-Abgleich ergaenzen

# ----------------------------------------------------------------- Selbsttest
Kopf "Selbsttest"
$fehler = 0
foreach ($f in (Get-ChildItem $Ziel -Filter '*.ps1' -File)) {
    $syntax = $null
    [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$syntax) | Out-Null
    if ($syntax) {
        Rot "  [x] Syntaxfehler: $($f.Name)"
        $syntax | ForEach-Object { Write-Host "      Zeile $($_.Extent.StartLineNumber): $($_.Message)" }
        $fehler = 1
    }
}
if ($fehler -eq 0) { Gruen "  [ok] Alle PowerShell-Skripte syntaktisch korrekt" }
Gelb "  [!] Die .sh-Entrypoints wurden NICHT geprueft — hier liegt keine bash."
Gelb "      Sie sind mitinstalliert und gelten unveraendert aus dem Kit."

$py = Finde-Python
if (-not $py) {
    Gelb "  [!] Python-Werkzeuge NICHT geprueft — kein Interpreter auf dieser Maschine."
    Gelb "      Das ist kein Befund ueber die Dateien, sondern das Fehlen einer Probe."
} else {
    & $py -m py_compile (Get-ChildItem (Join-Path $Ziel 'team\tools') -Filter '*.py' -File | ForEach-Object { $_.FullName }) 2>$null
    if ($LASTEXITCODE -eq 0) { Gruen "  [ok] Python-Werkzeuge kompilieren" }
    else { Rot "  [x] Python-Werkzeuge fehlerhaft"; $fehler = 1 }
}

$pt = Finde-Pytest
if ($pt) {
    Push-Location $Ziel
    try {
        $log = Join-Path ([System.IO.Path]::GetTempPath()) 'team-init-pytest.log'
        $vorab = $pt.Vorab
        & $pt.Befehl @vorab -q team/tests *> $log
        if ($LASTEXITCODE -eq 0) {
            $zeile = (Select-String -Path $log -Pattern '\d+ passed' | Select-Object -First 1)
            Gruen "  [ok] Regressionstests gruen ($($zeile.Matches[0].Value))"
        } else {
            Gelb "  [!] Regressionstests nicht vollstaendig gruen — Log: $log"
            Get-Content -Tail 3 $log | ForEach-Object { Gelb "      $_" }
        }
    } finally { Pop-Location }
} else {
    Gelb "  - pytest nicht gefunden — Regressionstests uebersprungen"
    Gelb "    Gesucht als Modul (<python> -m pytest) UND als Befehl im PATH."
}

# ------------------------------------------------------------------ Abschluss
Kopf "Fertig — $($script:Geschrieben) Dateien geschrieben, $($script:Uebersprungen) uebersprungen"
Write-Host @"

>>> Alles Weitere steht in $Ziel\TEAM.md <<<
    Bedienung, Befehle, Exit-Codes und Fehlersuche — fuer dich, nicht fuer die KI.
    Diese Terminal-Ausgabe scrollt weg; TEAM.md bleibt im Git.

Naechste Schritte im Zielprojekt:

  1. Werte pruefen:      notepad "$Ziel\team.config.ps1"
  2. Regeln pruefen:     notepad "$Ziel\CLAUDE.md"   (TODO-Stellen fuellen)
  3. Alles committen:    git -C "$Ziel" add -A; git -C "$Ziel" commit -m "chore: T.E.A.M. eingerichtet"
     ^ WICHTIG: vor dem ersten Lauf committen. Der Waechter haelt uncommittete
       Dateien fuer einen Uebergriff der Rollen und raeumt sie weg.
  4. Team-Tests:         cd "$Ziel"; .\team-test.cmd
  5. Erste Kaskade planen — Sitzung im Projektordner, starke Stufe (Default Opus):
       "Du bist unser Architekt, lies team/prompts/rolle-architekt.md."
  6. Lauf starten:       cd "$Ziel"; `$env:TEAM_BUDGET_USD='15'; .\vollautomatik.cmd
     ^ Deckel fuer DIESEN Lauf. Lieber nachziehen als zu tief ansetzen: ein zu
       tiefer Deckel wirft bezahlte Arbeit per Rollback weg und vervielfacht
       die Kosten, statt zu sparen (Feld-Lehre HM-32).
  7. NACH dem Lauf — Closeout, sonst sind die Kosten blind:
       .\team-status.cmd --rollen-abschluss <N> <domaene>
       .\team-status.cmd --architekt-abschluss <USD> <domaene> "Kaskade N geplant"
"@
if (-not $SmokeTest) {
    Write-Host ""
    Gelb "Hinweis: Kein Smoke-Test konfiguriert. Die Rollen laufen, aber ohne"
    Gelb "Verifikationsschritt — sie melden das in jedem Prompt."
    Gelb ""
    Gelb "In ${PlanOrdner}roadmap-skizzen.md liegt dafuer bereits 'Skizze 1:"
    Gelb "Verifikationsfaehigkeit herstellen'. Der Architekt haertet sie als erste"
    Gelb "Kaskade aus. Danach den Befehl bei TEAM_SMOKE_TEST eintragen."
}
exit $fehler

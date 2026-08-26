# Bahn: pwsh | Gegenstueck: kit-test.sh
<#
  kit-test.ps1 — Selbstverifikation des Kits auf einer WINDOWS-Maschine.

  WAS DAS HIER IST UND WAS NICHT
    kit-test.sh ist die vollstaendige Selbstverifikation; ihr Schritt 10/10
    beweist sogar, dass beide Installer byte-identische Baeume erzeugen. Nur:
    Sie braucht bash, und auf einer Windows-Maschine ohne WSL gibt es keine.
    Ein Anwender dort haette also GAR KEINE Moeglichkeit, seine Installation zu
    pruefen — und "ungeprueft" ist der Zustand, aus dem im Feld die teuren
    Fehler kommen.

    Dieses Skript schliesst genau diese Luecke. Es ist KEIN Ersatz fuer
    kit-test.sh und behauptet das auch nicht: Was es nicht pruefen kann, sagt
    es am Ende ausdruecklich. Ein uebersprungener Nachweis, den niemand sieht,
    liest sich sonst wie ein bestandener.

  Aufruf:  pwsh -File .\kit-test.ps1

  DAS ERFOLGSKRITERIUM IST DER EXIT-CODE, NICHT DIE SCHLUSSZEILE.
    pwsh -File .\kit-test.ps1; if ($LASTEXITCODE -eq 0) { "BEREIT" }
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
# BL-122: Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
# standardmaessig $true — ein Exit-Code != 0 aus einem NATIVEN Befehl ist damit
# ein TERMINIERENDER Fehler und nicht mehr nur ein Wert in $LASTEXITCODE. Diese
# Bahn ist durchgehend fuer den klassischen Vertrag geschrieben: aufrufen,
# $LASTEXITCODE lesen, entscheiden. Ohne diese Zeile ist jede dieser
# Entscheidungen unerreichbar — der Abbruch kommt vorher.
$PSNativeCommandUseErrorActionPreference = $false
# BL-135, Empfaengerseite. Dieses Skript FAENGT die Ausgabe fremder Prozesse
# auf — den Installer, pytest, und in Schritt 6 einen kompletten
# Vollautomatik-Lauf — und vergleicht sie anschliessend mit Mustern, in denen
# Umlaute und Geviertstriche stehen. PowerShell dekodiert die Ausgabe nativer
# Prozesse mit [Console]::OutputEncoding, und das ist unter Windows die
# OEM-Codepage der Konsole.
#
# Die Rollen schreiben seit BL-135 ausdruecklich UTF-8 (lib.psm1). Als cp850
# gelesen wird daraus "├╝ber RALPH_CAP" statt "über RALPH_CAP" — und die
# Pruefung faellt, obwohl der Lauf richtig war. Genau so ist dieser Schritt
# beim fuenften Anlauf rot geworden, nachdem die Schreibseite gefixt war:
# Eine Leitung hat zwei Enden, und beide muessen dieselbe Kodierung sprechen.
#
# lib.psm1 setzt dieselbe Zeile fuer alle Entrypoints; die erben es damit vom
# Import. Dieses Skript importiert die Bibliothek NICHT (es prueft sie), also
# steht sie hier eigens.
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
# Seit der Bahn-Trennung: BAHN ist <kit>\pwsh, KIT die Wurzel des Kits.
$BAHN = Split-Path -Parent $PSCommandPath
$KIT  = Split-Path -Parent $BAHN

function Kopf($t) { Write-Host ''; Write-Host $t -ForegroundColor White }
function Gruen($t) { Write-Host "  [ok] $t" -ForegroundColor Green }
function Rot($t) { Write-Host "  [x]  $t" -ForegroundColor Red }
function Gelb($t) { Write-Host "  [!]  $t" -ForegroundColor Yellow }
function Zeile($t) { Write-Host "       $t" }

$script:Fehler = 0

# EIN LAUF, DER ABSTUERZT, DARF NICHT GRUEN MELDEN.
# Beim ersten Bau dieses Skripts ist genau das passiert: Schritt 6 warf eine
# MethodInvocationException, die uebrigen Pruefungen liefen nie — und die
# Schlusszeile sagte "Selbstverifikation gruen". Ein Selbsttest, der einen
# Absturz ueberlebt und bestehen meldet, ist schaedlicher als gar keiner: Er
# erzeugt Vertrauen, das er nicht deckt. Der Trap faengt alles, was durch die
# try/catch der einzelnen Schritte rutscht.
trap {
    Rot "UNBEHANDELTER FEHLER: $($_.Exception.Message)"
    Zeile "  bei $($_.InvocationInfo.ScriptName):$($_.InvocationInfo.ScriptLineNumber)"
    $script:Fehler = 1
    continue
}

$script:Gepruefte = 0
function Pruefe {
    param([string]$Was, $Ist, $Soll)
    $script:Gepruefte++
    if ("$Ist" -eq "$Soll") { Gruen $Was }
    else { Rot "$Was — erwartet '$Soll', ist '$Ist'"; $script:Fehler = 1 }
}

# ---------------------------------------------- Gemeinsame Handgriffe (BL-145)
function Neues-WegwerfRepo {
    <#
      Ein frisches Projekt-Repo, wie `wegwerf_repo` in kit-test.sh. Bis BL-145
      brauchte dieses Skript nur EINES; seit Schritt 7 die Bahn-Abwahl prueft,
      sind es drei.
    #>
    param([string]$Pfad, [string]$Produktivcode = 'src')
    New-Item -ItemType Directory -Force -Path $Pfad | Out-Null
    Push-Location $Pfad
    try {
        & git init -q . 2>&1 | Out-Null
        & git config user.email 'test@team-kit.local' | Out-Null
        & git config user.name 'Kit-Test' | Out-Null
        New-Item -ItemType Directory -Force -Path $Produktivcode | Out-Null
        Set-Content -Path (Join-Path $Produktivcode 'app.py') -Value 'x = 1' -Encoding utf8
        & git add -A | Out-Null
        & git commit -q -m 'start' | Out-Null
    } finally { Pop-Location }
}

function Git-Zwischenstand {
    param([string]$Pfad, [string]$Botschaft)
    & git -C $Pfad add -A 2>&1 | Out-Null
    & git -C $Pfad commit -q -m $Botschaft 2>&1 | Out-Null
}

function Suite-Mitschnitt {
    <#
      Gegenstueck zu `suite_mitschnitt` in kit-test.sh: roh ins Log,
      eingerueckt auf den Bildschirm — gleichzeitig (BL-179/BL-176). Ein
      stummer Lauf ist von einem HAENGENDEN nicht zu unterscheiden, und dieser
      Lauf steht rund 14 Minuten still.

      Rueckgabe: der Exit-Code von pytest.
    #>
    param([string]$Arbeitsordner, [string]$Log, [string]$Befehl, [string[]]$Vorab)
    Push-Location $Arbeitsordner
    $gemerkt = $env:PYTHONUNBUFFERED
    $env:PYTHONUNBUFFERED = '1'
    try {
        & $Befehl @Vorab -q team/tests 2>&1 |
            Tee-Object -FilePath $Log |
            ForEach-Object { Zeile $_ }
        return $LASTEXITCODE
    } finally {
        if ($null -eq $gemerkt) {
            Remove-Item Env:PYTHONUNBUFFERED -ErrorAction SilentlyContinue
        } else { $env:PYTHONUNBUFFERED = $gemerkt }
        Pop-Location
    }
}

function Treffer {
    <#
      Wie oft ein Muster in einer Datei vorkommt — das pwsh-Gegenstueck zu
      `grep -c`. Fehlt die Datei, ist die Antwort 0 und nicht ein Abbruch:
      Eine fehlende Datei ist ein Befund, den die Pruefung selbst melden soll.
    #>
    param([string]$Datei, [string]$Muster)
    if (-not (Test-Path -LiteralPath $Datei)) { return 0 }
    $text = Get-Content -Raw -LiteralPath $Datei -ErrorAction SilentlyContinue
    if (-not $text) { return 0 }
    return ([regex]::Matches($text, $Muster)).Count
}

function Dateien-Mit-Endung {
    param([string]$Ordner, [string[]]$Endungen)
    if (-not (Test-Path -LiteralPath $Ordner)) { return 0 }
    return @(Get-ChildItem -LiteralPath $Ordner -File -ErrorAction SilentlyContinue |
             Where-Object { $Endungen -contains $_.Extension }).Count
}

# Wie viele Einzelpruefungen ein vollstaendiger Lauf fahren MUSS. Die Zahl ist
# die zweite Haelfte des Absturzschutzes: Ein Schritt, der stillschweigend
# uebersprungen wird, aendert die Zahl — und ein Selbsttest, der weniger
# geprueft hat als er soll, hat nicht bestanden, sondern nur nichts gemerkt.
$script:PruefungenSoll = 58

# BL-195: Die Installer- und Update-Aufrufe ab Schritt 5 laufen mit
# -OhneSelbsttest. Der Installer wuerde sonst jedes Mal die volle Suite
# mitfahren — und jeder Durchgang dauert in der Installation rund 19 Minuten.
#
# NICHT der erste Aufruf in Schritt 2: Dort haelt BL-127 fest, dass der
# Selbsttest des INSTALLERS seine Regressionstests wirklich faehrt. Diese
# Zusicherung darf ein Laufzeit-Schalter nicht aushebeln, und sie wird gleich
# darunter geprueft.
#
# Geprueft wird die Suite ausserdem dreimal AUSDRUECKLICH: Schritt 4
# (Auslieferungswerte), Schritt 5 (angepasste Konfiguration), Schritt 7
# (einbahnige Ablage). Was hier entfaellt, ist die Wiederholung — nicht die
# Zusicherung. Die Zahl der wirklich gefahrenen Durchgaenge steht am Ende
# neben PruefungenSoll; sie ist dieselbe Sorte Absturzschutz.
$script:SuiteLaeufe = 0

Write-Host '=== T.E.A.M.-Starterkit — Selbstverifikation (Windows) ===' -ForegroundColor White
Write-Host "  Kit: $KIT"

# --------------------------------------------------------- 1/8 Wegwerf-Repo
Kopf '1/8 — Wegwerf-Repo anlegen'
$basis = Join-Path ([System.IO.Path]::GetTempPath()) ("team-kit-test-" + [guid]::NewGuid())
# Gleicher Basename wie in kit-test.sh: Der Projektname leitet sich aus dem
# Ordner ab und taucht in Briefings und Ledger-Notizen auf.
$ziel = Join-Path $basis 'projekt'
New-Item -ItemType Directory -Force -Path $ziel | Out-Null
Push-Location $ziel
try {
    & git init -q . 2>&1 | Out-Null
    & git config user.email 'test@team-kit.local' | Out-Null
    & git config user.name 'Kit-Test' | Out-Null
    New-Item -ItemType Directory -Force -Path 'src' | Out-Null
    Set-Content -Path 'src/app.py' -Value "x = 1" -Encoding utf8
    & git add -A | Out-Null
    & git commit -q -m 'start' | Out-Null
    Gruen "Wegwerf-Repo unter $ziel"
} finally { Pop-Location }

# ------------------------------------------------------ 2/8 Kit installieren
Kopf '2/8 — Kit installieren (install.ps1, nicht-interaktiv)'
$installLog = Join-Path $basis 'install.log'
& (Join-Path $KIT 'pwsh\install.ps1') $ziel -NichtInteraktiv *> $installLog
if ($LASTEXITCODE -ne 0) {
    Rot 'install.ps1 schlug fehl:'
    Get-Content -Tail 20 $installLog | ForEach-Object { Zeile $_ }
    exit 1
}
$fertig = (Select-String -Path $installLog -Pattern 'Fertig — \d+ Dateien geschrieben' |
           Select-Object -First 1)
Gruen $(if ($fertig) { $fertig.Matches[0].Value } else { 'installiert' })
# BL-127, auf dieser Bahn bis BL-195 nicht geprueft: Der Selbsttest des
# INSTALLERS muss seine Regressionstests wirklich gefahren haben. Ein
# Installer, der sie still ueberspringt, meldet trotzdem "Fertig" — und der
# Anwender haelt eine ungeprueftte Installation fuer geprueft.
#
# Genau deshalb laeuft dieser eine Aufruf OHNE -OhneSelbsttest (BL-195).
$script:SuiteLaeufe++
Pruefe 'der Installer hat seine Regressionstests wirklich gefahren (BL-127)' `
    ((Treffer $installLog 'Regressionstests gruen') -ge 1) $true

# ------------------------------------------------- 3/8 Ungefuellte Platzhalter
Kopf '3/8 — Ungefüllte Platzhalter suchen'
# Ein uebrig gebliebenes {{...}} heisst: Der Installer kennt die Datei nicht
# oder der Platzhalter wurde umbenannt. Beides faellt sonst erst im Feld auf,
# wo die Briefings die Pfade des Ursprungsprojekts nennen wuerden — falsche
# Guard-Grenze. Geprueft werden BEIDE Konfigurationen: Ein {{PYTHON}}, das nur
# in team.config.ps1 steht, faellt einem bash-Lauf nie auf.
# __pycache__ ausgenommen — dieselbe Begruendung wie in kit-test.sh, und sie
# hat der pwsh-Bahn bis BL-145 GEFEHLT: Der Compiler faltet benachbarte
# String-Literale zu einer Konstanten zusammen, so dass ein Test, der die Marke
# bewusst ZERLEGT schreibt, im .pyc trotzdem wieder als Fund erscheint. Der
# Bytecode entsteht hier schon vor diesem Schritt, weil install.ps1 seinen
# eigenen Regressionslauf faehrt. Die Zusicherung betrifft den Quelltext.
$reste = @(Get-ChildItem -Path $ziel -Recurse -File -ErrorAction SilentlyContinue |
           Where-Object { $_.FullName -notmatch '[\\/]\.git[\\/]' } |
           Where-Object { $_.FullName -notmatch '[\\/]__pycache__[\\/]' } |
           Where-Object {
               try { (Get-Content -Raw -LiteralPath $_.FullName -ErrorAction Stop) -match '\{\{[A-Z_]+\}\}' }
               catch { $false }
           })
if ($reste.Count) {
    Rot 'Ungefüllte Platzhalter in:'
    foreach ($f in $reste) { Zeile $f.FullName }
    exit 1
}
Gruen 'keine'

# ------------------------------------------------------ 4/8 Regressionstests
Kopf '4/8 — Regressionstests in der Installation'
Push-Location $ziel
try {
    # Vor dem Testlauf committen — dieselbe Reihenfolge, die TEAM.md dem
    # Anwender vorschreibt. Ein Test, der den Git-Zustand liest, sieht damit
    # den echten.
    & git add -A | Out-Null
    & git commit -q -m 'chore: T.E.A.M. eingerichtet' | Out-Null
    # BL-124: Modulaufruf bevorzugt — siehe team-test.ps1.
    $ptBefehl = $null
    foreach ($k in @('python', 'python3', 'py')) {
        if (-not (Get-Command $k -ErrorAction SilentlyContinue)) { continue }
        try { & $k -m pytest --version 2>$null | Out-Null } catch { continue }
        if ($LASTEXITCODE -eq 0) { $ptBefehl = $k; break }
    }
    if ($ptBefehl -or (Get-Command pytest -ErrorAction SilentlyContinue)) {
        $log = Join-Path $basis 'pytest.log'
        # BL-179, Bauart aus BL-176: roh ins Log, eingerueckt auf den
        # Bildschirm — gleichzeitig. Vorher ging alles nur ins Log, und dieser
        # Lauf steht rund 14 Minuten still. Ein stummer Lauf ist von einem
        # HAENGENDEN nicht zu unterscheiden; genau diese Frage hat BL-176
        # ausgeloest. Dort ist sie nur fuer die INSTALLER beantwortet worden —
        # der Selbsttest selbst blieb uebrig, und er ist der laengste Lauf,
        # den das Kit kennt.
        #
        # PYTHONUNBUFFERED, weil Python in eine Pipe blockweise puffert: Ohne
        # das kaemen die Fortschrittszeilen erst am Schluss und der Haenger
        # waere nur kuerzer geworden, nicht weg. Das Log bleibt ROH — die
        # Einrueckung entsteht erst danach fuer den Bildschirm, damit die
        # Select-String-Auswertung darunter unveraendert liest. Ein lokales
        # $ErrorActionPreference braucht es hier nicht: Diese Datei steht seit
        # BL-122 ohnehin auf 'Continue' (Zeile 26).
        $befehl = if ($ptBefehl) { $ptBefehl } else { 'pytest' }
        $vorab  = if ($ptBefehl) { @('-m', 'pytest') } else { @() }
        $script:SuiteLaeufe++
        $gemerktPuffer = $env:PYTHONUNBUFFERED
        $env:PYTHONUNBUFFERED = '1'
        try {
            & $befehl @vorab -q team/tests 2>&1 |
                Tee-Object -FilePath $log |
                ForEach-Object { Zeile $_ }
            $rc = $LASTEXITCODE
        } finally {
            if ($null -eq $gemerktPuffer) {
                Remove-Item Env:PYTHONUNBUFFERED -ErrorAction SilentlyContinue
            } else { $env:PYTHONUNBUFFERED = $gemerktPuffer }
        }
        $zeile = (Select-String -Path $log -Pattern '\d+ passed' | Select-Object -First 1)
        if ($rc -eq 0) { Gruen "grün ($($zeile.Matches[0].Value))" }
        else {
            Rot "NICHT grün — Log: $log"
            Get-Content -Tail 5 $log | ForEach-Object { Zeile $_ }
            $script:Fehler = 1
        }
    } else {
        Gelb 'pytest fehlt — Regressionstests UNGEPRÜFT.'
        Zeile 'Das ist die halbe Zusicherung dieses Schritts. Nachholen:'
        Zeile '  python -m pip install pytest'
        $script:Fehler = 1
    }
} finally { Pop-Location }

# ------------------------- 5/8 Suite unter angepasster Konfiguration (BL-58)
Kopf '5/8 — Regressionstests unter angepasster Konfiguration (BL-58)'
# BL-145: Dieser Schritt fehlte der pwsh-Bahn ganz. Er faengt eine Fehlerklasse,
# die in einer FRISCHEN Installation nie auffaellt: einen Test, der den
# PROJEKTWERT misst und dabei behauptet, eine Zusicherung des KITS zu pruefen.
# Solange die Konfiguration auf den Auslieferungswerten steht, sind beide
# dasselbe — und der Test ist gruen aus dem falschen Grund.
#
# Angefasst werden BEIDE Konfigurationen. Ein Wert, der nur in team.config.sh
# angehoben wird, laesst die pwsh-Bahn auf dem Auslieferungsstand: Die Suite
# faehrt dann teils gegen alte, teils gegen neue Werte, und ein Fehlschlag
# waere nicht mehr zuzuordnen.
$paare = @(
    @{ Sh = 'TEAM_ROLE_BUDGET_USD';  ShNeu = '10';              Ps = 'TEAM_ROLE_BUDGET_USD';  PsNeu = '10' },
    @{ Sh = 'TEAM_ROLE_HARDCAP_USD'; ShNeu = '20';              Ps = 'TEAM_ROLE_HARDCAP_USD'; PsNeu = '20' },
    @{ Sh = 'TEAM_FIX_PRAEFIX';      ShNeu = 'fix(qa)';         Ps = 'TEAM_FIX_PRAEFIX';      PsNeu = 'fix(qa)' },
    @{ Sh = 'TEAM_FEAT_PRAEFIX';     ShNeu = 'feature';         Ps = 'TEAM_FEAT_PRAEFIX';     PsNeu = 'feature' },
    @{ Sh = 'TEAM_DOMAENEN';         ShNeu = 'backend frontend'; Ps = 'TEAM_DOMAENEN';        PsNeu = 'backend frontend' }
)
$confShPfad = Join-Path $ziel 'team.config.sh'
$confPsPfad = Join-Path $ziel 'team.config.ps1'
# ZEILENWEISE ersetzt, nicht ueber [regex]::Replace. Grund: Die neuen Werte
# enthalten `${NAME:-wert}` und `$NAME` — und im ERSATZTEXT von .NET ist `$`
# ein Steuerzeichen (`${name}` ist dort eine Gruppenreferenz). Eine Ersetzung,
# die daran stillschweigend etwas anderes einsetzt, waere genau die Bauart,
# gegen die die Kontrolle unten geschrieben ist: Sie liefe auf eine
# Konfiguration hinaus, die anders aussieht als gemeint.
$confShZeilen = [System.IO.File]::ReadAllLines($confShPfad)
$confPsZeilen = [System.IO.File]::ReadAllLines($confPsPfad)
foreach ($p in $paare) {
    for ($i = 0; $i -lt $confShZeilen.Count; $i++) {
        if ($confShZeilen[$i].StartsWith("$($p.Sh)=")) {
            $confShZeilen[$i] = '{0}="${{{0}:-{1}}}"' -f $p.Sh, $p.ShNeu
        }
    }
    for ($i = 0; $i -lt $confPsZeilen.Count; $i++) {
        if ($confPsZeilen[$i] -match "^\`$$([regex]::Escape($p.Ps))\s*=") {
            $confPsZeilen[$i] = "`$$($p.Ps) = Team-Wert '$($p.Ps)' '$($p.PsNeu)'"
        }
    }
}
$confSh = ($confShZeilen -join "`n") + "`n"
$confPs = ($confPsZeilen -join "`n") + "`n"
# .sh OHNE BOM, .ps1 MIT — das ist NICHT dieselbe Zeile (BL-113/BL-134). Die
# Verwechslung hat diesen Selbsttest schon einmal seinen eigenen roten Test
# bauen lassen; die Begruendung steht ausfuehrlich in Schritt 6.
[System.IO.File]::WriteAllText($confShPfad, $confSh,
    (New-Object System.Text.UTF8Encoding($false)))
[System.IO.File]::WriteAllText($confPsPfad, $confPs,
    (New-Object System.Text.UTF8Encoding($true)))

# Eine Ersetzung, die nichts trifft, meldet sich nicht — die Suite liefe dann
# gegen die unveraenderte Konfiguration und waere gruen, ohne irgendetwas
# geprueft zu haben. Das waere dieselbe Bauart wie der Fund selbst, nur eine
# Etage hoeher.
$fehltWas = @()
foreach ($p in $paare) {
    if ((Treffer $confShPfad ([regex]::Escape("$($p.Sh):-$($p.ShNeu)"))) -lt 1) {
        $fehltWas += "team.config.sh: $($p.Sh)"
    }
    $sollZeile = "`$$($p.Ps) = Team-Wert '$($p.Ps)' '$($p.PsNeu)'"
    if ((Treffer $confPsPfad ([regex]::Escape($sollZeile))) -lt 1) {
        $fehltWas += "team.config.ps1: $($p.Ps)"
    }
}
if ($fehltWas.Count) {
    Rot 'Die Anpassung hat nicht gegriffen:'
    foreach ($f in $fehltWas) { Zeile $f }
    Zeile 'Variable umbenannt oder Zeile umgebaut? Dann prueft dieser Schritt nichts mehr.'
    exit 1
}
Gruen 'Caps 10/20, Präfixe fix(qa)/feature, zwei Domänen — in BEIDEN Konfigurationen'

if ($ptBefehl -or (Get-Command pytest -ErrorAction SilentlyContinue)) {
    Git-Zwischenstand $ziel 'chore: angepasste Konfiguration'
    $logAngepasst = Join-Path $basis 'pytest-angepasst.log'
    $script:SuiteLaeufe++
    $rc = Suite-Mitschnitt $ziel $logAngepasst `
            $(if ($ptBefehl) { $ptBefehl } else { 'pytest' }) `
            $(if ($ptBefehl) { @('-m', 'pytest') } else { @() })
    Pruefe 'Suite bleibt grün unter angepasster Konfiguration (BL-58)' $rc 0
    if ($rc -ne 0) {
        Zeile 'Das ist der BL-58-Fall: Der fehlgeschlagene Test misst den PROJEKTWERT,'
        Zeile 'behauptet aber, eine Zusicherung des KITS zu pruefen. Die Zusicherung ist'
        Zeile 'meist richtig, die Messstelle falsch — Vorbild fuer den Umbau ist'
        Zeile '_lib_default() in team/tests/test_hm32_budget_zwei_schwellen.py: Es liest'
        Zeile 'die Zeile NAME="${NAME:-wert}" statisch aus team/lib.sh, statt zu sourcen.'
        Get-Content -Tail 15 $logAngepasst | ForEach-Object { Zeile $_ }
    }
} else {
    Gelb 'pytest fehlt — der angepasste Lauf ist UNGEPRÜFT.'
    $script:Fehler = 1
}

# ----------------------------------------------- 6/8 Update schuetzt Projektdaten
Kopf '6/8 — Update-Pfad schützt Projektdaten'
# Dieselbe Praeparation wie in kit-test.sh: Ein Update darf Kostenhistorie,
# Kaskadenstand, Beutebuch und den von Hand gesetzten Smoke-Test NICHT
# anfassen. Empirisch nachgestellt (BL-8) — mit --force tut es genau das.
Push-Location $ziel
try {
    Add-Content -Path '.budget-ledger' -Value '2026-08-01 | 1 | 9.4204 | abo | produkt | roles | Lauf' -Encoding utf8
    Add-Content -Path 'plans/beutebuch.md' -Value '### HM-1 — echter Fund' -Encoding utf8
    Set-Content -Path '.ralph-state' -Value '5' -Encoding ascii
    # Der Smoke-Test in BEIDEN Konfigurationen — er ist der Wert, an dem BL-8
    # im Feld aufgefallen ist.
    $confSh = (Get-Content -Raw 'team.config.sh') -replace '(?m)^TEAM_SMOKE_TEST=.*$',
              'TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-./smoke.sh}"'
    [System.IO.File]::WriteAllText((Join-Path $ziel 'team.config.sh'), $confSh,
        (New-Object System.Text.UTF8Encoding($false)))
    $confPs = (Get-Content -Raw 'team.config.ps1') -replace "(?m)^\`$TEAM_SMOKE_TEST = .*$",
              "`$TEAM_SMOKE_TEST = Team-Wert 'TEAM_SMOKE_TEST' './smoke.ps1'"
    # BL-134: MIT BOM — und das ist nicht dieselbe Zeile wie zwei hoeher.
    #
    # Die Zeile darueber schreibt eine .sh und muss BOM-los sein; diese hier
    # schreibt PowerShell-Quelltext und muss ein BOM tragen (BL-113,
    # .gitattributes). Kopiert wurde trotzdem die obere. Die Folge: Der
    # Selbsttest praeparierte sich seinen eigenen roten Test — Schritt 5 fuhr
    # `install.ps1 -Update`, dessen Regressionslauf meldete
    # `test_powershell_quelltext_traegt_bom` als Fehlschlag, und kit-test.ps1
    # brach mit "install.ps1 -Update schlug fehl" ab. Der Installer hatte
    # nichts falsch gemacht; die Vorbereitung hatte die Datei kaputtgemacht.
    #
    # Ein Selbsttest, der seinen eigenen Befund erzeugt, ist die teuerste
    # Bauart: Er kostet die volle Laufzeit und zeigt auf die falsche Stelle.
    # Und die Regel, die er verletzte, ist keine Formsache — Windows
    # PowerShell 5.1 liest eine .ps1 ohne BOM in der ANSI-Codepage, und jeder
    # Geviertstrich darin schliesst dann seine Zeichenkette mitten im Satz.
    [System.IO.File]::WriteAllText((Join-Path $ziel 'team.config.ps1'), $confPs,
        (New-Object System.Text.UTF8Encoding($true)))
    # Ein Test, den das Kit nicht kennt — wie ihn ein Projekt schreibt, das
    # eine Luecke im Team selbst schliesst, bevor der Fund im Kit ankommt.
    Set-Content -Path 'team/tests/test_projekteigener_fund.py' `
        -Value "def test_projekteigener_fund():`n    assert True" -Encoding utf8
    # BL-178: Eine eigene Regel in CLAUDE.md — so, wie ein gelebtes Projekt
    # sie hat. Sie ist zugleich der Pruefkoerper fuer den Abgleich-Block: Das
    # Update fasst CLAUDE.md zu Recht nicht an (sie traegt Projektarbeit), muss
    # die Abweichung von der Kit-Fassung aber MELDEN. Ohne diese Zeile waere
    # die installierte Datei identisch mit der frisch gerenderten, der Block
    # meldete "nichts offen", und die Erkennung bliebe ungeprueft.
    Add-Content -Path 'CLAUDE.md' -Value 'Eigene Projektregel dieses Projekts.' -Encoding utf8
    # BL-145, die drei Praeparationen, die dieser Bahn gefehlt haben.
    #
    # (a) Eine lokal veraenderte Infrastruktur-Datei — der Fall, in dem ein noch
    #     nicht zurueckgemeldeter Fix vom Update ueberschrieben wird (BL-12).
    Add-Content -Path 'team/tools/beutebuch.py' `
        -Value "`n# lokaler Fix, noch nicht ans Kit gemeldet" -Encoding utf8
    # (b) Ein .gitignore auf dem Fragmentstand eines aelteren Kits (BL-109) —
    #     genau die Lage jedes Projekts, das frueh installiert und seither nur
    #     -Update gefahren hat. Der Block ist da, zwei Zeilen fehlen.
    $gi = (Get-Content '.gitignore') |
          Where-Object { $_ -notmatch '^\.team-focus-(harry|marv)$' }
    Set-Content -Path '.gitignore' -Value $gi -Encoding utf8
    # (c) Dasselbe fuer die .gitattributes (BL-136). DIES ist der Fall, an dem
    #     BL-136 zerbrach — und den dieses Skript bis BL-145 nicht kannte.
    $ga = (Get-Content '.gitattributes') |
          Where-Object { $_ -notmatch '^\*\.(psm1|bat)\s' }
    Set-Content -Path '.gitattributes' -Value $ga -Encoding utf8
    & git add -A | Out-Null
    & git commit -q -m 'projektstand' | Out-Null
} finally { Pop-Location }

$updateLog = Join-Path $basis 'update.log'
& (Join-Path $KIT 'pwsh\install.ps1') $ziel -Update -OhneSelbsttest *> $updateLog
if ($LASTEXITCODE -ne 0) {
    Rot 'install.ps1 -Update schlug fehl:'
    Get-Content -Tail 20 $updateLog | ForEach-Object { Zeile $_ }
    exit 1
}

Push-Location $ziel
try {
    Pruefe 'Ledger-Zeile überlebt' `
        (@(Get-Content '.budget-ledger' | Where-Object { $_ -match '9\.4204' }).Count) 1
    Pruefe 'Beutebuch-Fund überlebt' `
        (@(Get-Content 'plans/beutebuch.md' | Where-Object { $_ -match 'HM-1 — echter Fund' }).Count) 1
    Pruefe 'Kaskadenstand überlebt' ((Get-Content -Raw '.ralph-state').Trim()) '5'
    Pruefe 'Smoke-Test in team.config.sh überlebt' `
        (@(Get-Content 'team.config.sh' | Where-Object { $_ -match 'smoke\.sh' }).Count -gt 0) $true
    Pruefe 'Smoke-Test in team.config.ps1 überlebt' `
        (@(Get-Content 'team.config.ps1' | Where-Object { $_ -match 'smoke\.ps1' }).Count -gt 0) $true
    Pruefe 'projekteigener Test bleibt erhalten' `
        (Test-Path 'team/tests/test_projekteigener_fund.py') $true
    # Die Gegenprobe: Die INFRASTRUKTUR muss sich sehr wohl erneuert haben.
    Pruefe 'PowerShell-Kern ist installiert' (Test-Path 'team/lib.psm1') $true
    Pruefe 'Sweep-Logik ist installiert' (Test-Path 'team/redteam.ps1') $true
    # BL-178: Der Abgleich-Block, den es bis 2026-08-26 nur in install.sh gab.
    # Er ist die einzige Stelle, an der ein Projekt erfaehrt, dass ihm REGELN
    # aus einer neueren Kit-Fassung fehlen — die Mechanik wird aktualisiert,
    # die Regeln nicht (die Haelfte von BL-4). Geprueft wird beides: dass der
    # Block laeuft UND dass er die praeparierte Abweichung findet. Ein Block,
    # der nur "nichts offen" sagen kann, waere von einem fehlenden nicht zu
    # unterscheiden.
    $abgleichLog = Get-Content -Raw $updateLog
    Pruefe 'Abgleich-Block laeuft (BL-178)' `
        ($abgleichLog -match 'Bitte von Hand abgleichen') $true
    Pruefe 'Abgleich meldet die eigene Projektregel' `
        ($abgleichLog -match 'CLAUDE\.md weicht von der Kit-Fassung ab') $true
    Pruefe 'Abgleich ordnet die Abweichung ein' `
        ($abgleichLog -match 'CLAUDE\.md ist eine Abweichung normal') $true
    # TEAM.md wird seit BL-175 im Update mitgerendert und muss deshalb GLEICH
    # sein. Die Zeile ist die Gegenrichtung: Ein Abgleich, der alles meldet,
    # ist so wertlos wie einer, der nichts meldet (BL-14).
    Pruefe 'Abgleich meldet TEAM.md NICHT' `
        ($abgleichLog -match 'TEAM\.md weicht von der Kit-Fassung ab') $false

    # --- BL-145: der Umfang, den die bash-Fassung seit Langem hat -----------
    # Die Zusicherungen unten haben in dieser Bahn GEFEHLT. Genau darum ging es
    # bei BL-136/BL-144: Der Fix zu BL-136 galt als "kit-test.ps1 alle Schritte
    # gruen" nachgewiesen — nur prueft dieses Skript den Fall gar nicht, an dem
    # er zerbrach. "Gruen" bedeutete auf den beiden Bahnen verschieden viel,
    # und niemand sah das beim Lesen.
    Pruefe 'angehobener Hard-Cap überlebt das Update' `
        (Treffer 'team.config.sh' 'TEAM_ROLE_HARDCAP_USD:-20') 1
    Pruefe 'auch in der pwsh-Konfiguration' `
        (Treffer 'team.config.ps1' "TEAM_ROLE_HARDCAP_USD' '20'") 1
    # BL-12: Ein Testfile, das das Kit nicht kennt, kann ein projekteigener
    # Infrastruktur-Test sein — im Feld hat ein pauschales Loeschen genau so
    # einen entfernt. Es bleibt liegen UND wird gemeldet.
    Pruefe 'projekteigener Test wird als unbekannt gemeldet' `
        (Treffer $updateLog 'test_projekteigener_fund\.py') 1
    Pruefe 'lokal abweichende Infrastruktur wird gemeldet' `
        ($abgleichLog -match 'bitte gegenlesen') $true
    Pruefe 'keine offenen Platzhalter in den Briefings' `
        (@(Get-ChildItem (Join-Path $ziel 'team\prompts') -File -ErrorAction SilentlyContinue |
           Where-Object { (Get-Content -Raw $_.FullName) -match '\{\{[A-Z_]+\}\}' }).Count) 0

    # --- BL-109: der zurueckgebliebene .gitignore-Block ---------------------
    # "Der Block ist da" heisst NICHT "der Block ist vollstaendig". Der stille
    # Fall ist der teure: Das Update meldete Erfolg und liess das Projekt auf
    # dem Fragmentstand seines Installationstages zurueck.
    Pruefe 'veraltetes .gitignore wird gemeldet' `
        (Treffer $updateLog '\.gitignore liegt .* hinter der Vorlage') 1
    Pruefe 'mit der richtigen Zeilenzahl' `
        (Treffer $updateLog '\.gitignore liegt 2 Zeile\(n\) hinter der Vorlage') 1
    # Je zweimal: einmal in der Aufzaehlung, einmal im nachtragbaren Befehl.
    Pruefe 'erste fehlende Zeile namentlich genannt' `
        (Treffer $updateLog '\.team-focus-harry') 2
    Pruefe 'zweite fehlende Zeile namentlich genannt' `
        (Treffer $updateLog '\.team-focus-marv') 2
    # Nicht eigenmaechtig ergaenzen: Eine fehlende Zeile kann eine bewusst
    # entfernte sein. Die Meldung ist die risikofreie Haelfte.
    Pruefe '.gitignore wird NICHT von selbst ergänzt' `
        (Treffer (Join-Path $ziel '.gitignore') 'team-focus') 0

    # --- BL-136: dieselben Zusicherungen fuer die .gitattributes ------------
    # DIES ist der Fall, an dem BL-136 zerbrach und den dieses Skript bis
    # BL-145 nicht kannte.
    Pruefe 'veraltete .gitattributes wird gemeldet' `
        (Treffer $updateLog '\.gitattributes liegt .* hinter der Vorlage') 1
    Pruefe 'mit der richtigen Zeilenzahl' `
        (Treffer $updateLog '\.gitattributes liegt 2 Zeile\(n\) hinter der Vorlage') 1
    Pruefe 'fehlende LF-Zeile namentlich genannt' `
        (Treffer $updateLog '\*\.psm1') 2
    Pruefe 'fehlende CRLF-Zeile namentlich genannt' `
        (Treffer $updateLog '\*\.bat') 2
    # Ohne `add --renormalize` wirkt der Nachtrag erst beim naechsten Klon —
    # genau der Abstand zwischen Ursache und Wirkung, den BL-136 schliessen
    # wollte.
    Pruefe 'und der Renormalisierungs-Schritt dazu' `
        (Treffer $updateLog 'add --renormalize') 1
    Pruefe '.gitattributes wird NICHT von selbst ergänzt' `
        (Treffer (Join-Path $ziel '.gitattributes') '(?m)^\*\.psm1') 0
} finally { Pop-Location }

# --- Die Gegenprobe: Eine Meldung, die immer erscheint, ist keine (BL-14) ----
# Mit vollstaendigem Fragment muss derselbe Lauf SCHWEIGEN. Ohne diese Haelfte
# koennte die Meldung fest verdrahtet sein und der Test bliebe gruen.
Add-Content -Path (Join-Path $ziel '.gitignore') `
    -Value ".team-focus-harry`n.team-focus-marv" -Encoding utf8
Add-Content -Path (Join-Path $ziel '.gitattributes') `
    -Value "*.psm1  text eol=lf`n*.bat   text eol=crlf" -Encoding utf8
Git-Zwischenstand $ziel 'chore: Fragmente vervollstaendigt'

$update2Log = Join-Path $basis 'update2.log'
& (Join-Path $KIT 'pwsh\install.ps1') $ziel -Update -OhneSelbsttest *> $update2Log
if ($LASTEXITCODE -ne 0) {
    Rot 'zweiter install.ps1 -Update (Gegenprobe) schlug fehl:'
    Get-Content -Tail 20 $update2Log | ForEach-Object { Zeile $_ }
    exit 1
}
Pruefe 'vollständiges .gitignore wird nicht angemahnt' `
    (Treffer $update2Log '\.gitignore liegt .* hinter der Vorlage') 0
Pruefe 'und ausdrücklich als vollständig quittiert' `
    (Treffer $update2Log '\.gitignore enthaelt den Block vollstaendig') 1
Pruefe 'vollständige .gitattributes wird nicht angemahnt' `
    (Treffer $update2Log '\.gitattributes liegt .* hinter der Vorlage') 0
Pruefe 'und ausdrücklich als vollständig quittiert' `
    (Treffer $update2Log '\.gitattributes enthaelt den Block vollstaendig') 1

# ------------- 7/8 Abwahl einer Bahn, ihr Bestand und ihr Rueckweg (BL-145)
Kopf '7/8 — Abwahl einer Bahn, ihr Bestand und ihr Rückweg (BL-119/BL-126/BL-129/BL-147)'
# BL-145 nennt diesen Schritt als zweitwichtigsten, und der Grund ist die
# Verbreitung: **Auf Windows ist die einbahnige Ablage der NORMALFALL** — wer
# hier installiert, hat meist keine bash und waehlt sie ab. Die Zusicherung von
# BL-129 ("die Tests bleiben in einer einbahnigen Ablage gruen") galt fuer
# diese Bahn bis hierher UNBELEGT, obwohl sie genau hier am haeufigsten
# gebraucht wird.
#
# Drei Zusicherungen haengen daran, und sie ziehen in verschiedene Richtungen:
#
#   ABWAHL (BL-119): --NurPwsh installiert nur eine Bahn, sichtbar im Protokoll.
#   BESTAND (BL-147): Ein -Update OHNE Schalter HAELT die Bahn. Bis BL-147
#     machte das Update das Projekt "wieder vollstaendig" — im Feld waren das
#     21 ungebetene Dateien in einem Projekt, das sie nie wollte.
#   RUECKWEG (BL-119 + BL-126): -Update -BeideBahnen macht es vollstaendig,
#     und die zurueckgeholte Bahn bekommt die Werte des PROJEKTS, nicht die
#     Auslieferungswerte. Faellt der Installer auf letztere zurueck, hat die
#     neue Bahn eine andere Guard-Grenze als die laufende — und der Guard
#     schuetzt dann den falschen Ordner.
$bBasis = Join-Path ([System.IO.Path]::GetTempPath()) ("team-kit-abwahl-" + [guid]::NewGuid())
$bRepo = Join-Path $bBasis 'projekt'
Neues-WegwerfRepo $bRepo 'quellcode'

$abwahlLog = Join-Path $bBasis 'abwahl.log'
$env:TEAM_INIT_PRODUKTIVCODE = 'quellcode/'
$env:TEAM_INIT_PROJEKT = 'einbahnig-pwsh'
try {
    & (Join-Path $KIT 'pwsh\install.ps1') $bRepo -NichtInteraktiv -NurPwsh -OhneSelbsttest *> $abwahlLog
    $rcAbwahl = $LASTEXITCODE
} finally {
    Remove-Item Env:TEAM_INIT_PRODUKTIVCODE -ErrorAction SilentlyContinue
    Remove-Item Env:TEAM_INIT_PROJEKT -ErrorAction SilentlyContinue
}
if ($rcAbwahl -ne 0) {
    Rot 'Installation mit -NurPwsh schlug fehl:'
    Get-Content -Tail 20 $abwahlLog | ForEach-Object { Zeile $_ }
    exit 1
}

Pruefe 'keine .sh im Projekt' (Dateien-Mit-Endung $bRepo @('.sh')) 0
# BL-154: gemessen gegen die QUELLE, nicht gegen eine abgeschriebene Zahl. Als
# der elfte Entrypoint dazukam, behauptete eine fest verdrahtete 10 das
# Gegenteil dessen, was sie gefunden hatte.
Pruefe 'die pwsh-Bahn ist vollständig' `
    (Dateien-Mit-Endung $bRepo @('.ps1', '.cmd')) `
    (@(Get-ChildItem (Join-Path $KIT 'pwsh\entry') -File |
       Where-Object { $_.Extension -in @('.ps1', '.cmd') }).Count)
Pruefe 'kein bash-Kern in team/' (Dateien-Mit-Endung (Join-Path $bRepo 'team') @('.sh')) 0
Pruefe 'und die Abwahl steht im Protokoll' `
    (Treffer $abwahlLog 'Nur die pwsh-Bahn installiert') 1

# --- BL-129: Die Tests duerfen in einer einbahnigen Ablage nicht ROT sein.
# Eine abgewaehlte Bahn ist kein Defekt — aber der Uebersprung muss SICHTBAR
# sein, sonst liest er sich am Ende wie ein bestandener Nachweis.
if ($ptBefehl -or (Get-Command pytest -ErrorAction SilentlyContinue)) {
    $einbahnigLog = Join-Path $bBasis 'einbahnig.log'
    $script:SuiteLaeufe++
    $rcEin = Suite-Mitschnitt $bRepo $einbahnigLog `
                $(if ($ptBefehl) { $ptBefehl } else { 'pytest' }) `
                $(if ($ptBefehl) { @('-m', 'pytest') } else { @() })
    Pruefe 'Tests bleiben grün in einer nur-pwsh-Ablage (BL-129)' $rcEin 0
    Pruefe 'kein Fehlschlag durch die fehlende Bahn' `
        (Treffer $einbahnigLog '(?m)^\d+ (failed|error)') 0
    Pruefe 'und die Einbahnigkeit steht in der Zusammenfassung' `
        (Treffer $einbahnigLog 'einbahnige Ablage') 1
    # Der eigentliche Inhalt von BL-129: Die uebersprungene Bahn wird BENANNT
    # und GEZAEHLT. Ohne die Zahl bliebe unsichtbar, wie viel der Nachweis
    # ausgelassen hat.
    Pruefe 'die abgewählte bash-Bahn ist als Übersprung ausgewiesen' `
        (Treffer $einbahnigLog 'bash-Bahn uebersprungen') 1
    Pruefe 'und der Grund nennt die ABWAHL, nicht einen Defekt' `
        (Treffer $einbahnigLog 'in dieser Ablage abgewaehlt \(--nur-pwsh\)') 1
} else {
    Gelb 'pytest fehlt — die Einbahnigkeit ist UNGEPRÜFT.'
    $script:Fehler = 1
}

# --- Der Bestand (BL-147): Das Routine-Update haelt die Bahn
Git-Zwischenstand $bRepo 'einbahnig pwsh installiert'
$bestandLog = Join-Path $bBasis 'bestand.log'
& (Join-Path $KIT 'pwsh\install.ps1') $bRepo -Update -OhneSelbsttest *> $bestandLog
if ($LASTEXITCODE -ne 0) {
    Rot '-Update auf einem NUR-PWSH-Projekt schlug fehl (BL-126):'
    Get-Content -Tail 20 $bestandLog | ForEach-Object { Zeile $_ }
    exit 1
}
Pruefe '-Update lässt die nur-pwsh-Ablage einbahnig (BL-147)' `
    (Dateien-Mit-Endung $bRepo @('.sh')) 0
Pruefe 'und die Erkennung nennt die pwsh-Bahn' `
    (Treffer $bestandLog 'Einbahnige Ablage erkannt: nur die pwsh-Bahn') 1

# --- Der Rueckweg, jetzt ausdruecklich (BL-119 + BL-126)
Git-Zwischenstand $bRepo 'einbahnig pwsh geblieben'
$rueckwegLog = Join-Path $bBasis 'rueckweg.log'
& (Join-Path $KIT 'pwsh\install.ps1') $bRepo -Update -BeideBahnen -OhneSelbsttest *> $rueckwegLog
if ($LASTEXITCODE -ne 0) {
    Rot '-Update -BeideBahnen auf einem NUR-PWSH-Projekt schlug fehl (BL-126):'
    Get-Content -Tail 20 $rueckwegLog | ForEach-Object { Zeile $_ }
    exit 1
}
Pruefe '-BeideBahnen holt die Bash-Bahn zurück' `
    (Dateien-Mit-Endung $bRepo @('.sh')) `
    (@(Get-ChildItem (Join-Path $KIT 'bash\entry') -File -Filter '*.sh').Count)
Pruefe 'team.config.sh ist wieder da' `
    (Test-Path (Join-Path $bRepo 'team.config.sh')) $true
# Der eigentliche Fund von BL-119: Die Datei war da und trotzdem halb fertig.
Pruefe 'und VOLLSTÄNDIG gefüllt (kein Platzhalter übrig)' `
    (Treffer (Join-Path $bRepo 'team.config.sh') '\{\{') 0
# Der Kern von BL-126: Die Werte muessen aus der VORHANDENEN Konfiguration
# stammen, nicht aus den Auslieferungswerten.
Pruefe 'mit den Werten des Projekts, aus team.config.ps1 gelesen' `
    (Treffer (Join-Path $bRepo 'team.config.sh') 'TEAM_PRODUKTIVCODE:-quellcode/') 1
Pruefe 'und die Quelle steht im Protokoll' `
    (Treffer $rueckwegLog 'Projektwerte aus team.config.ps1 gelesen') 1
Pruefe 'das Nachziehen ist gemeldet worden' `
    (Treffer $rueckwegLog 'team.config.sh fehlte und ist neu erzeugt worden') 1

Remove-Item -Recurse -Force $bBasis -ErrorAction SilentlyContinue

# --------------------------------------------------------- 8/8 Trockenlauf
Kopf '8/8 — Trockenlauf der Rollen (TEAM_DRY_RUN=1, keine CLI-Kosten)'
# Der Schritt, den es unter bash so nicht gibt: Er belegt, dass die Kette
# Shim -> .ps1 -> lib.psm1 -> Werkzeuge auf DIESER Maschine traegt — ohne
# Agenten-CLI und ohne einen Cent. Genau das ist die Frage, die ein Anwender
# auf einer frischen Windows-Maschine hat.
Push-Location $ziel
try {
  try {
    # BL-150: Der Plankopf steht hier ABSICHTLICH fett — so, wie ein Architekt
    # ihn im Feld angelegt hat, der dem Stil des uebrigen Kopfes folgte
    # (`**Plan:**`, `**Stufen:**`). Bis dahin baute dieser Selbsttest seinen
    # Plankopf immer blank und pruefte damit genau den Fall nie, der im Feld
    # eintrat: Ralph stieg mit Exit 1 aus, `Cap ?` im Status, und die
    # Budget-Empfehlung kam nie an. Blank wird von den Funktionstests der
    # Suite abgedeckt (test_bl150_plankopf_auszeichnung.py, fuenf Notationen
    # auf beiden Bahnen) — hier steht die Notation, die weh getan hat.
    Set-Content -Path 'plans/ralph-kaskade-1-selbsttest.md' `
        -Value "**RALPH_CAP=1**`n**BUDGET_EMPFEHLUNG_USD=9**`n`n# Stufe 1`n" -Encoding utf8
    Set-Content -Path '.ralph-plan' -Value 'plans/ralph-kaskade-1-selbsttest.md' -Encoding ascii
    # Zurueck auf Stufe 1: Schritt 5 hat den Kaskadenstand auf 5 gesetzt (das
    # war dort der Beweis, dass ein Update ihn nicht anfasst). Ohne das Zuruecksetzen
    # laege die naechste Stufe ueber RALPH_CAP=1, Ralph haette sofort Feierabend
    # und der Trockenlauf pruefte nichts — waere aber gruen. Genau die Sorte
    # Test, die bestanden meldet, ohne etwas ausgefuehrt zu haben.
    Set-Content -Path '.ralph-state' -Value '1' -Encoding ascii
    & git add -A | Out-Null
    & git commit -q -m 'chore: Plan für den Selbsttest' | Out-Null

    $gemerktRun = $env:TEAM_DRY_RUN
    $gemerktResult = $env:TEAM_DRY_RESULT
    $env:TEAM_DRY_RUN = '1'
    $env:TEAM_DRY_RESULT = 'fertig <promise>STUFE_1_COMPLETE</promise> <promise>REDTEAM_SWEEP_COMPLETE</promise>'
    try {
        $trockenLog = Join-Path $basis 'trocken.log'
        # Eigener Prozess: Die Rollen schreiben mit
        # [Console]::Out.WriteLine, das PowerShells *>-Umlenkung nicht
        # einfaengt (siehe Rolle-Starten in vollautomatik.ps1).
        & pwsh -NoProfile -File ./vollautomatik.ps1 *> $trockenLog
        $rc = $LASTEXITCODE
        $text = Get-Content -Raw $trockenLog
        Pruefe 'Vollautomatik läuft durch (Exit 0)' $rc 0
        Pruefe 'Ralph hat die Stufe quittiert' ($text -match 'Stufe 1 abgeschlossen') $true
        Pruefe 'Ralph erreicht den Cap' ($text -match 'über RALPH_CAP') $true
        Pruefe 'Harry hat gesweept' ($text -match 'harry hat einen Sweep abgeschlossen') $true
        Pruefe 'Marv hat gesweept' ($text -match 'marv hat einen Sweep abgeschlossen') $true
        Pruefe 'Abschlussbericht erscheint' ($text -match 'ABSCHLUSSBERICHT') $true
        # Kein echter Aufruf: Die Dry-Run-Logs tragen exakt 0.01 USD je Rolle.
        Pruefe 'keine echten CLI-Kosten' ($text -match 'DRY-RUN — kein Claude-Aufruf') $true
        if ($script:Fehler -ne 0) { Get-Content -Tail 15 $trockenLog | ForEach-Object { Zeile $_ } }
    } finally {
        $env:TEAM_DRY_RUN = $gemerktRun
        $env:TEAM_DRY_RESULT = $gemerktResult
    }
  } catch {
    Rot "Trockenlauf abgebrochen: $($_.Exception.Message)"
    $script:Fehler = 1
  }
} finally { Pop-Location }

# ----------------------------------------------------------------- Abschluss
Kopf 'Was dieser Lauf NICHT geprüft hat'
# Die Ehrlichkeit ist hier kein Stil, sondern der Zweck: Wer glaubt, alles
# geprüft zu haben, prüft den Rest nie.
Zeile 'Die Bash-Bahn (.sh) — hier liegt keine bash. Sie ist mitinstalliert und'
Zeile 'gilt unverändert aus dem Kit.'
Zeile 'Den GLEICHSTAND beider Installer (kit-test.sh, Schritt 10/10) — der'
Zeile 'braucht beide Shells nebeneinander und läuft auf einer Linux-Maschine.'
Zeile 'Das Regel-Inventar (kit-test.sh, Schritt 9) — es ist reines Python und'
Zeile 'laeuft in der Suite ohnehin mit.'
Zeile 'Den Einzug in eine gewachsene Codebasis (kit-test.sh, Schritt 7).'
Zeile 'Die Einrichtungsroutine (kit-test.sh, Schritt 10) — sie prueft eine'
Zeile 'Bash-Routine.'

Kopf 'Ergebnis'
# BL-195: Die Zahl der wirklich gefahrenen Suite-Durchgaenge gehoert ins
# Ergebnis. Ohne sie waere ein Schalter, der versehentlich auch einen echten
# Durchgang abstellt, von einem gruenen Lauf nicht zu unterscheiden.
if ($script:SuiteLaeufe -ne 4) {
    Rot "Nur $($script:SuiteLaeufe) von 4 Suite-Durchgängen gefahren."
    Zeile 'Die vier sind: der Selbsttest des Installers (2, BL-127),'
    Zeile 'Auslieferungswerte (4), angepasste Konfiguration (5), einbahnige'
    Zeile 'Ablage (7). Fehlt einer, ist die Zusicherung dahinter offen.'
    $script:Fehler = 1
} else {
    Zeile 'Suite-Durchgänge: 4 — die uebrigen Installer-Aufrufe liefen mit'
    Zeile '-OhneSelbsttest (BL-195); sie haetten nur wiederholt.'
}
if ($script:Gepruefte -ne $script:PruefungenSoll) {
    Rot "Nur $($script:Gepruefte) von $($script:PruefungenSoll) Einzelprüfungen gefahren — ein Schritt wurde übersprungen."
    $script:Fehler = 1
}
if ($script:Fehler -ne 0) {
    Write-Host '  Selbstverifikation NICHT grün.' -ForegroundColor Red
    Zeile "Wegwerf-Repo bleibt zur Ansicht liegen: $basis"
    exit 1
}
Remove-Item -Recurse -Force $basis -ErrorAction SilentlyContinue
Write-Host '  Selbstverifikation grün (pwsh-Bahn).' -ForegroundColor Green
exit 0

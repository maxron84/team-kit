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

# Wie viele Einzelpruefungen ein vollstaendiger Lauf fahren MUSS. Die Zahl ist
# die zweite Haelfte des Absturzschutzes: Ein Schritt, der stillschweigend
# uebersprungen wird, aendert die Zahl — und ein Selbsttest, der weniger
# geprueft hat als er soll, hat nicht bestanden, sondern nur nichts gemerkt.
$script:PruefungenSoll = 15

Write-Host '=== T.E.A.M.-Starterkit — Selbstverifikation (Windows) ===' -ForegroundColor White
Write-Host "  Kit: $KIT"

# --------------------------------------------------------- 1/6 Wegwerf-Repo
Kopf '1/6 — Wegwerf-Repo anlegen'
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

# ------------------------------------------------------ 2/6 Kit installieren
Kopf '2/6 — Kit installieren (install.ps1, nicht-interaktiv)'
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

# ------------------------------------------------- 3/6 Ungefuellte Platzhalter
Kopf '3/6 — Ungefüllte Platzhalter suchen'
# Ein uebrig gebliebenes {{...}} heisst: Der Installer kennt die Datei nicht
# oder der Platzhalter wurde umbenannt. Beides faellt sonst erst im Feld auf,
# wo die Briefings die Pfade des Ursprungsprojekts nennen wuerden — falsche
# Guard-Grenze. Geprueft werden BEIDE Konfigurationen: Ein {{PYTHON}}, das nur
# in team.config.ps1 steht, faellt einem bash-Lauf nie auf.
$reste = @(Get-ChildItem -Path $ziel -Recurse -File -ErrorAction SilentlyContinue |
           Where-Object { $_.FullName -notmatch '[\\/]\.git[\\/]' } |
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

# ------------------------------------------------------ 4/6 Regressionstests
Kopf '4/6 — Regressionstests in der Installation'
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

# ----------------------------------------------- 5/6 Update schuetzt Projektdaten
Kopf '5/6 — Update-Pfad schützt Projektdaten'
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
    & git add -A | Out-Null
    & git commit -q -m 'projektstand' | Out-Null
} finally { Pop-Location }

$updateLog = Join-Path $basis 'update.log'
& (Join-Path $KIT 'pwsh\install.ps1') $ziel -Update *> $updateLog
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
} finally { Pop-Location }

# --------------------------------------------------------- 6/6 Trockenlauf
Kopf '6/6 — Trockenlauf der Rollen (TEAM_DRY_RUN=1, keine CLI-Kosten)'
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
Zeile 'Das Regel-Inventar und den Einzug in eine gewachsene Codebasis'
Zeile '(kit-test.sh, Schritte 7 und 8).'

Kopf 'Ergebnis'
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

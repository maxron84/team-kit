# Bahn: pwsh | Gegenstueck: install.sh
<#
  install.ps1 — installiert das T.E.A.M. in ein Zielprojekt (Windows, nativ).

  Aufruf:  pwsh -File install.ps1 <zielpfad> [-NichtInteraktiv] [-Force|-Update]
                                             [-NurBash|-NurPwsh|-BeideBahnen]
           pwsh -File install.ps1 -Hilfe

    <zielpfad>        Das Projekt, in das das Team einziehen soll. Muss ein
                      Git-Repository sein. Pflichtangabe (ausser bei -Hilfe).
    -NichtInteraktiv  Keine Rueckfragen; Werte aus den TEAM_INIT_*-Umgebungs-
                      variablen oder den Defaults. Fuer Skripte und Tests.
    -Update           Nur die Team-INFRASTRUKTUR aktualisieren — Entrypoints,
                      team\lib.psm1, team\tools, team\prompts, team\tests und
                      TEAM.md, die Bedienungsanleitung. Ruehrt KEINE
                      Projektdaten an: team.config.*, CLAUDE.md, CHANGELOG.md,
                      Ledger, State und plans\ bleiben, wie sie sind. Der
                      richtige Weg, um ein bestehendes Projekt auf eine neue
                      Kit-Version zu heben.
    -Force            Vorhandene Dateien ueberschreiben (Standard: ueberspringen).

    ACHTUNG  -Force ist NUR fuer eine kaputte Erstinstallation gedacht, NIE fuer
             ein gelebtes Projekt: Es ueberschreibt auch .budget-ledger
             (Kostenhistorie weg), .ralph-state (Kaskadenstand zurueck auf 1),
             das Beutebuch (alle Funde weg), CHANGELOG.md, plans\*.md und die
             Konfiguration (Smoke-Test weg). Empirisch nachgestellt, BL-8.
             Fuer Updates: -Update.

    -NurBash          Nur die bash-Bahn ablegen (Entrypoints *.sh,
                      team/lib.sh, team.config.sh).
    -NurPwsh          Nur die pwsh-Bahn ablegen (Entrypoints *.cmd/*.ps1,
                      team/lib.psm1, team.config.ps1).
                      Ohne beide Schalter kommen BEIDE Bahnen — die Abwahl
                      ist ausdruecklich und kommt vom Anwender (BL-119).
    -BeideBahnen      Nur mit -Update: eine frueher abgewaehlte Bahn wieder
                      zurueckholen. Schliesst -NurBash/-NurPwsh aus (BL-147).
    -Hilfe            Diesen Kopf ausgeben und sonst nichts tun.
                      Auch als -Help und -h.

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
    # Drift an. Zurueckgeholt wird mit -Update -BeideBahnen (BL-147).
    [switch]$NurBash,
    [switch]$NurPwsh,
    # BL-147: Der Rueckweg aus BL-119 war bis hierher der Default und damit ein
    # Automatismus — ein Update ohne Schalter legte die zweite Bahn dazu, auch
    # in ein Projekt, das nie eine wollte. Jetzt ist er ein Schalter.
    # Begruendung am Erkennungsblock im Update-Pfad.
    [switch]$BeideBahnen,
    # BL-156: Das Gegenstueck zu --hilfe in install.sh. Die Aliasse bilden die
    # drei Schreibweisen der bash-Fassung (-h/--hilfe/--help) nach, damit ein
    # Wechsel der Bahn nicht auch ein Wechsel der Gewohnheit ist.
    [Alias('Help', 'h')]
    [switch]$Hilfe
)

$ErrorActionPreference = 'Stop'
# BL-122: Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
# standardmaessig $true — ein Exit-Code != 0 aus einem NATIVEN Befehl ist damit
# ein TERMINIERENDER Fehler und nicht mehr nur ein Wert in $LASTEXITCODE. Diese
# Bahn ist durchgehend fuer den klassischen Vertrag geschrieben: aufrufen,
# $LASTEXITCODE lesen, entscheiden. Ohne diese Zeile ist jede dieser
# Entscheidungen unerreichbar — der Abbruch kommt vorher.
$PSNativeCommandUseErrorActionPreference = $false
# BL-135: Dieses Skript faengt die Ausgabe nativer Prozesse auf. PowerShell
# dekodiert sie mit [Console]::OutputEncoding, und das ist unter Windows die
# OEM-Codepage der Konsole (auf der Fundmaschine 850). Alles im Kit spricht
# UTF-8 — als cp850 gelesen wird aus einem Umlaut ein Paar Rahmenzeichen, und
# aus einem Geviertstrich drei Zeichen. Wer lib.psm1 importiert, erbt die
# Einstellung von dort; diese Datei tut es nicht und setzt sie deshalb selbst.
# Ohne BOM: Das ist eine Kodierung fuer einen STROM, nicht fuer eine Datei.
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

# BL-156: Der Hilfetext IST der Dateikopf, keine zweite Fassung daneben —
# dieselbe Bauart wie --hilfe in install.sh und dieselbe Lehre wie BL-154: Eine
# Abschrift laeuft auseinander, und dann sagt -Hilfe etwas anderes als die
# Datei. Waechst der Kopf, waechst die Hilfe mit.
#
# WARUM NICHT comment-based help. Das waere der pwsh-uebliche Weg und braechte
# -? geschenkt. Auf dieser Maschine gemessen (pwsh 7.6.5): Get-Help findet den
# <# … #>-Block NICHT, wenn die Zeile `# Bahn: pwsh | Gegenstueck: install.sh`
# davorsteht — die Ausgabe schrumpft auf die blosse Syntaxzeile. Ohne die
# Bahn-Zeile funktioniert es. Die Bahn-Zeile ist aber nicht verhandelbar: Sie
# muss laut test_bahn_kopfzeile.py in den ersten drei Zeilen stehen, und sie
# ist die einzige Stelle, an der eine Datei ihre Bahn selbst nennt. Also liest
# die Hilfe die eigene Datei, statt den Kopf fuer ein Werkzeug umzubauen.
#
# Gelesen wird ab Zeile 2 — Zeile 1 ist die Bahn-Kopfzeile, Maschinensache —
# vom oeffnenden <# bis zum schliessenden #>. Die zwei fuehrenden Leerzeichen
# des Blocks fallen weg, damit die Einrueckung dieselbe ist wie in der
# bash-Fassung (dort faellt das "# " weg).
function Zeige-Hilfe {
    $zeilen = [System.IO.File]::ReadAllLines($PSCommandPath)
    $drin = $false
    foreach ($z in $zeilen[1..($zeilen.Count - 1)]) {
        if (-not $drin) {
            if ($z.TrimStart() -eq '<#') { $drin = $true }
            continue
        }
        if ($z.TrimStart() -eq '#>') { break }
        Write-Host ($z -replace '^  ', '')
    }
}

if ($Hilfe) { Zeige-Hilfe; exit 0 }

if ($NurBash -and $NurPwsh) {
    Write-Host "FEHLER: -NurBash und -NurPwsh schliessen einander aus." -ForegroundColor Red
    exit 2
}
$NurBahn = if ($NurBash) { 'bash' } elseif ($NurPwsh) { 'pwsh' } else { '' }
if ($BeideBahnen -and $NurBahn) {
    $abwahl = if ($NurBahn -eq 'pwsh') { '-NurPwsh' } else { '-NurBash' }
    Write-Host "FEHLER: -BeideBahnen und $abwahl schliessen sich aus." -ForegroundColor Red
    Write-Host "  -BeideBahnen holt eine fehlende Bahn zurueck, -Nur* waehlt eine ab."
    exit 2
}

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

function Get-KitBahnDateien {
    <#
      BL-147: Die Dateien, die das KIT fuer eine Bahn ausliefert — als Paare
      aus Zielname und Unterordner. Grundlage fuer die Erkennung UND fuer die
      Reste-Meldung: Beide duerfen nicht an der Endung entscheiden. Ein
      projekteigenes deploy.ps1 ist keine pwsh-Bahn, und ein build.sh macht
      aus einem Windows-Projekt kein zweibahniges.
    #>
    param([string]$Bahn)
    $liste = @()
    if ($Bahn -eq 'bash') {
        foreach ($f in (Get-ChildItem (Join-Path $KIT 'bash\entry') -Filter '*.sh' -File)) {
            $liste += @{ Name = $f.Name; Ordner = '' }
        }
        $liste += @{ Name = 'lib.sh';     Ordner = 'team/' }
        $liste += @{ Name = 'redteam.sh'; Ordner = 'team/' }
    } else {
        foreach ($muster in @('*.ps1', '*.cmd')) {
            foreach ($f in (Get-ChildItem (Join-Path $KIT 'pwsh\entry') -Filter $muster -File)) {
                $liste += @{ Name = $f.Name; Ordner = '' }
            }
        }
        $liste += @{ Name = 'lib.psm1';    Ordner = 'team/' }
        $liste += @{ Name = 'redteam.ps1'; Ordner = 'team/' }
    }
    return $liste
}

function Test-BahnLiegtDa {
    <# BL-147: Liegt diese Bahn im Zielprojekt? #>
    param([string]$Bahn)
    foreach ($d in (Get-KitBahnDateien $Bahn)) {
        if (Test-Path (Join-Path $Ziel "$($d.Ordner)$($d.Name)") -PathType Leaf) { return $true }
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
    Write-Host "Alle Optionen: pwsh -File install.ps1 -Hilfe"
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

function Abgleich-Unterschiede {
    <#
      BL-178: Die Zeilen, in denen sich zwei Textdateien unterscheiden —
      OHNE dass die Zeilenenden ins Gewicht fallen.

      Eigene Funktion, damit ein Test sie aus der ECHTEN Datei holen und
      fahren kann. Ein Test gegen einen nachgebauten Zwilling beweist etwas
      ueber den Zwilling (Lehre BL-142); und die Zeilenenden sind hier genau
      die Stelle, an der die bash-Fassung schon einmal falsch lag (BL-137).

      `diff --strip-trailing-cr` hat auf dieser Bahn kein Gegenstueck — es
      wird auch keines gebraucht: `Get-Content` zerlegt an CRLF UND an LF und
      liefert die Zeilen ohne Wagenruecklauf. Eine vor BL-137 unter Windows
      installierte Fassung mit CRLF vergleicht sich damit sauber gegen die
      frisch gerenderte mit LF, statt JEDE Zeile als abgewichen zu melden.
      Ein stiller Fehler, gegen einen lauten Fehlalarm getauscht, waere kein
      Fortschritt (Bauart BL-14). Dass es so ist, steht unter Test — nicht
      nur in diesem Kommentar.

      Compare-Object vergleicht als MENGE, nicht Zeile gegen Zeile: Eine
      reine Umsortierung faellt damit nicht auf. Bewusst in Kauf genommen —
      `-SyncWindow 0` laesst eine einzige eingefuegte Zeile alle folgenden
      als abgewichen gelten, und eine Zahl, die bei jeder Kleinigkeit
      dreistellig wird, sagt dem Leser nichts.
    #>
    param([string]$Links, [string]$Rechts)
    return @(Compare-Object (Get-Content -LiteralPath $Links) `
                            (Get-Content -LiteralPath $Rechts))
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
        # BL-149: ZWEI Platzhalter fuer einen Wert. {{SMOKE_TEST}} steht in
        # Regeltexten — dort sagt der TODO-Satz einem Menschen, was fehlt.
        # {{SMOKE_TEST_KONFIG}} steht NUR in team.config.*, und dort war er ein
        # Schaden: Die Weichen der Bibliothek unterscheiden "konfiguriert" von
        # "nicht konfiguriert" ueber leer/nicht-leer, also galt der Platzhalter
        # als KONFIGURIERTER Befehl. In Kaskade 1 jedes Projekts landete er im
        # Prompt der Rollen, in der Werkzeug-Allowlist des Red Teams und wurde
        # von der Selbstpruefung woertlich ausgefuehrt (Exit 127). Ausfuehrliche
        # Begruendung in der Fuell-Routine von install.sh.
        '{{SMOKE_TEST}}'       = $(if ($SmokeTest) { $SmokeTest } else { 'TODO: noch keiner — Stufe 1 der ersten Kaskade' })
        # BL-170: Die VIERTE Einsetzstelle. In Ralphs Briefing steht der Satz
        # unter den EISERNEN GRENZEN und in Backticks — also in der
        # Auszeichnung, an der eine ausfuehrende Instanz einen Befehl erkennt.
        # Ein TODO-Satz dort ist derselbe Fehler wie ein nicht-leerer Default
        # in team.config.*, nur eine Ebene hoeher: Das Briefing ist eine
        # statische Datei, die TODO-Weiche der Bibliothek greift dort nicht,
        # und im Prompt derselben Stufe steht daneben SMOKE_ZEILE mit der
        # richtigen Aussage ("kein Smoke-Test konfiguriert, Schritt entfaellt").
        # Zwei einander widersprechende Anweisungen im selben Prompt.
        #
        # Deshalb ein eigener Platzhalter fuer den GANZEN Satz: Ohne
        # Smoke-Test steht dort Prosa ohne Backticks.
        '{{SMOKE_TEST_GRENZE}}' = $(if ($SmokeTest) {
            "Der Smoke-Test (``$SmokeTest``) muss gruen sein, bevor die Stufe fertig ist."
        } else {
            'Fuer dieses Projekt ist noch KEIN Smoke-Test konfiguriert. Ihn zu bauen ist Aufgabe von Stufe 1 dieser Kaskade; bis dahin entfaellt der Schritt, und ich erfinde keinen Befehl.'
        })
        '{{SMOKE_TEST_KONFIG}}' = $SmokeTest
        '{{TECH_STACK}}'       = $TechStack
        '{{DEPLOY}}'           = $Deploy
        '{{DEPLOY_AUSNAHMEN}}' = $DeployAusnahmen
        '{{DOMAENEN}}'         = $Domaenen
        '{{COMMIT_ENTSCHEID}}' = $CommitEntscheid
        '{{PYTHON}}'           = $Python
        '{{WEITERER_CODE}}'    = $WeitererCode
        '{{TEST_BESTAND}}'     = $TestBestand
        '{{PLAN_BESTAND}}'     = $PlanBestand
        # BL-153: Wo das Kit auf DIESER Maschine liegt. Stand bis einschliesslich 2.12.0 als
        # ~/Source/team-kit in der Prosa und zeigte damit ueberall dorthin, wo
        # der Autor geklont hatte. Steht nur in team.config.*; das Werkzeug
        # kit_meldung.py kann ohne ihn arbeiten, aber nicht ohne Suchen.
        #
        # BL-163: Schraegstriche statt Rueckstriche — und zwar in BEIDE
        # Konfigurationen, denn dieser Installer schreibt team.config.sh mit.
        # Bis 2026-08-25 setzte die pwsh-Bahn hier `C:\Users\...`, die
        # bash-Bahn `C:/Users/...`; Stufe 11 des Selbsttests ("beide Installer
        # erzeugen denselben Baum") war damit auf Windows dauerhaft rot.
        #
        # Nachgemessen sind BEIDE Formen funktionsfaehig — in bash (auch nach
        # dem Sourcen), in Python und in PowerShell. Der Fix ist deshalb keine
        # Fehlerbehebung, sondern eine Vereinheitlichung: Eine Pruefung, die
        # immer rot steht, wird nicht gelesen (BL-14) — und sie ist die
        # einzige, die einen ECHTEN Auseinanderlauf der beiden Installer
        # faende. Genommen wird die Schraegstrich-Form, weil sie in allen drei
        # Sprachen ohne Maskierung durch jeden Kontext geht.
        '{{KIT_PFAD}}'         = $KIT.Replace('\', '/')
    }
    # BL-139: die bahnabhaengigen Pfade. Nannten die Regeltexte frueher fest,
    # und in einer einbahnigen Ablage schickten sie damit jede Rolle an Dateien,
    # die es dort nicht gibt — still, ohne Meldung. Am teuersten war
    # team.config.sh: Der Regeltext verlangte Eintraege dort, waehrend
    # team/lib.psm1 team.config.ps1 liest.
    #
    # Vorbelegt ist die bash-Bahn, wie in install.sh: In einer zweibahnigen
    # Ablage (dem Default) liegt beides, und der gerenderte Text bleibt Byte
    # fuer Byte der von vorher. Nur die Abwahl der bash-Bahn aendert etwas.
    if ($script:NurBahn -eq 'pwsh') {
        $script:Werte['{{RUF}}']     = '.\'
        $script:Werte['{{ENDUNG}}']  = '.cmd'
        $script:Werte['{{KONFIG}}']  = 'team.config.ps1'
        $script:Werte['{{LIB}}']     = 'team/lib.psm1'
        $script:Werte['{{REDTEAM}}'] = 'team/redteam.ps1'
    } else {
        $script:Werte['{{RUF}}']     = './'
        $script:Werte['{{ENDUNG}}']  = '.sh'
        $script:Werte['{{KONFIG}}']  = 'team.config.sh'
        $script:Werte['{{LIB}}']     = 'team/lib.sh'
        $script:Werte['{{REDTEAM}}'] = 'team/redteam.sh'
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

function Melde-VeraltetenRegeltext {
    <#
      BL-177. Der Rest, den BL-175 ausgewiesen hat.

      BL-139 hat die bahnabhaengigen Stellen der VORLAGEN auf Platzhalter
      gestellt, BL-140 die Backlognummern auf `Kit-`. Beides wirkt beim
      RENDERN — also nur bei der naechsten Erstinstallation. Ein Projekt, das
      vorher eingezogen ist, behaelt seine CLAUDE.md unveraendert, und das
      Update fasst sie zu Recht nicht an: Sie traegt Projektarbeit.

      Damit steht in einem gelebten Projekt weiter ein Regeltext, der
      Dateien nennt, die es dort nicht gibt — und der Fehlermodus ist STILL.
      Ein totes `.\ralph.cmd` scheitert sichtbar; ein `team.config.sh`, in das
      eine Rolle `TEAM_SMOKE_TEST` eintragen soll, waehrend `team/lib.psm1`
      `team.config.ps1` liest, scheitert nie: Der Wert wird eingetragen und
      nie gelesen. Jede Rolle hat diesen Text im Systemprompt.

      Im Feld (`duke-itam-2026`) war das am 2026-08-25 nachweisbar: 14 tote
      Pfade und 5 blanke Kit-Nummern in CLAUDE.md, ein Jahr nach dem Einzug
      und ueber mehrere Updates hinweg — niemandem gemeldet.

      REPARIERT WIRD NICHT AUTOMATISCH (Lehre BL-12). CLAUDE.md ist
      Projektdatei; ein Installer, der darin ersetzt, ueberschreibt fremde
      Arbeit. Gemeldet wird mit der Zuordnung, die der Anwender braucht.
    #>
    $datei = Join-Path $Ziel 'CLAUDE.md'
    if (-not (Test-Path $datei)) { return }
    $text = [System.IO.File]::ReadAllText($datei)

    # Die Zwei-Bahnen-Region ausschneiden: Dort ist das Nennen BEIDER Bahnen
    # die Aufgabe, kein Fehler. An ihrem TEXT erkannt, nicht an Zeilennummern
    # — die verschieben sich beim naechsten Absatz, und eine Ausnahme, die
    # dann die falsche Stelle schuetzt, faellt niemandem auf (BL-139).
    $regionAuf = 'Installiert mit dem **T.E.A.M.-Starterkit**. Ablage:'
    $regionZu  = '**Der `team/`-Ordner gehört der Infrastruktur'
    $i = $text.IndexOf($regionAuf)
    if ($i -ge 0) {
        $j = $text.IndexOf($regionZu, $i)
        if ($j -lt 0) { $j = $text.Length }
        $text = $text.Substring(0, $i) + $text.Substring($j)
    }

    # (1) Pfade, die der Text nennt und die es hier nicht gibt. Kit-Pfade sind
    # ausgenommen: Sie liegen im Kit bzw. global, nicht im Zielprojekt, und
    # ihre Abwesenheit ist keine Aussage ueber die Bahn.
    $kitPfade = @('install.sh', 'install.ps1', 'team-auth-setup.sh',
                  'team-auth-setup.ps1', 'team-init.sh', 'team-init.ps1')
    $tot = [System.Collections.Generic.List[string]]::new()
    $muster = '(?<![\w/.\\-])(?:\./|\.\\)?((?:team/)?[A-Za-z0-9_.-]+\.(?:sh|ps1|psm1|cmd))'
    foreach ($m in [regex]::Matches($text, $muster)) {
        $rel = $m.Groups[1].Value
        if ($kitPfade -contains ($rel -split '/')[-1]) { continue }
        if (Test-Path (Join-Path $Ziel $rel)) { continue }
        if (-not $tot.Contains($rel)) { $tot.Add($rel) }
    }

    # (2) Blanke Backlognummern, die die VORLAGE inzwischen `Kit-` schreibt.
    # Die Vorlage ist der Massstab, nicht eine Liste hier: Eine Liste waere ab
    # der naechsten neuen Nummer falsch (BL-154).
    $blank = [System.Collections.Generic.List[string]]::new()
    $vorlage = Join-Path $KIT 'bootstrap\CLAUDE.md.vorlage'
    if (Test-Path $vorlage) {
        $vorlagentext = [System.IO.File]::ReadAllText($vorlage)
        foreach ($m in [regex]::Matches($vorlagentext, 'Kit-((?:BL|HM)-\d+)')) {
            $nummer = $m.Groups[1].Value
            if ($blank.Contains($nummer)) { continue }
            if ([regex]::IsMatch($text, '(?<!Kit-)\b' + [regex]::Escape($nummer) + '\b')) {
                $blank.Add($nummer)
            }
        }
    }

    if ($tot.Count -eq 0 -and $blank.Count -eq 0) { return }

    Kopf "CLAUDE.md stammt aus einer Fassung vor Kit-BL-139/Kit-BL-140 (Kit-BL-177)"
    Write-Host "  Diese Datei steht im Systemprompt JEDER Rolle. Das Update hat sie"
    Write-Host "  nicht angefasst — sie traegt Projektarbeit, und die gehoert dir."
    if ($tot.Count) {
        Rot "  [x] $($tot.Count) genannte Pfade gibt es in dieser Ablage nicht:"
        foreach ($p in $tot) { Write-Host "        $p" }
        Gelb "      Der teuerste Fall ist der leiseste: Verlangt der Text Eintraege"
        Gelb "      in einer Konfiguration, die hier nicht gelesen wird, wird der"
        Gelb "      Wert eingetragen und wirkt nie. Kein Abbruch, keine Meldung."
        Write-Host "      Zuordnung fuer diese Ablage:"
        Write-Host "        $($script:Werte['{{KONFIG}}'])  <- team.config.*"
        Write-Host "        $($script:Werte['{{LIB}}'])  <- team/lib.*"
        Write-Host "        $($script:Werte['{{REDTEAM}}'])  <- team/redteam.*"
        Write-Host "        $($script:Werte['{{RUF}}'])<name>$($script:Werte['{{ENDUNG}}'])  <- Entrypoints in der Wurzel"
    }
    if ($blank.Count) {
        Rot "  [x] $($blank.Count) blanke Backlognummern meinen den KIT-Backlog:"
        Write-Host "        $($blank -join ', ')"
        Gelb "      Blank gelesen zeigen sie auf deinen eigenen Backlog — dort"
        Gelb '      steht etwas anderes oder gar nichts. Kit- davorsetzen.'
    }
    Gelb "  Nicht automatisch ersetzt (Lehre BL-12): In CLAUDE.md steckt deine"
    Gelb "  Arbeit. Die Zwei-Bahnen-Region ('Ablage:') bleibt ausdruecklich, wie"
    Gelb "  sie ist — dort ist das Nennen beider Bahnen die Aufgabe."
}

function Pytest-Mitschnitt {
    <#
      Faehrt die Regressionssuite und zeigt sie GLEICHZEITIG auf dem Bildschirm
      und im Log.

      Vorher ging alles nur ins Log (`*> $log`). Der Bildschirm zeigte dann
      "Selbsttest" und danach minutenlang nichts — im Feld sah das aus wie ein
      Haenger und war keiner: Die Suite lief, nur stumm. Einbahnig sind das rund
      drei bis vier Minuten, zweibahnig rund zwanzig. Wer das nicht weiss, bricht
      ab und haelt einen gesunden Installer fuer kaputt.

      Zwei Feinheiten, ohne die es nur halb wirkt:

      1. PYTHONUNBUFFERED. Schreibt Python nicht auf ein Terminal, sondern in
         eine Pipe, puffert es blockweise. Die Fortschrittszeilen kaemen dann in
         Schueben von einigen KB, also praktisch erst am Schluss — der Haenger
         waere nur kuerzer geworden, nicht weg. Die Variable schaltet das ab und
         wird danach auf ihren alten Wert zurueckgesetzt (auch wenn sie vorher
         gar nicht gesetzt war).
      2. Tee-Object schreibt ROH ins Log; die Einrueckung entsteht erst danach
         fuer den Bildschirm. Damit bleibt die Datei genau das, was pytest
         geschrieben hat — `Select-String '\d+ passed'` und `Get-Content -Tail`
         der Aufrufer lesen unveraendert weiter, und wer das Log verschickt,
         verschickt kein eingeruecktes Zerrbild.

      Rueckgabe: der Exit-Code von pytest.
    #>
    param([hashtable]$Pt, [string]$Log)

    # Nur fuer diesen Aufruf: `2>&1` macht aus Fremdprozess-stderr Fehlerobjekte
    # im Datenstrom. Unter 'Stop' waere die erste stderr-Zeile von pytest ein
    # Abbruch statt einer Ausgabe. Die Zuweisung gilt nur in dieser Funktion.
    $ErrorActionPreference = 'Continue'

    $gemerktPuffer = $env:PYTHONUNBUFFERED
    $env:PYTHONUNBUFFERED = '1'
    try {
        $vorab = $Pt.Vorab
        & $Pt.Befehl @vorab -q team/tests 2>&1 |
            Tee-Object -FilePath $Log |
            ForEach-Object { Write-Host "      $_" }
        return $LASTEXITCODE
    } finally {
        if ($null -eq $gemerktPuffer) { Remove-Item Env:PYTHONUNBUFFERED -ErrorAction SilentlyContinue }
        else { $env:PYTHONUNBUFFERED = $gemerktPuffer }
    }
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
function Gitattributes-Abgleich {
    <#
      BL-136, dieselbe Bauart wie Gitignore-Abgleich und aus demselben Grund
      geschrieben. Das Kit-Repo haelt diese Regel seit Langem fuer sich selbst;
      die ZIELPROJEKTE bekamen nie eine .gitattributes. Sie schuetzte damit
      genau dort nicht, wo das Kit im Feld laeuft.

      Der Fall entsteht NICHT bei der Installation — der Installer schreibt mit
      LF. Er entsteht beim naechsten Klon oder Checkout, unter Git for Windows
      mit dem Auslieferungswert core.autocrlf=true: Dann traegt jede .sh CRLF,
      an die Shebang-Zeile haengt sich ein Wagenruecklauf, und bash sucht einen
      Interpreter, dessen Name auf genau dieses unsichtbare Zeichen endet. Die
      Meldung lautet "bad interpreter" und sieht nach einer kaputten
      Installation aus. Weit weg von der Ursache, auf einer anderen Maschine,
      oft Wochen spaeter.

      Ergaenzt wird nur bei der ERSTINSTALLATION, gemeldet beim Update — die
      Datei gehoert dem Projekt.
    #>
    param([ValidateSet('ergaenzen', 'melden')][string]$Modus)
    $fragment = Join-Path $KIT 'bootstrap\gitattributes.fragment'
    $datei = Join-Path $Ziel '.gitattributes'
    $vorhanden = if (Test-Path $datei) { [System.IO.File]::ReadAllText($datei) } else { "" }

    if ($Modus -eq 'ergaenzen' -and $vorhanden -notmatch 'T\.E\.A\.M\.-Zeilenenden') {
        Add-Content -Path $datei -Value ([System.IO.File]::ReadAllText($fragment)) -NoNewline
        Gruen "  [ok] .gitattributes ergaenzt"
        return
    }
    $bestand = @($vorhanden -split "`r?`n")
    $fehlende = @()
    foreach ($zeile in ([System.IO.File]::ReadAllLines($fragment))) {
        if (-not $zeile.Trim() -or $zeile.TrimStart().StartsWith('#')) { continue }
        if ($bestand -notcontains $zeile) { $fehlende += $zeile }
    }
    if ($fehlende.Count -eq 0) {
        Gruen "  [ok] .gitattributes enthaelt den Block vollstaendig"
        return
    }
    Gelb "  [!] .gitattributes liegt $($fehlende.Count) Zeile(n) hinter der Vorlage — es fehlen:"
    foreach ($z in $fehlende) { Gelb "        $z" }
    Gelb "    Nicht automatisch ergaenzt (die Datei gehoert dem Projekt) —"
    Gelb "    nachtragen mit:"
    Gelb "      `"$($fehlende -join "``n")`" | Add-Content `"$datei`""
    Gelb "    Danach EINMAL neu einlesen, sonst wirkt es erst beim naechsten"
    Gelb "    Klon:  git -C `"$Ziel`" add --renormalize ."
}

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

function Python-Aus-Config {
    <#
      Der Interpretername, auf den eine INSTALLIERTE Konfiguration zeigt.
      Gelesen wird die Werkzeugzeile, nicht die Variable: In der .sh kann sie
      auf $TEAM_PYTHON zeigen (dann wird der eine Zeile hoeher aufgeloest), in
      der .ps1 steht der Name direkt im Default von Team-Wert.
    #>
    param([string]$Pfad)
    $text = [System.IO.File]::ReadAllText($Pfad)
    if ($text -notmatch '[-:"''$ ]([A-Za-z0-9_.]+) team/tools/kosten\.py') { return '' }
    $name = $Matches[1]
    if ($name -eq 'TEAM_PYTHON') {
        # Der optionale Wagenruecklauf vor dem Zeilenanker: Eine
        # team.config.sh, die unter Windows liegt, hat CRLF. .NET liest die
        # Datei roh, und der Anker im Mehrzeilenmodus steht VOR dem
        # Zeilenvorschub, also HINTER dem Wagenruecklauf. Ohne ihn findet der
        # Ausdruck die Zeile auf genau der Plattform nicht, fuer die er
        # gebaut ist.
        if ($text -match '(?m)^TEAM_PYTHON="\$\{TEAM_PYTHON:-(.*)\}"\r?$') { $name = $Matches[1] }
        else { return '' }
    }
    return $name
}

function Python-Abgleich {
    <#
      BL-133, derselbe Schnitt wie BL-109 bei der .gitignore: "-Update fasst
      team.config.* nicht an" ist richtig; "sieht sie gar nicht an" war es
      nicht.

      Ein Projekt, das vor BL-122/BL-131 eingerichtet wurde, traegt in BEIDEN
      Konfigurationen den Namen `python3` — die Vorlagen hatten damals gar
      keinen Platzhalter, es gab nichts zu fuellen. Unter Windows ist dieser
      Name nicht abwesend, sondern BELEGT: der App-Execution-Alias aus dem
      Microsoft Store. Er startet, schreibt "Python was not found" und endet
      mit 49.

      Die Wirkung ist deshalb keine Fehlermeldung, sondern eine LEERE Zahl.
      `.\team-status.ps1 -Budget` zeigte "Ralph-Logs (Bau, o. Archiv):
      USD" — nicht null, nicht Fehler, leer. Der Kostenpfad war seit dem
      Installationstag tot, und jedes Update meldete Erfolg.

      Geprueft wird der START, nicht die Existenz (Lehre BL-122). Gemeldet,
      nicht repariert: Die Konfiguration traegt Projektdaten, und der Nachtrag
      steht als kopierbare Zeile daneben.
    #>
    $kaputt = $false
    $gefunden = $false
    foreach ($name in @('team.config.sh', 'team.config.ps1')) {
        $pfad = Join-Path $Ziel $name
        if (-not (Test-Path $pfad)) { continue }
        $gefunden = $true
        $interpreter = Python-Aus-Config $pfad
        if (-not $interpreter) {
            Gelb "  [!] ${name}: kein Interpretername auffindbar — bitte die Zeile"
            Gelb "      mit team/tools/kosten.py von Hand ansehen."
            continue
        }
        $laeuft = $false
        if (Get-Command $interpreter -ErrorAction SilentlyContinue) {
            try {
                & $interpreter -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 8) else 1)' 2>$null | Out-Null
                $laeuft = ($LASTEXITCODE -eq 0)
            } catch { $laeuft = $false }
        }
        if ($laeuft) {
            Gruen "  [ok] ${name}: '$interpreter' startet und ist Python 3.8+"
            continue
        }
        $kaputt = $true
        Rot  "  [x] ${name}: '$interpreter' antwortet auf dieser Maschine nicht."
        $hier = Finde-Python
        if ($hier) { Gelb "      Hier laeuft Python unter dem Namen '$hier'." }
        else       { Gelb "      Es liess sich auch kein anderer Name finden — Python fehlt."; $hier = 'python' }
        Gelb "      Nachtragen (-Update fasst die Datei nicht an):"
        if ($name -eq 'team.config.sh') {
            Gelb "        TEAM_PYTHON=`"`${TEAM_PYTHON:-$hier}`""
            Gelb "        TEAM_BEUTEBUCH_TOOL=`"`${TEAM_BEUTEBUCH_TOOL:-`$TEAM_PYTHON team/tools/beutebuch.py}`""
            Gelb "        TEAM_KOSTEN_TOOL=`"`${TEAM_KOSTEN_TOOL:-`$TEAM_PYTHON team/tools/kosten.py}`""
        } else {
            Gelb "        `$TEAM_BEUTEBUCH_TOOL = Team-Wert 'TEAM_BEUTEBUCH_TOOL' '$hier team/tools/beutebuch.py'"
            Gelb "        `$TEAM_KOSTEN_TOOL    = Team-Wert 'TEAM_KOSTEN_TOOL'    '$hier team/tools/kosten.py'"
        }
    }
    if (-not $gefunden) { Gelb "  [!] keine Konfiguration gefunden" }
    return (-not $kaputt)
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
    # im Feld ein 12-USD-Fix an beutebuch.py verloren.
    #
    # Zwei Ausnahmen, beide aus demselben Grund: Briefings UND TEAM.md werden
    # nach dem Kopieren gerendert. Ihre installierte Fassung weicht deshalb
    # IMMER von der Kit-Fassung ab — die Platzhalter sind dort gefuellt. Ein
    # Warner, der bei jedem Lauf dieselben Dateien meldet, erzieht dazu, ihn zu
    # ueberlesen; dann geht der echte Fund darin unter (BL-175).
    if ($Immer -and (Test-Path $zielDatei) -and
        $Rel -notlike 'team/prompts/*' -and $Rel -ne 'TEAM.md') {
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

    # BL-147: Welche Bahn ein Projekt faehrt, sagt die ABLAGE — nicht der
    # Schalter, den beim Update gerade niemand tippt. Bis hierher galt der
    # Umkehrschluss: Ein Update ohne Schalter machte das Projekt "wieder
    # vollstaendig" (BL-119) und legte die zweite Bahn dazu. Als Rueckweg aus
    # einer Abwahl gedacht — im Feld ist es der Normalfall geworden, und der
    # Normalfall will keine zweite Bahn.
    #
    # Feld A, 2026-08-22: Ein Routine-Update legte 21 pwsh-Dateien in ein
    # reines Bash-Projekt. Untracked, unbestellt, und weil sie im Baum lagen,
    # fuhr die Testsuite ab da eine Bahn mit, die dort niemand faehrt (conftest
    # entscheidet an der ANWESENHEIT der Dateien). Auf dieser Bahn gilt es
    # spiegelbildlich: Ein Windows-Projekt bekommt keine .sh dazu.
    #
    # Der Rueckweg bleibt, er wird nur ausdruecklich: -BeideBahnen. Derselbe
    # Schnitt wie bei der Abwahl selbst ("kommt vom Anwender, nie vom
    # Installer") — nur jetzt in beide Richtungen.
    if (-not $NurBahn -and -not $BeideBahnen) {
        $hatBash = Test-BahnLiegtDa 'bash'
        $hatPwsh = Test-BahnLiegtDa 'pwsh'
        if ($hatBash -and -not $hatPwsh)      { $script:NurBahn = 'bash' }
        elseif ($hatPwsh -and -not $hatBash)  { $script:NurBahn = 'pwsh' }
        if ($script:NurBahn) {
            # Setze-Werte laeuft weiter unten und liest $script:NurBahn — die
            # Regeltexte bekommen ihre Pfade damit aus der ERKANNTEN Bahn.
            # Sonst nennt der Systemprompt jeder Rolle Dateien, die es hier
            # nicht gibt (BL-139).
            Gruen "  [ok] Einbahnige Ablage erkannt: nur die $($script:NurBahn)-Bahn (BL-147)"
            Write-Host "    Das Update haelt sie einbahnig und legt keine Dateien der"
            Write-Host "    anderen Bahn dazu. Zweibahnig machen (ausdruecklich):"
            Write-Host "      pwsh -File '$KIT\pwsh\install.ps1' '$Ziel' -Update -BeideBahnen"
        }
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

    # BL-52: Ein Projekt von vor 2.6.0 kennt TEAM_WEITERER_CODE nicht, und
    # -Update fasst die Konfiguration bewusst nicht an. Der Hinweis kommt nur,
    # wenn in der Projektwurzel ueberhaupt fremder Code liegt — sonst waere er
    # in jedem gruenen Projekt Rauschen (BL-14).
    #
    # BL-155: Diese Haelfte fehlte auf der pwsh-Bahn GANZ — nicht ungeprueft,
    # sondern ungebaut. Ein einbahnig-pwsh installiertes Bestandsprojekt erfuhr
    # damit nie, dass sein Einstiegspunkt in der Wurzel ausserhalb des
    # Pruefumfangs liegt, und genau so wird unter Windows installiert.
    if (-not (Konf 'TEAM_WEITERER_CODE' '')) {
        # BL-154: Gefragt wird das KIT, nicht eine abgeschriebene Namensliste.
        # Was in bash\entry\ oder pwsh\entry\ liegt, ist ein Entrypoint des
        # Kits und damit kein Projektcode. Eine eigene Liste an dieser Stelle
        # waere die Abschrift, die auf der bash-Bahn gerade abgeschafft wurde —
        # nur umgezogen, und ab dem naechsten neuen Entrypoint wieder falsch.
        $wurzelCode = @()
        foreach ($f in (Get-ChildItem -LiteralPath $Ziel -File)) {
            # Punktdateien fallen raus — .ralph-state, .budget-ledger,
            # .gitignore, .gitattributes sind der Zustand des Teams und nicht
            # der Code des Projekts. In der bash-Fassung erledigt das die
            # Shell nebenbei (`"$ZIEL"/*` fasst keine Punktdatei an); hier
            # muss es DASTEHEN, denn eine Punktdatei traegt unter Windows kein
            # Hidden-Attribut und Get-ChildItem liefert sie ganz normal mit.
            # Ohne diese Zeile meldete das Update den eigenen Zustand des
            # Teams als ungepruefen Projektcode — eine Warnung in jedem
            # gruenen Projekt, also genau der Fehler aus BL-154/BL-14.
            if ($f.Name.StartsWith('.')) { continue }
            if ((Test-Path (Join-Path $KIT "bash\entry\$($f.Name)")) -or
                (Test-Path (Join-Path $KIT "pwsh\entry\$($f.Name)"))) { continue }
            # Doku und Konfigdateien greift kein Red Team an. Alles andere MIT
            # Endung ist Code, der heute ausserhalb des Pruefumfangs liegt.
            if ($f.Name -like 'LICENSE*' -or $f.Name -eq 'Makefile') { continue }
            if ($f.Name -match '(?i)\.(md|toml|cfg|ini|txt|json|ya?ml)$') { continue }
            if ($f.Name -notmatch '\.') { continue }
            $wurzelCode += $f.Name
        }
        if ($wurzelCode) {
            Kopf "Pruefumfang endet an ${Produktivcode} (BL-52)"
            Write-Host "  Ungeprueft in der Wurzel: $($wurzelCode -join ' ')"
            Gelb "  Das Red Team prueft ausschliesslich ${Produktivcode} — Einstiegs-"
            Gelb "  punkte und Build-Skripte daneben sieht es nie, und ein sauberer"
            Gelb "  Sweep liest sich trotzdem wie ein sauberes Projekt."
            # Die Abhilfe nennt die Datei, die dieses Projekt WIRKLICH hat, und
            # die Schreibweise, die dort gilt. Die bash-Fassung sagt fest
            # team.config.sh — in einer einbahnig-pwsh-Ablage waere das ein
            # Verweis auf eine Datei, die es nicht gibt.
            Gelb "  Abhilfe ($konfQuelle, -Update fasst sie nicht an):"
            if ($konfQuelle -eq 'team.config.ps1') {
                Gelb "    `$TEAM_WEITERER_CODE = Team-Wert 'TEAM_WEITERER_CODE' '<pfade>'"
            } else {
                Gelb "    TEAM_WEITERER_CODE=`"`${TEAM_WEITERER_CODE:-<pfade>}`""
            }
        }
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
        $commitEntscheid = 'Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Stakeholder führt sie aus.'
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

    # BL-175: TEAM.md ist Kit-Doku, keine Projektdatei — und fiel bis
    # hierher durch JEDES Update. Geschrieben wurde sie nur bei der
    # Erstinstallation; in der Liste "Unangetastet geblieben (Projektdaten)"
    # weiter unten steht sie auch nicht. Sie fiel zwischen beide Listen, und
    # das faellt nicht auf: Eine veraltete Anleitung sieht aus wie eine
    # Anleitung.
    #
    # Der Schaden ist zweigeteilt, und der zweite Teil ist der schwerere:
    #
    #   1. Die Bedienungsanleitung eines aktualisierten Projekts bleibt auf dem
    #      Stand des Einzugstags. Exit-Codes, Befehle, Fehlersuche — alles, was
    #      das Kit seither gelernt hat, kommt dort nie an.
    #   2. In einer EINBAHNIGEN Ablage nennt die alte Fassung die ABGEWAEHLTE
    #      Bahn. Im Feld standen in einer -NurPwsh-Installation 15 tote
    #      .sh-Pfade in TEAM.md; der Text schickte jeden Leser an Dateien, die
    #      es dort nicht gibt. Das ist genau der Befund, den BL-139 fuer die
    #      Vorlagen abgestellt hat — TEAM.md blieb uebrig, weil die Reparatur
    #      am Rendern ansetzte und diese Datei nie neu gerendert wurde.
    #
    # CLAUDE.md bleibt bewusst aussen vor. Die traegt Projektarbeit — gefuellte
    # TODO-Stellen, projekteigene Regeln — und gehoert zu den Projektdaten.
    # TEAM.md traegt keine: Sie wird gerendert und sonst nicht angefasst.
    Kopiere (Join-Path $KIT 'bootstrap\TEAM.md') 'TEAM.md' -Immer
    Fuelle-Datei (Join-Path $Ziel 'TEAM.md')

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

    # BL-136: dieselbe Bauart, dieselbe Begruendung. Ein Projekt ohne diese
    # Regel checkt seine .sh unter Windows mit CRLF aus, und jeder Aufruf
    # endet mit "bad interpreter" — weit weg von der Ursache.
    Kopf ".gitattributes gegen die Vorlage (BL-136)"
    Gitattributes-Abgleich melden

    # BL-133: dieselbe Bauart wie die Zeile darueber — was -Update nicht
    # anfasst, muss es trotzdem ANSEHEN. Ein Interpretername, der auf dieser
    # Maschine nicht startet, macht den Kostenpfad tot und die Anzeige leer,
    # ohne je einen Fehler zu melden.
    Kopf "Interpreter der Team-Werkzeuge (BL-131/BL-133)"
    Python-Abgleich | Out-Null

    # BL-133: Die Abwahl einer Bahn wirkt bisher nur bei der ERSTinstallation.
    # Test-BahnAbgewaehlt laesst den Installer die Dateien der anderen Bahn
    # ueberspringen — was schon daliegt, bleibt liegen. Fuer ein bestehendes
    # zweibahniges Projekt heisst -NurPwsh beim Update also "ab jetzt nicht
    # mehr aktualisieren", nicht "weg damit". Der Unterschied ist folgenreich:
    # Die Testsuite entscheidet an der ANWESENHEIT der Dateien, welche Bahn
    # sie faehrt (conftest: bahnen_in_der_ablage) — sie faehrt also weiter
    # eine Bahn, die der Anwender gerade abgewaehlt hat, mit einer Bibliothek,
    # die von diesem Update an veraltet.
    #
    # Geloescht wird trotzdem nichts (Lehre BL-12: Ein pauschales Loeschen des
    # Installers hat im Feld einen projekteigenen Test mitgenommen). Genannt
    # wird es, mit dem Befehl daneben.
    if ($script:NurBahn) {
        # Gezaehlt wird nur, was das KIT ausliefert (BL-147, dieselbe
        # Ueberlegung wie bei der Erkennung): Ein projekteigenes deploy.ps1
        # gehoert nicht der abgewaehlten Bahn, und ein "git rm" darauf waere
        # ein Rat, der fremde Arbeit loescht.
        $reste = @()
        $andereBahn = if ($script:NurBahn -eq 'pwsh') { 'bash' } else { 'pwsh' }
        foreach ($d in (Get-KitBahnDateien $andereBahn)) {
            if (Test-Path (Join-Path $Ziel "$($d.Ordner)$($d.Name)") -PathType Leaf) {
                $reste += "$($d.Ordner)$($d.Name)"
            }
        }
        if ($reste.Count) {
            Kopf "Abgewaehlte Bahn liegt noch da (BL-119/BL-133)"
            $schalter = if ($script:NurBahn -eq 'pwsh') { '-NurPwsh' } else { '-NurBash' }
            Write-Host "  $schalter hat diese Dateien nicht mehr aktualisiert,"
            Write-Host "  aber auch nicht entfernt:"
            foreach ($r in $reste) { Write-Host "    - $r" }
            Gelb "  Solange sie liegen, faehrt .\team-test.ps1 die andere Bahn"
            Gelb "  weiter — mit einer Bibliothek, die ab jetzt veraltet. Entfernen"
            Gelb "  (bewusst nicht automatisch, Lehre BL-12):"
            Gelb "    git -C '$Ziel' rm $($reste -join ' ')"
        }
    }

    Melde-VeraltetenRegeltext

    # BL-178: Diesen Block hatte NUR install.sh — auf einer reinen pwsh-Ablage,
    # unter Windows der Normalfall, bekam ihn also niemand je zu sehen.
    #
    # Doku-Dateien tragen Projektanpassungen (gefuellte TODOs, eigene
    # Abschnitte) und werden deshalb NICHT ueberschrieben. Der Mensch muss aber
    # erfahren, dass sich die Kit-Fassung geaendert hat — sonst laufen die
    # REGELN im Projekt der Mechanik hinterher, und das war die Haelfte des
    # BL-4-Fehlers. Es ist dieselbe Gattung wie BL-145 ("gruen bedeutet auf den
    # beiden Bahnen verschieden viel"), nur bei den REGELN statt bei den Tests.
    # `Feld B` ist pwsh-only, ist mehrfach aktualisiert worden und hat diese
    # Meldung nie bekommen — ein Teil der Antwort darauf, warum die kaputte
    # CLAUDE.md dort so lange unbemerkt blieb (BL-177).
    #
    # PORTIERUNG, KEIN NEUENTWURF: Die bash-Fassung ist erprobt und traegt ihre
    # Feldlehren im Quelltext. Verglichen wird die MIT DENSELBEN WERTEN
    # gerenderte Kit-Vorlage gegen die installierte Datei — sonst meldet der
    # Abgleich immer eine Abweichung (gefuellte gegen ungefuellte Platzhalter)
    # und wird zur Warnung, die man wegklickt (BL-14).
    Kopf "Bitte von Hand abgleichen"
    $abgleich = 0
    # Gerendert wird in den TEMP-Bereich, NICHT ins Projekt: Eine uncommittete
    # Datei ausserhalb der Whitelist sieht fuer den Read-Only-Guard aus wie ein
    # Regelbruch.
    $abgleichDir = Join-Path ([System.IO.Path]::GetTempPath()) `
                             ("team-kit-abgleich-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Force -Path $abgleichDir | Out-Null
    foreach ($paar in @(
        @{ Quelle = 'bootstrap/TEAM.md';           Name = 'TEAM.md' },
        @{ Quelle = 'bootstrap/CLAUDE.md.vorlage'; Name = 'CLAUDE.md' })) {
        $installiert = Join-Path $Ziel $paar.Name
        if (-not (Test-Path $installiert -PathType Leaf)) { continue }
        $gerendert = Join-Path $abgleichDir $paar.Name
        Copy-Item (Join-Path $KIT $paar.Quelle) $gerendert -Force
        Fuelle-Datei $gerendert
        # Die Begruendung zu Zeilenenden und Mengenvergleich steht bei
        # Abgleich-Unterschiede — dort, wo sie auch unter Test steht.
        $unterschied = Abgleich-Unterschiede $gerendert $installiert
        if ($unterschied.Count) {
            Write-Host "  ! $($paar.Name) weicht von der Kit-Fassung ab ($($unterschied.Count) Zeilen)"
            # Der genannte Befehl muss AUF DIESER BAHN ausfuehrbar sein. Ein
            # `diff`-Aufruf, den Windows nicht kennt, ist die Bauart BL-44
            # (angekuendigt, aber nicht am wirksamen Ort ausfuehrbar) — und
            # genau der Fehler, den die bash-Fassung schon einmal gemacht hat.
            # Es ist WOERTLICH derselbe Aufruf, den Abgleich-Unterschiede eine
            # Zeile hoeher gefahren hat: Wer hier ein anderes Bild saehe als
            # der Installer, suchte den Fehler an der falschen Stelle.
            Write-Host "      Compare-Object (Get-Content -LiteralPath '$gerendert') (Get-Content -LiteralPath '$installiert')"
            $abgleich++
        } else {
            Remove-Item -LiteralPath $gerendert -Force
        }
    }
    if ($abgleich -eq 0) {
        Remove-Item -LiteralPath $abgleichDir -Force -Recurse -ErrorAction SilentlyContinue
        Gruen "  [ok] nichts offen"
    } else {
        # Ohne diesen Absatz ist der Block eine Warnung, die man wegklickt
        # (BL-14): Bei CLAUDE.md ist eine Abweichung der NORMALFALL, und wer
        # das nicht weiss, haelt den Befund fuer Rauschen.
        Gelb "  Bei CLAUDE.md ist eine Abweichung normal (Projektanpassungen,"
        Gelb "  gefuellte TODOs). Entscheidend ist, ob dir REGELN aus der neuen"
        Gelb "  Kit-Fassung fehlen — die Mechanik ist aktualisiert, die Regeln"
        Gelb "  im Projekt sind es nicht (das war die Haelfte von BL-4)."
        Write-Host "  Die gerenderte Kit-Fassung liegt unter $abgleichDir\ bereit;"
        Write-Host "  sie traegt bereits deine Werte. Temporaer — nach dem Abgleich"
        Write-Host "  loeschen. Behalte deine Projekt-Spezifika und eigene Regeln,"
        Write-Host "  uebernimm den Rest."
    }

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
            $rc = Pytest-Mitschnitt -Pt $pt -Log $log
            if ($rc -eq 0) {
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
    'Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Stakeholder führt sie aus.'
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
Gitattributes-Abgleich ergaenzen

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
        $rc = Pytest-Mitschnitt -Pt $pt -Log $log
        if ($rc -eq 0) {
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

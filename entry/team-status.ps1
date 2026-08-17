<#
  team-status.ps1 — Monitoring-Dashboard der T.E.A.M.-Vollautomatik.
  Zeigt Kaskaden-Stand, Beutebuch-Zaehlung, Kosten, Sperr-Status und letzte
  Aktivitaet. Einmalig oder als Live-Ansicht.

  Aufruf:  .\team-status.cmd            einmalige Momentaufnahme
           .\team-status.cmd --watch    Live (Refresh alle 5 s)
           .\team-status.cmd --budget   Kumulierter Kontostand (Ledger + Logs)
           .\team-status.cmd --architekt-abschluss <USD> <domaene> ["<notiz>"]
           .\team-status.cmd --akteur-abschluss <rolle> <auth> <USD> <domaene> ["<notiz>"]
           .\team-status.cmd --rollen-abschluss <kaskade> <domaene> ["<notiz-rollen>"] ["<notiz-bau>"] [--addieren|--ersetzen]
           .\team-status.cmd --ledger-pruefen [--kaskade N]
           .\team-status.cmd --altlast [N]
           .\team-status.cmd --beutebuch-archivieren [--dry-run]
#>
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
Import-Module ./team/lib.psm1 -Force -DisableNameChecking

$ralphCapWert = team_ralph_cap

function Status-ArchitektZeile {
    <#
      "beschriftung<TAB>USD" der Architekt-Kennzahl — EINE Quelle fuer BEIDE
      Ansichten (Momentaufnahme und --budget).

      BL-18 (Feld platformer, Closeout K3): Der Zusatz "nicht im Gesamt
      enthalten" stand in --budget UNBEDINGT — er gilt aber nur fuer den Modus
      "geschaetzt". Im Modus "echt" stammt der Wert aus einer Ledger-Zeile
      DIESER Kaskade, und die summiert der Kontostand mit. Der Modus schaltet
      ausgerechnet beim Kaskaden-Abschluss um, also genau dann, wenn die Zahl
      abgelesen und weitergegeben wird: Im Feld haette der beim Wort genommene
      Kontostand 81.27 statt 71.57 USD ergeben, 13 % zu viel.

      Zweiter Teil desselben Befunds: Der Wert ist KASKADENSCHARF, waehrend die
      Zeilen daneben lebenslang kumulieren. Die Beschriftung nennt den
      Bezugsrahmen deshalb ausdruecklich ("K3").
    #>
    $teile = (team_architekt_stand) -split "`t"
    $usd = $teile[0]
    $status = if ($teile.Count -ge 2) { $teile[1] } else { 'geschätzt' }
    $kaskade = team_architekt_kaskade
    $bezug = if ($status -eq 'echt') { 'im Gesamt enthalten' } else { 'nicht im Gesamt enthalten' }
    $rahmen = if ($kaskade) { "K$kaskade " } else { '' }
    Write-Output "Architekt $rahmen($status, $bezug)`t$usd"
}

function Status-Einmal {
    [Console]::Out.WriteLine('════════════════════════════════════════════════════════')
    [Console]::Out.WriteLine("  T.E.A.M.-Status — $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    [Console]::Out.WriteLine('════════════════════════════════════════════════════════')

    # Kaskade
    $stufe = '?'
    if (Test-Path '.ralph-state') { $stufe = ((Get-Content -TotalCount 1 '.ralph-state') -replace '\s', '') }
    $capAnzeige = if ($ralphCapWert) { $ralphCapWert } else { '?' }
    [Console]::Out.WriteLine("  Kaskade : nächste Stufe $stufe / Cap $capAnzeige")
    if ($ralphCapWert -match '^\d+$' -and [int]$ralphCapWert -ne 0 -and
        $stufe -match '^\d+$' -and [int]$stufe -gt [int]$ralphCapWert) {
        [Console]::Out.WriteLine('            → Bau abgeschlossen (Ralph hat Feierabend).')
    }

    # Sperre — hier zeigt sich der Windows-Zweig von seiner besseren Seite: Der
    # Oeffnungsversuch mit FileShare::None ist eine echte Probe, waehrend die
    # Bash-Fassung auf ein kooperatives flock angewiesen ist.
    $laeuft = $false
    if (Test-Path '.team-loop.lock') {
        try {
            $s = [System.IO.File]::Open('.team-loop.lock', [System.IO.FileMode]::Open,
                 [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
            $s.Close()
        } catch { $laeuft = $true }
    }
    if ($laeuft) { [Console]::Out.WriteLine('  Pipeline: 🟢 läuft gerade (Sperre gehalten)') }
    else { [Console]::Out.WriteLine('  Pipeline: ⚪ idle') }

    # Beutebuch
    [Console]::Out.WriteLine('  ──────── Beutebuch ────────')
    $counts = @(Team-Werkzeug $TEAM_BEUTEBUCH_TOOL @('count') 2>$null | Where-Object { $_ })
    # ACHTUNG, POWERSHELL-FALLE (gilt fuer jeden -f-Ausdruck in dieser Datei):
    # Der Formatausdruck braucht EIGENE Klammern. In
    # [Console]::Out.WriteLine(...) ist das Komma der Argumenttrenner der
    # METHODE, nicht der Array-Operator — `WriteLine('{0} {1}' -f $a, $b)` wird
    # zu `WriteLine(('{0} {1}' -f $a), $b)`, und -f bekommt ein Argument fuer
    # zwei Platzhalter. Das faellt erst zur Laufzeit auf, mitten in einem
    # Bericht, und sieht aus wie ein Datenfehler statt wie ein Syntaxproblem.
    if ($counts.Count) {
        foreach ($z in $counts) {
            $sp = $z -split "`t"
            $n = if ($sp.Count -ge 2) { $sp[1] } else { '' }
            [Console]::Out.WriteLine(('    {0,-32} {1}' -f $sp[0], $n))
        }
    } else {
        [Console]::Out.WriteLine('    (keine Funde)')
    }

    # Kosten — LEBENSLANG kumuliert, NICHT "dieser Lauf" (BL-24). Die
    # Aufschluesselung summiert alle *nicht archivierten* Logs; die
    # verlaessliche Gesamtzahl ist die Ledger-gestuetzte "Gesamt"-Zeile. Die
    # Pro-Lauf-Kosten stehen separat in der Vollautomatik-Schlusszeile.
    [Console]::Out.WriteLine('  ──────── Kosten (lebenslang kumuliert) ────────')
    $kRalph = team_kosten_summe @('.ralph-logs')
    $kTeam = team_kosten_summe @('.team-logs')
    $kGesamt = team_kontostand_gesamt
    $az = (Status-ArchitektZeile) -split "`t"
    [Console]::Out.WriteLine('    Ralph-Logs (Bau, o. Archiv)   : {0,9} USD' -f $kRalph)
    [Console]::Out.WriteLine('    Team-Logs (Fixe, o. Archiv)   : {0,9} USD' -f $kTeam)
    [Console]::Out.WriteLine(('    {0,-30}: {1,9} USD' -f $az[0], $az[1]))
    [Console]::Out.WriteLine('    Gesamt-Kontostand (inkl. Ledger): {0,9} USD' -f $kGesamt)

    # Letzte Aktivitaet
    [Console]::Out.WriteLine('  ──────── Letzte Commits ────────')
    $log = @(& git log --oneline -5 2>$null)
    if ($log.Count) { foreach ($z in $log) { [Console]::Out.WriteLine("    $z") } }
    else { [Console]::Out.WriteLine('    (kein Git-Log)') }
    # Neue Laeufe schreiben vollautomatik-*.log; aeltere (vor der Umbenennung
    # pock/wache -> halbautomatik/vollautomatik, BL-19) heissen noch wache-*.log.
    $letzte = @(Get-ChildItem -Path '.team-logs' -Filter '*.log' -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -like 'vollautomatik-*' -or $_.Name -like 'wache-*' } |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1)
    if ($letzte.Count) {
        [Console]::Out.WriteLine("  ──────── Vollautomatik (letzte 3 Zeilen: $($letzte[0].Name)) ────────")
        foreach ($z in @(Get-Content -Tail 3 $letzte[0].FullName)) { [Console]::Out.WriteLine("    $z") }
    }
    [Console]::Out.WriteLine('════════════════════════════════════════════════════════')
}

function Status-Budget {
    # Kumulierter Kontostand = historische Ledger-Basis plus aktuelle lokale
    # Logs, Abo/API getrennt ausgewiesen. Mit leeren Log-Ordnern ist die
    # Ausgabe exakt die Ledger-Basissumme.
    $split = (team_kosten_split @('.ralph-logs', '.team-logs')) -split "`t"
    $abo = if ($split.Count -ge 1 -and $split[0]) { [double]$split[0] } else { 0.0 }
    $api = if ($split.Count -ge 2 -and $split[1]) { [double]$split[1] } else { 0.0 }
    $lsplit = (team_ledger_split) -split "`t"
    $ledgerAbo = if ($lsplit.Count -ge 1 -and $lsplit[0]) { [double]$lsplit[0] } else { 0.0 }
    $ledgerApi = if ($lsplit.Count -ge 2 -and $lsplit[1]) { [double]$lsplit[1] } else { 0.0 }
    $ledgerGemischt = if ($lsplit.Count -ge 3 -and $lsplit[2]) { $lsplit[2] } else { '0.0000' }
    $gesamt = team_kontostand_gesamt
    $az = (Status-ArchitektZeile) -split "`t"

    # Der Ledger-Anteil wird zu den Live-Logs addiert, damit die beiden
    # Kopfzeilen nach einer Archivierung nicht mehr nur den Live-Teil zeigen.
    # "gemischt" bleibt eine eigene, ehrliche dritte Zeile statt geraten
    # aufgeteilt zu werden.
    $apiGesamt = ($api + $ledgerApi).ToString('F4', [cultureinfo]::InvariantCulture)
    $aboGesamt = ($abo + $ledgerAbo).ToString('F4', [cultureinfo]::InvariantCulture)

    [Console]::Out.WriteLine('════════════════════════════════════════════════════════')
    [Console]::Out.WriteLine("  T.E.A.M.-Kontostand — $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    [Console]::Out.WriteLine('════════════════════════════════════════════════════════')
    [Console]::Out.WriteLine("  real via API abgerechnet           : $apiGesamt USD")
    [Console]::Out.WriteLine("  Abo-Gegenwert (nicht abgerechnet)  : $aboGesamt USD")
    [Console]::Out.WriteLine("  gemischt (Ledger, nicht aufteilbar): $ledgerGemischt USD")
    [Console]::Out.WriteLine(('  {0,-35}: {1} USD' -f $az[0], $az[1]))
    [Console]::Out.WriteLine("  Gesamt (Basis + laufend), lebenslang: $gesamt USD")

    # Domaenengetrennte Ledger-Aufstellung (BL-29). Nur die committete Ledger
    # traegt eine Domaene je Zeile — Altzeilen davor zaehlen als
    # "unzugeordnet", NIE stillschweigend einer Domaene zugeschlagen.
    #
    # BL-9: Der Block erscheint nur, wenn dieses Projekt WIRKLICH mehrere
    # Domaenen fuehrt. Bei genau einer wiederholt er nur die Gesamtsumme. Eine
    # Zeile, die immer null zeigt, erzieht dazu, den ganzen Block zu ueberlesen.
    $ledgerGesamt = [double](team_ledger_summe)
    $domaenen = @(($TEAM_DOMAENEN -replace ',', ' ') -split '\s+' | Where-Object { $_ })
    if ($domaenen.Count -gt 1) {
        [Console]::Out.WriteLine('  ──────── Domänen (Ledger-Basis) ────────')
        $summeDomaenen = 0.0
        foreach ($d in $domaenen) {
            $wert = team_ledger_domaene $d
            [Console]::Out.WriteLine(('    📦 {0,-30}: {1} USD' -f $d, $wert))
            $summeDomaenen += [double]$wert
        }
        $unzugeordnet = ($ledgerGesamt - $summeDomaenen).ToString('F4', [cultureinfo]::InvariantCulture)
        [Console]::Out.WriteLine(('    ⚪ {0,-30}: {1} USD' -f 'unzugeordnet', $unzugeordnet))
    }

    # BL-23: KEIN B/A-Prozent. Der Gesamt-Kontostand (lebenslang) und der
    # Pro-Lauf-Deckel sind strikt getrennte Kennzahlen — sie gegeneinander zu
    # prozentuieren suggeriert faelschlich ein "gesprengtes Budget" (real 205 %
    # ausgeschoepft), obwohl die Pro-Lauf-Durchsetzung davon voellig unberuehrt
    # ist. Die Empfehlung wird nur informativ ausgewiesen.
    $empfehlung = team_budget_empfehlung
    if ($empfehlung) {
        $d = 0.0
        [double]::TryParse($empfehlung, [ref]$d) | Out-Null
        [Console]::Out.WriteLine("  Empf. Pro-Lauf-Deckel (naechster Lauf): $($d.ToString('F2',[cultureinfo]::InvariantCulture)) USD")
        [Console]::Out.WriteLine('  Hinweis: Pro-Lauf-Deckel gilt gegen die Kosten EINES Laufs,')
        [Console]::Out.WriteLine('           nicht gegen den kumulierten Gesamt-Kontostand oben.')
    }

    # Skizze D: Der Kontostand prueft ungefragt seine eigene Vollstaendigkeit
    # mit — und zwar gegen die archivierten Rohlogs, also gegen eine ANDERE
    # Quelle als die Zahlen darueber. Genau das fehlte bei BL-1/BL-4/BL-5: Alle
    # drei Berichte zogen ihre Kennzahl aus derselben Quelle wie der Fehler und
    # bestaetigten ihn deshalb, statt ihn zu zeigen. Bewusst nur ANZEIGE.
    $befunde = @(Team-Werkzeug $TEAM_KOSTEN_TOOL @('ledger-pruefen') 2>$null)
    $warnungen = @($befunde | Where-Object { $_ -like '`[WARNUNG`]*' })
    if ($warnungen.Count) {
        [Console]::Out.WriteLine('  ──────── Ledger-Konsistenz ────────')
        foreach ($z in $warnungen) { [Console]::Out.WriteLine("    $z") }
        [Console]::Out.WriteLine('    → Details: .\team-status.cmd --ledger-pruefen')
    }
    [Console]::Out.WriteLine('════════════════════════════════════════════════════════')
}

function Status-ArchitektAbschluss {
    # A1-Ersetzung (BL-28): haengt die echte Architekt-Ledger-Zeile an und
    # ersetzt dabei eine vorhandene Zeile derselben Kaskade (Idempotenz).
    param([string[]]$Argumente)
    $usd = if ($Argumente.Count -ge 1) { $Argumente[0] } else { '' }
    $domaene = if ($Argumente.Count -ge 2) { $Argumente[1] } else { '' }
    $notiz = if ($Argumente.Count -ge 3) { $Argumente[2] } else { '' }
    if (-not $usd -or -not $domaene) {
        Team-Fehler 'Nutzung: team-status --architekt-abschluss <USD> <domaene> ["<notiz>"]'
        return 1
    }
    $a = @('architekt-abschluss', '--usd', $usd, '--domaene', $domaene)
    if ($notiz) { $a += @('--notiz', $notiz) }
    Team-Werkzeug $TEAM_KOSTEN_TOOL $a
    return $LASTEXITCODE
}

function Status-AkteurAbschluss {
    <#
      Rollen-agnostische A1-Ersetzung (BL-33). BL-26: Der Wrapper las
      ausschliesslich die ersten fuenf Argumente — jedes weitere fiel
      kommentarlos weg. `--kaskade vor-23` erreichte das Werkzeug damit nie,
      das leitete die Nummer aus .ralph-plan ab und ersetzte im Feld eine
      fremde, abgeschlossene Zeile ueber 8,4678 USD. Verschaerfend: Ein
      veralteter .ralph-plan-Zeiger ist nach jedem Closeout der NORMALZUSTAND,
      die Fehlbuchung trifft also systematisch die zuletzt abgeschlossene
      Kaskade.

      Ein Argument, das mit -- beginnt, ist NIE die Notiz — sonst waere
      `… <domaene> --kaskade 22` als Notiztext "--kaskade" gebucht worden.
    #>
    param([string[]]$Argumente)
    if ($Argumente.Count -lt 4 -or -not $Argumente[0] -or -not $Argumente[1] -or
        -not $Argumente[2] -or -not $Argumente[3]) {
        Team-Fehler 'Nutzung: team-status --akteur-abschluss <rolle> <auth:abo|api> <USD> <domaene> ["<notiz>"] [weitere kosten.py-Schalter]'
        return 1
    }
    $rolle, $auth, $usd, $domaene = $Argumente[0..3]
    $rest = @()
    if ($Argumente.Count -gt 4) { $rest = @($Argumente[4..($Argumente.Count - 1)]) }
    $notiz = ''
    if ($rest.Count -and $rest[0] -and -not $rest[0].StartsWith('--')) {
        $notiz = $rest[0]
        $rest = if ($rest.Count -gt 1) { @($rest[1..($rest.Count - 1)]) } else { @() }
    }
    team_akteur_abschluss $rolle $auth $usd $domaene $notiz '.budget-ledger' '.' @rest
    return $LASTEXITCODE
}

function Status-RollenAbschluss {
    <#
      Kaskadenscharfer Abschluss BEIDER Kostenquellen (BL-4): .team-logs
      (Harry/Marv/Frank/Axel -> rolle=roles) UND .ralph-logs (Bau ->
      rolle=ralph). Zwei getrennte Ledger-Zeilen, EINE Bedienhandlung: Ralphs
      Baukosten fielen im Feld nur deshalb aus dem committeten Ledger, weil sie
      einen zweiten, nirgends vorgeschriebenen Befehl gebraucht haetten.

      Beide Verben laufen unabhaengig: Bricht einer ab (z. B. BL-5-Bestand),
      wird der andere trotzdem versucht und der Fehler am Ende gemeldet.

      BL-34: Die beiden Zeilen bekommen GETRENNTE Notizen. Fehlt die Bau-Notiz,
      wird sie aus dem Plannamen ABGELEITET — der Text des Menschen wird nicht
      mehr auf eine Zeile kopiert, die er nicht beschreibt.
    #>
    param([string[]]$Argumente)
    $kaskade = if ($Argumente.Count -ge 1) { $Argumente[0] } else { '' }
    $domaene = if ($Argumente.Count -ge 2) { $Argumente[1] } else { '' }
    if (-not $kaskade -or -not $domaene) {
        Team-Fehler 'Nutzung: team-status --rollen-abschluss <kaskade> <domaene> ["<notiz-rollen>"] ["<notiz-bau>"] [--addieren|--ersetzen]'
        return 1
    }
    $rest = @()
    if ($Argumente.Count -gt 2) { $rest = @($Argumente[2..($Argumente.Count - 1)]) }
    $notiz = ''
    $bauNotiz = ''
    if ($rest.Count -and $rest[0] -and -not $rest[0].StartsWith('--')) {
        $notiz = $rest[0]; $rest = if ($rest.Count -gt 1) { @($rest[1..($rest.Count - 1)]) } else { @() }
    }
    if ($rest.Count -and $rest[0] -and -not $rest[0].StartsWith('--')) {
        $bauNotiz = $rest[0]; $rest = if ($rest.Count -gt 1) { @($rest[1..($rest.Count - 1)]) } else { @() }
    }
    $modus = if ($rest.Count) { $rest[0] } else { '' }
    if ($modus -and $modus -notin @('--addieren', '--ersetzen')) {
        Team-Fehler "Unbekannter Modus '$modus' — erlaubt: --addieren, --ersetzen"
        return 1
    }
    # Nur ableiten, wenn der Mensch nichts eigenes gesagt hat. Bleibt die
    # Ableitung leer, schreibt kosten.py seinen eigenen Vorspann — ehrlich
    # unbeschriftet ist besser als falsch beschriftet.
    if (-not $bauNotiz) { $bauNotiz = team_bau_notiz }

    $rc = 0
    foreach ($verb in @('rollen-abschluss', 'ralph-abschluss')) {
        # BL-34: je Zielrolle der EIGENE Text, nie derselbe zweimal.
        $zeilenNotiz = if ($verb -eq 'ralph-abschluss') { $bauNotiz } else { $notiz }
        $a = @($verb, '--kaskade', $kaskade, '--domaene', $domaene)
        if ($zeilenNotiz) { $a += @('--notiz', $zeilenNotiz) }
        $a += '--archivieren'
        if ($modus) { $a += $modus }
        Team-Werkzeug $TEAM_KOSTEN_TOOL $a
        if ($LASTEXITCODE -ne 0) { $rc = $LASTEXITCODE }
    }
    return $rc
}

function Status-Altlast {
    <#
      Produktivdateien, die seit N Kaskaden (Default 5) in KEINEM Diff lagen.

      BL-40: Das Red Team prueft entlang des Diffs. Nie beruehrter Code ist
      damit der am schlechtesten gepruefte, und niemand weist darauf hin. Im
      Feld lagen BEIDE Funde einer Kaskade in Code, den sie nicht geschrieben
      hatte; dieselbe Datei lieferte in DREI aufeinanderfolgenden Kaskaden
      Funde — immer dann, wenn sie angefasst wurde. Gruendlichkeit korreliert
      also mit Aenderungshaeufigkeit, nicht mit Risiko.

      Bewusst nur eine KENNZAHL und kein automatischer Sweep: Die Kosten
      skalieren mit der Flaeche, und die Diff-Bindung ist der Grund, warum die
      Sweeps ueberhaupt bezahlbar sind.
    #>
    param([string[]]$Argumente)
    $n = if ($Argumente.Count -ge 1 -and $Argumente[0]) { [int]$Argumente[0] } else { 5 }
    # Als Zeitmarke dient der Add-Commit der N-letzten Kaskaden-Plandatei: Die
    # entsteht bei jeder Scharfschaltung genau einmal und ist damit die einzige
    # maschinell lesbare Kaskadengrenze im Repo.
    $marken = @(& git log --diff-filter=A --format='%H %ct' --reverse -- "${TEAM_PLAN_ORDNER}ralph-kaskade-*.md" 2>$null |
                Where-Object { $_ })
    if ($marken.Count -lt $n) {
        [Console]::Out.WriteLine("Altlast-Kennzahl: weniger als $n Kaskaden im Repo — noch keine Aussage moeglich.")
        return 0
    }
    $seit = [long](($marken[-$n] -split '\s+')[1])
    [Console]::Out.WriteLine("Produktivdateien ohne Diff seit den letzten $n Kaskaden:")
    $pfade = @($TEAM_PRODUKTIVCODE)
    if ($TEAM_WEITERER_CODE) { $pfade += @($TEAM_WEITERER_CODE -split '\s+' | Where-Object { $_ }) }
    $gefunden = 0
    foreach ($datei in @(& git ls-files -- @pfade 2>$null | Where-Object { $_ })) {
        $letzte = & git log -1 --format=%ct -- $datei 2>$null
        if (-not $letzte) { continue }
        if ([long]$letzte -lt $seit) {
            $datum = [DateTimeOffset]::FromUnixTimeSeconds([long]$letzte).LocalDateTime.ToString('yyyy-MM-dd')
            [Console]::Out.WriteLine("  $datei (zuletzt $datum)")
            $gefunden++
        }
    }
    if ($gefunden -eq 0) {
        [Console]::Out.WriteLine('  (keine — jede Produktivdatei war zuletzt im Diff)')
    } else {
        [Console]::Out.WriteLine("  $gefunden Datei(en). Kandidaten fuer einen Altlast-Sweep:")
        [Console]::Out.WriteLine('  $env:TEAM_REDTEAM_FOCUS = "Altlast-Sweep: <Datei(en) aus dieser Liste>"; .\harry.cmd')
    }
    return 0
}

# --- Argument-Verteilung ------------------------------------------------------
$rest = @()
if ($args.Count -gt 1) { $rest = @($args[1..($args.Count - 1)]) }

switch ($(if ($args.Count) { $args[0] } else { '' })) {
    '--budget' { Status-Budget; exit 0 }
    '--architekt-abschluss' { exit (Status-ArchitektAbschluss $rest) }
    '--akteur-abschluss'    { exit (Status-AkteurAbschluss $rest) }
    '--rollen-abschluss'    { exit (Status-RollenAbschluss $rest) }
    '--ledger-pruefen' {
        # Reicht durch (Skizze D). Exit 4 = Warnbefunde, 0 = sauber.
        Team-Werkzeug $TEAM_KOSTEN_TOOL (@('ledger-pruefen') + $rest)
        exit $LASTEXITCODE
    }
    '--altlast' { exit (Status-Altlast $rest) }
    '--beutebuch-archivieren' {
        # Bewusst NICHT in der Vollautomatik verdrahtet — ein laufender Sweep
        # darf nie unter seinen eigenen Funden rotieren. Rein manuelles
        # Abschluss-Werkzeug wie --rollen-abschluss.
        Team-Werkzeug $TEAM_BEUTEBUCH_TOOL (@('archiviere') + $rest)
        exit $LASTEXITCODE
    }
    '--watch' {
        while ($true) {
            Clear-Host
            Status-Einmal
            [Console]::Out.WriteLine('  (--watch: Refresh 5 s · Strg+C beendet)')
            Start-Sleep -Seconds 5
        }
    }
    default { Status-Einmal; exit 0 }
}

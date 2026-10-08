# Das Update ueberschreibt die lokale xdist-Pruefung der Selbstpruefung zum dritten Mal - bitte ins Kit uebernehmen

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-08-das-update-ueberschreibt-die-lokale-xdist-pruefung-der-selbs.md
      .\kit-melden.cmd ablegen  2026-10-08-das-update-ueberschreibt-die-lokale-xdist-pruefung-der-selbs.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-08-das-update-ueberschreibt-die-lokale-xdist-pruefung-der-selbs.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python-Dienst mit Electron-Oberfläche,
  rund 37 Kaskaden. Der Smoke-Test fährt pytest mit pytest-xdist (`-n auto --dist loadgroup`).

## Was passiert ist

`TEAM_SMOKE_TEST` enthält xdist-Optionen. Fehlt pytest-xdist im Interpreter des ersten Tokens,
bricht pytest schon am Kommandozeilenparser ab (`unrecognized arguments: -n`). Für
`team_quittung_selbstpruefung` ist das ein gewöhnliches Rot: Sie meldet „ROT, auch der zweite
Lauf war rot — kein Flackern" und schickt den Menschen auf Fehlersuche im Produktivcode, obwohl
nur ein Paket fehlt.

Das Projekt hat dafür am 2026-09-14 eine Prüfung in `team/lib.psm1` ergänzt
(`team_smoke_test_xdist_verfuegbar`, rund 35 Zeilen, aufgerufen vor dem Smoke-Lauf), dazu einen
Regressionstest im eigenen Testordner. Jedes Kit-Update ersetzt `team/lib.psm1`: am 2026-09-17
zweimal, am 2026-10-08 zum dritten Mal. Beim dritten Mal hat `Kit-BL-270` die alte Datei
gesichert und als abweichend gemeldet, das hat geholfen. Trotzdem war danach die Projekt-Suite
rot, weil der eigene Regressionstest die Funktion nicht mehr fand. Damit wäre das Gate der
nächsten Kaskade rot gewesen, ohne dass sich am Produkt etwas geändert hatte.

## Wo es steckt

`pwsh/lib.psm1`, `team_quittung_selbstpruefung`, Schritt (3) vor dem Smoke-Lauf, und das
Gegenstück in `bash/lib.sh`. Dieselbe Fehlerklasse kennt das Projekt schon von seinem eigenen
Lastlauf-Skript. Dort hat es einen eigenen Wächter, die zentrale Selbstprüfung hat keinen.

## Warum das jede Installation trifft

Jedes Projekt, dessen Smoke-Test `-n`/`--dist` trägt, hat diese Fehlerklasse. Die Prüfung gehört
an den zentralen Aufrufer im Kit, nicht ins Feld, wo sie jedes Update wieder entfernt.

## Was ich schon versucht habe

Lokal zum dritten Mal wiederhergestellt (2026-10-08). Geprüft wird jetzt der Befehl, der dort
wirklich läuft — seit `Kit-BL-232` kann das `TEAM_SMOKE_TEST_SCHNELL` sein. Vorschlag zur
Übernahme, pwsh-Fassung:

```powershell
function team_smoke_test_xdist_verfuegbar {
    param([string]$SmokeTest)
    $teile = @($SmokeTest -split '\s+' | Where-Object { $_ })
    if (-not $teile.Count) { return $true }
    $brauchtXdist = @($teile | Where-Object {
        $_ -eq '-n' -or $_ -eq '--dist' -or $_ -like '--dist=*'
    }).Count -gt 0
    if (-not $brauchtXdist) { return $true }
    $python = $teile[0]
    & $python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('xdist') else 1)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Team-Fehler "    ✗ TEAM_SMOKE_TEST verwendet pytest-xdist-Optionen (-n/--dist), aber"
        Team-Fehler "      pytest-xdist ist in '$python' nicht verfuegbar. Es wird deshalb NICHT"
        Team-Fehler "      automatisch quittiert -- installiere pytest-xdist oder setze"
        Team-Fehler "      TEAM_SMOKE_TEST ohne -n/--dist."
        return $false
    }
    return $true
}

# in team_quittung_selbstpruefung, direkt nach der Wahl von $smoke:
if (-not (team_smoke_test_xdist_verfuegbar $smoke)) { return $false }
```

Gefahren mit dem Regressionstest des Projekts: vorher 2 rot (Funktion fehlte), nachher 2 grün.
Die Kit-Tests zur Selbstprüfung (`test_bl110`) bleiben grün.

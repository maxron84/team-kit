# TEAM_GATE_DATEI wird nicht exportiert - die Gate-Meldung aus BL-256 stuerzt genau dann ab, wenn sie gebraucht wird

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1 plus Unreleased-Stand
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python und Electron, 25
  Kaskaden gebaut, rund 240 Testdateien.

## Was passiert ist

Ein Vollautomatik-Lauf endete mit rotem Gate — also in genau der Lage, für die
`BL-256` gebaut wurde. Statt der roten Tests kam das hier:

    [17:58:00] === LAUF BEENDET — GATE ROT ===
    [17:58:00]   Erste Meldung: <zeile aus der gate-datei>
    Get-Content: …\vollautomatik.ps1:546:34
    Line |
     546 |      foreach ($z in @(Get-Content $TEAM_GATE_DATEI | Where-Object …
         |                                   ~~~~~~~~~~~~~~~~
         | Cannot bind argument to parameter 'Path' because it is null.

**Und die Handlungsanweisung darunter kam mit einem Loch:**

    [17:58:01]   Nächster Schritt: den roten Baum reparieren. Ist er grün, gehört
    [17:58:01]    gelöscht — dann meldet sich der nächste Lauf wieder normal.

Zwischen „gehört" und „gelöscht" steht der Dateiname — `$TEAM_GATE_DATEI`
interpoliert zu Leerstring. **Der Satz sagt dem Menschen also nicht, was er
löschen soll**, und die Liste der roten Tests bekommt er gar nicht erst.

## Wo es steckt

`lib.psm1`:317 definiert

    $TEAM_GATE_DATEI = Team-Default 'TEAM_GATE_DATEI' '.team-gate-rot'

`Export-ModuleMember -Function * -Variable @( … )` (`lib.psm1`:2055) führt
rund 35 Variablen auf — `TEAM_LOCK_DATEI`, `TEAM_GUARD_LAUFZEIT`,
`TEAM_SMOKE_TEST` und andere —, **`TEAM_GATE_DATEI` steht nicht darunter.**

Damit gilt:

| Ort | sieht die Variable |
|---|---|
| `lib.psm1`:626–627 (im Modul) | **ja** — das Schreiben und Prüfen der Gate-Datei funktioniert |
| `vollautomatik.ps1`:546 und :552 (außerhalb) | **nein**, `$null` |

Deshalb schreibt der Loop die Gate-Datei korrekt, legt sie korrekt an und
stolpert erst beim **Vorlesen**. Die Mechanik ist heil, nur ihr Ausgang ist es
nicht.

**Dieselbe Bauform ist im Kit bereits einmal gefixt worden.** Unmittelbar in
derselben Exportliste steht der Kommentar zu `BL-182`, zweite Hälfte:
*„`TEAM_KIT_PFAD` stand in `team.config.ps1` und kam trotzdem nie an — die
Konfiguration wird ins MODUL geladen …"*. `BL-256` hat eine neue Variable
eingeführt und den Eintrag in dieselbe Liste vergessen.

## Warum das jede Installation trifft

`BL-256` existiert, damit ein Lauf sich **nicht** als fertig meldet, während
das Gate rot ist. Der Schreibpfad tut das auch. Aber der **Lesepfad** —
derjenige, der dem Menschen sagt, *welche* Tests rot sind und *welche Datei*
danach zu löschen ist — läuft außerhalb des Moduls und ist damit auf jeder
pwsh-Installation tot.

**Der Schaden ist nicht der Absturz, sondern der Zeitpunkt.** Die Meldung
feuert ausschließlich im roten Fall, also dann, wenn der Mensch sie am
dringendsten braucht und am wenigsten Zeit hat, im Kit-Quelltext
nachzuschlagen. Ein Anwender ohne Kenntnis der Interna bleibt mit einer
PowerShell-Ausnahme und einem Satz mit Loch zurück.

**Zur Einordnung, damit die Priorität stimmt:** Kein Datenverlust, keine
falsche Grün-Meldung — das Gate bleibt rot und der Lauf sagt das auch. Es ist
ein kaputter Diagnoseausgang, kein kaputtes Gate.

## Was ich schon versucht habe

**Lokal nichts gefixt** — der Befund sitzt in `lib.psm1` und verfällt beim
nächsten `--update`; in diesem Projekt dreimal nachgewiesen.

**Fix:** `'TEAM_GATE_DATEI'` in die Exportliste in `lib.psm1`:2055 aufnehmen.
Eine Zeichenkette.

**Zwei Vorschläge darüber hinaus, weil die Liste der Fehlermodus ist:**

1. **Die Liste prüfbar machen.** Eine Gegenprobe, die jede `$TEAM_*`-Variable,
   die außerhalb des Moduls gelesen wird, gegen die Exportliste hält, hätte
   `BL-182` und diesen Fall gefunden. Statisch machbar: Die Lesestellen stehen
   sämtlich in den Entrypoints.
2. **Oder die Liste abschaffen.** `Export-ModuleMember -Variable *` wäre eine
   Zeile und macht das Vergessen unmöglich. Falls die Aufzählung Absicht ist
   (Kapselung), gehört der Grund an die Liste — heute liest sie sich wie eine
   gewachsene Sammlung, und genau so verhält sie sich auch.

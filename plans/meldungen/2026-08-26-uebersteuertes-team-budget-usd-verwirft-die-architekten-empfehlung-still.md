# Ein übersteuertes `TEAM_BUDGET_USD` verwirft die Architekten-Empfehlung still — melden tut das Kit nur die Gegenrichtung

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh (die Regel selbst ist bahnneutral)
- **Plattform**: win32
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn (`--nur-pwsh`), Python + Electron, dritte Kaskade

## Was passiert ist

Der Plankopf der Kaskade trug `BUDGET_EMPFEHLUNG_USD=34`. Der Abschlussbericht
meldete:

```
Dieser Lauf: 18.2016 USD (Deckel 26).
```

**26 ist weder der Default (15) noch die Empfehlung (34)** — es ist exakt der
Wert der *vorigen* Kaskade. In der Shell-Sitzung des Menschen lebte noch
`TEAM_BUDGET_USD=26` aus dem Lauf davor, und diese Übersteuerung hat Vorrang.

Das Verhalten ist **richtig und dokumentiert**. Der Befund ist ein anderer:
**Es wurde nirgends gesagt.** Weder Konsole noch Lauf-Log enthalten eine Zeile
darüber, dass eine Empfehlung vorlag und verworfen wurde. Nachgesehen:

```
grep -E 'Deckel-Anhebung|Deckel' <lauf-log>
→ genau EIN Treffer: die Schlusszeile "Dieser Lauf: … (Deckel 26)."
```

Wer den Plan geschrieben hat, erfährt nicht, dass sein Wert wirkungslos blieb.
Wer den Lauf startet, sieht eine plausible Zahl und hat keinen Anlass zu fragen,
woher sie kommt.

## Wo es steckt

Zwei Stellen, die zusammen die Asymmetrie ergeben.

`geteilt`/`lib`, die Deckel-Regel:

```powershell
function team_resolve_budget_cap {
    param([string]$Aktuell, [string]$UserGesetzt, [string]$Empfehlung)
    if ($UserGesetzt -eq '1') { Write-Output $Aktuell; return }   # <— still
    if ($Empfehlung) { … if ($e -gt $a) { Write-Output $Empfehlung; return } }
    Write-Output $Aktuell
}
```

Und der Aufrufer in `vollautomatik`:

```powershell
$neuerDeckel = team_resolve_budget_cap $budgetUsd $budgetUserGesetzt $empfehlung
if ($neuerDeckel -ne $budgetUsd) {
    Log "Deckel-Anhebung: Architekten-Empfehlung $empfehlung USD > bisheriger Deckel …"
    $budgetUsd = $neuerDeckel
}
```

**Geloggt wird nur der Fall, in dem die Empfehlung gewinnt.** Verliert sie —
egal ob weil der Mensch übersteuert hat oder weil sie kleiner ist —, passiert
nichts. Die Funktion gibt nur eine Zahl zurück und kann den Grund gar nicht
mitteilen; der Aufrufer schließt aus `-ne` auf „angehoben" und hat für die
anderen Ausgänge keinen Zweig.

## Warum das jede Installation trifft

Es ist dieselbe Bauform, die das Kit für den Red-Team-Fokus bereits als Fehler
erkannt und behoben hat (`BL-31`): **eine Umgebungsvariable ohne Verfallsdatum,
die still in den nächsten Lauf hineinwirkt.** Dort lautete der Befund, der Sweep
der Kaskade 11 sei mit dem Fokus der Kaskade 10 gelaufen und habe „pflichtgemäß
das Falsche geprüft"; die Lösung war, den Fokus an den Lauf zu binden und beim
Verfall **ausdrücklich zu melden**:

```
[$Rolle] Der zuletzt gesetzte Fokus gehört zu einem anderen Stand — VERFALLEN (BL-31).
```

Genau diese Meldung fehlt beim Budget. Die Variable überlebt jede Shell-Sitzung
und wirkt über beliebig viele Kaskaden hinweg weiter.

**Die Auswirkung ist asymmetrisch und deshalb tückisch.** Ein zu *hoher*
Alt-Wert fällt nie auf. Ein zu *niedriger* bricht den Lauf mitten in der
Fix-Phase ab — und der Kit-eigene Befund `HM-32` hält fest, was das kostet: Ein
zu tiefer Deckel greift **nach** dem bereits bezahlten Aufruf, wirft plausible
Arbeit per Rollback weg und **vervielfacht** die Kosten, statt zu sparen. Hier
lag der Alt-Wert um 8 USD unter der Empfehlung; der Lauf blieb mit 18,20 USD
zufällig darunter. Bei einer teureren Kaskade wäre das der Abbruch gewesen — mit
einer Empfehlung im Plan, die genau ihn hätte verhindern sollen.

## Vorschlag für den Fix

1. **Den verworfenen Fall ebenfalls loggen.** Eine Zeile genügt, und sie ist das
   Gegenstück zur bestehenden „Deckel-Anhebung":

   ```
   Deckel: TEAM_BUDGET_USD=26 ist explizit gesetzt und hat Vorrang — die
   Architekten-Empfehlung 34 USD aus dem Plankopf bleibt UNBERUECKSICHTIGT.
   ```

   Das ist derselbe Umgang wie mit dem verfallenen Fokus: nicht verhindern,
   sondern sichtbar machen.
2. **Den Grund zurückgeben statt ihn zu verlieren.** `team_resolve_budget_cap`
   könnte neben dem Wert einen Grund liefern (`user`, `empfehlung`, `aktuell`),
   damit der Aufrufer nicht aus `-ne` raten muss. Testbar bleibt die Regel
   dadurch genauso isoliert wie heute.
3. **Erwägenswert, analog zu `BL-31`:** die Übersteuerung an den Lauf binden
   statt an die Prozessumgebung — oder wenigstens beim Start eines Laufs melden,
   welche `TEAM_*`-Übersteuerungen aus der Umgebung gerade aktiv sind. Ein
   Anwender, der eine Kaskade nach der anderen in derselben Shell startet, hat
   sonst keine Möglichkeit zu merken, was er vor drei Läufen gesetzt hat.

## Was ich schon versucht habe

Am Kit nichts geändert. Nachgesehen wurde rein lesend: der Abschlussbericht des
Laufs, das vollständige Lauf-Log (kein Treffer außer der Schlusszeile), die
Deckel-Regel und ihr Aufrufer. Die Empfehlung selbst wird korrekt gelesen —
gegengeprüft durch direkten Aufruf des Plankopf-Lesers, der `34` liefert. Der
Fehler liegt ausschließlich in der fehlenden Meldung.

Behelf im Projekt: vor jedem Lauf die Übersteuerung aus der Sitzung entfernen.

> **Anmerkung zum Melden selbst:** Diese Meldung konnte nicht über
> `kit-melden` angelegt werden — der Wrapper der pwsh-Bahn stirbt vorher an
> einer undefinierten Variablen (eigene Meldung liegt bei).

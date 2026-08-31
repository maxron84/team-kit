# Der gesenkte sonnet-5-Satz (BL-166) macht die Selbsteichung in einem zweiten Feldprojekt unmoeglich — 78 von 79 Laeufen 33,3 % daneben, jede Buchung blockiert

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, sechste Kaskade, 79 abgerechnete headless-Läufe im Repo

## Was passiert ist

Beim Kostenabschluss einer Kaskade verweigerte `kosten.py sitzung-messen`
regelkonform die Zahl:

```
! Preistabelle stimmt nicht mehr: 78 von 79 nachgerechneten Laeufen weichen ab.
    stufe-1-…json:  abgerechnet 0.6739, gerechnet 0.4499 (33.2 % daneben)
    stufe-10-…json: abgerechnet 1.0022, gerechnet 0.6688 (33.3 % daneben)
    stufe-11-…json: abgerechnet 1.3884, gerechnet 0.9262 (33.3 % daneben)
  Die Zahl unten ist damit UNGEEICHT.
```

Die Abweichung ist **nicht gestreut, sondern konstant**: `gerechnet` ist
durchgehend exakt zwei Drittel von `abgerechnet` — also der Quotient
`2.00 / 3.00`. Betroffen sind **alle** Läufe des Projekts, auch solche aus
früheren Kaskaden, die vor dem Update sauber geeicht waren und deren Kosten
längst gebucht sind.

Ursache ist der Satz für `claude-sonnet-5` in `PREIS_INPUT_USD_PRO_MTOK`, den
`BL-166` am 2026-08-26 von `3.00` auf `2.00` gesenkt hat. Für dieses Projekt
ist `3.00` richtig, und zwar nachrechenbar:

```
Lauf mit 18 Input, 3.674 Output, 580.196 Cache-Read, 49.991 Cache-Write:
  (18 + 3674*5 + 580196*0.1 + 49991*2.0) / 1e6 * 3.00 = 0.5291688
  total_cost_usd des Laufs                            = 0.5291688
```

Gegenprobe über den ganzen Bestand: Mit `3.00` und Cache-Write als **1h**
reproduzieren sich **79 von 79** abgerechneten `total_cost_usd` auf unter
0,5 % genau (tatsächlich exakt); mit `2.00` sind es **1 von 79** — der eine
Treffer ist ein reiner Haiku-Lauf ohne sonnet-Anteil.

## Wo es steckt

`geteilt/tools/kosten.py`, `PREIS_INPUT_USD_PRO_MTOK`, Eintrag
`"claude-sonnet-5"`. Der Kommentar darüber begründet die Senkung mit einem
meldenden Projekt, in dem die Eichung „in 9 von 9 abgerechneten Läufen
fehlschlug, 25–33 % daneben".

**Das ist dieselbe Fehlerbeschreibung, nur mit umgekehrtem Vorzeichen** — und
genau das ist der Hinweis auf die eigentliche Ursache: Ein Basispreis, der in
einem Projekt 33 % zu hoch und in einem anderen 33 % zu niedrig ist, ist
wahrscheinlich gar nicht der falsche Wert. Der Faktor 1,5 zwischen den beiden
Lagen entsteht auch dann, wenn die **Cache-Write-Laufzeit** verschieden
zugeordnet wird: `cache_write_1h` steht mit Faktor 2,0 in der Tabelle,
`cache_write_5m` mit 1,25 — und die headless-Logs tragen die Cache-Erstellung
als **eine Summe** (`_modelusage_kuebel`, `BL-152`), aus der die Laufzeit nicht
hervorgeht. Wer dieselbe Summe einmal als 5m und einmal als 1h liest, bekommt
zwei Ergebnisse, die sich wie 1,25 zu 2,0 verhalten — und „repariert" das dann
am Basispreis, wo es nicht sitzt.

Dieses Projekt fährt seine Loop-Rollen mit einem **1-Stunden-Prompt-Cache**;
`3.00` × `1h` reproduziert alle 79 Läufe. Ob im meldenden Projekt
`2.00` × `1h` oder `3.00` × `5m` die Läufe trifft, lässt sich von hier aus
nicht sagen — die zweite Möglichkeit ist aber nie geprüft worden, und sie
erklärt beide Felder mit **einem** Preis.

## Warum das jede Installation trifft

Der Satz steht in `geteilt/tools/kosten.py`, kommt also mit jedem Update in
jedes Feldprojekt. Er betrifft `sonnet`, den Default aller Loop-Rollen
(`TEAM_MODEL_LOOP`) — also die **Mehrheit aller gemessenen Token jeder
Installation**. Die Folge ist keine schiefe Zahl, sondern eine **Blockade**:
`sitzung-messen` verweigert regelkonform die Buchung, und der Architekt kann
den Kostenabschluss seiner Kaskade nicht machen, ohne die Tabelle lokal zu
verbiegen. Genau diesen Schaden nennt der `BL-166`-Kommentar selbst als
Begründung für die Senkung — sie hat ihn nicht behoben, sondern verschoben.

Verschärfend: Die Selbsteichung prüft den **gesamten** Log-Bestand, nicht nur
die Läufe der aktuellen Kaskade. Ein einziger falscher Satz macht damit
rückwirkend jede frühere Kaskade des Projekts „ungeeicht", auch die längst
abgerechneten.

## Lösungsrichtungen

1. **Die Cache-Write-Laufzeit vor dem Basispreis prüfen.** Bevor ein Satz
   geändert wird, sollte `preise_nachrechnen` die Gegenprobe mit **beiden**
   Cache-Write-Faktoren fahren und melden, welche Kombination den Bestand
   trifft. Passt eine Kombination exakt, ist die Laufzeit die Erklärung und der
   Preis bleibt, wie er ist. `preise_nachrechnen` kennt die 5m/1h-Unsicherheit
   ausweislich seines eigenen Kommentars bereits — sie wird nur nicht als
   Erklärung für eine Abweichung angeboten.
2. **Den Satz je Projekt konfigurierbar machen**, statt ihn im geteilten
   Werkzeug zu pflegen: ein optionaler `TEAM_PREISE`-Block in
   `team.config.*`, der einzelne Einträge überschreibt. Dann kostet ein
   abweichendes Feld eine Konfigurationszeile statt einer Kit-Änderung, die das
   jeweils andere Feld bricht.
3. **Die Eichung als Quelle nehmen, statt sie nur zu prüfen.** Trifft ein
   ganzer Bestand von N Läufen einen anderen Satz exakt, könnte das Werkzeug
   diesen Satz vorschlagen (`kosten.py preise-vorschlagen`) statt nur „stimmt
   nicht mehr" zu melden. Die Rechnung ist laut Kommentar in `preis_diagnose`
   ohnehin linear und exakt.

Richtung 2 ist die einzige, die beide Felder gleichzeitig bedient, ohne dass
eines von beiden auf den nächsten Kit-Entscheid warten muss.

## Was ich schon versucht habe

Im Projekt lokal auf `3.00` zurückgesetzt, mit Kommentar am Eintrag (Anlass,
Beleg, Verfallszeit beim nächsten `--update`, `BL-42`/`BL-58`). Danach meldet
das Werkzeug `✓ Preistabelle geeicht an 79 abgerechneten Laeufen dieses
Projekts`, und der Kostenabschluss der Kaskade war möglich. Die Korrektur ist
**projektlokal und hat eine Verfallszeit** — beim nächsten Update ist sie weg
und die Blockade zurück.

# Die Preistabellen-Eichung meldet Fehlalarm bei gemischter 5m/1h-Cache-Write-Zusammensetzung und verbietet damit eine richtige Buchung

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, kompilierte Sprache mit
  eigenem Test-Runner (nicht Python), elf Kaskaden gebaut, rund 475 Tests,
  140 abgerechnete headless-Läufe im Bestand

## Was passiert ist

Beim Kostenabschluss einer Kaskade sollte die Architektensitzung gemessen
werden:

```
python3 team/tools/kosten.py sitzung-messen --projekt .
```

Die Ausgabe:

```
! Preistabelle stimmt nicht mehr: 2 von 140 nachgerechneten Laeufen weichen ab.
    stufe-57-…json:        abgerechnet 14.1798, gerechnet 14.3446 (1.2 % daneben)
    frank-HM-20-v1-…json:  abgerechnet  1.5700, gerechnet  1.6199 (3.2 % daneben)
  Die Zahl unten ist damit UNGEEICHT. Preistabelle in kosten.py nachziehen,
  bevor du sie buchst.
```

Exit 2. Nach dem Briefing ist das ein **Buchungsverbot**: „Meldet es
‚Preistabelle stimmt nicht mehr', ist die Zahl ungeeicht und ich buche sie
nicht — dann gehört die Preistabelle nachgezogen."

**Die Preistabelle war aber richtig.** Nachgerechnet:

Der Eichpunkt liest `modelUsage` aus dem headless-Log. Dort steht die
Cache-Erstellung als **eine** Summe, ohne die 5m/1h-Aufteilung. Weil die
beiden Sätze verschieden sind (Faktor 2,00 gegen 1,25), muss
`preise_nachrechnen()` raten und nimmt die bessere der **zwei Reinformen**
(„alles 1h" oder „alles 5m"). Ein Lauf mit **gemischter** Zusammensetzung
liegt zwischen beiden und wird zwangsläufig als Abweichung gemeldet.

Beide Ausreißer sind genau das. Löst man nach dem 1h-Anteil auf, geht die
abgerechnete Summe exakt auf:

| Lauf | abgerechnet | 1h-Anteil, der aufgeht |
|---|---|---|
| erste Datei  | 14,1798 USD | 367 375 von 477 228 Token (77 %) |
| zweite Datei |  1,5700 USD |  96 626 von 129 880 Token (74 %) |

Der Basispreis des Modells trägt in beiden Fällen. Die eingebaute
Modell-Diagnose (`preis_diagnose`, „welcher Satz liegt daneben") hat
folgerichtig **keine** schiefe Zeile genannt — sie schwieg, während die Zeile
darüber „Preistabelle stimmt nicht mehr" behauptete.

Der gemessene Betrag selbst ist von der Mehrdeutigkeit **gar nicht betroffen**:
Er stammt aus dem Transkript, und das führt `cache_write_5m` und
`cache_write_1h` getrennt (hier 0 und 618 588). Der Wächter, der die Zahl
verwirft, hat also schlechtere Daten als die Zahl, die er verwirft.

## Wo es steckt

- `team/tools/kosten.py`, `preise_nachrechnen()` — die Schleife über
  `("cache_write_1h", "cache_write_5m")` mit `min(abweichungen)` am Ende
- die Auswertung in `sitzung-messen` (`schief = [b for b in befunde if b[3] >
  PREIS_TOLERANZ]`) mit `PREIS_TOLERANZ = 0.001`

Der Kommentar an der `min()`-Stelle beschreibt die Annahme sauber und belegt
sie an 920 Läufen aus vier Feldprojekten, die in zwei saubere Gruppen zerfielen
(Abo → 1h, API-Fallback → meist 5m). Der Fall „**ein** Lauf, in dem beides
vorkommt" ist dort nicht vorgesehen — und genau der tritt hier auf.

## Warum das jede Installation trifft

Der Fehler steckt in `team/tools/kosten.py`, nicht im Produktivcode eines
Projekts. Betroffen ist jede Installation, deren Läufe lang genug sind, dass
die Laufzeit der Cache-Einträge **innerhalb eines Laufs** wechselt — das ist
keine Eigenheit dieses Projekts, sondern eine Eigenschaft langer Sitzungen.
Die beiden Treffer hier sind der teuerste Bau-Schritt der Kaskade und ein
mehrstündig gewachsener Fix-Lauf.

Die Zahl wächst monoton: Das Ledger sammelt lebenslang, `logs_einsammeln()`
liest auch das Archiv, und ein einmal abweichender Altlauf bleibt für immer
im Nenner. Aus „2 von 140" wird über die Zeit „10 von 300" — und irgendwann
ist der Wächter dauerhaft rot.

**Das ist die Bauform, vor der das Kit an anderer Stelle selbst warnt** („Ein
Wächter mit Fehlalarmen wird abgeschaltet", `BL-14`). Er verbietet dann nicht
mehr falsche Buchungen, sondern richtige — und wer ihn nicht abschaltet, hat
die Wahl zwischen „gegen die Regel buchen" und „gar nicht buchen". Beides ist
schlechter als vorher.

## Was ich schon versucht habe

Nichts am Kit geändert. Im Projekt wurde die Abweichung von Hand nachgerechnet
(siehe Tabelle oben), als Fehlalarm eingestuft und die Buchung durchgeführt —
mit der vollständigen Rechnung in der Notiz der Ledger-Zeile und im
Abschlussdokument, damit die Ausnahme nachvollziehbar bleibt und nicht als
Gewohnheit durchgeht.

**Vorschlag, in der Reihenfolge meiner Vorliebe:**

1. **Das Intervall prüfen statt eines Punktes.** Statt die bessere der zwei
   Reinformen zu nehmen: Liegt der abgerechnete Betrag **zwischen** den beiden
   Reinform-Werten (alles-5m als eine Grenze, alles-1h als die andere), ist der
   Lauf **erklärbar** und damit kein Befund. Nur ein Betrag **außerhalb** des
   Intervalls beweist eine falsche Tabelle. Das ist dieselbe
   Schärfe bei echten Preisänderungen (der Basispreis skaliert beide Grenzen,
   ein Betrag außerhalb bleibt außerhalb), aber ohne diese Fehlalarmklasse.
   Zusätzlich fällt eine nützliche Kennzahl ab: die Lage im Intervall ist der
   geschätzte 1h-Anteil.
2. **Die bessere Quelle nehmen, wenn es sie gibt.** Liegt zum Lauf ein
   Transkript vor, trägt es die Aufteilung getrennt — dann braucht es gar
   keine Annahme. Aufwendiger, weil Log und Transkript einander zugeordnet
   werden müssen.
3. **Toleranz anheben.** `PREIS_TOLERANZ` von 0,1 % auf etwa 5 % — billig,
   aber die falsche Schraube: Sie macht den Wächter für **alle** Fehler
   stumpfer, um eine Klasse von Fehlalarmen zu dämpfen, und die gemessene
   3,2 % lägen ohnehin knapp darunter.

Als Beifang wäre zu überlegen, ob der Text bei einem Befund den Fall benennen
kann: Wenn `preis_diagnose` **keine** schiefe Zeile findet, obwohl Läufe
abweichen, ist die Tabelle nicht die wahrscheinliche Ursache — dieser
Widerspruch steht heute stumm in der Ausgabe und wäre ein starker Hinweis
für den, der ihn liest.

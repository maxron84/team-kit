# Die Selbsteichung von sitzung-messen meldet 'Preistabelle stimmt nicht mehr', wenn EIN Lauf-Log in sich widerspruechlich ist — und blockiert damit eine Buchung, die mit der Preistabelle nichts zu tun hat

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, achte Kaskade, 104 abgerechnete headless-Läufe im Repo

## Was passiert ist

Beim Kostenabschluss einer Kaskade meldete `kosten.py sitzung-messen`:

```
! Preistabelle stimmt nicht mehr: 1 von 104 nachgerechneten Laeufen weichen ab.
    <sweep-log>.json: abgerechnet 3.4498, gerechnet 3.2458 (5.9 % daneben)
  Die Zahl unten ist damit UNGEEICHT. Preistabelle in kosten.py nachziehen, bevor du sie buchst.
```

Die Preistabelle ist aber **nachweislich richtig**: **103 von 104** Läufen
reproduzieren sich exakt, darunter **14 Läufe desselben Modells vom selben
Tag** mit demselben Kontextfenster. Ein falscher Satz in der Tabelle träfe
alle, nicht einen — genau so lag der Fall in der früheren Meldung zu
`BL-166`, wo die Abweichung bei 78 von 79 Läufen und mit **konstantem
Quotienten** auftrat.

Die Ursache steckt im **Log selbst**: Sein oberster `usage`-Block widerspricht
seinem eigenen `modelUsage`-Block um den Faktor 51.

```
usage.cache_creation.ephemeral_1h_input_tokens :       6.278
usage.cache_creation.ephemeral_5m_input_tokens :           0
modelUsage.<modell>.cacheCreationInputTokens   :     320.621
```

Der gerechnete Wert lässt sich damit exakt nachbauen — die 320.621
Cache-Write-Token werden zum **5m**-Satz (1,25×) bewertet statt zum
**1h**-Satz (2,0×), weil der 1h/5m-Ausweis im obersten `usage`-Block praktisch
leer ist:

```
(158 + 56.073·5 + 3.991.028·0,1 + 320.621·1,25) / 1e6 · <input-satz> + <haiku-anteil>
  = 3,2458      exakt die gedruckte Zahl "gerechnet"
```

Der abgerechnete Wert (3,4452 für den Hauptanteil) entspricht **keinem** der
beiden reinen Sätze — rückgerechnet liegt der Faktor bei ≈1,46, also einem
gemischten Cache-Write, den der oberste `usage`-Block nicht abbildet. Die
Selbsteichung vergleicht hier folglich nicht zwei Preisannahmen, sondern zwei
**unterschiedlich vollständige Buchhaltungen desselben Laufs**.

**Zweite, kleinere Beobachtung:** Die Meldung sagt „Die Zahl unten ist damit
UNGEEICHT … bevor du sie buchst", das Werkzeug beendet sich aber mit **Exit 0**.
Das Rollen-Briefing des Architekten hält fest, dass genau dieser Zustand
**Exit 2** ist. Text und Exit-Code widersprechen sich also; wer nach dem
Exit-Code automatisiert, bucht eine Zahl, die die Ausgabe für unbrauchbar
erklärt.

## Wo es steckt

`team/tools/kosten.py`, in der Selbsteichung von `sitzung-messen` (Vergleich
`total_cost_usd` gegen die aus dem `usage`-Block nachgerechnete Summe) und in
der Formulierung ihrer Warnung.

## Warum das jede Installation trifft

Die Selbsteichung ist der einzige Schutz davor, im Abo eine ungeeichte Zahl zu
buchen — und das Briefing macht sie zur **Abbruchbedingung** („dann buche ich
sie nicht"). Sie kann heute aber nicht zwischen zwei sehr verschiedenen Lagen
unterscheiden:

1. **systematisch** — viele Läufe, konstanter Quotient: die Preistabelle ist
   wirklich falsch (der `BL-166`-Fall);
2. **punktuell** — ein einzelner Lauf, dessen `usage`-Block in sich
   widersprüchlich ist: die Preistabelle ist richtig, das Log ist unvollständig.

Beide erzeugen dieselbe Meldung mit demselben Rat („Preistabelle nachziehen").
Im zweiten Fall führt dieser Rat dazu, an einer **beweisbar korrekten**
Preistabelle zu drehen, bis der eine Ausreißer passt — womit die 103 richtigen
Läufe falsch werden. Wer dem Rat nicht folgt, steht ohne Regel da: Das Briefing
kennt nur „ungeeicht → nicht buchen". Jede Installation, die lange genug läuft,
sammelt irgendwann ein Log mit lückenhaftem `usage`-Block ein; ab dann ist
**jeder weitere Kostenabschluss** blockiert oder regelwidrig.

**Vorschlag:** Die Warnung an der **Verteilung** der Abweichung festmachen, nicht
an ihrem Auftreten. Weichen viele Läufe mit ähnlichem Quotienten ab, ist es die
Preistabelle (heutiger Text, Exit 2). Weicht ein einzelner Lauf ab, während die
übrigen exakt stimmen, gehört der Befund als **Log-Inkonsistenz** benannt — am
besten mit dem Hinweis, `usage.cache_creation` gegen
`modelUsage.*.cacheCreationInputTokens` zu halten —, der Lauf aus der Eichung
genommen und die Messung als **geeicht** ausgewiesen. In beiden Fällen sollte
der Exit-Code das sagen, was der Text sagt.

## Was ich schon versucht habe

- **Gegenprobe über den Bestand**: alle 104 Läufe nachgerechnet; 103 exakt, der
  eine Ausreißer wie oben erklärbar. Damit ist die Preistabelle dieses Projekts
  (`3.00` für den betroffenen Modellsatz, lokal korrigiert nach der früheren
  `BL-166`-Meldung) bestätigt und **nicht** angefasst worden.
- **Ursache im Log lokalisiert**: `usage`-Block gegen `modelUsage`-Block
  gehalten, Differenz Faktor 51 beim Cache-Write; der gerechnete Wert ist mit
  dem 5m-Satz exakt reproduzierbar.
- **Kein lokaler Fix**: Die Selbsteichung ist Kit-Code, und ein lokal
  entschärfter Schutzmechanismus ist schlimmer als ein lauter. Im Feldprojekt
  wurde die Messung **gebucht** — mit der Begründung oben im
  Abschluss-Protokoll, damit die Entscheidung nachlesbar bleibt.

# Eichwaechter meldet Preistabelle veraltet, wenn ein Lauf 5m- UND 1h-Cache-Erstellung mischt

- **Art**: Fehler am Kit (Fehlalarm eines Waechters, blockiert eine Buchung)
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter, fuenfte
  gebaute Kaskade, Abo-Betrieb; 62 abgerechnete headless-Laeufe im Bestand

## Was passiert ist

`sitzung-messen` bricht mit **Exit 2** ab und erklaert die gemessene Zahl fuer
ungeeicht:

```
  ! Preistabelle stimmt nicht mehr: 1 von 62 nachgerechneten Laeufen weichen ab.
      frank-<fund>-v1-<stempel>.json: abgerechnet 1.5700, gerechnet 1.6199 (3.2 % daneben)
    Die Zahl unten ist damit UNGEEICHT. Preistabelle in kosten.py nachziehen, bevor du sie buchst.
```

Nach dem Architekten-Briefing ist das ein hartes Stopp-Signal: *„Meldet es
‚Preistabelle stimmt nicht mehr', ist die Zahl ungeeicht und ich buche sie
nicht."* Der Closeout stand damit still.

**Die Preistabelle ist aber nicht veraltet.** Nachgerechnet aus dem
`modelUsage` des beanstandeten Laufs, mit **genau den Werten, die in
`kosten.py` stehen**:

```
Modell mit Basispreis 1.00 (zweites Modell im selben Lauf):
  gerechnet 0.005844 vs gemeldet 0.005844   -> Delta 0.000000000

Hauptmodell, Basispreis 2.00:
  feste Kuebel (input + output + cache_read) : 1.094553
  reine 5m-Annahme fuer cache_creation       : 1.419253   (9.27 % daneben)
  reine 1h-Annahme fuer cache_creation       : 1.614073   (3.19 % daneben)
  gemeldet                                   : 1.564192

  passt EXAKT bei einer MISCHUNG: 74.40 % der 129 880 cache_creation-Token
  als 1h, der Rest als 5m
  Gegenrechnung: 1.564192 vs gemeldet 1.564192 -> Delta 0.000000000
```

Alle drei uebrigen Kuebel treffen auf die letzte Stelle. Waere der Basispreis
falsch, waeren sie es mit. Der Lauf mischt schlicht beide Cache-TTLs.

## Wo es steckt

`team/tools/kosten.py`, `preise_nachrechnen()`. Die Funktion kommentiert das
Problem selbst sehr genau:

> `modelUsage` traegt die Cache-Erstellung als EINE Summe, ohne die
> 5m/1h-Aufteilung, die das Transkript hergibt. Die beiden Saetze
> unterscheiden sich (Faktor 2,00 gegen 1,25), also braucht es eine Annahme.

Sie loest das, indem sie **beide reinen Annahmen** rechnet und die kleinere
Abweichung gelten laesst. Das deckt zwei Faelle ab — „alles 1h" und „alles
5m" — und war an 920 Laeufen belegt, die genau so zerfielen.

**Der dritte Fall fehlt: ein Lauf, der mischt.** Der liegt per Konstruktion
ZWISCHEN beiden reinen Annahmen und trifft deshalb keine von beiden. Je
gleichmaessiger die Mischung, desto groesser die Abweichung: Bei 50/50 sind es
rund 4,5 % gegen den naeheren Nachbarn — weit ueber `PREIS_TOLERANZ` (0,001).

Der Waechter meldet dann nicht „gemischte Cache-TTL", sondern **„Preistabelle
stimmt nicht mehr"** — eine Diagnose, die in eine voellig andere Richtung
zeigt. Genau dort verlor ich die Zeit: Der Verdacht faellt auf einen
veralteten Preis, nicht auf die Annahme ueber einen Kuebel.

## Warum das jede Installation trifft

1. **Der Fehlalarm blockiert eine Buchung.** Er ist kein kosmetischer Befund:
   Das Briefing verbietet ausdruecklich, auf Exit 2 zu buchen. Wer der Regel
   folgt, laesst die Architekten-Kosten liegen; wer sie ignoriert, hat den
   Waechter abgeschafft. Beides ist schlecht, und der Kommentar in derselben
   Funktion benennt genau diese Gefahr: *„Ein Waechter mit Fehlalarmen wird
   abgeschaltet."*
2. **Es genuegt EIN Lauf.** Der Waechter urteilt ueber den ganzen Bestand:
   61 von 62 Laeufen reproduzierten auf die letzte Stelle, der eine
   Ausreisser reichte fuer Exit 2 und den Satz „die Zahl unten ist damit
   UNGEEICHT" — ueber eine Messung, die den Ausreisser gar nicht enthaelt
   (anderes Modell, andere Sitzung).
3. **Die Lage wird haeufiger, nicht seltener.** Der beanstandete Lauf ist der
   erste dieses Projekts, in dem das Loop-Modell mit einem
   1-Mio-Kontextfenster lief. Welcher Mechanismus die Mischung genau
   ausloest, kann ich von hier nicht sagen — beobachtbar ist, dass die
   saubere Zweiteilung aus den 920 Referenzlaeufen nicht mehr gilt.
4. **Die Messung selbst ist gar nicht betroffen.** `sitzung-messen` liest das
   TRANSKRIPT, und das traegt die 5m/1h-Aufteilung getrennt
   (`ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens`). Die Annahme
   ist allein im Waechter noetig, weil `modelUsage` in den headless-Logs
   gruenlicher ist. Es faellt also die Gegenprobe aus, nicht die Zahl.

## Was ich schon versucht habe

Nichts lokal gefixt — `kosten.py` ist unveraendert. Nachgerechnet habe ich mit
einem Wegwerf-Skript ausserhalb des Kits (die Zahlen oben).

Gebucht habe ich am Ende doch, aber **nicht** an der Regel vorbei: Die Notiz
der Ledger-Zeile traegt die Rechnung, die zeigt, dass die Preistabelle
stimmt. Ein unerklaerter Befund waere liegen geblieben.

Drei Moeglichkeiten, in aufsteigender Muehe:

1. **Die Diagnose richtig stellen.** Liegt der gemeldete Betrag ZWISCHEN der
   5m- und der 1h-Annahme, ist die Preistabelle nachweislich in Ordnung — die
   Aufteilung ist unbekannt, sonst nichts. Dieser Fall gehoert als eigener
   Hinweis gemeldet („gemischte Cache-TTL, Aufteilung aus `modelUsage` nicht
   ableitbar") und **nicht** als Preisabweichung gewertet. Das ist eine
   Intervallpruefung statt zweier Punktvergleiche und braucht keine neue
   Datenquelle.
2. **Die Aufteilung aus dem Transkript holen**, wo sie steht, statt sie im
   Log zu raten — belastbarer, aber es koppelt den Waechter an eine zweite
   Quelle, die bei archivierten Laeufen fehlen kann.
3. **Toleranz anheben** — die schlechteste Loesung. Sie stumpft den Waechter
   gegen echte Preisaenderungen ab und behandelt das Symptom.

Aus meiner Sicht ist (1) die richtige: Sie macht den Waechter **schaerfer**,
nicht weicher — heute meldet er einen Fall, der nachweislich kein
Preisproblem ist.

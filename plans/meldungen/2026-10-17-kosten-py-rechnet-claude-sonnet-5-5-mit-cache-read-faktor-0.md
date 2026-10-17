# kosten.py rechnet claude-sonnet-5-5 mit Cache-Read-Faktor 0,10 statt 0,05

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-17-kosten-py-rechnet-claude-sonnet-5-5-mit-cache-read-faktor-0.md
      ./kit-melden.sh ablegen  2026-10-17-kosten-py-rechnet-claude-sonnet-5-5-mit-cache-read-faktor-0.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-17-kosten-py-rechnet-claude-sonnet-5-5-mit-cache-read-faktor-0.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-24 im meldenden Projekt; verwandt mit Kit-BL-302 (derselbe Fehler für Opus 5.5)
- **Art**: Fehler am Kit (Kostenmessung und Selbsteichung)
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; siebte Kaskade, alle Loop-Rollen auf `claude-sonnet-5-5`

## Was passiert ist

`python3 team/tools/kosten.py sitzung-messen <transkript>` über die Transkripte der Rollen-Läufe einer
Kaskade (sechs Ralph-Stufen, zwei Sweeps, sechs Frank-Läufe, alle `claude-sonnet-5-5`) ergibt durchweg
18 bis 34 % mehr als `total_cost_usd` im Log desselben Laufs. Die Token sind dabei gleich: input, output,
cache_read und cache_write_1h des Transkripts (nach dem Dedup über die Nachrichten-ID) stimmen mit
`modelUsage` des Logs überein. Beispiel, eine Stufe:

```
Transkript (sitzung-messen):  input 40, output 25374, cache_read 2219224, cache_write_1h 129479  -> 1.2156 USD
Log, modelUsage claude-sonnet-5-5: dieselben Token                                         -> costUSD 0.9936584
```

Der Unterschied ist genau der Cache-Read-Anteil: 2 219 224 Token × 2,00 USD/Mio × 0,10 = 0,4438 USD in der
Tabelle des Kits, × 0,05 = 0,2219 USD in der CLI. Mit dem Faktor 0,05 reproduziert die Tabelle `costUSD`
aller 14 Läufe dieser Kaskade auf sechs Nachkommastellen:

| Lauf | Log costUSD (sonnet) | Tabelle, Faktor 0,10 | Faktor 0,05 |
|---|---|---|---|
| stufe-40 | 1.016871 | 1.278515 | 1.016871 |
| stufe-41 | 0.901380 | 1.062423 | 0.901380 |
| stufe-42 | 1.142160 | 1.462490 | 1.142160 |
| stufe-43 | 0.993658 | 1.215581 | 0.993658 |
| stufe-44 | 0.573448 | 0.732297 | 0.573448 |
| stufe-45 | 1.049683 | 1.364370 | 1.049683 |
| harry | 1.786847 | 2.389380 | 1.786847 |
| marv | 0.919260 | 1.104673 | 0.919261 |
| frank (sechs Läufe) | 0.228515 bis 0.339056 | je 15 bis 25 % höher | gleich |

Dieselbe Nachrechnung über alle 75 archivierten `claude-sonnet-5-5`-Logs des Projekts (sechs Kaskaden):
75 von 75 passen mit 0,05, keiner mit 0,10.

Die Selbsteichung sieht das nicht. `sitzung-messen` meldet beim selben Aufruf: „~ 12 von 48 nachgerechneten
Laeufen reproduzieren sich nicht — die Preistabelle ist dafuer NICHT die Ursache“ und „Die Zahl unten
bleibt geeicht“.

## Wo es steckt

- `team/tools/kosten.py`, `CACHE_READ_FAKTOR_JE_MODELL`: Dort stehen `claude-opus-5-5` (0,05),
  `claude-fable-5-1` und `claude-mythos-5-1` (0,025). `claude-sonnet-5-5` fehlt und erbt aus
  `PREIS_VIELFACHE` den Faktor 0,10. Kit-BL-302 hat diesen Fehler für Opus 5.5 behoben; Sonnet 5.5 blieb
  draußen.
- Die Selbsteichung (die Nachrechnung der abgerechneten headless-Läufe) erkennt einen falschen
  Cache-Read-Faktor offenbar nicht: Sie hält die Tabelle für richtig, obwohl kein einziger
  `claude-sonnet-5-5`-Lauf mit ihr aufgeht. Wie sie zu „12 von 48“ kommt, habe ich nicht untersucht.
- Nebenbefund: `claude-haiku-5-5` steht nicht in `PREIS_INPUT_USD_PRO_MTOK`; jeder Rollen-Lauf trägt
  einen kleinen Haiku-Anteil im Log. Das Werkzeug sagt das selbst; der Betrag ist klein.

## Warum das jede Installation trifft

`sonnet` ist der Default aller Loop-Rollen (`TEAM_MODEL_LOOP`), und die CLI löst ihn heute zu
`claude-sonnet-5-5` auf. Jede Messung eines Sonnet-5.5-Transkripts mit `sitzung-messen` liegt damit um den
Cache-Read-Anteil zu hoch — bei einer Rolle, die interaktiv im Abo arbeitet (`--akteur-abschluss`, etwa
Frank im Abo), landet der überhöhte Betrag im Ledger. Und eine Selbsteichung, die einen falschen
Tabellensatz für richtig erklärt, nimmt dem Architekten genau die Gegenprobe, für die es sie gibt.

Nicht betroffen: die Buchungen aus den Rollen-Logs (`--rollen-abschluss` übernimmt `total_cost_usd`;
nachgerechnet). Opus-5.5-Sitzungen rechnet die Tabelle seit Kit-BL-302 mit 0,05; nachgerechnet habe ich das
nicht, denn das Projekt hat keinen abgerechneten Opus-Lauf.

## Was ich schon versucht habe

Nichts im Kit geändert. Im Projekt trifft es keine Buchung: Die Rollen sind aus ihren Logs gebucht, der
Architekt arbeitet auf Opus 5.5. Vorschlag: `"claude-sonnet-5-5": 0.05` in `CACHE_READ_FAKTOR_JE_MODELL`,
dazu ein Test, der einen echten Sonnet-5.5-Log mit `modelUsage` nachrechnet, und eine Selbsteichung, die
bei einem Modell scheitert, dessen Läufe ausnahmslos nicht aufgehen.

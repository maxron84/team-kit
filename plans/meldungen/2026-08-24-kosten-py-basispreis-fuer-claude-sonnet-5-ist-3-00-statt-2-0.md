# kosten.py: Basispreis fuer claude-sonnet-5 ist 3.00 statt 2.00 — jede Abo-Messung faellt aus der Eichung

- **Art**: Fehler am Kit
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter mit SQLite.
  Loop-Rollen auf dem Default `sonnet`, Architekt auf `opus`, alle Rollen
  Abo-first.

## Was passiert ist

Beim Kostenabschluss der ersten Kaskade rief der Architekt weisungsgemaess

    python3 team/tools/kosten.py sitzung-messen --projekt .

auf. Statt einer buchbaren Zahl kam die Eich-Warnung:

    ! Preistabelle stimmt nicht mehr: 9 von 9 nachgerechneten Laeufen weichen ab.
        stufe-1-...json: abgerechnet 0.8451, gerechnet 1.1281 (33.5 % daneben)
        stufe-2-...json: abgerechnet 0.4676, gerechnet 0.5851 (25.1 % daneben)
        stufe-3-...json: abgerechnet 0.5236, gerechnet 0.6593 (25.9 % daneben)
      Die Zahl unten ist damit UNGEEICHT. Preistabelle in kosten.py nachziehen,
      bevor du sie buchst.
    ...
    EXIT: 2

Neun von neun Eichpunkten — alle vier Ralph-Stufen, beide Red-Team-Sweeps, alle
drei Frank-Laeufe. Kein einziger Lauf reproduzierte seinen abgerechneten
Betrag.

Die Nachrechnung von Hand zeigt, dass nicht die vier Verhaeltnisse aus
`PREIS_VIELFACHE` daneben liegen, sondern ausschliesslich der Basispreis. Loest
man die Gleichung

    total_cost_usd = B * (input + 5*output + 2*cache_write_1h + 0.1*cache_read) / 1e6

je Lauf nach `B` auf, kommt fuer `claude-sonnet-5` in **allen neun** Laeufen
exakt `2.000` heraus — nicht naeherungsweise, sondern auf drei Nachkommastellen
identisch, ueber Token-Mengen von 0,47 bis 1,04 USD hinweg. Der in derselben
Rechnung mitlaufende `claude-haiku-4-5` ergibt genauso exakt `1.000` und
bestaetigt damit sowohl die Methode als auch die uebrigen Tabellenwerte.

`PREIS_INPUT_USD_PRO_MTOK["claude-sonnet-5"]` steht aber auf `3.00` — dem Satz
von `claude-sonnet-4-5`/`4-6`, die in derselben Tabelle direkt darunter stehen.
Der Eintrag ist offenbar beim Aufnehmen der 5er-Generation aus der Zeile
darueber uebernommen worden.

## Wo es steckt

`team/tools/kosten.py`, Tabelle `PREIS_INPUT_USD_PRO_MTOK` (~Zeile 988):

    "claude-sonnet-5":   3.00,   <- falsch, gemessen 2.00
    "claude-sonnet-4-6": 3.00,
    "claude-sonnet-4-5": 3.00,

Die Verhaeltnistabelle `PREIS_VIELFACHE` daneben stimmt und muss nicht
angefasst werden; `preise_nachrechnen` und die 5m/1h-Fallunterscheidung
arbeiten korrekt — die Eichung hat den Fehler ja gefunden.

## Warum das jede Installation trifft

`sonnet` ist der ausgelieferte Default fuer alle Loop-Rollen
(`TEAM_MODEL_LOOP`). Jedes Projekt, das die Vorgabe nicht aendert, erzeugt
damit ausschliesslich Eichpunkte, die die Tabelle nicht reproduzieren kann —
die Eichung schlaegt strukturell fehl, und zwar in **100 %** der Faelle, nicht
in Randfaellen.

Der Schaden hat zwei Auspraegungen, und die zweite ist die schlimmere:

1. **Der gehorsame Architekt bucht gar nicht.** Das Briefing sagt woertlich:
   „Meldet es ‚Preistabelle stimmt nicht mehr', ist die Zahl ungeeicht und ich
   buche sie nicht." Er befolgt also die Regel, laesst den Kostenabschluss aus
   — und genau die Kosten, die das Ledger erfassen soll, bleiben unerfasst.
   Der Mechanismus schaltet sich selbst ab.
2. **Der ungeduldige Architekt bucht zu viel.** Wer die Warnung ueberliest,
   bucht bei einer Opus-Sitzung nach oben verzerrte Betraege — der Fehler
   sitzt im Basispreis, also skaliert er mit. In diesem Projekt haetten die
   vier Ralph-Stufen statt 2,88 USD rund 3,84 USD gemeldet.

Beide Wege enden dort, wo `BL-141` hinwollte: eine Zahl, die aussieht wie eine
Messung. Nur diesmal, weil die Eichung recht hat und die Tabelle nicht.

Nebenbefund derselben Sitzung, gleiche Datei, viel kleiner: `sitzung-messen
--help` faellt mit einem `FileNotFoundError`-Traceback um, weil `--help` als
Transkriptpfad an `sitzung_messen()` durchgereicht wird. Fuer ein Werkzeug, das
ein Briefing dem Menschen namentlich zum Aufruf empfiehlt, ist das die erste
Eingabe, die er versucht.

## Was ich schon versucht habe

Lokal nachgezogen — eine Zeile:

    -    "claude-sonnet-5":   3.00,
    +    "claude-sonnet-5":   2.00,   # lokal nachgezogen, siehe BL-8

Danach meldet dasselbe Kommando

    ✓ Preistabelle geeicht an 9 abgerechneten Laeufen dieses Projekts

und Exit `0`. Alle neun Eichpunkte reproduzieren ihren abgerechneten Betrag;
kein weiterer Wert musste angefasst werden.

Der lokale Fix hat die bekannte Verfallszeit (`BL-42`/`BL-58`) — er ueberlebt
das naechste `install.sh --update` nicht, deshalb diese Meldung. Im Projekt
liegt er als `BL-8` im Backlog, damit er nach einem Update gegengeprueft wird.

Vorschlag fuer die Gegenprobe im Kit: Die neun Eichpunkte sind gewoehnliche
Rollen-Logs. Ein Regressionstest, der einen solchen Log mit `modelUsage` und
`total_cost_usd` gegen `preise_nachrechnen` haelt, haette den Fehler beim
Aufnehmen der 5er-Generation sofort gezeigt — die Tabelle ist damit nicht
laenger eine Behauptung, wie es der Docstring von `preise_nachrechnen`
ausdruecklich anstrebt.

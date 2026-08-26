# Stufennummer ohne Plan-Block ist ein stiller No-Op und wird als vierter Ausgang gemeldet

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Bestand, Linux, bash-Bahn, Dart/Flutter (Android-Ziel),
  sechste Kaskade abgeschlossen, ~7.000 Zeilen Produktivcode, 277 Tests

Ein Vorfall, zwei Befunde. Der zweite ist der gefaehrlichere, weil er dem
Menschen einen konkreten, falschen Befehl vorlegt.

## Was passiert ist

Nach dem Closeout der sechsten Kaskade (Stufen 28–33, `RALPH_CAP=33`,
`.ralph-state` auf `34`) hat der Mensch `.ralph-state` versehentlich auf `17`
gesetzt — ein Wert aus einer alten Uebergabenachricht, die zu einer drei
Kaskaden aelteren Plandatei gehoerte. `.ralph-plan` zeigte unveraendert auf den
Plan der sechsten Kaskade.

Dieser Plan definiert ausschliesslich `## Stufe 28` bis `## Stufe 33`. Eine
Stufe 17 kommt darin nicht vor. Ralph wurde trotzdem gestartet:

```
=== Ralph: Stufe 17 (Plan: plans/ralph-kaskade-6-….md, Budget: 20 USD) ===
Ralph: Stufe 17 hat 0.3288568000 USD gekostet.
[ralph] Selbstpruefung des vierten Ausgangs (BL-41) fuer Stufe 17:
    ✗ Kein Commit fuer Stufe 17 und keine uncommitteten Aenderungen.
      Die Sitzung hat nichts hinterlassen — das ist NICHT der vierte Ausgang.
[ralph] STUFE FERTIG, QUITTUNG FEHLT (BL-41) — Stufe 17 hat kein
        <promise>STUFE_17_COMPLETE</promise> gegeben.
```

**Das Modell hat sich vorbildlich verhalten.** Es hat die Inkonsistenz selbst
erkannt, nichts gebaut, kein Promise gegeben und im Ergebnistext genau das
Richtige empfohlen: „`.ralph-state` muss vom Menschen auf den korrekten
naechsten Wert gesetzt werden — nach dem Abschluss-Protokoll waere das `34`."

Der Schaden ist also klein: 0,33 USD und ein gestoppter Lauf. Er wird nur
deshalb ueberhaupt zum Problem, weil die Shell danach etwas anderes empfiehlt.

## Befund 1: Ralph prueft nicht, ob die Stufe im aktiven Plan ueberhaupt steht

Eine Stufennummer, zu der es im aktiven Plan keinen `## Stufe N`-Block gibt,
ist keine baubare Aufgabe — das steht fest, **bevor** ein Aufruf abgesetzt
wird, und es ist mit einem `grep` auf die Plandatei zu klaeren.

Stattdessen wird ein voller, bezahlter Aufruf gestartet, und ob dabei etwas
Sinnvolles passiert, haengt allein daran, dass das Modell die Lage von selbst
durchschaut. Diesmal hat es das getan. Ein anderes Modell — oder ein guenstiges
Loop-Modell an einem schlechten Tag — koennte genauso gut die naechstgelegene
Stufe bauen, eine laengst gebaute Stufe erneut anfassen oder etwas erfinden.
Der Loop hat dafuer keine Schranke.

Die Fehlerklassen sind im Kit sonst sorgfaeltig benannt (Pausen-Exit 42,
vierter Ausgang 43). Hier fehlt eine: **„Stufe steht nicht im aktiven Plan"**
— ein Zustandsfehler vor dem ersten Token, mit eigenem Exit-Code, ohne
bezahlten Aufruf.

Erschwerend: Die beiden Zeiger `.ralph-plan` und `.ralph-state` sind
unabhaengig voneinander von Hand zu setzen, beide ungetrackt (in
`.gitignore`), und **nichts prueft ihre Zusammenpassung**. Der Statusbericht
zeigt „naechste Stufe 17 / Cap 33" — beides plausible Zahlen, in dieser
Kombination aber unmoeglich, weil der Plan bei 28 anfaengt. Genau diese Zeile
haette den Fehler zeigen koennen und zeigt ihn nicht.

## Befund 2: Die BL-41-Selbstpruefung widerspricht sich und empfiehlt dann das Falsche

Die Selbstpruefung stellt korrekt fest:

> ✗ Kein Commit fuer Stufe 17 und keine uncommitteten Aenderungen.
>   Die Sitzung hat nichts hinterlassen — **das ist NICHT der vierte Ausgang.**

Und direkt danach wird trotzdem der vierte Ausgang gemeldet, samt vollem
Handlungsplan fuer den vierten Ausgang — einschliesslich dieses Satzes:

> - Beides ja: von Hand quittieren — `echo 18 > .ralph-state`, dann erneut
>   starten.

**Dieser Befehl ist hier falsch, und er ist der einzige konkrete Befehl im
ganzen Block.** Er wuerde eine Stufe quittieren, die nie gebaut wurde, weil sie
im aktiven Plan nicht existiert; danach stuende der Zeiger auf 18 statt auf 34,
also sechzehn Stufen hinter der Wahrheit — und der naechste Lauf liefe in
genau denselben No-Op, eine Nummer weiter. Der Mensch bekaeme dieselbe Meldung
mit derselben Empfehlung und koennte sie sechzehn Mal befolgen.

Der Text raet ausdruecklich „NICHT neu bauen, bevor die von Ralph genannten
zwei Pruefungen gelaufen sind" — die zwei Pruefungen (`git log` / Smoke-Test)
sind hier aber beide unauffaellig: kein Commit, Baum gruen, 277 Tests. Sie
koennen diesen Fall gar nicht von einem echten vierten Ausgang unterscheiden,
denn der Unterschied liegt nicht im Repo, sondern im Verhaeltnis von
`.ralph-state` zum aktiven Plan.

Dazu kommt: Ralph hatte die richtige Antwort im Ergebnistext stehen (`34`, mit
Begruendung aus dem Abschluss-Protokoll). Sie erscheint in der Konsole nicht.
Sichtbar ist nur die Shell-Empfehlung, die daneben liegt. Wer dem Werkzeug
vertraut statt das JSON-Log zu oeffnen, macht es falsch.

## Warum das jede Installation trifft

Beides steckt in `bash/entry/ralph.sh` und in der BL-41-Selbstpruefung, nicht
in Produktivcode.

Der Auslöser ist banal und wiederholbar: Zwischen zwei Kaskaden liegen bei uns
Tage, und eine Uebergabenachricht mit einem nackten `echo N > .ralph-state`
verfaellt still, sobald die naechste Kaskade gehaertet ist. Jede Installation,
die den Zeiger von Hand setzt — also jede —, kann ihn auf eine Nummer setzen,
die zum aktiven Plan nicht passt: nach einem Closeout, nach einem Planwechsel,
nach einem Copy-Paste aus einer aelteren Nachricht, nach einem abgebrochenen
Lauf. Der Zeiger ist ungetrackt, also gibt es nicht einmal ein `git diff`, das
die Aenderung zeigt.

Und die Folge ist in der schlechten Variante nicht ein gestoppter Lauf, sondern
eine falsche Quittung: Nach `echo 18 > .ralph-state` gilt eine nie gebaute
Stufe als fertig, und das Buchhaltungsmittel des Loops stimmt nicht mehr.

## Vorschlag

**Zu Befund 1** — vor dem Aufruf pruefen, nicht danach:

1. Vor dem ersten Token pruefen, ob der aktive Plan einen `## Stufe N`-Block
   fuer die Nummer aus `.ralph-state` enthaelt. Fehlt er, mit einer eigenen,
   benannten Fehlerklasse abbrechen („Stufe N steht nicht in <plandatei>") und
   die Spanne nennen, die der Plan tatsaechlich abdeckt („dieser Plan definiert
   Stufen 28–33"). Kein Aufruf, keine Kosten.
2. Die Meldung sollte den wahrscheinlichsten Grund gleich mitnennen, weil er
   fast immer derselbe ist: „`.ralph-state` und `.ralph-plan` passen nicht
   zusammen — wurde der Plan gewechselt, ohne den Zeiger nachzuziehen, oder
   umgekehrt?"
3. Denselben Abgleich in den Statusbericht: Liegt `.ralph-state` ausserhalb der
   Stufenspanne des aktiven Plans, gehoert das in die Kaskaden-Zeile. Heute
   zeigt sie „naechste Stufe 17 / Cap 33" und laesst es wie einen normalen
   Zwischenstand aussehen.

**Zu Befund 2** — der Widerspruch ist der eigentliche Fehler:

4. Stellt die Selbstpruefung fest „das ist NICHT der vierte Ausgang", dann darf
   der Handlungsplan des vierten Ausgangs **nicht** gedruckt werden — schon gar
   nicht sein `echo N+1 > .ralph-state`. Der Fall „Sitzung hat nichts
   hinterlassen" braucht einen eigenen, kurzen Text, und der lautet nicht
   „quittiere von Hand", sondern „hier wurde nichts gebaut, pruefe die
   Ausgangslage".
5. Wenn die Selbstpruefung ohnehin schon zwischen den Faellen unterscheidet,
   sollte sie auch die Konsequenz tragen: verschiedene Exit-Codes fuer „fertig,
   Quittung fehlt" (Arbeit liegt vor, quittieren ist richtig) und „nichts
   hinterlassen" (nichts zu quittieren).
6. Den Ergebnistext des Modells bei fehlendem Promise mit ausgeben, mindestens
   gekuerzt. In diesem Vorfall stand die richtige Antwort dort und war die
   einzige richtige Angabe auf dem Bildschirm — sie blieb im `.json`-Log
   liegen, waehrend die falsche Empfehlung in der Konsole stand.

## Was ich schon versucht habe

Nichts umgangen. Der Vorfall war nach der Diagnose in einem Schritt behoben:
`.ralph-state` auf `34` gesetzt, den Wert aus dem committeten
Abschluss-Protokoll der sechsten Kaskade. Der Statusbericht meldet danach
wieder „Bau abgeschlossen (Ralph hat Feierabend)".

Vorher die zwei von Ralph verlangten Pruefungen gefahren, um auszuschliessen,
dass doch Arbeit vorlag: kein Commit und keine uncommitteten Aenderungen
(`git log`/`git status`), Smoke-Test gruen mit 277 Tests. Der bezahlte Aufruf
(0,33 USD) hat tatsaechlich nichts hinterlassen.

Die Empfehlung `echo 18 > .ralph-state` habe ich **nicht** befolgt. Sie waere
der Fehler gewesen, den diese Meldung beschreibt — und sie stand als einziger
konkreter Befehl auf dem Bildschirm.

Kein lokaler Fix am Kit-Code, also auch keine Verfallszeit. Auf unserer Seite
ziehen wir nur die Uebergabe-Konvention nach: kein nacktes
`echo N > .ralph-state` mehr in einer Uebergabenachricht, sondern immer mit
Kaskadennummer und Plandatei daneben, damit ein Copy-Paste aus einer aelteren
Nachricht als veraltet zu erkennen ist.

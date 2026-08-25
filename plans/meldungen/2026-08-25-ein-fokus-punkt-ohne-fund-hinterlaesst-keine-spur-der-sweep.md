# Ein Fokus-Punkt ohne Fund hinterlaesst keine Spur — der Sweep quittiert nicht, was er geprueft hat

- **Art**: Fehler am Kit
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Flutter/Dart mit SQLite,
  vier gebaute Kaskaden, 23 Stufen, 218 Tests. Alle Rollen im Abomodus.

Drei Befunde, die dasselbe Muster haben und deshalb zusammen gemeldet werden:
**Die Team-Infrastruktur meldet Ergebnisse, aber nicht Abdeckung** — und an
drei Stellen liest sich das Fehlen einer Rückmeldung wie ein sauberes
Ergebnis. Der erste ist der schwerste, die beiden anderen liegen seit
mehreren Kaskaden unterhalb der Meldeschwelle und werden hier mit angehängt.

---

## 1. Der Sweep quittiert nicht, was er geprueft hat (neu)

### Was passiert ist

Der Fokus-String einer Kaskade hatte **13 nummerierte Punkte** — jeder eine
benannte Naht zwischen dem neu Gebauten und einer bereits geschlossenen
Zusicherung. Zurückgekommen sind aus zwei Sweeps **zwei Funde**. Über die
übrigen elf Punkte sagt der Lauf **nichts**.

Die Abschlussmeldungen beider Rollen bestehen aus je einem Satz über den
eigenen Fund plus dem Promise. Kein Wort dazu, welche Punkte angeschaut und
für sauber befunden wurden.

Konkret blieb dadurch eine ausdrücklich gestellte Frage offen. Fokus-Punkt 9
lautete sinngemäß: „Rechne nach, ob die Form auch bei 360 logischen Pixeln
hält — Geräte darunter sind verbreitet, und der Plan prüft nur bei 411."
Ob das jemand nachgerechnet hat, ist nach dem Lauf nicht mehr feststellbar.
Im Closeout muss der Punkt deshalb als **ungeprüft** in die Handprüfungen
wandern — möglicherweise zum zweiten Mal.

### Wo es steckt

`team/redteam.sh`, im Prompt-Aufbau der Sweep-Rollen:

```
Findest du NICHTS, ändere keine Datei.
Beende IMMER mit exakt: <promise>REDTEAM_SWEEP_COMPLETE</promise>
```

Die Anweisung ist für sich richtig — sie hält die Read-Only-Grenze sauber und
verhindert Alibi-Commits. Sie hat nur keine Gegenrichtung: Es gibt keine
Stelle, an der die Rolle sagen **darf**, was sie geprüft hat. Das Promise ist
die Sweep-Quittung, und es trägt genau ein Bit.

### Warum das jede Installation trifft

Die Regeldatei stellt den Fokus als **einzigen** Hebel für die Prüftiefe dar:
Ein zweiter Sweep über denselben Bau meldet „nichts Neues zu prüfen", weil die
Sweep-Marke der letzte geprüfte Commit ist — die Tiefe lässt sich also nur
über das Bauvolumen davor und über die Qualität des Fokus-Strings drehen.

Ein Hebel ohne Rückmeldung lässt sich aber nicht nachjustieren. Nach vier
Kaskaden weiß die planende Rolle nicht, ob ein Punkt nichts brachte, **weil
dort nichts ist** oder **weil er zu vage formuliert war**. Beide Fälle sehen
identisch aus: kein Fund, kein Wort.

Der Schaden ist derselbe, den das Kit an anderer Stelle schon benannt hat:
Ein Pfad, der nie wirklich ausgeführt wird, während die Anzeige grün bleibt.
Hier ist es ein Prüfpunkt, der nie wirklich angeschaut wird, während der
Sweep sich für vollständig erklärt. Er kostet die planende Rolle bei jedem
Closeout dieselbe Entscheidung — den Punkt als ungeprüft führen und die
Arbeit ein zweites Mal ansetzen, oder ihn stillschweigend abhaken.

### Was ich schon versucht habe

Nichts lokal gepatcht — der Fix gehört in den Prompt-Aufbau, und ein lokaler
Eingriff dort hätte die bekannte Verfallszeit beim nächsten `--update`.

Vorschlag zur Form, bewusst schmal gehalten, damit er die Read-Only-Grenze
nicht anfasst: Die Rolle beendet ihren Sweep mit **einer** Zeile je
Fokus-Punkt — Nummer, und eines von `Fund <HM-Nr>` / `geprüft, ohne Befund` /
`nicht erreichbar (Begründung)`. Diese Zeilen gehören **nicht** ins
Beutebuch (dort stehen Funde), sondern in die Sweep-Ausgabe und damit ins
Lauf-Log, das die planende Rolle im Closeout ohnehin liest. Kein neuer
Schreibpfad, keine Aufweichung von „Findest du NICHTS, ändere keine Datei".

Die dritte Kategorie ist die wichtigste: „nicht erreichbar" ist die Antwort,
die heute vollständig fehlt und die am meisten wert wäre — sie sagt der
planenden Rolle, dass ihr Fokus-Punkt in der Prüfumgebung gar nicht rot
werden kann.

---

## 2. Der Abschlussbericht zitiert sich selbst (liegt seit vier Kaskaden)

Der Block „Vollautomatik (letzte 3 Zeilen: …)" im Abschlussbericht liest das
Logfile, in das er im selben Moment schreibt. Im gedruckten Endbericht zeigt
er deshalb seine eigenen zwei Zeilen davor **plus seine eigene Überschrift**
— an genau der Stelle, an der ein Mensch den Verlauf des Laufs sucht. Aus dem
letzten Lauf, wörtlich:

```
  ──────── Vollautomatik (letzte 3 Zeilen: vollautomatik-….log) ────────
      c5bf352 fix(uat): …
      2d3d651 docs(beute): …
    ──────── Vollautomatik (letzte 3 Zeilen: vollautomatik-….log) ────────
```

Rein kosmetisch, aber irreführend: Die Überschrift verspricht den Verlauf und
liefert die Commit-Liste von zwei Zeilen weiter oben. In demselben Bericht
erscheint der Hinweis auf einen verworfenen Versuch fünfmal.

**Wo es steckt:** die Berichtsausgabe von `team-status.sh` bzw. der Aufruf am
Ende von `vollautomatik.sh` — der Tail wird gelesen, während dieselbe Ausgabe
in die Datei läuft. Ein Snapshot der Logdatei **vor** dem Schreiben des
Berichts würde reichen.

---

## 3. Pro-Lauf-Deckel und Schlusszeile gelten je Aufruf, nicht je Kaskade (liegt seit einer Kaskade)

Wird eine Kaskade durch einen Cap-Abbruch in zwei `vollautomatik.sh`-Aufrufe
geteilt, hebt **jeder** Aufruf den Lauf-Deckel aus `BUDGET_EMPFEHLUNG_USD`
neu an, jeder für sich. Die Kaskade bekam so das **Doppelte** des geplanten
Spielraums, ohne dass jemand das entschieden hat, und verbrauchte 42 % über
der Empfehlung, gegen die sie geplant war. Nichts warnt, und keine Zeile setzt
die Segmente zusammen.

Dieselbe Trennung macht die gedruckte Schlusszeile irreführend: „Dieser Lauf:
… USD" ist das **zweite Segment**; wer sie als Kaskadenkosten liest,
unterschätzte im belegten Fall um 59 %.

**Das Ledger ist ausdrücklich NICHT betroffen** — der Rollen-Abschluss liest
die unarchivierten Logs beider Segmente und bucht korrekt. Der Fehler sitzt
allein in der Anzeige und in der Deckel-Governance.

**Wo es steckt:** die Deckel-Anhebung und die Schlusszeile in
`vollautomatik.sh`. Eine Möglichkeit wäre, den Lauf-Deckel gegen die Summe
der noch nicht abgeschlossenen Segmente derselben Kaskade zu prüfen statt
gegen das aktuelle Segment — dann wäre er wieder das, was sein Name sagt.

---

## Gemeinsamer Nenner

Alle drei Befunde sind Auskunfts-Fehler, keine Ausführungs-Fehler: Der Lauf
tut das Richtige und **berichtet unvollständig darüber**. Das ist die Klasse,
die sich am längsten hält, weil nichts rot wird — Punkt 2 und 3 liegen seit
mehreren Kaskaden genau deshalb unter der Meldeschwelle. Punkt 1 ist der
teuerste der drei, weil er den einzigen Hebel für die Prüftiefe blind macht.

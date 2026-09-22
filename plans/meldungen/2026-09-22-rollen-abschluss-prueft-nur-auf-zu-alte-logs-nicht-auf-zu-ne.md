# rollen-abschluss prueft nur auf zu ALTE Logs, nicht auf zu neue

- **Bezug**: BL-122
- **Art**: Fehler
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, 29 gebaute Kaskaden

## Was passiert ist

Beim Nachbuchen einer **übersprungenen** Kaskade (siehe die Meldung
*„Eine ganze Kaskade kann ohne Closeout ausfallen"*) lagen in den Logordnern
die Rohlogs **zweier** Kaskaden gleichzeitig: die der nachzubuchenden älteren
und die der gerade abgeschlossenen neueren.

`--rollen-abschluss <ältere Nummer>` hätte **beide Sätze** unter der älteren
Nummer gebucht und danach **beide** archiviert. Der Wächter aus `BL-221`
greift hier nicht: Er prüft, ob Logs **älter** sind als der Kaskadenbeginn —
die fremden Logs waren aber **neuer**.

Ich habe die neueren Logs von Hand beiseitegelegt, gebucht, und sie danach
zurückgelegt. Das funktioniert, setzt aber voraus, dass man das Problem
**vorher** kennt.

## Wo es steckt

`team/tools/kosten.py`, im Verb `rollen-abschluss` bzw. in
`logs_vor_kaskadenbeginn()`.

Die Begründung im Quelltext trifft genau zu — und beschreibt dabei nur die
eine Richtung:

```
# BL-221: … Ein Werkzeug, das eine Fehlzuordnung sicher genug erkennt,
# um sie zu benennen, darf sie nicht ausfuehren. Jetzt: Abbruch vor dem
# Buchen und vor dem Archivieren, Exit 1 …
```

Der Satz gilt wortgleich für Logs, die **nach** dem Ende der gebuchten
Kaskade entstanden sind. Die Erkennung ist genauso sicher: Es gibt eine
nächste Kaskadennummer mit einer eigenen Plandatei und einem eigenen
Anfangszeitpunkt.

## Warum das jede Installation trifft

Der Auslöser ist nicht exotisch. Es genügt, dass **ein** Closeout ausfällt
oder verschoben wird — dann liegen beim nächsten Abschluss zwei Kaskaden im
Ordner. Der Kommentar zu `BL-221` sagt selbst, dass der verwandte Fall *„der
Regelfall ist, nicht der Ausreißer"*.

Der Schaden ist derselbe, den `BL-221` bereits benennt: Die Kosten stehen
unter der falschen Kaskade **und** die Belege sind weg, sodass ein zweiter
Aufruf sie nicht mehr findet. Er ist hier sogar unauffälliger, weil er die
**ältere** Kaskade zu groß macht — und ein zu großer Wert in einer
abgeschlossenen Kaskade fällt niemandem mehr auf.

## Vorschlag

Die Prüfung symmetrisch machen: Neben `logs_vor_kaskadenbeginn` eine
`logs_nach_kaskadenende`. Das Ende einer Kaskade ist maschinell greifbar als
der **Beginn der nächsten** — also der Add-Commit der nächsten Plandatei, das
Kriterium, das das Kit für den Kaskadenbeginn bereits benutzt.

Verhalten wie bei `BL-221`: **Abbruch vor dem Buchen und vor dem
Archivieren**, Exit 1, benannte Übersteuerung. Für den Schalter bietet sich
`--auch-neuere` an, parallel zu `--auch-aeltere` — oder, falls ein Name
genügen soll, ein gemeinsames `--auch-fremde`.

**Nützlich wäre dabei ein Hinweis auf den Handgriff**, der hier wirklich
gebraucht wird, weil er nicht offensichtlich ist:

```
  Gehoeren sie zur naechsten Kaskade, lege sie beiseite, buche diese
  Kaskade, und lege sie danach zurueck.
```

## Was ich schon versucht habe

- **Zuerst gelesen, dann gehandelt.** Weil `--rollen-abschluss` ein
  Buchungsverb ohne Probelauf ist, habe ich vor dem ersten Aufruf im
  Quelltext nachgesehen, welche Dateien es einsammelt. Genau dabei fiel die
  fehlende Richtung auf.
- **Von Hand getrennt**: neuere Logs verschoben, ältere Kaskade gebucht
  (Ledger-Zeilen gezählt: +2, Beträge gegen die Einzellogs geprüft), Logs
  zurückgelegt, neuere Kaskade gebucht (wieder +2). Danach
  `--ledger-pruefen`: 0 Warnungen.
- **Lokaler Fix: keiner.**

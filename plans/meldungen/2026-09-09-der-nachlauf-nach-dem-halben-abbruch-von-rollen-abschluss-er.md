# Der Nachlauf nach dem halben Abbruch von rollen-abschluss ersetzt die korrekte Bauzeile durch 0.0000

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (dreizehn Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 550 Tests.

## Was passiert ist

Kostenabschluss einer Kaskade. Erster Aufruf, regulär:

```
.\team-status.cmd --rollen-abschluss <N> <domaene>
```

**Antwort:** die `BL-221`-Warnung („11 Log(s) sind AELTER als der Beginn der
Kaskade <N> … es wird NICHTS gebucht und NICHTS archiviert"), Exit **0**.

Der Satz gilt nur für die `roles`-Hälfte. Die `ralph`-Hälfte war bereits
gebucht — mit einer **Platzhalter-Notiz**, weil der Aufruf ohne Notiztexte
lief — und `.ralph-logs` bereits archiviert. **Das ist `BL-239`, unverändert
und zum zweiten Mal.** Neu ist, was danach passiert.

Zweiter Aufruf, korrigierend, mit beiden Notiztexten und `--ersetzen` (der im
Briefing vorgesehene Weg, eine falsche Altzeile richtigzustellen):

```
.\team-status.cmd --rollen-abschluss <N> <domaene> "<notiz-rollen>" "<notiz-bau>" --ersetzen
```

**Antwort:**

```
Warnung: keine Log-Dateien in .ralph-logs gefunden -- es wird 0.0000 USD
gebucht. Pruefe VOR dem Buchen, ob diese Kaskade wirklich keine Kosten hatte
oder ob die Logs bereits archiviert wurden (siehe .ralph-logs/archiv/) --
Archiv enthaelt bereits Dateien!.
```

Exit **0**. Die `roles`-Zeile wurde korrekt gebucht — und die **richtige**
`ralph`-Zeile über 6,7523 USD wurde durch **0,0000 USD** ersetzt.

Wiederherstellung nur von Hand, aus den drei bereits archivierten Stufenlogs
addiert (`4.3119793 + 1.1989119 + 1.2414147 = 6.7523059`) und über
`--akteur-abschluss ralph abo 6.7523 <domaene> "<notiz>" --kaskade <N>
--ersetzen` zurückgeschrieben.

## Wo es steckt

`team/tools/kosten.py`, Verb `ralph-abschluss` (und `rollen-abschluss`, das
denselben Mechanismus benutzt), in dem Zweig, der eine **leere** Logmenge
behandelt. Die Warnung dort ist bereits geschrieben und trifft genau ins
Schwarze — sie ist nur eine Warnung und kein Abbruch.

Der Auslöser davor sitzt in der pwsh-Oberfläche `team-status.ps1`, in der
Reihenfolge, in der `--rollen-abschluss` seine beiden Verben abarbeitet: erst
`ralph-abschluss` (bucht und archiviert), dann `rollen-abschluss` (bricht am
`BL-221`-Riegel ab). Das ist `BL-239`.

## Warum das jede Installation trifft

Beide Hälften stecken in `team/`, keine Zeile davon ist projektspezifisch. Die
Kette braucht keinen ungewöhnlichen Zustand: Eine Out-of-Loop-Runde zwischen
zwei Kaskaden ist der **Normalfall** eines Projekts mit Handabnahme — genau
dafür gibt es die benannten Nummern `vor-N`. Wer den `BL-221`-Riegel korrekt
befolgt, ruft danach zwangsläufig ein zweites Mal auf; und wer dabei die
Platzhalter-Notiz der ersten Hälfte richtigstellen will, nimmt `--ersetzen`,
weil das Briefing genau dafür `--ersetzen` nennt.

**Der Schaden ist still, wenn man ihn nicht sucht.** Die 0,0000-Zeile ist für
sich plausibel: Es gibt legitime 0,0000-Zeilen (eine Out-of-Loop-Runde hat
keinen Bau). `--ledger-pruefen` schweigt dazu, weil die Rohlogs archiviert
sind und die Zeile existiert. Aufgefallen ist es nur, weil derselbe Aufruf
sekundenlang zuvor 6,7523 USD gemeldet hatte.

## Was ich vorschlage

**Für `--ersetzen` ist „keine Logs gefunden" kein Warnfall, sondern ein
Abbruch.** Eine Ersetzung durch Null ist nie das, was jemand meint: Wer
`--ersetzen` schreibt, hat eine Zeile mit einem Betrag vor Augen. Bei einem
**Erstaufruf** kann 0,0000 richtig sein — dort soll die Warnung bleiben, wie
sie ist. Die Unterscheidung kostet eine Bedingung.

Das Kit warnt an anderer Stelle bereits vor genau diesem Schaden: Das
Rollen-Briefing des Architekten trägt den Satz *„Nie raten: Im Feld hat ein
stilles Ersetzen 5,5515 USD aus dem Ledger gelöscht."* Hier war es nicht
einmal still — und passiert ist es trotzdem, weil die Warnung **nach** der
Entscheidung kommt und nicht **vor** ihr.

## Was ich schon versucht habe

Nichts lokal gepatcht. Die Wiederherstellung lief über den regulären
`--akteur-abschluss`-Weg, und die Rechnung steht im Notiztext der Ledgerzeile,
damit die Handbuchung nachvollziehbar bleibt.

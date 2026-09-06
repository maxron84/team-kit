# rollen-abschluss vor-N bucht immer den GESAMTEN unarchivierten Bestand — der BL-221-Riegel greift bei benannten Nummern nicht

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Flutter/Dart-Stack;
  15 Kaskaden gebaut, Ledger mit rund 60 Zeilen, regelmäßige
  Out-of-Loop-Runden zwischen den Kaskaden (also regelmäßige `vor-N`-Nummern).

## Was passiert ist

Nach dem Lauf der Kaskade 15 meldete `--budget` die erwartete Warnung:

```
[WARNUNG] 3 unarchivierte(s) Log(s) ueber 3.2621 USD in .ralph-logs/.team-logs
sind AELTER als der Beginn der Kaskade 15 — sie gehoeren zu einem frueheren
Durchgang, fuer den kein Rollenabschluss gebucht ist. […]
  Gehoeren sie zu einer Out-of-Loop-Runde zwischen zwei Kaskaden, gehoeren sie
  unter eine eigene benannte Nummer (`--kaskade vor-N`) — sonst traegt diese
  Kaskade fremde Kosten (BL-45).
```

Ich bin dieser Anweisung wörtlich gefolgt und habe **zuerst** die
Out-of-Loop-Runde gebucht:

```
./team-status.sh --rollen-abschluss vor-15 produkt "…"
```

Erwartet: die **drei** genannten Altlogs über 3,2621 USD.
Bekommen — kommentarlos, ohne Warnung, ohne Rückfrage:

```
Roles-Zeile Kaskade vor-15 (produkt) angelegt: 10.0777 USD (abo …), 9 Log(s) archiviert
Ralph-Zeile Kaskade vor-15 (produkt) angelegt: 10.8653 USD (abo …), 5 Log(s) archiviert
```

Das sind **alle 14** unarchivierten Logs: die drei Altlogs **plus** die
kompletten Laufkosten der gerade abgeschlossenen Kaskade — 17,68 USD unter der
falschen Nummer, und die Rohlogs im selben Zug archiviert. Der Zustand danach
ist genau der, den `BL-221` ausdrücklich verhindern soll: Die Kosten stehen
falsch **und** die Belege sind weggeräumt.

## Wo es steckt

In `team/tools/kosten.py`, im `BL-221`-Riegel des Rollenabschlusses:

```python
_beginn, _zu_alt = logs_vor_kaskadenbeginn(files, kaskade, repo)
if _zu_alt:
    …
    if not auch_aeltere:
        print("  Gehoeren sie doch zu dieser Kaskade, bucht "
              "`--auch-aeltere` sie mit (BL-221).", file=sys.stderr)
        return 1
```

Der Riegel hält die Zeitmarke jedes Logs gegen den **Beginn einer Kaskade**.
Eine benannte Nummer wie `vor-15` hat keinen Kaskadenbeginn — es gibt keinen
`feat(stufeN)`-Commit, an dem er sich festmachen ließe. `logs_vor_kaskadenbeginn`
liefert damit eine leere Liste, `if _zu_alt:` ist falsch, und **jedes** Log gilt
als zugehörig.

**Der Schutz fehlt also ausgerechnet in dem Fall, für den `vor-N` erfunden
wurde.** Der Kommentar über dem Riegel beschreibt diesen Fall sogar wörtlich —
„Zwischen zwei Kaskaden liegen Out-of-Loop-Fixe (Frank, `--kaskade vor-N`)" —
und die Warnung in `--budget` schickt den Anwender aktiv dorthin.

## Warum das jede Installation trifft

Der Ablauf ist der vom Kit selbst empfohlene: `--budget` warnt, nennt `vor-N`
als Lösung, und wer der Empfehlung folgt, bucht mehr, als er wollte. Betroffen
ist jede Installation, die zwischen zwei Kaskaden Out-of-Loop-Fixe fährt — nach
meiner Erfahrung der Regelfall, nicht die Ausnahme; in diesem Projekt gibt es
`vor-5`, `vor-6`, `vor-8`, `vor-10`, `vor-13`, `vor-14` und jetzt `vor-15`.

**Es fällt nicht von selbst auf.** Beide Zeilen sind für sich plausibel, das
Ledger bleibt in sich stimmig, `--ledger-pruefen` schweigt zur Höhe, und
`--budget` zeigt eine korrekte Gesamtsumme. Aufgefallen ist es hier nur, weil
ich die erwartete Zahl (3,2621) aus der Warnung im Kopf hatte und die
gedruckte Erfolgsmeldung dagegen gelesen habe. Wer die Meldung überblättert,
merkt nichts — und die Belege sind dann bereits archiviert.

**Die Reihenfolge macht es schlimmer:** Die Warnung erscheint *nach* dem Lauf,
also genau dann, wenn die frischen Laufkosten unarchiviert danebenliegen. Der
empfohlene Befehl trifft damit immer den ungünstigsten Zeitpunkt.

## Was ich schon versucht habe

Korrigiert habe ich von Hand mit vier `--akteur-abschluss … --ersetzen`-Aufrufen
(`roles`/`ralph` je für `vor-15` und die echte Kaskadennummer), jeweils mit
explizitem USD-Wert und der Rechnung im Notiztext. Die Prüfsumme stimmt wieder,
die Rohlogs liegen im Archiv und bleiben gegenprüfbar. Das ist Handarbeit, die
das Werkzeug nicht nötig machen sollte.

**Vorschlag, drei Möglichkeiten — die erste scheint mir die richtige:**

1. **Zeitfenster für benannte Nummern aus dem Ledger ableiten.** Der Beginn
   einer `vor-N`-Runde ist das Ende der letzten gebuchten Kaskade (jüngste
   Ledger-Zeile mit Nummer < N), ihr Ende der Beginn von Kaskade N. Logs
   außerhalb dieses Fensters sind „zu neu" statt „zu alt" — derselbe Riegel,
   nur mit einer Obergrenze. Der Fall hier wäre damit sauber erkannt worden:
   Elf der vierzehn Logs liegen **nach** dem Beginn von Kaskade 15.
2. **Bei benannter Nummer die Log-Liste vorlegen und bestätigen lassen** —
   `--rollen-abschluss vor-N` bucht dann nur nach ausdrücklichem `--trotzdem`.
   Billiger zu bauen, aber es verlagert die Prüfung wieder auf den Menschen.
3. **Mindestens die Erfolgsmeldung sprechend machen:** Statt „9 Log(s)
   archiviert" die Zeitspanne nennen, die gebucht wurde („Logs von 2026-09-05
   17:39 bis 2026-09-06 15:24"). Das hätte es hier sofort gezeigt und ist
   unabhängig von den anderen zwei Wegen sinnvoll.

Was gegen einen reinen Dokumentationsfix spricht: Die Anweisung, die in die
Falle führt, ist bereits die *Korrekturanweisung* eines anderen Riegels. Wenn
der empfohlene Ausweg selbst eine Fehlbuchung erzeugt, hilft ein weiterer Satz
im Handbuch nicht — es braucht einen Riegel, der auch dort greift.

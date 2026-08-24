# P2 der Ledger-Pruefung uebersieht die Rolle und warnt bei JEDEM Closeout falsch

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-08-24-p2-der-ledger-pruefung-uebersieht-die-rolle-und-warnt-bei-je.md
      ./kit-melden.sh senden   2026-08-24-p2-der-ledger-pruefung-uebersieht-die-rolle-und-warnt-bei-je.md

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter. Drei
  Kaskaden gebaut und abgeschlossen, alle Rollen im Abomodus, eine Domäne.

## Was passiert ist

Beim Closeout der dritten Kaskade meldete die Ledger-Konsistenzprüfung —
sowohl in `--budget` als auch in `--ledger-pruefen` — wörtlich:

```
[WARNUNG] Kaskade 3 ist bereits gebucht (1 Zeile(n)), aber es liegen 13
unarchivierte Log(s) in .ralph-logs/.team-logs. Entweder lief danach noch eine
Rolle (dann `--rollen-abschluss ... --addieren`), oder der Abschluss lief ohne
--archivieren (dann zaehlt dieselbe Arbeit doppelt). Nicht einfach erneut
abschliessen: Der Default ueberschreibt nicht, aber ein --ersetzen hier
verliert den Altwert (BL-5).
```

**Keine der beiden angebotenen Ursachen traf zu.** Die eine gebuchte Zeile war
die `architekt`-Zeile der **Aushärtungs**-Sitzung. Die dreizehn unarchivierten
Logs waren die Rohbelege genau des Laufs, der gerade abgeschlossen werden
sollte — es hatte für diese Kaskade noch **überhaupt keinen** Rollenabschluss
gegeben.

Der Zustand war also der vollkommen normale „Kaskade gebaut, Closeout beginnt
jetzt". Die Warnung erschien trotzdem, mit zwei falschen Ursachen und zwei
Abhilfen, von denen eine (`--ersetzen`) beim Befolgen Geld aus dem Ledger
gelöscht hätte.

## Wo es steckt

`team/tools/kosten.py`, Prüfung **P2** der Ledger-Konsistenz. Die Bedingung
lautet sinngemäß:

```python
if aktuelle_kaskade is not None and aktuelle_kaskade in je_kaskade:
```

`je_kaskade` enthält **alle** Ledger-Zeilen der Kaskade, unabhängig von der
Rolle. Eine einzelne `architekt`-Zeile genügt daher, damit P2 die Kaskade für
„bereits gebucht" hält.

Die beiden Nachbarprüfungen machen genau diese Unterscheidung — und sagen im
Kommentar auch, warum:

- **P1** nimmt ausdrücklich aus: *„Kaskaden mit AUSSCHLIESSLICH einer
  architekt-Zeile bleiben ganz aussen vor: Das ist eine geplante, noch nicht
  gelaufene Kaskade."*
- **P1b** prüft ausdrücklich gegen die Rollenmenge:
  `not je_kaskade.get(aktuelle_kaskade, set()) & {"ralph", "roles"}`.

**Nur P2 fehlt die Ausnahme.** Der Fix wäre dieselbe Verengung wie in P1b:
nicht auf „irgendeine Zeile" prüfen, sondern auf eine Zeile aus
`{"ralph", "roles"}` — nur die entsprechen den Rohlogs, um die es P2 geht.
`LEDGER_OHNE_ROHLOG = ("architekt",)` steht im selben Modul und benennt genau
diese Trennung bereits.

## Warum das jede Installation trifft

Weil der auslösende Zustand nicht die Ausnahme, sondern der **vorgeschriebene
Ablauf** ist. Das Architekten-Briefing verlangt, dass eine Aushärtungs-Sitzung
ihre eigenen Kosten bucht, damit sie nicht dauerhaft aus dem Ledger fällt
(`BL-165`) — und sie bucht sie auf die Nummer der Kaskade, die gleich gebaut
wird. Ab diesem Moment existiert eine Zeile für die Kaskade, während die
Rohlogs noch entstehen.

Damit gilt: **Jede Kaskade, deren Aushärtung sich selbst bucht, zeigt diese
Warnung genau in dem Moment, in dem ihr Closeout beginnt.** Nicht gelegentlich
— strukturell, jedes Mal, in jeder Installation, die dem Briefing folgt. Zwei
Kit-Regeln arbeiten hier gegeneinander.

Der Schaden ist der, den dasselbe Modul an anderer Stelle für `BL-46` schon
beschreibt: *„Ein Waechter, der beim ersten Befolgen Geld kostet und sich nie
abstellen laesst, erzieht zum Wegsehen."* Genau das ist hier eine Prüfung
weiter noch offen. Und er trifft die teuerste Stelle: Das Architekten-Briefing
verlangt, dass kein Closeout mit unerklärtem Warnbefund schließt — der
Architekt muss den Fehlalarm also jedes Mal von Hand aufklären und begründet
im Abschluss-Doc ablegen, oder er gewöhnt sich an, `--ledger-pruefen` zu
überlesen. Beides ist teuer, das zweite ist gefährlich: Ab dann verschwindet
auch ein **echter** P2-Befund im Rauschen.

## Was ich schon versucht habe

- `--ledger-pruefen` gegen `--budget` gehalten, wie das Briefing es für den
  Zweifelsfall vorsieht: identischer Befund, weil beide dieselbe Funktion
  aufrufen. Die zweite Quelle klärt hier also nichts.
- Die Ledger-Zeilen und die dreizehn Rohlogs von Hand gegeneinander gerechnet.
  Ergebnis: nichts fehlte, nichts war doppelt; der `--rollen-abschluss` lief
  danach als ganz normale Erstbuchung durch (`ralph` und `roles` gab es für
  diese Kaskade noch nicht, der Kollisionsschutz schlug korrekt **nicht** an).
- **Keinen** der beiden vorgeschlagenen Wege benutzt. `--addieren` hätte eine
  Erstbuchung als Nachtrag getarnt, `--ersetzen` hätte den Betrag der
  Aushärtungs-Sitzung gelöscht.
- **Lokal nichts gepatcht.** Der Befund ist im Abschluss-Protokoll dieser
  Kaskade samt Begründung abgelegt, damit die Kaskade nicht mit einem
  unerklärten Warnbefund schließt.

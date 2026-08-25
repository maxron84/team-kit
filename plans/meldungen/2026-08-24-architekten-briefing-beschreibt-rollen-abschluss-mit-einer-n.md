# Architekten-Briefing beschreibt --rollen-abschluss mit EINER Notiz, das Werkzeug nimmt seit BL-34 zwei

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-08-24-architekten-briefing-beschreibt-rollen-abschluss-mit-einer-n.md
      ./kit-melden.sh senden   2026-08-24-architekten-briefing-beschreibt-rollen-abschluss-mit-einer-n.md

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
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter. Dritte
  Kaskade abgeschlossen, alle Rollen im Abomodus, eine Domäne.

## Was passiert ist

Beim Kostenabschluss der dritten Kaskade habe ich den Aufruf so abgesetzt, wie
das Architekten-Briefing ihn beschreibt — mit **einer** ausführlichen Notiz:

```
./team-status.sh --rollen-abschluss 3 <domaene> "<lange Notiz zum Lauf>"
```

Quittung:

```
Roles-Zeile Kaskade 3 (<domaene>) angelegt: 5.7687 USD …, 5 Log(s) archiviert
Ralph-Zeile Kaskade 3 (<domaene>) angelegt: 22.6490 USD …, 8 Log(s) archiviert
```

Beide Zeilen angelegt, Beträge korrekt, keine Warnung. Erst der Blick ins
Ledger zeigte, dass die **Bau-Zeile** meine Notiz nicht bekommen hat:

```
… | roles | Rollen: <meine lange Notiz> — abo … / api …
… | ralph | Bau: K3 chat — abo 22.6490 / api 0.0000
```

`Bau: K3 chat` ist aus dem Plandateinamen abgeleitet. Die Bau-Zeile trägt
damit **80 % der Lauf-Kosten und drei Wörter Prosa**.

## Wo es steckt

Nicht im Code — der ist richtig. In `team-status.sh` steht bei
`status_rollen_abschluss()` ausdrücklich:

> `BL-34`: Die beiden Zeilen bekommen GETRENNTE Notizen. Der dritte Parameter
> beschriftet die Rollen-Zeile (Harry/Marv/Frank/Axel), der optionale vierte
> die Bau-Zeile. Fehlt der vierte, wird die Bau-Notiz aus dem Plannamen
> ABGELEITET (`team_bau_notiz`) — der Text des Menschen wird nicht mehr auf
> eine Zeile kopiert, die er nicht beschreibt.

Das ist eine gute Änderung. Nur ist sie **im Briefing nicht angekommen**.
`team/prompts/rolle-architekt.md` beschreibt bis heute den Stand *davor*:

> Meine Notiz steht in **beiden** Zeilen, je mit eigenem Vorspann
> (`Rollen: …` / `Bau: …`) — sie ist die einzige Prosa-Spur je Ledger-Zeile.

Der Architekt liest also: „eine Notiz, sie landet in beiden Zeilen." Er
übergibt eine. Das Werkzeug macht seit `BL-34` etwas anderes. Die
Nutzungszeile nennt den vierten Parameter — aber sie erscheint nur bei
**falschem** Aufruf, und der Aufruf war nicht falsch.

## Warum das jede Installation trifft

Briefing und Werkzeug werden beide vom Kit ausgeliefert und widersprechen sich
in jeder Installation gleich. Der Fehler hat drei Eigenschaften, die ihn
schlecht auffindbar machen:

1. **Er meldet sich nicht.** Beide Zeilen entstehen, beide Beträge stimmen,
   der Exit-Code ist 0, `--ledger-pruefen` ist zufrieden. Es fehlt nur Prosa,
   und Prosa prüft niemand.
2. **Er trifft die teurere Zeile.** Bei uns trägt die Bau-Zeile 22,65 der
   28,42 USD des Laufs. Nach dem Abschluss sind die Rohlogs archiviert; die
   Ledger-Notiz ist dann das, was vom Lauf erzählend übrig ist — genau so
   sagt es das Briefing selbst („die einzige Prosa-Spur je Ledger-Zeile").
3. **Er ist nur einmal reparierbar, und nur mit dem gefährlichsten Verb.**
   Wer es später merkt, kann nicht einfach nachbuchen: Die Logs sind weg, ein
   zweiter `--rollen-abschluss` zählt 0. Der einzige Weg zurück ist
   `--akteur-abschluss ralph … --ersetzen` mit von Hand wiederholtem Betrag —
   also ausgerechnet das Verb, vor dem `BL-5` warnt, angewandt auf eine
   korrekte Zeile.

**Vorschlag:** Den Absatz im Architekten-Briefing auf `BL-34` nachziehen —
etwa: *„Der dritte Parameter beschriftet die Rollen-Zeile, der vierte die
Bau-Zeile. Lasse ich den vierten weg, wird die Bau-Notiz aus dem Plannamen
abgeleitet — dann steht an 80 % der Lauf-Kosten ein Dreiwort-Vermerk. Ich
schreibe **zwei** Notizen."* Zusätzlich denkbar: ein Hinweis in der Quittung,
wenn die Bau-Notiz abgeleitet statt übergeben wurde — sie ist ohnehin die
Stelle, an der der Architekt hinschaut.

Das ist derselbe Fehlertyp, den das Kit an anderer Stelle bereits als teuerste
Klasse führt: **Der Befehl, den die Doku einem Menschen nennt, stimmt nicht
mehr mit dem überein, was das Werkzeug tut** — und die Verifikation kann es
nicht sehen, weil sie über Beträge urteilt, nicht über Text.

## Was ich schon versucht habe

- Die Bau-Zeile nachträglich beschriftet:
  `--akteur-abschluss ralph abo 22.6490 <domaene> "<notiz>" --kaskade 3
  --ersetzen`, mit **unverändertem** Betrag. Gegenprobe per `diff` über die
  ersten sechs Ledger-Felder: nur die Zeilenposition hat sich geändert, kein
  Wert. `--ledger-pruefen` danach ohne Befund.
- **Am Kit lokal nichts geändert.** Der korrekte Aufruf (zwei Notizen) steht
  im Abschluss-Protokoll dieser Kaskade, damit der nächste Closeout ihn
  richtig absetzt — das ist Prosa in einem Projektdokument und überlebt kein
  `--update`.

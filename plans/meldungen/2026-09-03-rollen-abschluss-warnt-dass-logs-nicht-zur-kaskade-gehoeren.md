# rollen-abschluss warnt, dass Logs nicht zur Kaskade gehoeren, und bucht sie trotzdem darunter

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-09-03-rollen-abschluss-warnt-dass-logs-nicht-zur-kaskade-gehoeren.md
      ./kit-melden.sh ablegen  2026-09-03-rollen-abschluss-warnt-dass-logs-nicht-zur-kaskade-gehoeren.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-09-03-rollen-abschluss-warnt-dass-logs-nicht-zur-kaskade-gehoeren.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, kompilierte Sprache mit
  eigenem Test-Runner (nicht Python), dreizehn Kaskaden gebaut, rund 563 Tests,
  gut 180 abgerechnete headless-Laeufe im Bestand

## Was passiert ist

Beim Closeout einer Kaskade wurden die Rollenkosten gebucht:

```
./team-status.sh --rollen-abschluss 13 produkt
```

Die Ausgabe:

```
Hinweis: 1 Log(s) sind AELTER als der Beginn der Kaskade 13 (…) und werden
trotzdem unter dieser Nummer gebucht:
  .team-logs/frank-HM-62-v1-…json (…)
  Gehoeren sie zu einer Out-of-Loop-Runde zwischen zwei Kaskaden, gehoeren sie
  unter eine eigene benannte Nummer (`--kaskade vor-N`) — sonst traegt diese
  Kaskade fremde Kosten (BL-45).
Roles-Zeile Kaskade 13 (produkt) angelegt: 3.7260 USD …, 3 Log(s) archiviert
```

Das Werkzeug hat den Fall **erkannt**, die **richtige** Abhilfe **benannt** —
und dann das Gegenteil getan: Es hat das fremde Log mitgebucht und alle drei
Logs archiviert.

Damit ist der Zustand danach schlechter als vorher: Die Kosten stehen unter
der falschen Kaskade, **und** die Rohlogs sind bereits ins Archiv gewandert,
sodass ein zweiter Aufruf sie nicht mehr findet.

## Wo es steckt

Der Erkennungsteil liegt in `team/tools/kosten.py` (`logs_vor_kaskadenbeginn`),
der Buchungspfad in `team-status.sh` (`status_rollen_abschluss`).

Die Funktion ist da und funktioniert — sie wird im Wächter
(`--ledger-pruefen` / `--budget`) als **Warnung** ausgewertet. Auf dem
Buchungspfad wird derselbe Befund nur als Hinweistext gedruckt und hat keine
Wirkung auf den Ablauf.

## Warum das jede Installation trifft

Der Fehler steckt in einem Entrypoint plus einem Werkzeug des Kits, nicht in
Projektcode.

**Der Fall ist der Regelfall, nicht der Ausreißer.** Zwischen zwei Kaskaden
liegen Out-of-Loop-Fixe — dafür gibt es die Rolle „Frank" und die Konvention
`--kaskade vor-N`. Ein Frank-Lauf, der nach der letzten Buchung und vor dem
nächsten Kaskadenbeginn endet, fällt zwangsläufig in diese Lücke. Genau so lag
der Feldfall: Der Lauf endete um 23:07, der Kaskadenbeginn war 23:18, und die
Buchung der Runde davor war zu diesem Zeitpunkt bereits geschrieben.

**Die Korrektur ist Handarbeit am Ledger** — also genau das, was das Ledger
und seine Werkzeuge verhindern sollen. Ich musste die gebuchte Zeile in zwei
teilen (Kaskade und `vor-N`), die Beträge neu ausrechnen und die Prosa-Notiz
von Hand nachziehen. Wer das nicht bemerkt oder sich nicht zutraut, lässt die
falsche Zuordnung stehen; sie ist danach in keiner Prüfung mehr sichtbar,
weil `--ledger-pruefen` nur die **noch nicht archivierten** Rohlogs gegen das
Ledger hält.

**Der eigentliche Bruch ist die Bauart, nicht der Einzelfall.** Ein Werkzeug,
das eine Fehlzuordnung sicher genug erkennt, um sie zu benennen, darf sie
nicht ausführen. Es gibt in diesem Kit dieselbe Lehre bereits in der
Gegenrichtung: Die Umstellung von `geraet.sh --pruefen` auf echte Exit-Codes
(`Feld E`, `CF-34`) beruhte darauf, dass ein Befund, der nur als Fließtext
erscheint, an keiner Mechanik hängt und deshalb übergangen wird. Hier ist es
schärfer: Der Befund erscheint **und** die falsche Tat wird trotzdem
vollzogen.

## Was ich schon versucht habe

Lokal nichts repariert — der Fix gehört ins Kit.

Zwei Wege, absteigend nach Wirkung:

1. **Abbrechen statt buchen.** Wird ein Log gefunden, das älter ist als der
   Kaskadenbeginn, endet der Aufruf mit einem Exit ungleich `0`, ohne zu
   buchen und **ohne zu archivieren**; der Text nennt weiter `--kaskade vor-N`.
   Eine ausdrückliche Übersteuerung (`--auch-aeltere`) bleibt für den Fall,
   dass die Zuordnung wirklich stimmt. Das ist die Variante, die dem
   Exit-Code-Prinzip entspricht.
2. **Von selbst trennen.** Die älteren Logs unter `vor-N` buchen, die
   übrigen unter `N`, und beides ausgeben. Bequemer, aber es trifft eine
   Zuordnungsentscheidung ohne Rückfrage — was in einem Kostenledger
   vermutlich zu weit geht.

Wichtig ist bei beiden: **erst entscheiden, dann archivieren.** Dass die
Rohlogs schon weg sind, wenn der Mensch den Hinweis liest, macht die
Korrektur unnötig schwer — der Wächter zieht seine zweite Quelle genau aus
diesen Dateien.

Ergänzend, unabhängig vom gewählten Weg: Der Hinweis erscheint als
`Hinweis:` und ist damit von den harmlosen `[Hinweis]`-Zeilen des Wächters
nicht zu unterscheiden, von denen bei jedem Lauf mehrere stehen (typisch
sieben, alle gutartig). Als `WARNUNG:` wäre er das, was er ist.

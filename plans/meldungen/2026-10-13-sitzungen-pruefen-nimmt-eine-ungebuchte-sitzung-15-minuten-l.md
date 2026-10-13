# sitzungen-pruefen nimmt eine ungebuchte Sitzung 15 Minuten lang aus

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-13-sitzungen-pruefen-nimmt-eine-ungebuchte-sitzung-15-minuten-l.md
      ./kit-melden.sh ablegen  2026-10-13-sitzungen-pruefen-nimmt-eine-ungebuchte-sitzung-15-minuten-l.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-13-sitzungen-pruefen-nimmt-eine-ungebuchte-sitzung-15-minuten-l.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-10 (Folgefund zur Meldung „Vollautomatik startet trotz ungebuchter
  Planungssitzung der Kaskade“, im Projekt BL-3)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; zweite Kaskade

## Was passiert ist

Nach der ersten Kaskade war die Planungssitzung beim Start nicht gebucht. Der Commit
behauptete die Buchung trotzdem (im Projekt BL-3). Für die zweite Kaskade hat der
Architekt den Commit des Plans deshalb abgesichert, in der Scharfschalt-Sequenz:

```
python3 team/tools/kosten.py sitzungen-pruefen && git add … && git commit -m "…; Architekten-Sitzung … gebucht"
```

Der Stakeholder fuhr die Sequenz in einem eigenen Terminal, kurz nach der letzten
Antwort der Planungssitzung. Die Buchung der Sitzung (Schritt 1b) kam nicht im Ledger
an. `sitzungen-pruefen` meldete die Sitzung trotzdem nicht als Lücke:

```
  … <kennung>    7.7577 USD  laeuft noch (vermutlich diese Sitzung)
-- Keine Luecke: jede Sitzung im Fenster ist gebucht oder laeuft noch.
```

Exit 0, der Commit lief durch, und die Vollautomatik startete ohne Architekten-Zeile
für die Kaskade. Aufgefallen ist es erst nach dem Lauf, über
`./team-status.sh --ledger-pruefen` (Exit 4: „Kaskade 2 mit ralph-Zeile und ohne
architekt-Zeile“).

## Wo es steckt

`team/tools/kosten.py`, `sitzungen_pruefen()` mit `LAEUFT_MINUTEN = 15`. Ist die jüngste
Sitzung ungebucht oder mit Zuwachs und ihr Transkript jünger als 15 Minuten, bekommt
sie den Status „laeuft“ und zählt nicht als Lücke (BL-279: „die eigene Sitzung ist
nicht vergessen, sondern noch nicht fertig“).

Die Annahme dahinter gilt nur, wenn der Aufruf **aus** dieser Sitzung kommt. Die
Scharfschalt-Sequenz läuft aber typischerweise **danach** in einem anderen Terminal,
und genau in den 15 Minuten nach der letzten Antwort. Dann ist die jüngste Sitzung
nicht die prüfende, sondern die zu prüfende.

## Warum das jede Installation trifft

Das Architekten-Briefing legt den Kostenabschluss als ersten Schritt vor den Start
(Kit-BL-197, Kit-BL-291). Jede Prüfung, die danach mit `sitzungen-pruefen` absichern
will, dass er stattgefunden hat, läuft in dieses Fenster:
- ein Commit-Riegel wie oben;
- der Vorschlag aus der Folgemeldung zu BL-3, dass die Vollautomatik beim Start mit
  `sitzungen-pruefen` nach einer ungebuchten Planungssitzung fragt.

Beide würden die Lücke, für die sie gebaut sind, regelmäßig übersehen.

## Was ich schon versucht habe

Im Projekt sichert die Sequenz den Commit jetzt mit einer direkten Prüfung auf die
Architekten-Zeile der Kaskade im Ledger. Nach dem Lauf meldet `--ledger-pruefen` die
fehlende Zeile zuverlässig, vor dem Lauf gibt es noch keine Bau-Zeile, an der es sie
festmachen könnte.

Vorschläge, nicht ausprobiert:
- `sitzungen-pruefen --kaskade N`: Prüft, ob für Kaskade N eine Architekten-Zeile mit
  der Kennung der jüngsten Sitzung steht, ohne die „laeuft“-Ausnahme.
- Oder die Ausnahme nur gewähren, wenn der Aufruf erkennbar aus dieser Sitzung kommt.

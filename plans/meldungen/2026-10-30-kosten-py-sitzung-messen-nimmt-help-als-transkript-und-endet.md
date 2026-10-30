# kosten.py sitzung-messen nimmt --help als Transkript und endet im Traceback

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-30-kosten-py-sitzung-messen-nimmt-help-als-transkript-und-endet.md
      .\kit-melden.cmd ablegen  2026-10-30-kosten-py-sitzung-messen-nimmt-help-als-transkript-und-endet.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-30-kosten-py-sitzung-messen-nimmt-help-als-transkript-und-endet.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler im Werkzeug (Kleinigkeit)
- **Kit-Version**: 2.13.1
- **Bahn**: beide — `team/tools/kosten.py` ist für beide Bahnen dasselbe Werkzeug; aufgerufen aus Git Bash
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, Python; Kostenabschluss der fünften Kaskade

## Was passiert ist

Beim Kostenabschluss wollte der Architekt die Schalter von `sitzung-messen` nachlesen. Statt der
Hilfe kam ein Traceback:

```
$ python team/tools/kosten.py sitzung-messen --help
  File "team/tools/kosten.py", line 2311, in sitzung_messen
    with open(pfad, encoding="utf-8") as f:
FileNotFoundError: [Errno 2] No such file or directory: '--help'
```

Exit 1. Ebenso enden (ausgeführt, je letzte Zeile):

- `sitzung-messen -h` → `No such file or directory: '-h'`
- `sitzung-messen --bsi 2026-10-30T17:15:54Z <transkript>` (vertippt für `--bis`) →
  `No such file or directory: '--bsi'`
- `sitzung-messen gibt-es-nicht.jsonl` → `No such file or directory: 'gibt-es-nicht.jsonl'`

Ohne Argument kommt die Nutzungszeile (`Nutzung: kosten.py sitzung-messen (--projekt PFAD
[--alle] | TRANSKRIPT...) [--von ZEIT] [--bis ZEIT] [--ledger P]`, Exit 1), und `kosten.py --help`
druckt „Unbekannter Befehl: --help“ und die volle Nutzung.

Falsch gemessen wird nichts: Der Aufruf bricht ab, bevor er zählt. Wer den Befehl aber über
`--help` erschließen will, bekommt einen Absturz und liest den Quelltext.

## Wo es steckt

- `team/tools/kosten.py`, `_main`, Zweig `sitzung-messen` (Zeile 4112 in 2.13.1): Die Schleife
  kennt `--projekt`, `--alle`, `--von`, `--bis` und `--ledger`; jedes andere Argument hängt sie im
  `else` an die Liste der Transkripte an, auch eines mit `-` am Anfang.
- `sitzung_messen()` (Zeile 2311): öffnet jeden Pfad ohne Prüfung.
- Zum Vergleich: `turns`, `fallbacks`, `abdeckung` und `ledger` lassen Argumente mit `--` aus der
  Pfadliste heraus, `modelle` behandelt sie eigens. Dasselbe `else` wie hier steht noch bei
  `architekt-schaetzung` (Zeile 4500; gelesen, nicht ausgeführt).

Vorschlag: `-h`/`--help` drucken die Zeile aus `VERBEN` mit Exit 0; ein unbekanntes Argument mit
`-` am Anfang endet mit „Fehler: unbekannte Option …“ und der Nutzungszeile; ein Transkript, das
es nicht gibt, mit „Fehler: Transkript nicht gefunden: …“ — beides Exit 1, ohne Traceback.

## Warum das jede Installation trifft

Der Fehler steckt in `team/tools/kosten.py`, das jede Installation mitbringt, und das
Architekten-Briefing (`team/prompts/rolle-architekt.md`) schickt den Architekten beim
Kostenabschluss genau zu diesem Befehl.

## Was ich schon versucht habe

Nichts lokal gefixt. Umgangen: die Schalter aus der Nutzungszeile (Aufruf ohne Argument) und aus
dem Quelltext gelesen.

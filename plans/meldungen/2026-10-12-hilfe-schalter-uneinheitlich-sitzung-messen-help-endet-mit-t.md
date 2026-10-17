# Hilfe-Schalter uneinheitlich: sitzung-messen --help endet mit Traceback

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-12-hilfe-schalter-uneinheitlich-sitzung-messen-help-endet-mit-t.md
      ./kit-melden.sh ablegen  2026-10-12-hilfe-schalter-uneinheitlich-sitzung-messen-help-endet-mit-t.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-12-hilfe-schalter-uneinheitlich-sitzung-messen-help-endet-mit-t.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-1
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; erste Kaskade

## Was passiert ist

Der Architekt wollte vor der Scharfschalt-Sequenz die Schalter von
`sitzung-messen` nachlesen:

```
$ python3 team/tools/kosten.py sitzung-messen --help
  ! Keine abgerechneten Laeufe zum Eichen gefunden — die Zahl unten ruht allein auf der Preistabelle.
Traceback (most recent call last):
  ...
  File ".../team/tools/kosten.py", line 2234, in sitzung_messen
    with open(pfad, encoding="utf-8") as f:
FileNotFoundError: [Errno 2] No such file or directory: '--help'
```

`--help` wird als Transkriptpfad gelesen. Erwartet war die Nutzungszeile, die
`kosten.py` für das Verb kennt (`sitzung-messen (--projekt PFAD [--alle] |
TRANSKRIPT...) …`).

Ähnlich, aber ohne Traceback:

```
$ ./kit-melden.sh --hilfe
kit_meldung.py: error: the following arguments are required: verb
```

`Kit-BL-223` hat `--hilfe` für die Entrypoints eingeführt. `kit-melden.sh` reicht
es an `kit_meldung.py` durch, das es nicht kennt.

## Wo es steckt

`team/tools/kosten.py`, Verb `sitzung-messen`: Positionsargumente werden
ungeprüft als Pfade genommen. `kit-melden.sh` → `team/tools/kit_meldung.py`:
`--hilfe` fehlt im Parser (dort heißt es nur `-h`/`--help` je Verb).

## Warum das jede Installation trifft

Beide Stellen liegen in `team/` bzw. einem Entrypoint. `sitzung-messen` ruft
jeder Architekt in jedem Closeout auf; wer dort nach den Schaltern fragt,
bekommt einen Traceback statt einer Antwort.

## Was ich schon versucht habe

Nichts lokal gefixt. Ein Riegel wie bei den Entrypoints (unbekannter Schalter
→ Nutzungszeile, Exit 2) würde beide Fälle abdecken.

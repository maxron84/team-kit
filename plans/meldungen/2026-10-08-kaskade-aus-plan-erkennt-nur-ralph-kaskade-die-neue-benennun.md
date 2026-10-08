# kaskade_aus_plan erkennt nur ralph-kaskade-, die neue Benennung team-kaskade- faellt durch

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-08-kaskade-aus-plan-erkennt-nur-ralph-kaskade-die-neue-benennun.md
      .\kit-melden.cmd ablegen  2026-10-08-kaskade-aus-plan-erkennt-nur-ralph-kaskade-die-neue-benennun.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-08-kaskade-aus-plan-erkennt-nur-ralph-kaskade-die-neue-benennun.md   # sonst: Pull Request

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
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, 37 Pläne nach dem Muster
  `ralph-kaskade-N-…`. Gefunden beim Abgleich der Regeldatei nach dem Update vom 2026-10-08.

## Was passiert ist

Die Regeldatei-Vorlage nennt Plandateien jetzt `plans/team-kaskade-N-….md`. `PLAN_PRAEFIXE` in
`kosten.py`, die Plan-Erkennung in `lib.psm1` und `team-status` kennen beide Formen.
`kosten.py kaskade_aus_plan()` leitet die Kaskadennummer aus `.ralph-plan` ab und sucht dabei nur
`ralph-kaskade-(\d+)-`. Bei einem Plan nach neuer Benennung liefert sie `None`. Laut Docstring
verlangt der Aufrufer dann ein explizites `--kaskade`.

## Wo es steckt

`geteilt/tools/kosten.py`, `kaskade_aus_plan()`, der Regex `ralph-kaskade-(\d+)-`.

## Warum das jede Installation trifft

Jedes Projekt, das der neuen Vorlage folgt, verliert bei jeder Kaskade die automatische Nummer
im Kostenabschluss. Still ist der Fehler nicht, aber es ist dieselbe halbe Umstellung, gegen die
`PLAN_PRAEFIXE` gebaut wurde.

## Was ich schon versucht habe

Am Kit nichts. Vorschlag: den Regex aus `PLAN_PRAEFIXE` bilden, etwa
`(?:team|ralph)-kaskade-(\d+)-`, und einen Testfall mit neuer Benennung dazunehmen. Das Projekt
bleibt vorerst bei `ralph-kaskade-…`. Seine Regeldatei hält die alte Benennung ausdrücklich fest,
damit die 37 vorhandenen Pläne und neue nach demselben Muster heißen.

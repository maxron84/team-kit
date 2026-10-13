# Architekten-Briefing widerspricht sich, wenn TEAM_PYTHON python3 ist

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-13-architekten-briefing-widerspricht-sich-wenn-team-python-pyth.md
      ./kit-melden.sh ablegen  2026-10-13-architekten-briefing-widerspricht-sich-wenn-team-python-pyth.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-13-architekten-briefing-widerspricht-sich-wenn-team-python-pyth.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-9
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; zweite Kaskade

## Was passiert ist

Der Architekt las beim Aushärten sein Briefing und stieß im Abschnitt zur
Scharfschalt-Sequenz auf diesen Satz:

```
   Bahn bleibt eine `$env:`-Variable sonst in der Sitzung stehen, und der nächste
   Lauf fährt still mit dem Fokus und dem Deckel der vorigen Kaskade. Python
   heißt `python3`, nicht `python3`. Weiß ich die Bahn nicht, frage ich.
```

Der Satz widerspricht sich und sagt dem Leser nichts. Gemeint ist
vermutlich: Die Sequenz nennt den Interpreter so, wie er in dieser
Installation heißt.

## Wo es steckt

`geteilt/prompts/rolle-architekt.md`, Zeile 105 der Vorlage:

```
   heißt `{{PYTHON}}`, nicht `python3`. Weiß ich die Bahn nicht, frage ich.
```

Der Installer ersetzt `{{PYTHON}}` durch den Interpreter der Installation.
Heißt der `python3` — auf Linux und macOS der Normalfall —, steht derselbe
Name zweimal da. Lesbar ist der Satz nur in einer Installation, in der der
Interpreter anders heißt (etwa `py` oder `python`).

## Warum das jede Installation trifft

Das Briefing liegt in jeder Installation unter `team/prompts/`. Jede
Installation mit `python3` als Interpreter trägt den Widerspruch. Das ist die
Gattung „Literal statt Konfigurationswert“ (`BL-194`), diesmal in einem
Prosasatz: Der Wert ist eingesetzt, aber das danebenstehende Literal nimmt
an, er sei ein anderer.

## Was ich schon versucht habe

Nichts lokal geändert, `team/` bleibt unberührt. Vorschlag: den Vergleich
weglassen („Python heißt `{{PYTHON}}`, so wie in `TEAM_PYTHON`.“) oder ihn
nur ausgeben, wenn `{{PYTHON}}` nicht `python3` ist.

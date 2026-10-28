# Nachtrag: entfernte Modelle nur auf ausdrückliche Anweisung, Einrichtung je Anbieter, Abo oder API

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-28-nachtrag-entfernte-modelle-nur-auf-ausdrueckliche-anweisung.md
      .\kit-melden.cmd ablegen  2026-10-28-nachtrag-entfernte-modelle-nur-auf-ausdrueckliche-anweisung.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-28-nachtrag-entfernte-modelle-nur-auf-ausdrueckliche-anweisung.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: Meldung vom 2026-10-28 „Lokal oder entfernt je Rolle, jederzeit umschaltbar …“ — beantwortet deren offene Frage
- **Art**: Idee / Verbesserung — Auflage des Owners
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: wie in der Bezugsmeldung

## Was passiert ist

Die Bezugsmeldung ließ offen, ob „umgekehrt“ (eine Rolle zurück auf ein entferntes Modell) ein
Rückfall sein darf. Der Owner hat es danach entschieden, wörtlich:

> „die Nutzung entfernter Modelle wird dann nur mit expliziter Anweisung des Benutzers erfolgen,
> ggf mit Einrichtungsskript für bspw OpenRouter, Anthropic, OpenAI, etc. Abo oder Api, flexibel!“

## Wo es steckt

Wie in der Bezugsmeldung; dazu der Installer (Einrichtung der Anbieter) und die Auth-Auflösung,
die heute einen Anbieter kennt.

## Warum das jede Installation trifft

Wer lokal arbeitet, entscheidet selbst, ob und wohin Inhalte die Maschine verlassen. Ein stiller
Rückfall auf ein entferntes Modell nähme ihm genau diese Entscheidung ab.

## Was ich schon versucht habe

Nichts am Kit. Vorschlag, ohne Anspruch:

- **Nur ausdrücklich:** Eine Rolle nutzt ein entferntes Modell nur, wenn der Benutzer es für sie
  eingestellt oder für einen Lauf angewiesen hat. Scheitert eine lokale Rolle, übergibt sie an
  den Menschen, statt auszuweichen.
- **Einrichtung je Anbieter:** ein Skript, das einen Anbieter einrichtet (etwa OpenRouter,
  Anthropic, OpenAI) — je mit Abo oder API, wie es der Anbieter erlaubt.

# Franks Quittung ueberschreibt die Stand-Zeile, ein bewusst offener Rest der Erwartung steht nur im CHANGELOG

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-20-franks-quittung-ueberschreibt-die-stand-zeile-ein-bewusst-of.md
      .\kit-melden.cmd ablegen  2026-11-20-franks-quittung-ueberschreibt-die-stand-zeile-ein-bewusst-of.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-20-franks-quittung-ueberschreibt-die-stand-zeile-ein-bewusst-of.md   # sonst: Pull Request

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
- **Feldkürzel**: keins eingetragen — bitte vergeben (dasselbe Projekt wie die Meldungen vom 2026-11-02 und 2026-11-19)
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn; Workflow-XML mit Prüfkette in Python, rund 1 000 Tests; siebte Kaskade

## Was passiert ist

Ein Fund verlangte zwei Dinge: (1) ein Fehler im HTML-Leser soll nicht mehr
den ganzen Mailtext verschlucken, (2) ein Textteil, der trotz Inhalt keine
sichtbare Zeile ergibt, soll gemeldet werden, „nie still“. Frank baute (1),
und schrieb in den CHANGELOG-Eintrag: „Offen bleibt der zweite Teil der
Erwartung (Meldung bei Rohtext ohne sichtbare Zeilen): bewusst nicht gebaut.“

Die Fix-Phase meldete „HM-62 erledigt (Dreisatz verifiziert)“. Im Beutebuch
steht danach:

```
- **Status**: erledigt (Frank-Fix, ff36f52)
- **Stand**: 2026-11-20 — Status auf 'erledigt (Frank-Fix, ff36f52)' gesetzt
```

Dass ein Teil der Erwartung offen ist, steht nur im CHANGELOG. Wer das
Beutebuch von oben liest — genau der Leser, für den `Kit-BL-277` die
Stand-Zeile nach oben geholt hat —, hält den Fund für vollständig erledigt.
Aufgefallen ist es erst im Closeout, bei der Probe an der Wirklichkeit:
Derselbe Leser verschluckte weiter Text (Text im Kopf des HTML), und es gab
weiterhin keine Meldung. Daraus wurde ein neuer Fund. Bei den beiden anderen
Fixen derselben Fix-Phase trug die Stand-Zeile dieselbe Formel. Dort fehlte
nichts, sie sagte aber auch nichts.

## Wo es steckt

- `team/tools/beutebuch.py`, `set`: schreibt bei jedem Statuswechsel
  `Stand: <Datum> — Status auf '<Status>' gesetzt` (`Kit-BL-277`). Den
  Halbsatz „was davon gebaut ist, was offen bleibt“ aus der Vorlage kann der
  Aufruf nicht mitgeben.
- Franks Quittung (Dreisatz-Prüfung der Fix-Phase) prüft Commit, CHANGELOG und
  Status, aber nicht, ob der CHANGELOG-Eintrag einen offenen Rest nennt, den
  der Fundblock nicht trägt.
- Inhaltlich ist es derselbe Engpass wie in der Meldung vom 2026-11-19 („Ein
  Fund, der den Menschen braucht, hat im Loop keinen Ausgang“): Für „Teil der
  Erwartung bewusst nicht gebaut“ hat Frank keinen Status. Also quittiert er
  `erledigt` und schreibt den Rest in Prosa.

## Warum das jede Installation trifft

`beutebuch.py set`, die Quittung und Franks Briefing liegen im Kit. Jede
Installation bekommt nach jedem Fix dieselbe inhaltsleere Stand-Zeile, und ein
offener Rest steht dann nur noch dort, wo ihn die planende Rolle nicht liest.

## Was ich schon versucht habe

Im Projekt die Stand-Zeilen der drei Funde von Hand nachgetragen und aus dem
offenen Rest einen neuen Fund gemacht. Vorschläge, ohne Rangfolge:

1. `beutebuch.py set <HM> <Status> --stand "<Halbsatz>"`, und Franks Briefing
   verlangt den Halbsatz bei `erledigt`.
2. `beutebuch.py lint` (oder die Quittung) meldet einen Hinweis, wenn der
   CHANGELOG-Eintrag des Fixes „offen“, „nicht gebaut“ oder „bleibt“ enthält
   und die Stand-Zeile nur die Formel trägt.
3. Ein eigener Status für „erledigt bis auf einen benannten Rest“ (etwa
   `teilweise erledigt (Frank-Fix, <commit>) — Rest: …`), den die Fix-Phase
   nicht als fertig zählt und der Abschlussbericht dem Architekten zeigt.

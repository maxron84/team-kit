# Rundenlimit-Warnung auch dann, wenn die Fix-Phase in der letzten Runde regulaer mit nichts mehr zu tun endet

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-25-rundenlimit-warnung-auch-dann-wenn-die-fix-phase-in-der-letz.md
      .\kit-melden.cmd ablegen  2026-11-25-rundenlimit-warnung-auch-dann-wenn-die-fix-phase-in-der-letz.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-25-rundenlimit-warnung-auch-dann-wenn-die-fix-phase-in-der-letz.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit (falsche Warnung)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: keins eingetragen — dasselbe Projekt wie die Meldungen vom 2026-11-02, 2026-11-19 und 2026-11-20
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn; Workflow-XML mit Prüfkette in Python; achte Kaskade

## Was passiert ist

Fix-Phase mit höchstens 12 Runden. In den Runden 1 bis 11 gab es jeweils
etwas zu tun (acht Fixe, drei Fehlversuche, eine Ermittlungsakte). Danach
steht im Log:

```
[18:26:48] Runde 12: nichts mehr zu tun — Fix-Phase beendet.
[18:26:48] ⚠ 1 Fund(e) stehen auf 'offen' und sind NIEMANDEM übergeben — die Fix-Phase sieht sie nicht (Kit-BL-259). …
[18:26:48] WARNUNG: Rundenlimit (12) erreicht — evtl. offene Funde, Mensch prüfen.
```

Die Fix-Phase war regulär fertig. Die zweite Zeile stimmt (ein Fund aus der
Ermittlung stand auf `offen`), die dritte nicht: Das Limit hat nichts
abgeschnitten.

## Wo es steckt

`vollautomatik.ps1`, nach der Schleife der Fix-Runden:

```
if ($runde -ge $maxRunden) {
    Log "WARNUNG: Rundenlimit ($maxRunden) erreicht — evtl. offene Funde, Mensch prüfen."
}
```

Die Bedingung gilt auch dann, wenn die Schleife in der letzten erlaubten
Runde per `break` endete („nichts mehr zu tun"). Die bash-Bahn habe ich nicht
geprüft.

## Warum das jede Installation trifft

Die Zeile steht im Kit. Sie trifft jeden Lauf, dessen Fix-Phase genau in der
Runde `maxRunden` fertig wird, und sie verlangt „Mensch prüfen" für einen
regulären Abschluss. Eine Warnung, die ohne Anlass kommt, erzieht dazu, auch
die berechtigte daneben zu überlesen.

## Was ich schon versucht habe

Nichts geändert (Datei des Kits). Vorschlag: einen Merker setzen, wenn die
Schleife mit „nichts mehr zu tun" endet, und die Warnung nur ohne ihn
drucken.

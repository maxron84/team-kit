# Der Hinweis aus Kit-BL-289 trifft jeden regelkonformen Fund aus dem Loop-Sweep

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-20-der-hinweis-aus-kit-bl-289-trifft-jeden-regelkonformen-fund.md
      .\kit-melden.cmd ablegen  2026-11-20-der-hinweis-aus-kit-bl-289-trifft-jeden-regelkonformen-fund.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-20-der-hinweis-aus-kit-bl-289-trifft-jeden-regelkonformen-fund.md   # sonst: Pull Request

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

Eine Vollautomatik, zwei Red-Team-Sweeps, drei Funde. Vor den Frank-Läufen
meldete die Fix-Phase bei zwei von drei Funden:

```
[HM-61] Hinweis (sperrt nicht): Der Block nennt einen Testbefehl, zitiert aber keine Ausgabe. Ist er ausgefuehrt? Ein Befehlsergebnis wird belegt, nicht hergeleitet (Kit-BL-289) — im Feld war der behauptete rote Test gruen.
```

Beide Blöcke waren regelkonform. Der Testbefehl stand als Erwartung darin, so
wie `CLAUDE.md` es für den Fall verlangt, dass der Finder nicht ausführen darf:

```
5. Reproducer: `python -m pytest -q tests/test_hm61_….py -rxX` — Erwartung: 1 xfailed (nicht ausgeführt, Read-Only).
```

Im Loop-Sweep darf das Red Team nicht ausführen; der Prompt aus
`team/redteam.ps1` sagt „Führe KEINE Reproducer/Skripte aus“. Jeder Fund, der
seinen Reproducer-Befehl nennt — was gute Praxis ist —, bekommt den Hinweis
also. Der dritte Fund bekam ihn nur deshalb nicht, weil er keinen Befehl
nannte. Beide Funde waren echt; die Gegenprobe im Closeout machte beide
Reproducer ohne Fix rot.

## Wo es steckt

`team/tools/beutebuch.py`, `hinweise_text`: Der Hinweis kommt, sobald ein
Backtick-Span mit einem Testläufer (`TESTBEFEHL_RE`) im Block steht und kein
Zitat oder Codeblock (`ZITAT_RE`). Die erlaubte zweite Form aus
`Kit-BL-289` — das Ergebnis als Erwartung, „soll rot werden“, „nicht
ausgeführt“ — erkennt die Prüfung nicht.

## Warum das jede Installation trifft

Die Prüfung und der Prompt, der das Ausführen verbietet, liegen beide im Kit.
In jeder Installation feuert der Hinweis damit bei fast jedem Fund aus dem
Loop-Sweep. Ein Hinweis, der beim Regelfall immer kommt, erzieht dazu, ihn zu
überlesen — auch in dem einen Fall, für den er gebaut ist (ein Fund, der ein
Befehlsergebnis als Beobachtung behauptet). Der Stakeholder las die beiden
Zeilen als Warnung über den Lauf.

## Was ich schon versucht habe

Nichts am Kit geändert. Vorschläge, ohne Rangfolge:

1. Steht in der Zeile des Befehls oder direkt danach „Erwartung“, „erwartet“,
   „soll rot“ oder „nicht ausgeführt“, entfällt der Hinweis.
2. Oder umgekehrt: Der Hinweis kommt nur, wenn der Block ein Ergebnis als
   Beobachtung behauptet („ist rot“, „zeigt“, „schlägt fehl“, „failed“) und
   nichts zitiert.
3. Für Funde mit Angreifer Harry oder Marv aus einem Loop-Sweep ist die
   Erwartungsform die einzig mögliche; dort kann der Hinweis auch ganz
   entfallen.

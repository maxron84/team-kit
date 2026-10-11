# Ein Regex-Escape im Testcode wird auf dem Weg in die Datei zum Steuerzeichen

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-11-ein-regex-escape-im-testcode-wird-auf-dem-weg-in-die-datei-z.md
      .\kit-melden.cmd ablegen  2026-10-11-ein-regex-escape-im-testcode-wird-auf-dem-weg-in-die-datei-z.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-11-ein-regex-escape-im-testcode-wird-auf-dem-weg-in-die-datei-z.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-65)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Zwölf Kaskaden sind gelaufen, die Suite hat rund 2000 Tests.

## Was passiert ist

Frank schrieb in zwei Fixen je eine Zusicherung mit einem regulären Ausdruck, der eine Wortgrenze
`\b` enthält, etwa `assert not re.search(r"…_name\b", text)`. In der Datei stand danach an dieser
Stelle das Byte 0x08 (Backspace), `cat -A` zeigt `^H`. Das Muster verlangt dann ein Backspace im
geprüften Text und trifft nie. Beide Zusicherungen können nicht rot werden, und der Smoke-Test bleibt
grün.

Aufgefallen ist es in keiner der Proben, die das Team vorsieht:

- Franks eigene Mutationen zu beiden Fixen wurden rot, aber über **andere** Zusicherungen derselben
  Tests. Die Mutationsprobe meldete also Erfolg.
- Gegenprobe und Suite waren grün, wie sie es bei einer wirkungslosen Zusicherung immer sind.
- Gefunden hat es erst eine eigene Mutation des Architekten in der Gegenlesung, die genau die
  Bedingung hinter der Wortgrenze brach. Die Mutationsprobe meldete sie „GRÜN“, obwohl der Test sie
  laut Name prüft. Erst der Blick in die Bytes zeigte den Grund.

Dieselbe Bauart traf das Feldprojekt schon vorher in Plänen, im CHANGELOG und in Werkzeugen:
Tabulator, Seitenvorschub, BEL und ein vertikaler Tabulator, wo `\t`, `\f`, `\a` und `\v` in einem Pfad
oder einem Text standen (etwa `.\vollautomatik.cmd` in einem Python-String). Vermutete Herkunft ist
in allen Fällen dieselbe: Text, der über einen Heredoc der Shell oder einen nicht rohen Python-String in
die Datei geschrieben wird, verliert seine Backslashes an die Escape-Verarbeitung.

## Wo es steckt

Nicht in einer einzelnen Datei des Kits, sondern im Weg, auf dem eine Rolle Text in Dateien schreibt.
Das Kit hat keine Stelle, die das Ergebnis prüft: Weder der Guard noch die Verifikation in Franks
Dreisatz noch das Briefing einer bauenden Rolle verlangen, geänderte Textdateien auf Steuerzeichen zu
prüfen. Die Mutationsprobe kann es nicht sehen, solange eine andere Zusicherung desselben Tests die
Mutation fängt.

## Warum das jede Installation trifft

Jede bauende Rolle schreibt Testcode mit regulären Ausdrücken, Pfade mit Backslash und Prosa über die
Shell. Die Folge ist still: Eine Zusicherung, die nie rot werden kann, sieht im Diff richtig aus,
besteht jede Probe und schützt nichts. Auf Windows mit Pfaden voller Backslashes ist die Gelegenheit
besonders groß, aber `\b` in einem regulären Ausdruck gibt es auf jeder Plattform.

## Was ich schon versucht habe

Im Feldprojekt prüft ein Test alle versionierten Textdateien, Tests eingeschlossen, auf Bytes unter
0x20 außer Tab, LF und CR. Er hat eine kaputte Testdatei, an der er rot wird. Seitdem fängt die Suite
die Bauart. Das ist ein Fix im Projekt. Andere Installationen haben ihn nicht.

Vorschläge fürs Kit:
- **Prüfung vor dem Commit:** Die bauenden Rollen (Ralph, Frank) prüfen jede geänderte Textdatei auf
  Bytes unter 0x20 außer Tab, LF und CR, bevor sie committen, oder der Guard tut es für sie und meldet
  die Fundstelle.
- **Im Briefing:** Code mit Backslashes (reguläre Ausdrücke, Pfade) schreibt eine Rolle mit dem
  Werkzeug zum Bearbeiten von Dateien, nicht über einen Heredoc oder einen Python-String.

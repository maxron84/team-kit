# Testlücken-Fund mit grün abgelegtem Reproducer kann Franks Abnahme nicht bestehen

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-29-testluecken-fund-mit-gruen-abgelegtem-reproducer-kann-franks.md
      .\kit-melden.cmd ablegen  2026-10-29-testluecken-fund-mit-gruen-abgelegtem-reproducer-kann-franks.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-29-testluecken-fund-mit-gruen-abgelegtem-reproducer-kann-franks.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: HM-11
- **Art**: Lücke in der Doku
- **Kit-Version**: 2.13.1 (installiert vom Stand nach 2.13.1, Kit-Commit `1ca387e`)
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, nur pwsh-Bahn; ein kleines Python-Prüfwerkzeug mit pytest-Suite. Erste Kaskade: 4 Stufen, 11 Red-Team-Funde.

## Was passiert ist

Marv fand eine Lücke in der Testabdeckung (HM-11, Schwere „klein"): Ein Test
schützte eine `.gitattributes`-Regel nur für zwei Dateiarten. Den Reproducer
legte Marv **grün und ohne `xfail`** ab — der neue Test war schon die
Behebung.

Frank lief danach dreimal in dieselbe Wand. Er fuhr die Gegenprobe, stellte
„nichts zu fixen" fest, legte nur `docs:`-Commits für CHANGELOG und Beutebuch
an und gab das Promise. Dreimal folgte der Rollback, weil die Abnahme einen
`fix(uat)`-Commit und einen Diff verlangt, der eine im Fund backtick-referenzierte
Datei berührt. Danach ging der Fund an Axel. Axel erklärte den Mechanismus und
fand eine echte Restlücke: Die Mutation `src/** -text eol=lf` überlebte den
Test. Erst damit hatte Frank etwas zu fixen, und es ging im ersten Versuch
durch.

Kosten des Umwegs: drei Frank-Versuche (0,41 USD) und eine Axel-Akte
(1,22 USD), zusammen rund 1,64 USD für einen Fund der Schwere „klein". Die
übrigen elf Fixe desselben Laufs gingen je im ersten Versuch durch, für
0,24–0,47 USD pro Fix.

## Wo es steckt

Zwischen zwei Regeln, die einzeln stimmen:

- **Beutezug-Dreisatz** (`CLAUDE.md`, Abschnitt Harry & Marv, Punkt 2): Den
  Test gleich mit anzulegen ist optional; ist er rot, dann `xfail` mit
  `strict=True`. Was gilt, wenn der Fund **selbst** eine Testlücke ist und der
  Reproducer damit schon die Behebung, sagt die Regel nicht.
- **Franks Abnahme** (`pwsh/entry/frank.ps1`, Zeilen 209–214: `$hatFixCommit`
  und `team_diff_beruehrt_fund`): verlangt einen `fix(uat)`-Commit mit
  Substanz. Für einen schon behobenen Testlücken-Fund ist das unerfüllbar.
  Axel schreibt dazu selbst: kein Fehler im Werkzeug, der Riegel tut, wofür er
  gebaut ist.

## Warum das jede Installation trifft

Testlücken-Funde („diese Prüfregel überlebt eine Mutation") sind für das Red
Team typisch, und der kürzeste Beleg ist der schon erweiterte, grüne Test. Jede
Installation, deren Red Team so einen Fund ablegt, zahlt drei Rollbacks und
eine Axel-Akte, bevor überhaupt jemand fixen kann.

## Was ich schon versucht habe

Nichts am Kit. Zwei Vorschläge, einer genügt:

- **Briefings von Harry und Marv:** Bei einer Testlücke den Reproducer als
  **roten** Test der fehlenden Zusicherung ablegen (`xfail(strict=True)`),
  nicht als schon erweiterten Test. Dann hat Frank einen roten Ausgangszustand
  und eine Datei, die sein Diff berühren muss.
- **Eigene Quittungsform** „durch Reproducer erledigt": Frank darf sie ohne
  `fix(uat)` setzen, wenn eine Mutation den Reproducer nachweislich rot macht.

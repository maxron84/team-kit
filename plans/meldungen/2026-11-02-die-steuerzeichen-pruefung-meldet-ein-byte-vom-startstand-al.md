# Die Steuerzeichen-Prüfung meldet ein Byte vom Startstand als Ergebnis des Laufs

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-02-die-steuerzeichen-pruefung-meldet-ein-byte-vom-startstand-al.md
      .\kit-melden.cmd ablegen  2026-11-02-die-steuerzeichen-pruefung-meldet-ein-byte-vom-startstand-al.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-02-die-steuerzeichen-pruefung-meldet-ein-byte-vom-startstand-al.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit (Meldung der Steuerzeichen-Prüfung, `Kit-BL-327`)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; rund 700 Tests

## Was passiert ist

Vollautomatik, Fixphase mit vielen kleinen Funden, je ein Frank-Lauf. Franks CHANGELOG-Eintrag zu
einem Fund schrieb ein `\r` aus dem Text als echtes CR in die Datei. Die Prüfung stoppte zu Recht:

```
[frank] STEUERZEICHEN im Ergebnis dieses Laufs (Kit-BL-327):
  CHANGELOG.md:53: 0x0D (CR), wahrscheinlich aus `\r` — …<Text des Eintrags>…
  ✗ 1 Steuerzeichen in 1 Datei(en) — geprueft: die Dateien der Commits <start>..HEAD (Kit-BL-327).
```

Der Mensch startete neu, ohne zu reparieren. Der nächste Frank-Lauf behob seinen Fund sauber,
schrieb seinen Eintrag ins CHANGELOG und stoppte an demselben Byte, jetzt als `CHANGELOG.md:54`,
wieder „im Ergebnis dieses Laufs“, Exit 45. Der dritte Lauf ebenso (`:55`). Erst dann fiel auf,
dass es immer dasselbe alte Byte war. Drei Stopps, zwei davon für ein Byte, das der gestoppte Lauf
nicht geschrieben hatte; die Zeilennummer wanderte, weil jeder neue Eintrag darüber landete.

## Wo es steckt

`team/tools/steuerzeichen.py pruefen --seit <start>`, aufgerufen von `team_steuerzeichen_pruefen`
(`team/lib.sh`, `team/lib.psm1`): Es nimmt die Dateien, die die Commits `<start>..HEAD` anfassen
(`git diff --name-only`), und liest jede ganz aus dem Commit. Ein Byte, das am Startstand schon in
der Datei stand, zählt wie ein neues, und die Meldung schreibt es dem laufenden Lauf zu.

## Warum das jede Installation trifft

Es trifft jede schreibende Rolle, sobald eine Datei, die sie anfasst, schon ein Steuerzeichen trägt —
vor allem Sammeldateien, in die jeder Lauf schreibt (CHANGELOG, Beutebuch, Backlog). Ein Byte
stoppt dann jeden weiteren Lauf, bis jemand es findet, und die Meldung zeigt dabei auf den falschen
Lauf.

## Was ich schon versucht habe

- Repariert: das Byte im CHANGELOG durch den Text `\r` ersetzt und committet; danach lief die
  Fixphase durch. Am Kit selbst nichts geändert.
- Vorschlag, ohne Anspruch: Ein Byte, das am Startstand schon in derselben Datei stand, als solches
  benennen („stand schon vor diesem Lauf da“, möglichst mit dem Commit, der es brachte) und dafür
  anders oder gar nicht stoppen; „Ergebnis dieses Laufs“ nur für neue Bytes. Einfachster Weg: nur
  die Zeilen prüfen, die der Diff `<start>..HEAD` hinzufügt.

# Die Commit-Zeile nach dem Update nimmt mit add -A fremde Aenderungen im Arbeitsbaum mit

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-04-die-commit-zeile-nach-dem-update-nimmt-mit-add-a-fremde-aend.md
      .\kit-melden.cmd ablegen  2026-10-04-die-commit-zeile-nach-dem-update-nimmt-mit-add-a-fremde-aend.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-04-die-commit-zeile-nach-dem-update-nimmt-mit-add-a-fremde-aend.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-41)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Sieben Kaskaden sind gelaufen. Der Produktivcode liegt in einem Unterordner der Wurzel,
  die Szenariodatei bearbeitet der Mensch zusätzlich in einem Editor, der direkt in den
  Produktivcode-Ordner speichert.

## Was passiert ist

Das Update endet mit einem Vorschlag zum Committen:

```
git -C "<ziel>" add -A; git -C "<ziel>" commit -m "chore: T.E.A.M. aktualisiert"
```

Der Mensch hatte vor dem Update im Editor eine Änderung an der Szenariodatei gespeichert, die
für den nächsten Lauf vorgesehen war: zwei Objekte gelöscht, damit fiel auch eine
Addon-Abhängigkeit weg. Sie lag noch uncommittet im Arbeitsbaum. Er führte die vorgeschlagene
Zeile aus. Damit steckte die erste Hälfte der Produktänderung im Commit „chore: T.E.A.M.
aktualisiert“, die zweite Hälfte (ein neu gesetztes Objekt) kam in einem eigenen Commit danach.

Geschadet hat es hier nicht, die Mission war vollständig und alle Prüfungen grün. Aufgefallen
ist es erst in der Gegenlesung nach dem nächsten Lauf, beim Abgleich der Vorbedingung mit dem Log.
Ein Update-Commit, der Produktivcode trägt, ist im Log nicht als solcher zu erkennen: Wer die
Geschichte nach Produktänderungen durchsieht, überspringt „chore: T.E.A.M. …“, und ein Sweep
über einen Commit-Bereich liest ihn als Infrastruktur.

## Wo es steckt

- `pwsh/install.ps1`, Zeile 1770 (Ende des Updates): `git -C "$Ziel" add -A; git -C "$Ziel" commit -m "chore: T.E.A.M. aktualisiert"`.
- `bash/install.sh`, Zeile 1520: dieselbe Zeile mit `&&`.
- Verwandt, aber weniger heikel: Die Einrichtung schlägt `add -A` mit „chore: T.E.A.M.
  eingerichtet“ vor (`pwsh/install.ps1`, Zeile 2259; `bash/install.sh`, Zeile 2181). In einem
  Bestandsprojekt trifft das dieselben fremden Änderungen.

Stand: Kit-Update vom 2026-10-04, die Zeilen stehen dort unverändert.

## Warum das jede Installation trifft

Die Zeile ist der Vorschlag des Updates selbst, und der Mensch übernimmt ihn wörtlich. Jedes
Update in einem Arbeitsbaum mit uncommitteten Änderungen nimmt diese mit, ohne sie zu nennen.
Das Update weiß, welche Dateien ihm gehören: `team/.kit-stand` führt sie mit Prüfsumme.

## Was ich schon versucht habe

Nichts am Kit. Vorschläge:

1. Nur die Pfade des Kits stagen, etwa aus der Liste in `team/.kit-stand` plus den Dateien,
   die das Update neu angelegt oder geändert hat.
2. Oder vor dem Vorschlag `git status --porcelain` lesen und jede Änderung außerhalb der
   Kit-Pfade nennen, mit dem Hinweis, sie vorher getrennt zu committen.

Im Projekt ist nichts gefixt. Die beiden Commits bleiben, wie sie sind, der Hergang steht im
Backlog.

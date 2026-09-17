# BL-255 legt .ralph-uebersprungen an, ohne sie zu ignorieren - der zweite Uebersprung bricht am eigenen Riegel ab

- **Bezug**: HM-144
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst plus
  Electron-Oberfläche, rund 1170 Tests, 24 gebaute Kaskaden.

## Was passiert ist

`BL-255` führt die zweite Quittungsform ein (`STUFE_N_UEBERSPRUNGEN`) und dazu
eine Buchhaltungsdatei `.ralph-uebersprungen`, die der Abschlussbericht liest.
Sie ist weder in den `.gitignore`-Block eingetragen, den das Kit bei der
Einrichtung selbst schreibt, noch in `$TEAM_GUARD_LAUFZEIT`.

**Damit stellt sich der Loop selbst ein Bein.** Ralphs eigener Riegel für die
zweite Quittungsform verlangt einen sauberen Baum — zu Recht, denn ein
Übersprung ohne Commit wäre von „nicht gelaufen" nicht zu unterscheiden:

```
if (@(& git status --porcelain | Where-Object { $_ }).Count) {
    Team-Fehler "Ralph: Stufe $stufe meldet sich als planmäßig übersprungen, lässt aber Uncommittetes liegen (BL-255)."
```

Der Ablauf:

1. Stufe N wird planmäßig übersprungen. Der Riegel prüft — Baum sauber, alles
   richtig. Danach entsteht `.ralph-uebersprungen` als **nicht ignorierte**
   neue Datei.
2. Ab hier ist `git status --porcelain` nie mehr leer.
3. Beim **zweiten** Übersprung desselben Laufs schlägt der Riegel an. Ralph
   bricht mit Exit 1 ab und meldet „lässt Uncommittetes liegen" — eine
   Diagnose, die auf sein eigenes Buchhaltungsartefakt zeigt und den Menschen
   zum `git status` schickt, wo er eine Datei findet, die der Loop selbst
   angelegt hat.

Zwei Folgefehler auf demselben Grund:

- Der `BL-41`-Selbstprüfungspfad committet bei Bedarf mit `git add -A`. Er
  nimmt das Artefakt mit ins Repo — als `feat(stufeN)`-Commit mit generischem
  Betreff.
- `team_rollback_rolle` filtert nur `$TEAM_GUARD_LAUFZEIT` heraus, löscht die
  Datei also bei jedem gescheiterten Rollenlauf. Dann kann der Abschlussbericht
  die übersprungenen Stufen nicht mehr ausweisen — die Zählung, für die
  `BL-255 (c)` gebaut wurde, ist weg. (Dieselbe Bauart wie die Gate-Datei aus
  `BL-256`, eigene Meldung.)

## Wo es steckt

- `ralph.ps1`, `$uebersprungenDatei = '.ralph-uebersprungen'` — die Datei
  entsteht hier, geprüft wird sie wenige Zeilen darüber.
- `team/lib.psm1`, `$TEAM_GUARD_LAUFZEIT` — die Liste der Artefakte, die ein
  Rollback verschont.
- Der `.gitignore`-Block „T.E.A.M.-Loop-Laufzeitartefakte", den der Installer
  schreibt. Dort stehen `.ralph-state`, `.frank-attempts`, `.team-focus-*` und
  die übrigen Zustandsdateien; die neue fehlt.

**Die drei Stellen gehören zusammen und werden bisher einzeln gepflegt.** Jede
neue Zustandsdatei muss an allen dreien nachgetragen werden, und keine davon
meldet sich, wenn sie vergessen wurde. Eine gemeinsame Quelle (eine Liste, aus
der `.gitignore`-Block, Guard-Muster und Installer gespeist werden) würde diese
Fundklasse schließen; beide Funde dieses Updates sind Belege dafür.

## Warum das jede Installation trifft

`.gitignore`-Block, Guard-Muster und `ralph.ps1` gehören dem Kit. Jede
Installation, die `BL-255` bekommt, bekommt den Fehler mit — sichtbar wird er
erst bei einer Kaskade mit **zwei** Abbruchbedingungen, also spät und unter
Kosten: Der Lauf bricht mitten in der Kette ab, und die Diagnose zeigt in die
falsche Richtung.

**Der Kit-Regressionstest zu `BL-255` ist grün** (508 bestandene Kit-Tests). Er
prüft die Quittungsform und die Riegel je für sich; dass der erste Übersprung
die Vorbedingung des zweiten zerstört, liegt zwischen ihnen.

## Was ich schon versucht habe

Lokal beide Dateien in den `.gitignore`-Block und in `$TEAM_GUARD_LAUFZEIT`
nachgetragen, mit Reproducer: Ein frisches Repo bekommt die `.gitignore` des
Projekts, danach wird `.ralph-uebersprungen` angelegt und `git status
--porcelain` gemessen — die Größe, an der Ralph tatsächlich misst. Eine
Gegenprobe mit einer gewöhnlichen neuen Datei beweist, dass die Messung
anschlägt. Ohne den Eintrag ist der Test rot.

**Der Eintrag in `TEAM_GUARD_LAUFZEIT` hat die bekannte Verfallszeit**
(`BL-42`/`BL-58`); der `.gitignore`-Eintrag dürfte überleben, weil das Update
Projektdateien nicht anfasst.

# Die gitignore-Vorlage kennt .ralph-state, aber nicht .vollautomatik-state - der Guard warnt bei jedem Rollenstart

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-05-die-gitignore-vorlage-kennt-ralph-state-aber-nicht-vollautom.md
      .\kit-melden.cmd ablegen  2026-09-05-die-gitignore-vorlage-kennt-ralph-state-aber-nicht-vollautom.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-05-die-gitignore-vorlage-kennt-ralph-state-aber-nicht-vollautom.md   # sonst: Pull Request

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
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn (`--nur-pwsh`), Python-Dienst
  plus Electron-Oberfläche, zehnte Kaskade.

## Was passiert ist

Die Vollautomatik schreibt ihren Phasenzustand während des Laufs in
`.vollautomatik-state`. Diese Datei ist **getrackt**, weil die
`.gitignore`-Vorlage des Kits sie nicht nennt — ihre drei Geschwister stehen
dort sehr wohl:

```
.ralph-logs/
.team-logs/
.ralph-state
```

`.vollautomatik-state` fehlt. Folge: Sobald ein Lauf die Phase wechselt, ist
der Arbeitsbaum dreckig, und der Guard meldet bei **jedem** Rollenstart:

```
[guard] WARNUNG: Der Arbeitsbaum ist beim Rollenstart NICHT sauber:
  .vollautomatik-state
[guard] Diese Pfade werden der Rolle nicht angelastet, solange sie unverändert bleiben.
[guard] Zwei schreibende Instanzen auf einem Arbeitsbaum sind trotzdem unzulässig — bitte committen.
```

Die Aufforderung „bitte committen" ist mitten im eigenen Lauf weder möglich
noch sinnvoll: Die Datei wird beim nächsten Phasenwechsel wieder beschrieben.
**Die Vollautomatik verstößt also gegen die Sauberkeitsregel ihres eigenen
Guards, und zwar zwangsläufig und bei jedem Rollenstart.**

Der Guard behandelt den Fall danach korrekt (kein Rollback, „nicht dieser
Rolle zugeschrieben"). Der Schaden ist nicht der Rollback, sondern die
**Entwertung der Warnung**.

## Wo es steckt

- Die `.gitignore`-Vorlage des Bootstraps — dort fehlt die eine Zeile.
- `vollautomatik.ps1` / `vollautomatik.sh` schreiben die Datei während des
  Laufs (im pwsh-Skript rund um die Zuweisung von `$phasenState`).
- Der Guard in `team/lib.psm1` / `team/lib.sh` prüft die Sauberkeit des
  Arbeitsbaums beim Rollenstart und sieht die Datei deshalb immer.

## Warum das jede Installation trifft

Die Datei kommt aus dem Kit, die Vorlage kommt aus dem Kit, der Guard kommt aus
dem Kit — es braucht kein Zutun des Projekts, damit der Fall eintritt. Jede
Installation, die die Vollautomatik benutzt, sieht die Warnung ab dem ersten
Lauf mit Phasenwechsel.

**Belegter Schaden: Alarmmüdigkeit, und sie hat im Feld schon zugeschlagen.**
In einem Lauf standen beim zweiten Red-Team-Sweep zwei Pfade in der Warnung —
die strukturelle Zustandsdatei und eine **echte** Fremdänderung (eine zweite
Instanz hatte im Plan-Ordner geschrieben). Der echte Fall stand direkt neben
dem Dauerfall und ging in ihm unter; bemerkt wurde er erst später beim Lesen
des Protokolls. Genau davor soll die Warnung schützen.

## Was ich schon versucht habe

Lokal behoben: die Zeile in `.gitignore` ergänzt und `git rm --cached
.vollautomatik-state`. Danach ist der Arbeitsbaum beim Rollenstart sauber und
die Warnung bedeutet wieder etwas. **Diese Korrektur hat eine Verfallszeit,
soweit die Vorlage sie überschreibt** — sie gehört deshalb in die Vorlage,
nicht in jede Kopie.

## Vorschläge

1. **Die eine Zeile in die `.gitignore`-Vorlage** des Bootstraps, neben
   `.ralph-state`.
2. **Bestehende Installationen mitnehmen:** Ein `--update` sollte melden, dass
   `.vollautomatik-state` noch getrackt ist, und `git rm --cached` vorschlagen.
   Die reine Vorlagenänderung erreicht die Bestandsprojekte nicht — dort ist
   die Datei bereits im Index, und `.gitignore` greift dann nicht mehr.
3. **Grundsätzlich, über diesen Fall hinaus:** Der Guard könnte die
   Zustandsdateien des Kits selbst von der Sauberkeitsprüfung ausnehmen,
   statt sich auf eine vollständige `.gitignore` zu verlassen. Er kennt ihre
   Namen ohnehin. Dann trifft derselbe Fehler auch keine Installation mehr,
   die ihre `.gitignore` selbst gepflegt hat.

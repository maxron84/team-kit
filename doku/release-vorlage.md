# Release-Vorlage — T.E.A.M.-Starterkit

Vorlage und Reihenfolge für die GitHub-Release-Seite
(`https://github.com/maxron84/team-kit/releases/new`).

## Warum es diese Seite überhaupt gibt

Ein Feldprojekt erfährt von einer neuen Kit-Version **nirgends automatisch**.
`install.sh --update` meldet, was es ersetzt hat — aber niemand ruft es auf,
solange er nichts von der neuen Version weiß. Der Release ist damit der einzige
Ort, an dem die Frage *„muss ich hier updaten, und was gewinne ich dadurch?"*
beantwortet wird. Genau danach ist die Vorlage gebaut: Der **Update-Befehl**
steht in den Notes, nicht nur die Fundliste.

Das ist die `BL-129`-Familie in ihrer Release-Spielart: Zwischen „im Kit
erledigt" und „hier wirksam" liegt ein Installationsschritt, den kein Prozess
terminiert.

## Konventionen

| Feld der Seite | Wert |
|---|---|
| **Tag** | `vMAJOR.MINOR.PATCH` — mit `v`, exakt die CHANGELOG-Version |
| **Target** | `master` |
| **Release title** | `vX.Y.Z — <Kernsatz der Version>` (derselbe Satz, der im CHANGELOG fett über dem Abschnitt steht) |
| **Release notes** | nach der Vorlage unten |
| **Release label** | **None**. `Pre-release` nur für Fassungen, die bewusst noch **nicht** in ein Feldprojekt sollen — die Voreinstellung der Seite ist nicht immer `None`, also hinsehen. Ein als Pre-release veröffentlichter Stand wird nicht „latest" und wird beim Nachschauen übersehen |
| **Generate release notes** | nicht benutzen. Die Commit-Titel sind die Innensicht (`fix(BL-109): …`); die Notes sollen die **Außensicht** tragen |

**Versionssprung** nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/)
und SemVer, gemessen am Zielprojekt: `MAJOR` — ein Update bricht bestehende
Installationen (Config-Wert entfällt, Entrypoint umbenannt). `MINOR` — neue
Mechanik oder neuer Config-Wert, `--update` bleibt gefahrlos. `PATCH` — nur
Behobenes und Doku.

## Reihenfolge (vor dem Klick auf *Publish release*)

Die Notes sind das **letzte** Glied, nicht das erste — sie zitieren, was in
den Dateien schon steht.

1. `CHANGELOG.md`: `## [Unreleased]` stehen lassen, darunter
   `## [X.Y.Z] — <Datum>` mit einem Absatz, der die Version in **einem** Satz
   fasst. Die Einträge selbst sind zu diesem Zeitpunkt schon geschrieben.
2. `README.md`: den Absatz **Stand: Version …** nachziehen (Versionsnummer,
   Datum, zwei bis drei Sätze) und die genannte **Testzahl**.
3. `kit-test.sh`: die Zahl im Kopfkommentar (`Stand X.Y.Z: N Fälle in M
   Dateien`) — sie veraltet sonst still.
   Ist-Zahlen holen: `./kit-test.sh` (Schritt 4 druckt „N passed") und
   `ls team/tests/test_*.py | wc -l`.
4. `plans/backlog.md`: abgetragene Einträge ins Archiv, Statuszellen prüfen
   (`BL-53`: die Auflösung gehört an den **Anfang** der Zelle, nicht hinter
   das alte „offen." — sonst liest sich die Zeile maschinell weiter als offen).
5. `./kit-test.sh` **muss grün sein** — alle acht Schritte. Ein Release ohne
   diesen Lauf behauptet eine Zusicherung, die niemand geprüft hat.
6. Committen, dann taggen und veröffentlichen (Befehle unten).

## Die Vorlage

Alles zwischen den Linien in das Feld **Release notes** kopieren und die
`{{…}}` ersetzen. Abschnitte ohne Inhalt **ersatzlos streichen** — ein leeres
„### Behoben" erzieht zum Wegsehen (`BL-14`).

---

````markdown
{{EIN ABSATZ: worum es in dieser Version geht — derselbe Text wie im CHANGELOG
unter der Versionsüberschrift. Kein „diverse Verbesserungen": Wer im Feld
sitzt, will wissen, ob ihn das betrifft.}}

### Neu

- **{{Titel}}** (`{{BL-NR}}`). {{Was es tut, und woran man merkt, dass man es
  braucht. Feldbeleg mit Zahl, wenn es einen gibt.}}

### Behoben

- **{{Titel}}** (`{{BL-NR}}`). {{Der Fehler, sein Feldbeleg, die Behebung.}}

### Betrifft dich, wenn …

- {{Eine Zeile je Fund: die Lage im Zielprojekt, an der man erkennt, dass man
  den Fehler hat. Weglassen, wenn die Fundliste selbst schon so gelesen
  werden kann.}}

### Bestehendes Projekt aktualisieren

```
bash ~/Source/team-kit/install.sh --update <zielpfad>
git -C <zielpfad> add -A && git -C <zielpfad> commit -m "chore: T.E.A.M. aktualisiert"
```

Nie `--force` — das überschreibt Ledger, Kaskadenstand, Beutebuch und
`team.config.sh` (`BL-8`). `--update` fasst ausschließlich die Infrastruktur
an. **Nach dem Update committen, bevor der nächste Lauf startet**: Der
Read-Only-Guard wertet die uncommitteten Dateien in `team/` sonst als
Übergriff und räumt sie weg (`BL-10`). Nicht in einen laufenden Lauf hinein
aktualisieren — der Installer bricht dafür selbst ab.

{{Nur wenn es diesmal etwas gibt:}} **Von Hand nachzuziehen:** {{z. B. neue
Config-Werte, neue `.gitignore`-Zeilen — alles, was `--update` bewusst nicht
anfasst, weil es Projektdatum ist. Der Installer meldet es beim Lauf.}}

### Neu installieren

```
bash ~/.claude/scripts/team-init.sh <zielpfad>
```

### Geprüft

`./kit-test.sh` grün — {{N}} Regressionstests in einer echten Installation,
zweimal (Auslieferungswerte und angepasste `team.config.sh`), dazu
Update-Pfad, Einzug in eine gewachsene Codebasis und das Regel-Inventar.

**Vollständige Änderungen:** [CHANGELOG.md](https://github.com/maxron84/team-kit/blob/master/CHANGELOG.md)
{{· [Vergleich zu vX.Y.Z](https://github.com/maxron84/team-kit/compare/vX.Y.Z...vA.B.C) — NUR aufnehmen, wenn der Vor-Tag wirklich existiert. Lokal reichen die Tags nur bis v2.3.2; `git ls-remote --tags origin` sagt, was auf GitHub liegt. Ein Vergleichslink auf einen fehlenden Tag ist ein 404 an der prominentesten Stelle der Seite.}}
````

---

## Befehle

Den CHANGELOG-Abschnitt einer Version ausschneiden (Rohstoff für die Notes,
nichts von Hand abtippen):

```
awk '/^## \[2\.10\.0\]/{p=1;next} /^## \[/{p=0} p' CHANGELOG.md
```

Tag setzen und Release veröffentlichen — mit `gh` in einem Zug, die Notes aus
einer Datei:

```
git tag -a v2.10.0 -m "v2.10.0 — <Kernsatz>"
git push origin master --tags
gh release create v2.10.0 --target master --title "v2.10.0 — <Kernsatz>" --notes-file <datei>
```

Ohne `gh`: `git push --tags`, dann auf der Release-Seite den bestehenden Tag
im Feld **Tag** auswählen statt einen neuen anzulegen.

## Was NICHT in die Notes gehört

- **Die Fundtexte des Backlogs im Volltext.** Sie sind Innensicht mit
  Dateizeilen und Kostenbeträgen; der Release-Leser entscheidet nur, ob er
  updatet. Verlinken statt kopieren.
- **Zahlen ohne Bezug.** „369 Tests" sagt nichts, wenn nicht dabeisteht, wo
  sie gelaufen sind — in einer echten Installation, nicht im Kit-Repo.
- **Ankündigungen.** Was noch nicht committet ist, steht im Backlog, nicht im
  Release.

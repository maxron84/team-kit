# Der Commit-Block des Red-Team-Sweeps umgeht den Fremdfilter

- **Bezug**: BL-17
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Python + Electron.
  Fünf Kaskaden gebaut, Red Team läuft automatisiert im Sweep.

## Was passiert ist

Zwei Befunde derselben Wurzel: Der Read-Only-Guard nimmt seinen Schnappschuss
**beim Rollenstart**. Er beantwortet damit genau eine Frage — *war dieser Pfad
beim Start schon schmutzig und ist er es unverändert?* Daraus folgen zwei
Fälle, die sehr verschieden geschützt sind.

| | **Fall A** — lag **vor** Rollenstart im Baum | **Fall B** — entsteht **während** des Laufs |
|---|---|---|
| Schnappschuss kennt den Pfad | ja → gilt als fremd | nein → gilt als Werk der Rolle |
| `team_guard_verify` / `team_rollback_rolle` | geschützt (ausgefiltert) | wird zurückgesetzt bzw. gelöscht |
| Commit-Block des Sweeps | **wird mitcommittet** ← Befund 1 | wird mitcommittet — Befund 1 greift hier nicht |
| Ein Commit schützt? | ja | **nein** ← Befund 2 |

**Ausgelöst** hat die Prüfung ein Handgriff im Feld: eine Kit-Meldung wurde
manuell committet, mit der Begründung *„sonst ist Marv im Weg"*. Die Frage
dahinter war, ob Meldungen künftig sofort committet werden sollten. Die Antwort
ist nein — und der Weg dorthin legte beide Befunde frei.

## Wo es steckt

### Befund 1 — der Sweep staged den Testordner blanko

`team/redteam.ps1`, Commit-Block am Ende des Sweeps (in 2.13.1 bei Zeile 271):

```powershell
if (@(& git status --porcelain -- $TEAM_BEUTEBUCH $TEAM_TEST_ORDNER | Where-Object { $_ }).Count) {
    & git add $TEAM_BEUTEBUCH $TEAM_TEST_ORDNER | Out-Null
    & git commit -q -m "docs(beute): ...-Sweep über $rangeDesc — $fundText"
}
```

`git add <testordner>` nimmt **jede** untracked Datei darin mit, auch fremde.
Sie landet unter der Sweep-Botschaft (*„docs(beute): Marv-Sweep … — 1 neuer
Fund"*), also unter einer Urheberschaft, die nicht stimmt.

**Das ist eine Auslassung, kein Entwurf.** `team_guard_verify` und
`team_rollback_rolle` rufen beide `team_fremd_ausfiltern`. Der Commit-Block ist
die **dritte** Stelle mit derselben Zuständigkeit und die einzige ohne den
Filter — wörtlich die Bauform von `BL-114` (dort war der `git clean`
eingeschränkt, das `git reset --hard` daneben nicht). Zwei Stellen wurden
nachgezogen, diese nicht.

**Feldbeleg:** Beim Start einer Sitzung lag ein fremder Reproducer-Test
untracked im Testordner. Gut ausgegangen ist es nur, weil der Fixer den Fund
ohnehin bearbeitete und die Datei regulär mitnahm — nicht, weil der Guard sie
geschützt hätte.

### Befund 2 — ein Commit überlebt den Rollback nicht

`team/lib.psm1`, `team_pfade_zuruecksetzen` (in 2.13.1 bei Zeile 1087)
entscheidet je Pfad per `git cat-file -e $StartHash:$pfad`:

- Exit 0 → bei Start getrackt → `git checkout $StartHash -- $pfad`
- Exit ≠ 0 → `git rm -rf --cached` + `Remove-Item -Recurse -Force`

Eine Datei, die es beim Rollenstart nicht gab, fällt **immer** in den
Lösch-Zweig. Ob sie inzwischen committet ist, ändert daran nichts:
`team_rollback_rolle` sammelt `git diff --name-only $StartHash HEAD` — der
fremde Commit ist darin —, `git reset --soft $StartHash` holt die Datei zurück
in den Index, danach greift der Lösch-Zweig.

**In einem leeren Repo nachgestellt** (Datei nach `$StartHash` angelegt *und*
committet):

```
--- Was team_rollback_rolle sammeln würde:
plans/kit-meldungen/fund.md          <- committet, trotzdem in der Liste
--- Die Weiche in team_pfade_zuruecksetzen:
git cat-file -e $StartHash:pfad  ->  Exit 128   (!= 0  =>  LÖSCH-Zweig)
```

## Warum das jede Installation trifft

Beide Stellen liegen in `team/` — in der Bibliothek und im Red-Team-Skript.
Jede Installation, deren Testordner beim Rollenstart fremde untracked Dateien
enthält, committet sie unter fremder Urheberschaft; jede Installation, in der
während eines Laufs von Hand geschrieben wird, verliert das Geschriebene beim
nächsten Rollback.

Der zweite Fall trifft besonders die Projekte, die den Rückkanal **benutzen**:
Eine Kit-Meldung entsteht typischerweise genau dann, wenn einem beim Zuschauen
etwas auffällt — also während ein Lauf läuft. Der Guard wertet sie dann als
Werk der Rolle.

Ein lokaler Fix im Feld hätte ein Verfallsdatum beim nächsten `--update`
(vgl. `BL-42`/`BL-58`), deshalb diese Meldung statt eines Eingriffs.

## Vorschlag

**Befund 1 ist deterministisch schließbar.** Die zu stagenden Pfade aus
`git status --porcelain -- $TEAM_BEUTEBUCH $TEAM_TEST_ORDNER` einsammeln, durch
`team_fremd_ausfiltern` schicken und **namentlich** stagen, statt den Ordner
blanko zu adressieren.

Dazu gehört ein Team-Regressionstest mit **beiden** Richtungen — sonst wird der
Fix grün, indem gar nichts mehr committet wird:

| Fall | Erwartung |
|---|---|
| fremde untracked Datei im Testordner (vor Rollenstart da) | **nicht** Teil des Sweep-Commits, bleibt unangetastet im Baum |
| eigener neuer Reproducer der Rolle | **weiterhin** Teil des Sweep-Commits |
| Beutebuch-Eintrag der Rolle | **weiterhin** Teil des Sweep-Commits |

Die zweite Zeile ist die eigentliche Absicherung: Der Sweep **soll** Reproducer
committen — genau das ist sein Beitrag.

**Befund 2 ist eine Entwurfsfrage, kein Einzeiler.** `team_fremd_ausfiltern`
*kann* per Konstruktion nichts über Pfade wissen, die nach dem Start entstanden.
Deshalb liegt hier eine Frage bei statt einer fertigen Lösung — mit der
Richtung, die der Code an sich selbst schon anlegt (`lib.psm1`, Kommentar bei
Zeile 1052):

> „Ein Rest, der liegen bleibt, ist sichtbar und behebbar; fremde Arbeit, die
> gelöscht wurde, ist weg."

Denkbare Richtung: Pfade, die ausschließlich von Commits berührt werden, die
**nicht** dem Botschaftsmuster der laufenden Rolle folgen, werden **gemeldet
statt gelöscht**. Bewusst als Vorschlag markiert — die Mustererkennung ist
fragil, die Fehlerrichtung aber die richtige.

## Was ich schon versucht habe

**Kein lokaler Fix**, bewusst: Beide Stellen liegen in `team/` und wären beim
nächsten `--update` weg. Im Feld gilt stattdessen eine Handregel in `TEAM.md` —
während ein Lauf läuft, gehört Handarbeit nicht in denselben Arbeitsbaum,
sondern in einen zweiten Klon oder hinter das Laufende.

**Verworfen: „kit-melden committet selbst."** Das war die naheliegende Antwort
auf den Auslöser und wäre falsch gewesen — zweifach. `neu` legt einen
**Entwurf** an; ein Werkzeug, das den ungeprüft committet, committet unfertige
Meldungen. Und wirksam gewesen wäre es ohnehin nicht: Gerettet hat den
Auslöser-Commit, dass er **vor** dem Rollenstart lag, nicht dass er ein Commit
war. Wirksam ist **vorher**, nicht **sofort**. Falls das Kit so etwas je bauen
soll, dann gekoppelt an `pruefen` mit Exit 0 — als eigener Vorschlag, nicht in
dieser Meldung.

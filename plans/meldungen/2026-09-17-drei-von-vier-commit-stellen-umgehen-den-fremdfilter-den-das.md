# Drei von vier Commit-Stellen umgehen den Fremdfilter, den das Kit dafuer hat

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1 plus Unreleased-Stand
- **Bahn**: pwsh (der Befund gilt für beide Bahnen, siehe unten)
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python und Electron, 25
  Kaskaden gebaut, rund 240 Testdateien. Ein Mensch und mehrere Rollen
  arbeiten in **einem** Arbeitsbaum.

## Was passiert ist

Ein Mensch wollte während eines laufenden Vollautomatik-Laufs eine
Dokumentationsdatei in den Plan-Ordner legen. Er konnte es nicht — und der
Grund ist eine Kit-Mechanik, nicht seine Vorsicht:

Läuft eine Stufe, und legt daneben jemand eine neue Datei in den Arbeitsbaum,
dann nimmt der Commit-Block der bauenden Rolle sie **mit**. Er staged mit
`git add -A`. Die fremde Datei landet danach unter einer Urheberschaft, die
nicht stimmt — und schlimmer: Löst danach ein Rollback aus, räumt
`git reset --hard` plus `git clean -fd` sie **weg**.

Es gibt im Kit kein Verbot dagegen. Es gibt nur die Gewohnheit des Menschen,
während eines Laufs den Arbeitsbaum nicht anzufassen — also eine Regel, die
niemand durchsetzt und die genau dann bricht, wenn jemand Neues dazukommt.

## Wo es steckt

**Das Kit hat die Lösung bereits gebaut und an einer von vier Stellen
eingesetzt.** `team_eigene_pfade` und `team_fremd_ausfiltern` (`lib.psm1`)
existieren genau dafür; ihr eigener Kommentar nennt den Hergang wörtlich:

> *„Committet eine Rolle eine fremde Datei aus so einem Ordner versehentlich
> mit (`git add -A` ist bei bypassPermissions der Normalfall), taucht sie
> danach als `plans/closeout.md` auf …"*

Gemessen am Kit-Quelltext, beide Bahnen:

| Stelle | pwsh | bash | Fremdfilter |
|---|---|---|---|
| Red-Team-Sweep | `redteam.ps1`:283 `git add -- @eigenePfade` | `redteam.sh`:310 | **ja** (`BL-206`) |
| Axel | `axel.ps1`:163 `git add $TEAM_PLAN_ORDNER` | `axel.sh`:156 | **nein** — Ordner blanko |
| Frank | `frank.ps1`:275 `git add $TEAM_BEUTEBUCH` | `frank.sh`:283 | **nein** — Einzeldatei, geringes Risiko |
| Ralph (`BL-41`-Fallback) | `ralph.ps1`:219 `git add -A` | `ralph.sh`:233 | **nein** — alles |

**`BL-206` ist damit auf genau eine seiner vier Geschwisterstellen angewandt
worden.** Der Eintrag beschreibt seinen eigenen Fehlermodus dabei präzise —
*„zwei Stellen nachgezogen, die dritte nicht"* —, und dieselbe Bauform liegt
jetzt eine Ebene höher noch einmal vor.

**Die Axel-Zeile ist die schärfste, nicht die Ralph-Zeile.** Sie staged den
**Plan-Ordner blanko**, und `git add` auf einen Ordner nimmt jede untracked
Datei darin mit. Der dokumentierte Geschädigte von `BL-114` war *„genau die
uncommittete Closeout-Ausgabe"* — die im Plan-Ordner liegt. Diese Commit-Stelle
zielt also unmittelbar auf die Datei, wegen der `BL-114` geschrieben wurde.

**Die zweite Hälfte steckt in den Briefings, nicht im Code.** Im Normalfall
committet nicht das Skript, sondern die Rolle selbst — die Skript-Blöcke oben
sind Auffangpfade. Und **kein einziges Rollen-Briefing sagt, was zu stagen
ist**:

- `rolle-ralph.md` verlangt *„ein Commit pro Stufe"* (Zeilen 4 und 23) und
  sagt zum Umfang **nichts**.
- `rolle-frank.md`:22 verlangt *„Code-Fix committen mit klarem Präfix"* und
  sagt zum Umfang **nichts**.
- `rolle-harry.md` und `rolle-marv.md` erwähnen Commits gar nicht.

Unter `bypassPermissions` ist `git add -A` der naheliegendste Griff — der
Kit-Kommentar nennt ihn selbst *„der Normalfall"*. Eine Rolle, die es nicht
besser gesagt bekommt, tut genau das.

## Warum das jede Installation trifft

Der Befund sitzt in `lib`, in drei Entrypoints und in den Rollen-Briefings —
also in allem, was ein `--update` überschreibt. Jede Installation, in der ein
Mensch **neben** dem Loop arbeitet, hat ihn.

Und dieser Fall wird häufiger, nicht seltener: Das Kit zieht mit `ablegen`
gerade Wege ein, die den Menschen **während** eines Laufs an die Tastatur
holen. Dasselbe Kit weiß das an anderer Stelle bereits — sein eigener Test zu
`ablegen` begründet den pfadgenauen Commit im Kit-Repo mit dem Satz *„ein
`git add -A` nähme fremde Arbeit mit (Lehre `BL-12`)"*. Im **Zielprojekt** gilt
dieselbe Lehre; dort ist sie nur nicht umgesetzt.

Damit sind es drei unabhängige Einträge — `BL-12`, `BL-114`, `BL-206` —, die
dieselbe Lehre auf drei Schauplätzen gezogen haben. Die Mechanik dafür steht
seit `BL-206` bereit. Sie ist nur nicht überall angeschlossen.

## Was ich schon versucht habe

**Lokal nichts gefixt, bewusst.** Der Befund sitzt vollständig in `team/` und
in den Entrypoints; ein Patch hier verfällt beim nächsten `--update` — in
diesem Projekt bereits dreimal nachgewiesen.

Behelf im Feld bisher: die **Regel** *„nicht committen, während eine Rolle
läuft"*, notfalls ein Sicherungszweig. Sie hat gehalten, solange derselbe
Mensch sie kannte. Sie ist aber keine Mechanik, und sie kostet: Am Meldetag
musste eine fertige Doku-Datei liegen bleiben, bis der Lauf durch war.

**Vorschlag, in der Reihenfolge der Wirkung:**

1. **Die drei Stellen durch `team_eigene_pfade` schicken**, wie es der
   Red-Team-Sweep seit `BL-206` tut. Für Axel und Frank ist das eine Zeile.
   Beide Bahnen gleich.
2. **Für Ralphs `git add -A` reicht das nicht** — eine bauende Stufe darf
   Dateien erzeugen, die niemand vorher kennt (Sperrdateien, Erzeugnisse), und
   eine Positivliste würde sie verschweigen. Tragfähig ist der
   **Startschnappschuss**, den das Kit für den Rollback ohnehin schon zieht:
   stagen, was sich **seit Rollenstart** geändert hat, **minus** dem, was beim
   Start bereits schmutzig oder untracked war. Das ist dieselbe Information,
   nur einmal in die andere Richtung gelesen.
3. **Einen Satz in jedes Rollen-Briefing**, das committet — „stage namentlich,
   was du selbst angefasst hast, nie `git add -A`". Ohne ihn greift die
   Mechanik nur im Auffangpfad, während der Normalfall der Vermutung der Rolle
   überlassen bleibt.

**Eine Randnotiz zum Meldeweg, weil sie denselben Fehler zeigt:**
`kit-melden neu` legt seinen Entwurf unter `<plan-ordner>/kit-meldungen/` ab —
also **in** den Ordner, den Axel blanko staged, und als untracked Datei, die
Ralphs `git add -A` mitnimmt. Diese Meldung hier musste deshalb über
`--meldungen` an einem Ort außerhalb des Arbeitsbaums entstehen. Das Flag gibt
es, es ist nur nirgends als der Weg beschrieben, der es bei laufendem Loop ist.

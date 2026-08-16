![T.E.A.M. — Toll, ein anderer macht's. Sechs Rollenkarten im Terminal-Look:
Ralph Wiggum (Bau-Loop), der Architekt (Plan & Closeout), Frank der Fixer
(Ad-hoc-Fixes) — die drei dürfen Code schreiben; Harry (Red Team Security),
Marv (Red Team Chaos) und Axel Foley (Forensik) sind read-only. Darüber der
Leitsatz: Finder ≠ Fixer.](team-banner.webp)

# T.E.A.M.-Starterkit

Ein vollständiges KI-Rollenteam auf Knopfdruck in ein Software-Projekt —
frisch angelegt **oder seit Jahren gewachsen**.

```bash
cd ~/Source/team-kit
bash install.sh ~/Source/mein-projekt
```

*(Kurzform von überall: `bash ~/.claude/scripts/team-init.sh <zielpfad>`)*

Ein Befehl, ein kurzes Aufnahme-Interview, danach liegen 75 Dateien im
Zielprojekt: der gehärtete Bau-Loop, das Read-Only Red Team, der Fixer, der
Forensiker, die Kostenmechanik, die Bootstrap-Dateien, die Bedienanleitung
`TEAM.md` und 369 Regressionstests.

**Stand: Version 2.10.0** (2026-08-16). Der Backlog des Kits ist wieder leer.
Neu: Der vierte `BL-41`-Ausgang — Log meldet Erfolg, Quittung fehlt — prüft
sich selbst, statt die Vollautomatik mitten in der Kaskade anzuhalten; im Feld
war der Fall neunmal aufgetreten und neunmal gleich ausgegangen. Behoben: ein
Kit-Test, der am Füllstand des Beutebuchs hing, und ein `install.sh --update`,
das ein gewachsenes `.gitignore` nie nachzog. Abgetragene Einträge stehen in
[plans/backlog-archiv.md](plans/backlog-archiv.md) (63 Stück).

---

## Was das T.E.A.M. ist

Sechs KI-Rollen unter der Regie **eines** Menschen (des *Strippenziehers*):

| Rolle | Aufgabe | Darf Produktivcode ändern? |
|---|---|---|
| **Ralph** | Bau-Loop, arbeitet den Plan Stufe für Stufe ab | ja |
| **Der Architekt** | plant Kaskaden, setzt Caps, macht den Closeout | nur im Ausnahmefall |
| **Frank** | Ad-hoc-Fixes außerhalb des Loops | ja |
| **Harry** | Red Team Security — greift an, fixt nicht | **nein** (Guard) |
| **Marv** | Red Team Chaos — bricht Dinge, fixt nicht | **nein** (Guard) |
| **Axel** | Forensiker für die harten Fälle, starkes Modell | **nein** (Guard) |

Tragendes Prinzip: **Finder ≠ Fixer.** Wer einen Fehler findet, behebt ihn nicht
selbst — das macht Frank. Jede Übergabe läuft über das Beutebuch und bleibt
nachvollziehbar.

## Herkunft

Der Code stammt aus dem Projekt `website-maxron-de`, wo er über **22 Kaskaden**
scharf gelaufen ist (2026-07-10 bis 2026-08-01): reale Red-Team-Funde `HM-1`…`HM-53`,
Frank-Fixes, wirksamer Read-Only-Guard. Er wurde **nicht neu geschrieben**, sondern
übernommen und parametrisiert — die teuer gelernten Details bleiben erhalten.

Seither läuft das Kit im Feldprojekt `team-kit_project_platformer`: **33 Kaskaden,
157 Stufen, 93 Red-Team-Funde `HM-1`…`HM-93`, 49 `vollautomatik.sh`-Läufe,
rund 1265 USD Abo-Gegenwert — vollständig geledgert** (Stand 2026-08-11). Aus
diesem Betrieb und aus Einzügen in fremde Codebasen kommen die Backlog-Einträge
`BL-1`…`BL-61`; was davon behoben ist, steht im [CHANGELOG](CHANGELOG.md) und
in [plans/backlog-archiv.md](plans/backlog-archiv.md), der Rest in
[plans/backlog.md](plans/backlog.md).

Die konzeptionelle Grundlage steht im LLM-Wiki des Autors
(`../llm-wiki/wiki/vorlagen/claude-md-ki-team.md`) — ein privates
Schwester-Repo, nicht Teil dieses Kits.

## Installation

```bash
bash install.sh <zielpfad> [--nicht-interaktiv] [--update|--force]
```

**Ein bestehendes Projekt auf eine neue Kit-Version heben:** `--update`. Es
fasst **nur** die Infrastruktur an (Entrypoints außer `team.config.sh`,
`team/lib.sh`, `team/redteam.sh`, `team/tools/`, `team/prompts/`,
`team/tests/`) und lässt Ledger, Kaskadenstand, Beutebuch, CHANGELOG, `plans/`,
`CLAUDE.md` und `team.config.sh` unberührt. Zum Schluss meldet es, welche
Doku-Dateien von der Kit-Fassung abweichen — die **Regeln** müssen von Hand
nachgezogen werden, sonst läuft die Doku der Mechanik hinterher.

> ⚠ **`--force` ist kein Update.** Es überschreibt auch Projektdaten:
> `.budget-ledger` wird geleert (Kostenhistorie weg), `.ralph-state` auf `1`
> zurückgesetzt (Kaskadenstand weg), das Beutebuch durch die leere Vorlage
> ersetzt (**alle Funde weg**), dazu `CHANGELOG.md`, `plans/*.md` und
> `team.config.sh` (Smoke-Test weg). Empirisch nachgestellt, siehe `BL-8`.
> `--force` ist nur für eine kaputte **Erst**installation gedacht.

**Voraussetzungen**: Zielpfad ist ein Git-Repository, `claude` im PATH,
Auth eingerichtet (`bash ~/.claude/scripts/team-auth-setup.sh`).

**Das Aufnahme-Interview:**

Jede Frage kommt mit einer kurzen Erklärung, was sie bewirkt und was ein
falscher Wert kostet. Die Reihenfolge ist Absicht: Erst werden die beiden
**Schreibordner** vergeben, danach erst der Prüfumfang — so ist beim Beantworten
klar, welche Ordner dort nicht mehr hingehören.

| Frage | Default | Bedeutung |
|---|---|---|
| Projektname | Ordnername | erscheint in Berichten und Ledger |
| Ordner mit dem Programmcode | `src/` | **tabu** für Harry, Marv, Axel — und zugleich der **Prüfumfang** des Sweeps |
| Ordner für Tests | `tests/` | wo Reproducer hindürfen (bleibt **deinem** Testrunner) |
| Ordner für Pläne und Berichte | `plans/` | Kaskaden, Beutebuch, Akten, Roadmap — **Schreibzone** der Read-Only-Rollen (`BL-51`) |
| Weiterer Code (außerhalb) | *(leer)* | Leerliste (`main.py bin/`): Code, der mitgeprüft wird, aber nicht unter dem Produktivcode-Ordner liegt. Im neuen Projekt leer, im Bestand entscheidend (`BL-52`). Der Installer listet dazu, was er in der Wurzel gefunden hat |
| Prüfbefehl (Smoke-Test) | *(leer)* | **der wichtigste Wert**, siehe unten |
| Technik in einer Zeile | *TODO-Zeile* | eine Zeile für `CLAUDE.md`, reine Doku |
| Kostenkonten (Domänen) | `produkt` | Arbeitsstränge **dieses** Projekts; eines reicht (`BL-9`) |
| Architekt committet selbst? | `n` | sonst liefert er die Befehle zum Kopieren |

Test- und Plan-Ordner im Prüfumfang nimmt der Installer **wieder heraus** und
sagt warum: Derselbe Ordner kann nicht zugleich tabu und Ablageort sein — sonst
stünde beides im selben Absatz des Rollen-Auftrags.

Der **Smoke-Test** ist der eine Befehl, mit dem eine Rolle feststellt, dass das
Projekt heil ist. Ralph schließt keine Stufe ohne ihn ab, Frank verifiziert keinen
Fix. Gibt es ihn noch nicht, bleibt das Feld leer — die Rollen melden das dann in
jedem Prompt als offenen Punkt, statt still ohne Sicherheitsnetz zu arbeiten.
Ihn nachzuliefern ist typischerweise Stufe 1 der ersten Kaskade.

Der Installer ist **idempotent**: Ein zweiter Lauf überschreibt nichts, sondern
meldet, was bereits vorhanden ist. `--force` überschreibt bewusst.

## Nach der Installation

```bash
# 1. Werte prüfen
$EDITOR team.config.sh          # der EINZIGE Ort für Projektwerte
$EDITOR CLAUDE.md               # TODO-Stellen füllen

# 2. Committen — VOR dem ersten Guard-Lauf!
git add -A && git commit -m "chore: T.E.A.M. eingerichtet"

# 3. Team-Tests (prüft NUR die Infrastruktur, nicht dein Projekt)
./team-test.sh

# 4. Erste Kaskade planen — Claude-Sitzung im Projektordner, Opus:
#    "Du bist unser Architekt, lies team/prompts/rolle-architekt.md."

# 5. Scharfschalten und starten
echo plans/ralph-kaskade-1-….md > .ralph-plan
./vollautomatik.sh

# 6. NACH dem Lauf — Closeout, sonst sind die Kosten blind
./team-status.sh --rollen-abschluss 1 produkt
./team-status.sh --architekt-abschluss <USD> produkt "Kaskade 1 geplant"
```

> **Warum vor dem ersten Lauf committen?** Der Read-Only-Guard betrachtet
> uncommittete Dateien außerhalb der Whitelist als Verletzung und räumt sie weg.
> Im Ursprungsprojekt hat das einmal die gesamte frisch gebaute Team-Infrastruktur
> gelöscht. Seitdem ist der Rollback chirurgisch — aber die Regel bleibt.

## In ein bestehendes Projekt

**Das T.E.A.M. kann sich in eine gewachsene Codebasis einarbeiten** — es braucht
kein leeres Repo. Die Rollen lesen den Bestand, der Architekt plant gegen ihn,
und das Kit legt sich **neben** deinen Code: eigene Entrypoints, ein `team/`-
Namensraum, `TEAM.md`. Deine Ordner werden nicht angefasst, dein Testrunner
bleibt deiner, der Smoke-Test ist im Bestandsprojekt meist schon vorhanden —
genau das Feld, das im leeren Projekt zuerst fehlt.

> **Belegstand.** Die Stellen, an denen die Defaults nur für ein Neuprojekt
> taugten, stammen aus einer fremden Bestandscodebasis (`Project-Family-ERP`,
> Python/tkinter, Einstiegspunkt in der Wurzel, `src/`, `bin/`, gewachsene
> `tests/`, belegtes `plans/`): erst **gelesen** (2026-08-11 → `BL-51`/`BL-52`,
> gebaut in 2.6.0), dann **installiert** (2026-08-13 → `BL-57`, gebaut in
> 2.8.0). Der Einzug förderte eine Klasse zutage, die kein Codelesen zeigt:
> Die Fragen waren richtig, aber so gestellt, dass sie falsch beantwortet
> wurden. **Noch nicht** gelaufen ist ein scharfer Bestandslauf mit Agenten.

**Zwei Stellen, an denen ein Bestandsprojekt anders liegt:**

| Falle | Warum sie nur im Bestand greift | Was das Kit tut |
|---|---|---|
| **Schreibzone** (`BL-51`) | Die Guard-Whitelist ist **positiv**: Harry, Marv und Axel dürfen Plan- und Test-Ordner schreiben und löschen. Zeigen sie auf ein belegtes `plans/`/`docs/` oder eine gewachsene Suite, haben die drei ausdrücklich als Read-Only geführten Rollen Schreibrecht auf Bestand — **der Guard schlägt dort nie an**. | Der Installer prüft beide Ordner, nennt die gefundenen Dateien samt Folge und bietet einen anderen Ordner an. Wer behält, bekommt den Bestand in `TEAM_*_ORDNER_BESTAND` vermerkt; die Rollen-Prompts nennen ihn als fremdes Eigentum. **Die harte Variante bleibt der eigene, leere Ordner** (`team-plans/`) — nur dort ist die Grenze Mechanik statt Auflage. |
| **Prüfumfang** (`BL-52`) | Der Sweep-Auftrag zeigte auf `TEAM_PRODUKTIVCODE` — **einen einzelnen Ordner**. Im Bestand liegen Einstiegspunkt (`main.py`), Build- und Deploy-Skripte regelmäßig daneben und wurden nie angegriffen. Ein Sweep, der `src/` sauber meldet, sieht dann aus wie ein sauberes Projekt. Das ist **keine** Guard-Lücke, sondern eine Prüfumfangs-Lücke. | Das Interview fragt danach; `TEAM_WEITERER_CODE` (Leerliste, Dateien und Ordner) kommt in Scope-Zeile, eiserne Regel und Franks Fix-Auftrag. **Mitgeprüft heißt genauso tabu**, nicht freigegeben. `--update` erinnert daran, wenn in der Wurzel ungeprüfter Code liegt. |

**Erste Kaskade im Bestand:** den Fokus auf die **Naht** zwischen Neuem und
Gewachsenem legen, nicht auf die neue Mechanik. Feld-Gegenprobe aus zwei
aufeinanderfolgenden Kaskaden (`BL-43`): Der Naht-Fokus brachte fünf Funde,
allesamt Wechselwirkungen; die Vorkaskade mit Fokus auf die neue Mechanik fand
dieselbe Fundklasse **nicht** — sie fiel erst dem Menschen in der Abnahme auf
und kostete vier Fixes außerhalb des Loops.

**Der Rest ist wie im Neuprojekt** — mit einer Betonung: Vor dem ersten
Guard-Lauf committen ist im Bestand keine Formalie, sondern der Unterschied
zwischen „uncommittete Team-Dateien" und „der Guard räumt sie weg".

## Aufbau des Kits

```
entry/                  Entrypoints — landen in der Wurzel des Zielprojekts
├── vollautomatik.sh    Orchestrator: Ralph → Red Team → Frank → Axel
├── halbautomatik.sh    Schrittweise, mit Halt beim Menschen
├── team-status.sh      Kontostand, Pipeline, Beutebuch-Übersicht
├── team-test.sh        Regressionstests der Team-Infrastruktur
├── ralph.sh frank.sh axel.sh harry.sh marv.sh
└── team.config.sh      ALLE Projektwerte an einer Stelle

team/                   Team-Namensraum — landet als team/ im Zielprojekt
├── lib.sh             1159 Z — Auth, Guard, Budget, 429-Mechanik, Kosten
├── redteam.sh          Gemeinsame Sweep-Logik von Harry und Marv
├── tools/              kosten.py (1569 Z), beutebuch.py (286 Z)
├── prompts/            Sechs Rollen-Briefings (inkl. Architekt)
└── tests/              54 Testdateien, 362 Testfälle

bootstrap/              CLAUDE.md- und TEAM.md-Vorlage, CHANGELOG, Beutebuch, Roadmap, …
install.sh              Der Installer
kit-test.sh             Selbstverifikation in 8 Stufen: installiert in ein
                        Wegwerf-Repo, fährt dort die Tests zweimal (Ausliefe-
                        rungswerte und angepasste team.config.sh), prüft
                        Update-Pfad, Bestandslage und Regel-Inventar — DAS Gate
                        vor jedem Release
kit-regelinventar.py    Prüfer für das Regel-Inventar (Stufe 8). Kit-only —
                        bewacht die Vorlage, nicht die installierte CLAUDE.md
plans/                  Roadmap und Backlog DES KITS (nicht die Vorlagen —
                        die liegen in bootstrap/ und werden installiert)
doku/anhang-a.md        Die Warum-Schicht: Bauentscheide und Feld-Betriebs-
                        lehren (A.0–A.10). Bleibt im Kit, wird nicht installiert
doku/regel-inventar.md  Jede Regel der Vorlage als NORM/HERLEITUNG/HISTORIE,
                        mit Träger und wörtlichem Zitat
```

### Im Zielprojekt

```
projekt/
├── vollautomatik.sh …  Entrypoints sichtbar oben — du tippst sie direkt
├── team.config.sh      die eine Konfigdatei
├── team/               Team-Infrastruktur (lib, tools, prompts, tests)
├── TEAM.md             Bedienanleitung für DICH — lies sie zuerst
├── CLAUDE.md CHANGELOG.md plans/
└── <dein-code>/        unberührt
```

**Das Kit fasst deine Ordner nicht an.** `tests/`, `scripts/` und dein
Produktivcode bleiben, wie sie sind — nichts Stack-Fremdes landet darin. Die
**eine** Ausnahme, und sie ist gewollt: In Test- und Plan-Ordner *dürfen* die
Rollen schreiben (Reproducer, Kaskadenakten). Im Bestandsprojekt ist das der
Grund für den eigenen Plan-Ordner — siehe `BL-51` oben.

## Betrieb

| Befehl | Wirkung |
|---|---|
| `./vollautomatik.sh` | Ganze Kaskade automatisch durchfahren |
| `./halbautomatik.sh <rolle>` | Einzelnen Schritt, Entscheidung beim Menschen |
| `./team-status.sh` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --budget` | Kontostand, API vs. Abo getrennt |
| `./team-status.sh --ledger-pruefen` | Ist für jede Kaskade alles gebucht? Gegenprobe gegen die archivierten Rohlogs (Exit `4` = Warnbefunde) |
| `./team-status.sh --altlast [N]` | Produktivdateien, die seit N Kaskaden in keinem Diff lagen — die Auswahlhilfe für einen Altlast-Sweep (`BL-40`) |
| `./team-test.sh` | Regressionstests der Team-Infrastruktur (pytest) |
| `bash <kit>/install.sh . --update` | Auf eine neue Kit-Version heben, ohne Projektdaten anzufassen |
| `python3 team/tools/beutebuch.py list` | Alle Funde mit Status |
| `python3 team/tools/zitat_lint.py` | Plandateien, die einen erledigten Backlog-Eintrag noch als offene Frage zitieren (`BL-50`) |

**Exit-Codes**: `0` = durchgelaufen · `1` = echter Fehler · `3` = nichts zu tun ·
`42` = Session-Limit, Lauf pausiert (kein Fehler, kein Datenverlust) ·
`43` = **Stufe fertig, Quittung fehlt** (`BL-41`, seit 2.5.0): Die Rolle hat
gearbeitet und das Log meldet Erfolg, aber das Promise fehlt — meist, weil sie
auf einen Hintergrund-Task wartete, den es headless nicht gibt. **Nicht neu
bauen.** Erst prüfen: committet? Suite grün? Dann von Hand quittieren. Im Feld
kostete das Verwechseln mit „Fehler" viermal die bereits bezahlte Arbeit
(zusammen 19,47 USD).

## Grenzen

- **Sprach- und stackagnostisch, aber python3 wird gebraucht.** Die Team-Werkzeuge
  sind Python und liegen unter `team/tools/`. Das ist eine Abhängigkeit der
  **Team-Infrastruktur** — auf einer Ebene mit `git`, `flock` und der Agenten-CLI —
  nicht deines Projekts. Verifiziert in Go-, Rust- und PHP-Projektstrukturen.
- **Im Feld gelaufen, aber an einem Projekttyp.** Die 33 Kaskaden stammen aus
  **einem** Feldprojekt (Python/pygame, von null aufgebaut). Jeder Lauf hat
  Kit-Fehler zutage gefördert — `BL-1`…`BL-56`, von der toten Fixphase über
  zwei Löcher in der Kostenerfassung bis zur vierten Fehlerklasse „Stufe
  fertig, Quittung fehlt". Die Erwartung ist nicht, dass das aufhört; die
  Mechanik dafür ist der Rückkanal Feld → Kit.
- **Bestandsprojekte: der Einzug ist belegt, der Betrieb nicht.** `BL-51`,
  `BL-52` und `BL-57` stammen aus einer echten gewachsenen Codebasis und sind
  gegen die nachgestellte Lage geprüft (`kit-test.sh`, Schritt 6). Was fehlt,
  ist eine Kaskade mit echten Agenten in einem Bestandsprojekt — bis dahin ist
  belegt, dass das Team dort **einzieht**, nicht, dass es dort **arbeitet**.
- **Noch nie gelaufen: Axel.** Der Forensiker hat in 33 Kaskaden keine einzige
  Ledgerzeile — sein Pfad ist getestet, aber nicht im Feld belegt.
- **Selbstverifikation**: `./kit-test.sh` installiert das Kit in ein
  Wegwerf-Repo und fährt dort die 362 Tests — **zweimal**: einmal mit den
  Auslieferungswerten, einmal mit angepasster `team.config.sh` (Caps,
  Commit-Präfixe, zwei Domänen). Der zweite Lauf ist die Lehre aus `BL-58`: In
  einer frischen Installation stehen dieselben Werte wie in `team/lib.sh`, ein
  Test, der die Zusicherung am *aufgelösten* Wert misst statt an der
  Bibliothek, ist dort immer grün — und wird erst im Feldprojekt rot.
  `pytest team/tests` **im Kit-Repo** schlägt dagegen erwartungsgemäß fehl —
  die Tests setzen die installierte Ablage voraus (Entrypoints in der Wurzel
  statt unter `entry/`).
- **Regeln ändern heißt: Inventarzeile nachziehen.** Stufe 8 prüft jede
  geltende Regel der Vorlage gegen `doku/regel-inventar.md` — wörtliches Zitat,
  und in welcher Datei es steht. Das verbietet keine Änderung, es macht sie
  sichtbar: Wer eine Regel umformuliert, verschiebt oder streicht, bekommt rot
  und muss die betroffene Zeile **benannt** nachziehen, statt sie stillschweigend
  verschwinden zu lassen.
- **Guard-Tests nur in Wegwerf-Repos.** Nie im echten Projekt.
- **`--permission-mode default` ist undokumentiert.** Die beiden Read-Only-Rollen
  (Harry/Marv über `redteam.sh`, Axel) rufen die CLI damit auf. Der Wert wird von
  Claude Code 2.1.206 **akzeptiert**, taucht in `claude --help` aber nicht mehr in
  der Auswahlliste auf (dort stehen `acceptEdits`, `auto`, `bypassPermissions`,
  `manual`, `dontAsk`, `plan`). Falls eine künftige CLI ihn entfernt, schlagen
  genau diese beiden Rollen fehl — dann den passenden Nachfolger einsetzen und
  die Guard-Wirksamkeit erneut gegen die CLI verifizieren (Anhang A.5).
- **Budget-Caps großzügig ansetzen.** Ein zu tiefer Pro-Fall-Cap wirft teure,
  aber plausible Fixes per Rollback weg und **vervielfacht** die Kosten
  (Feld-Lehre `HM-32`).

## Lizenz

[MIT](LICENSE) — © 2026 Max Ron.

Benutzen, ändern, weitergeben und in eigene Projekte einziehen ist ausdrücklich
erlaubt, kommerziell wie privat; es bleibt nur die Namensnennung. Das gilt
**auch für die 75 Dateien, die der Installer im Zielprojekt hinterlässt** — sie
lösen keine Lizenzpflicht für den Code des Zielprojekts aus. Der Code stammt aus
einem eigenen Projekt des Autors; das Urheberrecht liegt vollständig bei ihm.

Das gilt auch für den Banner: `team-banner.webp` ist aus der mitgelieferten
Quelle `team-banner.svg` gerendert und enthält kein fremdes Material.

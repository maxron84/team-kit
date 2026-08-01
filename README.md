# T.E.A.M.-Starterkit

Ein vollständiges KI-Rollenteam auf Knopfdruck in ein neues Software-Projekt.

```bash
cd ~/Source/team-kit
bash install.sh ~/Source/mein-neues-projekt
```

*(Kurzform von überall: `bash ~/.claude/scripts/team-init.sh <zielpfad>`)*

Ein Befehl, sieben Fragen, danach liegen 59 Dateien im Zielprojekt: der gehärtete
Bau-Loop, das Read-Only Red Team, der Fixer, der Forensiker, die Kostenmechanik,
die Bootstrap-Dateien, die Bedienanleitung `TEAM.md` und 30 Regressionstests.

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

Die konzeptionelle Grundlage steht im [LLM-Wiki](../llm-wiki/wiki/vorlagen/claude-md-ki-team.md).

## Installation

```bash
bash install.sh <zielpfad> [--nicht-interaktiv] [--force]
```

**Voraussetzungen**: Zielpfad ist ein Git-Repository, `claude` im PATH,
Auth eingerichtet (`bash ~/.claude/scripts/team-auth-setup.sh`).

**Die sieben Fragen:**

| Frage | Default | Bedeutung |
|---|---|---|
| Projektname | Ordnername | erscheint in Berichten und Ledger |
| Produktivcode-Ordner | `src/` | **tabu** für Harry, Marv, Axel |
| Test-Ordner | `tests/` | wo Reproducer hindürfen (bleibt **deinem** Testrunner) |
| Plan-Ordner | `plans/` | Kaskaden, Beutebuch, Akten, Roadmap |
| Smoke-Test-Befehl | *(leer)* | **der wichtigste Wert**, siehe unten |
| Domänen | `produkt team` | Kostentrennung Produktarbeit ↔ Team-Infrastruktur |
| Architekt committet selbst? | `n` | sonst liefert er die Befehle zum Kopieren |

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
├── lib.sh              871 Z — Auth, Guard, Budget, 429-Mechanik, Kosten
├── redteam.sh          Gemeinsame Sweep-Logik von Harry und Marv
├── tools/              kosten.py (1126 Z), beutebuch.py (280 Z)
├── prompts/            Sechs Rollen-Briefings (inkl. Architekt)
└── tests/              30 Testdateien, 151 Testfälle

bootstrap/              CLAUDE.md- und TEAM.md-Vorlage, CHANGELOG, Beutebuch, Roadmap, …
install.sh              Der Installer
kit-test.sh             Selbstverifikation: installiert in ein Wegwerf-Repo
                        und fährt dort die Tests — DAS Gate vor jedem Release
plans/                  Roadmap und Backlog DES KITS (nicht die Vorlagen —
                        die liegen in bootstrap/ und werden installiert)
doku/anhang-a.md        Bau-Anleitung und Betriebslehren
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
Produktivcode bleiben, wie sie sind — nichts Stack-Fremdes landet darin.

## Betrieb

| Befehl | Wirkung |
|---|---|
| `./vollautomatik.sh` | Ganze Kaskade automatisch durchfahren |
| `./halbautomatik.sh <rolle>` | Einzelnen Schritt, Entscheidung beim Menschen |
| `./team-status.sh` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --budget` | Kontostand, API vs. Abo getrennt |
| `./team-test.sh` | Regressionstests der Team-Infrastruktur (pytest) |
| `python3 team/tools/beutebuch.py list` | Alle Funde mit Status |

**Exit-Codes**: `0` = durchgelaufen · `1` = echter Fehler · `3` = nichts zu tun ·
`42` = Session-Limit, Lauf pausiert (kein Fehler, kein Datenverlust).

## Grenzen

- **Sprach- und stackagnostisch, aber python3 wird gebraucht.** Die Team-Werkzeuge
  sind Python und liegen unter `team/tools/`. Das ist eine Abhängigkeit der
  **Team-Infrastruktur** — auf einer Ebene mit `git`, `flock` und der Agenten-CLI —
  nicht deines Projekts. Verifiziert in Go-, Rust- und PHP-Projektstrukturen.
- **Im Feld gelaufen (2026-08-01).** Im Projekt `team-kit_project_platformer`
  ist eine vollständige Kaskade 1 durchgefahren: Ralph baute drei Stufen
  (je ~0,72 USD), Harry und Marv sweepten und fanden `HM-1`…`HM-3`, Frank fixte
  alle drei, und der Read-Only-Guard griff nachweislich. Gesamtaufwand der
  Kaskade: 9,42 USD, vollständig geledgert.
  **Der Lauf deckte drei Kit-Fehler auf**, die im Kit selbst behoben sind:
  eine tote Fixphase (`BL-1`, 2.2.1) sowie zwei Löcher in der Kostenerfassung
  (`BL-4`, `BL-5`, siehe `[Unreleased]`).
  **Noch nicht gelaufen**: Axel (Forensiker) und eine `vollautomatik.sh`-Kaskade,
  die alle vier Phasen in **einem** Durchlauf schafft — die Fixphase des ersten
  Laufs starb an `BL-1`, Frank lief danach über `halbautomatik.sh`.
- **Selbstverifikation**: `./kit-test.sh` installiert das Kit in ein
  Wegwerf-Repo und fährt dort die 151 Tests. `pytest team/tests` **im Kit-Repo**
  schlägt dagegen erwartungsgemäß fehl — die Tests setzen die installierte
  Ablage voraus (Entrypoints in der Wurzel statt unter `entry/`).
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

Privates Werkzeug. Der Code stammt aus einem eigenen Projekt des Autors.

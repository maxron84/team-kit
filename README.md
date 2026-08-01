# T.E.A.M.-Starterkit

Ein vollständiges KI-Rollenteam auf Knopfdruck in ein neues Software-Projekt.

```bash
bash ~/.claude/scripts/team-init.sh ~/Source/mein-neues-projekt
```

Ein Befehl, fünf Fragen, danach liegen 51 Dateien im Zielprojekt: der gehärtete
Bau-Loop, das Read-Only Red Team, der Fixer, der Forensiker, die Kostenmechanik,
die Bootstrap-Dateien und 25 Regressionstests.

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

**Die fünf Fragen:**

| Frage | Default | Bedeutung |
|---|---|---|
| Projektname | Ordnername | erscheint in Berichten und Ledger |
| Produktivcode-Ordner | `src/` | **tabu** für Harry, Marv, Axel |
| Test-Ordner | `tests/` | Reproducer und Regressionstests |
| Plan-Ordner | `plans/` | Kaskaden, Beutebuch, Akten, Roadmap |
| Smoke-Test-Befehl | *(leer)* | **der wichtigste Wert**, siehe unten |

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

# 3. Erste Kaskade planen (Claude-Sitzung, Rolle "Der Architekt")
#    Skizze in plans/roadmap-skizzen.md aushärten

# 4. Scharfschalten und starten
echo plans/ralph-kaskade-1-….md > .ralph-plan
./vollautomatik.sh
```

> **Warum vor dem ersten Lauf committen?** Der Read-Only-Guard betrachtet
> uncommittete Dateien außerhalb der Whitelist als Verletzung und räumt sie weg.
> Im Ursprungsprojekt hat das einmal die gesamte frisch gebaute Team-Infrastruktur
> gelöscht. Seitdem ist der Rollback chirurgisch — aber die Regel bleibt.

## Aufbau des Kits

```
kern/                   Was ins Zielprojekt wandert
├── team-lib.sh         821 Z — Auth, Guard, Budget, 429-Mechanik, Kosten
├── team.config.sh      Alle Projektwerte an EINER Stelle
├── ralph.sh            Bau-Loop
├── frank.sh            Fixer (Event-Loop am Beutebuch)
├── axel.sh             Forensiker (starkes Modell, ein Fall pro Aufruf)
├── harry.sh marv.sh    Red Team (dünn, sourcen redteam.sh)
├── redteam.sh          Gemeinsame Sweep-Logik + Guard
├── vollautomatik.sh    Orchestrator: Ralph → Red Team → Frank → Axel
├── halbautomatik.sh    Schrittweise, mit Halt beim Menschen
├── team-status.sh      Kontostand, Pipeline, Beutebuch-Übersicht
└── scripts/
    ├── kosten.py       952 Z — Ledger, Splits, Akteur-Abschluss
    └── beutebuch.py    Zustandsmaschine der Funde

prompts/                Rollen-Briefings (~20 Z je Rolle)
bootstrap/              CLAUDE.md-Vorlage, CHANGELOG, Beutebuch, Roadmap, …
tests/                  25 Regressionstests der Team-Infrastruktur
install.sh              Der Installer
doku/anhang-a.md        Bau-Anleitung und Betriebslehren
```

## Betrieb

| Befehl | Wirkung |
|---|---|
| `./vollautomatik.sh` | Ganze Kaskade automatisch durchfahren |
| `./halbautomatik.sh <rolle>` | Einzelnen Schritt, Entscheidung beim Menschen |
| `./team-status.sh` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --budget` | Kontostand, API vs. Abo getrennt |
| `python3 scripts/beutebuch.py list` | Alle Funde mit Status |

**Exit-Codes**: `0` = durchgelaufen · `1` = echter Fehler · `3` = nichts zu tun ·
`42` = Session-Limit, Lauf pausiert (kein Fehler, kein Datenverlust).

## Grenzen

- **Nicht end-zu-end getestet.** Verifiziert sind: Installation, Syntax,
  127 Regressionstests, Guard-Rollback, Idempotenz, Verhalten aller Rollen ohne
  Arbeitsvorrat. **Nicht** verifiziert ist ein vollständiger scharfer
  `vollautomatik.sh`-Lauf in einem neuen Projekt — der kostet echtes Geld und
  braucht einen echten Plan.
- **Guard-Tests nur in Wegwerf-Repos.** Nie im echten Projekt.
- **Budget-Caps großzügig ansetzen.** Ein zu tiefer Pro-Fall-Cap wirft teure,
  aber plausible Fixes per Rollback weg und **vervielfacht** die Kosten
  (Feld-Lehre `HM-32`).

## Lizenz

Privates Werkzeug. Der Code stammt aus einem eigenen Projekt des Autors.

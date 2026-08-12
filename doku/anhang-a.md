---
date: 2026-08-01
type: anleitung
tags: [anleitung, softwareprojekt, automatisierung, kosten, setup]
status: active
---

# T.E.A.M.-Skripte kontextabhängig generieren (Anhang A)

**Zusammenfassung**: Bau-Anleitung für die Team-Skripte der
[T.E.A.M.-Vorlage](../vorlagen/claude-md-ki-team.md) — Vorbedingungen, Generierungs-Reihenfolge,
Auth-Fallback, Read-Only-Guard, Budget-Governance, 429-Robustheit, Kostenerfassung und
Doku-Konsolidierung. Wird **einmal beim Einrichten** gebraucht, nicht im laufenden Betrieb.
**Quellen**: Feldprojekt `website-maxron-de`, Kaskaden 1–22 (2026-07-10 bis 2026-08-01);
ausgelagert aus [claude-md-ki-team](../vorlagen/claude-md-ki-team.md).
**Zuletzt aktualisiert**: 2026-08-01

---

> **Warum eigene Seite?** Diese Anleitung stand bis 2026-08-01 als „Anhang A" in der
> T.E.A.M.-Vorlage und machte dort **gut die Hälfte der Seite** aus (29,8 KB von 69,8 KB).
> Sie beschreibt aber **Einrichtungsarbeit**, nicht die Regeln, nach denen das Team danach
> arbeitet — und wurde deshalb ausgelagert. Die Abschnittsnummern **A.1–A.10 bleiben
> unverändert**, damit alle bestehenden Verweise („siehe Anhang A.7") weiter stimmen.
>
> Das ist dieselbe Schichtung, die **A.10** (unten) für die Regeldatei des Zielprojekts
> vorschreibt: geltende Regeln getrennt von Herleitung und Baugeschichte halten.

## Voraussetzung

Diese Anleitung setzt voraus, dass der Vorlagenblock aus
[claude-md-ki-team](../vorlagen/claude-md-ki-team.md) bereits als `CLAUDE.md` im Zielprojekt liegt
und die `{{PLATZHALTER}}` über das Aufnahme-Interview gefüllt sind. Erst danach werden die
Skripte gebaut.

---

## Anhang A — Team-Skripte kontextabhängig generieren

**Statt Skripte zu kopieren**, generiert die aufnehmende Instanz sie passend zum Zielprojekt — **sofern das zum Zeitpunkt des Einspielens möglich ist**.

## A.0 Bootstrap — was vor dem ersten Lauf existieren muss

*(Ergänzt 2026-08-01 aus der Inspektion des Feldprojekts `website-maxron-de`. Diese Liste fehlte bisher: Die Vorlage beschrieb die Skripte, aber nicht die Dateien, auf die sie zugreifen. Im Feldprojekt sind sie über 22 Kaskaden nebenbei entstanden — in einem neuen Projekt müssen sie **vorher** da sein, sonst scheitert der erste Lauf an einer fehlenden Datei statt an einem echten Problem.)*

Die Rollen lesen und schreiben an festen Stellen. Fehlt eine davon, bricht der Lauf ab oder — schlimmer — eine Rolle legt sie in einem geratenen Format neu an.

| Datei | Zweck | Startinhalt |
|---|---|---|
| `CLAUDE.md` | Regelquelle (der Vorlagenblock, Platzhalter gefüllt) | Vorlage |
| `CHANGELOG.md` | Übergabepunkt aller Rollen | Kopf + leerer `## [Unreleased]`-Block |
| `{{Plan-Ordner}}/roadmap-skizzen.md` | Ungehärtete Stränge | Überschrift + erste Skizze |
| `{{Plan-Ordner}}/backlog.md` | Aufgaben, die keine Kaskade sind | Überschrift |
| `{{Plan-Ordner}}/beutebuch.md` | Red-Team-Funde | Überschrift **+ `## Vorlage`-Block mit dem Fund-Format** + leerer `## Funde` |
| `{{Plan-Ordner}}/ermittlungsakten/` | Axels Ausgaben | leerer Ordner (`.gitkeep`) |
| `prompts/rolle-*.md` | Rollen-Briefings (A.10) | fünf Dateien, ~20 Zeilen |
| `{{ledger-datei}}` | Kosten-Basis, **committet** | leer anlegen |
| `{{Test-Ordner}}/` | Reproducer- und Regressionstests | leerer Ordner |

Der **`## Vorlage`-Block im Beutebuch** ist kein Schmuck: Harry und Marv schreiben ihre Funde direkt darunter und richten sich am Block aus. Ohne ihn divergieren die Fund-Formate ab dem zweiten Sweep, und die Zustandsmaschine (`beutebuch.py`) findet die Status-Zeilen nicht mehr.

**Reihenfolge:** Diese Dateien zuerst, dann A.1–A.2. Ein Skript, das gegen eine fehlende Datei läuft, produziert einen Fehler, der wie ein Skriptfehler aussieht, aber keiner ist.

## A.1 Vorbedingungs-Check (immer zuerst)

Vor jeder Skript-Generierung prüfen:

- **Git-Repo vorhanden?** (`git rev-parse --is-inside-work-tree`) — sonst nur die Doku-Sektion einspielen, Skript-Teil überspringen.
- **Claude-CLI verfügbar?** (`claude --version`) — bestimmt, ob Loop-Skripte überhaupt sinnvoll sind.
- **Existiert schon ein Loop?** (`ls {{loop-skript}}`) — falls ja, **nicht überschreiben**, sondern nur `team-lib.sh` + Rollen-Skripte ergänzen und den bestehenden Loop darauf umstellen.
- **Commit-Konvention** des Zielprojekts erfassen (`git log --oneline -20`) — bestätigt `{{fix-präfix}}` / `{{feat-präfix}}`.

## A.2 Was generiert wird (empfohlene Reihenfolge)

Referenz-Bausteine — nach dem bewährten Loop-Muster **beschrieben**, nicht als fertiger Code geliefert. Reifegrad wie angegeben:

1. **`team-lib.sh`** ✅ — gemeinsame Bausteine (Config-Sourcing, `flock`-Guard, Promise-Auswertung, Logging, Budget-Flags) + zentrale **Auth-Logik** (A.3). Im Feld gewachsen um: `team_claude` (Abo-first + API-Fallback, 429-Erkennung/-Retry, Exit 42), `team_guard_verify` (chirurgischer Guard), die Fehler-/429-Helfer (`team_result_is_error`, `team_result_is_429`, `team_429_reset_epoch`, `team_429_sleep`), die Kosten-Helfer (`team_kosten_summe`/`team_kosten_split`/`team_ledger_summe`/`team_kontostand_gesamt`/`team_kosten_seit` sowie einen Summierer über **alle** Versuchs-Logs eines Aufrufs, `BL-55`), `team_logs_archivieren` (Log-Rotation gegen Doppelzählung), `team_architekt_schaetzung` und `team_resolve_budget_cap`.
2. **`{{loop-skript}}`** ✅ — Ralph-Äquivalent: falls keiner existiert, nach dem Loop-Muster generieren; sonst auf `team-lib.sh` umstellen.
3. **`frank.sh`** ✅ — Event-Loop am Beutebuch (einfachster Loop, kein Guard): greift Funde mit Status `an Frank übergeben`, fixt nach Franks Dreisatz, Promise `<promise>FRANK_FIX_COMPLETE</promise>`, Versuchszähler (Default 3) → dann `an Mensch eskaliert`.
4. **Read-Only-Guard** ✅ — 3 Linien (A.4) + rollenspezifischer `pre-commit`-Hook (aktiv nur bei `{{ROLE-ENV}}=harry|marv`).
5. **`harry.sh` / `marv.sh`** ✅ — State = letzter geprüfter Commit-Hash; Trigger = neue Commits seit State (Angriff auf **stabilen** Code, idealerweise am Kaskaden-Übergang); Promise `<promise>REDTEAM_SWEEP_COMPLETE</promise>`; **Guard Pflicht**.
6. **Polling-Orchestrator (Vollautomatik)** ✅ — dünne Schleife, die die Loops sequenziell startet (`inotify`/`post-commit` als späterer Ausbau). Sprechend benennen (`vollautomatik.sh`; ein schrittweiser Bruder `halbautomatik.sh` mit Halt/Entscheidung durch den {{Strippenzieher}}) statt kryptischer Marken-Namen (Designhinweis 7). Erkennt **Exit 42** (Session-Pause, A.8) in **allen** Phasen und die **Stagnations-Bremse** (`TEAM_FIX_MAX_STAGNATION`) in der Fixphase; liest `BUDGET_EMPFEHLUNG_USD` aus dem aktiven Plan und hebt den Lauf-Deckel nur an (nie senken).
7. **Kosten-/Status-Werkzeug (`kosten.py` + `team-status.sh`)** ✅ — bündelt die Kosten-Summierung an **einer** Stelle (statt doppelt in `vollautomatik.sh`/`team-status.sh`); `--budget` zeigt den domänengetrennten Kontostand, `--akteur-abschluss` trägt echte interaktive Akteur-Kosten ein (A.9).
8. **`.gitignore`** ergänzen — vollständige Liste aus dem Feldprojekt (2026-08-01 nachgetragen, die frühere Kurzfassung war unvollständig):

   ```gitignore
   # Team-Loop-Laufzeitartefakte
   .{{rolle}}-logs/          # pro Rolle, z. B. .ralph-logs/ .team-logs/
   .team-loop.lock
   .{{rolle}}-state          # z. B. .ralph-state .harry-state .marv-state
   .ralph-plan               # Zeiger auf den aktiven Plan
   .frank-attempts           # Versuchszähler des Fixers
   .budget-ledger.lock       # Lock der Ledger-Datei (Race, HM-48)
   backups/
   ```

   **Nicht** ignorieren: die `{{ledger-datei}}` selbst — sie ist die committete Kostenbasis. Die drei zuletzt genannten Einträge fehlten in der bisherigen Anleitung; `.ralph-plan` und `.budget-ledger.lock` sind dabei die wichtigsten, weil sie sonst als Arbeitsverzeichnis-Änderung im Read-Only-Guard auftauchen.

> **Ablage-Konvention (Feld-Lehre website-maxron-de, 2026-07-11):** Die
> **Orchestrierungs-Entrypoints** (`vollautomatik.sh`, `halbautomatik.sh`,
> `ralph.sh`, Rollen-Skripte, `team-lib.sh`, `team-status.sh`) gehören sichtbar
> ins **Wurzelverzeichnis** — der {{Strippenzieher}} tippt sie direkt als
> `./vollautomatik.sh`. Das **aufgerufene Produkt-/Betriebswerkzeug**
> (Smoke-Test, Deploy, Beutebuch-Zustandsmaschine, `kosten.py`) gehört in
> [`scripts/`]. Dieselbe Logik wie `Makefile`/`.github/`: Einstiegspunkte oben,
> Werkzeug im Unterordner. Die Top-Level-Skripte sind über relative
> Geschwister-Pfade (`source ./team-lib.sh`, `./ralph.sh`) eng verzahnt und
> erwarten die Repo-Root als Standort — nicht ohne Not verschieben.

## A.3 Auth-Fallback  ✅ erprobt für alle automatisierten Rollen (website-maxron-de, 2026-07-10 bis 2026-08-01)

Zentral in `team-lib.sh` (Feldprojekt: Helfer `team_claude`): Rollen starten im **Abomodus**, fallen bei einem gescheiterten Aufruf **aufruf-lokal** auf `api` zurück, danach zurück zu Abo. **Axel** ist bei der **Auth** in die Abo-first-Regel aufgenommen (Feldprojekt website-maxron-de, Strippenzieher-Entscheid 2026-07-10: starkes Modell im Abo ist günstiger, das Budget-Cap pro Fall bleibt als Airbag) — sein **Modell** bleibt davon unberührt **immer stark** (`{{starkes-modell}}`, siehe Axel-Sektion: Modell und Auth sind zwei getrennte Achsen). **Seit dem Folge-Entscheid 2026-07-13 läuft auch Der Architekt Abo-first** — damit ist **keine** Rolle mehr fest API, und die Kosten der interaktiven Rollen sind **Abo-Gegenwert** statt Konsolenwert (Folgewirkung auf A1, siehe A.9). Das erprobte Rezept:

- **`team_resolve_auth_mode [rollen-default]`**: löst Env `AUTH_MODE` → `~/.config/claude-team/auth-mode` → Rollen-Default auf. `abo` **entfernt** `ANTHROPIC_API_KEY` aus der Prozess-Umgebung (Verdrängungsfalle, s. o.); `api` lädt den Key notfalls aus `~/.config/claude-team/api-key` (`chmod 600`) — erst diese Key-Datei macht den Fallback möglich, wenn der Loop ohne Key in der Env gestartet wurde.
- **Stufen-lokal durch frische Auflösung**: Der Loop merkt sich die etwaige Nutzer-Übersteuerung beim Start (`AUTH_MODE_START="${AUTH_MODE:-}"`) und löst **pro Stufe neu** auf — damit endet jeder Fallback automatisch mit der Stufe.
- **Fehlersignal** (✅ verifiziert, siehe A.5): Aufruf gilt als gescheitert bei Exit-Code ≠ 0 **oder** `is_error: true` in der `--output-format json`-Antwort (Helfer `team_result_is_error`; unlesbares JSON zählt als Fehler).
- **Genau ein Retry**: Scheitert der Abo-Aufruf, folgt ein einziger API-Versuch mit eigener Log-Datei (z. B. `stufe-N-api-fallback-….json`); scheitert auch der → harter Abbruch, Mensch schaut in die Logs.
- **Maschinen-Einrichtung**: `~/.claude/scripts/team-auth-setup.sh` (idempotent; Config anlegen, Key-Migration aus Shell-Profilen mit Backup und Ersatz der Export-Zeile, optionaler headless Abo-Test inkl. Erkennung der „takes precedence"-Warnung).

## A.4 Read-Only-Guard (3 Linien, Defense-in-Depth)  ✅ erprobt (website-maxron-de, 2026-07-10)

1. **Prompt** — „Du bist Harry/Marv, schreibe ausschließlich `{{Test-Ordner}}` und `{{Plan-Ordner}}`." (notwendig, nicht hinreichend)
2. **Tool-Permissions** — headless `--permission-mode default` + enge `--allowedTools`-Liste: `Read`/`Grep`/`Glob` überall, `Write`/`Edit` nur auf `{{Test-Ordner}}**` + `{{Plan-Ordner}}**`, **kein** `git commit` in der Allowlist (das Skript committet die Whitelist-Änderungen deterministisch — der Angreifer selbst nicht).
3. **Post-Hook** (deterministische Garantie) — nach der Iteration `git diff --name-only <START_HASH> HEAD` + `git status --porcelain` gegen die Whitelist.

> ⚠️ **Guard-Härtungs-Lektion (Feldtest 2026-07-10, teuer gelernt):** Der Rollback in Linie 3 muss **chirurgisch** sein — **nur die konkret gelisteten Verletzer-Pfade** zurücksetzen (getrackt → `git checkout <START_HASH> -- <pfad>`; neu → gezielt `rm`/`git rm`). Ein **blindes `git reset --hard` + `git clean -fd`** ist ein Footgun: Im Feldtest löschte es die **gesamte noch uncommittete Team-Infrastruktur**, weil im Testmoment alle neuen Skripte als „Nicht-Whitelist" galten. Zwei Betriebsregeln dazu: (a) **Infrastruktur committen, bevor** je ein Guard läuft — im Normalbetrieb ist der Baum zwischen den Phasen ohnehin sauber (jede Rolle committet); (b) **Guard-Tests nur in einem Wegwerf-Repo**, nie im echten. Ein rollenspezifischer `pre-commit`-Hook bleibt optionaler Zusatz (Gürtel + Hosenträger).

> ⚠️ **Staging-Lektion (Feldlauf website-maxron-de, 2026-07-11):** Beim Commit der erlaubten Whitelist-Änderungen **datei-genau stagen**, nicht ordner-weit. Der gemeinsame Red-Team-Sweep-Commit staged zunächst das **ganze Plan-Verzeichnis** (`git add {{Plan-Ordner}}`), obwohl Harry/Marv laut Prompt nur ins Beutebuch (+ `{{Test-Ordner}}`) schreiben. Da **Der Architekt interaktiv außerhalb des `flock`** arbeitet (kein Loop, nicht vom Lock erfasst), kann er gleichzeitig **uncommittete** Plan-Dateien unter derselben Whitelist liegen haben — ein parallel laufender Sweep zog so fremde Architekten-Arbeit in seinen `docs(beute)`-Commit. Eine Ordner-Whitelist (`^({{Test-Ordner}}|{{Plan-Ordner}})`) ist **nicht** dasselbe wie datei-genaues Staging: gezielt nur die eigenen Ausgabepfade stagen (`git add {{Beutebuch-Pfad}} {{Test-Ordner}}`); die Whitelist bleibt als zusätzliche Absicherung. Optional: Vorab-Check auf fremde uncommittete Änderungen außerhalb der eigenen Ausgabepfade.

> ⚠️ **Zuschreibungs-Lektion (Feld K2, 2026-08-01 — `BL-16`):** Linie 3 hatte **keinen Ausgangszustand**. Sie las nur „welche Pfade sind **jetzt** schmutzig" und schrieb jeden davon der **laufenden Rolle** zu — jeder fremde Schreiber (parallele Sitzung, Handänderung, abgebrochenes Werkzeug) wurde angelastet **und** hart zurückgesetzt. Der eigene Kommentar „schützt parallele/legitime uncommittete Arbeit" galt nur gegenüber dem blanko `reset --hard` aus der Lektion oben; das chirurgische `git checkout -- <pfad>` zerstört fremde Arbeit **genauso**, nur gezielter. Real eingetreten: Axels korrekte Ermittlung (Akte fertig geschrieben) zählte als „Aufruf fehlgeschlagen" → Stagnationszähler → **Lauf gestoppt**, und die zurückgerollten Pfade waren die unbeteiligte Arbeit einer parallelen Sitzung. **Zwei Ebenen, getrennt zu bauen:** (1) **Zuschreibung** — `team_guard_begin` hält einen Schnappschuss mit **Blob-Hashes** (nicht nur Pfaden, sonst kommt eine Rolle frei, die eine ohnehin schmutzige Datei anfasst); was vorher schmutzig war und es unverändert blieb, gehört nicht der Rolle. Dazu eine laute Warnung schon beim Start, wenn der Baum nicht sauber ist. (2) **Urteil** — liegt das **Ergebnis** der Rolle vor (Akte + Statuswechsel bzw. Sweep-Quittung), kassiert der Guard den **Übergriff**, nicht die Arbeit. **Diagnose-Lehre:** Der Übergriff wurde zunächst der falschen Rolle zugeschrieben, weil die Pfadliste im Log neben ihrem Namen stand — belegt war das nirgends. Die Meldung muss die beiden Fälle **sprachlich trennen**: „diese Pfade waren beim Rollenstart bereits geändert" vs. „**diese Rolle** hat sie geändert".

Ausführlich: [read-only-guard](../konzepte/read-only-guard.md)

> **Frank-Variante:** Frank *darf* Produktivcode ändern → statt Guard eine **Dreisatz-Verifikation** (ein `{{fix-präfix}}`-Commit im Bereich `START_HASH..HEAD`, CHANGELOG ergänzt, Beutebuch-Status auf `erledigt`).
>
> ⚠️ **Verifikations-Lektion (Feldlauf website-maxron-de, 2026-07-10):** **Nicht** verlangen, dass **HEAD selbst** der `{{fix-präfix}}`-Commit ist — der Fixer darf den CHANGELOG-/Status-Edit legitim in einen `docs:`-**Folgecommit** legen (der Prompt erlaubt das sogar ausdrücklich). Prüfe stattdessen `git log START_HASH..HEAD --pretty=%s | grep {{fix-präfix}}`. Der ursprüngliche „letzter Commit"-Check rollte korrekt gefixte Arbeit fälschlich zurück.

## A.5 Faktencheck-Pflicht (Spec vor Annahme)

An der **real installierten** CLI verifizieren — **nicht raten**:

- **Tool-Permission-Format** (Settings-Datei vs. Flags; ob `permissions.deny` unterstützt wird). Falls `deny` fehlt: **Post-Hook (Linie 3) ist die Haupt-Garantie** — der Guard ist gegen beide Fälle robust. ✅ **verifiziert an der Claude-CLI (2026-07-10):** headless `--permission-mode default` + `--allowedTools`-Allowlist greift; ein Red-Team-Sweep mit auf `{{Test-Ordner}}`/`{{Plan-Ordner}}` beschränkter Allowlist ließ Produktivcode unangetastet.
- **Provider-Timeout-Signal** für den Auth-Fallback — ✅ verifiziert an der Claude-CLI (2026-07-10): Exit-Code ≠ 0 **oder** Feld `is_error` in der `--output-format json`-Ausgabe; die „takes precedence"-Warnung im Text signalisiert zusätzlich, dass eine andere Auth-Quelle das Abo verdrängt.

## A.6 Parallelität & Reproducer

- **Empfehlung:** sequenziell (Rollen hängen inhaltlich voneinander ab: Ralph → Red Team → Frank) + **`flock`-Airbag** in **alle** Loops, gegen `index.lock`-/`status`-Races. Echte Parallelität (Git-Worktrees) bleibt späterer Ausbau.
- **Guard-Reproducer:** ein Loop, der absichtlich `{{Produktivcode-Globs}}` anfasst, **muss** vom Post-Hook hart zurückgerollt werden (grüner Regressions-Schutz).

## A.7 Budget-Governance & Feld-Betriebslehren  ✅ erprobt (website-maxron-de, Kaskaden 6–22, 2026-07-11 bis 2026-08-01)

**Budget-Governance (optionaler, aber empfohlener Ausbau).** Statt eines starren, wandernden Projekt-Gesamtdeckels bewährt sich das Modell **„Pro-Lauf-Deckel = operative Grenze, Gesamtstand nur dokumentiert"**:

- **Committete `{{ledger-datei}}` (z. B. `.budget-ledger`)** — append-only, tab-/pipe-getrennt (`datum | kaskade | usd | auth | notiz`), **nicht** `.gitignore`-t. Sie ist die maschinenlesbare historische Basis, weil die Log-Ordner (`.{{rolle}}-logs/`) rotiert/`.gitignore`-t sind und den Stand sonst „vergessen".
- **Log-Rotation/Archivierung (Pflicht, sonst Doppelzählung) — aber im Closeout, nicht im Lauf.** Wer eine committete Ledger-Datei einführt, **muss** die zugrundeliegenden Rohlogs **nach** dem Anhängen der Ledger-Zeile aus dem gezählten Pfad entfernen — **archivieren, nicht löschen** (z. B. Helfer `team_logs_archivieren <dir>`, verschiebt `*.json` nach `<dir>/archiv/`, das vom Kosten-Tool nicht-rekursiv **nicht** mitgezählt wird). Fehlt dieser Schritt, zählt **jede** abgeschlossene Kaskade **doppelt** (Ledger-Zeile **und** die nie gelöschte Rohlog-Datei). **Reihenfolge: Ledger-Zeile anhängen → direkt danach archivieren — beides aber im Architekten-Closeout NACH dem Lauf, niemals in einer Loop-Stufe.** Eine Abschluss-**Stufe** würde mitten im Lauf genau das Geld wegräumen, das die Pro-Lauf-Durchsetzung noch messen muss (Lehre 8 — im Feld teuer gelernt). Ein Kaskaden-Plan endet in seiner letzten Stufe mit Doku/CHANGELOG.
- **Kontostand-Tool** (z. B. `./team-status.sh --budget`, Kern in einem kleinen `scripts/kosten.py`): summiert Ledger-Basis **plus** laufende Logs und weist **real via API abgerechnet** und **Abo-Gegenwert (nicht abgerechnet)** getrennt aus — sonst wird der Abo-Gegenwert als reale Ausgabe fehlinterpretiert.
- **Zwei Kennzahlen sauber trennen — nie vermischen.** **A) Kosten dieses Laufs** (nur Logs seit Lauf-Start, z. B. `kosten.py summe --since EPOCH` + Helfer `team_kosten_seit "$LAUF_START"`) ist die **operative Grenze**, gegen die die Durchsetzung den Pro-Lauf-Deckel prüft. **B) Gesamt-Kontostand** (lebenslang: Ledger-Basis + alle Logs) ist **reine Anzeige** (`--budget`, Abschlussbericht, Notify, Deckel-Anhebungs-Meldung). Wird die Durchsetzung versehentlich auf B umgestellt, stoppt der Lauf **sofort**, sobald die Lebenssumme die Plan-Empfehlung übersteigt — noch bevor der aktuelle Lauf etwas kostet.
- **`BUDGET_EMPFEHLUNG_USD=…`-Zeile je Kaskaden-Plan** — der Architekt setzt sie analog zu `RALPH_CAP=…`. Die Vollautomatik liest sie und **hebt den Lauf-Deckel automatisch nur an, senkt nie**; eine explizite User-Übersteuerung (`TEAM_BUDGET_USD=…`) hat Vorrang; fehlt die Zeile, gilt der bisherige Default. Die Halbautomatik zeigt Stand + Empfehlung und fragt den User.
- **CAP/PLAN aus dem aktiven Plan statt Skript-Edit** — der Loop liest `RALPH_CAP` per `grep` aus dem aktiven Plan und den Plan-Pfad aus einer Zeiger-Datei (z. B. `.ralph-plan`). Kaskadenwechsel wird `echo {{Plan-Präfix}}-N-….md > .ralph-plan` statt eines Skript-Edits; nur das *Auslesen* ist automatisiert, das *Weiterschalten* bleibt bewusste Strippenzieher-Aktion. Verhindert den stillen Fehlstart „`RALPH_CAP` vergessen".

**Feld-Betriebslehren (in scharfen Läufen real erlebt — für jedes Team wertvoll):**

1. **Budget-Cap-Timing.** Der Pro-Stufe-Budget-Check greift typischerweise **nach** dem LLM-Aufruf, aber **vor** dem State-Weiterschalten. Sprengt eine Stufe den Cap, ist ihre Arbeit bereits **committet**, aber die State-Datei bleibt stehen und die Vollautomatik stoppt — **kein Datenverlust**. Der Mensch prüft den Commit, schaltet manuell weiter (`echo N+1 > {{state-Datei}}`) und setzt fort. **Konsequenz:** den Pro-Stufe-Default großzügig genug wählen (Infrastruktur-/Skript-Stufen kosten mehr als reine Content-Stufen — im Feld 1 → 3 USD angehoben).
2. **Red-Team-Fokus ist kaskaden-abhängig  ✅ gebaut (Kaskade 7).** Ein fest auf den Produktivcode (`{{Produktivcode-Globs}}`) verdrahteter Red-Team-Auftrag zielt bei einer **Infrastruktur-Kaskade** (die nur `*.sh`/Skripte/Doku anfasst) am Bau vorbei. Lösung im Feld: eine Env `TEAM_REDTEAM_FOCUS`, die **beide** festen Verdrahtungen übersteuert — den `AUFTRAG` der Red-Team-Rollen **und** den „Prüfe … unter {{Produktivcode-Globs}}"-Prompt-Scope; ohne Env bleibt alles wortgleich beim Produktivcode-Default (rückwärtskompatibel). Dogfooding: der Red-Team-Schritt der Kaskade, die diese Env baute, war selbst ihr erster Anwendungsfall (Harry/Marv auf die geänderten Skripte statt auf den Produktivcode gelenkt).
3. **„success ohne Promise" ≠ harter Fehler  ✅ gebaut (Kaskade 7).** Verweigert der Read-Only-Guard einer Red-Team-Rolle korrekt das Ausführen (`permission_denials`), kann sie in eine Rückfrage laufen und **kein Sweep-Promise** ausgeben — obwohl sie einen Fund sauber ins Beutebuch übergeben hat. Wertet die Vollautomatik jedes Nicht-Promise als harten Stopp, hängt ein Neustart an derselben Stelle. Im Feld **beide Hebel gebaut** (Gürtel + Hosenträger): (1) **Prompt-Härtung** — die Red-Team-Rollen stellen **nie** Ausführ-Rückfragen (der Guard erzwingt Read-Only ohnehin) und geben bei sauber übergebenem Fund **immer** das Promise aus; (2) **Logik-Härtung** — ein `success`-Log (kein `is_error`) mit **neuem, sauber übergebenem** Beutebuch-Eintrag zählt **nicht** als harter Fehler. Echte Fehler (`is_error`, Guard-Bruch, Aufruf-Fehlschlag) bleiben harter Stopp. Übergangsweise ließ sich ein solcher Fund gezielt über die Halbautomatik (`halbautomatik.sh frank`) weiterverarbeiten.
4. **Log-Rotation nicht vergessen (Doppelzählung).** Die committete Ledger-Datei sichert Kosten gegen das Rotieren/Löschen der `.gitignore`-ten Log-Ordner — **aber nur, wenn der Rotationsschritt auch gebaut wird**. Wird er vergessen, zählt jede abgeschlossene Kaskade doppelt (Ledger-Zeile **und** nie gelöschte Rohlog-Datei); im Feld summierte sich das über sieben Kaskaden auf real ~13,7 USD Phantom-Kosten. Gegenmittel: der Pflicht-Archivierungsschritt oben (Ledger-Zeile → **direkt danach** `team_logs_archivieren`) — **im Closeout nach dem Lauf**, siehe Lehre 8.
5. **Durchsetzung misst Pro-Lauf-Kosten (A), nicht die Lebenssumme (B).** Wird die harte Budget-Durchsetzung versehentlich auf den lebenslangen Gesamtstand (B) statt auf die Kosten des aktuellen Laufs (A) verdrahtet, stoppt die Vollautomatik **sofort**, sobald die kumulierte Lebenssumme die Plan-Empfehlung übersteigt — man müsste bei jeder Kaskade den Pro-Lauf-Deckel hochdrehen, nur um eine Lebenszeit-Summe zu überbieten. Durchsetzung immer gegen A (Logs seit Lauf-Start); B bleibt reine Anzeige (siehe Governance-Punkte oben).

6. **Zwei-Schwellen-Budget statt divergierender Defaults  ✅ gebaut (`BL-30`).** Ein zentraler **Soft-Cap** (`{{TEAM_ROLE_BUDGET_USD}}`, Default 5 USD) für alle Rollen plus ein **Hard-Cap** (`{{TEAM_ROLE_HARDCAP_USD}}`, Default 10 USD) für Frank & Axel ersetzen mehrere auseinanderlaufende Pro-Rolle-Defaults. **Kernlehre (realer Auslöser HM-32):** Ein Pro-Fall-Cap greift **nach** dem bereits bezahlten Aufruf — ist er zu tief, wird ein teurer, aber plausibler Fix als „Fehlversuch" per Rollback weggeworfen und **vervielfacht** die Kosten, statt zu sparen. Für die iterierenden Rollen (Frank/Axel) daher: Soft-Cap = **nur Hinweis** (kein Rollback), erst der Hard-Cap bricht ab. Details siehe `## Kostenkontrolle`.

7. **Prosa-Arbeit gehört nicht in den Bau-Loop  ✅ erprobt (Kaskade 22).** Eine Kaskade, die überwiegend **Text** umbaut (Doku verdichten, verschieben, inventarisieren), ist im Loop **rund doppelt so teuer** wie eine Code-Kaskade: im Feld **3,23 / 3,97 / 4,68 USD** je Prosa-Stufe gegen **2,16 / 2,35 USD** je Code-Stufe derselben Kaskade (Vergleichs-Kaskade: 1,85 USD/Stufe). **Ursache:** Der Loop zahlt pro Stufe einen **Kaltstart** und liest die inzwischen gewachsene Datei erneut vollständig; der interaktive Architekt hält denselben Kontext über alle Schritte. **Zweite, unangenehmere Wirkung:** Die teuerste Stufe lag mit 4,68 USD **über der 80-%-Warnschwelle** des 5-USD-Pro-Stufe-Caps — die Kaskade stand näher am harten Stopp, als die Gesamtsumme vermuten ließ. **Konsequenz:** Textvolumen-gebundene Arbeit beim Aushärten als **Architekt-Handarbeit** einplanen (Planungsregel 2), auch wenn der Rest der Kaskade in den Loop gehört.

8. **Die Kostenmessung darf weder blind werden noch Fehlversuche verschenken  ✅ gefixt (`BL-55`, 2026-08-01).** Im Feld druckte ein Abschlussbericht **6,1644 USD**, ausgegeben waren **26,4183 USD** — eine Untertreibung um **77 %**, entdeckt nur, weil ein Mensch die Zahl unplausibel fand. Drei Ursachen, jede für sich übertragbar:
   - **(a) Die Pflicht-Reihenfolge war selbst der Bug.** Eine Kaskaden-Abschluss-**Stufe** *innerhalb* des Laufs ledgerte und **archivierte** die Rohlogs — dadurch fielen 20,25 USD aus der Pro-Lauf-Durchsetzung (Kennzahl A), und zwar **unmittelbar bevor** die offene Fixphase startete: der Deckel war ab da faktisch **zurückgesetzt**, dieselbe Leerlauf-Klasse wie die Stagnations-Bremse sie verhindern soll. **Regel:** Kostenabschluss nur im **Closeout nach dem Lauf**.
   - **(b) Die Durchsetzung muss die Archivpfade mitzählen.** Sonst wird sie blind, sobald überhaupt jemand mitten im Lauf archiviert. Im Feld über einen **mtime-Filter** gelöst (`mv` erhält die mtime, ältere Kaskaden fallen sauber heraus). Kennzahl **B** bleibt bewusst **ohne** Archiv — sonst zählt die Ledger-Basis doppelt.
   - **(c) Ein gescheiterter Aufrufversuch war gratis.** Die Kosten eines Aufrufs wurden aus dem **finalen** Log gelesen. Scheitert der Abo-Aufruf nach 1,68 USD und kostet der API-Fallback 0,40 USD, meldet die Stufe **0,40**. Damit ist der Pro-Stufe-Cap **umgehbar**: 4,9 (Abo-Fehlversuch) + 4,9 (API) melden 4,9 gegen einen 5-USD-Cap. **Regel:** Kosten eines Aufrufs = **Summe aller Versuchs-Logs** (Abo-Fehlversuch + API-Fallback + 429-Retries); das finale Log bleibt separat für Promise-/Erfolgsauswertung.

## A.8 Session-Limit-Robustheit (429) generieren  ✅ erprobt (`BL-20`/`BL-25`, website-maxron-de 2026-07-11)

Ein Claude-Session-Limit ist eine **dritte Fehlerklasse** neben „sauberer Erfolg" und „echter Fehler" — der **Verhaltens-Vertrag** steht im Vorlagenblock („Loop-Mechanik & Auth"); **hier** liegen die **numerischen Default-Deckel** (die Feinabstimmung), auf die der Block verweist:

- **Zentral in `team_claude()`:** 429-Erkennung (`api_error_status == 429` **oder** Text „session limit"/„resets"), **API-Fallback zuerst** (separates Kontingent), dann Auto-Retry mit Deckel, sonst **Exit 42** + `TEAM_LAST_PAUSE`/`TEAM_LAST_RESET`.
- **Kosten über alle Versuche summieren (`BL-55`, A.7/Lehre 8c).** Weil ein Aufruf hier **mehrfach** stattfinden kann (Abo-Fehlversuch → API-Fallback → 429-Retries) und **jeder Versuch bezahlt** ist, muss `team_claude()` **alle** Versuchs-Logs sammeln und ihre Kosten **summieren** — nicht nur das letzte Log lesen. Sonst ist der Pro-Stufe-Cap umgehbar. Die Variable mit dem **finalen** Log bleibt davon getrennt bestehen: sie ist die richtige Quelle für die Promise-/Erfolgsauswertung (die Rollen-Skripte müssen sie lesen, nicht ihre eigene unveränderte Ausgangsvariable).
- **Env-Deckel (Defaults):** `TEAM_429_MAX_RETRIES` = **2**, `TEAM_429_MAX_WARTEN` = **1800 s** (`0` schaltet den Auto-Retry A komplett ab), `TEAM_429_PUFFER` = **30 s** (Aufschlag auf die geparste Reset-Zeit). Ist der Reset unbekannt oder liegt er jenseits von `TEAM_429_MAX_WARTEN`, entfällt das Warten sofort zugunsten des Pausen-Exits.
- **Alle Rollen-Skripte** reichen Exit 42 **unverändert** durch (kein State-Fortschritt, kein Fehlversuchs-Zähler); der Read-Only-Guard läuft auf **jedem** Pfad (auch Pause) **vor** der RC-Auswertung.
- **`vollautomatik.sh`** erkennt Exit 42 in **allen** Phasen (Ralph, Red-Team-Sweeps, Frank↔Axel-Fixphase) und beendet mit einer eigenen Pausen-Meldung statt „ECHTER Fehler".
- **Auslauf-Bremse** `TEAM_FIX_MAX_STAGNATION` = **2** (grobe zweite Obergrenze `TEAM_MAX_RUNDEN` = **12**): Fixphase bricht ab, wenn N Runden **keinen** Fortschritt zeigen (kein Frank-Fix, keine neue Axel-Akte, kein Beutebuch-Statuswechsel per Snapshot-Vergleich).
- **Testbarkeit:** Fixture-Tests netz-/CLI-frei halten (`subprocess`+`bash -c`), Warten über `TEAM_DRY_RUN=1`/`TEAM_429_SKIP_SLEEP=1` überspringbar machen.
- **Es gibt eine VIERTE Fehlerklasse: Sitzung beendet, Auftrag unquittiert (`BL-41`).** Eine bauende Rolle startet einen Hintergrund-Task/Monitor/Wakeup und „wartet" darauf — headless kommt diese Benachrichtigung nie. Die CLI beendet die Sitzung, und das Ergebnis-JSON trägt `subtype: "success"`, `is_error: false`, `stop_reason: end_turn`: **für jede is_error-Prüfung ein sauberer Erfolg.** Nur das fehlende Promise verrät den Fall. Vier Vorfälle im Feld, **19,47 USD**, jedes Mal für Arbeit, die fertig und grün war — der Neustart wirft sie weg, von Hand quittieren rettet sie. Zwei Bauteile, und **beide** werden gebraucht: (1) **Prävention** — die Smoke-Zeile verbietet Hintergrund-Betrieb und Wakeup **mit Begründung**; sie wirkt, aber sie steht am Prompt-Anfang, während der Vorfall nach 65 Turns passiert: Prompt-Prävention skaliert **gegenläufig zur Stufenlänge**, und der Anreiz wächst mit der Laufzeit der Suite. (2) **Erkennung** — fehlt das Promise, während das Log sich selbst für erfolgreich erklärt, gibt der Loop eine **benannte** Meldung samt Prüfweg aus (hier: eigener Exit **43**, wie der Pausen-Exit 42 durchgereicht) statt „ECHTER Fehler". **Nicht auf Vokabeln prüfen:** Drei Vorfälle, drei Formulierungen („background pytest run and monitor", „fallback check / wakeup", „set up a monitor to catch its completion") — geprüft wird die Struktur, nicht der Wortlaut.

## A.9 Interaktive Akteur-Kosten erfassen  ✅ erprobt (`BL-28`/`BL-29`/`BL-33`/`HM-36`/`BL-55`, website-maxron-de 2026-07-12 bis 2026-08-01)

Interaktiv arbeitende Rollen (Architekt, Frank-im-Abo) laufen **außerhalb** `team_claude` und schreiben keine `total_cost_usd`-JSONs — sonst strukturell unerfasst. Der operative Vertrag liegt seit `BL-56` **zweigeteilt** (Dreischnitt, „das WANN gilt für alle, das WIE nur für einen"): Das **WANN** — Kostenabschluss nach dem Lauf im Architekten-Closeout, **nie** in einer Loop-Stufe — steht im Vorlagenblock („Kostenkontrolle"), weil es auch Ralph begrenzt. Das **WIE** — Verben, Ledger-Zeilen, Domänen, Abo-Messung — steht im Briefing `prompts/rolle-architekt.md`, weil keine andere Rolle diese Befehle je aufruft. **Hier** liegen die **Bau-Details** des Kosten-Werkzeugs (`kosten.py`):

- **A2 (nur Architekt):** Unterkommando `kosten.py architekt-schaetzung --since REF` (Wrapper `team_architekt_schaetzung`) schätzt aus dem Zeilen-Churn (`git diff --numstat` in `{{Plan-Ordner}}/**` + `CLAUDE.md` seit dem letzten Ledger-Commit) × Eichfaktor `{{ARCHITEKT_USD_PRO_CHURN_ZEILE}}` (an einer realen Session eichen, Rechenweg im Code kommentieren) — bewusst grob, **nie** persistiert; für `{{Produktivcode-Globs}}`-Fixes (Frank) nicht aussagekräftig, daher architekt-spezifisch.
- **A1 (rollen-agnostisch):** Kern `kosten.py akteur-abschluss` mit `akteur_abschluss(usd, domaene, kaskade, rolle, auth, notiz)` hängt den Wert an und **ersetzt** (statt verdoppelt) die Zeile derselben **Rolle + Kaskade** (Idempotenz; Architekt- und Frank-Zeile überschreiben sich nicht). Der Wert ist im API-Betrieb der abgelesene Konsolenwert, im **Abo-Betrieb** die A2-Schätzung als **Abo-Gegenwert** (siehe Vorlagenblock). Defensiv validieren (endliche, nicht-negative Zahl, **keine** rohe `python3 -c`-Interpolation — Lehre aus `BL-23`/`HM-17`). `architekt-abschluss` bleibt als dünner Alias (`--rolle architekt --auth api`).
- **Sanitisierung gilt für *jedes* interpolierte Feld (Fund `HM-36`).** Nicht nur die Notiz, sondern **auch** `rolle` und `kaskade` müssen **vor** Idempotenz-Match und Zeilen-Template gegen das Trennzeichen und Zeilenumbrüche gesäubert werden — sonst zerschießt ein einzelnes `|` im Rollennamen das Ledger-Schema. Die atomare Schreib-/Ersetzungslogik in **einen** gemeinsamen Helfer auslagern, den alle Abschluss-Funktionen nutzen (sonst divergieren zwei Atomizitäts-Implementierungen, und der Schutz gilt nur für eine davon).
- **Rollenkosten kaskadenscharf ledgern (`rollen-abschluss`).** Die automatisch geloggten Rollenkosten (Red Team, Fixer, Forensiker) wandern nicht in eine kaskadenübergreifende Sammelzeile, sondern in **eine `rolle=roles`-Zeile je Kaskade**: `kosten.py rollen-abschluss --kaskade N --domaene …`, Oberfläche `./team-status.sh --rollen-abschluss <kaskade> <domaene>` — **ledgert und archiviert in einem Schritt**. `auth` ergibt sich aus dem tatsächlichen Abo/API-Split, der exakte Split gehört in die Notiz. Ein zweiter Aufruf für dieselbe Kaskade **bricht ab** und nennt Alt-, Neu- und Summenwert (`--addieren` für den Nachlauf, `--ersetzen` für die Korrektur — `BL-5`). Läuft **nie** in der Vollautomatik — reines Closeout-Werkzeug (A.7, Lehre 8a). **Die Notiz trägt den Rollenbezug voran** (`"Rollen: …"` / `"Bau: …"`, `BL-19`): Eine Bedienhandlung schreibt **zwei** Zeilen, aber es gibt nur **einen** Notiztext — ohne Vorspann beschreibt er zwangsläufig höchstens eine von beiden, und im Feld trug Ralphs Zeile über vier Baustufen die Notiz „Harry/Marv-Sweeps". Die Notiz ist die **einzige** Prosa-Spur je Ledger-Zeile; sie muss aus sich heraus sagen, welche Kosten die Zeile trägt.
- **Auth-Split ehrlich halten (`ledger --split`).** Die Aufschlüsselung „real abgerechnet vs. Abo-Gegenwert" muss auch die `auth`-Spalte **archivierter** Ledger-Zeilen berücksichtigen, sonst fehlt die historische Zuordnung nach jeder Archivierung. Bucket-Regel mit **drittem Bucket**: `abo` → abo, `api` → api, **jeder** andere Wert (`"abo/api"`, leer, unbekannt, Altzeilen) → **`gemischt`**, so dass immer `abo + api + gemischt == Summe` gilt. **Nie** einen Split raten.
- **Ledger-Schema rückwärtskompatibel erweitern:** `datum | kaskade | usd | auth | domaene | rolle | notiz` (bestehende 5-Feld-Zeilen bleiben gültig). `domaene` aus dem Kaskaden-**Bezug** ableiten, **nicht** aus dem rohen `{{Plan-Ordner}}/`-Pfad (Planungs-Commits liegen immer dort). `kosten.py ledger --domaene … [--rolle …] [--kaskade N]` filtert; Altzeilen ohne die Felder zählen bei gesetztem Filter **nie** mit („unzugeordnet", nie stillschweigend zugeschlagen). `--budget` markiert die Architekt-Zeile als „geschätzt" oder „echt".
- **Ein Aufruf ohne Beleg ist keine Null (`BL-46`).** Ein gescheiterter Anlauf kann ein **0-Byte-Log** hinterlassen — im Feld nach **47 Minuten** Laufzeit. Eine Summierung, die eine unlesbare Datei stillschweigend mit 0 zählt, macht „Kosten unbekannt" von „hat nichts gekostet" ununterscheidbar: Der Abo-Gegenwert fällt aus **jedem** Kostenabschluss, der Pro-Stufe-Deckel bekommt auf diese Hälfte keinen Griff, und die Stufe erscheint in der Kostentabelle als die **billigste**, obwohl sie als teuerste angesetzt war — wer die Tabelle später als Vergleichsband liest, schreibt eine Zahl fort, die eine halbe Stufe beschreibt. **Bauregel:** Der Aufrufer ersetzt ein unbrauchbares Versuchslog durch einen **Ersatzzettel** mit dem, was belegbar ist (Dauer, `total_cost_usd: null`, Marke „verworfen"), die Summierung zählt ihn **nicht** als 0, sondern meldet ihn getrennt — **nicht schätzen, nur sichtbar machen**. Und: Der Zettel ist gerade **kein** Kostenbeleg, also wird er beim Abschluss **mitarchiviert**; sonst hält ihn der Ledger-Wächter dauerhaft für einen Verdachtsfall und empfiehlt eine Abhilfe (`--ersetzen`), die nach `BL-5` echtes Geld vernichtet. Ein Wächter, dessen Warnung sich nicht abstellen lässt, erzieht zum Wegsehen (`BL-14`).
- **Jede Kennzahl sagt, ob sie in der Summe daneben schon drinsteckt (`BL-18`).** Die Architekt-Zeile in `--budget` hat zwei Modi, und der Modus schaltet ausgerechnet **beim Kaskaden-Abschluss** um — in dem Moment, in dem die Zahl abgelesen und weitergegeben wird: „geschätzt" (A2-Churn, in **keiner** Ledger-Zeile ⇒ **nicht** im Gesamt) wird zu „echt" (Ledger-Zeile dieser Kaskade ⇒ **sehr wohl** im Gesamt, `team_kontostand_gesamt` summiert sie mit). Ein fest verdrahteter Zusatz „nicht im Gesamt enthalten" ist damit die Hälfte der Zeit falsch und lädt zum Doppeladdieren ein (im Feld 81,27 statt 71,57 USD, 13 % zu viel). **Der Zusatz gehört an den Modus, nicht an die Zeile.** Zweite Hälfte derselben Regel: Steht in einem Block, der **lebenslang** kumuliert, eine **kaskadenscharfe** Zahl, muss die Beschriftung den Bezugsrahmen nennen (`Architekt K3 (…)`) — sonst liest man den Kaskadenwert als Lebenssumme.

- **Drei Herleitungen, die den Vertrag tragen** *(2026-08-12 aus dem Vorlagenblock hierher verschoben, `BL-56` — geltende Regel blieb dort, das Warum liegt jetzt hier)*:
  - **Der reale Auslöser:** Eine **einzelne** Architekten-Session kostete laut Konsole **~16 USD** — und war strukturell unerfasst, weil sie außerhalb `team_claude` lief. Ohne A1/A2 fällt nicht ein Rundungsfehler aus dem Ledger, sondern der Löwenanteil einer Kaskade.
  - **Warum die Prüfung kein hartes Gate ist (Skizze D, `--ledger-pruefen`):** Exit `4` bei Warnbefunden, aber **kein** Abbruch im Closeout — eine Kaskade mit legitim fehlender Zeile könnte sonst nicht abschließen, und **ein Gate, das man regelmäßig umgeht, ist wirkungslos** (dieselbe Lehre wie `BL-14`). Stattdessen läuft die Prüfung bei jedem `--budget` ungefragt mit. Ihr Wert liegt darin, dass die dritte Frage („ergeben die archivierten Rohlogs mehr, als das Ledger ausweist?") ihre Kennzahl aus einer **anderen** Quelle zieht als das Geprüfte — genau das fehlte bei `BL-1`, `BL-4` und `BL-5`, die alle drei ein Mensch beim Vergleich zweier Dokumente fand, nicht ein Werkzeug.
  - **Warum eine Domäne der Normalfall ist (`BL-9`):** Die frühere feste Trennung `produkt` ↔ `team` stammt aus dem **Ursprungsprojekt**, in dem die Team-Infrastruktur **im** Projekt gebaut wurde. Seit es das Kit gibt, gilt das nicht mehr — was am Team auffällt, geht als Fund ins Kit-Repo zurück und wird dort verbucht; eine „T.E.A.M."-Zeile im Kontostand eines Feldprojekts wäre strukturell `0.0000`. Eine Kennzahl, die immer null zeigt, erzieht dazu, den ganzen Block zu überlesen.

## A.10 Doku-Konsolidierung — die Regeldatei schlank halten  ✅ erprobt (`BL-54`, website-maxron-de Kaskade 22, 2026-08-01)

Nach ~20 Kaskaden wächst die Wissensbasis zuverlässig zu, ohne sich zu schichten. Im Feld: `CLAUDE.md` **859 Zeilen**, davon ~334 Z reine Baugeschichte („am TT.MM. ergänzt"-Blöcke) und ~200 Z Herleitung — **geltende Kernregeln nur ~160 Z**; die Fundliste **3075 Zeilen** bei ~46 abgeschlossenen von 53 Funden, von vier Rollen bei **jedem** Sweep gelesen. Der **operative Vertrag** steht im Vorlagenblock („Doku-Hygiene"); hier die Bau-Details:

- **Die Doppelbezahlung ist der eigentliche Hebel.** Die Regeldatei liegt ohnehin im Systemprompt jeder Instanz. Fordert der Rollen-Prompt zusätzlich „Rolle siehe CLAUDE.md — lies sie zuerst", zahlt **jeder** Rollenaufruf einen **zweiten Voll-Read** (im Feld ~20–30 Aufrufe je Kaskade). Ersatz: **Rollen-Briefings** `prompts/rolle-*.md` mit **je ~20 Zeilen** (wer ich bin / mein Auftrag / meine eiserne Grenze / mein Dreisatz / mein Promise) und Fallback auf die Regeldatei, falls die Briefing-Datei fehlt. Im Feld: **859 Z → 19–23 Z je Rollenaufruf**.
- **Sicherheitsgurt zuerst bauen, dann umbauen — das ist die eigentliche Lehre.** **Vor** dem ersten Verschieben ein **Regel-Inventar** anlegen: jede Aussage der Regeldatei als **`NORM`** (geltendes Recht), **`HERLEITUNG`** (warum) oder **`HISTORIE`** (wann gebaut) klassifiziert, mit wörtlichem Zitat. Dazu ein **dauerhafter Regressionstest**: jedes `NORM`-Zitat muss wörtlich (whitespace-normalisiert) in der Regeldatei vorkommen, und jeder Abschnitt muss im Inventar vertreten sein. `HERLEITUNG`/`HISTORIE` dürfen ins Wiki wandern, `NORM` nicht. **Leitplanke: kürzt Text, nie Geltung** — Regel streichen, Default ändern, Guard lockern, Rolle umdefinieren sind im Umbau verboten.
- **Der Gurt hat im Feld real gehalten.** Als eine spätere Regeländerung (`BL-55`) eine Regel **bewusst umkehrte**, schlug der Test rot an und zwang dazu, die betroffenen Inventar-Zeilen **benannt** nachzuziehen — statt sie stillschweigend verschwinden zu lassen. Genau dafür ist er da: Er verbietet keine Änderung, er macht sie **sichtbar**.
- **Fundliste rotieren — mit archiv-bewusster Nummernvergabe.** Abgeschlossene Funde in ein Archiv-Doc verschieben (im Feld **3075 Z → 46 Z**). **Fallstrick:** Die `next-id`-Logik der Zustandsmaschine muss **Archiv und aktive Liste zusammen** betrachten, sonst vergibt sie nach der Rotation **doppelte Fund-Nummern** und zwei verschiedene Funde tragen dieselbe ID.
- **Diese Kaskade nicht in den Loop geben** — sie ist der Musterfall für A.7/Lehre 7 (Prosa-Arbeit als Architekt-Handarbeit).
- **Im Kit gebaut, als Vorlage benutzbar (`BL-56`, 2026-08-12):** Das Inventar für die ausgelieferte Regeldatei liegt in [`doku/regel-inventar.md`](regel-inventar.md), der Prüfer in [`kit-regelinventar.py`](../kit-regelinventar.py) (Stufe 7 in `kit-test.sh`). Zwei Bauentscheide, die ein Nachbau übernehmen sollte: **(1) Normalisiert vergleichen** — Blockquote-Marker, Betonungszeichen und Zeilenumbrüche raus, sonst scheitert ein wörtlich richtiges Zitat an einem `**nie**` mitten im Satz (dieselbe Vorsichtsmaßnahme wie in `test_bl55`). **(2) Der Prüfer bewacht die VORLAGE, nicht die Installation** — ein Feldprojekt darf seine `CLAUDE.md` umformulieren, die Vorlage darf es nicht unbemerkt; deshalb liegt er in der Kit-Wurzel, die der Installer nicht kopiert. Beim Aufbau fiel auf: Die Abschnittsliste muss ```-Blöcke überspringen, sonst verlangt sie Inventarzeilen für die Beispiel-Gliederung des Abschluss-Docs.

### A.10.1 Bauformen im Detail

*(Ergänzt 2026-08-01 aus der Feldinspektion. A.10 beschrieb bisher das Prinzip, aber nicht die Form — ein neues Projekt musste sie erraten.)*

**Der Briefing-Helfer** gehört in `team-lib.sh` und hat einen **Pflicht-Fallback**, sonst legt eine fehlende Briefing-Datei den Lauf lahm:

```bash
# team_briefing <rolle>: Inhalt von prompts/rolle-<rolle>.md ausgeben.
# Fallback bei fehlender/leerer Datei: exakt die alte Prompt-Zeile — kein
# Abbruch, keine Fehlermeldung. Ein Fehler hier darf nie einen Lauf stoppen.
team_briefing() {
    local datei="prompts/rolle-$1.md"
    if [ -s "$datei" ]; then cat "$datei"
    else echo "Rolle siehe CLAUDE.md — lies sie zuerst."; fi
}
```

Aufruf in jedem Rollen-Skript als **erste** Prompt-Zeile: `PROMPT="$(team_briefing ralph) …"`.

**Briefing-Aufbau** — fünf feste Überschriften, ~20 Zeilen, hier gekürzt am Beispiel Harry:

```markdown
# Briefing — Harry (Read-Only Red Team, Security)
**Wer ich bin:** …
**Mein Auftrag:** …
**Meine eiserne Grenze:** Ich ändere **niemals** Dateien in `{{Produktivcode-Globs}}` …
**Mein Dreisatz (Beutezug):** 1. Fund ins Beutebuch … 2. Reproducer-Test … 3. Übergabe an Frank …
**Mein Promise:** `<promise>REDTEAM_SWEEP_COMPLETE</promise>` — **immer**, auch nach
einem Fund, ohne Ausführ-Rückfragen zu stellen.
```

Der Nachsatz beim Promise ist die gebaute „success ohne Promise"-Härtung (A.7, Lehre 3) — er gehört **in jedes** Red-Team-Briefing, nicht nur in die Skriptlogik.

**Das Regel-Inventar** ist eine Tabelle mit fortlaufender Nummer, im Feldprojekt 646 Zeilen für eine 859-Zeilen-Regeldatei:

| R-Nr | Klasse | Abschnitt | Zitat |
|---|---|---|---|
| R-1 | NORM | Projekt-Spezifika | statisches HTML/CSS/JS, **ohne Build-Schritt** |
| R-12 | HERLEITUNG | Das Team (Rollen) | Der Mensch delegiert seine Arbeit ans … |
| R-32 | HISTORIE | Das Team (Rollen) | Strippenzieher-Entscheid 2026-07-13 — die frühere Regel ist aufgehoben |

Die Zitate sind **wörtliche Ausschnitte**, oft nur Halbsätze — genau so ist es richtig: Der Regressionstest prüft wörtliches (whitespace-normalisiertes) Vorkommen, und kurze Zitate überleben Umformatierungen, die einen ganzen Absatz brechen würden.

**Wohin Herleitung und Historie wandern**: in ein Projekt-`wiki/` mit eigenem `index.md`. Im Feldprojekt liegen dort `team-historie.md` (die Baugeschichte der Loop-Infrastruktur, wörtlich aus Anhang A ausgelagert), `kosten.md` (Kostenauswertung je Kaskade) und die Betriebs-Runbooks. Jede Seite verweist im Kopf zurück: „Verbindlich ist allein `CLAUDE.md` — hier steht, **wie es dazu kam**." Diesen Satz mitschreiben; er verhindert, dass das Wiki mit der Zeit als zweite Regelquelle gelesen wird.


---

## Verwandte Seiten

- [claude-md-ki-team](../vorlagen/claude-md-ki-team.md) — Die Vorlage, zu der diese Anleitung gehört
- [read-only-guard](../konzepte/read-only-guard.md) — Die 3-Linien-Durchsetzung aus A.4 im Detail
- [kostencounter](../konzepte/kostencounter.md) — Kostenkontroll-Standard dieses Wikis (Bezug zu A.7/A.9)
- [ralph-schleife](../konzepte/ralph-schleife.md) — Das Loop-Muster hinter dem Bau-Loop
- [finder-fixer-prinzip](../konzepte/finder-fixer-prinzip.md) — Warum Guard und Dreisatz-Verifikation getrennt sind
- [claude-md-token-sparen](../konzepte/claude-md-token-sparen.md) — Der Token-Grund hinter A.10 und hinter dieser Auslagerung
- [ki-team-forensik](../konzepte/ki-team-forensik.md) — Konzeptskizze: dieselbe Infrastruktur für Legacy-Forensik

---

[Wiki-Index](../index.md)

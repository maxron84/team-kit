# Anhang A — warum das Kit so gebaut ist

**Diese Datei ist die Warum-Schicht des Kits.** Sie erklärt die Entscheidungen
hinter der Mechanik und die Lehren, die sie erzwungen haben. Sie ist **keine**
Bedienanleitung und **keine** Regelquelle:

| Frage | steht in |
|---|---|
| Wie bediene ich das Team? | `bootstrap/TEAM.md` (landet im Zielprojekt) |
| Woran halten sich die Rollen? | `bootstrap/CLAUDE.md.vorlage` (wird zu `CLAUDE.md`) |
| **Warum ist es so gebaut?** | **diese Datei** |

Sie bleibt im Kit-Repo — der Installer kopiert sie **nicht** ins Zielprojekt.
Wer dort auf „Anhang A.7" stößt, liest hier nach.

**Quellen:** Feldprojekt `website-maxron-de`, Kaskaden 1–22 (2026-07-10 bis
2026-08-01); Feldprojekt `team-kit_project_platformer`, 33 Kaskaden (bis
2026-08-11); Einzug in `Project-Family-ERP` (2026-08-13). Die Abschnitts-
nummern **A.0–A.10 bleiben stabil** — Regeldatei, Regel-Inventar und
Backlog-Einträge verweisen darauf.

---

## A.0 Was vor dem ersten Lauf existieren muss

Die Rollen lesen und schreiben an **festen** Stellen. Fehlt eine davon, bricht
der Lauf ab oder — schlimmer — eine Rolle legt sie in einem geratenen Format
neu an. Der Installer legt deshalb alle an:

| Datei | Zweck | Startinhalt |
|---|---|---|
| `CLAUDE.md` | Regelquelle (Vorlage, Platzhalter gefüllt) | Vorlage |
| `CHANGELOG.md` | Übergabepunkt aller Rollen | Kopf + leerer `## [Unreleased]`-Block |
| `<plan>/roadmap-skizzen.md` | Ungehärtete Stränge | Überschrift + erste Skizze |
| `<plan>/backlog.md` | Aufgaben, die keine Kaskade sind | Überschrift |
| `<plan>/beutebuch.md` | Red-Team-Funde | Überschrift **+ `## Vorlage`-Block mit dem Fund-Format** + leerer `## Funde` |
| `<plan>/ermittlungsakten/` | Axels Ausgaben | leerer Ordner (`.gitkeep`) |
| `team/prompts/rolle-*.md` | Rollen-Briefings (A.10) | sechs Dateien, ~20 Zeilen |
| `.budget-ledger` | Kosten-Basis, **committet** | leer |
| `<test>/` | Reproducer- und Regressionstests | leerer Ordner |

*(Diese Liste fehlte bis 2026-08-01. Im Ursprungsprojekt waren die Dateien über
22 Kaskaden nebenbei entstanden — in einem neuen Projekt müssen sie **vorher**
da sein, sonst scheitert der erste Lauf an einer fehlenden Datei statt an einem
echten Problem.)*

Der **`## Vorlage`-Block im Beutebuch** ist kein Schmuck: Harry und Marv
schreiben ihre Funde direkt darunter und richten sich am Block aus. Ohne ihn
divergieren die Fund-Formate ab dem zweiten Sweep, und die Zustandsmaschine
(`team/tools/beutebuch.py`) findet die Status-Zeilen nicht mehr.

## A.1 Was der Installer vorher prüft

- **Git-Repo vorhanden?** (`git rev-parse --is-inside-work-tree`) — die Rollen
  committen, rollen zurück und prüfen Commit-Bereiche. Ohne Git funktioniert
  davon nichts, deshalb bricht der Installer hier ab.
- **Claude-CLI verfügbar?** (`claude --version`) — fehlt sie, werden die
  Dateien trotzdem installiert, aber kein Loop kann laufen.
- **Auth eingerichtet?** (`~/.config/claude-team/`) — siehe A.3.
- **Liegen schon Team-Dateien da?** Dann bleiben sie unangetastet; der
  Installer ist idempotent.

## A.2 Wo was liegt — und warum dort

Das Kit **liefert** die Skripte aus, statt sie generieren zu lassen. Die
Ablage-Konvention stammt aus dem Feld (`website-maxron-de`, 2026-07-11):

```
./vollautomatik.sh ./halbautomatik.sh ./team-status.sh ./team-test.sh
./ralph.sh ./frank.sh ./axel.sh ./harry.sh ./marv.sh    Entrypoints (Wurzel)
./team.config.sh                                        ALLE Projektwerte
team/lib.sh  team/redteam.sh                            Bibliothek
team/tools/kosten.py  team/tools/beutebuch.py           Werkzeuge (Python)
team/prompts/rolle-*.md                                 Rollen-Briefings
team/tests/                                             Team-Regressionstests
```

**Einstiegspunkte sichtbar oben, Werkzeug im Unterordner** — dieselbe Logik wie
`Makefile`/`.github/`. Der Strippenzieher tippt `./vollautomatik.sh` direkt.
Die Entrypoints sind über relative Geschwister-Pfade eng verzahnt und erwarten
die Repo-Wurzel als Standort — nicht ohne Not verschieben.

Der `team/`-Namensraum ist der zweite Teil derselben Entscheidung: Damit
berührt das Kit die Konventionen des Projekts nicht. Der Test- und der
Produktivcode-Ordner bleiben dem Projekt, und kein stack-fremder Code landet
darin.

**`.gitignore`-Fragment** (vom Installer angehängt):

```gitignore
.ralph-logs/ .team-logs/     # Rohlogs, rotiert
.team-loop.lock
.ralph-state .harry-state .marv-state
.ralph-plan                  # Zeiger auf den aktiven Plan
.frank-attempts              # Versuchszähler des Fixers
.budget-ledger.lock          # Lock der Ledger-Datei (Race, HM-48)
backups/
```

**Nicht** ignorieren: `.budget-ledger` selbst — sie ist die committete
Kostenbasis. `.ralph-plan` und `.budget-ledger.lock` sind die wichtigsten
Einträge der Liste: Ohne sie tauchen sie als Arbeitsverzeichnis-Änderung im
Read-Only-Guard auf.

## A.3 Auth-Fallback ✅ erprobt für alle automatisierten Rollen

Zentral in `team/lib.sh` (Helfer `team_claude`): Rollen starten im
**Abomodus**, fallen bei einem gescheiterten Aufruf **aufruf-lokal** auf `api`
zurück, danach zurück zu Abo.

**Axel** ist bei der **Auth** in die Abo-first-Regel aufgenommen
(Strippenzieher-Entscheid 2026-07-10: starkes Modell im Abo ist günstiger, das
Budget-Cap pro Fall bleibt als Airbag) — sein **Modell** bleibt davon unberührt
immer stark. Modell und Auth sind zwei getrennte Achsen. Seit dem
Folge-Entscheid 2026-07-13 läuft auch Der Architekt Abo-first — damit ist
**keine** Rolle mehr fest API, und die Kosten der interaktiven Rollen sind
**Abo-Gegenwert** statt Konsolenwert (Folgewirkung auf A.9).

- **`team_resolve_auth_mode [rollen-default]`**: löst Env `AUTH_MODE` →
  `~/.config/claude-team/auth-mode` → Rollen-Default auf. `abo` **entfernt**
  `ANTHROPIC_API_KEY` aus der Prozess-Umgebung (Verdrängungsfalle); `api` lädt
  den Key notfalls aus `~/.config/claude-team/api-key` (`chmod 600`) — erst
  diese Key-Datei macht den Fallback möglich, wenn der Loop ohne Key in der Env
  gestartet wurde.
- **Stufen-lokal durch frische Auflösung**: Der Loop merkt sich die etwaige
  Nutzer-Übersteuerung beim Start (`AUTH_MODE_START`) und löst **pro Stufe
  neu** auf — damit endet jeder Fallback automatisch mit der Stufe.
- **Fehlersignal** (✅ verifiziert, siehe A.5): Exit-Code ≠ 0 **oder**
  `is_error: true` in der `--output-format json`-Antwort (Helfer
  `team_result_is_error`; unlesbares JSON zählt als Fehler).
- **Genau ein Retry**: Scheitert der Abo-Aufruf, folgt ein einziger
  API-Versuch mit eigener Log-Datei; scheitert auch der → harter Abbruch.
- **Maschinen-Einrichtung**: `~/.claude/scripts/team-auth-setup.sh` (idempotent;
  Key-Migration aus Shell-Profilen mit Backup, optionaler headless Abo-Test
  inklusive Erkennung der „takes precedence"-Warnung).

## A.4 Read-Only-Guard — drei Linien ✅ erprobt

1. **Prompt** — „Du bist Harry/Marv, schreibe ausschließlich in Test- und
   Plan-Ordner." (notwendig, nicht hinreichend)
2. **Tool-Permissions** — headless `--permission-mode default` + enge
   `--allowedTools`-Liste: `Read`/`Grep`/`Glob` überall, `Write`/`Edit` nur auf
   Test- und Plan-Ordner, **kein** `git commit` in der Allowlist (das Skript
   committet die erlaubten Änderungen deterministisch — der Angreifer nicht).
3. **Post-Hook** (deterministische Garantie) — nach der Iteration
   `git diff --name-only <START_HASH> HEAD` + `git status --porcelain` gegen
   die Whitelist (`team_guard_verify` in `team/lib.sh`).

> ⚠️ **Härtungs-Lektion (2026-07-10, teuer gelernt):** Der Rollback in Linie 3
> muss **chirurgisch** sein — **nur die konkret gelisteten Verletzer-Pfade**
> zurücksetzen (getrackt → `git checkout <START_HASH> -- <pfad>`; neu → gezielt
> `rm`/`git rm`). Ein blindes `git reset --hard` + `git clean -fd` ist ein
> Footgun: Im Feldtest löschte es die **gesamte noch uncommittete
> Team-Infrastruktur**, weil im Testmoment alle neuen Skripte als
> „Nicht-Whitelist" galten. Zwei Betriebsregeln: (a) **Infrastruktur
> committen, bevor** je ein Guard läuft; (b) **Guard-Tests nur in einem
> Wegwerf-Repo**, nie im echten.

> ⚠️ **Staging-Lektion (2026-07-11):** Beim Commit der erlaubten Änderungen
> **datei-genau stagen**, nicht ordner-weit. Der Sweep-Commit staged sonst den
> **ganzen** Plan-Ordner, obwohl Harry/Marv nur ins Beutebuch schreiben. Da Der
> Architekt interaktiv **außerhalb des `flock`** arbeitet, kann er gleichzeitig
> uncommittete Plan-Dateien unter derselben Whitelist liegen haben — ein
> parallel laufender Sweep zog so fremde Architekten-Arbeit in seinen Commit.
> Eine Ordner-Whitelist ist **nicht** dasselbe wie datei-genaues Staging.

> ⚠️ **Zuschreibungs-Lektion (`BL-16`, 2026-08-01):** Linie 3 hatte **keinen
> Ausgangszustand**. Sie las nur „welche Pfade sind **jetzt** schmutzig" und
> schrieb jeden davon der **laufenden Rolle** zu — jeder fremde Schreiber
> (parallele Sitzung, Handänderung, abgebrochenes Werkzeug) wurde angelastet
> **und** hart zurückgesetzt. Das chirurgische `git checkout -- <pfad>`
> zerstört fremde Arbeit **genauso**, nur gezielter. Real eingetreten: Axels
> korrekte Ermittlung zählte als „Aufruf fehlgeschlagen" → Stagnationszähler →
> **Lauf gestoppt**, und die zurückgerollten Pfade waren die unbeteiligte
> Arbeit einer parallelen Sitzung. **Zwei Ebenen, getrennt zu bauen:**
> (1) **Zuschreibung** — `team_guard_begin` hält einen Schnappschuss mit
> **Blob-Hashes** (nicht nur Pfaden, sonst kommt eine Rolle frei, die eine
> ohnehin schmutzige Datei anfasst); was vorher schmutzig war und unverändert
> blieb, gehört nicht der Rolle. (2) **Urteil** — liegt das **Ergebnis** der
> Rolle vor (Akte + Statuswechsel bzw. Sweep-Quittung), kassiert der Guard den
> **Übergriff**, nicht die Arbeit. **Diagnose-Lehre:** Die Meldung muss beide
> Fälle **sprachlich trennen** — „diese Pfade waren beim Rollenstart bereits
> geändert" vs. „**diese Rolle** hat sie geändert".

> **Frank-Variante:** Frank *darf* Produktivcode ändern → statt Guard eine
> **Dreisatz-Verifikation** (ein Fix-Commit im Bereich `START_HASH..HEAD`,
> CHANGELOG ergänzt, Beutebuch-Status auf `erledigt`).
>
> ⚠️ **Verifikations-Lektion (2026-07-10):** **Nicht** verlangen, dass **HEAD
> selbst** der Fix-Commit ist — der Fixer darf den CHANGELOG-/Status-Edit
> legitim in einen `docs:`-Folgecommit legen. Prüfe stattdessen
> `git log START_HASH..HEAD --pretty=%s`. Der ursprüngliche „letzter
> Commit"-Check rollte korrekt gefixte Arbeit fälschlich zurück.

**Die Whitelist ist positiv — und damit endet der Schutz an ihrem Rand**
(`BL-51`). Test- und Plan-Ordner sind die einzigen Pfade, die die
Read-Only-Rollen schreiben dürfen; dort schlägt der Guard nie an. In einem
neuen Projekt ist das folgenlos. Zieht das Team in eine gewachsene Codebasis
ein, liegt dort fremdes Eigentum, und die drei ausdrücklich als read-only
geführten Rollen haben Schreib- und Löschrecht darauf. Der Installer warnt und
vermerkt den Bestand in `TEAM_*_ORDNER_BESTAND`, die Rollen-Prompts nennen ihn
als fremdes Eigentum — **das ist eine Prompt-Auflage, keine Mechanik.** Die
harte Variante bleibt ein eigener, leerer Plan-Ordner.

## A.5 Faktencheck-Pflicht (Spec vor Annahme)

An der **real installierten** CLI verifizieren — **nicht raten**:

- **Tool-Permission-Format** (Settings-Datei vs. Flags; ob `permissions.deny`
  unterstützt wird). Falls `deny` fehlt: **Post-Hook (Linie 3) ist die
  Haupt-Garantie** — der Guard ist gegen beide Fälle robust. ✅ **verifiziert
  (2026-07-10):** headless `--permission-mode default` + `--allowedTools`
  greift; ein Sweep mit auf Test-/Plan-Ordner beschränkter Allowlist ließ
  Produktivcode unangetastet.
- **Provider-Timeout-Signal** für den Auth-Fallback — ✅ verifiziert
  (2026-07-10): Exit-Code ≠ 0 **oder** Feld `is_error` in der
  `--output-format json`-Ausgabe.

> ⚠️ `--permission-mode default` ist **undokumentiert**. Claude Code 2.1.206
> akzeptiert den Wert, listet ihn in `claude --help` aber nicht mehr auf.
> Entfernt eine künftige CLI ihn, schlagen genau die beiden Read-Only-Rollen
> fehl — dann den Nachfolger einsetzen und die Guard-Wirksamkeit **erneut
> gegen die CLI verifizieren**.

## A.6 Parallelität & Reproducer

- **Sequenziell** (die Rollen hängen inhaltlich voneinander ab: Ralph → Red
  Team → Frank) + **`flock`-Airbag** in **allen** Loops, gegen
  `index.lock`-/`status`-Races. Echte Parallelität (Git-Worktrees) bleibt
  späterer Ausbau.
- **Guard-Reproducer:** ein Loop, der absichtlich Produktivcode anfasst, **muss**
  vom Post-Hook hart zurückgerollt werden (grüner Regressions-Schutz).

## A.7 Budget-Governance & Feld-Betriebslehren ✅ erprobt

**Modell: „Pro-Lauf-Deckel = operative Grenze, Gesamtstand nur dokumentiert"**
— statt eines starren, wandernden Projekt-Gesamtdeckels.

- **Committete `.budget-ledger`** — append-only, pipe-getrennt, **nicht**
  `.gitignore`-t. Sie ist die maschinenlesbare historische Basis, weil die
  Log-Ordner rotiert und ignoriert werden und den Stand sonst „vergessen".
- **Log-Rotation (Pflicht, sonst Doppelzählung) — aber im Closeout, nicht im
  Lauf.** Wer eine committete Ledger-Datei einführt, **muss** die Rohlogs
  **nach** dem Anhängen der Ledger-Zeile aus dem gezählten Pfad entfernen —
  **archivieren, nicht löschen** (`team_logs_archivieren`, verschiebt nach
  `<dir>/archiv/`, das nicht-rekursiv nicht mitgezählt wird). Fehlt der
  Schritt, zählt **jede** abgeschlossene Kaskade **doppelt**. **Reihenfolge:
  Ledger-Zeile anhängen → direkt danach archivieren — beides im
  Architekten-Closeout NACH dem Lauf, niemals in einer Loop-Stufe** (Lehre 8).
- **Kontostand-Werkzeug** (`./team-status.sh --budget`, Kern
  `team/tools/kosten.py`): summiert Ledger-Basis **plus** laufende Logs und
  weist **real via API abgerechnet** und **Abo-Gegenwert** getrennt aus — sonst
  wird der Abo-Gegenwert als reale Ausgabe fehlinterpretiert.
- **Zwei Kennzahlen sauber trennen — nie vermischen.** **A) Kosten dieses
  Laufs** (nur Logs seit Lauf-Start) ist die **operative Grenze** für die
  Durchsetzung. **B) Gesamt-Kontostand** (lebenslang: Ledger + alle Logs) ist
  **reine Anzeige**. Wird die Durchsetzung versehentlich auf B umgestellt,
  stoppt der Lauf **sofort**, sobald die Lebenssumme die Plan-Empfehlung
  übersteigt — noch bevor der aktuelle Lauf etwas kostet.
- **`BUDGET_EMPFEHLUNG_USD=…` je Kaskaden-Plan** — der Architekt setzt sie
  analog zu `RALPH_CAP=…`. Die Vollautomatik **hebt den Lauf-Deckel nur an,
  senkt nie**; `TEAM_BUDGET_USD=…` hat Vorrang.
- **CAP/PLAN aus dem aktiven Plan statt Skript-Edit** — der Loop liest
  `RALPH_CAP` aus dem aktiven Plan und den Plan-Pfad aus `.ralph-plan`. Nur das
  *Auslesen* ist automatisiert, das *Weiterschalten* bleibt bewusste
  Strippenzieher-Aktion. Verhindert den stillen Fehlstart „`RALPH_CAP`
  vergessen".

**Feld-Betriebslehren — in scharfen Läufen real erlebt:**

1. **Budget-Cap-Timing.** Der Pro-Stufe-Check greift **nach** dem LLM-Aufruf,
   aber **vor** dem State-Weiterschalten. Sprengt eine Stufe den Cap, ist ihre
   Arbeit bereits **committet**, aber die State-Datei bleibt stehen — **kein
   Datenverlust**. Der Mensch prüft den Commit, schaltet weiter, setzt fort.
   **Konsequenz:** den Pro-Stufe-Default großzügig wählen (im Feld 1 → 3 USD
   angehoben).
2. **Red-Team-Fokus ist kaskaden-abhängig ✅ gebaut.** Ein fest auf den
   Produktivcode verdrahteter Auftrag zielt bei einer **Infrastruktur-Kaskade**
   am Bau vorbei. Lösung: `TEAM_REDTEAM_FOCUS` übersteuert **beide**
   Verdrahtungen — den Auftrag der Red-Team-Rollen **und** den Prompt-Scope;
   ohne Env bleibt alles beim Produktivcode-Default.
3. **„success ohne Promise" ≠ harter Fehler ✅ gebaut.** Verweigert der Guard
   einer Rolle korrekt das Ausführen, kann sie in eine Rückfrage laufen und
   **kein Promise** ausgeben — obwohl sie einen Fund sauber übergeben hat.
   Wertet die Vollautomatik jedes Nicht-Promise als harten Stopp, hängt ein
   Neustart an derselben Stelle. **Beide Hebel gebaut:** (1) **Prompt-Härtung**
   — die Red-Team-Rollen stellen **nie** Ausführ-Rückfragen und geben bei
   sauber übergebenem Fund **immer** das Promise aus; (2) **Logik-Härtung** —
   ein `success`-Log mit **neuem, sauber übergebenem** Beutebuch-Eintrag zählt
   **nicht** als harter Fehler.
4. **Log-Rotation nicht vergessen (Doppelzählung).** Wird der Rotationsschritt
   vergessen, zählt jede abgeschlossene Kaskade doppelt; im Feld summierte sich
   das über sieben Kaskaden auf real ~13,7 USD Phantom-Kosten.
5. **Durchsetzung misst Pro-Lauf-Kosten (A), nicht die Lebenssumme (B).**
   Sonst müsste man bei jeder Kaskade den Pro-Lauf-Deckel hochdrehen, nur um
   eine Lebenszeit-Summe zu überbieten.
6. **Zwei-Schwellen-Budget statt divergierender Defaults ✅ gebaut (`BL-30`).**
   Ein zentraler **Soft-Cap** (`TEAM_ROLE_BUDGET_USD`, Default 5 USD) für alle
   Rollen plus ein **Hard-Cap** (`TEAM_ROLE_HARDCAP_USD`, Default 10 USD) für
   Frank & Axel. **Kernlehre (realer Auslöser `HM-32`):** Ein Pro-Fall-Cap
   greift **nach** dem bereits bezahlten Aufruf — ist er zu tief, wird ein
   teurer, aber plausibler Fix als „Fehlversuch" per Rollback weggeworfen und
   **vervielfacht** die Kosten, statt zu sparen. Für die iterierenden Rollen
   daher: Soft-Cap = **nur Hinweis**, erst der Hard-Cap bricht ab.
7. **Prosa-Arbeit gehört nicht in den Bau-Loop ✅ erprobt.** Eine Kaskade, die
   überwiegend **Text** umbaut, ist im Loop rund doppelt so teuer wie eine
   Code-Kaskade: im Feld Prosa-Stufen **3,23 / 3,97 / 4,68 USD** gegenüber
   **2,16 / 2,35 USD** für Code-Stufen derselben Kaskade. **Ursache:** Der Loop
   zahlt pro Stufe einen **Kaltstart** und liest die gewachsene Datei erneut
   vollständig; der interaktive Architekt hält denselben Kontext über alle
   Schritte. **Zweite Wirkung:** Die teuerste Stufe lag mit 4,68 USD über der
   80-%-Warnschwelle des 5-USD-Caps — die Kaskade stand näher am harten Stopp,
   als die Gesamtsumme vermuten ließ. **Konsequenz:** Textvolumen-gebundene
   Arbeit als **Architekt-Handarbeit** einplanen.
8. **Die Kostenmessung darf weder blind werden noch Fehlversuche verschenken
   ✅ gefixt (`BL-55`).** Im Feld druckte ein Abschlussbericht **6,1644 USD**,
   ausgegeben waren **26,4183 USD** — eine Untertreibung um **77 %**, entdeckt
   nur, weil ein Mensch die Zahl unplausibel fand. Drei Ursachen:
   - **(a) Die Pflicht-Reihenfolge war selbst der Bug.** Eine
     Abschluss-**Stufe** *innerhalb* des Laufs ledgerte und **archivierte** die
     Rohlogs — dadurch fielen 20,25 USD aus der Durchsetzung, unmittelbar bevor
     die offene Fixphase startete: der Deckel war ab da faktisch
     **zurückgesetzt**. **Regel:** Kostenabschluss nur im **Closeout nach dem
     Lauf**.
   - **(b) Die Durchsetzung muss die Archivpfade mitzählen**, sonst wird sie
     blind, sobald überhaupt jemand mitten im Lauf archiviert. Über einen
     mtime-Filter gelöst. Kennzahl **B** bleibt bewusst **ohne** Archiv — sonst
     zählt die Ledger-Basis doppelt.
   - **(c) Ein gescheiterter Aufrufversuch war gratis.** Die Kosten wurden aus
     dem **finalen** Log gelesen. Scheitert der Abo-Aufruf nach 1,68 USD und
     kostet der API-Fallback 0,40 USD, meldet die Stufe **0,40** — der
     Pro-Stufe-Cap ist damit **umgehbar**. **Regel:** Kosten eines Aufrufs =
     **Summe aller Versuchs-Logs**; das finale Log bleibt separat für die
     Promise-Auswertung.

## A.8 Session-Limit-Robustheit (429) ✅ erprobt (`BL-20`/`BL-25`)

Ein Session-Limit ist eine **dritte Fehlerklasse** neben „sauberer Erfolg" und
„echter Fehler". Der Verhaltens-Vertrag steht in der Regeldatei
(„Loop-Mechanik & Auth"); **hier** liegen die numerischen Default-Deckel:

- **Zentral in `team_claude()`:** 429-Erkennung (`api_error_status == 429`
  **oder** Text „session limit"/„resets"), **API-Fallback zuerst** (separates
  Kontingent), dann Auto-Retry mit Deckel, sonst **Exit 42**.
- **Kosten über alle Versuche summieren** (`BL-55`, A.7/Lehre 8c). Weil ein
  Aufruf hier **mehrfach** stattfinden kann und **jeder Versuch bezahlt** ist,
  sammelt `team_claude()` **alle** Versuchs-Logs. Die Variable mit dem
  **finalen** Log bleibt getrennt bestehen — sie ist die richtige Quelle für
  die Promise-Auswertung.
- **Env-Deckel:** `TEAM_429_MAX_RETRIES` = **2**, `TEAM_429_MAX_WARTEN` =
  **1800 s** (`0` schaltet den Auto-Retry ab), `TEAM_429_PUFFER` = **30 s**.
  Ist der Reset unbekannt oder liegt er jenseits des Maximums, entfällt das
  Warten sofort zugunsten des Pausen-Exits.
- **Alle Rollen-Skripte** reichen Exit 42 **unverändert** durch (kein
  State-Fortschritt, kein Fehlversuchs-Zähler); der Guard läuft auf **jedem**
  Pfad (auch Pause) **vor** der RC-Auswertung.
- **Auslauf-Bremse** `TEAM_FIX_MAX_STAGNATION` = **2** (zweite Obergrenze
  `TEAM_MAX_RUNDEN` = **12**): Die Fixphase bricht ab, wenn N Runden **keinen**
  Fortschritt zeigen (kein Fix, keine neue Akte, kein Statuswechsel).
- **Testbarkeit:** Fixture-Tests netz-/CLI-frei halten (`subprocess` +
  `bash -c`), Warten über `TEAM_DRY_RUN=1`/`TEAM_429_SKIP_SLEEP=1`
  überspringbar machen.
- **Es gibt eine VIERTE Fehlerklasse: Sitzung beendet, Auftrag unquittiert
  (`BL-41`, Exit 43).** Eine bauende Rolle startet einen Hintergrund-Task und
  „wartet" darauf — headless kommt die Benachrichtigung nie. Die CLI beendet
  die Sitzung, und das Ergebnis-JSON trägt `subtype: "success"`,
  `is_error: false`: **für jede is_error-Prüfung ein sauberer Erfolg.** Nur das
  fehlende Promise verrät den Fall. Vier Vorfälle im Feld, **19,47 USD**, jedes
  Mal für Arbeit, die fertig und grün war. Zwei Bauteile, **beide** nötig:
  (1) **Prävention** — die Smoke-Zeile verbietet Hintergrund-Betrieb **mit
  Begründung**; sie wirkt, aber sie steht am Prompt-Anfang, während der Vorfall
  nach 65 Turns passiert: Prompt-Prävention skaliert **gegenläufig zur
  Stufenlänge**. (2) **Erkennung** — fehlt das Promise, während das Log sich
  selbst für erfolgreich erklärt, gibt der Loop eine **benannte** Meldung samt
  Prüfweg aus (Exit **43**) statt „ECHTER Fehler". **Nicht auf Vokabeln
  prüfen:** Drei Vorfälle, drei Formulierungen — geprüft wird die Struktur.

## A.9 Interaktive Akteur-Kosten erfassen ✅ erprobt

Interaktiv arbeitende Rollen (Architekt, Frank-im-Abo) laufen **außerhalb**
`team_claude` und schreiben keine `total_cost_usd`-JSONs — sonst strukturell
unerfasst. Der operative Vertrag liegt **zweigeteilt** (`BL-56`): Das **WANN**
— Kostenabschluss nach dem Lauf, **nie** in einer Loop-Stufe — steht in der
Regeldatei, weil es auch Ralph begrenzt. Das **WIE** — Verben, Ledger-Zeilen,
Domänen, Abo-Messung — steht im Briefing `team/prompts/rolle-architekt.md`,
weil keine andere Rolle diese Befehle je aufruft. **Hier** liegen die
Bau-Details von `team/tools/kosten.py`:

- **A2 (nur Architekt):** `kosten.py architekt-schaetzung --since REF` schätzt
  aus dem Zeilen-Churn (`git diff --numstat` im Plan-Ordner + `CLAUDE.md` seit
  dem letzten Ledger-Commit) × Eichfaktor — bewusst grob, **nie** persistiert;
  für Produktivcode-Fixes nicht aussagekräftig, daher architekt-spezifisch.
- **A1 (rollen-agnostisch):** `kosten.py akteur-abschluss` hängt den Wert an
  und **ersetzt** (statt verdoppelt) die Zeile derselben **Rolle + Kaskade**.
  Der Wert ist im API-Betrieb der abgelesene Konsolenwert, im **Abo-Betrieb**
  die A2-Schätzung als **Abo-Gegenwert**. Defensiv validieren (endliche,
  nicht-negative Zahl, **keine** rohe `python3 -c`-Interpolation).
- **Sanitisierung gilt für *jedes* interpolierte Feld (`HM-36`).** Nicht nur
  die Notiz, sondern **auch** `rolle` und `kaskade` müssen **vor** dem
  Idempotenz-Match gegen Trennzeichen und Zeilenumbrüche gesäubert werden —
  sonst zerschießt ein einzelnes `|` im Rollennamen das Ledger-Schema.
- **Rollenkosten kaskadenscharf ledgern.** Die automatisch geloggten
  Rollenkosten wandern in **eine `rolle=roles`-Zeile je Kaskade**;
  `./team-status.sh --rollen-abschluss <kaskade> <domaene>` **ledgert und
  archiviert in einem Schritt**. Ein zweiter Aufruf für dieselbe Kaskade
  **bricht ab** und nennt Alt-, Neu- und Summenwert (`--addieren` für den
  Nachlauf, `--ersetzen` für die Korrektur — `BL-5`). Läuft **nie** in der
  Vollautomatik. **Die Notiz trägt den Rollenbezug voran** (`"Rollen: …"` /
  `"Bau: …"`, `BL-19`): Eine Bedienhandlung schreibt **zwei** Zeilen, aber es
  gibt nur **einen** Notiztext — ohne Vorspann beschreibt er höchstens eine von
  beiden. Die Notiz ist die einzige Prosa-Spur je Ledger-Zeile.
- **Auth-Split ehrlich halten.** Die Aufschlüsselung „real abgerechnet vs.
  Abo-Gegenwert" muss auch die `auth`-Spalte **archivierter** Zeilen
  berücksichtigen. Bucket-Regel mit **drittem Bucket**: `abo` → abo, `api` →
  api, **jeder** andere Wert → **`gemischt`**, so dass immer
  `abo + api + gemischt == Summe` gilt. **Nie** einen Split raten.
- **Ledger-Schema rückwärtskompatibel erweitern:**
  `datum | kaskade | usd | auth | domaene | rolle | notiz` (bestehende
  5-Feld-Zeilen bleiben gültig). `domaene` aus dem Kaskaden-**Bezug** ableiten,
  **nicht** aus dem rohen Plan-Ordner-Pfad. Altzeilen ohne die Felder zählen
  bei gesetztem Filter **nie** mit („unzugeordnet", nie stillschweigend
  zugeschlagen).
- **Ein Aufruf ohne Beleg ist keine Null (`BL-46`).** Ein gescheiterter Anlauf
  kann ein **0-Byte-Log** hinterlassen — im Feld nach **47 Minuten** Laufzeit.
  Eine Summierung, die eine unlesbare Datei stillschweigend mit 0 zählt, macht
  „Kosten unbekannt" von „hat nichts gekostet" ununterscheidbar: Die Stufe
  erscheint als die **billigste**, obwohl sie als teuerste angesetzt war.
  **Bauregel:** Ein unbrauchbares Versuchslog wird durch einen **Ersatzzettel**
  ersetzt (Dauer, `total_cost_usd: null`, Marke „verworfen"), die Summierung
  zählt ihn **nicht** als 0, sondern meldet ihn getrennt — **nicht schätzen,
  nur sichtbar machen**. Und: Der Zettel wird beim Abschluss **mitarchiviert**;
  sonst hält ihn der Ledger-Wächter dauerhaft für einen Verdachtsfall und
  empfiehlt eine Abhilfe, die nach `BL-5` echtes Geld vernichtet. Ein Wächter,
  dessen Warnung sich nicht abstellen lässt, erzieht zum Wegsehen (`BL-14`).
- **Jede Kennzahl sagt, ob sie in der Summe daneben schon drinsteckt
  (`BL-18`).** Die Architekt-Zeile in `--budget` hat zwei Modi, und der Modus
  schaltet ausgerechnet **beim Kaskaden-Abschluss** um — in dem Moment, in dem
  die Zahl abgelesen und weitergegeben wird: „geschätzt" (in **keiner**
  Ledger-Zeile ⇒ **nicht** im Gesamt) wird zu „echt" (⇒ **sehr wohl** im
  Gesamt). Ein fest verdrahteter Zusatz „nicht im Gesamt enthalten" ist damit
  die Hälfte der Zeit falsch und lädt zum Doppeladdieren ein (im Feld 81,27
  statt 71,57 USD, 13 % zu viel). **Der Zusatz gehört an den Modus, nicht an
  die Zeile.** Zweite Hälfte derselben Regel: Steht in einem Block, der
  **lebenslang** kumuliert, eine **kaskadenscharfe** Zahl, muss die
  Beschriftung den Bezugsrahmen nennen (`Architekt K3 (…)`).

**Drei Herleitungen, die den Vertrag tragen:**

- **Der reale Auslöser:** eine **einzelne** Architekten-Session kostete laut
  Konsole **~16 USD** — und war strukturell unerfasst, weil sie außerhalb
  `team_claude` lief. Ohne A1/A2 fällt nicht ein Rundungsfehler aus dem
  Ledger, sondern der Löwenanteil einer Kaskade.
- **Warum die Prüfung kein hartes Gate ist (`--ledger-pruefen`):** Exit `4` bei
  Warnbefunden, aber **kein** Abbruch im Closeout — eine Kaskade mit legitim
  fehlender Zeile könnte sonst nicht abschließen, und **ein Gate, das man
  regelmäßig umgeht, ist wirkungslos** (dieselbe Lehre wie `BL-14`).
  Stattdessen läuft die Prüfung bei jedem `--budget` ungefragt mit. Ihr Wert
  liegt darin, dass die dritte Frage („ergeben die archivierten Rohlogs mehr,
  als das Ledger ausweist?") ihre Kennzahl aus einer **anderen** Quelle zieht
  als das Geprüfte — genau das fehlte bei `BL-1`, `BL-4` und `BL-5`, die alle
  drei ein Mensch beim Vergleich zweier Dokumente fand, nicht ein Werkzeug.
- **Warum eine Domäne der Normalfall ist (`BL-9`):** Die frühere feste Trennung
  `produkt` ↔ `team` stammt aus dem **Ursprungsprojekt**, in dem die
  Team-Infrastruktur **im** Projekt gebaut wurde. Seit es das Kit gibt, gilt
  das nicht mehr — was am Team auffällt, geht als Fund ins Kit-Repo zurück und
  wird dort verbucht; eine „T.E.A.M."-Zeile im Kontostand eines Feldprojekts
  wäre strukturell `0.0000`. Eine Kennzahl, die immer null zeigt, erzieht dazu,
  den ganzen Block zu überlesen.

## A.10 Doku-Konsolidierung — die Regeldatei schlank halten ✅ erprobt (`BL-54`)

Nach ~20 Kaskaden wächst die Wissensbasis zuverlässig zu, ohne sich zu
schichten. Im Feld: `CLAUDE.md` **859 Zeilen**, davon ~334 Z reine
Baugeschichte und ~200 Z Herleitung — **geltende Kernregeln nur ~160 Z**; die
Fundliste **3075 Zeilen** bei ~46 abgeschlossenen von 53 Funden, von vier
Rollen bei **jedem** Sweep gelesen. Der operative Vertrag steht in der
Regeldatei („Doku-Hygiene"); hier die Bau-Details:

- **Die Doppelbezahlung ist der eigentliche Hebel.** Die Regeldatei liegt
  ohnehin im Systemprompt jeder Instanz. Fordert der Rollen-Prompt zusätzlich
  „Rolle siehe CLAUDE.md — lies sie zuerst", zahlt **jeder** Rollenaufruf einen
  **zweiten Voll-Read** (im Feld ~20–30 Aufrufe je Kaskade). Ersatz:
  **Rollen-Briefings** `team/prompts/rolle-*.md` mit **je ~20 Zeilen** (wer ich
  bin / mein Auftrag / meine eiserne Grenze / mein Dreisatz / mein Promise) und
  Fallback auf die Regeldatei, falls die Briefing-Datei fehlt. Im Feld:
  **859 Z → 19–23 Z je Rollenaufruf**.
- **Sicherheitsgurt zuerst bauen, dann umbauen — das ist die eigentliche
  Lehre.** **Vor** dem ersten Verschieben ein **Regel-Inventar** anlegen: jede
  Aussage der Regeldatei als **`NORM`** (geltendes Recht), **`HERLEITUNG`**
  (warum) oder **`HISTORIE`** (wann gebaut) klassifiziert, mit wörtlichem
  Zitat. Dazu ein **dauerhafter Regressionstest**: jedes `NORM`-Zitat muss
  wörtlich (whitespace-normalisiert) in seinem Träger vorkommen, und jeder
  Abschnitt muss im Inventar vertreten sein. `HERLEITUNG`/`HISTORIE` dürfen
  auswandern, `NORM` nicht. **Leitplanke: kürzt Text, nie Geltung** — Regel
  streichen, Default ändern, Guard lockern, Rolle umdefinieren sind im Umbau
  verboten.
- **Der Gurt hat im Feld real gehalten.** Als eine spätere Regeländerung
  (`BL-55`) eine Regel **bewusst umkehrte**, schlug der Test rot an und zwang
  dazu, die betroffenen Inventar-Zeilen **benannt** nachzuziehen. Genau dafür
  ist er da: Er verbietet keine Änderung, er macht sie **sichtbar**.
- **Fundliste rotieren — mit archiv-bewusster Nummernvergabe.** Abgeschlossene
  Funde in ein Archiv-Doc verschieben (im Feld **3075 Z → 46 Z**).
  **Fallstrick:** Die `next-id`-Logik muss **Archiv und aktive Liste zusammen**
  betrachten, sonst vergibt sie nach der Rotation **doppelte Fund-Nummern**.
- **Diese Kaskade nicht in den Loop geben** — sie ist der Musterfall für
  A.7/Lehre 7 (Prosa-Arbeit als Architekt-Handarbeit).
- **Im Kit gebaut (`BL-56`):** Das Inventar für die ausgelieferte Regeldatei
  liegt in [`regel-inventar.md`](regel-inventar.md), der Prüfer in
  [`kit-regelinventar.py`](../kit-regelinventar.py) (Stufe 7 in `kit-test.sh`).
  Zwei Bauentscheide, die ein Nachbau übernehmen sollte: **(1) Normalisiert
  vergleichen** — Blockquote-Marker, Betonungszeichen und Zeilenumbrüche raus,
  sonst scheitert ein wörtlich richtiges Zitat an einem `**nie**` mitten im
  Satz. **(2) Der Prüfer bewacht die VORLAGE, nicht die Installation** — ein
  Feldprojekt darf seine `CLAUDE.md` umformulieren, die Vorlage darf es nicht
  unbemerkt; deshalb liegt er in der Kit-Wurzel, die der Installer nicht
  kopiert. Die Abschnittsliste muss ```-Blöcke überspringen, sonst verlangt sie
  Inventarzeilen für die Beispiel-Gliederung des Abschluss-Docs.

### A.10.1 Bauformen im Detail

**Der Briefing-Helfer** (`team_briefing` in `team/lib.sh`) hat einen
**Pflicht-Fallback**, sonst legt eine fehlende Briefing-Datei den Lauf lahm:

```bash
# team_briefing <rolle>: Inhalt von team/prompts/rolle-<rolle>.md ausgeben.
# Fallback bei fehlender/leerer Datei: exakt die alte Prompt-Zeile — kein
# Abbruch, keine Fehlermeldung. Ein Fehler hier darf nie einen Lauf stoppen.
```

Aufruf in jedem Rollen-Skript als **erste** Prompt-Zeile:
`PROMPT="$(team_briefing ralph) …"`.

**Briefing-Aufbau** — fünf feste Überschriften, ~20 Zeilen: *Wer ich bin / Mein
Auftrag / Meine eiserne Grenze / Mein Dreisatz / Mein Promise.* Der Nachsatz
beim Promise („**immer**, auch nach einem Fund, ohne Ausführ-Rückfragen") ist
die gebaute „success ohne Promise"-Härtung (A.7, Lehre 3) — er gehört **in
jedes** Red-Team-Briefing, nicht nur in die Skriptlogik.

**Das Regel-Inventar** ist eine Tabelle mit Abschnitt, Klasse, Träger und
Zitat. Die Zitate sind **wörtliche Ausschnitte**, oft nur Halbsätze — genau so
ist es richtig: Der Test prüft wörtliches (normalisiertes) Vorkommen, und kurze
Zitate überleben Umformatierungen, die einen ganzen Absatz brechen würden.

**Die Träger-Spalte** nennt die Datei, die eine Aussage **ausliefert**. Ohne
sie ginge jede zwischen Regeldatei und Briefing verschobene Regel rot, und der
Gurt würde den Umbau **blockieren**, statt ihn sichtbar zu machen.

---

*Die konzeptionelle Grundlage (Vorlage, Guard-Konzept, Ralph-Schleife,
Finder-Fixer-Prinzip) liegt im privaten LLM-Wiki des Autors unter
`../../llm-wiki/wiki/` — ein Schwester-Repo, nicht Teil dieses Kits.*

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

**Quellen:** Das Ursprungsprojekt, Kaskaden 1–22 (2026-07-10 bis
2026-08-01); `Feld A`, 33 Kaskaden (bis 2026-08-11); Einzug in `Feld C`
(2026-08-13); `Feld B`, erste Kaskade auf der pwsh-Bahn (2026-08-21). Wofür
die Kürzel stehen, sagt die Profiltabelle im
[README](../README.md#herkunft) — die Projekte werden bewusst nicht
genannt, für den Beleg zählt ihre Lage. Die Abschnitts-
nummern **A.0–A.11 bleiben stabil** — Regeldatei, Regel-Inventar und
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
Ablage-Konvention stammt aus dem Feld (Ursprungsprojekt, 2026-07-11):

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
`Makefile`/`.github/`. Der Stakeholder tippt `./vollautomatik.sh` direkt.
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
(Stakeholder-Entscheid 2026-07-10: starkes Modell im Abo ist günstiger, das
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
- **Maschinen-Einrichtung**: `bash/scripts/team-auth-setup.sh` im Kit (idempotent;
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
  Stakeholder-Aktion. Verhindert den stillen Fehlstart „`RALPH_CAP`
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

9. **Der Kontext ist der Kostentreiber, nicht der erzeugte Text (`BL-35`).**
   Der teuerste Einzelposten des Feldprojekts war keine Kaskade, sondern **eine
   lange interaktive Sitzung**: 70,42 USD für eine Datei plus Sprites, davon
   rund **75 % reine Kontext-Wiedervorlage** (159 Mio Token `cache_read` gegen
   566 Tsd. Token erzeugten Text). Zum Vergleich kostete eine **komplette**
   Kaskade — Aushärtung, vier Bau-Stufen, Sweeps, Fixphase, Closeout — 24,71
   USD. Zwei Regeln, beide bezahlt:
   - **Rollenwechsel = neue Sitzung.** Ein `/model`-Wechsel tauscht das
     **Modell**, nicht den **Kontext**: Im Feld kostete Frank dadurch 11,44 USD
     reine Wiedervorlage, bevor er die erste Zeile ansah.
   - **Eine Nachbesserungsschleife ist kein Grund, die Sitzung offen zu
     lassen.** Ab der dritten, vierten Runde ist der Wiedervorlage-Anteil
     größer als die Arbeit. Ein Schnitt mit kurzer schriftlicher Übergabe ist
     billiger als die Bequemlichkeit des laufenden Kontexts.
10. **Ein Fund, dessen erster Schritt Wartezeit ist, gehört nicht in den Loop
   (`BL-36`).** Frank hat keine Wartezeit: Seine Fixphase ist auf
   **Urteilsarbeit in einer Sitzung** geschnitten. Im Feld bekam er einen
   Flaky-Test-Fund, dessen Reproduktion eine **Messreihe** war; er startete sie
   korrekt (35 Minuten, methodisch sauber) — und hatte danach keine Sitzung
   mehr, um den Fix zu committen. Der Lauf war verbraucht, das Ergebnis nicht
   gesichert. Erst als der Architekt die Messreihe **außerhalb** des Loops fuhr
   und den **diagnostizierten** Fund übergab, war es Frank-Arbeit. **Das
   Kriterium ist nicht „schwer", sondern „hat der Loop dafür die richtige
   Form?"** — verbraucht der kritische Pfad **Uhrzeit statt Denken**
   (Messreihen, Reproduktionsläufe, Warten auf externe Zustände), wird der Fund
   **vor** der Übergabe diagnostiziert.
11. **Zwei Schätzfehler, die sich über drei Kaskaden wiederholt haben
   (`BL-37`).** Beide betreffen die **Aushärtung**, nicht den Bau:
   - **Eine wiederholte Zusicherung ist nie billiger als das Original.** Die
     Stufe „zweiter Gegnertyp = die einfachere Zustandsmaschine" war mit 3,0
     angesetzt und kostete **5,90** (Soft-Cap gerissen): Sie musste die
     Zusicherung der Vorstufe in einer **anderen** Zustandsmaschine neu bauen.
     **Regel:** Eine Zusicherung, die in einer zweiten Zustandsmaschine
     wiederholt wird, bekommt **mindestens** den Ansatz der ersten.
   - **Kopplung schlägt Urteilsarbeit.** Dieselbe Kaskade setzte die
     „schwierige" Entwurfsstufe auf 5,0 (real 3,31, **−34 %**) und die
     „mechanische" Umbenennungsstufe auf 3,5 (real 4,69, **+34 %**). Der
     Unterschied ist die **Streuung**: konzentriert in einer neuen Datei gegen
     breit über vier Module gekoppelt. **Regel:** Der Kostentreiber im Loop ist
     die **Zahl gleichzeitig zu erfüllender Kopplungen**, nicht die
     Schwierigkeit des Gedankens — ab etwa drei gekoppelten Ansprüchen die
     Stufe teilen.
   - **Das Turn-Profil ist die Diagnose.** 87 Turns in 13 Minuten gegen 47/57
     Turns über 17 Minuten bei den *teureren* Nachbarstufen: viele kurze Turns
     = Nacharbeit (Planfehler), wenige lange = Urteilsarbeit (richtig
     geschnitten). Die Zahl steht in jedem Log; seit `BL-37` weist der
     Abschlussbericht sie aus (`kosten.py turns`).
12. **Beweisbarkeit gehört vor den Stufenschnitt (`BL-38`).** Im Feld hing eine
   ganze Kaskade an der Zusicherung „die Bewegung läuft in Subpixeln". Ein
   Spike vor der Aushärtung ergab: Unter der headless-Umgebung, in der **die
   gesamte Suite läuft**, ist genau diese Eigenschaft **prinzipiell
   unsichtbar** — der Software-Renderer rundet. Die Zusicherung wäre grün
   gewesen, ohne je geprüft worden zu sein. **Regel für die
   Aushärtungs-Checkliste:** *Mit welchem Befehl wird diese Zusicherung rot —
   und läuft dieser Befehl in der Umgebung, in der wir prüfen?* Kostet einen
   Spike, spart eine Kaskade, deren Kernaussage unbelegt bleibt. Das ist die
   `BL-17`-Krankheit in ihrer subtilsten Form: nicht die Verifikation richtet
   sich den Erfolg ein, sondern die **Prüfumgebung ist für den Gegenstand
   blind**.

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
  **A2 misst bewegten Text, der Treiber ist aber die Kontext-Wiedervorlage
  (`BL-32`).** Solange die Arbeit überwiegend **Schreiben** ist, trägt der
  Stellvertreter und überschätzt verlässlich (Feld: +13 / +28 / +23 / +27 %);
  daraus entstand die Korrekturregel `A2 / 1,25`. **Diese Regel gilt nur für
  schreiblastige Sitzungen** — pauschal angewandt vergrößert sie den Fehler:
  Eine Beschaffungssitzung (viel Lesen, 22 Mio Token Wiedervorlage, kaum
  Doku-Churn) zeigte 9,40 gegen gemessene **18,39** (−49 %), `A2 / 1,25` hätte
  daraus −59 % gemacht; eine gemischte Sitzung mit zwei Testläufen lag bei
  **+96 %**, korrigiert immer noch bei +57 %. **Reine Dateirotation zählt seit
  `BL-32` nicht mehr als Churn** (Archivdateien fallen aus der Messung) — nach
  einer Beutebuch-Rotation von 2.456 Zeilen sprang der Schätzer sonst auf 43,68
  USD für eine Sitzung, in der niemand nachgedacht hatte. **Belastbar ist die
  Richtung, nicht der Betrag:** A2 wird am Laufende abgelesen, gemessen wird
  nach dem Closeout; ein sauberer Datenpunkt entstünde erst, wenn beide im
  **selben Moment** genommen werden.
- **A1 (rollen-agnostisch):** `kosten.py akteur-abschluss` hängt den Wert an.
  Steht für dieselbe **Rolle + Kaskade** schon eine Zeile, **bricht der Aufruf
  ab** und nennt Alt-, Neu- und Summenwert (`--addieren` für die Folgesitzung,
  `--ersetzen` für die Korrektur einer Fehlmessung — `BL-25`, symmetrisch zu
  `BL-5`). Vorher wurde still ersetzt; im Feld sind so 5,5515 USD spurlos
  verschwunden, weil ein Akteur vormittags aushärtete und abends abschloss.
  Der Wert ist im API-Betrieb der abgelesene Konsolenwert, im **Abo-Betrieb**
  die Messung aus dem Sitzungstranskript als **Abo-Gegenwert**. Defensiv
  validieren (endliche, nicht-negative Zahl, **keine** rohe `python3
  -c`-Interpolation). **Wrapper reichen Schalter durch, statt sie zu
  schlucken** (`BL-26`): Ein verschluckter `--kaskade` buchte im Feld auf die
  Nummer aus `.ralph-plan` — die nach jedem Closeout auf die **vorige** Kaskade
  zeigt — und ersetzte dort eine abgeschlossene Zeile über 8,4678 USD.
- **Ein tauglicher Abo-Messweg hat fünf Eigenschaften (`BL-33`, `BL-116`).** Das Kit
  besitzt das Messwerkzeug nicht, **verlässt sich aber darauf** — deshalb steht
  hier, was es können muss, statt einen Namen zu nennen:
  **(1) Modell je Antwort** aus dem Transkript (`message.model`), nicht als
  Aufrufer-Vorgabe: Eine Sonnet-Sitzung mit der Opus-Tabelle abgerechnet ergab
  **14,36 statt 8,61 USD (+67 %)**, und eine in sich **gemischte** Sitzung (122
  Opus- und 520 Sonnet-Antworten) **106,13 statt 70,42 (+51 %)** — es genügt
  also nicht, den Aufrufer das Modell wählen zu lassen.
  **(2) Deduplikation über die Nachrichten-ID** — sonst grobe Überschätzung.
  **(3) Cache-Write nach Laufzeit getrennt.**
  **(4) Ein Transkript je Aufruf** — mehrere kommentarlos zu summieren macht
  die Messung in beiden Richtungen falsch.
  **(5) Den bereits gebuchten Abschnitt ausnehmen** — wer zwei Kaskaden in
  **derselben** Sitzung abschließt, misst beim zweiten Closeout wieder das
  **ganze** Transkript, und der schon gebuchte Teil wandert ein zweites Mal ins
  Ledger.
- **Warum (5) nicht schon in (1)–(4) steckte (`BL-116`).** Der Fall sieht aus
  wie (4) und ist es nicht: „Ein Transkript je Aufruf" verbietet, **mehrere**
  Transkripte zu summieren, und sagt nichts über **ein** Transkript mit zwei
  Buchungspunkten. Die Deduplikation über die Nachrichten-ID (2) greift
  ebenfalls nicht — jede Antwort der ersten Hälfte kommt genau **einmal** vor,
  nur eben bereits bezahlt. Und der A1-Kollisionsschutz greift nicht, weil er
  bei **derselben Rolle + Kaskade** anschlägt: Hier entstehen **zwei**
  Kaskadennummern und damit zwei Zeilen, die jede für sich plausibel sind. Der
  Fall fällt also in **keiner** bestehenden Prüfung auf — im Feld gemerkt erst
  beim Nachrechnen (`Feld A`, dortiges `BL-120`).
  **Feld-Rezept, solange kein Werkzeug es kann:** Rohwert **minus bereits
  gebucht**, mit der Rechnung im Notiztext der Ledger-Zeile, damit sie
  nachvollziehbar bleibt. **Billiger ist die Vermeidung:** ein Closeout je
  Sitzung — das steht im Briefing des Architekten, an der Stelle, an der
  gebucht wird.
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
  [`kit-regelinventar.py`](../geteilt/kit-regelinventar.py) (Stufe 9 in `kit-test.sh`).
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

## A.11 Modellwahl — agnostisch mit Anspruch, Ziel lokal

**Entscheid:** Das Kit bindet sich an **kein** Modell und an keinen Anbieter.
Die Rollen-Skripte kennen zwei Stufen — `TEAM_MODEL_LOOP` (Default `sonnet`)
und `TEAM_MODEL_STRONG` (Default `opus`) —, und beide sind Variablen mit
Default in `team/lib.sh`, keine Konstanten im Code.

**Warum zwei Stufen und nicht sechs.** Eine Stufe je Rolle wäre feiner, aber
niemand könnte sie begründen: Es gibt keine Messung, die Harry von Marv
unterscheidet. Zwei Stufen dagegen trennen genau das, was sich unterscheiden
lässt — *viele billige Aufrufe mit engem Auftrag* von *wenigen teuren mit
offenem Auftrag*. Die Trennlinie fällt mit der Kostenlinie zusammen: Die
schwache Stufe trägt die Masse der Läufe.

**Warum Fähigkeiten statt Benchmarks.** Ein Modell taugt hier nicht, weil es
eine Rangliste anführt, sondern weil es sechs Dinge durchhält: eine ~40 KB
große Regeldatei bei **jedem** Aufruf tragen; Werkzeuge über viele Schritte
zuverlässig aufrufen; das `<promise>`-Protokoll bis zum Ende eines langen Laufs
einhalten; Auflagen befolgen, die technisch nicht erzwungen sind; ohne
Rückfragen headless arbeiten; eine Stufe samt ihrer Tests zu Ende bringen.
Jeder dieser Punkte ist im Feld schon einmal gerissen — Punkt drei ist die
gesamte `BL-41`-Familie, Punkt sechs ist `BL-108`.

**Warum von unten nach oben eingewechselt wird.** Unten sind die Aufträge enger
umrissen, die Läufe zahlreicher und ein Fehlschlag billiger: Ein Ralph, der
eine Stufe vergeigt, kostet eine Stufe. Oben entscheidet sich, ob der Plan
überhaupt taugt — ein schwacher Architekt produziert Arbeit, die *korrekt
ausgeführt* trotzdem wertlos ist, und das fällt erst Kaskaden später auf. Der
billige Irrtum gehört deshalb an den Anfang der Umstellung, der teure ans Ende.

**Warum ein Modellwechsel den Guard aufwertet, nicht abwertet.** Die
Read-Only-Mechanik (A.4) ist der Grund, warum überhaupt mit einem schwächeren
Modell experimentiert werden **darf**: Sie hängt nicht an der Einsicht der
Rolle, sondern an Git und einer Whitelist. Je weniger man einem Modell
zutraut, desto mehr trägt die Mechanik — wer die Stufe wechselt, hat den
Guard-Test also nicht *auch* noch zu fahren, sondern **zuerst**.

**Was ein Wechsel technisch berührt.** `team_claude()` in `team/lib.sh` ist die
einzige Stelle, die die CLI aufruft. Daran hängen drei Verträge, die ein
Ersatz mitbringen muss: das **Ergebnis-JSON** (`is_error`, `subtype`,
`total_cost_usd`), der **Auth-Fallback** (A.3) und die 429-Behandlung (A.8).
Modellagnostisch ist das Kit heute; CLI-agnostisch ist es **nicht**, und diese
Unterscheidung gehört ehrlich benannt.

**Der offene Punkt, den ein lokaler Betrieb aufwirft:** Die gesamte
Kostenmechanik misst in **USD**. Läuft ein Modell lokal, ist dieser Wert null —
und ein Konto, das strukturell null zeigt, erzieht dazu, den Block zu überlesen
(dieselbe Falle wie `BL-9`/`BL-14`). Wer lokal fährt, braucht dort eine zweite
Einheit (Laufzeit, Energie, belegte GPU-Zeit) oder eine ausdrückliche
Kennzeichnung „nicht in USD gemessen". Bevor die erste lokale Stufe Standard
wird, ist das zu entscheiden — nicht danach.

**Prüfmaßstab für den Wechsel** (in dieser Reihenfolge): `kit-test.sh` grün ·
Guard-Wirksamkeit gegen die neue Bindung erneut verifiziert (A.5, A.4) · eine
vollständige Kaskade im Feld · und als Kennzahl die **Rate der Exit-`43`-Fälle
und Guard-Verletzungen je Kaskade** — sie misst genau das, was Benchmarks nicht
zeigen: ob das Modell das Protokoll durchhält, wenn niemand zusieht.

**Stand:** Alle automatisierten Rollen laufen über Claude Code (`claude -p`),
die Weiterentwicklung des Kits ebenfalls. Ein Lauf mit einem lokalen
Open-Weights-Modell ist **nicht** belegt. Das ist Ziel, nicht Zustand.

## A.12 Die Maschine vor dem Projekt — warum es `kit-einrichten.sh` gibt

`install.sh` prüft, was das **Zielprojekt** braucht (A.1). Was die **Maschine**
braucht, prüfte bis 2.11.0 niemand: Es stand in der README und galt
stillschweigend, weil das Kit nur auf der Maschine lief, auf der es entstanden
ist. Zwei Wege haben das aufgebrochen — der Klon aus GitHub durch jemand
anderen, und Windows mit WSL.

**Die Lücke, die der Klon aufdeckte.** README, `install.sh` und `TEAM.md`
verwiesen auf `~/.claude/scripts/team-auth-setup.sh` — eine Datei, die es nur
auf der Autorenmaschine gab. Wer klonte, bekam eine Anleitung, deren erster
Schritt ins Leere zeigte. Deshalb liegen die beiden Maschinen-Skripte jetzt
**im Repo** (`scripts/`), und `~/.claude/scripts/` bekommt auf Wunsch einen
**Symlink** statt einer Kopie: Eine zweite Kopie läuft dem Kit hinterher, und
zwar unbemerkt — dieselbe Klasse wie die Doku-Drift, gegen die A.10 arbeitet.

**Die drei WSL-Fallen haben ein gemeinsames Muster: Sie sehen aus wie ein
kaputtes Kit und sind keines.**

| Falle | Was wirklich passiert | Wie es sich meldet |
|---|---|---|
| CRLF | Git for Windows klont mit `core.autocrlf=true`; der Shebang wird zu `#!/usr/bin/env bash\r` | `bad interpreter: No such file or directory` |
| DrvFs (`/mnt/c`) | `chmod +x` verpufft ohne `metadata`-Mount; `flock` ohne Zusicherung; 9p ist langsam | `Permission denied` auf frisch installierten Entrypoints; nie sauberer Arbeitsbaum |
| Fehlende Bordmittel | `python3`/`flock` sind Abhängigkeiten der **Infrastruktur**, nicht des Projekts | Abbruch mitten im ersten Lauf — also **nach** bezahlter Agentenzeit |

Gegen die erste Falle hilft eine Datei statt einer Warnung: `.gitattributes`
mit `* text=auto eol=lf` erzwingt LF im Arbeitsbaum, unabhängig von der
Git-Konfiguration der Maschine. Die Prüfung bleibt trotzdem — für Klone, die
älter sind als die Datei.

**Der Bauentscheid, auf den es ankommt: proben statt voraussetzen.**
`kit-einrichten.sh` fragt nicht „liegt der Pfad unter `/mnt`?" und schließt
daraus auf die Rechte. Es legt eine temporäre Datei an, ruft `chmod +x` auf und
prüft, ob das Bit **hält**; danach setzt es `flock -n` auf dieselbe Datei. Das
ist derselbe Grundsatz wie A.5 (Faktencheck vor Annahme): Die Pfadheuristik
erklärt den Regelfall, die Probe entscheidet den Einzelfall — und sie greift
auch auf einem Netzlaufwerk, an das die Heuristik nicht gedacht hat.

### A.12.1 Das einzige Stück Kit außerhalb des Repos

`~/.claude/scripts/team-init.sh` ist der Kurzbefehl, der den Installer von
überall erreichbar macht. Er ist damit auch die **einzige** Datei des Kits, von
der eine Fassung außerhalb des Repos liegen kann — und genau deshalb die
einzige, die still verrotten kann. Ein Symlink kann das nicht; eine **Kopie**
schon, und sie meldet sich nicht. Sie behauptet eines Tages, das Kit sei nicht
da.

**Genau so ist der Umzug auf `bash/` und `pwsh/` aufgefallen** — nicht durch
eine Warnung des Kits, sondern durch einen Launcher, der nicht mehr lief. Die
Kopie auf der Maschine stammte aus einer Fassung von vor dem Verknüpfungs-
Mechanismus, suchte `<kit>/install.sh` und fand nichts mehr. Das Kit selbst war
grün.

Drei Maßnahmen, und keine ersetzt die andere:

1. **Der Launcher ist ablage-tolerant.** Er rät nicht *einen* Ort, sondern
   kennt alle, an denen ein Installer je lag (`bash/install.sh`, davor
   `install.sh`), und sucht zwei Elternebenen ab — weil er selbst vor der
   Bahn-Trennung eine Ebene höher lag. Eine Kopie beliebigen Alters
   funktioniert damit weiter: Sie muss wissen, **wo** das Kit liegt, nicht
   **wie** es innen aufgebaut ist. Die Liste wächst nach unten; oben steht
   immer die aktuelle Ablage.
2. **`install.sh` meldet eine veraltete Kopie bei jedem Lauf.** Das ist der
   Moment, in dem sich die Kit-Fassung ändert — also der einzige, in dem die
   Meldung ankommt. Geschrieben wird dort **nichts**: Ein Projekt-Installer,
   der ungefragt im Home-Verzeichnis aufräumt, ist eine Überraschung, keine
   Hilfe.
3. **`kit-einrichten.sh --verknuepfen` repariert.** Bis 2.10 hat es eine echte
   Datei nur *gemeldet* und nicht angefasst — vorsichtig gedacht, im Ergebnis
   wirkungslos: Die Meldung kommt nur, wenn jemand `--verknuepfen` fährt, und
   wer eine Kopie hat, hat es meist nie getan. Jetzt wird ersetzt, aber **nur
   was erkennbar vom Kit stammt** (die Bahn-Kennung aus `A.13` als Marke), mit
   einer Sicherung daneben. Was die Marke nicht trägt, hat jemand selbst
   geschrieben und bleibt liegen: Eine fremde Datei wegzuräumen wäre schlimmer
   als jede veraltete Kopie.

Geprüft wird das in `kit-test.sh` Stufe 10 — und zwar an einer **Kopie an
fremdem Ort**, nicht am Symlink: Der Symlink-Fall läuft über den aufgelösten
Pfad und würde den Fehler nie zeigen. Dazu die Gegenprobe, ohne die die
Meldung wertlos wäre: Der **aktuelle** Launcher darf sie nicht auslösen, sonst
warnt der Installer immer und niemand liest die Warnung noch.

**Wo die Probe selbst an ihre Grenze kommt: WSL 1.** Die Sperrprobe ist
`flock -n <datei> true` — *ein* Prozess. Auf einem echten Kernel belegt das
mit dem gelungenen Aufruf auch den wechselseitigen Ausschluss; auf einer
Syscall-Übersetzung ist das eine Annahme, keine Herleitung. Genau deshalb steht
in [einrichtung.md](einrichtung.md) für den WSL-1-Fall eine **Zwei-Prozess**-
Gegenprobe: Wo die eingebaute Probe nur die schwächere Aussage trifft, muss die
stärkere von Hand nachgereicht werden — statt die Lücke unbenannt zu lassen.
WSL 1 wird darum gewarnt, nicht abgebrochen: Wer in einer VM ohne nested
virtualization sitzt, hat die Wahl nicht.

**Belegstand:** Der Linux-Weg läuft auf der Entwicklungsmaschine. Der WSL-Weg
ist **hergeleitet, nicht durchlaufen** — die Regeln folgen aus den bekannten
Eigenschaften von DrvFs und Git for Windows, und die Proben melden den Fall an
der Maschine. Ein vollständiger Durchlauf unter Windows steht aus. Die Routine
selbst steht in [einrichtung.md](einrichtung.md).

---

## A.13 Zwei Bahnen, ein Wort dafür — die Bahn-Kennung

**Der Schnitt heißt nicht „Windows gegen Linux".** Er heißt `bash` gegen
`pwsh`. Wer unter Windows in einer WSL-Distro arbeitet, fährt die **Bash**-
Bahn; wer Windows ohne WSL benutzt, die **pwsh**-Bahn. Die alte Benennung
nach Betriebssystem beschrieb genau den häufigsten Fall falsch — und WSL ist
im Feld der Normalfall, nicht die Ausnahme.

Deshalb gilt seit 2026-08-20 ein Begriffspaar, und nur eines:

| Begriff | meint | Beispiele |
|---|---|---|
| **Bash-Bahn** / **pwsh-Bahn** | die Code-Bahn — welche Shell den Code ausführt | `ralph.sh` ↔ `ralph.ps1`, `lib.sh` ↔ `lib.psm1` |
| **Weg** | den Installationsweg des Anwenders | „Linux", „WSL", „Windows nativ" |

Vorher standen dafür vier Paare nebeneinander — „Linux/WSL" gegen „Windows
nativ" im README, „Bash-Zweig" gegen „PowerShell-Zweig" im Bauplan,
`feat(windows)` in den Commits, „Bahn" in `conftest.py`. Vier Namen für eine
Sache sind kein Stilproblem: Sie machen unauffindbar, was zusammengehört.
`conftest.py` hatte das Wort bereits scharf definiert (die Doppelbahn-Quote,
`@pytest.mark.nur_bash`) — die übrigen drei sind daran angeglichen worden,
nicht umgekehrt.

**Commit-Scopes** folgen demselben Paar: `(bash)`, `(pwsh)`, `(beide)` statt
`(windows)`. Ein Fix, der nur eine Bahn anfasst, ist damit an der Betreffzeile
zu erkennen — und ein `(bash)`-Commit an einer `.ps1` fällt auf.

### Warum die Kennung in jeder Datei steht

Bis hierher war die Zugehörigkeit einer Datei nur an ihrer **Endung**
abzulesen. Das reichte an drei Stellen nicht (der Stand vor dem Umzug, den
der nächste Abschnitt beschreibt):

1. `entry/` listete 29 Dateien alphabetisch verschränkt — `axel.cmd`,
   `axel.ps1`, `axel.sh`, `frank.cmd`, … Der Ordner zeigte keine zwei Bahnen,
   sondern einen Haufen.
2. Die Namensgleichheit `ralph.sh` ↔ `ralph.ps1` ↔ `ralph.cmd` ist die
   Kopplung, auf der die Doppelbahn-Testbahn ruht. Sie stand als
   Absichtserklärung im Bauplan und wurde von nichts geprüft.
3. Geteilter Code war von bahn-gebundenem nicht zu unterscheiden.
   `team/tools/*.py` ist **bewusst** nicht portiert — die pwsh-Bahn ist eine
   zweite *Orchestrierung*, kein zweiter Zustandscode. Dieser Entscheid stand
   in der Doku und in keiner Datei.

Jede Skriptdatei trägt deshalb in einer der ersten drei Zeilen:

```
# Bahn: bash  | Gegenstueck: ralph.ps1
# Bahn: pwsh  | Gegenstueck: ralph.sh
# Bahn: beide | Gegenstueck: keines (geteilter Zustandscode, nicht portiert)
```

**Reines ASCII, `|` statt Geviertstrich.** Dieselbe Zeile steht auch in einer
`.cmd`, und die liest der Kommandozeileninterpreter in der OEM-Codepage der
Maschine (850 oder 437, je nach Gerät) — ASCII ist das einzige, was dort
überall dasselbe bedeutet (`BL-113`, siehe A.2). Ein Suchmuster findet die
Zeile damit in jeder Datei des Kits:

```
grep -rlE '^(#|rem) Bahn: pwsh' .
```

Die Verankerung am Zeilenanfang ist nicht Kosmetik: Ohne sie stehen auch die
Dateien in der Liste, die das Muster nur **zitieren** — diese Doku, der Test
und der Backlog-Eintrag `BL-118`. Mit ihr bleibt genau eine Datei zu viel
übrig, nämlich diese hier (der Codeblock oben beginnt am Zeilenanfang).

**`keines` braucht einen Grund in Klammern.** Übernommen von
`@pytest.mark.nur_bash`, wo der Grund ebenfalls Pflicht ist: Eine fehlende und
eine vergessene Portierung sehen sonst gleich aus — und die vergessene fällt
erst auf der Zielmaschine auf, wie `BL-113` teuer belegt hat.

Durchgesetzt wird die Regel von
[`team/tests/test_bahn_kopfzeile.py`](../geteilt/tests/test_bahn_kopfzeile.py):
Vollständigkeit, Bahn passt zur Endung, Gegenstück existiert und liegt auf der
anderen Bahn, Paare sind wechselseitig, `keines` trägt einen Grund, Kennung
ist ASCII. Im Kit sucht der Test **rekursiv** — damit auch jede neue Datei
erfasst wird; im installierten Projekt prüft er nur die Namensliste des Kits,
weil dort fremder Code liegt (dieselbe Erwägung wie in
`test_bl113_bom_regel.py`).

### Die Ablage folgt der Kennung (`BL-118`, 2026-08-20)

Die Kennung machte die Trennung **greppbar**. Sichtbar wurde sie erst, als die
Ablage nachzog: `bash/`, `pwsh/` und `geteilt/` auf oberster Ebene, in der
Wurzel kein einziges Skript mehr. `ls bash/` ist seitdem die vollständige
Bash-Bahn — vorher war das eine Suche über vier Ordner und drei Endungen.

Drei Dinge sind dabei mehr als Optik geworden:

1. **`.gitattributes` hängt am Pfad statt an der Endung.** `pwsh/**/*.cmd
   text eol=crlf` statt `*.cmd text eol=crlf`. Eine Batch-Datei außerhalb von
   `pwsh/` bekommt die Regel **nicht** — und das ist gewollt: Dann stimmt die
   Ablage nicht. `kit-test.sh` prüft seitdem zweierlei, die Regel **und** dass
   git sie auf einer echten Datei anwendet (`git check-attr`); eine Regel, die
   dasteht und nicht greift, sieht im `grep` bestanden aus.
2. **Das Gegenstück ist über den Pfad prüfbar.** Im Kit liegt es in der
   **gespiegelten** Bahn — `bash/entry/ralph.sh` ↔ `pwsh/entry/ralph.ps1`,
   `bash/lib.sh` ↔ `pwsh/lib.psm1`. Gespiegelt wird nur das erste
   Pfadsegment; der Rest ist in beiden Bahnen identisch, und genau das ist
   die Zusicherung.
3. **Die Übersetzung steht an EINER Stelle.** Die Tests laufen in zwei
   Ablagen (Kit und installiertes Projekt) und sprachen die Kit-Ablage an 105
   Stellen direkt an. Statt 105 Fallunterscheidungen gibt es jetzt
   `kit_pfad()` in `conftest.py` — gesprochen wird in der Sprache des
   **Zielprojekts** (`kit_pfad("lib.sh")`), weil das die Ablage ist, für die
   die Tests geschrieben sind.

**Der Preis war die Fallhöhe.** Der Umzug hat in der Kit-Ablage 281 Tests
umgeworfen, bevor `kit_pfad()` da war, und 24 Dateien ließen sich nicht
einmal mehr einsammeln — ein einziger Import-Pfad in 23 Kopien. Maßstab war
deshalb nicht „grün", sondern **derselbe Befundstand wie vorher**: 21
Fehlschläge in der Kit-Ablage, Datei für Datei identisch mit dem Stand vor
dem Umzug (die Tests setzen die installierte Ablage voraus, siehe
`kit-test.sh`). In der Installation selbst: 431 grün, unverändert.

### Die Abwahl und ihr Rückweg (`BL-119`, 2026-08-20)

Im Zielprojekt bleiben **beide** Bahnen der Default, und das ist keine
Bequemlichkeit: `team.config.sh` und `team.config.ps1` sind zwei Generate
**einer** Quelle (denselben neun Antworten). Wer nur eine Bahn installiert,
hat unter dem anderen System keine Konfiguration — und schreibt sie
irgendwann von Hand. Genau dort fängt Drift an.

Der Wunsch aus dem Feld ist trotzdem berechtigt: „Warum liegen hier 19
Dateien für ein System, das ich nie benutze?" Die Antwort ist ein Schalter,
der die Abwahl beim **Anwender** lässt: `--nur-bash` / `--nur-pwsh`
(`-NurBash` / `-NurPwsh`). Nicht der Installer entscheidet, was fehlt.

**Was den Schalter erst vertretbar macht, ist der Rückweg.** Ein späteres
`--update` ohne Schalter muss das Projekt wieder vollständig machen — sonst
ist die Abwahl eine Einbahnstraße, und der Anwender sitzt mit einem halben
Projekt da, ohne es zu merken. Beim ersten Bau ist genau das passiert, und
der Haken saß an einer Stelle, die man leicht übersieht:

> Die Entrypoints kamen zurück, die **Konfiguration** nicht. Ein Update fasst
> `team.config.*` grundsätzlich nicht an (Projektdaten, wie das Ledger).
> Richtig — solange sie da ist. **Fehlt** sie, ist „nicht anfassen" kein
> Schutz mehr, sondern eine halbe Bahn: `ralph.ps1` läge da und fände keine
> Werte.

Der Update-Pfad erzeugt eine fehlende Bahn-Konfiguration deshalb neu, aus den
Werten der **vorhandenen** (nicht aus den Auslieferungswerten), und sagt es.
Dabei kam ein zweiter Fund heraus: Der Update-Pfad in `install.sh` hat eine
**eigene** Füll-Routine, und die kannte nur 13 der 17 Platzhalter. Für ihre
bisherige Aufgabe reichte das — sie renderte nur bestehende Dateien nach.
Sobald sie eine Datei *erzeugt*, zählt jeder Platzhalter: vier blieben stehen,
und die Datei war da und trotzdem halb fertig.

**In einem einbahnigen Projekt bleiben die Tests grün.** Eine abgewählte Bahn
ist kein Defekt — aber der Übersprung muss **sichtbar** sein, sonst liest er
sich am Ende wie ein bestandener Nachweis. `conftest.py` meldet ihn in der
Doppelbahn-Zusammenfassung („einbahnige Ablage: nur bash installiert — die
andere Bahn ist abgewählt"), dieselbe Bauart wie bei `@pytest.mark.nur_bash`.

Beides — Abwahl und Rückweg — steht als Stufe 8 in `kit-test.sh`, nicht in
der Doku: Ein Rückweg, den niemand fährt, verrottet.

---

*Die konzeptionelle Grundlage (Vorlage, Guard-Konzept, Ralph-Schleife,
Finder-Fixer-Prinzip) liegt im privaten LLM-Wiki des Autors unter
`../../llm-wiki/wiki/` — ein Schwester-Repo, nicht Teil dieses Kits.*

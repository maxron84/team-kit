![T.E.A.M. — Toll, ein anderer macht's. Sechs Rollenkarten im Terminal-Look:
Ralph Wiggum (Bau-Loop), der Architekt (Plan & Closeout), Frank der Fixer
(Ad-hoc-Fixes) — die drei dürfen Code schreiben; Harry (Red Team Security),
Marv (Red Team Chaos) und Axel Foley (Forensik) sind read-only. Darüber der
Leitsatz: Finder ≠ Fixer.](team-banner.webp)

# T.E.A.M.-Starterkit

Ein vollständiges KI-Rollenteam auf Knopfdruck in ein Software-Projekt —
frisch angelegt **oder seit Jahren gewachsen**.

```bash
git clone https://github.com/maxron84/team-kit.git ~/Source/team-kit
cd ~/Source/team-kit
bash bash/kit-einrichten.sh ~/Source/mein-projekt
```

`kit-einrichten.sh` prüft die Maschine (Bordmittel, Zeilenenden, Dateisystem,
Auth) und übergibt dann an `install.sh`. Wer die Maschine schon eingerichtet
hat, ruft den Installer direkt auf: `bash bash/install.sh ~/Source/mein-projekt` —
oder, nach `--verknuepfen`, von überall mit
`bash ~/.claude/scripts/team-init.sh <zielpfad>`.

**Windows** geht denselben Weg, aber **in einer WSL2-Distro** und mit dem Repo
im Linux-Dateisystem. Die ganze Routine für beide Plattformen, mit IDE (VS
Codium bzw. VS Code) und Agenten-Werkzeug, steht in
[doku/einrichtung.md](doku/einrichtung.md).

Ein Befehl, ein kurzes Aufnahme-Interview, danach liegen 121 Dateien im
Zielprojekt: der gehärtete Bau-Loop, das Read-Only Red Team, der Fixer, der
Forensiker, die Kostenmechanik, die Bootstrap-Dateien, die Bedienanleitung
`TEAM.md` und 369 Regressionstests.

**Stand: Version 2.10.0** (2026-08-16). Der Backlog des Kits ist wieder leer.
Neu: Der vierte `BL-41`-Ausgang — Log meldet Erfolg, Quittung fehlt — prüft
sich selbst, statt die Vollautomatik mitten in der Kaskade anzuhalten; im Feld
war der Fall neunmal aufgetreten und neunmal gleich ausgegangen. Behoben: ein
Kit-Test, der am Füllstand des Beutebuchs hing, und ein `install.sh --update`,
das ein gewachsenes `.gitignore` nie nachzog. Neu dokumentiert ist die
**Modellhaltung** des Kits (Abschnitt unten): agnostisch, mit benannten
Fähigkeitsanforderungen und lokalen Modellen als Fernziel. Abgetragene Einträge
stehen in [plans/backlog-archiv.md](plans/backlog-archiv.md) (63 Stück).

---

## Inhalt

> **Zum ersten Mal hier? → [doku/einrichtung.md](doku/einrichtung.md).**
> Klonen, Maschine einrichten, in ein Projekt einbinden — für **Linux** und für
> **Windows mit WSL**, mit IDE- und Werkzeug-Beispielen, einer Gegenprobe und
> elf Fehlerbildern. Dort steht auch die Trennlinie, die für dieses Kit
> tragend ist: **was Pflicht ist und was nur Beispiel.**

**Diese Seite:**

| Abschnitt | Worum es geht |
|---|---|
| [Was das T.E.A.M. ist](#was-das-team-ist) | Die sechs Rollen und das Prinzip *Finder ≠ Fixer* |
| [Modelle](#modelle--agnostisch-aber-nicht-anspruchslos) | Zwei Stufen statt Modellnamen, sechs vorausgesetzte Fähigkeiten, Ziel lokal |
| [Herkunft](#herkunft) | Woher der Code kommt und wo er scharf gelaufen ist |
| [Installation](#installation) | `install.sh`, das Aufnahme-Interview, `--update` gegen `--force` |
| [Nach der Installation](#nach-der-installation) | Die sechs Schritte bis zur ersten Kaskade |
| [In ein bestehendes Projekt](#in-ein-bestehendes-projekt) | Schreibzone und Prüfumfang im Bestand (`BL-51`, `BL-52`) |
| [Aufbau des Kits](#aufbau-des-kits) | Welche Datei wo liegt — im Kit und im Zielprojekt |
| [Betrieb](#betrieb) | Befehle und Exit-Codes |
| [Grenzen](#grenzen) | Was belegt ist und was ausdrücklich nicht |
| [Lizenz](#lizenz) | MIT |

**Die Dokumentation.** `doku/` bleibt im Kit und wird **nicht** mitinstalliert —
die Bedienanleitung fürs Zielprojekt ist `TEAM.md`:

| Datei | Für wen | Inhalt |
|---|---|---|
| **[doku/einrichtung.md](doku/einrichtung.md)** | **wer das Kit auf eine Maschine holt** | **Die Routine: Klonen, Bordmittel, WSL, IDE, Auth, Einbinden, Fehlerbilder, Belegstand** |
| [doku/faq.md](doku/faq.md) | wer beim Aufsetzen hängt | Ganze Fragen statt Symptomzeilen — beginnend mit *Claude-CLI nicht gefunden* (Linux, WSL, Windows) |
| [doku/anhang-a.md](doku/anhang-a.md) | wer wissen will, *warum* es so gebaut ist | Die Warum-Schicht: Bauentscheide und Feld-Betriebslehren (A.0–A.13) |
| [doku/regel-inventar.md](doku/regel-inventar.md) | wer eine Regel der Vorlage ändert | Jede Regel als NORM/HERLEITUNG/HISTORIE, mit Träger und wörtlichem Zitat |
| [CHANGELOG.md](CHANGELOG.md) | wer eine bestehende Installation nachzieht | Jede Änderung mit Begründung und Feldbeleg |
| [plans/backlog.md](plans/backlog.md) | wer am Kit mitbaut | Offene Punkte (Abgetragenes im [Archiv](plans/backlog-archiv.md)) |
| `TEAM.md` | der Strippenzieher im Zielprojekt | Bedienanleitung — wird installiert und liegt danach im Projekt |

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

## Modelle — agnostisch, aber nicht anspruchslos

**Das Kit legt sich auf kein Modell fest, weder heute noch künftig.** Die
Rollen-Skripte kennen keine Modellnamen, sie kennen zwei **Stufen**:

| Stufe | Variable | Default | Wer darauf läuft |
|---|---|---|---|
| schwach | `TEAM_MODEL_LOOP` | `sonnet` | Ralph (Bau-Loop), Harry und Marv (Sweep), Frank (Fixes) |
| stark | `TEAM_MODEL_STRONG` | `opus` | Axel (Forensik) — und die Architekten-Sitzung, die du selbst startest |

Beide stehen in [team/lib.sh](bash/lib.sh) und lassen sich pro Lauf
überschreiben (`TEAM_MODEL_LOOP=… ./vollautomatik.sh`). Es sind **Defaults,
keine Voraussetzung**.

Vorausgesetzt werden **Fähigkeiten**, nicht Anbieter. Das Niveau, auf dem sie
heute nachweislich reichen, ist das von **Sonnet** (schwache Stufe) und **Opus**
(starke Stufe). Ein Kandidat muss:

1. **eine große Regeldatei tragen** — `CLAUDE.md` wird bei jedem Rollenaufruf
   geladen (rund 40 KB) und ist die Grundlage jeder Auflage;
2. **Werkzeuge zuverlässig aufrufen** — Dateien lesen und schreiben, Shell,
   Tests starten, über viele Schritte hinweg;
3. **ein Ausgabeprotokoll durchhalten** — jede Rolle quittiert mit einem
   `<promise>`-Marker; wer ihn am Ende eines langen Laufs vergisst, produziert
   genau die Klasse „Arbeit fertig, Quittung fehlt" (`BL-41`);
4. **Auflagen einhalten, die niemand erzwingt** — die Read-Only-Rollen *könnten*
   Produktivcode schreiben; dass sie es nicht tun, ist zuerst Prompt-Disziplin
   und erst danach der Guard;
5. **ohne Rückfragen arbeiten** — die Läufe sind headless, es sitzt niemand
   daneben, der eine Zwischenfrage beantwortet;
6. **mehrstufige Arbeit selbst zu Ende bringen** — eine Stufe umfasst
   Produktivcode *und* die Tests, die sie beweisen.

**Stand heute** laufen alle automatisierten Rollen über **Claude Code**
(`claude -p`), die Weiterentwicklung des Kits selbst ebenfalls. Die eigentliche
Bindung ist dabei nicht das Modell, sondern die **CLI**: `team_claude()` in
`team/lib.sh` ist die **einzige** Stelle im Kit, die sie aufruft — dort hängen
das JSON-Ergebnisformat (`is_error`, `subtype`, `total_cost_usd`), der
Auth-Fallback und die Kostenmechanik dran. Wer das Kit auf eine andere Agenten-
CLI setzt, tauscht diese eine Funktion, nicht die Rollen.

**Das langfristige Ziel ist lokal.** Der Markt der Open-Weights-Modelle wird
beobachtet; sobald dort bezahlbare Fassungen die obigen Fähigkeiten halten,
werden sie **schrittweise von unten nach oben** zum Standard: erst die schwache
Stufe (Bau-Loop, Sweeps, Fixes — die Masse der Aufrufe und der Kosten), später
die starke (Forensik und Planung). Die Reihenfolge ist Absicht: Unten sind die
Aufgaben enger umrissen, die Läufe zahlreicher und ein Fehlschlag billiger; oben
entscheidet sich, ob ein Plan überhaupt taugt. Maßstab für den Wechsel sind
**nicht Benchmark-Zahlen, sondern die Zusicherungen dieses Kits**: `kit-test.sh`
grün, der Guard hält, das Promise-Protokoll wird durchgehalten, und der
Smoke-Test des Feldprojekts bleibt es auch. Bis dahin läuft die Entwicklung mit
den üblichen Cloud-Modellen weiter.

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
# Linux und WSL
bash bash/install.sh <zielpfad> [--nicht-interaktiv] [--update|--force]
                                [--nur-bash|--nur-pwsh]
```

```powershell
# Windows nativ (PowerShell 7, ohne WSL)
pwsh -File pwsh\install.ps1 <zielpfad> [-NichtInteraktiv] [-Update|-Force]
                                       [-NurBash|-NurPwsh]
```

> **Beide Installer erzeugen aus denselben neun Antworten byte-identische
> Bäume** — festgenagelt in `kit-test.sh`, Schritt 11/11. Sie schreiben auch
> **beide** Konfigurationen (`team.config.sh` *und* `team.config.ps1`), damit
> ein auf Linux eingerichtetes Projekt unter Windows nicht ohne Konfiguration
> dasteht. Die pwsh-Bahn ist **gebaut, aber noch nicht auf Windows
> abgenommen** — siehe [doku/einrichtung.md, *Belegstand*](doku/einrichtung.md#belegstand).

**Nur eine Bahn installieren:** `--nur-bash` bzw. `--nur-pwsh` (PowerShell:
`-NurBash` / `-NurPwsh`). Ein Projekt bekommt dann statt 29 Entrypoints nur
die zehn der gewählten Bahn. **Default ist beides**, und das hat einen Grund:
`team.config.sh` und `team.config.ps1` sind zwei Generate **einer** Quelle
(denselben neun Antworten). Wer nur eine Bahn installiert, hat unter dem
anderen System keine Konfiguration — und schreibt sie irgendwann von Hand.
Genau dort fängt Drift an. Die Abwahl ist deshalb ausdrücklich und kommt vom
Anwender, nie vom Installer.

**Sie ist keine Einbahnstraße:** Ein späteres `--update` *ohne* Schalter macht
das Projekt wieder vollständig — samt der fehlenden Konfiguration, erzeugt aus
den Werten der vorhandenen, nicht aus den Auslieferungswerten. In einem
einbahnigen Projekt bleiben die Team-Tests grün; die fehlende Bahn erscheint
als **sichtbarer** Vermerk in der Testzusammenfassung („einbahnige Ablage"),
nicht als Fehlschlag und nicht als stiller Übersprung.

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
Auth eingerichtet (`bash scripts/team-auth-setup.sh`). Geprüft und erklärt
werden sie von `kit-einrichten.sh` bzw. `kit-einrichten.ps1`; die ausführliche
Fassung — Linux, Windows mit WSL und Windows nativ — steht in
[doku/einrichtung.md](doku/einrichtung.md). Welche
**Fähigkeiten** ein Modell mitbringen muss — und warum das Kit trotzdem keinen
Modellnamen kennt — steht oben im Abschnitt **Modelle**.

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

# 4. Erste Kaskade planen — Sitzung im Projektordner, starke Stufe (Default Opus):
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

**Die Ablage trennt die beiden Bahnen — ein Blick sagt, was wozu gehört.**
`ls bash/` ist die vollständige Bash-Bahn, `ls pwsh/` die vollständige
pwsh-Bahn. Was in `geteilt/` liegt, gilt für beide und ist bewusst **nicht**
portiert.

```
bash/                   ALLES, was die Bash-Bahn ausmacht
├── install.sh          Der Installer
├── kit-einrichten.sh   Vorflug-Prüfung zwischen Klon und Installation:
│                       Bordmittel, Zeilenenden, Dateisystem (WSL!), Auth —
│                       prüft mit Proben statt Annahmen, kostet nichts
├── kit-test.sh         Selbstverifikation in 11 Stufen: installiert in ein
│                       Wegwerf-Repo, fährt dort die Tests zweimal (Ausliefe-
│                       rungswerte und angepasste team.config.sh), prüft
│                       Update-Pfad, Bestandslage, Bahn-Abwahl samt
│                       Rueckweg, Regel-Inventar und die Einrichtungs-
│                       routine — DAS Gate vor jedem Push
├── lib.sh              Auth, Guard, Budget, 429-Mechanik, Kosten
├── redteam.sh          Gemeinsame Sweep-Logik von Harry und Marv
├── entry/              Entrypoints — landen in der WURZEL des Zielprojekts
│   ├── vollautomatik.sh    Orchestrator: Ralph → Red Team → Frank → Axel
│   ├── halbautomatik.sh    Schrittweise, mit Halt beim Menschen
│   ├── team-status.sh      Kontostand, Pipeline, Beutebuch-Übersicht
│   ├── team-test.sh        Regressionstests der Team-Infrastruktur
│   ├── ralph.sh frank.sh axel.sh harry.sh marv.sh
│   └── team.config.sh      ALLE Projektwerte an einer Stelle
└── scripts/            Maschinen-Skripte, NICHT installiert
    ├── team-auth-setup.sh  Auth der Agenten-CLI (Beispiel Claude Code)
    └── team-init.sh        Dünner Launcher, für ~/.claude/scripts/

pwsh/                   ALLES, was die pwsh-Bahn ausmacht — spiegelbildlich
├── install.ps1  kit-einrichten.ps1  kit-test.ps1
├── pruefe-windows.ps1  Eigenständige Vorflug-Probe für die Zielmaschine,
│                       hängt an keiner Kit-Datei (kein Gegenstück in bash/)
├── lib.psm1  redteam.ps1
├── entry/              ralph.ps1 + ralph.cmd, frank.ps1 + frank.cmd, …
│                       Die .cmd sind Einzeiler auf die gleichnamige .ps1
└── scripts/            team-auth-setup.ps1  team-init.ps1

geteilt/                Gilt auf BEIDEN Bahnen, bewusst nicht portiert
├── tools/              kosten.py, beutebuch.py, zitat_lint.py — Ledger,
│                       Beutebuch und Kostenrechnung liegen auf beiden Wegen
│                       in denselben Dateien. Die pwsh-Bahn ist eine zweite
│                       ORCHESTRIERUNG, kein zweiter Zustandscode
├── prompts/            Sechs Rollen-Briefings (inkl. Architekt)
├── tests/              69 Testdateien, 487 Fälle — der Doppelbahn-Harnisch
│                       fährt jeden Fall gegen BEIDE Bahnen, aus EINEM
│                       Testkörper
└── kit-regelinventar.py  Prüfer für das Regel-Inventar (Stufe 9). Kit-only —
                        bewacht die Vorlage, nicht die installierte CLAUDE.md

bootstrap/              CLAUDE.md- und TEAM.md-Vorlage, CHANGELOG, Beutebuch, Roadmap, …
plans/                  Roadmap und Backlog DES KITS (nicht die Vorlagen —
                        die liegen in bootstrap/ und werden installiert)
doku/anhang-a.md        Die Warum-Schicht: Bauentscheide und Feld-Betriebs-
                        lehren (A.0–A.13). Bleibt im Kit, wird nicht installiert
doku/einrichtung.md     Klonen und Einbinden — Linux und Windows mit WSL,
                        IDE- und Werkzeug-Beispiele, Fehlerbilder, Belegstand
doku/regel-inventar.md  Jede Regel der Vorlage als NORM/HERLEITUNG/HISTORIE,
                        mit Träger und wörtlichem Zitat
doku/faq.md             Ganze Fragen mit ganzer Antwort — Installation der
                        Agenten-CLI, PATH-Fallen, was danach noch fehlt
```

**In der Wurzel liegt kein einziges Skript** — nur README, CHANGELOG, LICENSE
und die vier Ordner oben. Wer eine `.sh` sucht, schaut in `bash/`; wer eine
`.ps1` sucht, in `pwsh/`. Ein Namenspaar wie `ralph.sh` ↔ `ralph.ps1` liegt in
**gespiegelten** Pfaden (`bash/entry/` ↔ `pwsh/entry/`), und jede Datei nennt
ihr Gegenstück in Zeile 1 (`# Bahn: bash | Gegenstueck: ralph.ps1`, siehe
[A.13](doku/anhang-a.md)). Beides wird geprüft, nicht vereinbart —
[`geteilt/tests/test_bahn_kopfzeile.py`](geteilt/tests/test_bahn_kopfzeile.py).

**Das Zielprojekt sieht anders aus als das Kit.** Dort landen die Entrypoints
flach in der Wurzel und alles Aufgerufene unter `team/` — die Bahn-Ordner des
Kits werden beim Installieren aufgelöst:

| im Kit | im Zielprojekt |
|---|---|
| `bash/entry/ralph.sh`, `pwsh/entry/ralph.ps1` | `ralph.sh`, `ralph.ps1` (Wurzel) |
| `bash/lib.sh`, `pwsh/lib.psm1` | `team/lib.sh`, `team/lib.psm1` |
| `geteilt/tools/`, `geteilt/prompts/`, `geteilt/tests/` | `team/tools/`, `team/prompts/`, `team/tests/` |

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

| Bash-Bahn (Linux · WSL) | pwsh-Bahn (Windows ohne WSL) | Wirkung |
|---|---|---|
| `./vollautomatik.sh` | `.\vollautomatik.cmd` | Ganze Kaskade automatisch durchfahren |
| `./halbautomatik.sh <rolle>` | `.\halbautomatik.cmd <rolle>` | Einzelnen Schritt, Entscheidung beim Menschen |
| `./team-status.sh` | `.\team-status.cmd` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --budget` | `.\team-status.cmd --budget` | Kontostand, API vs. Abo getrennt |
| `./team-status.sh --ledger-pruefen` | `.\team-status.cmd --ledger-pruefen` | Ist für jede Kaskade alles gebucht? Gegenprobe gegen die archivierten Rohlogs (Exit `4` = Warnbefunde) |
| `./team-status.sh --altlast [N]` | `.\team-status.cmd --altlast [N]` | Produktivdateien, die seit N Kaskaden in keinem Diff lagen — die Auswahlhilfe für einen Altlast-Sweep (`BL-40`) |
| `./team-test.sh` | `.\team-test.cmd` | Regressionstests der Team-Infrastruktur (pytest) |
| `bash <kit>/bash/install.sh . --update` | `pwsh -File <kit>\pwsh\install.ps1 . -Update` | Auf eine neue Kit-Version heben, ohne Projektdaten anzufassen |
| `python3 team/tools/beutebuch.py list` | *(gleich)* | Alle Funde mit Status |
| `python3 team/tools/zitat_lint.py` | *(gleich)* | Plandateien, die einen erledigten Backlog-Eintrag noch als offene Frage zitieren (`BL-50`) |

**Welche Spalte gilt, entscheidet die Shell, nicht das Betriebssystem.** Wer
unter Windows in einer WSL-Distro arbeitet, steht in der **linken** Spalte —
WSL ist Windows und fährt die Bash-Bahn. Die rechte Spalte gilt für Windows
**ohne** WSL.

Die `.cmd`-Dateien sind Einzeiler auf die gleichnamige `.ps1`. Die beiden
letzten Zeilen stehen bewusst als *(gleich)* da: Die Python-Werkzeuge werden
**nicht** portiert — Ledger, Beutebuch und Kostenrechnung liegen auf beiden
Wegen in denselben Dateien. Die pwsh-Bahn ist eine zweite
**Orchestrierung**, kein zweiter Zustandscode.

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
- **Modellagnostisch ja, CLI-agnostisch nein.** Die Rollen sprechen zwei Stufen
  an (`TEAM_MODEL_LOOP`/`TEAM_MODEL_STRONG`), keine Modellnamen — aber der
  einzige erprobte Weg zu einem Modell führt heute über `claude -p`. Daran
  hängen das Ergebnis-JSON, der Auth-Fallback und die gesamte Kostenmechanik.
  Der Tausch findet in **einer** Funktion statt (`team_claude()` in
  `team/lib.sh`); belegt ist er nicht. Ebenso wenig belegt ist bisher ein Lauf
  mit einem lokalen Open-Weights-Modell — das ist Ziel, nicht Zustand.
- **Selbstverifikation**: `bash bash/kit-test.sh` installiert das Kit in ein
  Wegwerf-Repo und fährt dort die 487 Tests — **zweimal**: einmal mit den
  Auslieferungswerten, einmal mit angepasster `team.config.sh` (Caps,
  Commit-Präfixe, zwei Domänen). Der zweite Lauf ist die Lehre aus `BL-58`: In
  einer frischen Installation stehen dieselben Werte wie in `team/lib.sh`, ein
  Test, der die Zusicherung am *aufgelösten* Wert misst statt an der
  Bibliothek, ist dort immer grün — und wird erst im Feldprojekt rot.
  `pytest team/tests` **im Kit-Repo** schlägt dagegen erwartungsgemäß fehl —
  die Tests setzen die installierte Ablage voraus (Entrypoints in der Wurzel
  statt unter `bash/entry/` bzw. `pwsh/entry/`).
- **Regeln ändern heißt: Inventarzeile nachziehen.** Stufe 9 prüft jede
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
**auch für die 121 Dateien, die der Installer im Zielprojekt hinterlässt** — sie
lösen keine Lizenzpflicht für den Code des Zielprojekts aus. Der Code stammt aus
einem eigenen Projekt des Autors; das Urheberrecht liegt vollständig bei ihm.

Das gilt auch für den Banner: `team-banner.webp` ist aus der mitgelieferten
Quelle `team-banner.svg` gerendert und enthält kein fremdes Material.

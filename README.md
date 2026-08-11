# T.E.A.M.-Starterkit

Ein vollständiges KI-Rollenteam auf Knopfdruck in ein Software-Projekt —
frisch angelegt **oder seit Jahren gewachsen**.

```bash
cd ~/Source/team-kit
bash install.sh ~/Source/mein-projekt
```

*(Kurzform von überall: `bash ~/.claude/scripts/team-init.sh <zielpfad>`)*

Ein Befehl, ein kurzes Aufnahme-Interview, danach liegen 73 Dateien im
Zielprojekt: der gehärtete Bau-Loop, das Read-Only Red Team, der Fixer, der
Forensiker, die Kostenmechanik, die Bootstrap-Dateien, die Bedienanleitung
`TEAM.md` und 267 Regressionstests.

**Stand: Version 2.5.0** (2026-08-11). Für ein Bestandsprojekt gibt es zwei
Einstellungen, die anders gesetzt werden müssen als im Default — siehe
[In ein bestehendes Projekt](#in-ein-bestehendes-projekt).

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
diesem Betrieb kommen die Backlog-Einträge `BL-1`…`BL-50`; was davon behoben ist,
steht im [CHANGELOG](CHANGELOG.md), der Rest in [plans/backlog.md](plans/backlog.md).

Die konzeptionelle Grundlage steht im [LLM-Wiki](../llm-wiki/wiki/vorlagen/claude-md-ki-team.md).

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

| Frage | Default | Bedeutung |
|---|---|---|
| Projektname | Ordnername | erscheint in Berichten und Ledger |
| Produktivcode-Ordner | `src/` | **tabu** für Harry, Marv, Axel — und zugleich der **Prüfumfang** des Sweeps (`BL-52`) |
| Test-Ordner | `tests/` | wo Reproducer hindürfen (bleibt **deinem** Testrunner) |
| Plan-Ordner | `plans/` | Kaskaden, Beutebuch, Akten, Roadmap — **Schreibzone** der Read-Only-Rollen (`BL-51`) |
| Smoke-Test-Befehl | *(leer)* | **der wichtigste Wert**, siehe unten |
| Tech-Stack | *TODO-Zeile* | eine Zeile für `CLAUDE.md`, reine Doku |
| Domänen | `produkt` | Arbeitsstränge **dieses** Projekts; eine reicht (`BL-9`) |
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

## In ein bestehendes Projekt

**Das T.E.A.M. kann sich in eine gewachsene Codebasis einarbeiten** — es braucht
kein leeres Repo. Die Rollen lesen den Bestand, der Architekt plant gegen ihn,
und das Kit legt sich **neben** deinen Code: eigene Entrypoints, ein `team/`-
Namensraum, `TEAM.md`. Deine Ordner werden nicht angefasst, dein Testrunner
bleibt deiner, der Smoke-Test ist im Bestandsprojekt meist schon vorhanden —
genau das Feld, das im leeren Projekt zuerst fehlt.

> **Belegstand.** Nachgewiesen ist bisher die **Analyse**, nicht der scharfe
> Lauf: Am fremden Bestandsprojekt `Project-Family-ERP` (Python/tkinter,
> Einstiegspunkt in der Wurzel, `src/`, `bin/`, gewachsene `tests/`, belegtes
> `plans/`) hat eine Architekten-Sitzung 2026-08-11 **nur gelesen, nicht
> installiert** und dabei die beiden Stellen gefunden, an denen die Defaults
> nur für ein Neuprojekt taugen (`BL-51`, `BL-52`). Beide sind **offen**; bis
> ein Bestandslauf sie im Feld bestätigt hat, sind sie hier von Hand zu
> umgehen.

**Zwei Werte anders setzen als im Default:**

| Falle | Warum sie nur im Bestand greift | Was du tust |
|---|---|---|
| **Plan-Ordner** (`BL-51`) | Die Guard-Whitelist ist **positiv**: Harry, Marv und Axel dürfen im Plan-Ordner schreiben und löschen. Zeigt er auf ein bereits belegtes `plans/` oder `docs/`, bekommen die drei ausdrücklich als Read-Only geführten Rollen stillschweigend Schreibrecht auf Bestandsdokumente — **der Guard schlägt dort nie an**. Der Installer prüft nicht, ob der Ordner leer ist. | Einen **eigenen, leeren** Ordner angeben, z. B. `team-plans/`. |
| **Prüfumfang** (`BL-52`) | Der Sweep-Auftrag zeigt auf `TEAM_PRODUKTIVCODE` — **einen einzelnen Ordner**. Im Bestand liegen Einstiegspunkt (`main.py`), Build- und Deploy-Skripte regelmäßig daneben und werden nie angegriffen. Ein Sweep, der `src/` sauber meldet, sieht dann aus wie ein sauberes Projekt. Das ist **keine** Guard-Lücke (außerhalb der Whitelist bleibt jede Änderung eine Verletzung), sondern eine Prüfumfangs-Lücke. | Den Code außerhalb im **Fokus-String** der Kaskade benennen, bis `TEAM_PRODUKTIVCODE` eine Leerliste akzeptiert. |

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
└── tests/              44 Testdateien, 267 Testfälle

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
| `./team-test.sh` | Regressionstests der Team-Infrastruktur (pytest) |
| `bash <kit>/install.sh . --update` | Auf eine neue Kit-Version heben, ohne Projektdaten anzufassen |
| `python3 team/tools/beutebuch.py list` | Alle Funde mit Status |

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
  Kit-Fehler zutage gefördert — `BL-1`…`BL-50`, von der toten Fixphase über
  zwei Löcher in der Kostenerfassung bis zur vierten Fehlerklasse „Stufe
  fertig, Quittung fehlt". Die Erwartung ist nicht, dass das aufhört; die
  Mechanik dafür ist der Rückkanal Feld → Kit.
- **Bestandsprojekte sind analysiert, nicht gefahren.** Siehe
  [In ein bestehendes Projekt](#in-ein-bestehendes-projekt): `BL-51` und
  `BL-52` sind offen, die Umgehung steht dort.
- **Noch nie gelaufen: Axel.** Der Forensiker hat in 33 Kaskaden keine einzige
  Ledgerzeile — sein Pfad ist getestet, aber nicht im Feld belegt.
- **Selbstverifikation**: `./kit-test.sh` installiert das Kit in ein
  Wegwerf-Repo und fährt dort die 267 Tests. `pytest team/tests` **im Kit-Repo**
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

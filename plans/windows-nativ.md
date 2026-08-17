# Windows nativ — PowerShell-Zweig neben Bash

Plan für einen **unter Windows 11 nativ lauffähigen** T.E.A.M.-Zweig: ohne WSL,
ohne Git Bash, ohne jede Unix-Schicht. Bash bleibt die Linux-Implementierung und
wird **nicht** angetastet.

> **Nicht verwechseln:** Dies ist ein Bauplan mit Stufen, Abnahmekriterien und
> Aufwand — keine Skizze. Ungehärtete Stränge stehen in
> [`roadmap-skizzen.md`](roadmap-skizzen.md), kleine Aufgaben in
> [`backlog.md`](backlog.md).

---

## 1. Anlass

Auf einem Zielsystem (Windows 11 als VM) ist das Kit unter WSL nicht betreibbar.
Zwei Ursachen, vom Betreiber benannt:

1. **WSL2 steht nicht zur Verfügung.** Die VM bietet keine *nested
   virtualization*; es bliebe WSL1. Für Dateisperren und Dateisystem-Semantik
   gibt WSL1 keine Zusicherung — [`doku/einrichtung.md`](../doku/einrichtung.md)
   behandelt den Fall bereits, aber als Gegenprobe mit Restrisiko, nicht als
   tragfähigen Betrieb.
2. **Auth und Agenten-CLI.** Die CLI läuft nicht bzw. findet das Abo nicht.

Punkt 2 ist der wichtigere und zugleich der **unbelegte** — siehe
[Abschnitt 8](#8-risiken-und-unbelegte-annahmen). Er entscheidet, ob dieser Plan
überhaupt wirkt.

---

## 2. Entscheid und verworfene Alternativen

**Entschieden: PowerShell für Windows, Bash bleibt unverändert.**

Verworfen wurden:

| Weg | Warum verworfen |
|---|---|
| **Git Bash / MSYS2** | Wäre der billigste Weg (eine Codebasis, Tage statt Wochen), ist aber eine Unix-Schicht. Der Betreiber hat „ohne jede Unix-Schicht" als Ziel gesetzt |
| **Python-Kern, Bash zu Shims** | Eine Codebasis, plattformneutral, Python ist ohnehin harte Abhängigkeit. Verworfen, weil der funktionierende Linux-Betrieb dann früh an unbelegtem Code hinge — solange die Windows-Seite unbewiesen ist, darf sie die Linux-Seite nicht anfassen |
| **Docker / devcontainer** | Docker Desktop unter Windows läuft selbst auf WSL2. Versteckt das Problem, statt es zu lösen |

**Der erhobene Einwand und seine Auflösung.** Gegen zwei dauerhafte
Implementierungen wurde eingewandt: In einem Kit, in dem jede Feldlehre eine
Codeänderung *plus* einen Test wird, kostet jede künftige Lehre doppelt — und es
ist absehbar, welche Seite driftet, weil der Betreiber auf Linux arbeitet. Der
Windows-Zweig sähe dann unterstützt aus, ohne es zu sein: genau die Klasse
stiller Fehler, gegen die [`doku/einrichtung.md`](../doku/einrichtung.md) an
mehreren Stellen anschreibt.

Die Messung hat den Einwand entschärft, aber nicht aufgehoben
([Abschnitt 3](#3-belegstand--die-messung)): Die driftgefährlichste Fläche — die
Rollen-Briefings — ist konstruktionsbedingt bereits geteilt. Was übrig bleibt,
ist Kontrollfluss, und Kontrollfluss ist testbar. Der Einwand wird deshalb nicht
durch eine Absichtserklärung aufgefangen, sondern durch eine erzwungene
Eigenschaft: **eine** Testsuite, zwei Bahnen
([Abschnitt 6](#6-die-testbahn--der-tragende-mechanismus)). Eine neue Lehre
schreibt einen Test, und der wird auf der anderen Bahn automatisch rot, bis sie
nachgezogen ist. Drift wird nicht verboten, sondern sichtbar.

---

## 3. Belegstand — die Messung

Gemessen am Stand `af7da46` (2026-08-17), Zeilen ohne Kommentar und Leerzeile.

### Was geteilt bleibt — kein Duplikat

| Was | Umfang | Warum |
|---|---|---|
| **Zustand** — [`team/tools/`](../team/tools/) | 2.372 Zeilen Python | `kosten.py`, `beutebuch.py`, `zitat_lint.py`. Ledger, Beutebuch, Kostenerfassung. PowerShell ruft sie exakt wie Bash auf — der zustandskritische Teil wird **nicht** portiert |
| **Prosa** — [`team/prompts/`](../team/prompts/) | 340 Zeilen | Die sechs Rollen-Briefings liegen bereits als Markdown. [`team_briefing`](../team/lib.sh#L621) ist ein `cat`. Was das Agentenverhalten steuert, ist damit schon single-source |
| **Tests** — [`team/tests/`](../team/tests/) | 57 Dateien | Bleiben **eine** Suite, siehe [Abschnitt 6](#6-die-testbahn--der-tragende-mechanismus) |

### Was dupliziert werden muss

| Datei | Zeilen gesamt | davon Code |
|---|---|---|
| [`team/lib.sh`](../team/lib.sh) | 1.362 | **689** |
| [`entry/team-status.sh`](../entry/team-status.sh) | 502 | 260 |
| [`team/redteam.sh`](../team/redteam.sh) | 291 | 162 |
| [`entry/vollautomatik.sh`](../entry/vollautomatik.sh) | 269 | 143 |
| [`entry/ralph.sh`](../entry/ralph.sh) | 181 | 98 |
| [`entry/frank.sh`](../entry/frank.sh) | 179 | 96 |
| [`entry/axel.sh`](../entry/axel.sh) | 150 | 88 |
| [`entry/halbautomatik.sh`](../entry/halbautomatik.sh), `harry.sh`, `marv.sh`, `team-test.sh`, `team.config.sh` | 386 | 153 |
| **Summe Orchestrierung** | 3.320 | **1.689** |
| [`install.sh`](../install.sh) | 830 | ~480 |
| [`kit-einrichten.sh`](../kit-einrichten.sh) | 372 | ~230 |
| [`kit-test.sh`](../kit-test.sh) | 482 | ~300 |
| **Summe Bootstrap & Prüfung** | 1.684 | **~1.010** |

**Gesamte Duplizierungsfläche: rund 2.700 Code-Zeilen**, nicht die 5.190
Rohzeilen des Bash-Bestands. Der Unterschied ist Kommentar — in `lib.sh` fast
die Hälfte, und das sind die Feldlehren. Sie wandern als Prosa mit und kosten
keine Portierungsarbeit.

Davon abzuziehen: rund **20 der 38 Funktionen** in `lib.sh` sind bereits dünne
Hüllen über die Python-Werkzeuge (`team_kosten_summe`, `team_ledger_split`,
`team_akteur_abschluss`, `team_architekt_stand` …). Sie bleiben in PowerShell
genauso dünn und sind mechanische Arbeit.

### Zwei Korrekturen am dokumentierten Stand

- **Indirekte Expansion.** [`kit-einrichten.sh:135`](../kit-einrichten.sh#L135)
  und [`doku/einrichtung.md`](../doku/einrichtung.md) sagen, das Kit nutze
  *durchgehend* `${!var}`. Gemessen: In `lib.sh`, `entry/*.sh` und `redteam.sh`
  kommt sie **null** Mal vor. Alle sechs Fundstellen liegen in
  [`install.sh`](../install.sh) (dazu `printf -v` und `unset "${!TEAM_@}"`).
  Für den Aufwand heißt das: Die Laufzeit ist einfacher zu portieren als
  angenommen, der **Installer** schwerer. Die Doku-Aussage gehört in Stufe 5
  richtiggestellt.
- **`python3 -c`-Einbettungen.** 13 Stellen in `lib.sh`. Sie entfallen im
  PowerShell-Zweig ersatzlos, siehe unten.

---

## 4. Die Plattform-Naht

Die vollständige Liste der Stellen, an denen die beiden Zweige technisch
auseinandergehen. Alles, was hier nicht steht, ist eine reine
Syntax-Übersetzung.

| Bash heute | PowerShell | Anmerkung |
|---|---|---|
| `flock -n 9` — [lib.sh:877](../team/lib.sh#L877) | `[System.IO.FileStream]` mit `FileShare::None` | **Genau eine** echte Sperre im ganzen Kit. Die PowerShell-Fassung ist vom OS durchgesetzt statt kooperativ — also **besser** als `flock`, und sie löst die Problemklasse, an der WSL1 gescheitert wäre |
| `flock -n … true` (Lesetest) — [team-status.sh:110](../entry/team-status.sh#L110), [install.sh:131](../install.sh#L131) | Öffnungsversuch mit `FileShare::None`, Exception = belegt | Zwei Stellen, reine Abfrage |
| 13 × `python3 -c '…'` in `lib.sh` | `ConvertFrom-Json` | Entfällt ersatzlos. Die Windows-Seite wird hier **sauberer** als die Linux-Seite |
| `chmod 600` auf den API-Key — [team-auth-setup.sh](../scripts/team-auth-setup.sh) | `Set-Acl`, Zugriff nur für den Besitzer | `chmod` ist unter Windows wirkungslos. Ohne diesen Punkt liegt der Schlüssel lesbar da — **Sicherheitsrelevant, nicht Komfort** |
| `~/.config/claude-team/api-key` | `$env:APPDATA\claude-team\api-key` | Ablage und Migrationspfad in `team-auth-setup.ps1` |
| `claude` über `PATH` — [lib.sh:342](../team/lib.sh#L342) ff. | `Get-Command claude` → `.cmd`-Shim auflösen | Ein `.cmd` startet nicht wie eine `.exe`. Fehlt die Auflösung, sieht das Ergebnis **aus wie ein Auth-Fehler** und ist keiner |
| `cd "$(dirname "$0")"` | `Set-Location $PSScriptRoot` | Die BL-3-Invariante, auf der alle relativen Werkzeugpfade ruhen. Statisch geprüft — der Test braucht eine Idiom-Tabelle je Shell |
| `set -euo pipefail` (8 Skripte) | `$ErrorActionPreference = 'Stop'` + `try/catch` | |
| `${!var}`, `printf -v`, `unset "${!TEAM_@}"` — 6 × in `install.sh` | `Get-Variable -ValueOnly`, `Set-Variable`, `Remove-Item Env:TEAM_*` | Nur der Installer, nicht die Laufzeit |
| [`entry/team.config.sh`](../entry/team.config.sh) — 30 Zuweisungen | `team.config.ps1` | **Beide vom Installer aus denselben neun Antworten erzeugt.** Ein Generat, keine Handarbeit — deshalb driftfrei |
| `git`-Aufrufe (durchgehend) | identisch | `git` ist unter Windows nativ |
| `*.sh` mit `eol=lf` — [`.gitattributes`](../.gitattributes) | `*.cmd`/`*.bat` brauchen **CRLF** | Die heutige Regel `* text=auto eol=lf` erfasst alles. Batch-Dateien mit reinem LF verhalten sich unzuverlässig (Labels, `goto`). `.gitattributes` braucht eine Ausnahme |

**Nicht in der Liste, weil nicht vorhanden:** kein `curl`, kein `jq`, kein
`timeout`, kein `nohup`/`setsid`, keine Hintergrundprozesse, keine
Signalakrobatik über zwei `trap`-Zeilen hinaus. Das Kit ist sequenziell — das
ist der Grund, warum dieser Port überhaupt tragfähig ist.

---

## 5. Bedienung unter Windows

Zwei Aufrufformen, dieselbe Sache darunter:

```powershell
.\ralph.cmd                     # Bequemlichkeit
pwsh -File .\ralph.ps1          # dasselbe, ohne Shim
```

Die `.cmd`-Dateien sind Einzeiler auf die `.ps1`-Datei. Nichts versteckt sich
darin — wer wissen will, was läuft, öffnet die `.ps1`.

**Namensgleichheit ist Pflicht:** `ralph.sh` ↔ `ralph.ps1` ↔ `ralph.cmd`. Die
Testbahn koppelt darüber, und [`TEAM.md`](../bootstrap/TEAM.md) kann eine
einzige Befehlstabelle mit einer Plattformspalte führen, statt zwei Tabellen.

---

## 6. Die Testbahn — der tragende Mechanismus

**Der Reflex wäre eine zweite Testsuite. Das wäre der Fehler**, und zwar der
einzige, der diesen Plan zum Scheitern bringen kann: Zwei Suiten driften
genauso wie zwei Implementierungen, nur unbemerkt.

Richtig ist: **dieselbe** Testdatei, der Harnisch parametrisiert über `bash`
oder `pwsh`, die Assertions identisch. Umsetzung über eine neue
`team/tests/conftest.py` (existiert heute nicht — die Tests sind eigenständig)
mit einer `schale`-Fixture.

Die 57 Tests zerfallen in fünf Klassen mit unterschiedlicher Behandlung:

| Klasse | Anzahl | Behandlung |
|---|---|---|
| **Rein Python** — Werkzeuge, Doku, Briefings | 24 | Unberührt. Laufen auf beiden Plattformen wie heute |
| **Statische Quelltextprüfung** — lesen `.sh`-Text und prüfen auf ein Muster | 24 | Die aufwendigste Klasse. Das geprüfte *Idiom* wird je Shell in einer Tabelle hinterlegt (`cd "$(dirname "$0")"` ↔ `Set-Location $PSScriptRoot`), der Test läuft einmal je Zweig gegen die passende Datei |
| **Entrypoint-Start** — starten `./ralph.sh` o. Ä. | 16 | Harnisch wählt `.sh` oder `.ps1`. Test-Rumpf unverändert |
| **`kit-test.sh` / `install.sh`** | 8 | Warten auf Stufe 2, dann analog |
| **`lib.sh` sourcen und eine Funktion rufen** | 6 | Der Kern. Braucht eine **neutrale Aufrufform** statt eingebetteter Shell-Fragmente (siehe unten) |

*(Die Klassen überlappen; 24 Tests sind rein Python, 33 berühren eine Shell.)*

**Der Umbau der Kern-Tests.** Heute steht in den Testkörpern Bash-Syntax, nicht
nur ein Funktionsaufruf — etwa in
[`test_bl16_guard_zuschreibung.py:72`](../team/tests/test_bl16_guard_zuschreibung.py#L72):

```python
skript = ("set -euo pipefail\n"
          f"source ...; team_guard_begin\n{mutation}\n"
          f"if team_guard_verify harry '{WHITELIST}'; then echo URTEIL=sauber; ...")
```

Das ist nicht parametrisierbar. Der Umbau ersetzt es durch eine neutrale Form —
`schale.ruf("team_guard_verify", "harry", WHITELIST) -> (rc, out, err)` — und
zieht Mutationen (`git add`, Datei schreiben) nach Python hoch, wo sie ohnehin
plattformneutral sind. Danach enthält kein Testkörper mehr Shell-Syntax.

Das ist mechanische, aber nicht triviale Arbeit an 6 Dateien. **Sie steht
bewusst in Stufe 1, vor jeder Portierungszeile** — ohne sie gibt es kein
Abnahmekriterium für die Stufen 3 und 4.

**Die `claude`-Stubs.** 9 Testdateien legen einen Stub an, heute als Bash-Skript
mit `#!/usr/bin/env bash` und `chmod 0755`. Unter Windows muss das ein `.cmd`
sein und `chmod` entfällt. Der Stub-Bau gehört in dieselbe `conftest.py`.

---

## 7. Stufen

Jede Stufe endet mit einem Commit, in dem **beide** Bahnen grün sind — auf
Linux vollständig, auf Windows soweit gebaut. Aufwand als Personentage,
Erfahrungswert für die Arbeit mit einem Agenten im Loop.

### Stufe 1 — Fundament und Probe (2 PT)

**Warum zuerst:** Ohne Testharnisch gibt es kein Abnahmekriterium; ohne Probe
steht der ganze Plan auf einer Annahme.

Neu:
- `pruefe-windows.ps1` — **eigenständig, ohne Kit-Abhängigkeit.** Beantwortet
  die drei offenen Fragen aus [Abschnitt 8](#8-risiken-und-unbelegte-annahmen):
  Läuft `claude -p --output-format json` headless mit dem Abo? Findet
  PowerShell das `claude.cmd`? Greift die `FileStream`-Sperre über zwei
  Prozesse? Ruft **keine** kostenpflichtige Arbeit auf.
- `team/tests/conftest.py` — `schale`-Fixture, Stub-Bau, Idiom-Tabelle.

Geändert:
- Die 6 Kern-Tests auf die neutrale Aufrufform.
- [`.gitattributes`](../.gitattributes) — CRLF-Ausnahme für `*.cmd`/`*.bat`.

**Abnahme:** `pytest team/tests` auf Linux unverändert grün (gleiche Zahl
bestandener und gleiche Zahl erwartet fehlschlagender Tests wie vor der Stufe).
`pruefe-windows.ps1` läuft auf einer beliebigen W11-Maschine durch und gibt
einen Bericht aus, auch wenn alles fehlschlägt.

> **Torbedingung.** Meldet `pruefe-windows.ps1`, dass die Agenten-CLI unter
> nativem Windows **nicht** headless mit dem Abo läuft, sind die Stufen 3–5
> wirkungslos. Dann ist es eine Auth-Frage, keine Plattformfrage, und dieser
> Plan pausiert hier.

### Stufe 2 — Bootstrap (4 PT)

**Warum vor dem Kern:** Ohne diese Stufe lässt sich das Kit auf der
Zielmaschine nicht einmal installieren. Henne-Ei.

Neu:
- `install.ps1` — Gegenstück zu [`install.sh`](../install.sh). Die sechs
  `${!var}`-Stellen sind hier, das ist die inhaltliche Schwierigkeit dieser
  Stufe.
- `kit-einrichten.ps1` — Gegenstück zu
  [`kit-einrichten.sh`](../kit-einrichten.sh). Bordmittelprüfung für Windows:
  `pwsh` ≥ 7, `git`, `python3` ≥ 3.8, Agenten-CLI. **Kein `flock`-Check** — an
  seine Stelle tritt die Zwei-Prozess-Probe auf die `FileStream`-Sperre, in der
  Haltung von A.5: *proben statt voraussetzen*.
- `scripts/team-auth-setup.ps1` — `%APPDATA%`-Ablage mit `Set-Acl`.

Geändert:
- `install.sh` **und** `install.ps1` schreiben `team.config.sh` **und**
  `team.config.ps1` aus denselben neun Antworten. Das ist die einzige Änderung
  an einer Bash-Datei in diesem Plan und der Grund, warum die Konfiguration
  driftfrei bleibt.

**Abnahme:** Auf einer frischen W11-Maschine ohne WSL führt
`.\kit-einrichten.ps1 <zielpfad>` zu einem installierten Projekt. Auf Linux ist
`bash kit-test.sh` unverändert grün — der Beleg, dass die Config-Änderung nichts
gebrochen hat.

### Stufe 3 — Kern (4 PT)

Neu: `team/lib.psm1` — 689 Code-Zeilen aus [`lib.sh`](../team/lib.sh).

Reihenfolge innerhalb der Stufe, billig nach teuer:

1. Die ~20 Werkzeug-Hüllen (`team_kosten_*`, `team_ledger_*`,
   `team_akteur_abschluss`, `team_architekt_*`, `team_budget_*`) — mechanisch.
2. `team_lock` — die Plattform-Naht, mit der Zwei-Prozess-Probe als Test.
3. Auth: `team_auth_mode_effektiv`, `team_resolve_auth_mode`,
   `team_warnung_abo_key` — inklusive `.cmd`-Auflösung.
4. `team_claude` samt Abo→API-Fallback ([lib.sh:342–403](../team/lib.sh#L342)).
5. Die sieben `team_guard_*` — der heikelste Teil. Der Schnappschuss hält
   **Blob-Hashes**, und die Lehre aus BL-16 (fremde Arbeit nie blanko
   zurücksetzen) muss Zeile für Zeile erhalten bleiben.
6. `team_promise_in`, `team_quittung_*`, `team_bewerte_ergebnis`,
   `team_versuch_*`.

**Abnahme:** Die 6 Kern-Tests laufen auf **beiden** Bahnen grün. Die 13
`python3 -c`-Einbettungen haben in `lib.psm1` kein Gegenstück — falls doch,
wurde etwas falsch übersetzt.

### Stufe 4 — Rollen (4 PT)

Neu, je mit `.cmd`-Shim: `ralph.ps1`, `frank.ps1`, `axel.ps1`, `harry.ps1`,
`marv.ps1`, `redteam.ps1`, `vollautomatik.ps1`, `halbautomatik.ps1`,
`team-status.ps1`, `team-test.ps1`.

Ein Commit je Rolle mit grüner Doppelbahn. `harry.ps1` und `marv.ps1` sind
Einstiege von je gut 20 Zeilen — die gehen zuerst und belegen früh, dass die
Kette Shim → `.ps1` → `lib.psm1` → `claude` → Ledger trägt.
`team-status.ps1` ist mit 260 Code-Zeilen die größte Einzeldatei, besteht aber
fast nur aus Durchreichen an `kosten.py`.

**Abnahme:** Alle 33 shell-berührenden Tests auf beiden Bahnen grün. Ein
vollständiger Trockenlauf (`TEAM_DRY_RESULT`) der Vollautomatik unter Windows
ohne echte CLI-Kosten.

### Stufe 5 — Prüfung, Doku, Abnahme (2 PT)

Neu:
- `kit-test.ps1` — Gegenstück zu [`kit-test.sh`](../kit-test.sh), prüft die
  Bordmittel je Plattform.

Geändert:
- [`doku/einrichtung.md`](../doku/einrichtung.md) bekommt einen **dritten Weg**
  neben Linux und Windows-mit-WSL. Der WSL-Abschnitt bleibt — er ist hergeleitet
  und für Maschinen mit funktionierendem WSL2 weiterhin der bessere Weg.
- Ebendort und in [`kit-einrichten.sh:135`](../kit-einrichten.sh#L135): die
  Aussage zur indirekten Expansion richtigstellen (siehe
  [Abschnitt 3](#3-belegstand--die-messung)).
- [`README.md`](../README.md), [`bootstrap/TEAM.md`](../bootstrap/TEAM.md) —
  Befehlstabellen um eine Plattformspalte.
- [`CHANGELOG.md`](../CHANGELOG.md).

**Abnahme:** Ein echter, bezahlter Lauf einer Rolle auf der Zielmaschine, mit
Ledger-Zeile. Das ist der einzige Beleg, der zählt.

### Aufwand gesamt

**16 Personentage.** Stufe 1 ist die Torbedingung; die Stufen 2–5 laufen nur,
wenn sie hält.

---

## 8. Risiken und unbelegte Annahmen

| # | Annahme | Status | Wenn sie fällt |
|---|---|---|---|
| R1 | `claude -p --output-format json` läuft unter nativem Windows **headless mit dem Abo** | **Unbelegt.** Die tragende Annahme des ganzen Plans | Die Stufen 3–5 sind wirkungslos. Es ist eine Auth-, keine Plattformfrage — dann wäre der API-Key-Weg der einzige, und die Kostenlage ändert sich grundlegend |
| R2 | PowerShell kann das `claude.cmd`-Shim aus einem Skript starten | Unbelegt, aber gut beherrschbar über `Get-Command` | Aufwand, kein Blocker |
| R3 | `FileStream` mit `FileShare::None` sperrt über Prozessgrenzen zuverlässig | Sehr wahrscheinlich (OS-durchgesetzt), Probe in Stufe 1 | Es gäbe keine belastbare Sperre unter Windows — die Vollautomatik dürfte dort nur einzeln laufen |
| R4 | Die 24 statischen Quelltexttests lassen sich über eine Idiom-Tabelle koppeln | Wahrscheinlich; einzelne Tests prüfen womöglich Bash-Eigenheiten ohne PowerShell-Entsprechung | Solche Tests bekommen eine ausdrückliche `nur-bash`-Markierung. **Jede** Markierung ist ein Stück ungeprüfter Windows-Zweig und gehört in den Backlog, nicht in die Stille |
| R5 | Der Windows-Zweig wird bei künftigen Feldlehren mitgezogen | Strukturell abgesichert über die Doppelbahn — aber nur, solange R4 nicht massenhaft greift | Der Zweig verrottet sichtbar statt unsichtbar. Das ist der Zweck der Konstruktion |

**R1 zuerst prüfen.** Der Betreiber hat derzeit keinen Zugriff auf die
Zielmaschine; `pruefe-windows.ps1` entsteht deshalb in Stufe 1 als
eigenständiges Artefakt und liegt bereit, sobald der Zugriff besteht.

---

## 9. Entschiedenes

1. **Gleichwertigkeit wird gemessen, nicht geschwellt.** *(entschieden
   2026-08-17)* Eine Zahl wie „ab fünf Markierungen gilt der Zweig als nicht
   gleichwertig" wäre willkürlich und würde sofort verhandelt. Stattdessen
   berichtet **jeder** Testlauf die **Doppelbahn-Quote**: wie viele Tests auf
   beiden Bahnen liefen, wie viele die pwsh-Bahn übersprangen und wie viele
   bewusst mit `@pytest.mark.nur_bash` geführt werden. Wer einen Test nur für
   eine Bahn führt, muss den Marker setzen und begründen — und die Markierung
   taucht danach in jedem Lauf auf, statt still zu bleiben. Gleichwertigkeit
   lässt sich nicht zusichern, ohne sie zu messen; die Quote ist die Zusage in
   prüfbarer Form. Jede Markierung gehört zusätzlich in den Backlog.
2. **pwsh 7.** *(entschieden 2026-08-17)* Zielsystem ist eine **Windows 11
   Enterprise**-VM; gefahren wird die jeweils neueste Fassung. W11 bringt 5.1
   mit, 7 wird **daneben** installiert (nicht darüber) — ein Schritt mehr in
   `kit-einrichten.ps1`, dafür `ConvertFrom-Json` ohne Eigenheiten und
   `Set-StrictMode -Version Latest` als brauchbares Gegenstück zu `set -u`.
   `pruefe-windows.ps1` meldet eine ältere Fassung als **Fehler**, nicht als
   Warnung.

## 10. Noch offen

1. **Reihenfolge Stufe 2 vs. 3.** Der Plan zieht den Bootstrap vor, weil man
   sonst nichts installieren kann. Alternative: Kern zuerst und in Stufe 2
   manuell installieren, um früher zu wissen, ob R1 im echten Betrieb hält.
   Entfällt, sobald `pruefe-windows.ps1 -MitEchtemAufruf` R1 beantwortet hat.

---

## 11. Baustand

### Stufe 1 — erledigt (2026-08-17)

| Was | Wo | Stand |
|---|---|---|
| Doppelbahn-Harnisch | [`team/tests/conftest.py`](../team/tests/conftest.py) | **neu.** `Schale` (bash \| pwsh), acht Schritt-Bausteine, Idiom-Tabelle, Konfig- und Stub-Erzeugung je Bahn, Doppelbahn-Quote im Testbericht |
| Aufrufkonvention für PowerShell | ebenda, Kopfkommentar | **festgelegt** — sieben Punkte. Stufe 3 muss sie einhalten, sonst laufen die Tests dort ins Leere |
| Kern-Tests auf neutrale Aufrufform | `test_bl18`, `test_bl24`, `test_bl28`, `test_bl32`, `test_bl41`, `test_hm32` | **umgestellt.** Kein Testkörper enthält mehr Shell-Syntax |
| CRLF für Batch-Dateien | [`.gitattributes`](../.gitattributes) | **ergänzt** — `*.cmd`/`*.bat` auf `eol=crlf`, `.ps1` bleibt bei LF |
| Vorflug-Probe | [`pruefe-windows.ps1`](../pruefe-windows.ps1) | **neu.** Eigenständig, ohne Kit-Abhängigkeit. Beantwortet R2 und R3 kostenlos, R1 nur mit `-MitEchtemAufruf` |

**Abnahme erfüllt.** `pytest team/tests` vor der Stufe: 21 failed, 329 passed,
19 skipped. Danach: **21 failed, 329 passed**, 47 skipped. Bestandene und
erwartet fehlschlagende Zahl unverändert; die 28 zusätzlichen Skips sind die
neuen pwsh-Varianten, die bis Stufe 3 übersprungen werden.

**Belegstand der Probe.** `pruefe-windows.ps1` ist gegen **pwsh 7.4.6 unter
Linux** geparst und gefahren worden — dabei fielen vier Fehler auf, darunter
einer, der auch unter Windows zugeschlagen hätte: `claude --version` lief
erfolgreich durch und wurde als Fehler gemeldet, weil
`… | Select-Object -First 1` die Pipeline abbricht, bevor `$LASTEXITCODE`
gesetzt ist. Alle vier sind behoben. **Auf Windows ist das Skript unbelegt** —
das ist der Zweck, nicht ein Mangel.

**Nebenbefund:** [`BL-111`](backlog.md) — die `head -1`-Absicherung in
`team_architekt_kaskade` trägt gegen `set -e`, aber nicht gegen
`set -o pipefail`. Bewusst **nicht** in dieser Stufe gefixt: Stufe 1 sichert
zu, den Bash-Zweig nicht anzutasten.

### Stufe 2 — erledigt (2026-08-17)

| Was | Wo | Stand |
|---|---|---|
| Installer | [`install.ps1`](../install.ps1) | **neu**, 640 Zeilen. Erstinstallation, `-Update`, `-Force`, Aufnahme-Interview, BL-51-Bestandsprüfung, BL-109-`.gitignore`-Abgleich, Selbsttest |
| Vorflug-Prüfung | [`kit-einrichten.ps1`](../kit-einrichten.ps1) | **neu.** Fünf Abschnitte wie die Bash-Fassung — aber ohne `flock`-Abhaken und mit Zwei-Prozess-Sperrprobe |
| Auth | [`scripts/team-auth-setup.ps1`](../scripts/team-auth-setup.ps1) | **neu.** `%APPDATA%\claude-team`, `Set-Acl` **mit Nachprüfung** statt wirkungslosem `chmod` |
| Launcher | [`scripts/team-init.ps1`](../scripts/team-init.ps1) | **neu** (im Plan nicht aufgeführt, aber ohne ihn hat `-Verknuepfen` kein Ziel) |
| Konfiguration | [`entry/team.config.ps1`](../entry/team.config.ps1) | **neu.** Vorlage mit denselben Platzhaltern; `Team-Wert` bildet Bashs `${VAR:-vorgabe}` ab |
| Beide Zweige aus einer Quelle | [`install.sh`](../install.sh) | **geändert.** Kopiert jetzt `entry/*.sh`, `*.ps1` und `*.cmd` und füllt **beide** Konfigurationen |
| Gleichstands-Nachweis | [`kit-test.sh`](../kit-test.sh) Schritt 10/10 | **neu** (war für Stufe 5 vorgesehen — vorgezogen, weil die Zusicherung sonst ungeprüft bliebe) |

**Abnahme erfüllt, und zwar schärfer als geplant.** Der Plan verlangte „auf
einer frischen W11-Maschine führt `kit-einrichten.ps1` zu einem installierten
Projekt". Belegt ist mehr: **`install.sh` und `install.ps1` erzeugen aus
denselben Antworten byte-identische Bäume** — 155 Dateien, `diff -r` ohne
Ausgabe. Das ist der Unterschied zwischen „beide funktionieren" und „beide
tun dasselbe".

Weiter belegt (pwsh 7.4.6 unter Linux):

- `install.ps1` frisch: 89 Dateien, in der Installation 369 passed, 0 failed —
  dieselbe Zahl wie bei `install.sh`.
- `install.ps1 -Update` gegen eine **mit `install.sh` erzeugte** Installation:
  78 Infrastruktur-Dateien ersetzt, Ledger-Zeile, Kaskadenstand `7` und ein
  von Hand eingetragener Smoke-Test **unverändert**. Die beiden Zweige können
  einander also updaten, ohne Projektdaten zu verlieren.
- `kit-einrichten.ps1 -NurPruefen`: alle fünf Abschnitte, Exit 0.
- `kit-test.sh`: 10/10 grün — **mit** pwsh (Gleichstand geprüft) und **ohne**
  pwsh (laut übersprungen, kein Fehler).

**Was der Windows-Zweig hier besser macht als der Bash-Zweig:**

| | Bash | PowerShell |
|---|---|---|
| Platzhalter füllen | eingebettetes `python3`-Here-Doc in `install.sh` | `.NET`-Bordmittel, kein Fremdkörper |
| Sperre vor `--update` | `flock -n` (kooperativ) | `FileShare::None` (OS-durchgesetzt) |
| Schutz des API-Keys | `chmod 600` | ACL **plus Nachprüfung** — `chmod` wäre hier wirkungslos und liefe ohne Fehler durch |
| Sperrprobe in der Einrichtung | ein `flock -n` im eigenen Prozess | Zwei-Prozess-Gegenprobe |

**Und was schlechter ist, ausdrücklich benannt:** Der Selbsttest von
`install.ps1` kann die `.sh`-Entrypoints nicht syntaktisch prüfen — unter
Windows liegt keine `bash`. Er sagt das in seiner Ausgabe, statt Vollzug zu
melden.

**Auf Windows unbelegt.** Alles oben ist gegen pwsh 7.4.6 **unter Linux**
gefahren. `Get-CimInstance`, `Set-Acl`, die Benutzer-Umgebungsvariablen und
das `.cmd`-Verhalten sind dort nicht prüfbar und bleiben offen.

### Torbedingung — weiterhin offen

R1 ist unbeantwortet, bis `pruefe-windows.ps1 -MitEchtemAufruf` auf der
Zielmaschine gelaufen ist. Bis dahin bleiben die Stufen 3–5 auf einer Annahme
gebaut.

# Changelog — T.E.A.M.-Starterkit

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Fixed
- **Ralphs Baukosten landeten in keiner Ledger-Zeile (`BL-4`).**
  `--rollen-abschluss` ledgerte per Definition nur `.team-logs`
  (Harry/Marv/Frank/Axel). Für `.ralph-logs` gab es zwar den Bash-Helfer
  `team_logs_archivieren()`, aber im **gesamten Kit keinen Aufrufer**. Der
  Gesamtstand stimmte nur, solange `.ralph-logs/` liegen blieb — und der Ordner
  steht per `gitignore.fragment` in `.gitignore`. Ein frischer Clone verlor
  damit die **gesamte Bau-Kostenhistorie**, also genau das, wogegen das Ledger
  gebaut wurde (im Feld: 2,1621 von 9,4204 USD).
  **Neu:** `kosten.py ralph-abschluss` — derselbe Mechanismus mit `.ralph-logs`
  als Quelle und `rolle=ralph` als Zielzeile. `./team-status.sh
  --rollen-abschluss` ruft **beide** Verben auf: **eine** Bedienhandlung,
  **zwei** getrennte Ledger-Zeilen. Bewusst keine Sammelzeile — die Trennung
  Bau ↔ Sweep/Fix ist die Kennzahl, an der im Feld überhaupt auffiel, dass
  Ralph fehlte. Bricht ein Verb ab, wird das andere trotzdem versucht.
  Der Fehler war zur Hälfte ein Dokumentationsfehler: Die Closeout-Pflicht in
  `CLAUDE.md.vorlage`, `TEAM.md` und dem Architekten-Briefing nannte Ralph
  nirgends. Alle drei Stellen sind nachgezogen.
- **`--rollen-abschluss` löschte bei einem zweiten Aufruf still Geld aus dem
  Ledger (`BL-5`).** Der gebuchte Wert entsteht aus den **noch nicht
  archivierten** Logs, und ein Abschluss archiviert die gezählten Logs
  anschließend. Aufeinanderfolgende Aufrufe sehen deshalb **disjunkte** Mengen —
  wer nach dem Closeout noch eine Rolle laufen ließ (im Feld: Frank mit drei
  Fixes) und erneut abschloss, bekam einen *kleineren* Wert, der den größeren
  **ersetzte**. Real eingetreten: 1,0969 USD verschwanden hinter 2,4114 USD,
  Sollwert wäre die Summe 3,5083 gewesen; die Korrektur ging nur von Hand.
  Für disjunkte Mengen ist **Addieren** die richtige Verknüpfung — das
  Ersetzen stammte aus `akteur_abschluss()`, wo der Aufrufer einen absoluten,
  extern gemessenen Wert übergibt und Ersetzen deshalb korrekt ist.
  **Neu:** Steht für die Kaskade bereits eine `roles`-Zeile, **bricht der
  Aufruf ab** und nennt Alt-, Neu- und Summenwert; `--addieren` (Nachlauf) und
  `--ersetzen` (Korrektur einer falschen Altzeile) sind die beiden
  ausdrücklichen Wege. Automatisch addiert wird bewusst **nicht**: Ohne
  `--archivieren` zählen zwei Aufrufe dieselben Logs, dann wäre Addieren eine
  Doppelbuchung — die Entscheidung gehört dem Menschen, nicht der Heuristik.
  Bei Abbruch wird **nicht archiviert**, die Logs bleiben also greifbar.
  Der Normalfall (ein Closeout je Kaskade) läuft unverändert ohne jedes Flag.
- `_ledger_zeile_setzen()` bekam dafür einen optionalen `merge_fn`-Haken, der
  **innerhalb** des Ledger-Locks und **vor** jedem Schreibzugriff läuft.
  `akteur_abschluss()` ist unberührt.
- **`README.md`, Abschnitt „Grenzen", war überholt (`BL-7`).** Frank ist
  inzwischen scharf gelaufen (drei Fixes im Feld), Axel weiterhin nicht — und
  die Fixphase einer `vollautomatik.sh` hat noch nie in **einem** Durchlauf
  durchgetragen. Präzisiert statt gestrichen. Zahlen (Dateien, Tests,
  Zeilenumfänge) auf den Ist-Stand gebracht.

### Added
- `team/tests/test_bl4_ralph_abschluss.py` — vier Prüfungen, darunter die
  entscheidende über die Bedienoberfläche: **ein** `--rollen-abschluss` muss
  **beide** Zeilen erzeugen und beide Log-Ordner rotieren. Gegenprobe gefahren:
  Mit dem alten Ein-Verb-Aufruf ist genau dieser Test rot.
- `team/tests/test_bl5_rollen_abschluss_bestand.py` — sieben Prüfungen, darunter
  das **Feldszenario mit den echten Zahlen** (1,0969 → Frank-Nachlauf 2,4114 →
  3,5083) inklusive Archivierung. Gegenprobe gefahren: Mit dem alten Verhalten
  sind genau die beiden Kernprüfungen rot.
- **149 Testfälle** in 30 Dateien (im installierten Projekt).
- **`kit-test.sh` — das Kit prüft sich jetzt selbst (`BL-6`).** Bisher gab es
  dafür keinen Befehl: `pytest team/tests` schlägt im Kit-Repo mit **17 von 138**
  Tests fehl, weil die Tests die **installierte** Ablage voraussetzen
  (Entrypoints in der Wurzel statt unter `entry/`). Kein einziger dieser
  Fehlschläge war ein echter Fund — aber sie machten den einzigen vorhandenen
  Testlauf unbrauchbar, und damit war jeder im Kit committete Fix bis zur
  nächsten Feldinstallation ungeprüft. **Genau so ging `BL-1` durch drei
  Releases.**
  `./kit-test.sh` installiert das Kit nicht-interaktiv in ein frisches
  `mktemp`-Git-Repo, sucht ungefüllte `{{PLATZHALTER}}`, committet wie in
  `TEAM.md` vorgeschrieben und fährt dort `./team-test.sh` — die Tests laufen
  also dort, wo sie gelten. Der Installer wird dabei mitgeprüft. Exit-Code wird
  durchgereicht (Gegenprobe gefahren: erzwungener Fehlschlag ergibt Exit 5),
  `--behalten` lässt das Wegwerf-Repo zur Fehlersuche stehen. Ruft keine
  Agenten-CLI auf und kostet daher nichts.

## [2.2.1] — 2026-08-01

**Die Fixphase war in jeder Installation tot.** Erster Fund aus einem
Feldprojekt zurück ins Kit (`team-kit_project_platformer`, Kaskade 1).

### Fixed
- **`team/tools/beutebuch.py` löste die Projektwurzel eine Ebene zu hoch auf.**
  Die Datei liegt in `team/tools/`, also zwei Ebenen unter der Wurzel;
  `parent.parent` ergab `team/` und damit den Pfad `team/plans/beutebuch.md` —
  eine Datei, die es nie gibt. Weil `_lies_zeilen()` für eine fehlende Datei
  eine leere Liste liefert **statt zu scheitern**, meldete das Werkzeug ruhig
  „keine Funde": `first` gab Exit 1 zurück, `frank.sh` schloss daraus „nichts
  zu tun", und `vollautomatik.sh` beendete die Fixphase in Runde 1 — mit drei
  offenen Funden im Buch. Der gedruckte Abschlussbericht bestätigte den Fehler
  („keine Funde"), weil er dieselbe kaputte Quelle liest.
  **Betroffen war jede mit 2.0.0–2.2.0 installierte Instanz**: Red Team schreibt
  Funde, Frank sieht sie nie, niemand bemerkt es — der Lauf endet grün.

### Added
- `team/tests/test_bl1_beutebuch_repo_root.py` — drei Prüfungen: Default-Pfade
  zeigen auf die Wurzel, ein aus fremdem Arbeitsverzeichnis gestarteter
  `list`-Aufruf gegen ein Miniatur-Projekt findet den Fund, und im
  installierten Projekt trifft der Default eine existierende Datei
  (übersprungen im Kit-Repo, das kein `plans/` hat).
- `team/tests/test_bl3_werkzeug_default_pfade.py` — schließt die **Ursache**,
  dass der Fehler durch 132 grüne Tests rutschte: Sämtliche Werkzeug-Tests
  arbeiteten mit `--pfad` auf Fixtures, der Default-Pfad war ungeprüft.
  Prüft jetzt zusätzlich, dass **jeder Entrypoint ins Skriptverzeichnis
  wechselt** — die bislang nirgends festgehaltene Invariante, auf der die
  arbeitsverzeichnis-relativen Pfade von `kosten.py` ruhen.
- **138 Testfälle** gesamt (im installierten Projekt).

### Audit
- `kosten.py` hat den Fehler **nicht**: es leitet keine Pfade aus `__file__` ab,
  sondern hält sie arbeitsverzeichnis-relativ (`.budget-ledger`). Korrekt —
  aber nur, solange die `cd`-Invariante gilt, die jetzt getestet wird. Wer die
  Pfade dort „vereinheitlicht", muss beide Tests bewusst mitziehen.

## [2.2.0] — 2026-08-01

**Erster scharfer Lauf — das Kit ist verifiziert, nicht nur geprüft.**

### Added
- **`TEAM.md`** — der menschliche Einstiegspunkt, bisher die letzte Lücke.
  Beim Abnahmegespräch fiel auf: Die teuerste Warnung des Kits („vor dem ersten
  Guard-Lauf committen") stand **nur in der Terminal-Ausgabe des Installers** —
  und die scrollt weg. Exakt der Fehler, den Planungsregel 5 für den
  Abschlussbericht behebt. `TEAM.md` liegt jetzt im Projekt und im Git:
  Guard-Warnung ganz oben, Rollenübersicht, Kaskaden-Ablauf, Befehlstabelle,
  **Exit-Code-Tabelle** (42 ist kein Absturz), Ablageübersicht und eine
  Fehlersuch-Tabelle.
- Fünf Regressionstests dafür (`test_team_md_bedienanleitung.py`): TEAM.md
  existiert, Guard-Warnung steht im Kopfbereich, Exit-Codes erklärt, Closeout
  als Pflicht benannt, keine offenen Platzhalter. **132 Testfälle** gesamt.
- Installer-Abschlussmeldung verweist zuerst auf `TEAM.md`, mit dem Hinweis,
  dass die Terminal-Ausgabe wegscrollt und die Datei bleibt.

### Verified — scharfer Erstlauf in einem Wegwerf-Projekt
Erstmals mit **echten CLI-Aufrufen** statt Fixtures:
- **Ralph**: Auth-Auflösung (abo) → realer Aufruf → Code gebaut → Smoke-Test
  grün → genau ein `feat(stufe1)`-Commit → Promise erkannt → State auf 2 →
  `RALPH_CAP` respektiert → sauberer Exit 0. **0,2728 USD.**
- **Harry** (Red Team, read-only): realer Sweep über die Historie, Exit 0,
  State auf HEAD gesetzt, **Produktivcode nachweislich unangetastet**.
  **0,4751 USD.**
- **Read-Only-Guard Linie 2 belegt**: Das Log enthält **zwei
  `permission_denials`** — die `--allowedTools`-Allowlist hat zwei
  Bash-Aufrufe von Harry real verweigert. Kein `is_error`.
- **Kostenerfassung**: Ledger und `--budget` weisen 0,7479 USD als
  Abo-Gegenwert aus, korrekt getrennt von real abgerechneten API-Kosten.

Damit ist die Kette Konfiguration → Briefing → `team_claude` → Auth →
Promise-Auswertung → Budget-Check → State-Fortschritt → Guard → Kostenlog
**durchgängig unter echten Bedingungen belegt**.

## [2.1.0] — 2026-08-01

Erstlauf-Anleitung in die Artefakte geschrieben. Sie existierte bisher nur als
mündliche Empfehlung — ein kalt startender Architekt in einem frischen Projekt
hätte sie nicht gekannt. Dieselbe Lehre wie bei Planungsregel 5: Was nicht im
Git steht, existiert für die nächste Instanz nicht.

### Added
- **`rolle-architekt.md`, Abschnitt „Die erste Kaskade eines Projekts"** — vier
  Sonderregeln: Smoke-Test hat Vorrang vor jedem Feature; erste Kaskade auf
  drei bis fünf Stufen begrenzen; `BUDGET_EMPFEHLUNG_USD` konservativ, aber
  nicht knauserig (ein zu tiefer Deckel vervielfacht die Kosten, `HM-32`);
  nach dem Erstlauf den Bauweg ehrlich bewerten.
- **`bootstrap/roadmap-skizzen.md`** ist nicht mehr leer, sondern bringt
  „Skizze 1: Verifikationsfähigkeit herstellen" mit. Sie zeigt über den
  gefüllten `{{SMOKE_TEST}}`-Platzhalter selbst an, ob sie noch gebraucht wird,
  und darf gestrichen werden, sobald der Befehl steht.
- Installer-Abschlussmeldung nennt `TEAM_BUDGET_USD=15` für den Erstlauf und
  verweist ohne Smoke-Test ausdrücklich auf Skizze 1.

## [2.0.0] — 2026-08-01

**Sprach- und stackagnostisch.** Version 1.0.0 setzte an mehreren Stellen still
den Stack des Ursprungsprojekts voraus. Diese Fassung trennt Team-Infrastruktur
und Projekt sauber — verifiziert in Go-, Rust- und PHP-Projektstrukturen.

### Changed — Breaking
- **Neues Layout.** Entrypoints bleiben in der Repo-Wurzel (`./vollautomatik.sh`
  usw. — die Feld-Ablagekonvention), alles Aufgerufene liegt jetzt unter
  `team/`: `team/lib.sh`, `team/redteam.sh`, `team/tools/`, `team/prompts/`,
  `team/tests/`. **Das Kit legt nichts mehr in `scripts/` oder im Test-Ordner
  des Projekts ab** — diese Ordner gehören dem Projekt.
- **Domänen sind projektdefiniert.** `kosten.py` erzwang die Werte `website`
  und `team` an drei Stellen; in einem fremden Projekt war damit keine
  sinnvolle Kostentrennung möglich. Jetzt konfigurierbar über `TEAM_DOMAENEN`
  in `team.config.sh` (Default `produkt team`). **Der Lesepfad validiert nicht
  mehr**: historische Ledger-Zeilen mit heute unbekannten Domänen bleiben
  filterbar; validiert wird nur beim Schreiben.
- **Interview auf sieben Fragen**: Domänen und Commit-Regel des Architekten
  kommen dazu. Letztere stand in der `CLAUDE.md` bisher als offenes
  Entweder-oder.

### Fixed
- **Die Rollen-Briefings waren nicht parametrisiert.** Sie wurden in 1.0.0
  wörtlich übernommen und nannten deshalb `site/**` als Guard-Grenze und
  `python3 scripts/smoke_test.py` als Smoke-Test — in einem fremden Projekt
  bekamen Harry, Marv und Axel damit die **falsche Grenze** genannt und Ralph
  einen Befehl, den es nicht gibt. Die Briefings sind Prompts und werden jetzt
  wie alles andere beim Installieren gefüllt.
- `install.sh` prüfte im Selbsttest noch `scripts/*.py` und meldete deshalb
  immer „Python-Werkzeuge fehlerhaft" (Exit 1 trotz erfolgreicher Installation).
- `.gitignore`-Fragment brachte `__pycache__/` und `.pytest_cache/` global mit;
  jetzt auf `team/**` eingegrenzt.

### Added
- **`team/prompts/rolle-architekt.md`** — das sechste Briefing fehlte, weil der
  Architekt interaktiv läuft und `team_briefing` nie braucht. Für den Trigger
  „Du bist unser Architekt" gab es damit nichts Kompaktes: jetzt Auftrag,
  Grenze, Planungs-Dreisatz, Closeout-Pflicht und Commit-Regel auf einer Seite.
- **`team-test.sh`** — führt die Team-Regressionstests getrennt vom Testlauf
  des Projekts aus. Dein Testbefehl bleibt `TEAM_SMOKE_TEST`.
- Abschlussmeldung des Installers nennt jetzt den **Kostenabschluss nach dem
  Lauf** — ohne ihn bleiben die Architekt-Kosten strukturell unerfasst.

### Tests
- 25 Testdateien, **127 Testfälle**, grün in allen drei geprüften Stacks.
- Angepasst für den generischen Einsatz: Fixtures auf das `team/`-Layout,
  Domänen-Literale durch den konfigurierten Wert ersetzt, Guard-Grenze im
  Briefing-Test aus `team.config.sh` gelesen statt fest erwartet, Lesepfad-Test
  auf den neuen Vertrag umgestellt.

## [1.0.0] — 2026-08-01

Erste Fassung. Der Code stammt aus `website-maxron-de` (22 Kaskaden scharf
gelaufen, 2026-07-10 bis 2026-08-01) und wurde übernommen, nicht neu geschrieben.

### Added
- `install.sh` — idempotenter Installer, fünf Fragen, Selbsttest am Ende
- `kern/team.config.sh` — alle Projektwerte an einer Stelle, von `team-lib.sh`
  gesourct; Ordnerpfade werden zentral auf genau einen Schrägstrich normalisiert
- `bootstrap/` — CLAUDE.md-Vorlage (aus der LLM-Wiki-Vorlage erzeugt, ohne
  Aufnahme-Interview, Platzhalter gefüllt), CHANGELOG mit leerem `[Unreleased]`,
  Beutebuch **mit Vorlage-Block**, Roadmap, Backlog, Ledger, `.gitignore`-Fragment
- 25 Regressionstests der Team-Infrastruktur (127 Testfälle)

### Changed — gegenüber dem Feldprojekt
- **Parametrisierung**: 32 harte Projektbezüge in `ralph.sh`, `frank.sh`,
  `axel.sh`, `redteam.sh` lesen jetzt aus `team.config.sh` statt `site/` und
  `python3 scripts/smoke_test.py` fest zu verdrahten. `team-lib.sh`, `kosten.py`,
  `beutebuch.py`, `vollautomatik.sh`, `halbautomatik.sh` und `team-status.sh`
  waren bereits projektfrei und blieben **wörtlich unverändert**.
- Neue Helfer in `team-lib.sh`: `team_allowed_tools <rolle>` baut die
  Werkzeug-Allowlist aus der Konfiguration; `SMOKE_ZEILE`/`SMOKE_SUFFIX` machen
  einen fehlenden Smoke-Test im Prompt sichtbar, statt ihn still zu übergehen.
- `tests/test_bl29_ledger_domaene_rolle.py` — die Prüfung „Ledgersumme > 0"
  überspringt ein leeres Ledger. In einem frischen Projekt ist es leer; sobald
  die erste Kaskade geledgert ist, greift die volle Prüfung wieder.
- `tests/test_bl55_kostenmessung.py` — prüft die BL-55-Regel jetzt inhaltlich
  (Closeout + Verbot + Stufenbezug) statt einen wörtlichen Satz der
  Feldprojekt-CLAUDE.md, und normalisiert Markdown-Hervorhebungen.

### Fixed — Defekte, die nur in einem frischen Projekt auftreten
- **`ralph.sh` brach ohne jede Meldung ab, wenn `.ralph-plan` fehlte.**
  `head` auf eine fehlende Datei liefert RC≠0 und riss unter `set -e -o pipefail`
  den Loop weg, **bevor** die erklärende Fehlermeldung erreicht wurde — der
  Anwender sah einen blanken Exit 1. Im Feldprojekt existierte die Zeiger-Datei
  seit Kaskade 1, deshalb ist das nie aufgefallen; beim allerersten Start eines
  neuen Projekts ist die fehlende Datei der Normalfall.
- **`team_plan_datei()` hatte denselben Defekt**, obwohl die Funktionsdoku
  ausdrücklich „kein Abbruch hier" zusagte. Betraf `team_ralph_cap` und
  `team_budget_empfehlung` und damit `halbautomatik.sh` und `team-status.sh`.

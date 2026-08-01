# Changelog — T.E.A.M.-Starterkit

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

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

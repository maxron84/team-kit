# Changelog — T.E.A.M.-Starterkit

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

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

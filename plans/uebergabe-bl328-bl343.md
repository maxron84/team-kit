# Übergabe 2026-10-17 — `BL-328` bis `BL-343` bauen

**Für die Bau-Maschine.** Auftrag des Owners vom 2026-10-17, auf derselben
Grundlage wie am 2026-10-12: Auf der Linux-Maschine ist nur triagiert.
Gebaut und nachgewiesen wird auf der Bau-Maschine. Diese Datei ist der
Auftrag. Der letzte Bau-Commit dieser Übergabe löscht sie; als Beleg bleiben
Archiv, CHANGELOG und Commits.

## Stand beim Pull

- **Triage:** `BL-328` bis `BL-343` stehen in [`backlog.md`](backlog.md), je
  mit Hergang, Meldung, Befund der Triage und den Vorschlägen. Neu ist das
  Feldkürzel `Feld G` (README, Abschnitt Herkunft). Das README nennt
  20 offene Einträge, die höchste Nummer ist `BL-343`.
- **Vorher zu bauen:** [`uebergabe-bl326-bl327.md`](uebergabe-bl326-bl327.md),
  mit dem Nachtrag vom 2026-10-17 dort. Zwei Korrekturen daran betreffen
  diese Übergabe unmittelbar (Guard-Haken von `BL-327`, CLI-Aufruf von
  `BL-326`).
- **Auf der Linux-Maschine geprüft:** Kit-Suite 1708 passed, 1 failed
  (`test_bl173`, der bekannte Umgebungsfall), 324 skipped. Ein früherer Lauf
  flackerte an `test_bl220` — das ist `BL-343`. Frische
  Installation: 2010 Fälle, 200 Testdateien, 265 Dateien. README-Wächter,
  `kit-regelinventar.py` und `test_bl267` grün.
- **Wie geprüft:** Jede Meldung am Code beider Bahnen. Nachgestellt nur auf
  der bash-Bahn, mit Wegwerf-Installationen, Stub-Rollen und
  Werkzeugaufrufen. pwsh ist dort nicht installiert: **Jede pwsh-Fundstelle
  unten ist gelesen, nicht gefahren.**
- **Zeilennummern** gelten für `f8e01c2`. Nach dem Bau von `BL-326` und
  `BL-327` verschieben sie sich; die Funktionsnamen bleiben.
- Die Testskizzen der Triage lagen in einem Sitzungsordner der
  Linux-Maschine und kommen nicht mit. Was sie zusichern, steht je Eintrag
  unter **Tests**.
- Das CLI-Verhalten zu `BL-332` und `BL-337` ist an Claude Code 2.1.296
  nachgesehen. Auf der Bau-Maschine `claude --version` notieren.

## Reihenfolge

| Welle | Einträge | Warum so |
|---|---|---|
| 0 | `BL-326`, `BL-327` | eigene Übergabe, mit Nachtrag. Startprüfung und `BL-337` setzen auf `BL-326` auf |
| 1 | `BL-328`, `BL-331`, `BL-338`, `BL-342`, `BL-343` | klein, ohne Entscheidung des Owners (bis auf einen Wortlaut), keine Überschneidung |
| 2 | `BL-339`, `BL-334`, `BL-329`, `BL-332` | alle in `kosten.py`, derselben Datei wie `BL-326`; `BL-332` liefert `--kaskade` für Welle 3 |
| 3 | `BL-330`, `BL-333`, `BL-336` | die gemeinsame Startprüfung, nach `BL-326` (Wiederanlauf) und `BL-332` |
| 4 | `BL-341`, `BL-335`, `BL-340` Teil A | Ende der Fix-Phase, Franks Briefing, Gegenlesen-Block des Architekten |
| 5 | `BL-337` | baut auf dem CLI-Aufruf aus `BL-326` auf; die Formatfrage vorher klären |
| — | `BL-340` Teil B | **nicht bauen:** erst eine Skizze in `roadmap-skizzen.md`, Entscheidung des Owners |

Größen: S sind `BL-328`, `BL-329`, `BL-330`, `BL-331`, `BL-332`, `BL-334`,
`BL-335`, `BL-338`, `BL-342`, `BL-343` und `BL-340` Teil A. M sind `BL-333`, `BL-336`,
`BL-337`, `BL-339` und `BL-341`. Die Startprüfung als Ganzes ist L.

## Fragen an den Owner

Der Bau fragt den Owner zu Beginn nach diesen Punkten. Daneben steht die
Empfehlung der Triage. Alles, was hier nicht steht, ist ohne Entscheidung
baubar.

| Eintrag | Frage | Empfehlung der Triage |
|---|---|---|
| `BL-329` | Woher nimmt `kit-melden` seine Hilfe, und wie weit reicht der Fix? | Dateikopf wie bei den Entrypoints (`BL-223`); zuerst `kosten.py` und `kit-melden`, die übrigen Werkzeuge als Folgepunkt |
| `BL-330` | Ungebuchte Aushärtung beim Start: Warnung oder Abbruch? | Warnung, im Abschlussbericht wiederholt. Die Buchung lässt sich über den Transkriptpfad nachholen |
| `BL-332` | Rückfall ohne Sitzungskennung? `--kaskade N` in die Scharfschalt-Sequenz? | alte Heuristik nur bei `CLAUDECODE=1`, sonst keine Ausnahme; ja, als Commit-Riegel der Sequenz |
| `BL-333` | Was bricht ab? Stash über Prompt oder Mechanik? | nur der Plan bricht ab, übrige schmutzige Pfade warnen einmal; Stash: Satz in Regel 4 des Prompts und Zählung |
| `BL-334` | Unbekanntes Modell mit Token? Buchungszeile bei Exit 2? | Verbot wie heute; keine Buchungszeile bei Exit 2 |
| `BL-335` | Was folgt bei „nicht mehr rot als `grep`"? Ralph mitziehen? | Frank schreibt den Test, der die Grenze festhält, sonst nennt er die Lücke im Fix-Bericht; Ralph zeilenneutral mit |
| `BL-336` | Abbruch beim Start statt Warnung? Name des Schalters? Lauf-Fokus für die Wiederaufnahme? | Abbruch mit Exit 2; `TEAM_REDTEAM_OHNE_FOKUS=1`; ja |
| `BL-337` | Format? Urteilsregel? Rohstrom? Prämisse aus `BL-41`? | `stream-json --verbose` mit Normalisierer; ein Promise in irgendeinem Ergebnis zählt, eine späte Fehlerantwort nach einem Ergebnis mit Promise löst keinen Fallback aus; Rohstrom als `.jsonl`, nie `*.json`; keine undokumentierten Umgebungsschalter der CLI; die Prämisse im selben Bau korrigieren, zeilenneutral in allen vier Briefings |
| `BL-338` | Wortlaut | „🟢 dieser Lauf"; den Abschnitt der letzten Zeilen weglassen |
| `BL-339` | Präfixregel? Tiefe der Eichhärtung? `TEAM_PREISE` auch für Faktoren? | Präfixregel ja; Eichung (a) bis (c) unten; `TEAM_PREISE` vorerst nicht |
| `BL-340` B | Abnahme als Phase oder Rolle? | erst eine Skizze |
| `BL-341` | Den Satz aus `BL-256` zum Teil kippen? Auch das Ende der Bauphase messen? | ja, eng geschnitten; die Bauphase nicht |

---

## `BL-328` — Der Testharnisch neutralisiert die Projektumgebung

**Wo:**

- Exporte: `bash/entry/team.config.sh:66` (`TEAM_PLAN_ORDNER`), `:302`
  (`TEAM_DOMAENEN`), `:332` (`TEAM_PREISE`); `pwsh/entry/team.config.ps1:271`,
  `:274`, `:301`. Aus den Bibliotheken kommen `TEAM_LOCK_HELD`
  (`bash/lib.sh:2201`, `pwsh/lib.psm1:1402`), `TEAM_ABO_KEY_WARNUNG_GEZEIGT`
  und `TEAM_KEY_AUS_FALLBACK` dazu; `AUTH_MODE` (nur pwsh) wirkt nicht.
- `team-test.sh:15-19` und `team-test.ps1:24-27` laden die Konfiguration
  bewusst nicht. Der Aufruf von pytest steht in `team-test.sh:55`,
  `team-test.ps1:65` und `team-test.cmd:27`.
- `geteilt/tests/conftest.py:256-282`: `TEAM_PYTHON` per `setdefault`,
  `TEAM_BENACHRICHTIGUNG=0`, `TEAM_PREISE=""`. Die Minimal-Umgebung
  `basis_umgebung` (`:298`) gilt nur für `Schale.lauf` (`:933`).
- Vorbild im Installer: `bash/install.sh:1573-1587` (`unset "${!TEAM_@}"`),
  `pwsh/install.ps1:1806-1811`.

**Bauen:** `conftest.py` entfernt beim Laden jedes `TEAM_*` außer
`TEAM_PYTHON` aus `os.environ` und setzt danach wie bisher
`TEAM_BENACHRICHTIGUNG=0` und `TEAM_PREISE=""`. Die Exporte der
Konfigurationen bleiben (`BL-209`, `BL-238`).

**Fallen:**

- `TEAM_PLAN_ORDNER` löschen, nicht leeren. `kit_meldung.py:321` und
  `schreibzone.py:101` nehmen `os.environ.get(…, "plans")`; ein leerer Wert
  wäre die Projektwurzel.
- `TEAM_PREISE` muss `""` bleiben, sonst greift wieder der Rückfall auf die
  Projektdatei (`BL-323`). `TEAM_PYTHON` muss bleiben (`BL-133`).
- `test_bl202…:124-134` hält die Exporte beider Konfigurationen fest.
  `test_bl262:55` verlangt dieselben Verstellungen in `kit-test.sh` und
  `kit-test.ps1`, falls Stufe 5 erweitert wird.
- Die Kommentare `install.sh:1573-1577` und `install.ps1:1806-1807`
  nachziehen; ihre Annahme „wie ./team-test.sh beim Anwender" gilt im
  Rollenlauf nicht.

**Tests** (neue Datei, z. B. `test_bl328_rollenumgebung_erreicht_die_suite_nicht.py`):

- Ein verschachtelter pytest-Lauf über `test_stufe43_architekt_abschluss.py`,
  `test_bl27_vergessener_abschluss.py` und unter POSIX den flock-Fall aus
  `test_bl190`, mit `TEAM_DOMAENEN=produkt`, `TEAM_PLAN_ORDNER=docs/plans/`
  und `TEAM_LOCK_HELD=1`, endet mit rc 0. Heute rot (gemessen 8 + 8 + 1).
- Jeder Name, den `team.config.*` oder eine Bibliothek exportiert, steht in
  der Neutral-Liste des Harnischs (Bauart wie `test_bl275`), je Bahn. Heute
  rot an `TEAM_DOMAENEN`, `TEAM_PLAN_ORDNER` und `TEAM_LOCK_HELD`.

## `BL-329` — Hilfe je Verb, `kit-melden --hilfe`

**Wo:**

- `geteilt/tools/kosten.py`: `_main` (`:3628`), der Riegel `:3644`, die
  Bedienfehler-Konvention `:3916`. Parser von `sitzung-messen` `:3992-4036`;
  eine unbekannte Option gilt als Pfad (`:4034-4035`), `--projekt`
  überschreibt `pfade` (`:4058`, `:4064`). `VERBEN` ist die Einzelquelle
  (`BL-253`).
- `kit-melden.sh:44-50`, `kit-melden.ps1:55` und `:74`, `kit-melden.cmd:26`.
  `team_hilfe_wenn_gefragt` (`bash/lib.sh:266`) ist da und unbenutzt; in pwsh
  gibt es `Team-HilfeKopf`, ein Gegenstück zu `team_hilfe_wenn_gefragt`
  fehlt. argparse in `kit_meldung.py:739`.

**Bauen:**

1. Ist das erste Argument `--hilfe`, `--help` oder `-h`: `nutzung(sys.stdout)`
   und Exit 0. Steht einer der drei hinter einem Verb:
   `Nutzung: kosten.py {VERBEN[verb]}` und Exit 0.
2. `sitzung-messen`: Ein Token mit `-`, das keine bekannte Option ist, ergibt
   „unbekanntes Argument" und Exit 1. Pfade vor der Eichung auf Existenz
   prüfen.
3. `kit-melden.sh`: nach `source` `team_hilfe_wenn_gefragt "$@"`.
   `kit-melden.ps1`: `--hilfe` → `Team-HilfeKopf $PSCommandPath`, Exit 0.

**Fallen:**

- In `kosten.py` heißt Exit 2 bei `sitzung-messen` „ungeeicht, nicht buchen"
  (`:4305`). Die Hilfe endet mit 0, ein Bedienfehler mit 1 — nicht mit 2,
  wie die Meldung vorschlägt.
- `test_bl253`: Exit 1 ohne Argumente und „Unbekannter Befehl" plus
  „Nutzung:" auf stderr bleiben. Die Dispatch-Regex (`:59-60`) liest
  `if befehl == …`-Zweige; den Hilfezweig nicht so schreiben, sonst verlangt
  der Test einen `VERBEN`-Eintrag.
- `test_bl227:43-46`: Die Kopf-Regex `./kit-melden.sh <verb>` verträgt eine
  Zeile mit `--hilfe`, aber kein Verb `hilfe` ohne Striche.
- Die Bibliotheken rufen `kosten.py` maschinell auf: nur exakte Tokens
  abfangen.

**Tests:**

- Parametrisiert über `kosten.VERBEN` × (`--hilfe`, `--help`, `-h`): Exit 0,
  die Nutzungszeile des Verbs auf stdout, kein Traceback, nichts geschrieben.
  Heute 51 von 51 rot.
- `sitzung-messen --gibts-nicht` endet mit Exit 1 ohne Traceback;
  `kosten.py --hilfe` mit Exit 0. Heute beide rot.
- `test_bl223`: `kit-melden` aufnehmen, besser die feste Liste durch einen
  Glob über die installierten Entrypoints ohne `team.config.*` ersetzen.
  Heute rot (Exit 2).
- pwsh statisch: `kit-melden.ps1` kennt `--hilfe` und `Team-HilfeKopf`.

## Die gemeinsame Startprüfung — `BL-330`, `BL-333`, `BL-336`

Drei Meldungen aus `Feld G` beschreiben, was die Vollautomatik beim Start
nicht prüft. Der Wiederanlauf aus `BL-326` gehört an dieselbe Stelle. Das
wird **ein** Haken, nicht vier.

**Ort:** `vollautomatik.sh` zwischen `phasen_zeiger_lesen` (`:401`) und
Phase 1 (`:403`), `vollautomatik.ps1` zwischen `Phasen-Zeiger-Lesen`
(`:502`) und `:504`. Erst dort sind `AB_PHASE` und `phasen_faellig` bekannt,
und das Lauf-Log schreibt schon mit. Die Ralph-Anteile kommen zusätzlich
nach `ralph.sh:60` und `ralph.ps1:56`; das deckt Einzel- und Halbautomatik
ab.

**Bauform:** die zusammengesetzte Logik als ein Python-Werkzeug für beide
Bahnen, wie bei `BL-327`. Es gibt 0, 3 oder 2 zurück; die Bahnen loggen und
mappen nur. Das hält beide Bahnen gleich und lässt sich ohne pwsh testen.
Ein neues Werkzeug heißt: README-Zahlen neu messen.

**Reihenfolge der Prüfungen.** Erst alle Befunde sammeln, dann entscheiden,
damit ein Neustart genügt:

1. Optionen, `AB_PHASE`, Sperre, Phasenlage — gibt es schon, Exit 2.
2. Wiederanlauf aus `BL-326` (Stub `abgebrochen` und schmutziger Baum):
   Exit 42. Er kommt zuerst, weil halbe Arbeit sonst als geänderter Plan oder
   schmutziger Baum fehlgedeutet wird.
3. Phase 1 fällig: Der Plan ist getrackt und gleich HEAD (`BL-333`), sonst
   Abbruch.
4. Phase 2 oder 3 fällig: Fokus leer und kein gültiger Lauf-Fokus → Abbruch,
   außer mit `TEAM_REDTEAM_OHNE_FOKUS=1` (`BL-336`).
   `TEAM_REDTEAM_FOCUS_2` ohne `TEAM_REDTEAM_FOCUS` ebenso. Ein wortgleicher
   Fokus zu einem anderen Plan wird gewarnt.
5. Phase 1 fällig: übrige schmutzige Pfade, ohne `TEAM_GUARD_LAUFZEIT` und
   Ignoriertes, einmal warnen.
6. Phase 1 fällig, Kaskade N nummeriert, Transkripte vorhanden:
   `sitzungen-pruefen --kaskade N` (`BL-332`) warnt (`BL-330`). Optional die
   `[WARNUNG]`-Zeilen aus `ledger-pruefen` dazu; sie fangen eine vorige
   Kaskade ohne Closeout (P4, `BL-280`).

Gibt es danach einen Befund der Abbruchklasse, druckt der Schritt alle
Befunde, „Kein Lauf gestartet — nichts gekostet", und endet mit Exit 2.
Sonst merkt er die Warnungen und wiederholt sie im Abschlussbericht, nach dem
Muster `LINT_BEFUNDE` (`vollautomatik.sh:306-314` und `:613-616`,
`.ps1:410-418` und `:751-753`).

**Exit 2**, weil das Muster von `BL-241` dafür steht („Kein Lauf
gestartet"). Nicht 42: Das ist die Pause, sie bleibt für `BL-326` und lädt
zum blinden Neustart derselben Zeile ein. Nicht 43 oder 44, die sind belegt.
Das README (`:813-819`) und die Köpfe nennen 2 und 44 bisher nicht; das
nachziehen.

**Worauf der Schritt aufsetzt:** `team_plan_datei` (`bash/lib.sh:2643`,
`pwsh/lib.psm1:1025`), `team_architekt_kaskade` (`:2530` / `:1035`),
`team_architekt_stand` (`:2594` / `:1140`), `team_budget_empfehlung` und
`team_plankopf_wert`, `team_plan_stufen`, `phasen_faellig`
(`vollautomatik.sh:245`, `.ps1:346`); in `kosten.py` `sitzungen_pruefen`,
`ledger_anzahl`, `kaskade_aus_plan` und `ledger_pruefen`.

**Später, Entscheidung des Owners:** Als `./vollautomatik.sh --pruefen`
würde daraus der „Konsistenz-Check" der Scharfschalt-Sequenz
(`rolle-architekt.md:98`, Regel 4), der heute nirgends ein Befehl ist. Er
ersetzte die still anhaltende `&&`-Kette aus `BL-336`.

### `BL-330` — die ungebuchte Aushärtung

**Wo:** Start liest nur Deckel und Empfehlung (`vollautomatik.sh:137-151`,
`.ps1:259-271`). `kaskaden_nummer` (`:283-287`, `.ps1:386-391`) dient nur dem
Bericht.

**Bauen:** Schritt 6 oben. Die Warnung nennt Kennung und „Kaskade N".

**Fallen:**

- In Fixtures ohne Transkript endet `sitzungen-pruefen` mit Exit 1
  (`kosten.py:4339-4342`). Das bleibt still; sonst rauscht es in rund
  29 Vollautomatik-Testdateien und in `test_bl250…:107-114` („Bericht bleibt
  ruhig").
- Nur die jüngste Sitzung prüfen, nicht das ganze Fenster ab der ältesten
  Ledger-Zeile — sonst meldet jeder Start jede Altlücke (`BL-14`). Ein
  Bestandsledger ohne Kennung ist keine Lücke.
- Die Tests brauchen eigenes `HOME` und `USERPROFILE` und erben keine
  `CLAUDE*`-Variablen.

**Ungeprüft, beim Bau ansehen:** Die `Buchen:`-Zeile von `sitzung-messen`
trägt kein `--kaskade` (`kosten.py:2640-2647`). Ohne den Schalter bucht
`akteur-abschluss` auf die Kaskade aus `.ralph-plan` (`:4577-4578`), und die
zeigt vor dem Schritt „Zeiger umlegen" (`rolle-architekt.md:319-322`) noch
auf die vorige Kaskade. Das wäre eine zweite Art, die Aushärtung zu
verlieren.

**Tests:** Fixture wie `test_bl217_phasen_zeiger.py:51-87` mit Stub-Rollen,
committetem `plans/team-kaskade-2-x.md` und `.ralph-state=1`; im Ledger die
Architekten-Zeile der Skizze für K2; ein Fake-HOME mit gebuchter Skizze und
ungebuchter Aushärtung (mtime vor fünf Minuten); keine `CLAUDE*`. Erwartet:
eine Warnung vor „=== PHASE 1" mit Kennung und „Kaskade 2", wiederholt nach
„=== ABSCHLUSSBERICHT", Exit unverändert. Heute rot. Gegenprobe: Ist die
Aushärtung für K2 gebucht, bleibt der Lauf still.

### `BL-333` — der Plan außerhalb von Git, Ralph ohne Warnung, `git stash`

**Wo:**

- `ralph.sh:38-42` prüft nur, ob der Plan existiert, `:56-60` den Deckel;
  `:125` zieht `team_stufen_schnappschuss`, `:137-139` ist Regel 4 des
  Prompts, `:152-160` der Aufruf. pwsh: `ralph.ps1:38-46`, `:51-55`, `:120`,
  `:133-135`, `:149-155`.
- Der Warnblock steht in `team_guard_begin` (`bash/lib.sh:1476-1484`,
  `pwsh/lib.psm1:1614-1624`).
- `kaskade_beginn` (`kosten.py:1643-1685`); die Berichtszeile
  `vollautomatik.sh:587-590`, `.ps1:719-726`; `--rollen-abschluss`
  `kosten.py:4883-4911`.

**Bauen:**

1. Ein Helfer neben `team_plan_datei`:
   `git ls-files --error-unmatch -- <plan>` und
   `git diff --quiet HEAD -- <plan>`. Aufruf in `ralph.*` nach dem Deckel und
   im Startschritt (Schritt 3 oben). Exit 2; die Meldung nennt den Pfad und
   den Commit-Befehl. Die Phase-1-Auswertung (`vollautomatik.sh:420-423`,
   `.ps1:521-524`) reicht rc 2 als 2 durch, nicht als „Fehler (1)".
2. Den Warnblock aus `team_guard_begin` als eigenen Helfer herauslösen und
   einmal vor der Stufenschleife rufen (`ralph.sh` vor `:87`, `ralph.ps1` vor
   `:85`).
3. Stash: ein Satz in Regel 4 des Prompts, auf beiden Bahnen wortgleich.
   Dazu als Mechanik: `git stash list` vor und nach `team_claude` zählen;
   ist die Liste gewachsen, laut melden.

**Fallen:**

- `rolle-ralph.md` steht auf 45 von 45 Zeilen; der Stash-Satz gehört deshalb
  in den Prompt. `test_bl112` und `test_bl117` verlangen wortgleiche Prosa
  auf beiden Bahnen.
- Die Vollautomatik-Fixtures zeigen mit `.ralph-plan` auf einen Plan, den es
  nicht gibt, und nutzen einen Stub-Ralph (`test_bl217…:80`). Ein fehlender
  Plan bleibt Ralphs bisheriger Fehler (`ralph.sh:39-42`), kein neuer
  Abbruch der Startprüfung.
- Ralph-Fixtures committen den Plan (Stichprobe `test_bl41`, `test_bl60`,
  `test_bl110`, `test_bl150`, `test_bl151`, `test_bl301`); vollständig
  ungeprüft.
- Eine neue Laufzeitdatei gehört in `TEAM_GUARD_LAUFZEIT`
  (`bash/lib.sh:1531`, `pwsh/lib.psm1:1460`), ins gitignore-Fragment und in
  `test_bl269`.

**Tests** (beide Bahnen):

- (a) Der Plan wird erst nach dem Commit angelegt, eine CLI-Attrappe
  schreibt eine Marke: rc 2, stderr nennt Plan und `git add`, die Marke
  fehlt. Heute läuft die Attrappe.
- (b) Plan committet und danach geändert: dasselbe.
- (c) Plan sauber, `plans/backlog.md` geändert: genau eine
  „[guard] WARNUNG … NICHT sauber" mit diesem Pfad. Heute keine.
- (d) Die Attrappe hinterlässt einen Stash: eine Warnung. Heute keine.
- (e) Vollautomatik mit Stub-Rollen und existierendem, aber ungetracktem
  Plan: rc 2, kein „STUB ralph". Heute rc 0.
- Gegenprobe: sauberer, committeter Plan → alles unverändert.

### `BL-336` — der fehlende Fokus

**Wo:** Vor Phase 1 liest die Vollautomatik nur `TEAM_REDTEAM_FOCUS_2`
(`vollautomatik.sh:457-462`, `.ps1:570-579`). Verfall: `bash/redteam.sh:65-113`
(Verfall `:101-111`, wortgleich `:93-99`), `pwsh/redteam.ps1:84-124`.
Bericht: `vollautomatik.sh:591-599`, `.ps1:728-737`. Regel 4:
`bootstrap/CLAUDE.md.vorlage:334-344`; Briefing `rolle-architekt.md:96-99`
und `:106-108`.

**Bauen:**

- Schritt 4 oben, nur wenn Phase 2 oder 3 fällig ist — nicht bei
  `TEAM_VOLLAUTOMATIK_AB_PHASE=4` und nicht in der Fixphase.
- Die Fokuslage beim Start ins Lauf-Log schreiben. Danach steht fest, wie
  gestartet wurde.
- Den Lauf-Fokus für die Wiederaufnahme festhalten, etwa als dritte Zeile in
  `.vollautomatik-state` (`phasen_naechste` `vollautomatik.sh:241-243`,
  `.ps1:340-344`; die Datei wird bei `:569` gelöscht). Heute übernimmt Harry
  nach einer Pause seinen alten Fokus, und Marv bekommt keinen.
- Kopf, Regel 4 und Architekten-Briefing nachziehen. Regel 4 nennt die
  Sequenz noch ohne den Kostenabschluss, den das Briefing seit `BL-291` an
  erster Stelle hat.

**Fallen:**

- Rund zwei Dutzend Vollautomatik-Tests laufen ohne Fokus und erwarten
  rc 0 (z. B. `test_bl250…:87-103`, `test_bl217`, `test_bl241`). Sie brauchen
  einen Harnisch-Schalter in `conftest.py` wie `TEAM_BENACHRICHTIGUNG`
  (`:267`, `:317`). `BL-328` räumt im Harnisch jedes `TEAM_*` ab; der
  Schalter wird **danach** gesetzt.
- `pwsh/kit-test.ps1:995-1047`: Der Trockenlauf fährt ohne Fokus und
  verlangt Exit 0 und beide Sweeps. Dort einen Fokus setzen.
- Die NORM-Zitate `doku/regel-inventar.md:99-101` und `:104` wörtlich
  erhalten. Eine neue Laufzeitdatei fällt unter `test_bl269`.

**Tests** (beide Bahnen, mit den Helfern aus `test_bl241` und `test_bl217`):

- (a) Ohne Fokus und ohne Schalter: rc 2, der Text nennt
  `TEAM_REDTEAM_FOCUS` und den Schalter, kein „STUB ralph". Heute rc 0.
- (b) Mit `TEAM_REDTEAM_OHNE_FOKUS=1`: Der Lauf fährt, die Startzeile sagt
  „ohne Fokus auf Ansage". Heute fehlt die Zeile.
- (c) `AB_PHASE=4` ohne Fokus: Der Lauf fährt (bleibt grün).
- (d) Wortgleicher Fokus zu einem anderen Plan: Der Befund steht vor
  „=== PHASE 1". Heute erst im Sweep.
- (e) Wiederaufnahme bei Phase 3 ohne Variable: Marv bekommt den Lauf-Fokus.
  Heute VERFALLEN.

## `BL-331` — der Python-Name in der Prosa

**Wo:**

- `geteilt/prompts/rolle-architekt.md:104-105` (der Satz), `:194`
  (`python3 team/tools/zitat_lint.py`), `:30` (`ralph.sh`).
- `bootstrap/TEAM.md:364` und `:387` (direkt über `:388-389`, die den
  Platzhalter tragen); `bootstrap/beutebuch.md:50`; schwach
  `bootstrap/CLAUDE.md.vorlage:702` (Prosa).
- Ersetzung ohne Bedingung: `bash/install.sh:1200` (Update, `:1310`) und
  `:2067` (Erstinstallation, `:2185-2191`); `pwsh/install.ps1:396` über
  `Fuelle-Datei` (`:327-340`), Aufrufe `:1541-1543` und `:2239-2246`.

**Bauen:** „Python heißt hier `{{PYTHON}}`." — zeilenneutral und auf jeder
Plattform wahr. Die vier Literale auf den Platzhalter, `:30` auf
`ralph{{ENDUNG}}`. Keine bedingte Ersetzung im Installer; sie bräuchte drei
Füllroutinen und den Gleichstand beider Bäume (`BL-163`).

**Fallen:**

- `doku/regel-inventar.md:104` zitiert „**Den Fokus setze ich bei jeder
  Kaskade**" aus `:106`, direkt nach dem Satz. Die Zeile darf beim Umbruch
  nicht verrutschen.
- Ein Test darf die Marke nicht wörtlich enthalten (kit-test Schritt 3,
  `test_bl163…:127`). Er setzt sie mit `"".join(...)` zusammen, wie
  `test_bl131…:66`.
- `beutebuch.md` und `CLAUDE.md` sind Projektdaten. Dort kommt der Fix nur
  bei Neuinstallation an oder über den Abgleich aus `BL-311`. Ob
  `CLAUDE.md.vorlage:702` angefasst wird, ist Abwägung: Es erzeugt in jedem
  Feldprojekt einen Abgleich-Vorschlag.

**Tests** (bahnneutral, neue Datei):

- (a) Marke durch `python3` ersetzt, Leerraum normalisiert: Das Muster
  „`X`, nicht `X`" trifft nirgends. Heute rot an `:105`. Läuft auch in einer
  Installation.
- (b) Kein wörtliches `python3` in Briefings, `TEAM.md` und `beutebuch.md`
  (Muster aus `test_bl131…:126`). Heute rot an den vier Stellen. Nur in der
  Kit-Ablage; in einer Installation ist der Text schon gerendert.
- (c) Optional: kein `*.sh` in `rolle-architekt.md` außerhalb `:100-102`.
  Rot an `:30`.

## `BL-332` — die 15-Minuten-Ausnahme und `--kaskade N`

**Wo:** `kosten.py:2652-2656` und `:2743-2747` (die Ausnahme nach Alter),
Ausgabe `:4354`, Exit `:4401`. `transkript_kennung` (`:2189-2192`),
`sitzungs_dateien` (`:2195-2207`, zählt auch `<kennung>/subagents/`),
`gebuchte_quellen` (`:803-811`). Nutzungszeile `:120ff`, `VERBEN` `:3592`.

**Bauen:**

- Die Ausnahme gilt nur, wenn `CLAUDE_CODE_SESSION_ID` die Sitzung trifft.
  Ohne die Variable bleibt die alte Heuristik nur bei `CLAUDECODE=1`
  (Empfehlung), sonst gibt es keine Ausnahme.
- Neuer Modus `--kaskade N`: Die jüngste interaktive Sitzung braucht eine
  Architekten-Zeile für Kaskade N mit ihrer Kennung in den Quellen. „nicht
  gebucht" ist dort immer eine Lücke, „zuwachs" nicht. „unter K N-1 gebucht"
  wird ausdrücklich benannt.
- Doku: `rolle-architekt.md:217-220`, `bootstrap/TEAM.md:247`,
  `doku/faq.md:491`, `doku/anhang-a.md:612`.

**Fallen:**

- `test_bl247…:391-397` schreibt das heutige Verhalten fest; der Fall
  braucht künftig `CLAUDE_CODE_SESSION_ID`.
- `_cli` (`:107-114`) reicht `os.environ` durch. Läuft die Suite in einer
  Agentensitzung, kommen echte `CLAUDE*`-Werte mit. Jeder Fall setzt oder
  entfernt sie ausdrücklich.
- `test_bl253` prüft Verben und Nutzungszeile. Exit 0 bei „ohne Zuordnung"
  und „erwaehnt" bleibt (`:4401`).
- Nicht geprüft: CLI-Einstieg ohne IDE, Windows, `--resume`. Auf der
  Bau-Maschine nachsehen, ob `CLAUDE_CODE_SESSION_ID` dort gesetzt ist.

**Tests:**

- (a) Sitzung eben geschrieben, Umgebung ohne `CLAUDE*`: rc 3 und „NICHT
  gebucht". Heute rc 0.
- (b) `CLAUDE_CODE_SESSION_ID=andere`: rc 3. Heute 0.
- (c) `--kaskade 2`, nur die Skizze für K2 gebucht: rc 3. Heute rc 1
  („unbekanntes Argument").
- Gegenrichtung: Die Kennung trifft → rc 0 und „laeuft noch".

## `BL-334` — `<synthetic>` mit null Token

**Wo:** `kosten.py:2244` (`if not usage: continue`), `:2252`
(`gesehen.add`), `:2265-2268`. `sitzung_kosten` `:2425-2443` (`:2438`).
Warnung `:4251-4254`, Exit `:4305`, `_buchungen_drucken` `:4290`.
`sitzungen-pruefen` gibt nur einen Hinweis (`:4367`). Ledger-Meta `:4610`,
Anzeige `protokolle.py:165`. Briefing `rolle-architekt.md:259-262`,
`doku/faq.md:482-483`.

**Bauen:**

- Sätze überspringen, deren fünf Token-Zähler alle 0 sind — **vor**
  `gesehen.add(kennung)`, damit ein Null-Satz keine echte Nachrichten-ID
  verbraucht. Das deckt auch den Phantom-Zuwachs.
- Ein Modell nur dann `unbekannt` führen, wenn es Token hat.
- Exit 2 nur bei „ungeeicht" oder bei Token ohne Preis, dann mit deren Zahl.
  Bei Exit 2 keine `Buchen:`-Zeile (Empfehlung).
- Briefingsatz und FAQ auf „folge der Schlusszeile" kürzen.
- `<synthetic>` **nicht** mit Preis 0 in die Tabelle: Sie dient auch
  `modelle` als Versionsquelle (`:1379`), und die Antwortzahl bliebe falsch.

**Fallen:**

- `test_bl141::test_unbekanntes_modell_wird_genannt_statt_geraten` (9 Mio
  Token) bleibt grün — deshalb eine Token-Regel, keine Namensliste.
- `test_bl141::test_cli_bricht_bei_veralteter_preistabelle_nicht_still_ab`
  und `test_bl218:184` pinnen Exit 2 für „ungeeicht" und `GESAMT:` auf
  stdout.
- Die Antwortzahl sinkt: `Antworten:`, `LANGE_SITZUNG_ANTWORTEN`, die
  Ledger-Meta `antworten` (wird nirgends gegengeprüft).
- `rolle-architekt.md` hat kein Zeilenlimit; der Satz steht nicht im
  Regel-Inventar. Gleiche Datei wie `BL-326`.

**Tests:** Ein Transkript mit einer echten Antwort und zwei
`<synthetic>`-Null-Sätzen: Exit 0, keine Warnung, „Antworten: 1".
`sitzung_messen(von=<nach der echten Antwort>)` liefert 0 Antworten, und
`sitzungen_pruefen` sagt „gebucht" statt „zuwachs". Gegenprobe: Ein
unbekanntes Modell mit Token wird weiter genannt.

## `BL-335` — Franks Gegenprobe

**Wo:** `geteilt/prompts/rolle-frank.md:35-41`; `rolle-ralph.md:25` und
`:28` (dieselbe Formulierung) und `:36-41` (sein Absatz zum Zählen roter
Stellen); die Regel `bootstrap/CLAUDE.md.vorlage:432-436` und `:443-453`. Im
Regel-Inventar steht Frank nur mit `doku/regel-inventar.md:83-84`.

**Bauen** — Vorschlag der Triage, sechs statt sieben Zeilen, je höchstens
80 Zeichen, an einer Kopie gegen die Prüfmarken geprüft:

```
**Führt mein Fix einen zentralen Wert ein oder ändert ihn** (Konstante, Grenze,
Default, Schwellwert), fahre ich ihn probeweise auf **zwei fremde Werte**, höher
und niedriger, lasse je die Suite laufen und setze ihn **nachweislich zurück**.
Rot ist der Beleg (`Kit-BL-167`): Die Zahl roter Tests je Verstellung kommt in
den Commit-Text; ist sie nicht größer als die `grep`-Treffer nach Name und Wert,
hält kein Test den Wert fest. Im Feld: `grep` fünf, das Verstellen **sieben**.
```

- Was danach folgt (Test schreiben oder im Fix-Bericht nennen), entscheidet
  der Owner. Es muss in dieselben sechs Zeilen passen, sonst ist die Zeile
  für `BL-327` wieder weg.
- Ralph zeilenneutral in `:28`: „… niedrigeren — und je Wert die roten Tests
  der Suite gezählt habe. **Danach setze ich den Wert …**".
- Eine NORM-Zeile „Rot ist der Beleg" mit Träger `rolle-frank` ins
  Regel-Inventar, damit die nächste Straffung den Satz nicht wieder still
  streicht (so geschehen in `8c79d5a`).

**Fallen:**

- Zeilenlimit 45: `test_stufe90_briefings.py:84-91`, `test_bl165…:302-319`,
  `test_bl219…:115-120`.
- `test_bl49_regler_gegenprobe.py:41-65` verlangt in Frank **und** Ralph
  „zwei fremde Werte", „zurück", „Suite", „(probeweise) Verstellen" und
  „sieben". „Suite" steht heute nur im zu streichenden „Suite beide Male
  grün" — stumpf streichen macht `test_bl49` rot. Der Wortlaut der Meldung
  trägt weder „Suite" noch „sieben".
- Bei jeder Straffung erhalten: „Dreisatz" (`test_stufe90:38-45` und
  `:94-104`), „Eingaben aus echter Quelle" und „wie dokumentiert"
  (`test_bl219:118`), die Inventarzeilen `:83` und `:84`.
- Den Docstring `test_bl165…:290-296` mitziehen („Frank steht bewusst NICHT
  in dieser Liste"). Schreibweise `Kit-BL-167`, sonst schlägt `test_bl140`
  an.
- Archiv, Eintrag `BL-167`: Der Satz, Ralph und Frank zögen nach, stimmt
  für Frank nicht. Beim Abtragen richtigstellen.

**Tests:**

- `test_bl165…::test_die_briefings_kennen_das_kriterium` um
  `rolle-frank.md` erweitern. Heute rot.
- `test_bl49`: „beide Male grün" steht weder bei Frank noch bei Ralph.
  Heute rot an `frank:38` und `ralph:28`.
- Franks Absatz nennt die Einführung (Muster „zentralen Wert ein"). Heute
  rot.

## `BL-337` — mehrere Ergebnisse einer Sitzung

**Wo:**

- `team_claude` (`bash/lib.sh:712`), CLI-Aufrufe `:747`, `:823`
  (API-Fallback), `:856`, `:858` (429-Retry). pwsh: `Team-ClaudeSchreiben`
  (`pwsh/lib.psm1:2365-2393`, `$roh = & $Claude … --output-format json` in
  `:2387`), aufgerufen in `:2487`, `:2551` und `:2581`.
- Leser des einen Objekts: `team_promise_in` (`bash/lib.sh:955-965`,
  `pwsh/lib.psm1:722-729`), `team_result_meldet_erfolg` (`:1074` / `:799`),
  `team_result_is_error` (`:2273` / `:696`, daran hängt der Fallback),
  `team_result_auszug` (`bash/lib.sh:999`), `team_bewerte_ergebnis`
  (`bash/lib.sh:2292`, `pwsh/lib.psm1:706`). In `kosten.py` die
  Abdeckungszeilen (`:3836`), `permission_denials` (`:1553`, `:1586`), das
  Turn-Profil `turn_profil` (`:1321-1347`, Ausgabe `:3765-3767`; im Bericht
  `vollautomatik.sh:583`, `.ps1:715`) und `team_kein_zug`
  (`bash/lib.sh:932`, `pwsh/lib.psm1:926`).
- Die Prämisse aus `BL-41` („headless kein zweiter Gesprächszug"):
  `SMOKE_ZEILE` und `SMOKE_SUFFIX` (`bash/lib.sh:147`, `:168`;
  `pwsh/lib.psm1:364`, `:386`), `rolle-ralph.md:17`, `rolle-harry.md:24`,
  `rolle-marv.md:24`, `rolle-axel.md:16`, `team_quittung_fehlt_melden`
  (`bash/lib.sh:1098`, `pwsh/lib.psm1:2077`), `README.md:817`.

**Was die CLI tut** (2.1.296, aus `claude --help` und den Schema-Texten der
CLI, ohne Prompt): Im json-Modus schreibt sie am Ende genau ein Objekt, das
letzte Ergebnis. Mit `--verbose` schreibt sie ein Array aller Nachrichten,
mit `stream-json --verbose` JSONL. `total_cost_usd` und `modelUsage` laufen
kumulativ, `num_turns` und `usage` gelten je Turn. Im Print-Modus wartet die
CLI nach dem letzten Turn auf Hintergrund-Shells, bis zu zehn Minuten.

**Bauen** (nach `BL-326`, im Abschlussschritt des CLI-Aufrufs):

1. Ausgabe als `--output-format stream-json --verbose` in die Nebendatei aus
   `BL-326`; pwsh streamt, statt `$roh` zu sammeln.
2. Ein Normalisierer in `kosten.py`, neben `fehlergrund` (`:3781`), nach dem
   Muster von `BL-316`. Er liest drei Formen: JSONL (stream-json), das Array
   (json mit `--verbose`) und das Einzelobjekt (alte Form, Attrappen,
   `TEAM_DRY_RUN`). Er schreibt ein Objekt nach `$out`:
   - die kumulativen Felder aus dem letzten Ergebnis (`total_cost_usd`,
     `modelUsage`, `duration_api_ms`, `session_id`);
   - `num_turns` und `duration_ms` summiert;
   - eine Liste `team_ergebnisse` mit Index, `subtype`, `is_error`, Turns und
     dem Anfang von `result`;
   - einen Merker für die späte Antwort.

   Trägt `result` alle Ergebnistexte, bleiben die Leser unverändert. Sonst
   sucht `team_promise_in` in `team_ergebnisse`.
3. Turn-Profil: Turns summieren und die Stufe als „Antwort auf späte
   Hintergrundmeldung" ausweisen. Das Format „N Turns" bleibt.
4. Die Urteilsregel in `team_bewerte_ergebnis` nach Entscheid des Owners.
5. Die Prämisse aus `BL-41` korrigieren, wenn der Owner zustimmt. Der
   Hintergrund-Absatz bleibt in ralph, harry, marv und axel byte-gleich.

**Kleinste Vorstufe**, falls der Owner das Format vertagt (S, ohne
Formatwechsel): `result_index > 0` erkennen und im Turn-Profil und in der
Quittungsmeldung benennen.

**Fallen:**

- **Nur das Flag umzustellen richtet Schaden an.** bash: `json.load`
  scheitert, und `team_versuch_sichern` (`bash/lib.sh:634-655`)
  überschreibt die Ausgabe mit dem Ersatzzettel (`is_error`) — jeder Aufruf
  geht in den API-Fallback. pwsh: `Team-JsonLesen` (`:238-245`) liefert
  `$null`, ebenso. Der Normalisierer läuft vor `team_versuch_melden`.
- **Kumulative Felder nie summieren.** Sonst verdoppelt sich
  `TEAM_LAST_COST`, `team_budget_check` greift falsch, und das Ledger zählt
  doppelt.
- **Den Rohstrom nicht als `*.json` ablegen.** Mit `--verbose` trägt er jede
  Werkzeug-Ein- und Ausgabe. `team_log_dateien` (`:426-442`) globbt
  `*.json`, `logs_einsammeln` liest rekursiv samt Archiv (`:2975ff`).
- **Attrappen:** Elf Testdateien hängen eine über `TEAM_CLAUDE_BIN` ein,
  `test_bl41` über `PATH`. Alle geben ein Einzelobjekt aus, gleich welches
  Flag; dazu die `DRY_RUN`-Stubs (`bash/lib.sh:721-730`,
  `pwsh/lib.psm1:2467-2476`). Der Normalisierer nimmt diese Form an.
- `test_bl32_messung_und_lehren.py:97-121` prüft das Turn-Profil an
  Einzelobjekten und „87 Turns".
- Briefings: ralph, harry, marv und frank stehen auf 45 von 45
  (`test_stufe90_briefings.py:89`, `test_bl265:218-233`). Der
  Hintergrund-Absatz ist in ralph, harry, marv und axel byte-gleich
  (`test_bl265:135-152`). `SMOKE_ZEILE` und `SMOKE_SUFFIX` lauten in beiden
  Bahnen gleich (`test_bl112`, `test_bl265:116`).
- Keine undokumentierten Umgebungsschalter der CLI setzen. Im Binary stehen
  `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` und
  `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`; ihr Verhalten ist nicht
  zugesichert.

**Tests** (neue Datei, beide Bahnen über `schale`). Die Attrappe ist gebaut
wie `_stub` in `test_bl316:125-147` und bildet CLI 2.1.296 nach: bei `json`
nur Ergebnis 1 ohne Promise (`result_index` 1, `num_turns` 1,
`total_cost_usd` 1.1271); bei `json --verbose` das Array; bei
`stream-json --verbose` JSONL mit init, Ergebnis 0 (`STUFE_7_COMPLETE`,
23 Turns, 0.95) und Ergebnis 1.

- (a) `team_claude`, dann `team_promise_in STUFE_7_COMPLETE` → 0. Heute rot.
- (b) `TEAM_LAST_COST` bleibt 1.1271 und wird nicht 2.0771 — die Gegenprobe
  gegen Summieren. Heute grün, bleibt grün.
- (c) `kosten.py turns` meldet „24 Turns" und den Merker. Heute „1 Turns".
- (d) Über `ralph.*` wie `test_bl41:136-175`: Exit 0, `.ralph-state` auf
  N+1, keine Selbstprüfung auf stderr. Heute läuft die Selbstprüfung.
- (e) Nach Entscheid des Owners: Ergebnis 1 mit `is_error` → kein Fallback
  (Zähler der Attrappe 1). Heute 2.

## `BL-338` — der Bericht zitiert sich selbst

**Wo:**

- bash: `vollautomatik.sh:97` (`LAUF_LOG`), `:103-104`
  (`exec > >(tee -a "$LAUF_LOG") 2>&1`), `:570-571` (Bericht).
  `team-status.sh:196-200` nimmt das jüngste Lauf-Log und zeigt
  `tail -n 3`; die Pipeline-Zeile `:124-131` fragt `team_pipeline_laeuft`
  (`bash/lib.sh:2232`).
- pwsh: `Log` (`vollautomatik.ps1:108-116`), `team-status.ps1` über
  `Rolle-Starten` (`:702-703`; jede Zeile sofort ins Lauf-Log `:212`, Takt
  50 ms `:226`). `team-status.ps1:193-199` und `:114-122`
  (`team_pipeline_laeuft` `pwsh/lib.psm1:1316`).
- Fixphase: `fixphase.sh:29`, `fixphase.ps1` — fährt die Vollautomatik und
  hat denselben Fehler.

**Bauen:**

- Pipeline-Zeile: Ist `TEAM_LOCK_HELD=1` gesetzt (exportiert vom
  Sperrinhaber, `bash/lib.sh:2201`, `pwsh/lib.psm1:1402`), steht dort
  „🟢 dieser Lauf (Sperre gehalten vom Aufrufer)". Der Aufruf von
  `team_pipeline_laeuft` bleibt für den Fall ohne Variable.
- Log-Zeilen: Die Vollautomatik exportiert ihren eigenen Logpfad, etwa
  `TEAM_LAUF_LOG`, nach `vollautomatik.sh:97` bzw. `.ps1:103`. Ist das
  jüngste Log das eigene, entfällt der Abschnitt. `TEAM_LOCK_HELD` allein
  reicht dafür nicht, weil die Halbautomatik es auch setzt.

**Fallen:**

- `test_bl190:441-458` und `test_bl199:230-243` verlangen
  `team_pipeline_laeuft` und „unbekannt" im Text beider
  `team-status`-Skripte. Den neuen Zweig davor setzen.
- Keine neue Flagge: Sie zöge Dispatcher (`team-status.sh:595-633`),
  Hilfekopf und `test_bl222`/`test_bl223` mit (`BL-222`).
- Die End-zu-End-Tests sehen den Fehler nicht: `test_bl256` `_projekt`
  (`:158-189`) kopiert `team-status.sh` nicht mit, `test_bl241:33`,
  `test_bl217:48` und `test_bl210:161` setzen Stubs dafür ein.
- Im Status-Menü der Halbautomatik ist `TEAM_LOCK_HELD` ebenfalls gesetzt.
  Der neue Wortlaut muss dort auch stimmen.

**Tests** (neue Datei):

- bash: Minimalprojekt wie `test_bl256`, aber mit der echten
  `team-status.sh` (und `schreibzone.py`), Stub-Rollen, `./vollautomatik.sh`.
  Unter „Vollautomatik (letzte 3 Zeilen" stehen keine Zeilen dieser
  Statusausgabe, oder der Abschnitt fehlt; im Bericht steht kein „läuft
  gerade". Heute rot (fünf von fünf Läufen).
- pwsh: dasselbe mit `vollautomatik.ps1`. „läuft gerade" ist sicher nur unter
  Windows rot, unter Linux-pwsh ungeprüft; notfalls `skipif`.
- Gegenprobe: Aufruf außerhalb eines Laufs, während ein fremder Prozess die
  Sperre hält → weiter „läuft gerade" und die drei Zeilen.

## `BL-339` — Cache-Read-Satz von Sonnet 5.5 und die blinde Eichung

**Wo:** `CACHE_READ_FAKTOR_JE_MODELL` (`kosten.py:2394-2398`);
`PREIS_VIELFACHE` (`:1887`), `preis_vielfache` (`:2401`);
`PREIS_INPUT_USD_PRO_MTOK` (`:1894-1922`); `modell_basispreis` (`:2026`).
Eichung: `preise_nachrechnen` (`:2752`, übersprungene Logs `:2802-2810`,
Intervall `:2864-2869`), `preis_versatz` (`:2874`, `:2907-2913`),
`preis_diagnose` (`:2916-2969`), Ausgabe `:4127-4211`. `TEAM_PREISE` kennt
nur Basispreise (`:1974`).

**Bauen:**

1. `"claude-sonnet-5-5": 0.05` in `CACHE_READ_FAKTOR_JE_MODELL`.
2. `claude-haiku-5-5` in `PREIS_INPUT_USD_PRO_MTOK`. Ein Feldlog impliziert
   0,10 USD je Mio Input; Satz und die Regel für lange Prompts vor dem
   Eintrag an der Preisliste prüfen.
3. Eichung härten:
   - (a) die Cache-Write-Laufzeit aus `usage.cache_creation` übernehmen,
     wenn die Summen mit `modelUsage` gleich sind; das Intervall bleibt nur
     Rückfall;
   - (b) je Modell urteilen;
   - (c) übersprungene Logs nennen, etwa „38 von 86 nicht nachgerechnet:
     claude-haiku-5-5 ohne Preis".
   - Optional (d): Basispreis und Cache-Read-Satz zusammen fitten (ein
     2×2-System) und den falschen Satz benennen. Ohne (d) schreibt die
     Diagnose den Fehler nach (a) dem Basispreis zu und schlägt nach
     `BL-211` eine falsche `TEAM_PREISE`-Zeile vor.
4. Präfixregel (Owner): Nur exakte IDs oder IDs mit Datums- oder
   Plattformsuffix treffen. Eine neue Unterversion ist dann laut unbekannt
   statt still falsch; nach `BL-334` schadet ein unbekanntes Modell ohne
   Token nichts mehr.
5. Alte Buchungen werden wie bei `BL-302` nicht nachgerechnet.

**Fallen:**

- `test_bl302_cache_read_satz_je_modell.py:66` pinnt
  `("claude-sonnet-5-5", 0.20)`. Der Docstring `:17-19` und der Archivtext
  von `BL-302` („zufällig stimmen") müssen mit.
- `test_bl141::test_unbekanntes_modell_im_log_ist_kein_befund` pinnt
  `preise_nachrechnen(...) == []`. Die Rückgabeform halten, den Zähler für
  übersprungene Logs getrennt führen.
- Die Fixtures von `test_bl218` und `test_bl152` haben kein `usage`; der
  Intervall-Rückfall muss bleiben.
- `test_bl166` `SAETZE` um Sonnet 5.5 und Haiku 5.5 ergänzen.
- Nach dem Haiku-Eintrag warnt `modelle` bei Rollen auf `haiku-4-5`
  (Exit 3). Gewollt; `test_bl264` pinnt es nicht.
- Die Stubs aus `BL-326` haben kein `modelUsage` und dürfen im neuen Zähler
  nicht als „unbekanntes Modell" erscheinen.

**Tests:**

- (i) 1 Mio Cache-Read auf `claude-sonnet-5-5` kostet 0,10 USD.
- (ii) `modell_basispreis("claude-haiku-5-5")` liefert den Satz der
  Preisliste.
- (iii) Der Feldlauf als Zahlen — input 40, output 25374, cache_read
  2219224, 1h-Write 129479, `total_cost_usd` 0.9936584 — reproduziert sich.
  Heute nicht.
- (iv) Gattungstest: zehn Logs eines Modells, abgerechnet mit halbem
  Cache-Read-Satz, Cache-Read zehnmal Cache-Write → „Preistabelle stimmt
  nicht mehr" und Exit 2. Heute „✓ Preistabelle geeicht" und Exit 0.

## `BL-340` Teil A — zwei Sätze im Gegenlesen-Block

**Wo:** Gegenlesen-Block `rolle-architekt.md:344-357` (`BL-288`),
Gegenprobe `:348-349`. Der Reproducer darf nach `rolle-frank.md:15-21` auch
in einer Bestandsdatei liegen (`BL-216`). Mechanisch prüft das Kit nur, ob
er existiert (`team_reproducer_liegt_vor`, `bash/lib.sh:2041`,
`pwsh/lib.psm1:2029`); `beutebuch.py reproducer` (`:605-619`) verwirft den
`::Fall`-Teil (`DATEI_RE` `:100`).

**Bauen:** Zwei Sätze im Gegenlesen-Block. Die Gegenprobe gilt dem
Reproducer-Fall (Datei::Fall aus der Zeile „Reproducer-Test") und neuen
Fällen; ein angepasster Bestandstest darf vor dem Fix begründet grün sein.
Vor der Mutationsprobe muss die Suite am HEAD grün sein. `rolle-frank.md`
nicht anfassen (45 von 45).

**Fallen:** `test_bl219_abnahme_gegenlesen_zielstand.py:106-114` pinnt
„**Gegenprobe**", „**Mutationsprobe**", „Kit-BL-288" und „**jede** sichtbare
Zusage". `test_bl325_laufzeit_belege.py:132-143` pinnt „**Was ohne den
Menschen laufen kann, läuft ohne ihn:**"; die Regel-Zitate
`doku/regel-inventar.md:105-107` machen `kit-regelinventar.py` bei jeder
Umformulierung rot.

**Tests:** `test_bl219…::test_der_architekt_liest_mit_drei_proben_gegen`
erweitern: Das Briefing nennt den Reproducer-Fall als Gegenstand, den
begründet grünen Bestandstest und die grüne Suite am HEAD vor der
Mutationsprobe. Heute rot.

**Teil B, nicht bauen:** Eine Abnahme als Phase oder Rolle berührte eine
Phase nach Phase 4 (`vollautomatik.sh:473-562`, `.ps1:599-683`), den
Phasenzeiger, Allowlist und Whitelist, ein neues Briefing mit 45-Zeilen-Grenze,
die Rollenerkennung (`kosten.py:2314`), die Dateilisten der Installer,
`TEAM.md`, das Regel-Inventar und die Regel `rolle-architekt.md:384-387`
(`BL-325`). Erst eine Skizze, dann ein Entscheid des Owners.

## `BL-341` — gemessen wird auch nach dem letzten Fix

**Wo:**

- Franks Prompt: `bash/entry/frank.sh:110` (Smoke in Schritt 1),
  `:121-135` (Schritt 3, Doku im selben oder einem Folge-Commit),
  „Dreisatz verifiziert" `:192-210`; pwsh `frank.ps1:116`, `:127-142`,
  `:194-215`. Smoke-Text `bash/lib.sh:168`, `pwsh/lib.psm1:386`.
- Volle Suite am Phasenende: `vollautomatik.sh:316-341` (Bedingung `:322`,
  Logtext `:324`, Aufrufe `:427` und `:567`, Ende `:659-677`);
  `vollautomatik.ps1:421-444` (Bedingung `:426`, Logtext `:428`, Aufrufe
  `:528` und `:699`, Ende `:781-796`).
- Fixphase: `fixphase.sh:29`, `fixphase.ps1:35-38`.

**Bauen:**

- Beim Start der Fix-Phase den HEAD merken (nach `vollautomatik.sh:474`,
  `.ps1:597`). Am Ende (`:567`, `.ps1:699`) die volle Suite auch ohne
  `TEAM_SMOKE_TEST_SCHNELL` fahren, wenn `TEAM_SMOKE_TEST` gesetzt ist und
  sich der HEAD in der Fix-Phase bewegt hat. Rot setzt das Gate: Exit 44,
  die vorhandene Mechanik.
- Bedingung und Logtext anpassen (`:322`/`:324`, `.ps1:426`/`:428`): „die
  Stufen liefen mit …" stimmt ohne SCHNELL nicht.
- Den Parallellauf-Schutz `team_smoke_parallel_lauf` (`bash/lib.sh:1143`,
  `pwsh/lib.psm1:2090`) mitnehmen.
- Doku: `CLAUDE.md.vorlage:584-587`, die Kommentare in
  `team.config.sh:176-182` und `team.config.ps1` (erreichen nur
  Neuinstallationen, `BL-200`).
- Dazu die Prüfung aus `BL-327` aus `frank.*` und `ralph.*` rufen — siehe
  den Nachtrag in der Übergabe zu `BL-326`/`BL-327`.

**Fallen:**

- `test_bl232_verifikation_waechst_mit.py:185-191`
  (`ohne_schnellen_befehl_keine_zusatzrunde`, bash) bleibt mit der engen
  Fassung grün, weil der Stub nicht committet. Mit „immer" würde er rot.
- `test_bl232:162-183` schreibt „Volle Suite ROT am Ende der Bauphase" fest.
- `test_bl256:223-233` (Normalfall „Vollautomatik beendet.") bleibt
  unberührt; `:273-277` verlangt dieselben Merkmale auf beiden Bahnen.
- Wiederaufnahme in Phase 4 (`BL-217`): „HEAD seit Phasenstart" übersieht
  die Commits eines abgebrochenen Vorlaufs. Den Start-HEAD mit dem
  Phasenzeiger festhalten.

**Tests:**

- bash, Harness `_bash_projekt`: Der Frank-Stub committet beim ersten
  Aufruf `fix(uat): x (HM-1)` und `docs: y (HM-1)` und endet mit 0, danach
  mit 3. `TEAM_SMOKE_TEST=./voll.sh` endet mit 1, SCHNELL ist nicht gesetzt.
  `fixphase.sh` endet mit Exit 44 und „GATE ROT". Heute Exit 0.
- pwsh: derselbe Test über `_pwsh_projekt` und `frank.ps1`.
- Abgrenzung auf beiden Bahnen: Ohne Commit in der Fix-Phase läuft keine
  volle Suite. Den pwsh-Zwilling zu `test_bl232:185` gibt es heute nicht.

## `BL-342` — `beutebuch.py` und der Planordner

**Wo:** `geteilt/tools/beutebuch.py:89-90` (`BEUTEBUCH`, `ARCHIV`),
`_lies_zeilen` (`:132-136`, eine fehlende Datei ergibt eine leere Liste),
`--pfad` (`:559`). `TEAM_BEUTEBUCH_TOOL` in `team.config.sh:226` und
`team.config.ps1:202` übergibt keinen Pfad. Vorbild: `plan_ordner()` in
`kosten.py` (`BL-209`).

**Bauen:** `BEUTEBUCH` und `ARCHIV` aus `TEAM_PLAN_ORDNER` bilden, mit
Rückfall auf `plans`. Ein fehlendes Beutebuch laut melden statt leer zu
antworten. Der Bau entscheidet, ob als Fehler oder als Warnung — die Rollen
dürfen daran nicht brechen.

**Fallen:** `test_bl1…:51-52` pinnt `plans/beutebuch.md`; `test_bl1…:76-79`
überspringt sich in der Kit-Ablage. Nach `BL-328` sehen die Tests im
Harnisch den Rückfall `plans`. Tests für einen anderen Planordner setzen ihn
ausdrücklich.

**Tests:** In einer Installation mit Planordner `docs/plans` findet
`beutebuch.py list` einen dort eingetragenen Fund (heute leer), und
`test_bl324` (drei Fälle), `test_bl47` (zwei) und `test_bl114` (einer) sind
grün. Ein fehlendes Beutebuch wird gemeldet.

## `BL-343` — ein flackernder Kit-Test

**Wo:** `geteilt/tests/test_bl220_kaskadennummer_gegen_den_plan.py`,
Fixture `_repo` (`:57-78`): Commit des Plans in `:69`, das Log
`.team-logs/frank.json` danach in `:76`. Der Vergleich steht in
`logs_vor_kaskadenbeginn` (`kosten.py:1688-1703`, `mtime < beginn`);
`beginn` kommt aus `kaskade_beginn` (`:1643`, `git log --diff-filter=A
--format=%ct`, ganze Sekunden).

**Bauen:** In der Fixture die mtime des Logs ausdrücklich hinter den Commit
setzen (`os.utime`, Commit-Zeit plus eine Sekunde). Dann die Geschwister
suchen: jeder Test, der einen Plan committet und danach Logs für
`rollen-abschluss`, `kaskade_beginn` oder `logs_vor_kaskadenbeginn`
schreibt, beide Bahnen. Die Produktivlogik bleibt; im Betrieb liegen Minuten
zwischen Plan-Commit und Log.

**Fallen:** Nicht die Toleranz im Produktivvergleich aufweichen — ein Log aus
der Sekunde vor dem Plan-Commit gehört wirklich nicht zur Kaskade
(`BL-45`).

**Tests:** Die Fixture setzt die mtime des Logs ausdrücklich, und ein Fall
sichert das zu: Eine mtime eine Millisekunde vor der Commit-Sekunde wäre
ohne den Eingriff „älter". Gemessen auf der Linux-Maschine: Das Muster
„Zeit nehmen, dann Datei schreiben" lag in 366724 Versuchen 973-mal vor der
genommenen Sekunde. Der Rotfall selbst ist also selten; der Test macht die
Lage deterministisch, statt auf das Flackern zu warten.

---

## Nachweis auf der Bau-Maschine

- `bash bash/kit-test.sh` **und** `pwsh -File pwsh/kit-test.ps1`. Fast jeder
  Eintrag fasst beide Bahnen an, und die pwsh-Hälfte ist bei der Triage nie
  gefahren.
- Dazu `python3 -m pytest geteilt/tests -q` im Kit selbst. Die Tests der
  Kit-Werkzeuge laufen nur dort (`BL-307`).
- Jeder neue Test ist gegen den Stand vor seinem Fix **rot**.
- `CLAUDE*`-Variablen: Läuft die Suite aus einer Agentensitzung, erben die
  Tests `CLAUDECODE` und `CLAUDE_CODE_SESSION_ID`. Tests, die davon abhängen
  (`BL-330`, `BL-332`), setzen oder entfernen sie selbst.
- Die README-Zahlen nach allen Bauten an einer frischen Installation
  **messen**: Fälle, Testdateien, Dateien. Dann
  `python3 geteilt/kit-readme-pruefen.py --faelle N --testdateien N --dateien N`
  und `python3 geteilt/kit-regelinventar.py`.

## Danach

- Jeden Eintrag mit Begründung ins [Archiv](backlog-archiv.md) verschieben,
  Einträge in `CHANGELOG.md` unter `[Unreleased]` ergänzen und im README
  „Offen sind 20 Einträge" nachziehen. Der README-Wächter rechnet nach.
- `BL-340` Teil B bleibt offen, bis der Owner entschieden hat.
- Wird in Teilen gebaut, die erledigten Abschnitte hier streichen. Der
  letzte Bau-Commit löscht diese Datei und den Hinweis auf sie in
  `backlog.md`.
- Erst nach grünem Nachweis pushen.
- **Beifang, Doku:** Der README-Abschnitt „Grenzen" nennt `Feld F` und
  `Feld G` nicht, und „nur eine Kombination ist eingelaufen" stimmt seit
  `Feld F` (fünfzehn Kaskaden auf pwsh) nicht mehr. Beim Nachziehen der
  Zahlen mit erledigen.

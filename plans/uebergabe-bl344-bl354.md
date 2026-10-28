# Übergabe 2026-10-28 — `BL-344` bis `BL-354` bauen

**Bauauftrag.** Triagiert am 2026-10-28, diesmal auf der Windows-Maschine.
Gebaut wird weiter auf der Linux-Maschine (Entscheid des Owners vom
2026-10-18); die Windows-Maschine prüft danach mit
`pwsh -File pwsh/kit-test.ps1`. Die offene Übergabe
[`uebergabe-bl328-bl343.md`](uebergabe-bl328-bl343.md) (Wellen 2 bis 5) gilt
daneben weiter. Diese Datei ist der Auftrag für die elf neuen Einträge. Der
letzte Bau-Commit löscht sie; als Beleg bleiben Archiv, CHANGELOG und Commits.

## Stand beim Pull

- **Triage:** `BL-344` bis `BL-354` stehen in [`backlog.md`](backlog.md), je
  mit Hergang, Meldung, Befund der Triage und den Vorschlägen. Neu ist das
  Feldkürzel `Feld H` (README, Abschnitt Herkunft). Das README nennt
  24 offene Einträge, die höchste Nummer ist `BL-354`.
- **Wie geprüft:** Jede Meldung am Code beider Bahnen, auf Windows 11 mit Git
  Bash und pwsh 7 nebeneinander. **Gefahren**, nicht nur gelesen: `BL-349` und
  `BL-350` in einer Wegwerf-Installation mit beiden Bahnen; `BL-344` und
  `BL-346` synthetisch am Kit-Werkzeug; `BL-345` und `BL-347` waren am
  2026-10-26 auf dieser Maschine nachgestellt (Code seither unverändert);
  `BL-353` an der laufenden Sitzung gemessen. Aus dem Quelltext hergeleitet
  und nicht gefahren sind nur die bash-Hälfte von `BL-348` und der
  Halb-Fehlschlag von `--rollen-abschluss` in `BL-349`.
- **Zeilennummern** gelten für `bbb6efb`. Nach den Bauten aus der anderen
  Übergabe verschieben sie sich; die Funktionsnamen bleiben.
- Die Probeskripte der Triage lagen im Sitzungsordner der Windows-Maschine und
  kommen nicht mit. Was sie zusichern, steht je Eintrag unter **Tests**.

## Reihenfolge

| Welle | Einträge | Warum so |
|---|---|---|
| A | `BL-346`, `BL-345` | beide `smoke_warten.py`, klein, ohne Entscheidung. `Feld B` hält den Umstieg auf den Zwei-Schritt-Weg zurück, bis beide gebaut sind |
| B | `BL-349`, `BL-350` | beide `team-status.ps1`, nur pwsh — auf der Bau-Maschine blind geschrieben, Nachweis auf Windows |
| C | `BL-347`, `BL-348` | Testharnisch und Selbsttests. Danach ist `kit-test.ps1` auf Windows wieder ein Signal |
| D | `BL-344` | `kit_basis.py`, nach der Entscheidung über die Variante |
| E | `BL-351`, `BL-353` | Regeltexte. Franks Teil von `BL-351` zusammen mit `BL-335` (Welle 4 der anderen Übergabe): Beide fassen denselben Absatz an, und Frank steht auf der 45-Zeilen-Grenze |
| — | `BL-352`, `BL-354` | **nicht bauen:** erst eine Skizze in `roadmap-skizzen.md`, Entscheidung des Owners |

Größen: S sind `BL-345`, `BL-346`, `BL-347`, `BL-348` und `BL-350`. M sind
`BL-344` und `BL-349`. `BL-351` ist als Regeltext S, mit mechanischer
Gegenprobe L; `BL-353` als Satz S, mit Werkzeug M.

## Fragen an den Owner

Der Bau fragt zu Beginn nach diesen Punkten. Daneben steht die Empfehlung der
Triage. Alles, was hier nicht steht, ist ohne Entscheidung baubar.

| Eintrag | Frage | Empfehlung der Triage |
|---|---|---|
| `BL-344` | Ausstehende Basis mechanisch übernehmen, oder nur ein Hinweis auf `kit_basis.py schreiben --claude`? | mechanisch mit den drei Kriterien unten, der Hinweis zusätzlich |
| `BL-348` | `kit-test.sh` nach einem roten Schritt 2 weiterfahren wie `kit-test.ps1`? | ja |
| `BL-351` | Wer entscheidet über einen vertragsändernden Fund? Wird „Verträge" ein fester Planabschnitt? Wird Franks Gegenprobe Mechanik? | der Architekt; ja; die Mechanik als eigener Schritt nach `BL-335` |
| `BL-353` | Nur der Satz in der Verifikationskette, oder auch ein Werkzeug? | beides — das Werkzeug ruft die Vollautomatik am Ende, statt einen weiteren Satz in den Closeout zu schreiben |
| `BL-352`, `BL-354` | Welche Ebene zuerst? Betrifft „nur ausdrücklich" auch den heutigen Rückfall vom Abo auf die API? | erst die Skizze |

---

## `BL-346` — `warten` ohne Kennung

**Wo:** `geteilt/tools/smoke_warten.py:114-116` (`_juengster`), `warten`
`:119-144`. Der Nachsatz der Rollen in `bash/lib.sh:133` und
`pwsh/lib.psm1:350`.

**Bauen:**

- `_juengster()` nimmt nur Namen im eigenen Format
  `smoke-\d{8}-\d{6}-\d{6}\.log`. Im eigenen Format ist die Namensordnung die
  Zeitordnung; die Änderungszeit taugt nicht, ein fremdes Log kann jünger sein.
- Der Nachsatz beider Bahnen nennt `warten <kennung>` und sagt, woher die
  Kennung kommt: `start` druckt sie als erste Zeile auf stdout.

**Fallen:**

- Die Briefings `rolle-{axel,harry,marv,ralph}.md` nennen „`… warten` im
  VORDERGRUND bis nicht 75" und stehen auf der 45-Zeilen-Grenze. Dort nichts
  ergänzen; der Nachsatz trägt die Kennung.
- Beide Nachsätze gleich halten — `test_bl112` und `test_bl117` halten die
  Prompts der Bahnen gegeneinander.

**Tests:**

- Ein leerer `smoke-stufe158-1790169213.log` ohne `.rc` neben einem frischen
  `start`: `warten` ohne Kennung findet den eigenen Lauf und endet mit dessen
  Exit-Code. Gegen den alten Stand: 75 mit der fremden Kennung (so
  nachgestellt).
- Nur fremde Logs: `warten` meldet „kein Smoke-Lauf gefunden" (Exit 2) statt 75.

## `BL-345` — `cmd.exe` und der Schrägstrich

**Wo:** `smoke_warten.py:62-75` (`_lauf`, `shell=True` in `:66`); `_teile`
`:167-175` zerlegt Windows-gerecht, aber nur für `umgebung`.

**Bauen:**

- Eine reine Funktion, die unter Windows den ersten Token normalisiert: nur
  wenn er ungequotet ist und einen Schrägstrich trägt, wird er mit
  Rückstrichen geschrieben. Alles andere bleibt Zeichen für Zeichen, wie es
  war. `_lauf` fährt das Ergebnis.
- Die Funktion bekommt das Betriebssystem als Parameter, damit ihr Kern auf
  der Bau-Maschine testbar ist.

**Fallen:**

- Am Rohtext des ersten Tokens arbeiten, nicht am Ergebnis von `_teile`: Das
  entfernt Anführungszeichen, und ein gequoteter Pfad muss unberührt bleiben.
- `python -m pytest …`, `uv run pytest`, `"C:/…/python.exe" …` und
  `.venv\Scripts\python.exe` bleiben unverändert.
- `shell=True` bleibt: `TEAM_SMOKE_TEST` darf Shell-Syntax tragen.

**Tests:**

- Reine Funktion, auf allen Plattformen: die drei Schreibweisen aus der
  Meldung und die unveränderlichen Fälle oben.
- Ein Windows-Fall (sonst `skip`) mit echtem `start` und `warten`: Ein `.cmd`
  im Unterordner reicht, `sub/probe.cmd` mit `@exit /b 0`, aufgerufen als
  `sub/probe.cmd` ohne Anführungszeichen. Gegen den alten Stand Exit 1 mit
  „'sub' is not recognized …" (bei der Triage gemessen), nach dem Fix 0.

## `BL-349` — die stumme Buchung

**Wo:** `pwsh/entry/team-status.ps1`, Verteiler `:569-579`;
`Status-ArchitektAbschluss` `:307-339` (`Team-Werkzeug` in `:337`);
`Status-AkteurAbschluss` `:341-371`, das `team_akteur_abschluss` ruft
(`pwsh/lib.psm1:1004`, nur von hier); `Status-RollenAbschluss` `:373-478`,
die beiden Buchungen in `:473-477`. `Team-Werkzeug` steht in
`pwsh/lib.psm1:198-211`.

**Bauen:** Die drei Buchungswege geben die Ausgabe des Werkzeugs zeilenweise
über `[Console]::Out.WriteLine` aus und liefern nur `$LASTEXITCODE` zurück —
so wie `Status-Hilfe` und `Status-Altlast` es schon tun. Für
`team_akteur_abschluss` dasselbe.

**Fallen:**

- pwsh ist auf der Bau-Maschine nicht installiert: blind schreiben, auf
  Windows nachweisen. Jeder neue Test überspringt ohne pwsh **und** in einer
  einbahnigen Ablage ohne `team-status.ps1` — genau dieser Ausrutscher hat
  laut Backlog schon einmal eine Runde gekostet.
- Nicht `Out-Host`: Es schreibt an einer Umleitung vorbei, und die Tests
  lesen stdout.
- `$LASTEXITCODE` direkt nach dem Werkzeug sichern, bevor ein anderer Aufruf
  ihn überschreibt.
- stderr bleibt, wie es ist — der Fehlerweg kommt heute schon durch.

**Tests (pwsh):**

- `--architekt-abschluss` und `--akteur-abschluss` drucken „… angelegt: …
  (abo)" und den Hinweis aus `BL-252`. Heute rot: keine Ausgabe.
- Ein `TEAM_KOSTEN_TOOL` als Attrappe, das eine Zeile auf stdout schreibt und
  mit 3 endet: Der Wrapper endet mit 3. Heute 0 (bei der Triage gemessen).
- `--rollen-abschluss` mit einer Attrappe, die beide `--nur-pruefen` und
  `rollen-abschluss` besteht und `ralph-abschluss` mit 1 ablehnt: Exit 1.
  Heute hergeleitet 0.
- `test_bl143::test_die_meldung_nennt_die_achse` zusätzlich über den
  pwsh-Wrapper fahren — die Zusicherung aus `BL-143` galt bisher nur dem
  Werkzeug.

## `BL-350` — das `#>` im Kommentar

**Wo:** `team-status.ps1:531-536`, das zitierte `#>` in `:534`. Der Wächter
ist `geteilt/tests/test_bl229_pwsh_dateien_parsen.py`.

**Bauen:**

- Den Satz ohne Endezeichen schreiben, etwa „zwischen den Kommentarmarken am
  Dateianfang".
- Den Wächter um die Gattung erweitern: Hinter dem schließenden `#>` eines
  Blockkommentars steht auf derselben Zeile nichts mehr. Geprüft am
  Tokenstrom des Parsers (`[System.Management.Automation.Language.Parser]`),
  den der Wächter ohnehin in pwsh fährt — nicht per Textsuche.

**Fallen:** Einzeilige Blöcke wie `<# BL-147: … #>` (`pwsh/install.ps1:202`)
sind korrekt und müssen durchgehen. Zeilenkommentare wie
`# <# … #>-Block …` (`install.ps1:120`) sind keine Blockkommentare.

**Tests:** `--hilfe` druckt nichts auf stderr (pwsh). Die Gegenprobe des
Wächters: eine synthetische Datei mit einem Kommentar wie in `:534` wird rot.

## `BL-347` — der Testharnisch von `test_bl326`

**Wo:** `geteilt/tests/test_bl326_abgebrochener_rollenaufruf.py:270-278`
(`_abschiessen`); die Attrappe `_attrappe` `:183-201` (`sleep 60` in `:201`);
`_starte` `:295`.

**Bauen:** Unter Windows nach `taskkill /F /T`: `proc.wait(timeout=30)`,
danach `stdout` und `stderr` schließen, statt mit
`communicate(timeout=30)` auf das Ende der Pipes zu warten. Der Linux-Zweig
bleibt. Ein Kommentar an der Stelle: `taskkill /T` erreicht keine MSYS-Enkel
(Fork-Nachbildung, tote Eltern-PID) — für den nächsten Test, der unter Windows
einen Baum mit Git Bash beendet.

**Fallen:** Auf Linux nicht nachweisbar, dort ist der Fall grün. Nachweis ist
`kit-test.ps1` auf der Windows-Maschine: vorher 2 failed in der Datei, danach
29 passed (so in einer Kopie belegt).

## `BL-348` — Schritt 2 der Selbsttests

**Wo:** `bash/kit-test.sh:245-257`, `pwsh/kit-test.ps1:240-241`. Die drei
Zeilen der Installer: `bash/install.sh:2251`, `:2253`, `:2257` und
`pwsh/install.ps1:2317`, `:2319`, `:2324`.

**Bauen:** An den drei Zeilen der Installer unterscheiden, nicht an pytest —
sie sind die Schnittstelle, die `BL-127` prüft:

- „Regressionstests grün" — grün wie heute.
- „nicht vollständig grün" — rot mit der Meldung „gefahren, aber rot" und den
  `FAILED`-Zeilen aus dem Installer-Log.
- „übersprungen" oder keine der drei Zeilen — der `BL-127`-Fall, Text wie
  heute.

Ob `kit-test.sh` danach weiterfährt, entscheidet der Owner.

**Tests:** Textwächter nach dem Muster von `test_bl127`: Beide Selbsttests
kennen die Zeile „nicht vollständig grün" und unterscheiden sie von
„übersprungen".

## `BL-344` — die ausstehende Basis

**Wo:** `geteilt/tools/kit_basis.py:343-414` (`claude`), der Konfliktweg ab
`:390`, die geschätzte Basis in `:398-399`; `dreiwege` `:266-283`; der
Docstring `:33-35`. Aufgerufen aus `bash/install.sh:1498-1507` und
`pwsh/install.ps1:1728`.

**Bauen (Empfehlung der Triage):**

- Bei Exit 10 legt `claude()` die gerenderte Kit-Fassung als
  `team/.kit-basis/CLAUDE.md.ausstehend` ab und merkt sich den Stand der
  CLAUDE.md zum Zeitpunkt des Vorschlags (Prüfsumme).
- Beim nächsten Lauf, vor dem Abgleich: Liegt eine ausstehende Fassung vor,
  wird sie Basis, wenn **alle drei** gelten — die CLAUDE.md ist seit dem
  Vorschlag geändert; sie trägt keine Konfliktmarken; der Dreiwege-Abgleich
  aus jetziger CLAUDE.md, alter Basis und ausstehender Fassung mit
  `git merge-file --ours` ergibt die CLAUDE.md unverändert. Das dritte
  Kriterium heißt: Jede Änderung der ausstehenden Fassung ist übernommen oder
  bewusst anders. Danach läuft der Abgleich wie heute.
- Gilt eins nicht, bleibt alles wie heute: Basis stehen lassen, erneut
  vorschlagen.
- Der Installer nennt zusätzlich `kit_basis.py schreiben --claude …` als Weg
  von Hand.

**Fallen:**

- Ohne das dritte Kriterium gälte eine aus anderem Grund bearbeitete
  CLAUDE.md als Übernahme. Die neuen Regeln fielen dann beim nächsten Abgleich
  als „bewusst entfernt" heraus — genau was der Docstring verhindern will.
- Randfall: Löst der Mensch jeden Konflikt zugunsten des Projekts auf und gab
  es keine konfliktfreie Änderung, ist die CLAUDE.md unverändert, und das
  erste Kriterium hält die Übernahme zurück. Das ist der heutige Zustand,
  kein neuer Fehler.
- `lesen()` liefert Text, BOM und Zeilenende getrennt. Verglichen wird der
  Text, sonst schlägt CRLF an.

**Tests:** Der Fall der Triage, als Test: Basis B0; das Kit ändert Regel 2,
das Projekt formuliert sie eigen; aufgelöst zugunsten des Projekts und
übernommen; das nächste Kit bringt nur eine neue Regel 4. Nach dem Fix: Exit 0,
Regel 4 eingearbeitet, die eigene Regel 2 bleibt. Heute: Exit 10, eine
Konfliktstelle, Datei unverändert. Gegenfall: Die CLAUDE.md wird nach dem
Vorschlag nur an anderer Stelle geändert, die konfliktfreie Änderung fehlt —
die Basis bleibt, der Vorschlag kommt wieder.

## `BL-351` — Vertragswerte und Franks Gegenprobe

**Wo:** `bootstrap/CLAUDE.md.vorlage:190-215` (Beutezug-Dreisatz, Punkt 3,
der Absatz zu `Kit-BL-289` ab `:207`) und `:229-240` (Ausschlusskriterium).
Im Regel-Inventar `doku/regel-inventar.md:90`. Frank:
`geteilt/prompts/rolle-frank.md:19-20` (Gegenprobe) und `:35-41` (zentrale
Werte); Schritt 0 in `bash/entry/frank.sh:125-129` und
`pwsh/entry/frank.ps1:132-136`. Die Prüfung nach dem Lauf:
`team_reproducer_liegt_vor` in `bash/lib.sh:2219-2238` und
`pwsh/lib.psm1:2029`.

**Bauen — Regeltext, Vorschlag der Triage:**

- Punkt 3, ein Absatz nach dem zu `Kit-BL-289`: *„Dasselbe gilt für das
  Verhalten eines Fremdsystems, das der Plan gemessen hat (`Kit-BL-351`):
  Behauptet ein Fund, was ein Server, ein Gerät oder ein Dienst tut, den im
  Loop niemand starten darf, und nennt der Plan dazu eine Messung, zitiert der
  Fund die Planstelle und sagt, warum die Messung nicht trägt."*
- Ausschlusskriterium, ein zweiter Fall: *„Ebenso nicht an Frank geht ein
  Fund, dessen Erwartung einen Wert aus den Verträgen des Plans umstellt
  (Grenze, Konstante, Exit-Code, Format). Er geht an den Architekten; der
  entscheidet die Richtung, wenn nötig mit dem Stakeholder, und übergibt
  dann."*
- Frank, zeilenneutral: Stellt sein Fix einen Wert um, den der Plan festlegt,
  nennt der Commit-Text die Planstelle. Ist der Test schon ohne den Fix grün,
  fixt er nicht; die Prämisse geht zurück an den Architekten.

**Fallen:**

- `rolle-frank.md`, `rolle-harry.md` und `rolle-marv.md` stehen auf genau
  45 Zeilen (`test_stufe90_briefings.py`). Die einzige Reserve bei Frank ist
  die Zeile, die `BL-335` mit seiner Sechszeilen-Fassung freigibt — darum
  beide zusammen. Die Prüfmarken aus `test_bl49`, `test_bl219` und
  `test_stufe90` gelten weiter (Liste in der anderen Übergabe bei `BL-335`).
- Jede neue Regel bekommt eine NORM-Zeile im Regel-Inventar;
  `kit-regelinventar.py` prüft wörtlich. Schreibweise `Kit-BL-351` in der
  Vorlage, sonst schlägt `test_bl140` an.
- „Verträge" ist heute kein fester Planabschnitt; das Kit kennt den Begriff
  nur als Planungsfrage (`rolle-architekt.md:110`). Hängt am Owner.
- Die mechanische Gegenprobe (das Kit fährt Franks neuen Test gegen den
  Elternstand) ist ein Bau am geldausgebenden Pfad. Nicht in diesem Zug,
  sondern nach der Entscheidung als eigener Schritt.

**Tests:** Textwächter: Punkt 3 nennt das Fremdsystem und die Planstelle;
das Ausschlusskriterium nennt die Verträge des Plans; Franks Briefing nennt
die Planstelle im Commit-Text. Je eine Inventarzeile.

## `BL-353` — die Konsole gehört zur Umgebung

**Wo:** `bootstrap/CLAUDE.md.vorlage:26-43` (Verifikationskette), im
Regel-Inventar `doku/regel-inventar.md:54`. Der Zwei-Schritt-Weg startet die
Suite in `smoke_warten.py:97-104` mit `DETACHED_PROCESS` und
`CREATE_NEW_PROCESS_GROUP`.

**Was gemessen ist:** In der laufenden Sitzung hatte `claude.exe` selbst
Strg+C eingeschaltet. Im Baum des Bash-Werkzeugs war es ab dem ersten
`bash.exe` von Git abgeschaltet, und alles darunter erbte es. Im Baum des
PowerShell-Werkzeugs (`cmd.exe` → `pwsh.exe`) war es eingeschaltet; unter
einem Git Bash, aus diesem pwsh gestartet, war es wieder abgeschaltet. Die
Marke kommt also mit Git Bash. Gelesen wurde rein lesend das Bit 0 von
`ConsoleFlags` in den Prozessparametern jedes Prozesses der Kette.

**Bauen:**

- Ein Satz in der Verifikationskette mit NORM-Zeile: Auch was die Sitzung
  vererbt, gehört zur Umgebung — unter Windows erbt jeder Befehl aus dem
  Bash-Werkzeug eine Konsole mit abgeschaltetem Strg+C, das Terminal des
  Menschen hat es eingeschaltet.
- Falls der Owner das Werkzeug will: unter Windows den Smoke-Test einmal in
  einer neuen, verborgenen Konsole mit eingeschaltetem Strg+C fahren
  (`CREATE_NEW_CONSOLE`, im Kind `SetConsoleCtrlHandler(NULL, FALSE)` vor dem
  Start) und den Exit-Code melden. Die Vollautomatik ruft es am Ende einmal;
  auf anderen Plattformen tut es nichts.

**Fallen:**

- Nicht in den Zwei-Schritt-Weg einbauen: Dort läuft die Suite ohne Konsole,
  eine Konsolenprobe ist da sinnlos.
- Nur auf Windows nachweisbar. Für den Test genügt ein Python-Kind, das sich
  selbst `GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0)` schickt und abbricht,
  wenn Strg+C eingeschaltet ist. **Nur in einer eigenen, neuen Konsole** —
  nie in der Konsole der laufenden Sitzung: Das Ereignis erreicht jeden
  Prozess dieser Konsole, und die CLI selbst hat Strg+C eingeschaltet.

## `BL-352`, `BL-354` — nicht bauen, erst eine Skizze

Die Skizze trägt beide Einträge zusammen: die drei Ebenen der Wahl (Vorgabe je
Rolle, je Stufe im Plan, auf Zuruf), die Programm-Stufe als Ebene „je Stufe",
„entfernt nur ausdrücklich", das Einrichtungsskript je Anbieter, die
Kosteneinheit aus `BL-247` Punkt 4, eine Phase ohne Modell aus `BL-340`
Teil B und das Verhältnis zu Skizze F. Bis dahin ist aus `BL-352` nur Doku
fällig: Für die dritte Naht genügt ein Muster in `TEAM_PLAN_ORDNER_BESTAND`
(etwa `*/stufe-*/tests/*`). Es nennt die Abnahmequellen im Prompt der
Read-Only-Rollen als fremdes Eigentum und macht den Hinweis aus
`schreibzone.py` stumm; eine Guard-Sperre bräuchte eine Entscheidung gegen
`BL-51`.

---

## Nachweis

- Auf der Bau-Maschine: `bash bash/kit-test.sh` und
  `python3 -m pytest geteilt/tests -q` im Kit selbst.
- Auf der Windows-Maschine danach: `pwsh -File pwsh/kit-test.ps1` aus einer
  bereinigten Umgebung (ohne `CLAUDE*`, `TEAM_*`,
  `PSExecutionPolicyPreference`). Erst dort sind `BL-345`, `BL-347`, `BL-349`,
  `BL-350`, `BL-353` und die pwsh-Hälfte von `BL-348` belegt.
- Jeder neue Test ist gegen den Stand vor seinem Fix **rot**.
- Die README-Zahlen nach allen Bauten an einer frischen Installation messen,
  dann `python3 geteilt/kit-readme-pruefen.py --faelle N --testdateien N
  --dateien N` und `python3 geteilt/kit-regelinventar.py`.

## Danach

- Jeden Eintrag mit Begründung ins [Archiv](backlog-archiv.md) verschieben,
  `CHANGELOG.md` unter `[Unreleased]` ergänzen und im README die Zahl der
  offenen Einträge nachziehen. Der README-Wächter rechnet nach.
- `BL-352` und `BL-354` bleiben offen, bis die Skizze steht und der Owner
  entschieden hat.
- Wird in Teilen gebaut, die erledigten Abschnitte hier streichen. Der letzte
  Bau-Commit löscht diese Datei und den Hinweis auf sie in `backlog.md`.
- Erst nach grünem Nachweis pushen.

# Übergabe 2026-10-12 — `BL-326` und `BL-327` bauen

**Für die Bau-Maschine.** Auftrag des Owners vom 2026-10-12: Auf der
Linux-Maschine ist nur triagiert. Gebaut und nachgewiesen wird auf der
Bau-Maschine, weil die vollen Nachweisläufe viel Rechenzeit brauchen. Diese
Datei ist der Auftrag. Der Bau-Commit löscht sie wieder; als Beleg bleiben
Archiv, CHANGELOG und Commit.

## Stand beim Pull

- **Triage:** `BL-326` und `BL-327` stehen in [`backlog.md`](backlog.md), mit
  Hergang, Meldung und den Vorschlägen der Meldungen. Das README nennt 4 offene
  Einträge, die höchste Nummer ist `BL-327`.
- **Beifang:** `test_bl307::test_die_alterung_greift` war seit `4de27dc`
  (Welle 1, `BL-323`) auf master rot. Die Testkonfiguration hatte keine
  `TEAM_PREISE`-Zeile, und das Alterungswerkzeug verlangt sie seither. Die
  Zeile ist jetzt ergänzt. Der Test prüft außerdem, dass die Alterung die Preise
  tatsächlich gesetzt hat; die Mutationsprobe dazu schlägt an.
- **Auf der Linux-Maschine geprüft:** Kit-Suite mit 1708 passed und
  1 failed (`test_bl173`, ein bekannter Umgebungsfall dort). In einer frischen
  Installation ist die Suite grün mit 1263 passed. Die README-Zahlen sind
  gemessen: 2010 Fälle, 200 Testdateien, 265 installierte Dateien.
- **Nicht geprüft:** Die pwsh-Bahn ist dort nicht installiert, 128 Fälle
  wurden übersprungen. `kit-test.sh` und `kit-test.ps1` liefen nicht.

## Zuerst: die Falle aus `BL-327`

Code mit Backslashes schreibst du **nur mit dem Werkzeug zum Bearbeiten von
Dateien**. Das gilt für reguläre Ausdrücke, Pfade und Escape-Tabellen. Nicht
über einen Heredoc, nicht über `python -c` und nicht über einen nicht rohen
String. Das Kit hat es schon selbst getroffen: Im Archiv, Eintrag `BL-234`,
steht zweimal 0x08, wo `\b` stehen sollte. Für `BL-327` schreibst du genau
solche Muster (`[\x00-\x08…]`, `\r(?!\n)`).

## `BL-326` — Stub vor dem Aufruf, Sichten beim Wiederanlauf

**Wo:**

- bash: `team_claude` (`bash/lib.sh:712`). Der Aufruf `… > "$out"` steht in
  `:747`, der API-Fallback in `:823`, `:856` und `:858`. Danach schreibt
  `team_versuch_melden` (`:661`) über `team_versuch_sichern` (`:634`) den
  Ersatzzettel aus `BL-46`, aber erst **nach** dem Aufruf.
- pwsh: `team_claude` (`pwsh/lib.psm1:2441`) ruft `Team-ClaudeSchreiben`
  (`:2365`) auf, und das schreibt erst nach dem Ende der CLI.
  `team_versuch_sichern` und `team_versuch_melden` stehen bei `:864` und `:891`.
- `geteilt/tools/kosten.py`: `_datei_kosten`, `_ist_verworfener_versuch`,
  `verworfene_versuche` und `verworfen_hinweis` (`BL-46`).
- Guard: `team_guard_begin` (`bash/lib.sh:1473`, `pwsh/lib.psm1:1594`) warnt bei
  schmutzigem Arbeitsbaum nur.

**Bauen:**

1. **Stub vor jedem CLI-Aufruf, auch vor dem API-Fallback.** Der Stub ist der
   Ersatzzettel aus `BL-46`, nur vorab geschrieben. Er trägt
   `team_versuch: "abgebrochen"`, die Rolle, den Start und eine
   Sitzungskennung. Dieselbe Kennung geht als `--session-id <uuid>` an die CLI.
   Die CLI nimmt die Option an; das ist auf der Linux-Maschine nachgesehen. Kein
   Aufrufer übergibt `--resume` oder `--continue`. Das Ende des Aufrufs
   überschreibt den Stub.
   - **Falle bash:** `> "$out"` leert den Stub, sobald die CLI startet. Die
     Ausgabe muss deshalb erst in eine Nebendatei und danach per `mv` auf
     `$out`.
   - Eine UUID ohne `uuidgen` (Git Bash) erzeugst du über `$TEAM_PYTHON`, in pwsh
     mit `[guid]::NewGuid()`.
   - `kosten.py` zählt `abgebrochen` wie `verworfen`: Die Kosten sind
     UNBEKANNT, niemals 0.0. Der Hinweis nennt die Sitzungskennung und den
     Befehl, mit dem sie sich messen lässt (`kosten.py sitzung-messen`). Aus der
     Meldung: Eine Buchung ohne Rohlog ließe `--ledger-pruefen` dauerhaft
     warnen. Mit dem Stub gibt es dieses Rohlog.
2. **Wiederanlauf.** Vor dem ersten Rollenaufruf eines Laufs prüfen: Liegt ein
   Stub `abgebrochen` vor **und** ist der Arbeitsbaum schmutzig, dann nennt der
   Lauf Rolle, Sitzung und Pfade und hält mit Exit 42 an. Das ist die Semantik
   der Pause: Der State bleibt stehen, der Mensch committet oder verwirft und
   startet dieselbe Zeile neu. Bei sauberem Arbeitsbaum läuft er weiter, und der
   Stub bleibt als Kostenlücke im Bericht. Ein alter Stub darf **höchstens
   einmal** anhalten. Wie der Vermerk „gesichtet" aussieht, entscheidet der Bau.
3. **Tests auf beiden Bahnen:** Ein abgebrochener Aufruf (Attrappe der CLI, die
   schläft, und dann den Wrapper abschießen) hinterlässt einen Stub mit
   Kennung. `kosten.py` nennt ihn als unbekannt und nicht als 0. Ein
   Wiederanlauf mit Stub und schmutzigem Baum endet mit Exit 42, ein
   Wiederanlauf mit sauberem Baum läuft weiter. Jeder Test muss gegen den alten
   Stand **rot** sein.

## `BL-327` — Steuerzeichen-Prüfung im Guard, ein Satz im Briefing

**Wo:**

- `team_guard_verify` (`bash/lib.sh:1897`, `pwsh/lib.psm1:1906`) kennt die
  geänderten Pfade der Rolle.
- `geteilt/prompts/rolle-ralph.md` und `rolle-frank.md` haben **beide schon
  45 Zeilen, also genau das Limit** (`test_stufe90_briefings.py`). Ein neuer Satz
  muss deshalb gegen eine Straffung an anderer Stelle getauscht werden, wie bei
  `BL-215` und `BL-216`. Die neue Regel kommt nach `doku/regel-inventar.md`;
  `kit-regelinventar.py` meldet, wenn eine Regel wegfällt.

**Bauen:**

1. **Eine Prüfung für beide Bahnen**, als Python-Werkzeug unter
   `geteilt/tools/`, so wie `kosten.py`. Regel: Bytes unter 0x20 sind
   verboten, außer Tab (0x09) und LF (0x0A). CR (0x0D) ist nur direkt vor einem
   LF erlaubt, am Dateiende also nicht allein. Ausgabe: Datei:Zeile, das Byte
   und das wahrscheinliche Escape (0x08 aus `\b`, 0x0C aus `\f`, 0x0B aus `\v`,
   0x07 aus `\a`, 0x0D aus `\r`).
   - **Binär** heißt: ein NUL in den ersten 8000 Bytes, wie git es zählt.
     **Nicht** `git ls-files --eol` nehmen: Ein einzelnes CR macht dort die
     Datei zu `-text`, und genau dieser Fall soll gefunden werden.
   - **Blinder Fleck, benennen und nicht wegdiskutieren:** Ein `\t`, das zum
     Tabulator wurde, und ein `\n`, das zum Zeilenumbruch wurde, sieht die Regel
     nicht, weil beide Zeichen erlaubt sind. Dagegen hilft nur der Satz im
     Briefing.
   - Fixtures, die absichtlich Steuerzeichen enthalten, brauchen einen
     ausdrücklichen Ausweg. Der Bau entscheidet, welchen.
2. **Der Guard ruft die Prüfung** für die geänderten Textdateien der Rolle auf,
   auf beiden Bahnen. Ein Fund macht den Schritt rot und nennt Datei und Zeile.
   **Kein Rollback**, denn die Arbeit ist reparierbar. Eine bloße Warnung
   reicht aber auch nicht. Der Satz im Briefing von Ralph und Frank nennt beides:
   Backslash-Code mit dem Bearbeiten-Werkzeug schreiben, und vor dem Commit das
   Werkzeug über die geänderten Dateien laufen lassen.
3. **Ein Kit-Test über die eigenen versionierten Dateien.** Er ist zuerst rot an
   `plans/backlog-archiv.md`, Zeile 83, Eintrag `BL-234`: Dort stehen seit
   `0373347` zwei 0x08 in `REFERENZ_RE`. Danach diese zwei Bytes zu `\b`
   reparieren, mit dem Bearbeiten-Werkzeug.
4. **Tests auf beiden Bahnen:** Der Guard findet 0x08 in einer geänderten
   Testdatei und nennt Datei und Zeile. Eine CRLF-Datei geht durch. Ein
   einzelnes CR wird gefunden, mitten im Text und am Dateiende. Eine Binärdatei
   wird übersprungen. Gegenprobe: Jeder Test ist gegen den alten Stand rot.

## Nachweis auf der Bau-Maschine

- `bash bash/kit-test.sh` **und** `pwsh -File pwsh/kit-test.ps1`. Beide
  Bibliotheken werden angefasst, also zählt keine Bahn als „gleich gebaut".
- **Dazu `python3 -m pytest geteilt/tests -q` im Kit selbst.** `kit-test.sh`
  fährt nur `team/tests` in einer Installation, und dort werden die Tests der
  Kit-Werkzeuge übersprungen („liegt nur im Kit"). Auf diesem Weg ist
  `test_bl307` seit `4de27dc` rot geblieben.
- Die README-Zahlen nach dem Bau an einer frischen Installation **messen**,
  nicht rechnen: Fälle, Testdateien, Dateien. Dann
  `python3 geteilt/kit-readme-pruefen.py --faelle N --testdateien N --dateien N`
  und `python3 geteilt/kit-regelinventar.py` ausführen.

## Danach

- `BL-326` und `BL-327` mit Begründung ins [Archiv](backlog-archiv.md)
  verschieben. Einträge in `CHANGELOG.md` unter `[Unreleased]` ergänzen.
- Im README „Offen sind 4 Einträge" nachziehen. Der README-Wächter rechnet
  nach.
- Diese Datei im Bau-Commit löschen und den Hinweis auf sie in `backlog.md`
  entfernen.
- Erst nach grünem Nachweis pushen.

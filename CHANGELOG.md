# Changelog — T.E.A.M.-Starterkit

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Added

- **BL-112 — ein Test, der meldet, wenn die beiden Zweige verschiedene Agenten
  steuern.** Die Rollen-Briefings sind single-source (`team_briefing` liest
  `team/prompts/rolle-*.md`), der **zusammengesetzte** Prompt war es nicht: Er
  entsteht erst im Einstiegsskript und stand seit der Portierung zweimal im
  Repo — einmal `.sh`, einmal `.ps1`. Wer eine Feldlehre nachschärft und nur
  eine Fassung anfasst, bekommt zwei Zweige, die verschiedene Agenten steuern;
  kein Test schlug an, weil beide Zweige grün laufen.

  [`team/tests/test_bl112_prompt_gleichstand.py`](geteilt/tests/test_bl112_prompt_gleichstand.py)
  zieht den Prompt-Quelltext aus beiden Zweigen, rechnet die Syntax heraus
  (jede Variableneinsetzung wird **ein** Platzhalter) und vergleicht die
  verbleibende Prosa zeichenweise — vier Prompt-Blöcke und fünf
  Prosa-Variablen, darunter `SMOKE_ZEILE` aus der **Bibliothek**, die der
  Befund nicht im Blick hatte. Stand beim Bau: noch keine Drift, alle neun
  Vergleiche zeichengleich.

  Die Ausnahmeliste (genau ein Eintrag: `team.config.sh` ↔ `team.config.ps1`)
  trägt Begründungspflicht und wird selbst bewacht — eine Ausnahme, die keinen
  Vergleich mehr rettet, fällt auf. Ohne das wäre die Liste die Sammelstelle,
  hinter der echte Drift verschwindet. **Nicht** geprüft wird Drift in den
  eingesetzten Werten; das zeigt nur ein Lauf mit beiden Shells auf einer
  Maschine und steht als `BL-117` offen, statt hier behauptet zu werden.

### Fixed

- **BL-114 — der Rollback eines Rollenlaufs riss fremde uncommittete Arbeit
  mit, und die Bibliothek verbot sich das zwei Zeilen weiter selbst.**
  `frank.sh`/`frank.ps1` rollten auf **zwei** Pfaden (Session-Limit und
  Fehlversuch) mit unbeschränktem `git reset --hard` + `git clean -fd` zurück;
  `axel` und `redteam` hatten ihren `git clean` zwar eingeschränkt, ihr
  `git reset --hard` daneben aber nicht. Der Kopf des Read-Only-Guards
  beschreibt wörtlich die Gegenregel — *„niemals blanko `git reset --hard`/
  `clean -fd`. (Lektion 2026-07-10: ein blindes reset+clean löschte einmal die
  gesamte uncommittete Team-Infrastruktur. Nie wieder.)"* Die Lehre war am
  **Guard** angewandt und am **Aufrufer** nicht.

  Die chirurgische Schleife des Guards ist jetzt als
  `team_pfade_zuruecksetzen` herausgelöst, darauf sitzt `team_rollback_rolle`,
  und alle sechs Stellen rufen sie auf. HEAD wandert mit `--soft` zurück
  (gestagte fremde Arbeit bleibt unberührt), die Pfade **dieser** Rolle holt
  die Schleife einzeln. Frank bekommt dafür erstmals einen Startschnappschuss
  (`team_guard_begin`) — als schreibende Rolle hatte er keinen und konnte
  fremde Arbeit gar nicht von der eigenen unterscheiden. Reichweite von
  `HM-29` und die Ausnahme für Laufzeitartefakte (`BL-4`/`BL-24`) bleiben.

  **Beim Bauen aufgefallen, und es betraf auch den Guard:** `git status
  --porcelain` meldet einen untracked **Ordner** als EINEN Eintrag (`plans/`).
  Committet eine Rolle eine fremde Datei daraus versehentlich mit, taucht sie
  danach als `plans/closeout.md` auf und passt auf keinen Eintrag der
  Fremdliste mehr — ein reiner Zeichenvergleich hätte sie gelöscht. Der neue
  gemeinsame Filter `team_fremd_ausfiltern` zählt einen Pfad auch dann als
  fremd, wenn er **unter** einem fremden Ordnereintrag liegt.

  Gegenprobe in
  [`team/tests/test_bl114_rollback_verschont_fremde_arbeit.py`](geteilt/tests/test_bl114_rollback_verschont_fremde_arbeit.py)
  (21 Fälle): Schonung **und** Wirksamkeit je Bahn, dazu ein echter
  `frank.sh`-Lauf mit gestubbter CLI. Mit dem alten Rollback verschwindet dort
  `CHANGELOG.md` — genau die Datei aus dem Feldbericht —, mit dem Fix
  überlebt sie. Der ursprüngliche Verlustfall (nach einem **erfolgreichen**
  Lauf) ist damit **nicht** erklärt; sein Mechanismus war nie bewiesen.

- **BL-116 — ein Transkript, zwei Closeouts: der zweite bucht die Summe
  beider Kaskaden.** Der Abo-Messweg misst das Sitzungstranskript. Wer zwei
  Kaskaden in **derselben** Sitzung abschließt, misst beim zweiten Closeout
  wieder das **ganze** Transkript — der bereits gebuchte Teil steckt darin und
  wandert ein zweites Mal ins Ledger. Aus dem Feld zurückgespielt
  (`team-kit_project_platformer`, dortiges `BL-120`).

  **Der Befund ist die Unsichtbarkeit, nicht der Rechenfehler.** Keine
  bestehende Absicherung schlägt an: Die vierte Eigenschaft aus `BL-33` („ein
  Transkript je Aufruf") verbietet, **mehrere** Transkripte zu summieren, und
  sagt nichts über **eines** mit zwei Buchungspunkten; die Deduplikation über
  die Nachrichten-ID greift nicht, weil jede Antwort der ersten Hälfte genau
  einmal vorkommt — nur eben bereits bezahlt; und der A1-Kollisionsschutz
  schlägt bei **derselben Rolle + Kaskade** an, während hier zwei
  Kaskadennummern entstehen, also zwei für sich plausible Zeilen.

  Zuständigkeitslage und Entscheid wie bei `BL-33`: Das Messwerkzeug gehört
  dem Kit nicht, also wird die **Eigenschaft** benannt statt der Datei. A.9
  führt jetzt **fünf** Eigenschaften — neu „(5) Den bereits gebuchten
  Abschnitt ausnehmen", mit einem eigenen Absatz dazu, **warum** sie nicht
  schon in (1)–(4) steckte. Dazu die vermeidende Hälfte im Briefing des
  Architekten, an der Stelle, an der gebucht wird: **„Ein Closeout je
  Sitzung"**, samt Ausweg für den Ausnahmefall (Rohwert minus bereits gebucht,
  Rechnung in den Notiztext). Geprüft nach Träger getrennt: A.9 über das
  Regel-Inventar, das Briefing über
  [`team/tests/test_bl116_ein_closeout_je_sitzung.py`](geteilt/tests/test_bl116_ein_closeout_je_sitzung.py).

- **BL-111 — drei Ableitungen aus der Plan-Datei rissen den Aufrufer unter
  `set -o pipefail` weg, und der Kommentar darüber sagte das Gegenteil zu.**
  `team_architekt_kaskade` beendete seine Pipeline mit `| head -1` und
  begründete das wörtlich damit, ein Projekt ohne erkennbare Kaskade dürfe den
  Aufrufer *„unter set -e nicht wegreissen"*. Das stimmt für `set -e` und ist
  unter `set -o pipefail` wirkungslos: Dort bestimmt der erste fehlschlagende
  Teil den Status, also der leere `grep`. Gemessen: `set -e` → `rc=0`,
  `set -euo pipefail` → **Abbruch**. Alle bauenden und prüfenden Rollen laufen
  mit voller Strenge.

  **Der Umfang war größer als der Befund.** Nachgemessen an allen fünf
  Ableitungen sind **drei** betroffen — neben `team_architekt_kaskade` auch
  `team_ralph_cap` und `team_budget_empfehlung`, gleiche Bauart
  (`grep … | head -1 | cut`). Bei beiden ist der Fall, den sie nicht
  überlebten, der **dokumentierte Normalfall**: eine Plandatei ohne diese
  Zeile. Der Kommentar von `team_budget_empfehlung` sagte sogar „kein
  Abbruch" zu. Alle drei halten ihren Rückgabewert jetzt mit `{ … ; } || true`
  auf 0. Der PowerShell-Zweig war nie betroffen (keine Pipeline).

  Gegenprobe zweifach: `test_bl18_architekt_zeile_beschriftung.py` fährt jetzt
  `strikt=True` statt `strikt="abbruch"`, und
  [`team/tests/test_bl111_ableitungen_unter_pipefail.py`](geteilt/tests/test_bl111_ableitungen_unter_pipefail.py)
  prüft je Funktion **beide** Pfade — leer unter voller Strenge **und** der
  vorhandene Wert, sonst wäre `funktion() { :; }` ein grüner Weg. Mit der
  alten `lib.sh` fallen genau die Leer-Fälle.

- **BL-115 — die Vorlage lehrte eine Statuszeile, die das eigene Werkzeug nicht
  findet, und das Werkzeug meldete den Fehlgriff nicht, sondern stürzte ab.**
  Die Regeldatei schrieb *„Status auf `offen → an Frank übergeben` setzen"*.
  Der Pfeil meint den **Übergang**, liest sich aber als **Feldwert**; von Hand
  abgeschrieben entsteht `- **Status**: offen → an Frank übergeben`. `list`
  zeigt den Fund weiter an, `first 'an Frank übergeben'` findet ihn **nicht**,
  `frank.sh` meldet „nichts zu tun" — und der bezahlte Lauf ist verbraucht,
  ohne dass irgendetwas auf den Widerspruch hinweist. Im Feld an `HM-106` genau
  so passiert.

  Drei Hälften desselben Fehlers, alle drei gefixt: Die Vorlage nennt jetzt den
  **Zielwert** und den Pfeil ausdrücklich als Übergang (die Status-Kette selbst
  bleibt und ist eigens abgesichert). `first`, `dateien`, `reproducer`, `lint`
  und `set` geben bei fehlendem Pflichtargument eine **Nutzungszeile und
  Exit 2** statt eines `IndexError`-Tracebacks — ausgerechnet auf dem Weg, den
  man geht, wenn man gerade prüft, ob ein Fund auffindbar ist. Und
  `beutebuch.py lint` meldet neu eine Statuszeile, die auf **keinen** Wert der
  Kette passt (Exit 3), mit dem richtigen Wert in der Meldung.

  **Der Fund beim Bauen:** Die naheliegende Prüfung wäre stumm grün gewesen.
  `passt()` vergleicht per Präfix, und `offen → an Frank übergeben` **beginnt**
  mit `offen` — der Wächter hätte seinen eigenen Anlassfall durchgelassen.
  Deshalb `status_bekannt()`: exakter Kettenwert oder Wert plus Klammerzusatz
  (`erledigt (Frank-Fix, abc1234)`), sonst nichts. Dieser String steht als
  Gegenprobe im Test —
  [`team/tests/test_bl115_statuszeile_und_nutzungshinweis.py`](geteilt/tests/test_bl115_statuszeile_und_nutzungshinweis.py),
  14 Fälle.

- **BL-113 — der native Windows-Zweig startete auf der Zielmaschine nicht, und
  zwar wegen einer fehlenden Kodierungsangabe.** Beim ersten Kontakt mit einer
  echten Windows-11-Enterprise-VM brach `kit-einrichten.ps1` mit **zehn
  Syntaxfehlern** ab, von denen **keiner echt war**. Windows PowerShell 5.1
  liest eine Datei ohne Byte-Order-Mark nicht als UTF-8, sondern in der
  ANSI-Codepage; der Geviertstrich `—` wird dabei zu `â€"`, und dessen letztes
  Zeichen ist U+201D — für PowerShell eine **gültige Stringgrenze**. Jeder
  Gedankenstrich schließt damit seine Zeichenkette mitten im Satz. Im Zweig
  stehen 443 davon.

  Neu ist deshalb eine Kodierungsregel an **einer** Stelle je Installer
  (`Team-Kodierung` in [install.ps1](pwsh/install.ps1), das `fuelle`-Here-Doc in
  [install.sh](bash/install.sh)): **`.ps1`/`.psm1` mit BOM, alles andere ohne.**
  Die zweite Hälfte ist gleich teuer bezahlt — ein BOM vor einer Shebang-Zeile
  macht aus ihr Zeichensalat, und `json.load` bricht darüber ab, worauf
  `kosten.py` die Datei still als `0.0000` zählt. `.cmd` wurde auf reines
  ASCII gezogen (der Kommandozeileninterpreter liest sie in der **OEM**-
  Codepage, nicht in 1252). Als Nebenertrag erreicht 5.1 jetzt die
  Versionsprüfung und **sagt**, dass `pwsh` gebraucht wird, statt zu zerfallen.

  **Warum keine der bestehenden Prüfungen das finden konnte:** Sie fahren
  alle unter pwsh 7, und pwsh 7 liest UTF-8 ohne BOM überall korrekt. Zum
  Zeitpunkt des Fehlschlags waren `kit-test.sh` (10/10), `kit-test.ps1`
  (15/15), die Doppelbahn (364 bestanden) und der Syntaxcheck über alle
  `.ps1` grün. Die Lehre steckt in der Bauart der neuen Prüfung: Was die
  Zielmaschine anders **liest** statt anders **tut**, prüft man an den Bytes.
  [`team/tests/test_bl113_bom_regel.py`](geteilt/tests/test_bl113_bom_regel.py)
  sieht sich Dateianfänge an, braucht kein PowerShell und greift deshalb auch
  dort, wo der Zweig gar nicht laufen kann; `kit-test.sh` Schritt 10 prüft
  dieselben drei Regeln im Kit, und [.gitattributes](.gitattributes) trägt die
  Begründung neben der CRLF-Regel — weil dort danach gesucht wird.

### Added

- **[`doku/einrichtung.md`](doku/einrichtung.md) beschreibt jetzt DREI Wege**
  statt zwei: Linux, Windows mit WSL und **Windows nativ** (PowerShell, ohne
  WSL). Der neue Abschnitt sagt zuerst, **wann** er der richtige ist — nämlich
  wenn WSL2 ausfällt (VM ohne *nested virtualization*, verwalteter Rechner,
  gesperrte Firmware) — und stellt die vier echten Unterschiede
  gegenüber: kooperatives `flock` gegen die vom Betriebssystem **durchgesetzte**
  `FileShare::None`-Sperre, `/mnt/c` gegen Netzlaufwerk und OneDrive,
  fehlendes Exec-Bit gegen die Ausführungsrichtlinie, `kit-test.sh` gegen
  `kit-test.ps1`. Dazu acht Detailabschnitte, darunter drei Fallen, die alle
  dasselbe Muster haben — sie sehen nach etwas anderem aus, als sie sind:
  ein `claude`, das nicht aufgelöst wird, **sieht aus wie ein Auth-Fehler**;
  ein Store-Platzhalter **trägt den Namen** `python.exe` und ist keiner; ein
  nach OneDrive umgeleitetes Benutzerprofil **fällt im Pfad nicht auf**.
- **Acht neue Fehlerbilder für den nativen Weg** — von der
  Ausführungsrichtlinie über die BOM-Falle bis zur `Set-Location`-Falle
  (PowerShell-Position und Prozess-Arbeitsverzeichnis sind zwei verschiedene
  Dinge). Und im **Belegstand** steht der neue Zweig mit dem Status, den er
  wirklich hat: *gebaut und gefahren, aber nicht auf Windows* — samt
  ausdrücklicher Liste dessen, was unter Linux gar nicht prüfbar ist.
- **Befehlstabellen mit Plattformspalte** in [README.md](README.md) und
  [bootstrap/TEAM.md](bootstrap/TEAM.md). Die Python-Werkzeuge stehen dort
  bewusst als *(gleich)*: Sie werden **nicht** portiert — Ledger, Beutebuch und
  Kostenrechnung liegen auf beiden Wegen in denselben Dateien. Der
  PowerShell-Zweig ist eine zweite **Orchestrierung**, kein zweiter
  Zustandscode.

### Fixed

- **Die Begründung für `bash` ≥ 4 stand falsch in
  [`kit-einrichten.sh`](bash/kit-einrichten.sh) und in der Doku.** Dort hieß es, das
  Kit nutze *durchgehend* indirekte Expansion (`${!var}`). Nachgemessen kommt
  sie in der **Laufzeit** — `team/lib.sh`, `entry/*.sh`, `team/redteam.sh` —
  genau **null** Mal vor; alle sechs Fundstellen liegen im **Installer**. Die
  Anforderung bleibt bestehen, nur mit dem richtigen Grund: Ohne Installer
  kommt niemand zu einer Laufzeit. Keine Kleinigkeit — die alte Formulierung
  hätte jeden, der die Laufzeit portiert oder prüft, an der falschen Stelle
  suchen lassen. (Gefunden beim Vermessen für den Windows-Zweig, Stufe 1.)

### Added (Fortsetzung)

- **Die Rollen laufen unter Windows — der Zweig ist bedienbar.** Zehn
  Einstiege plus die gemeinsame Sweep-Logik, je mit `.cmd`-Shim:
  [`ralph.ps1`](pwsh/entry/ralph.ps1), [`frank.ps1`](pwsh/entry/frank.ps1),
  [`axel.ps1`](pwsh/entry/axel.ps1), [`harry.ps1`](pwsh/entry/harry.ps1),
  [`marv.ps1`](pwsh/entry/marv.ps1), [`vollautomatik.ps1`](pwsh/entry/vollautomatik.ps1),
  [`halbautomatik.ps1`](pwsh/entry/halbautomatik.ps1),
  [`team-status.ps1`](pwsh/entry/team-status.ps1),
  [`team-test.ps1`](pwsh/entry/team-test.ps1),
  [`team/redteam.ps1`](pwsh/redteam.ps1). Die `.cmd`-Dateien sind Einzeiler auf
  die `.ps1` — kein Symlink, denn der braucht unter Windows
  Administratorrechte, und ein Einrichtungsschritt, der an Rechten scheitert,
  hat sein Versprechen gebrochen.
  **Belegt durch einen Trockenlauf der ganzen Kette** (`TEAM_DRY_RUN=1`, keine
  CLI-Kosten): Ralph baut Stufe 1, erhält das Promise, schaltet weiter,
  erreicht `RALPH_CAP`; Harry und Marv sweepen; Frank findet nichts; der
  Abschlussbericht erkennt Kaskade K1, liest Sperr-Status und
  Kostenaufteilung und zitiert die letzten Zeilen des Lauf-Logs.
- **Die BL-3-Invariante wird jetzt auf beiden Bahnen geprüft.** Sie ist die
  Zusicherung, auf der **alle** relativen Werkzeugpfade ruhen — ohne sie hängt
  jede Kostenzahl davon ab, aus welchem Verzeichnis gestartet wurde, und
  `kosten.py` meldet still `0.0000`. Beide Zweige sichern dasselbe zu, nur
  anders geschrieben (`cd "$(dirname "$0")"` bzw. `Set-Location $PSScriptRoot`).
  Die Zuordnung steht in `Schale.wechsel_ins_skriptverzeichnis`, **nicht** im
  Test: Sonst führte jede der 24 statischen Quelltextprüfungen ihre eigene
  Übersetzungstabelle, und die erste vergessene wäre eine stille Lücke im
  Windows-Zweig.

### Fixed (Windows-Zweig)

- **`team/redteam.ps1` wurde von KEINEM der beiden Installer kopiert.** Beide
  kannten unter `team/` nur `.sh` und `.psm1`; die Rollen starteten mit *„term
  './team/redteam.ps1' is not recognized"*. Bemerkenswert daran: Die
  Gleichstandsprüfung aus Schritt 10/10 sieht so etwas **nicht** — beide
  Installer waren gleich falsch, die Bäume also identisch. Gefunden hat es der
  Trockenlauf, und genau dafür steht er im Plan.
- **Eine PowerShell-Falle im Formatoperator, fünfmal.** In
  `[Console]::Out.WriteLine('{0} {1}' -f $a, $b)` ist das Komma der
  **Argumenttrenner der Methode**, nicht der Array-Operator: Der Ausdruck wird
  zu `WriteLine(('{0} {1}' -f $a), $b)`, und `-f` bekommt ein Argument für zwei
  Platzhalter. Das fällt erst zur Laufzeit auf, mitten im Statusbericht, und
  sieht aus wie ein Datenfehler statt wie ein Syntaxproblem.

### Added (Fortsetzung)

- **Der Kern des Windows-Zweigs — [`team/lib.psm1`](pwsh/lib.psm1), und die 28
  schlafenden Tests wachen auf.** Alle 42 Funktionen aus
  [`team/lib.sh`](bash/lib.sh) sind portiert: Werkzeug-Hüllen, Sperre, Auth,
  `team_claude` samt Abo→API-Fallback und 429-Logik, die sieben `team_guard_*`,
  Promise, Quittung, Bewertung. Die Funktionsnamen bleiben **zeichengleich**
  (`team_guard_verify`, nicht `Verify-TeamGuard`) — PowerShell warnt darüber bei
  jedem Import, und die Warnung wird abgestellt statt der Name geändert: Die
  Namensgleichheit ist es, was **eine** Testsuite für beide Bahnen möglich
  macht. Ergebnis: `pytest team/tests` meldet ohne `pwsh` 332 passed, mit
  `pwsh` **363 passed** — die Differenz von 31 sind exakt die bis dahin
  übersprungenen Varianten, bei **unveränderten** 21 erwarteten Fehlschlägen.
  Damit laufen auch die fünf Guard-Tests aus `BL-24` auf beiden Bahnen und
  weisen dort einen echten chirurgischen Rollback nach.
- **Die 13 eingebetteten `python3 -c`-Blöcke entfallen ersatzlos.**
  `ConvertFrom-Json`, `[regex]` und `[DateTimeOffset]` ersetzen sie; in
  `lib.psm1` kommt `python3 -c` nur noch in zwei Kommentaren vor. Und
  `team_lock` nimmt eine vom Betriebssystem **durchgesetzte** Sperre
  (`FileShare::None`) statt des kooperativen `flock` — über zwei echte Prozesse
  geprüft: Elternprozess sperrt, Kindprozess wird abgewiesen, nach `team_unlock`
  bekommt das Kind die Sperre.

### Fixed

- **Die Kodierung der Kostenlogs hing an einer PowerShell-Voreinstellung — und
  ihr Bruch wäre still gewesen.** Der naheliegende Weg `& claude … > $Out`
  schreibt mit der Standardkodierung der Sitzung: unter pwsh 7 heute UTF8NoBOM,
  unter Windows PowerShell 5.1 UTF-16LE, und ein `$PSDefaultParameterValues` im
  Benutzerprofil kann es jederzeit umstellen. Python bricht an einem BOM ab —
  aber [`team/tools/kosten.py`](geteilt/tools/kosten.py) **fängt das ab und zählt
  die Datei still als `0.0000`**. Das ist exakt die Fehlerklasse aus `BL-46`
  (Log von 0 Byte nach 47 Minuten Laufzeit) und `BL-55` (Pro-Stufe-Cap
  umgehbar): Eine bezahlte Stufe erscheint als die **billigste** der Kaskade,
  der Deckel bekommt auf sie keinen Griff, und auffallen würde es erst, wenn
  jemand die Kostentabelle als Vergleichsband liest. `Team-ClaudeSchreiben`
  legt die Kodierung jetzt ausdrücklich fest;
  [`test_stufe3_kostenlog_kodierung.py`](geteilt/tests/test_stufe3_kostenlog_kodierung.py)
  pinnt sie auf beiden Bahnen, inklusive Umlaut-Rundlauf — reines ASCII sähe in
  UTF-8 und Latin-1 gleich aus und bewiese nichts.
- **`install.sh` kannte den PowerShell-Kern nicht.** Sie kopiert `team/lib.sh`
  und `team/redteam.sh` namentlich; `team/lib.psm1` wäre durch das Raster
  gefallen, und ein Projekt liefe nach `--update` auf einer Hälfte veraltet
  weiter. Gefunden von der Gleichstandsprüfung in `kit-test.sh` (10/10) —
  genau dafür ist sie da.

### Changed

- **`kit-test.sh` braucht mit `pwsh` auf dem PATH rund 11 Minuten statt gut
  vier.** Die eingebetteten pytest-Läufe fahren jetzt beide Bahnen. Das ist der
  Preis der Doppelbahn und kein Fehler — aber er gehört genannt, damit niemand
  einen Hänger vermutet.

### Added (Fortsetzung)

- **Der Bootstrap des Windows-Zweigs — und der Nachweis, dass beide Installer
  dasselbe tun.** Neu sind [`install.ps1`](pwsh/install.ps1),
  [`kit-einrichten.ps1`](pwsh/kit-einrichten.ps1),
  [`scripts/team-auth-setup.ps1`](pwsh/scripts/team-auth-setup.ps1),
  [`scripts/team-init.ps1`](pwsh/scripts/team-init.ps1) und die Konfigurationsvorlage
  [`entry/team.config.ps1`](pwsh/entry/team.config.ps1). Ohne sie ließe sich das Kit
  auf einer Windows-Maschine ohne WSL gar nicht erst einrichten — deshalb steht
  der Bootstrap **vor** dem Kern und nicht danach.
  **Die Zusicherung ist nicht „beide funktionieren", sondern „beide tun
  dasselbe":** `install.sh` und `install.ps1` erzeugen aus denselben neun
  Antworten **byte-identische Bäume** (155 Dateien, `diff -r` ohne Ausgabe).
  Festgenagelt in [`kit-test.sh`](bash/kit-test.sh) als Schritt 10/10 — ein
  Vergleich statt einer Liste von Einzelprüfungen, denn eine Liste prüft nur,
  woran jemand gedacht hat. Fehlt `pwsh`, sagt der Schritt **laut**, dass die
  halbe Zusicherung des Windows-Zweigs hier ungeprüft blieb; ein
  übersprungener Nachweis, den niemand sieht, liest sich am Ende wie ein
  bestandener.
- **`team.config.sh` und `team.config.ps1` sind zwei Generate einer Quelle.**
  Beide Installer schreiben **beide** Konfigurationen — auch `install.sh` unter
  Linux, wo die PowerShell-Fassung niemand braucht. Der Grund ist die
  Driftfreiheit: Schriebe nur `install.ps1` die `.ps1`-Fassung, hätte ein auf
  Linux eingerichtetes Projekt unter Windows keine Konfiguration, und jemand
  schriebe sie von Hand. Genau dort fängt Drift an. Belegt ist außerdem, dass
  die Zweige einander **updaten** können: `install.ps1 -Update` gegen eine mit
  `install.sh` erzeugte Installation ersetzte 78 Infrastruktur-Dateien und ließ
  Ledger, Kaskadenstand und den von Hand eingetragenen Smoke-Test unberührt.
- **Drei Stellen, an denen der Windows-Zweig strenger ist als der Bash-Zweig.**
  Die Platzhalter-Ersetzung braucht kein eingebettetes `python3`-Here-Doc mehr,
  sondern .NET-Bordmittel. Die Sperrprüfung vor einem Update ist eine vom
  Betriebssystem **durchgesetzte** Sperre (`FileShare::None`) statt des
  kooperativen `flock`, und `kit-einrichten.ps1` probt sie mit **zwei
  Prozessen** statt mit einem. Und der API-Key wird nicht mit `chmod 600`
  geschützt — das läuft unter Windows ohne Fehler durch und bewirkt **nichts**,
  der Schlüssel läge danach lesbar da, mit einem grünen Haken daneben —,
  sondern über eine ACL, die anschließend **nachgeprüft** wird.
  Umgekehrt ausdrücklich benannt: Der Selbsttest von `install.ps1` kann die
  `.sh`-Entrypoints nicht syntaktisch prüfen, weil unter Windows keine `bash`
  vorliegt. Er sagt das, statt Vollzug zu melden.
- **Die Doppelbahn: eine Testsuite, zwei Shells.** Das Kit bekommt einen
  nativen Windows-Zweig in PowerShell, während Bash die Linux-Implementierung
  bleibt ([`plans/windows-nativ.md`](plans/windows-nativ.md)). Der nahe
  liegende Weg wäre eine zweite Testsuite gewesen — und das wäre der eine
  Fehler, der das Vorhaben zum Scheitern bringt: Zwei Suiten driften genauso
  wie zwei Implementierungen, nur unbemerkt. Neu ist deshalb
  [`team/tests/conftest.py`](geteilt/tests/conftest.py) mit der `Schale`: Ein
  Test formuliert nur noch **Schritte**, und wie ein Schritt in der jeweiligen
  Shell ausgesprochen wird, weiß allein der Harnisch. Damit wird eine künftige
  Feldlehre auf der anderen Bahn **automatisch rot**, bis sie nachgezogen ist
  — Drift ist nicht verboten, sondern sichtbar. Sechs Tests (`BL-18`, `BL-24`,
  `BL-28`, `BL-32`, `BL-41`, `HM-32`) tragen keine Shell-Syntax mehr im
  Testkörper. Die Schritte einer Folge bleiben dabei in **einem** Prozess,
  weil `team_guard_begin` seinen Schnappschuss in einer Shell-Variablen
  ablegt: Ein `verify` im zweiten Prozess sähe einen leeren Schnappschuss und
  spräche jede Rolle frei — grün und wertlos. Der Kopf der Datei legt zugleich
  die **Aufrufkonvention** für den PowerShell-Zweig fest (sieben Punkte),
  damit Stufe 3 nicht gegen einen unausgesprochenen Vertrag baut.
- **Die Doppelbahn-Quote steht in jedem Testlauf.** Gleichwertigkeit lässt
  sich nicht zusichern, ohne sie zu messen, und eine Schwelle („ab fünf
  Ausnahmen gilt der Zweig als abgehängt") wäre willkürlich und sofort
  verhandelbar. Der Bericht nennt stattdessen, wie viele Tests auf beiden
  Bahnen liefen, wie viele die pwsh-Bahn übersprangen und wie viele bewusst
  mit `@pytest.mark.nur_bash` geführt werden. Jede Markierung braucht eine
  Begründung und gehört zusätzlich in den Backlog.
- **[`pruefe-windows.ps1`](pwsh/pruefe-windows.ps1)** — die Vorflug-Probe für den
  nativen Zweig, **eigenständig** und ohne jede Kit-Abhängigkeit, damit sie
  einzeln auf die Zielmaschine kopiert werden kann. Sie beantwortet, was der
  Bauplan bisher nur annimmt: ob PowerShell die Agenten-CLI findet und startet
  (unter Windows ein `.cmd`-Shim — schlägt das fehl, **sieht das aus wie ein
  Auth-Fehler und ist keiner**), ob `[System.IO.FileStream]` mit
  `FileShare::None` über Prozessgrenzen sperrt (der Ersatz für `flock`,
  geprüft mit einer Zwei-Prozess-Gegenprobe statt mit einer Erwartung), und
  wie die Auth-Lage aussieht. Der Standardlauf **kostet nichts**; die
  abschließende Antwort auf die Abo-Frage braucht `-MitEchtemAufruf` und sagt
  das vorher. Erfolgskriterium ist der Exit-Code, nicht die Schlusszeile.
- **Klonen und Einbinden ist jetzt eine Routine — für Linux und für Windows
  mit WSL.** Bis hierher begann jede Anleitung in dem Zustand, in dem die
  Autorenmaschine ohnehin war. Neu ist [`kit-einrichten.sh`](bash/kit-einrichten.sh):
  die Vorflug-Prüfung zwischen `git clone` und `install.sh`. Fünf Abschnitte —
  Umgebung (Linux/WSL1/WSL2), Bordmittel (`bash` ≥ 4, `git`, `python3` ≥ 3.8,
  `flock` als Fehler; `pytest` und die Agenten-CLI als Hinweis), Lage des
  Klons, Auth, Kurzbefehl — und am Ende die Übergabe an `install.sh`, wenn ein
  Zielpfad genannt wurde. Es ruft **keine** Agenten-CLI auf und kostet nichts.
  Der Bauentscheid dahinter: **proben statt voraussetzen.** Das Skript schließt
  nicht aus dem Pfad auf die Rechte, sondern legt eine temporäre Datei an,
  ruft `chmod +x` auf und prüft, ob das Bit hält — danach `flock -n` auf
  dieselbe Datei. Dieselbe Haltung wie A.5: Die Heuristik erklärt den
  Regelfall, die Probe entscheidet den Einzelfall.
- **[`doku/einrichtung.md`](doku/einrichtung.md)** — die Routine ausgeschrieben:
  kurzer Weg je Plattform, Bordmittel je Distribution, WSL-Besonderheiten,
  IDE-Beispiele (**VS Codium** unter Linux, **VS Code + WSL-Erweiterung** unter
  Windows — der Grund ist die Lizenz der Remote-Erweiterungen, nicht der
  Geschmack), Auth, Einbindung, Gegenprobe, elf Fehlerbilder mit Ursache und
  Abhilfe, und ein Abschnitt **Belegstand**. Vorangestellt ist die Tabelle
  *Was Pflicht ist und was Beispiel*: Pflicht sind `bash`/`git`/`python3`/
  `flock`; IDE, Agenten-CLI und Modell sind Beispiele mit benanntem
  Tauschpunkt. Eigener Unterabschnitt für den Fall **„nur WSL 1 möglich"**
  (VM ohne nested virtualization, gesperrte Firmware): erst der Schalter am
  Hypervisor je Produkt, dann — weil die eingebaute Sperrprobe einprozessig ist
  und auf einer Syscall-Übersetzung nur die schwächere Aussage trifft — eine
  **Zwei-Prozess-Gegenprobe für `flock`**, und die Regeln, die dort strenger
  gelten (`/mnt/c` doppelt verboten, obwohl WSL 1 dort *schneller* ist).
- **[`scripts/`](bash/scripts/) — die Maschinen-Skripte liegen jetzt im Repo.**
  README, `install.sh` und `TEAM.md` verwiesen auf
  `~/.claude/scripts/team-auth-setup.sh`, eine Datei, die es nur auf der
  Autorenmaschine gab: **Wer das öffentliche Repo klonte, bekam eine Anleitung,
  deren erster Schritt ins Leere zeigte.** Neu ausgeliefert werden
  `scripts/team-auth-setup.sh` und `scripts/team-init.sh`;
  `kit-einrichten.sh --verknuepfen` legt dafür unter `~/.claude/scripts/` einen
  **Symlink** an, nie eine Kopie (eine zweite Kopie läuft dem Kit unbemerkt
  hinterher), und rührt eine dort vorhandene echte Datei nicht an, sondern
  meldet sie.
- **[`.gitattributes`](.gitattributes)** mit `* text=auto eol=lf`. Git for
  Windows klont per Default mit `core.autocrlf=true`; der Shebang wird dann zu
  `#!/usr/bin/env bash\r` und bash meldet `bad interpreter` — ein Fehlerbild,
  das nach einer kaputten Installation aussieht und keines ist. Damit ist der
  Fall nicht mehr dokumentiert, sondern erledigt. Die CRLF-Prüfung in
  `kit-einrichten.sh` bleibt trotzdem: für Klone, die älter sind als die Datei.
- **`kit-test.sh`: neuer Schritt 9/9 — Einrichtungsroutine.** Die Routine steht
  **vor** `install.sh`; wer sie kaputt ausliefert, blockiert den Einstieg,
  bevor die Schritte 1–8 überhaupt greifen. Geprüft werden Syntax aller neuen
  Skripte, ein Durchlauf mit `--nur-pruefen` (Exit 0, nichts angefasst, keine
  Probendatei zurückgelassen), die Ablehnung eines Zielpfads ohne Git samt
  genanntem Ausweg, der Launcher **über einen Symlink**, der LF-Riegel in
  `.gitattributes` und dass die README nicht mehr auf den Pfad der
  Autorenmaschine zeigt. Beim ersten Lauf fiel der Schritt selbst durch: Das
  „Verzeichnis ohne Git" lag im Wegwerf-Repo und war damit sehr wohl in einem
  Arbeitsbaum — der Test hätte eine Ablehnung als ausbleibend geprüft, die
  nicht ausbleiben darf.
- **[`doku/anhang-a.md`](doku/anhang-a.md), A.12** — die Warum-Schicht dazu:
  die Lücke, die der fremde Klon aufdeckte, die drei WSL-Fallen mit ihrem
  gemeinsamen Muster („sieht aus wie ein kaputtes Kit und ist keines"), der
  Entscheid für Proben statt Annahmen und der Belegstand.

### Removed

- **`doku/release-vorlage.md` entfernt.** Das Kit veröffentlicht keine
  GitHub-Releases; ausgeliefert wird der **Quellstand**, und der Weg dorthin
  ist `git clone` (siehe [doku/einrichtung.md](doku/einrichtung.md)). Eine
  Vorlage für eine Seite, die niemand füllt, ist genau die Sorte Dokument, die
  später als geltender Prozess gelesen wird. `CHANGELOG.md` bleibt der Ort, an
  dem eine Änderung samt Begründung nachschlagbar ist — daran ändert sich
  nichts. Mitgezogen: Die README nennt `kit-test.sh` jetzt „DAS Gate vor jedem
  **Push**" statt „vor jedem Release", ebenso die Skizze in
  [plans/roadmap-skizzen.md](plans/roadmap-skizzen.md).

### Changed

- **README: Gliederung mit Inhaltsverzeichnis.** Die Seite ist auf 400 Zeilen
  gewachsen und hatte keinen Einstieg — neu ist ein Abschnitt **Inhalt** direkt
  unter dem Kopf: ein Verweiskasten auf
  [doku/einrichtung.md](doku/einrichtung.md) für alle, die das Kit zum ersten
  Mal auf eine Maschine holen, eine Tabelle der zehn Abschnitte dieser Seite,
  und eine Tabelle **Die Dokumentation** — welche Datei in `doku/` für wen
  gedacht ist, samt der Feststellung, dass `doku/` im Kit bleibt und `TEAM.md`
  die Anleitung im Zielprojekt ist.
- **README**: Der Einstieg beginnt jetzt beim `git clone` und führt über
  `kit-einrichten.sh`; die Auth-Voraussetzung zeigt auf `scripts/`, der Baum
  unter *Aufbau des Kits* führt `scripts/`, `kit-einrichten.sh` und
  `doku/einrichtung.md`. `install.sh` nennt im Auth-Hinweis den Pfad im Kit
  statt den auf der Autorenmaschine.

> **Belegstand dieses Eintrags:** Der Linux-Weg ist auf der
> Entwicklungsmaschine durchlaufen. Der WSL-Weg ist **hergeleitet, nicht
> durchlaufen** — die Regeln folgen aus den bekannten Eigenschaften von DrvFs
> und Git for Windows; die Proben melden den Fall an der Maschine. Ein
> vollständiger Durchlauf unter Windows steht aus.

## [2.10.0] — 2026-08-16

**Der Loop hält nicht mehr an, wo er neunmal dasselbe gehört hat.** Der vierte
`BL-41`-Ausgang — Log meldet Erfolg, Quittung fehlt — ist im Feld in neun
Kaskaden aufgetreten und jedes Mal gleich ausgegangen; er prüft sich jetzt
selbst, streng und in beide Richtungen. Dazu zwei Feldfunde am Rand des
Betriebs: ein Kit-Test, der am Füllstand des Beutebuchs hing, und ein
`.gitignore`, das der Installer für vollständig hielt, weil es den Block
*überhaupt* trug. Damit ist der Backlog des Kits wieder leer. Dazu eine
Festlegung, die bisher nur im Kopf des Autors stand: **Modellagnostik mit
benanntem Anspruch** — das Kit kennt keine Modellnamen, sondern zwei Stufen und
sechs vorausgesetzte Fähigkeiten; das Fernziel sind bezahlbare lokale Modelle,
eingewechselt von unten nach oben.

### Added

- **Der vierte Ausgang prüft sich selbst** (`BL-110`, schließt `BL-108` mit).
  Fehlt die Quittung, während das Log sich selbst für erfolgreich erklärt
  (`BL-41`), fährt `team_quittung_selbstpruefung` die Prüfliste jetzt selbst,
  statt den Lauf anzuhalten und einen Menschen dieselben drei Schritte gehen zu
  lassen. Im Feld ist der Fall in **neun** Kaskaden aufgetreten und **jedes
  Mal** gleich ausgegangen: Arbeit fertig, nur die Quittung fehlt.
  Drei Bedingungen im UND, im Zweifel „nicht bestanden": Arbeit vorhanden,
  **mindestens eine Datei unter `TEAM_TEST_ORDNER` berührt** (die Blindstelle,
  die Commit und grüner Baum nicht sehen — `BL-108`), Smoke-Test grün. Ein
  gesprengter Soft-Cap schließt die Automatik aus; abschaltbar über
  `TEAM_QUITTUNG_AUTO=0`. Uncommittete Arbeit wird dabei gesichert, sonst liefe
  die nächste Stufe auf schmutzigem Baum.

### Changed

- **Die Modellhaltung des Kits steht jetzt in den Dokus — als Agnostik mit
  benanntem Anspruch.** Bisher stand nirgends, warum die Rollen zwei Stufen
  ansprechen (`TEAM_MODEL_LOOP`, `TEAM_MODEL_STRONG`) statt Modellnamen, und
  „Opus" tauchte in der Anleitung wie eine Voraussetzung auf. Neu und
  gleichlautend in [README.md](README.md) (Abschnitt **Modelle**),
  [bootstrap/TEAM.md](bootstrap/TEAM.md) (*Welches Modell arbeitet wo*),
  [entry/team.config.sh](bash/entry/team.config.sh) (kommentierter Block an der
  Stelle, wo man es verstellt) und [doku/anhang-a.md](doku/anhang-a.md) (**A.11**,
  die Warum-Schicht): Das Kit bindet sich an **kein** Modell und keinen
  Anbieter; `sonnet`/`opus` sind Defaults, keine Voraussetzung. Vorausgesetzt
  werden **sechs Fähigkeiten** — große Regeldatei tragen, Werkzeuge zuverlässig
  aufrufen, das `<promise>`-Protokoll bis zum Ende durchhalten, unerzwungene
  Auflagen einhalten, ohne Rückfragen headless arbeiten, eine Stufe samt Tests
  zu Ende bringen —, und das Niveau, auf dem sie heute nachweislich reichen,
  ist Sonnet/Opus. **Langfristig lokal:** Sobald bezahlbare Open-Weights-Modelle
  diese Fähigkeiten halten, werden sie **von unten nach oben** Standard — erst
  die schwache Stufe (Masse der Aufrufe, billiger Irrtum), dann die starke.
  A.11 benennt dazu drei Dinge ehrlich: Das Kit ist modellagnostisch, aber
  **nicht CLI-agnostisch** (`team_claude()` ist die einzige Aufrufstelle, an ihr
  hängen Ergebnis-JSON, Auth-Fallback und 429-Behandlung); der Guard wird durch
  einen Modellwechsel **wichtiger**, nicht unwichtiger; und die Kostenmechanik
  misst USD — im lokalen Betrieb wäre sie strukturell null und damit eine
  Kennzahl, die zum Wegsehen erzieht (`BL-9`/`BL-14`-Falle). Ein Lauf mit einem
  lokalen Modell ist **nicht** belegt: Ziel, nicht Zustand.

### Fixed

- **`install.sh --update` zog ein gewachsenes `.gitignore` nie nach**
  (`BL-109`). Der Update-Pfad sah die Datei gar nicht an, und die
  Erstinstallation prüfte nur, ob der Block **überhaupt** dasteht — nicht, ob
  er vollständig ist. Ein Projekt, das früh installiert und seither brav
  `--update` gefahren ist, blieb damit dauerhaft auf dem Fragmentstand seines
  Installationstages, während der Installer Erfolg meldete. Im Feld
  (platformer) fehlten so `.team-focus-harry` und `.team-focus-marv`: beide
  standen nach **jedem** Sweep als untracked im Baum, sahen im Closeout wie
  unfertige Arbeit aus, und ein unachtsames `git add -A` hätte einen
  Fokus-String verewigt, der für genau einen Lauf galt. Beide Pfade vergleichen
  jetzt **Zeile für Zeile** gegen `bootstrap/gitignore.fragment` und melden die
  fehlenden namentlich, samt kopierbarem Nachtrag-Befehl. **Ergänzt wird
  nichts** — eine fehlende Zeile kann eine bewusst entfernte sein, und
  `--update` fasst Projektdateien grundsätzlich nicht an. Der stille Fall ist
  der teure; die Meldung ist die risikofreie Hälfte.

- **`test_bl47_sweep_ergebnis.py` hing an einem leeren Beutebuch** (`BL-62`).
  Die Gegenproben hängten Funde mit **fest verdrahteten** Nummern an, während
  `_fixture()` das echte Beutebuch des Zielprojekts hereinkopiert und
  `redteam.sh` neue Funde über `next-id` vorher/nachher zählt. Ein `HM-1`, den
  es dort längst gibt, erhöht die nächste freie Nummer nicht — der Sweep meldet
  korrekt „keine neuen Funde", und der Test fällt um, obwohl die Mechanik
  stimmt. Die Nummer kommt jetzt aus dem kopierten Beutebuch. Im Feld
  (platformer, Beutebuch bis `HM-100`) sind daran zwei Gegenproben unmittelbar
  nach einem Kit-Update rot geworden.

## [2.9.0] — 2026-08-14

**Der Backlog ist abgearbeitet.** 26 offene Rückmeldungen aus dem Feld —
`BL-20`…`BL-61` — von drei Buchungsverlusten am Kostenwerkzeug über einen
Guard-Rollback, der Vollzug meldete, den er nicht leisten konnte, bis zu zwölf
Betriebslehren, die nirgends standen. Vier Funde wurden **beim Bauen** entdeckt
und mit behoben; zwei davon hätte der jeweilige Fix selbst verursacht.

### Fixed

- **Drei Buchungsverluste am selben Werkzeug.** `akteur-abschluss` ersetzte
  still, wo `rollen-abschluss` seit `BL-5` abbricht (`BL-25`, im Feld 5,5515
  USD spurlos verloren); die Wrapper verschluckten Schalter, sodass `--kaskade`
  nie ankam und auf die Kaskade aus `.ralph-plan` gebucht wurde (`BL-26`, eine
  abgeschlossene Zeile über 8,4678 USD ersetzt); **ein** Notiztext beschriftete
  **zwei** Ledger-Zeilen (`BL-34`, zweimal im Feld die Arbeit des Red Teams
  über Ralphs Baustufen).
- **Der Wächter sah die vergessene Buchung nicht** (`BL-27`): `ledger-pruefen`
  wischte jede Kaskade ohne Rollenzeile als „geplant" weg — 33,89 USD lagen
  ungebucht in den Logordnern, gemeldet wurden null Warnungen. Das tragende
  Merkmal ist das **Alter** der Logs, nicht ihre Anwesenheit: Während eines
  laufenden Baus sind offene Logs der Normalzustand. Dieselbe Mechanik meldet
  beim Buchen Logs, die aus der Zeit **zwischen** zwei Kaskaden stammen
  (`BL-45`).
- **Der chirurgische Rollback konnte keine Verzeichnisse entfernen** (`BL-24`)
  und druckte den Vollzug elf Zeilen vor dem Aufräumen. Jetzt `rm -rf` mit
  Plausibilitätsprüfung, Erfolgskontrolle und Meldung **danach**.
- **Ein quittierter Fund ohne wirksamen Regressionstest** (`BL-22`/`BL-28`):
  Der Substanz-Anker bestand, sobald irgendeine im Fundblock genannte Datei im
  Diff lag — meist die Produktivdatei. Geprüft wird jetzt die reservierte
  Reproducer-Datei; `xfail` verlangt `strict=True`, und Franks Dreisatz beginnt
  mit der Gegenprobe „ohne den Fix muss der Test rot sein".
- **Der Fundblock wird geprüft, bevor er Geld kostet** (`BL-29`):
  `beutebuch.py lint` vor dem ersten Frank-Aufruf, Exit 3 statt Fehlversuch —
  ein unbrauchbarer Auftrag ist kein Versagen des Ausführenden.
- **Der Deckel vernichtete die Quittung statt der Arbeit** (`BL-30`): Ein
  nachweislich erfolgreicher read-only-Sweep behält seinen Zustandszeiger.
- **Der Cap verdeckte die `BL-41`-Erkennung** (`BL-60`): Eine Stufe, die beides
  tat, meldete sich als generischer Fehler. Die Reihenfolge der **Meldung** ist
  gedreht, der Effekt des Caps unverändert. Dazu der dritte Ausgang in der
  Prüfanleitung (`BL-61`): Rot **nur** in den neu angelegten Testdateien der
  Stufe heißt defekter Testaufbau, nicht kaputter Produktivcode — ein Neubau
  hätte im Feld 330 Zeilen korrekte Arbeit weggeworfen.
- **Der Budget-Stopp stoppte im teuersten Moment** (`BL-23`): Kulanzband von
  15 % für eine angefangene Fixrunde, **einmal**; jeder Abbruch druckt jetzt
  die offenen Funde und den Fortsetzungsbefehl.

### Changed

- **Die Red-Team-Aufträge behaupten keinen Stack mehr** (`BL-20`). Der
  ausgelieferte Default beschrieb eine statische Website — in jedem anderen
  Projekt eine **sachlich falsche** Behauptung, die das Modell übernimmt.
  Projektseitig übersteuerbar über `TEAM_REDTEAM_AUFTRAG_HARRY`/`_MARV`.
  Marvs Auftrag fragt zusätzlich, **was der gewöhnliche Pfad kostet** (`BL-21`,
  mit Schwelle: asymptotisch, kein Feintuning).
- **Der Red-Team-Fokus hat ein Verfallsdatum** (`BL-31`): an den Stand
  gebunden, nicht an die Prozessumgebung. Dazu seine **Bauform** — „welche
  bestehenden Verträge berührt das Neue?" (`BL-43`) — und die Auflage, dass
  Prüfpunkte in den **String** gehören, nicht in die Übergabenachricht
  (`BL-44`). Zwei neue Fragen in jedem Sweep-Prompt: Kontrollfluss statt
  Rumpfvergleich und die Durchzählung mitbenutzter Bedingungen (`BL-39`).
- **`A2 / 1,25` gilt nur für schreiblastige Sitzungen** (`BL-32`); reine
  Dateirotation zählt nicht mehr als Churn. Die A1-Regel nennt die vier
  Eigenschaften eines tauglichen Abo-Messwegs, statt ein Werkzeug zu nennen,
  das dem Kit nicht gehört (`BL-33`).
- **Zwölf Feld-Betriebslehren** in `doku/anhang-a.md` (`BL-35`…`BL-38`), die
  planwirksamen zusätzlich im Architekten-Briefing.

### Added

- **`./team-status.sh --altlast [N]`** (`BL-40`) — Produktivdateien ohne Diff
  seit N Kaskaden. Nur eine Kennzahl: Die Diff-Bindung ist der Grund, warum die
  Sweeps bezahlbar sind.
- **`kosten.py turns`** (`BL-37`) — das Turn-Profil stand in jedem Log und
  wurde nie ausgewertet. `vollautomatik.sh` druckt es im Abschlussbericht.
- **`team/tools/zitat_lint.py`** (`BL-50`, Stufe 2) — meldet Plandateien, die
  einen erledigten Backlog-Eintrag noch als offene Frage zitieren. Bewusst
  schmal: Der erste Anlauf fiel prompt in die eigene Falle und meldete drei
  Rückblicke im Roadmap-Dokument des Kits.
- **`plans/backlog-archiv.md`** (`BL-53`) — 58 abgetragene Einträge, wörtlich.
  Der aktive Backlog schrumpft von 154 KB auf 6 KB.

### Beim Bauen gefunden

- **`kit-test.sh` gab bei rotem Testlauf Exit 0 zurück** (`BL-59`) — `RC=$?` im
  `then`-Zweig eines `if ! cmd`. Rot für den Menschen, grün für jede Automatik.
- **Der scharfgestellte Guard-Rollback hätte die Kostenlogs des laufenden
  Aufrufs gelöscht** — `.team-logs/` ist ein untracked Verzeichnis außerhalb
  jeder Whitelist. `TEAM_GUARD_LAUFZEIT` nimmt die Artefakte der Shell aus der
  Bewertung.
- **Die `BL-27`-Prüfung hätte bei jedem `--budget` mitten im Lauf rot
  gemeldet** — `test_bl13` fing es beim Bauen ab und erzwang das richtige
  Merkmal.
- **`BL-42` und `BL-58` waren derselbe Fund**, zweimal aus demselben
  Feldprojekt gemeldet: Der erste Bericht blieb liegen, `--update` überschrieb
  den Feldfix, das Feld musste ihn erneut melden.

## [2.8.1] — 2026-08-14

**Ein Kit-Test, der nur dort scheitern kann, wo niemand hinsieht, ist keine
Zusicherung.** Aus dem Feldprojekt kam zurück, dass `test_zentrale_defaults`
den Soft-Cap per `source team/lib.sh` las — und `lib.sh` sourct in ihren ersten
Zeilen die `team.config.sh` des Projekts. Der Test maß damit den *Projektwert*
und behauptete, den *Bibliotheks-Default* zu prüfen. Im Kit-Repo (das gar keine
`team.config.sh` hat) und in jeder frischen Installation ist er deshalb immer
grün; rot wird er ausschließlich in einem Feldprojekt, das seine Caps
regelkonform angehoben hat.

### Fixed

- **`test_zentrale_defaults` misst wieder das Kit (`BL-58`).** Neu ist
  `_lib_default()`: Es liest die Zeile `NAME="${NAME:-wert}"` **statisch** aus
  `team/lib.sh`, statt die Bibliothek zu sourcen. Zurückgespielt aus
  `team-kit_project_platformer`, wo der Fix seit dem 2026-08-09 lief und ein
  `install.sh --update` auf 2.6.0 ihn überschrieben hatte — der `BL-12`-Fall,
  vor dem der Installer selbst warnt.
- **`kit-test.sh` meldete Fehlschläge rot und beendete sich mit Exit 0
  (`BL-59`).** `RC=$?` stand im `then`-Zweig eines `if ! cmd` — dort hat das
  `!` den Status bereits umgedreht, `$?` ist immer 0. Das Gate schrieb
  „FEHLGESCHLAGEN (Exit 0)" und gab genau diese 0 zurück: für jeden Aufrufer
  ein grüner Lauf. Gefunden bei der Gegenprobe zur neuen Stufe 5.
- **`gelb()` war in `kit-test.sh` nie definiert**, wurde aber im Fehlerzweig
  der Abgleich-Pfad-Erkennung aufgerufen — bei `set -e` hätte dort statt der
  Erklärung ein „command not found" mit Exit 127 gestanden.

### Added

- **`kit-test.sh` fährt die Regressionssuite zweimal — Stufe 5 ist neu:**
  einmal im Auslieferungszustand, einmal gegen eine Installation mit
  **angepasster** `team.config.sh` (Caps 10/20, Präfixe `fix(qa)`/`feature`,
  zwei Domänen). Verstellt wird nur, wozu die Config an Ort und Stelle einlädt;
  Pfade und Ordner bleiben unangetastet — die sind die Ablage, gegen die Tests
  gelten dürfen, nicht der Regler, an dem ein Projekt dreht. Schlägt der zweite
  Lauf fehl, nennt die Meldung die Klasse (Messstelle statt Zusicherung) und
  `_lib_default()` als Vorbild. Ein `grep`-Riegel davor stellt sicher, dass die
  `sed`-Anpassung überhaupt gegriffen hat — ein Schritt, der nichts verstellt,
  wäre derselbe Fehler eine Etage höher.
- **`test_projektwert_haelt_das_hard_groesser_soft_verhaeltnis`** — ebenfalls
  aus dem Feld zurückgespielt und dort vom Update mitgerissen. Er prüft
  ausdrücklich die **aufgelösten** Werte: `team_budget_check` wertet den
  Hard-Cap nur bei `hard > soft` aus, bei `hard == soft` verlieren Frank und
  Axel ihren harten Abbruch still. Genau diese Falle war bei der Cap-Anhebung
  im Feld beinahe zugeschnappt. Damit 281 Testfälle.

## [2.8.0] — 2026-08-13

**Das Interview redet jetzt mit dem Anwender, nicht mit dem Autor.** Ein Einzug
in `Project-Family-ERP` legte offen, dass die Fragen zwar korrekt waren, aber
nur für den verständlich, der die Mechanik dahinter schon kennt: Der Anwender
trug `tests/` in den *Prüfumfang* ein — den Ordner, den er zwei Fragen später
als *Schreibzone* vergab —, und ließ zugleich `main.py` und `bin/` weg, also
genau den Code, für den die Frage gebaut wurde.

### Changed

- **Jede Interview-Frage hat einen Vorspann in Anwendersprache.** Was die
  Antwort bewirkt, ein konkretes Beispiel und was ein falscher Wert kostet.
  Begriffe, die nur intern etwas heißen — „Produktivcode-Ordner", „Guard",
  „Domänen", „Smoke-Test" — stehen nicht mehr in der Frage, sondern werden
  erklärt: „Ordner mit dem Programmcode", „ein Wächter setzt das durch",
  „Kostenkonten", „Prüfbefehl".
- **Die Fragen kommen in neuer Reihenfolge:** erst Test- und Plan-Ordner, dann
  der Prüfumfang. Vorher wurde nach Code *außerhalb* gefragt, bevor feststand,
  welche Ordner die Rollen beschreiben dürfen — die Frage war zum Zeitpunkt
  ihres Erscheinens gar nicht beantwortbar.
- **Der Installer listet Kandidaten für den Prüfumfang auf.** Was in der Wurzel
  neben dem Produktivcode-Ordner liegt und nach Code aussieht (`main.py`,
  `bin/`, `deploy/`), steht jetzt zum Abschreiben in der Frage. Beiwerk —
  `docs/`, `data/`, Konfigurationsdateien, die Team-Entrypoints — ist gefiltert.
- **Die `BL-51`-Warnung sagt die Folge in einem Satz:** „Der Wächter, der sie
  von deinem Code fernhält, greift in diesem Ordner NICHT" — und nennt den
  sicheren Ausweg beim Namen (`team-plans/`).

### Fixed

- **Ein Schreibordner im Prüfumfang wird wieder herausgenommen.** Stand
  `tests/` in beiden Antworten, sagte der Rollen-Auftrag in **einem Absatz**
  „Du änderst NIEMALS Produktivcode (… und tests/)" und „Schreiben NUR unter
  tests/". Harrys Reproducer-Auftrag war damit widersprüchlich; welche Hälfte
  gewinnt, entschied das Modell pro Lauf neu. Der Installer entfernt die
  Kollision und begründet sie. Der Bestandsschutz für vorhandene Testdateien
  liegt ohnehin woanders (`BL-51`).
- **Die Schlussbefehle laufen auch bei Pfaden mit Leerzeichen.** `git -C
  /home/…/Projekt (copy) add -A` war nicht kopierbar — der Zielpfad steht jetzt
  in Anführungszeichen, im Einzug wie im `--update`.
- **Die Regeldatei nannte einen Platzhalter, den niemand füllt.** In
  `## Kostenkontrolle` stand `{{z. B. Sonnet via Claude Code — …}}` — kein
  echter Platzhalter (die Prüfung sucht `{{GROSSBUCHSTABEN}}`), also stand er
  **wörtlich so in jeder installierten `CLAUDE.md`**. Daneben vier weitere
  Substitutions-Leichen (`Soft-Cap `5``, `` `5`/`10` ``, ein nacktes
  `` (`sonnet`) ``) und ein Verweis auf `team-lib.sh`, die es seit dem
  `team/`-Namensraum nicht mehr gibt. Alle fünf Stellen nennen jetzt die
  **wirklichen** Variablennamen und ihre Defaults.
- **Stale Pfadnamen quer durch Kommentare und Docstrings.** `team-lib.sh` →
  `team/lib.sh`, `scripts/kosten.py` → `team/tools/kosten.py`,
  `scripts/beutebuch.py` → `team/tools/beutebuch.py`, `prompts/rolle-*.md` →
  `team/prompts/rolle-*.md`. Wer (Mensch oder Rolle) einem dieser Verweise
  folgte, landete im Leeren.
- **`team.config.sh` empfahl im Kommentar genau das, was `BL-9` verbietet.**
  Der Domänen-Block erklärte die zweite Domäne als „Arbeit an der
  Team-Infrastruktur" und gab `"app team"` als Beispiel — eine Zeile, die in
  einem Feldprojekt strukturell `0.0000` bleibt. Jetzt steht dort, warum EIN
  Konto der Normalfall ist und was mehrere kosten.
- **Doppelte Zeile und kaputte Auszeichnung in `TEAM.md`.**
  „Guard-Experimente nur in einem Wegwerf-Repo" stand zweimal hintereinander;
  im API-Key-Absatz war Fettschrift ineinander verschachtelt.

### Removed

- **`doku/anhang-a.md` war eine Wiki-Seite aus einem fremden Repo.** Sie trug
  Wiki-Frontmatter, **neun tote Links** (`../konzepte/…`, `../vorlagen/…`,
  `../index.md`), eine zweite Platzhalter-Konvention, die niemand füllt
  (`{{Plan-Ordner}}`, `{{loop-skript}}`, `{{ledger-datei}}`) — und vor allem
  eine Anleitung, **die Skripte zu generieren**, die das Kit längst ausliefert.
  Neu geschrieben als kit-native Warum-Schicht: −28 % Zeichen, ein einziger
  verbleibender Link, und ein Kopf, der sagt, wofür die Datei **nicht**
  zuständig ist. Die Abschnittsnummern `A.0`–`A.10` bleiben stabil, weil
  Regeldatei, Regel-Inventar und Backlog darauf verweisen.
- **`bootstrap/ermittlungsakten/` gelöscht.** Der Installer legt den Ordner
  direkt an; die Vorlage wurde nie kopiert.

## [2.7.1] — 2026-08-12

**Der Weg zurück ins eigene Projekt.** Zwei Lücken, die beide erst auffielen,
als die Frage lautete: „Was hat mein zukünftiges Ich in sechs Monaten
eigentlich zur Verfügung?" — Antwort: im Projekt liegt nur `TEAM.md`, der
README bleibt im Kit-Repo zurück.

### Added

- **`TEAM.md` erklärt jetzt, wie man auf eine neue Kit-Version hebt.** Bisher
  stand dazu **kein Wort** in der einzigen Anleitung, die im Zielprojekt liegt.
  Neu: der Befehl, was `--update` anfasst und was nicht, die `--force`-Warnung,
  und vor allem **der Schritt, den nur der Mensch machen kann** — die Regeln aus
  der neuen `CLAUDE.md` nachziehen, weil der Updater sie zum Schutz der
  Projektdaten nicht überschreibt. Mit dem kopierbaren `diff`-Befehl aus dem
  Fix unten.

### Fixed

- **Der Abgleich-Hinweis beim `--update` war nicht ausführbar.** Er nannte
  `diff <(…) <zieldatei>` — das `<(…)` stand für „die mit deinen Werten
  gerenderte Kit-Vorlage", nur sagte er nirgends, wie man die rendert. Der
  Befehl ließ sich nicht kopieren, und der Hinweis verlangte damit genau die
  Arbeit, die er abnehmen wollte. Bauart `BL-44`: angekündigt, aber nicht am
  wirksamen Ort ausführbar. Der Installer legt die gerenderte Fassung jetzt in
  einem Temp-Verzeichnis ab, **behält sie bei einer Abweichung** und druckt den
  fertigen Befehl samt Zeilenzahl der Unterschiede. **Bewusst nicht im Projekt
  abgelegt:** Eine uncommittete Datei außerhalb der Whitelist sieht für den
  Read-Only-Guard aus wie ein Regelbruch.

  Sechs neue Prüfungen in `kit-test.sh` Stufe 5 sichern das ab — dass kein
  Platzhalter mehr auftaucht, dass die genannte Datei existiert, gefüllte Werte
  trägt, der Befehl wirklich läuft, und dass sie **außerhalb** des Projekts
  liegt. Gegenprobe gefahren: Rückbau auf den alten Hinweis → rot.

## [2.7.0] — 2026-08-12

**Die Regeldatei wird geschnitten, und ein Gurt bewacht den Schnitt (`BL-56`).**

Jede Rolle startet über `claude -p`; Claude Code lädt dabei automatisch die
installierte `CLAUDE.md`. Bei ~25 Rollenaufrufen je Kaskade waren das rund
**990k Token allein für Regeln** — und die Rolle bekam ~11k Token Projektregeln
gegen ~500 Token eigenen Auftrag. Der Dreischnitt bringt die Vorlage auf
**26.985 B (−31,6 %)** nach dem Grundsatz **„das WANN gilt für alle, das WIE nur
für einen"**. Zuschnitt am Ende: **Rollen-Regeln → Regeldatei, Bedienung →
`TEAM.md`, Bau → Anhang A.**

Damit dabei nichts still verschwindet, entstand zuerst das **Regel-Inventar**:
73 klassifizierte Aussagen, 61 davon geltendes Recht mit wörtlichem Zitat und
Trägerdatei, geprüft als Stufe 7 in `kit-test.sh`.

Dazu ein **Einstieg für Entwickler, die das Kit nicht kennen** — bisher benutzte
`TEAM.md` ein Dutzend Fachbegriffe, ohne sie irgendwo zu erklären.

### Added

- **Einstieg für Neulinge in `TEAM.md` — „Worum es überhaupt geht" plus
  Glossar.** Bisher traf ein Entwickler, der das Kit nicht kennt, in den **ersten
  32 Zeilen** auf vier undefinierte Begriffe (*Guard*, *Sweep* in Zeile 17;
  *Kaskade*, *Cap*, *Closeout* in Zeile 32) — und ein Glossar gab es nirgends,
  obwohl *Kaskade* 14×, *Guard* 9×, *Beutebuch* und *Ledger* je 7× vorkommen. Neu
  sind ein Abschnitt, der das Modell in drei Punkten erklärt (geplant wird vor dem
  Bauen · Finder ≠ Fixer · jeder Lauf wird gezählt), und ein Glossar mit 15
  Begriffen à einem Satz. Beides steht **nach** der Commit-Warnung: Ein Test
  besteht darauf, dass die teuerste Warnung des Kits im Kopfbereich bleibt — er
  hat den ersten Entwurf zu Recht abgelehnt. `TEAM.md` wird vom Menschen gelesen,
  nicht bei jedem Rollenaufruf geladen; der Zuwachs kostet kein Token-Budget.

- **Regel-Inventar — der Sicherheitsgurt vor dem Umbau der Regeldatei
  (`BL-56`, Vorbedingung aus A.10).** [`doku/regel-inventar.md`](doku/regel-inventar.md)
  klassifiziert **72 Aussagen** der ausgelieferten Regeldatei über alle 10
  Abschnitte als `NORM` (60), `HERLEITUNG` (11) oder `HISTORIE` (1) — mit
  wörtlichem Zitat. [`kit-regelinventar.py`](geteilt/kit-regelinventar.py) prüft als
  **Stufe 7 in `kit-test.sh`**, dass jedes `NORM`-Zitat wörtlich in
  `bootstrap/CLAUDE.md.vorlage` steht, dass kein Abschnitt unerfasst ist und
  dass das Inventar keine Abschnitte nennt, die es nicht mehr gibt.

  **Der Gurt verbietet keine Änderung — er macht sie sichtbar.** Wer eine Regel
  umformuliert oder streicht, bekommt rot und muss die Inventarzeile **benannt**
  nachziehen, statt sie stillschweigend verschwinden zu lassen. Gegenprobe über
  die volle Kette gefahren: entfernte Regel → `kit-test.sh` Exit 1 mit
  Namensnennung der verschwundenen Regel; ebenso neuer Abschnitt ohne
  Inventarzeile und Inventar-Leiche.

  Zwei Bauentscheide, die auch für Nachbauten gelten (in A.10 nachgetragen):
  Verglichen wird **normalisiert** (Blockquote-Marker, Betonungszeichen,
  Zeilenumbrüche raus) — sonst scheitert ein wörtlich richtiges Zitat an einem
  `**nie**` mitten im Satz. Und der Prüfer bewacht die **Vorlage**, nicht die
  Installation: Ein Feldprojekt darf seine `CLAUDE.md` umformulieren (so hält es
  `test_bl55` ausdrücklich fest), die Vorlage darf es nicht unbemerkt.

### Changed

- **Repo-Pflege nach dem Umbau — die zitierenden Stellen nachgezogen.** Genau
  die Gegenrichtung, die die eigene Pflichtzeile verlangt („welche Stellen
  zitieren, was sich geändert hat?"). `README.md`: Aufbau um
  `kit-regelinventar.py` und `doku/regel-inventar.md` ergänzt, `kit-test.sh` als
  **7**-stufig beschrieben, und die Regel „Regeln ändern heißt: Inventarzeile
  nachziehen" unter „Grenzen" aufgenommen. `doku/anhang-a.md` A.9: Der Satz „der
  operative Vertrag steht im Vorlagenblock" stimmte nach dem Schnitt nur noch
  halb — er ist jetzt **zweigeteilt** beschrieben (WANN im Vorlagenblock, WIE im
  Architekten-Briefing). `doku/regel-inventar.md`: `anhang-a` fehlte in der
  Träger-Liste, obwohl der Prüfer ihn längst kennt; dazu der Zuschnitt in einem
  Satz (Regeldatei = was Rollen befolgen, `TEAM.md` = was der Strippenzieher
  tut, `anhang-a` = warum es so gebaut ist). `BL-56` trug noch die Zahlen seiner
  Frühfassung (72/60 statt 73/61; 5,7 KB und „14 KB", real 8,2 KB und knapp
  17 KB) und einen fehlenden Satztrenner — beides berichtigt.

  **Nicht geändert, weil geprüft und korrekt:** die „75 Dateien" im README. Eine
  Zählung der echten Installation ergibt 128 Dateien, davon sind 53
  `__pycache__`/`.pytest_cache`/Logs — **git-getrackt sind exakt 75**.

- **Dreischnitt, dritter Block: `## Loop-Mechanik & Auth` von 6,3 auf 2,8 KB
  (`BL-56`).** Der Befund dahinter: **Das meiste hieran macht die Shell, nicht
  die Rolle.** Auth-Auflösung, Retry-Deckel, Cap-Durchsetzung und
  Key-Verdrängung laufen in `team/lib.sh`, **bevor** eine Rolle startet — sie
  las seitenweise Verhalten mit, das sie nicht beeinflussen kann. Geblieben ist,
  wonach eine Rolle handelt: `.ralph-state`, „429 weicht den Guard nicht auf",
  Exit 42 unverändert durchreichen, Guard auf **jedem** Pfad, Smoke-Test im
  Vordergrund. Zwei Regeln wechselten den Träger zum **Menschen**: die
  `.bashrc`-Key-Falle (bindet den Strippenzieher an seiner Maschine, keine Rolle
  kann sie befolgen) steht jetzt in `TEAM.md` samt ~13,8-USD-Feldbeleg; „Die
  Arbeit ist meistens fertig" stand dort längst wortgleich.

- **Dreischnitt, zweiter Block: `## Kaskaden-Planungsregeln` von 8,2 auf 5,3 KB
  (`BL-56`).** Das ausführliche Verfahren (Plankopf, Scharfschalt-Sequenz
  Schritt für Schritt) steht im Briefing des Architekten; in der Regeldatei
  bleibt je Regel der normative Kern plus alles, was **andere** Rollen
  begrenzt. **Testgepinnt und deshalb unangetastet:** die Gegenprobe-Regel samt
  Feld-Beleg (`test_bl49` verlangt „zwei fremde Werte"/„sieben"), die
  Pflichtzeile „nebenbei eingelöst — wer zitiert sie?" und die Schreibweise
  `Kit-BL-<N>` (`test_bl50`).

  **Ein Test hat einen echten Fehler abgefangen.** Die kopierfertige Gliederung
  des Abschluss-Docs war mit weggefallen — `test_bl50` verlangt sie
  ausdrücklich, weil die Pflichtzeile **im** Block stehen muss und nicht
  daneben: Die Gliederung ist das, was ein kalt startendes Architekt-Ich
  kopiert, und beim Kopieren fiele die Frage sonst weg. Genau die Bauart aus
  `BL-44`. Der Block wurde **wörtlich aus dem Altstand** zurückgeholt, nicht neu
  getippt.

- **Dreischnitt, erster Block: `## Kostenkontrolle` von 8,6 auf 3,2 KB
  (`BL-56`).** Das **WANN** gilt für alle und bleibt in der Regeldatei
  (Zwei-Schwellen-Modell, was ein überschrittener Cap für die eigene Arbeit
  bedeutet, Token-Sparregeln, und die Pflicht, den Kostenabschluss **nach** dem
  Lauf im Architekten-Closeout zu machen, **nie** in einer Loop-Stufe). Das
  **WIE** — Verben, Ledger-Zeilen, Domänen, Abo-Messung, Prüfung gegen eine
  zweite Quelle — steht jetzt im Briefing des Architekten; keine andere Rolle
  ruft diese Befehle je auf. Drei Herleitungen wanderten nach Anhang A.9
  (`~16 USD`-Auslöser, warum `--ledger-pruefen` kein hartes Gate ist, warum
  **eine** Domäne der Normalfall ist).

  Der Umbau war **kein Umzug, sondern ein Dedup**: `rolle-architekt.md` trug
  die Substanz bereits (Closeout mit Pflichtfrage, `--addieren`/`--ersetzen`,
  `--ledger-pruefen`, Abo-Messung). Ergänzt wurden nur die drei Regeln, die
  wirklich fehlten. Der Regel-Inventar-Gurt meldete **genau drei** NORMen mit
  gewechseltem Träger und sonst nichts — der Beleg, dass Text gekürzt wurde und
  keine Geltung. Vorlage: **39.472 → 33.358 B (−15,5 %)**.

- **Die Regeldatei-Vorlage trägt keine Aktenlage mehr (Vorstufe zu `BL-56`).**
  Die mehrsprachigen Fassungen des T.E.A.M.-Akronyms stehen jetzt in
  `bootstrap/TEAM.md` — sie richten sich an den Menschen, nicht an die Rollen,
  und die Bedienanleitung ist ihr Ort. Wörtlich verschoben, per Diff gegen den
  alten Stand geprüft. Dazu vier Entscheid-Provenienzen entfernt („Entscheid
  2026-07-13", „die frühere Regel ist aufgehoben"), deren Aktenlage
  `doku/anhang-a.md` A.3 **bereits wörtlich trägt** — das war Doppelung, keine
  Streichung. Die Regeln selbst sind unverändert; kein Beleg, kein
  `✅ erprobt`-Marker und keine Geltung angetastet. **753 B, 1,9 %.**

  Der Anlass ist die Messung in `BL-56`: Jede Rolle startet über `claude -p`,
  Claude Code lädt dabei automatisch die installierte `CLAUDE.md` — ~11k Token
  je Aufruf, ~990k Token je Kaskade allein für Regeln. Mehr als diese 753 B war
  ohne Geltungs-Entscheid nicht zu holen: Die Dateigröße ist **testgeschützte
  Absicht** (`test_bl49`, `test_bl17` verlangen den Feld-Beleg ausdrücklich *in*
  der Regeldatei, `test_bl50` beide Träger). Der eigentliche Hebel — 14 KB, die
  nur den Architekten binden und trotzdem in jeden Loop-Rollen-Aufruf geladen
  werden — steht als benannter Entscheid in `BL-56`.

## [2.6.0] — 2026-08-12

**Das Kit zieht in gewachsene Codebasen ein (`BL-51`, `BL-52`).**

Beide Befunde stammen aus der Analyse einer fremden Bestandscodebasis
(`Project-Family-ERP`, 2026-08-11, nur gelesen). Der rote Faden: **Zwei
tragende Defaults sind Annahmen über ein leeres Repo — und sie scheitern
lautlos.** Ein belegter Plan-Ordner macht die Read-Only-Rollen zu
Schreibberechtigten, ohne dass der Guard je anschlägt; ein Prüfumfang aus
genau einem Ordner lässt den Einstiegspunkt ungeprüft, und der Sweep meldet
trotzdem „sauber".

### Added

- **`TEAM_WEITERER_CODE` — der Prüfumfang endet nicht mehr am
  Produktivcode-Ordner (`BL-52`).** Leerliste aus Dateien **und** Ordnern
  (`"main.py bin/"`), die mitgeprüft werden, ohne unter `TEAM_PRODUKTIVCODE` zu
  liegen. Sie erscheint in der Scope-Zeile des Sweeps
  ([`team/redteam.sh`](bash/redteam.sh)), in der **eisernen Regel** von Red Team
  und Axel — mitgeprüft heißt **genauso tabu**, nicht „freigegeben" — und in
  Franks Fix-Auftrag ([`entry/frank.sh`](bash/entry/frank.sh)), damit er den Fund
  dort reparieren darf, wo er liegt. Das Aufnahme-Interview fragt danach
  (neunter Wert); im neuen Projekt bleibt der Wert leer und **kein Wortlaut
  ändert sich** — dafür gibt es eine eigene Gegenprobe.
  **Nicht** umgesetzt wurde die Backlog-Skizze, `TEAM_PRODUKTIVCODE` selbst zur
  Liste zu machen: Der Wert trägt die Invariante „endet auf genau einen
  Schrägstrich" ([`entry/team.config.sh`](bash/entry/team.config.sh)), an der
  `**`-Muster, Guard-Meldungen und ein Test-Regex hängen — und eine Liste, die
  auch einzelne Dateien enthalten darf, kann sie nicht halten.
- **Der Installer erkennt eine belegte Schreibzone (`BL-51`).** Nach dem
  Interview prüft er Plan- **und** Test-Ordner auf Inhalt, nennt die gefundenen
  Dateien und die Folge in einem Satz („Harry, Marv und Axel dürfen in diesem
  Ordner schreiben und löschen — der Guard schlägt dort NICHT an"), und bietet
  interaktiv einen anderen Ordner an. **Gewarnt, nicht verboten:** Ein bewusst
  geteilter Ordner kann legitim sein.
- **`TEAM_TEST_ORDNER_BESTAND` / `TEAM_PLAN_ORDNER_BESTAND`.** Wer den Ordner
  behält, bekommt den Bestand in `team.config.sh` vermerkt — und aus dieser
  Quelle nennen die Rollen-Prompts ihn als **fremdes Eigentum**: neue Dateien
  anlegen ja, Bestehendes ändern oder löschen nein, „auch nicht, was in dieser
  Aufzählung fehlt". Der letzte Halbsatz ist tragend: Die Liste ist bei zwölf
  Einträgen gekürzt und veraltet, sobald jemand eine Datei hinzulegt.
  **Das ist eine Prompt-Auflage, keine Mechanik** — der Guard kann sie nicht
  erzwingen, weil die Pfade auf seiner Whitelist stehen. Die Config sagt das an
  Ort und Stelle und nennt die harte Variante: ein eigener, leerer Plan-Ordner.
- **`kit-test.sh` fährt einen sechsten Schritt: den Einzug in eine gewachsene
  Codebasis.** Zweites Wegwerf-Repo mit belegtem `plans/`, gewachsener
  `tests/`-Suite und `main.py` in der Wurzel — die Lage aus Family-ERP. Zwölf
  Zusicherungen, darunter beide **Gegenproben** im leeren Repo: Dort schweigen
  Installer und Update. Eine Warnung, die immer erscheint, erzieht zum
  Wegsehen (`BL-14`).

### Changed

- **`install.sh --update` schaut auf das, was es nicht anfassen darf.** Es
  fasst `team.config.sh` weiterhin nicht an, meldet aber (a) den vermerkten
  Bestand in der Schreibzone und (b) — nur wenn `TEAM_WEITERER_CODE` fehlt und
  in der Wurzel wirklich Code liegt — die ungeprüften Dateien samt der Zeile,
  die man einträgt. Gemeldet wird **ausschließlich**, was in der Config steht
  oder wirklich existiert: Nach dem Einzug ist der Plan-Ordner die
  Arbeitsfläche des Teams, dort ist „fremd" nicht mehr unterscheidbar.
- **Doku-Träger nachgezogen:** [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage)
  (Red-Team-Kapitel: Prüfumfang **und** Schreibzone sind im Bestand keine
  Selbstverständlichkeit), [`bootstrap/TEAM.md`](bootstrap/TEAM.md) (eigener
  Abschnitt „Zog das Team in eine gewachsene Codebasis ein?") und die
  [README](README.md).

### Tests

- **Zwei neue Testdateien, 280 statt 267 Testfälle.**
  `test_bl52_pruefumfang.py` und `test_bl51_bestandsordner.py` prüfen am
  **echten Prompt**: `harry.sh` läuft mit gestubbter CLI, die den Prompt
  wegschreibt. Ein Test gegen den Skript-Quelltext hätte die Kopplung
  „Wert gesetzt ⇒ steht im Auftrag" nicht gezeigt.
- **Die Fixtures setzen die Bestandswerte selbst zurück.** Die Config benutzt
  `${VAR:-default}` — eine **leere** Umgebungsvariable fällt auf den
  Projektwert zurück. Ohne das wäre die Gegenprobe „ohne Bestand kein Block"
  in genau den Projekten rot geworden, für die das Feature gebaut ist.
- **Gegenprobe gefahren:** ohne den Fix 11 der 13 neuen Fälle rot; die zwei
  Gegenproben (leerer Wert ⇒ unveränderter Wortlaut) bleiben erwartungsgemäß
  in beiden Richtungen grün.

## [2.5.0] — 2026-08-11

**Sechs Feldbefunde aus `team-kit_project_platformer` (K29–K33), abgearbeitet.**

Der rote Faden: **Ein Vorgang, der Geld gekostet hat, muss eine Spur
hinterlassen, die man von „nichts passiert" unterscheiden kann.** Fünf der
sechs Einträge sind Varianten davon — ein Erfolgslog ohne Auftrag, ein
Kostenlog ohne Inhalt, ein Sweep ohne Fund, eine Warnung ohne zutreffende
Ursache, ein abgetragener Backlog-Punkt ohne Nachzug in den Zitaten.

### Added

- **Vierte Fehlerklasse wird erkannt und benannt: „Stufe fertig, Quittung
  fehlt" (`BL-41`, zweite Hälfte).** Neben Erfolg, echtem Fehler und
  Session-Limit gibt es einen vierten Ausgang: Die Rolle startet einen
  Hintergrund-Task/Monitor/Wakeup und wartet auf eine Benachrichtigung, die es
  headless nicht gibt. Das Log trägt dann `subtype: success`, `is_error:
  false` — **es sieht aus wie ein Erfolg** —, nur das Promise fehlt. Vier
  Vorfälle im Feld, **19,47 USD**, jedes Mal für Arbeit, die fertig und grün
  war. Die bisherige Meldung („KEIN Promise — Log prüfen") schickte den
  Menschen in ein Log, das Erfolg meldet, und von dort in den **Plan** statt in
  den Fehlermodus; dreimal folgte darauf ein Neubau, der die bezahlte Arbeit
  wegwarf.
  **Neu:** `team_result_meldet_erfolg` + `team_quittung_fehlt_melden` in
  [`team/lib.sh`](bash/lib.sh); [`ralph.sh`](bash/entry/ralph.sh) endet in diesem
  Fall mit dem eigenen **Exit 43** und druckt den Prüfweg (committet? Suite
  grün? dann von Hand quittieren), [`vollautomatik.sh`](bash/entry/vollautomatik.sh)
  und [`halbautomatik.sh`](bash/entry/halbautomatik.sh) reichen ihn als eigenen
  Ausgang durch — nicht als „Fehler". **Geprüft wird die Struktur, nicht der
  Wortlaut:** Die drei Feldvorfälle formulierten es dreimal anders („background
  pytest run and monitor", „fallback check / wakeup", „set up a monitor to catch
  its completion"), und die vierte Variante schreibt jemand morgen. Die
  Vordergrund-Auflage in `SMOKE_ZEILE` (2.4.x) bleibt als **Prävention** — sie
  hat in K33 nicht gehalten, obwohl sie wortgleich installiert war: Ein Satz aus
  dem ersten Turn konkurriert nach 65 Turns mit dem gesamten seither gewachsenen
  Kontext. Prävention per Prompt skaliert **gegenläufig zur Stufenlänge**.
- **Verworfene Versuche bekommen einen Ersatzzettel (`BL-46`).** Scheitert ein
  Aufruf so, dass das Log unlesbar bleibt (im Feld: **0 Byte nach 47 Minuten**),
  schreibt `team_claude` an seine Stelle einen Zettel mit dem, was belegbar ist:
  `total_cost_usd: null`, `team_versuch: "verworfen"`, gemessene Dauer.
  **Nicht geschätzt — sichtbar gemacht.**

### Fixed

- **`kosten.py summe` zählte ein unlesbares Log still als 0.0000 (`BL-46`).**
  Das ist der Pfad, den Live-Kontostand, `--budget` und die Pro-Lauf-/
  Pro-Stufe-Deckel benutzen: Der Abo-Gegenwert von 47 Minuten fiel aus **jedem**
  Kostenabschluss, der Deckel bekam auf diese Hälfte keinen Griff, und die Stufe
  erschien als die **billigste** der Kaskade, obwohl sie als teuerste angesetzt
  war. **Neu:** Die Zahl auf stdout bleibt unverändert (Aufrufer parsen sie), der
  Hinweis geht nach stderr — „N verworfener Versuch(e), zusammen 47 min, Kosten
  UNBEKANNT".
- **`ledger-pruefen` schlug wegen desselben Logs dauerhaft falschen Alarm
  (`BL-46`).** P2 meldete die Kaskade als verdächtig, nannte zwei Ursachen, von
  denen keine zutraf, und empfahl als Abhilfe `--ersetzen` — eine Handlung, die
  nach `BL-5` den Altwert vernichtet. Der Wächter empfahl also, Geld zu
  verlieren, und es gab **keinen dokumentierten Weg**, den Rest loszuwerden.
  **Neu:** Unarchivierte Logs **ohne Kostenbeleg** (Ersatzzettel oder kaputt)
  sind ein Hinweis statt einer Warnung und nennen den Weg heraus; der
  `BL-5`-Fall (echtes unarchiviertes Log) bleibt unverändert eine Warnung.
  `--rollen-abschluss` archiviert Ersatzzettel **mit** (sie können nicht doppelt
  zählen) und sagt beim Buchen, dass der Betrag nachweislich unvollständig ist;
  eine wirklich unlesbare Datei bleibt liegen — mit genanntem Ausweg.
- **Ein Sweep ohne Fund war von einem abgebrochenen Sweep nicht zu
  unterscheiden (`BL-47`).** Im Feld: Marv, 9 Minuten, **3,1418 USD**, eine
  einzige committete Datei (ein Sondenskript), null Beutebuch-Zeilen — und
  trotzdem Commit-Botschaft „neue Funde/Reproducer" plus Protokollzeile „Funde
  committet. Übergabe an Frank." Inhaltlich war das Nichtfinden richtig; der
  Fund ist die **Ununterscheidbarkeit**: Eine read-only-Rolle hat weder
  Statuswechsel noch Produktivdiff, an dem sie sonst auffiele. **Neu:**
  [`redteam.sh`](bash/redteam.sh) zählt die **wirklichen** neuen Funde
  (`next-id` vorher gegen nachher — die Zahl lag längst vor) und schreibt sie in
  Commit-Botschaft **und** Protokoll: „1 neuer Fund" / „keine neuen Funde",
  „Geprüft, KEINE neuen Funde … Keine Übergabe an Frank." Dazu im Sweep-Auftrag
  die fehlende Pflicht: Ein Wegwerf-Skript wird **gelöscht** oder als
  `HM-<Nr>`-Reproducer **benannt** — was in `tests/` bleibt, braucht einen Namen
  und einen Fund.
- **Die Abo-Key-Startwarnung zeigte nach einem API-Fallback auf die falsche
  Ursache (`BL-48`).** Sie empfahl, den Key „aus `.bashrc`" zu nehmen — dort lag
  keiner. Gesetzt hatte ihn der API-Fallback der **vorigen Stufe** im selben
  Prozessbaum. Weil die Warnung nur **einmal pro Prozessbaum** feuert,
  verbrauchte der Fehlalarm zusätzlich genau das Fenster, das dem echten Fall
  zusteht (dort real ~13,8 USD Leerlauf über API). **Neu:**
  `team_resolve_auth_mode` markiert einen **selbst geladenen** Key
  (`TEAM_KEY_AUS_FALLBACK`); die Meldung sagt dann, was wirklich passiert ist,
  und **verbraucht das Warnfenster nicht**.

### Changed

- **Zentrale Werte werden gegengeprobt, nicht gegrept (`BL-49`).** Neue Regel in
  den bauenden Briefings (Ralph, Frank) und in der Aushärtungs-Checkliste: Wer
  eine Konstante/einen Default/einen Schwellwert ändert, fährt sie probeweise
  gegen **zwei fremde Werte** (höher/niedriger), lässt die Suite laufen und
  setzt den Wert **nachweislich zurück**. Grund: Eine *arithmetische* Kopplung
  ist per Textsuche unauffindbar — im Feld fand `grep` nach Name und altem Wert
  **fünf** Stellen, das Verstellen **sieben**; die zwei zusätzlichen wären beim
  nächsten Tweak an unerklärlicher Stelle rot geworden.
- **Der Closeout pflegt jetzt auch die Gegenrichtung (`BL-50`, Stufe 1).**
  Erledigte Backlog-Einträge abzutragen funktionierte; **nichts** pflegte die
  Stellen, die den Backlog **zitieren** — Skizzen und Kandidatenlisten
  begründen ihre offenen Fragen mit Backlog-Nummern und veralten still. Der
  Fehler schlägt beim **Vorlegen der Kandidaten** zu, also nachdem eine Option
  formuliert wurde, die es nicht mehr gibt (im Feld: drei Kaskaden lang eine
  Prämisse, die der zitierte Eintrag selbst widerlegte). **Neu:** Pflichtzeile in
  Abschnitt 4 der Abschluss-Gliederung *(„Welche offenen Punkte hat dieser Lauf
  **nebenbei** eingelöst, und wer zitiert sie?")* — in der Gliederung selbst, nicht
  nur in der Prosa daneben —, dazu die Schreibweise `Kit-BL-<N>` für fremde
  Backlog-Nummern. **Offen bleibt Stufe 2**, der maschinelle Lint: Roh gemessen
  lag seine Trefferquote bei ~40 % (sechs von zehn Markierungen waren legitime
  Rückblicke); roh ausgeliefert wäre er die Falle aus `BL-14` — eine Warnung, die
  bei jedem Aufruf erscheint und zum Wegsehen erzieht.
- **Sechs neue Testdateien, 267 statt 232 Testfälle.** Jeder Eintrag mit
  Gegenprobe: Mit zurückgerollten Quellen fallen **25** der neuen Zusicherungen,
  keine bestehende. `BL-41`, `BL-47` und der Abschlusspfad von `BL-46` werden
  über die **wirkliche Bedienoberfläche** geprüft (`ralph.sh`/`harry.sh` gegen
  ein Wegwerf-Repo mit gestubbter CLI), nicht nur auf Bibliotheksebene.

## [2.4.4] — 2026-08-02

**Zwei Kennzahlen, die im Closeout das Falsche behaupteten.**

Beide aus dem Feld (`team-kit_project_platformer`, Architekt-Closeout K3),
beide gefunden beim Nachrechnen des Endstands — nicht von einem Werkzeug.
Kein Rechenfehler: Das Ledger war jedes Mal korrekt, falsch war, was die
Anzeige über die Zahlen **sagte**.

### Fixed

- **`--budget` behauptete „nicht im Gesamt enthalten" — auch dann, wenn die
  Architekten-Zeile sehr wohl enthalten war (`BL-18`).**
  [`entry/team-status.sh`](bash/entry/team-status.sh) druckte den Zusatz
  **unbedingt**, obwohl `team_architekt_stand` zwei Modi hat: Im Modus
  `geschätzt` stammt der Wert aus der A2-Churn-Schätzung und steht in **keiner**
  Ledger-Zeile — der Zusatz stimmt. Im Modus `echt` stammt er aus einer
  **Ledger-Zeile** der laufenden Kaskade, und die summiert
  `team_kontostand_gesamt` mit — der Zusatz ist dann falsch. Der Modus schaltet
  ausgerechnet **beim Kaskaden-Abschluss** um, also genau in dem Moment, in dem
  die Zahl abgelesen und weitergegeben wird. Im Feld: Anzeige „Architekt (echt,
  nicht im Gesamt enthalten): 9.7000" bei „Gesamt: 71.5706" — der beim Wort
  genommene Kontostand wäre **81,27 statt 71,57 USD** gewesen, 13 % zu viel.
  **Neu:** Der Zusatz hängt am Modus (`echt` ⇒ „im Gesamt enthalten"), und die
  Beschriftung nennt den Bezugsrahmen: `Architekt K3 (echt, im Gesamt
  enthalten)`. Denn der Wert gilt für **eine** Kaskade, während jede andere
  Zeile des Blocks lebenslang kumuliert — ohne Rahmen las man 9,70 als
  Lebenssumme des Architekten (real: 37,30). Die Nummer liefert die neue
  `team_architekt_kaskade`; `team_architekt_stand` behält seinen
  Zwei-Felder-Vertrag, an dem `team-status.sh` und drei Testdateien hängen.
- **Dieselbe Einladung zum Doppeladdieren stand im zweiten Block (`BL-18`,
  Nachzug).** Die Momentaufnahme (`./team-status.sh` ohne Argument) zeigte die
  reine A2-Schätzung — „Architekt (geschätzt, A2)" — direkt über
  „Gesamt-Kontostand (inkl. Ledger)". Nach dem Buchen stand dort also eine
  **Schätzung** neben einer Summe, welche die **echte** Zeile bereits enthält,
  und die Beschriftung war modusblind. **Neu:** Beide Ansichten bauen ihre
  Beschriftung aus **einer** Quelle (`status_architekt_zeile`); zwei Anzeigen
  derselben Kennzahl können nicht mehr auseinanderlaufen. Ein eigener Testfall
  hält genau das fest.
- **`--rollen-abschluss` schrieb eine Notiz wortgleich in zwei Zeilen mit
  verschiedener Bedeutung (`BL-19`).** Seit `BL-4` ruft die eine
  Bedienhandlung zwei Verben mit demselben `--notiz` auf: `rollen-abschluss`
  bucht `.team-logs`, `ralph-abschluss` bucht `.ralph-logs`. Ein Text kann aber
  höchstens eine der beiden Zeilen beschreiben — im Feld trug Ralphs Zeile über
  **vier Baustufen** die Notiz „Harry/Marv-Sweeps + Frank HM-6". Das Ledger ist
  die maschinelle Wahrheit für ein kalt startendes Architekt-Ich, und dieses
  Feld ist die **einzige** Prosa-Spur je Zeile. Ein Rückfall obendrein: Genau
  diese Beschwerde stand schon in Feld-`BL-5`, der `BL-4`-Fix hat sie
  strukturell wieder eingebaut.
  **Neu:** [`kosten.py`](geteilt/tools/kosten.py) setzt den Vorspann selbst, aus
  der Zielrolle — `Rollen: …` / `Bau: …`, für projekteigene Rollen deren Name.
  Kein zweiter Bedienparameter: Die Bedienung bleibt einhändig, und ein
  optionales `--notiz-ralph` wäre dieselbe Falle wie das „optional" in `BL-15`
  gewesen — was man setzen *kann*, setzt im Closeout niemand.

### Changed

- Die `Gesamt`-Zeile in `--budget` heißt zur Abgrenzung von der
  kaskadenscharfen Architekt-Zeile jetzt „(Basis + laufend), lebenslang".
- Leseregeln zu beiden Kennzahlen in [`bootstrap/TEAM.md`](bootstrap/TEAM.md)
  und im Architekten-Briefing; Bau-Details als Lehren in
  [`doku/anhang-a.md`](doku/anhang-a.md) A.9. Dabei fiel dort eine seit `BL-5`
  veraltete Aussage auf („ein zweiter Aufruf **ersetzt** die Zeile" — er bricht
  seither ab) und wurde mitkorrigiert.
- Zwei neue Regressionstests (`test_bl18_…`, `test_bl19_…`), beide mit
  gefahrener Gegenprobe. Die Installation fährt jetzt **228** Tests.

## [2.4.3] — 2026-08-02

**Der Guard urteilte ohne Ausgangszustand — und die einzige Verifikation, die
zwischen Doku und Testaufruf schaut, gab es nicht.**

Zwei Entscheide des Strippenziehers, beide gebaut. `BL-16` war der letzte
offene Feld-K2-Befund; `BL-17` kam aus demselben Feld nach.

### Fixed

- **Der Read-Only-Guard schrieb jede schmutzige Datei der laufenden Rolle zu
  (`BL-16`, Ebene 1).** [`team_guard_verify`](bash/lib.sh) bildete die
  Verletzerliste aus `git diff --name-only` **plus** `git status --porcelain`
  und hatte **keinen Ausgangszustand**: Sie wusste nicht, was beim Rollenstart
  bereits schmutzig war. Jeder fremde Schreiber — eine parallele Sitzung, eine
  Handänderung, ein abgebrochenes Werkzeug — wurde der Rolle angelastet **und**
  hart zurückgesetzt. Der eigene Kommentar der Funktion („schützt parallele/
  legitime uncommittete Arbeit") galt nur gegenüber dem blanko `reset --hard`,
  das sie ablöste; das chirurgische `git checkout -- <pfad>` zerstört fremde
  Arbeit genauso, nur gezielter.
  **Neu:** `team_guard_begin` hält `TEAM_GUARD_VORHER`, einen Schnappschuss mit
  **Blob-Hashes**. Der Hash ist der Punkt: Ein reiner Pfadabgleich wäre ein
  Freibrief für jede Rolle, die eine ohnehin schmutzige Datei zusätzlich
  verändert. Unverändert ⇒ fremd, kein Rollback, keine Zuschreibung.
  Verändert ⇒ ihre Sache. Bei nicht sauberem Baum warnt `team_guard_begin`
  laut und nennt die Pfade — **warnen statt abbrechen**, weil uncommittete
  Arbeit der Normalfall ist und ein harter Abbruch legitime Läufe erschlüge.
- **Eine Guard-Verletzung kassiert den Übergriff, nicht die Arbeit (`BL-16`,
  Ebene 2).** Bisher übersetzten [`entry/axel.sh`](bash/entry/axel.sh) und
  [`team/redteam.sh`](bash/redteam.sh) jeden Übergriff sofort in `RC=1`. Damit
  zählte im Feld eine **fertige, korrekte** Ermittlung als „Aufruf
  fehlgeschlagen" → Stagnationszähler → Lauf gestoppt.
  **Neu:** `team_guard_urteil <rolle> <übergriff> <ergebnis>`. Liegt das
  Ergebnis der Rolle vor — bei Axel Akte **und** Statuswechsel, bei Harry/Marv
  die Sweep-Quittung —, zählt die Runde. Der Grenzübertritt ist zu diesem
  Zeitpunkt bereits chirurgisch zurückgerollt und laut gemeldet; ein
  zusätzlicher Fehlschlag bestraft nur noch das Falsche. Fehlt das Ergebnis,
  bleibt es beim Fehlschlag.
- **Die Guard-Meldung trennt die beiden Fälle jetzt sprachlich.** „**DIESE
  ROLLE** hat die folgenden Pfade geändert" vs. „**NICHT angelastet** (beim
  Rollenstart bereits geändert, seither unverändert)". Im Feld wurde der
  Übergriff zunächst der falschen Rolle zugeschrieben, weil die Pfadliste im
  Log neben ihrem Namen stand — belegt war das nirgends.

### Added

- **Die Verifikationskette darf sich den Erfolg nicht selbst einrichten
  (`BL-17`).** Regel in [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage)
  und [`bootstrap/TEAM.md`](bootstrap/TEAM.md): Jeder Befehl, den die Doku
  einem Menschen nennt, muss in der Verifikation **buchstabengetreu**
  vorkommen — gleiche Argumente, gleiche Umgebung, kein zusätzliches
  `PYTHONPATH`, kein stilles `cd`. Dazu ein **fester Sweep-Schwerpunkt** „Doku
  gegen Verifikation diffen" in den Briefings von Harry und Marv.
  **Warum beides:** Im Feld war der dokumentierte Startbefehl kaputt, während
  der Smoke-Test grün meldete. Fünf Red-Team-Funde derselben Kaskade hatten
  exakt diese Bauart, und **keiner** der Sweeps hat diesen gefunden — die
  Lücke klafft zwischen Doku und Testaufruf, nicht im Code, und ist beim
  Codelesen unsichtbar. Gefunden hat sie der Mensch beim ersten eigenen Start.
  Ein maschineller Diff wurde **verworfen** (stackagnostisch schwer, hohe
  Falschmelderate zu erwarten) — er kommt, wenn ein zweiter Fall dieser Bauart
  auftritt.
- **`test_bl16_guard_zuschreibung.py`** (13 Fälle, gegen ein Wegwerf-Repo und
  mit `set -euo pipefail` wie im Ernstfall) und
  **`test_bl17_doku_gegen_verifikation.py`**. Beide Gegenrichtungen von
  `BL-16` eigens abgesichert: Eine vorab schmutzige Datei, die die Rolle
  **doch** anfasst, bleibt eine Verletzung, und bei sauberem Start urteilt der
  Guard unverändert scharf. Gegenprobe gefahren — mit ausgeschalteter
  Zuschreibung fallen genau zwei Zusicherungen. **214 Testfälle** in 35
  Dateien.
- **Zuschreibungs-Lektion in [`doku/anhang-a.md`](doku/anhang-a.md) A.4**, neben
  der Rollback- und der Staging-Lektion. Die drei zusammen sind die Geschichte
  dieses Guards.

### Bemerkt

- **`BL-17` fand seinen eigenen Fund.** Der Regressionstest schlug beim ersten
  Lauf an: Die Regelphrase stand in der Vorlage über einen Zeilenumbruch
  zerrissen und war damit als zusammenhängende Aussage nicht auffindbar. Genau
  die Sorte Formfehler, die eine Regel unwirksam macht, ohne dass jemand sie
  bemerkt — dasselbe Muster wie die fehlenden Backticks in `BL-15`.

## [2.4.2] — 2026-08-02

**Die ausgelieferte Beutebuch-Vorlage lehrte genau die Falle, die `BL-11` im
Regex behoben hatte.**

`BL-11` (Release 2.3.x) hat `DATEI_RE` beigebracht, per Pytest-Node-ID
referenzierte Dateien zu lesen. Das war die **halbe** Reparatur: Der Extraktor
*konnte* den Pfad seither lesen — die Vorlage erzeugte nur nie einen. Sie nannte
ihn **ohne Backticks** und als **„optional"**, an fünf Stellen in vier Dateien,
in **jeder** frischen Installation. Aus dem Feld zurückgespielt (dort `BL-7`,
`team-kit_project_platformer`), wo derselbe Defekt an einem einzigen Fund
12,00 USD verbrannt hat: 9 Frank-Versuche, 3 Axel-Akten, keine Zeile Code
überlebt — bei grünem Smoke-Test und gültigem Promise, also ohne jedes
Fehlersignal.

### Fixed

- **Die `Reproducer-Test`-Zeile ist Pflichtfeld, der Pfad steht in Backticks
  (`BL-15`).** Zwei voneinander unabhängige Defekte, von denen **keiner allein
  wirkt**: (1) „optional" ⇒ Harry und Marv lassen das Feld leer, Franks neue,
  regelkonform nach der Fund-Nummer benannte Testdatei ist im Fund-Block nie
  referenziert, und `team_diff_beruehrt_fund` rollt jeden regelkonformen Fix
  zurück. (2) Ohne Backticks ⇒ selbst ein *ausgefülltes* Feld bleibt unsichtbar,
  weil `DATEI_RE` ausschließlich Backtick-Pfade liest. Die Prompt-Pflicht allein
  hätte also **nichts** bewirkt.
  **Neu:** Die Zeile wird **immer** gesetzt — auch wenn die Datei noch nicht
  existiert. Sie ist keine Quittung über getane Arbeit, sondern eine
  **Reservierung** des Dateinamens für Frank. Geändert in
  [`bootstrap/beutebuch.md`](bootstrap/beutebuch.md) (Vorlage + Begründungs­block),
  [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage) (Beutezug-Dreisatz
  Schritt 2 + Fund-Format), [`team/prompts/rolle-harry.md`](geteilt/prompts/rolle-harry.md),
  [`team/prompts/rolle-marv.md`](geteilt/prompts/rolle-marv.md).
- **Der Guard bleibt unangetastet scharf.** Gewählt wurde die Prompt-Pflicht,
  nicht die Guard-Lockerung (Strippenzieher-Entscheid im Feld, 2026-08-02).
  Begründung aus dem Feld: Beim Folgefund setzte Frank die Zeile **von sich
  aus** — dem Muster des vorigen Fundblocks folgend — und kam in **einem**
  Versuch durch. Das Muster trägt, sobald es sichtbar ist; es braucht nur eine
  verbindliche Regel statt Nachahmung.
- **Sechste Stelle, im Feld nicht sichtbar:** `CLAUDE.md.vorlage` schrieb den
  Pfad als `{{TEST_ORDNER}}/…`. Der Platzhalter trägt seinen Schrägstrich
  bereits, das expandierte also zu `tests//…`. Im Feld stand dort die schon
  substituierte Fassung, weshalb der Fund von dort nur fünf Stellen nennen
  konnte.

### Added

- **`test_bl15_reproducer_zeile_ankertauglich.py`** — der Regressionstest, den
  der Feldbefund ausdrücklich empfohlen hat und der diesen Fund verhindert
  hätte: Er nimmt die **wirklich ausgelieferte** Zeile aus allen vier Quellen,
  füllt sie so aus, wie die Vorlage es ansagt, und lässt `DATEI_RE` darauf los.
  Er läuft in beiden Ablagen — im Kit gegen `bootstrap/`, im installierten
  Projekt gegen die substituierten Zieldateien — und prüft zusätzlich, dass die
  Zeile überhaupt noch existiert und nicht wieder als „optional" markiert ist.
  Gegenprobe gefahren: Mit der alten Zeile schlagen genau zwei Zusicherungen
  fehl. **197 Testfälle** in 33 Dateien.

### Bemerkt

- **`install.sh` kompiliert die Tests, die es ausliefert.** Der Installer fährt
  zum Abschluss `pytest` gegen die frische Installation und legt dabei
  `.pyc`-Dateien an. `kit-test.sh` Stufe 3 durchsucht danach **alles** im
  Zielbaum nach übrig gebliebenen Installer-Platzhaltern — auch den Bytecode.
  Eine Testdatei, die einen Platzhalter als String-Literal führt, meldet sich
  damit selbst als Fund. Zusammensetzen hilft nicht: CPython faltet konstante
  Konkatenation beim Kompilieren. Der neue Test ersetzt Platzhalter deshalb
  über ein Muster, nicht über ein Literal.
- **`BL-17` neu im Backlog**, aus dem Feld nachgetragen (dort `BL-10`): *Die
  Verifikationskette darf sich den Erfolg nicht selbst einrichten.* Der
  dokumentierte Startbefehl war kaputt, während der Smoke-Test grün meldete —
  weil Smoke-Test und `pytest.ini` still ein `PYTHONPATH` dazusetzten, das es
  beim Anwender nie gibt. **Fünf** Red-Team-Funde derselben Kaskade hatten
  exakt diese Bauart, und **keiner** der Sweeps hat diesen gefunden: Harry und
  Marv lesen den Code, die Lücke klafft aber zwischen **Doku und Testaufruf**.
  Braucht einen Entscheid, in welcher Form die Regel greift.

## [2.4.1] — 2026-08-01

**Zwei Fehler in `ledger-pruefen`, gefunden beim ersten Einsatz auf einem
fremden, gewachsenen Ledger.**

Beim Rückspielen der Kit-Fixes in das Ursprungsprojekt `website-maxron-de` —
den Ahnherrn des Kits, der das flache Vor-Kit-Layout trägt und deshalb **kein**
`install.sh --update` annimmt — lief `ledger-pruefen` erstmals gegen 67
gewachsene Ledger-Zeilen aus 22 Kaskaden. Es meldete drei Warnungen. **Keine
davon war echt**, und keine war je auflösbar. Ein Werkzeug, das bei jedem Lauf
rot ist, erzieht genau zu dem Wegsehen, gegen das seine zwei Schweregrade
gebaut wurden (Skizze D, Frage 2).

### Fixed

- **Eine Rohquelle kann mehrere Ledger-Rollen speisen (`BL-13`).** `P3` bildete
  Archivordner 1:1 auf **eine** Rolle ab (`roles ↔ .team-logs`). Das ist
  falsch, sobald ein Projekt eine weitere Rolle **separat** bucht — und genau
  dafür existiert `akteur-abschluss --rolle <X>`. Real schreiben
  [`team/redteam.sh`](bash/redteam.sh), [`entry/frank.sh`](bash/entry/frank.sh),
  [`entry/axel.sh`](bash/entry/axel.sh) und
  [`entry/vollautomatik.sh`](bash/entry/vollautomatik.sh) **alle** nach
  `.team-logs`, während der Ahnherr Franks Out-of-Loop-Arbeit als eigene
  `frank`-Zeile bucht. `P3` meldete dieses Geld als „archiviert, aber nie
  gebucht" — strukturell unauflösbar, denn nachbuchen kann man nichts, was
  bereits gebucht **ist**.
  **Neu:** Die Rollenmenge je Ordner wird aus dem Ledger **abgeleitet** statt
  festverdrahtet. `.ralph-logs` gehört Ralph allein, `.team-logs` jeder
  weiteren Rolle mit Rohlog. `architekt` bleibt ausdrücklich außen vor
  (`LEDGER_OHNE_ROHLOG`): Diese Zeile ist eine gemessene Schätzung aus dem
  Transkript, ihr entspricht keine Log-Datei — im Ahnherrn trägt sie 275 USD
  und hätte jede echte Untergebuchung maskiert. Der Befund **nennt die
  gezählten Rollen**, damit ein Mensch die Zahl nachrechnen kann; genau dieses
  Nachrechnen hat `BL-1`, `BL-4` und `BL-5` überhaupt erst gefunden.
- **Benannte Kaskaden sind Out-of-Loop-Buchungen (`BL-14`).** Die `P1`-Regel
  „`roles` ohne `ralph` ⇒ Warnung" stimmt für **nummerierte** Kaskaden: Wo
  gesweept wurde, wurde auch gebaut. Für benannte (`post-20`,
  `roles-post-k13`) gilt sie nicht — das sind Fixserien **nach** dem Lauf, in
  denen Ralph gar nicht gebaut hat. Die fehlende `ralph`-Zeile ist dort
  korrekt, die Warnung dauerhaft unauflösbar, und sie erschien bei **jedem**
  `--budget`. **Neu:** Warnung nur bei `kaskade.isdigit()`, sonst ein Hinweis,
  der den Grund nennt.

### Added

- **6 neue Testfälle** in `test_bl13_ledger_pruefen.py`, darunter beide
  Gegenrichtungen: Eine echte Untergebuchung muss trotz der erweiterten
  Rollenmenge weiterhin anschlagen (mit der echten `BL-4`-Zahl 2,1621 USD),
  und bei einer **nummerierten** Kaskade bleibt die fehlende `ralph`-Zeile
  eine Warnung. Dazu ein Schutzwächter, dass die `architekt`-Zeile keine
  Rohlogs deckt. **182 Testfälle** in 32 Dateien.

### Bemerkt

- **Der Rückkanal lief bisher nur in eine Richtung.** Feld → Kit war geregelt
  (Skizze C), Kit → **Ahnherr** nicht. `BL-11` lag deshalb zwei Kaskaden im
  Feld, bevor es ins Kit kam — und im Ursprungsprojekt lag derselbe Fehler bis
  heute. Dort sind die drei fehlenden Fixes jetzt einzeln nachgezogen
  (`BL-57`/`BL-58`/`BL-59` im dortigen Backlog); eine Migration auf das
  Kit-Layout wäre 531 Pfadverweise in 61 Dateien und wurde bewusst **nicht**
  gemacht (Strippenzieher-Entscheid 2026-08-01).

## [2.4.0] — 2026-08-01

**Das Ledger prüft jetzt seine eigene Vollständigkeit** (Roadmap-Skizze D).

### Added
- **`./team-status.sh --ledger-pruefen` / `kosten.py ledger-pruefen`.** Drei
  Prüfungen: (1) trägt jede gelaufene Kaskade eine Zeile je Quelle —
  `ralph`/`roles`/`architekt`? (2) liegen unarchivierte Logs herum, obwohl die
  Kaskade schon gebucht ist? (3) **ergeben die archivierten Rohlogs mehr, als
  im Ledger steht?**
  Nur die dritte Frage zieht ihre Kennzahl aus einer **anderen** Quelle als das
  Geprüfte — und genau das fehlte bisher: `BL-1`, `BL-4` und `BL-5` sind alle
  drei **nicht** durch ein Werkzeug aufgefallen, sondern dadurch, dass ein
  Mensch den gedruckten Bericht neben das Ledger hielt. Dreimal dasselbe
  Muster: Ein Bericht, der seine Kennzahl aus derselben Quelle zieht wie der
  Fehler, bestätigt ihn, statt ihn zu zeigen.
  Exit `4` bei Warnbefunden (`1` bleibt dem Bedienfehler vorbehalten), zwei
  Schweregrade (`warnung` = sehr wahrscheinlich verlorenes Geld, `hinweis` =
  kann legitim sein). Bewusst **kein** hartes Gate im Closeout: Eine Kaskade
  mit legitim fehlender Zeile könnte sonst nicht abschließen, und ein Gate,
  das man regelmäßig umgeht, ist wirkungslos. Stattdessen laufen die Warnungen
  bei jedem `--budget` ungefragt mit.
- **16 neue Testfälle** (`test_bl13_ledger_pruefen.py`), darunter `BL-4` und
  `BL-5` mit ihren **echten Feldzahlen** (2,1621 USD nie gebucht bzw. 1,0969
  USD überschrieben) — beide schlagen an. Gegenprobe für alle drei Prüfungen
  einzeln gefahren. **176 Testfälle** in 32 Dateien.

### Entschieden
- **Der Rohlog-Vergleich läuft je Quelle, nicht je Kaskade.** Die Skizze wollte
  Zeile gegen *ihre* Rohlogs halten; das ist mit der heutigen Ablage nicht
  ehrlich beantwortbar, weil Log-Dateinamen keine Kaskadennummer tragen
  (`stufe-<n>-<ts>.json`, `harry-<ts>.json`) und das Archiv **ein** flacher
  Ordner je Quelle ist. Zuordnen ließe sich nur über mtime-Fenster — in der
  Kostenmechanik wird nicht geraten. Ein Archiv je Kaskade
  (`archiv/kaskade-<n>/`) wäre sauberer gewesen, hätte aber `lauf_kosten()` in
  `vollautomatik.sh` gebrochen, das `.ralph-logs/archiv` **nicht-rekursiv**
  globbt und den Pro-Lauf-Deckel auch gegen bereits weggeräumtes Geld misst
  (`BL-55`). Archivordner ↔ Ledger-Rolle entsprechen einander dagegen
  eindeutig — der Vergleich braucht damit **keine** Zuordnung und hätte `BL-4`
  wie `BL-5` trotzdem gefunden.

### Changed
- Closeout-Regel in `CLAUDE.md.vorlage`, `TEAM.md` und dem Architekten-Briefing
  nachgezogen: Der Abschluss wird **geprüft, nicht geglaubt**; ein stehender
  Warnbefund gehört samt Begründung ins Abschluss-Doc.

## [2.3.2] — 2026-08-01

**Der erste echte `--update`-Einsatz hat zwei Löcher aufgedeckt — beide im
Update selbst.**

### Fixed
- **`--update` löschte projekteigene Tests und nahm lokale Fixes still zurück
  (`BL-12`).** Ein pauschales `rm team/tests/test_*.py` sollte umbenannte
  Kit-Tests einer Altversion entfernen. Im Feld löschte es einen **vom Projekt
  geschriebenen** Infrastruktur-Test, und im selben Lauf wurde
  `team/tools/beutebuch.py` mit der älteren Kit-Fassung überschrieben — samt
  einem lokalen Fix, der real 12,00 USD gekostet hatte. Die Annahme
  „`team/tests/` gehört exklusiv dem Kit" ist falsch, sobald ein Projekt eine
  Lücke im Team selbst schließt.
  **Neu:** `--update` löscht **nichts** mehr. Tests, die das Kit nicht kennt,
  bleiben liegen und werden gemeldet; jede ersetzte Infrastruktur-Datei, die
  vorher von der Kit-Fassung abwich, wird mit `git diff`-Befehl ausgewiesen —
  mit dem ausdrücklichen Hinweis, einen darin steckenden eigenen Fix erst ins
  Kit zurückzuspielen und dann erneut zu updaten.

### Added
- **`BL-11` aus dem Feld zurückgeholt:** `DATEI_RE` in `beutebuch.py` erkennt
  jetzt Pytest-Node-IDs (`datei.py::test_x[param]`) und extrahiert den reinen
  Dateipfad. Vorher galt eine so referenzierte Datei still als „nicht
  referenziert", der Substanz-Anker verwarf jeden Fix, der nur sie berührte,
  und Frank lief in einen endlosen Rollback-Zyklus (real 12,00 USD an `HM-4`).
  Fix und Reproducer stammen aus dem Feldprojekt und lagen dort **zwei
  Kaskaden lang** — genau das Loch, das der Rückkanal schließen soll.
- Drei weitere Zusicherungen in `kit-test.sh` Stufe 5 (projekteigener Test
  überlebt, wird gemeldet, abweichende Infrastruktur wird gemeldet).
- **160 Testfälle** in 31 Dateien.

## [2.3.1] — 2026-08-01

**Sofortnachtrag zu 2.3.0, im Feld erzwungen.**

### Fixed
- **`install.sh --update` lief in einen aktiven Lauf hinein (`BL-10`).** Beim
  ersten Einsatz von `--update` auf ein Feldprojekt lief dort noch
  `vollautomatik.sh`. Das Update legte uncommittete Dateien in `team/` ab; der
  unmittelbar folgende Axel-Lauf (read-only, Whitelist nur `plans/`) wertete
  sie als **Guard-Verletzung**, rollte sie zurück und buchte seine Runde als
  Fehlschlag — obwohl er seine Ermittlungsakte geliefert hatte. Dritte
  Stagnation in Folge, **Lauf gestoppt**, Update spurlos weg.
  Der Guard hat dabei genau das getan, wofür er gebaut ist, und die
  Projektdaten blieben unversehrt. Gefehlt hat die Sperre im Installer:
  `--update` prüft jetzt per `flock -n`, ob `.team-loop.lock` **gehalten** wird
  (nicht bloß existiert), bricht dann mit Exit 2 ab, warnt zusätzlich vor einem
  schmutzigen Arbeitsbaum und macht das anschließende Committen zur
  ausdrücklichen Pflicht — sonst räumt der nächste Read-Only-Lauf das Update
  weg.

## [2.3.0] — 2026-08-01

**Die Kostenerfassung stimmt wieder, und das Kit prüft sich selbst.** Erntelauf
der ersten Feldkaskade: drei Fehler kamen aus dem Feld zurück (`BL-4`, `BL-5`,
`BL-9`), drei fielen beim Aufräumen auf (`BL-6`, `BL-7`, `BL-8`).

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
- **Zwei Fehler im obigen Fix selbst**, gefunden bei einem manuellen
  Durchlauf gegen eine echte Installation — **nicht** von den 149 Tests:
  (1) `merge_fn` schrieb die Rolle hart als `roles`; ein `--addieren` auf die
  `ralph`-Zeile hätte sie in eine zweite `roles`-Zeile verwandelt und die
  Baukosten erneut unsichtbar gemacht — der `BL-4`-Fehler eine Ebene tiefer,
  erzeugt vom `BL-5`-Fix. (2) Beim Nachlauf **einer** Rolle ist die andere
  Quelle regulär leer; `--addieren` buchte dort `+0,0000` und überschrieb dabei
  Datum und Notiz der bestehenden Zeile mit dem Text des fremden Nachlaufs.
  Beides behoben und mit je einem Regressionstest belegt.
  **Lehre:** Die Tests prüften je Rolle nur einen Modus — die Kreuzkombination
  (andere Rolle × anderer Modus) blieb blind. Ein einziger Durchlauf durch die
  echte Bedienoberfläche fand, was 149 grüne Tests nicht fanden.
- **`README.md`, Abschnitt „Grenzen", war überholt (`BL-7`).** Frank ist
  inzwischen scharf gelaufen (drei Fixes im Feld), Axel weiterhin nicht — und
  die Fixphase einer `vollautomatik.sh` hat noch nie in **einem** Durchlauf
  durchgetragen. Präzisiert statt gestrichen. Zahlen (Dateien, Tests,
  Zeilenumfänge) auf den Ist-Stand gebracht.

- **`--force` war die einzige dokumentierte Update-Option — und
  datenvernichtend (`BL-8`).** Ohne Flag ändert `install.sh` an einem
  bestehenden Projekt gar nichts, mit `--force` überschreibt er auch die
  Projektdaten. Empirisch nachgestellt: `.budget-ledger` geleert,
  `.ralph-state` von `5` auf `1` zurück, Beutebuch-Fund weg, `TEAM_SMOKE_TEST`
  aus `team.config.sh` verschwunden. Ein Feldprojekt konnte die Fixes dieses
  Releases damit gar nicht bekommen, ohne seine Geschichte zu verlieren.
- **Feldprojekte führten eine „T.E.A.M."-Domäne, die strukturell null ist
  (`BL-9`).** Der Kontostand zeigte einen Domänenblock mit einer hart auf die
  Domäne `team` verdrahteten Zeile. In einem Feldprojekt wird am Team nicht
  entwickelt — Funde gehen ins Kit zurück und werden dort verbucht —, die
  Zeile war also immer `0.0000`. Eine Kennzahl, die nie etwas zeigt, erzieht
  dazu, den ganzen Block zu überlesen. Die Verdrahtung war zudem für **jede**
  Konfiguration ohne `team` falsch (z. B. `backend frontend`).
  **Neu:** Installer-Default ist **eine** Domäne (`produkt`); der Block
  erscheint nur bei mehreren und listet dann **jede** konfigurierte Domäne.

### Added
- **`install.sh --update`** — der sichere Weg auf eine neue Kit-Version. Fasst
  nur die Infrastruktur an (Entrypoints außer `team.config.sh`, `team/lib.sh`,
  `team/redteam.sh`, `team/tools/`, `team/prompts/`, `team/tests/`) und lässt
  Ledger, Kaskadenstand, Beutebuch, CHANGELOG, `plans/`, `CLAUDE.md` und
  `team.config.sh` unberührt. Liest die Projektwerte aus der **installierten**
  `team.config.sh` (sonst bekämen die Briefings die falschen Pfade und damit
  eine falsche Guard-Grenze), rettet den Commit-Entscheid aus dem bisherigen
  Architekten-Briefing, entfernt Testdateien entfallener Versionen und meldet
  am Ende, welche Doku-Dateien von der Kit-Fassung abweichen — die **Regeln**
  zieht der Mensch nach, sonst läuft die Doku der Mechanik hinterher (das war
  die Hälfte von `BL-4`).
- `kit-test.sh` prüft den Update-Pfad als **Stufe 5**: Es macht das
  Wegwerf-Projekt künstlich „lebendig" (Ledger, Kaskadenstand, Beutebuch-Fund,
  eigener Smoke-Test, Alttest einer Vorversion) und weist nach, dass `--update`
  davon nichts anfasst.
- `team/tests/test_bl4_ralph_abschluss.py` — vier Prüfungen, darunter die
  entscheidende über die Bedienoberfläche: **ein** `--rollen-abschluss` muss
  **beide** Zeilen erzeugen und beide Log-Ordner rotieren. Gegenprobe gefahren:
  Mit dem alten Ein-Verb-Aufruf ist genau dieser Test rot.
- `team/tests/test_bl5_rollen_abschluss_bestand.py` — sieben Prüfungen, darunter
  das **Feldszenario mit den echten Zahlen** (1,0969 → Frank-Nachlauf 2,4114 →
  3,5083) inklusive Archivierung. Gegenprobe gefahren: Mit dem alten Verhalten
  sind genau die beiden Kernprüfungen rot.
- **153 Testfälle** in 30 Dateien (im installierten Projekt).
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

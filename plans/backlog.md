# Backlog — T.E.A.M.-Starterkit

Aufgaben am **Kit selbst**, die keine eigene Kaskade rechtfertigen: kleine
Verbesserungen, technische Schulden, Rückmeldungen aus Feldprojekten.

> **Nicht verwechseln:** `bootstrap/backlog.md` ist die **Vorlage** für
> Zielprojekte. Diese Datei ist der Backlog des Kits.

**Nummernraum**: `BL-n` ist historisch gewachsen und wird zwischen Ursprungs-
projekt (`website-maxron-de`), Kit und Feldprojekten geteilt. `BL-1`…`BL-5`
tragen hier dieselbe Bedeutung wie im Feldprojekt
`team-kit_project_platformer`, damit die Spur lesbar bleibt. Neue kit-eigene
Funde ab `BL-6`. Verweise auf den Backlog eines **anderen** Projekts werden
`Kit-BL-<N>` geschrieben (`BL-50`).

> **Abgetragene Einträge stehen im Archiv:**
> [`backlog-archiv.md`](backlog-archiv.md). Dort liegt die vollständige
> Begründung jedes erledigten Punktes — sie wird nachgeschlagen, nicht
> mitgelesen. Diese Datei trägt nur, woran noch Arbeit hängt (`BL-53`).

**Abtrag 2026-08-21 (Kit-Sitzung nach dem Windows-Pull), laufend.** Der Pull
selbst hat einen eigenen Fund mitgebracht (`BL-144`, Selbsttest der bash-Bahn
seit `BL-136` rot). Seither abgetragen: `BL-144`, `BL-142`, `BL-143`, `BL-129`. Die Reihenfolge
folgt der Wirkung, nicht der Nummer — zuerst, was den dokumentierten Weg
blockiert, dann was falsch bucht, dann was falsch anleitet.

**Stand 2026-08-21: fünf Meldungen aus dem Feld dazu** (`BL-139` bis `BL-143`),
alle aus `duke-itam-2026` — einer frischen, mit `--nur-pwsh` installierten
Ablage, die an diesem Tag ihre **allererste** Kaskade geplant, gebaut und
abgeschlossen hat. `BL-139`/`BL-140` fielen beim **Anlegen** auf, `BL-141` bis
`BL-143` im **Closeout**.

Der Tag zerfällt in zwei Gruppen. **Die Vorlagen** (`BL-139`, `BL-140`, in
`bootstrap/`) schicken die Rollen an Dateien und Nummern, die es so nicht gibt —
still, ohne Meldung. **Die Kostenkette** (`BL-141`–`BL-143`, in
`geteilt/tools/kosten.py` und `team-status.ps1`) ist der eigentliche Fund des
Tages: Der erste echte Kostenabschluss eines Projekts hat sie alle drei
aufgedeckt, und keiner davon war vorher zu sehen, weil sie erst beim
**vollständigen** Durchlauf zuschlagen — `BL-142` brach genau bei dem Aufruf
ab, den die Doku vorgibt (abgetragen), `BL-143` buchte Abo-Kosten in die
API-Spalte (abgetragen), und
`BL-141` liefert die Zahl, die dort landet, als Zeilen-Churn-Proxy statt als
Messung. Wer eine Kaskade zu Ende führt, trifft alle drei nacheinander.

`BL-139` ist der inhaltliche Zwilling von `BL-129` (abgetragen) — dort fiel die
einbahnige Ablage im Testharnisch auf, hier im Regeltext, den jede Rolle in
jedem Aufruf im Systemprompt hat.

**Stand 2026-08-20: drei offene Einträge** (`BL-117`, `BL-120`, `BL-129` —
Letzterer am 2026-08-21 abgetragen).
`BL-120` ist am selben Tag beim Doku-Durchgang dazugekommen und hat mit dem
Rest dieses Tages nichts zu tun: ein Gerüst, das erst eine Frage trägt.
`BL-121` (Ordneranlage im Interview), `BL-122` (Exit-Code als Ausnahme),
`BL-123` (blanker `pwsh`-Aufruf), `BL-124` (pytest nicht gefunden) und
`BL-125` (`kosten.py` unter Windows nicht ladbar) und `BL-126` (ein
einbahnig pwsh installiertes Projekt war nicht aktualisierbar) sind am
selben Tag entstanden und **noch am selben Tag abgetragen** worden — alle
sechs aus dem Feld, von derselben echten Windows-Maschine. `BL-127` und
`BL-128` sind beim **Trockenlauf zu `BL-126`** herausgefallen: nicht durch
Lesen, sondern durch einen Lauf mit einem Schalter, den sonst niemand
benutzt. `BL-129` ist der Rest desselben Laufs und bleibt offen. An diesem Tag sind
`BL-111`, `BL-112`, `BL-114`, `BL-115`, `BL-116`, `BL-118` und `BL-119`
abgetragen worden. `BL-117` bleibt und ist beim Abtragen von `BL-112` als
ausgewiesener Rest entstanden — die Hälfte der Zusicherung, die sich nur auf
einer Maschine mit PowerShell 7 beweisen lässt. Alle Begründungen stehen im
Archiv.

> **Der Rest, den dieser Tag hinterlässt, ist derselbe wie `BL-117`:** Die
> pwsh-Bahn hat mit `BL-118` einen strukturellen Umbau und mit `BL-119` einen
> neuen Schalter bekommen, und beides ist auf dieser Maschine nur **statisch
> gelesen**, nicht gefahren. `kit-test.sh` Stufe 11 (Gleichstand der
> Installer) braucht PowerShell 7 und wird hier übersprungen.

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-141 | **Die Architekten-Kostenzeile ist ein Zeilen-Churn-Proxy und lag im Feld 35 % zu niedrig — obwohl die Daten fuer eine exakte Messung bereits auf der Platte liegen.** `architekt_schaetzung()` in `geteilt/tools/kosten.py` rechnet `git_churn(seit, ("plans", "CLAUDE.md")) * ARCHITEKT_USD_PRO_CHURN_ZEILE`. Damit misst sie die **Groesse des Diffs**, nicht die Arbeit: Eine Sitzung mit viel Lesen, Pruefen und Gegenproben und wenig geschriebenem Text wird systematisch unterschaetzt, eine Prosa-Sitzung ueberschaetzt. Im Feld (`duke-itam-2026`, Kaskade 1) meldete die Zeile **7,6861 USD**; die Messung aus dem Sitzungstranskript ergab **11,7582 USD**. Das Briefing des Architekten verlangt ausdruecklich eine Transkript-Messung ("Antworten ueber die Nachrichten-ID deduplizieren, Preismodell an einem headless-Lauf mit bekanntem Konsolenwert eichen") — aber **kein** Werkzeug des Kits kann das, also schreibt jeder Architekt sich das Skript neu, oder er nimmt die Churn-Zahl und bucht sie als gemessen | Feld (`duke-itam-2026`), 2026-08-21, im Closeout von Kaskade 1. Belegt statt behauptet: Das CLI-Transkript liegt unter `~/.claude/projects/<slug>/<session>.jsonl` und traegt pro Assistant-Satz ein vollstaendiges `usage`-Objekt (`input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation.ephemeral_1h/5m_input_tokens`). Die headless-Logs des Kits (`.ralph-logs/*.json`, `.team-logs/*.json`) tragen **beides** — dieselbe `usage`-Struktur **und** den abgerechneten `total_cost_usd`, je Modell aufgeschluesselt in `modelUsage`. Das sind fertige Eichpunkte | **offen.** Bauform steht fest und ist im Feld einmal durchgerechnet: **(1)** Preisvielfache aus den vorhandenen headless-Logs ableiten statt eintragen — aus 8 Laeufen ergaben sich Output = 5x Input, Cache-Read = 0,1x Input, Cache-Write-1h = 2,0x Input, und das Modell reproduzierte alle 8 Konsolenwerte auf 4e-16 USD genau. **(2)** Das Transkript der laufenden Sitzung ueber `message.id` deduplizieren — roh waren es 172 Assistant-Saetze, nach Dedup 76; ohne diesen Schritt zaehlt man mehr als doppelt. **(3)** Basispreis je Modell-ID aus einer gepflegten Tabelle, mit ehrlichem Ausweis, wenn die ID unbekannt ist. **Gegenprobe, die es erst gueltig macht:** Das Werkzeug rechnet die headless-Logs mit demselben Code nach und vergleicht gegen deren `total_cost_usd` — weicht es ab, ist die Preistabelle veraltet und das Werkzeug sagt das, statt eine falsche Zahl zu buchen. Solange das fehlt, sollte die Zeile wenigstens **`(Churn-Proxy)`** heissen statt `(geschaetzt)`: Der heutige Text laesst offen, woraus geschaetzt wurde, und lud im Feld dazu ein, die Zahl fuer eine Messung zu halten |
| BL-139 | **In einer `--nur-pwsh` installierten Ablage nennen die ausgelieferten REGELTEXTE durchgehend die Bash-Bahn — und schicken damit jede Rolle an eine Datei, die es nicht gibt.** Im Feldprojekt `duke-itam-2026`: `CLAUDE.md` nennt **14** verschiedene `.sh`-Pfade (`team.config.sh`, `ralph.sh`, `team/lib.sh`, `team/redteam.sh`, `./team-test.sh`, `./vollautomatik.sh` …), **keiner** davon existiert; `TEAM.md` kommt auf **23** Nennungen. Am teuersten ist `team.config.sh`: Der Regeltext schickt jede Rolle genau dorthin, um `TEAM_SMOKE_TEST`, `TEAM_WEITERER_CODE` oder `TEAM_DOMAENEN` nachzutragen — und `team/lib.psm1` liest `team.config.ps1` (Zeile 101) und sagt das in seiner eigenen Warnung (Zeile 205) auch so. **Zwei einander widersprechende Anweisungen im selben Systemprompt.** Der Fehlermodus ist still: Wer der Regel folgt, legt eine `team.config.sh` an, die nie gelesen wird — kein Abbruch, keine Meldung, der Wert wirkt einfach nicht. Bei `TEAM_SMOKE_TEST` heißt das: Das Team läuft weiter ohne Sicherheitsnetz und meldet in jedem Prompt „kein Smoke-Test konfiguriert", obwohl gerade einer eingetragen wurde | Feld (`duke-itam-2026`), 2026-08-21, vom Architekten beim Anlegen der ersten Kaskade gemessen statt vermutet: `for f in $(grep -oE '[A-Za-z0-9_./-]+\.sh' CLAUDE.md \| sort -u); do test -e "$f" \|\| echo FEHLT $f; done` → 14 von 14 fehlend. Aufgefallen, weil die Skizzenvorlage `roadmap-skizzen.md` beim Abtragen von „Verifikationsfähigkeit herstellen" ausdrücklich sagt: „Den Befehl in `team.config.sh` eintragen" | **offen.** Quelle sind die Vorlagen, nicht das Feldprojekt: `bootstrap/CLAUDE.md.vorlage`, `bootstrap/TEAM.md`, `bootstrap/roadmap-skizzen.md`. Zwei Bauformen denkbar — **(a)** der Installer ersetzt beim einbahnigen Einbau die Pfadnennungen der abgewählten Bahn (mechanisch, trifft alle 37 Stellen, muss aber `TEAM.md`s absichtliche Zwei-Bahnen-Tabelle verschonen); **(b)** die Vorlagen schreiben Bahn-neutral (`team.config.*`, „der Entrypoint `ralph`") und nennen die konkrete Endung nur in der einen Tabelle, die beide Bahnen gegenüberstellt. **(b)** ist billiger und hält auch, wenn später eine dritte Bahn dazukommt. **Gegenprobe, die den Fix erst gültig macht:** ein Test, der nach `install.sh --nur-pwsh` **jeden** in `CLAUDE.md` und `TEAM.md` als Pfad genannten Entrypoint gegen das Dateisystem hält — genau der Lauf, der diesen Fund gefunden hat. Ohne ihn wandert dieselbe Lücke beim nächsten Vorlagen-Umbau zurück. Lokal im Feldprojekt entschärft durch einen Absatz in den Projekt-Spezifika, der die Übersetzung einmal verbindlich festhält (`Kit-BL-1` dort) |
| BL-140 | **Die Regeltexte zitieren den Kit-Backlog blank (`BL-52`, `BL-30`, `HM-32`) — und verletzen damit genau die Regel, die sie selbst aufstellen.** `CLAUDE.md` schreibt vor: „Verweist eine Zeile auf den Backlog eines **anderen** Projekts, wird sie als `Kit-BL-<N>` geschrieben, nie als blankes `BL-<N>`. Der Nummernraum ist sonst doppelt belegt." In derselben Datei stehen dann bare Verweise auf Kit-Einträge — `BL-52` (Prüfumfang), `BL-51` (Schreibzone), `BL-20`/`BL-25` (429), `BL-30` (Zwei-Schwellen), `BL-115`, `BL-116`, `BL-9`, `BL-41` und weitere. **In einem frischen Feldprojekt ist der Nummernraum damit ab Tag 1 doppelt belegt:** Der eigene Backlog fängt bei `BL-1` an, während der Regeltext im selben Repo unter `BL-1` eine Kit-Feldlehre meint (Bericht aus derselben Quelle). Wer — Mensch oder Rolle — einen Verweis nachschlägt, landet im falschen Dokument oder findet gar nichts und hält den Verweis für veraltet | Feld (`duke-itam-2026`), 2026-08-21, beim Anlegen des ersten eigenen Backlog-Eintrags: Die Frage „darf mein erster Eintrag `BL-1` heißen?" ließ sich aus den Regeltexten **nicht** beantworten, weil beide Lesarten dort belegt sind | **offen, klein.** Der Fix ist mechanisch und einmalig: In `bootstrap/CLAUDE.md.vorlage` und `bootstrap/TEAM.md` jede Nummer, die einen **Kit**-Eintrag meint, auf `Kit-BL-<N>` umstellen (`HM-<N>` analog auf `Kit-HM-<N>`, wo eine Feldlehre des Kits gemeint ist). Danach gilt in einem Zielprojekt ohne Ausnahme: blank = mein Backlog, `Kit-` = fremd. **Gegenprobe:** ein Lint über die Vorlagen, der ein blankes `BL-<N>` außerhalb der Vorlage `bootstrap/backlog.md` beanstandet — die Regel ist sonst wieder nur Prosa, und der nächste Textumbau bringt sie zurück |
| BL-120 | **`doku/faq.md` ist als Gerüst gebaut und trägt bisher genau eine Frage.** Die Seite beantwortet *ganze* Fragen — die dritte Sorte neben „wie geht der Weg?" (`einrichtung.md`) und „was heißt diese Meldung?" (Fehlerbilder-Tabelle, eine Zeile je Symptom). Drin ist die Installation der Agenten-CLI für Linux, WSL und Windows. Offen ist der Rest des Gerüsts. Drei Kandidaten stehen fest, alle drei aus Stellen, an denen die Doku heute nur eine Zeile hergibt: **(1)** „Lauf endet mit Exit `42`/`43` — was heißt das und was mache ich jetzt?" (die Fehlerbilder-Tabelle verweist auf den README-Abschnitt *Betrieb*, der die Codes nennt, aber nicht die Handlung); **(2)** „Wie hole ich eine abgewählte Bahn zurück?" (`BL-119` hat den Schalter gebaut, der Rückweg steht in `A.13` als Bauentscheid, nicht als Handlungsanweisung); **(3)** „Warum kostet mein Lauf mehr als geschätzt?" (`A.7` und `A.9` tragen den Stoff, aber als Betriebslehre für den, der das Kit baut, nicht für den, der es bedient) | Kit, 2026-08-20 — beim Anlegen der Seite ausgewiesen statt behauptet: Eine FAQ mit einer Frage ist ein Versprechen, kein Nachschlagewerk. Die drei Kandidaten sind nicht ausgedacht, sondern die Stellen, an denen im Doku-Audit desselben Tages eine Symptomzeile auf eine Erklärung zeigte, die es so nicht gibt | **offen, wächst mit dem Feld.** Bewusst *keine* Kaskade: Jede Frage kostet einen Abschnitt und soll erst geschrieben werden, wenn sie wirklich gestellt wurde — eine FAQ, die Fragen erfindet, wird lang und trotzdem nicht gelesen. Die Bauform steht fest und ist an der ersten Frage vorgeführt: Symptomtabelle mit den echten Wortlauten, Schritt 0 (*ist es überhaupt dieser Fall?*), die Antwort je Plattform mit einer Entscheidungsspalte statt einer Aufzählung, und ein **eigener Belegstand**, sobald fremde Befehle zitiert werden |
| BL-117 | **Der Prompt-Gleichstand ist am QUELLTEXT bewiesen, nicht am LAUF — Drift in den eingesetzten Werten bliebe unsichtbar.** [`test_bl112_prompt_gleichstand.py`](../geteilt/tests/test_bl112_prompt_gleichstand.py) vergleicht die **Prosa** beider Bahnen, nachdem jede Variableneinsetzung zu einem Platzhalter geworden ist. Das trifft den Fall, für den `BL-112` geschrieben wurde (jemand schärft eine Feldlehre in nur einer Fassung nach), und es lässt genau eine Lücke: Setzen die beiden Bahnen in denselben Platzhalter **verschiedene Werte** ein — ein anders abgeleiteter Ordnername, eine Fallunterscheidung, die nur eine Seite kennt, ein `team.config.ps1`, das einen Wert anders vorbelegt —, sind die Prompts verschieden und der Test bleibt grün. Diese Hälfte kann nur ein **Lauf** zeigen | Kit, 2026-08-20 — beim Abtragen von `BL-112` ausgewiesen statt behauptet: Die Fix-Skizze dort sah den Lauf-Vergleich vor, und der braucht **beide** Shells auf **einer** Maschine. Auf der Entwicklungsmaschine ist kein `pwsh` installiert; ein blind geschriebener Test, dessen erste Ausführung auf einer fremden Maschine stattfindet, wird dort „angepasst" statt gelesen — dieselbe Erwägung, die `BL-113` teuer belegt hat (die pwsh-Bahn fiel erst auf der Zielmaschine auf) | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Bauart wie in `BL-112` skizziert: ein `claude`-Stub, der sein `-p`-Argument in eine Datei schreibt statt zu arbeiten (`Schale.claude_stub` kann das Gerüst schon), jede Rolle einmal je Bahn gefahren, die beiden Prompt-Dateien zeichenweise verglichen. **Die Ausnahmeliste ist bereits da** und wird mitbenutzt, samt ihrer Probe gegen unnötige Einträge — der Lauf-Vergleich erbt sie, statt eine zweite aufzumachen. **Gegenprobe, die ihn erst gültig macht:** ein absichtlich abweichend vorbelegter Wert in einer der beiden Konfigurationen, an dem der Test fallen muss. Solange er fehlt, gilt die Zusicherung „gleicher Prompt" ausdrücklich nur für die Prosa |

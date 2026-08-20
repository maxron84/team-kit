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

**Stand 2026-08-20: drei offene Einträge** (`BL-117`, `BL-120`, `BL-129`).
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
| BL-129 | **In einer mit `--nur-pwsh` installierten Ablage sind 109 der 487 Tests ROT — die Zusicherung „Tests bleiben grün in einbahniger Ablage" gilt nur in der geprüften Richtung.** `kit-test.sh` Stufe 8 belegt sie für `--nur-bash` (dort läuft der Doppelbahn-Harnisch sauber in den Übersprung). Umgekehrt fallen alle Fälle, die die **bash**-Bahn fahren, ins Leere statt zu überspringen: `test_stufe90_briefings.py` liest `team/redteam.sh` (`FileNotFoundError`), `test_stufe44_domaenen_status.py`, `test_stufe51_akteur_cli.py`, `test_stufe53_ledger_split.py` und weitere rufen `team-status.sh` auf, und selbst parametrisierte Fälle laufen als `[bash]` los, obwohl die Bahn gar nicht da ist. Der Harnisch kennt `bahnen_in_der_ablage()` und `ueberspringe_ohne_beide_bahnen()` — beides greift hier nicht: Ein Test, der **nur** die eine Bahn braucht, hat keinen Übersprung für **ihr** Fehlen | Kit, 2026-08-20 — beim Trockenlauf zu `BL-126` gemessen, nicht vermutet: `install.sh --nur-pwsh` in ein leeres Repo, dann `pytest team/tests` → `109 failed, 242 passed, 136 skipped`. Aufgefallen ist es erst, weil `BL-127` den Testlauf des Installers überhaupt wieder scharf gemacht hat — vorher meldete er „übersprungen" und niemand sah die Roten | **offen.** Bauart steht fest und ist billig: ein `ueberspringe_ohne_bahn("bash")` neben dem vorhandenen Helfer, angewandt auf die Tests, die eine bestimmte Bahn FAHREN (nicht auf die, die beide vergleichen), plus ein Übersprung für die `[bash]`/`[pwsh]`-Parametrisierung, sobald die jeweilige Bahn fehlt. **Die Gegenprobe, die ihn erst gültig macht:** Der Übersprung muss in der Zusammenfassung SICHTBAR sein (dasselbe `_QUOTE`-Muster wie bei der einbahnigen Ablage) — ein stiller Übersprung von 109 Fällen liest sich am Ende wie ein bestandener Nachweis, und das wäre schlimmer als das rote Bild von heute. Dazu gehört die Stufe 8 nachgezogen: Was dort für `--nur-bash` steht, muss dann auch für `--nur-pwsh` behauptet werden dürfen |
| BL-120 | **`doku/faq.md` ist als Gerüst gebaut und trägt bisher genau eine Frage.** Die Seite beantwortet *ganze* Fragen — die dritte Sorte neben „wie geht der Weg?" (`einrichtung.md`) und „was heißt diese Meldung?" (Fehlerbilder-Tabelle, eine Zeile je Symptom). Drin ist die Installation der Agenten-CLI für Linux, WSL und Windows. Offen ist der Rest des Gerüsts. Drei Kandidaten stehen fest, alle drei aus Stellen, an denen die Doku heute nur eine Zeile hergibt: **(1)** „Lauf endet mit Exit `42`/`43` — was heißt das und was mache ich jetzt?" (die Fehlerbilder-Tabelle verweist auf den README-Abschnitt *Betrieb*, der die Codes nennt, aber nicht die Handlung); **(2)** „Wie hole ich eine abgewählte Bahn zurück?" (`BL-119` hat den Schalter gebaut, der Rückweg steht in `A.13` als Bauentscheid, nicht als Handlungsanweisung); **(3)** „Warum kostet mein Lauf mehr als geschätzt?" (`A.7` und `A.9` tragen den Stoff, aber als Betriebslehre für den, der das Kit baut, nicht für den, der es bedient) | Kit, 2026-08-20 — beim Anlegen der Seite ausgewiesen statt behauptet: Eine FAQ mit einer Frage ist ein Versprechen, kein Nachschlagewerk. Die drei Kandidaten sind nicht ausgedacht, sondern die Stellen, an denen im Doku-Audit desselben Tages eine Symptomzeile auf eine Erklärung zeigte, die es so nicht gibt | **offen, wächst mit dem Feld.** Bewusst *keine* Kaskade: Jede Frage kostet einen Abschnitt und soll erst geschrieben werden, wenn sie wirklich gestellt wurde — eine FAQ, die Fragen erfindet, wird lang und trotzdem nicht gelesen. Die Bauform steht fest und ist an der ersten Frage vorgeführt: Symptomtabelle mit den echten Wortlauten, Schritt 0 (*ist es überhaupt dieser Fall?*), die Antwort je Plattform mit einer Entscheidungsspalte statt einer Aufzählung, und ein **eigener Belegstand**, sobald fremde Befehle zitiert werden |
| BL-117 | **Der Prompt-Gleichstand ist am QUELLTEXT bewiesen, nicht am LAUF — Drift in den eingesetzten Werten bliebe unsichtbar.** [`test_bl112_prompt_gleichstand.py`](../geteilt/tests/test_bl112_prompt_gleichstand.py) vergleicht die **Prosa** beider Bahnen, nachdem jede Variableneinsetzung zu einem Platzhalter geworden ist. Das trifft den Fall, für den `BL-112` geschrieben wurde (jemand schärft eine Feldlehre in nur einer Fassung nach), und es lässt genau eine Lücke: Setzen die beiden Bahnen in denselben Platzhalter **verschiedene Werte** ein — ein anders abgeleiteter Ordnername, eine Fallunterscheidung, die nur eine Seite kennt, ein `team.config.ps1`, das einen Wert anders vorbelegt —, sind die Prompts verschieden und der Test bleibt grün. Diese Hälfte kann nur ein **Lauf** zeigen | Kit, 2026-08-20 — beim Abtragen von `BL-112` ausgewiesen statt behauptet: Die Fix-Skizze dort sah den Lauf-Vergleich vor, und der braucht **beide** Shells auf **einer** Maschine. Auf der Entwicklungsmaschine ist kein `pwsh` installiert; ein blind geschriebener Test, dessen erste Ausführung auf einer fremden Maschine stattfindet, wird dort „angepasst" statt gelesen — dieselbe Erwägung, die `BL-113` teuer belegt hat (die pwsh-Bahn fiel erst auf der Zielmaschine auf) | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Bauart wie in `BL-112` skizziert: ein `claude`-Stub, der sein `-p`-Argument in eine Datei schreibt statt zu arbeiten (`Schale.claude_stub` kann das Gerüst schon), jede Rolle einmal je Bahn gefahren, die beiden Prompt-Dateien zeichenweise verglichen. **Die Ausnahmeliste ist bereits da** und wird mitbenutzt, samt ihrer Probe gegen unnötige Einträge — der Lauf-Vergleich erbt sie, statt eine zweite aufzumachen. **Gegenprobe, die ihn erst gültig macht:** ein absichtlich abweichend vorbelegter Wert in einer der beiden Konfigurationen, an dem der Test fallen muss. Solange er fehlt, gilt die Zusicherung „gleicher Prompt" ausdrücklich nur für die Prosa |

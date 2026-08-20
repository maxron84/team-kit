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

**Stand 2026-08-20: zwei offene Einträge** (`BL-117`, `BL-119`). An diesem Tag
sind `BL-111`, `BL-112`, `BL-114`, `BL-115`, `BL-116` und `BL-118` abgetragen
worden; `BL-117` ist beim Abtragen von `BL-112` als ausgewiesener Rest
entstanden — die Hälfte der Zusicherung, die sich nur auf einer Maschine mit
PowerShell 7 beweisen lässt. `BL-118` (Ordner-Trennung im Kit) ist noch am
selben Tag abgetragen worden; `BL-119` bleibt: Die Trennung ist im **Kit**
sichtbar, im **Zielprojekt** noch nicht. Alle Begründungen stehen im Archiv.

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-117 | **Der Prompt-Gleichstand ist am QUELLTEXT bewiesen, nicht am LAUF — Drift in den eingesetzten Werten bliebe unsichtbar.** [`test_bl112_prompt_gleichstand.py`](../geteilt/tests/test_bl112_prompt_gleichstand.py) vergleicht die **Prosa** beider Bahnen, nachdem jede Variableneinsetzung zu einem Platzhalter geworden ist. Das trifft den Fall, für den `BL-112` geschrieben wurde (jemand schärft eine Feldlehre in nur einer Fassung nach), und es lässt genau eine Lücke: Setzen die beiden Bahnen in denselben Platzhalter **verschiedene Werte** ein — ein anders abgeleiteter Ordnername, eine Fallunterscheidung, die nur eine Seite kennt, ein `team.config.ps1`, das einen Wert anders vorbelegt —, sind die Prompts verschieden und der Test bleibt grün. Diese Hälfte kann nur ein **Lauf** zeigen | Kit, 2026-08-20 — beim Abtragen von `BL-112` ausgewiesen statt behauptet: Die Fix-Skizze dort sah den Lauf-Vergleich vor, und der braucht **beide** Shells auf **einer** Maschine. Auf der Entwicklungsmaschine ist kein `pwsh` installiert; ein blind geschriebener Test, dessen erste Ausführung auf einer fremden Maschine stattfindet, wird dort „angepasst" statt gelesen — dieselbe Erwägung, die `BL-113` teuer belegt hat (die pwsh-Bahn fiel erst auf der Zielmaschine auf) | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Bauart wie in `BL-112` skizziert: ein `claude`-Stub, der sein `-p`-Argument in eine Datei schreibt statt zu arbeiten (`Schale.claude_stub` kann das Gerüst schon), jede Rolle einmal je Bahn gefahren, die beiden Prompt-Dateien zeichenweise verglichen. **Die Ausnahmeliste ist bereits da** und wird mitbenutzt, samt ihrer Probe gegen unnötige Einträge — der Lauf-Vergleich erbt sie, statt eine zweite aufzumachen. **Gegenprobe, die ihn erst gültig macht:** ein absichtlich abweichend vorbelegter Wert in einer der beiden Konfigurationen, an dem der Test fallen muss. Solange er fehlt, gilt die Zusicherung „gleicher Prompt" ausdrücklich nur für die Prosa |
| BL-119 | **Ein Zielprojekt bekommt 29 Entrypoints in die Wurzel, von denen der Anwender 19 nie anfasst.** Wer unter Linux arbeitet, sieht `ralph.ps1` und `ralph.cmd` neben `ralph.sh`; wer Windows ohne WSL benutzt, das Umgekehrte. Der naheliegende Wunsch — nur die eigene Bahn installieren, oder die fremde in einen Unterordner — hat **zwei belegte Gegengründe**, und der zweite ist ein echter Konflikt, keine Formsache: **(a)** `install.sh` installiert beide Bahnen ausdrücklich deshalb, weil `team.config.sh` und `team.config.ps1` **zwei Generate einer Quelle** sind (denselben neun Antworten). Installierte nur eine Bahn, hätte ein auf Linux eingerichtetes Projekt unter Windows keine Konfiguration — und jemand schriebe sie von Hand. Genau dort fängt Drift an. **(b)** `BL-3` pinnt, dass jeder Entrypoint als zweite Zeile in **sein** Skriptverzeichnis wechselt; `kosten.py` hält seine Pfade arbeitsverzeichnis-relativ (`.budget-ledger`). Läge die pwsh-Bahn in `windows/`, meldete `kosten.py` dort still `0.0000 USD` statt zu scheitern — dieselbe Klasse wie `BL-55`, und die Budget-Durchsetzung wäre blind | Kit, 2026-08-20 — beim Bau der Bahn-Kennung als der teure Rest ausgewiesen. Die Frage kommt aus dem Feld („warum liegen hier 19 Dateien für ein System, das ich nicht benutze?") und ist berechtigt; die Antwort ist nur keine Ablage-Frage, sondern eine Invarianten-Frage | **offen, und ausdrücklich NICHT als Ordner-Umzug zu bauen.** Der billige Weg, der beide Gegengründe respektiert: ein Installer-Schalter (`--nur-bash` / `-NurPwsh`) als **bewusste Abwahl** durch den Anwender, Default bleibt beides. Dann trägt der Abwählende die Folge, statt sie geerbt zu bekommen. **Gegenprobe, die ihn erst gültig macht:** ein so installiertes Projekt muss beim späteren `--update` ohne Schalter wieder vollständig werden, sonst ist die Abwahl eine Einbahnstraße. Ein Umzug in `windows/` wäre nur tragfähig, wenn vorher `BL-3` von „Skriptverzeichnis" auf „Repo-Wurzel" umgestellt und neu bewiesen wird — das ist eine eigene Kaskade, keine Aufräumarbeit |

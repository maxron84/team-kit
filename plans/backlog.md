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

**Stand 2026-08-20: fünf offene Einträge** (`BL-111`, `BL-112`, `BL-114`,
`BL-115`, `BL-116`). Die zuletzt abgetragenen (`BL-62`, `BL-108`, `BL-109`,
`BL-110`, `BL-113`) stehen mit voller Begründung im Archiv.

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-112 | **Die Briefings sind geteilt, der ZUSAMMENGESETZTE Prompt ist es nicht — rund 140 Zeilen agentensteuernde Prosa liegen jetzt doppelt.** Der Plan [`windows-nativ.md`](windows-nativ.md) stützt sich auf die Feststellung, die driftgefährlichste Fläche sei „konstruktionsbedingt bereits single-source": [`team_briefing`](../team/lib.sh#L621) ist ein `cat` auf [`team/prompts/rolle-*.md`](../team/prompts/), und die 340 Zeilen Briefing gelten damit für beide Zweige. **Das stimmt — und es ist die halbe Wahrheit.** Der Prompt, der die Rolle wirklich erreicht, entsteht erst im Einstiegsskript: In [`team/redteam.sh`](../team/redteam.sh#L117-L152) sind das 35 Zeilen (Auftrag, `SCOPE_LINE`, `KONTROLLFLUSS_ZEILE` aus BL-39, die EISERNE REGEL, der Beutebuch-Block, der BL-47-Absatz), dazu je ~20 Zeilen in [`ralph.sh`](../entry/ralph.sh#L72-L84), [`frank.sh`](../entry/frank.sh#L78-L99) und [`axel.sh`](../entry/axel.sh#L54-L74). Diese Prosa steht seit Stufe 4 **zweimal** im Repo — einmal in `.sh`, einmal in `.ps1`. Wer eine Feldlehre in Harrys Auftrag nachschärft und nur eine Fassung anfasst, bekommt zwei Zweige, die **verschiedene Agenten** steuern. Kein Test schlägt an: Beide Zweige laufen grün, die Prompts sind nur nicht mehr dieselben. Das ist die einzige verbliebene Stelle, an der Drift **unsichtbar** wäre — überall sonst greift die Doppelbahn. **Nachgemessen 2026-08-20: noch keine Drift eingetreten.** Die vier Prompt-Blöcke wurden normalisiert verglichen (Variablensyntax herausgerechnet, `PROMPT="…"` gegen `@"…"@`) — `ralph`, `frank`, `axel` und `redteam` sind heute **zeichengleich**. Der Eintrag beschreibt also ein Risiko, keinen Schaden; das ist der günstigste Zeitpunkt für den Test, weil er grün startet und jede spätere Abweichung ihm zuzuschreiben ist. **Die Fläche ist grösser als oben angegeben:** Agentensteuernde Prosa liegt nicht nur in den vier Einstiegsskripten, sondern auch in der Bibliothek selbst — `SMOKE_ZEILE` in [`lib.sh:34`](../team/lib.sh#L34) und [`lib.psm1:144`](../team/lib.psm1#L144) trägt die Vordergrund-Regel aus `BL-41` und ist ebenfalls doppelt geführt | Kit, 2026-08-17 — bei der Portierung der Rollen ([plans/windows-nativ.md](windows-nativ.md), Stufe 4) aufgefallen und dort im Baustand vermerkt | **offen.** **Fix-Skizze, bewusst NICHT „Prosa nach `team/prompts/` auslagern":** Das wäre der naheliegende Weg und würde den Bash-Zweig verhaltensrelevant anfassen — was die Stufen 1–4 ausdrücklich nicht tun. Stattdessen ein **Gleichstands-Test in der Doppelbahn**, dieselbe Bauart wie Schritt 10/10 in `kit-test.sh`: ein `claude`-Stub, der sein `-p`-Argument in eine Datei schreibt statt zu arbeiten, jede Rolle einmal je Bahn gefahren, und die beiden Prompt-Dateien **zeichenweise** verglichen. Das prüft nicht, woran jemand gedacht hat, sondern jede Zeile, die auseinanderläuft. Der Stub gehört in `Schale.claude_stub` (existiert bereits, muss nur die Argumente mitschreiben). Danach ist auch die Auslagerung nach `team/prompts/` gefahrlos möglich — mit einem Test, der beweist, dass sie den Prompt nicht verändert hat. **Eine Stolperstelle der Skizze, vor dem Bau zu klären:** Der zeichenweise Vergleich schlägt auch auf **legitime** Zweigunterschiede an — `SMOKE_ZEILE` nennt im Bash-Zweig `team.config.sh` und im PowerShell-Zweig `team.config.ps1`, und das ist richtig so. Der Test braucht deshalb eine **ausgewiesene Ausnahmeliste mit Begründung je Eintrag**; ohne sie ist er am ersten Tag rot und wird abgeschaltet statt gelesen, und ohne die Begründungspflicht wird die Liste zur Sammelstelle, hinter der die echte Drift verschwindet |

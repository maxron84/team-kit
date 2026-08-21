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
seit `BL-136` rot). Seither abgetragen: `BL-144`, `BL-142`, `BL-143`, `BL-129`, `BL-140`,
`BL-139`, `BL-141`, `BL-120`. Damit sind alle fünf Feldmeldungen des Tages
abgetragen — und vom Stand davor bleibt nur `BL-117`. Die Reihenfolge
folgt der Wirkung, nicht der Nummer — zuerst, was den dokumentierten Weg
blockiert, dann was falsch bucht, dann was falsch anleitet.

**Stand 2026-08-21: fünf Meldungen aus dem Feld dazu** (`BL-139` bis `BL-143`),
alle aus `duke-itam-2026` — einer frischen, mit `--nur-pwsh` installierten
Ablage, die an diesem Tag ihre **allererste** Kaskade geplant, gebaut und
abgeschlossen hat. `BL-139`/`BL-140` fielen beim **Anlegen** auf, `BL-141` bis
`BL-143` im **Closeout**.

Der Tag zerfällt in zwei Gruppen. **Die Vorlagen** (`BL-139`, `BL-140`, in
`bootstrap/`) schicken die Rollen an Dateien und Nummern, die es so nicht gibt —
still, ohne Meldung. **Beide sind abgetragen**: die Nummern stimmen wieder,
und die Pfade nennen die Bahn, in der sie stehen. **Die Kostenkette** (`BL-141`–`BL-143`, in
`geteilt/tools/kosten.py` und `team-status.ps1`) ist der eigentliche Fund des
Tages: Der erste echte Kostenabschluss eines Projekts hat sie alle drei
aufgedeckt, und keiner davon war vorher zu sehen, weil sie erst beim
**vollständigen** Durchlauf zuschlagen — `BL-142` brach genau bei dem Aufruf
ab, den die Doku vorgibt (abgetragen), `BL-143` buchte Abo-Kosten in die
API-Spalte (abgetragen), und
`BL-141` lieferte die Zahl, die dort landet, als Zeilen-Churn-Proxy statt als
Messung. Wer eine Kaskade zu Ende führte, traf alle drei nacheinander — **alle
drei sind abgetragen**, und die Messung liegt jetzt als Werkzeug im Kit
(`kosten.py sitzung-messen`).

`BL-139` war der inhaltliche Zwilling von `BL-129` (beide abgetragen) — dort
fiel die einbahnige Ablage im Testharnisch auf, hier im Regeltext, den jede
Rolle in jedem Aufruf im Systemprompt hat.

**Stand 2026-08-20: drei offene Einträge** (`BL-117`, `BL-120`, `BL-129` — die
letzten beiden am 2026-08-21 abgetragen; `BL-117` bleibt und kann hier nicht
fallen, siehe unten).
`BL-120` war am selben Tag beim Doku-Durchgang dazugekommen und hatte mit dem
Rest dieses Tages nichts zu tun: ein Gerüst, das erst eine Frage trug. Die drei
dort benannten Kandidaten sind geschrieben; das Gerüst darüber hinaus bleibt
bewusst leer.
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
| BL-117 | **Der Prompt-Gleichstand ist am QUELLTEXT bewiesen, nicht am LAUF — Drift in den eingesetzten Werten bliebe unsichtbar.** [`test_bl112_prompt_gleichstand.py`](../geteilt/tests/test_bl112_prompt_gleichstand.py) vergleicht die **Prosa** beider Bahnen, nachdem jede Variableneinsetzung zu einem Platzhalter geworden ist. Das trifft den Fall, für den `BL-112` geschrieben wurde (jemand schärft eine Feldlehre in nur einer Fassung nach), und es lässt genau eine Lücke: Setzen die beiden Bahnen in denselben Platzhalter **verschiedene Werte** ein — ein anders abgeleiteter Ordnername, eine Fallunterscheidung, die nur eine Seite kennt, ein `team.config.ps1`, das einen Wert anders vorbelegt —, sind die Prompts verschieden und der Test bleibt grün. Diese Hälfte kann nur ein **Lauf** zeigen | Kit, 2026-08-20 — beim Abtragen von `BL-112` ausgewiesen statt behauptet: Die Fix-Skizze dort sah den Lauf-Vergleich vor, und der braucht **beide** Shells auf **einer** Maschine. Auf der Entwicklungsmaschine ist kein `pwsh` installiert; ein blind geschriebener Test, dessen erste Ausführung auf einer fremden Maschine stattfindet, wird dort „angepasst" statt gelesen — dieselbe Erwägung, die `BL-113` teuer belegt hat (die pwsh-Bahn fiel erst auf der Zielmaschine auf) | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Bauart wie in `BL-112` skizziert: ein `claude`-Stub, der sein `-p`-Argument in eine Datei schreibt statt zu arbeiten (`Schale.claude_stub` kann das Gerüst schon), jede Rolle einmal je Bahn gefahren, die beiden Prompt-Dateien zeichenweise verglichen. **Die Ausnahmeliste ist bereits da** und wird mitbenutzt, samt ihrer Probe gegen unnötige Einträge — der Lauf-Vergleich erbt sie, statt eine zweite aufzumachen. **Gegenprobe, die ihn erst gültig macht:** ein absichtlich abweichend vorbelegter Wert in einer der beiden Konfigurationen, an dem der Test fallen muss. Solange er fehlt, gilt die Zusicherung „gleicher Prompt" ausdrücklich nur für die Prosa |

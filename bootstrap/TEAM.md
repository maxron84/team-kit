# T.E.A.M. in {{PROJEKTNAME}} — Bedienung

Dieses Projekt wird von einem **Team aus KI-Rollen** vorangetrieben, das du als
*Strippenzieher* steuerst. Diese Datei ist für **dich**, den Menschen.
Die Regeln für die KI-Rollen stehen in [`CLAUDE.md`](CLAUDE.md).

**Neu hier?** Erst die Warnung direkt darunter — sie ist die teuerste des
Kits. Dann [Worum es überhaupt geht](#worum-es-überhaupt-geht) und das
[Glossar](#glossar--die-begriffe-in-einem-satz); danach ergibt der Rest sich
von selbst. Später mal einen neueren Kit-Stand holen? →
[Auf eine neue Kit-Version heben](#auf-eine-neue-kit-version-heben).

---

## ⚠️ Zuerst: committen

**Bevor du irgendeine Rolle startest, muss der Baum sauber sein.**

```bash
git add -A && git commit -m "chore: T.E.A.M. eingerichtet"
```

Der Read-Only-Guard prüft nach jedem Sweep, ob eine Rolle außerhalb ihrer
erlaubten Pfade geschrieben hat — und setzt Verletzer zurück. **Uncommittete
Dateien außerhalb der Whitelist sehen für ihn genauso aus wie ein Regelbruch.**
Im Ursprungsprojekt hat ein Guard-Lauf einmal die gesamte frisch gebaute
Team-Infrastruktur gelöscht, weil sie noch nicht committet war.

Der Rollback ist heute chirurgisch (er trifft nur die konkret gelisteten Pfade),
aber die Regel bleibt: **erst committen, dann starten.**

---

## Worum es überhaupt geht

Du kannst eine KI bitten, ein Feature zu bauen. Das funktioniert — bis das
Projekt groß genug ist, dass „bau mal" nicht mehr reicht. Dann passieren drei
Dinge: Die KI baut Dinge vorweg, die noch niemand entschieden hat. Sie findet
ihre eigenen Fehler nicht, weil sie ihren eigenen Code für richtig hält. Und
niemand weiß hinterher, was das gekostet hat.

Das T.E.A.M. beantwortet genau diese drei Punkte — mit **Arbeitsteilung statt
einer allmächtigen Instanz**:

- **Geplant wird vor dem Bauen.** Eine **Kaskade** ist ein Bauabschnitt, der
  vorher in nummerierte **Stufen** zerlegt wurde. Der Bau-Loop arbeitet sie
  stur der Reihe nach ab und darf **nichts vorwegnehmen**. Das klingt
  bürokratisch und ist der Kern: Es macht den Fortschritt prüfbar und den
  Abbruch billig.
- **Finder ≠ Fixer.** Wer einen Fehler sucht, darf ihn nicht beheben. Das Red
  Team (Harry, Marv) kommt **read-only** ins Projekt — es kann gar nicht
  „schnell mal reparieren" und damit den Fund verwischen. Ein Fund wird
  aufgeschrieben und **übergeben**. Wer prüft, was er selbst gebaut hat, findet
  vorhersehbar wenig.
- **Jeder Lauf kostet Geld, also wird es gezählt.** Budget-Deckel brechen
  Ausreißer ab, und nach jedem Lauf wandern die tatsächlichen Kosten in eine
  committete Datei. Ohne diesen Schritt ist der Verbrauch nach zwei Wochen
  blind.

**Deine Rolle dabei:** Du entscheidest Richtung und Prioritäten, gibst
Kaskaden frei und schaltest sie scharf. Bauen, Angreifen, Fixen und Ermitteln
machen die KI-Rollen. Deshalb *„Toll, Ein Anderer Macht's"* — mit voller
Absicht.

---

## Glossar — die Begriffe in einem Satz

Diese Wörter tauchen überall auf; hier stehen sie einmal an einem Ort.

| Begriff | Bedeutung |
|---|---|
| **Strippenzieher** | Du. Der Mensch, der Richtung, Prioritäten und Freigaben bestimmt. |
| **Kaskade** | Ein geplanter Bauabschnitt, zerlegt in nummerierte Stufen. Die Einheit, in der hier gearbeitet und abgerechnet wird. |
| **Stufe** | Ein Schritt einer Kaskade — ein Commit, ein grüner Smoke-Test. |
| **Aushärten** | Eine lose Skizze in einen festen Plan mit Stufennummern und Deckel überführen. Macht der Architekt, erst auf deine Freigabe. |
| **Scharfschalten** | Den Zeiger `.ralph-plan` auf den fertigen Plan setzen, damit der Loop ihn baut. Bleibt **deine** Handarbeit. |
| **Promise** | Die Quittung einer Rolle am Ende ihrer Arbeit (`<promise>STUFE_N_COMPLETE</promise>`). Fehlt sie, gilt die Stufe als unfertig. |
| **Sweep** | Ein Durchlauf des Red Teams: Harry und Marv suchen Schwachstellen, ohne etwas zu ändern. |
| **Fund** | Eine entdeckte Schwachstelle, dokumentiert mit Reproschritten. Trägt eine Nummer (`HM-7`). |
| **Beutebuch** | Die Datei, in der alle Funde stehen — samt Status, wer gerade dran ist. Das Übergabeprotokoll zwischen den Rollen. |
| **Ermittlungsakte** | Axels Bericht zu einem harten Fall: Ursache plus Fix-Plan (`AX-3`). Er denkt, Frank tippt. |
| **Guard** | Die Schutzmechanik, die nach jedem Lauf prüft, ob eine read-only Rolle doch geschrieben hat — und das zurücksetzt. |
| **Cap** | Ein Budget-Deckel in USD. **Soft-Cap** warnt, **Hard-Cap** bricht ab. |
| **Ledger** | Die committete Kostendatei (`.budget-ledger`). Die maschinelle Wahrheit darüber, was gelaufen ist. |
| **Closeout** | Der Pflichtabschluss nach jedem Lauf: Protokoll schreiben, Kosten buchen. Ohne ihn sind die Kosten blind. |
| **Backlog** | Kleinkram und Schulden, die keine eigene Kaskade rechtfertigen. |

---

## Die sechs Rollen

| Rolle | Was sie tut | Produktivcode? |
|---|---|---|
| **Der Architekt** | plant Kaskaden, setzt Caps, macht den Closeout | nur im Ausnahmefall |
| **Ralph** | Bau-Loop, arbeitet den Plan Stufe für Stufe ab | ja |
| **Frank** | Ad-hoc-Fixes außerhalb des Loops | ja |
| **Harry** | Red Team Security — greift an, fixt nicht | **nein** (Guard) |
| **Marv** | Red Team Chaos — bricht Dinge, fixt nicht | **nein** (Guard) |
| **Axel** | Forensiker für harte Fälle, starkes Modell | **nein** (Guard) |

**Finder ≠ Fixer**: Wer einen Fehler findet, behebt ihn nicht selbst. Übergabe
läuft über das Beutebuch ([`{{PLAN_ORDNER}}/beutebuch.md`]({{PLAN_ORDNER}}/beutebuch.md)).

### Welches Modell arbeitet wo

Die Skripte kennen **keine Modellnamen**, sondern zwei Stufen — du kannst sie
pro Lauf überschreiben, ohne irgendetwas neu zu installieren:

| Stufe | Variable | Default | Wer darauf läuft |
|---|---|---|---|
| schwach | `TEAM_MODEL_LOOP` | `sonnet` | Ralph, Harry, Marv, Frank |
| stark | `TEAM_MODEL_STRONG` | `opus` | Axel — und deine Architekten-Sitzung |

```bash
TEAM_MODEL_LOOP=opus ./vollautomatik.sh     # eine Kaskade auf der starken Stufe
```

Die Defaults sind **Defaults, keine Voraussetzung**. Vorausgesetzt sind
Fähigkeiten: eine große Regeldatei tragen (`CLAUDE.md` wird bei jedem
Rollenaufruf geladen), Werkzeuge zuverlässig aufrufen, das `<promise>`-Protokoll
bis zum Ende eines langen Laufs durchhalten, Auflagen einhalten, die niemand
erzwingt, und ohne Rückfragen arbeiten — es sitzt niemand daneben. Heute
erfüllen das Sonnet und Opus über Claude Code; das Kit ist so gebaut, dass sich
das austauschen lässt (Hintergrund: `README.md`, Abschnitt **Modelle**).

**Kosten sind der Grund für die Trennung.** Die schwache Stufe trägt die Masse
der Aufrufe. Wer sie hochdreht, dreht die Rechnung mit hoch — deshalb steht der
Kontostand in `./team-status.sh --budget` und nicht im Kleingedruckten.

> **T.E.A.M. international** — für Projekte auf Englisch oder Italienisch bleiben
> die Initialen **T-E-A-M** zwingend erhalten, ebenso die selbstironische Pointe
> („die Arbeit macht — mit voller Absicht — ein anderer"):
> - 🇬🇧 **Thankfully, Everyone (but me) Achieves More** — dreht das bekannte
>   Motivationsposter „Together Everyone Achieves More" ironisch um.
> - 🇮🇹 **Tanto, Ecco, Altri (lo fanno)… Ma certo!** — „Ach, sieh an, andere
>   machen's… aber sicher!"; das achselzuckende *„Tanto…"* spiegelt das ironische
>   deutsche „Toll".

---

## Der Ablauf einer Kaskade

### 1. Planen — Claude-Sitzung in diesem Ordner, starkes Modell

> Du bist unser Architekt, lies `team/prompts/rolle-architekt.md`.

Er schreibt eine Skizze in
[`{{PLAN_ORDNER}}/roadmap-skizzen.md`]({{PLAN_ORDNER}}/roadmap-skizzen.md),
härtet sie auf deine Freigabe zu `{{PLAN_ORDNER}}/ralph-kaskade-N-….md` aus und
gibt dir am Ende eine **kopierfertige Scharfschalt-Sequenz**. Du musst nichts
selbst zusammensuchen.

### 2. Scharfschalten

```bash
echo {{PLAN_ORDNER}}/ralph-kaskade-N-….md > .ralph-plan
```

Diese Zeiger-Datei ist die **einzige** Quelle für Plan-Pfad, `RALPH_CAP` und
`BUDGET_EMPFEHLUNG_USD`. Ein veralteter Zeiger ist die häufigste Ursache für
einen stillen Fehlstart.

### 3. Laufen lassen

```bash
TEAM_BUDGET_USD=15 ./vollautomatik.sh
```

Fährt die ganze Kaskade: Ralph baut → Red Team greift an → Frank fixt →
Axel knackt die harten Fälle → Abschlussbericht.

Vorsichtiger, Schritt für Schritt mit Halt bei dir:

```bash
./halbautomatik.sh          # zeigt den empfohlenen nächsten Schritt
./halbautomatik.sh ralph    # nur diesen einen Schritt
```

### 4. Closeout — Pflicht, nicht Kür

```bash
./team-status.sh --rollen-abschluss <N> <domaene> ["<notiz-rollen>"] ["<notiz-bau>"]
./team-status.sh --architekt-abschluss <USD> <domaene> "Kaskade N geplant"
```

Der erste Befehl schließt **beide** Kostenquellen des Laufs ab und schreibt
dafür **zwei** Ledger-Zeilen: `roles` für Harry/Marv/Frank/Axel und `ralph`
für die Baukosten. Die Rohlogs werden dabei archiviert, damit der Kontostand
sie nicht ein zweites Mal zählt. Jede Zeile bekommt ihren **eigenen** Text:
Der dritte Parameter beschriftet die Rollen-Zeile, der vierte die Bau-Zeile.
Lässt du den vierten weg, wird die Bau-Notiz aus dem Plannamen abgeleitet
(`K22 doku-konsolidierung`) — **nicht** von deinem Rollen-Text kopiert. Grund:
Beim Abschluss denkst du an die Sweeps, und genau dieser Text stand im Feld
zweimal über Ralphs Baustufen.

**Wenn für Kaskade und Rolle schon eine Zeile steht, brechen beide Befehle
ab** und nennen Alt-, Neu- und Summenwert. Dann entscheidest du:
`--addieren` (es lief noch etwas nach bzw. du arbeitest in einer zweiten
Sitzung an derselben Kaskade) oder `--ersetzen` (die Altzeile war eine
Fehlmessung). Nichts wird stillschweigend überschrieben — im Feld sind so
5,5515 USD spurlos aus einem Ledger verschwunden.

Buchst du für eine **andere** als die aktive Kaskade, hänge `--kaskade <N>`
an: Ohne den Schalter nimmt das Werkzeug die Nummer aus `.ralph-plan`, und
die zeigt nach einem Closeout noch auf die **vorige** Kaskade.

**Warum das nicht optional ist:** Der Architekt läuft interaktiv, außerhalb der
Kostenlogs. Ohne diesen Schritt bleibt seine Sitzung strukturell unerfasst — im
Ursprungsprojekt waren das real rund 16 USD pro Session. Der Kostenabschluss
gehört **nach** den Lauf, niemals in eine Loop-Stufe.

**Was `<domaene>` ist:** der Arbeitsstrang, auf den die Kosten gebucht werden —
bei den meisten Projekten schlicht `produkt`. **Dieses Projekt führt genau eine
Domäne**, solange du in `team.config.sh` nichts anderes einträgst. Mehrere sind
nur sinnvoll, wenn *dieses* Projekt fachlich getrennte Stränge hat (etwa
`backend frontend`). Eine eigene Domäne für die Arbeit am T.E.A.M. brauchst du
**nicht**: Am Team wird hier nicht entwickelt — was dir am Team auffällt, geht
ins Kit-Repo zurück und wird dort verbucht.

**Wenn nach dem Closeout noch eine Rolle lief** (z. B. ein Frank-Fix), bricht ein
zweiter `--rollen-abschluss` ab, statt die erste Buchung zu überschreiben, und
nennt Alt-, Neu- und Summenwert. Den Nachlauf buchst du mit
`--rollen-abschluss <N> <domaene> "" --addieren` dazu; `--ersetzen` gibt es für
den Fall, dass die alte Zeile schlicht falsch war.

**Prüfen statt glauben:**

```bash
./team-status.sh --ledger-pruefen
```

Sagt dir, ob für jede Kaskade alles gebucht ist: fehlt eine Zeile je Quelle
(`ralph`/`roles`/`architekt`), liegen unarchivierte Logs herum, obwohl die
Kaskade schon abgeschlossen ist, **liegen Logs herum, die älter sind als die
laufende Kaskade** (dann wurde ein früherer Durchgang gebaut und nie
abgeschlossen — im Feld lagen so 33,89 USD ungebucht in den Logordnern, ohne
dass irgendetwas rot wurde), und — die eigentliche Probe — **ergeben die
archivierten Rohlogs mehr, als im Ledger steht?** Diese letzte Frage stellt die
Gegenkennzahl aus einer **anderen** Quelle als das Ledger selbst. Genau daran
hakte es dreimal: Die schwersten Kostenfehler des Kits (`BL-1`, `BL-4`, `BL-5`)
sind alle **nicht** durch ein Werkzeug aufgefallen, sondern dadurch, dass ein
Mensch den Bericht neben das Ledger hielt. Exit `4` heißt Warnbefunde, `0`
sauber. Warnungen laufen bei jedem `--budget` ungefragt mit.

**Die Architekt-Zeile in `--budget` liest du an ihrer Beschriftung**, nicht aus
dem Gedächtnis: Sie gilt für **eine** Kaskade (`Architekt K3 …`), während jede
andere Zeile des Blocks lebenslang kumuliert, und sie sagt selbst, ob sie im
`Gesamt` schon steckt. `geschätzt` heißt „nicht im Gesamt enthalten" (der Wert
ist eine Live-Schätzung, keine Ledger-Zeile) — sobald du sie per
`--architekt-abschluss` gebucht hast, springt sie auf `echt, im Gesamt
enthalten` und darf **nicht** noch einmal draufgerechnet werden.

```bash
python3 team/tools/zitat_lint.py
```

Meldet Plandateien, die einen **erledigten** Backlog-Eintrag noch als offene
Frage zitieren — der Fall, der sonst erst auffällt, wenn dir jemand einen
Kandidaten vorlegt, den es nicht mehr gibt. Exit `3` = Befunde, kein Blocker.

Der Architekt schreibt außerdem ein `{{PLAN_ORDNER}}/kaskade-N-abschluss.md`.
Der Terminal-Abschlussbericht ist flüchtig; das Protokoll bleibt im Git.

---

## Befehle im Überblick

| Linux / WSL | Windows | Wirkung |
|---|---|---|
| `./vollautomatik.sh` | `.\vollautomatik.cmd` | ganze Kaskade automatisch |
| `./halbautomatik.sh [rolle]` | `.\halbautomatik.cmd [rolle]` | ein Schritt, Entscheidung bei dir |
| `./team-status.sh` | `.\team-status.cmd` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --budget` | `.\team-status.cmd --budget` | Kontostand, API vs. Abo getrennt |
| `./team-test.sh` | `.\team-test.cmd` | Regressionstests der **Team-Infrastruktur** |
| `python3 team/tools/beutebuch.py list` | *(gleich)* | alle Funde mit Status |

**Welche Spalte für dich gilt:** die linke, wenn du unter Linux oder in einer
WSL-Distro arbeitest; die rechte, wenn du Windows **ohne** WSL benutzt. Beide
Spalten tun dasselbe — es sind zwei Schreibweisen, kein Funktionsunterschied.
Die letzte Zeile steht bewusst als *(gleich)* da: Die Werkzeuge sind Python und
werden auf beiden Wegen identisch aufgerufen.

`./team-test.sh` prüft **nicht** dein Projekt. Dein Testbefehl ist:
`{{SMOKE_TEST}}`

> **Regel: Der Smoke-Test darf keine Umgebung setzen, die die Doku nicht nennt.**
> Jeder Befehl, den deine Doku einem Menschen nennt, muss in der Verifikation
> buchstabengetreu vorkommen — gleiche Argumente, gleiche Umgebung, kein
> zusätzliches `PYTHONPATH`, kein stilles `cd`. Sonst passiert, was im Feld
> passiert ist: Der dokumentierte Startbefehl war kaputt, der Smoke-Test meldete
> grün, und gefunden hat es niemand aus dem Team — sondern der Mensch, als er
> das Produkt zum ersten Mal selbst startete.

---

## Exit-Codes — was sie bedeuten

| Code | Bedeutung | Was tun |
|---|---|---|
| `0` | durchgelaufen | Closeout machen |
| `1` | **echter Fehler** | Log lesen, Ursache beheben |
| `3` | nichts zu tun | normal, kein Fehler |
| `42` | **Session-Limit** — Lauf pausiert | **kein Fehler.** Kein Datenverlust, State steht. Später erneut starten. |
| `43` | **Stufe fertig, Quittung fehlt** | **Nicht neu bauen.** Erst prüfen: hat die Rolle committet, ist der Smoke-Test grün? Wenn ja: von Hand quittieren (`echo <nächste Stufe> > .ralph-state`) und weiterlaufen lassen. |

`42` ist die häufigste Verwechslung: Das ist kein Absturz, sondern eine saubere
Pause. Nichts ist verloren, der Lauf setzt beim nächsten Start fort.

`43` ist die zweite: Die Rolle hat ihre Sitzung beendet, ohne zu quittieren —
meist, weil sie auf einen Hintergrund-Task wartete, den es in einer
headless-Sitzung nicht gibt. Das Log meldet trotzdem Erfolg. **Die Arbeit ist
in diesem Fall meistens fertig**; ein Neustart wirft sie weg und zahlt sie noch
einmal (im Feld viermal passiert, zusammen 19,47 USD). Die Meldung des Loops
nennt die zwei Prüfungen, die vorher zu machen sind.

---

## Wo was liegt

```
team.config.sh          ALLE Projektwerte — der einzige Ort zum Ändern
CLAUDE.md               Regeln für die KI-Rollen (geltendes Recht)
{{PLAN_ORDNER}}/        Kaskaden-Pläne, Beutebuch, Ermittlungsakten, Roadmap
team/                   Team-Infrastruktur (lib, tools, prompts, tests)
.budget-ledger          Kostenbasis — committet, nicht ignorieren
.ralph-plan             Zeiger auf den aktiven Plan
.ralph-state            nächste zu bauende Stufe
```

**Einen Wert ändern?** Immer in `team.config.sh`. Er wirkt sofort in allen
Rollen, ohne Neuinstallation.

### Zog das Team in eine gewachsene Codebasis ein?

Zwei Werte in `team.config.sh` tragen dann Gewicht, die im neuen Projekt leer
bleiben dürfen:

| Wert | Wozu |
|---|---|
| `TEAM_WEITERER_CODE` | Code außerhalb von `{{PRODUKTIVCODE}}`, der mitgeprüft werden soll: Einstiegspunkt in der Wurzel, Build-/Deploy-Skripte. Was hier nicht steht, greift das Red Team **nie** an — und ein sauberer Sweep sieht trotzdem aus wie ein sauberes Projekt (`BL-52`). |
| `TEAM_TEST_ORDNER_BESTAND` / `TEAM_PLAN_ORDNER_BESTAND` | Was beim Einzug schon in den beiden Schreibordnern lag. Der Guard schlägt dort **nicht** an — Harry, Marv und Axel dürfen dort schreiben und löschen. Die Einträge werden den Rollen im Prompt als fremdes Eigentum genannt: neue Dateien anlegen ja, Bestehendes anfassen nein (`BL-51`). |

Der Installer füllt beides beim Einzug und warnt, wenn Plan- oder Test-Ordner
belegt sind. **Die harte Variante** bleibt der eigene, leere Plan-Ordner
(`team-plans/`): Dann ist die Grenze Mechanik statt Prompt-Auflage.

---

## Auf eine neue Kit-Version heben

Das T.E.A.M. wird weiterentwickelt. So holst du dir einen neueren Stand — der
Kit-Pfad ist der Ordner, aus dem installiert wurde (typisch
`~/Source/team-kit`):

```bash
# Linux und WSL
git add -A && git commit -m "chore: vor Kit-Update"   # erst committen!
bash <kit-pfad>/install.sh . --update
```

```powershell
# Windows ohne WSL
git add -A; git commit -m "chore: vor Kit-Update"     # erst committen!
pwsh -File <kit-pfad>\install.ps1 . -Update
```

**`--update` fasst nur die Infrastruktur an** — Entrypoints, `team/lib.sh`,
die Werkzeuge, die Rollen-Briefings, die Team-Tests. **Unangetastet bleiben**
deine Projektdaten: `team.config.sh`, `team.config.ps1`, `CLAUDE.md`, `CHANGELOG.md`,
`.budget-ledger`, `.ralph-state` und der ganze Plan-Ordner. Der Lauf listet am
Ende beides auf.

> ⚠ **Nimm niemals `--force`.** Das ist kein Update: Es leert das Ledger
> (Kostenhistorie weg), setzt `.ralph-state` auf 1 zurück (Kaskadenstand weg)
> und ersetzt das Beutebuch durch die leere Vorlage (**alle Funde weg**).
> `--force` ist nur für eine kaputte **Erst**installation gedacht.

**Der Schritt, den nur du machen kannst: die Regeln nachziehen.** Weil
`CLAUDE.md` deine Projektwerte und womöglich eigene Regeln trägt, schreibt der
Updater sie **nicht** um — er meldet nur, dass die Kit-Fassung sich geändert
hat, und legt sie **mit deinen Werten gerendert** zum Vergleich bereit:

```
! CLAUDE.md weicht von der Kit-Fassung ab (412 Zeilen)
    diff -u "/tmp/team-kit-abgleich-…/CLAUDE.md" "…/CLAUDE.md"
```

Diesen Befehl kannst du direkt kopieren. Beim Durchsehen gilt: **deine**
Projekt-Spezifika und eigenen Regeln behalten, geänderte oder neue **Kit-Regeln
übernehmen.** Überspringst du das, läuft die Mechanik der Doku davon — die
Skripte können dann etwas, wovon die Regeln nichts wissen. Genau daran ist im
Feld schon einmal die halbe Kostenerfassung gescheitert.

Was sich zwischen den Versionen geändert hat, steht im `CHANGELOG.md` **des
Kit-Repos** (nicht in deinem — deiner gehört deinem Projekt).

---

## Wenn etwas schiefgeht

| Symptom | Ursache | Abhilfe |
|---|---|---|
| `FEHLER: Kein aktiver Plan gesetzt` | `.ralph-plan` fehlt oder zeigt ins Leere | Zeiger setzen (Schritt 2) |
| `Stufe N liegt über RALPH_CAP` | Kaskade fertig | nächste planen |
| Lauf stoppt mit Exit 1 nach einer Stufe | Budget-Cap gesprengt | Commit prüfen, `echo N+1 > .ralph-state`, mit höherem Deckel fortsetzen |
| Guard meldet Verletzung | Rolle schrieb außerhalb ihrer Pfade — **oder** es lag etwas Uncommittetes herum | oben nachlesen |
| `Kein Fund … nichts zu tun` (Exit 3) | Beutebuch leer | normal |

**Budget-Caps nicht zu tief ansetzen.** Ein zu tiefer Pro-Fall-Cap wirft
bezahlte, plausible Arbeit per Rollback weg und **vervielfacht** die Kosten,
statt zu sparen. Lieber großzügig starten und nachjustieren.

**Der API-Key gehört nicht in dein Shell-Profil — das ist der teuerste stille
Fehler.** Ein exportierter `ANTHROPIC_API_KEY` hat **Vorrang vor dem
Abo-Login** („takes precedence"-Warnung der CLI). Der Lauf funktioniert dann
tadellos — er wird nur komplett über die API abgerechnet statt übers Abo. Im
Feld lief so ein **~13,8-USD-Leerlauf-Lauf** vollständig über API, weil ein
`.bashrc`-Key das Design still aushebelte. Der Key gehört **nie** per `export`
in `.bashrc` & Co., sondern in `~/.config/claude-team/api-key` (eine Zeile,
`chmod 600`) — dorthin legt ihn `team-auth-setup.sh`.

Zwei Tücken dabei: Das Team entfernt den Key im Abo-Modus zwar aktiv aus der
Prozess-Umgebung und warnt einmal pro Lauf auf stderr — aber **bereits offene
Terminals und IDE-Prozesse behalten einen geerbten Key** bis `unset` oder
Neustart (Env-Vererbung).

**Guard-Experimente nur in einem Wegwerf-Repo**, nie hier.

---

*Eingerichtet mit dem T.E.A.M.-Starterkit. Warum das Kit so gebaut ist, steht
in `doku/anhang-a.md` — im **Kit-Repo**, nicht in diesem Projekt.*

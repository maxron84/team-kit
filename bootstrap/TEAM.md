# T.E.A.M. in {{PROJEKTNAME}} — Bedienung

Dieses Projekt wird von einem **Team aus KI-Rollen** vorangetrieben, das du als
*Stakeholder* steuerst. Diese Datei ist für **dich**, den Menschen.
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

## ⚠️ Und danach: währenddessen nichts von Hand schreiben

**Während ein Lauf läuft, gehört Handarbeit nicht in diesen Arbeitsbaum.**
Der Guard merkt sich den Baumzustand beim **Rollenstart**. Was danach
entsteht, gilt für ihn als Werk der Rolle — und wird beim nächsten Rollback
zurückgenommen, **auch wenn du es committet hast**. Muss währenddessen etwas
geschrieben werden (Kit-Meldung, Notiz), dann in einem zweiten Klon, oder
warte den Lauf ab.

Der Abschnitt darüber regelt den Zeitpunkt **davor** und deckt diesen Fall
nicht ab: Ein Commit schützt nur, was **vor** dem Rollenstart lag. Wirksam ist
*vorher*, nicht *sofort*.

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
| **Stakeholder** | Du. Der Mensch, der Richtung, Prioritäten und Freigaben bestimmt. |
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
TEAM_MODEL_LOOP=opus {{RUF}}vollautomatik{{ENDUNG}}     # eine Kaskade auf der starken Stufe
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
Kontostand in `{{RUF}}team-status{{ENDUNG}} --budget` und nicht im Kleingedruckten.

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
TEAM_BUDGET_USD=15 {{RUF}}vollautomatik{{ENDUNG}}
```

Fährt die ganze Kaskade: Ralph baut → Red Team greift an → Frank fixt →
Axel knackt die harten Fälle → Abschlussbericht.

Vorsichtiger, Schritt für Schritt mit Halt bei dir:

```bash
{{RUF}}halbautomatik{{ENDUNG}}          # zeigt den empfohlenen nächsten Schritt
{{RUF}}halbautomatik{{ENDUNG}} ralph    # nur diesen einen Schritt
```

### 4. Closeout — Pflicht, nicht Kür

```bash
{{RUF}}team-status{{ENDUNG}} --rollen-abschluss <N> <domaene> ["<notiz-rollen>"] ["<notiz-bau>"]
{{RUF}}team-status{{ENDUNG}} --architekt-abschluss <USD> <domaene> "Kaskade N geplant"
```

**Woher `<USD>` kommt.** Im Abo gibt es keinen Konsolenwert — gemessen wird aus
dem Sitzungstranskript, nicht geschätzt:

```
{{PYTHON}} team/tools/kosten.py sitzung-messen --projekt .
```

Das Werkzeug eicht sich an den abgerechneten Läufen deines Projekts. Sagt es
„Preistabelle stimmt nicht mehr", ist die Zahl **ungeeicht** — nicht buchen,
sondern die Tabelle nachziehen (Exit `2`). Gemessen wird die **letzte**
Sitzung; liegen mehrere vor, sagt es das und nennt `--alle` (`Kit-BL-186`). Die Zeile `Architekt (Churn-Proxy)`
im Kontostand ist **keine** Messung: Sie rechnet Zeilen-Churn mal Eichfaktor und
misst damit die Größe des Diffs, nicht die Arbeit. Im Feld lag sie 35 % zu
niedrig (`Kit-BL-141`).

Der zweite Befehl bucht als **Abo-Gegenwert** (`auth = abo`) — das ist die
Vorbelegung, weil im Abo kein Geld fließt und die Zeile `real via API
abgerechnet` im Kontostand genau das behaupten würde. Hast du **wirklich** über
einen API-Key gearbeitet, hängst du `--auth api` an. Die Erfolgsmeldung nennt
die Achse, die sie gebucht hat (`… angelegt: 16.3990 USD (abo)`) — lies sie,
statt sie zu überblättern: Im Feld sind so 16,3990 USD in die falsche Spalte
gewandert, und aufgefallen ist es erst beim Nachlesen der Ledger-Zeile
(`Kit-BL-143`).

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

> ### Die Regel für jede interaktive Sitzung
>
> **Jede interaktive Sitzung bucht genau einmal — zweimal zählt doppelt,
> keinmal ist unwiederbringlich verloren** (`Kit-BL-116`, `Kit-BL-165`).
>
> Die beiden Hälften zeigen in **entgegengesetzte** Richtungen, und einzeln
> führt jede in einen Fehler. Wer nur die erste kennt, bucht aus Vorsicht
> seltener — und verliert Sitzungen.
>
> - **Nicht zweimal.** Zwei Closeouts in derselben Sitzung messen **dasselbe**
>   Transkript ein zweites Mal; der erste Betrag wandert erneut ins Ledger.
>   Dafür gibt es `--addieren`/`--ersetzen` oben: Der zweite Aufruf bricht ab
>   und lässt **dich** entscheiden.
> - **Und nicht keinmal.** `sitzung-messen` liest das **zuletzt geänderte**
>   Transkript, also die *laufende* Sitzung — nicht das Projekt als Ganzes.
>   Eine Sitzung, die nicht bucht, wird deshalb **nie** gemessen: Ihr
>   Transkript ist eine eigene Datei, die keine spätere Messung je anfasst.
>   Die Kosten sind nicht „später fällig", sie sind **weg**.
>
> **Der häufigste Fall, und er entsteht aus einem Rat dieses Kits:** Nach
> einem gebuchten Closeout beginnst du für die nächste Kaskade eine **neue**
> Sitzung. Planst du darin K(N+1), bucht diese Sitzung selbst nichts — und
> beim Closeout von K(N+1) wird nur *dessen* Transkript gemessen. Die gesamte
> Planungsarbeit fällt aus dem Ledger.
>
> **Also:** Eine Planungssitzung ohne Closeout bucht ihre Kosten selbst, mit
> `--architekt-abschluss <USD> <domaene> "Kaskade N+1 geplant" --kaskade <N+1>`.

**Was `<domaene>` ist:** der Arbeitsstrang, auf den die Kosten gebucht werden —
bei den meisten Projekten schlicht `produkt`. **Dieses Projekt führt genau eine
Domäne**, solange du in `{{KONFIG}}` nichts anderes einträgst. Mehrere sind
nur sinnvoll, wenn *dieses* Projekt fachlich getrennte Stränge hat (etwa
`backend frontend`). Eine eigene Domäne für die Arbeit am T.E.A.M. brauchst du
**nicht**: Am Team wird hier nicht entwickelt — was dir am Team auffällt, geht
über `{{RUF}}kit-melden{{ENDUNG}}` ins Kit-Repo zurück und wird dort verbucht.

**Wenn nach dem Closeout noch eine Rolle lief** (z. B. ein Frank-Fix), bricht ein
zweiter `--rollen-abschluss` ab, statt die erste Buchung zu überschreiben, und
nennt Alt-, Neu- und Summenwert. Den Nachlauf buchst du mit
`--rollen-abschluss <N> <domaene> "" --addieren` dazu; `--ersetzen` gibt es für
den Fall, dass die alte Zeile schlicht falsch war.

**Prüfen statt glauben:**

```bash
{{RUF}}team-status{{ENDUNG}} --ledger-pruefen
```

Sagt dir, ob für jede Kaskade alles gebucht ist: fehlt eine Zeile je Quelle
(`ralph`/`roles`/`architekt`), liegen unarchivierte Logs herum, obwohl die
Kaskade schon abgeschlossen ist, **liegen Logs herum, die älter sind als die
laufende Kaskade** (dann wurde ein früherer Durchgang gebaut und nie
abgeschlossen — im Feld lagen so 33,89 USD ungebucht in den Logordnern, ohne
dass irgendetwas rot wurde), und — die eigentliche Probe — **ergeben die
archivierten Rohlogs mehr, als im Ledger steht?** Diese letzte Frage stellt die
Gegenkennzahl aus einer **anderen** Quelle als das Ledger selbst. Genau daran
hakte es dreimal: Die schwersten Kostenfehler des Kits (`Kit-BL-1`, `Kit-BL-4`, `Kit-BL-5`)
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

| Bash-Bahn (Linux · WSL) | pwsh-Bahn (Windows ohne WSL) | Wirkung |
|---|---|---|
| `./vollautomatik.sh` | `.\vollautomatik.cmd` | ganze Kaskade automatisch |
| `./halbautomatik.sh [rolle]` | `.\halbautomatik.cmd [rolle]` | ein Schritt, Entscheidung bei dir |
| `./team-status.sh` | `.\team-status.cmd` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --watch` | `.\team-status.cmd --watch` | **dasselbe live**, Refresh alle 5 s · `Strg+C` beendet |
| `./team-status.sh --budget` | `.\team-status.cmd --budget` | Kontostand, API vs. Abo getrennt |
| `./team-test.sh` | `.\team-test.cmd` | Regressionstests der **Team-Infrastruktur** |
| `python3 team/tools/beutebuch.py list` | *(gleich)* | alle Funde mit Status |
| `{{RUF}}kit-melden{{ENDUNG}} neu --titel "…"` | *(gleich, mit `.cmd`)* | Fund **am T.E.A.M. selbst** melden — siehe unten |

> **Das Monitoring ist schon da.** `--watch` zeichnet denselben Block alle 5 s
> neu — Pipeline, Beutebuch, Kaskadenstand, laufende Sperre. Es steht hier,
> weil es zwei Kaskaden lang nur im Kommentarkopf des Skripts stand und ein
> Stakeholder daraufhin fragte, ob ihm ein Update fehle. **Es fehlte nichts,
> es war nur nicht auffindbar** (`Kit-BL-183`).
>
> Was `--watch` **nicht** kann: eine Zeilenspur mitschreiben. Es zeichnet neu,
> hängt nicht an — was einmal durchgelaufen ist, ist weg. Wer den Verlauf
> braucht, liest das Lauf-Log unter `.team-logs/` mit (`tail -f` bzw.
> `Get-Content -Wait`).

**Welche Spalte für dich gilt:** die linke, wenn du unter Linux oder in einer
WSL-Distro arbeitest; die rechte, wenn du Windows **ohne** WSL benutzt. Nicht
das Betriebssystem entscheidet, sondern die Shell — WSL ist Windows und steht
trotzdem links.

**Fehlt eine der beiden Spalten in deinem Projekt?** Wenn hier keine `.cmd`-
und `.ps1`-Dateien liegen (oder umgekehrt keine `.sh`), ist diese Bahn bei der
Installation ausdrücklich **abgewählt** worden (`--nur-bash` / `--nur-pwsh`).
Das ist kein Defekt, und ein `--update` ändert daran nichts: Es **hält** die
Bahn, die hier liegt (`Kit-BL-147`). Zurückholen musst du sie **ausdrücklich**
— das macht das Projekt wieder vollständig, samt der fehlenden Konfiguration:

```bash
bash <kit-pfad>/bash/install.sh . --update --beide-bahnen
```

```powershell
pwsh -File <kit-pfad>\pwsh\install.ps1 . -Update -BeideBahnen
```

Beide Spalten tun dasselbe — es sind zwei Schreibweisen, kein Funktionsunterschied.
Die letzte Zeile steht bewusst als *(gleich)* da: Die Werkzeuge sind Python und
werden auf beiden Wegen identisch aufgerufen.

`{{RUF}}team-test{{ENDUNG}}` prüft **nicht** dein Projekt. Dein Testbefehl ist:
`{{SMOKE_TEST}}`

> **Regel: Der Smoke-Test darf keine Umgebung setzen, die die Doku nicht nennt.**
> Jeder Befehl, den deine Doku einem Menschen nennt, muss in der Verifikation
> buchstabengetreu vorkommen — gleiche Argumente, gleiche Umgebung, kein
> zusätzliches `PYTHONPATH`, kein stilles `cd`. Sonst passiert, was im Feld
> passiert ist: Der dokumentierte Startbefehl war kaputt, der Smoke-Test meldete
> grün, und gefunden hat es niemand aus dem Team — sondern der Mensch, als er
> das Produkt zum ersten Mal selbst startete.

---

## Wenn der Fehler am Team liegt, nicht an deinem Projekt

Manchmal ist der Fehler nicht deiner. Erkennungsmerkmal: Er steckt in `team/`,
in einem Entrypoint hier in der Wurzel oder in einer Regel aus
`CLAUDE.md`/`TEAM.md` — **nicht** in deinem Produktivcode. Dann trifft er jede
weitere Installation, und dieses Projekt repariert ihn bei jedem `--update`
aufs Neue.

```
{{RUF}}kit-melden{{ENDUNG}} neu --titel "Kurz, was schiefging"
```

Das legt einen Entwurf unter `{{PLAN_ORDNER}}/kit-meldungen/` an. Ausfüllen,
dann:

```
{{RUF}}kit-melden{{ENDUNG}} pruefen                # Exit 4 = bitte ansehen
{{RUF}}kit-melden{{ENDUNG}} ablegen <datei>        # Kit liegt daneben — kein gh nötig
{{RUF}}kit-melden{{ENDUNG}} senden <datei>         # Pull Request — fragt vorher
```

**Welchen der beiden Wege du nimmst, hängt davon ab, wem das Kit gehört:**

| Du bist | Weg | Warum |
|---|---|---|
| **fremder Kit-Nutzer** | `senden` — Pull Request | Du hast keine Schreibrechte am Kit; der PR ist dein Weg hinein |
| **Owner des Kits** | `ablegen` **plus** eine `BL-n`-Zeile im Kit-Backlog | Ein PR gegen dein eigenes Repo hieße, deine eigene Meldung zu reviewen und zu mergen. Ohne die Unterscheidung erzeugt jedes deiner Feldprojekte Zweige, PRs und Issues am eigenen Repo — eine Vorgangs-Historie, die keine Vorgänge abbildet (`Kit-BL-187`) |

`senden` erkennt den Owner am GitHub-Konto, bricht ab und nennt den richtigen
Weg — du musst es nicht wissen, bevor du tippst.

**`ablegen` committet, aber pusht nicht** (`Kit-BL-168`). Owner zu sein löst die
Frage der **Zuständigkeit**, nicht die der **Veröffentlichung**: Das Kit-Repo
ist öffentlich, und deine Meldung ist beim Lesen einer privaten Codebasis
entstanden. Der Push ist deine Entscheidung, nach dem Gegenlesen. Eine
`BL-`Nummer steht bewusst nicht in der Datei — die vergibt der Maintainer beim
Triage.

**Drei Dinge, die du wissen solltest:**

- **Deine Meldung wird öffentlich.** `pruefen` sucht deshalb absolute Pfade,
  Konto- und Rechnernamen, Schlüssel — und den **Namen dieses Projekts**. Das
  Kit führt seine Feldbelege unter `Feld A`…`Feld D` statt unter Namen; für den
  Beleg zählt die *Lage* eines Projekts (Plattform, Bahn, Greenfield oder
  Bestand), nicht sein Name. `senden` geht über Befunde nur hinweg, wenn du es
  ausdrücklich sagst.
- **Senden ist deine Entscheidung, nicht die einer Rolle.** Der Architekt und
  Frank dürfen eine Meldung *schreiben* — das steht in ihren Briefings. Senden
  darf nur ein Mensch: Ein Pull Request wirkt nach außen und lässt sich nicht
  zurückholen.
- **Kein `gh` installiert?** Dann gibt `senden` einen vorbefüllten Issue-Link
  aus; ein Browser und ein GitHub-Konto genügen. Die Meldung bleibt in jedem
  Fall als Datei liegen.

**Trag den Fund außerdem in `{{PLAN_ORDNER}}/backlog.md` ein** und setz den
Status auf „ans Kit gemeldet (…)". Sonst weiß niemand, ob der Rückkanal wirklich
bedient wurde — und ein lokaler Fix hat eine Verfallszeit: Er endet beim
nächsten `--update`.

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
{{KONFIG}}          ALLE Projektwerte — der einzige Ort zum Ändern
CLAUDE.md               Regeln für die KI-Rollen (geltendes Recht)
{{PLAN_ORDNER}}/        Kaskaden-Pläne, Beutebuch, Ermittlungsakten, Roadmap
team/                   Team-Infrastruktur (lib, tools, prompts, tests)
.budget-ledger          Kostenbasis — committet, nicht ignorieren
.ralph-plan             Zeiger auf den aktiven Plan
.ralph-state            nächste zu bauende Stufe
```

**Einen Wert ändern?** Immer in `{{KONFIG}}`. Er wirkt sofort in allen
Rollen, ohne Neuinstallation.

### Zog das Team in eine gewachsene Codebasis ein?

Zwei Werte in `{{KONFIG}}` tragen dann Gewicht, die im neuen Projekt leer
bleiben dürfen:

| Wert | Wozu |
|---|---|
| `TEAM_WEITERER_CODE` | Code außerhalb von `{{PRODUKTIVCODE}}`, der mitgeprüft werden soll: Einstiegspunkt in der Wurzel, Build-/Deploy-Skripte. Was hier nicht steht, greift das Red Team **nie** an — und ein sauberer Sweep sieht trotzdem aus wie ein sauberes Projekt (`Kit-BL-52`). |
| `TEAM_TEST_ORDNER_BESTAND` / `TEAM_PLAN_ORDNER_BESTAND` | Was beim Einzug schon in den beiden Schreibordnern lag. Der Guard schlägt dort **nicht** an — Harry, Marv und Axel dürfen dort schreiben und löschen. Die Einträge werden den Rollen im Prompt als fremdes Eigentum genannt: neue Dateien anlegen ja, Bestehendes anfassen nein (`Kit-BL-51`). |

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
bash <kit-pfad>/bash/install.sh . --update
```

```powershell
# Windows ohne WSL
git add -A; git commit -m "chore: vor Kit-Update"     # erst committen!
pwsh -File <kit-pfad>\pwsh\install.ps1 . -Update
```

**`--update` fasst nur die Infrastruktur an** — Entrypoints, `{{LIB}}`,
die Werkzeuge, die Rollen-Briefings, die Team-Tests. **Die Bahn wechselt es
nicht**: Was einbahnig ist, bleibt einbahnig (`Kit-BL-147`). **Unangetastet
bleiben**
deine Projektdaten: deine Konfiguration (`team.config.*` — je Bahn eine),
`CLAUDE.md`, `CHANGELOG.md`,
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
`chmod 600`).

**Wie er dorthin kommt — der Handweg zuerst, weil er immer geht** (drei
Zeilen, keine Voraussetzung):

```
install -m 600 -D /dev/null ~/.config/claude-team/api-key
read -rs -p "API-Key: " k && printf '%s\n' "$k" > ~/.config/claude-team/api-key
unset k
```

Auf der pwsh-Bahn liegt die Datei unter `%APPDATA%\claude-team\api-key`;
`Read-Host -AsSecureString` und `Set-Content` tun dasselbe.

Es gibt dafür auch ein Skript, aber **der Installer legt es nicht ins
Projekt** — es ist ausdrücklich ein Beispiel und keine Kit-Mechanik. Wer das
Kit-Repo lokal liegen hat (der Pfad steht in `team.config.*` als
`TEAM_KIT_PFAD`), findet es unter `<kit>/bash/scripts/team-auth-setup.sh`
bzw. `<kit>/pwsh/scripts/team-auth-setup.ps1`.

> **Warum das hier so ausführlich steht** (`Kit-BL-164`): Diese Zeile nannte
> lange nur den Skriptnamen — ein Skript, das es im Projekt nicht gibt und
> dessen Fundort nirgends stand. Wer den Key hinterlegen will und das Werkzeug
> nicht findet, greift mit einiger Wahrscheinlichkeit zu genau dem `export`,
> vor dem der Absatz zwei Zeilen darüber warnt. **Ein Dokument, das ein
> Werkzeug nennt, das der Leser nicht hat, muss den Weg ohne dieses Werkzeug
> zeigen.**

Zwei Tücken dabei: Das Team entfernt den Key im Abo-Modus zwar aktiv aus der
Prozess-Umgebung und warnt einmal pro Lauf auf stderr — aber **bereits offene
Terminals und IDE-Prozesse behalten einen geerbten Key** bis `unset` oder
Neustart (Env-Vererbung).

**Guard-Experimente nur in einem Wegwerf-Repo**, nie hier.

---

*Eingerichtet mit dem T.E.A.M.-Starterkit. Warum das Kit so gebaut ist, steht
in `doku/anhang-a.md` — im **Kit-Repo**, nicht in diesem Projekt.*

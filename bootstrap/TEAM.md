# T.E.A.M. in {{PROJEKTNAME}} — Bedienung

Dieses Projekt wird von einem **Team aus KI-Rollen** vorangetrieben, das du als
*Strippenzieher* steuerst. Diese Datei ist für **dich**, den Menschen.
Die Regeln für die KI-Rollen stehen in [`CLAUDE.md`](CLAUDE.md).

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
./team-status.sh --rollen-abschluss <N> <domaene>
./team-status.sh --architekt-abschluss <USD> <domaene> "Kaskade N geplant"
```

Der erste Befehl schließt **beide** Kostenquellen des Laufs ab und schreibt
dafür **zwei** Ledger-Zeilen: `roles` für Harry/Marv/Frank/Axel und `ralph`
für die Baukosten. Die Rohlogs werden dabei archiviert, damit der Kontostand
sie nicht ein zweites Mal zählt. Deine Notiz landet in **beiden** Zeilen, jede
mit ihrem eigenen Vorspann (`Rollen: …` bzw. `Bau: …`) — so sagt jede Zeile aus
sich heraus, welche Kosten sie trägt, auch wenn dein Text nur zur anderen passt.

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
Kaskade schon abgeschlossen ist, und — die eigentliche Probe — **ergeben die
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

Der Architekt schreibt außerdem ein `{{PLAN_ORDNER}}/kaskade-N-abschluss.md`.
Der Terminal-Abschlussbericht ist flüchtig; das Protokoll bleibt im Git.

---

## Befehle im Überblick

| Befehl | Wirkung |
|---|---|
| `./vollautomatik.sh` | ganze Kaskade automatisch |
| `./halbautomatik.sh [rolle]` | ein Schritt, Entscheidung bei dir |
| `./team-status.sh` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --budget` | Kontostand, API vs. Abo getrennt |
| `./team-test.sh` | Regressionstests der **Team-Infrastruktur** |
| `python3 team/tools/beutebuch.py list` | alle Funde mit Status |

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

**Guard-Experimente nur in einem Wegwerf-Repo**, nie hier.

---

*Eingerichtet mit dem T.E.A.M.-Starterkit. Bau-Anleitung und Betriebslehren:
`doku/anhang-a.md` im Kit-Repo.*

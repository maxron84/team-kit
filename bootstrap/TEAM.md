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
sie nicht ein zweites Mal zählt.

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

---

## Exit-Codes — was sie bedeuten

| Code | Bedeutung | Was tun |
|---|---|---|
| `0` | durchgelaufen | Closeout machen |
| `1` | **echter Fehler** | Log lesen, Ursache beheben |
| `3` | nichts zu tun | normal, kein Fehler |
| `42` | **Session-Limit** — Lauf pausiert | **kein Fehler.** Kein Datenverlust, State steht. Später erneut starten. |

`42` ist die häufigste Verwechslung: Das ist kein Absturz, sondern eine saubere
Pause. Nichts ist verloren, der Lauf setzt beim nächsten Start fort.

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

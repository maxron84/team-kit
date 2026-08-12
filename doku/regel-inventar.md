# Regel-Inventar — `bootstrap/CLAUDE.md.vorlage`

Der **Sicherheitsgurt** aus [Anhang A.10](anhang-a.md) für den Umbau der
Regeldatei (`BL-56`). Jede tragende Aussage der Vorlage ist hier klassifiziert:

| Klasse | Bedeutung | darf ins Wiki wandern? |
|---|---|---|
| **NORM** | geltendes Recht — die Regel selbst | **nein** |
| **HERLEITUNG** | warum die Regel so lautet (Feld-Beleg) | ja, mit Vorbehalt* |
| **HISTORIE** | wann/von wem gebaut, was vorher galt | ja |

\* **Vorbehalt:** Zwei Belege sind **testgeschützt** und dürfen die Regeldatei
nicht verlassen — [`test_bl49`](../team/tests/test_bl49_regler_gegenprobe.py)
verlangt „das Verstellen"/„sieben", [`test_bl17`](../team/tests/test_bl17_doku_gegen_verifikation.py)
verlangt „PYTHONPATH". Begründung beider Docstrings: *Eine Regel ohne ihren
Beleg wird als Büroaufwand gelesen und nicht angewandt.* Sie sind unten als
HERLEITUNG geführt, aber mit `⚓` markiert.

**Wozu das gut ist:** Der Gurt verbietet keine Änderung — er macht sie
**sichtbar**. Wer eine Regel umformuliert oder streicht, bekommt in
[`kit-regelinventar.py`](../kit-regelinventar.py) rot und muss die betroffene
Zeile hier **benannt** nachziehen. Im Feld hat genau das gehalten, als `BL-55`
eine Regel bewusst umkehrte.

**Die Spalte „Träger"** nennt die Datei, die eine Aussage **ausliefert**.
Die Spalte „Abschnitt" bleibt daneben die **Sachgruppe** — sie sagt, worum es
geht, nicht wo es steht. Beim Dreischnitt (`BL-56`) wandern Regeln aus der
Regeldatei in die Rollen-Briefings; ohne diese Spalte ginge jede verschobene
Regel rot, und der Gurt würde den Umbau **blockieren**, statt ihn sichtbar zu
machen. Erlaubte Träger: `Regeldatei`, `TEAM.md`, `rolle-architekt`,
`rolle-ralph`, `rolle-harry`, `rolle-marv`, `rolle-frank`, `rolle-axel`.

**Geprüft wird zweierlei** (Stufe 7 in `kit-test.sh`):
1. Jedes **NORM**-Zitat kommt wörtlich in **seinem Träger** vor.
2. Jeder Abschnitt der Regeldatei ist hier vertreten — und kein Abschnitt hier,
   den es nicht mehr gibt.

**Abdeckung:** Vollständig für **NORM** — jede geltende Regel ist erfasst. Für
HERLEITUNG/HISTORIE sind die Blöcke erfasst, die beim Umbau zur Disposition
stehen; erschöpfend ist diese Spalte bewusst nicht.

---

| Abschnitt | Klasse | Träger | Zitat |
|---|---|---|
| Projekt-Spezifika | NORM | Regeldatei | Muss als erster Abschnitt stehen |
| Projekt-Spezifika | NORM | Regeldatei | Jeder Befehl, den die Doku einem Menschen nennt, muss in der Verifikation **buchstabengetreu** vorkommen |
| Projekt-Spezifika | NORM | Regeldatei | Der Smoke-Test darf keine Umgebung setzen, die die Doku nicht nennt |
| Projekt-Spezifika | HERLEITUNG | Regeldatei | ⚓ er setzte still ein `PYTHONPATH`, das der Anwender nie hat |
| Projekt-Spezifika | HERLEITUNG | Regeldatei | Wer eine Krücke in die Verifikation einbaut, damit sie grün wird, hat die Verifikation abgeschafft |
| Das Team (Rollen) | NORM | Regeldatei | Jede Instanz sollte wissen, **welche Rolle sie gerade ausfüllt** |
| Das Team (Rollen) | NORM | Regeldatei | Nimmt **keine** Features aus späteren Stufen vorweg. |
| Das Team (Rollen) | NORM | Regeldatei | Spec ist Wahrheit vor Annahmen. |
| Das Team (Rollen) | NORM | Regeldatei | **Rührt keinen Produktivcode an.** |
| Das Team (Rollen) | NORM | Regeldatei | Out-of-Loop-Fixes sind **Franks** Aufgabe. |
| Das Team (Rollen) | NORM | Regeldatei | Der Architekt greift **nur im Ausnahmefall** selbst zum Produktivcode |
| Das Team (Rollen) | NORM | Regeldatei | jede Rolle einen sauber definierten Übergabepunkt |
| Franks Dreisatz — Out-of-Loop-Fixes  ✅ erprobt | NORM | Regeldatei | **Code-Fix committen** mit klarem Präfix |
| Franks Dreisatz — Out-of-Loop-Fixes  ✅ erprobt | NORM | Regeldatei | Dieser Block ist die **Single Source of Truth** für alle Out-of-Loop-Fixes. |
| Franks Dreisatz — Out-of-Loop-Fixes  ✅ erprobt | NORM | Regeldatei | Ralph liest den `[Unreleased]`-Block vor jeder Stufe und baut ein dort gelistetes Problem **nicht erneut**. |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | Regeldatei | **Kein Produktivcode.** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | Regeldatei | Ein Fund wird sauber dokumentiert und **an Frank übergeben** (Finder ≠ Fixer). |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | Regeldatei | **Der Prüfumfang ist nicht automatisch ein einzelner Ordner** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | Regeldatei | **neue Dateien anlegen ja, Bestehendes ändern oder löschen nein** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | Regeldatei | **Pflicht: `Reproducer-Test`-Zeile setzen**, mit dem Pfad **in Backticks** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | Regeldatei | **Reproducer-Tests nach der Fund-Nummer benennen** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | HERLEITUNG | Regeldatei | eine **neue** Testdatei ist nie vorab referenziert, ihr regelkonformer Fix würde also stillschweigend zurückgerollt |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | Regeldatei | **Axel denkt, Frank tippt.** |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | Regeldatei | **Nie im Dauer-Loop** (ein Fall pro Aufruf). |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | Regeldatei | **Modell:** **immer stark** |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | Regeldatei | **Auth:** **Abo-first mit aufruf-lokalem API-Fallback** |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | Regeldatei | **Ermittlungsakte** in |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | Regeldatei | Nur wenn **selbst Axel** nicht weiterkommt: `an Mensch eskaliert`. |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | **1. Skizze zuerst.** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | Nur die **jeweils nächste** Kaskade wird so ausgehärtet; alles Fernere bleibt Skizze. |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | **3. Nummerierung erst bei der Aushärtung.** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | **4. Scharfschalt-Sequenz ist Pflicht-Ausgabe** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | Der Architekt **gibt die Sequenz nur aus** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | **5. Abschluss-Doc ist Pflicht pro gebauter Kaskade** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | rolle-architekt | Textvolumen-gebundene Prosa-Arbeit (Doku umbauen, verdichten, umziehen) plane ich als **eigene Handarbeit** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | Wert probeweise auf **zwei fremde Werte** (höher/niedriger), Suite laufen lassen, danach **nachweislich zurücksetzen** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Regeldatei | wird sie als `Kit-BL-<N>` geschrieben, nie als blankes `BL-<N>` |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | HERLEITUNG | Regeldatei | ⚓ Im Feld fand `grep` **fünf** Stellen, das Verstellen **sieben** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | HERLEITUNG | anhang-a | Prosa-Stufen **3,23 / 3,97 / 4,68 USD** gegenüber **2,16 / 2,35 USD** für Code-Stufen |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | HERLEITUNG | Regeldatei | Im Feld stand eine Skizze drei Kaskaden lang auf einer Prämisse, die der zitierte Eintrag selbst widerlegte |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Regeldatei | Diese `CLAUDE.md` ist **geltendes Recht**, kein Bautagebuch. |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Regeldatei | Geltende Regel → hierher. Herleitung/Historie → Wiki oder Historien-Doc, **wörtlich verschoben**, nie ersatzlos gestrichen. |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Regeldatei | **Rollen-Briefings statt Volltext.** |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Regeldatei | **Fund-/Aufgabenlisten archivieren**, sobald sie überwiegend abgeschlossen sind |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Regeldatei | **Leitplanke: kürzt Text, nie Geltung.** |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Regeldatei | dafür braucht es einen eigenen, benannten Entscheid |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | HERLEITUNG | Regeldatei | kommt pro Rollenaufruf ein **zweiter Voll-Read** obendrauf (bei ~20–30 Aufrufen je Kaskade) |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | **Permission-Mode:** `bypassPermissions` |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | **Zustand:** [`.ralph-state`](.ralph-state) = nächste auszuführende Stufe. |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | Der Key gehört **nie** per `export` in `.bashrc` & Co. |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | sie weicht Guard/Read-Only-Regeln **nicht** auf |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | reichen 42 **unverändert als eigenen Exit 42** durch |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | Der Read-Only-Guard läuft dabei auf **jedem** Pfad (auch Pause) |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | Der Smoke-Test läuft im **Vordergrund**, nie als Hintergrund-Task und nie mit einem Wakeup darauf. |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | **Kein** Aufweichen echter Fehler — die Bremse misst ausschließlich Fortschritt. |
| Loop-Mechanik & Auth (Ralph) | NORM | Regeldatei | **Die Arbeit ist in diesem Fall meistens fertig** |
| Loop-Mechanik & Auth (Ralph) | HERLEITUNG | Regeldatei | ein ~13,8-USD-Leerlauf-Lauf lief komplett über API statt Abo-first |
| Kostenkontrolle | NORM | Regeldatei | **Modell** und **Auth** sind zwei getrennte Achsen |
| Kostenkontrolle | NORM | Regeldatei | ein überschrittener **Soft-Cap** ist nur ein **Hinweis** |
| Kostenkontrolle | NORM | Regeldatei | Das starke/teure Modell (Axel, Architekt) läuft **nie im Dauer-Loop** |
| Kostenkontrolle | NORM | Regeldatei | Nur aktivieren, wenn das Budget es erzwingt, und Axel möglichst **ausnehmen**. |
| Kostenkontrolle | NORM | rolle-architekt | Das Tool **ersetzt** (statt verdoppelt) eine vorhandene Zeile **derselben Rolle + Kaskade** |
| Kostenkontrolle | NORM | rolle-architekt | **nie** stillschweigend als abgerechneter Betrag ausgegeben |
| Kostenkontrolle | NORM | Regeldatei | beides **nach** dem Lauf im Architekten-Closeout, **nie** in einer Loop-Stufe |
| Kostenkontrolle | NORM | rolle-architekt | **maschinelle Wahrheit ist die committete `.budget-ledger` plus das Kontostand-Werkzeug** |
| Kostenkontrolle | HERLEITUNG | Regeldatei | Der zu tiefe Cap „sparte" nichts, sondern **vervielfachte** die Kosten. |
| Kostenkontrolle | HERLEITUNG | anhang-a | eine **einzelne** Architekten-Session kostete laut Konsole **~16 USD** |
| Kostenkontrolle | HERLEITUNG | anhang-a | ein Gate, das man regelmäßig umgeht, ist wirkungslos |
| Kostenkontrolle | NORM | rolle-architekt | **eine** Domäne ist der Normalfall |
| Kostenkontrolle | HISTORIE | anhang-a | Die frühere feste Trennung `produkt` ↔ `team` stammt aus dem **Ursprungsprojekt** |
| Anhang A — Loop-Infrastruktur | NORM | Regeldatei | **Der `team/`-Ordner gehört der Infrastruktur, nicht dem Projekt.** |
| Anhang A — Loop-Infrastruktur | NORM | Regeldatei | **Team-Tests laufen getrennt** |
| Anhang A — Loop-Infrastruktur | NORM | Regeldatei | Diese Datei bleibt **Regelquelle** |

---

## Verwandte Seiten

- [Anhang A.10](anhang-a.md) — Doku-Konsolidierung, die Lehre hinter diesem Inventar
- [`kit-regelinventar.py`](../kit-regelinventar.py) — der Prüfer
- `plans/backlog.md`, `BL-56` — der Entscheid, für den dieses Inventar die Vorbedingung ist

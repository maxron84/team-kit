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

**Geprüft wird zweierlei** (Stufe 7 in `kit-test.sh`):
1. Jedes **NORM**-Zitat kommt wörtlich in der Regeldatei vor.
2. Jeder Abschnitt der Regeldatei ist hier vertreten — und kein Abschnitt hier,
   den es nicht mehr gibt.

**Abdeckung:** Vollständig für **NORM** — jede geltende Regel ist erfasst. Für
HERLEITUNG/HISTORIE sind die Blöcke erfasst, die beim Umbau zur Disposition
stehen; erschöpfend ist diese Spalte bewusst nicht.

---

| Abschnitt | Klasse | Zitat |
|---|---|---|
| Projekt-Spezifika | NORM | Muss als erster Abschnitt stehen |
| Projekt-Spezifika | NORM | Jeder Befehl, den die Doku einem Menschen nennt, muss in der Verifikation **buchstabengetreu** vorkommen |
| Projekt-Spezifika | NORM | Der Smoke-Test darf keine Umgebung setzen, die die Doku nicht nennt |
| Projekt-Spezifika | HERLEITUNG | ⚓ er setzte still ein `PYTHONPATH`, das der Anwender nie hat |
| Projekt-Spezifika | HERLEITUNG | Wer eine Krücke in die Verifikation einbaut, damit sie grün wird, hat die Verifikation abgeschafft |
| Das Team (Rollen) | NORM | Jede Instanz sollte wissen, **welche Rolle sie gerade ausfüllt** |
| Das Team (Rollen) | NORM | Nimmt **keine** Features aus späteren Stufen vorweg. |
| Das Team (Rollen) | NORM | Spec ist Wahrheit vor Annahmen. |
| Das Team (Rollen) | NORM | **Rührt keinen Produktivcode an.** |
| Das Team (Rollen) | NORM | Out-of-Loop-Fixes sind **Franks** Aufgabe. |
| Das Team (Rollen) | NORM | Der Architekt greift **nur im Ausnahmefall** selbst zum Produktivcode |
| Das Team (Rollen) | NORM | jede Rolle einen sauber definierten Übergabepunkt |
| Franks Dreisatz — Out-of-Loop-Fixes  ✅ erprobt | NORM | **Code-Fix committen** mit klarem Präfix |
| Franks Dreisatz — Out-of-Loop-Fixes  ✅ erprobt | NORM | Dieser Block ist die **Single Source of Truth** für alle Out-of-Loop-Fixes. |
| Franks Dreisatz — Out-of-Loop-Fixes  ✅ erprobt | NORM | Ralph liest den `[Unreleased]`-Block vor jeder Stufe und baut ein dort gelistetes Problem **nicht erneut**. |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | **Kein Produktivcode.** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | Ein Fund wird sauber dokumentiert und **an Frank übergeben** (Finder ≠ Fixer). |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | **Der Prüfumfang ist nicht automatisch ein einzelner Ordner** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | **neue Dateien anlegen ja, Bestehendes ändern oder löschen nein** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | **Pflicht: `Reproducer-Test`-Zeile setzen**, mit dem Pfad **in Backticks** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | NORM | **Reproducer-Tests nach der Fund-Nummer benennen** |
| Harry & Marv — Read-Only Red Team  ✅ erprobt (manuell **und** automatisiert) | HERLEITUNG | eine **neue** Testdatei ist nie vorab referenziert, ihr regelkonformer Fix würde also stillschweigend zurückgerollt |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | **Axel denkt, Frank tippt.** |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | **Nie im Dauer-Loop** (ein Fall pro Aufruf). |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | **Modell:** **immer stark** |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | **Auth:** **Abo-first mit aufruf-lokalem API-Fallback** |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | **Ermittlungsakte** in |
| Axel — Read-Only Forensiker  ✅ erprobt (manuell) | NORM | Nur wenn **selbst Axel** nicht weiterkommt: `an Mensch eskaliert`. |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | **1. Skizze zuerst.** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Nur die **jeweils nächste** Kaskade wird so ausgehärtet; alles Fernere bleibt Skizze. |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | **3. Nummerierung erst bei der Aushärtung.** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | **4. Scharfschalt-Sequenz ist Pflicht-Ausgabe** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Der Architekt **gibt die Sequenz nur aus** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | **5. Abschluss-Doc ist Pflicht pro gebauter Kaskade** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | **Textvolumen-gebundene Prosa-Arbeit** (Doku umbauen, verdichten, umziehen) plant der Architekt als **eigene Handarbeit** ein |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | Wert probeweise auf **zwei fremde Werte** (höher/niedriger), Suite laufen lassen, danach **nachweislich zurücksetzen** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | NORM | wird sie als `Kit-BL-<N>` geschrieben, nie als blankes `BL-<N>` |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | HERLEITUNG | ⚓ Im Feld fand `grep` **fünf** Stellen, das Verstellen **sieben** |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | HERLEITUNG | Im Feld kosteten Prosa-Stufen **3,23 / 3,97 / 4,68 USD** gegenüber **2,16 / 2,35 USD** für Code-Stufen |
| Kaskaden-Planungsregeln (verbindlich für den Architekten)  ✅ erprobt | HERLEITUNG | Im Feld stand eine Skizze drei Kaskaden lang auf einer Prämisse, die der zitierte Eintrag selbst widerlegte |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Diese `CLAUDE.md` ist **geltendes Recht**, kein Bautagebuch. |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | Geltende Regel → hierher. Herleitung/Historie → Wiki oder Historien-Doc, **wörtlich verschoben**, nie ersatzlos gestrichen. |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | **Rollen-Briefings statt Volltext.** |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | **Fund-/Aufgabenlisten archivieren**, sobald sie überwiegend abgeschlossen sind |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | **Leitplanke: kürzt Text, nie Geltung.** |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | NORM | dafür braucht es einen eigenen, benannten Entscheid |
| Doku-Hygiene — die Regeldatei bleibt Regelquelle  ✅ erprobt | HERLEITUNG | kommt pro Rollenaufruf ein **zweiter Voll-Read** obendrauf (bei ~20–30 Aufrufen je Kaskade) |
| Loop-Mechanik & Auth (Ralph) | NORM | **Permission-Mode:** `bypassPermissions` |
| Loop-Mechanik & Auth (Ralph) | NORM | **Zustand:** [`.ralph-state`](.ralph-state) = nächste auszuführende Stufe. |
| Loop-Mechanik & Auth (Ralph) | NORM | Der Key gehört **nie** per `export` in `.bashrc` & Co. |
| Loop-Mechanik & Auth (Ralph) | NORM | sie weicht Guard/Read-Only-Regeln **nicht** auf |
| Loop-Mechanik & Auth (Ralph) | NORM | reichen 42 **unverändert als eigenen Exit 42** durch |
| Loop-Mechanik & Auth (Ralph) | NORM | Der Read-Only-Guard läuft dabei auf **jedem** Pfad (auch Pause) |
| Loop-Mechanik & Auth (Ralph) | NORM | Der Smoke-Test läuft im **Vordergrund**, nie als Hintergrund-Task und nie mit einem Wakeup darauf. |
| Loop-Mechanik & Auth (Ralph) | NORM | **Kein** Aufweichen echter Fehler — die Bremse misst ausschließlich Fortschritt. |
| Loop-Mechanik & Auth (Ralph) | NORM | **Die Arbeit ist in diesem Fall meistens fertig** |
| Loop-Mechanik & Auth (Ralph) | HERLEITUNG | ein ~13,8-USD-Leerlauf-Lauf lief komplett über API statt Abo-first |
| Kostenkontrolle | NORM | **Modell** und **Auth** sind zwei getrennte Achsen |
| Kostenkontrolle | NORM | ein überschrittener **Soft-Cap** ist nur ein **Hinweis** |
| Kostenkontrolle | NORM | Das starke/teure Modell (Axel, Architekt) läuft **nie im Dauer-Loop** |
| Kostenkontrolle | NORM | Nur aktivieren, wenn das Budget es erzwingt, und Axel möglichst **ausnehmen**. |
| Kostenkontrolle | NORM | Das Tool **ersetzt** (statt verdoppelt) eine vorhandene Zeile **derselben Rolle + Kaskade** |
| Kostenkontrolle | NORM | **nie** stillschweigend als abgerechneter Betrag ausgegeben |
| Kostenkontrolle | NORM | beides **nach** dem Lauf im Architekten-Closeout, **nie** in einer Loop-Stufe |
| Kostenkontrolle | NORM | maschinelle Wahrheit ist die committete .budget-ledger plus das Kontostand-Werkzeug |
| Kostenkontrolle | HERLEITUNG | Der zu tiefe Cap „sparte" nichts, sondern **vervielfachte** die Kosten. |
| Kostenkontrolle | HERLEITUNG | eine einzelne Architekten-Session kostete laut Konsole **~16 USD** — strukturell unerfasst |
| Kostenkontrolle | HERLEITUNG | ein Gate, das man regelmäßig umgeht, wirkungslos ist |
| Kostenkontrolle | HISTORIE | Die frühere feste Trennung `produkt` ↔ `team` stammt aus dem Ursprungsprojekt |
| Anhang A — Loop-Infrastruktur | NORM | **Der `team/`-Ordner gehört der Infrastruktur, nicht dem Projekt.** |
| Anhang A — Loop-Infrastruktur | NORM | **Team-Tests laufen getrennt** |
| Anhang A — Loop-Infrastruktur | NORM | Diese Datei bleibt **Regelquelle** |

---

## Verwandte Seiten

- [Anhang A.10](anhang-a.md) — Doku-Konsolidierung, die Lehre hinter diesem Inventar
- [`kit-regelinventar.py`](../kit-regelinventar.py) — der Prüfer
- `plans/backlog.md`, `BL-56` — der Entscheid, für den dieses Inventar die Vorbedingung ist

# Roadmap-Skizzen — T.E.A.M.-Starterkit

Ungehärtete Stränge für die Weiterentwicklung **des Kits selbst**. Ziel, grober
Umfang, Bezug, offene Fragen — **ohne** Stufennummern, **ohne** Cap
(Kaskaden-Planungsregel 1).

> **Nicht verwechseln:** `bootstrap/roadmap-skizzen.md` ist die **Vorlage**, die
> der Installer in Zielprojekte kopiert. Diese Datei hier ist die Roadmap des
> Kits. `install.sh` liest ausschließlich aus `bootstrap/` — dieser Ordner
> landet in keiner Installation.

**Quelle der meisten Stränge:** das Feldprojekt
`~/Source/team-kit_project_platformer`, Kaskade 1 (2026-08-01). Dort ist das Kit
zum ersten Mal scharf über eine volle Kaskade gelaufen, und genau dort fielen die
Fehler auf, die kein Kit-Test finden konnte.

---

## ~~Skizze A: Das Kit kann sich selbst nicht prüfen~~ — gebaut 2026-08-01

Als `kit-test.sh` umgesetzt (Architekt-Ausnahme, Backlog `BL-6`). Der Strang
lief **nicht** über eine Kaskade: Es war ein Skript und ein Gegenbeweis, keine
mehrstufige Arbeit.

**Was entschieden wurde:** „Installieren und dort prüfen" statt
layout-agnostischer Tests — das prüft den Installer gleich mit und lässt die
149 Tests dort laufen, wo sie gelten. Die 17 Fehlschläge von
`pytest team/tests` **im Kit-Repo** bleiben bestehen und sind **erwartet**.

**Offen geblieben:** Ob der Lauf zusätzlich in einen Git-Hook gehört, oder ob
die Regel „vor jedem Release" reicht. Bisher reicht sie — es gibt genau einen
Menschen im Prozess.

---

## ~~Skizze B: Die Kostenerfassung ist strukturell unvollständig~~ — gebaut 2026-08-01

`BL-4` und `BL-5` behoben (Architekt-Ausnahme nach Franks Dreisatz), je mit
Regressionstest und gefahrener Gegenprobe.

**Die beiden Entscheide, die offen waren:**

1. **`BL-4`** — *eigener Verb oder Erweiterung?* Beides: `kosten.py
   ralph-abschluss` als eigener Verb mit eigener `ralph`-Ledgerzeile, aber
   `./team-status.sh --rollen-abschluss` ruft beide Verben. **Eine**
   Bedienhandlung, **zwei** Zeilen. Eine Sammelzeile hätte die Trennung
   Bau ↔ Sweep/Fix gekostet — und genau an dieser Kennzahl fiel im Feld
   überhaupt auf, dass Ralph fehlte.
2. **`BL-5`** — *addieren, abbrechen oder erkennen?* Abbrechen als Default,
   `--addieren` und `--ersetzen` als ausdrückliche Wege. Begründung: Der Wert
   entsteht aus **disjunkten** Log-Mengen (jeder Abschluss archiviert, was er
   zählte), dafür ist Addieren die richtige Verknüpfung. Automatisch addiert
   wird trotzdem nicht — **ohne** `--archivieren` zählen zwei Aufrufe dieselben
   Logs, dann wäre Addieren eine Doppelbuchung. Die Unterscheidung gehört dem
   Menschen, nicht einer Heuristik.

**Offen geblieben:** Ein Ledger-Konsistenzcheck (`--ledger-pruefen`), der
Lücken meldet, statt sie erst im nächsten Closeout auffallen zu lassen. Wäre
das Werkzeug gewesen, das `BL-4` gefunden hätte, statt eines aufmerksamen
Menschen beim Abgleich zweier Dokumente. **Nächster Kandidat für eine echte
Kaskade** — siehe Skizze D.

---

## ~~Skizze C: Der Rückkanal Feld → Kit ist Handarbeit~~ — geregelt 2026-08-01

Bewusst **als Konvention, nicht als Werkzeug** gelöst: Das Kit hat jetzt ein
eigenes `plans/backlog.md`, und drei Stellen sagen, wohin ein Kit-Fund gehört —
die Backlog-Vorlage `bootstrap/backlog.md`, das Architekten-Briefing und der
Statuswert „ans Kit gemeldet".

**Warum kein Werkzeug:** Bei einem Menschen und zwei Repos wäre jede
Automatisierung teurer als das Problem. Das ändert sich ab dem dritten
Feldprojekt — dann neu bewerten.

---

## Skizze D: Das Ledger prüft seine eigene Vollständigkeit nicht

- **Ziel**: Ein Befehl sagt, ob für eine abgeschlossene Kaskade **alles**
  gebucht ist — statt dass es beim Lesen zweier Dokumente auffällt.
- **Stand**: Es gibt nichts dergleichen. `BL-4` (Ralph fehlte komplett) und
  `BL-5` (Altwert überschrieben) sind **beide** nicht durch ein Werkzeug
  aufgefallen, sondern dadurch, dass jemand den gedruckten Bericht gegen das
  Ledger hielt. `BL-1` genauso. Das ist dreimal dasselbe Muster: **Ein Bericht,
  der seine Kennzahl aus derselben Quelle zieht, bestätigt einen Fehler, statt
  ihn zu zeigen.**
- **Umfang**: Ein `--ledger-pruefen`, das je Kaskade prüft, was da sein müsste:
  Liegt für jede Kaskade mit archivierten Logs auch eine Zeile je Quelle vor
  (`ralph`, `roles`, `architekt`)? Steht in einem Log-Ordner etwas
  Unarchiviertes, obwohl die Kaskade als abgeschlossen gilt? Ist eine Zeile
  auffällig kleiner als die Summe ihrer archivierten Rohlogs?
- **Bezug**: Die Kostenmechanik ist die einzige Stelle im Kit, deren Fehler
  **still** sind — Code-Fehler zeigt der Smoke-Test, Kostenfehler zeigt
  niemand. Alle drei bisherigen Kit-Fehler waren von dieser Art.
- **Offene Fragen**:
  - Woher weiß das Werkzeug, dass eine Kaskade „abgeschlossen" ist? Aus dem
    Archiv-Ordner, aus `.ralph-state`, oder aus einer Abschlusszeile?
  - Warnung oder Exit ungleich 0? Ein hartes Gate im Closeout wäre wirksamer,
    riskiert aber, dass eine Kaskade mit legitim fehlender Zeile blockiert.
  - Lohnt eine **Kaskade** (Ralph baut) oder ist es wieder Handarbeit? Anders
    als A–C ist das echte Werkzeugarbeit mit Testbedarf — der erste Strang des
    Kits, der in den Loop gehören könnte.

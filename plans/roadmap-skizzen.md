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
Tests dort laufen, wo sie gelten (damals 149, Stand 2.6.0 **280**). Die
Fehlschläge von `pytest team/tests` **im Kit-Repo** bleiben bestehen und sind
**erwartet** — damals 17, Stand 2.6.0 **21** von 280.

**Offen geblieben:** Ob der Lauf zusätzlich in einen Git-Hook gehört, oder ob
die Regel „vor jedem Push" reicht. Bisher reicht sie — es gibt genau einen
Menschen im Prozess. *(Die Regel hieß bis 2026-08-16 „vor jedem Release";
das Kit veröffentlicht keine Releases mehr, ausgeliefert wird der Quellstand.)*

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

## ~~Skizze D: Das Ledger prüft seine eigene Vollständigkeit nicht~~ — gebaut 2026-08-01

Als `kosten.py ledger-pruefen` / `./team-status.sh --ledger-pruefen` umgesetzt
(Architekten-Handarbeit nach Franks Dreisatz, Release 2.4.0). Der Strang lief
**nicht** über eine Kaskade — im Kit-Repo ist kein Team installiert, Ralph kann
hier nichts bauen (Strippenzieher-Entscheid 2026-08-01: bleibt so).

**Die drei offenen Fragen, beantwortet:**

1. *Woher weiß das Werkzeug, dass eine Kaskade abgeschlossen ist?* Aus dem
   **Ledger**, nicht aus `.ralph-state`. Eine Kaskade gilt als abgeschlossen,
   sobald sie eine `ralph`- oder `roles`-Zeile trägt. `.ralph-state` ist ein
   Bauzeiger und wird von `--force` zurückgesetzt; der Archiv-Ordner — der
   ursprüngliche Kandidat — schied an einer harten Randbedingung aus, siehe
   unten.
2. *Warnung oder Exit ≠ 0?* **Beides, getrennt.** Exit `4` bei Warnbefunden
   (`1` bleibt dem Bedienfehler), aber **kein** hartes Gate im Closeout: Eine
   Kaskade mit legitim fehlender Zeile dürfte sonst nicht abschließen, und ein
   Gate, das man regelmäßig umgehen muss, wird umgangen. Stattdessen läuft die
   Prüfung bei jedem `--budget` ungefragt mit — sichtbar, aber nicht blockend.
   Zwei Schweregrade: `warnung` (sehr wahrscheinlich verlorenes Geld) und
   `hinweis` (kann legitim sein). Ein Werkzeug, das bei jedem Lauf rot ist,
   erzieht zum Wegsehen.
3. *Kaskade oder Handarbeit?* Handarbeit — siehe oben.

**Die Randbedingung, die der Entwurf nicht kannte — und was sie geändert hat:**
Die Skizze wollte je Kaskade prüfen, ob eine Zeile kleiner ist als *ihre*
archivierten Rohlogs. Das ist mit der heutigen Ablage **nicht ehrlich
beantwortbar**: Log-Dateinamen tragen keine Kaskadennummer
(`stufe-<n>-<ts>.json`, `harry-<ts>.json`), und das Archiv ist **ein** flacher
Ordner je Quelle. Zuordnen ließe sich nur über mtime-Fenster — also raten, und
in der Kostenmechanik wird nicht geraten. Ein Archiv je Kaskade
(`archiv/kaskade-<n>/`) wäre der saubere Weg gewesen, hätte aber `lauf_kosten()`
in `vollautomatik.sh` gebrochen: Das globbt `.ralph-logs/archiv`
**nicht-rekursiv** und misst den Pro-Lauf-Deckel damit auch gegen Geld, das
eine Abschluss-Stufe *innerhalb* des Laufs schon weggeräumt hat (`BL-55`).
**Entscheid:** Der Rohlog-Vergleich läuft je **Quelle** statt je Kaskade —
Archivordner und Ledger-Rolle entsprechen einander eindeutig, ohne jede
Zuordnung. `BL-4` und `BL-5` hätte er beide gefunden; beide sind mit ihren
echten Feldzahlen als Regressionstest hinterlegt.

**Offen geblieben:** Ein Archiv je Kaskade bliebe die genauere Lösung und würde
den Vergleich kaskadenscharf machen. Der Preis ist eine Änderung an der
Pro-Lauf-Durchsetzung (`lauf_kosten` müsste rekursiv globben, ohne `BL-55`
wieder aufzureißen) — das ist echte Werkzeugarbeit mit Testbedarf und wäre der
nächste Kandidat, **falls** je ein Team im Kit-Repo läuft.

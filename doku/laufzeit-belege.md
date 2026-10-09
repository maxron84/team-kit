# Laufzeit-Belege — was ein Programm erst im Lauf zeigt

> **Wunsch des Owners** (`BL-325`, 2026-10-09): *„Debuglog-orientiertes
> Development … soll in Zukunft für alle Projekte dieser Art hervorgehoben
> werden … Handabnahmen durch den Stakeholder sollen möglichst breitflächig und
> effizient unterstützt werden, um menschliche Fehler bei Auswertungen klein zu
> halten. Der Mensch soll beobachten und bei Look and Feel … beratend tätig
> sein."* Und: Handabnahmen allgemein automatisieren, wo es geht.

Für wen dieses Kapitel ist: Projekte, deren Verhalten sich erst im **laufenden**
Programm zeigt — Spiele, Apps im Emulator oder auf dem Gerät, Oberflächen. Dort
prüft der Smoke-Test, was statisch prüfbar ist; was das Programm *tut*, sah
bisher nur der Mensch. Er wurde zum Debugger: Werte am Bildschirm ablesen,
beschreiben, wiederholen — und jede Abnahme hing an seinem Gedächtnis.

## Einschalten

Ein Wert in `team.config.*`, keine Interviewfrage:

```bash
TEAM_LAUFZEIT_BELEG="Log der Engine unter logs/engine.log"      # bash
```
```powershell
$TEAM_LAUFZEIT_BELEG = 'adb logcat -s MeinSpiel, Emulator ohne Fenster'   # pwsh
```

Der Satz sagt, **wo** das laufende Programm seine Belege schreibt. Ein laufendes
Projekt bekommt den Wert beim nächsten Update leer eingetragen (`BL-311`); wer
ihn füllt, schaltet das Folgende ein. Leer bleibt alles, wie es war.

| Rolle | Was sich ändert |
|---|---|
| **Ralph, Frank** | Bauen oder fixen sie Laufzeitverhalten, schreiben sie an jedem Entscheidungspunkt eine Logzeile mit festem Präfix und liefern die Auswerteregel mit — geprüft an einer Testdatei im **echten** Logformat und mit einer Mutation, die sie rot macht. Ein Fix bringt die Logzeile mit, an der der nächste Lauf ihn belegt. Was nur ein Mensch sehen kann, melden sie als Frage. |
| **Harry, Marv** | Eine eigene Fundklasse: Laufzeitverhalten, das der Code behauptet, ohne dass eine Logzeile es belegt oder eine Auswerteregel sie liest — und eine Auswerteregel, die nur gegen eine nachgeahmte Testdatei geprüft ist. |
| **Der Architekt** | Plant je Stufe die Belege, prüft Annahmen über die Laufzeit vorher mit einer Probe, fährt automatisierbare Proben selbst und belegt die Abnahme aus dem Log. Die Regeln stehen in seinem Briefing. |
| **Du** | Beobachtest und berätst — Look and Feel, Entscheidungen. Du liest keine Werte ab und notierst nichts. |

## Das Verfahren

Gewachsen über elf Kaskaden in `Feld F` (Spielskript-Stack, Windows, pwsh-Bahn,
Smoke-Test nur statisch). Jede der sechs Regeln hat dort einen Fehler beendet.

1. **Die Laufzeit schreibt ihre Belege selbst.** Jede Stufe, die
   Laufzeitverhalten baut, schreibt ihre Belege ins Log — mit einem festen
   Präfix je Kanal (Info, Fehler, Selbsttest, Probe …) und wenigen Werten je
   Zeile: Manche Laufzeit kappt lange Zeilen (dort bei rund 1000 Zeichen).
   Ereignisse erkennt ein Handler im Programm, nicht das Auge.
2. **Ein Werkzeug im Projekt wertet das Log aus.** Es filtert die Kanäle, fasst
   Proben zusammen und fällt das Urteil des Selbsttests. Jede Auswerteregel hat
   eine Testdatei im **echten** Format des Logs und eine Mutation, die sie rot
   macht — zweimal fiel eine Regel erst an einer echten Zeile auf, weil die
   Testdatei das Format nur nachahmte. Mehrere Durchgänge in einem Log trennt
   es an einer festen Startzeile und nennt ihre Zahl.
3. **Das Programm prüft sich selbst.** Ein Selbsttest mit `START`, einer Zeile
   je Prüfung und `SUMMARY`, auf Wunsch als Liste einzelner Prüfungen. Jede
   Stufe, die Laufzeitverhalten baut, bringt ihre Prüfung mit. Der Mensch
   startet ihn mit einer Zeile und wartet.
4. **Was ohne den Menschen laufen kann, läuft ohne ihn.** Der Architekt startet
   gezielte Prüfungen auf einem lokalen headless Server — nur lokal, mit
   Zufallspasswort, am Ende sanft beendet und aufgeräumt; kein Loop-Lauf und
   kein Test startet ihn. Sieben solche Läufe fanden ohne einen Handgriff des
   Menschen die Ursache eines Fehlers, der drei Kaskaden lang offen war.
5. **Die Handabnahme ist Beobachtung, keine Messung** — Vorlage unten.
6. **Annahmen über die Laufzeit werden vorher belegt.** Trägt eine Annahme den
   Kern einer Stufe, kommt vor dem Bau eine Probe: genau eine Größe gegenüber
   dem Commit geändert, eine Kontrolle läuft mit. Zwei Stufen sind gescheitert,
   bevor diese Regel galt.

**Der Preis:** Der Architekt trägt in `Feld F` rund 80 % jeder Kaskade, ein
großer Teil davon Auswertung und Serverbetrieb. Das ist die Arbeit, die vorher
der Mensch mit Ablesen, Beschreiben und Wiederholen geleistet hat — und dabei
die Fehler machte, die der Wunsch klein halten will.

## Vorlage: Handabnahme

```markdown
### Handabnahme — <Stufe / Thema>

**Vorbereitung** (automatisiert, schon erledigt): <Build, Server, Daten, Log geleert>

**Schritte** (ein Block, kopierfertig — Konsolenbefehle sind statisch geprüft):
    <Befehl 1>
    <Befehl 2>

**Worauf du schaust** (beobachten, nicht ablesen): <was sich bewegen, erscheinen, klingen soll>

**Fragen** (eine je Zeile, nur was nur du sehen kannst):
- Fühlt sich <X> richtig an?
- …

**Handarbeit, die kein Skript kann** (eigener Schritt): <z. B. Speichern und Laden>

**Auswertung**: macht der Architekt aus dem Log. Höchstens zwei Nachproben.
```

## Android-Variante (`Feld E`, nicht erprobt)

Für eine App mit Emulator auf der bash-Bahn liegen die Bausteine bereit, erprobt
ist das Verfahren dort noch nicht:

- **Belege:** `adb logcat` mit festem Tag (`adb logcat -s <Tag>`), Präfixe je
  Kanal wie oben.
- **Ohne den Menschen:** Emulator ohne Fenster, instrumentierte
  Oberflächentests, Eingaben und Bildschirmfotos über `adb shell input` und
  `adb exec-out screencap`.
- **Zielstand:** `TEAM_ZIELSTAND_PRUEFUNG` (`BL-300`) prüft, ob der Emulator
  den eben gebauten Stand trägt — der erste Schritt, bevor ein Lauf dort etwas
  belegen kann.

Was dort an Logs, Emulator und automatisierten Abnahmen schon läuft, gehört als
Meldung zurück ins Kit; dieses Kapitel wächst mit.

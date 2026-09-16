# Ein verfallener Red-Team-Fokus ist nur eine Logzeile mitten im Lauf — der Abschlussbericht schweigt darueber

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (vierzehn Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 583 Tests.

## Was passiert ist

Vollautomatik-Lauf einer Kaskade, 2 h 15 min, vier Bau-Stufen und zwei Sweeps.
Beide Sweeps liefen **ohne** den Fokus-String, den die Scharfschalt-Sequenz
gesetzt hatte. Im Lauflog steht es korrekt, zweimal:

```
[harry] Der zuletzt gesetzte Fokus gehört zu einem anderen Stand (55f46be…) — VERFALLEN (BL-31).
  Dieser Sweep läuft mit dem Grundauftrag. Für eine gezielte Prüfung TEAM_REDTEAM_FOCUS neu setzen.
[marv]  Der zuletzt gesetzte Fokus gehört zu einem anderen Stand (0b5ba5f…) — VERFALLEN (BL-31).
```

Die Mechanik selbst ist richtig und tut genau das, wofür `BL-31` sie gebaut
hat (`team/redteam.ps1`:83–96): Ein Fokus aus einem fremden Stand wird
verworfen statt still weiterverwendet. Beanstandet wird **nicht** der Verfall.

## Was fehlt

**Der Abschlussbericht sagt es nicht.** Er zählt Beutebuch-Stände, Kosten,
Commits und die Turn-Aufstellung je Rolle — dass die beiden teuersten Prüfungen
des Laufs ohne ihren Auftrag gelaufen sind, steht dort **nirgends**. Die zwei
Zeilen liegen rund 1 000 Zeilen und zwei Phasen vor dem Bericht, mitten in
einem Lauf, den man per Definition nicht beobachtet — er läuft headless, das
ist sein Zweck.

**Das Ergebnis sieht dabei aus wie ein geglückter Sweep.** In unserem Fall
haben beide Angreifer je einen Fund der Schwere „hoch" geliefert; der Lauf war
nach jeder sichtbaren Kennzahl ein guter. Aufgefallen ist es erst im Closeout,
beim Lesen des Rohlogs — und nur, weil dort ohnehin gelesen wird.

**Die Wirkung ist genau die, gegen die `BL-31` gebaut wurde**, nur eine Stufe
später: `BL-31` verhindert, dass ein **falscher** Fokus still weiterwirkt.
Übrig bleibt, dass **gar kein** Fokus still wirkt.

## Warum es passieren konnte

`$env:TEAM_REDTEAM_FOCUS` war beim Lauf leer — die Sequenz gibt das Setzen der
Variable und den Start als **zwei** kopierbare Blöcke aus, und zwischen ihnen
liegt für den Menschen jede Gelegenheit, die Shell zu wechseln, den Block zu
überspringen oder den Lauf aus einem anderen Fenster zu starten. Das ist unsere
Bauform und wir richten sie bei uns; das Kit trifft daran keine Schuld.

Die Folge trifft aber jeden Nutzer derselben Bauform, und die Sequenz-Vorlage
des Kits sieht genauso aus.

## Vorschlag

Einer von beiden reicht:

1. **Der Abschlussbericht nennt es.** Eine Zeile in der Phasen-Übersicht —
   `Red Team: harry (Grundauftrag, Fokus VERFALLEN), marv (Grundauftrag, Fokus
   VERFALLEN)`. Der Bericht ist die Stelle, die ein Mensch garantiert liest.
2. **Die Sequenz-Vorlage koppelt Fokus und Start.** Fokus-Zuweisung und
   `vollautomatik` in **einer** Kommandozeile statt in zwei Blöcken; dann kann
   die Variable den Lauf nicht verfehlen.

Punkt 1 ist der wichtigere: Er wirkt auch dann, wenn der Fokus aus einem ganz
anderen Grund verfällt.

## Bezug

- `BL-31` (Fokus an den Lauf binden) — die Mechanik, die hier korrekt gegriffen hat.
- Feldprotokoll: `plans/kaskade-14-abschluss.md`, Abschnitt 4.1.

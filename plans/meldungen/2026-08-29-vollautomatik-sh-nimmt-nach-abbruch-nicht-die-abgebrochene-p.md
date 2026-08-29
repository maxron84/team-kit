# vollautomatik.sh nimmt nach Abbruch nicht die abgebrochene Phase auf, sondern faengt die Phasenkette von vorn an

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Bestand, Linux, bash-Bahn, Flutter/Dart-App (Mobile),
  neunte Kaskade, Beutebuch mit laufender Frank/Axel-Fixphase.

## Was passiert ist

Ein Vollautomatik-Lauf wurde in **Phase 4** (Fix-Runden) vom Pro-Lauf-Deckel
gestoppt, unmittelbar nachdem Frank einen Fund gefixt hatte:

```
[frank] HM-40 erledigt (Dreisatz verifiziert).
Runde 2: Frank hat einen Fund gefixt.
LAUF-BUDGET erreicht: dieser Lauf 18.9909 USD >= Deckel 18 USD — harter Stopp
--- WIE ES WEITERGEHT (Budget-Deckel) ---
Keine offenen Funde — nur der Closeout fehlt: ...
Ganzen Lauf fortsetzen: ./vollautomatik.sh (nimmt den Faden am Zeigerstand auf)
```

Der Lauf wurde wie angeboten mit `./vollautomatik.sh` fortgesetzt. Erwartet
war, dass er dort weitermacht, wo er stehen geblieben ist — also in Phase 4.
Tatsächlich:

```
=== PHASE 1: Ralph (Bau der Kaskade) ===
Ralph: Stufe 49 liegt über RALPH_CAP=48 — Feierabend.
=== PHASE Red Team: harry ===
=== harry: Sweep über Commits <alter-stand>..<HEAD> ===
```

Der Fortsetzungslauf beginnt die Phasenkette **von vorn**. Phase 1 ist billig
(Ralph steht über dem Cap und geht sofort), aber Phase 2/3 sind es nicht: Seit
dem letzten Red-Team-Sweep sind Frank-Fix-Commits und Sweep-Dokumentation
entstanden, also liegen für Harry und Marv „neue Commits" vor. Der
Fortsetzungslauf kauft damit **zwei volle Red-Team-Sweeps über Franks eigene
Fixes**, bevor er die Arbeit erreicht, wegen der er gestartet wurde.

Nebenwirkung, die den Effekt verstärkt: Der Fortsetzungslauf setzt `LAUF_START`
neu und hat damit den vollen Pro-Lauf-Deckel wieder frei. Das ist für sich
richtig (BL-18), heißt hier aber: Das ganze frische Budget kann in einen Sweep
laufen, den niemand bestellt hat, und die Fixphase steht danach wieder vor
demselben Deckel wie vorher.

## Wo es steckt

`vollautomatik.sh` (Entrypoint, bash-Bahn; die pwsh-Bahn `vollautomatik.ps1`
dürfte dieselbe Bauart haben).

Das Skript ist **phasen-zustandslos**. Es gibt Zustandsdateien für die
einzelnen Rollen — `.ralph-state` (nächste Stufe), `.harry-state`/`.marv-state`
(zuletzt geprüfter Commit) —, aber **keine** für den Orchestrator selbst. Beim
Start beginnt es unbedingt bei Phase 1 und arbeitet die Kette linear ab; welche
Phase beim letzten Mal abgebrochen wurde, wird nirgends festgehalten.

Damit ist auch die Zeile aus `abbruch_bericht()` sachlich falsch:

```
log "Ganzen Lauf fortsetzen: ./vollautomatik.sh (nimmt den Faden am Zeigerstand auf)"
```

„Zeigerstand" gibt es nur für Ralph. Für die Phasenkette existiert kein Zeiger,
also kann sie den Faden nicht aufnehmen. Die Meldung verspricht eine
Semantik, die das Skript nicht hat — dieselbe Bauart wie ein Smoke-Test, der
grün meldet, weil er eine Umgebung setzt, die der Anwender nicht hat: Der
Mensch handelt nach der Zusage, nicht nach dem Code.

Betroffen ist **jeder** Abbruchpfad, der den Weiterweg anbietet, nicht nur der
Budget-Deckel: Stagnation (Exit 1) und die Session-Limit-Pause (Exit 42, „bitte
später erneut starten") kommen zurück und finden dieselbe Kette von vorn.

## Warum das jede Installation trifft

Der Fehler steckt in einem Entrypoint des Kits, nicht im Projektcode. Jede
Installation, die einen Vollautomatik-Lauf in Phase 4 abbricht — und der
Pro-Lauf-Deckel ist genau dafür gebaut, dass das regelmäßig passiert —, zahlt
beim Fortsetzen einen Red-Team-Durchgang über die Commits der eigenen
Fixphase. Je später im Lauf der Abbruch, desto teurer die Wiederaufnahme:
Zurückgesetzt wird immer auf Phase 1.

Ein lokaler Fix hier hätte Verfallsdatum bis zum nächsten `--update`
(`BL-42`/`BL-58`), deshalb die Meldung statt eines Eingriffs.

## Vorschlag

Ein **Phasen-Zeiger** für den Orchestrator, analog zu `.ralph-state`:

1. `vollautomatik.sh` schreibt beim Betreten jeder Phase den Phasennamen in
   eine Zustandsdatei (z. B. `.vollautomatik-state`), zusammen mit dem
   Plan-Zeiger (`.ralph-plan`) und dem Stufenstand, gegen den er gilt.
2. Beim **regulären** Ende (Abschlussbericht) wird die Datei gelöscht. Sie
   überlebt also genau die Abbrüche — Deckel, Stagnation, Pause 42.
3. Beim Start: Existiert die Datei **und** passen Plan-Zeiger und Stufenstand
   noch, steigt der Lauf bei der vermerkten Phase ein und protokolliert das
   ausdrücklich („Faden aufgenommen bei Phase 4 — Phasen 1–3 übersprungen,
   Stand vom …"). Passt sie nicht mehr (neue Kaskade, umgelegter Plan), wird
   sie verworfen und normal bei Phase 1 begonnen — ein veralteter Zeiger darf
   niemals einen Bau überspringen.
4. Ein benannter Weg zurück auf Anfang, für den Fall, dass der Mensch die
   Sweeps ausdrücklich will: `TEAM_VOLLAUTOMATIK_AB_PHASE=1` oder
   `./vollautomatik.sh --von-vorn`.
5. Die Zeile in `abbruch_bericht()` sagt dann, was stimmt, und nennt die Phase
   beim Namen: „Ganzen Lauf fortsetzen: ./vollautomatik.sh (setzt bei Phase 4
   fort)".

**Gegenargument, das wir geprüft haben:** Beim Überspringen der Phasen 2/3
bleiben Franks Fix-Commits ungesweept. Das ist kein Verlust, sondern
Aufschub — die Sweep-Marke ist commit-basiert, der nächste reguläre Sweep
beginnt hinter `.harry-state`/`.marv-state` und nimmt die Fix-Commits dann
ohnehin mit. Umgekehrt hat der heutige Zustand einen zweiten, stilleren
Nachteil: Der ungeplante Sweep **verschiebt die Marke auf HEAD** und
verbraucht damit den Prüfdurchgang über die Fix-Commits zu einem Zeitpunkt,
zu dem der Fokus-String noch der der Bauphase ist.

Wenn der Vorschlag zu groß ist, wäre die **minimale** Korrektur, wenigstens die
falsche Zusage zu entfernen und den Weiterweg phasengenau zu benennen
(„Fixphase fortsetzen: ./frank.sh" steht bei offenen Funden schon da; hier
fehlt sie, weil der Fund bereits erledigt war und nur der Closeout offen ist).

## Was ich schon versucht habe

Nichts gefixt — der Fund liegt im Kit, nicht im Projekt. Nachgelesen:
`vollautomatik.sh` (Phasenkette, `budget_ok`, `abbruch_bericht`),
`team/redteam.sh` (Sweep-Marke `.<rolle>-state`, Exit 3 „nichts Neues"),
`team/lib.sh` (kein Phasen-Zustand vorhanden). Der Hergang oben ist der
Original-Lauf, nicht nachgestellt.

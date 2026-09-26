# kit-test.sh verstellt in Stufe 5 nur team.config.sh - wo pwsh liegt, faellt dort BL-117 und der Selbsttest bricht ab

- **Bezug**: BL-58, BL-117
- **Art**: Fehler
- **Kit-Version**: 2.13.1 (Quellstand `370ff1d`)
- **Bahn**: bash (Selbsttest), betrifft den Doppelbahn-Harnisch
- **Plattform**: win32
- **Feldkürzel**: — (kein Feldprojekt)
- **Lage des Projekts**: kein Projekt — `bash bash/kit-test.sh` im Kit-Repo, auf einer frisch eingerichteten Windows-11-Maschine mit Git Bash 5.3 und pwsh 7.6 nebeneinander; `kit-test.ps1` ist dort grün

## Was passiert ist

`bash bash/kit-test.sh` bricht in Stufe 5/11 ab („Regressionstests unter
angepasster team.config.sh", `BL-58`). Im Auslieferungszustand ist die Suite
grün (Stufe 4: 998 bestanden, 407 übersprungen), unter der angepassten
Konfiguration fällt genau ein Fall:

```
FAILED team/tests/test_bl117_prompt_gleichstand_am_lauf.py::test_beide_bahnen_setzen_denselben_prompt_ab[frank]
E       -2. Genau EIN Commit: 'fix(qa): <was+warum> (HM-2)'.
E       +2. Genau EIN Commit: 'fix(uat): <was+warum> (HM-2)'.
1 failed, 997 passed, 407 skipped
```

Danach endet der Lauf mit Exit 1; die Stufen 6–11 laufen nicht. Auf derselben
Maschine ist `pwsh -File .\pwsh\kit-test.ps1` grün — auch sein Schritt 6/9,
der dieselbe Suite unter angepasster Konfiguration fährt.

## Wo es steckt

In `bash/kit-test.sh`, Stufe 5 (Zeile ~460–480). Sie verstellt fünf Werte —
darunter `TEAM_FIX_PRAEFIX` auf `fix(qa)` — und zwar **nur in
`team.config.sh`**. `team.config.ps1` bleibt auf dem Auslieferungswert
`fix(uat)`.

Das Gegenstück in `pwsh/kit-test.ps1` (Schritt 6/9) verstellt seit `cbd6772`
**beide** Konfigurationen und begründet es selbst:

```
# Angefasst werden BEIDE Konfigurationen. Ein Wert, der nur in team.config.sh
# angehoben wird, laesst die pwsh-Bahn auf dem Auslieferungsstand: Die Suite
# faehrt dann teils gegen alte, teils gegen neue Werte, und ein Fehlschlag
# waere nicht mehr zuzuordnen.
```

Die bash-Fassung ist dabei nicht nachgezogen worden. Am selben Tag kam mit
`cd5887f` der Gleichstandstest aus `BL-117` dazu, der die Prompts beider
Bahnen **am Lauf** zeichenweise vergleicht — `frank` von Anfang an in
`ROLLEN`. Franks Prompt trägt den Präfix schon länger
(`'${TEAM_FIX_PRAEFIX}: <was+warum> ($HM)'`). Seit dem 2026-08-26 vergleicht
Stufe 5 also `fix(qa)` gegen `fix(uat)`. Der letzte dokumentierte volle Lauf
auf Windows (11/11, README) ist vom 2026-08-25, einen Tag davor.

## Warum das jede Installation trifft

Nicht jede Installation, aber jeden Wirt, auf dem `kit-test.sh` den
Doppelbahn-Harnisch voll fahren kann: bash **und** pwsh 7 im PATH — Git Bash
unter Windows, oder Linux mit pwsh. Ohne pwsh überspringt sich der Fall
(`verlange_pwsh()`), und Stufe 5 ist grün. Die Lücke ist genau dort
unsichtbar, wo sie nicht zuschlägt.

Das Gewicht kommt aus `CONTRIBUTING.md`: **Nachweis ist `bash bash/kit-test.sh`**.
Auf einem Wirt mit beiden Shells endet dieser Nachweis in Stufe 5 — der
Update-Pfad, der Einzug in eine gewachsene Codebasis, die Abwahl einer Bahn,
das Regel-Inventar, die Einrichtungsroutine und der Gleichstand der Installer
(Stufen 6–11) werden dort nicht erreicht. Seit dem 2026-09-17 hat zusätzlich
die README-Drift (sieben neue Testdateien, Zahlen nicht nachgezogen; im selben
Zug nachgezogen) den Lauf schon nach Stufe 2 beendet und diesen Befund
verdeckt.

**Die Fehlermeldung lenkt in die falsche Richtung.** Sie schlägt vor, einen
legitimen Unterschied in `AUSNAHMEN` von `test_bl112_prompt_gleichstand.py`
einzutragen. Hier wäre das der falsche Fix: Er würde einen echten
Bahnunterschied im Präfix künftig verdecken.

## Gegenprobe

In einer Kopie der Installation, die `kit-test.ps1` zur Ansicht zurücklässt,
nur diesen einen Fall gefahren. Die bahneigenen Smoke-Zeilen aus dessen
Schritt 7 sind dafür in beiden Konfigurationen entfernt, sodass beide Bahnen
auf denselben Wert der Bibliothek fallen — einzige Variable ist die
Präfix-Zeile in `team.config.ps1`:

| `team.config.sh` | `team.config.ps1` | Ergebnis |
|---|---|---|
| `fix(qa)` | `fix(qa)` | 1 passed |
| `fix(qa)` | `fix(uat)` | failed — genau die Diff-Zeile oben |

**Nebenbefund derselben Gattung (`BL-58`), in der Gegenprobe gesehen, im Feld
nicht belegt:** Mit den bahneigenen Smoke-Tests aus Schritt 7 (`./smoke.sh`
bzw. `./smoke.ps1`) fällt derselbe Fall ebenfalls — Franks Prompt nennt den
Smoke-Test. Hergeleitet, nicht gefahren: Ein Projekt, das je Bahn ein eigenes
Smoke-Skript einträgt, bekäme in `team-test` ein Rot, obwohl beide Bahnen
richtig arbeiten. Der Test misst dann den Projektwert und behauptet, eine
Zusicherung des Kits zu prüfen.

## Vorschlag

1. `kit-test.sh` Stufe 5 verstellt dieselben fünf Werte auch in
   `team.config.ps1` und prüft, dass die Anpassung dort gegriffen hat — die
   Bauform von `kit-test.ps1` Schritt 6.
2. Ein Quelltext-Gleichstand beider Selbsttests für diese Werteliste (Bauart
   `BL-208`), damit nicht wieder nur eine Fassung nachgezogen wird.
3. Zu erwägen: Der `BL-117`-Fall setzt beiden Bahnen dieselben `TEAM_*`-Werte
   über die Umgebung, statt die Projektkonfiguration zu lesen. Beide
   Konfigurationen lassen die Umgebung vor (`${NAME:-…}` bzw. `Team-Wert`).
   Dann prüft der Fall die Zusicherung des Kits und nicht den Projektwert,
   und der Nebenbefund entfällt mit.

## Was ich schon versucht habe

- **Ursache belegt statt vermutet**: siehe Gegenprobe.
- **Lokaler Fix: keiner.** `kit-test.sh` bleibt auf Wirten mit bash und pwsh 7
  in Stufe 5 rot, bis Punkt 1 umgesetzt ist.

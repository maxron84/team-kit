# bash-Bahn: harry.sh und marv.sh lesen TEAM_REDTEAM_AUFTRAG_* vor dem Laden von team.config.sh - der Grundauftrag wirkt dort nie

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-27-bash-bahn-harry-sh-und-marv-sh-lesen-team-redteam-auftrag-vo.md
      .\kit-melden.cmd ablegen  2026-09-27-bash-bahn-harry-sh-und-marv-sh-lesen-team-redteam-auftrag-vo.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-27-bash-bahn-harry-sh-und-marv-sh-lesen-team-redteam-auftrag-vo.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash betroffen, pwsh korrekt (beide installiert, beide gefahren)
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, beide Bahnen; Spielskript-Stack,
  erste Kaskade in Planung.

## Was passiert ist

Der Architekt hat bei der Planung der ersten Kaskade einen projektspezifischen
Grundauftrag für Harry und Marv gesetzt — so, wie Kopfkommentar und Doku es
verlangen: `TEAM_REDTEAM_AUFTRAG_HARRY`/`_MARV` in `team.config.sh` **und**
`team.config.ps1`, beide Werte zeichengleich (gegengeprüft).

Danach war `./team-test.sh` an genau zwei Stellen rot:

```
FAILED team/tests/test_bl117_prompt_gleichstand_am_lauf.py::test_beide_bahnen_setzen_denselben_prompt_ab[harry]
FAILED team/tests/test_bl117_prompt_gleichstand_am_lauf.py::test_beide_bahnen_setzen_denselben_prompt_ab[marv]
```

Der Diff im Fehlertext: Die **bash**-Bahn setzt den stackneutralen Default
(`Auftrag: Chaos/Regression — wirf dem Programm Steine in den Weg …`) ab, die
**pwsh**-Bahn den konfigurierten Grundauftrag. Alles andere im Prompt ist
gleich, auch die Scope-Zeile mit `TEAM_WEITERER_CODE`.

## Wo es steckt

Reihenfolge in den bash-Wrappern (`bash/entry/harry.sh`, `bash/entry/marv.sh`):

```
export AUFTRAG="${TEAM_REDTEAM_AUFTRAG_HARRY:-<stackneutraler Default>}"
source ./team/redteam.sh      # sourct erst hier team/lib.sh -> team.config.sh
```

Beim Auswerten von `${TEAM_REDTEAM_AUFTRAG_HARRY:-…}` ist `team.config.sh` noch
nicht geladen. Die Variable kann dort nur aus der **Prozessumgebung** kommen;
ein Wert in `team.config.sh` erreicht den Wrapper nie. `redteam.sh` verkettet
danach (`team_redteam_auftrag "$AUFTRAG" ""`) den schon auf den Default
gefallenen Wert mit dem Fokus.

Die pwsh-Wrapper machen es richtig: `Import-Module ./team/lib.psm1` (lädt
`team.config.ps1`) steht **vor** `$auftrag = $TEAM_REDTEAM_AUFTRAG_HARRY`.

## Warum das jede Installation trifft

Jedes Projekt auf der bash-Bahn, das den Grundauftrag so setzt, wie der
Kopfkommentar von `harry.sh` es empfiehlt („setzen TEAM_REDTEAM_AUFTRAG_HARRY in
team.config.sh"), bekommt ihn nie in den Prompt, **ohne jedes Signal**. Die
Sweeps laufen, finden etwas oder nichts, und niemand sieht, dass die dauerhafte
Kenntnis der Angriffsfläche fehlt. Das ist das Schadensbild aus `BL-172`, eine
Ebene tiefer: `BL-172` hat das Verketten von Fokus und Grundauftrag repariert,
der Grundauftrag kommt auf dieser Bahn aber gar nicht erst an.

**Warum die Kit-eigenen Tests es nicht zeigen:** Im Kit ist der Wert leer,
beide Bahnen fallen auf denselben Default, und `BL-117` ist grün. Sichtbar wird
die Divergenz erst in einer **installierten** Ablage, deren Konfiguration den
Wert tatsächlich setzt. Tests, die den Grundauftrag über die **Umgebung**
setzen, gehen am Fehler vorbei, weil die Umgebung ja ankommt.

## Was ich schon versucht habe

Nicht lokal gefixt — die Wrapper sind Kit-Dateien, und ein lokaler Fix verfiele
beim nächsten `--update`. Stattdessen **umgangen**: Grundauftrag in beiden
`team.config.*` wieder leer (beide Bahnen setzen denselben Prompt ab,
`BL-117` wieder grün), der projektspezifische Teil steht vorerst im
Kaskaden-Fokus (`TEAM_REDTEAM_FOCUS`), der beide Bahnen erreicht.

**Vorschlag:** In `harry.sh`/`marv.sh` erst `source ./team/lib.sh` (oder nur
`team.config.sh`), dann `AUFTRAG` ableiten — so wie die pwsh-Bahn. Alternativ
den Default erst in `redteam.sh` nach dem Laden der Bibliothek einsetzen.
**Nachweis:** `BL-117` mit einer Fixture-Konfiguration fahren, die
`TEAM_REDTEAM_AUFTRAG_*` **in der Datei** setzt (nicht in der Umgebung).
**Gegenprobe:** die alte Reihenfolge zurück → `[harry]` und `[marv]` rot.

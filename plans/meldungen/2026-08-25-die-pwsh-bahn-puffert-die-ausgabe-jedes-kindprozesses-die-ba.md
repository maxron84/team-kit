# Die pwsh-Bahn puffert die Ausgabe jedes Kindprozesses - die Bash-Bahn streamt sie

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-08-25-die-pwsh-bahn-puffert-die-ausgabe-jedes-kindprozesses-die-ba.md
      .\kit-melden.cmd senden   2026-08-25-die-pwsh-bahn-puffert-die-ausgabe-jedes-kindprozesses-die-ba.md

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
- **Bahn**: pwsh
- **Plattform**: win32
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn (`--nur-pwsh`), Python + Electron, zweite Kaskade

## Was passiert ist

`vollautomatik` gestartet. Nach

```
[16:28:05] === PHASE 1: Ralph (Bau der Kaskade) ===
```

kam **36 Minuten lang keine einzige weitere Zeile** — weder auf der Konsole noch
im Lauf-Log unter `.team-logs/`, das bei 53 Bytes stehen blieb.

In dieser Zeit liefen fünf Stufen erfolgreich durch und wurden committet; die
`.ralph-logs/stufe-*.json` und `.ralph-state` belegen es. Nach außen war der Lauf
davon nicht zu unterscheiden von einem Hänger, und genau so wurde er auch
gelesen — die Frage des Stakeholders lautete wörtlich „Stimmt hier irgendwas
nicht? Es kommt keine weitere Zeile."

Auf der Bash-Bahn erscheint dieselbe Ausgabe live.

**Die Puffergrenze ist der Kindprozess, nicht der Lauf.** Das erklärt, warum das
Log am Ende doch gefüllt ist und der Fehler deshalb leicht übersehen wird:

| Phase | Aufrufe | Stille am Stück |
|---|---|---|
| Ralph (Bau) | **ein** Aufruf für **alle** Stufen | 36 min |
| Harry / Marv | je ein Aufruf | ~5 min |
| Frank | ein Aufruf je Fix-Versuch | 3–10 min |

Ralph ist der schlimmste Fall, weil ein einziger Prozess die ganze Kaskade
abarbeitet. Wer den Fehler nach dem Lauf sucht, findet ein vollständiges Log und
zieht den falschen Schluss.

## Wo es steckt

`pwsh/entry/vollautomatik.ps1`, in der Hilfsfunktion, die eine Rolle als eigenen
Prozess startet:

```powershell
$ausgabe = & pwsh -NoProfile -File $Skript @Argumente 2>&1
$code = $LASTEXITCODE
foreach ($z in $ausgabe) {
    $text = [string]$z
    [Console]::Out.WriteLine($text)
    Add-Content -LiteralPath $laufLog -Value $text -Encoding utf8
}
```

Die Zuweisung an `$ausgabe` **sammelt den kompletten Kindprozess ein**, bevor die
erste Zeile ausgegeben wird.

Das Gegenstück in `bash/entry/vollautomatik.sh` ist eine einzige Zeile, ganz oben:

```bash
exec > >(tee -a "$LAUF_LOG") 2>&1
```

Sie leitet den Strom der Shell selbst um; jeder Kindprozess erbt ihn und schreibt
live. Das ist kein Detailunterschied, sondern eine andere Konstruktion: `tee`
streamt, `$ausgabe = &…` puffert.

**Der Kommentar über der pwsh-Stelle beschreibt das Problem selbst.** Er
begründet über mehrere Absätze, warum ein externer Prozess nötig ist — die
Rollen schreiben mit `[Console]::Out.WriteLine`, was `&` und `2>&1` im selben
Prozess nicht einfangen — und schließt mit dem Satz, das Lauf-Log hätte sonst
nur die Zeilen des Orchestrators, „und team-status.ps1 zeigt genau dessen letzte
drei Zeilen an". Die Begründung ist richtig; die Umsetzung fällt hinter sie
zurück und liefert während des Laufs genau das Ergebnis, das sie verhindern
wollte.

## Warum das jede Installation trifft

Es steckt in `pwsh/entry/vollautomatik.ps1`, also im Kit selbst, und trifft jede
pwsh-Installation bei jedem Lauf. Es ist zugleich eine **Bahn-Asymmetrie**: Das
im Code dokumentierte Verhalten („Alles doppelt: Konsole + Lauf-Log") gilt nur
auf einer der beiden Bahnen, und keine Doku unterscheidet.

Die Auswirkung ist nicht kosmetisch. Ein Lauf ohne Lebenszeichen ist von einem
hängenden Lauf nicht zu unterscheiden — und die naheliegende Reaktion darauf
(abbrechen und neu starten) ist die teuerste: Sie wirft bezahlte Stufen weg oder
erzeugt einen zweiten Lauf neben dem ersten.

`--watch` in `team-status` ist dafür kein Ersatz: Es zeichnet den ganzen Block
periodisch neu, statt anzuhängen. Wer mitlesen will, bekommt ein flackerndes
Vollbild statt einer Zeilenspur, und was einmal durchgelaufen ist, ist weg.

## Was ich schon versucht habe

Am Kit selbst nichts geändert: Der Lauf war aktiv, und `ralph` committet mit
`git add -A` — jede angelegte Datei wäre in den nächsten Stufen-Commit gewandert.
Ein lokaler Patch hätte ohnehin nur bis zum nächsten `--update` gehalten
(`BL-42`/`BL-58`).

Behelf im Projekt, rein lesend: ein kleines Skript, das im Takt die Spuren liest,
die während des Laufs **auf der Platte** entstehen — neue `.ralph-logs/*.json`
und `.team-logs/*.json` (je eine Zeile mit `subtype`, `num_turns`,
`total_cost_usd`), Wechsel in `.ralph-state`, neue Commits — und sie **anhängend**
ausgibt. Das ersetzt den Strom nicht, macht den Lauf aber wieder lesbar.

**Vorschlag für den Fix**, nach Eingriffstiefe:

1. **Streamen statt sammeln.** Die Ausgabe zeilenweise durch die Pipeline führen
   und dabei auf Konsole *und* ins Log schreiben, statt sie einer Variablen
   zuzuweisen:

   ```powershell
   & pwsh -NoProfile -File $Skript @Argumente 2>&1 | ForEach-Object {
       $text = [string]$_
       [Console]::Out.WriteLine($text)
       Add-Content -LiteralPath $laufLog -Value $text -Encoding utf8
   }
   $code = $LASTEXITCODE
   ```

   `$LASTEXITCODE` bleibt hinter einer Pipeline gültig — ein Regressionstest
   sollte genau das festhalten, weil daran ein späterer Rückbau scheitern würde.

2. **Ein Test, der die Asymmetrie festnagelt.** Er darf **nicht** prüfen, dass am
   Ende Zeilen im Log stehen — das tun sie heute auch. Er muss prüfen, dass sie
   **vor** dem Ende des Kindprozesses dort stehen: eine Wegwerf-Rolle, die eine
   Zeile schreibt und dann wartet, währenddessen das Log lesen.

3. **`--watch` anhängend statt neuzeichnend**, oder ein zweiter Modus daneben
   (`--folgen`). Ein Beobachter, der die Historie überschreibt, ist genau dann
   nutzlos, wenn man wissen will, was in den letzten Minuten passiert ist.

> **Anmerkung zum Melden selbst:** Diese Meldung konnte nicht über
> `kit-melden` angelegt werden — der Wrapper der pwsh-Bahn stirbt vorher an
> einer undefinierten Variablen. Dazu liegt eine eigene Meldung bei; sie ist die
> Voraussetzung dafür, dass diese hier auf dem vorgesehenen Weg entstehen kann.

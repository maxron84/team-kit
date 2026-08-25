# kit-melden ist auf der pwsh-Bahn komplett funktionsunfaehig - TEAM_PYTHON gibt es dort nicht

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-08-25-kit-melden-ist-auf-der-pwsh-bahn-komplett-funktionsunfaehig.md
      .\kit-melden.cmd senden   2026-08-25-kit-melden-ist-auf-der-pwsh-bahn-komplett-funktionsunfaehig.md

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

Erster Versuch überhaupt, auf dieser Installation eine Meldung anzulegen:

```
.\kit-melden.cmd neu --titel "..."
```

Ergebnis:

```
InvalidOperation: ...\kit-melden.ps1:37
Line |
  37 |  & $TEAM_PYTHON team/tools/kit_meldung.py `
     |    ~~~~~~~~~~~~
     | The expression after '&' in a pipeline element produced an object that was
     | not valid. It must result in a command name, a script block, or a
     | CommandInfo object.
```

Exit 1. Betroffen ist **jedes** Verb — `neu`, `pruefen`, `senden`, `issue-link`,
`kit-pfad` —, weil alle durch dieselbe eine Zeile laufen. Der Rückkanal vom Feld
zum Kit ist auf der pwsh-Bahn damit vollständig tot, und zwar seit dem ersten
Tag; es gibt keinen Aufruf, der ihn je erreicht hätte.

## Wo es steckt

`pwsh/entry/kit-melden.ps1`, Zeile 37:

```powershell
& $TEAM_PYTHON team/tools/kit_meldung.py `
    --projektwurzel . `
    --meldungen $meldungen `
    ...
```

**`$TEAM_PYTHON` wird auf der pwsh-Bahn nirgends definiert.** Weder in
`pwsh/entry/team.config.ps1` noch in `pwsh/lib.psm1` noch in `pwsh/redteam.ps1`
kommt der Name vor — `kit-melden.ps1` ist die einzige Fundstelle der ganzen
Bahn. In PowerShell ist eine undefinierte Variable `$null`, und `& $null` ist
genau der zitierte `InvalidOperation`.

Die Bash-Bahn definiert ihn an **zwei** Stellen:

- `bash/lib.sh:120` — `TEAM_PYTHON="${TEAM_PYTHON:-python3}"`
- `bash/entry/team.config.sh:132` — `TEAM_PYTHON="${TEAM_PYTHON:-{{PYTHON}}}"`,
  also mit einem Platzhalter, den der Installer zur Einrichtungszeit füllt.

Beim Übersetzen nach pwsh ist die *Verwendung* mitgekommen, die *Definition*
nicht.

**Die pwsh-Bahn löst den Interpreter sonst anders auf** — über vollständige
Werkzeugzeilen plus `Team-Werkzeug` zur Wortzerlegung:

```powershell
$TEAM_BEUTEBUCH_TOOL = Team-Wert 'TEAM_BEUTEBUCH_TOOL' 'python team/tools/beutebuch.py'
$TEAM_KOSTEN_TOOL    = Team-Wert 'TEAM_KOSTEN_TOOL'    'python team/tools/kosten.py'
```

`kit-melden.ps1` ist der einzige Entrypoint, der aus diesem Muster ausbricht.
Das ist zugleich der naheliegendste Fix (siehe unten).

## Warum das jede Installation trifft

Es steckt in einem Entrypoint des Kits, nicht in Projektcode, und die fehlende
Definition ist nicht umgebungsabhängig — der Aufruf kann auf **keiner**
pwsh-Installation funktionieren.

Die Auswirkung ist größer als ein einzelner kaputter Befehl, weil dieser Befehl
der **Rückkanal** ist. `CLAUDE.md` und das Architekten-Briefing verpflichten die
Rolle ausdrücklich darauf: Steckt ein Fund in `team/`, in einem Entrypoint oder
in einer Regel, ist es „kein Fehler dieses Projekts, sondern des Kits", und es
ist eine Meldung anzulegen. Auf der pwsh-Bahn ist genau dieser Schritt seit
jeher unausführbar. Jeder Kit-Fehler, den eine pwsh-Installation findet, bleibt
dort liegen — und trifft die nächste Installation erneut.

Der Fall ist selbstbezüglich: Die erste Meldung, an der es hier scheiterte,
beschreibt einen anderen Kit-Fehler (gepufferte Lauf-Ausgabe auf der pwsh-Bahn).
Sie liegt bei und musste am Wrapper vorbei angelegt werden.

**Hinweis auf eine mögliche zweite Lücke gleicher Art:** `TEAM_KIT_PFAD` wird in
`kit-melden.ps1` gelesen (`if ($TEAM_KIT_PFAD) {...}`), taucht in der
pwsh-Konfiguration aber ebenfalls nicht auf. Dort ist es unkritisch, weil die
Abfrage den leeren Fall abfängt — ein `--kit ""` geht durch. Es sieht trotzdem
nach demselben Übersetzungsverlust aus und wäre einen Blick wert.

## Was ich schon versucht habe

Am Kit nichts geändert; ein lokaler Patch hätte nur bis zum nächsten `--update`
gehalten (`BL-42`/`BL-58`), und die Meldung soll die Ursache erreichen, nicht das
Symptom hier zudecken.

Umgehung, mit der beide Meldungen dieser Sitzung entstanden sind — das Werkzeug
direkt aufrufen, mit denselben Argumenten, die der Wrapper durchreicht:

```powershell
<interpreter> team/tools/kit_meldung.py `
    --projektwurzel . `
    --meldungen plans/kit-meldungen `
    --kit "<pfad-zum-kit>" `
    --projekt "<projektname>" `
    neu --titel "..."
```

Das funktioniert einwandfrei; `kit_meldung.py` selbst ist in Ordnung. Kaputt ist
nur der pwsh-Wrapper davor.

**Vorschlag für den Fix:**

1. **Dem Muster der Bahn folgen**, statt eine neue Variable einzuführen: eine
   Werkzeugzeile in `pwsh/entry/team.config.ps1` anlegen, analog zu
   `TEAM_KOSTEN_TOOL`, und über `Team-Werkzeug` aufrufen —

   ```powershell
   $TEAM_KIT_MELDUNG_TOOL = Team-Wert 'TEAM_KIT_MELDUNG_TOOL' 'python team/tools/kit_meldung.py'
   ```

   Dann liegt die Interpreter-Frage an derselben Stelle wie für `kosten.py` und
   `beutebuch.py`, und es gibt keinen Sonderweg mehr.

2. **Ein Rauchtest über alle Entrypoints der Bahn.** Der eigentliche Befund ist
   nicht die eine Zeile, sondern dass ein Entrypoint **nie** ausgeführt wurde:
   Ein Aufruf von `kit-melden kit-pfad` (harmlos, rein diagnostisch) hätte den
   Fehler am ersten Tag gezeigt. Ein Test, der jeden Entrypoint einmal mit einem
   nebenwirkungsfreien Verb aufruft und auf Exit 0 prüft, fängt diese ganze
   Klasse.

3. **Ein Wächter gegen undefinierte Variablen** in den pwsh-Entrypoints. Was in
   Bash `set -u` leistet, gibt es hier nicht von selbst: `$null` läuft still
   weiter, bis es jemand aufruft. `Set-StrictMode -Version Latest` in den
   Entrypoints hätte dieselbe Wirkung und hätte auch diesen Fall gemeldet.

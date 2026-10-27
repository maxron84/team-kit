# team-status.cmd bucht auf der pwsh-Bahn stumm - die Meldung mit der gebuchten Achse erscheint nie

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-26-team-status-cmd-bucht-auf-der-pwsh-bahn-stumm-die-meldung-mi.md
      .\kit-melden.cmd ablegen  2026-10-26-team-status-cmd-bucht-auf-der-pwsh-bahn-stumm-die-meldung-mi.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-26-team-status-cmd-bucht-auf-der-pwsh-bahn-stumm-die-meldung-mi.md   # sonst: Pull Request

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
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; erste Architekten-Sitzung, noch keine Kaskade gelaufen

## Was passiert ist

Am Ende einer reinen Planungssitzung hat der Architekt seine Sitzung gebucht, wie
das Briefing es verlangt (`Kit-BL-165`), auf der pwsh-Bahn:

```
python team/tools/kosten.py sitzung-messen --projekt .
.\team-status.cmd --architekt-abschluss 6.9315 produkt "<notiz>" --kaskade 1 --transkript <kennung> --bis <zeit>
```

Erwartet war die Zeile `Architekt-Zeile Kaskade 1 (produkt) angelegt: 6.9315 USD (abo)`
samt dem Hinweis aus `Kit-BL-252`. Das Briefing verlangt ausdrücklich, sie zu lesen:
„Ich lese die Erfolgsmeldung, statt sie zu überblättern: Sie nennt die gebuchte
Achse“ (`Kit-BL-143`). Es kam **nichts**, Exit 0. Die Zeile stand trotzdem richtig
im Ledger (Achse `abo`), und `--ledger-pruefen` meldete keine Befunde — aufgefallen
ist es nur, weil die Meldung fehlte.

Nachgestellt in einer Wegwerf-Kopie des Projekts, das echte Ledger blieb unberührt:

| Aufruf | Ausgabe | Exit |
|---|---|---|
| `.\team-status.cmd --architekt-abschluss 0.0100 produkt 'Probe' --kaskade 99` | **keine** (Zeile geschrieben) | 0 |
| derselbe Aufruf noch einmal (Kollisionsschutz greift) | `Fehler: Fuer Kaskade 99 steht bereits eine architekt-Zeile …` | 1 |
| `python team/tools/kosten.py akteur-abschluss … --kaskade 97` (direkt, Erfolg) | `Architekt-Zeile Kaskade 97 (produkt) angelegt: 0.0100 USD (abo)` plus Hinweis | 0 |
| `./team-status.sh --architekt-abschluss 0.0100 produkt "Probe bash" --kaskade 98` (bash-Bahn) | `Architekt-Zeile Kaskade 98 (produkt) angelegt: 0.0100 USD (abo)` plus Hinweis | 0 |

Der Fehlerweg kommt also durch (stderr), der Erfolgsweg nicht (stdout), und nur auf
der pwsh-Bahn.

**Beifang aus derselben Datei:** `.\team-status.cmd --hilfe` druckt vor dem Hilfetext
drei Fehler (die bash-Bahn druckt die Hilfe sauber):

```
The term 'am' is not recognized as a name of a cmdlet, function, script file, or executable program.
The term 'waechst' is not recognized as a name of a cmdlet, function, script file, or executable program.
The term 'Hilfe' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

## Wo es steckt

1. **Stumme Buchung:** `pwsh/entry/team-status.ps1`, der Verteiler am Dateiende:

   ```
   '--architekt-abschluss' { exit (Status-ArchitektAbschluss $rest) }
   '--akteur-abschluss'    { exit (Status-AkteurAbschluss $rest) }
   '--rollen-abschluss'    { exit (Status-RollenAbschluss $rest) }
   ```

   `exit (Funktion)` nimmt alles, was die Funktion auf den Ausgabestrom schreibt, als
   ihren Rückgabewert. Die Buchungsfunktionen rufen `kosten.py` über `Team-Werkzeug`
   (`& $befehl @(…)` in `pwsh/lib.psm1`); dessen stdout landet im Rückgabewert statt
   auf dem Bildschirm. `Status-Hilfe` und `Status-Altlast` schreiben deshalb über
   `[Console]::Out.WriteLine` — die Buchungswege nicht.

   **Die zweite Hälfte, mit einer Wegwerf-Probe belegt:** Schreibt das gerufene
   Werkzeug auf stdout **und** endet ungleich 0, endet `exit (…)` mit **0** — der
   Rückgabewert ist dann ein Feld aus Textzeilen und Exit-Code. Probe: eine Funktion
   ruft `python -c "print('…'); sys.exit(N)"`, danach `return $LASTEXITCODE`, und das
   Skript endet mit `exit (Wrapper N)`. Für N = 0, 1 und 3 war der Exit-Code des
   Skripts jedes Mal 0. Am echten `kosten.py` habe ich keinen Fehlerpfad gefunden, der
   vorher auf stdout schreibt; dass der Exit-Code stimmt, hängt also daran, dass das so
   bleibt. `--rollen-abschluss` habe ich nicht nachgestellt (dafür fehlten Rollen-Logs),
   er hat dieselbe Bauart.

2. **Hilfe:** `Status-Hilfe` in derselben Datei. Ihr Kommentarblock enthält den Satz
   „Gelesen wird der Block zwischen `<#` und `#>` am Dateianfang“. Das zitierte `#>`
   beendet den Block-Kommentar — Backticks maskieren in einem PowerShell-Kommentar
   nichts. Die Reste der Zeilen laufen als Befehle. Dieselbe Bauart wie `Kit-BL-229`
   (ein zitiertes Kommentar-Endezeichen hatte `pwsh/lib.psm1` zerlegt).

## Warum das jede Installation trifft

Beides steckt in einem Entrypoint des Kits und ist am Kit-Stand `2fd244d` unverändert
(die installierte Datei ist zeichengleich mit `pwsh/entry/team-status.ps1`). Jede
pwsh-Installation bucht damit jeden Closeout stumm — genau an der Stelle, an der das
Briefing das Lesen der Meldung verlangt, um eine Buchung auf der falschen Achse zu
erkennen (`Kit-BL-143`: im Feld standen 16,3990 USD unter „real via API abgerechnet“).
Auch der Hinweis aus `Kit-BL-252`, nach der Buchung eine neue Sitzung zu öffnen,
erreicht auf dieser Bahn niemanden.

## Was ich schon versucht habe

Im Projekt nichts geändert: Der Fix gehört ins Kit, ein lokaler Fix verfiele beim
nächsten `--update` (`Kit-BL-42`/`Kit-BL-58`). Bis dahin hilft nur, nach jeder Buchung
das Ledger selbst zu lesen.

Vorschlag, ohne Anspruch: Die Buchungsfunktionen geben die Werkzeugausgabe
ausdrücklich auf den Bildschirm (wie `Status-Hilfe` über `[Console]::Out.WriteLine`)
und liefern nur den Exit-Code zurück. Für die Hilfe das `#>` im Kommentar umschreiben
(„zwischen den Kommentarmarken am Dateianfang“). Je ein Regressionsfall auf der
pwsh-Bahn: Die Erfolgsmeldung einer Buchung erscheint; `--hilfe` druckt keine
Fehlerzeile.

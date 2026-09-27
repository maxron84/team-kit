# Architekten-Briefing kennt nur die bash-Bahn

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-27-architekten-briefing-kennt-nur-die-bash-bahn.md
      .\kit-melden.cmd ablegen  2026-09-27-architekten-briefing-kennt-nur-die-bash-bahn.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-27-architekten-briefing-kennt-nur-die-bash-bahn.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit — Briefing und Scharfschalt-Sequenz nur für bash; auf pwsh zusätzlich ein ausgehebelter Verfallsschutz (BL-31)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh (beide Bahnen installiert, der Stakeholder arbeitet nur in pwsh)
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, Spielskript-Stack mit Prüfwerkzeug in
  Python; zwei Kaskaden gelaufen.

## Was passiert ist

Der Architekt hat die Scharfschalt-Sequenz so ausgegeben, wie sein Briefing sie
vorgibt: `TEAM_REDTEAM_FOCUS='…' ./vollautomatik.sh`, `./team-status.sh`,
`./team-status.sh --architekt-abschluss …`, `python3 team/tools/kosten.py …`. Der
Stakeholder hat sie in pwsh eingefügt. Die Folgen:

1. **Der Start fiel aus:** `The term 'TEAM_REDTEAM_FOCUS=Kontext: …' is not recognized
   as a name of a cmdlet, function, script file, or executable program.` Das war
   harmlos und fiel sofort auf.
2. **Die Kostenbuchung fehlte, ohne dass es auffiel:** `./team-status.sh` und
   `./team-status.sh --architekt-abschluss …` gaben in pwsh nichts aus, und im
   Ledger stand keine Zeile. Aufgefallen ist das erst, als der Architekt das
   Ledger las.
3. **`echo … > .ralph-plan` schreibt in pwsh CRLF.** Beide Bahnen lesen den Zeiger
   trotzdem richtig (`tr -d '[:space:]'` bzw. `Get-Content`), das war also kein
   Schaden.
4. **Umgebungsvariablen bleiben in der pwsh-Sitzung stehen.** Ein
   `$env:TEAM_BUDGET_USD = 18` aus dem Lauf davor hat die Plan-Empfehlung des
   nächsten Laufs übersteuert:
   `Deckel: Der Plan empfiehlt 20 USD, gefahren wird mit 18 USD. Grund: TEAM_BUDGET_USD ist gesetzt und hat Vorrang.`
   Geschadet hat es nicht, der Lauf blieb darunter. Die Meldung erscheint aber nur
   im Log, und der Lauf fährt weiter.

## Wo es steckt

- `team/prompts/rolle-architekt.md`: Dreisatz Schritt 3 (Kostenabschluss als
  letzter Schritt der Sequenz), Abschnitt „Nach jedem Lauf" und die Tabelle zum
  Rückkanal nennen nur `./team-status.sh`, `./kit-melden.sh` und `python3`. Auf
  Windows ist `python3` oft nur der Store-Platzhalter; `team.config.*` kennt dafür
  `TEAM_PYTHON`. `TEAM.md` hat die Übersetzungstabelle bash ↔ pwsh, das Briefing
  nicht. Die Vorlage von `kit-melden` rendert dagegen schon je Bahn
  (`.\kit-melden.cmd …`), der Installer kennt die Bahn also.
- **Schwerer wiegt Punkt 4 für den Fokus.** `team/redteam.ps1` (ebenso
  `redteam.sh`): Ist `TEAM_REDTEAM_FOCUS` gesetzt, wird er ungeprüft mit dem
  aktuellen HEAD in `.team-focus-<rolle>` geschrieben und benutzt. Die
  HEAD-Bindung aus BL-31 greift nur, wenn die Variable **nicht** gesetzt ist. In
  bash setzt `VAR='…' ./vollautomatik.sh` sie nur für diesen Aufruf. In pwsh
  heißt der dokumentierte Weg `$env:VAR = '…'; .\vollautomatik.cmd` (so auch im
  Kommentar zu den Modellstufen in `team.config.ps1`), und damit bleibt der
  Fokus der vorigen Kaskade in der Sitzung stehen. Der nächste Lauf nimmt ihn
  still als frischen Fokus. Das ist genau der Feldfall, den BL-31 abstellen
  sollte.

## Warum das jede Installation trifft

Jede Installation, deren Stakeholder in pwsh arbeitet, bekommt vom Architekten
eine Sequenz, die dort nicht läuft. Der Teil, der still scheitert, ist die
Kostenbuchung, also genau der Schritt, den `Kit-BL-197` an ein Ereignis gebunden
hat, damit er nicht verloren geht. Punkt 4 trifft jede pwsh-Installation auch
ohne Architekten: Wer nach der Anleitung `$env:` setzt, fährt die nächste
Kaskade mit dem alten Fokus und dem alten Deckel.

## Was ich schon versucht habe

Lokal habe ich nichts am Kit geändert. Der Architekt dieses Projekts hat sich
notiert, Sequenzen nur noch in pwsh auszugeben: `.\*.cmd`, `$env:X = '…'`, nach
dem Lauf `Remove-Item Env:X`. Das hält aber nur in diesem Projekt.

**Vorschlag:**
1. Das Briefing nach der Bahn rendern, so wie die `kit-melden`-Vorlage, oder
   wenigstens die Übersetzungstabelle aus `TEAM.md` dort aufnehmen, mit
   `TEAM_PYTHON` statt `python3`.
2. Die pwsh-Form der Sequenz räumt ihre Variablen selbst ab:
   `$env:TEAM_REDTEAM_FOCUS = '…'; .\vollautomatik.cmd; Remove-Item Env:TEAM_REDTEAM_FOCUS`.
   `TEAM_BUDGET_USD` bleibt dabei ungesetzt, der Plankopf regelt den Deckel.
3. Robuster wäre es, wenn `vollautomatik` den Fokus zusammen mit dem Plan
   festhält und laut wird, wenn ein gesetzter Fokus wortgleich zu einem
   anderen Plan gehört.

**Nachweis:** Ein Test auf der pwsh-Bahn setzt `$env:TEAM_REDTEAM_FOCUS`, fährt
zwei Sweeps auf verschiedenen HEADs und erwartet beim zweiten eine Warnung
statt der stillen Übernahme.
**Gegenprobe:** Ohne den Fix läuft der zweite Sweep mit dem alten Fokus und
ohne Warnung.

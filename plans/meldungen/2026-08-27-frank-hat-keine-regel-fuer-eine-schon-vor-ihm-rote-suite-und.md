# Frank hat keine Regel fuer eine schon vor ihm rote Suite und stellt headless Rueckfragen ins Leere

- **Art**: Fehler am Kit (Regelluecke + fehlender Rueckkanal)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkuerzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, ~120
  Tests, vierte gebaute Kaskade

## Was passiert ist

Frank sollte einen Fund fixen. Sein Diff war fertig und nachweislich
nicht-regressiv — die Suite war aber **unabhaengig von ihm** rot: eine ambiente
Umgebungsvariable der Entwicklermaschine leckte in eine In-Prozess-Testbank.
Ein bereits gefixter Geschwisterfund deckte nur die Subprozess-Testbaenke ab,
nicht diese.

Frank hat die Lage korrekt erkannt und woertlich protokolliert:

> **Das ist mein Hindernis:** Franks Dreisatz verlangt fuer einen `src/`-Fix
> explizit den gruenen Smoke-Test-Befehl woertlich — den kann ich auf dieser
> Maschine gerade nicht liefern, obwohl mein Diff nachweislich keinen einzigen
> zusaetzlichen Fehlschlag verursacht.

Danach tat er das, was sein Briefing ihm vorgibt: kein Promise, Hindernis
beschreiben. Zusaetzlich stellte er **zwei Rueckfragen**:

> 1. Soll ich den Fix trotzdem committen, da er nachweislich isoliert korrekt
>    und nicht-regressiv ist?
> 2. Der Umgebungs-Leck ist ein eigener, neuer Fund — soll ich den irgendwo
>    vormerken, oder ueberlaesst du das dem naechsten Red-Team-Lauf?

Beide Fragen gingen an einen Menschen, den es in diesem Aufruf nicht gibt. Der
Lauf ist headless (`--permission-mode bypassPermissions`), niemand liest mit,
und die Fragen liegen nur im gitignorierten Lauf-Log. Ergebnis: 2,75 USD
bezahlte, inhaltlich fertige Arbeit verworfen, im Folgeaufruf neu gemacht — und
der **nebenbei gefundene zweite Fehler** ging beinahe verloren. Gerettet hat
ihn allein, dass ein Mensch spaeter das Log oeffnete; er wurde danach als
eigener Fix nachgezogen.

## Wo es steckt

**(1) Die Regelluecke.** `pwsh/entry/frank.ps1` baut Schritt 1 des Auftrags mit
`$SMOKE_SUFFIX` (`pwsh/lib.psm1:227`): `" Smoke-Test grün: <befehl>."` Die
Auflage ist **absolut** formuliert und kennt den Fall nicht, dass die Rotheit
nicht von Frank stammt. `geteilt/prompts/rolle-frank.md` sagt dazu nichts.
Damit gibt es fuer eine vorbestehend rote Suite genau einen Ausgang: abbrechen.

Das ist ein schlechter Tausch. Was die Auflage schuetzen will, ist *„Frank
bricht nichts"* — gemessen wird aber *„der Baum ist gruen"*, und das ist eine
Eigenschaft der **Maschine**, nicht des Fixes.

**Vorschlag:** Differenzmessung statt Absolutwert. `frank.ps1` ruft ohnehin
schon `team_guard_begin` und kennt `$startHash`. Die Auflage koennte lauten:
*„Der Smoke-Test darf durch deinen Fix **keinen neuen** Fehlschlag bekommen.
War die Suite schon vor deinem Eingriff rot, miss beide Staende und weise die
Differenz nach; nenne die vorbestehenden Fehlschlaege im Commit-Text."* Das
haelt die Schutzwirkung und macht die Rolle unabhaengig von einer Maschine, die
sie nicht aufraeumen darf.

**(2) Der fehlende Rueckkanal.** Frank kennt genau zwei Ausgaenge: Promise oder
kein Promise. Fuer *„Hindernis, aber unterwegs etwas gefunden"* gibt es keinen.
Alles, was er nebenbei sieht, endet im gitignorierten Log — auch dann, wenn es
ein echter neuer Fehler ist.

**Vorschlag:** Frank darf einen **neuen Fundblock mit Status `offen`** ins
Beutebuch schreiben. Das verletzt *Finder != Fixer* nicht, sondern bestaetigt
es: Er meldet und ruehrt ihn nicht an. Die zweite Frage oben war exakt diese
Bitte um Erlaubnis — sie waere mit einer Zeile im Briefing nie entstanden.

Angrenzend, vermutlich dieselbe Wurzel: Das Briefing verbietet Rueckfragen
nicht ausdruecklich. Ein Satz wie *„Es liest niemand mit. Stelle keine Fragen,
sondern triff die beste belegbare Entscheidung und schreibe auf, was du
entschieden hast"* waere die vorbeugende Fassung.

## Warum das jede Installation trifft

Beide Teile stecken in `geteilt/prompts/rolle-frank.md` und in der
Prompt-Konstruktion von `frank.ps1`/`frank.sh` — jede Installation erbt sie.
Die rote Fremdsuite ist kein Ausnahmefall: Jedes Bestandsprojekt hat
Umgebungsabhaengigkeiten, und jede Maschine mit Firmenrichtlinien, Proxy oder
gesetzten Variablen kann eine Suite roetlich faerben, ohne dass es mit dem Fund
zu tun hat. Getroffen wird dabei ausgerechnet der Fall, in dem Frank **richtig
gearbeitet hat** — die Arbeit wird trotzdem verworfen und im naechsten Aufruf
bezahlt wiederholt.

## Was ich schon versucht habe

Lokal nichts geaendert; ein Eingriff in `team/` haette ein Verfallsdatum beim
naechsten `--update`. Der zweite Fehler wurde spaeter von Hand als eigener Fund
nachgezogen und gefixt — durch einen Menschen, der das Log gelesen hat, nicht
durch das Verfahren.

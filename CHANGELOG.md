# Changelog — T.E.A.M.-Starterkit

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [2.5.0] — 2026-08-11

**Sechs Feldbefunde aus `team-kit_project_platformer` (K29–K33), abgearbeitet.**

Der rote Faden: **Ein Vorgang, der Geld gekostet hat, muss eine Spur
hinterlassen, die man von „nichts passiert" unterscheiden kann.** Fünf der
sechs Einträge sind Varianten davon — ein Erfolgslog ohne Auftrag, ein
Kostenlog ohne Inhalt, ein Sweep ohne Fund, eine Warnung ohne zutreffende
Ursache, ein abgetragener Backlog-Punkt ohne Nachzug in den Zitaten.

### Added

- **Vierte Fehlerklasse wird erkannt und benannt: „Stufe fertig, Quittung
  fehlt" (`BL-41`, zweite Hälfte).** Neben Erfolg, echtem Fehler und
  Session-Limit gibt es einen vierten Ausgang: Die Rolle startet einen
  Hintergrund-Task/Monitor/Wakeup und wartet auf eine Benachrichtigung, die es
  headless nicht gibt. Das Log trägt dann `subtype: success`, `is_error:
  false` — **es sieht aus wie ein Erfolg** —, nur das Promise fehlt. Vier
  Vorfälle im Feld, **19,47 USD**, jedes Mal für Arbeit, die fertig und grün
  war. Die bisherige Meldung („KEIN Promise — Log prüfen") schickte den
  Menschen in ein Log, das Erfolg meldet, und von dort in den **Plan** statt in
  den Fehlermodus; dreimal folgte darauf ein Neubau, der die bezahlte Arbeit
  wegwarf.
  **Neu:** `team_result_meldet_erfolg` + `team_quittung_fehlt_melden` in
  [`team/lib.sh`](team/lib.sh); [`ralph.sh`](entry/ralph.sh) endet in diesem
  Fall mit dem eigenen **Exit 43** und druckt den Prüfweg (committet? Suite
  grün? dann von Hand quittieren), [`vollautomatik.sh`](entry/vollautomatik.sh)
  und [`halbautomatik.sh`](entry/halbautomatik.sh) reichen ihn als eigenen
  Ausgang durch — nicht als „Fehler". **Geprüft wird die Struktur, nicht der
  Wortlaut:** Die drei Feldvorfälle formulierten es dreimal anders („background
  pytest run and monitor", „fallback check / wakeup", „set up a monitor to catch
  its completion"), und die vierte Variante schreibt jemand morgen. Die
  Vordergrund-Auflage in `SMOKE_ZEILE` (2.4.x) bleibt als **Prävention** — sie
  hat in K33 nicht gehalten, obwohl sie wortgleich installiert war: Ein Satz aus
  dem ersten Turn konkurriert nach 65 Turns mit dem gesamten seither gewachsenen
  Kontext. Prävention per Prompt skaliert **gegenläufig zur Stufenlänge**.
- **Verworfene Versuche bekommen einen Ersatzzettel (`BL-46`).** Scheitert ein
  Aufruf so, dass das Log unlesbar bleibt (im Feld: **0 Byte nach 47 Minuten**),
  schreibt `team_claude` an seine Stelle einen Zettel mit dem, was belegbar ist:
  `total_cost_usd: null`, `team_versuch: "verworfen"`, gemessene Dauer.
  **Nicht geschätzt — sichtbar gemacht.**

### Fixed

- **`kosten.py summe` zählte ein unlesbares Log still als 0.0000 (`BL-46`).**
  Das ist der Pfad, den Live-Kontostand, `--budget` und die Pro-Lauf-/
  Pro-Stufe-Deckel benutzen: Der Abo-Gegenwert von 47 Minuten fiel aus **jedem**
  Kostenabschluss, der Deckel bekam auf diese Hälfte keinen Griff, und die Stufe
  erschien als die **billigste** der Kaskade, obwohl sie als teuerste angesetzt
  war. **Neu:** Die Zahl auf stdout bleibt unverändert (Aufrufer parsen sie), der
  Hinweis geht nach stderr — „N verworfener Versuch(e), zusammen 47 min, Kosten
  UNBEKANNT".
- **`ledger-pruefen` schlug wegen desselben Logs dauerhaft falschen Alarm
  (`BL-46`).** P2 meldete die Kaskade als verdächtig, nannte zwei Ursachen, von
  denen keine zutraf, und empfahl als Abhilfe `--ersetzen` — eine Handlung, die
  nach `BL-5` den Altwert vernichtet. Der Wächter empfahl also, Geld zu
  verlieren, und es gab **keinen dokumentierten Weg**, den Rest loszuwerden.
  **Neu:** Unarchivierte Logs **ohne Kostenbeleg** (Ersatzzettel oder kaputt)
  sind ein Hinweis statt einer Warnung und nennen den Weg heraus; der
  `BL-5`-Fall (echtes unarchiviertes Log) bleibt unverändert eine Warnung.
  `--rollen-abschluss` archiviert Ersatzzettel **mit** (sie können nicht doppelt
  zählen) und sagt beim Buchen, dass der Betrag nachweislich unvollständig ist;
  eine wirklich unlesbare Datei bleibt liegen — mit genanntem Ausweg.
- **Ein Sweep ohne Fund war von einem abgebrochenen Sweep nicht zu
  unterscheiden (`BL-47`).** Im Feld: Marv, 9 Minuten, **3,1418 USD**, eine
  einzige committete Datei (ein Sondenskript), null Beutebuch-Zeilen — und
  trotzdem Commit-Botschaft „neue Funde/Reproducer" plus Protokollzeile „Funde
  committet. Übergabe an Frank." Inhaltlich war das Nichtfinden richtig; der
  Fund ist die **Ununterscheidbarkeit**: Eine read-only-Rolle hat weder
  Statuswechsel noch Produktivdiff, an dem sie sonst auffiele. **Neu:**
  [`redteam.sh`](team/redteam.sh) zählt die **wirklichen** neuen Funde
  (`next-id` vorher gegen nachher — die Zahl lag längst vor) und schreibt sie in
  Commit-Botschaft **und** Protokoll: „1 neuer Fund" / „keine neuen Funde",
  „Geprüft, KEINE neuen Funde … Keine Übergabe an Frank." Dazu im Sweep-Auftrag
  die fehlende Pflicht: Ein Wegwerf-Skript wird **gelöscht** oder als
  `HM-<Nr>`-Reproducer **benannt** — was in `tests/` bleibt, braucht einen Namen
  und einen Fund.
- **Die Abo-Key-Startwarnung zeigte nach einem API-Fallback auf die falsche
  Ursache (`BL-48`).** Sie empfahl, den Key „aus `.bashrc`" zu nehmen — dort lag
  keiner. Gesetzt hatte ihn der API-Fallback der **vorigen Stufe** im selben
  Prozessbaum. Weil die Warnung nur **einmal pro Prozessbaum** feuert,
  verbrauchte der Fehlalarm zusätzlich genau das Fenster, das dem echten Fall
  zusteht (dort real ~13,8 USD Leerlauf über API). **Neu:**
  `team_resolve_auth_mode` markiert einen **selbst geladenen** Key
  (`TEAM_KEY_AUS_FALLBACK`); die Meldung sagt dann, was wirklich passiert ist,
  und **verbraucht das Warnfenster nicht**.

### Changed

- **Zentrale Werte werden gegengeprobt, nicht gegrept (`BL-49`).** Neue Regel in
  den bauenden Briefings (Ralph, Frank) und in der Aushärtungs-Checkliste: Wer
  eine Konstante/einen Default/einen Schwellwert ändert, fährt sie probeweise
  gegen **zwei fremde Werte** (höher/niedriger), lässt die Suite laufen und
  setzt den Wert **nachweislich zurück**. Grund: Eine *arithmetische* Kopplung
  ist per Textsuche unauffindbar — im Feld fand `grep` nach Name und altem Wert
  **fünf** Stellen, das Verstellen **sieben**; die zwei zusätzlichen wären beim
  nächsten Tweak an unerklärlicher Stelle rot geworden.
- **Der Closeout pflegt jetzt auch die Gegenrichtung (`BL-50`, Stufe 1).**
  Erledigte Backlog-Einträge abzutragen funktionierte; **nichts** pflegte die
  Stellen, die den Backlog **zitieren** — Skizzen und Kandidatenlisten
  begründen ihre offenen Fragen mit Backlog-Nummern und veralten still. Der
  Fehler schlägt beim **Vorlegen der Kandidaten** zu, also nachdem eine Option
  formuliert wurde, die es nicht mehr gibt (im Feld: drei Kaskaden lang eine
  Prämisse, die der zitierte Eintrag selbst widerlegte). **Neu:** Pflichtzeile in
  Abschnitt 4 der Abschluss-Gliederung *(„Welche offenen Punkte hat dieser Lauf
  **nebenbei** eingelöst, und wer zitiert sie?")* — in der Gliederung selbst, nicht
  nur in der Prosa daneben —, dazu die Schreibweise `Kit-BL-<N>` für fremde
  Backlog-Nummern. **Offen bleibt Stufe 2**, der maschinelle Lint: Roh gemessen
  lag seine Trefferquote bei ~40 % (sechs von zehn Markierungen waren legitime
  Rückblicke); roh ausgeliefert wäre er die Falle aus `BL-14` — eine Warnung, die
  bei jedem Aufruf erscheint und zum Wegsehen erzieht.
- **Sechs neue Testdateien, 267 statt 232 Testfälle.** Jeder Eintrag mit
  Gegenprobe: Mit zurückgerollten Quellen fallen **25** der neuen Zusicherungen,
  keine bestehende. `BL-41`, `BL-47` und der Abschlusspfad von `BL-46` werden
  über die **wirkliche Bedienoberfläche** geprüft (`ralph.sh`/`harry.sh` gegen
  ein Wegwerf-Repo mit gestubbter CLI), nicht nur auf Bibliotheksebene.

## [2.4.4] — 2026-08-02

**Zwei Kennzahlen, die im Closeout das Falsche behaupteten.**

Beide aus dem Feld (`team-kit_project_platformer`, Architekt-Closeout K3),
beide gefunden beim Nachrechnen des Endstands — nicht von einem Werkzeug.
Kein Rechenfehler: Das Ledger war jedes Mal korrekt, falsch war, was die
Anzeige über die Zahlen **sagte**.

### Fixed

- **`--budget` behauptete „nicht im Gesamt enthalten" — auch dann, wenn die
  Architekten-Zeile sehr wohl enthalten war (`BL-18`).**
  [`entry/team-status.sh`](entry/team-status.sh) druckte den Zusatz
  **unbedingt**, obwohl `team_architekt_stand` zwei Modi hat: Im Modus
  `geschätzt` stammt der Wert aus der A2-Churn-Schätzung und steht in **keiner**
  Ledger-Zeile — der Zusatz stimmt. Im Modus `echt` stammt er aus einer
  **Ledger-Zeile** der laufenden Kaskade, und die summiert
  `team_kontostand_gesamt` mit — der Zusatz ist dann falsch. Der Modus schaltet
  ausgerechnet **beim Kaskaden-Abschluss** um, also genau in dem Moment, in dem
  die Zahl abgelesen und weitergegeben wird. Im Feld: Anzeige „Architekt (echt,
  nicht im Gesamt enthalten): 9.7000" bei „Gesamt: 71.5706" — der beim Wort
  genommene Kontostand wäre **81,27 statt 71,57 USD** gewesen, 13 % zu viel.
  **Neu:** Der Zusatz hängt am Modus (`echt` ⇒ „im Gesamt enthalten"), und die
  Beschriftung nennt den Bezugsrahmen: `Architekt K3 (echt, im Gesamt
  enthalten)`. Denn der Wert gilt für **eine** Kaskade, während jede andere
  Zeile des Blocks lebenslang kumuliert — ohne Rahmen las man 9,70 als
  Lebenssumme des Architekten (real: 37,30). Die Nummer liefert die neue
  `team_architekt_kaskade`; `team_architekt_stand` behält seinen
  Zwei-Felder-Vertrag, an dem `team-status.sh` und drei Testdateien hängen.
- **Dieselbe Einladung zum Doppeladdieren stand im zweiten Block (`BL-18`,
  Nachzug).** Die Momentaufnahme (`./team-status.sh` ohne Argument) zeigte die
  reine A2-Schätzung — „Architekt (geschätzt, A2)" — direkt über
  „Gesamt-Kontostand (inkl. Ledger)". Nach dem Buchen stand dort also eine
  **Schätzung** neben einer Summe, welche die **echte** Zeile bereits enthält,
  und die Beschriftung war modusblind. **Neu:** Beide Ansichten bauen ihre
  Beschriftung aus **einer** Quelle (`status_architekt_zeile`); zwei Anzeigen
  derselben Kennzahl können nicht mehr auseinanderlaufen. Ein eigener Testfall
  hält genau das fest.
- **`--rollen-abschluss` schrieb eine Notiz wortgleich in zwei Zeilen mit
  verschiedener Bedeutung (`BL-19`).** Seit `BL-4` ruft die eine
  Bedienhandlung zwei Verben mit demselben `--notiz` auf: `rollen-abschluss`
  bucht `.team-logs`, `ralph-abschluss` bucht `.ralph-logs`. Ein Text kann aber
  höchstens eine der beiden Zeilen beschreiben — im Feld trug Ralphs Zeile über
  **vier Baustufen** die Notiz „Harry/Marv-Sweeps + Frank HM-6". Das Ledger ist
  die maschinelle Wahrheit für ein kalt startendes Architekt-Ich, und dieses
  Feld ist die **einzige** Prosa-Spur je Zeile. Ein Rückfall obendrein: Genau
  diese Beschwerde stand schon in Feld-`BL-5`, der `BL-4`-Fix hat sie
  strukturell wieder eingebaut.
  **Neu:** [`kosten.py`](team/tools/kosten.py) setzt den Vorspann selbst, aus
  der Zielrolle — `Rollen: …` / `Bau: …`, für projekteigene Rollen deren Name.
  Kein zweiter Bedienparameter: Die Bedienung bleibt einhändig, und ein
  optionales `--notiz-ralph` wäre dieselbe Falle wie das „optional" in `BL-15`
  gewesen — was man setzen *kann*, setzt im Closeout niemand.

### Changed

- Die `Gesamt`-Zeile in `--budget` heißt zur Abgrenzung von der
  kaskadenscharfen Architekt-Zeile jetzt „(Basis + laufend), lebenslang".
- Leseregeln zu beiden Kennzahlen in [`bootstrap/TEAM.md`](bootstrap/TEAM.md)
  und im Architekten-Briefing; Bau-Details als Lehren in
  [`doku/anhang-a.md`](doku/anhang-a.md) A.9. Dabei fiel dort eine seit `BL-5`
  veraltete Aussage auf („ein zweiter Aufruf **ersetzt** die Zeile" — er bricht
  seither ab) und wurde mitkorrigiert.
- Zwei neue Regressionstests (`test_bl18_…`, `test_bl19_…`), beide mit
  gefahrener Gegenprobe. Die Installation fährt jetzt **228** Tests.

## [2.4.3] — 2026-08-02

**Der Guard urteilte ohne Ausgangszustand — und die einzige Verifikation, die
zwischen Doku und Testaufruf schaut, gab es nicht.**

Zwei Entscheide des Strippenziehers, beide gebaut. `BL-16` war der letzte
offene Feld-K2-Befund; `BL-17` kam aus demselben Feld nach.

### Fixed

- **Der Read-Only-Guard schrieb jede schmutzige Datei der laufenden Rolle zu
  (`BL-16`, Ebene 1).** [`team_guard_verify`](team/lib.sh) bildete die
  Verletzerliste aus `git diff --name-only` **plus** `git status --porcelain`
  und hatte **keinen Ausgangszustand**: Sie wusste nicht, was beim Rollenstart
  bereits schmutzig war. Jeder fremde Schreiber — eine parallele Sitzung, eine
  Handänderung, ein abgebrochenes Werkzeug — wurde der Rolle angelastet **und**
  hart zurückgesetzt. Der eigene Kommentar der Funktion („schützt parallele/
  legitime uncommittete Arbeit") galt nur gegenüber dem blanko `reset --hard`,
  das sie ablöste; das chirurgische `git checkout -- <pfad>` zerstört fremde
  Arbeit genauso, nur gezielter.
  **Neu:** `team_guard_begin` hält `TEAM_GUARD_VORHER`, einen Schnappschuss mit
  **Blob-Hashes**. Der Hash ist der Punkt: Ein reiner Pfadabgleich wäre ein
  Freibrief für jede Rolle, die eine ohnehin schmutzige Datei zusätzlich
  verändert. Unverändert ⇒ fremd, kein Rollback, keine Zuschreibung.
  Verändert ⇒ ihre Sache. Bei nicht sauberem Baum warnt `team_guard_begin`
  laut und nennt die Pfade — **warnen statt abbrechen**, weil uncommittete
  Arbeit der Normalfall ist und ein harter Abbruch legitime Läufe erschlüge.
- **Eine Guard-Verletzung kassiert den Übergriff, nicht die Arbeit (`BL-16`,
  Ebene 2).** Bisher übersetzten [`entry/axel.sh`](entry/axel.sh) und
  [`team/redteam.sh`](team/redteam.sh) jeden Übergriff sofort in `RC=1`. Damit
  zählte im Feld eine **fertige, korrekte** Ermittlung als „Aufruf
  fehlgeschlagen" → Stagnationszähler → Lauf gestoppt.
  **Neu:** `team_guard_urteil <rolle> <übergriff> <ergebnis>`. Liegt das
  Ergebnis der Rolle vor — bei Axel Akte **und** Statuswechsel, bei Harry/Marv
  die Sweep-Quittung —, zählt die Runde. Der Grenzübertritt ist zu diesem
  Zeitpunkt bereits chirurgisch zurückgerollt und laut gemeldet; ein
  zusätzlicher Fehlschlag bestraft nur noch das Falsche. Fehlt das Ergebnis,
  bleibt es beim Fehlschlag.
- **Die Guard-Meldung trennt die beiden Fälle jetzt sprachlich.** „**DIESE
  ROLLE** hat die folgenden Pfade geändert" vs. „**NICHT angelastet** (beim
  Rollenstart bereits geändert, seither unverändert)". Im Feld wurde der
  Übergriff zunächst der falschen Rolle zugeschrieben, weil die Pfadliste im
  Log neben ihrem Namen stand — belegt war das nirgends.

### Added

- **Die Verifikationskette darf sich den Erfolg nicht selbst einrichten
  (`BL-17`).** Regel in [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage)
  und [`bootstrap/TEAM.md`](bootstrap/TEAM.md): Jeder Befehl, den die Doku
  einem Menschen nennt, muss in der Verifikation **buchstabengetreu**
  vorkommen — gleiche Argumente, gleiche Umgebung, kein zusätzliches
  `PYTHONPATH`, kein stilles `cd`. Dazu ein **fester Sweep-Schwerpunkt** „Doku
  gegen Verifikation diffen" in den Briefings von Harry und Marv.
  **Warum beides:** Im Feld war der dokumentierte Startbefehl kaputt, während
  der Smoke-Test grün meldete. Fünf Red-Team-Funde derselben Kaskade hatten
  exakt diese Bauart, und **keiner** der Sweeps hat diesen gefunden — die
  Lücke klafft zwischen Doku und Testaufruf, nicht im Code, und ist beim
  Codelesen unsichtbar. Gefunden hat sie der Mensch beim ersten eigenen Start.
  Ein maschineller Diff wurde **verworfen** (stackagnostisch schwer, hohe
  Falschmelderate zu erwarten) — er kommt, wenn ein zweiter Fall dieser Bauart
  auftritt.
- **`test_bl16_guard_zuschreibung.py`** (13 Fälle, gegen ein Wegwerf-Repo und
  mit `set -euo pipefail` wie im Ernstfall) und
  **`test_bl17_doku_gegen_verifikation.py`**. Beide Gegenrichtungen von
  `BL-16` eigens abgesichert: Eine vorab schmutzige Datei, die die Rolle
  **doch** anfasst, bleibt eine Verletzung, und bei sauberem Start urteilt der
  Guard unverändert scharf. Gegenprobe gefahren — mit ausgeschalteter
  Zuschreibung fallen genau zwei Zusicherungen. **214 Testfälle** in 35
  Dateien.
- **Zuschreibungs-Lektion in [`doku/anhang-a.md`](doku/anhang-a.md) A.4**, neben
  der Rollback- und der Staging-Lektion. Die drei zusammen sind die Geschichte
  dieses Guards.

### Bemerkt

- **`BL-17` fand seinen eigenen Fund.** Der Regressionstest schlug beim ersten
  Lauf an: Die Regelphrase stand in der Vorlage über einen Zeilenumbruch
  zerrissen und war damit als zusammenhängende Aussage nicht auffindbar. Genau
  die Sorte Formfehler, die eine Regel unwirksam macht, ohne dass jemand sie
  bemerkt — dasselbe Muster wie die fehlenden Backticks in `BL-15`.

## [2.4.2] — 2026-08-02

**Die ausgelieferte Beutebuch-Vorlage lehrte genau die Falle, die `BL-11` im
Regex behoben hatte.**

`BL-11` (Release 2.3.x) hat `DATEI_RE` beigebracht, per Pytest-Node-ID
referenzierte Dateien zu lesen. Das war die **halbe** Reparatur: Der Extraktor
*konnte* den Pfad seither lesen — die Vorlage erzeugte nur nie einen. Sie nannte
ihn **ohne Backticks** und als **„optional"**, an fünf Stellen in vier Dateien,
in **jeder** frischen Installation. Aus dem Feld zurückgespielt (dort `BL-7`,
`team-kit_project_platformer`), wo derselbe Defekt an einem einzigen Fund
12,00 USD verbrannt hat: 9 Frank-Versuche, 3 Axel-Akten, keine Zeile Code
überlebt — bei grünem Smoke-Test und gültigem Promise, also ohne jedes
Fehlersignal.

### Fixed

- **Die `Reproducer-Test`-Zeile ist Pflichtfeld, der Pfad steht in Backticks
  (`BL-15`).** Zwei voneinander unabhängige Defekte, von denen **keiner allein
  wirkt**: (1) „optional" ⇒ Harry und Marv lassen das Feld leer, Franks neue,
  regelkonform nach der Fund-Nummer benannte Testdatei ist im Fund-Block nie
  referenziert, und `team_diff_beruehrt_fund` rollt jeden regelkonformen Fix
  zurück. (2) Ohne Backticks ⇒ selbst ein *ausgefülltes* Feld bleibt unsichtbar,
  weil `DATEI_RE` ausschließlich Backtick-Pfade liest. Die Prompt-Pflicht allein
  hätte also **nichts** bewirkt.
  **Neu:** Die Zeile wird **immer** gesetzt — auch wenn die Datei noch nicht
  existiert. Sie ist keine Quittung über getane Arbeit, sondern eine
  **Reservierung** des Dateinamens für Frank. Geändert in
  [`bootstrap/beutebuch.md`](bootstrap/beutebuch.md) (Vorlage + Begründungs­block),
  [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage) (Beutezug-Dreisatz
  Schritt 2 + Fund-Format), [`team/prompts/rolle-harry.md`](team/prompts/rolle-harry.md),
  [`team/prompts/rolle-marv.md`](team/prompts/rolle-marv.md).
- **Der Guard bleibt unangetastet scharf.** Gewählt wurde die Prompt-Pflicht,
  nicht die Guard-Lockerung (Strippenzieher-Entscheid im Feld, 2026-08-02).
  Begründung aus dem Feld: Beim Folgefund setzte Frank die Zeile **von sich
  aus** — dem Muster des vorigen Fundblocks folgend — und kam in **einem**
  Versuch durch. Das Muster trägt, sobald es sichtbar ist; es braucht nur eine
  verbindliche Regel statt Nachahmung.
- **Sechste Stelle, im Feld nicht sichtbar:** `CLAUDE.md.vorlage` schrieb den
  Pfad als `{{TEST_ORDNER}}/…`. Der Platzhalter trägt seinen Schrägstrich
  bereits, das expandierte also zu `tests//…`. Im Feld stand dort die schon
  substituierte Fassung, weshalb der Fund von dort nur fünf Stellen nennen
  konnte.

### Added

- **`test_bl15_reproducer_zeile_ankertauglich.py`** — der Regressionstest, den
  der Feldbefund ausdrücklich empfohlen hat und der diesen Fund verhindert
  hätte: Er nimmt die **wirklich ausgelieferte** Zeile aus allen vier Quellen,
  füllt sie so aus, wie die Vorlage es ansagt, und lässt `DATEI_RE` darauf los.
  Er läuft in beiden Ablagen — im Kit gegen `bootstrap/`, im installierten
  Projekt gegen die substituierten Zieldateien — und prüft zusätzlich, dass die
  Zeile überhaupt noch existiert und nicht wieder als „optional" markiert ist.
  Gegenprobe gefahren: Mit der alten Zeile schlagen genau zwei Zusicherungen
  fehl. **197 Testfälle** in 33 Dateien.

### Bemerkt

- **`install.sh` kompiliert die Tests, die es ausliefert.** Der Installer fährt
  zum Abschluss `pytest` gegen die frische Installation und legt dabei
  `.pyc`-Dateien an. `kit-test.sh` Stufe 3 durchsucht danach **alles** im
  Zielbaum nach übrig gebliebenen Installer-Platzhaltern — auch den Bytecode.
  Eine Testdatei, die einen Platzhalter als String-Literal führt, meldet sich
  damit selbst als Fund. Zusammensetzen hilft nicht: CPython faltet konstante
  Konkatenation beim Kompilieren. Der neue Test ersetzt Platzhalter deshalb
  über ein Muster, nicht über ein Literal.
- **`BL-17` neu im Backlog**, aus dem Feld nachgetragen (dort `BL-10`): *Die
  Verifikationskette darf sich den Erfolg nicht selbst einrichten.* Der
  dokumentierte Startbefehl war kaputt, während der Smoke-Test grün meldete —
  weil Smoke-Test und `pytest.ini` still ein `PYTHONPATH` dazusetzten, das es
  beim Anwender nie gibt. **Fünf** Red-Team-Funde derselben Kaskade hatten
  exakt diese Bauart, und **keiner** der Sweeps hat diesen gefunden: Harry und
  Marv lesen den Code, die Lücke klafft aber zwischen **Doku und Testaufruf**.
  Braucht einen Entscheid, in welcher Form die Regel greift.

## [2.4.1] — 2026-08-01

**Zwei Fehler in `ledger-pruefen`, gefunden beim ersten Einsatz auf einem
fremden, gewachsenen Ledger.**

Beim Rückspielen der Kit-Fixes in das Ursprungsprojekt `website-maxron-de` —
den Ahnherrn des Kits, der das flache Vor-Kit-Layout trägt und deshalb **kein**
`install.sh --update` annimmt — lief `ledger-pruefen` erstmals gegen 67
gewachsene Ledger-Zeilen aus 22 Kaskaden. Es meldete drei Warnungen. **Keine
davon war echt**, und keine war je auflösbar. Ein Werkzeug, das bei jedem Lauf
rot ist, erzieht genau zu dem Wegsehen, gegen das seine zwei Schweregrade
gebaut wurden (Skizze D, Frage 2).

### Fixed

- **Eine Rohquelle kann mehrere Ledger-Rollen speisen (`BL-13`).** `P3` bildete
  Archivordner 1:1 auf **eine** Rolle ab (`roles ↔ .team-logs`). Das ist
  falsch, sobald ein Projekt eine weitere Rolle **separat** bucht — und genau
  dafür existiert `akteur-abschluss --rolle <X>`. Real schreiben
  [`team/redteam.sh`](team/redteam.sh), [`entry/frank.sh`](entry/frank.sh),
  [`entry/axel.sh`](entry/axel.sh) und
  [`entry/vollautomatik.sh`](entry/vollautomatik.sh) **alle** nach
  `.team-logs`, während der Ahnherr Franks Out-of-Loop-Arbeit als eigene
  `frank`-Zeile bucht. `P3` meldete dieses Geld als „archiviert, aber nie
  gebucht" — strukturell unauflösbar, denn nachbuchen kann man nichts, was
  bereits gebucht **ist**.
  **Neu:** Die Rollenmenge je Ordner wird aus dem Ledger **abgeleitet** statt
  festverdrahtet. `.ralph-logs` gehört Ralph allein, `.team-logs` jeder
  weiteren Rolle mit Rohlog. `architekt` bleibt ausdrücklich außen vor
  (`LEDGER_OHNE_ROHLOG`): Diese Zeile ist eine gemessene Schätzung aus dem
  Transkript, ihr entspricht keine Log-Datei — im Ahnherrn trägt sie 275 USD
  und hätte jede echte Untergebuchung maskiert. Der Befund **nennt die
  gezählten Rollen**, damit ein Mensch die Zahl nachrechnen kann; genau dieses
  Nachrechnen hat `BL-1`, `BL-4` und `BL-5` überhaupt erst gefunden.
- **Benannte Kaskaden sind Out-of-Loop-Buchungen (`BL-14`).** Die `P1`-Regel
  „`roles` ohne `ralph` ⇒ Warnung" stimmt für **nummerierte** Kaskaden: Wo
  gesweept wurde, wurde auch gebaut. Für benannte (`post-20`,
  `roles-post-k13`) gilt sie nicht — das sind Fixserien **nach** dem Lauf, in
  denen Ralph gar nicht gebaut hat. Die fehlende `ralph`-Zeile ist dort
  korrekt, die Warnung dauerhaft unauflösbar, und sie erschien bei **jedem**
  `--budget`. **Neu:** Warnung nur bei `kaskade.isdigit()`, sonst ein Hinweis,
  der den Grund nennt.

### Added

- **6 neue Testfälle** in `test_bl13_ledger_pruefen.py`, darunter beide
  Gegenrichtungen: Eine echte Untergebuchung muss trotz der erweiterten
  Rollenmenge weiterhin anschlagen (mit der echten `BL-4`-Zahl 2,1621 USD),
  und bei einer **nummerierten** Kaskade bleibt die fehlende `ralph`-Zeile
  eine Warnung. Dazu ein Schutzwächter, dass die `architekt`-Zeile keine
  Rohlogs deckt. **182 Testfälle** in 32 Dateien.

### Bemerkt

- **Der Rückkanal lief bisher nur in eine Richtung.** Feld → Kit war geregelt
  (Skizze C), Kit → **Ahnherr** nicht. `BL-11` lag deshalb zwei Kaskaden im
  Feld, bevor es ins Kit kam — und im Ursprungsprojekt lag derselbe Fehler bis
  heute. Dort sind die drei fehlenden Fixes jetzt einzeln nachgezogen
  (`BL-57`/`BL-58`/`BL-59` im dortigen Backlog); eine Migration auf das
  Kit-Layout wäre 531 Pfadverweise in 61 Dateien und wurde bewusst **nicht**
  gemacht (Strippenzieher-Entscheid 2026-08-01).

## [2.4.0] — 2026-08-01

**Das Ledger prüft jetzt seine eigene Vollständigkeit** (Roadmap-Skizze D).

### Added
- **`./team-status.sh --ledger-pruefen` / `kosten.py ledger-pruefen`.** Drei
  Prüfungen: (1) trägt jede gelaufene Kaskade eine Zeile je Quelle —
  `ralph`/`roles`/`architekt`? (2) liegen unarchivierte Logs herum, obwohl die
  Kaskade schon gebucht ist? (3) **ergeben die archivierten Rohlogs mehr, als
  im Ledger steht?**
  Nur die dritte Frage zieht ihre Kennzahl aus einer **anderen** Quelle als das
  Geprüfte — und genau das fehlte bisher: `BL-1`, `BL-4` und `BL-5` sind alle
  drei **nicht** durch ein Werkzeug aufgefallen, sondern dadurch, dass ein
  Mensch den gedruckten Bericht neben das Ledger hielt. Dreimal dasselbe
  Muster: Ein Bericht, der seine Kennzahl aus derselben Quelle zieht wie der
  Fehler, bestätigt ihn, statt ihn zu zeigen.
  Exit `4` bei Warnbefunden (`1` bleibt dem Bedienfehler vorbehalten), zwei
  Schweregrade (`warnung` = sehr wahrscheinlich verlorenes Geld, `hinweis` =
  kann legitim sein). Bewusst **kein** hartes Gate im Closeout: Eine Kaskade
  mit legitim fehlender Zeile könnte sonst nicht abschließen, und ein Gate,
  das man regelmäßig umgeht, ist wirkungslos. Stattdessen laufen die Warnungen
  bei jedem `--budget` ungefragt mit.
- **16 neue Testfälle** (`test_bl13_ledger_pruefen.py`), darunter `BL-4` und
  `BL-5` mit ihren **echten Feldzahlen** (2,1621 USD nie gebucht bzw. 1,0969
  USD überschrieben) — beide schlagen an. Gegenprobe für alle drei Prüfungen
  einzeln gefahren. **176 Testfälle** in 32 Dateien.

### Entschieden
- **Der Rohlog-Vergleich läuft je Quelle, nicht je Kaskade.** Die Skizze wollte
  Zeile gegen *ihre* Rohlogs halten; das ist mit der heutigen Ablage nicht
  ehrlich beantwortbar, weil Log-Dateinamen keine Kaskadennummer tragen
  (`stufe-<n>-<ts>.json`, `harry-<ts>.json`) und das Archiv **ein** flacher
  Ordner je Quelle ist. Zuordnen ließe sich nur über mtime-Fenster — in der
  Kostenmechanik wird nicht geraten. Ein Archiv je Kaskade
  (`archiv/kaskade-<n>/`) wäre sauberer gewesen, hätte aber `lauf_kosten()` in
  `vollautomatik.sh` gebrochen, das `.ralph-logs/archiv` **nicht-rekursiv**
  globbt und den Pro-Lauf-Deckel auch gegen bereits weggeräumtes Geld misst
  (`BL-55`). Archivordner ↔ Ledger-Rolle entsprechen einander dagegen
  eindeutig — der Vergleich braucht damit **keine** Zuordnung und hätte `BL-4`
  wie `BL-5` trotzdem gefunden.

### Changed
- Closeout-Regel in `CLAUDE.md.vorlage`, `TEAM.md` und dem Architekten-Briefing
  nachgezogen: Der Abschluss wird **geprüft, nicht geglaubt**; ein stehender
  Warnbefund gehört samt Begründung ins Abschluss-Doc.

## [2.3.2] — 2026-08-01

**Der erste echte `--update`-Einsatz hat zwei Löcher aufgedeckt — beide im
Update selbst.**

### Fixed
- **`--update` löschte projekteigene Tests und nahm lokale Fixes still zurück
  (`BL-12`).** Ein pauschales `rm team/tests/test_*.py` sollte umbenannte
  Kit-Tests einer Altversion entfernen. Im Feld löschte es einen **vom Projekt
  geschriebenen** Infrastruktur-Test, und im selben Lauf wurde
  `team/tools/beutebuch.py` mit der älteren Kit-Fassung überschrieben — samt
  einem lokalen Fix, der real 12,00 USD gekostet hatte. Die Annahme
  „`team/tests/` gehört exklusiv dem Kit" ist falsch, sobald ein Projekt eine
  Lücke im Team selbst schließt.
  **Neu:** `--update` löscht **nichts** mehr. Tests, die das Kit nicht kennt,
  bleiben liegen und werden gemeldet; jede ersetzte Infrastruktur-Datei, die
  vorher von der Kit-Fassung abwich, wird mit `git diff`-Befehl ausgewiesen —
  mit dem ausdrücklichen Hinweis, einen darin steckenden eigenen Fix erst ins
  Kit zurückzuspielen und dann erneut zu updaten.

### Added
- **`BL-11` aus dem Feld zurückgeholt:** `DATEI_RE` in `beutebuch.py` erkennt
  jetzt Pytest-Node-IDs (`datei.py::test_x[param]`) und extrahiert den reinen
  Dateipfad. Vorher galt eine so referenzierte Datei still als „nicht
  referenziert", der Substanz-Anker verwarf jeden Fix, der nur sie berührte,
  und Frank lief in einen endlosen Rollback-Zyklus (real 12,00 USD an `HM-4`).
  Fix und Reproducer stammen aus dem Feldprojekt und lagen dort **zwei
  Kaskaden lang** — genau das Loch, das der Rückkanal schließen soll.
- Drei weitere Zusicherungen in `kit-test.sh` Stufe 5 (projekteigener Test
  überlebt, wird gemeldet, abweichende Infrastruktur wird gemeldet).
- **160 Testfälle** in 31 Dateien.

## [2.3.1] — 2026-08-01

**Sofortnachtrag zu 2.3.0, im Feld erzwungen.**

### Fixed
- **`install.sh --update` lief in einen aktiven Lauf hinein (`BL-10`).** Beim
  ersten Einsatz von `--update` auf ein Feldprojekt lief dort noch
  `vollautomatik.sh`. Das Update legte uncommittete Dateien in `team/` ab; der
  unmittelbar folgende Axel-Lauf (read-only, Whitelist nur `plans/`) wertete
  sie als **Guard-Verletzung**, rollte sie zurück und buchte seine Runde als
  Fehlschlag — obwohl er seine Ermittlungsakte geliefert hatte. Dritte
  Stagnation in Folge, **Lauf gestoppt**, Update spurlos weg.
  Der Guard hat dabei genau das getan, wofür er gebaut ist, und die
  Projektdaten blieben unversehrt. Gefehlt hat die Sperre im Installer:
  `--update` prüft jetzt per `flock -n`, ob `.team-loop.lock` **gehalten** wird
  (nicht bloß existiert), bricht dann mit Exit 2 ab, warnt zusätzlich vor einem
  schmutzigen Arbeitsbaum und macht das anschließende Committen zur
  ausdrücklichen Pflicht — sonst räumt der nächste Read-Only-Lauf das Update
  weg.

## [2.3.0] — 2026-08-01

**Die Kostenerfassung stimmt wieder, und das Kit prüft sich selbst.** Erntelauf
der ersten Feldkaskade: drei Fehler kamen aus dem Feld zurück (`BL-4`, `BL-5`,
`BL-9`), drei fielen beim Aufräumen auf (`BL-6`, `BL-7`, `BL-8`).

### Fixed
- **Ralphs Baukosten landeten in keiner Ledger-Zeile (`BL-4`).**
  `--rollen-abschluss` ledgerte per Definition nur `.team-logs`
  (Harry/Marv/Frank/Axel). Für `.ralph-logs` gab es zwar den Bash-Helfer
  `team_logs_archivieren()`, aber im **gesamten Kit keinen Aufrufer**. Der
  Gesamtstand stimmte nur, solange `.ralph-logs/` liegen blieb — und der Ordner
  steht per `gitignore.fragment` in `.gitignore`. Ein frischer Clone verlor
  damit die **gesamte Bau-Kostenhistorie**, also genau das, wogegen das Ledger
  gebaut wurde (im Feld: 2,1621 von 9,4204 USD).
  **Neu:** `kosten.py ralph-abschluss` — derselbe Mechanismus mit `.ralph-logs`
  als Quelle und `rolle=ralph` als Zielzeile. `./team-status.sh
  --rollen-abschluss` ruft **beide** Verben auf: **eine** Bedienhandlung,
  **zwei** getrennte Ledger-Zeilen. Bewusst keine Sammelzeile — die Trennung
  Bau ↔ Sweep/Fix ist die Kennzahl, an der im Feld überhaupt auffiel, dass
  Ralph fehlte. Bricht ein Verb ab, wird das andere trotzdem versucht.
  Der Fehler war zur Hälfte ein Dokumentationsfehler: Die Closeout-Pflicht in
  `CLAUDE.md.vorlage`, `TEAM.md` und dem Architekten-Briefing nannte Ralph
  nirgends. Alle drei Stellen sind nachgezogen.
- **`--rollen-abschluss` löschte bei einem zweiten Aufruf still Geld aus dem
  Ledger (`BL-5`).** Der gebuchte Wert entsteht aus den **noch nicht
  archivierten** Logs, und ein Abschluss archiviert die gezählten Logs
  anschließend. Aufeinanderfolgende Aufrufe sehen deshalb **disjunkte** Mengen —
  wer nach dem Closeout noch eine Rolle laufen ließ (im Feld: Frank mit drei
  Fixes) und erneut abschloss, bekam einen *kleineren* Wert, der den größeren
  **ersetzte**. Real eingetreten: 1,0969 USD verschwanden hinter 2,4114 USD,
  Sollwert wäre die Summe 3,5083 gewesen; die Korrektur ging nur von Hand.
  Für disjunkte Mengen ist **Addieren** die richtige Verknüpfung — das
  Ersetzen stammte aus `akteur_abschluss()`, wo der Aufrufer einen absoluten,
  extern gemessenen Wert übergibt und Ersetzen deshalb korrekt ist.
  **Neu:** Steht für die Kaskade bereits eine `roles`-Zeile, **bricht der
  Aufruf ab** und nennt Alt-, Neu- und Summenwert; `--addieren` (Nachlauf) und
  `--ersetzen` (Korrektur einer falschen Altzeile) sind die beiden
  ausdrücklichen Wege. Automatisch addiert wird bewusst **nicht**: Ohne
  `--archivieren` zählen zwei Aufrufe dieselben Logs, dann wäre Addieren eine
  Doppelbuchung — die Entscheidung gehört dem Menschen, nicht der Heuristik.
  Bei Abbruch wird **nicht archiviert**, die Logs bleiben also greifbar.
  Der Normalfall (ein Closeout je Kaskade) läuft unverändert ohne jedes Flag.
- `_ledger_zeile_setzen()` bekam dafür einen optionalen `merge_fn`-Haken, der
  **innerhalb** des Ledger-Locks und **vor** jedem Schreibzugriff läuft.
  `akteur_abschluss()` ist unberührt.
- **Zwei Fehler im obigen Fix selbst**, gefunden bei einem manuellen
  Durchlauf gegen eine echte Installation — **nicht** von den 149 Tests:
  (1) `merge_fn` schrieb die Rolle hart als `roles`; ein `--addieren` auf die
  `ralph`-Zeile hätte sie in eine zweite `roles`-Zeile verwandelt und die
  Baukosten erneut unsichtbar gemacht — der `BL-4`-Fehler eine Ebene tiefer,
  erzeugt vom `BL-5`-Fix. (2) Beim Nachlauf **einer** Rolle ist die andere
  Quelle regulär leer; `--addieren` buchte dort `+0,0000` und überschrieb dabei
  Datum und Notiz der bestehenden Zeile mit dem Text des fremden Nachlaufs.
  Beides behoben und mit je einem Regressionstest belegt.
  **Lehre:** Die Tests prüften je Rolle nur einen Modus — die Kreuzkombination
  (andere Rolle × anderer Modus) blieb blind. Ein einziger Durchlauf durch die
  echte Bedienoberfläche fand, was 149 grüne Tests nicht fanden.
- **`README.md`, Abschnitt „Grenzen", war überholt (`BL-7`).** Frank ist
  inzwischen scharf gelaufen (drei Fixes im Feld), Axel weiterhin nicht — und
  die Fixphase einer `vollautomatik.sh` hat noch nie in **einem** Durchlauf
  durchgetragen. Präzisiert statt gestrichen. Zahlen (Dateien, Tests,
  Zeilenumfänge) auf den Ist-Stand gebracht.

- **`--force` war die einzige dokumentierte Update-Option — und
  datenvernichtend (`BL-8`).** Ohne Flag ändert `install.sh` an einem
  bestehenden Projekt gar nichts, mit `--force` überschreibt er auch die
  Projektdaten. Empirisch nachgestellt: `.budget-ledger` geleert,
  `.ralph-state` von `5` auf `1` zurück, Beutebuch-Fund weg, `TEAM_SMOKE_TEST`
  aus `team.config.sh` verschwunden. Ein Feldprojekt konnte die Fixes dieses
  Releases damit gar nicht bekommen, ohne seine Geschichte zu verlieren.
- **Feldprojekte führten eine „T.E.A.M."-Domäne, die strukturell null ist
  (`BL-9`).** Der Kontostand zeigte einen Domänenblock mit einer hart auf die
  Domäne `team` verdrahteten Zeile. In einem Feldprojekt wird am Team nicht
  entwickelt — Funde gehen ins Kit zurück und werden dort verbucht —, die
  Zeile war also immer `0.0000`. Eine Kennzahl, die nie etwas zeigt, erzieht
  dazu, den ganzen Block zu überlesen. Die Verdrahtung war zudem für **jede**
  Konfiguration ohne `team` falsch (z. B. `backend frontend`).
  **Neu:** Installer-Default ist **eine** Domäne (`produkt`); der Block
  erscheint nur bei mehreren und listet dann **jede** konfigurierte Domäne.

### Added
- **`install.sh --update`** — der sichere Weg auf eine neue Kit-Version. Fasst
  nur die Infrastruktur an (Entrypoints außer `team.config.sh`, `team/lib.sh`,
  `team/redteam.sh`, `team/tools/`, `team/prompts/`, `team/tests/`) und lässt
  Ledger, Kaskadenstand, Beutebuch, CHANGELOG, `plans/`, `CLAUDE.md` und
  `team.config.sh` unberührt. Liest die Projektwerte aus der **installierten**
  `team.config.sh` (sonst bekämen die Briefings die falschen Pfade und damit
  eine falsche Guard-Grenze), rettet den Commit-Entscheid aus dem bisherigen
  Architekten-Briefing, entfernt Testdateien entfallener Versionen und meldet
  am Ende, welche Doku-Dateien von der Kit-Fassung abweichen — die **Regeln**
  zieht der Mensch nach, sonst läuft die Doku der Mechanik hinterher (das war
  die Hälfte von `BL-4`).
- `kit-test.sh` prüft den Update-Pfad als **Stufe 5**: Es macht das
  Wegwerf-Projekt künstlich „lebendig" (Ledger, Kaskadenstand, Beutebuch-Fund,
  eigener Smoke-Test, Alttest einer Vorversion) und weist nach, dass `--update`
  davon nichts anfasst.
- `team/tests/test_bl4_ralph_abschluss.py` — vier Prüfungen, darunter die
  entscheidende über die Bedienoberfläche: **ein** `--rollen-abschluss` muss
  **beide** Zeilen erzeugen und beide Log-Ordner rotieren. Gegenprobe gefahren:
  Mit dem alten Ein-Verb-Aufruf ist genau dieser Test rot.
- `team/tests/test_bl5_rollen_abschluss_bestand.py` — sieben Prüfungen, darunter
  das **Feldszenario mit den echten Zahlen** (1,0969 → Frank-Nachlauf 2,4114 →
  3,5083) inklusive Archivierung. Gegenprobe gefahren: Mit dem alten Verhalten
  sind genau die beiden Kernprüfungen rot.
- **153 Testfälle** in 30 Dateien (im installierten Projekt).
- **`kit-test.sh` — das Kit prüft sich jetzt selbst (`BL-6`).** Bisher gab es
  dafür keinen Befehl: `pytest team/tests` schlägt im Kit-Repo mit **17 von 138**
  Tests fehl, weil die Tests die **installierte** Ablage voraussetzen
  (Entrypoints in der Wurzel statt unter `entry/`). Kein einziger dieser
  Fehlschläge war ein echter Fund — aber sie machten den einzigen vorhandenen
  Testlauf unbrauchbar, und damit war jeder im Kit committete Fix bis zur
  nächsten Feldinstallation ungeprüft. **Genau so ging `BL-1` durch drei
  Releases.**
  `./kit-test.sh` installiert das Kit nicht-interaktiv in ein frisches
  `mktemp`-Git-Repo, sucht ungefüllte `{{PLATZHALTER}}`, committet wie in
  `TEAM.md` vorgeschrieben und fährt dort `./team-test.sh` — die Tests laufen
  also dort, wo sie gelten. Der Installer wird dabei mitgeprüft. Exit-Code wird
  durchgereicht (Gegenprobe gefahren: erzwungener Fehlschlag ergibt Exit 5),
  `--behalten` lässt das Wegwerf-Repo zur Fehlersuche stehen. Ruft keine
  Agenten-CLI auf und kostet daher nichts.

## [2.2.1] — 2026-08-01

**Die Fixphase war in jeder Installation tot.** Erster Fund aus einem
Feldprojekt zurück ins Kit (`team-kit_project_platformer`, Kaskade 1).

### Fixed
- **`team/tools/beutebuch.py` löste die Projektwurzel eine Ebene zu hoch auf.**
  Die Datei liegt in `team/tools/`, also zwei Ebenen unter der Wurzel;
  `parent.parent` ergab `team/` und damit den Pfad `team/plans/beutebuch.md` —
  eine Datei, die es nie gibt. Weil `_lies_zeilen()` für eine fehlende Datei
  eine leere Liste liefert **statt zu scheitern**, meldete das Werkzeug ruhig
  „keine Funde": `first` gab Exit 1 zurück, `frank.sh` schloss daraus „nichts
  zu tun", und `vollautomatik.sh` beendete die Fixphase in Runde 1 — mit drei
  offenen Funden im Buch. Der gedruckte Abschlussbericht bestätigte den Fehler
  („keine Funde"), weil er dieselbe kaputte Quelle liest.
  **Betroffen war jede mit 2.0.0–2.2.0 installierte Instanz**: Red Team schreibt
  Funde, Frank sieht sie nie, niemand bemerkt es — der Lauf endet grün.

### Added
- `team/tests/test_bl1_beutebuch_repo_root.py` — drei Prüfungen: Default-Pfade
  zeigen auf die Wurzel, ein aus fremdem Arbeitsverzeichnis gestarteter
  `list`-Aufruf gegen ein Miniatur-Projekt findet den Fund, und im
  installierten Projekt trifft der Default eine existierende Datei
  (übersprungen im Kit-Repo, das kein `plans/` hat).
- `team/tests/test_bl3_werkzeug_default_pfade.py` — schließt die **Ursache**,
  dass der Fehler durch 132 grüne Tests rutschte: Sämtliche Werkzeug-Tests
  arbeiteten mit `--pfad` auf Fixtures, der Default-Pfad war ungeprüft.
  Prüft jetzt zusätzlich, dass **jeder Entrypoint ins Skriptverzeichnis
  wechselt** — die bislang nirgends festgehaltene Invariante, auf der die
  arbeitsverzeichnis-relativen Pfade von `kosten.py` ruhen.
- **138 Testfälle** gesamt (im installierten Projekt).

### Audit
- `kosten.py` hat den Fehler **nicht**: es leitet keine Pfade aus `__file__` ab,
  sondern hält sie arbeitsverzeichnis-relativ (`.budget-ledger`). Korrekt —
  aber nur, solange die `cd`-Invariante gilt, die jetzt getestet wird. Wer die
  Pfade dort „vereinheitlicht", muss beide Tests bewusst mitziehen.

## [2.2.0] — 2026-08-01

**Erster scharfer Lauf — das Kit ist verifiziert, nicht nur geprüft.**

### Added
- **`TEAM.md`** — der menschliche Einstiegspunkt, bisher die letzte Lücke.
  Beim Abnahmegespräch fiel auf: Die teuerste Warnung des Kits („vor dem ersten
  Guard-Lauf committen") stand **nur in der Terminal-Ausgabe des Installers** —
  und die scrollt weg. Exakt der Fehler, den Planungsregel 5 für den
  Abschlussbericht behebt. `TEAM.md` liegt jetzt im Projekt und im Git:
  Guard-Warnung ganz oben, Rollenübersicht, Kaskaden-Ablauf, Befehlstabelle,
  **Exit-Code-Tabelle** (42 ist kein Absturz), Ablageübersicht und eine
  Fehlersuch-Tabelle.
- Fünf Regressionstests dafür (`test_team_md_bedienanleitung.py`): TEAM.md
  existiert, Guard-Warnung steht im Kopfbereich, Exit-Codes erklärt, Closeout
  als Pflicht benannt, keine offenen Platzhalter. **132 Testfälle** gesamt.
- Installer-Abschlussmeldung verweist zuerst auf `TEAM.md`, mit dem Hinweis,
  dass die Terminal-Ausgabe wegscrollt und die Datei bleibt.

### Verified — scharfer Erstlauf in einem Wegwerf-Projekt
Erstmals mit **echten CLI-Aufrufen** statt Fixtures:
- **Ralph**: Auth-Auflösung (abo) → realer Aufruf → Code gebaut → Smoke-Test
  grün → genau ein `feat(stufe1)`-Commit → Promise erkannt → State auf 2 →
  `RALPH_CAP` respektiert → sauberer Exit 0. **0,2728 USD.**
- **Harry** (Red Team, read-only): realer Sweep über die Historie, Exit 0,
  State auf HEAD gesetzt, **Produktivcode nachweislich unangetastet**.
  **0,4751 USD.**
- **Read-Only-Guard Linie 2 belegt**: Das Log enthält **zwei
  `permission_denials`** — die `--allowedTools`-Allowlist hat zwei
  Bash-Aufrufe von Harry real verweigert. Kein `is_error`.
- **Kostenerfassung**: Ledger und `--budget` weisen 0,7479 USD als
  Abo-Gegenwert aus, korrekt getrennt von real abgerechneten API-Kosten.

Damit ist die Kette Konfiguration → Briefing → `team_claude` → Auth →
Promise-Auswertung → Budget-Check → State-Fortschritt → Guard → Kostenlog
**durchgängig unter echten Bedingungen belegt**.

## [2.1.0] — 2026-08-01

Erstlauf-Anleitung in die Artefakte geschrieben. Sie existierte bisher nur als
mündliche Empfehlung — ein kalt startender Architekt in einem frischen Projekt
hätte sie nicht gekannt. Dieselbe Lehre wie bei Planungsregel 5: Was nicht im
Git steht, existiert für die nächste Instanz nicht.

### Added
- **`rolle-architekt.md`, Abschnitt „Die erste Kaskade eines Projekts"** — vier
  Sonderregeln: Smoke-Test hat Vorrang vor jedem Feature; erste Kaskade auf
  drei bis fünf Stufen begrenzen; `BUDGET_EMPFEHLUNG_USD` konservativ, aber
  nicht knauserig (ein zu tiefer Deckel vervielfacht die Kosten, `HM-32`);
  nach dem Erstlauf den Bauweg ehrlich bewerten.
- **`bootstrap/roadmap-skizzen.md`** ist nicht mehr leer, sondern bringt
  „Skizze 1: Verifikationsfähigkeit herstellen" mit. Sie zeigt über den
  gefüllten `{{SMOKE_TEST}}`-Platzhalter selbst an, ob sie noch gebraucht wird,
  und darf gestrichen werden, sobald der Befehl steht.
- Installer-Abschlussmeldung nennt `TEAM_BUDGET_USD=15` für den Erstlauf und
  verweist ohne Smoke-Test ausdrücklich auf Skizze 1.

## [2.0.0] — 2026-08-01

**Sprach- und stackagnostisch.** Version 1.0.0 setzte an mehreren Stellen still
den Stack des Ursprungsprojekts voraus. Diese Fassung trennt Team-Infrastruktur
und Projekt sauber — verifiziert in Go-, Rust- und PHP-Projektstrukturen.

### Changed — Breaking
- **Neues Layout.** Entrypoints bleiben in der Repo-Wurzel (`./vollautomatik.sh`
  usw. — die Feld-Ablagekonvention), alles Aufgerufene liegt jetzt unter
  `team/`: `team/lib.sh`, `team/redteam.sh`, `team/tools/`, `team/prompts/`,
  `team/tests/`. **Das Kit legt nichts mehr in `scripts/` oder im Test-Ordner
  des Projekts ab** — diese Ordner gehören dem Projekt.
- **Domänen sind projektdefiniert.** `kosten.py` erzwang die Werte `website`
  und `team` an drei Stellen; in einem fremden Projekt war damit keine
  sinnvolle Kostentrennung möglich. Jetzt konfigurierbar über `TEAM_DOMAENEN`
  in `team.config.sh` (Default `produkt team`). **Der Lesepfad validiert nicht
  mehr**: historische Ledger-Zeilen mit heute unbekannten Domänen bleiben
  filterbar; validiert wird nur beim Schreiben.
- **Interview auf sieben Fragen**: Domänen und Commit-Regel des Architekten
  kommen dazu. Letztere stand in der `CLAUDE.md` bisher als offenes
  Entweder-oder.

### Fixed
- **Die Rollen-Briefings waren nicht parametrisiert.** Sie wurden in 1.0.0
  wörtlich übernommen und nannten deshalb `site/**` als Guard-Grenze und
  `python3 scripts/smoke_test.py` als Smoke-Test — in einem fremden Projekt
  bekamen Harry, Marv und Axel damit die **falsche Grenze** genannt und Ralph
  einen Befehl, den es nicht gibt. Die Briefings sind Prompts und werden jetzt
  wie alles andere beim Installieren gefüllt.
- `install.sh` prüfte im Selbsttest noch `scripts/*.py` und meldete deshalb
  immer „Python-Werkzeuge fehlerhaft" (Exit 1 trotz erfolgreicher Installation).
- `.gitignore`-Fragment brachte `__pycache__/` und `.pytest_cache/` global mit;
  jetzt auf `team/**` eingegrenzt.

### Added
- **`team/prompts/rolle-architekt.md`** — das sechste Briefing fehlte, weil der
  Architekt interaktiv läuft und `team_briefing` nie braucht. Für den Trigger
  „Du bist unser Architekt" gab es damit nichts Kompaktes: jetzt Auftrag,
  Grenze, Planungs-Dreisatz, Closeout-Pflicht und Commit-Regel auf einer Seite.
- **`team-test.sh`** — führt die Team-Regressionstests getrennt vom Testlauf
  des Projekts aus. Dein Testbefehl bleibt `TEAM_SMOKE_TEST`.
- Abschlussmeldung des Installers nennt jetzt den **Kostenabschluss nach dem
  Lauf** — ohne ihn bleiben die Architekt-Kosten strukturell unerfasst.

### Tests
- 25 Testdateien, **127 Testfälle**, grün in allen drei geprüften Stacks.
- Angepasst für den generischen Einsatz: Fixtures auf das `team/`-Layout,
  Domänen-Literale durch den konfigurierten Wert ersetzt, Guard-Grenze im
  Briefing-Test aus `team.config.sh` gelesen statt fest erwartet, Lesepfad-Test
  auf den neuen Vertrag umgestellt.

## [1.0.0] — 2026-08-01

Erste Fassung. Der Code stammt aus `website-maxron-de` (22 Kaskaden scharf
gelaufen, 2026-07-10 bis 2026-08-01) und wurde übernommen, nicht neu geschrieben.

### Added
- `install.sh` — idempotenter Installer, fünf Fragen, Selbsttest am Ende
- `kern/team.config.sh` — alle Projektwerte an einer Stelle, von `team-lib.sh`
  gesourct; Ordnerpfade werden zentral auf genau einen Schrägstrich normalisiert
- `bootstrap/` — CLAUDE.md-Vorlage (aus der LLM-Wiki-Vorlage erzeugt, ohne
  Aufnahme-Interview, Platzhalter gefüllt), CHANGELOG mit leerem `[Unreleased]`,
  Beutebuch **mit Vorlage-Block**, Roadmap, Backlog, Ledger, `.gitignore`-Fragment
- 25 Regressionstests der Team-Infrastruktur (127 Testfälle)

### Changed — gegenüber dem Feldprojekt
- **Parametrisierung**: 32 harte Projektbezüge in `ralph.sh`, `frank.sh`,
  `axel.sh`, `redteam.sh` lesen jetzt aus `team.config.sh` statt `site/` und
  `python3 scripts/smoke_test.py` fest zu verdrahten. `team-lib.sh`, `kosten.py`,
  `beutebuch.py`, `vollautomatik.sh`, `halbautomatik.sh` und `team-status.sh`
  waren bereits projektfrei und blieben **wörtlich unverändert**.
- Neue Helfer in `team-lib.sh`: `team_allowed_tools <rolle>` baut die
  Werkzeug-Allowlist aus der Konfiguration; `SMOKE_ZEILE`/`SMOKE_SUFFIX` machen
  einen fehlenden Smoke-Test im Prompt sichtbar, statt ihn still zu übergehen.
- `tests/test_bl29_ledger_domaene_rolle.py` — die Prüfung „Ledgersumme > 0"
  überspringt ein leeres Ledger. In einem frischen Projekt ist es leer; sobald
  die erste Kaskade geledgert ist, greift die volle Prüfung wieder.
- `tests/test_bl55_kostenmessung.py` — prüft die BL-55-Regel jetzt inhaltlich
  (Closeout + Verbot + Stufenbezug) statt einen wörtlichen Satz der
  Feldprojekt-CLAUDE.md, und normalisiert Markdown-Hervorhebungen.

### Fixed — Defekte, die nur in einem frischen Projekt auftreten
- **`ralph.sh` brach ohne jede Meldung ab, wenn `.ralph-plan` fehlte.**
  `head` auf eine fehlende Datei liefert RC≠0 und riss unter `set -e -o pipefail`
  den Loop weg, **bevor** die erklärende Fehlermeldung erreicht wurde — der
  Anwender sah einen blanken Exit 1. Im Feldprojekt existierte die Zeiger-Datei
  seit Kaskade 1, deshalb ist das nie aufgefallen; beim allerersten Start eines
  neuen Projekts ist die fehlende Datei der Normalfall.
- **`team_plan_datei()` hatte denselben Defekt**, obwohl die Funktionsdoku
  ausdrücklich „kein Abbruch hier" zusagte. Betraf `team_ralph_cap` und
  `team_budget_empfehlung` und damit `halbautomatik.sh` und `team-status.sh`.

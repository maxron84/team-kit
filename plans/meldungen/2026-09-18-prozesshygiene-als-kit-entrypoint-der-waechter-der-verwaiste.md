# Prozesshygiene als Kit-Entrypoint - der Waechter, der verwaiste Rollen-Prozesse nach Kommandozeile und Elternprozess beurteilt

- **Art**: Lücke in der Doku
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python und Electron,
  27 Kaskaden gebaut, rund 250 Testdateien.

> **Das ist die zweite Hälfte einer bereits gemeldeten Sache.** Die erste
> Hälfte — *„Vollautomatik hängt endlos, wenn eine Rolle GUI-Enkel
> hinterlässt"*, gemeldet am 2026-09-13 — beschreibt die **Mechanik** im Kit:
> Die Pipeline in `Rolle-Starten` endet erst bei EOF, und EOF kommt erst, wenn
> auch Enkelprozesse das geerbte Schreibende loslassen. Diese Meldung hier
> beschreibt den **Auslöser-Teil**, den das Feld inzwischen gebaut hat, und
> bietet ihn dem Kit an. Beide zusammen ergeben erst den Fall.

## Was passiert ist

**Nicht ein Fehler, sondern eine Erzählung, die nie geprüft wurde.**

Am 2026-09-09 stand in diesem Projekt zum ersten Mal die Diagnose *„N
verwaiste pwsh-Prozesse vor dem Lauf gefunden"* — als Erklärung für eine
flackernde Testsuite, deren Teardowns mit `PermissionError [WinError 32]`
fielen. Die Diagnose wurde **noch am selben Abend widerlegt**: Die fünf
Prozesse waren Terminals der Entwicklungsumgebung, erkennbar an einem
**lebenden** gemeinsamen Elternprozess und am Marker `shellIntegration` in der
Kommandozeile. Die Lehre wurde wörtlich aufgeschrieben:

> *Ein Prozess wird nach seiner **Kommandozeile** beurteilt, nicht nach Name
> und Alter.*

**Danach ist dieselbe widerlegte Diagnose viermal wiederholt worden** — in
einem CHANGELOG-Eintrag, in zwei Red-Team-Funden und, am deutlichsten, in
einem Vollautomatik-Lauf, wo die Zeile

    5 verwaiste pwsh-Prozesse vor dem Lauf gefunden; Ursache ausserhalb dieser Stufe

von fünf aufeinanderfolgenden Ralph-Stufen und dreimal von Frank an die
Gate-Datei angehängt wurde. **Kein einziges Mal** ist dabei eine
Kommandozeile angesehen worden; jede Wiederholung stammte aus `Get-Process`
oder `tasklist`, also aus Name und Alter.

**Gemessen, als endlich jemand nachsah** (`Get-CimInstance Win32_Process` mit
Elternauflösung, auf derselben Maschine): vier Prozesse der fraglichen
Gattung, **drei** davon Terminals der Entwicklungsumgebung mit **lebendem**
Elternprozess und `shellIntegration` in der Kommandozeile, der vierte die
eigene Sitzung. **Null Waisen nach beiden unabhängigen Regeln.** Eines dieser
Terminals lief nachweislich **vor** dem fraglichen Lauf an und läuft heute
noch — nach Name und Alter wäre es damals mitgezählt worden.

**Warum das mehr wiegt als vier Einzelfälle:** Die Erklärung ist
**selbstbestätigend** geworden. Sie erklärt jeden Flake, kostet nichts und
wird nie geprüft. Solange sie steht, ist ein **echter** Waise unsichtbar —
weil er wie die nächste Wiederholung aussieht. Das ist dieselbe Bauart wie ein
Wächter, der über einer leeren Ergebnismenge grün meldet, nur in Prosa statt
in Code.

## Wo es steckt

**Im Kit steckt die Ursache; im Feld steckt bisher die Abhilfe.**

Die Ursache ist bereits gemeldet (Meldung vom 2026-09-13): Die Pipeline in
`Rolle-Starten` wartet auf EOF, und ein GUI-Enkel, der das geerbte
Schreibende hält, verhindert es. **Was fehlt, ist die Gegenprobe** — ein
Werkzeug, das vor dem Lauf sagt, ob überhaupt etwas dasteht, und zwar mit
einem Urteil, das stimmt.

Das Kit hat für diese Klasse keinen Ort:

- `team-status` berichtet Zustand, misst aber keine Prozesse.
- Die Entrypoints starten Rollen, prüfen aber die Maschine nicht, auf der sie
  laufen.
- In den Rollen-Briefings steht die Regel *„vor dem Lauf nachsehen"* nirgends,
  und das ist richtig so — sie ist keine Loop-Arbeit.

**Folge: Sie lebt als Gedächtnisarbeit des Menschen** — und Gedächtnisarbeit
hat in diesem Fall viermal in Folge versagt.

## Warum das jede Installation trifft

**Weil der Auslöser im Kit sitzt, nicht im Projekt.** Was hier verwaist,
hinterlässt eine **Rolle** — gestartet von einem Kit-Entrypoint, über eine
Kit-Pipeline, die auf EOF wartet. Jede Installation, die Rollen headless
startet und deren Werkzeuge Kindprozesse erzeugen (ein Testlauf, ein
Buildschritt, ein GUI), kann denselben Zustand erreichen.

**Und jede Installation bekommt dieselbe Falle mitgeliefert:** Der
naheliegendste Griff zum Nachsehen ist `Get-Process` oder `tasklist`, und
genau der urteilt nach Name und Alter. Auf einer Entwicklermaschine ist ein
Terminal der Entwicklungsumgebung davon **nicht zu unterscheiden**. Die
Fehldiagnose ist also nicht ein Missgeschick dieses Projekts, sondern der
**Normalausgang** des naheliegenden Vorgehens.

**Der Unterschied zwischen beiden Urteilen ist nicht akademisch.** Er
entscheidet, ob ein Abräumer ein totes Überbleibsel beendet oder das Terminal,
in dem gerade jemand arbeitet.

## Was ich schon versucht habe

**Gebaut, nicht nur versucht** — fünf Stufen, Gate grün, zwei kritische
Red-Team-Funde unterwegs gefunden und behoben. Die Bauform ist bewusst so
gewählt, dass sie übernehmbar ist:

**1. Erhebung und Urteil sind getrennt.** Ein pwsh-Skript erhebt die Prozesse
samt `ParentProcessId`, `CommandLine`, `ExecutablePath` und Startzeiten und
gibt **JSON** aus. Ein Python-Modul daneben urteilt **ausschließlich über
Datensätze** und sieht selbst keine Prozesse. Das macht das Urteil ohne
laufende Maschine testbar — die Testsuite prüft es gegen erfundene
Prozesslandschaften, nicht gegen die Maschine des Entwicklers.

**2. Drei unabhängige Merkmale statt einem.**

    verwaist   := Elternprozess lebt nicht mehr
    harmlos    := Elternprozess ist eine bekannte Huelle (Terminal der
                  Entwicklungsumgebung, cmd-Wrapper, Explorer, verschachteltes
                  pwsh) ODER die Kommandozeile traegt den Terminal-Marker
    zum_repo   := ExecutablePath oder CommandLine liegen unter der Repo-Wurzel

Gemeldet wird nur, was **verwaist und zum_repo und nicht harmlos** ist. Die
Pfadprüfung normalisiert vorher Schrägstrich-Richtung und Groß-/Kleinschreibung
— auf Windows liefern die beiden Felder beide Richtungen gemischt.

**3. Der Wächter meldet vor jedem Suitenlauf und nennt die geprüfte Menge.**
Ein `pytest_sessionstart`-Haken druckt eine Zeile:

    Prozesshygiene: keine Waisen -- geprueft: 6 Prozesse.

**Die geprüfte Menge gehört in die Meldung.** Ohne sie sind *„keine Waisen"*
und *„nichts gesehen"* nicht unterscheidbar, und ein Wächter, der über einer
leeren Menge grün meldet, ist genau das Problem, das er lösen soll. Unter
paralleler Ausführung steht die Zeile **einmal** — der Haken gehört auf den
Steuerprozess, nicht auf jeden Arbeiter, sonst meldet er vielfach und misst
fremde Prüfstände mit.

**4. Abräumen nur auf ausdrückliche Anweisung, Trockenlauf als Vorgabe.**

### Die zwei kritischen Funde am Abräumer — sie gehören in diese Meldung

**Wer diesen Teil übernimmt, übernimmt auch die zwei Fallen.** Beide wurden
vom Red Team gefunden, beide sind behoben, und beide sind **nicht** speziell:

- **Ein toter Elternprozess ist kein hinreichender Waisen-Beweis.** Startet
  jemand eine GUI-Anwendung aus einer Shell und schließt danach die Shell —
  ein alltäglicher Vorgang; ein GUI-Prozess unter Windows lebt ohne sein
  Start-Terminal weiter —, dann zeigt sein `ParentProcessId` auf einen toten
  Prozess, und der Pfad liegt unter der Repo-Wurzel. Beide Merkmale treffen zu,
  und die Anwendung läuft und wird gerade benutzt. Ein `taskkill /T /F`
  hätte sie samt ihrem gesamten Prozessbaum erschlagen. **Das `harmlos`-Merkmal
  muss auch beim Abräumen konsultiert werden, nicht nur beim Melden** — und
  bekannte GUI-Gattungen brauchen eine eigene Ausnahme.
- **Der Verifikationstest des Abräumers darf ihn nicht scharf abfeuern.** Der
  Reproducer rief den echten Schalter gegen die **lebende Maschine** auf. Er
  trug eine Markierung, die ihn hätte ausschließen sollen — aber eine
  Markierung filtert von sich aus nichts, und der **dokumentierte**
  Testbefehl des Projekts trug keinen entsprechenden Ausschluss. Ergebnis:
  **Jeder reguläre Testlauf** — jede Rolle, jeder Mensch, jeder Sweep — führte
  ein maschinenweites Abräumen aus, ohne dass es irgendwo stand.

**Die allgemeine Lehre, die für das Kit interessanter ist als der Code:** Wo
ein Werkzeug etwas **beendet, löscht oder überschreibt**, genügt die Frage
*„urteilt der Filter richtig?"* nicht. Es braucht die zweite Frage: **„Was
steht außerhalb der Prüfmenge, wenn der Schalter fällt?"** Im zweiten Fall war
die Antwort *„die ganze Maschine"*, und ausgelöst hat ihn der dokumentierte
Standardbefehl.

### Was übernehmbar ist und was Feldwissen bleibt

Das ist im Feld nachgemessen worden, und die Grenze verläuft nicht dort, wo
man sie zuerst vermutet:

| Teil | Zuordnung |
|---|---|
| Erhebung (JSON), Urteilsfunktion, Abräumer mit Trockenlauf | **generisch** — in jeder Installation gleich |
| Liste der bekannten Hüllen, GUI-Ausnahmen, Wächter-Anbindung ans Testframework | **feldseitig** — hängt an Werkzeugkette und Umgebung |

**Der Rahmen ist übernehmbar; die Merkmalslisten sind es nicht.** Ein
Kit-Entrypoint sollte die Listen deshalb aus der Projektkonfiguration lesen,
nicht fest verdrahten.

### Wie es im Feld geführt wird

**Als Provisorium, ausdrücklich** — mit demselben Wortlaut und derselben
Bauform wie die Fixphasen-Kette, die aus genau demselben Grund als Provisorium
geführt wird (das Kit hat sie als Phase der Vollautomatik, nur ohne
Einzeleinstieg). Kommt ein Kit-Entrypoint, ersetzt er das Skript samt Vermerk.

**Der Code liegt bereit** und kann auf Wunsch als Patch nachgereicht werden;
er steht hier nicht vollständig drin, weil die Bauform wichtiger ist als die
Zeilen — und weil die Merkmalslisten ohnehin nicht übernommen werden sollten.

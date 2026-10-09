# Laufzeit ueber das Log belegen, Handabnahmen automatisieren: der Mensch beobachtet und beraet

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-09-laufzeit-ueber-das-log-belegen-handabnahmen-automatisieren-d.md
      .\kit-melden.cmd ablegen  2026-10-09-laufzeit-ueber-das-log-belegen-handabnahmen-automatisieren-d.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-09-laufzeit-ueber-das-log-belegen-handabnahmen-automatisieren-d.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: Wunsch des Owners, geäußert in `Feld F` am 2026-10-09. Im Feldprojekt bekommt er
  seine Backlog-Zeile nach dem laufenden Lauf.
- **Art**: Idee / Verbesserung (Wunsch des Owners; gilt für laufende und für neue Projekte, beide
  Bahnen)
- **Kit-Version**: 2.13.1 (dazu `[Unreleased]`)
- **Bahn**: pwsh (der Wunsch gilt für beide Bahnen)
- **Plattform**: win32
- **Feldkürzel**: `Feld F` (laut Profiltabelle im README; `TEAM_FELD_KUERZEL` ist im Projekt noch
  leer)
- **Lage des Projekts**: Greenfield, Windows 11, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python, zwölf Kaskaden. Der Smoke-Test prüft nur statisch. Was das Programm tut, zeigt sich erst im
  laufenden Spiel oder auf einem lokalen headless Server.

## Der Wunsch (Wortlaut des Owners)

> „Debuglog orientiertes Development wie in diesem Projekt soll in Zukunft für alle Projekte dieser
> Art hervorgehoben werden, gerne auch noch extremer, Handabnahmen durch den Stakeholder sollen
> möglichst breitflächig und effizient unterstützt werden, um menschliche Fehler bei Auswertungen
> klein zu halten. Der Mensch soll beobachten und bei Look and Feel und ähnlichen Fragen in der
> Hauptsache beratend tätig sein. Hinweis, es gibt Stand Datum dieser Niederschrift mindestens ein
> weiteres visuell bewegtes Gaming projekt unter dem Teamkit. Das heißt, dieser Wunsch gilt für
> bereits vorhandene laufende Projekte, ebenso wie künftige neu angefangene.“
>
> Nachtrag: „Handabnahmen kann man so auch allgemein automatisieren, wo es möglich ist, es gibt noch
> ein Android Projekt auf einer anderen Maschine im bash Zweig. Also mit Android Emulator.“

Betroffen sind damit mindestens `Feld A` (Spiel-Engine, bash-Bahn), `Feld E` (Android-Tablet,
Emulator, bash-Bahn) und `Feld F` (Spielskript-Stack, pwsh-Bahn), dazu jedes künftige Projekt,
dessen Verhalten erst im laufenden Programm sichtbar wird: Spiele, Apps im Emulator oder auf dem
Gerät, Oberflächen.

## Was passiert ist (Feldbeleg aus `Feld F`)

In den ersten Kaskaden war die Handabnahme der erste Lauf überhaupt, und der Mensch wurde zum
Debugger. Er las Werte am Bildschirm ab, beschrieb, was er gesehen hatte, und eine Abnahme hing an
seinem Gedächtnis. Über elf Kaskaden ist daraus ein Verfahren gewachsen, in dem er nur noch
beobachtet, berät und entscheidet:

1. **Die Laufzeit schreibt ihre Belege selbst.** Jede Stufe, die Laufzeitverhalten baut, schreibt
   ihre Belege ins Log der Engine. Die Zeilen tragen einen festen Präfix je Kanal (Info, Reset,
   Fehler, Selbsttest, Probe) und je Zeile nur wenige Werte, weil die Engine lange Zeilen bei rund
   1000 Zeichen kappt. Ereignisse wie ein Durchstarten oder ein Sprung der Figur erkennt ein
   Ereignis-Handler, nicht das Auge. Der Mensch liest keinen Wert ab und notiert nichts.
2. **Ein Werkzeug im Projekt wertet das Log aus.** Es filtert die Kanäle, fasst jede Probe zusammen
   und fällt das Urteil des Selbsttests. Jede Auswerteregel hat eine Testdatei im echten Format des
   Logs und eine Mutation, die sie rot macht. Zweimal fiel eine Regel erst an einer echten Zeile auf,
   weil die Testdatei das Format nur nachahmte. Mehrere Durchgänge in einem Log trennt das Werkzeug
   an einer festen Startzeile und nennt ihre Zahl.
3. **Das Programm prüft sich selbst.** Ein Selbsttest mit START, einer Zeile je Prüfung und SUMMARY
   läuft in der Entwicklervorschau mit Zeitraffer, auf Wunsch auch als Liste einzelner Prüfungen.
   Jede Stufe, die Laufzeitverhalten baut, bringt ihre Prüfung mit (Projektregel seit der vierten
   Kaskade). Heute sind es 35 Prüfungen in rund 32 Minuten. Der Mensch startet sie mit einer Zeile
   und wartet.
4. **Was ohne den Menschen laufen kann, läuft ohne ihn.** Seit der elften Kaskade startet der
   Architekt gezielte Prüfungen und Proben auf einem lokalen headless Server: nur lokal, mit
   Zufallspasswort, am Ende sanft beendet und aufgeräumt. Kein Loop-Lauf und kein Test startet ihn.
   Sieben solche Läufe fanden ohne einen Handgriff des Menschen die Ursache eines Fehlers, der drei
   Kaskaden lang offen war und vorher zwei Handproben und eine Nachprobe gekostet hatte, und dazu den
   Weg für einen zweiten Fund.
5. **Die Handabnahme ist Beobachtung, keine Messung.** Die Schritte stehen kopierfertig in einem
   Block. Konsolenbefehle sind vorher durch die statische Prüfung gelaufen. Jede Frage an den
   Menschen ist eine Zeile und betrifft nur Look and Feel oder was nur er sehen kann. Handarbeit, die
   kein Skript kann (etwa Speichern und Laden), steht als eigener Schritt da. Je Handprobe gibt es
   höchstens zwei Nachproben. Die Auswertung macht der Architekt aus dem Log, und ob der Editor des
   Menschen Dateien geändert hat, prüft er selbst.
6. **Annahmen über die Laufzeit werden vorher belegt.** Trägt eine Annahme über das Verhalten der
   Engine den Kern einer Stufe, kommt vor dem Bau eine Konsolen- oder Serverprobe. Zwei Stufen sind
   gescheitert, bevor diese Regel galt. Eine Probe ändert gegenüber dem Commit genau eine Größe und
   lässt eine Kontrolle mitlaufen. Fallen Engine-Zeilen und Ereignisse zusammen, wird erst eine der
   Größen gezielt verändert, bevor ein Fix entsteht.

Der Preis: Der Architekt trägt in `Feld F` rund 79 bis 86 % jeder Kaskade (die letzten beiden),
ein großer Teil davon ist Auswertung und Serverbetrieb. Das ist die Arbeit, die vorher der Mensch
mit Ablesen, Beschreiben und Wiederholen geleistet hat.

## Wo es steckt

- Die Briefings unter `geteilt/prompts/` kennen den Smoke-Test, die Probe an der Wirklichkeit
  (`Kit-BL-288`) und die Frage „Mit welchem Befehl wird diese Zusicherung ROT?“. Für Verhalten, das
  nur im laufenden Programm sichtbar ist, sagen sie nichts: keine Regel, dass eine
  Laufzeitbehauptung eine Logzeile und eine Auswerteregel braucht, kein Selbsttest, keine Vorlage
  für eine Handabnahme, keine automatisierten Läufe ohne den Menschen. Eine Suche nach „Handprobe“
  oder „Look and Feel“ trifft im Kit nur die Profiltabelle des README.
- `TEAM_ZIELSTAND_PRUEFUNG` (`Kit-BL-300`) prüft, ob Gerät, Emulator oder installierte Fassung den
  gebauten Stand tragen. Das ist der erste Schritt auf diesem Weg, aber er sagt nicht, was ein Lauf
  dort belegen soll.
- In `Feld F` steht alles oben als Projektregel (die Konventionen der Skriptsprache in der
  projekteigenen `CLAUDE.md`, die Leitplanken jedes Plans, die Notizen des Architekten). Jede andere
  Installation fängt damit bei null an.

## Warum das jede Installation trifft

Jedes Projekt, dessen Verhalten erst im laufenden Programm sichtbar wird, hat dieselbe Spaltung: Der
Loop prüft statisch, der Mensch sieht die Laufzeit. Ohne Anleitung im Kit erfindet jedes Projekt
das Verfahren neu (`Feld F` brauchte dafür elf Kaskaden), oder der Mensch bleibt der Debugger und
macht bei der Auswertung genau die Fehler, die der Owner klein halten will. Der Wunsch gilt
ausdrücklich für laufende und künftige Projekte und für beide Bahnen.

## Vorschlag fürs Kit

1. **Ein Projektmerkmal „Laufzeit nur im laufenden Programm sichtbar“** in `team.config.*`, etwa
   `TEAM_LAUFZEIT_BELEG` mit der Quelle der Belege (Log der Engine, `adb logcat` mit festem Tag,
   Konsole einer Oberfläche). Der Installer fragt danach, ein `-Update` fragt laufende Projekte
   einmal. Ist es gesetzt, bekommen die Briefings den Abschnitt „Belege aus dem Log“ (Punkte 2
   bis 5).
2. **Architekt:** Jede Stufe, die Laufzeitverhalten baut, nennt die Logzeilen, die sie belegen
   (Kanal, Präfix, Felder), die Auswerteregel samt Testdatei im echten Format und Mutation, und ihre
   Prüfung im Selbsttest. „Beleg nur im Spiel“ bleibt für Look and Feel, alles andere bekommt eine
   Logzeile. Die Abnahme (`Kit-BL-219`) belegt jeden Punkt aus dem Log; das Urteil des Menschen gilt
   für Look and Feel und für Entscheide. Eine Vorlage für Handabnahmen: Vorbereitung
   (automatisiert), Schritte als ein kopierfertiger Block, worauf er schaut (ohne Werte abzulesen),
   eine Frage je Zeile, Auswertung durch den Architekten, höchstens zwei Nachproben. Eine
   Laufzeitannahme, die eine Stufe trägt, bekommt vorher eine Probe.
3. **Automatisieren, wo es geht:** Läuft das Programm ohne Menschen (headless Server, Emulator ohne
   Fenster, instrumentierte Oberflächentests, Eingaben und Bildschirmfotos über `adb`), fährt der
   Architekt Proben und Selbsttests selbst, mit Sicherheitsregeln des Projekts: nur lokal, am Ende
   aufgeräumt, kein Loop-Lauf startet es. Der Mensch startet nur, was sein Auge oder eine nicht
   automatisierbare Umgebung braucht.
4. **Ralph und Frank:** beim Bauen instrumentieren, also an jedem Entscheidungspunkt eine kurze
   Logzeile schreiben, die eine Prüfung liest. Ein Fix an Laufzeitverhalten bringt die Logzeile mit,
   an der der nächste Lauf ihn belegt.
5. **Harry und Marv:** eine eigene Fundklasse „Laufzeitbehauptung ohne Logzeile oder ohne
   Auswerteregel“. Auswerteregeln, die nur gegen nachgeahmte Testdateien geprüft sind, sind ein
   Fund.
6. **Doku:** ein Kapitel unter `doku/` mit `Feld F` als Feldbeispiel (Engine-Log, Selbsttest,
   headless Server) und der Android-Variante als zweitem (`adb logcat`, Emulator, instrumentierte
   Tests), die `Feld E` beisteuern kann.

## Was ich schon versucht habe

Im Feldprojekt ist alles oben gebaut und Projektregel. Es übersteht jedes Update, weil es in Dateien
des Projekts steht, aber keine andere Installation hat es. Für `Feld A` und `Feld E` ist der Wunsch
nicht erprobt. Was dort schon an Logs, Emulator und automatisierten Abnahmen läuft, weiß ich nicht.

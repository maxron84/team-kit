# Abnahme-Loop: eine Rolle wertet Gegenlesung und Serverläufe aus, ohne dass eine Sitzung wartet

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-16-abnahme-loop-eine-rolle-wertet-gegenlesung-und-serverlaeufe.md
      .\kit-melden.cmd ablegen  2026-10-16-abnahme-loop-eine-rolle-wertet-gegenlesung-und-serverlaeufe.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-16-abnahme-loop-eine-rolle-wertet-gegenlesung-und-serverlaeufe.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: zwei Backlog-Einträge des Feldprojekts (dort BL-75 und BL-76) und der Plan seiner Kaskade 15
- **Art**: Idee / Verbesserung
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in Python. Fünfzehn
  Kaskaden sind gelaufen, die Suite hat rund 2700 Tests. Laufzeitverhalten zeigt nur das Spiel selbst; seit Kaskade 11
  startet ein Werkzeug des Projekts dafür einen lokalen Spielserver mit Prüfungen und Proben.

## Was passiert ist

Bis Kaskade 14 hat der Architekt jede Abnahme selbst gefahren: die Gegenlesung der Fixe (Gegenprobe der neuen Tests
gegen den Stand vor dem Fix, Mutationsreihen über alle Specs, Kontrollen, Stellprobe), Serverläufe mit Proben und die
Auswertung der Logs. Seine Sitzung mit starkem Modell wartete dabei mit. Eine Mutationsreihe dauert rund 20 Minuten, ein
Serverlauf 40 bis 150 Minuten. In Kaskade 14 kostete der Architekt rund 390 USD Abo-Gegenwert, Bau und Prüfrollen
zusammen rund 41 USD. Der Mensch entschied: ein eigener Loop, im Projekt gebaut, danach diese Meldung.

Gebaut in Kaskade 15 (elf Stufen, 11,67 USD Bau): ein Befehl `.\abnahme.cmd <auftrag> …` in der Wurzel, die Werkzeuge
als Python-Paket unter `tools/` (nur Standardbibliothek), dazu eine Rolle mit günstigem Modell (im Feld „Otto“), ihr
Briefing liegt im Paket. Nichts davon liegt unter `team/`, ein Update überschreibt es also nicht. Der Ablauf ist fest:

1. Sperre über `team_lock` (eine Pipeline zur Zeit, auch gegen die Vollautomatik).
2. Ein Python-Prozess im Fenster des Menschen. Er prüft die Vorbedingungen (Arbeitsbaum sauber, kein Gate, kein
   Spielprozess) und die Aufträge. Ein Auftrag ist eine JSON-Datei mit Läufen und mit Fragen, je Frage `erwartung` und
   `beleg`. Dann fährt er die Gegenlesung aller Fixe seit der letzten Abnahme und die Serverläufe der Aufträge
   nacheinander. Gestartet wird nur über das Serverwerkzeug des Projekts, nur lokal, mit Passwort, sanft beendet und
   mit Beleg: die Netzwerkzeilen des Serverprozesses und die Prozessliste danach. Danach schreibt er Auszüge und
   Auswertungen jedes Logs und einen Lagebericht mit allen Fragen und der Leseliste. Das Skript wartet selbst,
   währenddessen läuft keine Modell-Sitzung.
3. Die Rolle liest nur (Read, Grep, Glob, `git log`, `git diff`, `git show`, das Beutebuch-Werkzeug). Sie schreibt
   einen Bericht mit festen Abschnitten, je Frage genau eine Zeile `ABDECKUNG <auftrag> <nr>: beantwortet` oder
   `… nicht beantwortbar - <Grund>`, und Funde ans Ende des Beutebuchs. Edit und Write gelten nur für Bericht und
   Beutebuch, relativ und absolut (`Kit-BL-292`).
4. Prüfung: Guard mit schmaler Whitelist, Budget nach `Kit-BL-30`, Quittung, Bericht vollständig, `beutebuch.py lint`
   und ein Test auf Steuerzeichen. Dann ein Commit `docs(abnahme): …` und ein Zeiger auf den gelesenen Stand für die
   nächste Gegenlesung. Fällt die Prüfung durch, landet das Ergebnis als Kopie in der Ablage, die Rolle wird
   zurückgerollt, und `-NurAuswertung <ablage>` wiederholt nur Schritt 3 und 4.

Die Bibliothek des Kits nutzt der Loop nur über exportierte Funktionen (`team_lock`, `team_claude`,
`team_guard_begin`, `team_guard_verify`, `team_guard_urteil`, `team_budget_check`, `team_promise_in`,
`team_result_meldet_erfolg`, `team_rollback_rolle`, `team_eigene_pfade`, `Team-Werkzeug`, `Team-Fehler`,
`Team-HilfeKopf`). Ein Vertragstest im Projekt hält Namen und Parameter fest. Ändert ein Update sie, wird die Suite rot,
statt dass der Loop still bricht.

**Die erste Abnahme** (drei Aufträge, gestartet 4 s nach dem Ende der Vollautomatik):

- Der Lauf dauerte 2 h 30 min ohne Handgriff: Gegenlesung 3 min, drei Serverläufe mit 60, 38 und 47 min, alle mit dem
  Endsignal der Mission. Der Server lauschte nur auf 127.0.0.1, danach liefen kein Serverprozess und keine
  Missionskopie mehr. Modellkosten in dieser Zeit: null.
- Die Rolle brauchte 5 min, 50 Turns und 1,30 USD (Deckel 20). Ihr Bericht beantwortet alle 15 Fragen mit Datei und
  Zeile als Beleg und deutet die Gegenlesung richtig. Er enthält einen Fund mit Ursache und Erwartung und zwei eigene
  Auffälligkeiten an den Auswertungen; eine davon ist ein echter Fehler im Werkzeug. Zweimal wollte die Rolle das
  Beutebuch per Shell-Heredoc erweitern, die CLI lehnte ab, danach nahm sie Edit.
- **Verworfen wurde das Ergebnis trotzdem.** Der letzte Docs-Commit der Fix-Phase, 12 s vor dem Start, trug ein BEL
  im CHANGELOG (Backslash-Falle, siehe die Meldung vom 2026-10-11 und die zweite Meldung von heute). Die Suite am HEAD
  war damit rot. Jede Mutationsreihe scheiterte an ihrer Grundprobe, 1384 Mutationen und 5 Kontrollen blieben
  ungeprüft, und die Serverläufe liefen trotzdem. Am Ende verwarf die Schlussprüfung den vollständigen Bericht, weil
  der Test auf Steuerzeichen über das ganze Repo urteilt und nicht über die Dateien der Rolle. Die Rolle selbst hatte
  genau dieses Zeichen als Fund eingetragen.

## Wo es steckt

Kein Fehler im Kit, sondern eine Rolle, die fehlt. Das Kit kennt Bau (Ralph), Angriff (Harry, Marv), Fix (Frank),
Forensik (Axel) und Planung (Architekt), aber keine Abnahme, die Laufzeitverhalten belegt. Heute schließt diese Lücke
der Architekt mit starkem Modell und wartender Sitzung, oder der Mensch mit Handproben. `TEAM_ZIELSTAND_PRUEFUNG`
(`Kit-BL-300`) prüft nur, ob das Ziel den gebauten Stand trägt, nicht, wie er sich verhält.

## Warum das jede Installation trifft

Jedes Projekt, dessen Verhalten erst zur Laufzeit sichtbar wird (Spiel, Emulator, Gerät, Dienst), braucht nach dem Bau
eine Abnahme mit Wartezeit. Für eine Modell-Sitzung ist Warten der teuerste Teil (`Kit-BL-281`: 2,01 USD für null
Fortschritt), und das Ausschlusskriterium für Franks Übergabe (Messreihen gehen nicht an Frank) schiebt genau diese
Arbeit zum Architekten mit dem teuersten Modell.

## Was ich schon versucht habe

Gebaut ist der Loop im Projekt, außerhalb von `team/`, wie oben beschrieben. Die erste Abnahme ergab diese Vorschläge
fürs Kit:

1. **Das Skript wartet, die Rolle urteilt.** Gegenlesung und Serverläufe kosten keine Token, wenn ein Skript sie fährt.
   Die Rolle bekommt am Ende fertige Auszüge, einen Lagebericht unter 400 Zeilen und Fragen mit Erwartung und Beleg.
   Die Auswertung einer Abnahme von 2,5 Stunden kostete 1,30 USD.
2. **Schlussprüfungen urteilen nur über das, was die Rolle geschrieben hat.** Eine Prüfung über das ganze Repo verwirft
   mit fremdem Rot auch ein richtiges Ergebnis (im Feldprojekt BL-75). Für Berichte genügt die Prüfung der
   geschriebenen Dateien oder der Vergleich mit dem Stand vor der Rolle.
3. **Vorbedingung: Die Suite ist am HEAD grün.** Sonst ist jede Gegenlesung mit Mutationsreihen wertlos, und der Lauf
   merkt es erst nach Stunden. Die Prüfung kostet rund 2 Minuten, der Lauf dauert 2,5 Stunden.
4. **Gegenprobe der Fixe:** Rot verlangen von neuen Testdateien eines Fixes. Ein angepasster Bestandstest kann vor dem
   Fix grün sein; das ist kein Fehler (im Feldprojekt BL-76, die Rolle hat es mit Begründung so entschieden).
5. **Vertrag statt Kopie:** Eine Rolle außerhalb von `team/` nutzt die Bibliothek nur über exportierte Funktionen, ein
   Vertragstest hält sie fest. Bietet das Kit einen Platz für die Abnahme an, etwa eine Phase nach Frank in der
   Vollautomatik oder einen Einstieg `abnahme` mit einem Lauf-Befehl des Projekts wie `TEAM_ZIELSTAND_PRUEFUNG`, entfällt
   der Vertragstest.
6. **Offen im Feld:** Ob die Mutationsreihen im Loop tragen, ist nicht belegt; in der ersten Abnahme lief keine einzige
   Mutation. Das zeigt die nächste Abnahme.

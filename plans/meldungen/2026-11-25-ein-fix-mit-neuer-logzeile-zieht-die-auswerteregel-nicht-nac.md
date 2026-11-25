# Ein Fix mit neuer Logzeile zieht die Auswerteregel nicht nach - dreimal in einer Kaskade, obwohl Franks Prompt es verlangt

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-25-ein-fix-mit-neuer-logzeile-zieht-die-auswerteregel-nicht-nac.md
      .\kit-melden.cmd ablegen  2026-11-25-ein-fix-mit-neuer-logzeile-zieht-die-auswerteregel-nicht-nac.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-25-ein-fix-mit-neuer-logzeile-zieht-die-auswerteregel-nicht-nac.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit (die Auflage aus `Kit-BL-325` greift bei Fixen nicht)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: keins eingetragen — dasselbe Projekt wie die Meldungen vom 2026-11-02, 2026-11-19 und 2026-11-20
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn; Workflow-XML mit Prüfkette in Python, rund 1 400 Tests; achte Kaskade; `TEAM_LAUFZEIT_BELEG` gesetzt (Joblog des Handlaufs, Zeilen mit festem Präfix)

## Was passiert ist

Das Projekt belegt Laufzeitverhalten über Logzeilen mit festem Präfix. Eine
Auswerteregel je Zeilentyp liest sie aus dem Joblog und rechnet nach, ob der
Lauf richtig gehandelt hat — eine zweite Zustandsmaschine neben dem Programm.
In einer Fix-Phase änderten drei Fixe, was im Log steht, und keiner zog die
Regel nach, die es liest:

1. Neuer Wert `mail=fehlgeschlagen` in einer bestehenden Zeile. Die Regel
   meldete ihn mit dem falschen Grund („erwartet neu oder heute schon").
2. Neue zweite Zeile `FEHLERMAIL|merk_zurueckgenommen=<n>` nach
   `ergebnis=fehlgeschlagen`. Die Regel zählte beide als Fehler-Mail und
   meldete „nicht versucht oder doppelt".
3. Neue Zeile `HINWEIS|…|feld=Unterlage`, mit der das Programm einen
   Datensatz als nicht vollständig wertet und deshalb nicht aufräumt. Die
   Regel kennt die Zeile nicht, hält den Datensatz für vollständig und meldet
   „vollständig ohne Aufräumen". Der geplante Abnahmelauf fiele durch, obwohl
   das Programm richtig handelt.

Jeder dieser Fixe war im ersten Versuch grün, die Fix-Phase meldete jeweils
„Dreisatz verifiziert". Gefunden hat 1 und 2 die Ermittlung (Axel) zu einem
anderen Fund — mit 10,33 USD der teuerste Posten des Laufs, nach drei
Frank-Rollbacks. Fall 3 kam erst im Closeout heraus, bei der Probe an der
Wirklichkeit (Kit-BL-288): echtes Joblog, dokumentierter Aufruf der
Auswertung. Ein vierter Fall eine Ebene tiefer: Ein Fix änderte, was ein
Zähler im Log zählt. Danach sagte der Befundtext der Regel das Gegenteil
dessen, was das Programm tut; gefunden in der Mutationsprobe des Architekten.

## Wo es steckt

- Franks Prompt bekommt mit `TEAM_LAUFZEIT_BELEG` die Zeile aus
  `team/lib.psm1` (`$laufzeit`, `Kit-BL-325`): „Baust oder fixt du
  Laufzeitverhalten, … liefere die Auswerteregel mit, die sie liest … Ein Fix
  an Laufzeitverhalten bringt die Logzeile mit, an der der nächste Lauf ihn
  belegt." Die Auflage steht also da. Befolgt wurde der zweite Satz (die
  Logzeile kam jedes Mal mit), nicht der erste (die Regel nachziehen).
- Franks Quittung (Dreisatz-Prüfung in `frank.ps1`) prüft Commit, CHANGELOG,
  Status und den Substanzbezug, aber nicht, ob ein Fix, der eine Zeile mit dem
  Log-Präfix hinzufügt oder ändert, auch die Auswertung berührt.
- Der Substanz-Anker (`team_diff_beruehrt_fund`) ist zufrieden, sobald der
  Diff eine Datei aus dem Fundblock berührt — hier das Programm. Die
  Auswerteregel steht in keinem der drei Fundblöcke.

## Warum das jede Installation trifft

Jede Installation mit `TEAM_LAUFZEIT_BELEG` hat diese zwei Zustandsmaschinen:
das Programm, das schreibt, und die Regel, die das Geschriebene nachrechnet.
Ein Fix sieht nur seinen Fund. Die Regel steht nicht im Fundblock, also fragt
niemand nach ihr, und keine Prüfung vergleicht beide. Die Suite bleibt grün,
weil die Tests der Regel nachgebaute Logzeilen benutzen. Gefunden wird so ein
Fehler erst im Closeout oder beim Handlauf, also nach dem Lauf.

## Was ich schon versucht habe

Im Projekt ist die Regel für alle vier Fälle nachgezogen oder als Fund an
Frank übergeben. Ein Reproducer bindet die Zeilenformen an die print-Tasks des
Programms: Eine neue Form macht ihn rot. Das fängt 1 und 2, aber nicht 3 —
dort ist die Form bekannt, neu ist ihre Bedeutung.

Vorschläge, ohne Rangfolge:

1. Ein Wert `TEAM_LAUFZEIT_AUSWERTUNG` (Pfad der Auswerteregel). Die Quittung
   meldet einen Hinweis (sperrt nicht), wenn Franks Diff in einer
   Produktdatei eine Zeile mit dem Log-Präfix hinzufügt oder ändert und die
   Auswertung nicht berührt.
2. Franks Prompt sagt es für Fixe eigens: „Ändert dein Fix, was im Log steht
   oder wann es steht, zieh die Auswerteregel im selben Commit nach — auch
   wenn der Fund sie nicht nennt."

# Backlog — T.E.A.M.-Starterkit

Aufgaben am **Kit selbst**, die keine eigene Kaskade rechtfertigen: kleine
Verbesserungen, technische Schulden, Rückmeldungen aus Feldprojekten.

> **Nicht verwechseln:** `bootstrap/backlog.md` ist die **Vorlage** für
> Zielprojekte. Diese Datei ist der Backlog des Kits.

**Nummernraum**: `BL-n` ist historisch gewachsen und wird zwischen Ursprungs-
projekt, Kit und Feldprojekten geteilt. `BL-1`…`BL-5`
tragen hier dieselbe Bedeutung wie im Feldprojekt
`Feld A`, damit die Spur lesbar bleibt. Neue kit-eigene
Funde ab `BL-6`. Verweise auf den Backlog eines **anderen** Projekts werden
`Kit-BL-<N>` geschrieben (`BL-50`).

> **Feldbelege tragen Kürzel statt Namen** (`Feld A`…`Feld H`) —
> die Profiltabelle steht im [README](../README.md#herkunft).

> **Die Statusspalte beginnt mit einem Merkwort** (`BL-224`) — `offen`,
> `teilweise` oder `erledigt`, danach darf jede Prosa stehen. `offen` und
> `teilweise` zählen als offen. Der Grund ist eine Zahl: Das README nennt, wie
> viele Einträge offen sind, und `geteilt/kit-readme-pruefen.py` rechnet sie
> **hier** nach. Eine Zelle, die mit „Befund 1 erledigt …, Befund 2 bleibt
> offen" beginnt, ist für einen Leser klar und für einen Zähler nicht — der
> Wächter meldet sie deshalb namentlich als **unentscheidbar**, statt zu raten.

> **Abgetragene Einträge stehen im Archiv:**
> [`backlog-archiv.md`](backlog-archiv.md). Dort liegt die vollständige
> Begründung jedes erledigten Punktes — sie wird nachgeschlagen, nicht
> mitgelesen. Diese Datei trägt nur, woran noch Arbeit hängt (`BL-53`).

**Stand 2026-10-28 — Triage: zehn Meldungen vom 2026-10-26 bis
2026-10-28 lagen ohne Nummer da** — drei aus `Feld B`, zwei aus der
pwsh-Prüfung der Bauten vom 2026-10-18 auf der Windows-Maschine und fünf aus
einem neuen Feld. Sie bekommen `BL-344` bis `BL-354`. Der Nachtrag zu
`smoke_warten.py start` teilt die Nummer seiner Hauptmeldung (`BL-345`), der
Nachtrag „entfernte Modelle nur ausdrücklich" die seiner Bezugsmeldung
(`BL-354`), und Teil 3 der Meldung „Lokale Stufen im Team" ist der zweite
Feldfall von `BL-351`. Zwei Meldungen tragen je einen zweiten, eigenständigen
Befund; er bekommt eine eigene Nummer (`BL-348`, `BL-350`).

> **Diesmal auf Windows triagiert, mit beiden Bahnen.** Jede Meldung ist am
> Code nachgeprüft. Nachgestellt: die stumme Buchung und die Hilfe auf der
> pwsh-Bahn in einer Wegwerf-Installation mit beiden Bahnen, die Basis der
> CLAUDE.md und `warten` ohne Kennung synthetisch am Kit-Werkzeug.
> `smoke_warten.py start` unter `cmd.exe` und `test_bl326` waren schon am
> 2026-10-26 auf dieser Maschine nachgestellt, der Code ist seither
> unverändert. Die Strg+C-Behauptung aus `BL-353` ist an der laufenden Sitzung
> gemessen, rein lesend — und präzisiert die Meldung.

> **Ein neues Feldkürzel: `Feld H`** — Greenfield, Windows 11, beide Bahnen
> installiert, gearbeitet auf der pwsh-Bahn, Python: Das Produkt lässt ein
> lokales Sprachmodell (32K-Fenster) über einen lokalen Server arbeiten; ab
> der dritten Kaskade baut ein Programm im Produktivcode einzelne Stufen mit
> diesem Modell. Drei Kaskaden bis zum 2026-10-28, Planung ab dem 2026-10-26.
> Die Meldungen trugen noch kein Kürzel („vergibt der Maintainer"); von dort
> kommen `BL-349` bis `BL-354`. Die Profilzeile steht im
> [README](../README.md#herkunft).

**Was die Triage sortiert hat, nach Wirkung:**

- **Still falsch, ohne Signal:** `BL-344` (nach einer Handauflösung rückt die
  Basis der CLAUDE.md nie vor — nachgestellt: Schon **eine** bewusst anders
  formulierte Stelle hält danach jede neue Kit-Regel auf, die Datei bleibt bei
  jedem Update ganz unangetastet), `BL-349` (die pwsh-Bahn bucht jeden
  Closeout stumm; die Meldung mit der gebuchten Achse, die das Briefing lesen
  lässt, erscheint nie, und ein rotes Werkzeug mit Ausgabe endet dort mit
  Exit 0), `BL-351` (ein Red-Team-Fund stellt über Franks Fix einen
  Vertragswert um, den der Plan gemessen hat — zweimal im Feld, aufgefallen
  erst im Closeout).
- **Falscher Befund, der eine Rolle losschickt:** `BL-345` (`smoke_warten.py`
  meldet unter Windows ROT, ohne dass ein Test lief, wenn der Interpreterpfad
  relativ mit Schrägstrichen steht), `BL-353` (die Suite ist in jeder Rolle
  grün und im Terminal des Menschen rot — die Rolle erbt eine Konsole mit
  abgeschaltetem Strg+C), `BL-348` (ein roter Installer-Selbsttest heißt in
  Schritt 2 beider Selbsttests „nicht gefahren").
- **Geld ohne Grund:** `BL-346` (ein einziger fremder `smoke-*.log` hält
  `warten` ohne Kennung für immer bei 75; die Rolle wartet, bis Frist oder
  Budget erschöpft sind — der Ausgang, gegen den `BL-281` gebaut ist).
- **Kit-Selbsttest rot, ohne Fehler im Produktcode:** `BL-347` (`test_bl326`
  hängt unter Windows auf der bash-Bahn, weil `taskkill /T` den MSYS-Enkel der
  Attrappe nicht erreicht).
- **Anzeige:** `BL-350` (`team-status.cmd --hilfe` druckt drei Fehler; der
  Wächter aus `BL-229` sieht es nicht, weil der Rest der Zeile parst).
- **Ein Weg, den es nicht gibt, und die Auflage des Owners dazu:** `BL-352`
  (eine Stufe, die ein Programm statt eines Agenten baut, hat im Loop keinen
  Platz — drei Nähte von Hand), `BL-354` (jede Rolle jederzeit lokal oder
  entfernt; entfernte Modelle nur auf ausdrückliche Anweisung).

> **`BL-352` und `BL-354` sind ein Strang, kein Bau.** Der Owner hat die
> Endform entschieden: Die lokale Werkbank wird ein lokaler Teil des Kits.
> Das berührt `team_claude()` (heute der einzige Weg jeder Rolle), die
> Konfiguration, das Briefing des Architekten, die Startbefehle, das Ledger
> (`BL-247`, offener Punkt 4) und eine Phase ohne Modell (`BL-340` Teil B) —
> und es ist die Frage, die Skizze F für eine zweite CLI stellt, hier für ein
> lokales Modell. Vor dem Bau steht eine Skizze in `roadmap-skizzen.md`. Ohne
> sie baubar ist aus `BL-352` nichts; für seine dritte Naht gibt es schon
> heute einen Weg über die Konfiguration.

> **Gebaut wird weiter auf der Linux-Maschine.** Reihenfolge, Fundstellen,
> Fallen, Nachweis und die Fragen an den Owner stehen in
> [`uebergabe-bl344-bl354.md`](uebergabe-bl344-bl354.md); die offene
> Übergabe zu `BL-328` bis `BL-343` gilt daneben weiter. Fünf Einträge lassen
> sich auf der Bau-Maschine nicht nachweisen — `BL-345`, `BL-347`, `BL-349`,
> `BL-350` und `BL-353` brauchen Windows (`cmd.exe`, MSYS unter Windows, pwsh,
> die Windows-Konsole), dazu die pwsh-Hälfte von `BL-348`. Die
> Windows-Maschine fährt sie nach dem Bau.

**Stand 2026-10-17 — Triage: vierzehn Meldungen vom 2026-10-12 bis
2026-10-17 lagen ohne Nummer da**, zwölf aus einem neuen Feld und zwei aus
`Feld F`. Sie bekommen `BL-328` bis `BL-341`. Dazu kommen zwei Beifänge:
`BL-342` beim Nachstellen von `BL-328`, `BL-343` im Nachweislauf dieser
Triage. Jede Meldung ist am Code beider Bahnen nachgeprüft
und, wo es ging, auf der bash-Bahn nachgestellt. pwsh ist auf der
Triage-Maschine nicht installiert; die pwsh-Fundstellen sind gelesen, nicht
gefahren.

> **Ein neues Feldkürzel: `Feld G`** — Greenfield, Linux, bash-Bahn:
> Prüfwerkzeuge in Python über den Ausgaben einer Analyse-Werkzeugkette für
> Binärdateien; die Eingaben sind große Fremddaten.
> Sieben Kaskaden vom 2026-10-12 bis zum 2026-10-17, dann abgeschlossen. Seine
> Meldungen trugen noch kein Kürzel („noch keins vergeben"); von dort kommen
> `BL-328` bis `BL-339`. Die Profilzeile steht im
> [README](../README.md#herkunft).

**Was die Triage sortiert hat, nach Wirkung:**

- **Geld falsch gezählt oder ohne Spur:** `BL-339` (Sonnet 5.5 mit doppeltem
  Cache-Read-Satz — jede Messung eines Sonnet-5.5-Transkripts liegt 18 bis
  34 % zu hoch, und die Selbsteichung erklärt die Tabelle für geeicht),
  `BL-330` und `BL-332` (die Aushärtung ist beim Start ungebucht, und der
  Prüfer, der es sagen soll, hält sie 15 Minuten lang für die laufende
  Sitzung), `BL-334` (Exit 2 wegen Einträgen mit null Token, und das Briefing
  liest Exit 2 als „nicht buchen").
- **Still falsch, ohne Signal:** `BL-341` (die Vollautomatik meldet „beendet"
  auf einem roten HEAD), `BL-333` (acht Stufen auf einem Plan außerhalb von
  Git — danach gilt jedes Log des Laufs als älter als die Kaskade), `BL-337`
  (eine späte Hintergrundmeldung ersetzt das Ergebnis; Promise, Turns und
  Fehlerstatus hängen an der zweiten Antwort), `BL-342` (bei einem anderen
  Planordner findet das Beutebuch-Werkzeug still keinen Fund), `BL-336`
  (beide Sweeps ohne den Fokus des Plans).
- **Falscher Befund, der eine Rolle losschickt:** `BL-328` (die Kit-Suite ist
  im Rollenlauf rot und außerhalb grün), `BL-335` (Franks Briefing lässt die
  Gegenprobe eines neuen Werts aus und verlangt dabei eine grüne Suite),
  `BL-343` (ein Kit-Test flackert, weil die mtime eines Logs vor der
  Commit-Sekunde des Plans liegen kann).
- **Anzeige und Bedienung:** `BL-338` (der Abschlussbericht zitiert sich
  selbst), `BL-329` (`--help` endet mit Traceback oder antwortet still falsch),
  `BL-331` (das Architekten-Briefing widerspricht sich).
- **Eine Idee, keine Störung:** `BL-340` — ein Abnahme-Loop, in dem ein Skript
  wartet und eine günstige Rolle urteilt.

> **Drei Startfehler, eine Stelle.** `BL-330`, `BL-333` und `BL-336`
> beschreiben, was die Vollautomatik beim Start nicht prüft, und der
> Wiederanlauf aus `BL-326` sitzt an derselben Stelle. In `Feld G` lief der
> Bau drei Kaskaden hintereinander ohne gebuchte Aushärtung. Die vier bekommen
> eine gemeinsame Startprüfung; Reihenfolge und Exit-Code stehen in der
> Übergabe.

> **Zwei Korrekturen an der offenen Übergabe zu `BL-327`.** Die
> Steuerzeichen-Prüfung sollte an `team_guard_verify` hängen — das rufen nur
> Red Team und Axel, nicht Frank und Ralph, die das Zeichen schreiben
> (`BL-341` zeigt es im Feld). Und der Kit-Test über die eigenen Dateien würde
> mitinstalliert und urteilte dann über das ganze Feldprojekt, genau der
> Fehlermodus aus `BL-340`. Beides ist beim Bau am 2026-10-18 umgesetzt (im
> [Archiv](backlog-archiv.md) bei `BL-327`).

> **Gebaut wird seit 2026-10-18 auf der Linux-Maschine** (Entscheid des
> Owners); die pwsh-Bahn prüft danach die Bau-Maschine. Der Auftrag mit
> Reihenfolge, Fundstellen, Fallen, Nachweis und den Fragen an den Owner steht
> in [`uebergabe-bl328-bl343.md`](uebergabe-bl328-bl343.md); der letzte
> Bau-Commit löscht ihn wieder.

**Stand 2026-10-12 — Triage: zwei Meldungen aus `Feld F` vom 2026-10-10 und
2026-10-11 lagen ohne Nummer da.** Sie bekommen `BL-326` und `BL-327`. Beide
trugen noch kein Kürzel („vergibt der Maintainer"); ihre Lage ist die von
`Feld F`.

- **Still falsch, ohne Signal:** `BL-327` (ein `\b` im regulären Ausdruck wird
  auf dem Weg in die Datei zum Backspace — die Zusicherung kann nie rot werden
  und besteht jede Probe des Teams), `BL-326` (ein abgebrochener Rollenaufruf
  hinterlässt halbe Arbeit, auf der der Wiederanlauf ungeprüft weiterbaut).
- **Geld ohne Spur:** ebenfalls `BL-326` — die Kosten des abgebrochenen
  Aufrufs fehlen im Ledger, und kein Prüfer zeigt die Lücke.

> **`BL-327` steckt auch im Kit.** Der Eintrag `BL-234` im
> [Archiv](backlog-archiv.md) trägt seit dem 2026-10-03 zweimal das Byte 0x08,
> wo `\b` stehen sollte — geschrieben in einer Fix-Sitzung am Kit, von keinem
> Wächter bemerkt. Die Meldung beschreibt also keine Eigenheit des
> Feldprojekts, sondern den Weg, auf dem Agenten Text in Dateien schreiben.

> **Gebaut am 2026-10-18** auf der Linux-Maschine, beide Bahnen geschrieben,
> die bash-Bahn nachgewiesen; die Begründungen stehen im
> [Archiv](backlog-archiv.md). Die Übergabe dazu ist mit dem Bau gelöscht.

**Stand 2026-10-09 — Triage: zwölf Meldungen vom 2026-09-25 bis 2026-10-09
lagen ohne Nummer da.** Sie bekommen `BL-315` bis `BL-325`; der Nachtrag vom
2026-10-09 (Ablehnung durch die Schutzregeln des Modells) teilt die Nummer
seiner Hauptmeldung (`BL-316`). Zwei Meldungen aus `Feld F` trugen noch kein
Kürzel („vergibt der Maintainer") — ihre Lage ist die von `Feld F`, und so
stehen sie hier.

> **Zwei davon sind älter, als ihre Ankunft vermuten lässt.** Die Meldungen
> vom 2026-09-25 (Exit 43, `BL-315`) und vom 2026-09-30 (abgelaufene
> Anmeldung, `BL-316`) wurden im Feld geschrieben und erst am 2026-10-08 ins
> Kit committet. Die Triage vom 2026-10-03 konnte sie nicht sehen;
> `BL-315` beschreibt deshalb einen Fall, für den `BL-281` inzwischen eine
> Antwort hat — der Eintrag sagt, was sie nicht abdeckt.

**Was die Triage sortiert hat, nach Wirkung:**

- **Echtes Geld ohne Grund:** `BL-316` (eine abgelaufene Anmeldung schickt
  den Rest des Laufs über die API, und die Zeile nennt „Timeout/Limit").
- **Still falsch, ohne Signal:** `BL-319` (ein Sweep meldet einen Punkt als
  geprüft, dessen Dateien er nie gelesen hat), `BL-324` (ein Fix unter
  `TEAM_WEITERER_CODE` läuft im Normalfall der Fixphase ohne Suite),
  `BL-317` (die Notiz jeder Sitzung außer der letzten verschwindet aus dem
  Ledger), `BL-318` (der Update-Commit trägt fremde Produktänderungen).
- **Falscher Befund, der einen Menschen losschickt:** `BL-320` (ein fehlendes
  Paket gilt als roter Baum), `BL-323` (der Update-Selbsttest ist rot, ohne
  dass etwas kaputt ist), `BL-322` (`warten` direkt nach `start` sagt „zuerst
  `start`").
- **Bedienung:** `BL-321` (der Kostenabschluss verlangt bei neuer
  Plan-Benennung `--kaskade` von Hand), `BL-315` (Exit 43, den die
  Selbstprüfung selbst auflösen könnte).
- **Ein Wunsch des Owners, keine Störung:** `BL-325` — was ein Programm erst im
  Lauf zeigt, soll aus dem Log belegt werden statt am Bildschirm abgelesen.

> **Am selben Tag abgetragen, alle elf**, in drei Wellen und vier Einzelzügen
> (Begründungen im [Archiv](backlog-archiv.md)). Wo eine Meldung eine schärfere
> Auflage vorschlug, hat zuerst das Kit den Schritt übernommen — Richtung
> „Programm statt Prompt": Die Selbstprüfung wartet selbst auf den verwaisten
> Testlauf (`BL-315`), die Installer messen, was sie geändert haben (`BL-318`),
> die Freigaben gelten für beide Shell-Werkzeuge und abgelehnte Lesebefehle
> werden gezählt (`BL-319`). Beifang: Die README-Zahlen lagen seit `BL-312`
> bis `BL-314` drei Testdateien hinter der Installation, und ein bestehender
> Test (`test_bl19`) schrieb das Fehlverhalten aus `BL-317` fest.

**Stand 2026-10-04 — das erste Update eines Bestandsprojekts mit
Prüfsummenliste (`Feld F`) endete mit rotem Selbsttest, ohne Defekt im
Projekt.** Zwei Bauarten (`BL-307`): Ein Werkzeug las die Kaskaden des
umgebenden Projekts statt der Fixture, und Tests suchten neue Regeln in
Projektdateien, die das Update nicht anfasst. Eine Sandbox mit Vorgeschichte
fand 43 solche Fälle, eine frische Installation keinen. Dazu `BL-308` (der
pwsh-Installer nannte einbahnig „mitinstallierte" .sh-Dateien) und die
Beifänge `BL-309` und `BL-310`. Alle vier am selben Tag abgetragen; der Selbsttest fährt
seither eine vierte Konfiguration, das gealterte Bestandsprojekt. Aus der
Frage danach, warum das Update die gemeldeten Handgriffe nicht selbst
erledigt, wurde `BL-311`: Es trägt jetzt nach, was die Kit-Fassung seit dem
letzten Update neu hat; von Hand bleiben nur echte Konflikte.

**Stand 2026-10-03 — Triage: 28 Meldungen vom 2026-09-17 bis 2026-10-02 lagen
ohne Nummer da.** Sie bekommen `BL-269` bis `BL-292`; zwei davon sind
Nachträge zu einer anderen Meldung und teilen deren Nummer (`BL-270`,
`BL-275`), zwei weitere beschreiben dieselbe Lücke an zwei Dateien
(`BL-269`). Die Meldung vom 2026-09-22 zu `--rollen-abschluss` und zu neuen
Logs gehört zur Übergabe der bash-Maschine (`BL-266`), die im selben Zug
zusammengeführt wird: `BL-265` bis `BL-267` sind abgetragen, `BL-268`
(die Nachverlinkung von dreizehn Altmeldungen) bleibt offen.

> **Ein neues Feldkürzel: `Feld F`** — Greenfield, Windows 11, beide Bahnen
> installiert, gefahren wird pwsh; ein Spielskript-Stack mit Prüfwerkzeug in
> Python. Von dort kommen `BL-264` und `BL-283` bis `BL-292`. Die Profilzeile
> steht im [README](../README.md#herkunft).

> **Und dreizehn ältere lagen unter einer falschen Annahme.** Die Übergabe
> der bash-Maschine führte sie als „triagiert, nur nicht verlinkt" in einer
> gefrorenen Ausnahmeliste. Zugeordnet an distinktiven Fakten statt an
> Titeln: Drei waren triagiert (`BL-192`, `BL-193`, `BL-197`), eine ist die
> Erstmeldung von `BL-218` — und **neun waren nie triagiert**. Sie bekommen
> `BL-293` bis `BL-301`; die Ausnahmeliste ist leer (`BL-268`).

> **Die Warteschlange ist erneut vom Kopf her abgearbeitet worden, nicht von
> vorn.** Am 2026-09-26 wurden `BL-262` und `BL-263` gebaut, während
> 19 ältere Meldungen ohne Nummer daneben lagen — darunter zwei Nachträge, die
> dieselbe Lücke ein zweites und drittes Mal belegten (`BL-275`: der Bericht
> über ein rotes Gate stürzt seit dem 2026-09-17 bei jedem roten Lauf ab). Der
> Wächter, der das künftig am ersten Tag meldet, kommt mit der Übergabe
> (`BL-267`).

**Was die Triage sortiert hat, nach Wirkung:**

- **Still falsch, ohne Signal:** `BL-292` (vier Red-Team-Funde nur im `result`,
  der Sweep meldet „sauber"), `BL-285` (der Grundauftrag aus der
  Konfiguration erreicht die bash-Bahn nie), `BL-283` (die erste Kaskade baut
  ab Stufe 2 ohne Smoke-Test), `BL-269` (zwei Laufzeitartefakte, die der Loop
  sich selbst wegräumt bzw. an denen er sich selbst blockiert).
- **Kaputter Diagnoseausgang:** `BL-275`, `BL-276`, `BL-287`, `BL-290`.
- **Kosten, die nirgends auftauchen:** `BL-272`, `BL-279`, `BL-280`, `BL-291`.
- **Fremde Arbeit in Gefahr:** `BL-271` (Rollback auf einen Commit statt auf
  den Arbeitsbaum), `BL-274` (drei Commit-Stellen ohne Fremdfilter), `BL-270`
  (das Update meldet nicht, was es überschreibt).
- **Vordergrund-Regel, dritte und vierte Lage:** `BL-273`, `BL-281` — die
  Werkzeugfrist ist eine Obergrenze, und die Warteschleife gehört selbst in
  den Vordergrund.
- **Bedienung und Briefings:** `BL-277`, `BL-282`, `BL-284`, `BL-286`,
  `BL-288`, `BL-289`; dazu `BL-278` als angebotener neuer Entrypoint.

> **Am selben Tag in zwei Wellen abgetragen:** zuerst `BL-264` (Prio 1),
> `BL-269`, `BL-275`, `BL-285`, `BL-286`, `BL-287`, `BL-290` und der Beifang
> `BL-302`; dann `BL-272`, `BL-283`, `BL-289`, `BL-291` bis `BL-295`,
> `BL-297`, `BL-301` und der Beifang `BL-303` (Axel meldete eine Akte, die es
> nicht gab). `BL-284` ist teilweise gebaut. Aus der Triage offen sind damit
> 17 — Entwurfsfragen wie `BL-270`, `BL-271`, `BL-278` und die
> Vordergrund-Lagen `BL-273`/`BL-281` darunter.

---

**Stand 2026-08-25 — `BL-146` ist abgetragen, Version 2.13.0 ist geschnitten;
`BL-175`, `BL-176` und `BL-177` kamen am selben Tag aus dem Feld dazu und sind
als 2.13.1 geschnitten.**
`bash bash/kit-test.sh` ist auf dieser Maschine vollständig durchgelaufen:
**11 von 11 Stufen, 141 Prüfungen grün, Exit 0**, 5 h 57 min. Damit ist die
pwsh-Bahn keine Behauptung mit Testkörper mehr.

> **Der Ertrag waren die sechs Läufe, nicht der siebte.** Der Erstlauf hat
> **sechs** Einträge erzeugt (`BL-158` bis `BL-163`), und fünf davon sind auf
> einem Linux-Wirt prinzipiell unsichtbar. Vier Läufe fielen an echten Funden,
> zwei an eigenen Flüchtigkeitsfehlern beim Nachbauen. **Kein fallender Fall
> wurde grün gedreht** — in jedem Fall lag der Fehler im Werkzeug oder in der
> Erwartung, nie im Testkörper.

> **Wer den Selbsttest hier wieder fährt, prüft vorher diese zwei Dinge** — je
> zwei Minuten, sie sparen je einen 20-Minuten-Rundlauf. Zwei der sechs Läufe
> sind genau daran gestorben: eine
> Testdatei, die eine nur im Kit liegende Datei ohne Übersprung öffnet (in der
> installierten Ablage rot statt übersprungen), und eine, die eine
> Platzhalter-Marke **wörtlich** zitiert (Stufe 3 meldet sie als ungefüllt;
> `test_bl153_rueckkanal_meldung.py` löst das seit langem, indem es die Marke
> zur Laufzeit zusammensetzt). Beides kostet sonst je 20 Minuten pro Runde.

**Nachtrag 2026-08-25 — vier Funde aus dem Feld, alle am selben Tag
abgetragen** (`BL-175` bis `BL-177` und `BL-179`, Begründungen im
[Archiv](backlog-archiv.md)). Ausgelöst hat sie eine Frage, keine rote Zeile:
„Hängt der Installer?"

> **Diese vier trugen ursprünglich die Nummern `BL-164`…`BL-168`** und sind
> beim Zusammenführen mit `origin/master` umgezogen (`d05c8d7`): Dieselben
> Nummern waren auf der anderen Maschine bereits für `Feld E` vergeben und
> **gepusht**. Umgezogen ist die ungepushte Seite — dieselbe Regel, die
> `41b2ee0` am selben Tag schon einmal angewandt hat.

- **`BL-176`** — er hing nicht, er war **stumm**. Beide Installer leiteten den
  pytest-Lauf ihres Selbsttests vollständig ins Log um; auf dem Bildschirm
  stand `Selbsttest` und danach minutenlang nichts. Gemessen: 3 min 41, zu
  keinem Zeitpunkt hängengeblieben. Ein stummer Lauf ist von einem hängenden
  nicht zu unterscheiden, und die teure Antwort auf diese Frage ist der Abbruch.
- **`BL-175`** — und im Regressionslauf derselben Sitzung lag der schwerere
  Fund: **`TEAM.md` fiel durch JEDES Update.** Sie wird nur bei der
  Erstinstallation gerendert und steht auch nicht in der Liste „Unangetastet
  geblieben (Projektdaten)" — sie fiel zwischen beide Listen. In der
  einbahnigen Feldablage nannte die alte Fassung damit 15 tote `.sh`-Pfade:
  **genau der Befund, den `BL-139` abgestellt hat.** Der Fix dort setzte am
  Rendern an und erreichte deshalb kein bestehendes Projekt.

- **`BL-177`** — und der Rest davon: `CLAUDE.md` lässt sich **nicht**
  nachziehen, sie trägt Projektarbeit. Ein Projekt, das vor `BL-139` einzog,
  behält seinen kaputten Regeltext, und nichts sagt das. Beide Installer melden
  ihn jetzt beim Update — mit der Zuordnung, aber ohne ihn anzufassen.
- **`BL-179`** — und beim Aufräumen fiel auf, dass die **Selbsttests selbst**
  noch stumm liefen: `kit-test.ps1` 14 Minuten, `kit-test.sh` zweimal in
  Stufe 8 (der schwersten, ~55 min). `BL-176` hatte nur die Installer
  getroffen. Jetzt prüft ein Wächter die Gattung statt der Stellen.
- **`BL-178`** (offen, beim Bauen von `BL-177` gefunden) — `install.ps1` hat
  den Block „Bitte von Hand abgleichen" **gar nicht**, den `install.sh` seit
  langem fährt. Die pwsh-Bahn sagt einem Projekt also nie, dass ihm Regeln aus
  einer neueren Kit-Fassung fehlen. Auf Windows ist die einbahnige pwsh-Ablage
  der Normalfall.

> **Die Lehre ist die von `BL-139`, eine Ebene höher:** Ein Fix an einer
> Vorlage repariert die nächste Installation. Er repariert **keine** Datei, die
> das Update nicht anfasst — und welche das sind, stand nirgends geschrieben.
> `TEAM.md` war in keiner der beiden Listen, weder bei den aktualisierten noch
> bei den geschonten. Beide Installer nennen jetzt in ihrer Hilfe ausdrücklich
> beide Seiten.

**Was noch offen ist: 16 Einträge**, und sie zerfallen in zwei Gruppen.

- **Fünf Bauvorhaben am Kit selbst:** `BL-145` (`kit-test.ps1` auf Deckung
  bringen — 6 von 11 Stufen), `BL-117` (Prompt-Gleichstand am LAUF), `BL-144`
  (die Ausführungsrichtlinie aus dem Feld), `BL-178` (der Abgleich-Block fehlt
  der pwsh-Bahn) und `BL-180` (der README-Zahlenwächter kann Kit- und
  Feldzahlen nicht unterscheiden).
- **Elf Meldungen aus `Feld E`** (`BL-164`…`BL-174`), dem ersten Zielprojekt im
  echten Betrieb — Triage der ersten Betriebs-Meldungen, über `origin/master`
  hereingekommen.

Keiner davon ist ein Rest dieser Version; es sind sämtlich eigene Vorhaben.

---

**Stand 2026-08-24 — die erste Kit-Sitzung auf der Windows-Maschine.** Zwei der
fünf offenen Einträge sind abgetragen, beide vollständig in
[`backlog-archiv.md`](backlog-archiv.md) begründet:

- **`BL-156`** — `install.ps1` beantwortet `-Hilfe`/`-Help`/`-h` mit seinem
  Dateikopf, und der Kopf erklärt endlich `-NurBash`, `-NurPwsh` und
  `-BeideBahnen`. Die Frage, die der Eintrag ausdrücklich hierher verwiesen
  hatte, ist **gemessen** beantwortet: `Get-Help` findet den `<# … #>`-Block
  nicht, solange die `# Bahn:`-Kopfzeile davorsteht. Also derselbe Weg wie in
  bash — die Hilfe liest die eigene Datei.
- **`BL-155`** — die Wurzel-Code-Prüfung aus `BL-52` gibt es jetzt auch auf der
  pwsh-Bahn, mit derselben **Messung** statt einer zweiten Liste (`BL-154`).

> **Die Reihenfolge ist bewusst gegen den Vorschlag von unten gedreht worden.**
> Dort stand `BL-146` (ein Lauf) vor `BL-155`/`BL-156` (Bau), weil der Lauf
> billiger ist. Auf dieser Maschine wäre das der teurere Weg gewesen: Beide
> Bauten fassen `install.ps1` an, und `kit-test.sh` ruft in seinen elf
> Schritten elf Mal einen Installer auf. Ein Lauf **vor** dem Bau hätte den
> geänderten Code gar nicht gesehen und hätte danach ohnehin wiederholt werden
> müssen. Gebaut wurde deshalb zuerst; `BL-146` fährt jetzt über **beides**.

**Der dritte Lauf** (6 h 09 min, 137 Prüfungen grün) erreichte erstmals
**Stufe 11** — die Stufe, auf der laut ihrem eigenen Kommentar „die ganze
pwsh-Bahn ruht" und die auf dieser Maschine nie gefahren worden war. Sie brachte
zwei weitere Einträge, beide im Archiv begründet:

- **`BL-161`** — `$KIT` wanderte roh in ein `pwsh -Command`. PowerShell las den
  POSIX-Pfad als Windows-Pfad und meldete „Cannot find path". Die Folge war
  nicht nur eine rote Zeile: Die Syntaxprüfung sah **null** `.ps1`-Dateien
  statt achtzehn — sie war wirkungslos, nicht bloß rot.
- **`BL-162`** — der Gleichstands-Prüfer **starb an seinem eigenen Befund**.
  `diff` endet mit 1, wenn es Unterschiede gibt; unter `set -euo pipefail` riss
  das den Lauf weg, still und ohne Meldung. Auf Linux nie aufgefallen, weil die
  Bäume dort immer gleich waren. Ein Prüfer, der nur überlebt, solange er nichts
  findet, ist keiner.
- **`BL-163`** — und darunter lag der Befund, den `BL-162` verdeckt hatte: Die
  beiden Installer setzten in **dieselbe Marke verschiedene Werte** ein
  (`TEAM_KIT_PFAD` mit Schräg- bzw. Rückstrichen). Keine der Formen ist kaputt
  — nachgemessen in bash, Python und PowerShell —, aber Stufe 11 stand damit
  auf Windows dauerhaft rot, und der harmlose Unterschied hätte den schädlichen
  verdeckt.

> **`BL-163` ist der erste gemessene Fall der Gattung, die `BL-117` benennt.**
> Dort steht wörtlich: „Setzen die beiden Bahnen in denselben Platzhalter
> **verschiedene Werte** ein … sind die Prompts verschieden und der Test bleibt
> grün." Hier traf es `team.config.*` statt eines Rollen-Prompts — dieselbe
> Mechanik, anderer Adressat. **`BL-117` ist damit belegt, nicht geschlossen.**

**Der zweite Lauf** (5 h 31 min, 118 Prüfungen grün) fiel in **Stufe 10** mit
vier roten Prüfungen. Sie hatten genau **zwei** Ursachen, beide Windows, beide
im Archiv begründet:

- **`BL-159`** — `kit-einrichten.sh` fällte ein POSIX-Urteil über einen
  Windows-Wirt: drei Fehler, „die Maschine ist noch nicht bereit", Abhilfe
  `sudo apt install util-linux`. Die Befunde stimmen, der Schweregrad nicht —
  nativ unter Windows ist die pwsh-Bahn zuständig. Jetzt Warnungen, die **mehr**
  erklären als die Fehler vorher.
- **`BL-160`** — `--verknuepfen` meldete „✓ Verknüpft: … → …" und legte eine
  **Kopie** an: Unter MSYS erzeugt `ln -s` ohne Symlink-Recht keine
  Verknüpfung. Ausgerechnet die Reparatur erzeugte damit die veraltete
  Launcher-Kopie, gegen die sie gebaut ist. Dieselbe Wurzel machte die
  Symlink-Prüfung der Stufe 10 **grün aus dem falschen Grund**.

> **Genau das ist der Ertrag von `BL-146`.** Der Eintrag sagt: „ein fallender
> Fall ist das **erwartete** Ergebnis eines Erstlaufs" — und: „Was dabei nicht
> passieren darf: einen fallenden Fall ‚anpassen', bis er grün ist." Keiner der
> vier wurde angepasst. Zwei waren echte Defekte im Werkzeug, einer eine
> Erwartung, die nur auf POSIX gilt, einer eine Zählprüfung, die „geprüft?" mit
> „bestanden?" verwechselte.

**Dazu ein Eintrag, der schon beim Bauen auffiel und im selben Zug behoben
wurde** — `BL-158`, ebenfalls im Archiv begründet: Die beiden Kit-eigenen
Prüfer (`geteilt/kit-readme-pruefen.py`, `geteilt/kit-regelinventar.py`)
starben unter Windows auf ihrer **Erfolgs**-Spur, weil ihre Häkchen-Meldung
unter cp1252 nicht durch stdout passt. `kit-test.sh` hätte das in Schritt 3 als
„Das README steht gegen die frische Installation" gemeldet — ein inhaltlicher
Befund, den es gar nicht gibt. Der Fix ist die UTF-8-Zeile, die
`team/tools/*.py` seit `BL-133` trägt; der Wächter von damals prüft die
**Gattung**, kannte aber nur eine von zweien.

**Was gefunden wurde, weil gebaut wurde.** `install.ps1` hätte den eigenen
Zustand des Teams als „ungeprüften Projektcode" gemeldet: Unter Windows trägt
eine Punktdatei **kein** Hidden-Attribut, `Get-ChildItem` liefert
`.ralph-state`, `.budget-ledger`, `.gitignore` und `.gitattributes` also ganz
normal mit — in `install.sh` fallen sie nebenbei durch das Glob. Der erste Lauf
hat es sofort gezeigt. Das ist der Fehlermodus, den `BL-154` gerade abgeschafft
hatte (eine Warnung in jedem grünen Projekt erzieht zum Wegsehen), und er wäre
beim bloßen Lesen der bash-Fassung unsichtbar geblieben.

---

**Stand 2026-08-23 — was davor passiert ist.** Eine Kit-Sitzung auf der
Linux-Maschine hat vier Dinge gebaut; die drei mit `BL-`Nummer sind
vollständig in [`backlog-archiv.md`](backlog-archiv.md) begründet:

- **`BL-153`** — der Rückkanal Feld → Kit ist ein **Werkzeug** statt einer
  Konvention: `kit-melden.sh`/`.ps1`/`.cmd`, `team/tools/kit_meldung.py`,
  `TEAM_KIT_PFAD` in beiden Konfigurationen, dazu `CONTRIBUTING.md`,
  `.github/PULL_REQUEST_TEMPLATE.md` und `plans/meldungen/`.
- **`BL-154`** — zwei Abschriften durch Messungen ersetzt: die
  Entrypoint-Ausnahmeliste in `install.sh` und die Entrypoint-Zahlen in
  `kit-test.sh`.
- **`--hilfe` für `install.sh`** (ohne eigene `BL-`Nummer, im CHANGELOG unter
  `[Unreleased]` begründet). Der Installer kann seine Optionen jetzt selbst
  ausgeben, und der Hilfetext **ist** der Dateikopf statt einer zweiten Fassung
  daneben — dieselbe Erwägung wie bei `BL-154`: eine Abschrift läuft
  auseinander. Der Kopf trägt dabei erstmals die **vollständige** Liste;
  `--nur-bash`, `--nur-pwsh` und `--beide-bahnen` standen bisher nur in der
  `Aufruf:`-Zeile und wurden nirgends erklärt.
- **`BL-157`** — beim Fahren des Gates danach gefunden: `kit-test.sh` starb auf
  einer Maschine **ohne** globale Git-Identität mit Exit 128, vor der ersten
  Prüfung. Drei seiner sechs Wegwerf-Repos setzten keine lokale Identität,
  obwohl der Kommentar in Schritt 1 genau das verlangte. Ersetzt durch
  Mechanik (`wegwerf_repo`) plus Wächter — eine Konvention, die nur dasteht,
  wird an der Hälfte der Stellen nicht befolgt.

**Dazu vier Funde aus `Feld E`** (`BL-169`…`BL-172`), dem ersten Zielprojekt
**ohne pytest** — Dart/Flutter mit SQLite. Alle vier stammen aus dem Aushärten
der **ersten** Kaskade, also aus dem Zeitfenster, das ein laufendes Projekt
nicht mehr hat, und alle vier haben dieselbe Bauart: **eine Annahme des Kits,
die stillschweigend Python heißt.** `BL-169` (Ordner-Defaults und
Reproducer-Namensmuster gegen paketgebundene Testsuche) ist der Kern; `BL-171`
(die Kit-Selbsttests verdrahten `.py` und `strict=True`) ist seine Spiegelseite
in der eigenen Suite. `BL-170` ist die vierte Einsetzstelle von
`{{SMOKE_TEST}}`, die der Abtrag von `BL-149` nicht mitgezählt hat — ein
Rollen-Briefing, das kein Mensch gegenliest. `BL-172` ist unabhängig davon: Der
Kaskaden-Fokus verdrängt den projektspezifischen Grundauftrag, statt ihn zu
ergänzen.

> **Was diese vier gemeinsam nahelegen:** Das Kit ist in der **Konfiguration**
> stackneutral und in seinen **Beispielen, Vorgabewerten und Selbsttests** nicht.
> Solange jedes Zielprojekt pytest fuhr, konnte das nicht auffallen — die
> Vorgaben waren dort schlicht richtig. `BL-169` und `BL-171` teilen sich
> deshalb einen Fix: das Namensmuster des Reproducers gehört neben
> `TEAM_TEST_ORDNER` in die Konfiguration, und die Selbsttests lesen es von
> dort, statt es zu wissen.

> **Nachtrag 2026-08-26 — der geteilte Fix war gar nicht nötig, und das ist
> die eigentliche Lehre.** `BL-171` ist abgetragen, **ohne** auf das
> Namensmuster in der Konfiguration zu warten: Die Selbsttests brauchten die
> Endung nie, sie brauchten den **Ordner** — und der steht seit jeher in
> `TEAM_TEST_ORDNER`. Eine Annahme, die niemand braucht, wird nicht
> konfigurierbar gemacht, sondern gestrichen. `BL-169` bleibt davon unberührt
> offen: Dort geht es um die ausgelieferten **Vorgabewerte**, und die sind
> eine echte Entscheidung, keine überflüssige Zusicherung.

**Was das für die Windows-Maschine bedeutet:** Die bash-Bahn ist gefahren
(`kit-test.sh` vollständig grün), die **pwsh-Bahn von `BL-153` ist geschrieben
und nie gelaufen** — sie hängt als Punkt (6) an `BL-146`. `BL-155` und `BL-156`
waren neu und eine andere Klasse: dort fehlte die pwsh-Hälfte ganz. **Beide
sind am 2026-08-24 abgetragen** (siehe oben); offen bleiben `BL-146`, `BL-145`
und `BL-117`.

> **Wenn `BL-146` dort grün ist, ist der Release-Schnitt fällig.** Alles seit
> 2.12.0 liegt im CHANGELOG unter `[Unreleased]`; erst der Windows-Lauf macht
> aus der pwsh-Hälfte eine Zusicherung. Zum Schnitt gehören:
> `## [2.13.0]`-Überschrift im CHANGELOG, das Versions-Badge im README und die
> „Stand: Version …"-Zeile darunter. **Vorher nicht** — eine Version, deren
> zweite Bahn ungeprüft ist, behauptet mehr, als sie hält.

---

**Abtrag 2026-08-21 (Kit-Sitzung nach dem Windows-Pull), abgeschlossen.** Der
Pull selbst hat einen eigenen Fund mitgebracht (`BL-144`: Der Selbsttest der
bash-Bahn war seit `BL-136` rot, weil dessen Erfolgsmeldung einen zweiten
Absender bekam — nachgewiesen war der Fix nur gegen `kit-test.ps1`, das diesen
Schritt gar nicht fährt). Abgetragen in dieser Reihenfolge, die der **Wirkung**
folgt und nicht der Nummer — zuerst, was den dokumentierten Weg blockiert, dann
was falsch bucht, dann was falsch anleitet:

`BL-144` · `BL-142` · `BL-143` · `BL-129` · `BL-140` · `BL-139` · `BL-141` ·
`BL-120`.

**Damit sind alle fünf Feldmeldungen des Tages abgetragen**, dazu die drei
älteren, die es sein konnten.

> ### ⇢ Was auf der Windows-Maschine ansteht
>
> **Alle fünf offenen Einträge gehören dorthin**, und zwar in dieser Reihenfolge —
> vom billigsten zum teuersten. **Nachtrag 2026-08-24:** `BL-155` und `BL-156`
> sind abgetragen; die Reihenfolge wurde dabei gedreht (Bau vor Lauf, Begründung
> ganz oben). Es bleiben `BL-146`, `BL-145` und `BL-117`.
>
> | | Was | Aufwand |
> |---|---|---|
> | `BL-146` | **Einmal `bash bash/kit-test.sh` fahren.** Vier Testfälle und drei Code-Stellen der pwsh-Bahn sind geschrieben und nie ausgeführt — seit `BL-147` dazu die Bahn-Erkennung des Update-Pfads (`Get-KitBahnDateien`, `Test-BahnLiegtDa`, `-BeideBahnen`), seit `BL-150` das neue `team_plankopf_wert` in `lib.psm1` samt zwölf Testfällen und der fett gesetzte Trockenlauf-Plankopf in `kit-test.ps1`, **seit `BL-153` die gesamte pwsh-Hälfte des Rückkanals** (`kit-melden.ps1`/`.cmd`, `{{KIT_PFAD}}` in `Setze-Werte`, die neue Zeile in `team.config.ps1`). Kein Bau, nur Ausführung — und ein fallender Fall ist das **erwartete** Ergebnis eines Erstlaufs | ein Lauf |
> | `BL-155` | **`install.ps1` kennt die Wurzel-Code-Prüfung aus `BL-52` gar nicht.** Kein Erstlauf-Punkt, sondern eine fehlende Hälfte — Bau. Aufgefallen bei `BL-154`, wo die bash-Fassung repariert wurde | ~~Bau, klein~~ **abgetragen 2026-08-24** |
> | `BL-156` | **`install.ps1` hat kein Gegenstück zu `--hilfe`** — und sein Kopf nennt die drei Bahn-Schalter gar nicht. Wie `BL-155` eine fehlende, keine ungeprüfte Hälfte | ~~Bau, klein~~ **abgetragen 2026-08-24** |
> | `BL-145` | **`kit-test.ps1` auf Deckung bringen.** Er fährt 6 von 11 Schritten und 15 von 127 Prüfungen — das ist der strukturelle Grund, warum `BL-136` als „grün" galt, während die bash-Bahn rot war | Bau, gestaffelt |
> | `BL-117` | **Prompt-Gleichstand am LAUF statt am Quelltext.** Braucht beide Shells auf **einer** Maschine | Bau |
>
> **Warum sie hier liegen bleiben mussten:** Auf der Entwicklungsmaschine liegt
> kein PowerShell 7. `BL-117` warnt selbst davor, ihn ohne eine zu schreiben —
> „ein blind geschriebener Test, dessen erste Ausführung auf einer fremden
> Maschine stattfindet, wird dort *angepasst* statt gelesen". Das ist die Lehre
> aus `BL-113`, und sie hat dieses Repo bereits einmal Geld gekostet. Dieselbe
> Lehre gilt für `BL-145` und für das Lesen von `BL-146`.
>
> **Die Regel, die bis dahin gilt:** Ein Fix an gemeinsamem Code ist erst
> nachgewiesen, wenn **`kit-test.sh`** gelaufen ist — nicht, wenn `kit-test.ps1`
> grün meldet. Genau diese Verwechslung war `BL-144`.

**Was der Abtrag über die Einträge hinaus gefunden hat** — jeder dieser Punkte
ist erst beim Bauen aufgefallen, nicht beim Lesen:

| Fund | Wo |
|---|---|
| `--architekt-abschluss` warf **alle** Zusatzschalter weg, auf beiden Bahnen — derselbe Fehler wie `BL-26`, nur nie nachgezogen. Ein `--auth`, das der Alias erbt, aber der Wrapper wegwirft, wäre ein Fix, der sich nur im Unit-Test beweist | `BL-143` |
| Ein grüner Test schrieb die Fehlbuchung **fest** (`auth == "api"`) und war Teil des Grundes, warum sie niemandem auffiel | `BL-143` |
| Der `BL-130`-Wächter suchte zeilenweise und schlug an einem **korrekten** Aufruf Fehlalarm — ein Wächter mit Fehlalarmen wird abgeschaltet | `BL-143` |
| `BL-129` war zur Hälfte schon von `BL-130`/`BL-133` miterledigt; die 109 roten Tests waren null. Was **wirklich** fehlte, war die Zusicherung — und der Satz „bewusst nicht geprüft" war still zur Falschaussage geworden | `BL-129` |
| Der Fix zu `BL-140` ist **nicht** mechanisch: Zwei Stellen hätte ein Such-und-Ersetze kaputtgemacht, und daraus folgt eine Regel mit **drei** Sorten statt zwei | `BL-140` |
| Die Spiegelseite von `BL-139` in der `--nur-bash`-Richtung — vom Feld nie gemeldet, weil dort nur pwsh läuft | `BL-139` |

Und zweimal hat eine neue Zusicherung **sich selbst** gefangen, bevor sie etwas
anderes fangen konnte: Der `BL-142`-Riegel hätte eine von drei Stellen gesehen
(zwei standen hinter einem Semikolon), und die `BL-140`-Notationstabelle fiel
durch die eigene Prüfung, weil sie eine echte Nummer als Beispiel nannte.

**Stand 2026-08-21: fünf Meldungen aus dem Feld dazu** (`BL-139` bis `BL-143`),
alle aus `Feld B` — einer frischen, mit `--nur-pwsh` installierten
Ablage, die an diesem Tag ihre **allererste** Kaskade geplant, gebaut und
abgeschlossen hat. `BL-139`/`BL-140` fielen beim **Anlegen** auf, `BL-141` bis
`BL-143` im **Closeout**.

Der Tag zerfällt in zwei Gruppen. **Die Vorlagen** (`BL-139`, `BL-140`, in
`bootstrap/`) schicken die Rollen an Dateien und Nummern, die es so nicht gibt —
still, ohne Meldung. **Beide sind abgetragen**: die Nummern stimmen wieder,
und die Pfade nennen die Bahn, in der sie stehen. **Die Kostenkette** (`BL-141`–`BL-143`, in
`geteilt/tools/kosten.py` und `team-status.ps1`) ist der eigentliche Fund des
Tages: Der erste echte Kostenabschluss eines Projekts hat sie alle drei
aufgedeckt, und keiner davon war vorher zu sehen, weil sie erst beim
**vollständigen** Durchlauf zuschlagen — `BL-142` brach genau bei dem Aufruf
ab, den die Doku vorgibt (abgetragen), `BL-143` buchte Abo-Kosten in die
API-Spalte (abgetragen), und
`BL-141` lieferte die Zahl, die dort landet, als Zeilen-Churn-Proxy statt als
Messung. Wer eine Kaskade zu Ende führte, traf alle drei nacheinander — **alle
drei sind abgetragen**, und die Messung liegt jetzt als Werkzeug im Kit
(`kosten.py sitzung-messen`).

`BL-139` war der inhaltliche Zwilling von `BL-129` (beide abgetragen) — dort
fiel die einbahnige Ablage im Testharnisch auf, hier im Regeltext, den jede
Rolle in jedem Aufruf im Systemprompt hat.

**Stand 2026-08-20: drei offene Einträge** (`BL-117`, `BL-120`, `BL-129` — die
letzten beiden am 2026-08-21 abgetragen; `BL-117` bleibt und kann hier nicht
fallen, siehe unten).
`BL-120` war am selben Tag beim Doku-Durchgang dazugekommen und hatte mit dem
Rest dieses Tages nichts zu tun: ein Gerüst, das erst eine Frage trug. Die drei
dort benannten Kandidaten sind geschrieben; das Gerüst darüber hinaus bleibt
bewusst leer.
`BL-121` (Ordneranlage im Interview), `BL-122` (Exit-Code als Ausnahme),
`BL-123` (blanker `pwsh`-Aufruf), `BL-124` (pytest nicht gefunden) und
`BL-125` (`kosten.py` unter Windows nicht ladbar) und `BL-126` (ein
einbahnig pwsh installiertes Projekt war nicht aktualisierbar) sind am
selben Tag entstanden und **noch am selben Tag abgetragen** worden — alle
sechs aus dem Feld, von derselben echten Windows-Maschine. `BL-127` und
`BL-128` sind beim **Trockenlauf zu `BL-126`** herausgefallen: nicht durch
Lesen, sondern durch einen Lauf mit einem Schalter, den sonst niemand
benutzt. `BL-129` ist der Rest desselben Laufs und bleibt offen. An diesem Tag sind
`BL-111`, `BL-112`, `BL-114`, `BL-115`, `BL-116`, `BL-118` und `BL-119`
abgetragen worden. `BL-117` bleibt und ist beim Abtragen von `BL-112` als
ausgewiesener Rest entstanden — die Hälfte der Zusicherung, die sich nur auf
einer Maschine mit PowerShell 7 beweisen lässt. Alle Begründungen stehen im
Archiv.

> **Der Rest, den dieser Tag hinterlässt, ist derselbe wie `BL-117`:** Die
> pwsh-Bahn hat mit `BL-118` einen strukturellen Umbau und mit `BL-119` einen
> neuen Schalter bekommen, und beides ist auf dieser Maschine nur **statisch
> gelesen**, nicht gefahren. `kit-test.sh` Stufe 11 (Gleichstand der
> Installer) braucht PowerShell 7 und wird hier übersprungen.

> **Faellig auf der bash-Maschine, 2026-08-27 — und der einzige Punkt, der
> NICHT in der Tabelle steht. Am 2026-08-28 abgetragen, bis auf den Rest, der
> PowerShell 7 braucht.** `BL-190` war abgetragen und der Fix bewiesen, aber auf
> einer Maschine **ohne** `flock` — also genau dort, wo der Fund entstand. Was
> dort nicht laufen konnte, ist die **Gegenrichtung**: Wo `flock` da ist, muss es
> weiter genommen werden. Der Fall dazu
> (`test_bl190_sperre_ohne_flock.py::test_team_lock_mit_flock_nimmt_weiter_flock`)
> ist auf einem Linux-Wirt **mit** `flock` jetzt **gruen gefahren** statt
> uebersprungen. Dazu stand ein vollstaendiger `bash bash/kit-test.sh` aus, seit
> dem 2026-08-24 nicht mehr gefahren; er ist jetzt durch — **11 von 11 Stufen,
> 134 Pruefungen gruen, Exit 0**, 4 min 02.
>
> **Der Ertrag war nicht der gruene Lauf, sondern die zwei Abbrueche davor.** Der
> Selbsttest kam zweimal nicht bis Stufe 3, und beide Male an einer Zahl, die am
> Vortag auf der pwsh-Bahn gruen gemeldet worden war: die Dateizahl (README 169,
> Installation **175**) und die Testfallzahl (README 1054, Installation **1053**,
> an vier Stellen). Daraus ist `BL-208` geworden. **Was weiter aussteht**, und nur
> das: die zwei Uebersprünge dieses Laufs, beide mit benanntem Grund — die
> Wurzel-Code-Pruefung der pwsh-Bahn (`BL-155`) und der Gleichstand der beiden
> Installer (Stufe 11), samt der Gegenprobe, die `BL-178` ausdruecklich einer
> bash-Sitzung hinterlassen hat (*beide Installer gegen dieselbe Installation,
> dieselbe gemeldete DATEI*). **Dazu gekommen ist der end-zu-end-Beleg von
> `BL-208`** — dass `kit-test.ps1` die Dateizahl WIRKLICH rot meldet, nicht nur
> laut Quelltext. Alle vier brauchen PowerShell 7 auf demselben Wirt; auf
> dieser Maschine ist `pwsh` nicht installiert. **Ein Lauf traegt sie alle ab:**
> `bash bash/kit-test.sh` auf einer Windows-Maschine, danach
> `pwsh -File pwsh/kit-test.ps1`. Steht hier und nicht im
> Archiv, weil das Archiv **nachgeschlagen** wird und nicht gelesen: Ein Rest, den
> nur der Eintrag kennt, den niemand mehr oeffnet, ist keiner.

**Stand 2026-08-28, zweiter Teil — die vier pwsh-seitigen Einträge sind
abgetragen.** `BL-199`, `BL-198`, `BL-196` (Teile 1+2) und `BL-200`. Drei davon
waren derselbe Rest: **`kit-test.ps1` sicherte weniger zu als `kit-test.sh`,
und das stand nirgends** — die Gattung von `BL-145`. Die pwsh-Bahn prüft jetzt
das README nach (neuer Schritt 5/9, vier Gegenproben) und räumt ihre
Abgleichsablagen weg.

> **`BL-199` ist der Eintrag, dessen erste Frage keine technische war** — soll
> „eine Pipeline zur Zeit" bahnübergreifend gelten? Beantwortet ist sie mit
> einer **Messung** statt mit einer Meinung: `/proc/<pid>/winpid` liegt unter
> Git for Windows vor, und PowerShell findet den bash-Prozess darüber
> (Hin- und Rückweg nachgemessen). Damit war Variante (a) des Eintrags
> gangbar, und Variante (b) — die `FileShare::None` gekostet hätte — nicht
> nötig. Die Grenzen stehen in `doku/anhang-a.md`: Unter Linux hält
> bahnübergreifend keine der beiden Proben.

> **Zwei Wächter haben beim ersten Lauf sofort Befunde geliefert**, und beide
> sind der Beleg für ihren Eintrag: Der README-Wächter fand **drei** veraltete
> `BL-1`…`BL-N`-Spannen (199/153/146 statt 207), und der Schlüsselmengen-Test
> fand die zwei Stellen, an denen die Konfigurations-Vorlagen auseinanderlaufen
> — beide begründet, beide jetzt namentlich mit Grund festgehalten.

**Stand 2026-08-28 — die beiden Meldungen dieses Tages sind abgetragen.**
`BL-206` (Befund 1) und `BL-207` (beide Richtungen) sind gebaut, auf **beiden
Bahnen**, mit je einem Regressionstest, der die Gegenrichtung mitfaehrt — bei
`BL-206` „der Sweep committet seinen eigenen Reproducer WEITER", bei `BL-207`
„ein wirklich roter Baum bleibt rot und ein gruener wird weiter quittiert".
Ohne die zweite Richtung wird ein Fix dieser Gattung gruen, indem die geprüfte
Stelle aufhoert zu arbeiten. Beide Gegenproben sind gegen den alten Stand
gefahren: `BL-206` sechs fallende Faelle, `BL-207` acht.

> **Was von diesen beiden bewusst offen bleibt** — es steht in der Tabelle und
> nicht nur hier: **Befund 2 von `BL-206`** (ein Commit waehrend des Laufs
> ueberlebt den Rollback nicht) ist eine Entwurfsfrage; bis sie entschieden
> ist, traegt `bootstrap/TEAM.md` die Handregel. Und **`BL-201`** ist durch
> `BL-207` nur zur Haelfte mit abgetragen: Frank kennt die Auflage jetzt,
> `harry`/`marv`/`axel` nennen sie in ihren Briefings weiterhin nicht.

> **Der Beleg dieses Tages ist die Kit-Suite, nicht `kit-test.sh`.** Gefahren
> ist `python -m pytest geteilt/tests` auf der Windows-Maschine; der
> vollstaendige `bash bash/kit-test.sh` steht weiter aus (siehe den Absatz
> darueber). Zwei Faelle von `BL-207` **uebersprangen** dabei auf der
> bash-Bahn mit benanntem Grund: Die MSYS-`ps` von Git for Windows kennt kein
> `-o` und zeigt keine Kommandozeilen — auf dieser Bahn dieses Wirts ist ein
> Parallellauf nicht feststellbar. Auf der pwsh-Bahn desselben Wirts laufen
> sie, und unter Linux laeuft die bash-Bahn.

**Stand 2026-08-28, dritter Teil — der ausstehende bash-Lauf ist nachgeholt,
und er hat sich sofort bezahlt gemacht.** `bash bash/kit-test.sh` ist auf einem
Linux-Wirt vollstaendig durchgelaufen: **11 von 11 Stufen, 134 Pruefungen
gruen, Exit 0**, 4 min 02. Zwei Uebersprünge, beide mit benanntem Grund und
beide `pwsh`-abhaengig (Wurzel-Code-Pruefung der pwsh-Bahn, Gleichstand der
Installer). Dazu ist die `flock`-Gegenrichtung aus `BL-190` erstmals **gefahren**
statt uebersprungen.

> **Der Ertrag waren die zwei Abbrueche, nicht der dritte Lauf** — dieselbe
> Lehre wie am 2026-08-25, eine Ebene weiter. Der Selbsttest kam zweimal nicht
> bis Stufe 3, und beide Male an einer Zahl, die am Vortag auf der **anderen
> Bahn** gruen gemeldet worden war. Das ist kein Zufall und keine
> Unaufmerksamkeit: `kit-test.ps1` prueft von den drei Zahlen-Gattungen nur
> zwei, und die Zahl der Testfaelle zaehlt in der Kit-Ablage anders als in einer
> Installation. Beides steht als `BL-208` in der Tabelle. **Die Gattung ist die
> von `BL-145`** — gruen bedeutet auf den beiden Bahnen verschieden viel —, und
> sie ist damit an einer Stelle wieder aufgetaucht, die `BL-198` am Vortag
> ausdruecklich geschlossen hatte.

**Stand 2026-08-28, vierter Teil — sechs Eintraege abgetragen, alle auf beiden
Bahnen und jeder mit gefahrener Gegenprobe.** `BL-197`, `BL-201`, `BL-205`,
`BL-208`, `BL-169` und `BL-202` (samt `BL-209`, das beim Bauen des letzten
herausfiel). Damit stehen noch **vier** offen, und sie zerfallen in
zwei Gruppen, die verschieden behandelt gehoeren.

> **Der Ertrag von `BL-202` war nicht die Umbenennung, sondern ihre Praemisse.**
> Der Eintrag sagt *„Keine Mechanik haengt am Praefix"* — sie sitzt an SECHS
> Stellen ueber beide Bahnen, und in allen sechs ist „nichts gefunden" ein
> GUELTIGER Wert. Die vorgeschlagene Umbenennung haette die Ableitungen also
> nicht kaputt gemacht, sondern **stumm gestellt**: leerer Ledger-Notiztext,
> „noch keine Aussage moeglich" bei der Altlast-Kennzahl, `None` bei
> `kaskade_beginn` — und damit `BL-45` und `BL-27` ohne Stimme. Daneben fiel
> `BL-209` heraus, das **schon heute** trifft: derselbe Aufruf hatte auch den
> ORDNER verdrahtet, obwohl das Interview ihn abfragt. Wer einen Eintrag
> abtraegt, prueft seine Begruendung mit — sie ist eine Beobachtung, kein
> Befund.

- **Drei warten auf eine ENTSCHEIDUNG, nicht auf Arbeit.** `BL-206` (Befund 2)
  ist eine Entwurfsfrage zum Rollback-Schnappschuss; `BL-194` sagt selbst
  *„Erst entscheiden, welche der beiden Bauformen gefahren wird, dann bauen"*;
  und `BL-193` Weg (2) kostet eine **Formataenderung am Ledger** — der Eintrag
  legt fest, dass darueber erst nach `BL-197` Teil (1) zu befinden ist, und
  genau das ist jetzt der Fall. Teil (1) holt einen guten Teil seines Nutzens,
  **ohne** das Format anzufassen; ob der Lueckenfinder den Preis noch wert ist,
  ist damit eine offene Frage an den Owner und keine offene Arbeit.
- **Zwei sind Arbeit.** `BL-202` ist reine Semantik ohne Fehlverhalten und
  traegt seine niedrige Prioritaet selbst. `BL-204` ist der teurere: Phase 4 aus
  der Vollautomatik in die Bibliothek zu ziehen ist ein Umbau am **Geld
  ausgebenden** Pfad — die Schleife ruft Frank und Axel. Ein solcher Umbau,
  nur statisch belegt, ist genau die Gattung, bei der dieses Kit sonst einen
  Menschen im Lauf haben will; er gehoert an eine Sitzung, in der ein echter
  Lauf danebengefahren werden kann.

**Stand 2026-09-03 — acht liegengebliebene Meldungen aus `Feld E` eingereiht
(`BL-215`…`BL-222`).** Sie lagen seit dem 2026-08-29 als Dateien unter
`plans/meldungen/`, ohne je eine Nummer bekommen zu haben: Der Rückkanal hat
sie abgelegt, die Triage ist zwischen zwei Fix-Sitzungen durchgefallen. Sechs
davon sind älter als `BL-210`, das am 2026-08-31 eingereiht wurde — die
Warteschlange wurde also nicht von vorn abgearbeitet, sondern vom Kopf.

> **Das ist derselbe Ausgang, den `BL-210` beschreibt, eine Ebene höher:** Was
> nicht an einer Mechanik hängt, wird übergangen. Eine Meldung wird per
> `kit-melden ablegen` committet, die `BL-n`-Zeile schreibt ein Mensch von
> Hand, und nichts vergleicht die beiden Mengen. **Ein Wächter, der
> `plans/meldungen/*.md` gegen die in `backlog.md`/`backlog-archiv.md`
> verlinkten Dateinamen hält, hätte alle acht am ersten Tag genannt** — er
> gehört auf dieselbe Liste wie der README-Zahlenwächter (`BL-198`).

- **Zwei bilden ein Paar und gehören zusammen gebaut** — `BL-220` und `BL-221`,
  beide `--rollen-abschluss`, beide eine Fehlzuordnung im Kaskadenfeld, beide
  still und beide erst beim Closeout sichtbar.
- **`BL-218` ist der Zwilling von `BL-213`** aus dem anderen Feld: dieselbe
  Stelle, derselbe Irrtum („ein einzelner erklärbarer Ausreißer wird zur
  Aussage über die TABELLE"), und `BL-211` verweist schon darauf. Die drei
  gehören zusammen entschieden, nicht nacheinander.
- **`BL-222` ist die billigste und die mit dem schlechtesten Verhältnis von
  Aufwand zu Schaden** — zwei Zweige in einem Dispatcher gegen ein falsches
  Erfolgssignal auf jedem Buchungsverb.
- **`BL-219` ist keine Arbeit, sondern eine Entscheidung** und als einziger
  Eintrag eine Idee statt eines Fehlers. Sein Fund — der Kaskadenplan ist das
  einzige Artefakt ohne prüfende Gegenrolle — steht unabhängig von der
  Rollenidee, die ihn zutage gefördert hat.

**Noch am selben Tag abgetragen: sieben der acht, dazu `BL-213`.** Im Archiv
begründet: `BL-215`, `BL-216`, `BL-217`, `BL-218`, `BL-220`, `BL-221`,
`BL-222` — und `BL-213`, das mit `BL-218` an derselben Stelle fiel. **Offen
bleibt allein `BL-219`**, und das aus dem Grund, den es selbst nennt: Es ist
eine Entscheidung des Owners, keine Arbeit. `bash bash/kit-test.sh` ist
danach vollständig durchgelaufen.

> **Der Ertrag war auch hier nicht der grüne Lauf, sondern zwei Abbrüche
> davor** — und beide sind alte Bekannte:
>
> - **Die Zahlen des READMEs standen wieder gegen die Installation.** Drei neue
>   Testdateien heben die Dateizahl (181 → 184), die Testdateizahl (125 → 128)
>   und die Fallzahl (1141 → 1178). Der Wächter aus `BL-198`/`BL-208` hat alle
>   drei gefangen, bevor sie behauptet wurden — genau wofür er gebaut ist.
> - **Zwei neue Testfälle waren in einer einbahnigen Ablage rot statt
>   übersprungen**, weil sie `team-status.ps1` ohne Übersprung öffneten. Das ist
>   wörtlich der Ausrutscher, vor dem der Kopf dieser Datei warnt, und er hat
>   auch diesmal genau eine Runde gekostet.

> **Zwei Stellen sind beim Abtragen aufgefallen und stehen NICHT als eigener
> Eintrag da, weil sie zu bestehenden gehören:**
>
> - **Ein grüner Test hat die Fehlbuchung von `BL-221` festgeschrieben.**
>   `test_bl27_vergessener_abschluss.py` verlangte wörtlich `returncode == 0`
>   und trug den Kommentar *„Kein Abbruch: gebucht wird trotzdem, der Mensch
>   entscheidet"*. Der Mensch KANN dort nicht entscheiden — wenn er den Hinweis
>   liest, ist gebucht und archiviert. Dieselbe Bauart wie das `auth == "api"`
>   aus `BL-143`: eine Zusicherung, die den Fehler konserviert, statt ihn zu
>   fangen.
> - **Der Beifang von `BL-215` ist der Rest von `BL-169`.** Beide
>   Red-Team-Briefings und `bootstrap/CLAUDE.md.vorlage` verlangen weiter
>   `xfail` mit `strict=True`, und das Reproducer-Namensmuster trägt weiter
>   `.py`. Das ist kein Textfehler, sondern ein ausgelieferter Vorgabewert —
>   und damit dieselbe Entscheidung, die `BL-169` offen hält.

> **Der Abtrag hat einen eigenen Fund erzeugt: `BL-223`** (im
> [Archiv](backlog-archiv.md) begründet, noch am selben Tag abgetragen). Die
> Rückfrage lautete „Haben die ganzen Skripte jeweils eine help flag?" —
> und die Antwort war schlechter als erwartet: Von vierzehn Einstiegspunkten
> hatten **drei** eine Hilfe, und die fünf Rollen-Skripte lasen ihre Argumente
> **überhaupt nicht**. `./ralph.sh --hilfe` startete damit einen bezahlten
> Rollenlauf. **Das ist `BL-222` eine Stufe teurer** — dort kostete der stille
> Ausgang eine falsche Statusausgabe, hier einen Modellaufruf. Der Fund wäre
> ohne die Rückfrage nicht entstanden: `BL-222` war abgetragen, der Wächter
> stand, und niemand hätte die Nachbarn nachgemessen.

**Nachtrag desselben Tages — die vier abtragbaren Feld-B-Einträge sind
abgetragen: `BL-210`, `BL-211`, `BL-212` und `BL-214`** (Begründungen im
[Archiv](backlog-archiv.md)). `BL-212` war dabei fast geschenkt: Der
Phasen-Zeiger aus `BL-217` weiß genau, welche Phase erreicht wurde, und
`BL-212` ist die Frage, ob der Bericht das auch sagt.

> **Beim Abtragen von `BL-214` fiel seine Prämisse.** Der Eintrag beschreibt
> eine Asymmetrie zwischen `frank.ps1` und `ralph.ps1` — nachgemessen fehlte
> der vierte Ausgang auch `frank.sh`. Es war keine **Bahn**-Asymmetrie,
> sondern eine **Rollen**-Asymmetrie auf beiden Bahnen, und ein Fix nur auf der
> pwsh-Seite hätte die bash-Hälfte des Schadens stehen lassen. Dieselbe Lehre
> wie bei `BL-202`: Wer einen Eintrag abträgt, prüft seine Begründung mit.

> **`BL-211` ist bewusst NICHT durch Zurückdrehen des Kit-Satzes abgetragen.**
> Der mit `BL-166` gesenkte Wert ist für das Feld richtig, das ihn ausgelöst
> hat; für das meldende Feld ist er um 33,3 % falsch. **Beide haben recht** —
> sie rechnen gegen verschiedene Verträge ab. Eine zentrale Zahl kann das nicht
> auflösen, also darf ein Projekt sie überschreiben (`TEAM_PREISE`). Das ist
> die einzige der drei vorgeschlagenen Richtungen, bei der kein Feld auf den
> nächsten Kit-Entscheid warten muss.

**Was offen bleibt — fünf Einträge, und bei vieren ist die ENTSCHEIDUNG der
offene Teil, nicht die Arbeit.** Jeder dieser Einträge sagt das selbst:

| Nr | Was fehlt | Warum es hier nicht abgetragen wurde |
|---|---|---|
| `BL-193` | Weg (3), der Lückenfinder | Kostet eine **Formatänderung am Ledger**. Der Eintrag legt fest, dass darüber erst nach `BL-197` Teil (1) zu befinden ist — das ist jetzt der Fall, und die Frage ist damit fällig, nicht erledigt |
| `BL-194` | zwei Bauformen | *„Erst entscheiden, welche der beiden Bauformen gefahren wird, dann bauen"* — wörtlich der Eintrag |
| `BL-204` | Phase 4 in die Bibliothek | Umbau am **Geld ausgebenden** Pfad. In dieser Sitzung ist Phase 4 bereits zweimal geändert worden (`BL-210`, `BL-214`); ein dritter, rein statisch belegter Eingriff wäre genau die Gattung, bei der dieses Kit sonst einen Menschen im Lauf haben will |
| `BL-206` (2) | Rollback-Schnappschuss | Entwurfsfrage. Die Handregel steht bis dahin in `bootstrap/TEAM.md` |
| `BL-219` | Abnahme-Gate | Eine **neue Rolle**, kein Fix — das ist eine Kaskade, keine Sitzungsaufgabe. Der Schnitt, den das Feld empfiehlt, steht im Eintrag |

> **Und eine Beobachtung, die kein eigener Eintrag ist, aber dieselbe Bauart
> hat:** Elf Zeilen dieser Tabelle tragen im Status „erledigt 2026-08-28" und
> stehen trotzdem noch hier statt im Archiv. Wer die Datei nach „was ist offen"
> liest, liest damit 18 Zeilen, von denen 5 gemeint sind. Genau diese
> Unlesbarkeit hat die acht Meldungen aus `Feld E` durchfallen lassen. Sie
> gehören beim nächsten Durchgang verschoben — nicht in dieser Sitzung, weil
> die Statustexte fremde Entscheidungen zusammenfassen und ein falsch
> verschobener Eintrag aus der Arbeitsliste verschwindet.

> **Das Zeilenlimit der Briefings hat zwei dieser Fixes zugeschnitten, und das
> gehört festgehalten.** `BL-215` und `BL-216` gehören beide in Prompts, die
> 45 Zeilen nicht überschreiten dürfen — Frank lag exakt auf der Grenze, Harry
> und Marv bei 44. Der Umfang der neuen Regeln ist deshalb **nicht** frei
> gewählt: Er ist gegen Straffungen an anderer Stelle eingetauscht. Weggefallen
> ist dabei keine Regel und keine Begründung, und `kit-regelinventar.py` prüft
> genau das mit — es hat eine umformulierte NORM-Zeile sofort gemeldet.

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-205 | **Frank hat keine Regel fuer eine schon vor ihm rote Suite — und stellt headless Rueckfragen, die niemand liest.** Schritt 1 seines Auftrags traegt `$SMOKE_SUFFIX` (`pwsh/lib.psm1:227`, bash-Gegenstueck gleich): *„Smoke-Test gruen: <befehl>.“* Die Auflage ist **absolut** und kennt den Fall nicht, dass die Rotheit **nicht von Frank** stammt; `geteilt/prompts/rolle-frank.md` sagt dazu nichts. Damit misst sie eine Eigenschaft der **Maschine** statt eine des Fixes — und trifft ausgerechnet den Lauf, in dem die Rolle richtig gearbeitet hat. **Zweiter Teil, gleiche Wurzel:** Frank kennt genau zwei Ausgaenge (Promise / kein Promise). Fuer *„Hindernis, aber unterwegs einen echten neuen Fehler gefunden“* gibt es keinen — der Beifang endet im gitignorierten Log | `Feld B`, 2026-08-27 — Frank hatte einen fertigen, nachweislich nicht-regressiven Diff; die Suite war unabhaengig von ihm rot (ambiente Umgebungsvariable leckte in eine In-Prozess-Testbank). Er brach regelkonform ab und stellte **zwei Rueckfragen an einen Menschen, den es im headless Lauf nicht gibt** — u. a. die Bitte, den nebenbei entdeckten zweiten Fehler vormerken zu duerfen. Kostenpunkt: 2,7517 USD verworfen und im Folgeaufruf neu bezahlt; der zweite Fehler wurde nur gerettet, weil ein Mensch spaeter das Log oeffnete. Voller Hergang: [`plans/meldungen/2026-08-27-frank-hat-keine-regel-fuer-eine-schon-vor-ihm-rote-suite-und.md`](meldungen/2026-08-27-frank-hat-keine-regel-fuer-eine-schon-vor-ihm-rote-suite-und.md) | **erledigt 2026-08-28 — alle drei vorgeschlagenen Zeilen, auf beiden Bahnen.** **(1) Differenzmessung statt Absolutwert:** `$SMOKE_SUFFIX` sagt jetzt, dass eine schon VOR Frank rote Suite **kein Abbruchgrund** ist — er misst beide Staende und belegt, dass durch SEINEN Fix kein NEUER Fehlschlag entsteht. Die Faehigkeit war da: Frank kennt seinen Ausgangs-Commit ueber `team_guard_begin` ohnehin, es fehlte nur die Auflage. **(2) Der dritte Ausgang:** Findet Frank unterwegs einen echten zweiten Fehler, legt er dafuer einen NEUEN Fundblock mit Status `offen` an und **fixt ihn nicht** — das bestaetigt *Finder ist nicht Fixer*, statt es zu verletzen. Vorher endete der Beifang im gitignorierten Log und wurde nur gerettet, weil ein Mensch spaeter das Log oeffnete. **(3)** *„Es liest niemand mit "— stelle KEINE Rueckfragen, entscheide belegbar und schreibe auf, was du entschieden hast."* **Wo es gelandet ist, und warum nicht im Briefing:** (1) in beiden Bibliotheken, (2) und (3) im **Auftragstext** beider Frank-Entrypoints. `rolle-frank.md` liegt exakt auf dem harten 45-Zeilen-Limit, und ein Briefing liegt in JEDEM Prompt seiner Rolle; der Auftragstext traegt ohnehin die laufspezifischen Auflagen und ist nicht laengenbegrenzt. Regressionstest `test_bl205_frank_kennt_die_schon_rote_suite.py`, **11 Faelle**, darunter die Gegenrichtung, dass `BL-205` die aeltere Vordergrund-Auflage aus `BL-207`/`BL-201` in derselben Zeile **nicht verdraengt** — ein Zusatz, der die aeltere hinausdraengt, tauscht einen Fehler gegen einen anderen. **Gegenprobe gefahren:** gegen den alten Stand fallen 9 von 11; die zwei gruenen sind die Gegenrichtungen |
| BL-203 | **Das README macht das Diff-Lesen zur Betriebsbedingung — der Owner selbst betreibt das Kit anders.** `README.md` (Abschnitt „Fuer wen“, Zeilen 44–53) schreibt: *„Wer den Diff nicht liest, kann diese Fragen nicht beantworten“*, ausdruecklich als **Betriebsbedingung**. Der Betreiber von `Feld B` liest den Diff kaum bis gar nicht — bei vier gebauten Kaskaden, ~19 abgearbeiteten Funden und erteilten Abnahmen. Die Bedingung ist also nicht verletzt, sondern **falsch benannt**: Geurteilt wird an den Stellen, die das Kit selbst bereitstellt — Reproschritte (Fund echt oder Rauschen), Reproducer-Test (Ursache oder Symptom), Stufen-Zusicherung und UAT (abnahmereif), Kostenbuchfuehrung (war es das wert). Bedingung ist die **Faehigkeit**, im Zweifel hineinzusehen, nicht die **Taetigkeit** | `Feld B`, 2026-08-27 — Aussage des Betreibers: *„Ich lese den Code kaum bis gar nicht. Aber ich kann es jederzeit, wenn ich will. Das T.E.A.M. mit den entsprechend faehigen Modellen ist eher eine weitere Abstraktionsschicht als eine Ergaenzung zum Coden.“* Voller Hergang samt Formulierungsvorschlag: [`plans/meldungen/2026-08-27-readme-beschreibt-das-diff-lesen-als-betriebsbedingung-der-o.md`](meldungen/2026-08-27-readme-beschreibt-das-diff-lesen-als-betriebsbedingung-der-o.md) | **erledigt 2026-08-28 — im README umgesetzt.** Der freigegebene Wortlaut steht im Abschnitt „Fuer wen", aufgeteilt in zwei Absaetze (die Rolle, dann das *Warum trotzdem „erfahren"*). **Zwei Folgestellen mitgezogen**, die dieselbe Aussage trugen und sonst zwei Absaetze spaeter widersprochen haetten: der Regiepult-Absatz (*„liest den Diff und gibst die naechste Stufe frei"* -> *„urteilst am Ergebnis"*) und die Pruefeinheit unter „Der Antrieb" (*„Menge, die ein Stakeholder noch lesen und verantworten kann"* -> verantworten zuerst, lesen als Rueckfallweg *wenn es klemmt*). Die Bestandsaufnahme der Meldung nannte nur die eine Stelle; ein `grep` auf *Diff* fand drei |
| BL-202 | **Kaskaden-Plandateien heissen `ralph-kaskade-N-<thema>.md`, obwohl sie das ganze Team binden.** Der Name nennt **eine** Rolle; das Dokument bindet alle: Ralph liest die Stufenbloecke, Harry/Marv beziehen ihren Sweep-Fokus aus dem Plankopf, Frank arbeitet gegen dieselben Zusicherungen, der Architekt schreibt das Abschluss-Doc gegen den Stufenbogen, und der Mensch entscheidet an dieser Datei, was ueberhaupt gebaut wird. Keine Mechanik haengt am Praefix — es steht nur in Vorlagen und Anleitungen (`bootstrap/CLAUDE.md.vorlage`, `bootstrap/TEAM.md`, `bootstrap/roadmap-skizzen.md`, `geteilt/prompts/rolle-architekt.md`, die Entrypoints beider Bahnen, `install.sh`, `lib.sh` sowie mehrere `geteilt/tests/` als Beispielwert) | `Feld B`, 2026-08-27, beim Schreiben der fuenften Kaskade. Voller Hergang: [`plans/meldungen/2026-08-27-kaskaden-plandateien-heissen-ralph-kaskade-n-obwohl-sie-das.md`](meldungen/2026-08-27-kaskaden-plandateien-heissen-ralph-kaskade-n-obwohl-sie-das.md) | **erledigt 2026-08-28 — aber ANDERS als vorgeschlagen, weil die Praemisse des Eintrags falsch war.** **Der Eintrag sagt: *„Keine Mechanik haengt am Praefix."* Das stimmt nicht** — sie sitzt an SECHS Stellen ueber beide Bahnen: `kaskade_beginn()` in `kosten.py` (darauf stuetzen sich der Zeitraum-Abgleich aus `BL-45` und die P1b-Pruefung aus `BL-27`), `team_architekt_kaskade` und `team_bau_notiz` in `lib.sh` (`BL-34`), die Altlast-Kennzahl in `team-status.sh`, und die drei pwsh-Gegenstuecke. **Warum das schlimmer ist als ein Fehler:** In allen sechs Faellen ist „nichts gefunden" ein GUELTIGER Wert — eine benannte Kaskade hat keine Nummer, ein frisches Projekt keine Plandatei. Die naive Umbenennung haette die Ableitungen also nicht kaputt gemacht, sondern **stumm gestellt**. **Deshalb war der Fix nicht die Umbenennung, sondern die TOLERANZ:** Alle sechs Stellen erkennen jetzt beide Formen, `kosten.py` haelt sie in `PLAN_PRAEFIXE` an EINER Stelle (`BL-154`). Erst danach ist in den VORLAGEN umbenannt (`bootstrap/`, `rolle-architekt.md`, README, `ralph.sh`-Kopf, `install.sh`-Abschlusstext); Bestandsprojekte behalten ihre Dateinamen, und ein eigener Fall haelt fest, dass die historischen Verweise im Kit-Archiv **nicht** mitumbenannt werden — sie sind die Spur, und die Spur ist hier das Produkt. **Zweiter Fund derselben Zeile, und er trifft SCHON HEUTE (`BL-209`):** `kaskade_beginn()` hatte auch den ORDNER als Literal (`"plans"`), obwohl `TEAM_PLAN_ORDNER` im Interview abgefragt wird. **Jedes Projekt mit einem abweichenden Planordner hat `BL-45` und `BL-27` seither stumm.** Beide `team.config.*` exportieren den Wert jetzt, wie `TEAM_DOMAENEN` daneben. **Am VERHALTEN belegt, nicht nur am Quelltext:** vier Kombinationen aus Praefix und Ordner durch `kaskade_beginn` gefahren — gegen den alten Stand liefert genau EINE einen Zeitstempel, die anderen drei `None`. Dazu die Gegenrichtung: eine benannte Kaskade (`post-20`) muss weiter `None` liefern, sonst datiert der Abgleich auf eine Datei, die die Kaskade gar nicht eroeffnet hat. Regressionstest `test_bl202_plandatei_traegt_beide_praefixe.py`, **23 Faelle**; gegen den alten Stand fallen 20, die drei gruenen sind die Gegenrichtungen |
| BL-201 | **Die Vorsorge gegen den vierten Ausgang fehlt im Briefing der bauenden Rolle — das Kit kennt ihn nur als Nachsorge.** `BL-41` erkennt den vierten Ausgang zuverlaessig und gibt dem Menschen eine Pruefreihenfolge. Die **vorbeugende** Auflage steht in der `CLAUDE.md`-Vorlage (*„Der Smoke-Test laeuft im **Vordergrund**, nie als Hintergrund-Task und nie mit einem Wakeup darauf"*) — im Briefing `rolle-ralph.md` (39 Zeilen) steht sie **nicht**: kein Treffer fuer Vordergrund, Hintergrund, Wakeup, Monitor oder 43. Die Rolle erreicht die Regel damit nur ueber einen Abschnitt, der ihr einleitend sagt, er betreffe groesstenteils die Shell und nicht sie. Die Doku-Hygiene sieht die Briefings ausdruecklich als den Weg vor, auf dem eine Rolle ihre Auflagen erhaelt. **Nebenbefund, der die Diagnose verteuert:** Die Selbstpruefung meldete im selben Atemzug „Smoke-Test ist ROT", obwohl der Baum gruen war — sie wertete den **unfertigen** Hintergrundlauf als roten Test. Die anschliessende Pruefreihenfolge bietet dann zwei Zweige, die **beide einen roten Baum voraussetzen**; der zweite („Stufe neu bauen") haette eine fertige, bezahlte Stufe weggeworfen | `Feld B`, 2026-08-27 — Bestandsprojekt im vierten Kaskadenlauf (Windows, pwsh-Bahn, Python+Electron, ~120 Tests). Die Stufe war vollstaendig gebaut, aber uncommittet; das Log meldete `subtype: success` ohne Promise, 59 Turns, 1,93 USD verloren. Aufgeloest hat den Fall **allein** das Feld `result` im Lauf-Log, das die Anleitung nicht erwaehnt — dort stand die Ursache woertlich. Voller Hergang: [`plans/meldungen/2026-08-27-die-vorsorge-gegen-den-vierten-ausgang-fehlt-im-briefing-der.md`](meldungen/2026-08-27-die-vorsorge-gegen-den-vierten-ausgang-fehlt-im-briefing-der.md) | **erledigt 2026-08-28 — beide Teile, mit einer benannten Abweichung vom Vorschlag.** **(1)** Die Auflage steht jetzt in **vier** Briefings (`ralph`, `axel`, `harry`, `marv`), fuenf Zeilen, mit Grund (*headless, keine Benachrichtigung, das Log meldet trotzdem *`subtype: success`), Preis (19,47 USD) und **Ausweg** — das Zeitlimit wird auf `TEAM_SMOKE_TEST_TIMEOUT` aus `{{KONFIG}}` gehoben, statt in den Hintergrund auszuweichen (die Naht zu `BL-207`: eine Auflage, die nicht einhaltbar ist, erzeugt genau das Verhalten, das sie verbietet). **Frank steht bewusst NICHT dabei, und das ist die Abweichung:** Er traegt sie seit `BL-207` **woertlich zur Laufzeit** in Schritt 1 seines Auftrags (`$SMOKE_SUFFIX`) — genau weil er den Smoke-Test oefter faehrt —, und sein Briefing liegt **exakt** auf dem harten 45-Zeilen-Limit. Das Limit ist keine Formsache: Ein Briefing liegt in JEDEM Prompt seiner Rolle. Ein Zusatz, der eine andere Zusicherung bricht, ist keiner — dieselbe Abwaegung, die `test_bl165` fuer `BL-167` schon einmal getroffen hat. Ein eigener Fall sichert die Ausnahme ab, sonst waere sie ein Loch. **(2)** Die Nachsorge behauptet nicht mehr, als sie weiss: Die Meldung zum vierten Ausgang nennt jetzt das Feld `result` — den einzigen Ort, an dem im Feld die Ursache stand und den die Anleitung nirgends erwaehnte —, und die Rot-Meldung der Selbstpruefung ist **relativiert** (*„Miss im VORDERGRUND nach, bevor du den Befund verwendest"*). Ohne das liest sich ein Befund als sicher, der es nicht ist, und schickt den Menschen in den Pruefzweig, der eine fertige, bezahlte Stufe wegwirft. Beides auf BEIDEN Bahnen, mit Gleichstands-Fall. **Beim Bauen fast eine andere Zusicherung gerissen:** Der erste Wurf haengte allen fuenf Briefings einen 13-zeiligen Absatz an und schob vier ueber das Limit — der Fall dagegen steht jetzt in der Datei, damit die naechste Ergaenzung es sofort merkt statt erst im Suite-Lauf. Regressionstest `test_bl201_vordergrund_auflage_in_allen_briefings.py`, **23 Faelle**. **Gegenprobe gefahren:** gegen den alten Stand fallen 21 von 23; die zwei gruenen sind die Gegenrichtungen (Frank hatte die Auflage zur Laufzeit schon, das Limit galt schon) |
| BL-200 | **Ein `--update` traegt neue Konfigurationswerte nicht ins Feldprojekt nach — und liefert damit Fixes aus, die es im selben Zug wieder aufhebt.** Der Grundsatz *„`--update` fasst `team.config.*` nicht an"* ist richtig; die Datei traegt Projektwerte. Es gibt aber **keinen Schritt, der die SCHLUESSELMENGE abgleicht**: Ein Wert, den die Vorlage neu einfuehrt, erreicht eine bestehende Installation nie — und wird auch nicht gemeldet. **Gemessen im Feld, nicht vermutet:** Nach dem Update fehlten in `team.config.ps1` **vier** Werte, die die Vorlage inzwischen setzt: `TEAM_MELDUNG_TOOL` (`BL-182`) — **hart**, `Team-Werkzeug ''` laeuft in `& $null` und bricht ab, fuer JEDES Verb des Rueckkanals; `TEAM_KIT_PFAD` (`BL-153`) und `TEAM_FELD_KUERZEL` (`BL-168`) — **still**, `--kit ''` bzw. `--kuerzel ''`; `TEAM_CLAUDE_BIN` (`BL-173`) — **gnaedig**, `lib.psm1` faellt auf `'claude'` zurueck. **Der Fall ist deshalb schaerfer als er aussieht:** `BL-182` ist im Kit vollstaendig gebaut und mit fuenf Pruefrichtungen belegt — im Feld hat das Update den Fix ausgeliefert und den Fehler mit **woertlich derselben** Meldung wiederhergestellt, nur eine Zeile tiefer (`lib.psm1:146` statt `kit-melden.ps1:37`). Jeder kuenftige Fix, der einen neuen Konfigurationswert einfuehrt, ist im Feld ab dem Update **ein Regress statt eines Fixes**, und welche Klasse er trifft, entscheidet der Zufall. **Der Schnitt, der hier fehlt, steht im Haus:** `Python-Abgleich` (`BL-133`) ist woertlich derselbe Gedanke — *„`--update` fasst `team.config.*` nicht an" ist richtig; „sieht sie gar nicht an" war es nicht* —, nur fuer **einen** Wert. **Nebenbefund an genau dieser Funktion:** Die kopierbaren Zeilen, die sie ausgibt, nennen `TEAM_BEUTEBUCH_TOOL` und `TEAM_KOSTEN_TOOL`; `TEAM_MELDUNG_TOOL` ist seit `BL-182` die dritte Zeile derselben Bauart und fehlt dort. **Warum die Suite es nur zufaellig fand:** Gefangen hat den harten Fall ausschliesslich die Gegenrichtung eines mitgelieferten Falls (`test_bl182…::test_die_werkzeugzeile_steht_in_der_konfiguration`, „man darf (1) nicht durch Loeschen gruen machen") — und die gibt es nur, weil dieser eine Fund sie zufaellig brauchte. Fuer `BL-153`, `BL-168` und `BL-173` existiert nichts Vergleichbares; genau diese drei fehlten im Feld **wochenlang unbemerkt**. Der Riegel `test_jeder_konfigurationswert_steht_in_der_exportliste` prueft bereits **eine** Richtung dieser Gattung (*was die Konfiguration setzt, muss die Modulgrenze ueberleben*); die Gegenrichtung — *was die Vorlage setzt, muss die Installation haben* — ist ungeprueft, und sie ist die, die im Feld zuschlaegt | `Feld B`, 2026-08-27 — beim Regressionslauf direkt nach einem `--update`: **ein** roter Fall von 390, `test_bl182_rueckkanal_auf_der_pwsh_bahn.py::test_die_werkzeugzeile_steht_in_der_konfiguration`. Die drei stillen Werte fielen erst beim Nachsehen wegen des vierten auf. Meldung: `plans/meldungen/2026-08-27-ein-update-traegt-neue-konfigurationswerte-nicht-ins-feldpro.md` | **erledigt 2026-08-28 — alle drei Teile.** **(1)** `konfig_abgleich` / `Konfig-Abgleich` in BEIDEN Installern: `--update` vergleicht die `$TEAM_*`-Namen der Vorlage mit denen der installierten Konfiguration und meldet die fehlenden **namentlich**, mit der Zeile aus der VORLAGE daneben (steht darin noch ein Platzhalter, wird das ausdruecklich gesagt). **Gemeldet, nicht repariert.** Ein Wert, der ohne Inhalt HART abbricht, bekommt einen roten Befund — erkannt an der GATTUNG (`*_TOOL`: eine leere Werkzeugzeile laeuft in einen Aufruf ohne Programm) und nicht an einer Namensliste. **(2)** Die Gattung als Test: Was die Bibliothek liest, ohne einen eigenen Rueckfall zu setzen, steht in der Vorlagen-Konfiguration — und die Schluesselmengen beider Bahnen sind deckungsgleich **bis auf zwei begruendete Ausnahmen**, die namentlich mit Grund in der Testdatei stehen: `TEAM_PYTHON` (nur bash — dort erledigt die Wortzerlegung der Shell den Rest) und `TEAM_MELDUNG_TOOL` (nur pwsh — dort braucht es ganze Werkzeugzeilen, `BL-182`). Ein zweiter Fall prueft, ob eine Ausnahme noch gilt; eine Ausnahmeliste, die niemand nachprueft, ist eine Erlaubnis mit unbekanntem Umfang. **(3)** Die kopierbaren Zeilen in `python_abgleich` nennen `TEAM_MELDUNG_TOOL`. Regressionstest `test_bl200_konfig_abgleich.py`, 10 Faelle, mit der Gegenprobe des Eintrags: eine praeparierte Installation ohne den Wert schlaegt namentlich an, dieselbe **vollstaendig** schweigt. Gegenprobe gefahren |
| BL-199 | **Die pwsh-Bahn sieht die Sperre der bash-Bahn nicht — und seit `BL-190` gibt es diesen Fall überhaupt erst.** Beide Bahnen liegen nach einer Installation im **selben** Arbeitsbaum (`BL-126`: jeder Installer schreibt beide Konfigurationen). Die Zusicherung heisst *„eine Pipeline zur Zeit"*, nicht *„eine je Bahn"*. Seit `BL-190` sperrt die bash-Bahn ohne `flock` über `.team-loop.lock.d`; die pwsh-Bahn kennt nur `.team-loop.lock` — an **drei** Stellen: `lib.psm1` (`team_lock`, `FileStream` mit `FileShare::None`), `entry/team-status.ps1` (Zeile ~104, „Pipeline: läuft/idle") und `install.ps1` (Zeile ~1080, der `BL-10`-Schutz vor einem Update in einen laufenden Lauf hinein). Ein bash-Lauf auf einer Windows-Maschine ist für alle drei **unsichtbar**: Der Kontostand meldet *idle*, und `install.ps1 --update` legt uncommittete Dateien in `team/` ab — genau der Schaden, gegen den `BL-10` gebaut wurde. **Der naheliegende Fix trägt nicht, und das ist der eigentliche Inhalt dieses Eintrags:** Die pwsh-Seite kann die hinterlegte PID **nicht auswerten**. **Gemessen am 2026-08-27, nicht vermutet:** Eine laufende Git-Bash meldete `$$` = `15946`; `Get-Process -Id 15946` in PowerShell auf derselben Maschine, zur selben Zeit, fand **nichts**. MSYS führt einen **eigenen Prozessraum**, und seine PID ist keine Windows-PID. Ein `Get-Process`-Test würde damit **jede** gehaltene bash-Sperre als verwaist einstufen — die Zusicherung wäre nicht wiederhergestellt, sondern schriftlich abgeschafft. **Ehrlichkeitshalber:** Der umgekehrte Weg war auch vorher nicht zugesichert. `FileShare::None` wird nur von **Windows** durchgesetzt; unter Linux erzwingt .NET es nicht, und `flock` ist kooperativ. Bahnübergreifend hat die Sperre also **nie** gehalten. Neu ist nur, dass es jetzt zwei verschiedene **Artefakte** gibt und der Fall damit sichtbar wird | Kit, 2026-08-27 — beim Bauen von `BL-190` aufgefallen, als die drei bash-seitigen Aufrufstellen der Frage *„läuft gerade eine Pipeline?"* nachgezogen wurden. Der Eintrag `BL-190` schreibt ausdrücklich *„Was NICHT betroffen ist: die pwsh-Bahn (sie sperrt über einen eigenen Weg)"* — das stimmte für den **Fund** und stimmt für die **Reparatur** nicht mehr, weil sie ein zweites Sperrartefakt eingeführt hat. **Gemessen:** Der PID-Namensraum-Befund oben (`$$` = 15946 in Git-Bash, `Get-Process -Id 15946` in PowerShell leer, beide gleichzeitig auf derselben Maschine). **Nicht aus dem Feld:** Es ist kein Vorfall gemeldet, und der Fall setzt voraus, dass jemand auf einer Windows-Maschine die bash-Bahn **und** die pwsh-Bahn im selben Arbeitsbaum fährt — auf Windows ist die bash-Bahn laut Zwei-Bahnen-Tabelle die zweite Wahl. Das senkt die Wahrscheinlichkeit, nicht den Schaden | **erledigt 2026-08-28 — Variante (a) des Eintrags, nachdem sie nachgemessen wurde.** **Die Entwurfsfrage ist beantwortet und steht geschrieben** (`doku/anhang-a.md`, Abschnitt „Die Reichweite der Sperre"): Sie gilt bahnuebergreifend, MIT benannten Grenzen. **Der PID-Weg ist doch gangbar** — gemessen am 2026-08-28, Hin- und Rueckweg: `/proc/<pid>/winpid` liegt unter Git for Windows vor, und `Get-Process -Id <winpid>` findet den bash-Prozess. Die bash-Bahn legt `winpid` deshalb zusaetzlich zu `pid` ab; die pwsh-Seite wertet sie aus. **Und die Gegenrichtung fiel dabei mit ab:** Ein Schreib-Oeffnen von `.team-loop.lock` scheitert unter Windows mit *„Device or resource busy"*, solange die pwsh-Bahn sie mit `FileShare::None` haelt — `flock` sieht das nicht, das Betriebssystem schon. Damit sehen sich beide Bahnen gegenseitig, ohne dass `FileShare::None` aufgegeben wird; Variante (b) haette genau das gekostet. **`team_pipeline_laeuft` hat jetzt DREI Zustaende** (0 laeuft / 1 nicht / 2 unklar) und existiert erstmals auch auf der pwsh-Bahn; alle drei Aufrufstellen fragen sie: `install.ps1` bricht bei 2 ab (Vorsicht ist beim `BL-10`-Schutz die richtige Richtung, und die Meldung nennt das Entfernen von Hand), `team-status.ps1` meldet **unbekannt** statt einer Behauptung. **Was NICHT gilt, steht ebenfalls dort:** Unter Linux setzt .NET `FileShare::None` nicht durch und `flock` ist kooperativ — bahnuebergreifend haelt dort keine der beiden Proben. Regressionstest `test_bl199_sperre_ueber_beide_bahnen.py` (15 Faelle, davon einer die Messung selbst) mit der Gegenrichtung: sauberer Baum schweigt, eine VERWAISTE Sperre blockiert nicht dauerhaft. Gegenprobe gefahren: gegen den alten Stand fallen 12 Faelle |
| BL-198 | **Der README-Wächter deckt die Testzahlen ab, aber nicht die zwei Backlog-Zahlen daneben — und meldet trotzdem „alle Zahlen sind gemessen".** `geteilt/kit-readme-pruefen.py` prüft drei Gattungen, und zwar richtig: Testfälle, Testdateien, installierte Dateien. Alle drei bekommen ihre Sollzahl aus einer **frischen Installation** (`bash/kit-test.sh` Zeile ~354). Zwei weitere Zahlen im selben README behaupten dasselbe über dasselbe Kit und werden von **niemandem** gemessen: die Spanne `BL-1`…`BL-<N>` (Zeile ~343) und die Zahl der Archiv-Einträge (Zeilen ~114 und ~345, zweimal dieselbe Zahl in freier Prosa). Beide sind aus dem Repo in einer Zeile ableitbar — `grep -c '^| BL-' plans/backlog-archiv.md` und die höchste vergebene Nummer über Backlog **und** Archiv. **Nicht vermutet, sondern eingetreten:** Am 2026-08-26 kam `BL-196` dazu, das README nannte weiter `BL-195`, und alle drei Doku-Wächter blieben grün. Gefunden wurde es beim Eintragen von `BL-197` — von Hand, nicht vom Wächter. **Die schärfere Hälfte ist die Schlusszeile.** `main()` hängt jede Zahlenprüfung an ein `if a.<zahl> is not None`, druckt am Ende aber unbedingt `✓ README: alle genannten Pfade existieren, alle Zahlen sind gemessen.` Ohne Argumente — also bei jedem Aufruf von Hand, und genau so wird er nach einer Doku-Änderung aufgerufen — läuft **keine einzige** Zahlenprüfung, und die Erfolgszeile behauptet trotzdem, alle seien gemessen. Das ist die Gattung von `BL-145`: Zwei Aufrufwege desselben Skripts sichern verschieden viel zu, und beide melden dasselbe Grün. **Und es gibt eine zweite Hälfte, die schwerer wiegt als die erste — sie ist ebenfalls `BL-145`s Gattung, nur an einer Stelle, die dort nicht mitkam:** Die drei Zahlen, die der Wächter *kann*, prüft **nur `kit-test.sh`** (Zeile ~354). `kit-test.ps1` prüft das README an **keiner** Stelle. Auf einer pwsh-Maschine ist die Drift damit **strukturell unsichtbar**, und auf der bash-Maschine kostet der Nachweis Stunden. **Gemessen am 2026-08-27, nicht vermutet:** Das README nennt `757 Regressionstests` (zweimal, dazu im Badge), `97 Testdateien` und `153 Dateien`; gemessen an einer **frischen Installation** — also so, wie `kit-test.sh` es tut — sind es **973 Fälle**, **113 Testdateien** und **169 Dateien**. Die Badge-Zahl steht seit `6f48dec` (Kit `2.13.1`) unverändert; seither sind **216 Fälle**, **16 Testdateien** und **16 ausgelieferte Dateien** dazugekommen, ohne dass ein Wächter angeschlagen hat. Der Selbsttest der bash-Bahn wäre in Schritt 3 seither **rot** — gefahren hat ihn seit dem 2026-08-24 niemand. **Und ein vierter Fall derselben Gattung stand daneben:** Der Absatz, der die Trägerregel aus `BL-180` erklärt, führte als Gegenbeispiel die nackte Zahl „86 Tests" an — und wurde vom Wächter zu Recht als unqualifizierte Aussage über das Kit gemeldet. Die Regel verletzte ihr eigenes Beispiel, und niemand hat es gesehen, weil niemand den Wächter mit Argumenten gefahren hat | Kit, 2026-08-27 — beim Verbuchen der Feld-E-Meldung zu `BL-197`. Nicht aus dem Betrieb: Beim Nachziehen der README-Zahlen fiel auf, dass die Spanne noch `BL-195` sagte, obwohl `BL-196` seit dem Vortag im Backlog steht — und dass `kit-readme-pruefen.py` das folgenlos durchwinkt und danach „alle Zahlen sind gemessen" druckt. **Gezählt, nicht geschätzt:** Von den fünf Zahlen, die das README über sich selbst behauptet, sind drei gemessen und zwei nicht; die Doku-Wächter laufen nach **jeder** Doku-Änderung, also lief der Wächter über die falsche Zahl mindestens einmal hinweg | **erledigt 2026-08-28 — alle drei Teile.** **(1)** `kit-readme-pruefen.py` misst die zwei Backlog-Zahlen jetzt SELBST aus dem Repo (`backlog_zahlen()`), statt sie sich uebergeben zu lassen: Der Backlog des Kits wird nicht mitinstalliert, und ein Aufrufer, der sie ableiten muesste, koennte es anders. Zwei Gattungen, positiv geprueft — die Spanne erkennt man an ihrem ANFANG (`BL-1`…), damit ein Feldbeleg wie `BL-158`…`BL-168` nicht mitgemeldet wird (`BL-180`). **Der Waechter hat beim ersten Lauf sofort DREI veraltete Stellen gefunden** (199/153/146 statt 207) — der Beleg fuer den Eintrag, gefunden von der Mechanik statt von Hand. **(2)** Die Schlusszeile nennt die gemessenen Gattungen beim Namen und sagt ausdruecklich „KEINE Zahl geprueft", wenn keine lief. **(3)** `kit-test.ps1` prueft das README als eigener Schritt 5/9, mit vier Gegenproben (verfaelschte Testzahl, verfaelschte BL-Spanne, verfaelschte Archivzahl, dazu die Gegenrichtung „das unveraenderte README bleibt gruen"). **(4) Im vollen Suite-Lauf nachgebessert:** Der erste Wurf forderte die zwei Zahlen UNBEDINGT ein — auch bei einem `--readme`, das nicht auf das README des Kits zeigt. Das tut es regelmaessig (beide Selbsttests fahren ihre Gegenproben an einer KOPIE, `BL-180` an einem Fixture aus zwei Zeilen), und der Waechter schlug damit an einer RICHTIGEN Datei rot an — die Bauart aus `BL-180`, ohne Absicht wiederhergestellt. Getrennt sind jetzt die zwei Haelften: ein falscher WERT ist ueberall rot, das EINFORDERN einer fehlenden Zahl gilt nur fuer `KIT/README.md`. Regressionstest `test_bl198_readme_zahlen_vollstaendig.py`, 12 Faelle — die Gegenrichtung braucht ein Mini-Kit im tmp-Verzeichnis (Pruefer + `plans/` + README), weil ein Test am echten README die Regel nur bestaetigen koennte, indem er es verstuemmelt. Gegenprobe gefahren |
| BL-197 | **Die Buchungsregel für eine Sitzung ohne Closeout hängt an einer Erinnerung statt an einem Ereignis — und ihr Ausfall ist im Bericht baulich unsichtbar.** `BL-165` hat die Regel ins Architekten-Briefing gebracht: *„Eine Sitzung ohne Closeout bucht ihre Kosten selbst"*, samt Befehl und Begründung. Der Melder **hat** sie — er ist auf `2.13.1`, er zitiert sie wörtlich, er hat sie verstanden. Sie hat trotzdem an **einem Tag zweimal** nicht gegriffen. **Der Unterschied ist nicht Disziplin, sondern Auslöser.** Ein Closeout hat einen: Die Kaskade ist fertig, der Loop meldet Feierabend, das Briefing verlangt ein Abschluss-Doc, und der Kostenabschluss steht als Punkt 2 in derselben Liste. Eine reine Planungs- oder Nachbesserungssitzung hat keinen — sie **endet einfach**, der Mensch schliesst das Fenster, sobald der Plan committet ist, und in diesem Moment liest niemand mehr eine Regel. **Erschwerend baut das Kit den Fall selbst:** Das Briefing empfiehlt „nach einem gebuchten Closeout eine **neue** Sitzung für die nächste Kaskade" — die Empfehlung erzeugt genau die Sitzung, die die Regel abfangen soll, und beide stehen im selben Dokument. **Der zweite Halbsatz ist der schwerere, und er ist im Quelltext nachgeprüft, nicht geglaubt:** `ledger_pruefen()` P1 stuft eine fehlende `architekt`-Zeile als **Hinweis** ein (`geteilt/tools/kosten.py`, Zeilen ~697–703: *„Legitim, wenn der Architekt fuer diese Kaskade nichts abzurechnen hatte"*). Und der Kontostand zeigt **ausschliesslich** `[WARNUNG]`-Zeilen — `bash/entry/team-status.sh` Zeile ~271 filtert auf `*WARNUNG*`, `pwsh/entry/team-status.ps1` Zeile ~237 auf dasselbe Muster. **Ein Hinweis erscheint im Regelbericht also nie.** Die Schwere ist damit keine Beschriftungsfrage, sie entscheidet zwischen *unsichtbar* und *sichtbar*. An der Stelle steht stattdessen `Architekt K<N> (Churn-Proxy, nicht im Gesamt enthalten)` (`bash/lib.sh` Zeile ~1456, dokumentiert in `doku/faq.md` Zeile ~412) — eine Schätzung, die aussieht wie eine Erfassung. **Abgrenzung zu `BL-193`, denn die beiden sehen sich ähnlich und sind es nicht:** `BL-193` beschreibt die **Messung** — `sitzung-messen --projekt .` liest nur das zuletzt geänderte Transkript, die Aushärtung liegt zwei Sitzungen zurück. Dieser Eintrag beschreibt den **Anlass zu messen**. Beide Wege, die `BL-193` gebaut hat, setzen voraus, dass jemand im richtigen Moment daran denkt; keiner von beiden bringt einen Auslöser mit | `Feld E`, 2026-08-26, beim Öffnen des Closeouts der **siebten** Kaskade (Kit `2.13.1`, Linux, bash-Bahn, Flutter/Dart mit SQLite, Abo-Auth, Ledger seit der ersten Kaskade lückenlos geführt). Das Ledger hatte für diese Kaskade keine `architekt`-Zeile, obwohl der Plan zwei Tage zuvor ausgehärtet und committet war. Die Suche nach dem Grund förderte einen **zweiten** Fall desselben Tages zutage. **Gemessen, nicht geschätzt:** Sitzung A (Nachlauf zur vorigen Kaskade — zwei Handprüfungen am Gerät, ein Hilfsskript auf echte Exit-Codes umgebaut, zwei Meldungen ans Kit) **36,22 USD**; Sitzung B (Aushärtung der nächsten Kaskade — Prototyp-Abgleich und Plandokument) **7,68 USD**; zusammen **43,90 USD** Abo-Gegenwert, die nie im Ledger standen. Beide Sitzungen waren regulär, produktiv und haben committet — keine hat gebucht. **Gerettet wurde der Betrag nur durch einen Zufall:** `sitzung-messen` liest benannte Transkripte, und die zwei Dateien lagen noch da. Der Regelfall ist ein anderer — ohne Argument liest das Werkzeug das **zuletzt geänderte** Transkript, und das ist beim nächsten Closeout ein drittes. Reiht sich in die Grössenordnung aus `BL-193` ein: dort **10,65 USD** und **39 %** der Architektenkosten einer Kaskade, frühere Aushärtungen desselben Projekts zwischen **8,7 und 34,8 USD**. **Lokal nichts gepatcht**, ausdrücklich mit Begründung: Der Fund steckt im Briefing, also im Kit; ein lokaler Eingriff hätte die bekannte Verfallszeit beim nächsten `--update` — Meldung: `plans/meldungen/2026-08-26-eine-sitzung-ohne-closeout-hat-keinen-ausloeser-der-sie-zum.md` (nachverlinkt 2026-10-03, `BL-268`) | **erledigt 2026-08-28 — Teile (1) und (2); der Rest wurde `BL-193` Weg (2).** **(1)** `ledger_pruefen()` P1 stuft eine **nummerierte** Kaskade mit `ralph`-Zeile und ohne `architekt`-Zeile jetzt als **Warnung** ein — benannte Kaskaden bleiben Hinweis, dieselbe Unterscheidung und derselbe Grund wie in `BL-14`. **Gebuendelt, nicht je Kaskade:** Ein gewachsenes Feld-Ledger, in dem der Architekt nie gebucht hat, erzeugt EINE Warnung mit Zahl und namentlich genannten Kaskaden statt N dauerhaft unaufloesbarer — die Falle aus `BL-14` war von Anfang an mitgebaut. Die Wirkung kommt vom Kontostand, der ausschliesslich `[WARNUNG]` zeigt: derselbe Filter auf **beiden** Bahnen, und genau darum entscheidet die Schwere zwischen unsichtbar und sichtbar. **(2)** Der Kostenabschluss der Sitzung haengt jetzt als **letzter, kopierfertiger Schritt** an der Scharfschalt-Sequenz — einer Pflicht-Ausgabe am Ende JEDER Aushaertung. Damit haengt er an einem **Ereignis** statt an einer Erinnerung. Zwei Befehle, weil der Betrag erst gemessen werden muss; die `BL-165`-Regel wird ausdruecklich **nicht** ersetzt (sie sagt das Warum, die Sequenz das Wann). Regressionstest `test_bl197_architekt_fehlt_ist_eine_warnung.py`, **13 Faelle** — darunter die vier Gegenproben, die der Eintrag woertlich verlangt, jede einzeln zurueckgedreht: eine von sieben ergibt GENAU EINE Warnung mit der 7 namentlich · ein vollstaendig gebuchtes Ledger **schweigt** · `post-7` bleibt Hinweis · sechs von sieben ergeben EINE Warnung, nicht sechs. Dazu die Bahn-Gegenprobe an der Quelle (beide `team-status`-Filter). **Gegenprobe gefahren:** gegen den alten Stand fallen 4 von 10 Faellen in Teil (1) und 3 von 3 in Teil (2); die uebrigen sind die Gegenrichtungen und muessen beidseitig gruen bleiben. **Vier bestehende Faelle mitgezogen** (`test_bl13` dreimal, `test_bl46` einmal): Ihre Fixtures trugen eine nummerierte Kaskade ohne Architekt-Zeile und behaupteten `rc == 0` nur nebenbei — sie pruefen P2/P3 und bekommen die Zeile jetzt, damit sie das pruefen, was sie meinen. **Was offen bleibt:** `BL-193` Weg (2), der Lueckenfinder — er kostet eine Formataenderung am Ledger und ist erst jetzt sinnvoll zu entscheiden, weil Teil (1) einen guten Teil seines Nutzens ohne das Format holt |
| BL-196 | **Die Abgleichsablage aus `BL-178` bleibt liegen, und niemand sagt, dass sie weggeworfen werden darf.** Beide Installer rendern für den Block „Bitte von Hand abgleichen" die Kit-Fassung der abweichenden Dateien in ein Wegwerf-Verzeichnis (`$TMPDIR/team-kit-abgleich-*`) und nennen im Hinweis den Vergleichsbefehl darauf. Aufgeräumt wird **nur, wenn nichts abweicht** (`install.ps1`, `$abgleich -eq 0`); weicht etwas ab — und bei `CLAUDE.md` ist das laut demselben Block ausdrücklich der **Normalfall** —, bleibt das Verzeichnis stehen. Das ist so gewollt: Der Anwender soll den genannten Befehl noch ausführen können. Nur endet die Zusage dort. **Kein Satz sagt, dass die Ablage danach entbehrlich ist**, kein Lauf entfernt eine ältere, und der Hinweis nennt sie nicht als temporär — geprüft: In `install.sh` und `install.ps1` kommt keine Formulierung über Aufräumen oder Löschen vor. **Gemessen, nicht vermutet:** Nach einem Arbeitstag mit Selbsttest-Läufen und Update-Proben lagen **elf** solcher Verzeichnisse in `%TEMP%` (36–60 KB je Stück, also kein Platzproblem — ein Ordnungsproblem). **Warum das trotzdem zählt:** Ein Verzeichnis, dessen Lebensdauer niemand benennt, wird entweder nie gelöscht oder im falschen Moment — nämlich bevor der Anwender den Vergleich gefahren hat. Beides ist vermeidbar, und die Bauart ist dieselbe wie bei `BL-44`: ein Hinweis, der eine Handlung ankündigt, ohne ihren Rahmen zu nennen. **Eine zweite Hälfte, und sie gehört zur Gattung von `BL-145`:** `kit-test.sh` räumt seine eigenen Abgleichsablagen nach jedem der beiden Update-Läufe ausdrücklich weg (Zeilen ~538 und ~603, mit einer Schranke gegen einen leeren Pfad); `kit-test.ps1` tut das **nicht**. Der pwsh-Selbsttest hinterlässt damit je Lauf mindestens ein Verzeichnis — bei einem Lauf, der ohnehin eine Stunde dauert und deshalb wiederholt wird, summiert sich das | Kit, 2026-08-26 — beim Aufräumen nach den `BL-145`-Läufen aufgefallen. Nicht aus dem Betrieb, sondern beim Nachsehen, was die Läufe in `%TEMP%` hinterlassen hatten: elf `team-kit-abgleich-*` neben drei `team-kit-test-*`. Die drei Selbsttest-Ordner sind erklärt (sie bleiben bei einem **roten** Lauf absichtlich zur Ansicht liegen, so steht es in der Schlusszeile); die elf anderen sind es nicht | **erledigt 2026-08-28 — Teile (1) und (2), Teil (3) bewusst nicht.** **(1)** Beide Installer sagen jetzt, WAS die Ablage ist (*„eine KOPIE zum Nachlesen im Temp-Bereich, kein Teil deines Projekts"*) und stellen den Loeschbefehl kopierfertig daneben — `rm -rf` bzw. `Remove-Item -Recurse -Force`, je in der Schreibweise IHRER Bahn; ein `rm -rf`, das Windows nicht kennt, waere die Bauart `BL-44` ein zweites Mal. **(2)** `kit-test.ps1` raeumt seine eigenen Ablagen weg wie `kit-test.sh` — mit derselben Schranke gegen einen unerwarteten Pfad UND mit der Gegenrichtung: Wird nichts erkannt, faellt der Schritt rot, statt still nichts zu tun und gruen auszusehen. **(3) NICHT gebaut**, und der Eintrag sagt es selbst (*„erst danach, und nur wenn es sich lohnt"*): Dass ein Update die Ablage des vorigen entfernt, kostet Zustand ueber Laeufe hinweg und loest ein Problem, das (1) und (2) bereits kleinhalten. Regressionstest `test_bl196_abgleichsablage_hat_ein_ende.py`, 12 Faelle auf beiden Bahnen — darunter die Gegenrichtung, dass die Ablage NICHT vorzeitig geloescht wird (sie ist die einzige Stelle, an der die Kit-Fassung sichtbar ist, `BL-4`). Gegenprobe gefahren |
| BL-169 | **`src/` + `tests/` als ausgelieferte Ordner-Defaults machen Reproducer-Tests in jedem Stack mit paketgebundener Testsuche unausführbar — und zwar stumm.** `bootstrap/team.config.sh` belegt `TEAM_PRODUKTIVCODE` mit `src/` und `TEAM_TEST_ORDNER` mit `tests/` vor. Das trägt, solange der Testläufer die Dateien am **Pfad** findet (pytest). Es trägt **nicht**, sobald er sie am **Paket** findet: Dart/Flutter sammelt ausschließlich innerhalb des Pakets und ausschließlich unterhalb von `test/`; liegt das Paket unter `src/`, liegt der vom Kit vorgesehene Testordner **außerhalb** davon. Dieselbe Bauart bei Cargo (`tests/` relativ zu `Cargo.toml`), Go (Paketverzeichnis) und Gradle (`src/test/`). **Die zweite Hälfte ist vom Ordner unabhängig und wiegt schwerer:** Der Läufer nimmt nur Dateien mit einem bestimmten Namensmuster — `_test.dart` bei Dart, `_test.go` bei Go. Die Konvention des Kits lautet `tests/test_hm<nr>_<stichwort>.py` und steht wörtlich in `bootstrap/CLAUDE.md.vorlage` (Fund-Format **und** der Absatz zur Benennung nach der Fund-Nummer), in `bootstrap/beutebuch.md` und in `geteilt/prompts/rolle-harry.md`/`rolle-marv.md`. Buchstabengetreu auf Dart übertragen ergibt das `test_hm36_foo.dart` — einen Namen, den der Läufer ignoriert. **Folge in beiden Hälften identisch:** Franks regelkonform abgelegter Reproducer wird nie ausgeführt, der Smoke-Test bleibt grün, das Beutebuch zeigt einen Fund mit Reproducer, geprüft wird nichts. Das ist derselbe Schaden wie `BL-15` (Backtick-Regel) und `BL-28` (`strict`-Marker), nur eine Ebene tiefer: Dort war der Test da und stumm markiert, hier wird er gar nicht erst gefunden. **Nicht betroffen ist der Extraktor:** `DATEI_RE` in `team/tools/beutebuch.py` akzeptiert jede Endung und hat den umgestellten Dart-Pfad im Lauf korrekt als `test/hm6_stichwort_test.dart` erkannt — der Substanz-Anker trägt, allein die Vorgabewerte und Beispiele tragen nicht | `Feld E`, 2026-08-23, vom Architekten beim Aushärten der **ersten** Kaskade gefunden — durch Lesen der Kopplung zwischen Konfiguration und Testläufer, **bevor** ein Lauf startete. Dasselbe Zeitfenster wie `BL-149`: Sobald ein Projekt seine Ordner einmal richtig gesetzt hat, ist der Default für immer unsichtbar, und ein laufendes Projekt kann den Fehler gar nicht mehr erleben. Getroffen wird ausschließlich der Erstlauf | **erledigt 2026-08-28 — beide Wege, wie der Eintrag sie verlangt (*„Beides zusammen, nicht eines davon"*).** **(1) Der erkannte Stack:** Beide Installer halten die Interview-Antwort `TECH_STACK` gegen den Testordner und melden den Widerspruch — Dart/Flutter, Cargo/Rust, Go und JVM/Gradle, je mit den ueblichen Ordnern UND dem Namensmuster (`<stichwort>_test.dart`, `_test.go`). **GEMELDET, NICHT REPARIERT**, und die Meldung sagt das selbst: Der Stack steht als freie Prosa da, ein Installer, der daraus stillschweigend Ordner umschreibt, raet — und ueberschriebe womoeglich eine bewusste Antwort. Dieselbe Entscheidung wie in `BL-200`. Die Meldung nennt auch die **stumme Folge**, denn daran haengt der Wert des Eintrags: Franks Reproducer wird nie ausgefuehrt, der Smoke-Test bleibt **gruen**, das Beutebuch zeigt einen Fund mit Reproducer. **(2) Der unerkannte Stack:** Die Kopplung steht jetzt im Kommentar am `TEAM_TEST_ORDNER` beider Konfigurationsvorlagen — Pfadsuche gegen Paketsuche, mit denselben vier Gattungen und dem Namensmuster als zweiter, schwererer Haelfte. **End-zu-end gefahren, nicht nur getestet:** frische Installation mit `TEAM_INIT_TECH_STACK="Flutter Dart sqlite"` und den Vorgabewerten — die Meldung erscheint mit `lib/`, `test/` und `<stichwort>_test.dart`. **Und die Gegenrichtung**, ohne die es keine Gegenprobe ist: `"python3 tkinter sqlite"` und `"TypeScript React Vite"` erzeugen **null** Meldungen — ein Waechter, der immer anschlaegt, ist keiner (`BL-14`). Regressionstest `test_bl169_paketgebundener_stack.py`, **11 Faelle**, alle elf fallen gegen den alten Stand. **Was bewusst offen bleibt, und der Eintrag verlangt es ausdruecklich:** die Gegenprobe am **LAEUFER** — eine frische Installation fuer einen paketgebundenen Stack, in der der konfigurierte Smoke-Test die Reproducer-Datei nachweislich AUSFUEHRT. Sie braucht Dart, Cargo oder Go auf dem Wirt; auf dieser Maschine liegt keiner davon. Bis dahin ist die Kopplung **benannt**, nicht **bewiesen** |
| BL-207 | **Die Auflage „Smoke-Test im Vordergrund“ ist nicht erfuellbar, sobald die Suite laenger laeuft als die Vordergrundgrenze des Werkzeugs (120 s) — und die BL-41-Selbstpruefung stellt dann einen ZWEITEN Lauf daneben.** Jede Suite waechst; ab dem Tag, an dem sie die Grenze reisst, laeuft jede bauende Rolle regelmaessig in den vierten Ausgang. **Zweiter, gefaehrlicherer Befund:** Die `BL-41`-Selbstpruefung startet den Verifikationsbefehl bedingungslos ein zweites Mal, ohne zu pruefen, ob bereits ein Lauf laeuft. Zwei gleichzeitige Testlaeufe kollidieren (Datenbankdateien, Ports, App-Nutzerverzeichnisse) — die Selbstpruefung meldet **ROT** fuer einen Baum, der allein gefahren gruen ist, und schickt den Menschen per `BL-61`-Text ausdruecklich auf die falsche Faehrte (Testaufbau). Wer ihr glaubt und neu baut, wirft bezahlte, fertige Arbeit weg | Feld B, 2026-08-28, Closeout einer Kaskade — **gemessen, nicht vermutet**: In EINEM Lauf dreimal getroffen, woertlich im Feld `result` der Logs (Bau-Rolle letzte Stufe, Fixer-Versuche 1 und 2 desselben Fundes), zusammen **4,9480 USD** = 32 % der Rollenkosten des Laufs. Die beiden Fixer-Versuche wurden per Rollback verworfen und als Fehlversuche gezaehlt, obwohl der Fix inhaltlich fertig war; der erfolgreiche dritte Versuch unterscheidet sich sachlich nicht vom ersten. Suite dort 149-220 s, allein gefahren gruen (199 passed) | **erledigt 2026-08-28 — beide vorgeschlagenen Richtungen gebaut.** Meldung liegt: [`2026-08-28-die-suite-ist-laenger-als-die-vordergrundgrenze-der-bauenden.md`](meldungen/2026-08-28-die-suite-ist-laenger-als-die-vordergrundgrenze-der-bauenden.md). **Verhaeltnis zu `BL-201`:** Dieselbe Bauform, aber `BL-201` hat sie zweimal mit einer **schaerferen Auflage** beantwortet — dies ist der Beleg, dass Schaerfe nicht hilft, weil es kein Disziplinproblem ist. Eine Auflage, die die Rolle nicht einhalten KANN, erzeugt genau das Verhalten, das sie verbieten soll. `BL-204`/`BL-205` grenzen an, treffen aber die Bedienbarkeit der Fixphase. **(1) Die Auflage traegt jetzt eine Zahl:** `TEAM_SMOKE_TEST_TIMEOUT` (Default **600 s**) steht in beiden `team.config.*` **und** hat einen Bibliotheks-Default — nach `BL-200` die „gnaedige" Klasse, ein bestehendes Projekt bekommt sie beim Update nicht als Leerwert. Genannt wird sie im **Prompt**: in `SMOKE_ZEILE` (Ralph) und **in `SMOKE_SUFFIX`**, dem einzigen, was Frank ueber den Smoke-Test liest — genau die Luecke, die den haerter betroffenen der beiden Rollen traf. Dazu die Regeldatei-Vorlage und das Regel-Inventar. **(2) Die Selbstpruefung stellt keinen zweiten Lauf mehr daneben:** `team_smoke_parallel_lauf` erkennt einen laufenden Verifikationslauf an der Prozesstabelle (`Win32_Process` bzw. `ps -eo args=`), meldet **UNBEKANNT statt ROT**, laesst den `BL-61`-Text weg und startet den zweiten Lauf gar nicht erst; die gefundene Kommandozeile steht in der Meldung, damit ein Fehlalarm in einem Blick erkennbar ist. Ist die Prozesstabelle nicht auswertbar (die MSYS-`ps` von Git for Windows kennt kein `-o`), bleibt es beim bisherigen Verhalten — **lieber keine Erkennung als eine falsche**; Windows wird ueber die pwsh-Bahn bedient, dort traegt `Win32_Process` die Kommandozeile. Regressionstest `test_bl207_vordergrund_zeitlimit_und_paralleler_lauf.py` mit **beiden** Gegenrichtungen (roter Baum bleibt rot samt `BL-61`, gruener wird weiterhin quittiert). Gegenprobe gefahren: gegen den alten Stand fallen acht Faelle auf beiden Bahnen. **Was BL-201 davon mit abtraegt:** Punkt (b) der Nachtrags-Messung (Frank kennt die Auflage nicht) ist damit geschlossen. Offen bleibt dort, dass `harry`/`marv`/`axel` die Auflage in ihren Briefings weiterhin nicht nennen |
| BL-208 | **Von den drei Zahlen-Gattungen, die das README ueber sich selbst behauptet, prueft `kit-test.ps1` nur zwei — die Dateizahl liest es aus dem Installer-Log und DRUCKT sie bloss.** `BL-198` Teil (3) hat den README-Schritt auf die pwsh-Bahn gebracht (Schritt 5/9) und dort zwei Gattungen geschlossen: Testfaelle und Testdateien. Die dritte, die Zahl der ausgelieferten Dateien, bleibt ungeprueft: `--dateien` kommt in `pwsh/kit-test.ps1` **nullmal** vor, in `bash/kit-test.sh` dreimal; die pwsh-Fassung zieht die Zeile `Fertig — <N> Dateien geschrieben` aus dem Log und gibt sie als Erfolgsmeldung aus (`kit-test.ps1:215-217`), ohne sie gegen das README zu halten. Die bash-Fassung haelt sie inline dagegen und bricht ab (`kit-test.sh:230-240`). **Damit ist `BL-198` genau um die Gattung unvollstaendig, die den Eintrag ausgeloest hat** — eine Zahl, die niemand nachrechnet, veraltet lautlos. **Zweiter Befund, dieselbe Wurzel:** Die Zahl der Testfaelle ist **koerperabhaengig**. In der Kit-Ablage sind es 1054, in einer frischen Installation 1053; die Differenz ist genau ein Fall, `test_kit_pruefer_ueberlebt_eine_cp1252_ausgabe` ist ueber `geteilt/kit-*.py` parametrisiert (zwei Pruefer im Kit, in einer Installation gibt es `geteilt/` nicht und der Rueckfallwert `("(keiner)",)` liefert einen Parameter). Beide Selbsttests messen die INSTALLATION und haben damit recht; das README trug die KIT-Zahl. Nirgends steht, dass die beiden Koerper verschieden zaehlen — wer von Hand nachmisst, misst im Kit und liegt um eins daneben | Kit, 2026-08-28 — beim Nachholen des ausstehenden `bash bash/kit-test.sh` (der Absatz „Faellig auf der bash-Maschine"). **Gemessen, nicht vermutet:** Der Lauf brach zweimal ab, bevor er Stufe 3 erreichte — einmal an der Dateizahl (README 169, Installation **175**; sechs Dateien seit dem letzten Commit dazugekommen, kein Waechter hat angeschlagen), einmal an der Testfallzahl (README 1054, Installation **1053**, an vier Stellen). Beide Zahlen waren am Vortag auf der pwsh-Bahn gruen gemeldet worden | **erledigt 2026-08-28 — beide Teile, am selben Tag wie der Fund.** **(1)** `kit-test.ps1` liest die Dateizahl des Installers jetzt als ZAHL (`$GeschriebenIst`) und reicht sie als `--dateien` an den Pruefer durch — dieselben drei Gattungen wie auf der bash-Bahn, an EINER Stelle statt an zwei. Dazu die Gegenprobe, die den Zusatz erst gueltig macht (verfaelschte Dateizahl muss rot werden), und die Falle, die der Fix selbst aufgestellt haette: Ist die Zahl nicht lesbar, sagt der Schritt das **laut** (`UNGEPRUEFT (BL-208)`), statt weniger zu pruefen und gruen auszusehen. **(2)** Die Schlusszeile des Pruefers nennt jetzt den **Massstab**, nicht nur die Gattungen: *„die Selbsttests messen an einer frischen INSTALLATION, nicht an der Kit-Ablage — die beiden zaehlen verschieden"*. Ein Satz, der diesen Eintrag ueberfluessig gemacht haette. Mit der Gegenrichtung: Bei einem Aufruf OHNE Zahlen erscheint der Satz **nicht** — sonst behauptete er eine Messung, die nicht stattgefunden hat, also `BL-198` eine Zeile tiefer. Regressionstest `test_bl208_dateizahl_auf_beiden_bahnen.py`, **7 Faelle**; gegen den alten Stand fallen **alle sieben**. **Was diese Faelle NICHT leisten und was deshalb offen bleibt:** Sie pruefen den QUELLTEXT beider Selbsttests gegeneinander — die Bauform, mit der `BL-178` seinen Gleichstand haelt. Der end-zu-end-Beleg der pwsh-Bahn braucht PowerShell 7 auf demselben Wirt und steht im Absatz „Faellig auf der bash-Maschine" neben der `BL-178`-Gegenprobe und der Wurzel-Code-Pruefung aus `BL-155` |
| BL-209 | **`kaskade_beginn()` sucht die Plandatei einer Kaskade in einem verdrahteten Ordner `plans/` — obwohl `TEAM_PLAN_ORDNER` im Aufnahme-Interview abgefragt wird.** `geteilt/tools/kosten.py` baut sein Suchmuster aus zwei Literalen: dem Ordner `"plans"` und dem Dateinamen-Praefix `"ralph-kaskade-"`. Der Ordner ist aber konfigurierbar; das Interview fragt ihn ab, beide `team.config.*` fuehren ihn, und ein Projekt darf dort `team-plans/` oder `docs/plaene/` antworten. **In jedem solchen Projekt findet die Suche NIE eine Plandatei.** Und das ist kein Fehler, sondern **Schweigen**: `kaskade_beginn` gibt dann `None` zurueck, und `None` ist an dieser Stelle ein gueltiger Wert — eine benannte Kaskade hat keine nummerierte Plandatei, ein frisches Projekt gar keine. **Zwei Waechter stuetzen sich darauf und hoeren still auf zu arbeiten:** der Zeitraum-Abgleich aus `BL-45` (er faengt einen Lauf, der ZWISCHEN zwei Kaskaden liegt und sonst falsch beschriftet gebucht wird — im Feld 4,2560 USD) und die P1b-Pruefung aus `BL-27` (unarchivierte Logs, die aelter sind als der Kaskadenbeginn — im Feld 33,89 USD). Beide melden dann nichts mehr, und „nichts gemeldet" liest sich wie „nichts gefunden". **Dieselbe Gattung wie `BL-131`:** eine Maschinen- bzw. Projekteigenschaft als Literal im Werkzeug | Kit, 2026-08-28 — beim Bauen von `BL-202` gefunden. Nicht gesucht: Der Eintrag behauptet, keine Mechanik haenge am Dateinamen-Praefix; beim Nachzaehlen der Fundstellen fiel der Ordner daneben mit auf. **Am Verhalten gemessen, nicht vermutet:** vier Kombinationen aus Praefix und Ordner durch `kaskade_beginn` gefahren — gegen den alten Stand liefert genau EINE einen Zeitstempel (`plans/ralph-kaskade-…`), die anderen drei `None` | **erledigt 2026-08-28, zusammen mit `BL-202`.** Neu ist `plan_ordner()` in `kosten.py`: Es liest `TEAM_PLAN_ORDNER` aus der Umgebung und faellt auf `plans` zurueck — dieselbe Bauart wie `erlaubte_domaenen()` zehn Zeilen darueber, und aus demselben Grund. Beide `team.config.*` **exportieren** den Wert jetzt (`export` bzw. `$env:`), genau wie `TEAM_DOMAENEN` daneben; ohne den Export nuetzt das Ableiten nichts. Das Praefix liegt in `PLAN_PRAEFIXE` an EINER Stelle statt als Literal (`BL-154`). **Gegenprobe gefahren** und in `test_bl202_plandatei_traegt_beide_praefixe.py` festgehalten: dieselben vier Kombinationen muessen jetzt ALLE einen Zeitstempel liefern — und die Gegenrichtung, eine benannte Kaskade (`post-20`) muss weiter `None` liefern, sonst datiert der Abgleich auf eine Datei, die die Kaskade gar nicht eroeffnet hat |
| BL-243 | **Es gibt kein lesbares Projektgedaechtnis — die Artefakte sind vollstaendig, und niemand kann sie lesen.** Gemessen im meldenden Feldprojekt nach dreizehn Kaskaden: `beutebuch.md` 3.755 Zeilen mit 67 Funden, `backlog.md` 56 Eintraege als Tabelle mit Zellen ueber 2.000 Zeichen, 12 Abschluss-Protokolle mit zusammen 4.635 Zeilen, 13 Plaene mit 4.449 Zeilen, `CHANGELOG.md` 1.220 Zeilen, 27 Kit-Meldungen — **rund 14.000 Zeilen foermlicher Dokumente**, alles korrekt, alles maschinennah. Und die einfachste Frage, die ein Mensch an ein Projekt stellt (was ist hier passiert, in welcher Reihenfolge, und was haben wir gelernt), ist daraus in vertretbarer Zeit NICHT zu beantworten — auch nicht vom Architekten, der das meiste davon geschrieben hat. Jedes Artefakt ist fuer seinen Zweck richtig gebaut: Das Beutebuch ist eine Zustandsmaschine, der Backlog eine Tabelle fuer `beutebuch.py`/`zitat-lint.py`, das Abschluss-Doc ein Nachweis. **Keines ist eine Erzaehlung, und die Summe erst recht nicht.** Es fehlt keine Datei — es fehlt eine SCHICHT. | Feld B, 2026-09-08, Kit 2.13.1, pwsh/win32, dreizehnte Kaskade. Belegt an drei Kostenstellen: der Wiedereinstieg jeder neuen Architekten-Sitzung (Arbeit des STARKEN Modells, je Sitzung neu bezahlt), die Uebergabe an Menschen (derselbe Sachverhalt musste an einem Tag dreimal neu formuliert werden — fachlich, kurz, fuer Uneingeweihte), und die Wiederholung von Fehlern (Lehren stehen verstreut in Fundbloecken und Backlog-Zellen und sind nur auffindbar, wenn man weiss, dass man sie sucht). Meldung: `plans/meldungen/2026-09-08-es-gibt-kein-lesbares-projektgedaechtnis-die-artefakte-sin.md` | **teilweise (2026-10-03) — der kleine Vorschlag ist gebaut, der große bewusst zurückgestellt.** Jedes Abschluss-Doc beginnt jetzt mit **Für Menschen**: zehn Sätze ohne Fachkürzel (Frage, gebaut, Überraschung, Kosten, offen) — im Architekten-Briefing und in der Vorlage. **Der große Vorschlag** (gesetzte Ausgabe je Kaskade unter `doku/tagebuch/`, Rolle `Raoul`) ist zurückgestellt, Entscheid unter der Freigabe des Owners. Sein Rohmaterial, die Sitzungsprotokolle, liegt seit dem 2026-10-03 im Projekt (`protokolle.py ablegen`, gebaut mit `BL-242`). Zurückgestellt bleibt er aus zwei Gründen: Eine nach außen zeigbare Ausgabe braucht zuerst eine Schwärzungs-Prüfliste, die es noch nicht gibt; und eine siebte Rolle liegt auf einer anderen Achse als die Befugnis am Code — der Einwand des Melders selbst. **Nächster Schritt:** eine Probeausgabe von Hand für eine abgeschlossene Kaskade; an ihr lassen sich Form, Aufwand und Prüfliste messen, bevor eine Rolle gebaut wird. Regressionstest `test_bl219_abnahme_gegenlesen_zielstand.py` |
| BL-247 | **Der Ledger bucht Dollar, gemessen werden Token — die Basis hat ein Verfallsdatum, das Messergebnis nicht.** `kosten.py sitzung-messen` zaehlt je Modell **fuenf** Groessen (`input`, `output`, `cache_read`, `cache_write_5m`, `cache_write_1h`) und druckt sie auch aus; in die Ledger-Zeile geht davon **eine** Zahl — der Dollarbetrag. Token, Modell und Preisstand sind nach der Buchung weg, die Umrechnung ist unumkehrbar. **Im Abo ist der gebuchte Betrag ohnehin schon eine Ableitung** (die Zeilen tragen den Vermerk *Abo-Gegenwert*, es ist niemandem etwas abgerechnet worden): Gebucht wird eine Bewertung von Token zu API-Preisen — die Messgroesse ist also laengst der Token, nur speichert das Format sie nicht. **Was das im Feld gekostet hat:** Der Kit-Basispreis fuer `claude-sonnet-5` stand mit 2.00 statt 3.00 USD/Mio Input — durchgehend 33,3 % zu niedrig (`BL-166`, `BL-211`). Mit Token als Basis waere die Korrektur eine **Neuberechnung** gewesen; mit Dollar als Basis ist jede vorher gebuchte Zeile dauerhaft falsch und **nicht nachrechenbar**. Dasselbe gilt fuer jede kuenftige Preisaenderung, und Preise aendern sich haeufiger als Ledger-Formate. **Zwei weitere Stellen:** Die Zeile nennt das **Modell nicht** — ein Modellwechsel ist im Kit ein Einzeiler (`TEAM_MODEL_LOOP`), danach vergleichen Kaskaden-Vergleiche stillschweigend Ungleiches; und der Abo-Gegenwert ist der einzige Wert, den das Kit ueber Abo-Nutzung ueberhaupt bilden kann, also der preislistenabhaengigste von allen. | Feld B, 2026-09-16, Kit 2.13.1, pwsh/win32, Bestandsprojekt nach der 22. Kaskade, Ledger mit 75 Zeilen ueber acht Wochen, Auth durchgehend Abo. **Entscheid des meldenden Strippenziehers, kein Fund einer Rolle.** Meldung: `plans/meldungen/2026-09-16-der-ledger-bucht-dollar-gemessen-werden-token-die-basis-hat.md` | **teilweise (2026-10-03) — Schritt 1 („schreiben") ist gebaut, Schritt 2 („rechnen") bleibt bewusst offen.** Eine gemessene Buchung legt im optionalen achten Feld der Zeile (`{"v":2,"quellen":[…]}`) je Buchung eine Quelle ab: Token je Modell und Sorte, die benutzten Basispreise, bei Sitzungen Transkript-Kennung und Fenster; `--rollen-abschluss` schreibt die Token aus `modelUsage` der Logs mit (die Cache-Erstellung dort als `cache_write`, weil das Log ihre Laufzeit nicht nennt). Die Dollarspalte bleibt die Summe, die `--budget` zählt. **Die harte Auflage, die Kennung:** Eine Zeile ohne das Feld ist dollargeboren, `zeilen_basis()` unterscheidet token/dollar/gemischt, Bestandszeilen werden nicht nachgerüstet; `--ledger-pruefen` nennt eine Zeile, deren Quellen ihre Dollarspalte nicht mehr ergeben (Handkorrektur). Vorschlag (3) steht jetzt als Regel in `doku/anhang-a.md`. **Offen:** (2) Dollar als Ableitung aus Token und datierter Preisliste — die Meldung selbst verlangt, damit zu warten, bis Schritt 1 im Feld Zeilen erzeugt hat, gegen die Schritt 2 prüfbar ist; (4) eine Pauschale für selbstgehostete Modelle (`TEAM_PREISE` nimmt schon heute einen Satz je Modell an, eine Pauschale ist das nicht); (5) die Auflösung bis zum einzelnen Aufruf — sie liegt im Rohlog-Archiv, nicht im Ledger. Regressionstest `test_bl247_ledger_traegt_die_messung.py` |
| BL-329 | **`kosten.py` beantwortet `--help`, `-h` und `--hilfe` bei keinem seiner 17 Verben mit der Nutzungszeile — `sitzung-messen` endet mit einem Traceback, andere antworten still falsch; und `kit-melden --hilfe` fehlt seit `BL-223`.** Der Architekt wollte vor der Scharfschalt-Sequenz die Schalter von `sitzung-messen` nachlesen: `--help` wurde als Transkriptpfad gelesen (`FileNotFoundError: … '--help'`). `./kit-melden.sh --hilfe` endet mit „the following arguments are required: verb". **Bei der Triage alle 17 Verben mit allen drei Schaltern gefahren:** Keins druckt seine Nutzungszeile. `summe` (`0.0000`), `turns`, `abdeckung`, `fallbacks`, `fehlergrund` und `lesen-verweigert` antworten mit Exit 0 leer oder falsch, `ledger -h` mit `0.0000`; die buchenden Verben enden mit „unbekanntes Argument" und schreiben nichts. `sitzung-messen --projekt . --help` misst sogar voll und druckt eine Buchungszeile, und jede unbekannte Option gilt dort als Pfad. `kit-melden` fehlt in der festen Liste von `test_bl223`, deren Docstring „Gattung" behauptet; `team_hilfe_wenn_gefragt` steht in `bash/lib.sh` bereit und ist unbenutzt. pwsh (`kit-melden.ps1` reicht `$args` durch) nur am Code geprüft | Feld G, 2026-10-12, Kit 2.13.1, linux/bash, erste Kaskade. Meldung: `plans/meldungen/2026-10-12-hilfe-schalter-uneinheitlich-sitzung-messen-help-endet-mit-t.md` | **offen.** Vorschlag der Meldung: ein Riegel wie bei den Entrypoints — unbekannter Schalter → Nutzungszeile, Exit 2. Triage: In `kosten.py` heißt Exit 2 bei `sitzung-messen` „ungeeicht, nicht buchen"; die Hilfe endet dort mit 0, ein Bedienfehler mit 1. Die Hilfe je Verb speist sich aus `VERBEN` (`BL-253`), eine Quelle für alle 17. Owner: woher `kit-melden` seine Hilfe nimmt (Dateikopf wie bei `BL-154` und `BL-223`, oder argparse) und wie weit der Fix reicht (diese beiden Werkzeuge oder alles unter `team/tools/`) |
| BL-330 | **Die Vollautomatik startet, obwohl die Aushärtungs-Sitzung der Kaskade nicht gebucht ist — und vor dem Lauf gibt es keinen Prüfer, der das sehen kann.** Die Scharfschalt-Sequenz begann wie verlangt (`BL-197`, `BL-291`) mit dem Kostenabschluss der Aushärtung; gebucht wurde nichts. Das Ledger trug nach dem Lauf nur die Zeile der Skizzen-Sitzung, der Commit davor trotzdem „Architekten-Sitzung gebucht", weil die Commit-Vorlage der Sequenz das voraussetzte. Die Vollautomatik startete ohne Hinweis; erst `sitzungen-pruefen` im Closeout zeigte die Lücke. **Bei der Triage bestätigt, beide Bahnen:** Beim Start liest die Vollautomatik nur Deckel und Budget-Empfehlung, kein Ledger-Werkzeug. **Zwei Zusätze, beide nachgestellt:** Der Vorschlag der Meldung — beim Start `sitzungen-pruefen` fragen — hätte den eigenen Fall nicht gefunden, solange der Start weniger als 15 Minuten nach der letzten Antwort liegt (`BL-332`). Und steht für Kaskade N schon irgendeine Architekten-Zeile, hier die der Skizze, sind `ledger --anzahl` und P1 aus `BL-197` zufrieden | Feld G, 2026-10-12, Kit 2.13.1, linux/bash, erste Kaskade; in `Feld G` drei Kaskaden hintereinander (`BL-332`, `BL-334`). Meldung: `plans/meldungen/2026-10-12-vollautomatik-startet-trotz-ungebuchter-planungssitzung-der.md` | **offen.** Vorschlag der Meldung: Die Vollautomatik ruft beim Start `sitzungen-pruefen` und meldet ungebuchte Sitzungen — Warnung, kein Abbruch. Triage: Gefragt wird nicht „welche Sitzung ist ungebucht", sondern „trägt eine Architekten-Zeile für Kaskade N die Kennung der jüngsten interaktiven Sitzung" — das ist `sitzungen-pruefen --kaskade N` aus `BL-332`, über die Ledger-Quellen aus `BL-247`. Teil der gemeinsamen Startprüfung mit `BL-333`, `BL-336` und dem Wiederanlauf aus `BL-326`; die Warnung kehrt im Abschlussbericht wieder. Owner: Warnung (Empfehlung der Triage: Die Buchung lässt sich über den Transkriptpfad nachholen) oder Abbruch |
| BL-332 | **`sitzungen-pruefen` hält die jüngste ungebuchte Sitzung 15 Minuten lang für „diese Sitzung" — auch wenn der Aufruf aus einem anderen Terminal kommt, und genau dann läuft die Scharfschalt-Sequenz.** Nach `BL-330` sicherte der Architekt den Plan-Commit mit `sitzungen-pruefen && git commit …`. Der Stakeholder fuhr die Sequenz kurz nach der letzten Antwort der Planungssitzung in einem eigenen Terminal; die Buchung kam nicht im Ledger an, `sitzungen-pruefen` meldete „laeuft noch (vermutlich diese Sitzung)" mit Exit 0, der Commit lief durch, und die Vollautomatik startete ohne Architekten-Zeile. Erst `--ledger-pruefen` nach dem Lauf zeigte es. **Bei der Triage bestätigt** (geteiltes Werkzeug, beide Bahnen): „Diese Sitzung" bestimmt allein das Alter des Transkripts (`LAEUFT_MINUTEN = 15`, `BL-279`); Umgebung und Sitzungskennung liest `kosten.py` nicht. Nachgestellt: letzte Antwort vor fünf Minuten → Exit 0, auch mit der Kennung einer fremden Sitzung in der Umgebung; vor 16 Minuten → „NICHT gebucht", Exit 3. Die CLI setzt in ihren Kindprozessen `CLAUDECODE=1` und `CLAUDE_CODE_SESSION_ID`, und die Kennung ist der Dateiname des Transkripts (nachgesehen an CLI 2.1.296 über die IDE; CLI-Einstieg, Windows und `--resume` ungeprüft). Eine Vollautomatik aus einem eigenen Terminal hat keine Kennung — ihr steht die Ausnahme nie zu | Feld G, 2026-10-13, Kit 2.13.1, linux/bash, zweite Kaskade; Folgefund zu `BL-330`. Meldung: `plans/meldungen/2026-10-13-sitzungen-pruefen-nimmt-eine-ungebuchte-sitzung-15-minuten-l.md` | **offen.** Zwei Vorschläge der Meldung: `sitzungen-pruefen --kaskade N` ohne die Ausnahme, oder die Ausnahme nur, wenn der Aufruf erkennbar aus der Sitzung kommt. Triage: beides. Die Ausnahme gilt nur, wenn `CLAUDE_CODE_SESSION_ID` die Sitzung trifft. `--kaskade N` verlangt eine Architekten-Zeile für Kaskade N mit der Kennung der jüngsten interaktiven Sitzung; „zuwachs" zählt dort als gebucht, „unter Kaskade N-1 gebucht" wird benannt. Owner: die Rückfallregel ohne Kennung (Empfehlung der Triage: die alte Heuristik nur bei `CLAUDECODE=1`) und ob `--kaskade N` in die Scharfschalt-Sequenz kommt |
| BL-333 | **Ralph baut acht Stufen auf einem Plan, der nicht im Git liegt — die Ralph-Phase warnt als einzige nicht vor einem schmutzigen Baum, und ein `git stash` nimmt fremde Arbeit mit.** Die Vollautomatik startete, während die Ausgabe der Aushärtung uncommittet lag: der aktive Plan untracked, Roadmap, Backlog und Beutebuch geändert, im Beutebuch ein Fund des Architekten. Ralphs Phase lief acht Stufen und 23 Minuten ohne Warnung; die erste kam beim Start von Harry. Ralph nahm die fremden Backlog-Änderungen in seinen Commit und benutzte für eine Klon-Probe `git stash` — der untracked Plan lag dabei kurz nicht im Baum. Harrys Commit „2 neue Funde" trug drei Fundblöcke; der dritte war der uncommittete Fund des Architekten. Zuordnen ließ sich alles nur, weil Ralph es quittiert hat. **Bei der Triage bestätigt, beide Bahnen:** `ralph.*` zieht nur `team_stufen_schnappschuss` („ohne Warnung", `BL-274`); die Warnung aus `team_guard_begin` haben Red Team, Frank und Axel. Weder `ralph.*` noch Voll- oder Halbautomatik fragen Git nach dem Plan. Abweichung: Das Verbot von `git add -A` steht in Regel 4 des Ralph-Prompts im Entrypoint, nicht in `rolle-ralph.md`; `git stash` kommt im Kit nirgends vor. **Und schwerer als gemeldet** (auf Funktionsebene nachgestellt): Der Beginn einer Kaskade ist der Add-Commit ihres Plans (`kaskade_beginn`). Solange der Plan ungetrackt ist, fehlt die Berichtszeile „Kaskade N bisher" still; wird er erst im Closeout committet, gilt jedes Log des Laufs als älter als die Kaskade, und `--rollen-abschluss N` bucht ohne `--auch-aeltere` nichts. Harrys Commit ist Fall (a) aus `BL-271`, per Pfadfilter nicht lösbar | Feld G, 2026-10-16, Kit 2.13.1, linux/bash, dritte Kaskade, ein Mensch und die Rollen in einem Arbeitsbaum. Meldung: `plans/meldungen/2026-10-16-ralph-baut-acht-stufen-auf-einem-plan-der-nicht-committet-is.md` | **offen.** Drei Vorschläge der Meldung: (1) Planprüfung beim Start — Plan untracked oder vom HEAD abweichend → Abbruch mit Pfad und Commit-Befehl, in der Vollautomatik und in `ralph.*`; (2) die Warnung aus `team_guard_begin` einmal beim Start der Ralph-Phase; (3) „kein `git stash`" für Ralph. Triage: (1) als Abbruch, weil der verschobene Kaskadenbeginn nach dem Lauf nicht mehr heilbar ist; (2) den Warnblock als eigenen Helfer herauslösen; (3) in Regel 4 des Prompts statt ins Briefing (45 von 45 Zeilen), dazu als Mechanik `git stash list` vor und nach dem Aufruf zählen. Teil der gemeinsamen Startprüfung (`BL-330`). Owner: ob außer dem Plan auch andere schmutzige Rollen-Zonen abbrechen, und Stash über Prompt oder Mechanik |
| BL-334 | **`sitzung-messen` endet mit Exit 2, weil `<synthetic>`-Einträge mit null Token als unbekanntes Modell zählen — und das Architekten-Briefing liest Exit 2 als „nicht buchen".** Im Closeout war eine Aushärtungs-Sitzung nachzubuchen. `sitzung-messen` warnte „Modell '<synthetic>' steht nicht in der Preistabelle", druckte `GESAMT` und eine Buchungszeile und endete mit Exit 2. Beide `<synthetic>`-Einträge trugen 0 in jedem Token-Feld; die CLI schreibt den Namen für Nachrichten, die sie ohne API-Aufruf selbst erzeugt, etwa Abbruch- und Fehlermeldungen. Das Briefing sagt: Exit 2 heißt ungeeicht, „ich buche sie nicht". Der Architekt zählte nach und buchte trotzdem. **Bei der Triage nachgestellt:** `if not usage: continue` lässt einen Satz mit lauter Nullen durch, weil das Dict nicht leer ist; `sitzung_kosten` führt jedes Modell ohne Preis als unbekannt, gleich wie viele Token; am Ende steht `return 2 if (schief or unbekannt)`. **Drei Zusätze:** Die Buchungszeile kommt auch bei Exit 2 — Ausgabe und Exit-Code widersprechen sich, auch im echten Ungeeicht-Fall. Ein `<synthetic>` nach der Buchung erzeugt einen Phantom-Zuwachs („ZUWACHS seither: 0.0000 USD in 2 Antwort(en)", `sitzungen-pruefen` Exit 3). Und `akteur-abschluss --transkript` schreibt `ohne_preis: ["<synthetic>"]` in die Ledger-Meta. `sitzungen-pruefen` nennt dieselben Einträge nur als Hinweis — zwei Verben, zwei Strengen. Die Zuordnung „Exit 2 = nicht buchen" steht auch in `doku/faq.md` | Feld G, 2026-10-16, Kit 2.13.1, linux/bash, dritte Kaskade. In `Feld G` war die Aushärtung drei Kaskaden hintereinander beim Start nicht gebucht; ob Exit 2 dabei mitspielte, ist nicht belegt. Meldung: `plans/meldungen/2026-10-16-sitzung-messen-endet-mit-exit-2-wegen-synthetic-mit-0-token.md` | **offen.** Zwei Vorschläge der Meldung: Einträge ohne Token nicht als unbekanntes Modell zählen oder `<synthetic>` mit Preis 0 in die Tabelle aufnehmen; Exit 2 nur, wenn wirklich Token ohne Preis bleiben, und dann deren Zahl nennen. Triage: der erste Weg als Token-Regel — Sätze, deren fünf Zähler alle 0 sind, vor der Dedup über die Nachrichten-ID überspringen —, nicht als Namensliste und nicht über die Preistabelle, die auch `modelle` als Versionsquelle dient. `test_bl141` hält ein unbekanntes Modell mit 9 Mio Token fest; das bleibt. Owner: was bei einem echten unbekannten Modell mit Token gilt (Verbot wie heute oder buchbar als Untergrenze) und ob die Buchungszeile bei Exit 2 entfällt |
| BL-335 | **Franks Briefing verlangt die Gegenprobe zentraler Werte nur, wenn ein Fix einen Wert ändert, und dann eine grüne Suite — beides widerspricht der Regel, die rote Stellen zählt (`BL-167`).** In zwei Kaskaden in Folge fixte Frank einen Fund aus Fremddaten mit einer neuen Längengrenze, deren Verbraucher im selben Fix entstand, beide Male ohne Gegenprobe. Franks Quittung: „nicht nötig, weil `_MAX_ZIFFERN` eine neue Konstante ist, die vorher nichts las". Im Closeout nachgeholt: Grenze auf 10000 → 2 Tests rot, auf 5 → 11; die Textsuche fand den Namen in keinem Test. Beide Fixe waren richtig; es fehlte der Nachweis, welche Tests an der Grenze hängen. **Bei der Triage bestätigt:** `rolle-frank.md` sagt „Wenn mein Fix einen zentralen Wert **ändert** … Suite beide Male grün"; die Regel in `CLAUDE.md` zählt die roten Stellen. Frank trug den Absatz aus `BL-167` schon einmal: `c3732fa` fügte ihn ein, `8c79d5a` strich ihn zwanzig Minuten später wegen des 45-Zeilen-Limits — das Archiv behauptet bei `BL-167` trotzdem, Ralph und Frank zögen nach. Ralph trägt dieselbe Formulierung („ändere", „Suite beide Male grün") und widerspricht damit seinem eigenen Absatz zum Zählen roter Stellen. Franks Absatz steht nicht im Regel-Inventar; nichts schützte ihn vor dem stillen Wegfall | Feld G, 2026-10-17, Kit 2.13.1, linux/bash, vierte Kaskade (Fälle aus der dritten und vierten). Meldung: `plans/meldungen/2026-10-17-franks-briefing-verlangt-die-gegenprobe-zentraler-werte-nur.md` | **offen.** Vorschlag der Meldung: der Absatz neu — „führt mein Fix einen zentralen Wert ein oder ändert er einen", je Verstellung die roten Tests zählen und in den Commit-Text schreiben; nennt das Verstellen nicht mehr rote Stellen als die Textsuche, fehlt ein Test, der die Grenze festhält. Triage: zeilenneutral machbar; eine Fassung mit sechs statt sieben Zeilen gibt in `rolle-frank.md` eine Zeile für `BL-327` frei. `test_bl49` verlangt in Frank und Ralph die Marken „Suite" und „sieben", die der Wortlaut der Meldung nicht trägt. Dazu eine NORM-Zeile im Regel-Inventar. Owner: was bei „nicht mehr rot als `grep`" folgt (Frank schreibt den fehlenden Test, wie die Meldung, oder nennt es im Fix-Bericht, wie `c3732fa`) und ob Ralph mitgezogen wird |
| BL-336 | **Die Vollautomatik startet ohne Red-Team-Fokus und sagt es erst im Abschlussbericht — beide Sweeps liefen mit dem Grundauftrag an den zwölf Nähten vorbei, die der Plan benannt hatte.** Die Startsequenz des Architekten war eine stille `&&`-Kette: sauberer Baum, State, Architekten-Zeile im Ledger, dann `TEAM_REDTEAM_FOCUS='…' ./vollautomatik.sh`. Sie hielt an der fehlenden Buchung an, ohne etwas auszugeben. Gelaufen ist die Vollautomatik trotzdem, 22 Sekunden nach dem Ledger-Commit, ohne Fokus in der Umgebung — wie sie gestartet wurde, steht nirgends. Sechs Stufen bauten in 22 Minuten; erst beim Start der Sweeps meldete jede Rolle „Fokus … VERFALLEN (Kit-BL-31) … Grundauftrag". Die Nähte prüfte der Architekt im Closeout nach, mit dem starken Modell statt mit zwei Sweeps auf dem günstigen. **Bei der Triage bestätigt, beide Bahnen:** Vor Phase 1 liest die Vollautomatik nur `TEAM_REDTEAM_FOCUS_2`. Im Auslöser eine Teil-Dublette zu `BL-250` (leerer Fokus beim Start; gebaut wurden damals Bericht und Einzeiler) — neu ist der Beleg, dass der Einzeiler nicht trägt, wenn die Kette davor still anhält. `BL-31` hat ausdrücklich entschieden: „Kein Abbruch: Ein Werkzeug, das den Lauf verweigert, wird umgangen"; `BL-284` warnt bewusst nur. Zusätzlich aus dem Code, nicht gefahren: Wird nach einer Pause in Phase 2 ohne Variable fortgesetzt, übernimmt Harry seinen alten Fokus, und Marv bekommt keinen. Drift: Regel 4 in `CLAUDE.md` nennt die Sequenz ohne den Kostenabschluss, den das Architekten-Briefing seit `BL-291` an erster Stelle hat | Feld G, 2026-10-17, Kit 2.13.1, linux/bash, vierte Kaskade. Meldung: `plans/meldungen/2026-10-17-vollautomatik-startet-ohne-red-team-fokus-und-sagt-es-erst-i.md` | **offen.** Zwei Vorschläge der Meldung: (1) Fokusprüfung beim Start — stehen Red-Team-Phasen an und ist der Fokus leer, bricht die Vollautomatik vor dem Bau ab; ausdrücklich ohne Fokus fährt sie nur mit einem Schalter (`TEAM_REDTEAM_OHNE_FOKUS=1`), und ein wortgleicher Fokus (`BL-284`) bekommt dieselbe Prüfung; (2) in denselben Startschritt gehört die Buchungsprüfung aus `BL-330`. Triage: Teil der gemeinsamen Startprüfung. Der Abbruch beim Start kostet nichts, und der Mensch ist da — die Begründung von `BL-31` gilt für den Sweep, nicht für diesen Zeitpunkt. Owner: Abbruch statt Warnung beim Start (das kehrt `BL-31` und `BL-284` dafür um), der Name des Schalters, und ob der Lauf-Fokus für die Wiederaufnahme festgehalten wird |
| BL-337 | **Eine Hintergrundmeldung nach dem Stufenende ersetzt das Ergebnis im Rollenlog — die CLI hält die Sitzung bis zu zehn Minuten offen, und das Kit sieht nur ihre letzte Antwort.** Ralph rief ein Skript per Heredoc auf, das nicht zurückkam; das Bash-Werkzeug der CLI schob es nach 120 s in den Hintergrund. Ralph baute die Stufe fertig, committete und quittierte. Die Sitzung wartete trotzdem auf den Task, bis die CLI ihn nach zehn Minuten stoppte, und beantwortete dessen Meldung als zweite Antwort. `claude -p --output-format json` gibt nur das letzte Ergebnisobjekt aus (`"result_index": 1`, `"num_turns": 1`). Das Promise stand nur im Log, weil die Rolle es in der zweiten Antwort wiederholte; der Bericht führte die Stufe mit „1 Turns". **Bei der Triage bestätigt** (CLI 2.1.296, aus `claude --help` und den Schema-Texten der CLI, ohne Prompt): Im json-Modus kommt genau ein Objekt, das letzte; alle Ergebnisse liefern nur `--verbose` oder `stream-json --verbose`. `total_cost_usd` und `modelUsage` laufen kumulativ, `num_turns` zählt je Turn. Im Print-Modus wartet die CLI nach dem letzten Turn auf Hintergrund-Shells, bis zu zehn Minuten. Alle Prüfungen des Kits lesen nur dieses eine Objekt: `team_promise_in`, `team_result_meldet_erfolg`, `team_result_is_error` (daran hängt der API-Fallback) und das Turn-Profil. **Abweichungen:** Kosten und Token kommen aus den kumulativen Feldern und stimmen; falsch ist nur `num_turns`. „Sonst Exit 43" ist für Ralph zu pessimistisch — die Selbstprüfung (`BL-41`) hätte quittiert, mit einem zweiten Smoke-Lauf und der falschen Diagnose „vierter Ausgang"; Frank und Axel trifft es härter. **Neu aus dem Code:** Ist die späte Antwort ein Fehler (`is_error`, etwa ein 429), gilt der ganze Aufruf als gescheitert, und im Abo baut der API-Fallback die fertige Stufe ein zweites Mal. Die Prämisse von `BL-41` — headless gibt es keinen zweiten Gesprächszug — ist für die heutige CLI falsch; sie steht noch im Smoke-Text beider Bibliotheken, in vier Briefings und im README | Feld G, 2026-10-17, Kit 2.13.1, linux/bash, fünfte Kaskade mit zehn Stufen, Vollautomatik. Meldung: `plans/meldungen/2026-10-17-eine-hintergrundmeldung-nach-dem-stufenende-ersetzt-das-erge.md` | **offen.** Drei Vorschläge der Meldung: (1) alle Ergebnisobjekte sichern (`stream-json`) und das Promise in jedem suchen; (2) Turns, Dauer und Token über alle Ergebnisse summieren und eine späte Antwort im Bericht ausweisen; (3) ein Satz im Briefing der bauenden Rolle: einen in den Hintergrund geschobenen Befehl vor dem Quittieren ausdrücklich stoppen. Triage: (1) und (2) über einen Normalisierer in `kosten.py`, der die kumulativen Felder aus dem letzten Ergebnis nimmt und nur `num_turns` summiert — Kosten zu summieren verdoppelte den Stufendeckel. (3) träfe einen Absatz, der in vier Briefings byte-gleich stehen muss, und schriebe die falsche Prämisse fort. Baut auf `BL-326` auf, dieselben Aufrufzeilen. Owner: Format, Urteilsregel (zählt ein Promise in irgendeinem Ergebnis, löst eine späte Fehlerantwort noch den Fallback aus), Ablage des Rohstroms, Korrektur der Prämisse |
| BL-339 | **`kosten.py` rechnet `claude-sonnet-5-5` mit dem Cache-Read-Faktor 0,10 statt 0,05 — jede Messung eines Sonnet-5.5-Transkripts liegt 18 bis 34 % zu hoch, und die Selbsteichung erklärt die Tabelle für geeicht.** `sitzung-messen` über die 14 Rollen-Läufe einer Kaskade, alle auf `claude-sonnet-5-5`, ergab durchweg 18 bis 34 % mehr als `total_cost_usd` im Log desselben Laufs, bei gleichen Token. Der Unterschied ist genau der Cache-Read-Anteil: Mit 0,05 reproduziert die Tabelle `costUSD` aller 14 auf sechs Nachkommastellen, über alle 75 archivierten Sonnet-5.5-Logs des Projekts 75 von 75. Die Selbsteichung meldete dabei „12 von 48 … reproduzieren sich nicht — die Preistabelle ist dafuer NICHT die Ursache". **Bei der Triage bestätigt** und an den Feldlogs nachgerechnet: `CACHE_READ_FAKTOR_JE_MODELL` kennt Opus 5.5 (0,05) und Fable/Mythos 5.1 (0,025); Sonnet 5.5 erbt 0,10. **Warum die Eichung blind ist**, nachgestellt: (1) 38 der 86 Logs tragen einen Anteil `claude-haiku-5-5`, das in der Preistabelle fehlt, und fallen still heraus; (2) das [5m,1h]-Intervall aus `BL-218` gleicht den Faktorfehler aus, solange Cache-Read höchstens etwa das 15-Fache von Cache-Write ist — dabei tragen die Logs die Aufteilung selbst (`usage.cache_creation`, in allen 86 nur 1h); (3) die Diagnose prüft nur den Basispreis. Gattungsprobe: zehn Opus-5-Logs, abgerechnet mit halbem Cache-Read-Satz, ergeben heute „✓ Preistabelle geeicht" mit Exit 0. **Strukturell:** Der längste Präfix lässt künftige Unterversionen still erben (`claude-opus-5-6` bekäme 0,10) — die Fehlerklasse von `BL-302`, nur verschoben. `BL-302` nahm an, bei Sonnet stimme der Satz zufällig; `test_bl302` schreibt 0,20 USD je Mio Cache-Read für Sonnet 5.5 fest | Feld G, 2026-10-17, Kit 2.13.1, linux/bash, siebte Kaskade, alle Loop-Rollen auf `claude-sonnet-5-5`. Nicht betroffen sind Buchungen aus Rollen-Logs (`--rollen-abschluss` übernimmt `total_cost_usd`); betroffen ist jede Buchung über `sitzung-messen`, also jede interaktive Abo-Sitzung auf Sonnet 5.5. Meldung: `plans/meldungen/2026-10-17-kosten-py-rechnet-claude-sonnet-5-5-mit-cache-read-faktor-0.md` | **offen.** Vorschlag der Meldung: `"claude-sonnet-5-5": 0.05`, ein Test, der einen echten Sonnet-5.5-Log nachrechnet, und eine Selbsteichung, die scheitert, wenn kein Lauf eines Modells aufgeht. Triage: die Tabelle, dazu `claude-haiku-5-5` (ein Feldlog impliziert 0,10 USD je Mio Input; Satz und Regel für lange Prompts vor dem Eintrag an der Preisliste prüfen); und die Eichung härten — Cache-Write-Laufzeit aus `usage.cache_creation` statt Intervall, je Modell urteilen, übersprungene Logs nennen. Der Vorschlag der Meldung greift allein nicht: Heute weichen nur 12 von 37 Sonnet-5.5-Läufen ab. Owner: Präfixregel (eine unbekannte Unterversion laut statt still), Tiefe der Eichhärtung, ob `TEAM_PREISE` auch Faktoren übersteuern darf; alte Buchungen werden wie bei `BL-302` nicht nachgerechnet |
| BL-340 | **Das Kit hat keinen Platz für eine Abnahme, die Laufzeitverhalten belegt — heute wartet dafür der Architekt mit dem teuersten Modell; im Feld lief sie zweieinhalb Stunden als Skript, und die Auswertung kostete 1,30 USD.** Bis Kaskade 14 fuhr der Architekt jede Abnahme selbst: Gegenlesung der Fixe mit Mutationsreihen (je rund 20 Minuten) und Serverläufe von 40 bis 150 Minuten; seine Sitzung wartete mit. In Kaskade 14 kostete er rund 390 USD Abo-Gegenwert, Bau und Prüfrollen zusammen rund 41 USD. In Kaskade 15 baute das Feld einen eigenen Loop außerhalb von `team/`: Ein Skript fährt Gegenlesung und Serverläufe ohne Modell und schreibt Auszüge, einen Lagebericht und Fragen mit Erwartung und Beleg; danach urteilt eine günstige Rolle nur lesend. Die erste Abnahme lief 2 h 30 ohne Handgriff; die Rolle brauchte 5 Minuten und 1,30 USD und beantwortete alle 15 Fragen mit Beleg. Verworfen wurde das Ergebnis trotzdem: Der letzte Docs-Commit der Fix-Phase trug ein BEL (`BL-327`, `BL-341`), die Suite am HEAD war rot, keine Mutation lief, und die Schlussprüfung urteilte über das ganze Repo statt über die Dateien der Rolle. **Bei der Triage eingeordnet, keine Dublette:** `BL-219` hat keine Laufzeit-Abnahme gebaut (Plankopf, Abnahme-Abschnitt im Abschluss-Doc, eine Frage an den Stakeholder, ausdrücklich ohne neue Rolle); `BL-300` prüft nur, ob das Ziel den gebauten Stand trägt; `BL-325` legt solche Proben beim Architekten fest. Von den sechs Vorschlägen ist (2) „Schlussprüfungen urteilen nur über das Geschriebene" im Kit schon Prinzip (`BL-205`, `BL-256`) und wird Auflage an den Bau von `BL-327`. (3) „Suite am HEAD grün als Vorbedingung" und (4) „Rot nur von neuen Testdateien verlangen" sind kleine Sätze im Gegenlesen-Block des Architekten — (4) aber nicht wörtlich, sonst fielen die Reproducer in Bestandsdateien heraus (`BL-216`). (5), ein Vertrag über exportierte Funktionen: pwsh exportiert heute alles, bash hat keine Modulgrenze. (6) ist Feldsache | Feld F, 2026-10-16, Kit 2.13.1, win32/pwsh, fünfzehn Kaskaden; Art: Idee. Meldung: `plans/meldungen/2026-10-16-abnahme-loop-eine-rolle-wertet-gegenlesung-und-serverlaeufe.md` | **offen — zum Teil eine Entscheidung des Owners.** (A) Ohne Entscheidung baubar: (3) und (4) als Sätze im Gegenlesen-Block — die Gegenprobe gilt dem Reproducer-Fall und neuen Fällen, ein angepasster Bestandstest darf begründet grün sein, und vor der Mutationsprobe muss die Suite am HEAD grün sein. (B) Der Loop selbst ist eine neue Phase oder Rolle und damit eine Kaskade, keine Sitzungsaufgabe; vorher eine Skizze in `roadmap-skizzen.md`. Eine kleinere erste Stufe, ebenfalls Owner: ein Konfigurationsplatz nach dem Muster von `TEAM_ZIELSTAND_PRUEFUNG`, den die Vollautomatik am Ende ohne Modell fährt. Mit (B) entfällt (5) |
| BL-341 | **Nach Franks letztem Commit misst niemand mehr — ohne zweistufigen Smoke-Test meldet die Vollautomatik „beendet" auf einem roten HEAD.** In einer Fix-Phase mit drei Funden schrieb Frank zweimal ein BEL ins CHANGELOG: Im Eintrag stand `.\abnahme.cmd`, und aus `\a` wurde auf dem Weg über einen Python-String das Steuerzeichen (`BL-327`). Das erste fand er beim nächsten Fund selbst; das zweite kam mit dem letzten Docs-Commit, nach seinem letzten Suitenlauf. `frank.ps1` meldete „Dreisatz verifiziert", die Fix-Phase „nichts mehr zu tun", die Vollautomatik „beendet" — der HEAD war rot. Bemerkt hat es erst die Abnahme 4 s später, deren Ergebnis nach 2,5 Stunden verworfen wurde (`BL-340`). **Bei der Triage bestätigt**, auf der bash-Bahn mit Stub-Rollen nachgestellt: Der Frank-Stub committet `fix(uat)` und `docs:`, die Suite ist rot; ohne `TEAM_SMOKE_TEST_SCHNELL` endet der Lauf mit Exit 0 und „Vollautomatik beendet.", mit dem Schalter mit „Volle Suite ROT am Ende der Fix-Phase" und Exit 44. Abweichung: Den Folge-Commit erlaubt der Prompt im Entrypoint (`frank.*`, Schritt 3), nicht `rolle-frank.md` — jede Doku-Änderung liegt dort nach dem letzten Smoke, auch ohne Folge-Commit. Herkunft der Lücke: `BL-256` entschied „Der Loop misst den Suitenstand nicht selbst nach — das wäre die Doppelmessung", und `BL-232` baute die Suite am Phasenende nur für den zweistufigen Betrieb. Die Fixphase hat dieselbe Lücke. `BL-327`, wie übergeben, fängt hier nichts: Seine Prüfung hängt an `team_guard_verify`, und das rufen nur Red Team und Axel | Feld F, 2026-10-16, Kit 2.13.1, win32/pwsh, fünfzehn Kaskaden; Feldbeleg zu `BL-327`. Meldung: `plans/meldungen/2026-10-16-nach-franks-docs-commit-laeuft-kein-test-mehr-die-vollautoma.md` | **offen.** Zwei Vorschläge der Meldung: (1) die Vollautomatik fährt den Smoke-Test am Ende der Fix-Phase immer, und rot setzt das Gate; (2) `frank.*` fährt ihn nach dem letzten Commit eines Fixes, und rot zählt als Fehlversuch. Triage: (1), eng geschnitten — nur wenn `TEAM_SMOKE_TEST` gesetzt ist und sich der HEAD in der Fix-Phase bewegt hat. Das kostet einen Suitenlauf je Lauf mit Fix und keine Modellkosten; rot setzt das Gate und endet mit Exit 44, die vorhandene Mechanik. (2) wäre überwiegend eine Doppelmessung und verwürfe per Rollback einen bezahlten, reparierbaren Fix (gegen `BL-214`, `BL-228`). Dazu billig: die Prüfung aus `BL-327` auch aus `frank.*` und `ralph.*` rufen. Owner: Das kippt den Satz aus `BL-256` zum Teil; und ob auch das Ende der Bauphase gemessen wird |
| BL-344 | **Nach einer Handauflösung rückt die Basis der CLAUDE.md nie vor — jedes weitere Update legt dieselben Konflikte wieder vor, und schon eine einzige bewusst anders formulierte Stelle hält danach jede neue Kit-Regel auf.** Das erste Update mit `BL-311` schätzte die Basis aus der Kit-Geschichte und legte einen Vorschlag mit neun Konfliktstellen vor; der Mensch löste sie von Hand auf und übernahm, wie der Installer es sagt („Ansehen, Konflikte aufloesen, dann uebernehmen"). Beim nächsten Update brachte die Vorlage zwei neue Absätze (`BL-315`, `BL-316`), gemeldet wurden **elf** Konfliktstellen, und die Datei blieb unangetastet. Gegen die richtige Basis — die gerenderte Kit-Fassung des ersten Updates — ging ein Absatz sauber hinein, an einer Stelle blieb ein echter Konflikt; die übrigen zehn waren die Handentscheidungen vom ersten Mal. **Bei der Triage bestätigt:** `kit_basis.py`, `claude()` setzt die Basis nur auf den konfliktfreien Wegen neu. Auf dem Konfliktweg (Exit 10) bleibt sie stehen — bei geschätzter Basis wird die Schätzung als Basis festgeschrieben —, und danach setzt sie nichts mehr. Der Docstring sagt, die Basis rücke vor, „wenn das Projekt die Kit-Fassung aufgenommen hat"; erkennen kann das nur ein konfliktfreier Abgleich, und eine bewusst andere Stelle ist nie konfliktfrei. **Synthetisch nachgestellt** am Kit-Werkzeug (Basis B0; das Kit ändert Regel 2, das Projekt formuliert sie eigen; aufgelöst zugunsten des Projekts; das nächste Kit bringt nur eine neue Regel 4): Exit 10, eine Konfliktstelle — die alte Entscheidung —, Regel 4 steht nur im Vorschlag, die CLAUDE.md bleibt unverändert. Weil bei einem Konflikt die ganze Datei stehen bleibt, ist das kein Rauschen in einer Liste, sondern Stillstand: Ab der ersten bewussten Abweichung trägt das Update nie wieder eine Regel selbst ein. `test_bl311_update_traegt_nach.py` deckt „aufgelöst, dann nächstes Update" nicht | Feld B, 2026-10-26, Kit 2.13.1, win32/pwsh, Bestand, CLAUDE.md mit gut tausend Zeilen; zweites Update seit `BL-311`, gefunden beim Update auf `84a7e81`. Meldung: `plans/meldungen/2026-10-26-nach-einer-handaufloesung-rueckt-die-claude-md-basis-nie-vor.md` | **offen.** Vorschläge der Meldung: (1) Bei Exit 10 legt `claude()` die gerenderte Kit-Fassung als ausstehende Basis neben die Basis; das nächste Update übernimmt sie, wenn die CLAUDE.md seit dem Vorschlag geändert ist und keine Konfliktmarken trägt. (2) Einfacher, auf Vertrauen gebaut: Der Installer nennt `kit_basis.py schreiben --claude <gerenderte Fassung>` als zweiten Schritt neben dem Kopierbefehl. Triage: (1), mit einem dritten Kriterium — sonst gälte eine aus anderem Grund bearbeitete CLAUDE.md als Übernahme, und die neuen Regeln fielen beim nächsten Abgleich als „bewusst entfernt" still heraus, genau was der Docstring verhindern will. Das dritte Kriterium: Der Dreiwege-Abgleich aus jetziger CLAUDE.md, alter Basis und ausstehender Fassung, Konflikte zugunsten des Projekts aufgelöst (`git merge-file --ours`), ergibt die CLAUDE.md unverändert — dann ist jede Änderung der ausstehenden Fassung übernommen oder bewusst anders. (2) zusätzlich als Hinweis, für den Weg von Hand. Owner: welche Variante |
| BL-345 | **`smoke_warten.py start` scheitert unter Windows an einem relativen Interpreterpfad mit Schrägstrichen — `cmd.exe` liest den Pfad als Schalter, und `warten` meldet ROT, ohne dass ein Test gelaufen ist.** Den Umstieg auf den Zwei-Schritt-Weg (`BL-273`) gab das Feld erst nach einem Probelauf frei, mit genau dem Befehl, den der Nachsatz jeder Rolle vorgibt: `start --befehl ".venv/Scripts/python.exe -m pytest --version"`. `warten` endete mit „Fertig: Exit 1 (ROT)", im Log `'.venv' is not recognized as an internal or external command`. In Anführungszeichen oder mit Rückstrichen: Exit 0. `_lauf()` ruft `subprocess.run(befehl, shell=True)`, unter Windows also `cmd.exe /c`, und `cmd.exe` nimmt den Schrägstrich im ungequoteten Programmnamen als Schalter. Git Bash und pwsh fahren denselben Befehl richtig; die Kit-Tests fahren `sys.executable`, absolut und in Anführungszeichen. Damit schickt ausgerechnet der Weg, der den vierten Ausgang verhindern soll, die Rolle in den Produktivcode — die Gattung von `BL-320`, am anderen Ende. **Bei der Triage bestätigt:** Der Nachtrag hat es am 2026-10-26 auf dieser Maschine am Kit-Werkzeug nachgestellt, Zeile für Zeile wie die Meldung; `smoke_warten.py` ist seit `17421e8` unverändert. Schon ein `.cmd` im Unterordner (`sub/probe.cmd`) scheitert genauso — der Windows-Testfall braucht kein venv. `smoke_warten.py` ist die einzige Stelle des Kits mit `shell=True`: Die Vollautomatik fährt `TEAM_SMOKE_TEST` auf der pwsh-Bahn über `Team-Werkzeug`, auf der bash-Bahn über die Shell, beide ohne `cmd.exe`. `_teile()` zerlegt den Befehl für `umgebung` schon heute Windows-gerecht | Feld B, 2026-10-26, Kit 2.13.1, win32/pwsh, Bestand, Python mit venv, Suite 7 bis 17 Minuten, `TEAM_SMOKE_TEST` mit relativem venv-Interpreter. Nachtrag: Kit, 2026-10-26, nachgestellt auf der Windows-Maschine am Quellstand `530e942`. Meldungen: `plans/meldungen/2026-10-26-smoke-warten-py-start-scheitert-unter-windows-an-einem-relat.md`, `plans/meldungen/2026-10-26-nachtrag-smoke-warten-py-start-unter-windows-am-kit-stand-nach.md` | **offen.** Vorschlag der Meldung: unter Windows den ersten Token vor dem Start normalisieren, als Pfad mit Rückstrichen oder in Anführungszeichen, dazu ein Testfall in der Feldform; sonst nennt die Doku die Einschränkung, und `start` warnt. Triage: normalisieren, eng geschnitten — nur unter Windows, nur der erste Token, nur ungequotet und mit Schrägstrich. Als reine Funktion, damit der Kern auch auf der Bau-Maschine testbar ist; dazu ein Windows-Fall mit echtem `cmd.exe`, der vor dem Fix rot ist. Das Feld wartet mit dem Umstieg auf diesen Fix. Ohne Entscheidung baubar |
| BL-346 | **`smoke_warten.py warten` ohne Kennung nimmt den Lauf mit dem größten Namen — ein einziger fremder `smoke-*.log` hält es für immer bei 75, und die Rolle wartet, bis Frist oder Budget erschöpft sind.** `start` druckte `20261026-121601-817710`; das folgende `warten` ohne Kennung meldete „Laeuft noch (stufe158-1790169213)" — ein Log vom 2026-09-23, von einer Rolle des Feldes selbst benannt, ohne `.rc`. Jeder weitere Aufruf: 75, und 75 heißt „läuft noch", nicht rot. Genau gegen diesen Ausgang ist `BL-281` gebaut; der Nachsatz der Rollen nennt `warten` ohne Kennung. **Bei der Triage bestätigt und nachgestellt:** `_juengster()` sortiert `.team-logs/smoke-*.log` nach dem Namen und nimmt den letzten, und `stufe…` sortiert hinter jede Kennung, die mit `2026…` beginnt. Am Kit-Werkzeug mit einem leeren `smoke-stufe158-1790169213.log` neben einem frischen Lauf: `warten` ohne Kennung Exit 75 mit der fremden Kennung, `warten <kennung>` Exit 0. Der Nachsatz in `bash/lib.sh` und `pwsh/lib.psm1` sagt wörtlich „danach rufst du '… smoke_warten.py warten' IM VORDERGRUND auf" | Feld B, 2026-10-26, Kit 2.13.1, win32/pwsh, Bestand, gut hundert Logs in `.team-logs/`, darunter zwei `smoke-*.log` aus der Zeit vor `smoke_warten.py`. Meldung: `plans/meldungen/2026-10-26-smoke-warten-py-warten-ohne-kennung-nimmt-den-lauf-mit-dem-g.md` | **offen.** Vorschläge der Meldung: nur Namen im eigenen Kennungsformat berücksichtigen oder nach Änderungszeit wählen; die Kennung aus `start` im Nachsatz an `warten` weitergeben; ein Testfall mit fremdem `smoke-*.log`. Triage: das Format, nicht die Änderungszeit — ein fremdes Log kann jünger sein, und im eigenen Format ist die Namensordnung die Zeitordnung. Dazu der Nachsatz beider Bahnen mit `warten <kennung>`. Ohne Entscheidung baubar |
| BL-347 | **`test_bl326` hängt unter Windows auf der bash-Bahn — `taskkill /T` erreicht den MSYS-Enkel der Attrappe nicht, und `kit-test.ps1` endet mit fünf roten Zeilen aus einem Testharnisch.** Die pwsh-Prüfung der Bauten vom 2026-10-18 endete nach 67 Minuten „NICHT grün": Schritt 2, Schritt 4 und dreimal Schritt 6, alle aus demselben Suite-Ergebnis — `2 failed, 1623 passed, 504 skipped`, beide `[bash]`-Fälle von `test_bl326_abgebrochener_rollenaufruf.py` mit `TimeoutExpired` in `_abschiessen()`. Am Nachbau ohne Kit: Windows sieht den Baum `bash.exe` → `bash.exe` → `sh.exe`, `taskkill /F /T` beendet alle drei; das `sleep.exe` der Attrappe hängt mit einer toten Eltern-PID nicht in diesem Baum (Fork-Nachbildung von MSYS), überlebt und hält die geerbten Pipes 60 s offen, und `communicate(timeout=30)` läuft vorher ab. Unter Linux greift `os.killpg` die ganze Sitzung, deshalb ist der Fall auf der Bau-Maschine grün. **Gegenprobe in einer Kopie:** `_abschiessen()` wartet unter Windows auf das Prozessende (`proc.wait(timeout=30)`) und schließt danach die Pipes — 29 passed statt 2 failed, 27 passed. Der Produktcode von `BL-326` arbeitet damit auf beiden Bahnen richtig; rot ist nur das Aufräumen des Tests | Kit, 2026-10-26 — `pwsh -File pwsh/kit-test.ps1` auf der Windows-Maschine (Git Bash und pwsh 7.6 nebeneinander) in einem eigenen Worktree mit bereinigter Umgebung, Quellstand `530e942`, Code wie `84a7e81`. Meldung: `plans/meldungen/2026-10-26-test-bl326-haengt-unter-windows-auf-der-bash-bahn-taskkill-t.md` | **offen.** Vorschläge der Meldung: (1) `_abschiessen()` wie in der Gegenprobe, Alternative ungeprüft: Die Attrappe wartet ohne MSYS-Kind (`exec sleep 60`); (3) ein Hinweis im Harnisch für künftige Tests, die unter Windows einen Baum mit Git Bash beenden. Vorschlag (2) ist `BL-348`. Triage: (1) wie belegt, (3) als Kommentar an `_abschiessen()`. Nur unter Windows nachweisbar: Die Bau-Maschine schreibt es, die Windows-Maschine fährt `kit-test.ps1`. Ohne Entscheidung baubar |
| BL-348 | **Schritt 2 beider Selbsttests liest einen roten Installer-Selbsttest als „nicht gefahren" — `kit-test.sh` bricht dann mit einer Meldung ab, die auf einen übersprungenen Selbsttest zeigt.** Im Lauf von `BL-347` meldete `kit-test.ps1` „der Installer hat seine Regressionstests wirklich gefahren (BL-127) — erwartet 'True', ist 'False'". Gefahren hatte er sie: Das Installer-Log zeigt „2 failed, 1623 passed …" und „Regressionstests nicht vollstaendig gruen". **Bei der Triage bestätigt:** Beide Prüfungen suchen nur die Erfolgszeile — `kit-test.ps1` zählt Treffer von `Regressionstests gruen`, `kit-test.sh` fragt `grep -q 'Regressionstests grün'` und meldet sonst „✗ Der Installer hat seine Regressionstests NICHT gefahren" mit `exit 1`. Ein einziger roter Test beendet den bash-Selbsttest also in Schritt 2, und wer der Meldung folgt, sucht am Installer statt in der Suite. Beide Installer unterscheiden die Fälle selbst: „Regressionstests grün", „nicht vollständig grün — Log: …" und „pytest nicht gefunden — Regressionstests übersprungen" (pwsh in ASCII-Schreibweise). Die bash-Hälfte ist aus dem Quelltext hergeleitet, nicht gefahren | Kit, 2026-10-26 — Nebenbefund der Meldung zu `BL-347`: `plans/meldungen/2026-10-26-test-bl326-haengt-unter-windows-auf-der-bash-bahn-taskkill-t.md` | **offen.** Vorschlag der Meldung: „gefahren" und „grün" getrennt prüfen, etwa an der Zusammenfassungszeile von pytest; rot bleibt rot, heißt aber nicht mehr „nicht gefahren". Triage: an den drei Zeilen der Installer, nicht an pytest — sie sind die Schnittstelle, die `BL-127` prüft. „übersprungen" bleibt der `BL-127`-Fall, „nicht vollständig grün" wird „gefahren, aber rot" mit den `FAILED`-Zeilen aus dem Log. Owner: ob `kit-test.sh` danach weiterfährt wie `kit-test.ps1` — Empfehlung ja, die übrigen Schritte liefern unabhängige Befunde (im Windows-Lauf waren sie alle grün) |
| BL-349 | **`team-status.cmd` bucht auf der pwsh-Bahn stumm — die Erfolgsmeldung mit der gebuchten Achse, die das Briefing lesen lässt, erscheint nie, und ein Werkzeug, das auf stdout schreibt und rot endet, endet dort mit Exit 0.** Der Architekt buchte am Ende seiner ersten Planungssitzung wie verlangt (`BL-165`): `.\team-status.cmd --architekt-abschluss 6.9315 produkt "<notiz>" --kaskade 1 …`. Erwartet war „Architekt-Zeile Kaskade 1 (produkt) angelegt: 6.9315 USD (abo)" samt dem Hinweis aus `BL-252`; das Briefing verlangt, die Zeile zu lesen, weil sie die gebuchte Achse nennt (`BL-143`). Es kam nichts, Exit 0, die Zeile stand richtig im Ledger. Der Fehlerweg (stderr) kommt durch, der Erfolgsweg (stdout) nicht, und nur auf der pwsh-Bahn. Ursache: Der Verteiler endet mit `exit (Status-ArchitektAbschluss $rest)`, und `exit (…)` nimmt alles, was die Funktion auf den Ausgabestrom schreibt, als ihren Rückgabewert — auch die stdout-Zeilen von `kosten.py`, das über `Team-Werkzeug` (`& $befehl …`) läuft. **Bei der Triage nachgestellt** in einer Wegwerf-Installation mit beiden Bahnen: `--architekt-abschluss` und `--akteur-abschluss` auf der pwsh-Bahn Exit 0 ohne jede Ausgabe, die Zeilen geschrieben; die Kollision Exit 1 mit Meldung; `./team-status.sh --architekt-abschluss` druckt Zeile und Hinweis. Die zweite Hälfte ebenfalls gemessen: Schreibt die gerufene Funktion auf stdout und liefert 1 oder 3, endet das Skript mit 0; ohne Ausgabe stimmt der Code. Daraus hergeleitet, nicht gefahren: `--rollen-abschluss` bucht zwei Hälften nacheinander; scheitert die zweite nach der Vorprüfung aus `BL-239`, steht die erste Buchung schon auf stdout, und der Wrapper meldet Exit 0. `exit (Funktion)` gibt es nur in `team-status.ps1`, für fünf Verben; `Status-Hilfe` und `Status-Altlast` schreiben deshalb über `[Console]::Out` — die drei Buchungswege nicht. Kein Test sieht es: `test_bl143::test_die_meldung_nennt_die_achse` prüft die Meldung am Werkzeug direkt, `test_pwsh_wrapper_reicht_schalter_durch` nur Exit-Code und Ledger | Feld H, 2026-10-26, Kit 2.13.1, win32/pwsh, Greenfield, erste Architekten-Sitzung, noch keine Kaskade. Meldung: `plans/meldungen/2026-10-26-team-status-cmd-bucht-auf-der-pwsh-bahn-stumm-die-meldung-mi.md` | **offen.** Vorschlag der Meldung: Die Buchungsfunktionen geben die Werkzeugausgabe ausdrücklich auf den Bildschirm, wie `Status-Hilfe` über `[Console]::Out.WriteLine`, und liefern nur den Exit-Code zurück; ein Regressionsfall auf der pwsh-Bahn, dass die Erfolgsmeldung erscheint. Triage: so, für alle drei Buchungsverben samt `team_akteur_abschluss` in `pwsh/lib.psm1` (nur von hier gerufen). Nicht über `Out-Host` — das schreibt an einer Umleitung vorbei, und die Tests lesen stdout. Dazu ein zweiter Fall: Ein `TEAM_KOSTEN_TOOL` als Attrappe, das auf stdout schreibt und mit 3 endet, ergibt Exit 3. Nur mit pwsh nachweisbar. Ohne Entscheidung baubar |
| BL-350 | **`team-status.cmd --hilfe` druckt vor dem Hilfetext drei Fehler — ein zitiertes `#>` beendet den Kommentarblock von `Status-Hilfe`, und der Wächter aus `BL-229` sieht es nicht, weil der Rest der Zeile parst.** `The term 'am' is not recognized …`, ebenso für `waechst` und `Hilfe`; die bash-Bahn druckt die Hilfe sauber. Der Kommentarblock enthält „Gelesen wird der Block zwischen `<#` und `#>` am Dateianfang"; Backticks maskieren in einem PowerShell-Kommentar nichts, und die Reste der Zeilen laufen als Befehle — die Bauart von `BL-229`, an dem ein zitiertes Endezeichen `pwsh/lib.psm1` zerlegt hatte. **Bei der Triage nachgestellt:** stdout trägt die Hilfe vollständig, stderr beginnt mit `am: … team-status.ps1:534`, Exit 0. Gattungssuche über alle `.ps1` und `.psm1`: nur diese Stelle. `test_bl229_pwsh_dateien_parsen.py` prüft, ob jede Datei parst, und hier parst sie: „am Dateianfang; waechst der Kopf, waechst die" und „Hilfe mit." sind gültige Befehlszeilen | Feld H, 2026-10-26 — Beifang der Meldung zu `BL-349`: `plans/meldungen/2026-10-26-team-status-cmd-bucht-auf-der-pwsh-bahn-stumm-die-meldung-mi.md` | **offen.** Vorschlag der Meldung: den Satz ohne `#>` schreiben („zwischen den Kommentarmarken am Dateianfang"); ein Regressionsfall, dass `--hilfe` keine Fehlerzeile druckt. Triage: so, und den Wächter aus `BL-229` um die Gattung erweitern: Hinter dem schließenden `#>` eines Blockkommentars steht auf derselben Zeile nichts mehr — geprüft am Tokenstrom des Parsers, nicht per Textsuche. Das fängt diesen Fall und lässt einzeilige Blöcke wie `<# BL-147: … #>` durch. Ohne Entscheidung baubar |
| BL-351 | **Ein Red-Team-Fund stellt über Franks Fix einen Vertragswert um, den der Plan mit einer Messung belegt — beide Rollen regelkonform, sichtbar erst dort, wo der Vertrag gebraucht wird. Zweimal im Feld.** (1) Der Plan legte unter „Verträge" eine Auftragsgrenze für das lokale Modell fest (24.000 geschätzte Token, Antwortlänge 16.384) und belegte mit einer Vorprobe samt Rohdaten: Der Server kürzt nicht still — ein Prompt über dem Fenster endet mit HTTP 400, eine Antwort am Fensterrand mit `finish_reason` `length`. Harry meldete (mittel), Grenze plus Antwortlänge überstiegen das Fenster, der Server kürze „je nach Einstellung stillschweigend den Prompt" — als Erwartung, nicht als Beobachtung, regelkonform nach `BL-289`, denn den Server durfte er im Loop nicht fahren. Frank setzte die Erwartung um (Grenze 16.384), Dreisatz sauber, der neue Test vor dem Fix rot. Im Closeout wurde eine der fünf Abnahmeaufgaben (17.000 Token, in der Vorprobe dreimal grün) vor dem Modellaufruf abgelehnt, und das halbe Fenster blieb für jeden Auftrag ungenutzt; der Stakeholder ging zum Planwert zurück und hielt den belastbaren Kern über eine andere Mechanik. Kosten: eine weitere Fix-Runde, eine Abnahme in zwei Teilen. (2) In der dritten Kaskade behauptete ein Fund, `git check-ignore` erkenne einen Ordner mit dem Muster `/ordner/*` nicht, korrekt als „nicht ausgeführt" gekennzeichnet; Frank stellte den Prüfpfad des Plans um und schrieb einen Test. Die Gegenprobe im Closeout: Der Test war schon vor dem Fix grün, die Behauptung falsch (Git 2.55 meldet den Ordner als ignoriert) — diesmal folgenlos. **Bei der Triage bestätigt:** Punkt 3 des Beutezug-Dreisatzes verlangt Belege für das Laufzeitverhalten einer **Sprachkonstruktion** und für das Ergebnis eines Befehls, den der Finder ausführen **kann**; ein Fremdsystem, das im Loop niemand starten darf, fällt durch beide Raster — auch wenn der Plan das Gegenteil gemessen hat. Das Ausschlusskriterium für die Übergabe kennt nur „die Reproduktion ist eine Messreihe". Fall (2) hätte Franks eigene Regel gefangen („Ohne meinen Fix muss dieser Test rot werden — geprüft, nicht vermutet", `rolle-frank.md` und Schritt 0 in `frank.*`), aber sie steht nur im Prompt: `team_reproducer_liegt_vor` prüft, ob die Datei existiert, nicht, ob sie ohne den Fix rot ist. Fall (1) fängt auch sie nicht — der Test war rot, weil er die neue Erwartung festschrieb | Feld H, 2026-10-27 (Fall 1, zweite Kaskade, sieben Stufen) und 2026-10-28 (Fall 2, dritte Kaskade; Teil 3 der Meldung zu `BL-352`), Kit 2.13.1, win32/pwsh, Greenfield. Meldung: `plans/meldungen/2026-10-27-ein-red-team-fund-aendert-ueber-franks-fix-einen-vertragswer.md` | **offen.** Vorschläge der Meldungen: (a) Punkt 3 erweitern — behauptet ein Fund Verhalten eines Fremdsystems, das der Plan gemessen hat, zitiert er die Planstelle und begründet, warum die Messung nicht trägt; (b) das Ausschlusskriterium erweitern — ein Fund, dessen Erwartung einen Wert aus den Verträgen des Plans ändert (Grenze, Konstante, Exit-Code, Format), geht an den Architekten, nicht an Frank; (c) Frank als Netz: Stellt ein Fix einen Planwert um, nennt der Commit-Text die Planstelle; (d) Frank fährt seinen Test gegen den Stand ohne Fix, und ist er dort grün, geht die Prämisse zurück an den Architekten. Triage: (a) und (b) in `CLAUDE.md.vorlage`, je mit NORM-Zeile im Regel-Inventar (Zeile 90 trägt das heutige Kriterium). (c) und die Folge aus (d) zeilenneutral in `rolle-frank.md`, das wie die Briefings von Harry und Marv auf der 45-Zeilen-Grenze steht — zusammen mit `BL-335` bauen, der denselben Absatz anfasst und mit seiner Sechszeilen-Fassung eine Zeile freigibt. (d) als Prüfung ist heute Regel, nicht Mechanik; das Kit könnte den neuen Test nach Franks Lauf selbst gegen den Elternstand fahren und grün als Befund melden — der Weg „Programm statt Prompt", aber ein Bau am geldausgebenden Pfad. Zu (b): „Verträge" ist im Feldplan ein eigener Abschnitt; das Kit kennt den Begriff nur als Planungsfrage („welche bestehenden Verträge berührt das Neue?"). Owner: wer über einen vertragsändernden Fund entscheidet (der Architekt, wie die Meldung vorschlägt, oder gleich der Stakeholder); ob „Verträge" ein fester Planabschnitt wird, damit Harry und Marv ihn finden; ob die Gegenprobe Mechanik wird |
| BL-352 | **Eine Stufe, die ein Programm statt eines Agenten baut, hat im Loop keinen Platz — der Bau trug, aber an drei Nähten von Hand.** In der dritten Kaskade trug eine Stufe statt eines Promise einen Bauauftrag (zu ändernde Datei, Abnahmetest). Der Mensch rief das Programm vor der Vollautomatik von Hand — es lässt das lokale Modell einen Bauschritt machen: Auftrag samt roter Abnahmetests, Änderung, Smoke-Test, Commit —; es baute im ersten Versuch und committete `feat(stufe1): …` mit Trailern (Versuche, Sekunden, Token). Danach setzte der Mensch `.ralph-state` weiter, Ralph hatte Feierabend, Harry und Marv sweepten, Frank fixte drei Funde. Die Nähte: (1) Den Bau startet und quittiert der Mensch; der Loop kennt keine Stufe ohne Promise, und ein Promise braucht es auch nicht — das Programm weiß, ob die Tests grün sind (Exit 0 und ein neuer Commit). (2) Die Baukosten sind lokal (Sekunden, Token), nicht USD; ohne ralph-Zeile meldet `--ledger-pruefen` im Closeout „keine ralph-Zeile, obwohl eine roles-Zeile steht … (Kit-BL-4-Muster)" mit Exit 4 — ein richtiger Zustand als Warnung in jedem Closeout einer solchen Kaskade. (3) Die Abnahmequelle liegt unter `plans/<plan>/stufe-<N>/tests/`; der Konsistenz-Check nennt sie „weder Team-Artefakt noch Bestand" (`BL-237`), und nur ihr Prompt hält Harry und Marv davon ab, sie zu ändern. **Bei der Triage bestätigt:** Jede Rolle ruft `team_claude()` (`bash/lib.sh`, `pwsh/lib.psm1`); die Warnung steht in `kosten.py` für jede nummerierte Kaskade mit roles- und ohne ralph-Zeile; `schreibzone.py` meldet die Datei. Für (3) gibt es schon heute einen Weg: `TEAM_PLAN_ORDNER_BESTAND` nimmt Präfixe und Muster (`fnmatch`), und ein Eintrag wie `*/stufe-*/tests/*` nennt alle Abnahmequellen im Prompt der Read-Only-Rollen als fremdes Eigentum und macht den Hinweis stumm. Eine Guard-Sperre im Plan-Ordner haben `BL-51` und `BL-237` bewusst verworfen — auf seiner eigenen Whitelist kann der Guard nicht urteilen | Feld H, 2026-10-28, Kit 2.13.1, win32/pwsh, Greenfield, dritte Kaskade mit einer Stufe, erstmals vom Programm gebaut. Meldung: `plans/meldungen/2026-10-28-lokale-stufen-im-team-weg-fuer-eine-stufe-die-ein-programm-b.md` (Teil 1; Teil 2 ist `BL-353`, Teil 3 der zweite Feldfall von `BL-351`) | **offen — ein Strang, vor dem Bau eine Skizze.** Vorschläge der Meldung: Eine Stufe mit Bauauftrag ruft ein konfigurierbares Programm statt `team_claude()`, Exit 0 plus neuer Commit ist die Quittung, jeder andere Exit hält den Loop mit dem Bericht des Programms an; im Ledger eine Einheit oder Kennzeichnung „lokal", und `--ledger-pruefen` nimmt die fehlende Bau-Zeile hin, wenn alle Stufen der Kaskade Programm-Stufen waren; Abnahmequellen unter `plans/` als bekannte Art im Konsistenz-Check, per Guard gesperrt. Triage: Alle drei hängen an der Auflage des Owners aus `BL-354` — die Programm-Stufe ist dort die Ebene „je Stufe im Plan", die Einheit ist `BL-247` Punkt 4, und eine Phase ohne Modell ist die offene Frage von `BL-340` Teil B. Das gehört in eine gemeinsame Skizze. Bis dahin nennt die Doku den Weg über `TEAM_PLAN_ORDNER_BESTAND` für (3); eine Guard-Sperre bräuchte eine Entscheidung gegen `BL-51`. Owner: die Skizze |
| BL-353 | **Die Suite ist in jeder Rolle grün und im Terminal des Menschen rot — die Rolle erbt eine Konsole mit abgeschaltetem Strg+C, und die Regel zur Verifikationskette kennt nur Umgebung, die ein Befehl setzt.** Eine Lebensprüfung im Produktivcode nutzte `os.kill(pid, 0)`; unter Windows ist `0` der Wert von `CTRL_C_EVENT`, der Aufruf schickt also ein Strg+C in die eigene Konsole. Die Suite war in jedem Lauf aller Rollen grün. Im Terminal des Menschen brach der Smoke-Test bei 60 % ohne Ergebniszeile ab, und pwsh beendete die ganze Befehlszeile mit Exit 1. Gefunden hat es erst eine Probe des Architekten in einer eigenen Konsole mit eingeschaltetem Strg+C. Die Regel „Der Smoke-Test darf keine Umgebung setzen, die die Doku nicht nennt" greift nicht: Nicht der Befehl setzt die Umgebung, sondern die Sitzung. **Bei der Triage gemessen,** an der laufenden Sitzung (Claude Code unter Windows 11), rein lesend über die geerbte Marke „Strg+C ignorieren" im Prozessblock jedes Prozesses: `claude.exe` selbst hat Strg+C eingeschaltet. Abgeschaltet ist es im Baum des Bash-Werkzeugs, ab dem ersten `bash.exe` von Git, und alles darunter erbt es — auch ein von dort gestartetes `pwsh` oder `python`. Der Baum des PowerShell-Werkzeugs derselben Sitzung (`cmd.exe` → `pwsh.exe`) hat es eingeschaltet; startet man daraus Git Bash, ist es darunter wieder aus. Die Marke kommt also mit Git Bash, nicht mit der CLI. Die Meldung beschreibt damit genau den Weg, auf dem eine Rolle unter Windows Befehle über das Bash-Werkzeug fährt; welche Schale sie nimmt, wählt das Modell. `signal.CTRL_C_EVENT` ist 0. Der Zwei-Schritt-Weg startet die Suite zudem ohne Konsole in einer neuen Prozessgruppe (`smoke_warten.py start`: `DETACHED_PROCESS`, `CREATE_NEW_PROCESS_GROUP`) | Feld H, 2026-10-28, Kit 2.13.1, win32/pwsh, Greenfield, dritte Kaskade. Meldung: `plans/meldungen/2026-10-28-lokale-stufen-im-team-weg-fuer-eine-stufe-die-ein-programm-b.md` (Teil 2) | **offen.** Vorschläge der Meldung: ein Werkzeug, das den Smoke-Test einmal in einer frischen Konsole mit eingeschaltetem Strg+C fährt (Windows: neue Konsole, `SetConsoleCtrlHandler(NULL, FALSE)`), etwa im Closeout oder in `team-test`; dazu ein Satz in der Verifikationskette, dass der Zustand der Konsole zur Umgebung gehört. Triage: der Satz in jedem Fall, mit NORM-Zeile (das Regel-Inventar trägt die heutige Regel in Zeile 54) — und die Messung gehört hinein: Git Bash schaltet ab, die CLI nicht. Für die Probe passt die Richtung „Programm statt Prompt" besser als ein weiterer Satz im Closeout: ein Werkzeug, nur unter Windows, das den Smoke-Test in einer neuen, verborgenen Konsole mit eingeschaltetem Strg+C fährt und das die Vollautomatik am Ende einmal ruft. Owner: ob das Werkzeug gebaut wird oder der Satz genügt |
| BL-354 | **Lokal oder entfernt je Rolle, jederzeit umschaltbar — und entfernte Modelle nur auf ausdrückliche Anweisung: die Auflage des Owners an die lokale Stufe.** Nach der ersten Stufe, die das lokale Modell gebaut hat, entschied der Owner die Endform: Die lokale Werkbank wird ein lokaler Teil des Kits. Wörtlich: „Wird ein lokaler Teil des Kits, das Kit soll skalierbar sein für den Benutzer und zwar jederzeit, im Sinne von welche Rolle wird 100% lokal und umgekehrt, oder auch nur 50% nach ermessen des Architekten, oder auch auf Zuruf des Benutzers spontan". Die offene Frage, ob „umgekehrt" ein Rückfall sein darf, beantwortet der Nachtrag: „die Nutzung entfernter Modelle wird dann nur mit expliziter Anweisung des Benutzers erfolgen, ggf mit Einrichtungsskript für bspw OpenRouter, Anthropic, OpenAI, etc. Abo oder Api, flexibel!" Scheitert eine lokale Rolle, übergibt sie an den Menschen, statt auszuweichen. **Bei der Triage eingeordnet:** Die Wahl gibt es heute nicht — jede Rolle ruft `team_claude()`, und die Auth-Auflösung kennt einen Anbieter: Abo zuerst, die API als automatischer Rückfall (Stakeholder-Entscheid 2026-07-10, `bash/lib.sh`). Skizze F (Codex neben Claude Code) stellt dieselbe Frage für eine zweite CLI und nennt vier Verträge, die jeder zweite Weg mitbringen muss: Ergebnis-JSON, Auth-Fallback, 429-Behandlung, `--permission-mode`. Für ein lokales Modell hinter einem Programm gelten sie anders — die Quittung ist dort Exit-Code und Commit (`BL-352`) | Feld H, 2026-10-28, Kit 2.13.1, win32/pwsh; Auflage des Owners mit Nachtrag. Meldungen: `plans/meldungen/2026-10-28-lokal-oder-entfernt-je-rolle-jederzeit-umschaltbar-auflage-d.md`, `plans/meldungen/2026-10-28-nachtrag-entfernte-modelle-nur-auf-ausdrueckliche-anweisung.md` | **offen — die Entscheidung steht, der Weg nicht.** Vorschläge der Meldungen: drei Ebenen derselben Wahl — eine Vorgabe je Rolle in `team.config.*` (lokal, entfernt oder gemischt), je Stufe im Plan nach Ermessen des Architekten (im Feld: der Bauauftrag aus `BL-352`), auf Zuruf beim Start nur für diesen Lauf; entfernt nur, wenn eingestellt oder angewiesen; ein Einrichtungsskript je Anbieter, je mit Abo oder API. Triage: eine Skizze in `roadmap-skizzen.md`, die `BL-352` und `BL-354` zusammen trägt, mit `BL-247` Punkt 4 (die Kosteneinheit „lokal") und `BL-340` Teil B (eine Phase ohne Modell) als Teilen und mit ihrem Verhältnis zu Skizze F. Owner, vor der Skizze: ob „nur ausdrücklich" auch den heutigen automatischen Rückfall vom Abo auf die API betrifft — beide Wege sind entfernt, aber `BL-316` zeigt, was ein stiller Rückfall kostet; welche der drei Ebenen zuerst |

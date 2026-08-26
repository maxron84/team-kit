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

> **Feldbelege tragen Kürzel statt Namen** (`Feld A`…`Feld D`) —
> die Profiltabelle steht im [README](../README.md#herkunft).

> **Abgetragene Einträge stehen im Archiv:**
> [`backlog-archiv.md`](backlog-archiv.md). Dort liegt die vollständige
> Begründung jedes erledigten Punktes — sie wird nachgeschlagen, nicht
> mitgelesen. Diese Datei trägt nur, woran noch Arbeit hängt (`BL-53`).

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

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-190 | **Fehlt `flock`, meldet das Kit „eine andere Pipeline läuft bereits" — und bricht ab.** `team_lock()` in `lib.sh` (Zeile ~1109) öffnet `.team-loop.lock` auf Deskriptor 9 und entscheidet dann an **einer** Bedingung: `if ! flock -n 9; then` → Meldung „Eine andere T.E.A.M.-Pipeline läuft bereits (.team-loop.lock) — Abbruch." und Rückgabe 1. Ein **fehlendes Programm** liefert dort denselben Nicht-Null-Status wie eine **belegte Sperre**. Unter Git for Windows gibt es `flock` nicht — es gehört nicht zum MSYS2-Kern, den Git mitliefert. **Folge:** Auf einer solchen Maschine bricht **jede** Rolle der bash-Bahn sofort ab, mit einer Meldung, die auf einen Nebenläufigkeitskonflikt zeigt, den es nicht gibt. Wer ihr folgt, sucht nach einem zweiten Lauf, killt Prozesse oder löscht die Lock-Datei — und nichts davon hilft, weil die Datei nie das Problem war. Der wahre Grund (`flock: command not found`) scrollt eine Zeile vorher vorbei und ist die einzige Spur. **Das ist dieselbe Fehlerklasse wie `BL-173` und `BL-162`:** ein fehlendes Mittel wird in eine bestehende Fehlerklasse gepresst, in die es nicht gehört — dort ein PATH-Problem als Auth-Fehler, hier ein fehlendes Werkzeug als Sperrkonflikt. **Was NICHT betroffen ist:** die pwsh-Bahn (sie sperrt über einen eigenen Weg) und alles, was unter `TEAM_LOCK_HELD=1` läuft — also die Kind-Skripte der Vollautomatik und die Rollen-Tests der Suite, die diese Variable seit Langem setzen. Genau deshalb ist der Fall im Selbsttest nie aufgefallen: Die Testkonvention umgeht die Sperre, und die Zielumgebung des Kits war bisher Linux oder WSL, wo `flock` vorhanden ist | Kit, 2026-08-26 — beim Bauen des Lauf-Vergleichs für `BL-117` gefunden. Der erste Vorflug in einer echten Installation auf dieser Maschine starb an dieser Stelle, bevor ein einziger Prompt entstand: `./team/lib.sh: line 1114: flock: command not found` / `[harry] Eine andere T.E.A.M.-Pipeline läuft bereits`. **Gemessen, nicht vermutet:** `command -v flock` ist auf der Maschine leer, `.team-loop.lock` war neu angelegt und von niemandem gehalten. Der Fund ist ein Nebenprodukt der Vorflug-Regel (neue Testdateien in **beiden** Ablagen fahren) — im Kit-Layout überspringt der Test, und dort wäre nichts aufgefallen | **offen.** Zwei Teile, und der zweite wiegt schwerer als der erste. **(1) Die Fehlerklasse trennen:** `team_lock` prüft **vor** dem Sperrversuch, ob `flock` überhaupt auflösbar ist, und meldet im Fehlfall den wahren Grund — nicht einen Sperrkonflikt. Dieselbe Bauart wie `team_cli_vorhanden`/`team_cli_fehlt_melden` aus `BL-173`; die Vorlage steht also schon im Haus. **(2) Entscheiden, was dann gilt** — und das ist eine Frage an den Betreiber, keine technische: Läuft das Team ohne Sperre weiter (laut, mit einer benannten Einschränkung), oder bricht es ab? **Für „weiterlaufen" spricht,** dass die Sperre gegen *versehentliche* Doppelläufe schützt und ein Einzelbetreiber auf einer Windows-Maschine praktisch nie zwei Pipelines startet. **Für „abbrechen" spricht,** dass ein Doppellauf zwei Rollen gleichzeitig in denselben Arbeitsbaum committen lässt — und das ist der Schaden, den `BL-12` teuer belegt hat. **Eine dritte Möglichkeit, die beides erfüllt:** ein Ersatzverfahren ohne `flock` — ein Sperrordner per `mkdir` (atomar auf jedem POSIX-Dateisystem und unter MSYS), der die PID hinterlegt und beim Aufräumen wieder verschwindet. Dann bleibt die Zusicherung erhalten, statt sie gegen eine Meldung zu tauschen. **Gegenprobe, die den Fix erst gültig macht:** Zwei Läufe in derselben Ablage, der zweite muss abgewiesen werden — **auf einer Maschine ohne `flock`**. Und ein Lauf, bei dem `flock` fehlt und keine Sperre gehalten wird, muss genau **eine** Meldung erzeugen, die das Werkzeug nennt, und **keine** über eine fremde Pipeline. Ein Stub, der `flock` aus dem PATH nimmt, reicht für beides |
| BL-169 | **`src/` + `tests/` als ausgelieferte Ordner-Defaults machen Reproducer-Tests in jedem Stack mit paketgebundener Testsuche unausführbar — und zwar stumm.** `bootstrap/team.config.sh` belegt `TEAM_PRODUKTIVCODE` mit `src/` und `TEAM_TEST_ORDNER` mit `tests/` vor. Das trägt, solange der Testläufer die Dateien am **Pfad** findet (pytest). Es trägt **nicht**, sobald er sie am **Paket** findet: Dart/Flutter sammelt ausschließlich innerhalb des Pakets und ausschließlich unterhalb von `test/`; liegt das Paket unter `src/`, liegt der vom Kit vorgesehene Testordner **außerhalb** davon. Dieselbe Bauart bei Cargo (`tests/` relativ zu `Cargo.toml`), Go (Paketverzeichnis) und Gradle (`src/test/`). **Die zweite Hälfte ist vom Ordner unabhängig und wiegt schwerer:** Der Läufer nimmt nur Dateien mit einem bestimmten Namensmuster — `_test.dart` bei Dart, `_test.go` bei Go. Die Konvention des Kits lautet `tests/test_hm<nr>_<stichwort>.py` und steht wörtlich in `bootstrap/CLAUDE.md.vorlage` (Fund-Format **und** der Absatz zur Benennung nach der Fund-Nummer), in `bootstrap/beutebuch.md` und in `geteilt/prompts/rolle-harry.md`/`rolle-marv.md`. Buchstabengetreu auf Dart übertragen ergibt das `test_hm36_foo.dart` — einen Namen, den der Läufer ignoriert. **Folge in beiden Hälften identisch:** Franks regelkonform abgelegter Reproducer wird nie ausgeführt, der Smoke-Test bleibt grün, das Beutebuch zeigt einen Fund mit Reproducer, geprüft wird nichts. Das ist derselbe Schaden wie `BL-15` (Backtick-Regel) und `BL-28` (`strict`-Marker), nur eine Ebene tiefer: Dort war der Test da und stumm markiert, hier wird er gar nicht erst gefunden. **Nicht betroffen ist der Extraktor:** `DATEI_RE` in `team/tools/beutebuch.py` akzeptiert jede Endung und hat den umgestellten Dart-Pfad im Lauf korrekt als `test/hm6_stichwort_test.dart` erkannt — der Substanz-Anker trägt, allein die Vorgabewerte und Beispiele tragen nicht | `Feld E`, 2026-08-23, vom Architekten beim Aushärten der **ersten** Kaskade gefunden — durch Lesen der Kopplung zwischen Konfiguration und Testläufer, **bevor** ein Lauf startete. Dasselbe Zeitfenster wie `BL-149`: Sobald ein Projekt seine Ordner einmal richtig gesetzt hat, ist der Default für immer unsichtbar, und ein laufendes Projekt kann den Fehler gar nicht mehr erleben. Getroffen wird ausschließlich der Erstlauf | **offen.** Zwei Wege, und sie fangen Verschiedenes. **(1) Der Installer leitet ab statt vorzugeben:** Er kennt den Stack bereits aus dem Aufnahme-Interview — aus ihm folgen Produktivcode-Ordner, Testordner **und** das Namensmuster des Reproducers. Für Dart/Flutter `lib/` + `test/` + `<name>_test.dart`, für Cargo `src/` + `tests/`, für Go das Paketverzeichnis + `_test.go`. **(2) Wo der Stack unbekannt bleibt**, gehört die Kopplung in den Kommentar von `bootstrap/team.config.sh`, in einem Satz: *Der Testordner muss dort liegen, wo der Läufer sucht, und der Dateiname so heißen, dass er ihn nimmt.* Beides zusammen, nicht eines davon — (1) hilft dem erkannten Stack, (2) dem unerkannten. **Die Gegenprobe, die den Fix erst gültig macht:** Eine frische Installation für einen paketgebundenen Stack, in der die ausgelieferte `Reproducer-Test`-Zeile ausgefüllt, die Datei angelegt und der **konfigurierte Smoke-Test** gefahren wird — er muss diese Datei nachweislich **ausführen**. `test_bl15_reproducer_zeile_ankertauglich.py` prüft heute, ob `DATEI_RE` den Pfad sieht; ob der Testläufer ihn sieht, prüft niemand, und genau dort sitzt der Fund |
| BL-171 | **`kit-test.sh` kann in einem Nicht-Python-Zielprojekt nicht grün werden — zwei Zusicherungen prüfen die Sprache statt der Sache.** Nachdem `Feld E` seine Reproducer-Konvention vom Python- auf das Dart-Format gezogen hatte (`BL-158`), meldete `./team-test.sh` dort **sieben** Fehlschläge, keinen davon an der Eigenschaft, die der jeweilige Test absichern soll. **(1) `geteilt/tests/test_bl15_reproducer_zeile_ankertauglich.py:153`** — der Test prüft zuerst das Richtige, nämlich ob `DATEI_RE` in der ausgefüllten `Reproducer-Test`-Zeile überhaupt einen Pfad findet. Dieser Teil war **grün**. Erst die Folgezeile bricht: Sie verlangt zusätzlich, dass der extrahierte Pfad auf `.py` endet — der Ordner kommt aus der Konfiguration, die Endung steht als Literal daneben. Vier Fälle (Beutebuch-Vorlage, Regeldatei, Briefing Harry, Briefing Marv). **(2) `geteilt/tests/test_bl28_reproducer_wirksam.py:211`** — `test_briefings_verlangen_strict` verlangt den **pytest**-Marker `strict=True` wörtlich in der Regeldatei und in zwei Briefings, drei Fälle. In Dart gibt es dazu keine Entsprechung: Das Test-Paket kennt nur `skip:`, und `skip:` ist in beide Richtungen stumm, also genau der Marker, den `BL-28` verbietet. Die einzige sichere Regel für Dart lautet deshalb, dass das Red Team einen roten Reproducer **gar nicht erst anlegt** und nur den Dateinamen reserviert, während Frank die Testdatei mit dem Fix schreibt — das ist **strenger** als die Kit-Regel und fällt trotzdem als Verstoß durch. **Warum ein roter Sockel teurer ist, als er aussieht:** `TEAM.md` nennt `./team-test.sh` als den Befehl, mit dem man das Team selbst prüft. Sieben dauerhaft rote Fälle machen die Suite als Signal wertlos — der nächste echte Regressionsfund geht darin unter, und niemand kann ohne Nachlesen sagen, welcher Fehlschlag neu ist. **Der naheliegende Ausweg ist der falsche und deshalb die eigentliche Gefahr:** Ein Projekt biegt seine Regel auf pytest-Formulierungen zurück, damit die Suite grün wird. Dann steht in seiner Regeldatei ein `strict=True`, das es in seiner Sprache nicht gibt — grüne Suite, fiktive Regel. Das ist die Bauart von `BL-17`, angewandt auf die Selbstprüfung des Kits | `Feld E`, 2026-08-23, beim Aushärten der ersten Kaskade. Die sieben Fälle wurden dort bewusst **nicht** gepatcht: an den Kit-Tests vorbeizureparieren hieße, die Verifikation abzuschaffen statt das Problem zu lösen. Sie stehen im Projekt-Backlog als bekannter Sockel, damit ein späterer Lauf neue Fehlschläge von diesen unterscheiden kann | **offen.** Beide Zusicherungen an die konfigurierte Sprache binden statt an Python. **(1)** Die erwartete Endung aus derselben Quelle ziehen wie `TEST_ORDNER` — das Namensmuster des Reproducers ist ohnehin der Wert, den `BL-158` in die Konfiguration holen will; die beiden Einträge teilen sich diesen Fix. **(2)** Statt des Literals `strict=True` prüfen, dass die Regeldatei **überhaupt eine** Aussage darüber trifft, wie ein roter Reproducer zu behandeln ist — die Zusicherung von `BL-28` ist „es gibt keine stummen Ausgänge", nicht „es steht pytest da". Wo das Kit die Sprache nicht kennt, ist ein sichtbarer Übersprung mit Begründung ehrlicher als ein Fehlschlag; die Doppelbahn-Quote führt dafür bereits die passende Bauform. **Gegenprobe:** Dieselbe Suite in einer Installation mit nicht-Python-Konfiguration fahren — sie muss grün sein, **und** ein absichtlich stumm markierter Reproducer muss sie rot machen |
| BL-145 | **`kit-test.ps1` fährt 6 von 11 Schritten und 15 von 127 Einzelprüfungen — und genau diese Lücke hat `BL-136` durchgelassen.** Der Fix zu `BL-136` (`.gitattributes` ins Zielprojekt) ist als „kit-test.ps1 alle 6 Schritte grün (EXIT 0)" nachgewiesen worden. Er war es auch — nur prüft `kit-test.ps1` den Fall gar nicht, an dem er zerbrach: Die `.gitignore`/`.gitattributes`-Zusicherungen des Update-Pfads leben in Stufe 6 von `kit-test.sh` (dort inzwischen 30 Einzelprüfungen), und der pwsh-Selbsttest hat davon eine dünne Fassung. Ergebnis: Der Selbsttest der **bash**-Bahn war rot, während der Nachweis der pwsh-Bahn grün meldete — vier Commits lang unbemerkt (`BL-144`). **Was `kit-test.ps1` gar nicht hat:** Stufe 5 (zweiter Suite-Lauf unter angepasster Konfiguration, `BL-58` — dort fällt eine falsch gesetzte Messstelle auf, die in einer frischen Installation nie auffällt), Stufe 7 (Einzug in eine gewachsene Codebasis, `BL-51`/`BL-52`), Stufe 8 (Abwahl einer Bahn und ihr Rückweg, `BL-119` — **hier liegt seit `BL-129` die Zusicherung, dass eine einbahnige Ablage grün bleibt**), Stufe 9 (Regel-Inventar gegen die Regeldatei, `A.10`/`BL-56`), Stufe 10 (Einrichtungsroutine) und Stufe 11 (Gleichstand der Installer). Die Zahl `$PruefungenSoll = 15` ist dabei selbst ein Absturzschutz und richtig gebaut — sie sichert nur einen viel kleineren Umfang ab, als ihr Name vermuten lässt | Kit, 2026-08-21 — beim Abtragen von `BL-144` als Ursache **hinter** der Ursache ausgewiesen. Gemessen, nicht geschätzt: 6 gegen 11 Schritte, 15 gegen 127 Einzelprüfungen im selben Lauf. Der Befund ist nicht, dass `kit-test.ps1` schlecht gebaut wäre — er ist, dass „grün" auf den beiden Bahnen **verschieden viel bedeutet** und niemand das beim Lesen sieht | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Nicht als „alles portieren" anzugehen: Stufe 9 (Regel-Inventar) ist reines Python und läuft dort ohnehin, Stufe 10 prüft eine Bash-Routine. **Die Reihenfolge folgt der Wirkung:** zuerst Stufe 6 auf den Umfang der bash-Fassung bringen (dort saß `BL-136`/`BL-144`), dann Stufe 8 (die einbahnige Ablage ist auf Windows der **Normalfall**, und `BL-129`s Zusicherung gilt dort bisher unbelegt), dann Stufe 5. **Die Gegenprobe, die es erst gültig macht:** Ein absichtlich zurückgedrehter Fix muss den pwsh-Selbsttest **rot** machen — genau das hat er bei `BL-136` nicht getan. Solange das offen ist, gilt: **Ein Fix an gemeinsamem Code ist erst nachgewiesen, wenn `kit-test.sh` gelaufen ist**, nicht wenn `kit-test.ps1` grün meldet |

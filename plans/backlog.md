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
| BL-167 | **Die Regel „Zentrale Werte gehoeren gegengeprobt, nicht gegrept" nennt keinen Zeitpunkt — und ohne ihn prueft die Gegenprobe zuverlaessig nichts.** Die Regel verlangt, dass eine Stufe, die einen zentralen Wert aendert, ihn probeweise auf zwei fremde Werte setzt, die Suite laufen laesst und nachweislich zuruecksetzt. „Aendert eine Stufe einen zentralen Wert" trifft auf die **einfuehrende** Stufe zu — genau dort ist die Probe aber wertlos, solange kein anderer Code den Wert liest. Im Feld stand die Probe in der Stufe, die eine Wertabbildung anlegte; ihr einziger Verbraucher entstand **drei Stufen spaeter**. Die Probe meldete **2** rote Stellen — deckungsgleich mit dem, was `grep` ohnehin fand — und der Commit-Text las sich wie eine bestandene Pruefung. Im Closeout nachgeholt, nachdem der Verbraucher existierte: dieselbe Verstellung macht **11** Tests rot; allein zwei der fuenf Werte zu verstellen macht **10** Tests in **7** Dateien rot, darunter **drei**, die die Textsuche gar nicht nennt. **Der Fehlermodus ist der, den die Regel selbst verhindern soll, eine Ebene hoeher:** eine Verifikation, die zuverlaessig gruen ist, ohne etwas geprueft zu haben — und die ihre eigene Wirkungslosigkeit als Bestaetigung ausgibt. **Er trifft ausgerechnet den sauberen Stufenschnitt:** Wer Logik und Verbraucher trennt — was das Kit an anderer Stelle empfiehlt —, legt die Probe fast zwangslaeufig in die falsche Stufe. Je besser geschnitten, desto verlaesslicher greift der Fehler | `Feld E`, 2026-08-24, Closeout K2. Volltext: [`plans/meldungen/2026-08-24-gegenprobe-zentraler-werte-gehoert-in-die-verbrauchende-stuf.md`](meldungen/2026-08-24-gegenprobe-zentraler-werte-gehoert-in-die-verbrauchende-stuf.md). Aufgefallen nur, weil der Loop die Zahl **2** ehrlich in den Commit-Text geschrieben hat; ohne diese Angabe waere die leere Probe nicht unterscheidbar von einer bestandenen | **offen.** **(1)** Die Regel um den Zeitpunkt ergaenzen: Die Gegenprobe gehoert in die Stufe, in der der Wert einen **Verbraucher** hat; fallen beide auseinander, wandert sie in die spaetere Stufe, und die einfuehrende verweist darauf. **(2)** Wichtiger, weil maschinell pruefbar und ohne Planvorsatz wirksam: Ergibt die Probe **weniger oder gleich viele** rote Stellen, als die Textsuche Fundstellen nennt, hat sie nichts geprueft — das ist kein bestandenes Ergebnis, sondern der Hinweis, dass sie zu frueh lief. **(3)** Das Architekten-Briefing zieht beim Stufenschnitt nach. **Gegenprobe:** eine Kaskade, die einen zentralen Wert einfuehrt und erst spaeter verbraucht — die Probe in der einfuehrenden Stufe muss als *zu frueh* auffallen, nicht als *bestanden* |
| BL-165 | **Die Sitzungs-Invariante lautet „genau EINE Buchung je Sitzung — nicht null und nicht zwei", und `TEAM.md` nennt keine der beiden Haelften.** `BL-116` hat die eine Haelfte geloest: Zwei Closeouts in derselben Sitzung messen dasselbe Transkript zweimal, der erste Betrag wandert ein zweites Mal ins Ledger. Diese Regel steht heute in `geteilt/prompts/rolle-architekt.md`, in `doku/regel-inventar.md`, in `test_bl116_ein_closeout_je_sitzung.py` und im Backlog-Archiv — also ausschliesslich an Orten, die der **Mensch** nicht liest. In `bootstrap/TEAM.md`, der Bedienanleitung, die mitinstalliert wird, kommt der Satz **nicht vor** (`grep -c 'Closeout je Sitzung'` → 0). **Die andere Haelfte ist nirgends dokumentiert, auch nicht im Briefing.** `transkripte_aus_projekt()` gibt genau **eine** Datei zurueck: `return [max(dateien, key=os.path.getmtime)]` — das zuletzt geaenderte Transkript, also die laufende Sitzung. Daraus folgt zwingend: Eine Sitzung, die **nicht** bucht, wird **nie** gemessen. Ihr Transkript ist eine eigene `.jsonl`, die keine spaetere Messung je anfasst; die Kosten sind nicht „spaeter faellig", sondern dauerhaft weg. Dieser Umstand steht in **keiner** `.md` des Kits — nur im Code und in dessen Docstring. `TEAM.md` sagt lediglich „Ohne diesen Schritt bleibt seine Sitzung strukturell unerfasst", und zwar im Zusammenhang **des Closeouts**, nicht als Regel fuer jede Sitzung; dass es unnachholbar ist, sagt der Satz nicht. **Der Kit-eigene Rat erzeugt die Luecke, die er nicht benennt:** Das Architekten-Briefing schliesst mit „nach einem gebuchten Closeout eine **neue** Sitzung fuer die naechste Kaskade". Befolgt man das, plant man K(N+1) in einer Sitzung, die selbst nichts bucht — und beim Closeout von K(N+1) wird nur **dessen** Transkript gemessen. Die gesamte Planungsarbeit einer Kaskade faellt damit strukturell aus dem Ledger. Das wiegt schwer, weil `TEAM.md` die Groessenordnung selbst nennt: „im Ursprungsprojekt waren das real rund 16 USD pro Session." **Beide Haelften zusammen ergeben erst die Regel**; einzeln fuehrt jede in einen Fehler, und sie zeigen in entgegengesetzte Richtungen — wer nur `BL-116` kennt, bucht aus Vorsicht seltener und verliert Sitzungen | `Feld E`, 2026-08-24. Der Stakeholder — Owner des Kits und seit mehreren Kaskaden im Betrieb — fragte, ob er nach jedem Kaskadenabschluss eine neue Sitzung starten soll, und kannte die Regel nicht. Das ist der Beleg: Sie steht an vier Orten, aber an keinem, den ein Anwender im Betrieb aufschlaegt. Die zweite Haelfte war auch dem Architekten neu; sie liess sich nur durch Lesen von `kosten.py` feststellen | **offen.** **(1)** Die Invariante in `bootstrap/TEAM.md` in den Kosten-Abschnitt aufnehmen, in EINEM Satz und in beide Richtungen: *Jede interaktive Sitzung bucht genau einmal — zweimal zaehlt doppelt, keinmal ist unwiederbringlich verloren.* Der Abschnitt erklaert `--addieren` bereits; ihm fehlt nur der Grund, warum man es ueberhaupt braucht. **(2)** Den Messumfang offenlegen: dass `sitzung-messen` das zuletzt geaenderte Transkript liest und damit immer nur die aktuelle Sitzung — ein Anwender kann das sonst nicht wissen und vermutet naheliegenderweise eine Gesamtmessung. **(3)** Das Architekten-Briefing um den Fall ergaenzen, den sein eigener Rat erzeugt: Eine Planungssitzung ohne Closeout bucht ihre Kosten selbst, mit `--kaskade <N+1>`. **Gegenprobe:** Zwei aufeinanderfolgende Sitzungen an einem Projekt, von denen die erste bucht und die zweite nicht — die Summe im Ledger muss danach nachweislich kleiner sein als die Summe beider gemessener Transkripte. Genau diese Differenz ist heute unsichtbar |
| BL-164 | **`TEAM.md` verweist den Anwender auf `team-auth-setup.sh` — ein Skript, das der Installer nicht ins Projekt legt und dessen Fundort die Zeile nicht nennt.** Die Stelle lautet: Der Key gehoert „nie per `export` in `.bashrc` & Co., sondern in `~/.config/claude-team/api-key` (eine Zeile, `chmod 600`) — dorthin legt ihn `team-auth-setup.sh`." Im installierten Projekt gibt es diese Datei nicht: `ls team-auth-setup.sh` schlaegt fehl, die Entrypoints in der Wurzel sind `vollautomatik/halbautomatik/team-status/team-test/ralph/frank/axel/harry/marv/kit-melden`. Der zweite im Skriptkopf genannte Ort — `~/.claude/scripts/team-auth-setup.sh`, angelegt „wenn `kit-einrichten.sh` die Verknuepfung angelegt hat" — existierte auf der Maschine ebenfalls nicht. Das Skript liegt ausschliesslich im Kit-Repo unter `bash/scripts/team-auth-setup.sh`, und **dieser Pfad steht in `TEAM.md` nirgends**; `TEAM.md` ist aber genau das Dokument, das mitinstalliert wird und dem Stakeholder im Projekt als Bedienanleitung dient. **Warum das mehr ist als eine fehlende Pfadangabe:** Die Zeile steht im Zusammenhang mit der teuersten dokumentierten Auth-Lehre des Kits — dem `~13,8-USD-Leerlauf-Lauf`, der vollstaendig ueber API lief, weil ein `.bashrc`-Key das Abo-first-Design still aushebelte. Die Regel „nicht in `.bashrc`, sondern in die Datei" ist also gut belegt; das genannte **Mittel**, sie richtig umzusetzen, ist im Projekt nicht auffindbar. Wer den Key hinterlegen will und das Skript nicht findet, greift mit einiger Wahrscheinlichkeit zu genau dem `export`, vor dem der Absatz zwei Zeilen darueber warnt — der Verweis leitet damit ins Gegenteil seiner Absicht. Erschwerend: Ohne hinterlegten Key ist zusaetzlich der Pausen-Exit `42` unerreichbar (`BL-163`), das Mittel ist also wichtiger, als der Absatz vermuten laesst | `Feld E`, 2026-08-24. Der Stakeholder fragte, wie er den API-Key hinterlegt; die Antwort aus `TEAM.md` liess sich nicht befolgen. Gefunden wurde das Skript erst durch ein `find` ueber das Kit-Repo — was nur moeglich war, weil der Stakeholder zufaellig auch dessen Owner ist und es lokal liegen hat. Ein gewoehnliches Zielprojekt hat das Kit-Repo nicht auf der Platte | **offen, klein, aber mit Wirkung.** Drei Wege, sie schliessen sich nicht aus. **(1)** Das Skript mitinstallieren — es ist als „EIN BEISPIEL, keine Kit-Mechanik" gekennzeichnet, was gegen die Wurzel spricht, aber nicht gegen `team/scripts/`. **(2)** Falls es bewusst nicht mitkommt: In `TEAM.md` den vollstaendigen Weg nennen, samt der Voraussetzung, dass das Kit-Repo lokal vorliegt — und den **Handweg** als gleichwertige Alternative danebenstellen, denn er ist drei Zeilen lang (`install -m 600 -D /dev/null …`, `read -rs`, `chmod`). Ein Dokument, das ein Werkzeug nennt, das der Leser nicht hat, muss den Weg ohne dieses Werkzeug zeigen. **(3)** `TEAM_KIT_PFAD` steht seit `BL-153` ohnehin in `team.config.sh` — die Zeile koennte den Pfad daraus ableiten statt ihn zu verschweigen. **Gegenprobe:** In einer frischen Installation muss jeder in `TEAM.md` genannte Befehl entweder vorhanden oder mit vollstaendigem Fundort versehen sein; das ist maschinell pruefbar und faellt in dieselbe Familie wie `BL-17` (Doku gegen Verifikation) |
| BL-174 | **In einer reinen Abo-Installation ist der Pausen-Exit 42 unerreichbar: Der fehlende API-Schluessel bricht `team_claude()` ab, BEVOR die 429-Behandlung laeuft.** Der Fallback in `team_claude()` lautet `if [ "$fehler" -eq 1 ] && [ "$AUTH_MODE" = "abo" ]; then AUTH_MODE=api; team_resolve_auth_mode \|\| return 1; …`. `team_resolve_auth_mode` gibt fuer `AUTH_MODE=api` ohne `ANTHROPIC_API_KEY` und ohne lesbares `~/.config/claude-team/api-key` eine `1` zurueck — also verlaesst das `\|\| return 1` die Funktion **sofort**. Die gesamte 429-Sonderbehandlung steht im Quelltext **darunter** und wird nie erreicht. **Folge:** Ein Session-Limit — die Fehlerklasse, fuer die `BL-20`/`BL-25` eigens den Exit `42` eingefuehrt haben („weder ein sauberer Erfolg noch ein echter Fehler, sondern eine eigene, klar benannte Klasse") — kommt in einer Abo-only-Installation als **Exit 1** heraus: „ECHTER Fehler, Mensch gefragt". Kein Warten bis zum Reset, kein Pausen-Signal, keine der drei dokumentierten Zusicherungen (kein State-Fortschritt, kein Fehlversuchs-Zaehler, sauberes Wiederaufnehmen). **Das widerspricht der ausgelieferten Regel**, die den API-Fallback als vorhanden voraussetzt: „Loop-Rollen starten im Abomodus; scheitert ein Aufruf (Timeout/Limit/Fehler), folgt **ein** aufruf-lokaler API-Retry, danach wieder Abo." Ein Projekt ohne Schluessel hat diesen Retry nicht — und verliert damit **zusaetzlich** die 429-Mechanik, die logisch gar nichts mit Auth zu tun hat. **Warum das gerade die Abo-Installation trifft, also den empfohlenen Normalfall:** Seit dem Entscheid „keine Rolle ist fest `api`, auch Axel und der Architekt laufen Abo-first" ist eine Installation ganz ohne API-Schluessel eine voll unterstuetzte Lage. Genau dort ist der Airbag ausgebaut, und zwar unsichtbar: Der Fehler zeigt sich erst nach Stunden Laufzeit, wenn das Kontingent voll ist — an der teuersten Stelle | `Feld E`, 2026-08-24, beim Pruefen der Anmeldelage vor dem ersten Lauf gefunden. Kein Lauf noetig: Die Kette `\|\| return 1` steht vor dem 429-Block, das ist am Quelltext ablesbar. Anlass war die Frage des Stakeholders, ob die CLI ueberhaupt angemeldet sei — Abo ja (`subscriptionType: max`), API-Schluessel nirgends. Dieselbe Sitzung hatte zuvor `BL-162` geliefert; beide Male war die Ursache, dass ein **fehlendes Mittel** in eine Fehlerklasse gepresst wird, in die es nicht gehoert | **offen.** Die Reihenfolge umdrehen, nicht den Fallback erzwingen: Schlaegt der Abo-Aufruf fehl, **zuerst** pruefen, ob ueberhaupt ein API-Weg zur Verfuegung steht — steht keiner, den Fallback ueberspringen und **regulaer in die 429-Behandlung laufen**, statt die Funktion zu verlassen. Ein fehlender Schluessel ist in einer Abo-Installation kein Fehler, sondern der erwartete Zustand; er darf den Ablauf nicht abschneiden. Zweitens gehoert der Umstand in die Regeldatei: Der Satz ueber den aufruf-lokalen API-Retry beschreibt heute eine Ausstattung, die nicht jede Installation hat. **Gegenprobe, die den Fix erst gueltig macht:** Ein Lauf ohne jeden API-Schluessel, dessen Abo-Aufruf einen 429 liefert, muss mit **Exit 42** enden und den State unveraendert lassen — heute endet er mit Exit 1. Ein Stub, der ein 429-Ergebnis in das Log schreibt, reicht dafuer; ein echtes Limit muss niemand abwarten |
| BL-173 | **Die Agenten-CLI wird als blanker Kommandoname aufgerufen, ohne Override — und wenn sie fehlt, meldet das Kit einen Auth-Fehler statt des wahren Grundes.** `lib.sh` ruft in `team_claude()` schlicht `claude -p …` auf. Es gibt dafür **keine** Konfigurationsvariable, weder in `bootstrap/team.config.sh` noch in der Umgebung. **Das Kit hat diese Lehre für Python bereits gezogen und für die CLI nicht angewandt:** `BL-131` hat `TEAM_PYTHON` eingeführt, mit der Begründung „Wie der Interpreter **heißt**, entscheidet die Maschine, nicht diese Datei" — der Installer trägt ein, was er auf **dieser** Maschine gefunden hat. Für die Agenten-CLI gilt dasselbe Argument, und zwar stärker: Claude Code wird legitim **IDE-gebündelt** ausgeliefert (VS Code / VSCodium-Erweiterung, Binary unter `resources/native-binary/claude`), und eine Maschine kann eine vollständig eingerichtete, angemeldete Installation haben, ohne dass `claude` in irgendeinem `PATH` auflösbar ist. Genau diese Lage lag in `Feld E` vor: `~/.claude/.credentials.json` vorhanden, Abo aktiv, Erweiterung lief — und `command -v claude` leer. **Die zweite Hälfte wiegt schwerer als die erste, weil sie in die Irre führt.** Der Ablauf beim Start der ersten Vollautomatik: `claude: command not found` (eine Zeile, scrollt vorbei) → `team_bewerte_ergebnis` sieht ein 0-Byte-Log und schreibt einen **Ersatzzettel** für einen Aufruf, der nie stattgefunden hat („die Dauer ist belegt, die Kosten sind UNBEKANNT") → der Abo-Fehler löst planmäßig den **API-Fallback** aus → und der bricht mit der Meldung ab, die stehen bleibt und die der Mensch liest: `FEHLER: AUTH_MODE=api, aber weder ANTHROPIC_API_KEY gesetzt noch …/api-key lesbar.` **Diagnostiziert wird ein Auth-Problem; vorliegt ein PATH-Problem.** Wer dieser Meldung folgt, besorgt einen API-Schlüssel und hinterlegt ihn — und dann scheitert der Lauf ein zweites Mal an derselben Stelle, weil auch der API-Weg dasselbe `claude` aufruft. Eine fehlende Programmdatei ist **keine** Fehlerklasse, die ein Auth-Fallback heilen kann | `Feld E`, 2026-08-24, beim allerersten `./vollautomatik.sh`-Aufruf des Projekts. Der Lauf starb in Phase 1 vor der ersten Stufe; nichts gebaut, nichts bezahlt, State unverändert — der Fehler ist also billig, aber er trifft **jede** Erstinbetriebnahme auf einer Maschine ohne Standalone-CLI, und das ist bei IDE-Nutzern der Normalfall, nicht die Ausnahme. Aufgelöst wurde er erst durch das Absuchen der laufenden Prozesse (`ps -eo args`), weil weder `$HOME` noch `/usr/local/bin` noch `npm root -g` etwas hergaben | **offen.** Zwei Hälften, und die zweite ist die wichtigere. **(1) Ein `TEAM_CLAUDE_BIN` genau nach dem Muster von `TEAM_PYTHON`**: Default `claude`, in `bootstrap/team.config.sh` mit demselben Kommentar-Duktus, vom Installer mit dem gefüllt, was er auf dieser Maschine wirklich gefunden hat — und die Suche kennt dann auch den IDE-Ort. Damit läuft das Team auf einer Maschine, auf der es heute gar nicht anspringt, ohne dass jemand am `PATH` dreht. **(2) Die Fehlerklasse trennen:** `team_claude()` prüft **vor** dem ersten Aufruf, ob die CLI überhaupt auflösbar ist (`command -v`), und bricht mit einer Meldung ab, die den wahren Grund nennt und den Fundort vorschlägt. Kein API-Fallback, kein Ersatzzettel, kein Fehlversuchs-Zähler — nichts davon passt auf „das Programm gibt es nicht". Das ist dieselbe Erwägung wie bei Exit `42`/`43`: eine eigene Fehlerklasse, die man **benennt**, statt sie in eine bestehende zu pressen. **Gegenprobe, die den Fix erst gültig macht:** Ein Lauf mit `PATH` ohne `claude` muss genau eine Meldung erzeugen — „CLI nicht gefunden" — und **keine** über einen fehlenden API-Schlüssel; und ein Lauf mit gesetztem `TEAM_CLAUDE_BIN` auf einen Pfad außerhalb des `PATH` muss normal durchlaufen |
| BL-169 | **`src/` + `tests/` als ausgelieferte Ordner-Defaults machen Reproducer-Tests in jedem Stack mit paketgebundener Testsuche unausführbar — und zwar stumm.** `bootstrap/team.config.sh` belegt `TEAM_PRODUKTIVCODE` mit `src/` und `TEAM_TEST_ORDNER` mit `tests/` vor. Das trägt, solange der Testläufer die Dateien am **Pfad** findet (pytest). Es trägt **nicht**, sobald er sie am **Paket** findet: Dart/Flutter sammelt ausschließlich innerhalb des Pakets und ausschließlich unterhalb von `test/`; liegt das Paket unter `src/`, liegt der vom Kit vorgesehene Testordner **außerhalb** davon. Dieselbe Bauart bei Cargo (`tests/` relativ zu `Cargo.toml`), Go (Paketverzeichnis) und Gradle (`src/test/`). **Die zweite Hälfte ist vom Ordner unabhängig und wiegt schwerer:** Der Läufer nimmt nur Dateien mit einem bestimmten Namensmuster — `_test.dart` bei Dart, `_test.go` bei Go. Die Konvention des Kits lautet `tests/test_hm<nr>_<stichwort>.py` und steht wörtlich in `bootstrap/CLAUDE.md.vorlage` (Fund-Format **und** der Absatz zur Benennung nach der Fund-Nummer), in `bootstrap/beutebuch.md` und in `geteilt/prompts/rolle-harry.md`/`rolle-marv.md`. Buchstabengetreu auf Dart übertragen ergibt das `test_hm36_foo.dart` — einen Namen, den der Läufer ignoriert. **Folge in beiden Hälften identisch:** Franks regelkonform abgelegter Reproducer wird nie ausgeführt, der Smoke-Test bleibt grün, das Beutebuch zeigt einen Fund mit Reproducer, geprüft wird nichts. Das ist derselbe Schaden wie `BL-15` (Backtick-Regel) und `BL-28` (`strict`-Marker), nur eine Ebene tiefer: Dort war der Test da und stumm markiert, hier wird er gar nicht erst gefunden. **Nicht betroffen ist der Extraktor:** `DATEI_RE` in `team/tools/beutebuch.py` akzeptiert jede Endung und hat den umgestellten Dart-Pfad im Lauf korrekt als `test/hm6_stichwort_test.dart` erkannt — der Substanz-Anker trägt, allein die Vorgabewerte und Beispiele tragen nicht | `Feld E`, 2026-08-23, vom Architekten beim Aushärten der **ersten** Kaskade gefunden — durch Lesen der Kopplung zwischen Konfiguration und Testläufer, **bevor** ein Lauf startete. Dasselbe Zeitfenster wie `BL-149`: Sobald ein Projekt seine Ordner einmal richtig gesetzt hat, ist der Default für immer unsichtbar, und ein laufendes Projekt kann den Fehler gar nicht mehr erleben. Getroffen wird ausschließlich der Erstlauf | **offen.** Zwei Wege, und sie fangen Verschiedenes. **(1) Der Installer leitet ab statt vorzugeben:** Er kennt den Stack bereits aus dem Aufnahme-Interview — aus ihm folgen Produktivcode-Ordner, Testordner **und** das Namensmuster des Reproducers. Für Dart/Flutter `lib/` + `test/` + `<name>_test.dart`, für Cargo `src/` + `tests/`, für Go das Paketverzeichnis + `_test.go`. **(2) Wo der Stack unbekannt bleibt**, gehört die Kopplung in den Kommentar von `bootstrap/team.config.sh`, in einem Satz: *Der Testordner muss dort liegen, wo der Läufer sucht, und der Dateiname so heißen, dass er ihn nimmt.* Beides zusammen, nicht eines davon — (1) hilft dem erkannten Stack, (2) dem unerkannten. **Die Gegenprobe, die den Fix erst gültig macht:** Eine frische Installation für einen paketgebundenen Stack, in der die ausgelieferte `Reproducer-Test`-Zeile ausgefüllt, die Datei angelegt und der **konfigurierte Smoke-Test** gefahren wird — er muss diese Datei nachweislich **ausführen**. `test_bl15_reproducer_zeile_ankertauglich.py` prüft heute, ob `DATEI_RE` den Pfad sieht; ob der Testläufer ihn sieht, prüft niemand, und genau dort sitzt der Fund |
| BL-170 | **`{{SMOKE_TEST}}` steht auch in `geteilt/prompts/rolle-ralph.md` — der vierten Einsetzstelle, die der Abtrag von `BL-149` nicht mitgezählt hat. Sie ist die einzige, die kein Mensch liest.** `BL-149` ist sauber abgetragen, und der Entscheid dort ist richtig: `{{SMOKE_TEST}}` bleibt der **Prosa**-Platzhalter und darf den TODO-Satz tragen, `{{SMOKE_TEST_KONFIG}}` bleibt leer, dazu normalisiert `lib.sh` (Zeilen 43–44) einen mit `TODO` beginnenden Wert **einmal beim Laden** zu leer. Der Archiveintrag benennt die Prosa-Ziele ausdrücklich — `CLAUDE.md`, `TEAM.md` und die Skizzen-Vorlage, „dort ist er richtig". Eine vierte Stelle trägt denselben Platzhalter und kommt in dieser Aufzählung nicht vor: `geteilt/prompts/rolle-ralph.md:14`, die Zeile mit dem Smoke-Test in Ralphs eisernen Grenzen. **Warum diese Stelle anders ist als die drei anderen:** `CLAUDE.md` und `TEAM.md` sind Dokumente für einen Menschen, der einen TODO-Satz als TODO liest. Ein Rollen-Briefing ist die Arbeitsanweisung einer ausführenden Instanz; der Satz steht dort **in Backticks** und **unter den eisernen Grenzen** — also in Auszeichnung und an der Position, an der sonst ein ausführbarer Befehl steht. **Die `TODO`-Weiche schützt ihn nicht:** Sie normalisiert die Umgebungsvariable beim Laden der Bibliothek; das Briefing ist eine statische Datei, in die der Installer den Text eingesetzt hat, und `team_briefing()` gibt sie unverändert aus. **Das Ergebnis ist ein Widerspruch im Prompt derselben Stufe:** `SMOKE_ZEILE` sagt korrekt, es sei kein Smoke-Test konfiguriert und der Schritt entfalle — das Briefing daneben nennt einen Smoke-Test, der wie ein Befehl aussieht. Was eine Instanz daraus macht, ist nicht vorhersagbar, und es trifft wie `BL-149` ausschließlich die erste Kaskade eines Projekts | `Feld E`, 2026-08-23, beim Aushärten der ersten Kaskade. Aufgefallen nicht am Prompt, sondern beim Nachschlagen, **warum** der Satz noch im Projekt steht, obwohl `BL-149` als abgetragen geführt ist. Die Antwort stand im Archiveintrag selbst: Er zählt drei Ziele auf, `install.sh` bedient vier. Eine Aufzählung, die vollständig aussieht, ist schwerer zu prüfen als eine, die es nicht behauptet | **offen, klein.** Der Fix ist eine Weiche wie bei `{{SMOKE_TEST_KONFIG}}`, nicht ein weiterer Platzhalter: Ist kein Smoke-Test konfiguriert, gehört ins Briefing ein Satz, der erkennbar **kein Befehl** ist und **nicht in Backticks** steht — etwa, dass noch keiner konfiguriert sei und sein Bau Stufe 1 dieser Kaskade ist. Backticks sind die Auszeichnung, an der eine Instanz einen ausführbaren Befehl erkennt; sie um einen Platzhalter zu legen ist dieselbe Klasse Fehler wie ein nicht-leerer Default. **Die Gegenprobe:** In einer frischen Installation ohne gesetzten Smoke-Test darf `team_briefing ralph` **keinen** Backtick-Ausdruck enthalten, der mit `TODO` beginnt. `test_bl149_platzhalter_ist_kein_befehl.py` ist der Ort, an dem dieser Fall danebenpasst: Er fährt heute `SMOKE_ZEILE` und `team_allowed_tools`; die dritte Verbrauchsstelle ist das Briefing |
| BL-171 | **`kit-test.sh` kann in einem Nicht-Python-Zielprojekt nicht grün werden — zwei Zusicherungen prüfen die Sprache statt der Sache.** Nachdem `Feld E` seine Reproducer-Konvention vom Python- auf das Dart-Format gezogen hatte (`BL-158`), meldete `./team-test.sh` dort **sieben** Fehlschläge, keinen davon an der Eigenschaft, die der jeweilige Test absichern soll. **(1) `geteilt/tests/test_bl15_reproducer_zeile_ankertauglich.py:153`** — der Test prüft zuerst das Richtige, nämlich ob `DATEI_RE` in der ausgefüllten `Reproducer-Test`-Zeile überhaupt einen Pfad findet. Dieser Teil war **grün**. Erst die Folgezeile bricht: Sie verlangt zusätzlich, dass der extrahierte Pfad auf `.py` endet — der Ordner kommt aus der Konfiguration, die Endung steht als Literal daneben. Vier Fälle (Beutebuch-Vorlage, Regeldatei, Briefing Harry, Briefing Marv). **(2) `geteilt/tests/test_bl28_reproducer_wirksam.py:211`** — `test_briefings_verlangen_strict` verlangt den **pytest**-Marker `strict=True` wörtlich in der Regeldatei und in zwei Briefings, drei Fälle. In Dart gibt es dazu keine Entsprechung: Das Test-Paket kennt nur `skip:`, und `skip:` ist in beide Richtungen stumm, also genau der Marker, den `BL-28` verbietet. Die einzige sichere Regel für Dart lautet deshalb, dass das Red Team einen roten Reproducer **gar nicht erst anlegt** und nur den Dateinamen reserviert, während Frank die Testdatei mit dem Fix schreibt — das ist **strenger** als die Kit-Regel und fällt trotzdem als Verstoß durch. **Warum ein roter Sockel teurer ist, als er aussieht:** `TEAM.md` nennt `./team-test.sh` als den Befehl, mit dem man das Team selbst prüft. Sieben dauerhaft rote Fälle machen die Suite als Signal wertlos — der nächste echte Regressionsfund geht darin unter, und niemand kann ohne Nachlesen sagen, welcher Fehlschlag neu ist. **Der naheliegende Ausweg ist der falsche und deshalb die eigentliche Gefahr:** Ein Projekt biegt seine Regel auf pytest-Formulierungen zurück, damit die Suite grün wird. Dann steht in seiner Regeldatei ein `strict=True`, das es in seiner Sprache nicht gibt — grüne Suite, fiktive Regel. Das ist die Bauart von `BL-17`, angewandt auf die Selbstprüfung des Kits | `Feld E`, 2026-08-23, beim Aushärten der ersten Kaskade. Die sieben Fälle wurden dort bewusst **nicht** gepatcht: an den Kit-Tests vorbeizureparieren hieße, die Verifikation abzuschaffen statt das Problem zu lösen. Sie stehen im Projekt-Backlog als bekannter Sockel, damit ein späterer Lauf neue Fehlschläge von diesen unterscheiden kann | **offen.** Beide Zusicherungen an die konfigurierte Sprache binden statt an Python. **(1)** Die erwartete Endung aus derselben Quelle ziehen wie `TEST_ORDNER` — das Namensmuster des Reproducers ist ohnehin der Wert, den `BL-158` in die Konfiguration holen will; die beiden Einträge teilen sich diesen Fix. **(2)** Statt des Literals `strict=True` prüfen, dass die Regeldatei **überhaupt eine** Aussage darüber trifft, wie ein roter Reproducer zu behandeln ist — die Zusicherung von `BL-28` ist „es gibt keine stummen Ausgänge", nicht „es steht pytest da". Wo das Kit die Sprache nicht kennt, ist ein sichtbarer Übersprung mit Begründung ehrlicher als ein Fehlschlag; die Doppelbahn-Quote führt dafür bereits die passende Bauform. **Gegenprobe:** Dieselbe Suite in einer Installation mit nicht-Python-Konfiguration fahren — sie muss grün sein, **und** ein absichtlich stumm markierter Reproducer muss sie rot machen |
| BL-172 | **`TEAM_REDTEAM_FOCUS` verdrängt den projektspezifischen Grundauftrag, statt ihn zu ergänzen — und weil die Regel einen Fokus bei JEDER Kaskade verlangt, sind `TEAM_REDTEAM_AUFTRAG_*` strukturell tot.** `bash/entry/harry.sh:23` und `bash/entry/marv.sh:21` setzen `AUFTRAG` über die Kette Fokus → Grundauftrag → stackneutraler Default; `bash/redteam.sh:80` baut `SCOPE_LINE` nach demselben Muster. Ein gesetzter Fokus **ersetzt** den Grundauftrag also, er tritt nicht neben ihn. Das kollidiert mit einer normativen Aussage der Regeldatei: Der Fokus wird bei **jeder** Kaskade gesetzt, auch bei reinen Produktivcode-Läufen, und er hat kein Verfallsdatum. Wird er pflichtgemäß immer gesetzt, greift der Grundauftrag **nie** — er wirkt allein in dem Lauf, den es laut Regel nicht geben soll. **Warum das nicht bloß Kosmetik ist:** Der Kommentar bei `TEAM_REDTEAM_AUFTRAG_*` in `bootstrap/team.config.sh` empfiehlt das Ausfüllen ausdrücklich und belegt es mit einem Feldfall — derselbe Sweep über denselben Code fand mit passendem Auftrag einen Fund, den er ohne ihn nicht sah. Und er grenzt die Werte vom Fokus ab: nicht zu verwechseln, der Fokus gelte für **eine** Kaskade. Genau diese Abgrenzung setzt der Code nicht um. Es sind nicht zwei Achsen, sondern **eine mit Vorrang**. Dabei sollen die beiden Werte gerade tragen, was sich **nicht** pro Kaskade ändert — etwa, dass in diesem Projekt personenbezogene Daten Minderjähriger in einer lokalen Datenbank liegen —, und der Fokus das, was diese eine Kaskade berührt. Beides zugleich zu brauchen ist der Normalfall, nicht die Ausnahme. **Der Schaden ist leise:** Der Sweep läuft, findet etwas, und niemand sieht, dass die dauerhafte Kenntnis der Angriffsfläche in diesem Lauf gar nicht im Prompt stand — dieselbe Klasse wie `BL-31` (ein Fokus, der stillschweigend das Falsche prüft), nur mit umgekehrtem Vorzeichen | `Feld E`, 2026-08-23, beim Formulieren der Scharfschalt-Sequenz der ersten Kaskade. Aufgefallen unmittelbar nach dem Ausfüllen der beiden Grundauftrags-Werte: Beim Nachlesen, wie der Fokus übergeben wird, stand die Verdrängung in der Variablen-Kette. Ohne diesen Blick wären beide Werte ab dem ersten Lauf wirkungslos gewesen, ohne dass irgendetwas darauf hingewiesen hätte | **offen.** Fokus und Grundauftrag **verketten** statt sie gegeneinander auszuspielen: der Grundauftrag als stehender Rahmen, der Fokus als Schwerpunkt dieses Laufs — im Prompt genügt eine Reihenfolge. **Zu bedenken ist dabei, dass `TEAM_REDTEAM_FOCUS` zwei Dinge steuert, die auseinanderfallen:** `SCOPE_LINE` (**wo** geprüft wird — dort ist Ersetzen richtig, ein Fokus schneidet den Umfang bewusst zu) und `AUFTRAG` (**worauf** geachtet wird — dort ist Ersetzen falsch). Der Fix gehört an die zweite Stelle, nicht an beide. **Mindestens** aber gehört die Verdrängung in den Kommentar von `bootstrap/team.config.sh`: Dann weiß ein Projekt wenigstens, dass es seine Angriffsfläche in jeden Fokus-String hineinschreiben muss — der Behelf, den `Feld E` für seine erste Kaskade gewählt hat. **Gegenprobe:** Ein Lauf mit gesetztem Fokus **und** gesetztem Grundauftrag, in dem der Prompt beides nachweislich enthält |
| BL-145 | **`kit-test.ps1` fährt 6 von 11 Schritten und 15 von 127 Einzelprüfungen — und genau diese Lücke hat `BL-136` durchgelassen.** Der Fix zu `BL-136` (`.gitattributes` ins Zielprojekt) ist als „kit-test.ps1 alle 6 Schritte grün (EXIT 0)" nachgewiesen worden. Er war es auch — nur prüft `kit-test.ps1` den Fall gar nicht, an dem er zerbrach: Die `.gitignore`/`.gitattributes`-Zusicherungen des Update-Pfads leben in Stufe 6 von `kit-test.sh` (dort inzwischen 30 Einzelprüfungen), und der pwsh-Selbsttest hat davon eine dünne Fassung. Ergebnis: Der Selbsttest der **bash**-Bahn war rot, während der Nachweis der pwsh-Bahn grün meldete — vier Commits lang unbemerkt (`BL-144`). **Was `kit-test.ps1` gar nicht hat:** Stufe 5 (zweiter Suite-Lauf unter angepasster Konfiguration, `BL-58` — dort fällt eine falsch gesetzte Messstelle auf, die in einer frischen Installation nie auffällt), Stufe 7 (Einzug in eine gewachsene Codebasis, `BL-51`/`BL-52`), Stufe 8 (Abwahl einer Bahn und ihr Rückweg, `BL-119` — **hier liegt seit `BL-129` die Zusicherung, dass eine einbahnige Ablage grün bleibt**), Stufe 9 (Regel-Inventar gegen die Regeldatei, `A.10`/`BL-56`), Stufe 10 (Einrichtungsroutine) und Stufe 11 (Gleichstand der Installer). Die Zahl `$PruefungenSoll = 15` ist dabei selbst ein Absturzschutz und richtig gebaut — sie sichert nur einen viel kleineren Umfang ab, als ihr Name vermuten lässt | Kit, 2026-08-21 — beim Abtragen von `BL-144` als Ursache **hinter** der Ursache ausgewiesen. Gemessen, nicht geschätzt: 6 gegen 11 Schritte, 15 gegen 127 Einzelprüfungen im selben Lauf. Der Befund ist nicht, dass `kit-test.ps1` schlecht gebaut wäre — er ist, dass „grün" auf den beiden Bahnen **verschieden viel bedeutet** und niemand das beim Lesen sieht | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Nicht als „alles portieren" anzugehen: Stufe 9 (Regel-Inventar) ist reines Python und läuft dort ohnehin, Stufe 10 prüft eine Bash-Routine. **Die Reihenfolge folgt der Wirkung:** zuerst Stufe 6 auf den Umfang der bash-Fassung bringen (dort saß `BL-136`/`BL-144`), dann Stufe 8 (die einbahnige Ablage ist auf Windows der **Normalfall**, und `BL-129`s Zusicherung gilt dort bisher unbelegt), dann Stufe 5. **Die Gegenprobe, die es erst gültig macht:** Ein absichtlich zurückgedrehter Fix muss den pwsh-Selbsttest **rot** machen — genau das hat er bei `BL-136` nicht getan. Solange das offen ist, gilt: **Ein Fix an gemeinsamem Code ist erst nachgewiesen, wenn `kit-test.sh` gelaufen ist**, nicht wenn `kit-test.ps1` grün meldet |
| BL-117 | **Der Prompt-Gleichstand ist am QUELLTEXT bewiesen, nicht am LAUF — Drift in den eingesetzten Werten bliebe unsichtbar.** [`test_bl112_prompt_gleichstand.py`](../geteilt/tests/test_bl112_prompt_gleichstand.py) vergleicht die **Prosa** beider Bahnen, nachdem jede Variableneinsetzung zu einem Platzhalter geworden ist. Das trifft den Fall, für den `BL-112` geschrieben wurde (jemand schärft eine Feldlehre in nur einer Fassung nach), und es lässt genau eine Lücke: Setzen die beiden Bahnen in denselben Platzhalter **verschiedene Werte** ein — ein anders abgeleiteter Ordnername, eine Fallunterscheidung, die nur eine Seite kennt, ein `team.config.ps1`, das einen Wert anders vorbelegt —, sind die Prompts verschieden und der Test bleibt grün. Diese Hälfte kann nur ein **Lauf** zeigen | Kit, 2026-08-20 — beim Abtragen von `BL-112` ausgewiesen statt behauptet: Die Fix-Skizze dort sah den Lauf-Vergleich vor, und der braucht **beide** Shells auf **einer** Maschine. Auf der Entwicklungsmaschine ist kein `pwsh` installiert; ein blind geschriebener Test, dessen erste Ausführung auf einer fremden Maschine stattfindet, wird dort „angepasst" statt gelesen — dieselbe Erwägung, die `BL-113` teuer belegt hat (die pwsh-Bahn fiel erst auf der Zielmaschine auf) | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Bauart wie in `BL-112` skizziert: ein `claude`-Stub, der sein `-p`-Argument in eine Datei schreibt statt zu arbeiten (`Schale.claude_stub` kann das Gerüst schon), jede Rolle einmal je Bahn gefahren, die beiden Prompt-Dateien zeichenweise verglichen. **Die Ausnahmeliste ist bereits da** und wird mitbenutzt, samt ihrer Probe gegen unnötige Einträge — der Lauf-Vergleich erbt sie, statt eine zweite aufzumachen. **Gegenprobe, die ihn erst gültig macht:** ein absichtlich abweichend vorbelegter Wert in einer der beiden Konfigurationen, an dem der Test fallen muss. Solange er fehlt, gilt die Zusicherung „gleicher Prompt" ausdrücklich nur für die Prosa |
| BL-189 | **Die einzige Abhilfe, die das Kit fuer die Ausfuehrungsrichtlinie nennt, ist die eine, die gegen eine Gruppenrichtlinie nicht gewinnen kann.** `pwsh/kit-einrichten.ps1` (Zeile ~141) prueft vorbildlich den **effektiven** Wert und nennt bei `Restricted`/`AllSigned` als Abhilfe `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`; wortgleich in `doku/einrichtung.md` Abschnitt 2 (Zeile 442) und in der Fehlertabelle (Zeile 693). Die Rangfolge der Bereiche ist aber `MachinePolicy > UserPolicy > Process > CurrentUser > LocalMachine` — **`CurrentUser` ist der zweitniedrigste**. Auf einer domaenenverwalteten Maschine (GPO "Skriptausfuehrung aktivieren") setzt der Befehl seinen Bereich zwar, am effektiven Wert aendert er **nichts**, und er quittiert mit `PermissionDenied / ExecutionPolicyOverride`. Der naechste Lauf von `kit-einrichten.ps1` meldet daraufhin **exakt denselben Fehler**: Das Werkzeug sagt "tu X", X meldet rot, das Werkzeug sagt wieder "tu X". Auch `-ExecutionPolicy Bypass` am Aufruf der `.cmd`-Bahn hilft nicht — das ist Bereich `Process` und verliert ebenfalls gegen die GPO. Ausgerechnet die Diagnose-Sorgfalt, die das Kit im `:keinpwsh`-Zweig jedes `.cmd`-Aufrufers betreibt ("Das ist KEIN Fehler des Kits"), fehlt hier: Das Symptom ist richtig benannt, die Abhilfe ist auf dieser Maschine nicht ausfuehrbar, und **nichts sagt das**. **Gegenrichtung, gleicher Ursprung:** Steht die GPO auf `Unrestricted`, laeuft alles — aber der Setz-Befehl aus Abschnitt 2 wirft dieselbe rote Wand, **ohne dass irgendetwas kaputt ist**. Wer der Einrichtungsdoku folgt, bekommt dann einen Fehler beim Befolgen einer Anweisung, die er gar nicht gebraucht haette | Feld (`duke-itam-2026`), 2026-08-21. Nicht aus dem Kit-Betrieb, sondern von nebenan: Der Strippenzieher stolperte beim venv-Aktivieren ueber genau diese Meldung. **Gemessen, nicht vermutet:** `HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell` -> `EnableScripts=1`, `ExecutionPolicy=Unrestricted` (Bereich `MachinePolicy`); `Get-ExecutionPolicy -List` zeigt daneben ein wirkungsloses `Process=Bypass`. Auf einer `AllSigned`-verwalteten Maschine haette das Kit den Fund beim **ersten Kontakt** geliefert — `install.ps1` und `kit-einrichten.ps1` sind beides `.ps1` | **offen.** Kleinste Fassung, drei Teile: **(1)** `kit-einrichten.ps1` gibt bei `Restricted`/`AllSigned` zusaetzlich `Get-ExecutionPolicy -List` aus und unterscheidet zwei Faelle — steht der harte Wert in `MachinePolicy`/`UserPolicy`, lautet die Abhilfe "**das kann kein Benutzerbefehl aendern, das entscheidet die IT**", nicht `Set-ExecutionPolicy`. **(2)** Dieselbe Unterscheidung in `doku/einrichtung.md` Abschnitt 2 und als eigene Zeile in der Fehlertabelle, samt der harmlosen Gegenrichtung (`Unrestricted` per GPO: Meldung folgenlos, Zeile ueberspringen). **(3)** In Abschnitt 2 `Get-ExecutionPolicy -List` **vor** den Setz-Befehl stellen — wer schon `RemoteSigned`/`Unrestricted` hat, soll ihn gar nicht erst tippen. **Ausdruecklich NICHT aufnehmen:** einen Umgehungsweg (`-Command`-Rohr, MotW entfernen, `Unblock-File` pauschal). Auf einer verwalteten Maschine ist die Richtlinie eine **Vorgabe**, kein Hindernis; ein Kit, das sie umgeht, macht seinen Anwender zum Regelbrecher. **Gegenprobe, die den Fix erst gueltig macht:** die Fallunterscheidung in eine Funktion ziehen, die eine **Bereichsliste** entgegennimmt statt selbst zu messen, und sie mit beiden Listen fahren (harter Wert in `MachinePolicy` / harter Wert nur in `LocalMachine`) — beide Zweige nachweisbar, ohne dass der Test eine echte GPO braucht **Umzug 2026-08-26 (`BL-188`): Dieser Eintrag hiess bis dahin `BL-144`.** Dieselbe Nummer trug im Archiv seit demselben Tag (2026-08-21) ein anderer Fund — der rote bash-Selbsttest seit `BL-136`, auf der anderen Maschine vergeben. Umgezogen ist **diese** Seite, weil auf sie vier Verweise zeigen und auf die andere acht; die sonst geltende Regel „die ungepushte Seite zieht um" (`41b2ee0`) griff nicht mehr, beide waren laengst gepusht. Wer `Kit-BL-144` in einem Feldprojekt liest und die Ausfuehrungsrichtlinie meint, meint diesen Eintrag. |
| BL-183 | **`team-status --watch` steht in keiner Bedienanleitung — der einzige Live-Modus ist nur im Kommentarkopf des Skripts dokumentiert.** `TEAM.md` nennt `--budget`, `--rollen-abschluss`, `--architekt-abschluss`, `--ledger-pruefen` und beschreibt in der Werkzeugtabelle den Momentaufnahme-Modus; `--watch` (Refresh alle 5 s) kommt in **keiner** Zeile vor. Der Befund entstand aus der woertlichen Frage eines Stakeholders nach zwei Kaskaden: *„Ich sehe wieder kein Monitoring, das ist weil ich noch kein Update vom Kit herausgefahren habe, korrekt?"* — **die Vermutung war falsch, und das ist der Punkt:** Das Dashboard war die ganze Zeit installiert und lauffaehig. Es fehlte nichts, es war nur nicht auffindbar | `Feld B`, 2026-08-25. Meldung: [`plans/meldungen/2026-08-25-team-status-watch-steht-in-keiner-bedienanleitung.md`](meldungen/2026-08-25-team-status-watch-steht-in-keiner-bedienanleitung.md) | **offen** |
| BL-185 | **Ein uebersteuertes `TEAM_BUDGET_USD` verwirft die Plan-Empfehlung STILL — gemeldet wird nur die Gegenrichtung.** Der Plan empfahl `BUDGET_EMPFEHLUNG_USD=34`, der Lauf lief mit **Deckel 26** — dem Wert der Vorkaskade, der in der interaktiven Shell-Sitzung weiterlebte. Die Umgebungsvariable hat Vorrang, und das Kit meldet nur, wenn eine Empfehlung den Deckel **anhebt**, nie wenn sie verworfen wird. **Die falsche Zahl ist damit nirgends zu sehen.** Folgenlos blieb es nur, weil der Lauf mit 18,20 unter beiden Deckeln blieb; ein 8 USD zu tiefer Deckel bricht mitten in der Fixphase ab und rollt bezahlte Arbeit zurueck (`BL-32`-Muster). **Der Unterschied zur Empfehlung ist die Lebensdauer:** `BUDGET_EMPFEHLUNG_USD` haengt am Plan und altert mit ihm, `TEAM_BUDGET_USD` ist eine Umgebungsvariable ohne Verfallsdatum | `Feld B`, 2026-08-25, aufgefallen erst im K3-Closeout beim Lesen des eigenen Abschlussberichts. Meldung: [`plans/meldungen/2026-08-26-uebersteuertes-team-budget-usd-verwirft-die-architekten-empfehlung-still.md`](meldungen/2026-08-26-uebersteuertes-team-budget-usd-verwirft-die-architekten-empfehlung-still.md) | **offen** |

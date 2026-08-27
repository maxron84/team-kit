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
> NICHT in der Tabelle steht:** `BL-190` ist abgetragen und der Fix ist
> bewiesen, aber auf einer Maschine **ohne** `flock` — also genau dort, wo der
> Fund entstand. Was dort nicht laufen kann, ist die **Gegenrichtung**: Wo
> `flock` da ist, muss es weiter genommen werden, und der Fall dazu
> (`test_bl190_sperre_ohne_flock.py::test_team_lock_mit_flock_nimmt_weiter_flock`)
> **uebersprang** hier mit benanntem Grund. Dazu steht ein vollstaendiger
> `bash bash/kit-test.sh` aus; er ist seit dem 2026-08-24 nicht mehr gefahren
> worden, und **Schritt 3 war seither rot** (`BL-198`) — die README-Zahlen sind
> am 2026-08-27 gemessen nachgezogen, aber der Beleg dafuer fehlt noch. Steht
> hier und nicht im Archiv, weil das Archiv **nachgeschlagen** wird und nicht
> gelesen: Ein Rest, den nur der Eintrag kennt, den niemand mehr oeffnet, ist
> keiner.

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-199 | **Die pwsh-Bahn sieht die Sperre der bash-Bahn nicht — und seit `BL-190` gibt es diesen Fall überhaupt erst.** Beide Bahnen liegen nach einer Installation im **selben** Arbeitsbaum (`BL-126`: jeder Installer schreibt beide Konfigurationen). Die Zusicherung heisst *„eine Pipeline zur Zeit"*, nicht *„eine je Bahn"*. Seit `BL-190` sperrt die bash-Bahn ohne `flock` über `.team-loop.lock.d`; die pwsh-Bahn kennt nur `.team-loop.lock` — an **drei** Stellen: `lib.psm1` (`team_lock`, `FileStream` mit `FileShare::None`), `entry/team-status.ps1` (Zeile ~104, „Pipeline: läuft/idle") und `install.ps1` (Zeile ~1080, der `BL-10`-Schutz vor einem Update in einen laufenden Lauf hinein). Ein bash-Lauf auf einer Windows-Maschine ist für alle drei **unsichtbar**: Der Kontostand meldet *idle*, und `install.ps1 --update` legt uncommittete Dateien in `team/` ab — genau der Schaden, gegen den `BL-10` gebaut wurde. **Der naheliegende Fix trägt nicht, und das ist der eigentliche Inhalt dieses Eintrags:** Die pwsh-Seite kann die hinterlegte PID **nicht auswerten**. **Gemessen am 2026-08-27, nicht vermutet:** Eine laufende Git-Bash meldete `$$` = `15946`; `Get-Process -Id 15946` in PowerShell auf derselben Maschine, zur selben Zeit, fand **nichts**. MSYS führt einen **eigenen Prozessraum**, und seine PID ist keine Windows-PID. Ein `Get-Process`-Test würde damit **jede** gehaltene bash-Sperre als verwaist einstufen — die Zusicherung wäre nicht wiederhergestellt, sondern schriftlich abgeschafft. **Ehrlichkeitshalber:** Der umgekehrte Weg war auch vorher nicht zugesichert. `FileShare::None` wird nur von **Windows** durchgesetzt; unter Linux erzwingt .NET es nicht, und `flock` ist kooperativ. Bahnübergreifend hat die Sperre also **nie** gehalten. Neu ist nur, dass es jetzt zwei verschiedene **Artefakte** gibt und der Fall damit sichtbar wird | Kit, 2026-08-27 — beim Bauen von `BL-190` aufgefallen, als die drei bash-seitigen Aufrufstellen der Frage *„läuft gerade eine Pipeline?"* nachgezogen wurden. Der Eintrag `BL-190` schreibt ausdrücklich *„Was NICHT betroffen ist: die pwsh-Bahn (sie sperrt über einen eigenen Weg)"* — das stimmte für den **Fund** und stimmt für die **Reparatur** nicht mehr, weil sie ein zweites Sperrartefakt eingeführt hat. **Gemessen:** Der PID-Namensraum-Befund oben (`$$` = 15946 in Git-Bash, `Get-Process -Id 15946` in PowerShell leer, beide gleichzeitig auf derselben Maschine). **Nicht aus dem Feld:** Es ist kein Vorfall gemeldet, und der Fall setzt voraus, dass jemand auf einer Windows-Maschine die bash-Bahn **und** die pwsh-Bahn im selben Arbeitsbaum fährt — auf Windows ist die bash-Bahn laut Zwei-Bahnen-Tabelle die zweite Wahl. Das senkt die Wahrscheinlichkeit, nicht den Schaden | **offen.** **Die erste Frage ist nicht technisch, und sie gehört vor jede Zeile Code:** Soll *„eine Pipeline zur Zeit"* **bahnübergreifend** gelten? Bisher tut sie es nachweislich nicht, auf keiner Plattform — die Zusicherung war also immer schon je Bahn gemeint, ohne dass es irgendwo steht. **Der billigste ehrliche Weg ist deshalb, es hinzuschreiben** (`doku/anhang-a.md`, Sperren-Abschnitt): Die Sperre schützt vor einem versehentlichen Doppellauf **derselben** Bahn; wer beide Bahnen gleichzeitig im selben Arbeitsbaum fährt, ist auf sich gestellt. Das kostet einen Absatz und beseitigt die stillste Hälfte des Problems — die falsche Erwartung. **Wenn sie bahnübergreifend gelten soll, ist der PID-Weg tot** und es braucht ein Merkmal, das **beide** Seiten lesen können. Zwei Kandidaten, beide mit einem Haken, der vor dem Bauen gemessen gehört: (a) **Die Windows-PID zusätzlich hinterlegen.** Git-Bash kann sie über `/proc/<pid>/winpid` beschaffen; ob das unter Git for Windows verlässlich vorliegt, ist **nachzumessen**, nicht anzunehmen. Dann liest die pwsh-Seite `winpid` und die bash-Seite weiter `pid`. (b) **Ein gemeinsames Artefakt statt zweier.** Beide Bahnen sperren über denselben Ordner, und beide prüfen die Lebendigkeit über einen Weg, den beide haben. Der Haken ist gross: Das nähme der pwsh-Bahn `FileShare::None`, also die einzige Sperre im Kit, die das **Betriebssystem** durchsetzt — ein Rückschritt, den `doku/einrichtung.md` ausdrücklich als Vorteil der pwsh-Bahn führt. **Zwischenschritt, der unabhängig von der Entscheidung trägt und wenig kostet:** `install.ps1` bricht vor einem `--update` ab, wenn `.team-loop.lock.d` **existiert** — ohne PID-Auswertung, also konservativ —, und nennt in der Meldung, wie eine verwaiste Sperre von Hand entfernt wird. Beim `BL-10`-Schutz ist Vorsicht die richtige Richtung: Ein zu Unrecht abgelehntes Update kostet einen Satz, ein zu Unrecht erlaubtes hat im Feld einen Lauf gestoppt. Für `team-status.ps1` gilt dasselbe **nicht** — dort wäre ein dauerhaftes „läuft gerade" eine Falschaussage im Bericht; die Zeile braucht das echte Merkmal und wartet auf die Entscheidung. **Gegenprobe, die den Fix erst gültig macht:** Ein Arbeitsbaum mit einer von der bash-Bahn gehaltenen Sperre — `install.ps1 --update` muss abbrechen, `team-status.ps1` darf nicht „idle" melden. Und die Gegenrichtung, ohne die es keine Meldung ist: derselbe Baum ohne Sperre muss beide Wege **schweigen** lassen. Ist (a) gebaut, kommt die Probe dazu, dass eine **verwaiste** bash-Sperre den pwsh-Weg nicht dauerhaft blockiert — sonst tauscht dieser Eintrag denselben Fehlalarm ein, den `BL-190` gerade abgestellt hat |
| BL-198 | **Der README-Wächter deckt die Testzahlen ab, aber nicht die zwei Backlog-Zahlen daneben — und meldet trotzdem „alle Zahlen sind gemessen".** `geteilt/kit-readme-pruefen.py` prüft drei Gattungen, und zwar richtig: Testfälle, Testdateien, installierte Dateien. Alle drei bekommen ihre Sollzahl aus einer **frischen Installation** (`bash/kit-test.sh` Zeile ~354). Zwei weitere Zahlen im selben README behaupten dasselbe über dasselbe Kit und werden von **niemandem** gemessen: die Spanne `BL-1`…`BL-<N>` (Zeile ~343) und die Zahl der Archiv-Einträge (Zeilen ~114 und ~345, zweimal dieselbe Zahl in freier Prosa). Beide sind aus dem Repo in einer Zeile ableitbar — `grep -c '^| BL-' plans/backlog-archiv.md` und die höchste vergebene Nummer über Backlog **und** Archiv. **Nicht vermutet, sondern eingetreten:** Am 2026-08-26 kam `BL-196` dazu, das README nannte weiter `BL-195`, und alle drei Doku-Wächter blieben grün. Gefunden wurde es beim Eintragen von `BL-197` — von Hand, nicht vom Wächter. **Die schärfere Hälfte ist die Schlusszeile.** `main()` hängt jede Zahlenprüfung an ein `if a.<zahl> is not None`, druckt am Ende aber unbedingt `✓ README: alle genannten Pfade existieren, alle Zahlen sind gemessen.` Ohne Argumente — also bei jedem Aufruf von Hand, und genau so wird er nach einer Doku-Änderung aufgerufen — läuft **keine einzige** Zahlenprüfung, und die Erfolgszeile behauptet trotzdem, alle seien gemessen. Das ist die Gattung von `BL-145`: Zwei Aufrufwege desselben Skripts sichern verschieden viel zu, und beide melden dasselbe Grün. **Und es gibt eine zweite Hälfte, die schwerer wiegt als die erste — sie ist ebenfalls `BL-145`s Gattung, nur an einer Stelle, die dort nicht mitkam:** Die drei Zahlen, die der Wächter *kann*, prüft **nur `kit-test.sh`** (Zeile ~354). `kit-test.ps1` prüft das README an **keiner** Stelle. Auf einer pwsh-Maschine ist die Drift damit **strukturell unsichtbar**, und auf der bash-Maschine kostet der Nachweis Stunden. **Gemessen am 2026-08-27, nicht vermutet:** Das README nennt `757 Regressionstests` (zweimal, dazu im Badge), `97 Testdateien` und `153 Dateien`; gemessen an einer **frischen Installation** — also so, wie `kit-test.sh` es tut — sind es **973 Fälle**, **113 Testdateien** und **169 Dateien**. Die Badge-Zahl steht seit `6f48dec` (Kit `2.13.1`) unverändert; seither sind **216 Fälle**, **16 Testdateien** und **16 ausgelieferte Dateien** dazugekommen, ohne dass ein Wächter angeschlagen hat. Der Selbsttest der bash-Bahn wäre in Schritt 3 seither **rot** — gefahren hat ihn seit dem 2026-08-24 niemand. **Und ein vierter Fall derselben Gattung stand daneben:** Der Absatz, der die Trägerregel aus `BL-180` erklärt, führte als Gegenbeispiel die nackte Zahl „86 Tests" an — und wurde vom Wächter zu Recht als unqualifizierte Aussage über das Kit gemeldet. Die Regel verletzte ihr eigenes Beispiel, und niemand hat es gesehen, weil niemand den Wächter mit Argumenten gefahren hat | Kit, 2026-08-27 — beim Verbuchen der Feld-E-Meldung zu `BL-197`. Nicht aus dem Betrieb: Beim Nachziehen der README-Zahlen fiel auf, dass die Spanne noch `BL-195` sagte, obwohl `BL-196` seit dem Vortag im Backlog steht — und dass `kit-readme-pruefen.py` das folgenlos durchwinkt und danach „alle Zahlen sind gemessen" druckt. **Gezählt, nicht geschätzt:** Von den fünf Zahlen, die das README über sich selbst behauptet, sind drei gemessen und zwei nicht; die Doku-Wächter laufen nach **jeder** Doku-Änderung, also lief der Wächter über die falsche Zahl mindestens einmal hinweg | **offen — zwei Teile, der zweite ist der wichtigere.** **(1) Die zwei Zahlen mitmessen.** `--archiv-eintraege <N>` und `--hoechste-bl <N>` nach dem Muster der drei vorhandenen: ein Regex-Satz je Gattung, positiv geprüft, nicht namentlich verboten — die Begründung dafür steht schon im Kommentar bei `kit-test.sh` Zeile ~347 („der Vorläufer kannte zwei feste Formulierungen und übersah deshalb wochenlang ein drittes"). Die Sollzahlen kommen aus dem Repo, nicht aus der Installation: Der Backlog **des Kits** wird nicht mitinstalliert. **(2) Die Erfolgszeile sagt, was sie geprüft hat.** Sie nennt die gemessenen Gattungen beim Namen und schweigt über die, die ohne Argument gar nicht liefen — oder sie verlangt die Argumente. Eine Zusicherung, die ohne Argumente dieselbe Zeile druckt wie mit, ist nach `BL-14` keine. **Gegenprobe, die den Eintrag erst gültig macht:** Ein README mit einer um eins zu niedrigen `BL`-Spanne und ein README mit einer falschen Archivzahl müssen **je einzeln** rot werden — beide Gattungen getrennt zurückgedreht, an einer Kopie, wie es `kit-test.sh` für die drei vorhandenen schon tut. Und die Gegenrichtung, ohne die es keine Meldung ist: das unveränderte README muss grün bleiben. Für Teil (2): Ein Aufruf **ohne** Zahlenargumente darf die Zeile „alle Zahlen sind gemessen" **nicht** mehr drucken — das ist der Fall, an dem der Fund hängt. **(3) Und der Teil, der die Drift erst sichtbar macht: `kit-test.ps1` prüft das README wie `kit-test.sh`.** Solange nur die bash-Bahn nachrechnet, hängt die Aktualität dieser Zahlen an einem Lauf, den auf einer pwsh-Maschine niemand fahren kann — der Rest von `BL-145`, an derselben Stelle wie `BL-196` Teil (2). Bis dahin bleibt jede Doku-Änderung darauf angewiesen, dass jemand von Hand zählt. **Nicht Teil dieses Eintrags, weil schon geschehen:** Die drei Zahlen sind am 2026-08-27 auf den gemessenen Stand gezogen worden — von Hand, beim Bauen von `BL-190`, und genau das ist der Beleg für den Eintrag |
| BL-197 | **Die Buchungsregel für eine Sitzung ohne Closeout hängt an einer Erinnerung statt an einem Ereignis — und ihr Ausfall ist im Bericht baulich unsichtbar.** `BL-165` hat die Regel ins Architekten-Briefing gebracht: *„Eine Sitzung ohne Closeout bucht ihre Kosten selbst"*, samt Befehl und Begründung. Der Melder **hat** sie — er ist auf `2.13.1`, er zitiert sie wörtlich, er hat sie verstanden. Sie hat trotzdem an **einem Tag zweimal** nicht gegriffen. **Der Unterschied ist nicht Disziplin, sondern Auslöser.** Ein Closeout hat einen: Die Kaskade ist fertig, der Loop meldet Feierabend, das Briefing verlangt ein Abschluss-Doc, und der Kostenabschluss steht als Punkt 2 in derselben Liste. Eine reine Planungs- oder Nachbesserungssitzung hat keinen — sie **endet einfach**, der Mensch schliesst das Fenster, sobald der Plan committet ist, und in diesem Moment liest niemand mehr eine Regel. **Erschwerend baut das Kit den Fall selbst:** Das Briefing empfiehlt „nach einem gebuchten Closeout eine **neue** Sitzung für die nächste Kaskade" — die Empfehlung erzeugt genau die Sitzung, die die Regel abfangen soll, und beide stehen im selben Dokument. **Der zweite Halbsatz ist der schwerere, und er ist im Quelltext nachgeprüft, nicht geglaubt:** `ledger_pruefen()` P1 stuft eine fehlende `architekt`-Zeile als **Hinweis** ein (`geteilt/tools/kosten.py`, Zeilen ~697–703: *„Legitim, wenn der Architekt fuer diese Kaskade nichts abzurechnen hatte"*). Und der Kontostand zeigt **ausschliesslich** `[WARNUNG]`-Zeilen — `bash/entry/team-status.sh` Zeile ~271 filtert auf `*WARNUNG*`, `pwsh/entry/team-status.ps1` Zeile ~237 auf dasselbe Muster. **Ein Hinweis erscheint im Regelbericht also nie.** Die Schwere ist damit keine Beschriftungsfrage, sie entscheidet zwischen *unsichtbar* und *sichtbar*. An der Stelle steht stattdessen `Architekt K<N> (Churn-Proxy, nicht im Gesamt enthalten)` (`bash/lib.sh` Zeile ~1456, dokumentiert in `doku/faq.md` Zeile ~412) — eine Schätzung, die aussieht wie eine Erfassung. **Abgrenzung zu `BL-193`, denn die beiden sehen sich ähnlich und sind es nicht:** `BL-193` beschreibt die **Messung** — `sitzung-messen --projekt .` liest nur das zuletzt geänderte Transkript, die Aushärtung liegt zwei Sitzungen zurück. Dieser Eintrag beschreibt den **Anlass zu messen**. Beide Wege, die `BL-193` gebaut hat, setzen voraus, dass jemand im richtigen Moment daran denkt; keiner von beiden bringt einen Auslöser mit | `Feld E`, 2026-08-26, beim Öffnen des Closeouts der **siebten** Kaskade (Kit `2.13.1`, Linux, bash-Bahn, Flutter/Dart mit SQLite, Abo-Auth, Ledger seit der ersten Kaskade lückenlos geführt). Das Ledger hatte für diese Kaskade keine `architekt`-Zeile, obwohl der Plan zwei Tage zuvor ausgehärtet und committet war. Die Suche nach dem Grund förderte einen **zweiten** Fall desselben Tages zutage. **Gemessen, nicht geschätzt:** Sitzung A (Nachlauf zur vorigen Kaskade — zwei Handprüfungen am Gerät, ein Hilfsskript auf echte Exit-Codes umgebaut, zwei Meldungen ans Kit) **36,22 USD**; Sitzung B (Aushärtung der nächsten Kaskade — Prototyp-Abgleich und Plandokument) **7,68 USD**; zusammen **43,90 USD** Abo-Gegenwert, die nie im Ledger standen. Beide Sitzungen waren regulär, produktiv und haben committet — keine hat gebucht. **Gerettet wurde der Betrag nur durch einen Zufall:** `sitzung-messen` liest benannte Transkripte, und die zwei Dateien lagen noch da. Der Regelfall ist ein anderer — ohne Argument liest das Werkzeug das **zuletzt geänderte** Transkript, und das ist beim nächsten Closeout ein drittes. Reiht sich in die Grössenordnung aus `BL-193` ein: dort **10,65 USD** und **39 %** der Architektenkosten einer Kaskade, frühere Aushärtungen desselben Projekts zwischen **8,7 und 34,8 USD**. **Lokal nichts gepatcht**, ausdrücklich mit Begründung: Der Fund steckt im Briefing, also im Kit; ein lokaler Eingriff hätte die bekannte Verfallszeit beim nächsten `--update` | **offen — zwei Teile, und der billigere ist der wichtigere.** **(1) Den stillen Fall laut machen, und er kostet keine neue Mechanik.** In `ledger_pruefen()` P1 wird eine **nummerierte** Kaskade mit `ralph`-Zeile und ohne `architekt`-Zeile zur **Warnung** statt zum Hinweis. Das Argument ist wörtlich dasselbe, das `ralph-fehlt` schon trägt — dort *„gebaut wurde immer, wenn gesweept wurde"*, hier *„geplant wurde immer, wenn gebaut wurde"*: Ohne Aushärtung gäbe es nichts zu bauen. **Benannte Kaskaden bleiben ein Hinweis** (`post-20`, `roles-post-k13` sind Out-of-Loop-Fixserien ohne Aushärtung) — dieselbe Unterscheidung, derselbe Grund wie in `BL-14`. **Die Falle gehört von Anfang an mitgebaut:** Ein unter einer älteren Kit-Fassung gewachsenes Ledger, in dem der Architekt nie gebucht hat, wird auf einen Schlag zu **N** Warnungen — dauerhaft unauflösbar, weil die Transkripte längst weg sind. Das ist der Fehlermodus aus `BL-14` selbst: Eine Warnung, die immer erscheint, ist keine. Also **eine** gebündelte Warnung, die Zahl und Kaskaden nennt, nicht eine je Kaskade. **Gegenprobe, die den Teil erst gültig macht — vier Fälle, jeder einzeln zurückgedreht:** Ein Ledger mit den Kaskaden 1–7, in dem nur 7 die `architekt`-Zeile fehlt, muss **genau eine** Warnung erzeugen und 7 namentlich nennen · dasselbe Ledger vollständig gebucht muss **schweigen** (sonst ist es keine Meldung) · eine benannte Kaskade `post-7` mit `ralph` und ohne `architekt` muss **Hinweis** bleiben · und ein Ledger, in dem **sechs von sieben** Kaskaden die Zeile fehlt, muss **eine** Warnung erzeugen, nicht sechs. Dazu die Bahn-Gegenprobe, die dem Fund seine Wirkung gibt: Der Kontostand (`--budget`) muss die Zeile **zeigen**, auf **beiden** Bahnen — vorher zeigte er sie nicht, und genau das ist der Fund. **(2) Den Auslöser dorthin legen, wo er entsteht.** Die **Scharfschalt-Sequenz** ist schon heute eine Pflicht-Ausgabe — Briefing Punkt 3: *„am Ende jeder Aushärtung **immer automatisch**"*. Hängt der Kostenabschluss der Sitzung als **letzter, kopierfertiger Schritt** daran, hängt er an einem **Ereignis** statt an Erinnerung. Zwei Befehle, weil der Betrag erst gemessen werden muss: `kosten.py sitzung-messen`, dann `--architekt-abschluss <USD> <domaene> "Kaskade N+1 geplant" --kaskade <N+1>` mit der Kaskadennummer **vorausgefüllt aus dem Plankopf**. **Ausdrücklich NICHT:** die `BL-165`-Regel ersetzen. Die Regel sagt das **Warum**, die Sequenz liefert das **Wann**; gelesen wird im entscheidenden Moment nur die Sequenz. **Gegenprobe:** die Bauart aus `BL-193` — den **Absatz** schneiden, nicht den Abschnitt, und die Fälle **zählen** statt suchen. `--architekt-abschluss` und `--kaskade` stehen in derselben Datei schon aus anderem Grund; ein Fall über den ganzen Abschnitt bliebe grün, wenn man den neuen Satz wieder herausnimmt. Das hat bei `BL-193` und `BL-195` je einen Anlauf gekostet. **Ausdrücklich NICHT Teil dieses Eintrags:** der Lückenfinder aus `BL-193` Weg (2). Er bleibt offen und bleibt der gründlichere — er findet die Lücke **maschinell**, statt sie einer Regel anzuvertrauen. Er kostet aber eine **Formatänderung am Ledger** (gemessene Transkript-ID je Zeile) mit eigener Gegenprobe gegen gewachsene Feld-Ledger. Teil (1) hier holt einen guten Teil seines Nutzens, **ohne** das Format anzufassen. Reihenfolge: erst (1), dann (2), und erst danach entscheiden, ob `BL-193` Weg (2) den Preis noch wert ist |
| BL-196 | **Die Abgleichsablage aus `BL-178` bleibt liegen, und niemand sagt, dass sie weggeworfen werden darf.** Beide Installer rendern für den Block „Bitte von Hand abgleichen" die Kit-Fassung der abweichenden Dateien in ein Wegwerf-Verzeichnis (`$TMPDIR/team-kit-abgleich-*`) und nennen im Hinweis den Vergleichsbefehl darauf. Aufgeräumt wird **nur, wenn nichts abweicht** (`install.ps1`, `$abgleich -eq 0`); weicht etwas ab — und bei `CLAUDE.md` ist das laut demselben Block ausdrücklich der **Normalfall** —, bleibt das Verzeichnis stehen. Das ist so gewollt: Der Anwender soll den genannten Befehl noch ausführen können. Nur endet die Zusage dort. **Kein Satz sagt, dass die Ablage danach entbehrlich ist**, kein Lauf entfernt eine ältere, und der Hinweis nennt sie nicht als temporär — geprüft: In `install.sh` und `install.ps1` kommt keine Formulierung über Aufräumen oder Löschen vor. **Gemessen, nicht vermutet:** Nach einem Arbeitstag mit Selbsttest-Läufen und Update-Proben lagen **elf** solcher Verzeichnisse in `%TEMP%` (36–60 KB je Stück, also kein Platzproblem — ein Ordnungsproblem). **Warum das trotzdem zählt:** Ein Verzeichnis, dessen Lebensdauer niemand benennt, wird entweder nie gelöscht oder im falschen Moment — nämlich bevor der Anwender den Vergleich gefahren hat. Beides ist vermeidbar, und die Bauart ist dieselbe wie bei `BL-44`: ein Hinweis, der eine Handlung ankündigt, ohne ihren Rahmen zu nennen. **Eine zweite Hälfte, und sie gehört zur Gattung von `BL-145`:** `kit-test.sh` räumt seine eigenen Abgleichsablagen nach jedem der beiden Update-Läufe ausdrücklich weg (Zeilen ~538 und ~603, mit einer Schranke gegen einen leeren Pfad); `kit-test.ps1` tut das **nicht**. Der pwsh-Selbsttest hinterlässt damit je Lauf mindestens ein Verzeichnis — bei einem Lauf, der ohnehin eine Stunde dauert und deshalb wiederholt wird, summiert sich das | Kit, 2026-08-26 — beim Aufräumen nach den `BL-145`-Läufen aufgefallen. Nicht aus dem Betrieb, sondern beim Nachsehen, was die Läufe in `%TEMP%` hinterlassen hatten: elf `team-kit-abgleich-*` neben drei `team-kit-test-*`. Die drei Selbsttest-Ordner sind erklärt (sie bleiben bei einem **roten** Lauf absichtlich zur Ansicht liegen, so steht es in der Schlusszeile); die elf anderen sind es nicht | **offen.** Drei Teile, und der erste ist der wichtigste. **(1) Der Hinweis sagt, was mit der Ablage geschieht.** Eine Zeile unter dem Vergleichsbefehl: dass die gerenderte Kit-Fassung eine **Kopie zum Nachlesen** ist, dass sie im Temp-Verzeichnis liegt und nach dem Abgleich gelöscht werden kann — samt dem Befehl dafür, kopierfertig, auf beiden Bahnen in der jeweils richtigen Schreibweise. Ohne diesen Satz ist jede weitere Mechanik Rätselraten. **(2) `kit-test.ps1` räumt seine eigenen Ablagen weg**, wie `kit-test.sh` es tut — mit derselben Schranke gegen einen leeren oder unerwarteten Pfad, denn ein `Remove-Item -Recurse` auf einen falsch geparsten Pfad ist teurer als der liegen gebliebene Ordner. Das ist der Rest der Doppelbahn-Angleichung aus `BL-145`. **(3) Erst danach, und nur wenn es sich lohnt:** Der Installer entfernt beim **nächsten** Update die Ablage des vorigen — sie hat ihren Zweck dann erfüllt. **Ausdrücklich NICHT:** die Ablage sofort nach dem Rendern löschen. Sie ist die einzige Stelle, an der der Anwender die Kit-Fassung sehen kann, und der Block ist genau dafür gebaut (`BL-4`, zweite Hälfte). **Gegenprobe, die den Fix erst gültig macht:** Ein Update mit einer abweichenden Datei, danach der genannte Löschbefehl — er muss die Ablage treffen und **nichts** ausserhalb von `$TMPDIR/team-kit-abgleich-*`. Und ein Selbsttest-Lauf auf beiden Bahnen darf **keine** Abgleichsablage hinterlassen; gezählt wird vorher und nachher, nicht geschätzt |
| BL-193 | **Die Aushärtungs-Sitzung einer Kaskade ist mit dem dokumentierten Ablauf strukturell nicht buchbar.** `sitzung-messen --projekt .` liest **immer nur das zuletzt geänderte Transkript**. Zum Zeitpunkt des Closeouts ist das die Closeout-Sitzung selbst; die Aushärtungs-Sitzung liegt zwei Sitzungen zurück, wird nie gelesen, und **keine Meldung weist auf sie hin**. **Der Ablauf erzwingt das, er lässt es nicht bloss zu:** (1) Der Architekt härtet die nächste Kaskade aus — laut Kit ausdrücklich eigene Handarbeit und laut Briefing das Teuerste, was er tut. (2) Der Stakeholder legt den Zeiger um und startet den Lauf; zwischen (1) und (2) gibt es **keinen** Buchungsschritt, denn das Briefing verbietet den Kostenabschluss in einer Loop-Stufe ausdrücklich. (3) Der Closeout läuft danach in einer **neuen** Sitzung, so verlangt es „Ein Closeout je Sitzung". Damit ist die Aushärtungs-Sitzung zum Buchungszeitpunkt **niemals** die zuletzt geänderte. Wer sich an den dokumentierten Ablauf hält, verliert sie. **Und zwar lautlos:** Das Ledger ist in sich konsistent, `--ledger-pruefen` meldet nichts (es hält archivierte Rohlogs gegen das Ledger, und für eine interaktive Sitzung gibt es keinen Rohlog), `--budget` zeigt eine plausible Summe. Der Fehlbetrag ist nur sichtbar, wenn jemand die Transkript-Ablage von Hand gegen das Ledger hält. **Wo es steckt:** `geteilt/prompts/rolle-architekt.md`, Abschnitt „Nach jedem Lauf (Closeout, Pflicht)", Punkt 2. Er nennt zwei Quellen — die Laufkosten und „meine eigene Sitzung" —, und „meine eigene Sitzung" ist im Closeout-Kontext eindeutig die Closeout-Sitzung. Die Aushärtungs-Sitzung derselben Kaskade wird an **keiner** Stelle erwähnt. Der Abschnitt kennt die verwandte Falle bereits, aber nur in der **anderen** Richtung: „Ein Closeout je Sitzung" warnt davor, dass zwei Closeouts in **einer** Sitzung denselben Betrag doppelt buchen (`BL-116`). Der umgekehrte Fall — **eine** Kaskade über **mehrere** Sitzungen, von denen nur die letzte gemessen wird — steht nicht da. Verwandt mit `BL-165`: Beide beschreiben Symptome derselben Ursache — **die Messung hängt an „zuletzt geändert", die Buchhaltung an „Kaskade"** | `Feld E`, 2026-08-25, beim Kostenabschluss der sechsten Kaskade (Kit 2.13.0, Linux, bash-Bahn, Flutter/Dart, Abo-Auth für alle Rollen). **Gemessen, nicht geschätzt:** In diesem Projekt waren es **10,65 USD Abo-Gegenwert** — **39 % der gesamten Architektenkosten dieser Kaskade**. Gebucht wurden sie nur, weil der Architekt die Transkript-Ablage von Hand durchsucht und `sitzung-messen` mit einem ausdrücklich benannten Pfad aufgerufen hat; **das steht in keinem Briefing**. Kein Einzelfall dieses Laufs: Die Aushärtungen früherer Kaskaden derselben Installation liegen zwischen **8,7 und 34,8 USD**. Ob eine Installation überhaupt betroffen ist, hängt allein daran, ob die Aushärtung zufällig in derselben Sitzung lag wie der vorige Closeout — bei zwei Kaskaden war das so, bei dieser nicht | **offen — zwei der drei Wege sind gebaut, der dritte ist der teure.** **Was am 2026-08-26 schon da war:** Weg (3), „die Aushärtung buchen, wo sie entsteht", ist mit `BL-165` am selben Tag ins Architekten-Briefing gekommen — *„Eine Sitzung ohne Closeout bucht ihre Kosten selbst"*, samt dem Befehl `--architekt-abschluss <USD> <domaene> "Kaskade N+1 geplant" --kaskade <N+1>`. Der Melder ist auf Kit **2.13.0**, also auf der Fassung davor; für ihn ist das die Reparatur, für das Kit war es schon geschehen. **Was heute dazugekommen ist — Weg (1), und er ist mehr als eine Sofortmaßnahme:** Die Vorbeugungsregel hilft nur, wer **vor** der Aushärtung steht. Wer beim Closeout steht, hat sie hinter sich; ihm nützt sie nichts, er braucht den **Rückweg**. Punkt 2 des Closeout-Abschnitts sagt jetzt ausdrücklich, dass **„meine eigene Sitzung" ZWEI sind** — Aushärtung und Closeout —, dass `sitzung-messen --projekt .` nur die letzte davon liest, und wie die andere nachzuholen ist: über ihren **Pfad**, gebucht mit `--addieren`. Mit der Gegenrichtung daneben, denn ohne sie wäre der Rückweg schädlich: Wurde die Aushärtung an ihrem Ende gebucht, steckt sie schon im Ledger und darf **nicht** ein zweites Mal drauf (`BL-116`). Dazu die Größenordnung aus dem Feld (10,65 USD, 39 % der Architektenkosten einer Kaskade) und der Satz, der den Fund erst gefährlich macht: **Nichts meldet diese Lücke** — das Ledger ist stimmig, `--ledger-pruefen` schweigt mangels Rohlog, `--budget` zeigt eine plausible Summe. Vier Fälle in `geteilt/tests/test_bl165_bedienanleitung_nennt_die_regeln.py` halten den Absatz fest; jede der vier Gegenproben greift (Rückweg ohne `--addieren` · Pfad-Hinweis raus · Doppelbuchungs-Warnung raus · Verweis auf die Vorbeugungsregel raus). **Ein Umstand, der beim Bauen Zeit gekostet hat und hier festgehalten gehört:** Der erste Entwurf prüfte den **ganzen** Punkt 2 auf `--addieren` und `Pfad`. Beides steht dort schon aus anderem Grund — `--addieren` für den Nachlauf einer Rolle —, und **drei von drei Gegenproben blieben grün**. Die Zusicherung gilt dem Absatz, also wird jetzt der Absatz geschnitten. **Was offen bleibt: Weg (2), der Lückenfinder** (`kosten.py sitzung-lueckenpruefung --projekt .`) — alle Transkripte auflisten, die jünger sind als die älteste Ledger-Zeile und in keiner Buchung vorkommen. Er ist der einzige der drei, der die Lücke **maschinell** findet statt sie einer Regel anzuvertrauen, und damit der gründlichste; er ist auch der teuerste, weil `--akteur-abschluss` dafür die gemessene Transkript-ID in der Ledger-Zeile ablegen müsste. Heute steht sie dort nur, wenn der Architekt sie von Hand in die Notiz schreibt — das ist eine **Formatänderung am Ledger** und braucht ihre eigene Gegenprobe gegen gewachsene Ledger aus dem Feld. **Gegenprobe für den offenen Teil:** Eine Ablage mit **zwei** Transkripten, von denen das ältere die Aushärtung ist und in keiner Ledger-Zeile vorkommt — der Lückenfinder muss genau dieses eine melden und das jüngere nicht. Und die Gegenrichtung: Ist beides gebucht, muss er schweigen |
| BL-194 | **Der Selbsttest fährt zwei Konfigurationen — und beide sind Python. Die ganze Gattung „eine Annahme des Kits, die stillschweigend Python heißt" ist damit nur im Feld zu finden.** `kit-test.sh` installiert das Kit zweimal in ein Wegwerf-Repo, einmal mit den Auslieferungswerten und einmal mit angepasster Konfiguration. Angepasst werden dabei **Ordner**, nicht **Sprachen**: `TEAM_TEST_ORDNER` wandert, die Reproducer-Konvention, die Test-Endung und der Smoke-Test bleiben pytest. Genau deshalb ist `BL-171` (zwei Zusicherungen verdrahten `.py` und `strict=True`) nicht im Selbsttest aufgefallen, sondern erst, als ein Dart-Projekt seine Suite fuhr — und dort als **Sockel von sechs bis sieben dauerhaft roten Fällen**, also an der Stelle, an der die Suite als Signal wertlos wird. **Der Aufwand ist der Punkt, an dem zu entscheiden ist:** Eine dritte, wirklich nicht-python Konfiguration braucht ein Wegwerf-Projekt mit fremdem Test-Läufer — oder, billiger und fast so gut, eine Konfiguration, die nur die **Marken** verdreht (Endung, Reproducer-Muster, Smoke-Befehl), ohne dass ein zweiter Interpreter installiert sein muss. Die zweite Bauform fängt die Gattung „Literal statt Konfigurationswert", und mehr war an `BL-171` nicht dran | Kit, 2026-08-26 — beim Abtragen von `BL-171` und `BL-191` festgehalten. Beide sind in einer **Installation** rot geworden und in der **Kit-Ablage** unsichtbar geblieben; `BL-191` auf jedem POSIX-Wirt, `BL-171` in jedem Nicht-Python-Projekt. Der Selbsttest hat in beiden Fällen nichts gemeldet | **offen.** Erst entscheiden, welche der beiden Bauformen gefahren wird (echtes fremdes Test-Paket oder verdrehte Marken), dann bauen. **Gegenprobe, die den Fix erst gültig macht:** `.py` und `strict=True` in den beiden Zusicherungen wieder als Literal einsetzen — die neue Stufe muss rot werden, die bestehenden zwei Konfigurationen müssen grün bleiben |
| BL-169 | **`src/` + `tests/` als ausgelieferte Ordner-Defaults machen Reproducer-Tests in jedem Stack mit paketgebundener Testsuche unausführbar — und zwar stumm.** `bootstrap/team.config.sh` belegt `TEAM_PRODUKTIVCODE` mit `src/` und `TEAM_TEST_ORDNER` mit `tests/` vor. Das trägt, solange der Testläufer die Dateien am **Pfad** findet (pytest). Es trägt **nicht**, sobald er sie am **Paket** findet: Dart/Flutter sammelt ausschließlich innerhalb des Pakets und ausschließlich unterhalb von `test/`; liegt das Paket unter `src/`, liegt der vom Kit vorgesehene Testordner **außerhalb** davon. Dieselbe Bauart bei Cargo (`tests/` relativ zu `Cargo.toml`), Go (Paketverzeichnis) und Gradle (`src/test/`). **Die zweite Hälfte ist vom Ordner unabhängig und wiegt schwerer:** Der Läufer nimmt nur Dateien mit einem bestimmten Namensmuster — `_test.dart` bei Dart, `_test.go` bei Go. Die Konvention des Kits lautet `tests/test_hm<nr>_<stichwort>.py` und steht wörtlich in `bootstrap/CLAUDE.md.vorlage` (Fund-Format **und** der Absatz zur Benennung nach der Fund-Nummer), in `bootstrap/beutebuch.md` und in `geteilt/prompts/rolle-harry.md`/`rolle-marv.md`. Buchstabengetreu auf Dart übertragen ergibt das `test_hm36_foo.dart` — einen Namen, den der Läufer ignoriert. **Folge in beiden Hälften identisch:** Franks regelkonform abgelegter Reproducer wird nie ausgeführt, der Smoke-Test bleibt grün, das Beutebuch zeigt einen Fund mit Reproducer, geprüft wird nichts. Das ist derselbe Schaden wie `BL-15` (Backtick-Regel) und `BL-28` (`strict`-Marker), nur eine Ebene tiefer: Dort war der Test da und stumm markiert, hier wird er gar nicht erst gefunden. **Nicht betroffen ist der Extraktor:** `DATEI_RE` in `team/tools/beutebuch.py` akzeptiert jede Endung und hat den umgestellten Dart-Pfad im Lauf korrekt als `test/hm6_stichwort_test.dart` erkannt — der Substanz-Anker trägt, allein die Vorgabewerte und Beispiele tragen nicht | `Feld E`, 2026-08-23, vom Architekten beim Aushärten der **ersten** Kaskade gefunden — durch Lesen der Kopplung zwischen Konfiguration und Testläufer, **bevor** ein Lauf startete. Dasselbe Zeitfenster wie `BL-149`: Sobald ein Projekt seine Ordner einmal richtig gesetzt hat, ist der Default für immer unsichtbar, und ein laufendes Projekt kann den Fehler gar nicht mehr erleben. Getroffen wird ausschließlich der Erstlauf | **offen.** Zwei Wege, und sie fangen Verschiedenes. **(1) Der Installer leitet ab statt vorzugeben:** Er kennt den Stack bereits aus dem Aufnahme-Interview — aus ihm folgen Produktivcode-Ordner, Testordner **und** das Namensmuster des Reproducers. Für Dart/Flutter `lib/` + `test/` + `<name>_test.dart`, für Cargo `src/` + `tests/`, für Go das Paketverzeichnis + `_test.go`. **(2) Wo der Stack unbekannt bleibt**, gehört die Kopplung in den Kommentar von `bootstrap/team.config.sh`, in einem Satz: *Der Testordner muss dort liegen, wo der Läufer sucht, und der Dateiname so heißen, dass er ihn nimmt.* Beides zusammen, nicht eines davon — (1) hilft dem erkannten Stack, (2) dem unerkannten. **Die Gegenprobe, die den Fix erst gültig macht:** Eine frische Installation für einen paketgebundenen Stack, in der die ausgelieferte `Reproducer-Test`-Zeile ausgefüllt, die Datei angelegt und der **konfigurierte Smoke-Test** gefahren wird — er muss diese Datei nachweislich **ausführen**. `test_bl15_reproducer_zeile_ankertauglich.py` prüft heute, ob `DATEI_RE` den Pfad sieht; ob der Testläufer ihn sieht, prüft niemand, und genau dort sitzt der Fund |

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

**Stand 2026-08-28, vierter Teil — fuenf Eintraege abgetragen, alle auf beiden
Bahnen und jeder mit gefahrener Gegenprobe.** `BL-197`, `BL-201`, `BL-205`,
`BL-208` und `BL-169`. Damit stehen noch **fuenf** offen, und sie zerfallen in
zwei Gruppen, die verschieden behandelt gehoeren.

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

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-206 | **Der Commit-Block des Red-Team-Sweeps umgeht den Fremdfilter — fremde untracked Dateien im Testordner werden unter der Sweep-Botschaft mitcommittet.** `pwsh/redteam.ps1` staged `$TEAM_TEST_ORDNER` blanko (`git add <ordner>` nimmt jede untracked Datei mit), waehrend `team_guard_verify` und `team_rollback_rolle` beide `team_fremd_ausfiltern` benutzen — dieselbe Bauform wie `BL-114`, die dritte Stelle wurde nicht nachgezogen. **Zweiter, tieferer Befund:** `team_pfade_zuruecksetzen` loescht jeden Pfad, den es bei `$StartHash` nicht gab — **auch wenn er inzwischen committet ist**. Der Guard-Schnappschuss ist ein Zeitpunkt; alles, was nach dem Rollenstart entsteht, gilt fuer ihn als Werk der Rolle. Trifft besonders die Projekte, die den Rueckkanal benutzen: Eine Kit-Meldung entsteht typischerweise **waehrend** ein Lauf laeuft | Feld B, 2026-08-28. Ausgeloest durch einen manuellen Commit mit der Begruendung *„sonst ist Marv im Weg"*. Befund 2 in einem leeren Repo nachgestellt: `git cat-file -e $StartHash:pfad` liefert Exit 128, also den Loesch-Zweig. Feldbeleg fuer Befund 1: ein fremder Reproducer lag untracked im Testordner und ging nur gut aus, weil der Fixer den Fund ohnehin bearbeitete | **Befund 1 erledigt 2026-08-28, Befund 2 bleibt offen.** Meldung liegt: [`2026-08-28-der-commit-block-des-red-team-sweeps-umgeht-den-fremdfilter.md`](meldungen/2026-08-28-der-commit-block-des-red-team-sweeps-umgeht-den-fremdfilter.md). **Befund 1:** Neu ist `team_eigene_pfade` in **beiden** Bibliotheken — sie loest die Pathspecs mit `--untracked-files=all` bis zur **Datei** auf (ein blanko gestagter untracked Ordner waere wieder derselbe Fehler), schickt sie durch denselben `team_fremd_ausfiltern`, den Guard und Rollback ohnehin benutzen, und **meldet auf stderr namentlich**, was sie ausgelassen hat (still auslassen waere die Fehlerrichtung von `BL-160`). Beide Sweep-Skripte stagen danach namentlich. Regressionstest `test_bl206_sweep_committet_nur_eigenes.py`: fuenf Faelle an der Bibliothek auf **beiden** Bahnen, drei am laufenden `harry.sh` — und die Gegenrichtung ist die eigentliche Absicherung (eigener Reproducer und Beutebuch-Zeile muessen WEITER committet werden). Gegenprobe gefahren: gegen den alten Stand fallen sechs Faelle, gegen den neuen laufen alle. **Befund 2 (Entwurfsfrage, offen):** Ein Pfad, den es beim Rollenstart nicht gab, faellt im Rollback **immer** in den Loesch-Zweig — auch committet. `team_fremd_ausfiltern` kann per Konstruktion nichts ueber Pfade wissen, die nach dem Start entstanden. Solange das offen ist, steht die **Handregel** in `bootstrap/TEAM.md` (eigener Abschnitt neben „Zuerst: committen"): *Waehrend ein Lauf laeuft, gehoert Handarbeit nicht in diesen Arbeitsbaum.* Sie gehoert in die **Vorlage**, weil `--update` die Datei neu schreibt (`BL-58`) — lokal notiert waere sie beim naechsten Update still weg |
| BL-205 | **Frank hat keine Regel fuer eine schon vor ihm rote Suite — und stellt headless Rueckfragen, die niemand liest.** Schritt 1 seines Auftrags traegt `$SMOKE_SUFFIX` (`pwsh/lib.psm1:227`, bash-Gegenstueck gleich): *„Smoke-Test gruen: <befehl>.“* Die Auflage ist **absolut** und kennt den Fall nicht, dass die Rotheit **nicht von Frank** stammt; `geteilt/prompts/rolle-frank.md` sagt dazu nichts. Damit misst sie eine Eigenschaft der **Maschine** statt eine des Fixes — und trifft ausgerechnet den Lauf, in dem die Rolle richtig gearbeitet hat. **Zweiter Teil, gleiche Wurzel:** Frank kennt genau zwei Ausgaenge (Promise / kein Promise). Fuer *„Hindernis, aber unterwegs einen echten neuen Fehler gefunden“* gibt es keinen — der Beifang endet im gitignorierten Log | `Feld B`, 2026-08-27 — Frank hatte einen fertigen, nachweislich nicht-regressiven Diff; die Suite war unabhaengig von ihm rot (ambiente Umgebungsvariable leckte in eine In-Prozess-Testbank). Er brach regelkonform ab und stellte **zwei Rueckfragen an einen Menschen, den es im headless Lauf nicht gibt** — u. a. die Bitte, den nebenbei entdeckten zweiten Fehler vormerken zu duerfen. Kostenpunkt: 2,7517 USD verworfen und im Folgeaufruf neu bezahlt; der zweite Fehler wurde nur gerettet, weil ein Mensch spaeter das Log oeffnete. Voller Hergang: [`plans/meldungen/2026-08-27-frank-hat-keine-regel-fuer-eine-schon-vor-ihm-rote-suite-und.md`](meldungen/2026-08-27-frank-hat-keine-regel-fuer-eine-schon-vor-ihm-rote-suite-und.md) | **erledigt 2026-08-28 — alle drei vorgeschlagenen Zeilen, auf beiden Bahnen.** **(1) Differenzmessung statt Absolutwert:** `$SMOKE_SUFFIX` sagt jetzt, dass eine schon VOR Frank rote Suite **kein Abbruchgrund** ist — er misst beide Staende und belegt, dass durch SEINEN Fix kein NEUER Fehlschlag entsteht. Die Faehigkeit war da: Frank kennt seinen Ausgangs-Commit ueber `team_guard_begin` ohnehin, es fehlte nur die Auflage. **(2) Der dritte Ausgang:** Findet Frank unterwegs einen echten zweiten Fehler, legt er dafuer einen NEUEN Fundblock mit Status `offen` an und **fixt ihn nicht** — das bestaetigt *Finder ist nicht Fixer*, statt es zu verletzen. Vorher endete der Beifang im gitignorierten Log und wurde nur gerettet, weil ein Mensch spaeter das Log oeffnete. **(3)** *„Es liest niemand mit "— stelle KEINE Rueckfragen, entscheide belegbar und schreibe auf, was du entschieden hast."* **Wo es gelandet ist, und warum nicht im Briefing:** (1) in beiden Bibliotheken, (2) und (3) im **Auftragstext** beider Frank-Entrypoints. `rolle-frank.md` liegt exakt auf dem harten 45-Zeilen-Limit, und ein Briefing liegt in JEDEM Prompt seiner Rolle; der Auftragstext traegt ohnehin die laufspezifischen Auflagen und ist nicht laengenbegrenzt. Regressionstest `test_bl205_frank_kennt_die_schon_rote_suite.py`, **11 Faelle**, darunter die Gegenrichtung, dass `BL-205` die aeltere Vordergrund-Auflage aus `BL-207`/`BL-201` in derselben Zeile **nicht verdraengt** — ein Zusatz, der die aeltere hinausdraengt, tauscht einen Fehler gegen einen anderen. **Gegenprobe gefahren:** gegen den alten Stand fallen 9 von 11; die zwei gruenen sind die Gegenrichtungen |
| BL-204 | **Die Fixphase Frank<->Axel gibt es nur als Innenteil der Vollautomatik — es fehlt der eigene Einstieg.** Phase 4 in `pwsh/entry/vollautomatik.ps1` ist die fertige Automatik: Rundendeckel (`TEAM_MAX_RUNDEN`), Axel nur wenn ein Fall auf ihn wartet, Rueckkehr ueber `Fix-Plan liegt vor`, Auslauf-Bremse (`TEAM_FIX_MAX_STAGNATION`), Budget-Pruefung je Runde, Abbruch-Bericht. Erreichbar ist sie nur, indem man den **ganzen** Lauf startet — also Ralph und die Red-Team-Phasen gleich mit. Der Fall *„Sweep war gestern, heute nur die Funde abarbeiten“* ist damit Handarbeit. Am deutlichsten sagt es das Kit selbst: `Abbruch-Bericht` raet woertlich `Fixphase fortsetzen: .\frank.cmd (ein Fund je Aufruf)` — die Handkurbel, zwanzig Zeilen unter der Schleife, die dasselbe selbstaendig faehrt. Die Exit-Codes von `frank.ps1`/`axel.ps1` (0/1/3/42) sind bereits genau der Vertrag, den ein Aufrufer braucht | `Feld B`, 2026-08-27 — acht Funde ausserhalb eines Laufs abgearbeitet: **17 Handstarts** von `.\frank.cmd`, gezaehlt an den Lauf-Logs (HM-16 1, HM-17 3, HM-13 1, HM-19 2, HM-10 1, HM-14 1, HM-15 4, HM-18 3). Voller Hergang: [`plans/meldungen/2026-08-27-die-fixphase-frank-axel-gibt-es-nur-als-innenteil-der-vollau.md`](meldungen/2026-08-27-die-fixphase-frank-axel-gibt-es-nur-als-innenteil-der-vollau.md) | **offen.** **Vorschlag:** Phase 4 als `team_fixphase` in die Bibliothek ziehen und zwei Aufrufer bedienen — die Vollautomatik wie bisher, dazu ein eigener Einstieg (`.\frank.cmd --auto` oder `.\fixphase.cmd`). Kein neues Verhalten, derselbe Code mit einer zweiten Tuer; **Auslauf-Bremse und Budget-Pruefung je Runde muss der neue Einstieg erben**, sonst dreht er an einem unloesbaren Fund teuer leer. Der `Abbruch-Bericht` nennt dann den Einstieg statt der Handkurbel |
| BL-203 | **Das README macht das Diff-Lesen zur Betriebsbedingung — der Owner selbst betreibt das Kit anders.** `README.md` (Abschnitt „Fuer wen“, Zeilen 44–53) schreibt: *„Wer den Diff nicht liest, kann diese Fragen nicht beantworten“*, ausdruecklich als **Betriebsbedingung**. Der Betreiber von `Feld B` liest den Diff kaum bis gar nicht — bei vier gebauten Kaskaden, ~19 abgearbeiteten Funden und erteilten Abnahmen. Die Bedingung ist also nicht verletzt, sondern **falsch benannt**: Geurteilt wird an den Stellen, die das Kit selbst bereitstellt — Reproschritte (Fund echt oder Rauschen), Reproducer-Test (Ursache oder Symptom), Stufen-Zusicherung und UAT (abnahmereif), Kostenbuchfuehrung (war es das wert). Bedingung ist die **Faehigkeit**, im Zweifel hineinzusehen, nicht die **Taetigkeit** | `Feld B`, 2026-08-27 — Aussage des Betreibers: *„Ich lese den Code kaum bis gar nicht. Aber ich kann es jederzeit, wenn ich will. Das T.E.A.M. mit den entsprechend faehigen Modellen ist eher eine weitere Abstraktionsschicht als eine Ergaenzung zum Coden.“* Voller Hergang samt Formulierungsvorschlag: [`plans/meldungen/2026-08-27-readme-beschreibt-das-diff-lesen-als-betriebsbedingung-der-o.md`](meldungen/2026-08-27-readme-beschreibt-das-diff-lesen-als-betriebsbedingung-der-o.md) | **erledigt 2026-08-28 — im README umgesetzt.** Der freigegebene Wortlaut steht im Abschnitt „Fuer wen", aufgeteilt in zwei Absaetze (die Rolle, dann das *Warum trotzdem „erfahren"*). **Zwei Folgestellen mitgezogen**, die dieselbe Aussage trugen und sonst zwei Absaetze spaeter widersprochen haetten: der Regiepult-Absatz (*„liest den Diff und gibst die naechste Stufe frei"* -> *„urteilst am Ergebnis"*) und die Pruefeinheit unter „Der Antrieb" (*„Menge, die ein Stakeholder noch lesen und verantworten kann"* -> verantworten zuerst, lesen als Rueckfallweg *wenn es klemmt*). Die Bestandsaufnahme der Meldung nannte nur die eine Stelle; ein `grep` auf *Diff* fand drei |
| BL-202 | **Kaskaden-Plandateien heissen `ralph-kaskade-N-<thema>.md`, obwohl sie das ganze Team binden.** Der Name nennt **eine** Rolle; das Dokument bindet alle: Ralph liest die Stufenbloecke, Harry/Marv beziehen ihren Sweep-Fokus aus dem Plankopf, Frank arbeitet gegen dieselben Zusicherungen, der Architekt schreibt das Abschluss-Doc gegen den Stufenbogen, und der Mensch entscheidet an dieser Datei, was ueberhaupt gebaut wird. Keine Mechanik haengt am Praefix — es steht nur in Vorlagen und Anleitungen (`bootstrap/CLAUDE.md.vorlage`, `bootstrap/TEAM.md`, `bootstrap/roadmap-skizzen.md`, `geteilt/prompts/rolle-architekt.md`, die Entrypoints beider Bahnen, `install.sh`, `lib.sh` sowie mehrere `geteilt/tests/` als Beispielwert) | `Feld B`, 2026-08-27, beim Schreiben der fuenften Kaskade. Voller Hergang: [`plans/meldungen/2026-08-27-kaskaden-plandateien-heissen-ralph-kaskade-n-obwohl-sie-das.md`](meldungen/2026-08-27-kaskaden-plandateien-heissen-ralph-kaskade-n-obwohl-sie-das.md) | **offen, niedrige Prioritaet — reine Semantik, kein Fehlverhalten.** **Vorschlag:** `plans/team-kaskade-N-<thema>.md`, und zwar **nur fuer kuenftige Projekte** (`bootstrap/` + Briefings). Bestandsprojekte behalten ihre Dateinamen; ihr `.ralph-plan` zeigt auf gewachsene Dateien, und beide Formen duerfen nebeneinander bestehen, weil nichts am Praefix haengt |
| BL-201 | **Die Vorsorge gegen den vierten Ausgang fehlt im Briefing der bauenden Rolle — das Kit kennt ihn nur als Nachsorge.** `BL-41` erkennt den vierten Ausgang zuverlaessig und gibt dem Menschen eine Pruefreihenfolge. Die **vorbeugende** Auflage steht in der `CLAUDE.md`-Vorlage (*„Der Smoke-Test laeuft im **Vordergrund**, nie als Hintergrund-Task und nie mit einem Wakeup darauf"*) — im Briefing `rolle-ralph.md` (39 Zeilen) steht sie **nicht**: kein Treffer fuer Vordergrund, Hintergrund, Wakeup, Monitor oder 43. Die Rolle erreicht die Regel damit nur ueber einen Abschnitt, der ihr einleitend sagt, er betreffe groesstenteils die Shell und nicht sie. Die Doku-Hygiene sieht die Briefings ausdruecklich als den Weg vor, auf dem eine Rolle ihre Auflagen erhaelt. **Nebenbefund, der die Diagnose verteuert:** Die Selbstpruefung meldete im selben Atemzug „Smoke-Test ist ROT", obwohl der Baum gruen war — sie wertete den **unfertigen** Hintergrundlauf als roten Test. Die anschliessende Pruefreihenfolge bietet dann zwei Zweige, die **beide einen roten Baum voraussetzen**; der zweite („Stufe neu bauen") haette eine fertige, bezahlte Stufe weggeworfen | `Feld B`, 2026-08-27 — Bestandsprojekt im vierten Kaskadenlauf (Windows, pwsh-Bahn, Python+Electron, ~120 Tests). Die Stufe war vollstaendig gebaut, aber uncommittet; das Log meldete `subtype: success` ohne Promise, 59 Turns, 1,93 USD verloren. Aufgeloest hat den Fall **allein** das Feld `result` im Lauf-Log, das die Anleitung nicht erwaehnt — dort stand die Ursache woertlich. Voller Hergang: [`plans/meldungen/2026-08-27-die-vorsorge-gegen-den-vierten-ausgang-fehlt-im-briefing-der.md`](meldungen/2026-08-27-die-vorsorge-gegen-den-vierten-ausgang-fehlt-im-briefing-der.md) | **erledigt 2026-08-28 — beide Teile, mit einer benannten Abweichung vom Vorschlag.** **(1)** Die Auflage steht jetzt in **vier** Briefings (`ralph`, `axel`, `harry`, `marv`), fuenf Zeilen, mit Grund (*headless, keine Benachrichtigung, das Log meldet trotzdem *`subtype: success`), Preis (19,47 USD) und **Ausweg** — das Zeitlimit wird auf `TEAM_SMOKE_TEST_TIMEOUT` aus `{{KONFIG}}` gehoben, statt in den Hintergrund auszuweichen (die Naht zu `BL-207`: eine Auflage, die nicht einhaltbar ist, erzeugt genau das Verhalten, das sie verbietet). **Frank steht bewusst NICHT dabei, und das ist die Abweichung:** Er traegt sie seit `BL-207` **woertlich zur Laufzeit** in Schritt 1 seines Auftrags (`$SMOKE_SUFFIX`) — genau weil er den Smoke-Test oefter faehrt —, und sein Briefing liegt **exakt** auf dem harten 45-Zeilen-Limit. Das Limit ist keine Formsache: Ein Briefing liegt in JEDEM Prompt seiner Rolle. Ein Zusatz, der eine andere Zusicherung bricht, ist keiner — dieselbe Abwaegung, die `test_bl165` fuer `BL-167` schon einmal getroffen hat. Ein eigener Fall sichert die Ausnahme ab, sonst waere sie ein Loch. **(2)** Die Nachsorge behauptet nicht mehr, als sie weiss: Die Meldung zum vierten Ausgang nennt jetzt das Feld `result` — den einzigen Ort, an dem im Feld die Ursache stand und den die Anleitung nirgends erwaehnte —, und die Rot-Meldung der Selbstpruefung ist **relativiert** (*„Miss im VORDERGRUND nach, bevor du den Befund verwendest"*). Ohne das liest sich ein Befund als sicher, der es nicht ist, und schickt den Menschen in den Pruefzweig, der eine fertige, bezahlte Stufe wegwirft. Beides auf BEIDEN Bahnen, mit Gleichstands-Fall. **Beim Bauen fast eine andere Zusicherung gerissen:** Der erste Wurf haengte allen fuenf Briefings einen 13-zeiligen Absatz an und schob vier ueber das Limit — der Fall dagegen steht jetzt in der Datei, damit die naechste Ergaenzung es sofort merkt statt erst im Suite-Lauf. Regressionstest `test_bl201_vordergrund_auflage_in_allen_briefings.py`, **23 Faelle**. **Gegenprobe gefahren:** gegen den alten Stand fallen 21 von 23; die zwei gruenen sind die Gegenrichtungen (Frank hatte die Auflage zur Laufzeit schon, das Limit galt schon) |
| BL-200 | **Ein `--update` traegt neue Konfigurationswerte nicht ins Feldprojekt nach — und liefert damit Fixes aus, die es im selben Zug wieder aufhebt.** Der Grundsatz *„`--update` fasst `team.config.*` nicht an"* ist richtig; die Datei traegt Projektwerte. Es gibt aber **keinen Schritt, der die SCHLUESSELMENGE abgleicht**: Ein Wert, den die Vorlage neu einfuehrt, erreicht eine bestehende Installation nie — und wird auch nicht gemeldet. **Gemessen im Feld, nicht vermutet:** Nach dem Update fehlten in `team.config.ps1` **vier** Werte, die die Vorlage inzwischen setzt: `TEAM_MELDUNG_TOOL` (`BL-182`) — **hart**, `Team-Werkzeug ''` laeuft in `& $null` und bricht ab, fuer JEDES Verb des Rueckkanals; `TEAM_KIT_PFAD` (`BL-153`) und `TEAM_FELD_KUERZEL` (`BL-168`) — **still**, `--kit ''` bzw. `--kuerzel ''`; `TEAM_CLAUDE_BIN` (`BL-173`) — **gnaedig**, `lib.psm1` faellt auf `'claude'` zurueck. **Der Fall ist deshalb schaerfer als er aussieht:** `BL-182` ist im Kit vollstaendig gebaut und mit fuenf Pruefrichtungen belegt — im Feld hat das Update den Fix ausgeliefert und den Fehler mit **woertlich derselben** Meldung wiederhergestellt, nur eine Zeile tiefer (`lib.psm1:146` statt `kit-melden.ps1:37`). Jeder kuenftige Fix, der einen neuen Konfigurationswert einfuehrt, ist im Feld ab dem Update **ein Regress statt eines Fixes**, und welche Klasse er trifft, entscheidet der Zufall. **Der Schnitt, der hier fehlt, steht im Haus:** `Python-Abgleich` (`BL-133`) ist woertlich derselbe Gedanke — *„`--update` fasst `team.config.*` nicht an" ist richtig; „sieht sie gar nicht an" war es nicht* —, nur fuer **einen** Wert. **Nebenbefund an genau dieser Funktion:** Die kopierbaren Zeilen, die sie ausgibt, nennen `TEAM_BEUTEBUCH_TOOL` und `TEAM_KOSTEN_TOOL`; `TEAM_MELDUNG_TOOL` ist seit `BL-182` die dritte Zeile derselben Bauart und fehlt dort. **Warum die Suite es nur zufaellig fand:** Gefangen hat den harten Fall ausschliesslich die Gegenrichtung eines mitgelieferten Falls (`test_bl182…::test_die_werkzeugzeile_steht_in_der_konfiguration`, „man darf (1) nicht durch Loeschen gruen machen") — und die gibt es nur, weil dieser eine Fund sie zufaellig brauchte. Fuer `BL-153`, `BL-168` und `BL-173` existiert nichts Vergleichbares; genau diese drei fehlten im Feld **wochenlang unbemerkt**. Der Riegel `test_jeder_konfigurationswert_steht_in_der_exportliste` prueft bereits **eine** Richtung dieser Gattung (*was die Konfiguration setzt, muss die Modulgrenze ueberleben*); die Gegenrichtung — *was die Vorlage setzt, muss die Installation haben* — ist ungeprueft, und sie ist die, die im Feld zuschlaegt | `Feld B`, 2026-08-27 — beim Regressionslauf direkt nach einem `--update`: **ein** roter Fall von 390, `test_bl182_rueckkanal_auf_der_pwsh_bahn.py::test_die_werkzeugzeile_steht_in_der_konfiguration`. Die drei stillen Werte fielen erst beim Nachsehen wegen des vierten auf. Meldung: `plans/meldungen/2026-08-27-ein-update-traegt-neue-konfigurationswerte-nicht-ins-feldpro.md` | **erledigt 2026-08-28 — alle drei Teile.** **(1)** `konfig_abgleich` / `Konfig-Abgleich` in BEIDEN Installern: `--update` vergleicht die `$TEAM_*`-Namen der Vorlage mit denen der installierten Konfiguration und meldet die fehlenden **namentlich**, mit der Zeile aus der VORLAGE daneben (steht darin noch ein Platzhalter, wird das ausdruecklich gesagt). **Gemeldet, nicht repariert.** Ein Wert, der ohne Inhalt HART abbricht, bekommt einen roten Befund — erkannt an der GATTUNG (`*_TOOL`: eine leere Werkzeugzeile laeuft in einen Aufruf ohne Programm) und nicht an einer Namensliste. **(2)** Die Gattung als Test: Was die Bibliothek liest, ohne einen eigenen Rueckfall zu setzen, steht in der Vorlagen-Konfiguration — und die Schluesselmengen beider Bahnen sind deckungsgleich **bis auf zwei begruendete Ausnahmen**, die namentlich mit Grund in der Testdatei stehen: `TEAM_PYTHON` (nur bash — dort erledigt die Wortzerlegung der Shell den Rest) und `TEAM_MELDUNG_TOOL` (nur pwsh — dort braucht es ganze Werkzeugzeilen, `BL-182`). Ein zweiter Fall prueft, ob eine Ausnahme noch gilt; eine Ausnahmeliste, die niemand nachprueft, ist eine Erlaubnis mit unbekanntem Umfang. **(3)** Die kopierbaren Zeilen in `python_abgleich` nennen `TEAM_MELDUNG_TOOL`. Regressionstest `test_bl200_konfig_abgleich.py`, 10 Faelle, mit der Gegenprobe des Eintrags: eine praeparierte Installation ohne den Wert schlaegt namentlich an, dieselbe **vollstaendig** schweigt. Gegenprobe gefahren |
| BL-199 | **Die pwsh-Bahn sieht die Sperre der bash-Bahn nicht — und seit `BL-190` gibt es diesen Fall überhaupt erst.** Beide Bahnen liegen nach einer Installation im **selben** Arbeitsbaum (`BL-126`: jeder Installer schreibt beide Konfigurationen). Die Zusicherung heisst *„eine Pipeline zur Zeit"*, nicht *„eine je Bahn"*. Seit `BL-190` sperrt die bash-Bahn ohne `flock` über `.team-loop.lock.d`; die pwsh-Bahn kennt nur `.team-loop.lock` — an **drei** Stellen: `lib.psm1` (`team_lock`, `FileStream` mit `FileShare::None`), `entry/team-status.ps1` (Zeile ~104, „Pipeline: läuft/idle") und `install.ps1` (Zeile ~1080, der `BL-10`-Schutz vor einem Update in einen laufenden Lauf hinein). Ein bash-Lauf auf einer Windows-Maschine ist für alle drei **unsichtbar**: Der Kontostand meldet *idle*, und `install.ps1 --update` legt uncommittete Dateien in `team/` ab — genau der Schaden, gegen den `BL-10` gebaut wurde. **Der naheliegende Fix trägt nicht, und das ist der eigentliche Inhalt dieses Eintrags:** Die pwsh-Seite kann die hinterlegte PID **nicht auswerten**. **Gemessen am 2026-08-27, nicht vermutet:** Eine laufende Git-Bash meldete `$$` = `15946`; `Get-Process -Id 15946` in PowerShell auf derselben Maschine, zur selben Zeit, fand **nichts**. MSYS führt einen **eigenen Prozessraum**, und seine PID ist keine Windows-PID. Ein `Get-Process`-Test würde damit **jede** gehaltene bash-Sperre als verwaist einstufen — die Zusicherung wäre nicht wiederhergestellt, sondern schriftlich abgeschafft. **Ehrlichkeitshalber:** Der umgekehrte Weg war auch vorher nicht zugesichert. `FileShare::None` wird nur von **Windows** durchgesetzt; unter Linux erzwingt .NET es nicht, und `flock` ist kooperativ. Bahnübergreifend hat die Sperre also **nie** gehalten. Neu ist nur, dass es jetzt zwei verschiedene **Artefakte** gibt und der Fall damit sichtbar wird | Kit, 2026-08-27 — beim Bauen von `BL-190` aufgefallen, als die drei bash-seitigen Aufrufstellen der Frage *„läuft gerade eine Pipeline?"* nachgezogen wurden. Der Eintrag `BL-190` schreibt ausdrücklich *„Was NICHT betroffen ist: die pwsh-Bahn (sie sperrt über einen eigenen Weg)"* — das stimmte für den **Fund** und stimmt für die **Reparatur** nicht mehr, weil sie ein zweites Sperrartefakt eingeführt hat. **Gemessen:** Der PID-Namensraum-Befund oben (`$$` = 15946 in Git-Bash, `Get-Process -Id 15946` in PowerShell leer, beide gleichzeitig auf derselben Maschine). **Nicht aus dem Feld:** Es ist kein Vorfall gemeldet, und der Fall setzt voraus, dass jemand auf einer Windows-Maschine die bash-Bahn **und** die pwsh-Bahn im selben Arbeitsbaum fährt — auf Windows ist die bash-Bahn laut Zwei-Bahnen-Tabelle die zweite Wahl. Das senkt die Wahrscheinlichkeit, nicht den Schaden | **erledigt 2026-08-28 — Variante (a) des Eintrags, nachdem sie nachgemessen wurde.** **Die Entwurfsfrage ist beantwortet und steht geschrieben** (`doku/anhang-a.md`, Abschnitt „Die Reichweite der Sperre"): Sie gilt bahnuebergreifend, MIT benannten Grenzen. **Der PID-Weg ist doch gangbar** — gemessen am 2026-08-28, Hin- und Rueckweg: `/proc/<pid>/winpid` liegt unter Git for Windows vor, und `Get-Process -Id <winpid>` findet den bash-Prozess. Die bash-Bahn legt `winpid` deshalb zusaetzlich zu `pid` ab; die pwsh-Seite wertet sie aus. **Und die Gegenrichtung fiel dabei mit ab:** Ein Schreib-Oeffnen von `.team-loop.lock` scheitert unter Windows mit *„Device or resource busy"*, solange die pwsh-Bahn sie mit `FileShare::None` haelt — `flock` sieht das nicht, das Betriebssystem schon. Damit sehen sich beide Bahnen gegenseitig, ohne dass `FileShare::None` aufgegeben wird; Variante (b) haette genau das gekostet. **`team_pipeline_laeuft` hat jetzt DREI Zustaende** (0 laeuft / 1 nicht / 2 unklar) und existiert erstmals auch auf der pwsh-Bahn; alle drei Aufrufstellen fragen sie: `install.ps1` bricht bei 2 ab (Vorsicht ist beim `BL-10`-Schutz die richtige Richtung, und die Meldung nennt das Entfernen von Hand), `team-status.ps1` meldet **unbekannt** statt einer Behauptung. **Was NICHT gilt, steht ebenfalls dort:** Unter Linux setzt .NET `FileShare::None` nicht durch und `flock` ist kooperativ — bahnuebergreifend haelt dort keine der beiden Proben. Regressionstest `test_bl199_sperre_ueber_beide_bahnen.py` (15 Faelle, davon einer die Messung selbst) mit der Gegenrichtung: sauberer Baum schweigt, eine VERWAISTE Sperre blockiert nicht dauerhaft. Gegenprobe gefahren: gegen den alten Stand fallen 12 Faelle |
| BL-198 | **Der README-Wächter deckt die Testzahlen ab, aber nicht die zwei Backlog-Zahlen daneben — und meldet trotzdem „alle Zahlen sind gemessen".** `geteilt/kit-readme-pruefen.py` prüft drei Gattungen, und zwar richtig: Testfälle, Testdateien, installierte Dateien. Alle drei bekommen ihre Sollzahl aus einer **frischen Installation** (`bash/kit-test.sh` Zeile ~354). Zwei weitere Zahlen im selben README behaupten dasselbe über dasselbe Kit und werden von **niemandem** gemessen: die Spanne `BL-1`…`BL-<N>` (Zeile ~343) und die Zahl der Archiv-Einträge (Zeilen ~114 und ~345, zweimal dieselbe Zahl in freier Prosa). Beide sind aus dem Repo in einer Zeile ableitbar — `grep -c '^| BL-' plans/backlog-archiv.md` und die höchste vergebene Nummer über Backlog **und** Archiv. **Nicht vermutet, sondern eingetreten:** Am 2026-08-26 kam `BL-196` dazu, das README nannte weiter `BL-195`, und alle drei Doku-Wächter blieben grün. Gefunden wurde es beim Eintragen von `BL-197` — von Hand, nicht vom Wächter. **Die schärfere Hälfte ist die Schlusszeile.** `main()` hängt jede Zahlenprüfung an ein `if a.<zahl> is not None`, druckt am Ende aber unbedingt `✓ README: alle genannten Pfade existieren, alle Zahlen sind gemessen.` Ohne Argumente — also bei jedem Aufruf von Hand, und genau so wird er nach einer Doku-Änderung aufgerufen — läuft **keine einzige** Zahlenprüfung, und die Erfolgszeile behauptet trotzdem, alle seien gemessen. Das ist die Gattung von `BL-145`: Zwei Aufrufwege desselben Skripts sichern verschieden viel zu, und beide melden dasselbe Grün. **Und es gibt eine zweite Hälfte, die schwerer wiegt als die erste — sie ist ebenfalls `BL-145`s Gattung, nur an einer Stelle, die dort nicht mitkam:** Die drei Zahlen, die der Wächter *kann*, prüft **nur `kit-test.sh`** (Zeile ~354). `kit-test.ps1` prüft das README an **keiner** Stelle. Auf einer pwsh-Maschine ist die Drift damit **strukturell unsichtbar**, und auf der bash-Maschine kostet der Nachweis Stunden. **Gemessen am 2026-08-27, nicht vermutet:** Das README nennt `757 Regressionstests` (zweimal, dazu im Badge), `97 Testdateien` und `153 Dateien`; gemessen an einer **frischen Installation** — also so, wie `kit-test.sh` es tut — sind es **973 Fälle**, **113 Testdateien** und **169 Dateien**. Die Badge-Zahl steht seit `6f48dec` (Kit `2.13.1`) unverändert; seither sind **216 Fälle**, **16 Testdateien** und **16 ausgelieferte Dateien** dazugekommen, ohne dass ein Wächter angeschlagen hat. Der Selbsttest der bash-Bahn wäre in Schritt 3 seither **rot** — gefahren hat ihn seit dem 2026-08-24 niemand. **Und ein vierter Fall derselben Gattung stand daneben:** Der Absatz, der die Trägerregel aus `BL-180` erklärt, führte als Gegenbeispiel die nackte Zahl „86 Tests" an — und wurde vom Wächter zu Recht als unqualifizierte Aussage über das Kit gemeldet. Die Regel verletzte ihr eigenes Beispiel, und niemand hat es gesehen, weil niemand den Wächter mit Argumenten gefahren hat | Kit, 2026-08-27 — beim Verbuchen der Feld-E-Meldung zu `BL-197`. Nicht aus dem Betrieb: Beim Nachziehen der README-Zahlen fiel auf, dass die Spanne noch `BL-195` sagte, obwohl `BL-196` seit dem Vortag im Backlog steht — und dass `kit-readme-pruefen.py` das folgenlos durchwinkt und danach „alle Zahlen sind gemessen" druckt. **Gezählt, nicht geschätzt:** Von den fünf Zahlen, die das README über sich selbst behauptet, sind drei gemessen und zwei nicht; die Doku-Wächter laufen nach **jeder** Doku-Änderung, also lief der Wächter über die falsche Zahl mindestens einmal hinweg | **erledigt 2026-08-28 — alle drei Teile.** **(1)** `kit-readme-pruefen.py` misst die zwei Backlog-Zahlen jetzt SELBST aus dem Repo (`backlog_zahlen()`), statt sie sich uebergeben zu lassen: Der Backlog des Kits wird nicht mitinstalliert, und ein Aufrufer, der sie ableiten muesste, koennte es anders. Zwei Gattungen, positiv geprueft — die Spanne erkennt man an ihrem ANFANG (`BL-1`…), damit ein Feldbeleg wie `BL-158`…`BL-168` nicht mitgemeldet wird (`BL-180`). **Der Waechter hat beim ersten Lauf sofort DREI veraltete Stellen gefunden** (199/153/146 statt 207) — der Beleg fuer den Eintrag, gefunden von der Mechanik statt von Hand. **(2)** Die Schlusszeile nennt die gemessenen Gattungen beim Namen und sagt ausdruecklich „KEINE Zahl geprueft", wenn keine lief. **(3)** `kit-test.ps1` prueft das README als eigener Schritt 5/9, mit vier Gegenproben (verfaelschte Testzahl, verfaelschte BL-Spanne, verfaelschte Archivzahl, dazu die Gegenrichtung „das unveraenderte README bleibt gruen"). **(4) Im vollen Suite-Lauf nachgebessert:** Der erste Wurf forderte die zwei Zahlen UNBEDINGT ein — auch bei einem `--readme`, das nicht auf das README des Kits zeigt. Das tut es regelmaessig (beide Selbsttests fahren ihre Gegenproben an einer KOPIE, `BL-180` an einem Fixture aus zwei Zeilen), und der Waechter schlug damit an einer RICHTIGEN Datei rot an — die Bauart aus `BL-180`, ohne Absicht wiederhergestellt. Getrennt sind jetzt die zwei Haelften: ein falscher WERT ist ueberall rot, das EINFORDERN einer fehlenden Zahl gilt nur fuer `KIT/README.md`. Regressionstest `test_bl198_readme_zahlen_vollstaendig.py`, 12 Faelle — die Gegenrichtung braucht ein Mini-Kit im tmp-Verzeichnis (Pruefer + `plans/` + README), weil ein Test am echten README die Regel nur bestaetigen koennte, indem er es verstuemmelt. Gegenprobe gefahren |
| BL-197 | **Die Buchungsregel für eine Sitzung ohne Closeout hängt an einer Erinnerung statt an einem Ereignis — und ihr Ausfall ist im Bericht baulich unsichtbar.** `BL-165` hat die Regel ins Architekten-Briefing gebracht: *„Eine Sitzung ohne Closeout bucht ihre Kosten selbst"*, samt Befehl und Begründung. Der Melder **hat** sie — er ist auf `2.13.1`, er zitiert sie wörtlich, er hat sie verstanden. Sie hat trotzdem an **einem Tag zweimal** nicht gegriffen. **Der Unterschied ist nicht Disziplin, sondern Auslöser.** Ein Closeout hat einen: Die Kaskade ist fertig, der Loop meldet Feierabend, das Briefing verlangt ein Abschluss-Doc, und der Kostenabschluss steht als Punkt 2 in derselben Liste. Eine reine Planungs- oder Nachbesserungssitzung hat keinen — sie **endet einfach**, der Mensch schliesst das Fenster, sobald der Plan committet ist, und in diesem Moment liest niemand mehr eine Regel. **Erschwerend baut das Kit den Fall selbst:** Das Briefing empfiehlt „nach einem gebuchten Closeout eine **neue** Sitzung für die nächste Kaskade" — die Empfehlung erzeugt genau die Sitzung, die die Regel abfangen soll, und beide stehen im selben Dokument. **Der zweite Halbsatz ist der schwerere, und er ist im Quelltext nachgeprüft, nicht geglaubt:** `ledger_pruefen()` P1 stuft eine fehlende `architekt`-Zeile als **Hinweis** ein (`geteilt/tools/kosten.py`, Zeilen ~697–703: *„Legitim, wenn der Architekt fuer diese Kaskade nichts abzurechnen hatte"*). Und der Kontostand zeigt **ausschliesslich** `[WARNUNG]`-Zeilen — `bash/entry/team-status.sh` Zeile ~271 filtert auf `*WARNUNG*`, `pwsh/entry/team-status.ps1` Zeile ~237 auf dasselbe Muster. **Ein Hinweis erscheint im Regelbericht also nie.** Die Schwere ist damit keine Beschriftungsfrage, sie entscheidet zwischen *unsichtbar* und *sichtbar*. An der Stelle steht stattdessen `Architekt K<N> (Churn-Proxy, nicht im Gesamt enthalten)` (`bash/lib.sh` Zeile ~1456, dokumentiert in `doku/faq.md` Zeile ~412) — eine Schätzung, die aussieht wie eine Erfassung. **Abgrenzung zu `BL-193`, denn die beiden sehen sich ähnlich und sind es nicht:** `BL-193` beschreibt die **Messung** — `sitzung-messen --projekt .` liest nur das zuletzt geänderte Transkript, die Aushärtung liegt zwei Sitzungen zurück. Dieser Eintrag beschreibt den **Anlass zu messen**. Beide Wege, die `BL-193` gebaut hat, setzen voraus, dass jemand im richtigen Moment daran denkt; keiner von beiden bringt einen Auslöser mit | `Feld E`, 2026-08-26, beim Öffnen des Closeouts der **siebten** Kaskade (Kit `2.13.1`, Linux, bash-Bahn, Flutter/Dart mit SQLite, Abo-Auth, Ledger seit der ersten Kaskade lückenlos geführt). Das Ledger hatte für diese Kaskade keine `architekt`-Zeile, obwohl der Plan zwei Tage zuvor ausgehärtet und committet war. Die Suche nach dem Grund förderte einen **zweiten** Fall desselben Tages zutage. **Gemessen, nicht geschätzt:** Sitzung A (Nachlauf zur vorigen Kaskade — zwei Handprüfungen am Gerät, ein Hilfsskript auf echte Exit-Codes umgebaut, zwei Meldungen ans Kit) **36,22 USD**; Sitzung B (Aushärtung der nächsten Kaskade — Prototyp-Abgleich und Plandokument) **7,68 USD**; zusammen **43,90 USD** Abo-Gegenwert, die nie im Ledger standen. Beide Sitzungen waren regulär, produktiv und haben committet — keine hat gebucht. **Gerettet wurde der Betrag nur durch einen Zufall:** `sitzung-messen` liest benannte Transkripte, und die zwei Dateien lagen noch da. Der Regelfall ist ein anderer — ohne Argument liest das Werkzeug das **zuletzt geänderte** Transkript, und das ist beim nächsten Closeout ein drittes. Reiht sich in die Grössenordnung aus `BL-193` ein: dort **10,65 USD** und **39 %** der Architektenkosten einer Kaskade, frühere Aushärtungen desselben Projekts zwischen **8,7 und 34,8 USD**. **Lokal nichts gepatcht**, ausdrücklich mit Begründung: Der Fund steckt im Briefing, also im Kit; ein lokaler Eingriff hätte die bekannte Verfallszeit beim nächsten `--update` | **Teile (1) und (2) erledigt 2026-08-28.** **(1)** `ledger_pruefen()` P1 stuft eine **nummerierte** Kaskade mit `ralph`-Zeile und ohne `architekt`-Zeile jetzt als **Warnung** ein — benannte Kaskaden bleiben Hinweis, dieselbe Unterscheidung und derselbe Grund wie in `BL-14`. **Gebuendelt, nicht je Kaskade:** Ein gewachsenes Feld-Ledger, in dem der Architekt nie gebucht hat, erzeugt EINE Warnung mit Zahl und namentlich genannten Kaskaden statt N dauerhaft unaufloesbarer — die Falle aus `BL-14` war von Anfang an mitgebaut. Die Wirkung kommt vom Kontostand, der ausschliesslich `[WARNUNG]` zeigt: derselbe Filter auf **beiden** Bahnen, und genau darum entscheidet die Schwere zwischen unsichtbar und sichtbar. **(2)** Der Kostenabschluss der Sitzung haengt jetzt als **letzter, kopierfertiger Schritt** an der Scharfschalt-Sequenz — einer Pflicht-Ausgabe am Ende JEDER Aushaertung. Damit haengt er an einem **Ereignis** statt an einer Erinnerung. Zwei Befehle, weil der Betrag erst gemessen werden muss; die `BL-165`-Regel wird ausdruecklich **nicht** ersetzt (sie sagt das Warum, die Sequenz das Wann). Regressionstest `test_bl197_architekt_fehlt_ist_eine_warnung.py`, **13 Faelle** — darunter die vier Gegenproben, die der Eintrag woertlich verlangt, jede einzeln zurueckgedreht: eine von sieben ergibt GENAU EINE Warnung mit der 7 namentlich · ein vollstaendig gebuchtes Ledger **schweigt** · `post-7` bleibt Hinweis · sechs von sieben ergeben EINE Warnung, nicht sechs. Dazu die Bahn-Gegenprobe an der Quelle (beide `team-status`-Filter). **Gegenprobe gefahren:** gegen den alten Stand fallen 4 von 10 Faellen in Teil (1) und 3 von 3 in Teil (2); die uebrigen sind die Gegenrichtungen und muessen beidseitig gruen bleiben. **Vier bestehende Faelle mitgezogen** (`test_bl13` dreimal, `test_bl46` einmal): Ihre Fixtures trugen eine nummerierte Kaskade ohne Architekt-Zeile und behaupteten `rc == 0` nur nebenbei — sie pruefen P2/P3 und bekommen die Zeile jetzt, damit sie das pruefen, was sie meinen. **Was offen bleibt:** `BL-193` Weg (2), der Lueckenfinder — er kostet eine Formataenderung am Ledger und ist erst jetzt sinnvoll zu entscheiden, weil Teil (1) einen guten Teil seines Nutzens ohne das Format holt |
| BL-196 | **Die Abgleichsablage aus `BL-178` bleibt liegen, und niemand sagt, dass sie weggeworfen werden darf.** Beide Installer rendern für den Block „Bitte von Hand abgleichen" die Kit-Fassung der abweichenden Dateien in ein Wegwerf-Verzeichnis (`$TMPDIR/team-kit-abgleich-*`) und nennen im Hinweis den Vergleichsbefehl darauf. Aufgeräumt wird **nur, wenn nichts abweicht** (`install.ps1`, `$abgleich -eq 0`); weicht etwas ab — und bei `CLAUDE.md` ist das laut demselben Block ausdrücklich der **Normalfall** —, bleibt das Verzeichnis stehen. Das ist so gewollt: Der Anwender soll den genannten Befehl noch ausführen können. Nur endet die Zusage dort. **Kein Satz sagt, dass die Ablage danach entbehrlich ist**, kein Lauf entfernt eine ältere, und der Hinweis nennt sie nicht als temporär — geprüft: In `install.sh` und `install.ps1` kommt keine Formulierung über Aufräumen oder Löschen vor. **Gemessen, nicht vermutet:** Nach einem Arbeitstag mit Selbsttest-Läufen und Update-Proben lagen **elf** solcher Verzeichnisse in `%TEMP%` (36–60 KB je Stück, also kein Platzproblem — ein Ordnungsproblem). **Warum das trotzdem zählt:** Ein Verzeichnis, dessen Lebensdauer niemand benennt, wird entweder nie gelöscht oder im falschen Moment — nämlich bevor der Anwender den Vergleich gefahren hat. Beides ist vermeidbar, und die Bauart ist dieselbe wie bei `BL-44`: ein Hinweis, der eine Handlung ankündigt, ohne ihren Rahmen zu nennen. **Eine zweite Hälfte, und sie gehört zur Gattung von `BL-145`:** `kit-test.sh` räumt seine eigenen Abgleichsablagen nach jedem der beiden Update-Läufe ausdrücklich weg (Zeilen ~538 und ~603, mit einer Schranke gegen einen leeren Pfad); `kit-test.ps1` tut das **nicht**. Der pwsh-Selbsttest hinterlässt damit je Lauf mindestens ein Verzeichnis — bei einem Lauf, der ohnehin eine Stunde dauert und deshalb wiederholt wird, summiert sich das | Kit, 2026-08-26 — beim Aufräumen nach den `BL-145`-Läufen aufgefallen. Nicht aus dem Betrieb, sondern beim Nachsehen, was die Läufe in `%TEMP%` hinterlassen hatten: elf `team-kit-abgleich-*` neben drei `team-kit-test-*`. Die drei Selbsttest-Ordner sind erklärt (sie bleiben bei einem **roten** Lauf absichtlich zur Ansicht liegen, so steht es in der Schlusszeile); die elf anderen sind es nicht | **Teile (1) und (2) erledigt 2026-08-28, Teil (3) bewusst nicht.** **(1)** Beide Installer sagen jetzt, WAS die Ablage ist (*„eine KOPIE zum Nachlesen im Temp-Bereich, kein Teil deines Projekts"*) und stellen den Loeschbefehl kopierfertig daneben — `rm -rf` bzw. `Remove-Item -Recurse -Force`, je in der Schreibweise IHRER Bahn; ein `rm -rf`, das Windows nicht kennt, waere die Bauart `BL-44` ein zweites Mal. **(2)** `kit-test.ps1` raeumt seine eigenen Ablagen weg wie `kit-test.sh` — mit derselben Schranke gegen einen unerwarteten Pfad UND mit der Gegenrichtung: Wird nichts erkannt, faellt der Schritt rot, statt still nichts zu tun und gruen auszusehen. **(3) NICHT gebaut**, und der Eintrag sagt es selbst (*„erst danach, und nur wenn es sich lohnt"*): Dass ein Update die Ablage des vorigen entfernt, kostet Zustand ueber Laeufe hinweg und loest ein Problem, das (1) und (2) bereits kleinhalten. Regressionstest `test_bl196_abgleichsablage_hat_ein_ende.py`, 12 Faelle auf beiden Bahnen — darunter die Gegenrichtung, dass die Ablage NICHT vorzeitig geloescht wird (sie ist die einzige Stelle, an der die Kit-Fassung sichtbar ist, `BL-4`). Gegenprobe gefahren |
| BL-193 | **Die Aushärtungs-Sitzung einer Kaskade ist mit dem dokumentierten Ablauf strukturell nicht buchbar.** `sitzung-messen --projekt .` liest **immer nur das zuletzt geänderte Transkript**. Zum Zeitpunkt des Closeouts ist das die Closeout-Sitzung selbst; die Aushärtungs-Sitzung liegt zwei Sitzungen zurück, wird nie gelesen, und **keine Meldung weist auf sie hin**. **Der Ablauf erzwingt das, er lässt es nicht bloss zu:** (1) Der Architekt härtet die nächste Kaskade aus — laut Kit ausdrücklich eigene Handarbeit und laut Briefing das Teuerste, was er tut. (2) Der Stakeholder legt den Zeiger um und startet den Lauf; zwischen (1) und (2) gibt es **keinen** Buchungsschritt, denn das Briefing verbietet den Kostenabschluss in einer Loop-Stufe ausdrücklich. (3) Der Closeout läuft danach in einer **neuen** Sitzung, so verlangt es „Ein Closeout je Sitzung". Damit ist die Aushärtungs-Sitzung zum Buchungszeitpunkt **niemals** die zuletzt geänderte. Wer sich an den dokumentierten Ablauf hält, verliert sie. **Und zwar lautlos:** Das Ledger ist in sich konsistent, `--ledger-pruefen` meldet nichts (es hält archivierte Rohlogs gegen das Ledger, und für eine interaktive Sitzung gibt es keinen Rohlog), `--budget` zeigt eine plausible Summe. Der Fehlbetrag ist nur sichtbar, wenn jemand die Transkript-Ablage von Hand gegen das Ledger hält. **Wo es steckt:** `geteilt/prompts/rolle-architekt.md`, Abschnitt „Nach jedem Lauf (Closeout, Pflicht)", Punkt 2. Er nennt zwei Quellen — die Laufkosten und „meine eigene Sitzung" —, und „meine eigene Sitzung" ist im Closeout-Kontext eindeutig die Closeout-Sitzung. Die Aushärtungs-Sitzung derselben Kaskade wird an **keiner** Stelle erwähnt. Der Abschnitt kennt die verwandte Falle bereits, aber nur in der **anderen** Richtung: „Ein Closeout je Sitzung" warnt davor, dass zwei Closeouts in **einer** Sitzung denselben Betrag doppelt buchen (`BL-116`). Der umgekehrte Fall — **eine** Kaskade über **mehrere** Sitzungen, von denen nur die letzte gemessen wird — steht nicht da. Verwandt mit `BL-165`: Beide beschreiben Symptome derselben Ursache — **die Messung hängt an „zuletzt geändert", die Buchhaltung an „Kaskade"** | `Feld E`, 2026-08-25, beim Kostenabschluss der sechsten Kaskade (Kit 2.13.0, Linux, bash-Bahn, Flutter/Dart, Abo-Auth für alle Rollen). **Gemessen, nicht geschätzt:** In diesem Projekt waren es **10,65 USD Abo-Gegenwert** — **39 % der gesamten Architektenkosten dieser Kaskade**. Gebucht wurden sie nur, weil der Architekt die Transkript-Ablage von Hand durchsucht und `sitzung-messen` mit einem ausdrücklich benannten Pfad aufgerufen hat; **das steht in keinem Briefing**. Kein Einzelfall dieses Laufs: Die Aushärtungen früherer Kaskaden derselben Installation liegen zwischen **8,7 und 34,8 USD**. Ob eine Installation überhaupt betroffen ist, hängt allein daran, ob die Aushärtung zufällig in derselben Sitzung lag wie der vorige Closeout — bei zwei Kaskaden war das so, bei dieser nicht | **offen — zwei der drei Wege sind gebaut, der dritte ist der teure.** **Was am 2026-08-26 schon da war:** Weg (3), „die Aushärtung buchen, wo sie entsteht", ist mit `BL-165` am selben Tag ins Architekten-Briefing gekommen — *„Eine Sitzung ohne Closeout bucht ihre Kosten selbst"*, samt dem Befehl `--architekt-abschluss <USD> <domaene> "Kaskade N+1 geplant" --kaskade <N+1>`. Der Melder ist auf Kit **2.13.0**, also auf der Fassung davor; für ihn ist das die Reparatur, für das Kit war es schon geschehen. **Was heute dazugekommen ist — Weg (1), und er ist mehr als eine Sofortmaßnahme:** Die Vorbeugungsregel hilft nur, wer **vor** der Aushärtung steht. Wer beim Closeout steht, hat sie hinter sich; ihm nützt sie nichts, er braucht den **Rückweg**. Punkt 2 des Closeout-Abschnitts sagt jetzt ausdrücklich, dass **„meine eigene Sitzung" ZWEI sind** — Aushärtung und Closeout —, dass `sitzung-messen --projekt .` nur die letzte davon liest, und wie die andere nachzuholen ist: über ihren **Pfad**, gebucht mit `--addieren`. Mit der Gegenrichtung daneben, denn ohne sie wäre der Rückweg schädlich: Wurde die Aushärtung an ihrem Ende gebucht, steckt sie schon im Ledger und darf **nicht** ein zweites Mal drauf (`BL-116`). Dazu die Größenordnung aus dem Feld (10,65 USD, 39 % der Architektenkosten einer Kaskade) und der Satz, der den Fund erst gefährlich macht: **Nichts meldet diese Lücke** — das Ledger ist stimmig, `--ledger-pruefen` schweigt mangels Rohlog, `--budget` zeigt eine plausible Summe. Vier Fälle in `geteilt/tests/test_bl165_bedienanleitung_nennt_die_regeln.py` halten den Absatz fest; jede der vier Gegenproben greift (Rückweg ohne `--addieren` · Pfad-Hinweis raus · Doppelbuchungs-Warnung raus · Verweis auf die Vorbeugungsregel raus). **Ein Umstand, der beim Bauen Zeit gekostet hat und hier festgehalten gehört:** Der erste Entwurf prüfte den **ganzen** Punkt 2 auf `--addieren` und `Pfad`. Beides steht dort schon aus anderem Grund — `--addieren` für den Nachlauf einer Rolle —, und **drei von drei Gegenproben blieben grün**. Die Zusicherung gilt dem Absatz, also wird jetzt der Absatz geschnitten. **Was offen bleibt: Weg (2), der Lückenfinder** (`kosten.py sitzung-lueckenpruefung --projekt .`) — alle Transkripte auflisten, die jünger sind als die älteste Ledger-Zeile und in keiner Buchung vorkommen. Er ist der einzige der drei, der die Lücke **maschinell** findet statt sie einer Regel anzuvertrauen, und damit der gründlichste; er ist auch der teuerste, weil `--akteur-abschluss` dafür die gemessene Transkript-ID in der Ledger-Zeile ablegen müsste. Heute steht sie dort nur, wenn der Architekt sie von Hand in die Notiz schreibt — das ist eine **Formatänderung am Ledger** und braucht ihre eigene Gegenprobe gegen gewachsene Ledger aus dem Feld. **Gegenprobe für den offenen Teil:** Eine Ablage mit **zwei** Transkripten, von denen das ältere die Aushärtung ist und in keiner Ledger-Zeile vorkommt — der Lückenfinder muss genau dieses eine melden und das jüngere nicht. Und die Gegenrichtung: Ist beides gebucht, muss er schweigen |
| BL-194 | **Der Selbsttest fährt zwei Konfigurationen — und beide sind Python. Die ganze Gattung „eine Annahme des Kits, die stillschweigend Python heißt" ist damit nur im Feld zu finden.** `kit-test.sh` installiert das Kit zweimal in ein Wegwerf-Repo, einmal mit den Auslieferungswerten und einmal mit angepasster Konfiguration. Angepasst werden dabei **Ordner**, nicht **Sprachen**: `TEAM_TEST_ORDNER` wandert, die Reproducer-Konvention, die Test-Endung und der Smoke-Test bleiben pytest. Genau deshalb ist `BL-171` (zwei Zusicherungen verdrahten `.py` und `strict=True`) nicht im Selbsttest aufgefallen, sondern erst, als ein Dart-Projekt seine Suite fuhr — und dort als **Sockel von sechs bis sieben dauerhaft roten Fällen**, also an der Stelle, an der die Suite als Signal wertlos wird. **Der Aufwand ist der Punkt, an dem zu entscheiden ist:** Eine dritte, wirklich nicht-python Konfiguration braucht ein Wegwerf-Projekt mit fremdem Test-Läufer — oder, billiger und fast so gut, eine Konfiguration, die nur die **Marken** verdreht (Endung, Reproducer-Muster, Smoke-Befehl), ohne dass ein zweiter Interpreter installiert sein muss. Die zweite Bauform fängt die Gattung „Literal statt Konfigurationswert", und mehr war an `BL-171` nicht dran | Kit, 2026-08-26 — beim Abtragen von `BL-171` und `BL-191` festgehalten. Beide sind in einer **Installation** rot geworden und in der **Kit-Ablage** unsichtbar geblieben; `BL-191` auf jedem POSIX-Wirt, `BL-171` in jedem Nicht-Python-Projekt. Der Selbsttest hat in beiden Fällen nichts gemeldet | **offen.** Erst entscheiden, welche der beiden Bauformen gefahren wird (echtes fremdes Test-Paket oder verdrehte Marken), dann bauen. **Gegenprobe, die den Fix erst gültig macht:** `.py` und `strict=True` in den beiden Zusicherungen wieder als Literal einsetzen — die neue Stufe muss rot werden, die bestehenden zwei Konfigurationen müssen grün bleiben |
| BL-169 | **`src/` + `tests/` als ausgelieferte Ordner-Defaults machen Reproducer-Tests in jedem Stack mit paketgebundener Testsuche unausführbar — und zwar stumm.** `bootstrap/team.config.sh` belegt `TEAM_PRODUKTIVCODE` mit `src/` und `TEAM_TEST_ORDNER` mit `tests/` vor. Das trägt, solange der Testläufer die Dateien am **Pfad** findet (pytest). Es trägt **nicht**, sobald er sie am **Paket** findet: Dart/Flutter sammelt ausschließlich innerhalb des Pakets und ausschließlich unterhalb von `test/`; liegt das Paket unter `src/`, liegt der vom Kit vorgesehene Testordner **außerhalb** davon. Dieselbe Bauart bei Cargo (`tests/` relativ zu `Cargo.toml`), Go (Paketverzeichnis) und Gradle (`src/test/`). **Die zweite Hälfte ist vom Ordner unabhängig und wiegt schwerer:** Der Läufer nimmt nur Dateien mit einem bestimmten Namensmuster — `_test.dart` bei Dart, `_test.go` bei Go. Die Konvention des Kits lautet `tests/test_hm<nr>_<stichwort>.py` und steht wörtlich in `bootstrap/CLAUDE.md.vorlage` (Fund-Format **und** der Absatz zur Benennung nach der Fund-Nummer), in `bootstrap/beutebuch.md` und in `geteilt/prompts/rolle-harry.md`/`rolle-marv.md`. Buchstabengetreu auf Dart übertragen ergibt das `test_hm36_foo.dart` — einen Namen, den der Läufer ignoriert. **Folge in beiden Hälften identisch:** Franks regelkonform abgelegter Reproducer wird nie ausgeführt, der Smoke-Test bleibt grün, das Beutebuch zeigt einen Fund mit Reproducer, geprüft wird nichts. Das ist derselbe Schaden wie `BL-15` (Backtick-Regel) und `BL-28` (`strict`-Marker), nur eine Ebene tiefer: Dort war der Test da und stumm markiert, hier wird er gar nicht erst gefunden. **Nicht betroffen ist der Extraktor:** `DATEI_RE` in `team/tools/beutebuch.py` akzeptiert jede Endung und hat den umgestellten Dart-Pfad im Lauf korrekt als `test/hm6_stichwort_test.dart` erkannt — der Substanz-Anker trägt, allein die Vorgabewerte und Beispiele tragen nicht | `Feld E`, 2026-08-23, vom Architekten beim Aushärten der **ersten** Kaskade gefunden — durch Lesen der Kopplung zwischen Konfiguration und Testläufer, **bevor** ein Lauf startete. Dasselbe Zeitfenster wie `BL-149`: Sobald ein Projekt seine Ordner einmal richtig gesetzt hat, ist der Default für immer unsichtbar, und ein laufendes Projekt kann den Fehler gar nicht mehr erleben. Getroffen wird ausschließlich der Erstlauf | **erledigt 2026-08-28 — beide Wege, wie der Eintrag sie verlangt (*„Beides zusammen, nicht eines davon"*).** **(1) Der erkannte Stack:** Beide Installer halten die Interview-Antwort `TECH_STACK` gegen den Testordner und melden den Widerspruch — Dart/Flutter, Cargo/Rust, Go und JVM/Gradle, je mit den ueblichen Ordnern UND dem Namensmuster (`<stichwort>_test.dart`, `_test.go`). **GEMELDET, NICHT REPARIERT**, und die Meldung sagt das selbst: Der Stack steht als freie Prosa da, ein Installer, der daraus stillschweigend Ordner umschreibt, raet — und ueberschriebe womoeglich eine bewusste Antwort. Dieselbe Entscheidung wie in `BL-200`. Die Meldung nennt auch die **stumme Folge**, denn daran haengt der Wert des Eintrags: Franks Reproducer wird nie ausgefuehrt, der Smoke-Test bleibt **gruen**, das Beutebuch zeigt einen Fund mit Reproducer. **(2) Der unerkannte Stack:** Die Kopplung steht jetzt im Kommentar am `TEAM_TEST_ORDNER` beider Konfigurationsvorlagen — Pfadsuche gegen Paketsuche, mit denselben vier Gattungen und dem Namensmuster als zweiter, schwererer Haelfte. **End-zu-end gefahren, nicht nur getestet:** frische Installation mit `TEAM_INIT_TECH_STACK="Flutter Dart sqlite"` und den Vorgabewerten — die Meldung erscheint mit `lib/`, `test/` und `<stichwort>_test.dart`. **Und die Gegenrichtung**, ohne die es keine Gegenprobe ist: `"python3 tkinter sqlite"` und `"TypeScript React Vite"` erzeugen **null** Meldungen — ein Waechter, der immer anschlaegt, ist keiner (`BL-14`). Regressionstest `test_bl169_paketgebundener_stack.py`, **11 Faelle**, alle elf fallen gegen den alten Stand. **Was bewusst offen bleibt, und der Eintrag verlangt es ausdruecklich:** die Gegenprobe am **LAEUFER** — eine frische Installation fuer einen paketgebundenen Stack, in der der konfigurierte Smoke-Test die Reproducer-Datei nachweislich AUSFUEHRT. Sie braucht Dart, Cargo oder Go auf dem Wirt; auf dieser Maschine liegt keiner davon. Bis dahin ist die Kopplung **benannt**, nicht **bewiesen** |
| BL-207 | **Die Auflage „Smoke-Test im Vordergrund“ ist nicht erfuellbar, sobald die Suite laenger laeuft als die Vordergrundgrenze des Werkzeugs (120 s) — und die BL-41-Selbstpruefung stellt dann einen ZWEITEN Lauf daneben.** Jede Suite waechst; ab dem Tag, an dem sie die Grenze reisst, laeuft jede bauende Rolle regelmaessig in den vierten Ausgang. **Zweiter, gefaehrlicherer Befund:** Die `BL-41`-Selbstpruefung startet den Verifikationsbefehl bedingungslos ein zweites Mal, ohne zu pruefen, ob bereits ein Lauf laeuft. Zwei gleichzeitige Testlaeufe kollidieren (Datenbankdateien, Ports, App-Nutzerverzeichnisse) — die Selbstpruefung meldet **ROT** fuer einen Baum, der allein gefahren gruen ist, und schickt den Menschen per `BL-61`-Text ausdruecklich auf die falsche Faehrte (Testaufbau). Wer ihr glaubt und neu baut, wirft bezahlte, fertige Arbeit weg | Feld B, 2026-08-28, Closeout einer Kaskade — **gemessen, nicht vermutet**: In EINEM Lauf dreimal getroffen, woertlich im Feld `result` der Logs (Bau-Rolle letzte Stufe, Fixer-Versuche 1 und 2 desselben Fundes), zusammen **4,9480 USD** = 32 % der Rollenkosten des Laufs. Die beiden Fixer-Versuche wurden per Rollback verworfen und als Fehlversuche gezaehlt, obwohl der Fix inhaltlich fertig war; der erfolgreiche dritte Versuch unterscheidet sich sachlich nicht vom ersten. Suite dort 149-220 s, allein gefahren gruen (199 passed) | **erledigt 2026-08-28 — beide vorgeschlagenen Richtungen gebaut.** Meldung liegt: [`2026-08-28-die-suite-ist-laenger-als-die-vordergrundgrenze-der-bauenden.md`](meldungen/2026-08-28-die-suite-ist-laenger-als-die-vordergrundgrenze-der-bauenden.md). **Verhaeltnis zu `BL-201`:** Dieselbe Bauform, aber `BL-201` hat sie zweimal mit einer **schaerferen Auflage** beantwortet — dies ist der Beleg, dass Schaerfe nicht hilft, weil es kein Disziplinproblem ist. Eine Auflage, die die Rolle nicht einhalten KANN, erzeugt genau das Verhalten, das sie verbieten soll. `BL-204`/`BL-205` grenzen an, treffen aber die Bedienbarkeit der Fixphase. **(1) Die Auflage traegt jetzt eine Zahl:** `TEAM_SMOKE_TEST_TIMEOUT` (Default **600 s**) steht in beiden `team.config.*` **und** hat einen Bibliotheks-Default — nach `BL-200` die „gnaedige" Klasse, ein bestehendes Projekt bekommt sie beim Update nicht als Leerwert. Genannt wird sie im **Prompt**: in `SMOKE_ZEILE` (Ralph) und **in `SMOKE_SUFFIX`**, dem einzigen, was Frank ueber den Smoke-Test liest — genau die Luecke, die den haerter betroffenen der beiden Rollen traf. Dazu die Regeldatei-Vorlage und das Regel-Inventar. **(2) Die Selbstpruefung stellt keinen zweiten Lauf mehr daneben:** `team_smoke_parallel_lauf` erkennt einen laufenden Verifikationslauf an der Prozesstabelle (`Win32_Process` bzw. `ps -eo args=`), meldet **UNBEKANNT statt ROT**, laesst den `BL-61`-Text weg und startet den zweiten Lauf gar nicht erst; die gefundene Kommandozeile steht in der Meldung, damit ein Fehlalarm in einem Blick erkennbar ist. Ist die Prozesstabelle nicht auswertbar (die MSYS-`ps` von Git for Windows kennt kein `-o`), bleibt es beim bisherigen Verhalten — **lieber keine Erkennung als eine falsche**; Windows wird ueber die pwsh-Bahn bedient, dort traegt `Win32_Process` die Kommandozeile. Regressionstest `test_bl207_vordergrund_zeitlimit_und_paralleler_lauf.py` mit **beiden** Gegenrichtungen (roter Baum bleibt rot samt `BL-61`, gruener wird weiterhin quittiert). Gegenprobe gefahren: gegen den alten Stand fallen acht Faelle auf beiden Bahnen. **Was BL-201 davon mit abtraegt:** Punkt (b) der Nachtrags-Messung (Frank kennt die Auflage nicht) ist damit geschlossen. Offen bleibt dort, dass `harry`/`marv`/`axel` die Auflage in ihren Briefings weiterhin nicht nennen |
| BL-208 | **Von den drei Zahlen-Gattungen, die das README ueber sich selbst behauptet, prueft `kit-test.ps1` nur zwei — die Dateizahl liest es aus dem Installer-Log und DRUCKT sie bloss.** `BL-198` Teil (3) hat den README-Schritt auf die pwsh-Bahn gebracht (Schritt 5/9) und dort zwei Gattungen geschlossen: Testfaelle und Testdateien. Die dritte, die Zahl der ausgelieferten Dateien, bleibt ungeprueft: `--dateien` kommt in `pwsh/kit-test.ps1` **nullmal** vor, in `bash/kit-test.sh` dreimal; die pwsh-Fassung zieht die Zeile `Fertig — <N> Dateien geschrieben` aus dem Log und gibt sie als Erfolgsmeldung aus (`kit-test.ps1:215-217`), ohne sie gegen das README zu halten. Die bash-Fassung haelt sie inline dagegen und bricht ab (`kit-test.sh:230-240`). **Damit ist `BL-198` genau um die Gattung unvollstaendig, die den Eintrag ausgeloest hat** — eine Zahl, die niemand nachrechnet, veraltet lautlos. **Zweiter Befund, dieselbe Wurzel:** Die Zahl der Testfaelle ist **koerperabhaengig**. In der Kit-Ablage sind es 1054, in einer frischen Installation 1053; die Differenz ist genau ein Fall, `test_kit_pruefer_ueberlebt_eine_cp1252_ausgabe` ist ueber `geteilt/kit-*.py` parametrisiert (zwei Pruefer im Kit, in einer Installation gibt es `geteilt/` nicht und der Rueckfallwert `("(keiner)",)` liefert einen Parameter). Beide Selbsttests messen die INSTALLATION und haben damit recht; das README trug die KIT-Zahl. Nirgends steht, dass die beiden Koerper verschieden zaehlen — wer von Hand nachmisst, misst im Kit und liegt um eins daneben | Kit, 2026-08-28 — beim Nachholen des ausstehenden `bash bash/kit-test.sh` (der Absatz „Faellig auf der bash-Maschine"). **Gemessen, nicht vermutet:** Der Lauf brach zweimal ab, bevor er Stufe 3 erreichte — einmal an der Dateizahl (README 169, Installation **175**; sechs Dateien seit dem letzten Commit dazugekommen, kein Waechter hat angeschlagen), einmal an der Testfallzahl (README 1054, Installation **1053**, an vier Stellen). Beide Zahlen waren am Vortag auf der pwsh-Bahn gruen gemeldet worden | **erledigt 2026-08-28 — beide Teile, am selben Tag wie der Fund.** **(1)** `kit-test.ps1` liest die Dateizahl des Installers jetzt als ZAHL (`$GeschriebenIst`) und reicht sie als `--dateien` an den Pruefer durch — dieselben drei Gattungen wie auf der bash-Bahn, an EINER Stelle statt an zwei. Dazu die Gegenprobe, die den Zusatz erst gueltig macht (verfaelschte Dateizahl muss rot werden), und die Falle, die der Fix selbst aufgestellt haette: Ist die Zahl nicht lesbar, sagt der Schritt das **laut** (`UNGEPRUEFT (BL-208)`), statt weniger zu pruefen und gruen auszusehen. **(2)** Die Schlusszeile des Pruefers nennt jetzt den **Massstab**, nicht nur die Gattungen: *„die Selbsttests messen an einer frischen INSTALLATION, nicht an der Kit-Ablage — die beiden zaehlen verschieden"*. Ein Satz, der diesen Eintrag ueberfluessig gemacht haette. Mit der Gegenrichtung: Bei einem Aufruf OHNE Zahlen erscheint der Satz **nicht** — sonst behauptete er eine Messung, die nicht stattgefunden hat, also `BL-198` eine Zeile tiefer. Regressionstest `test_bl208_dateizahl_auf_beiden_bahnen.py`, **7 Faelle**; gegen den alten Stand fallen **alle sieben**. **Was diese Faelle NICHT leisten und was deshalb offen bleibt:** Sie pruefen den QUELLTEXT beider Selbsttests gegeneinander — die Bauform, mit der `BL-178` seinen Gleichstand haelt. Der end-zu-end-Beleg der pwsh-Bahn braucht PowerShell 7 auf demselben Wirt und steht im Absatz „Faellig auf der bash-Maschine" neben der `BL-178`-Gegenprobe und der Wurzel-Code-Pruefung aus `BL-155` |

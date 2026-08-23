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

**Stand 2026-08-23 — was zuletzt passiert ist.** Eine Kit-Sitzung auf der
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

**Was das für die Windows-Maschine bedeutet:** Die bash-Bahn ist gefahren
(`kit-test.sh` vollständig grün), die **pwsh-Bahn von `BL-153` ist geschrieben
und nie gelaufen** — sie hängt als Punkt (6) an `BL-146`. `BL-155` und `BL-156`
sind neu und eine andere Klasse: dort fehlt die pwsh-Hälfte ganz.

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
> vom billigsten zum teuersten:
>
> | | Was | Aufwand |
> |---|---|---|
> | `BL-146` | **Einmal `bash bash/kit-test.sh` fahren.** Vier Testfälle und drei Code-Stellen der pwsh-Bahn sind geschrieben und nie ausgeführt — seit `BL-147` dazu die Bahn-Erkennung des Update-Pfads (`Get-KitBahnDateien`, `Test-BahnLiegtDa`, `-BeideBahnen`), seit `BL-150` das neue `team_plankopf_wert` in `lib.psm1` samt zwölf Testfällen und der fett gesetzte Trockenlauf-Plankopf in `kit-test.ps1`, **seit `BL-153` die gesamte pwsh-Hälfte des Rückkanals** (`kit-melden.ps1`/`.cmd`, `{{KIT_PFAD}}` in `Setze-Werte`, die neue Zeile in `team.config.ps1`). Kein Bau, nur Ausführung — und ein fallender Fall ist das **erwartete** Ergebnis eines Erstlaufs | ein Lauf |
> | `BL-155` | **`install.ps1` kennt die Wurzel-Code-Prüfung aus `BL-52` gar nicht.** Kein Erstlauf-Punkt, sondern eine fehlende Hälfte — Bau. Aufgefallen bei `BL-154`, wo die bash-Fassung repariert wurde | Bau, klein |
> | `BL-156` | **`install.ps1` hat kein Gegenstück zu `--hilfe`** — und sein Kopf nennt die drei Bahn-Schalter gar nicht. Wie `BL-155` eine fehlende, keine ungeprüfte Hälfte | Bau, klein |
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
| BL-145 | **`kit-test.ps1` fährt 6 von 11 Schritten und 15 von 127 Einzelprüfungen — und genau diese Lücke hat `BL-136` durchgelassen.** Der Fix zu `BL-136` (`.gitattributes` ins Zielprojekt) ist als „kit-test.ps1 alle 6 Schritte grün (EXIT 0)" nachgewiesen worden. Er war es auch — nur prüft `kit-test.ps1` den Fall gar nicht, an dem er zerbrach: Die `.gitignore`/`.gitattributes`-Zusicherungen des Update-Pfads leben in Stufe 6 von `kit-test.sh` (dort inzwischen 30 Einzelprüfungen), und der pwsh-Selbsttest hat davon eine dünne Fassung. Ergebnis: Der Selbsttest der **bash**-Bahn war rot, während der Nachweis der pwsh-Bahn grün meldete — vier Commits lang unbemerkt (`BL-144`). **Was `kit-test.ps1` gar nicht hat:** Stufe 5 (zweiter Suite-Lauf unter angepasster Konfiguration, `BL-58` — dort fällt eine falsch gesetzte Messstelle auf, die in einer frischen Installation nie auffällt), Stufe 7 (Einzug in eine gewachsene Codebasis, `BL-51`/`BL-52`), Stufe 8 (Abwahl einer Bahn und ihr Rückweg, `BL-119` — **hier liegt seit `BL-129` die Zusicherung, dass eine einbahnige Ablage grün bleibt**), Stufe 9 (Regel-Inventar gegen die Regeldatei, `A.10`/`BL-56`), Stufe 10 (Einrichtungsroutine) und Stufe 11 (Gleichstand der Installer). Die Zahl `$PruefungenSoll = 15` ist dabei selbst ein Absturzschutz und richtig gebaut — sie sichert nur einen viel kleineren Umfang ab, als ihr Name vermuten lässt | Kit, 2026-08-21 — beim Abtragen von `BL-144` als Ursache **hinter** der Ursache ausgewiesen. Gemessen, nicht geschätzt: 6 gegen 11 Schritte, 15 gegen 127 Einzelprüfungen im selben Lauf. Der Befund ist nicht, dass `kit-test.ps1` schlecht gebaut wäre — er ist, dass „grün" auf den beiden Bahnen **verschieden viel bedeutet** und niemand das beim Lesen sieht | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Nicht als „alles portieren" anzugehen: Stufe 9 (Regel-Inventar) ist reines Python und läuft dort ohnehin, Stufe 10 prüft eine Bash-Routine. **Die Reihenfolge folgt der Wirkung:** zuerst Stufe 6 auf den Umfang der bash-Fassung bringen (dort saß `BL-136`/`BL-144`), dann Stufe 8 (die einbahnige Ablage ist auf Windows der **Normalfall**, und `BL-129`s Zusicherung gilt dort bisher unbelegt), dann Stufe 5. **Die Gegenprobe, die es erst gültig macht:** Ein absichtlich zurückgedrehter Fix muss den pwsh-Selbsttest **rot** machen — genau das hat er bei `BL-136` nicht getan. Solange das offen ist, gilt: **Ein Fix an gemeinsamem Code ist erst nachgewiesen, wenn `kit-test.sh` gelaufen ist**, nicht wenn `kit-test.ps1` grün meldet |
| BL-155 | **`install.ps1` kennt die Wurzel-Code-Prüfung aus `BL-52` gar nicht.** Die bash-Fassung meldet beim Update ungeprüften Code in der Projektwurzel („Ungeprueft in der Wurzel: …") und nennt `TEAM_WEITERER_CODE` als Abhilfe. Auf der pwsh-Bahn gibt es diesen Hinweis nicht — ein einbahnig-pwsh installiertes Bestandsprojekt (also genau die Lage von `Feld B`) erfährt nie, dass sein Einstiegspunkt in der Wurzel außerhalb des Prüfumfangs liegt. Das ist **keine** ungeprüfte Hälfte wie bei `BL-146`, sondern eine **fehlende**: Es gibt nichts auszuführen | Kit, 2026-08-23, aufgefallen beim Abtragen von `BL-154`. Dort wurde die Ausnahmeliste der **bash**-Fassung von einer Abschrift auf eine Messung umgestellt; beim Suchen des Gegenstücks in `install.ps1` stellte sich heraus, dass es keines gibt. Bewusst **nicht** mitgenommen, statt sie blind zu schreiben — die Lehre aus `BL-113`/`BL-117`: Ein blind geschriebener pwsh-Zweig wird bei seiner ersten Ausführung auf der fremden Maschine *angepasst* statt gelesen | **offen, Bau auf der Windows-Maschine.** Klein, aber nicht trivial: Die bash-Fassung erkennt einen Entrypoint jetzt daran, dass die Datei in `bash/entry/` oder `pwsh/entry/` liegt (`BL-154`) — die pwsh-Fassung muss dieselbe Regel nehmen, nicht eine zweite Liste, sonst ist die Abschrift bloß umgezogen. **Reihenfolge:** erst `BL-146` (ein Lauf, deckt auf, was sonst noch liegt), dann das hier |
| BL-156 | **`install.ps1` hat kein Gegenstück zum neuen `--hilfe`, und sein Kopf ist zusätzlich unvollständig.** `install.sh` beantwortet seit dem 2026-08-23 `-h`/`--hilfe`/`--help` mit seinem eigenen Dateikopf — die Optionsliste kann also niemand mehr verfehlen, ohne die Datei zu öffnen. Auf der pwsh-Bahn gibt es das nicht: `param()` kennt keinen `-Hilfe`-Schalter, und der `<# … #>`-Block am Dateianfang trägt **kein** `.SYNOPSIS`/`.PARAMETER`, ist also auch keine comment-based help, aus der `Get-Help` eine Liste bauen könnte. **Der zweite Teil wiegt schwerer als der erste** und besteht schon länger: Der Kopf von `install.ps1` erklärt `-NichtInteraktiv`, `-Update` und `-Force` — `-NurBash`, `-NurPwsh` und `-BeideBahnen` stehen nur in `param()`. Sie kommen nicht einmal in der `Aufruf:`-Zeile vor, anders als in der bash-Fassung. Wer unter Windows eine Bahn abwählen oder mit `BL-147` zurückholen will, findet im Skript selbst keinen Hinweis darauf, dass das geht | Kit, 2026-08-23, aufgefallen beim Bau des `--hilfe`-Schalters. Der Anlass war Bedienung, nicht Symmetrie: Es gab keinen Weg, die Optionen von `install.sh` abzufragen, ohne die Datei zu öffnen — und beim Schreiben der Liste fiel auf, dass drei Schalter auf **beiden** Bahnen undokumentiert waren. In `install.sh` sind sie jetzt erklärt, in `install.ps1` nicht. Bewusst **nicht** blind mitgenommen — dieselbe Erwägung wie bei `BL-155`, die Lehre aus `BL-113`/`BL-117` | **offen, Bau auf der Windows-Maschine.** Zwei Hälften, und die zweite ist die dringendere: **(1)** Den Kopf um die drei Bahn-Schalter ergänzen — reine Prosa, aber sie fehlt seit `BL-119`/`BL-147`. **(2)** Einen `-Hilfe`-Switch, der denselben Weg geht wie die bash-Fassung: **den Kopf ausgeben, keinen zweiten Text pflegen**. Zwei Bauarten stehen zur Wahl, und die Entscheidung gehört auf die Maschine, auf der sie laufen kann — den `<# … #>`-Block zur Laufzeit aus der eigenen Datei lesen (`$PSCommandPath`), oder ihn in echte comment-based help umbauen und `Get-Help $PSCommandPath -Detailed` ausgeben. Die zweite ist die pwsh-übliche und bekommt `-?` geschenkt; sie ändert aber die Form des Kopfes, und ob `Get-Help` ihn bei vorangestellter `# Bahn:`-Zeile überhaupt findet, ist eine Frage, die nur ein Lauf beantwortet. **Reihenfolge:** erst `BL-146` (ein Lauf), dann `BL-155`, dann das hier — es ist der billigste der drei und der einzige, an dem niemand scheitert |
| BL-146 | **Vier Testfälle und drei Code-Stellen der pwsh-Bahn sind geschrieben und noch nie ausgeführt worden.** Der Abtrag vom 2026-08-21 ist auf einem Wirt ohne PowerShell 7 entstanden. Alles, was dort nur übersprungen wurde, ist damit eine **Behauptung mit Testkörper**, keine Zusicherung. Namentlich: **(1)** die drei pwsh-Fälle aus `BL-142` — die Sonde, die `Rest-Ohne-Erstes` über den **Syntaxbaum** aus der echten Datei holt und in echtem PowerShell fährt; der **Gegenbeweis**, dass das alte Idiom wirklich einen String liefert; und der Aufruf aus der Doku end-to-end (`--rollen-abschluss <N> <domaene>` mit ZWEI Notizen und **ohne** Modus-Schalter). **(2)** der pwsh-Fall aus `BL-143`, der belegt, dass `Status-ArchitektAbschluss` `--kaskade` und `--auth` durchreicht. **(3)** Drei Code-Stellen, deren bash-Zwilling gelaufen ist und deren pwsh-Fassung nicht: die Platzhalter-Füllung in `install.ps1` (`BL-139`), die `Churn-Proxy`-Beschriftung in `lib.psm1` (`BL-141`) und der `Rest-Ohne-Erstes`-Aufruf in `Status-ArchitektAbschluss`. **(4)** Seit `BL-150` (2026-08-23) das neue `team_plankopf_wert` in `lib.psm1` — es duldet Auszeichnung im Plankopf und trägt jetzt `team_ralph_cap`/`team_budget_empfehlung`, also den Wert, ohne den Ralph gar nicht erst startet. Zwölf Testfälle (`test_bl150_plankopf_auszeichnung.py`, fünf Notationen × zwei Funktionen plus zwei Gegenproben) laufen auf dieser Maschine sichtbar als übersprungen. Dazu der Trockenlauf-Plankopf in `kit-test.ps1`, der jetzt **fett** steht statt blank — der Schritt existiert nur in der pwsh-Bahn, seine Änderung ist hier also durch nichts gedeckt. **(5)** Seit `BL-149` (2026-08-23) die TODO-Weiche in `lib.psm1`, der neue `{{SMOKE_TEST_KONFIG}}`-Platzhalter in `team.config.ps1` und seine Füllung in `install.ps1` — fünf Testfälle laufen hier sichtbar als übersprungen. **Das wiegt schwer**: Ein `install.ps1`, das den neuen Platzhalter nicht füllt, liefert eine `team.config.ps1` mit einem stehen gebliebenen `{{SMOKE_TEST_KONFIG}}` aus — und das ist genau der Zustand, den `BL-119` teuer bezahlt hat. **(6)** Seit `BL-153` (2026-08-23) die **gesamte pwsh-Hälfte des Rückkanals**: `kit-melden.ps1` und `kit-melden.cmd` sind neu und noch nie gestartet worden; `{{KIT_PFAD}}` wird in `Setze-Werte` gefüllt und die Füllung ist nie gelaufen; die Zeile `$TEAM_KIT_PFAD = Team-Wert …` in `team.config.ps1` ist nie gerendert worden. **Derselbe Hebel wie unter (5)**: Füllt `install.ps1` den Platzhalter nicht, liegt `{{KIT_PFAD}}` wörtlich in der ausgelieferten Konfiguration — der Zustand aus `BL-119`. Der Suchlauf, der das fände, ist Schritt 3 von `kit-test.sh`, und `kit-test.ps1` fährt ihn nicht (`BL-145`). Dazu zwei Fälle in `test_bl153_rueckkanal_meldung.py`, die auf Windows **bewusst** übersprungen werden (`skipif os.name == 'nt'`), weil der `gh`-Platzhalter ein `sh`-Skript ist — das Tor „senden geht ohne Bestätigung nicht raus" ist dort also ungeprüft, und es ist die tragendste Zusicherung des Werkzeugs. Und `kit_meldung.py neu` wählt Bahn, Ruf und Endung über `os.name`; der Windows-Zweig dieser Weiche ist nie gelaufen | Kit, 2026-08-21 — beim Abtragen ausgewiesen statt verschwiegen. Auf diesem Wirt melden die Fälle sichtbar `pwsh-Bahn nicht verfuegbar: pwsh nicht installiert` in der Doppelbahn-Quote; sie sind also nicht still übersprungen. Der Punkt ist ein anderer: Ein sichtbarer Übersprung ist ehrlich, aber kein Nachweis | **offen, ein einziger Lauf auf der Windows-Maschine.** Kein Bau, nur Ausführung: `bash bash/kit-test.sh` dort einmal fahren — die Bash-Bahn ist unter Git for Windows verfügbar und fährt **beide** Bahnen; das ist der Lauf, der `BL-137` gefunden hat. **Wenn ein Fall fällt, ist das das erwartete Ergebnis eines Erstlaufs, kein Rückschlag** — die Lehre aus `BL-113` ist genau, dass die erste Ausführung auf der Zielmaschine stattfindet und **gelesen** wird, nicht dass der Test bis dahin perfekt sein muss. Was dabei **nicht** passieren darf: einen fallenden Fall „anpassen", bis er grün ist. Fällt er, ist entweder der Fix falsch oder der Test — und die Antwort steht im Fall selbst, weil jeder von ihnen seine Erwartung ausschreibt. Abtragen heißt hier: gelaufen, gelesen, Ergebnis vermerkt |
| BL-117 | **Der Prompt-Gleichstand ist am QUELLTEXT bewiesen, nicht am LAUF — Drift in den eingesetzten Werten bliebe unsichtbar.** [`test_bl112_prompt_gleichstand.py`](../geteilt/tests/test_bl112_prompt_gleichstand.py) vergleicht die **Prosa** beider Bahnen, nachdem jede Variableneinsetzung zu einem Platzhalter geworden ist. Das trifft den Fall, für den `BL-112` geschrieben wurde (jemand schärft eine Feldlehre in nur einer Fassung nach), und es lässt genau eine Lücke: Setzen die beiden Bahnen in denselben Platzhalter **verschiedene Werte** ein — ein anders abgeleiteter Ordnername, eine Fallunterscheidung, die nur eine Seite kennt, ein `team.config.ps1`, das einen Wert anders vorbelegt —, sind die Prompts verschieden und der Test bleibt grün. Diese Hälfte kann nur ein **Lauf** zeigen | Kit, 2026-08-20 — beim Abtragen von `BL-112` ausgewiesen statt behauptet: Die Fix-Skizze dort sah den Lauf-Vergleich vor, und der braucht **beide** Shells auf **einer** Maschine. Auf der Entwicklungsmaschine ist kein `pwsh` installiert; ein blind geschriebener Test, dessen erste Ausführung auf einer fremden Maschine stattfindet, wird dort „angepasst" statt gelesen — dieselbe Erwägung, die `BL-113` teuer belegt hat (die pwsh-Bahn fiel erst auf der Zielmaschine auf) | **offen, nur auf einer Maschine mit PowerShell 7 zu bauen.** Bauart wie in `BL-112` skizziert: ein `claude`-Stub, der sein `-p`-Argument in eine Datei schreibt statt zu arbeiten (`Schale.claude_stub` kann das Gerüst schon), jede Rolle einmal je Bahn gefahren, die beiden Prompt-Dateien zeichenweise verglichen. **Die Ausnahmeliste ist bereits da** und wird mitbenutzt, samt ihrer Probe gegen unnötige Einträge — der Lauf-Vergleich erbt sie, statt eine zweite aufzumachen. **Gegenprobe, die ihn erst gültig macht:** ein absichtlich abweichend vorbelegter Wert in einer der beiden Konfigurationen, an dem der Test fallen muss. Solange er fehlt, gilt die Zusicherung „gleicher Prompt" ausdrücklich nur für die Prosa |

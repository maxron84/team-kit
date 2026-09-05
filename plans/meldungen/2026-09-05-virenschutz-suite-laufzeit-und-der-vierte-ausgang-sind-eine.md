# Virenschutz, Suite-Laufzeit und der vierte Ausgang sind eine Kausalkette - das Kit behandelt sie als drei Einzelfaelle

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-05-virenschutz-suite-laufzeit-und-der-vierte-ausgang-sind-eine.md
      .\kit-melden.cmd ablegen  2026-09-05-virenschutz-suite-laufzeit-und-der-vierte-ausgang-sind-eine.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-05-virenschutz-suite-laufzeit-und-der-vierte-ausgang-sind-eine.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn (`--nur-pwsh`), Python-Dienst
  plus Electron-Oberfläche, rund 450 Tests, zehnte Kaskade. Auf dem Rechner läuft
  ein Virenschutz eines Drittanbieters, auf den das Baukonto **keinen Zugriff**
  hat (`Get-MpPreference` antwortet `0x800106ba`). Eine Ausnahme für Repo und
  virtuelle Umgebung ist also nicht einrichtbar — das ist für eine
  Firmen-Windows-Installation eher der Normalfall als die Ausnahme.

## Was passiert ist

Diese Meldung beschreibt **einen** Mechanismus, nicht drei Vorfälle. Das Kit
hat für drei seiner Glieder bereits je eine eigene Abhilfe (`Kit-BL-207`,
die Selbstprüfung des vierten Ausgangs, die 429-Behandlung) — aber es sieht
nicht, dass sie zusammenhängen, und deshalb greift keine davon an der Stelle,
an der die Kette anfängt.

### Glied 1 — Auf Windows kostet jeder Testprozess einen Virenscan

Die Prüfstände dieses Projekts starten je Test einen echten
Oberflächen-Kindprozess (Electron) und teils zusätzlich einen echten
Sprachlaufzeit-Kindprozess. Unter Windows gibt es kein `fork`; jeder Start ist
ein vollständiger Prozessstart samt Abbildladen, und der Echtzeitschutz scannt
dabei jedes Mal mit.

**Wie teuer ein Start ist, lässt sich auf dieser Maschine NICHT über die
Differenz zweier Läufe bestimmen** — das ist selbst ein Befund. Drei
Vordergrundläufe am selben Tag:

| Lauf | Tests | Dauer |
|---|---|---|
| erster | 422 | 294,80 s |
| zweiter, am Ende eines dreistündigen Bau-Laufs | 451 | **492,79 s** |
| dritter | 453 | **378,55 s** |

Der dritte ist bei **mehr** Tests **114 s schneller** als der zweite: **Die
Suite streut um rund 30 %**, je nachdem, was sonst auf der Maschine läuft. Aus
den ersten beiden Läufen hatte ich zunächst „6,8 s je zusätzlichem Test"
abgeleitet — **diese Zahl ist widerrufen**, sie war eine Gerade durch zwei
Punkte.

**Belastbar ist nur, was INNERHALB eines Laufs gemessen wird**, und das genügt
für den Befund: `--durations=30` zeigt am selben Lauf eine Prüfstands-Datei mit
fünf Tests und **fünf** Starts bei **42 s** gegen eine Datei mit **einem**
Start und Messung in einer Fixture bei **13,75 s Setup** (Tests danach im
Millisekundenbereich). Der Preis hängt an der Zahl der **Starts**, nicht an der
Zahl der Tests — und die Streuung zwischen Läufen ist ein zweites Problem
derselben Ursache: Wer 20 Prozessstarts je Lauf hat, hängt an der Tagesform des
Virenscanners.

### Glied 2 — Die Suite wächst mit STARTS, nicht mit Tests

`--durations=30` am selben Lauf zeigt beide Seiten nebeneinander:

- Eine Prüfstands-Datei mit fünf Tests, von denen **jeder** den
  Oberflächenprozess neu startet: **42 s**.
- Eine andere Prüfstands-Datei, die alle ihre Zusicherungen aus **einem**
  Start misst (Messung in einer Fixture, Assertions danach): **13,75 s
  Setup**, die Tests selbst dann im Millisekundenbereich.

Diese Gegenüberstellung stammt aus EINER Messung und ist damit streuungsfrei. Sie ist auch die Erklärung für einen scheinbaren Widerspruch, an dem dieses
Projekt zwei Kaskaden lang falsch geplant hat: Eine Kaskade legte vier
Prüfstands-Dateien nach und die Suite wurde **schneller**, was die lineare
Prognose „N Dateien = N × Startzeit" zu widerlegen schien. Sie war nicht
widerlegt, sondern falsch parametrisiert — die vier Dateien teilten sich ihre
Starts.

### Glied 3 — Der Loop fährt die Suite bis zu zweimal je Stufe

Das ist der Punkt, an dem aus einem Projektproblem ein **Kit**-Problem wird.
Je Stufe läuft der Verifikationsbefehl

1. **von der bauenden Rolle**, weil die Stufenverifikation ihn verlangt, und
2. **noch einmal von der Selbstprüfung des vierten Ausgangs**, unmittelbar
   danach, im selben Arbeitsverzeichnis, auf demselben Stand.

Die Selbstprüfung meldet das sogar wörtlich mit `… Smoke-Test läuft …`. Sie
misst damit exakt das, was die Rolle Sekunden zuvor gemessen hat. **Bei einer
Suite von acht Minuten und vier Stufen sind das rund 32 Minuten reine
Doppelmessung je Lauf.**

Belegt am Lauf dieser Kaskade:

```
[21:28:03] === PHASE 1: Ralph (Bau der Kaskade) ===
Stufe 1 … 2,0356 USD   (Commit 21:53)
Stufe 2 … 2,2854 USD   (Commit 22:18)
Stufe 3 … 9,3226 USD   (Commit 00:06)
Stufe 4 … 2,5412 USD   (Commit 00:22)
[00:31:10] Lauf gestoppt
```

**3 Stunden 3 Minuten Wanduhrzeit für 16,19 USD Modellkosten.** Die Kosten sind
das Maß für die Denkzeit; sie entsprechen grob 40 Minuten davon. Der Rest —
über zwei Stunden — ist Warten auf die Suite.

### Glied 4 — Je länger die Suite läuft, desto lastempfindlicher wird sie

Zwei aufeinanderfolgende Läufe endeten im **vierten Ausgang** („Stufe fertig,
Quittung fehlt"). Der zweite davon so:

- Die Selbstprüfung meldete **16 Fehlschläge**, alle in **einer** Prüfstands-Datei
  (Messungen an Oberflächenzuständen).
- Dieselbe Datei allein gefahren: **23 passed in 13,07 s**.
- Die volle Suite unmittelbar danach, im Vordergrund und ohne Nebenlast:
  **451 passed, 0 failed in 492,79 s**.

Es war Last, kein Regress. Die bauende Rolle hat das **selbst korrekt
diagnostiziert** — Gegenprobe auf den Vorstand, zweiter Lauf mit einem
*anderen* Fehlschlags-Subset — und daraufhin regelkonform kein Promise gegeben,
weil ein Fund dieser Kategorie laut Regelwerk nicht an die bauende Rolle geht.
Das Verhalten der Rolle war also richtig. **Trotzdem stand der Lauf**, und die
Auflösung kostete einen Menschen drei Diagnoseläufe und eine Handquittung.

### Glied 5 — Die vorhandenen Abhilfen greifen alle hinter der Ursache

- `TEAM_SMOKE_TEST_TIMEOUT` (Default 600 s, aus `Kit-BL-207`) verhindert, dass
  die Rolle die Suite als Hintergrundlauf startet. Es ist ein **Deckel**, keine
  Bremse: Bei 493 s bleiben 107 s Puffer, und die Suite wuchs an einem einzigen
  Tag um 198 s. Es gibt **keine Warnung**, wenn ein Lauf sich der Grenze nähert
  — der Übergang von „läuft" zu „bricht ab" ist unangekündigt.
- Die Selbstprüfung des vierten Ausgangs erkennt den Ausgang zuverlässig, ist
  aber selbst der zweite Suitenlauf aus Glied 3.
- Nichts im Kit adressiert Glied 1 und 2.

## Wo es steckt

- **`team/lib.psm1` / `team/lib.sh`** — der Verifikationsbefehl kennt genau
  **eine** Form (`TEAM_SMOKE_TEST`). Es gibt keinen Begriff für „schnelle
  Teilmenge je Stufe, vollständiger Lauf am Phasenende".
- **Die Selbstprüfung des vierten Ausgangs** (aufgerufen aus den bauenden
  Entrypoints) — sie startet den Verifikationsbefehl neu, statt das Ergebnis
  des Laufs zu verwenden, den die Rolle gerade gefahren hat.
- **`TEAM_SMOKE_TEST_TIMEOUT`** in der Bibliothek — Deckel ohne Frühwarnschwelle.
- **Die Einrichtung** (`--init`/`--update`) — sie prüft auf Windows nicht, ob
  Repo und virtuelle Umgebung vom Echtzeitschutz ausgenommen sind, und sagt
  auch nicht, dass es diesen Hebel gibt.

## Warum das jede Installation trifft

Jede Installation auf **Windows mit aktivem Echtzeitschutz** zahlt Glied 1 —
und das ist die Standardkonfiguration eines Firmenrechners, also vermutlich die
Mehrheit der pwsh-Bahn. Glied 3 trifft **jede** Installation unabhängig von der
Plattform: Die Doppelmessung ist Kit-Mechanik, nicht Projektsache. Sie ist nur
dort unauffällig, wo die Suite Sekunden braucht — genau dann, wenn ein Projekt
noch klein ist. Das Problem wächst also mit dem Erfolg des Kits im Projekt und
schlägt zu, wenn am meisten auf dem Spiel steht.

Besonders unangenehm: Die drei vorhandenen Abhilfen erzeugen zusammen den
Eindruck, das Thema sei behandelt. Ein Deckel, eine Selbstprüfung und eine
Fehlerklasse — jede für sich richtig gebaut, alle drei hinter der Ursache.

## Was ich schon versucht habe

- **AV-Ausnahme:** ausgeschlossen, kein Zugriff auf den Virenschutz. Das ist
  keine Nachlässigkeit dieses Projekts, sondern die wahrscheinliche Lage jeder
  verwalteten Firmeninstallation — der Vorschlag „nimm dein Repo aus dem Scan"
  taugt deshalb nicht als Kit-Antwort.
- **Diagnose statt Vermutung:** Die Zahlen oben stammen aus drei Läufen im
  Vordergrund ohne Nebenlast plus einem Lauf mit `--durations=30`. Erst diese
  Messung hat die Ursache von „die Suite ist halt lang" auf „jeder
  Kindprozessstart kostet 6,8 s" verschoben.
- **Im Projekt geplant** (das ist Projektarbeit und gehört nicht ins Kit, steht
  hier nur als Beleg, dass die Ursachenzuordnung trägt): Prüfstands-Starts je
  Datei bündeln, danach die Ablageorte je Worker isolieren und parallelisieren.
  Erwartung nach der Messung: von 493 s auf rund 70 s.

## Vorschläge

Nach Wirkung sortiert, alle vier unabhängig voneinander umsetzbar:

1. **Die Doppelmessung abschaffen.** Die Selbstprüfung sollte das Ergebnis des
   Verifikationslaufs verwenden, den die Rolle gerade gefahren hat, statt ihn
   zu wiederholen. Wo das nicht geht, sollte sie es wenigstens **melden**
   („zweiter Suitenlauf, weil das Ergebnis der Rolle nicht vorliegt") — dann
   sieht der Betreiber, wofür seine Wartezeit draufgeht. Das ist der einzige
   Vorschlag, der ohne jede Projektarbeit sofort die halbe Wartezeit spart.
2. **Zweistufige Verifikation als Kit-Begriff**, etwa `TEAM_SMOKE_TEST_SCHNELL`
   neben `TEAM_SMOKE_TEST`: je Stufe der schnelle Befehl, am Ende der Bauphase
   und vor der Übergabe der vollständige. Heute muss jedes Projekt das selbst
   erfinden — und wer es erfindet, schwächt dabei unbemerkt die
   Stufenverifikation, weil es keine Kit-Regel dafür gibt, wann der volle Lauf
   verbindlich ist.
3. **Flaky vom Regress trennen, bevor der Mensch geweckt wird.** Meldet die
   Selbstprüfung einen roten Baum, könnte sie die roten Dateien **allein**
   wiederholen und den Unterschied berichten. Genau diese Handbewegung hat den
   Fall oben aufgelöst, und sie ist mechanisch. Heute steht in der Ausgabe der
   richtige Rat an den Menschen — aber ausführen muss ihn der Mensch, mitten in
   der Nacht, nach drei Stunden Lauf.
4. **Frühwarnung statt Deckel.** `TEAM_SMOKE_TEST_TIMEOUT` sollte bei
   Überschreiten eines Anteils (etwa 75 %) warnen und die gemessene Dauer
   nennen. Ein Projekt sieht sonst erst am Abbruch, dass es die Grenze reißt —
   und dann steckt es mitten in einer Kaskade.

Zusatz für die Windows-Dokumentation: Der Zusammenhang „ein Testprozessstart =
ein Virenscan" gehört in die Einrichtungshinweise der pwsh-Bahn, zusammen mit
dem Hinweis, dass Prüfstände mit eigenem Kindprozess je **Start** zahlen und
nicht je Test. Wer das früh weiß, baut seine Prüfstände von Anfang an
gebündelt — das kostet beim Bauen nichts und ist später eine eigene Kaskade.

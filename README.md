[![Linux — verifiziert](https://img.shields.io/badge/Linux-verifiziert-2ea44f?style=flat-square&logo=linux&logoColor=white)](doku/einrichtung.md#belegstand)
[![Windows WSL2 — hergeleitet](https://img.shields.io/badge/Windows_WSL2-hergeleitet-dfb317?style=flat-square&logo=windows&logoColor=white)](doku/einrichtung.md#belegstand)
[![Windows nativ — im Feld gelaufen](https://img.shields.io/badge/Windows_nativ-im_Feld_gelaufen-2ea44f?style=flat-square&logo=powershell&logoColor=white)](doku/einrichtung.md#belegstand)
[![macOS — nicht belegt](https://img.shields.io/badge/macOS-nicht_belegt-9f9f9f?style=flat-square&logo=apple&logoColor=white)](doku/einrichtung.md#belegstand)

[![Version 2.13.1](https://img.shields.io/badge/Version-2.13.1-007ec6?style=flat-square)](CHANGELOG.md)
[![Regressionstests 1220](https://img.shields.io/badge/Regressionstests-1220-2ea44f?style=flat-square&logo=pytest&logoColor=white)](geteilt/tests)
[![Selbsttest 11 Stufen](https://img.shields.io/badge/Selbsttest-11_Stufen-2ea44f?style=flat-square)](bash/kit-test.sh)
[![Lizenz MIT](https://img.shields.io/badge/Lizenz-MIT-007ec6?style=flat-square)](LICENSE)

[![Projekt-Stack agnostisch](https://img.shields.io/badge/Projekt--Stack-agnostisch-2ea44f?style=flat-square)](#grenzen)
[![Antrieb — Nutzen je Token](https://img.shields.io/badge/Antrieb-Nutzen_je_Token-8957e5?style=flat-square)](#der-antrieb-nutzen-je-token)
[![Modelle agnostisch](https://img.shields.io/badge/Modelle-agnostisch-8957e5?style=flat-square)](#modelle--agnostisch-aber-nicht-anspruchslos)
[![Agenten-CLI nur Claude Code](https://img.shields.io/badge/Agenten--CLI-nur_Claude_Code-fe7d37?style=flat-square&logo=anthropic&logoColor=white)](#grenzen)
[![Lokale Modelle Fernziel](https://img.shields.io/badge/Lokale_Modelle-Fernziel-fe7d37?style=flat-square)](#modelle--agnostisch-aber-nicht-anspruchslos)
[![Binary nicht geplant](https://img.shields.io/badge/Binary-nicht_geplant-e05d44?style=flat-square)](#grenzen)

> **Der Farbcode ist der Belegstand des Kits, nicht die Wunschliste:**
> 🟢 im Feld belegt · 🟡 hergeleitet und an der Maschine geprüft ·
> 🟠 gebaut oder gewollt, aber nicht abgenommen · 🔴 nicht vorhanden ·
> ⚪ nicht belegt. Woher die Einstufung kommt, steht im
> [Belegstand](doku/einrichtung.md#belegstand) und unter [Grenzen](#grenzen).

![T.E.A.M. — Toll, ein anderer macht's. Sechs Rollenkarten im Terminal-Look:
Ralph Wiggum (Bau-Loop), der Architekt (Plan & Closeout), Frank der Fixer
(Ad-hoc-Fixes) — die drei dürfen Code schreiben; Harry (Red Team Security),
Marv (Red Team Chaos) und Axel Foley (Forensik) sind read-only. Darüber der
Leitsatz: Finder ≠ Fixer.](team-banner.webp)

# T.E.A.M.-Starterkit

Ein vollständiges KI-Rollenteam auf Knopfdruck in ein Software-Projekt —
frisch angelegt **oder seit Jahren gewachsen**.

## Was das ist — und für wen

**Was das ist.** Kein Chat-Assistent und kein Autopilot, sondern ein
**Regiepult**. Sechs KI-Rollen mit harten Auflagen, ein Loop, der einen
geschriebenen Plan Stufe für Stufe abarbeitet — **ein Commit je Stufe** —, und
eine Buchführung, die hinterher zeigt, was jede einzelne Stufe gekostet hat. Du
tippst den Code nicht; du entscheidest, **was** gebaut wird, urteilst am
Ergebnis und gibst die nächste Stufe frei.

**Für wen.** Für **erfahrene Entwickler** — nicht, damit sie mehr Code lesen,
sondern damit sie weniger müssen. Das T.E.A.M. ist eine
**Abstraktionsschicht**, kein Beiwerk zum Selbertippen: Du entscheidest,
**was** gebaut wird, und urteilst am **Ergebnis** — trägt die Stufe ihre
Zusicherung, ist der Red-Team-Fund echt oder Rauschen, behebt Franks Fix die
Ursache oder das Symptom, stimmt der Preis? Die Rolle dabei ist die eines
**fachlich orientierten Stakeholders**: Product Owner, Chefentwickler, Tech
Lead.

**Warum trotzdem „erfahren"?** Weil jede Abstraktionsschicht irgendwann klemmt.
Wer den Diff nie lesen **könnte**, kann einen Fehler des Teams nicht von einem
Fehler der eigenen Vorgabe unterscheiden — und beurteilt dann nur noch, ob es
sich gut anhört. Der Unterschied ist der zwischen *„ich lese den Diff nicht"*
(Normalbetrieb, völlig in Ordnung) und *„ich könnte ihn nicht lesen"* (die
eigentliche Betriebsbedingung). Das tragende Prinzip **Finder ≠ Fixer** endet
bei einem Menschen, der den Fund *beurteilen* muss; kann er das nicht, wird das
Beutebuch zur Ablage statt zur Entscheidung, und das Team baut zuverlässig,
ausdauernd und teuer am Ziel vorbei.

**Warum es das gibt.** Der Antrieb ist **Kosten/Nutzen**, nicht Bequemlichkeit —
agnostisch gesagt: **Nutzen je Token**. Das ist der Unterschied zum Bauen über
ein oder mehrere Chatfenster, und es ist derselbe Maßstab, der später für ein
**lokales Modell offline** gilt. Ausgeführt unter
[Der Antrieb](#der-antrieb-nutzen-je-token).

## Schnellstart

```bash
git clone https://github.com/maxron84/team-kit.git ~/Source/team-kit
cd ~/Source/team-kit
bash bash/kit-einrichten.sh ~/Source/mein-projekt
```

`kit-einrichten.sh` prüft die Maschine (Bordmittel, Zeilenenden, Dateisystem,
Auth) und übergibt dann an `install.sh`. Wer die Maschine schon eingerichtet
hat, ruft den Installer direkt auf: `bash bash/install.sh ~/Source/mein-projekt` —
oder, nach `--verknuepfen`, von überall mit
`bash ~/.claude/scripts/team-init.sh <zielpfad>`.

**Windows** geht denselben Weg, aber **in einer WSL2-Distro** und mit dem Repo
im Linux-Dateisystem. Die ganze Routine für beide Plattformen, mit IDE (VS
Codium bzw. VS Code) und Agenten-Werkzeug, steht in
[doku/einrichtung.md](doku/einrichtung.md).

Ein Befehl, ein kurzes Aufnahme-Interview, danach liegen 186 Dateien im
Zielprojekt: der gehärtete Bau-Loop, das Read-Only Red Team, der Fixer, der
Forensiker, die Kostenmechanik, die Bootstrap-Dateien, die Bedienanleitung
`TEAM.md` und 1220 Regressionstests.

**Stand: Version 2.13.1** (2026-08-25). Drei Fehlerbehebungen aus dem Feld,
ausgelöst durch eine Frage statt durch eine rote Zeile: „Hängt der Installer
beim Selbsttest?" Er hing nicht — er war **stumm** (`BL-176`), und ein stummer
Lauf ist von einem hängenden nicht zu unterscheiden. Beim Nachsehen lag
darunter der schwerere Fund: **`TEAM.md` fiel durch jedes Update** (`BL-175`),
die Bedienungsanleitung eines aktualisierten Projekts blieb auf dem Stand des
Einzugstags. Dessen Rest wurde `BL-177`: Ein Projekt, das vor `BL-139` einzog,
behält seinen kaputten Regeltext — beide Installer melden das jetzt, ohne ihn
anzufassen.

**Der Nachweis aus 2.13.0** (2026-08-25) steht unverändert: Der
Selbsttest des Kits ist auf einer echten Windows-Maschine vollständig
durchgelaufen — **11 von 11 Stufen, 141 Prüfungen grün**. Bis dahin war die
pwsh-Bahn an mehreren Stellen geschrieben und nie ausgeführt worden (`BL-146`),
also eine Behauptung mit Testkörper.

**Der Ertrag waren die sechs Läufe davor.** Der Erstlauf hat sechs Einträge
erzeugt, und fünf davon sind auf einem Linux-Wirt prinzipiell unsichtbar: zwei
Werkzeuge, die unter der Windows-Codepage auf ihrer **Erfolgs**-Spur starben;
eine Vorflug-Prüfung, die eine Maschine für unbereit erklärte, auf der die
native Bahn tadellos läuft; ein `--verknuepfen`, das „✓ Verknüpft" meldete und
eine **Kopie** anlegte; eine Syntaxprüfung, die null statt achtzehn Dateien sah;
und ein Gleichstands-Prüfer, der **an seinem eigenen Befund starb**, weil `diff`
mit 1 endet, wenn es etwas findet. Keiner der fallenden Fälle wurde grün
gedreht.

**Offen sind 4 Einträge** — keine Reste dieser Version, sondern zwei
Meldungen aus dem Feld und zwei eigene Bauvorhaben:
[plans/backlog.md](plans/backlog.md). Abgetragenes steht in
[plans/backlog-archiv.md](plans/backlog-archiv.md) (151 Einträge).

---

## Inhalt

> **Zum ersten Mal hier? → [doku/einrichtung.md](doku/einrichtung.md).**
> Klonen, Maschine einrichten, in ein Projekt einbinden — für **Linux** und für
> **Windows mit WSL**, mit IDE- und Werkzeug-Beispielen, einer Gegenprobe und
> elf Fehlerbildern. Dort steht auch die Trennlinie, die für dieses Kit
> tragend ist: **was Pflicht ist und was nur Beispiel.**

**Diese Seite:**

| Abschnitt | Worum es geht |
|---|---|
| [Was das ist — und für wen](#was-das-ist--und-für-wen) | Regiepult statt Autopilot — und die Betriebsbedingung dahinter |
| [Was das T.E.A.M. ist](#was-das-team-ist) | Die sechs Rollen und das Prinzip *Finder ≠ Fixer* |
| [Der Antrieb](#der-antrieb-nutzen-je-token) | Nutzen je Token: vier Hebel, die Gegenrechnung zum Chatfenster, die Rolle von Git |
| [Modelle](#modelle--agnostisch-aber-nicht-anspruchslos) | Zwei Stufen statt Modellnamen, sechs vorausgesetzte Fähigkeiten, Ziel lokal |
| [Herkunft](#herkunft) | Woher der Code kommt und wo er scharf gelaufen ist |
| [Installation](#installation) | `install.sh`, das Aufnahme-Interview, `--update` gegen `--force` |
| [Nach der Installation](#nach-der-installation) | Die sechs Schritte bis zur ersten Kaskade |
| [In ein bestehendes Projekt](#in-ein-bestehendes-projekt) | Schreibzone und Prüfumfang im Bestand (`BL-51`, `BL-52`) |
| [Aufbau des Kits](#aufbau-des-kits) | Welche Datei wo liegt — im Kit und im Zielprojekt |
| [Betrieb](#betrieb) | Befehle und Exit-Codes |
| [Rückkanal Feld → Kit](#der-rückkanal-feld--kit) | Wie ein Fund am Kit zurückkommt — und warum der Mensch sendet |
| [Grenzen](#grenzen) | Was belegt ist und was ausdrücklich nicht |
| [Lizenz](#lizenz) | MIT |

**Die Dokumentation.** `doku/` bleibt im Kit und wird **nicht** mitinstalliert —
die Bedienanleitung fürs Zielprojekt ist `TEAM.md`:

| Datei | Für wen | Inhalt |
|---|---|---|
| **[doku/einrichtung.md](doku/einrichtung.md)** | **wer das Kit auf eine Maschine holt** | **Die Routine: Klonen, Bordmittel, WSL, IDE, Auth, Einbinden, Fehlerbilder, Belegstand** |
| [doku/faq.md](doku/faq.md) | wer beim Aufsetzen oder im Betrieb hängt | Vier ganze Fragen statt Symptomzeilen: CLI nicht gefunden, Exit `42`/`43`, abgewählte Bahn zurückholen, Kosten höher als geschätzt |
| [doku/anhang-a.md](doku/anhang-a.md) | wer wissen will, *warum* es so gebaut ist | Die Warum-Schicht: Bauentscheide und Feld-Betriebslehren (A.0–A.13) |
| [doku/regel-inventar.md](doku/regel-inventar.md) | wer eine Regel der Vorlage ändert | Jede Regel als NORM/HERLEITUNG/HISTORIE, mit Träger und wörtlichem Zitat |
| [CHANGELOG.md](CHANGELOG.md) | wer eine bestehende Installation nachzieht | Jede Änderung mit Begründung und Feldbeleg |
| [CONTRIBUTING.md](CONTRIBUTING.md) | wer einen Fund am Kit zurückmelden will | Der Meldeweg, die Redaktionsregel, was ein Code-PR nachweisen muss |
| [plans/backlog.md](plans/backlog.md) | wer am Kit mitbaut | Offene Punkte (Abgetragenes im [Archiv](plans/backlog-archiv.md)) |
| [plans/windows-nativ.md](plans/windows-nativ.md) | wer die pwsh-Bahn versteht oder erweitert | Der Bauplan der zweiten Bahn: Anlass, verworfene Alternativen, Stufen, Abnahmekriterien |
| [plans/roadmap-skizzen.md](plans/roadmap-skizzen.md) | wer eine Idee sucht statt einer Aufgabe | Ungehärtete Stränge — bewusst noch kein Plan |
| `TEAM.md` | der Stakeholder im Zielprojekt | Bedienanleitung — wird installiert und liegt danach im Projekt |

---

## Was das T.E.A.M. ist

Sechs KI-Rollen unter der Regie **eines** Menschen (des *Stakeholders*):

| Rolle | Aufgabe | Darf Produktivcode ändern? |
|---|---|---|
| **Ralph** | Bau-Loop, arbeitet den Plan Stufe für Stufe ab | ja |
| **Der Architekt** | plant Kaskaden, setzt Caps, macht den Closeout | nur im Ausnahmefall |
| **Frank** | Ad-hoc-Fixes außerhalb des Loops | ja |
| **Harry** | Red Team Security — greift an, fixt nicht | **nein** (Guard) |
| **Marv** | Red Team Chaos — bricht Dinge, fixt nicht | **nein** (Guard) |
| **Axel** | Forensiker für die harten Fälle, starkes Modell | **nein** (Guard) |

Tragendes Prinzip: **Finder ≠ Fixer.** Wer einen Fehler findet, behebt ihn nicht
selbst — das macht Frank. Jede Übergabe läuft über das Beutebuch und bleibt
nachvollziehbar.

## Der Antrieb: Nutzen je Token

**Der eigentliche Antrieb dieses Kits ist Kosten/Nutzen.** Ein Rollenteam mit
Loop ist kein Selbstzweck: **Graphen und Loops sind der heutige Stand der
Technik**, um sich einem guten Ergebnis *iterativ* zu nähern — Schritt für
Schritt, Commit für Commit, mit einer menschlichen Abnahme dazwischen. Kommt
morgen eine bessere Mechanik, wird sie getauscht; das Ziel bleibt.

Bewusst formuliert als **Nutzen je Token**, nicht als „Kosten pro Monat". Wer in
Token rechnet statt in Dollar, hat die Rechnung schon aufgestellt, die für ein
**lokales Modell offline** gilt — dort kostet nicht der Token Geld, sondern
Zeit, Strom und Kontextfenster. Es ist dieselbe Optimierung mit anderen
Einheiten, und deshalb ist das
[Fernziel lokal](#modelle--agnostisch-aber-nicht-anspruchslos) kein Anhängsel,
sondern die Konsequenz: Wer sich heute an ein volles Kontextfenster gewöhnt,
kann später nicht auf ein kleines Modell wechseln. Wer heute mit engen Stufen
auskommt, kann es.

**Vier Hebel — alle gebaut, alle im Feld gefahren:**

| Hebel | Was dahintersteckt |
|---|---|
| **Zwei Stufen statt eines Modells** | Die Rollen kennen keine Modellnamen, sondern `TEAM_MODEL_LOOP` und `TEAM_MODEL_STRONG`. Die **Masse** der Aufrufe (Bau-Loop, Sweeps, Fixes) läuft auf der günstigen Stufe; die starke läuft **nie im Dauer-Loop**, sondern fallweise — ein Fall pro Aufruf |
| **Caps mit zwei Schwellen** | Soft-Cap = Hinweis, Hard-Cap = Airbag. Die Trennung ist eine bezahlte Feldlehre (`HM-32`): Ein zu enger Cap greift **nach** dem bereits bezahlten Aufruf und wirft plausible Arbeit per Rollback weg — er spart nichts, er **vervielfacht** |
| **Messen statt schätzen** | Jeder Aufruf schreibt seinen Preis ins Ledger, getrennt nach API-Geld und Abo-Gegenwert. `--budget` zeigt den Kontostand, `--ledger-pruefen` sucht die Lücken, `kosten.py sitzung-messen` holt die interaktiven Sitzungen nach, die von sich aus keinen Wert melden |
| **Der Commit als Buchungseinheit** | Eine Stufe = ein Commit = eine Ledgerzeile. Damit ist „was hat dieses Feature gekostet" keine Schätzung, sondern eine Abfrage — siehe unten |

### Was das gegenüber einem Chatfenster ändert

In einem Chatfenster wächst der Kontext **monoton**: Jeder Folgeschritt trägt
die gesamte Vorgeschichte mit, auch die verworfenen Zwischenstände. Caching
verbilligt das, aber es schafft es nicht ab. Und am Ende weiß niemand, was
welcher Schritt gekostet hat — im Abo gibt es dafür nicht einmal eine Zahl auf
der Konsole.

Der Loop dreht beides um. Jeder Rollenaufruf ist ein **eigener Prozess** mit
*genau* dem Kontext, den die Stufe braucht: die Regeldatei, der aktive Plan,
die eine Stufe. Was die vorige Stufe an Irrwegen produziert hat, ist nicht
mehr im Kontext — es steht im Commit, wo man es nachlesen kann, wenn man will,
und wo es nichts kostet, wenn man nicht will. Der Preis jedes Aufrufs kommt als
Zahl zurück und landet in der Buchhaltung.

Belegt ist das an `Feld A`: 33 Kaskaden, 157 Stufen, 49 Loop-Läufe,
rund 1265 USD Abo-Gegenwert — **vollständig geledgert**, aufgeschlüsselt bis
auf die Stufe. Nicht, weil die Summe klein wäre, sondern weil sie **bekannt**
ist. Was sich nicht messen lässt, lässt sich auch nicht optimieren; genau
deshalb waren die drei teuersten Kit-Fehler dieses Jahres alle Löcher in der
**Kostenerfassung** und nicht im Bau-Code.

### Warum Git hier mehr trägt als anderswo

**Feine, atomare Commits sind kein Alleinstellungsmerkmal** — im gesamten
Umfeld des agentischen Programmierens gelten sie als empfohlene Praxis, und das
zu Recht. Der Unterschied liegt darin, **wer** sie durchsetzt und **wozu** sie
dienen.

Anderswo ist der Commit eine **Empfehlung an den Menschen**, und der Rückweg
ist typischerweise ein **editor-lokaler Snapshot** — ohne Diff, nicht teilbar,
nicht in der Historie, beim Maschinenwechsel weg. Hier ist der Commit ein
**Zustandsübergang der Maschine** und trägt drei Lasten gleichzeitig:

1. **Bedingung des Fortschritts.** Ralph schaltet `.ralph-state` erst **nach**
   dem Commit weiter. Eine Stufe ohne Commit ist kein halber Erfolg, sondern
   eine eigene, benannte Fehlerklasse mit eigenem Exit-Code (`43`) — weil die
   Verwechslung mit „Fehler" im Feld viermal die bereits bezahlte Arbeit
   gekostet hat (zusammen 19,47 USD).
2. **Buchungseinheit des Geldes.** Ein Snapshot kostet nichts und bucht nichts;
   er ist ein Undo. Ein Commit hier ist die Zeile, an der Ledger, Cap und
   Rollback ansetzen. Deshalb ist auch der Rollback keine kostenlose Geste: Er
   wirft bezahlte Arbeit weg, und genau das ist der Grund, warum die Caps
   großzügig stehen.
3. **Prüfeinheit des Menschen.** Eine Stufe je Commit ist die Menge, die ein
   Stakeholder noch verantworten kann — und die er, wenn es klemmt, als Diff
   auch noch lesen kann. Die Feinkörnigkeit ist keine Ordnungsliebe — sie ist
   die **Portionierung, in der Kontrolle überhaupt ausübbar bleibt**, und damit
   die Verbindung zurück zu „für wen".

**Und die Grenze, damit es keine Sparversprechen gibt:** Das Kit senkt nicht
den Preis pro Token. Es senkt die **Zahl der Token, die für nichts verbrannt
werden** — durch enge Stufen, billige Rollen, abgebrochene Leerläufe und
dadurch, dass doppelte Arbeit überhaupt sichtbar wird. Die 1265 USD aus
`Feld A` sind der Beleg dafür, dass hier gearbeitet wurde, nicht dafür, dass es
umsonst war.

## Modelle — agnostisch, aber nicht anspruchslos

**Das Kit legt sich auf kein Modell fest, weder heute noch künftig.** Die
Rollen-Skripte kennen keine Modellnamen, sie kennen zwei **Stufen**:

| Stufe | Variable | Default | Wer darauf läuft |
|---|---|---|---|
| schwach | `TEAM_MODEL_LOOP` | `sonnet` | Ralph (Bau-Loop), Harry und Marv (Sweep), Frank (Fixes) |
| stark | `TEAM_MODEL_STRONG` | `opus` | Axel (Forensik) — und die Architekten-Sitzung, die du selbst startest |

Beide stehen in [team/lib.sh](bash/lib.sh) und lassen sich pro Lauf
überschreiben (`TEAM_MODEL_LOOP=… ./vollautomatik.sh`). Es sind **Defaults,
keine Voraussetzung**.

Vorausgesetzt werden **Fähigkeiten**, nicht Anbieter. Das Niveau, auf dem sie
heute nachweislich reichen, ist das von **Sonnet** (schwache Stufe) und **Opus**
(starke Stufe). Ein Kandidat muss:

1. **eine große Regeldatei tragen** — `CLAUDE.md` wird bei jedem Rollenaufruf
   geladen (rund 40 KB) und ist die Grundlage jeder Auflage;
2. **Werkzeuge zuverlässig aufrufen** — Dateien lesen und schreiben, Shell,
   Tests starten, über viele Schritte hinweg;
3. **ein Ausgabeprotokoll durchhalten** — jede Rolle quittiert mit einem
   `<promise>`-Marker; wer ihn am Ende eines langen Laufs vergisst, produziert
   genau die Klasse „Arbeit fertig, Quittung fehlt" (`BL-41`);
4. **Auflagen einhalten, die niemand erzwingt** — die Read-Only-Rollen *könnten*
   Produktivcode schreiben; dass sie es nicht tun, ist zuerst Prompt-Disziplin
   und erst danach der Guard;
5. **ohne Rückfragen arbeiten** — die Läufe sind headless, es sitzt niemand
   daneben, der eine Zwischenfrage beantwortet;
6. **mehrstufige Arbeit selbst zu Ende bringen** — eine Stufe umfasst
   Produktivcode *und* die Tests, die sie beweisen.

**Stand heute** laufen alle automatisierten Rollen über **Claude Code**
(`claude -p`), die Weiterentwicklung des Kits selbst ebenfalls. Die eigentliche
Bindung ist dabei nicht das Modell, sondern die **CLI**: `team_claude()` in
`team/lib.sh` ist die **einzige** Stelle im Kit, die sie aufruft — dort hängen
das JSON-Ergebnisformat (`is_error`, `subtype`, `total_cost_usd`), der
Auth-Fallback und die Kostenmechanik dran. Wer das Kit auf eine andere Agenten-
CLI setzt, tauscht diese eine Funktion, nicht die Rollen.

**Das langfristige Ziel ist lokal.** Der Markt der Open-Weights-Modelle wird
beobachtet; sobald dort bezahlbare Fassungen die obigen Fähigkeiten halten,
werden sie **schrittweise von unten nach oben** zum Standard: erst die schwache
Stufe (Bau-Loop, Sweeps, Fixes — die Masse der Aufrufe und der Kosten), später
die starke (Forensik und Planung). Die Reihenfolge ist Absicht: Unten sind die
Aufgaben enger umrissen, die Läufe zahlreicher und ein Fehlschlag billiger; oben
entscheidet sich, ob ein Plan überhaupt taugt. Maßstab für den Wechsel sind
**nicht Benchmark-Zahlen, sondern die Zusicherungen dieses Kits**: `kit-test.sh`
grün, der Guard hält, das Promise-Protokoll wird durchgehalten, und der
Smoke-Test des Feldprojekts bleibt es auch. Bis dahin läuft die Entwicklung mit
den üblichen Cloud-Modellen weiter.

## Herkunft

Der Code stammt aus dem **Ursprungsprojekt**, wo er über **22 Kaskaden**
scharf gelaufen ist (2026-07-10 bis 2026-08-01): reale Red-Team-Funde `HM-1`…`HM-53`,
Frank-Fixes, wirksamer Read-Only-Guard. Er wurde **nicht neu geschrieben**, sondern
übernommen und parametrisiert — die teuer gelernten Details bleiben erhalten.

Seither kommen die Befunde aus dem laufenden Betrieb. **Die Projekte werden
nicht genannt** — für den Beleg zählt nicht, wie sie heißen, sondern was sie
haben und was sie getan haben. Dafür tragen sie feste Kürzel:

> **Zahlen in dieser Tabelle nennen ihren Träger** — „86 Tests in Feld E" oder
> „86 Projekt-Tests", nie bloß die nackte Zahl. Sie beschreiben **fremde** Projekte;
> eine unqualifizierte Zahl ist eine Aussage über das **Kit**, und
> `kit-readme-pruefen.py` prüft sie als solche gegen die gemessene Fallzahl.
> Eine blanke Feldzahl hat `kit-test.sh` Stufe 3 schon einmal nach 45 Minuten
> abbrechen lassen (`BL-180`).

| Kürzel | Profil | Was dort gelaufen ist |
|---|---|---|
| **Ursprung** | Web-Projekt, Linux, bash-Bahn | 22 Kaskaden (2026-07-10 bis 2026-08-01), `HM-1`…`HM-53` — die Quelle des Codes |
| **`Feld A`** | Greenfield, Python mit Spiel-Engine, Linux, bash-Bahn | 33 Kaskaden, 157 Stufen, `HM-1`…`HM-93`, 49 `vollautomatik.sh`-Läufe, rund 1265 USD Abo-Gegenwert — vollständig geledgert (Stand 2026-08-11) |
| **`Feld B`** | Greenfield, Windows 11, **einbahnig pwsh** installiert | Erste Kaskade geplant, gebaut und abgeschlossen (2026-08-21) — der erste vollständige Kostenabschluss eines Projekts überhaupt |
| **`Feld C`** | Fremde, **gewachsene** Codebasis: Python/tkinter, Einstiegspunkt in der Wurzel, `src/`, `bin/`, gewachsene `tests/`, belegtes `plans/` | Gelesen (2026-08-11) und installiert (2026-08-13). **Keine** Kaskade — belegt ist der Einzug, nicht der Betrieb |
| **`Feld D`** | Greenfield, Linux, bash-Bahn: Electron + Python 3 + SQLite — Neubau, dessen tkinter-Vorgänger als reine Lesereferenz danebenliegt | Erste Kaskade geplant und gebaut (2026-08-23), Stufen 1–4 grün, Stufe 5 an der Umgebung blockiert. `BL-149`…`BL-151` — **drei Erstlauf-Funde**, alle aus dem Zeitfenster, das ein laufendes Projekt gar nicht mehr hat |

| **`Feld E`** | Greenfield, Linux, bash-Bahn: Dart/Flutter + SQLite für ein **Android-Tablet** — Neubau, dessen Python/tkinter-Vorgänger (~25.500 LOC, 17 Spec-Dokumente) als reine Lesereferenz danebenliegt | **Zwei Kaskaden geplant, gebaut und abgeschlossen** (2026-08-24): Datenfundament und Einrichtungs-Wizard, zusammen 10 Stufen ohne Fehlversuch, 86 Tests in `Feld E`, 5 Red-Team-Funde, rund 50 USD Abo-Gegenwert — vollständig geledgert. `BL-158`…`BL-168` — **elf Funde**: die ersten acht vor der ersten gebauten Stufe, aus dem Lesen der Kopplungen zwischen Konfiguration, Testläufer und Rollen-Prompt; die letzten drei aus dem Betrieb (Preistabelle, Zeitpunkt der Gegenprobe, Rückkanal). Der erste Stack ohne pytest: Was das Kit an Python-Annahmen mitträgt, wird hier zum ersten Mal sichtbar. Zugleich der erste Beleg für den Rückkanal als Werkzeug statt als Handarbeit |
Ein künftiges Projekt bekommt den nächsten Buchstaben. Aus diesen sechs Quellen
kommen die Backlog-Einträge `BL-1`…`BL-223`; was davon behoben ist, steht im
[CHANGELOG](CHANGELOG.md) und in
[plans/backlog-archiv.md](plans/backlog-archiv.md) (151 Einträge), der Rest in
[plans/backlog.md](plans/backlog.md).

Die konzeptionelle Grundlage steht im LLM-Wiki des Autors
(`../llm-wiki/wiki/vorlagen/claude-md-ki-team.md`) — ein privates
Schwester-Repo, nicht Teil dieses Kits.

## Installation

```bash
# Linux und WSL
bash bash/install.sh <zielpfad> [--nicht-interaktiv] [--update|--force]
                                [--nur-bash|--nur-pwsh|--beide-bahnen]
bash bash/install.sh --hilfe    # alle Optionen mit Erklärung
```

```powershell
# Windows nativ (PowerShell 7, ohne WSL)
pwsh -File pwsh\install.ps1 <zielpfad> [-NichtInteraktiv] [-Update|-Force]
                                       [-NurBash|-NurPwsh|-BeideBahnen]
```

> **Beide Installer erzeugen aus denselben neun Antworten byte-identische
> Bäume** — festgenagelt in `kit-test.sh`, Schritt 11/11. Sie schreiben auch
> **beide** Konfigurationen (`team.config.sh` *und* `team.config.ps1`), damit
> ein auf Linux eingerichtetes Projekt unter Windows nicht ohne Konfiguration
> dasteht. Die pwsh-Bahn ist inzwischen **auf einer echten Windows-Maschine
> gelaufen**, samt einer vollständigen Kaskade (`Feld B`). Was dort noch fehlt,
> ist nicht die Bahn, sondern ihr **Selbsttest**: `kit-test.ps1` fährt 6 von 11
> Stufen und 15 von 127 Prüfungen (`BL-145`). Ein Fix an gemeinsamem Code gilt
> deshalb erst als nachgewiesen, wenn **`kit-test.sh`** gelaufen ist — nicht,
> wenn `kit-test.ps1` grün meldet. Siehe
> [doku/einrichtung.md, *Belegstand*](doku/einrichtung.md#belegstand).

**Nur eine Bahn installieren:** `--nur-bash` bzw. `--nur-pwsh` (PowerShell:
`-NurBash` / `-NurPwsh`). Ein Projekt bekommt dann statt 29 Entrypoints nur
die zehn der gewählten Bahn. **Default ist beides**, und das hat einen Grund:
`team.config.sh` und `team.config.ps1` sind zwei Generate **einer** Quelle
(denselben neun Antworten). Wer nur eine Bahn installiert, hat unter dem
anderen System keine Konfiguration — und schreibt sie irgendwann von Hand.
Genau dort fängt Drift an. Die Abwahl ist deshalb ausdrücklich und kommt vom
Anwender, nie vom Installer.

**Ein Update hält die Bahn** (`BL-147`): Der Installer erkennt eine einbahnige
Ablage an den Dateien, die das **Kit** ausliefert — nicht an Endungen, ein
projekteigenes `deploy.ps1` zählt also nicht — und legt nichts der anderen
Bahn dazu. Bis `BL-147` war es umgekehrt, und im Feld bekam ein reines
Bash-Projekt bei einem Routine-Update **21 ungebetene pwsh-Dateien**.

**Sie ist trotzdem keine Einbahnstraße:** `--update --beide-bahnen`
(`-BeideBahnen`) macht das Projekt vollständig — samt der fehlenden
Konfiguration, erzeugt aus den Werten der vorhandenen, nicht aus den
Auslieferungswerten. Der Rückweg kommt damit vom **Anwender**, wie die Abwahl
selbst. In einem einbahnigen Projekt bleiben die Team-Tests grün; die fehlende
Bahn erscheint als **sichtbarer** Vermerk in der Testzusammenfassung
(„einbahnige Ablage"), nicht als Fehlschlag und nicht als stiller Übersprung.

**Ein bestehendes Projekt auf eine neue Kit-Version heben:** `--update`. Es
fasst **nur** die Infrastruktur an (Entrypoints außer `team.config.sh`,
`team/lib.sh`, `team/redteam.sh`, `team/tools/`, `team/prompts/`,
`team/tests/`) und lässt Ledger, Kaskadenstand, Beutebuch, CHANGELOG, `plans/`,
`CLAUDE.md` und `team.config.sh` unberührt. **Die Bahn ändert es nicht** — eine
einbahnige Ablage bleibt einbahnig (`BL-147`). Zum Schluss meldet es, welche
Doku-Dateien von der Kit-Fassung abweichen — die **Regeln** müssen von Hand
nachgezogen werden, sonst läuft die Doku der Mechanik hinterher.

> ⚠ **`--force` ist kein Update.** Es überschreibt auch Projektdaten:
> `.budget-ledger` wird geleert (Kostenhistorie weg), `.ralph-state` auf `1`
> zurückgesetzt (Kaskadenstand weg), das Beutebuch durch die leere Vorlage
> ersetzt (**alle Funde weg**), dazu `CHANGELOG.md`, `plans/*.md` und
> `team.config.sh` (Smoke-Test weg). Empirisch nachgestellt, siehe `BL-8`.
> `--force` ist nur für eine kaputte **Erst**installation gedacht.

**Voraussetzungen**: Zielpfad ist ein Git-Repository, `claude` im PATH,
Auth eingerichtet (`bash bash/scripts/team-auth-setup.sh`). Geprüft und erklärt
werden sie von `kit-einrichten.sh` bzw. `kit-einrichten.ps1`; die ausführliche
Fassung — Linux, Windows mit WSL und Windows nativ — steht in
[doku/einrichtung.md](doku/einrichtung.md). Welche
**Fähigkeiten** ein Modell mitbringen muss — und warum das Kit trotzdem keinen
Modellnamen kennt — steht oben im Abschnitt **Modelle**.

**Das Aufnahme-Interview:**

Jede Frage kommt mit einer kurzen Erklärung, was sie bewirkt und was ein
falscher Wert kostet. Die Reihenfolge ist Absicht: Erst werden die beiden
**Schreibordner** vergeben, danach erst der Prüfumfang — so ist beim Beantworten
klar, welche Ordner dort nicht mehr hingehören.

| Frage | Default | Bedeutung |
|---|---|---|
| Projektname | Ordnername | erscheint in Berichten und Ledger |
| Ordner mit dem Programmcode | `src/` | **tabu** für Harry, Marv, Axel — und zugleich der **Prüfumfang** des Sweeps |
| Ordner für Tests | `tests/` | wo Reproducer hindürfen (bleibt **deinem** Testrunner) |
| Ordner für Pläne und Berichte | `plans/` | Kaskaden, Beutebuch, Akten, Roadmap — **Schreibzone** der Read-Only-Rollen (`BL-51`) |
| Weiterer Code (außerhalb) | *(leer)* | Leerliste (`main.py bin/`): Code, der mitgeprüft wird, aber nicht unter dem Produktivcode-Ordner liegt. Im neuen Projekt leer, im Bestand entscheidend (`BL-52`). Der Installer listet dazu, was er in der Wurzel gefunden hat |
| Prüfbefehl (Smoke-Test) | *(leer)* | **der wichtigste Wert**, siehe unten |
| Technik in einer Zeile | *TODO-Zeile* | eine Zeile für `CLAUDE.md`, reine Doku |
| Kostenkonten (Domänen) | `produkt` | Arbeitsstränge **dieses** Projekts; eines reicht (`BL-9`) |
| Architekt committet selbst? | `n` | sonst liefert er die Befehle zum Kopieren |

Test- und Plan-Ordner im Prüfumfang nimmt der Installer **wieder heraus** und
sagt warum: Derselbe Ordner kann nicht zugleich tabu und Ablageort sein — sonst
stünde beides im selben Absatz des Rollen-Auftrags.

Der **Smoke-Test** ist der eine Befehl, mit dem eine Rolle feststellt, dass das
Projekt heil ist. Ralph schließt keine Stufe ohne ihn ab, Frank verifiziert keinen
Fix. Gibt es ihn noch nicht, bleibt das Feld leer — die Rollen melden das dann in
jedem Prompt als offenen Punkt, statt still ohne Sicherheitsnetz zu arbeiten.
Ihn nachzuliefern ist typischerweise Stufe 1 der ersten Kaskade.

Der Installer ist **idempotent**: Ein zweiter Lauf überschreibt nichts, sondern
meldet, was bereits vorhanden ist. `--force` überschreibt bewusst.

## Nach der Installation

```bash
# 1. Werte prüfen
$EDITOR team.config.sh          # der EINZIGE Ort für Projektwerte
$EDITOR CLAUDE.md               # TODO-Stellen füllen

# 2. Committen — VOR dem ersten Guard-Lauf!
git add -A && git commit -m "chore: T.E.A.M. eingerichtet"

# 3. Team-Tests (prüft NUR die Infrastruktur, nicht dein Projekt)
./team-test.sh

# 4. Erste Kaskade planen — Sitzung im Projektordner, starke Stufe (Default Opus):
#    "Du bist unser Architekt, lies team/prompts/rolle-architekt.md."

# 5. Scharfschalten und starten
echo plans/team-kaskade-1-….md > .ralph-plan
./vollautomatik.sh

# 6. NACH dem Lauf — Closeout, sonst sind die Kosten blind
./team-status.sh --rollen-abschluss 1 produkt
./team-status.sh --architekt-abschluss <USD> produkt "Kaskade 1 geplant"
```

> **Warum vor dem ersten Lauf committen?** Der Read-Only-Guard betrachtet
> uncommittete Dateien außerhalb der Whitelist als Verletzung und räumt sie weg.
> Im Ursprungsprojekt hat das einmal die gesamte frisch gebaute Team-Infrastruktur
> gelöscht. Seitdem ist der Rollback chirurgisch — aber die Regel bleibt.

## In ein bestehendes Projekt

**Das T.E.A.M. kann sich in eine gewachsene Codebasis einarbeiten** — es braucht
kein leeres Repo. Die Rollen lesen den Bestand, der Architekt plant gegen ihn,
und das Kit legt sich **neben** deinen Code: eigene Entrypoints, ein `team/`-
Namensraum, `TEAM.md`. Deine Ordner werden nicht angefasst, dein Testrunner
bleibt deiner, der Smoke-Test ist im Bestandsprojekt meist schon vorhanden —
genau das Feld, das im leeren Projekt zuerst fehlt.

> **Belegstand.** Die Stellen, an denen die Defaults nur für ein Neuprojekt
> taugten, stammen aus einer fremden Bestandscodebasis (`Feld C`,
> Python/tkinter, Einstiegspunkt in der Wurzel, `src/`, `bin/`, gewachsene
> `tests/`, belegtes `plans/`): erst **gelesen** (2026-08-11 → `BL-51`/`BL-52`,
> gebaut in 2.6.0), dann **installiert** (2026-08-13 → `BL-57`, gebaut in
> 2.8.0). Der Einzug förderte eine Klasse zutage, die kein Codelesen zeigt:
> Die Fragen waren richtig, aber so gestellt, dass sie falsch beantwortet
> wurden. **Noch nicht** gelaufen ist ein scharfer Bestandslauf mit Agenten.

**Zwei Stellen, an denen ein Bestandsprojekt anders liegt:**

| Falle | Warum sie nur im Bestand greift | Was das Kit tut |
|---|---|---|
| **Schreibzone** (`BL-51`) | Die Guard-Whitelist ist **positiv**: Harry, Marv und Axel dürfen Plan- und Test-Ordner schreiben und löschen. Zeigen sie auf ein belegtes `plans/`/`docs/` oder eine gewachsene Suite, haben die drei ausdrücklich als Read-Only geführten Rollen Schreibrecht auf Bestand — **der Guard schlägt dort nie an**. | Der Installer prüft beide Ordner, nennt die gefundenen Dateien samt Folge und bietet einen anderen Ordner an. Wer behält, bekommt den Bestand in `TEAM_*_ORDNER_BESTAND` vermerkt; die Rollen-Prompts nennen ihn als fremdes Eigentum. **Die harte Variante bleibt der eigene, leere Ordner** (`team-plans/`) — nur dort ist die Grenze Mechanik statt Auflage. |
| **Prüfumfang** (`BL-52`) | Der Sweep-Auftrag zeigte auf `TEAM_PRODUKTIVCODE` — **einen einzelnen Ordner**. Im Bestand liegen Einstiegspunkt (`main.py`), Build- und Deploy-Skripte regelmäßig daneben und wurden nie angegriffen. Ein Sweep, der `src/` sauber meldet, sieht dann aus wie ein sauberes Projekt. Das ist **keine** Guard-Lücke, sondern eine Prüfumfangs-Lücke. | Das Interview fragt danach; `TEAM_WEITERER_CODE` (Leerliste, Dateien und Ordner) kommt in Scope-Zeile, eiserne Regel und Franks Fix-Auftrag. **Mitgeprüft heißt genauso tabu**, nicht freigegeben. `--update` erinnert daran, wenn in der Wurzel ungeprüfter Code liegt. |

**Erste Kaskade im Bestand:** den Fokus auf die **Naht** zwischen Neuem und
Gewachsenem legen, nicht auf die neue Mechanik. Feld-Gegenprobe aus zwei
aufeinanderfolgenden Kaskaden (`BL-43`): Der Naht-Fokus brachte fünf Funde,
allesamt Wechselwirkungen; die Vorkaskade mit Fokus auf die neue Mechanik fand
dieselbe Fundklasse **nicht** — sie fiel erst dem Menschen in der Abnahme auf
und kostete vier Fixes außerhalb des Loops.

**Der Rest ist wie im Neuprojekt** — mit einer Betonung: Vor dem ersten
Guard-Lauf committen ist im Bestand keine Formalie, sondern der Unterschied
zwischen „uncommittete Team-Dateien" und „der Guard räumt sie weg".

## Aufbau des Kits

**Die Ablage trennt die beiden Bahnen — ein Blick sagt, was wozu gehört.**
`ls bash/` ist die vollständige Bash-Bahn, `ls pwsh/` die vollständige
pwsh-Bahn. Was in `geteilt/` liegt, gilt für beide und ist bewusst **nicht**
portiert.

```
bash/                   ALLES, was die Bash-Bahn ausmacht
├── install.sh          Der Installer
├── kit-einrichten.sh   Vorflug-Prüfung zwischen Klon und Installation:
│                       Bordmittel, Zeilenenden, Dateisystem (WSL!), Auth —
│                       prüft mit Proben statt Annahmen, kostet nichts
├── kit-test.sh         Selbstverifikation in 11 Stufen: installiert in ein
│                       Wegwerf-Repo, fährt dort die Tests zweimal (Ausliefe-
│                       rungswerte und angepasste team.config.sh), prüft
│                       Update-Pfad, Bestandslage, Bahn-Abwahl samt
│                       Rueckweg, Regel-Inventar und die Einrichtungs-
│                       routine — DAS Gate vor jedem Push
├── lib.sh              Auth, Guard, Budget, 429-Mechanik, Kosten
├── redteam.sh          Gemeinsame Sweep-Logik von Harry und Marv
├── entry/              Entrypoints — landen in der WURZEL des Zielprojekts
│   ├── vollautomatik.sh    Orchestrator: Ralph → Red Team → Frank → Axel
│   ├── halbautomatik.sh    Schrittweise, mit Halt beim Menschen
│   ├── team-status.sh      Kontostand, Pipeline, Beutebuch-Übersicht
│   ├── team-test.sh        Regressionstests der Team-Infrastruktur
│   ├── kit-melden.sh       Rückkanal: Fund AM KIT melden (`BL-153`)
│   ├── ralph.sh frank.sh axel.sh harry.sh marv.sh
│   └── team.config.sh      ALLE Projektwerte an einer Stelle
└── scripts/            Maschinen-Skripte, NICHT installiert
    ├── team-auth-setup.sh  Auth der Agenten-CLI (Beispiel Claude Code)
    └── team-init.sh        Dünner Launcher, für ~/.claude/scripts/

pwsh/                   ALLES, was die pwsh-Bahn ausmacht — spiegelbildlich
├── install.ps1  kit-einrichten.ps1  kit-test.ps1
├── pruefe-windows.ps1  Eigenständige Vorflug-Probe für die Zielmaschine,
│                       hängt an keiner Kit-Datei (kein Gegenstück in bash/)
├── lib.psm1  redteam.ps1
├── entry/              ralph.ps1 + ralph.cmd, frank.ps1 + frank.cmd, …
│                       Die .cmd sind Einzeiler auf die gleichnamige .ps1
└── scripts/            team-auth-setup.ps1  team-init.ps1

geteilt/                Gilt auf BEIDEN Bahnen, bewusst nicht portiert
├── tools/              kosten.py, beutebuch.py, zitat_lint.py,
│                       kit_meldung.py — Ledger,
│                       Beutebuch und Kostenrechnung liegen auf beiden Wegen
│                       in denselben Dateien. Die pwsh-Bahn ist eine zweite
│                       ORCHESTRIERUNG, kein zweiter Zustandscode
├── prompts/            Sechs Rollen-Briefings (inkl. Architekt)
├── tests/              130 Testdateien, 1220 Fälle — der Doppelbahn-Harnisch
│                       fährt jeden Fall gegen BEIDE Bahnen, aus EINEM
│                       Testkörper
├── kit-regelinventar.py  Prüfer für das Regel-Inventar (Stufe 9). Kit-only —
│                       bewacht die Vorlage, nicht die installierte CLAUDE.md
└── kit-readme-pruefen.py Prüfer für dieses README (Stufe 5). Kit-only — jede
                        Zahl gegen die frische Installation, jeder genannte
                        Pfad gegen das Dateisystem

bootstrap/              CLAUDE.md- und TEAM.md-Vorlage, CHANGELOG, Beutebuch, Roadmap, …
plans/                  Roadmap und Backlog DES KITS (nicht die Vorlagen —
                        die liegen in bootstrap/ und werden installiert)
plans/meldungen/        Meldungen fremder Nutzer, je eine Datei — kommen als
                        Pull Request an (`BL-153`), Nummer beim Triage
CONTRIBUTING.md         Der Meldeweg von außen: Redaktionsregel, was ein
                        Code-PR nachweisen muss
doku/anhang-a.md        Die Warum-Schicht: Bauentscheide und Feld-Betriebs-
                        lehren (A.0–A.13). Bleibt im Kit, wird nicht installiert
doku/einrichtung.md     Klonen und Einbinden — Linux und Windows mit WSL,
                        IDE- und Werkzeug-Beispiele, Fehlerbilder, Belegstand
doku/regel-inventar.md  Jede Regel der Vorlage als NORM/HERLEITUNG/HISTORIE,
                        mit Träger und wörtlichem Zitat
doku/faq.md             Ganze Fragen mit ganzer Antwort — Installation der
                        Agenten-CLI, PATH-Fallen, was danach noch fehlt
```

**In der Wurzel liegt kein einziges Skript** — nur README, CHANGELOG, LICENSE
und die vier Ordner oben. Wer eine `.sh` sucht, schaut in `bash/`; wer eine
`.ps1` sucht, in `pwsh/`. Ein Namenspaar wie `ralph.sh` ↔ `ralph.ps1` liegt in
**gespiegelten** Pfaden (`bash/entry/` ↔ `pwsh/entry/`), und jede Datei nennt
ihr Gegenstück in Zeile 1 (`# Bahn: bash | Gegenstueck: ralph.ps1`, siehe
[A.13](doku/anhang-a.md)). Beides wird geprüft, nicht vereinbart —
[`geteilt/tests/test_bahn_kopfzeile.py`](geteilt/tests/test_bahn_kopfzeile.py).

**Das Zielprojekt sieht anders aus als das Kit.** Dort landen die Entrypoints
flach in der Wurzel und alles Aufgerufene unter `team/` — die Bahn-Ordner des
Kits werden beim Installieren aufgelöst:

| im Kit | im Zielprojekt |
|---|---|
| `bash/entry/ralph.sh`, `pwsh/entry/ralph.ps1` | `ralph.sh`, `ralph.ps1` (Wurzel) |
| `bash/lib.sh`, `pwsh/lib.psm1` | `team/lib.sh`, `team/lib.psm1` |
| `geteilt/tools/`, `geteilt/prompts/`, `geteilt/tests/` | `team/tools/`, `team/prompts/`, `team/tests/` |

### Im Zielprojekt

```
projekt/
├── vollautomatik.sh …  Entrypoints sichtbar oben — du tippst sie direkt
├── team.config.sh      die eine Konfigdatei
├── team/               Team-Infrastruktur (lib, tools, prompts, tests)
├── TEAM.md             Bedienanleitung für DICH — lies sie zuerst
├── CLAUDE.md CHANGELOG.md plans/
└── <dein-code>/        unberührt
```

**Das Kit fasst deine Ordner nicht an.** `tests/`, `scripts/` und dein
Produktivcode bleiben, wie sie sind — nichts Stack-Fremdes landet darin. Die
**eine** Ausnahme, und sie ist gewollt: In Test- und Plan-Ordner *dürfen* die
Rollen schreiben (Reproducer, Kaskadenakten). Im Bestandsprojekt ist das der
Grund für den eigenen Plan-Ordner — siehe `BL-51` oben.

## Betrieb

| Bash-Bahn (Linux · WSL) | pwsh-Bahn (Windows ohne WSL) | Wirkung |
|---|---|---|
| `./vollautomatik.sh` | `.\vollautomatik.cmd` | Ganze Kaskade automatisch durchfahren |
| `./halbautomatik.sh <rolle>` | `.\halbautomatik.cmd <rolle>` | Einzelnen Schritt, Entscheidung beim Menschen |
| `./team-status.sh` | `.\team-status.cmd` | Pipeline, Beutebuch, Kaskadenstand |
| `./team-status.sh --budget` | `.\team-status.cmd --budget` | Kontostand, API vs. Abo getrennt |
| `./team-status.sh --ledger-pruefen` | `.\team-status.cmd --ledger-pruefen` | Ist für jede Kaskade alles gebucht? Gegenprobe gegen die archivierten Rohlogs (Exit `4` = Warnbefunde) |
| `./team-status.sh --altlast [N]` | `.\team-status.cmd --altlast [N]` | Produktivdateien, die seit N Kaskaden in keinem Diff lagen — die Auswahlhilfe für einen Altlast-Sweep (`BL-40`) |
| `./team-test.sh` | `.\team-test.cmd` | Regressionstests der Team-Infrastruktur (pytest) |
| `bash <kit>/bash/install.sh . --update` | `pwsh -File <kit>\pwsh\install.ps1 . -Update` | Auf eine neue Kit-Version heben, ohne Projektdaten anzufassen — und ohne die Bahn zu wechseln (`BL-147`) |
| `bash <kit>/bash/install.sh . --update --beide-bahnen` | `pwsh -File <kit>\pwsh\install.ps1 . -Update -BeideBahnen` | Eine abgewählte Bahn zurückholen (`BL-119`) |
| `python3 team/tools/beutebuch.py list` | `python team\tools\beutebuch.py list` | Alle Funde mit Status |
| `./kit-melden.sh neu --titel "…"` | `.\kit-melden.cmd neu --titel "…"` | Fund **am Kit** melden: legt einen Entwurf nach Vorlage an (`BL-153`) |
| `./kit-melden.sh pruefen` | `.\kit-melden.cmd pruefen` | Redaktionsprüfung vor dem Senden — absolute Pfade, Konto-, Rechner- und Projektnamen, Schlüssel (Exit `4` = Befunde) |
| `./kit-melden.sh senden <datei>` | `.\kit-melden.cmd senden <datei>` | Pull Request ans Kit-Repo über `gh` — **fragt vorher**. Ohne `gh`: vorbefüllter Issue-Link |
| `python3 team/tools/zitat_lint.py` | `python team\tools\zitat_lint.py` | Plandateien, die einen erledigten Backlog-Eintrag noch als offene Frage zitieren (`BL-50`) |

> **Der Interpretername gehört der Maschine, nicht der Bahn** (`BL-131`,
> `BL-133`). Unter Windows legen weder python.org noch winget ein
> `python3.exe` an; was dort unter dem Namen antwortet, ist der
> App-Execution-Alias aus dem Microsoft Store — er startet den Store und
> meldet *„Python was not found"*. Welcher Name auf **deiner** Maschine
> gilt, steht in `team.config.sh` bzw. `team.config.ps1`; der Installer
> hat ihn dort eingetragen.

**Welche Spalte gilt, entscheidet die Shell, nicht das Betriebssystem.** Wer
unter Windows in einer WSL-Distro arbeitet, steht in der **linken** Spalte —
WSL ist Windows und fährt die Bash-Bahn. Die rechte Spalte gilt für Windows
**ohne** WSL.

Die `.cmd`-Dateien sind Einzeiler auf die gleichnamige `.ps1`. Die beiden
letzten Zeilen stehen bewusst als *(gleich)* da: Die Python-Werkzeuge werden
**nicht** portiert — Ledger, Beutebuch und Kostenrechnung liegen auf beiden
Wegen in denselben Dateien. Die pwsh-Bahn ist eine zweite
**Orchestrierung**, kein zweiter Zustandscode.

**Exit-Codes**: `0` = durchgelaufen · `1` = echter Fehler · `3` = nichts zu tun ·
`42` = Session-Limit, Lauf pausiert (kein Fehler, kein Datenverlust) ·
`43` = **Stufe fertig, Quittung fehlt** (`BL-41`, seit 2.5.0): Die Rolle hat
gearbeitet und das Log meldet Erfolg, aber das Promise fehlt — meist, weil sie
auf einen Hintergrund-Task wartete, den es headless nicht gibt. **Nicht neu
bauen.** Erst prüfen: committet? Suite grün? Dann von Hand quittieren. Im Feld
kostete das Verwechseln mit „Fehler" viermal die bereits bezahlte Arbeit
(zusammen 19,47 USD).

## Der Rückkanal Feld → Kit

**Jeder Lauf in einem echten Projekt fördert Kit-Fehler zutage** — `BL-1` bis
`BL-223` sind fast alle so entstanden. Damit das nicht von der Disziplin
einzelner abhängt, ist der Weg zurück ein Befehl aus dem installierten Projekt
heraus:

```bash
./kit-melden.sh neu --titel "Kurz, was schiefging"   # Entwurf nach Vorlage
$EDITOR plans/kit-meldungen/<datum>-<slug>.md        # ausfüllen
./kit-melden.sh pruefen                              # Redaktionsprüfung
./kit-melden.sh senden plans/kit-meldungen/<datum>-<slug>.md
```

`senden` legt über `gh` einen Pull Request an, der **eine neue Datei** unter
`plans/meldungen/` hinzufügt und sonst nichts anfasst — so kollidieren zwei
Meldungen nicht, und niemand muss um eine `BL`-Nummer wettlaufen; die vergibt
der Maintainer beim Triage. Ohne `gh` kommt stattdessen ein vorbefüllter
Issue-Link; ein GitHub-Konto im Browser genügt. Näheres in
[CONTRIBUTING.md](CONTRIBUTING.md).

**Drei Entscheidungen, die daran hängen:**

- **Der Loop schreibt, der Mensch sendet.** `neu` und `pruefen` dürfen
  automatisch laufen — eine Rolle darf einen Fund erkennen und ausformulieren.
  `senden` nicht: Ein Pull Request wirkt nach außen und lässt sich nicht
  zurückholen. Das ist *Finder ≠ Fixer*, angewandt auf den Rückkanal.
- **Redaktion ist Pflicht, nicht Kür.** Die Meldung schreibt eine Rolle, die
  gerade eine **private** Codebasis gelesen hat. `pruefen` sucht absolute
  Pfade, Konto- und Rechnernamen, Schlüssel, E-Mail — und den **Namen deines
  Projekts**: Das Kit führt seine eigenen Feldbelege aus genau diesem Grund
  unter `Feld A`…`Feld D`. `senden` geht darüber nicht hinweg, ohne dass man es
  ausdrücklich sagt.
- **Die Meldung wird immer als Datei abgelegt**, auch wenn das Kit gerade nicht
  erreichbar ist. Ein Eintrag, der nur im Feld liegt, hat eine Verfallszeit —
  sie endet beim nächsten `--update`. Genau so ging `BL-42` verloren und musste
  als `BL-58` ein zweites Mal gemeldet werden.

> **Belegstand 🟠:** Der Weg ist gebaut und auf der bash-Bahn gefahren
> (`neu`, `pruefen`, `issue-link`, die Suchkaskade). **Der Pull Request selbst
> ist nicht abgenommen** — `kit-test.sh` kann keinen echten PR anlegen, und es
> ist bisher keiner angekommen. Bis dahin gilt für ihn dasselbe wie für alles
> andere hier: gebaut, nicht belegt.

## Grenzen

- **Sprach- und stackagnostisch, aber python3 wird gebraucht.** Die Team-Werkzeuge
  sind Python und liegen unter `team/tools/`. Das ist eine Abhängigkeit der
  **Team-Infrastruktur** — auf einer Ebene mit `git`, `flock` und der Agenten-CLI —
  nicht deines Projekts. Verifiziert in Go-, Rust- und PHP-Projektstrukturen.
- **Im Feld gelaufen, aber schmal aufgestellt.** Der Dauerbetrieb liegt bei
  **einem** Projekt (`Feld A`: 33 Kaskaden, Greenfield, Linux, bash-Bahn);
  `Feld B` hat **eine** Kaskade auf der pwsh-Bahn gefahren, `Feld C` gar keine.
  Zwei Plattformen und zwei Bahnen sind damit berührt, aber nur **eine**
  Kombination ist eingelaufen. Jeder Lauf hat Kit-Fehler zutage gefördert —
  `BL-1`…`BL-223`, von der toten Fixphase über zwei Löcher in der
  Kostenerfassung und die Zeilenenden bis zur vierten Fehlerklasse „Stufe
  fertig, Quittung fehlt". Die Erwartung ist nicht, dass das aufhört; die
  Mechanik dafür ist der [Rückkanal Feld → Kit](#der-rückkanal-feld--kit) —
  seit `BL-153` ein Werkzeug statt einer Konvention.
- **Bestandsprojekte: der Einzug ist belegt, der Betrieb nicht.** `BL-51`,
  `BL-52` und `BL-57` stammen aus `Feld C`, einer echten gewachsenen Codebasis,
  und sind gegen die nachgestellte Lage geprüft (`kit-test.sh`, Schritt 6). Was
  fehlt, ist eine Kaskade mit echten Agenten in einem Bestandsprojekt — bis
  dahin ist belegt, dass das Team dort **einzieht**, nicht, dass es dort
  **arbeitet**.
- **Noch nie gelaufen: Axel.** Der Forensiker hat in keinem Feld eine einzige
  Ledgerzeile — sein Pfad ist getestet, aber nicht im Feld belegt.
- **Kein Binary, keine Fassung ohne Bordmittel.** Das Kit ist eine Sammlung von
  Skripten und setzt `git`, `bash` ≥ 4 bzw. PowerShell ≥ 7 und `python3`
  voraus; `flock` ist seit `BL-190` nur noch der **bevorzugte** Weg zur
  Loop-Sperre, nicht mehr Bedingung. Eine gepackte, abhängigkeitsfreie
  Auslieferung ist **nicht geplant** — und macOS ist damit nicht verboten, aber
  unbelegt: Die Bordmittel-`bash` ist dort 3.2. `kit-einrichten.sh` sagt das an
  der Maschine, statt es vorauszusetzen.
- **Modellagnostisch ja, CLI-agnostisch nein.** Die Rollen sprechen zwei Stufen
  an (`TEAM_MODEL_LOOP`/`TEAM_MODEL_STRONG`), keine Modellnamen — aber der
  einzige erprobte Weg zu einem Modell führt heute über `claude -p`. Daran
  hängen das Ergebnis-JSON, der Auth-Fallback und die gesamte Kostenmechanik.
  Der Tausch findet in **einer** Funktion statt (`team_claude()` in
  `team/lib.sh`); belegt ist er nicht. Ebenso wenig belegt ist bisher ein Lauf
  mit einem lokalen Open-Weights-Modell — das ist Ziel, nicht Zustand.
- **Selbstverifikation**: `bash bash/kit-test.sh` installiert das Kit in ein
  Wegwerf-Repo und fährt dort die 1220 Tests — **zweimal**: einmal mit den
  Auslieferungswerten, einmal mit angepasster `team.config.sh` (Caps,
  Commit-Präfixe, zwei Domänen). Der zweite Lauf ist die Lehre aus `BL-58`: In
  einer frischen Installation stehen dieselben Werte wie in `team/lib.sh`, ein
  Test, der die Zusicherung am *aufgelösten* Wert misst statt an der
  Bibliothek, ist dort immer grün — und wird erst im Feldprojekt rot.
  `pytest team/tests` **im Kit-Repo** schlägt dagegen erwartungsgemäß fehl —
  die Tests setzen die installierte Ablage voraus (Entrypoints in der Wurzel
  statt unter `bash/entry/` bzw. `pwsh/entry/`).
- **Regeln ändern heißt: Inventarzeile nachziehen.** Stufe 9 prüft jede
  geltende Regel der Vorlage gegen `doku/regel-inventar.md` — wörtliches Zitat,
  und in welcher Datei es steht. Das verbietet keine Änderung, es macht sie
  sichtbar: Wer eine Regel umformuliert, verschiebt oder streicht, bekommt rot
  und muss die betroffene Zeile **benannt** nachziehen, statt sie stillschweigend
  verschwinden zu lassen.
- **Guard-Tests nur in Wegwerf-Repos.** Nie im echten Projekt.
- **`--permission-mode default` ist undokumentiert.** Die beiden Read-Only-Rollen
  (Harry/Marv über `redteam.sh`, Axel) rufen die CLI damit auf. Der Wert wird von
  Claude Code 2.1.206 **akzeptiert**, taucht in `claude --help` aber nicht mehr in
  der Auswahlliste auf (dort stehen `acceptEdits`, `auto`, `bypassPermissions`,
  `manual`, `dontAsk`, `plan`). Falls eine künftige CLI ihn entfernt, schlagen
  genau diese beiden Rollen fehl — dann den passenden Nachfolger einsetzen und
  die Guard-Wirksamkeit erneut gegen die CLI verifizieren (Anhang A.5).
- **Budget-Caps großzügig ansetzen.** Ein zu tiefer Pro-Fall-Cap wirft teure,
  aber plausible Fixes per Rollback weg und **vervielfacht** die Kosten
  (Feld-Lehre `HM-32`).

## Lizenz

[MIT](LICENSE) — © 2026 Max Ron.

Benutzen, ändern, weitergeben und in eigene Projekte einziehen ist ausdrücklich
erlaubt, kommerziell wie privat; es bleibt nur die Namensnennung. Das gilt
**auch für die 186 Dateien, die der Installer im Zielprojekt hinterlässt** — sie
lösen keine Lizenzpflicht für den Code des Zielprojekts aus. Der Code stammt aus
einem eigenen Projekt des Autors; das Urheberrecht liegt vollständig bei ihm.

Das gilt auch für den Banner: `team-banner.webp` ist aus der mitgelieferten
Quelle `team-banner.svg` gerendert und enthält kein fremdes Material.

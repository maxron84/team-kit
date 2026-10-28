# Roadmap-Skizzen — T.E.A.M.-Starterkit

Ungehärtete Stränge für die Weiterentwicklung **des Kits selbst**. Ziel, grober
Umfang, Bezug, offene Fragen — **ohne** Stufennummern, **ohne** Cap
(Kaskaden-Planungsregel 1).

> **Nicht verwechseln:** `bootstrap/roadmap-skizzen.md` ist die **Vorlage**, die
> der Installer in Zielprojekte kopiert. Diese Datei hier ist die Roadmap des
> Kits. `install.sh` liest ausschließlich aus `bootstrap/` — dieser Ordner
> landet in keiner Installation.

**Quelle der meisten Stränge:** das Feldprojekt
`~/Source/Feld A`, Kaskade 1 (2026-08-01). Dort ist das Kit
zum ersten Mal scharf über eine volle Kaskade gelaufen, und genau dort fielen die
Fehler auf, die kein Kit-Test finden konnte.

---

## ~~Skizze A: Das Kit kann sich selbst nicht prüfen~~ — gebaut 2026-08-01

Als `kit-test.sh` umgesetzt (Architekt-Ausnahme, Backlog `BL-6`). Der Strang
lief **nicht** über eine Kaskade: Es war ein Skript und ein Gegenbeweis, keine
mehrstufige Arbeit.

**Was entschieden wurde:** „Installieren und dort prüfen" statt
layout-agnostischer Tests — das prüft den Installer gleich mit und lässt die
Tests dort laufen, wo sie gelten (damals 149, Stand 2.6.0 **280**). Die
Fehlschläge von `pytest team/tests` **im Kit-Repo** bleiben bestehen und sind
**erwartet** — damals 17, Stand 2.6.0 **21** von 280.

**Offen geblieben:** Ob der Lauf zusätzlich in einen Git-Hook gehört, oder ob
die Regel „vor jedem Push" reicht. Bisher reicht sie — es gibt genau einen
Menschen im Prozess. *(Die Regel hieß bis 2026-08-16 „vor jedem Release";
das Kit veröffentlicht keine Releases mehr, ausgeliefert wird der Quellstand.)*

---

## ~~Skizze B: Die Kostenerfassung ist strukturell unvollständig~~ — gebaut 2026-08-01

`BL-4` und `BL-5` behoben (Architekt-Ausnahme nach Franks Dreisatz), je mit
Regressionstest und gefahrener Gegenprobe.

**Die beiden Entscheide, die offen waren:**

1. **`BL-4`** — *eigener Verb oder Erweiterung?* Beides: `kosten.py
   ralph-abschluss` als eigener Verb mit eigener `ralph`-Ledgerzeile, aber
   `./team-status.sh --rollen-abschluss` ruft beide Verben. **Eine**
   Bedienhandlung, **zwei** Zeilen. Eine Sammelzeile hätte die Trennung
   Bau ↔ Sweep/Fix gekostet — und genau an dieser Kennzahl fiel im Feld
   überhaupt auf, dass Ralph fehlte.
2. **`BL-5`** — *addieren, abbrechen oder erkennen?* Abbrechen als Default,
   `--addieren` und `--ersetzen` als ausdrückliche Wege. Begründung: Der Wert
   entsteht aus **disjunkten** Log-Mengen (jeder Abschluss archiviert, was er
   zählte), dafür ist Addieren die richtige Verknüpfung. Automatisch addiert
   wird trotzdem nicht — **ohne** `--archivieren` zählen zwei Aufrufe dieselben
   Logs, dann wäre Addieren eine Doppelbuchung. Die Unterscheidung gehört dem
   Menschen, nicht einer Heuristik.

**Offen geblieben:** Ein Ledger-Konsistenzcheck (`--ledger-pruefen`), der
Lücken meldet, statt sie erst im nächsten Closeout auffallen zu lassen. Wäre
das Werkzeug gewesen, das `BL-4` gefunden hätte, statt eines aufmerksamen
Menschen beim Abgleich zweier Dokumente. **Nächster Kandidat für eine echte
Kaskade** — siehe Skizze D.

---

## ~~Skizze C: Der Rückkanal Feld → Kit ist Handarbeit~~ — geregelt 2026-08-01

Bewusst **als Konvention, nicht als Werkzeug** gelöst: Das Kit hat jetzt ein
eigenes `plans/backlog.md`, und drei Stellen sagen, wohin ein Kit-Fund gehört —
die Backlog-Vorlage `bootstrap/backlog.md`, das Architekten-Briefing und der
Statuswert „ans Kit gemeldet".

**Warum kein Werkzeug:** Bei einem Menschen und zwei Repos wäre jede
Automatisierung teurer als das Problem. Das ändert sich ab dem dritten
Feldprojekt — dann neu bewerten.

**Neu bewertet 2026-08-23 (`BL-153`) — die Antwort hat sich gedreht.** Mit
`Feld D` ist der Auslöser gefallen, und beim Nachlesen kam ein Grund dazu, den
die Skizze nicht kannte: Die Konvention nannte `~/Source/team-kit`, also die
Ablage **einer** Maschine, und das installierte Projekt wusste nirgends, wo das
Kit liegt. Die Rechnung „ein Mensch, zwei Repos" stimmte auch nur, solange
**derselbe** Mensch beide hat — für einen fremden Nutzer war sie nie richtig,
und der hat obendrein kein Schreibrecht. Gebaut als `kit_meldung.py` mit
`kit-melden.sh`/`.cmd`, mit der Trennung „der Loop schreibt, der Mensch sendet"
und einer Redaktionsprüfung, die auch den **Projektnamen** sucht. Der
GitHub-Weg (Fork, Zweig, eine Datei unter `plans/meldungen/`, PR) ist gebaut,
aber **nicht abgenommen**: `kit-test.sh` kann keinen echten PR anlegen.

---

## ~~Skizze D: Das Ledger prüft seine eigene Vollständigkeit nicht~~ — gebaut 2026-08-01

Als `kosten.py ledger-pruefen` / `./team-status.sh --ledger-pruefen` umgesetzt
(Architekten-Handarbeit nach Franks Dreisatz, Release 2.4.0). Der Strang lief
**nicht** über eine Kaskade — im Kit-Repo ist kein Team installiert, Ralph kann
hier nichts bauen (Stakeholder-Entscheid 2026-08-01: bleibt so).

**Die drei offenen Fragen, beantwortet:**

1. *Woher weiß das Werkzeug, dass eine Kaskade abgeschlossen ist?* Aus dem
   **Ledger**, nicht aus `.ralph-state`. Eine Kaskade gilt als abgeschlossen,
   sobald sie eine `ralph`- oder `roles`-Zeile trägt. `.ralph-state` ist ein
   Bauzeiger und wird von `--force` zurückgesetzt; der Archiv-Ordner — der
   ursprüngliche Kandidat — schied an einer harten Randbedingung aus, siehe
   unten.
2. *Warnung oder Exit ≠ 0?* **Beides, getrennt.** Exit `4` bei Warnbefunden
   (`1` bleibt dem Bedienfehler), aber **kein** hartes Gate im Closeout: Eine
   Kaskade mit legitim fehlender Zeile dürfte sonst nicht abschließen, und ein
   Gate, das man regelmäßig umgehen muss, wird umgangen. Stattdessen läuft die
   Prüfung bei jedem `--budget` ungefragt mit — sichtbar, aber nicht blockend.
   Zwei Schweregrade: `warnung` (sehr wahrscheinlich verlorenes Geld) und
   `hinweis` (kann legitim sein). Ein Werkzeug, das bei jedem Lauf rot ist,
   erzieht zum Wegsehen.
3. *Kaskade oder Handarbeit?* Handarbeit — siehe oben.

**Die Randbedingung, die der Entwurf nicht kannte — und was sie geändert hat:**
Die Skizze wollte je Kaskade prüfen, ob eine Zeile kleiner ist als *ihre*
archivierten Rohlogs. Das ist mit der heutigen Ablage **nicht ehrlich
beantwortbar**: Log-Dateinamen tragen keine Kaskadennummer
(`stufe-<n>-<ts>.json`, `harry-<ts>.json`), und das Archiv ist **ein** flacher
Ordner je Quelle. Zuordnen ließe sich nur über mtime-Fenster — also raten, und
in der Kostenmechanik wird nicht geraten. Ein Archiv je Kaskade
(`archiv/kaskade-<n>/`) wäre der saubere Weg gewesen, hätte aber `lauf_kosten()`
in `vollautomatik.sh` gebrochen: Das globbt `.ralph-logs/archiv`
**nicht-rekursiv** und misst den Pro-Lauf-Deckel damit auch gegen Geld, das
eine Abschluss-Stufe *innerhalb* des Laufs schon weggeräumt hat (`BL-55`).
**Entscheid:** Der Rohlog-Vergleich läuft je **Quelle** statt je Kaskade —
Archivordner und Ledger-Rolle entsprechen einander eindeutig, ohne jede
Zuordnung. `BL-4` und `BL-5` hätte er beide gefunden; beide sind mit ihren
echten Feldzahlen als Regressionstest hinterlegt.

**Offen geblieben:** Ein Archiv je Kaskade bliebe die genauere Lösung und würde
den Vergleich kaskadenscharf machen. Der Preis ist eine Änderung an der
Pro-Lauf-Durchsetzung (`lauf_kosten` müsste rekursiv globben, ohne `BL-55`
wieder aufzureißen) — das ist echte Werkzeugarbeit mit Testbedarf und wäre der
nächste Kandidat, **falls** je ein Team im Kit-Repo läuft.

---

> **Die drei folgenden Stränge sind offen** (Entscheid des Owners, 2026-09-03).
> Sie stehen seit demselben Tag als Abzeichen im README-Kopf — `Agenten-CLI`,
> `Sprachen`, `Binary` —, und sie stehen dort in **Orange**: gewollt, nicht
> abgenommen. Ein Abzeichen ohne Strang wäre eine Ankündigung ohne Adresse;
> hier ist die Adresse. Gebaut ist an allen dreien **nichts**.

## Skizze E: Gepackte Auslieferung — das Kit ohne Bordmittel-Kette

**Ziel.** Eine Fassung, die weniger von der Zielmaschine verlangt als heute
(`git`, `bash` ≥ 4 bzw. PowerShell ≥ 7, `python3`). Anlass ist nicht
Bequemlichkeit, sondern der Belegstand: macOS scheitert heute an der
Bordmittel-`bash` (3.2), und jede Einrichtung, die eine Kette prüfen muss, hat
eine Stelle, an der sie abbricht — `kit-einrichten.sh` existiert genau deshalb.

**Grober Umfang.** Kandidat ist **ausschließlich der Python-Teil**
(`geteilt/tools/`): Ledger, Beutebuch, Kostenrechnung, Meldungswerkzeug. Das
ist die einzige Abhängigkeit, die das Kit mitbringt und die ein Projekt nicht
ohnehin hat. **Nicht** Kandidat ist die Orchestrierung — sie *ist* die Shell;
ein „Binary", das `bash` ersetzt, wäre ein anderes Produkt.

**Bezug.** `BL-190` (Sperre ohne `flock`) ist derselbe Gedanke eine Etage
tiefer: eine Bedingung zu einer Bevorzugung machen, statt sie vorauszusetzen.

**Offene Fragen — vor dem Bauen zu entscheiden:**

1. *Was gewinnt man wirklich?* `python3` fehlt auf kaum einer
   Entwicklermaschine. Wird hier eine Hürde beseitigt oder eine gefühlte?
2. *Der Grundsatz dagegen.* Heute liegt **jede** Datei im Zielprojekt lesbar
   daneben — das trägt den Read-Only-Guard, den Diff als Prüfeinheit und die
   Nachvollziehbarkeit des Ledgers. Ein undurchsichtiges Binary im
   `team/`-Namensraum widerspricht dem. Beilegen statt ersetzen?
3. *Wer baut die Artefakte?* Drei Plattformen, drei Bauläufe, drei Signaturen
   — das ist eine Freigabe-Kette, die das Kit heute nicht hat (es
   veröffentlicht keine Releases, ausgeliefert wird der Quellstand).
4. *Die Gegenprobe, die den Strang erst gültig macht:* `kit-test.sh` grün auf
   einer Maschine **ohne** `python3` — sonst ist die Zusicherung nicht geprüft,
   sondern behauptet.

---

## Skizze F: Die zweite Agenten-CLI — Codex neben Claude Code

**Ziel.** Das Kit ist modellagnostisch und **nicht** CLI-agnostisch; das steht
so unter *Grenzen* und in `anhang-a.md`, A.11. Der Strang macht daraus einen
Beleg statt einer Absichtserklärung: dieselbe Kaskade über **zwei** CLIs.

**Warum die zweite und nicht „irgendeine".** Solange es genau einen Weg gibt,
ist die Behauptung „die Bindung hängt an *einer* Funktion" unwiderlegt und
unbelegt zugleich. Erst der zweite Weg zeigt, ob `team_claude()` wirklich die
einzige Stelle ist — oder ob die Annahme an Dutzenden Stellen mitläuft.

**Grober Umfang.** Vier Verträge muss ein Zweitweg mitbringen, und sie sind in
A.11 benannt: das **Ergebnis-JSON** (`is_error`, `subtype`, `total_cost_usd`),
der **Auth-Fallback** (A.3), die **429-Behandlung** (A.8) und der
**`--permission-mode`**, an dem die Read-Only-Rollen hängen (A.5). Dazu die
Preistabelle in `kosten.py`: Sie rechnet heute Claude-Modelle, und ein zweiter
Anbieter bringt eigene Modellnamen und eigene Preise mit — `TEAM_PREISE`
(`BL-211`) ist dafür der vorhandene Hebel.

**Offene Fragen:**

1. *Wo endet `TEAM_CLAUDE_BIN`?* Der Name stammt aus `BL-173` und meint heute
   „die Agenten-CLI". Zwei CLIs brauchen entweder zwei Variablen oder eine
   neutrale (`TEAM_AGENT_CLI`) plus eine **Bahn-Kennung**, welche Aufrufform
   gilt. Umbenennen heißt: Konfigurationsvorlagen, Installer, beide
   Bibliotheken, Regel-Inventar — und Bestandsprojekte behalten ihren Namen.
   Dieselbe Lage wie `BL-202`, und dort war die Antwort **Toleranz**, nicht
   Umbenennung.
2. *Kostenmechanik.* Meldet die zweite CLI überhaupt einen Preis je Aufruf?
   Tut sie es nicht, ist der Ersatzzettel der Normalfall statt der Ausnahme —
   und `sitzung-messen` müsste die Lücke schließen, nicht der Aufruf.
3. *Abnahmekriterium.* Dasselbe wie für einen Modellwechsel (A.11): eine
   vollständige Kaskade im Feld, `kit-test.sh` grün, Guard-Wirksamkeit gegen
   die neue Bindung **erneut** verifiziert, und die Rate der Exit-`43`-Fälle
   als Kennzahl. Eine grüne Suite belegt hier gar nichts — sie ruft die CLI
   nicht auf.

---

## Skizze G: Eine englische Fassung des Kits

**Ziel.** Das Kit ist durchgehend deutsch — Doku, `TEAM.md`,
Regeldatei-Vorlage, **Rollen-Briefings**, Auftragstexte und jede
Werkzeugmeldung. Für ein
englischsprachiges Team ist das heute keine Sprachbarriere in der Doku, sondern
im **Betrieb**: Die Prompts, mit denen die Rollen arbeiten, sind deutsch.

**Grober Umfang — und die ehrliche Reihenfolge der Arbeit.** Die Prosa ist der
kleinere Teil. Der größere sind die **Kopplungen**, die das Kit sich selbst
gegeben hat:

- `doku/regel-inventar.md` zitiert jede Regel **wörtlich**;
  `geteilt/kit-regelinventar.py` prüft die Zitate zeichengenau (`kit-test.sh`
  Stufe 9). Eine übersetzte Regel ist dort ein Befund, kein Fortschritt.
- `geteilt/tools/zitat_lint.py` prüft Plandateien gegen Backlog-Zitate.
- Die Regressionsfälle greifen an vielen Stellen auf **deutsche
  Zeichenketten** zu — Promise-Marker sind sprachfrei, Meldungstexte nicht.
- Die 45-Zeilen-Grenze der Briefings gilt weiter: Englisch ist meist kürzer,
  aber „meist" ist keine Zusicherung. Jede übersetzte Fassung muss die Grenze
  einzeln belegen.

**Was in jeder Fassung unverändert bleibt:** der Name `T.E.A.M.` samt der
Initialen und der selbstironischen Pointe. Die Auflösungen stehen in
`bootstrap/TEAM.md` — 🇬🇧 *Thankfully, Everyone (but me) Achieves More*.

**Offene Fragen:**

1. *Zwei Bäume oder ein Baum mit zwei Sprachdateien?* Zwei Bäume driften
   auseinander — dieselbe Gattung wie die Doppelbahn, und dort kostet der
   Gleichstand einen eigenen Selbsttest-Schritt. Ein Baum mit Sprachdateien
   verlangt, dass **jeder** Meldungstext durch eine Nachschlagestelle geht;
   das ist ein Umbau an jeder Zeile, die heute etwas ausgibt.
2. *Wie weit reicht die Übersetzung?* Nur die installierten Teile (Briefings,
   `TEAM.md`, `CLAUDE.md`-Vorlage, Werkzeugmeldungen) — oder auch Backlog,
   Archiv und Anhang A? Der Backlog **ist** die Feldlehre; er ist die größte
   Textmasse und der geringste Nutzen für den Anwender.
3. *Wer prüft die Übersetzung fachlich?* Die Feldlehren tragen ihre
   Genauigkeit im Wortlaut; eine glatte, aber ungenaue Übersetzung ist
   schlimmer als keine. Dieselbe Sorge, aus der `CONTRIBUTING.md` die
   Redaktionsregel hat.

---

> **Offen seit 2026-10-28** (Triage, Auftrag des Owners). Anders als E bis G
> steht dieser Strang nicht als Abzeichen im README-Kopf. Er trägt `BL-352` und
> `BL-354`, dazu als Teile `BL-247` Punkt 4 und `BL-340` Teil B. Gebaut ist
> **nichts**; alle vier bleiben offen, bis der Owner entschieden hat.

## Skizze H: Jede Rolle lokal oder entfernt — die Wahl des Wegs

**Ziel.** Die Auflage des Owners aus `BL-354`, wörtlich: „… welche Rolle wird
100% lokal und umgekehrt, oder auch nur 50% nach ermessen des Architekten, oder
auch auf Zuruf des Benutzers spontan". Dazu der Nachtrag: Entfernte Modelle nur
auf ausdrückliche Anweisung des Benutzers; scheitert eine lokale Rolle,
übergibt sie an den Menschen, statt auszuweichen. Das Ziel „lokal, von unten
nach oben" (README, A.11) bekommt damit einen Schalter statt eines Stichtags.

**Der Feldbeleg.** `Feld H`, Kaskade 3: Eine Stufe trug statt eines Promise
einen Bauauftrag. Ein Programm im Projekt ließ ein lokales Modell mit
32K-Fenster bauen — Auftrag samt roter Abnahmetests, Änderung, Smoke-Test,
Commit — und traf im ersten Versuch; der Rest der Kaskade lief wie immer. Drei
Nähte gingen von Hand (`BL-352`): Start und Quittung des Baus, Kosten ohne
USD, eine Abnahmequelle ohne Schutz.

**Was es heute gibt.** Jeder automatische Aufruf hängt an einer Stelle:
`team_claude()` (in pwsh `Team-ClaudeSchreiben`). Davor stehen zwei
Modellnamen (`TEAM_MODEL_LOOP`, `TEAM_MODEL_STRONG`) und **ein** Anbieter: Abo
zuerst, die API als automatischer Rückfall (Entscheid 2026-07-10), seit
`BL-316` nicht mehr nach einer abgelaufenen Anmeldung. Eingerichtet wird er von
`team-auth-setup`, das sich selbst „ein Beispiel, keine Kit-Mechanik" nennt.
Der Architekt ist die Sitzung des Menschen; ihr Modell wählt der Mensch, nicht
das Kit.

**Grober Umfang — drei Ebenen derselben Wahl:**

1. **Je Rolle**, als Vorgabe in `team.config.*`: `entfernt` (wie heute, der
   Standard), `lokal` oder `gemischt` — dann wählt der Architekt je Stufe. Das
   sind die drei Fälle der Auflage: ganz lokal, umgekehrt, nach Ermessen des
   Architekten.
2. **Je Stufe im Plan**, wo die Vorgabe `gemischt` sagt: der Bauauftrag aus
   `Feld H`, die **Programm-Stufe**. Der Loop ruft für diese Stufe statt
   `team_claude()` ein Programm. Exit 0 plus ein neuer Commit ist die Quittung,
   jeder andere Exit hält den Loop mit dem Bericht des Programms an. Ein
   Promise braucht es nicht; das Programm weiß selbst, ob die Tests grün sind.
   Dafür schreibt der Architekt die Abnahmetests vorher.
3. **Auf Zuruf**: eine Option der Startbefehle, die die Vorgabe für einen Lauf
   ersetzt.

**Die Regel dazwischen:** Kein Weg wechselt von selbst. Entfernt läuft eine
Rolle nur, wenn der Mensch es eingestellt (`entfernt`, `gemischt`) oder
zugerufen hat; scheitert eine lokale Stufe, hält der Loop an. So wird „nur
ausdrücklich" eine Eigenschaft der Auflösung statt eines Satzes im Prompt.

**Was die Programm-Stufe außerdem braucht** — die drei Nähte aus `BL-352`:

- **Kosten.** Die Bauzeile bleibt eine `ralph`-Zeile, mit 0 USD **und** der
  Kennung „lokal" — ohne Kennung gäbe die Null die Kosten falsch wieder.
  Sekunden und Token kommen in das Quellenfeld, das `BL-247` Schritt 1 schon
  schreibt. Dann findet `--ledger-pruefen` seine Zeile; heute meldet es den
  richtigen Zustand als Warnung (Exit 4). Das ist `BL-247` Punkt 4, ohne
  Pauschale.
- **Abnahmequelle.** Die roten Tests des Auftrags darf das Programm nicht
  ändern. Das prüft das Kit nach dem Lauf am Diff, nicht der Prompt. Für Harry
  und Marv genügt bis dahin ein Muster in `TEAM_PLAN_ORDNER_BESTAND`
  (`*/stufe-*/tests/*`); eine Guard-Sperre im Planordner bräuchte eine
  Entscheidung gegen `BL-51`.
- **Scheitern.** Kein Rückfall. Der Loop hält an, der Bericht steht im Log, und
  der Mensch entscheidet — etwa, die Stufe auf Zuruf entfernt zu wiederholen.

**Einrichtung je Anbieter.** Die Programm-Stufe spricht mit dem Modell über
eine Schnittstelle, nicht über die Agenten-CLI. Spricht sie ein Format, das
auch entfernte Anbieter anbieten (das OpenAI-kompatible), ist „entfernt" für
sie nur eine andere Adresse mit Schlüssel. Ein Einrichtungsskript je Anbieter
legt Adresse, Modell und Schlüssel ab, wie heute `team-auth-setup` den
Anthropic-Schlüssel. **Abo oder API:** Ein Abo lässt sich bei den großen
Anbietern nach heutigem Stand nur über deren eigene CLI nutzen (Claude Code,
Codex). Ein Abo-Weg führt darum zu Skizze F, die API zur Programm-Stufe. Vor
dem Bau je Anbieter nachsehen.

**Eine Phase ohne Modell** (`BL-340` Teil B) ist derselbe Baustein, nur ganz
ohne Modell: ein konfiguriertes Programm als Schritt, Exit-Code und Bericht als
Ergebnis, danach urteilt eine günstige Rolle nur lesend. Die kleinste erste
Stufe ist ein Konfigurationsplatz nach dem Muster von
`TEAM_ZIELSTAND_PRUEFUNG`, den die Vollautomatik am Ende fährt.

**Verhältnis zu Skizze F.** F fragt, ob eine **zweite CLI** an derselben Stelle
steckt, und nennt vier Verträge: Ergebnis-JSON, Auth-Rückfall, 429-Behandlung,
`--permission-mode`. Für die Programm-Stufe gelten sie anders: Die Quittung ist
Exit-Code und Commit, einen Rückfall gibt es nicht, ein lokales Modell kennt
kein Kontingent, und das Modell hat keine Shell — das Programm schreibt. Beide
Stränge brauchen dieselbe Weiche vor `team_claude()`. Wer zuerst baut, legt
ihren Namen fest; Frage 1 aus F (`TEAM_CLAUDE_BIN` oder ein neutraler Name)
gilt für beide.

**Offene Fragen — vor dem Bauen zu entscheiden:**

1. *Betrifft „nur ausdrücklich" auch den Rückfall vom Abo auf die API?* Beide
   Wege sind entfernt, und der Rückfall war gewollt. Aber er kostet Geld, ohne
   zu fragen: In `BL-316` rund 12,5 USD für Stunden, in denen eine
   Neuanmeldung gereicht hätte; bei einer Ablehnung durch die Schutzregeln half
   er. Vorschlag: Er bleibt, wird aber ausdrücklich — das Einrichtungsskript
   fragt einmal danach; Bestandsinstallationen behalten ihn.
2. *Welche Ebene zuerst?* Vorschlag: je Stufe, also die Programm-Stufe. Sie ist
   als einzige im Feld belegt und schließt `BL-352`. Danach die Vorgabe je
   Rolle, zuletzt der Zuruf.
3. *Wessen Programm?* Die Werkbank wird ein lokaler Teil des Kits (Entscheid
   des Owners). Vorschlag: Der erste Bau ruft ein **konfiguriertes** Programm,
   damit das aus `Feld H` sofort passt; danach zieht die Werkbank nach
   `geteilt/tools/` und wird der Standard.
4. *Was heißt „lokal" für die Prüfrollen?* Harry, Marv und Frank arbeiten mit
   Shell und Werkzeugen der CLI. Ein lokales Modell ohne Shell braucht für sie
   eine eigene Werkbank: Das Kit schneidet den Code zu, das Modell antwortet
   mit Funden oder einer Änderung. Ob eine Agenten-CLI gegen ein lokales Modell
   trägt, ist nicht geprüft. Bis dahin heißt „Rolle lokal" nur für den Bau
   etwas.
5. *Abnahme als Phase oder Rolle?* Die Frage aus `BL-340` Teil B, mit dem
   Konfigurationsplatz als erster Stufe.
6. *Abnahmekriterium.* Vorschlag nach A.11: eine Kaskade im Feld, deren lokale
   Stufe der Loop startet und quittiert; kein Handgriff an `.ralph-state`;
   `--ledger-pruefen` still; die Abnahmetests nach dem Bau unverändert;
   `kit-test.sh` und `kit-test.ps1` grün.

# Changelog — T.E.A.M.-Starterkit

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

> **Feldbelege tragen Kürzel statt Namen** (`Feld A`…`Feld D`).
> Wofür sie stehen, sagt die Profiltabelle im
> [README](README.md#herkunft): Für den Beleg zählt die Lage eines
> Projekts — Plattform, Bahn, Greenfield oder Bestand —, nicht sein Name.

## [Unreleased]

### Added

- **`kit-melden ablegen` — der Weg für alle, die das Kit daneben liegen haben**
  (`BL-168`, gemeldet von `Feld E`). Bis hierher gab es ein Werkzeug für den
  Weg, den niemand geht (Pull Request über `gh`), und keins für den, den alle
  gehen: Das Kit liegt geklont daneben, `TEAM_KIT_PFAD` zeigt darauf, und
  `gh auth status` ist auf der Maschine nicht angemeldet.

  **Die Folge war messbar:** Im meldenden Projekt sind **acht** Funde von Hand
  ins lokale Kit getippt worden — am Werkzeug vorbei und damit auch an seiner
  Redaktionsprüfung, der einzigen Stelle, an der ein Projektname auffällt,
  **bevor** er in einem öffentlichen Repo steht.

  `ablegen` kopiert die Meldung nach `<kit>/plans/meldungen/` und committet sie
  dort — **ohne Push** und **ohne `BL-`Nummer**. Committet wird **pfadgenau**:
  Der Kit-Arbeitsbaum gehört dem Maintainer, ein `git add -A` nähme fremde
  Arbeit mit (`BL-12`). Die Redaktionsprüfung ist hier **Vorbedingung**, nicht
  Empfehlung.

  **Warum committen ja und pushen nein:** Owner zu sein löst die Frage der
  **Zuständigkeit**, nicht die der **Veröffentlichung**. Das Kit-Repo ist
  öffentlich, und die Meldung entsteht beim Lesen einer privaten Codebasis.

  Dazu zwei Teile, die denselben Weg begehbar machen: `pruefen` löst den
  **blanken** Dateinamen jetzt auch gegen den Meldungsordner auf (CWD gewinnt)
  — bis dahin nannte die Vorlage einen Befehl, den sie selbst nicht lauffähig
  machte. Und `TEAM_FELD_KUERZEL` steht in **beiden** `team.config.*`: Das
  Kürzel lebte bis hierher ausschließlich im Kit-README, also **außerhalb** der
  Installation, die es nennen müsste.

### Changed

- **Der Rückkanal trennt jetzt zwei Rollen — und `senden` sagt es selbst**
  (`BL-187`, Entscheid des Owners 2026-08-26). Ein **fremder** Kit-Nutzer
  sendet einen Pull Request; der **Owner** legt die Meldung ins lokal liegende
  Repo und schreibt dort eine `BL-n`-Zeile. Ein PR gegen das eigene Repo hieße,
  die eigene Meldung zu reviewen und zu mergen — und ohne die Unterscheidung
  erzeugt jedes Feldprojekt des Owners Zweige, PRs und Issues am eigenen Repo:
  eine Vorgangs-Historie, die keine Vorgänge abbildet.

  `senden` prüft das GitHub-Konto gegen den Repo-Eigentümer, bricht ab und
  nennt den richtigen Weg — **vor** der Bestätigungsfrage. Vorher kannte das
  Werkzeug denselben Fall bereits und nutzte ihn nur, um den Fork zu
  überspringen: Es lief **sehenden Auges** in den falschen Weg. Zwei Fallen
  sind eigens geschlossen: Antwortet `gh` nicht, wird **niemand** zum
  Eigentümer erklärt, und eine **leere** Antwort gilt nicht als Treffer.

  Die Rollen stehen jetzt in Briefing, `bootstrap/TEAM.md`,
  `bootstrap/CLAUDE.md.vorlage`, `bootstrap/backlog.md` und
  `plans/meldungen/README.md` — jeweils mit dem Grund daneben.

### Changed

- **Fünf Regeln, die es längst gab — nur nicht dort, wo sie gebraucht werden.**
  Gemeinsamer Nenner: Jede war im Code, in einem Test, im Archiv oder im
  Kommentarkopf sauber festgehalten, also ausschließlich an Orten, die der
  Mensch im Zielprojekt nicht liest.

  - **Die Sitzungs-Invariante hat zwei Hälften, `TEAM.md` nannte keine**
    (`BL-165`). *Jede interaktive Sitzung bucht genau einmal — zweimal zählt
    doppelt, keinmal ist unwiederbringlich verloren.* `BL-116` löste die eine
    Hälfte; die andere war **nirgends** dokumentiert: `sitzung-messen` liest
    das zuletzt geänderte Transkript, also die *laufende* Sitzung. Eine
    Sitzung, die nicht bucht, wird deshalb **nie** gemessen — die Kosten sind
    nicht „später fällig", sie sind weg. **Der Kit-eigene Rat erzeugte die
    Lücke, die er nicht benannte:** „nach einem gebuchten Closeout eine neue
    Sitzung für die nächste Kaskade" — wer dem folgt, plant K(N+1) in einer
    Sitzung, die selbst nichts bucht. Die Invariante steht jetzt im
    Kosten-Abschnitt, der Messumfang ist offengelegt, und das Briefing nennt
    den Fall samt Befehl.
  - **`team-status --watch` stand in keiner Bedienanleitung** (`BL-183`). Der
    Anlass, wörtlich: *„Ich sehe wieder kein Monitoring, das ist weil ich noch
    kein Update vom Kit herausgefahren habe, korrekt?"* — die Vermutung war
    falsch. **Es fehlte nichts, es war nur nicht auffindbar.** Jetzt in der
    Befehlstabelle, mit dem, was `--watch` **nicht** kann: neu zeichnen statt
    anhängen.
  - **`TEAM.md` verwies auf ein Werkzeug, das der Leser nicht hat**
    (`BL-164`). `team-auth-setup.sh` liegt nur im Kit; wer es nicht findet,
    greift zu genau dem `export`, vor dem der Absatz zwei Zeilen darüber warnt
    — der Verweis leitete ins **Gegenteil** seiner Absicht. Jetzt steht der
    **Handweg zuerst** (drei Zeilen, keine Voraussetzung), das Skript danach
    mit vollem Fundort. Merksatz: *Ein Dokument, das ein Werkzeug nennt, das
    der Leser nicht hat, muss den Weg ohne dieses Werkzeug zeigen.*
  - **Die Gegenprobe für zentrale Werte nannte keinen Zeitpunkt** (`BL-167`)
    — und prüfte deshalb zuverlässig nichts. In der **einführenden** Stufe ist
    sie wertlos, solange kein Verbraucher existiert, meldet aber grün. Die
    Regel nennt jetzt den Zeitpunkt und ein nachprüfbares Kriterium:
    **weniger oder gleich viele rote Stellen als Textsuch-Fundstellen heißt,
    dass nichts geprüft wurde.** Gemessen: erst 2 rote Stellen gegen 2
    grep-Treffer, nachgeholt 11 rote in 7 Dateien, darunter drei, die die
    Textsuche gar nicht nennt.
  - **`{{SMOKE_TEST}}` stand auch in Ralphs eisernen Grenzen** (`BL-170`) —
    **in Backticks**, also in der Auszeichnung, an der eine ausführende
    Instanz einen Befehl erkennt, und im selben Prompt sagte `SMOKE_ZEILE`
    daneben das Gegenteil. Neu ist `{{SMOKE_TEST_GRENZE}}`, das den **ganzen
    Satz** trägt: mit Smoke-Test in Backticks, ohne einen als Prosa. Gefüllt
    in allen drei Routinen (`install.ps1` und **beide** von `install.sh`).

### Fixed

- ⚠️ **`kosten.py` rechnete `claude-sonnet-5` mit 3.00 statt 2.00 USD/Mio
  Input** (`BL-166`, gemeldet von `Feld E`). Weil `sonnet` der Default aller
  Loop-Rollen ist (`TEAM_MODEL_LOOP`), betraf der falsche Satz die **Mehrheit
  aller gemessenen Token** jeder Installation: Die Selbsteichung schlug in
  9 von 9 abgerechneten Läufen an, 25–33 % daneben, und das Werkzeug
  verweigerte mit Exit 2 regelkonform jede Buchung. **Kein stiller Fehler** —
  die Eichung tat genau, was sie soll; der Schaden war die Blockade.

  Der Satz ist gegen die Preistabelle des Anbieters nachgeschlagen, nicht aus
  dem Gedächtnis gesetzt; sie bestätigt zugleich, dass die **übrigen zehn
  Sätze stimmen**.

  **Wichtiger als der Wert: Die Eichung benennt den Fund jetzt.** Sie wusste
  bereits, dass etwas nicht stimmt, sagte aber nicht, *was* — und ließ den
  Betreiber vor einer Tabelle mit elf Sätzen stehen. Neben der Verweigerung
  steht jetzt: `claude-sonnet-5: Tabelle 2.00, abgerechnet entspricht 3.00
  USD/Mio Input (+50 %)`. Die Rechnung ist exakt (die Kosten sind im
  Basispreis linear); gelesen werden nur **Einmodell-Läufe**, weil bei zwei
  Modellen in einem Log die Aufteilung unterbestimmt wäre und jede Zuweisung
  geraten — eine geratene Zahl sieht hier aus wie eine Messung (`BL-141`).

  **Ein Fund unter dem Fund:** `test_bl152_…` prüft, ob die Eichung das
  **Log-Format** liest — und hing trotzdem an der **aktuellen** Preistabelle.
  Vier Fälle fielen beim Satzwechsel und zeigten auf den Log-Leser, wo der
  Preis stand. Die gemessenen Fixture-Zahlen bleiben unangetastet; für die
  Datei gilt jetzt der Satz, der **zur Messzeit galt**, ausdrücklich als
  solcher benannt. Damit ist auch belegt, dass beide Messungen recht hatten —
  der Satz wurde zwischenzeitlich real gesenkt.

- **`zitat_lint.py` übersah die natürlichste deutsche Vorbedingungs-Bauform**
  (`BL-184`, gemeldet von `Feld B`) — also genau den Fall, als dessen
  Gegenprobe es gedacht ist. *„**Vorbedingung für den ersten Bump:** `BL-6`
  muss vorher erledigt sein"* wurde nach dem Abtragen von `BL-6` **nicht**
  gemeldet, während es in derselben Sitzung fünfmal anschlug, wo nichts war.

  Beide Fehlerrichtungen hatten dieselbe Wurzel: Das Werkzeug beurteilte
  **Absätze nach Stichwörtern** statt **Sätze nach Bezug**. Der Schnitt liegt
  jetzt auf dem Satz (Abkürzungen wie `z. B.` zerschneiden ihn nicht), die
  Vorbedingungs-Bauform steht als eigenes, engeres Muster daneben — nicht als
  weiterer Eintrag in der Wortliste, denn die aufzublähen war schon einmal die
  falsche Antwort. Der Backlog prüft jetzt seine **eigenen Statusfelder** mit:
  absatzweise meldete er dort **29** Zeilen reines Rauschen, feldweise und
  satzweise sind es **0**. Und der grüne Lauf sagt, wann er etwas aussagt —
  *Abtragen zuerst, linten danach*.

- **Der README-Zahlenwächter konnte Kit-Zahlen nicht von Feldzahlen
  unterscheiden** (`BL-180`). Die Herkunftstabelle beschreibt fremde Projekte,
  deren Zahlen legitime andere Zahlen sind; der Wächter las „86 Tests" als
  Behauptung über das Kit. `kit-test.sh` Stufe 3 brach daran ab — nach rund
  45 Minuten. **Ein Selbsttest, der an einer richtigen Angabe stirbt, ist
  teurer als einer, der gar nicht prüft.**

  Gelöst nicht durch Ausblenden der Tabelle (das hielte bis zur nächsten
  fremden Zahl daneben), sondern durch Schärfen: Eine Zahl über ein fremdes
  Projekt nennt ihren **Träger** (`86 Tests in Feld E`, `86 Projekt-Tests`);
  jede unqualifizierte Zahl **ist** eine Aussage über das Kit und wird weiter
  geprüft. `des Kits` zählt nicht als fremder Träger. Der Befund nennt den
  Ausweg, und die Regel steht als Merksatz über der Tabelle selbst.


- ⚠️ **`kit-melden` war auf der pwsh-Bahn komplett funktionsunfähig — der
  Rückkanal Feld → Kit ist dort seit dem ersten Tag tot gewesen** (`BL-182`,
  gemeldet von `Feld B`). `kit-melden.ps1` rief `& $TEAM_PYTHON
  team/tools/kit_meldung.py` auf. Diese Variable gibt es **nur auf der
  bash-Bahn**; hier war sie leer, und `&` auf eine leere Zeichenkette bricht
  ab („must result in a command name"), Exit 1 — für **jedes** der fünf
  Verben, weil alle durch dieselbe Zeile laufen.

  **In einer nie gelaufenen Datei sammeln sich Fehler an, und der erste
  verdeckt die übrigen.** Beim Belegen des Fixes kamen zwei weitere heraus:

  1. **`TEAM_KIT_PFAD` kam nie an**, obwohl er in `team.config.ps1` stand. Die
     Konfiguration wird ins **Modul** dot-gesourct, und was nicht in
     `Export-ModuleMember -Variable` steht, sieht ein Entrypoint nicht.
     `kit-pfad` meldete „Kein Kit gefunden — weder TEAM_KIT_PFAD noch die
     üblichen Ablagen" **genau dann, wenn der Wert eingetragen war.** Das ist
     der Fund, den `BL-153` abstellen wollte, einmal um die Modulgrenze herum
     wiedergekehrt — und auf der bash-Bahn strukturell unsichtbar, weil
     `source` keine solche Grenze kennt.
  2. **`kit-melden.ps1` war der einzige der zehn Entrypoints ohne
     `-DisableNameChecking`.** Die `Import-Module`-Warnung über „unapproved
     verbs" landet auf **stdout**, mit ANSI-Farbe, **vor** der Nutzausgabe —
     und `neu` gibt auf stdout einen Pfad aus, den der Aufrufer weiterverwendet.

  Der Fix folgt der Bauform der Bahn statt sie neu zu erfinden:
  `TEAM_MELDUNG_TOOL` in `team.config.ps1` (mit `{{PYTHON}}`-Platzhalter, den
  beide Installer über dieselbe Ersetzungstabelle ohnehin füllen), zerlegt von
  `Team-Werkzeug` — wie `TEAM_KOSTEN_TOOL` und `TEAM_BEUTEBUCH_TOOL`.

  **Zwei Wächter prüfen die Gattung statt der Stelle** (`BL-154`): Jeder Wert,
  den `team.config.ps1` setzt, muss die Modulgrenze überleben (einmal am Text,
  einmal am **laufenden** Modul — heute 27 von 27, fehlalarmfrei), und jeder
  Entrypoint importiert `lib.psm1` ohne Namensprüfung (vorher stand es 9 zu 1).

  **Nachweis:** 10 Fälle in `test_bl182_rueckkanal_auf_der_pwsh_bahn.py`,
  darunter alle fünf Verben end-to-end gegen ein Fixture-Projekt unter echtem
  `pwsh`. **Gegenprobe:** jede der drei Hälften einzeln zurückgedreht → 6, 8
  und 8 der 10 Fälle fallen; wieder eingesetzt → 10 grün.

- **`BL-144` war DOPPELT vergeben — aktiver Backlog und Archiv trugen unter
  derselben Nummer zwei verschiedene Funde** (`BL-188`). Am 2026-08-21 vergaben
  zwei Maschinen dieselbe Nummer: die Ausführungsrichtlinie per
  Gruppenrichtlinie (aus `Feld B`) und der rote bash-Selbsttest seit `BL-136`.
  Beide waren gepusht, bevor es auffiel — die sonst geltende Regel „die
  ungepushte Seite zieht um" hatte damit keinen Ansatzpunkt mehr.

  **Aufgelöst nach der Zahl der Verweise:** acht zeigen auf den bash-Selbsttest,
  vier auf die Ausführungsrichtlinie. Die vier sind mitgezogen — einzeln
  geprüft, nicht pauschal ersetzt, denn die Verweise waren zwischen beiden
  Bedeutungen gemischt, und genau das war der Schaden. Die
  Ausführungsrichtlinie heißt jetzt **`BL-189`** und sagt in ihrem Status, wie
  sie vorher hieß; `Feld B` hat seine Quittung nachgezogen.

  **Der Prüfbefehl ist jetzt ein Test, kein Vorgehen.** Der Fund entstand aus
  einem `grep | sort | uniq -d`, den jemand von Hand fuhr, weil die Gegenprobe
  gegen das Archiv Teil seines *Vorgehens* war und nicht Teil seines Auftrags —
  eine Handprüfung gilt genau einmal.
  `test_bl188_jede_nummer_nur_einmal.py` prüft die Gattung: keine Nummer in
  beiden Dateien, keine zweimal in derselben, und der umgezogene Eintrag nennt
  seinen alten Namen. **Gegenprobe:** Kollision wörtlich wiederhergestellt →
  der Fall fällt und nennt `BL-144`.

- ⚠️ **Den Block „Bitte von Hand abgleichen" hatte nur `install.sh` — die
  pwsh-Bahn sagte einem Projekt nie, dass ihm Regeln aus einer neueren
  Kit-Fassung fehlen** (`BL-178`). Doku-Dateien tragen Projektanpassungen und
  werden vom Update zu Recht nicht überschrieben; der Mensch muss aber
  erfahren, dass sich die Kit-Fassung geändert hat — sonst laufen die
  **Regeln** im Projekt der Mechanik hinterher, und das war die Hälfte des
  `BL-4`-Fehlers. Gemessen war der Fund als `grep -c`: `install.sh` 1,
  `install.ps1` 0; die drei ähnlich klingenden Blöcke dort (Gitignore-,
  Gitattributes-, Python-Abgleich) sind andere Prüfungen.

  Es ist dieselbe Gattung wie `BL-145` („grün bedeutet auf den beiden Bahnen
  verschieden viel"), nur bei den **Regeln** statt bei den Tests. Der
  Feldbeleg lag schon vor: `Feld B` ist pwsh-only, ist mehrfach aktualisiert
  worden und hat diese Meldung nie bekommen — ein Teil der Antwort darauf,
  warum die kaputte `CLAUDE.md` dort so lange unbemerkt blieb (`BL-177`).

  **Portierung, kein Neuentwurf**, mit allen vier Auflagen: in den TEMP-Bereich
  rendern statt ins Projekt (eine uncommittete Datei außerhalb der Whitelist
  sieht für den Read-Only-Guard aus wie ein Regelbruch); Zeilenenden ausnehmen
  — `Get-Content` zerlegt an CRLF **und** LF und liefert die Zeilen ohne
  Wagenrücklauf, `--strip-trailing-cr` braucht es hier also nicht; einen auf
  **dieser** Bahn ausführbaren Befehl nennen (`Compare-Object`, kein `diff`,
  das Windows nicht kennt — Bauart `BL-44`); und sagen, dass eine Abweichung
  bei `CLAUDE.md` **normal** ist.

  **Ein bewusster Unterschied, benannt statt verschwiegen:** `Compare-Object`
  vergleicht als Menge — eine reine Umsortierung fällt nicht auf.
  `-SyncWindow 0` ließe dagegen eine einzige eingefügte Zeile alle folgenden
  als abgewichen gelten.

  **Nachweis, zweistufig:** 13 Fälle in
  `test_bl178_abgleich_auf_beiden_bahnen.py` (Gleichstand, die vier Auflagen
  einzeln, und das Verhalten der echten Vergleichsfunktion über den
  Syntaxbaum), dazu vier Prüfungen in `kit-test.ps1` Schritt 5 gegen eine
  echte Installation mit präparierter Projektregel — der Block muss die
  Abweichung **finden**, nicht nur laufen.

  **End-zu-End gefahren:** frische Installation, eigene Projektregel in
  `CLAUDE.md`, neue Regel in der Kit-Vorlage, dann `-Update`. Gemeldet wird
  `CLAUDE.md … (2 Zeilen)` und **nicht** `TEAM.md`; der genannte Befehl,
  wörtlich ausgeführt, liefert dieselben 2 Zeilen. Die installierte Datei trug
  dabei eine CRLF-Zeile, die **keinen** Fehlalarm erzeugte, und im Projekt
  blieb nichts liegen.

- ⚠️ **Die pwsh-Bahn sammelte die Ausgabe jeder Rolle ein, statt sie zu
  streamen — Konsole und Lauf-Log blieben während des Laufs stumm** (`BL-181`,
  gemeldet von `Feld B` mit vollständiger Messreihe). In `Rolle-Starten` stand
  `$ausgabe = & pwsh … 2>&1` mit einer `foreach`-Schleife danach. Die
  Zuweisung sammelt den **kompletten** Kindprozess ein, bevor die erste Zeile
  herauskommt; weil Konsole und `Add-Content` in derselben Schleife hingen,
  schwiegen beide Hälften gemeinsam. Auf der bash-Bahn erledigt das eine
  einzige Zeile ganz oben — `exec > >(tee -a "$LAUF_LOG") 2>&1` —, und jeder
  Kindprozess erbt den Strom.

  **Gemessen, nicht vermutet** (66-Minuten-Lauf, Takt 15 s gegen die Spuren
  auf der Platte):

  ```
  20:18:35  logbytes=53     state=10
  20:44:46  logbytes=53     state=16   ← SIEBEN Stufen gebaut, Log unverändert
  20:53:19  logbytes=1672   state=17   ← Bau-Rolle endet: 31 Zeilen auf einen Schlag
  21:19:19  logbytes=6086              ← Abschlussbericht
  ```

  Jeder Sprung liegt exakt auf einem Rollenende: **Die Puffergrenze ist der
  Kindprozess.** Die Bau-Rolle ist ein Aufruf für alle Stufen und belegte 40
  der 66 Laufminuten — 61 % des Laufs in einem stummen Block. Ein Lauf ohne
  Lebenszeichen ist von einem hängenden nicht zu unterscheiden, und die
  naheliegende Reaktion darauf ist die teuerste: Der Abbruch wirft bezahlte
  Stufen weg. Dieselbe Lehre wie `BL-176`/`BL-179`, hier an der Stelle, die am
  längsten schweigt.

  **Die zweite Hälfte des Schadens war `team-status`:** Es zeigt „die letzten
  3 Zeilen" des Lauf-Logs — während des Laufs gab es sie nicht. Das
  mitgelieferte Monitoring-Werkzeug war genau in dem Zeitraum blind, für den
  man es aufruft, und zeigte dabei keinen Fehler, sondern eine stundenalte
  Zeile, die aussah wie die aktuelle.

  **Nachweis:** 5 Fälle in `test_bl181_lauf_log_streamt.py`. Der Test prüft
  ausdrücklich **nicht**, dass am Ende Zeilen im Log stehen — das taten sie
  vorher auch, und genau daran ist der Fehler so lange vorbeigelaufen. Er
  prüft, dass sie **vor** dem frühestmöglichen Ende der Rolle dort stehen.
  **Gegenprobe, zweifach:** die alte Bauform wörtlich als Sonde (bleibt stumm)
  und die echte Funktion zurückgedreht → 3 der 5 Fälle fallen.

  **Was offen bleibt:** `team-status --watch` zeichnet den Block periodisch
  neu, statt anzuhängen — ein eigener Entwurf, der an `BL-183` hängt.

- ⚠️ **`kosten.py sitzung-messen --projekt` fand unter Windows NIE ein
  Transkript — leeres Ergebnis, kein Fehler, Exit 0** (`BL-186`, gemeldet von
  `Feld B`). `transkripte_aus_projekt()` bildete den Ordnernamen mit
  `voll.replace(os.sep, "-")`. Das ersetzt den Trenner `\`, lässt aber den
  **Doppelpunkt des Laufwerks** stehen: Gesucht wurde `C:-Users-…`, der Ordner
  heißt `C--Users-…`.

  Das trifft den **einzigen** Befehl, den das Architekten-Briefing für die
  Frage „woher kommt `<USD>`?" nennt. Wer der Meldung „kein Transkript
  gefunden" glaubt, schließt daraus, es gebe nichts zu buchen — und die
  Architektenkosten bleiben strukturell unerfasst.

  Beim Nachmessen kam eine zweite Abweichung heraus: Auf der Fundmaschine
  liegen `C--Users-…-team-kit` und `c--Users-…-duke-itam-2026`
  **nebeneinander** — derselbe Wirt, dasselbe Laufwerk, einmal groß und einmal
  klein. Der Laufwerksbuchstabe kommt aus dem Arbeitsverzeichnis des
  aufrufenden Prozesses. Gesucht wird deshalb in zwei Stufen: erst der exakte
  Name (auf POSIX unverändert), dann ein Vergleich über eine lockere Form.
  **Nachgemessen:** vorher 0 Transkripte, jetzt 9 bzw. 37.

  **Der zweite Teil ist plattformunabhängig und eine Entscheidung, keine
  Reparatur:** Die Funktion lieferte nur das zuletzt geänderte Transkript,
  während Docstring und Nutzungszeile im Plural sprachen. `sitzung-messen`
  misst weiterhin **eine** Sitzung — das ist sein Name. Was aufhört, ist die
  Stille: Liegen mehrere vor, nennt der Aufruf ihre Zahl und den neuen
  Schalter `--alle`. Briefing, `bootstrap/TEAM.md` und FAQ sagen es ebenfalls.

  **Nachweis:** 11 Fälle in `test_bl186_transkripte_unter_windows.py` — der
  Ordnername ist dafür in eine eigene Funktion gezogen, die sich auf **jedem**
  Wirt befragen lässt. Genau daran ist der Fund drei Monate vorbeigelaufen.
  **Gegenprobe:** beide Hälften einzeln zurückgedreht → je 3 Fälle fallen.

### Fixed (Doku)

- **Sechs Backlog-Zeilen verlinkten ihre Meldungsdatei ins Leere.** Die am
  2026-08-26 eingetragenen Zeilen schrieben `](plans/meldungen/…)` — aus
  `plans/backlog.md` heraus zeigt das auf `plans/plans/meldungen/…`. Die
  Anzeige bleibt der volle Pfad, das Ziel ist jetzt relativ, wie bei den zwei
  älteren Zeilen.

_Sonst nichts Offenes aus dieser Version. Die 9 offenen Backlog-Einträge sind_
_fünf Meldungen aus `Feld E` (`BL-169`, `BL-171`…`BL-174`), eine aus `Feld B`_
_(`BL-185`) und drei eigene Vorhaben am Kit (`BL-117`, `BL-145`,_
_`BL-189`) — siehe_
_[plans/backlog.md](plans/backlog.md)._

## [2.13.1] — 2026-08-25

**Vier Funde, ausgelöst durch eine Frage statt durch eine rote Zeile:**
„Hängt der Installer beim Selbsttest?" Er hing nicht — er war stumm
(`BL-176`). Beim Nachsehen lag darunter der schwerere Fund (`BL-175`), beim
Abtragen fiel dessen Rest heraus (`BL-177`), und beim Aufräumen zeigte sich,
dass die Selbsttests selbst noch stumm liefen (`BL-179`).

### Fixed

- ⚠️ **`TEAM.md` fiel durch JEDES Update — die Bedienungsanleitung blieb auf
  dem Stand des Einzugstags** (`BL-175`). Beide Installer rendern sie nur bei
  der Erstinstallation. `Kopiere-Infrastruktur` kennt sie nicht, und in der
  Liste „Unangetastet geblieben (Projektdaten)" steht sie auch nicht — sie
  fiel zwischen beide Listen. Das fällt nicht auf: **Eine veraltete Anleitung
  sieht aus wie eine Anleitung.**

  Der Schaden ist zweigeteilt, und der zweite Teil ist der schwerere:

  1. Exit-Codes, Befehle, Fehlersuche — alles, was das Kit seit dem Einzug
     gelernt hat, kommt in einem aktualisierten Projekt nie an.
  2. In einer **einbahnigen** Ablage nennt die alte Fassung die **abgewählte**
     Bahn. Im Feld standen in einer `--nur-pwsh`-Installation **15 tote
     `.sh`-Pfade** in `TEAM.md`; der Text schickte jeden Leser an Dateien, die
     es dort nicht gibt.

  Punkt 2 ist genau der Befund, den `BL-139` abgestellt hat. `TEAM.md` blieb
  übrig, **weil die Reparatur am Rendern ansetzte** — ein Fix an einer Vorlage
  repariert die nächste Installation, nicht die bestehende.

  Beide Installer ziehen `TEAM.md` jetzt im Update-Pfad mit, direkt neben den
  Briefings. `CLAUDE.md` bleibt ausdrücklich draußen: Die trägt Projektarbeit.
  Im selben Zug ist `TEAM.md` aus dem `BL-12`-Abweichungswarner genommen — sie
  wird gerendert und weicht deshalb immer von der Kit-Fassung ab, genau wie die
  Briefings; ein Warner, der bei jedem Lauf dieselbe Datei meldet, erzieht
  dazu, ihn zu überlesen (`BL-14`).

  **Nachweis:** Update im Feldprojekt gefahren, `315 passed, 420 skipped`,
  Exit 0 — die drei roten Fälle (`BL-139` zweimal, `BL-140`) sind weg.

- **Der Selbsttest lief stumm — und ein stummer Lauf ist von einem hängenden
  nicht zu unterscheiden** (`BL-176`). Beide Installer leiteten den
  pytest-Lauf ihres Selbsttests vollständig in eine Logdatei um. Auf dem
  Bildschirm stand `Selbsttest`, danach minutenlang nichts. Gemessen: Der
  Prozess lief 3 min 41 und war zu keinem Zeitpunkt hängengeblieben. Die teure
  Antwort auf die Frage „hängt das?" ist der Abbruch — er wirft einen gesunden
  Lauf weg, der nur Geduld gebraucht hätte.

  `Pytest-Mitschnitt` (pwsh) und `pytest_mitschnitt` (bash) schreiben jetzt
  beides: roh ins Log, eingerückt auf den Bildschirm. Drei Teile, ohne die es
  nur halb wirkt:

  | | Warum es sonst nicht wirkt |
  |---|---|
  | `PYTHONUNBUFFERED=1` | Python puffert in eine Pipe blockweise — die Zeilen kämen erst am Schluss, der Hänger wäre nur kürzer |
  | Log bleibt **roh** | Die Einrückung entsteht erst nach `tee` für den Bildschirm. Sonst brechen die Auswertungen der Aufrufer, die aus dem Log lesen |
  | Exit-Code überlebt die Pipe | `$LASTEXITCODE` nach der Pipeline bzw. `set -o pipefail`. Sonst meldet `sed` grün, was pytest rot gemeldet hat |

  **Nicht umgestellt** sind die Transkript-Umleitungen in
  `kit-test.ps1`/`kit-test.sh`, die die Installer-Ausgabe einfangen — dort ist
  die Stille gewollt, sonst flutet ein Lauf mit 17 Installer-Aufrufen das
  Terminal.

- **Ein Projekt, das vor `BL-139`/`BL-140` einzog, behält seinen kaputten
  Regeltext — und kein Update sagt das je** (`BL-177`). Der Rest, den `BL-175`
  ausgewiesen hat: `TEAM.md` ließ sich nachziehen, `CLAUDE.md` **nicht**. Sie
  trägt Projektarbeit — gefüllte TODO-Stellen, eigene Regeln —, und ein
  Installer, der darin ersetzt, überschreibt fremde Arbeit (`BL-12`).

  Der Fehlermodus ist still. Ein totes `ralph.sh` scheitert sichtbar; ein
  `team.config.sh`, in das eine Rolle `TEAM_SMOKE_TEST` eintragen soll, während
  `team/lib.psm1` `team.config.ps1` liest, scheitert nie — der Wert wird
  eingetragen und nie gelesen.

  Beide Installer melden den Zustand jetzt beim Update: welche Pfade tot sind,
  welche Nummern blank, und die Zuordnung für **diese** Ablage. **Repariert
  wird ausdrücklich nicht**, und die Meldung sagt auch, warum nicht.

  Zwei Bauentscheidungen machen ihn erst brauchbar: Die Zwei-Bahnen-Region wird
  ausgeschnitten (sonst Fehlalarm in **jeder** einbahnigen Ablage — und ein
  Wächter mit Fehlalarm wird abgeschaltet statt befolgt, `BL-143`), und die
  Kit-Nummern kommen aus der **Vorlage** statt aus einer Liste im Installer
  (eine Liste wäre ab der nächsten Nummer falsch, `BL-154`).

  Daher findet er am Feldtext **7** blanke Nummern, wo der `BL-140`-Wächter
  dort 5 fand: Er misst gegen den Maßstab des Kits, nicht gegen den Backlog des
  Projekts.

- **Auch die Selbsttests liefen stumm — der längste Lauf des Kits am längsten**
  (`BL-179`). `BL-176` hat die Suite-Läufe der beiden **Installer** sichtbar
  gemacht und die Selbsttests übersehen, wo derselbe Fehler schwerer wiegt:

  | Stelle | war still |
  |---|---|
  | `kit-test.ps1`, ein direkter Suite-Lauf | ~14 min |
  | `kit-test.sh`, Stufe 8, zwei Läufe | Stufe 8 dauert ~55 min |

  Dieselbe Bauart wie `BL-176` an allen drei Stellen. In `kit-test.sh` als
  **ein** Helfer statt zweier Abschriften — zwei Fassungen desselben Aufrufs
  laufen irgendwann auseinander.

  Der Wächter prüft die **Gattung**, nicht die drei bekannten Stellen: Kein
  Selbsttest und kein Installer darf einen pytest-Lauf, der ein
  Testverzeichnis nennt, vollständig in eine Datei umleiten. Dass er dabei
  einen **Lauf** von einer `--version`-**Probe** unterscheidet, ist keine
  Feinarbeit, sondern die Bedingung: Der erste Entwurf hatte die
  Unterscheidung nicht und meldete drei Proben als Befund — ein Wächter, der
  an einer richtigen Stelle rot schlägt, wird abgeschaltet statt befolgt
  (`BL-143`).

  **Die Ausnahme steht ausdrücklich unter Test:** `kit-test.ps1` fängt die
  Installer-Ausgabe weiter als **Transkript** ein. Ein Lauf mit 17
  Installer-Aufrufen würde das Terminal sonst fluten und genau den Fortschritt
  erschlagen, den dieser Fix sichtbar macht. Ein Transkript wird **nach** dem
  Lauf gelesen, ein Fortschritt **während**.

### Changed

- Die Hilfe beider Installer nennt bei `--update`/`-Update` jetzt **beide**
  Seiten: was aktualisiert wird (Entrypoints, Bibliothek, `team/`-Werkzeuge,
  Briefings, Tests und `TEAM.md`) und was ausdrücklich unangetastet bleibt
  (`team.config.*`, `CLAUDE.md`, `CHANGELOG.md`, Ledger, State, `plans/`).
  Dass `TEAM.md` in keiner der beiden Aufzählungen stand, war die Lücke, durch
  die `BL-175` fiel.

**Was diese Version NICHT bringt:** `BL-178` — `install.ps1` fehlt der Block
„Bitte von Hand abgleichen", den `install.sh` seit langem fährt. Beim Bauen von
`BL-177` gefunden, ausgewiesen statt verschwiegen, und ein Teil der Antwort
darauf, warum der kaputte Regeltext im Feld so lange unbemerkt blieb.

## [2.13.0] — 2026-08-25

**Die Runde, in der die pwsh-Bahn ihren Selbsttest bestanden hat.** `BL-146`
war seit dem 2026-08-21 der Eintrag, der alles andere trug: Vier Testfälle und
drei Code-Stellen der pwsh-Bahn waren geschrieben und **nie ausgeführt**
worden, und bis zum Release wuchs die Liste auf die gesamte pwsh-Hälfte des
Rückkanals. Alles davon war eine Behauptung mit Testkörper.

Am 2026-08-25 ist `bash bash/kit-test.sh` auf einer echten Windows-Maschine
durchgelaufen: **11 von 11 Stufen, 141 Prüfungen grün, Exit 0.** Damit ist die
zweite Bahn keine Herleitung mehr.

**Der Ertrag war nicht der grüne Lauf, sondern die sechs davor.** Der Erstlauf
hat sechs Einträge erzeugt, und **fünf davon sind auf einem Linux-Wirt
prinzipiell unsichtbar**:

| | Was nur ein Windows-Lauf zeigt |
|---|---|
| `BL-158` | Die Kit-eigenen Prüfer starben unter cp1252 auf ihrer **Erfolgs**-Spur — `kit-test.sh` hätte das als inhaltlichen Befund gemeldet, den es nicht gibt |
| `BL-159` | `kit-einrichten.sh` fällte ein POSIX-Urteil über einen Windows-Wirt und riet zu einem Paket, das es dort nicht gibt |
| `BL-160` | `--verknuepfen` meldete „✓ Verknüpft" und legte eine **Kopie** an — die Reparatur erzeugte den Schaden, gegen den sie gebaut ist |
| `BL-161` | Ein MSYS-Pfad in `pwsh -Command` ließ die Syntaxprüfung **null** statt achtzehn Dateien sehen — wirkungslos, nicht bloß rot |
| `BL-162` | Der Gleichstands-Prüfer **starb an seinem eigenen Befund**: `diff` endet mit 1, wenn es etwas findet |
| `BL-163` | Dieselbe Marke, zwei Werte — der erste **gemessene** Fall der Gattung, die `BL-117` seit Tagen benennt |

**Kein einziger fallender Fall wurde grün gedreht.** In jedem Fall lag der
Fehler im Werkzeug oder in der Erwartung, nie im Testkörper — genau das, was
`BL-146` als Bedingung formuliert hatte: *„Fällt er, ist entweder der Fix
falsch oder der Test — und die Antwort steht im Fall selbst."*

Dazu die beiden fehlenden Hälften der pwsh-Bahn, die den Anlass für die Sitzung
gaben: `BL-155` (die Wurzel-Code-Prüfung aus `BL-52`) und `BL-156` (`-Hilfe`
für `install.ps1`). Feldbefunde sind mit ⚠️ markiert.

### Added

- **`install.sh` beantwortet `-h` / `--hilfe` / `--help` mit seiner
  Optionsliste.** Bisher gab es keinen Weg, die Schalter des Installers zu
  erfahren, ohne die Datei zu öffnen — und `kit-einrichten.sh`, das Skript
  davor, kann es seit jeher.

  **Der Hilfetext ist der Dateikopf, keine zweite Fassung daneben.** Das ist
  dieselbe Erwägung wie bei `BL-154`: Eine Abschrift läuft irgendwann
  auseinander, und dann sagt `--hilfe` etwas anderes als die Datei. Gelesen
  wird ab Zeile 3 — Zeile 1 ist die Shebang, Zeile 2 die Bahn-Kopfzeile,
  beides Maschinensache — bis zur ersten Zeile, die kein Kommentar mehr ist.
  Anders als das feste `sed -n '2,30p'` in `kit-einrichten.sh` hat die Fassung
  hier keine Zeilennummer im Bauch: Wächst der Kopf, wächst die Hilfe mit,
  statt mitten im Satz abzuschneiden.

  **Dabei ist herausgekommen, dass die Liste gar nicht vollständig war.**
  `--nur-bash`, `--nur-pwsh` und `--beide-bahnen` standen nur in der
  `Aufruf:`-Zeile und wurden nirgends erklärt — die drei Schalter also, mit
  denen man eine Bahn abwählt (`BL-119`) und mit `--update` zurückholt
  (`BL-147`). Sie sind jetzt erklärt, dazu `<zielpfad>` als Pflichtangabe. Und
  der Abbruch „Kein Zielpfad angegeben" nennt `--hilfe`: Das ist der Weg, auf
  dem die Liste ohne Vorwissen gefunden wird.

  **Die pwsh-Hälfte wurde als `BL-156` ausgewiesen statt blind mitgeschrieben**
  — die Lehre aus `BL-113`/`BL-117` — und ist am 2026-08-24 auf der
  Windows-Maschine nachgezogen worden (siehe den nächsten Eintrag).

- **`install.ps1` beantwortet `-Hilfe` / `-Help` / `-h` mit seiner Optionsliste,
  und sein Kopf erklärt endlich die drei Bahn-Schalter** (`BL-156`). Dieselbe
  Bauart wie auf der bash-Bahn: Der Hilfetext **ist** der `<# … #>`-Block am
  Dateianfang, gelesen zur Laufzeit aus `$PSCommandPath`. Die drei Aliasse
  bilden `-h`/`--hilfe`/`--help` nach — ein Wechsel der Bahn soll kein Wechsel
  der Gewohnheit sein. Der Abbruch „Kein Zielpfad angegeben" verweist auf
  `-Hilfe`, wie drüben auf `--hilfe`.

  **Der schwerere Teil war der Kopf, nicht der Schalter.** `-NurBash`,
  `-NurPwsh` und `-BeideBahnen` standen ausschließlich in `param()` — anders
  als in `install.sh` nicht einmal in der `Aufruf:`-Zeile. Wer unter Windows
  eine Bahn abwählen (`BL-119`) oder mit `-Update` zurückholen (`BL-147`)
  wollte, fand im Skript keinen Hinweis darauf, dass das überhaupt geht. Beide
  Köpfe erklären jetzt dieselben Schalter.

  **`Get-Help` wäre der pwsh-übliche Weg gewesen und ist es nicht geworden —
  gemessen, nicht vermutet.** Auf der Zielmaschine (pwsh 7.6.5) findet
  `Get-Help` den `<# … #>`-Block **nicht**, solange die Zeile
  `# Bahn: pwsh | Gegenstueck: install.sh` davorsteht: Die Ausgabe schrumpft
  auf die blanke Syntaxzeile. Ohne die Bahn-Zeile funktioniert es. Die
  Bahn-Zeile ist aber nicht verhandelbar — `test_bahn_kopfzeile.py` verlangt
  sie in den ersten drei Zeilen, und sie ist die einzige Stelle, an der eine
  Datei ihre Bahn selbst nennt. Also liest die Hilfe die eigene Datei, statt
  den Kopf für ein Werkzeug umzubauen. Genau diese Frage hatte `BL-156` auf
  die Maschine verwiesen, auf der sie beantwortbar ist.

  **Geprüft wird am LAUF, nicht am Quelltext**
  ([`test_bl156_installer_hilfe.py`](geteilt/tests/test_bl156_installer_hilfe.py),
  13 Fälle): Beide Installer werden wirklich gestartet — das geht ohne
  Zielprojekt und ohne Installation. Der tragende Fall vergleicht die Ausgabe
  **zeichenweise mit dem Dateikopf**; er fällt, sobald daneben eine zweite
  Fassung entsteht. Ein Fall hält zusätzlich die `Get-Help`-Messung fest, damit
  die Entscheidung nicht später still zurückgedreht wird.

- **Der Rückkanal Feld → Kit ist ein Werkzeug statt einer Konvention**
  (`BL-153`). Neu im Zielprojekt: `kit-melden.sh` / `.cmd` mit
  `team/tools/kit_meldung.py` dahinter — `neu` legt einen Meldungsentwurf nach
  Vorlage an, `pruefen` redigiert ihn, `senden` legt über `gh` einen Pull
  Request gegen das Kit-Repo an. Im Kit dazu die Empfangsseite:
  [`CONTRIBUTING.md`](CONTRIBUTING.md), eine PR-Vorlage und `plans/meldungen/`.

  **Der Anlass war nicht die fehlende Automatik, sondern ein fest verdrahteter
  Pfad.** Die drei Stellen, die bisher sagten, wohin ein Kit-Fund gehört,
  nannten alle `~/Source/team-kit` — die Ablage **einer** Maschine. Das
  installierte Projekt wusste nirgends, wo das Kit liegt: `TEAM_KIT_PFAD` gab es
  nur im Launcher auf der Kit-Seite. Wer woandershin geklont hatte, bekam eine
  Anweisung ins Leere; ein fremder Nutzer ohnehin, und der hat zusätzlich kein
  Schreibrecht. `TEAM_KIT_PFAD` steht deshalb jetzt in **beiden**
  Konfigurationen und wird von **beiden** Installern gefüllt — in `install.sh`
  in beiden Füll-Routinen, weil Erstinstallation und Update getrennte haben.

  **Drei Entscheidungen tragen den Entwurf:**

  - **Der Loop schreibt, der Mensch sendet.** `neu` und `pruefen` dürfen
    automatisch laufen; `senden` verlangt eine Bestätigung und verweigert ohne
    Terminal den Dienst. Ein Pull Request wirkt nach außen und lässt sich nicht
    zurückholen — und die Meldung schreibt eine Rolle, die gerade eine **fremde,
    private** Codebasis gelesen hat. Das ist *Finder ≠ Fixer*, angewandt auf den
    Rückkanal.
  - **Die Redaktionsprüfung ist ein Gate, kein Hinweis.** Sie sucht absolute
    Pfade, Konto-, Rechner- und **Projektnamen**, E-Mail, schlüsselartige
    Zeichenketten und offene TODO-Marken (Exit `4`). Der Projektname steht
    bewusst darin: Das Kit führt seine eigenen Feldbelege aus genau diesem Grund
    unter `Feld A`…`Feld D`. `--ja` bestätigt das **Senden**, nicht die Befunde
    — dafür gibt es `--trotzdem`.
  - **Ein PR legt eine neue Datei unter `plans/meldungen/` an** und rührt
    `plans/backlog.md` nicht an. Sonst kollidiert jede zweite Meldung an
    derselben Stelle, und der `BL-n`-Nummernraum wird zum Wettlauf zwischen
    Leuten, die voneinander nichts wissen. Die Nummer vergibt der Maintainer
    beim Triage.

  Ohne `gh` fällt `senden` auf einen vorbefüllten **Issue-Link** zurück; ein
  Browser und ein Konto genügen. Und die Meldung wird **immer** als Datei
  abgelegt, auch ohne erreichbares Kit — ein Eintrag, der nur im Feld liegt, hat
  eine Verfallszeit, sie endet beim nächsten `--update`. Genau so ging `BL-42`
  verloren und musste als `BL-58` ein zweites Mal gemeldet werden.

  **Zwei Funde kamen aus den eigenen Tests und sind im Werkzeug behoben, nicht
  im Test:** Die Prüfung meldete zunächst nur den *ersten* Grund je Zeile — der
  auffälligste Befund verdeckte damit die leiseren, und wer zweimal nachbessern
  muss, um alles zu sehen, sendet nach dem ersten Mal. Und ein ausdrücklich
  getipptes `--kit`, das nicht auf ein Kit zeigte, wich **still** auf ein
  anderes aus; das ist jetzt ein Bedienfehler, während ein veraltetes
  `TEAM_KIT_PFAD` aus der Konfiguration weiterhin mit Ansage übersprungen wird
  (eine Konfiguration darf veralten, ein Tastendruck nicht).

  **Belegstand:** `neu`, `pruefen`, `issue-link` und die Suchkaskade sind auf
  der bash-Bahn gefahren, 28 neue Testfälle. **Der Pull Request selbst ist
  nicht abgenommen** — `kit-test.sh` kann keinen echten anlegen, und bisher ist
  keiner angekommen.

- **Das README sagt jetzt im Kopf, was das hier ist und für wen** — und stellt
  den Antrieb nach vorn, statt ihn über sechs Dokumente zu verteilen. Zwei neue
  Abschnitte:

  - **„Was das ist — und für wen"** steht **vor** dem Schnellstart, weil ein
    Leser, der die Sache noch nicht kennt, nicht zuerst auf ein
    `git clone` stoßen sollte. Drei Blöcke: Regiepult statt Autopilot; die
    Zielgruppe (erfahrene Entwickler in der Rolle eines fachlich orientierten
    Stakeholders — PO, Chefentwickler, Tech Lead); und der Antrieb in einem
    Satz. **Die Zielgruppe ist dabei als Betriebsbedingung formuliert, nicht
    als Empfehlung:** *Finder ≠ Fixer* endet bei einem Menschen, der den Fund
    beurteilen können muss. Wer den Diff nicht liest, macht aus dem Beutebuch
    eine Ablage.
  - **„Der Antrieb: Nutzen je Token"** bündelt die vier Kostenhebel, die
    bisher einzeln in `CLAUDE.md.vorlage`, Anhang A und dem Architekten-
    Briefing standen: zwei Modellstufen, Caps mit zwei Schwellen, Messen statt
    Schätzen, und der Commit als Buchungseinheit. Dazu die Gegenrechnung zum
    Chatfenster (monoton wachsender Kontext gegen prozessfrischen Kontext je
    Stufe) und eine Grenze, damit kein Sparversprechen entsteht: Das Kit senkt
    nicht den Preis je Token, sondern die Zahl der für nichts verbrannten.

  **Die Wortwahl „Nutzen je Token" statt „Kosten" ist Absicht** und deckt sich
  mit der Modell- und CLI-Agnostik des Kits: Für ein lokales Modell offline
  kostet der Token kein Geld, sondern Zeit, Strom und Kontextfenster. Es ist
  dieselbe Optimierung mit anderen Einheiten — damit ist das Fernziel lokal
  kein Anhängsel, sondern die Konsequenz.

  **Zur Rolle von Git wurde vorher geprüft, statt sie zu behaupten.** Feine,
  atomare Commits sind im agentischen Programmieren **verbreitete
  Empfehlung** — als Praxis also *kein* Alleinstellungsmerkmal. Der belegbare
  Unterschied ist, wer sie durchsetzt und wozu sie dienen: Anderswo ist der
  Commit eine Empfehlung an den Menschen und der Rückweg ein editor-lokaler
  Snapshot (ohne Diff, nicht teilbar, nicht in der Historie). Hier ist er ein
  **Zustandsübergang der Maschine** und trägt drei Lasten gleichzeitig —
  Bedingung des Fortschritts (`.ralph-state` schaltet erst nach dem Commit,
  Fehlklasse `43`), Buchungseinheit des Geldes (Ledger, Cap, Rollback setzen
  dort an) und Prüfeinheit des Menschen (ein Diff je Stufe ist die Portion,
  in der Kontrolle ausübbar bleibt). So steht es im README, und der
  Alleinstellungsanspruch liegt ausdrücklich **nicht** auf Git allein.

### Fixed

- ⚠️ **Dieselbe Marke, zwei Werte — der Fall, den `BL-117` vorhergesagt hat**
  (`BL-163`). Der erste Gleichstands-Vergleich der beiden Installer auf einer
  echten Windows-Maschine fand genau **einen** inhaltlichen Unterschied:

  ```
  install.sh    TEAM_KIT_PFAD = C:/Users/…/team-kit
  install.ps1   TEAM_KIT_PFAD = C:\Users\…\team-kit
  ```

  Beide Installer schreiben **beide** Konfigurationen. In einer mit
  `install.ps1` erzeugten Ablage stand die Rückstrich-Form also auch in
  `team.config.sh`.

  **Nachgemessen ist keine der beiden Formen kaputt:** Beide werden in bash
  (auch nach dem Sourcen der Konfiguration), in Python und in PowerShell
  korrekt aufgelöst. Der Pfad zeigte nie ins Leere.

  **Die Wirkung lag woanders.** `kit-test.sh` Stufe 11 prüft „beide Installer
  erzeugen denselben Baum", und diese Prüfung war damit auf Windows **dauerhaft
  rot**. Eine Prüfung, die immer rot steht, wird nicht gelesen (`BL-14`) — und
  sie ist die einzige, die einen *echten* Auseinanderlauf der beiden Installer
  fände. Der harmlose Unterschied hätte den schädlichen verdeckt.

  `install.ps1` normalisiert den Wert jetzt auf Schrägstriche; die bash-Fassung
  bleibt unverändert, weil die MSYS-Schicht dort ohnehin schon diese Form
  liefert. Genommen wurde die Schrägstrich-Form, weil sie in allen drei
  Sprachen ohne Maskierung durch jeden Kontext geht — ein Rückstrich tut das in
  bash ausdrücklich nicht.

  **Der Zusammenhang mit `BL-117` ist der eigentliche Ertrag.** Jener Eintrag
  hält fest, dass der Prompt-Gleichstand am *Quelltext* bewiesen ist und nicht
  am *Lauf*, und benennt die Lücke wörtlich: „Setzen die beiden Bahnen in
  denselben Platzhalter **verschiedene Werte** ein … sind die Prompts
  verschieden und der Test bleibt grün." Das hier ist der erste **gemessene**
  Fall dieser Gattung. Er traf nicht einen Rollen-Prompt, sondern
  `team.config.*` — dieselbe Mechanik, anderer Adressat.

  Im selben Zug nimmt Stufe 11 `.pytest_cache` aus dem Vergleich, mit derselben
  Begründung, mit der `__pycache__` schon draußen war: `lastfailed` entsteht
  nur, *wenn* etwas fehlschlug, und `nodeids` hängt am Stand der Testdateien im
  Moment des Laufs. Beides beschreibt den Testlauf, nicht das Erzeugnis des
  Installers.

- ⚠️ **Der Gleichstands-Prüfer starb an seinem eigenen Befund** (`BL-162`).
  Stufe 11 von `kit-test.sh` misst, ob `install.sh` und `install.ps1` denselben
  Baum erzeugen:

  ```
  W_DIFF="$(diff -r --exclude=.git "$W_A" "$W_B" | head -20)"
  ```

  `diff` endet mit **1**, wenn es Unterschiede gibt — also genau in dem Fall,
  für den die Prüfung existiert. Unter `set -euo pipefail` reißt das die
  Zuweisung und damit den ganzen Lauf weg, **still und ohne Meldung**: Der
  Selbsttest endete nach sechs Stunden mit Exit 1 und ohne ein Wort darüber,
  was er gefunden hatte.

  Auf Linux ist es nie aufgefallen, weil die Bäume dort immer gleich waren und
  `diff` 0 lieferte. **Ein Prüfer, der nur überlebt, solange er nichts findet,
  ist keiner** — dieselbe Gattung wie `BL-111`, eine Ebene höher: dort starb
  eine Ableitung an ihrem leeren Normalfall, hier ein Test an seinem Fund.

  Der Wächter dazu prüft die **Bauart**, nicht die zwei bekannten Stellen: jede
  Zuweisung `VAR="$( … )"`, deren Befehl seinen Exit-Code als *Aussage* führt
  (`diff`, `cmp` — „gefunden" ist dort 1, nicht 0), muss ihn abfangen. Mit
  Gegenprobe an der wörtlichen Fassung von vorher.

- ⚠️ **Ein MSYS-Pfad wanderte roh in ein `pwsh -Command`** (`BL-161`). Dieselbe
  Stufe reicht `$KIT` in einen PowerShell-Aufruf hinein. Als **Argument**
  wandelt die MSYS-Schicht von Git-Bash einen Pfad selbst um — deshalb laufen
  die `-File`-Aufrufe unverändert. **Innerhalb** eines `-Command`-Strings ist er
  bloßer Text: PowerShell las den POSIX-Pfad `/c/Users/…` als einen relativen
  Windows-Pfad unterhalb von `C:` und meldete „Cannot find path".

  **Die Folge war nicht nur eine rote Zeile.** Die Syntaxprüfung sah damit
  **null** PowerShell-Dateien statt achtzehn — sie war auf dieser Bahn
  wirkungslos, und an der Stelle, an der sonst die Liste der kaputten Dateien
  steht, stand der Fehlertext. Nach dem Fix werden die 18 Dateien wirklich
  geparst. `pwsh_pfad` schaltet über `cygpath -w`, wo es das gibt, und reicht
  den Pfad sonst unverändert durch — auf POSIX ist er bereits richtig.

  Beide Funde stammen aus dem **dritten** `kit-test.sh`-Lauf auf der
  Windows-Maschine — dem ersten, der Stufe 11 überhaupt erreicht hat. Sie ist
  die Stufe, auf der laut ihrem eigenen Kommentar „die ganze pwsh-Bahn ruht",
  und sie war dort nie gefahren worden.

- ⚠️ **`kit-einrichten.sh` fällte ein POSIX-Urteil über einen Windows-Wirt —
  und schickte den Anwender an ein Paket, das es dort nicht gibt** (`BL-159`).
  Auf einer nativen Windows-Maschine unter Git for Windows meldete die
  Vorflug-Prüfung **drei Fehler** und „die Maschine ist noch nicht bereit":
  `flock` fehlt, `chmod +x` wirkt nicht, `flock` greift nicht.

  **Alle drei Befunde sind wahr** — Git for Windows liefert kein `flock`, und
  NTFS trägt unter Git-Bash kein Exec-Bit. Falsch war der **Schweregrad**. Die
  Zwei-Bahnen-Tabelle im README sagt „Bash-Bahn (Linux · WSL)" gegen
  „pwsh-Bahn (Windows ohne WSL)": Nativ unter Windows ist die bash-Bahn die
  zweite Wahl. Das Kit erklärte damit eine Maschine für unbereit, auf der
  seine **native** Bahn tadellos läuft — und empfahl `sudo apt install
  util-linux`. Eine Abhilfe, die auf dieser Maschine nicht ausführbar ist, ist
  keine; dieselbe Erwägung wie bei `BL-189`.

  **Die Befunde verschwinden nicht, sie werden Warnungen** — und sie erklären
  jetzt mehr als vorher, nicht weniger: Jede nennt ihre Folge und die Bahn, auf
  der es die Folge nicht gibt (die `.cmd`-Einstiege der pwsh-Bahn statt
  `./ralph.sh`; dieselbe Bahn sperrt über Betriebssystem-Dateisperren statt
  über `flock`). Und die
  Umgebungszeile sagt nicht mehr „Unbekanntes System" zu Git for Windows — das
  war es nie: Das Kit fährt mit genau dieser bash seinen eigenen Selbsttest.

  **Ein zweiter, kleinerer Fund derselben Sorte im selben Zug:** Fehlte `flock`
  als Werkzeug, meldete das Skript den Befund **zweimal** — in 2/5 („Werkzeug
  fehlt") und in 3/5 („Sperre greift nicht"). Zwei Meldungen für *eine* Ursache
  lesen sich wie zwei Probleme. Die Sperrprobe schweigt jetzt, wenn es nichts
  zu proben gibt; `kit-test.sh` prüft dafür die **Gattung** („probiert *oder*
  Fehlen benannt") statt einer festen Zeile — Schweigen geht weiterhin nicht
  durch.

- ⚠️ **`--verknuepfen` meldete „✓ Verknüpft" und legte eine Kopie an**
  (`BL-160`). Unter MSYS/Git-Bash erzeugt `ln -s` ohne Symlink-Recht keine
  Verknüpfung, sondern kopiert — und meldet Erfolg. `kit-einrichten.sh` gab das
  ungeprüft weiter, **mit Pfeil**: `✓ Verknüpft: …/team-init.sh → …`.

  **Das wiegt schwerer, als es klingt.** `~/.claude/scripts/team-init.sh` ist
  laut `kit-test.sh` „das einzige Stück des Kits, von dem eine Kopie außerhalb
  des Repos liegen kann"; das Kit hat eine eigene Erkennung dafür gebaut, weil
  so eine Kopie veraltet und dann stillsteht. Ausgerechnet die **Reparatur**
  erzeugte sie — und der Satz daneben, „Eine Verknüpfung kann nicht veralten —
  die Kopie konnte es", war damit eine Falschaussage.

  Beide Verknüpfungs-Pfade gehen jetzt durch `verknuepfung_bestaetigen`: erst
  `[ -L … ]`, dann die Meldung. Schlägt es fehl, nennt die Warnung die Folge und
  **drei** Abhilfen — Entwicklermodus plus `MSYS=winsymlinks:nativestrict`, der
  Aufruf über den vollen Pfad, oder die pwsh-Bahn. Die mittlere ist die, die
  auf einer verwalteten Maschine als einzige bleibt. Dieselbe Erwägung wie
  `BL-189`, und dieselbe wie ein Abschnitt weiter oben. Der Erklärblock steht
  **einmal**, nicht zweimal hintereinander (`BL-14`).

  **Gemessen, nicht vermutet:** Auf der Fundmaschine legt `ln -s` eine reguläre
  Datei an; `MSYS=winsymlinks:nativestrict ln -s` und `cmd /c mklink` scheitern
  beide mit „Operation not permitted" (kein Entwicklermodus, keine
  Administratorrechte). Der Symlink-Fall des Launchers in `kit-test.sh` Stufe 10
  prüfte dort deshalb gar keinen Symlink — und war trotzdem **grün**, weil die
  Kopie am fremden Ort ebenfalls mit 2 endet. Ein grüner Haken aus dem falschen
  Grund; aufgedeckt erst durch die Folgezusicherung „und es ist der Installer,
  der sich meldet". Stufe 10 probiert die Symlink-Fähigkeit jetzt, überspringt
  den Fall **sichtbar**, wenn sie fehlt, und prüft an seiner Stelle die
  wichtigere Zusicherung: dass `--verknuepfen` keine Verknüpfung *behauptet*.

- ⚠️ **Die beiden Kit-eigenen Prüfer starben unter Windows auf ihrer
  *Erfolgs*-Spur — mit einer Meldung, die etwas völlig anderes behauptet**
  (`BL-158`). `geteilt/kit-readme-pruefen.py` und `geteilt/kit-regelinventar.py`
  geben ihr Ergebnis mit einem Häkchen aus. Für `stdout`/`stderr` gilt Pythons
  Default, und der ist unter Windows die ANSI-Codepage der Maschine, sobald die
  Ausgabe in eine Pipe geht statt in eine Konsole — auf einem deutschen System
  cp1252. Beide sterben dort mit `UnicodeEncodeError` und Exit 1, **und zwar
  genau dann, wenn alles in Ordnung ist**.

  `kit-test.sh` fährt sie in Schritt 3 und Schritt 9 unter `if ! …` und meldet
  daraufhin „Das README steht gegen die frische Installation" bzw. ein rotes
  Regel-Inventar. Das ist der teuerste Fehlermodus, den dieses Repo kennt: Er
  **sieht aus wie ein inhaltlicher Befund, ist keiner**, und er schickt den
  Leser an eine Stelle, an der nichts kaputt ist.

  **Der Fix ist eine Zeile, die es im Kit längst gibt.** `team/tools/*.py`
  tragen die UTF-8-Umstellung seit `BL-133`. Dessen Wächter prüft ausdrücklich
  die **Gattung** statt einer Namensliste — nur eben die Gattung
  `team/tools/*.py`. Die zweite Gattung `geteilt/kit-*.py` (die Prüfer, die der
  Installer bewusst *nicht* mitkopiert) lag daneben und war von nichts gedeckt.
  Zwei Gattungen, ein Fehler, ein Wächter, der nur eine kannte. Er deckt jetzt
  beide — wieder als Gattung: Jedes `geteilt/kit-*.py` wird unter gestelltem
  `PYTHONIOENCODING=cp1252` als **Prozess** gestartet, erwartet werden Exit 0
  *und* ein UTF-8-Häkchen in den Rohbytes. Ein Programm, das seine
  Erfolgsmeldung nicht loswird, ist nicht erfolgreich.

  **Gegenprobe, die den Fix erst gültig macht:** die Umstellung in
  `kit-readme-pruefen.py` zurückgedreht → der Fall fällt, mit genau dem
  `UnicodeEncodeError` im Fehlertext; wieder eingesetzt → grün.

  Nicht über `PYTHONIOENCODING` beim Aufrufer gelöst: Das müssten
  `kit-test.sh`, `kit-test.ps1` und der Mensch auf der Kommandozeile jeder für
  sich setzen — dieselbe Erwägung wie im Kopf von `beutebuch.py`. *Eine
  Zusicherung, die an fünf Stellen wiederholt werden muss, ist eine, die eine
  Stelle vergisst.*

- **`kit-test.sh` starb auf einer Maschine ohne globale Git-Identität mit
  Exit 128 — vor der ersten Prüfung** (`BL-157`). Der Selbsttest legt sechs
  Wegwerf-Repos an; drei gaben ihnen eine lokale Identität, drei nicht
  (`A_REPO`/`B_REPO` in Schritt 8, `E_ZIEL` in Schritt 10). Alle drei
  committen, und ohne Identität bricht git dort ab.

  **Die Absicht stand ausdrücklich da** — „Lokale Identität, damit der Lauf
  auch ohne globale Git-Config committen kann", als Kommentar in Schritt 1 —,
  nur hat sie niemand durchgesetzt. Deshalb ist der Fix nicht das Nachtragen
  der drei Zeilenpaare, sondern `wegwerf_repo <pfad>`: anlegen und Identität
  setzen in einem Zug, alle sechs Stellen gehen hindurch. Dazu ein Wächter,
  der die **Gattung** prüft — jede Zeile, die ein Repo anlegt — statt einer
  Liste der bekannten Stellen. Seine erste Fassung hatte selbst einen
  Fehlalarm (`-m init`, also eine Commit-**Nachricht**); `BL-143` in klein, im
  selben Zug behoben.

  **Warum es so lange grün blieb:** Frühere Läufe fanden auf Maschinen **mit**
  globaler Identität statt. Die Zusicherung hing damit an einer Einstellung
  außerhalb des Repos — von der vier der sechs Repos ausdrücklich unabhängig
  waren. Der Fehlermodus ist der teuerste, den dieses Kit kennt: Er sieht aus
  wie ein kaputtes Kit, ist keines, und trifft bevorzugt den Erstlauf auf
  einer frisch aufgesetzten Maschine.


- ⚠️ **Die Ausnahmeliste des `BL-52`-Hinweises war eine Abschrift der
  Entrypoints** (`BL-154`). `install.sh` meldet beim Update ungeprüften Code in
  der Projektwurzel und nahm die eigenen Entrypoints per handgepflegter
  `case`-Liste davon aus — 24 Namen. Ab dem nächsten neuen Entrypoint ist so
  eine Liste falsch, und zwar auf die unangenehme Art: **Das Kit meldet dann
  seine eigene Datei als „ungeprüften Projektcode".** Eine Warnung, die in jedem
  grünen Projekt erscheint, erzieht zum Wegsehen (`BL-14`) — und daneben steht
  der Hinweis auf *echten* Wurzel-Code, den man dann mit übersieht.

  Nicht theoretisch: Beim Einbau von `BL-153` wurde der Selbsttest an zwei
  Stellen rot, und die zweite war irreführend. Im Bestandsprojekt meldete
  Schritt 7 `main.py` **nicht mehr** — die drei neuen `kit-melden`-Dateien
  standen alphabetisch davor, und die Prüfung sah auf den exakten Zeilenanfang.
  Ein neuer Entrypoint hat also einen **bestehenden** Fund unsichtbar gemacht.

  Beide Abschriften sind durch eine **Messung an der Quelle** ersetzt: Eine
  Datei in der Projektwurzel ist ein Entrypoint des Kits, wenn es sie in
  `bash/entry/` oder `pwsh/entry/` gibt — und `kit-test.sh` zählt „die Bash-Bahn
  ist vollständig" gegen `ls "$KIT"/bash/entry/*.sh` statt gegen die
  abgeschriebene `10`. Dieselbe Lehre wie im Kopf von
  `geteilt/kit-readme-pruefen.py`: *Ein Wächter, der eine Abschrift prüft,
  veraltet mit ihr.*

  Im selben Zug liest `test_bl133_interpreter_und_ausgabe.py` seine
  Werkzeugliste jetzt aus dem Ordner statt aus drei fest genannten Namen —
  sonst wäre die UTF-8-Zusicherung stillschweigend an `kit_meldung.py`
  vorbeigelaufen, ausgerechnet am ersten Werkzeug, das Prosa mit Umlauten
  ausgibt.

  **Damals offen und bewusst nicht mitgenommen:** Die pwsh-Bahn hatte den
  `BL-52`-Hinweis gar nicht — `install.ps1` kannte keine Wurzel-Code-Prüfung.
  Das war keine ungeprüfte Hälfte, sondern eine **fehlende**. Ausgewiesen als
  `BL-155`, nachgezogen am 2026-08-24 auf der Windows-Maschine; siehe den
  nächsten Eintrag.

- ⚠️ **`install.ps1` kannte die Wurzel-Code-Prüfung aus `BL-52` gar nicht**
  (`BL-155`). Ein einbahnig-pwsh installiertes Bestandsprojekt — also genau
  die Lage, für die die pwsh-Bahn gebaut ist — erfuhr beim Update nie, dass
  sein Einstiegspunkt in der Wurzel außerhalb des Prüfumfangs liegt. Der
  Hinweis steht jetzt an derselben Stelle wie drüben: direkt hinter dem
  `BL-51`-Block im Update-Pfad, mit demselben Wortlaut, damit ein Befund nicht
  zwei Fehlermeldungen hat.

  **Die Entrypoints werden gemessen, nicht abgeschrieben** — dieselbe Regel wie
  in `BL-154`, nicht eine zweite Liste. Eine eigene Aufzählung hier wäre die
  Abschrift gewesen, nur umgezogen.

  **Eine Stelle ist besser als das Vorbild.** Die bash-Fassung nennt in der
  Abhilfe fest `team.config.sh`. In einer einbahnig-pwsh installierten Ablage
  gibt es diese Datei nicht — die Abhilfe verwiese dort auf etwas, das der
  Leser nicht findet. Die pwsh-Fassung nennt die Quelle, aus der sie die Werte
  wirklich gelesen hat, und zeigt die Schreibweise, die dort gilt.

  **Beim Bau ist ein Unterschied zwischen den Bahnen aufgefallen, den die
  Portierung sonst geerbt hätte:** In `install.sh` fallen `.ralph-state`,
  `.budget-ledger`, `.gitignore` und `.gitattributes` durch das Glob —
  `"$ZIEL"/*` fasst keine Punktdatei an. Unter Windows trägt eine Punktdatei
  **kein** Hidden-Attribut, `Get-ChildItem` liefert sie also ganz normal mit.
  Ohne ausdrücklichen Ausschluss hätte das Update den eigenen Zustand des
  Teams als „ungeprüften Projektcode" gemeldet — die Warnung in jedem grünen
  Projekt, also genau der Fehlermodus, den `BL-154` gerade abgeschafft hatte.
  Der Ausschluss steht deshalb **mit Begründung** im Code und nicht als
  stiller Einzeiler.

  **Nachgewiesen wird auf zwei Ebenen.** Am Quelltext für beide Bahnen
  ([`test_bl155_wurzel_code_auf_beiden_bahnen.py`](geteilt/tests/test_bl155_wurzel_code_auf_beiden_bahnen.py),
  7 Fälle, laufen auch ohne PowerShell) — darunter die Gegenprobe, dass in
  `install.ps1` **keine** Entrypoint-Aufzählung danebenstehen geblieben ist.
  Und am Lauf in `kit-test.sh` Stufe 7, wo das Bestandsprojekt mit `main.py`
  in der Wurzel bereits steht: Dort fährt jetzt auch `install.ps1 -Update` und
  muss denselben Befund melden — ohne einen Entrypoint des Kits und ohne eine
  Punktdatei zu nennen. Fehlt `pwsh`, wird das ausdrücklich als **ungeprüft**
  ausgegeben statt still übersprungen.

- ⚠️ **Der `BL-140`-Lint verbot in einem Feldprojekt genau die Schreibweise,
  die seine eigene Regel als richtig erklärt** (`BL-148`). Die Regel kennt
  **drei** Sorten — blank = mein Backlog, `Kit-BL-<N>` = der des Kits, ein
  drittes Projekt wird **benannt**. Durchgesetzt wurde davon nur eine: Der
  Test verbot **jede** blanke Nummer, mit einer im Testkörper hartkodierten
  Ausnahmeliste. Im Kit-Repo ist das richtig. In einer **Installation** liest
  derselbe Test die projekteigene `CLAUDE.md`, und dort sind blanke Nummern
  der Normalfall — und die Ausnahmeliste lässt sich nicht aufrüsten, weil
  `--update` `team/tests/` überschreibt.

  **Die dritte Sorte ist jetzt maschinell lesbar**, statt durch eine Liste
  angenähert zu werden:

  - **(b)** Die Zeile **nennt ein Projekt** in Backticks (`` `Feld A` ``,
    `` `website-maxron-de` ``) → kein Fund. Gilt **überall**, auch in
    Vorlagen: Ein benanntes drittes Projekt ist für jeden Leser eindeutig,
    egal wo der Text landet.
  - **(a)** Die Nummer steht im **eigenen Backlog oder Beutebuch** des
    Projekts → kein Fund. Gilt **nur in Projekttexten**, nie in Vorlagen.
  - **(c)** Alles andere bleibt ein Fund.

  **Der entscheidende Schnitt ist nicht „Kit gegen Installation", sondern
  Vorlage gegen Projekttext.** Eine Vorlage (`bootstrap/*`,
  `*/prompts/rolle-*.md`) wird in ein fremdes Projekt geliefert; dort heißt
  blank „der Backlog *dieses* Projekts", und der existiert zur Lintzeit nicht.
  Würde (a) dort greifen, löste der Lint die Nummer gegen den Backlog des
  **Kits** auf und erlaubte genau den Verweis, den `BL-140` verboten hat. Ein
  eigener Fall hält das fest.

  **Der Beleg, dass die Regel trägt:** Die hartkodierte Ausnahme für
  `rolle-architekt.md`/`BL-120` ist **ersatzlos entfallen** — Sorte (b)
  erkennt sie jetzt selbst, weil die Zeile `` `Feld A` `` nennt. Übrig bleiben
  zwei Ausnahmen, und die tragen eine **vierte** Sorte, die keine Regel
  erkennen kann: das Formatbeispiel im Glossar („Trägt eine Nummer
  (`HM-7`)").

  **Am echten Feldprojekt nachgemessen** (`Feld A`, 25 blanke Verweise in
  seiner `CLAUDE.md`): Die neue Regel räumt **14 davon ohne jede Änderung**
  ab. Von den verbleibenden elf brauchen **zwei** nur Backticks um einen
  Projektnamen, der schon dasteht; die anderen neun sind echte Funde — acht
  meinen den Kit-Backlog, einer zeigt ins Leere.

  **Die Backtick-Pflicht ist eine Entscheidung, kein Versehen**, und sie steht
  als eigener Fall im Test: `website-maxron-de` und `rollen-agnostisch` haben
  dieselbe Gestalt. Eine Regel, die beide nimmt, wäre eine Freikarte für jede
  zweite Zeile; eine, die beide ablehnt, verlöre die dritte Sorte ganz.
  Backticks sind im Kit ohnehin Hausstil, der Fix kostet eine Sekunde, und ein
  Projektname in Backticks ist greppbar.

  **Im Kit-Repo ändert sich nichts** — dort gibt es keine Projekttexte, also
  greift (a) nie. Die Gegenproben laufen deshalb gegen **gebaute** Ablagen:
  Ein Test, der nur die eigene Ablage kennt, hätte `BL-148` nicht gefunden und
  würde ihn auch nicht fangen.

- ⚠️ **Die Eichprüfung der Preistabelle konnte nie bestehen — sie las
  `modelUsage` mit den Schlüsseln des Transkripts** (`BL-152`).
  `preise_nachrechnen()` reichte einen `modelUsage`-Eintrag an
  `_usage_addieren()` weiter. Die beiden Strukturen sehen sich ähnlich und
  kommen aus verschiedenen Quellen: Das Transkript trägt **snake_case**
  (`input_tokens`), das headless-Log **camelCase** (`inputTokens`). Jeder
  Kübel blieb auf 0, `gerechnet` wurde `0.0000`, und die Abweichung war
  **immer exakt 100 %** — unabhängig davon, ob die Tabelle stimmte.
  `sitzung-messen` meldete daraufhin „Preistabelle stimmt nicht mehr" und
  erklärte die eigene, korrekt gemessene Zahl für `UNGEEICHT`. **Die Warnung
  zeigte genau dorthin, wo der Fehler nicht war**, und riet von einer Buchung
  ab, die in Ordnung gewesen wäre.

  **Nachgemessen an 920 abgerechneten Läufen aus vier Feldprojekten** — statt
  an den elf, die der Backlog-Eintrag hatte: Mit den richtigen Schlüsseln
  reproduzieren **alle 920** den abgerechneten Betrag exakt. Die Preistabelle
  war die ganze Zeit korrekt.

  **Die 5m/1h-Frage ist damit auch beantwortet, und anders als vermutet.**
  `modelUsage` trägt die Cache-Erstellung als eine Summe ohne Aufteilung nach
  Laufzeit; die Sätze unterscheiden sich (2,00 gegen 1,25). Dieselben 920
  Läufe zerfallen sauber in zwei Gruppen: **808 Abo-Läufe rechnen 1h ab, 112
  API-Fallback-Läufe überwiegend 5m** (110 von 112). Eine **feste** Annahme
  ist damit für eine der beiden Gruppen immer falsch — „immer 1h", der
  ursprüngliche Vorschlag, hätte 110 von 920 Läufen als „Preistabelle
  veraltet" gemeldet. Ein leiserer Fehlalarm, aber derselbe Fehler, und ein
  Wächter mit Fehlalarmen wird abgeschaltet (`BL-14`). Gezählt wird deshalb
  die **kleinere** der beiden Abweichungen. Die Laufart am Dateinamen
  festzumachen wäre die naheliegende Alternative und ist nachweislich
  schlechter: 2 der 112 Fallback-Läufe rechnen mit 1h ab.

  **Der Wächter bleibt scharf, ebenfalls gemessen:** Eine um 5 % verstellte
  Preistabelle wird bei 920 von 920 Läufen erkannt, eine um 20 % verstellte
  bei 907. Die Annahme betrifft nur **einen** Kübel; der Basispreis, um den es
  bei einer Preisänderung geht, steckt in allen.

  **Warum es niemandem auffiel — und das ist der eigentliche Fund:** Es *gab*
  einen Test. `test_bl141_sitzung_messen.py` prüfte die Eichung in vier
  Fällen, alle vier grün. Sie bauten ihre `modelUsage`-Fixture aber in der
  Sprache des **Lesers** (`input_tokens`) statt in der des **echten Logs**.
  Ein Test, der sein Testmaterial im Dialekt des Codes schreibt, prüft den
  Code gegen sich selbst — er hat die Fehlbuchung **festgeschrieben**, statt
  sie zu fangen. Dieselbe Bauart wie in `BL-143`. Die vier Fixtures sind
  nachgezogen, mit der Lehre an der Zeile, an der sie hängt.

  **Unter Test:** `test_bl152_eichung_liest_das_log_format.py`, neun Fälle mit
  einem Fixture aus **echten abgerechneten Läufen** — nur die Zahlenfelder,
  kein Text, keine Pfade; beide Lauf-Arten, drei Basispreise, ein Lauf unter
  einem Zehntelcent. Genau darin liegt ihr Wert: Ein Fixture, das aus der
  Preistabelle abgeleitet wäre, könnte die Tabelle nicht prüfen. Dazu die
  Gegenprobe über fünf verstellte Preistabellen und ein Fall, der festhält,
  dass `_usage_addieren` das Log-Format **nicht** lesen darf — zwei Leser für
  zwei Formate war der Punkt.

- ⚠️ **Der Platzhalter war nicht leer — und alle Weichen prüfen nur auf leer.
  Damit startete die allererste Kaskade JEDES Projekts mit einem kaputten
  Prompt** (`BL-149`). `team.config.*` kam mit der Vorbelegung
  `TEAM_SMOKE_TEST="TODO: noch keiner — Stufe 1 der ersten Kaskade"` aus dem
  Installer. Die Bibliothek unterscheidet „konfiguriert" von „nicht
  konfiguriert" aber allein über leer/nicht-leer — für sie war der Satz ein
  **konfigurierter Befehl**. Drei Folgen, alle in Kaskade 1:

  1. `SMOKE_ZEILE` schrieb jeder bauenden Rolle in den Prompt: „Smoke-Test
     ausführen: `TODO: noch keiner — Stufe 1 der ersten Kaskade` — muss grün
     sein", samt dem Nachsatz, ihn ja im Vordergrund auszuführen.
  2. `team_allowed_tools` hängte `Bash(TODO: noch keiner — …)` in die
     Werkzeug-Allowlist des Red Teams.
  3. `team_quittung_selbstpruefung` führte den Wert **wörtlich** aus — Exit
     127 — und meldete „✗ … ist ROT". Der vierte Ausgang (`BL-41`) konnte in
     Stufe 1 damit **nie** automatisch quittieren, obwohl genau diese Stufe
     die Aufgabe hat, den Smoke-Test überhaupt erst zu bauen.

  Der Kommentar unmittelbar über der Zeile sagte selbst: „Ist er **leer**,
  lassen die Rollen den Smoke-Test-Schritt aus" — die Vorbelegung widersprach
  ihrer eigenen Dokumentation.

  **Zwei Hälften gebaut.** Der **Fall**: `{{SMOKE_TEST}}` bleibt der
  Prosa-Platzhalter und trägt den TODO-Satz weiter in `CLAUDE.md`, `TEAM.md`
  und die Skizzen-Vorlage — dort ist er richtig, er sagt einem Menschen, was
  fehlt. Neu daneben steht `{{SMOKE_TEST_KONFIG}}`, der **nur** in
  `team.config.*` vorkommt und leer bleibt, wenn nichts konfiguriert ist
  (dieselbe Bauart wie `{{WEITERER_CODE}}`). Die **Klasse**: Die Bibliothek
  behandelt einen mit `TODO` beginnenden Wert wie leer — ein Mensch trägt in
  eine leere Zeile gern selbst ein „TODO" ein, und Platzhalter dieser Sorte
  werden erfahrungsgemäß an anderer Stelle wieder eingeführt. Normalisiert
  wird **einmal**, beim Laden, statt an drei Verbrauchsstellen einzeln.

  **Warum das so lange unsichtbar war** — und das ist der eigentliche Fund:
  Der Fehler hat ein Zeitfenster von genau einer Kaskade pro Projekt. Dazu
  kam eine zweite Blindstelle, schwarz auf weiß in
  `test_bl41_smoke_zeile_vordergrund.py`: Dessen Schlusskommentar erklärte den
  else-Zweig („Kein Smoke-Test konfiguriert") für **nicht prüfbar**, weil eine
  Installation `TEAM_SMOKE_TEST` immer selbst setze. Das stimmte — **weil**
  der Installer die nicht-leere Vorbelegung schrieb. Der Zweig, in dem der
  Fund saß, war der einzige, den niemand fuhr; der Kommentar hat ihn
  beschrieben, ohne ihn zu erkennen, und als Testlücke abgehakt. Er ist jetzt
  berichtigt und verweist auf den Test, der den Zweig fährt.

  **Unter Test:** `test_bl149_platzhalter_ist_kein_befehl.py` fährt beide
  Verbrauchsstellen auf **beiden Bahnen** in einer Ablage **ohne**
  `team.config` — dann entscheidet allein die Umgebung, und der Test gilt in
  beiden Ablagen gleich. Dazu drei Gegenproben (ein echter Befehl kommt
  weiterhin im Prompt und in der Allowlist an; `./todo.sh` wird **nicht**
  geschluckt, weil die Weiche am Präfix und großgeschrieben greift) und vier
  statische Prüfungen über die Vorbelegung selbst — inklusive der, dass
  **beide** Füll-Routinen von `install.sh` den neuen Platzhalter kennen
  (`BL-119` hat gezeigt, was eine halb fertige Konfiguration kostet).
  Gegenprobe gefahren: Jede Hälfte des Fixes einzeln zurückgedreht macht
  eigene Fälle rot.

  ⚠️ **Die pwsh-Hälfte ist geschrieben, aber nicht gefahren** — kein
  PowerShell 7 auf der Entwicklungsmaschine. Siehe `BL-146`.

- ⚠️ **Der Plankopf ist Markdown — die Leser lasen ihn wie Konfiguration**
  (`BL-150`). Beide Bahnen ankerten auf `^\s*RALPH_CAP=` und nahmen den Rest
  der Zeile. Der Architekt legte den Plankopf aber fett an
  (`**RALPH_CAP=5**`): Die führenden Sterne verhinderten den Treffer, und
  selbst bei Treffer wäre der Wert `5**` gewesen. **Ralph stieg mit Exit 1
  aus, `team-status` zeigte `Cap ?`, und `BUDGET_EMPFEHLUNG_USD` ging nie in
  die Deckel-Anhebung der Vollautomatik ein** — ein fehlender Wert, den
  niemand vermisst, weil sein Fehlen wie ein bewusst niedriger Deckel
  aussieht.

  **Der Fehler war eingebaut, nicht zufällig.** Das Architekten-Briefing
  verlangte „die Zeilen `RALPH_CAP=…` und `BUDGET_EMPFEHLUNG_USD=…` im
  Plankopf" — ohne ein Wort über Blank-Pflicht, während der übrige Plankopf
  (`**Plan:**`, `**Stufen:**`, `**Typ:**`) durchgehend fett ist. Wer sich exakt
  ans Briefing hielt und dem Stil des eigenen Dokuments folgte, blockierte den
  Bau.

  **Beide Hälften gebaut, weil keine für sich trägt:** Die Leser dulden jetzt
  Auszeichnung (führende `**`/`` ` ``/`_`/Aufzählungs- und Zitatzeichen,
  nachlaufende ebenso) — und das Briefing spricht die Blank-Pflicht aus und
  zeigt den Plankopf als Block. Eine geduldete Auszeichnung ohne Briefing-Satz
  lädt zum Weiterschreiben ein; ein Briefing-Satz ohne duldenden Leser trifft
  den nächsten Architekten, der ihn überliest.

  Nebenbei ist die zweite Kopie derselben Ableitung verschwunden:
  `team_ralph_cap` und `team_budget_empfehlung` teilen sich auf beiden Bahnen
  jetzt ein `team_plankopf_wert`. Zwei Kopien einer Pipeline waren einen
  Eintrag zuvor schon der eigentliche Befund (`BL-151`).

  **Unter Test:** `test_bl150_plankopf_auszeichnung.py` fährt **fünf
  Notationen** × zwei Funktionen auf **beiden Bahnen** unter voller Strenge,
  dazu zwei Gegenproben gegen eine zu weiche Duldung (ein Plan ohne die Zeile
  bleibt leer und still; ein Prosa-Verweis wird **nicht** gelesen), einen
  End-zu-End-Lauf durch `ralph.sh` gegen einen fett gesetzten Plankopf und
  eine Prüfung, dass das Briefing die Regel wirklich trägt. `kit-test.ps1`
  baut seinen Trockenlauf-Plankopf jetzt **fett** statt blank — er prüfte
  bisher genau den Fall nie, der im Feld eintrat. Gegenprobe gefahren: am
  zurückgedrehten Leser werden neun Fälle rot, die blanke Notation bleibt
  grün.

  ⚠️ **Die pwsh-Hälfte ist geschrieben, aber nicht gefahren** — auf der
  Entwicklungsmaschine ist kein PowerShell 7. Sie gehört damit auf den Stapel
  aus `BL-146` und ist eine Behauptung mit Testkörper, keine Zusicherung.

- ⚠️ **`ralph.sh` starb still, bevor die eigene Fehlermeldung lief** (`BL-151`).
  Unter `set -euo pipefail` reißt eine Kommandosubstitution mit leerem `grep`
  oder fehlgeschlagenem `head` den Aufrufer sofort weg — das `if [ -z … ]`
  darunter wurde **nie erreicht**. Betroffen waren die `RALPH_CAP`-Zeile und
  die Stufennummer aus `.ralph-state`; beide Klartextmeldungen waren toter
  Text.

  Im Feld (`Feld D`, 2026-08-23, allererster Vollautomatik-Start) sah der
  Mensch genau einen Satz: `Ralph endete mit Fehler (1) — Vollautomatik
  stoppt`. Das Lauf-Log trug denselben einen Satz, obwohl `vollautomatik.sh`
  stderr korrekt mitschreibt. **Die Fehlerlage war in 30 Sekunden behoben —
  sie zu finden kostete Log, Skriptlektüre und eine eigene Messung.**

  **Der Befund ist nicht das fehlende `|| true`, sondern die Doppelpflege.**
  Neun Zeilen über der kaputten Stelle stand die Schutzform bereits, samt
  Kommentar; `team_ralph_cap` in `lib.sh` liest denselben Wert und hatte die
  Härtung mit `BL-111` ausdrücklich bekommen. `ralph.sh` hatte die Funktion
  nur nicht aufgerufen, sondern die `grep`-Kette danebengestellt — und die
  Kopie bekam die Härtung nicht mit. Die pwsh-Bahn hatte den Fehler **nie**:
  `ralph.ps1` ruft `team_ralph_cap` auf und erreicht seine Meldung. Ab jetzt
  beide.

  **Unter Test:** `test_bl151_ralph_diagnose.py` fährt beide Fehlerlagen als
  echten Prozess (kein CLI-Stub nötig — sie schlagen zu, *bevor* der erste
  Agentenaufruf fällig wäre) und hält zusätzlich die **Klasse** fest: In
  `ralph.sh` darf keine zweite Ableitung von `RALPH_CAP` stehen. Ohne diese
  dritte Prüfung käme die nächste Kopie ungehärtet zurück und die beiden
  anderen blieben grün. Gegenprobe gefahren: am zurückgedrehten Code werden
  alle drei rot.

- ⚠️ **Ein `--update` legte die zweite Bahn dazu — auch in ein Projekt, das nie
  eine wollte** (`BL-147`). Gedacht war das als Rückweg aus einer Abwahl
  (`BL-119`: „ein Update macht das Projekt wieder vollständig"). Nur fährt
  niemand ein `--update`, um eine Bahn zurückzuholen — man fährt es, um eine
  neue Kit-Version zu bekommen. Der Ausnahmefall war die Vorbelegung.

  Im Feld (`Feld A`, 2026-08-22) legte ein Routine-Update **21 pwsh-Dateien**
  in ein reines Bash-Projekt: 19 Entrypoints, `team/lib.psm1`,
  `team/redteam.ps1`. Untracked, unbestellt — und weil sie im Baum lagen, fuhr
  die Testsuite ab da eine Bahn mit, die dort niemand fährt
  (`conftest.bahnen_in_der_ablage` entscheidet an der **Anwesenheit** der
  Dateien).

  **Jetzt sagt die Ablage, welche Bahn ein Projekt fährt.** Der Update-Pfad
  beider Installer erkennt eine einbahnige Ablage und hält sie einbahnig; er
  meldet es (`Einbahnige Ablage erkannt: nur die bash-Bahn`). Der Rückweg
  bleibt, er wird nur **ausdrücklich**: `--update --beide-bahnen`
  (`-BeideBahnen`). Damit kommt die Entscheidung in beide Richtungen vom
  Anwender, nie vom Installer — derselbe Schnitt wie bei der Abwahl selbst.

  **Erkannt wird an den Dateien, die das Kit ausliefert, nicht an Endungen.**
  Ein projekteigenes `deploy.ps1` ist keine pwsh-Bahn, ein `build.sh` macht aus
  einem Windows-Projekt kein zweibahniges; eine Endungs-Heuristik hätte im Feld
  an genau dieser Stelle vorbeigelesen. Aus derselben Liste ist jetzt auch die
  Reste-Meldung gebaut — die zählte vorher nach Endung und hätte irgendwann
  `git rm` auf die eigene Datei eines Anwenders vorgeschlagen (Lehre `BL-12`,
  nur andersherum).

  **Unter Test:** `kit-test.sh` Stufe 8 prüft in **beiden** Richtungen erst den
  Bestand (ein `--update` lässt die einbahnige Ablage einbahnig, in der Wurzel
  *und* in `team/`), dann den Rückweg über `--beide-bahnen` mit den bisherigen
  Zusicherungen (Konfiguration aus den **Projektwerten**, keine Platzhalter).
  Dazu fünf Fälle am Quelltext beider Installer
  (`test_bl147_update_erkennt_die_bahn.py`), weil die pwsh-Fassung auf einer
  Maschine ohne PowerShell nicht **gefahren** werden kann — genau die
  `BL-117`-Lage. ⚠️ **Die pwsh-Seite dieses Fixes ist damit geschrieben und
  nicht ausgeführt** (`BL-146`).

## [2.12.0] — 2026-08-22

**Die Windows-Runde.** Erste Kaskade eines Projekts auf der pwsh-Bahn, auf
einer echten Windows-Maschine, einbahnig installiert — und der erste
vollständige Kostenabschluss überhaupt. Beides zusammen hat `BL-120`…`BL-146`
erzeugt: die Kostenkette, die Zeilenenden, den Interpreternamen, die
Regeltexte einer einbahnigen Ablage. Feldbefunde sind mit ⚠️ markiert.

### Changed

- **Die Feldprojekte werden nicht mehr genannt — sie werden beschrieben.**
  Bis hierher standen in Doku, Backlog, CHANGELOG, Code-Kommentaren, Test-
  Docstrings und im **ausgelieferten** Architekten-Briefing die echten Namen
  von vier Projekten, dazu ein absoluter Pfad der Autorenmaschine und die
  Dateinamen aus einer fremden Codebasis. Für den Beleg trägt der Name nichts
  bei: Was zählt, ist die **Lage** — Plattform, Bahn, Greenfield oder Bestand,
  und was dort gelaufen ist.

  Sie heißen jetzt `Feld A`, `Feld B` und `Feld C`, das vierte ist „das
  Ursprungsprojekt". Die Zuordnung steht **einmal**, als Profiltabelle im
  README unter *Herkunft*; ein künftiges Projekt bekommt den nächsten
  Buchstaben. Das Kürzel trägt die Identität, die Tabelle die Beweiskraft —
  deshalb muss ein Kürzel nicht umbenannt werden, wenn ein Feld später mehr
  belegt als heute.

  **Nicht mechanisch war eine Stelle:** Die `BL-140`-Regel kennt als dritte
  Sorte „ein DRITTES Projekt wird **benannt**, nicht präfigiert", und ihr
  einziger konkreter Fall im Briefing nannte ein Feldprojekt beim Namen. Die
  Regel bleibt gültig — sie benennt jetzt das Kürzel. Die Ausnahmeliste des
  Lints trägt den Grund nach.

- **„Strippenzieher" heißt jetzt „Stakeholder".** Der Begriff stand an 85
  Stellen, darunter in `CLAUDE.md.vorlage` und `TEAM.md` — beides Texte, die
  in **jedes** Zielprojekt ausgeliefert werden. „Stakeholder" ist neutraler
  und trägt dieselbe Bedeutung: der eine Mensch, der Richtung, Prioritäten und
  Freigaben bestimmt.

  **Bewusst ohne Update-Funktion.** Bereits eingerichtete Projekte behalten
  ihren Wortlaut; `--update` fasst `CLAUDE.md` und `TEAM.md` grundsätzlich
  nicht an, und eine Sonderbehandlung dafür wäre ein Eingriff in Projektdaten
  wegen einer Wortwahl.

  **Zwei Stellen hat der Wechsel mitgenommen**, und beide hätte ein reines
  Such-und-Ersetze stehen lassen: „des **Strippenzieher**" war schon vorher
  ein falscher Genitiv (jetzt „des **Stakeholders**"), und „Der Strippenzieher
  zieht die Fäden" war ein Wortspiel auf den alten Begriff — ohne ihn bleibt
  eine schiefe Metapher stehen, die zudem genau den Beiklang trägt, der weg
  sollte. Dort steht jetzt „setzt den Rahmen". Das Regel-Inventar (Stufe 9)
  ist mitgezogen und grün.

### Added

- **Das README trägt seinen Belegstand jetzt im Kopf.** Über dem Banner steht
  eine Reihe Statusabzeichen, und ihr Farbcode ist nicht Marketing, sondern
  die Skala, die das Kit ohnehin führt: 🟢 im Feld belegt, 🟡 hergeleitet,
  🟠 gebaut oder gewollt aber nicht abgenommen, 🔴 nicht vorhanden, ⚪ nicht
  belegt. Damit steht die Aussage, für die man sonst bis *Grenzen* scrollen
  musste, in der ersten Bildschirmhöhe — inklusive der unbequemen: `Binary`
  ist rot, `Agenten-CLI` orange, `macOS` grau. Jedes Abzeichen verlinkt auf
  die Stelle, die es begründet.

- **`geteilt/kit-readme-pruefen.py` — die Zahlen und Pfade des README stehen
  unter Test.** Neu in `kit-test.sh`, Stufe 5, mit Gegenprobe in beide
  Richtungen (verfälschte Zahl und toter Pfad werden einzeln rot).

  **Der Anlass ist ein Rückfall.** Für die Testzahlen gab es bereits einen
  Wächter — er kannte **zwei feste Formulierungen**. Eine dritte Stelle in
  freier Prosa nannte weiterhin `369 Regressionstests`, während es 590 waren:
  ausgerechnet die Zahl, vor der der Kommentar über dem alten Wächter warnt.
  Für die Pfade galt dasselbe eine Etage tiefer: Der vorhandene Wächter verbot
  **namentlich** den alten Autorenmaschinen-Pfad und konnte deshalb nicht
  sehen, dass daneben ein neuer falscher stand.

  Geprüft wird jetzt die **Gattung** statt der Abschrift: jede Zahl, die eine
  Testzahl behauptet — auch die im Abzeichen —, und jeder Pfad, den das README
  nennt, positiv gegen das Dateisystem. Die Messwerte kommen weiterhin von
  außen, aus einer **frischen Installation**; eine im Repo nachgerechnete Zahl
  wäre wieder eine Abschrift. Die Ausnahmeliste der Pfadprüfung ist eng und
  begründet: Das README nennt zwei Ablagen nebeneinander — die des Kits und
  die eines Zielprojekts —, und ein Wächter, der die zweite anmahnt, wird
  abgeschaltet statt befolgt (Bauart `BL-14`).

### Fixed

- **`README` — das Flaggschiff stand sechs Tage und 69 Einträge hinter dem
  Repo.** Es nannte Version 2.10.0, einen „wieder leeren" Backlog, 63
  abgetragene Einträge und den Stand `BL-1`…`BL-61`; wirklich waren es drei
  offene Einträge, 93 abgetragene und `BL-1`…`BL-146`.

  **Der Teil, der weh tut, ist die Untertreibung.** Das zweite Feldprojekt kam
  im README **null mal** vor, obwohl es auf einer echten Windows-Maschine eine
  vollständige Kaskade gefahren hat. Zwei Kernaussagen waren dadurch zu
  pessimistisch: die pwsh-Bahn sei „gebaut, aber noch nicht auf Windows
  abgenommen", und das Kit sei „im Feld gelaufen, aber an einem Projekttyp".
  Beide sind auf den heutigen Beleg gehoben, samt der Lücke, die **wirklich**
  offen ist: `kit-test.ps1` fährt 6 von 11 Stufen und 15 von 127 Prüfungen
  (`BL-145`). Ein Kit, dessen Hausregel „was verifiziert ist, heißt
  verifiziert" lautet, verliert an so einer Stelle in beide Richtungen.

- **`doku/einrichtung.md` — der Belegstand endete mit „Der nächste
  Windows-Lauf ist der Beleg", und der Lauf war am selben Tag passiert.** Der
  vierte Kontakt fehlte: die erste vollständige Kaskade auf der pwsh-Bahn,
  einbahnig installiert, mit echten Ledgerzeilen. Er ist nachgetragen — mit
  der Trennung, die ihn erst brauchbar macht: was er belegt (die CLI läuft
  dort headless mit dem Abo, die Rollen quittieren, der Closeout schreibt) und
  was nicht (es war ein Greenfield, und der Selbsttest der Bahn deckt sie
  nicht).

- **`README` — `bash scripts/team-auth-setup.sh` zeigte ins Leere.** Das
  Skript liegt unter `bash/scripts/`; ein `scripts/` in der Wurzel gibt es
  nicht, was das README vier Absätze später selbst schreibt („In der Wurzel
  liegt kein einziges Skript"). Steht jetzt unter Test.

- **`kit-test.sh` Stufe 10 schrieb ein Urteil fest statt einer Zusicherung.**
  Die Prüfung verlangte wörtlich `Windows nativ (PowerShell): gebaut und
  gefahren` in `doku/einrichtung.md` — und wurde rot, als der Belegstand
  nachgezogen wurde, weil der Weg auf einer echten Windows-Maschine gelaufen
  ist. Ihr eigener Kommentar sagt etwas anderes: Der native Weg müsse **im
  Belegstand geführt** sein. Sie prüfte also eine Abschrift statt der
  Eigenschaft und hätte bei **jedem** Zugewinn an Beleg nachgezogen werden
  müssen. Ein Wächter, der ein Urteil einfriert, ist die stille Behauptung,
  das Urteil dürfe sich nicht ändern — zeichengleich mit dem Test, der
  `auth == "api"` festschrieb (`BL-143`). Geprüft wird jetzt, **dass** der
  Eintrag existiert, nicht **wie** er ausfällt.

  Gefunden beim ersten `kit-test.sh`-Lauf dieser Runde — nicht beim Lesen.

- **`README` — die Doku-Karte verschwieg die beiden größten Plandateien.**
  `plans/windows-nativ.md` (701 Zeilen, der Bauplan der zweiten Bahn) und
  `plans/roadmap-skizzen.md` fehlten in der Übersicht; die FAQ war mit „eine
  Frage" beschrieben, obwohl sie vier ausgebaute trägt.

- **`CHANGELOG` — 1950 Zeilen lagen unter `[Unreleased]`, und eine Version,
  auf die zwei Dokumente zeigten, gab es nicht.** `doku/anhang-a.md` schreibt
  „prüfte bis 2.11.0 niemand", der Launcher-Kommentar nennt den Umzug auf
  `bash/` — beides Verweise auf eine Fassung, die nie geschnitten wurde. Der
  Block ist an seiner natürlichen Naht getrennt: **2.11.0** (2026-08-20) ist
  die Bahn-Runde, die die Ablage auf `bash/`/`pwsh/`/`geteilt/` umgestellt
  hat, **2.12.0** die Windows-Runde.

- **`BL-120` — die FAQ trug eine Frage und war ein Versprechen.**

  Die Seite war als Gerüst gebaut und beantwortete genau eine Frage. Der Eintrag
  benannte drei Kandidaten — keine erfundenen, sondern genau die Stellen, an
  denen im Doku-Audit eine Symptomzeile auf eine Erklärung zeigte, die es so
  nicht gibt. Alle drei sind jetzt geschrieben.

  **`42` / `43` — was mache ich jetzt?** Beides sind eigene Ausgänge neben `0`
  und `1`, und die Antwort trennt sie scharf: `42` heißt **warten** (der Zustand
  steht, es gibt nichts zu reparieren; drei Env-Stellschrauben, falls es zu früh
  kommt), `43` heißt **nachsehen**. Die vier Entscheidungszeilen sind wörtlich
  die Prüfungen, die `ralph.sh` beim Aussteigen ausgibt — inklusive der dritten,
  die im Feld übersehen wurde: „Baum rot" heißt nicht „Stufe kaputt", es kommt
  darauf an, **wo** er rot ist. Der Feldbetrag steht daneben: 19,47 USD in vier
  Neubauten bereits bezahlter Arbeit.

  **Wie hole ich eine abgewählte Bahn zurück?** Ein `--update` **ohne**
  Schalter — und die Antwort nennt den Teil, der beim ersten Bau vergessen
  wurde: die Konfiguration, erzeugt aus den Werten der **vorhandenen** Bahn
  statt aus den Auslieferungswerten (sonst bekäme die zurückgeholte Bahn eine
  andere Guard-Grenze als die laufende). Die eigentliche Falle steht als eigener
  Abschnitt: Ein `--update` **mit** Schalter wählt nicht ab, es hört nur auf zu
  aktualisieren — die Dateien bleiben liegen, veralten still, und die Testsuite
  entscheidet an ihrer Anwesenheit, welche Bahn sie fährt.

  **Warum kostet mein Lauf mehr als geschätzt?** Die Antwort beginnt nicht mit
  einer Erklärung, sondern mit der Frage, **welche Zahl** der Leser überhaupt
  liest: vier Zeilen des Kontostands mit ihrem jeweiligen Bezugsrahmen, weil die
  häufigste Verwechslung die kaskadenscharfe Architektenzeile gegen die
  lebenslange Summe ist (`Kit-BL-18`, im Feld 13 % zu viel). Dann der
  `Churn-Proxy` als das, was er ist, mit dem Messweg daneben. Dann die Erklärung,
  warum die Zahl höher ist als das Ergebnis vermuten lässt — mit einer
  **gemessenen** Verhältniszahl statt einer Faustregel:

  > 58 806 159 `cache_read`-Token gegen 210 804 erzeugte — rund **280 : 1**, aus
  > dem Transkript der Sitzung, in der `Kit-BL-141` gebaut wurde.

  Daraus drei Betriebsfolgen, und zuletzt der Fall, in dem eine Kaskade
  **wirklich** doppelt zählt (fehlende Archivierung) samt der Prüfung, die eine
  **andere** Quelle befragt.

  **Das Gerüst darüber hinaus bleibt bewusst leer.** Der Eintrag sagt
  ausdrücklich „bewusst *keine* Kaskade: Jede Frage soll erst geschrieben
  werden, wenn sie wirklich gestellt wurde" — eine FAQ, die Fragen erfindet,
  wird lang und trotzdem nicht gelesen.

  Bauform der ersten Frage durchgehalten: Symptomtabelle mit den echten
  Wortlauten, Einordnung vorweg, Schritt 0 (*ist es überhaupt dieser Fall?*),
  Antwort mit **Entscheidungsspalte** statt Aufzählung, und ein eigener
  Belegstand, der Gemessenes von Übernommenem trennt.

- **`BL-141` — die Architekten-Kostenzeile war ein Zeilen-Churn-Proxy und lag im
  Feld 35 % zu niedrig.**
  ⚠️ **Feldbefund** aus `Feld B`, Kaskade 1: Die Zeile meldete
  **7,6861 USD**; die Messung aus dem Sitzungstranskript ergab **11,7582 USD**.

  `architekt_schaetzung()` rechnet `git_churn(…) × Eichfaktor` — das misst die
  **Größe des Diffs**, nicht die Arbeit. Eine Sitzung mit viel Lesen, Prüfen und
  Gegenproben und wenig geschriebenem Text wird systematisch unterschätzt. Das
  Architekten-Briefing verlangt die Transkript-Messung ausdrücklich, aber **kein
  Werkzeug des Kits konnte sie** — also schrieb sich jeder Architekt das Skript
  neu, oder er nahm die Churn-Zahl und buchte sie als gemessen.

  **Neu: `kosten.py sitzung-messen --projekt .`** — im Kit, nicht als Skript
  daneben.

  **Die drei Fallen, alle drei unter Test:**

  1. **Deduplikation über die Nachrichten-ID.** Eine Antwort erzeugt mehrere
     Transkriptzeilen mit derselben `usage`-Angabe. Mit Gegenrichtung: Ein Fix,
     der *alles* verwirft, wäre sonst grün — und die gebuchte Zahl null statt
     zu hoch.
  2. **Cache-Write nach Laufzeit getrennt** (1h = 2,0× Input, 5m = 1,25×).
     Ältere Transkripte ohne Aufschlüsselung werden konservativ als 5m
     gebucht — also eher zu niedrig. Eine zu niedrige Zahl fällt beim Abgleich
     auf; eine zu hohe wird geglaubt.
  3. **Basispreis am Modell**, längster Präfix, damit datierte Varianten und
     Plattform-Präfixe (`anthropic.claude-…`) mitlaufen. Ein unbekanntes Modell
     wird **namentlich genannt und aus der Summe gelassen**, statt geraten.

  **Die Preise sind nicht aus dem Gedächtnis geschrieben**, sondern gegen die
  Referenz des Anbieters geholt — und sie bestätigen die Feldmessung exakt:

  | | Vielfaches vom Input |
  |---|---|
  | Output | 5,0× |
  | Cache-Write 1h | 2,0× |
  | Cache-Write 5m | 1,25× |
  | Cache-Read | 0,1× |

  Nur der Basispreis hängt am Modell. Das hält die Tabelle klein und den Fehler
  unwahrscheinlich.

  **Der eigentliche Inhalt ist die Selbstprüfung.** Eine Preistabelle im
  Quelltext ist eine Behauptung. `preise_nachrechnen()` rechnet die
  **abgerechneten** headless-Läufe des Projekts mit **demselben Code** nach und
  vergleicht gegen deren `total_cost_usd`:

  ```
  ! Preistabelle stimmt nicht mehr: 1 von 1 nachgerechneten Laeufen weicht ab.
      b.json: abgerechnet 45.0000, gerechnet 30.0000 (33.3 % daneben)
    Die Zahl unten ist damit UNGEEICHT.
  ```

  Exit `2`. Das Werkzeug verschluckt die Zahl nicht — aber es lässt sie auch
  nicht als Messung durchgehen. **Gegengeprüft in beide Richtungen:** eine
  stimmige Tabelle wird ausdrücklich quittiert (eine Meldung, die immer
  erscheint, ist keine — Bauart `BL-14`), eine um 50 % falsche schlägt an; ein
  Log ohne `modelUsage` und ein Log mit unbekanntem Modell sind **kein**
  Befund, sonst meldete jedes ältere Projekt eine veraltete Tabelle.

  **Am echten Feld belegt, nicht nur an Fixtures.** Gegen das Transkript der
  Bau-Sitzung gefahren: 483 rohe Sätze, **242 nach Dedup** — mehr als die
  Hälfte Duplikate. Der Löwenanteil liegt auf `cache_read`, genau wie das
  Briefing vorhersagt.

  **Beschriftung nachgezogen:** Die Churn-Zeile heißt `Churn-Proxy` statt
  `geschätzt` (beide Bahnen); drei Tests, die die alte Beschriftung
  festschrieben, sind mitgezogen. `TEAM.md` und das Architekten-Briefing nennen
  jetzt den gemessenen Weg samt der Regel, eine ungeeichte Zahl **nicht** zu
  buchen — damit ist der dokumentierte Weg auch der richtige.

- **`BL-139` — in einer einbahnigen Ablage nannten die Regeltexte die andere
  Bahn und schickten jede Rolle an Dateien, die es dort nicht gibt.**
  ⚠️ **Feldbefund** aus `Feld B`, mit `--nur-pwsh` installiert.
  `CLAUDE.md` nannte **14** verschiedene `.sh`-Pfade, **keiner** existierte;
  `TEAM.md` kam auf 23 Nennungen. Gemessen, nicht vermutet:

  ```bash
  for f in $(grep -oE '[A-Za-z0-9_./-]+\.sh' CLAUDE.md | sort -u); do
      test -e "$f" || echo FEHLT $f
  done          # -> 14 von 14 fehlend
  ```

  **Die teuerste Stelle ist nicht die auffälligste.** Ein `./ralph.sh`, das es
  nicht gibt, scheitert sichtbar. `team.config.sh` nicht: Der Regeltext
  schickte jede Rolle dorthin, um `TEAM_SMOKE_TEST` nachzutragen — während
  `team/lib.psm1` `team.config.ps1` liest und das in seiner eigenen Warnung
  auch so sagt. **Zwei einander widersprechende Anweisungen im selben
  Systemprompt.** Wer der Regel folgt, legt eine Datei an, die nie gelesen
  wird: kein Abbruch, keine Meldung, der Wert wirkt einfach nicht. Bei
  `TEAM_SMOKE_TEST` läuft das Team dann ohne Sicherheitsnetz weiter und meldet
  in jedem Prompt „kein Smoke-Test konfiguriert", obwohl gerade einer
  eingetragen wurde.

  **Gebaut als Platzhalter, nicht als bahn-neutrale Prosa.** Die Vorlagen
  tragen an den bahnabhängigen Stellen `{{RUF}}`, `{{ENDUNG}}`, `{{KONFIG}}`,
  `{{LIB}}`, `{{REDTEAM}}`; beide Installer füllen sie beim Rendern. Der Grund
  für diesen Zuschnitt: Bahn-neutrale Prosa kostet die **kopierbaren Befehle**
  (aus `./ralph.sh` würde „der Entrypoint ralph"), und eine Nachbearbeitung der
  fertigen Datei sieht der Vorlage nicht an, welche Stellen bahnabhängig
  **sind** — eine neu dazugeschriebene Zeile nähme still die alte Bahn. Mit
  Platzhaltern sagt die Vorlage es selbst, und der Test fängt die neue Zeile.

  **Vorbelegt ist die bash-Bahn**, damit die zweibahnige Ablage — der Default —
  Byte für Byte den Text von vorher bekommt. Nur eine Abwahl ändert etwas.

  **Zwei Regionen bleiben ausdrücklich literal:** die Zwei-Bahnen-Tabelle in
  `TEAM.md` und der Ablage-Block in `CLAUDE.md`. Dort ist es ihre Aufgabe,
  beide Bahnen zu nennen. Erkannt werden sie an ihren **Überschriften**, nicht
  an Zeilennummern — und ein eigener Test schlägt an, wenn eine Region
  umbenannt wird. Sonst schützte die Ausnahme nach dem nächsten Umbau lautlos
  die falsche Stelle.

  **Unter Test, drei Fälle, gefahren in allen drei Ablagen** (`--nur-pwsh`,
  `--nur-bash`, zweibahnig): jeder genannte Pfad liegt auch da; die
  Konfiguration eigens (der **stille** Fall); und die Gegenrichtung über die
  Regionen. **Gegenprobe:** Eine einzige zurückgedrehte Stelle lässt beide
  Zusicherungen fallen.

  **Was der Lauf zusätzlich gefunden hat — die Spiegelseite, die das Feld nie
  sehen konnte.** In `TEAM.md` stand „Unangetastet bleiben deine Projektdaten:
  `team.config.sh`, `team.config.ps1`, …". In einer `--nur-bash`-Ablage ist der
  zweite Name tot; in einer `--nur-pwsh`-Ablage hätte der Platzhalter denselben
  Namen **zweimal** gerendert. Das Feld meldete nur die pwsh-Richtung — die
  bash-Richtung fiel erst auf, weil der Test **beide** fährt. Jetzt steht dort
  `team.config.*`, je Bahn eine.

  **Nebenfund an der eigenen Zusicherung:** Der erste Pfad-Regex hatte den
  Punkt weder in der Zeichenklasse noch in der Vorausschau und zerlegte
  `team.config.sh` in ein `config.sh`, das es nirgends gibt — zehn gemeldete
  tote Pfade, die alle derselbe lebende waren. Ein Wächter mit Fehlalarmen wird
  stillgelegt (Bauart `BL-14`).

- **`BL-140` — die Regeltexte zitierten den Kit-Backlog blank und verletzten
  damit genau die Regel, die sie selbst aufstellen.**

  `CLAUDE.md` schreibt vor: „Verweist eine Zeile auf den Backlog eines
  **anderen** Projekts, wird sie als `Kit-BL-<N>` geschrieben, nie als blankes
  `BL-<N>`." In derselben Datei standen dann bare Verweise auf Kit-Einträge.
  Ein frisches Projekt fängt seinen eigenen Backlog bei `BL-1` an, während der
  Regeltext im selben Repo unter `BL-1` eine Kit-Feldlehre meint — die Frage
  „darf mein erster Eintrag `BL-1` heißen?" ließ sich aus den Regeltexten
  **nicht** beantworten, weil beide Lesarten dort belegt waren.

  **Der Fix ist nicht mechanisch — und das ist der eigentliche Fund.** Der
  Backlog-Eintrag nannte ihn „mechanisch und einmalig". Beim Abtragen kamen
  zwei Fälle heraus, die ein blindes Such-und-Ersetze **kaputt gemacht** hätte:

  1. `HM-7` und `AX-3` im Glossar von `TEAM.md` sind **Formatbeispiele** für die
     Nummerierung im Beutebuch des **Zielprojekts** („Trägt eine Nummer
     (`HM-7`)"). Ein `Kit-`-Präfix wäre dort schlicht falsch.
  2. `BL-120` im Architekten-Briefing meint **weder** das Kit **noch** das
     Zielprojekt: `Kit-BL-116` nennt als Quelle das `Feld A`
     und dessen dortiges `BL-120`. Das Kit-`BL-120` ist das FAQ-Gerüst — aus
     einem **richtigen** Verweis wäre ein falscher geworden.

  **Daraus folgt eine Regel mit drei Sorten, nicht zwei:**

  | Schreibweise | meint |
  |---|---|
  | `BL-<N>` blank | meinen Backlog — den dieses Projekts |
  | `Kit-BL-<N>` | den Backlog des Kits |
  | `BL-<N>` im Projekt `<name>` | den eines **dritten** Projekts: benannt, nicht präfigiert |

  Die Regel in `CLAUDE.md.vorlage` sagte nur zwei; sie ist als Tabelle
  nachgezogen — samt der Warnung, dass die dritte Sorte genau der Fall ist, an
  dem mechanisches Umbenennen scheitert. Umgestellt sind **14** Verweise, drei
  bleiben bewusst blank.

  **Unter Test, drei Fälle:** der Lint über alle **ausgelieferten** Regeltexte
  (Vorlagen im Kit, gerenderte Dateien in einer Installation); eine
  Ausnahmeliste, in der jeder Eintrag einen **Grund** trägt und die selbst
  geprüft wird — ein verwaister Eintrag, dessen Stelle es nicht mehr gibt, wäre
  eine stille Erlaubnis für die nächste blanke Nummer an derselben Stelle; und
  die Gegenrichtung, dass die Regel überhaupt im Regeltext **steht**. Ein Lint,
  der eine ungeschriebene Regel durchsetzt, überrascht nur beim nächsten
  Textumbau.

  **Was der Lint an sich selbst gefunden hat:** Die neue Notationstabelle stand
  zuerst mit `BL-7` als Beispielzahl da und fiel durch die eigene Prüfung — zu
  Recht: Eine Notationstabelle mit echter Nummer ist von einem Verweis auf
  genau diesen Eintrag nicht zu unterscheiden. Sie führte vor, was sie
  verbietet, und nennt jetzt `<N>`.

  Mitgezogen: die Inventarzeile in `doku/regel-inventar.md` — `A.10` verlangt
  das **benannte Nachziehen**, nicht das Unterlassen der Änderung.

- **`BL-129` — „Tests bleiben grün in einbahniger Ablage" galt nur in der
  geprüften Richtung.**

  **Nachgemessen statt übernommen.** Der Eintrag nannte **109 rote Tests** in
  einer mit `--nur-pwsh` installierten Ablage. Heute sind es:

  ```
  198 passed, 371 skipped     (0 failed)
  ```

  Die Roten sind zwischen dem Aufnehmen des Eintrags und heute verschwunden,
  **ohne dass jemand `BL-129` bearbeitet hätte**: `BL-130` (Sammeltest gegen
  Plattformannahmen) und `BL-133` (`basis_umgebung()`, plus der Übersprung von
  Modulen mit bash-Abhängigkeit beim **Einsammeln**) haben den Mechanismus
  nebenbei mitgebracht.

  **Der eigentliche Abtrag ist die Zusicherung.** In `kit-test.sh` stand
  wörtlich:

  > BEWUSST NICHT geprüft: dass die Tests in einer nur-pwsh-Ablage grün
  > bleiben. Sie sind es nicht (109 rot).

  Ein Satz, der nach dem Verschwinden seiner Ursache still zur **Falschaussage**
  wurde — und den Nachweis weiter ausließ. Stufe 8 fährt die Suite jetzt in
  **beiden** Richtungen, und zwar **vor** dem `--update`, das die abgewählte
  Bahn zurückholt. Der erste Entwurf stand dahinter und hätte eine
  **vollständige** Installation gemessen: ein Nachweis, der genau das nicht
  prüft, was er behauptet.

  **Fünf Zusicherungen statt einer Farbe:** grün; Einbahnigkeit in der
  Zusammenfassung; die abgewählte Bahn als Übersprung **ausgewiesen**; der Grund
  nennt die **Abwahl** statt eines Defekts; und der Rückweg steht daneben. Ein
  stiller Übersprung von 371 Fällen liest sich am Ende wie ein bestandener
  Nachweis — schlimmer als das rote Bild, das er ersetzt.

  **Nebenfund, mitbehoben.** Der Übersprungsgrund lautete `team/lib.sh fehlt in
  dieser Ablage` — ein Satz, der nach kaputter Installation klingt, während er
  in Wahrheit eine bewusste Abwahl des Anwenders beschreibt (`BL-119`). Wer den
  Unterschied nicht liest, sucht nach einem Defekt, den es nicht gibt. Er
  unterscheidet die beiden Lagen jetzt an der **anderen** Bahn: Liegt sie da,
  war es eine Abwahl; liegt keine von beiden, ist die Ablage wirklich
  unvollständig — und dann darf der Satz auch so klingen.

  Der in `BL-129` geplante `ueberspringe_ohne_bahn()`-Helfer kam mit `BL-143`
  bereits ins Repo: `BL-142` hatte sofort einen neuen Fall erzeugt. Der Bedarf
  ist **strukturell**, nicht historisch — `ueberspringe_ohne_beide_bahnen()`
  trifft nur Tests, die beide Bahnen **vergleichen**, nicht die, die **eine**
  fahren.

- **`BL-143` — der Alias `--architekt-abschluss` buchte fest `auth=api`: gegen
  die eigene Regel, und mit sichtbarer Geldwirkung.**
  ⚠️ **Feldbefund** aus `Feld B`, Closeout der ersten Kaskade. Das
  Werkzeug meldete

  ```
  Architekt-Zeile Kaskade 1 (produkt) angelegt: 16.3990 USD
  ```

  und schrieb dabei `auth = api`. Im Kontostand landeten die 16,3990 USD damit
  in der Zeile **`real via API abgerechnet`** — echtes Geld, das nie geflossen
  ist. Der Architekt lief im Abo.

  **Warum das ein Regelbruch ist.** `CLAUDE.md` und das Architekten-Briefing
  sagen seit der Abo-Umstellung ausdrücklich: „Auch Axel und Der Architekt
  laufen Abo-first — **keine** Rolle ist mehr fest `api`", und der
  Architektenwert sei „als **Abo-Gegenwert** zu buchen und **nie**
  stillschweigend als abgerechneter Betrag auszugeben". Der Alias tat genau
  Letzteres — an der einen Stelle, die `TEAM.md` und das Briefing als den
  **normalen** Weg nennen.

  **Warum es niemandem auffiel: die Meldung schwieg zur Achse.** Der Satz oben
  ist wahr und verschweigt genau das Feld, in dem der Fehler saß. Gemerkt wurde
  es erst beim **Lesen der geschriebenen Ledger-Zeile** — also nicht durch das
  Werkzeug, sondern trotz seiner Meldung. Die Roles- und Ralph-Zeilen nennen
  ihre Achse längst (`abo 4.5571 / api 0.0000`); ausgerechnet diese nicht.

  **Der Fund, ohne den der Fix wirkungslos geblieben wäre.** Beide Wrapper —
  `status_architekt_abschluss` (bash) und `Status-ArchitektAbschluss` (pwsh) —
  lasen ausschließlich die ersten **drei** Argumente; jedes weitere fiel
  kommentarlos weg. Das ist zeichengleich der Fehler, den `BL-26` für
  `--akteur-abschluss` abgetragen hat, hier nur nie nachgezogen. Verschärfend:
  Das Briefing behauptet wörtlich, der Wrapper reiche die Schalter durch. Ein
  `--auth`, das der Alias erbt, aber der Wrapper wegwirft, wäre ein Fix, der
  sich nur im Unit-Test beweist.

  **Gebaut:** Vorbelegung `abo` statt Festlegung `api` (`--auth` bleibt
  überschreibbar — der häufige Fall ist die Vorgabe, der seltene der Schalter);
  die Erfolgsmeldung nennt die Achse, für **beide** Verben; die Durchreiche in
  beiden Wrappern nach dem `BL-26`-Muster; `TEAM.md` und Architekten-Briefing
  nachgezogen.

  **Unter Test, sieben Fälle am Verhalten** gegen ein echtes Fixture-Ledger,
  plus ein Lint über die Vorlagen: Kein Regeltext darf wieder `auth=api`
  versprechen — und `TEAM.md` darf zur Vorbelegung auch nicht einfach
  **schweigen**, denn eine stille Vorbelegung wäre nur die freundlichere
  Fassung desselben Problems. **Gegenprobe dreifach gefahren:** Vorbelegung
  zurückgedreht, Achse aus der Meldung entfernt, Durchreiche wieder ausgebaut —
  jedes Mal wird genau der zuständige Fall rot.

  **Zwei Nebenfunde, beide behoben.** `test_stufe43_architekt_abschluss.py`
  sicherte `auth == "api"` zu und schrieb die Fehlbuchung damit **fest** — ein
  grüner Test war Teil des Grundes, warum es niemandem auffiel. Und der
  `BL-130`-Wächter suchte **zeilenweise**, wodurch seine Vorausschau
  `text=True(?!\s*,\s*encoding=)` bei einem völlig korrekten, über zwei Zeilen
  gesetzten Aufruf **Fehlalarm** schlug. Ein Wächter, der an einer richtigen
  Stelle rot wird, wird nicht befolgt, sondern abgeschaltet — er liest jetzt
  den ganzen Text und leitet die Zeilennummer daraus ab, in beide Richtungen
  gegengeprüft.

  Neu im Harnisch: `entrypoint_pfad()`. `kit_pfad()` kann Entrypoints nicht
  auflösen und soll es nicht — sie folgen einer anderen Ablageregel (Wurzel in
  der Installation, `bash/entry/` bzw. `pwsh/entry/` im Kit) als die
  Team-Infrastruktur.

- **`BL-142` — `--rollen-abschluss` mit BEIDEN Notizen brach immer ab: also
  genau bei dem Aufruf, den die Doku vorgibt.**
  ⚠️ **Feldbefund** aus `Feld B`, Closeout der ersten Kaskade, erster
  echter Kostenabschluss eines Projekts:

  ```
  Method invocation failed because [System.Char] does not contain
  a method named 'StartsWith'.
  Unbekannter Modus 'K'
  ```

  Das `K` ist das **erste Zeichen der zweiten Notiz**.

  **Die Ursache ist eine Sprachregel, kein Tippfehler.** In
  `Status-RollenAbschluss` stand zweimal — und in `Status-AkteurAbschluss` ein
  drittes Mal:

  ```powershell
  $rest = if ($rest.Count -gt 1) { @($rest[1..($rest.Count - 1)]) } else { @() }
  ```

  Der `@(…)`-Ausdruck erzeugt ein Array, aber die Rückgabe aus einem
  if-**Block** läuft durch die Ausgabepipeline, und die entpackt ein
  **einelementiges** Array zu seinem Element. Bei genau zwei Notizen wurde
  `$rest` damit zum String. Sichtbar ist das beim Lesen nicht: Ein String *hat*
  eine `Count`-Property mit Wert 1, die Bedingung trägt also weiter — erst
  `$rest[0]` liefert dann einen `[Char]`.

  **Warum es niemand vorher traf.** Die Fälle laufen auseinander, und nur einer
  ist kaputt:

  | Aufruf | `$rest` wird | |
  |---|---|---|
  | zwei Notizen, kein Schalter | `String` | **kaputt** |
  | eine Notiz | `$null` | läuft durch |
  | zwei Notizen + `--addieren` | `Object[]` | funktioniert |

  Die vorhandenen Testfälle benutzten entweder eine Notiz oder hängten einen
  Schalter an. Genau der dokumentierte Aufruf war der ungetestete.

  **Der Fix ist eine Funktion, keine drei reparierten Zeilen.**
  `Rest-Ohne-Erstes` gibt mit dem **unären Komma** zurück (`return ,@($neu)`) —
  ohne das hätte sie denselben Fehler wie die Zeilen, die sie ersetzt, denn
  auch eine Funktionsrückgabe läuft durch die Pipeline. Die übrigen fünf
  `$x = if (…) { @(…) }` im Kit sind gegengeprüft: Alle liefern in beiden
  Zweigen ein dreielementiges Literal und werden nur in `foreach` benutzt —
  Ausnahmen mit Beleg, keine offenen Reste.

  **Unter Test, vier Ebenen:** Quelltext-Riegel gegen die Rückkehr des Idioms
  (läuft auf jedem Wirt); Verhalten der echten Funktion, über den
  **Syntaxbaum** aus der echten Datei geholt statt nachgebaut; **Gegenbeweis**,
  dass das alte Idiom wirklich einen String liefert; und der Aufruf aus der
  Doku end-to-end gegen ein Fixture-Projekt — zwei Notizen, kein
  Modus-Schalter.

  **Was die Gegenprobe zusätzlich gefunden hat:** Der erste Quelltext-Riegel
  verlangte den Zeilenanfang und hätte damit genau **eine** der drei Stellen
  gesehen — zwei standen als zweite Anweisung hinter einem Semikolon.
  Aufgefallen beim Zurückdrehen einer einzelnen Stelle, nicht beim Lesen. Der
  Riegel kennt jetzt beide Formen und ist gegen alle drei einzeln geprüft.

  Neu im Harnisch: `verlange_pwsh()` — das Gegenstück zu `verlange_bash()`. Es
  fehlte, weil die pwsh-Bahn ihre Fälle bisher über die parametrisierte Fixture
  fuhr; ein Test, der **nur** pwsh braucht, hatte keinen Übersprung mit Grund.

- **`BL-144` — der Selbsttest der bash-Bahn war seit `BL-136` rot, und die
  Meldung zeigte auf die falsche Stelle.**

  `BL-136` hat `gitattributes_abgleich()` in `bash/install.sh` gebaut, wörtlich
  in der Bauart von `gitignore_abgleich()`: gleiche Struktur, gleiche Quittung.

  ```
    ✓ .gitignore enthält den Block vollständig
    ✓ .gitattributes enthält den Block vollständig
  ```

  Damit hatte diese Zeile ab sofort **zwei Absender**. Stufe 6 von
  `kit-test.sh` zählt sie seit `BL-109` ungefiltert und erwartet `1`:

  ```
    ✗ und ausdruecklich als vollstaendig quittiert — erwartet '1', ist '2'
  ```

  Der Lauf brach bei 6/11 ab, unter der Beschriftung einer Prüfung über das
  `.gitignore` — an dem nichts falsch war.

  **Dahinter lag der teurere Teil.** `.gitattributes` hatte in
  `bash/kit-test.sh` **überhaupt keine Abdeckung**. Der Melde-Zweig — die
  Hälfte, für die `BL-136` geschrieben wurde, weil `--update` Projektdateien
  grundsätzlich nicht anfasst — wurde in der bash-Bahn nie gefahren. Ein
  Projekt, das den Block vom Installationstag trägt und seither nur `--update`
  gesehen hat, ist genau der Fall aus `BL-109`, und er war auf dieser Bahn
  ungeprüft.

  **Warum es niemandem auffiel.** Die Ursache steht im Commit von `BL-136`
  selbst: Als Nachweis ist dort „kit-test.ps1 alle 6 Schritte gruen (EXIT 0)"
  ausgewiesen. `kit-test.ps1` hat diese Prüfung nicht — sie ist einer von 11
  Schritten, die nur `kit-test.sh` fährt. Dieselbe Bauart wie `BL-129` bis
  `BL-131`, nur spiegelverkehrt: Dort blieb die pwsh-Bahn ungeprüft, weil auf
  dem Bauwirt kein `pwsh` liegt; hier blieb die **bash**-Bahn ungeprüft, weil
  auf dem Fundwirt keine bash-Verifikation gefahren wurde. Eine
  Zwei-Bahnen-Zusicherung, die abwechselnd auf je einer Bahn belegt wird, ist
  auf keiner belegt.

  **Der Fix, zwei Teile — und der zweite ist der eigentliche.**

  1. Die vier Prüfungen nennen jetzt ihre Datei (`.gitignore liegt … hinter
     der Vorlage` statt `hinter der Vorlage`), statt eine Meldung zu zählen,
     die inzwischen mehreren gehört. Eine Zählung über einen Meldungstext ohne
     Absender ist ein stiller Kopplungspunkt: Der nächste Abgleich derselben
     Bauart — `.editorconfig`, `.mailmap`, was auch immer — hätte den Lauf
     erneut an einer fremden Stelle abgebrochen.
  2. Die sechs `.gitignore`-Zusicherungen sind für `.gitattributes`
     gespiegelt, samt der beiden Zeilen, an denen der Melde-Zweig hängt: der
     genannten Zeilenzahl und `git add --renormalize .`. Ohne den zweiten
     Schritt wirkt der Nachtrag erst beim nächsten Klon — also genau der
     Abstand zwischen Ursache und Wirkung, den `BL-136` schließen wollte. Ein
     Nachweis, der ihn nicht mitprüft, lässt die teure Hälfte offen.
     Präpariert wird dafür, wie beim `.gitignore`, eine um zwei Zeilen
     zurückgebliebene Datei — `*.psm1` und `*.bat`, je eine aus dem LF- und
     eine aus dem CRLF-Teil, damit beide Regelblöcke getroffen sind.

  **Gegenprobe in beide Richtungen gefahren, nicht behauptet:** mit intaktem
  Melde-Zweig treffen alle sechs Zusicherungen ihre Sollwerte; mit
  ausgebautem Melde-Zweig fällt der Treffer auf `0` und die Prüfung wird rot.
  Damit ist belegt, dass sie etwas absichert und nicht nur beschreibt, was
  ohnehin gilt (Bauart `BL-14`).

  Nachweis: `kit-test.sh` 11/11, Exit 0 — Stufe 6 jetzt 30 statt 22
  Zusicherungen.

- **`BL-138` — ein grüner Lauf, der als roter endete: am Aufräumen.**
  ⚠️ **Feldbefund**, gemeldet vom Anwender beim ersten eigenen Testlauf in
  `Feld B`. Das Fortschrittsband war makellos — 542 Zeichen, 228
  Punkte, 314 `s`, kein `F`, kein `E`. Unmittelbar hinter `[100%]` begann
  eine Wand aus Traceback:

  ```
  PermissionError: [WinError 5] Access is denied:
      …\pytest-of-…\garbage-8ed10858-…\repo\.git\objects\48\54f1a4…
  ```

  und endete in einem `KeyboardInterrupt` — der Anwender hat abgebrochen und
  damit einen bestandenen Lauf als gescheitert gesehen.

  **Die Kette, nachgemessen statt vermutet.** Die Kit-Tests legen echte
  Git-Repos in `tmp_path` an; sie müssen es, denn ein Guard-Test gegen einen
  erfundenen Git-Zustand prüft nichts. Git schreibt lose Objekte
  **schreibgeschützt** — gezählt in einem liegengebliebenen Ordner: **989 von
  5622 Dateien, ausnahmslos unter `.git/objects`**. pytest hebt die letzten
  drei Laufordner auf und räumt am Sitzungsende die älteren weg. Und dort
  trennen sich die Plattformen:

  | | `unlink()` auf einer schreibgeschützten Datei |
  |---|---|
  | POSIX | **geht** — geprüft wird das Schreibrecht am *Verzeichnis* |
  | Windows | `ERROR_ACCESS_DENIED (5)` — `FILE_ATTRIBUTE_READONLY` blockiert |

  pytest fängt den Fehler ab und versucht es erneut, `chmod` plus Retry,
  **einzeln pro Datei**. Bei 989 Objekten auf NTFS dauert das minutenlang,
  und zwar schweigend.

  **Warum das ein Kit-Fehler ist und kein pytest-Fehler.** pytest räumt auf,
  was ihm übergeben wird. Übergeben hat es das Kit — mit einem Schreibschutz,
  den das Kit selbst verursacht hat, indem es Git in den Wegwerfbereich
  laufen ließ. Wer einen Bereich als wegwerfbar deklariert, schuldet ihm auch,
  dass er wegwerfbar bleibt. Derselbe Zuschnitt wie `BL-130`: eine Annahme
  des **Prüfstands** über die Plattform, nicht über den Prüfling.

  **Warum der Schaden mit der Zeit wächst.** Der Fehler tritt nicht bei dem
  Lauf auf, der ihn verursacht, sondern drei Läufe später — zu einem
  Zeitpunkt, an dem niemand mehr an den Lauf denkt, der ihn hinterlassen hat.
  Dieselbe Verzögerungsbauart wie `BL-136`, dort über den Klon.

  Neu in [`geteilt/tests/conftest.py`](geteilt/tests/conftest.py):
  `schreibschutz_loesen()` und ein `pytest_sessionfinish` mit `tryfirst=True`
  — `_pytest.tmpdir` räumt im selben Hook auf, der Schreibschutz muss also
  vorher weg sein. Angefasst wird nur der Bereich *dieser* Sitzung, und nur,
  wenn er überhaupt entstanden ist (`_basetemp` statt `getbasetemp()`, denn
  Letzteres legt den Ordner an).

  Unter Test:
  [`test_bl138_wegwerfbereich_bleibt_wegwerfbar.py`](geteilt/tests/test_bl138_wegwerfbereich_bleibt_wegwerfbar.py) —
  mit Gegenbeweis, dass die Löschung *ohne* das Lösen unter Windows wirklich
  scheitert, sonst bliebe offen, ob die Zusicherung etwas absichert oder nur
  beschreibt, was ohnehin gilt.

- **`BL-137` — `BL-129` hat eine Schreibstelle geheilt. Es waren fünf.**
  ⚠️ **Feldbefund**, aufgefallen beim ersten Lauf von
  [`bash/kit-test.sh`](bash/kit-test.sh) unter Git for Windows: Mitten in den
  Regressionstests stand, zwischen den Punkten, eine Zeile von Git —
  `warning: in the working copy of 'team.config.sh', CRLF will be replaced by
  LF the next time Git touches it`, und zwar für genau acht Dateien einer
  frischen Installation. Gemessen im Wegwerf-Repo:

  ```
  team.config.sh                 181 Wagenrückläufe
  team.config.ps1                157
  team/prompts/rolle-*.md (6×)    33 je Datei
  ralph.sh, team/lib.sh            0
  ```

  Die Trennlinie ist scharf und nennt den Täter: betroffen ist
  **ausschließlich**, was durch `fuelle()` gelaufen ist — die Routine, die
  die Platzhalter ersetzt. Wer nur kopiert wurde, ist heil geblieben.

  **Die Ursache.** `Path.write_text()` öffnet im Textmodus mit
  `newline=None`, und der übersetzt beim Schreiben jedes `\n` in `os.linesep`
  — unter Windows in `\r\n`. Nicht die geänderte Zeile allein: `fuelle()`
  liest die Datei ganz und schreibt sie ganz zurück, also bekommt jede Zeile
  ihr Byte, auch die, an der nie ein Platzhalter stand.

  Es ist zeichengleich der Fehler aus `BL-129` — dort `os.fdopen(fd, "w")` in
  `kosten.py`. Dieselbe Schicht, dieselbe Vorgabe, dasselbe Byte; damals nur
  an der Fundstelle behoben und nicht nach den Geschwistern gesucht. Die
  Bauart von `BL-131` und `BL-133`: ein Fund, der als Einzelstelle behandelt
  wird, obwohl er ein Muster ist.

  **Warum es trotzdem nicht sofort knallte.** Git-Bash entfernt unter MSYS
  die Wagenrückläufe beim `source`; die Werte kommen richtig an. Genau
  deshalb meldete der Selbsttest 519 Fälle grün, während Git danebenstand und
  die Verletzung ansagte. Ein Fehler, den die nächste Schicht repariert, ist
  keiner, der weg ist — er ist einer, der auf eine Schicht wartet, die es
  nicht tut. Die wartende Schicht heißt Commit: Vor `BL-136` trug kein
  Zielprojekt eine `.gitattributes`, eine unter Windows installierte
  `team.config.sh` ging also **mit** CRLF ins Repo, und der nächste Klon auf
  einer POSIX-Maschine bekam sie zurück, wie sie eingecheckt war.

  **Die dritte Stelle: `beutebuch.py`.** `archiviere` schreibt aktives Buch
  und Archiv neu, `set` das aktive Buch — alle drei lesen mit `read_text`
  (universal newlines) und schrieben mit `write_text` (Übersetzung). Ein
  einziges `beutebuch.py set HM-1 erledigt` rüstete damit das *ganze*
  Beutebuch um. Anders als bei den Konfigurationen fängt hier nichts auf: Das
  Beutebuch liegt unter dem Plan-Ordner, dessen Name konfigurierbar ist — das
  Fragment aus `BL-136` kann es nicht mit einer festen Regel treffen
  (nachgemessen im Feldprojekt: `attr/` leer).

  **Die pwsh-Bahn hatte den Fehler nie.** [`pwsh/install.ps1`](pwsh/install.ps1)
  schreibt über `[System.IO.File]::WriteAllText`, und das übersetzt keine
  Zeilenenden. Getroffen hat es die Bahn, von der alle annahmen, sie laufe
  ohnehin nur unter Linux — dieselbe Annahme wie in `BL-131` und `BL-133`,
  nur andersherum.

  Behoben mit `p.open("w", …, newline="")` an allen fünf Stellen — nicht mit
  `write_text(…, newline=…)`, denn den Parameter gibt es erst ab Python 3.10,
  und das Kit verlangt 3.8.

  **Der Abgleich musste mitziehen.** `--update` rendert die Kit-Fassung von
  `TEAM.md`/`CLAUDE.md` frisch und vergleicht sie gegen die installierte.
  Nach diesem Fix ist die frische LF und eine vorher installierte CRLF —
  `diff` hätte **jede** Zeile als abgewichen gemeldet und den Anwender vor
  eine Inhaltsänderung gestellt, die keine ist. Ein stiller Fehler, gegen
  einen lauten Fehlalarm getauscht, ist kein Fortschritt (Bauart `BL-14`).
  `--strip-trailing-cr` steht deshalb auch in dem Befehl, den die Meldung zum
  Nachsehen nennt: Wer dort ein anderes Bild sieht als der Installer, sucht
  an der falschen Stelle.

  Unter Test:
  [`test_bl137_zeilenenden_beim_schreiben.py`](geteilt/tests/test_bl137_zeilenenden_beim_schreiben.py)
  — Verhalten *und* Quelltext nebeneinander, mit derselben Begründung wie bei
  `BL-129`: Unter Linux ist `os.linesep` schon `\n`, ein reiner
  Verhaltenstest wäre auf der Maschine, auf der das Kit meistens gebaut wird,
  auch ohne den Fix grün. Die Quelltext-Zusicherungen prüfen über den
  Syntaxbaum statt über Textsuche — der erste Entwurf schlug an der Stelle
  an, die den Fehler *erklärt*, und hätte gefordert, die Begründung zu
  löschen.

- **`BL-136` — die Regel gegen `bad interpreter` schützte das Kit, nicht die
  Projekte.** ⚠️ **Feldbefund**, aufgefallen beim Committen von
  `Feld B`: Git meldete für jede Datei
  `LF will be replaced by CRLF the next time Git touches it`.

  Das Kit-Repo trägt seit Langem eine `.gitattributes` mit
  `* text=auto eol=lf`, und ihr Kopf nennt den Grund ausdrücklich: Unter Git
  for Windows ist `core.autocrlf=true` der Auslieferungswert, ein Klon landet
  dann mit CRLF im Arbeitsbaum, an der Shebang-Zeile hängt ein
  Wagenrücklauf, und bash sucht einen Interpreter, dessen Name auf genau
  dieses unsichtbare Zeichen endet:

  ```
  bash: ./ralph.sh: /usr/bin/env: bad interpreter: No such file or directory
  ```

  Nur: Diese Datei liegt im **Kit**. Kein Installer hat je eine in ein
  Zielprojekt gelegt — es gab dafür nicht einmal eine Vorlage. Die Regel
  schützte damit genau den Ort nicht, an dem das Kit im Feld läuft.

  **Warum es so lange unbemerkt blieb.** Der Fall entsteht *nicht* bei der
  Installation — der Installer schreibt mit LF, und unmittelbar danach läuft
  alles. Er entsteht beim nächsten **Klon oder Checkout**: später, meist auf
  einer anderen Maschine, mit einer Meldung, die nach einer kaputten
  Installation aussieht statt nach einer Zeileneinstellung. Und auf einem
  POSIX-Wirt steht `core.autocrlf` per Default auf `false` — wer das Kit
  unter Linux entwickelt, sieht den Fall nie. Dieselbe Blindstelle wie bei
  `BL-126` und `BL-129`…`BL-131`.

  Neu: [`bootstrap/gitattributes.fragment`](bootstrap/gitattributes.fragment),
  in beiden Installern behandelt wie das `gitignore.fragment` — bei der
  **Erstinstallation** ergänzt, beim **Update** gemeldet, weil die Datei dem
  Projekt gehört (Bauart `BL-109`). Die Meldung nennt auch den zweiten
  Schritt, `git add --renormalize .`: Ohne ihn wirkt der Nachtrag erst beim
  nächsten Klon, und der Abstand zwischen Ursache und Wirkung entstünde noch
  einmal.

  **Das Fragment hält sich zurück.** `* text=auto eol=lf` ist im Kit-Repo
  richtig und als Vorlage falsch: Es gälte für den Code des Projekts mit, und
  ob der LF oder CRLF trägt, ist nicht die Entscheidung des Teams. Geregelt
  werden die Dateiarten, die das Kit *mitbringt* — dieselbe Zurückhaltung,
  die `gitignore.fragment` seit jeher übt.

  Unter Test:
  [`test_bl136_zeilenenden_im_zielprojekt.py`](geteilt/tests/test_bl136_zeilenenden_im_zielprojekt.py) —
  am Quelltext, weil der Fall auf dem Wirt, auf dem die Suite meistens läuft,
  gar nicht herstellbar ist. Mitgeprüft wird die Reihenfolge: In
  `.gitattributes` gewinnt die spätere Zeile, und stünde die Sammelregel
  hinter der `.cmd`-Ausnahme, wäre diese stillschweigend aufgehoben.

- **`BL-135` — die pwsh-Bahn rechnete in der OEM-Codepage der Konsole.**
  ⚠️ **Feldbefund**, gefunden von [`pwsh/kit-test.ps1`](pwsh/kit-test.ps1)
  Schritt 6 — und zwar erst, **nachdem** `BL-134` den Schritt davor repariert
  hatte. Bis dahin stieg der Selbsttest in Schritt 5 aus und hat Schritt 6 nie
  erreicht.

  `[Console]::OutputEncoding` ist unter Windows die OEM-Codepage der Konsole
  (auf der Fundmaschine **850** — noch einmal eine andere als die cp1252 aus
  `BL-133`). PowerShell benutzt sie für **zweierlei**:

  **Beim Schreiben** — die harmlose Hälfte. Die Rollen melden mit
  `[Console]::Out.WriteLine` (Aufrufkonvention Punkt 5). cp850 kennt keinen
  Geviertstrich; .NET ersetzt ihn beim Kodieren still durch einen Bindestrich.
  Aus `[ralph] DRY-RUN — kein Claude-Aufruf.` wurde im umgelenkten Log
  `[ralph] DRY-RUN - kein Claude-Aufruf.` Kein Fehler, keine Meldung, ein
  anderes Zeichen.

  **Beim Lesen** — und hier hängt eine **Entscheidung** daran. PowerShell
  dekodiert die Ausgabe *nativer* Prozesse mit derselben Kodierung. Die
  Werkzeuge unter [`geteilt/tools/`](geteilt/tools/) schreiben seit `BL-133`
  ausdrücklich UTF-8; als cp850 gelesen wird aus dem `ü` in `überholt`
  (U+00FC) das Zeichenpaar `├╝` (U+251C U+255D). Der Filter in
  [`vollautomatik.ps1`](pwsh/entry/vollautomatik.ps1)

  ```powershell
  Where-Object { $_ -and $_ -notmatch 'erledigt|überholt' }
  ```

  trifft dann nicht mehr: Ein **überholter Fund bleibt in der Liste der
  offenen Arbeit stehen**, und die Fixphase arbeitet an etwas, das erledigt
  ist. `erledigt` ist reines ASCII und funktionierte die ganze Zeit — nur der
  Umlaut fiel durch.

  **Nicht die Schuld von `BL-133`.** Naheliegender Verdacht, und er ist falsch:
  Vorher schrieben die Werkzeuge cp1252, als cp850 gelesen wurde aus dem
  Umlaut `³`. Auch kein Treffer. Der Pfad war vorher kaputt und danach — nur
  mit einem anderen falschen Zeichen. Was `BL-133` geändert hat: Die
  Werkzeugseite spricht jetzt **eindeutig** UTF-8, und damit ist die Leseseite
  überhaupt erst reparierbar. Zwei Enden einer Leitung; eines allein
  festzuziehen genügt nie.

  Behoben in [`pwsh/lib.psm1`](pwsh/lib.psm1) — dort und nicht in den
  Entrypoints, weil die Bibliothek die eine Stelle ist, die **jede** Rolle
  durchläuft. `[Console]::OutputEncoding` und `$OutputEncoding` (die
  Gegenrichtung: was an native Prozesse *übergeben* wird) auf UTF-8, beide
  **ohne BOM** — das ist eine Kodierung für einen Strom, nicht für eine Datei.

  Unter Test:
  [`test_bl135_kodierung_an_der_prozessgrenze.py`](geteilt/tests/test_bl135_kodierung_an_der_prozessgrenze.py) —
  am **Verhalten**, mit gestellter Codepage 850. Ein Test, der auf eine
  cp850-Konsole *wartet*, liefe genau einmal: auf der Maschine, auf der der
  Fund schon gemacht ist.

  **Die Empfängerseite gehört dazu — eine Leitung hat zwei Enden.** Nach dem
  Fix auf der Schreibseite fiel im Selbsttest eine Prüfung, die vorher grün
  war: `kit-test.ps1` fängt einen kompletten Vollautomatik-Lauf auf und
  vergleicht ihn mit Mustern aus Umlauten und Geviertstrichen. Die Rollen
  schrieben nun korrekt UTF-8 — der auffangende Prozess dekodierte weiter
  cp850, und aus `über RALPH_CAP` wurde `├╝ber RALPH_CAP`. Die Prüfung fiel,
  obwohl der Lauf richtig war.

  Das **Produkt war davon nicht betroffen**:
  [`vollautomatik.ps1`](pwsh/entry/vollautomatik.ps1) importiert `lib.psm1`,
  bevor es in `Rolle-Starten` auffängt, und erbt die Einstellung damit. Vier
  eigenständige pwsh-Skripte taten es nicht — `install.ps1`,
  `kit-einrichten.ps1`, `pruefe-windows.ps1`, `team-auth-setup.ps1` — und
  `kit-test.ps1` als fünftes. Alle fünf setzen die Kodierung jetzt selbst.
  Gefunden hat sie nicht das Auge, sondern der Wächter, der zu diesem Zweck
  dazukam: *wer Prozessausgabe auffängt und `lib.psm1` nicht importiert, muss
  UTF-8 selbst einstellen.*

- **`BL-134` — der Selbsttest praeparierte sich seinen eigenen roten Test.**
  Gefunden beim ersten Lauf von [`pwsh/kit-test.ps1`](pwsh/kit-test.ps1) auf
  der Zielmaschine. Schritt 5 stellt einen gelebten Projektstand her, um zu
  belegen, dass `-Update` Projektdaten nicht anfasst — und schreibt dafür den
  Smoke-Test in **beide** Konfigurationen zurück. Die Zeile für `team.config.sh`
  ist korrekt BOM-los; die zwei Zeilen tiefer für `team.config.ps1` war
  mitkopiert und damit ebenfalls BOM-los. Für PowerShell-Quelltext ist das
  genau die Verletzung, gegen die `BL-113` steht.

  Die Folge war kein Zeichenfehler, sondern ein **Abbruch mit falschem
  Fingerzeig**: Der anschließende `install.ps1 -Update` fährt seinerseits die
  Regressionstests, die meldeten `test_powershell_quelltext_traegt_bom` als
  Fehlschlag (`1 failed, 512 passed`), und `kit-test.ps1` brach mit
  *„install.ps1 -Update schlug fehl"* ab. Der Installer hatte nichts falsch
  gemacht — die Vorbereitung hatte die Datei kaputtgemacht. Das ist die
  teuerste Bauart Fehlschlag: volle Laufzeit (2 × 13 min) für einen Befund,
  der auf die falsche Stelle zeigt.

  Unter Test:
  [`test_bl113_bom_regel.py`](geteilt/tests/test_bl113_bom_regel.py) —
  `test_wer_powershell_quelltext_SCHREIBT_setzt_das_bom`. Die Regel bindet
  nicht mehr nur die **ausgelieferten** Dateien, sondern jede Stelle im Kit,
  die zur Laufzeit eine `.ps1` schreibt. Geprüft wird am Quelltext: Die Wirkung
  ist nur unter Windows PowerShell 5.1 sichtbar, die Verwechslung aber überall.
  Datenschreiber (Ledger, Kostenlogs, Beutebuch) sind ausgenommen und müssen es
  sein — dort ist BOM-los richtig.

- **`BL-133` — der Windows-Lauf war rot, und keiner der 68 Fehlschläge kam aus
  dem Kit.** ⚠️ **Feldbefund, dritter Windows-Lauf** (`Feld B`,
  `68 failed, 436 passed`). **65** dieser Fehlschläge trugen wörtlich dieselbe
  Zeile: *„Python was not found …"*. Das ist `BL-131`, und der war abgetragen —
  nur nicht überall. `BL-131` hat **drei** Orte gezählt; der Name stand an
  **vier weiteren**:

  * **Die Entrypoints.** [`bash/entry/team-status.sh`](bash/entry/team-status.sh)
    fünfmal, [`bash/entry/vollautomatik.sh`](bash/entry/vollautomatik.sh)
    dreimal — beide sourcen `team/lib.sh` und *hätten* `$TEAM_PYTHON` gehabt.
    Die Wirkung war ungleich: Im Statusskript wurden aus Beträgen **leere**
    Zeichenketten (`real via API abgerechnet:  USD`) — nicht null, nicht
    Fehler, leer. In `vollautomatik.sh` saß der Aufruf in `budget_ok`; der
    Store-Alias endet mit **49**, also ≠ 0, und das las die Bedingung als
    *„Deckel nicht überschritten"*. Der Lauf lief weiter, und zwar genau dann,
    wenn er hätte anhalten sollen.
  * **Der Harnisch.** `lib.sh` nimmt den Namen aus `team.config.sh`; der
    Harnisch ist aber kein installiertes Projekt. Er sourct die Bibliothek
    direkt, und dann greift deren POSIX-Default. Für die zwei Werkzeugzeilen
    löste `werkzeug_wert()` das längst auf — für die **dreizehn Aufrufe in der
    Bibliothek** hatte es niemand nachgezogen. `basis_umgebung()` trägt
    `TEAM_PYTHON` jetzt mit, wie im Feld die Konfiguration.
  * **Neun einzelne Testdateien**, die ihre Umgebung weiter selbst bauten —
    mit einem Suchpfad aus festen POSIX-Verzeichnissen. Unter Windows liegt
    dort nichts: kein `git`, kein `python`, keine Agenten-CLI. Die fünfte
    Annahme, die der Sammeltest aus `BL-130` noch nicht kannte.
  * **Die Konfiguration eines gelebten Projekts** — der bittere Teil. `--update`
    fasst `team.config.*` bewusst nicht an (Projektdaten). Ein Projekt, das
    **vor** `BL-122`/`BL-131` eingerichtet wurde, trägt darin `python3`; die
    Vorlagen hatten damals gar keinen Platzhalter, es gab nichts zu füllen.
    Diese Projekte bekommen die Heilung also **nie**, auf **keiner** Bahn: Im
    Feldprojekt war `team.config.ps1` genauso betroffen wie `team.config.sh` —
    und die pwsh-Bahn ist dort die einzige, die benutzt wird.

  Beide Installer prüfen den konfigurierten Interpreter jetzt im Update-Pfad,
  in der Bauart von `BL-109` (`.gitignore`-Abgleich): geprüft wird der
  **Start**, nicht die Existenz (`command -v` *findet* den Alias — Lehre
  `BL-122`); **gemeldet**, nicht repariert, mit der nachzutragenden Zeile
  daneben. Ebenso gemeldet wird seit jetzt, dass `--nur-pwsh`/`--nur-bash` beim
  **Update** die Dateien der abgewählten Bahn nur nicht mehr aktualisiert, sie
  aber liegen lässt — und die Testsuite entscheidet an genau dieser Anwesenheit,
  welche Bahn sie fährt. Gelöscht wird nichts (Lehre `BL-12`).

- **`BL-133` (zweiter Fund) — die Python-Werkzeuge schrieben ihre Ausgabe in der
  Locale des Wirts.** Drei Fehlschläge desselben Laufs trugen nicht *„Python was
  not found"*, sondern ein Ersatzzeichen mitten im Wort:
  `assert 'an Frank übergeben' in '… an Frank �bergeben …'`.

  Gelesen und geschrieben wird in [`geteilt/tools/`](geteilt/tools/) überall mit
  ausdrücklichem `encoding="utf-8"` (`BL-113`, `BL-129`) — für `stdout`/`stderr`
  galt weiter Pythons Default, und der ist unter Windows die ANSI-Codepage der
  Maschine. Der Statuswert verließ das Werkzeug als cp1252-Bytes, der Aufrufer
  liest UTF-8, aus dem Umlaut wurde `U+FFFD`.

  Die Wirkung war kein Zeichenfehler, sondern ein **falsches Urteil**:
  `frank.sh` verglich den zurückgegebenen Status mit *„an Frank übergeben"*,
  fand keine Übereinstimmung und meldete *„Kein Fund … nichts zu tun."* — vor
  einem Beutebuch, in dem genau der stand. Die Fixphase lief an jedem
  übergebenen Fund vorbei: dieselbe Wirkung wie `BL-1`, aus einer völlig
  anderen Richtung. Alle drei Werkzeuge stellen ihre Ausgabeströme jetzt beim
  Start auf UTF-8 — nicht per `PYTHONIOENCODING`, denn das müsste jeder
  Aufrufer setzen, und eine Zusicherung, die an fünf Stellen wiederholt werden
  muss, ist eine, die eine Stelle vergisst.

  Unter Test:
  [`test_bl133_interpreter_und_ausgabe.py`](geteilt/tests/test_bl133_interpreter_und_ausgabe.py) —
  hier **am Verhalten** und nicht am Quelltext, weil beide Fälle auch auf einem
  Linux-Wirt fallen, sobald jemand sie zurückdreht. Die Locale wird dafür
  gestellt (`PYTHONIOENCODING=cp1252`) statt vorausgesetzt.

- **`BL-131` — die Bash-Bahn verdrahtete `python3`, auch unter Windows.**
  ⚠️ **Feldbefund, zweiter Windows-Lauf.** An drei Stellen stand der Name des
  Interpreters fest im Text, jedes Mal mit derselben Begründung: *„dieser
  Installer läuft unter Linux"*. Unter **Git for Windows** läuft er das nicht.

  * [`bash/lib.sh`](bash/lib.sh) — **dreizehn** Aufrufe (`python3 -c '…'`).
  * [`bash/entry/team.config.sh`](bash/entry/team.config.sh) — `TEAM_KOSTEN_TOOL`
    und `TEAM_BEUTEBUCH_TOOL` mit eingebautem `python3`, **ohne Platzhalter**.
  * [`bash/install.sh`](bash/install.sh) — der Installer selbst und der Wert,
    den er in **beide** Konfigurationen schreibt.

  Unter Windows ist `python3` nicht abwesend, sondern **belegt**:
  `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe` ist der
  App-Execution-Alias aus dem Microsoft Store. `command -v` findet ihn, der
  Aufruf startet den Store und meldet *„Python was not found"*, Exit 49. Tot
  waren damit `team_promise_in`, `team_result_meldet_erfolg`,
  `team_429_reset_epoch` und die Budget-Summen — also genau die Funktionen, an
  denen Geld und Abbruchentscheidungen hängen.

  **Warum es so lange unbemerkt blieb.** Der Fund ist zeichengleich mit
  `BL-122`/`BL-125`, und `Finde-Python` löst ihn auf der pwsh-Bahn seit Langem;
  die pwsh-Bahn hat die dreizehn Blöcke sogar ganz durch native Ausdrücke
  ersetzt. Die Bash-Bahn hat es nie nachgezogen, weil sie als *„die
  Linux-Bahn"* galt und niemand sie unter Windows gefahren hat. Das ist die
  Doppelbahn-Drift, gegen die der gemeinsame Harnisch gebaut wurde — an einer
  Stelle, die kein Test berührte.

  Bitter dabei: Ein Windows-Projekt bekam eine **korrekte** `team.config.ps1`
  und eine **kaputte** `team.config.sh` daneben. Beide Installer schreiben
  beide Konfigurationen (`BL-126`) — die eine war seit jeher halb blind, weil
  es dort gar keinen Platzhalter zu füllen gab.

  Behoben: `TEAM_PYTHON` als Bibliotheks-Default nach Vertrag Punkt 6, beide
  Werkzeugzeilen davon abgeleitet, `{{PYTHON}}` jetzt auch in der
  `.sh`-Vorlage, und `finde_python()` in `install.sh` als Gegenstück zu
  `Finde-Python` — **plattformabhängige Reihenfolge** (`python` vor `python3`
  unter Windows) und **Start *und* Version** als Probe, weil `command -v`
  allein den Store-Alias findet.

  Unter Test:
  [`test_bl131_python_name_ist_maschinensache.py`](geteilt/tests/test_bl131_python_name_ist_maschinensache.py) —
  sieben Zusicherungen, davon fünf am Quelltext, weil `python3` unter Linux
  richtig ist und ein Verhaltenstest den Rückfall dort nicht meldete.

- **`BL-132` — `text=True` ohne Kodierung machte `stdout` zu `None`.**
  ⚠️ **Feldbefund, zweiter Windows-Lauf — und die Erklärung für ein Rätsel aus
  `BL-130`.** 77 `subprocess`-Aufrufe der Testsuite standen auf `text=True`
  ohne `encoding=`. Die Ausgabe des Kindprozesses wird dann in der **Locale des
  Wirts** dekodiert; auf einem deutschen Windows ist das cp1252, und das erste
  UTF-8-Byte wirft `UnicodeDecodeError`.

  Der Fehler fällt aber **im Reader-Thread von `subprocess`** an. Der Aufrufer
  sieht keine Ausnahme — er bekommt `stdout is None`. Der Test scheitert
  Zeilen später mit `'NoneType' object has no attribute 'splitlines'` bzw.
  `argument of type 'NoneType' is not iterable`, und pytest meldet die wahre
  Ursache nur als **Warnung**, die in einem roten Lauf niemand liest. Genau
  daran ist die erste Analyse hängengeblieben: Der `NoneType` war aus dem
  Testcode heraus nicht erklärbar, weil `capture_output=True` ihn nicht
  erzeugen *kann* — die Ursache lag eine Ebene tiefer.

  Wo die Dekodierung nicht warf, log sie: `Rolle siehe CLAUDE.md â€” lies sie
  zuerst.` Dasselbe Muster, nur ohne Ausnahme.

  Behoben: `encoding="utf-8", errors="replace"` an allen 77 Stellen. Der
  Sammeltest in `BL-130` hält es fest — `text=True` ohne `encoding=` fällt ab
  jetzt auf **jedem** Wirt auf.

  Ebenfalls hier berichtigt: Das Entrypoint-Muster des `BL-130`-Wächters
  verlangte, dass die Argumentliste direkt nach dem Skriptnamen endet, und
  ließ `["./team-status.sh", "--budget"]` durch. Fünf Tests blieben deshalb
  rot, während der Wächter grün meldete — ein Wächter, der die Hälfte der
  Fälle nicht sieht, ist schlimmer als keiner.

- **`BL-130` — die Testsuite maß unter Windows sich selbst, nicht das Kit.**
  ⚠️ **Feldbefund, dieselbe Windows-Maschine wie `BL-113` und
  `BL-122`…`BL-128`.** Der erste Lauf der Regressionssuite unter nativem
  Windows meldete **160 Fehlschläge**. Keiner davon kam aus dem Kit. Der
  Harnisch in `geteilt/tests/conftest.py` war für einen POSIX-Wirt
  geschrieben, und das stand nirgends — es war einfach so.

  Vier Annahmen trugen dort nicht:

  1. **`bash` im PATH ist eine Bash.** Unter Windows ist es fast immer
     `C:\Windows\System32\bash.exe`, der WSL-Launcher. Ohne installierte
     Distro schreibt der eine **UTF-16-Diagnose nach stdout** und endet
     mit 1. Ein Test, der damit einen Konfigwert liest, bekommt eine
     Zeichenkette voller NUL-Bytes — und die Meldung, die der Mensch sieht,
     lautet `ValueError: mkdir: embedded null character in path`. Zwölf
     Tests scheiterten so; keine dieser Meldungen nennt die Ursache.
  2. **Ein Skript ist ausführbar, weil das x-Bit gesetzt ist.**
     `subprocess.run(["./ralph.sh"])` verlässt sich auf den Shebang; Windows
     liest keinen. 24 Tests endeten mit
     `OSError: [WinError 193] %1 is not a valid Win32 application`.
  3. **Der PATH wird mit `:` zusammengesetzt.** Unter Windows trennt `;`.
     Der `claude`-Stub, den ein Test gerade gelegt hatte, wurde nie gefunden.
  4. **Ein Kindprozess braucht nur `HOME` und `PATH`.** Unter Windows braucht
     er `SystemRoot` (sonst antwortet jeder Prozessstart mit einem
     COM+-Registry-Fehler) und `PATHEXT` (sonst findet PowerShell kein
     einziges `.exe` — `git` ist dann *not recognized*, und **jeder** Test,
     der ein Wegwerf-Repo baut, fällt). Das traf auch die **pwsh**-Bahn, die
     mit der Plattformfrage sonst nichts zu tun hat.

  Dazu, aus derselben Wurzel: 30 Stellen schrieben `python3` fest — den Namen,
  den es unter Windows nicht gibt (`Finde-Python` in `install.ps1` löst genau
  deshalb `python` vor `python3` auf, **BL-125**). Was `where python3` dort
  findet, ist der App-Execution-Alias aus dem Microsoft Store.

  **Warum das ein eigener Fund ist und keine Fußnote.** Ein roter Lauf, dessen
  Fehler nicht vom Prüfgegenstand kommen, ist schlimmer als ein ausgelassener:
  Er kostet dieselbe Zeit und liefert eine Zahl, der niemand mehr glaubt.
  `BL-129` lag in dieser Liste und war von den 159 anderen nicht zu
  unterscheiden. Betroffen ist auch der **Selbsttest der Erstinstallation**
  (`BL-127`) — der lief auf Windows in genau diese 160 Fehlschläge.

  Behoben in `conftest.py` als eine Plattformschicht, die die vier Annahmen an
  **einer** Stelle auflöst statt in 21 Testdateien: `BASH` (sucht Git for
  Windows, **schließt den WSL-Stub in System32 aus**), `entrypoint_aufruf()`,
  `pfad_voran()`, `basis_umgebung()` und `werkzeug_wert()`. Findet sich keine
  echte Bash, wird die Bash-Bahn **mit Begründung übersprungen** statt rot —
  ein WSL-Stub, der UTF-16-Müll liefert, beweist nichts über das Kit. Die
  Übersprungenen stehen in der Doppelbahn-Quote am Ende jedes Laufs.

  Unter Test:
  [`test_bl130_harnisch_plattformannahmen.py`](geteilt/tests/test_bl130_harnisch_plattformannahmen.py).
  Die Bash-Auflösung wird mit **gestellter Plattform** gefahren — der Zweig ist
  sonst nur unter Windows erreichbar und wäre genau die Bauart „Zweig, der nie
  gefahren wurde", gegen die `BL-126`…`BL-128` stehen. Ein Sammeltest hält die
  vier Annahmen über alle Testdateien fest; er fällt auf **jedem** Wirt,
  sobald eine Datei wieder `["bash", …]` oder `"python3 team/tools/…"`
  schreibt.

- **`BL-129` — das Ledger bekam unter Windows in jeder Zeile ein CR-Byte.**
  ⚠️ **Der Befund, der unter den 160 aus `BL-130` lag.**
  `_ledger_zeile_ersetzen()` in `kosten.py` schrieb die Datei mit
  `os.fdopen(fd, "w")`, also im Textmodus mit `newline=None`. Der übersetzt
  jedes `\n` in `os.linesep` — unter Windows in `\r\n`. Betroffen war nicht
  die neue Zeile allein: Die Funktion schreibt die Datei **vollständig neu**,
  also bekamen Kopfzeile und alle Bestandszeilen bei **jedem**
  `akteur-abschluss` ein CR dazu.

  **Genau dieses Byte ist der Schaden, gegen den `HM-36`, `HM-37` und `HM-38`
  die Feldwerte sanitisieren**: Ein rohes CR wird beim nächsten Einlesen unter
  universal newlines als Zeilenumbruch gelesen und zerlegt die Zeile. Drei
  Funde, drei Tests, eine Sanitisierungsfunktion — und die Plattform setzte
  das Byte hinterher wieder ein. Die Absicherung konnte den Fall nicht fangen:
  Sie greift auf die **Feldwerte**, eine Schicht über dem Schreibvorgang. Eine
  Absicherung, die eine Schicht zu früh sitzt, sieht aus wie eine und ist
  keine — dieselbe Bauart wie `BL-15`/`BL-17`.

  Zweite Hälfte, Bauart `BL-125`: Dieselben Aufrufe nannten **keine
  Kodierung**, galten also in der Locale des Wirts. Auf einem deutschen
  Windows ist das cp1252. Eine Notiz mit Umlaut wandert dann als cp1252 in die
  Datei; sobald sie den Rechner wechselt, ist sie Mojibake, und
  `kosten.py ledger` bricht auf einem UTF-8-Wirt mit `UnicodeDecodeError` ab.

  Behoben: `newline=""` und `encoding="utf-8"` am Schreibvorgang, `encoding`
  an **allen** Lesestellen (die Kostenlogs mit `utf-8-sig`, weil Windows
  PowerShell 5.1 sie mit BOM schreibt — `BL-113`/Stufe 3). Ein vor dem Fix
  entstandenes CRLF-Ledger **heilt beim nächsten Schreibzugriff**, statt den
  Schaden weiterzutragen.

  Unter Test:
  [`test_bl129_ledger_zeilenende_und_kodierung.py`](geteilt/tests/test_bl129_ledger_zeilenende_und_kodierung.py).
  Neben den Verhaltenstests steht eine **Quelltext-Zusicherung**: Unter Linux
  ist `os.linesep` bereits `\n` und die Locale praktisch immer UTF-8 — ein
  rein verhaltensbasierter Test wäre auf der Maschine, auf der er meistens
  läuft, auch **ohne** den Fix grün und meldete den Rückfall genau dort nicht,
  wo er gebaut wird. Dieselbe Überlegung wie bei `BL-126`.

- **`BL-126` — ein mit `--nur-pwsh` installiertes Projekt ließ sich nicht
  aktualisieren.** ⚠️ **Feldbefund, dieselbe Windows-Maschine wie
  `BL-122`…`BL-125`.** Der Update-Pfad **beider** Installer erkannte eine
  Installation nur an `team.config.sh`. Genau die gibt es in einem einbahnig
  pwsh installierten Projekt nicht — der Installer erklärte es für *keine*
  T.E.A.M.-Installation und stieg mit Exit 2 aus, **bevor** er die fehlende
  Bahn nachziehen konnte.

  Damit war der Rückweg, den `BL-119` ausdrücklich verspricht („ein Update
  ohne Schalter macht das Projekt wieder vollständig"), in dieser Richtung
  versperrt: Die Abwahl war die Einbahnstraße, die sie nicht sein darf. Auf
  der pwsh-Bahn wiegt das schwerer als auf der anderen — ein Windows-Projekt
  ohne bash ist der **Normalfall**, für den sie gebaut ist.

  **Warum es durchrutschte, steht im Selbsttest selbst.** `kit-test.sh`
  Stufe 8 bewies den Rückweg — für `--nur-bash`. Also für die Richtung, in
  der die Datei, an der alles hängt, zufällig vorhanden ist. Die andere
  Richtung ist nie gefahren worden.

  Behoben auf beiden Bahnen: Als Merkmal zählt jede der beiden
  Konfigurationen, und fehlt die `.sh`, werden die Projektwerte aus der
  `.ps1` gelesen (`$TEAM_X = Team-Wert 'TEAM_X' 'wert'` — gelesen, nicht
  gesourct). Aus **welcher** Quelle sie stammen, steht jetzt in der Ausgabe:
  Ein stiller Rückfall auf die Auslieferungswerte gäbe der zurückgeholten
  Bahn eine andere Guard-Grenze als der, die schon läuft.

  Unter Test: `kit-test.sh` Stufe 8 fährt jetzt **beide** Richtungen als
  echte Installation, und
  [`test_bl126_update_beide_konfigurationen.py`](geteilt/tests/test_bl126_update_beide_konfigurationen.py)
  hält die Zusicherung am Quelltext beider Bahnen fest — der Lauf kann die
  pwsh-Fassung auf einer Maschine ohne PowerShell nicht prüfen, und genau
  dort ist der Fehler aufgetreten.


- **`BL-127` — jede frische Installation hat ihre Regressionstests
  übersprungen.** `team_pytest()` war **innerhalb** des `--update`-Blocks
  definiert. Bash definiert eine Funktion erst, wenn die Definition
  *ausgeführt* wird; auf dem Erstinstallations-Pfad wurde der Block nie
  betreten. Der Selbsttest rief eine Funktion auf, die es nicht gab
  (`team_pytest: command not found`), fing den Fehlschlag im `if` ab und
  meldete in Gelb „pytest nicht gefunden — Regressionstests übersprungen".

  Das ist genau die Prüfung, für die `BL-124` einen Tag zuvor gebaut wurde —
  tot auf dem Weg, auf dem sie am meisten zählt. Die Einrückung tarnte es:
  Die Funktion stand in Spalte 0 und sah nach oberster Ebene aus. Die
  pwsh-Bahn war **nicht** betroffen (dort steht `Finde-Pytest` oben), also
  stille Drift zwischen zwei Fassungen derselben Lehre.

  Gefunden nicht durch Lesen, sondern durch einen **Trockenlauf** mit einem
  Schalter, den sonst niemand benutzt. Behoben durch Herausziehen der
  Definition; `kit-test.sh` Stufe 2 sieht jetzt nach, ob der Installer seine
  Tests **wirklich gefahren** hat (er hatte 442 Fälle grün, sobald die
  Funktion erreichbar war). Statisch festgehalten in
  [`test_bl127_selbsttest_der_erstinstallation.py`](geteilt/tests/test_bl127_selbsttest_der_erstinstallation.py).


- **`BL-128` — eine gelungene Installation meldete sich selbst als kaputt.**
  Der Selbsttest lief mit einem ungeprüften Glob: `for f in "$ZIEL"/*.sh`
  reicht bei null Treffern das **Muster** durch, `bash -n "$ZIEL/*.sh"`
  scheitert an einer Datei namens `*.sh`, und heraus kam
  `✗ Syntaxfehler: *.sh` samt Exit 1. Getroffen hat es jede mit `--nur-pwsh`
  installierte Ablage — dort *gibt* es keine `.sh`, und das ist kein Defekt,
  sondern die Abwahl aus `BL-119`.

  Behoben an **beiden** Selbsttests (Erstinstallation und Update — ein Fix an
  nur einer Stelle wäre genau die halbe Arbeit, aus der solche Funde
  entstehen). Die leere Ablage wird jetzt benannt statt stillschweigend
  übersprungen: „keine .sh zu prüfen (Bash-Bahn abgewählt)". Unter Test in
  derselben Datei wie `BL-127`, dazu eine Zusicherung in `kit-test.sh`
  Stufe 8.


- **`BL-125` — `kosten.py` war unter Windows nicht ladbar, und das nahm alles
  mit.** ⚠️ **Feldbefund, dieselbe Windows-Maschine wie `BL-122`…`BL-124`.**
  `team-test.cmd` brach mit **21 Sammelfehlern** ab, alle mit demselben Satz
  am Ende: `ModuleNotFoundError: No module named 'fcntl'`.

  **Die sichtbare Hälfte war die harmlosere.** `fcntl` ist ein POSIX-Modul,
  und es stand als **ungeschützter Import auf Modulebene**. Damit fiel nicht
  die Sperre aus, für die es da war, sondern die **ganze Datei** — und mit ihr
  jeder Kostenpfad der pwsh-Bahn: `--akteur-abschluss`, `--rollen-abschluss`,
  `--ralph-abschluss`. Ein Lauf auf der nativen Windows-Bahn hätte seine
  Kosten nie in den Ledger geschrieben. Aufgefallen ist es an den Tests, weil
  21 Testdateien `kosten.py` importieren; getroffen hat es den Betrieb.

  **Warum es so lange unsichtbar blieb:** Die pwsh-Bahn ist auf der
  Entwicklungsmaschine nie gefahren (dort ist kein `pwsh`), und die
  Testsuite lief dort unter Linux, wo `fcntl` selbstverständlich da ist. Ein
  plattformgebundener Import fällt eben nicht dort auf, wo er geschrieben
  wird.

  Behoben, ohne die Zusicherung aufzugeben, für die die Sperre gebaut wurde
  (**HM-48**: zwei überlappende Abschluss-Aufrufe dürfen sich keine Zeile
  herausreißen). `fcntl` und `msvcrt` werden **weich** geladen; welcher
  Mechanismus greift, entscheidet `_lock_belegen()` zur Laufzeit — `flock`
  auf POSIX, eine Bytebereichssperre auf Byte 0 derselben Lock-Datei unter
  Windows. Beide sperren handle-bezogen, also auch zwischen zwei Threads
  desselben Prozesses. Weil die Windows-Sperre kein blockierendes Warten mit
  offenem Ende kennt, wartet der Windows-Zweig **30 Sekunden** gepollt und
  meldet danach mit Wortlaut, dass **nichts** geschrieben wurde. Fehlt beides,
  wird ebenfalls nichts geschrieben: Ein stiller Schreibvorgang ohne Sperre
  wäre `HM-48` zurück.

  Unter Test: [`test_bl125_kosten_ohne_fcntl.py`](geteilt/tests/test_bl125_kosten_ohne_fcntl.py),
  fünf Fälle. Der Windows-Fall wird **nachgestellt**, nicht abgewartet: ein
  Import-Blocker versteckt `fcntl` (und `msvcrt`) genau so, wie Windows es
  zeigt, und ein `msvcrt`-Doppel fährt die HM-48-Race auf dem Windows-Zweig —
  beide Zeilen müssen überleben, und die Spur der Sperre muss sich
  abwechseln. Der fünfte Fall prüft die **Klasse statt des Falls**: Kein
  Werkzeug unter `team/tools/` darf ein plattformgebundenes Modul
  ungeschützt auf Modulebene importieren. Gegenprobe gefahren: `kosten.py`
  aus `HEAD` zurückgespielt, **alle fünf** Fälle fallen.

  **Weiterhin blind geschrieben** wie `BL-122`…`BL-124`: Auf dieser Maschine
  ist kein Windows. Der Windows-Zweig ist gegen ein Doppel bewiesen, nicht
  gegen `msvcrt` selbst — der Rest, den `BL-117` ohnehin schon ausweist.


- **`BL-124` — pytest war installiert, und das Kit meldete „nicht gefunden".**
  ⚠️ **Feldbefund, dieselbe Windows-Maschine wie `BL-122` und `BL-123`.**
  Gesucht wurde ein **Name im PATH**, statt die Fähigkeit zu proben.
  `pip install pytest` legt die ausführbare Datei in ein Scripts- bzw.
  bin-Verzeichnis, das oft nicht im PATH steht — bei `--user` warnt pip beim
  Installieren sogar ausdrücklich davor. Das Modul ist dann da und
  importierbar; der Befehl ist es nicht.

  **Das Kit hat den Zustand selbst erzeugt.** `team-test.sh` empfahl wörtlich
  `pip install --user pytest` — also genau die Installationsart, deren
  Zielverzeichnis typischerweise fehlt — und meldete danach „pytest nicht
  gefunden", zusammen mit derselben Empfehlung noch einmal. Wer ihr folgt,
  landet in einer Schleife, aus der die Meldung nicht herausführt.

  Die zweite, leisere Hälfte: Ein `pytest` im PATH kann zu einer **anderen**
  Python-Installation gehören als das Python, unter dem `team/tools/` läuft.
  Dann laufen die Tests unter einem anderen Interpreter als der Code, den sie
  prüfen — grün, und trotzdem ohne Aussage. Der Modulaufruf über denselben
  Interpreter schließt beides zugleich aus.

  Behoben auf **beiden Bahnen** und an allen fünf Stellen, die pytest suchen:
  `team-test.sh`/`.ps1`, die Selbstverifikation in `install.sh`/`.ps1` (sie
  meldete „Regressionstests übersprungen", obwohl pytest da war), die
  Vorflug-Prüfung in `kit-einrichten.sh`/`.ps1` und `kit-test.ps1`. Überall
  gilt jetzt: erst `<python> -m pytest`, dann als **zweiter** Versuch ein
  `pytest` im PATH, dessen Interpreter man nicht kennt. Die Meldung im
  Fehlerfall sagt, dass **beide** Wege probiert wurden.

  Ein `set -e`-Fallstrick in der eigenen Ergänzung mitentschärft: Eine
  `&&`-Kette, deren erstes Glied im **Erfolgsfall** falsch ist, hätte
  `kit-einrichten.sh` beendet. Jetzt ein `if`.

  Unter Test: [`test_bl124_pytest_als_modul.py`](geteilt/tests/test_bl124_pytest_als_modul.py),
  zwei Fälle — der Modulweg muss versucht werden, **und** kein Hinweis darf
  `--user` empfehlen, ohne die PATH-Falle zu nennen. Gegenprobe gefahren:
  `team-test.sh` aus `HEAD` zurückgespielt, **beide** Fälle fallen namentlich.


- **`BL-123` — die neun `.cmd`-Aufrufer riefen `pwsh` blank auf.**
  ⚠️ **Feldbefund, dieselbe Windows-Maschine wie `BL-122`.** Fehlt PowerShell 7
  im PATH **genau dieser** cmd-Sitzung, war
  `'pwsh' is not recognized as an internal or external command` die einzige
  Auskunft, die der Anwender bekam — eine Meldung über `cmd`, nicht über das
  Kit. Sie nennt weder Ursache noch Ausweg und sieht aus wie eine kaputte
  Installation.

  Das Kit kannte diese Falle bereits und hatte sie an anderer Stelle gelöst:
  `Team-ClaudeBefehl` löst `claude` über `Get-Command` auf und meldet den
  Fehlschlag mit eigenem Wortlaut, weil eine gescheiterte Auflösung sonst wie
  ein Auth-Fehler aussieht. Für den Interpreter, der die **ganze Bahn** trägt,
  galt dieselbe Lehre nicht — obwohl er die empfindlichere Stelle ist: Wer
  `claude` nicht findet, hat ein Kit, das läuft und sich beschwert. Wer `pwsh`
  nicht findet, hat gar nichts.

  Alle neun `.cmd` lösen `pwsh` jetzt über den PATH und die üblichen
  Installationsorte auf (`%ProgramFiles%`, `%ProgramW6432%`, `WindowsApps`).
  Scheitert das, nennen sie die Ursache, dass Windows PowerShell **5.1 nicht
  genügt**, den `winget`-Befehl und die Notwendigkeit einer **neuen** Sitzung —
  und enden mit Exit 127 statt mit einer Fremdmeldung.

  **Der generierte Launcher unter `~\.claude\scripts\` hatte dieselbe
  Zeile** und ist mitbehandelt. Dazu ein Folgefund: Eine **veraltete** Fassung
  davon wäre als „zeigt woandershin" abgelehnt worden und still kaputt
  geblieben. Sie wird jetzt nachgezogen — mit Sicherung daneben und nur, wenn
  sie erkennbar auf dieselbe Kit-Datei zeigt. Dieselbe Lehre wie `A.12.1`: Ein
  veralteter Aufrufer meldet sich nicht, er behauptet eines Tages, das Kit sei
  nicht da.

  Unter Test: [`test_bl123_pwsh_aufloesung.py`](geteilt/tests/test_bl123_pwsh_aufloesung.py),
  zwei Fälle — kein blanker Aufruf, **und** jede Auflösung nennt einen Ausweg
  (eine Auflösung ohne Meldung wäre nur eine leisere Fassung desselben
  Fehlers). Gegenprobe gefahren: alte Fassung von `marv.cmd` zurückgespielt,
  Test fällt namentlich.


- **`BL-121` — das Aufnahme-Interview fragte nach dem Produktivcode-Ordner,
  prüfte aber nie, ob es ihn gibt, und legte ihn nie an.**
  ⚠️ **Im Feld bestätigt**, auf einer Windows-Maschine: „die Ordner werden
  automatisch erstellt, außer `src/`" — und nachgeschoben, in der
  allgemeineren und schlimmeren Form: **auch ein eingegebener Name wird nicht
  angelegt.** An `src/` war nichts besonderes; der Installer legte schlicht
  keinen Produktivcode-Ordner an, egal wie er hieß.

  Der Name wurde nur **eingesetzt** — in die Guard-Grenze, in den Prüfumfang,
  in die Briefings der drei Read-Only-Rollen, in `team.config.sh`. Test- und
  Plan-Ordner entstehen sehr wohl; der Produktivcode-Ordner war der einzige,
  der ausfiel. Zwei stille Folgen: Im neuen Projekt zeigten Guard und
  Prüfumfang nach der Installation auf einen Pfad, den es nicht gibt. Im
  Bestandsprojekt wurde ein Tippfehler wortlos übernommen, und der erste
  Bericht meldete „sauber" über einen leeren Suchraum — dieselbe Fehlerklasse
  wie `BL-52`, nur eine Frage früher.

  `src/` bleibt Standardvorschlag und die Frage bleibt eine Frage. Neu ist,
  was **danach** passiert: Ist der Ordner da, wird er genommen. Ist er es
  nicht, wird er **angelegt und das angesagt** — im Bestand aber erst,
  nachdem die vorhandenen Wurzelordner zum Abschreiben gezeigt wurden, denn
  dort ist Nichtexistenz eher ein Tippfehler als ein neues Projekt (dieselbe
  Erwägung wie bei `kandidaten_ausserhalb()` für `BL-52`). Nicht-interaktiv
  wird ohne Rückfrage angelegt, aber nicht wortlos.

  **Die `.gitkeep`-Frage ist entschieden statt offengelassen:** Ein neu
  angelegter leerer Ordner bekommt eine Platzhalterdatei. Ohne sie wäre er
  nach dem Commit weg, den der nächste Schritt ausdrücklich verlangt
  („Committen — VOR dem ersten Guard-Lauf"), und der Fehler wäre beim
  nächsten Klon zurück. Dieselbe Lösung wie bei `ermittlungsakten/`.

  Beide Bahnen. Gegenprobe in `kit-test.sh` Stufe 2, drei Zusicherungen:
  `src/` existiert nach der Installation, ein **eigener** Name
  (`TEAM_INIT_PRODUKTIVCODE=quelle/`) wird ebenso angelegt **und angesagt**,
  und der Ordner überlebt einen echten `git commit`. Die Commit-Probe läuft in
  einem eigenen Wegwerf-Repo, damit sie den Git-Stand nicht verändert, gegen
  den die späteren Stufen prüfen.


- **`BL-122` — auf der pwsh-Bahn war ein Exit-Code != 0 eine Ausnahme statt
  eines Werts. Die gesamte Fehlerbehandlung war damit unerreichbar.**
  ⚠️ **Feldbefund von einer echten Windows-Maschine.** `kit-einrichten.ps1`
  brach in der Übergabe an `install.ps1` ab; die Meldung nannte `python3.exe`
  und sah aus wie ein fehlendes Python. Es war keines.

  Unter Windows liegen in `%LOCALAPPDATA%\Microsoft\WindowsApps`
  App-Execution-Aliase namens `python.exe` **und** `python3.exe`.
  `Get-Command` gibt sie klaglos zurück; gestartet öffnen sie den Microsoft
  Store und enden mit Exit-Code 9009. Genau dafür war die Kandidatenschleife
  gebaut — sie prüft die Antwort, nicht den Namen. Nur kam sie nicht dazu:
  Seit **PowerShell 7.4** steht `$PSNativeCommandUseErrorActionPreference`
  standardmäßig auf `$true`, ein nativer Befehl mit Exit-Code != 0 löst damit
  einen Fehler nach `$ErrorActionPreference` aus — und `install.ps1` steht auf
  `'Stop'`. Der Platzhalter warf einen **terminierenden** Fehler beim ersten
  Kandidaten. `2>$null` half nicht: Die Meldung kommt von PowerShell, nicht
  vom Programm.

  **Die Fehlerklasse ist breiter als die Fundstelle.** Die ganze Bahn ist für
  den klassischen Vertrag geschrieben — aufrufen, `$LASTEXITCODE` lesen,
  entscheiden. Unter 7.4 war jede dieser Entscheidungen tot, sobald der
  Aufrufer auf `'Stop'` stand: `Team-ClaudeSchreiben` liest den Exit-Code der
  Agenten-CLI, und daran hängen **429-Mechanik, Abo-nach-Key-Fallback und
  Ergebnisprüfung** — jeder normale CLI-Fehler hätte den Lauf gerissen statt
  ihn zu behandeln. Dazu die freundliche Meldung „ist kein Git-Repository"
  samt Exit 2, und die Selbstverifikation, die ihre Befunde über
  `$LASTEXITCODE` meldet.

  **Warum kein Test das gefunden hat:** nicht wegen der Plattform — die
  Präferenz gilt überall — sondern weil unter Linux jeder dieser Aufrufe
  **gelingt**. Geprüft worden ist immer nur der glückliche Pfad. Der
  Store-Platzhalter macht unter Windows aus dem glücklichen Pfad einen
  Fehlerpfad und legt frei, was die ganze Zeit unerreichbar war. Dieselbe
  Familie wie `BL-113`: unter pwsh 7 auf Linux vollständig grün, auf dem Ziel
  an der ersten Datei gescheitert.

  Behoben in vier Schritten: Der Pin
  `$PSNativeCommandUseErrorActionPreference = $false` steht jetzt in **allen
  17 ausführbaren pwsh-Dateien** und zusätzlich in `lib.psm1` — eine
  Modulfunktion erbt die Präferenz des Aufrufers nicht zuverlässig. Die
  Python-Suche fragt **plattformgerecht** (unter Windows `python` zuerst, denn
  python.org und winget legen kein `python3.exe` an), fängt den Kandidaten in
  `try/catch` ab und prüft die **Version** statt eines Lebenszeichens — ein
  Python 2 beantwortet `print(1)` klaglos. Der stille Rückfall auf `python3`
  ist weg: Er trug sich unter Windows in `team.config.ps1` ein und ließ Kosten
  und Beutebuch auf einen Namen zeigen, den es dort nachweislich nicht gibt.
  Und `pruefe-windows.ps1` meldet einen Platzhalter nicht mehr als grün — als
  Vorflug-Probe der Zielmaschine wäre sie sonst genau die Annahme, die sie
  ersetzen soll.

  Unter Test: [`test_bl122_native_exitcode.py`](geteilt/tests/test_bl122_native_exitcode.py).
  Gegenprobe gefahren — Pin aus `ralph.ps1` entfernt, Test fällt namentlich;
  wieder eingesetzt, grün. **Der Beweis auf der Zielmaschine steht aus:** Auf
  der Entwicklungsmaschine ist kein `pwsh`, keine dieser Dateien konnte hier
  geparst werden.

## [2.11.0] — 2026-08-20

**Die Bahn-Runde.** Das Repo bekommt seine heutige Ablage: `bash/`, `pwsh/`
und `geteilt/`, jede Datei mit einer Bahn-Kennung in Zeile 1, dazu die Abwahl
einer Bahn samt Rückweg (`BL-107`…`BL-119`). Seit dieser Fassung liegt der
Installer unter `bash/install.sh`.

### Changed

- **Der Launcher außerhalb des Repos kann nicht mehr still verrotten.**
  `~/.claude/scripts/team-init.sh` ist das einzige Stück des Kits, von dem
  eine Fassung außerhalb des Repos liegen kann. Ein Symlink kann nicht
  veralten, eine **Kopie** schon — und sie meldet sich nicht, sondern
  behauptet eines Tages, das Kit sei nicht da. Genau so ist der Umzug auf
  `bash/` aufgefallen: nicht durch eine Warnung, sondern durch einen Launcher,
  der nicht mehr lief.

  Drei Maßnahmen: Der Launcher ist **ablage-tolerant** — er kennt alle Orte,
  an denen ein Installer je lag, und sucht zwei Elternebenen ab; eine Kopie
  beliebigen Alters läuft damit weiter, sie muss nur wissen *wo* das Kit
  liegt, nicht *wie* es innen aufgebaut ist. `install.sh` **meldet** eine
  veraltete Kopie bei jedem Lauf (schreibt aber nichts ins Home-Verzeichnis —
  ein Projekt-Installer, der dort aufräumt, ist eine Überraschung).
  `kit-einrichten.sh --verknuepfen` **repariert** sie jetzt, statt sie nur zu
  melden, mit Sicherung daneben und nur bei erkennbaren Kit-Kopien.

  Geprüft in `kit-test.sh` Stufe 10 an einer Kopie an **fremdem** Ort — der
  Symlink-Fall läuft über den aufgelösten Pfad und würde den Fehler nie
  zeigen — samt der Gegenprobe, dass der aktuelle Launcher die Meldung *nicht*
  auslöst. `A.12.1`.

- **Die Ablage trennt die beiden Bahnen — `bash/`, `pwsh/`, `geteilt/`.**
  ⚠️ **Der Installer heißt jetzt [`bash/install.sh`](bash/install.sh) bzw.
  [`pwsh/install.ps1`](pwsh/install.ps1).** In der Wurzel liegt kein Skript
  mehr; `ls bash/` ist die vollständige Bash-Bahn. Vorher war die Zugehörigkeit
  einer Datei nur an ihrer **Endung** abzulesen: `entry/` listete 29 Dateien
  alphabetisch verschränkt (`axel.cmd`, `axel.ps1`, `axel.sh`, `frank.cmd`, …).

  Drei Dinge sind dabei mehr als Optik geworden: `.gitattributes` hängt am
  **Pfad** statt an der Endung (`pwsh/**/*.cmd text eol=crlf`) — und
  `kit-test.sh` prüft nicht nur, dass die Regel dasteht, sondern per
  `git check-attr`, dass git sie auf einer echten Datei anwendet. Das
  **Gegenstück** einer Datei liegt in der *gespiegelten* Bahn
  (`bash/entry/ralph.sh` ↔ `pwsh/entry/ralph.ps1`) und ist damit über den Pfad
  prüfbar. Und die Übersetzung zwischen Kit-Ablage und Projekt-Ablage steht an
  **einer** Stelle: `kit_pfad()` in
  [`conftest.py`](geteilt/tests/conftest.py).

  **Das Zielprojekt-Layout ändert sich nicht** — Entrypoints flach in der
  Wurzel, alles Aufgerufene unter `team/`. `team-init.sh`/`.ps1` suchen den
  Installer eine Ebene tiefer; der Kurzbefehl unter `~/.claude/scripts/`
  bleibt bedienbar, muss aber **neu verknüpft** werden
  (`bash bash/kit-einrichten.sh --verknuepfen`) — eine alte Kopie zeigt auf
  `<kit>/install.sh` und findet nichts mehr.

  Der Preis stand vorher fest und ist gemessen worden: Die Tests sprachen die
  Kit-Ablage an 105 Stellen direkt an; ohne `kit_pfad()` fielen 281 Fälle um
  und 24 Dateien ließen sich nicht einmal einsammeln. Maßstab war deshalb
  nicht „grün", sondern **Befundgleichheit** — 21 Fehlschläge in der
  Kit-Ablage, Datei für Datei identisch mit dem Stand davor (die Tests setzen
  die installierte Ablage voraus). In der Installation: 431 grün, unverändert.
  `BL-118`.

- **Ein Begriffspaar für die zwei Bahnen: `Bash-Bahn` und `pwsh-Bahn`.** Der
  Schnitt heißt **nicht** „Windows gegen Linux" — wer unter Windows in einer
  WSL-Distro arbeitet, fährt die *Bash*-Bahn, und WSL ist im Feld der
  Normalfall. Die Benennung nach Betriebssystem beschrieb damit ausgerechnet
  den häufigsten Fall falsch. Vorher standen vier Paare nebeneinander
  („Linux/WSL" gegen „Windows nativ" im README, „Bash-Zweig" gegen
  „PowerShell-Zweig" im Bauplan, `feat(windows)` in den Commits, „Bahn" in
  `conftest.py`). Angeglichen wurde an `conftest.py`, wo das Wort bereits
  scharf definiert war. **Weg** bleibt der Installationsweg (Linux · WSL ·
  Windows nativ); Commit-Scopes sind `(bash)`, `(pwsh)`, `(beide)`. Beide
  Befehlstabellen tragen die Korrektur in der Kopfzeile. `A.13`.

### Added

- **`doku/faq.md` — ganze Fragen mit ganzer Antwort.** Die Doku beantwortete
  bisher zwei Sorten Frage: *„wie geht der Weg?"* (`einrichtung.md`) und
  *„was heißt diese Meldung?"* (die Fehlerbilder-Tabelle, eine Zeile je
  Symptom). Eine dritte fiel durch: die Frage, deren Antwort **mehr als eine
  Zeile** braucht, aber kein Bauentscheid ist und darum auch nicht nach
  Anhang A gehört.

  Erste Frage: **„Claude-CLI nicht gefunden — wie installiere ich sie?"** für
  Linux, WSL und Windows nativ. Sie steht hier und nicht in der Tabelle, weil
  die Antwort vier Dinge trennen muss, die im Feld ständig verwechselt
  werden: die **Installationswege** (nativ, Paketverwaltung, npm — mit der
  Entscheidungshilfe, wann welcher), der **PATH**, die **geerbte Umgebung**
  (Terminal, IDE, `cron` — dieselbe Maschine, drei verschiedene PATHs) und
  die **Auth**, die danach immer noch aussteht. Der teuerste Fehlschluss der
  pwsh-Bahn hängt genau an dieser Trennung: Ein nicht auflösbares `claude`
  sieht aus wie ein Auth-Fehler und ist keiner.

  Der Abschnitt trägt einen eigenen **Belegstand**, weil er fremde Befehle
  zitiert: Die Kit-Seite ist verifiziert, der npm-Weg unter Linux ist im
  Betrieb, die native Installation und der apt-Weg sind aus der Herstellerdoku
  **übernommen, nicht durchlaufen**. Fremde Befehle altern schneller als
  dieses Repo — im Zweifel gilt die Herstellerdoku.

  Verlinkt aus `README.md` (Doku-Tabelle und Ablage-Baum) und aus
  `einrichtung.md` an den drei Stellen, an denen die Frage aufschlägt.
  Mitgenommen: ein toter Anker in `einrichtung.md`
  (`#die-einbindung--auf-beiden-plattformen-gleich`), der bei der Umbenennung
  des Abschnitts auf *„auf allen Wegen dieselbe"* zurückgeblieben war.

- **Die Bahn-Kennung — jede Skriptdatei sagt in Zeile 1, wo sie hingehört.**
  48 Dateien tragen `# Bahn: bash | Gegenstueck: ralph.ps1` (in `.cmd`:
  `rem …`). Reines ASCII und `|` statt Geviertstrich, weil dieselbe Zeile in
  einer `.cmd` steht — die liest der Kommandozeileninterpreter in der
  OEM-Codepage (`BL-113`). Ein Suchmuster findet sie damit in jeder Datei:
  `grep -rlE '^(#|rem) Bahn: pwsh' .`

  Damit ist dreierlei greppbar, das vorher nur Absicht war: welche Dateien zu
  welcher Bahn gehören, dass `ralph.sh` ↔ `ralph.ps1` ↔ `ralph.cmd` ein Paar
  sind (die Kopplung, auf der die Doppelbahn-Testbahn ruht — vorher eine
  Absichtserklärung im Bauplan), und welcher Code **geteilt** ist:
  `geteilt/tools/*.py` trägt `Bahn: beide`, denn die pwsh-Bahn ist eine zweite
  *Orchestrierung*, kein zweiter Zustandscode. `keines` braucht einen Grund in
  Klammern — übernommen von `@pytest.mark.nur_bash`, weil eine fehlende und
  eine vergessene Portierung sonst gleich aussehen.

  Durchgesetzt von
  [`geteilt/tests/test_bahn_kopfzeile.py`](geteilt/tests/test_bahn_kopfzeile.py)
  (8 Fälle): Vollständigkeit, Bahn passt zur Endung, Gegenstück existiert und
  liegt auf der anderen Bahn, Paare sind wechselseitig, `keines` trägt einen
  Grund, Kennung ist ASCII. Im Kit **rekursiv** — damit auch jede neue Datei
  erfasst wird; im installierten Projekt nur die Namensliste des Kits, weil
  dort fremder Code liegt. `A.13`.

- **Bahn-Abwahl im Zielprojekt: `--nur-bash` / `--nur-pwsh`** (PowerShell:
  `-NurBash` / `-NurPwsh`). Statt 29 Entrypoints landen nur die zehn der
  gewählten Bahn im Projekt. **Default bleibt beides**, und das ist keine
  Bequemlichkeit: `team.config.sh` und `team.config.ps1` sind zwei Generate
  *einer* Quelle. Wer nur eine Bahn installiert, hat unter dem anderen System
  keine Konfiguration — und schreibt sie irgendwann von Hand. Die Abwahl kommt
  deshalb vom **Anwender**, nie vom Installer. Bewusst kein Ordner-Umzug im
  Zielprojekt: Damit entfällt der `BL-3`-Konflikt vollständig.

  **Der Rückweg ist der eigentliche Inhalt.** Ein `--update` ohne Schalter
  macht das Projekt wieder vollständig. Beim ersten Bau ist genau das
  gescheitert, an der Stelle, die man übersieht: Die Entrypoints kamen zurück,
  die **Konfiguration** nicht — ein Update fasst `team.config.*` grundsätzlich
  nicht an. Richtig, solange sie da ist; fehlt sie, ist „nicht anfassen" kein
  Schutz mehr, sondern eine halbe Bahn. Beide Update-Pfade erzeugen eine
  fehlende Bahn-Konfiguration jetzt neu, aus den Werten der *vorhandenen*.
  Dabei kam ein zweiter Fund heraus: Der Update-Pfad in `install.sh` hat eine
  **eigene** Füll-Routine, die nur 13 der 17 Platzhalter kannte — fürs
  Nachrendern reichte das, fürs Erzeugen nicht.

  In einem einbahnigen Projekt bleiben die Tests **grün**; die fehlende Bahn
  erscheint als sichtbarer Vermerk in der Doppelbahn-Zusammenfassung
  („einbahnige Ablage"), nicht als Fehlschlag und nicht als stiller
  Übersprung. Nachweis: `kit-test.sh` **Stufe 8/11** mit zwölf Zusicherungen
  über Abwahl *und* Rückweg. `BL-119`.

- **BL-112 — ein Test, der meldet, wenn die beiden Zweige verschiedene Agenten
  steuern.** Die Rollen-Briefings sind single-source (`team_briefing` liest
  `team/prompts/rolle-*.md`), der **zusammengesetzte** Prompt war es nicht: Er
  entsteht erst im Einstiegsskript und stand seit der Portierung zweimal im
  Repo — einmal `.sh`, einmal `.ps1`. Wer eine Feldlehre nachschärft und nur
  eine Fassung anfasst, bekommt zwei Zweige, die verschiedene Agenten steuern;
  kein Test schlug an, weil beide Zweige grün laufen.

  [`team/tests/test_bl112_prompt_gleichstand.py`](geteilt/tests/test_bl112_prompt_gleichstand.py)
  zieht den Prompt-Quelltext aus beiden Zweigen, rechnet die Syntax heraus
  (jede Variableneinsetzung wird **ein** Platzhalter) und vergleicht die
  verbleibende Prosa zeichenweise — vier Prompt-Blöcke und fünf
  Prosa-Variablen, darunter `SMOKE_ZEILE` aus der **Bibliothek**, die der
  Befund nicht im Blick hatte. Stand beim Bau: noch keine Drift, alle neun
  Vergleiche zeichengleich.

  Die Ausnahmeliste (genau ein Eintrag: `team.config.sh` ↔ `team.config.ps1`)
  trägt Begründungspflicht und wird selbst bewacht — eine Ausnahme, die keinen
  Vergleich mehr rettet, fällt auf. Ohne das wäre die Liste die Sammelstelle,
  hinter der echte Drift verschwindet. **Nicht** geprüft wird Drift in den
  eingesetzten Werten; das zeigt nur ein Lauf mit beiden Shells auf einer
  Maschine und steht als `BL-117` offen, statt hier behauptet zu werden.

### Fixed

- **Doku-Audit: sechs Stellen nannten Pfade oder Zahlen, die es nicht gibt.**
  Am schwersten wog `doku/einrichtung.md`, Abschnitt *Die Einbindung* — die
  meistbenutzten Befehle des ganzen Dokuments zeigten weiter auf
  `~/Source/team-kit/install.sh`. `bootstrap/TEAM.md` landet in **jedem**
  Zielprojekt und nannte `<kit-pfad>/install.sh` für das Update. Dazu drei
  weitere Aufrufe und die Testzahlen im README (62/369 statt 65/476).

  `bootstrap/TEAM.md` erklärt jetzt außerdem, was eine **fehlende Spalte** in
  der Befehlstabelle bedeutet: Wer mit `--nur-bash` installiert hat, findet
  dort keine `.cmd`-Befehle — kein Defekt, sondern die eigene Abwahl, samt
  dem Befehl, der sie zurücknimmt. `bootstrap/CLAUDE.md.vorlage` führt die
  pwsh-Bahn jetzt in der Dateikarte, `doku/einrichtung.md` den Abwahl-Schalter
  und die neue Reparatur beim Verknüpfen.

  Beide Zahlenpaare werden jetzt **nachgerechnet**: `kit-test.sh` misst
  Dateizahl und Testzahlen an einer frischen Installation und vergleicht sie
  mit dem README. Gegenprobe gefahren.

- **„75 Dateien" stimmte seit Jahren nicht — es sind 117.** Die Zahl stand in
  README (zweimal) und `doku/einrichtung.md`. Eine Zahl, die niemand
  nachrechnet, veraltet lautlos und liest sich trotzdem wie eine Zusicherung.
  `kit-test.sh` Stufe 2 vergleicht sie jetzt mit dem, was der Installer
  tatsächlich schreibt, und fällt bei Abweichung.


- **BL-114 — der Rollback eines Rollenlaufs riss fremde uncommittete Arbeit
  mit, und die Bibliothek verbot sich das zwei Zeilen weiter selbst.**
  `frank.sh`/`frank.ps1` rollten auf **zwei** Pfaden (Session-Limit und
  Fehlversuch) mit unbeschränktem `git reset --hard` + `git clean -fd` zurück;
  `axel` und `redteam` hatten ihren `git clean` zwar eingeschränkt, ihr
  `git reset --hard` daneben aber nicht. Der Kopf des Read-Only-Guards
  beschreibt wörtlich die Gegenregel — *„niemals blanko `git reset --hard`/
  `clean -fd`. (Lektion 2026-07-10: ein blindes reset+clean löschte einmal die
  gesamte uncommittete Team-Infrastruktur. Nie wieder.)"* Die Lehre war am
  **Guard** angewandt und am **Aufrufer** nicht.

  Die chirurgische Schleife des Guards ist jetzt als
  `team_pfade_zuruecksetzen` herausgelöst, darauf sitzt `team_rollback_rolle`,
  und alle sechs Stellen rufen sie auf. HEAD wandert mit `--soft` zurück
  (gestagte fremde Arbeit bleibt unberührt), die Pfade **dieser** Rolle holt
  die Schleife einzeln. Frank bekommt dafür erstmals einen Startschnappschuss
  (`team_guard_begin`) — als schreibende Rolle hatte er keinen und konnte
  fremde Arbeit gar nicht von der eigenen unterscheiden. Reichweite von
  `HM-29` und die Ausnahme für Laufzeitartefakte (`BL-4`/`BL-24`) bleiben.

  **Beim Bauen aufgefallen, und es betraf auch den Guard:** `git status
  --porcelain` meldet einen untracked **Ordner** als EINEN Eintrag (`plans/`).
  Committet eine Rolle eine fremde Datei daraus versehentlich mit, taucht sie
  danach als `plans/closeout.md` auf und passt auf keinen Eintrag der
  Fremdliste mehr — ein reiner Zeichenvergleich hätte sie gelöscht. Der neue
  gemeinsame Filter `team_fremd_ausfiltern` zählt einen Pfad auch dann als
  fremd, wenn er **unter** einem fremden Ordnereintrag liegt.

  Gegenprobe in
  [`team/tests/test_bl114_rollback_verschont_fremde_arbeit.py`](geteilt/tests/test_bl114_rollback_verschont_fremde_arbeit.py)
  (21 Fälle): Schonung **und** Wirksamkeit je Bahn, dazu ein echter
  `frank.sh`-Lauf mit gestubbter CLI. Mit dem alten Rollback verschwindet dort
  `CHANGELOG.md` — genau die Datei aus dem Feldbericht —, mit dem Fix
  überlebt sie. Der ursprüngliche Verlustfall (nach einem **erfolgreichen**
  Lauf) ist damit **nicht** erklärt; sein Mechanismus war nie bewiesen.

- **BL-116 — ein Transkript, zwei Closeouts: der zweite bucht die Summe
  beider Kaskaden.** Der Abo-Messweg misst das Sitzungstranskript. Wer zwei
  Kaskaden in **derselben** Sitzung abschließt, misst beim zweiten Closeout
  wieder das **ganze** Transkript — der bereits gebuchte Teil steckt darin und
  wandert ein zweites Mal ins Ledger. Aus dem Feld zurückgespielt
  (`Feld A`, dortiges `BL-120`).

  **Der Befund ist die Unsichtbarkeit, nicht der Rechenfehler.** Keine
  bestehende Absicherung schlägt an: Die vierte Eigenschaft aus `BL-33` („ein
  Transkript je Aufruf") verbietet, **mehrere** Transkripte zu summieren, und
  sagt nichts über **eines** mit zwei Buchungspunkten; die Deduplikation über
  die Nachrichten-ID greift nicht, weil jede Antwort der ersten Hälfte genau
  einmal vorkommt — nur eben bereits bezahlt; und der A1-Kollisionsschutz
  schlägt bei **derselben Rolle + Kaskade** an, während hier zwei
  Kaskadennummern entstehen, also zwei für sich plausible Zeilen.

  Zuständigkeitslage und Entscheid wie bei `BL-33`: Das Messwerkzeug gehört
  dem Kit nicht, also wird die **Eigenschaft** benannt statt der Datei. A.9
  führt jetzt **fünf** Eigenschaften — neu „(5) Den bereits gebuchten
  Abschnitt ausnehmen", mit einem eigenen Absatz dazu, **warum** sie nicht
  schon in (1)–(4) steckte. Dazu die vermeidende Hälfte im Briefing des
  Architekten, an der Stelle, an der gebucht wird: **„Ein Closeout je
  Sitzung"**, samt Ausweg für den Ausnahmefall (Rohwert minus bereits gebucht,
  Rechnung in den Notiztext). Geprüft nach Träger getrennt: A.9 über das
  Regel-Inventar, das Briefing über
  [`team/tests/test_bl116_ein_closeout_je_sitzung.py`](geteilt/tests/test_bl116_ein_closeout_je_sitzung.py).

- **BL-111 — drei Ableitungen aus der Plan-Datei rissen den Aufrufer unter
  `set -o pipefail` weg, und der Kommentar darüber sagte das Gegenteil zu.**
  `team_architekt_kaskade` beendete seine Pipeline mit `| head -1` und
  begründete das wörtlich damit, ein Projekt ohne erkennbare Kaskade dürfe den
  Aufrufer *„unter set -e nicht wegreissen"*. Das stimmt für `set -e` und ist
  unter `set -o pipefail` wirkungslos: Dort bestimmt der erste fehlschlagende
  Teil den Status, also der leere `grep`. Gemessen: `set -e` → `rc=0`,
  `set -euo pipefail` → **Abbruch**. Alle bauenden und prüfenden Rollen laufen
  mit voller Strenge.

  **Der Umfang war größer als der Befund.** Nachgemessen an allen fünf
  Ableitungen sind **drei** betroffen — neben `team_architekt_kaskade` auch
  `team_ralph_cap` und `team_budget_empfehlung`, gleiche Bauart
  (`grep … | head -1 | cut`). Bei beiden ist der Fall, den sie nicht
  überlebten, der **dokumentierte Normalfall**: eine Plandatei ohne diese
  Zeile. Der Kommentar von `team_budget_empfehlung` sagte sogar „kein
  Abbruch" zu. Alle drei halten ihren Rückgabewert jetzt mit `{ … ; } || true`
  auf 0. Der PowerShell-Zweig war nie betroffen (keine Pipeline).

  Gegenprobe zweifach: `test_bl18_architekt_zeile_beschriftung.py` fährt jetzt
  `strikt=True` statt `strikt="abbruch"`, und
  [`team/tests/test_bl111_ableitungen_unter_pipefail.py`](geteilt/tests/test_bl111_ableitungen_unter_pipefail.py)
  prüft je Funktion **beide** Pfade — leer unter voller Strenge **und** der
  vorhandene Wert, sonst wäre `funktion() { :; }` ein grüner Weg. Mit der
  alten `lib.sh` fallen genau die Leer-Fälle.

- **BL-115 — die Vorlage lehrte eine Statuszeile, die das eigene Werkzeug nicht
  findet, und das Werkzeug meldete den Fehlgriff nicht, sondern stürzte ab.**
  Die Regeldatei schrieb *„Status auf `offen → an Frank übergeben` setzen"*.
  Der Pfeil meint den **Übergang**, liest sich aber als **Feldwert**; von Hand
  abgeschrieben entsteht `- **Status**: offen → an Frank übergeben`. `list`
  zeigt den Fund weiter an, `first 'an Frank übergeben'` findet ihn **nicht**,
  `frank.sh` meldet „nichts zu tun" — und der bezahlte Lauf ist verbraucht,
  ohne dass irgendetwas auf den Widerspruch hinweist. Im Feld an `HM-106` genau
  so passiert.

  Drei Hälften desselben Fehlers, alle drei gefixt: Die Vorlage nennt jetzt den
  **Zielwert** und den Pfeil ausdrücklich als Übergang (die Status-Kette selbst
  bleibt und ist eigens abgesichert). `first`, `dateien`, `reproducer`, `lint`
  und `set` geben bei fehlendem Pflichtargument eine **Nutzungszeile und
  Exit 2** statt eines `IndexError`-Tracebacks — ausgerechnet auf dem Weg, den
  man geht, wenn man gerade prüft, ob ein Fund auffindbar ist. Und
  `beutebuch.py lint` meldet neu eine Statuszeile, die auf **keinen** Wert der
  Kette passt (Exit 3), mit dem richtigen Wert in der Meldung.

  **Der Fund beim Bauen:** Die naheliegende Prüfung wäre stumm grün gewesen.
  `passt()` vergleicht per Präfix, und `offen → an Frank übergeben` **beginnt**
  mit `offen` — der Wächter hätte seinen eigenen Anlassfall durchgelassen.
  Deshalb `status_bekannt()`: exakter Kettenwert oder Wert plus Klammerzusatz
  (`erledigt (Frank-Fix, abc1234)`), sonst nichts. Dieser String steht als
  Gegenprobe im Test —
  [`team/tests/test_bl115_statuszeile_und_nutzungshinweis.py`](geteilt/tests/test_bl115_statuszeile_und_nutzungshinweis.py),
  14 Fälle.

- **BL-113 — der native Windows-Zweig startete auf der Zielmaschine nicht, und
  zwar wegen einer fehlenden Kodierungsangabe.** Beim ersten Kontakt mit einer
  echten Windows-11-Enterprise-VM brach `kit-einrichten.ps1` mit **zehn
  Syntaxfehlern** ab, von denen **keiner echt war**. Windows PowerShell 5.1
  liest eine Datei ohne Byte-Order-Mark nicht als UTF-8, sondern in der
  ANSI-Codepage; der Geviertstrich `—` wird dabei zu `â€"`, und dessen letztes
  Zeichen ist U+201D — für PowerShell eine **gültige Stringgrenze**. Jeder
  Gedankenstrich schließt damit seine Zeichenkette mitten im Satz. Im Zweig
  stehen 443 davon.

  Neu ist deshalb eine Kodierungsregel an **einer** Stelle je Installer
  (`Team-Kodierung` in [install.ps1](pwsh/install.ps1), das `fuelle`-Here-Doc in
  [install.sh](bash/install.sh)): **`.ps1`/`.psm1` mit BOM, alles andere ohne.**
  Die zweite Hälfte ist gleich teuer bezahlt — ein BOM vor einer Shebang-Zeile
  macht aus ihr Zeichensalat, und `json.load` bricht darüber ab, worauf
  `kosten.py` die Datei still als `0.0000` zählt. `.cmd` wurde auf reines
  ASCII gezogen (der Kommandozeileninterpreter liest sie in der **OEM**-
  Codepage, nicht in 1252). Als Nebenertrag erreicht 5.1 jetzt die
  Versionsprüfung und **sagt**, dass `pwsh` gebraucht wird, statt zu zerfallen.

  **Warum keine der bestehenden Prüfungen das finden konnte:** Sie fahren
  alle unter pwsh 7, und pwsh 7 liest UTF-8 ohne BOM überall korrekt. Zum
  Zeitpunkt des Fehlschlags waren `kit-test.sh` (10/10), `kit-test.ps1`
  (15/15), die Doppelbahn (364 bestanden) und der Syntaxcheck über alle
  `.ps1` grün. Die Lehre steckt in der Bauart der neuen Prüfung: Was die
  Zielmaschine anders **liest** statt anders **tut**, prüft man an den Bytes.
  [`team/tests/test_bl113_bom_regel.py`](geteilt/tests/test_bl113_bom_regel.py)
  sieht sich Dateianfänge an, braucht kein PowerShell und greift deshalb auch
  dort, wo der Zweig gar nicht laufen kann; `kit-test.sh` Schritt 10 prüft
  dieselben drei Regeln im Kit, und [.gitattributes](.gitattributes) trägt die
  Begründung neben der CRLF-Regel — weil dort danach gesucht wird.

### Added

- **[`doku/einrichtung.md`](doku/einrichtung.md) beschreibt jetzt DREI Wege**
  statt zwei: Linux, Windows mit WSL und **Windows nativ** (PowerShell, ohne
  WSL). Der neue Abschnitt sagt zuerst, **wann** er der richtige ist — nämlich
  wenn WSL2 ausfällt (VM ohne *nested virtualization*, verwalteter Rechner,
  gesperrte Firmware) — und stellt die vier echten Unterschiede
  gegenüber: kooperatives `flock` gegen die vom Betriebssystem **durchgesetzte**
  `FileShare::None`-Sperre, `/mnt/c` gegen Netzlaufwerk und OneDrive,
  fehlendes Exec-Bit gegen die Ausführungsrichtlinie, `kit-test.sh` gegen
  `kit-test.ps1`. Dazu acht Detailabschnitte, darunter drei Fallen, die alle
  dasselbe Muster haben — sie sehen nach etwas anderem aus, als sie sind:
  ein `claude`, das nicht aufgelöst wird, **sieht aus wie ein Auth-Fehler**;
  ein Store-Platzhalter **trägt den Namen** `python.exe` und ist keiner; ein
  nach OneDrive umgeleitetes Benutzerprofil **fällt im Pfad nicht auf**.
- **Acht neue Fehlerbilder für den nativen Weg** — von der
  Ausführungsrichtlinie über die BOM-Falle bis zur `Set-Location`-Falle
  (PowerShell-Position und Prozess-Arbeitsverzeichnis sind zwei verschiedene
  Dinge). Und im **Belegstand** steht der neue Zweig mit dem Status, den er
  wirklich hat: *gebaut und gefahren, aber nicht auf Windows* — samt
  ausdrücklicher Liste dessen, was unter Linux gar nicht prüfbar ist.
- **Befehlstabellen mit Plattformspalte** in [README.md](README.md) und
  [bootstrap/TEAM.md](bootstrap/TEAM.md). Die Python-Werkzeuge stehen dort
  bewusst als *(gleich)*: Sie werden **nicht** portiert — Ledger, Beutebuch und
  Kostenrechnung liegen auf beiden Wegen in denselben Dateien. Der
  PowerShell-Zweig ist eine zweite **Orchestrierung**, kein zweiter
  Zustandscode.

### Fixed

- **Die Begründung für `bash` ≥ 4 stand falsch in
  [`kit-einrichten.sh`](bash/kit-einrichten.sh) und in der Doku.** Dort hieß es, das
  Kit nutze *durchgehend* indirekte Expansion (`${!var}`). Nachgemessen kommt
  sie in der **Laufzeit** — `team/lib.sh`, `entry/*.sh`, `team/redteam.sh` —
  genau **null** Mal vor; alle sechs Fundstellen liegen im **Installer**. Die
  Anforderung bleibt bestehen, nur mit dem richtigen Grund: Ohne Installer
  kommt niemand zu einer Laufzeit. Keine Kleinigkeit — die alte Formulierung
  hätte jeden, der die Laufzeit portiert oder prüft, an der falschen Stelle
  suchen lassen. (Gefunden beim Vermessen für den Windows-Zweig, Stufe 1.)

### Added (Fortsetzung)

- **Die Rollen laufen unter Windows — der Zweig ist bedienbar.** Zehn
  Einstiege plus die gemeinsame Sweep-Logik, je mit `.cmd`-Shim:
  [`ralph.ps1`](pwsh/entry/ralph.ps1), [`frank.ps1`](pwsh/entry/frank.ps1),
  [`axel.ps1`](pwsh/entry/axel.ps1), [`harry.ps1`](pwsh/entry/harry.ps1),
  [`marv.ps1`](pwsh/entry/marv.ps1), [`vollautomatik.ps1`](pwsh/entry/vollautomatik.ps1),
  [`halbautomatik.ps1`](pwsh/entry/halbautomatik.ps1),
  [`team-status.ps1`](pwsh/entry/team-status.ps1),
  [`team-test.ps1`](pwsh/entry/team-test.ps1),
  [`team/redteam.ps1`](pwsh/redteam.ps1). Die `.cmd`-Dateien sind Einzeiler auf
  die `.ps1` — kein Symlink, denn der braucht unter Windows
  Administratorrechte, und ein Einrichtungsschritt, der an Rechten scheitert,
  hat sein Versprechen gebrochen.
  **Belegt durch einen Trockenlauf der ganzen Kette** (`TEAM_DRY_RUN=1`, keine
  CLI-Kosten): Ralph baut Stufe 1, erhält das Promise, schaltet weiter,
  erreicht `RALPH_CAP`; Harry und Marv sweepen; Frank findet nichts; der
  Abschlussbericht erkennt Kaskade K1, liest Sperr-Status und
  Kostenaufteilung und zitiert die letzten Zeilen des Lauf-Logs.
- **Die BL-3-Invariante wird jetzt auf beiden Bahnen geprüft.** Sie ist die
  Zusicherung, auf der **alle** relativen Werkzeugpfade ruhen — ohne sie hängt
  jede Kostenzahl davon ab, aus welchem Verzeichnis gestartet wurde, und
  `kosten.py` meldet still `0.0000`. Beide Zweige sichern dasselbe zu, nur
  anders geschrieben (`cd "$(dirname "$0")"` bzw. `Set-Location $PSScriptRoot`).
  Die Zuordnung steht in `Schale.wechsel_ins_skriptverzeichnis`, **nicht** im
  Test: Sonst führte jede der 24 statischen Quelltextprüfungen ihre eigene
  Übersetzungstabelle, und die erste vergessene wäre eine stille Lücke im
  Windows-Zweig.

### Fixed (Windows-Zweig)

- **`team/redteam.ps1` wurde von KEINEM der beiden Installer kopiert.** Beide
  kannten unter `team/` nur `.sh` und `.psm1`; die Rollen starteten mit *„term
  './team/redteam.ps1' is not recognized"*. Bemerkenswert daran: Die
  Gleichstandsprüfung aus Schritt 10/10 sieht so etwas **nicht** — beide
  Installer waren gleich falsch, die Bäume also identisch. Gefunden hat es der
  Trockenlauf, und genau dafür steht er im Plan.
- **Eine PowerShell-Falle im Formatoperator, fünfmal.** In
  `[Console]::Out.WriteLine('{0} {1}' -f $a, $b)` ist das Komma der
  **Argumenttrenner der Methode**, nicht der Array-Operator: Der Ausdruck wird
  zu `WriteLine(('{0} {1}' -f $a), $b)`, und `-f` bekommt ein Argument für zwei
  Platzhalter. Das fällt erst zur Laufzeit auf, mitten im Statusbericht, und
  sieht aus wie ein Datenfehler statt wie ein Syntaxproblem.

### Added (Fortsetzung)

- **Der Kern des Windows-Zweigs — [`team/lib.psm1`](pwsh/lib.psm1), und die 28
  schlafenden Tests wachen auf.** Alle 42 Funktionen aus
  [`team/lib.sh`](bash/lib.sh) sind portiert: Werkzeug-Hüllen, Sperre, Auth,
  `team_claude` samt Abo→API-Fallback und 429-Logik, die sieben `team_guard_*`,
  Promise, Quittung, Bewertung. Die Funktionsnamen bleiben **zeichengleich**
  (`team_guard_verify`, nicht `Verify-TeamGuard`) — PowerShell warnt darüber bei
  jedem Import, und die Warnung wird abgestellt statt der Name geändert: Die
  Namensgleichheit ist es, was **eine** Testsuite für beide Bahnen möglich
  macht. Ergebnis: `pytest team/tests` meldet ohne `pwsh` 332 passed, mit
  `pwsh` **363 passed** — die Differenz von 31 sind exakt die bis dahin
  übersprungenen Varianten, bei **unveränderten** 21 erwarteten Fehlschlägen.
  Damit laufen auch die fünf Guard-Tests aus `BL-24` auf beiden Bahnen und
  weisen dort einen echten chirurgischen Rollback nach.
- **Die 13 eingebetteten `python3 -c`-Blöcke entfallen ersatzlos.**
  `ConvertFrom-Json`, `[regex]` und `[DateTimeOffset]` ersetzen sie; in
  `lib.psm1` kommt `python3 -c` nur noch in zwei Kommentaren vor. Und
  `team_lock` nimmt eine vom Betriebssystem **durchgesetzte** Sperre
  (`FileShare::None`) statt des kooperativen `flock` — über zwei echte Prozesse
  geprüft: Elternprozess sperrt, Kindprozess wird abgewiesen, nach `team_unlock`
  bekommt das Kind die Sperre.

### Fixed

- **Die Kodierung der Kostenlogs hing an einer PowerShell-Voreinstellung — und
  ihr Bruch wäre still gewesen.** Der naheliegende Weg `& claude … > $Out`
  schreibt mit der Standardkodierung der Sitzung: unter pwsh 7 heute UTF8NoBOM,
  unter Windows PowerShell 5.1 UTF-16LE, und ein `$PSDefaultParameterValues` im
  Benutzerprofil kann es jederzeit umstellen. Python bricht an einem BOM ab —
  aber [`team/tools/kosten.py`](geteilt/tools/kosten.py) **fängt das ab und zählt
  die Datei still als `0.0000`**. Das ist exakt die Fehlerklasse aus `BL-46`
  (Log von 0 Byte nach 47 Minuten Laufzeit) und `BL-55` (Pro-Stufe-Cap
  umgehbar): Eine bezahlte Stufe erscheint als die **billigste** der Kaskade,
  der Deckel bekommt auf sie keinen Griff, und auffallen würde es erst, wenn
  jemand die Kostentabelle als Vergleichsband liest. `Team-ClaudeSchreiben`
  legt die Kodierung jetzt ausdrücklich fest;
  [`test_stufe3_kostenlog_kodierung.py`](geteilt/tests/test_stufe3_kostenlog_kodierung.py)
  pinnt sie auf beiden Bahnen, inklusive Umlaut-Rundlauf — reines ASCII sähe in
  UTF-8 und Latin-1 gleich aus und bewiese nichts.
- **`install.sh` kannte den PowerShell-Kern nicht.** Sie kopiert `team/lib.sh`
  und `team/redteam.sh` namentlich; `team/lib.psm1` wäre durch das Raster
  gefallen, und ein Projekt liefe nach `--update` auf einer Hälfte veraltet
  weiter. Gefunden von der Gleichstandsprüfung in `kit-test.sh` (10/10) —
  genau dafür ist sie da.

### Changed

- **`kit-test.sh` braucht mit `pwsh` auf dem PATH rund 11 Minuten statt gut
  vier.** Die eingebetteten pytest-Läufe fahren jetzt beide Bahnen. Das ist der
  Preis der Doppelbahn und kein Fehler — aber er gehört genannt, damit niemand
  einen Hänger vermutet.

### Added (Fortsetzung)

- **Der Bootstrap des Windows-Zweigs — und der Nachweis, dass beide Installer
  dasselbe tun.** Neu sind [`install.ps1`](pwsh/install.ps1),
  [`kit-einrichten.ps1`](pwsh/kit-einrichten.ps1),
  [`scripts/team-auth-setup.ps1`](pwsh/scripts/team-auth-setup.ps1),
  [`scripts/team-init.ps1`](pwsh/scripts/team-init.ps1) und die Konfigurationsvorlage
  [`entry/team.config.ps1`](pwsh/entry/team.config.ps1). Ohne sie ließe sich das Kit
  auf einer Windows-Maschine ohne WSL gar nicht erst einrichten — deshalb steht
  der Bootstrap **vor** dem Kern und nicht danach.
  **Die Zusicherung ist nicht „beide funktionieren", sondern „beide tun
  dasselbe":** `install.sh` und `install.ps1` erzeugen aus denselben neun
  Antworten **byte-identische Bäume** (155 Dateien, `diff -r` ohne Ausgabe).
  Festgenagelt in [`kit-test.sh`](bash/kit-test.sh) als Schritt 10/10 — ein
  Vergleich statt einer Liste von Einzelprüfungen, denn eine Liste prüft nur,
  woran jemand gedacht hat. Fehlt `pwsh`, sagt der Schritt **laut**, dass die
  halbe Zusicherung des Windows-Zweigs hier ungeprüft blieb; ein
  übersprungener Nachweis, den niemand sieht, liest sich am Ende wie ein
  bestandener.
- **`team.config.sh` und `team.config.ps1` sind zwei Generate einer Quelle.**
  Beide Installer schreiben **beide** Konfigurationen — auch `install.sh` unter
  Linux, wo die PowerShell-Fassung niemand braucht. Der Grund ist die
  Driftfreiheit: Schriebe nur `install.ps1` die `.ps1`-Fassung, hätte ein auf
  Linux eingerichtetes Projekt unter Windows keine Konfiguration, und jemand
  schriebe sie von Hand. Genau dort fängt Drift an. Belegt ist außerdem, dass
  die Zweige einander **updaten** können: `install.ps1 -Update` gegen eine mit
  `install.sh` erzeugte Installation ersetzte 78 Infrastruktur-Dateien und ließ
  Ledger, Kaskadenstand und den von Hand eingetragenen Smoke-Test unberührt.
- **Drei Stellen, an denen der Windows-Zweig strenger ist als der Bash-Zweig.**
  Die Platzhalter-Ersetzung braucht kein eingebettetes `python3`-Here-Doc mehr,
  sondern .NET-Bordmittel. Die Sperrprüfung vor einem Update ist eine vom
  Betriebssystem **durchgesetzte** Sperre (`FileShare::None`) statt des
  kooperativen `flock`, und `kit-einrichten.ps1` probt sie mit **zwei
  Prozessen** statt mit einem. Und der API-Key wird nicht mit `chmod 600`
  geschützt — das läuft unter Windows ohne Fehler durch und bewirkt **nichts**,
  der Schlüssel läge danach lesbar da, mit einem grünen Haken daneben —,
  sondern über eine ACL, die anschließend **nachgeprüft** wird.
  Umgekehrt ausdrücklich benannt: Der Selbsttest von `install.ps1` kann die
  `.sh`-Entrypoints nicht syntaktisch prüfen, weil unter Windows keine `bash`
  vorliegt. Er sagt das, statt Vollzug zu melden.
- **Die Doppelbahn: eine Testsuite, zwei Shells.** Das Kit bekommt einen
  nativen Windows-Zweig in PowerShell, während Bash die Linux-Implementierung
  bleibt ([`plans/windows-nativ.md`](plans/windows-nativ.md)). Der nahe
  liegende Weg wäre eine zweite Testsuite gewesen — und das wäre der eine
  Fehler, der das Vorhaben zum Scheitern bringt: Zwei Suiten driften genauso
  wie zwei Implementierungen, nur unbemerkt. Neu ist deshalb
  [`team/tests/conftest.py`](geteilt/tests/conftest.py) mit der `Schale`: Ein
  Test formuliert nur noch **Schritte**, und wie ein Schritt in der jeweiligen
  Shell ausgesprochen wird, weiß allein der Harnisch. Damit wird eine künftige
  Feldlehre auf der anderen Bahn **automatisch rot**, bis sie nachgezogen ist
  — Drift ist nicht verboten, sondern sichtbar. Sechs Tests (`BL-18`, `BL-24`,
  `BL-28`, `BL-32`, `BL-41`, `HM-32`) tragen keine Shell-Syntax mehr im
  Testkörper. Die Schritte einer Folge bleiben dabei in **einem** Prozess,
  weil `team_guard_begin` seinen Schnappschuss in einer Shell-Variablen
  ablegt: Ein `verify` im zweiten Prozess sähe einen leeren Schnappschuss und
  spräche jede Rolle frei — grün und wertlos. Der Kopf der Datei legt zugleich
  die **Aufrufkonvention** für den PowerShell-Zweig fest (sieben Punkte),
  damit Stufe 3 nicht gegen einen unausgesprochenen Vertrag baut.
- **Die Doppelbahn-Quote steht in jedem Testlauf.** Gleichwertigkeit lässt
  sich nicht zusichern, ohne sie zu messen, und eine Schwelle („ab fünf
  Ausnahmen gilt der Zweig als abgehängt") wäre willkürlich und sofort
  verhandelbar. Der Bericht nennt stattdessen, wie viele Tests auf beiden
  Bahnen liefen, wie viele die pwsh-Bahn übersprangen und wie viele bewusst
  mit `@pytest.mark.nur_bash` geführt werden. Jede Markierung braucht eine
  Begründung und gehört zusätzlich in den Backlog.
- **[`pruefe-windows.ps1`](pwsh/pruefe-windows.ps1)** — die Vorflug-Probe für den
  nativen Zweig, **eigenständig** und ohne jede Kit-Abhängigkeit, damit sie
  einzeln auf die Zielmaschine kopiert werden kann. Sie beantwortet, was der
  Bauplan bisher nur annimmt: ob PowerShell die Agenten-CLI findet und startet
  (unter Windows ein `.cmd`-Shim — schlägt das fehl, **sieht das aus wie ein
  Auth-Fehler und ist keiner**), ob `[System.IO.FileStream]` mit
  `FileShare::None` über Prozessgrenzen sperrt (der Ersatz für `flock`,
  geprüft mit einer Zwei-Prozess-Gegenprobe statt mit einer Erwartung), und
  wie die Auth-Lage aussieht. Der Standardlauf **kostet nichts**; die
  abschließende Antwort auf die Abo-Frage braucht `-MitEchtemAufruf` und sagt
  das vorher. Erfolgskriterium ist der Exit-Code, nicht die Schlusszeile.
- **Klonen und Einbinden ist jetzt eine Routine — für Linux und für Windows
  mit WSL.** Bis hierher begann jede Anleitung in dem Zustand, in dem die
  Autorenmaschine ohnehin war. Neu ist [`kit-einrichten.sh`](bash/kit-einrichten.sh):
  die Vorflug-Prüfung zwischen `git clone` und `install.sh`. Fünf Abschnitte —
  Umgebung (Linux/WSL1/WSL2), Bordmittel (`bash` ≥ 4, `git`, `python3` ≥ 3.8,
  `flock` als Fehler; `pytest` und die Agenten-CLI als Hinweis), Lage des
  Klons, Auth, Kurzbefehl — und am Ende die Übergabe an `install.sh`, wenn ein
  Zielpfad genannt wurde. Es ruft **keine** Agenten-CLI auf und kostet nichts.
  Der Bauentscheid dahinter: **proben statt voraussetzen.** Das Skript schließt
  nicht aus dem Pfad auf die Rechte, sondern legt eine temporäre Datei an,
  ruft `chmod +x` auf und prüft, ob das Bit hält — danach `flock -n` auf
  dieselbe Datei. Dieselbe Haltung wie A.5: Die Heuristik erklärt den
  Regelfall, die Probe entscheidet den Einzelfall.
- **[`doku/einrichtung.md`](doku/einrichtung.md)** — die Routine ausgeschrieben:
  kurzer Weg je Plattform, Bordmittel je Distribution, WSL-Besonderheiten,
  IDE-Beispiele (**VS Codium** unter Linux, **VS Code + WSL-Erweiterung** unter
  Windows — der Grund ist die Lizenz der Remote-Erweiterungen, nicht der
  Geschmack), Auth, Einbindung, Gegenprobe, elf Fehlerbilder mit Ursache und
  Abhilfe, und ein Abschnitt **Belegstand**. Vorangestellt ist die Tabelle
  *Was Pflicht ist und was Beispiel*: Pflicht sind `bash`/`git`/`python3`/
  `flock`; IDE, Agenten-CLI und Modell sind Beispiele mit benanntem
  Tauschpunkt. Eigener Unterabschnitt für den Fall **„nur WSL 1 möglich"**
  (VM ohne nested virtualization, gesperrte Firmware): erst der Schalter am
  Hypervisor je Produkt, dann — weil die eingebaute Sperrprobe einprozessig ist
  und auf einer Syscall-Übersetzung nur die schwächere Aussage trifft — eine
  **Zwei-Prozess-Gegenprobe für `flock`**, und die Regeln, die dort strenger
  gelten (`/mnt/c` doppelt verboten, obwohl WSL 1 dort *schneller* ist).
- **[`scripts/`](bash/scripts/) — die Maschinen-Skripte liegen jetzt im Repo.**
  README, `install.sh` und `TEAM.md` verwiesen auf
  `~/.claude/scripts/team-auth-setup.sh`, eine Datei, die es nur auf der
  Autorenmaschine gab: **Wer das öffentliche Repo klonte, bekam eine Anleitung,
  deren erster Schritt ins Leere zeigte.** Neu ausgeliefert werden
  `scripts/team-auth-setup.sh` und `scripts/team-init.sh`;
  `kit-einrichten.sh --verknuepfen` legt dafür unter `~/.claude/scripts/` einen
  **Symlink** an, nie eine Kopie (eine zweite Kopie läuft dem Kit unbemerkt
  hinterher), und rührt eine dort vorhandene echte Datei nicht an, sondern
  meldet sie.
- **[`.gitattributes`](.gitattributes)** mit `* text=auto eol=lf`. Git for
  Windows klont per Default mit `core.autocrlf=true`; der Shebang wird dann zu
  `#!/usr/bin/env bash\r` und bash meldet `bad interpreter` — ein Fehlerbild,
  das nach einer kaputten Installation aussieht und keines ist. Damit ist der
  Fall nicht mehr dokumentiert, sondern erledigt. Die CRLF-Prüfung in
  `kit-einrichten.sh` bleibt trotzdem: für Klone, die älter sind als die Datei.
- **`kit-test.sh`: neuer Schritt 9/9 — Einrichtungsroutine.** Die Routine steht
  **vor** `install.sh`; wer sie kaputt ausliefert, blockiert den Einstieg,
  bevor die Schritte 1–8 überhaupt greifen. Geprüft werden Syntax aller neuen
  Skripte, ein Durchlauf mit `--nur-pruefen` (Exit 0, nichts angefasst, keine
  Probendatei zurückgelassen), die Ablehnung eines Zielpfads ohne Git samt
  genanntem Ausweg, der Launcher **über einen Symlink**, der LF-Riegel in
  `.gitattributes` und dass die README nicht mehr auf den Pfad der
  Autorenmaschine zeigt. Beim ersten Lauf fiel der Schritt selbst durch: Das
  „Verzeichnis ohne Git" lag im Wegwerf-Repo und war damit sehr wohl in einem
  Arbeitsbaum — der Test hätte eine Ablehnung als ausbleibend geprüft, die
  nicht ausbleiben darf.
- **[`doku/anhang-a.md`](doku/anhang-a.md), A.12** — die Warum-Schicht dazu:
  die Lücke, die der fremde Klon aufdeckte, die drei WSL-Fallen mit ihrem
  gemeinsamen Muster („sieht aus wie ein kaputtes Kit und ist keines"), der
  Entscheid für Proben statt Annahmen und der Belegstand.

### Removed

- **`doku/release-vorlage.md` entfernt.** Das Kit veröffentlicht keine
  GitHub-Releases; ausgeliefert wird der **Quellstand**, und der Weg dorthin
  ist `git clone` (siehe [doku/einrichtung.md](doku/einrichtung.md)). Eine
  Vorlage für eine Seite, die niemand füllt, ist genau die Sorte Dokument, die
  später als geltender Prozess gelesen wird. `CHANGELOG.md` bleibt der Ort, an
  dem eine Änderung samt Begründung nachschlagbar ist — daran ändert sich
  nichts. Mitgezogen: Die README nennt `kit-test.sh` jetzt „DAS Gate vor jedem
  **Push**" statt „vor jedem Release", ebenso die Skizze in
  [plans/roadmap-skizzen.md](plans/roadmap-skizzen.md).

### Changed

- **README: Gliederung mit Inhaltsverzeichnis.** Die Seite ist auf 400 Zeilen
  gewachsen und hatte keinen Einstieg — neu ist ein Abschnitt **Inhalt** direkt
  unter dem Kopf: ein Verweiskasten auf
  [doku/einrichtung.md](doku/einrichtung.md) für alle, die das Kit zum ersten
  Mal auf eine Maschine holen, eine Tabelle der zehn Abschnitte dieser Seite,
  und eine Tabelle **Die Dokumentation** — welche Datei in `doku/` für wen
  gedacht ist, samt der Feststellung, dass `doku/` im Kit bleibt und `TEAM.md`
  die Anleitung im Zielprojekt ist.
- **README**: Der Einstieg beginnt jetzt beim `git clone` und führt über
  `kit-einrichten.sh`; die Auth-Voraussetzung zeigt auf `scripts/`, der Baum
  unter *Aufbau des Kits* führt `scripts/`, `kit-einrichten.sh` und
  `doku/einrichtung.md`. `install.sh` nennt im Auth-Hinweis den Pfad im Kit
  statt den auf der Autorenmaschine.

> **Belegstand dieses Eintrags:** Der Linux-Weg ist auf der
> Entwicklungsmaschine durchlaufen. Der WSL-Weg ist **hergeleitet, nicht
> durchlaufen** — die Regeln folgen aus den bekannten Eigenschaften von DrvFs
> und Git for Windows; die Proben melden den Fall an der Maschine. Ein
> vollständiger Durchlauf unter Windows steht aus.

## [2.10.0] — 2026-08-16

**Der Loop hält nicht mehr an, wo er neunmal dasselbe gehört hat.** Der vierte
`BL-41`-Ausgang — Log meldet Erfolg, Quittung fehlt — ist im Feld in neun
Kaskaden aufgetreten und jedes Mal gleich ausgegangen; er prüft sich jetzt
selbst, streng und in beide Richtungen. Dazu zwei Feldfunde am Rand des
Betriebs: ein Kit-Test, der am Füllstand des Beutebuchs hing, und ein
`.gitignore`, das der Installer für vollständig hielt, weil es den Block
*überhaupt* trug. Damit ist der Backlog des Kits wieder leer. Dazu eine
Festlegung, die bisher nur im Kopf des Autors stand: **Modellagnostik mit
benanntem Anspruch** — das Kit kennt keine Modellnamen, sondern zwei Stufen und
sechs vorausgesetzte Fähigkeiten; das Fernziel sind bezahlbare lokale Modelle,
eingewechselt von unten nach oben.

### Added

- **Der vierte Ausgang prüft sich selbst** (`BL-110`, schließt `BL-108` mit).
  Fehlt die Quittung, während das Log sich selbst für erfolgreich erklärt
  (`BL-41`), fährt `team_quittung_selbstpruefung` die Prüfliste jetzt selbst,
  statt den Lauf anzuhalten und einen Menschen dieselben drei Schritte gehen zu
  lassen. Im Feld ist der Fall in **neun** Kaskaden aufgetreten und **jedes
  Mal** gleich ausgegangen: Arbeit fertig, nur die Quittung fehlt.
  Drei Bedingungen im UND, im Zweifel „nicht bestanden": Arbeit vorhanden,
  **mindestens eine Datei unter `TEAM_TEST_ORDNER` berührt** (die Blindstelle,
  die Commit und grüner Baum nicht sehen — `BL-108`), Smoke-Test grün. Ein
  gesprengter Soft-Cap schließt die Automatik aus; abschaltbar über
  `TEAM_QUITTUNG_AUTO=0`. Uncommittete Arbeit wird dabei gesichert, sonst liefe
  die nächste Stufe auf schmutzigem Baum.

### Changed

- **Die Modellhaltung des Kits steht jetzt in den Dokus — als Agnostik mit
  benanntem Anspruch.** Bisher stand nirgends, warum die Rollen zwei Stufen
  ansprechen (`TEAM_MODEL_LOOP`, `TEAM_MODEL_STRONG`) statt Modellnamen, und
  „Opus" tauchte in der Anleitung wie eine Voraussetzung auf. Neu und
  gleichlautend in [README.md](README.md) (Abschnitt **Modelle**),
  [bootstrap/TEAM.md](bootstrap/TEAM.md) (*Welches Modell arbeitet wo*),
  [entry/team.config.sh](bash/entry/team.config.sh) (kommentierter Block an der
  Stelle, wo man es verstellt) und [doku/anhang-a.md](doku/anhang-a.md) (**A.11**,
  die Warum-Schicht): Das Kit bindet sich an **kein** Modell und keinen
  Anbieter; `sonnet`/`opus` sind Defaults, keine Voraussetzung. Vorausgesetzt
  werden **sechs Fähigkeiten** — große Regeldatei tragen, Werkzeuge zuverlässig
  aufrufen, das `<promise>`-Protokoll bis zum Ende durchhalten, unerzwungene
  Auflagen einhalten, ohne Rückfragen headless arbeiten, eine Stufe samt Tests
  zu Ende bringen —, und das Niveau, auf dem sie heute nachweislich reichen,
  ist Sonnet/Opus. **Langfristig lokal:** Sobald bezahlbare Open-Weights-Modelle
  diese Fähigkeiten halten, werden sie **von unten nach oben** Standard — erst
  die schwache Stufe (Masse der Aufrufe, billiger Irrtum), dann die starke.
  A.11 benennt dazu drei Dinge ehrlich: Das Kit ist modellagnostisch, aber
  **nicht CLI-agnostisch** (`team_claude()` ist die einzige Aufrufstelle, an ihr
  hängen Ergebnis-JSON, Auth-Fallback und 429-Behandlung); der Guard wird durch
  einen Modellwechsel **wichtiger**, nicht unwichtiger; und die Kostenmechanik
  misst USD — im lokalen Betrieb wäre sie strukturell null und damit eine
  Kennzahl, die zum Wegsehen erzieht (`BL-9`/`BL-14`-Falle). Ein Lauf mit einem
  lokalen Modell ist **nicht** belegt: Ziel, nicht Zustand.

### Fixed

- **`install.sh --update` zog ein gewachsenes `.gitignore` nie nach**
  (`BL-109`). Der Update-Pfad sah die Datei gar nicht an, und die
  Erstinstallation prüfte nur, ob der Block **überhaupt** dasteht — nicht, ob
  er vollständig ist. Ein Projekt, das früh installiert und seither brav
  `--update` gefahren ist, blieb damit dauerhaft auf dem Fragmentstand seines
  Installationstages, während der Installer Erfolg meldete. Im Feld
  (Feld A) fehlten so `.team-focus-harry` und `.team-focus-marv`: beide
  standen nach **jedem** Sweep als untracked im Baum, sahen im Closeout wie
  unfertige Arbeit aus, und ein unachtsames `git add -A` hätte einen
  Fokus-String verewigt, der für genau einen Lauf galt. Beide Pfade vergleichen
  jetzt **Zeile für Zeile** gegen `bootstrap/gitignore.fragment` und melden die
  fehlenden namentlich, samt kopierbarem Nachtrag-Befehl. **Ergänzt wird
  nichts** — eine fehlende Zeile kann eine bewusst entfernte sein, und
  `--update` fasst Projektdateien grundsätzlich nicht an. Der stille Fall ist
  der teure; die Meldung ist die risikofreie Hälfte.

- **`test_bl47_sweep_ergebnis.py` hing an einem leeren Beutebuch** (`BL-62`).
  Die Gegenproben hängten Funde mit **fest verdrahteten** Nummern an, während
  `_fixture()` das echte Beutebuch des Zielprojekts hereinkopiert und
  `redteam.sh` neue Funde über `next-id` vorher/nachher zählt. Ein `HM-1`, den
  es dort längst gibt, erhöht die nächste freie Nummer nicht — der Sweep meldet
  korrekt „keine neuen Funde", und der Test fällt um, obwohl die Mechanik
  stimmt. Die Nummer kommt jetzt aus dem kopierten Beutebuch. Im Feld
  (Feld A, Beutebuch bis `HM-100`) sind daran zwei Gegenproben unmittelbar
  nach einem Kit-Update rot geworden.

## [2.9.0] — 2026-08-14

**Der Backlog ist abgearbeitet.** 26 offene Rückmeldungen aus dem Feld —
`BL-20`…`BL-61` — von drei Buchungsverlusten am Kostenwerkzeug über einen
Guard-Rollback, der Vollzug meldete, den er nicht leisten konnte, bis zu zwölf
Betriebslehren, die nirgends standen. Vier Funde wurden **beim Bauen** entdeckt
und mit behoben; zwei davon hätte der jeweilige Fix selbst verursacht.

### Fixed

- **Drei Buchungsverluste am selben Werkzeug.** `akteur-abschluss` ersetzte
  still, wo `rollen-abschluss` seit `BL-5` abbricht (`BL-25`, im Feld 5,5515
  USD spurlos verloren); die Wrapper verschluckten Schalter, sodass `--kaskade`
  nie ankam und auf die Kaskade aus `.ralph-plan` gebucht wurde (`BL-26`, eine
  abgeschlossene Zeile über 8,4678 USD ersetzt); **ein** Notiztext beschriftete
  **zwei** Ledger-Zeilen (`BL-34`, zweimal im Feld die Arbeit des Red Teams
  über Ralphs Baustufen).
- **Der Wächter sah die vergessene Buchung nicht** (`BL-27`): `ledger-pruefen`
  wischte jede Kaskade ohne Rollenzeile als „geplant" weg — 33,89 USD lagen
  ungebucht in den Logordnern, gemeldet wurden null Warnungen. Das tragende
  Merkmal ist das **Alter** der Logs, nicht ihre Anwesenheit: Während eines
  laufenden Baus sind offene Logs der Normalzustand. Dieselbe Mechanik meldet
  beim Buchen Logs, die aus der Zeit **zwischen** zwei Kaskaden stammen
  (`BL-45`).
- **Der chirurgische Rollback konnte keine Verzeichnisse entfernen** (`BL-24`)
  und druckte den Vollzug elf Zeilen vor dem Aufräumen. Jetzt `rm -rf` mit
  Plausibilitätsprüfung, Erfolgskontrolle und Meldung **danach**.
- **Ein quittierter Fund ohne wirksamen Regressionstest** (`BL-22`/`BL-28`):
  Der Substanz-Anker bestand, sobald irgendeine im Fundblock genannte Datei im
  Diff lag — meist die Produktivdatei. Geprüft wird jetzt die reservierte
  Reproducer-Datei; `xfail` verlangt `strict=True`, und Franks Dreisatz beginnt
  mit der Gegenprobe „ohne den Fix muss der Test rot sein".
- **Der Fundblock wird geprüft, bevor er Geld kostet** (`BL-29`):
  `beutebuch.py lint` vor dem ersten Frank-Aufruf, Exit 3 statt Fehlversuch —
  ein unbrauchbarer Auftrag ist kein Versagen des Ausführenden.
- **Der Deckel vernichtete die Quittung statt der Arbeit** (`BL-30`): Ein
  nachweislich erfolgreicher read-only-Sweep behält seinen Zustandszeiger.
- **Der Cap verdeckte die `BL-41`-Erkennung** (`BL-60`): Eine Stufe, die beides
  tat, meldete sich als generischer Fehler. Die Reihenfolge der **Meldung** ist
  gedreht, der Effekt des Caps unverändert. Dazu der dritte Ausgang in der
  Prüfanleitung (`BL-61`): Rot **nur** in den neu angelegten Testdateien der
  Stufe heißt defekter Testaufbau, nicht kaputter Produktivcode — ein Neubau
  hätte im Feld 330 Zeilen korrekte Arbeit weggeworfen.
- **Der Budget-Stopp stoppte im teuersten Moment** (`BL-23`): Kulanzband von
  15 % für eine angefangene Fixrunde, **einmal**; jeder Abbruch druckt jetzt
  die offenen Funde und den Fortsetzungsbefehl.

### Changed

- **Die Red-Team-Aufträge behaupten keinen Stack mehr** (`BL-20`). Der
  ausgelieferte Default beschrieb eine statische Website — in jedem anderen
  Projekt eine **sachlich falsche** Behauptung, die das Modell übernimmt.
  Projektseitig übersteuerbar über `TEAM_REDTEAM_AUFTRAG_HARRY`/`_MARV`.
  Marvs Auftrag fragt zusätzlich, **was der gewöhnliche Pfad kostet** (`BL-21`,
  mit Schwelle: asymptotisch, kein Feintuning).
- **Der Red-Team-Fokus hat ein Verfallsdatum** (`BL-31`): an den Stand
  gebunden, nicht an die Prozessumgebung. Dazu seine **Bauform** — „welche
  bestehenden Verträge berührt das Neue?" (`BL-43`) — und die Auflage, dass
  Prüfpunkte in den **String** gehören, nicht in die Übergabenachricht
  (`BL-44`). Zwei neue Fragen in jedem Sweep-Prompt: Kontrollfluss statt
  Rumpfvergleich und die Durchzählung mitbenutzter Bedingungen (`BL-39`).
- **`A2 / 1,25` gilt nur für schreiblastige Sitzungen** (`BL-32`); reine
  Dateirotation zählt nicht mehr als Churn. Die A1-Regel nennt die vier
  Eigenschaften eines tauglichen Abo-Messwegs, statt ein Werkzeug zu nennen,
  das dem Kit nicht gehört (`BL-33`).
- **Zwölf Feld-Betriebslehren** in `doku/anhang-a.md` (`BL-35`…`BL-38`), die
  planwirksamen zusätzlich im Architekten-Briefing.

### Added

- **`./team-status.sh --altlast [N]`** (`BL-40`) — Produktivdateien ohne Diff
  seit N Kaskaden. Nur eine Kennzahl: Die Diff-Bindung ist der Grund, warum die
  Sweeps bezahlbar sind.
- **`kosten.py turns`** (`BL-37`) — das Turn-Profil stand in jedem Log und
  wurde nie ausgewertet. `vollautomatik.sh` druckt es im Abschlussbericht.
- **`team/tools/zitat_lint.py`** (`BL-50`, Stufe 2) — meldet Plandateien, die
  einen erledigten Backlog-Eintrag noch als offene Frage zitieren. Bewusst
  schmal: Der erste Anlauf fiel prompt in die eigene Falle und meldete drei
  Rückblicke im Roadmap-Dokument des Kits.
- **`plans/backlog-archiv.md`** (`BL-53`) — 58 abgetragene Einträge, wörtlich.
  Der aktive Backlog schrumpft von 154 KB auf 6 KB.

### Beim Bauen gefunden

- **`kit-test.sh` gab bei rotem Testlauf Exit 0 zurück** (`BL-59`) — `RC=$?` im
  `then`-Zweig eines `if ! cmd`. Rot für den Menschen, grün für jede Automatik.
- **Der scharfgestellte Guard-Rollback hätte die Kostenlogs des laufenden
  Aufrufs gelöscht** — `.team-logs/` ist ein untracked Verzeichnis außerhalb
  jeder Whitelist. `TEAM_GUARD_LAUFZEIT` nimmt die Artefakte der Shell aus der
  Bewertung.
- **Die `BL-27`-Prüfung hätte bei jedem `--budget` mitten im Lauf rot
  gemeldet** — `test_bl13` fing es beim Bauen ab und erzwang das richtige
  Merkmal.
- **`BL-42` und `BL-58` waren derselbe Fund**, zweimal aus demselben
  Feldprojekt gemeldet: Der erste Bericht blieb liegen, `--update` überschrieb
  den Feldfix, das Feld musste ihn erneut melden.

## [2.8.1] — 2026-08-14

**Ein Kit-Test, der nur dort scheitern kann, wo niemand hinsieht, ist keine
Zusicherung.** Aus dem Feldprojekt kam zurück, dass `test_zentrale_defaults`
den Soft-Cap per `source team/lib.sh` las — und `lib.sh` sourct in ihren ersten
Zeilen die `team.config.sh` des Projekts. Der Test maß damit den *Projektwert*
und behauptete, den *Bibliotheks-Default* zu prüfen. Im Kit-Repo (das gar keine
`team.config.sh` hat) und in jeder frischen Installation ist er deshalb immer
grün; rot wird er ausschließlich in einem Feldprojekt, das seine Caps
regelkonform angehoben hat.

### Fixed

- **`test_zentrale_defaults` misst wieder das Kit (`BL-58`).** Neu ist
  `_lib_default()`: Es liest die Zeile `NAME="${NAME:-wert}"` **statisch** aus
  `team/lib.sh`, statt die Bibliothek zu sourcen. Zurückgespielt aus
  `Feld A`, wo der Fix seit dem 2026-08-09 lief und ein
  `install.sh --update` auf 2.6.0 ihn überschrieben hatte — der `BL-12`-Fall,
  vor dem der Installer selbst warnt.
- **`kit-test.sh` meldete Fehlschläge rot und beendete sich mit Exit 0
  (`BL-59`).** `RC=$?` stand im `then`-Zweig eines `if ! cmd` — dort hat das
  `!` den Status bereits umgedreht, `$?` ist immer 0. Das Gate schrieb
  „FEHLGESCHLAGEN (Exit 0)" und gab genau diese 0 zurück: für jeden Aufrufer
  ein grüner Lauf. Gefunden bei der Gegenprobe zur neuen Stufe 5.
- **`gelb()` war in `kit-test.sh` nie definiert**, wurde aber im Fehlerzweig
  der Abgleich-Pfad-Erkennung aufgerufen — bei `set -e` hätte dort statt der
  Erklärung ein „command not found" mit Exit 127 gestanden.

### Added

- **`kit-test.sh` fährt die Regressionssuite zweimal — Stufe 5 ist neu:**
  einmal im Auslieferungszustand, einmal gegen eine Installation mit
  **angepasster** `team.config.sh` (Caps 10/20, Präfixe `fix(qa)`/`feature`,
  zwei Domänen). Verstellt wird nur, wozu die Config an Ort und Stelle einlädt;
  Pfade und Ordner bleiben unangetastet — die sind die Ablage, gegen die Tests
  gelten dürfen, nicht der Regler, an dem ein Projekt dreht. Schlägt der zweite
  Lauf fehl, nennt die Meldung die Klasse (Messstelle statt Zusicherung) und
  `_lib_default()` als Vorbild. Ein `grep`-Riegel davor stellt sicher, dass die
  `sed`-Anpassung überhaupt gegriffen hat — ein Schritt, der nichts verstellt,
  wäre derselbe Fehler eine Etage höher.
- **`test_projektwert_haelt_das_hard_groesser_soft_verhaeltnis`** — ebenfalls
  aus dem Feld zurückgespielt und dort vom Update mitgerissen. Er prüft
  ausdrücklich die **aufgelösten** Werte: `team_budget_check` wertet den
  Hard-Cap nur bei `hard > soft` aus, bei `hard == soft` verlieren Frank und
  Axel ihren harten Abbruch still. Genau diese Falle war bei der Cap-Anhebung
  im Feld beinahe zugeschnappt. Damit 281 Testfälle.

## [2.8.0] — 2026-08-13

**Das Interview redet jetzt mit dem Anwender, nicht mit dem Autor.** Ein Einzug
in `Feld C` legte offen, dass die Fragen zwar korrekt waren, aber
nur für den verständlich, der die Mechanik dahinter schon kennt: Der Anwender
trug `tests/` in den *Prüfumfang* ein — den Ordner, den er zwei Fragen später
als *Schreibzone* vergab —, und ließ zugleich `main.py` und `bin/` weg, also
genau den Code, für den die Frage gebaut wurde.

### Changed

- **Jede Interview-Frage hat einen Vorspann in Anwendersprache.** Was die
  Antwort bewirkt, ein konkretes Beispiel und was ein falscher Wert kostet.
  Begriffe, die nur intern etwas heißen — „Produktivcode-Ordner", „Guard",
  „Domänen", „Smoke-Test" — stehen nicht mehr in der Frage, sondern werden
  erklärt: „Ordner mit dem Programmcode", „ein Wächter setzt das durch",
  „Kostenkonten", „Prüfbefehl".
- **Die Fragen kommen in neuer Reihenfolge:** erst Test- und Plan-Ordner, dann
  der Prüfumfang. Vorher wurde nach Code *außerhalb* gefragt, bevor feststand,
  welche Ordner die Rollen beschreiben dürfen — die Frage war zum Zeitpunkt
  ihres Erscheinens gar nicht beantwortbar.
- **Der Installer listet Kandidaten für den Prüfumfang auf.** Was in der Wurzel
  neben dem Produktivcode-Ordner liegt und nach Code aussieht (`main.py`,
  `bin/`, `deploy/`), steht jetzt zum Abschreiben in der Frage. Beiwerk —
  `docs/`, `data/`, Konfigurationsdateien, die Team-Entrypoints — ist gefiltert.
- **Die `BL-51`-Warnung sagt die Folge in einem Satz:** „Der Wächter, der sie
  von deinem Code fernhält, greift in diesem Ordner NICHT" — und nennt den
  sicheren Ausweg beim Namen (`team-plans/`).

### Fixed

- **Ein Schreibordner im Prüfumfang wird wieder herausgenommen.** Stand
  `tests/` in beiden Antworten, sagte der Rollen-Auftrag in **einem Absatz**
  „Du änderst NIEMALS Produktivcode (… und tests/)" und „Schreiben NUR unter
  tests/". Harrys Reproducer-Auftrag war damit widersprüchlich; welche Hälfte
  gewinnt, entschied das Modell pro Lauf neu. Der Installer entfernt die
  Kollision und begründet sie. Der Bestandsschutz für vorhandene Testdateien
  liegt ohnehin woanders (`BL-51`).
- **Die Schlussbefehle laufen auch bei Pfaden mit Leerzeichen.** `git -C
  /home/…/Projekt (copy) add -A` war nicht kopierbar — der Zielpfad steht jetzt
  in Anführungszeichen, im Einzug wie im `--update`.
- **Die Regeldatei nannte einen Platzhalter, den niemand füllt.** In
  `## Kostenkontrolle` stand `{{z. B. Sonnet via Claude Code — …}}` — kein
  echter Platzhalter (die Prüfung sucht `{{GROSSBUCHSTABEN}}`), also stand er
  **wörtlich so in jeder installierten `CLAUDE.md`**. Daneben vier weitere
  Substitutions-Leichen (`Soft-Cap `5``, `` `5`/`10` ``, ein nacktes
  `` (`sonnet`) ``) und ein Verweis auf `team-lib.sh`, die es seit dem
  `team/`-Namensraum nicht mehr gibt. Alle fünf Stellen nennen jetzt die
  **wirklichen** Variablennamen und ihre Defaults.
- **Stale Pfadnamen quer durch Kommentare und Docstrings.** `team-lib.sh` →
  `team/lib.sh`, `scripts/kosten.py` → `team/tools/kosten.py`,
  `scripts/beutebuch.py` → `team/tools/beutebuch.py`, `prompts/rolle-*.md` →
  `team/prompts/rolle-*.md`. Wer (Mensch oder Rolle) einem dieser Verweise
  folgte, landete im Leeren.
- **`team.config.sh` empfahl im Kommentar genau das, was `BL-9` verbietet.**
  Der Domänen-Block erklärte die zweite Domäne als „Arbeit an der
  Team-Infrastruktur" und gab `"app team"` als Beispiel — eine Zeile, die in
  einem Feldprojekt strukturell `0.0000` bleibt. Jetzt steht dort, warum EIN
  Konto der Normalfall ist und was mehrere kosten.
- **Doppelte Zeile und kaputte Auszeichnung in `TEAM.md`.**
  „Guard-Experimente nur in einem Wegwerf-Repo" stand zweimal hintereinander;
  im API-Key-Absatz war Fettschrift ineinander verschachtelt.

### Removed

- **`doku/anhang-a.md` war eine Wiki-Seite aus einem fremden Repo.** Sie trug
  Wiki-Frontmatter, **neun tote Links** (`../konzepte/…`, `../vorlagen/…`,
  `../index.md`), eine zweite Platzhalter-Konvention, die niemand füllt
  (`{{Plan-Ordner}}`, `{{loop-skript}}`, `{{ledger-datei}}`) — und vor allem
  eine Anleitung, **die Skripte zu generieren**, die das Kit längst ausliefert.
  Neu geschrieben als kit-native Warum-Schicht: −28 % Zeichen, ein einziger
  verbleibender Link, und ein Kopf, der sagt, wofür die Datei **nicht**
  zuständig ist. Die Abschnittsnummern `A.0`–`A.10` bleiben stabil, weil
  Regeldatei, Regel-Inventar und Backlog darauf verweisen.
- **`bootstrap/ermittlungsakten/` gelöscht.** Der Installer legt den Ordner
  direkt an; die Vorlage wurde nie kopiert.

## [2.7.1] — 2026-08-12

**Der Weg zurück ins eigene Projekt.** Zwei Lücken, die beide erst auffielen,
als die Frage lautete: „Was hat mein zukünftiges Ich in sechs Monaten
eigentlich zur Verfügung?" — Antwort: im Projekt liegt nur `TEAM.md`, der
README bleibt im Kit-Repo zurück.

### Added

- **`TEAM.md` erklärt jetzt, wie man auf eine neue Kit-Version hebt.** Bisher
  stand dazu **kein Wort** in der einzigen Anleitung, die im Zielprojekt liegt.
  Neu: der Befehl, was `--update` anfasst und was nicht, die `--force`-Warnung,
  und vor allem **der Schritt, den nur der Mensch machen kann** — die Regeln aus
  der neuen `CLAUDE.md` nachziehen, weil der Updater sie zum Schutz der
  Projektdaten nicht überschreibt. Mit dem kopierbaren `diff`-Befehl aus dem
  Fix unten.

### Fixed

- **Der Abgleich-Hinweis beim `--update` war nicht ausführbar.** Er nannte
  `diff <(…) <zieldatei>` — das `<(…)` stand für „die mit deinen Werten
  gerenderte Kit-Vorlage", nur sagte er nirgends, wie man die rendert. Der
  Befehl ließ sich nicht kopieren, und der Hinweis verlangte damit genau die
  Arbeit, die er abnehmen wollte. Bauart `BL-44`: angekündigt, aber nicht am
  wirksamen Ort ausführbar. Der Installer legt die gerenderte Fassung jetzt in
  einem Temp-Verzeichnis ab, **behält sie bei einer Abweichung** und druckt den
  fertigen Befehl samt Zeilenzahl der Unterschiede. **Bewusst nicht im Projekt
  abgelegt:** Eine uncommittete Datei außerhalb der Whitelist sieht für den
  Read-Only-Guard aus wie ein Regelbruch.

  Sechs neue Prüfungen in `kit-test.sh` Stufe 5 sichern das ab — dass kein
  Platzhalter mehr auftaucht, dass die genannte Datei existiert, gefüllte Werte
  trägt, der Befehl wirklich läuft, und dass sie **außerhalb** des Projekts
  liegt. Gegenprobe gefahren: Rückbau auf den alten Hinweis → rot.

## [2.7.0] — 2026-08-12

**Die Regeldatei wird geschnitten, und ein Gurt bewacht den Schnitt (`BL-56`).**

Jede Rolle startet über `claude -p`; Claude Code lädt dabei automatisch die
installierte `CLAUDE.md`. Bei ~25 Rollenaufrufen je Kaskade waren das rund
**990k Token allein für Regeln** — und die Rolle bekam ~11k Token Projektregeln
gegen ~500 Token eigenen Auftrag. Der Dreischnitt bringt die Vorlage auf
**26.985 B (−31,6 %)** nach dem Grundsatz **„das WANN gilt für alle, das WIE nur
für einen"**. Zuschnitt am Ende: **Rollen-Regeln → Regeldatei, Bedienung →
`TEAM.md`, Bau → Anhang A.**

Damit dabei nichts still verschwindet, entstand zuerst das **Regel-Inventar**:
73 klassifizierte Aussagen, 61 davon geltendes Recht mit wörtlichem Zitat und
Trägerdatei, geprüft als Stufe 7 in `kit-test.sh`.

Dazu ein **Einstieg für Entwickler, die das Kit nicht kennen** — bisher benutzte
`TEAM.md` ein Dutzend Fachbegriffe, ohne sie irgendwo zu erklären.

### Added

- **Einstieg für Neulinge in `TEAM.md` — „Worum es überhaupt geht" plus
  Glossar.** Bisher traf ein Entwickler, der das Kit nicht kennt, in den **ersten
  32 Zeilen** auf vier undefinierte Begriffe (*Guard*, *Sweep* in Zeile 17;
  *Kaskade*, *Cap*, *Closeout* in Zeile 32) — und ein Glossar gab es nirgends,
  obwohl *Kaskade* 14×, *Guard* 9×, *Beutebuch* und *Ledger* je 7× vorkommen. Neu
  sind ein Abschnitt, der das Modell in drei Punkten erklärt (geplant wird vor dem
  Bauen · Finder ≠ Fixer · jeder Lauf wird gezählt), und ein Glossar mit 15
  Begriffen à einem Satz. Beides steht **nach** der Commit-Warnung: Ein Test
  besteht darauf, dass die teuerste Warnung des Kits im Kopfbereich bleibt — er
  hat den ersten Entwurf zu Recht abgelehnt. `TEAM.md` wird vom Menschen gelesen,
  nicht bei jedem Rollenaufruf geladen; der Zuwachs kostet kein Token-Budget.

- **Regel-Inventar — der Sicherheitsgurt vor dem Umbau der Regeldatei
  (`BL-56`, Vorbedingung aus A.10).** [`doku/regel-inventar.md`](doku/regel-inventar.md)
  klassifiziert **72 Aussagen** der ausgelieferten Regeldatei über alle 10
  Abschnitte als `NORM` (60), `HERLEITUNG` (11) oder `HISTORIE` (1) — mit
  wörtlichem Zitat. [`kit-regelinventar.py`](geteilt/kit-regelinventar.py) prüft als
  **Stufe 7 in `kit-test.sh`**, dass jedes `NORM`-Zitat wörtlich in
  `bootstrap/CLAUDE.md.vorlage` steht, dass kein Abschnitt unerfasst ist und
  dass das Inventar keine Abschnitte nennt, die es nicht mehr gibt.

  **Der Gurt verbietet keine Änderung — er macht sie sichtbar.** Wer eine Regel
  umformuliert oder streicht, bekommt rot und muss die Inventarzeile **benannt**
  nachziehen, statt sie stillschweigend verschwinden zu lassen. Gegenprobe über
  die volle Kette gefahren: entfernte Regel → `kit-test.sh` Exit 1 mit
  Namensnennung der verschwundenen Regel; ebenso neuer Abschnitt ohne
  Inventarzeile und Inventar-Leiche.

  Zwei Bauentscheide, die auch für Nachbauten gelten (in A.10 nachgetragen):
  Verglichen wird **normalisiert** (Blockquote-Marker, Betonungszeichen,
  Zeilenumbrüche raus) — sonst scheitert ein wörtlich richtiges Zitat an einem
  `**nie**` mitten im Satz. Und der Prüfer bewacht die **Vorlage**, nicht die
  Installation: Ein Feldprojekt darf seine `CLAUDE.md` umformulieren (so hält es
  `test_bl55` ausdrücklich fest), die Vorlage darf es nicht unbemerkt.

### Changed

- **Repo-Pflege nach dem Umbau — die zitierenden Stellen nachgezogen.** Genau
  die Gegenrichtung, die die eigene Pflichtzeile verlangt („welche Stellen
  zitieren, was sich geändert hat?"). `README.md`: Aufbau um
  `kit-regelinventar.py` und `doku/regel-inventar.md` ergänzt, `kit-test.sh` als
  **7**-stufig beschrieben, und die Regel „Regeln ändern heißt: Inventarzeile
  nachziehen" unter „Grenzen" aufgenommen. `doku/anhang-a.md` A.9: Der Satz „der
  operative Vertrag steht im Vorlagenblock" stimmte nach dem Schnitt nur noch
  halb — er ist jetzt **zweigeteilt** beschrieben (WANN im Vorlagenblock, WIE im
  Architekten-Briefing). `doku/regel-inventar.md`: `anhang-a` fehlte in der
  Träger-Liste, obwohl der Prüfer ihn längst kennt; dazu der Zuschnitt in einem
  Satz (Regeldatei = was Rollen befolgen, `TEAM.md` = was der Stakeholder
  tut, `anhang-a` = warum es so gebaut ist). `BL-56` trug noch die Zahlen seiner
  Frühfassung (72/60 statt 73/61; 5,7 KB und „14 KB", real 8,2 KB und knapp
  17 KB) und einen fehlenden Satztrenner — beides berichtigt.

  **Nicht geändert, weil geprüft und korrekt:** die „75 Dateien" im README. Eine
  Zählung der echten Installation ergibt 128 Dateien, davon sind 53
  `__pycache__`/`.pytest_cache`/Logs — **git-getrackt sind exakt 75**.

- **Dreischnitt, dritter Block: `## Loop-Mechanik & Auth` von 6,3 auf 2,8 KB
  (`BL-56`).** Der Befund dahinter: **Das meiste hieran macht die Shell, nicht
  die Rolle.** Auth-Auflösung, Retry-Deckel, Cap-Durchsetzung und
  Key-Verdrängung laufen in `team/lib.sh`, **bevor** eine Rolle startet — sie
  las seitenweise Verhalten mit, das sie nicht beeinflussen kann. Geblieben ist,
  wonach eine Rolle handelt: `.ralph-state`, „429 weicht den Guard nicht auf",
  Exit 42 unverändert durchreichen, Guard auf **jedem** Pfad, Smoke-Test im
  Vordergrund. Zwei Regeln wechselten den Träger zum **Menschen**: die
  `.bashrc`-Key-Falle (bindet den Stakeholder an seiner Maschine, keine Rolle
  kann sie befolgen) steht jetzt in `TEAM.md` samt ~13,8-USD-Feldbeleg; „Die
  Arbeit ist meistens fertig" stand dort längst wortgleich.

- **Dreischnitt, zweiter Block: `## Kaskaden-Planungsregeln` von 8,2 auf 5,3 KB
  (`BL-56`).** Das ausführliche Verfahren (Plankopf, Scharfschalt-Sequenz
  Schritt für Schritt) steht im Briefing des Architekten; in der Regeldatei
  bleibt je Regel der normative Kern plus alles, was **andere** Rollen
  begrenzt. **Testgepinnt und deshalb unangetastet:** die Gegenprobe-Regel samt
  Feld-Beleg (`test_bl49` verlangt „zwei fremde Werte"/„sieben"), die
  Pflichtzeile „nebenbei eingelöst — wer zitiert sie?" und die Schreibweise
  `Kit-BL-<N>` (`test_bl50`).

  **Ein Test hat einen echten Fehler abgefangen.** Die kopierfertige Gliederung
  des Abschluss-Docs war mit weggefallen — `test_bl50` verlangt sie
  ausdrücklich, weil die Pflichtzeile **im** Block stehen muss und nicht
  daneben: Die Gliederung ist das, was ein kalt startendes Architekt-Ich
  kopiert, und beim Kopieren fiele die Frage sonst weg. Genau die Bauart aus
  `BL-44`. Der Block wurde **wörtlich aus dem Altstand** zurückgeholt, nicht neu
  getippt.

- **Dreischnitt, erster Block: `## Kostenkontrolle` von 8,6 auf 3,2 KB
  (`BL-56`).** Das **WANN** gilt für alle und bleibt in der Regeldatei
  (Zwei-Schwellen-Modell, was ein überschrittener Cap für die eigene Arbeit
  bedeutet, Token-Sparregeln, und die Pflicht, den Kostenabschluss **nach** dem
  Lauf im Architekten-Closeout zu machen, **nie** in einer Loop-Stufe). Das
  **WIE** — Verben, Ledger-Zeilen, Domänen, Abo-Messung, Prüfung gegen eine
  zweite Quelle — steht jetzt im Briefing des Architekten; keine andere Rolle
  ruft diese Befehle je auf. Drei Herleitungen wanderten nach Anhang A.9
  (`~16 USD`-Auslöser, warum `--ledger-pruefen` kein hartes Gate ist, warum
  **eine** Domäne der Normalfall ist).

  Der Umbau war **kein Umzug, sondern ein Dedup**: `rolle-architekt.md` trug
  die Substanz bereits (Closeout mit Pflichtfrage, `--addieren`/`--ersetzen`,
  `--ledger-pruefen`, Abo-Messung). Ergänzt wurden nur die drei Regeln, die
  wirklich fehlten. Der Regel-Inventar-Gurt meldete **genau drei** NORMen mit
  gewechseltem Träger und sonst nichts — der Beleg, dass Text gekürzt wurde und
  keine Geltung. Vorlage: **39.472 → 33.358 B (−15,5 %)**.

- **Die Regeldatei-Vorlage trägt keine Aktenlage mehr (Vorstufe zu `BL-56`).**
  Die mehrsprachigen Fassungen des T.E.A.M.-Akronyms stehen jetzt in
  `bootstrap/TEAM.md` — sie richten sich an den Menschen, nicht an die Rollen,
  und die Bedienanleitung ist ihr Ort. Wörtlich verschoben, per Diff gegen den
  alten Stand geprüft. Dazu vier Entscheid-Provenienzen entfernt („Entscheid
  2026-07-13", „die frühere Regel ist aufgehoben"), deren Aktenlage
  `doku/anhang-a.md` A.3 **bereits wörtlich trägt** — das war Doppelung, keine
  Streichung. Die Regeln selbst sind unverändert; kein Beleg, kein
  `✅ erprobt`-Marker und keine Geltung angetastet. **753 B, 1,9 %.**

  Der Anlass ist die Messung in `BL-56`: Jede Rolle startet über `claude -p`,
  Claude Code lädt dabei automatisch die installierte `CLAUDE.md` — ~11k Token
  je Aufruf, ~990k Token je Kaskade allein für Regeln. Mehr als diese 753 B war
  ohne Geltungs-Entscheid nicht zu holen: Die Dateigröße ist **testgeschützte
  Absicht** (`test_bl49`, `test_bl17` verlangen den Feld-Beleg ausdrücklich *in*
  der Regeldatei, `test_bl50` beide Träger). Der eigentliche Hebel — 14 KB, die
  nur den Architekten binden und trotzdem in jeden Loop-Rollen-Aufruf geladen
  werden — steht als benannter Entscheid in `BL-56`.

## [2.6.0] — 2026-08-12

**Das Kit zieht in gewachsene Codebasen ein (`BL-51`, `BL-52`).**

Beide Befunde stammen aus der Analyse einer fremden Bestandscodebasis
(`Feld C`, 2026-08-11, nur gelesen). Der rote Faden: **Zwei
tragende Defaults sind Annahmen über ein leeres Repo — und sie scheitern
lautlos.** Ein belegter Plan-Ordner macht die Read-Only-Rollen zu
Schreibberechtigten, ohne dass der Guard je anschlägt; ein Prüfumfang aus
genau einem Ordner lässt den Einstiegspunkt ungeprüft, und der Sweep meldet
trotzdem „sauber".

### Added

- **`TEAM_WEITERER_CODE` — der Prüfumfang endet nicht mehr am
  Produktivcode-Ordner (`BL-52`).** Leerliste aus Dateien **und** Ordnern
  (`"main.py bin/"`), die mitgeprüft werden, ohne unter `TEAM_PRODUKTIVCODE` zu
  liegen. Sie erscheint in der Scope-Zeile des Sweeps
  ([`team/redteam.sh`](bash/redteam.sh)), in der **eisernen Regel** von Red Team
  und Axel — mitgeprüft heißt **genauso tabu**, nicht „freigegeben" — und in
  Franks Fix-Auftrag ([`entry/frank.sh`](bash/entry/frank.sh)), damit er den Fund
  dort reparieren darf, wo er liegt. Das Aufnahme-Interview fragt danach
  (neunter Wert); im neuen Projekt bleibt der Wert leer und **kein Wortlaut
  ändert sich** — dafür gibt es eine eigene Gegenprobe.
  **Nicht** umgesetzt wurde die Backlog-Skizze, `TEAM_PRODUKTIVCODE` selbst zur
  Liste zu machen: Der Wert trägt die Invariante „endet auf genau einen
  Schrägstrich" ([`entry/team.config.sh`](bash/entry/team.config.sh)), an der
  `**`-Muster, Guard-Meldungen und ein Test-Regex hängen — und eine Liste, die
  auch einzelne Dateien enthalten darf, kann sie nicht halten.
- **Der Installer erkennt eine belegte Schreibzone (`BL-51`).** Nach dem
  Interview prüft er Plan- **und** Test-Ordner auf Inhalt, nennt die gefundenen
  Dateien und die Folge in einem Satz („Harry, Marv und Axel dürfen in diesem
  Ordner schreiben und löschen — der Guard schlägt dort NICHT an"), und bietet
  interaktiv einen anderen Ordner an. **Gewarnt, nicht verboten:** Ein bewusst
  geteilter Ordner kann legitim sein.
- **`TEAM_TEST_ORDNER_BESTAND` / `TEAM_PLAN_ORDNER_BESTAND`.** Wer den Ordner
  behält, bekommt den Bestand in `team.config.sh` vermerkt — und aus dieser
  Quelle nennen die Rollen-Prompts ihn als **fremdes Eigentum**: neue Dateien
  anlegen ja, Bestehendes ändern oder löschen nein, „auch nicht, was in dieser
  Aufzählung fehlt". Der letzte Halbsatz ist tragend: Die Liste ist bei zwölf
  Einträgen gekürzt und veraltet, sobald jemand eine Datei hinzulegt.
  **Das ist eine Prompt-Auflage, keine Mechanik** — der Guard kann sie nicht
  erzwingen, weil die Pfade auf seiner Whitelist stehen. Die Config sagt das an
  Ort und Stelle und nennt die harte Variante: ein eigener, leerer Plan-Ordner.
- **`kit-test.sh` fährt einen sechsten Schritt: den Einzug in eine gewachsene
  Codebasis.** Zweites Wegwerf-Repo mit belegtem `plans/`, gewachsener
  `tests/`-Suite und `main.py` in der Wurzel — die Lage aus `Feld C`. Zwölf
  Zusicherungen, darunter beide **Gegenproben** im leeren Repo: Dort schweigen
  Installer und Update. Eine Warnung, die immer erscheint, erzieht zum
  Wegsehen (`BL-14`).

### Changed

- **`install.sh --update` schaut auf das, was es nicht anfassen darf.** Es
  fasst `team.config.sh` weiterhin nicht an, meldet aber (a) den vermerkten
  Bestand in der Schreibzone und (b) — nur wenn `TEAM_WEITERER_CODE` fehlt und
  in der Wurzel wirklich Code liegt — die ungeprüften Dateien samt der Zeile,
  die man einträgt. Gemeldet wird **ausschließlich**, was in der Config steht
  oder wirklich existiert: Nach dem Einzug ist der Plan-Ordner die
  Arbeitsfläche des Teams, dort ist „fremd" nicht mehr unterscheidbar.
- **Doku-Träger nachgezogen:** [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage)
  (Red-Team-Kapitel: Prüfumfang **und** Schreibzone sind im Bestand keine
  Selbstverständlichkeit), [`bootstrap/TEAM.md`](bootstrap/TEAM.md) (eigener
  Abschnitt „Zog das Team in eine gewachsene Codebasis ein?") und die
  [README](README.md).

### Tests

- **Zwei neue Testdateien, 280 statt 267 Testfälle.**
  `test_bl52_pruefumfang.py` und `test_bl51_bestandsordner.py` prüfen am
  **echten Prompt**: `harry.sh` läuft mit gestubbter CLI, die den Prompt
  wegschreibt. Ein Test gegen den Skript-Quelltext hätte die Kopplung
  „Wert gesetzt ⇒ steht im Auftrag" nicht gezeigt.
- **Die Fixtures setzen die Bestandswerte selbst zurück.** Die Config benutzt
  `${VAR:-default}` — eine **leere** Umgebungsvariable fällt auf den
  Projektwert zurück. Ohne das wäre die Gegenprobe „ohne Bestand kein Block"
  in genau den Projekten rot geworden, für die das Feature gebaut ist.
- **Gegenprobe gefahren:** ohne den Fix 11 der 13 neuen Fälle rot; die zwei
  Gegenproben (leerer Wert ⇒ unveränderter Wortlaut) bleiben erwartungsgemäß
  in beiden Richtungen grün.

## [2.5.0] — 2026-08-11

**Sechs Feldbefunde aus `Feld A` (K29–K33), abgearbeitet.**

Der rote Faden: **Ein Vorgang, der Geld gekostet hat, muss eine Spur
hinterlassen, die man von „nichts passiert" unterscheiden kann.** Fünf der
sechs Einträge sind Varianten davon — ein Erfolgslog ohne Auftrag, ein
Kostenlog ohne Inhalt, ein Sweep ohne Fund, eine Warnung ohne zutreffende
Ursache, ein abgetragener Backlog-Punkt ohne Nachzug in den Zitaten.

### Added

- **Vierte Fehlerklasse wird erkannt und benannt: „Stufe fertig, Quittung
  fehlt" (`BL-41`, zweite Hälfte).** Neben Erfolg, echtem Fehler und
  Session-Limit gibt es einen vierten Ausgang: Die Rolle startet einen
  Hintergrund-Task/Monitor/Wakeup und wartet auf eine Benachrichtigung, die es
  headless nicht gibt. Das Log trägt dann `subtype: success`, `is_error:
  false` — **es sieht aus wie ein Erfolg** —, nur das Promise fehlt. Vier
  Vorfälle im Feld, **19,47 USD**, jedes Mal für Arbeit, die fertig und grün
  war. Die bisherige Meldung („KEIN Promise — Log prüfen") schickte den
  Menschen in ein Log, das Erfolg meldet, und von dort in den **Plan** statt in
  den Fehlermodus; dreimal folgte darauf ein Neubau, der die bezahlte Arbeit
  wegwarf.
  **Neu:** `team_result_meldet_erfolg` + `team_quittung_fehlt_melden` in
  [`team/lib.sh`](bash/lib.sh); [`ralph.sh`](bash/entry/ralph.sh) endet in diesem
  Fall mit dem eigenen **Exit 43** und druckt den Prüfweg (committet? Suite
  grün? dann von Hand quittieren), [`vollautomatik.sh`](bash/entry/vollautomatik.sh)
  und [`halbautomatik.sh`](bash/entry/halbautomatik.sh) reichen ihn als eigenen
  Ausgang durch — nicht als „Fehler". **Geprüft wird die Struktur, nicht der
  Wortlaut:** Die drei Feldvorfälle formulierten es dreimal anders („background
  pytest run and monitor", „fallback check / wakeup", „set up a monitor to catch
  its completion"), und die vierte Variante schreibt jemand morgen. Die
  Vordergrund-Auflage in `SMOKE_ZEILE` (2.4.x) bleibt als **Prävention** — sie
  hat in K33 nicht gehalten, obwohl sie wortgleich installiert war: Ein Satz aus
  dem ersten Turn konkurriert nach 65 Turns mit dem gesamten seither gewachsenen
  Kontext. Prävention per Prompt skaliert **gegenläufig zur Stufenlänge**.
- **Verworfene Versuche bekommen einen Ersatzzettel (`BL-46`).** Scheitert ein
  Aufruf so, dass das Log unlesbar bleibt (im Feld: **0 Byte nach 47 Minuten**),
  schreibt `team_claude` an seine Stelle einen Zettel mit dem, was belegbar ist:
  `total_cost_usd: null`, `team_versuch: "verworfen"`, gemessene Dauer.
  **Nicht geschätzt — sichtbar gemacht.**

### Fixed

- **`kosten.py summe` zählte ein unlesbares Log still als 0.0000 (`BL-46`).**
  Das ist der Pfad, den Live-Kontostand, `--budget` und die Pro-Lauf-/
  Pro-Stufe-Deckel benutzen: Der Abo-Gegenwert von 47 Minuten fiel aus **jedem**
  Kostenabschluss, der Deckel bekam auf diese Hälfte keinen Griff, und die Stufe
  erschien als die **billigste** der Kaskade, obwohl sie als teuerste angesetzt
  war. **Neu:** Die Zahl auf stdout bleibt unverändert (Aufrufer parsen sie), der
  Hinweis geht nach stderr — „N verworfener Versuch(e), zusammen 47 min, Kosten
  UNBEKANNT".
- **`ledger-pruefen` schlug wegen desselben Logs dauerhaft falschen Alarm
  (`BL-46`).** P2 meldete die Kaskade als verdächtig, nannte zwei Ursachen, von
  denen keine zutraf, und empfahl als Abhilfe `--ersetzen` — eine Handlung, die
  nach `BL-5` den Altwert vernichtet. Der Wächter empfahl also, Geld zu
  verlieren, und es gab **keinen dokumentierten Weg**, den Rest loszuwerden.
  **Neu:** Unarchivierte Logs **ohne Kostenbeleg** (Ersatzzettel oder kaputt)
  sind ein Hinweis statt einer Warnung und nennen den Weg heraus; der
  `BL-5`-Fall (echtes unarchiviertes Log) bleibt unverändert eine Warnung.
  `--rollen-abschluss` archiviert Ersatzzettel **mit** (sie können nicht doppelt
  zählen) und sagt beim Buchen, dass der Betrag nachweislich unvollständig ist;
  eine wirklich unlesbare Datei bleibt liegen — mit genanntem Ausweg.
- **Ein Sweep ohne Fund war von einem abgebrochenen Sweep nicht zu
  unterscheiden (`BL-47`).** Im Feld: Marv, 9 Minuten, **3,1418 USD**, eine
  einzige committete Datei (ein Sondenskript), null Beutebuch-Zeilen — und
  trotzdem Commit-Botschaft „neue Funde/Reproducer" plus Protokollzeile „Funde
  committet. Übergabe an Frank." Inhaltlich war das Nichtfinden richtig; der
  Fund ist die **Ununterscheidbarkeit**: Eine read-only-Rolle hat weder
  Statuswechsel noch Produktivdiff, an dem sie sonst auffiele. **Neu:**
  [`redteam.sh`](bash/redteam.sh) zählt die **wirklichen** neuen Funde
  (`next-id` vorher gegen nachher — die Zahl lag längst vor) und schreibt sie in
  Commit-Botschaft **und** Protokoll: „1 neuer Fund" / „keine neuen Funde",
  „Geprüft, KEINE neuen Funde … Keine Übergabe an Frank." Dazu im Sweep-Auftrag
  die fehlende Pflicht: Ein Wegwerf-Skript wird **gelöscht** oder als
  `HM-<Nr>`-Reproducer **benannt** — was in `tests/` bleibt, braucht einen Namen
  und einen Fund.
- **Die Abo-Key-Startwarnung zeigte nach einem API-Fallback auf die falsche
  Ursache (`BL-48`).** Sie empfahl, den Key „aus `.bashrc`" zu nehmen — dort lag
  keiner. Gesetzt hatte ihn der API-Fallback der **vorigen Stufe** im selben
  Prozessbaum. Weil die Warnung nur **einmal pro Prozessbaum** feuert,
  verbrauchte der Fehlalarm zusätzlich genau das Fenster, das dem echten Fall
  zusteht (dort real ~13,8 USD Leerlauf über API). **Neu:**
  `team_resolve_auth_mode` markiert einen **selbst geladenen** Key
  (`TEAM_KEY_AUS_FALLBACK`); die Meldung sagt dann, was wirklich passiert ist,
  und **verbraucht das Warnfenster nicht**.

### Changed

- **Zentrale Werte werden gegengeprobt, nicht gegrept (`BL-49`).** Neue Regel in
  den bauenden Briefings (Ralph, Frank) und in der Aushärtungs-Checkliste: Wer
  eine Konstante/einen Default/einen Schwellwert ändert, fährt sie probeweise
  gegen **zwei fremde Werte** (höher/niedriger), lässt die Suite laufen und
  setzt den Wert **nachweislich zurück**. Grund: Eine *arithmetische* Kopplung
  ist per Textsuche unauffindbar — im Feld fand `grep` nach Name und altem Wert
  **fünf** Stellen, das Verstellen **sieben**; die zwei zusätzlichen wären beim
  nächsten Tweak an unerklärlicher Stelle rot geworden.
- **Der Closeout pflegt jetzt auch die Gegenrichtung (`BL-50`, Stufe 1).**
  Erledigte Backlog-Einträge abzutragen funktionierte; **nichts** pflegte die
  Stellen, die den Backlog **zitieren** — Skizzen und Kandidatenlisten
  begründen ihre offenen Fragen mit Backlog-Nummern und veralten still. Der
  Fehler schlägt beim **Vorlegen der Kandidaten** zu, also nachdem eine Option
  formuliert wurde, die es nicht mehr gibt (im Feld: drei Kaskaden lang eine
  Prämisse, die der zitierte Eintrag selbst widerlegte). **Neu:** Pflichtzeile in
  Abschnitt 4 der Abschluss-Gliederung *(„Welche offenen Punkte hat dieser Lauf
  **nebenbei** eingelöst, und wer zitiert sie?")* — in der Gliederung selbst, nicht
  nur in der Prosa daneben —, dazu die Schreibweise `Kit-BL-<N>` für fremde
  Backlog-Nummern. **Offen bleibt Stufe 2**, der maschinelle Lint: Roh gemessen
  lag seine Trefferquote bei ~40 % (sechs von zehn Markierungen waren legitime
  Rückblicke); roh ausgeliefert wäre er die Falle aus `BL-14` — eine Warnung, die
  bei jedem Aufruf erscheint und zum Wegsehen erzieht.
- **Sechs neue Testdateien, 267 statt 232 Testfälle.** Jeder Eintrag mit
  Gegenprobe: Mit zurückgerollten Quellen fallen **25** der neuen Zusicherungen,
  keine bestehende. `BL-41`, `BL-47` und der Abschlusspfad von `BL-46` werden
  über die **wirkliche Bedienoberfläche** geprüft (`ralph.sh`/`harry.sh` gegen
  ein Wegwerf-Repo mit gestubbter CLI), nicht nur auf Bibliotheksebene.

## [2.4.4] — 2026-08-02

**Zwei Kennzahlen, die im Closeout das Falsche behaupteten.**

Beide aus dem Feld (`Feld A`, Architekt-Closeout K3),
beide gefunden beim Nachrechnen des Endstands — nicht von einem Werkzeug.
Kein Rechenfehler: Das Ledger war jedes Mal korrekt, falsch war, was die
Anzeige über die Zahlen **sagte**.

### Fixed

- **`--budget` behauptete „nicht im Gesamt enthalten" — auch dann, wenn die
  Architekten-Zeile sehr wohl enthalten war (`BL-18`).**
  [`entry/team-status.sh`](bash/entry/team-status.sh) druckte den Zusatz
  **unbedingt**, obwohl `team_architekt_stand` zwei Modi hat: Im Modus
  `geschätzt` stammt der Wert aus der A2-Churn-Schätzung und steht in **keiner**
  Ledger-Zeile — der Zusatz stimmt. Im Modus `echt` stammt er aus einer
  **Ledger-Zeile** der laufenden Kaskade, und die summiert
  `team_kontostand_gesamt` mit — der Zusatz ist dann falsch. Der Modus schaltet
  ausgerechnet **beim Kaskaden-Abschluss** um, also genau in dem Moment, in dem
  die Zahl abgelesen und weitergegeben wird. Im Feld: Anzeige „Architekt (echt,
  nicht im Gesamt enthalten): 9.7000" bei „Gesamt: 71.5706" — der beim Wort
  genommene Kontostand wäre **81,27 statt 71,57 USD** gewesen, 13 % zu viel.
  **Neu:** Der Zusatz hängt am Modus (`echt` ⇒ „im Gesamt enthalten"), und die
  Beschriftung nennt den Bezugsrahmen: `Architekt K3 (echt, im Gesamt
  enthalten)`. Denn der Wert gilt für **eine** Kaskade, während jede andere
  Zeile des Blocks lebenslang kumuliert — ohne Rahmen las man 9,70 als
  Lebenssumme des Architekten (real: 37,30). Die Nummer liefert die neue
  `team_architekt_kaskade`; `team_architekt_stand` behält seinen
  Zwei-Felder-Vertrag, an dem `team-status.sh` und drei Testdateien hängen.
- **Dieselbe Einladung zum Doppeladdieren stand im zweiten Block (`BL-18`,
  Nachzug).** Die Momentaufnahme (`./team-status.sh` ohne Argument) zeigte die
  reine A2-Schätzung — „Architekt (geschätzt, A2)" — direkt über
  „Gesamt-Kontostand (inkl. Ledger)". Nach dem Buchen stand dort also eine
  **Schätzung** neben einer Summe, welche die **echte** Zeile bereits enthält,
  und die Beschriftung war modusblind. **Neu:** Beide Ansichten bauen ihre
  Beschriftung aus **einer** Quelle (`status_architekt_zeile`); zwei Anzeigen
  derselben Kennzahl können nicht mehr auseinanderlaufen. Ein eigener Testfall
  hält genau das fest.
- **`--rollen-abschluss` schrieb eine Notiz wortgleich in zwei Zeilen mit
  verschiedener Bedeutung (`BL-19`).** Seit `BL-4` ruft die eine
  Bedienhandlung zwei Verben mit demselben `--notiz` auf: `rollen-abschluss`
  bucht `.team-logs`, `ralph-abschluss` bucht `.ralph-logs`. Ein Text kann aber
  höchstens eine der beiden Zeilen beschreiben — im Feld trug Ralphs Zeile über
  **vier Baustufen** die Notiz „Harry/Marv-Sweeps + Frank HM-6". Das Ledger ist
  die maschinelle Wahrheit für ein kalt startendes Architekt-Ich, und dieses
  Feld ist die **einzige** Prosa-Spur je Zeile. Ein Rückfall obendrein: Genau
  diese Beschwerde stand schon in Feld-`BL-5`, der `BL-4`-Fix hat sie
  strukturell wieder eingebaut.
  **Neu:** [`kosten.py`](geteilt/tools/kosten.py) setzt den Vorspann selbst, aus
  der Zielrolle — `Rollen: …` / `Bau: …`, für projekteigene Rollen deren Name.
  Kein zweiter Bedienparameter: Die Bedienung bleibt einhändig, und ein
  optionales `--notiz-ralph` wäre dieselbe Falle wie das „optional" in `BL-15`
  gewesen — was man setzen *kann*, setzt im Closeout niemand.

### Changed

- Die `Gesamt`-Zeile in `--budget` heißt zur Abgrenzung von der
  kaskadenscharfen Architekt-Zeile jetzt „(Basis + laufend), lebenslang".
- Leseregeln zu beiden Kennzahlen in [`bootstrap/TEAM.md`](bootstrap/TEAM.md)
  und im Architekten-Briefing; Bau-Details als Lehren in
  [`doku/anhang-a.md`](doku/anhang-a.md) A.9. Dabei fiel dort eine seit `BL-5`
  veraltete Aussage auf („ein zweiter Aufruf **ersetzt** die Zeile" — er bricht
  seither ab) und wurde mitkorrigiert.
- Zwei neue Regressionstests (`test_bl18_…`, `test_bl19_…`), beide mit
  gefahrener Gegenprobe. Die Installation fährt jetzt **228** Tests.

## [2.4.3] — 2026-08-02

**Der Guard urteilte ohne Ausgangszustand — und die einzige Verifikation, die
zwischen Doku und Testaufruf schaut, gab es nicht.**

Zwei Entscheide des Stakeholders, beide gebaut. `BL-16` war der letzte
offene Feld-K2-Befund; `BL-17` kam aus demselben Feld nach.

### Fixed

- **Der Read-Only-Guard schrieb jede schmutzige Datei der laufenden Rolle zu
  (`BL-16`, Ebene 1).** [`team_guard_verify`](bash/lib.sh) bildete die
  Verletzerliste aus `git diff --name-only` **plus** `git status --porcelain`
  und hatte **keinen Ausgangszustand**: Sie wusste nicht, was beim Rollenstart
  bereits schmutzig war. Jeder fremde Schreiber — eine parallele Sitzung, eine
  Handänderung, ein abgebrochenes Werkzeug — wurde der Rolle angelastet **und**
  hart zurückgesetzt. Der eigene Kommentar der Funktion („schützt parallele/
  legitime uncommittete Arbeit") galt nur gegenüber dem blanko `reset --hard`,
  das sie ablöste; das chirurgische `git checkout -- <pfad>` zerstört fremde
  Arbeit genauso, nur gezielter.
  **Neu:** `team_guard_begin` hält `TEAM_GUARD_VORHER`, einen Schnappschuss mit
  **Blob-Hashes**. Der Hash ist der Punkt: Ein reiner Pfadabgleich wäre ein
  Freibrief für jede Rolle, die eine ohnehin schmutzige Datei zusätzlich
  verändert. Unverändert ⇒ fremd, kein Rollback, keine Zuschreibung.
  Verändert ⇒ ihre Sache. Bei nicht sauberem Baum warnt `team_guard_begin`
  laut und nennt die Pfade — **warnen statt abbrechen**, weil uncommittete
  Arbeit der Normalfall ist und ein harter Abbruch legitime Läufe erschlüge.
- **Eine Guard-Verletzung kassiert den Übergriff, nicht die Arbeit (`BL-16`,
  Ebene 2).** Bisher übersetzten [`entry/axel.sh`](bash/entry/axel.sh) und
  [`team/redteam.sh`](bash/redteam.sh) jeden Übergriff sofort in `RC=1`. Damit
  zählte im Feld eine **fertige, korrekte** Ermittlung als „Aufruf
  fehlgeschlagen" → Stagnationszähler → Lauf gestoppt.
  **Neu:** `team_guard_urteil <rolle> <übergriff> <ergebnis>`. Liegt das
  Ergebnis der Rolle vor — bei Axel Akte **und** Statuswechsel, bei Harry/Marv
  die Sweep-Quittung —, zählt die Runde. Der Grenzübertritt ist zu diesem
  Zeitpunkt bereits chirurgisch zurückgerollt und laut gemeldet; ein
  zusätzlicher Fehlschlag bestraft nur noch das Falsche. Fehlt das Ergebnis,
  bleibt es beim Fehlschlag.
- **Die Guard-Meldung trennt die beiden Fälle jetzt sprachlich.** „**DIESE
  ROLLE** hat die folgenden Pfade geändert" vs. „**NICHT angelastet** (beim
  Rollenstart bereits geändert, seither unverändert)". Im Feld wurde der
  Übergriff zunächst der falschen Rolle zugeschrieben, weil die Pfadliste im
  Log neben ihrem Namen stand — belegt war das nirgends.

### Added

- **Die Verifikationskette darf sich den Erfolg nicht selbst einrichten
  (`BL-17`).** Regel in [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage)
  und [`bootstrap/TEAM.md`](bootstrap/TEAM.md): Jeder Befehl, den die Doku
  einem Menschen nennt, muss in der Verifikation **buchstabengetreu**
  vorkommen — gleiche Argumente, gleiche Umgebung, kein zusätzliches
  `PYTHONPATH`, kein stilles `cd`. Dazu ein **fester Sweep-Schwerpunkt** „Doku
  gegen Verifikation diffen" in den Briefings von Harry und Marv.
  **Warum beides:** Im Feld war der dokumentierte Startbefehl kaputt, während
  der Smoke-Test grün meldete. Fünf Red-Team-Funde derselben Kaskade hatten
  exakt diese Bauart, und **keiner** der Sweeps hat diesen gefunden — die
  Lücke klafft zwischen Doku und Testaufruf, nicht im Code, und ist beim
  Codelesen unsichtbar. Gefunden hat sie der Mensch beim ersten eigenen Start.
  Ein maschineller Diff wurde **verworfen** (stackagnostisch schwer, hohe
  Falschmelderate zu erwarten) — er kommt, wenn ein zweiter Fall dieser Bauart
  auftritt.
- **`test_bl16_guard_zuschreibung.py`** (13 Fälle, gegen ein Wegwerf-Repo und
  mit `set -euo pipefail` wie im Ernstfall) und
  **`test_bl17_doku_gegen_verifikation.py`**. Beide Gegenrichtungen von
  `BL-16` eigens abgesichert: Eine vorab schmutzige Datei, die die Rolle
  **doch** anfasst, bleibt eine Verletzung, und bei sauberem Start urteilt der
  Guard unverändert scharf. Gegenprobe gefahren — mit ausgeschalteter
  Zuschreibung fallen genau zwei Zusicherungen. **214 Testfälle** in 35
  Dateien.
- **Zuschreibungs-Lektion in [`doku/anhang-a.md`](doku/anhang-a.md) A.4**, neben
  der Rollback- und der Staging-Lektion. Die drei zusammen sind die Geschichte
  dieses Guards.

### Bemerkt

- **`BL-17` fand seinen eigenen Fund.** Der Regressionstest schlug beim ersten
  Lauf an: Die Regelphrase stand in der Vorlage über einen Zeilenumbruch
  zerrissen und war damit als zusammenhängende Aussage nicht auffindbar. Genau
  die Sorte Formfehler, die eine Regel unwirksam macht, ohne dass jemand sie
  bemerkt — dasselbe Muster wie die fehlenden Backticks in `BL-15`.

## [2.4.2] — 2026-08-02

**Die ausgelieferte Beutebuch-Vorlage lehrte genau die Falle, die `BL-11` im
Regex behoben hatte.**

`BL-11` (Release 2.3.x) hat `DATEI_RE` beigebracht, per Pytest-Node-ID
referenzierte Dateien zu lesen. Das war die **halbe** Reparatur: Der Extraktor
*konnte* den Pfad seither lesen — die Vorlage erzeugte nur nie einen. Sie nannte
ihn **ohne Backticks** und als **„optional"**, an fünf Stellen in vier Dateien,
in **jeder** frischen Installation. Aus dem Feld zurückgespielt (dort `BL-7`,
`Feld A`), wo derselbe Defekt an einem einzigen Fund
12,00 USD verbrannt hat: 9 Frank-Versuche, 3 Axel-Akten, keine Zeile Code
überlebt — bei grünem Smoke-Test und gültigem Promise, also ohne jedes
Fehlersignal.

### Fixed

- **Die `Reproducer-Test`-Zeile ist Pflichtfeld, der Pfad steht in Backticks
  (`BL-15`).** Zwei voneinander unabhängige Defekte, von denen **keiner allein
  wirkt**: (1) „optional" ⇒ Harry und Marv lassen das Feld leer, Franks neue,
  regelkonform nach der Fund-Nummer benannte Testdatei ist im Fund-Block nie
  referenziert, und `team_diff_beruehrt_fund` rollt jeden regelkonformen Fix
  zurück. (2) Ohne Backticks ⇒ selbst ein *ausgefülltes* Feld bleibt unsichtbar,
  weil `DATEI_RE` ausschließlich Backtick-Pfade liest. Die Prompt-Pflicht allein
  hätte also **nichts** bewirkt.
  **Neu:** Die Zeile wird **immer** gesetzt — auch wenn die Datei noch nicht
  existiert. Sie ist keine Quittung über getane Arbeit, sondern eine
  **Reservierung** des Dateinamens für Frank. Geändert in
  [`bootstrap/beutebuch.md`](bootstrap/beutebuch.md) (Vorlage + Begründungs­block),
  [`bootstrap/CLAUDE.md.vorlage`](bootstrap/CLAUDE.md.vorlage) (Beutezug-Dreisatz
  Schritt 2 + Fund-Format), [`team/prompts/rolle-harry.md`](geteilt/prompts/rolle-harry.md),
  [`team/prompts/rolle-marv.md`](geteilt/prompts/rolle-marv.md).
- **Der Guard bleibt unangetastet scharf.** Gewählt wurde die Prompt-Pflicht,
  nicht die Guard-Lockerung (Stakeholder-Entscheid im Feld, 2026-08-02).
  Begründung aus dem Feld: Beim Folgefund setzte Frank die Zeile **von sich
  aus** — dem Muster des vorigen Fundblocks folgend — und kam in **einem**
  Versuch durch. Das Muster trägt, sobald es sichtbar ist; es braucht nur eine
  verbindliche Regel statt Nachahmung.
- **Sechste Stelle, im Feld nicht sichtbar:** `CLAUDE.md.vorlage` schrieb den
  Pfad als `{{TEST_ORDNER}}/…`. Der Platzhalter trägt seinen Schrägstrich
  bereits, das expandierte also zu `tests//…`. Im Feld stand dort die schon
  substituierte Fassung, weshalb der Fund von dort nur fünf Stellen nennen
  konnte.

### Added

- **`test_bl15_reproducer_zeile_ankertauglich.py`** — der Regressionstest, den
  der Feldbefund ausdrücklich empfohlen hat und der diesen Fund verhindert
  hätte: Er nimmt die **wirklich ausgelieferte** Zeile aus allen vier Quellen,
  füllt sie so aus, wie die Vorlage es ansagt, und lässt `DATEI_RE` darauf los.
  Er läuft in beiden Ablagen — im Kit gegen `bootstrap/`, im installierten
  Projekt gegen die substituierten Zieldateien — und prüft zusätzlich, dass die
  Zeile überhaupt noch existiert und nicht wieder als „optional" markiert ist.
  Gegenprobe gefahren: Mit der alten Zeile schlagen genau zwei Zusicherungen
  fehl. **197 Testfälle** in 33 Dateien.

### Bemerkt

- **`install.sh` kompiliert die Tests, die es ausliefert.** Der Installer fährt
  zum Abschluss `pytest` gegen die frische Installation und legt dabei
  `.pyc`-Dateien an. `kit-test.sh` Stufe 3 durchsucht danach **alles** im
  Zielbaum nach übrig gebliebenen Installer-Platzhaltern — auch den Bytecode.
  Eine Testdatei, die einen Platzhalter als String-Literal führt, meldet sich
  damit selbst als Fund. Zusammensetzen hilft nicht: CPython faltet konstante
  Konkatenation beim Kompilieren. Der neue Test ersetzt Platzhalter deshalb
  über ein Muster, nicht über ein Literal.
- **`BL-17` neu im Backlog**, aus dem Feld nachgetragen (dort `BL-10`): *Die
  Verifikationskette darf sich den Erfolg nicht selbst einrichten.* Der
  dokumentierte Startbefehl war kaputt, während der Smoke-Test grün meldete —
  weil Smoke-Test und `pytest.ini` still ein `PYTHONPATH` dazusetzten, das es
  beim Anwender nie gibt. **Fünf** Red-Team-Funde derselben Kaskade hatten
  exakt diese Bauart, und **keiner** der Sweeps hat diesen gefunden: Harry und
  Marv lesen den Code, die Lücke klafft aber zwischen **Doku und Testaufruf**.
  Braucht einen Entscheid, in welcher Form die Regel greift.

## [2.4.1] — 2026-08-01

**Zwei Fehler in `ledger-pruefen`, gefunden beim ersten Einsatz auf einem
fremden, gewachsenen Ledger.**

Beim Rückspielen der Kit-Fixes in das Ursprungsprojekt —
den Ahnherrn des Kits, der das flache Vor-Kit-Layout trägt und deshalb **kein**
`install.sh --update` annimmt — lief `ledger-pruefen` erstmals gegen 67
gewachsene Ledger-Zeilen aus 22 Kaskaden. Es meldete drei Warnungen. **Keine
davon war echt**, und keine war je auflösbar. Ein Werkzeug, das bei jedem Lauf
rot ist, erzieht genau zu dem Wegsehen, gegen das seine zwei Schweregrade
gebaut wurden (Skizze D, Frage 2).

### Fixed

- **Eine Rohquelle kann mehrere Ledger-Rollen speisen (`BL-13`).** `P3` bildete
  Archivordner 1:1 auf **eine** Rolle ab (`roles ↔ .team-logs`). Das ist
  falsch, sobald ein Projekt eine weitere Rolle **separat** bucht — und genau
  dafür existiert `akteur-abschluss --rolle <X>`. Real schreiben
  [`team/redteam.sh`](bash/redteam.sh), [`entry/frank.sh`](bash/entry/frank.sh),
  [`entry/axel.sh`](bash/entry/axel.sh) und
  [`entry/vollautomatik.sh`](bash/entry/vollautomatik.sh) **alle** nach
  `.team-logs`, während der Ahnherr Franks Out-of-Loop-Arbeit als eigene
  `frank`-Zeile bucht. `P3` meldete dieses Geld als „archiviert, aber nie
  gebucht" — strukturell unauflösbar, denn nachbuchen kann man nichts, was
  bereits gebucht **ist**.
  **Neu:** Die Rollenmenge je Ordner wird aus dem Ledger **abgeleitet** statt
  festverdrahtet. `.ralph-logs` gehört Ralph allein, `.team-logs` jeder
  weiteren Rolle mit Rohlog. `architekt` bleibt ausdrücklich außen vor
  (`LEDGER_OHNE_ROHLOG`): Diese Zeile ist eine gemessene Schätzung aus dem
  Transkript, ihr entspricht keine Log-Datei — im Ahnherrn trägt sie 275 USD
  und hätte jede echte Untergebuchung maskiert. Der Befund **nennt die
  gezählten Rollen**, damit ein Mensch die Zahl nachrechnen kann; genau dieses
  Nachrechnen hat `BL-1`, `BL-4` und `BL-5` überhaupt erst gefunden.
- **Benannte Kaskaden sind Out-of-Loop-Buchungen (`BL-14`).** Die `P1`-Regel
  „`roles` ohne `ralph` ⇒ Warnung" stimmt für **nummerierte** Kaskaden: Wo
  gesweept wurde, wurde auch gebaut. Für benannte (`post-20`,
  `roles-post-k13`) gilt sie nicht — das sind Fixserien **nach** dem Lauf, in
  denen Ralph gar nicht gebaut hat. Die fehlende `ralph`-Zeile ist dort
  korrekt, die Warnung dauerhaft unauflösbar, und sie erschien bei **jedem**
  `--budget`. **Neu:** Warnung nur bei `kaskade.isdigit()`, sonst ein Hinweis,
  der den Grund nennt.

### Added

- **6 neue Testfälle** in `test_bl13_ledger_pruefen.py`, darunter beide
  Gegenrichtungen: Eine echte Untergebuchung muss trotz der erweiterten
  Rollenmenge weiterhin anschlagen (mit der echten `BL-4`-Zahl 2,1621 USD),
  und bei einer **nummerierten** Kaskade bleibt die fehlende `ralph`-Zeile
  eine Warnung. Dazu ein Schutzwächter, dass die `architekt`-Zeile keine
  Rohlogs deckt. **182 Testfälle** in 32 Dateien.

### Bemerkt

- **Der Rückkanal lief bisher nur in eine Richtung.** Feld → Kit war geregelt
  (Skizze C), Kit → **Ahnherr** nicht. `BL-11` lag deshalb zwei Kaskaden im
  Feld, bevor es ins Kit kam — und im Ursprungsprojekt lag derselbe Fehler bis
  heute. Dort sind die drei fehlenden Fixes jetzt einzeln nachgezogen
  (`BL-57`/`BL-58`/`BL-59` im dortigen Backlog); eine Migration auf das
  Kit-Layout wäre 531 Pfadverweise in 61 Dateien und wurde bewusst **nicht**
  gemacht (Stakeholder-Entscheid 2026-08-01).

## [2.4.0] — 2026-08-01

**Das Ledger prüft jetzt seine eigene Vollständigkeit** (Roadmap-Skizze D).

### Added
- **`./team-status.sh --ledger-pruefen` / `kosten.py ledger-pruefen`.** Drei
  Prüfungen: (1) trägt jede gelaufene Kaskade eine Zeile je Quelle —
  `ralph`/`roles`/`architekt`? (2) liegen unarchivierte Logs herum, obwohl die
  Kaskade schon gebucht ist? (3) **ergeben die archivierten Rohlogs mehr, als
  im Ledger steht?**
  Nur die dritte Frage zieht ihre Kennzahl aus einer **anderen** Quelle als das
  Geprüfte — und genau das fehlte bisher: `BL-1`, `BL-4` und `BL-5` sind alle
  drei **nicht** durch ein Werkzeug aufgefallen, sondern dadurch, dass ein
  Mensch den gedruckten Bericht neben das Ledger hielt. Dreimal dasselbe
  Muster: Ein Bericht, der seine Kennzahl aus derselben Quelle zieht wie der
  Fehler, bestätigt ihn, statt ihn zu zeigen.
  Exit `4` bei Warnbefunden (`1` bleibt dem Bedienfehler vorbehalten), zwei
  Schweregrade (`warnung` = sehr wahrscheinlich verlorenes Geld, `hinweis` =
  kann legitim sein). Bewusst **kein** hartes Gate im Closeout: Eine Kaskade
  mit legitim fehlender Zeile könnte sonst nicht abschließen, und ein Gate,
  das man regelmäßig umgeht, ist wirkungslos. Stattdessen laufen die Warnungen
  bei jedem `--budget` ungefragt mit.
- **16 neue Testfälle** (`test_bl13_ledger_pruefen.py`), darunter `BL-4` und
  `BL-5` mit ihren **echten Feldzahlen** (2,1621 USD nie gebucht bzw. 1,0969
  USD überschrieben) — beide schlagen an. Gegenprobe für alle drei Prüfungen
  einzeln gefahren. **176 Testfälle** in 32 Dateien.

### Entschieden
- **Der Rohlog-Vergleich läuft je Quelle, nicht je Kaskade.** Die Skizze wollte
  Zeile gegen *ihre* Rohlogs halten; das ist mit der heutigen Ablage nicht
  ehrlich beantwortbar, weil Log-Dateinamen keine Kaskadennummer tragen
  (`stufe-<n>-<ts>.json`, `harry-<ts>.json`) und das Archiv **ein** flacher
  Ordner je Quelle ist. Zuordnen ließe sich nur über mtime-Fenster — in der
  Kostenmechanik wird nicht geraten. Ein Archiv je Kaskade
  (`archiv/kaskade-<n>/`) wäre sauberer gewesen, hätte aber `lauf_kosten()` in
  `vollautomatik.sh` gebrochen, das `.ralph-logs/archiv` **nicht-rekursiv**
  globbt und den Pro-Lauf-Deckel auch gegen bereits weggeräumtes Geld misst
  (`BL-55`). Archivordner ↔ Ledger-Rolle entsprechen einander dagegen
  eindeutig — der Vergleich braucht damit **keine** Zuordnung und hätte `BL-4`
  wie `BL-5` trotzdem gefunden.

### Changed
- Closeout-Regel in `CLAUDE.md.vorlage`, `TEAM.md` und dem Architekten-Briefing
  nachgezogen: Der Abschluss wird **geprüft, nicht geglaubt**; ein stehender
  Warnbefund gehört samt Begründung ins Abschluss-Doc.

## [2.3.2] — 2026-08-01

**Der erste echte `--update`-Einsatz hat zwei Löcher aufgedeckt — beide im
Update selbst.**

### Fixed
- **`--update` löschte projekteigene Tests und nahm lokale Fixes still zurück
  (`BL-12`).** Ein pauschales `rm team/tests/test_*.py` sollte umbenannte
  Kit-Tests einer Altversion entfernen. Im Feld löschte es einen **vom Projekt
  geschriebenen** Infrastruktur-Test, und im selben Lauf wurde
  `team/tools/beutebuch.py` mit der älteren Kit-Fassung überschrieben — samt
  einem lokalen Fix, der real 12,00 USD gekostet hatte. Die Annahme
  „`team/tests/` gehört exklusiv dem Kit" ist falsch, sobald ein Projekt eine
  Lücke im Team selbst schließt.
  **Neu:** `--update` löscht **nichts** mehr. Tests, die das Kit nicht kennt,
  bleiben liegen und werden gemeldet; jede ersetzte Infrastruktur-Datei, die
  vorher von der Kit-Fassung abwich, wird mit `git diff`-Befehl ausgewiesen —
  mit dem ausdrücklichen Hinweis, einen darin steckenden eigenen Fix erst ins
  Kit zurückzuspielen und dann erneut zu updaten.

### Added
- **`BL-11` aus dem Feld zurückgeholt:** `DATEI_RE` in `beutebuch.py` erkennt
  jetzt Pytest-Node-IDs (`datei.py::test_x[param]`) und extrahiert den reinen
  Dateipfad. Vorher galt eine so referenzierte Datei still als „nicht
  referenziert", der Substanz-Anker verwarf jeden Fix, der nur sie berührte,
  und Frank lief in einen endlosen Rollback-Zyklus (real 12,00 USD an `HM-4`).
  Fix und Reproducer stammen aus dem Feldprojekt und lagen dort **zwei
  Kaskaden lang** — genau das Loch, das der Rückkanal schließen soll.
- Drei weitere Zusicherungen in `kit-test.sh` Stufe 5 (projekteigener Test
  überlebt, wird gemeldet, abweichende Infrastruktur wird gemeldet).
- **160 Testfälle** in 31 Dateien.

## [2.3.1] — 2026-08-01

**Sofortnachtrag zu 2.3.0, im Feld erzwungen.**

### Fixed
- **`install.sh --update` lief in einen aktiven Lauf hinein (`BL-10`).** Beim
  ersten Einsatz von `--update` auf ein Feldprojekt lief dort noch
  `vollautomatik.sh`. Das Update legte uncommittete Dateien in `team/` ab; der
  unmittelbar folgende Axel-Lauf (read-only, Whitelist nur `plans/`) wertete
  sie als **Guard-Verletzung**, rollte sie zurück und buchte seine Runde als
  Fehlschlag — obwohl er seine Ermittlungsakte geliefert hatte. Dritte
  Stagnation in Folge, **Lauf gestoppt**, Update spurlos weg.
  Der Guard hat dabei genau das getan, wofür er gebaut ist, und die
  Projektdaten blieben unversehrt. Gefehlt hat die Sperre im Installer:
  `--update` prüft jetzt per `flock -n`, ob `.team-loop.lock` **gehalten** wird
  (nicht bloß existiert), bricht dann mit Exit 2 ab, warnt zusätzlich vor einem
  schmutzigen Arbeitsbaum und macht das anschließende Committen zur
  ausdrücklichen Pflicht — sonst räumt der nächste Read-Only-Lauf das Update
  weg.

## [2.3.0] — 2026-08-01

**Die Kostenerfassung stimmt wieder, und das Kit prüft sich selbst.** Erntelauf
der ersten Feldkaskade: drei Fehler kamen aus dem Feld zurück (`BL-4`, `BL-5`,
`BL-9`), drei fielen beim Aufräumen auf (`BL-6`, `BL-7`, `BL-8`).

### Fixed
- **Ralphs Baukosten landeten in keiner Ledger-Zeile (`BL-4`).**
  `--rollen-abschluss` ledgerte per Definition nur `.team-logs`
  (Harry/Marv/Frank/Axel). Für `.ralph-logs` gab es zwar den Bash-Helfer
  `team_logs_archivieren()`, aber im **gesamten Kit keinen Aufrufer**. Der
  Gesamtstand stimmte nur, solange `.ralph-logs/` liegen blieb — und der Ordner
  steht per `gitignore.fragment` in `.gitignore`. Ein frischer Clone verlor
  damit die **gesamte Bau-Kostenhistorie**, also genau das, wogegen das Ledger
  gebaut wurde (im Feld: 2,1621 von 9,4204 USD).
  **Neu:** `kosten.py ralph-abschluss` — derselbe Mechanismus mit `.ralph-logs`
  als Quelle und `rolle=ralph` als Zielzeile. `./team-status.sh
  --rollen-abschluss` ruft **beide** Verben auf: **eine** Bedienhandlung,
  **zwei** getrennte Ledger-Zeilen. Bewusst keine Sammelzeile — die Trennung
  Bau ↔ Sweep/Fix ist die Kennzahl, an der im Feld überhaupt auffiel, dass
  Ralph fehlte. Bricht ein Verb ab, wird das andere trotzdem versucht.
  Der Fehler war zur Hälfte ein Dokumentationsfehler: Die Closeout-Pflicht in
  `CLAUDE.md.vorlage`, `TEAM.md` und dem Architekten-Briefing nannte Ralph
  nirgends. Alle drei Stellen sind nachgezogen.
- **`--rollen-abschluss` löschte bei einem zweiten Aufruf still Geld aus dem
  Ledger (`BL-5`).** Der gebuchte Wert entsteht aus den **noch nicht
  archivierten** Logs, und ein Abschluss archiviert die gezählten Logs
  anschließend. Aufeinanderfolgende Aufrufe sehen deshalb **disjunkte** Mengen —
  wer nach dem Closeout noch eine Rolle laufen ließ (im Feld: Frank mit drei
  Fixes) und erneut abschloss, bekam einen *kleineren* Wert, der den größeren
  **ersetzte**. Real eingetreten: 1,0969 USD verschwanden hinter 2,4114 USD,
  Sollwert wäre die Summe 3,5083 gewesen; die Korrektur ging nur von Hand.
  Für disjunkte Mengen ist **Addieren** die richtige Verknüpfung — das
  Ersetzen stammte aus `akteur_abschluss()`, wo der Aufrufer einen absoluten,
  extern gemessenen Wert übergibt und Ersetzen deshalb korrekt ist.
  **Neu:** Steht für die Kaskade bereits eine `roles`-Zeile, **bricht der
  Aufruf ab** und nennt Alt-, Neu- und Summenwert; `--addieren` (Nachlauf) und
  `--ersetzen` (Korrektur einer falschen Altzeile) sind die beiden
  ausdrücklichen Wege. Automatisch addiert wird bewusst **nicht**: Ohne
  `--archivieren` zählen zwei Aufrufe dieselben Logs, dann wäre Addieren eine
  Doppelbuchung — die Entscheidung gehört dem Menschen, nicht der Heuristik.
  Bei Abbruch wird **nicht archiviert**, die Logs bleiben also greifbar.
  Der Normalfall (ein Closeout je Kaskade) läuft unverändert ohne jedes Flag.
- `_ledger_zeile_setzen()` bekam dafür einen optionalen `merge_fn`-Haken, der
  **innerhalb** des Ledger-Locks und **vor** jedem Schreibzugriff läuft.
  `akteur_abschluss()` ist unberührt.
- **Zwei Fehler im obigen Fix selbst**, gefunden bei einem manuellen
  Durchlauf gegen eine echte Installation — **nicht** von den 149 Tests:
  (1) `merge_fn` schrieb die Rolle hart als `roles`; ein `--addieren` auf die
  `ralph`-Zeile hätte sie in eine zweite `roles`-Zeile verwandelt und die
  Baukosten erneut unsichtbar gemacht — der `BL-4`-Fehler eine Ebene tiefer,
  erzeugt vom `BL-5`-Fix. (2) Beim Nachlauf **einer** Rolle ist die andere
  Quelle regulär leer; `--addieren` buchte dort `+0,0000` und überschrieb dabei
  Datum und Notiz der bestehenden Zeile mit dem Text des fremden Nachlaufs.
  Beides behoben und mit je einem Regressionstest belegt.
  **Lehre:** Die Tests prüften je Rolle nur einen Modus — die Kreuzkombination
  (andere Rolle × anderer Modus) blieb blind. Ein einziger Durchlauf durch die
  echte Bedienoberfläche fand, was 149 grüne Tests nicht fanden.
- **`README.md`, Abschnitt „Grenzen", war überholt (`BL-7`).** Frank ist
  inzwischen scharf gelaufen (drei Fixes im Feld), Axel weiterhin nicht — und
  die Fixphase einer `vollautomatik.sh` hat noch nie in **einem** Durchlauf
  durchgetragen. Präzisiert statt gestrichen. Zahlen (Dateien, Tests,
  Zeilenumfänge) auf den Ist-Stand gebracht.

- **`--force` war die einzige dokumentierte Update-Option — und
  datenvernichtend (`BL-8`).** Ohne Flag ändert `install.sh` an einem
  bestehenden Projekt gar nichts, mit `--force` überschreibt er auch die
  Projektdaten. Empirisch nachgestellt: `.budget-ledger` geleert,
  `.ralph-state` von `5` auf `1` zurück, Beutebuch-Fund weg, `TEAM_SMOKE_TEST`
  aus `team.config.sh` verschwunden. Ein Feldprojekt konnte die Fixes dieses
  Releases damit gar nicht bekommen, ohne seine Geschichte zu verlieren.
- **Feldprojekte führten eine „T.E.A.M."-Domäne, die strukturell null ist
  (`BL-9`).** Der Kontostand zeigte einen Domänenblock mit einer hart auf die
  Domäne `team` verdrahteten Zeile. In einem Feldprojekt wird am Team nicht
  entwickelt — Funde gehen ins Kit zurück und werden dort verbucht —, die
  Zeile war also immer `0.0000`. Eine Kennzahl, die nie etwas zeigt, erzieht
  dazu, den ganzen Block zu überlesen. Die Verdrahtung war zudem für **jede**
  Konfiguration ohne `team` falsch (z. B. `backend frontend`).
  **Neu:** Installer-Default ist **eine** Domäne (`produkt`); der Block
  erscheint nur bei mehreren und listet dann **jede** konfigurierte Domäne.

### Added
- **`install.sh --update`** — der sichere Weg auf eine neue Kit-Version. Fasst
  nur die Infrastruktur an (Entrypoints außer `team.config.sh`, `team/lib.sh`,
  `team/redteam.sh`, `team/tools/`, `team/prompts/`, `team/tests/`) und lässt
  Ledger, Kaskadenstand, Beutebuch, CHANGELOG, `plans/`, `CLAUDE.md` und
  `team.config.sh` unberührt. Liest die Projektwerte aus der **installierten**
  `team.config.sh` (sonst bekämen die Briefings die falschen Pfade und damit
  eine falsche Guard-Grenze), rettet den Commit-Entscheid aus dem bisherigen
  Architekten-Briefing, entfernt Testdateien entfallener Versionen und meldet
  am Ende, welche Doku-Dateien von der Kit-Fassung abweichen — die **Regeln**
  zieht der Mensch nach, sonst läuft die Doku der Mechanik hinterher (das war
  die Hälfte von `BL-4`).
- `kit-test.sh` prüft den Update-Pfad als **Stufe 5**: Es macht das
  Wegwerf-Projekt künstlich „lebendig" (Ledger, Kaskadenstand, Beutebuch-Fund,
  eigener Smoke-Test, Alttest einer Vorversion) und weist nach, dass `--update`
  davon nichts anfasst.
- `team/tests/test_bl4_ralph_abschluss.py` — vier Prüfungen, darunter die
  entscheidende über die Bedienoberfläche: **ein** `--rollen-abschluss` muss
  **beide** Zeilen erzeugen und beide Log-Ordner rotieren. Gegenprobe gefahren:
  Mit dem alten Ein-Verb-Aufruf ist genau dieser Test rot.
- `team/tests/test_bl5_rollen_abschluss_bestand.py` — sieben Prüfungen, darunter
  das **Feldszenario mit den echten Zahlen** (1,0969 → Frank-Nachlauf 2,4114 →
  3,5083) inklusive Archivierung. Gegenprobe gefahren: Mit dem alten Verhalten
  sind genau die beiden Kernprüfungen rot.
- **153 Testfälle** in 30 Dateien (im installierten Projekt).
- **`kit-test.sh` — das Kit prüft sich jetzt selbst (`BL-6`).** Bisher gab es
  dafür keinen Befehl: `pytest team/tests` schlägt im Kit-Repo mit **17 von 138**
  Tests fehl, weil die Tests die **installierte** Ablage voraussetzen
  (Entrypoints in der Wurzel statt unter `entry/`). Kein einziger dieser
  Fehlschläge war ein echter Fund — aber sie machten den einzigen vorhandenen
  Testlauf unbrauchbar, und damit war jeder im Kit committete Fix bis zur
  nächsten Feldinstallation ungeprüft. **Genau so ging `BL-1` durch drei
  Releases.**
  `./kit-test.sh` installiert das Kit nicht-interaktiv in ein frisches
  `mktemp`-Git-Repo, sucht ungefüllte `{{PLATZHALTER}}`, committet wie in
  `TEAM.md` vorgeschrieben und fährt dort `./team-test.sh` — die Tests laufen
  also dort, wo sie gelten. Der Installer wird dabei mitgeprüft. Exit-Code wird
  durchgereicht (Gegenprobe gefahren: erzwungener Fehlschlag ergibt Exit 5),
  `--behalten` lässt das Wegwerf-Repo zur Fehlersuche stehen. Ruft keine
  Agenten-CLI auf und kostet daher nichts.

## [2.2.1] — 2026-08-01

**Die Fixphase war in jeder Installation tot.** Erster Fund aus einem
Feldprojekt zurück ins Kit (`Feld A`, Kaskade 1).

### Fixed
- **`team/tools/beutebuch.py` löste die Projektwurzel eine Ebene zu hoch auf.**
  Die Datei liegt in `team/tools/`, also zwei Ebenen unter der Wurzel;
  `parent.parent` ergab `team/` und damit den Pfad `team/plans/beutebuch.md` —
  eine Datei, die es nie gibt. Weil `_lies_zeilen()` für eine fehlende Datei
  eine leere Liste liefert **statt zu scheitern**, meldete das Werkzeug ruhig
  „keine Funde": `first` gab Exit 1 zurück, `frank.sh` schloss daraus „nichts
  zu tun", und `vollautomatik.sh` beendete die Fixphase in Runde 1 — mit drei
  offenen Funden im Buch. Der gedruckte Abschlussbericht bestätigte den Fehler
  („keine Funde"), weil er dieselbe kaputte Quelle liest.
  **Betroffen war jede mit 2.0.0–2.2.0 installierte Instanz**: Red Team schreibt
  Funde, Frank sieht sie nie, niemand bemerkt es — der Lauf endet grün.

### Added
- `team/tests/test_bl1_beutebuch_repo_root.py` — drei Prüfungen: Default-Pfade
  zeigen auf die Wurzel, ein aus fremdem Arbeitsverzeichnis gestarteter
  `list`-Aufruf gegen ein Miniatur-Projekt findet den Fund, und im
  installierten Projekt trifft der Default eine existierende Datei
  (übersprungen im Kit-Repo, das kein `plans/` hat).
- `team/tests/test_bl3_werkzeug_default_pfade.py` — schließt die **Ursache**,
  dass der Fehler durch 132 grüne Tests rutschte: Sämtliche Werkzeug-Tests
  arbeiteten mit `--pfad` auf Fixtures, der Default-Pfad war ungeprüft.
  Prüft jetzt zusätzlich, dass **jeder Entrypoint ins Skriptverzeichnis
  wechselt** — die bislang nirgends festgehaltene Invariante, auf der die
  arbeitsverzeichnis-relativen Pfade von `kosten.py` ruhen.
- **138 Testfälle** gesamt (im installierten Projekt).

### Audit
- `kosten.py` hat den Fehler **nicht**: es leitet keine Pfade aus `__file__` ab,
  sondern hält sie arbeitsverzeichnis-relativ (`.budget-ledger`). Korrekt —
  aber nur, solange die `cd`-Invariante gilt, die jetzt getestet wird. Wer die
  Pfade dort „vereinheitlicht", muss beide Tests bewusst mitziehen.

## [2.2.0] — 2026-08-01

**Erster scharfer Lauf — das Kit ist verifiziert, nicht nur geprüft.**

### Added
- **`TEAM.md`** — der menschliche Einstiegspunkt, bisher die letzte Lücke.
  Beim Abnahmegespräch fiel auf: Die teuerste Warnung des Kits („vor dem ersten
  Guard-Lauf committen") stand **nur in der Terminal-Ausgabe des Installers** —
  und die scrollt weg. Exakt der Fehler, den Planungsregel 5 für den
  Abschlussbericht behebt. `TEAM.md` liegt jetzt im Projekt und im Git:
  Guard-Warnung ganz oben, Rollenübersicht, Kaskaden-Ablauf, Befehlstabelle,
  **Exit-Code-Tabelle** (42 ist kein Absturz), Ablageübersicht und eine
  Fehlersuch-Tabelle.
- Fünf Regressionstests dafür (`test_team_md_bedienanleitung.py`): TEAM.md
  existiert, Guard-Warnung steht im Kopfbereich, Exit-Codes erklärt, Closeout
  als Pflicht benannt, keine offenen Platzhalter. **132 Testfälle** gesamt.
- Installer-Abschlussmeldung verweist zuerst auf `TEAM.md`, mit dem Hinweis,
  dass die Terminal-Ausgabe wegscrollt und die Datei bleibt.

### Verified — scharfer Erstlauf in einem Wegwerf-Projekt
Erstmals mit **echten CLI-Aufrufen** statt Fixtures:
- **Ralph**: Auth-Auflösung (abo) → realer Aufruf → Code gebaut → Smoke-Test
  grün → genau ein `feat(stufe1)`-Commit → Promise erkannt → State auf 2 →
  `RALPH_CAP` respektiert → sauberer Exit 0. **0,2728 USD.**
- **Harry** (Red Team, read-only): realer Sweep über die Historie, Exit 0,
  State auf HEAD gesetzt, **Produktivcode nachweislich unangetastet**.
  **0,4751 USD.**
- **Read-Only-Guard Linie 2 belegt**: Das Log enthält **zwei
  `permission_denials`** — die `--allowedTools`-Allowlist hat zwei
  Bash-Aufrufe von Harry real verweigert. Kein `is_error`.
- **Kostenerfassung**: Ledger und `--budget` weisen 0,7479 USD als
  Abo-Gegenwert aus, korrekt getrennt von real abgerechneten API-Kosten.

Damit ist die Kette Konfiguration → Briefing → `team_claude` → Auth →
Promise-Auswertung → Budget-Check → State-Fortschritt → Guard → Kostenlog
**durchgängig unter echten Bedingungen belegt**.

## [2.1.0] — 2026-08-01

Erstlauf-Anleitung in die Artefakte geschrieben. Sie existierte bisher nur als
mündliche Empfehlung — ein kalt startender Architekt in einem frischen Projekt
hätte sie nicht gekannt. Dieselbe Lehre wie bei Planungsregel 5: Was nicht im
Git steht, existiert für die nächste Instanz nicht.

### Added
- **`rolle-architekt.md`, Abschnitt „Die erste Kaskade eines Projekts"** — vier
  Sonderregeln: Smoke-Test hat Vorrang vor jedem Feature; erste Kaskade auf
  drei bis fünf Stufen begrenzen; `BUDGET_EMPFEHLUNG_USD` konservativ, aber
  nicht knauserig (ein zu tiefer Deckel vervielfacht die Kosten, `HM-32`);
  nach dem Erstlauf den Bauweg ehrlich bewerten.
- **`bootstrap/roadmap-skizzen.md`** ist nicht mehr leer, sondern bringt
  „Skizze 1: Verifikationsfähigkeit herstellen" mit. Sie zeigt über den
  gefüllten `{{SMOKE_TEST}}`-Platzhalter selbst an, ob sie noch gebraucht wird,
  und darf gestrichen werden, sobald der Befehl steht.
- Installer-Abschlussmeldung nennt `TEAM_BUDGET_USD=15` für den Erstlauf und
  verweist ohne Smoke-Test ausdrücklich auf Skizze 1.

## [2.0.0] — 2026-08-01

**Sprach- und stackagnostisch.** Version 1.0.0 setzte an mehreren Stellen still
den Stack des Ursprungsprojekts voraus. Diese Fassung trennt Team-Infrastruktur
und Projekt sauber — verifiziert in Go-, Rust- und PHP-Projektstrukturen.

### Changed — Breaking
- **Neues Layout.** Entrypoints bleiben in der Repo-Wurzel (`./vollautomatik.sh`
  usw. — die Feld-Ablagekonvention), alles Aufgerufene liegt jetzt unter
  `team/`: `team/lib.sh`, `team/redteam.sh`, `team/tools/`, `team/prompts/`,
  `team/tests/`. **Das Kit legt nichts mehr in `scripts/` oder im Test-Ordner
  des Projekts ab** — diese Ordner gehören dem Projekt.
- **Domänen sind projektdefiniert.** `kosten.py` erzwang die Werte `website`
  und `team` an drei Stellen; in einem fremden Projekt war damit keine
  sinnvolle Kostentrennung möglich. Jetzt konfigurierbar über `TEAM_DOMAENEN`
  in `team.config.sh` (Default `produkt team`). **Der Lesepfad validiert nicht
  mehr**: historische Ledger-Zeilen mit heute unbekannten Domänen bleiben
  filterbar; validiert wird nur beim Schreiben.
- **Interview auf sieben Fragen**: Domänen und Commit-Regel des Architekten
  kommen dazu. Letztere stand in der `CLAUDE.md` bisher als offenes
  Entweder-oder.

### Fixed
- **Die Rollen-Briefings waren nicht parametrisiert.** Sie wurden in 1.0.0
  wörtlich übernommen und nannten deshalb `site/**` als Guard-Grenze und
  `python3 scripts/smoke_test.py` als Smoke-Test — in einem fremden Projekt
  bekamen Harry, Marv und Axel damit die **falsche Grenze** genannt und Ralph
  einen Befehl, den es nicht gibt. Die Briefings sind Prompts und werden jetzt
  wie alles andere beim Installieren gefüllt.
- `install.sh` prüfte im Selbsttest noch `scripts/*.py` und meldete deshalb
  immer „Python-Werkzeuge fehlerhaft" (Exit 1 trotz erfolgreicher Installation).
- `.gitignore`-Fragment brachte `__pycache__/` und `.pytest_cache/` global mit;
  jetzt auf `team/**` eingegrenzt.

### Added
- **`team/prompts/rolle-architekt.md`** — das sechste Briefing fehlte, weil der
  Architekt interaktiv läuft und `team_briefing` nie braucht. Für den Trigger
  „Du bist unser Architekt" gab es damit nichts Kompaktes: jetzt Auftrag,
  Grenze, Planungs-Dreisatz, Closeout-Pflicht und Commit-Regel auf einer Seite.
- **`team-test.sh`** — führt die Team-Regressionstests getrennt vom Testlauf
  des Projekts aus. Dein Testbefehl bleibt `TEAM_SMOKE_TEST`.
- Abschlussmeldung des Installers nennt jetzt den **Kostenabschluss nach dem
  Lauf** — ohne ihn bleiben die Architekt-Kosten strukturell unerfasst.

### Tests
- 25 Testdateien, **127 Testfälle**, grün in allen drei geprüften Stacks.
- Angepasst für den generischen Einsatz: Fixtures auf das `team/`-Layout,
  Domänen-Literale durch den konfigurierten Wert ersetzt, Guard-Grenze im
  Briefing-Test aus `team.config.sh` gelesen statt fest erwartet, Lesepfad-Test
  auf den neuen Vertrag umgestellt.

## [1.0.0] — 2026-08-01

Erste Fassung. Der Code stammt aus dem Ursprungsprojekt (22 Kaskaden scharf
gelaufen, 2026-07-10 bis 2026-08-01) und wurde übernommen, nicht neu geschrieben.

### Added
- `install.sh` — idempotenter Installer, fünf Fragen, Selbsttest am Ende
- `kern/team.config.sh` — alle Projektwerte an einer Stelle, von `team-lib.sh`
  gesourct; Ordnerpfade werden zentral auf genau einen Schrägstrich normalisiert
- `bootstrap/` — CLAUDE.md-Vorlage (aus der LLM-Wiki-Vorlage erzeugt, ohne
  Aufnahme-Interview, Platzhalter gefüllt), CHANGELOG mit leerem `[Unreleased]`,
  Beutebuch **mit Vorlage-Block**, Roadmap, Backlog, Ledger, `.gitignore`-Fragment
- 25 Regressionstests der Team-Infrastruktur (127 Testfälle)

### Changed — gegenüber dem Feldprojekt
- **Parametrisierung**: 32 harte Projektbezüge in `ralph.sh`, `frank.sh`,
  `axel.sh`, `redteam.sh` lesen jetzt aus `team.config.sh` statt `site/` und
  `python3 scripts/smoke_test.py` fest zu verdrahten. `team-lib.sh`, `kosten.py`,
  `beutebuch.py`, `vollautomatik.sh`, `halbautomatik.sh` und `team-status.sh`
  waren bereits projektfrei und blieben **wörtlich unverändert**.
- Neue Helfer in `team-lib.sh`: `team_allowed_tools <rolle>` baut die
  Werkzeug-Allowlist aus der Konfiguration; `SMOKE_ZEILE`/`SMOKE_SUFFIX` machen
  einen fehlenden Smoke-Test im Prompt sichtbar, statt ihn still zu übergehen.
- `tests/test_bl29_ledger_domaene_rolle.py` — die Prüfung „Ledgersumme > 0"
  überspringt ein leeres Ledger. In einem frischen Projekt ist es leer; sobald
  die erste Kaskade geledgert ist, greift die volle Prüfung wieder.
- `tests/test_bl55_kostenmessung.py` — prüft die BL-55-Regel jetzt inhaltlich
  (Closeout + Verbot + Stufenbezug) statt einen wörtlichen Satz der
  Feldprojekt-CLAUDE.md, und normalisiert Markdown-Hervorhebungen.

### Fixed — Defekte, die nur in einem frischen Projekt auftreten
- **`ralph.sh` brach ohne jede Meldung ab, wenn `.ralph-plan` fehlte.**
  `head` auf eine fehlende Datei liefert RC≠0 und riss unter `set -e -o pipefail`
  den Loop weg, **bevor** die erklärende Fehlermeldung erreicht wurde — der
  Anwender sah einen blanken Exit 1. Im Feldprojekt existierte die Zeiger-Datei
  seit Kaskade 1, deshalb ist das nie aufgefallen; beim allerersten Start eines
  neuen Projekts ist die fehlende Datei der Normalfall.
- **`team_plan_datei()` hatte denselben Defekt**, obwohl die Funktionsdoku
  ausdrücklich „kein Abbruch hier" zusagte. Betraf `team_ralph_cap` und
  `team_budget_empfehlung` und damit `halbautomatik.sh` und `team-status.sh`.

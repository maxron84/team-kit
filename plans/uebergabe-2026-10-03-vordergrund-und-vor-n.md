# Übergabe 2026-10-03 — bash-Maschine an die pwsh-Maschine

**Lies das vor dem Zusammenführen.** Diese Datei liegt auf dem Zweig
`bl232-234-vordergrund-und-vor-n` und **nicht** auf `master`. Der Zweig trägt
fertige, geprüfte Arbeit mit **kollidierenden Nummern** — er ist absichtlich
nicht gepusht worden, wohin er nicht gehört.

## Lage

| | |
|---|---|
| Zweig | `bl232-234-vordergrund-und-vor-n` |
| Basis | `0af1347` — das war der `master` dieser Maschine, **78 Commits hinter `origin/master`** |
| Stand oben beim Schreiben | `84cc689` |
| Sicherung lokal | Zweig `sicherung-bl-vordergrund-vor-n`, derselbe Commit |
| `master` dieser Maschine | **unangetastet gelassen**, steht weiter auf dem Arbeitscommit; nichts gepusht |

Ein Rebase auf `origin/master` ist **angefangen und abgebrochen** worden, damit
hier kein halber Merge liegenbleibt. Die Konflikte sind unten namentlich
aufgeführt — sie sind echt, aber überschaubar.

## Der Fehler, der mitgeliefert wird: die Nummern sind belegt

Vergeben wurde gegen das **lokale** Archiv, und das war 78 Commits alt. `BL-232`
bis `BL-236` sind oben längst an andere Funde vergeben:

| hier | oben belegt für |
|---|---|
| `BL-232` | Virenschutz, Suite-Laufzeit und vierter Ausgang als EINE Kausalkette |
| `BL-233` | `.gitignore`-Vorlage kennt `.vollautomatik-state` nicht |
| `BL-234` | `zitat_lint.py` kennt nur `BL-`Nummern |
| `BL-235` | Laufzeit-Ausgaben nennen Kit-Nummern blank |
| `BL-236` | Rollback der Fixphase wirft fremde Commits weg |

Höchste oben belegte Nummer: **`BL-264`**. Freie Nummern beginnen also bei
`BL-265`. Das ist wörtlich der Fehler aus `BL-188`, und nach der Regel aus
`41b2ee0` zieht die **ungepushte** Seite um — das ist diese. **Umzubenennen
sind dabei nicht nur die Tabellenzeilen**, sondern auch die drei Testdateinamen,
ihre Kopfkommentare und die `BL-`Verweise in `kosten.py`, `lib.sh`, `lib.psm1`
und `regel-inventar.md`.

## Was von der Arbeit oben noch FEHLT — und was nicht

Nachgemessen an `origin/master`, nicht vermutet:

- **Fehlt oben: der Monitor.** `SMOKE_SUFFIX` und `SMOKE_ZEILE` verbieten dort
  `Hintergrund-Task` und `Wakeup`, aber **nicht den Monitor**. Genau diese
  Bauform stand im Feld wörtlich im `result` der Rolle (*„I'll hold here until
  the smoke-test MONITOR notifies me of completion"*) und hat 13,13 USD an
  einem Vormittag gekostet. Die vier Briefings nennen alle drei Bauformen, die
  beiden Laufzeit-Bausteine nur zwei — das ist der ganze Befund.
- **Fehlt oben: der `vor-N`-Riegel.** In `origin/master:geteilt/tools/kosten.py`
  gibt es keine Spur von `--auch-neuere`, `logs_nach_fenster_ende` oder einer
  Prüfung auf zu NEUE Logs. Die Meldung dazu liegt oben (`72646bc`), der Fix
  nicht. **Vorsicht:** Prüfe, ob dieser Meldung oben inzwischen eine eigene
  `BL-`Nummer zugeteilt wurde — dann ist das die Nummer, unter der der Fix
  hierher gehört, und keine neue.
- **Fehlt oben: die Zeiteinheit im BRIEFING.** Die vier Briefings sagen weiter
  nur *„erhöhe ich das Zeitlimit auf `TEAM_SMOKE_TEST_TIMEOUT` aus
  `{{KONFIG}}`"*, ohne Einheit.
- **Ist oben SCHON gebaut: die Zeiteinheit im Laufzeit-Baustein.** Als `BL-258`,
  fast im selben Wortlaut (*„viele Werkzeuge erwarten MILLISEKUNDEN — das wären
  `${TEAM_SMOKE_TEST_TIMEOUT}000`"*). **Die hiesige Hälfte davon ist
  überflüssig und gehört verworfen, nicht gemerget.** Verwandt und oben
  ebenfalls schon gemeldet: `d7b7e58` (*der Vordergrund-Rat setzt voraus, dass
  die Werkzeugfrist erhöhbar ist*).

## Die Konflikte, und wie sie aufzulösen sind

Der abgebrochene Rebase meldete sieben Dateien:

**Urteilssache — hier NICHT den hiesigen Text übernehmen:**

- `bash/lib.sh`, `pwsh/lib.psm1` — **oben ist die Grundlage, nicht hier.**
  Upstreams `SMOKE_SUFFIX` trägt inzwischen den `TEAM_GATE_DATEI`-Satz
  (`BL-256`) **und** die Millisekunden-Klausel (`BL-258`); beides fehlt hier.
  Wer den hiesigen Text drüberlegt, löscht zwei fremde Fixes. Richtig ist: den
  Upstream-Text nehmen und **nur** die dritte Bauform einsetzen — aus
  *„NIEMALS als Hintergrund-Task und kein Wakeup darauf"* wird *„NIEMALS als
  Hintergrund-Task, als Monitor oder mit einem Wakeup darauf"*. Beide Bahnen
  wortgleich halten, `test_bl112_prompt_gleichstand.py` prüft das.

**Buchhaltung — mechanisch, aber gegen den oberen Stand neu zu schreiben:**

- `plans/backlog.md`, `plans/backlog-archiv.md` — die hiesigen Zeilen und der
  `Stand`-Abschnitt sind mit den neuen Nummern neu einzusetzen; die
  `Stand:`-Zeile des Archivs zählt oben anders.
- `CHANGELOG.md` — die vier hiesigen Einträge umnummerieren, den
  `BL-233`-Absatz streichen (siehe oben) und in den `Unreleased`-Block oben
  einhängen.
- `README.md`, `doku/einrichtung.md` — **die hiesigen Zahlen sind falsch für
  den oberen Stand.** Oben stehen schon `1405` Fälle, `146` Testdateien,
  `202` Dateien (`8ece79d`); hier `1362` / `142` / `198`. Nach dem Merge **neu
  messen**, nicht rechnen: Installation in ein Wegwerf-Repo, dort zählen, dann
  `geteilt/kit-readme-pruefen.py --faelle N --testdateien N --dateien N`.
  Dazu die Backlog-Zahlen (Archivgröße, höchste Nummer, offene Einträge).

**Sauber automatisch zusammengegangen** (kein Konflikt, aber gegenlesen):
`bootstrap/CLAUDE.md.vorlage`, `doku/regel-inventar.md`,
`geteilt/prompts/rolle-harry.md`, `geteilt/prompts/rolle-marv.md`,
`geteilt/tools/kosten.py`. `rolle-ralph.md`, `rolle-axel.md`,
`bash/entry/team-status.sh` und `pwsh/entry/team-status.ps1` hat oben niemand
angefasst — die hiesige Fassung gilt.

> **Eine Stelle, die beim Gegenlesen Zeit spart:** Oben haben `rolle-harry.md`
> und `rolle-marv.md` ihren Beutezug-Dreisatz geändert (`BL-254`), `ralph` und
> `axel` nicht. Die vier Briefings sind damit nicht mehr durchgängig
> byte-gleich. Der hiesige Wächter vergleicht ausdrücklich **nur den
> Vordergrund-Absatz** und ist davon nicht betroffen — das war Absicht, nicht
> Glück.

## Was hier geprüft ist, und was nicht

**Geprüft** (auf dem alten Stand, bash-Bahn, Linux):

- `python3 -m pytest geteilt/tests -q` → 1188 passed, 192 skipped
- Suite in einer **frischen Installation** → 865 passed, **0 failed**
- `geteilt/kit-regelinventar.py` grün, `geteilt/kit-readme-pruefen.py` grün
- Der Feldfall von `vor-N` nachgespielt: Exit 1, Ledger leer, Archiv leer
- **Zehn Gegenproben gefahren, jede greift** — je Fix mindestens zwei, darunter
  „Monitor entfernen", „Umrechnung entfernen", „ein Briefing abweichend
  umformulieren", „Riegel abschalten", „Zeitspanne entfernen", „Schalter im
  Wrapper wegwerfen"

**Nicht geprüft, und das ist der Teil für die andere Maschine:**

- `bash bash/kit-test.sh` in voller Länge (rund 6 h) — **gar nicht gelaufen**
- **die ganze pwsh-Bahn** — kein PowerShell 7 auf diesem Wirt. Die Änderungen
  an `pwsh/lib.psm1` und `pwsh/entry/team-status.ps1` sind **nach Quelltext
  gespiegelt und nie ausgeführt**. Der Durchreiche-Testfall für `--auch-neuere`
  ist geschrieben und übersprungen.
- `test_bl173::test_bash_installer_findet_die_ide_gebuendelte_cli` ist auf
  diesem Wirt **dauerhaft rot** (keine IDE-gebündelte CLI vorhanden) — war es
  schon vor dieser Arbeit. Kein Befund am Kit.

## Der Wächter, der das hier erst nötig gemacht hat

`geteilt/tests/test_bl235_jede_meldung_bekommt_ihre_nummer.py` hält
`plans/meldungen/*.md` gegen die Verweise in Backlog und Archiv. Er ist der
Wächter, den der `Stand`-Eintrag vom 2026-09-03 nach acht liegengebliebenen
Meldungen wörtlich vorgeschlagen hatte; ohne ihn lagen die drei Meldungen
dieser Arbeit einen Monat.

Zwei Dinge daran gehören mit über:

1. **Sein erster Entwurf hat seine eigene Prämisse widerlegt.** Er nahm eine
   datierte Schwelle an („verlinkt wird seit dem 2026-08-27") und behauptete,
   sie sei gemessen. Der eigene Kontrollfall fiel sofort: vor dem Tag sind acht
   Meldungen verlinkt und dreizehn nicht. Statt der Schwelle steht eine
   **gefrorene Altlast** aus dreizehn Namen, die nur schrumpfen kann.
2. **Die Altlast ist gegen den oberen Stand neu zu messen.** Oben sind seit dem
   alten Stand viele Meldungen dazugekommen; die dreizehn Namen stimmen
   vielleicht nicht mehr. Der Wächter sagt es selbst, wenn man ihn dort fährt.

Die Nachverlinkung dieser dreizehn ist **offen** (hier als `BL-236` notiert,
Nummer ebenfalls umzuziehen) und bewusst nicht geraten: Eine Titelähnlichkeit
über die Archivzeilen liefert 50–87 % **auch für falsche Zeilen**, eindeutig
sind nur drei (`BL-192`, `BL-193`, `BL-197`). Eine falsche Herkunftsspur sieht
aus wie ein Beleg und zeigt woandershin — der Schaden, den `BL-188` für den
Nummernraum beschreibt.

## Kürzester Weg für die andere Maschine

1. `git fetch` und diesen Zweig auschecken.
2. Den `BL-233`-Anteil verwerfen (oben als `BL-258` erledigt).
3. Nummern ab `BL-265` neu vergeben — Tabellenzeilen, Testdateinamen,
   Kopfkommentare, Code-Verweise. Vorher prüfen, ob `72646bc` oben schon eine
   Nummer hat.
4. `bash/lib.sh` und `pwsh/lib.psm1` **aus dem oberen Stand** nehmen und nur
   den Monitor einsetzen.
5. Buchhaltung neu schreiben, README-Zahlen **messen**.
6. `kit-test.ps1` und `kit-test.sh` fahren — erst dann ist die pwsh-Hälfte
   dieser Arbeit mehr als eine Behauptung.

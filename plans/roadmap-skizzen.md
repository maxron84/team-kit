# Roadmap-Skizzen — T.E.A.M.-Starterkit

Ungehärtete Stränge für die Weiterentwicklung **des Kits selbst**. Ziel, grober
Umfang, Bezug, offene Fragen — **ohne** Stufennummern, **ohne** Cap
(Kaskaden-Planungsregel 1).

> **Nicht verwechseln:** `bootstrap/roadmap-skizzen.md` ist die **Vorlage**, die
> der Installer in Zielprojekte kopiert. Diese Datei hier ist die Roadmap des
> Kits. `install.sh` liest ausschließlich aus `bootstrap/` — dieser Ordner
> landet in keiner Installation.

**Quelle der meisten Stränge:** das Feldprojekt
`~/Source/team-kit_project_platformer`, Kaskade 1 (2026-08-01). Dort ist das Kit
zum ersten Mal scharf über eine volle Kaskade gelaufen, und genau dort fielen die
Fehler auf, die kein Kit-Test finden konnte.

---

## Skizze A: Das Kit kann sich selbst nicht prüfen

- **Ziel**: Ein Befehl im Kit-Repo sagt verlässlich, ob das Kit heil ist.
- **Stand**: Es gibt keinen. `python3 -m pytest team/tests` im Kit-Repo ergibt
  **17 Fehlschläge von 138** — sämtlich aus derselben Ursache: Die Tests setzen
  die **installierte** Ablage voraus (`team-status.sh`, `ralph.sh`, `axel.sh`,
  `vollautomatik.sh`, `CLAUDE.md`, `team.config.sh` **in der Wurzel**), während
  sie im Kit unter `entry/` bzw. `bootstrap/` liegen. Kein Testfall ist rot,
  weil etwas kaputt wäre.
- **Bezug**: Das ist die Ursache hinter der Ursache von `BL-1`. Das Kit hat
  heute **genau einen** verlässlichen Prüfweg: in ein Wegwerf-Projekt
  installieren und dort `./team-test.sh` laufen lassen — von Hand, ohne
  Zwang, und für 2.0.0–2.2.0 offenkundig nicht getan. Ein Fix, der im Kit
  committet wird, ist bis zur nächsten Feldinstallation ungeprüft.
- **Umfang**: So klein wie möglich. Ein Skript im Kit-Repo, das in ein
  temporäres Git-Repo installiert (`install.sh --nicht-interaktiv`), dort
  `./team-test.sh` fährt und dessen Exit-Code durchreicht. Kein zweiter
  Testbaum, keine Duplikate — die 138 Tests bleiben, wo sie sind, und werden
  dort ausgeführt, wo sie gelten: in der Installation.
- **Offene Fragen**:
  - Bleibt es beim „installiere und prüfe" — oder sollen die Tests zusätzlich
    layout-agnostisch werden (Entrypoint-Pfad aus einer Variablen)? Ersteres
    prüft mehr (den Installer gleich mit), Letzteres läuft schneller.
  - Gehört der Lauf zusätzlich in eine Git-Hook/CI, oder reicht die Disziplin
    „vor jedem Release"?
  - Der Guard-Test darf laut `README.md` nur in Wegwerf-Repos laufen — ein
    `mktemp -d`-Repo ist genau das, aber die Regel sollte im Skript stehen.

---

## Skizze B: Die Kostenerfassung ist strukturell unvollständig

- **Ziel**: Nach einem Closeout stehen **alle** Kosten einer Kaskade im
  committeten Ledger — und ein zweiter Abschluss kann nichts stillschweigend
  vernichten.
- **Stand**: Zwei bestätigte Kit-Fehler, beide im Feld real eingetreten und dort
  nur **von Hand** repariert (`BL-4`, `BL-5` — Details im
  [Backlog](backlog.md)). Kurz:
  - **`BL-4`**: Ralphs Baukosten landen **nie** im Ledger. `--rollen-abschluss`
    ledgert ausschließlich `.team-logs`; für `.ralph-logs` existiert
    `team_logs_archivieren()` ([team/lib.sh:799](../team/lib.sh#L799)) — von
    **keinem** Skript aufgerufen. Der Gesamtstand stimmt heute nur, solange
    `.ralph-logs` liegen bleibt, und dieser Ordner ist `.gitignore`t. Ein
    frischer Clone verliert die gesamte Bau-Kostenhistorie — also genau das,
    wogegen das Ledger gebaut wurde. Im Feld: 2,1621 USD von 9,4204 USD.
  - **`BL-5`**: `rollen_abschluss()` **ersetzt** die `roles`-Zeile derselben
    Kaskade ([team/tools/kosten.py:574](../team/tools/kosten.py#L574)),
    gezählt werden aber nur die **noch nicht archivierten** Logs. Weil der
    erste Aufruf archiviert hat, schreibt ein Nachlauf *weniger* und löscht den
    alten Wert. Im Feld reproduziert: 1,0969 wurde durch 2,4114 ersetzt.
- **Bezug**: Beide Fehler treffen **jede** Installation, nicht nur das
  Feldprojekt. Sie sind leise: Der gedruckte Abschlussbericht bestätigt sie,
  weil er aus derselben Quelle liest — dasselbe Muster wie bei `BL-1`.
- **Umfang**: Werkzeug **und** Regel. Ein Fix nur im Code reicht bei `BL-4`
  nicht: Solange die Kaskadenabschluss-Pflicht in `bootstrap/CLAUDE.md.vorlage`,
  `bootstrap/TEAM.md` und `team/prompts/rolle-architekt.md` nur
  `--rollen-abschluss` und `--akteur-abschluss` nennt, trägt niemand Ralph nach.
- **Offene Fragen**:
  - **`BL-4`**: eigener `--ralph-abschluss`, oder soll `--rollen-abschluss`
    Ralph gleich mit erledigen? Letzteres ist ein Befehl weniger im Closeout,
    vermischt aber zwei Rollen in einer Zeile und verliert die Trennung
    Bau ↔ Sweep/Fix, die das Ledger heute sauber führt. **Strippenzieher-
    Entscheid nötig.**
  - **`BL-5`**: Das Ersetzen ist **kein Versehen** — es ist laut Docstring
    gewollt, damit ein abgebrochener Abschluss wiederholbar bleibt. Der
    gefährliche Fall ist nur „ersetzen, **nachdem** archiviert wurde".
    Drei Wege: (a) addieren statt ersetzen, (b) abbrechen mit Hinweis, wenn
    schon eine Zeile steht, (c) erkennen, ob seit der bestehenden Zeile
    archiviert wurde, und nur dann abbrechen. (c) ist am genauesten und am
    teuersten. **Entscheid nötig, bevor gehärtet wird.**
  - Braucht es einen Ledger-Konsistenzcheck (`--ledger-pruefen`), der solche
    Lücken meldet, statt sie erst im nächsten Closeout auffallen zu lassen?

---

## Skizze C: Der Rückkanal Feld → Kit ist Handarbeit

- **Ziel**: Ein Fund, der im Feld als Kit-Fehler erkannt wird, geht nicht
  verloren, wenn niemand daran denkt.
- **Stand**: `BL-2` (die Rückmeldung von `BL-1`) hat funktioniert, weil sie im
  Feld-Backlog stand und jemand sie gelesen hat. `BL-4` und `BL-5` sind
  **beide** ausdrücklich als Kit-Fehler markiert („Fix gehört ins Kit") und
  lagen bis heute trotzdem nur im Feldprojekt — im Kit existierte bis zu dieser
  Sitzung weder ein Backlog noch eine Roadmap.
- **Umfang**: Klein und prosalastig. Eine feste Stelle im Kit (dieses
  `plans/backlog.md`), ein Satz in der Vorlage, der Feld-Architekten sagt, wohin
  Kit-Funde gehen, und ggf. eine Statuszeile „ans Kit gemeldet: ja/nein".
- **Bezug**: Ohne den Kanal skaliert das Kit nicht über zwei Feldprojekte
  hinaus — die teuersten Funde entstehen definitionsgemäß dort, nicht hier.
- **Offene Fragen**: Reicht die Konvention, oder braucht es Werkzeug? **Nach
  der Architekten-Feldlehre gehört diese Skizze nicht in den Loop** — reine
  Prosa-Arbeit, kostet dort etwa das Doppelte einer Code-Stufe.

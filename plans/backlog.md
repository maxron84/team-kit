# Backlog — T.E.A.M.-Starterkit

Aufgaben am **Kit selbst**, die keine eigene Kaskade rechtfertigen: kleine
Verbesserungen, technische Schulden, Rückmeldungen aus Feldprojekten.

> **Nicht verwechseln:** `bootstrap/backlog.md` ist die **Vorlage** für
> Zielprojekte. Diese Datei ist der Backlog des Kits.

**Nummernraum**: `BL-n` ist historisch gewachsen und wird zwischen Ursprungs-
projekt (`website-maxron-de`), Kit und Feldprojekten geteilt. `BL-1`…`BL-5`
tragen hier dieselbe Bedeutung wie im Feldprojekt
`team-kit_project_platformer`, damit die Spur lesbar bleibt. Neue kit-eigene
Funde ab `BL-6`.

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-1 | `beutebuch.py` löste die Projektwurzel eine Ebene zu hoch auf — die Fixphase übersprang still jeden übergebenen Fund | Feld K1 → Kit | **erledigt** (Release 2.2.1, Commit `e2966f4`) |
| BL-2 | `BL-1` ans Kit zurückmelden | Feld K1 | **erledigt** (ebd.) |
| BL-3 | Werkzeug-Tests deckten nur `--pfad`-Fixtures ab, Default-Pfade waren ungeprüft; `kosten.py` auf dieselbe Lücke prüfen | Feld K1 → Kit | **erledigt** — Audit: `kosten.py` hat den Fehler nicht (keine `__file__`-Ableitung); die tragende `cd`-Invariante ist jetzt getestet (`test_bl3_werkzeug_default_pfade.py`) |
| BL-4 | **Ralphs Baukosten landen nie im committeten Ledger.** `--rollen-abschluss` ledgert laut Docstring ausschließlich `.team-logs` (Harry/Marv/Frank/Axel). Für `.ralph-logs` existiert `team_logs_archivieren()` in [team/lib.sh:799](../team/lib.sh#L799), wird aber **von keinem Skript aufgerufen** — im gesamten Kit gibt es keinen Aufrufer. Der Gesamtstand stimmt nur, solange `.ralph-logs` liegen bleibt; der Ordner ist per `bootstrap/gitignore.fragment` ignoriert. Ein frischer Clone verliert die gesamte Bau-Kostenhistorie. Betrifft **jede** Installation. Im Feld K1: 2,1621 USD von 9,4204 USD ungeledgert, von Hand nachgetragen | Feld K1 → Kit, im Kit-Code verifiziert 2026-08-01 | **offen** — Code **und** Regel (Closeout-Pflicht nennt Ralph nirgends). Siehe [Skizze B](roadmap-skizzen.md), Entscheid offen: eigener `--ralph-abschluss` vs. Erweiterung von `--rollen-abschluss` |
| BL-5 | **`--rollen-abschluss` ersetzt still, statt zu addieren.** `rollen_abschluss()` ([team/tools/kosten.py:574](../team/tools/kosten.py#L574)) ersetzt die `roles`-Zeile derselben Kaskade; gezählt werden nur die **noch nicht archivierten** Logs. Da der erste Aufruf per `--archivieren` archiviert hat, schreibt ein Nachlauf einen *kleineren* Wert und löscht den alten. Wer nach dem Kostenabschluss noch eine Rolle laufen lässt und erneut abschließt, verliert den alten Wert kommentarlos. Im Feld live reproduziert (1,0969 wurde durch 2,4114 ersetzt); Korrektur nur von Hand | Feld K1 → Kit, im Kit-Code verifiziert 2026-08-01 | **offen** — Vorsicht: Das Ersetzen ist laut Docstring **beabsichtigt** (Wiederholbarkeit eines abgebrochenen Abschlusses). Nur „ersetzen nach dem Archivieren" ist der Fehler. Drei Fixwege in [Skizze B](roadmap-skizzen.md), Entscheid offen |
| BL-6 | **Die 138 Kit-Tests laufen im Kit-Repo nicht.** `python3 -m pytest team/tests` ergibt hier 17 Fehlschläge — alle aus einer Ursache: Die Tests setzen die installierte Ablage voraus (Entrypoints in der Wurzel), im Kit liegen sie unter `entry/`/`bootstrap/`. Kein echter Regressionsfund. Folge: Ein im Kit committeter Fix ist bis zur nächsten Feldinstallation ungeprüft — die Ursache hinter der Ursache von `BL-1` | Architekt-Sitzung 2026-08-01 | **offen** — siehe [Skizze A](roadmap-skizzen.md) |
| BL-7 | `README.md`, Abschnitt „Grenzen", ist überholt: „Noch nicht gelaufen: … inklusive Frank und Axel." Frank ist inzwischen scharf gelaufen (Feld K1, Fixes `506a8af`, `53142ec`, `cf16462` für `HM-1`…`HM-3`) — allerdings nach dem `BL-1`-Fix und außerhalb der `vollautomatik.sh`-Fixphase. Für **Axel** stimmt die Aussage weiter. Präzisieren statt streichen | Architekt-Sitzung 2026-08-01 | **offen**, klein — reine Doku |

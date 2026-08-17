# Backlog — T.E.A.M.-Starterkit

Aufgaben am **Kit selbst**, die keine eigene Kaskade rechtfertigen: kleine
Verbesserungen, technische Schulden, Rückmeldungen aus Feldprojekten.

> **Nicht verwechseln:** `bootstrap/backlog.md` ist die **Vorlage** für
> Zielprojekte. Diese Datei ist der Backlog des Kits.

**Nummernraum**: `BL-n` ist historisch gewachsen und wird zwischen Ursprungs-
projekt (`website-maxron-de`), Kit und Feldprojekten geteilt. `BL-1`…`BL-5`
tragen hier dieselbe Bedeutung wie im Feldprojekt
`team-kit_project_platformer`, damit die Spur lesbar bleibt. Neue kit-eigene
Funde ab `BL-6`. Verweise auf den Backlog eines **anderen** Projekts werden
`Kit-BL-<N>` geschrieben (`BL-50`).

> **Abgetragene Einträge stehen im Archiv:**
> [`backlog-archiv.md`](backlog-archiv.md). Dort liegt die vollständige
> Begründung jedes erledigten Punktes — sie wird nachgeschlagen, nicht
> mitgelesen. Diese Datei trägt nur, woran noch Arbeit hängt (`BL-53`).

**Stand 2026-08-17: ein offener Eintrag** (`BL-111`). Die zuletzt abgetragenen
(`BL-53`, `BL-62`, `BL-108`, `BL-109`, `BL-110`) stehen mit voller Begründung
im Archiv.

| Nr | Was | Woher | Status |
|---|---|---|---|
| BL-111 | **Die `head -1`-Absicherung in `team_architekt_kaskade` trägt gegen `set -e`, aber nicht gegen `set -o pipefail` — und der Kommentar darüber behauptet die breitere Zusicherung.** [team/lib.sh:1145-1151](../team/lib.sh#L1145-L1151) beendet die Pipeline mit `\| head -1`, und der Kommentar begründet das wörtlich mit *„head -1 haelt den RC auch bei leerem grep-Ergebnis auf 0 — unter set -e darf ein Projekt ohne erkennbare Kaskade den Aufrufer nicht wegreissen."* Das stimmt für `set -e` und ist unter `set -o pipefail` **wirkungslos**: Dort bestimmt der erste fehlschlagende Teil den Status der Pipeline, also der leere `grep` (rc 1), egal was `head` zurückgibt. Gemessen an einem Wegwerf-Repo ohne erkennbare Kaskadennummer: `set -e` → `rc=0 wert=[]`, `set -eu` → `rc=0 wert=[]`, `set -euo pipefail` → **rc=1, Abbruch, keine Ausgabe**. **Heute latent, nicht live:** Einziger Aufrufer ist [entry/team-status.sh:86](../entry/team-status.sh#L86) (`kaskade="$(team_architekt_kaskade)"`), und `team-status.sh` setzt keine strikten Optionen. Aber **alle** bauenden und prüfenden Rollen laufen mit `set -euo pipefail` (`ralph.sh`, `frank.sh`, `axel.sh`, `harry.sh`, `marv.sh`, `redteam.sh`) — die erste Rolle, die diese Funktion in einer Kommandosubstitution aufruft, oder ein `set -euo pipefail` in `team-status.sh`, macht daraus einen harten Abbruch bei jedem Projekt mit **benannter** statt nummerierter Kaskade (`plans/roles-post-k13.md`). Dieselbe Bauart wie `BL-15`/`BL-17`: Die Absicherung existiert, deckt aber den Fall nicht, den ihr Kommentar behauptet. **Gleiche Prüfung wert:** `team_bau_notiz` und `team_plan_datei` leiten ebenfalls aus derselben Plandatei ab | Kit, 2026-08-17 — beim Bau der Doppelbahn ([plans/windows-nativ.md](windows-nativ.md), Stufe 1) aufgefallen: Der neue Harnisch fährt Folgen mit voller Strenge, und der bis dahin nur gegen `set -e` gefahrene Test fiel | **offen.** Bewusst nicht in Stufe 1 mitgefixt — die Stufe sichert zu, den Bash-Zweig **nicht** anzutasten, und ein Verhaltensfix wäre genau das. Der Test [test_bl18_architekt_zeile_beschriftung.py](../team/tests/test_bl18_architekt_zeile_beschriftung.py) nennt seither ausdrücklich `strikt="abbruch"` als die Stufe, für die die Zusicherung gilt, statt die breitere zu behaupten. **Fix-Skizze:** `\|\| true` hinter die Pipeline oder die Ableitung nach Python ziehen (`kosten.py`/`beutebuch.py` haben dieselbe Aufgabe schon); danach den Test auf `strikt=True` heben — das ist die Gegenprobe |

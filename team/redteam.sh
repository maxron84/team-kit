#!/usr/bin/env bash
# redteam.sh — gemeinsame Sweep-Logik für Harry & Marv (Read-Only Red Team).
# Wird NICHT direkt aufgerufen, sondern von harry.sh / marv.sh gesourct,
# nachdem diese ROLLE und AUFTRAG gesetzt haben.
#
# Eiserne Regel (siehe CLAUDE.md): kein Produktivcode. Schreibrechte nur auf
# tests/ und plans/ — dreifach abgesichert (Prompt, --allowedTools, Post-Guard).
# Der Angreifer committet NICHT selbst; dieses Skript committet die
# Beutebuch-/Test-Änderungen deterministisch als docs(beute): …
#
# State: .<rolle>-state = zuletzt geprüfter Commit-Hash. Angriff nur auf
# STABILEN Code (neue Commits seit State) — idealerweise am Kaskaden-Übergang.
# Exit: 0 = gearbeitet · 3 = nichts Neues zu prüfen · 1 = Fehler/Guard-Bruch
#       42 = Session-Limit — Sweep pausiert (kein Fehler, State steht)
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh
team_lock "$ROLLE" || exit 1

STATE_FILE=".${ROLLE}-state"
LOG_DIR=".team-logs"; mkdir -p "$LOG_DIR"
WHITELIST="$TEAM_WHITELIST_REDTEAM"

HEAD_HASH="$(git rev-parse HEAD)"
LAST="$( [ -f "$STATE_FILE" ] && cat "$STATE_FILE" || echo "" )"
if [ "$LAST" = "$HEAD_HASH" ]; then
    echo "[$ROLLE] Kein neuer Commit seit letztem Sweep ($HEAD_HASH) — nichts zu tun."
    exit 3
fi

RANGE_DESC="$( [ -n "$LAST" ] && echo "Commits $LAST..$HEAD_HASH" || echo "gesamte bisherige Historie" )"
echo "=== $ROLLE: Sweep über $RANGE_DESC ==="
OUT="$LOG_DIR/${ROLLE}-$(date +%Y%m%d-%H%M%S).json"
NEXT_ID="$($TEAM_BEUTEBUCH_TOOL next-id)"

if [ -n "${TEAM_REDTEAM_FOCUS:-}" ]; then
    SCOPE_LINE="Prüfe den STABILEN Code im folgenden Fokus-Bereich ($RANGE_DESC): $TEAM_REDTEAM_FOCUS"
else
    SCOPE_LINE="Prüfe den STABILEN Code der App unter ${TEAM_PRODUKTIVCODE} ($RANGE_DESC)."
fi

PROMPT="$(team_briefing "$ROLLE")

Auftrag: $AUFTRAG
$SCOPE_LINE

EISERNE REGEL: Du änderst NIEMALS Produktivcode (${TEAM_PRODUKTIVCODE}**). Schreiben NUR unter
${TEAM_TEST_ORDNER} (Reproducer, klar als xfail/Skip markiert) und ${TEAM_PLAN_ORDNER}. Du committest NICHT.

Führe KEINE Reproducer/Skripte aus und stelle KEINE Rückfrage zum Ausführen —
du bist strikt read-only (der Guard erzwingt das ohnehin). Dokumentiere
Reproschritte ALS TEXT, statt sie laufen zu lassen.

Jeder Fund kommt ins Beutebuch ${TEAM_BEUTEBUCH} — hänge unter '## Funde' einen
Block an (nächste freie Nummer beginnt bei $NEXT_ID):
### HM-<Nr> — <Kurztitel>
- **Angreifer**: ${ROLLE^}
- **Schweregrad**: kritisch|hoch|mittel|klein
- **Status**: an Frank übergeben
- **Reproschritte**: 1. … 2. …
- **Erwartung**: …
- **Realität**: …

Was in ${TEAM_TEST_ORDNER} liegen bleibt, braucht einen Namen und einen Fund
(BL-47): Ein Hilfs-/Sondenskript ohne zugehörigen Fund LÖSCHST du wieder,
bevor du fertig meldest — oder du benennst es als Reproducer nach seinem Fund
(test_hm<Nr>_<stichwort>). Eine namenlose Datei im Test-Ordner wird nie wieder
gelesen, ist von keinem Fundblock referenziert und fällt trotzdem unter die
Zusicherungen des Projekts.

Findest du NICHTS, ändere keine Datei.
Beende IMMER mit exakt: <promise>REDTEAM_SWEEP_COMPLETE</promise> — AUCH WENN
du einen Fund ins Beutebuch geschrieben hast; das Promise ist die
Sweep-Quittung, nicht der Fund-Beleg."

ALLOWED_TOOLS="$(team_allowed_tools redteam)"
team_guard_begin
RC=0
team_claude "$ROLLE" "$TEAM_MODEL_LOOP" "$OUT" "$PROMPT" \
    --permission-mode default \
    --allowedTools "$ALLOWED_TOOLS" \
    || RC=$?

# Linie 3: harte Durchsetzung der Read-Only-Grenze (chirurgisch). Läuft AUF
# JEDEM Pfad — auch 42-Pause und generischer Fehler (HM-18): team_claude ist
# kein atomarer Vorgang, Teil-Session-Seiteneffekte können bereits VOR einem
# Abbruch im Arbeitsverzeichnis liegen und müssen auch dann zurückgesetzt werden.
# BL-16 Ebene 2: Der Übergriff wird hier NICHT mehr sofort in einen Fehlschlag
# übersetzt — das Urteil fällt unten, wenn die Sweep-Quittung geprüft ist.
# Zurückgerollt und gemeldet hat team_guard_verify bereits.
GUARD_UEBERGRIFF=0
if ! team_guard_verify "$ROLLE" "$WHITELIST"; then
    GUARD_UEBERGRIFF=1
fi

if [ "$RC" -eq 42 ]; then
    # HM-27: der Guard oben resettet nur Pfade AUSSERHALB der Whitelist — ein
    # bereits geschriebener Beutebuch-Eintrag/Reproducer INNERHALB tests/|plans/
    # bliebe sonst als impliziter, nie verifizierter Fortschritt liegen. Analog
    # zu frank.sh (Zeile 68) vor dem exit 42 verwerfen.
    echo "[$ROLLE] Session-Limit — Sweep pausiert (Reset: ${TEAM_LAST_RESET:-unbekannt}). Kein Fehler, $STATE_FILE bleibt unverändert; halbfertige ${TEAM_TEST_ORDNER}/${TEAM_PLAN_ORDNER}-Seiteneffekte werden verworfen." >&2
    git reset --hard "$HEAD_HASH" >/dev/null
    git clean -fd -- "$TEAM_TEST_ORDNER" "$TEAM_PLAN_ORDNER" >/dev/null
    exit 42
elif [ "$RC" -ne 0 ]; then
    echo "[$ROLLE] Aufruf fehlgeschlagen." >&2
    exit 1
fi

# Budget: Harry/Marv sind read-only (nichts Bezahltes geht durch einen Abbruch
# verloren) → sofortiger Hard-Cap beim zentralen Soft-Cap-Wert, KEIN Soft-Fenster
# (team_budget_check ohne hard-limit; Strippenzieher-Entscheid 2026-07-12, HM-32).
# Vor diesem Fix hatte redteam.sh GAR KEINEN Budget-Check — die Sweep-Kosten
# wurden nur angezeigt, nie gedeckelt.
ROLLE_BUDGET_USD="${ROLE_BUDGET_USD:-${TEAM_ROLE_BUDGET_USD}}"
BUDGET_RC=0
team_budget_check "$TEAM_LAST_COST" "$ROLLE_BUDGET_USD" "${ROLLE^} Sweep" || BUDGET_RC=$?
if [ "$BUDGET_RC" -ge 2 ]; then
    echo "[$ROLLE] Budget-Hard-Cap überschritten — Abbruch (read-only, kein Datenverlust; $STATE_FILE bleibt unverändert)." >&2
    exit 1
fi

if ! team_promise_in "$TEAM_LAST_OUT" "REDTEAM_SWEEP_COMPLETE"; then
    # Defensiv (Stufe 23, BL-16): Der Aufruf ist an dieser Stelle garantiert
    # NICHT is_error (team_claude hätte sonst schon oben abgebrochen), und ein
    # etwaiger Übergriff ausserhalb tests/|plans/ ist bereits zurückgerollt
    # (über sein Urteil entscheidet team_guard_urteil unten). Fehlt trotzdem das
    # Promise, zählt ein sauberer NEUER Beutebuch-Eintrag als erfolgreicher
    # Sweep — der Dreisatz (Fund im Beutebuch) ist die eigentliche Quittung, das
    # Promise nur eine (hier fehlende) Zusatzbestätigung.
    NEUER_FUND=0
    [ -n "$(git status --porcelain -- "$TEAM_BEUTEBUCH")" ] && NEUER_FUND=1
    [ "$($TEAM_BEUTEBUCH_TOOL next-id)" != "$NEXT_ID" ] && NEUER_FUND=1

    if [ "$NEUER_FUND" -eq 0 ]; then
        echo "[$ROLLE] Kein Sweep-Promise und kein neuer Fund — Log prüfen: $TEAM_LAST_OUT" >&2
        exit 1
    fi
    echo "[$ROLLE] WARNUNG: Sweep ohne Promise, aber sauberer Fund übergeben — als Erfolg gewertet; Prompt-Härtung siehe Stufe 23. Log: $TEAM_LAST_OUT" >&2
fi

# BL-16 Ebene 2: Das Ergebnis des Sweeps ist die Quittung — Promise oder (oben
# ersatzweise anerkannt) ein sauberer neuer Fund. Wer hier ankommt, hat sie
# geliefert; ein Guard-Übergriff kassiert dann den Übergriff, nicht den Sweep.
if ! team_guard_urteil "$ROLLE" "$GUARD_UEBERGRIFF" 1; then
    exit 1
fi

# BL-47 (Feld K29, 2026-08-10): Das ERGEBNIS zählen, nicht die Absicht
# behaupten. Ein Marv-Sweep über 9 Minuten und 3,14 USD committete eine einzige
# Sondendatei und keine Beutebuch-Zeile — Commit-Botschaft trotzdem „neue
# Funde/Reproducer", Protokollzeile „Funde committet. Übergabe an Frank."
# Damit ist „geprüft, nichts gefunden" von „nie fertig geworden" nicht mehr zu
# unterscheiden: Beides kostet gleich viel und sieht identisch aus. Die Zahl
# liegt vor — NEXT_ID vor dem Sweep gegen next-id danach —, sie wurde nur nie
# ausgewertet. Bei einer read-only-Rolle gibt es weder State-Wechsel noch
# Produktivdiff, an dem der Unterschied sonst auffiele.
NEXT_ID_NACHHER="$($TEAM_BEUTEBUCH_TOOL next-id)"
NEUE_FUNDE=$(( ${NEXT_ID_NACHHER#HM-} - ${NEXT_ID#HM-} ))
[ "$NEUE_FUNDE" -lt 0 ] && NEUE_FUNDE=0
if [ "$NEUE_FUNDE" -eq 1 ]; then
    FUND_TEXT="1 neuer Fund"
elif [ "$NEUE_FUNDE" -gt 1 ]; then
    FUND_TEXT="$NEUE_FUNDE neue Funde"
else
    FUND_TEXT="keine neuen Funde"
fi

# Whitelist-Änderungen deterministisch committen (der Angreifer selbst darf nicht).
echo "$HEAD_HASH" > "$STATE_FILE"
if [ -n "$(git status --porcelain -- "$TEAM_BEUTEBUCH" "$TEAM_TEST_ORDNER")" ]; then
    git add "$TEAM_BEUTEBUCH" "$TEAM_TEST_ORDNER"
    git commit -q -m "docs(beute): ${ROLLE^}-Sweep über $RANGE_DESC — $FUND_TEXT" || true
    if [ "$NEUE_FUNDE" -eq 0 ]; then
        # Der benannte Fall: geprüft, nichts gefunden — committet sind nur
        # Testdateien. Nicht "Funde committet", das war die Lüge im Feld.
        echo "[$ROLLE] Geprüft, KEINE neuen Funde ($TEAM_LAST_COST USD) — committet sind nur ${TEAM_TEST_ORDNER}-Dateien. Keine Übergabe an Frank."
    else
        echo "[$ROLLE] $FUND_TEXT committet ($TEAM_LAST_COST USD). Übergabe an Frank."
    fi
else
    echo "[$ROLLE] Geprüft, keine neuen Funde ($TEAM_LAST_COST USD). Sauber, nichts zu committen."
fi
exit 0

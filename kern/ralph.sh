#!/usr/bin/env bash
# ralph.sh — der headless Bau-Loop (Rolle "Ralph", siehe CLAUDE.md).
# Arbeitet den aktiven Kaskaden-Plan Stufe für Stufe ab, ein Commit pro Stufe.
#
# Aufruf:   ./ralph.sh            (oder über ./vollautomatik.sh als Phase 1)
# Env:      RALPH_BUDGET_USD  Budget pro Stufe (Default TEAM_ROLE_BUDGET_USD=5,
#                             sofortiger Hard-Cap — Ralph committet als letzten
#                             Schritt und hat danach ohnehin Feierabend, ein
#                             gesprengtes Budget stoppt VOR dem State-Weiterschalten)
#           TEAM_MODEL_LOOP   Modell (Default sonnet)
#           AUTH_MODE         api|abo (siehe team-lib.sh)
# Exit:     0 = Kaskade fertig/Cap erreicht · 1 = Fehler
#           42 = Session-Limit — Stufe pausiert (kein Fehler, State steht),
#                siehe team_claude()/CLAUDE.md „Loop-Mechanik & Auth"
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=team-lib.sh
source ./team-lib.sh
team_lock ralph

# PLAN_DATEI: der aktive, ausgehärtete Kaskaden-Plan. Zeigt der Strippenzieher
# per Zeiger-Datei .ralph-plan (eine Zeile, Pfad) auf den jeweils freigegebenen
# Plan — Umschalten auf die nächste Kaskade ist damit ein Einzeiler:
#   echo plans/ralph-kaskade-N-….md > .ralph-plan
PLAN_ZEIGER=".ralph-plan"
# Starterkit-Fix: `head` auf eine fehlende Datei liefert RC!=0 und riss unter
# `set -e -o pipefail` den ganzen Loop weg, BEVOR die Fehlermeldung unten kam —
# ein blanker Exit 1 ohne jeden Hinweis. Im Feldprojekt existierte .ralph-plan
# seit Kaskade 1, deshalb fiel das nie auf; in einem frischen Projekt ist die
# fehlende Datei der NORMALFALL beim allerersten Start.
PLAN_DATEI="$( { head -n1 "$PLAN_ZEIGER" 2>/dev/null || true; } | tr -d '[:space:]')"
if [ -z "$PLAN_DATEI" ] || [ ! -f "$PLAN_DATEI" ]; then
    echo "FEHLER: Kein aktiver Plan gesetzt: echo ${TEAM_PLAN_ORDNER}… > $PLAN_ZEIGER" >&2
    exit 1
fi

# RALPH_CAP: höchste freigegebene Stufe. Steht als 'RALPH_CAP=<zahl>'-Zeile im
# Kopf des aktiven Plans (Setzt DER ARCHITEKT bei der Aushärtung der jeweils
# nächsten Kaskade) — einzige Quelle, keine Doppelpflege in diesem Skript.
RALPH_CAP="$(grep -E '^[[:space:]]*RALPH_CAP=' "$PLAN_DATEI" | head -1 | cut -d= -f2 | tr -d '[:space:]')"
if [ -z "$RALPH_CAP" ] || ! [ "$RALPH_CAP" -eq "$RALPH_CAP" ] 2>/dev/null; then
    echo "FEHLER: Keine gültige RALPH_CAP=-Zeile in $PLAN_DATEI." >&2
    exit 1
fi

# Sofortiger Hard-Cap beim zentralen Soft-Cap-Wert (kein Soft-Fenster für Ralph):
# team_budget_check wird OHNE hard-limit aufgerufen, ein überschrittenes Limit
# liefert RC 2 und stoppt den Lauf VOR dem State-Weiterschalten (kein Rollback,
# der Commit der Stufe bleibt — der Mensch schaltet manuell weiter).
RALPH_BUDGET_USD="${RALPH_BUDGET_USD:-${TEAM_ROLE_BUDGET_USD}}"
STATE_FILE=".ralph-state"
LOG_DIR=".ralph-logs"
mkdir -p "$LOG_DIR"

while true; do
    STUFE="$(head -n1 "$STATE_FILE" | tr -d '[:space:]')"
    if [ -z "$STUFE" ] || ! [ "$STUFE" -eq "$STUFE" ] 2>/dev/null; then
        echo "FEHLER: $STATE_FILE enthält keine gültige Stufennummer." >&2
        exit 1
    fi
    if [ "$STUFE" -gt "$RALPH_CAP" ]; then
        echo "Ralph: Stufe $STUFE liegt über RALPH_CAP=$RALPH_CAP — Feierabend."
        exit 0
    fi

    echo "=== Ralph: Stufe $STUFE (Plan: $PLAN_DATEI, Budget: $RALPH_BUDGET_USD USD) ==="
    OUT="$LOG_DIR/stufe-$STUFE-$(date +%Y%m%d-%H%M%S).json"

    PROMPT="$(team_briefing ralph)

Aufgabe: Setze AUSSCHLIESSLICH Stufe $STUFE aus $PLAN_DATEI um.

Regeln:
1. Lies vor Beginn den [Unreleased]-Block in ${TEAM_CHANGELOG} — dort gelistete
   Fixes NICHT erneut bauen.
2. Keine Features aus späteren Stufen vorwegnehmen.
3. ${SMOKE_ZEILE}
4. Genau EIN Commit: '${TEAM_FEAT_PRAEFIX}(stufe$STUFE): <kurzbeschreibung>'.
5. NUR wenn Umsetzung + Verifikation der Stufe vollständig erfüllt sind,
   beende deine Antwort mit exakt: <promise>STUFE_${STUFE}_COMPLETE</promise>
   Andernfalls beschreibe, was fehlt, und gib das Promise NICHT aus."

    RC=0
    team_claude ralph "$TEAM_MODEL_LOOP" "$OUT" "$PROMPT" \
        --permission-mode bypassPermissions || RC=$?
    if [ "$RC" -eq 42 ]; then
        echo "Ralph: Session-Limit — Stufe $STUFE pausiert (Reset: ${TEAM_LAST_RESET:-unbekannt}). Kein Fehler, $STATE_FILE bleibt auf $STUFE. Bitte später erneut starten." >&2
        exit 42
    elif [ "$RC" -ne 0 ]; then
        exit 1
    fi

    echo "Ralph: Stufe $STUFE hat $TEAM_LAST_COST USD gekostet."
    RC=0
    # Ralph: OHNE hard-limit aufrufen → sofortiger Hard-Cap. RC>=2 (Soft-Cap
    # überschritten) ist für Ralph der harte Fall: Stopp VOR dem State-
    # Weiterschalten (Commit der Stufe bleibt, kein Rollback; Mensch schaltet
    # manuell weiter, ggf. mit erhöhtem RALPH_BUDGET_USD).
    team_budget_check "$TEAM_LAST_COST" "$RALPH_BUDGET_USD" "Ralph Stufe $STUFE" || RC=$?
    if [ "$RC" -ge 2 ]; then
        exit 1
    fi
    # RC=1 (Warnschwelle): weitermachen ist erlaubt, die Meldung steht im Log.

    if team_promise_in "$TEAM_LAST_OUT" "STUFE_${STUFE}_COMPLETE"; then
        NEXT=$((STUFE + 1))
        echo "$NEXT" > "$STATE_FILE"
        echo "Ralph: Promise erhalten — Stufe $STUFE abgeschlossen, weiter mit $NEXT."
    else
        echo "Ralph: KEIN Promise für Stufe $STUFE — Loop stoppt. Log prüfen: $TEAM_LAST_OUT" >&2
        exit 1
    fi
done

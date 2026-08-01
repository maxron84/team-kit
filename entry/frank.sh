#!/usr/bin/env bash
# frank.sh — Frank der Fixer als Event-Loop am Beutebuch.
# Greift EINEN Fund mit Status 'an Frank übergeben', fixt ihn nach Franks
# Dreisatz (Commit fix(uat) → CHANGELOG → Beutebuch-Status). Ein Fund pro Aufruf.
#
# Frank DARF Produktivcode ändern (kein Read-Only-Guard) — statt dessen
# Dreisatz-Verifikation nach dem Aufruf.
#
# Versuchszähler .frank-attempts (transient): ab TEAM_FRANK_MAX_VERSUCHE (3)
# Fehlversuchen wird der Fund auf 'an Axel übergeben' gesetzt.
# Exit: 0 = gefixt · 3 = kein offener Fund für Frank · 1 = Fehlversuch
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh
team_lock frank || exit 1

# Zwei-Schwellen-Modell (Strippenzieher-Entscheid 2026-07-12, HM-32): Frank ist
# ein iterierendes "Sorgenkind" — ein Soft-Cap-Überlauf ist bei einem normalen
# Fix NICHT ungewöhnlich und darf NICHT die bereits bezahlte Arbeit per Rollback
# wegwerfen (der alte 1-USD-Cap tat genau das und war ökonomisch absurd). Erst
# der HARD-Cap (Ausreißer) bricht mit Rollback+Cleanup ab.
FRANK_BUDGET_USD="${ROLE_BUDGET_USD:-${TEAM_ROLE_BUDGET_USD}}"
FRANK_HARDCAP_USD="${ROLE_HARDCAP_USD:-${TEAM_ROLE_HARDCAP_USD}}"
MAX_VERSUCHE="${TEAM_FRANK_MAX_VERSUCHE:-3}"
LOG_DIR=".team-logs"; mkdir -p "$LOG_DIR"
ATTEMPTS_FILE=".frank-attempts"

# Frank arbeitet Funde ab, die entweder frisch an ihn gingen ODER von Axel mit
# Fix-Plan zurückkamen. 'Fix-Plan liegt vor' hat Vorrang (Axel hat vorgedacht).
HM="$($TEAM_BEUTEBUCH_TOOL first 'Fix-Plan liegt vor' \
      || $TEAM_BEUTEBUCH_TOOL first 'an Frank übergeben')" || {
    echo "[frank] Kein Fund mit Status 'an Frank übergeben' / 'Fix-Plan liegt vor' — nichts zu tun."
    exit 3
}

# Versuchszähler für genau diesen Fund führen (Format: "HM-N COUNT").
gelesen_hm="" ; gelesen_n=0
if [ -f "$ATTEMPTS_FILE" ]; then read -r gelesen_hm gelesen_n < "$ATTEMPTS_FILE" || true; fi
if [ "$gelesen_hm" = "$HM" ]; then VERSUCH=$((gelesen_n + 1)); else VERSUCH=1; fi

echo "=== Frank: $HM (Versuch $VERSUCH/$MAX_VERSUCHE, Budget $FRANK_BUDGET_USD USD) ==="
OUT="$LOG_DIR/frank-${HM}-v${VERSUCH}-$(date +%Y%m%d-%H%M%S).json"
START_HASH="$(git rev-parse HEAD)"

# Fokus-Zeile (HM-29): analog zu Harry/Marv (TEAM_REDTEAM_FOCUS, BL-15) fest
# "Code-Fix unter site/" vorzuschreiben ist für Infra-Kaskaden (Team-Skripte
# statt site/) sachlich falsch — der Prompt widersprach bislang der Realität
# der laufenden Kaskade. Ist TEAM_REDTEAM_FOCUS gesetzt (Strippenzieher-Schalter
# derselben Kaskade), übernimmt Frank denselben Fokus statt der site/-Fixierung.
SCHRITT1="Code-Fix unter ${TEAM_PRODUKTIVCODE} umsetzen.${SMOKE_SUFFIX}"
if [ -n "${TEAM_REDTEAM_FOCUS:-}" ]; then
    SCHRITT1="Code-Fix im Fokus-Bereich dieser Kaskade umsetzen (${TEAM_REDTEAM_FOCUS}). Betrifft der Fix ${TEAM_PRODUKTIVCODE}, zusätzlich:${SMOKE_SUFFIX}"
fi

PROMPT="$(team_briefing frank)

Behebe GENAU den Fund $HM aus ${TEAM_BEUTEBUCH} (lies dessen Reproschritte).
Falls zu $HM eine Ermittlungsakte unter ${TEAM_ERMITTLUNGSAKTEN}/ existiert (Axel
hat einen Fix-Plan hinterlegt), folge diesem Plan.

Franks Dreisatz — alle drei Schritte sind PFLICHT:
1. $SCHRITT1
2. Genau EIN Commit: '${TEAM_FIX_PRAEFIX}: <was+warum> ($HM)'.
3. ${TEAM_CHANGELOG} unter '## [Unreleased]' → '### Fixes' den Fix eintragen (Was+Warum)
   UND den Beutebuch-Status setzen:
   $TEAM_BEUTEBUCH_TOOL set $HM 'erledigt (Frank-Fix, <commit-kurzhash>)'
   (Den CHANGELOG-/Status-Edit im selben oder einem Folge-Commit 'docs: …' sichern.)

Schaffst du einen sauberen Fix inkl. Dreisatz, beende mit exakt:
<promise>FRANK_FIX_COMPLETE</promise>
Sonst gib das Promise NICHT aus und beschreibe das Hindernis."

RC_CLAUDE=0
team_claude frank "$TEAM_MODEL_LOOP" "$OUT" "$PROMPT" \
    --permission-mode bypassPermissions || RC_CLAUDE=$?

echo "Frank: $HM Versuch $VERSUCH kostete $TEAM_LAST_COST USD."

# Session-Pause (Exit 42, HM-24): kein inhaltlicher Fehlversuch — Frank kam nie
# zum Zug, also weder Rollback noch Versuchszähler noch Axel-Eskalation. Die
# Pause wird unverändert an vollautomatik.sh durchgereicht.
if [ "$RC_CLAUDE" -eq 42 ]; then
    echo "[frank] Session-Limit — Fix pausiert (Reset: ${TEAM_LAST_RESET:-unbekannt}). Kein Fehlversuch, Zähler unverändert." >&2
    git reset --hard "$START_HASH" >/dev/null; git clean -fd >/dev/null
    exit 42
fi

# Zwei-Schwellen-Prüfung (mit hard-limit): RC 0/1 = ok/Warnschwelle,
# RC 2 = SOFT-Cap überschritten (nur Hinweis, Fix bleibt gültig und wird normal
# geprüft — KEIN Rollback, KEIN Fehlversuch), RC 3 = HARD-Cap überschritten
# (echter Ausreißer → Rollback+Cleanup+Zähler wie beim gescheiterten Dreisatz,
# das ist das HM-30-Verhalten, aber jetzt NUR beim Hard-Cap).
RC=0
team_budget_check "$TEAM_LAST_COST" "$FRANK_BUDGET_USD" "Frank $HM" "$FRANK_HARDCAP_USD" || RC=$?
BUDGET_GESPRENGT=0
if [ "$RC" -eq 2 ]; then
    echo "[frank] Soft-Cap überschritten ($TEAM_LAST_COST USD ≥ $FRANK_BUDGET_USD USD) — kein Abbruch, Fix wird normal geprüft (Hard-Cap $FRANK_HARDCAP_USD USD)." >&2
elif [ "$RC" -ge 3 ]; then
    echo "[frank] HARD-Cap gesprengt ($TEAM_LAST_COST USD ≥ $FRANK_HARDCAP_USD USD) — Abbruch mit Rollback." >&2
    BUDGET_GESPRENGT=1
fi

# Erfolg = Promise + IRGENDEIN neuer fix(uat)-Commit im Bereich + Status erledigt.
# (Frank darf den CHANGELOG-/Status-Edit laut Prompt in einen 'docs:'-Folgecommit
#  legen — deshalb NICHT verlangen, dass HEAD selbst fix(uat) ist, sondern nur,
#  dass START_HASH..HEAD einen fix(uat)-Commit enthält.)
# Ein gesprengtes Budget (HM-30) prüfen wir gar nicht erst auf Erfolg — inhaltlich
# ist das immer ein Fehlversuch und fällt direkt in denselben Rollback+Zähler-Pfad
# wie ein gescheiterter Dreisatz, statt (wie zuvor) über 'exit 1' daran vorbei zu
# laufen und dabei weder aufzuräumen noch den Versuchszähler fortzuschreiben.
if [ "$BUDGET_GESPRENGT" -eq 0 ]; then
    NEUER_STATUS="$($TEAM_BEUTEBUCH_TOOL list | awk -v h="$HM" -F'\t' '$1==h{print $2}')"
    if team_promise_in "$TEAM_LAST_OUT" "FRANK_FIX_COMPLETE" \
       && [ "$(git rev-parse HEAD)" != "$START_HASH" ] \
       && git log "$START_HASH..HEAD" --pretty=%s | grep -qF "$TEAM_FIX_PRAEFIX" \
       && printf '%s' "$NEUER_STATUS" | grep -q "erledigt" \
       && team_diff_beruehrt_fund "$HM" "$START_HASH"; then
        rm -f "$ATTEMPTS_FILE"
        echo "[frank] $HM erledigt (Dreisatz verifiziert)."
        exit 0
    fi
fi

# Fehlversuch: aufräumen, zählen, ggf. an Axel eskalieren. git clean OHNE
# Pfad-Einschränkung (HM-29): Frank läuft mit bypassPermissions und kann daher
# auch AUSSERHALB von site/ neue, nie committete Dateien anlegen — ein auf
# "-- site/" verengter Cleanup ließ solche Altlasten bislang einen gescheiterten
# Versuch überleben (respektiert .gitignore, .team-logs/.ralph-logs u. Ä. bleiben
# unangetastet).
echo "[frank] $HM Versuch $VERSUCH gescheitert (Budget/Promise/Commit/Dreisatz/Substanzbezug unvollständig) — Rollback." >&2
git reset --hard "$START_HASH" >/dev/null; git clean -fd >/dev/null
printf '%s %s\n' "$HM" "$VERSUCH" > "$ATTEMPTS_FILE"

if [ "$VERSUCH" -ge "$MAX_VERSUCHE" ]; then
    $TEAM_BEUTEBUCH_TOOL set "$HM" "an Axel übergeben"
    git add "$TEAM_BEUTEBUCH"
    git commit -q -m "docs(beute): $HM nach $VERSUCH Frank-Versuchen an Axel übergeben"
    rm -f "$ATTEMPTS_FILE"
    echo "[frank] $HM nach $MAX_VERSUCHE Versuchen an Axel eskaliert."
fi
exit 1

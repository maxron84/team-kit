#!/usr/bin/env bash
# axel.sh — Axel Foley, Read-Only Forensiker, automatisch gerufen.
# Nimmt EINEN Fall mit Status 'an Axel übergeben', erstellt eine Ermittlungsakte
# unter plans/ermittlungsakten/ (Root-Cause + Fix-Plan) und gibt an Frank zurück
# (Status → 'Fix-Plan liegt vor'). Ein Fall pro Aufruf.
#
# Read-Only wie das Red Team: darf NUR plans/ schreiben (Guard Linie 3).
# Axel denkt, Frank tippt. Startet NIE von selbst im Dauer-Loop — nur ein Fall.
#
# Modell: TEAM_MODEL_STRONG (Default opus; 'fable'/'claude-fable-5' möglich).
# Strippenzieher-Entscheid 2026-07-10: Auth auch bei Axel Abo-first + API-Fallback.
# Exit: 0 = Akte erstellt · 3 = kein Axel-Fall · 1 = Fehler/Guard-Bruch
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh
team_lock axel || exit 1

# Zwei-Schwellen-Modell (Strippenzieher-Entscheid 2026-07-12, HM-32): Axel ist
# wie Frank ein iterierendes "Sorgenkind". Soft-Cap = nur Hinweis (die Akte bleibt
# gültig, wenn sie bereits bezahlt ist); erst der Hard-Cap bricht ab.
AXEL_BUDGET_USD="${AXEL_BUDGET_USD:-${TEAM_ROLE_BUDGET_USD}}"
AXEL_HARDCAP_USD="${AXEL_HARDCAP_USD:-${TEAM_ROLE_HARDCAP_USD}}"
LOG_DIR=".team-logs"; mkdir -p "$LOG_DIR"
WHITELIST="$TEAM_WHITELIST_AXEL"

HM="$($TEAM_BEUTEBUCH_TOOL first "an Axel übergeben")" || {
    echo "[axel] Kein Fall mit Status 'an Axel übergeben' — nichts zu tun."
    exit 3
}

echo "=== Axel: Ermittlung zu $HM (Modell $TEAM_MODEL_STRONG, Budget $AXEL_BUDGET_USD USD) ==="
OUT="$LOG_DIR/axel-${HM}-$(date +%Y%m%d-%H%M%S).json"
AX_NR="$(find "$TEAM_ERMITTLUNGSAKTEN" -name 'AX-*.md' 2>/dev/null | wc -l | awk '{print $1+1}')"
START_HASH="$(git rev-parse HEAD)"

# BL-52: derselbe Prüfumfang wie beim Red Team — was Harry und Marv angreifen
# dürfen, muss Axel lesen dürfen und trotzdem tabu bleiben.
AXEL_TABU="${TEAM_PRODUKTIVCODE}**"
[ -n "${TEAM_WEITERER_CODE:-}" ] && AXEL_TABU="${TEAM_PRODUKTIVCODE}** und ${TEAM_WEITERER_CODE}"

# BL-51: Der Plan-Ordner ist Axels EINZIGE Schreibzone; in einer gewachsenen
# Codebasis liegt dort fremdes Eigentum, auf das der Guard nicht anschlägt.
AXEL_BESTAND=""
if [ -n "${TEAM_PLAN_ORDNER_BESTAND:-}" ]; then
    AXEL_BESTAND="
BESTAND — NICHT DEIN EIGENTUM: In ${TEAM_PLAN_ORDNER} lagen beim Einzug des Teams
schon fremde Dateien (${TEAM_PLAN_ORDNER_BESTAND}). Du legst dort NUR NEUE Dateien an
und änderst oder löschst nichts, was du nicht selbst angelegt hast — auch nicht,
was in dieser Aufzählung fehlt. Der Guard lässt dich hier gewähren.
"
fi

PROMPT="$(team_briefing axel)

Knacke den Fall $HM aus ${TEAM_BEUTEBUCH}, an dem Frank gescheitert ist.

EISERNE REGEL: Read-only. Du änderst NUR ${TEAM_PLAN_ORDNER} — NIEMALS ${AXEL_TABU}. Du fixst NICHTS
und committest NICHT. Du lieferst eine Ermittlungsakte, Frank setzt sie um.
${AXEL_BESTAND}

Lege ${TEAM_ERMITTLUNGSAKTEN}/AX-${AX_NR}.md an:
# AX-${AX_NR} — <Titel> (Bezug: $HM)
## Root-Cause
<tiefe Ursachenanalyse — warum tritt der Fehler wirklich auf>
## Warum Franks Versuche scheiterten
<konkret>
## Schrittweiser Fix-Plan
1. … 2. … (so präzise, dass Frank es 1:1 umsetzen kann)

Setze danach den Status zurück an Frank:
$TEAM_BEUTEBUCH_TOOL set $HM 'Fix-Plan liegt vor'

Beende mit exakt: <promise>AXEL_CASE_COMPLETE</promise>"

ALLOWED_TOOLS="$(team_allowed_tools axel)"
team_guard_begin
RC=0
team_claude axel "$TEAM_MODEL_STRONG" "$OUT" "$PROMPT" \
    --permission-mode default \
    --allowedTools "$ALLOWED_TOOLS" \
    || RC=$?

# Linie 3: harte Durchsetzung der Read-Only-Grenze (chirurgisch). Läuft AUF
# JEDEM Pfad — auch 42-Pause und generischer Fehler (HM-18/HM-23): team_claude
# ist kein atomarer Vorgang, Teil-Session-Seiteneffekte können bereits VOR
# einem Abbruch im Arbeitsverzeichnis liegen und müssen auch dann zurückgesetzt werden.
# BL-16 Ebene 2: Der Übergriff wird hier NICHT mehr sofort in einen Fehlschlag
# übersetzt — das Urteil fällt unten, wenn feststeht, ob die Ermittlung geliefert
# wurde. Zurückgerollt und gemeldet hat team_guard_verify bereits.
GUARD_UEBERGRIFF=0
if ! team_guard_verify axel "$WHITELIST"; then
    GUARD_UEBERGRIFF=1
fi

if [ "$RC" -eq 42 ]; then
    # HM-27: der Guard oben resettet nur Pfade AUSSERHALB der Whitelist — eine
    # bereits geschriebene, aber nie committete Ermittlungsakte/ein bereits
    # ausgeführter Statuswechsel INNERHALB plans/ blieben sonst als impliziter,
    # nie verifizierter Fortschritt liegen. Analog zu frank.sh (Zeile 68) vor
    # dem exit 42 verwerfen.
    echo "[axel] Session-Limit — Ermittlung pausiert (Reset: ${TEAM_LAST_RESET:-unbekannt}). Halbfertige ${TEAM_PLAN_ORDNER}-Seiteneffekte werden verworfen." >&2
    git reset --hard "$START_HASH" >/dev/null
    git clean -fd -- "$TEAM_PLAN_ORDNER" >/dev/null
    exit 42
elif [ "$RC" -ne 0 ]; then
    echo "[axel] Aufruf fehlgeschlagen." >&2
    exit 1
fi

echo "Axel: $HM kostete $TEAM_LAST_COST USD."
# Zwei-Schwellen-Prüfung (mit hard-limit): RC 2 = Soft-Cap überschritten (nur
# Hinweis, die Akte bleibt gültig und wird normal auf ihr Promise geprüft),
# RC 3 = Hard-Cap überschritten (echter Ausreißer → Abbruch). Der Guard (Linie 3)
# lief bereits oben auf JEDEM Pfad (HM-23), daher hier nur die RC-Auswertung.
BUDGET_RC=0
team_budget_check "$TEAM_LAST_COST" "$AXEL_BUDGET_USD" "Axel $HM" "$AXEL_HARDCAP_USD" || BUDGET_RC=$?
if [ "$BUDGET_RC" -eq 2 ]; then
    echo "[axel] Soft-Cap überschritten ($TEAM_LAST_COST USD ≥ $AXEL_BUDGET_USD USD) — kein Abbruch, Akte wird normal geprüft (Hard-Cap $AXEL_HARDCAP_USD USD)." >&2
elif [ "$BUDGET_RC" -ge 3 ]; then
    echo "[axel] HARD-Cap gesprengt ($TEAM_LAST_COST USD ≥ $AXEL_HARDCAP_USD USD) — Abbruch." >&2
    exit 1
fi

if ! team_promise_in "$TEAM_LAST_OUT" "AXEL_CASE_COMPLETE"; then
    echo "[axel] Kein Akten-Promise — Log prüfen: $TEAM_LAST_OUT" >&2
    exit 1
fi

# BL-16 Ebene 2: Das Ergebnis der Rolle ist die Akte UND der Statuswechsel.
# Liegen beide vor, zählt die Runde auch dann, wenn der Guard einen Übergriff
# kassieren musste — die Ermittlung ist geleistet.
AKTE="${TEAM_ERMITTLUNGSAKTEN}/AX-${AX_NR}.md"
STATUS_JETZT="$($TEAM_BEUTEBUCH_TOOL list | awk -F'\t' -v h="$HM" '$1==h{print $2}')"
ERGEBNIS=0
if [ -f "$AKTE" ] && [ "$STATUS_JETZT" = "Fix-Plan liegt vor" ]; then
    ERGEBNIS=1
fi
if ! team_guard_urteil axel "$GUARD_UEBERGRIFF" "$ERGEBNIS"; then
    echo "[axel] Akte vorhanden: $([ -f "$AKTE" ] && echo ja || echo nein) · Status $HM: ${STATUS_JETZT:-unbekannt}" >&2
    exit 1
fi

# Akte + Status-Update deterministisch committen (Axel selbst darf nicht).
if [ -n "$(git status --porcelain -- "$TEAM_PLAN_ORDNER")" ]; then
    git add "$TEAM_PLAN_ORDNER"
    git commit -q -m "docs(akte): AX-${AX_NR} zu $HM — Root-Cause + Fix-Plan für Frank"
fi
echo "[axel] Ermittlungsakte AX-${AX_NR} erstellt, $HM zurück an Frank ('Fix-Plan liegt vor')."
exit 0

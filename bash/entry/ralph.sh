#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: ralph.ps1
# ralph.sh — der headless Bau-Loop (Rolle "Ralph", siehe CLAUDE.md).
# Arbeitet den aktiven Kaskaden-Plan Stufe für Stufe ab, ein Commit pro Stufe.
#
# Aufruf:   ./ralph.sh            (oder über ./vollautomatik.sh als Phase 1)
# Env:      RALPH_BUDGET_USD  Budget pro Stufe (Default TEAM_ROLE_BUDGET_USD=5,
#                             sofortiger Hard-Cap — Ralph committet als letzten
#                             Schritt und hat danach ohnehin Feierabend, ein
#                             gesprengtes Budget stoppt VOR dem State-Weiterschalten)
#           TEAM_MODEL_LOOP   Modell (Default sonnet)
#           AUTH_MODE         api|abo (siehe team/lib.sh)
# Exit:     0 = Kaskade fertig/Cap erreicht · 1 = Fehler
#           42 = Session-Limit — Stufe pausiert (kein Fehler, State steht),
#                siehe team_claude()/CLAUDE.md „Loop-Mechanik & Auth"
#           43 = Stufe fertig, Quittung fehlt (BL-41): Das Log meldet Erfolg,
#                das Promise fehlt. Arbeit meist FERTIG — nicht neu bauen,
#                sondern prüfen und von Hand quittieren (Meldung nennt den Weg)
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh
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
    #
    # BL-60: Der EFFEKT des Caps bleibt unverändert — die MELDUNG kommt erst
    # nach der Quittungsprüfung. Vorher stieg der Cap mit `exit 1` aus, bevor
    # die BL-41-Erkennung überhaupt lief; eine Stufe, die beides tut (Cap
    # sprengen UND ohne Quittung enden), meldete sich als generischer „Fehler
    # (1)". Das ist kein Randfall: Eine lange Stufe ist teurer UND wartet eher
    # auf einen Hintergrund-Smoke-Test — die Verdeckung trifft bevorzugt die
    # teuren Stufen, bei denen ein unnötiger Neubau am meisten kostet. Im Feld
    # (K35) trat BL-41 dreimal in einer Kaskade auf; zweimal griff die
    # Erkennung vorbildlich, beim dritten Mal (11,09 USD) verdeckte sie der Cap.
    team_budget_check "$TEAM_LAST_COST" "$RALPH_BUDGET_USD" "Ralph Stufe $STUFE" || RC=$?
    CAP_GESPRENGT=0
    [ "$RC" -ge 2 ] && CAP_GESPRENGT=1
    # RC=1 (Warnschwelle): weitermachen ist erlaubt, die Meldung steht im Log.

    if team_promise_in "$TEAM_LAST_OUT" "STUFE_${STUFE}_COMPLETE"; then
        # Quittung liegt vor: Beim gesprengten Cap bleibt es beim heutigen
        # Verhalten — Stopp OHNE Weiterschalten, der Commit der Stufe bleibt.
        if [ "$CAP_GESPRENGT" -eq 1 ]; then
            exit 1
        fi
        NEXT=$((STUFE + 1))
        echo "$NEXT" > "$STATE_FILE"
        echo "Ralph: Promise erhalten — Stufe $STUFE abgeschlossen, weiter mit $NEXT."
    else
        # BL-41: Erst prüfen, ob der BENANNTE vierte Ausgang vorliegt (Sitzung
        # beendet, Log meldet Erfolg, Quittung fehlt) — sonst führt die
        # generische Meldung den Menschen in den Plan statt in den Fehlermodus.
        CAP_ZEILE="(Soft-Cap eingehalten.)"
        [ "$CAP_GESPRENGT" -eq 1 ] && CAP_ZEILE="ACHTUNG: Soft-Cap ebenfalls überschritten ($TEAM_LAST_COST USD ≥ $RALPH_BUDGET_USD USD) — beim Neustart RALPH_BUDGET_USD anheben, sonst stoppt die nächste Stufe genauso."
        # BL-61: Der dritte Ausgang. „Sonst neu bauen" warf zwei sehr
        # verschiedene Lagen zusammen — und im Feld hätte der Neubau 330 Zeilen
        # fertigen, korrekten Produktivcode weggeworfen (7,46 USD), weil die
        # von der Stufe SELBST geschriebenen Tests drei Aufbaufehler hatten.
        # Gleiches Modell, gleicher Prompt, gleiche Stufe: Der Neubau hätte sie
        # mit hoher Wahrscheinlichkeit erneut erzeugt.
        #
        # Vor der Meldung an den Menschen: die Prüfliste SELBST fahren
        # (team_quittung_selbstpruefung). Sie ist neunmal im Feld mit demselben
        # Ergebnis ausgegangen; besteht sie, quittiert der Loop selbst und
        # läuft weiter, statt die Vollautomatik mitten in der Kaskade
        # anzuhalten. Der gesprengte Cap schließt das aus — dort gilt
        # unverändert "Stopp VOR dem Weiterschalten", die Automatik darf eine
        # Budget-Entscheidung des Menschen nicht überschreiben.
        if [ "$CAP_GESPRENGT" -eq 0 ] \
            && team_result_meldet_erfolg "$TEAM_LAST_OUT" \
            && team_quittung_selbstpruefung ralph "$STUFE"; then
            # Committen, falls die Stufe ihre Arbeit uncommittet liegen ließ:
            # Ohne Commit liefe die nächste Stufe auf einem schmutzigen Baum,
            # und der Read-Only-Guard der Sweep-Phase sähe fremde Änderungen.
            if [ -n "$(git status --porcelain)" ]; then
                git add -A
                git commit -q -m "${TEAM_FEAT_PRAEFIX:-feat}(stufe$STUFE): Arbeit der Stufe $STUFE, automatisch gesichert

Die Sitzung endete als subtype=success ohne <promise> (BL-41, vierter
Ausgang) und ohne eigenen Commit. Die Selbstpruefung des Loops hat
Arbeit, Zusicherung (BL-135) und gruenen Smoke-Test bestaetigt und
quittiert die Stufe deshalb selbst. Betreff bewusst generisch: Der
Loop kennt den Inhalt der Stufe nicht - der Plan tut es."
                echo "Ralph: Stufe $STUFE war uncommittet — automatisch gesichert."
            fi
            NEXT=$((STUFE + 1))
            echo "$NEXT" > "$STATE_FILE"
            echo "Ralph: Quittung fehlte (BL-41), Selbstprüfung bestanden — Stufe $STUFE abgeschlossen, weiter mit $NEXT."
            continue
        fi
        if team_quittung_fehlt_melden ralph "$TEAM_LAST_OUT" \
            "Stufe $STUFE hat kein <promise>STUFE_${STUFE}_COMPLETE</promise> gegeben." \
            "git log -1 && git status — hat Ralph committet?" \
            "${TEAM_SMOKE_TEST:-(kein Smoke-Test konfiguriert)} — ist der Baum grün?" \
            "Beides ja: von Hand quittieren — \`echo $((STUFE + 1)) > $STATE_FILE\`, dann erneut starten." \
            "Baum ROT? Erst prüfen, WO: Sind ausschließlich die von DIESER Stufe neu angelegten Testdateien rot (\`git status\` zeigt sie als '??'), ist der Testaufbau der wahrscheinlichere Schuldige als der Produktivcode — dann den Aufbau von Hand reparieren, OHNE eine Zusicherung abzuschwächen, statt die Stufe neu zu bauen." \
            "Ist BESTEHENDER Testbestand rot, hat die Stufe etwas gebrochen: dann neu bauen." \
            "$CAP_ZEILE"; then
            exit 43
        fi
        echo "Ralph: KEIN Promise für Stufe $STUFE — Loop stoppt. Log prüfen: $TEAM_LAST_OUT" >&2
        exit 1
    fi
done

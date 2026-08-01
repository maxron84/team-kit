#!/usr/bin/env bash
# team-lib.sh — gemeinsame Bibliothek der T.E.A.M.-Rollen (siehe CLAUDE.md, Anhang A).
# Wird per `source` eingebunden, nicht direkt ausgeführt.

# --- Projekt-Konfiguration (T.E.A.M.-Starterkit) ------------------------------
# Alle projektspezifischen Werte stehen in team.config.sh. Sie wird ZUERST
# gesourct, damit die ${VAR:-default}-Zuweisungen unten sie stehen lassen.
# Fehlt die Datei, laufen die Rollen mit den Defaults dieser Bibliothek weiter —
# so bricht ein Lauf nie an einer fehlenden Konfigdatei ab (gleiche Logik wie
# der Pflicht-Fallback in team_briefing).
# lib.sh liegt in team/, team.config.sh eine Ebene darüber in der Repo-Wurzel.
if [ -f "$(dirname "${BASH_SOURCE[0]}")/../team.config.sh" ]; then
    # shellcheck source=../team.config.sh disable=SC1091
    source "$(dirname "${BASH_SOURCE[0]}")/../team.config.sh"
else
    echo "[team-lib] WARNUNG: team.config.sh fehlt — Bibliotheks-Defaults aktiv." >&2
fi

# --- Abgeleitete Prompt-Bausteine (Starterkit) --------------------------------
# Smoke-Test-Zeile für die bauenden Rollen. Ist kein Befehl konfiguriert, wird
# der Schritt AUSDRÜCKLICH als offener Punkt benannt, statt still zu
# verschwinden — sonst merkt niemand, dass das Sicherheitsnetz fehlt.
if [ -n "${TEAM_SMOKE_TEST:-}" ]; then
    SMOKE_ZEILE="Smoke-Test ausführen: ${TEAM_SMOKE_TEST} — muss grün sein."
    SMOKE_SUFFIX=" Smoke-Test grün: ${TEAM_SMOKE_TEST}."
else
    SMOKE_ZEILE="(Kein Smoke-Test konfiguriert — Schritt entfällt. Das Team arbeitet ohne Sicherheitsnetz; TEAM_SMOKE_TEST in team.config.sh nachtragen.)"
    SMOKE_SUFFIX=""
fi

# team_allowed_tools <redteam|axel>: Werkzeug-Allowlist für Guard-Linie 2.
# Axel bekommt NUR den Plan-Ordner, das Red Team zusätzlich den Test-Ordner.
team_allowed_tools() {
    local basis="Read Grep Glob Bash(${TEAM_BEUTEBUCH_TOOL}:*) Bash(git log:*) Bash(git diff:*) Bash(git show:*)"
    [ -n "${TEAM_SMOKE_TEST:-}" ] && basis="$basis Bash(${TEAM_SMOKE_TEST})"
    local plan="Edit(${TEAM_PLAN_ORDNER%/}/**) Write(${TEAM_PLAN_ORDNER%/}/**)"
    case "$1" in
        axel) echo "$basis $plan" ;;
        *)    echo "$basis $plan Edit(${TEAM_TEST_ORDNER%/}/**) Write(${TEAM_TEST_ORDNER%/}/**)" ;;
    esac
}

# --- Modelle -----------------------------------------------------------------
# Loop-Rollen (Ralph, Harry, Marv, Frank): günstiges Modell.
# Axel & Der Architekt: starkes Modell, immer API.
TEAM_MODEL_LOOP="${TEAM_MODEL_LOOP:-sonnet}"
TEAM_MODEL_STRONG="${TEAM_MODEL_STRONG:-opus}"

# --- Budget pro Rolle (Zwei-Schwellen-Modell) --------------------------------
# Strippenzieher-Entscheid 2026-07-12 (realer Auslöser HM-32): Ein zu tiefes
# Pro-Rolle-Budget ist ökonomisch absurd — der alte 1-USD-Frank-Cap griff ERST
# NACH dem (bereits bezahlten) Claude-Aufruf und warf über den Rollback die
# schon bezahlte Arbeit weg, der nächste Versuch kostete erneut: der Cap
# "sparte" nichts, er vervielfachte die Kosten und blockierte obendrein den Fund.
#
# Neues Modell — EINE zentrale Basiszahl statt drei divergierender Defaults:
#   TEAM_ROLE_BUDGET_USD   (Default 5) — Soft-Cap, gilt für ALLE Rollen.
#   TEAM_ROLE_HARDCAP_USD  (Default 10) — Hard-Cap für die iterierenden
#                          "Sorgenkinder" Frank & Axel (2× Soft).
#
# Zwei Schwellen (siehe team_budget_check):
#   - Frank & Axel: SOFT-Cap = nur deutlicher Hinweis, KEIN Rollback, der Fix
#     bleibt gültig und wird normal geprüft; erst der HARD-Cap (Ausreißer:
#     Endlosschleife/kaputter Prompt) bricht mit Rollback+Cleanup ab.
#   - Ralph/Harry/Marv: sofortiger HART-Cap beim Soft-Wert (kein Soft-Fenster) —
#     Ralph hat nach dem Commit ohnehin Feierabend (kein Rollback, Mensch
#     schaltet weiter), Harry/Marv sind read-only (nichts Bezahltes geht verloren).
TEAM_ROLE_BUDGET_USD="${TEAM_ROLE_BUDGET_USD:-5}"
TEAM_ROLE_HARDCAP_USD="${TEAM_ROLE_HARDCAP_USD:-10}"

# --- Auth-Modus --------------------------------------------------------------
# team_resolve_auth_mode [rollen-default]
#
# Auflösung (Prio absteigend):
#   1. Env AUTH_MODE            — explizite Übersteuerung pro Aufruf
#   2. ~/.config/claude-team/auth-mode  — maschinenlokaler Default
#   3. Rollen-Default ($1)      — Loop-Rollen übergeben "abo",
#                                 starke Rollen (Axel/Architekt) nichts → "api"
#
# "abo" = Claude-Abo via `claude login`. Der API-Key wird aus der Umgebung
#         entfernt, damit die CLI sicher über das Abo abrechnet.
# "api" = Pay-per-Use. Key-Quelle: Env ANTHROPIC_API_KEY, sonst
#         ~/.config/claude-team/api-key (eine Zeile, chmod 600).
#         Der Key gehört bewusst NICHT in .bashrc — sonst greifen ihn auch
#         interaktive Abo-Sessions auf.
# team_auth_mode_effektiv [rollen-default] — löst NUR den Modus auf
# (Env AUTH_MODE → ~/.config/claude-team/auth-mode → Rollen-Default) und gibt ihn
# auf stdout aus. KEINE Seiteneffekte (kein unset, kein Key-Laden). Erlaubt
# Orchestratoren (vollautomatik.sh/halbautomatik.sh), den effektiven Modus zu
# prüfen, ohne die Prozess-Umgebung anzufassen.
team_auth_mode_effektiv() {
    local rollen_default="${1:-api}"
    local cfg="$HOME/.config/claude-team/auth-mode"
    if [ -n "${AUTH_MODE:-}" ]; then
        printf '%s\n' "$AUTH_MODE"
    elif [ -f "$cfg" ]; then
        head -n1 "$cfg" | tr -d '[:space:]'
    else
        printf '%s\n' "$rollen_default"
    fi
}

# team_warnung_abo_key — warnt EINMAL pro Prozessbaum, wenn im Abo-Modus ein
# ANTHROPIC_API_KEY in der Umgebung liegt (das Abo-first-Design still aushebelt).
# Idempotent: setzt beim ersten Auslösen TEAM_ABO_KEY_WARNUNG_GEZEIGT=1
# (exportiert), sodass alle NACHKOMMEN-Prozesse schweigen. Damit „einmal pro
# Prozessbaum" auch über die SIBLING-Rollenprozesse von vollautomatik.sh/
# halbautomatik.sh hält (HM-32), seeden die Orchestratoren diese Funktion selbst
# EINMAL im eigenen Prozess — analog team_lock/TEAM_LOCK_HELD.
team_warnung_abo_key() {
    if [ -n "${ANTHROPIC_API_KEY:-}" ] \
        && [ "${TEAM_ABO_KEY_WARNUNG:-1}" != "0" ] \
        && [ "${TEAM_ABO_KEY_WARNUNG_GEZEIGT:-0}" != "1" ]; then
        echo "WARNUNG: AUTH_MODE=abo, aber ANTHROPIC_API_KEY liegt in der Prozess-Umgebung —" >&2
        echo "  die Claude-CLI kann dann den (teuren) API-Weg dem Abo vorziehen." >&2
        echo "  Empfohlen: den Key aus .bashrc/der Shell-Env nehmen und stattdessen in" >&2
        echo "  ~/.config/claude-team/api-key (chmod 600) ablegen — siehe CLAUDE.md 'Auth-Modi'." >&2
        echo "  Selbstprüfen: echo \"\${ANTHROPIC_API_KEY:+gesetzt}\" (leer = ok)." >&2
        export TEAM_ABO_KEY_WARNUNG_GEZEIGT=1
    fi
}

team_resolve_auth_mode() {
    local rollen_default="${1:-api}"
    local keyfile="$HOME/.config/claude-team/api-key"

    AUTH_MODE="$(team_auth_mode_effektiv "$rollen_default")"

    case "$AUTH_MODE" in
        api)
            if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
                if [ -r "$keyfile" ]; then
                    ANTHROPIC_API_KEY="$(head -n1 "$keyfile" | tr -d '[:space:]')"
                    export ANTHROPIC_API_KEY
                else
                    echo "FEHLER: AUTH_MODE=api, aber weder ANTHROPIC_API_KEY gesetzt noch $keyfile lesbar." >&2
                    return 1
                fi
            fi
            ;;
        abo)
            team_warnung_abo_key
            # Abo-Abrechnung erzwingen: API-Key aus der Umgebung nehmen.
            unset ANTHROPIC_API_KEY
            ;;
        *)
            echo "FEHLER: Unbekannter AUTH_MODE '$AUTH_MODE' (erlaubt: api|abo)." >&2
            return 1
            ;;
    esac
    echo "Auth-Modus: $AUTH_MODE"
}

# --- Zentraler Claude-Aufruf ---------------------------------------------------
# team_claude <rolle> <modell> <outfile> <prompt> [weitere claude-Flags …]
#
# Abo-first mit automatischem API-Fallback (Strippenzieher-Entscheid 2026-07-10:
# gilt für ALLE Rollen, auch Axel): Auth wird pro Aufruf frisch aufgelöst;
# scheitert der Abo-Aufruf (Exit ≠ 0 oder is_error), folgt genau EIN API-Retry.
# Nach dem Aufruf stehen TEAM_LAST_COST (USD) und TEAM_LAST_OUT (Log-Datei).
# TEAM_LAST_COST ist die Summe ALLER Versuche dieses Aufrufs (gescheiterter
# Abo-Versuch + API-Fallback + 429-Retries), nicht nur des letzten — sonst waere
# der Pro-Stufe-Budget-Cap durch einen teuren Fehlversuch umgehbar (BL-55).
# TEAM_LAST_OUT bleibt das FINALE Log (Promise-Pruefung, HM-20).
#
# Session-Limit (429, Kaskade 9 / Stufe 30, Strategie A+B; API-Fallback-Reihenfolge
# per Strippenzieher-Entscheid 2026-07-11 umgestellt, Commit f787936): Bei JEDEM
# Abo-Fehler — Timeout, normaler Fehler ODER 429/Session-Limit — versucht
# team_claude SOFORT den einmaligen API-Fallback (eigenes, separates Kontingent;
# hilft auch bei einem Abo-429). Erst wenn AUCH das finale (ggf. API-)Ergebnis
# noch ein 429 ist (team_result_is_429), greift die Warte-und-Wiederhol-Logik
# (A). Ist der Reset unbekannt, zu weit in der Zukunft, oder sind die Retries
# erschöpft, gibt team_claude ein eindeutiges Pausen-Signal zurück (B):
# Exit-Code 42, TEAM_LAST_PAUSE=1 und TEAM_LAST_RESET="HH:MM". Ein normaler
# (nicht-429) Fehler, der auch über API scheitert, endet mit Exit 1.
#
#   TEAM_429_MAX_RETRIES  Anzahl Warte-und-Wiederhol-Zyklen (Default 2).
#   TEAM_429_MAX_WARTEN   Harte Obergrenze der Wartezeit in Sekunden
#                         (Default 1800 = 30 Min); 0 schaltet A komplett ab
#                         (nur B, reiner Pausen-Exit).
#   TEAM_429_PUFFER       Sicherheitspuffer nach dem Reset-Zeitpunkt in
#                         Sekunden (Default 30).
#
# TEAM_DRY_RUN=1: kein echter Aufruf — schreibt ein Stub-JSON mit dem Inhalt
# von TEAM_DRY_RESULT (Default leer) für Mechanik-Tests der Pipeline.
TEAM_AUTH_USER="${AUTH_MODE:-}"
TEAM_429_MAX_RETRIES="${TEAM_429_MAX_RETRIES:-2}"
TEAM_429_MAX_WARTEN="${TEAM_429_MAX_WARTEN:-1800}"
TEAM_429_PUFFER="${TEAM_429_PUFFER:-30}"

# team_429_env_int <variablenname> <default>
# Erzwingt, dass die benannte TEAM_429_*-Variable eine reine, nicht-negative
# Ganzzahl ist, BEVOR sie in $(( … ))/[ … ] verwendet wird. Ein aus der
# Umgebung übernommener Wert wie "$(beliebiger Befehl)" würde in einer
# Bash-Arithmetik-Expansion sonst ausgeführt (Command-Injection, HM-17); ein
# nicht-numerischer Wert wie "abc" ließe `test` stillschweigend scheitern und
# den TEAM_429_MAX_WARTEN-Deckel fail-open statt fail-safe wirkungslos werden
# (ebenfalls HM-17). Bei ungültigem Wert: Fehlermeldung + Fallback auf Default.
team_429_env_int() {
    local name="$1" default="$2" wert
    eval "wert=\"\${$name}\""
    case "$wert" in
        ''|*[!0-9]*)
            echo "[team_claude] Ungültiger Wert für ${name}=\"${wert}\" (muss eine nicht-negative Ganzzahl sein) — falle auf Default ${default} zurück." >&2
            eval "$name=\"$default\""
            ;;
    esac
}
team_429_env_int TEAM_429_MAX_RETRIES 2
team_429_env_int TEAM_429_MAX_WARTEN 1800
team_429_env_int TEAM_429_PUFFER 30

# team_429_sleep <sekunden>
# Kapselt `sleep` fürs Warten auf einen Session-Limit-Reset. TEAM_DRY_RUN=1
# oder TEAM_429_SKIP_SLEEP=1 überspringen das echte Warten — so darf ein Test
# niemals real bis zu 30 Minuten blockieren (Verifikationspflicht Stufe 30).
team_429_sleep() {
    local sekunden="$1"
    if [ "${TEAM_DRY_RUN:-0}" = "1" ] || [ "${TEAM_429_SKIP_SLEEP:-0}" = "1" ]; then
        echo "[429] (Test) sleep ${sekunden}s übersprungen." >&2
        return 0
    fi
    sleep "$sekunden"
}

team_claude() {
    local rolle="$1" modell="$2" out="$3" prompt="$4"
    shift 4
    TEAM_LAST_PAUSE=0
    TEAM_LAST_RESET=""

    if [ "${TEAM_DRY_RUN:-0}" = "1" ]; then
        python3 - "$out" "${TEAM_DRY_RESULT:-}" <<'PY'
import json, sys
json.dump({"result": sys.argv[2], "total_cost_usd": 0.01, "is_error": False},
          open(sys.argv[1], "w"))
PY
        TEAM_LAST_COST="0.01"; TEAM_LAST_OUT="$out"
        echo "[$rolle] DRY-RUN — kein Claude-Aufruf."
        return 0
    fi

    AUTH_MODE="$TEAM_AUTH_USER"
    team_resolve_auth_mode abo || return 1

    local fehler=0 cli_exit=0
    # Alle Logs DIESES Aufrufs — auch die gescheiterten Vorversuche. TEAM_LAST_COST
    # ist die Summe darueber, nicht nur der letzte Versuch (BL-55).
    local -a versuch_logs=()
    claude -p "$prompt" --model "$modell" --output-format json "$@" > "$out" || cli_exit=1
    versuch_logs+=("$out")
    if team_bewerte_ergebnis "$rolle" "$out" "$cli_exit"; then fehler=0; else fehler=1; fi

    # Strippenzieher-Entscheid (2026-07-11): Bei JEDEM Abo-Fehler — egal ob
    # Timeout, normaler Fehler ODER 429/Session-Limit — SOFORT den API-Fallback
    # versuchen. Der API-Key hat ein eigenes, separates Kontingent (bewiesen
    # 2026-07-11: bei erschöpftem Abo-Kontingent liefert derselbe Prompt mit dem
    # Key erfolgreich `result:ok`), daher hilft der Fallback auch bei einem
    # Abo-429. Erst wenn AUCH der API-Weg scheitert, greift die 429-Warte-/
    # Retry-/Pausen-Logik weiter unten.
    #
    # WICHTIG (Bugfix 2026-07-11): Der Key wird dem `claude`-Aufruf EXPLIZIT als
    # Aufruf-lokales Environment vorangestellt (ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
    # claude …). Ein bloßes `export` über team_resolve_auth_mode reicht NICHT:
    # die CLI bevorzugte im selben Prozess weiterhin die (limitierte) Abo-Session
    # und ignorierte den frisch exportierten Key — der Fallback lief real erneut
    # ins Abo-429. Mit dem vorangestellten Key greift der API-Weg zuverlässig.
    if [ "$fehler" -eq 1 ] && [ "$AUTH_MODE" = "abo" ]; then
        echo "[$rolle] Abo-Aufruf fehlgeschlagen (Timeout/Limit/429?) — einmaliger API-Fallback. Log: $out"
        AUTH_MODE=api
        team_resolve_auth_mode || return 1
        out="${out%.json}-api-fallback.json"
        cli_exit=0
        ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" claude -p "$prompt" --model "$modell" --output-format json "$@" > "$out" || cli_exit=1
        versuch_logs+=("$out")
        if team_bewerte_ergebnis "$rolle" "$out" "$cli_exit"; then fehler=0; else fehler=1; fi
    fi

    # 429-Sonderbehandlung jetzt auf dem FINALEN (ggf. API-)Ergebnis: nur wenn
    # auch der API-Weg noch einen 429 liefert, wird gewartet/gepausiert.
    if [ "$fehler" -eq 1 ] && team_result_is_429 "$out"; then
        local versuch=1 reset_epoch jetzt warten reset_hhmm pausieren=1
        while [ "$versuch" -le "$TEAM_429_MAX_RETRIES" ]; do
            reset_epoch="$(team_429_reset_epoch "$out")" || reset_epoch=""
            if [ -z "$reset_epoch" ]; then
                echo "[$rolle] 429 erkannt, Reset-Zeit unbekannt — kein Warten, Pausen-Signal." >&2
                break
            fi
            jetzt="$(date +%s)"
            warten=$(( reset_epoch - jetzt + TEAM_429_PUFFER ))
            reset_hhmm="$(date -d "@$reset_epoch" +%H:%M 2>/dev/null || date -r "$reset_epoch" +%H:%M)"
            if [ "$TEAM_429_MAX_WARTEN" -le 0 ] || [ "$warten" -gt "$TEAM_429_MAX_WARTEN" ]; then
                echo "[$rolle] 429 erkannt, Reset erst in ${warten}s (> TEAM_429_MAX_WARTEN=${TEAM_429_MAX_WARTEN}s) — kein Warten, Pausen-Signal." >&2
                break
            fi

            echo "[$rolle] 429/Session-Limit erkannt (Versuch $versuch/$TEAM_429_MAX_RETRIES) — warte ${warten}s bis Reset (${reset_hhmm}) + Puffer." >&2
            team_429_sleep "$warten"

            out="${out%.json}-429-retry${versuch}.json"
            cli_exit=0
            # Wie beim API-Fallback oben: Key explizit voranstellen, falls der
            # aktuelle AUTH_MODE api ist (sonst greift die CLI ggf. die Abo-Session).
            if [ "$AUTH_MODE" = "api" ]; then
                ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" claude -p "$prompt" --model "$modell" --output-format json "$@" > "$out" || cli_exit=1
            else
                claude -p "$prompt" --model "$modell" --output-format json "$@" > "$out" || cli_exit=1
            fi
            versuch_logs+=("$out")
            if team_bewerte_ergebnis "$rolle" "$out" "$cli_exit"; then fehler=0; else fehler=1; fi

            if [ "$fehler" -eq 0 ]; then
                echo "[$rolle] Retry nach 429 erfolgreich. Log: $out" >&2
                pausieren=0
                break
            fi
            if ! team_result_is_429 "$out"; then
                echo "[$rolle] Retry lieferte einen normalen (nicht-429) Fehler — weiter im normalen Fehlerpfad." >&2
                pausieren=0
                break
            fi
            versuch=$((versuch + 1))
        done

        if [ "$fehler" -eq 1 ] && [ "$pausieren" -eq 1 ]; then
            TEAM_LAST_PAUSE=1
            TEAM_LAST_RESET="${reset_hhmm:-unbekannt}"
            TEAM_LAST_COST="$(team_summe_cost_usd "${versuch_logs[@]}")"
            TEAM_LAST_OUT="$out"
            echo "[$rolle] 429/Session-Limit — Retries erschöpft oder Reset zu weit entfernt. Pausen-Signal (Reset: $TEAM_LAST_RESET)." >&2
            return 42
        fi
    fi

    TEAM_LAST_COST="$(team_summe_cost_usd "${versuch_logs[@]}")"
    TEAM_LAST_OUT="$out"
    if [ "$fehler" -eq 1 ]; then
        echo "[$rolle] Claude-Aufruf endgültig fehlgeschlagen, Log: $out" >&2
        return 1
    fi
    return 0
}

# team_promise_in <json-datei> <promise-text>
# Rückgabe 0, wenn das Ergebnis <promise>TEXT</promise> enthält.
team_promise_in() {
    python3 -c '
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)
result = data.get("result", "") or ""
sys.exit(0 if f"<promise>{sys.argv[2]}</promise>" in result else 1)
' "$1" "$2"
}

# --- Rollen-Briefings (Stufe 90) ----------------------------------------------
# team_briefing <rolle>: gibt den Inhalt von prompts/rolle-<rolle>.md aus —
# ersetzt die frühere Prompt-Zeile "Rolle siehe CLAUDE.md — lies sie zuerst.",
# die jeden Rollenaufruf einen zusätzlichen Voll-Read von CLAUDE.md auslösen
# ließ. Fallback (Pflicht, Selbstbezugs-Risiko dieser Kaskade): fehlt die Datei
# oder ist sie leer, liefert der Helfer exakt die alte Zeile zurück — kein
# Abbruch, keine stderr-Fehlermeldung, damit ein Fehler hier nie einen Lauf
# lahmlegt.
team_briefing() {
    local datei="team/prompts/rolle-$1.md"
    if [ -s "$datei" ]; then
        cat "$datei"
    else
        echo "Rolle siehe CLAUDE.md — lies sie zuerst."
    fi
}

# --- Read-Only-Guard (Linie 3 — deterministisch, CHIRURGISCH) -------------------
# team_guard_begin: merkt sich HEAD als Rollback-Punkt.
# team_guard_verify <rolle> <whitelist-regex>:
#   Ermittelt geänderte Pfade (committet seit Start + Arbeitsverzeichnis), die
#   NICHT auf die Whitelist passen. Bei Verletzung wird NUR jeder einzelne
#   Verletzer-Pfad zurückgesetzt — niemals blanko `git reset --hard`/`clean -fd`.
#   Das schützt parallele/legitime uncommittete Arbeit an anderer Stelle.
#   (Lektion 2026-07-10: ein blindes reset+clean löschte einmal die gesamte
#   uncommittete Team-Infrastruktur. Nie wieder.)
team_guard_begin() {
    TEAM_GUARD_HASH="$(git rev-parse HEAD)"
}

team_guard_verify() {
    local rolle="$1" whitelist="$2" verletzungen pfad
    verletzungen="$( { git diff --name-only "$TEAM_GUARD_HASH" HEAD 2>/dev/null;
                       git status --porcelain | cut -c4-; } | sort -u \
                     | grep -Ev "$whitelist" || true)"
    [ -z "$verletzungen" ] && return 0

    echo "[$rolle] GUARD-VERLETZUNG — chirurgischer Rollback der folgenden Pfade:" >&2
    printf '%s\n' "$verletzungen" >&2
    while IFS= read -r pfad; do
        [ -z "$pfad" ] && continue
        if git cat-file -e "$TEAM_GUARD_HASH:$pfad" 2>/dev/null; then
            # War beim Start getrackt → auf Startstand zurückholen.
            git checkout "$TEAM_GUARD_HASH" -- "$pfad" 2>/dev/null || true
        else
            # Neu entstanden (committet oder untracked) → gezielt entfernen.
            git rm -f --cached -- "$pfad" >/dev/null 2>&1 || true
            rm -f -- "$pfad"
        fi
    done <<< "$verletzungen"
    return 1
}

# --- Substanz-Anker für Frank (HM-29) -----------------------------------------
# team_diff_beruehrt_fund <HM-Nr> <start-hash>
# Franks Dreisatz-Verifikation prüfte bislang nur FORM (Promise, Commit-
# Message-Muster, Beutebuch-Status), nie, ob der committete Diff überhaupt mit
# dem gemeldeten Fund zu tun hat — ein Fund konnte so fälschlich als "erledigt"
# verbucht werden, obwohl die eigentliche Fundstelle nie angefasst wurde
# (HM-29). Diese Funktion prüft LOSE, ob mindestens eine der im Beutebuch-Block
# per Backtick referenzierten Dateien (scripts/beutebuch.py dateien) im Diff
# seit start-hash vorkommt. Nennt der Fund KEINE Datei, gilt die Prüfung als
# bestanden (kein falscher Blocker bei rein beschreibenden Funden).
team_diff_beruehrt_fund() {
    local hm="$1" start="$2" fund_dateien diff_dateien f d
    fund_dateien="$($TEAM_BEUTEBUCH_TOOL dateien "$hm" 2>/dev/null || true)"
    [ -z "$fund_dateien" ] && return 0
    diff_dateien="$(git diff --name-only "$start" HEAD)"
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        while IFS= read -r d; do
            case "$d" in
                *"$f") return 0 ;;
            esac
        done <<< "$diff_dateien"
    done <<< "$fund_dateien"
    return 1
}

# --- Lock (eine Pipeline zur Zeit) -----------------------------------------------
# team_lock <label>: nimmt .team-loop.lock (non-blocking). Läuft das Skript
# unterhalb der Vollautomatik (TEAM_LOCK_HELD=1), wird nicht erneut gelockt.
team_lock() {
    if [ "${TEAM_LOCK_HELD:-0}" = "1" ]; then return 0; fi
    exec 9>.team-loop.lock
    if ! flock -n 9; then
        echo "[$1] Eine andere T.E.A.M.-Pipeline läuft bereits (.team-loop.lock) — Abbruch." >&2
        return 1
    fi
    export TEAM_LOCK_HELD=1
}

# --- Ergebnis-Prüfung --------------------------------------------------------
# team_result_is_error <json-datei>
# Rückgabe 0, wenn die JSON-Ausgabe von `claude -p` einen Fehler meldet
# (is_error) oder gar nicht lesbar ist — dann greift z. B. Ralphs API-Fallback.
team_result_is_error() {
    python3 -c '
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
sys.exit(0 if data.get("is_error") else 1)
' "$1"
}

# team_bewerte_ergebnis <rolle> <out-datei> <cli-exit-code>
# HM-33: Der reine Prozess-Exit-Code der `claude`-CLI darf ein geschriebenes
# Erfolgs-JSON (is_error:false) nicht überstimmen — z. B. endet die CLI bei
# gesetztem ANTHROPIC_API_KEY mit einer reinen "connectors disabled"-Warnung
# und Exit≠0, obwohl das Ergebnis inhaltlich erfolgreich ist. Das geschriebene
# JSON ist die letzte Instanz: Rückgabe 1 (Fehler) NUR wenn team_result_is_error
# zutrifft (Datei nicht lesbar ODER is_error:true) — der CLI-Exit-Code fließt
# nur noch in die Warnzeile ein, nicht mehr in die Erfolgs-/Fehler-Entscheidung.
team_bewerte_ergebnis() {
    local rolle="$1" out="$2" cli_exit="$3"
    if team_result_is_error "$out"; then
        return 1
    fi
    if [ "$cli_exit" -ne 0 ]; then
        echo "[$rolle] CLI-Exit≠0 trotz gültigem Erfolgs-JSON — werte als Erfolg (vermutlich reine CLI-Warnung, siehe HM-33)." >&2
    fi
    return 0
}

# --- Session-Limit (429) -------------------------------------------------------
# Kaskade 9 / Stufe 29 (plans/ralph-kaskade-9-session-limit.md): reine
# Erkennungs-/Parse-Logik. Warten/Retry folgt in Stufe 30.

# team_result_is_429 <json-datei>
# Rückgabe 0, wenn die JSON-Ausgabe von `claude -p` ein Session-Limit (429)
# meldet — über zwei Signale: das starke Feld api_error_status == 429, oder
# (Fallback für CLI-Versionen ohne dieses Feld) das Feld "result" IST IN
# GÄNZE (nicht nur als Teilstring irgendwo enthalten, HM-21) exakt die CLI-
# Systemmeldung "You've hit your session limit · resets HH[:MM]pm[ (Zone)]" —
# die Minuten sind OPTIONAL (BL-32): die CLI schreibt bei vollen Stunden nur
# "resets 3pm" (ohne ":00"), belegt durch den echten Vorfall in
# .ralph-logs/archiv/stufe-49-20260712-134536.json — ohne diese Optionalität
# wurde ein Doppel-429 (Abo UND API) fälschlich als "echter Fehler" (Exit 1)
# statt als Session-Limit gewertet und die Auto-Warte-/Retry-Logik übersprungen.
# belegt durch den echten Vorfall in .team-logs/harry-20260711-184756.json
# ("You've hit your session limit · resets 6:50pm (Europe/Berlin)", ganzes
# result-Feld, num_turns 1: die CLI liefert diesen Satz unverändert und
# OHNE umgebenden Fließtext, weil dabei nie ein Modell-Turn stattfindet).
# HM-19 hatte den Anker bereits auf "hit your session limit" + wortgrenzen-
# geschütztes Reset-Muster verengt, blieb aber ein Teilstring-Suche — dadurch
# genügte weiterhin ein Claude-generierter Erklärtext, der das Beutebuch/den
# Kaskade-9-Plan wörtlich zitiert (HM-21: genau dieses Zitat steht jetzt
# dauerhaft im Repo). Ein bloßes Zitat mitten in längerem Fließtext hat immer
# zusätzliche Wörter davor/danach im result-Feld und besteht den vollständigen
# Abgleich (re.fullmatch auf den getrimmten String) deshalb NICHT mehr.
# Nicht lesbare Datei → kein 429 (Rückgabe 1), das bleibt Sache von
# team_result_is_error.
team_result_is_429() {
    python3 -c '
import json, re, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)
if data.get("api_error_status") == 429:
    sys.exit(0)
text = str(data.get("result") or "").strip()
# BL-32: Minuten optional (\d{1,2}(:\d{2})?) — die CLI schreibt bei vollen
# Stunden nur "resets 3pm" ohne ":00" (echter Vorfall stufe-49).
pattern = r"you.ve hit your session limit\s*[·\-–:]\s*resets\s+\d{1,2}(:\d{2})?\s*[ap]m(\s*\([^)]*\))?\.?"
if re.fullmatch(pattern, text, re.IGNORECASE):
    sys.exit(0)
sys.exit(1)
' "$1"
}

# team_429_reset_epoch <json-datei>
# Liest die Reset-Uhrzeit aus dem freien Ergebnistext ("resets HH:MMpm",
# 12h-Format, lokale Zeitzone) und gibt einen Unix-Epoch-Zeitpunkt in der
# Zukunft aus. Liegt die geparste Uhrzeit heute schon in der Vergangenheit,
# gilt sie für morgen (Reset über Mitternacht). Kein/unlesbares Datum → leere
# Ausgabe, Exit 1 — der Aufrufer behandelt das wie "Reset unbekannt".
# HM-22: durchsucht wie team_result_is_429 NUR das Feld "result" (nicht den
# kompletten JSON-Dump, der Zitate/andere Felder mit "resets HH:MMpm" enthalten
# kann) und verlangt Wortgrenzen um "resets ... [ap]m" — sonst kann ein Treffer
# aus falscher Fundstelle (z. B. einem Doku-Zitat) einen falschen Reset-
# Zeitpunkt liefern.
team_429_reset_epoch() {
    python3 -c '
import json, re, sys
from datetime import datetime, timedelta

try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)

text = str(data.get("result") or "")
# BL-32: Minuten-Gruppe optional; bei "resets 3pm" (volle Stunde ohne ":MM")
# ist die Minute 0. Ohne diese Optionalität lieferte die Funktion "Reset
# unbekannt", wodurch die Auto-Warte-/Retry-Logik (Strategie A) übersprungen
# und ein Doppel-429 fälschlich als harter Fehler (Exit 1) behandelt wurde.
m = re.search(r"\bresets\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m)\b", text, re.IGNORECASE)
if not m:
    sys.exit(1)

hour = int(m.group(1)) % 12
if m.group(3).lower() == "pm":
    hour += 12
minute = int(m.group(2)) if m.group(2) else 0
if minute > 59:
    sys.exit(1)

now = datetime.now()
reset = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
if reset <= now:
    reset += timedelta(days=1)

print(int(reset.timestamp()))
' "$1"
}

# --- Kosten ------------------------------------------------------------------
# team_summe_cost_usd <json-datei…>
# Summe von total_cost_usd über MEHRERE Logs — die Kosten EINES team_claude-
# Aufrufs inklusive aller gescheiterten Vorversuche (Abo-Versuch vor dem
# API-Fallback, 429-Zwischenversuche). Fehlende/kaputte Dateien zaehlen als 0.
# Hintergrund (BL-55, real erlebt 2026-08-01, Kaskade 22 Stufe 93): Der Abo-
# Versuch scheiterte NACH 1.6806 USD, der API-Fallback kostete 0.3984 — gemeldet
# und gegen den Pro-Stufe-Cap geprueft wurden nur die 0.3984, weil TEAM_LAST_COST
# allein aus dem FINALEN Log gelesen wurde. Damit war der Cap umgehbar: 4.9 USD
# Abo-Fehlversuch + 4.9 USD API meldeten 4.9 gegen einen 5-USD-Deckel.
team_summe_cost_usd() {
    python3 -c '
import json, sys
gesamt = 0.0
for pfad in sys.argv[1:]:
    try:
        gesamt += float(json.load(open(pfad)).get("total_cost_usd", 0) or 0)
    except Exception:
        pass
print(f"{gesamt:.10f}")
' "$@"
}

# team_extract_cost_usd <json-datei>
# Liest total_cost_usd aus der JSON-Ausgabe von `claude -p --output-format json`.
team_extract_cost_usd() {
    python3 -c '
import json, sys
try:
    data = json.load(open(sys.argv[1]))
    print(data.get("total_cost_usd", 0) or 0)
except Exception:
    print(0)
' "$1"
}

# --- Kosten-Summierung (zentral, dedupliziert vollautomatik.sh/team-status.sh) -
# Kapselt scripts/kosten.py — vorher existierte dieselbe Python-Summierung
# doppelt/dreifach als Inline-Heredoc in vollautomatik.sh und team-status.sh.

# team_kosten_summe <dir…>: Gesamtsumme total_cost_usd über alle *.json in
# den angegebenen Log-Ordnern (Abo + API zusammen).
team_kosten_summe() {
    $TEAM_KOSTEN_TOOL summe "$@"
}

# team_kosten_seit <epoch> <dir…>: Summe total_cost_usd nur über *.json, deren
# mtime >= <epoch> ist — die Kosten EINES Laufs (seit dem gemerkten Startpunkt),
# nicht lebenslang. Grundlage der Pro-Lauf-Deckel-Durchsetzung in vollautomatik.sh
# (BL-18, Strippenzieher-Entscheid: „Pro-Lauf-Deckel = operative Grenze,
# Gesamtrahmen nur dokumentiert" — CLAUDE.md/BL-13). Der lebenslange Kontostand
# bleibt team_kontostand_gesamt (Anzeige, nicht Durchsetzung).
team_kosten_seit() {
    local seit="$1"; shift
    $TEAM_KOSTEN_TOOL summe --since "$seit" "$@"
}

# team_kosten_split <dir…>: wie team_kosten_summe, aber getrennt nach
# Abo-Gegenwert (nicht abgerechnet) und real abgerechneter API — Ausgabe
# "abo<TAB>api" (Klassifizierung über den Dateinamen, siehe team_claude:
# API-Fallback-Logs enden auf "-api-fallback.json").
team_kosten_split() {
    $TEAM_KOSTEN_TOOL summe --split "$@"
}

# team_ledger_summe [pfad]: historische Basissumme aus der committeten
# .budget-ledger (append-only, Stufe 18 in
# plans/ralph-kaskade-6-budget-governance.md). Kommentarzeilen (#) und
# Leerzeilen werden ignoriert; fehlende Datei ergibt 0.
team_ledger_summe() {
    $TEAM_KOSTEN_TOOL ledger "${1:-.budget-ledger}"
}

# team_ledger_domaene <website|team> [pfad]: Ledger-Summe gefiltert auf eine
# Domaene (BL-29, Kaskade 13/Stufe 41/44). Altzeilen ohne Domaenenfeld (vor
# Kaskade 13) zaehlen hier NIE mit — sie bleiben "unzugeordnet" (Differenz aus
# team_ledger_summe minus website minus team).
team_ledger_domaene() {
    local domaene="$1" pfad="${2:-.budget-ledger}"
    $TEAM_KOSTEN_TOOL ledger "$pfad" --domaene "$domaene"
}

# team_ledger_split [pfad]: wie team_ledger_summe, aber die usd-Spalte nach
# auth-Bucket getrennt — Ausgabe "abo<TAB>api<TAB>gemischt" (BL-17-Restpunkt/
# BL-29-"1b", Kaskade 16/Stufe 53). "gemischt" sammelt alles, was NICHT exakt
# auth=="abo" oder auth=="api" ist (v. a. "abo/api", aber auch Altzeilen ohne
# auth-Wert) — ehrlich statt geraten, es gilt immer
# abo+api+gemischt == team_ledger_summe.
team_ledger_split() {
    $TEAM_KOSTEN_TOOL ledger "${1:-.budget-ledger}" --split
}

# team_akteur_abschluss <rolle> <auth:abo|api> <usd> <domaene:website|team>
# [notiz] [pfad] [repo]: rollen-agnostischer A1-Abschluss (BL-33, Kaskade 15/
# Stufe 51) — duenner Wrapper um `kosten.py akteur-abschluss` fuer JEDE
# interaktiv (ausserhalb team_claude) arbeitende Rolle (Architekt, Frank im
# Abomodus, …), analog den bestehenden team_ledger_*-Wrappern. Alle Werte
# gehen als eigene argv-Elemente an python3 (kein `python3 -c` mit roher
# Interpolation — Lehre aus BL-23/HM-17). pfad/repo optional, Default wie
# kosten.py (".budget-ledger"/"."), damit Fixture-Tests isoliert gegen ein
# Test-Ledger pruefen koennen.
team_akteur_abschluss() {
    local rolle="$1" auth="$2" usd="$3" domaene="$4" notiz="${5:-}"
    local pfad="${6:-.budget-ledger}" repo="${7:-.}"
    if [ -n "$notiz" ]; then
        $TEAM_KOSTEN_TOOL akteur-abschluss --usd "$usd" \
            --domaene "$domaene" --rolle "$rolle" --auth "$auth" \
            --notiz "$notiz" --pfad "$pfad" --repo "$repo"
    else
        $TEAM_KOSTEN_TOOL akteur-abschluss --usd "$usd" \
            --domaene "$domaene" --rolle "$rolle" --auth "$auth" \
            --pfad "$pfad" --repo "$repo"
    fi
}

# team_architekt_stand [ledger-pfad] [plan-datei]: liefert "USD<TAB>status"
# fuer die Architekt-Kosten der AKTIVEN Kaskade — BL-28-Hybrid A2->A1
# (Kaskade 13/Stufe 44): Hat der Strippenzieher fuer diese Kaskade bereits
# eine echte Architekt-Zeile per `architekt-abschluss` (Stufe 43)
# eingetragen, ist status "echt" und der Wert kommt aus der Ledger. Sonst
# status "geschaetzt" mit der A2-Live-Schaetzung (team_architekt_schaetzung).
# Beide Pfade optional (Default ".budget-ledger"/aktives .ralph-plan) —
# Fixture-Tests koennen so isoliert gegen ein Test-Ledger/-Plan pruefen.
# HM-46: Existenz einer echten Zeile wird ueber die TREFFERANZAHL
# (--anzahl) geprueft, nicht mehr ueber einen Wertevergleich der Summe
# gegen den String "0.0000" — eine echte Zeile mit usd=0.0000 (z. B. eine
# Kaskade, in der der Architekt nachweislich 0 USD kostete) ist am
# Summenwert allein nicht von "keine Zeile vorhanden" zu unterscheiden.
team_architekt_stand() {
    local ledger_pfad="${1:-.budget-ledger}" plan_datei="${2:-$(team_plan_datei)}"
    local kaskade anzahl echt
    kaskade="$(printf '%s' "$plan_datei" | grep -oE 'ralph-kaskade-[0-9]+' | grep -oE '[0-9]+' | head -1)"
    if [ -n "$kaskade" ]; then
        anzahl="$($TEAM_KOSTEN_TOOL ledger "$ledger_pfad" --rolle architekt --kaskade "$kaskade" --anzahl 2>/dev/null)"
        if [ -n "$anzahl" ] && [ "$anzahl" -gt 0 ] 2>/dev/null; then
            echt="$($TEAM_KOSTEN_TOOL ledger "$ledger_pfad" --rolle architekt --kaskade "$kaskade" 2>/dev/null)"
            printf '%s\techt\n' "$echt"
            return 0
        fi
    fi
    printf '%s\tgeschätzt\n' "$(team_architekt_schaetzung)"
}

# team_architekt_schaetzung: A2-Live-Schaetzung der Architekt-Kosten (BL-28,
# Kaskade 13/Stufe 42) — der Architekt laeuft interaktiv ausserhalb von
# team_claude und schreibt keine total_cost_usd-JSONs. Proxy: Zeilen-Churn
# (git diff --numstat) ueber plans/** + CLAUDE.md seit dem letzten
# .budget-ledger-Commit, mal Eichfaktor (siehe scripts/kosten.py). Bewusst
# eine GROBE Groessenordnung — Stufe 43 ersetzt sie beim Kaskaden-Abschluss
# durch den echten Konsolenwert (A1). Ohne bisherigen Ledger-Commit (frisches
# Repo) ist die Ausgabe 0.0000 statt eines Abbruchs.
team_architekt_schaetzung() {
    local ref
    ref="$(git log -1 --format=%H -- .budget-ledger 2>/dev/null)"
    if [ -z "$ref" ]; then
        echo "0.0000"
        return 0
    fi
    $TEAM_KOSTEN_TOOL architekt-schaetzung --since "$ref" 2>/dev/null \
        || echo "0.0000"
}

# --- Deckel-Empfehlung (Governance, Stufe 19) --------------------------------
# Der Architekt hinterlegt im Kopf des aktiven Kaskaden-Plans eine Zeile
# `BUDGET_EMPFEHLUNG_USD=<zahl>` (siehe
# plans/ralph-kaskade-6-budget-governance.md). vollautomatik.sh/halbautomatik.sh lesen sie hier
# zentral, statt das grep-Muster mehrfach zu duplizieren.

# team_plan_datei: aktive Plan-Datei aus der Zeiger-Datei .ralph-plan (eine
# Zeile, Pfad — Stufe 20 in plans/ralph-kaskade-6-budget-governance.md). Fehlt
# die Zeiger-Datei, ist die Ausgabe leer — der Aufrufer fällt auf seinen
# Default zurück (kein Abbruch hier; ralph.sh selbst bricht beim Bau ab).
team_plan_datei() {
    # Starterkit-Fix: `|| true` — sonst reisst der RC!=0 einer fehlenden
    # Zeiger-Datei den Aufrufer unter `set -e` weg, obwohl die Doku oben
    # ausdruecklich "kein Abbruch hier" zusagt (frisches Projekt = Normalfall).
    { head -n1 .ralph-plan 2>/dev/null || true; } | tr -d '[:space:]'
}

# team_ralph_cap [plan-datei]: liest RALPH_CAP aus der angegebenen (oder sonst
# der aktiven) Plan-Datei — dasselbe Muster wie team_budget_empfehlung. Fehlt
# Datei/Zeile, ist die Ausgabe leer.
team_ralph_cap() {
    local plan="${1:-$(team_plan_datei)}"
    [ -n "$plan" ] && [ -f "$plan" ] || return 0
    grep -E '^[[:space:]]*RALPH_CAP=' "$plan" | head -1 | cut -d= -f2 | tr -d '[:space:]'
}

# team_budget_empfehlung [plan-datei]: liest BUDGET_EMPFEHLUNG_USD aus der
# angegebenen (oder sonst der aktiven) Plan-Datei. Fehlt Datei/Zeile, ist die
# Ausgabe leer — der Aufrufer fällt dann auf seinen Default zurück (kein
# Abbruch, keine Rateraterei).
team_budget_empfehlung() {
    local plan="${1:-$(team_plan_datei)}"
    [ -n "$plan" ] && [ -f "$plan" ] || return 0
    grep -E '^[[:space:]]*BUDGET_EMPFEHLUNG_USD=' "$plan" \
        | head -1 | cut -d= -f2 | tr -d '[:space:]'
}

# team_kontostand_gesamt: kumulierter Kontostand wie `team-status.sh --budget`
# ("Gesamt"-Zeile) = historische .budget-ledger-Basis + aktuelle lokale Logs
# (.ralph-logs + .team-logs).
team_kontostand_gesamt() {
    local basis abo api
    basis="$(team_ledger_summe)"
    IFS=$'\t' read -r abo api <<<"$(team_kosten_split .ralph-logs .team-logs)"
    # kein rohes ${…}-Interpolieren — BL-23/HM-17/HM-34/HM-42: Werte als
    # eigene sys.argv-Elemente uebergeben statt in den Python-Quelltext.
    python3 -c "import sys; print(f'{float(sys.argv[1]) + float(sys.argv[2]) + float(sys.argv[3]):.4f}')" "$basis" "$abo" "$api"
}

# team_logs_archivieren <dir>: verschiebt die aktuell in <dir> liegenden
# *.json-Rohlogs nach <dir>/archiv/ (bleiben lokal erhalten, zaehlen aber
# wegen des nicht-rekursiven glob() in scripts/kosten.py nicht mehr in
# team_kosten_summe/team_kontostand_gesamt mit). AUFRUFEN, direkt NACHDEM
# eine neue .budget-ledger-Zeile fuer eine abgeschlossene Kaskade angehaengt
# wurde — sonst zaehlt der Kontostand dieselben Kosten doppelt (Ledger-Zeile
# + Rohlog), siehe BL-17. Ohne diesen Schritt bleibt die Ledger-Zeile die
# einzige Quelle, die je nach Log-Rotation ueberlebt; das war die urspruengliche
# Absicherungsidee hinter der Ledger (siehe Stufe 18,
# plans/ralph-kaskade-6-budget-governance.md) — bislang fehlte nur der
# Vollzug.
team_logs_archivieren() {
    local dir="$1" archiv
    [ -d "$dir" ] || return 0
    archiv="$dir/archiv"
    mkdir -p "$archiv"
    find "$dir" -maxdepth 1 -name '*.json' -exec mv -t "$archiv" {} + 2>/dev/null
    return 0
}

# team_resolve_budget_cap <aktueller-deckel> <user-hat-gesetzt:0|1> <empfehlung>
# Reine Rechenlogik der "nur anheben, nie senken"-Regel (Strippenzieher-
# Entscheid 2, Stufe 19) — isoliert testbar ohne echten vollautomatik.sh-Lauf:
#   - hat der User TEAM_BUDGET_USD explizit gesetzt, gewinnt IMMER der
#     aktuelle Wert (auch wenn die Empfehlung höher läge);
#   - sonst gewinnt die Empfehlung, aber nur wenn sie größer als der aktuelle
#     (Default-)Deckel ist — eine niedrigere Empfehlung senkt nie.
team_resolve_budget_cap() {
    local aktuell="$1" user_gesetzt="$2" empfehlung="$3"
    if [ "$user_gesetzt" = "1" ]; then
        echo "$aktuell"; return 0
    fi
    if [ -n "$empfehlung" ] \
       && python3 -c "import sys; sys.exit(0 if float(sys.argv[1]) > float(sys.argv[2]) else 1)" "$empfehlung" "$aktuell" 2>/dev/null; then
        echo "$empfehlung"; return 0
    fi
    echo "$aktuell"
}

# team_budget_check <kosten> <soft-limit> <label> [hard-limit]
#
# Zwei-Schwellen-Modell (Strippenzieher-Entscheid 2026-07-12, HM-32).
# Rückgabe:
#   0 = ok (unter der Warnschwelle)
#   1 = Warnschwelle (80 % des Soft-Limits) erreicht — reiner Hinweis
#   2 = SOFT-Limit überschritten — deutlicher Hinweis; der Aufrufer entscheidet,
#       ob das ein weicher (weitermachen) oder harter (Abbruch) Fall ist:
#         * Frank/Axel behandeln 2 als WEICH (kein Rollback, Fix bleibt gültig),
#         * Ralph/Harry/Marv rufen OHNE hard-limit auf und behandeln 2 als HART.
#   3 = HARD-Limit überschritten — IMMER harter Abbruch (nur bei gesetztem
#       hard-limit > soft-limit möglich; die iterierenden Rollen Frank/Axel).
#
# Rückwärtskompatibel: Ohne <hard-limit> verhält sich die Funktion wie zuvor
# (0/1/2), 2 bleibt "Soft-Limit überschritten". Der neue Zustand 3 tritt nur
# auf, wenn ein sinnvolles hard-limit (> soft-limit) übergeben wird.
team_budget_check() {
    python3 -c '
import sys
cost = float(sys.argv[1])
soft = float(sys.argv[2])
label = sys.argv[3]
hard = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None

if hard is not None and hard > soft and cost >= hard:
    print(f"HARD-CAP ÜBERSCHRITTEN ({label}): {cost:.2f} USD >= Hard-Cap {hard:.2f} USD — harter Abbruch.")
    sys.exit(3)
if cost >= soft:
    print(f"SOFT-CAP ÜBERSCHRITTEN ({label}): {cost:.2f} USD >= Soft-Cap {soft:.2f} USD.")
    sys.exit(2)
if cost >= 0.8 * soft:
    print(f"WARNSCHWELLE ({label}): {cost:.2f} USD >= 80 % von {soft:.2f} USD — Strippenzieher informieren.")
    sys.exit(1)
sys.exit(0)
' "$1" "$2" "$3" "${4:-}"
}

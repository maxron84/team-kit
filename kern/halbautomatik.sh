#!/usr/bin/env bash
# halbautomatik.sh — die T.E.A.M.-HALBAUTOMATIK.
# Wie die Vollautomatik (vollautomatik.sh), aber der Strippenzieher entscheidet
# zwischen JEDEM Schritt selbst. Nutzt dieselben Rollen-Skripte
# (Ralph/Harry/Marv/Frank/Axel), hält das Lock über die Sitzung und reicht es an
# die Kinder weiter.
#
# Zwei Betriebsarten:
#   ./halbautomatik.sh              interaktiv: zeigt Status + empfohlenen nächsten
#                                   Schritt, wartet auf deine Taste, führt EINEN
#                                   Schritt aus, fragt wieder — Schritt für Schritt.
#   ./halbautomatik.sh <schritt>    Einzelschritt ohne Menü (für Skripte/Tests):
#                                   ralph | harry | marv | frank | axel | status | next
#
# Env wie bei der Vollautomatik (TEAM_MODEL_*, AUTH_MODE, Budgets). Kein
# Gesamt-Deckel-Zwang: bei der Halbautomatik siehst du die Kosten nach jedem
# Schritt selbst.
set -uo pipefail
cd "$(dirname "$0")"
# shellcheck source=team-lib.sh
source ./team-lib.sh

# HM-32: Warn-Guard im EIGENEN Prozess seeden, BEVOR die erste Rolle geforkt wird
# — die Rollen laufen als SIBLING-Subprozesse, ein in einem Kind gesetzter
# Env-Guard erreicht die Geschwister nie (analog team_lock/TEAM_LOCK_HELD). Nur
# im Abo-Modus relevant; im reinen api-Modus ist der Key legitim → keine Warnung.
if [ "$(team_auth_mode_effektiv abo)" = "abo" ]; then
    team_warnung_abo_key
fi

RALPH_CAP_VALUE="$(team_ralph_cap)"

# --- empfohlener nächster Schritt aus dem aktuellen Zustand -------------------
naechster_schritt() {
    local stufe head
    stufe="$( [ -f .ralph-state ] && tr -d '[:space:]' < .ralph-state || echo 1 )"
    if [ "${RALPH_CAP_VALUE:-0}" != "0" ] && [ "$stufe" -le "${RALPH_CAP_VALUE:-0}" ] 2>/dev/null; then
        echo ralph; return
    fi
    head="$(git rev-parse HEAD)"
    if [ "$(cat .harry-state 2>/dev/null || echo x)" != "$head" ]; then echo harry; return; fi
    if [ "$(cat .marv-state 2>/dev/null || echo x)" != "$head" ]; then echo marv; return; fi
    if python3 scripts/beutebuch.py first "Fix-Plan liegt vor" >/dev/null \
       || python3 scripts/beutebuch.py first "an Frank übergeben" >/dev/null; then
        echo frank; return
    fi
    if python3 scripts/beutebuch.py first "an Axel übergeben" >/dev/null; then echo axel; return; fi
    echo fertig
}

# --- einen Schritt ausführen (gibt dessen Exit-Code weiter) ------------------
schritt_ausfuehren() {
    case "$1" in
        ralph) ./ralph.sh ;;
        harry) ./harry.sh ;;
        marv)  ./marv.sh ;;
        frank) ./frank.sh ;;
        axel)  ./axel.sh ;;
        *) echo "Unbekannter Schritt: $1" >&2; return 2 ;;
    esac
}

deute_exit() {  # $1=schritt $2=rc — menschliche Einordnung
    case "$2" in
        0) echo "  → $1 hat gearbeitet (Exit 0)." ;;
        3) echo "  → $1: nichts zu tun (Exit 3)." ;;
        *) echo "  → $1 endete mit Fehler (Exit $2) — Logs prüfen (.team-logs/, .ralph-logs/)." ;;
    esac
}

# --- Deckel-Dialog vor dem Ralph-Schritt (interaktiv, Stufe 19) --------------
# Nur beim ralph-Schritt relevant (Bau kostet am meisten) — Read-Only-Rollen
# brauchen keinen Dialog. Der Nicht-Interaktiv-Modus (./halbautomatik.sh ralph) ruft
# diese Funktion NICHT auf (siehe Einzelschritt-Modus unten) und bleibt damit
# ohne Dialog lauffähig.
deckel_dialog_ralph() {
    local empfehlung eingabe
    echo "  ── Deckel-Check vor dem Bau-Schritt ──"
    ./team-status.sh --budget | sed 's/^/  /'
    empfehlung="$(team_budget_empfehlung)"
    if [ -n "$empfehlung" ]; then
        printf "  Architekten-Empfehlung: %s USD. [Enter]=übernehmen, oder Zahl eingeben > " "$empfehlung"
    else
        empfehlung=15
        printf "  Keine Architekten-Empfehlung im aktiven Plan — Default %s USD. [Enter]=übernehmen, oder Zahl eingeben > " "$empfehlung"
    fi
    read -r eingabe || eingabe=""
    TEAM_BUDGET_USD="${eingabe:-$empfehlung}"
    export TEAM_BUDGET_USD
    echo "  → Deckel für diesen Lauf: $TEAM_BUDGET_USD USD."
}

# --- Einzelschritt-Modus (nicht-interaktiv) ----------------------------------
if [ "$#" -ge 1 ]; then
    case "$1" in
        status) ./team-status.sh; exit 0 ;;
        next)   naechster_schritt; exit 0 ;;
        ralph|harry|marv|frank|axel)
            team_lock halbautomatik || exit 1
            schritt_ausfuehren "$1"; rc=$?
            deute_exit "$1" "$rc"
            exit "$rc" ;;
        *) echo "Aufruf: ./halbautomatik.sh [ralph|harry|marv|frank|axel|status|next]" >&2; exit 2 ;;
    esac
fi

# --- Interaktiver Modus ------------------------------------------------------
if [ ! -t 0 ]; then
    echo "halbautomatik.sh ohne Terminal aufgerufen — hier ist der empfohlene nächste Schritt:"
    echo "  $(naechster_schritt)"
    echo "Für einen konkreten Schritt: ./halbautomatik.sh <ralph|harry|marv|frank|axel>"
    exit 0
fi

team_lock halbautomatik || exit 1
echo "═══ T.E.A.M. Halbautomatik — Schritt für Schritt ═══"
echo "Du entscheidest jeden Schritt. [Enter]=Empfehlung · [q]=Schluss · [?]=Hilfe"

while true; do
    empfohlen="$(naechster_schritt)"
    echo
    echo "──────────────────────────────────────────────"
    echo "  Empfohlener nächster Schritt: ${empfohlen}"
    if [ "$empfohlen" = "fertig" ]; then
        echo "  (Kaskade gebaut, Red Team durch, Beutebuch abgearbeitet.)"
    fi
    printf "  [Enter]=%s  [r]alph [h]arry [m]arv [f]rank [a]xel  [s]tatus  [q]uit > " "$empfohlen"
    read -r taste || { echo; break; }

    case "$taste" in
        "")  [ "$empfohlen" = "fertig" ] && { echo "  Nichts zu tun — nutze [q] zum Beenden."; continue; }
             [ "$empfohlen" = "ralph" ] && deckel_dialog_ralph
             schritt_ausfuehren "$empfohlen"; deute_exit "$empfohlen" "$?" ;;
        r|ralph) deckel_dialog_ralph; schritt_ausfuehren ralph; deute_exit ralph "$?" ;;
        h|harry) schritt_ausfuehren harry; deute_exit harry "$?" ;;
        m|marv)  schritt_ausfuehren marv;  deute_exit marv  "$?" ;;
        f|frank) schritt_ausfuehren frank; deute_exit frank "$?" ;;
        a|axel)  schritt_ausfuehren axel;  deute_exit axel  "$?" ;;
        s|status) ./team-status.sh ;;
        q|quit|exit) echo "  Halbautomatik beendet. Der Rest wartet geduldig."; break ;;
        \?|h\?|help)
            echo "  Enter=empfohlenen Schritt · r/h/m/f/a=bestimmte Rolle erzwingen"
            echo "  s=Status-Dashboard · q=beenden. Ein Tastendruck = ein Schritt." ;;
        *) echo "  Unbekannt: '$taste' — [?] für Hilfe." ;;
    esac
done

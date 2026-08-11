#!/usr/bin/env bash
# vollautomatik.sh — der Vollautomatik-Orchestrator: fährt eine komplette
# Kaskade vollautomatisch durch. Ralph baut → Red Team greift an → Frank fixt →
# Axel knackt die harten Fälle → Abschlussbericht.
#
# Aufruf:  ./vollautomatik.sh
# Env:     TEAM_MAX_RUNDEN   Fix-Runden Frank/Axel (Default 12) — grobe Obergrenze.
#          TEAM_FIX_MAX_STAGNATION  Auslauf-Bremse (Default = TEAM_FRANK_MAX_VERSUCHE,
#                            sonst 3; HM-31-Fix): bricht Phase 4 ab, sobald so viele
#                            Runden IN FOLGE weder einen Frank-Fix noch eine neue
#                            Axel-Akte noch eine Beutebuch-Statusänderung gebracht
#                            haben — statt teuer bis TEAM_MAX_RUNDEN leerzudrehen.
#                            Muss >= TEAM_FRANK_MAX_VERSUCHE (Default 3) bleiben, sonst
#                            greift die Bremse VOR Franks eigener Auto-Eskalation an
#                            Axel (frank.sh Zeile ~19/95–101) — jeder Fehlversuch, der
#                            den Beutebuch-Status noch nicht ändert, zählt hier wie dort
#                            identisch mit; erst der eskalierende Versuch ändert den
#                            Status und setzt die Stagnation zurück. Daher Default hier
#                            an TEAM_FRANK_MAX_VERSUCHE gekoppelt statt unabhängig fest 2.
#          TEAM_BUDGET_USD   Deckel für DIESEN Lauf (Default 15) — die harte
#                            Durchsetzung misst nur die Kosten dieses einen
#                            Laufs (A), nicht den lebenslangen Kontostand (BL-18).
#          TEAM_MODEL_LOOP / TEAM_MODEL_STRONG / AUTH_MODE  (siehe team-lib.sh)
# Exit:    0 = Lauf durch · 1 = echter Fehler (Mensch gefragt; inkl. Stagnation)
#          43 = Stufe fertig, Quittung fehlt (BL-41, durchgereicht von ralph.sh):
#               kein Neubau — prüfen und von Hand quittieren
#          42 = Session-Limit — Lauf pausiert (kein Fehler, kein
#               Datenverlust, State steht; siehe Kaskade 9/Stufe 31,
#               CLAUDE.md „Loop-Mechanik & Auth") — greift in Phase 4 jetzt auch
#               bei einem Exit 42 von frank.sh/axel.sh (Kaskade 11/Stufe 38).
#
# Sequenziell + flock-gesichert. Hält das Lock über den ganzen Lauf und gibt es
# an die Kind-Skripte weiter (TEAM_LOCK_HELD=1), damit die sich nicht selbst
# aussperren.
set -uo pipefail   # kein -e: Rollen-Exit 3 (nichts zu tun) ist normal
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh
team_lock vollautomatik || exit 1

# HM-32: Warn-Guard im EIGENEN Prozess seeden, BEVOR die erste Rolle geforkt wird
# — die Rollen laufen als SIBLING-Subprozesse, ein in einem Kind gesetzter
# Env-Guard erreicht die Geschwister nie (analog team_lock/TEAM_LOCK_HELD). Nur
# im Abo-Modus relevant; im reinen api-Modus ist der Key legitim → keine Warnung.
if [ "$(team_auth_mode_effektiv abo)" = "abo" ]; then
    team_warnung_abo_key
fi

MAX_RUNDEN="${TEAM_MAX_RUNDEN:-12}"
# HM-31: Default an TEAM_FRANK_MAX_VERSUCHE koppeln (statt fest 2), sonst
# bricht die Bremse regelmäßig VOR Franks eigener Auto-Eskalation an Axel ab.
STAGNATION_MAX="${TEAM_FIX_MAX_STAGNATION:-${TEAM_FRANK_MAX_VERSUCHE:-3}}"
TEAM_BUDGET_USD_USER_GESETZT=0
[ -n "${TEAM_BUDGET_USD:-}" ] && TEAM_BUDGET_USD_USER_GESETZT=1
TEAM_BUDGET_USD="${TEAM_BUDGET_USD:-15}"
LOG_DIR=".team-logs"; mkdir -p "$LOG_DIR"
LAUF_LOG="$LOG_DIR/vollautomatik-$(date +%Y%m%d-%H%M%S).log"
# Startzeitpunkt dieses Laufs — die Pro-Lauf-Deckel-Durchsetzung (budget_ok)
# zählt nur Logs, die seither entstanden sind (BL-18). -1 s Puffer gegen
# Sekunden-Rundung zwischen date und den ersten Rollen-Logs.
LAUF_START=$(( $(date +%s) - 1 ))

# Alles doppelt: Konsole + Lauf-Log (team-status liest die letzten Zeilen).
exec > >(tee -a "$LAUF_LOG") 2>&1

trap 'echo "[vollautomatik] abgebrochen (Signal) — Lock wird freigegeben."; exit 130' INT TERM

log() { echo "[$(date +%H:%M:%S)] $*"; }

# --- Zwei bewusst getrennte Kennzahlen (BL-18, Strippenzieher-Entscheid) ------
# A) lauf_kosten  — Kosten NUR DIESES Laufs (Logs seit LAUF_START). Das ist die
#    operative Grenze, gegen die budget_ok() den Pro-Lauf-Deckel durchsetzt:
#    „Pro-Lauf-Deckel = operative Grenze" (CLAUDE.md/BL-13). Vorher (BL-17) maß
#    die Durchsetzung fälschlich den lebenslangen Kontostand B — dadurch stoppte
#    die Vollautomatik, sobald die Lebenssumme die Plan-Empfehlung überstieg (dauerhaft),
#    noch bevor der aktuelle Lauf überhaupt etwas kostete.
# B) kontostand_gesamt — lebenslange Summe (Ledger-Basis + alle laufenden Logs),
#    identisch zu `team-status.sh --budget`. Reine ANZEIGE (Abschlussbericht,
#    Notify, Deckel-Anhebungs-Meldung), NIE Durchsetzung.
#    Die Archiv-Unterordner zaehlen bei A BEWUSST mit: eine Abschluss-Stufe
#    INNERHALB des Laufs kann .ralph-logs/.team-logs nach <dir>/archiv/
#    wegraeumen (team_logs_archivieren, BL-17-Pflicht). Ohne die Archivpfade
#    faellt das bereits ausgegebene Geld mitten im Lauf aus der Messung — real
#    erlebt in Kaskade 22 (2026-08-01): nach Stufe 93 sank der gemessene Lauf
#    von 26.42 auf 6.16 USD, also GENAU bevor die offene Fix-Phase (bis zu 12
#    Frank/Axel-Runden) startete. Der mtime-Filter >= LAUF_START haelt die
#    historischen Archiv-Logs frueherer Kaskaden zuverlaessig draussen; `mv`
#    innerhalb desselben Dateisystems laesst die mtime unveraendert (BL-55).
lauf_kosten()       { team_kosten_seit "$LAUF_START" .ralph-logs .team-logs .ralph-logs/archiv .team-logs/archiv; }
kontostand_gesamt() { team_kontostand_gesamt; }

# --- Deckel-Governance: Architekten-Empfehlung nur ANHEBEN, nie senken ------
# (Strippenzieher-Entscheid 2, Kaskade 6 Stufe 19). Eine explizite
# TEAM_BUDGET_USD-Übersteuerung durch den User hat immer Vorrang und wird
# nicht überschrieben — team_resolve_budget_cap kapselt die Regel isoliert
# testbar (siehe team-lib.sh).
BUDGET_EMPFEHLUNG="$(team_budget_empfehlung)"
NEUER_DECKEL="$(team_resolve_budget_cap "$TEAM_BUDGET_USD" "$TEAM_BUDGET_USD_USER_GESETZT" "$BUDGET_EMPFEHLUNG")"
if [ "$NEUER_DECKEL" != "$TEAM_BUDGET_USD" ]; then
    log "Deckel-Anhebung: Architekten-Empfehlung $BUDGET_EMPFEHLUNG USD > bisheriger Deckel $TEAM_BUDGET_USD USD — automatisch übernommen. Gesamt-Kontostand $(kontostand_gesamt) USD -> neuer Lauf-Deckel $NEUER_DECKEL USD."
    TEAM_BUDGET_USD="$NEUER_DECKEL"
fi

budget_ok() {
    local jetzt; jetzt="$(lauf_kosten)"
    if python3 -c "import sys; sys.exit(0 if float('$jetzt') >= float('$TEAM_BUDGET_USD') else 1)"; then
        log "LAUF-BUDGET erreicht: dieser Lauf $jetzt USD >= Deckel $TEAM_BUDGET_USD USD — harter Stopp (Gesamt-Kontostand $(kontostand_gesamt) USD, nur Anzeige)."
        return 1
    fi
    return 0
}

# --- Phase 1: Ralph baut die Kaskade -----------------------------------------
log "=== PHASE 1: Ralph (Bau der Kaskade) ==="
./ralph.sh; rc=$?
if [ "$rc" -eq 42 ]; then
    log "⏸ Session-Limit erreicht — Lauf pausiert (Ralph). Bitte später './vollautomatik.sh' erneut starten. Kein Fehler, kein Datenverlust (State steht)."
    exit 42
fi
if [ "$rc" -eq 43 ]; then
    # BL-41: Eigener Ausgang neben 0/1/42 — Ralphs Meldung nennt bereits den
    # Prüfweg. Hier NICHT als "Fehler" protokollieren: Der Lauf stoppt, aber
    # die bezahlte Arbeit ist mit hoher Wahrscheinlichkeit fertig, und ein
    # generisches "endete mit Fehler" hat im Feld viermal zum Neubau statt zum
    # Nachsehen geführt (19,47 USD).
    log "⚠ Stufe fertig, Quittung fehlt (BL-41) — Lauf gestoppt. NICHT neu bauen, bevor die von Ralph genannten zwei Prüfungen gelaufen sind."
    exit 43
fi
if [ "$rc" -ne 0 ]; then
    log "Ralph endete mit Fehler ($rc) — Vollautomatik stoppt, Mensch gefragt."
    exit 1
fi
budget_ok || exit 1

# --- Phase 2+3: Red-Team-Sweeps ----------------------------------------------
for rolle in harry marv; do
    log "=== PHASE Red Team: $rolle ==="
    ./"$rolle".sh; rc=$?
    case "$rc" in
        0) log "$rolle hat einen Sweep abgeschlossen." ;;
        3) log "$rolle: nichts Neues zu prüfen." ;;
        42) log "⏸ Session-Limit erreicht — Lauf pausiert ($rolle). Bitte später './vollautomatik.sh' erneut starten. Kein Fehler, kein Datenverlust (State steht)."; exit 42 ;;
        *) log "$rolle endete mit ECHTEM Fehler ($rc: is_error/Guard-Verletzung/Aufruf-Fehlschlag — ein bloß fehlendes Promise bei sauberem Fund liefert bereits 0) — Vollautomatik stoppt."; exit 1 ;;
    esac
    budget_ok || exit 1
done

# --- Phase 4: Fix-Runden (Frank ↔ Axel) --------------------------------------
# Auslauf-Bremse (Kaskade 11/Stufe 38, Architekt-Beobachtung 2026-07-11): Ein
# Fund kann über viele Runden hinweg IMMER WIEDER einen Fehlversuch/Fehler
# produzieren (getan=1, aber kein echter Fortschritt) — TEAM_MAX_RUNDEN allein
# deckelt das nur grob (bis zu 12 teure Runden). STAGNATION zählt Runden OHNE
# Fortschritt (kein Frank-Fix, keine neue Axel-Akte, kein Beutebuch-Statuswechsel)
# und bricht früh und benannt ab, statt leerzudrehen.
log "=== PHASE 4: Fix-Runden (max $MAX_RUNDEN, Auslauf-Bremse ab $STAGNATION_MAX Leerlauf-Runden in Folge) ==="
runde=0
stagnation=0
while [ "$runde" -lt "$MAX_RUNDEN" ]; do
    runde=$((runde + 1))
    getan=0
    fortschritt=0
    VORHER="$($TEAM_BEUTEBUCH_TOOL list)"

    ./frank.sh; rc=$?
    case "$rc" in
        0) getan=1; fortschritt=1; log "Runde $runde: Frank hat einen Fund gefixt." ;;
        3) : ;;  # kein Frank-Fund
        42) log "⏸ Session-Limit erreicht — Lauf pausiert (Frank). Bitte später './vollautomatik.sh' erneut starten. Kein Fehler, kein Datenverlust (State steht)."; exit 42 ;;
        *) getan=1; log "Runde $runde: Frank-Fehlversuch (ggf. Eskalation an Axel)." ;;
    esac
    budget_ok || exit 1

    # Axel nur rufen, wenn ein Fall auf ihn wartet.
    if $TEAM_BEUTEBUCH_TOOL first "an Axel übergeben" >/dev/null; then
        ./axel.sh; rc=$?
        case "$rc" in
            0) getan=1; fortschritt=1; log "Runde $runde: Axel hat eine Ermittlungsakte geliefert." ;;
            3) : ;;
            42) log "⏸ Session-Limit erreicht — Lauf pausiert (Axel). Bitte später './vollautomatik.sh' erneut starten. Kein Fehler, kein Datenverlust (State steht)."; exit 42 ;;
            *) getan=1; log "Runde $runde: Axel-Fehler ($rc) — Fall bleibt offen." ;;
        esac
        budget_ok || exit 1
    fi

    if [ "$getan" -eq 0 ]; then
        log "Runde $runde: nichts mehr zu tun — Fix-Phase beendet."
        break
    fi

    NACHHER="$($TEAM_BEUTEBUCH_TOOL list)"
    if [ "$fortschritt" -eq 0 ] && [ "$VORHER" = "$NACHHER" ]; then
        stagnation=$((stagnation + 1))
        log "Runde $runde: kein Fix/keine neue Akte/kein Statuswechsel — Stagnation $stagnation/$STAGNATION_MAX."
    else
        stagnation=0
    fi

    if [ "$stagnation" -ge "$STAGNATION_MAX" ]; then
        STUCK="$($TEAM_BEUTEBUCH_TOOL first 'an Frank übergeben' 2>/dev/null \
            || $TEAM_BEUTEBUCH_TOOL first 'Fix-Plan liegt vor' 2>/dev/null \
            || $TEAM_BEUTEBUCH_TOOL first 'an Axel übergeben' 2>/dev/null \
            || echo '?')"
        log "⛔ Fix-Phase stagniert: $STUCK macht seit $stagnation Runden keinen Fortschritt — Mensch prüfen. Lauf gestoppt, um Leerlaufkosten zu vermeiden."
        exit 1
    fi
done
[ "$runde" -ge "$MAX_RUNDEN" ] && log "WARNUNG: Rundenlimit ($MAX_RUNDEN) erreicht — evtl. offene Funde, Mensch prüfen."

# --- Abschluss ---------------------------------------------------------------
log "=== ABSCHLUSSBERICHT ==="
./team-status.sh || true
log "Dieser Lauf: $(lauf_kosten) USD (Deckel $TEAM_BUDGET_USD). Gesamt-Kontostand: $(kontostand_gesamt) USD."
command -v notify-send >/dev/null && \
    notify-send "T.E.A.M. Vollautomatik fertig" "Kaskade durch. Dieser Lauf: $(lauf_kosten) USD · Gesamt: $(kontostand_gesamt) USD" 2>/dev/null || true
log "Vollautomatik beendet."

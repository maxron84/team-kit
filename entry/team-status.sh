#!/usr/bin/env bash
# team-status.sh — Monitoring-Dashboard der T.E.A.M.-Vollautomatik.
# Zeigt Kaskaden-Stand, Beutebuch-Zählung, Kosten, Lock-Status und letzte
# Aktivität. Einmalig oder als Live-Ansicht.
#
# Aufruf:  ./team-status.sh            einmalige Momentaufnahme
#          ./team-status.sh --watch    Live (Refresh alle 5 s, Strg+C beendet)
#          ./team-status.sh --budget   Kumulierter Kontostand (Ledger + Logs)
#          ./team-status.sh --architekt-abschluss <USD> <domaene> ["<notiz>"]
#                                       A1-Ersetzung: echte Architekt-Zeile
#                                       (Konsolenwert) in .budget-ledger
#                                       eintragen, ersetzt eine vorhandene
#                                       Architekt-Zeile derselben Kaskade
#          ./team-status.sh --akteur-abschluss <rolle> <auth:abo|api> <USD>
#                            <domaene> ["<notiz>"]
#                                       Rollen-agnostische A1-Ersetzung
#                                       (BL-33, Kaskade 15/Stufe 51): wie
#                                       --architekt-abschluss, aber fuer JEDE
#                                       interaktiv (ausserhalb team_claude)
#                                       arbeitende Rolle, z. B.
#                                       `frank abo 12.34 produkt "…"`
#          ./team-status.sh --rollen-abschluss <kaskade> <domaene>
#                            ["<notiz>"]
#                                       Kaskadenscharfe Rollenkosten (BL-17-
#                                       Restpunkt/BL-29-"1b", Kaskade 16/
#                                       Stufe 54): ledgert die .team-logs-
#                                       Kosten (Harry/Marv/Frank/Axel) DIESER
#                                       Kaskade als EINE rolle=roles-Zeile und
#                                       archiviert .team-logs DANACH (analog
#                                       dem bestehenden .ralph-logs-Pflicht-
#                                       schritt). Nur manueller Kaskaden-
#                                       Abschluss, laeuft NICHT automatisch in
#                                       vollautomatik.sh.
#          ./team-status.sh --ledger-pruefen [--kaskade N]
#                                       Konsistenzpruefung des Ledgers
#                                       (Skizze D): fehlende Zeile je Quelle,
#                                       unarchivierte Logs bei bereits
#                                       gebuchter Kaskade, und die Gegenprobe
#                                       gegen die archivierten Rohlogs.
#                                       Exit 4 = Warnbefunde, 0 = sauber oder
#                                       nur Hinweise. Laeuft bei --budget
#                                       ungefragt mit (dort nur Anzeige).
#          ./team-status.sh --beutebuch-archivieren [--dry-run]
#                                       Verschiebt erledigte/ueberholte Funde
#                                       (Kaskade 22/Stufe 91) wortgleich nach
#                                       plans/beutebuch-archiv.md. Manuelles
#                                       Abschluss-Werkzeug, NICHT in
#                                       vollautomatik.sh verdrahtet.
set -uo pipefail
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh

RALPH_CAP_VALUE="$(team_ralph_cap)"

status_einmal() {
    echo "════════════════════════════════════════════════════════"
    echo "  T.E.A.M.-Status — $(date '+%Y-%m-%d %H:%M:%S')"
    echo "════════════════════════════════════════════════════════"

    # Kaskade
    local stufe; stufe="$( [ -f .ralph-state ] && tr -d '[:space:]' < .ralph-state || echo '?')"
    echo "  Kaskade : nächste Stufe $stufe / Cap ${RALPH_CAP_VALUE:-?}"
    if [ "${RALPH_CAP_VALUE:-0}" != "0" ] && [ "$stufe" != "?" ] \
       && [ "$stufe" -gt "${RALPH_CAP_VALUE:-0}" ] 2>/dev/null; then
        echo "            → Bau abgeschlossen (Ralph hat Feierabend)."
    fi

    # Lock
    if [ -f .team-loop.lock ] && command -v flock >/dev/null \
       && ! flock -n .team-loop.lock true 2>/dev/null; then
        echo "  Pipeline: 🟢 läuft gerade (Lock gehalten)"
    else
        echo "  Pipeline: ⚪ idle"
    fi

    # Beutebuch
    echo "  ──────── Beutebuch ────────"
    local counts; counts="$($TEAM_BEUTEBUCH_TOOL count 2>/dev/null || true)"
    if [ -n "$counts" ]; then
        printf '%s\n' "$counts" | while IFS=$'\t' read -r st n; do
            printf "    %-32s %s\n" "$st" "$n"
        done
    else
        echo "    (keine Funde)"
    fi

    # Kosten — LEBENSLANG kumuliert, NICHT „dieser Lauf" (BL-24). Die
    # Aufschlüsselung Ralph/Team summiert alle *nicht archivierten* Logs der
    # jeweiligen Ordner (das BL-17-Archiv .ralph-logs/archiv/ fällt bewusst aus
    # dem nicht-rekursiven glob() und ist hier daher nicht enthalten — die
    # verlässliche Gesamtzahl ist die Ledger-gestützte „Gesamt"-Zeile). Die
    # Pro-Lauf-Kosten stehen separat in der vollautomatik.sh-Schlusszeile
    # („Dieser Lauf: … USD", Kennzahl A). „Gesamt" hier = Kennzahl B
    # (team_kontostand_gesamt, inkl. .budget-ledger-Basis) — dieselbe Zahl wie
    # `--budget`, damit nie zwei widersprüchliche „Gesamt"-Werte entstehen.
    echo "  ──────── Kosten (lebenslang kumuliert) ────────"
    local k_ralph k_team k_gesamt k_architekt
    k_ralph="$(team_kosten_summe .ralph-logs)"
    k_team="$(team_kosten_summe .team-logs)"
    k_gesamt="$(team_kontostand_gesamt)"
    k_architekt="$(team_architekt_schaetzung)"
    printf "    Ralph-Logs (Bau, o. Archiv)   : %9s USD\n" "$k_ralph"
    printf "    Team-Logs (Fixe, o. Archiv)   : %9s USD\n" "$k_team"
    printf "    Architekt (geschätzt, A2)     : %9s USD\n" "$k_architekt"
    printf "    Gesamt-Kontostand (inkl. Ledger): %9s USD\n" "$k_gesamt"

    # Letzte Aktivität
    echo "  ──────── Letzte Commits ────────"
    git log --oneline -5 2>/dev/null | sed 's/^/    /' || echo "    (kein Git-Log)"
    # Neue Läufe schreiben vollautomatik-*.log; ältere (vor der Umbenennung
    # pock/wache -> halbautomatik/vollautomatik, BL-19) heißen noch wache-*.log —
    # beide Muster berücksichtigen, damit historische Logs weiter gefunden werden.
    local letzte_lauf; letzte_lauf="$(ls -t .team-logs/vollautomatik-*.log .team-logs/wache-*.log 2>/dev/null | head -1 || true)"
    if [ -n "$letzte_lauf" ]; then
        echo "  ──────── Vollautomatik (letzte 3 Zeilen: $(basename "$letzte_lauf")) ────────"
        tail -n 3 "$letzte_lauf" | sed 's/^/    /'
    fi
    echo "════════════════════════════════════════════════════════"
}

# status_budget: kumulierter Kontostand = historische .budget-ledger-Basis
# plus aktuelle lokale Logs (.ralph-logs/ + .team-logs/), Abo/API getrennt
# ausgewiesen (Strippenzieher-Entscheid 3, siehe
# plans/ralph-kaskade-6-budget-governance.md, Stufe 18). Mit leeren
# Log-Ordnern ist die Ausgabe exakt die Ledger-Basissumme.
status_budget() {
    local abo api gesamt empfehlung
    local architekt_usd architekt_status
    local ledger_gesamt ledger_unzugeordnet
    local _domaenen_liste _domaenen_anzahl _summe_domaenen _d _wert
    local ledger_abo ledger_api ledger_gemischt api_gesamt abo_gesamt
    IFS=$'\t' read -r abo api <<<"$(team_kosten_split .ralph-logs .team-logs)"
    IFS=$'\t' read -r ledger_abo ledger_api ledger_gemischt <<<"$(team_ledger_split)"
    gesamt="$(team_kontostand_gesamt)"
    IFS=$'\t' read -r architekt_usd architekt_status <<<"$(team_architekt_stand)"

    # Ledger-Anteil (auth-Spalte, BL-17-Restpunkt/BL-29-"1b", Stufe 53) zu den
    # Live-Logs addieren, damit die beiden Kopfzeilen nach einer Archivierung
    # (team_logs_archivieren) nicht mehr nur den Live-Teil zeigen. "gemischt"
    # (v. a. Ledger-Zeilen mit auth="abo/api") bleibt eine eigene, ehrliche
    # dritte Zeile statt geraten aufgeteilt zu werden. Werte defensiv als
    # eigene argv-Elemente an python3 (kein rohes ${…}-Interpolieren — BL-23/
    # HM-17).
    api_gesamt="$(python3 -c "
import sys
a, b = (float(x) for x in sys.argv[1:3])
print(f'{a + b:.4f}')
" "$api" "$ledger_api")"
    abo_gesamt="$(python3 -c "
import sys
a, b = (float(x) for x in sys.argv[1:3])
print(f'{a + b:.4f}')
" "$abo" "$ledger_abo")"

    echo "════════════════════════════════════════════════════════"
    echo "  T.E.A.M.-Kontostand — $(date '+%Y-%m-%d %H:%M:%S')"
    echo "════════════════════════════════════════════════════════"
    printf "  real via API abgerechnet           : %s USD\n" "$api_gesamt"
    printf "  Abo-Gegenwert (nicht abgerechnet)  : %s USD\n" "$abo_gesamt"
    printf "  gemischt (Ledger, nicht aufteilbar): %s USD\n" "$ledger_gemischt"
    printf "  Architekt (%s, nicht im Gesamt enthalten): %s USD\n" "$architekt_status" "$architekt_usd"
    printf "  Gesamt (Basis + laufend)           : %s USD\n" "$gesamt"

    # Domänengetrennte Ledger-Aufstellung (BL-29, Kaskade 13/Stufe 44). Nur
    # die committete .budget-ledger trägt bislang eine Domäne je Zeile (ab
    # Kaskade 13) — Altzeilen davor zählen als "unzugeordnet", NIE
    # stillschweigend einer Domäne zugeschlagen (siehe scripts/kosten.py).
    ledger_gesamt="$(team_ledger_summe)"
    # BL-9: Der Block erscheint nur, wenn dieses Projekt WIRKLICH mehrere
    # Domänen führt. Bei genau einer wiederholt er nur die Gesamtsumme und
    # zeigte zusätzlich eine feste "🔧 T.E.A.M."-Zeile, die in einem
    # Feldprojekt strukturell 0.0000 ist: Am Team wird hier nicht gearbeitet,
    # Funde werden ins Kit-Repo zurückgespielt und dort verbucht. Eine Zeile,
    # die immer null zeigt, erzieht dazu, den ganzen Block zu überlesen.
    _domaenen_liste="$(printf %s "${TEAM_DOMAENEN:-produkt}" | tr "," " ")"
    _domaenen_anzahl="$(printf %s "$_domaenen_liste" | wc -w)"
    if [ "$_domaenen_anzahl" -gt 1 ]; then
        echo "  ──────── Domänen (Ledger-Basis) ────────"
        _summe_domaenen=0
        for _d in $_domaenen_liste; do
            _wert="$(team_ledger_domaene "$_d")"
            printf "    📦 %-30s: %s USD\n" "$_d" "$_wert"
            _summe_domaenen="$(python3 -c "
import sys
print(f'{float(sys.argv[1]) + float(sys.argv[2]):.4f}')
" "$_summe_domaenen" "$_wert")"
        done
        ledger_unzugeordnet="$(python3 -c "
import sys
g, d = (float(x) for x in sys.argv[1:3])
print(f'{g - d:.4f}')
" "$ledger_gesamt" "$_summe_domaenen")"
        printf "    ⚪ %-30s: %s USD\n" "unzugeordnet" "$ledger_unzugeordnet"
    fi

    # BL-23: KEIN B/A-Prozent mehr. Der Gesamt-Kontostand B (lebenslang
    # kumuliert) und der Pro-Lauf-Deckel A (BUDGET_EMPFEHLUNG_USD) sind laut
    # BL-18/CLAUDE.md strikt getrennte Kennzahlen — sie gegeneinander zu
    # prozentuieren suggeriert fälschlich ein „gesprengtes Budget" (real
    # 205 % ausgeschoepft), obwohl die Pro-Lauf-Durchsetzung (vollautomatik.sh
    # budget_ok → team_kosten_seit LAUF_START) davon völlig unberührt ist.
    # Die Empfehlung wird nur informativ ausgewiesen und klar als Pro-Lauf-
    # Deckel gekennzeichnet. Werte defensiv per Argument an python3 übergeben
    # (kein rohes ${…}-Interpolieren → kein SyntaxError bei leerem Wert).
    empfehlung="$(team_budget_empfehlung)"
    if [ -n "$empfehlung" ]; then
        python3 -c "
import sys
d = float(sys.argv[1]) if sys.argv[1] else 0.0
print(f'  Empf. Pro-Lauf-Deckel (naechster Lauf): {d:.2f} USD')
print('  Hinweis: Pro-Lauf-Deckel gilt gegen die Kosten EINES Laufs,')
print('           nicht gegen den kumulierten Gesamt-Kontostand oben.')
" "$empfehlung"
    fi

    # Skizze D: Der Kontostand prüft ungefragt seine eigene Vollständigkeit
    # mit — und zwar gegen die archivierten Rohlogs, also gegen eine ANDERE
    # Quelle als die Zahlen darüber. Genau das fehlte bei BL-1/BL-4/BL-5:
    # Alle drei Berichte zogen ihre Kennzahl aus derselben Quelle wie der
    # Fehler und bestätigten ihn deshalb, statt ihn zu zeigen. Bewusst nur
    # ANZEIGE: `--budget` bleibt exit 0, auch wenn Befunde vorliegen. Das
    # Detail liefert `--ledger-pruefen` (exit 4).
    local _befunde
    _befunde="$($TEAM_KOSTEN_TOOL ledger-pruefen 2>/dev/null || true)"
    case "$_befunde" in
        *WARNUNG*)
            echo "  ──────── Ledger-Konsistenz ────────"
            printf %s "$_befunde" | grep '^\[WARNUNG\]' | sed 's/^/    /'
            echo "    → Details: ./team-status.sh --ledger-pruefen"
            ;;
    esac
    echo "════════════════════════════════════════════════════════"
}

# status_architekt_abschluss: A1-Ersetzung (BL-28, Stufe 43) — haengt die
# echte Architekt-Ledger-Zeile an (Konsolenwert vom Strippenzieher abgelesen)
# und ersetzt dabei eine vorhandene Architekt-Zeile derselben Kaskade
# (Idempotenz). Alle Werte gehen als eigene argv-Elemente an python3 (kein
# python3 -c mit roher String-Interpolation — Lehre aus BL-23/HM-17).
status_architekt_abschluss() {
    local usd="${1:-}" domaene="${2:-}" notiz="${3:-}"
    if [ -z "$usd" ] || [ -z "$domaene" ]; then
        echo "Nutzung: $0 --architekt-abschluss <USD> <domaene> [\"<notiz>\"]" >&2
        return 1
    fi
    if [ -n "$notiz" ]; then
        $TEAM_KOSTEN_TOOL architekt-abschluss --usd "$usd" \
            --domaene "$domaene" --notiz "$notiz"
    else
        $TEAM_KOSTEN_TOOL architekt-abschluss --usd "$usd" \
            --domaene "$domaene"
    fi
}

# status_akteur_abschluss: rollen-agnostische A1-Ersetzung (BL-33, Kaskade
# 15/Stufe 51) — wie status_architekt_abschluss, aber mit expliziter
# Rolle/Auth statt der festen architekt/api-Vorbelegung. Reicht alle Werte
# als eigene argv-Elemente an team_akteur_abschluss()/kosten.py weiter (kein
# python3 -c mit roher Interpolation — BL-23/HM-17).
status_akteur_abschluss() {
    local rolle="${1:-}" auth="${2:-}" usd="${3:-}" domaene="${4:-}" notiz="${5:-}"
    if [ -z "$rolle" ] || [ -z "$auth" ] || [ -z "$usd" ] || [ -z "$domaene" ]; then
        echo "Nutzung: $0 --akteur-abschluss <rolle> <auth:abo|api> <USD> <domaene> [\"<notiz>\"]" >&2
        return 1
    fi
    team_akteur_abschluss "$rolle" "$auth" "$usd" "$domaene" "$notiz"
}

# status_rollen_abschluss: kaskadenscharfer .team-logs-Abschluss (BL-17-
# Restpunkt/BL-29-"1b", Kaskade 16/Stufe 54; Ein-Prozess-Fix HM-39/AX-4,
# Kaskade "ledger-race") — ledgert die .team-logs-Kosten DIESER Kaskade als
# EINE rolle=roles-Zeile UND archiviert .team-logs in EINEM Python-Aufruf
# (kosten.py rollen-abschluss --archivieren), statt Zaehlen (Python) und
# Archivieren (vorher: team_logs_archivieren als eigener Bash-Schritt danach)
# auf zwei getrennte Snapshots zu zwei verschiedenen Zeitpunkten zu verteilen
# — genau das war der Race: ein zwischen den beiden Schritten neu
# entstandenes Log wurde ungezaehlt trotzdem archiviert und war fortan aus
# jeder Kostenrechnung verschwunden. kosten.py archiviert jetzt intern exakt
# die bei der Zaehlung gefasste Dateiliste, NACHDEM die Ledger-Zeile
# erfolgreich geschrieben wurde (bei Fehler wird nicht archiviert — die noch
# ungesicherten .team-logs bleiben liegen). Werte gehen als eigene
# argv-Elemente an python3 (kein python3 -c mit roher Interpolation —
# BL-23/HM-17). team_logs_archivieren() bleibt fuer den .ralph-logs-Abschluss
# unveraendert bestehen (dort kein vergleichbarer Race, da nur der
# sequentielle Ralph-Loop unter Lock schreibt).
#
# BL-5: Steht fuer die Kaskade schon eine roles-Zeile, bricht der Aufruf ab,
# statt sie zu ueberschreiben — die Fehlermeldung nennt Alt-, Neu- und
# Summenwert. --addieren (Nachlauf: eine Rolle lief nach dem Abschluss noch)
# und --ersetzen (Korrektur einer falschen Altzeile) werden als optionaler
# vierter Parameter durchgereicht.
status_rollen_abschluss() {
    local kaskade="${1:-}" domaene="${2:-}" notiz="${3:-}" modus="${4:-}"
    if [ -z "$kaskade" ] || [ -z "$domaene" ]; then
        echo "Nutzung: $0 --rollen-abschluss <kaskade> <domaene> [\"<notiz>\"] [--addieren|--ersetzen]" >&2
        return 1
    fi
    case "$modus" in
        ""|--addieren|--ersetzen) ;;
        *) echo "Unbekannter Modus '$modus' — erlaubt: --addieren, --ersetzen" >&2
           return 1 ;;
    esac

    # BL-4: BEIDE Kostenquellen einer Kaskade abschliessen — .team-logs
    # (Harry/Marv/Frank/Axel -> rolle=roles) UND .ralph-logs (Bau -> rolle=
    # ralph). Zwei getrennte Ledger-Zeilen, EINE Bedienhandlung: Ralphs
    # Baukosten fielen im Feld nur deshalb aus dem committeten Ledger, weil
    # sie einen zweiten, nirgends vorgeschriebenen Befehl gebraucht haetten.
    # Beide Verben laufen unabhaengig: Bricht einer ab (z. B. BL-5-Bestand),
    # wird der andere trotzdem versucht und der Fehler am Ende gemeldet.
    local rc=0 einzel_rc verb
    for verb in rollen-abschluss ralph-abschluss; do
        einzel_rc=0
        if [ -n "$notiz" ]; then
            $TEAM_KOSTEN_TOOL "$verb" --kaskade "$kaskade" \
                --domaene "$domaene" --notiz "$notiz" --archivieren \
                ${modus:+"$modus"} || einzel_rc=$?
        else
            $TEAM_KOSTEN_TOOL "$verb" --kaskade "$kaskade" \
                --domaene "$domaene" --archivieren ${modus:+"$modus"} || einzel_rc=$?
        fi
        [ "$einzel_rc" -eq 0 ] || rc="$einzel_rc"
    done
    return "$rc"
}

# status_ledger_pruefen: reicht auf kosten.py ledger-pruefen durch (Skizze D).
# Exit 4 = Warnbefunde, 0 = sauber oder nur Hinweise, 1 = Bedienfehler.
status_ledger_pruefen() {
    $TEAM_KOSTEN_TOOL ledger-pruefen "$@"
}

# status_beutebuch_archivieren: reicht auf beutebuch.py archiviere durch
# (Kaskade 22/Stufe 91). Bewusst NICHT in vollautomatik.sh verdrahtet
# (Strippenzieher-Entscheid, plans/ralph-kaskade-22-doku-konsolidierung.md) —
# ein laufender Sweep darf nie unter seinen eigenen Funden rotieren. Rein
# manuelles Abschluss-Werkzeug wie --rollen-abschluss.
status_beutebuch_archivieren() {
    $TEAM_BEUTEBUCH_TOOL archiviere "$@"
}

if [ "${1:-}" = "--budget" ]; then
    status_budget
elif [ "${1:-}" = "--architekt-abschluss" ]; then
    shift
    status_architekt_abschluss "$@"
elif [ "${1:-}" = "--akteur-abschluss" ]; then
    shift
    status_akteur_abschluss "$@"
elif [ "${1:-}" = "--rollen-abschluss" ]; then
    shift
    status_rollen_abschluss "$@"
elif [ "${1:-}" = "--ledger-pruefen" ]; then
    shift
    status_ledger_pruefen "$@"
elif [ "${1:-}" = "--beutebuch-archivieren" ]; then
    shift
    status_beutebuch_archivieren "$@"
elif [ "${1:-}" = "--watch" ]; then
    trap 'echo; echo "Monitoring beendet."; exit 0' INT
    while true; do
        clear
        status_einmal
        echo "  (--watch: Refresh 5 s · Strg+C beendet)"
        sleep 5
    done
else
    status_einmal
fi

#!/usr/bin/env bash
# kit-test.sh — Selbstverifikation des Kits (BL-6).
#
# Aufruf:  ./kit-test.sh [--behalten] [weitere pytest-Argumente]
#
#   --behalten   Das Wegwerf-Repo nach dem Lauf NICHT löschen (Fehlersuche).
#
# WARUM ES DIESES SKRIPT GIBT
#
# Die 138 Regressionstests unter team/tests/ setzen die INSTALLIERTE Ablage
# voraus: Entrypoints in der Repo-Wurzel, CLAUDE.md und team.config.sh mit
# gefüllten Platzhaltern. Im Kit-Repo liegen sie unter entry/ und bootstrap/ —
# `pytest team/tests` schlägt hier deshalb mit 17 Fehlern fehl, ohne dass
# irgendetwas kaputt wäre. Ergebnis: Ein im Kit committeter Fix war bis zur
# nächsten Feldinstallation ungeprüft. Genau so ging BL-1 (tote Fixphase) durch
# drei Releases.
#
# Statt die Tests layout-agnostisch zu machen, prüft dieses Skript dort, wo die
# Tests gelten: in einer echten Installation. Das prüft den Installer gleich mit.
#
# Das Zielrepo ist ein frisches mktemp-Verzeichnis — ein Wegwerf-Repo im Sinne
# der README-Regel "Guard-Tests nie im echten Projekt". Es wird am Ende
# gelöscht (außer bei --behalten). Dieses Skript ruft KEINE Agenten-CLI auf und
# kostet daher nichts.
set -euo pipefail
cd "$(dirname "$0")"
KIT="$(pwd)"

BEHALTEN=0
PYTEST_ARGS=()
for arg in "$@"; do
    case "$arg" in
        --behalten) BEHALTEN=1 ;;
        *)          PYTEST_ARGS+=("$arg") ;;
    esac
done

rot()  { printf '\033[31m%s\033[0m\n' "$*"; }
gruen(){ printf '\033[32m%s\033[0m\n' "$*"; }
kopf() { printf '\n\033[1m%s\033[0m\n' "$*"; }

if ! command -v pytest >/dev/null 2>&1; then
    rot "pytest nicht gefunden — die Selbstverifikation braucht es."
    echo "  Installation: pip install --user pytest" >&2
    exit 2
fi

ZIEL="$(mktemp -d "${TMPDIR:-/tmp}/team-kit-selbsttest.XXXXXX")"
aufraeumen() {
    if [ "$BEHALTEN" -eq 1 ]; then
        printf '\nWegwerf-Repo behalten: %s\n' "$ZIEL"
    else
        rm -rf "$ZIEL"
    fi
}
trap aufraeumen EXIT

kopf "1/4 — Wegwerf-Repo anlegen"
git -C "$ZIEL" init -q
# Lokale Identität, damit der Lauf auch ohne globale Git-Config committen kann.
git -C "$ZIEL" config user.email "kit-test@localhost"
git -C "$ZIEL" config user.name  "Kit-Selbsttest"
gruen "  ✓ $ZIEL"

kopf "2/4 — Kit installieren (nicht-interaktiv)"
# Ohne TEAM_INIT_*-Vorgaben: genau die Defaults, die ein Anwender bekäme.
if ! bash "$KIT/install.sh" "$ZIEL" --nicht-interaktiv > "$ZIEL/.install.log" 2>&1; then
    rot "  ✗ install.sh schlug fehl:"
    tail -20 "$ZIEL/.install.log" >&2
    exit 1
fi
gruen "  ✓ $(grep -oE 'Fertig — [0-9]+ Dateien geschrieben' "$ZIEL/.install.log" | head -1)"

kopf "3/4 — Ungefüllte Platzhalter suchen"
# Ein übrig gebliebenes {{...}} heißt: Der Installer kennt die Datei nicht oder
# der Platzhalter wurde umbenannt. Beides fällt sonst erst im Feld auf, wo die
# Briefings die Pfade des Ursprungsprojekts nennen würden — falsche Guard-Grenze.
RESTE="$(grep -rlE '\{\{[A-Z_]+\}\}' "$ZIEL" \
           --exclude-dir=.git --exclude=.install.log 2>/dev/null || true)"
if [ -n "$RESTE" ]; then
    rot "  ✗ Ungefüllte Platzhalter in:"
    echo "$RESTE" | sed 's|^|      |' >&2
    exit 1
fi
gruen "  ✓ keine"

kopf "4/5 — Regressionstests in der Installation"
# Vor dem Testlauf committen — dieselbe Reihenfolge, die TEAM.md dem Anwender
# vorschreibt. Ein Test, der den Git-Zustand liest, sieht damit den echten.
git -C "$ZIEL" add -A
git -C "$ZIEL" commit -q -m "chore: T.E.A.M. eingerichtet"

cd "$ZIEL"
if ! ./team-test.sh "${PYTEST_ARGS[@]}"; then
    RC=$?
    rot "
✗ Kit-Selbstverifikation FEHLGESCHLAGEN (Exit $RC)."
    [ "$BEHALTEN" -eq 0 ] && echo "  Mit --behalten erneut laufen lassen, um im Repo nachzusehen." >&2
    exit "$RC"
fi

# BL-8: --update ist der einzige sichere Weg, ein gelebtes Projekt auf eine
# neue Kit-Version zu heben. Der Beweis dafuer gehoert ins Gate, nicht in ein
# einmaliges Handprotokoll: Wir tun so, als sei das Projekt in Betrieb
# (Ledger, Kaskadenstand, Beutebuch-Fund, eigener Smoke-Test), fahren das
# Update und pruefen, dass davon NICHTS angefasst wurde.
kopf "5/5 — Update-Pfad schuetzt Projektdaten"
echo '2026-08-01 | 1 | 9.4204 | abo | produkt | roles | Lauf' >> "$ZIEL/.budget-ledger"
echo '### HM-1 — echter Fund' >> "$ZIEL/plans/beutebuch.md"
echo '5' > "$ZIEL/.ralph-state"
sed -i 's|^TEAM_SMOKE_TEST=.*|TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-./smoke.sh}"|' \
    "$ZIEL/team.config.sh"
# Ein Test, den das Kit nicht kennt — wie ihn ein Projekt schreibt, das eine
# Luecke im Team selbst schliesst, bevor der Fund im Kit ankommt.
printf 'def test_projekteigener_fund():\n    assert True\n' \
    > "$ZIEL/team/tests/test_projekteigener_fund.py"
# Eine lokal veraenderte Infrastruktur-Datei — der Fall, in dem ein noch nicht
# zurueckgemeldeter Fix vom Update ueberschrieben wird.
printf '\n# lokaler Fix, noch nicht ans Kit gemeldet\n' >> "$ZIEL/team/tools/beutebuch.py"

if ! bash "$KIT/install.sh" "$ZIEL" --update > "$ZIEL/.update.log" 2>&1; then
    rot "  ✗ install.sh --update schlug fehl:"
    tail -20 "$ZIEL/.update.log" >&2
    exit 1
fi

UPDATE_FEHLER=0
pruefe() {  # pruefe <beschreibung> <ist> <soll>
    if [ "$2" = "$3" ]; then
        gruen "  ✓ $1"
    else
        rot "  ✗ $1 — erwartet '$3', ist '$2'"
        UPDATE_FEHLER=1
    fi
}
pruefe "Ledger unangetastet"      "$(grep -c 'Lauf$' "$ZIEL/.budget-ledger")" "1"
pruefe "Kaskadenstand unangetastet" "$(cat "$ZIEL/.ralph-state")"             "5"
pruefe "Beutebuch-Fund erhalten"  "$(grep -c 'HM-1' "$ZIEL/plans/beutebuch.md")" "1"
pruefe "Smoke-Test in der Config erhalten" \
       "$(grep -c 'smoke.sh' "$ZIEL/team.config.sh")" "1"
# BL-12: NICHT loeschen. Ein Testfile, das das Kit nicht kennt, kann ein
# projekteigener Infrastruktur-Test sein — im Feld hat ein pauschales rm genau
# so einen geloescht. Es bleibt liegen und wird gemeldet.
pruefe "projekteigener Test in team/tests bleibt erhalten" \
       "$([ -f "$ZIEL/team/tests/test_projekteigener_fund.py" ] && echo da || echo weg)" "da"
pruefe "und wird als unbekannt gemeldet" \
       "$(grep -c 'test_projekteigener_fund.py' "$ZIEL/.update.log")" "1"
pruefe "lokal abweichende Infrastruktur wird gemeldet" \
       "$(grep -c 'bitte gegenlesen' "$ZIEL/.update.log")" "1"
pruefe "keine offenen Platzhalter in den Briefings" \
       "$(grep -rlE '\{\{[A-Z_]+\}\}' "$ZIEL/team/prompts/" | wc -l)" "0"
[ "$UPDATE_FEHLER" -eq 0 ] || exit 1

gruen "
✓ Kit-Selbstverifikation grün."

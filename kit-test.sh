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

kopf "4/4 — Regressionstests in der Installation"
# Vor dem Testlauf committen — dieselbe Reihenfolge, die TEAM.md dem Anwender
# vorschreibt. Ein Test, der den Git-Zustand liest, sieht damit den echten.
git -C "$ZIEL" add -A
git -C "$ZIEL" commit -q -m "chore: T.E.A.M. eingerichtet"

cd "$ZIEL"
if ./team-test.sh "${PYTEST_ARGS[@]}"; then
    gruen "
✓ Kit-Selbstverifikation grün."
else
    RC=$?
    rot "
✗ Kit-Selbstverifikation FEHLGESCHLAGEN (Exit $RC)."
    [ "$BEHALTEN" -eq 0 ] && echo "  Mit --behalten erneut laufen lassen, um im Repo nachzusehen." >&2
    exit "$RC"
fi

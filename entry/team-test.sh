#!/usr/bin/env bash
# team-test.sh — führt die Regressionstests der TEAM-INFRASTRUKTUR aus.
#
# Bewusst getrennt vom Testlauf des Projekts: Die Team-Tests sind pytest und
# prüfen team/lib.sh, team/tools/*.py und die Briefings — nicht deinen Code.
# Dein Projekt behält seinen eigenen Test-Befehl (siehe TEAM_SMOKE_TEST).
#
# Aufruf:  ./team-test.sh [weitere pytest-Argumente]
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v pytest >/dev/null 2>&1; then
    echo "pytest nicht gefunden — die Team-Tests brauchen es." >&2
    echo "  Installation: pip install --user pytest" >&2
    echo "  (Abhängigkeit der Team-Infrastruktur, nicht deines Projekts.)" >&2
    exit 2
fi
exec pytest -q team/tests "$@"

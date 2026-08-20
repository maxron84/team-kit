#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: team-test.ps1
# team-test.sh — führt die Regressionstests der TEAM-INFRASTRUKTUR aus.
#
# Bewusst getrennt vom Testlauf des Projekts: Die Team-Tests sind pytest und
# prüfen team/lib.sh, team/tools/*.py und die Briefings — nicht deinen Code.
# Dein Projekt behält seinen eigenen Test-Befehl (siehe TEAM_SMOKE_TEST).
#
# Aufruf:  ./team-test.sh [weitere pytest-Argumente]
set -euo pipefail
cd "$(dirname "$0")"

# BL-124: pytest wird AUFGELÖST, nicht vorausgesetzt.
#
# `pip install --user pytest` — genau der Befehl, den diese Datei bisher
# empfahl — legt die ausführbare Datei in ein Scripts-/bin-Verzeichnis, das oft
# NICHT im PATH steht; pip warnt beim Installieren sogar davor. Das Modul ist
# dann installiert, und `command -v pytest` findet trotzdem nichts. Diese Datei
# meldete daraufhin "pytest nicht gefunden" und empfahl noch einmal genau die
# Installation, die den Zustand erzeugt hatte.
#
# Der Weg über den Interpreter findet es in beiden Fällen — und benutzt
# garantiert DASSELBE Python wie die übrigen Team-Werkzeuge. Ein `pytest` im
# PATH kann zu einer anderen Installation gehören als das Python, unter dem
# team/tools/ läuft; dann testet man etwas anderes, als man betreibt.
for TEAM_PY in python3 python py; do
    command -v "$TEAM_PY" >/dev/null 2>&1 || continue
    if "$TEAM_PY" -m pytest --version >/dev/null 2>&1; then
        exec "$TEAM_PY" -m pytest -q team/tests "$@"
    fi
done
# Letzter Versuch: ein pytest im PATH, dessen Interpreter wir nicht kennen.
if command -v pytest >/dev/null 2>&1; then
    exec pytest -q team/tests "$@"
fi
echo "pytest nicht gefunden — die Team-Tests brauchen es." >&2
echo "  Gesucht wurde als MODUL (python3/python/py -m pytest) und als Befehl." >&2
echo "  Installation:  python3 -m pip install --user pytest" >&2
echo "  Debian/Ubuntu: sudo apt install python3-pytest" >&2
echo "  (Abhängigkeit der Team-Infrastruktur, nicht deines Projekts.)" >&2
exit 2

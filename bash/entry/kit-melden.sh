#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: kit-melden.ps1
# kit-melden.sh — Rückkanal Feld → Kit: einen Fund am T.E.A.M. SELBST melden.
#
# Für Funde an deinem PROJEKT ist dieses Skript falsch — die gehören ins
# Beutebuch bzw. in den Backlog des Projekts. Hier geht es um Fehler in der
# Team-Infrastruktur: in team/, in einem Entrypoint (*.sh in der Wurzel) oder
# in einer Regel aus CLAUDE.md/TEAM.md. Erkennungsmerkmal: Der Fehler trifft
# jede weitere Installation, und dieses Projekt repariert ihn bei jedem
# `--update` aufs Neue.
#
# Aufruf:
#   ./kit-melden.sh neu --titel "…"     Entwurf nach Vorlage anlegen
#   ./kit-melden.sh pruefen             Redaktionsprüfung (Exit 4 = Befunde)
#   ./kit-melden.sh senden <datei>      Pull Request — fragt vorher
#   ./kit-melden.sh issue-link <datei>  nur den vorbefüllten Link
#   ./kit-melden.sh kit-pfad            wo liegt das Kit? (Diagnose)
#
# WARUM SENDEN EINE EIGENE HANDLUNG IST: Ein Pull Request wirkt nach außen und
# lässt sich nicht zurückholen, und die Meldung schreibt eine Rolle, die gerade
# eine private Codebasis gelesen hat. `neu` und `pruefen` dürfen automatisch
# laufen, `senden` nicht — dieselbe Trennung wie „Finder ≠ Fixer".
set -uo pipefail
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh

# Die Werte werden AUSDRÜCKLICH durchgereicht statt exportiert: Ein Werkzeug,
# das seine Eingaben aus der Umgebung errät, verhält sich je nach Aufrufer
# anders — und der Aufrufer ist hier mal ein Mensch, mal eine Rolle, mal ein
# Test. Dieselbe Bauart wie bei beutebuch.py (--pfad).
exec "$TEAM_PYTHON" team/tools/kit_meldung.py \
    --projektwurzel . \
    --meldungen "${TEAM_PLAN_ORDNER%/}/kit-meldungen" \
    --kit "${TEAM_KIT_PFAD:-}" \
    --projekt "${TEAM_PROJEKT:-}" \
    "$@"

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
#   ./kit-melden.sh ablegen <datei>     ins lokal liegende Kit legen + committen
#   ./kit-melden.sh senden <datei>      Pull Request — fragt vorher
#   ./kit-melden.sh issue-link <datei>  nur den vorbefüllten Link
#   ./kit-melden.sh kit-pfad            wo liegt das Kit? (Diagnose)
#
# WARUM SENDEN EINE EIGENE HANDLUNG IST: Ein Pull Request wirkt nach außen und
# lässt sich nicht zurückholen, und die Meldung schreibt eine Rolle, die gerade
# eine private Codebasis gelesen hat. `neu` und `pruefen` dürfen automatisch
# laufen, `senden` nicht — dieselbe Trennung wie „Finder ≠ Fixer".
#
# ABLEGEN ODER SENDEN (BL-227, der Rest von BL-187): Liegt das Kit geklont
# daneben und zeigt TEAM_KIT_PFAD darauf, ist `ablegen` der Weg — es committet
# PFADGENAU ins Kit und pusht NICHT. `senden` ist für Melder OHNE Kit-Repo.
# Ein Owner, der einen Pull Request gegen sein eigenes Repo anlegt, reviewt und
# merged seine eigene Meldung; BL-187 hat das festgestellt und Rollen-Briefing,
# TEAM.md und CLAUDE.md.vorlage nachgezogen — dieser Hilfetext blieb stehen.
# Wer das Werkzeug über seine eigene Hilfe erschließt, fand deshalb weiter nur
# `senden`, also genau den Weg, von dem BL-187 sagt, dass er hier der falsche
# ist.
#
# `ablegen` ist dabei nicht das lockerere `senden`, sondern das straffere: kein
# Push (den macht ein Mensch, der den Text gelesen hat), keine BL-Nummer (die
# vergibt der Maintainer beim Triage, sonst wäre der Nummernraum ein Wettlauf
# zwischen Meldern, die voneinander nichts wissen) und die Redaktionsprüfung
# als VORBEDINGUNG, nicht als Empfehlung — was hier durchgeht, liegt im
# Eingangskorb eines öffentlichen Repos.
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
    --kuerzel "${TEAM_FELD_KUERZEL:-}" \
    "$@"

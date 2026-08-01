#!/usr/bin/env bash
# harry.sh — Read-Only Red Team, Schwerpunkt Security/Pentest.
# Dünner Wrapper: setzt Rolle + Auftrag, Rest macht redteam.sh.
set -euo pipefail
cd "$(dirname "$0")"
export ROLLE="harry"
export AUFTRAG="${TEAM_REDTEAM_FOCUS:-Security/Pentest — versuche die App auszuhebeln: Pfad-/Injection-Tricks in lokalen Verweisen, gefährliche Muster im ausgelieferten HTML/JS/CSS (z. B. inline-Handler, externe Ressourcen, Datenlecks in Kommentaren/Platzhaltern), unsichere Links (target=_blank ohne rel=noopener), fehlende Schutz-Header-Hinweise. Statische Site — kein Server, aber Auslieferungs-Sicherheit zählt.}"
# shellcheck source=redteam.sh
source ./team/redteam.sh

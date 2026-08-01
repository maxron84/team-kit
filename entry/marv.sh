#!/usr/bin/env bash
# marv.sh — Read-Only Red Team, Schwerpunkt Chaos/Regression.
# Dünner Wrapper: setzt Rolle + Auftrag, Rest macht redteam.sh.
set -euo pipefail
cd "$(dirname "$0")"
export ROLLE="marv"
export AUFTRAG="${TEAM_REDTEAM_FOCUS:-Chaos/Regression — wirf der App Steine in den Weg: kaputte/leere/riesige Inhalte, tote oder falsch relative Links, fehlende Alt-Texte/Labels, Layout-Brüche bei sehr langem Text, Inkonsistenzen zwischen den Seiten (Header/Footer/Titel), Verstöße gegen prefers-reduced-motion, Encoding-/Sonderzeichen-Fallen. 'DAU klickt dreimal'-Mentalität.}"
# shellcheck source=redteam.sh
source ./team/redteam.sh

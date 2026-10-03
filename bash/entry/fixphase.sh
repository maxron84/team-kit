#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: fixphase.ps1
# fixphase.sh — NUR die Fix-Phase: Frank fixt, Axel knackt die harten Faelle,
# mit Lauf-Deckel, Auslauf-Bremse und Abschlussbericht. Ohne Bau und ohne
# Red-Team-Sweeps (Kit-BL-241, Kit-BL-204).
#
# Fuer Funde ausserhalb einer Kaskade: nach einer Handabnahme, zwischen zwei
# Kaskaden, nach einem Abbruch in der Fix-Phase. `frank.sh` in einer Schleife
# waere eine Fix-Phase OHNE Axel: Nach drei Fehlversuchen setzt Frank den Fund
# auf 'an Axel übergeben', findet ihn danach nicht mehr, und die Schleife
# meldet 'nichts zu tun', waehrend ein Fall auf Axel wartet. Die volle
# Vollautomatik faehrt davor zwei bezahlte Sweeps, die neue Funde erzeugen.
#
# Derselbe Code wie Phase 4 der Vollautomatik — eine zweite Tuer, kein zweites
# Verhalten. Bricht der Lauf ab (Deckel, Bremse, Session-Pause), nimmt
# ./fixphase.sh oder ./vollautomatik.sh ihn bei Phase 4 wieder auf.
#
# Aufruf: ./fixphase.sh        (keine Argumente; --hilfe zeigt diesen Kopf)
# Env:    wie vollautomatik.sh — TEAM_BUDGET_USD, TEAM_MAX_RUNDEN,
#         TEAM_FIX_MAX_STAGNATION.
# Exit:   wie vollautomatik.sh — 0 durch · 1 Fehler/Stagnation/Deckel ·
#         42 Session-Pause · 43 Fix fertig, Quittung fehlt · 44 Gate rot.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=team/lib.sh
source ./team/lib.sh
# BL-223: Dieses Skript kennt keine Argumente.
team_argumente_pruefen "$@"
TEAM_VOLLAUTOMATIK_AB_PHASE=4 exec ./vollautomatik.sh

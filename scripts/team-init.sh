#!/usr/bin/env bash
# team-init.sh — Starter für das T.E.A.M.-Starterkit.
#
# Dünner Launcher: findet das Kit-Repo und reicht alle Argumente durch.
# Der eigentliche Installer lebt versioniert im Kit (<kit>/install.sh).
#
# Aufruf:  bash <kit>/scripts/team-init.sh <zielpfad> [--nicht-interaktiv] [--update|--force]
#
#   --update   Bestehende Installation auf eine neue Kit-Version heben; fasst
#              nur Infrastruktur an. Der richtige Weg für gelebte Projekte.
#   --force    NUR für eine kaputte Erstinstallation — überschreibt auch
#              Ledger, Kaskadenstand und Beutebuch (BL-8).
#
# Der Sinn des Skripts ist die VERKNÜPFUNG: `kit-einrichten.sh --verknuepfen`
# legt es als Symlink unter ~/.claude/scripts/ ab, danach ist der Installer von
# überall aus einem kurzen Befehl erreichbar, ohne dass eine zweite Kopie
# entsteht, die auseinanderläuft. Deshalb löst das Skript den Symlink auf und
# leitet den Kit-Ort aus seinem EIGENEN Ort ab, statt ihn zu raten.
#
# Reihenfolge der Kit-Suche:
#   1. $TEAM_KIT_PFAD              (ausdrücklich gesetzt gewinnt immer)
#   2. Elternordner dieses Skripts (Symlink aufgelöst) — der Normalfall
#   3. ~/Source/team-kit           (historischer Ort, letzter Versuch)
set -euo pipefail

# Symlink-Kette auflösen — ohne `readlink -f`, das auf manchen Systemen
# (BSD/macOS-Bordmittel) nicht dieselbe Bedeutung hat.
QUELLE="${BASH_SOURCE[0]}"
while [ -L "$QUELLE" ]; do
    VERWEIS="$(readlink "$QUELLE")"
    case "$VERWEIS" in
        /*) QUELLE="$VERWEIS" ;;
        *)  QUELLE="$(dirname "$QUELLE")/$VERWEIS" ;;
    esac
done
HIER="$(cd "$(dirname "$QUELLE")" && pwd)"

for kandidat in "${TEAM_KIT_PFAD:-}" "$(cd "$HIER/.." && pwd)" "$HOME/Source/team-kit"; do
    [ -n "$kandidat" ] || continue
    if [ -f "$kandidat/install.sh" ]; then
        exec bash "$kandidat/install.sh" "$@"
    fi
done

printf '\033[31mFEHLER: T.E.A.M.-Starterkit nicht gefunden.\033[0m\n' >&2
echo "  Gesucht in: ${TEAM_KIT_PFAD:+$TEAM_KIT_PFAD, }$(cd "$HIER/.." && pwd), $HOME/Source/team-kit" >&2
echo "  Anderer Ort? TEAM_KIT_PFAD=/pfad/zum/kit bash $0 ..." >&2
exit 2

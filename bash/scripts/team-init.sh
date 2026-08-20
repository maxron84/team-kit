#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: team-init.ps1
# team-init.sh — Starter für das T.E.A.M.-Starterkit.
#
# Dünner Launcher: findet das Kit-Repo und reicht alle Argumente durch.
# Der eigentliche Installer lebt versioniert im Kit (<kit>/bash/install.sh).
#
# Aufruf:  bash <kit>/bash/scripts/team-init.sh <zielpfad> [--nicht-interaktiv] [--update|--force]
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
#
# WARUM DIESES SKRIPT MEHRERE ABLAGEN KENNT
#     Es ist das EINZIGE Stück des Kits, von dem eine Kopie außerhalb des
#     Repos liegen kann (unter ~/.claude/scripts/). Eine solche Kopie wird
#     nicht mitgezogen, wenn sich im Kit etwas verschiebt — und genau das ist
#     passiert: Der Umzug auf bash/ und pwsh/ hat jede ältere Kopie
#     stillgelegt, weil sie <kit>/install.sh suchte. Der Anwender sah einen
#     Launcher, der plötzlich behauptete, das Kit sei nicht da.
#
#     Deshalb rät dieses Skript nicht EINEN Ort, sondern kennt alle, an denen
#     ein Installer je lag, und nimmt den ersten, den es findet. Eine Kopie
#     beliebigen Alters funktioniert damit weiter — sie muss nur wissen, wo
#     das Kit liegt, nicht wie es innen aufgebaut ist. Die Liste wächst nach
#     unten; oben steht immer die aktuelle Ablage.
#
#     Der bessere Weg bleibt der Symlink (`kit-einrichten.sh --verknuepfen`):
#     Der kann gar nicht erst veralten. Diese Liste ist der Fallschirm für
#     die Kopien, die es trotzdem gibt.
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

# Ablagen des Installers, neueste zuerst. `bash/install.sh` seit der
# Bahn-Trennung, `install.sh` davor.
INSTALLER_ORTE="bash/install.sh install.sh"

# Kit-Kandidaten. Zwei Elternebenen, weil dieses Skript vor der Bahn-Trennung
# unter <kit>/scripts/ lag und heute unter <kit>/bash/scripts/ — eine Kopie
# aus der Zeit davor liegt entsprechend anders.
KANDIDATEN="${TEAM_KIT_PFAD:-}
$(cd "$HIER/../.." 2>/dev/null && pwd)
$(cd "$HIER/.." 2>/dev/null && pwd)
$HOME/Source/team-kit"

GESUCHT=""
while IFS= read -r kandidat; do
    [ -n "$kandidat" ] || continue
    for ort in $INSTALLER_ORTE; do
        GESUCHT="$GESUCHT
  $kandidat/$ort"
        if [ -f "$kandidat/$ort" ]; then
            exec bash "$kandidat/$ort" "$@"
        fi
    done
done <<EOF
$KANDIDATEN
EOF

printf '\033[31mFEHLER: T.E.A.M.-Starterkit nicht gefunden.\033[0m\n' >&2
echo "  Gesucht in:$GESUCHT" >&2
echo "  Anderer Ort? TEAM_KIT_PFAD=/pfad/zum/kit bash $0 ..." >&2
exit 2

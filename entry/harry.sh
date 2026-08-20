#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: harry.ps1
# harry.sh — Read-Only Red Team, Schwerpunkt Security/Angriffsflaeche.
# Duenner Wrapper: setzt Rolle + Auftrag, Rest macht redteam.sh.
#
# BL-20: Der ausgelieferte Default beschrieb bis 2.8.1 eine statische Website
# ("Statische Site — kein Server", inline-Handler, target=_blank). In jedem
# anderen Stack zielte er nicht bloss daneben, sondern behauptete etwas
# SACHLICH FALSCHES ueber das Zielprojekt — und ein Modell uebernimmt das als
# Tatsache. Feld-Beleg (pygame-Spiel, K3): Harrys Sweep ueber vier neue
# Baustufen, darunter ein pfadnehmender Datei-Leser, kostete 0,4567 USD und
# meldete NULL Funde; derselbe Code mit passendem Fokus: 1,0247 USD, ein Fund.
# Der leere Sweep war kein Beleg fuer Fehlerfreiheit, sondern fuer einen
# Auftrag, der am Projekt vorbeisah.
#
# Der Default beschreibt deshalb jetzt die METHODE, nicht die Technologie.
# Projekte, die es genauer sagen koennen, setzen TEAM_REDTEAM_AUFTRAG_HARRY in
# team.config.sh — dort, weil `install.sh --update` diese Datei ueberleben
# laesst; eine Anpassung hier wuerde beim naechsten Update ueberschrieben.
set -euo pipefail
cd "$(dirname "$0")"
export ROLLE="harry"
export AUFTRAG="${TEAM_REDTEAM_FOCUS:-${TEAM_REDTEAM_AUFTRAG_HARRY:-Security/Angriffsflaeche — versuche das Programm auszuhebeln. Frage dich: Was gelangt von AUSSEN in diesen Prozess (Eingaben, Dateien, Argumente, Umgebung, Netz, Zwischenablage), und was passiert bei Werten, mit denen niemand gerechnet hat — zu gross, leer, fremdes Encoding, boesartig geformte Pfade? Wo verlaesst sich Code auf eine Zusicherung, die der Aufrufer gar nicht geben muss? Wo werden Rechte, Geheimnisse oder Ressourcen weitergereicht, ohne dass jemand sie prueft? Belege jeden Fund an der Fundstelle im Code.}}"
# shellcheck source=redteam.sh
source ./team/redteam.sh

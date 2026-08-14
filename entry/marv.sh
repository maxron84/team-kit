#!/usr/bin/env bash
# marv.sh — Read-Only Red Team, Schwerpunkt Chaos/Regression.
# Duenner Wrapper: setzt Rolle + Auftrag, Rest macht redteam.sh.
#
# BL-20: siehe harry.sh — der Default nennt keine Technologie mehr, sondern die
# Methode. Projektseitige Uebersteuerung: TEAM_REDTEAM_AUFTRAG_MARV in
# team.config.sh.
#
# BL-21: Der zweite Absatz ist neu und schliesst eine DIMENSION, nicht eine
# Stack-Luecke. Alle Rollenauftraege des Kits waren adversarisch (was kann ein
# Angreifer, was bricht bei Missbrauch); was der GEWOEHNLICHE Pfad kostet,
# fragte keiner. Feld-Beleg: ein Spiel zog 42 % CPU-Last bei 103 gruenen Tests
# — eine @property berechnete einen invarianten Wert ~600x je Frame neu. Harry
# hatte dieselbe Datei kurz zuvor gelesen und drei Zeilen darueber einen Fund
# gelandet; seine Frage zeigte auf Einlese-Robustheit, nicht auf Dauerkosten.
# Die Schwelle im Text ist Absicht: "das ginge schneller" ist unbegrenzt.
set -euo pipefail
cd "$(dirname "$0")"
export ROLLE="marv"
export AUFTRAG="${TEAM_REDTEAM_FOCUS:-${TEAM_REDTEAM_AUFTRAG_MARV:-Chaos/Regression — wirf dem Programm Steine in den Weg: kaputte, leere, riesige oder widerspruechliche Daten; Sonderzeichen und Encoding-Fallen; Zustaende in falscher Reihenfolge; abgebrochene Vorgaenge; alles, was ein ungeduldiger Anwender dreimal hintereinander tut. Pruefe ausserdem, was der GEWOEHNLICHE Pfad kostet: Wird Invariantes bei jedem Aufruf neu berechnet, waechst Arbeit mit einer Groesse, die nicht wachsen muesste? Melde das NUR, wenn der normale Betrieb asymptotisch mehr kostet als noetig — kein Feintuning. Diese Luecke liegt zwischen Korrektheit und Kosten und ist bei gruener Suite unsichtbar.}}"
# shellcheck source=redteam.sh
source ./team/redteam.sh

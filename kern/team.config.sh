#!/usr/bin/env bash
# team.config.sh — alle projektspezifischen Werte des T.E.A.M. an EINER Stelle.
#
# Wird von team-lib.sh gesourct, also von jedem Rollen-Skript. Änderungen hier
# wirken sofort in allen Rollen — kein erneutes Installieren nötig.
#
# Diese Datei gehört INS GIT des Zielprojekts (sie enthält keine Geheimnisse).
# Geheimnisse (API-Key) liegen unter ~/.config/claude-team/, siehe team-lib.sh.

# --- Projekt ------------------------------------------------------------------
# Name des Projekts/Repos — erscheint in Berichten und Ledger-Notizen.
TEAM_PROJEKT="${TEAM_PROJEKT:-{{PROJEKTNAME}}}"

# --- Pfade --------------------------------------------------------------------
# Produktivcode: das, was Harry, Marv und Axel NIEMALS anfassen dürfen.
# Ohne Schrägstrich am Ende schreiben; die Skripte hängen ** selbst an.
TEAM_PRODUKTIVCODE="${TEAM_PRODUKTIVCODE:-{{PRODUKTIVCODE}}}"

# Test-Ordner: hier dürfen Red Team und Frank Reproducer ablegen.
TEAM_TEST_ORDNER="${TEAM_TEST_ORDNER:-{{TEST_ORDNER}}}"

# Plan-Ordner: Kaskaden-Pläne, Beutebuch, Ermittlungsakten, Roadmap, Backlog.
TEAM_PLAN_ORDNER="${TEAM_PLAN_ORDNER:-{{PLAN_ORDNER}}}"

# Schreibweise vereinheitlichen: Ordner enden IMMER auf genau einen Schrägstrich,
# egal wie sie oben eingetragen wurden. Alles Weitere darf sich darauf verlassen.
TEAM_PRODUKTIVCODE="${TEAM_PRODUKTIVCODE%/}/"
TEAM_TEST_ORDNER="${TEAM_TEST_ORDNER%/}/"
TEAM_PLAN_ORDNER="${TEAM_PLAN_ORDNER%/}/"

# Abgeleitete Pfade — nur ändern, wenn die Struktur wirklich abweicht.
TEAM_BEUTEBUCH="${TEAM_BEUTEBUCH:-${TEAM_PLAN_ORDNER}beutebuch.md}"
TEAM_ERMITTLUNGSAKTEN="${TEAM_ERMITTLUNGSAKTEN:-${TEAM_PLAN_ORDNER}ermittlungsakten}"
TEAM_ROADMAP="${TEAM_ROADMAP:-${TEAM_PLAN_ORDNER}roadmap-skizzen.md}"
TEAM_BACKLOG="${TEAM_BACKLOG:-${TEAM_PLAN_ORDNER}backlog.md}"
TEAM_CHANGELOG="${TEAM_CHANGELOG:-CHANGELOG.md}"

# --- Verifikation -------------------------------------------------------------
# DER kritische Wert: der eine Befehl, mit dem eine Rolle feststellt, dass das
# Projekt heil ist. Ralph kann ohne ihn keine Stufe abschließen, Frank keinen
# Fix verifizieren.
#
# Ist er leer, lassen die Rollen den Smoke-Test-Schritt aus und melden das im
# Prompt als offenen Punkt — das Team läuft, aber ohne Sicherheitsnetz.
# Das ist ein Zustand für Tag 1, kein Dauerzustand.
TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-{{SMOKE_TEST}}}"

# --- Commit-Konventionen ------------------------------------------------------
TEAM_FIX_PRAEFIX="${TEAM_FIX_PRAEFIX:-fix(uat)}"
TEAM_FEAT_PRAEFIX="${TEAM_FEAT_PRAEFIX:-feat}"

# --- Werkzeuge ----------------------------------------------------------------
# Aufruf der Beutebuch-Zustandsmaschine (Pfad relativ zur Repo-Wurzel).
TEAM_BEUTEBUCH_TOOL="${TEAM_BEUTEBUCH_TOOL:-python3 scripts/beutebuch.py}"
TEAM_KOSTEN_TOOL="${TEAM_KOSTEN_TOOL:-python3 scripts/kosten.py}"

# --- Budget (Defaults aus dem Feld, HM-32/BL-30) ------------------------------
# Soft-Cap gilt für alle Rollen (nur Hinweis bei Frank/Axel), Hard-Cap bricht ab.
# Zu tiefe Pro-Fall-Caps VERVIELFACHEN die Kosten, statt zu sparen — sie werfen
# teure, aber plausible Fixes per Rollback weg. Lieber großzügig ansetzen.
TEAM_ROLE_BUDGET_USD="${TEAM_ROLE_BUDGET_USD:-5}"
TEAM_ROLE_HARDCAP_USD="${TEAM_ROLE_HARDCAP_USD:-10}"

# --- Ledger -------------------------------------------------------------------
# Committete Kostenbasis. NICHT in .gitignore aufnehmen.
TEAM_LEDGER="${TEAM_LEDGER:-.budget-ledger}"

# --- Abgeleitet: Read-Only-Whitelist für Guard Linie 3 ------------------------
# Regex der Pfade, die Harry/Marv schreiben dürfen. Axel bekommt nur den
# Plan-Ordner (enger, siehe axel.sh).
TEAM_WHITELIST_REDTEAM="${TEAM_WHITELIST_REDTEAM:-^(${TEAM_TEST_ORDNER%/}/|${TEAM_PLAN_ORDNER%/}/)}"
TEAM_WHITELIST_AXEL="${TEAM_WHITELIST_AXEL:-^${TEAM_PLAN_ORDNER%/}/}"

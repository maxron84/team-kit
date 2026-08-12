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

# --- Prüfumfang außerhalb des Produktivcode-Ordners (BL-52) -------------------
# Leerliste von Dateien UND Ordnern, die zum Prüfumfang des Red Teams gehören,
# aber nicht unter TEAM_PRODUKTIVCODE liegen: Einstiegspunkt in der Repo-Wurzel,
# Build- und Deploy-Skripte. Beispiel: "main.py bin/ deploy/".
#
# In einem frisch angelegten Projekt bleibt der Wert LEER — dort liegt alles
# unter TEAM_PRODUKTIVCODE, und die Annahme trägt. In einer gewachsenen
# Codebasis ist er der Unterschied zwischen „src/ ist sauber" und „das Projekt
# ist geprüft": Der Code, der als erstes läuft, liegt dort regelmäßig daneben
# und wurde bis 2.6.0 nie angegriffen, ohne dass es jemandem auffiel.
#
# WICHTIG — das erweitert den PRÜFUMFANG, nicht die Schreibrechte: Diese Pfade
# sind für Harry, Marv und Axel genauso tabu wie TEAM_PRODUKTIVCODE. Die
# Guard-Whitelist unten bleibt unverändert (nur Test- und Plan-Ordner).
# KEIN abschließender Schrägstrich nötig; die Liste wird nicht normalisiert,
# weil sie auch einzelne Dateien enthalten darf.
TEAM_WEITERER_CODE="${TEAM_WEITERER_CODE:-{{WEITERER_CODE}}}"

# --- Bestand in der Schreibzone der Read-Only-Rollen (BL-51) ------------------
# Test- und Plan-Ordner sind die EINZIGEN Pfade, die Harry, Marv und Axel
# schreiben dürfen (siehe Whitelist unten) — dort schlägt der Guard also nicht
# an. Zog das Team in eine gewachsene Codebasis ein, lagen in diesen Ordnern
# schon fremde Dateien: eine gewachsene Testsuite, fachliche Dokumente.
#
# Was hier steht, nennen die Rollen-Prompts ausdrücklich als fremdes Eigentum:
# neue Dateien anlegen ja, Bestehendes ändern oder löschen nein. Das ist eine
# PROMPT-Auflage, keine Mechanik — der Guard kann es nicht erzwingen, weil die
# Pfade auf seiner Whitelist stehen. Wer die Mechanik will, gibt dem Team einen
# eigenen, leeren Plan-Ordner (z. B. team-plans/).
#
# Leerliste, vom Installer beim Einzug gefüllt (bis zu zwölf Einträge, dann
# gekürzt — der Prompt ergänzt ohnehin „und alles, was du dort nicht selbst
# angelegt hast"). Leer = der Ordner war leer, der Normalfall im neuen Projekt.
# Von Hand nachtragen ist ausdrücklich erlaubt. Dateinamen mit Leerzeichen
# werden nicht unterstützt.
TEAM_TEST_ORDNER_BESTAND="${TEAM_TEST_ORDNER_BESTAND:-{{TEST_BESTAND}}}"
TEAM_PLAN_ORDNER_BESTAND="${TEAM_PLAN_ORDNER_BESTAND:-{{PLAN_BESTAND}}}"

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

# --- Werkzeuge der Team-Infrastruktur ------------------------------------------
# Die Team-Werkzeuge liegen unter team/tools/ und sind in Python geschrieben.
# python3 ist damit eine Abhängigkeit der TEAM-INFRASTRUKTUR — auf einer Ebene
# mit git, flock und der Agenten-CLI. Das PROJEKT bleibt davon unberührt: ein
# Rust-Projekt bleibt ein reines Rust-Projekt, in dem ein Werkzeugordner liegt.
TEAM_BEUTEBUCH_TOOL="${TEAM_BEUTEBUCH_TOOL:-python3 team/tools/beutebuch.py}"
TEAM_KOSTEN_TOOL="${TEAM_KOSTEN_TOOL:-python3 team/tools/kosten.py}"

# --- Budget (Defaults aus dem Feld, HM-32/BL-30) ------------------------------
# Soft-Cap gilt für alle Rollen (nur Hinweis bei Frank/Axel), Hard-Cap bricht ab.
# Zu tiefe Pro-Fall-Caps VERVIELFACHEN die Kosten, statt zu sparen — sie werfen
# teure, aber plausible Fixes per Rollback weg. Lieber großzügig ansetzen.
TEAM_ROLE_BUDGET_USD="${TEAM_ROLE_BUDGET_USD:-5}"
TEAM_ROLE_HARDCAP_USD="${TEAM_ROLE_HARDCAP_USD:-10}"

# --- Domänen ------------------------------------------------------------------
# Die Domäne trennt im Kostenledger die Produktarbeit von der Arbeit an der
# Team-Infrastruktur selbst. Welche Namen gelten, bestimmt DIESES Projekt —
# die Werkzeuge schreiben keine vor. Erster Wert = Produktarbeit (wird im
# Statusbericht als solche ausgewiesen), zweiter = Team-Infrastruktur.
#
# Beispiele: "app team" · "backend frontend team" · "shop team"
TEAM_DOMAENEN="${TEAM_DOMAENEN:-{{DOMAENEN}}}"
export TEAM_DOMAENEN   # die Python-Werkzeuge lesen sie aus der Umgebung

# --- Ledger -------------------------------------------------------------------
# Committete Kostenbasis. NICHT in .gitignore aufnehmen.
TEAM_LEDGER="${TEAM_LEDGER:-.budget-ledger}"

# --- Abgeleitet: Read-Only-Whitelist für Guard Linie 3 ------------------------
# Regex der Pfade, die Harry/Marv schreiben dürfen. Axel bekommt nur den
# Plan-Ordner (enger, siehe axel.sh).
TEAM_WHITELIST_REDTEAM="${TEAM_WHITELIST_REDTEAM:-^(${TEAM_TEST_ORDNER%/}/|${TEAM_PLAN_ORDNER%/}/)}"
TEAM_WHITELIST_AXEL="${TEAM_WHITELIST_AXEL:-^${TEAM_PLAN_ORDNER%/}/}"

#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: team.config.ps1
# team.config.sh — alle projektspezifischen Werte des T.E.A.M. an EINER Stelle.
#
# Wird von team/lib.sh gesourct, also von jedem Rollen-Skript. Änderungen hier
# wirken sofort in allen Rollen — kein erneutes Installieren nötig.
#
# Diese Datei gehört INS GIT des Zielprojekts (sie enthält keine Geheimnisse).
# Geheimnisse (API-Key) liegen unter ~/.config/claude-team/, siehe team/lib.sh.

# --- Projekt ------------------------------------------------------------------
# Name des Projekts/Repos — erscheint in Berichten und Ledger-Notizen.
TEAM_PROJEKT="${TEAM_PROJEKT:-{{PROJEKTNAME}}}"

# Feldkuerzel: Unter welchem Namen dieses Projekt im Kit gefuehrt wird
# (`Feld A`, `Feld B`, …). LEER lassen, wenn noch keins vergeben ist — der
# Maintainer vergibt es beim Triage der ersten Meldung.
#
# BL-168: Das Kuerzel lebte bis 2026-08-26 AUSSCHLIESSLICH in der
# Profiltabelle des Kit-READMEs, also ausserhalb der Installation, die es
# nennen muesste. Wer eine Meldung schrieb, wusste deshalb nicht, wie sein
# Projekt drueben heisst — und schrieb entweder den NAMEN hinein (den die
# Redaktionspruefung dann zu Recht anschlaegt) oder gar nichts. Genau dieser
# Anonymisierung wegen fuehrt das Kit seine Feldbelege ueberhaupt unter
# Kuerzeln.
TEAM_FELD_KUERZEL="${TEAM_FELD_KUERZEL:-}"

# --- Pfade --------------------------------------------------------------------
# Produktivcode: das, was Harry, Marv und Axel NIEMALS anfassen dürfen.
# Der abschließende Schrägstrich ist egal — er wird unten vereinheitlicht.
TEAM_PRODUKTIVCODE="${TEAM_PRODUKTIVCODE:-{{PRODUKTIVCODE}}}"

# Test-Ordner: hier dürfen Red Team und Frank Reproducer ablegen.
#
# DIE KOPPLUNG, DIE HIER STEHEN MUSS (`Kit-BL-169`): Der Testordner muss dort
# liegen, wo DEIN Testläufer sucht, und der Dateiname so heißen, dass er ihn
# nimmt. Beides ist stackabhängig, und beides fällt sonst LAUTLOS aus:
#   * pytest findet die Dateien am PFAD — `src/` + `tests/` trägt.
#   * Dart/Flutter sammelt ausschließlich INNERHALB des Pakets und
#     ausschließlich unterhalb von `test/`. Liegt das Paket unter `src/`,
#     liegt `tests/` außerhalb davon und wird nie gelesen. Dieselbe Bauart
#     bei Cargo (`tests/` relativ zu `Cargo.toml`), Go (Paketverzeichnis)
#     und Gradle (`src/test/`).
#   * Der Läufer nimmt oft nur ein NAMENSMUSTER: `_test.dart`, `_test.go`.
#     Die Kit-Konvention `test_hm<nr>_<stichwort>.py` buchstabengetreu auf
#     Dart übertragen ergibt `test_hm36_foo.dart` — einen Namen, den der
#     Läufer ignoriert. Pass das Muster im Beutebuch-Format mit an.
# Die Folge ist in beiden Hälften dieselbe und schlimmer als ein Fehler:
# Franks regelkonform abgelegter Reproducer wird NIE ausgeführt, der
# Smoke-Test bleibt grün, das Beutebuch zeigt einen Fund mit Reproducer —
# geprüft wird nichts.
TEAM_TEST_ORDNER="${TEAM_TEST_ORDNER:-{{TEST_ORDNER}}}"

# Plan-Ordner: Kaskaden-Pläne, Beutebuch, Ermittlungsakten, Roadmap, Backlog.
TEAM_PLAN_ORDNER="${TEAM_PLAN_ORDNER:-{{PLAN_ORDNER}}}"

# Schreibweise vereinheitlichen: Ordner enden IMMER auf genau einen Schrägstrich,
# egal wie sie oben eingetragen wurden. Alles Weitere darf sich darauf verlassen.
TEAM_PRODUKTIVCODE="${TEAM_PRODUKTIVCODE%/}/"
TEAM_TEST_ORDNER="${TEAM_TEST_ORDNER%/}/"
TEAM_PLAN_ORDNER="${TEAM_PLAN_ORDNER%/}/"
# BL-209: Die Python-Werkzeuge suchen die Plandatei einer Kaskade darin
# (`kaskade_beginn`, Grundlage des Zeitraum-Abgleichs aus BL-45 und der
# P1b-Pruefung aus BL-27). Ohne diesen Export nahmen sie "plans" an — in einem
# Projekt mit anderem Ordner fanden sie nie etwas und schwiegen dazu.
export TEAM_PLAN_ORDNER

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

# --- Rueckkanal zum Kit (BL-153) ----------------------------------------------
# Wo liegt das T.E.A.M.-Kit auf DIESER Maschine? Gefuellt vom Installer mit dem
# Pfad, aus dem installiert wurde.
#
# Wozu: Faellt an der Team-Infrastruktur selbst etwas auf — in team/, in einem
# Entrypoint oder in einer Regel aus CLAUDE.md/TEAM.md —, gehoert der Fund ins
# KIT zurueck, nicht nur in den Backlog dieses Projekts. Sonst trifft derselbe
# Fehler jede weitere Installation, und dieses Projekt repariert ihn bei jedem
# Update aufs Neue. Das Werkzeug dafuer ist team/tools/kit_meldung.py.
#
# BL-153: Bis einschliesslich 2.12.0 stand der Pfad als ~/Source/team-kit in der Prosa der
# Backlog-Vorlage und im Briefing des Architekten — also fest verdrahtet auf
# die Ablage EINER Maschine. Wer woandershin geklont hatte, bekam eine
# Anweisung, die ins Leere zeigt; ein fremder Nutzer ohnehin. Der Wert steht
# deshalb hier, wo ihn ein Mensch korrigieren kann, und das Werkzeug sucht
# zusaetzlich die ueblichen Orte ab, falls er nicht stimmt.
#
# Leer ist erlaubt: Dann sucht das Werkzeug allein, und wenn es nichts findet,
# legt es die Meldung als Datei im Projekt ab, statt sie zu verlieren.
TEAM_KIT_PFAD="${TEAM_KIT_PFAD:-{{KIT_PFAD}}}"

# --- Verifikation -------------------------------------------------------------
# DER kritische Wert: der eine Befehl, mit dem eine Rolle feststellt, dass das
# Projekt heil ist. Ralph kann ohne ihn keine Stufe abschließen, Frank keinen
# Fix verifizieren.
#
# Ist er leer, lassen die Rollen den Smoke-Test-Schritt aus und melden das im
# Prompt als offenen Punkt — das Team läuft, aber ohne Sicherheitsnetz.
# Das ist ein Zustand für Tag 1, kein Dauerzustand.
#
# BL-149: Hier stand als Vorbelegung der Satz "TODO: noch keiner — Stufe 1 der
# ersten Kaskade". Er war gut gemeint und hat jede erste Kaskade beschädigt:
# Ein nicht-leerer Wert ist für die Weichen oben ein KONFIGURIERTER Befehl, und
# der Satz landete wörtlich im Prompt der Rollen, in der Werkzeug-Allowlist des
# Red Teams und in der Selbstprüfung, die ihn AUSFÜHRTE (Exit 127, "ist ROT").
# Der Hinweis steht deshalb hier im Kommentar, wo er niemanden ausführt:
# Trägt Stufe 1 der ersten Kaskade den echten Prüfbefehl ein, kommt er unten
# in die Zeile.
TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-{{SMOKE_TEST_KONFIG}}}"

# BL-207: Wie lange dieser Befehl im VORDERGRUND laufen darf. Die Zahl steht
# im Prompt jeder bauenden Rolle — sie ist der Grund, warum die Rolle das
# Zeitlimit ihres Werkzeugs hochsetzt, statt in den Hintergrund auszuweichen.
# Jede Suite waechst; ab dem Tag, an dem sie die Vordergrundgrenze des
# Werkzeugs (120 s) reisst, laeuft jede bauende Rolle sonst regelmaessig in
# den vierten Ausgang (BL-41). Leer lassen heisst: der Bibliotheks-Default.
TEAM_SMOKE_TEST_TIMEOUT="${TEAM_SMOKE_TEST_TIMEOUT:-600}"

# --- Commit-Konventionen ------------------------------------------------------
TEAM_FIX_PRAEFIX="${TEAM_FIX_PRAEFIX:-fix(uat)}"
TEAM_FEAT_PRAEFIX="${TEAM_FEAT_PRAEFIX:-feat}"

# --- Werkzeuge der Team-Infrastruktur ------------------------------------------
# Die Team-Werkzeuge liegen unter team/tools/ und sind in Python geschrieben.
# Python ist damit eine Abhängigkeit der TEAM-INFRASTRUKTUR — auf einer Ebene
# mit git, flock und der Agenten-CLI. Das PROJEKT bleibt davon unberührt: ein
# Rust-Projekt bleibt ein reines Rust-Projekt, in dem ein Werkzeugordner liegt.
#
# BL-131: Wie der Interpreter HEISST, entscheidet die Maschine, nicht diese
# Datei. Unter Windows legen weder python.org noch winget ein python3.exe an;
# was dort unter dem Namen antwortet, ist der App-Execution-Alias aus dem
# Microsoft Store — er startet den Store und meldet "Python was not found".
# Der Installer trägt hier ein, was er auf DIESER Maschine gefunden hat.
TEAM_PYTHON="${TEAM_PYTHON:-{{PYTHON}}}"

# Die Agenten-CLI. Wie sie HEISST und wo sie liegt, entscheidet die Maschine —
# dieselbe Erwaegung wie bei TEAM_PYTHON (BL-131), und sie wiegt hier schwerer.
#
# BL-173: Claude Code wird legitim IDE-GEBUENDELT ausgeliefert (VS Code /
# VSCodium-Erweiterung, Binaerdatei unter resources/native-binary/claude). Eine
# Maschine kann eine vollstaendig eingerichtete, ANGEMELDETE Installation
# haben, ohne dass `claude` in irgendeinem PATH aufloesbar ist — genau diese
# Lage lag im Feld vor: .credentials.json vorhanden, Abo aktiv, Erweiterung
# lief, und die Aufloesung ueber den PATH leer.
#
# Der Installer traegt hier ein, was er auf DIESER Maschine gefunden hat:
# den blossen Namen, wenn die CLI im PATH steht, sonst den vollen Pfad zur
# IDE-gebuendelten Binaerdatei. Ein Wert MIT Pfadtrenner wird direkt genommen,
# ohne PATH-Suche.
TEAM_CLAUDE_BIN="${TEAM_CLAUDE_BIN:-{{CLAUDE_BIN}}}"
TEAM_BEUTEBUCH_TOOL="${TEAM_BEUTEBUCH_TOOL:-$TEAM_PYTHON team/tools/beutebuch.py}"
TEAM_KOSTEN_TOOL="${TEAM_KOSTEN_TOOL:-$TEAM_PYTHON team/tools/kosten.py}"

# --- Angriffsfläche des Red Teams (BL-20) -------------------------------------
# Der ausgelieferte Grundauftrag von Harry und Marv beschreibt die METHODE, nicht
# deinen Stack — er behauptet bewusst nichts über dein Projekt. Wer die
# Angriffsfläche in einem Satz benennen kann, holt hier deutlich mehr heraus:
# Im Feld fand derselbe Sweep über denselben Code mit passendem Auftrag einen
# Fund, den er ohne ihn nicht sah.
#
# Beispiele: "Level-Dateien und Speicherstände kommen von der Platte und sind
# nicht vertrauenswürdig" · "Alle Eingänge sind HTTP-Handler unter api/" ·
# "Der Prozess liest Sensordaten über die serielle Schnittstelle".
#
# Diese Werte stehen hier und nicht in harry.sh/marv.sh, weil `install.sh
# --update` diese Datei bewusst überleben lässt — eine Anpassung im Skript wäre
# beim nächsten Update weg. Leer lassen ist in Ordnung; dann gilt der
# stack-neutrale Default.
#
# NICHT zu verwechseln mit TEAM_REDTEAM_FOCUS: Der ist der Fokus EINER Kaskade
# (Umgebungsvariable, gilt für einen Lauf). Diese beiden sind der stehende
# Grundauftrag des Projekts.
TEAM_REDTEAM_AUFTRAG_HARRY="${TEAM_REDTEAM_AUFTRAG_HARRY:-}"
TEAM_REDTEAM_AUFTRAG_MARV="${TEAM_REDTEAM_AUFTRAG_MARV:-}"

# --- Modellstufen -------------------------------------------------------------
# Die Rollen-Skripte kennen KEINE Modellnamen, sondern zwei Stufen. Beide haben
# ihren Default in team/lib.sh und sind hier bewusst NICHT gesetzt — wer sie
# einträgt, überschreibt die Kit-Defaults dauerhaft für dieses Projekt:
#
#   TEAM_MODEL_LOOP="${TEAM_MODEL_LOOP:-sonnet}"    Ralph, Harry, Marv, Frank
#   TEAM_MODEL_STRONG="${TEAM_MODEL_STRONG:-opus}"  Axel (und die Architekten-
#                                                   Sitzung, die du selbst führst)
#
# Für einen einzelnen Lauf reicht die Umgebung:
#   TEAM_MODEL_LOOP=opus ./vollautomatik.sh
#
# Die Stufen sind Absicht, nicht Zufall: Die schwache trägt die Masse der
# Aufrufe und damit der Kosten. Sie ist zugleich die Stelle, an der ein anderes
# Modell — künftig auch ein lokales — zuerst eingewechselt wird. Vorausgesetzt
# wird kein bestimmtes Modell, sondern Fähigkeit: große Regeldatei tragen,
# Werkzeuge zuverlässig aufrufen, das Promise-Protokoll bis zum Ende
# durchhalten, ohne Rückfragen arbeiten. Näheres im README des Kits, Abschnitt
# „Modelle".

# --- Budget (Defaults aus dem Feld, HM-32/BL-30) ------------------------------
# Soft-Cap gilt für alle Rollen (nur Hinweis bei Frank/Axel), Hard-Cap bricht ab.
# Zu tiefe Pro-Fall-Caps VERVIELFACHEN die Kosten, statt zu sparen — sie werfen
# teure, aber plausible Fixes per Rollback weg. Lieber großzügig ansetzen.
TEAM_ROLE_BUDGET_USD="${TEAM_ROLE_BUDGET_USD:-5}"
TEAM_ROLE_HARDCAP_USD="${TEAM_ROLE_HARDCAP_USD:-10}"

# --- Domänen ------------------------------------------------------------------
# Kostenkonten: Unter welchen Namen die Ausgaben im Ledger gebucht werden.
# Welche Namen gelten, bestimmt DIESES Projekt — die Werkzeuge schreiben keine
# vor. Der erste Wert gilt als Produktarbeit und wird im Statusbericht als
# solche ausgewiesen.
#
# EIN Name ist der Normalfall (BL-9). Jeder Kostenabschluss bucht auf GENAU
# EINE Domäne; mehrere Namen heißen also: nach jedem Lauf entscheiden, wohin er
# gehört — auch wenn er mehrere Bereiche berührt hat. Nur eintragen, wenn die
# Ausgaben wirklich getrennt gelesen werden sollen, z. B. "backend frontend".
#
# KEINE eigene Domäne für die Arbeit am T.E.A.M. selbst: Am Team wird hier
# nicht entwickelt — was auffällt, geht ins Kit-Repo zurück und wird dort
# verbucht. Eine "team"-Zeile bliebe hier strukturell 0.0000, und eine
# Kennzahl, die immer null zeigt, erzieht dazu, den Block zu überlesen.
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

# Bahn: pwsh | Gegenstueck: team.config.sh
# team.config.ps1 — alle projektspezifischen Werte des T.E.A.M. an EINER Stelle.
#
# PowerShell-Fassung von team.config.sh. BEIDE werden vom Installer aus
# DENSELBEN neun Antworten erzeugt — sie sind zwei Generate einer Quelle, keine
# zwei gepflegten Dateien. Deshalb koennen sie nicht auseinanderlaufen, und
# deshalb steht hier auch derselbe Text: Wer eine Begruendung sucht, soll sie
# in der Datei finden, die er gerade offen hat.
#
# Wird von team/lib.psm1 per Dot-Sourcing geladen, also von jedem Rollen-Skript.
# Aenderungen hier wirken sofort in allen Rollen — kein erneutes Installieren.
#
# Diese Datei gehoert INS GIT des Zielprojekts (sie enthaelt keine Geheimnisse).
# Geheimnisse (API-Key) liegen unter %APPDATA%\claude-team\, siehe team/lib.psm1.

# Team-Wert: der Ersatz fuer Bashs ${VAR:-vorgabe}. Die Umgebung gewinnt, sonst
# gilt der eingetragene Wert. NICHT zu verwechseln mit `Team-Default` in
# team/lib.psm1: Das ist der BIBLIOTHEKS-Default, den ein Projekt hier
# ueberschreibt. Die Funktion steht bewusst in dieser Datei und nicht in der
# Bibliothek — die Config wird VOR der Bibliothek geladen, und eine
# Reihenfolgeabhaengigkeit an dieser Stelle waere eine Falle, die nur beim
# ersten echten Lauf auffiele.
function Team-Wert {
    param([string]$Name, [string]$Vorgabe)
    $ausEnv = [Environment]::GetEnvironmentVariable($Name)
    if ($ausEnv) { return $ausEnv }
    return $Vorgabe
}

# Ordnerangaben enden IMMER auf genau einen Schraegstrich.
function Team-Ordner { param([string]$Wert) return ($Wert.TrimEnd('/', '\') + '/') }

# --- Projekt ------------------------------------------------------------------
# Name des Projekts/Repos — erscheint in Berichten und Ledger-Notizen.
$TEAM_PROJEKT = Team-Wert 'TEAM_PROJEKT' '{{PROJEKTNAME}}'

# --- Pfade --------------------------------------------------------------------
# Produktivcode: das, was Harry, Marv und Axel NIEMALS anfassen duerfen.
# Der abschliessende Schraegstrich ist egal — er wird unten vereinheitlicht.
$TEAM_PRODUKTIVCODE = Team-Wert 'TEAM_PRODUKTIVCODE' '{{PRODUKTIVCODE}}'

# Test-Ordner: hier duerfen Red Team und Frank Reproducer ablegen.
$TEAM_TEST_ORDNER = Team-Wert 'TEAM_TEST_ORDNER' '{{TEST_ORDNER}}'

# Plan-Ordner: Kaskaden-Plaene, Beutebuch, Ermittlungsakten, Roadmap, Backlog.
$TEAM_PLAN_ORDNER = Team-Wert 'TEAM_PLAN_ORDNER' '{{PLAN_ORDNER}}'

# Schreibweise vereinheitlichen. Alles Weitere darf sich darauf verlassen.
# Beachte: hier wird AUCH der Backslash abgeschnitten. Unter Windows tippt
# jeder `src\`, und die Guard-Whitelist ist ein Regex ueber git-Pfade — die
# nennen Schraegstriche, immer, auch unter Windows.
$TEAM_PRODUKTIVCODE = Team-Ordner $TEAM_PRODUKTIVCODE
$TEAM_TEST_ORDNER   = Team-Ordner $TEAM_TEST_ORDNER
$TEAM_PLAN_ORDNER   = Team-Ordner $TEAM_PLAN_ORDNER

# --- Pruefumfang ausserhalb des Produktivcode-Ordners (BL-52) -----------------
# Leerliste von Dateien UND Ordnern, die zum Pruefumfang des Red Teams gehoeren,
# aber nicht unter TEAM_PRODUKTIVCODE liegen: Einstiegspunkt in der Repo-Wurzel,
# Build- und Deploy-Skripte. Beispiel: "main.py bin/ deploy/".
#
# WICHTIG — das erweitert den PRUEFUMFANG, nicht die Schreibrechte: Diese Pfade
# sind fuer Harry, Marv und Axel genauso tabu wie TEAM_PRODUKTIVCODE.
$TEAM_WEITERER_CODE = Team-Wert 'TEAM_WEITERER_CODE' '{{WEITERER_CODE}}'

# --- Bestand in der Schreibzone der Read-Only-Rollen (BL-51) ------------------
# Was hier steht, nennen die Rollen-Prompts ausdruecklich als fremdes Eigentum:
# neue Dateien anlegen ja, Bestehendes aendern oder loeschen nein. Das ist eine
# PROMPT-Auflage, keine Mechanik — der Guard kann es nicht erzwingen, weil die
# Pfade auf seiner Whitelist stehen. Wer die Mechanik will, gibt dem Team einen
# eigenen, leeren Plan-Ordner (z. B. team-plans/).
$TEAM_TEST_ORDNER_BESTAND = Team-Wert 'TEAM_TEST_ORDNER_BESTAND' '{{TEST_BESTAND}}'
$TEAM_PLAN_ORDNER_BESTAND = Team-Wert 'TEAM_PLAN_ORDNER_BESTAND' '{{PLAN_BESTAND}}'

# Abgeleitete Pfade — nur aendern, wenn die Struktur wirklich abweicht.
$TEAM_BEUTEBUCH       = Team-Wert 'TEAM_BEUTEBUCH'       "${TEAM_PLAN_ORDNER}beutebuch.md"
$TEAM_ERMITTLUNGSAKTEN = Team-Wert 'TEAM_ERMITTLUNGSAKTEN' "${TEAM_PLAN_ORDNER}ermittlungsakten"
$TEAM_ROADMAP         = Team-Wert 'TEAM_ROADMAP'         "${TEAM_PLAN_ORDNER}roadmap-skizzen.md"
$TEAM_BACKLOG         = Team-Wert 'TEAM_BACKLOG'         "${TEAM_PLAN_ORDNER}backlog.md"
$TEAM_CHANGELOG       = Team-Wert 'TEAM_CHANGELOG'       'CHANGELOG.md'

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
# BL-153: Bis einschliesslich 2.12.0 stand der Pfad als ~/Source/team-kit fest verdrahtet in
# der Prosa — also auf die Ablage EINER Maschine. Wer woandershin geklont
# hatte, bekam eine Anweisung, die ins Leere zeigt; ein fremder Nutzer ohnehin.
#
# ACHTUNG, wenn install.sh diese Datei geschrieben hat: Der bash-Installer
# schreibt team.config.ps1 fuer eine Maschine, auf der er selbst nie war — der
# Pfad hier ist dann der der Linux-Seite. Das Werkzeug faellt in dem Fall auf
# seine eigene Suche zurueck; von Hand nachtragen ist der bessere Weg.
#
# Leer ist erlaubt: Dann sucht das Werkzeug allein, und wenn es nichts findet,
# legt es die Meldung als Datei im Projekt ab, statt sie zu verlieren.
$TEAM_KIT_PFAD = Team-Wert 'TEAM_KIT_PFAD' '{{KIT_PFAD}}'

# --- Verifikation -------------------------------------------------------------
# DER kritische Wert: der eine Befehl, mit dem eine Rolle feststellt, dass das
# Projekt heil ist. Ralph kann ohne ihn keine Stufe abschliessen, Frank keinen
# Fix verifizieren.
#
# Ist er leer, lassen die Rollen den Smoke-Test-Schritt aus und melden das im
# Prompt als offenen Punkt — das Team laeuft, aber ohne Sicherheitsnetz.
# Das ist ein Zustand fuer Tag 1, kein Dauerzustand.
#
# BL-149: Hier stand als Vorbelegung der Satz "TODO: noch keiner — Stufe 1 der
# ersten Kaskade". Er war gut gemeint und hat jede erste Kaskade beschaedigt:
# Ein nicht-leerer Wert ist fuer die Weichen oben ein KONFIGURIERTER Befehl, und
# der Satz landete wörtlich im Prompt der Rollen, in der Werkzeug-Allowlist des
# Red Teams und in der Selbstpruefung, die ihn AUSFUEHRTE (Exit 127, "ist ROT").
# Der Hinweis steht deshalb hier im Kommentar, wo er niemanden ausführt:
# Trägt Stufe 1 der ersten Kaskade den echten Pruefbefehl ein, kommt er unten
# in die Zeile.
$TEAM_SMOKE_TEST = Team-Wert 'TEAM_SMOKE_TEST' '{{SMOKE_TEST_KONFIG}}'

# --- Commit-Konventionen ------------------------------------------------------
$TEAM_FIX_PRAEFIX  = Team-Wert 'TEAM_FIX_PRAEFIX'  'fix(uat)'
$TEAM_FEAT_PRAEFIX = Team-Wert 'TEAM_FEAT_PRAEFIX' 'feat'

# --- Werkzeuge der Team-Infrastruktur -----------------------------------------
# Die Team-Werkzeuge liegen unter team/tools/ und sind in Python geschrieben.
# python3 ist damit eine Abhaengigkeit der TEAM-INFRASTRUKTUR — auf einer Ebene
# mit git und der Agenten-CLI. Sie sind der Grund, warum die pwsh-Bahn
# KEIN zweiter Zustandscode ist: Ledger, Beutebuch und Kostenrechnung liegen
# hier wie dort in denselben Dateien.
#
# Unter Windows heisst der Interpreter je nach Installation `python` oder `py`;
# der Installer traegt ein, was er gefunden hat.
$TEAM_BEUTEBUCH_TOOL = Team-Wert 'TEAM_BEUTEBUCH_TOOL' '{{PYTHON}} team/tools/beutebuch.py'
$TEAM_KOSTEN_TOOL    = Team-Wert 'TEAM_KOSTEN_TOOL'    '{{PYTHON}} team/tools/kosten.py'

# --- Angriffsflaeche des Red Teams (BL-20) ------------------------------------
# Der ausgelieferte Grundauftrag von Harry und Marv beschreibt die METHODE, nicht
# deinen Stack. Wer die Angriffsflaeche in einem Satz benennen kann, holt hier
# deutlich mehr heraus: Im Feld fand derselbe Sweep ueber denselben Code mit
# passendem Auftrag einen Fund, den er ohne ihn nicht sah.
#
# NICHT zu verwechseln mit TEAM_REDTEAM_FOCUS: Der ist der Fokus EINER Kaskade
# (Umgebungsvariable, gilt fuer einen Lauf). Diese beiden sind der stehende
# Grundauftrag des Projekts.
$TEAM_REDTEAM_AUFTRAG_HARRY = Team-Wert 'TEAM_REDTEAM_AUFTRAG_HARRY' ''
$TEAM_REDTEAM_AUFTRAG_MARV  = Team-Wert 'TEAM_REDTEAM_AUFTRAG_MARV'  ''

# --- Modellstufen -------------------------------------------------------------
# Die Rollen-Skripte kennen KEINE Modellnamen, sondern zwei Stufen. Beide haben
# ihren Default in team/lib.psm1 und sind hier bewusst NICHT gesetzt:
#
#   $TEAM_MODEL_LOOP   = Team-Wert 'TEAM_MODEL_LOOP'   'sonnet'   Ralph, Harry, Marv, Frank
#   $TEAM_MODEL_STRONG = Team-Wert 'TEAM_MODEL_STRONG' 'opus'     Axel (und die Architekten-Sitzung)
#
# Fuer einen einzelnen Lauf reicht die Umgebung:
#   $env:TEAM_MODEL_LOOP = 'opus'; .\vollautomatik.cmd

# --- Budget (Defaults aus dem Feld, HM-32/BL-30) ------------------------------
# Soft-Cap gilt fuer alle Rollen (nur Hinweis bei Frank/Axel), Hard-Cap bricht ab.
# Zu tiefe Pro-Fall-Caps VERVIELFACHEN die Kosten, statt zu sparen — sie werfen
# teure, aber plausible Fixes per Rollback weg. Lieber grosszuegig ansetzen.
$TEAM_ROLE_BUDGET_USD  = Team-Wert 'TEAM_ROLE_BUDGET_USD'  '5'
$TEAM_ROLE_HARDCAP_USD = Team-Wert 'TEAM_ROLE_HARDCAP_USD' '10'

# --- Domaenen -----------------------------------------------------------------
# Kostenkonten: Unter welchen Namen die Ausgaben im Ledger gebucht werden.
# EIN Name ist der Normalfall (BL-9). Jeder Kostenabschluss bucht auf GENAU
# EINE Domaene; mehrere Namen heissen also: nach jedem Lauf entscheiden, wohin
# er gehoert — auch wenn er mehrere Bereiche beruehrt hat.
$TEAM_DOMAENEN = Team-Wert 'TEAM_DOMAENEN' '{{DOMAENEN}}'
# Die Python-Werkzeuge lesen sie aus der Umgebung — dieselbe Zusicherung wie
# das `export` in der Bash-Fassung.
$env:TEAM_DOMAENEN = $TEAM_DOMAENEN

# --- Ledger -------------------------------------------------------------------
# Committete Kostenbasis. NICHT in .gitignore aufnehmen.
$TEAM_LEDGER = Team-Wert 'TEAM_LEDGER' '.budget-ledger'

# --- Abgeleitet: Read-Only-Whitelist fuer Guard Linie 3 -----------------------
# Regex der Pfade, die Harry/Marv schreiben duerfen. Axel bekommt nur den
# Plan-Ordner (enger, siehe axel.ps1). Die Muster nennen SCHRAEGSTRICHE, weil
# git seine Pfade so ausgibt — auch unter Windows.
$TEAM_WHITELIST_REDTEAM = Team-Wert 'TEAM_WHITELIST_REDTEAM' `
    ("^(" + $TEAM_TEST_ORDNER.TrimEnd('/') + "/|" + $TEAM_PLAN_ORDNER.TrimEnd('/') + "/)")
$TEAM_WHITELIST_AXEL = Team-Wert 'TEAM_WHITELIST_AXEL' `
    ("^" + $TEAM_PLAN_ORDNER.TrimEnd('/') + "/")

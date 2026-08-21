#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: kit-test.ps1
# kit-test.sh — Selbstverifikation des Kits (BL-6).
#
# Aufruf:  ./kit-test.sh [--behalten] [weitere pytest-Argumente]
#
#   --behalten   Das Wegwerf-Repo nach dem Lauf NICHT löschen (Fehlersuche).
#
# WARUM ES DIESES SKRIPT GIBT
#
# Die Regressionstests unter team/tests/ (Stand 2026-08-21: 569 Fälle in 81 Dateien)
# setzen die INSTALLIERTE Ablage voraus: Entrypoints in der Repo-Wurzel,
# CLAUDE.md und team.config.sh mit gefüllten Platzhaltern. Im Kit-Repo liegen
# sie unter bash/entry/, pwsh/entry/ und bootstrap/ — `pytest geteilt/tests`
# schlägt hier deshalb fehl (Stand 2026-08-21: 21 Fehler, 472 grün, 76 über-
# sprungen — dieselben 21 wie vor dem Bahn-Umzug), ohne dass
# irgendetwas kaputt wäre. Ergebnis: Ein im Kit committeter Fix war bis zur
# nächsten Feldinstallation ungeprüft. Genau so ging BL-1 (tote Fixphase) durch
# drei Releases.
#
# Statt die Tests layout-agnostisch zu machen, prüft dieses Skript dort, wo die
# Tests gelten: in einer echten Installation. Das prüft den Installer gleich mit.
#
# Die Suite läuft dabei ZWEIMAL: einmal im Auslieferungszustand (Schritt 4) und
# einmal mit angepasster team.config.sh (Schritt 5). Der zweite Lauf ist die
# Lehre aus BL-58 — eine frische Installation trägt dieselben Werte wie die
# Bibliothek, dort fällt eine falsch gesetzte Messstelle nie auf.
#
# Schritt 9 prüft die Stufe DAVOR: die Einrichtungsroutine (kit-einrichten.sh,
# scripts/, .gitattributes). Sie liegt vor install.sh — wer sie kaputt
# ausliefert, blockiert den Einstieg, bevor die Schritte 1–8 überhaupt zum
# Tragen kommen. Geprüft wird mit --nur-pruefen; das fasst nichts an.
#
# Das Zielrepo ist ein frisches mktemp-Verzeichnis — ein Wegwerf-Repo im Sinne
# der README-Regel "Guard-Tests nie im echten Projekt". Es wird am Ende
# gelöscht (außer bei --behalten). Dieses Skript ruft KEINE Agenten-CLI auf und
# kostet daher nichts.
set -euo pipefail
# Seit der Bahn-Trennung liegt dieses Skript unter bash/. Gearbeitet wird
# weiterhin von der KIT-WURZEL aus — alle Pruefungen unten nennen ihre
# Pfade bahnweise (bash/, pwsh/, geteilt/), und genau das ist der Punkt:
# Laege eines Tages ein .ps1 unter bash/, fiele es hier sofort auf.
cd "$(dirname "$0")/.."
KIT="$(pwd)"

BEHALTEN=0
PYTEST_ARGS=()
for arg in "$@"; do
    case "$arg" in
        --behalten) BEHALTEN=1 ;;
        *)          PYTEST_ARGS+=("$arg") ;;
    esac
done

rot()  { printf '\033[31m%s\033[0m\n' "$*"; }
gruen(){ printf '\033[32m%s\033[0m\n' "$*"; }
# gelb wurde in Schritt 6 aufgerufen, ohne je definiert zu sein. Der Aufruf
# steht im Fehlerzweig der Abgleich-Pfad-Erkennung — bei `set -e` hätte dort
# statt der Meldung ein "command not found" mit Exit 127 gestanden, also
# ausgerechnet dann, wenn das Skript etwas erklären wollte.
gelb() { printf '\033[33m%s\033[0m\n' "$*"; }
kopf() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# KIT_PYTHON: der Name, unter dem Python auf DIESER Maschine antwortet.
#
# BL-137. BL-131 hat den festen `python3` aus lib.sh, der Konfigurationsvorlage
# und install.sh geholt, BL-133 aus den Entrypoints. Die WERKZEUGE DES KITS
# SELBST — dieses Skript und kit-einrichten.sh — standen auf keiner der beiden
# Listen, und zwar mit derselben Begruendung wie damals: "die faehrt ja nur
# unter Linux".
#
# Sie faehrt hier nicht unter Linux. Unter Git for Windows ist `python3` der
# App-Execution-Alias aus dem Microsoft Store: Er startet, meldet "Python was
# not found" und endet mit 49. Die Wirkung ist dieselbe wie ueberall sonst in
# dieser Reihe — nur an der teuersten Stelle: Die Selbstverifikation des Kits
# war auf einer Windows-Maschine ueberhaupt nicht fahrbar. Wer dort etwas am
# Kit aendert, hat gar keine Moeglichkeit, es zu pruefen; "ungeprueft" ist der
# Zustand, aus dem im Feld die teuren Fehler kommen.
#
# Reihenfolge und Probe sind zeichengleich mit finde_python() in install.sh und
# Finde-Python in install.ps1: Unter Windows `python` VOR `python3`, sonst
# umgekehrt, und geprueft wird START UND VERSION — `command -v` allein findet
# auch den Store-Alias (Lehre BL-122).
kit_python() {
    local kandidaten="python3 python py"
    case "$(uname -s 2>/dev/null)" in
        MINGW*|MSYS*|CYGWIN*|Windows*) kandidaten="python python3 py" ;;
    esac
    local py
    for py in $kandidaten; do
        command -v "$py" >/dev/null 2>&1 || continue
        if "$py" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 8) else 1)' \
                >/dev/null 2>&1; then
            printf '%s' "$py"; return 0
        fi
    done
    return 1
}

if ! KIT_PYTHON="$(kit_python)"; then
    rot "FEHLER: Kein lauffaehiges Python 3.8+ gefunden."
    echo '  Geprueft wurde START UND VERSION, nicht blosse Anwesenheit: Unter' >&2
    echo '  Windows ist "python3" der App-Execution-Alias aus dem Microsoft' >&2
    echo '  Store. Er beantwortet "command -v", ohne einen Interpreter zu' >&2
    echo '  starten (Lehre BL-122).' >&2
    exit 2
fi

# BL-137, zweite Haelfte: pytest wird AUFGELOEST, nicht vorausgesetzt.
#
# Hier stand `command -v pytest`. Das ist genau das Anti-Muster, gegen das
# BL-124 steht: `pip install --user pytest` legt die ausfuehrbare Datei in
# ein Scripts-/bin-Verzeichnis, das oft NICHT im PATH steht — pip warnt beim
# Installieren sogar davor. Das Modul ist dann installiert, `command -v`
# findet trotzdem nichts, und dieses Skript empfahl daraufhin genau die
# Installation, die den Zustand erzeugt hatte. Auf der Windows-Maschine war
# das der ZWEITE Grund, warum die Selbstverifikation der Bash-Bahn dort nicht
# fahrbar war — noch vor der ersten Pruefung.
#
# Der Weg ueber den Interpreter findet es in beiden Faellen und benutzt
# garantiert DASSELBE Python wie die uebrigen Kit-Werkzeuge.
if ! "$KIT_PYTHON" -m pytest --version >/dev/null 2>&1; then
    rot "pytest nicht gefunden — die Selbstverifikation braucht es."
    echo "  Gesucht wurde als MODUL: $KIT_PYTHON -m pytest" >&2
    echo "  Installation: $KIT_PYTHON -m pip install --user pytest" >&2
    exit 2
fi

ZIEL="$(mktemp -d "${TMPDIR:-/tmp}/team-kit-selbsttest.XXXXXX")"
aufraeumen() {
    if [ "$BEHALTEN" -eq 1 ]; then
        printf '\nWegwerf-Repo behalten: %s\n' "$ZIEL"
    else
        rm -rf "$ZIEL"
    fi
}
trap aufraeumen EXIT

kopf "1/11 — Wegwerf-Repo anlegen"
git -C "$ZIEL" init -q
# Lokale Identität, damit der Lauf auch ohne globale Git-Config committen kann.
git -C "$ZIEL" config user.email "kit-test@localhost"
git -C "$ZIEL" config user.name  "Kit-Selbsttest"
gruen "  ✓ $ZIEL"

kopf "2/11 — Kit installieren (nicht-interaktiv)"
# Ohne TEAM_INIT_*-Vorgaben: genau die Defaults, die ein Anwender bekäme.
if ! bash "$KIT/bash/install.sh" "$ZIEL" --nicht-interaktiv > "$ZIEL/.install.log" 2>&1; then
    rot "  ✗ install.sh schlug fehl:"
    tail -20 "$ZIEL/.install.log" >&2
    exit 1
fi
gruen "  ✓ $(grep -oE 'Fertig — [0-9]+ Dateien geschrieben' "$ZIEL/.install.log" | head -1)"

# BL-127: Der Selbsttest des Installers MUSS seine Regressionstests gefahren
# haben. Er meldete "pytest nicht gefunden — übersprungen", weil team_pytest()
# innerhalb des --update-Blocks definiert war und auf dem Erstinstallations-
# Pfad nie zur Ausfuehrung kam. Eine uebersprungene Pruefung sieht in gelb
# fast aus wie eine bestandene; gemerkt hat es niemand, weil kein Schritt
# nachsah. Jetzt sieht einer nach.
if grep -q 'Regressionstests grün' "$ZIEL/.install.log"; then
    gruen "  ✓ und der Selbsttest hat seine Regressionstests wirklich gefahren"
else
    rot "  ✗ Der Installer hat seine Regressionstests NICHT gefahren"
    sed 's/\x1b\[[0-9;]*m//g' "$ZIEL/.install.log" | grep -iE 'pytest|Regressionstests' | head -3
    exit 1
fi

# Die Zahl steht auch in der Doku — und stand dort jahrelang falsch (75 statt
# 117). Eine Zahl, die niemand nachrechnet, veraltet lautlos und liest sich
# trotzdem wie eine Zusicherung. Jetzt rechnet der Installer sie vor und der
# README muss mitziehen.
# Inline statt ueber pruefe(): Die Helfer sind hier noch nicht definiert.
GESCHRIEBEN_IST="$(grep -oE 'Fertig — [0-9]+ Dateien' "$ZIEL/.install.log" \
                   | head -1 | grep -oE '[0-9]+')"
README_NENNT="$(grep -c "$GESCHRIEBEN_IST Dateien" "$KIT/README.md" || true)"
if [ "$README_NENNT" = "2" ]; then
    gruen "  ✓ README nennt dieselbe Dateizahl ($GESCHRIEBEN_IST) an beiden Stellen"
else
    rot "  ✗ README nennt nicht $GESCHRIEBEN_IST Dateien (gefunden: $README_NENNT von 2)"
    echo "      Der Installer schreibt $GESCHRIEBEN_IST Dateien. Eine Zahl, die"
    echo "      niemand nachrechnet, veraltet lautlos und liest sich trotzdem"
    echo "      wie eine Zusicherung — sie stand jahrelang auf 75."
    exit 1
fi

# BL-121: Der Produktivcode-Ordner muss NACH der Installation existieren.
# Vorher wurde sein Name nur eingesetzt — in die Guard-Grenze, in den
# Pruefumfang, in die Briefings der drei Read-Only-Rollen —, aber nie geprueft
# und nie angelegt. Das Red Team prueft dann einen leeren Suchraum und der
# erste Bericht meldet "sauber" ueber nichts.
#
# Drei Zusicherungen, und die dritte ist die, die im Feld gebrochen waere:
# Ein LEERER Ordner ist fuer Git nicht vorhanden. Der Schritt direkt nach der
# Installation heisst "Committen, VOR dem ersten Guard-Lauf" — ohne
# Platzhalterdatei waere der Ordner nach dem naechsten Klon wieder weg.
if [ ! -d "$ZIEL/src" ]; then
    rot "  ✗ Produktivcode-Ordner src/ fehlt nach der Installation (BL-121)"
    exit 1
fi
if [ ! -f "$ZIEL/src/.gitkeep" ]; then
    rot "  ✗ src/ ist leer und ohne .gitkeep — der Ordner faellt beim ersten Commit weg"
    exit 1
fi
gruen "  ✓ Produktivcode-Ordner src/ angelegt, mit .gitkeep"

# Und dasselbe mit einem NICHT vorgegebenen Namen: An src/ ist nichts
# besonderes, der Fehler traf jeden eingegebenen Ordner. Eigenes Wegwerf-Repo,
# damit die Hauptinstallation unberuehrt bleibt.
ZIEL2="$(mktemp -d -t team-kit-bl121.XXXXXX)"
git -C "$ZIEL2" init -q
git -C "$ZIEL2" config user.email "kit-test@localhost"
git -C "$ZIEL2" config user.name  "Kit-Selbsttest"
if ! TEAM_INIT_PRODUKTIVCODE="quelle/" bash "$KIT/bash/install.sh" "$ZIEL2" \
        --nicht-interaktiv > "$ZIEL2/.install.log" 2>&1; then
    rot "  ✗ install.sh mit TEAM_INIT_PRODUKTIVCODE schlug fehl:"
    tail -20 "$ZIEL2/.install.log" >&2
    exit 1
fi
if [ ! -d "$ZIEL2/quelle" ]; then
    rot "  ✗ Eigener Produktivcode-Ordner 'quelle/' wurde nicht angelegt (BL-121)"
    exit 1
fi
if ! grep -q 'ohne Rueckfrage, aber nicht ohne Ansage' "$ZIEL2/.install.log"; then
    rot "  ✗ Der Installer legt 'quelle/' still an — nicht-interaktiv darf er das,"
    echo "      aber nicht wortlos. Die Ansage fehlt im Log."
    exit 1
fi
# Die Commit-Probe gehoert hierher und nicht ins Haupt-Repo: Ein Commit dort
# wuerde den Git-Stand veraendern, gegen den die spaeteren Stufen pruefen.
git -C "$ZIEL2" add -A >/dev/null 2>&1
git -C "$ZIEL2" commit -q -m "test: Installationsstand" >/dev/null 2>&1
if ! git -C "$ZIEL2" ls-files --error-unmatch quelle/.gitkeep >/dev/null 2>&1; then
    rot "  ✗ 'quelle/' hat den Commit nicht ueberlebt — genau der Fall, den"
    echo "      .gitkeep verhindern soll (BL-121)."
    exit 1
fi
rm -rf "$ZIEL2"
gruen "  ✓ Eigener Ordnername wird ebenso angelegt, angesagt und ueberlebt den Commit"

kopf "3/11 — Ungefüllte Platzhalter suchen"
# Ein übrig gebliebenes {{...}} heißt: Der Installer kennt die Datei nicht oder
# der Platzhalter wurde umbenannt. Beides fällt sonst erst im Feld auf, wo die
# Briefings die Pfade des Ursprungsprojekts nennen würden — falsche Guard-Grenze.
# __pycache__ ausgenommen: Dort liegt kompilierter Bytecode, den der Testlauf
# eine Zeile weiter unten selbst erzeugt — kein ausgeliefertes Dokument, in dem
# ein Platzhalter je gefuellt wuerde. Und er ist eine Falschmeldungsquelle: Der
# Compiler faltet benachbarte String-Literale zu einer Konstanten zusammen, so
# dass ein Test, der die Marke bewusst ZERLEGT schreibt, im .pyc trotzdem
# wieder als Fund erscheint (aufgefallen an test_bl131). Die Zusicherung
# betrifft den Quelltext; dort greift sie unveraendert.
RESTE="$(grep -rlE '\{\{[A-Z_]+\}\}' "$ZIEL" \
           --exclude-dir=.git --exclude-dir=__pycache__ \
           --exclude=.install.log 2>/dev/null || true)"
if [ -n "$RESTE" ]; then
    rot "  ✗ Ungefüllte Platzhalter in:"
    echo "$RESTE" | sed 's|^|      |' >&2
    exit 1
fi
gruen "  ✓ keine"

kopf "4/11 — Regressionstests in der Installation (Auslieferungswerte)"
# Vor dem Testlauf committen — dieselbe Reihenfolge, die TEAM.md dem Anwender
# vorschreibt. Ein Test, der den Git-Zustand liest, sieht damit den echten.
git -C "$ZIEL" add -A
git -C "$ZIEL" commit -q -m "chore: T.E.A.M. eingerichtet"

cd "$ZIEL"
# BL-59: `RC=$?` IM then-Zweig eines `if ! cmd` liest immer 0 — das `!` hat den
# Status schon umgedreht. Das Gate schrieb also "FEHLGESCHLAGEN (Exit 0)" und
# beendete sich mit genau diesem Exit 0: rot auf dem Bildschirm, grün für jeden
# Aufrufer. Gefunden bei der Gegenprobe zu Schritt 5, wo dieselbe Zeile stand.
RC=0
./team-test.sh "${PYTEST_ARGS[@]}" || RC=$?
if [ "$RC" -ne 0 ]; then
    rot "
✗ Kit-Selbstverifikation FEHLGESCHLAGEN (Exit $RC)."
    [ "$BEHALTEN" -eq 0 ] && echo "  Mit --behalten erneut laufen lassen, um im Repo nachzusehen." >&2
    exit "$RC"
fi

# Die beiden Zahlen, die im README stehen — nachgerechnet statt geglaubt.
# "62 Testdateien" und "369 Tests" standen dort, waehrend es 65 und 476 waren.
# Eine Zahl, die niemand nachrechnet, veraltet lautlos und liest sich trotzdem
# wie eine Zusicherung (dieselbe Klasse wie die 75 Dateien in Schritt 2).
#
# Bewusst NICHT aus der Ausgabe von team-test.sh gezogen: Deren Exit-Code
# traegt das Ergebnis des ganzen Schritts, und eine Pipeline davor hat schon
# einmal genau diesen Code verschluckt (BL-59). Ein eigener collect-only-Lauf
# kostet eine Sekunde und fasst nichts an.
T_DATEIEN="$(ls "$ZIEL"/team/tests/test_*.py | wc -l | tr -d ' ')"
T_FAELLE="$("$KIT_PYTHON" -m pytest "$ZIEL/team/tests" --collect-only -q 2>/dev/null \
            | tail -1 | grep -oE '^[0-9]+' || true)"
if grep -q "$T_DATEIEN Testdateien, $T_FAELLE Fälle" "$KIT/README.md" \
   && grep -q "die $T_FAELLE Tests" "$KIT/README.md"; then
    gruen "  ✓ README nennt dieselben Testzahlen ($T_DATEIEN Dateien, $T_FAELLE Fälle)"
else
    rot "  ✗ README nennt nicht '$T_DATEIEN Testdateien, $T_FAELLE Fälle' bzw. 'die $T_FAELLE Tests'"
    echo "      Gemessen an der frischen Installation. Beide Stellen im README"
    echo "      nachziehen — sonst steht dort wieder eine Zahl, die niemand prueft."
    exit 1
fi

# BL-58: Schritt 4 prüft die Installation im AUSLIEFERUNGSZUSTAND — dort trägt
# team.config.sh genau die Werte, die auch in team/lib.sh als Default stehen.
# Ein Test, der eine Kit-Zusicherung am AUFGELÖSTEN Wert misst statt an der
# Bibliothek, ist deshalb hier grün, obwohl er die falsche Stelle misst. Rot
# wird er erst in einem Feldprojekt, das seine Werte angepasst hat — also an dem
# einen Ort, an dem niemand mehr auf einen Kit-Test schaut.
#
# Genau so ging BL-58 durch: `test_zentrale_defaults` las den Soft-Cap per
# `source team/lib.sh` — und lib.sh sourct in ihren ersten Zeilen selbst die
# team.config.sh des Projekts. Der Test las damit den Projektwert und behauptete,
# den Bibliotheks-Default zu prüfen. Im Kit und in jeder frischen Installation
# grün, im Feld rot, sobald dort ein Cap regelkonform angehoben wurde.
#
# Dieser Schritt ist die fehlende Messstelle: dieselbe Suite ein zweites Mal,
# gegen eine Installation, in der die zum Verstellen GEDACHTEN Werte verstellt
# SIND. Verstellt wird nur, wozu team.config.sh an Ort und Stelle einlädt —
# Caps ("lieber großzügig ansetzen"), Commit-Präfixe, mehrere Domänen. Pfade
# und Ordner bleiben unangetastet: Die sind die Ablage, gegen die die Tests
# gelten dürfen, nicht der Regler, an dem ein Projekt dreht.
kopf "5/11 — Regressionstests unter angepasster team.config.sh (BL-58)"
sed -i \
    -e 's|^TEAM_ROLE_BUDGET_USD=.*|TEAM_ROLE_BUDGET_USD="${TEAM_ROLE_BUDGET_USD:-10}"|' \
    -e 's|^TEAM_ROLE_HARDCAP_USD=.*|TEAM_ROLE_HARDCAP_USD="${TEAM_ROLE_HARDCAP_USD:-20}"|' \
    -e 's|^TEAM_FIX_PRAEFIX=.*|TEAM_FIX_PRAEFIX="${TEAM_FIX_PRAEFIX:-fix(qa)}"|' \
    -e 's|^TEAM_FEAT_PRAEFIX=.*|TEAM_FEAT_PRAEFIX="${TEAM_FEAT_PRAEFIX:-feature}"|' \
    -e 's|^TEAM_DOMAENEN=.*|TEAM_DOMAENEN="${TEAM_DOMAENEN:-backend frontend}"|' \
    "$ZIEL/team.config.sh"
# Ein `sed`, das nichts trifft, meldet sich nicht — die Suite liefe dann gegen
# die unveränderte Config und wäre grün, ohne irgendetwas geprüft zu haben.
# Das wäre dieselbe Bauart wie der Fund selbst, nur eine Etage höher.
for erwartet in 'TEAM_ROLE_BUDGET_USD:-10' 'TEAM_ROLE_HARDCAP_USD:-20' \
                'TEAM_FIX_PRAEFIX:-fix(qa)' 'TEAM_FEAT_PRAEFIX:-feature' \
                'TEAM_DOMAENEN:-backend frontend'; do
    if ! grep -qF -- "$erwartet" "$ZIEL/team.config.sh"; then
        rot "  ✗ '$erwartet' steht nicht in team.config.sh — die Anpassung hat nicht gegriffen."
        echo "      Variable umbenannt oder Zeile umgebaut? Dann prüft dieser Schritt nichts mehr." >&2
        exit 1
    fi
done
gruen "  ✓ Caps 10/20, Präfixe fix(qa)/feature, zwei Domänen gesetzt"

RC=0
./team-test.sh "${PYTEST_ARGS[@]}" || RC=$?
if [ "$RC" -ne 0 ]; then
    rot "
✗ Die Suite ist grün im Auslieferungszustand und rot mit angepasster Config (Exit $RC)."
    echo "  Das ist der BL-58-Fall: Der fehlgeschlagene Test misst den PROJEKTWERT," >&2
    echo "  behauptet aber, eine Zusicherung des KITS zu prüfen. Die Zusicherung ist" >&2
    echo "  meist richtig, die Messstelle falsch — Vorbild für den Umbau ist" >&2
    echo "  _lib_default() in team/tests/test_hm32_budget_zwei_schwellen.py: Es liest" >&2
    echo "  die Zeile NAME=\"\${NAME:-wert}\" statisch aus team/lib.sh, statt zu sourcen." >&2
    echo "  Gilt die Zusicherung dagegen wirklich für den aufgelösten Wert (Beispiel:" >&2
    echo "  hard > soft), gehört sie ausdrücklich als solche geschrieben." >&2
    exit "$RC"
fi

# BL-8: --update ist der einzige sichere Weg, ein gelebtes Projekt auf eine
# neue Kit-Version zu heben. Der Beweis dafuer gehoert ins Gate, nicht in ein
# einmaliges Handprotokoll: Wir tun so, als sei das Projekt in Betrieb
# (Ledger, Kaskadenstand, Beutebuch-Fund, eigener Smoke-Test), fahren das
# Update und pruefen, dass davon NICHTS angefasst wurde.
kopf "6/11 — Update-Pfad schuetzt Projektdaten"
echo '2026-08-01 | 1 | 9.4204 | abo | produkt | roles | Lauf' >> "$ZIEL/.budget-ledger"
echo '### HM-1 — echter Fund' >> "$ZIEL/plans/beutebuch.md"
echo '5' > "$ZIEL/.ralph-state"
sed -i 's|^TEAM_SMOKE_TEST=.*|TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-./smoke.sh}"|' \
    "$ZIEL/team.config.sh"
# Ein Test, den das Kit nicht kennt — wie ihn ein Projekt schreibt, das eine
# Luecke im Team selbst schliesst, bevor der Fund im Kit ankommt.
printf 'def test_projekteigener_fund():\n    assert True\n' \
    > "$ZIEL/team/tests/test_projekteigener_fund.py"
# Eine lokal veraenderte Infrastruktur-Datei — der Fall, in dem ein noch nicht
# zurueckgemeldeter Fix vom Update ueberschrieben wird.
printf '\n# lokaler Fix, noch nicht ans Kit gemeldet\n' >> "$ZIEL/team/tools/beutebuch.py"
# BL-109: Ein .gitignore auf dem Fragmentstand eines aelteren Kits — genau die
# Lage jedes Projekts, das frueh installiert und seither nur --update gefahren
# hat. Der Block ist vorhanden, zwei seither dazugekommene Zeilen fehlen. Der
# Installer hat das bisher als "enthaelt den Block bereits" abgehakt.
sed -i '/^\.team-focus-harry$/d; /^\.team-focus-marv$/d' "$ZIEL/.gitignore"
# BL-136 hat dieselbe Bauart fuer die .gitattributes gebaut, aber nur die
# pwsh-Bahn hat sie nachgewiesen. Dieselbe Lage hier: Block vorhanden, zwei
# Zeilen der Vorlage fehlen. Ohne diesen Griff faehrt der Melde-Zweig von
# gitattributes_abgleich() in der bash-Bahn ueberhaupt nie.
sed -i '/^\*\.psm1[[:space:]]/d; /^\*\.bat[[:space:]]/d' "$ZIEL/.gitattributes"

if ! bash "$KIT/bash/install.sh" "$ZIEL" --update > "$ZIEL/.update.log" 2>&1; then
    rot "  ✗ install.sh --update schlug fehl:"
    tail -20 "$ZIEL/.update.log" >&2
    exit 1
fi

UPDATE_FEHLER=0
pruefe() {  # pruefe <beschreibung> <ist> <soll>
    if [ "$2" = "$3" ]; then
        gruen "  ✓ $1"
    else
        rot "  ✗ $1 — erwartet '$3', ist '$2'"
        UPDATE_FEHLER=1
    fi
}
pruefe "Ledger unangetastet"      "$(grep -c 'Lauf$' "$ZIEL/.budget-ledger")" "1"
pruefe "Kaskadenstand unangetastet" "$(cat "$ZIEL/.ralph-state")"             "5"
pruefe "Beutebuch-Fund erhalten"  "$(grep -c 'HM-1' "$ZIEL/plans/beutebuch.md")" "1"
pruefe "Smoke-Test in der Config erhalten" \
       "$(grep -c 'smoke.sh' "$ZIEL/team.config.sh")" "1"
# Der konkrete BL-58-Wert: Genau diese Anhebung hat im Feld ein `--update`
# nicht ueberlebt — allerdings in der Testdatei, nicht in der Config. Dass die
# Config sie traegt, ist die andere Haelfte des Versprechens.
pruefe "angehobener Hard-Cap ueberlebt das Update" \
       "$(grep -c 'TEAM_ROLE_HARDCAP_USD:-20' "$ZIEL/team.config.sh")" "1"
# BL-12: NICHT loeschen. Ein Testfile, das das Kit nicht kennt, kann ein
# projekteigener Infrastruktur-Test sein — im Feld hat ein pauschales rm genau
# so einen geloescht. Es bleibt liegen und wird gemeldet.
pruefe "projekteigener Test in team/tests bleibt erhalten" \
       "$([ -f "$ZIEL/team/tests/test_projekteigener_fund.py" ] && echo da || echo weg)" "da"
pruefe "und wird als unbekannt gemeldet" \
       "$(grep -c 'test_projekteigener_fund.py' "$ZIEL/.update.log")" "1"
pruefe "lokal abweichende Infrastruktur wird gemeldet" \
       "$(grep -c 'bitte gegenlesen' "$ZIEL/.update.log")" "1"
pruefe "keine offenen Platzhalter in den Briefings" \
       "$(grep -rlE '\{\{[A-Z_]+\}\}' "$ZIEL/team/prompts/" | wc -l)" "0"
# Der Abgleich-Hinweis muss AUSFUEHRBAR sein, nicht nur gut gemeint. Vorher
# stand dort `diff <(…)` — ein Platzhalter, den niemand kopieren kann, fuer
# genau die Arbeit, die der Hinweis abnehmen wollte (Bauart BL-44).
pruefe "Abgleich-Hinweis nennt keinen Platzhalter mehr" \
       "$(grep -c 'diff <(…)' "$ZIEL/.update.log")" "0"
# BL-137: `diff [^"]*-u` statt `diff -u` — der Befehl traegt seit dem Fix
# --strip-trailing-cr zwischen Kommando und Flagge. Ein Muster, das den
# Befehl bis aufs Zeichen festnagelt, prueft nicht den Hinweis, sondern
# seine Schreibweise, und macht jede Verbesserung daran zum Testfehler.
ABGLEICH_BEFEHL="$(grep -oE 'diff [^"]*-u "[^"]+" "[^"]+"' "$ZIEL/.update.log" | head -1)"
pruefe "Abgleich-Hinweis nennt einen diff-Befehl" \
       "$([ -n "$ABGLEICH_BEFEHL" ] && echo ja || echo nein)" "ja"
# Die genannte gerenderte Vorlage muss existieren UND gefuellt sein — ein Pfad
# auf eine geloeschte Datei waere derselbe Fehler in gruen.
ABGLEICH_QUELLE="$(printf '%s' "$ABGLEICH_BEFEHL" | sed -E 's/^diff [^"]*-u "([^"]+)".*/\1/')"
pruefe "die genannte Kit-Fassung liegt wirklich da" \
       "$([ -f "$ABGLEICH_QUELLE" ] && echo da || echo weg)" "da"
# `grep -c` gibt bei null Treffern "0" aus UND Exit 1 zurueck — ein `|| echo 99`
# haengt seinen Wert deshalb an die 0 an, statt sie zu ersetzen. `|| true`
# schluckt nur den Exit; fehlt die Datei, bleibt die Ausgabe leer und die
# Pruefung schlaegt korrekt fehl.
pruefe "und traegt die Projektwerte statt Platzhalter" \
       "$(grep -cE '\{\{[A-Z_]+\}\}' "$ABGLEICH_QUELLE" 2>/dev/null || true)" "0"
pruefe "der Befehl laeuft und zeigt Unterschiede" \
       "$(eval "$ABGLEICH_BEFEHL" >/dev/null 2>&1; echo $?)" "1"
# Nicht im Projekt ablegen: Eine uncommittete Datei ausserhalb der Whitelist
# sieht fuer den Read-Only-Guard aus wie ein Regelbruch.
pruefe "die Kit-Fassung liegt NICHT im Projekt" \
       "$(case "$ABGLEICH_QUELLE" in "$ZIEL"/*) echo drin ;; *) echo draussen ;; esac)" "draussen"
# Aufraeumen NUR bei einem plausiblen Pfad. Ohne diese Schranke waere
# ABGLEICH_QUELLE bei einem fehlgeschlagenen Match leer, `dirname ""` ergaebe
# "." — und `rm -rf .` raeumte das Arbeitsverzeichnis ab.
case "$ABGLEICH_QUELLE" in
    */team-kit-abgleich-*/*) rm -rf "$(dirname "$ABGLEICH_QUELLE")" ;;
    *) gelb "  (kein Abgleich-Verzeichnis erkannt — nichts aufgeraeumt)" ;;
esac

# BL-109: Der zurueckgebliebene .gitignore-Block wird GEMELDET, nicht als
# "enthaelt den Block bereits" abgehakt — und beide fehlenden Zeilen werden
# namentlich genannt, sonst weiss niemand, was nachzutragen ist. Der stille
# Fall ist der teure: Das Update meldete bisher Erfolg und liess das Projekt
# trotzdem auf dem Fragmentstand seines Installationstages zurueck.
pruefe "veraltetes .gitignore wird gemeldet" \
       "$(grep -c '\.gitignore liegt .* hinter der Vorlage' "$ZIEL/.update.log")" "1"
pruefe "mit der richtigen Zeilenzahl" \
       "$(grep -c '\.gitignore liegt 2 Zeile(n) hinter der Vorlage' "$ZIEL/.update.log")" "1"
# Je zweimal: einmal in der Aufzaehlung, einmal im nachtragbaren Befehl.
pruefe "erste fehlende Zeile namentlich genannt" \
       "$(grep -c '\.team-focus-harry' "$ZIEL/.update.log")" "2"
pruefe "zweite fehlende Zeile namentlich genannt" \
       "$(grep -c '\.team-focus-marv' "$ZIEL/.update.log")" "2"
# Nicht eigenmaechtig ergaenzen: Eine fehlende Zeile kann eine bewusst
# entfernte sein. Die Meldung ist die risikofreie Haelfte.
pruefe ".gitignore wird NICHT von selbst ergaenzt" \
       "$(grep -c 'team-focus' "$ZIEL/.gitignore")" "0"

# BL-136, dieselben vier Zusicherungen fuer die .gitattributes. Sie fehlten:
# Der Fix ist am 2026-08-21 nur gegen kit-test.ps1 (6 Schritte) nachgewiesen
# worden, und die bash-Bahn hat die Datei seither ueberhaupt nicht angefasst.
# Genau die Luecke, an der der Fehlbetrag bis zum naechsten Feldlauf sitzt.
pruefe "veraltete .gitattributes wird gemeldet" \
       "$(grep -c '\.gitattributes liegt .* hinter der Vorlage' "$ZIEL/.update.log")" "1"
pruefe "mit der richtigen Zeilenzahl" \
       "$(grep -c '\.gitattributes liegt 2 Zeile(n) hinter der Vorlage' "$ZIEL/.update.log")" "1"
# Je zweimal wie oben: Aufzaehlung und nachtragbarer Befehl.
pruefe "fehlende LF-Zeile namentlich genannt" \
       "$(grep -c '\*\.psm1' "$ZIEL/.update.log")" "2"
pruefe "fehlende CRLF-Zeile namentlich genannt" \
       "$(grep -c '\*\.bat' "$ZIEL/.update.log")" "2"
# Der zweite Schritt gehoert zur Meldung: Ohne `add --renormalize` wirkt der
# Nachtrag erst beim naechsten Klon — genau der Abstand zwischen Ursache und
# Wirkung, den BL-136 schliessen wollte.
pruefe "und der Renormalisierungs-Schritt dazu" \
       "$(grep -c 'add --renormalize' "$ZIEL/.update.log")" "1"
pruefe ".gitattributes wird NICHT von selbst ergaenzt" \
       "$(grep -c '^\*\.psm1' "$ZIEL/.gitattributes")" "0"
# Gegenprobe: Eine Meldung, die immer erscheint, ist keine (Bauart BL-14).
# Mit vollstaendigem Fragment muss derselbe Lauf schweigen.
printf '.team-focus-harry\n.team-focus-marv\n' >> "$ZIEL/.gitignore"
printf '*.psm1  text eol=lf\n*.bat   text eol=crlf\n' >> "$ZIEL/.gitattributes"
if ! bash "$KIT/bash/install.sh" "$ZIEL" --update > "$ZIEL/.update2.log" 2>&1; then
    rot "  ✗ zweiter install.sh --update (Gegenprobe) schlug fehl:"
    tail -20 "$ZIEL/.update2.log" >&2
    exit 1
fi
pruefe "vollstaendiges .gitignore wird nicht angemahnt" \
       "$(grep -c '\.gitignore liegt .* hinter der Vorlage' "$ZIEL/.update2.log")" "0"
pruefe "und ausdruecklich als vollstaendig quittiert" \
       "$(grep -c '\.gitignore enthält den Block vollständig' "$ZIEL/.update2.log")" "1"
pruefe "vollstaendige .gitattributes wird nicht angemahnt" \
       "$(grep -c '\.gitattributes liegt .* hinter der Vorlage' "$ZIEL/.update2.log")" "0"
pruefe "und ausdruecklich als vollstaendig quittiert" \
       "$(grep -c '\.gitattributes enthält den Block vollständig' "$ZIEL/.update2.log")" "1"
# Auch dieser Lauf legt eine Kit-Fassung zum Abgleich ab — mit aufraeumen,
# sonst bleibt je Selbsttest ein Verzeichnis in /tmp liegen.
ABGLEICH2="$(grep -oE 'diff [^"]*-u "[^"]+"' "$ZIEL/.update2.log" | head -1 \
             | sed -E 's/^diff [^"]*-u "([^"]+)"/\1/')"
case "$ABGLEICH2" in
    */team-kit-abgleich-*/*) rm -rf "$(dirname "$ABGLEICH2")" ;;
esac

[ "$UPDATE_FEHLER" -eq 0 ] || exit 1

# BL-51/BL-52: Die beiden Bestandsprojekt-Befunde. Der Installer ist die einzige
# Stelle, an der sie auffallen koennen — in der Installation liegt er nicht mehr,
# also gehoert der Nachweis hierher und nicht in team/tests/.
kopf "7/11 — Einzug in eine gewachsene Codebasis (BL-51, BL-52)"
BESTAND_REPO="$(mktemp -d "${TMPDIR:-/tmp}/team-kit-bestand.XXXXXX")"
bestand_aufraeumen() { [ "$BEHALTEN" -eq 1 ] || rm -rf "$BESTAND_REPO"; }
trap 'aufraeumen; bestand_aufraeumen' EXIT
git -C "$BESTAND_REPO" init -q
git -C "$BESTAND_REPO" config user.email "kit-test@localhost"
git -C "$BESTAND_REPO" config user.name  "Kit-Selbsttest"
# Die Lage aus Project-Family-ERP: belegtes plans/, gewachsene Testsuite,
# Einstiegspunkt in der Wurzel.
mkdir -p "$BESTAND_REPO/plans" "$BESTAND_REPO/tests" "$BESTAND_REPO/src"
echo '# Architektur' > "$BESTAND_REPO/plans/family-erp-architecture.md"
echo '# Refactoring' > "$BESTAND_REPO/plans/codebase-refactoring-plan.md"
echo 'def test_alt(): pass' > "$BESTAND_REPO/tests/test_scanner.py"
echo 'print("start")' > "$BESTAND_REPO/main.py"
git -C "$BESTAND_REPO" add -A
git -C "$BESTAND_REPO" commit -q -m "Bestand vor dem Einzug"

# tests/ im Pruefumfang ist die Falle aus dem Feld: Der Ordner steht dann
# zugleich als "tabu" und als Schreibziel im selben Rollen-Prompt.
if ! TEAM_INIT_WEITERER_CODE="tests/" bash "$KIT/bash/install.sh" "$BESTAND_REPO" --nicht-interaktiv \
        > "$BESTAND_REPO/.install.log" 2>&1; then
    rot "  ✗ install.sh schlug im Bestandsprojekt fehl:"
    tail -20 "$BESTAND_REPO/.install.log" >&2
    exit 1
fi

BESTAND_FEHLER=0
b_pruefe() {  # b_pruefe <beschreibung> <ist> <soll>
    if [ "$2" = "$3" ]; then
        gruen "  ✓ $1"
    else
        rot "  ✗ $1 — erwartet '$3', ist '$2'"
        BESTAND_FEHLER=1
    fi
}
b_pruefe "belegter Plan-Ordner wird gemeldet" \
    "$(grep -c "Plan-Ordner 'plans/' ist nicht leer" "$BESTAND_REPO/.install.log")" "1"
b_pruefe "die Folge wird benannt (Waechter greift dort nicht)" \
    "$(grep -c 'greift in diesem Ordner NICHT' "$BESTAND_REPO/.install.log")" "2"
b_pruefe "belegter Test-Ordner wird gemeldet" \
    "$(grep -c "Test-Ordner 'tests/' ist nicht leer" "$BESTAND_REPO/.install.log")" "1"
b_pruefe "Bestandsdokument namentlich genannt" \
    "$(grep -c 'family-erp-architecture.md' "$BESTAND_REPO/.install.log")" "1"
# Der Vermerk ist der Traeger: Aus ihm holen die Rollen-Prompts den Bestand.
b_pruefe "Plan-Bestand steht in team.config.sh" \
    "$(grep -c 'TEAM_PLAN_ORDNER_BESTAND:-.*codebase-refactoring-plan.md' \
        "$BESTAND_REPO/team.config.sh")" "1"
b_pruefe "Test-Bestand steht in team.config.sh" \
    "$(grep -c 'TEAM_TEST_ORDNER_BESTAND:-.*test_scanner.py' \
        "$BESTAND_REPO/team.config.sh")" "1"
b_pruefe "keine offenen Platzhalter" \
    "$(grep -rlE '\{\{[A-Z_]+\}\}' "$BESTAND_REPO" --exclude-dir=.git \
        --exclude=.install.log 2>/dev/null | wc -l)" "0"
# Kollision Pruefumfang/Schreibzone: Ein Schreibordner im Pruefumfang machte den
# Rollen-Prompt widerspruechlich ("tabu" und "schreib hierhin" in EINEM Absatz).
b_pruefe "Schreibordner wird aus dem Pruefumfang genommen" \
    "$(grep -c 'Wieder aus dem Prüfumfang genommen: tests/' "$BESTAND_REPO/.install.log")" "1"
b_pruefe "und landet nicht in team.config.sh" \
    "$(grep -c 'TEAM_WEITERER_CODE:-tests' "$BESTAND_REPO/team.config.sh")" "0"
# Gegenprobe: Im leeren Repo aus Schritt 2 darf nichts davon erschienen sein —
# eine Warnung, die immer kommt, erzieht zum Wegsehen (BL-14).
b_pruefe "im leeren Repo schweigt die Pruefung" \
    "$(grep -c 'ist nicht leer' "$ZIEL/.install.log")" "0"
b_pruefe "und meldet die leere Schreibzone ausdruecklich" \
    "$(grep -c 'nichts fremdes in der Schreibzone' "$ZIEL/.install.log")" "1"
# BL-52: Der Hinweis auf ungeprueften Wurzel-Code kommt beim Update, weil
# team.config.sh dort nicht angefasst wird.
if ! bash "$KIT/bash/install.sh" "$BESTAND_REPO" --update \
        > "$BESTAND_REPO/.update.log" 2>&1; then
    rot "  ✗ install.sh --update schlug im Bestandsprojekt fehl:"
    tail -20 "$BESTAND_REPO/.update.log" >&2
    exit 1
fi
b_pruefe "Update meldet ungeprueften Code in der Wurzel" \
    "$(grep -c 'Ungeprueft in der Wurzel: main.py' "$BESTAND_REPO/.update.log")" "1"
b_pruefe "Update erinnert an den Bestand in der Schreibzone" \
    "$(grep -c 'Bestand in der Schreibzone' "$BESTAND_REPO/.update.log")" "1"
b_pruefe "im leeren Repo schweigt auch das Update" \
    "$(grep -c 'Ungeprueft in der Wurzel' "$ZIEL/.update.log")" "0"
[ "$BESTAND_FEHLER" -eq 0 ] || exit 1

kopf "8/11 — Abwahl einer Bahn und ihr Rueckweg (BL-119)"
# Der Schalter --nur-bash/--nur-pwsh ist eine ausdrueckliche Abwahl durch den
# Anwender. Was ihn ueberhaupt erst vertretbar macht, ist der RUECKWEG: Ein
# spaeteres --update ohne Schalter muss das Projekt wieder vollstaendig
# machen. Sonst waere die Abwahl eine Einbahnstrasse, und der Anwender saesse
# mit einem halben Projekt da, ohne es zu merken.
#
# Beim ersten Bau ist genau das passiert: Die Entrypoints kamen zurueck, die
# KONFIGURATION nicht — ein Update fasst team.config.* grundsaetzlich nicht
# an. Richtig, solange sie da ist; fehlt sie, ist "nicht anfassen" kein
# Schutz, sondern eine halbe Bahn. Deshalb steht der Rueckweg hier und nicht
# in der Doku.
A_REPO="$(mktemp -d)/projekt"
mkdir -p "$A_REPO"
git -C "$A_REPO" init -q
git -C "$A_REPO" commit -q --allow-empty -m "init"

bash "$KIT/bash/install.sh" "$A_REPO" --nicht-interaktiv --nur-bash \
     > "$A_REPO/.abwahl.log" 2>&1 || { rot "  ✗ Installation mit --nur-bash schlug fehl"; exit 1; }

a_pruefe() {
    if [ "$2" = "$3" ]; then gruen "  ✓ $1"
    else rot "  ✗ $1 — erwartet: $3, ist: $2"; exit 1; fi
}
a_pruefe "keine .ps1/.cmd im Projekt"  "$(ls "$A_REPO" | grep -cE '\.ps1$|\.cmd$')" "0"
a_pruefe "die Bash-Bahn ist vollstaendig" "$(ls "$A_REPO"/*.sh | wc -l)" "10"
a_pruefe "kein PowerShell-Kern in team/" \
    "$(ls "$A_REPO/team" | grep -cE '\.psm1$|\.ps1$')" "0"
a_pruefe "und die Abwahl steht im Protokoll" \
    "$(grep -c 'Nur die bash-Bahn installiert' "$A_REPO/.abwahl.log")" "1"

# Die Tests des Projekts duerfen in einer einbahnigen Ablage nicht ROT sein.
# Eine abgewaehlte Bahn ist kein Defekt — aber der Uebersprung muss SICHTBAR
# sein, sonst liest er sich am Ende wie ein bestandener Nachweis.
( cd "$A_REPO" && "$KIT_PYTHON" -m pytest team/tests -q > .einbahnig.log 2>&1 )
a_pruefe "Tests bleiben gruen (kein Fehlschlag durch die fehlende Bahn)" \
    "$(grep -cE '^[0-9]+ (failed|error)' "$A_REPO/.einbahnig.log")" "0"
a_pruefe "und die Einbahnigkeit steht in der Zusammenfassung" \
    "$(grep -c 'einbahnige Ablage' "$A_REPO/.einbahnig.log")" "1"

# --- Der Rueckweg
git -C "$A_REPO" add -A >/dev/null 2>&1
git -C "$A_REPO" commit -q -m "einbahnig installiert"
bash "$KIT/bash/install.sh" "$A_REPO" --update > "$A_REPO/.rueckweg.log" 2>&1 \
    || { rot "  ✗ --update auf einem einbahnigen Projekt schlug fehl"; \
         sed 's/\x1b\[[0-9;]*m//g' "$A_REPO/.rueckweg.log" | tail -20; exit 1; }
a_pruefe "--update holt die pwsh-Bahn zurueck" \
    "$(ls "$A_REPO" | grep -cE '\.ps1$|\.cmd$')" "19"
a_pruefe "auch den PowerShell-Kern" \
    "$(ls "$A_REPO/team" | grep -cE '\.psm1$|\.ps1$')" "2"
a_pruefe "team.config.ps1 ist wieder da" \
    "$([ -f "$A_REPO/team.config.ps1" ] && echo ja || echo nein)" "ja"
# Der eigentliche Fund: Die Datei war da und trotzdem halb fertig.
a_pruefe "und VOLLSTAENDIG gefuellt (kein Platzhalter uebrig)" \
    "$(grep -c '{{' "$A_REPO/team.config.ps1")" "0"
a_pruefe "mit den Werten des Projekts, nicht den Auslieferungswerten" \
    "$(grep -c "TEAM_PROJEKT' 'projekt'" "$A_REPO/team.config.ps1")" "1"
a_pruefe "und das Nachziehen ist gemeldet worden" \
    "$(grep -c 'team.config.ps1 fehlte und ist neu erzeugt worden' "$A_REPO/.rueckweg.log")" "1"
rm -rf "$(dirname "$A_REPO")"

# --- Dieselbe Zusicherung in der ANDEREN Richtung (BL-126)
# Bis hierher stand oben nur --nur-bash. Das ist die Richtung, die zufaellig
# funktionierte: Der Update-Pfad las seine Projektwerte aus team.config.sh und
# nahm ihr Vorhandensein zugleich als Merkmal "ist eine Installation". In einem
# mit --nur-pwsh installierten Projekt gibt es diese Datei nicht — der
# Installer erklaerte es fuer keine Installation und stieg mit Exit 2 aus,
# BEVOR er die fehlende Bahn nachziehen konnte. Die Abwahl war in dieser
# Richtung genau die Einbahnstrasse, die sie nicht sein darf.
#
# Im Feld getroffen hat es einen Windows-Anwender, also den Normalfall, fuer
# den die pwsh-Bahn ueberhaupt gebaut ist.
B_REPO="$(mktemp -d)/projekt"
mkdir -p "$B_REPO"
git -C "$B_REPO" init -q
git -C "$B_REPO" commit -q --allow-empty -m "init"

TEAM_INIT_PRODUKTIVCODE="quellcode/" TEAM_INIT_PROJEKT="einbahnig-pwsh" \
    bash "$KIT/bash/install.sh" "$B_REPO" --nicht-interaktiv --nur-pwsh \
    > "$B_REPO/.abwahl.log" 2>&1 \
    || { rot "  ✗ Installation mit --nur-pwsh schlug fehl"; \
         sed 's/\x1b\[[0-9;]*m//g' "$B_REPO/.abwahl.log" | tail -10; exit 1; }
a_pruefe "keine .sh im Projekt" "$(ls "$B_REPO" | grep -cE '\.sh$')" "0"
# BL-128: In dieser Ablage findet der Glob des Selbsttests nichts. Reicht bash
# das Muster durch, meldet der Installer "Syntaxfehler: *.sh" und Exit 1 —
# eine gelungene Installation, die sich selbst fuer kaputt erklaert.
a_pruefe "und der Selbsttest meldet KEINEN Syntaxfehler ueber das Glob-Muster" \
    "$(grep -c 'Syntaxfehler: \*.sh' "$B_REPO/.abwahl.log")" "0"

# BL-129, abgetragen 2026-08-21: Hier stand jahrelang "BEWUSST NICHT geprueft
# — sie sind es nicht (109 rot)". Das war ehrlich und es war eine Luecke: Die
# Zusicherung "Tests bleiben gruen in einbahniger Ablage" galt nur in der
# Richtung, die oben geprueft wird (--nur-bash). Die andere blieb offen, weil
# ein Test, der EINE Bahn FAEHRT, keinen Uebersprung fuer IHR Fehlen hatte —
# er lief los und scheiterte an einer Datei, die es dort nicht gibt.
#
# Aufgeloest haben es BL-130 und BL-133 nebenbei: Seit die Tests ihre Umgebung
# ueber basis_umgebung() beziehen und der Harnisch Module mit bash-Abhaengigkeit
# beim Einsammeln ueberspringt, ist die Ablage gruen. Nachgemessen statt
# angenommen: 198 gruen, 371 uebersprungen, NULL rot.
#
# Der Uebersprung MUSS sichtbar sein. Ein stiller Uebersprung von 371 Faellen
# liest sich am Ende wie ein bestandener Nachweis, und das waere schlimmer als
# das rote Bild, das er ersetzt — deshalb steht die Quotenzeile mit unter Test
# und nicht nur die Farbe.
( cd "$B_REPO" && "$KIT_PYTHON" -m pytest team/tests -q > .einbahnig.log 2>&1 ) \
    || { rot "  ✗ Tests in einer nur-pwsh-Ablage sind ROT (BL-129)"; \
         tail -25 "$B_REPO/.einbahnig.log" >&2; exit 1; }
a_pruefe "Tests bleiben gruen (kein Fehlschlag durch die fehlende Bahn)" \
    "$(grep -cE '^[0-9]+ (failed|error)' "$B_REPO/.einbahnig.log")" "0"
a_pruefe "und die Einbahnigkeit steht in der Zusammenfassung" \
    "$(grep -c 'einbahnige Ablage' "$B_REPO/.einbahnig.log")" "1"
# Der eigentliche Inhalt von BL-129: Die uebersprungene Bahn wird BENANNT und
# GEZAEHLT. Ohne die Zahl bliebe unsichtbar, wie viel der Nachweis ausgelassen
# hat.
a_pruefe "die abgewaehlte bash-Bahn ist als Uebersprung ausgewiesen" \
    "$(grep -c 'bash-Bahn uebersprungen' "$B_REPO/.einbahnig.log")" "1"
a_pruefe "und der Grund nennt die ABWAHL, nicht einen Defekt" \
    "$(grep -c 'in dieser Ablage abgewaehlt (--nur-pwsh)' "$B_REPO/.einbahnig.log")" "1"
a_pruefe "samt Rueckweg" \
    "$(grep -c 'update ohne Schalter holt sie zurueck' "$B_REPO/.einbahnig.log")" "2"

git -C "$B_REPO" add -A >/dev/null 2>&1
git -C "$B_REPO" commit -q -m "einbahnig pwsh installiert"
bash "$KIT/bash/install.sh" "$B_REPO" --update > "$B_REPO/.rueckweg.log" 2>&1 \
    || { rot "  ✗ --update auf einem NUR-PWSH-Projekt schlug fehl (BL-126)"; \
         sed 's/\x1b\[[0-9;]*m//g' "$B_REPO/.rueckweg.log" | tail -20; exit 1; }
a_pruefe "--update holt die Bash-Bahn zurueck" "$(ls "$B_REPO"/*.sh | wc -l)" "10"
a_pruefe "team.config.sh ist wieder da" \
    "$([ -f "$B_REPO/team.config.sh" ] && echo ja || echo nein)" "ja"
a_pruefe "und VOLLSTAENDIG gefuellt (kein Platzhalter uebrig)" \
    "$(grep -c '{{' "$B_REPO/team.config.sh")" "0"
# Der Kern: Die Werte muessen aus der VORHANDENEN Konfiguration stammen. Faellt
# der Installer auf die Auslieferungswerte zurueck, bekommt die zurueckgeholte
# Bahn eine andere Guard-Grenze als die, die schon laeuft — und der Guard
# schuetzt dann den falschen Ordner.
a_pruefe "mit den Werten des Projekts, aus team.config.ps1 gelesen" \
    "$(grep -c 'TEAM_PRODUKTIVCODE:-quellcode/' "$B_REPO/team.config.sh")" "1"
a_pruefe "und die Quelle steht im Protokoll" \
    "$(grep -c 'Projektwerte aus team.config.ps1 gelesen' "$B_REPO/.rueckweg.log")" "1"
a_pruefe "das Nachziehen ist gemeldet worden" \
    "$(grep -c 'team.config.sh fehlte und ist neu erzeugt worden' "$B_REPO/.rueckweg.log")" "1"
rm -rf "$(dirname "$B_REPO")"

kopf "9/11 — Regel-Inventar gegen die Regeldatei (A.10, BL-56)"
# Der Sicherheitsgurt vor dem Umbau der Regeldatei: Jedes NORM-Zitat muss
# woertlich in bootstrap/CLAUDE.md.vorlage stehen, jeder Abschnitt im Inventar
# vertreten sein. Prueft die VORLAGE, nicht die Installation — ein Feldprojekt
# darf seine CLAUDE.md umformulieren (so haelt es test_bl55 ausdruecklich
# fest), die Vorlage darf es nicht unbemerkt.
if ! "$KIT_PYTHON" "$KIT/geteilt/kit-regelinventar.py"; then
    rot "  ✗ Regel-Inventar und Regeldatei stehen auseinander."
    exit 1
fi

kopf "10/11 — Einrichtungsroutine (Klon → Maschine → Installer)"
# kit-einrichten.sh steht VOR install.sh: Wer es kaputt ausliefert, blockiert
# den Einstieg, noch bevor die Stufen 1–8 ueberhaupt zum Tragen kommen. Der
# Weg wird deshalb hier durchgespielt — ohne Agenten-CLI und ohne Schreiben
# ausserhalb des Wegwerf-Repos (--nur-pruefen fasst nichts an).
E_FEHLER=0
e_pruefe() {  # e_pruefe <beschreibung> <ist> <soll>
    if [ "$2" = "$3" ]; then gruen "  ✓ $1"
    else rot "  ✗ $1 — erwartet '$3', ist '$2'"; E_FEHLER=1; fi
}

for f in "$KIT/bash/kit-einrichten.sh" "$KIT"/bash/scripts/*.sh; do
    if bash -n "$f" 2>/dev/null; then gruen "  ✓ Syntax: $(basename "$f")"
    else rot "  ✗ Syntaxfehler: $(basename "$f")"; E_FEHLER=1; fi
done

# a) Die Maschine, auf der dieser Test laeuft, muss die Pruefung bestehen —
#    sonst behauptet das Kit Lauffaehigkeit, die es gerade widerlegt.
E_LOG="$ZIEL/.einrichten.log"
E_EXIT=0
bash "$KIT/bash/kit-einrichten.sh" --nur-pruefen --nicht-interaktiv >"$E_LOG" 2>&1 || E_EXIT=$?
e_pruefe "--nur-pruefen laeuft durch (Exit 0)" "$E_EXIT" "0"
e_pruefe "und fasst nichts an (keine Verknuepfung angelegt)" \
    "$(grep -c 'uebersprungen wegen --nur-pruefen\|übersprungen wegen --nur-pruefen' "$E_LOG")" "1"
# BL-137: 'Python' statt 'python3'. kit-einrichten.sh nennt seit dieser
# Fassung den GEFUNDENEN Namen ('Python 3.13 (als python)') statt eines
# festen — die Beschriftung hier muss mitziehen, sonst prueft dieser Schritt
# auf eine Zeile, die es nicht mehr gibt, und meldet die Einrichtungsroutine
# als kaputt, obwohl sie richtig geworden ist.
for pflicht in git Python flock bash; do
    e_pruefe "Bordmittel geprueft: $pflicht" \
        "$(grep -cE "✓ $pflicht|✗ $pflicht" "$E_LOG")" "1"
done
e_pruefe "Exec-Bit wird PROBIERT, nicht vorausgesetzt" \
    "$(grep -c 'chmod +x wirkt' "$E_LOG")" "1"
e_pruefe "Dateisperre wird PROBIERT" \
    "$(grep -c 'flock) funktionieren hier\|flock greift in diesem Ordner nicht' "$E_LOG")" "1"
e_pruefe "keine Probendatei zurueckgelassen" \
    "$(find "$KIT" -maxdepth 1 -name '.einrichten-probe.*' | wc -l)" "0"

# b) Ein Zielpfad ohne Git ist ein harter Fehler — sonst laeuft der Installer
#    in genau die Bedingung, die er selbst als erstes ablehnt (A.1).
#    Das Verzeichnis muss AUSSERHALB des Wegwerf-Repos liegen: Ein Unterordner
#    von $ZIEL liegt im dortigen Arbeitsbaum, `rev-parse --is-inside-work-tree`
#    sagt dann korrekt "ja" — und der Test haette geprueft, dass eine Ablehnung
#    ausbleibt, die gar nicht ausbleiben darf. (Genau so beim ersten Lauf
#    dieses Schritts passiert.)
E_OHNE_GIT="$(mktemp -d "${TMPDIR:-/tmp}/team-kit-ohne-git.XXXXXX")"
E_EXIT=0
bash "$KIT/bash/kit-einrichten.sh" "$E_OHNE_GIT" --nur-pruefen --nicht-interaktiv >"$E_LOG" 2>&1 || E_EXIT=$?
rm -rf "$E_OHNE_GIT"
e_pruefe "Zielpfad ohne Git wird abgelehnt (Exit 1)" "$E_EXIT" "1"
e_pruefe "und der Ausweg steht dabei" "$(grep -c 'git -C .* init' "$E_LOG")" "1"

# c) Der Launcher findet das Kit ueber den Symlink — genau so liegt er nach
#    --verknuepfen unter ~/.claude/scripts/. Ohne Zielpfad muss er den
#    Installer erreichen und dessen Aufruffehler (Exit 2) durchreichen.
ln -sfn "$KIT/bash/scripts/team-init.sh" "$ZIEL/team-init-link.sh"
E_EXIT=0
bash "$ZIEL/team-init-link.sh" >"$E_LOG" 2>&1 || E_EXIT=$?
e_pruefe "Launcher erreicht den Installer ueber einen Symlink (Exit 2)" "$E_EXIT" "2"
e_pruefe "und es ist der Installer, der sich meldet" \
    "$(grep -c 'Kein Zielpfad angegeben' "$E_LOG")" "1"

# c2) Der Launcher als KOPIE — der Fall, der im Feld weh getan hat.
#     ~/.claude/scripts/team-init.sh ist das einzige Stueck des Kits, von dem
#     eine Kopie ausserhalb des Repos liegen kann. Sie wird nicht mitgezogen,
#     wenn sich im Kit etwas verschiebt: Der Umzug auf bash/ hat jede aeltere
#     Kopie stillgelegt, weil sie <kit>/install.sh suchte. Der Anwender sah
#     keinen Fehler des Kits, sondern einen Launcher, der behauptete, das Kit
#     sei nicht da.
#
#     Der Launcher kennt deshalb ALLE Ablagen, an denen ein Installer je lag.
#     Geprueft wird das an einer Kopie an einem FREMDEN Ort — der Symlink-Fall
#     oben wuerde es nicht zeigen, weil er ueber den aufgeloesten Pfad laeuft.
E_KOPIE="$(mktemp -d)"
cp "$KIT/bash/scripts/team-init.sh" "$E_KOPIE/team-init.sh"
E_EXIT=0
TEAM_KIT_PFAD="$KIT" bash "$E_KOPIE/team-init.sh" >"$E_LOG" 2>&1 || E_EXIT=$?
e_pruefe "Kopie an fremdem Ort erreicht den Installer (Exit 2)" "$E_EXIT" "2"

#     Und derselbe Launcher in der ALTEN Ablage (<kit>/scripts/ statt
#     <kit>/bash/scripts/): Eine Kopie von damals liegt eine Ebene hoeher.
E_ALT="$(mktemp -d)"
mkdir -p "$E_ALT/scripts" "$E_ALT/bash"
cp "$KIT/bash/scripts/team-init.sh" "$E_ALT/scripts/"
cp "$KIT/bash/install.sh"           "$E_ALT/bash/"
E_EXIT=0
bash "$E_ALT/scripts/team-init.sh" >"$E_LOG" 2>&1 || E_EXIT=$?
e_pruefe "Kopie in der ALTEN Ablage findet den Installer trotzdem" "$E_EXIT" "2"
rm -rf "$E_KOPIE" "$E_ALT"

# c3) Und der Installer muss eine veraltete Kopie MELDEN — bei jedem Lauf,
#     weil das der Moment ist, in dem sich die Kit-Fassung aendert. Geprueft
#     mit einem eigenen HOME, damit die Probe das echte nicht anfasst.
E_HOME="$(mktemp -d)"
mkdir -p "$E_HOME/.claude/scripts"
printf '#!/usr/bin/env bash\n# alte Kopie\nexec bash "$HOME/Source/team-kit/install.sh" "$@"\n' \
    > "$E_HOME/.claude/scripts/team-init.sh"
E_ZIEL="$(mktemp -d)/projekt"; mkdir -p "$E_ZIEL"
git -C "$E_ZIEL" init -q; git -C "$E_ZIEL" commit -q --allow-empty -m init
HOME="$E_HOME" bash "$KIT/bash/install.sh" "$E_ZIEL" --nicht-interaktiv >"$E_LOG" 2>&1 || true
e_pruefe "Installer meldet eine veraltete Launcher-Kopie" \
    "$(grep -c 'ist eine KOPIE aus einer' "$E_LOG")" "1"

#     Die Gegenprobe, ohne die die Meldung wertlos waere: Der AKTUELLE
#     Launcher darf sie NICHT ausloesen, sonst warnt der Installer immer und
#     niemand liest die Warnung noch.
cp "$KIT/bash/scripts/team-init.sh" "$E_HOME/.claude/scripts/team-init.sh"
HOME="$E_HOME" bash "$KIT/bash/install.sh" "$E_ZIEL" --update >"$E_LOG" 2>&1 || true
e_pruefe "und schweigt beim aktuellen Launcher" \
    "$(grep -c 'ist eine KOPIE aus einer' "$E_LOG")" "0"
rm -rf "$E_HOME" "$(dirname "$E_ZIEL")"

# c4) Und die Reparatur selbst: --verknuepfen muss eine Kit-Kopie ERSETZEN
#     (bis 2.10 hat es sie nur gemeldet und liegen gelassen — vorsichtig
#     gedacht, im Ergebnis wirkungslos), eine FREMDE Datei aber nicht.
#     Die zweite Haelfte ist die wichtigere: Eine Erkennung, die zu breit
#     greift, raeumt jemandem sein eigenes Skript weg.
E_HOME="$(mktemp -d)"
mkdir -p "$E_HOME/.claude/scripts"
# Eine ALTE Kit-Kopie: traegt die Kopfzeile der Kit-Datei, sonst nichts von heute.
{ echo '#!/usr/bin/env bash'
  grep -m1 '^# team-init.sh —' "$KIT/bash/scripts/team-init.sh"
  echo 'exec bash "$HOME/Source/team-kit/install.sh" "$@"'
} > "$E_HOME/.claude/scripts/team-init.sh"
# Eine FREMDE Datei unter dem Namen des Auth-Skripts.
printf '#!/bin/bash\n# mein eigenes Auth-Skript\necho hallo\n' \
    > "$E_HOME/.claude/scripts/team-auth-setup.sh"

HOME="$E_HOME" bash "$KIT/bash/kit-einrichten.sh" --verknuepfen --nicht-interaktiv \
    >"$E_LOG" 2>&1 || true
e_pruefe "--verknuepfen ersetzt die Kit-Kopie durch eine Verknuepfung" \
    "$([ -L "$E_HOME/.claude/scripts/team-init.sh" ] && echo ja || echo nein)" "ja"
e_pruefe "und legt die alte Fassung als Sicherung daneben" \
    "$([ -f "$E_HOME/.claude/scripts/team-init.sh.vor-verknuepfung" ] && echo ja || echo nein)" "ja"
e_pruefe "die FREMDE Datei bleibt unangetastet" \
    "$([ -L "$E_HOME/.claude/scripts/team-auth-setup.sh" ] && echo ja || echo nein)" "nein"
e_pruefe "und ihr Inhalt ist unveraendert" \
    "$(grep -c 'mein eigenes Auth-Skript' "$E_HOME/.claude/scripts/team-auth-setup.sh")" "1"
e_pruefe "und das wird gemeldet statt verschwiegen" \
    "$(grep -c 'stammt nicht erkennbar vom Kit' "$E_LOG")" "1"
rm -rf "$E_HOME"

# d) Der CRLF-Riegel: .gitattributes muss LF erzwingen, sonst haengt der
#    Windows-Weg wieder an der Git-Konfiguration der fremden Maschine.
e_pruefe ".gitattributes erzwingt LF" \
    "$(grep -c '^\* text=auto eol=lf' "$KIT/.gitattributes")" "1"

# e) Die Anleitung darf nicht auf Dateien zeigen, die es nur auf der
#    Autorenmaschine gibt — genau daran scheiterte der erste fremde Klon.
for datei in bash/scripts/team-auth-setup.sh bash/scripts/team-init.sh \
             doku/einrichtung.md bash/kit-einrichten.sh; do
    e_pruefe "ausgeliefert: $datei" "$([ -f "$KIT/$datei" ] && echo ja || echo nein)" "ja"
done
e_pruefe "README verweist nicht mehr auf den Pfad der Autorenmaschine" \
    "$(grep -c 'claude/scripts/team-auth-setup.sh' "$KIT/README.md")" "0"

# f) Der dritte Weg muss in der Anleitung stehen. Eine Bahn, die die Doku nicht
#    nennt, existiert fuer den Anwender nicht — und der native Weg ist genau
#    fuer die Maschinen da, auf denen der WSL-Weg ausfaellt.
e_pruefe "einrichtung.md nennt den nativen Windows-Weg" \
    "$(grep -c '^## Der kurze Weg — Windows nativ' "$KIT/doku/einrichtung.md")" "1"
e_pruefe "einrichtung.md fuehrt ihn im Belegstand" \
    "$(grep -c 'Windows nativ (PowerShell): gebaut und gefahren' "$KIT/doku/einrichtung.md")" "1"

[ "$E_FEHLER" -eq 0 ] || exit 1

kopf "11/11 — pwsh-Bahn: Gleichstand der beiden Installer"
# Die Zusicherung, auf der die ganze pwsh-Bahn ruht: install.sh und
# install.ps1 erzeugen aus DENSELBEN Antworten DASSELBE Projekt. Nicht
# "aehnlich", nicht "funktional gleichwertig" — Byte fuer Byte dasselbe.
#
# Warum das hier steht und nicht in team/tests/: Die Installer liegen nicht in
# der Installation. Dieselbe Ueberlegung wie bei BL-109.
#
# Warum ein Vergleich und keine Liste von Einzelpruefungen: Eine Liste prueft,
# woran jemand gedacht hat. Der Vergleich prueft auch, woran niemand gedacht
# hat — er faellt bei jeder Datei, die nur einer der beiden schreibt.
W_FEHLER=0
w_pruefe() {  # w_pruefe <beschreibung> <ist> <soll>
    if [ "$2" = "$3" ]; then gruen "  ✓ $1"
    else rot "  ✗ $1 — erwartet '$3', ist '$2'"; W_FEHLER=1; fi
}

# a) CRLF fuer Batch-Dateien. Ohne diese Regel verhalten sich .cmd-Dateien
#    sporadisch falsch — ein Fehlerbild, das nach einem Logikfehler aussieht.
# Seit der Bahn-Trennung haengt die Regel am PFAD: Eine .cmd kann nur unter
# pwsh/ liegen. Geprueft wird deshalb die Pfadregel — und gleich mit, dass
# git sie auf einer echten Datei auch anwendet (check-attr statt nur grep:
# eine Regel, die dasteht und nicht greift, sieht im grep bestanden aus).
w_pruefe ".gitattributes erzwingt CRLF fuer pwsh/**/*.cmd" \
    "$(grep -c '^pwsh/\*\*/\*\.cmd text eol=crlf' "$KIT/.gitattributes")" "1"
w_pruefe "und git wendet sie auf eine echte .cmd an" \
    "$(cd "$KIT" && git check-attr eol -- pwsh/entry/ralph.cmd | sed 's/.*: //')" "crlf"

# a2) BL-113 — das BOM vor PowerShell-Quelltext. Kein Schoenheitspunkt: Ohne
#     BOM liest Windows PowerShell 5.1 die Datei in der ANSI-Codepage, jeder
#     Geviertstrich endet auf U+201D, PowerShell haelt das fuer eine
#     Stringgrenze, und die Datei stirbt beim Parsen — noch bevor die
#     Versionspruefung sagen kann, dass hier pwsh 7 hingehoert.
#
#     Warum eine Pruefung und kein Kommentar: Unter pwsh 7 ist der Fehler
#     UNSICHTBAR. Die ganze pwsh-Bahn ist gegen pwsh 7 gebaut worden und
#     blieb gruen, waehrend keine einzige Datei auf der Zielmaschine startete.
OHNE_BOM=""
for f in $(cd "$KIT" && ls pwsh/*.ps1 pwsh/*.psm1 pwsh/entry/*.ps1 pwsh/scripts/*.ps1 2>/dev/null); do
    [ "$(head -c 3 "$KIT/$f" | od -An -tx1 | tr -d ' ')" = "efbbbf" ] || OHNE_BOM="$OHNE_BOM $f"
done
w_pruefe "alle .ps1/.psm1 tragen ein UTF-8-BOM" "${OHNE_BOM:-keine}" "keine"

# a3) Die Kehrseite derselben Regel. Ein BOM vor einer Shebang-Zeile macht aus
#     ihr Zeichensalat, und json.load bricht darueber ab — kosten.py hat eine so
#     verdorbene Datei stillschweigend als 0.0000 gezaehlt.
MIT_BOM=""
for f in $(cd "$KIT" && ls bash/*.sh bash/entry/*.sh bash/scripts/*.sh geteilt/*.py geteilt/tools/*.py 2>/dev/null); do
    [ "$(head -c 3 "$KIT/$f" | od -An -tx1 | tr -d ' ')" = "efbbbf" ] && MIT_BOM="$MIT_BOM $f"
done
w_pruefe "kein .sh/.py traegt ein BOM" "${MIT_BOM:-keine}" "keine"

# a4) .cmd wird vom Kommandozeileninterpreter in der OEM-Codepage gelesen
#     (850/437), nicht in 1252 und erst recht nicht in UTF-8. Dort ist reines
#     ASCII das einzige, was auf jeder Maschine dasselbe bedeutet.
NICHT_ASCII=""
for f in $(cd "$KIT" && ls pwsh/entry/*.cmd 2>/dev/null); do
    tr -d '\r' < "$KIT/$f" | LC_ALL=C grep -q '[^ -~	]' && NICHT_ASCII="$NICHT_ASCII $f"
done
w_pruefe "alle .cmd sind reines ASCII" "${NICHT_ASCII:-keine}" "keine"

# b) Ausgeliefert werden muss der ganze Bootstrap, nicht die Haelfte.
for datei in pwsh/install.ps1 pwsh/kit-einrichten.ps1 pwsh/kit-test.ps1 \
             pwsh/entry/team.config.ps1 pwsh/scripts/team-auth-setup.ps1 \
             pwsh/scripts/team-init.ps1 pwsh/pruefe-windows.ps1 \
             pwsh/lib.psm1 pwsh/redteam.ps1; do
    w_pruefe "ausgeliefert: $datei" "$([ -f "$KIT/$datei" ] && echo ja || echo nein)" "ja"
done

if ! command -v pwsh >/dev/null 2>&1; then
    # KEIN Fehler, aber auch kein Schweigen: Der Gleichstand ist auf dieser
    # Maschine UNGEPRUEFT, und das gehoert in die Ausgabe. Ein uebersprungener
    # Nachweis, den niemand sieht, liest sich am Ende wie ein bestandener.
    gelb "  ! pwsh fehlt — der Gleichstand der Installer ist hier UNGEPRUEFT."
    echo  "      Das ist die halbe Zusicherung der pwsh-Bahn. Nachholen auf"
    echo  "      einer Maschine mit PowerShell 7:  bash bash/kit-test.sh"
else
    gruen "  ✓ pwsh $(pwsh -NoProfile -Command '$PSVersionTable.PSVersion.ToString()' 2>/dev/null)"
    # c) Syntax aller PowerShell-Dateien — das Gegenstueck zu `bash -n`.
    W_SYNTAX="$(pwsh -NoProfile -Command "
        \$schlecht = @()
        foreach (\$f in (Get-ChildItem -Path '$KIT' -Filter *.ps1 -Recurse -File)) {
            \$e = \$null
            [System.Management.Automation.Language.Parser]::ParseFile(\$f.FullName, [ref]\$null, [ref]\$e) | Out-Null
            if (\$e) { \$schlecht += \$f.Name }
        }
        \$schlecht -join ' '" 2>&1)"
    w_pruefe "Syntax aller *.ps1" "${W_SYNTAX:-sauber}" "sauber"

    # d) Der Gleichstand selbst.
    W_A="$(mktemp -d "${TMPDIR:-/tmp}/team-kit-gleich-a-XXXXXX")"
    W_B="$(mktemp -d "${TMPDIR:-/tmp}/team-kit-gleich-b-XXXXXX")"
    # Gleicher Basename in beiden Baeumen: Der Projektname leitet sich aus dem
    # Ordner ab und wuerde sonst als Unterschied durchschlagen, der keiner ist.
    mkdir -p "$W_A/projekt" "$W_B/projekt"
    for d in "$W_A/projekt" "$W_B/projekt"; do
        git -C "$d" init -q .
        git -C "$d" config user.email t@l
        git -C "$d" config user.name T
    done
    bash "$KIT/bash/install.sh" "$W_A/projekt" --nicht-interaktiv >/dev/null 2>&1 || true
    pwsh -NoProfile -File "$KIT/pwsh/install.ps1" "$W_B/projekt" -NichtInteraktiv >/dev/null 2>&1 || true
    # __pycache__ ist ein Artefakt der Testlaeufe beider Installer, kein Erzeugnis.
    find "$W_A/projekt" "$W_B/projekt" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
    W_DIFF="$(diff -r --exclude=.git "$W_A/projekt" "$W_B/projekt" 2>&1 | head -20)"
    w_pruefe "install.sh und install.ps1 erzeugen denselben Baum" "${W_DIFF:-identisch}" "identisch"
    w_pruefe "beide schreiben team.config.sh UND team.config.ps1" \
        "$([ -f "$W_B/projekt/team.config.sh" ] && [ -f "$W_A/projekt/team.config.ps1" ] && echo ja || echo nein)" "ja"
    rm -rf "$W_A" "$W_B"
fi

[ "$W_FEHLER" -eq 0 ] || exit 1

gruen "
✓ Kit-Selbstverifikation grün."

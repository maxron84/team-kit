#!/usr/bin/env bash
# kit-test.sh — Selbstverifikation des Kits (BL-6).
#
# Aufruf:  ./kit-test.sh [--behalten] [weitere pytest-Argumente]
#
#   --behalten   Das Wegwerf-Repo nach dem Lauf NICHT löschen (Fehlersuche).
#
# WARUM ES DIESES SKRIPT GIBT
#
# Die Regressionstests unter team/tests/ (Stand 2.9.0: 362 Fälle in 54 Dateien)
# setzen die INSTALLIERTE Ablage voraus: Entrypoints in der Repo-Wurzel,
# CLAUDE.md und team.config.sh mit gefüllten Platzhaltern. Im Kit-Repo liegen
# sie unter entry/ und bootstrap/ — `pytest team/tests` schlägt hier deshalb
# fehl (Stand 2.6.0: 21 Fehler, 240 grün, 19 übersprungen), ohne dass
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
# Das Zielrepo ist ein frisches mktemp-Verzeichnis — ein Wegwerf-Repo im Sinne
# der README-Regel "Guard-Tests nie im echten Projekt". Es wird am Ende
# gelöscht (außer bei --behalten). Dieses Skript ruft KEINE Agenten-CLI auf und
# kostet daher nichts.
set -euo pipefail
cd "$(dirname "$0")"
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

if ! command -v pytest >/dev/null 2>&1; then
    rot "pytest nicht gefunden — die Selbstverifikation braucht es."
    echo "  Installation: pip install --user pytest" >&2
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

kopf "1/8 — Wegwerf-Repo anlegen"
git -C "$ZIEL" init -q
# Lokale Identität, damit der Lauf auch ohne globale Git-Config committen kann.
git -C "$ZIEL" config user.email "kit-test@localhost"
git -C "$ZIEL" config user.name  "Kit-Selbsttest"
gruen "  ✓ $ZIEL"

kopf "2/8 — Kit installieren (nicht-interaktiv)"
# Ohne TEAM_INIT_*-Vorgaben: genau die Defaults, die ein Anwender bekäme.
if ! bash "$KIT/install.sh" "$ZIEL" --nicht-interaktiv > "$ZIEL/.install.log" 2>&1; then
    rot "  ✗ install.sh schlug fehl:"
    tail -20 "$ZIEL/.install.log" >&2
    exit 1
fi
gruen "  ✓ $(grep -oE 'Fertig — [0-9]+ Dateien geschrieben' "$ZIEL/.install.log" | head -1)"

kopf "3/8 — Ungefüllte Platzhalter suchen"
# Ein übrig gebliebenes {{...}} heißt: Der Installer kennt die Datei nicht oder
# der Platzhalter wurde umbenannt. Beides fällt sonst erst im Feld auf, wo die
# Briefings die Pfade des Ursprungsprojekts nennen würden — falsche Guard-Grenze.
RESTE="$(grep -rlE '\{\{[A-Z_]+\}\}' "$ZIEL" \
           --exclude-dir=.git --exclude=.install.log 2>/dev/null || true)"
if [ -n "$RESTE" ]; then
    rot "  ✗ Ungefüllte Platzhalter in:"
    echo "$RESTE" | sed 's|^|      |' >&2
    exit 1
fi
gruen "  ✓ keine"

kopf "4/8 — Regressionstests in der Installation (Auslieferungswerte)"
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
kopf "5/8 — Regressionstests unter angepasster team.config.sh (BL-58)"
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
kopf "6/8 — Update-Pfad schuetzt Projektdaten"
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

if ! bash "$KIT/install.sh" "$ZIEL" --update > "$ZIEL/.update.log" 2>&1; then
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
ABGLEICH_BEFEHL="$(grep -oE 'diff -u "[^"]+" "[^"]+"' "$ZIEL/.update.log" | head -1)"
pruefe "Abgleich-Hinweis nennt einen diff-Befehl" \
       "$([ -n "$ABGLEICH_BEFEHL" ] && echo ja || echo nein)" "ja"
# Die genannte gerenderte Vorlage muss existieren UND gefuellt sein — ein Pfad
# auf eine geloeschte Datei waere derselbe Fehler in gruen.
ABGLEICH_QUELLE="$(printf '%s' "$ABGLEICH_BEFEHL" | sed -E 's/^diff -u "([^"]+)".*/\1/')"
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
[ "$UPDATE_FEHLER" -eq 0 ] || exit 1

# BL-51/BL-52: Die beiden Bestandsprojekt-Befunde. Der Installer ist die einzige
# Stelle, an der sie auffallen koennen — in der Installation liegt er nicht mehr,
# also gehoert der Nachweis hierher und nicht in team/tests/.
kopf "7/8 — Einzug in eine gewachsene Codebasis (BL-51, BL-52)"
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
if ! TEAM_INIT_WEITERER_CODE="tests/" bash "$KIT/install.sh" "$BESTAND_REPO" --nicht-interaktiv \
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
if ! bash "$KIT/install.sh" "$BESTAND_REPO" --update \
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

kopf "8/8 — Regel-Inventar gegen die Regeldatei (A.10, BL-56)"
# Der Sicherheitsgurt vor dem Umbau der Regeldatei: Jedes NORM-Zitat muss
# woertlich in bootstrap/CLAUDE.md.vorlage stehen, jeder Abschnitt im Inventar
# vertreten sein. Prueft die VORLAGE, nicht die Installation — ein Feldprojekt
# darf seine CLAUDE.md umformulieren (so haelt es test_bl55 ausdruecklich
# fest), die Vorlage darf es nicht unbemerkt.
if ! python3 "$KIT/kit-regelinventar.py"; then
    rot "  ✗ Regel-Inventar und Regeldatei stehen auseinander."
    exit 1
fi

gruen "
✓ Kit-Selbstverifikation grün."

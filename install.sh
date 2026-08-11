#!/usr/bin/env bash
# install.sh — installiert das T.E.A.M. in ein Zielprojekt.
#
# Aufruf:  bash install.sh <zielpfad> [--nicht-interaktiv] [--force|--update]
#
#   --nicht-interaktiv  Keine Rückfragen; Werte aus den TEAM_INIT_*-Umgebungs-
#                       variablen oder den Defaults. Für Skripte und Tests.
#   --update            Nur die Team-INFRASTRUKTUR aktualisieren (Entrypoints
#                       ausser team.config.sh, team/lib.sh, team/redteam.sh,
#                       team/tools/, team/prompts/, team/tests/). Rührt KEINE
#                       Projektdaten an. Der richtige Weg, um ein bestehendes
#                       Projekt auf eine neue Kit-Version zu heben.
#   --force             Vorhandene Dateien überschreiben (Standard: überspringen).
#
#   ⚠  --force ist NUR für eine kaputte Erstinstallation gedacht, NIE für ein
#      gelebtes Projekt: Es überschreibt auch .budget-ledger (Kostenhistorie
#      weg), .ralph-state (Kaskadenstand zurück auf 1), das Beutebuch (alle
#      Funde weg), CHANGELOG.md, plans/*.md und team.config.sh (Smoke-Test
#      weg). Empirisch nachgestellt, siehe BL-8. Für Updates: --update.
#
# Umgebungsvariablen für den nicht-interaktiven Betrieb:
#   TEAM_INIT_PROJEKT TEAM_INIT_PRODUKTIVCODE TEAM_INIT_TEST_ORDNER
#   TEAM_INIT_PLAN_ORDNER TEAM_INIT_SMOKE_TEST TEAM_INIT_TECH_STACK
#
# Der Installer ist idempotent: ein zweiter Lauf überschreibt nichts, sondern
# meldet, was bereits vorhanden ist.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZIEL=""
INTERAKTIV=1
FORCE=0
UPDATE=0

for arg in "$@"; do
    case "$arg" in
        --nicht-interaktiv) INTERAKTIV=0 ;;
        --force)            FORCE=1 ;;
        --update)           UPDATE=1 ;;
        -*) echo "Unbekannte Option: $arg" >&2; exit 2 ;;
        *)  ZIEL="$arg" ;;
    esac
done

rot()  { printf '\033[31m%s\033[0m\n' "$*"; }
gruen(){ printf '\033[32m%s\033[0m\n' "$*"; }
gelb() { printf '\033[33m%s\033[0m\n' "$*"; }
kopf() { printf '\n\033[1m%s\033[0m\n' "$*"; }

[ -n "$ZIEL" ] || { rot "FEHLER: Kein Zielpfad angegeben."; echo "Aufruf: bash install.sh <zielpfad>"; exit 2; }
ZIEL="$(cd "$ZIEL" 2>/dev/null && pwd)" || { rot "FEHLER: Zielpfad existiert nicht: $ZIEL"; exit 2; }

if [ "$UPDATE" -eq 1 ] && [ "$FORCE" -eq 1 ]; then
    rot "FEHLER: --update und --force schliessen sich aus."
    echo "  --update hebt ein gelebtes Projekt sicher auf eine neue Kit-Version."
    echo "  --force ueberschreibt ALLES, auch Ledger, State und Beutebuch."
    exit 2
fi

# ---------------------------------------------------------------- Update-Pfad
# BL-8: Bis hierher gab es fuer ein bestehendes Projekt keinen sicheren Weg auf
# eine neue Kit-Version. Ohne Flag ueberspringt der Installer jede vorhandene
# Datei (aendert also nichts), mit --force ueberschreibt er auch die
# PROJEKTDATEN — empirisch nachgestellt: .budget-ledger geleert, .ralph-state
# auf 1 zurueck, Beutebuch-Funde weg, TEAM_SMOKE_TEST aus team.config.sh
# verschwunden. Beides unbrauchbar. --update fasst ausschliesslich die
# Infrastruktur an.
if [ "$UPDATE" -eq 1 ]; then
    kopf "Update — nur Team-Infrastruktur"
    if [ ! -f "$ZIEL/team.config.sh" ]; then
        rot "FEHLER: $ZIEL sieht nicht nach einer T.E.A.M.-Installation aus"
        echo "  (team.config.sh fehlt). Fuer eine Erstinstallation ohne --update aufrufen."
        exit 2
    fi

    # BL-10: NIEMALS in einen laufenden Lauf hinein aktualisieren. Real
    # passiert (2026-08-01, team-kit_project_platformer): Ein Update waehrend
    # eines aktiven vollautomatik.sh-Laufs legte frische, uncommittete Dateien
    # in team/ ab. Der naechste Read-Only-Lauf (Axel, Whitelist nur plans/)
    # wertete sie als GUARD-VERLETZUNG, rollte sie chirurgisch zurueck und
    # buchte seine Runde als Fehlschlag — obwohl er seine Ermittlungsakte
    # geliefert hatte. Das war die dritte Stagnation in Folge und stoppte den
    # Lauf. Der Guard hat richtig gehandelt; fehlen durfte nur diese Sperre.
    if [ -e "$ZIEL/.team-loop.lock" ] && \
       ! flock -n "$ZIEL/.team-loop.lock" true 2>/dev/null; then
        rot "FEHLER: In $ZIEL laeuft gerade ein Team-Lauf (.team-loop.lock ist gehalten)."
        echo "  Ein Update wuerde uncommittete Dateien in team/ ablegen. Der naechste"
        echo "  Read-Only-Lauf (Harry/Marv/Axel) wertet die als Guard-Verletzung,"
        echo "  raeumt sie weg und bucht seine Runde als Fehlschlag — im Feld hat das"
        echo "  einen laufenden Lauf gestoppt (BL-10)."
        echo "  Erst den Lauf beenden lassen, dann erneut aufrufen."
        exit 2
    fi

    # Ein schmutziger Arbeitsbaum ist kein Abbruchgrund, aber die Warnung
    # gehoert VOR das Update: Nach dem Update ist nicht mehr unterscheidbar,
    # was von wem stammt.
    if [ -n "$(git -C "$ZIEL" status --porcelain 2>/dev/null)" ]; then
        gelb "  ! Der Arbeitsbaum ist nicht sauber. Das Update mischt seine Dateien"
        gelb "    unter deine. Empfehlung: abbrechen (Strg+C), erst committen."
        gelb "    Weiter in 5 s …"
        sleep 5
    fi

    # Projektwerte aus der INSTALLIERTEN Konfiguration lesen, nicht aus den
    # Defaults — sonst bekaemen die Rollen-Briefings die falschen Pfade und
    # damit eine falsche Guard-Grenze.
    # shellcheck disable=SC1091
    . "$ZIEL/team.config.sh"
    PROJEKT="${TEAM_PROJEKT:-$(basename "$ZIEL")}"
    PRODUKTIVCODE="${TEAM_PRODUKTIVCODE:-src/}"
    TEST_ORDNER="${TEAM_TEST_ORDNER:-tests/}"
    PLAN_ORDNER="${TEAM_PLAN_ORDNER:-plans/}"
    SMOKE_TEST="${TEAM_SMOKE_TEST:-}"
    DOMAENEN="${TEAM_DOMAENEN:-produkt}"
    # TECH_STACK/DEPLOY stehen NUR in CLAUDE.md, nicht in team.config.sh — sie
    # sind von hier aus nicht rekonstruierbar. Dieselben Vorgaben wie bei der
    # Erstinstallation, damit der Abgleich unten bei einer unveraenderten
    # CLAUDE.md "deckungsgleich" meldet und nur echte Anpassungen anzeigt.
    TECH_STACK="TODO: in CLAUDE.md nachtragen"
    DEPLOY="TODO: in CLAUDE.md nachtragen"
    DEPLOY_AUSNAHMEN="keine"
    gruen "  ✓ Projektwerte aus team.config.sh gelesen (Projekt: $PROJEKT)"

    # Der Commit-Entscheid steht NUR im Architekten-Briefing, nicht in der
    # Config. Aus der bestehenden Datei retten, statt ihn stillschweigend auf
    # den Default zurueckzusetzen.
    ARCHITEKT_ALT="$ZIEL/team/prompts/rolle-architekt.md"
    COMMIT_ENTSCHEID=""
    if [ -f "$ARCHITEKT_ALT" ]; then
        COMMIT_ENTSCHEID="$(sed -n 's/^\*\*Committen:\*\* //p' "$ARCHITEKT_ALT" | head -1)"
    fi
    if [ -n "$COMMIT_ENTSCHEID" ]; then
        gruen "  ✓ Commit-Entscheid aus dem bisherigen Briefing uebernommen"
    else
        COMMIT_ENTSCHEID="Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Strippenzieher führt sie aus."
        gelb "  ! Commit-Entscheid nicht lesbar — Default (nicht selbst committen) gesetzt."
    fi

    FORCE=1   # innerhalb der Infrastruktur bewusst ueberschreiben
    GESCHRIEBEN=0; UEBERSPRUNGEN=0
    ABWEICHEND=""
    kopiere() {
        local quelle="$1" rel="$2" modus="${3:-644}" ziel="$ZIEL/$2"
        mkdir -p "$(dirname "$ziel")"
        # BL-12: Wich die installierte Fassung vom Kit ab, kann darin ein
        # LOKALER Fix stecken, den noch niemand ans Kit zurueckgemeldet hat.
        # Genau so ging im Feld ein 12-USD-Fix an beutebuch.py verloren.
        # Briefings sind ausgenommen: Sie werden ohnehin neu gerendert und
        # weichen durch die gefuellten Platzhalter immer ab.
        case "$rel" in
            team/prompts/*) ;;
            *) [ -e "$ziel" ] && ! cmp -s "$quelle" "$ziel" \
                   && ABWEICHEND="$ABWEICHEND $rel" ;;
        esac
        cp "$quelle" "$ziel"; chmod "$modus" "$ziel"
        GESCHRIEBEN=$((GESCHRIEBEN + 1))
    }
    fuelle_abs() {
        local datei="$1"
        [ -f "$datei" ] || return 0
        python3 - "$datei" "$PROJEKT" "$PRODUKTIVCODE" "$TEST_ORDNER" "$PLAN_ORDNER" \
                           "$SMOKE_TEST" "$TECH_STACK" "$DEPLOY" "$DEPLOY_AUSNAHMEN" \
                           "$DOMAENEN" "$COMMIT_ENTSCHEID" <<'PY'
import sys, pathlib
(d, projekt, prod, test, plan, smoke, stack, deploy, ausn,
 domaenen, commit) = sys.argv[1:12]
p = pathlib.Path(d); t = p.read_text(encoding="utf-8")
for a, b in [("{{PROJEKTNAME}}", projekt), ("{{PRODUKTIVCODE}}", prod),
             ("{{TEST_ORDNER}}", test), ("{{PLAN_ORDNER}}", plan.rstrip("/")),
             ("{{BEUTEBUCH}}", plan.rstrip("/") + "/beutebuch.md"),
             ("{{CHANGELOG}}", "CHANGELOG.md"),
             ("{{FIX_PRAEFIX}}", "fix(uat)"), ("{{FEAT_PRAEFIX}}", "feat"),
             ("{{SMOKE_TEST}}", smoke or "TODO: noch keiner — Stufe 1 der ersten Kaskade"),
             ("{{TECH_STACK}}", stack), ("{{DEPLOY}}", deploy),
             ("{{DEPLOY_AUSNAHMEN}}", ausn), ("{{DOMAENEN}}", domaenen),
             ("{{COMMIT_ENTSCHEID}}", commit)]:
    t = t.replace(a, b)
p.write_text(t, encoding="utf-8")
PY
    }
    fuelle() { fuelle_abs "$ZIEL/$1"; }

    # Entrypoints — team.config.sh ist AUSGENOMMEN: sie traegt die
    # Projektwerte (Smoke-Test!) und ist damit Projektdatum, nicht Infrastruktur.
    for f in "$KIT"/entry/*.sh; do
        [ "$(basename "$f")" = "team.config.sh" ] && continue
        kopiere "$f" "$(basename "$f")" 755
    done
    kopiere "$KIT/team/lib.sh"     "team/lib.sh"     755
    kopiere "$KIT/team/redteam.sh" "team/redteam.sh" 755
    for f in "$KIT"/team/tools/*.py;   do kopiere "$f" "team/tools/$(basename "$f")" 755; done
    for f in "$KIT"/team/prompts/*.md; do kopiere "$f" "team/prompts/$(basename "$f")"; done
    # BL-12: Hier stand einmal ein pauschales rm auf team/tests/test_*.py, um
    # umbenannte Kit-Tests einer Altversion loszuwerden. Das hat im Feld einen
    # projekteigenen Infrastruktur-Test geloescht — team/tests/ ist eben NICHT
    # exklusiv Kit-Gebiet, sobald ein Projekt eine Luecke im Team selbst
    # schliesst. Jetzt wird nichts geloescht; Unbekanntes wird gemeldet.
    for f in "$KIT"/team/tests/test_*.py; do kopiere "$f" "team/tests/$(basename "$f")"; done
    FREMDE_TESTS=""
    for f in "$ZIEL"/team/tests/test_*.py; do
        [ -e "$f" ] || continue
        [ -e "$KIT/team/tests/$(basename "$f")" ] || \
            FREMDE_TESTS="$FREMDE_TESTS $(basename "$f")"
    done
    for d in "$ZIEL"/team/prompts/*.md; do fuelle "team/prompts/$(basename "$d")"; done
    gruen "  ✓ $GESCHRIEBEN Infrastruktur-Dateien aktualisiert"

    if [ -n "$ABWEICHEND" ]; then
        kopf "Ersetzt, obwohl abweichend — bitte gegenlesen"
        for f in $ABWEICHEND; do echo "  ! $f"; done
        gelb "  Diese Dateien wichen von der Kit-Fassung ab. Meist ist das nur"
        gelb "  eine aeltere Version — es kann aber ein LOKALER Fix sein, den"
        gelb "  niemand ans Kit zurueckgemeldet hat. Im Feld ging so ein Fix"
        gelb "  ueber 12,00 USD verloren (BL-12)."
        gelb "  Pruefen mit:  git -C $ZIEL diff -- $ABWEICHEND"
        gelb "  Steckt dort etwas Eigenes drin: ins Kit zurueckspielen, DANN erneut updaten."
    fi
    if [ -n "$FREMDE_TESTS" ]; then
        kopf "Unbekannte Tests in team/tests (unangetastet gelassen)"
        for f in $FREMDE_TESTS; do echo "  · $f"; done
        echo "  Kennt das Kit nicht — entweder vom Projekt ergaenzt (dann ans Kit"
        echo "  melden) oder Rest einer Altversion (dann loeschen)."
    fi

    kopf "Unangetastet geblieben (Projektdaten)"
    for d in team.config.sh CLAUDE.md CHANGELOG.md .budget-ledger .ralph-state \
             .gitignore "${PLAN_ORDNER}"; do
        [ -e "$ZIEL/$d" ] && echo "  · $d"
    done

    # Doku-Dateien tragen Projektanpassungen (gefuellte TODOs, eigene
    # Abschnitte) und werden deshalb NICHT ueberschrieben. Der Mensch muss
    # aber erfahren, dass sich die Kit-Fassung geaendert hat — sonst laufen
    # die REGELN im Projekt der Mechanik hinterher (genau die Haelfte des
    # BL-4-Fehlers).
    # Verglichen wird die MIT DENSELBEN WERTEN gerenderte Kit-Vorlage gegen
    # die installierte Datei — sonst meldet der Abgleich immer eine Abweichung
    # (gefuellte gegen ungefuellte Platzhalter) und wird zur Warnung, die man
    # wegklickt.
    kopf "Bitte von Hand abgleichen"
    ABGLEICH=0
    for paar in "bootstrap/TEAM.md:TEAM.md" "bootstrap/CLAUDE.md.vorlage:CLAUDE.md"; do
        quelle="$KIT/${paar%%:*}"; ziel="$ZIEL/${paar##*:}"
        [ -f "$ziel" ] || continue
        gerendert="$(mktemp)"
        cp "$quelle" "$gerendert"
        fuelle_abs "$gerendert"
        if ! diff -q "$gerendert" "$ziel" >/dev/null 2>&1; then
            echo "  ! ${paar##*:} weicht von der Kit-Fassung ab"
            echo "      diff <(…) $ZIEL/${paar##*:}  —  Kit-Vorlage: $KIT/${paar%%:*}"
            ABGLEICH=$((ABGLEICH + 1))
        fi
        rm -f "$gerendert"
    done
    if [ "$ABGLEICH" -eq 0 ]; then
        gruen "  ✓ nichts offen"
    else
        gelb "  Bei CLAUDE.md ist eine Abweichung normal (Projektanpassungen,"
        gelb "  gefuellte TODOs). Entscheidend ist, ob dir REGELN aus der neuen"
        gelb "  Kit-Fassung fehlen — die Mechanik ist aktualisiert, die Regeln"
        gelb "  im Projekt sind es nicht (das war die Haelfte von BL-4)."
    fi

    kopf "Selbsttest"
    FEHLER=0
    for f in "$ZIEL"/*.sh; do
        bash -n "$f" || { rot "  ✗ Syntaxfehler: $(basename "$f")"; FEHLER=1; }
    done
    [ "$FEHLER" -eq 0 ] && gruen "  ✓ Alle Shell-Skripte syntaktisch korrekt"
    # Der Selbsttest muss laufen wie ./team-test.sh beim Anwender: OHNE die
    # TEAM_*-Variablen, die dieses Skript beim Sourcen der Config geerbt hat.
    # Sonst gilt z. B. TEAM_DOMAENEN des Projekts auch fuer die Fixtures, und
    # jeder Test mit domaene="team" scheitert an einem Projekt, das diese
    # Domaene gar nicht fuehrt — ein Fehlalarm, der nur im Update auftraete.
    if command -v pytest >/dev/null 2>&1; then
        if (cd "$ZIEL" && unset "${!TEAM_@}" && pytest -q team/tests >/tmp/team-update-pytest.log 2>&1); then
            gruen "  ✓ Regressionstests grün ($(grep -oE '[0-9]+ passed' /tmp/team-update-pytest.log | head -1))"
        else
            rot "  ✗ Regressionstests NICHT grün — Log: /tmp/team-update-pytest.log"
            tail -3 /tmp/team-update-pytest.log
            FEHLER=1
        fi
    fi

    kopf "Update fertig"
    rot  "  JETZT COMMITTEN — vor dem naechsten Lauf, nicht danach."
    echo "    git -C $ZIEL add -A && git -C $ZIEL commit -m \"chore: T.E.A.M. aktualisiert\""
    echo
    echo "  Warum das keine Formalie ist: Die neuen Dateien liegen uncommittet in"
    echo "  team/. Der naechste Read-Only-Lauf (Harry/Marv/Axel) sieht sie ausserhalb"
    echo "  seiner Whitelist, wertet sie als Guard-Verletzung und raeumt sie weg —"
    echo "  das Update waere still wieder verschwunden (BL-10)."
    exit $FEHLER
fi

# ---------------------------------------------------------------- A.1 Vorbedingungen
kopf "A.1 — Vorbedingungen"
if ! git -C "$ZIEL" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    rot "FEHLER: $ZIEL ist kein Git-Repository."
    echo "  Die Rollen committen, rollen zurück und prüfen Commit-Bereiche —"
    echo "  ohne Git funktioniert davon nichts. Zuerst: git -C \"$ZIEL\" init"
    exit 2
fi
gruen "  ✓ Git-Repository"

if command -v claude >/dev/null 2>&1; then
    gruen "  ✓ Claude-CLI: $(claude --version 2>/dev/null | head -1)"
else
    gelb "  ! Claude-CLI nicht gefunden — die Dateien werden trotzdem installiert,"
    gelb "    aber kein Loop kann laufen, bis 'claude' im PATH ist."
fi

if [ -f "$HOME/.config/claude-team/api-key" ] || [ -f "$HOME/.config/claude-team/auth-mode" ]; then
    gruen "  ✓ Auth-Konfiguration unter ~/.config/claude-team/"
else
    gelb "  ! Keine Auth-Konfiguration gefunden. Vor dem ersten Lauf:"
    gelb "    bash ~/.claude/scripts/team-auth-setup.sh"
fi

BESTEHENDER_LOOP=""
for f in ralph.sh team-lib.sh vollautomatik.sh; do
    [ -e "$ZIEL/$f" ] && BESTEHENDER_LOOP="$BESTEHENDER_LOOP $f"
done
if [ -n "$BESTEHENDER_LOOP" ] && [ "$FORCE" -eq 0 ]; then
    gelb "  ! Vorhandene Team-Dateien:$BESTEHENDER_LOOP"
    gelb "    Sie bleiben unangetastet (--force überschreibt)."
fi

# ---------------------------------------------------------------- Aufnahme-Interview
frage() {  # frage <variable> <text> <default>
    local var="$1" text="$2" vorgabe="$3" eingabe=""
    local env_name="TEAM_INIT_${var}"
    if [ -n "${!env_name:-}" ]; then printf -v "$var" '%s' "${!env_name}"; return; fi
    if [ "$INTERAKTIV" -eq 0 ]; then printf -v "$var" '%s' "$vorgabe"; return; fi
    if [ -n "$vorgabe" ]; then read -r -p "  $text [$vorgabe]: " eingabe || true
    else                     read -r -p "  $text: " eingabe || true; fi
    printf -v "$var" '%s' "${eingabe:-$vorgabe}"
}

kopf "Aufnahme-Interview — acht Werte, alles Weitere per Feld-Default"
frage PROJEKT        "Projektname"                    "$(basename "$ZIEL")"
frage PRODUKTIVCODE  "Produktivcode-Ordner (tabu für Red Team)" "src/"
frage TEST_ORDNER    "Test-Ordner"                    "tests/"
frage PLAN_ORDNER    "Plan-Ordner"                    "plans/"
if [ "$INTERAKTIV" -eq 1 ]; then
    echo "  Smoke-Test: der EINE Befehl, mit dem eine Rolle prüft, ob das Projekt heil ist."
    echo "  Leer lassen, wenn es ihn noch nicht gibt — dann ist er Stufe 1 der ersten Kaskade."
fi
frage SMOKE_TEST     "Smoke-Test-Befehl"              ""
frage TECH_STACK     "Tech-Stack (eine Zeile)"        "TODO: in CLAUDE.md nachtragen"
if [ "$INTERAKTIV" -eq 1 ]; then
    echo "  Domänen trennen im Kostenledger verschiedene Arbeitsstränge."
    echo "  Default ist EINE Domäne: In einem Feldprojekt ist alles Produktarbeit."
    echo "  Arbeit am T.E.A.M. selbst gehört ins Kit-Repo, nicht hierher — dafür"
    echo "  braucht es keine zweite Domäne (siehe BL-9). Mehrere nur angeben, wenn"
    echo "  DIESES Projekt fachlich getrennte Stränge hat, z. B. \"backend frontend\"."
fi
frage DOMAENEN       "Domänen (Leerliste)"            "produkt"
if [ "$INTERAKTIV" -eq 1 ]; then
    echo "  Darf der Architekt selbst committen, oder liefert er dir die Befehle?"
fi
frage COMMIT_MODUS   "Architekt committet selbst? (j/n)" "n"

PRODUKTIVCODE="${PRODUKTIVCODE%/}/"
TEST_ORDNER="${TEST_ORDNER%/}/"
PLAN_ORDNER="${PLAN_ORDNER%/}/"
DEPLOY="TODO: in CLAUDE.md nachtragen"
DEPLOY_AUSNAHMEN="keine"
case "${COMMIT_MODUS,,}" in
    j|ja|y|yes) COMMIT_ENTSCHEID="Ich committe Plan-/Doku-Änderungen selbst (docs(plan): …)." ;;
    *)          COMMIT_ENTSCHEID="Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Strippenzieher führt sie aus." ;;
esac

# ---------------------------------------------------------------- Kopieren
kopf "A.2 — Dateien installieren"
GESCHRIEBEN=0; UEBERSPRUNGEN=0

kopiere() {  # kopiere <quelle> <ziel-relativ> [modus]
    local quelle="$1" rel="$2" modus="${3:-644}" ziel="$ZIEL/$2"
    mkdir -p "$(dirname "$ziel")"
    if [ -e "$ziel" ] && [ "$FORCE" -eq 0 ]; then
        UEBERSPRUNGEN=$((UEBERSPRUNGEN + 1)); return
    fi
    cp "$quelle" "$ziel"; chmod "$modus" "$ziel"
    GESCHRIEBEN=$((GESCHRIEBEN + 1))
}

schreibe() {  # schreibe <ziel-relativ> <inhalt>
    local ziel="$ZIEL/$1"
    mkdir -p "$(dirname "$ziel")"
    if [ -e "$ziel" ] && [ "$FORCE" -eq 0 ]; then
        UEBERSPRUNGEN=$((UEBERSPRUNGEN + 1)); return
    fi
    printf '%s' "$2" > "$ziel"
    GESCHRIEBEN=$((GESCHRIEBEN + 1))
}

# Platzhalter in einer Datei ersetzen
fuelle() {
    local datei="$ZIEL/$1"
    [ -f "$datei" ] || return 0
    python3 - "$datei" "$PROJEKT" "$PRODUKTIVCODE" "$TEST_ORDNER" "$PLAN_ORDNER" \
                       "$SMOKE_TEST" "$TECH_STACK" "$DEPLOY" "$DEPLOY_AUSNAHMEN" \
                       "$DOMAENEN" "$COMMIT_ENTSCHEID" <<'PY'
import sys, pathlib
(d, projekt, prod, test, plan, smoke, stack, deploy, ausn,
 domaenen, commit) = sys.argv[1:12]
p = pathlib.Path(d); t = p.read_text(encoding="utf-8")
for a, b in [("{{PROJEKTNAME}}", projekt), ("{{PRODUKTIVCODE}}", prod),
             ("{{TEST_ORDNER}}", test), ("{{PLAN_ORDNER}}", plan.rstrip("/")),
             ("{{BEUTEBUCH}}", plan.rstrip("/") + "/beutebuch.md"),
             ("{{CHANGELOG}}", "CHANGELOG.md"),
             ("{{FIX_PRAEFIX}}", "fix(uat)"), ("{{FEAT_PRAEFIX}}", "feat"),
             ("{{SMOKE_TEST}}", smoke or "TODO: noch keiner — Stufe 1 der ersten Kaskade"),
             ("{{TECH_STACK}}", stack), ("{{DEPLOY}}", deploy),
             ("{{DEPLOY_AUSNAHMEN}}", ausn), ("{{DOMAENEN}}", domaenen),
             ("{{COMMIT_ENTSCHEID}}", commit)]:
    t = t.replace(a, b)
p.write_text(t, encoding="utf-8")
PY
}

# Entrypoints in die Repo-Wurzel — der Strippenzieher tippt sie direkt
# (Ablage-Konvention aus dem Feld: Einstiegspunkte sichtbar oben).
for f in "$KIT"/entry/*.sh; do
    kopiere "$f" "$(basename "$f")" 755
done
# Alles Aufgerufene in den team/-Namensraum. Damit berührt das Kit die
# Konventionen des Projekts nicht: tests/ und scripts/ bleiben dem Projekt,
# und kein stack-fremder Code landet in deinen Ordnern.
kopiere "$KIT/team/lib.sh"     "team/lib.sh"     755
kopiere "$KIT/team/redteam.sh" "team/redteam.sh" 755
for f in "$KIT"/team/tools/*.py;      do kopiere "$f" "team/tools/$(basename "$f")" 755; done
for f in "$KIT"/team/prompts/*.md;    do kopiere "$f" "team/prompts/$(basename "$f")"; done
for f in "$KIT"/team/tests/test_*.py; do kopiere "$f" "team/tests/$(basename "$f")"; done
gruen "  ✓ Entrypoints (Wurzel) + team/ (lib, tools, prompts, $(ls "$KIT"/team/tests/test_*.py | wc -l) Tests)"

# ---------------------------------------------------------------- A.0 Bootstrap
kopf "A.0 — Bootstrap-Dateien"
kopiere "$KIT/bootstrap/CLAUDE.md.vorlage"    "CLAUDE.md"
kopiere "$KIT/bootstrap/TEAM.md"               "TEAM.md"
kopiere "$KIT/bootstrap/CHANGELOG.md"          "CHANGELOG.md"
kopiere "$KIT/bootstrap/beutebuch.md"          "${PLAN_ORDNER}beutebuch.md"
kopiere "$KIT/bootstrap/roadmap-skizzen.md"    "${PLAN_ORDNER}roadmap-skizzen.md"
kopiere "$KIT/bootstrap/backlog.md"            "${PLAN_ORDNER}backlog.md"
schreibe "${PLAN_ORDNER}ermittlungsakten/.gitkeep" ""
schreibe ".budget-ledger" ""
schreibe ".ralph-state" "1
"
mkdir -p "$ZIEL/${TEST_ORDNER}"
gruen "  ✓ CLAUDE.md, CHANGELOG, Beutebuch (mit Vorlage-Block), Roadmap, Backlog, Ledger, State"

# Platzhalter füllen — auch in den Briefings: sie sind selbst Prompts und
# nennen sonst die Pfade des Ursprungsprojekts (falsche Guard-Grenze!).
for d in CLAUDE.md TEAM.md team.config.sh CHANGELOG.md \
         "${PLAN_ORDNER}roadmap-skizzen.md" "${PLAN_ORDNER}backlog.md" \
         "${PLAN_ORDNER}beutebuch.md"; do
    fuelle "$d"
done
for d in "$ZIEL"/team/prompts/*.md; do
    fuelle "team/prompts/$(basename "$d")"
done

# ---------------------------------------------------------------- .gitignore
if ! grep -q "T.E.A.M.-Loop-Laufzeitartefakte" "$ZIEL/.gitignore" 2>/dev/null; then
    cat "$KIT/bootstrap/gitignore.fragment" >> "$ZIEL/.gitignore"
    gruen "  ✓ .gitignore ergänzt"
else
    gelb "  · .gitignore enthält den Block bereits"
fi

# ---------------------------------------------------------------- Selbsttest
kopf "Selbsttest"
FEHLER=0
for f in "$ZIEL"/*.sh; do
    bash -n "$f" || { rot "  ✗ Syntaxfehler: $(basename "$f")"; FEHLER=1; }
done
[ "$FEHLER" -eq 0 ] && gruen "  ✓ Alle Shell-Skripte syntaktisch korrekt"

if python3 -m py_compile "$ZIEL"/team/tools/*.py 2>/dev/null; then
    gruen "  ✓ Python-Werkzeuge kompilieren"
else
    rot "  ✗ Python-Werkzeuge fehlerhaft"; FEHLER=1
fi

if command -v pytest >/dev/null 2>&1; then
    if (cd "$ZIEL" && pytest -q team/tests >/tmp/team-init-pytest.log 2>&1); then
        gruen "  ✓ Regressionstests grün ($(grep -oE '[0-9]+ passed' /tmp/team-init-pytest.log | head -1))"
    else
        gelb "  ! Regressionstests nicht vollständig grün — Log: /tmp/team-init-pytest.log"
        gelb "    $(tail -3 /tmp/team-init-pytest.log | head -1)"
    fi
else
    gelb "  · pytest nicht installiert — Regressionstests übersprungen"
fi

# ---------------------------------------------------------------- Abschluss
kopf "Fertig — $GESCHRIEBEN Dateien geschrieben, $UEBERSPRUNGEN übersprungen"
cat <<EOF

>>> Alles Weitere steht in $ZIEL/TEAM.md <<<
    Bedienung, Befehle, Exit-Codes und Fehlersuche — für dich, nicht für die KI.
    Diese Terminal-Ausgabe scrollt weg; TEAM.md bleibt im Git.

Nächste Schritte im Zielprojekt:

  1. Werte prüfen:      \$EDITOR $ZIEL/team.config.sh
  2. Regeln prüfen:     \$EDITOR $ZIEL/CLAUDE.md   (TODO-Stellen füllen)
  3. Alles committen:   git -C $ZIEL add -A && git -C $ZIEL commit -m "chore: T.E.A.M. eingerichtet"
     ^ WICHTIG: vor dem ersten Guard-Lauf committen. Ein Read-Only-Guard
       betrachtet uncommittete Dateien als Verletzung und räumt sie weg.
  4. Team-Tests:        cd $ZIEL && ./team-test.sh
     (pytest, prüft NUR die Team-Infrastruktur — dein Projekt-Testbefehl
      bleibt davon unberührt)
  5. Erste Kaskade planen — Claude-Sitzung im Projektordner, Opus:
       "Du bist unser Architekt, lies team/prompts/rolle-architekt.md."
     Er härtet eine Skizze aus ${PLAN_ORDNER}roadmap-skizzen.md zu
     ${PLAN_ORDNER}ralph-kaskade-1-….md aus (mit RALPH_CAP= und
     BUDGET_EMPFEHLUNG_USD=) und gibt die Scharfschalt-Sequenz aus.
  6. Lauf starten:      cd $ZIEL && TEAM_BUDGET_USD=15 ./vollautomatik.sh
     ^ Deckel für DIESEN Lauf. Für einen kurzen Erstlauf sind 15 USD ein
       vernünftiger Start. Lieber nachziehen als zu tief ansetzen: ein zu
       tiefer Deckel wirft bezahlte Arbeit per Rollback weg und vervielfacht
       die Kosten, statt zu sparen (Feld-Lehre HM-32).
  7. NACH dem Lauf — Closeout, sonst sind die Kosten blind:
       ./team-status.sh --rollen-abschluss <N> <domaene>
       ./team-status.sh --architekt-abschluss <USD> <domaene> "Kaskade N geplant"
     Der Architekt läuft interaktiv, außerhalb der Kostenlogs — ohne diesen
     Schritt bleibt seine Sitzung strukturell unerfasst (im Feld ~16 USD).
EOF
if [ -z "$SMOKE_TEST" ]; then
    echo
    gelb "Hinweis: Kein Smoke-Test konfiguriert. Die Rollen laufen, aber ohne"
    gelb "Verifikationsschritt — sie melden das in jedem Prompt."
    gelb ""
    gelb "In ${PLAN_ORDNER}roadmap-skizzen.md liegt dafür bereits 'Skizze 1:"
    gelb "Verifikationsfähigkeit herstellen'. Der Architekt härtet sie als erste"
    gelb "Kaskade aus — sein Briefing kennt die Vorrangregel. Danach den Befehl"
    gelb "in team.config.sh bei TEAM_SMOKE_TEST eintragen."
fi
exit $FEHLER

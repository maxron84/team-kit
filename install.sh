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
#   TEAM_INIT_WEITERER_CODE (BL-52) TEAM_INIT_DOMAENEN TEAM_INIT_COMMIT_MODUS
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

# BL-109: "Der Block ist da" heisst NICHT "der Block ist vollstaendig". Das
# Fragment waechst mit dem Kit; wer frueh installiert und seither brav --update
# gefahren hat, blieb bisher dauerhaft auf dem Fragmentstand seines
# Installationstages — der Installer meldete dabei sogar Erfolg ("enthaelt den
# Block bereits") und der --update-Pfad sah gar nicht erst hin. Im Feld
# (team-kit_project_platformer) fehlten so .team-focus-harry und
# .team-focus-marv: beide standen nach JEDEM Sweep als untracked im Baum, sahen
# im Closeout wie unfertige Arbeit aus, und ein unachtsames `git add -A` haette
# einen Fokus-String verewigt, der fuer genau einen Lauf galt.
#
# Ergaenzt wird nur bei der ERSTINSTALLATION und nur der ganze Block. Fehlende
# Einzelzeilen werden ausschliesslich GEMELDET: Eine fehlende Zeile kann eine
# bewusst entfernte sein, und --update fasst Projektdateien grundsaetzlich
# nicht an. Der stille Fall ist der teure — die Meldung ist die risikofreie
# Haelfte und loeste den Fall im Feld vollstaendig.
gitignore_abgleich() {  # gitignore_abgleich <ergaenzen|melden>
    local zeile z fehlende="" nachtrag="" fehlzahl=0
    if [ "$1" = "ergaenzen" ] && \
       ! grep -q "T.E.A.M.-Loop-Laufzeitartefakte" "$ZIEL/.gitignore" 2>/dev/null; then
        cat "$KIT/bootstrap/gitignore.fragment" >> "$ZIEL/.gitignore"
        gruen "  ✓ .gitignore ergänzt"
        return 0
    fi
    # Verglichen wird Zeile fuer Zeile, nicht der Block als Ganzes: Der Block
    # kann seit Jahren dastehen und trotzdem die Haelfte der Vorlage vermissen.
    while IFS= read -r zeile || [ -n "$zeile" ]; do
        case "$zeile" in ''|'#'*) continue ;; esac
        if ! grep -Fxq -- "$zeile" "$ZIEL/.gitignore" 2>/dev/null; then
            fehlende="$fehlende$zeile
"
            nachtrag="$nachtrag '$zeile'"
            fehlzahl=$((fehlzahl + 1))
        fi
    done < "$KIT/bootstrap/gitignore.fragment"
    if [ "$fehlzahl" -eq 0 ]; then
        gruen "  ✓ .gitignore enthält den Block vollständig"
        return 0
    fi
    gelb "  ! .gitignore liegt $fehlzahl Zeile(n) hinter der Vorlage — es fehlen:"
    printf '%s' "$fehlende" | while IFS= read -r z; do gelb "      $z"; done
    gelb "    Nicht automatisch ergänzt (eine fehlende Zeile kann eine bewusst"
    gelb "    entfernte sein) — nachtragen mit:"
    gelb "      printf '%s\\n'$nachtrag >> \"$ZIEL/.gitignore\""
}

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

    # BL-51: --update ist der einzige Zeitpunkt, zu dem jemand von aussen auf
    # die Installation schaut. Gemeldet wird NUR, was in der Config steht —
    # keine Heuristik ueber den Ordnerinhalt: Nach dem Einzug ist der
    # Plan-Ordner die Arbeitsflaeche des Teams, dort ist "fremd" nicht mehr
    # unterscheidbar. Eine Warnung, die bei jedem Aufruf erscheint, erzieht zum
    # Wegsehen (BL-14).
    if [ -n "${TEAM_PLAN_ORDNER_BESTAND:-}${TEAM_TEST_ORDNER_BESTAND:-}" ]; then
        kopf "Bestand in der Schreibzone (BL-51)"
        [ -n "${TEAM_PLAN_ORDNER_BESTAND:-}" ] && \
            echo "  · ${PLAN_ORDNER}: ${TEAM_PLAN_ORDNER_BESTAND}"
        [ -n "${TEAM_TEST_ORDNER_BESTAND:-}" ] && \
            echo "  · ${TEST_ORDNER}: ${TEAM_TEST_ORDNER_BESTAND}"
        gelb "  Diese Dateien lagen beim Einzug des Teams schon da und stehen"
        gelb "  auf der Guard-Whitelist — die Read-Only-Rollen duerfen sie"
        gelb "  aendern und loeschen. Die Rollen-Prompts nennen sie als fremdes"
        gelb "  Eigentum; erzwingen kann der Guard es nicht. Wer die Mechanik"
        gelb "  will, gibt dem Team einen eigenen leeren Plan-Ordner."
    fi

    # BL-52: Ein Projekt von vor 2.6.0 kennt TEAM_WEITERER_CODE nicht, und
    # --update fasst team.config.sh bewusst nicht an. Der Hinweis kommt nur,
    # wenn im Wurzelverzeichnis ueberhaupt fremder Code liegt — sonst waere er
    # in jedem gruenen Projekt Rauschen.
    if [ -z "${TEAM_WEITERER_CODE:-}" ]; then
        WURZEL_CODE=""
        for f in "$ZIEL"/*; do
            [ -f "$f" ] || continue
            # Die Entrypoints des Kits sind kein Projektcode; Doku und
            # Konfigdateien greift kein Red Team an. Alles andere MIT Endung
            # ist Code, der heute ausserhalb des Pruefumfangs liegt.
            case "$(basename "$f")" in
                ralph.sh|frank.sh|axel.sh|harry.sh|marv.sh) ;;
                vollautomatik.sh|halbautomatik.sh|team-status.sh|team-test.sh|team.config.sh) ;;
                # Der Windows-Zweig: eigene Entrypoints des Kits, kein
                # Projektcode. Ohne diese Zeilen meldete der Installer die
                # eigenen Dateien als "ungeprueft in der Wurzel" — eine
                # Warnung, die bei jedem Aufruf erscheint, erzieht zum
                # Wegsehen (BL-14).
                ralph.ps1|frank.ps1|axel.ps1|harry.ps1|marv.ps1) ;;
                vollautomatik.ps1|halbautomatik.ps1|team-status.ps1|team-test.ps1|team.config.ps1) ;;
                ralph.cmd|frank.cmd|axel.cmd|harry.cmd|marv.cmd) ;;
                vollautomatik.cmd|halbautomatik.cmd|team-status.cmd|team-test.cmd) ;;
                *.md|LICENSE*|Makefile|*.toml|*.cfg|*.ini|*.txt|*.json|*.yaml|*.yml) ;;
                *.*) WURZEL_CODE="$WURZEL_CODE $(basename "$f")" ;;
            esac
        done
        if [ -n "$WURZEL_CODE" ]; then
            kopf "Pruefumfang endet an ${PRODUKTIVCODE} (BL-52)"
            echo "  Ungeprueft in der Wurzel:$WURZEL_CODE"
            gelb "  Das Red Team prueft ausschliesslich ${PRODUKTIVCODE} — Einstiegs-"
            gelb "  punkte und Build-Skripte daneben sieht es nie, und ein sauberer"
            gelb "  Sweep liest sich trotzdem wie ein sauberes Projekt."
            gelb "  Abhilfe (team.config.sh, --update fasst sie nicht an):"
            gelb "    TEAM_WEITERER_CODE=\"\${TEAM_WEITERER_CODE:-<pfade>}\""
        fi
    fi

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

    # Entrypoints — team.config.sh UND team.config.ps1 sind AUSGENOMMEN: sie
    # tragen die Projektwerte (Smoke-Test!) und sind damit Projektdatum, nicht
    # Infrastruktur. Beide Zweige werden aktualisiert; ein Projekt soll nach
    # einem Update nicht auf einer Haelfte veralten.
    for f in "$KIT"/entry/*.sh "$KIT"/entry/*.ps1 "$KIT"/entry/*.cmd; do
        [ -e "$f" ] || continue
        case "$(basename "$f")" in team.config.sh|team.config.ps1) continue ;; esac
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
    # conftest.py ist KEIN Test, aber ohne sie laeuft keiner der Tests, die den
    # Doppelbahn-Harnisch nehmen (`from conftest import …`). Sie faellt durch
    # das test_*.py-Muster und muss ausdruecklich mitkopiert werden — sonst
    # bricht die Installation an einem ModuleNotFoundError, den niemand mit
    # dem Installer in Verbindung bringt.
    kopiere "$KIT/team/tests/conftest.py" "team/tests/conftest.py"
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
    # team.config.ps1 steht hier aus demselben Grund wie team.config.sh: Sie
    # traegt die Projektwerte (Smoke-Test!) und ist damit Projektdatum, nicht
    # Infrastruktur. Beide werden vom Installer erzeugt, aber nur bei der
    # ERSTINSTALLATION — ein Update darf sie so wenig anfassen wie das Ledger.
    for d in team.config.sh team.config.ps1 CLAUDE.md CHANGELOG.md .budget-ledger .ralph-state \
             .gitignore "${PLAN_ORDNER}"; do
        [ -e "$ZIEL/$d" ] && echo "  · $d"
    done

    # BL-109: .gitignore bleibt unangetastet — aber "unangetastet" darf nicht
    # "ungeprueft" heissen. Bis hierher sah der Update-Pfad die Datei gar nicht
    # an; ein Projekt blieb auf dem Fragmentstand seines Installationstages,
    # waehrend der Installer Erfolg meldete. Gemeldet, nicht ergaenzt.
    kopf ".gitignore gegen die Vorlage (BL-109)"
    gitignore_abgleich melden

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
    # Die gerenderte Vorlage BLEIBT LIEGEN, wenn es eine Abweichung gibt, und
    # der Hinweis nennt einen Befehl, der sich kopieren laesst. Vorher stand
    # dort `diff <(…)` — ein Platzhalter fuer "die mit deinen Werten gerenderte
    # Vorlage", ohne zu sagen, wie man sie rendert. Der Hinweis verlangte damit
    # genau die Arbeit, die er abnehmen wollte (Bauart BL-44: angekuendigt, aber
    # nicht am wirksamen Ort ausfuehrbar).
    # Ablage im Temp-Bereich, NICHT im Projekt: Eine uncommittete Datei
    # ausserhalb der Whitelist sieht fuer den Read-Only-Guard aus wie ein
    # Regelbruch.
    ABGLEICH_DIR="$(mktemp -d "${TMPDIR:-/tmp}/team-kit-abgleich-XXXXXX")"
    for paar in "bootstrap/TEAM.md:TEAM.md" "bootstrap/CLAUDE.md.vorlage:CLAUDE.md"; do
        quelle="$KIT/${paar%%:*}"; ziel="$ZIEL/${paar##*:}"; name="${paar##*:}"
        [ -f "$ziel" ] || continue
        gerendert="$ABGLEICH_DIR/$name"
        cp "$quelle" "$gerendert"
        fuelle_abs "$gerendert"
        if ! diff -q "$gerendert" "$ziel" >/dev/null 2>&1; then
            zeilen="$(diff "$gerendert" "$ziel" | grep -c '^[<>]' || true)"
            echo "  ! $name weicht von der Kit-Fassung ab ($zeilen Zeilen)"
            echo "      diff -u \"$gerendert\" \"$ziel\""
            ABGLEICH=$((ABGLEICH + 1))
        else
            rm -f "$gerendert"
        fi
    done
    rmdir "$ABGLEICH_DIR" 2>/dev/null || true
    if [ "$ABGLEICH" -eq 0 ]; then
        gruen "  ✓ nichts offen"
    else
        gelb "  Bei CLAUDE.md ist eine Abweichung normal (Projektanpassungen,"
        gelb "  gefuellte TODOs). Entscheidend ist, ob dir REGELN aus der neuen"
        gelb "  Kit-Fassung fehlen — die Mechanik ist aktualisiert, die Regeln"
        gelb "  im Projekt sind es nicht (das war die Haelfte von BL-4)."
        echo "  Die gerenderte Kit-Fassung liegt unter $ABGLEICH_DIR/ bereit;"
        echo "  sie traegt bereits deine Werte. Temporaer — nach dem Abgleich"
        echo "  loeschen. Behalte deine Projekt-Spezifika und eigene Regeln,"
        echo "  uebernimm den Rest."
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
    echo "    git -C \"$ZIEL\" add -A && git -C \"$ZIEL\" commit -m \"chore: T.E.A.M. aktualisiert\""
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
    gelb "    bash $KIT/scripts/team-auth-setup.sh"
    gelb "    (oder gleich die ganze Maschine: bash $KIT/kit-einrichten.sh)"
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

# erklaerung: Vorspann zu einer Frage. Leerzeile davor, damit Frage und
# Erklaerung im Terminal nicht zu einer Wand verschwimmen — wer die Frage nicht
# findet, liest die Erklaerung nicht (BL-53).
erklaerung() {  # erklaerung <zeile>...
    [ "$INTERAKTIV" -eq 1 ] || return 0
    echo
    local zeile
    for zeile in "$@"; do echo "  $zeile"; done
}

# kandidaten_ausserhalb: was neben dem Produktivcode-Ordner in der Wurzel liegt
# und nach Code aussieht. Eine Liste zum Abschreiben schlaegt jede Erklaerung —
# die BL-52-Frage wird sonst verneint, weil dem Anwender im Moment der Frage
# nicht einfaellt, was er hat.
kandidaten_ausserhalb() {
    local eintrag name ausgabe="" n=0
    for eintrag in "$ZIEL"/*; do
        [ -e "$eintrag" ] || continue
        name="$(basename "$eintrag")"
        case "$name" in
            "${PRODUKTIVCODE%/}"|"${TEST_ORDNER%/}"|"${PLAN_ORDNER%/}") continue ;;
            team|node_modules|__pycache__|venv|.venv|dist|build|target) continue ;;
            docs|doku|data|assets|static|media|.*)                      continue ;;
            ralph.sh|frank.sh|harry.sh|marv.sh|axel.sh|install.sh)      continue ;;
            vollautomatik.sh|halbautomatik.sh|team-*.sh|team.config.sh) continue ;;
            ralph.ps1|frank.ps1|harry.ps1|marv.ps1|axel.ps1)            continue ;;
            vollautomatik.ps1|halbautomatik.ps1|team-*.ps1|team.config.ps1) continue ;;
            ralph.cmd|frank.cmd|harry.cmd|marv.cmd|axel.cmd|team-*.cmd) continue ;;
            vollautomatik.cmd|halbautomatik.cmd)                        continue ;;
            test_*|*_test.*|*.md|*.txt|*.json|*.toml|*.yaml|*.yml)      continue ;;
            *.cfg|*.ini|*.lock|LICENSE*|Makefile)                       continue ;;
        esac
        [ -d "$eintrag" ] && name="$name/"
        n=$((n + 1))
        [ "$n" -le 10 ] && ausgabe="$ausgabe $name"
    done
    [ "$n" -gt 10 ] && ausgabe="$ausgabe …"
    printf '%s' "${ausgabe# }"
}

kopf "Aufnahme-Interview — neun Fragen"
if [ "$INTERAKTIV" -eq 1 ]; then
    echo "  Hinter jeder Frage steht in [Klammern] eine Vorgabe. Enter nimmt sie an."
    echo "  Nichts davon ist endgültig: Alle Antworten landen in team.config.sh"
    echo "  und lassen sich dort jederzeit ändern."
fi
erklaerung "Unter welchem Namen soll das Projekt in Berichten und in der" \
           "Kostenabrechnung auftauchen?"
frage PROJEKT "Projektname" "$(basename "$ZIEL")"

erklaerung "In welchem Ordner liegt dein Programmcode?" \
           "Harry, Marv und Axel — die drei prüfenden Rollen — lesen ihn und" \
           "suchen dort Fehler. Ändern dürfen sie ihn nie; das macht allein" \
           "Frank, der Reparateur. Ein Wächter setzt das durch: Fasst eine der" \
           "drei den Ordner doch an, wird die Änderung automatisch zurückgenommen."
frage PRODUKTIVCODE "Ordner mit dem Programmcode" "src/"
PRODUKTIVCODE="${PRODUKTIVCODE%/}/"

erklaerung "Wohin dürfen die prüfenden Rollen Testdateien schreiben?" \
           "Findet Harry einen Fehler, legt er hier den Test ab, der ihn zeigt." \
           "Das ist einer von zwei Ordnern, in denen die drei schreiben UND" \
           "löschen dürfen — der Wächter greift hier nicht. Dein eigener" \
           "Testbefehl bleibt davon unberührt." \
           "Liegen dort schon eigene Tests, fragt der Installer gleich noch einmal."
frage TEST_ORDNER "Ordner für Tests" "tests/"
TEST_ORDNER="${TEST_ORDNER%/}/"

erklaerung "Wohin schreiben die Rollen ihre Pläne, Berichte und Fundlisten?" \
           "Der zweite Ordner mit Schreib- und Löschrecht. Am saubersten ist ein" \
           "eigener, leerer Ordner (z. B. team-plans/): Dann kommen die Rollen" \
           "mit deinen vorhandenen Dokumenten gar nicht erst in Berührung."
frage PLAN_ORDNER "Ordner für Pläne und Berichte" "plans/"
PLAN_ORDNER="${PLAN_ORDNER%/}/"

HINWEIS=("Liegt weiterer Programmcode AUSSERHALB von ${PRODUKTIVCODE}?" \
         "Gemeint ist Code, der beim Benutzen wirklich läuft: der Startpunkt in" \
         "der Wurzel (main.py), Build- und Deploy-Skripte (bin/, deploy/)." \
         "Was hier nicht steht, sieht sich nie jemand an — der Bericht meldet" \
         "dann \"sauber\" und meint bloß \"${PRODUKTIVCODE} ist sauber\"." \
         "NICHT eintragen: ${TEST_ORDNER} und ${PLAN_ORDNER}. Die hast du gerade" \
         "als Schreibordner vergeben, beides zugleich geht nicht." \
         "Neues Projekt oder alles unter ${PRODUKTIVCODE}: einfach Enter.")
KANDIDATEN="$(kandidaten_ausserhalb)"
[ -n "$KANDIDATEN" ] && HINWEIS+=("" "Neben ${PRODUKTIVCODE} liegt hier: ${KANDIDATEN}" \
                                     "Übernimm davon, was echter Programmcode ist.")
erklaerung "${HINWEIS[@]}"
frage WEITERER_CODE "Weiterer Code, mit Leerzeichen getrennt (leer = keiner)" ""

erklaerung "Gibt es EINEN Befehl, der zeigt, ob das Projekt noch heil ist?" \
           "Beispiele: 'pytest -q', 'npm test', 'python3 -c \"import src\"'." \
           "Die Rollen rufen ihn nach jeder Änderung auf. Schlägt er fehl, wird" \
           "die Änderung zurückgenommen — er ist das Sicherheitsnetz des Teams." \
           "Kennst du keinen: leer lassen. Dann ist es die erste Aufgabe des" \
           "Teams, einen zu bauen, und bis dahin sagt jede Rolle offen, dass sie" \
           "ohne Netz arbeitet."
frage SMOKE_TEST "Prüfbefehl (leer = gibt es noch nicht)" ""

erklaerung "Womit ist das Projekt gebaut? Eine Zeile, die den Rollen sagt," \
           "worauf sie sich einstellen müssen. Reine Beschreibung, nichts wird" \
           "davon ausgeführt." \
           "Beispiel: \"python3 tkinter sqlite\" oder \"TypeScript React Vite\"."
frage TECH_STACK "Technik in einer Zeile" "TODO: in CLAUDE.md nachtragen"

erklaerung "Auf welches Konto sollen die Kosten gebucht werden?" \
           "EIN Konto ist fast immer richtig: Dann landet jeder Lauf auf" \
           "'produkt' und du musst nie überlegen, wohin er gehört." \
           "Mehrere Konten nur, wenn du die Ausgaben wirklich getrennt sehen" \
           "willst. Der Preis: Beim Abrechnen nach jedem Lauf musst du dich für" \
           "GENAU EIN Konto entscheiden — auch wenn der Lauf mehrere Bereiche" \
           "berührt hat."
frage DOMAENEN "Kostenkonten, mit Leerzeichen getrennt" "produkt"

erklaerung "Der Architekt plant im Gespräch mit dir die nächste Runde und legt" \
           "den Plan in ${PLAN_ORDNER} ab. Soll er ihn selbst ins Git eintragen (j)," \
           "oder dir die fertigen Befehle zum Kopieren geben (n)?"
frage COMMIT_MODUS "Architekt committet selbst? (j/n)" "n"

# Kollision Pruefumfang/Schreibzone: Derselbe Ordner kann nicht beides sein.
# Stand er in beiden Antworten, sagte der Rollen-Prompt in EINEM Absatz "tabu"
# und "schreib hierhin" — beobachtet an Project-Family-ERP, wo tests/ in beiden
# stand und Harrys Reproducer-Auftrag damit widerspruechlich war. Wer seinen
# Testbestand schuetzen will, ist bei BL-51 richtig, nicht beim Pruefumfang.
if [ -n "$WEITERER_CODE" ]; then
    BEREINIGT=""; ENTFERNT=""
    for eintrag in $WEITERER_CODE; do
        case "${eintrag%/}/" in
            "$TEST_ORDNER"|"$PLAN_ORDNER") ENTFERNT="$ENTFERNT $eintrag" ;;
            *)                             BEREINIGT="$BEREINIGT $eintrag" ;;
        esac
    done
    if [ -n "$ENTFERNT" ]; then
        echo
        gelb "  ! Wieder aus dem Prüfumfang genommen:$ENTFERNT"
        gelb "    Das hast du eben schon als Schreibordner der Rollen vergeben."
        gelb "    Beides zugleich ginge nicht: Ihr Auftrag würde \"nicht anfassen\""
        gelb "    und \"hier ablegen\" im selben Absatz sagen. Um vorhandene Dateien"
        gelb "    darin kümmert sich der nächste Schritt."
        WEITERER_CODE="${BEREINIGT# }"
    fi
fi

# ---------------------------------------------------------------- BL-51
# Test- und Plan-Ordner sind die Schreibzone der drei Read-Only-Rollen: Die
# Guard-Whitelist ist POSITIV, dort schlaegt er nicht an. In einem neuen
# Projekt ist das folgenlos (die Ordner entstehen erst). In einer gewachsenen
# Codebasis ist "plans/" oder "docs/" typischerweise belegt — und Harry, Marv
# und Axel bekommen stillschweigend Schreib- und Loeschrecht auf
# Bestandsdokumente. Beobachtet an Project-Family-ERP: zehn fachliche Dokumente
# in plans/, darunter die Architektur- und die Refactoring-Planung.
#
# Gewarnt wird, nicht verboten: Ein bewusst geteilter Ordner kann legitim sein.
# Wer den Vorschlag annimmt, bekommt die Mechanik (eigener leerer Ordner); wer
# ihn ablehnt, bekommt den Bestand in team.config.sh vermerkt und damit in die
# Rollen-Prompts.
bestand_eintraege() {  # bestand_eintraege <ordner> — bis zu 12 Namen, sonst mit … gekuerzt
    local d="$ZIEL/${1%/}" n=0 ausgabe=""
    [ -d "$d" ] || return 0
    for eintrag in "$d"/* "$d"/.[!.]*; do
        [ -e "$eintrag" ] || continue
        n=$((n + 1))
        [ "$n" -le 12 ] && ausgabe="$ausgabe $(basename "$eintrag")"
    done
    [ "$n" -gt 12 ] && ausgabe="$ausgabe …"
    printf '%s' "${ausgabe# }"
}

bestand_pruefen() {  # bestand_pruefen <ORDNER-VARIABLE> <text> <rollen>
    local var="$1" text="$2" rollen="$3" eintraege neu
    while :; do
        eintraege="$(bestand_eintraege "${!var}")"
        [ -n "$eintraege" ] || break
        gelb "  ! Der $text '${!var}' ist nicht leer:"
        for e in $eintraege; do echo "      · $e"; done
        gelb "    Hier dürfen $rollen schreiben und löschen. Der Wächter, der sie"
        gelb "    von deinem Code fernhält, greift in diesem Ordner NICHT (BL-51)."
        gelb "    Deine Dateien verschwinden nicht einfach: Der Installer merkt sie"
        gelb "    sich und nennt sie den Rollen ausdrücklich als fremdes Eigentum."
        gelb "    Das ist aber eine Auflage an die KI, keine Sperre. Wirklich sicher"
        gelb "    ist nur ein eigener, leerer Ordner — z. B. team-${!var}"
        if [ "$INTERAKTIV" -eq 0 ]; then
            gelb "    Nicht-interaktiv: Ordner bleibt. Der Bestand wird in"
            gelb "    team.config.sh vermerkt und den Rollen als fremdes Eigentum genannt."
            break
        fi
        read -r -p "    Anderen, leeren Ordner nehmen? (Name, Enter = '${!var}' behalten): " neu || true
        [ -n "$neu" ] || break
        printf -v "$var" '%s' "${neu%/}/"
    done
    printf -v "${var}_BESTAND" '%s' "$(bestand_eintraege "${!var}")"
}

kopf "Liegt in den Schreibordnern der Rollen schon etwas? (BL-51)"
bestand_pruefen PLAN_ORDNER "Plan-Ordner" "Harry, Marv und Axel"
bestand_pruefen TEST_ORDNER "Test-Ordner" "Harry und Marv"
if [ -z "$PLAN_ORDNER_BESTAND" ] && [ -z "$TEST_ORDNER_BESTAND" ]; then
    gruen "  ✓ beide Ordner leer oder neu — nichts fremdes in der Schreibzone"
fi

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
                       "$DOMAENEN" "$COMMIT_ENTSCHEID" "$WEITERER_CODE" \
                       "$TEST_ORDNER_BESTAND" "$PLAN_ORDNER_BESTAND" <<'PY'
import sys, pathlib
(d, projekt, prod, test, plan, smoke, stack, deploy, ausn,
 domaenen, commit, weiterer, test_bestand, plan_bestand) = sys.argv[1:15]
p = pathlib.Path(d); t = p.read_text(encoding="utf-8")
for a, b in [("{{PROJEKTNAME}}", projekt), ("{{PRODUKTIVCODE}}", prod),
             ("{{TEST_ORDNER}}", test), ("{{PLAN_ORDNER}}", plan.rstrip("/")),
             ("{{BEUTEBUCH}}", plan.rstrip("/") + "/beutebuch.md"),
             ("{{CHANGELOG}}", "CHANGELOG.md"),
             ("{{FIX_PRAEFIX}}", "fix(uat)"), ("{{FEAT_PRAEFIX}}", "feat"),
             ("{{SMOKE_TEST}}", smoke or "TODO: noch keiner — Stufe 1 der ersten Kaskade"),
             ("{{TECH_STACK}}", stack), ("{{DEPLOY}}", deploy),
             ("{{DEPLOY_AUSNAHMEN}}", ausn), ("{{DOMAENEN}}", domaenen),
             ("{{COMMIT_ENTSCHEID}}", commit),
             # Nur in team.config.ps1: Unter Windows heisst der Interpreter je
             # nach Installation python/py. Dieser Installer laeuft unter
             # Linux, also steht hier python3; install.ps1 traegt ein, was es
             # auf der Maschine gefunden hat.
             ("{{PYTHON}}", "python3"),
             # BL-52/BL-51: leer ist der Normalfall — die Platzhalter stehen nur
             # in team.config.sh, damit eine leere Ersetzung nirgends Prosa
             # zerreisst.
             ("{{WEITERER_CODE}}", weiterer),
             ("{{TEST_BESTAND}}", test_bestand),
             ("{{PLAN_BESTAND}}", plan_bestand)]:
    t = t.replace(a, b)
p.write_text(t, encoding="utf-8")
PY
}

# Entrypoints in die Repo-Wurzel — der Strippenzieher tippt sie direkt
# (Ablage-Konvention aus dem Feld: Einstiegspunkte sichtbar oben).
# BEIDE Zweige werden installiert, auch wenn dieser Installer unter Linux
# laeuft und den Windows-Teil hier niemand braucht. Der Grund ist die
# Zusicherung, auf der der Windows-Zweig ruht: team.config.sh und
# team.config.ps1 sind ZWEI GENERATE EINER QUELLE (denselben neun Antworten),
# keine zwei gepflegten Dateien. Installierte nur install.ps1 den
# PowerShell-Teil, haette ein auf Linux eingerichtetes Projekt unter Windows
# keine Konfiguration — und jemand schriebe sie von Hand. Genau dort faengt
# Drift an. Das Projekt ist damit von beiden Systemen aus bedienbar, ohne dass
# irgendwer nachinstalliert.
for f in "$KIT"/entry/*.sh "$KIT"/entry/*.ps1 "$KIT"/entry/*.cmd; do
    [ -e "$f" ] || continue
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
# Siehe Begruendung im Update-Pfad: kein Test, aber Voraussetzung mehrerer.
kopiere "$KIT/team/tests/conftest.py" "team/tests/conftest.py"
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
for d in CLAUDE.md TEAM.md team.config.sh team.config.ps1 CHANGELOG.md \
         "${PLAN_ORDNER}roadmap-skizzen.md" "${PLAN_ORDNER}backlog.md" \
         "${PLAN_ORDNER}beutebuch.md"; do
    fuelle "$d"
done
for d in "$ZIEL"/team/prompts/*.md; do
    fuelle "team/prompts/$(basename "$d")"
done

# ---------------------------------------------------------------- .gitignore
gitignore_abgleich ergaenzen

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

  1. Werte prüfen:      \$EDITOR "$ZIEL/team.config.sh"
  2. Regeln prüfen:     \$EDITOR "$ZIEL/CLAUDE.md"   (TODO-Stellen füllen)
  3. Alles committen:   git -C "$ZIEL" add -A && git -C "$ZIEL" commit -m "chore: T.E.A.M. eingerichtet"
     ^ WICHTIG: vor dem ersten Lauf committen. Der Wächter hält uncommittete
       Dateien für einen Übergriff der Rollen und räumt sie weg.
  4. Team-Tests:        cd "$ZIEL" && ./team-test.sh
     (pytest, prüft NUR die Team-Infrastruktur — dein Projekt-Testbefehl
      bleibt davon unberührt)
  5. Erste Kaskade planen — Sitzung im Projektordner, starke Stufe (Default Opus):
       "Du bist unser Architekt, lies team/prompts/rolle-architekt.md."
     Er härtet eine Skizze aus ${PLAN_ORDNER}roadmap-skizzen.md zu
     ${PLAN_ORDNER}ralph-kaskade-1-….md aus (mit RALPH_CAP= und
     BUDGET_EMPFEHLUNG_USD=) und gibt die Scharfschalt-Sequenz aus.
  6. Lauf starten:      cd "$ZIEL" && TEAM_BUDGET_USD=15 ./vollautomatik.sh
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

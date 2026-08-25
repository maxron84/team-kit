#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: install.ps1
# install.sh — installiert das T.E.A.M. in ein Zielprojekt.
#
# Aufruf:  bash bash/install.sh <zielpfad> [--nicht-interaktiv] [--force|--update]
#                                          [--nur-bash|--nur-pwsh|--beide-bahnen]
#          bash bash/install.sh --hilfe
#
#   <zielpfad>          Das Projekt, in das das Team einziehen soll. Muss ein
#                       Git-Repository sein. Pflichtangabe (außer bei --hilfe).
#   --nicht-interaktiv  Keine Rückfragen; Werte aus den TEAM_INIT_*-Umgebungs-
#                       variablen oder den Defaults. Für Skripte und Tests.
#   --update            Nur die Team-INFRASTRUKTUR aktualisieren (Entrypoints
#                       ausser team.config.sh, team/lib.sh, team/redteam.sh,
#                       team/tools/, team/prompts/, team/tests/ und TEAM.md,
#                       die Bedienungsanleitung). Rührt KEINE Projektdaten an:
#                       team.config.*, CLAUDE.md, CHANGELOG.md, Ledger, State
#                       und plans/ bleiben, wie sie sind. Der richtige Weg, um
#                       ein bestehendes Projekt auf eine neue Kit-Version zu
#                       heben.
#   --force             Vorhandene Dateien überschreiben (Standard: überspringen).
#
#   ⚠  --force ist NUR für eine kaputte Erstinstallation gedacht, NIE für ein
#      gelebtes Projekt: Es überschreibt auch .budget-ledger (Kostenhistorie
#      weg), .ralph-state (Kaskadenstand zurück auf 1), das Beutebuch (alle
#      Funde weg), CHANGELOG.md, plans/*.md und team.config.sh (Smoke-Test
#      weg). Empirisch nachgestellt, siehe BL-8. Für Updates: --update.
#
#   --nur-bash          Nur die bash-Bahn ablegen (Entrypoints *.sh,
#                       team/lib.sh, team.config.sh).
#   --nur-pwsh          Nur die pwsh-Bahn ablegen (Entrypoints *.cmd/*.ps1,
#                       team/lib.psm1, team.config.ps1).
#                       Ohne beide Schalter kommen BEIDE Bahnen — die Abwahl
#                       ist ausdrücklich und kommt vom Anwender (BL-119).
#   --beide-bahnen      Nur mit --update: eine früher abgewählte Bahn wieder
#                       zurückholen. Schließt --nur-bash/--nur-pwsh aus.
#   -h, --hilfe, --help Diesen Kopf ausgeben und sonst nichts tun.
#
# Umgebungsvariablen für den nicht-interaktiven Betrieb:
#   TEAM_INIT_PROJEKT TEAM_INIT_PRODUKTIVCODE TEAM_INIT_TEST_ORDNER
#   TEAM_INIT_PLAN_ORDNER TEAM_INIT_SMOKE_TEST TEAM_INIT_TECH_STACK
#   TEAM_INIT_WEITERER_CODE (BL-52) TEAM_INIT_DOMAENEN TEAM_INIT_COMMIT_MODUS
#
# Der Installer ist idempotent: ein zweiter Lauf überschreibt nichts, sondern
# meldet, was bereits vorhanden ist.
set -euo pipefail

# Zwei Anker seit der Bahn-Trennung: BAHN ist <kit>/bash (hier liegt dieses
# Skript), KIT die Wurzel des Kits. Der Installer liest aus BEIDEN Bahnen —
# er installiert bewusst auch die pwsh-Seite (siehe Begruendung weiter unten).
BAHN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$(dirname "$BAHN")"
ZIEL=""
INTERAKTIV=1
FORCE=0
UPDATE=0
# Welche Bahnen installiert werden. Default ist BEIDE — siehe die ausfuehrliche
# Begruendung am Kopierblock: die zwei Konfigurationen sind zwei Generate EINER
# Quelle, und wer nur eine Bahn bekommt, schreibt die andere irgendwann von
# Hand. Die Abwahl ist deshalb ausdruecklich und kommt vom Anwender, nie vom
# Installer (BL-119).
NUR_BAHN=""
# BL-147: Der Rueckweg aus BL-119 — "ein Update macht das Projekt wieder
# vollstaendig" — war bis hierher der Default und damit ein Automatismus.
# Jetzt ist er ein Schalter. Begruendung am Erkennungsblock im Update-Pfad.
BEIDE_BAHNEN=0

# BL-139: Die Regeltexte nennen Pfade — und in einer einbahnigen Ablage nennen
# sie damit Dateien, die es dort nicht gibt. Im Feld (Feld B, mit
# --nur-pwsh installiert) waren das 14 tote .sh-Pfade in CLAUDE.md und 23 in
# TEAM.md. Am teuersten team.config.sh: Der Regeltext schickte jede Rolle
# dorthin, um TEAM_SMOKE_TEST nachzutragen, waehrend team/lib.psm1
# team.config.ps1 liest — zwei einander widersprechende Anweisungen im selben
# Systemprompt, und der Fehlermodus ist STILL. Wer der Regel folgt, legt eine
# Datei an, die nie gelesen wird: kein Abbruch, keine Meldung, der Wert wirkt
# einfach nicht.
#
# Gebaut als Platzhalter statt als Nachbearbeitung der fertigen Datei: Die
# Vorlage sagt dann selbst, welche Stellen bahnabhaengig sind, und eine neu
# dazugeschriebene Zeile faellt im Test auf, statt still die alte Bahn zu
# nennen. Die Zwei-Bahnen-Tabelle in TEAM.md und der Ablage-Block in
# CLAUDE.md.vorlage bleiben ausdruecklich literal — sie STELLEN die Bahnen
# GEGENUEBER, das ist ihr Zweck.
#
# Vorbelegt ist die bash-Bahn: In einer zweibahnigen Ablage (dem Default) liegt
# beides, und der gerenderte Text bleibt damit Byte fuer Byte der von vorher.
# Nur --nur-pwsh aendert etwas.
bahn_werte() {
    if [ "$NUR_BAHN" = "pwsh" ]; then
        BAHN_RUF='.\'         ; BAHN_ENDUNG='.cmd'
        BAHN_KONFIG='team.config.ps1'
        BAHN_LIB='team/lib.psm1'; BAHN_REDTEAM='team/redteam.ps1'
    else
        BAHN_RUF='./'          ; BAHN_ENDUNG='.sh'
        BAHN_KONFIG='team.config.sh'
        BAHN_LIB='team/lib.sh' ; BAHN_REDTEAM='team/redteam.sh'
    fi
}

# Der Hilfetext IST der Dateikopf, keine zweite Fassung daneben: Eine Abschrift
# laeuft irgendwann auseinander, und dann sagt --hilfe etwas anderes als die
# Datei (dieselbe Lehre wie BL-154). Gelesen wird ab Zeile 3 — Zeile 1 ist die
# Shebang, Zeile 2 die Bahn-Kopfzeile, beides Maschinensache — bis zur ersten
# Zeile, die kein Kommentar mehr ist. Waechst der Kopf, waechst die Hilfe mit.
hilfe() {
    sed -n '3,${
        /^#/!q
        s/^# \{0,1\}//
        p
    }' "${BASH_SOURCE[0]}"
}

for arg in "$@"; do
    case "$arg" in
        -h|--hilfe|--help)  hilfe; exit 0 ;;
        --nicht-interaktiv) INTERAKTIV=0 ;;
        --force)            FORCE=1 ;;
        --update)           UPDATE=1 ;;
        --nur-bash)         NUR_BAHN="bash" ;;
        --nur-pwsh)         NUR_BAHN="pwsh" ;;
        --beide-bahnen)     BEIDE_BAHNEN=1 ;;
        -*) echo "Unbekannte Option: $arg" >&2; exit 2 ;;
        *)  ZIEL="$arg" ;;
    esac
done

if [ "$BEIDE_BAHNEN" -eq 1 ] && [ -n "$NUR_BAHN" ]; then
    printf '\033[31m%s\033[0m\n' "FEHLER: --beide-bahnen und --nur-$NUR_BAHN schliessen sich aus."
    echo "  --beide-bahnen holt eine fehlende Bahn zurueck, --nur-* waehlt eine ab."
    exit 2
fi

# BL-139: Erst JETZT stehen die Schalter fest — vorher waeren die Werte geraten.
# (Nach der Bahn-Erkennung im Update-Pfad wird erneut gerufen, BL-147.)
bahn_werte

# Gehoert die Datei zu einer abgewaehlten Bahn? Entscheidet ueber die ENDUNG,
# weil das Kit an dieser Stelle Kit-Pfade (bash/entry/…) auf Projekt-Pfade
# (ralph.sh in der Wurzel) abbildet und der Bahn-Ordner damit weg ist.
bahn_abgewaehlt() {
    case "$NUR_BAHN" in
        bash) case "$1" in *.ps1|*.psm1|*.cmd) return 0 ;; esac ;;
        pwsh) case "$1" in *.sh) return 0 ;; esac ;;
    esac
    return 1
}

# BL-147: Liegt diese Bahn im Zielprojekt? Gefragt wird nach den Dateien, die
# das KIT ausliefert — nicht nach der Endung. Ein projekteigenes deploy.ps1
# ist keine pwsh-Bahn, und ein build.sh macht aus einem Windows-Projekt kein
# zweibahniges. Genau daran haette eine Endungs-Heuristik im Feld vorbeigelesen.
bahn_liegt_da() {  # bahn_liegt_da <bash|pwsh> — 0, wenn diese Bahn da ist
    local f
    if [ "$1" = "bash" ]; then
        for f in "$KIT"/bash/entry/*.sh; do
            [ -f "$ZIEL/$(basename "$f")" ] && return 0
        done
        [ -f "$ZIEL/team/lib.sh" ] && return 0
        [ -f "$ZIEL/team/redteam.sh" ] && return 0
    else
        for f in "$KIT"/pwsh/entry/*.ps1 "$KIT"/pwsh/entry/*.cmd; do
            [ -e "$f" ] || continue
            [ -f "$ZIEL/$(basename "$f")" ] && return 0
        done
        [ -f "$ZIEL/team/lib.psm1" ] && return 0
        [ -f "$ZIEL/team/redteam.ps1" ] && return 0
    fi
    return 1
}

rot()  { printf '\033[31m%s\033[0m\n' "$*"; }
gruen(){ printf '\033[32m%s\033[0m\n' "$*"; }
gelb() { printf '\033[33m%s\033[0m\n' "$*"; }
kopf() { printf '\n\033[1m%s\033[0m\n' "$*"; }

[ -n "$ZIEL" ] || { rot "FEHLER: Kein Zielpfad angegeben."; echo "Aufruf: bash bash/install.sh <zielpfad>"; echo "Alle Optionen: bash bash/install.sh --hilfe"; exit 2; }
ZIEL="$(cd "$ZIEL" 2>/dev/null && pwd)" || { rot "FEHLER: Zielpfad existiert nicht: $ZIEL"; exit 2; }

# BL-109: "Der Block ist da" heisst NICHT "der Block ist vollstaendig". Das
# Fragment waechst mit dem Kit; wer frueh installiert und seither brav --update
# gefahren hat, blieb bisher dauerhaft auf dem Fragmentstand seines
# Installationstages — der Installer meldete dabei sogar Erfolg ("enthaelt den
# Block bereits") und der --update-Pfad sah gar nicht erst hin. Im Feld
# (Feld A) fehlten so .team-focus-harry und
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

# gitattributes_abgleich — die Zeilenenden, mit denen das Projekt AUSCHECKT.
#
# BL-136, dieselbe Bauart wie gitignore_abgleich und aus demselben Grund
# geschrieben. Das Kit-Repo haelt diese Regel seit Langem fuer sich selbst; die
# ZIELPROJEKTE bekamen nie eine .gitattributes. Sie schuetzte damit genau dort
# nicht, wo das Kit im Feld laeuft.
#
# Der Fall entsteht NICHT bei der Installation — der Installer schreibt mit LF.
# Er entsteht beim naechsten Klon oder Checkout, unter Git for Windows mit dem
# Auslieferungswert core.autocrlf=true: Dann traegt jede .sh CRLF, an die
# Shebang-Zeile haengt sich ein Wagenruecklauf, und bash sucht einen
# Interpreter, dessen Name auf genau dieses unsichtbare Zeichen endet. Die
# Meldung lautet "bad interpreter" und sieht nach einer kaputten Installation
# aus. Weit weg von der Ursache, auf einer anderen Maschine, oft Wochen
# spaeter.
#
# Ergaenzt wird nur bei der ERSTINSTALLATION, gemeldet beim Update — die Datei
# gehoert dem Projekt (Bauart BL-109).
gitattributes_abgleich() {  # gitattributes_abgleich <ergaenzen|melden>
    local zeile z fehlende="" nachtrag="" fehlzahl=0
    if [ "$1" = "ergaenzen" ] && \
       ! grep -q "T.E.A.M.-Zeilenenden" "$ZIEL/.gitattributes" 2>/dev/null; then
        cat "$KIT/bootstrap/gitattributes.fragment" >> "$ZIEL/.gitattributes"
        gruen "  ✓ .gitattributes ergänzt"
        return 0
    fi
    # Zeile fuer Zeile wie beim .gitignore: Der Block kann dastehen und
    # trotzdem die Haelfte der Vorlage vermissen.
    while IFS= read -r zeile || [ -n "$zeile" ]; do
        case "$zeile" in ''|'#'*) continue ;; esac
        if ! grep -Fxq -- "$zeile" "$ZIEL/.gitattributes" 2>/dev/null; then
            fehlende="$fehlende$zeile
"
            nachtrag="$nachtrag '$zeile'"
            fehlzahl=$((fehlzahl + 1))
        fi
    done < "$KIT/bootstrap/gitattributes.fragment"
    if [ "$fehlzahl" -eq 0 ]; then
        gruen "  ✓ .gitattributes enthält den Block vollständig"
        return 0
    fi
    gelb "  ! .gitattributes liegt $fehlzahl Zeile(n) hinter der Vorlage — es fehlen:"
    printf '%s' "$fehlende" | while IFS= read -r z; do gelb "      $z"; done
    gelb "    Nicht automatisch ergänzt (die Datei gehört dem Projekt) —"
    gelb "    nachtragen mit:"
    gelb "      printf '%s\\n'$nachtrag >> \"$ZIEL/.gitattributes\""
    gelb "    Danach EINMAL neu einlesen, sonst wirkt es erst beim nächsten"
    gelb "    Klon:  git -C \"$ZIEL\" add --renormalize ."
}

# python_abgleich — steht in der Konfiguration ein Interpreter, der ANTWORTET?
#
# BL-133, derselbe Schnitt wie BL-109 bei der .gitignore: "--update fasst
# team.config.* nicht an" ist richtig; "sieht sie gar nicht an" war es nicht.
#
# Ein Projekt, das vor BL-122/BL-131 eingerichtet wurde, traegt in BEIDEN
# Konfigurationen den Namen `python3` — die Vorlagen hatten damals gar keinen
# Platzhalter, es gab nichts zu fuellen. Unter Windows ist dieser Name nicht
# abwesend, sondern BELEGT: der App-Execution-Alias aus dem Microsoft Store.
# Er startet, schreibt "Python was not found" und endet mit 49.
#
# Die Wirkung ist deshalb keine Fehlermeldung, sondern eine LEERE Zahl.
# `team-status --budget` zeigte "real via API abgerechnet:  USD" — nicht null,
# nicht Fehler, leer. Der komplette Kostenpfad war seit dem Installationstag
# tot, und jedes Update meldete Erfolg.
#
# Geprueft wird der START, nicht die Existenz: `command -v` findet den Alias
# (das ist die Lehre aus BL-122). Gemeldet, nicht repariert — die
# Konfiguration traegt Projektdaten; der Nachtrag steht als kopierbare Zeile
# daneben.
python_aus_config() {  # python_aus_config <konfigdatei>
    local name
    name="$(sed -n 's/.*[-:"'"'"'$ ]\([A-Za-z0-9_.]*\) team\/tools\/kosten\.py.*/\1/p' \
            "$1" | head -1)"
    if [ "$name" = "TEAM_PYTHON" ]; then
        # Die Werkzeugzeile zeigt auf die Variable — der Name steht eine Zeile
        # hoeher. `tr -d` davor, weil dieser Ausdruck als einziger am
        # ZEILENENDE ankert: Eine team.config.sh, die unter Windows liegt, hat
        # CRLF, und dann steht zwischen `}"` und dem Anker noch ein
        # Wagenruecklauf. Das sed aus Git for Windows nimmt ihn von sich aus
        # weg, GNU sed unter Linux nicht — der Fall waere also ausgerechnet
        # dort rot, wo diese Bahn zu Hause ist.
        name="$(tr -d '\r' < "$1" \
                | sed -n 's/^TEAM_PYTHON="\${TEAM_PYTHON:-\(.*\)}"$/\1/p' | head -1)"
    fi
    printf '%s' "$name"
}

python_abgleich() {
    local datei name gefunden=0 kaputt=0
    for datei in "$ZIEL/team.config.sh" "$ZIEL/team.config.ps1"; do
        [ -f "$datei" ] || continue
        gefunden=1
        name="$(python_aus_config "$datei")"
        if [ -z "$name" ]; then
            gelb "  ! $(basename "$datei"): kein Interpretername auffindbar —"
            gelb "    bitte die Zeile mit team/tools/kosten.py von Hand ansehen."
            continue
        fi
        if command -v "$name" >/dev/null 2>&1 && \
           "$name" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 8) else 1)' \
                >/dev/null 2>&1; then
            gruen "  ✓ $(basename "$datei"): '$name' startet und ist Python 3.8+"
            continue
        fi
        kaputt=1
        rot   "  ✗ $(basename "$datei"): '$name' antwortet auf dieser Maschine nicht."
        if [ "$PYTHON_GEFUNDEN" -eq 1 ]; then
            gelb "    Hier laeuft Python unter dem Namen '$PYTHON'."
        else
            gelb "    Es liess sich auch kein anderer Name finden — Python fehlt."
        fi
        case "$(basename "$datei")" in
            team.config.sh)
                gelb "    Nachtragen (--update fasst die Datei nicht an):"
                gelb "      TEAM_PYTHON=\"\${TEAM_PYTHON:-$PYTHON}\""
                gelb "      TEAM_BEUTEBUCH_TOOL=\"\${TEAM_BEUTEBUCH_TOOL:-\$TEAM_PYTHON team/tools/beutebuch.py}\""
                gelb "      TEAM_KOSTEN_TOOL=\"\${TEAM_KOSTEN_TOOL:-\$TEAM_PYTHON team/tools/kosten.py}\""
                ;;
            team.config.ps1)
                gelb "    Nachtragen (--update fasst die Datei nicht an):"
                gelb "      \$TEAM_BEUTEBUCH_TOOL = Team-Wert 'TEAM_BEUTEBUCH_TOOL' '$PYTHON team/tools/beutebuch.py'"
                gelb "      \$TEAM_KOSTEN_TOOL    = Team-Wert 'TEAM_KOSTEN_TOOL'    '$PYTHON team/tools/kosten.py'"
                ;;
        esac
    done
    [ "$gefunden" -eq 1 ] || gelb "  ! keine Konfiguration gefunden"
    [ "$kaputt" -eq 0 ]
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
# team_pytest: Der Aufruf, mit dem pytest hier erreichbar ist (BL-124).
# Bevorzugt der MODULAUFRUF ueber denselben Interpreter, unter dem auch
# team/tools/ laeuft: Ein pytest im PATH kann zu einer anderen Installation
# gehoeren, und bei `pip install --user` steht sein bin-Verzeichnis oft gar
# nicht im PATH. Gibt nichts aus und liefert 1, wenn es pytest nicht gibt.
#
# BL-127: Diese Definition stand bis hierher INNERHALB des --update-Blocks.
# Bash definiert eine Funktion erst, wenn die Definition AUSGEFUEHRT wird —
# auf dem Erstinstallations-Pfad wurde der Block nie betreten, und der
# Selbsttest am Ende rief eine Funktion auf, die es nicht gab
# ("team_pytest: command not found", danach "pytest nicht gefunden").
# Jede frische Installation hat damit ihre Regressionstests uebersprungen:
# genau die Pruefung, fuer die BL-124 gebaut wurde, tot auf dem Weg, auf
# dem sie am meisten zaehlt. Die Einrueckung tarnte es — die Funktion stand
# in Spalte 0 und sah aus wie eine Definition auf oberster Ebene.
# finde_python: der Name, unter dem Python auf DIESER Maschine antwortet.
#
# BL-131. Bis hierher stand an drei Stellen fest `python3` — im Installer
# selbst, in team.config.sh und dreizehnmal in lib.sh —, jeweils mit der
# Begruendung "dieser Installer laeuft unter Linux". Unter Git for Windows
# laeuft er das nicht. Und dort ist `python3` nicht etwa abwesend, sondern
# BELEGT: %LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe ist der
# App-Execution-Alias aus dem Microsoft Store. `command -v` findet ihn,
# der Aufruf startet den Store und meldet "Python was not found".
#
# Das ist derselbe Fund wie BL-122/BL-125 auf der pwsh-Bahn; `Finde-Python`
# in install.ps1 loest ihn dort seit Langem. Diese Bahn hatte ihn nie
# nachgezogen, weil niemand sie unter Windows gefahren hat. Die Reihenfolge
# ist deshalb zeichengleich mit der dort: unter Windows `python` zuerst,
# sonst `python3` zuerst.
#
# Geprueft wird START UND VERSION: Der Store-Alias startet und endet mit != 0,
# und ein `python` aus einer Alt-Installation koennte Python 2 sein.
finde_python() {
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

# Einmal aufloesen, ueberall benutzen. Faellt die Probe aus, bleibt der
# POSIX-Name stehen — aber die Luecke wird GENANNT statt verdeckt (die Meldung
# steht unten, wo auch die uebrigen Vorbedingungen gemeldet werden).
if PYTHON="$(finde_python)"; then
    PYTHON_GEFUNDEN=1
else
    PYTHON="python3"; PYTHON_GEFUNDEN=0
fi

team_pytest() {
    local py
    for py in "$PYTHON" python3 python py; do
        command -v "$py" >/dev/null 2>&1 || continue
        if "$py" -m pytest --version >/dev/null 2>&1; then
            printf '%s -m pytest' "$py"; return 0
        fi
    done
    command -v pytest >/dev/null 2>&1 && { printf 'pytest'; return 0; }
    return 1
}

# pytest_mitschnitt: Fährt die Regressionssuite und zeigt sie GLEICHZEITIG auf
# dem Bildschirm und im Log. Gegenstück zu Pytest-Mitschnitt in install.ps1.
#
# Vorher ging alles nur ins Log (`>… 2>&1`). Der Bildschirm zeigte dann
# "Selbsttest" und danach minutenlang nichts — im Feld sieht das aus wie ein
# Hänger und ist keiner: Die Suite läuft, nur stumm. Wer nicht weiß, dass sie
# einbahnig rund vier und zweibahnig rund zwanzig Minuten braucht, bricht ab und
# hält einen gesunden Installer für kaputt.
#
# Zwei Feinheiten, ohne die es nur halb wirkt:
#
#   1. PYTHONUNBUFFERED. Schreibt Python nicht auf ein Terminal, sondern in eine
#      Pipe, puffert es blockweise. Die Fortschrittszeilen kämen dann in Schüben
#      von einigen KB, also praktisch erst am Schluss — der Hänger wäre nur
#      kürzer geworden, nicht weg.
#   2. `tee` schreibt ROH ins Log; die Einrückung entsteht erst danach für den
#      Bildschirm. Damit bleibt die Datei genau das, was pytest geschrieben hat
#      — die `grep -oE '[0-9]+ passed'` und `tail -3` der Aufrufer lesen
#      unverändert weiter, und wer das Log verschickt, verschickt kein
#      eingerücktes Zerrbild.
#
# Der Exit-Code ist der von pytest, nicht der von sed: Dieses Skript läuft unter
# `set -o pipefail` (Zeile 43), und das ist hier keine Nebensache, sondern die
# Bedingung dafür, dass ein roter Testlauf überhaupt noch rot ankommt.
#
# Aufruf:  pytest_mitschnitt <logpfad> $PYTEST_AUFRUF
#          ^ $PYTEST_AUFRUF bewusst UNGEQUOTET — es ist ein mehrwortiger Aufruf
#            ("python3 -m pytest"), und die Wortzerlegung ist gewollt.
pytest_mitschnitt() {
    local log="$1"; shift
    PYTHONUNBUFFERED=1 "$@" -q team/tests 2>&1 | tee "$log" | sed 's/^/      /'
}

if [ "$UPDATE" -eq 1 ]; then
    kopf "Update — nur Team-Infrastruktur"
    # BL-126: Als Merkmal einer Installation zaehlt JEDE der beiden
    # Konfigurationen. Bis hierher zaehlte nur die Bash-Fassung — und damit
    # war der Rueckweg, den BL-119 ausdruecklich verspricht ("ein --update
    # ohne Schalter macht das Projekt wieder vollstaendig"), fuer ein mit
    # --nur-pwsh installiertes Projekt versperrt: Der Installer erklaerte es
    # fuer keine Installation und stieg aus, bevor er die fehlende Bahn
    # nachziehen konnte. Die Abwahl war in dieser Richtung eine
    # Einbahnstrasse — genau das, was sie nicht sein darf.
    if [ ! -f "$ZIEL/team.config.sh" ] && [ ! -f "$ZIEL/team.config.ps1" ]; then
        rot "FEHLER: $ZIEL sieht nicht nach einer T.E.A.M.-Installation aus"
        echo "  (weder team.config.sh noch team.config.ps1). Fuer eine"
        echo "  Erstinstallation ohne --update aufrufen."
        exit 2
    fi

    # BL-147: Welche Bahn ein Projekt faehrt, sagt die ABLAGE — nicht der
    # Schalter, den beim Update gerade niemand tippt. Bis hierher galt der
    # Umkehrschluss: Ein --update ohne Schalter machte das Projekt "wieder
    # vollstaendig" (BL-119) und legte die zweite Bahn dazu. Als Rueckweg aus
    # einer Abwahl gedacht — im Feld ist es der Normalfall geworden, und der
    # Normalfall will keine zweite Bahn.
    #
    # Feld A, 2026-08-22: Ein Routine-Update legte 21 pwsh-Dateien in ein
    # reines Bash-Projekt. Untracked, unbestellt, und weil sie im Baum lagen,
    # fuhr die Testsuite ab da eine Bahn mit, die dort niemand faehrt
    # (conftest entscheidet an der ANWESENHEIT der Dateien). Der Anwender
    # bemerkt es an 19 fremden Dateien in `git status` — falls er hinsieht.
    #
    # Der Rueckweg bleibt, er wird nur ausdruecklich: --beide-bahnen. Das ist
    # derselbe Schnitt wie bei der Abwahl selbst ("kommt vom Anwender, nie vom
    # Installer") — nur jetzt in beide Richtungen.
    if [ -z "$NUR_BAHN" ] && [ "$BEIDE_BAHNEN" -eq 0 ]; then
        if   bahn_liegt_da bash && ! bahn_liegt_da pwsh; then NUR_BAHN="bash"
        elif bahn_liegt_da pwsh && ! bahn_liegt_da bash; then NUR_BAHN="pwsh"
        fi
        if [ -n "$NUR_BAHN" ]; then
            # Die Bahn steht erst JETZT fest — die Regeltexte muessen ihre
            # Pfade daraus bekommen, sonst nennt der Systemprompt jeder Rolle
            # Dateien, die es hier nicht gibt (BL-139).
            bahn_werte
            gruen "  ✓ Einbahnige Ablage erkannt: nur die ${NUR_BAHN}-Bahn (BL-147)"
            echo  "    Das Update haelt sie einbahnig und legt keine Dateien der"
            echo  "    anderen Bahn dazu. Zweibahnig machen (ausdruecklich):"
            echo  "      bash $KIT/bash/install.sh \"$ZIEL\" --update --beide-bahnen"
        fi
    fi

    # BL-10: NIEMALS in einen laufenden Lauf hinein aktualisieren. Real
    # passiert (2026-08-01, Feld A): Ein Update waehrend
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
    #
    # BL-126: WELCHE der beiden Fassungen die Werte traegt, haengt an der
    # Installation. Ueblicherweise ist es die .sh (sie liegt in jeder
    # zweibahnigen Ablage); in einem mit --nur-pwsh installierten Projekt
    # gibt es sie nicht, und dann stehen die Werte NUR in der .ps1. Die wird
    # gelesen, nicht gesourct — fuer bash ist sie kein Skript. Die Zeilen,
    # um die es geht, haben eine feste Form, die der Installer selbst
    # erzeugt:  $TEAM_X = Team-Wert 'TEAM_X' 'wert'
    if [ -f "$ZIEL/team.config.sh" ]; then
        KONF_QUELLE="team.config.sh"
        # shellcheck disable=SC1091
        . "$ZIEL/team.config.sh"
    else
        KONF_QUELLE="team.config.ps1"
        for _name in TEAM_PROJEKT TEAM_PRODUKTIVCODE TEAM_TEST_ORDNER \
                     TEAM_PLAN_ORDNER TEAM_SMOKE_TEST TEAM_DOMAENEN \
                     TEAM_TEST_ORDNER_BESTAND TEAM_PLAN_ORDNER_BESTAND; do
            _wert="$(sed -n "s/^\\\$$_name[[:space:]]*=[[:space:]]*Team-Wert[[:space:]]*'$_name'[[:space:]]*'\(.*\)'[[:space:]]*\$/\1/p" \
                     "$ZIEL/team.config.ps1" | head -1)"
            [ -n "$_wert" ] && eval "$_name=\$_wert"
        done
        unset _name _wert
    fi
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
    gruen "  ✓ Projektwerte aus $KONF_QUELLE gelesen (Projekt: $PROJEKT)"

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
            NAME="$(basename "$f")"
            # BL-154: Hier stand eine ABSCHRIFT der Entrypoints — 24 Namen,
            # von Hand gepflegt. Sie war ab dem naechsten neuen Entrypoint
            # falsch, und zwar auf die unangenehme Art: Das Kit meldete seine
            # EIGENE Datei als "ungeprueften Projektcode". Eine Warnung, die
            # in jedem gruenen Projekt erscheint, erzieht zum Wegsehen
            # (BL-14) — und genau daneben stand der Hinweis auf echten
            # Wurzel-Code, den man dann mit uebersieht.
            #
            # Aufgefallen beim Einbau von kit-melden.sh (BL-153): Der leere
            # Selbsttest-Ordner meldete plotzlich drei Dateien, und im
            # Bestandsprojekt verschwand `main.py` hinter ihnen.
            #
            # Gefragt wird jetzt das Kit selbst: Was in bash/entry/ oder
            # pwsh/entry/ liegt, ist ein Entrypoint des Kits. Das kann nicht
            # veralten, weil es keine zweite Liste mehr gibt.
            if [ -e "$KIT/bash/entry/$NAME" ] || [ -e "$KIT/pwsh/entry/$NAME" ]; then
                continue
            fi
            case "$NAME" in
                *.md|LICENSE*|Makefile|*.toml|*.cfg|*.ini|*.txt|*.json|*.yaml|*.yml) ;;
                *.*) WURZEL_CODE="$WURZEL_CODE $NAME" ;;
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
        COMMIT_ENTSCHEID="Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Stakeholder führt sie aus."
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
        #
        # Zwei Ausnahmen, beide aus demselben Grund: Briefings UND TEAM.md
        # werden nach dem Kopieren gerendert. Ihre installierte Fassung weicht
        # deshalb IMMER von der Kit-Fassung ab — die Platzhalter sind dort
        # gefuellt. Ein Warner, der bei jedem Lauf dieselben Dateien meldet,
        # erzieht dazu, ihn zu ueberlesen; dann geht der echte Fund darin unter
        # (Kit-BL-164).
        case "$rel" in
            team/prompts/*|TEAM.md) ;;
            *) [ -e "$ziel" ] && ! cmp -s "$quelle" "$ziel" \
                   && ABWEICHEND="$ABWEICHEND $rel" ;;
        esac
        cp "$quelle" "$ziel"; chmod "$modus" "$ziel"
        GESCHRIEBEN=$((GESCHRIEBEN + 1))
    }
    fuelle_abs() {
        local datei="$1"
        [ -f "$datei" ] || return 0
        # Die letzten vier kamen mit BL-119 dazu. Sie fehlten hier, solange
        # der Update-Pfad nur BESTEHENDE Dateien nachrenderte — team.config.*
        # fasst er ja nicht an. Seit er eine abgewaehlte Bahn zurueckholen
        # kann, ERZEUGT er team.config.ps1, und dann zaehlt jeder Platzhalter:
        # vier ungefuellte blieben stehen und die Datei war halb fertig.
        "$PYTHON" - "$datei" "$PROJEKT" "$PRODUKTIVCODE" "$TEST_ORDNER" "$PLAN_ORDNER" \
                           "$SMOKE_TEST" "$TECH_STACK" "$DEPLOY" "$DEPLOY_AUSNAHMEN" \
                           "$DOMAENEN" "$COMMIT_ENTSCHEID" \
                           "${TEAM_WEITERER_CODE:-}" "${TEAM_TEST_ORDNER_BESTAND:-}" \
                           "${TEAM_PLAN_ORDNER_BESTAND:-}" "$PYTHON" \
                           "$BAHN_RUF" "$BAHN_ENDUNG" "$BAHN_KONFIG" \
                           "$BAHN_LIB" "$BAHN_REDTEAM" "$KIT" <<'PY'
import sys, pathlib
(d, projekt, prod, test, plan, smoke, stack, deploy, ausn,
 domaenen, commit, weiterer, test_bestand, plan_bestand,
 python_name, bahn_ruf, bahn_endung, bahn_konfig,
 bahn_lib, bahn_redteam, kit_pfad) = sys.argv[1:22]
# BL-113: siehe die Begruendung bei fuelle() weiter unten. Die Regel steht
# hier ein zweites Mal, weil der Update-Pfad eine eigene Fuell-Routine hat —
# und ein Update, das die Kodierung verliert, ist genau der Fall, in dem ein
# bisher laufendes Projekt ploetzlich nicht mehr startet.
p = pathlib.Path(d); t = p.read_text(encoding="utf-8-sig")
for a, b in [("{{PROJEKTNAME}}", projekt), ("{{PRODUKTIVCODE}}", prod),
             ("{{TEST_ORDNER}}", test), ("{{PLAN_ORDNER}}", plan.rstrip("/")),
             ("{{BEUTEBUCH}}", plan.rstrip("/") + "/beutebuch.md"),
             ("{{CHANGELOG}}", "CHANGELOG.md"),
             ("{{FIX_PRAEFIX}}", "fix(uat)"), ("{{FEAT_PRAEFIX}}", "feat"),
             # BL-149: ZWEI Platzhalter fuer einen Wert, und der Unterschied
             # ist der Unterschied zwischen Prosa und Konfiguration.
             #
             # {{SMOKE_TEST}} steht in Regeltexten (CLAUDE.md, TEAM.md,
             # roadmap-skizzen, Ralphs Briefing). Dort ist der TODO-Satz genau
             # richtig: Er sagt einem Menschen, was noch fehlt.
             #
             # {{SMOKE_TEST_KONFIG}} steht NUR in team.config.*, und dort war
             # derselbe Satz ein Schaden. Die Weichen der Bibliothek
             # unterscheiden "konfiguriert" von "nicht konfiguriert" ueber
             # leer/nicht-leer — ein nicht-leerer Platzhalter war fuer sie ein
             # KONFIGURIERTER Befehl. Folge in Kaskade 1 JEDES Projekts: Die
             # Rollen bekamen "Smoke-Test ausfuehren: TODO: noch keiner …" in
             # den Prompt, das Red Team ein Bash(TODO …) in die Allowlist, und
             # die Selbstpruefung fuehrte den Satz WOERTLICH aus (Exit 127,
             # "ist ROT"). Getroffen wurde ausschliesslich der Erstlauf — die
             # Lage mit der geringsten Projekterfahrung.
             #
             # Dieselbe Bauart wie {{WEITERER_CODE}} weiter unten: Ein
             # Platzhalter, der leer werden darf, gehoert in keine Prosa.
             ("{{SMOKE_TEST}}", smoke or "TODO: noch keiner — Stufe 1 der ersten Kaskade"),
             ("{{SMOKE_TEST_KONFIG}}", smoke),
             ("{{TECH_STACK}}", stack), ("{{DEPLOY}}", deploy),
             ("{{DEPLOY_AUSNAHMEN}}", ausn), ("{{DOMAENEN}}", domaenen),
             ("{{COMMIT_ENTSCHEID}}", commit),
             # BL-131: was auf DIESER Maschine wirklich antwortet — nicht
             # der Name, von dem die Bahn annimmt, sie laufe unter Linux.
             ("{{PYTHON}}", python_name),
             ("{{WEITERER_CODE}}", weiterer),
             ("{{TEST_BESTAND}}", test_bestand),
             ("{{PLAN_BESTAND}}", plan_bestand),
             # BL-139: die bahnabhaengigen Pfade. In einer einbahnigen Ablage
             # nannte der Regeltext sonst Dateien, die es dort nicht gibt.
             ("{{RUF}}", bahn_ruf), ("{{ENDUNG}}", bahn_endung),
             ("{{KONFIG}}", bahn_konfig), ("{{LIB}}", bahn_lib),
             ("{{REDTEAM}}", bahn_redteam),
             # BL-153: Wo das Kit auf DIESER Maschine liegt. Stand bis einschliesslich 2.12.0
             # als ~/Source/team-kit in der Prosa und zeigte damit ueberall
             # dorthin, wo der Autor geklont hatte. Steht nur in team.config.*;
             # das Werkzeug kann ohne ihn arbeiten, aber nicht ohne Suchen.
             ("{{KIT_PFAD}}", kit_pfad)]:
    t = t.replace(a, b)
# BL-137: schreiben OHNE Uebersetzung der Zeilenenden.
#
# `write_text()` oeffnet im Textmodus mit `newline=None`, und der uebersetzt
# unter Windows JEDES "\n" in "\r\n" — im ganzen Text, nicht nur an den
# ersetzten Stellen, denn `fuelle()` liest die Datei ganz und schreibt sie
# ganz zurueck. Gemessen an einer frischen Installation unter Git for
# Windows: team.config.sh 181 Wagenruecklaeufe, team.config.ps1 157, jedes
# Rollen-Briefing 33. Betroffen war ausschliesslich, was hier durchlief;
# was nur kopiert wurde, blieb heil.
#
# `p.open(..., newline="")` und nicht `write_text(..., newline=...)`:
# Letzteres gibt es erst ab Python 3.10, das Kit verlangt 3.8.
with p.open("w", newline="",
            encoding=("utf-8-sig" if p.suffix in (".ps1", ".psm1")
                      else "utf-8")) as fh:
    fh.write(t)
PY
    }
    fuelle() { fuelle_abs "$ZIEL/$1"; }

    # Entrypoints — team.config.sh UND team.config.ps1 sind AUSGENOMMEN: sie
    # tragen die Projektwerte (Smoke-Test!) und sind damit Projektdatum, nicht
    # Infrastruktur. Beide Bahnen werden aktualisiert; ein Projekt soll nach
    # einem Update nicht auf einer Haelfte veralten.
    for f in "$KIT"/bash/entry/*.sh "$KIT"/pwsh/entry/*.ps1 "$KIT"/pwsh/entry/*.cmd; do
        [ -e "$f" ] || continue
        case "$(basename "$f")" in team.config.sh|team.config.ps1) continue ;; esac
        bahn_abgewaehlt "$f" && continue
        kopiere "$f" "$(basename "$f")" 755
    done
    for f in "$KIT/bash/lib.sh" "$KIT/bash/redteam.sh"; do
        bahn_abgewaehlt "$f" && continue
        kopiere "$f" "team/$(basename "$f")" 755
    done
    # Der PowerShell-Kern gehoert zur Infrastruktur wie lib.sh. Faende er hier
    # keine Erwaehnung, liefe ein Projekt nach `--update` auf einer Haelfte
    # veraltet weiter — und die Gleichstandspruefung in kit-test.sh (10/10)
    # meldete es erst hinterher.
    for f in "$KIT/pwsh/lib.psm1" "$KIT/pwsh/redteam.ps1"; do
        [ -e "$f" ] || continue
        bahn_abgewaehlt "$f" && continue
        kopiere "$f" "team/$(basename "$f")" 755
    done

    # BL-119, die Gegenprobe zum Abwahl-Schalter: Ein Update OHNE Schalter
    # macht das Projekt wieder vollstaendig — sonst waere `--nur-bash` eine
    # Einbahnstrasse, und genau daran ist der Schalter beim ersten Versuch
    # gescheitert. Der Haken sitzt an einer Stelle, die man leicht uebersieht:
    # Die Entrypoints kommen zurueck, die KONFIGURATION nicht. Ein Update
    # fasst team.config.* grundsaetzlich nicht an (Projektdaten, siehe unten)
    # — richtig, solange sie DA ist. Fehlt sie, ist "nicht anfassen" kein
    # Schutz mehr, sondern eine halbe Bahn: ralph.ps1 laege da und faende
    # keine Werte.
    #
    # Erzeugt wird sie aus den Werten der VORHANDENEN Konfiguration (oben
    # gesourct), nicht aus den Defaults — sonst bekaeme die zurueckgeholte
    # Bahn andere Pfade als die, die schon laeuft. Das ist dieselbe Quelle
    # wie bei der Erstinstallation, nur spaeter gelesen.
    for paar in "bash/entry/team.config.sh:team.config.sh" \
                "pwsh/entry/team.config.ps1:team.config.ps1"; do
        quelle="$KIT/${paar%%:*}"; name="${paar##*:}"
        [ -e "$quelle" ] || continue
        bahn_abgewaehlt "$quelle" && continue
        [ -e "$ZIEL/$name" ] && continue
        kopiere "$quelle" "$name" 755
        fuelle "$name"
        gelb "  ! $name fehlte und ist neu erzeugt worden — aus den Werten von"
        echo  "    team.config.sh, nicht aus den Auslieferungswerten. Bitte"
        echo  "    gegenlesen: \$EDITOR \"$ZIEL/$name\""
    done
    for f in "$KIT"/geteilt/tools/*.py;   do kopiere "$f" "team/tools/$(basename "$f")" 755; done
    for f in "$KIT"/geteilt/prompts/*.md; do kopiere "$f" "team/prompts/$(basename "$f")"; done
    # BL-12: Hier stand einmal ein pauschales rm auf team/tests/test_*.py, um
    # umbenannte Kit-Tests einer Altversion loszuwerden. Das hat im Feld einen
    # projekteigenen Infrastruktur-Test geloescht — team/tests/ ist eben NICHT
    # exklusiv Kit-Gebiet, sobald ein Projekt eine Luecke im Team selbst
    # schliesst. Jetzt wird nichts geloescht; Unbekanntes wird gemeldet.
    for f in "$KIT"/geteilt/tests/test_*.py; do kopiere "$f" "team/tests/$(basename "$f")"; done
    # conftest.py ist KEIN Test, aber ohne sie laeuft keiner der Tests, die den
    # Doppelbahn-Harnisch nehmen (`from conftest import …`). Sie faellt durch
    # das test_*.py-Muster und muss ausdruecklich mitkopiert werden — sonst
    # bricht die Installation an einem ModuleNotFoundError, den niemand mit
    # dem Installer in Verbindung bringt.
    kopiere "$KIT/geteilt/tests/conftest.py" "team/tests/conftest.py"
    FREMDE_TESTS=""
    for f in "$ZIEL"/team/tests/test_*.py; do
        [ -e "$f" ] || continue
        [ -e "$KIT/geteilt/tests/$(basename "$f")" ] || \
            FREMDE_TESTS="$FREMDE_TESTS $(basename "$f")"
    done
    for d in "$ZIEL"/team/prompts/*.md; do fuelle "team/prompts/$(basename "$d")"; done

    # Kit-BL-164: TEAM.md ist Kit-Doku, keine Projektdatei — und fiel bis
    # hierher durch JEDES Update. Geschrieben wurde sie nur bei der
    # Erstinstallation; in der Liste "Unangetastet geblieben (Projektdaten)"
    # weiter unten steht sie auch nicht. Sie fiel zwischen beide Listen, und
    # das faellt nicht auf: Eine veraltete Anleitung sieht aus wie eine
    # Anleitung.
    #
    # Der Schaden ist zweigeteilt, und der zweite Teil ist der schwerere:
    #
    #   1. Die Bedienungsanleitung eines aktualisierten Projekts bleibt auf dem
    #      Stand des Einzugstags. Exit-Codes, Befehle, Fehlersuche — alles, was
    #      das Kit seither gelernt hat, kommt dort nie an.
    #   2. In einer EINBAHNIGEN Ablage nennt die alte Fassung die ABGEWAEHLTE
    #      Bahn. Im Feld standen in einer --nur-pwsh-Installation 15 tote
    #      .sh-Pfade in TEAM.md; der Text schickte jeden Leser an Dateien, die
    #      es dort nicht gibt. Das ist genau der Befund, den BL-139 fuer die
    #      Vorlagen abgestellt hat — TEAM.md blieb uebrig, weil die Reparatur
    #      am Rendern ansetzte und diese Datei nie neu gerendert wurde.
    #
    # CLAUDE.md bleibt bewusst aussen vor. Die traegt Projektarbeit — gefuellte
    # TODO-Stellen, projekteigene Regeln — und gehoert zu den Projektdaten.
    # TEAM.md traegt keine: Sie wird gerendert und sonst nicht angefasst.
    kopiere "$KIT/bootstrap/TEAM.md" "TEAM.md"
    fuelle "TEAM.md"

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

    # BL-136: dieselbe Bauart, dieselbe Begruendung. Ein Projekt ohne diese
    # Regel checkt seine .sh unter Windows mit CRLF aus, und jeder Aufruf
    # endet mit "bad interpreter" — weit weg von der Ursache.
    kopf ".gitattributes gegen die Vorlage (BL-136)"
    gitattributes_abgleich melden

    # BL-133: dieselbe Bauart wie die Zeile darueber — was --update nicht
    # anfasst, muss es trotzdem ANSEHEN. Ein Interpretername, der auf
    # dieser Maschine nicht startet, macht den Kostenpfad tot und die
    # Anzeige leer, ohne je einen Fehler zu melden.
    kopf "Interpreter der Team-Werkzeuge (BL-131/BL-133)"
    python_abgleich || true

    # BL-133: Die Abwahl einer Bahn wirkt bisher nur bei der ERSTinstallation.
    # `bahn_abgewaehlt` laesst den Installer die Dateien der anderen Bahn
    # ueberspringen — was schon daliegt, bleibt liegen. Fuer ein bestehendes
    # zweibahniges Projekt heisst `--nur-pwsh` beim Update also: "ab jetzt
    # nicht mehr aktualisieren", nicht "weg damit". Der Unterschied ist
    # folgenreich: Die Testsuite entscheidet an der ANWESENHEIT der Dateien,
    # welche Bahn sie faehrt (conftest: bahnen_in_der_ablage), und faehrt
    # damit weiter eine Bahn, die der Anwender gerade abgewaehlt hat — mit
    # einer Bibliothek, die von diesem Update an veraltet.
    #
    # Geloescht wird trotzdem nichts. Das ist die Lehre aus BL-12: Ein
    # pauschales rm des Installers hat im Feld einen projekteigenen Test
    # mitgenommen. Genannt wird es, mit dem Befehl daneben.
    if [ -n "$NUR_BAHN" ]; then
        # Gezaehlt wird nur, was das KIT ausliefert (BL-147, dieselbe
        # Ueberlegung wie bei der Erkennung): Ein projekteigenes deploy.ps1
        # gehoert nicht der abgewaehlten Bahn, und ein "git rm" darauf waere
        # ein Rat, der fremde Arbeit loescht.
        RESTE=""
        for f in "$KIT"/bash/entry/*.sh "$KIT"/pwsh/entry/*.ps1 "$KIT"/pwsh/entry/*.cmd; do
            [ -e "$f" ] || continue
            bahn_abgewaehlt "$f" || continue
            [ -f "$ZIEL/$(basename "$f")" ] && RESTE="$RESTE $(basename "$f")"
        done
        for f in "$KIT/bash/lib.sh" "$KIT/bash/redteam.sh" \
                 "$KIT/pwsh/lib.psm1" "$KIT/pwsh/redteam.ps1"; do
            [ -e "$f" ] || continue
            bahn_abgewaehlt "$f" || continue
            [ -f "$ZIEL/team/$(basename "$f")" ] && RESTE="$RESTE team/$(basename "$f")"
        done
        if [ -n "$RESTE" ]; then
            kopf "Abgewaehlte Bahn liegt noch da (BL-119/BL-133)"
            echo "  --nur-$NUR_BAHN hat diese Dateien nicht mehr aktualisiert,"
            echo "  aber auch nicht entfernt:"
            for r in $RESTE; do echo "    · $r"; done
            gelb "  Solange sie liegen, faehrt ./team-test die andere Bahn weiter —"
            gelb "  mit einer Bibliothek, die ab jetzt veraltet. Entfernen (bewusst"
            gelb "  nicht automatisch, Lehre BL-12):"
            gelb "    git -C \"$ZIEL\" rm$(printf ' %s' $RESTE)"
        fi
    fi

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
        # BL-137: --strip-trailing-cr, weil der Vergleich sonst am Zeilenende
        # haengenbleibt statt am Inhalt. Die frisch gerenderte Fassung traegt
        # seit diesem Fix LF; eine VOR dem Fix unter Windows installierte
        # traegt CRLF. Ohne die Flagge meldete dieser Abgleich dann JEDE Zeile
        # als abgewichen und stellte den Anwender vor eine Inhaltsaenderung,
        # die keine ist. Ein stiller Fehler, gegen einen lauten Fehlalarm
        # getauscht, ist kein Fortschritt (Bauart BL-14).
        #
        # Die Flagge steht auch im Befehl, den die Meldung zum Nachsehen
        # nennt: Wer dort ein anderes Bild sieht als der Installer, sucht den
        # Fehler an der falschen Stelle.
        if ! diff --strip-trailing-cr -q "$gerendert" "$ziel" >/dev/null 2>&1; then
            zeilen="$(diff --strip-trailing-cr "$gerendert" "$ziel" \
                      | grep -c '^[<>]' || true)"
            echo "  ! $name weicht von der Kit-Fassung ab ($zeilen Zeilen)"
            echo "      diff --strip-trailing-cr -u \"$gerendert\" \"$ziel\""
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
    # BL-128: leerer Glob -> bash reicht das Muster durch (Begruendung unten
    # beim Selbsttest der Erstinstallation).
    SH_ANZAHL=0
    for f in "$ZIEL"/*.sh; do
        [ -e "$f" ] || continue
        SH_ANZAHL=$((SH_ANZAHL + 1))
        bash -n "$f" || { rot "  ✗ Syntaxfehler: $(basename "$f")"; FEHLER=1; }
    done
    if [ "$SH_ANZAHL" -eq 0 ]; then
        gruen "  ✓ keine .sh zu pruefen (Bash-Bahn abgewaehlt)"
    elif [ "$FEHLER" -eq 0 ]; then
        gruen "  ✓ Alle Shell-Skripte syntaktisch korrekt"
    fi
    # Der Selbsttest muss laufen wie ./team-test.sh beim Anwender: OHNE die
    # TEAM_*-Variablen, die dieses Skript beim Sourcen der Config geerbt hat.
    # Sonst gilt z. B. TEAM_DOMAENEN des Projekts auch fuer die Fixtures, und
    # jeder Test mit domaene="team" scheitert an einem Projekt, das diese
    # Domaene gar nicht fuehrt — ein Fehlalarm, der nur im Update auftraete.
    if PYTEST_AUFRUF="$(team_pytest)"; then
        if (cd "$ZIEL" && unset "${!TEAM_@}" && pytest_mitschnitt /tmp/team-update-pytest.log $PYTEST_AUFRUF); then
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
    gelb "    bash $KIT/bash/scripts/team-auth-setup.sh"
    gelb "    (oder gleich die ganze Maschine: bash $KIT/bash/kit-einrichten.sh)"
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

# wurzel_ordner: die Ordner, die im Zielprojekt schon existieren. Abschreibhilfe
# fuer den Fall, dass der eingegebene Name ein Tippfehler ist (BL-121). Dieselbe
# Erwaegung wie bei kandidaten_ausserhalb(): Eine Liste zum Abschreiben schlaegt
# jede Erklaerung.
wurzel_ordner() {
    local eintrag name ausgabe="" n=0
    for eintrag in "$ZIEL"/*/; do
        [ -d "$eintrag" ] || continue
        name="$(basename "$eintrag")"
        case "$name" in
            team|node_modules|__pycache__|venv|.venv|dist|build|target|.*) continue ;;
        esac
        n=$((n + 1))
        [ "$n" -le 12 ] && ausgabe="$ausgabe ${name}/"
    done
    [ "$n" -gt 12 ] && ausgabe="$ausgabe …"
    printf '%s' "${ausgabe# }"
}

# produktivcode_anlegen: legt den Ordner an und sichert ihn gegen den naechsten
# Commit ab. Ein LEERER Ordner ist fuer Git nicht vorhanden — und der Schritt
# direkt nach der Installation heisst "Committen, VOR dem ersten Guard-Lauf".
# Ohne Platzhalter waere der Ordner nach dem naechsten Klon wieder weg und der
# Fehler von vorn da. Dieselbe Loesung wie bei ermittlungsakten/ (BL-121).
produktivcode_anlegen() {
    mkdir -p "$ZIEL/${PRODUKTIVCODE%/}"
    if [ -z "$(ls -A "$ZIEL/${PRODUKTIVCODE%/}" 2>/dev/null)" ]; then
        : > "$ZIEL/${PRODUKTIVCODE%/}/.gitkeep"
        return 0
    fi
    return 1
}

# produktivcode_sichern: Guard-Grenze, Pruefumfang und die Briefings der drei
# Read-Only-Rollen zeigen ab hier auf ${PRODUKTIVCODE}. Ein Name, den es nicht
# gibt, ist deshalb kein Schoenheitsfehler: Das Red Team prueft dann einen
# leeren Suchraum, und der erste Bericht meldet "sauber" ueber nichts. Vorher
# wurde der Name nur eingesetzt, nie geprueft und nie angelegt (BL-121).
#
# Im BESTAND ist ein nicht vorhandener Ordner eher ein Tippfehler als ein neues
# Projekt. Deshalb wird nicht wortlos angelegt, sondern erst gezeigt, was da
# ist — und angelegt wird trotzdem, wenn der Name so gewollt war.
produktivcode_sichern() {
    local vorhandene neu
    while :; do
        if [ -d "$ZIEL/${PRODUKTIVCODE%/}" ]; then
            gruen "  ✓ Produktivcode-Ordner ${PRODUKTIVCODE} ist vorhanden."
            return 0
        fi
        if [ "$INTERAKTIV" -eq 0 ]; then
            if produktivcode_anlegen; then
                gelb "  ! ${PRODUKTIVCODE} gab es nicht — angelegt, mit .gitkeep."
            else
                gelb "  ! ${PRODUKTIVCODE} gab es nicht — angelegt."
            fi
            gelb "    Nicht-interaktiv: ohne Rueckfrage, aber nicht ohne Ansage."
            return 0
        fi
        gelb "  ! Den Ordner '${PRODUKTIVCODE}' gibt es in diesem Projekt nicht."
        vorhandene="$(wurzel_ordner)"
        if [ -n "$vorhandene" ]; then
            echo "    Hier liegen: $vorhandene"
            echo "    Ist der gesuchte dabei, tipp ihn ab — ein Tippfehler faellt sonst"
            echo "    erst auf, wenn das Red Team "sauber" ueber einen leeren Ordner meldet."
        else
            echo "    Das Projekt ist noch leer. Bei einem neuen Projekt ist das der Normalfall."
        fi
        read -r -p "    Enter = '${PRODUKTIVCODE}' anlegen, oder anderen Namen eingeben: " neu || true
        if [ -z "$neu" ]; then
            if produktivcode_anlegen; then
                gruen "  ✓ ${PRODUKTIVCODE} angelegt — mit .gitkeep, sonst faellt der leere"
                gruen "    Ordner bei dem Commit weg, den der naechste Schritt verlangt."
            else
                gruen "  ✓ ${PRODUKTIVCODE} angelegt."
            fi
            return 0
        fi
        PRODUKTIVCODE="${neu%/}/"
    done
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
produktivcode_sichern

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
# und "schreib hierhin" — beobachtet an Feld C, wo tests/ in beiden
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
# Bestandsdokumente. Beobachtet an Feld C: zehn fachliche Dokumente
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
    *)          COMMIT_ENTSCHEID="Ich committe NICHT selbst — ich liefere die fertigen Commit-Befehle zum Kopieren, der Stakeholder führt sie aus." ;;
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
    "$PYTHON" - "$datei" "$PROJEKT" "$PRODUKTIVCODE" "$TEST_ORDNER" "$PLAN_ORDNER" \
                       "$SMOKE_TEST" "$TECH_STACK" "$DEPLOY" "$DEPLOY_AUSNAHMEN" \
                       "$DOMAENEN" "$COMMIT_ENTSCHEID" "$WEITERER_CODE" \
                       "$TEST_ORDNER_BESTAND" "$PLAN_ORDNER_BESTAND" "$PYTHON" \
                       "$BAHN_RUF" "$BAHN_ENDUNG" "$BAHN_KONFIG" \
                       "$BAHN_LIB" "$BAHN_REDTEAM" "$KIT" <<'PY'
import sys, pathlib
(d, projekt, prod, test, plan, smoke, stack, deploy, ausn,
 domaenen, commit, weiterer, test_bestand, plan_bestand,
 python_name, bahn_ruf, bahn_endung, bahn_konfig,
 bahn_lib, bahn_redteam, kit_pfad) = sys.argv[1:22]
# BL-113: utf-8-sig liest ein vorhandenes BOM weg, statt es als ﻿ mitten
# in den Text zu nehmen. Ob beim Schreiben wieder eines hinkommt, entscheidet
# unten allein die Endung — nicht der Zufall, was in der Vorlage stand.
p = pathlib.Path(d); t = p.read_text(encoding="utf-8-sig")
for a, b in [("{{PROJEKTNAME}}", projekt), ("{{PRODUKTIVCODE}}", prod),
             ("{{TEST_ORDNER}}", test), ("{{PLAN_ORDNER}}", plan.rstrip("/")),
             ("{{BEUTEBUCH}}", plan.rstrip("/") + "/beutebuch.md"),
             ("{{CHANGELOG}}", "CHANGELOG.md"),
             ("{{FIX_PRAEFIX}}", "fix(uat)"), ("{{FEAT_PRAEFIX}}", "feat"),
             # BL-149: siehe die Begruendung in der Fuell-Routine des
             # Update-Pfads weiter oben. {{SMOKE_TEST}} ist Prosa und darf den
             # TODO-Satz tragen; {{SMOKE_TEST_KONFIG}} steht nur in
             # team.config.* und muss LEER bleiben, weil die Weichen der
             # Bibliothek an leer/nicht-leer haengen.
             ("{{SMOKE_TEST}}", smoke or "TODO: noch keiner — Stufe 1 der ersten Kaskade"),
             ("{{SMOKE_TEST_KONFIG}}", smoke),
             ("{{TECH_STACK}}", stack), ("{{DEPLOY}}", deploy),
             ("{{DEPLOY_AUSNAHMEN}}", ausn), ("{{DOMAENEN}}", domaenen),
             ("{{COMMIT_ENTSCHEID}}", commit),
             # BL-131: In BEIDEN Konfigurationen. Unter Windows heisst der
             # Interpreter je nach Installation python/py, und seit team.config.sh
             # denselben Platzhalter traegt, gilt das fuer beide Bahnen.
             ("{{PYTHON}}", python_name),
             # BL-52/BL-51: leer ist der Normalfall — die Platzhalter stehen nur
             # in team.config.sh, damit eine leere Ersetzung nirgends Prosa
             # zerreisst.
             ("{{WEITERER_CODE}}", weiterer),
             ("{{TEST_BESTAND}}", test_bestand),
             ("{{PLAN_BESTAND}}", plan_bestand),
             # BL-139: die bahnabhaengigen Pfade. In einer einbahnigen Ablage
             # nannte der Regeltext sonst Dateien, die es dort nicht gibt.
             ("{{RUF}}", bahn_ruf), ("{{ENDUNG}}", bahn_endung),
             ("{{KONFIG}}", bahn_konfig), ("{{LIB}}", bahn_lib),
             ("{{REDTEAM}}", bahn_redteam),
             # BL-153: Wo das Kit auf DIESER Maschine liegt. Stand bis einschliesslich 2.12.0
             # als ~/Source/team-kit in der Prosa und zeigte damit ueberall
             # dorthin, wo der Autor geklont hatte. Steht nur in team.config.*;
             # das Werkzeug kann ohne ihn arbeiten, aber nicht ohne Suchen.
             ("{{KIT_PFAD}}", kit_pfad)]:
    t = t.replace(a, b)
# BL-113 — die Kodierungsregel des Kits, zeichengleich mit Team-Kodierung in
# install.ps1: PowerShell-Quelltext MIT BOM, alles andere OHNE.
#
# OHNE, weil ein BOM vor einer Shebang-Zeile aus ihr Zeichensalat macht und
# weil Pythons json.load darueber abbricht (kosten.py zaehlte eine so
# verdorbene Datei stillschweigend als 0.0000).
#
# MIT, weil Windows PowerShell 5.1 eine Datei OHNE BOM nicht als UTF-8 liest,
# sondern in der ANSI-Codepage. Der Geviertstrich wird dabei zu â€", dessen
# letztes Zeichen U+201D ist — fuer PowerShell eine echte Stringgrenze. Jeder
# Gedankenstrich schliesst dann seine Zeichenkette mitten im Satz, und die
# Datei stirbt beim Parsen, BEVOR die Versionspruefung erklaeren kann, dass
# hier pwsh 7 gebraucht wird.
#
# Dass dieser Installer unter Linux laeuft, aendert daran nichts: Er schreibt
# team.config.ps1 fuer eine Maschine, auf der er selbst nie sein wird.
# BL-137, dieselbe Begruendung wie in der Fuell-Routine der Erstinstallation:
# `newline=""`, weil der Textmodus unter Windows sonst jedes "\n" uebersetzt.
# Der Update-Pfad hat seine eigene Routine und braucht deshalb seine eigene
# Zeile — genau die Doppelung, die schon bei BL-113 hier stand.
with p.open("w", newline="",
            encoding=("utf-8-sig" if p.suffix in (".ps1", ".psm1")
                      else "utf-8")) as fh:
    fh.write(t)
PY
}

# Entrypoints in die Repo-Wurzel — der Stakeholder tippt sie direkt
# (Ablage-Konvention aus dem Feld: Einstiegspunkte sichtbar oben).
# BEIDE Bahnen werden installiert, auch wenn dieser Installer unter Linux
# laeuft und den Windows-Teil hier niemand braucht. Der Grund ist die
# Zusicherung, auf der die pwsh-Bahn ruht: team.config.sh und
# team.config.ps1 sind ZWEI GENERATE EINER QUELLE (denselben neun Antworten),
# keine zwei gepflegten Dateien. Installierte nur install.ps1 den
# PowerShell-Teil, haette ein auf Linux eingerichtetes Projekt unter Windows
# keine Konfiguration — und jemand schriebe sie von Hand. Genau dort faengt
# Drift an. Das Projekt ist damit von beiden Systemen aus bedienbar, ohne dass
# irgendwer nachinstalliert.
for f in "$KIT"/bash/entry/*.sh "$KIT"/pwsh/entry/*.ps1 "$KIT"/pwsh/entry/*.cmd; do
    [ -e "$f" ] || continue
    bahn_abgewaehlt "$f" && continue
    kopiere "$f" "$(basename "$f")" 755
done
# Alles Aufgerufene in den team/-Namensraum. Damit berührt das Kit die
# Konventionen des Projekts nicht: tests/ und scripts/ bleiben dem Projekt,
# und kein stack-fremder Code landet in deinen Ordnern.
for f in "$KIT/bash/lib.sh" "$KIT/bash/redteam.sh" \
         "$KIT/pwsh/lib.psm1" "$KIT/pwsh/redteam.ps1"; do
    [ -e "$f" ] || continue
    bahn_abgewaehlt "$f" && continue
    kopiere "$f" "team/$(basename "$f")" 755
done
for f in "$KIT"/geteilt/tools/*.py;      do kopiere "$f" "team/tools/$(basename "$f")" 755; done
for f in "$KIT"/geteilt/prompts/*.md;    do kopiere "$f" "team/prompts/$(basename "$f")"; done
for f in "$KIT"/geteilt/tests/test_*.py; do kopiere "$f" "team/tests/$(basename "$f")"; done
# Siehe Begruendung im Update-Pfad: kein Test, aber Voraussetzung mehrerer.
kopiere "$KIT/geteilt/tests/conftest.py" "team/tests/conftest.py"
gruen "  ✓ Entrypoints (Wurzel) + team/ (lib, tools, prompts, $(ls "$KIT"/geteilt/tests/test_*.py | wc -l) Tests)"
if [ -n "$NUR_BAHN" ]; then
    ANDERE="pwsh"; [ "$NUR_BAHN" = "pwsh" ] && ANDERE="bash"
    gelb "  ! Nur die ${NUR_BAHN}-Bahn installiert — die ${ANDERE}-Bahn fehlt in"
    echo  "    diesem Projekt, samt ihrer Konfiguration. Das ist deine Abwahl,"
    echo  "    kein Versehen des Installers."
    echo  "    Zurueckholen (macht das Projekt wieder vollstaendig):"
    echo  "      bash $KIT/bash/install.sh \"$ZIEL\" --update"
fi

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
gitattributes_abgleich ergaenzen

# ---------------------------------------------------------------- Selbsttest
kopf "Selbsttest"
FEHLER=0
# BL-128: Findet der Glob nichts, reicht bash das MUSTER selbst durch —
# `bash -n "$ZIEL/*.sh"` scheitert dann an einer Datei namens "*.sh" und der
# Selbsttest meldet "Syntaxfehler: *.sh" samt Exit 1. Genau das passiert in
# einer mit --nur-pwsh installierten Ablage: Dort GIBT es keine .sh, und das
# ist kein Defekt, sondern die Abwahl (BL-119). Ein Installer, der eine
# gelungene Installation als kaputt meldet, verbrennt das Vertrauen in
# jede weitere Meldung.
SH_ANZAHL=0
for f in "$ZIEL"/*.sh; do
    [ -e "$f" ] || continue
    SH_ANZAHL=$((SH_ANZAHL + 1))
    bash -n "$f" || { rot "  ✗ Syntaxfehler: $(basename "$f")"; FEHLER=1; }
done
if [ "$SH_ANZAHL" -eq 0 ]; then
    gruen "  ✓ keine .sh zu pruefen (Bash-Bahn abgewaehlt)"
elif [ "$FEHLER" -eq 0 ]; then
    gruen "  ✓ Alle Shell-Skripte syntaktisch korrekt"
fi

if "$PYTHON" -m py_compile "$ZIEL"/team/tools/*.py 2>/dev/null; then
    gruen "  ✓ Python-Werkzeuge kompilieren"
else
    rot "  ✗ Python-Werkzeuge fehlerhaft"; FEHLER=1
fi

if PYTEST_AUFRUF="$(team_pytest)"; then
    if (cd "$ZIEL" && pytest_mitschnitt /tmp/team-init-pytest.log $PYTEST_AUFRUF); then
        gruen "  ✓ Regressionstests grün ($(grep -oE '[0-9]+ passed' /tmp/team-init-pytest.log | head -1))"
    else
        gelb "  ! Regressionstests nicht vollständig grün — Log: /tmp/team-init-pytest.log"
        gelb "    $(tail -3 /tmp/team-init-pytest.log | head -1)"
    fi
else
    gelb "  · pytest nicht gefunden — Regressionstests übersprungen"
    gelb "    Gesucht als Modul (python3/python/py -m pytest) UND als Befehl im PATH."
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
# ------------------------------------------------- Der Launcher ausserhalb
# Das EINZIGE Stueck des Kits, von dem eine Kopie ausserhalb des Repos liegen
# kann: ~/.claude/scripts/team-init.sh. Eine Verknuepfung kann nicht veralten,
# eine Kopie schon — und sie meldet sich nicht von selbst, sondern behauptet
# eines Tages, das Kit sei nicht da. Genau so ist der Umzug auf bash/ im Feld
# aufgefallen: nicht durch eine Warnung, sondern durch einen Launcher, der
# nicht mehr lief.
#
# Geprueft wird bei JEDEM Install, weil das der Moment ist, in dem sich die
# Kit-Fassung aendert. GESCHRIEBEN wird hier nichts: Dieses Skript installiert
# ein Projekt, und ein Projekt-Installer, der ungefragt im Home-Verzeichnis
# aufraeumt, ist eine Ueberraschung, keine Hilfe. Repariert wird in
# kit-einrichten.sh — dem Skript, das fuer die MASCHINE zustaendig ist (A.12).
LAUNCHER="$HOME/.claude/scripts/team-init.sh"
if [ -e "$LAUNCHER" ] || [ -L "$LAUNCHER" ]; then
    if [ -L "$LAUNCHER" ] && [ ! -f "$LAUNCHER" ]; then
        echo
        gelb "Hinweis: ~/.claude/scripts/team-init.sh zeigt ins Leere"
        gelb "  ($(readlink "$LAUNCHER"))."
        gelb "  Wieder verknuepfen:  bash $KIT/bash/kit-einrichten.sh --verknuepfen"
    elif [ ! -L "$LAUNCHER" ] && ! grep -q 'INSTALLER_ORTE' "$LAUNCHER" 2>/dev/null; then
        echo
        gelb "Hinweis: ~/.claude/scripts/team-init.sh ist eine KOPIE aus einer"
        gelb "  aelteren Kit-Fassung, keine Verknuepfung. Sie kennt nur den"
        gelb "  damaligen Ort des Installers und schlaegt fehl, sobald er sich"
        gelb "  verschiebt — zuletzt beim Umzug auf bash/ und pwsh/."
        gelb "  Ersetzen (legt eine Sicherung daneben):"
        gelb "    bash $KIT/bash/kit-einrichten.sh --verknuepfen"
    fi
fi

exit $FEHLER

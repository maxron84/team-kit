#!/usr/bin/env bash
# Bahn: bash | Gegenstueck: kit-einrichten.ps1
# kit-einrichten.sh — die Vorflug-Prüfung zwischen `git clone` und `install.sh`.
#
# Aufruf:  bash kit-einrichten.sh [zielpfad] [--verknuepfen] [--auth]
#                                 [--nur-pruefen] [--nicht-interaktiv]
#
#   zielpfad            Projekt, in das das Team danach einziehen soll. Wird es
#                       angegeben und ist die Maschine grün, übergibt das Skript
#                       an install.sh — Klonen und Einbinden in einem Zug.
#   --verknuepfen       bash/scripts/team-init.sh und team-auth-setup.sh als
#                       SYMLINK unter ~/.claude/scripts/ ablegen (Kurzbefehl von
#                       überall, ohne zweite Kopie). Vorhandene echte Dateien
#                       werden nie überschrieben, nur gemeldet.
#   --auth              bash/scripts/team-auth-setup.sh mitlaufen lassen.
#   --nur-pruefen       Nur prüfen, nichts anfassen und nicht übergeben.
#   --nicht-interaktiv  Keine Rückfragen (dann wirken nur die Flags oben).
#
# WARUM ES DIESES SKRIPT GIBT
#
# install.sh prüft, was das ZIELPROJEKT braucht (Git-Repo, Auth, freie Ordner).
# Was die MASCHINE braucht, prüfte bisher niemand — es stand in der README und
# galt stillschweigend, weil das Kit bis dahin nur auf der Maschine lief, auf
# der es entstanden ist. Der Weg über einen frischen Klon, und erst recht über
# Windows mit WSL, hat drei Fallen, die alle dasselbe Muster haben: Sie sehen
# aus wie ein kaputtes Kit und sind keines.
#
#   1. CRLF. Git for Windows klont per Default mit core.autocrlf=true. Die
#      Skripte kommen mit \r an, und bash sucht einen Interpreter namens
#      "bash\r" ("bad interpreter"). Seit dieser Fassung hält .gitattributes
#      dagegen — die Prüfung bleibt, weil ein vor der Datei entstandener Klon
#      den Fehler weiter trägt.
#   2. Windows-Dateisystem. Ein Klon unter /mnt/c hängt an DrvFs: chmod +x
#      verpufft (ohne metadata-Mount), die Entrypoints sind nach der
#      Installation nicht ausführbar, und die Lock-Datei des Loops (flock)
#      steht auf einem Dateisystem, für das das Kit keine Zusicherung hat.
#   3. Fehlende Bordmittel. python3 und flock sind Abhängigkeiten der
#      TEAM-Infrastruktur, nicht des Projekts (README, Abschnitt "Grenzen").
#      Fehlt eines, fällt es erst mitten im ersten Lauf auf — also nachdem
#      Agentenzeit bezahlt wurde.
#
# Das Skript ruft KEINE Agenten-CLI auf und kostet daher nichts.
#
# Was hier Pflicht ist und was Beispiel: git, bash, python3 und flock sind
# Pflicht — ohne sie läuft die Mechanik nicht. Die Claude-CLI ist das heute
# erprobte Beispiel für ein Agenten-Werkzeug; fehlt sie, gibt es einen Hinweis
# und keinen Fehler. Dasselbe gilt für die IDE, nach der hier gar nicht erst
# gefragt wird. Siehe doku/einrichtung.md.
set -euo pipefail

# Seit der Bahn-Trennung: BAHN ist <kit>/bash, KIT die Wurzel des Kits.
BAHN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$(dirname "$BAHN")"
ZIEL=""
INTERAKTIV=1
VERKNUEPFEN=0
AUTH=0
NUR_PRUEFEN=0

for arg in "$@"; do
    case "$arg" in
        --verknuepfen)      VERKNUEPFEN=1 ;;
        --auth)             AUTH=1 ;;
        --nur-pruefen)      NUR_PRUEFEN=1 ;;
        --nicht-interaktiv) INTERAKTIV=0 ;;
        -h|--hilfe|--help)  sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        -*) echo "Unbekannte Option: $arg" >&2; exit 2 ;;
        *)  ZIEL="$arg" ;;
    esac
done
[ -t 0 ] || INTERAKTIV=0

rot()  { printf '\033[31m%s\033[0m\n' "$*"; }
gruen(){ printf '\033[32m%s\033[0m\n' "$*"; }
gelb() { printf '\033[33m%s\033[0m\n' "$*"; }
kopf() { printf '\n\033[1m%s\033[0m\n' "$*"; }

FEHLER=0
WARNUNGEN=0
fehler()  { rot  "  ✗ $1"; shift; for z in "$@"; do echo "      $z"; done; FEHLER=$((FEHLER+1)); }
warnung() { gelb "  ! $1"; shift; for z in "$@"; do echo "      $z"; done; WARNUNGEN=$((WARNUNGEN+1)); }
ok()      { gruen "  ✓ $1"; }

ja() {  # ja <frage> — nur interaktiv, Default nein
    [ "$INTERAKTIV" -eq 1 ] || return 1
    local antwort=""
    printf '  %s [j/N] ' "$1"
    read -r antwort || true
    case "$antwort" in [jJyY]*) return 0 ;; *) return 1 ;; esac
}

printf '\033[1m=== T.E.A.M.-Starterkit — Maschine einrichten ===\033[0m\n'
echo "  Kit: $KIT"

# ---------------------------------------------------------------- 1/5 Umgebung
kopf "1/5 — Umgebung"

UNTER_WSL=0
if [ -n "${WSL_DISTRO_NAME:-}" ] || { [ -r /proc/version ] && grep -qi microsoft /proc/version; }; then
    UNTER_WSL=1
fi

# BL-159: Auf welchem WIRT laeuft die bash-Bahn hier? Die Frage entscheidet
# ueber den SCHWEREGRAD zweier Befunde, nicht ueber ihren Inhalt.
#
# Die Zwei-Bahnen-Tabelle im README sagt es klar: "Bash-Bahn (Linux · WSL)"
# gegen "pwsh-Bahn (Windows ohne WSL)". Auf nativem Windows unter Git-Bash ist
# die bash-Bahn also die ZWEITE Wahl — und genau dort fehlt flock (Git for
# Windows liefert keines) und das Exec-Bit haelt auf NTFS nicht.
#
# Beides als FEHLER zu melden hiess: Das Kit erklaert eine Maschine fuer
# unbereit, auf der seine NATIVE Bahn tadellos laeuft, und schickt den
# Anwender an ein Paket (util-linux), das es fuer Git-Bash nicht gibt. Eine
# Abhilfe, die auf dieser Maschine nicht ausfuehrbar ist, ist keine — dieselbe
# Erwaegung wie bei BL-189, wo `Set-ExecutionPolicy -Scope CurrentUser` gegen
# eine Gruppenrichtlinie empfohlen wurde.
#
# Was NICHT passiert: Die Befunde verschwinden. Sie bleiben sichtbar, sie
# nennen ihre Folge, und sie nennen die Bahn, auf der es die Folge nicht gibt.
# Ein Befund, der zur Warnung wird, muss mehr erklaeren als einer, der ein
# Fehler bleibt — nicht weniger.
WIRT="posix"
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) WIRT="windows" ;;
esac

case "$(uname -s)" in
    Linux)
        if [ "$UNTER_WSL" -eq 1 ]; then
            # WSL1 und WSL2 sind zwei verschiedene Maschinen: WSL1 übersetzt
            # Syscalls (kein echter Kernel), WSL2 ist eine VM mit ext4. Die
            # Zusicherungen des Kits hängen an Dateisystem-Semantik, also am
            # Unterschied.
            if uname -r | grep -qi 'wsl2'; then
                ok "Linux unter WSL2${WSL_DISTRO_NAME:+ ($WSL_DISTRO_NAME)} — $(uname -r)"
            else
                warnung "Linux unter WSL, aber nicht erkennbar WSL2 ($(uname -r))." \
                        "WSL1 übersetzt Syscalls statt sie auszuführen; für Dateisperren" \
                        "(flock) und Rechte gibt das Kit dort keine Zusicherung." \
                        "Prüfen und umstellen (in PowerShell):  wsl -l -v  /  wsl --set-version <Distro> 2" \
                        "Geht WSL2 nicht (VM ohne nested virtualization)? Kein Abbruch — aber die" \
                        "Sperrprobe unten ist einprozessig und belegt hier weniger als auf einem" \
                        "echten Kernel. Zwei-Prozess-Gegenprobe: doku/einrichtung.md, 'Wenn nur WSL 1 geht'"
            fi
        else
            ok "Linux — $(uname -r)"
        fi
        ;;
    Darwin)
        warnung "macOS erkannt. Nicht belegt: Das Kit ist auf Linux (und abgeleitet WSL2)" \
                "erprobt. Bordmittel-bash ist dort 3.2 und flock fehlt —" \
                "beides prüft der nächste Abschnitt einzeln."
        ;;
    MINGW*|MSYS*|CYGWIN*)
        # BL-159: Hier stand "Unbekanntes System" — und das war es nie. Git
        # for Windows ist der dokumentierte Weg, die bash-Bahn unter Windows
        # zu fahren; das Kit prüft mit genau dieser bash seinen eigenen
        # Selbsttest. Ein "unbekannt" an dieser Stelle liest sich wie
        # "ungetestetes Gelände", und die zwei Fehler darunter bestätigten
        # den Eindruck.
        warnung "Windows nativ, bash über Git for Windows ($(uname -s))." \
                "Die bash-Bahn ist hier die ZWEITE Wahl: Nativ unter Windows" \
                "ist die pwsh-Bahn zuständig (README, Zwei-Bahnen-Tabelle)." \
                "Zwei Befunde folgen daraus und stehen unten einzeln —" \
                "fehlendes flock und ein Exec-Bit, das NTFS nicht trägt." \
                "Beide sind Warnungen und keine Fehler: Sie beschreiben die" \
                "Lage dieser Bahn auf dieser Maschine, nicht einen Defekt."
        ;;
    *)
        warnung "Unbekanntes System: $(uname -s). Die Prüfungen laufen trotzdem."
        ;;
esac

# ---------------------------------------------------------------- 2/5 Werkzeuge
kopf "2/5 — Werkzeuge"

# bash 4 aufwärts. Die Begründung stand hier bis 2026-08-17 falsch: "Das Kit
# nutzt DURCHGEHEND indirekte Expansion (${!var})". Nachgemessen kommt sie in
# der LAUFZEIT — bash/lib.sh, bash/entry/*.sh, bash/redteam.sh — NULL Mal vor.
# Alle sechs Fundstellen liegen in bash/install.sh (dazu `printf -v` und
# `unset "${!TEAM_@}"`), also im INSTALLER.
#
# Die Anforderung bleibt trotzdem bestehen, nur mit dem richtigen Grund: Der
# Installer braucht bash 4, und ohne ihn kommt niemand zu einer Laufzeit. Die
# alte Formulierung war keine Kleinigkeit — sie hätte jeden, der die Laufzeit
# portiert oder prüft, an der falschen Stelle suchen lassen.
if [ "${BASH_VERSINFO[0]}" -ge 4 ]; then
    ok "bash ${BASH_VERSION%%(*}"
else
    fehler "bash ${BASH_VERSION%%(*} ist zu alt (gebraucht wird 4 oder neuer)." \
           "Die Skripte nutzen indirekte Expansion; unter bash 3 brechen sie ab."
fi

if command -v git >/dev/null 2>&1; then
    ok "git $(git --version | awk '{print $3}')"
else
    fehler "git fehlt." \
           "Die Rollen committen, rollen zurück und prüfen Commit-Bereiche." \
           "Debian/Ubuntu:  sudo apt install git"
fi

# Python: Abhängigkeit der TEAM-Infrastruktur (team/tools/), nicht des Projekts.
#
# BL-137: Gesucht wird nach dem Namen, unter dem der Interpreter auf DIESER
# Maschine antwortet — nicht nach `python3`. Unter Windows legen weder
# python.org noch winget ein python3.exe an; was dort unter dem Namen
# antwortet, ist der App-Execution-Alias aus dem Microsoft Store. Er
# beantwortet `command -v`, startet aber keinen Interpreter: Diese Prüfung
# meldete deshalb auf einer Maschine MIT Python "python3 fehlt" und empfahl
# `apt install python3`.
#
# Geprüft wird START UND VERSION, nicht Anwesenheit (Lehre BL-122), und die
# Reihenfolge entscheidet die Plattform — zeichengleich mit finde_python() in
# install.sh. Die Meldung nennt den GEFUNDENEN Namen: Wer hier "Python 3.13
# (als python)" liest, weiß, was er in team.config.sh erwarten darf.
EINR_PY=""
EINR_PY_KANDIDATEN="python3 python py"
case "$(uname -s 2>/dev/null)" in
    MINGW*|MSYS*|CYGWIN*|Windows*) EINR_PY_KANDIDATEN="python python3 py" ;;
esac
for _py in $EINR_PY_KANDIDATEN; do
    command -v "$_py" >/dev/null 2>&1 || continue
    if "$_py" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 8) else 1)' \
            >/dev/null 2>&1; then
        EINR_PY="$_py"; break
    fi
done
if [ -n "$EINR_PY" ]; then
    ok "Python $("$EINR_PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])') (als $EINR_PY)"
else
    # Zwischen "gar nicht da" und "da, aber zu alt" unterscheiden — die
    # Abhilfe ist eine andere, und eine Meldung, die beides gleich nennt,
    # schickt den Menschen in die falsche Richtung.
    EINR_PY_ALT=""
    for _py in $EINR_PY_KANDIDATEN; do
        command -v "$_py" >/dev/null 2>&1 || continue
        if "$_py" -c 'import sys' >/dev/null 2>&1; then EINR_PY_ALT="$_py"; break; fi
    done
    if [ -n "$EINR_PY_ALT" ]; then
        fehler "Python $("$EINR_PY_ALT" -c 'import sys; print("%d.%d" % sys.version_info[:2])') ist zu alt (gebraucht wird 3.8 oder neuer)." \
               "team/tools/kosten.py und beutebuch.py setzen es voraus."
    else
        fehler "Python fehlt (gesucht als: $EINR_PY_KANDIDATEN)." \
               "Die Team-Werkzeuge (Kosten, Beutebuch) sind Python — das ist eine" \
               "Abhängigkeit der Infrastruktur, nicht deines Projekts." \
               "Debian/Ubuntu:  sudo apt install python3" \
               "Windows:        winget install Python.Python.3.12"
    fi
fi

if command -v flock >/dev/null 2>&1; then
    ok "flock $(flock --version 2>&1 | awk '{print $NF}')"
elif [ "$WIRT" = "windows" ]; then
    # BL-159: Hier stand ein Fehler samt "sudo apt install util-linux" — auf
    # einer Windows-Maschine ein Rat ins Leere. Git for Windows liefert kein
    # flock, und es gibt kein Paket, das eines nachliefert.
    #
    # BL-190: Und hier stand bis dahin, die Serialisierung FEHLE dann. Das war
    # damals wahr und ist es nicht mehr — die bash-Bahn sperrt ohne flock ueber
    # einen mkdir-Sperrordner. Eine Einrichtungspruefung, die dem Code
    # widerspricht, ist schlimmer als keine: Sie erzieht dazu, ihr nicht zu
    # glauben.
    # Gruen, nicht gelb: Die Lage ist vollstaendig abgedeckt, und eine Warnung,
    # die auf JEDER Git-for-Windows-Maschine erscheint und nichts zu tun
    # uebriglaesst, ist nach BL-14 keine.
    ok "flock fehlt — Git for Windows liefert keines; der Ersatzweg greift"
    echo "      Die bash-Bahn sperrt hier ueber einen mkdir-Sperrordner"
    echo "      (.team-loop.lock.d, BL-190). Die Zusicherung 'eine Pipeline zur"
    echo "      Zeit' bleibt; das Kit sagt den Ersatzweg beim Lauf einmal an."
    echo "      Nativ unter Windows ist ohnehin die pwsh-Bahn zustaendig"
    echo "      (README, Zwei-Bahnen-Tabelle) — sie sperrt ueber echte"
    echo "      Dateisperren des Betriebssystems und braucht kein flock."
else
    warnung "flock fehlt (Paket util-linux)." \
            "Seit BL-190 kein Abbruchgrund mehr: Die bash-Bahn weicht auf" \
            "einen mkdir-Sperrordner aus, und 'eine Pipeline zur Zeit' bleibt" \
            "zugesichert. flock ist trotzdem der bevorzugte Weg — es ist der" \
            "erprobte, und zwei Sperrmechaniken im Feld erschweren die" \
            "Ursachensuche bei einem Vorfall." \
            "Debian/Ubuntu:  sudo apt install util-linux"
fi

# pytest: nur für die Testläufe nötig, nicht für den Betrieb der Rollen.
# BL-124: als MODUL suchen, nicht nur als Befehl. `pip install --user pytest`
# legt die ausfuehrbare Datei in ein bin-Verzeichnis, das oft nicht im PATH
# steht — pip warnt beim Installieren sogar davor. Wer nur den Befehl sucht,
# meldet "fehlt" und empfiehlt genau die Installation, die es schon gibt.
PYTEST_AUFRUF=""
for _py in python3 python py; do
    command -v "$_py" >/dev/null 2>&1 || continue
    if "$_py" -m pytest --version >/dev/null 2>&1; then
        PYTEST_AUFRUF="$_py -m pytest"; break
    fi
done
# Bewusst ein if statt einer &&-Kette: Unter `set -e` reisst eine Kette, deren
# erstes Glied falsch ist, den ganzen Lauf mit — und falsch ist sie genau dann,
# wenn oben schon etwas gefunden wurde. Also im Erfolgsfall.
if [ -z "$PYTEST_AUFRUF" ] && command -v pytest >/dev/null 2>&1; then
    PYTEST_AUFRUF="pytest"
fi
if [ -n "$PYTEST_AUFRUF" ]; then
    ok "pytest $($PYTEST_AUFRUF --version 2>&1 | head -1 | awk '{print $2}') (via: $PYTEST_AUFRUF)"
else
    warnung "pytest fehlt. ./team-test.sh im Zielprojekt und ./kit-test.sh hier" \
            "brauchen es; die Rollen selbst nicht." \
            "Debian/Ubuntu:  sudo apt install python3-pytest   (oder: pipx install pytest)"
fi

# Agenten-CLI: BEISPIEL. Das Kit spricht zwei Modellstufen an, keine Namen; die
# einzige Aufrufstelle ist team_claude() in bash/lib.sh.
if command -v claude >/dev/null 2>&1; then
    ok "Agenten-CLI (Beispiel Claude Code): $(claude --version 2>/dev/null | head -1)"
else
    gelb "  ! Keine 'claude'-CLI im PATH."
    echo "      Das ist kein Fehler: Das Kit ist modell- und werkzeugagnostisch."
    echo "      Erprobt ist heute genau ein Weg — Claude Code. Wer ihn nimmt:"
    echo "        npm install -g @anthropic-ai/claude-code   (in der Distro, nicht in Windows)"
    echo "      Wer ein anderes Werkzeug nimmt, tauscht team_claude() in bash/lib.sh;"
    echo "      siehe doku/einrichtung.md, Abschnitt \"Ein anderes Werkzeug\"."
fi

# ---------------------------------------------------------------- 3/5 Lage des Klons
kopf "3/5 — Lage des Klons"

# a) Zeilenenden. Ein Klon, der vor .gitattributes entstanden ist, oder eine
#    über Windows kopierte Ablage trägt CRLF weiter.
CRLF_TREFFER=""
# Alles, was die Bash-Bahn ausmacht — ein Ordner, drei Globs. Vor der
# Bahn-Trennung standen hier vier Pfade aus drei Ablagen.
for f in "$BAHN"/*.sh "$BAHN"/entry/*.sh "$BAHN"/scripts/*.sh; do
    [ -f "$f" ] || continue
    if LC_ALL=C grep -qU $'\r' "$f" 2>/dev/null; then
        CRLF_TREFFER="$CRLF_TREFFER $(basename "$f")"
    fi
done
if [ -n "$CRLF_TREFFER" ]; then
    fehler "Skripte mit CRLF-Zeilenenden:$CRLF_TREFFER" \
           "bash meldet dann 'bad interpreter' — es ist NICHT das Kit kaputt." \
           "Saubere Abhilfe: in der Distro neu klonen (nicht in Windows kopieren)." \
           "In diesem Klon, wenn keine eigene Arbeit drinsteckt:" \
           "  git -C \"$KIT\" config core.autocrlf false" \
           "  git -C \"$KIT\" rm --cached -r . >/dev/null && git -C \"$KIT\" reset --hard" \
           "  (das zweite Kommando verwirft uncommittete Änderungen — vorher prüfen)"
else
    ok "Zeilenenden sind LF"
fi

# b) Dateisystem. Unter WSL ist ein Klon unter /mnt/… der teuerste stille Fehler.
pruefe_ablage() {  # pruefe_ablage <pfad> <beschriftung>
    local pfad="$1" name="$2"
    if [ "$UNTER_WSL" -eq 1 ] && [ "${pfad#/mnt/}" != "$pfad" ]; then
        if [ "${TEAM_EINRICHTEN_ERLAUBE_DRVFS:-0}" = "1" ]; then
            warnung "$name liegt unter $pfad (Windows-Dateisystem) — auf eigenen Wunsch zugelassen."
        else
            fehler "$name liegt im Windows-Dateisystem: $pfad" \
                   "Unter WSL hängt das an DrvFs. Folgen: chmod +x verpufft (die" \
                   "Entrypoints sind nach der Installation nicht ausführbar), Git sieht" \
                   "dauernd Rechteänderungen, und die Loop-Sperre (flock) liegt auf einem" \
                   "Dateisystem, für das das Kit keine Zusicherung hat." \
                   "Richtig ist das LINUX-Dateisystem der Distro, z. B. ~/Source/…" \
                   "Aus Windows erreichbar bleibt es über \\\\wsl\$\\<Distro>\\home\\<user>." \
                   "Bewusst trotzdem wollen: TEAM_EINRICHTEN_ERLAUBE_DRVFS=1 bash kit-einrichten.sh"
            return 1
        fi
    fi
    return 0
}
pruefe_ablage "$KIT" "Das Kit" && ok "Kit liegt auf $( [ "$UNTER_WSL" -eq 1 ] && echo "dem Linux-Dateisystem der Distro" || echo "einem lokalen Dateisystem" )"

# c) Wirkt das Exec-Bit hier überhaupt? Die Frage entscheidet, ob die
#    Entrypoints nach der Installation startbar sind — geprüft statt geglaubt.
PROBE="$(mktemp "$KIT/.einrichten-probe.XXXXXX")"
chmod +x "$PROBE" 2>/dev/null || true
if [ -x "$PROBE" ]; then
    ok "Ausführbar-Rechte greifen (chmod +x wirkt)"
elif [ "$WIRT" = "windows" ]; then
    # BL-159: Unter Git-Bash trägt NTFS kein Exec-Bit. Das ist keine kaputte
    # Maschine, sondern das Dateisystem — und es hat eine Abhilfe, die auf
    # dieser Maschine wirklich ausführbar ist.
    warnung "chmod +x wirkt hier nicht — NTFS trägt unter Git-Bash kein Exec-Bit." \
            "Folge: './ralph.sh' endet mit 'Permission denied'." \
            "Abhilfe, eine von zweien:" \
            "  bash ./ralph.sh   (statt ./ralph.sh — der Aufruf über den" \
            "                     Interpreter braucht das Exec-Bit nicht)" \
            "  oder unter Windows die pwsh-Bahn fahren: .\\ralph.cmd"
else
    fehler "chmod +x wirkt in diesem Ordner nicht." \
           "Der Installer setzt die Entrypoints ausführbar; hier bliebe das folgenlos" \
           "und './vollautomatik.sh' endete mit 'Permission denied'."
fi

# d) Und hält eine Dateisperre? Danach hängt die Serialisierung von Ledger und
#    Kaskadenstand.
#
# BL-159: Fehlt flock als WERKZEUG, ist das schon in 2/5 gemeldet — die Probe
# hier würde denselben Befund ein zweites Mal ausgeben, und zwei Meldungen für
# EINE Ursache lesen sich wie zwei Probleme. Geprüft wird hier, ob eine
# vorhandene Sperre in DIESEM Ordner greift; ohne Werkzeug gibt es dazu nichts
# zu sagen.
if ! command -v flock >/dev/null 2>&1; then
    :
elif flock -n "$PROBE" true 2>/dev/null; then
    ok "Dateisperren (flock) funktionieren hier"
else
    fehler "flock greift in diesem Ordner nicht." \
           "Ohne Sperre können zwei Rollen gleichzeitig auf Ledger und" \
           "Kaskadenstand schreiben. Typische Ursache: Netz- oder Windows-Laufwerk."
fi
rm -f "$PROBE"

# e) Und dasselbe für das Zielprojekt, falls eines genannt wurde.
if [ -n "$ZIEL" ]; then
    if ZIEL_ABS="$(cd "$ZIEL" 2>/dev/null && pwd)"; then
        ZIEL="$ZIEL_ABS"
        pruefe_ablage "$ZIEL" "Das Zielprojekt" || true
        if git -C "$ZIEL" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
            ok "Zielprojekt ist ein Git-Repository: $ZIEL"
        else
            fehler "Zielprojekt ist kein Git-Repository: $ZIEL" \
                   "Zuerst:  git -C \"$ZIEL\" init"
        fi
    else
        fehler "Zielpfad existiert nicht: $ZIEL"
        ZIEL=""
    fi
fi

# ---------------------------------------------------------------- 4/5 Auth
kopf "4/5 — Auth des Agenten-Werkzeugs (Beispiel Claude Code)"

if [ -f "$HOME/.config/claude-team/auth-mode" ] || [ -f "$HOME/.config/claude-team/api-key" ]; then
    ok "Auth-Konfiguration vorhanden: ~/.config/claude-team/"
elif [ "$NUR_PRUEFEN" -eq 1 ]; then
    warnung "Keine Auth-Konfiguration unter ~/.config/claude-team/." \
            "Nachholen:  bash $KIT/bash/scripts/team-auth-setup.sh"
elif [ "$AUTH" -eq 1 ] || ja "Auth jetzt einrichten (Abo als Prio 1, API-Key nur als Fallback)?"; then
    bash "$KIT/bash/scripts/team-auth-setup.sh" || warnung "Auth-Einrichtung abgebrochen — nachholbar, siehe oben."
else
    warnung "Keine Auth-Konfiguration unter ~/.config/claude-team/." \
            "Ohne sie läuft keine Rolle. Nachholen:" \
            "  bash $KIT/bash/scripts/team-auth-setup.sh" \
            "Merke: Der API-Key gehört NIE per export ins Shell-Profil — er hat" \
            "Vorrang vor dem Abo-Login und schaltet die Abrechnung still um."
fi

# ---------------------------------------------------------------- 5/5 Verknüpfung
kopf "5/5 — Kurzbefehl von überall (optional)"

# BL-160: Hat das `ln` wirklich eine Verknuepfung ergeben? PROBIERT, nicht
# vorausgesetzt — genau wie dieses Skript es zwei Abschnitte weiter oben mit
# chmod und flock haelt.
#
# Der Anlass ist gemessen: Unter MSYS/Git-Bash legt `ln -s` ohne Symlink-Recht
# eine KOPIE an und meldet Erfolg. Dieser Schritt sagte dann "Verknuepft: …→…"
# — mit Pfeil — und hatte eine regulaere Datei hingelegt. Das ist die
# unangenehmste Form des Fehlers: Ausgerechnet die REPARATUR erzeugt dann
# genau die veraltete Launcher-Kopie, gegen die sie gebaut ist, und der
# nebenstehende Satz "Eine Verknuepfung kann nicht veralten" wird zur
# Falschaussage.
#
# Warum Warnung und nicht Fehler: Der Kurzbefehl ist ausdruecklich optional
# (5/5), und der Weg ueber den vollen Pfad funktioniert weiter. Was nicht
# weiter geht, ist das stille Behaupten.
# Die Begründung steht EINMAL. Beide Launcher fallen auf derselben Maschine
# aus demselben Grund um; dieselben dreizehn Zeilen zweimal hintereinander
# erziehen zum Überblättern (BL-14), und dann geht die zweite Meldung im
# Wortlaut der ersten unter.
VERKNUEPFUNG_ERKLAERT=0
verknuepfung_bestaetigen() {  # verknuepfung_bestaetigen <ziel> <quelle> <erfolgstext>
    if [ -L "$1" ]; then ok "$3"; return 0; fi
    if [ "$VERKNUEPFUNG_ERKLAERT" -eq 1 ]; then
        warnung "Kopie statt Verknüpfung: $1 (gleiche Ursache wie oben)"
        return 1
    fi
    VERKNUEPFUNG_ERKLAERT=1
    warnung "Kopie statt Verknüpfung: $1" \
            "'ln -s' hat hier nicht verknüpft, sondern kopiert. Typische" \
            "Ursache: Git-Bash/MSYS ohne Symlink-Recht." \
            "Folge: Die Kopie veraltet, sobald sich das Kit ändert — der" \
            "Installer meldet sie dann bei jedem Lauf. Genau davor soll" \
            "dieser Schritt schützen." \
            "Abhilfe, eine von dreien:" \
            "  Entwicklermodus einschalten, dann erneut:" \
            "    MSYS=winsymlinks:nativestrict bash kit-einrichten.sh --verknuepfen" \
            "  oder den Launcher mit vollem Pfad aufrufen:" \
            "    bash $2 <zielpfad>" \
            "  oder unter Windows die pwsh-Bahn fahren (kit-einrichten.ps1)."
    return 1
}

verknuepfe() {  # verknuepfe <quelle> <zielname>
    local quelle="$1" ziel="$HOME/.claude/scripts/$2"
    if [ -L "$ziel" ]; then
        if [ "$(readlink "$ziel")" = "$quelle" ]; then ok "Verknüpft: $ziel"
        else warnung "$ziel zeigt woandershin: $(readlink "$ziel")" \
                     "Ersetzen:  ln -sfn \"$quelle\" \"$ziel\""; fi
    elif [ -e "$ziel" ]; then
        # Eine echte Datei statt einer Verknüpfung. Bis 2.10 wurde sie nur
        # gemeldet — und genau das hat im Feld nicht gereicht: Die Meldung
        # kommt nur, wenn jemand `--verknuepfen` fährt, und wer eine Kopie
        # hat, hat es meist nie getan. Die Kopie lag dann jahrelang da und
        # fiel erst auf, als der Umzug auf bash/ sie stilllegte.
        #
        # Ersetzt wird deshalb — aber NUR, was erkennbar vom Kit stammt. Die
        # Marke ist der Bahn-Kopf, den jede Kit-Datei trägt (A.13). Was sie
        # nicht trägt, hat jemand selbst geschrieben; das bleibt liegen und
        # wird gemeldet. Eine fremde Datei wegzuräumen wäre schlimmer als
        # jede veraltete Kopie.
        # Woran eine Kit-Kopie erkannt wird: an der KOPFZEILE der Kit-Datei
        # selbst (`# team-init.sh — …`). Sie steht in jeder Fassung, auch in
        # denen von vor der Bahn-Kennung, und sie ist spezifisch genug, dass
        # niemand sie zufaellig schreibt.
        #
        # Erster Versuch war eine Marke wie "T.E.A.M.-Starterkit" im Text —
        # zu eng: Die Kopie von team-auth-setup.sh auf der Autorenmaschine
        # sagt "T.E.A.M.-Konvention" und waere durchgefallen. Eine Erkennung,
        # die echte Kopien nicht erkennt, ist schlimmer als keine: Sie meldet
        # "stammt nicht vom Kit" und macht aus einem Fund eine Beruhigung.
        local kopfzeile
        kopfzeile="$(grep -m1 "^# $2 —" "$quelle" 2>/dev/null || true)"
        if [ -n "$kopfzeile" ] && grep -qF "$kopfzeile" "$ziel" 2>/dev/null; then
            local sicherung="$ziel.vor-verknuepfung"
            cp "$ziel" "$sicherung"
            ln -sfn "$quelle" "$ziel"
            if verknuepfung_bestaetigen "$ziel" "$quelle"                    "Ersetzt: $ziel war eine Kopie des Kits → jetzt Verknüpfung"; then
                echo "      Die alte Fassung liegt als $(basename "$sicherung") daneben."
                echo "      Eine Verknüpfung kann nicht veralten — die Kopie konnte es."
            else
                echo "      Die alte Fassung liegt als $(basename "$sicherung") daneben."
            fi
        else
            warnung "$ziel ist eine echte Datei und stammt nicht erkennbar vom Kit." \
                    "Nicht angefasst — sie könnte deine eigene sein." \
                    "Ersetzen, wenn sie es doch ist:  ln -sfn \"$quelle\" \"$ziel\""
        fi
    else
        mkdir -p "$HOME/.claude/scripts"
        ln -s "$quelle" "$ziel"
        verknuepfung_bestaetigen "$ziel" "$quelle" "Verknüpft: $ziel → $quelle" || true
    fi
}

if [ "$NUR_PRUEFEN" -eq 1 ]; then
    echo "  (übersprungen wegen --nur-pruefen)"
elif [ "$VERKNUEPFEN" -eq 1 ] || ja "bash/scripts/team-init.sh und team-auth-setup.sh nach ~/.claude/scripts/ verknüpfen?"; then
    verknuepfe "$KIT/bash/scripts/team-init.sh"       "team-init.sh"
    verknuepfe "$KIT/bash/scripts/team-auth-setup.sh" "team-auth-setup.sh"
    echo "      Danach von überall:  bash ~/.claude/scripts/team-init.sh <zielpfad>"
else
    echo "  Übersprungen. Der lange Weg tut es genauso:"
    echo "      bash $KIT/bash/install.sh <zielpfad>"
fi

# ---------------------------------------------------------------- Abschluss
kopf "Ergebnis"

if [ "$FEHLER" -gt 0 ]; then
    rot "  $FEHLER Fehler, $WARNUNGEN Warnungen — die Maschine ist noch nicht bereit."
    echo "  Erst die Fehler oben abarbeiten, dann dieses Skript erneut fahren."
    echo "  Die ausführliche Fassung mit Begründungen: doku/einrichtung.md"
    exit 1
fi

if [ "$WARNUNGEN" -gt 0 ]; then
    gelb "  0 Fehler, $WARNUNGEN Warnungen — lauffähig, aber lies sie."
else
    gruen "  Alles grün."
fi

if [ -n "$ZIEL" ] && [ "$NUR_PRUEFEN" -eq 0 ]; then
    kopf "Weiter: Einbinden in $ZIEL"
    if [ "$INTERAKTIV" -eq 0 ]; then
        # Ohne Mensch am Terminal wird auch der Installer nicht interaktiv
        # gefahren — sonst liefe sein Aufnahme-Interview gegen EOF und
        # beantwortete neun Fragen still mit den Defaults. Die Werte kommen
        # dann aus den TEAM_INIT_*-Umgebungsvariablen.
        echo "  (nicht-interaktiv — Werte aus TEAM_INIT_* bzw. Defaults)"
        exec bash "$KIT/bash/install.sh" "$ZIEL" --nicht-interaktiv
    fi
    if ja "install.sh jetzt starten?"; then
        exec bash "$KIT/bash/install.sh" "$ZIEL"
    fi
    echo "  Später:  bash $KIT/bash/install.sh \"$ZIEL\""
else
    kopf "Weiter"
    echo "  Einbinden in ein Projekt:  bash $KIT/bash/install.sh <zielpfad>"
    echo "  Kit selbst verifizieren:   ./kit-test.sh   (installiert in ein Wegwerf-Repo)"
    echo "  Die ganze Routine:         doku/einrichtung.md"
fi

#!/usr/bin/env bash
# kit-einrichten.sh — die Vorflug-Prüfung zwischen `git clone` und `install.sh`.
#
# Aufruf:  bash kit-einrichten.sh [zielpfad] [--verknuepfen] [--auth]
#                                 [--nur-pruefen] [--nicht-interaktiv]
#
#   zielpfad            Projekt, in das das Team danach einziehen soll. Wird es
#                       angegeben und ist die Maschine grün, übergibt das Skript
#                       an install.sh — Klonen und Einbinden in einem Zug.
#   --verknuepfen       scripts/team-init.sh und scripts/team-auth-setup.sh als
#                       SYMLINK unter ~/.claude/scripts/ ablegen (Kurzbefehl von
#                       überall, ohne zweite Kopie). Vorhandene echte Dateien
#                       werden nie überschrieben, nur gemeldet.
#   --auth              scripts/team-auth-setup.sh mitlaufen lassen.
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

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
    *)
        warnung "Unbekanntes System: $(uname -s). Die Prüfungen laufen trotzdem."
        ;;
esac

# ---------------------------------------------------------------- 2/5 Werkzeuge
kopf "2/5 — Werkzeuge"

# bash 4 aufwärts. Die Begründung stand hier bis 2026-08-17 falsch: "Das Kit
# nutzt DURCHGEHEND indirekte Expansion (${!var})". Nachgemessen kommt sie in
# der LAUFZEIT — team/lib.sh, entry/*.sh, team/redteam.sh — genau NULL Mal vor.
# Alle sechs Fundstellen liegen in install.sh (dazu `printf -v` und
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

# python3: Abhängigkeit der TEAM-Infrastruktur (team/tools/), nicht des Projekts.
if command -v python3 >/dev/null 2>&1; then
    PY_VERSION="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo '?')"
    if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
        ok "python3 $PY_VERSION"
    else
        fehler "python3 $PY_VERSION ist zu alt (gebraucht wird 3.8 oder neuer)." \
               "team/tools/kosten.py und beutebuch.py setzen es voraus."
    fi
else
    fehler "python3 fehlt." \
           "Die Team-Werkzeuge (Kosten, Beutebuch) sind Python — das ist eine" \
           "Abhängigkeit der Infrastruktur, nicht deines Projekts." \
           "Debian/Ubuntu:  sudo apt install python3"
fi

if command -v flock >/dev/null 2>&1; then
    ok "flock $(flock --version 2>&1 | awk '{print $NF}')"
else
    fehler "flock fehlt (Paket util-linux)." \
           "Ohne Dateisperre laufen zwei Rollen unbemerkt gleichzeitig auf" \
           "Ledger und Kaskadenstand." \
           "Debian/Ubuntu:  sudo apt install util-linux"
fi

# pytest: nur für die Testläufe nötig, nicht für den Betrieb der Rollen.
if command -v pytest >/dev/null 2>&1; then
    ok "pytest $(pytest --version 2>&1 | head -1 | awk '{print $2}')"
else
    warnung "pytest fehlt. ./team-test.sh im Zielprojekt und ./kit-test.sh hier" \
            "brauchen es; die Rollen selbst nicht." \
            "Debian/Ubuntu:  sudo apt install python3-pytest   (oder: pipx install pytest)"
fi

# Agenten-CLI: BEISPIEL. Das Kit spricht zwei Modellstufen an, keine Namen; die
# einzige Aufrufstelle ist team_claude() in team/lib.sh.
if command -v claude >/dev/null 2>&1; then
    ok "Agenten-CLI (Beispiel Claude Code): $(claude --version 2>/dev/null | head -1)"
else
    gelb "  ! Keine 'claude'-CLI im PATH."
    echo "      Das ist kein Fehler: Das Kit ist modell- und werkzeugagnostisch."
    echo "      Erprobt ist heute genau ein Weg — Claude Code. Wer ihn nimmt:"
    echo "        npm install -g @anthropic-ai/claude-code   (in der Distro, nicht in Windows)"
    echo "      Wer ein anderes Werkzeug nimmt, tauscht team_claude() in team/lib.sh;"
    echo "      siehe doku/einrichtung.md, Abschnitt \"Ein anderes Werkzeug\"."
fi

# ---------------------------------------------------------------- 3/5 Lage des Klons
kopf "3/5 — Lage des Klons"

# a) Zeilenenden. Ein Klon, der vor .gitattributes entstanden ist, oder eine
#    über Windows kopierte Ablage trägt CRLF weiter.
CRLF_TREFFER=""
for f in "$KIT/install.sh" "$KIT/kit-test.sh" "$KIT"/entry/*.sh "$KIT"/team/*.sh; do
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
else
    fehler "chmod +x wirkt in diesem Ordner nicht." \
           "Der Installer setzt die Entrypoints ausführbar; hier bliebe das folgenlos" \
           "und './vollautomatik.sh' endete mit 'Permission denied'."
fi

# d) Und hält eine Dateisperre? Danach hängt die Serialisierung von Ledger und
#    Kaskadenstand.
if flock -n "$PROBE" true 2>/dev/null; then
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
            "Nachholen:  bash $KIT/scripts/team-auth-setup.sh"
elif [ "$AUTH" -eq 1 ] || ja "Auth jetzt einrichten (Abo als Prio 1, API-Key nur als Fallback)?"; then
    bash "$KIT/scripts/team-auth-setup.sh" || warnung "Auth-Einrichtung abgebrochen — nachholbar, siehe oben."
else
    warnung "Keine Auth-Konfiguration unter ~/.config/claude-team/." \
            "Ohne sie läuft keine Rolle. Nachholen:" \
            "  bash $KIT/scripts/team-auth-setup.sh" \
            "Merke: Der API-Key gehört NIE per export ins Shell-Profil — er hat" \
            "Vorrang vor dem Abo-Login und schaltet die Abrechnung still um."
fi

# ---------------------------------------------------------------- 5/5 Verknüpfung
kopf "5/5 — Kurzbefehl von überall (optional)"

verknuepfe() {  # verknuepfe <quelle> <zielname>
    local quelle="$1" ziel="$HOME/.claude/scripts/$2"
    if [ -L "$ziel" ]; then
        if [ "$(readlink "$ziel")" = "$quelle" ]; then ok "Verknüpft: $ziel"
        else warnung "$ziel zeigt woandershin: $(readlink "$ziel")" \
                     "Ersetzen:  ln -sfn \"$quelle\" \"$ziel\""; fi
    elif [ -e "$ziel" ]; then
        # Nicht überschreiben: Das ist eine echte Datei, womöglich eine ältere
        # Kopie aus der Zeit vor dem Klon. Sie läuft dem Kit hinterher, aber
        # stillschweigend wegzuräumen ist schlimmer als sie zu melden.
        warnung "$ziel ist eine echte Datei, keine Verknüpfung — nicht angefasst." \
                "Sie läuft dem Kit hinterher, sobald sich hier etwas ändert." \
                "Ersetzen:  ln -sfn \"$quelle\" \"$ziel\""
    else
        mkdir -p "$HOME/.claude/scripts"
        ln -s "$quelle" "$ziel"
        ok "Verknüpft: $ziel → $quelle"
    fi
}

if [ "$NUR_PRUEFEN" -eq 1 ]; then
    echo "  (übersprungen wegen --nur-pruefen)"
elif [ "$VERKNUEPFEN" -eq 1 ] || ja "scripts/team-init.sh und team-auth-setup.sh nach ~/.claude/scripts/ verknüpfen?"; then
    verknuepfe "$KIT/scripts/team-init.sh"       "team-init.sh"
    verknuepfe "$KIT/scripts/team-auth-setup.sh" "team-auth-setup.sh"
    echo "      Danach von überall:  bash ~/.claude/scripts/team-init.sh <zielpfad>"
else
    echo "  Übersprungen. Der lange Weg tut es genauso:"
    echo "      bash $KIT/install.sh <zielpfad>"
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
        exec bash "$KIT/install.sh" "$ZIEL" --nicht-interaktiv
    fi
    if ja "install.sh jetzt starten?"; then
        exec bash "$KIT/install.sh" "$ZIEL"
    fi
    echo "  Später:  bash $KIT/install.sh \"$ZIEL\""
else
    kopf "Weiter"
    echo "  Einbinden in ein Projekt:  bash $KIT/install.sh <zielpfad>"
    echo "  Kit selbst verifizieren:   ./kit-test.sh   (installiert in ein Wegwerf-Repo)"
    echo "  Die ganze Routine:         doku/einrichtung.md"
fi

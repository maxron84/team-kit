#!/usr/bin/env bash
# team-auth-setup.sh — Einmalige Maschinen-Einrichtung: Claude-Abo als Prio 1,
# API-Key nur als geschützter Fallback (T.E.A.M.-Konvention, siehe Projekt-CLAUDE.md).
#
# Dieses Skript ist EIN BEISPIEL, keine Kit-Mechanik: Es richtet die Auth der
# heute erprobten Agenten-CLI (Claude Code) ein. Wer eine andere CLI einsetzt,
# richtet deren Auth auf deren Weg ein und tauscht `team_claude()` in
# team/lib.sh — siehe doku/einrichtung.md, Abschnitt "Ein anderes Werkzeug".
#
# Was das Skript tut (idempotent, kann gefahrlos mehrfach laufen):
#   1. Prüft, ob die 'claude'-CLI installiert ist.
#   2. Legt ~/.config/claude-team/auth-mode an (Default: abo).
#   3. Besorgt den API-Key für den Fallback:
#      a) nimmt eine schon vorhandene ~/.config/claude-team/api-key, sonst
#      b) zieht einen 'export ANTHROPIC_API_KEY=…' aus den Shell-Profilen um
#         (mit Backup, Zeile wird durch einen Hinweis ersetzt), sonst
#      c) fragt interaktiv nach dem Key (Eingabe unsichtbar, landet nie in
#         der Shell-History; leer = überspringen).
#   4. Warnt, wenn der Key in der AKTUELLEN Terminal-Sitzung noch exportiert ist.
#   5. Bietet einen headless Abo-Test an (claude -p, ohne API-Key in der Umgebung).
#
# Aufruf:  bash <kit>/scripts/team-auth-setup.sh
#          (oder, wenn kit-einrichten.sh die Verknüpfung angelegt hat:
#           bash ~/.claude/scripts/team-auth-setup.sh)
set -euo pipefail

CFG_DIR="$HOME/.config/claude-team"
MODE_FILE="$CFG_DIR/auth-mode"
KEY_FILE="$CFG_DIR/api-key"
STEMPEL="$(date +%Y-%m-%d)"

sag()  { printf '%s\n' "$*"; }
ok()   { printf '  ✓ %s\n' "$*"; }
warn() { printf '  ⚠ %s\n' "$*"; }

sag "=== T.E.A.M. Auth-Einrichtung — Abo als Prio 1, API nur als Fallback ==="
sag ""

# --- 1. CLI vorhanden? -------------------------------------------------------
if command -v claude >/dev/null 2>&1; then
    ok "claude-CLI gefunden: $(command -v claude)"
else
    warn "'claude' nicht im PATH — erst Claude Code installieren, dann erneut ausführen."
    exit 1
fi

# --- 2. Maschinen-Default: abo ------------------------------------------------
mkdir -p "$CFG_DIR"
if [ -f "$MODE_FILE" ]; then
    ok "auth-mode existiert bereits: '$(head -n1 "$MODE_FILE" | tr -d '[:space:]')' (bleibt unangetastet)"
else
    echo abo > "$MODE_FILE"
    ok "auth-mode angelegt: abo ($MODE_FILE)"
fi

# --- 3. API-Key für den Fallback ----------------------------------------------
key_quelle=""
if [ -s "$KEY_FILE" ]; then
    key_quelle="vorhandene Datei"
else
    # 3b) Migration aus Shell-Profilen (erste Fundstelle gewinnt)
    for prof in "$HOME/.bashrc" "$HOME/.profile" "$HOME/.bash_profile" "$HOME/.zshrc"; do
        [ -f "$prof" ] || continue
        key="$(sed -nE 's/^[[:space:]]*export[[:space:]]+ANTHROPIC_API_KEY=["'\'']?([^"'\''[:space:]]+)["'\'']?[[:space:]]*$/\1/p' "$prof" | head -n1)"
        if [ -n "$key" ]; then
            cp "$prof" "$prof.bak-teamauth-$STEMPEL"
            install -m 600 /dev/null "$KEY_FILE"
            printf '%s\n' "$key" > "$KEY_FILE"
            sed -i -E "s|^[[:space:]]*export[[:space:]]+ANTHROPIC_API_KEY=.*|# ANTHROPIC_API_KEY umgezogen nach ~/.config/claude-team/api-key — Abo ist Prio 1 (team-auth-setup.sh, $STEMPEL)|" "$prof"
            key_quelle="Migration aus $prof (Backup: $prof.bak-teamauth-$STEMPEL — nach erfolgreichem Test löschen, enthält den Key!)"
            break
        fi
    done

    # 3c) Interaktive Eingabe, falls nichts gefunden und ein Mensch dran sitzt
    if [ -z "$key_quelle" ] && [ -t 0 ]; then
        sag ""
        sag "  Kein API-Key gefunden. Für den Fallback einen Key von console.anthropic.com"
        printf '  hier einfügen (Eingabe bleibt unsichtbar, leer = ohne Fallback fortfahren): '
        read -rs key
        printf '\n'
        if [ -n "$key" ]; then
            install -m 600 /dev/null "$KEY_FILE"
            printf '%s\n' "$key" > "$KEY_FILE"
            key_quelle="manuelle Eingabe"
        fi
    fi
fi

if [ -s "$KEY_FILE" ]; then
    chmod 600 "$KEY_FILE"
    ok "API-Fallback-Key liegt in $KEY_FILE (chmod 600; Quelle: ${key_quelle:-vorhandene Datei})"
else
    warn "Kein API-Key hinterlegt — Abo funktioniert trotzdem, aber es gibt keinen Fallback."
    warn "Nachholen: install -m 600 /dev/null $KEY_FILE && nano $KEY_FILE"
fi

# --- 4. Aktuelle Terminal-Sitzung prüfen ---------------------------------------
sag ""
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    warn "In DIESER Terminal-Sitzung ist ANTHROPIC_API_KEY noch exportiert!"
    warn "Der Key verdrängt dein Abo — bitte jetzt ausführen:  unset ANTHROPIC_API_KEY"
    warn "(Neue Terminals sind automatisch sauber.)"
else
    ok "Kein ANTHROPIC_API_KEY in dieser Sitzung — Abo hat freie Bahn."
fi

# --- 5. Optionaler Abo-Test -----------------------------------------------------
if [ -t 0 ]; then
    printf 'Abo-Login jetzt headless testen? (kostet einen Mini-Abo-Anteil) [j/N] '
    read -r antwort
    if [ "${antwort,,}" = "j" ]; then
        sag "  Teste: claude -p (ohne API-Key in der Umgebung) …"
        ausgabe="$(env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN claude -p 'Antworte nur mit: pong' 2>&1)" || {
            warn "Test fehlgeschlagen — vermutlich fehlt der Abo-Login."
            warn "Einmalig nachholen: 'claude' starten → /login → Claude-Konto wählen → /exit"
            sag ""
            sag "$ausgabe"
            exit 1
        }
        if printf '%s' "$ausgabe" | grep -qi "takes precedence"; then
            warn "Antwort kam, aber eine andere Auth-Quelle verdrängt das Abo — Ausgabe prüfen:"
            sag "$ausgabe"
        else
            ok "Abo-Login funktioniert headless: $(printf '%s' "$ausgabe" | tail -n1)"
        fi
    fi
fi

# --- Zusammenfassung ------------------------------------------------------------
sag ""
sag "=== Fertig. So sprichst du die Modi an: ==="
sag "  ./ralph.sh                         → Abo zuerst, API-Fallback pro Stufe automatisch"
sag "  AUTH_MODE=api ./ralph.sh           → API für diesen Lauf erzwingen"
sag "  AUTH_MODE=abo …                    → Abo erzwingen (falls Config mal anders steht)"
sag "  Starke Rollen (Architekt/Axel):    ANTHROPIC_API_KEY=\$(cat $KEY_FILE) claude --model opus"
sag ""
sag "Merke: Der Key gehört NIE per export in .bashrc & Co. — sonst verdrängt er das Abo."

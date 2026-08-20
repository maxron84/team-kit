# FAQ — Fragen, die beim Aufsetzen wirklich kommen

Diese Seite beantwortet **ganze Fragen**. Sie ist die Ergänzung zu zwei
Nachbarn, und die Arbeitsteilung ist scharf:

| Seite | Beantwortet |
|---|---|
| [einrichtung.md](einrichtung.md) | **Wie geht der Weg?** Die Routine von `git clone` bis zum ersten Lauf |
| [einrichtung.md, *Fehlerbilder*](einrichtung.md#fehlerbilder) | **Was heißt diese eine Meldung?** Symptom → Ursache → Abhilfe, eine Zeile |
| **Diese Seite** | **Was tue ich jetzt?** Fragen, deren Antwort nicht in eine Tabellenzeile passt |
| [anhang-a.md](anhang-a.md) | **Warum ist das so gebaut?** Die Bauentscheide dahinter |

---

## Inhalt

| Frage | Kurz |
|---|---|
| [Claude-CLI nicht gefunden — wie installiere ich sie?](#claude-cli-nicht-gefunden--wie-installiere-ich-sie) | Installationswege für Linux, WSL und Windows nativ — und die drei Fälle, in denen sie installiert ist und der Lauf sie trotzdem nicht findet |

---

## Claude-CLI nicht gefunden — wie installiere ich sie?

**So sieht es aus:**

| Wo | Meldung |
|---|---|
| Linux / WSL | `claude: command not found` |
| Windows (pwsh) | `The term 'claude' is not recognized as a name of a cmdlet, function, script file, or operable program` |
| `kit-einrichten.sh` | `! Keine 'claude'-CLI im PATH.` — Warnung, **kein** Abbruch |
| Ein Rollen-Lauf auf der pwsh-Bahn | `FEHLER: 'claude' ist ueber PATH nicht auffindbar.` — das Kit sagt hier ausdrücklich dazu, dass es **kein** Auth-Fehler ist |

**Einordnung vorweg:** Das Kit ist werkzeugagnostisch — es ruft an genau einer
Stelle eine CLI auf ([`team_claude()`](../bash/lib.sh) bzw.
[`Team-ClaudeBefehl`](../pwsh/lib.psm1)). Erprobt ist heute **ein** Weg dorthin,
Claude Code. Deshalb beschreibt diese Antwort dessen Installation, ohne sie zur
Pflicht zu erklären; die Tauschstelle steht in
[einrichtung.md](einrichtung.md#ein-anderes-werkzeug-eine-andere-ide-ein-anderes-modell).

### Schritt 0 — ist sie wirklich nicht da?

Bevor irgendetwas installiert wird, die Frage sauber beantworten. Erst der
**Pfad**, dann die **Version** — die zweite Zeile ist die eigentliche Antwort,
denn ein gefundener Befehl, der nicht startet, ist ein anderer Fehler:

```bash
# Linux, WSL
command -v claude && claude --version
```

```powershell
# Windows nativ
(Get-Command claude -ErrorAction SilentlyContinue).Source
claude --version
```

Kommt eine Version wie `2.1.206 (Claude Code)`, ist die CLI da — dann weiter bei
[Sie ist installiert, der Lauf findet sie trotzdem nicht](#sie-ist-installiert-der-lauf-findet-sie-trotzdem-nicht).
Kommt nichts, wird installiert.

### Linux und WSL

**In WSL gilt: in der Distro installieren, nicht in Windows.** Das ist dieselbe
Regel wie beim Klon des Kits — Auth, Zustand und Sitzungsdateien sollen im
Linux-Profil liegen, in dem auch die Rollen laufen.

Drei Wege, alle vom Hersteller dokumentiert. Die Spalte *wann* ist die
Entscheidungshilfe:

| Weg | Befehl | Wann |
|---|---|---|
| **Native Installation** (Herstellerempfehlung) | `curl -fsSL https://claude.ai/install.sh \| bash` | Standardfall. Landet als `~/.local/bin/claude`, hält sich selbst aktuell, braucht kein Node |
| **Paketverwaltung** (apt/dnf/apk) | siehe unten | Maschinen, auf denen `curl … \| bash` nicht erwünscht ist, und alles, was über die normale System-Aktualisierung mitlaufen soll |
| **npm global** | `npm install -g @anthropic-ai/claude-code` | Wenn Node ohnehin steht. Braucht **Node ≥ 22**; installiert dieselbe native Binärdatei |

Für den apt-Weg (Debian, Ubuntu) — signiertes Herstellerrepo, Kanal `stable`:

```bash
sudo apt install curl gnupg
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc \
  -o /etc/apt/keyrings/claude-code.asc
gpg --show-keys /etc/apt/keyrings/claude-code.asc   # Fingerabdruck prüfen, s. u.
echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main" \
  | sudo tee /etc/apt/sources.list.d/claude-code.list
sudo apt update && sudo apt install claude-code
```

Der Fingerabdruck muss `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE` lauten. Er
wird **geprüft, nicht angenommen** — genau die Haltung, die
`kit-einrichten.sh` an jeder anderen Stelle auch fährt.

> **Nie `sudo npm install -g`.** Das erzeugt Dateien unter Fremdbesitz und einen
> Aktualisierungsweg, der ab dann Rechte braucht. Wenn der npm-Weg an Rechten
> scheitert, ist die native Installation die Antwort, nicht `sudo`.

Danach — **PATH**. Die native Installation legt die Datei nach
`~/.local/bin`; steht das nicht im `PATH`, ist der Befehl weiterhin unsichtbar:

```bash
echo "$PATH" | tr ':' '\n' | grep -qx "$HOME/.local/bin" && echo "PATH ok" || \
  echo 'export PATH="$HOME/.local/bin:$PATH"'   # in ~/.bashrc bzw. ~/.zshrc
exec "$SHELL" -l                                # neue Anmeldeshell, dann Schritt 0
```

### Windows nativ (ohne WSL)

| Weg | Befehl | Wann |
|---|---|---|
| **Native Installation** (Herstellerempfehlung) | `irm https://claude.ai/install.ps1 \| iex` | Standardfall. Landet als `%USERPROFILE%\.local\bin\claude.exe`, hält sich selbst aktuell, **kein Administrator nötig** |
| **WinGet** | `winget install Anthropic.ClaudeCode` | Wenn Software auf der Maschine ohnehin über WinGet läuft. Aktualisiert sich **nicht** von selbst: `winget upgrade Anthropic.ClaudeCode` |
| **npm global** | `npm install -g @anthropic-ai/claude-code` | Wenn Node ohnehin steht (**≥ 22**) |

Drei Dinge, die auf diesem Weg regelmäßig Zeit kosten:

1. **Nach der Installation eine NEUE `pwsh`-Sitzung öffnen.** PATH-Änderungen
   erreichen laufende Shells nicht. Das ist der häufigste Fall von
   „installiert und trotzdem nicht gefunden".
2. **`irm … | iex` ist PowerShell-Syntax.** Meldet die Konsole
   `'irm' is not recognized`, läuft dort CMD, nicht PowerShell — erkennbar am
   Prompt: `PS C:\…` ist PowerShell, `C:\…` ohne `PS` ist CMD. Für CMD lautet
   der Befehl `curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd`.
   Für das Kit selbst gilt ohnehin: **`pwsh` 7, nicht `powershell` 5.1** —
   siehe [einrichtung.md](einrichtung.md#1-powershell-7--nicht-51).
3. **[Git for Windows](https://git-scm.com/downloads/win) mitinstallieren.**
   Optional für die CLI, praktisch relevant fürs Kit: Ohne Git Bash führt
   Claude Code Shell-Befehle über PowerShell aus. Die Rollen des Kits rufen
   Tests und Werkzeuge auf — je näher deren Umgebung an der dokumentierten
   liegt, desto weniger Überraschungen. Findet die CLI Git Bash nicht, hilft
   `CLAUDE_CODE_GIT_BASH_PATH` in der `settings.json` der CLI.

> **Der Shim-Fall, wenn über npm installiert wurde:** `claude` ist dann kein
> Programm, sondern eine `.cmd`-Datei. Scheitert deren Auflösung, **sieht das
> Ergebnis aus wie ein Auth-Fehler und ist keiner**. Das Kit löst den Befehl
> deshalb über `Get-Command` auf und meldet den Fall mit eigenem Wortlaut
> ([`Team-ClaudeBefehl`](../pwsh/lib.psm1)). Wer diese Meldung sieht, sucht den
> Fehler im PATH — nicht im Konto.

### Sie ist installiert, der Lauf findet sie trotzdem nicht

Schritt 0 meldet eine Version, aber `vollautomatik.sh` bzw. `vollautomatik.ps1`
bricht ab. Dann steht die CLI in **einem anderen PATH** als der Prozess, der sie
ruft. Drei Fälle, absteigend nach Häufigkeit:

| Fall | Erkennungszeichen | Abhilfe |
|---|---|---|
| **Geerbte Umgebung** — Terminal oder IDE lief schon, bevor installiert wurde | In einer frisch geöffneten Konsole geht es, in der alten nicht | Bei einer IDE reicht ein neues Terminal-Tab **nicht** — die IDE selbst neu starten. Sie vererbt die Umgebung ihres eigenen Starts |
| **Installiert in einer Sandbox-Umgebung der IDE** (etwa ein Flatpak mit eigenem Node) | `command -v claude` zeigt einen Pfad **unterhalb** des IDE-Datenverzeichnisses, z. B. `~/.var/app/…/node/bin/claude` | Diese Installation gibt es nur im integrierten Terminal. Rollen, die aus einer normalen Shell, aus `cron` oder aus einem Dienst starten, sehen sie nie. Für den Benutzer neu installieren (nativer Weg → `~/.local/bin`) |
| **Nicht-interaktive Shell** — Start aus `cron`, `systemd`, einem CI-Runner | Von Hand läuft es, geplant nicht | Diese Prozesse lesen `~/.bashrc` nicht und starten mit einem minimalen PATH. `PATH` im Job-Aufruf selbst setzen, `~/.local/bin` inbegriffen |

Die Gegenprobe ist in allen drei Fällen dieselbe — **aus derselben Umgebung, in
der die Rollen laufen**, nicht aus der bequemen:

```bash
env -i HOME="$HOME" PATH="$PATH" bash -lc 'command -v claude && claude --version'
```

### Und danach

Installiert heißt nicht betriebsbereit. Es fehlen noch zwei Schritte, und beide
stehen ausführlich in [einrichtung.md](einrichtung.md):

```bash
claude                                          # einmalig: /login → Konto wählen → /exit
bash ~/Source/team-kit/bash/scripts/team-auth-setup.sh
```

```powershell
claude                                          # einmalig: /login → Konto wählen → /exit
pwsh -File .\pwsh\scripts\team-auth-setup.ps1
```

Claude Code braucht ein Konto mit Pro-, Max-, Team-, Enterprise- oder
Console-Zugang; der kostenlose Claude.ai-Tarif schließt Claude Code nicht ein.
`team-auth-setup` setzt danach das Abo als Priorität 1 und legt einen etwaigen
API-Key als **geschützten Fallback** ab, statt ihn in der Umgebung stehen zu
lassen — warum das die tragende Reihenfolge ist, steht in
[anhang-a.md, A.3](anhang-a.md#a3-auth-fallback--erprobt-für-alle-automatisierten-rollen).

Die abschließende Gegenprobe ist nicht `claude --version`, sondern der Aufruf,
den das Kit tatsächlich macht — headless, mit maschinenlesbarer Antwort:

```bash
env -u ANTHROPIC_API_KEY claude -p "sag ok" --output-format json
```

### Belegstand

- **Die Kit-Seite ist verifiziert.** Dass eine fehlende CLI eine Warnung und
  keinen Abbruch auslöst, dass die pwsh-Bahn den PATH-Fall mit eigenem Wortlaut
  vom Auth-Fall trennt, und dass es genau eine Aufrufstelle gibt — das steht im
  Code des Kits und unter Test.
- **Die Installationsbefehle stammen aus der Herstellerdoku**
  (`code.claude.com/docs/en/setup`, abgerufen am 20.08.2026) und sind hier
  nicht auf jeder Bahn nachgefahren worden. Auf der Entwicklungsmaschine des
  Kits ist der npm-Weg unter Linux im Betrieb (Claude Code 2.1.206); die
  native Installation, der apt-Weg, WinGet und der CMD-Weg sind
  **übernommen, nicht durchlaufen**. Fremde Befehle altern schneller als
  dieses Repo: Im Zweifel gilt die Herstellerdoku, nicht diese Seite.
- **Der Sandbox-Fall ist ein Feldbefund**, kein hergeleiteter: Auf der
  Entwicklungsmaschine liegt die CLI im Node-Verzeichnis eines Flatpak-Editors
  und ist außerhalb von dessen Terminal unsichtbar.

---

## Verwandte Seiten

- [einrichtung.md](einrichtung.md) — die Routine; dort auch die
  [Fehlerbilder](einrichtung.md#fehlerbilder) als Symptomtabelle
- [anhang-a.md](anhang-a.md) — die Warum-Schicht, u. a. A.3 (Auth-Fallback)
  und A.12 (warum die Maschine vor dem Projekt kommt)
- [README, *Betrieb*](../README.md#betrieb) — Befehle und Exit-Codes

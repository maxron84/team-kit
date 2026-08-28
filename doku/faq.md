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
| [Der Lauf endete mit `42` oder `43` — was mache ich jetzt?](#der-lauf-endete-mit-42-oder-43--was-mache-ich-jetzt) | Beides ist **kein** Fehler. `42` heißt warten, `43` heißt nachsehen — und `43` neu zu bauen hat im Feld viermal die bereits bezahlte Arbeit gekostet |
| [Wie hole ich eine abgewählte Bahn zurück?](#wie-hole-ich-eine-abgewählte-bahn-zurück) | Ein `--update` **ohne** Schalter. Die Falle liegt nicht beim Zurückholen, sondern beim Abwählen im Update |
| [Warum kostet mein Lauf mehr als geschätzt?](#warum-kostet-mein-lauf-mehr-als-geschätzt) | Meist keine Abweichung, sondern zwei verschiedene Zahlen — und eine davon war bis `Kit-BL-141` gar keine Messung |

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

## Der Lauf endete mit `42` oder `43` — was mache ich jetzt?

**So sieht es aus:**

| Exit | Zeile im Protokoll |
|---|---|
| `42` | `⏸ Session-Limit erreicht — Lauf pausiert (Ralph). Bitte später './vollautomatik.sh' erneut starten. Kein Fehler, kein Datenverlust (State steht).` |
| `43` | `⚠ Stufe fertig, Quittung fehlt (BL-41) — Lauf gestoppt. NICHT neu bauen, bevor die von Ralph genannten zwei Prüfungen gelaufen sind.` |

**Einordnung vorweg:** Beides sind **eigene Ausgänge neben `0` und `1`**, und
genau das ist ihr Zweck. Ein Lauf, der pausiert, und ein Lauf, dessen Arbeit
fertig ist und nur die Quittung vermissen lässt, sind **keine Fehler** — sie so
zu behandeln kostet Geld. Die Fehlerbilder-Tabelle in
[einrichtung.md](einrichtung.md#fehlerbilder) nennt die Codes; was zu **tun**
ist, steht hier.

### `42` — Session-Limit, der Lauf wartet auf dich

Das Kontingent des Abos ist erschöpft. Das Kit hat das erkannt (HTTP 429 oder
der Text „session limit"/„resets" in der Antwort), zuerst den **API-Fallback**
versucht — der hat ein eigenes Kontingent —, dann eine begrenzte Zahl von
Wiederholungen, und ist erst danach ausgestiegen.

**Was du tust: nichts, außer später erneut starten.**

```bash
./vollautomatik.sh        # nimmt den Faden am Zeigerstand auf
```

Der Zustand steht: `.ralph-state` ist **nicht** fortgeschritten, kein
Fehlversuchs-Zähler wurde erhöht, keine Stufe gilt als erledigt. Alle
Rollen-Skripte reichen `42` unverändert durch, damit genau das gilt.

> **Was du NICHT tust:** den Zeigerstand von Hand anfassen. Ein `42` hat nichts
> verschoben — es gibt nichts zu reparieren.

Wenn `42` **zu früh** kommt, sind drei Stellschrauben da. Sie stehen in der
Konfiguration, nicht im Code:

| Variable | Vorgabe | Wirkung |
|---|---|---|
| `TEAM_429_MAX_RETRIES` | `2` | Wie oft nach einem Limit erneut versucht wird |
| `TEAM_429_MAX_WARTEN` | `1800` s | Längste Wartezeit auf den Reset; `0` schaltet den Auto-Retry ab |
| `TEAM_429_PUFFER` | `30` s | Aufschlag auf den gemeldeten Reset-Zeitpunkt |

Ist der Reset-Zeitpunkt unbekannt oder liegt er jenseits des Maximums, wartet
das Kit **gar nicht** und geht sofort in den Pausen-Exit — lieber ein sauberes
Warten durch dich als eine Stunde blockierter Prozess.

### `43` — die Stufe ist fertig, nur die Quittung fehlt

Die Rolle hat gearbeitet, das Log meldet Erfolg, aber das
`<promise>`-Kennzeichen fehlt. Der häufigste Grund: Sie hat auf einen
Hintergrund-Task gewartet, den es im headless-Betrieb nicht gibt.

**Die Arbeit ist mit hoher Wahrscheinlichkeit fertig.** Deshalb protokolliert
das Kit `43` ausdrücklich **nicht** als Fehler: Im Feld hat das Verwechseln mit
„endete mit Fehler" viermal zum Neubau statt zum Nachsehen geführt — zusammen
**19,47 USD** für Arbeit, die bereits bezahlt war (`Kit-BL-41`).

**Schritt 0 — ist es überhaupt dieser Fall?** Die Rolle hat dir beim Aussteigen
zwei Prüfungen genannt. Fahre sie, bevor du irgendetwas anderes tust:

```bash
git log -1 && git status                 # hat die Rolle committet?
<dein Smoke-Test aus team.config.*>      # ist der Baum grün?
```

Dann entscheidest du **entlang des Ergebnisses**, nicht nach Gefühl:

| Befund | Was das heißt | Was du tust |
|---|---|---|
| Committet **und** Baum grün | Die Stufe ist fertig, nur die Quittung fehlt | Von Hand quittieren: `echo <N+1> > .ralph-state`, dann erneut starten |
| Baum rot, und rot sind **ausschließlich** die von dieser Stufe **neu angelegten** Testdateien (`git status` zeigt sie als `??`) | Der Testaufbau ist der wahrscheinlichere Schuldige als der Produktivcode | Den Aufbau von Hand reparieren — **ohne** eine Zusicherung abzuschwächen. Nicht neu bauen |
| Rot ist **bestehender** Testbestand | Die Stufe hat etwas gebrochen | Jetzt ist Neubau richtig |
| Nicht committet | Die Arbeit ist nicht da | Neu bauen |
| Baum rot, aber es lief noch ein **zweiter** Testlauf | Das Ergebnis ist eine Eigenschaft der Maschine, nicht des Codes | Allein nachmessen, wenn der andere Lauf durch ist. **Nicht** neu bauen |

> **Die dritte Zeile ist die, die im Feld übersehen wurde.** „Baum rot" heißt
> nicht automatisch „Stufe kaputt" — es kommt darauf an, **wo** er rot ist. Eine
> Zusicherung abzuschwächen, damit die Suite grün wird, macht den Test wertlos
> und den Befund unsichtbar.

> **Die LETZTE Zeile ist die teuerste Falle (`Kit-BL-207`).** Zwei
> gleichzeitige Testläufe kollidieren — über Datenbankdateien, Ports,
> Nutzerverzeichnisse. Im Feld hat das einen **grünen** Baum als rot gemeldet,
> mitsamt der Empfehlung, im Testaufbau zu suchen; ein Neubau hätte 2,36 USD
> fertige Arbeit weggeworfen. Die Selbstprüfung erkennt den Fall inzwischen
> selbst und meldet dann **UNBEKANNT statt rot** — steht das im Protokoll,
> ist nichts kaputt, es ist nur nichts gemessen.

> **Warum die Rolle überhaupt in den Hintergrund ausweicht:** weil die Suite
> irgendwann länger läuft als die Vordergrundgrenze des Agenten-Werkzeugs.
> Deshalb trägt die Auflage seit `Kit-BL-207` eine Zahl
> (`TEAM_SMOKE_TEST_TIMEOUT`, Default 600 s), die im Prompt jeder bauenden
> Rolle steht. Läuft deine Suite länger, **heb den Wert an** — sonst weicht
> die Rolle weiter aus, und zwar zu Recht.

### Belegstand

- **Beide Codes und ihre Behandlung stehen im Code des Kits und unter Test** —
  `vollautomatik.sh` reicht `42` aus jeder Phase durch und behandelt `43` als
  eigenen Ausgang; die ersten **vier** Entscheidungszeilen oben sind wörtlich
  die Prüfungen, die `ralph.sh` beim Aussteigen ausgibt. Die **fünfte**
  stammt nicht von dort, sondern aus der Selbstprüfung: Sie erkennt einen
  laufenden zweiten Verifikationslauf und meldet ihn als UNBEKANNT
  (`Kit-BL-207`).
- **Die 19,47 USD sind ein Feldbetrag**, kein hergeleiteter — vier Neubauten
  desselben Falls, bevor `Kit-BL-41` den eigenen Ausgang einführte.

---

## Wie hole ich eine abgewählte Bahn zurück?

**So sieht es aus:** In deinem Projekt liegen nur `.sh`-Dateien und keine
`.ps1`/`.cmd` (oder umgekehrt). `TEAM.md` zeigt eine Zwei-Bahnen-Tabelle, aber
eine Spalte gibt es bei dir nicht.

**Einordnung vorweg:** Das ist **kein Defekt**. Bei der Installation wurde
`--nur-bash` bzw. `--nur-pwsh` gesetzt — eine ausdrückliche Abwahl. Wer sie
trifft, trägt die Folge, statt sie geerbt zu bekommen; das ist der ganze Sinn
des Schalters (`Kit-BL-119`).

### Schritt 0 — ist es überhaupt eine Abwahl?

```bash
ls *.sh *.ps1 2>/dev/null | wc -l    # welche Bahnen liegen hier?
ls team.config.*                     # eine Konfiguration je Bahn
```

Fehlt eine Bahn **vollständig** (Entrypoints *und* Bibliothek *und*
Konfiguration), war es eine Abwahl. Fehlen nur einzelne Dateien, ist etwas
anderes passiert — dann ist ein `--update` trotzdem der richtige nächste
Schritt, aber lies dessen Bericht.

### Der Rückweg: `--update --beide-bahnen`

```bash
bash <kit-pfad>/bash/install.sh . --update --beide-bahnen
```

```powershell
pwsh -File <kit-pfad>\pwsh\install.ps1 . -Update -BeideBahnen
```

**Der Schalter ist seit `Kit-BL-147` nötig, und das ist der Punkt.** Vorher
genügte ein `--update` ohne alles — wer bloß eine neue Kit-Version wollte,
bekam die abgewählte Bahn zurück, ob er sie wollte oder nicht. Im Feld waren
das **21 ungebetene pwsh-Dateien** in einem reinen Bash-Projekt. Ein `--update`
**hält** die Bahn heute und meldet, dass es sie erkannt hat:

```
Einbahnige Ablage erkannt: nur die bash-Bahn (BL-147)
```

Erkannt wird an den Dateien, die das **Kit** ausliefert, nicht an Endungen —
ein projekteigenes `deploy.ps1` macht aus deinem Projekt keine pwsh-Ablage.

Das Update **mit** dem Schalter macht das Projekt wieder vollständig — Entrypoints, Bibliothek **und
die fehlende Konfiguration**. Die Konfiguration ist der Teil, der beim ersten
Bau vergessen wurde: Ein Update fasst `team.config.*` grundsätzlich nicht an,
also kamen die Entrypoints zurück und die Werte nicht. Der Update-Pfad
**erzeugt** eine fehlende Bahn-Konfiguration heute neu — aus den Werten der
**vorhandenen**, nicht aus den Auslieferungswerten. Sonst bekäme die
zurückgeholte Bahn eine andere Guard-Grenze als die, die schon läuft, und der
Guard schützte den falschen Ordner.

Der Lauf sagt dir, dass er es getan hat:

```
team.config.ps1 fehlte und ist neu erzeugt worden
Projektwerte aus team.config.sh gelesen
```

### Die eigentliche Falle liegt woanders

**Ein `--update` MIT Schalter wählt nicht ab — es hört nur auf zu
aktualisieren.** `--nur-pwsh` beim Update lässt die `.sh`-Dateien **liegen**;
sie veralten dann still. Und die Testsuite entscheidet **an ihrer Anwesenheit**,
welche Bahn sie fährt. Ein so behandeltes Projekt fährt also Tests gegen
Dateien, die niemand mehr pflegt.

Beide Installer melden das inzwischen ausdrücklich. **Gelöscht wird nichts** —
eine Datei, die das Kit nicht angelegt hat, löscht es auch nicht
(`Kit-BL-12`).

> **Wenn du eine Bahn wirklich loswerden willst**, ist das eine Entscheidung für
> dich und `git rm`, nicht für den Installer. Er meldet den Zustand; er räumt
> ihn nicht auf.

### Belegstand

- **Beides ist unter Test**, in beiden Richtungen: `kit-test.sh` Stufe 8 baut
  je eine einbahnige Ablage, fährt dort die Suite, prüft dann, dass ein
  schlichtes `--update` die Ablage **einbahnig lässt** (`Kit-BL-147`), und holt
  erst danach die fehlende Bahn per `--beide-bahnen` zurück — inklusive der
  Zusicherung, dass die Konfiguration mit den **Projektwerten** wiederkommt und
  keine Platzhalter übrig bleiben.
- **Dass die Tests in einer einbahnigen Ablage grün bleiben**, gilt seit
  `Kit-BL-129` für **beide** Richtungen; vorher war nur eine geprüft.

---

## Warum kostet mein Lauf mehr als geschätzt?

**So sieht es aus:** `--budget` zeigt eine Zahl, die Konsole oder dein Gefühl
zeigen eine andere.

**Einordnung vorweg:** Meistens ist das **keine Abweichung, sondern zwei
verschiedene Zahlen.** Lies zuerst die Beschriftung, dann die Zahl.

### Schritt 0 — welche Zahl liest du überhaupt?

```bash
./team-status.sh --budget
```

| Zeile | Was sie ist | Bezugsrahmen |
|---|---|---|
| `Ralph-Logs`, `Team-Logs` | **Abgerechnete** Beträge aus den Rohlogs der headless gelaufenen Rollen | seit dem letzten Closeout |
| `Architekt K<N> (echt, im Gesamt enthalten)` | Eine **gebuchte Ledger-Zeile** dieser Kaskade | **eine** Kaskade |
| `Architekt K<N> (Churn-Proxy, nicht im Gesamt enthalten)` | **Keine Messung** — siehe unten | **eine** Kaskade |
| `Gesamt-Kontostand (inkl. Ledger)` | Lebenslange Summe | seit Projektbeginn |

**Die häufigste Verwechslung** ist die dritte gegen die vierte Zeile: Der
Architektenwert gilt für **eine** Kaskade, die Zeilen daneben kumulieren
lebenslang. Im Feld ergab der beim Wort genommene Kontostand einmal 81,27 statt
71,57 USD — 13 % zu viel, weil der Architekt ein zweites Mal addiert wurde
(`Kit-BL-18`). Deshalb sagt die Zeile selbst, ob sie im Gesamt schon steckt.

### Der Churn-Proxy ist keine Schätzung deines Verbrauchs

Steht dort `Churn-Proxy`, ist die Zahl **Zeilen-Churn mal Eichfaktor** — sie
misst die **Größe des Diffs**, nicht die Arbeit. Eine Sitzung mit viel Lesen,
Prüfen und Gegenproben wird systematisch unterschätzt; im Feld lag sie **35 %
zu niedrig** (`Kit-BL-141`).

**Gemessen wird so:**

```
<dein Python> team/tools/kosten.py sitzung-messen --projekt .
```

Das Werkzeug liest das Sitzungstranskript, dedupliziert über die
Nachrichten-ID und **eicht sich an den abgerechneten Läufen deines Projekts**.
Sagt es „Preistabelle stimmt nicht mehr", ist die Zahl **ungeeicht** — dann
nicht buchen, sondern die Tabelle nachziehen (Exit `2`).

Gemessen wird die **letzte** Sitzung des Projekts. Liegen mehrere Transkripte
vor, sagt das Werkzeug es und nennt `--alle` — erstreckt sich eine Kaskade über
mehrere Sitzungen (Planung und Closeout getrennt), buchst du sonst zu wenig
(`BL-186`).

### Warum die Zahl höher ist, als das Ergebnis vermuten lässt

Der **Löwenanteil entfällt auf das erneute Vorlegen des Kontexts**, nicht auf
den erzeugten Text. Eine lange Sitzung legt bei jedem Schritt den gesamten
bisherigen Verlauf wieder vor. In einer gemessenen Bau-Sitzung dieses Kits
standen rund 58 Millionen `cache_read`-Token gegen 211 000 erzeugte — ein
Verhältnis von etwa 280 zu 1.

Daraus folgen drei Dinge, die im Betrieb wirklich helfen:

| Beobachtung | Was sie bedeutet |
|---|---|
| Kosten wachsen **überproportional** zur Sitzungslänge | Eine Kaskade je Sitzung abschließen, nicht drei |
| Ein Aufruf kann **mehrfach** stattfinden | Jeder Versuch ist bezahlt. Das Kit summiert deshalb **alle** Versuchs-Logs, nicht nur den letzten (`Kit-BL-55`) |
| Der Pro-Lauf-Deckel greift **nicht** gegen den Gesamtstand | Er ist die operative Grenze **eines** Laufs; der Gesamtstand ist dokumentiert, nicht durchgesetzt |

### Wenn eine Kaskade wirklich doppelt zählt

Dann fehlt die **Archivierung** der Rohlogs. Reihenfolge im Closeout:
Ledger-Zeile anhängen → **direkt danach** archivieren. Fehlt der zweite Schritt,
zählt jede abgeschlossene Kaskade doppelt, weil die Logs im gezählten Pfad
liegen bleiben. `--rollen-abschluss` tut beides in **einem** Aufruf — genau
deshalb.

Prüfen statt glauben:

```bash
./team-status.sh --ledger-pruefen
```

Exit `4` heißt Warnbefunde. Die Prüfung hält die **archivierten Rohlogs** gegen
das Ledger, also eine **andere** Quelle — ein Bericht, der seine Kennzahl aus
derselben Quelle zieht wie das Geprüfte, bestätigt einen Fehler, statt ihn zu
zeigen.

### Belegstand

- **Die Verhältniszahl 280 : 1 ist gemessen**, nicht geschätzt: aus dem
  Transkript der Sitzung, in der `Kit-BL-141` gebaut wurde (58 806 159
  `cache_read`-Token gegen 210 804 erzeugte).
- **Die 35 % und die 13 % sind Feldbeträge** aus `Feld B` bzw.
  `Feld A`, keine Modellrechnungen.
- **Die Preistabelle des Messwerkzeugs ist gegen die Herstellerangaben
  geprüft** und eicht sich zusätzlich an den abgerechneten Läufen des Projekts
  selbst — weicht sie ab, sagt das Werkzeug es, statt eine Zahl zu buchen.
---

## Verwandte Seiten

- [einrichtung.md](einrichtung.md) — die Routine; dort auch die
  [Fehlerbilder](einrichtung.md#fehlerbilder) als Symptomtabelle
- [anhang-a.md](anhang-a.md) — die Warum-Schicht, u. a. A.3 (Auth-Fallback)
  und A.12 (warum die Maschine vor dem Projekt kommt)
- [README, *Betrieb*](../README.md#betrieb) — Befehle und Exit-Codes

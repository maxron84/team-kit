# Einrichtung — vom `git clone` bis zum ersten Lauf

Diese Seite ist die Routine für zwei Maschinen: **Linux** und **Windows mit
WSL**. Sie beschreibt zwei Vorgänge, die gern verwechselt werden:

| Vorgang | Was passiert | Wie oft |
|---|---|---|
| **Klonen und einrichten** | Das Kit-Repo landet auf der Maschine, die Bordmittel werden geprüft, die Auth des Agenten-Werkzeugs steht | einmal pro Maschine |
| **Einbinden** | `install.sh` legt die 75 Dateien in ein **Zielprojekt** | einmal pro Projekt |

Der kurze Weg steht ganz oben; alles darunter ist die Begründung und der
Fehlerfall.

---

## Was Pflicht ist und was Beispiel

Das Kit ist auf **Agnostik von Umgebungen, Werkzeugen und Modellen** angelegt.
Diese Anleitung nennt trotzdem konkrete Produkte, weil eine Anleitung ohne
Produktnamen niemanden zum Laufen bringt. Die Trennlinie:

| Schicht | Pflicht | Beispiel in dieser Anleitung | Warum die Pflicht Pflicht ist |
|---|---|---|---|
| Betriebssystem | POSIX-Umgebung mit `bash` ≥ 4 | Linux; Windows über WSL2 (WSL1 nur mit [Gegenprobe](#wenn-nur-wsl-1-geht--vm-gesperrte-firmware-verwalteter-rechner)) | Das Kit ist eine Sammlung von Bash-Skripten und nutzt indirekte Expansion (`${!var}`) |
| Bordmittel | `git`, `python3` ≥ 3.8, `flock` | — | Git trägt Commit, Rollback und Guard; `team/tools/` ist Python; `flock` serialisiert Ledger und Kaskadenstand |
| Testrunner | `pytest` (nur für `team-test.sh`/`kit-test.sh`) | — | Die Rollen selbst brauchen ihn nicht |
| **IDE** | **keine** | VS Codium (Linux), VS Code + WSL-Erweiterung (Windows) | Das Kit wird im Terminal bedient. Ein Editor ist Komfort |
| **Agenten-Werkzeug** | **eine** CLI, die headless arbeitet und ein maschinenlesbares Ergebnis liefert | Claude Code (`claude -p`) | Die einzige Aufrufstelle ist `team_claude()` in [team/lib.sh](../team/lib.sh) |
| **Modell** | zwei Stufen: schwach und stark | `sonnet` / `opus` als Default | Die Rollen sprechen `TEAM_MODEL_LOOP`/`TEAM_MODEL_STRONG` an, keine Modellnamen — siehe [README, Abschnitt *Modelle*](../README.md#modelle--agnostisch-aber-nicht-anspruchslos) |

Wo unten `claude` steht, steht ein **Werkzeug**; wo `codium` steht, steht ein
**Editor**. Was beim Tausch zu tun ist, steht in
[Ein anderes Werkzeug, eine andere IDE, ein anderes Modell](#ein-anderes-werkzeug-eine-andere-ide-ein-anderes-modell).

---

## Der kurze Weg — Linux

```bash
# 1. Bordmittel (Debian/Ubuntu; andere Distributionen siehe unten)
sudo apt install git python3 python3-pytest util-linux

# 2. Klonen
git clone https://github.com/maxron84/team-kit.git ~/Source/team-kit
cd ~/Source/team-kit

# 3. Maschine prüfen und einrichten — und gleich in ein Projekt einbinden
bash kit-einrichten.sh ~/Source/mein-projekt
```

`kit-einrichten.sh` prüft Umgebung, Werkzeuge und die Lage des Klons, richtet
auf Wunsch die Auth ein, legt auf Wunsch den Kurzbefehl an und übergibt dann an
`install.sh`. Ohne Zielpfad prüft es nur die Maschine.

## Der kurze Weg — Windows mit WSL

```powershell
# In PowerShell als Administrator, danach Windows neu starten:
wsl --install -d Ubuntu
```

Danach **in der Distro** (Ubuntu-Terminal, nicht PowerShell) exakt dieselben
drei Schritte wie oben.

> **Die eine Regel, an der unter Windows alles hängt: Alles passiert in der
> Distro.** Klonen, Installieren, Laufenlassen, und das Repo liegt im
> **Linux**-Dateisystem (`~/Source/…`), nicht unter `/mnt/c/…`. Warum, steht
> unter [Die eine Regel](#2-die-eine-regel-linux-dateisystem).

---

## Linux im Detail

### 1. Bordmittel

| Distribution | Befehl |
|---|---|
| Debian, Ubuntu, Mint | `sudo apt install git python3 python3-pytest util-linux` |
| Fedora, RHEL | `sudo dnf install git python3 python3-pytest util-linux` |
| Arch, Manjaro | `sudo pacman -S git python python-pytest util-linux` |
| openSUSE | `sudo zypper install git python3 python3-pytest util-linux` |

`flock` steckt in `util-linux` und ist fast überall vorinstalliert. `pytest`
darf auch aus `pipx install pytest` kommen.

### 2. Klonen

```bash
git clone https://github.com/maxron84/team-kit.git ~/Source/team-kit
```

Der Ort ist frei wählbar. `~/Source/team-kit` ist nur die Konvention, auf die
der Kurzbefehl als letzten Versuch zurückfällt; überschreibbar mit
`TEAM_KIT_PFAD`.

**Nicht** ins Zielprojekt klonen. Das Kit lebt **neben** deinen Projekten und
schiebt Dateien hinein — es wird keine Abhängigkeit von ihnen.

### 3. Maschine einrichten

```bash
cd ~/Source/team-kit
bash kit-einrichten.sh            # nur prüfen und einrichten
bash kit-einrichten.sh --nur-pruefen   # gar nichts anfassen
```

Fünf Abschnitte, in dieser Reihenfolge:

1. **Umgebung** — Linux oder WSL, und ob es WSL2 ist. WSL1 ist eine Warnung,
   kein Abbruch — was dann zu tun ist, steht unter
   [Wenn nur WSL 1 geht](#wenn-nur-wsl-1-geht--vm-gesperrte-firmware-verwalteter-rechner).
2. **Werkzeuge** — `bash` ≥ 4, `git`, `python3` ≥ 3.8, `flock` sind Fehler,
   wenn sie fehlen; `pytest` und die Agenten-CLI nur Hinweise.
3. **Lage des Klons** — Zeilenenden, Dateisystem, und zwei **Proben** statt
   Annahmen: Greift `chmod +x` hier? Hält `flock` hier?
4. **Auth** — legt auf Wunsch `~/.config/claude-team/` an (Abo als Prio 1).
5. **Kurzbefehl** — verknüpft `scripts/team-init.sh` und
   `scripts/team-auth-setup.sh` nach `~/.claude/scripts/`, als **Symlink**, nie
   als Kopie. Eine schon vorhandene echte Datei wird gemeldet, nicht ersetzt.

Exit `0` = bereit (Warnungen möglich), `1` = mindestens ein harter Fehler.

### 4. IDE — VS Codium (Empfehlung für Linux)

Für das Kit reicht ein Terminal. Wer eine IDE will, nimmt unter Linux
sinnvollerweise **VS Codium**: derselbe Editor-Kern wie VS Code, aber ein Build
ohne Telemetrie und mit dem offenen Erweiterungs-Marktplatz Open VSX.

```bash
# z. B. als Flatpak
flatpak install flathub com.vscodium.codium
codium ~/Source/mein-projekt
```

Nützlich, aber **nichts davon ist Pflicht**: eine Bash-/ShellCheck-Erweiterung,
eine Python-Erweiterung, das integrierte Terminal.

> ⚠ **Der Fallstrick, den die IDE mitbringt: geerbte Umgebungsvariablen.** Ein
> `export ANTHROPIC_API_KEY=…` im Shell-Profil hat **Vorrang vor dem
> Abo-Login** — der Lauf funktioniert tadellos und wird nur komplett über die
> API abgerechnet. Im Feld kostete das einen ~13,8-USD-Leerlauf-Lauf. Das
> IDE-Terminal erbt diesen Wert beim Start der IDE: Wer den Key mit
> `team-auth-setup.sh` umzieht, muss **die IDE neu starten**, nicht nur ein
> neues Terminal-Tab öffnen. Details in [anhang-a.md, A.3](anhang-a.md).

### 5. Agenten-Werkzeug (Beispiel: Claude Code)

```bash
npm install -g @anthropic-ai/claude-code     # eine von mehreren Installationsarten
claude          # einmalig: /login → Konto wählen → /exit
bash ~/Source/team-kit/scripts/team-auth-setup.sh
```

`team-auth-setup.sh` ist idempotent. Es setzt `~/.config/claude-team/auth-mode`
auf `abo`, holt einen eventuell im Shell-Profil liegenden API-Key **dort heraus**
und legt ihn als geschützten Fallback nach `~/.config/claude-team/api-key`
(`chmod 600`). Auf Wunsch testet es das Abo headless.

### 6. Einbinden

Siehe [Die Einbindung](#die-einbindung--auf-beiden-plattformen-gleich).

---

## Windows mit WSL im Detail

### 1. WSL bereitstellen

```powershell
wsl --install -d Ubuntu       # PowerShell als Administrator, danach Neustart
wsl -l -v                     # Kontrolle: VERSION soll 2 sein
wsl --set-version Ubuntu 2    # falls dort 1 steht
```

WSL**1** übersetzt Linux-Syscalls, statt sie auszuführen. Für Dateisperren und
Rechte — also für genau die zwei Mechaniken, an denen das Kit hängt — gibt es
dort keine Zusicherung. `kit-einrichten.sh` warnt, wenn es WSL2 nicht erkennt.

#### Wenn nur WSL 1 geht — VM, gesperrte Firmware, verwalteter Rechner

Das Kit **blockt WSL 1 nicht**. Die Meldung in `kit-einrichten.sh` ist eine
Warnung, kein Fehler; abgebrochen wird nur bei Ablage unter `/mnt/…` und bei
fehlgeschlagenen Proben. Der Weg in drei Schritten:

**a) Erst prüfen, ob WSL 2 wirklich ausgeschlossen ist.** In einer VM scheitert
WSL 2 fast immer an fehlender *nested virtualization*, und die ist meist am
**Hypervisor** einschaltbar — nicht im Gast:

| Host | Schalter (VM ausgeschaltet) |
|---|---|
| Hyper-V | `Set-VMProcessor -VMName <VM> -ExposeVirtualizationExtensions $true`; dynamischen Speicher aus |
| VMware Workstation / ESXi | VM-Einstellungen → Prozessoren → *Virtualize Intel VT-x/EPT bzw. AMD-V/RVI* |
| VirtualBox 7 | `VBoxManage modifyvm <VM> --nested-hw-virt on` |
| KVM / Proxmox | CPU-Typ `host`, Modul mit `nested=1` |
| Cloud | Azure ab Dv3/Ev3 ja · GCP mit Lizenz-Flag · AWS nur `*.metal` |

Im Gast danach *Virtual Machine Platform* aktivieren und
`wsl --set-version <Distro> 2`.

**b) Bleibt es bei WSL 1: proben statt glauben.** Die Erwartung ist gut —
WSL 1 legt `~/` auf VolFs ab und trägt die Linux-Metadaten in NTFS-Attribute
ein, `chmod +x` hält also, und `flock()` ist implementiert. Aber die Probe in
`kit-einrichten.sh` ist `flock -n <datei> true`, also **ein** Prozess: Sie
belegt, dass der Aufruf gelingt, nicht dass zwei Prozesse sich wirklich
ausschließen. Auf einem echten Kernel ist das dasselbe, auf einer
Syscall-Übersetzung nicht zwingend. Deshalb auf dem Zielrechner zusätzlich:

```bash
bash kit-einrichten.sh --nur-pruefen     # Warnung „nicht erkennbar WSL2" ist hier erwartet

L=~/probe.lock                            # Zwei-Prozess-Gegenprobe für die Sperre
bash -c 'exec 9>"$0"; flock -x 9; echo "A: Sperre gehalten"; sleep 2' "$L" &
sleep 0.5
bash -c 'exec 9>"$0"; if flock -n 9; then echo "B: bekam sie AUCH -> flock greift NICHT"; else echo "B: abgewiesen -> flock greift"; fi' "$L"
wait; rm -f "$L"
```

„B: abgewiesen" heißt: Ledger und Kaskadenstand sind serialisiert, und
[`vollautomatik.sh`](../entry/vollautomatik.sh) — sequenziell, hält das Lock über
den ganzen Lauf — steht auf sicherem Grund. Kommt „B: bekam sie AUCH", gilt
genau die Warnung: Zwei Rollen können unbemerkt gleichzeitig schreiben. Dann
ist die Disziplin die Sperre: **immer nur ein Lauf**, und während eines Laufs
kein zweites Terminal auf dasselbe Projekt.

**c) Was auf WSL 1 strenger gilt als auf WSL 2:**

| Punkt | Auf WSL 1 |
|---|---|
| `/mnt/c` | doppelt verboten — DrvFs *und* Syscall-Übersetzung. Der Köder: WSL 1 ist auf `/mnt/c` **schneller** als WSL 2. Die Rechte- und Sperrprobleme bleiben trotzdem, siehe [Die eine Regel](#2-die-eine-regel-linux-dateisystem) |
| Tempo unter `~/` | spürbar langsamer als WSL 2 auf ext4, weil jeder Datei-Syscall übersetzt wird. Das Kit committet und testet pro Stufe — das schlägt in Wartezeit durch, nicht in Kosten |
| Kein echter Kernel | `inotify`, cgroups und Teile von `/proc` sind unvollständig. Für `bash`, `git` und `python3` unkritisch; für Node-Werkzeuge in aller Regel auch, aber unbelegt |

Und die ehrliche Reihenfolge, falls die Wahl offensteht: Bei einer VM ist
**Linux direkt als Gast** der kürzere Weg — das Kit ist dort erprobt, der
WSL-Weg ist hergeleitet (siehe [Belegstand](#belegstand)) und WSL 1 liegt noch
eine Stufe darunter.

### 2. Die eine Regel: Linux-Dateisystem

**Das Repo und das Zielprojekt liegen unter `~/` in der Distro, nicht unter
`/mnt/c/…`.** Drei Gründe, alle mit demselben Muster — es sieht aus wie ein
kaputtes Kit und ist keines:

| Was auf `/mnt/c` passiert | Wie es sich zeigt |
|---|---|
| `chmod +x` verpufft (DrvFs ohne `metadata`) | `install.sh` setzt die Entrypoints ausführbar, es bleibt folgenlos: `./vollautomatik.sh: Permission denied` |
| Git sieht dauernd Rechteänderungen | Ein Arbeitsbaum, der nie sauber ist — und der Read-Only-Guard bewertet unerwartete Dateien im Baum |
| `flock` auf einem Dateisystem ohne Zusicherung | Zwei Rollen schreiben unbemerkt gleichzeitig auf Ledger und Kaskadenstand |

Dazu ist der Zugriff über die 9p-Brücke deutlich langsamer — bei einem Repo,
das pro Stufe committet und testet, ist das nicht nur Komfort.

`kit-einrichten.sh` **bricht ab**, wenn Kit oder Zielprojekt unter `/mnt/`
liegen. Wer es wider besseres Wissen will:
`TEAM_EINRICHTEN_ERLAUBE_DRVFS=1 bash kit-einrichten.sh`.

Aus Windows erreichbar bleibt alles trotzdem — im Explorer über
`\\wsl$\Ubuntu\home\<benutzer>\Source`.

### 3. Zeilenenden

Git for Windows klont per Default mit `core.autocrlf=true`. Ein so entstandener
Klon trägt CRLF, und die erste Zeile jedes Skripts wird zu
`#!/usr/bin/env bash\r` — bash sucht dann einen Interpreter namens `bash\r`:

```
bash: ./vollautomatik.sh: /usr/bin/env: bad interpreter: No such file or directory
```

Zwei Dinge halten dagegen:

- Das Kit liefert eine [`.gitattributes`](../.gitattributes) mit `* text=auto eol=lf`
  aus. Ein **neuer** Klon bekommt LF, egal wie die Maschine konfiguriert ist.
- `kit-einrichten.sh` prüft die Skripte trotzdem — für Klone, die vor dieser
  Datei entstanden sind oder über Windows kopiert wurden.

Empfehlenswert in der Distro, einmalig: `git config --global core.autocrlf input`.

### 4. Bordmittel in der Distro

```bash
sudo apt update && sudo apt install git python3 python3-pytest util-linux
```

**In der Distro**, nicht in Windows. Ein Windows-`git.exe` oder ein
Windows-`node.exe` über `/mnt/c` aufzurufen funktioniert scheinbar und bringt
genau die Pfad- und Zeilenenden-Probleme zurück, die die Regel oben vermeidet.

### 5. Klonen und einrichten

```bash
git clone https://github.com/maxron84/team-kit.git ~/Source/team-kit
cd ~/Source/team-kit
bash kit-einrichten.sh ~/Source/mein-projekt
```

### 6. IDE — VS Code mit der WSL-Erweiterung

Unter Windows ist **VS Code** hier das praktikable Beispiel, und zwar aus einem
Lizenzgrund, nicht aus Geschmack: Microsofts Remote-Erweiterungen (darunter
**WSL**) sind für VS Code lizenziert und stehen in Open VSX nicht zur
Verfügung — VS Codium kann sie nicht regulär beziehen. Deshalb die Empfehlung
oben für Linux und diese hier für Windows.

1. VS Code in **Windows** installieren.
2. Erweiterung **WSL** (Microsoft) installieren.
3. In der Distro: `code ~/Source/mein-projekt` — oder in VS Code
   *Connect to WSL*.
4. **Kontrolle:** Unten links steht `WSL: Ubuntu`, und `pwd` im integrierten
   Terminal liefert einen Linux-Pfad. Steht dort ein `C:\`-Pfad, läuft die
   Sitzung in Windows und keiner der Befehle dieser Anleitung gilt.

Erweiterungen werden in einer WSL-Sitzung getrennt installiert („Install in
WSL: Ubuntu") — das ist Absicht und kein Fehler.

Wer Codium auch unter Windows will: Codium **in** der Distro als Linux-Anwendung
über WSLg betreiben, oder schlicht im Terminal arbeiten. Das Kit merkt keinen
Unterschied.

### 7. Agenten-Werkzeug in der Distro

Wie unter Linux (`npm install -g @anthropic-ai/claude-code`, `claude`, `/login`,
dann `scripts/team-auth-setup.sh`) — **in der Distro installiert**, nicht in
Windows. Ein aus Windows geerbter `ANTHROPIC_API_KEY` (etwa über
`WSLENV`) hat denselben Effekt wie einer im Shell-Profil: Er verdrängt das Abo.

---

## Die Einbindung — auf beiden Plattformen gleich

Ab hier gibt es keinen Plattformunterschied mehr.

```bash
bash ~/Source/team-kit/install.sh ~/Source/mein-projekt
# oder, nach --verknuepfen, von überall:
bash ~/.claude/scripts/team-init.sh ~/Source/mein-projekt
```

1. **Zielprojekt muss ein Git-Repo sein** — `git init` reicht. Neu oder seit
   Jahren gewachsen ist beides in Ordnung; für den Bestand siehe
   [README, *In ein bestehendes Projekt*](../README.md#in-ein-bestehendes-projekt).
2. **Das Aufnahme-Interview** stellt neun Fragen. Die Tabelle mit Defaults und
   Bedeutung steht im [README](../README.md#installation); der wichtigste Wert
   ist der **Smoke-Test**.
3. **Werte prüfen:** `team.config.sh` und die TODO-Stellen in `CLAUDE.md`.
4. **Committen — vor dem ersten Lauf, nicht danach:**
   ```bash
   git add -A && git commit -m "chore: T.E.A.M. eingerichtet"
   ```
   Der Read-Only-Guard wertet uncommittete Dateien außerhalb seiner Whitelist
   als Verletzung und räumt sie weg. Im Ursprungsprojekt hat das einmal die
   gesamte frisch gebaute Team-Infrastruktur gelöscht.
5. **Infrastruktur testen:** `./team-test.sh` (prüft das Team, nicht dein
   Projekt).
6. **Weiter in `TEAM.md`** — der Bedienanleitung, die jetzt im Projekt liegt.

Ein bestehendes Projekt auf eine neue Kit-Version heben: `--update`. Nie
`--force` (überschreibt Ledger, Kaskadenstand und Beutebuch).

---

## Gegenprobe — läuft es wirklich?

```bash
# auf der Maschine
bash ~/Source/team-kit/kit-einrichten.sh --nur-pruefen   # → "Alles grün", Exit 0
cd ~/Source/team-kit && ./kit-test.sh                    # → 9/9, dauert ein paar Minuten

# im Zielprojekt
./team-test.sh                                           # Infrastruktur-Tests
./team-status.sh                                         # Pipeline, Beutebuch, Kaskadenstand

# das Agenten-Werkzeug, headless und ohne Key in der Umgebung
env -u ANTHROPIC_API_KEY claude -p 'Antworte nur mit: pong'
```

`kit-test.sh` ruft **keine** Agenten-CLI auf und kostet daher nichts. Der letzte
Befehl kostet einen Mini-Anteil und ist der einzige Beweis, dass Auth wirklich
steht.

---

## Ein anderes Werkzeug, eine andere IDE, ein anderes Modell

| Tausch | Was zu tun ist | Aufwand |
|---|---|---|
| **Anderes Modell** | `TEAM_MODEL_LOOP` / `TEAM_MODEL_STRONG` in [team/lib.sh](../team/lib.sh) oder pro Lauf setzen | eine Zeile. Welche **Fähigkeiten** ein Kandidat mitbringen muss, steht im [README](../README.md#modelle--agnostisch-aber-nicht-anspruchslos) |
| **Andere IDE / keine** | nichts | Das Kit wird im Terminal bedient |
| **Andere Agenten-CLI** | `team_claude()` in [team/lib.sh](../team/lib.sh) austauschen — die **einzige** Stelle im Kit, die eine CLI aufruft | überschaubar, aber **nicht belegt**: An dieser Funktion hängen das Ergebnis-JSON (`is_error`, `subtype`, `total_cost_usd`), der Auth-Fallback und die 429-Mechanik. Wer tauscht, muss diese vier Dinge nachbauen — siehe [anhang-a.md, A.11](anhang-a.md) |
| **Anderes Auth-Verfahren** | `scripts/team-auth-setup.sh` ist ein Beispielskript für Claude Code, keine Kit-Mechanik | ersetzen |

Das Kit ist **modellagnostisch, aber nicht CLI-agnostisch**. Das ist eine
ehrliche Grenze, keine Absichtserklärung: Der einzige erprobte Weg zu einem
Modell führt heute über `claude -p`.

---

## Fehlerbilder

| Symptom | Ursache | Abhilfe |
|---|---|---|
| `/usr/bin/env: bad interpreter` | CRLF-Zeilenenden (Klon aus Windows) | In der Distro neu klonen; `git config --global core.autocrlf input` |
| `./vollautomatik.sh: Permission denied` | Exec-Bit greift nicht (DrvFs unter `/mnt/c`) | Repo ins Linux-Dateisystem verlegen; notfalls `chmod +x *.sh` |
| Alles quälend langsam unter WSL | Repo liegt unter `/mnt/c` (9p) | dito |
| `flock: … not implemented` oder Lauf hängt an der Sperre | Netz- oder Windows-Laufwerk | Repo auf ein lokales Linux-Dateisystem |
| `kit-einrichten.sh`: „nicht erkennbar WSL2" | Distro läuft unter WSL1 — in VMs meist fehlende nested virtualization | Warnung, kein Abbruch: [Wenn nur WSL 1 geht](#wenn-nur-wsl-1-geht--vm-gesperrte-firmware-verwalteter-rechner) — erst Hypervisor prüfen, sonst Zwei-Prozess-Gegenprobe für `flock` |
| `python3: command not found` mitten im Lauf | Bordmittel fehlt | `sudo apt install python3` — die Team-Werkzeuge sind Python |
| CLI meldet „takes precedence" | `ANTHROPIC_API_KEY` im Profil oder in der Umgebung | `scripts/team-auth-setup.sh`, dann `unset ANTHROPIC_API_KEY` — **und die IDE neu starten** (geerbte Umgebung) |
| `install.sh`: „ist kein Git-Repository" | Zielprojekt ohne Git | `git -C <ziel> init` |
| `team-test.sh` findet nichts | `pytest` fehlt | `sudo apt install python3-pytest` |
| `pytest team/tests` im **Kit-Repo** ist rot | Erwartet: Die Tests setzen die installierte Ablage voraus | Stattdessen `./kit-test.sh` |
| Lauf endet mit Exit `42` oder `43` | Kein Einrichtungsproblem: Session-Limit bzw. „Stufe fertig, Quittung fehlt" | [README, Exit-Codes](../README.md#betrieb) |

---

## Belegstand

Diese Anleitung folgt der Hausregel des Kits: Was verifiziert ist, wird als
verifiziert bezeichnet — der Rest nicht.

- **Linux: verifiziert.** Der komplette Weg (Klon, `kit-einrichten.sh`,
  `install.sh`, `kit-test.sh`) läuft auf der Entwicklungsmaschine des Kits
  (Linux 6.8, bash 5.3, git 2.55, Python 3.13, pytest 9.0, Claude Code 2.1.206).
- **Windows mit WSL: hergeleitet, nicht durchlaufen.** Die Regeln zu
  Dateisystem, Rechten und Zeilenenden folgen aus den bekannten Eigenschaften
  von DrvFs und Git for Windows, und `kit-einrichten.sh` prüft jede davon
  **an der Maschine** statt sie vorauszusetzen (Proben für `chmod +x` und
  `flock`). Ein vollständiger Durchlauf auf einer Windows-Maschine steht aus.
- **WSL 1: nicht zugesichert, aber nicht verboten.** Die Eigenschaften von
  VolFs (Metadaten in NTFS-Attributen) und die Implementierung von `flock()`
  in WSL 1 sprechen dafür, dass beide Proben grün werden — belegt ist das
  nicht, und die eingebaute Probe ist einprozessig. Deshalb steht dort die
  Zwei-Prozess-Gegenprobe: Sie entscheidet den Einzelfall an der Maschine,
  wie es A.12 für den ganzen WSL-Weg beschreibt.
- **IDEs: nicht Teil der Zusicherungen.** VS Codium und VS Code sind Beispiele.
  Das Kit kennt keine IDE.
- **Agenten-Werkzeug: ein erprobter Weg.** Claude Code. Alles andere ist als
  Tauschpunkt benannt (`team_claude()`), aber nicht belegt.

# Einrichtung — vom `git clone` bis zum ersten Lauf

Diese Seite ist die Routine für **drei Wege**: **Linux**, **Windows mit WSL**
und **Windows nativ** (PowerShell, ohne WSL). Sie beschreibt zwei Vorgänge, die
gern verwechselt werden:

| Vorgang | Was passiert | Wie oft |
|---|---|---|
| **Klonen und einrichten** | Das Kit-Repo landet auf der Maschine, die Bordmittel werden geprüft, die Auth des Agenten-Werkzeugs steht | einmal pro Maschine |
| **Einbinden** | `install.sh` legt die 126 Dateien in ein **Zielprojekt** | einmal pro Projekt |

Der kurze Weg steht ganz oben; alles darunter ist die Begründung und der
Fehlerfall.

---

## Was Pflicht ist und was Beispiel

Das Kit ist auf **Agnostik von Umgebungen, Werkzeugen und Modellen** angelegt.
Diese Anleitung nennt trotzdem konkrete Produkte, weil eine Anleitung ohne
Produktnamen niemanden zum Laufen bringt. Die Trennlinie:

| Schicht | Pflicht | Beispiel in dieser Anleitung | Warum die Pflicht Pflicht ist |
|---|---|---|---|
| Betriebssystem | **entweder** POSIX mit `bash` ≥ 4 **oder** PowerShell ≥ 7 | Linux; Windows über WSL2 (WSL1 nur mit [Gegenprobe](#wenn-nur-wsl-1-geht--vm-gesperrte-firmware-verwalteter-rechner)); Windows nativ | Das Kit hat **zwei Orchestrierungen** — Bash und PowerShell — die dieselben Python-Werkzeuge und dieselben Rollen-Briefings benutzen. Siehe [Windows nativ](#der-kurze-weg--windows-nativ-ohne-wsl) |
| Bordmittel | `git`, `python3` ≥ 3.8; auf dem Bash-Weg zusätzlich `flock` | — | Git trägt Commit, Rollback und Guard; `team/tools/` ist Python. Die Serialisierung von Ledger und Kaskadenstand macht auf dem Bash-Weg `flock`, auf dem PowerShell-Weg `[System.IO.FileStream]` — dort braucht es **kein** `flock` |
| Testrunner | `pytest` (nur für `team-test.sh`/`kit-test.sh`/`kit-test.ps1`) | — | Die Rollen selbst brauchen ihn nicht |
| **IDE** | **keine** | VS Codium (Linux), VS Code + WSL-Erweiterung (Windows) | Das Kit wird im Terminal bedient. Ein Editor ist Komfort |
| **Agenten-Werkzeug** | **eine** CLI, die headless arbeitet und ein maschinenlesbares Ergebnis liefert | Claude Code (`claude -p`) | Die einzige Aufrufstelle ist `team_claude()` in [team/lib.sh](../bash/lib.sh) |
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
bash bash/kit-einrichten.sh ~/Source/mein-projekt
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

## Der kurze Weg — Windows nativ (ohne WSL)

```powershell
# 1. Bordmittel
winget install --id Microsoft.PowerShell --source winget   # PowerShell 7
winget install --id Git.Git --source winget
winget install --id Python.Python.3.12 --source winget

# 2. Klonen — in einer NEUEN pwsh-Sitzung (PATH!)
git clone https://github.com/maxron84/team-kit.git $HOME\Source\team-kit
cd $HOME\Source\team-kit

# 3. Maschine prüfen und einrichten — und gleich in ein Projekt einbinden
pwsh -File .\pwsh\kit-einrichten.ps1 $HOME\Source\mein-projekt
```

**Wann dieser Weg der richtige ist:** Wenn WSL2 nicht zur Verfügung steht — in
einer VM ohne *nested virtualization*, auf einem verwalteten Rechner, bei
gesperrter Firmware. Steht WSL2 zur Verfügung, ist der WSL-Weg der erprobtere
(siehe [Belegstand](#belegstand)).

**Was hier anders ist als unter WSL — und warum es kein Kompromiss ist:**

| | WSL-Weg | nativer Weg |
|---|---|---|
| Sperre | `flock` — **kooperativ**, wirkt nur solange alle mitspielen | `[System.IO.FileStream]` mit `FileShare::None` — vom **Betriebssystem durchgesetzt** |
| Dateisystem-Falle | Klon unter `/mnt/c` (DrvFs) | Klon auf Netzlaufwerk oder in einem Sync-Ordner (OneDrive) |
| Was ein Skript am Start hindert | fehlendes Exec-Bit | die **Ausführungsrichtlinie** |
| Selbstprüfung | `bash bash/kit-test.sh` (11/11) | `pwsh -File .\pwsh\kit-test.ps1` (6 Schritte) |

`kit-einrichten.ps1` prüft genau diese Punkte — und zwar **proben statt
voraussetzen**: Die Sperre wird mit zwei echten Prozessen belegt, nicht
behauptet.

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
bash bash/kit-einrichten.sh            # nur prüfen und einrichten
bash bash/kit-einrichten.sh --nur-pruefen   # gar nichts anfassen
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
5. **Kurzbefehl** — verknüpft `bash/scripts/team-init.sh` und
   `bash/scripts/team-auth-setup.sh` nach `~/.claude/scripts/`, als **Symlink**, nie
   als Kopie: Eine Verknüpfung kann nicht veralten, eine Kopie schon — und sie
   meldet sich nicht, sondern behauptet eines Tages, das Kit sei nicht da.

   Liegt dort schon eine echte **Datei**, wird sie ersetzt, sofern sie
   erkennbar vom Kit stammt; die alte Fassung bleibt als
   `*.vor-verknuepfung` daneben liegen. Was nicht erkennbar vom Kit stammt,
   bleibt unangetastet und wird gemeldet — deine eigene Datei wegzuräumen
   wäre schlimmer als jede veraltete Kopie (`A.12.1`).

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
bash ~/Source/team-kit/bash/scripts/team-auth-setup.sh
```

Das ist **einer** von mehreren Wegen; die native Installation des Herstellers
und der apt-Weg stehen in der [FAQ](faq.md#claude-cli-nicht-gefunden--wie-installiere-ich-sie),
zusammen mit den PATH-Fallen danach.

`team-auth-setup.sh` ist idempotent. Es setzt `~/.config/claude-team/auth-mode`
auf `abo`, holt einen eventuell im Shell-Profil liegenden API-Key **dort heraus**
und legt ihn als geschützten Fallback nach `~/.config/claude-team/api-key`
(`chmod 600`). Auf Wunsch testet es das Abo headless.

### 6. Einbinden

Siehe [Die Einbindung](#die-einbindung--auf-allen-wegen-dieselbe).

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
bash bash/kit-einrichten.sh --nur-pruefen     # Warnung „nicht erkennbar WSL2" ist hier erwartet

L=~/probe.lock                           # Zwei-Prozess-Gegenprobe für die Sperre
bash -c 'exec 9>"$0"; flock -x 9; echo "A: Sperre gehalten"; sleep 2' "$L" &
sleep 0.5
bash -c 'exec 9>"$0"; if flock -n 9; then echo "B: bekam sie AUCH -> flock greift NICHT"; else echo "B: abgewiesen -> flock greift"; fi' "$L"
wait; rm -f "$L"
```

**Das Erfolgskriterium ist der Exit-Code, nicht die Farbe.** Unter WSL 1 endet
`kit-einrichten.sh` nicht mit „Alles grün", sondern mit

```
0 Fehler, 1 Warnungen — lauffähig, aber lies sie.
```

und **Exit `0`**. Das ist der Erfolgsfall. Erst `1` bedeutet, dass die Maschine
nicht bereit ist. Prüfbar mit `echo $?` oder
`bash bash/kit-einrichten.sh --nur-pruefen && echo BEREIT`.

„B: abgewiesen" heißt: Ledger und Kaskadenstand sind serialisiert, und
[`vollautomatik.sh`](../bash/entry/vollautomatik.sh) — sequenziell, hält das Lock über
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
`TEAM_EINRICHTEN_ERLAUBE_DRVFS=1 bash bash/kit-einrichten.sh`.

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
bash bash/kit-einrichten.sh ~/Source/mein-projekt
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
dann `bash/scripts/team-auth-setup.sh`) — **in der Distro installiert**, nicht in
Windows. Ein aus Windows geerbter `ANTHROPIC_API_KEY` (etwa über
`WSLENV`) hat denselben Effekt wie einer im Shell-Profil: Er verdrängt das Abo.

---

## Windows nativ im Detail

### 1. PowerShell 7 — nicht 5.1

Windows 11 bringt **PowerShell 5.1** mit. Das Kit setzt **7** voraus, und 7
wird **daneben** installiert, nicht darüber: Beide Fassungen existieren
parallel, `powershell` startet weiter die alte, `pwsh` die neue.

```powershell
winget install --id Microsoft.PowerShell --source winget
```

**Woran du merkst, dass versehentlich 5.1 läuft.** Startest du ein Kit-Skript
aus einem `powershell`-Fenster statt aus `pwsh`, siehst du keinen Hinweis,
sondern eine Wand aus Syntaxfehlern, die auf harmlose deutsche Prosa zeigen:

```
At kit-einrichten.ps1:113 char:39
+         "Windows 11 bringt 5.1 mit; 7 wird DANEBEN installiert, nicht ...
+                                       ~~~~
Unexpected token 'wird' in expression or statement.
```

Keiner dieser Fehler ist echt. 5.1 liest eine Datei ohne Byte-Order-Mark nicht
als UTF-8, sondern in der ANSI-Codepage; aus dem Gedankenstrich `—` wird dabei
`â€"`, und dessen letztes Zeichen hält PowerShell für ein Anführungszeichen.
Jeder Gedankenstrich schließt damit seine Zeichenkette mitten im Satz.

Das Kit versieht seine `.ps1`-Dateien deshalb mit einem BOM (**BL-113**), womit
auch 5.1 die Datei sauber liest — und dann die Versionsprüfung erreicht, die
dir sagt, dass hier `pwsh` hingehört. Siehst du die Fehler oben trotzdem, ist
der Klon älter als diese Regel: `git pull`, dann erneut.

> Merksatz: **`pwsh`, nie `powershell`.** Die `.cmd`-Aufrufer im Projekt tun
> das von sich aus — `.\ralph.cmd` startet immer `pwsh`. Der Fehler entsteht
> nur beim direkten Aufruf einer `.ps1`.

Warum 7 Pflicht ist: `ConvertFrom-Json` verhält sich dort verlässlich (es
ersetzt auf der pwsh-Bahn die eingebetteten Python-Aufrufe der Bash-Fassung),
und `Set-StrictMode -Version Latest` ist das brauchbare Gegenstück zu Bashs
`set -u`. Dazu kommt eine unauffällige, aber teure Eigenschaft: **5.1 schreibt
Umlenkungen als UTF-16**, 7 als UTF-8 ohne BOM. Die Kostenlogs des Kits liest
anschließend Python — und `json.load` bricht an einem BOM ab, während
`kosten.py` diesen Fehler abfängt und die Datei still als `0.0000` zählt.

> Das Kit legt die Kodierung seiner Kostenlogs deshalb **ausdrücklich** fest
> und verlässt sich nicht auf die Voreinstellung
> ([`team/lib.psm1`](../pwsh/lib.psm1), `Team-ClaudeSchreiben`). Der Punkt steht
> hier trotzdem, weil er erklärt, warum 5.1 nicht „auch irgendwie geht".

### 2. Die Ausführungsrichtlinie

Das Gegenstück zum fehlenden Exec-Bit unter Linux. Steht sie auf `Restricted`
oder `AllSigned`, startet **keine** `.ps1`-Datei.

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

`RemoteSigned` lässt lokale Skripte zu und verlangt für heruntergeladene eine
Signatur. Das Kit klonst du selbst — es zählt als lokal. Administratorrechte
braucht es dafür nicht (`-Scope CurrentUser`).

### 3. Die eine Regel: lokales Laufwerk

Das Gegenstück zu `/mnt/c` unter WSL. Nicht zugesichert sind:

- **gemappte Netzlaufwerke** und UNC-Pfade (`\\server\freigabe\…`),
- **Synchronisationsordner** — OneDrive, Dropbox, Google Drive, iCloud.

Der Grund ist derselbe wie bei DrvFs: Die Dateisperre ist dort nicht
zugesichert, und ein Sync-Client schreibt in Dateien, während eine Rolle sie
liest. Besonders tückisch unter Windows 11 Enterprise: Das Benutzerprofil kann
per Richtlinie **nach OneDrive umgeleitet** sein, ohne dass es im Pfad
auffällt. `kit-einrichten.ps1` erkennt beide Fälle heuristisch **und** probt
die Sperre danach mit zwei Prozessen — die Heuristik erklärt den Regelfall, die
Probe entscheidet den Einzelfall.

Richtig ist ein lokales Laufwerk, z. B. `C:\Source\…`.

### 4. Zeilenenden

Umgekehrt zum WSL-Fall: Hier ist nicht CRLF das Problem, sondern **fehlendes**
CRLF. `.cmd`-Dateien werden vom Kommandozeileninterpreter *während der
Ausführung* zeilenweise gelesen; bei reinem LF verhalten sich Labels und `goto`
unzuverlässig — sporadisch, also besonders schwer zuzuordnen.
[`.gitattributes`](../.gitattributes) erzwingt deshalb `eol=crlf` für `*.cmd`
und `*.bat`, während `.ps1` bei LF bleibt (PowerShell liest die Datei am
Stück).

### 5. Bordmittel

```powershell
git --version
python --version      # oder python3 / py — der Installer trägt ein, was er findet
pytest --version      # nur für die Selbstprüfung
```

> **Die Store-Falle:** Windows legt Platzhalter namens `python.exe` ab, die
> beim Aufruf nur den Microsoft Store öffnen. Sie tragen den Namen und
> beantworten keine Versionsfrage. Gegenprobe: `python -c "print(1)"`.
> `kit-einrichten.ps1` und `install.ps1` prüfen genau so und akzeptieren nur
> einen Interpreter, der wirklich antwortet.

**Kein `flock`.** Es gibt das unter Windows nicht, und die pwsh-Bahn
braucht es auch nicht. An seine Stelle tritt `[System.IO.FileStream]` mit
`FileShare::None` — eine vom Betriebssystem **durchgesetzte** Sperre, während
`flock` nur wirkt, solange alle Beteiligten mitspielen. Genau diese
Problemklasse hat die pwsh-Bahn ausgelöst: Unter WSL 1 gibt es für
Dateisperren keine Zusicherung.

### 6. Agenten-Werkzeug

```powershell
npm install -g @anthropic-ai/claude-code
```

Danach **eine neue Sitzung öffnen** — PATH-Änderungen erreichen laufende
Shells nicht. Native Installation und WinGet als Alternativen: siehe
[FAQ](faq.md#windows-nativ-ohne-wsl).

> **Der teuerste Fehlschluss auf diesem Weg:** Unter Windows ist `claude` kein
> Programm, sondern ein **`.cmd`-Shim**. Scheitert seine Auflösung, sieht das
> Ergebnis **aus wie ein Auth-Fehler** und ist keiner. Das Kit löst den Befehl
> deshalb über `Get-Command` auf und meldet den Fall mit eigenem Wortlaut
> ([`team/lib.psm1`](../pwsh/lib.psm1), `Team-ClaudeBefehl`).

### 7. Auth

```powershell
pwsh -File .\scripts\team-auth-setup.ps1
```

Ablage ist `%APPDATA%\claude-team\` mit denselben zwei Dateien wie unter Linux
(`auth-mode`, `api-key`). Zwei Unterschiede, die keine Pfadanpassungen sind:

- **`chmod 600` ist unter Windows wirkungslos.** Es läuft ohne Fehler durch und
  bewirkt **nichts** — der Schlüssel läge danach für jeden lesbar da, mit einem
  grünen Haken daneben. Stattdessen wird die Vererbung abgeschaltet und genau
  ein Berechtigter eingetragen. Das Skript **prüft das anschließend nach**,
  statt es zu glauben.
- **Ein verdrängender Key steht hier selten in einem Profil.** Unter Linux ist
  `.bashrc` der Normalfall; unter Windows ist es die
  **Benutzer-Umgebungsvariable** (`setx`, Systemsteuerung). Wer nur Profile
  durchsucht, meldet „sauber", während das Abo verdrängt bleibt — deshalb
  prüft `team-auth-setup.ps1` beides, die Umgebungsvariable zuerst.

### 8. Bedienung

Zwei Aufrufformen, dieselbe Sache darunter:

```powershell
.\ralph.cmd                     # Bequemlichkeit
pwsh -File .\ralph.ps1          # dasselbe, ohne Shim
```

Die `.cmd`-Dateien sind Einzeiler auf die `.ps1` — bewusst **kein Symlink**:
Der braucht unter Windows Administratorrechte oder den Entwicklermodus, und ein
Einrichtungsschritt, der an Rechten scheitert, hat sein Versprechen gebrochen.

---

## Die Einbindung — auf allen Wegen dieselbe

Ab hier gibt es keinen inhaltlichen Plattformunterschied mehr, nur eine andere
Schreibweise.

```bash
# Linux und WSL
bash ~/Source/team-kit/bash/install.sh ~/Source/mein-projekt
# oder, nach --verknuepfen, von überall:
bash ~/.claude/scripts/team-init.sh ~/Source/mein-projekt
```

```powershell
# Windows nativ
pwsh -File $HOME\Source\team-kit\pwsh\install.ps1 $HOME\Source\mein-projekt
# oder, nach -Verknuepfen, von überall:
& "$env:USERPROFILE\.claude\scripts\team-init.cmd" $HOME\Source\mein-projekt
```

**Nur eine Bahn installieren?** `--nur-bash` bzw. `--nur-pwsh` (PowerShell:
`-NurBash` / `-NurPwsh`). Das Projekt bekommt dann statt 29 Entrypoints nur
die zehn der gewählten Bahn. Es ist eine **Abwahl**, keine Empfehlung — der
Grund steht im Kasten darunter. Sie ist keine Einbahnstraße: Ein späteres
`--update` *ohne* Schalter macht das Projekt wieder vollständig, samt der
fehlenden Konfiguration.

> **Beide Installer schreiben BEIDE Konfigurationen** — `team.config.sh` *und*
> `team.config.ps1`, aus denselben neun Antworten. Das gilt auch für
> `install.sh` unter Linux, wo die PowerShell-Fassung niemand braucht: Ein
> Projekt, das auf Linux eingerichtet und später unter Windows bedient wird,
> hätte sonst dort keine Konfiguration, und jemand schriebe sie von Hand.
> Genau dort fängt Drift an. Belegt ist außerdem, dass beide Installer aus
> denselben Antworten **byte-identische Bäume** erzeugen
> (`kit-test.sh`, Schritt 11/11).

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
# Linux und WSL — auf der Maschine
bash ~/Source/team-kit/bash/kit-einrichten.sh --nur-pruefen   # → "Alles grün", Exit 0 *
cd ~/Source/team-kit && bash bash/kit-test.sh                    # → 11/11, dauert ein paar Minuten

# im Zielprojekt
./team-test.sh                                           # Infrastruktur-Tests
./team-status.sh                                         # Pipeline, Beutebuch, Kaskadenstand

# das Agenten-Werkzeug, headless und ohne Key in der Umgebung
env -u ANTHROPIC_API_KEY claude -p 'Antworte nur mit: pong'
```

```powershell
# Windows nativ — auf der Maschine
pwsh -File .\pwsh\kit-einrichten.ps1 -NurPruefen              # → Exit 0 *
pwsh -File .\pwsh\kit-test.ps1                                # → 6 Schritte, 15 Prüfungen

# im Zielprojekt
.\team-test.cmd
.\team-status.cmd

# das Agenten-Werkzeug, headless und ohne Key in der Umgebung
$env:ANTHROPIC_API_KEY = $null; claude -p 'Antworte nur mit: pong'
```

> **`kit-test.ps1` ist kein Ersatz für `kit-test.sh`, und es behauptet das auch
> nicht.** Es schließt die Lücke, dass eine Windows-Maschine ohne WSL gar keine
> Selbstprüfung hätte — und **sagt am Ende ausdrücklich, was es nicht geprüft
> hat**: die Bash-Bahn (dort liegt keine `bash`), den Gleichstand beider
> Installer (der braucht beide Shells nebeneinander) und das Regel-Inventar.
> Ein übersprungener Nachweis, den niemand sieht, liest sich sonst wie ein
> bestandener.

\* **Maßgeblich ist der Exit-Code, nicht die Schlusszeile.** Wer legitime
Warnungen hat — allen voran WSL 1 — bekommt statt „Alles grün" die Bilanz
`0 Fehler, N Warnungen — lauffähig, aber lies sie.` und trotzdem **Exit `0`**.
Auch das ist bereit. Siehe
[Wenn nur WSL 1 geht](#wenn-nur-wsl-1-geht--vm-gesperrte-firmware-verwalteter-rechner).

`kit-test.sh` ruft **keine** Agenten-CLI auf und kostet daher nichts. Der letzte
Befehl kostet einen Mini-Anteil und ist der einzige Beweis, dass Auth wirklich
steht.

---

## Ein anderes Werkzeug, eine andere IDE, ein anderes Modell

| Tausch | Was zu tun ist | Aufwand |
|---|---|---|
| **Anderes Modell** | `TEAM_MODEL_LOOP` / `TEAM_MODEL_STRONG` in [team/lib.sh](../bash/lib.sh) oder pro Lauf setzen | eine Zeile. Welche **Fähigkeiten** ein Kandidat mitbringen muss, steht im [README](../README.md#modelle--agnostisch-aber-nicht-anspruchslos) |
| **Andere IDE / keine** | nichts | Das Kit wird im Terminal bedient |
| **Andere Agenten-CLI** | `team_claude()` in [team/lib.sh](../bash/lib.sh) austauschen — die **einzige** Stelle im Kit, die eine CLI aufruft | überschaubar, aber **nicht belegt**: An dieser Funktion hängen das Ergebnis-JSON (`is_error`, `subtype`, `total_cost_usd`), der Auth-Fallback und die 429-Mechanik. Wer tauscht, muss diese vier Dinge nachbauen — siehe [anhang-a.md, A.11](anhang-a.md) |
| **Anderes Auth-Verfahren** | `bash/scripts/team-auth-setup.sh` ist ein Beispielskript für Claude Code, keine Kit-Mechanik | ersetzen |

Das Kit ist **modellagnostisch, aber nicht CLI-agnostisch**. Das ist eine
ehrliche Grenze, keine Absichtserklärung: Der einzige erprobte Weg zu einem
Modell führt heute über `claude -p`.

---

## Fehlerbilder

Eine Zeile je Symptom. Was mehr Platz braucht — etwa *„`claude` ist gar nicht
installiert, wie komme ich dazu?"* — steht in der [FAQ](faq.md).

| Symptom | Ursache | Abhilfe |
|---|---|---|
| `/usr/bin/env: bad interpreter` | CRLF-Zeilenenden (Klon aus Windows) | In der Distro neu klonen; `git config --global core.autocrlf input` |
| `./vollautomatik.sh: Permission denied` | Exec-Bit greift nicht (DrvFs unter `/mnt/c`) | Repo ins Linux-Dateisystem verlegen; notfalls `chmod +x *.sh` |
| Alles quälend langsam unter WSL | Repo liegt unter `/mnt/c` (9p) | dito |
| `flock: … not implemented` oder Lauf hängt an der Sperre | Netz- oder Windows-Laufwerk | Repo auf ein lokales Linux-Dateisystem |
| `kit-einrichten.sh`: „nicht erkennbar WSL2" | Distro läuft unter WSL1 — in VMs meist fehlende nested virtualization | Warnung, kein Abbruch: [Wenn nur WSL 1 geht](#wenn-nur-wsl-1-geht--vm-gesperrte-firmware-verwalteter-rechner) — erst Hypervisor prüfen, sonst Zwei-Prozess-Gegenprobe für `flock` |
| `python3: command not found` mitten im Lauf | Bordmittel fehlt | `sudo apt install python3` — die Team-Werkzeuge sind Python |
| CLI meldet „takes precedence" | `ANTHROPIC_API_KEY` im Profil oder in der Umgebung | `bash/scripts/team-auth-setup.sh`, dann `unset ANTHROPIC_API_KEY` — **und die IDE neu starten** (geerbte Umgebung) |
| `install.sh`: „ist kein Git-Repository" | Zielprojekt ohne Git | `git -C <ziel> init` |
| `team-test.sh` findet nichts | `pytest` fehlt | `sudo apt install python3-pytest` |
| `pytest geteilt/tests` im **Kit-Repo** ist rot | Erwartet: Die Tests setzen die installierte Ablage voraus | Stattdessen `bash bash/kit-test.sh` |
| Lauf endet mit Exit `42` oder `43` | Kein Einrichtungsproblem: Session-Limit bzw. „Stufe fertig, Quittung fehlt" | [README, Exit-Codes](../README.md#betrieb) |

**Nur auf dem nativen Windows-Weg:**

| Symptom | Ursache | Abhilfe |
|---|---|---|
| Wand aus `Unexpected token '…'` / `Missing argument in parameter list`, die auf deutsche Prosa zeigt | Kein Syntaxfehler: Windows PowerShell **5.1** liest eine `.ps1` ohne BOM in der ANSI-Codepage, `—` endet auf U+201D und schließt die Zeichenkette (BL-113) | Mit `pwsh` starten, nicht mit `powershell`. Zeigt der Klon die Fehler trotzdem, ist er älter als die BOM-Regel: `git pull` |
| `… cannot be loaded because running scripts is disabled` | Ausführungsrichtlinie `Restricted`/`AllSigned` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` — kein Administrator nötig |
| `The term 'claude' is not recognized` | `claude` ist ein `.cmd`-Shim; PATH-Änderung hat die laufende Shell nicht erreicht | **Neue** pwsh-Sitzung öffnen. **Das ist KEIN Auth-Fehler** — nicht verwechseln. Bleibt es dabei: [FAQ](faq.md#sie-ist-installiert-der-lauf-findet-sie-trotzdem-nicht) |
| `python` öffnet den Microsoft Store | Store-Platzhalter statt Interpreter | Echtes Python installieren; Gegenprobe `python -c "print(1)"` |
| `ModuleNotFoundError: No module named 'fcntl'` — bei `team-test.cmd` als Wand von Sammelfehlern, sonst bei jedem Kostenbefehl | `fcntl` ist ein POSIX-Modul; `kosten.py` importierte es ungeschützt und war unter Windows deshalb gar nicht ladbar (**BL-125**) | Im Kit behoben. Klon aktualisieren, dann `install.ps1 <ziel> --update` — die Datei liegt im Projekt unter `team/tools/` |
| `Could not find file '…'` bei einem relativen Pfad | Ein Skript hat `Set-Location` gesetzt, aber `[System.IO.File]` folgt dem **Prozess**-Arbeitsverzeichnis, nicht der PowerShell-Position | Im Kit behoben (`Team-Pfad` in [`team/lib.psm1`](../pwsh/lib.psm1)); tritt eigener Code darauf, dieselbe Auflösung nutzen |
| `.cmd` verhält sich sporadisch falsch (Labels, `goto`) | Batch-Datei mit reinem LF | `.gitattributes` erzwingt CRLF; ein Klon von vor dieser Regel: `git rm --cached -r .` und `git reset --hard` |
| Sperre greift nicht / Lauf hängt | Klon auf Netzlaufwerk oder in einem Sync-Ordner (OneDrive) | Auf ein lokales Laufwerk verlegen. Unter Windows 11 Enterprise kann das Benutzerprofil per Richtlinie nach OneDrive umgeleitet sein |
| Kosten stehen auf `0.0000`, obwohl ein Lauf lief | Kostenlog mit BOM oder UTF-16 — `kosten.py` fängt den Lesefehler ab und zählt still null | Mit `pwsh` **7** fahren, nicht mit `powershell` (5.1) |
| Statusbericht bricht mit „Error formatting a string" ab | In `[Console]::Out.WriteLine('{0} {1}' -f $a, $b)` ist das Komma der Argumenttrenner der **Methode** | Format-Ausdruck in eigene Klammern setzen. Im Kit behoben |

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
- **Windows nativ (PowerShell): gebaut und gefahren, aber NICHT auf Windows.**
  Die ganze pwsh-Bahn — `kit-einrichten.ps1`, `install.ps1`, `pwsh/lib.psm1`, die
  zehn Rollen-Einstiege, `kit-test.ps1` — ist gegen **pwsh 7.4.6 unter Linux**
  geprüft: Syntax, Einrichtung, Installation, ein `-Update` gegen eine mit
  `install.sh` erzeugte Installation, ein Trockenlauf der ganzen Kette, und die
  Zusicherung, dass beide Installer **byte-identische Bäume** erzeugen.
  Was das **nicht** belegt und dort auch nicht belegbar ist: `Get-CimInstance`,
  `Set-Acl`, die Benutzer-Umgebungsvariablen, das `.cmd`-Verhalten — und vor
  allem die tragende Frage, **ob `claude -p --output-format json` unter nativem
  Windows headless mit dem Abo läuft**. Dafür liegt
  [`pruefe-windows.ps1`](../pwsh/pruefe-windows.ps1) bereit; sie beantwortet genau
  diese drei Punkte und kostet im Standardlauf nichts. Solange sie nicht
  gefahren ist, gilt der native Weg als **gebaut, nicht abgenommen**.
- **Erster Kontakt mit einer echten Windows-Maschine (18.08.2026): rot.**
  `kit-einrichten.ps1` brach auf einer Windows-11-Enterprise-VM mit zehn
  Syntaxfehlern ab, ohne eine Zeile auszuführen — Ursache war die fehlende
  Kodierungsangabe, nicht der Code (**BL-113**, oben in den Fehlerbildern).
  Der Befund ist behoben und steht unter Test
  ([`team/tests/test_bl113_bom_regel.py`](../geteilt/tests/test_bl113_bom_regel.py),
  `kit-test.sh` Schritt 11). Er ist zugleich das Maß für den Rest dieses
  Abschnitts: Eine gegen pwsh 7 unter Linux vollständig grüne Bahn hat auf
  dem Ziel **an der ersten Datei** gescheitert. Was hier als „gefahren" steht,
  heißt weiterhin *unter Linux gefahren*.
- **Zweiter Kontakt — die Regressionssuite auf derselben Maschine
  (20.08.2026): rot, und zwar über sich selbst.** 160 der 487 Tests fielen.
  **Keiner davon kam aus dem Kit**: Der Testharnisch
  (`geteilt/tests/conftest.py`) setzte einen POSIX-Wirt voraus — `bash` im
  PATH ist unter Windows der WSL-Launcher aus `System32`, eine `.sh` ist dort
  keine ausführbare Datei, der PATH trennt mit `;`, und ein Kindprozess ohne
  `SystemRoot`/`PATHEXT` findet nicht einmal `git`. Behoben als **BL-130**;
  der eine echte Befund, der unter den 160 lag, ist **BL-129** (das Ledger
  bekam unter Windows in jeder Zeile ein CR-Byte).

  Der Vorgang wiederholt das Maß von BL-113 eine Ebene höher: Nicht nur der
  Code, auch **die Prüfvorrichtung** war gegen Linux gebaut. Solange die
  Suite auf dem Ziel nicht durchgelaufen ist, sagt eine grüne Zahl unter Linux
  nichts über Windows.

  **Was hier ebenfalls noch aussteht:** Die Fixes zu BL-129 und BL-130 sind
  gegen Linux verifiziert — mit echter Bash (455 Tests grün) **und** gegen
  einen simulierten Wirt ganz ohne Bash (0 Fehlschläge, die Bash-Bahn
  übersprungen mit Begründung). Auf einer **Windows-Maschine gefahren sind sie
  nicht.** Sie sind damit *hergeleitet*, nicht *abgenommen* — genau die
  Unterscheidung, an der BL-113 hing.

- **Dritter Kontakt — zweiter Lauf der Suite (21.08.2026): 160 → rund 50.**
  Die Bash-Bahn lief diesmal wirklich (`auf beiden Bahnen gelaufen: 38`) —
  Git for Windows wurde gefunden, der WSL-Stub blieb außen vor. Übrig blieben
  zwei Ursachen, beide diesmal **im Kit**, nicht im Harnisch:

  **BL-131** — die Bash-Bahn verdrahtete `python3` an drei Stellen fest, unter
  Windows der Store-Alias. **BL-132** — 77 `subprocess`-Aufrufe der Suite
  dekodierten in cp1252; der Fehler fiel im Reader-Thread an, und der Test sah
  nur `stdout is None`.

  **Die Lehre steht in BL-131 und ist die teuerste dieser Reihe:** Die
  pwsh-Bahn hatte den Python-Fund seit `BL-122` gelöst, die Bash-Bahn nie
  nachgezogen — weil sie als *„die Linux-Bahn"* galt. Genau das ist die Drift,
  gegen die die Doppelbahn gebaut ist. Sie war nur an einer Stelle, die kein
  Test berührte. Ein Windows-Projekt bekam dadurch eine korrekte
  `team.config.ps1` und eine kaputte `team.config.sh` daneben.

  Auch dieser Stand ist **hergeleitet, nicht abgenommen**: Verifiziert ist er
  gegen Linux (Kit-Selbsttest 11/11, 459 Tests in der Installation) und gegen
  einen simulierten Wirt ohne Bash. Der nächste Windows-Lauf ist der Beleg.

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

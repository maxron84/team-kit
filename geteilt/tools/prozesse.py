#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteiltes Werkzeug, von beiden Bahnen aus aufrufbar)
"""prozesse.py — Waisen-Kandidaten unter den Prozessen dieses Projekts, mit
Begruendung statt Vermutung (Kit-BL-278).

DIE LAGE
    Die Diagnose "verwaiste pwsh-Prozesse" ist im Feld viermal unwiderlegt
    wiederholt worden; fuenf Ralph-Stufen und drei Frank-Laeufe haben sie in
    die Gate-Datei uebernommen. Gewonnen war sie aus Name und Alter
    (`Get-Process`, `tasklist`), und sie zaehlte Terminals der
    Entwicklungsumgebung als Waisen. Nachgemessen mit Elternaufloesung: null
    Waisen. Die Erklaerung war selbstbestaetigend geworden — und ein ECHTER
    Waise waere darin unsichtbar gewesen.

DER WEG
    Erhebung und Urteil getrennt. `erheben` schreibt die Prozesstabelle als
    JSON; `pruefen` urteilt ueber die eigene Erhebung oder eine Datei
    (`--json`). Ein Kandidat erfuellt ALLE DREI Merkmale:
      (1) sein Elternprozess lebt nicht mehr — unter Windows auch dann, wenn
          die Eltern-PID inzwischen einem JUENGEREN Prozess gehoert;
      (2) er ist eine Huelle: Shell oder Terminal (Merkmalsliste aus
          `TEAM_PROZESS_HUELLEN`, `team.config.*` oder `--huellen`);
      (3) Pfad oder Befehlszeile liegen unter der Wurzel dieses Repos.
    Der Bericht nennt die gepruefte Menge und die Merkmale, nicht nur das
    Ergebnis.

ZWEI FALLEN, ausdruecklich uebernommen
    - Ein toter Elternprozess ist KEIN hinreichender Beweis: Eine
      GUI-Anwendung, aus einer inzwischen geschlossenen Shell gestartet,
      sieht genauso aus. Deshalb drei Merkmale — und das Ergebnis heisst
      "Kandidat", nicht "Waise".
    - Abgeraeumt wird NICHT. Das Werkzeug nennt je Kandidat den Befehl, mit
      dem ein Mensch ihn beendet. Im Feld hatte der Abraeumer zwei kritische
      Funde; ein Werkzeug ohne Abraeumer kann auch sein Test nicht scharf
      gegen die Maschine feuern.

NUTZUNG
    prozesse.py erheben                      Prozesstabelle als JSON
    prozesse.py pruefen [--json DATEI] [--wurzel PFAD] [--huellen "a b"]
                                             Exit 3 = es gibt Kandidaten
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts. Unter
# einem deutschen Windows schriebe Python sonst cp1252, und jeder Aufrufer im
# Kit liest UTF-8.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

HUELLEN = ("pwsh", "powershell", "cmd", "conhost", "bash", "sh", "dash",
           "zsh", "fish")


def _iso(roh):
    if not roh:
        return None
    try:
        return datetime.fromisoformat(str(roh).replace("Z", "+00:00"))
    except ValueError:
        return None


def erheben():
    """Die Prozesstabelle: pid, ppid, name, pfad, befehl, start (ISO)."""
    if os.name == "nt":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            raise RuntimeError("weder pwsh noch powershell gefunden")
        skript = ("Get-CimInstance Win32_Process | Select-Object "
                  "ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine,"
                  "@{n='Start';e={if ($_.CreationDate) "
                  "{ $_.CreationDate.ToString('o') }}} | ConvertTo-Json -Compress")
        r = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-Command",
                            skript], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        daten = json.loads(r.stdout or "[]")
        if isinstance(daten, dict):
            daten = [daten]
        return [{"pid": d.get("ProcessId"), "ppid": d.get("ParentProcessId"),
                 "name": d.get("Name") or "", "pfad": d.get("ExecutablePath") or "",
                 "befehl": d.get("CommandLine") or "", "start": d.get("Start")}
                for d in daten]
    r = subprocess.run(["ps", "-eo", "pid=,ppid=,comm=,args="],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=60)
    tabelle = []
    for zeile in r.stdout.splitlines():
        teile = zeile.split(None, 3)
        if len(teile) < 3 or not teile[0].isdigit():
            continue
        tabelle.append({"pid": int(teile[0]), "ppid": int(teile[1]),
                        "name": teile[2], "pfad": "",
                        "befehl": teile[3] if len(teile) > 3 else "",
                        "start": None})
    return tabelle


def _name(eintrag):
    name = os.path.basename(str(eintrag.get("name") or "")).lower()
    return name[:-4] if name.endswith(".exe") else name


def _unter(wurzel, *texte):
    w = os.path.abspath(wurzel).replace("\\", "/").rstrip("/").lower()
    return any(w and w in str(t or "").replace("\\", "/").lower() for t in texte)


def eltern_tot(eintrag, nach_pid):
    """Lebt der Elternprozess nicht mehr? Unter POSIX erbt init (PID 1) die
    Waisen; unter Windows bleibt die alte Eltern-PID stehen und kann einem
    JUENGEREN Prozess gehoeren — dann ist es nicht der Elternprozess."""
    ppid = eintrag.get("ppid")
    if ppid in (None, 0):
        return False
    if ppid == 1:          # POSIX: init hat ihn geerbt (unter Windows gibt es 1 nicht)
        return True
    eltern = nach_pid.get(ppid)
    if eltern is None:
        return True
    kind, alt = _iso(eintrag.get("start")), _iso(eltern.get("start"))
    return bool(kind and alt and alt > kind)


def urteilen(tabelle, wurzel, huellen=HUELLEN):
    """[(eintrag, grund)] — Kandidaten, die alle drei Merkmale erfuellen."""
    nach_pid = {e.get("pid"): e for e in tabelle}
    huellen = {h.lower() for h in huellen}
    treffer = []
    for e in tabelle:
        if _name(e) not in huellen:
            continue
        if not _unter(wurzel, e.get("pfad"), e.get("befehl")):
            continue
        if not eltern_tot(e, nach_pid):
            continue
        treffer.append((e, f"Elternprozess {e.get('ppid')} lebt nicht mehr"))
    return treffer


def huellen_aus_konfiguration(wurzel):
    """`TEAM_PROZESS_HUELLEN` aus der Umgebung oder aus `team.config.*`."""
    roh = os.environ.get("TEAM_PROZESS_HUELLEN", "")
    if not roh:
        muster = (re.compile(r'^\s*(?:export\s+)?TEAM_PROZESS_HUELLEN="'
                             r'(?:\$\{TEAM_PROZESS_HUELLEN:-)?([^"}]*)\}?"'),
                  re.compile(r"^\s*\$TEAM_PROZESS_HUELLEN\s*=\s*(?:Team-Wert\s+"
                             r"'TEAM_PROZESS_HUELLEN'\s+)?['\"]([^'\"]*)['\"]"))
        for name in ("team.config.sh", "team.config.ps1"):
            try:
                with open(os.path.join(wurzel, name), encoding="utf-8-sig") as fh:
                    for zeile in fh:
                        for m in muster:
                            t = m.match(zeile)
                            if t and t.group(1).strip():
                                roh = t.group(1)
                                break
            except OSError:
                continue
            if roh:
                break
    teile = roh.replace(",", " ").split()
    return tuple(teile) if teile else HUELLEN


def pruefen(tabelle, wurzel, huellen):
    treffer = urteilen(tabelle, wurzel, huellen)
    print(f"Geprueft: {len(tabelle)} Prozesse. Merkmale, ALLE drei: "
          f"Elternprozess tot · Huelle ({', '.join(huellen)}) · unter "
          f"{os.path.abspath(wurzel)} (Kit-BL-278).")
    if not treffer:
        print("Keine Waisen-Kandidaten.")
        return 0
    print(f"Kandidaten: {len(treffer)} — Kandidaten, keine Beweise: Eine "
          f"GUI-Anwendung aus einer geschlossenen Shell sieht genauso aus.")
    for e, grund in treffer:
        seit = f", seit {e['start'][:16]}" if e.get("start") else ""
        print(f"  PID {e.get('pid')}  {e.get('name')}{seit} — {grund}")
        befehl = (f"Stop-Process -Id {e.get('pid')}" if os.name == "nt"
                  else f"kill {e.get('pid')}")
        print(f"    beenden, nach eigener Pruefung: {befehl}")
    return 3


def main(argv):
    if not argv or argv[0] not in ("erheben", "pruefen"):
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "erheben":
        json.dump(erheben(), sys.stdout, ensure_ascii=False)
        print()
        return 0
    quelle, wurzel, huellen = None, ".", None
    rest = argv[1:]
    i = 0
    while i < len(rest):
        if rest[i] in ("--json", "--wurzel", "--huellen") and i + 1 < len(rest):
            if rest[i] == "--json":
                quelle = rest[i + 1]
            elif rest[i] == "--wurzel":
                wurzel = rest[i + 1]
            else:
                huellen = tuple(rest[i + 1].replace(",", " ").split())
            i += 2
        else:
            print(f"Fehler: unbekanntes Argument '{rest[i]}'", file=sys.stderr)
            return 2
    if quelle:
        with open(quelle, encoding="utf-8-sig") as fh:
            tabelle = json.load(fh)
    else:
        try:
            tabelle = erheben()
        except (OSError, RuntimeError, ValueError,
                subprocess.SubprocessError) as exc:
            print(f"Fehler: Erhebung gescheitert ({exc}).", file=sys.stderr)
            return 1
    return pruefen(tabelle, wurzel, huellen or huellen_aus_konfiguration(wurzel))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

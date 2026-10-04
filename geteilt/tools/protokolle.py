#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteiltes Werkzeug, von beiden Bahnen aus aufrufbar)
"""protokolle.py — die Sitzungsprotokolle dieses Projekts ins Projekt holen
(Kit-BL-242).

DIE LAGE
    Fuer jeden Rollenaufruf legt das Kit eine Datei in `.team-logs/` ab; die
    Sitzung, in der geplant, diagnostiziert und ENTSCHIEDEN wird, hatte kein
    Gegenstueck. Die Agenten-CLI schreibt je Sitzung ein Vollprotokoll nach
    `~/.claude/projects/<projekt>/<kennung>.jsonl` — im meldenden Feldprojekt
    209 Sitzungen und 133 MB, kein Byte davon im Projekt greifbar. Eine
    Ursachenkette ueber drei Handabnahmen lag nur dort, und im Repo stand sie
    nur, weil der Architekt sie von Hand abgeschrieben hatte.

DER WEG
    `ablegen` kopiert die Protokolle DIESES Projekts — samt denen ihrer
    Subagenten — nach `.team-protokolle/`, rueckwirkend und idempotent, und
    schreibt ein `index.md`: Zeitraum, Art, Nutzer-Zuege, Antworten und
    Kosten je Sitzung. Der Uebergabezettel traegt die DEUTUNG, das Protokoll
    den BELEG.

DIE DREI AUFLAGEN DER MELDUNG
    (1) Unkommittiert. In einem Protokoll steht alles, was je in eine Sitzung
        eingefuegt wurde — Token, Kennwoerter, Kundennamen. Die Zeile steht
        in der `.gitignore`-Vorlage; ein `--update` MELDET sie, wo sie fehlt,
        eingetragen wird sie von Hand (das Update aendert die `.gitignore`
        nie selbst, BL-109). Liegt der Ordner NICHT unter `.gitignore`,
        bricht `ablegen` ab, statt zu schreiben.
    (2) Nie automatisch in einen Kontext. Kein Briefing und kein Werkzeug liest
        den Ordner von sich aus — nur auf ausdrueckliche Nachfrage. Sonst
        zahlt jedes Projekt seine Historie in jedem Rollenaufruf mit.
    (3) Rueckwirkend. Der erste Lauf nimmt alle vorhandenen Verlaeufe mit.

NUTZUNG
    protokolle.py ablegen [--projekt PFAD] [--ziel ORDNER]
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kosten  # noqa: E402

ORDNER = ".team-protokolle"
ZWISCHENSPEICHER = ".index.json"


def ignoriert(projekt, ziel):
    """True: liegt unter .gitignore. False: liegt NICHT darunter. None: kein
    Git-Arbeitsbaum (dann kann auch nichts versehentlich committet werden)."""
    try:
        r = subprocess.run(["git", "-C", projekt, "rev-parse",
                            "--is-inside-work-tree"], capture_output=True,
                           text=True)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    probe = os.path.relpath(os.path.join(ziel, "probe.jsonl"), projekt)
    r = subprocess.run(["git", "-C", projekt, "check-ignore", "-q", probe],
                       capture_output=True, text=True)
    return r.returncode == 0


def _kopieren(quelle, ziel):
    """"neu", "aktualisiert" oder "gleich" — verglichen an Groesse und
    Aenderungszeit, kopiert samt Aenderungszeit."""
    if os.path.isfile(ziel):
        q, z = os.stat(quelle), os.stat(ziel)
        if q.st_size == z.st_size and int(q.st_mtime) <= int(z.st_mtime):
            return "gleich"
        art = "aktualisiert"
    else:
        art = "neu"
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    shutil.copy2(quelle, ziel)
    return art


def _zeile(pfad, dateien):
    """Die Indexzeile einer Sitzung — gemessen mit denselben Funktionen wie
    der Kostenabschluss, damit beide dieselbe Zahl nennen."""
    info = {}
    je, antworten, _ = kosten.sitzung_messen(dateien, info=info)
    usd, _z, unbekannt = kosten.sitzung_kosten(je)
    geaendert = datetime.fromtimestamp(os.path.getmtime(pfad))
    erste = info.get("erste").astimezone() if info.get("erste") else geaendert
    letzte = info.get("letzte").astimezone() if info.get("letzte") else geaendert
    return {"beginn": erste.strftime("%Y-%m-%d %H:%M"),
            "ende": letzte.strftime("%Y-%m-%d %H:%M"),
            "art": "Rollen-Lauf" if kosten.ist_rollenlauf(pfad) is True
                   else "Sitzung",
            "zuege": kosten.echte_nutzer_prompts([pfad]),
            "antworten": antworten, "usd": round(usd, 4),
            "ohne_preis": unbekannt, "subagenten": len(dateien) - 1}


def ablegen(projekt=".", ziel=None):
    ziel = ziel or os.path.join(projekt, ORDNER)
    if ignoriert(projekt, ziel) is False:
        print(f"Fehler: {ziel} liegt NICHT unter .gitignore — es wird nichts "
              f"abgelegt (Kit-BL-242). In einem Protokoll steht alles, was je "
              f"in eine Sitzung eingefuegt wurde. Die Zeile `{ORDNER}/` in "
              f"die .gitignore des Projekts eintragen (ein --update meldet "
              f"sie, traegt sie aber nicht selbst ein), dann erneut ablegen.",
              file=sys.stderr)
        return 1
    transkripte = sorted(kosten.transkripte_aus_projekt(projekt),
                         key=os.path.getmtime)
    if not transkripte:
        print(f"Keine Sitzungsprotokolle zu {os.path.abspath(projekt)} "
              f"gefunden.")
        return 0
    zaehler = {"neu": 0, "aktualisiert": 0, "gleich": 0}
    try:
        with open(os.path.join(ziel, ZWISCHENSPEICHER), encoding="utf-8") as fh:
            alt = json.load(fh)
    except (OSError, ValueError):
        alt = {}
    zeilen = {}
    for pfad in transkripte:
        kennung = kosten.transkript_kennung(pfad)
        dateien = kosten.sitzungs_dateien(pfad)
        geaendert = False
        for quelle in dateien:
            rel = os.path.relpath(quelle, os.path.dirname(pfad))
            art = _kopieren(quelle, os.path.join(ziel, rel))
            zaehler[art] += 1
            geaendert = geaendert or art != "gleich"
        stempel = [os.path.getsize(d) for d in dateien]
        if not geaendert and alt.get(kennung, {}).get("stempel") == stempel:
            zeilen[kennung] = alt[kennung]
        else:
            zeilen[kennung] = dict(_zeile(pfad, dateien), stempel=stempel)
    _index_schreiben(ziel, zeilen)
    print(f"{zaehler['neu']} neu, {zaehler['aktualisiert']} aktualisiert, "
          f"{zaehler['gleich']} unveraendert — {ziel}/index.md "
          f"({len(zeilen)} Protokolle, nicht versioniert, Kit-BL-242).")
    return 0


def _index_schreiben(ziel, zeilen):
    os.makedirs(ziel, exist_ok=True)
    with open(os.path.join(ziel, ZWISCHENSPEICHER), "w", encoding="utf-8") as fh:
        json.dump(zeilen, fh, ensure_ascii=False, indent=1)
    kopf = [
        "# Sitzungsprotokolle\n",
        "\n",
        "> Abgelegt von `team/tools/protokolle.py ablegen` (Kit-BL-242).\n",
        "> **Nicht versioniert**, und keine Rolle liest diesen Ordner von sich\n",
        "> aus — nur auf ausdrueckliche Nachfrage. Kosten im Abo sind ein\n",
        "> Abo-Gegenwert, kein abgerechneter Betrag.\n",
        "\n",
        "| Beginn | Ende | Art | Nutzer-Zuege | Antworten | USD | Protokoll |\n",
        "|---|---|---|---|---|---|---|\n",
    ]
    reihen = []
    for kennung, z in sorted(zeilen.items(), key=lambda kv: kv[1]["beginn"]):
        neben = (f" (+{z['subagenten']} Subagent"
                 f"{'en' if z['subagenten'] != 1 else ''})"
                 if z.get("subagenten") else "")
        usd = f"{z['usd']:.4f}" + (" (ohne Preis: " + ", ".join(z["ohne_preis"])
                                   + ")" if z.get("ohne_preis") else "")
        reihen.append(f"| {z['beginn']} | {z['ende']} | {z['art']} | "
                      f"{z['zuege']} | {z['antworten']} | {usd} | "
                      f"[{kennung[:8]}]({kennung}.jsonl){neben} |\n")
    with open(os.path.join(ziel, "index.md"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.writelines(kopf + reihen)


def main(argv):
    if not argv or argv[0] != "ablegen":
        print(__doc__, file=sys.stderr)
        return 2
    projekt, ziel = ".", None
    rest = argv[1:]
    i = 0
    while i < len(rest):
        if rest[i] in ("--projekt", "--ziel") and i + 1 < len(rest):
            if rest[i] == "--projekt":
                projekt = rest[i + 1]
            else:
                ziel = rest[i + 1]
            i += 2
        else:
            print(f"Fehler: unbekanntes Argument '{rest[i]}'", file=sys.stderr)
            return 2
    return ablegen(projekt, ziel)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteiltes Werkzeug, von beiden Bahnen aus aufrufbar)
"""schreibzone.py — was im Plan-Ordner liegt, ohne Team-Artefakt oder
verzeichneter Bestand zu sein (Kit-BL-237).

DIE LAGE
    Der Bestandsvermerk der Schreibzone (`TEAM_PLAN_ORDNER_BESTAND`, `BL-51`)
    wird beim Einzug erfasst und altert danach still. Im Feld lagen nach elf
    Kaskaden NEUN fremde Dateien im Plan-Ordner — darunter vier ausfuehrbare
    Pruefskripte (79 KB) und ein ausdruecklich verbindlicher
    Gestaltungsvertrag —, alle aenderbar und loeschbar durch die
    Read-Only-Rollen, weil der Vermerk beim Einzug zu Recht leer war und leer
    blieb. Dieselben vier Skripte standen auch nicht in `TEAM_WEITERER_CODE`
    und wurden nie gesweept: hineingewachsen, nicht beim Einzug entstanden.
    Gefunden hat es eine beilaeufige Frage des Stakeholders — kein Werkzeug.

DER WEG
    Ein Hinweis im Statusbericht, ausdruecklich ohne Guard-Mechanik (die
    Begruendung aus `BL-51` traegt weiter: Auf seiner eigenen Whitelist kann
    der Guard nicht urteilen) und ohne Meinung ueber die Zugehoerigkeit:
    Genannt wird, was weder Team-Artefakt noch im Bestandsvermerk ist, und
    eine ausfuehrbare Datei darunter bekommt den Zusatz, dass sie ausserhalb
    des Pruefumfangs liegt.

NUTZUNG
    schreibzone.py pruefen [--wurzel .] [--plan-ordner P] [--bestand "a b"]
                           [--weiterer "x y"]
    Ohne Schalter gelten TEAM_PLAN_ORDNER, TEAM_PLAN_ORDNER_BESTAND und
    TEAM_WEITERER_CODE aus der Umgebung. Exit 3 = es gibt Hinweise.
"""
import fnmatch
import os
import sys

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts. Unter
# einem deutschen Windows schriebe Python sonst cp1252, und jeder Aufrufer im
# Kit liest UTF-8.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

# Was das Team selbst im Plan-Ordner anlegt — die Artefakte aus CLAUDE.md und
# den Briefings. Muster relativ zum Plan-Ordner.
TEAM_ARTEFAKTE = (
    "beutebuch.md", "backlog.md", "backlog-archiv.md", "roadmap-skizzen.md",
    "*kaskade-*.md", "ermittlungsakten/*", "kit-meldungen/*", ".gitkeep",
)
AUSFUEHRBAR = (".py", ".sh", ".ps1", ".psm1", ".cmd", ".bat", ".js", ".mjs",
               ".cjs", ".ts", ".rb", ".pl")


def _team_artefakt(rel):
    return any(fnmatch.fnmatch(rel, m) for m in TEAM_ARTEFAKTE)


def _im_bestand(rel, bestand):
    for eintrag in bestand:
        e = eintrag.strip().strip("/")
        if e and (rel == e or rel.startswith(e + "/")
                  or fnmatch.fnmatch(rel, e)):
            return True
    return False


def _ausfuehrbar(pfad):
    if pfad.lower().endswith(AUSFUEHRBAR):
        return True
    if os.name != "nt" and os.access(pfad, os.X_OK):
        return True
    return False


def befunde(wurzel, plan_ordner, bestand, weiterer):
    """[(rel_zum_repo, ausfuehrbar, im_pruefumfang)] der fremden Dateien."""
    plan = os.path.join(wurzel, plan_ordner.strip("/"))
    if not os.path.isdir(plan):
        return []
    weiterer = [w.strip().strip("/") for w in weiterer if w.strip()]
    treffer = []
    for ordner, unter, dateien in os.walk(plan):
        unter[:] = sorted(u for u in unter if not u.startswith("."))
        for name in sorted(dateien):
            pfad = os.path.join(ordner, name)
            rel = os.path.relpath(pfad, plan).replace("\\", "/")
            if _team_artefakt(rel) or _im_bestand(rel, bestand):
                continue
            rel_repo = os.path.relpath(pfad, wurzel).replace("\\", "/")
            geprueft = any(rel_repo == w or rel_repo.startswith(w + "/")
                           for w in weiterer)
            treffer.append((rel_repo, _ausfuehrbar(pfad), geprueft))
    return treffer


def main(argv):
    if not argv or argv[0] != "pruefen":
        print(__doc__, file=sys.stderr)
        return 2
    werte = {"--wurzel": ".",
             "--plan-ordner": os.environ.get("TEAM_PLAN_ORDNER", "plans"),
             "--bestand": os.environ.get("TEAM_PLAN_ORDNER_BESTAND", ""),
             "--weiterer": os.environ.get("TEAM_WEITERER_CODE", "")}
    rest = argv[1:]
    i = 0
    while i < len(rest):
        if rest[i] in werte and i + 1 < len(rest):
            werte[rest[i]] = rest[i + 1]
            i += 2
        else:
            print(f"Fehler: unbekanntes Argument '{rest[i]}'", file=sys.stderr)
            return 2
    treffer = befunde(werte["--wurzel"], werte["--plan-ordner"],
                      werte["--bestand"].split(), werte["--weiterer"].split())
    if not treffer:
        return 0
    plan = werte["--plan-ordner"].strip("/")
    print(f"  Im Plan-Ordner, weder Team-Artefakt noch Bestand (Kit-BL-237):")
    for rel, ausfuehrbar, geprueft in treffer:
        zusatz = ""
        if ausfuehrbar and not geprueft:
            zusatz = "  — ausfuehrbar und NICHT im Pruefumfang des Red Teams"
        print(f"    · {rel}{zusatz}")
    print(f"    Read-Only-Rollen duerfen hier schreiben und loeschen. Gehoert es "
          f"dem Projekt: in TEAM_PLAN_ORDNER_BESTAND eintragen (dann bleibt es "
          f"fuer sie tabu); ist es Code: auch in TEAM_WEITERER_CODE (dann wird "
          f"es gesweept). Oder es zieht aus {plan}/ aus.")
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

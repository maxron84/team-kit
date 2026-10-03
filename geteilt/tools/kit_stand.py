#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteiltes Werkzeug, von beiden Installern aufgerufen)
"""kit_stand.py — die Pruefsummenliste der Kit-Dateien eines Projekts
(Kit-BL-270).

DIE LAGE
    Ein `--update` ersetzt jede Kit-Datei im Projekt durch die Fassung des
    Kits. Im Feld hat es so drei bewusst gesetzte Stellen ueberschrieben —
    einen ueber Fund, Fix und Reproducer eingebauten Waechter in der
    Bibliothek, den ausgefuellten Commit-Entscheid im Architekten-Briefing und
    eine Projektausnahme im Briefing der bauenden Rolle —, und wenige Stunden
    spaeter dieselben drei ein zweites Mal. Gemeldet wurde nichts. Fuer die
    Briefings KONNTE die alte Pruefung nichts melden: Sie verglich mit der
    Kit-Fassung, und eine gerenderte Datei weicht davon IMMER ab.

DER WEG
    Das Update merkt sich, was es selbst geschrieben hat: je Datei eine
    Pruefsumme in `team/.kit-stand`, NACH dem Rendern. Weicht eine Datei beim
    naechsten Update davon ab, hat sie seither jemand geaendert — dann wird
    sie gesichert und namentlich gemeldet, bevor sie ersetzt wird. Eine
    Kit-Aenderung allein meldet nichts mehr; das war das Rauschen, gegen das
    die alte Pruefung die Briefings ausnehmen musste (BL-175).

    Verglichen wird ohne BOM und mit LF: Ein Checkout mit `core.autocrlf` ist
    keine Aenderung im Projekt.

NUTZUNG (aus den Installern, nicht von Hand)
    kit_stand.py pruefen  --ziel Z --kit K     Pfade, die von der Liste
                                                abweichen, je Zeile. Exit 3,
                                                wenn es noch keine Liste gibt.
    kit_stand.py sichern  --ziel Z --stempel S PFAD...
    kit_stand.py sichern  --ziel Z --kit K --stempel S --alle
                                                nach backups/update-S/
    kit_stand.py schreiben --ziel Z --kit K     die Liste neu, ueber alles,
                                                was das Kit im Projekt hat
"""
import glob
import hashlib
import os
import shutil
import sys

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts. Unter
# einem deutschen Windows schriebe Python sonst cp1252, und jeder Aufrufer im
# Kit liest UTF-8.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

LISTE = os.path.join("team", ".kit-stand")


def kit_dateien(kit, ziel):
    """Die Pfade (relativ, mit `/`), die das Kit in ein Projekt legt und die
    dort liegen. Dieselbe Paarung wie in den Installern — die Konfigurationen
    sind Projektdaten und fehlen deshalb."""
    paare = []
    for ordner, muster in (("bash/entry", "*.sh"), ("pwsh/entry", "*.ps1"),
                           ("pwsh/entry", "*.cmd")):
        for f in glob.glob(os.path.join(kit, ordner, muster)):
            name = os.path.basename(f)
            if name not in ("team.config.sh", "team.config.ps1"):
                paare.append(name)
    for f in ("bash/lib.sh", "bash/redteam.sh", "pwsh/lib.psm1",
              "pwsh/redteam.ps1"):
        if os.path.isfile(os.path.join(kit, f)):
            paare.append("team/" + os.path.basename(f))
    for ordner, muster, ziel_ordner in (
            ("geteilt/tools", "*.py", "team/tools"),
            ("geteilt/prompts", "*.md", "team/prompts"),
            ("geteilt/tests", "test_*.py", "team/tests")):
        for f in glob.glob(os.path.join(kit, ordner, muster)):
            paare.append(f"{ziel_ordner}/{os.path.basename(f)}")
    paare += ["team/tests/conftest.py", "TEAM.md"]
    return sorted(p for p in set(paare)
                  if os.path.isfile(os.path.join(ziel, p)))


def pruefsumme(pfad):
    with open(pfad, "rb") as fh:
        roh = fh.read()
    if roh.startswith(b"\xef\xbb\xbf"):
        roh = roh[3:]
    return hashlib.sha256(roh.replace(b"\r\n", b"\n")).hexdigest()


def liste_lesen(ziel):
    pfad = os.path.join(ziel, LISTE)
    if not os.path.isfile(pfad):
        return None
    stand = {}
    with open(pfad, encoding="utf-8") as fh:
        for zeile in fh:
            teile = zeile.rstrip("\r\n").split("  ", 1)
            if len(teile) == 2 and len(teile[0]) == 64:
                stand[teile[1]] = teile[0]
    return stand


def pruefen(ziel, kit):
    stand = liste_lesen(ziel)
    if stand is None:
        return 3
    for rel in kit_dateien(kit, ziel):
        if rel in stand and pruefsumme(os.path.join(ziel, rel)) != stand[rel]:
            print(rel)
    return 0


def sichern(ziel, stempel, pfade):
    wurzel = os.path.join(ziel, "backups", f"update-{stempel}")
    for rel in pfade:
        quelle = os.path.join(ziel, rel)
        if not os.path.isfile(quelle):
            continue
        ziel_pfad = os.path.join(wurzel, rel)
        os.makedirs(os.path.dirname(ziel_pfad), exist_ok=True)
        shutil.copy2(quelle, ziel_pfad)
    print(os.path.join("backups", f"update-{stempel}"))
    return 0


def schreiben(ziel, kit):
    zeilen = [f"{pruefsumme(os.path.join(ziel, rel))}  {rel}\n"
              for rel in kit_dateien(kit, ziel)]
    pfad = os.path.join(ziel, LISTE)
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Kit-BL-270: Pruefsummen der Kit-Dateien, wie das letzte "
                 "Update sie schrieb. Nicht von Hand pflegen.\n")
        fh.writelines(zeilen)
    return 0


def main(argv):
    # Die Pfadliste liest die bash-Bahn per Befehlsersetzung. Unter Windows
    # schreibt Pythons Textmodus "\r\n"; das \r blieb am Pfad haengen, und
    # gesichert wurde nur die LETZTE Datei — beim Bauen an zwei geaenderten
    # Dateien gefunden.
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except (AttributeError, ValueError, OSError):
        pass
    if not argv or argv[0] not in ("pruefen", "sichern", "schreiben"):
        print(__doc__, file=sys.stderr)
        return 2
    verb, rest = argv[0], argv[1:]
    werte = {"--ziel": None, "--kit": None, "--stempel": None}
    alle = False
    pfade = []
    i = 0
    while i < len(rest):
        if rest[i] in werte and i + 1 < len(rest):
            werte[rest[i]] = rest[i + 1]
            i += 2
        elif rest[i] == "--alle":
            alle = True
            i += 1
        else:
            pfade.append(rest[i])
            i += 1
    ziel, kit, stempel = werte["--ziel"], werte["--kit"], werte["--stempel"]
    if not ziel or (verb != "sichern" and not kit):
        print(f"Fehler: {verb} braucht --ziel und --kit", file=sys.stderr)
        return 2
    if verb == "pruefen":
        return pruefen(ziel, kit)
    if verb == "schreiben":
        return schreiben(ziel, kit)
    if not stempel or (alle and not kit):
        print("Fehler: sichern braucht --stempel (und mit --alle --kit)",
              file=sys.stderr)
        return 2
    return sichern(ziel, stempel, kit_dateien(kit, ziel) if alle else pfade)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

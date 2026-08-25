#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (Kit-Werkzeug, von beiden Bahnen aus aufrufbar)
"""Prueft die nachrechenbaren Zusicherungen des README gegen die Wirklichkeit.

WARUM ES DIESES WERKZEUG GIBT
    Das README traegt Zahlen und Pfade, die sich wie Zusicherungen lesen, aber
    keine Mechanik hinter sich hatten. Zweimal ist genau daran etwas verrottet:

      * "62 Testdateien" und "369 Tests" standen im README, waehrend es 65 und
        476 waren. Daraufhin bekam kit-test.sh einen Waechter — der aber nur
        ZWEI feste Formulierungen kannte. Die dritte Stelle, freie Prosa mit
        "369 Regressionstests", stand danach noch Wochen falsch da.
      * `bash scripts/team-auth-setup.sh` stand als Befehl im README. Diesen
        Pfad gibt es nicht; das Skript liegt unter `bash/scripts/`. Der
        vorhandene Pfad-Waechter war NEGATIV formuliert (er verbot den alten
        Autorenmaschinen-Pfad) und konnte einen neuen falschen nicht sehen.

    Die Lehre aus beidem ist dieselbe: Ein Waechter, der eine ABSCHRIFT prueft,
    veraltet mit ihr. Geprueft wird deshalb die GATTUNG — jede Zahl, die eine
    Testzahl behauptet, und jeder Pfad, der auf das Repo zeigt.

WAS GEPRUEFT WIRD
    (1) Jede Zahl vor Regressionstests/Tests/Faelle/Testfaelle — auch die im
        Badge — gegen die gemessene Fallzahl.
    (2) Jede Zahl vor Testdateien gegen die gemessene Dateizahl.
    (3) Jede Zahl vor Dateien gegen das, was der Installer geschrieben hat.
    (4) Jeder Pfad, den das README nennt, gegen das Dateisystem des Kits.

    Die Messwerte kommen von aussen (kit-test.sh misst sie an einer FRISCHEN
    Installation). Ohne sie prueft das Werkzeug nur die Pfade — es rechnet
    bewusst nichts selbst nach, denn eine Zahl aus dem Repo waere wieder eine
    Abschrift statt einer Messung.

WARUM DIE PFADPRUEFUNG EINE AUSNAHMELISTE HAT
    Das README nennt zwei Ablagen nebeneinander: die des KITS (bash/, pwsh/,
    geteilt/ …) und die eines ZIELPROJEKTS (team/lib.sh, ./vollautomatik.sh).
    Die zweite Sorte existiert hier zu Recht nicht. Ein Waechter, der sie
    anmahnt, schlaegt an einer richtigen Stelle rot — und wird abgeschaltet
    statt befolgt. Die Regeln unten sind deshalb eng gefasst und benannt.
"""
import argparse
import re
import sys
from pathlib import Path

# BL-158: stdout/stderr ausdruecklich auf UTF-8 stellen — dieselbe Zeile, die
# `team/tools/*.py` seit BL-133 tragen, hier aber vergessen. Pythons Default
# fuer einen NICHT-Terminal-Strom ist die ANSI-Codepage der Maschine (auf einem
# deutschen Windows cp1252), und dieses Werkzeug gibt auf seiner ERFOLGS-Spur
# ein Haekchen aus. Ohne die Umstellung stirbt es also genau dann, wenn alles
# in Ordnung ist — mit UnicodeEncodeError und Exit 1. `kit-test.sh` liest das
# als "Das README steht gegen die frische Installation" und bricht ab: eine
# Kit-Meldung, die etwas voellig anderes behauptet als das, was passiert ist.
#
# Der BL-133-Waechter hat das nicht gesehen, weil er die GATTUNG
# `team/tools/*.py` prueft — und diese Datei liegt in `geteilt/`, weil der
# Installer sie nicht ins Zielprojekt kopiert. Zwei Gattungen, ein Fehler.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        # Ein umgelenkter Strom (pytest-capture) ist kein TextIOWrapper.
        pass

KIT = Path(__file__).resolve().parents[1]

# --- Zahlen -----------------------------------------------------------------
# Reihenfolge in der Alternative zaehlt: "Regressionstests" vor "Tests", sonst
# bliebe der laengere Begriff ungeprueft.
FAELLE = [
    re.compile(r"(\d+)\s+(?:Regressionstests|Testfälle|Tests|Fälle)\b"),
    re.compile(r"badge/Regressionstests-(\d+)-"),
]
TESTDATEIEN = [re.compile(r"(\d+)\s+Testdateien\b")]
DATEIEN = [re.compile(r"(\d+)\s+Dateien\b")]

# --- Pfade ------------------------------------------------------------------
PFAD_ENDUNG = re.compile(r"\.(?:sh|ps1|psm1|py|md|cmd|webp|svg)$")

# Jede Regel sagt, WARUM der Pfad hier nicht existieren muss. Eine Ausnahme
# ohne Grund waere eine Erlaubnis mit unbekanntem Umfang.
UEBERSPRUNGEN = (
    ("~",   "liegt im Home des Anwenders, nicht im Repo"),
    ("<",   "Platzhalter-Syntax wie <kit>/bash/install.sh"),
    ("./",  "Entrypoint eines ZIELPROJEKTS — im Kit liegt er unter bash/entry/"),
    ("../", "Schwester-Repo ausserhalb des Kits"),
    ("team/",  "Namensraum eines ZIELPROJEKTS — im Kit heisst er geteilt/ bzw. bash/"),
    ("team\\", "dasselbe auf der pwsh-Bahn"),
)


def _pfad_tokens(text):
    """Alles, was im README wie ein Pfad aussieht: Backticks und Link-Ziele."""
    tok = set()
    for m in re.finditer(r"`([^`\n]+)`", text):
        for wort in m.group(1).split():
            # Nur Randzeichen, NICHT den Punkt: sonst wird aus "./ralph.sh"
            # ein "/ralph.sh" und die ./-Regel unten greift nie. Ein
            # nachgestellter Punkt faellt ohnehin durch PFAD_ENDUNG.
            wort = wort.strip("(),;:")
            if "/" in wort and PFAD_ENDUNG.search(wort):
                tok.add(wort)
    for m in re.finditer(r"\]\(([^)\s]+)\)", text):
        ziel = m.group(1).split("#")[0]
        if ziel and not ziel.startswith(("http://", "https://", "mailto:")):
            tok.add(ziel)
    return tok


def pruefe_pfade(text):
    fehler = []
    for tok in sorted(_pfad_tokens(text)):
        if "*" in tok:
            continue  # ein Glob beschreibt eine Menge, keinen Pfad
        if any(tok.startswith(p) for p, _ in UEBERSPRUNGEN):
            continue
        if not (KIT / tok).exists():
            fehler.append(f"README nennt `{tok}` — im Kit gibt es das nicht.")
    return fehler


def pruefe_zahlen(text, soll, muster, was):
    fehler, gesehen = [], 0
    for rx in muster:
        for m in rx.finditer(text):
            gesehen += 1
            if int(m.group(1)) != soll:
                fehler.append(
                    f"README behauptet {m.group(1)} {was}, gemessen sind {soll} "
                    f"(»{m.group(0).strip()}«).")
    if gesehen == 0:
        fehler.append(f"README nennt die {was} ueberhaupt nicht mehr — "
                      f"eine Zusicherung, die verschwindet, faellt nicht auf.")
    return fehler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default=str(KIT / "README.md"))
    ap.add_argument("--faelle", type=int)
    ap.add_argument("--testdateien", type=int)
    ap.add_argument("--dateien", type=int)
    a = ap.parse_args()

    text = Path(a.readme).read_text(encoding="utf-8")
    fehler = pruefe_pfade(text)
    if a.faelle is not None:
        fehler += pruefe_zahlen(text, a.faelle, FAELLE, "Testfälle")
    if a.testdateien is not None:
        fehler += pruefe_zahlen(text, a.testdateien, TESTDATEIEN, "Testdateien")
    if a.dateien is not None:
        fehler += pruefe_zahlen(text, a.dateien, DATEIEN, "installierten Dateien")

    if fehler:
        for f in fehler:
            print(f"  ✗ {f}", file=sys.stderr)
        return 1
    print("✓ README: alle genannten Pfade existieren, alle Zahlen sind gemessen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

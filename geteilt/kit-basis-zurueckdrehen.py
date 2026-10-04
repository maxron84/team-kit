#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (Kit-Werkzeug, von beiden Bahnen aus aufrufbar)
"""Dreht in einer Wegwerf-Installation die Kit-Basis zurueck — fuer die
Update-Stufe des Selbsttests (Kit-BL-311).

WARUM
    Das Update traegt nach, was die Kit-Fassung SEIT DEM LETZTEN UPDATE neu
    hat (`team/.kit-basis/`). Im Selbsttest liegen Installation und Update auf
    demselben Kit-Stand: Es gibt nichts Neues, und der Nachtrag liefe nie.
    Dieses Werkzeug stellt die Lage her, als sei das Projekt mit einer
    aelteren Kit-Fassung installiert worden — drei Dinge fehlen in der Basis
    UND im Projekt:
      - die .gitignore-Zeile `.team-protokolle/`,
      - der Konfigurationswert `TEAM_ZIELSTAND_PRUEFUNG` (beide Bahnen),
      - die zwei Zeilen des Abschnitts 0 in der Abschluss-Gliederung der
        CLAUDE.md.
    Mit `--konflikt` aendert das Projekt dazu die Zeile direkt dahinter
    selbst: Kit und Projekt haben dieselbe Stelle angefasst, uebernommen
    werden darf nichts. `--aufloesen` nimmt diese Aenderung zurueck — dann
    arbeitet das naechste Update den Abschnitt ein.

    Eine Aenderung, die nichts trifft, ist ein Fehler (Exit 1): Sonst prueft
    die Stufe eine Lage, die es nicht gibt.

NUTZUNG
    kit-basis-zurueckdrehen.py                         prueft die Vorlagen
    kit-basis-zurueckdrehen.py <ablage> --konflikt     Basis zurueck + Konflikt
    kit-basis-zurueckdrehen.py <ablage> --aufloesen    Konflikt aufloesen
"""
import sys
from pathlib import Path

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

ABSCHNITT_0 = ("## 0. Für Menschen         Zehn Sätze ohne Fachkürzel: Frage, gebaut,\n"
               "##                         Überraschung, Kosten, offen (Kit-BL-243)\n")
DAHINTER = "## 1. Ist-Stand"
EIGEN = " (eigene Fassung des Projekts)"
GITIGNORE = ".team-protokolle/\n"
KONFIG = {"team.config.sh": 'TEAM_ZIELSTAND_PRUEFUNG="${TEAM_ZIELSTAND_PRUEFUNG:-}"\n',
          "team.config.ps1": "$TEAM_ZIELSTAND_PRUEFUNG = Team-Wert 'TEAM_ZIELSTAND_PRUEFUNG' ''\n"}
SCHLUESSEL = ("sh TEAM_ZIELSTAND_PRUEFUNG\n", "ps1 TEAM_ZIELSTAND_PRUEFUNG\n")


def _aendern(pfad, fehler, ersetzungen):
    roh = pfad.read_bytes()
    bom = roh.startswith(b"\xef\xbb\xbf")
    text = roh.decode("utf-8-sig")
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    for alt, neu in ersetzungen:
        if alt not in text:
            fehler.append(f"{pfad}: {alt.strip()!r} nicht gefunden")
            return
        text = text.replace(alt, neu, 1)
    if crlf:
        text = text.replace("\n", "\r\n")
    pfad.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))


def zurueckdrehen(ziel):
    fehler = []
    basis = ziel / "team" / ".kit-basis"
    _aendern(ziel / ".gitignore", fehler, [(GITIGNORE, "")])
    _aendern(basis / "gitignore.fragment", fehler, [(GITIGNORE, "")])
    for datei, zeile in KONFIG.items():
        if (ziel / datei).is_file():
            _aendern(ziel / datei, fehler, [(zeile, "")])
    _aendern(basis / "konfig-schluessel", fehler, [(s, "") for s in SCHLUESSEL])
    _aendern(basis / "CLAUDE.md", fehler, [(ABSCHNITT_0, "")])
    _aendern(ziel / "CLAUDE.md", fehler, [(ABSCHNITT_0, ""), (DAHINTER, DAHINTER + EIGEN)])
    return fehler


def aufloesen(ziel):
    fehler = []
    _aendern(ziel / "CLAUDE.md", fehler, [(DAHINTER + EIGEN, DAHINTER)])
    return fehler


def vorlagen_pruefen(kit):
    """Ohne Ziel: Stehen die Stellen, an denen gedreht wird, noch in den
    Vorlagen? Faellt hier auf, nicht erst nach einer Viertelstunde Selbsttest."""
    fehlt = []
    claude = (kit / "bootstrap" / "CLAUDE.md.vorlage").read_text(encoding="utf-8-sig")
    for marke in (ABSCHNITT_0, ABSCHNITT_0 + DAHINTER):
        if marke not in claude.replace("\r\n", "\n"):
            fehlt.append(f"bootstrap/CLAUDE.md.vorlage: {marke.splitlines()[-1]!r}")
    if GITIGNORE not in (kit / "bootstrap" / "gitignore.fragment").read_text(encoding="utf-8"):
        fehlt.append("bootstrap/gitignore.fragment: .team-protokolle/")
    for datei, vorlage in (("team.config.sh", "bash/entry/team.config.sh"),
                           ("team.config.ps1", "pwsh/entry/team.config.ps1")):
        if KONFIG[datei] not in (kit / vorlage).read_text(encoding="utf-8-sig"):
            fehlt.append(f"{vorlage}: TEAM_ZIELSTAND_PRUEFUNG")
    if fehlt:
        print("Diese Stellen fehlen in den Vorlagen — das Zurueckdrehen im "
              "Selbsttest griffe ins Leere (Kit-BL-311):", file=sys.stderr)
        for f in fehlt:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("✓ Alle Stellen zum Zurueckdrehen stehen in den Vorlagen (Kit-BL-311).")
    return 0


def main(argv):
    if not argv:
        return vorlagen_pruefen(Path(__file__).resolve().parents[1])
    if len(argv) != 2 or argv[1] not in ("--konflikt", "--aufloesen"):
        print(__doc__, file=sys.stderr)
        return 2
    ziel = Path(argv[0])
    fehler = zurueckdrehen(ziel) if argv[1] == "--konflikt" else aufloesen(ziel)
    if fehler:
        print("Das Zurueckdrehen hat nicht gegriffen — dann prueft die Stufe "
              "nichts mehr (Kit-BL-311):", file=sys.stderr)
        for f in fehler:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("Kit-Basis zurueckgedreht: .gitignore-Zeile, TEAM_ZIELSTAND_PRUEFUNG, "
          "Abschnitt 0 — mit Konflikt in der Zeile dahinter."
          if argv[1] == "--konflikt" else
          "Konflikt aufgeloest: die Zeile hinter Abschnitt 0 steht wieder wie in der Basis.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

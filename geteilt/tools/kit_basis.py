#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteiltes Werkzeug, von beiden Installern aufgerufen)
"""kit_basis.py — was die Kit-Fassung beim letzten Update war, damit das
naechste Update Neues selbst nachtragen kann (Kit-BL-311).

DIE LAGE
    Ein `--update` ersetzt die Infrastruktur und laesst die Projektdateien
    stehen: `.gitignore`, `team.config.*`, `CLAUDE.md`. Was die Kit-Fassung
    dort Neues hatte, meldete es nur, und der Mensch trug es von Hand nach —
    im Feld (`Feld F`, 2026-10-04) eine `.gitignore`-Zeile, zwei
    Konfigurationswerte und achtzig Zeilen Regeln. Der Grund war richtig:
    Eine fehlende Zeile kann eine bewusst entfernte sein, eine Regel im
    Projekt kann bewusst anders lauten. Unterscheiden liess sich das nicht,
    weil niemand wusste, was die Kit-Fassung beim letzten Mal war.

DER WEG
    Das Update merkt es sich: `team/.kit-basis/` haelt die Kit-Seite der drei
    Dateien so, wie sie beim letzten Lauf war. Damit wird die Frage
    entscheidbar:
      - NEU seit dem letzten Update — das Projekt kann es nicht bewusst
        entfernt haben: wird eingetragen.
      - Damals schon da, im Projekt jetzt weg — bewusst entfernt: nur gemeldet,
        wie bisher (BL-109, BL-200).
      - CLAUDE.md: Dreiwege-Abgleich aus Projekt, Basis und jetziger
        Kit-Fassung (`git merge-file`). Ohne Konflikt wird eingearbeitet und
        die alte Fassung gesichert. Mit Konflikt bleibt die Datei, wie sie
        ist; der Vorschlag mit Konfliktmarken liegt daneben.
    Ohne Basis — ein Projekt aus der Zeit davor — bleibt es fuer `.gitignore`
    und Konfiguration beim Melden. Fuer die CLAUDE.md wird die Basis aus der
    Geschichte des Kits geschaetzt; dann gibt es nur einen Vorschlag, nie
    einen Schreibzugriff.

    Die Basis rueckt nur vor, wenn das Projekt die Kit-Fassung aufgenommen
    hat. Bleibt ein Konflikt offen, bleibt sie stehen — das naechste Update
    bietet dieselben Regeln noch einmal an, statt sie zu vergessen.

NUTZUNG (aus den Installern, nicht von Hand)
    kit_basis.py schreiben --ziel Z --kit K [--claude DATEI]
    kit_basis.py gitignore --ziel Z --kit K
    kit_basis.py konfig    --ziel Z --kit K
    kit_basis.py claude    --ziel Z --kit K --neu DATEI --sicherung ORDNER
                           --ablage ORDNER --bahn sh|ps1

    Ausgabe je Zeile "<marke> <text>", Marke `ok`, `!` oder `-`; der Installer
    faerbt sie. `claude` endet mit 0 (nichts offen), 10 (ein Vorschlag wartet
    auf den Menschen) oder 11 (keine Basis — der Installer meldet wie bisher).
"""
import difflib
import os
import re
import subprocess
import sys
import tempfile

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

BASIS = os.path.join("team", ".kit-basis")
KONFIGS = (("team.config.sh", "sh", os.path.join("bash", "entry", "team.config.sh")),
           ("team.config.ps1", "ps1", os.path.join("pwsh", "entry", "team.config.ps1")))
VORLAGE_CLAUDE = "bootstrap/CLAUDE.md.vorlage"
PLATZHALTER = re.compile(r"\{\{([A-Z_]+)\}\}")
OFFEN, OHNE_BASIS = 10, 11


# --- Dateien lesen und schreiben, wie sie sind --------------------------------

def lesen(pfad):
    """(Text mit LF, BOM?, CRLF?) — geschrieben wird spaeter in derselben Art."""
    with open(pfad, "rb") as fh:
        roh = fh.read()
    bom = roh.startswith(b"\xef\xbb\xbf")
    text = roh.decode("utf-8-sig")
    return text.replace("\r\n", "\n"), bom, "\r\n" in text


def schreiben_wie(pfad, text, bom=False, crlf=False):
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(pfad, "wb") as fh:
        fh.write((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))


def _basis(ziel, name):
    return os.path.join(ziel, BASIS, name)


# --- Bausteine ----------------------------------------------------------------

def fragment_zeilen(text):
    return [z for z in text.split("\n") if z.strip() and not z.lstrip().startswith("#")]


def _zuweisung(name, bahn):
    return (re.compile(rf"^{re.escape(name)}=") if bahn == "sh"
            else re.compile(rf"^\${re.escape(name)}\s*="))


def konfig_schluessel(text, bahn):
    """Die Namen, die eine Konfiguration SETZT, in ihrer Reihenfolge — dieselbe
    Lesart wie konfig_schluessel/Konfig-Schluessel in den Installern."""
    muster = (r"^(TEAM_[A-Z0-9_]+)=" if bahn == "sh"
              else r"^\$(TEAM_[A-Z0-9_]+)\s*=")
    namen = []
    for m in re.finditer(muster, text, flags=re.M):
        if m.group(1) not in namen:
            namen.append(m.group(1))
    return namen


def _nachlauf(name, bahn):
    return (re.compile(rf"^export {re.escape(name)}\b") if bahn == "sh"
            else re.compile(rf"^\$env:{re.escape(name)}\s*="))


def vorlagen_block(text, name, bahn):
    """Kommentar darueber, die Zuweisung, ein `export`/`$env:` dazu — oder None,
    wenn der Wert Projekt- oder Maschinensache ist (Platzhalter)."""
    zeilen = text.split("\n")
    zuweisung, nachlauf = _zuweisung(name, bahn), _nachlauf(name, bahn)
    for i, z in enumerate(zeilen):
        if zuweisung.match(z):
            break
    else:
        return None
    if "{{" in zeilen[i]:
        return None
    j = i
    while j > 0 and zeilen[j - 1].startswith("#"):
        j -= 1
    block = zeilen[j:i + 1]
    block += [z for z in zeilen if nachlauf.match(z) and "{{" not in z]
    return block


# --- schreiben ------------------------------------------------------------------

def basis_schreiben(ziel, kit, claude=None):
    """Die Kit-Seite fuer das naechste Update ablegen: Fragment und
    Schluessel immer, die CLAUDE.md nur, wenn sie uebergeben wird."""
    os.makedirs(os.path.join(ziel, BASIS), exist_ok=True)
    fragment = os.path.join(kit, "bootstrap", "gitignore.fragment")
    if os.path.isfile(fragment):
        schreiben_wie(_basis(ziel, "gitignore.fragment"), lesen(fragment)[0])
    zeilen = []
    for _datei, bahn, vorlage in KONFIGS:
        pfad = os.path.join(kit, vorlage)
        if os.path.isfile(pfad):
            zeilen += [f"{bahn} {n}" for n in konfig_schluessel(lesen(pfad)[0], bahn)]
    schreiben_wie(_basis(ziel, "konfig-schluessel"), "\n".join(zeilen) + "\n")
    if claude:
        schreiben_wie(_basis(ziel, "CLAUDE.md"), lesen(claude)[0])
    return 0


# --- .gitignore -----------------------------------------------------------------

def gitignore(ziel, kit):
    basis = _basis(ziel, "gitignore.fragment")
    datei = os.path.join(ziel, ".gitignore")
    fragment = os.path.join(kit, "bootstrap", "gitignore.fragment")
    if not (os.path.isfile(basis) and os.path.isfile(datei) and os.path.isfile(fragment)):
        return 0
    jetzt = lesen(fragment)[0]
    alt = set(fragment_zeilen(lesen(basis)[0]))
    text, bom, crlf = lesen(datei)
    da = {z.strip() for z in text.split("\n")}
    neu = [z for z in fragment_zeilen(jetzt) if z.strip() not in da and z not in alt]
    if not neu:
        return 0
    zeilen = jetzt.split("\n")
    anhang = []
    for z in neu:
        i = zeilen.index(z)
        j = i
        while j > 0 and zeilen[j - 1].lstrip().startswith("#"):
            j -= 1
        anhang += zeilen[j:i + 1]
    if text and not text.endswith("\n"):
        text += "\n"
    schreiben_wie(datei, text + "\n".join(anhang) + "\n", bom, crlf)
    print(f"ok .gitignore: {len(neu)} neue Zeile(n) der Kit-Fassung eingetragen (Kit-BL-311):")
    for z in neu:
        print(f"-       {z}")
    return 0


# --- Konfiguration --------------------------------------------------------------

def _basis_schluessel(ziel):
    pfad = _basis(ziel, "konfig-schluessel")
    if not os.path.isfile(pfad):
        return None
    schluessel = {}
    for z in lesen(pfad)[0].split("\n"):
        teile = z.split()
        if len(teile) == 2:
            schluessel.setdefault(teile[0], set()).add(teile[1])
    return schluessel


def _einfuegen(text, block, name, reihenfolge, bahn):
    """Hinter den Wert, der in der Vorlage davor steht — sonst ans Ende."""
    zeilen = text.split("\n")
    stelle = None
    for vorher in reversed(reihenfolge[:reihenfolge.index(name)]):
        zuweisung, nachlauf = _zuweisung(vorher, bahn), _nachlauf(vorher, bahn)
        treffer = [i for i, z in enumerate(zeilen) if zuweisung.match(z)]
        if treffer:
            stelle = treffer[-1] + 1
            while stelle < len(zeilen) and nachlauf.match(zeilen[stelle]):
                stelle += 1
            break
    if stelle is None:
        while zeilen and zeilen[-1] == "":
            zeilen.pop()
        return "\n".join(zeilen + [""] + block) + "\n"
    return "\n".join(zeilen[:stelle] + [""] + block + zeilen[stelle:])


def konfig(ziel, kit):
    alt = _basis_schluessel(ziel)
    if alt is None:
        return 0
    for datei, bahn, vorlage in KONFIGS:
        pfad, vpfad = os.path.join(ziel, datei), os.path.join(kit, vorlage)
        if not (os.path.isfile(pfad) and os.path.isfile(vpfad)):
            continue
        vtext = lesen(vpfad)[0]
        text, bom, crlf = lesen(pfad)
        soll = konfig_schluessel(vtext, bahn)
        ist = set(konfig_schluessel(text, bahn))
        eingetragen = []
        for name in soll:
            if name in ist or name in alt.get(bahn, set()):
                continue
            block = vorlagen_block(vtext, name, bahn)
            if block is None:
                continue        # Projekt- oder Maschinensache: BL-200 meldet ihn
            text = _einfuegen(text, block, name, soll, bahn)
            eingetragen.append(name)
        if eingetragen:
            schreiben_wie(pfad, text, bom, crlf)
            print(f"ok {datei}: {len(eingetragen)} neue(r) Wert(e) der Kit-Fassung "
                  f"eingetragen, mit dem Vorgabewert der Vorlage (Kit-BL-311):")
            print(f"-       {', '.join(eingetragen)}")
    return 0


# --- CLAUDE.md ------------------------------------------------------------------

def _zaehlen(a, b):
    plus = minus = 0
    for z in difflib.unified_diff(a.split("\n"), b.split("\n"), lineterm="", n=0):
        if z.startswith("+") and not z.startswith("+++"):
            plus += 1
        elif z.startswith("-") and not z.startswith("---"):
            minus += 1
    return plus, minus


def dreiwege(projekt, basis, kit_jetzt):
    """(Ergebnis, Zahl der Konflikte) — `git merge-file`, so wie git selbst
    zusammenfuehrt. Konfliktstellen tragen die ueblichen Marken."""
    with tempfile.TemporaryDirectory() as tmp:
        pfade = []
        for name, text in (("projekt", projekt), ("basis", basis), ("kit", kit_jetzt)):
            p = os.path.join(tmp, name)
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            pfade.append(p)
        r = subprocess.run(
            ["git", "merge-file", "-p", "-L", "Projekt",
             "-L", "Kit-Fassung beim letzten Update", "-L", "Kit-Fassung jetzt",
             *pfade], capture_output=True)
    if r.returncode < 0 or r.returncode > 127:
        raise RuntimeError(r.stderr.decode("utf-8", "replace"))
    return r.stdout.decode("utf-8"), r.returncode


def _werte(vorlage, gerendert):
    """Platzhalter -> Wert, gelesen an ausgerichteten Zeilenpaaren der
    jetzigen Vorlage und ihrer gerenderten Fassung."""
    v, g = vorlage.split("\n"), gerendert.split("\n")
    werte = {}
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, v, g, autojunk=False).get_opcodes():
        if tag != "replace":
            continue
        for zv in v[i1:i2]:
            teile = PLATZHALTER.split(zv)
            if len(teile) == 1:
                continue
            regex = "^" + "".join(re.escape(t) if k % 2 == 0 else "(.*?)"
                                  for k, t in enumerate(teile)) + "$"
            for zg in g[j1:j2]:
                m = re.match(regex, zg)
                if m:
                    for name, wert in zip(teile[1::2], m.groups()):
                        werte.setdefault(name, wert)
                    break
    return werte


def basis_schaetzen(kit, kit_jetzt, projekt):
    """(Basis, Commit, Datum) — die historische Kit-Fassung, die dem Projekt am
    naechsten liegt, mit den Werten des Projekts gerendert. None, wenn das
    Kit kein Git-Klon ist."""
    def git(*args):
        return subprocess.run(["git", "-C", kit, *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
    vorlage = os.path.join(kit, *VORLAGE_CLAUDE.split("/"))
    if git("rev-parse", "--is-inside-work-tree").returncode != 0 \
            or not os.path.isfile(vorlage):
        return None
    werte = _werte(lesen(vorlage)[0], kit_jetzt)
    beste = None
    log = git("log", "--follow", "--format=@%h %ad", "--date=short",
              "--name-only", "--", VORLAGE_CLAUDE).stdout.split("\n")
    kopf = None
    for z in log:
        if z.startswith("@"):
            kopf = z[1:].split(" ", 1)
            continue
        if not z.strip() or not kopf:
            continue
        alt = git("show", f"{kopf[0]}:{z.strip()}")
        if alt.returncode != 0:
            continue
        text = alt.stdout.replace("\r\n", "\n")
        for name, wert in werte.items():
            text = text.replace("{{" + name + "}}", wert)
        abstand = sum(_zaehlen(text, projekt))
        if beste is None or abstand < beste[0]:
            beste = (abstand, text, kopf[0], kopf[1])
    return None if beste is None else beste[1:]


def claude(ziel, kit, neu, sicherung, ablage, bahn):
    pfad = os.path.join(ziel, "CLAUDE.md")
    if not (os.path.isfile(pfad) and os.path.isfile(neu)):
        return OHNE_BASIS
    projekt, bom, crlf = lesen(pfad)
    kit_jetzt = lesen(neu)[0]
    basis_pfad = _basis(ziel, "CLAUDE.md")
    geschaetzt = None
    if os.path.isfile(basis_pfad):
        basis = lesen(basis_pfad)[0]
    else:
        schaetzung = basis_schaetzen(kit, kit_jetzt, projekt)
        if schaetzung is None:
            return OHNE_BASIS
        basis, commit, datum = schaetzung
        geschaetzt = (commit, datum)

    def basis_setzen(text):
        os.makedirs(os.path.dirname(basis_pfad), exist_ok=True)
        schreiben_wie(basis_pfad, text)

    if kit_jetzt == basis:
        print("ok CLAUDE.md: seit dem letzten Update keine neue Regel in der "
              "Kit-Fassung — was abweicht, ist deine Anpassung (Kit-BL-311).")
        basis_setzen(kit_jetzt)
        return 0
    ergebnis, konflikte = dreiwege(projekt, basis, kit_jetzt)
    if not konflikte and ergebnis == projekt:
        print("ok CLAUDE.md: die neuen Regeln der Kit-Fassung stehen schon darin "
              "(Kit-BL-311).")
        basis_setzen(kit_jetzt)
        return 0
    if not konflikte and not geschaetzt:
        os.makedirs(sicherung, exist_ok=True)
        with open(pfad, "rb") as fh, \
                open(os.path.join(sicherung, "CLAUDE.md"), "wb") as aus:
            aus.write(fh.read())
        schreiben_wie(pfad, ergebnis, bom, crlf)
        basis_setzen(kit_jetzt)
        plus, minus = _zaehlen(projekt, ergebnis)
        rel = os.path.relpath(os.path.join(sicherung, "CLAUDE.md"), ziel)
        print(f"ok CLAUDE.md: die Regeln der jetzigen Kit-Fassung eingearbeitet "
              f"(+{plus}/-{minus} Zeilen), deine Anpassungen bleiben (Kit-BL-311).")
        print(f"-     Die alte Fassung liegt unter {rel.replace(os.sep, '/')}; "
              f"ansehen mit:  git diff -- CLAUDE.md")
        return 0

    os.makedirs(ablage, exist_ok=True)
    vorschlag = os.path.join(ablage, "CLAUDE.md.vorschlag")
    schreiben_wie(vorschlag, ergebnis, bom, crlf)
    # Die genannten Pfade in der Schreibweise der Bahn: Eine Git-Bash unter
    # Windows reicht `C:/…` herein, und ein angehaengtes `\` ergaebe einen
    # gemischten Pfad, den `cp` nicht zuverlaessig versteht.
    if bahn == "sh":
        vorschlag, pfad = vorschlag.replace("\\", "/"), pfad.replace("\\", "/")
    if geschaetzt:
        basis_setzen(basis)
        print(f"! CLAUDE.md: noch ohne Basis (erstes Update mit Kit-BL-311) — sie "
              f"stammt vermutlich aus der Kit-Fassung vom {geschaetzt[1]} "
              f"({geschaetzt[0]}). Uebernommen wird deshalb nichts, es gibt "
              f"einen Vorschlag.")
    else:
        print(f"! CLAUDE.md: {konflikte} Stelle(n) haben Kit-Fassung und Projekt "
              f"beide geaendert — uebernommen wird nichts (Kit-BL-311).")
    zusatz = f", {konflikte} Stelle(n) mit Konfliktmarken" if konflikte else ""
    print(f"-     Vorschlag mit den Regeln der jetzigen Kit-Fassung{zusatz}:")
    print(f"-       {vorschlag}")
    befehl = (f"Copy-Item -LiteralPath '{vorschlag}' -Destination '{pfad}'"
              if bahn == "ps1" else f"cp \"{vorschlag}\" \"{pfad}\"")
    print(f"-     Ansehen{', Konflikte aufloesen' if konflikte else ''}, "
          f"dann uebernehmen:  {befehl}")
    return OFFEN


# --- Aufruf ---------------------------------------------------------------------

def _argumente(argv, erlaubt):
    werte = {}
    i = 0
    while i < len(argv):
        name = argv[i][2:] if argv[i].startswith("--") else None
        if name not in erlaubt or i + 1 >= len(argv):
            raise ValueError(f"unbekanntes oder unvollstaendiges Argument: {argv[i]}")
        werte[name] = argv[i + 1]
        i += 2
    return werte


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    verb, rest = argv[0], argv[1:]
    try:
        if verb == "schreiben":
            a = _argumente(rest, {"ziel", "kit", "claude"})
            return basis_schreiben(a["ziel"], a["kit"], a.get("claude"))
        if verb == "gitignore":
            a = _argumente(rest, {"ziel", "kit"})
            return gitignore(a["ziel"], a["kit"])
        if verb == "konfig":
            a = _argumente(rest, {"ziel", "kit"})
            return konfig(a["ziel"], a["kit"])
        if verb == "claude":
            a = _argumente(rest, {"ziel", "kit", "neu", "sicherung", "ablage", "bahn"})
            return claude(a["ziel"], a["kit"], a["neu"], a["sicherung"],
                          a["ablage"], a.get("bahn", "sh"))
    except (KeyError, ValueError) as fehler:
        print(f"Fehler: {fehler}", file=sys.stderr)
        return 2
    print(f"Fehler: unbekanntes Verb '{verb}'", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

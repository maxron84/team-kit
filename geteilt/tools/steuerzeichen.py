#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteiltes Werkzeug, von beiden Bahnen aus aufrufbar)
r"""steuerzeichen.py — findet Steuerzeichen, die auf dem Weg in eine Datei aus
einem Backslash-Escape entstanden sind (Kit-BL-327).

DIE LAGE
    Ein `\b` in einem regulaeren Ausdruck wird zum Byte 0x08, wenn der Text
    ueber einen Heredoc der Shell, ueber `python -c` oder ueber einen nicht
    rohen Python-String in die Datei geht. Die Zusicherung verlangt dann ein
    Backspace im geprueften Text und kann nie mehr rot werden — sie besteht
    jede Probe des Teams, weil Mutationen ueber ANDERE Zusicherungen desselben
    Tests rot werden. Im Feld traf dieselbe Bauart Plaene, CHANGELOG und
    Werkzeuge: `\a` aus `.\abnahme.cmd`, `\v` aus `.\vollautomatik.cmd`, `\f`
    und `\r`. Ein CR ohne folgendes LF laesst git die Datei sogar als binaer
    einstufen; unter `core.autocrlf` ging sie dann ganz mit CRLF ins Repo.

DIE REGEL
    Verboten sind Bytes unter 0x20 — ausser Tab (0x09) und LF (0x0A). Ein CR
    (0x0D) ist nur direkt vor einem LF erlaubt; ein CR am Dateiende steht
    allein und zaehlt. Gemeldet wird Datei:Zeile, das Byte und das
    wahrscheinliche Escape (0x08 aus `\b`, 0x0C aus `\f`, 0x0B aus `\v`, 0x07
    aus `\a`, 0x0D aus `\r`, 0x1B aus `\e`, 0x01 bis 0x06 aus einem oktalen
    Escape wie dem Rueckverweis `\1`).

BINAER
    Eine Datei mit einem NUL in den ersten 8000 Bytes ist binaer und wird
    uebersprungen — dieselbe Grenze, an der git eine Datei fuer den Diff als
    binaer zaehlt. Ebenso eine, der .gitattributes `binary` oder `-diff` gibt.
    NICHT `git ls-files --eol`: Dort macht ein einzelnes CR die Datei zu
    `-text` — genau der Fall, den diese Pruefung finden soll.

DER BLINDE FLECK
    Ein `\t`, das zum Tabulator wurde, und ein `\n`, das zum Zeilenumbruch
    wurde, sieht diese Pruefung nicht: Beide Zeichen sind erlaubt, sonst waere
    jede Textdatei ein Fund. Dagegen hilft nur, Text mit Backslashes mit dem
    Werkzeug zum Bearbeiten von Dateien zu schreiben — der Satz dazu steht im
    Briefing von Ralph und Frank.

DER AUSWEG FUER ABSICHT
    Eine Datei, die Steuerzeichen absichtlich traegt (eine Fixture mit
    ANSI-Farbcodes, ein Seitenvorschub als Trenner), bekommt in .gitattributes
    das Attribut `steuerzeichen-erlaubt`:

        tests/fixtures/terminal-ausgabe.txt  steuerzeichen-erlaubt

    Ausdruecklich, versioniert und im Diff sichtbar. Gelesen wird die Datei
    trotzdem: Traegt sie Steuerzeichen, steht ein Hinweis da, kein Fund.

NUTZUNG
    steuerzeichen.py pruefen               die geaenderten Dateien des
                                           Arbeitsbaums (vor dem Commit)
    steuerzeichen.py pruefen --seit REV    die Dateien der Commits REV..HEAD,
                                           im committeten Stand
    steuerzeichen.py pruefen --versioniert alle versionierten Dateien
    steuerzeichen.py pruefen DATEI...      genau diese Dateien

    Exit 0 = sauber · 3 = Funde (auf stdout, Datei:Zeile) · 2 = Bedienfehler
"""
import re
import subprocess
import sys
from pathlib import Path

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts. Unter
# einem deutschen Windows schriebe Python sonst cp1252, und jeder Aufrufer im
# Kit liest UTF-8.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        # Ein umgelenkter Strom (pytest-capture) ist kein TextIOWrapper.
        pass

# Die Regel als EIN Muster: jedes Byte unter 0x20 ausser Tab, LF und CR — und
# jedes CR, auf das kein LF folgt, mitten im Text wie am Dateiende.
VERBOTEN = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]|\r(?!\n)")

# So weit sucht git ein NUL, bevor es eine Datei fuer den Diff binaer nennt.
BINAER_GRENZE = 8000

ATTRIBUT = "steuerzeichen-erlaubt"

# Bytes als Zahlen statt als Escape: Diese Datei soll selbst nicht davon
# abhaengen, dass ein Escape den Weg in sie unbeschaedigt ueberstanden hat.
NUL = bytes([0x00])
LF = 0x0A
TAB = 0x09

# Name und wahrscheinliche Herkunft je Byte — die Spur zurueck zu der Stelle
# im Code, die das Zeichen geschrieben hat.
HERKUNFT = {
    0x00: ("NUL", r"\0"),
    0x01: ("SOH", r"\1"),
    0x02: ("STX", r"\2"),
    0x03: ("ETX", r"\3"),
    0x04: ("EOT", r"\4"),
    0x05: ("ENQ", r"\5"),
    0x06: ("ACK", r"\6"),
    0x07: ("BEL", r"\a"),
    0x08: ("BS", r"\b"),
    0x0B: ("VT", r"\v"),
    0x0C: ("FF", r"\f"),
    0x0D: ("CR", r"\r"),
    0x1B: ("ESC", r"\e"),
}

# So viele Zeichen Zusammenhang stehen links und rechts der Fundstelle.
UMFELD = 32

NACHSATZ = r"""  Solche Zeichen entstehen meist auf dem Weg in die Datei: Text mit
  Backslashes ging ueber einen Heredoc, `python -c` oder einen nicht rohen
  String, und aus dem Escape wurde das Zeichen. Reparieren: das Byte durch
  sein Escape ersetzen — mit dem Werkzeug zum Bearbeiten von Dateien — und
  neu committen.
  Gehoert ein Zeichen absichtlich hinein (Fixture): in .gitattributes
  `<pfad> steuerzeichen-erlaubt` eintragen.
  Nicht erkennbar ist ein `\t`, das zum Tabulator, und ein `\n`, das zum
  Zeilenumbruch wurde — beide Zeichen sind erlaubt (Kit-BL-327)."""


class Bedienfehler(Exception):
    """Falscher Aufruf oder kein Git, wo eines gebraucht wird — Exit 2."""


def _git(cwd, *args, eingabe=None):
    try:
        return subprocess.run(["git", *args], cwd=str(cwd), input=eingabe,
                              capture_output=True)
    except OSError as fehler:
        raise Bedienfehler(f"git laesst sich nicht starten: {fehler}")


def _text(roh):
    """Ein Pfad aus git (Bytes) als str — ohne an fremder Kodierung zu
    sterben."""
    return roh.decode("utf-8", "surrogateescape")


def _bytes(pfad):
    return pfad.encode("utf-8", "surrogateescape")


def _anzeige(pfad):
    return _bytes(pfad).decode("utf-8", "replace")


def _nul_liste(roh):
    return [_text(t) for t in roh.split(NUL) if t]


def _wurzel(cwd):
    r = _git(cwd, "rev-parse", "--show-toplevel")
    if r.returncode != 0:
        raise Bedienfehler("kein Git-Repo — nenne die Dateien ausdruecklich: "
                           "steuerzeichen.py pruefen DATEI...")
    return Path(_text(r.stdout.strip()))


# --- Welche Dateien ------------------------------------------------------------

def geaenderte_dateien(wurzel):
    """Was der naechste Commit mitnaehme: geaendert, gestaged, neu — ohne
    Loeschungen. Pfade relativ zur Wurzel."""
    r = _git(wurzel, "status", "--porcelain", "-z", "--untracked-files=all")
    if r.returncode != 0:
        raise Bedienfehler(f"git status scheitert: {_text(r.stderr).strip()}")
    felder = r.stdout.split(NUL)
    pfade, i = [], 0
    while i < len(felder):
        feld = felder[i]
        i += 1
        if len(feld) < 4:
            continue
        # Bei einer Umbenennung (R) oder Kopie (C) folgt der alte Name als
        # eigenes Feld; gemeint ist der neue.
        if feld[:1] in (b"R", b"C"):
            i += 1
        pfade.append(_text(feld[3:]))
    return pfade


def dateien_seit(wurzel, rev):
    """Die Dateien der Commits REV..HEAD, ohne die geloeschten."""
    r = _git(wurzel, "diff", "-z", "--name-only", "--diff-filter=d", rev,
             "HEAD", "--")
    if r.returncode != 0:
        raise Bedienfehler(f"'{rev}..HEAD' laesst sich nicht vergleichen: "
                           f"{_text(r.stderr).strip()}")
    return _nul_liste(r.stdout)


def versionierte_dateien(wurzel):
    r = _git(wurzel, "ls-files", "-z")
    if r.returncode != 0:
        raise Bedienfehler(f"git ls-files scheitert: {_text(r.stderr).strip()}")
    return _nul_liste(r.stdout)


# --- Inhalte -------------------------------------------------------------------

def aus_dem_arbeitsbaum(basis, pfade):
    """[(pfad, bytes|None)] — None fuer alles, was keine lesbare Datei ist
    (Ordner, Verweis, geloescht)."""
    ergebnis = []
    for pfad in pfade:
        datei = basis / pfad
        if datei.is_symlink() or not datei.is_file():
            ergebnis.append((pfad, None))
            continue
        try:
            ergebnis.append((pfad, datei.read_bytes()))
        except OSError as fehler:
            print(f"  nicht lesbar: {_anzeige(pfad)} ({fehler})", file=sys.stderr)
            ergebnis.append((pfad, None))
    return ergebnis


def aus_dem_commit(wurzel, pfade, rev="HEAD"):
    """[(pfad, bytes|None)] im committeten Stand — geurteilt wird ueber den
    Commit, nicht ueber einen Arbeitsbaum, der ihn inzwischen ueberdeckt."""
    gueltig = [p for p in pfade if LF not in _bytes(p)]
    if not gueltig:
        return [(p, None) for p in pfade]
    anfrage = b"".join(rev.encode("utf-8") + b":" + _bytes(p) + bytes([LF])
                       for p in gueltig)
    r = _git(wurzel, "cat-file", "--batch", eingabe=anfrage)
    if r.returncode != 0:
        raise Bedienfehler(f"git cat-file scheitert: {_text(r.stderr).strip()}")
    aus, pos, inhalte = r.stdout, 0, {}
    for pfad in gueltig:
        ende = aus.index(LF, pos)
        kopf = aus[pos:ende]
        pos = ende + 1
        if kopf.endswith((b" missing", b" ambiguous")):
            inhalte[pfad] = None
            continue
        _, typ, groesse = kopf.rsplit(b" ", 2)
        groesse = int(groesse)
        inhalte[pfad] = aus[pos:pos + groesse] if typ == b"blob" else None
        pos += groesse + 1
    return [(p, inhalte.get(p)) for p in pfade]


def attribute(cwd, pfade):
    """{pfad: (binaer_per_attribut, erlaubt)} aus .gitattributes. Ausserhalb
    von Git gibt es keine — dann gilt fuer jede Datei die Regel."""
    if not pfade:
        return {}
    eingabe = b"".join(_bytes(p) + NUL for p in pfade)
    try:
        r = _git(cwd, "check-attr", "-z", "--stdin", "diff", ATTRIBUT,
                 eingabe=eingabe)
    except Bedienfehler:
        return {}
    if r.returncode != 0:
        return {}
    felder = r.stdout.split(NUL)
    ergebnis = {}
    for i in range(0, len(felder) - 2, 3):
        pfad, name, wert = _text(felder[i]), felder[i + 1], felder[i + 2]
        binaer, erlaubt = ergebnis.get(pfad, (False, False))
        if name == b"diff" and wert == b"unset":
            binaer = True
        if name == ATTRIBUT.encode("ascii") and wert in (b"set", b"true"):
            erlaubt = True
        ergebnis[pfad] = (binaer, erlaubt)
    return ergebnis


# --- Die Regel -----------------------------------------------------------------

def ist_binaer(daten):
    return 0 in daten[:BINAER_GRENZE]


def funde_in(daten):
    """[(zeile, offset)] je verbotenem Byte. Gezaehlt wird nach LF, wie git
    und `grep -n` zaehlen."""
    funde, zeile, bisher = [], 1, 0
    for treffer in VERBOTEN.finditer(daten):
        pos = treffer.start()
        zeile += daten.count(LF, bisher, pos)
        bisher = pos
        funde.append((zeile, pos))
    return funde


def _sichtbar(text):
    """Text mit jedem Steuerzeichen als <0xNN> — die Meldung selbst darf
    keines ins Log tragen (ein CR dort ueberschriebe die Zeile)."""
    return "".join(f"<0x{ord(z):02X}>" if ord(z) < 0x20 and ord(z) != TAB else z
                   for z in text)


def umfeld(daten, pos):
    """Die Fundstelle mit bis zu UMFELD Zeichen davor und danach, aus ihrer
    Zeile."""
    anfang = daten.rfind(LF, 0, pos) + 1
    ende = daten.find(LF, pos)
    ende = len(daten) if ende == -1 else ende
    links = daten[anfang:pos].decode("utf-8", "replace")
    rechts = daten[pos + 1:ende].decode("utf-8", "replace")
    vorn = "…" + links[-UMFELD:] if len(links) > UMFELD else links
    hinten = rechts[:UMFELD] + "…" if len(rechts) > UMFELD else rechts
    return _sichtbar(vorn + chr(daten[pos]) + hinten)


def beschreibung(byte):
    name, escape = HERKUNFT.get(byte, ("", ""))
    kopf = f"0x{byte:02X}" + (f" ({name})" if name else "")
    if escape:
        return f"{kopf}, wahrscheinlich aus `{escape}`"
    return f"{kopf}, Herkunft unbekannt"


def pruefe(eintraege, attr):
    """Gibt (funde, betroffene, hinweise, gepruefte) zurueck; Funde und
    Hinweise als fertige Zeilen, betroffene als Menge der Pfade."""
    funde, betroffene, hinweise, gepruefte = [], set(), [], 0
    for pfad, daten in eintraege:
        if daten is None:
            continue
        binaer, erlaubt = attr.get(pfad, (False, False))
        if binaer or ist_binaer(daten):
            continue
        gepruefte += 1
        treffer = funde_in(daten)
        if not treffer:
            continue
        if erlaubt:
            hinweise.append(
                f"  Hinweis: {_anzeige(pfad)} traegt {len(treffer)} "
                f"Steuerzeichen — per .gitattributes erlaubt ({ATTRIBUT}), "
                f"kein Fund.")
            continue
        betroffene.add(pfad)
        for zeile, pos in treffer:
            funde.append(f"{_anzeige(pfad)}:{zeile}: {beschreibung(daten[pos])}"
                         f" — {umfeld(daten, pos)}")
    return funde, betroffene, hinweise, gepruefte


# --- Aufruf --------------------------------------------------------------------

def _lies_argumente(argv):
    """(modus, wert, dateien) — modus ist geaendert, seit, versioniert oder
    dateien."""
    modus, wert, dateien = None, None, []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--hilfe", "--help", "-h"):
            return "hilfe", None, []
        if arg == "--seit":
            if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                raise Bedienfehler("--seit braucht einen Stand: --seit <commit>")
            if modus:
                raise Bedienfehler(f"--seit und --{modus} schliessen sich aus")
            modus, wert = "seit", argv[i + 1]
            i += 2
            continue
        if arg == "--versioniert":
            if modus:
                raise Bedienfehler(f"--versioniert und --{modus} schliessen "
                                   f"sich aus")
            modus = "versioniert"
            i += 1
            continue
        if arg.startswith("-"):
            raise Bedienfehler(f"unbekannter Schalter '{arg}'")
        dateien.append(arg)
        i += 1
    if modus and dateien:
        raise Bedienfehler(f"--{modus} und benannte Dateien schliessen sich aus")
    if dateien:
        return "dateien", None, dateien
    return modus or "geaendert", wert, []


def pruefen(argv, cwd=None):
    cwd = Path(cwd or Path.cwd())
    modus, wert, dateien = _lies_argumente(argv)
    if modus == "hilfe":
        print(__doc__)
        return 0
    if modus == "dateien":
        eintraege = aus_dem_arbeitsbaum(cwd, dateien)
        attr = attribute(cwd, dateien)
        was = f"{len(dateien)} benannte Datei(en)"
    else:
        wurzel = _wurzel(cwd)
        if modus == "seit":
            pfade = dateien_seit(wurzel, wert)
            eintraege = aus_dem_commit(wurzel, pfade)
            was = f"die Dateien der Commits {wert[:12]}..HEAD"
        elif modus == "versioniert":
            pfade = versionierte_dateien(wurzel)
            eintraege = aus_dem_arbeitsbaum(wurzel, pfade)
            was = "die versionierten Dateien"
        else:
            pfade = geaenderte_dateien(wurzel)
            eintraege = aus_dem_arbeitsbaum(wurzel, pfade)
            was = "die geaenderten Dateien"
        attr = attribute(wurzel, pfade)
    funde, betroffene, hinweise, gepruefte = pruefe(eintraege, attr)
    for zeile in funde:
        print(zeile)
    for zeile in hinweise:
        print(zeile)
    if funde:
        print(f"✗ {len(funde)} Steuerzeichen in {len(betroffene)} Datei(en) — "
              f"geprueft: {was} (Kit-BL-327).")
        print(NACHSATZ)
        return 3
    print(f"✓ Keine Steuerzeichen — geprueft: {was}, {gepruefte} Textdatei(en)"
          f" (Kit-BL-327).")
    return 0


def main(argv):
    if not argv or argv[0] in ("--hilfe", "--help", "-h"):
        if argv:
            print(__doc__)
            return 0
        print("Aufruf: steuerzeichen.py pruefen [--seit REV | --versioniert | "
              "DATEI...]   (--hilfe zeigt die Beschreibung)", file=sys.stderr)
        return 2
    if argv[0] != "pruefen":
        print(f"steuerzeichen.py: unbekanntes Verb '{argv[0]}' — bekannt ist "
              f"nur 'pruefen'. '--hilfe' zeigt die Beschreibung.",
              file=sys.stderr)
        return 2
    try:
        return pruefen(argv[1:])
    except Bedienfehler as fehler:
        print(f"steuerzeichen.py: {fehler}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

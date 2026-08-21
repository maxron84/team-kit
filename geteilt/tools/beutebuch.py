#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteilter Zustandscode, bewusst nicht portiert)
"""Beutebuch-Zustandsmaschine für die T.E.A.M.-Vollautomatik.

Parst und setzt die `- **Status**:`-Zeilen der `### HM-<Nr>`-Blöcke in
plans/beutebuch.md. Der Vorlagen-Block (## Vorlage) wird ignoriert.
Abgeschlossene Funde können nach plans/beutebuch-archiv.md rotiert werden
(Kaskade 22/Stufe 91) — beide Dateien zusammen bilden den vollständigen
HM-Nummernraum.

Aufrufe:
  beutebuch.py list [--alle]        → "HM-1<TAB>an Frank übergeben" je Zeile
                                       (--alle bezieht das Archiv mit ein)
  beutebuch.py first <status>       → erste HM-Nr mit diesem Status (Exit 1 = keiner)
  beutebuch.py set <HM-Nr> <status> → Status-Zeile des Blocks ersetzen
  beutebuch.py count                → "an Frank übergeben<TAB>2" je Status
  beutebuch.py next-id              → nächste freie HM-Nr, Maximum über
                                       aktivem Buch UND Archiv (z. B. "HM-3")
  beutebuch.py dateien <HM-Nr> [--alle]
                                     → per Backtick referenzierte Dateipfade
                                       aus dem Block dieses Funds, eine je Zeile
                                       (Substanz-Anker für Frank, siehe HM-29);
                                       --alle sucht bei Nicht-Fund auch im Archiv
  beutebuch.py reproducer <HM-Nr> [--alle]
                                     → Pfad aus der Reproducer-Test-Zeile
  beutebuch.py lint <HM-Nr>         → prueft den Fundblock auf das, was die
                                       Fixphase gleich auswertet: Statuszeile
                                       parsbar UND ein Wert der Status-Kette,
                                       Dateipfad in Backticks, Reproducer-Zeile
                                       (Exit 3 = Maengel, auf stderr)
  beutebuch.py archiviere [--dry-run]
                                     → verschiebt jeden Block mit Status
                                       'erledigt'/'überholt' wörtlich ans Ende
                                       von plans/beutebuch-archiv.md;
                                       --dry-run gibt nur die betroffenen
                                       Nummern aus, ändert keine Datei

`first`/`count`/`set` arbeiten unverändert nur auf dem aktiven Buch (dort
stehen die Fälle, die noch Arbeit bedeuten).

Optionale globale Flags (vor allem für Fixture-Tests, ersetzen die
Standardpfade auf die echten Dateien):
  --pfad DATEI          aktives Buch statt plans/beutebuch.md
  --archiv-pfad DATEI   Archiv statt plans/beutebuch-archiv.md

Status-Vergleich bei first/count/archiviere: exakter Vergleich, außer der
gespeicherte Status beginnt mit dem gesuchten (deckt 'erledigt (Frank-Fix,
abc123)' ab).
"""
import re
import sys
from pathlib import Path

# BL-133: Die AUSGABE dieses Werkzeugs ist UTF-8 — unabhaengig von der Locale
# des Wirts.
#
# Gelesen und geschrieben wird hier ueberall mit ausdruecklichem
# `encoding="utf-8"` (BL-113, BL-129). Fuer stdout/stderr galt weiter Pythons
# Default, und der ist unter Windows die ANSI-Codepage der Maschine — auf einem
# deutschen System cp1252. Ein "an Frank uebergeben" verliess das Werkzeug
# damit als cp1252-Bytes; jeder Aufrufer im Kit liest UTF-8 und bekam an der
# Stelle des Umlauts ein Ersatzzeichen. Der Vergleich mit dem Statuswert aus
# dem Beutebuch schlug dann fehl, und `frank.sh` meldete "Kein Fund mit Status
# 'an Frank uebergeben'" — vor einem Beutebuch, in dem genau der stand.
#
# Warum hier und nicht per PYTHONIOENCODING: Das muesste jeder Aufrufer setzen
# (lib.sh, lib.psm1, die Entrypoints, der Harnisch, der Mensch auf der
# Kommandozeile). Eine Zusicherung, die an fuenf Stellen wiederholt werden
# muss, ist eine, die eine Stelle vergisst.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        # Ein umgelenkter Strom (pytest-capture) ist kein TextIOWrapper. Er
        # ist dann auch nicht das Problem, gegen das dieser Block steht.
        pass

# Diese Datei liegt in team/tools/ — zwei Ebenen unter der Projektwurzel.
# Ein .parent zu wenig ergab team/plans/beutebuch.md, also eine Datei, die es
# nie gibt: das Werkzeug meldete dann still "keine Funde", und die komplette
# Frank-/Axel-Fixphase lief an jedem übergebenen Fund vorbei (BL-1).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BEUTEBUCH = REPO_ROOT / "plans" / "beutebuch.md"
ARCHIV = REPO_ROOT / "plans" / "beutebuch-archiv.md"
HM_RE = re.compile(r"^###\s+(HM-\d+)")
STATUS_RE = re.compile(r"^(-\s+\*\*Status\*\*:\s*)(.+?)\s*$")
# Der optionale `::…`-Teil fängt Pytest-Node-IDs (`datei.py::test_x`,
# `datei.py::test_x[param]`) und wird VERWORFEN — extrahiert wird nur der
# Dateipfad davor. Ohne ihn scheiterte der Match komplett, weil ":" nicht in der
# Zeichenklasse steht und der Regex Backticks an beiden Enden verlangt: eine so
# referenzierte Datei galt still als "nicht referenziert", der Substanz-Anker
# (team_diff_beruehrt_fund) verwarf jeden Fix, der nur sie berührte, und Frank
# lief in einen endlosen Rollback-Zyklus (im Feld BL-6, real 12,00 USD an HM-4).
DATEI_RE = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)(?:::[^`]*)?`")
# Die Pflichtzeile aus BL-15. Sie ist die EINZIGE Zeile im Fundblock, deren
# Zweck die Absicherung ist — deshalb ist ihr Pfad der richtige Anker fuer
# BL-28, waehrend "irgendeine im Block genannte Datei" auch die Produktivdatei
# treffen kann, die der Fix ohnehin anfasst.
REPRODUCER_RE = re.compile(r"^-\s+\*\*Reproducer-Test\*\*:\s*(.+?)\s*$")
# Die Status-Kette aus CLAUDE.md ("Status-Kette (Beutebuch/Backlog)"), also
# genau die Werte, die die Rollen setzen und suchen. Sie steht hier, weil ein
# Wert AUSSERHALB der Kette heute fuer jedes Werkzeug unsichtbar ist: `list`
# zeigt ihn an, `first` findet ihn nicht, die Rolle meldet "nichts zu tun" —
# und der bezahlte Lauf ist verbraucht, ohne dass irgendwo ein Widerspruch
# auftaucht (BL-115, im Feld an HM-106 passiert). `passt()` deckt dabei die
# Zusaetze ab, die Frank anhaengt ("erledigt (Frank-Fix, abc123)").
STATUS_KETTE = (
    "offen",
    "an Frank übergeben",
    "an Axel übergeben",
    "Fix-Plan liegt vor",
    "erledigt",
    "überholt",
    "an Mensch eskaliert",
)
# Nutzungszeile je Kommando mit Pflichtargument (BL-115).
NUTZUNG = {
    "first": "beutebuch.py first <status>",
    "dateien": "beutebuch.py dateien <HM-Nr> [--alle]",
    "reproducer": "beutebuch.py reproducer <HM-Nr> [--alle]",
    "lint": "beutebuch.py lint <HM-Nr>",
    "set": "beutebuch.py set <HM-Nr> <status>",
}


def _lies_zeilen(pfad):
    pfad = Path(pfad)
    if not pfad.is_file():
        return []
    return pfad.read_text(encoding="utf-8").splitlines()


def _schreibe(pfad, inhalt):
    """Schreibt eine Textdatei mit LF — auf JEDER Plattform (BL-137).

    `Path.write_text()` oeffnet im Textmodus mit `newline=None`, und der
    uebersetzt beim Schreiben jedes "\\n" in `os.linesep`, unter Windows also
    in "\\r\\n". Alle Schreibwege hier schreiben die Datei GANZ neu; betroffen
    waeren also nicht die geaenderten Zeilen, sondern alle. Ein einziges
    `beutebuch.py set HM-1 erledigt` haette das gesamte Beutebuch umgeruesst.

    Es ist zeichengleich der Fehler aus BL-129 — dort `os.fdopen(fd, "w")` in
    `kosten.py`. Dieselbe Schicht, dieselbe Vorgabe, dasselbe Byte; damals nur
    an der Stelle behoben, an der der Fund gemacht wurde.

    Anders als bei den Konfigurationen faengt hier nichts auf: Das Beutebuch
    liegt unter dem Plan-Ordner, dessen Name konfigurierbar ist. Das
    `.gitattributes`-Fragment aus BL-136 kann es nicht mit einer festen Regel
    treffen (nachgemessen im Feldprojekt: `attr/` leer) — was hier geschrieben
    wird, wird genau so eingecheckt.

    Beim Lesen gilt weiter `read_text` mit universal newlines. Ein Buch, das
    vor diesem Fix CRLF bekommen hat, wird dadurch beim naechsten Schreiben
    normalisiert statt vererbt.
    """
    pfad = Path(pfad)
    with pfad.open("w", encoding="utf-8", newline="") as fh:
        fh.write(inhalt)


def block_text(hm_soll, pfad=BEUTEBUCH):
    """Liefert den rohen Textblock '### HM-<n> …' bis vor den nächsten
    '### '/'## '-Header, oder None, wenn hm_soll dort nicht existiert."""
    zeilen = _lies_zeilen(pfad)
    start = None
    for i, zeile in enumerate(zeilen):
        m = HM_RE.match(zeile)
        if m and m.group(1) == hm_soll:
            start = i
            break
    if start is None:
        return None
    ende = len(zeilen)
    for j in range(start + 1, len(zeilen)):
        if zeilen[j].startswith("### ") or zeilen[j].startswith("## "):
            ende = j
            break
    return "\n".join(zeilen[start:ende])


def parse(pfad=BEUTEBUCH):
    """Liefert Liste (hm_id, status, status_zeilennr); Vorlagen-Block zählt nicht."""
    eintraege = []
    current, in_vorlage = None, False
    for nr, zeile in enumerate(_lies_zeilen(pfad)):
        if zeile.startswith("## "):
            in_vorlage = zeile.strip().lower().startswith("## vorlage")
            current = None
            continue
        if in_vorlage:
            continue
        m = HM_RE.match(zeile)
        if m:
            current = m.group(1)
            continue
        s = STATUS_RE.match(zeile)
        if s and current:
            eintraege.append((current, s.group(2), nr))
            current = None
    return eintraege


def passt(gespeichert: str, gesucht: str) -> bool:
    return gespeichert == gesucht or gespeichert.startswith(gesucht)


def _blockbereiche(zeilen):
    """Liefert alle HM-Blöcke einer Zeilenliste als dicts mit hm/status/
    start/ende/core. `ende` ist EXKLUSIV, reicht bis zum nächsten
    '### '/'## '-Header (oder EOF) und schließt die trennende Leerzeile am
    Blockende mit ein -- so kann ein Block per zeilen[start:ende] sauber
    herausgeschnitten werden, ohne Lücken/Doppel-Leerzeilen zu hinterlassen.
    `core` ist derselbe Blockinhalt OHNE die trennenden Leerzeilen davor/
    danach -- das ist der Text, der (byte-gleich) archiviert wird."""
    n = len(zeilen)
    ergebnisse = []
    i = 0
    while i < n:
        m = HM_RE.match(zeilen[i])
        if not m:
            i += 1
            continue
        start = i
        j = i + 1
        while j < n and not (zeilen[j].startswith("### ") or zeilen[j].startswith("## ")):
            j += 1
        core_ende = j
        while core_ende > start + 1 and zeilen[core_ende - 1] == "":
            core_ende -= 1
        status = None
        for zeile in zeilen[start + 1:core_ende]:
            s = STATUS_RE.match(zeile)
            if s:
                status = s.group(2)
                break
        ergebnisse.append({
            "hm": m.group(1),
            "status": status,
            "start": start,
            "ende": j,
            "core": zeilen[start:core_ende],
        })
        i = j
    return ergebnisse


def bloecke(pfad):
    return _blockbereiche(_lies_zeilen(pfad))


def archiviere(aktiv_pfad=BEUTEBUCH, archiv_pfad=ARCHIV, dry_run=False):
    """Verschiebt jeden Block mit Status 'erledigt'/'überholt' wörtlich vom
    aktiven Buch ans Ende des Archivs. Gibt die Liste der verschobenen
    HM-IDs zurück. Ohne Treffer oder im --dry-run bleiben beide Dateien
    unangetastet (Idempotenz/Nebenwirkungsfreiheit)."""
    aktiv_pfad = Path(aktiv_pfad)
    zeilen = _lies_zeilen(aktiv_pfad)
    kandidaten = _blockbereiche(zeilen)
    verschieben = [
        b for b in kandidaten
        if b["status"] and (passt(b["status"], "erledigt") or passt(b["status"], "überholt"))
    ]
    if dry_run or not verschieben:
        return [b["hm"] for b in verschieben]

    entfernen = set()
    for b in verschieben:
        entfernen.update(range(b["start"], b["ende"]))
    neue_aktiv_zeilen = [z for i, z in enumerate(zeilen) if i not in entfernen]
    _schreibe(aktiv_pfad, "\n".join(neue_aktiv_zeilen) + "\n")

    archiv_pfad = Path(archiv_pfad)
    bestehend = archiv_pfad.read_text(encoding="utf-8").rstrip("\n") if archiv_pfad.is_file() else ""
    neue_bloecke = "\n\n".join("\n".join(b["core"]) for b in verschieben)
    inhalt = f"{bestehend}\n\n{neue_bloecke}\n" if bestehend else f"{neue_bloecke}\n"
    _schreibe(archiv_pfad, inhalt)

    return [b["hm"] for b in verschieben]


def _next_id(aktiv_pfad, archiv_pfad):
    nummern = [int(hm.split("-")[1]) for hm, _, _ in parse(aktiv_pfad)]
    nummern += [int(hm.split("-")[1]) for hm, _, _ in parse(archiv_pfad)]
    return f"HM-{max(nummern, default=0) + 1}"


def reproducer_pfad(text):
    """Pfad aus der `- **Reproducer-Test**:`-Zeile eines Fundblocks, oder None.

    Der Pfad MUSS in Backticks stehen (BL-15) — eine Zeile ohne Backticks ist
    fuer jedes Werkzeug unlesbar und gilt deshalb als nicht gesetzt."""
    for zeile in text.splitlines():
        m = REPRODUCER_RE.match(zeile)
        if not m:
            continue
        treffer = DATEI_RE.findall(m.group(1))
        return treffer[0] if treffer else None
    return None


def lint(hm_soll, pfad=BEUTEBUCH):
    """Prueft EINEN Fundblock auf genau das, was die Fixphase gleich auswerten
    wird. Liefert eine Liste von Maengeln (leer = brauchbar) oder None, wenn
    es den Fund nicht gibt.

    BL-29: Im Feld nannte ein Fundblock die Fundstelle als `pfad::testname` in
    Backticks. Der Substanz-Anker erkannte sie nicht als Datei, Franks
    inhaltlich KORREKTER Fix scheiterte am Anker und wurde zurueckgesetzt —
    der Fehlversuchszaehler stand danach auf 1, ohne dass Frank einen Fehler
    gemacht hatte. Kostenpunkt: ein vollstaendiger Frank-Lauf.

    Der gemeinsame Nenner mit BL-11 und BL-15: Der Fundblock ist ein
    MASCHINENLESBARES Dokument, wird aber von Harry, Marv und dem Architekten
    wie Prosa geschrieben — und niemand prueft ihn, bevor er Geld kostet.
    Prueflinge sind deshalb genau die drei Groessen, an denen die Fixphase
    entscheidet: Statuszeile parsbar, mindestens ein Dateipfad extrahierbar,
    Reproducer-Zeile vorhanden und in Backticks.

    Die Kostenlogik ist dieselbe wie bei BL-23: Pruefungen, die VOR dem
    bezahlten Aufruf laufen, sind die einzigen, die den Aufruf noch sparen
    koennen."""
    text = block_text(hm_soll, pfad)
    if text is None:
        return None
    maengel = []
    status_treffer = [STATUS_RE.match(z) for z in text.splitlines()]
    status_treffer = [m for m in status_treffer if m]
    if not status_treffer:
        maengel.append(
            "keine parsbare `- **Status**:`-Zeile — die Fixphase findet den "
            "Fund nicht und kann seinen Status nicht fortschreiben.")
    else:
        wert = status_treffer[0].group(2)
        if not status_bekannt(wert):
            maengel.append(
                f"die Statuszeile traegt '{wert}' — das ist kein Wert der "
                f"Status-Kette ({', '.join(STATUS_KETTE)}). `first` findet den "
                f"Fund damit nicht, die Rolle meldet 'nichts zu tun', und der "
                f"Lauf ist verbraucht. Haeufigster Fall: der UEBERGANG statt "
                f"des Zielwerts eingetragen ('offen → an Frank übergeben' "
                f"statt 'an Frank übergeben').")
    if not DATEI_RE.findall(text):
        maengel.append(
            "kein Dateipfad in Backticks — der Substanz-Anker "
            "(team_diff_beruehrt_fund) kann keinen Fix als zum Fund gehoerig "
            "erkennen und wuerde JEDEN Fix zuruecknehmen.")
    zeilen = [z for z in text.splitlines() if REPRODUCER_RE.match(z)]
    if not zeilen:
        maengel.append(
            "keine `- **Reproducer-Test**:`-Zeile (Pflicht seit BL-15) — ohne "
            "sie kennt niemand den Namen, unter dem die Absicherung entstehen "
            "soll.")
    elif not reproducer_pfad(text):
        maengel.append(
            "die `- **Reproducer-Test**:`-Zeile nennt keinen Pfad in "
            "Backticks — fuer ein Werkzeug ist sie damit leer.")
    return maengel


def status_bekannt(wert: str) -> bool:
    """Ist `wert` ein Wert der Status-Kette (mit erlaubtem Klammerzusatz)?

    Bewusst STRENGER als `passt()`. `passt()` vergleicht mit `startswith`, und
    genau daran waere die Pruefung vorbeigelaufen, fuer die sie gebaut ist:
    'offen → an Frank übergeben' BEGINNT mit 'offen' und saehe damit gueltig
    aus — waehrend `first 'an Frank übergeben'` den Fund nicht findet, was der
    ganze Punkt von BL-115 ist. Erlaubt ist deshalb nur der blanke Wert oder
    der Wert plus Klammerzusatz, wie Frank ihn schreibt:
    'erledigt (Frank-Fix, abc1234)'."""
    return any(wert == bekannt or wert.startswith(bekannt + " (")
               for bekannt in STATUS_KETTE)


def _arg(rest, idx, cmd):
    """Pflichtargument holen — oder Nutzungshinweis und Exit 2.

    BL-115(b): `beutebuch.py first` ohne Argument endete in `rest[0]`, also in
    einem IndexError-Traceback. Der Aufruf steht ausgerechnet am Anfang der
    Gegenprobe "ist mein Fund ueberhaupt auffindbar?" — dort sieht ein
    Traceback wie ein kaputtes Werkzeug aus, waehrend nur ein Argument fehlt.
    Exit 2 ist derselbe Code, den `_pop_flag` und das unbekannte Kommando
    schon fuer Bedienfehler benutzen."""
    if idx < len(rest):
        return rest[idx]
    print(f"FEHLER: Aufruf unvollstaendig. Nutzung: {NUTZUNG[cmd]}", file=sys.stderr)
    if cmd in ("first", "set"):
        print("  Statuswerte der Kette: " + ", ".join(STATUS_KETTE), file=sys.stderr)
    sys.exit(2)


def _pop_flag(argv, name):
    if name in argv:
        idx = argv.index(name)
        if idx + 1 >= len(argv):
            print(f"FEHLER: {name} braucht einen Wert.", file=sys.stderr)
            sys.exit(2)
        wert = argv[idx + 1]
        del argv[idx:idx + 2]
        return wert
    return None


def main() -> int:
    argv = sys.argv[1:]
    aktiv_pfad = _pop_flag(argv, "--pfad") or BEUTEBUCH
    archiv_pfad = _pop_flag(argv, "--archiv-pfad") or ARCHIV
    cmd = argv[0] if argv else "list"
    rest = argv[1:]

    if cmd == "list":
        eintraege = parse(aktiv_pfad)
        if "--alle" in rest:
            eintraege = eintraege + parse(archiv_pfad)
        for hm, status, _ in eintraege:
            print(f"{hm}\t{status}")
        return 0

    if cmd == "first":
        gesucht = _arg(rest, 0, "first")
        for hm, status, _ in parse(aktiv_pfad):
            if passt(status, gesucht):
                print(hm)
                return 0
        return 1

    if cmd == "count":
        zaehler = {}
        for _, status, _ in parse(aktiv_pfad):
            zaehler[status] = zaehler.get(status, 0) + 1
        for status, n in sorted(zaehler.items()):
            print(f"{status}\t{n}")
        return 0

    if cmd == "next-id":
        print(_next_id(aktiv_pfad, archiv_pfad))
        return 0

    if cmd == "dateien":
        hm_soll = _arg(rest, 0, "dateien")
        alle = "--alle" in rest
        text = block_text(hm_soll, aktiv_pfad)
        if text is None and alle:
            text = block_text(hm_soll, archiv_pfad)
        if text is None:
            print(f"FEHLER: {hm_soll} nicht im Beutebuch gefunden.", file=sys.stderr)
            return 1
        for pfad in sorted(set(DATEI_RE.findall(text))):
            print(pfad)
        return 0

    if cmd == "reproducer":
        # BL-28: Der Pfad aus der Reproducer-Test-Zeile, allein. Exit 1, wenn
        # der Fund fehlt oder die Zeile keinen Pfad in Backticks traegt.
        hm_soll = _arg(rest, 0, "reproducer")
        text = block_text(hm_soll, aktiv_pfad)
        if text is None and "--alle" in rest:
            text = block_text(hm_soll, archiv_pfad)
        if text is None:
            print(f"FEHLER: {hm_soll} nicht im Beutebuch gefunden.", file=sys.stderr)
            return 1
        pfad = reproducer_pfad(text)
        if not pfad:
            return 1
        print(pfad)
        return 0

    if cmd == "lint":
        # BL-29: Was die Fixphase gleich auswerten wird, wird VOR dem ersten
        # bezahlten Frank-Aufruf geprueft.
        hm_soll = _arg(rest, 0, "lint")
        maengel = lint(hm_soll, aktiv_pfad)
        if maengel is None:
            print(f"FEHLER: {hm_soll} nicht im Beutebuch gefunden.", file=sys.stderr)
            return 1
        for mangel in maengel:
            print(f"[{hm_soll}] {mangel}", file=sys.stderr)
        return 3 if maengel else 0

    if cmd == "archiviere":
        dry_run = "--dry-run" in rest
        verschoben = archiviere(aktiv_pfad, archiv_pfad, dry_run=dry_run)
        for hm in verschoben:
            print(hm)
        return 0

    if cmd == "set":
        hm_soll, status_neu = _arg(rest, 0, "set"), _arg(rest, 1, "set")
        for hm, _, zeilennr in parse(aktiv_pfad):
            if hm == hm_soll:
                aktiv_pfad = Path(aktiv_pfad)
                zeilen = aktiv_pfad.read_text(encoding="utf-8").splitlines(keepends=True)
                # Zeilenende bewahren: STATUS_RE endet auf \s*$ und würde sonst
                # das \n mitfressen (HM-Fund beim 1. Feldlauf 2026-07-10).
                alt = zeilen[zeilennr]
                ende = "\n" if alt.endswith("\n") else ""
                zeilen[zeilennr] = STATUS_RE.sub(rf"\g<1>{status_neu}", alt.rstrip("\n")) + ende
                _schreibe(aktiv_pfad, "".join(zeilen))
                return 0
        print(f"FEHLER: {hm_soll} nicht im Beutebuch gefunden.", file=sys.stderr)
        return 1

    print(f"FEHLER: unbekanntes Kommando '{cmd}'.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

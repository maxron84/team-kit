#!/usr/bin/env python3
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

# Diese Datei liegt in team/tools/ — zwei Ebenen unter der Projektwurzel.
# Ein .parent zu wenig ergab team/plans/beutebuch.md, also eine Datei, die es
# nie gibt: das Werkzeug meldete dann still "keine Funde", und die komplette
# Frank-/Axel-Fixphase lief an jedem uebergebenen Fund vorbei (BL-1, im Feld
# erlebt am 2026-08-01 in team-kit_project_platformer, Kaskade 1).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BEUTEBUCH = REPO_ROOT / "plans" / "beutebuch.md"
ARCHIV = REPO_ROOT / "plans" / "beutebuch-archiv.md"
HM_RE = re.compile(r"^###\s+(HM-\d+)")
STATUS_RE = re.compile(r"^(-\s+\*\*Status\*\*:\s*)(.+?)\s*$")
DATEI_RE = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")


def _lies_zeilen(pfad):
    pfad = Path(pfad)
    if not pfad.is_file():
        return []
    return pfad.read_text(encoding="utf-8").splitlines()


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
    aktiv_pfad.write_text("\n".join(neue_aktiv_zeilen) + "\n", encoding="utf-8")

    archiv_pfad = Path(archiv_pfad)
    bestehend = archiv_pfad.read_text(encoding="utf-8").rstrip("\n") if archiv_pfad.is_file() else ""
    neue_bloecke = "\n\n".join("\n".join(b["core"]) for b in verschieben)
    inhalt = f"{bestehend}\n\n{neue_bloecke}\n" if bestehend else f"{neue_bloecke}\n"
    archiv_pfad.write_text(inhalt, encoding="utf-8")

    return [b["hm"] for b in verschieben]


def _next_id(aktiv_pfad, archiv_pfad):
    nummern = [int(hm.split("-")[1]) for hm, _, _ in parse(aktiv_pfad)]
    nummern += [int(hm.split("-")[1]) for hm, _, _ in parse(archiv_pfad)]
    return f"HM-{max(nummern, default=0) + 1}"


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
        gesucht = rest[0]
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
        hm_soll = rest[0]
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

    if cmd == "archiviere":
        dry_run = "--dry-run" in rest
        verschoben = archiviere(aktiv_pfad, archiv_pfad, dry_run=dry_run)
        for hm in verschoben:
            print(hm)
        return 0

    if cmd == "set":
        hm_soll, status_neu = rest[0], rest[1]
        for hm, _, zeilennr in parse(aktiv_pfad):
            if hm == hm_soll:
                aktiv_pfad = Path(aktiv_pfad)
                zeilen = aktiv_pfad.read_text(encoding="utf-8").splitlines(keepends=True)
                # Zeilenende bewahren: STATUS_RE endet auf \s*$ und würde sonst
                # das \n mitfressen (HM-Fund beim 1. Feldlauf 2026-07-10).
                alt = zeilen[zeilennr]
                ende = "\n" if alt.endswith("\n") else ""
                zeilen[zeilennr] = STATUS_RE.sub(rf"\g<1>{status_neu}", alt.rstrip("\n")) + ende
                aktiv_pfad.write_text("".join(zeilen), encoding="utf-8")
                return 0
        print(f"FEHLER: {hm_soll} nicht im Beutebuch gefunden.", file=sys.stderr)
        return 1

    print(f"FEHLER: unbekanntes Kommando '{cmd}'.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

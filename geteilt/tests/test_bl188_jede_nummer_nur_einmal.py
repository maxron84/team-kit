#!/usr/bin/env python3
"""BL-188: `BL-144` war DOPPELT vergeben — dieselbe Nummer trug im aktiven
Backlog und im Archiv zwei verschiedene Funde.

WIE ES DAZU KAM
    Am 2026-08-21 vergaben zwei Maschinen dieselbe Nummer: hier die
    Ausfuehrungsrichtlinie per Gruppenrichtlinie (aus `Feld B`), dort der rote
    bash-Selbsttest seit `BL-136`. Beide wurden gepusht, bevor es auffiel — die
    sonst geltende Regel „die ungepushte Seite zieht um" (`41b2ee0`) hatte
    damit keinen Ansatzpunkt mehr.

    Es ist genau der Fehler, vor dem die Doku-Hygiene-Regel „archiv-bewusste
    Nummernvergabe" warnt: Nach einer Rotation vergibt die Zustandsmaschine
    wieder Nummern, die im ARCHIV schon belegt sind — und das Archiv liest
    niemand mit, es wird nachgeschlagen.

WARUM DER SCHADEN SPAET UND LEISE ANFAELLT
    Ein Feldprojekt quittiert seinen lokalen Eintrag mit `Kit-BL-144` und zeigt
    je nach nachgeschlagener Datei auf den falschen Fund. `Feld B` tat das in
    seinem `BL-11`. Nichts bricht, nichts wird rot — die Spur zeigt nur
    woandershin, und das faellt erst auf, wenn jemand ihr folgt.

WARUM DIESE PRUEFUNG EIN TEST IST UND KEIN EINMALIGER BEFEHL
    Der Fund entstand aus einem `grep | sort | uniq -d`, den jemand von Hand
    fuhr, weil die Gegenprobe gegen das Archiv Teil seines VORGEHENS war —
    nicht Teil seines Auftrags. Eine Handpruefung gilt genau einmal (dieselbe
    Lehre wie `BL-7` im Feld). Der naechste Fall dieser Art waere sonst wieder
    nur zufaellig zu finden.

    Geprueft wird die GATTUNG, nicht der bekannte Fall: JEDE Nummer darf im
    Nummernraum des Kits genau einmal vorkommen — auch innerhalb einer Datei.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO_ROOT = Path(__file__).resolve().parents[2]
AKTIV = REPO_ROOT / "plans" / "backlog.md"
ARCHIV = REPO_ROOT / "plans" / "backlog-archiv.md"

# Eine Tabellenzeile beginnt mit `| BL-<n> |`. Prosa, die eine Nummer nur
# NENNT, faengt der Anker bewusst nicht — sonst zaehlte jeder Querverweis mit.
ZEILE = re.compile(r"^\| (BL-\d+) \|", re.MULTILINE)


def _ist_kit():
    """Nur im KIT pruefbar.

    In einer INSTALLIERTEN Ablage ist `plans/backlog.md` der Backlog des
    ZIELPROJEKTS — ein eigener Nummernraum, der mit dem des Kits nichts zu tun
    hat, und ein Archiv gibt es dort gar nicht. Erkannt wird das Kit an
    derselben Marke, die auch `kit_meldung.py` benutzt.
    """
    return (REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage").is_file()


def _nummern(pfad):
    return ZEILE.findall(pfad.read_text(encoding="utf-8"))


def test_keine_nummer_steht_in_beiden_dateien():
    """Der Fund selbst — als Gattung, nicht als Einzelfall.

    Der Befehl, aus dem er entstand:
        grep -hoE "^\\| BL-[0-9]+" plans/backlog.md plans/backlog-archiv.md
        | sort | uniq -d
    """
    if not _ist_kit():
        pytest.skip("kein Kit — `plans/backlog.md` ist hier der Projekt-Backlog "
                    "mit eigenem Nummernraum")
    if not (AKTIV.is_file() and ARCHIV.is_file()):
        pytest.skip("Backlog oder Archiv liegt in dieser Ablage nicht")
    doppelt = sorted(set(_nummern(AKTIV)) & set(_nummern(ARCHIV)),
                     key=lambda n: int(n.split("-")[1]))
    assert not doppelt, (
        "BL-188: Diese Nummern tragen im aktiven Backlog UND im Archiv je "
        "einen anderen Fund:\n  " + "\n  ".join(doppelt)
        + "\nEin Feldprojekt, das eine davon als `Kit-BL-n` quittiert, zeigt "
        "je nach nachgeschlagener Datei auf den falschen Eintrag. Aufloesen "
        "heisst: die Seite mit den WENIGEREN Verweisen bekommt eine frische "
        "Nummer, und der umgezogene Eintrag sagt im Status, wie er vorher "
        "hiess.")


@pytest.mark.parametrize("name", ["aktiv", "archiv"])
def test_keine_nummer_steht_zweimal_in_derselben_datei(name):
    """Die zweite Haelfte derselben Gattung.

    Zwei Zeilen mit derselben Nummer in EINER Datei sind noch leiser als der
    Fall darueber — die zweite steht dann meist weit unten, und wer die erste
    gefunden hat, sucht nicht weiter.
    """
    if not _ist_kit():
        pytest.skip("kein Kit — eigener Nummernraum")
    pfad = AKTIV if name == "aktiv" else ARCHIV
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt in dieser Ablage nicht")
    gesehen, doppelt = set(), []
    for n in _nummern(pfad):
        (doppelt.append(n) if n in gesehen else gesehen.add(n))
    assert not doppelt, (
        f"{pfad.name} fuehrt diese Nummern mehrfach: {sorted(set(doppelt))}")


def test_der_umgezogene_eintrag_sagt_wie_er_vorher_hiess():
    """Ohne diesen Satz ist ein Umzug eine stille Umschreibung der Geschichte.

    Ein Feldprojekt, das `Kit-BL-144` quittiert hat, muss die neue Nummer
    finden koennen, ohne den Commit zu lesen. Dieselbe Disziplin haben die
    Umzuege vom 2026-08-25 (`41b2ee0`, `d05c8d7`) im Kopf des Backlogs.
    """
    if not _ist_kit() or not AKTIV.is_file():
        pytest.skip("kein Kit")
    text = AKTIV.read_text(encoding="utf-8")
    zeile = [z for z in text.split("\n") if z.startswith("| BL-189 |")]
    if not zeile:
        pytest.skip("BL-189 ist nicht mehr offen — der Nachweis liegt im Archiv")
    assert "BL-144" in zeile[0], (
        "BL-189 sagt nicht mehr, dass er bis 2026-08-26 `BL-144` hiess. Wer "
        "einer alten Quittung folgt, landet dann im Nichts.")

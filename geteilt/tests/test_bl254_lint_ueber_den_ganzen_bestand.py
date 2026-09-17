#!/usr/bin/env python3
"""BL-254: Ein Rollen-Anhang kann einen fremden Fundblock zerschneiden, und
kein Guard kann es sehen — dazu erreichte `beutebuch.py lint` das Archiv gar
nicht.

DER FELDBEFUND
    Frank schrieb einen regelkonformen Beifang-Fund MITTEN in den Block seines
    Vorgaengers: zwischen dessen vorletzten Absatz und seine
    `Reproducer-Test`-Zeile. Danach endete der fremde Fund ohne Pflichtzeile,
    der neue trug am Ende eine fremde, KEIN Zeichen ging verloren, und der Diff
    sah aus wie Routine.

    Der Read-Only-Guard kann das PRINZIPIELL nicht sehen. Er urteilt ueber
    Schreibzonen; das Beutebuch ist fuer Frank eine erlaubte Datei, und die
    Lage eines Anhangs ist eine Frage der STRUKTUR, nicht des Pfades. Die
    Folge: Ein Fund ohne `Reproducer-Test`-Zeile bricht den Substanz-Anker, der
    regelkonforme Fix wuerde stillschweigend zurueckgerollt.

WARUM DIE PRUEFUNG SCHON DA WAR UND TROTZDEM NICHTS FAND
    `lint` gab es seit `BL-29`, und es meldet genau diesen Mangel. Es verlangte
    aber eine FUNDNUMMER — also prueft man den Fund, an den man gerade denkt.
    Der zerschnittene ist der andere.

    Nebenbefund, im Feld ueber 141 Funde gemessen: `lint` kannte als einziges
    der lesenden Verben kein `--alle`. 15 offene Funde linteten sauber, 126
    archivierte meldeten `nicht im Beutebuch gefunden` — 89 Prozent des
    Bestands unerreichbar. Und `archiviere` verschiebt Bloecke WOERTLICH, also
    auch einen bereits zerschnittenen.

WAS DIESER TEST PRUEFT
    Den gemeldeten Hergang als Fall: einen Block, der genau so zerschnitten
    ist, wie es im Feld passiert ist — der Vorgaenger ohne Pflichtzeile, der
    Anhang mit einer fremden. Beide Maengel muessen fallen, ohne dass jemand
    eine Nummer nennt. Dazu die Gegenrichtung (ein sauberer Bestand schweigt)
    und die Reichweite (`--alle` erreicht das Archiv).
"""
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if Path(_tools).is_dir():
        sys.path.insert(0, str(_tools))
        break
import beutebuch  # noqa: E402

BEUTEBUCH_PY = kit_pfad("tools", "beutebuch.py")

KOPF = "# Beutebuch\n\n## Funde\n\n"

SAUBER = """### HM-{nr} — Fund {nr}

- **Status**: offen
- **Fundstelle**: `src/modul{nr}.py`
- **Reproducer-Test**: `tests/test_hm{nr}_fund.py`

Ein Absatz Prosa.

"""

# Genau der Hergang aus dem Feld: HM-1 verliert seine Pflichtzeile an HM-2,
# weil HM-2 zwischen Prosa und Pflichtzeile eingefuegt wurde.
ZERSCHNITTEN = """### HM-1 — Der Vorgaenger

- **Status**: offen
- **Fundstelle**: `src/modul1.py`

Ein Absatz Prosa.

### HM-2 — Der Beifang, mitten hineingeschrieben

- **Status**: offen
- **Fundstelle**: `src/modul2.py`
- **Reproducer-Test**: `tests/test_hm1_fund.py`

"""


def _buch(pfad, inhalt):
    pfad.write_text(KOPF + inhalt, encoding="utf-8")
    return pfad


def _cli(*args):
    r = subprocess.run([sys.executable, str(BEUTEBUCH_PY), *args],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout, r.stderr


def test_lint_ohne_nummer_findet_den_zerschnittenen_block(tmp_path):
    """Der Fund selbst — und niemand muss wissen, WELCHER Fund betroffen ist."""
    buch = _buch(tmp_path / "beutebuch.md", ZERSCHNITTEN)
    rc, _, err = _cli("--pfad", str(buch), "lint")
    assert rc == 3, f"der zerschnittene Block bleibt unbemerkt (rc={rc}):\n{err}"
    assert "[HM-1]" in err, (
        "Gemeldet werden muss der Fund, dem die Pflichtzeile ABGESCHNITTEN "
        "wurde — an den denkt gerade niemand (BL-254).")
    assert "Reproducer-Test" in err


def test_lint_ohne_nummer_schweigt_bei_sauberem_bestand(tmp_path):
    """Gegenrichtung: Eine Meldung, die immer kommt, ist keine (BL-14)."""
    buch = _buch(tmp_path / "beutebuch.md",
                 SAUBER.format(nr=1) + SAUBER.format(nr=2))
    rc, _, err = _cli("--pfad", str(buch), "lint")
    assert rc == 0, f"Fehlalarm auf einem sauberen Bestand:\n{err}"
    assert "[HM-" not in err


def test_lint_ohne_nummer_nennt_den_umfang(tmp_path):
    """Sonst ist ein gruener Lauf von 'nichts geprueft' nicht zu unterscheiden
    — dieselbe Falschaussage wie in BL-198."""
    buch = _buch(tmp_path / "beutebuch.md",
                 SAUBER.format(nr=1) + SAUBER.format(nr=2))
    _, _, err = _cli("--pfad", str(buch), "lint")
    assert "2 Fundbloecke" in err, err


def test_lint_alle_erreicht_das_archiv(tmp_path):
    """Der Nebenbefund: 126 von 141 Funden lagen ausserhalb der Reichweite."""
    buch = _buch(tmp_path / "beutebuch.md", SAUBER.format(nr=9))
    archiv = _buch(tmp_path / "archiv.md", ZERSCHNITTEN)
    rc, _, err = _cli("--pfad", str(buch), "--archiv-pfad", str(archiv), "lint")
    assert rc == 0, f"ohne --alle gehoert das Archiv nicht dazu:\n{err}"
    rc, _, err = _cli("--pfad", str(buch), "--archiv-pfad", str(archiv),
                      "lint", "--alle")
    assert rc == 3, f"--alle erreicht das Archiv nicht (rc={rc}):\n{err}"
    assert "[HM-1]" in err


def test_lint_mit_nummer_findet_einen_archivierten_fund(tmp_path):
    """Bis hierher meldete jeder archivierte Fund `nicht im Beutebuch
    gefunden` — 89 Prozent des Bestands."""
    buch = _buch(tmp_path / "beutebuch.md", SAUBER.format(nr=9))
    archiv = _buch(tmp_path / "archiv.md", ZERSCHNITTEN)
    rc, _, err = _cli("--pfad", str(buch), "--archiv-pfad", str(archiv),
                      "lint", "HM-1")
    assert rc == 1 and "nicht im Beutebuch" in err, (
        "ohne --alle bleibt der Archivfund unbekannt — das ist die alte, "
        "gewollte Antwort")
    rc, _, err = _cli("--pfad", str(buch), "--archiv-pfad", str(archiv),
                      "lint", "HM-1", "--alle")
    assert rc == 3, f"--alle findet den archivierten Fund nicht (rc={rc}):\n{err}"
    assert "[HM-1]" in err


def test_lint_mit_nummer_bleibt_wie_es_war(tmp_path):
    """Der bestehende Vertrag aus BL-29/BL-115 wird nicht angefasst."""
    buch = _buch(tmp_path / "beutebuch.md", ZERSCHNITTEN)
    rc, _, err = _cli("--pfad", str(buch), "lint", "HM-2")
    assert rc == 0, f"HM-2 ist fuer sich brauchbar:\n{err}"
    rc, _, err = _cli("--pfad", str(buch), "lint", "HM-7")
    assert rc == 1 and "nicht im Beutebuch" in err


def test_die_doppelte_pflichtzeile_faellt_ebenfalls_auf(tmp_path):
    """Die zweite Haelfte desselben Hergangs (BL-210): Der Anhang traegt eine
    FREMDE Zeile am Ende. Steht sie in SEINEM Block, ist sie dort doppelt."""
    buch = _buch(tmp_path / "beutebuch.md", """### HM-1 — Der Anhang mit zwei Zeilen

- **Status**: offen
- **Fundstelle**: `src/modul1.py`
- **Reproducer-Test**: `tests/test_hm1_fund.py`
- **Reproducer-Test**: `tests/test_hm2_fremd.py`

""")
    rc, _, err = _cli("--pfad", str(buch), "lint")
    assert rc == 3, err
    assert "2 `- **Reproducer-Test**:`-Zeilen" in err, err


def test_lint_alle_liefert_jeden_block_einzeln(tmp_path):
    """Die Programmierschnittstelle, auf der der Lauf steht."""
    buch = _buch(tmp_path / "beutebuch.md", ZERSCHNITTEN)
    ergebnis = beutebuch.lint_alle([buch])
    assert [hm for hm, _ in ergebnis] == ["HM-1", "HM-2"]
    assert ergebnis[0][1], "HM-1 traegt den Mangel"
    assert not ergebnis[1][1], "HM-2 ist fuer sich brauchbar"


def test_ein_leeres_buch_ist_kein_befund(tmp_path):
    """Ein Projekt ohne Funde darf nicht rot werden."""
    buch = _buch(tmp_path / "beutebuch.md", "")
    rc, _, err = _cli("--pfad", str(buch), "lint")
    assert rc == 0, err

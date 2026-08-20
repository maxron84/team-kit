#!/usr/bin/env python3
"""BL-115 — zwei Haelften desselben Fehlers, beide teuer, beide still.

Im Feld (`team-kit_project_platformer`, HM-106, 2026-08-19) entstand die
Statuszeile `- **Status**: offen → an Frank übergeben`, weil die Regeldatei
den UEBERGANG in Feldwert-Schreibweise vorschrieb ("Status auf
`offen → an Frank übergeben` setzen"). Folge: `list` zeigt den Fund weiter an,
`first 'an Frank übergeben'` findet ihn NICHT, frank.sh meldet "nichts zu tun"
— und der bezahlte Lauf ist verbraucht, ohne dass irgendetwas auf den
Widerspruch hinweist. Wer daraufhin von Hand nachsieht, ruft `beutebuch.py
first` und bekam bis hierher einen IndexError-Traceback statt eines
Nutzungshinweises: Das Werkzeug sah kaputt aus, obwohl nur ein Argument
fehlte.

Drei Zusicherungen, eine je Haelfte plus der Waechter, der den Fall ueberhaupt
erst sichtbar macht:

  1. Die Regeldatei lehrt den FELDWERT, nicht den Uebergang.
  2. Pflichtargumente fehlen -> Nutzungszeile und Exit 2, kein Traceback.
  3. `lint` meldet eine Statuszeile, die auf keinen Wert der Kette passt.

Zu (3) die eigentliche Falle, an der eine naive Fassung vorbeilaeuft: Der
Praefix-Vergleich aus `passt()` haelt 'offen → an Frank übergeben' fuer
gueltig, weil der Wert mit 'offen' BEGINNT. Die Gegenprobe unten faehrt
deshalb genau diesen String — ohne sie waere ein `passt()`-basierter Waechter
stumm gruen und der Test wertlos.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

WURZEL = Path(__file__).resolve().parents[2]
TOOL = kit_pfad("tools", "beutebuch.py")

BUCH = """# Beutebuch

## Funde

### HM-1 — Uebergang statt Zielwert eingetragen
- **Angreifer**: Harry
- **Status**: offen → an Frank übergeben
- **Reproducer-Test**: `tests/test_hm1_x.py`
- Betrifft `src/foo.py`

### HM-2 — sauber uebergeben
- **Angreifer**: Marv
- **Status**: an Frank übergeben
- **Reproducer-Test**: `tests/test_hm2_x.py`
- Betrifft `src/bar.py`

### HM-3 — Frank-Quittung mit Zusatz
- **Angreifer**: Harry
- **Status**: erledigt (Frank-Fix, abc1234)
- **Reproducer-Test**: `tests/test_hm3_x.py`
- Betrifft `src/baz.py`
"""


def _modul():
    spec = importlib.util.spec_from_file_location("beutebuch_bl115", TOOL)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _buch(tmp_path):
    pfad = tmp_path / "beutebuch.md"
    pfad.write_text(BUCH, encoding="utf-8")
    return pfad


def _lauf(*args):
    return subprocess.run([sys.executable, str(TOOL), *args],
                          capture_output=True, text=True)


def _quelle(*kandidaten):
    """Kit-Vorlage oder installierte Zieldatei — je nachdem, wo wir laufen."""
    for kandidat in kandidaten:
        pfad = WURZEL / kandidat
        if pfad.is_file():
            return pfad
    raise AssertionError(f"keine der Quellen existiert: {kandidaten}")


# ---------------------------------------------------------------- (1) Vorlage
def test_regeldatei_lehrt_den_feldwert_statt_des_uebergangs():
    text = _quelle("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md").read_text(encoding="utf-8")
    assert "Status auf `offen → an Frank übergeben` setzen" not in text, (
        "Die Regeldatei schreibt den UEBERGANG in Feldwert-Schreibweise vor — "
        "genau daraus entstand HM-106."
    )
    assert "Status von `offen` auf `an Frank übergeben` setzen" in text, (
        "Die Regeldatei nennt den Zielwert nicht als Zielwert."
    )
    assert "beutebuch.py set" in text, (
        "Die Regeldatei nennt den Weg nicht, der den Feldwert von selbst "
        "richtig schreibt."
    )


def test_die_status_kette_bleibt_als_kette_lesbar():
    """Gegenprobe zu (1): Der Pfeil ist an SEINER Stelle richtig.

    Ohne diese Probe waere "alle Pfeile entfernen" ein gruener Weg — und die
    Kette, die den Ablauf beschreibt, waere zerstoert."""
    text = _quelle("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md").read_text(encoding="utf-8")
    assert "offen → an Frank übergeben → an Axel übergeben" in text, (
        "Die Status-Kette selbst fehlt — sie beschreibt den Ablauf und bleibt."
    )


# ------------------------------------------------- (2) Nutzungshinweis statt Traceback
@pytest.mark.parametrize("argv,erwartet", [
    (["first"], "beutebuch.py first <status>"),
    (["dateien"], "beutebuch.py dateien <HM-Nr>"),
    (["reproducer"], "beutebuch.py reproducer <HM-Nr>"),
    (["lint"], "beutebuch.py lint <HM-Nr>"),
    (["set"], "beutebuch.py set <HM-Nr> <status>"),
    (["set", "HM-1"], "beutebuch.py set <HM-Nr> <status>"),
])
def test_fehlendes_pflichtargument_gibt_nutzungszeile_und_exit_2(argv, erwartet):
    ergebnis = _lauf(*argv)
    assert ergebnis.returncode == 2, (
        f"'{' '.join(argv)}' endet mit {ergebnis.returncode} statt 2 "
        f"(Bedienfehler)"
    )
    assert "Traceback" not in ergebnis.stderr, (
        f"'{' '.join(argv)}' wirft weiterhin einen Traceback:\n{ergebnis.stderr}"
    )
    assert erwartet in ergebnis.stderr, (
        f"'{' '.join(argv)}' nennt seine Nutzung nicht:\n{ergebnis.stderr}"
    )


def test_first_nennt_die_bekannten_statuswerte():
    """Wer `first` ohne Argument ruft, sucht meist genau diese Liste."""
    ergebnis = _lauf("first")
    assert "an Frank übergeben" in ergebnis.stderr
    assert "Fix-Plan liegt vor" in ergebnis.stderr


# --------------------------------------------------------- (3) lint als Waechter
def test_lint_meldet_eine_statuszeile_ausserhalb_der_kette(tmp_path):
    pfad = _buch(tmp_path)
    ergebnis = _lauf("--pfad", str(pfad), "lint", "HM-1")
    assert ergebnis.returncode == 3, (
        f"lint meldet den Uebergangs-Status nicht (rc={ergebnis.returncode}) — "
        f"damit bleibt der Fall genauso unsichtbar wie vorher.\n{ergebnis.stderr}"
    )
    assert "Status-Kette" in ergebnis.stderr
    assert "an Frank übergeben" in ergebnis.stderr, (
        "Die Meldung nennt den richtigen Wert nicht — sie sagt dann, dass "
        "etwas falsch ist, aber nicht, was stattdessen gehoert."
    )


@pytest.mark.parametrize("hm", ["HM-2", "HM-3"])
def test_lint_bleibt_bei_gueltigen_statuswerten_still(tmp_path, hm):
    """HM-3 ist die teure Haelfte dieser Probe: 'erledigt (Frank-Fix, abc1234)'
    ist ein Kettenwert MIT Zusatz. Eine zu strenge Pruefung wuerde jede
    Frank-Quittung anmahnen — eine Dauerwarnung, die zum Wegsehen erzieht."""
    pfad = _buch(tmp_path)
    ergebnis = _lauf("--pfad", str(pfad), "lint", hm)
    assert ergebnis.returncode == 0, (
        f"lint meldet {hm} zu Unrecht:\n{ergebnis.stderr}"
    )


def test_praefix_vergleich_allein_wuerde_den_fall_durchlassen():
    """Die Gegenprobe, ohne die der Waechter stumm gruen sein koennte.

    `passt()` haelt 'offen → an Frank übergeben' fuer gueltig (Praefix
    'offen'). Genau deshalb prueft `lint` mit `status_bekannt()`."""
    modul = _modul()
    kaputt = "offen → an Frank übergeben"
    assert modul.passt(kaputt, "offen"), (
        "Voraussetzung entfallen: passt() vergleicht nicht mehr per Praefix — "
        "dann darf auch die Begruendung von status_bekannt() nachgezogen werden."
    )
    assert not modul.status_bekannt(kaputt), (
        "status_bekannt() uebernimmt die Praefix-Schwaeche von passt() — der "
        "Waechter waere damit blind fuer genau seinen Anlassfall."
    )
    assert modul.status_bekannt("erledigt (Frank-Fix, abc1234)")
    assert modul.status_bekannt("an Frank übergeben")


def test_first_findet_den_kaputten_status_wirklich_nicht(tmp_path):
    """Der Schaden selbst, damit er nicht zur Behauptung verkommt."""
    pfad = _buch(tmp_path)
    ergebnis = _lauf("--pfad", str(pfad), "first", "an Frank übergeben")
    assert ergebnis.stdout.strip() == "HM-2", (
        "Erwartet war HM-2 — HM-1 traegt den Uebergang und ist fuer `first` "
        f"unsichtbar. Ausgabe: {ergebnis.stdout!r}"
    )

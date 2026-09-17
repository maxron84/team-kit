#!/usr/bin/env python3
"""BL-253: Der Hilfetext von `kosten.py` nannte 3 von 10 Verben — und die
sieben verschwiegenen waren genau die BUCHENDEN.

DER FELDBEFUND
    Der Aufruf ohne Argumente antwortete
    `Nutzung: kosten.py summe [--split] DIR...` plus `ledger` und
    `ledger-pruefen`. Der Dispatch kannte ausserdem `turns`, `sitzung-messen`,
    `architekt-schaetzung`, `architekt-abschluss`, `akteur-abschluss`,
    `rollen-abschluss` und `ralph-abschluss`.

    Die Auswahl war die denkbar unguenstigste: Die drei genannten sind
    ABFRAGEN, die sieben fehlenden enthalten jedes Verb, das ein Closeout
    braucht. Die einzige andere Quelle dafuer sind die Rollen-Briefings — wer
    ohne geladenes Briefing arbeitet, findet den Kostenabschluss nicht und
    haelt ihn fuer nicht vorhanden.

WARUM DAS EIN MUSTER IST UND KEIN EINZELFALL
    `BL-227` war derselbe Fehler eine Datei weiter: `kit-melden` kannte sein
    eigenes `ablegen` nicht. Ein Verb wird ergaenzt, die Nutzungszeile nicht.
    Der Unterschied zwischen den beiden Werkzeugen ist zugleich der Fix:
    `kit_meldung.py` benutzt `argparse` mit Unterbefehlen und KANN seinen
    Hilfetext nicht veralten lassen; `kosten.py` verzweigt ueber eine
    `if befehl ==`-Kette und schrieb die Nutzungszeile als Zeichenkette
    daneben. Zwei Listen, die niemand gegeneinander haelt, driften.

WAS DIESER TEST PRUEFT — GATTUNG, NICHT DIE HEUTIGEN ZEHN NAMEN
    Ein Test, der die zehn Namen aufzaehlt, bleibt beim elften wieder gruen.
    Geprueft wird deshalb in beide Richtungen gegen die QUELLE:

      * Jedes Verb, auf das der Dispatch verzweigt, steht in `VERBEN`.
      * Jedes Verb aus `VERBEN` hat einen Zweig (sonst ist es angekuendigt und
        nicht gebaut).
      * Die gedruckte Nutzungszeile nennt jedes Verb.
      * Der Kopfkommentar der Datei — die Hilfe, die ein Mensch zuerst liest
        — nennt ebenfalls jedes Verb.
      * Ein unbekanntes Verb endet laut, nicht still.
"""
import re
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
import kosten  # noqa: E402

KOSTEN_PY = Path(kit_pfad("tools", "kosten.py"))

# Beide Bauformen des Dispatch: `if befehl == "x"` und `if befehl in ("x", "y")`.
EINZELN = re.compile(r'^\s{4}if befehl == "([a-z][a-z-]*)"', re.M)
MEHRERE = re.compile(r'^\s{4}if befehl in \(([^)]*)\)', re.M)


def _quelle():
    if not KOSTEN_PY.is_file():
        pytest.skip("kosten.py liegt in dieser Ablage nicht")
    return KOSTEN_PY.read_text(encoding="utf-8")


def _verben_des_dispatch():
    """Die Verben, auf die `_main` wirklich verzweigt — die Quelle der Wahrheit
    ist das VERHALTEN, nicht die Liste."""
    text = _quelle()
    verben = set(EINZELN.findall(text))
    for gruppe in MEHRERE.findall(text):
        verben |= set(re.findall(r'"([a-z][a-z-]*)"', gruppe))
    assert verben, "kein Dispatch-Zweig in kosten.py gefunden — Muster veraltet?"
    return verben


def _nutzungszeile():
    r = subprocess.run([sys.executable, str(KOSTEN_PY)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout + r.stderr


def test_nutzungszeile_nennt_jedes_verb_des_dispatch():
    """Der Fund selbst: sieben Verben waren unterhalb der Hilfe erreichbar."""
    _, text = _nutzungszeile()
    fehlend = sorted(v for v in _verben_des_dispatch()
                     if not re.search(rf"kosten\.py {re.escape(v)}\b", text))
    assert not fehlend, (
        f"Die Nutzungszeile verschweigt {fehlend}. Wer ohne geladenes Briefing "
        "arbeitet, findet diese Verben nicht und haelt sie fuer nicht "
        "vorhanden (BL-253).")


def test_verben_tabelle_deckt_sich_mit_dem_dispatch():
    """Beide Richtungen. Ein Verb ohne Zweig ist angekuendigt und nicht gebaut,
    ein Zweig ohne Eintrag ist seit dem Riegel gar nicht erreichbar."""
    dispatch = _verben_des_dispatch()
    tabelle = set(kosten.VERBEN)
    assert dispatch - tabelle == set(), (
        f"Dispatch kennt {sorted(dispatch - tabelle)}, VERBEN nicht — dieses "
        "Verb ist seit dem Riegel aus BL-253 UNERREICHBAR.")
    assert tabelle - dispatch == set(), (
        f"VERBEN kuendigt {sorted(tabelle - dispatch)} an, es gibt aber keinen "
        "Zweig dafuer.")


def test_die_buchenden_verben_stehen_benannt_da():
    """Der Fund ist nicht, dass Verben fehlten, sondern dass ausgerechnet die
    buchenden fehlten — also werden sie als solche ausgewiesen."""
    _, text = _nutzungszeile()
    assert "Bucht in den Ledger" in text, (
        "Die Nutzungszeile trennt Abfrage und Buchung nicht — genau diese "
        "Unterscheidung war im Feld der Unterschied zwischen 'gefunden' und "
        "'fuer nicht vorhanden gehalten' (BL-253).")
    for verb in kosten.BUCHENDE_VERBEN:
        assert verb in kosten.VERBEN, f"{verb} ist kein Verb dieses Werkzeugs"


def test_kopfkommentar_nennt_jedes_verb():
    """Die zweite Hilfe derselben Datei. Sie veraltet genauso still — im
    Ausgangszustand fehlten dort `turns`, `ledger-pruefen` und
    `sitzung-messen`."""
    kopf = _quelle().split('"""', 2)[1]
    fehlend = sorted(v for v in _verben_des_dispatch()
                     if not re.search(rf"kosten\.py {re.escape(v)}\b", kopf))
    assert not fehlend, (
        f"Der Kopfkommentar von kosten.py verschweigt {fehlend} (BL-253).")


def test_ohne_argumente_endet_rot_und_mit_der_liste():
    rc, text = _nutzungszeile()
    assert rc == 1, f"ein Aufruf ohne Verb muss rot enden, nicht {rc}"
    assert "Nutzung:" in text


def test_unbekanntes_verb_endet_laut():
    """Gegenrichtung: Der Riegel darf nicht schweigen, sonst waere ein Tippfehler
    ein stiller Erfolg."""
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "kein-solches-verb"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode != 0
    assert "Unbekannter Befehl" in r.stderr
    assert "Nutzung:" in r.stderr, (
        "Wer sich vertippt, bekommt die Liste — sonst raet er ein zweites Mal.")

#!/usr/bin/env python3
"""BL-267: Eine abgelegte Meldung bekommt ihre `BL-n` von Hand — und nichts
vergleicht die beiden Mengen.

WAS ZWEIMAL PASSIERT IST, und beim zweiten Mal war es vorhergesagt:

  * **2026-09-03:** Acht Meldungen aus `Feld E` lagen seit dem 2026-08-29
    unter `plans/meldungen/`, ohne je eine Nummer bekommen zu haben. Sechs
    davon waren aelter als `BL-210`, das zwischendurch eingereiht wurde — die
    Warteschlange wurde also nicht von vorn abgearbeitet, sondern vom Kopf.
    Der Stand-Eintrag dieses Tages hat diesen Waechter woertlich
    vorgeschlagen: *„Ein Waechter, der `plans/meldungen/*.md` gegen die in
    `backlog.md`/`backlog-archiv.md` verlinkten Dateinamen haelt, haette alle
    acht am ersten Tag genannt."*
  * **2026-10-03:** Beim Zusammenfuehren zweier Maschinen lagen auf dem
    gepushten Stand **29** Meldungen ohne Nummer: eine seit dem 2026-09-06
    (eine Fehlbuchung ueber 17,68 USD, `BL-266`) und 28 aus der Zeit vom
    2026-09-17 bis zum 2026-10-02 — darunter drei Nachtraege, die eine schon
    gemeldete Luecke ein zweites und drittes Mal belegten. Die andere Maschine
    hatte denselben Befund an drei Meldungen von Hand gefunden, auf einem
    Stand, der 78 Commits alt war. Gefunden wurde also wieder von Hand, mit
    genau dem Vergleich, den es seit dem 2026-09-03 haette geben sollen.

DIE GATTUNG: `kit-melden ablegen` committet die Datei, die `BL-n`-Zeile
schreibt ein Mensch. Was nicht an einer Mechanik haengt, wird uebergangen —
dieselbe Lehre wie `BL-210`, eine Ebene hoeher. Und der Schaden ist still:
Eine unverlinkte Meldung bricht nichts, sie liegt nur da. Niemand merkt, dass
ein bezahlter Feldbefund keine Spur ins Kit gefunden hat.

WARUM EINE GEFRORENE ALTLAST UND KEINE DATIERTE SCHWELLE
    Der erste Entwurf nahm eine Schwelle an („verlinkt wird seit dem
    2026-08-27") und behauptete, sie sei eine Tatsache. Der eigene Fall unten
    hat das widerlegt: VOR dem Tag sind acht Meldungen verlinkt und dreizehn
    nicht — die Konvention hat sich nicht an einem Tag durchgesetzt, sondern
    allmaehlich. Eine Schwelle waere also Nachsicht im Gewand einer Messung
    gewesen.

    Stattdessen stehen die dreizehn namentlich da. Der Unterschied zu einer
    gewachsenen Ausnahmeliste ist der Fall
    `test_die_altlast_kann_nur_SCHRUMPFEN`: Ein Name darf nur drin stehen,
    solange er wirklich unverlinkt ist. Wer eine Altmeldung nachverlinkt, wird
    rot und muss sie austragen; eine NEUE Meldung kann hier nicht landen, ohne
    dass jemand eine als gefroren markierte Konstante aufmacht. Eine Liste,
    die nur schrumpfen kann, ist kein Leck.

DIE ALTLAST IST LEER (`BL-268`, 2026-10-03), und ihr Befund war ein anderer
als angenommen. Die Liste stand hier mit der Begruendung „triagiert, nur nicht
verlinkt". Beim Zuordnen an DISTINKTIVEN Fakten (Betraege, zitierte
Fehlertexte, Zeilenzahlen — nicht am Titel, der liefert 50-87 % auch fuer
falsche Zeilen) stellte sich heraus: Nur drei waren triagiert (`BL-192`,
`BL-193`, `BL-197`), eine war derselbe Befund wie ein spaeter erneut
gemeldeter (`BL-218`) — und NEUN waren nie triagiert worden; sie haben
`BL-293` bis `BL-301` bekommen. Die gefrorene Liste haette diese neun also
dauerhaft als erledigt durchgewunken. Die Lehre gehoert zur Gattung des
Waechters: Eine Ausnahme braucht einen BELEG ihres Grundes, nicht nur einen
plausiblen Satz.
"""
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MELDUNGEN = REPO_ROOT / "plans" / "meldungen"
QUELLEN = (REPO_ROOT / "plans" / "backlog.md",
           REPO_ROOT / "plans" / "backlog-archiv.md")

# GEFROREN und LEER (2026-10-03, BL-268). Die dreizehn Namen, die hier
# standen, sind alle verlinkt — neun davon als neu triagierte Eintraege. Die
# Liste darf nie wieder wachsen: Wer hier etwas eintraegt, statt es zu
# verlinken, baut das Leck wieder ein, das BL-267 geschlossen hat — und die
# letzte Fuellung hat gezeigt, wie leicht eine Ausnahme dabei etwas Falsches
# behauptet.
ALTLAST = frozenset()

# Dateiname einer Meldung: `<datum>-<slug>.md`. Dasselbe Muster findet den
# Namen in einer Backlog-Zeile — als Link oder nur in Backticks, beides ist
# eine Spur, der ein Mensch folgen kann.
MELDUNGSNAME = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md")


def _ist_kit():
    """Nur im KIT pruefbar — dieselbe Marke wie in `test_bl188`.

    Eine INSTALLIERTE Ablage hat `plans/kit-meldungen/` (die AUSGEHENDEN
    Meldungen des Feldprojekts) und keinen Kit-Backlog. Dort gibt es nichts zu
    vergleichen, und ein roter Fall bewiese nichts ueber das Kit.
    """
    return (REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage").is_file()


def _verlange_kit():
    if not _ist_kit():
        pytest.skip("installierte Ablage — der Kit-Meldungsordner liegt hier "
                    "nicht")
    if not MELDUNGEN.is_dir():
        pytest.skip("plans/meldungen/ liegt in dieser Ablage nicht")


def _backlogtext():
    return "\n".join(p.read_text(encoding="utf-8") for p in QUELLEN
                     if p.is_file())


def meldungsdateien():
    return sorted(p.name for p in MELDUNGEN.glob("*.md")
                  if p.name != "README.md")


def unverlinkte(namen, text, altlast=ALTLAST):
    """Die EIGENTLICHE Pruefung, als reine Funktion.

    Getrennt von der Ablage, damit die Gegenproben synthetisch laufen koennen.
    Ein Waechter, dessen Gegenprobe das echte Repo veraendern muesste, bekommt
    keine — und einer ohne Gegenprobe beschreibt nur, was ohnehin gilt
    (`BL-14`).
    """
    return [n for n in namen if n not in altlast and n not in text]


# --- Der Fall, zweimal im Feld gelaufen -------------------------------------

def test_jede_meldung_ist_im_backlog_verlinkt():
    _verlange_kit()
    namen = meldungsdateien()
    assert namen, "plans/meldungen/ ist leer — dann prueft dieser Fall nichts"
    offen = unverlinkte(namen, _backlogtext())
    assert not offen, (
        "Diese Meldung(en) haben keine Zeile, die auf sie zeigt — sie sind "
        "abgelegt und NICHT triagiert:\n  "
        + "\n  ".join(offen)
        + "\n\nDer Weg einer Meldung hat drei Schritte "
          "(`plans/meldungen/README.md`); Schritt 2 ist die `BL-n`-Zeile in "
          "`plans/backlog.md`, die ihren Pfad nennt. Genau dieser Schritt ist "
          "zweimal zwischen zwei Fix-Sitzungen durchgefallen: acht Meldungen "
          "am 2026-09-03, neunundzwanzig am 2026-10-03 — darunter eine "
          "Fehlbuchung ueber 17,68 USD, die seit dem 2026-09-06 dalag.")


def test_keine_zeile_zeigt_auf_eine_meldung_die_es_nicht_gibt():
    """Die Spiegelrichtung, und sie ist die billigere Haelfte.

    Ein Verweis auf eine Datei, die nicht da ist, sieht im Backlog aus wie ein
    Beleg und ist keiner — dieselbe Gattung wie der tote Pfad, den
    `kit-readme-pruefen.py` im README sucht.
    """
    _verlange_kit()
    vorhanden = set(meldungsdateien())
    tot = set()
    for quelle in QUELLEN:
        if not quelle.is_file():
            continue
        for name in MELDUNGSNAME.findall(quelle.read_text(encoding="utf-8")):
            if name not in vorhanden:
                tot.add(f"{quelle.name}: {name}")
    assert not tot, (
        "Diese Verweise zeigen auf Meldungen, die es nicht gibt:\n  "
        + "\n  ".join(sorted(tot)))


# --- Die Altlast ist gefroren und kann nur schrumpfen -----------------------

def test_die_altlast_kann_nur_SCHRUMPFEN():
    """Der Fall, der diese Liste von einer Ausnahmeliste unterscheidet.

    Ein Name darf hier nur stehen, solange er wirklich unverlinkt ist. Wird
    eine Altmeldung nachverlinkt (`BL-268`), wird dieser Fall rot und verlangt
    den Austrag — die Liste verrottet also nicht, sie schrumpft. Und eine
    NEUE unverlinkte Meldung kann hier nicht stillschweigend landen: Wer sie
    eintraegt, fasst eine als gefroren markierte Konstante an.
    """
    _verlange_kit()
    text = _backlogtext()
    inzwischen_verlinkt = sorted(n for n in ALTLAST if n in text)
    assert not inzwischen_verlinkt, (
        "Diese Meldungen sind inzwischen verlinkt und gehoeren aus der "
        "Altlast heraus (BL-268):\n  " + "\n  ".join(inzwischen_verlinkt))


def test_die_altlast_nennt_nur_dateien_die_es_gibt():
    """Ein Eintrag fuer eine geloeschte Datei waere eine Ausnahme ohne
    Gegenstand — und die naechste Meldung mit demselben Namen waere damit
    stillschweigend freigestellt."""
    _verlange_kit()
    vorhanden = set(meldungsdateien())
    verwaist = sorted(n for n in ALTLAST if n not in vorhanden)
    assert not verwaist, (
        "Die Altlast nennt Dateien, die nicht mehr da sind:\n  "
        + "\n  ".join(verwaist))


# --- Die Gegenproben: der Waechter wird rot, und zwar nur dann --------------

def test_eine_frische_unverlinkte_meldung_wird_gemeldet():
    """Ohne diesen Fall waere der obige stumm gruen, sobald die Menge leer
    bleibt — die `BL-22`-Falle."""
    namen = ["2026-09-30-ein-frischer-fund-aus-dem-feld.md"]
    assert unverlinkte(namen, "Backlog ohne jeden Verweis") == namen


def test_eine_verlinkte_meldung_wird_NICHT_gemeldet():
    """Der Fehlalarm, der diesen Waechter abschalten wuerde (`BL-14`)."""
    name = "2026-09-30-ein-frischer-fund-aus-dem-feld.md"
    text = f"| BL-240 | … | Feld E — Meldung: [`{name}`](meldungen/{name}) | … |"
    assert unverlinkte([name], text) == []


def test_eine_meldung_der_altlast_wird_NICHT_gemeldet():
    """Der Mechanismus bleibt, auch wenn die Liste leer ist: Was in einer
    Altlast steht, wird nicht gemeldet. Geprueft an einer SYNTHETISCHEN
    Altlast — die echte ist seit BL-268 leer."""
    name = "2026-08-24-eine-alte-meldung.md"
    assert unverlinkte([name], "Backlog ohne jeden Verweis",
                       altlast=frozenset({name})) == []


def test_die_echte_altlast_ist_leer():
    """BL-268: Alle dreizehn sind verlinkt. Eine neue Ausnahme braeuchte einen
    Beleg ihres Grundes — die letzte Fuellung behauptete fuer neun Meldungen
    „triagiert", und keine davon war es."""
    assert ALTLAST == frozenset()


def test_die_altlast_steht_nicht_fuer_ein_ganzes_datum_frei():
    """Die Falle, in die der erste Entwurf gelaufen ist, als eigener Fall.

    Eine datierte Schwelle haette alles vor dem 2026-08-27 freigestellt — auch
    eine Meldung, die nie triagiert wurde und nur zufaellig alt ist. Die
    Altlast nennt deshalb DATEIEN und keine Spanne: Eine unverlinkte Meldung
    vom selben Tag, die nicht in der Liste steht, wird gemeldet.
    """
    name = "2026-08-24-eine-nie-triagierte-altmeldung.md"
    assert name not in ALTLAST
    assert unverlinkte([name], "Backlog ohne jeden Verweis") == [name]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

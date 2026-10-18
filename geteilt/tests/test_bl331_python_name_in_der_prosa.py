#!/usr/bin/env python3
"""BL-331: Das Architekten-Briefing widersprach sich in jeder Installation,
deren Interpreter `python3` heisst — und an vier anderen Stellen stand
`python3` woertlich, wo der Interpreter der Installation hingehoert.

WAS GEMELDET WURDE (`Feld G`, 2026-10-13)
    Der Architekt stiess beim Aushaerten auf diesen Satz in seinem Briefing:

        Python heißt `python3`, nicht `python3`.

    Die Vorlage sagte „heißt <Marke>, nicht `python3`", und beide Installer
    setzen den Interpreter OHNE Bedingung ein — beim Einrichten wie bei jedem
    `--update`. Auf Linux und macOS heisst er `python3`, dort stand derselbe
    Name zweimal da. Gattung „Literal statt Konfigurationswert" (`BL-194`),
    diesmal in Prosa.

DIE GEGENRICHTUNG, DIE DIE MELDUNG NICHT NENNT
    `python3` stand woertlich im Aufruf von `zitat_lint.py` (Architekt), zweimal
    in `TEAM.md` (einmal direkt ueber zwei Zeilen, die die Marke tragen) und in
    `beutebuch.md`. Unter Windows ist das der Store-Alias (`BL-131`). Dazu
    nannte das Briefing `ralph.sh`, das es in einer `--nur-pwsh`-Ablage nicht
    gibt — der Waechter aus `BL-139` liest `CLAUDE.md` und `TEAM.md`, aber nicht
    `team/prompts/`.

DER FIX
    „Python heißt hier <Marke>." — zeilenneutral und auf jeder Plattform wahr.
    Die vier Literale tragen die Marke, `ralph.sh` die Bahnendung. Keine
    bedingte Ersetzung im Installer: Sie braeuchte drei Fuellroutinen und den
    Gleichstand beider Baeume (`BL-163`).

WAS HIER GEPRUEFT WIRD
    (a) Mit `python3` gerendert und mit zusammengefasstem Leerraum steht
        nirgends „`X`, nicht `X`". Im Kit an den Vorlagen (Marke ersetzt), in
        einer Installation am schon gerenderten Text.
    (b) Keine gerenderte Vorlage ruft Python unter festem Namen auf (Muster aus
        `test_bl131`). Nur im Kit: In einer Installation ist die Marke laengst
        ersetzt, und der Name dort ist der der Maschine.
    (c) Kein Briefing nennt eine bahngebundene Datei ausserhalb der Stelle, die
        beide Bahnen gegenueberstellt. Im Kit an der Vorlage; in einer
        Installation liegt jede genannte Datei auch da — dieselbe Frage wie
        `BL-139`, an den Briefings.
"""
import re
from pathlib import Path

import pytest

from conftest import kit_pfad

WURZEL = Path(__file__).resolve().parents[2]

# Zusammengesetzt, nicht geschrieben — die Loesung aus test_bl131 und
# test_bl163: Stufe 3 von kit-test.sh meldet jede installierte Datei mit einer
# ungefuellten Marke, auch eine Testdatei, die sie nur zitiert. `"".join(...)`
# statt `+`, weil der Compiler benachbarte Literale zu einer Konstanten faltet.
MARKE = "".join(("{{", "PYTHON", "}}"))

# „`X`, nicht `X`" — derselbe Name zweimal, einmal verneint.
WIDERSPRUCH = re.compile(r"`([^`]+)`,? nicht `\1`")

# Ein Python-AUFRUF unter festem Namen: das Muster aus test_bl131 (Zeile mit
# `(?<![\w./$-])`). Prosa ueber den Namen (`python3` in Backticks, danach ein
# Satzzeichen) trifft es nicht — nur der Name vor einem Argument.
AUFRUF = re.compile(r"(?<![\w./$-])python3?(?=\s+(?:-c|-m|-\s|-\b|\S))")

# Ein Dateiname, den es nur in EINER Bahn gibt — Bauart aus test_bl139.
BAHNDATEI = re.compile(r"(?<![\w/.\\-])(\./|\.\\)?"
                       r"((?:team/)?[A-Za-z0-9_.-]+\.(?:sh|ps1|psm1|cmd))"
                       r"(?![A-Za-z0-9_])")

# Die Stelle, die beide Bahnen GEGENUEBERSTELLT („In der Bahn, in der der
# Mensch arbeitet", Kit-BL-284): Dort ist es ihre Aufgabe, beide zu nennen.
# Am Text erkannt, nicht an Zeilennummern — dieselbe Absicht wie in
# test_bl139: Eine Ausnahme, die nach dem naechsten Absatz die falsche Stelle
# schuetzt, faellt niemandem auf.
GEGENUEBERSTELLUNG = {
    "rolle-architekt.md": ("In der Bahn, in der der Mensch arbeitet",
                           "Remove-Item Env:VAR"),
}


def _ist_kit():
    """Dieselbe Marke wie in test_bl267: die Vorlage liegt nur im Kit."""
    return (WURZEL / "bootstrap" / "CLAUDE.md.vorlage").is_file()


def _briefings():
    ordner = kit_pfad("prompts")
    return sorted(ordner.glob("rolle-*.md")) if ordner.is_dir() else []


def _vorlagen():
    """Alles, was der Installer durch seine Fuellroutine schickt und als Text
    ausliefert: Briefings, TEAM.md, CLAUDE.md und die Plan-Vorlagen."""
    if not _ist_kit():
        return []
    dateien = _briefings() + sorted((WURZEL / "bootstrap").glob("*.md"))
    dateien.append(WURZEL / "bootstrap" / "CLAUDE.md.vorlage")
    return [d for d in dateien if d.is_file()]


def _gerenderte_kit_texte():
    """In einer Installation: was dem Kit gehoert und bei jedem `--update` neu
    gerendert wird. CLAUDE.md und das Beutebuch gehoeren dem Projekt
    (`BL-307`) — dort kommt der Fix nur bei einer Neuinstallation an."""
    if _ist_kit():
        return []
    dateien = _briefings()
    if (WURZEL / "TEAM.md").is_file():
        dateien.append(WURZEL / "TEAM.md")
    return dateien


def _ohne_gegenueberstellung(name, text):
    if name not in GEGENUEBERSTELLUNG:
        return text
    anfang, ende = GEGENUEBERSTELLUNG[name]
    if anfang not in text:
        return text
    i = text.index(anfang)
    j = text.find(ende, i)
    return text[:i] + (text[j:] if j >= 0 else "")


# --- (a) Der gemeldete Satz ----------------------------------------------------

def test_kein_satz_verneint_den_namen_den_er_gerade_nennt():
    """Der Feldfall: gerendert mit dem Namen, den Linux und macOS tragen."""
    dateien = _vorlagen() or _gerenderte_kit_texte()
    if not dateien:
        pytest.skip("weder Vorlagen noch gerenderte Briefings in dieser Ablage")
    funde = []
    for datei in dateien:
        text = datei.read_text(encoding="utf-8-sig").replace(MARKE, "python3")
        flach = re.sub(r"\s+", " ", text)
        for treffer in WIDERSPRUCH.finditer(flach):
            umfeld = flach[max(0, treffer.start() - 40):treffer.end() + 30]
            funde.append(f"{datei.name}: …{umfeld}…")
    assert not funde, (
        "Diese Saetze verneinen den Namen, den sie gerade nennen — gerendert "
        "mit `python3`, wie auf Linux und macOS (Kit-BL-331):\n  "
        + "\n  ".join(funde))


# --- (b) Die Gegenrichtung: der feste Name ------------------------------------

def test_keine_vorlage_ruft_python_unter_festem_namen():
    """Vier Stellen standen woertlich auf `python3` — unter Windows der
    Store-Alias, Exit 49 und „Python was not found" (`BL-131`)."""
    if not _ist_kit():
        pytest.skip("installierte Ablage — dort ist die Marke laengst ersetzt, "
                    "und der Name ist der der Maschine")
    funde = []
    for datei in _vorlagen():
        for nummer, zeile in enumerate(
                datei.read_text(encoding="utf-8-sig").splitlines(), 1):
            if AUFRUF.search(zeile):
                funde.append(f"{datei.relative_to(WURZEL)}:{nummer}: "
                             f"{zeile.strip()}")
    assert not funde, (
        f"Diese Vorlagen rufen Python unter festem Namen auf. Der Installer "
        f"setzt den Interpreter der Maschine nur dort ein, wo {MARKE} steht "
        f"(Kit-BL-331, Kit-BL-131):\n  " + "\n  ".join(funde))


def test_die_marke_steht_an_den_vier_stellen():
    """Gegenprobe: (b) darf nicht dadurch gruen werden, dass die Aufrufe aus
    dem Text verschwinden — die Befehle gehoeren hin, nur mit der Marke."""
    if not _ist_kit():
        pytest.skip("installierte Ablage — dort ist die Marke ersetzt")
    erwartet = (
        (kit_pfad("prompts", "rolle-architekt.md"),
         f"{MARKE} team/tools/zitat_lint.py"),
        (WURZEL / "bootstrap" / "TEAM.md", f"{MARKE} team/tools/zitat_lint.py"),
        (WURZEL / "bootstrap" / "TEAM.md",
         f"{MARKE} team/tools/beutebuch.py list"),
        (WURZEL / "bootstrap" / "beutebuch.md",
         f"{MARKE} team/tools/beutebuch.py lint"),
        (kit_pfad("prompts", "rolle-architekt.md"), f"heißt hier `{MARKE}`."),
    )
    fehlt = [f"{pfad.name}: {stelle}" for pfad, stelle in erwartet
             if stelle not in pfad.read_text(encoding="utf-8-sig")]
    assert not fehlt, ("Diese Stellen tragen die Marke nicht (mehr):\n  "
                       + "\n  ".join(fehlt))


# --- (c) Die Bahnendung --------------------------------------------------------

def test_kein_briefing_nennt_eine_datei_nur_einer_bahn():
    """Im Kit an der Vorlage: Eine bahngebundene Datei steht dort nur in der
    Gegenueberstellung. Sonst traegt sie RUF/ENDUNG als Marke, und der
    Installer setzt die Bahn der Ablage ein."""
    if not _ist_kit():
        pytest.skip("installierte Ablage — dort prueft der Fall darunter, dass "
                    "jede genannte Datei auch daliegt")
    funde = []
    for datei in _briefings():
        text = _ohne_gegenueberstellung(
            datei.name, datei.read_text(encoding="utf-8-sig"))
        for treffer in BAHNDATEI.finditer(text):
            nummer = text.count("\n", 0, treffer.start()) + 1
            funde.append(f"{datei.name}:{nummer} — {treffer.group(0)}")
    assert not funde, (
        "Diese Briefings nennen eine Datei, die es nur in EINER Bahn gibt — in "
        "einer einbahnigen Ablage schicken sie die Rolle ins Leere "
        "(Kit-BL-331, Kit-BL-139):\n  " + "\n  ".join(funde))


def test_jede_datei_die_ein_briefing_nennt_liegt_da():
    """In einer Installation, am gerenderten Text — die Frage aus `BL-139`,
    an den Briefings. In einer `--nur-pwsh`-Ablage war `ralph.sh` tot."""
    if _ist_kit():
        pytest.skip("Kit-Ablage — dort prueft der Fall darueber die Vorlage")
    dateien = _briefings()
    if not dateien:
        pytest.skip("keine gerenderten Briefings in dieser Ablage")
    tot = []
    for datei in dateien:
        text = _ohne_gegenueberstellung(
            datei.name, datei.read_text(encoding="utf-8-sig"))
        for treffer in BAHNDATEI.finditer(text):
            if not (WURZEL / treffer.group(2)).exists():
                nummer = text.count("\n", 0, treffer.start()) + 1
                tot.append(f"{datei.name}:{nummer} — {treffer.group(0)}")
    assert not tot, (
        "Diese Dateien nennt ein Briefing, und es gibt sie hier nicht "
        "(Kit-BL-331, Kit-BL-139):\n  " + "\n  ".join(tot))


def test_die_gegenueberstellung_ist_noch_da():
    """Gegenrichtung zur Ausnahme oben, wie in test_bl139: Wird die Stelle
    umformuliert, schuetzt die Ausnahme sonst still die falsche."""
    for name, (anfang, ende) in GEGENUEBERSTELLUNG.items():
        pfad = kit_pfad("prompts", name)
        if not pfad.is_file():
            pytest.skip(f"{name} liegt in dieser Ablage nicht")
        text = pfad.read_text(encoding="utf-8-sig")
        assert anfang in text and ende in text[text.find(anfang):], (
            f"{name}: Die Gegenueberstellung beider Bahnen ist nicht mehr "
            f"auffindbar ({anfang!r} … {ende!r}). Entweder gehoert die "
            f"Ausnahme geloescht, oder sie schuetzt seit dem Umbau die "
            f"falsche Stelle.")

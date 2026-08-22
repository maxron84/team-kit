#!/usr/bin/env python3
"""BL-140: Die Regeltexte zitierten den Kit-Backlog blank — und verletzten damit
genau die Regel, die sie selbst aufstellen.

DIE REGEL, DIE IN DENSELBEN DATEIEN STEHT
    `CLAUDE.md` schreibt vor: "Verweist eine Zeile auf den Backlog eines
    ANDEREN Projekts, wird sie als `Kit-BL-<N>` geschrieben, nie als blankes
    `BL-<N>`. Der Nummernraum ist sonst doppelt belegt."

    In derselben Datei standen dann bare Verweise auf Kit-Eintraege: `BL-52`,
    `BL-51`, `BL-20`/`BL-25`, `BL-30`, `BL-115`, `HM-32`.

WAS DAS IM FELD BEDEUTET
    Ein frisches Projekt faengt seinen eigenen Backlog bei `BL-1` an, waehrend
    der Regeltext im selben Repo unter `BL-1` eine Kit-Feldlehre meint. Die
    Frage "darf mein erster Eintrag BL-1 heissen?" liess sich aus den
    Regeltexten NICHT beantworten, weil beide Lesarten dort belegt waren.
    Wer nachschlaegt — Mensch oder Rolle — landet im falschen Dokument oder
    findet nichts und haelt den Verweis fuer veraltet.

WARUM DER FIX NICHT MECHANISCH IST
    Der Backlog-Eintrag nennt ihn "mechanisch und einmalig". Er ist es nicht,
    und das hat beim Abtragen zwei Faelle gezeigt, die ein blindes
    Such-und-Ersetze KAPUTT gemacht haette:

      * `HM-7` und `AX-3` im Glossar von TEAM.md sind FORMATBEISPIELE fuer die
        Nummerierung im Beutebuch des ZIELPROJEKTS ("Traegt eine Nummer
        (`HM-7`)"). Ein `Kit-`-Praefix waere dort schlicht falsch.
      * `BL-120` im Architekten-Briefing meint WEDER das Kit NOCH das
        Zielprojekt: `Kit-BL-116` nennt als Quelle das Feldprojekt
        `Feld A` und dessen dortiges `BL-120`. Das Kit-`BL-120` ist das
        FAQ-Geruest — aus einem richtigen Verweis waere ein falscher geworden.

    Daraus folgt die Regel, die dieser Lint durchsetzt, und sie hat DREI
    Sorten statt zwei:

        blank         mein Backlog (der des Zielprojekts)
        Kit-BL-<N>    der Backlog des Kits
        <Projekt>     ein DRITTES Projekt wird BENANNT, nicht praefigiert

WAS DIESER TEST PRUEFT
    Kein blanker `BL-<N>`/`HM-<N>` in einem Text, den das Kit AUSLIEFERT —
    ausser er steht in der Ausnahmeliste unten, jede Ausnahme mit Grund. Eine
    Ausnahmeliste ohne Gruende waere eine Liste von Verstoessen mit Amnestie.
"""
import re
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

# Blanke Nummer: nicht durch "Kit-" praefigiert. Der Bindestrich davor ist
# nicht-Wort, `\b` greift also auch mitten in "Kit-BL-52" — die Vorausschau
# nach hinten ist der eigentliche Filter.
BLANK = re.compile(r"(?<!Kit-)\b(BL|HM|AX)-\d+")

# Jede Ausnahme mit Grund. Schluessel ist (Dateiname, gefundene Nummer).
AUSNAHMEN = {
    ("TEAM.md", "HM-7"):
        "Formatbeispiel im Glossar: zeigt, wie eine Fundnummer im Beutebuch "
        "DIESES Projekts aussieht. Ein Kit-Praefix waere hier falsch.",
    ("TEAM.md", "AX-3"):
        "Formatbeispiel im Glossar, wie HM-7 — Axels Ermittlungsakte.",
    ("rolle-architekt.md", "BL-120"):
        "Meint den Backlog von `Feld A`, nicht den des Kits "
        "(Kit-BL-116 nennt ihn als Quelle) und nicht den des Zielprojekts. "
        "Das Projekt wird im Text BENANNT — das ist die dritte Sorte.",
}


def _ausgelieferte_texte():
    """Alles, was das Kit an Regeltext in ein Projekt legt.

    Zwei Ablagen: Im Kit liegen die Vorlagen unter bootstrap/ und die
    Briefings unter geteilt/prompts/; in einer Installation sind daraus
    CLAUDE.md/TEAM.md in der Wurzel und team/prompts/ geworden.
    """
    treffer = []
    for kandidat in (REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage",
                     REPO_ROOT / "CLAUDE.md",
                     REPO_ROOT / "bootstrap" / "TEAM.md",
                     REPO_ROOT / "TEAM.md",
                     REPO_ROOT / "bootstrap" / "roadmap-skizzen.md"):
        if kandidat.is_file():
            treffer.append(kandidat)
    prompts = kit_pfad("prompts")
    if prompts.is_dir():
        treffer.extend(sorted(prompts.glob("rolle-*.md")))
    return treffer


def test_kein_blanker_verweis_auf_einen_fremden_backlog():
    dateien = _ausgelieferte_texte()
    if not dateien:
        pytest.skip("keine ausgelieferten Regeltexte in dieser Ablage")
    funde = []
    for datei in dateien:
        text = datei.read_text(encoding="utf-8-sig")
        for m in BLANK.finditer(text):
            if (datei.name, m.group(0)) in AUSNAHMEN:
                continue
            zeile = text.count("\n", 0, m.start()) + 1
            funde.append(f"{datei.name}:{zeile} — {m.group(0)}: "
                         f"{text.splitlines()[zeile - 1].strip()[:80]}")
    assert not funde, (
        "BL-140: Diese Verweise sind blank und meinen damit den Backlog DIESES "
        "Projekts. Meinen sie den des Kits, gehoert `Kit-` davor; meinen sie "
        "ein drittes Projekt, gehoert dessen NAME in den Satz:\n  "
        + "\n  ".join(funde))


def test_jede_ausnahme_ist_noch_da_und_traegt_einen_grund():
    """Die Gegenrichtung. Ohne sie waere die Ausnahmeliste eine Einbahnstrasse:
    Ein geloeschter Satz laesst seinen Eintrag als stille Erlaubnis zurueck, und
    die naechste blanke Nummer an derselben Stelle faellt niemandem mehr auf.
    """
    dateien = {d.name: d.read_text(encoding="utf-8-sig")
               for d in _ausgelieferte_texte()}
    if not dateien:
        pytest.skip("keine ausgelieferten Regeltexte in dieser Ablage")
    verwaist = []
    for (name, nummer), grund in AUSNAHMEN.items():
        assert len(grund) > 40, f"Ausnahme {name}/{nummer} ohne echten Grund"
        if name not in dateien:
            continue          # andere Ablage, andere Dateien
        if not re.search(rf"(?<!Kit-)\b{re.escape(nummer)}\b", dateien[name]):
            verwaist.append(f"{name}/{nummer}")
    assert not verwaist, (
        "Diese Ausnahmen zeigen ins Leere — die Stelle gibt es nicht mehr. "
        "Eintrag loeschen, sonst erlaubt er lautlos die naechste:\n  "
        + "\n  ".join(verwaist))


def test_die_regel_steht_auch_im_regeltext():
    """Ein Lint, der eine Regel durchsetzt, die nirgends geschrieben steht,
    erzieht niemanden — er ueberrascht nur beim naechsten Textumbau."""
    for kandidat in (REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage",
                     REPO_ROOT / "CLAUDE.md"):
        if not kandidat.is_file():
            continue
        text = kandidat.read_text(encoding="utf-8-sig")
        assert "Kit-BL-" in text, (
            f"{kandidat.name} stellt die Kit-BL-Regel auf, benutzt sie aber "
            "selbst kein einziges Mal — genau der Zustand, den BL-140 "
            "beschreibt.")
        return
    pytest.skip("keine CLAUDE.md in dieser Ablage")

#!/usr/bin/env python3
"""BL-230/BL-231: Die Selbstkontrolle des pwsh-Selbsttests war selbst
unzuverlaessig — zwei Gegenproben verfaelschten nichts, und die
Plausibilitaetszahl war veraltet.

WIE DIE FUNDE ENTSTANDEN
    Der erste vollstaendige Lauf von `pwsh/kit-test.ps1`, nachdem `BL-229` die
    pwsh-Bahn wieder lauffaehig gemacht hatte, endete NICHT gruen — mit drei
    Befunden, die alle das Pruefwerk selbst betrafen, nicht das Gepruefte.

BL-230 — EINE GEGENPROBE, DIE NICHTS VERFAELSCHT
    Zwei Gegenproben in Schritt 5 verfaelschen eine Zahl im README und
    verlangen, dass `kit-readme-pruefen.py` rot wird. Geschrieben war das so:

        $readme -replace 'muster' + [char]0x5c + 'rest', 'ersatz'

    PowerShell zieht die ERSETZUNG in die Verkettung hinein: Das Muster wird zu
    "muster\\rest ersatz", und `-replace` laeuft in seiner EINARMIGEN Form
    (Treffer loeschen statt ersetzen). Kein Treffer, keine Aenderung, kein
    Fehler — die Kopie war identisch mit dem Original, der Pruefer blieb zu
    Recht gruen, und der Selbsttest las das als "der Waechter wird nicht rot".

    Betroffen ist NUR die zweiarmige Form. Ohne Komma ist dieselbe Verkettung
    korrekt, weil sie dann der ganze Operand ist — deshalb messen die
    `-match`-Zeilen im selben Skript richtig.

    Das ist `BL-14` eine Ebene hoeher: nicht ein Waechter, der nie rot wird,
    sondern ein GEGENBEWEIS, der nie falsifiziert. Er existiert genau dafuer.

BL-231 — EINE PLAUSIBILITAETSZAHL, DIE VERALTET
    `kit-test.ps1` zaehlt seine Einzelpruefungen und haelt sie gegen
    `$script:PruefungenSoll`. Der Kommentar darueber sagt ausdruecklich: "Wer
    eine Pruefung ergaenzt, zieht die Zahl nach." `BL-208` ergaenzte eine und
    zog sie nicht nach. Seither endete JEDER vollstaendige Lauf rot — aus
    Buchhaltungsgruenden.

    Dazu die Meldung: Sie lautete in BEIDEN Richtungen "ein Schritt wurde
    uebersprungen", bei mehr Pruefungen also "Nur 65 von 64 … uebersprungen".
    Das schickt den Leser an die falsche Stelle.

WAS DIESE TESTS PRUEFEN
    Beide Klassen fallen hier in SEKUNDEN auf, nicht erst nach einem Lauf von
    rund einer Stunde. Genau das ist der Ertrag: Ein Waechter, der nur am Ende
    eines teuren Laufs greift, wird beim Bauen nicht befragt.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
KIT_TEST = REPO_ROOT / "pwsh" / "kit-test.ps1"


def _quelle():
    if not KIT_TEST.is_file():
        pytest.skip("pwsh/kit-test.ps1 liegt nur im Kit, nicht in der Installation")
    return KIT_TEST.read_text(encoding="utf-8-sig")


# --- BL-230: die zweiarmige Form mit inline verkettetem Muster ------------
# Gesucht wird die GATTUNG, nicht die zwei bekannten Zeilen: Auf `-replace`
# folgt ein Muster-Operand (Literal oder blanke Variable), und DIREKT dahinter
# steht ein `+`. Genau diese Form zieht die Ersetzung in die Verkettung.
#
# Die Regel ist bewusst ENG. Ein Waechter mit Fehlalarmen wird abgeschaltet
# statt befolgt (BL-14), und die drei korrekten Bauarten sehen anders aus:
# Muster in einer Variablen (`-replace $m, 'x'`), geklammertes Muster
# (`-replace ('a' + $b), 'x'`) und nachtraegliche Verkettung des ERGEBNISSES
# (`($Out -replace 'a', '') + 'b'`). Alle drei bleiben stumm; gegen alle drei
# wird unten ausdruecklich geprueft.
ZWEIARMIG = re.compile(
    r"""-replace\s+(?:'[^'\n]*'|"[^"\n]*"|\$[\w:]+)\s*\+""")

PWSH_DATEIEN = sorted(
    p for muster in ("*.ps1", "*.psm1")
    for p in (REPO_ROOT / "pwsh").rglob(muster)) if (REPO_ROOT / "pwsh").is_dir() else []


@pytest.mark.parametrize("datei", PWSH_DATEIEN, ids=lambda p: p.name)
def test_kein_inline_verkettetes_muster_mit_ersatz(datei):
    """Der Fund selbst — und jede kuenftige Stelle derselben Bauart."""
    befunde = [f"{datei.name}:{nr}: {zeile.strip()[:90]}"
               for nr, zeile in enumerate(
                   datei.read_text(encoding="utf-8-sig").splitlines(), 1)
               if ZWEIARMIG.search(zeile)]
    assert not befunde, (
        "`-replace <verkettung>, <ersatz>` zieht die Ersetzung in die "
        "Verkettung: Das Muster wird zu \"<muster> <ersatz>\", und `-replace` "
        "laeuft einarmig (Treffer loeschen). Es ersetzt still NICHTS. Muster "
        "in eine Variable legen oder klammern (BL-230):\n  "
        + "\n  ".join(befunde))


def test_die_regel_faengt_den_urspruenglichen_fund():
    """Gegenprobe: Ein Waechter, der nie rot wird, sichert nichts ab
    (BL-14). Nachgestellt wird die Zeile im Wortlaut, in der der Fund sass."""
    kaputt = ("        -Value ($readme -replace '`BL-1`…`BL-(' + "
              "[char]0x5c + 'd+)`', '`BL-1`…`BL-1`')")
    assert ZWEIARMIG.search(kaputt), (
        "Die Regel erkennt die Zeile nicht mehr, in der der Fund sass — dann "
        "misst der Test oben nichts.")


@pytest.mark.parametrize("heil", [
    "    $neu = $readme -replace $musterSpanne, '`BL-1`…`BL-1`'",
    "    $x = $t -replace ('a' + [char]0x58 + 'b'), 'TREFFER'",
    r"    $Out = ($Out -replace '\.json$', '') + '-api-fallback.json'",
    r"    $d = @(($TEAM_DOMAENEN -replace ',', ' ') -split '\s+')",
    r"""    Team-Fehler ("  " + ($e -replace '^\S+\s', ''))""",
])
def test_die_regel_meldet_die_richtigen_formen_nicht(heil):
    """Die zweite Gegenprobe, und sie ist die wichtigere: Eine Regel mit
    Fehlalarmen wird abgeschaltet statt befolgt (BL-14)."""
    assert not ZWEIARMIG.search(heil), f"Fehlalarm auf einer korrekten Zeile: {heil}"


# --- BL-231: die Plausibilitaetszahl -------------------------------------

def test_pruefungensoll_stimmt_mit_den_wirklichen_pruefungen():
    """Die Zahl steht im Skript und wird erst nach rund einer Stunde Lauf
    gegen die Wirklichkeit gehalten. Hier dauert es Millisekunden."""
    quelle = _quelle()
    m = re.search(r"\$script:PruefungenSoll\s*=\s*(\d+)", quelle)
    assert m, "PruefungenSoll steht nicht mehr im Skript — der Absturzschutz fehlt."
    soll = int(m.group(1))
    ist = len(re.findall(r"^\s*Pruefe\s", quelle, re.M))
    assert soll == ist, (
        f"kit-test.ps1 ruft {ist} Einzelpruefungen auf, PruefungenSoll sagt "
        f"{soll}. Wer eine Pruefung ergaenzt, zieht die Zahl nach — sonst "
        "endet der Lauf nach einer Stunde rot, ohne dass etwas kaputt ist "
        "(BL-231).")


def test_die_meldung_unterscheidet_zu_wenig_von_zu_viel():
    """Beide Abweichungen sind Befunde, aber verschiedene. Eine Meldung, die
    bei 'mehr als erwartet' von einem uebersprungenen Schritt spricht, schickt
    den Leser an die falsche Stelle."""
    quelle = _quelle()
    assert "-lt $script:PruefungenSoll" in quelle, (
        "kit-test.ps1 vergleicht die Pruefzahl nicht mehr richtungsabhaengig "
        "(BL-231).")
    assert "-gt $script:PruefungenSoll" in quelle, (
        "kit-test.ps1 kennt den Fall 'mehr Pruefungen als erwartet' nicht — "
        "er wird dann als uebersprungener Schritt gemeldet (BL-231).")

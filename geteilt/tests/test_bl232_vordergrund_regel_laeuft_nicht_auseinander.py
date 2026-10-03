#!/usr/bin/env python3
"""BL-232/BL-233 — die Vordergrund-Auflage liegt SECHSMAL und lief auseinander.

Zwei Meldungen aus `Feld E` an zwei aufeinanderfolgenden Tagen, und erst
zusammen ergeben sie den Befund:

  * 2026-09-05, Frank, 13,13 USD in zwei Leerlaeufen. Sein `result` sagte
    woertlich *"I'll hold here until the smoke-test MONITOR notifies me of
    completion."* Die Meldung schloss daraus, ihm fehle die Regel — sie fehlt
    seinem BRIEFING, aber nicht seinem Prompt: Er bekommt sie seit BL-207 ueber
    `$SMOKE_SUFFIX` zur Laufzeit. **Nur stand im Suffix der Monitor nicht
    drin.** Die vier Briefings verbieten alle drei Bauformen
    (Hintergrund-Task, Wakeup, Monitor), die beiden Laufzeit-Bausteine
    verboten zwei — und die Rolle nahm die dritte.
  * 2026-09-06, Ralph, Exit 43. Hier stand der Absatz woertlich im Briefing,
    gelesen und zur Haelfte befolgt. Die Anweisung *„setze das Zeitlimit
    deines Werkzeugs auf diesen Wert"* nannte **600** und meinte Sekunden;
    das Werkzeug der Rolle nimmt sein Zeitlimit in **Millisekunden**. Wer ihr
    woertlich folgt, stellt 0,6 Sekunden ein und bekommt einen sofortigen
    Fehlschlag — und der naheliegende Ausweg ist genau der, den derselbe Satz
    zwei Zeilen spaeter verbietet.

DIE GATTUNG, und sie ist der Grund fuer diese Datei: Derselbe Satz steht an
SECHS Stellen — vier Briefings, zwei Laufzeit-Bausteine (mal zwei Bahnen) —
und niemand hielt sie gegeneinander. `test_bl201` prueft die vier Briefings
einzeln auf ihre Bestandteile; eine Stelle, die eine Bauform NICHT nennt,
faellt dort nur auf, wenn sie in der Liste steht. Der Laufzeit-Baustein stand
nicht in der Liste. Die Meldung vom 2026-09-05 hat den Waechter selbst
vorgeschlagen: *„Der Absatz ist in fuenf Briefings byte-gleich; ein Team-Test,
der genau das prueft, haette die Luecke ohne Feldschaden gefunden."*
"""
import re
import sys
from pathlib import Path

import pytest

from conftest import Variable

WURZEL = Path(__file__).resolve().parents[2]

# Die drei Bauformen, die im Feld VERSCHIEDEN benannt wurden — und von denen
# jede einzeln genuegt, um in den vierten Ausgang zu laufen. Wer nur zwei
# verbietet, bekommt die dritte: genau so ist BL-232 entstanden.
BAUFORMEN = ("Hintergrund-Task", "Monitor", "Wakeup")

# Die vier Briefings, die den Absatz tragen. Frank fehlt hier aus demselben
# gemessenen Grund wie in `test_bl201`: Sein Briefing liegt auf dem harten
# 45-Zeilen-Limit, und er bekommt die Auflage zur LAUFZEIT. Dass die
# Laufzeit-Fassung dieselben drei Bauformen nennen muss, ist nach BL-232 keine
# Nebensache mehr, sondern der Kern — sie steht unten als eigener Fall.
BRIEFINGS = ("ralph", "harry", "marv", "axel")

MARKE = "Lange Befehle laufen im VORDERGRUND"


def _briefing(rolle):
    for kandidat in (WURZEL / "geteilt" / "prompts" / f"rolle-{rolle}.md",
                     WURZEL / "team" / "prompts" / f"rolle-{rolle}.md"):
        if kandidat.is_file():
            return kandidat.read_text(encoding="utf-8")
    pytest.skip(f"rolle-{rolle}.md liegt hier nicht")


def _absatz(rolle):
    t = _briefing(rolle)
    assert MARKE in t, f"rolle-{rolle}.md traegt die Auflage nicht (BL-201)."
    anfang = t.index(MARKE)
    ende = t.find("\n**", anfang + len(MARKE))
    return t[anfang:ende if ende != -1 else len(t)]


def _bausteine(tmp_path, schale, namen, timeout):
    """Rendert die Prompt-Bausteine aus der ECHTEN Bibliothek.

    Gemessen statt gelesen: Der Fehler von BL-233 steckt im FERTIGEN Text, den
    die Rolle sieht — eine Quelltext-Suche nach `TEAM_SMOKE_TEST_TIMEOUT` sagt
    ueber die eingesetzte Zahl nichts. Die Bibliothek wird dafuer in ein leeres
    Verzeichnis kopiert, damit keine `team.config.*` daneben liegt (BL-100).
    """
    lib = schale.lib_kopieren(tmp_path)
    ergebnis = schale.lauf([Variable(n) for n in namen], cwd=tmp_path, lib=lib,
                           env={"TEAM_SMOKE_TEST": "./smoke.sh",
                                "TEAM_SMOKE_TEST_TIMEOUT": timeout})
    assert ergebnis.returncode == 0, ergebnis.stderr
    return ergebnis.stdout


# --- (1) Alle drei Bauformen, an JEDER Stelle -------------------------------

@pytest.mark.parametrize("rolle", BRIEFINGS)
def test_jedes_briefing_verbietet_alle_drei_bauformen(rolle):
    """Die Seite, die schon richtig war — als Gegenrichtung zu Fall (2).

    Ohne sie koennte der Fix unten gruen werden, indem die Briefings sich der
    aermeren Laufzeit-Fassung angleichen statt umgekehrt.
    """
    absatz = _absatz(rolle)
    fehlend = [b for b in BAUFORMEN if b not in absatz]
    assert not fehlend, (
        f"rolle-{rolle}.md verbietet {fehlend} nicht. Im Feld wurde der Fall "
        f"dreimal verschieden formuliert — wer nur zwei Bauformen verbietet, "
        f"bekommt die dritte (BL-232: 13,13 USD an einem Monitor).")


@pytest.mark.parametrize("baustein", ["SMOKE_ZEILE", "SMOKE_SUFFIX"])
def test_der_laufzeit_baustein_verbietet_alle_drei_bauformen(
        tmp_path, schale, baustein):
    """DER Fall von BL-232, und er ist gemessen statt vermutet.

    `SMOKE_SUFFIX` ist alles, was Frank ueber den Smoke-Test liest. Er nannte
    den Hintergrund-Task und den Wakeup und schwieg zum Monitor; Franks
    `result` nannte woertlich den Monitor. Die Luecke in der Auflage und die
    gewaehlte Bauform sind dieselbe Stelle.
    """
    text = _bausteine(tmp_path, schale, (baustein,), timeout="900")
    fehlend = [b for b in BAUFORMEN if b not in text]
    assert not fehlend, (
        f"{baustein} verbietet {fehlend} nicht — und ist bei Frank der "
        f"EINZIGE Ort, an dem er die Auflage ueberhaupt liest "
        f"(BL-207/BL-232).\n{text}")


# --- (2) Die sechs Stellen laufen nicht auseinander --------------------------

def test_der_briefing_absatz_ist_in_allen_vier_byte_gleich():
    """Der Waechter, den die Meldung selbst vorgeschlagen hat.

    Vier Kopien desselben Absatzes in vier Dateien: Wer eine davon
    nachzieht und die anderen vergisst, steuert vier Rollen mit vier
    verschiedenen Auflagen — und keine einzige Zusicherung wird rot. Genau so
    ist die Luecke von BL-232 entstanden, nur eine Ebene tiefer.
    """
    absaetze = {rolle: _absatz(rolle) for rolle in BRIEFINGS}
    erster = absaetze[BRIEFINGS[0]]
    abweichend = [r for r, a in absaetze.items() if a != erster]
    assert not abweichend, (
        f"Der Vordergrund-Absatz laeuft auseinander: {abweichend} weichen von "
        f"rolle-{BRIEFINGS[0]}.md ab. Vier Rollen bekaemen vier verschiedene "
        f"Auflagen, ohne dass eine Zusicherung rot wird.")


# --- (3) Die Zeiteinheit steht dort, wo die Zahl steht (BL-233) --------------

@pytest.mark.parametrize("baustein", ["SMOKE_ZEILE", "SMOKE_SUFFIX"])
def test_der_laufzeit_baustein_nennt_BEIDE_zeiteinheiten(tmp_path, schale,
                                                          baustein):
    """Ein Faktor 1 000 zwischen der Anweisung und dem Werkzeug.

    Der Wert ist in Sekunden gemeint (er geht an `timeout(1)`), das Werkzeug
    der Rolle nimmt Millisekunden. Die alte Fassung sagte „setze das Zeitlimit
    deines Werkzeugs auf diesen Wert" und nannte nur die Sekundenzahl — wer
    ihr folgt, stellt ein Tausendstel ein. Deshalb muss die umgerechnete Zahl
    DANEBEN stehen: Umrechnen ist Arbeit, die eine Auflage der Rolle nicht
    aufgeben darf.
    """
    text = _bausteine(tmp_path, schale, (baustein,), timeout="900")
    assert "900 Sekunden" in text, (
        f"{baustein} nennt die Einheit der Zahl nicht — die 900 allein ist "
        f"zwischen Sekunden und Millisekunden nicht entscheidbar.\n{text}")
    assert "900000" in text, (
        f"{baustein} nennt den Millisekunden-Wert nicht. Das Werkzeug der "
        f"Rolle nimmt sein Zeitlimit in Millisekunden; ohne die ausgerechnete "
        f"Zahl steht ein Faktor 1 000 zwischen Anweisung und Werkzeug "
        f"(BL-233).\n{text}")
    assert "Millisekunden" in text, (
        f"{baustein} sagt nicht, WOFUER die zweite Zahl steht.\n{text}")


@pytest.mark.parametrize("rolle", BRIEFINGS)
def test_das_briefing_nennt_die_einheit_der_zahl(rolle):
    """Dieselbe Falle im Briefing, nur ohne eingesetzten Wert.

    Hier steht der Name der Variablen statt ihrer Zahl, also kann die
    Umrechnung nicht ausgeschrieben werden — die EINHEIT muss aber dastehen,
    sonst erbt die Rolle denselben Faktor 1 000.
    """
    absatz = _absatz(rolle)
    assert "Sekunden" in absatz, (
        f"rolle-{rolle}.md nennt `TEAM_SMOKE_TEST_TIMEOUT` ohne Einheit.")
    assert "Millisekunden" in absatz, (
        f"rolle-{rolle}.md warnt nicht vor dem Werkzeug, das sein Zeitlimit "
        f"in Millisekunden nimmt (BL-233).")


def test_die_regeldatei_vorlage_traegt_beides():
    """Die Vorlage ist die Quelle, aus der ein Feldprojekt seine Regeln erbt.

    Ein Fix nur in den Briefings liesse die Regeldatei mit dem alten Wortlaut
    stehen — und `--update` schreibt sie nicht neu (`BL-177`). Dann steht die
    reparierte Regel im Prompt und die kaputte in der Regeldatei daneben.
    """
    pfad = WURZEL / "bootstrap" / "CLAUDE.md.vorlage"
    if not pfad.is_file():
        pytest.skip("Die Regeldatei-VORLAGE liegt nur im Kit.")
    text = pfad.read_text(encoding="utf-8")
    block = text[text.index("Vorbeugend gilt für jede bauende Rolle"):][:1200]
    for bauform in BAUFORMEN:
        assert bauform in block, (
            f"CLAUDE.md.vorlage verbietet '{bauform}' nicht (BL-232).")
    assert "Millisekunden" in block, (
        "CLAUDE.md.vorlage nennt die Umrechnung nicht (BL-233).")


# --- (4) Gegenrichtung: der Absatz bleibt bezahlbar --------------------------

@pytest.mark.parametrize("rolle", BRIEFINGS + ("frank",))
def test_die_briefings_bleiben_unter_dem_zeilenlimit(rolle):
    """Die Zusicherung, gegen die dieser Fix eingetauscht werden musste.

    Drei der vier Briefings lagen vor dem Fix exakt auf 45 Zeilen. Die neue
    Einheit ist deshalb gegen Fuellwoerter im selben Absatz getauscht worden
    und nicht drangehaengt — eine Auflage, die eine andere Zusicherung bricht,
    verschiebt nur die Kosten (die Lehre aus BL-201).
    """
    pfad = WURZEL / "geteilt" / "prompts" / f"rolle-{rolle}.md"
    if not pfad.is_file():
        pytest.skip("Briefings liegen hier nicht")
    n = len(pfad.read_text(encoding="utf-8").splitlines())
    assert n <= 45, (
        f"rolle-{rolle}.md hat {n} Zeilen (Limit 45). Jede Zeile wird bei "
        f"JEDEM Aufruf der Rolle bezahlt.")


def test_frank_bekommt_die_volle_auflage_zur_laufzeit():
    """Die Gegenrichtung zur Briefing-Ausnahme — der Kern von BL-232.

    `test_bl201` haelt fest, DASS Frank die Auflage zur Laufzeit bekommt, und
    prueft dafuer `VORDERGRUND` und `Hintergrund-Task`. Genau diese Liste war
    der blinde Fleck: Der Monitor stand nicht darin, also fiel sein Fehlen
    nicht auf — und Frank nahm den Monitor. Hier steht die VOLLSTAENDIGE
    Liste, am Quelltext beider Bahnen.
    """
    geprueft = 0
    for datei in ("bash/lib.sh", "pwsh/lib.psm1"):
        pfad = WURZEL / datei
        if not pfad.is_file():
            continue
        text = pfad.read_text(encoding="utf-8")
        zuweisung = re.search(r"^\s*\$?SMOKE_SUFFIX\s*=\s*\"(.*)$", text,
                              re.M)
        assert zuweisung, f"{datei}: SMOKE_SUFFIX wird nicht mehr gesetzt"
        block = zuweisung.group(1)
        for bauform in BAUFORMEN:
            assert bauform in block, (
                f"{datei}: Franks einziger Hinweis auf den Smoke-Test "
                f"verbietet '{bauform}' nicht — die Luecke von BL-232.")
        geprueft += 1
    if not geprueft:
        pytest.skip("keine Bibliothek dieser Ablage gefunden")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

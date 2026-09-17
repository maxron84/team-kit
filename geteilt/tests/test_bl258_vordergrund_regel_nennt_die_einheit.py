#!/usr/bin/env python3
"""BL-258: Die Vordergrund-Regel nennt Sekunden, das Werkzeug der Rolle rechnet
in Millisekunden — Faktor 1000 in die falsche Richtung.

DER FELDBEFUND
    Der Bau-Loop brach mitten in einer Kaskade mit Exit 43 ab (`BL-41` —
    „Stufe fertig, Quittung fehlt"). Ralphs `result`-Feld sagte woertlich, worauf
    er wartete: auf einen Hintergrundlauf, der das Standard-Zeitlimit des
    Werkzeugs ueberschritten hatte.

    BEMERKENSWERT IST NICHT DER FEHLER, SONDERN WO ER AUFTRAT: Der
    `BL-201`-Absatz stand in diesem Briefing vorhanden und woertlich. Die Rolle
    hat die Regel GELESEN, ihre erste Haelfte uebernommen („er darf lange
    brauchen") und die zweite gebrochen („niemals im Hintergrund").

    Der Satz lautete: „er darf bis zu ${TEAM_SMOKE_TEST_TIMEOUT} Sekunden
    brauchen, SETZE DAS ZEITLIMIT DEINES WERKZEUGS AUF DIESEN WERT". Der
    Konfigurationswert ist in Sekunden gemeint und wird an `timeout(1)`
    gereicht; das Werkzeug, mit dem die Rolle den Befehl ausfuehrt, nimmt sein
    Zeitlimit in MILLISEKUNDEN. Wer der Anweisung woertlich folgt, setzt 0,6
    Sekunden statt 600 — und der naheliegende Ausweg aus dem sofortigen
    Fehlschlag ist genau der, den derselbe Satz zwei Zeilen spaeter verbietet.

EHRLICH GEHALTEN
    In dem gemeldeten Lauf ist die Einheiten-Verwechslung NICHT als Ursache
    belegt — die Rolle nennt den Default-Timeout, hat also gar kein Limit
    gesetzt. Der Faktor 1000 steht trotzdem zwischen der Anweisung und dem
    Werkzeug, und er trifft jede Installation, deren Suite laenger laeuft als
    der Werkzeug-Default. Der Schaden ist gedeckelt, aber nicht null: `BL-41`
    fing den Lauf ab, bevor ein Neustart die fertige Arbeit wegwarf. Ohne
    diesen Riegel kostete derselbe Fehler im selben Feldprojekt 13,13 USD in
    zwei Leerlaeufen (`BL-257`).

WAS DIESER TEST PRUEFT — IN GATTUNGSFORM
    Nicht den heutigen Wortlaut, sondern die Bedingung: WO die Regel eine
    Zeitspanne in Sekunden nennt, muss sie auch die Millisekunden-Form nennen.
    Und zwar auf BEIDEN Bahnen — der Satz gehoert dem Kit, nicht dem Projekt,
    und ein Fix, der nur auf einer Bahn abgenommen wird, kann die andere
    unberuehrt lassen (`BL-229`).
"""
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]

BAHNEN = {
    "bash": WURZEL / "bash" / "lib.sh",
    "pwsh": WURZEL / "pwsh" / "lib.psm1",
}

# Die Stellen, an denen die Regel eine Zeitspanne ausspricht. Gesucht wird die
# GATTUNG: irgendeine Nennung des Zeitlimit-Werts mit dem Wort "Sekunden".
SEKUNDEN = re.compile(r"\$\{?TEAM_SMOKE_TEST_TIMEOUT\}?\s+Sekunden")
# Die Millisekunden-Form ist die Zeichenkette plus drei Nullen -- bewusst als
# TEXT und nicht als Rechnung: Ein `$(( ))` ueber einen nicht-numerischen
# Konfigurationswert waere ein Abbruch an einer Stelle, die nur einen Prompt
# baut.
MILLISEKUNDEN = re.compile(r"\$\{TEAM_SMOKE_TEST_TIMEOUT\}000")


def _quelle(bahn):
    pfad = BAHNEN[bahn]
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt in dieser Ablage nicht")
    return pfad.read_text(encoding="utf-8")


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_jede_sekunden_nennung_hat_ihre_millisekunden_form(bahn):
    """Der Fund selbst."""
    text = _quelle(bahn)
    sekunden = len(SEKUNDEN.findall(text))
    millis = len(MILLISEKUNDEN.findall(text))
    assert sekunden, (
        f"{BAHNEN[bahn].name} nennt das Zeitlimit gar nicht mehr in Sekunden "
        "— dann ist dieses Muster veraltet, nicht die Regel.")
    assert millis >= sekunden, (
        f"{BAHNEN[bahn].name} nennt {sekunden}-mal Sekunden, aber nur "
        f"{millis}-mal die Millisekunden-Form. Die Rolle rechnet nicht um; "
        "sie setzt den Wert, wie er dasteht (BL-258).")


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_die_einheit_wird_ausdruecklich_benannt(bahn):
    """Eine Zahl allein reicht nicht — die Verwechslung entsteht an der
    EINHEIT, also muss sie dastehen."""
    text = _quelle(bahn)
    assert "MILLISEKUNDEN" in text, (
        f"{BAHNEN[bahn].name} nennt die Einheit nicht, an der die Verwechslung "
        "haengt (BL-258).")


@pytest.mark.parametrize("bahn", sorted(BAHNEN))
def test_der_erlaubte_weg_steht_an_der_anweisung(bahn):
    """Die zweite und wichtigere Haelfte der Meldung: Die heutige Fassung nannte
    den erlaubten Weg als Nebensatz und das Verbot als eigenen Satz — gebrochen
    wurde sie von einer Rolle, die sie gelesen hatte. Der Ausweg gehoert an die
    Handlungsanweisung gebunden, nicht danebengestellt."""
    text = _quelle(bahn)
    assert "statt in den Hintergrund" in text, (
        f"{BAHNEN[bahn].name} bindet die verbotene Alternative nicht an die "
        "Anweisung (BL-258).")


def test_beide_bahnen_sagen_dasselbe():
    """Drift zwischen den Bahnen ist der Fehler, den die Doppelbahn sichtbar
    machen soll. Der Satz gehoert dem Kit, nicht dem Projekt."""
    bash = _quelle("bash")
    pwsh = _quelle("pwsh")
    for merkmal in ("MILLISEKUNDEN", "BL-258"):
        assert (merkmal in bash) == (merkmal in pwsh), (
            f"'{merkmal}' steht nur auf einer Bahn — ein Fix, der nur dort "
            "abgenommen wird, laesst die andere unberuehrt (BL-229).")

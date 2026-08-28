#!/usr/bin/env python3
"""Regressionstest fuer BL-205: Frank hat eine Regel fuer eine schon vor ihm
rote Suite — und stellt keine Rueckfragen mehr, die niemand liest.

DER FALL (Feld B, 2026-08-27): Frank hatte einen fertigen, nachweislich
nicht-regressiven Diff. Die Suite war rot, aber **unabhaengig von ihm** — eine
ambiente Umgebungsvariable leckte in eine In-Prozess-Testbank. Schritt 1 seines
Auftrags traegt `$SMOKE_SUFFIX`: *„Smoke-Test gruen: <befehl>."* Die Auflage war
**absolut** und kannte den Fall nicht, dass die Rotheit nicht von Frank stammt.
Sie misst damit eine Eigenschaft der **Maschine** statt eine des Fixes — und
trifft ausgerechnet den Lauf, in dem die Rolle richtig gearbeitet hat.

Frank brach regelkonform ab und stellte **zwei Rueckfragen an einen Menschen,
den es im headless Lauf nicht gibt**. Kostenpunkt: 2,7517 USD verworfen und im
Folgeaufruf neu bezahlt.

DER ZWEITE TEIL HAT DIESELBE WURZEL: Frank kannte genau zwei Ausgaenge (Promise
/ kein Promise). Fuer *„Hindernis, aber unterwegs einen echten neuen Fehler
gefunden"* gab es keinen — der Beifang endete im gitignorierten Log. Gerettet
wurde er nur, weil ein Mensch spaeter das Log oeffnete.

DIE DREI ZEILEN DES EINTRAGS, und wo sie gelandet sind:
  (1) Differenzmessung  -> `$SMOKE_SUFFIX` in beiden Bibliotheken;
  (2) Fundblock `offen` -> Franks Auftragstext in beiden Entrypoints;
  (3) „es liest niemand mit" -> ebenfalls Auftragstext.

WARUM NICHT INS BRIEFING: `rolle-frank.md` liegt exakt auf dem harten
45-Zeilen-Limit (`test_stufe90_briefings.py`), und ein Briefing liegt in JEDEM
Prompt seiner Rolle. Der Auftragstext ist der richtige Ort — er traegt ohnehin
die lauf-spezifischen Auflagen, und er ist nicht laengenbegrenzt.
"""
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]

BIBLIOTHEKEN = ["bash/lib.sh", "pwsh/lib.psm1"]
EINSTIEGE = ["bash/entry/frank.sh", "pwsh/entry/frank.ps1"]


def _lies(rel):
    pfad = WURZEL / rel
    if not pfad.is_file():
        pytest.skip(f"{rel} liegt hier nicht (Bahn abgewaehlt oder "
                    f"installierte Ablage statt Kit)")
    return pfad.read_text(encoding="utf-8")


def _smoke_suffix(rel):
    """Die EINE Zeile, die Frank seine Smoke-Auflage gibt.

    Geschnitten wird die Zeile, nicht die Datei: `BL-205`, `rot` und `Stand`
    kommen in `lib.sh` an einem Dutzend anderer Stellen vor, und eine
    Gegenprobe ueber die ganze Datei bliebe deshalb gruen. Dieselbe Lehre wie
    in BL-193.
    """
    for zeile in _lies(rel).splitlines():
        if "SMOKE_SUFFIX" in zeile and "Quittung" in zeile:
            return zeile
    pytest.fail(f"{rel}: die gefuellte SMOKE_SUFFIX-Zeile ist nicht mehr zu "
                f"finden — Frank bekommt seine Smoke-Auflage woanders her.")


# --- (1) Differenzmessung statt Absolutwert ---------------------------------

@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_die_auflage_kennt_die_schon_vorher_rote_suite(rel):
    """Der Kern: Die Auflage ist nicht mehr absolut.

    Ohne diesen Zusatz bricht Frank bei einer Rotheit ab, die nicht von ihm
    stammt — und wirft dabei einen fertigen, nicht-regressiven Diff weg.
    """
    zeile = _smoke_suffix(rel)
    assert "VOR deinem Fix rot" in zeile, (
        f"{rel}: Die Smoke-Auflage kennt den Fall 'schon vorher rot' nicht. "
        f"Sie misst dann eine Eigenschaft der MASCHINE statt eine des Fixes "
        f"und trifft den Lauf, in dem Frank richtig gearbeitet hat.")


@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_die_auflage_verlangt_BEIDE_staende(rel):
    """Die Differenz braucht zwei Messpunkte, sonst ist sie keine.

    Frank kennt seinen Ausgangs-Commit ueber `team_guard_begin` ohnehin — die
    Faehigkeit ist da, sie brauchte nur die Auflage.
    """
    zeile = _smoke_suffix(rel)
    assert "beide Staende" in zeile or "beide Stände" in zeile, (
        f"{rel}: Die Auflage nennt die zwei Messpunkte nicht.")
    assert "NEUER" in zeile, (
        f"{rel}: Ohne das Wort 'neu' bleibt die Auflage absolut — genau der "
        f"Zustand vor BL-205.")


@pytest.mark.parametrize("rel", BIBLIOTHEKEN)
def test_die_vordergrund_auflage_bleibt_daneben_stehen(rel):
    """Die Gegenrichtung: BL-205 darf BL-207/BL-201 nicht verdraengen.

    Beide Auflagen sitzen in derselben Zeile. Ein Zusatz, der die aeltere
    dabei herausdraengt, tauscht einen Fehler gegen einen anderen.
    """
    zeile = _smoke_suffix(rel)
    assert "VORDERGRUND" in zeile, (
        f"{rel}: Die Vordergrund-Auflage ist aus SMOKE_SUFFIX verschwunden "
        f"(BL-207/BL-201).")
    assert "TEAM_SMOKE_TEST_TIMEOUT" in zeile, (
        f"{rel}: Der Zeitwert aus BL-207 ist verschwunden — ohne ihn ist die "
        f"Vordergrund-Auflage bei langer Suite unerfuellbar.")


# --- (2) Der dritte Ausgang: Beifang gehoert ins Beutebuch -------------------

@pytest.mark.parametrize("rel", EINSTIEGE)
def test_frank_darf_einen_neuen_fund_als_offen_eintragen(rel):
    """*Finder ist nicht Fixer* — bestaetigt statt verletzt.

    Frank kannte zwei Ausgaenge. Fuer den dritten — Hindernis, aber ein echter
    neuer Fehler unterwegs — gab es keinen, und der Beifang landete im
    gitignorierten Log. Ein neuer Fundblock mit Status `offen` ist genau der
    Weg, der die Rollentrennung ACHTET: eintragen ja, beheben nein.
    """
    text = _lies(rel)
    assert "Fundblock" in text, (
        f"{rel}: Franks Auftrag kennt den dritten Ausgang nicht — ein "
        f"unterwegs gefundener zweiter Fehler ist damit wieder verloren.")
    assert "'offen'" in text or "‚offen‘" in text or "offen'" in text, (
        f"{rel}: Der Status des neuen Fundblocks steht nicht da. Ohne ihn "
        f"traegt Frank ihn womoeglich als erledigt ein.")
    assert "fixt ihn NICHT" in text or "fixe ihn NICHT" in text, (
        f"{rel}: Der Auftrag sagt nicht, dass Frank den Beifang NICHT selbst "
        f"behebt — das waere die Rollentrennung, die der Zusatz bestaetigen "
        f"soll, genau verletzt.")


# --- (3) Es liest niemand mit ------------------------------------------------

@pytest.mark.parametrize("rel", EINSTIEGE)
def test_frank_weiss_dass_niemand_mitliest(rel):
    """Zwei Rueckfragen an einen Menschen, den es headless nicht gibt.

    Der teuerste Teil des Vorfalls: 2,7517 USD verworfen und im Folgeaufruf
    neu bezahlt. Die Rolle hatte inhaltlich alles richtig gemacht.
    """
    text = _lies(rel)
    assert "liest niemand mit" in text, (
        f"{rel}: Franks Auftrag sagt nicht, dass die Sitzung headless ist.")
    assert "KEINE Rückfragen" in text or "KEINE Rueckfragen" in text, (
        f"{rel}: Der Auftrag untersagt Rueckfragen nicht ausdruecklich.")
    assert "entscheide belegbar" in text, (
        f"{rel}: Ein blosses Verbot laesst die Rolle ratlos zurueck — es "
        f"fehlt, WAS sie stattdessen tun soll.")


# --- Gleichstand der Bahnen --------------------------------------------------

def test_beide_bahnen_sagen_dasselbe():
    """Sonst bedeutet der Fix auf den zwei Bahnen verschieden viel — die
    Gattung von BL-145, an der dieses Kit oft genug haengt."""
    texte = [_lies(rel) for rel in EINSTIEGE]
    for satz in ("liest niemand mit", "Fundblock", "entscheide belegbar"):
        assert all(satz in t for t in texte), (
            f"Der Satz „{satz}“ steht nur in EINEM der beiden "
            f"Frank-Entrypoints.")
    zeilen = [_smoke_suffix(rel) for rel in BIBLIOTHEKEN]
    assert all("VOR deinem Fix rot" in z for z in zeilen), (
        "Die Differenzmessung steht nur auf EINER Bahn.")

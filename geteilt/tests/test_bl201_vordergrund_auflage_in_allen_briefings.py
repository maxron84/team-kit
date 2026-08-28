#!/usr/bin/env python3
"""Regressionstest fuer BL-201: Die Vorsorge gegen den vierten Ausgang erreicht
JEDE der fuenf Loop-Rollen — und die Nachsorge behauptet nicht mehr, als sie
weiss.

VIER ROLLEN BEKOMMEN SIE IM BRIEFING, FRANK ZUR LAUFZEIT. Das ist keine
Nachlaessigkeit, sondern eine Abwaegung gegen eine zweite Zusicherung: Sein
Briefing liegt exakt auf dem harten 45-Zeilen-Limit, und er traegt die Auflage
seit BL-207 ohnehin woertlich in Schritt 1 seines Auftrags. Beide Haelften sind
hier festgehalten, damit die Ausnahme kein Loch wird.

DER BEFUND, gemessen statt vermutet: Eine Suche nach `Vordergrund`,
`Hintergrund`, `Wakeup`, `Monitor` oder `43` ueber
`geteilt/prompts/rolle-{ralph,frank,axel,harry,marv}.md` lieferte **0 Treffer
in allen fuenf**. Das Kit kannte den vierten Ausgang ausschliesslich als
NACHSORGE (`BL-41` erkennt ihn zuverlaessig); die vorbeugende Auflage stand in
der `CLAUDE.md`-Vorlage — also in einem Abschnitt, der der Rolle einleitend
sagt, er betreffe groesstenteils die Shell und nicht sie.

DIE DOKU-HYGIENE DIESES KITS sieht die Briefings ausdruecklich als den Weg vor,
auf dem eine Rolle ihre Auflagen erhaelt. Eine Auflage, die nur woanders steht,
ist keine.

DER PREIS, zweimal gemessen:
  * bauende Rolle: viermal im Feld, zusammen 19,47 USD;
  * fixende Rolle: von 28 Frank-Laeufen endeten 10 ohne Promise, bei **9**
    davon stand im Log-Feld `result` woertlich das Warten auf einen
    Hintergrundlauf. Summe der neun vergeblichen Aufrufe: 10,7249 USD an EINEM
    Tag. Die Korrelation ist vollstaendig — kein einziger erfolgreicher Lauf
    zeigt dieses Muster.

FRANK IST HAERTER BETROFFEN ALS RALPH, und daraus folgt ein eigener
Schadenspfad: Bei Ralph kostet der vierte Ausgang eine Stufe. Bei Frank zaehlt
er zusaetzlich als Fehlversuch (`.frank-attempts`) und eskaliert den Fund ab
drei Fehlversuchen an Axel — das teure Modell wird also fuer einen Formfehler
gerufen, an einem Fund, an dem Frank inhaltlich nie gescheitert ist.
"""
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
# FRANK STEHT BEWUSST NICHT IN DIESER LISTE, und der Grund ist gemessen:
# Er bekommt die Auflage seit BL-207 WOERTLICH zur Laufzeit, ueber
# $SMOKE_SUFFIX in Schritt 1 seines Auftrags — genau weil er den Smoke-Test
# oefter faehrt als Ralph. Sein Briefing liegt zugleich exakt auf dem harten
# Limit von 45 Zeilen (`test_stufe90_briefings.py`), und das Limit ist keine
# Formsache: Ein Briefing liegt in JEDEM Prompt seiner Rolle, jede Zeile wird
# bei jedem Aufruf bezahlt. Ein Zusatz, der eine andere Zusicherung bricht,
# ist keiner — dieselbe Abwaegung, die `test_bl165` fuer BL-167 schon einmal
# getroffen hat. Dass er sie TROTZDEM hat, sichert der eigene Fall unten.
ROLLEN = ("ralph", "axel", "harry", "marv")


def _briefing(rolle):
    for kandidat in (WURZEL / "geteilt" / "prompts" / f"rolle-{rolle}.md",
                     WURZEL / "team" / "prompts" / f"rolle-{rolle}.md"):
        if kandidat.is_file():
            return kandidat.read_text(encoding="utf-8")
    pytest.skip(f"rolle-{rolle}.md liegt hier nicht")


def _absatz(rolle):
    """Der EINE Absatz mit der Auflage — nicht die ganze Datei.

    Bauart aus BL-193: Wer den Abschnitt prueft statt den Absatz, bekommt
    gruene Gegenproben geschenkt, weil die gesuchten Woerter anderswo in der
    Datei ohnehin vorkommen. Das hat dort einen Anlauf gekostet.
    """
    t = _briefing(rolle)
    marke = "Lange Befehle laufen im VORDERGRUND"
    assert marke in t, (
        f"BL-201: rolle-{rolle}.md nennt die Vordergrund-Auflage nicht. Die "
        f"Rolle erfaehrt sie damit nur ueber einen Abschnitt, der ihr sagt, "
        f"er betreffe sie groesstenteils nicht — und laeuft regelmaessig in "
        f"den vierten Ausgang (19,47 USD bei Ralph, 10,72 USD an EINEM Tag "
        f"bei Frank).")
    anfang = t.index(marke)
    ende = t.find("\n**", anfang + len(marke))
    return t[anfang:ende if ende != -1 else len(t)]


# --- Teil (1): die Auflage steht in allen fuenf ------------------------------

@pytest.mark.parametrize("rolle", ROLLEN)
def test_jedes_loop_briefing_traegt_die_auflage(rolle):
    """Alle fuenf, nicht nur `rolle-ralph.md`.

    Die Erstmeldung nannte nur Ralph. Der Nachtrag aus dem Feld hat den Umfang
    korrigiert: 0 Treffer in ALLEN fuenf, und Frank ist der haerter
    betroffene. Ein Fix, der nur die meldende Rolle bedient, laesst den
    teureren Fall stehen.
    """
    absatz = _absatz(rolle)
    assert "Hintergrund-Task" in absatz, (
        f"rolle-{rolle}.md verbietet den Hintergrund-Task nicht beim Namen.")
    assert "Wakeup" in absatz and "Monitor" in absatz, (
        f"rolle-{rolle}.md nennt nicht beide Bauformen. Im Feld wurde der "
        f"Fall dreimal verschieden formuliert; wer nur eine verbietet, "
        f"bekommt die andere.")


@pytest.mark.parametrize("rolle", ROLLEN)
def test_die_auflage_nennt_den_grund_statt_nur_das_verbot(rolle):
    """Eine Auflage ohne Grund ist die erste, die beim Kuerzen faellt.

    Der Grund ist der Kern des Falls: Die Sitzung ist headless, es kommt keine
    Benachrichtigung, und das Log meldet den Abbruch als ERFOLG.
    """
    absatz = _absatz(rolle)
    assert "headless" in absatz, (
        f"rolle-{rolle}.md sagt nicht, WARUM — ohne 'headless' liest sich die "
        f"Auflage wie eine Stilfrage.")
    assert "subtype: success" in absatz or "subtype=success" in absatz, (
        f"rolle-{rolle}.md nennt den taeuschenden Ausgang nicht. Genau er "
        f"macht den Fall teuer: Das Log sieht aus wie ein Erfolg.")


@pytest.mark.parametrize("rolle", ROLLEN)
def test_die_auflage_bietet_den_AUSWEG_statt_nur_das_verbot(rolle):
    """Der Punkt, an dem BL-207 und BL-201 sich beruehren.

    Eine Auflage, die eine Rolle nicht einhalten KANN, erzeugt genau das
    Verhalten, das sie verbieten soll: Reisst die Suite die
    Vordergrundgrenze des Werkzeugs, ist der Hintergrundlauf der einzige
    sichtbare Ausweg. Deshalb muss danebenstehen, dass das ZEITLIMIT
    hochgesetzt wird — und woher der Wert kommt.
    """
    absatz = _absatz(rolle)
    assert "TEAM_SMOKE_TEST_TIMEOUT" in absatz, (
        f"rolle-{rolle}.md nennt den konfigurierten Zeitwert nicht. Ohne ihn "
        f"ist die Auflage bei einer langen Suite unerfuellbar (BL-207).")
    assert "Zeitlimit" in absatz, (
        f"rolle-{rolle}.md sagt nicht, dass das Zeitlimit erhoeht wird.")


@pytest.mark.parametrize("rolle", ROLLEN)
def test_die_auflage_nennt_den_gemessenen_preis(rolle):
    """Zahlen ueberzeugen, wo Regeln abprallen — und beide Zahlen sind
    gemessen, nicht geschaetzt."""
    absatz = _absatz(rolle)
    assert "19,47" in absatz or "10,72" in absatz, (
        f"rolle-{rolle}.md nennt keinen Feldbetrag.")


# --- Teil (2): die Nachsorge behauptet nicht mehr, als sie weiss -------------

@pytest.mark.parametrize("datei", ["bash/lib.sh", "pwsh/lib.psm1"])
def test_die_quittungsmeldung_weist_auf_das_feld_result(datei):
    """Der kuerzeste Weg zur richtigen Diagnose, und er kostet eine Zeile.

    Aufgeloest hat den Feldfall **allein** das Feld `result` im Lauf-Log —
    dort stand die Ursache woertlich. Die Anleitung erwaehnte es an keiner
    Stelle; der Mensch las stattdessen die Pruefreihenfolge, deren beide
    Zweige einen roten Baum voraussetzen, und der zweite haette eine fertige,
    bezahlte Stufe weggeworfen.
    """
    pfad = WURZEL / datei
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt hier nicht (Bahn abgewaehlt)")
    text = pfad.read_text(encoding="utf-8")
    block = text[text.index("STUFE FERTIG, QUITTUNG FEHLT"):]
    block = block[:2000]
    assert "result" in block, (
        f"{datei}: Die Meldung zum vierten Ausgang nennt das Feld `result` "
        f"nicht — den einzigen Ort, an dem im Feld die Ursache stand.")


@pytest.mark.parametrize("datei", ["bash/lib.sh", "pwsh/lib.psm1"])
def test_die_rot_meldung_der_selbstpruefung_ist_relativiert(datei):
    """Ein Befund, der als sicher gelesen wird, obwohl er es nicht ist.

    Im Feld meldete die Selbstpruefung „Smoke-Test ist ROT", obwohl der Baum
    gruen war — sie wertete den unfertigen Hintergrundlauf als roten Test.
    Wer das fuer bare Muenze nimmt, landet in einer Pruefreihenfolge, deren
    Zweig 2 („Stufe neu bauen") eine fertige, bezahlte Stufe wegwirft.

    ABGRENZUNG ZU BL-207: Dort geht es um einen erkannt PARALLELEN Lauf, der
    zu UNBEKANNT fuehrt. Hier bleibt der Befund rot — er wird nur nicht mehr
    als sicher ausgegeben.
    """
    pfad = WURZEL / datei
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt hier nicht (Bahn abgewaehlt)")
    text = pfad.read_text(encoding="utf-8")
    marke = "ist ROT."
    assert marke in text, f"{datei}: der Rot-Zweig der Selbstpruefung fehlt"
    block = text[text.index(marke):][:1400]
    assert "VORDERGRUND nachmessen" in block or "Miss im VORDERGRUND" in block, (
        f"{datei}: Die Rot-Meldung wird nicht relativiert. Sie misst dann "
        f"womoeglich den halben Zustand eines abgebrochenen Hintergrundlaufs "
        f"und liest sich trotzdem wie ein Urteil ueber den Code.")
    assert "result" in block, (
        f"{datei}: Die Rot-Meldung verweist nicht auf das Feld `result`.")


def test_beide_bahnen_sagen_dasselbe():
    """Gleichstand — sonst bedeutet der Fix auf den zwei Bahnen verschieden
    viel (die Gattung von BL-145, an der dieses Kit oft genug haengt)."""
    paare = []
    for datei in ("bash/lib.sh", "pwsh/lib.psm1"):
        pfad = WURZEL / datei
        if not pfad.is_file():
            pytest.skip("einbahnige Ablage — Gleichstand hier nicht pruefbar")
        paare.append(pfad.read_text(encoding="utf-8"))
    for satz in ("worauf sie gewartet hat",
                 "halben Zustand statt deinen Code"):
        assert all(satz in t for t in paare), (
            f"Der Satz „{satz}“ steht nur auf EINER Bahn.")


def test_frank_bekommt_die_auflage_zur_LAUFZEIT():
    """Die Gegenrichtung zur Ausnahme oben — ohne sie waere sie ein Loch.

    Frank fehlt in der Briefing-Liste, weil sein Auftrag die Auflage
    ausgeschrieben mitbringt. Faellt das weg, hat ausgerechnet die HAERTER
    betroffene Rolle sie nirgends: Von 28 Frank-Laeufen endeten 10 ohne
    Promise, bei 9 davon stand das Warten auf einen Hintergrundlauf woertlich
    im Log-Feld `result` — 10,7249 USD an EINEM Tag.
    """
    for datei in ("bash/lib.sh", "pwsh/lib.psm1"):
        pfad = WURZEL / datei
        if not pfad.is_file():
            continue
        text = pfad.read_text(encoding="utf-8")
        assert "SMOKE_SUFFIX" in text, f"{datei}: SMOKE_SUFFIX gibt es nicht mehr"
        block = text[text.index("SMOKE_SUFFIX"):][:2500]
        assert "VORDERGRUND" in block, (
            f"{datei}: Franks Auftrag traegt die Vordergrund-Auflage nicht "
            f"mehr — und sein Briefing nennt sie ebenfalls nicht (Limit).")
        assert "Hintergrund-Task" in block, (
            f"{datei}: Franks Auftrag verbietet den Hintergrund-Task nicht.")


def test_die_briefings_bleiben_unter_dem_zeilenlimit():
    """Die Zusicherung, die dieser Eintrag beim Bauen fast gerissen haette.

    Der erste Wurf haengte allen fuenf Briefings einen 13-zeiligen Absatz an
    und schob vier davon ueber das Limit. Eine Auflage, die eine andere
    Zusicherung bricht, ist keine Verbesserung — sie verschiebt nur die
    Kosten. Der Fall steht hier, damit die naechste Ergaenzung es sofort
    merkt statt erst im Suite-Lauf.
    """
    for rolle in ROLLEN + ("frank",):
        pfad = WURZEL / "geteilt" / "prompts" / f"rolle-{rolle}.md"
        if not pfad.is_file():
            pytest.skip("Briefings liegen hier nicht")
        n = len(pfad.read_text(encoding="utf-8").splitlines())
        assert n <= 45, (
            f"rolle-{rolle}.md hat {n} Zeilen (Limit 45). Jede Zeile wird "
            f"bei JEDEM Aufruf der Rolle bezahlt.")

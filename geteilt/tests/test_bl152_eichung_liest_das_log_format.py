#!/usr/bin/env python3
"""BL-152: Die Eichpruefung der Preistabelle konnte nie bestehen.

DER FEHLER
    `preise_nachrechnen()` reicht einen `modelUsage`-Eintrag an
    `_usage_addieren()` weiter. Die beiden Strukturen sehen sich aehnlich und
    kommen aus verschiedenen Quellen:

        Transkript  `usage`       snake_case  input_tokens, output_tokens,
                                              cache_read_input_tokens,
                                              cache_creation{...}
        headless    `modelUsage`  camelCase   inputTokens, outputTokens,
                                              cacheReadInputTokens,
                                              cacheCreationInputTokens

    Der Leser fragte nach snake_case, im Log stand camelCase. Jeder Kuebel
    blieb auf 0, `gerechnet` wurde 0.0000, und die Abweichung war IMMER exakt
    100 % — unabhaengig davon, ob die Preistabelle stimmte.

WAS DAS FUER DEN ANWENDER BEDEUTETE
    `sitzung-messen` meldete "Preistabelle stimmt nicht mehr: N von N
    nachgerechneten Laeufen weichen ab" und erklaerte die eigene, korrekt
    gemessene Zahl fuer UNGEEICHT. Die Warnung zeigte also genau dorthin, wo
    der Fehler nicht war, und riet von einer Buchung ab, die in Ordnung
    gewesen waere. Gefunden hat es jemand, der der Warnung nachging, statt sie
    zu befolgen.

WARUM ES NIEMANDEM AUFFIEL — UND DAS IST DER EIGENTLICHE FUND
    Es gab einen Test. `test_bl141_sitzung_messen.py` prueft die Eichung in
    vier Faellen, und alle vier waren gruen. Sie bauten ihre `modelUsage`-
    Fixture aber in der Sprache des LESERS (`input_tokens`), nicht in der des
    ECHTEN LOGS (`inputTokens`). Ein Test, der sein Testmaterial im Dialekt
    des Codes schreibt, prueft den Code gegen sich selbst — er hat die
    Fehlbuchung FESTGESCHRIEBEN, statt sie zu fangen. Dieselbe Bauart wie in
    BL-143, wo ein gruener Test `auth == "api"` festhielt.

    Die Lehre daraus steht im Fixture unten: Sie ist aus ECHTEN abgerechneten
    Laeufen genommen, nicht gebaut. Nur die Zahlenfelder — `total_cost_usd`
    und die vier Token-Zaehler je Modell —, kein Text, keine Pfade.

DIE 5m/1h-FRAGE, NACHGEMESSEN STATT ANGENOMMEN
    `modelUsage` traegt die Cache-Erstellung als EINE Summe, ohne die
    Aufteilung nach Laufzeit, die das Transkript hergibt. Die Saetze
    unterscheiden sich (Faktor 2,00 gegen 1,25), also braucht es eine Annahme.

    An 920 abgerechneten Laeufen aus vier Feldprojekten gemessen, zerfaellt das
    in zwei Gruppen:

        808 Abo-Laeufe           1h trifft, 5m nicht
        112 API-Fallback-Laeufe  110 mal 5m, 2 mal 1h

    Eine FESTE Annahme ist damit fuer eine der beiden Gruppen immer falsch.
    "Immer 1h" — der urspruengliche Vorschlag im Backlog — haette 110 von 920
    Laeufen als "Preistabelle veraltet" gemeldet: ein leiserer Fehlalarm als
    vorher, aber derselbe Fehler, und ein Waechter mit Fehlalarmen wird
    abgeschaltet (BL-14). Deshalb zaehlt die KLEINERE der beiden Abweichungen.

    Das ist keine Nachsicht: Die Annahme betrifft nur EINEN Kuebel, waehrend
    der Basispreis — um den es bei einer Preisaenderung geht — in allen
    steckt. Der Test unten misst genau das nach.
"""
import json
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]


def _kosten_modul():
    for kandidat in (WURZEL / "geteilt" / "tools", WURZEL / "team" / "tools"):
        if (kandidat / "kosten.py").is_file():
            sys.path.insert(0, str(kandidat))
            import kosten
            return kosten
    pytest.skip("kosten.py nicht in dieser Ablage")


kosten = _kosten_modul()


# --- Die Saetze, unter denen DIESE Laeufe abgerechnet wurden -----------------
# BL-166 hat hier eine Kopplung sichtbar gemacht, die vorher niemand sah:
# Dieser Test prueft, ob die Eichung das LOG-FORMAT richtig liest — und hing
# trotzdem an der aktuellen Preistabelle. Als `claude-sonnet-5` von 3.00 auf
# 2.00 gesenkt wurde (real, zwischen der Messung dieser Laeufe und dem
# 2026-08-24), fielen vier Faelle dieser Datei. Sie zeigten damit auf den
# Log-Leser, wo der Preis stand: genau die Bauart, vor der `BL-152` selbst
# warnt ("die Warnung zeigte dorthin, wo der Fehler nicht war").
#
# Die Zahlen im Fixture sind GEMESSEN und werden nicht angefasst — sie
# umzurechnen waere Erfindung, und ihr ganzer Wert liegt darin, dass sie es
# nicht sind. Stattdessen gilt fuer diese Datei der Satz, der zur Messzeit
# GALT. Der Test prueft damit wieder genau das, was sein Name sagt.
#
# Wer hier einen Satz eintraegt, sagt damit: "So wurde damals abgerechnet."
# Die AKTUELLE Tabelle steht in kosten.py und wird von
# test_bl166_preistabelle_nennt_den_satz.py geprueft.
SAETZE_ZUR_MESSZEIT = {
    "claude-sonnet-5": 3.00,
}


@pytest.fixture(autouse=True)
def _preise_zur_messzeit(monkeypatch):
    for modell, satz in SAETZE_ZUR_MESSZEIT.items():
        monkeypatch.setitem(kosten.PREIS_INPUT_USD_PRO_MTOK, modell, satz)


# --- Das Fixture: echte abgerechnete Laeufe ----------------------------------
# Aus vier Feldprojekten, ohne Text und ohne Pfade — nur `total_cost_usd` und
# die vier Token-Zaehler je Modell. Ausgewaehlt nach Vielfalt, nicht nach
# Passung: beide Lauf-Arten, drei Basispreise (Sonnet, Opus, Haiku), ein Lauf
# mit zwei Modellen, ein Lauf ohne jede Cache-Nutzung, ein Lauf unter einem
# Zehntelcent.
#
# Diese Zahlen sind GEMESSEN, nicht gerechnet. Genau darin liegt ihr Wert: Ein
# Fixture, das aus der Preistabelle abgeleitet waere, koennte die Tabelle nicht
# pruefen — es waere ein Kreisschluss, und der Vorlaeufer in bl141 war einer.
ECHTE_LAEUFE = [
    # Abo-Lauf, zwei Modelle, Cache-Erstellung als 1h abgerechnet
    (1.1828416000000002,
     {"claude-haiku-4-5-20251001": {"inputTokens": 780, "outputTokens": 26,
                                    "cacheReadInputTokens": 0,
                                    "cacheCreationInputTokens": 0},
      "claude-sonnet-5": {"inputTokens": 3548, "outputTokens": 11865,
                          "cacheReadInputTokens": 1955742,
                          "cacheCreationInputTokens": 67765}}),
    # API-Fallback, Cache-Erstellung als 5m abgerechnet — der Fall, an dem
    # eine feste 1h-Annahme scheitert
    (0.48738719999999996,
     {"claude-haiku-4-5-20251001": {"inputTokens": 781, "outputTokens": 31,
                                    "cacheReadInputTokens": 0,
                                    "cacheCreationInputTokens": 0},
      "claude-sonnet-5": {"inputTokens": 3098, "outputTokens": 6923,
                          "cacheReadInputTokens": 570699,
                          "cacheCreationInputTokens": 53894}}),
    # API-Fallback, der TROTZDEM 1h abrechnet — der Grund, warum die Laufart
    # nicht am Dateinamen erkannt werden darf
    (0.6107423000000001,
     {"claude-haiku-4-5-20251001": {"inputTokens": 779, "outputTokens": 24,
                                    "cacheReadInputTokens": 0,
                                    "cacheCreationInputTokens": 0},
      "claude-sonnet-5": {"inputTokens": 3734, "outputTokens": 10349,
                          "cacheReadInputTokens": 669561,
                          "cacheCreationInputTokens": 40423}}),
    # Opus 4.8 — ein dritter Basispreis
    (1.21583475,
     {"claude-haiku-4-5-20251001": {"inputTokens": 828, "outputTokens": 22,
                                    "cacheReadInputTokens": 0,
                                    "cacheCreationInputTokens": 0},
      "claude-opus-4-8": {"inputTokens": 3223, "outputTokens": 11410,
                          "cacheReadInputTokens": 956251,
                          "cacheCreationInputTokens": 69665}}),
    # Ein Lauf unter einem Zehntelcent, ganz ohne Cache. Die Pruefung ist
    # relativ, damit gerade solche Laeufe nicht in der Rundung verschwinden.
    (0.0012289999999999998,
     {"claude-haiku-4-5-20251001": {"inputTokens": 1094, "outputTokens": 27,
                                    "cacheReadInputTokens": 0,
                                    "cacheCreationInputTokens": 0}}),
]


def _logs_schreiben(tmp_path, laeufe):
    ordner = tmp_path / ".ralph-logs"
    ordner.mkdir(parents=True, exist_ok=True)
    for i, (usd, nutzung) in enumerate(laeufe):
        (ordner / f"stufe-{i}.json").write_text(
            json.dumps({"total_cost_usd": usd, "modelUsage": nutzung}),
            encoding="utf-8")
    return kosten.logs_einsammeln(str(tmp_path))


# --- Der Fund ----------------------------------------------------------------

def test_echte_laeufe_reproduzieren_die_preistabelle(tmp_path):
    """Der Kern. Vor dem Fix war die Abweichung bei JEDEM dieser Laeufe exakt
    100 %, weil jeder Token-Kuebel leer blieb."""
    befunde = kosten.preise_nachrechnen(_logs_schreiben(tmp_path, ECHTE_LAEUFE))
    assert len(befunde) == len(ECHTE_LAEUFE), (
        f"nicht jeder Lauf wurde als Eichpunkt erkannt: {len(befunde)} von "
        f"{len(ECHTE_LAEUFE)}")
    schief = [(b[0], b[1], b[2], b[3]) for b in befunde
              if b[3] > kosten.PREIS_TOLERANZ]
    assert not schief, (
        "Abgerechnete Laeufe werden als 'Preistabelle veraltet' gemeldet. "
        "Ist die Abweichung ueberall ~100 %, liest die Eichung das Log-Format "
        "nicht (BL-152); ist sie ~10 %, ist es die 5m/1h-Annahme; ab 20 % ist "
        f"die Tabelle wirklich veraltet.\n  {schief}")


def test_die_abweichung_ist_nicht_nur_klein_sondern_null(tmp_path):
    """Die schaerfere Fassung.

    `PREIS_TOLERANZ` ist ein Promille — grosszuegig genug, dass ein
    halbrichtiger Leser darunter durchrutschen koennte. Echte abgerechnete
    Laeufe reproduzieren sich exakt, und das ist die Zusicherung, die zaehlt.
    """
    befunde = kosten.preise_nachrechnen(_logs_schreiben(tmp_path, ECHTE_LAEUFE))
    schlimmste = max(b[3] for b in befunde)
    assert schlimmste < 1e-9, (
        f"groesste Abweichung {schlimmste:.2e} — echte Laeufe muessen sich auf "
        "Gleitkomma-Genauigkeit reproduzieren, nicht nur 'ungefaehr'")


def test_der_adapter_liest_camelcase_und_nicht_snake_case():
    """Die Ursache direkt, ohne den Umweg ueber die Eichung.

    Ohne diesen Fall koennte jemand den Adapter auf snake_case zuruecksetzen
    und das Fixture gleich mit — beide Tests oben blieben gruen.
    """
    kuebel = kosten._modelusage_kuebel(
        {"inputTokens": 10, "outputTokens": 20,
         "cacheReadInputTokens": 30, "cacheCreationInputTokens": 40},
        "cache_write_1h")
    assert kuebel["input"] == 10 and kuebel["output"] == 20, kuebel
    assert kuebel["cache_read"] == 30, kuebel
    assert kuebel["cache_write_1h"] == 40 and kuebel["cache_write_5m"] == 0, kuebel

    # Die Gegenrichtung: Der Transkript-Leser darf das Log-Format NICHT lesen.
    # Beide Leser zu koennen waere kein Fortschritt, sondern der naechste
    # stille Formatfehler — dann faellt niemandem mehr auf, wenn eine Struktur
    # an der falschen Stelle ankommt.
    fremd = kosten._tokenkuebel()
    kosten._usage_addieren(fremd, {"inputTokens": 10, "outputTokens": 20})
    assert fremd == kosten._tokenkuebel(), (
        "_usage_addieren liest jetzt auch camelCase. Zwei Leser fuer zwei "
        "Formate war der Punkt von BL-152.")


# --- Die Gegenprobe: bleibt der Waechter scharf? ------------------------------

# Was eine verstellte Preistabelle ausloesen MUSS. Die Zahl ist gemessen, nicht
# gewuenscht: dieselbe Rechnung an 920 Feld-Laeufen ergab 920/920 bei +5 % und
# 907..916 von 920 bei +/-20 %.
#
# Der Eintrag bei -20 % ist der interessante und steht deshalb ausgeschrieben
# hier statt in einer Fussnote: Dort rutscht EIN Lauf des Fixtures durch, und
# zwar der API-Fallback, der als 5m abgerechnet wurde. Mit der 1h-Annahme und
# einem um 20 % gesenkten Basispreis landet er zufaellig auf 0,1 % am
# abgerechneten Betrag. Das ist der Preis dafuer, die 5m/1h-Unbekannte zu
# beseitigen — er ist real, klein und geht in dieselbe Richtung wie die
# Feldmessung. Ihn zu verschweigen waere schlimmer als ihn zu tragen: Die
# Warnung feuert weiterhin, weil sie an "N von M weichen ab" haengt und nicht
# an "alle".
@pytest.mark.parametrize("faktor,name,mindestens", [
    (1.05, "+5 %", 5),
    (1.10, "+10 %", 5),
    (1.20, "+20 %", 5),
    (0.90, "-10 %", 5),
    (0.80, "-20 %", 4),
])
def test_eine_veraltete_preistabelle_wird_weiterhin_erkannt(
        tmp_path, faktor, name, mindestens, monkeypatch):
    """Ohne diese Haelfte waere der Fix ein Waechter, der nie anschlaegt.

    Verstellt wird der BASISPREIS, also das, was sich bei einer echten
    Preisaenderung aendert — nicht der Cache-Faktor, ueber den die Annahme
    laeuft.
    """
    verstellt = {k: v * faktor for k, v in
                 kosten.PREIS_INPUT_USD_PRO_MTOK.items()}
    monkeypatch.setattr(kosten, "PREIS_INPUT_USD_PRO_MTOK", verstellt)
    befunde = kosten.preise_nachrechnen(_logs_schreiben(tmp_path, ECHTE_LAEUFE))
    schief = [b for b in befunde if b[3] > kosten.PREIS_TOLERANZ]
    assert len(schief) >= mindestens, (
        f"Eine um {name} verstellte Preistabelle wurde nur bei "
        f"{len(schief)} von {len(befunde)} Laeufen bemerkt (erwartet: "
        f"mindestens {mindestens}). Die Wahl der guenstigeren Cache-Annahme "
        "darf den Waechter nicht weiter entschaerfen als gemessen.")


def test_beide_cache_laufzeiten_werden_gebraucht(tmp_path):
    """Der Beleg fuer die Entscheidung, die kleinere Abweichung zu nehmen.

    Im Fixture stecken beide Gruppen. Waere eine der Laufzeiten fest verdrahtet,
    fiele die jeweils andere Gruppe durch — und genau das haette der
    urspruenglich vorgeschlagene Fix ('immer 1h') im Feld getan: 110 von 920
    Laeufen als 'Preistabelle veraltet'.
    """
    treffer = {"cache_write_1h": 0, "cache_write_5m": 0}
    for usd, nutzung in ECHTE_LAEUFE:
        if not any(u.get("cacheCreationInputTokens") for u in nutzung.values()):
            continue      # ohne Cache-Erstellung sind beide Annahmen gleich
        for art in treffer:
            gerechnet = sum(
                kosten.kosten_aus_tokens(kosten._modelusage_kuebel(u, art),
                                         kosten.modell_basispreis(m))
                for m, u in nutzung.items())
            if abs(gerechnet - usd) / usd < 1e-9:
                treffer[art] += 1
    assert treffer["cache_write_1h"] and treffer["cache_write_5m"], (
        "Das Fixture belegt nicht mehr beide Laufzeiten — dann traegt die "
        f"Begruendung fuer die Wahl der kleineren Abweichung nicht: {treffer}")

#!/usr/bin/env python3
"""BL-317: `--addieren` ersetzte die Notiz der Ledger-Zeile — die Beschreibung
jeder Sitzung außer der letzten ging verloren.

WAS GEMELDET WURDE (`Feld F`, 2026-10-04)
    Ein Nachlauf mit `--akteur-abschluss roles … --addieren` hinterließ eine
    Zeile, die nur noch die Notiz des Nachtrags trug; die Beschreibung des
    Laufs war weg, Zahlen und Quellen stimmten. Im Ledger des Projekts standen
    danach elf Zeilen mit nur der letzten Buchung — die Architekten-Zeilen
    aller sieben Kaskaden, jede aus fünf bis acht Sitzungen — und vier mit
    doppeltem Vorspann ("Rollen: Rollen: …", "Bau: Bau: …").

WARUM NICHTS ANSCHLUG
    Beträge, Quellen und `--ledger-pruefen` blieben stimmig: Geprüft werden
    Zahlen gegen Rohlogs, kein Text. Das Architekten-Briefing nennt die Notiz
    „die einzige Prosa-Spur je Ledger-Zeile" — und genau diese Spur ging beim
    Normalfall „Folgesitzung an derselben Kaskade" verloren.

Die Fälle fahren die Funktionen direkt, ohne Shell: Der Fehler sitzt in
`kosten.py`, beide Bahnen rufen dieselbe Stelle. Den Weg über
`team-status.sh --rollen-abschluss` hält `test_bl34` fest.
"""
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    monkeypatch.setenv("TEAM_DOMAENEN", "produkt team")
    pfad = tmp_path / ".budget-ledger"
    pfad.write_text(KOPF, encoding="utf-8")
    return pfad


def _notiz(pfad, rolle):
    zeilen = [z for z in kosten.ledger_zeilen(str(pfad)) if z["rolle"] == rolle]
    assert len(zeilen) == 1, f"genau eine {rolle}-Zeile erwartet: {zeilen}"
    return zeilen[0]["notiz"]


# --- Der Feldfall: Folgesitzungen an derselben Kaskade ----------------------

def test_der_architekt_behaelt_die_beschreibung_jeder_sitzung(ledger):
    """Drei Sitzungen an einer Kaskade, dreimal gebucht. Gegen den alten
    Stand gemessen: Danach stand nur noch die dritte Notiz da."""
    kosten.akteur_abschluss(4.10, "produkt", "7", "architekt", "abo",
                            notiz="Planung K7: Stufenschnitt", pfad=str(ledger))
    for notiz in ("Aushaertung K7 nach Sweep 1", "Closeout K7"):
        kosten.akteur_abschluss(1.25, "produkt", "7", "architekt", "abo",
                                notiz=notiz, pfad=str(ledger),
                                bestand="addieren")
    notiz = _notiz(ledger, "architekt")
    for teil in ("Planung K7: Stufenschnitt", "Aushaertung K7 nach Sweep 1",
                 "Closeout K7"):
        assert teil in notiz, (
            f"'{teil}' fehlt in der Notiz der Summenzeile — die Beschreibung "
            f"einer Sitzung ist verloren gegangen.\nNotiz: {notiz}")
    assert notiz.index("Planung") < notiz.index("Aushaertung") \
        < notiz.index("Closeout"), "die Reihenfolge der Sitzungen kippt"
    assert "addiert auf Bestand" in notiz


def test_ein_nachtrag_ohne_eigene_notiz_behaelt_die_alte(ledger):
    kosten.akteur_abschluss(2.0, "produkt", "7", "architekt", "abo",
                            notiz="Planung K7", pfad=str(ledger))
    kosten.akteur_abschluss(0.5, "produkt", "7", "architekt", "abo",
                            notiz="", pfad=str(ledger), bestand="addieren")
    notiz = _notiz(ledger, "architekt")
    assert "Planung K7" in notiz and "addiert auf Bestand" in notiz, notiz


def test_die_rollenzeile_behaelt_die_beschreibung_des_laufs(ledger):
    """Der Feldfall der Meldung: Nachlauf auf die Rollen-Zeile."""
    kosten.rollen_abschluss("7", 3.0, 0.0, domaene="produkt",
                            notiz="K7, Harry und Marv je 3 Sweeps",
                            pfad=str(ledger))
    kosten.rollen_abschluss("7", 0.75, 0.0, domaene="produkt",
                            notiz="Nachlauf Frank HM-12", pfad=str(ledger),
                            bestand="addieren")
    notiz = _notiz(ledger, "roles")
    assert "Harry und Marv je 3 Sweeps" in notiz, notiz
    assert "Nachlauf Frank HM-12" in notiz, notiz
    assert notiz.count("Rollen") == 1, (
        f"Der Vorspann steht im angehaengten Teil ein zweites Mal: {notiz}")


# --- Der doppelte Vorspann ---------------------------------------------------

@pytest.mark.parametrize("rolle,vorspann", [("roles", "Rollen"),
                                            ("ralph", "Bau")])
def test_eine_notiz_mit_vorspann_bekommt_ihn_nicht_zweimal(ledger, rolle,
                                                           vorspann):
    """Das Briefing zeigt die abgeleitete Form selbst (`Bau: K3 chat`), also
    schreibt der Architekt sie auch so."""
    kosten.rollen_abschluss("7", 1.0, 0.0, domaene="produkt",
                            notiz=f"{vorspann}: K7 Kameraführung",
                            pfad=str(ledger), rolle=rolle)
    notiz = _notiz(ledger, rolle)
    assert notiz.startswith(f"{vorspann}: K7 Kameraführung"), notiz
    assert f"{vorspann}: {vorspann}" not in notiz, notiz


def test_ein_fremder_vorspann_bleibt_stehen(ledger):
    """Die Gegenrichtung: Nur der EIGENE Vorspann wird nicht verdoppelt. Ein
    Text, der mit dem der anderen Zeile beginnt, ist Inhalt — BL-19 gibt die
    Zuordnung gerade deshalb je Zielrolle vor."""
    kosten.rollen_abschluss("7", 1.0, 0.0, domaene="produkt",
                            notiz="Bau: gehoert eigentlich zur anderen Zeile",
                            pfad=str(ledger))
    assert _notiz(ledger, "roles").startswith(
        "Rollen: Bau: gehoert eigentlich zur anderen Zeile")


# --- Gegenrichtungen ----------------------------------------------------------

def test_ersetzen_ersetzt_die_notiz_weiterhin(ledger):
    """`--ersetzen` ist die Korrektur einer FALSCHEN Altzeile — ihre Notiz
    zu behalten hiesse, die falsche Beschreibung weiterzutragen."""
    kosten.akteur_abschluss(9.99, "produkt", "7", "architekt", "abo",
                            notiz="Fehlmessung", pfad=str(ledger))
    kosten.akteur_abschluss(2.0, "produkt", "7", "architekt", "abo",
                            notiz="nachgemessen", pfad=str(ledger),
                            bestand="ersetzen")
    notiz = _notiz(ledger, "architekt")
    assert "Fehlmessung" not in notiz and "nachgemessen" in notiz, notiz


def test_eine_lange_notiz_wird_nicht_gekuerzt(ledger):
    """Abschneiden waere wieder stiller Verlust — eine lange Zeile ist ein
    sichtbarer Befund, eine gekuerzte nicht."""
    lang = "Sitzung " + "x" * 600
    kosten.akteur_abschluss(1.0, "produkt", "7", "architekt", "abo",
                            notiz=lang, pfad=str(ledger))
    kosten.akteur_abschluss(1.0, "produkt", "7", "architekt", "abo",
                            notiz="Closeout", pfad=str(ledger),
                            bestand="addieren")
    notiz = _notiz(ledger, "architekt")
    assert lang in notiz and "Closeout" in notiz


def test_die_summenzeile_bleibt_eine_zeile(ledger):
    """Die Haertung aus HM-36/HM-38 gilt auch fuer den angehaengten Teil."""
    kosten.akteur_abschluss(1.0, "produkt", "7", "architekt", "abo",
                            notiz="Planung", pfad=str(ledger))
    kosten.akteur_abschluss(1.0, "produkt", "7", "architekt", "abo",
                            notiz="Closeout | mit Pipe\nund Umbruch",
                            pfad=str(ledger), bestand="addieren")
    datenzeilen = [z for z in ledger.read_text(encoding="utf-8").splitlines()
                   if z and not z.startswith("#")]
    assert len(datenzeilen) == 1, datenzeilen
    # Sieben Felder plus das achte mit den Quellen der Summe (BL-298).
    assert len(datenzeilen[0].split("|")) == 8, datenzeilen[0]
    notiz = _notiz(ledger, "architekt")
    assert "Planung" in notiz and "Closeout / mit Pipe und Umbruch" in notiz


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

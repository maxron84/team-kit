#!/usr/bin/env python3
"""BL-116 — ein Transkript, zwei Closeouts: der zweite bucht die Summe beider.

Aus dem Feld zurueckgespielt (`team-kit_project_platformer`, dortiges
`BL-120`). Der Abo-Messweg misst das Sitzungstranskript. Wer zwei Kaskaden in
DERSELBEN Sitzung abschliesst, misst beim zweiten Closeout wieder das GANZE
Transkript — der bereits gebuchte Teil steckt darin und wandert ein zweites
Mal ins Ledger.

Warum keine der bestehenden Absicherungen anschlaegt, und warum das der
eigentliche Befund ist:

  * Die vierte Eigenschaft aus BL-33 ("ein Transkript je Aufruf") verbietet,
    MEHRERE Transkripte zu summieren — sie sagt nichts ueber EIN Transkript
    mit zwei Buchungspunkten.
  * Die Deduplikation ueber die Nachrichten-ID greift nicht: Jede Antwort der
    ersten Haelfte kommt genau EINMAL vor, nur eben bereits bezahlt.
  * Der A1-Kollisionsschutz greift nicht: Er schlaegt bei DERSELBEN Rolle +
    Kaskade an; hier entstehen zwei Kaskadennummern und damit zwei Zeilen,
    die jede fuer sich plausibel sind.

Das Kit besitzt das Messwerkzeug nicht (es liegt projektuebergreifend unter
`~/.claude/scripts/`), verlaesst sich aber darauf — dieselbe Zustaendigkeits-
lage wie bei BL-33. Der Entscheid ist deshalb derselbe: nicht das fremde
Skript einziehen, sondern die Eigenschaft benennen, die ein tauglicher
Messweg haben muss, plus die Anweisung, die den Fall gar nicht erst entstehen
laesst.

Dieser Test haelt die INSTALLIERTE Haelfte fest — das Briefing des
Architekten, das in jeder Installation liegt. Die Kit-Haelfte (`doku/anhang-a.md`,
A.9, fuenfte Eigenschaft) prueft das Regel-Inventar woertlich
(`kit-regelinventar.py`, Stufe 8 von `kit-test.sh`); ein zweiter Test darauf
waere in der Installation dauerhaft blind — die Bauart aus BL-58.
"""
from pathlib import Path

from conftest import kit_pfad

WURZEL = Path(__file__).resolve().parents[2]
BRIEFING = kit_pfad("prompts", "rolle-architekt.md")


def _briefing():
    return BRIEFING.read_text(encoding="utf-8")


def test_briefing_verlangt_eine_neue_sitzung_je_closeout():
    text = _briefing()
    assert "Ein Closeout je Sitzung" in text, (
        "Die Regel fehlt an der Stelle, an der gebucht wird — dann entsteht "
        "der Fall weiter, und nur das Nachrechnen faengt ihn."
    )
    assert "neue** Sitzung" in text or "neue Sitzung" in text, (
        "Die Regel sagt nicht, was stattdessen zu tun ist."
    )


def test_briefing_nennt_den_ausweg_fuer_den_ausnahmefall():
    """Eine Regel ohne Ausweg wird gebrochen, sobald sie im Weg steht — dann
    aber still. Der Ausweg macht den Bruch buchbar statt unsichtbar."""
    text = _briefing()
    assert "minus bereits gebucht" in text, (
        "Der Ausnahmefall (zweiter Closeout doch in derselben Sitzung) hat "
        "keinen benannten Weg."
    )
    assert "Notiztext" in text, (
        "Die Rechnung soll im Notiztext der Ledger-Zeile stehen — sonst ist "
        "der Abzug spaeter nicht nachvollziehbar."
    )


def test_briefing_begruendet_warum_es_nirgends_auffaellt():
    """Der teuerste Teil des Fundes ist nicht der Fehler, sondern seine
    Unsichtbarkeit. Ohne die Begruendung liest sich die Regel als Formalie —
    und Formalien werden weggelassen, wenn es eilt."""
    text = _briefing()
    assert "Kollisionsschutz" in text, (
        "Das Briefing sagt nicht, warum der vorhandene Schutz hier nicht "
        "greift — genau das macht den Fall teuer."
    )
    assert "verschiedener** Kaskadennummer" in text or "verschiedener Kaskadennummer" in text, (
        "Der Grund (zwei Kaskadennummern = zwei plausible Zeilen) fehlt."
    )

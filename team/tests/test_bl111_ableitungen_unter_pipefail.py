#!/usr/bin/env python3
"""BL-111 — Ableitungen aus der Plan-Datei duerfen unter VOLLER Strenge leer
zurueckkommen, ohne den Aufrufer wegzureissen.

`team_architekt_kaskade` beendete seine Pipeline mit `| head -1`, und der
Kommentar begruendete das woertlich damit, ein Projekt ohne erkennbare
Kaskade duerfe den Aufrufer "unter set -e nicht wegreissen". Das stimmt fuer
`set -e` und ist unter `set -o pipefail` WIRKUNGSLOS: Dort bestimmt der erste
fehlschlagende Teil den Status der Pipeline, also der leere `grep` (rc 1) —
egal was `head` zurueckgibt.

Der Befund war beim Schreiben des Backlog-Eintrags auf EINE Funktion
geschaetzt. Nachgemessen sind es DREI: `team_ralph_cap` und
`team_budget_empfehlung` haben dieselbe Bauart (`grep … | head -1 | cut`), und
bei beiden ist der Fall, den sie nicht ueberleben, ausdruecklich der
dokumentierte Normalfall — eine Plandatei ohne diese Zeile. Der Kommentar von
`team_budget_empfehlung` sagte sogar woertlich "kein Abbruch" zu.

Warum das mit `strikt=True` geprueft wird und nicht mit "abbruch": Genau die
Stufe ist der Unterschied. Alle bauenden und pruefenden Rollen (ralph, frank,
axel, harry, marv, redteam) laufen mit `set -euo pipefail`; `team-status.sh`
und die Automatiken mit `set -uo pipefail`. Ein Test auf der mittleren Stufe
waere gruen geblieben, waehrend die Zusicherung dort, wo sie gebraucht wird,
nicht gilt.

Gegenprobe eingebaut: Jede Funktion wird auch auf dem POSITIVEN Pfad gefahren.
Ein `|| true` an der falschen Stelle wuerde den Wert schlucken, und ein Test,
der nur "stirbt nicht" prueft, saehe das nicht.
"""
import shutil

import pytest

from conftest import FangUndMelde

OHNE_NUMMER = "plans/roles-post-k13.md"
MIT_NUMMER = "plans/ralph-kaskade-7-thema.md"


def _repo(tmp_path, schale, plan_datei, planinhalt=""):
    """Wegwerf-Projekt mit genau einer Plandatei und einem Zeiger darauf."""
    repo = tmp_path / "repo"
    (repo / "team").mkdir(parents=True)
    (repo / "plans").mkdir()
    shutil.copy(schale.kit_lib, repo / "team" / schale.lib_name)
    (repo / plan_datei).write_text(planinhalt, encoding="utf-8")
    (repo / ".ralph-plan").write_text(plan_datei + "\n", encoding="utf-8")
    return repo


def _lib(schale, repo):
    return repo / "team" / schale.lib_name


# ------------------------------------------------------- der Fall ohne Zeile
@pytest.mark.parametrize("funktion", [
    "team_architekt_kaskade",
    "team_ralph_cap",
    "team_budget_empfehlung",
])
def test_leere_ableitung_reisst_den_aufrufer_nicht_weg(tmp_path, schale, funktion):
    """Plandatei ohne Nummer, ohne RALPH_CAP, ohne BUDGET_EMPFEHLUNG_USD —
    also der dokumentierte Normalfall aller drei Funktionen."""
    repo = _repo(tmp_path, schale, OHNE_NUMMER,
                 planinhalt="# benannte Kaskade, keine der gesuchten Zeilen\n")
    ergebnis = schale.lauf(FangUndMelde(funktion), cwd=repo,
                           lib=_lib(schale, repo), strikt=True)
    assert ergebnis.returncode == 0, (
        f"{funktion} reisst den Aufrufer unter voller Strenge weg:\n"
        f"{ergebnis.stderr}"
    )
    assert "rc=0 wert=[]" in ergebnis.stdout, (
        f"{funktion} meldet nicht 'leer und still': {ergebnis.stdout!r}"
    )


# ------------------------------------------------- Gegenprobe: der Wert kommt an
@pytest.mark.parametrize("funktion,erwartet", [
    ("team_architekt_kaskade", "7"),
    ("team_ralph_cap", "12.50"),
    ("team_budget_empfehlung", "40.00"),
])
def test_vorhandener_wert_wird_weiterhin_geliefert(tmp_path, schale, funktion, erwartet):
    """Ohne diese Haelfte waere `funktion() { :; }` ein gruener Weg."""
    repo = _repo(tmp_path, schale, MIT_NUMMER,
                 planinhalt="RALPH_CAP=12.50\nBUDGET_EMPFEHLUNG_USD=40.00\n")
    ergebnis = schale.lauf(FangUndMelde(funktion), cwd=repo,
                           lib=_lib(schale, repo), strikt=True)
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert f"rc=0 wert=[{erwartet}]" in ergebnis.stdout, (
        f"{funktion} liefert den vorhandenen Wert nicht mehr: "
        f"{ergebnis.stdout!r}"
    )

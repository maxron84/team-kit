#!/usr/bin/env python3
"""BL-25/BL-26: Der Akteur-Abschluss darf eine bestehende Zeile nicht mehr
still ersetzen — und der Wrapper darf keine Schalter verschlucken.

BL-25 (Feld A, Lageaufnahme K9): `rollen-abschluss` bricht seit BL-5
bei bestehender Zeile ab und nennt Alt-, Neu- und Summenwert. `akteur-abschluss`
hatte dieselbe Ersetzungslogik OHNE diesen Schutzschalter. Im Feld stand die
Architektenzeile der Kaskade 9 auf 5,5515 USD; eine Folgesitzung an derselben
Kaskade buchte erneut und ersetzte sie — der erste Wert war weg, ohne Warnung.
Der Fall ist der Normalfall, nicht der Ausreisser: Wer vormittags aushaertet
und abends abschliesst, bucht zwangslaeufig zweimal.

BL-26 (Feld A, Zwischenstandssicherung vor K23): `team-status.sh
--akteur-abschluss` las nur $1…$5. `--kaskade vor-23` fiel damit weg, das
Werkzeug leitete die Nummer aus .ralph-plan ab und ersetzte die abgeschlossene
Architektenzeile der Kaskade 22 ueber 8,4678 USD. Verschaerfend: Ein veralteter
.ralph-plan-Zeiger ist nach jedem Closeout der Normalzustand.

Warum beide Faelle in EINER Datei stehen: Es sind zwei Haelften desselben
Buchungsverlusts — die eine im Kern, die andere in der Bedienoberflaeche. Ein
Fix ohne den anderen laesst den Verlust bestehen.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, kit_pfad, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

import os as _os
_dom = _os.environ.get("TEAM_DOMAENEN", "").replace(",", " ").split()
DOMAENE = _dom[0] if _dom else "produkt"

KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _ledger(tmp_path):
    pfad = tmp_path / ".budget-ledger"
    pfad.write_text(KOPF, encoding="utf-8")
    return str(pfad)


def _zeilen(pfad, rolle):
    return [z for z in kosten.ledger_zeilen(pfad) if z["rolle"] == rolle]


# --- BL-25: der Kern ---------------------------------------------------------

def test_zweiter_aufruf_bricht_ab_und_laesst_die_datei_unangetastet(tmp_path):
    pfad = _ledger(tmp_path)
    kosten.akteur_abschluss(5.5515, DOMAENE, "9", "architekt", "abo",
                             notiz="Aushaertung", pfad=pfad)
    vorher = Path(pfad).read_text(encoding="utf-8")

    with pytest.raises(ValueError) as fehler:
        kosten.akteur_abschluss(3.20, DOMAENE, "9", "architekt", "abo",
                                 notiz="Closeout", pfad=pfad)

    text = str(fehler.value)
    assert "5.5515" in text, "der Altwert muss in der Meldung stehen"
    assert "3.2000" in text, "der Neuwert muss in der Meldung stehen"
    assert "8.7515" in text, "die Summe muss in der Meldung stehen"
    assert "--addieren" in text and "--ersetzen" in text
    assert Path(pfad).read_text(encoding="utf-8") == vorher, \
        "bei Abbruch darf NICHTS geschrieben werden"


def test_addieren_summiert_die_folgesitzung(tmp_path):
    pfad = _ledger(tmp_path)
    kosten.akteur_abschluss(5.5515, DOMAENE, "9", "architekt", "abo", pfad=pfad)
    kosten.akteur_abschluss(3.20, DOMAENE, "9", "architekt", "abo",
                             pfad=pfad, bestand="addieren")
    zeilen = _zeilen(pfad, "architekt")
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == pytest.approx(8.7515)
    assert "5.5515" in zeilen[0]["notiz"], \
        "die Summenzeile muss den Bestand nennen, sonst ist sie nicht pruefbar"


def test_ersetzen_bleibt_der_korrekturweg(tmp_path):
    pfad = _ledger(tmp_path)
    kosten.akteur_abschluss(99.0, DOMAENE, "9", "architekt", "abo", pfad=pfad)
    kosten.akteur_abschluss(3.20, DOMAENE, "9", "architekt", "abo",
                             pfad=pfad, bestand="ersetzen")
    zeilen = _zeilen(pfad, "architekt")
    assert len(zeilen) == 1
    assert zeilen[0]["usd"] == pytest.approx(3.20)


def test_andere_rolle_derselben_kaskade_bleibt_unberuehrt(tmp_path):
    """Der Schutzschalter darf die bestehende Koexistenz nicht brechen:
    Frank- und Architekt-Zeile derselben Kaskade sind verschiedene Zeilen."""
    pfad = _ledger(tmp_path)
    kosten.akteur_abschluss(5.0, DOMAENE, "9", "architekt", "abo", pfad=pfad)
    kosten.akteur_abschluss(2.0, DOMAENE, "9", "frank", "abo", pfad=pfad)
    assert len(_zeilen(pfad, "architekt")) == 1
    assert len(_zeilen(pfad, "frank")) == 1


def test_architekt_abschluss_reicht_bestand_durch(tmp_path):
    """Der duenne Alias darf den Schalter nicht verlieren — der Architekt ist
    die Rolle, die am haeufigsten zweimal an derselben Kaskade bucht."""
    pfad = _ledger(tmp_path)
    kosten.architekt_abschluss(5.0, DOMAENE, "9", pfad=pfad)
    with pytest.raises(ValueError):
        kosten.architekt_abschluss(2.0, DOMAENE, "9", pfad=pfad)
    kosten.architekt_abschluss(2.0, DOMAENE, "9", pfad=pfad, bestand="addieren")
    assert _zeilen(pfad, "architekt")[0]["usd"] == pytest.approx(7.0)


def test_cli_bricht_ab_und_nennt_beide_auswege(tmp_path):
    pfad = _ledger(tmp_path)
    kosten._main(["akteur-abschluss", "--usd", "5.55", "--domaene", DOMAENE,
                  "--kaskade", "9", "--rolle", "architekt", "--auth", "abo",
                  "--pfad", pfad])
    rc = kosten._main(["akteur-abschluss", "--usd", "3.2", "--domaene", DOMAENE,
                       "--kaskade", "9", "--rolle", "architekt", "--auth", "abo",
                       "--pfad", pfad])
    assert rc == 1
    assert _zeilen(pfad, "architekt")[0]["usd"] == pytest.approx(5.55)

    rc = kosten._main(["akteur-abschluss", "--usd", "3.2", "--domaene", DOMAENE,
                       "--kaskade", "9", "--rolle", "architekt", "--auth", "abo",
                       "--addieren", "--pfad", pfad])
    assert rc == 0
    assert _zeilen(pfad, "architekt")[0]["usd"] == pytest.approx(8.75)


# --- BL-26: die Bedienoberflaeche -------------------------------------------

def _entrypoint(name):
    for kandidat in (REPO_ROOT / name,
                     REPO_ROOT / "bash" / "entry" / name,
                     REPO_ROOT / "pwsh" / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


TEAM_STATUS = _entrypoint("team-status.sh")
pytestmark = pytest.mark.skipif(TEAM_STATUS is None,
                                 reason="team-status.sh nicht gefunden")


def _wrapper_repo(tmp_path):
    (tmp_path / "team" / "tools").mkdir(parents=True)
    shutil.copy(TEAM_STATUS, tmp_path / "team-status.sh")
    shutil.copy(kit_pfad("lib.sh"), tmp_path / "team" / "lib.sh")
    shutil.copy(kit_pfad("tools", "kosten.py"),
                tmp_path / "team" / "tools" / "kosten.py")
    (tmp_path / "team.config.sh").write_text(
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        f'TEAM_DOMAENEN="{DOMAENE} team"\nexport TEAM_DOMAENEN\n',
        encoding="utf-8")
    (tmp_path / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    # Der Feldfall: Der Zeiger steht auf der ZULETZT abgeschlossenen Kaskade.
    (tmp_path / ".ralph-plan").write_text(
        "plans/ralph-kaskade-22-alt.md\n", encoding="utf-8")
    return tmp_path


def _status(repo, *args):
    return subprocess.run([BASH, "./team-status.sh", "--akteur-abschluss",
                           *args], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_wrapper_reicht_kaskade_durch_statt_auf_ralph_plan_zu_buchen(tmp_path):
    """Der Feldfall selbst: Mit --kaskade muss auf die GENANNTE Kaskade
    gebucht werden, nicht auf die aus .ralph-plan."""
    repo = _wrapper_repo(tmp_path)
    ergebnis = _status(repo, "architekt", "abo", "4.00", DOMAENE,
                       "Zwischenstand", "--kaskade", "vor-23")
    assert ergebnis.returncode == 0, ergebnis.stderr
    zeilen = _zeilen(str(repo / ".budget-ledger"), "architekt")
    assert len(zeilen) == 1
    assert zeilen[0]["kaskade"] == "vor-23", \
        "der Schalter wurde verschluckt — gebucht wurde auf .ralph-plan"


def test_wrapper_nimmt_einen_schalter_nicht_als_notiz(tmp_path):
    """Ohne Notiztext darf --kaskade nicht im Notizfeld landen."""
    repo = _wrapper_repo(tmp_path)
    ergebnis = _status(repo, "architekt", "abo", "4.00", DOMAENE,
                       "--kaskade", "vor-23")
    assert ergebnis.returncode == 0, ergebnis.stderr
    zeile = _zeilen(str(repo / ".budget-ledger"), "architekt")[0]
    assert zeile["kaskade"] == "vor-23"
    assert "--kaskade" not in zeile["notiz"]


def test_wrapper_meldet_unbekannten_schalter_statt_ihn_zu_schlucken(tmp_path):
    repo = _wrapper_repo(tmp_path)
    ergebnis = _status(repo, "architekt", "abo", "4.00", DOMAENE, "Notiz",
                       "--gibtsnicht")
    assert ergebnis.returncode != 0
    assert "unbekanntes Argument" in (ergebnis.stderr + ergebnis.stdout)
    assert not _zeilen(str(repo / ".budget-ledger"), "architekt")


def test_wrapper_bricht_bei_bestehender_zeile_ab(tmp_path):
    """BL-25 durch die Bedienoberflaeche hindurch — dort ist der Verlust
    im Feld eingetreten, nicht in der Python-Funktion."""
    repo = _wrapper_repo(tmp_path)
    _status(repo, "architekt", "abo", "5.5515", DOMAENE, "Aushaertung",
            "--kaskade", "9")
    ergebnis = _status(repo, "architekt", "abo", "3.20", DOMAENE, "Closeout",
                       "--kaskade", "9")
    assert ergebnis.returncode != 0
    assert "--addieren" in (ergebnis.stderr + ergebnis.stdout)
    zeilen = _zeilen(str(repo / ".budget-ledger"), "architekt")
    assert zeilen[0]["usd"] == pytest.approx(5.5515)

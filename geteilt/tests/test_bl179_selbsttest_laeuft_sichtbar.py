#!/usr/bin/env python3
"""BL-179: Auch die SELBSTTESTS liefen stumm — der laengste Lauf des Kits am
laengsten.

WAS BL-176 OFFEN GELASSEN HAT
    `BL-176` hat die Suite-Laeufe der beiden INSTALLER sichtbar gemacht: roh
    ins Log, eingerueckt auf den Bildschirm. Die Selbsttests blieben uebrig,
    und dort wiegt derselbe Fehler schwerer:

      * `kit-test.ps1` faehrt die Suite einmal direkt — rund 14 Minuten still.
      * `kit-test.sh` faehrt sie in Stufe 8 zweimal. Stufe 8 ist mit rund
        55 Minuten die schwerste des Selbsttests (gemessen 2026-08-25).

    Ein stummer Lauf ist von einem HAENGENDEN nicht zu unterscheiden. Genau
    diese Frage — „haengt das?" — hat `BL-176` ausgeloest, und die teure
    Antwort darauf ist der Abbruch: Er wirft einen gesunden Lauf weg, der nur
    Geduld gebraucht haette, und beim Selbsttest sind das Stunden.

WARUM DIESER TEST DIE GATTUNG PRUEFT
    Eine Liste der drei bekannten Stellen waere ab der naechsten neuen falsch
    (`BL-154`) — dieselbe Erwaegung wie bei `BL-162`. Geprueft wird deshalb die
    BAUART: Kein Selbsttest darf einen pytest-Lauf VOLLSTAENDIG in eine Datei
    umleiten, ohne ihn zugleich zu zeigen.

    Ausgenommen sind Umleitungen, die ein TRANSKRIPT einfangen — `kit-test.ps1`
    faengt die Ausgabe der Installer mit `*> $installLog`, und das ist Absicht:
    Ein Lauf mit 17 Installer-Aufrufen wuerde das Terminal sonst fluten. Der
    Unterschied ist nicht die Technik, sondern wer zusieht: Ein Transkript wird
    NACH dem Lauf gelesen, ein Fortschritt WAEHREND.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Die Selbsttests beider Bahnen und die beiden Installer — ueberall dort faehrt
# eine Suite, der jemand zusieht.
LAEUFER = ("bash/kit-test.sh", "pwsh/kit-test.ps1",
           "bash/install.sh", "pwsh/install.ps1")

# Eine pytest-Zeile, deren Ausgabe VOLLSTAENDIG in eine Datei geht:
#   pwsh:  ... -q team/tests *> $log       (alle Stroeme)
#   bash:  ... -q team/tests > log 2>&1    (stdout + stderr)
# `tee` faengt der Ausdruck bewusst nicht — dort geht die Ausgabe weiter.
UMLEITUNG = re.compile(r"\*>\s*\$?[\w'\"./-]|>\s*[\"'$./\w-]+\s+2>&1")

# WAS EINEN LAUF VON EINER PROBE UNTERSCHEIDET, IST DAS ZIEL
#   Beide Installer und beide Selbsttests fragen zuerst, OB es pytest gibt
#   (`-m pytest --version >/dev/null 2>&1`, `command -v pytest`). Diese Ausgabe
#   gehoert weggeworfen — sie ist die Antwort auf eine Ja/Nein-Frage und dauert
#   Millisekunden. Ein LAUF nennt dagegen ein Testverzeichnis und dauert
#   Minuten.
#
#   Der erste Entwurf dieses Waechters hatte den Unterschied nicht und meldete
#   drei Proben als Befund. Ein Waechter, der an einer richtigen Stelle rot
#   schlaegt, wird abgeschaltet statt befolgt (`BL-143`) — die Unterscheidung
#   ist deshalb kein Feinschliff, sondern die Bedingung dafuer, dass er
#   ueberhaupt etwas wert ist.
ZIELORDNER = ("team/tests", "geteilt/tests")
# `--collect-only` zaehlt Faelle und wird AUSGEWERTET, nicht angesehen; es
# dauert Sekunden. `--version` ist die Probe von oben.
KEIN_LAUF = ("--collect-only", "--version")


def _ist_stummer_lauf(zeile):
    if "pytest" not in zeile:
        return False
    if any(w in zeile for w in KEIN_LAUF):
        return False
    if not any(o in zeile for o in ZIELORDNER):
        return False
    return bool(UMLEITUNG.search(zeile))


def _quelle(rel):
    p = REPO_ROOT / rel
    if not p.is_file():
        pytest.skip(f"{rel} liegt hier nicht (installiertes Projekt statt Kit-Ablage)")
    return p.read_text(encoding="utf-8-sig")


@pytest.mark.parametrize("rel", LAEUFER)
def test_kein_pytest_lauf_verschwindet_vollstaendig_im_log(rel):
    """Die Gattungspruefung. Sie nennt die Zeile, damit der Befund nicht
    gesucht werden muss."""
    treffer = []
    for nr, zeile in enumerate(_quelle(rel).splitlines(), start=1):
        nackt = zeile.strip()
        # Kommentarzeilen erklaeren die alte Bauart oft woertlich — sie sind
        # der Grund, warum die Stelle heute richtig ist, nicht ihr Rest.
        if nackt.startswith("#"):
            continue
        if _ist_stummer_lauf(zeile):
            treffer.append(f"{rel}:{nr}: {nackt}")
    assert not treffer, (
        "BL-179: Diese pytest-Laeufe verschwinden vollstaendig in einer Datei. "
        "Wer zusieht, sieht minutenlang nichts und kann einen laufenden Lauf "
        "nicht von einem haengenden unterscheiden:\n  " + "\n  ".join(treffer)
        + "\n\nBauart: roh ins Log, eingerueckt auf den Bildschirm — "
        "`| tee <log> | sed` bzw. `| Tee-Object -FilePath <log> | ForEach-Object`.")


@pytest.mark.parametrize("rel,marke", [
    ("bash/kit-test.sh", "suite_mitschnitt"),
    ("pwsh/kit-test.ps1", "Tee-Object"),
    ("bash/install.sh", "pytest_mitschnitt"),
    ("pwsh/install.ps1", "Pytest-Mitschnitt"),
])
def test_der_mitschnitt_ist_wirklich_da(rel, marke):
    """Gegenrichtung zur Gattungspruefung: Die haette man auch gruen bekommen,
    indem man den pytest-Lauf ganz entfernt."""
    assert marke in _quelle(rel), (
        f"{rel} fuehrt keinen Mitschnitt ({marke}). Die Gattungspruefung allein "
        "waere auch dann gruen, wenn der Lauf ersatzlos verschwaende.")


@pytest.mark.parametrize("rel", LAEUFER)
def test_der_puffer_ist_abgeschaltet(rel):
    """Ohne das wirkt der Mitschnitt nur halb: Schreibt Python nicht auf ein
    Terminal, sondern in eine Pipe, puffert es blockweise — die Zeilen kaemen
    in Schueben und der Haenger waere nur kuerzer geworden, nicht weg."""
    assert "PYTHONUNBUFFERED" in _quelle(rel), (
        f"{rel} schaltet den Python-Puffer nicht ab. In eine Pipe puffert "
        "Python blockweise; der Fortschritt kaeme dann praktisch erst am "
        "Schluss (BL-179).")


def test_das_transkript_der_installer_bleibt_bewusst_stumm():
    """Die Ausnahme, ausdruecklich unter Test: `kit-test.ps1` faengt die
    Ausgabe der Installer als TRANSKRIPT ein. Wuerde jemand die Gattungsregel
    auch darauf anwenden, flutete ein Lauf mit 17 Installer-Aufrufen das
    Terminal — und der Fortschritt, den BL-179 sichtbar machen soll, ginge
    darin unter. Ein Fix, der seinen eigenen Zweck erschlaegt."""
    quelle = _quelle("pwsh/kit-test.ps1")
    assert re.search(r"install\.ps1'\)[^\n]*\*>\s*\$\w*[Ll]og", quelle), (
        "Die Transkript-Umleitung der Installer-Aufrufe ist verschwunden. "
        "Sie ist Absicht (BL-179): Ein Transkript wird NACH dem Lauf gelesen, "
        "ein Fortschritt WAEHREND. Wurde sie durch einen Mitschnitt ersetzt, "
        "flutet der Selbsttest das Terminal.")

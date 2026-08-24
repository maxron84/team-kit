#!/usr/bin/env python3
"""BL-41: Die Smoke-Zeile muss Vordergrund-Betrieb verlangen.

Aus dem Feld zurueckgespielt (Feld A, K27/K28). Eine
bauende Rolle startete den Smoke-Test als HINTERGRUND-Task und wartete danach
auf eine Benachrichtigung, die in einer headless-Sitzung nie eintrifft. Der
Lauf endet mit subtype=success und is_error=false — er SIEHT AUS WIE EIN
ERFOLG —, gibt aber kein Promise und committet nicht. Dreimal passiert,
zusammen 13,25 USD, jedes Mal fuer Arbeit, die bereits fertig und gruen war.

Die zweite Instanz ist die lehrreiche: Dort ahnte die Rolle die Gefahr und
stellte sich zusaetzlich einen WAKEUP als Rueckfallebene — und wartete dann
auf beide Ereignisse, die headless nicht eintreten koennen. Eine Auflage, die
nur den Hintergrund-Task verbietet, faengt diesen Fall nicht. Deshalb prueft
dieser Test beide Verbote getrennt.

Warum der ausgewertete WERT geprueft wird und nicht der Quelltext: Die Zeile
wirkt nur, wenn sie im Prompt landet. Ein Kommentar ueber der Zuweisung sieht
im Diff genauso aus und trifft keine Rolle. Der Test sourcet lib.sh deshalb
wie eine Rolle es tut und liest SMOKE_ZEILE aus.

Zur Herkunft im Feld: Dort lag der Fix zunaechst nur als installierte Kopie
und haette kein `install.sh --update` ueberlebt (vgl. BL-12, wo genau so ein
lokaler Fix ueber 12,00 USD verloren ging). Dieser Test ist die Gegenprobe
dazu — er faellt, sobald die Auflage aus dem Kit verschwindet.
"""

from pathlib import Path

import pytest

from conftest import Variable, kit_pfad

WURZEL = Path(__file__).resolve().parents[2]
LIB = kit_pfad("lib.sh")


def _smoke_zeile(schale, smoke_test="./smoke.sh"):
    """Wertet die Bibliothek aus wie eine Rolle und liefert die SMOKE_ZEILE.

    Die Warnung ueber die fehlende team.config.sh (im Kit-Repo erwartet) geht
    nach stderr und stoert die Auswertung nicht mehr — frueher musste sie mit
    `2>/dev/null` weggeworfen werden, was auch echte Fehler verschluckt haette.
    """
    if not schale.kit_lib.is_file():
        pytest.skip(f"{schale.lib_name} nicht gefunden unter {schale.kit_lib}")
    fertig = schale.lauf(Variable("SMOKE_ZEILE"), cwd=WURZEL,
                         env={"TEAM_SMOKE_TEST": smoke_test})
    assert fertig.returncode == 0, \
        f"{schale.lib_name} nicht ladbar: {fertig.stderr}"
    return fertig.stdout


# Jedes Verbot einzeln: Der Hintergrund-Task ist der Erstfall, der Wakeup die
# Variante aus der zweiten Instanz. Wer nur eines von beiden schliesst, hat den
# Fehlermodus nicht geschlossen.
@pytest.mark.parametrize("brocken, warum", [
    ("VORDERGRUND", "die positive Auflage - was die Rolle TUN soll"),
    ("Hintergrund-Task", "der Erstfall aus K27/125"),
    ("Wakeup", "die Variante aus K28/133 - Rueckfallebene, die auch nie feuert"),
    ("headless", "die Begruendung; ohne sie liest sich die Regel als willkuerlich"),
])
def test_smoke_zeile_traegt_die_notbremse(brocken, warum, schale):
    zeile = _smoke_zeile(schale)
    assert brocken in zeile, (
        f"'{brocken}' fehlt in SMOKE_ZEILE ({warum}).\n"
        f"Ist:\n{zeile}")


# Der else-Zweig (kein Smoke-Test konfiguriert) wird hier nicht geprueft, und
# das ist eine Zustaendigkeitsfrage, keine Unmoeglichkeit mehr.
#
# BIS BL-149 STAND HIER ETWAS ANDERES, und es war eine Falschaussage geworden:
# "laesst sich von aussen nicht mehr erzwingen, weil eine Installation
# TEAM_SMOKE_TEST immer selbst setzt". Das stimmte — aber nur, WEIL der
# Installer eine nicht-leere Vorbelegung schrieb ("TODO: noch keiner …"). Der
# Zweig war unpruefbar, weil der Fehler ihn unerreichbar machte. Anders gesagt:
# Dieser Kommentar hat den Fund von BL-149 anderthalb Jahre lang beschrieben,
# ohne ihn zu erkennen, und ihn als Testluecke abgehakt.
#
# Die Lehre ist nicht "haetten wir es doch geprueft", sondern: Ein Satz "geht
# hier nicht" gehoert regelmaessig nachgeprueft. Er beschreibt eine Umgebung,
# und Umgebungen aendern sich — hier hat er sogar die Ursache benannt.
#
# Geprueft wird der Zweig jetzt in `test_bl149_platzhalter_ist_kein_befehl.py`,
# in einer Ablage OHNE team.config: Dann entscheidet allein die Umgebung, und
# der Test ist in beiden Ablagen gleich gueltig. Zum Fund BL-41 traegt er
# weiterhin nichts bei — ohne Smoke-Test gibt es keinen Hintergrund-Task, der
# die Sitzung beenden koennte —, deshalb liegt er dort und nicht hier.

#!/usr/bin/env python3
"""BL-15: Die ausgelieferte `Reproducer-Test`-Zeile muss anker-tauglich sein.

Aus dem Feld zurueckgespielt (dort BL-7, team-kit_project_platformer,
Kaskade 2 — real 12,00 USD an HM-4 verbrannt: 9 Frank-Versuche, 3 Axel-Akten,
keine Zeile Code ueberlebt, bei gruenem Smoke-Test und gueltigem Promise).

Das Kit lieferte die Zeile als
    - **Reproducer-Test**: tests/test_hm<nr>_<stichwort> (optional)
aus — zwei voneinander unabhaengige Defekte, von denen KEINER allein wirkt:

  (1) "optional"  => Harry/Marv lassen das Feld leer. Franks neue, regelkonform
      nach der Fund-Nummer benannte Testdatei ist damit im Fund-Block nie
      referenziert, und `team_diff_beruehrt_fund` rollt seinen Fix zurueck.
  (2) ohne Backticks => selbst ein AUSGEFUELLTES Feld bleibt unsichtbar, weil
      DATEI_RE ausschliesslich Backtick-Pfade liest.

BL-11 hat nur (2)s Schwesterproblem im Regex geloest: Der Extraktor KANN den
Pfad seither lesen — die Vorlage erzeugte nur nie einen. Dieser Test schliesst
die andere Haelfte: Er nimmt die WIRKLICH AUSGELIEFERTE Zeile, fuellt sie so
aus, wie die Vorlage es ansagt, und laesst DATEI_RE darauf los.

Geprueft wird an der Quelle, die das jeweilige Repo hat: im Kit die Vorlagen
unter bootstrap/, im installierten Projekt die substituierten Zieldateien.
"""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
TOOL = WURZEL / "team" / "tools" / "beutebuch.py"

# Die Feldmarke, an der die Vorlagenzeile haengt. Absichtlich eng: Fliesstext
# ueber die Zeile ("die `Reproducer-Test`-Zeile ist Pflicht") traegt die
# Doppel-Sternchen mit Doppelpunkt NICHT und wird so nicht mitgeprueft.
FELD = "**Reproducer-Test**:"

# So fuellt eine Rolle die Vorlage aus (Autoren-Platzhalter im Vorlagentext).
BEISPIEL = {"<nr>": "6", "<stichwort>": "stichwort"}

# Installer-Platzhalter werden ueber dieses Muster ersetzt, nicht ueber ein
# Literal. Grund: install.sh laesst am Ende pytest gegen die frische Installation
# laufen und legt dabei .pyc-Dateien an; kit-test.sh Stufe 3 durchsucht danach
# ALLES im Zielbaum nach uebrig gebliebenen Platzhaltern — auch den Bytecode.
# Ein Literal (auch ein zusammengesetztes, CPython faltet das beim Kompilieren)
# stuende dort und liesse diese Testdatei sich selbst als Fund melden.
INSTALLER_PLATZHALTER = re.compile(r"\{\{([A-Z_]+)\}\}")
ERSATZ = {"TEST_ORDNER": lambda: TEST_ORDNER}


def _lade_datei_re():
    spec = importlib.util.spec_from_file_location("beutebuch_bl15", TOOL)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul.DATEI_RE


def _config_wert(name, default):
    """Liest einen Ordner aus team.config.sh; im Kit steht dort ein Platzhalter."""
    cfg = WURZEL / "team.config.sh"
    if cfg.exists():
        treffer = re.search(
            rf'{name}="\$\{{{name}:-([^}}]*)\}}"', cfg.read_text(encoding="utf-8")
        )
        if treffer and treffer.group(1) and "{{" not in treffer.group(1):
            return treffer.group(1).rstrip("/") + "/"
    return default


TEST_ORDNER = _config_wert("TEAM_TEST_ORDNER", "tests/")
PLAN_ORDNER = _config_wert("TEAM_PLAN_ORDNER", "plans/")


def _quellen():
    """Die vier Dateien, die die Zeile ausliefern — Kit-Vorlage oder Zieldatei.

    Im Kit-Repo liegen Beutebuch und Regeldatei unter bootstrap/, im
    installierten Projekt unter dem Plan-Ordner bzw. als CLAUDE.md. Die
    Rollen-Briefings liegen in beiden Faellen am selben Ort.
    """
    paare = [
        ("Beutebuch-Vorlage",
         ["bootstrap/beutebuch.md", f"{PLAN_ORDNER}beutebuch.md"]),
        ("Regeldatei",
         ["bootstrap/CLAUDE.md.vorlage", "CLAUDE.md"]),
        ("Briefing Harry", ["team/prompts/rolle-harry.md"]),
        ("Briefing Marv", ["team/prompts/rolle-marv.md"]),
    ]
    gefunden = []
    for name, kandidaten in paare:
        for kandidat in kandidaten:
            pfad = WURZEL / kandidat
            if pfad.is_file():
                gefunden.append((name, pfad))
                break
        else:
            raise AssertionError(f"{name}: keine der Quellen existiert: {kandidaten}")
    return gefunden


def _ausgefuellt(zeile):
    """Substituiert Installer- und Autoren-Platzhalter wie im echten Gebrauch."""
    zeile = INSTALLER_PLATZHALTER.sub(
        lambda t: ERSATZ[t.group(1)]() if t.group(1) in ERSATZ else t.group(0), zeile
    )
    for platzhalter, wert in BEISPIEL.items():
        zeile = zeile.replace(platzhalter, wert)
    return zeile


def _feldzeilen(pfad):
    return [z for z in pfad.read_text(encoding="utf-8").splitlines() if FELD in z]


QUELLEN = _quellen()


@pytest.mark.parametrize("name, pfad", QUELLEN, ids=[n for n, _ in QUELLEN])
def test_quelle_liefert_die_zeile_ueberhaupt(name, pfad):
    """Eine still geloeschte Zeile ist derselbe Fund noch einmal."""
    assert _feldzeilen(pfad), (
        f"{name} ({pfad.relative_to(WURZEL)}) enthaelt keine "
        f"'{FELD}'-Zeile mehr — Harry/Marv bekommen das Feld nicht zu sehen."
    )


@pytest.mark.parametrize("name, pfad", QUELLEN, ids=[n for n, _ in QUELLEN])
def test_ausgelieferte_zeile_ist_fuer_datei_re_sichtbar(name, pfad):
    """Der eigentliche BL-15-Test: ausfuellen wie angesagt, dann extrahieren.

    Genau diese Pruefung haette den Fund verhindert. Sie schlaegt an, sobald
    jemand die Backticks entfernt oder den Pfad umbaut, bis der Extraktor ihn
    nicht mehr sieht — und damit, bevor der naechste Fix stillschweigend
    zurueckgerollt wird.
    """
    datei_re = _lade_datei_re()
    for zeile in _feldzeilen(pfad):
        treffer = datei_re.findall(_ausgefuellt(zeile))
        assert treffer, (
            f"{name} ({pfad.relative_to(WURZEL)}): DATEI_RE findet in der "
            f"ausgefuellten Zeile keinen Pfad — der Substanz-Anker wuerde "
            f"Franks Fix zurueckrollen.\n  Zeile: {zeile.strip()}"
        )
        assert any(t.endswith(".py") and t.startswith(TEST_ORDNER) for t in treffer), (
            f"{name} ({pfad.relative_to(WURZEL)}): extrahiert wurde {treffer}, "
            f"erwartet war ein .py-Pfad unter {TEST_ORDNER!r}."
        )


@pytest.mark.parametrize("name, pfad", QUELLEN, ids=[n for n, _ in QUELLEN])
def test_zeile_ist_nicht_als_optional_ausgewiesen(name, pfad):
    """Defekt (1): Solange das Feld 'optional' heisst, bleibt es leer.

    Der Wortstamm darf in der Zeile selbst nicht vorkommen. Dass ANLEGEN des
    Tests optional bleibt, steht im Fliesstext daneben — nicht im Feld.
    """
    for zeile in _feldzeilen(pfad):
        assert "optional" not in zeile.lower(), (
            f"{name} ({pfad.relative_to(WURZEL)}): Die Zeile ist wieder als "
            f"optional markiert.\n  Zeile: {zeile.strip()}"
        )


def test_gegenprobe_alte_vorlagenzeile_bleibt_unsichtbar():
    """Beweist, dass der Test scharf ist: die alte Fassung faellt durch.

    Ohne Backticks liefert DATEI_RE [] — und zwar auch dann, wenn das Feld
    brav ausgefuellt wurde. Das ist der Grund, warum die Prompt-Pflicht allein
    (Variante (b) ohne den Backtick-Zusatz) nichts bewirkt haette.
    """
    datei_re = _lade_datei_re()
    alt = f"- **Reproducer-Test**: {TEST_ORDNER}test_hm6_stichwort (optional)"
    assert datei_re.findall(alt) == []

    neu = f"- **Reproducer-Test**: `{TEST_ORDNER}test_hm6_stichwort.py`"
    assert datei_re.findall(neu) == [f"{TEST_ORDNER}test_hm6_stichwort.py"]


@pytest.mark.parametrize("rolle", ["harry", "marv"])
def test_briefing_stellt_die_zeile_als_pflicht_dar(rolle):
    """Die Zeile muss auch dann gesetzt werden, wenn die Datei noch fehlt.

    Sie ist keine Quittung ueber getane Arbeit, sondern eine Reservierung des
    Dateinamens fuer Frank — steht das nicht im Briefing, faellt die Rolle auf
    'ich habe keinen Test geschrieben, also lasse ich das Feld leer' zurueck.
    """
    text = (WURZEL / "team" / "prompts" / f"rolle-{rolle}.md").read_text(encoding="utf-8")
    assert "**Pflicht:**" in text, f"rolle-{rolle}.md kennzeichnet die Zeile nicht als Pflicht"
    assert "Backticks" in text, f"rolle-{rolle}.md verlangt die Backticks nicht ausdruecklich"


if __name__ == "__main__":
    fehler = []
    for name, pfad in QUELLEN:
        for pruefung in (
            test_quelle_liefert_die_zeile_ueberhaupt,
            test_ausgelieferte_zeile_ist_fuer_datei_re_sichtbar,
            test_zeile_ist_nicht_als_optional_ausgewiesen,
        ):
            try:
                pruefung(name, pfad)
                print(f"OK   {pruefung.__name__}[{name}]")
            except AssertionError as e:
                fehler.append(f"{pruefung.__name__}[{name}]")
                print(f"FAIL {pruefung.__name__}[{name}]: {e}")
    for pruefung, arg in (
        (test_gegenprobe_alte_vorlagenzeile_bleibt_unsichtbar, None),
        (test_briefing_stellt_die_zeile_als_pflicht_dar, "harry"),
        (test_briefing_stellt_die_zeile_als_pflicht_dar, "marv"),
    ):
        try:
            pruefung() if arg is None else pruefung(arg)
            print(f"OK   {pruefung.__name__}{'' if arg is None else '[' + arg + ']'}")
        except AssertionError as e:
            fehler.append(pruefung.__name__)
            print(f"FAIL {pruefung.__name__}: {e}")
    if fehler:
        sys.exit(1)
    print("gruen — BL-15 verifiziert: die ausgelieferte Zeile ist anker-tauglich.")

#!/usr/bin/env python3
"""BL-314: Der Waechter behauptet die Zuordnung, statt sie zu belegen.

DER HERGANG (`Feld B`/`Feld F`, 2026-10-04, beim Update zweier Projekte)
    `melde_veralteten_regeltext` meldete: *„Diese blanken Backlognummern
    meinen den KIT-Backlog: BL-115 BL-20 BL-25 HM-32"* — und riet:
    *„Kit- davorsetzen."*

    NACHGEZAEHLT an dem Projekt, aus dem die Meldung kam: Von den vier
    Nummern traf die Aussage bei EINER zu.

      * `BL-20`/`BL-25` — der Satz nennt seinen Traeger selbst
        (*„website-maxron-de 2026-07-11"*), ein DRITTES Projekt. Weder der
        Kit-Backlog (BL-20: Red-Team-Auftrag fuer statische Websites) noch
        der eigene (BL-20: Verifikationskette misst keine Kosten) fuehrt dort
        ein Session-Limit. Dem Rat zu folgen haette eine Aussage ueber den
        Kit-Backlog behauptet, die der Text selbst widerlegt.
      * `BL-115` — die EIGENE Nummer, und der Satz wendet die Regel
        VORBILDLICH an: *„`BL-115` entstanden und als `Kit-BL-49`/`Kit-BL-50`
        ans Kit gemeldet"*. Blank die eigene, mit Praefix die fremden. Genau
        diese Zeile stand in der Maengelliste.
      * `HM-32` — hier traf es zu: Das eigene `HM-32` ist ein
        Fixschritt-Akkumulator, das gemeinte der Budget-Fund des Kits.

    Die Ursache ist eine lexikalische Koinzidenz: Gemeldet wurde jede Nummer,
    die die Kit-Vorlage mit `Kit-` schreibt und die im Projekttext irgendwo
    blank vorkommt. Welchen TRAEGER die Stelle meint, entscheidet der Satz,
    in dem sie steht — und den las niemand.

DER WEG
    (1) Ein Satz, der daneben schon eine Nummer MIT `Kit-` schreibt, wird
        uebergangen: Dort unterscheidet der Autor nachweislich bewusst.
    (2) Was uebrig bleibt, wird nicht behauptet, sondern BELEGT — der
        Gegenstand im Kit und der im eigenen Backlog stehen daneben. Zuordnen
        tut der Mensch.
    (3) `HM-` wird im BEUTEBUCH nachgeschlagen, nicht im Backlog. Die alte
        Suche haette dort nie etwas gefunden und „keine solche Nummer"
        gemeldet — eine Aussage, die dann falsch ist.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad  # noqa: F401  (Pfadanker, s. REPO_ROOT)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _waechter_quelltext():
    """Der EINGEBETTETE Python-Block des Installers, woertlich.

    Nachgebaut wuerde hier sonst die Logik, nicht der Code — und ein Test,
    der seine eigene Nachbildung prueft, bleibt gruen, waehrend das
    Ausgelieferte kaputtgeht.
    """
    installer = REPO_ROOT / "bash" / "install.sh"
    if not installer.is_file():
        pytest.skip("install.sh liegt hier nicht (installiertes Projekt)")
    quelle = installer.read_text(encoding="utf-8-sig")
    m = re.search(r'"\$PYTHON" - "\$datei" .*?<<\'PY\'\n(.*?)\nPY\n', quelle, re.S)
    assert m, "Der eingebettete Waechter-Block ist nicht mehr auffindbar."
    return m.group(1)


def _lauf(claude_md, vorlage, kit):
    r = subprocess.run([sys.executable, "-c", _waechter_quelltext(),
                        str(claude_md), str(vorlage), str(kit)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return [z[len("BLANK "):] for z in r.stdout.splitlines()
            if z.startswith("BLANK ")]


def _welt(tmp_path, claude_text):
    """Ein Kit und ein Projekt, beide mit eigenen Eintraegen zu denselben Nummern."""
    kit = tmp_path / "kit"
    (kit / "bootstrap").mkdir(parents=True)
    (kit / "plans").mkdir()
    (kit / "bootstrap" / "CLAUDE.md.vorlage").write_text(
        "Siehe `Kit-BL-20`, `Kit-BL-115` und `Kit-HM-32`.\n", encoding="utf-8")
    (kit / "plans" / "backlog.md").write_text(
        "| Nr | Was |\n|---|---|\n"
        "| BL-20 | **Der Red-Team-Auftrag beschreibt eine statische Website** |\n"
        "| BL-115 | **Die Vorlage lehrt eine Statuszeile ohne Werkzeug** |\n",
        encoding="utf-8")
    (kit / "plans" / "beutebuch.md").write_text(
        "### HM-32 — Der Frank-Cap greift nach dem bezahlten Aufruf\n",
        encoding="utf-8")

    projekt = tmp_path / "projekt"
    (projekt / "plans").mkdir(parents=True)
    (projekt / "plans" / "backlog.md").write_text(
        "| Nr | Was |\n|---|---|\n"
        "| BL-20 | **Die Verifikationskette misst Korrektheit, nie Kosten** |\n"
        "| BL-115 | **Nichts pflegt die Stellen, die den Backlog zitieren** |\n",
        encoding="utf-8")
    (projekt / "plans" / "beutebuch-archiv.md").write_text(
        "### HM-32 — Fixschritt-Akkumulator waechst unbegrenzt\n", encoding="utf-8")
    (projekt / "CLAUDE.md").write_text(claude_text, encoding="utf-8")
    return projekt / "CLAUDE.md", kit / "bootstrap" / "CLAUDE.md.vorlage", kit


def test_der_satz_der_die_regel_vorbildlich_anwendet_wird_nicht_gemeldet(tmp_path):
    """Der teuerste Fehlalarm: Gemeldet wurde die Zeile, die es richtig macht."""
    claude, vorlage, kit = _welt(
        tmp_path,
        "Der Fund ist hier als `BL-115` entstanden und als `Kit-BL-49` ans "
        "Kit gemeldet worden.\n")
    assert _lauf(claude, vorlage, kit) == [], (
        "Ein Satz, der die eigene Nummer blank und die fremde mit `Kit-` "
        "schreibt, wendet die Regel an — er verletzt sie nicht.")


def test_eine_gemeldete_nummer_kommt_mit_beiden_gegenstaenden(tmp_path):
    """Belegen statt behaupten: Der Mensch sieht, womit es verwechselbar ist."""
    claude, vorlage, kit = _welt(
        tmp_path, "Ein Session-Limit (`BL-20`, website-maxron-de 2026-07-11).\n")
    zeilen = _lauf(claude, vorlage, kit)
    assert len(zeilen) == 1, zeilen
    nr, im_kit, bei_dir = zeilen[0].split("\t")
    assert nr == "BL-20"
    assert "statische Website" in im_kit, im_kit
    assert "Verifikationskette" in bei_dir, bei_dir
    assert "Session-Limit" not in im_kit + bei_dir, (
        "Die Gegenprobe des Tests selbst: Steht der Gegenstand des Satzes in "
        "einem der beiden Backlogs, ist das Beispiel schlecht gewaehlt.")


def test_eine_hm_nummer_wird_im_beutebuch_nachgeschlagen(tmp_path):
    """`HM-` steht im Beutebuch, nicht im Backlog — als Ueberschrift."""
    claude, vorlage, kit = _welt(
        tmp_path, "Realer Ausloeser HM-32, 2026-07-12.\n")
    zeilen = _lauf(claude, vorlage, kit)
    assert len(zeilen) == 1, zeilen
    nr, im_kit, bei_dir = zeilen[0].split("\t")
    assert nr == "HM-32"
    assert "Frank-Cap" in im_kit, (
        "Der Gegenstand im Kit fehlt — im Backlog gesucht statt im Beutebuch?")
    assert "Akkumulator" in bei_dir, (
        "Der eigene Gegenstand fehlt; die alte Fassung meldete hier 'keine "
        "solche Nummer', und das ist falsch.")


def test_der_waechter_behauptet_die_zuordnung_nicht_mehr():
    """Die Ausgabe ist eine Entscheidungshilfe, keine Anweisung."""
    # BL-323: In einer installierten Ablage gibt es keine Installer — ohne
    # diesen Uebersprung war der Fall dort rot statt uebersprungen, und der
    # Selbsttest am Ende jedes Updates meldete einen Fehler, den es nicht gab.
    installer = REPO_ROOT / "bash" / "install.sh"
    if not installer.is_file():
        pytest.skip("install.sh liegt hier nicht (installiertes Projekt)")
    quelle = installer.read_text(encoding="utf-8-sig")
    assert "meinen den KIT-Backlog" not in quelle, (
        "Der Waechter behauptet wieder, die Nummern meinten das Kit — bei "
        "drei von vier Feldfaellen war das falsch.")
    assert "Kit- davorsetzen." not in quelle, (
        "Die Anweisung ist zurueck. Sie war bei zwei von vier Feldfaellen "
        "sachlich falsch und bei einem das Gegenteil des Richtigen.")
    for satz in ("Meint sie DEINEN Backlog", "Meint sie ein DRITTES Projekt"):
        assert satz in quelle, f"Die Entscheidungshilfe nennt '{satz}' nicht."


@pytest.mark.parametrize("merkmal", [
    "function Gegenstand", "function Satz-Um", "beutebuch",
    "Meint sie ein DRITTES Projekt",
])
def test_die_pwsh_bahn_zieht_mit(merkmal):
    """Beide Bahnen oder keine — eine stillschweigend halbe ist der teure Fall."""
    installer = REPO_ROOT / "pwsh" / "install.ps1"
    if not installer.is_file():
        pytest.skip("install.ps1 liegt hier nicht (installiertes Projekt)")
    quelle = installer.read_text(encoding="utf-8-sig")
    assert merkmal in quelle, (
        f"Der pwsh-Bahn fehlt '{merkmal}' — der Waechter urteilt dort weiter "
        "nach der alten, dreimal widerlegten Form.")
    assert "meinen den KIT-Backlog" not in quelle

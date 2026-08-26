#!/usr/bin/env python3
"""BL-195: Der Selbsttest fuhr dieselbe Suite neunmal.

WAS GEMESSEN WURDE
    Beide Installer fahren am Ende ihres Laufs die volle Suite der Zielablage.
    Bei einer **Erstinstallation** ist das genau richtig: Der Anwender soll
    erfahren, ob das, was da eingezogen ist, auf seiner Maschine läuft.

    Im **Selbsttest des Kits** ist derselbe Lauf eine Wiederholung — dort ist
    der Installer kein Ereignis, sondern ein Werkzeug, das mehrfach betätigt
    wird. Gemessen am 2026-08-26 (`kit-test.ps1` nach `BL-145`): **19:20** je
    Durchgang in der installierten Ablage, **19:57** für den
    installer-internen. Neun Durchgänge je Lauf ergaben rund **2 h 55 min**
    reine Suite-Zeit, davon etwa zwei Stunden Wiederholung.

WARUM DAS MEHR IST ALS WARTEZEIT
    Ein Nachweis, der einen halben Arbeitstag kostet, wird nicht gefahren —
    und ein Selbsttest, den niemand fährt, ist genau der Zustand, den
    `BL-145` behoben hat. `BL-136`/`BL-144` blieben vier Commits lang
    unbemerkt, weil der teure Nachweis unterblieb. Die Laufzeit ist damit die
    Ursache hinter der Ursache.

DIE GRENZE DES FIXES — UND WARUM SIE DA IST
    Der erste Installer-Aufruf jeder Bahn behält seinen Regressionslauf.
    Dort hängt `BL-127`: *Der Selbsttest des Installers MUSS seine
    Regressionstests gefahren haben.* Ein Laufzeit-Schalter darf eine
    Zusicherung nicht aushebeln — er darf nur die Wiederholung abstellen.

    Und die Voreinstellung bleibt **fahren**. Ein Fix, der den Übersprung zur
    Voreinstellung machte, nähme dem Erstlauf seine einzige Prüfung; das wäre
    ein größerer Schaden als der behobene.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import BASH, nur_code, verlange_pwsh  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO_ROOT / "bash" / "install.sh"
INSTALL_PS1 = REPO_ROOT / "pwsh" / "install.ps1"
TEST_SH = REPO_ROOT / "bash" / "kit-test.sh"
TEST_PS1 = REPO_ROOT / "pwsh" / "kit-test.ps1"


def _lies(pfad):
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt in dieser Ablage nicht (nur im Kit)")
    return pfad.read_text(encoding="utf-8-sig")


# --- (1) Der Schalter existiert auf beiden Bahnen ----------------------------

@pytest.mark.parametrize("pfad,muster", [
    # Der Schalter muss ENTGEGENGENOMMEN werden, nicht bloss irgendwo im Text
    # vorkommen. Der erste Entwurf dieses Falls prüfte nur „steht drin" — und
    # blieb grün, als die Zeile aus der Argumentschleife verschwand, weil das
    # Wort in der Übersprungs-Meldung weiterlebte.
    ("bash/install.sh", r"--ohne-selbsttest\)\s+OHNE_SELBSTTEST=1"),
    ("pwsh/install.ps1", r"\[switch\]\$OhneSelbsttest"),
])
def test_beide_installer_NEHMEN_den_schalter_entgegen(pfad, muster):
    """Ohne ihn auf **beiden** Bahnen bliebe der teure Lauf auf einer davon —
    und die Doppelbahn hätte wieder zwei verschiedene Bedeutungen von
    „Selbsttest gelaufen"."""
    assert re.search(muster, nur_code(_lies(REPO_ROOT / pfad))), (
        f"BL-195: {pfad} nimmt den Schalter nicht entgegen. Gesucht: {muster}")


@pytest.mark.parametrize("pfad", ["bash/install.sh", "pwsh/install.ps1"])
def test_der_uebersprung_ist_laut(pfad):
    """Ein **stiller** Übersprung liest sich hinterher wie ein bestandener
    Nachweis. Das ist die Bauart, gegen die das halbe Kit geschrieben ist.

    Gezählt wird, nicht bloß gesucht: Jede Bahn hat **zwei** Stellen, an denen
    der Regressionslauf steht — Erstinstallation und Update. Eine Prüfung, die
    nur „kommt vor" fragt, bleibt grün, wenn eine der beiden verstummt. Genau
    das hat die Gegenprobe zu diesem Test gezeigt.
    """
    text = _lies(REPO_ROOT / pfad)
    assert text.count("AUF VERLANGEN uebersprungen") >= 2, (
        f"BL-195: {pfad} meldet den Uebersprung an weniger als beiden "
        f"Stellen ({text.count('AUF VERLANGEN uebersprungen')}). "
        "Erstinstallation UND Update brauchen ihn.")
    assert text.count("KEIN gruenes Ergebnis") >= 2, (
        f"BL-195: {pfad} ordnet den Uebersprung nicht an beiden Stellen ein. "
        "Wer die Zeile liest, muss wissen, dass hier eine PROBE FEHLT und "
        "nicht eine bestanden wurde.")


# --- (2) Die Grenze: BL-127 bleibt unangetastet ------------------------------

def test_der_erste_aufruf_behaelt_seinen_selbsttest_bash():
    """`BL-127` hält fest, dass der Selbsttest des **Installers** seine
    Regressionstests wirklich fährt. Genau dieser eine Aufruf darf den
    Schalter nicht bekommen — sonst prüft der Schritt darunter eine
    Zusicherung, die der Schritt darüber gerade abgestellt hat."""
    text = _lies(TEST_SH)
    zeilen = [z for z in text.splitlines()
              if 'bash "$KIT/bash/install.sh"' in z]
    assert zeilen, "BL-195: keine Installer-Aufrufe in kit-test.sh gefunden."
    erste = zeilen[0]
    assert "--ohne-selbsttest" not in erste, (
        "BL-195: Der ERSTE Installer-Aufruf laeuft ohne Regressionstests. "
        f"Dann prueft BL-127 nichts mehr:\n  {erste.strip()}")
    # Und die Zusicherung selbst muss noch dastehen.
    assert "Regressionstests grün" in text, (
        "BL-127: Die Pruefung, ob der Installer seine Tests gefahren hat, "
        "steht nicht mehr in kit-test.sh.")


def test_der_erste_aufruf_behaelt_seinen_selbsttest_pwsh():
    """Dieselbe Grenze auf der anderen Bahn — und dort ist die `BL-127`-Probe
    mit `BL-195` überhaupt erst entstanden. Bis dahin konnte ein Installer,
    der seine Tests still überspringt, auf dieser Bahn „Fertig" melden."""
    text = _lies(TEST_PS1)
    zeilen = [z for z in text.splitlines()
              if "install.ps1'" in z and "*>" in z]
    assert zeilen, "BL-195: keine Installer-Aufrufe in kit-test.ps1 gefunden."
    assert "-OhneSelbsttest" not in zeilen[0], (
        "BL-195: Der ERSTE Installer-Aufruf laeuft ohne Regressionstests. "
        f"Dann prueft BL-127 nichts mehr:\n  {zeilen[0].strip()}")
    assert "BL-127" in text, (
        "BL-127: Die Pruefung fehlt der pwsh-Bahn — genau die Luecke, die "
        "BL-145 fuer andere Stufen geschlossen hat.")


@pytest.mark.parametrize("pfad", ["bash/kit-test.sh", "pwsh/kit-test.ps1"])
def test_die_wiederholung_ist_wirklich_abgestellt(pfad):
    """Die Gegenrichtung: Ein Schalter, den niemand setzt, spart nichts. Die
    Zusicherung ist nicht „es gibt ihn", sondern „er wird benutzt"."""
    text = _lies(REPO_ROOT / pfad)
    marke = "--ohne-selbsttest" if pfad.endswith(".sh") else "-OhneSelbsttest"
    # Der Schalter am Aufruf, nicht in der Prosa.
    treffer = [z for z in text.splitlines()
               if marke in z and ("install.sh" in z or "install.ps1" in z)]
    assert len(treffer) >= 2, (
        f"BL-195: In {pfad} setzen nur {len(treffer)} Installer-Aufrufe den "
        "Schalter. Dann laeuft die Wiederholung weiter, und der Nachweis "
        "kostet weiter einen halben Arbeitstag.")


# --- (3) Die Voreinstellung bleibt „fahren" ----------------------------------

def test_ohne_schalter_faehrt_der_installer_seine_tests_bash():
    """Der wichtigste Fall, und er ist eine **Gegenprobe**: Ein Fix, der den
    Übersprung zur Voreinstellung machte, nähme dem Erstlauf seine einzige
    Prüfung. Gemessen wird die Vorbelegung im Quelltext, nicht geraten."""
    text = _lies(INSTALL_SH)
    treffer = re.findall(r"(?m)^OHNE_SELBSTTEST=(\d)", text)
    assert treffer == ["0"], (
        "BL-195: Die Vorbelegung von OHNE_SELBSTTEST ist nicht 0 — dann "
        f"ueberspringt JEDE Installation ihren Selbsttest. Gefunden: {treffer}")


def test_ohne_schalter_faehrt_der_installer_seine_tests_pwsh():
    """Dasselbe für PowerShell: Ein `[switch]` ist standardmäßig `$false`.
    Was hier geprüft wird, ist, dass er auch wirklich als `[switch]` steht und
    nicht als Parameter mit gesetztem Vorgabewert."""
    text = _lies(INSTALL_PS1)
    assert re.search(r"\[switch\]\$OhneSelbsttest", text), (
        "BL-195: OhneSelbsttest ist kein [switch] — ein Parameter mit "
        "Vorgabewert koennte den Uebersprung zur Voreinstellung machen.")
    assert not re.search(r"\$OhneSelbsttest\s*=\s*\$true", text), (
        "BL-195: OhneSelbsttest wird im Skript auf $true gesetzt. Dann "
        "entscheidet nicht mehr der Aufrufer.")


# --- (4) Die Zahl der wirklich gefahrenen Durchgaenge ------------------------

def test_der_selbsttest_weist_seine_suite_laeufe_aus():
    """Der Absturzschutz zum Schalter, dieselbe Bauart wie `PruefungenSoll`.

    Wer die Wiederholung abstellt, darf dabei nicht versehentlich einen
    **echten** Durchgang mit abstellen — und ein Lauf, der weniger geprüft hat
    als er soll, hat nicht bestanden, sondern nur nichts gemerkt.
    """
    text = _lies(TEST_PS1)
    assert "SuiteLaeufe" in nur_code(text), (
        "BL-195: kit-test.ps1 zaehlt seine Suite-Durchgaenge nicht.")
    assert re.search(r"SuiteLaeufe -ne \d", text), (
        "BL-195: Die Zahl wird gezaehlt, aber nicht geprueft. Dann ist sie "
        "Zierde.")


# --- (5) Der Schalter wirkt, GEFAHREN ----------------------------------------

def test_bash_installer_ueberspringt_auf_verlangen(tmp_path):
    """Die Probe, die den Fix erst gültig macht — am **Quelltext** gemessen
    wäre sie nur die halbe Aussage.

    Gefahren wird nicht der ganze Installer (das wäre der Lauf, den dieser
    Eintrag gerade abschaffen will), sondern nur seine Weiche: der echte
    Codeblock aus der echten Datei, mit gesetztem und mit ungesetztem
    Schalter.
    """
    if not INSTALL_SH.is_file():
        pytest.skip("install.sh liegt in dieser Ablage nicht (nur im Kit)")
    quelle = INSTALL_SH.read_text(encoding="utf-8")
    anfang = quelle.index('if [ "$OHNE_SELBSTTEST" -eq 1 ]; then\n    gelb')
    ende = quelle.index("\nfi\n", anfang) + 4
    block = quelle[anfang:ende]
    assert "team_pytest" in block, (
        "Der herausgeloeste Block ist nicht die Weiche des Selbsttests.")

    skript = tmp_path / "weiche.sh"
    skript.write_text(
        "#!/bin/sh\n"
        'gelb() { printf "%s\\n" "$*"; }\n'
        'team_pytest() { printf "pytest"; }\n'
        'pytest_mitschnitt() { printf "GEFAHREN\\n"; return 0; }\n'
        'ZIEL="."\n'
        + block,
        encoding="utf-8", newline="\n")

    def lauf(wert):
        return subprocess.run(
            [BASH, str(skript)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
            timeout=60, env={**__import__("os").environ,
                             "OHNE_SELBSTTEST": wert})

    # Der Block liest OHNE_SELBSTTEST aus der Umgebung — im Installer ist es
    # eine Skriptvariable, hier wird sie gestellt.
    mit = lauf("1")
    ohne = lauf("0")
    assert "AUF VERLANGEN uebersprungen" in mit.stdout, (
        f"BL-195: Der Schalter wirkt nicht:\n{mit.stdout}{mit.stderr}")
    assert "GEFAHREN" not in mit.stdout, (
        f"BL-195: Trotz Schalter ist pytest gelaufen:\n{mit.stdout}")
    assert "GEFAHREN" in ohne.stdout, (
        "BL-195: OHNE Schalter laeuft pytest NICHT mehr — das ist der "
        f"Schaden, nicht der Fix:\n{ohne.stdout}{ohne.stderr}")

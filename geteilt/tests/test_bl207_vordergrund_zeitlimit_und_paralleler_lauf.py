#!/usr/bin/env python3
"""BL-207 — die Auflage "Smoke-Test im Vordergrund" war nicht erfuellbar, und
die Selbstpruefung stellte einen ZWEITEN Testlauf daneben.

`Feld B`, 2026-08-28. Die Suite dieses Projekts war ueber fuenf Kaskaden auf
149-220 s gewachsen; die Vordergrundgrenze des Agenten-Werkzeugs liegt bei
120 s. Die Rolle stand damit vor der Wahl zwischen einer Regelverletzung und
einem Werkzeug-Timeout und waehlte in DREI VON DREI Faellen dieselbe
Verletzung — woertlich im Log-Feld `result`: *"kicked off the full test suite
in the background since it's taking longer than the 2-minute foreground
limit"*. Zusammen 4,9480 USD in EINEM Lauf, 32 % der Rollenkosten, fuer null
Erkenntnis.

`BL-201` hatte dieselbe Bauform zweimal mit einer SCHAERFEREN Auflage
beantwortet. Dies ist der Beleg, dass Schaerfe nicht hilft: Es ist kein
Disziplinproblem. **Eine Auflage, die die Rolle nicht einhalten KANN, erzeugt
genau das Verhalten, das sie verbieten soll.** Die Antwort ist deshalb eine
ZAHL, die die Rolle im Werkzeug einstellen kann, und sie steht im Prompt.

Der zweite Befund ist der gefaehrlichere. Ralphs Hintergrund-pytest lief noch,
als die `BL-41`-Selbstpruefung IHREN eigenen startete. Zwei gleichzeitige
Laeufe kollidieren; die Selbstpruefung meldete daraufhin ROT fuer einen Baum,
der allein gefahren gruen war (199 passed, im Closeout nachgemessen) — und
schickte den Menschen per `BL-61`-Text ausdruecklich zur Ursachensuche im
Testaufbau. Wer ihr geglaubt und die Stufe neu gebaut haette, haette 2,36 USD
bezahlte, fertige Arbeit weggeworfen.

Diese Datei faehrt BEIDE Richtungen des zweiten Befunds. Ohne die Gegenrichtung
wuerde der Fix gruen, indem die Selbstpruefung gar nichts mehr prueft.
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

from conftest import (BASH, Ruf, Schreib, kit_pfad, ueberspringe_ohne_bahn)

WURZEL = Path(__file__).resolve().parents[2]


def _git(repo, *args):
    ergebnis = subprocess.run(["git", *args], cwd=str(repo),
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    assert ergebnis.returncode == 0, ergebnis.stderr
    return ergebnis.stdout.strip()


# --- (1) Die Auflage bekommt eine Zahl ---------------------------------------


def test_die_bibliothek_setzt_einen_eigenen_default(schale):
    """Der Wert muss einen Bibliotheks-Default haben, nicht nur eine Zeile in
    der Vorlage.

    `BL-200` ist der Grund: `--update` fasst `team.config.*` nicht an. Ein
    neuer Konfigurationswert ohne Rueckfall erreicht eine BESTEHENDE
    Installation nie — und wird auch nicht gemeldet. Ein Wert mit Default ist
    die 'gnaedige' Klasse: Das Feld bekommt ihn beim Update stillschweigend
    richtig.
    """
    quelle = schale.kit_lib.read_text(encoding="utf-8")
    treffer = re.search(schale.default_muster("TEAM_SMOKE_TEST_TIMEOUT"),
                        quelle, re.M)
    assert treffer, (
        "TEAM_SMOKE_TEST_TIMEOUT hat in "
        f"{schale.lib_name} keinen Bibliotheks-Default in der greppbaren "
        "Form (Vertrag Punkt 6) — eine bestehende Installation sieht den "
        "Wert damit LEER (BL-200).")
    assert treffer.group(1).isdigit() and int(treffer.group(1)) > 120, (
        "Der Default muss eine Sekundenzahl OBERHALB der 120-s-Wand des "
        f"Werkzeugs sein, war: {treffer.group(1)!r}")


def test_die_vorlage_traegt_den_wert_auf_beiden_bahnen():
    """`BL-126`: Beide Bahnen bekommen ihre Konfiguration aus derselben
    Quelle. Ein Wert, den nur eine Vorlage setzt, ist eine Drift mit
    Verfallsdatum."""
    vorlagen = [WURZEL / v for v in ("bash/entry/team.config.sh",
                                     "pwsh/entry/team.config.ps1")]
    vorhanden = [p for p in vorlagen if p.is_file()]
    if not vorhanden:
        pytest.skip("Die Konfigurations-VORLAGEN liegen nur im Kit — eine "
                    "Installation traegt ihr gerendertes Ergebnis.")
    for pfad in vorhanden:
        assert "TEAM_SMOKE_TEST_TIMEOUT" in pfad.read_text(encoding="utf-8"), (
            f"{pfad.name} nennt TEAM_SMOKE_TEST_TIMEOUT nicht.")


def _bausteine(tmp_path, schale, namen, smoke="./smoke.sh", timeout=None):
    """Rendert Prompt-Bausteine aus der ECHTEN Bibliothek — OHNE Projektwerte.

    Die Bibliothek wird in ein leeres Verzeichnis kopiert, damit KEINE
    `team.config.*` daneben liegt. In der installierten Ablage laege sonst die
    des Zielprojekts daneben, und der Test maesse dessen Werte statt der
    uebergebenen — die Lehre aus BL-100, hier fuer die Ablage statt fuer den
    Default.
    """
    from conftest import Variable
    lib = schale.lib_kopieren(tmp_path)
    umgebung = {"TEAM_SMOKE_TEST": smoke}
    if timeout:
        umgebung["TEAM_SMOKE_TEST_TIMEOUT"] = timeout
    ergebnis = schale.lauf([Variable(n) for n in namen],
                           cwd=tmp_path, lib=lib, env=umgebung)
    assert ergebnis.returncode == 0, ergebnis.stderr
    return ergebnis.stdout


def test_die_bauende_rolle_liest_die_zahl_im_prompt(tmp_path, schale):
    """Solange die Rolle nur 'Vordergrund, sonst nichts' liest, sieht sie eine
    120-s-Wand und weicht aus. Die Zahl muss im Prompt stehen, nicht nur in
    der Konfiguration."""
    text = _bausteine(tmp_path, schale, ("SMOKE_ZEILE", "SMOKE_SUFFIX"),
                      timeout="900")
    assert "900" in text, (
        "Weder SMOKE_ZEILE noch SMOKE_SUFFIX nennen das Zeitlimit — die Rolle "
        f"erfaehrt nie, dass sie laenger als 120 s warten darf.\n{text}")
    assert "VORDERGRUND" in text, (
        "Die Auflage selbst darf dabei nicht verschwinden.")


def test_auch_der_fixer_bekommt_die_auflage(tmp_path, schale):
    """Frank bekommt NUR SMOKE_SUFFIX, nicht SMOKE_ZEILE — und faehrt den
    Smoke-Test oefter als Ralph.

    Im Feld endeten 10 von 28 Frank-Laeufen ohne Promise, bei NEUN davon stand
    das Warten auf einen Hintergrundlauf woertlich im Log-Feld `result`
    (10,7249 USD an einem Tag). Bei ihm ist der vierte Ausgang zusaetzlich ein
    Fehlversuch (`.frank-attempts`) und eskaliert ab dem dritten an Axel — das
    teure Modell wird also fuer einen Formfehler gerufen.
    """
    suffix = _bausteine(tmp_path, schale, ("SMOKE_SUFFIX",), timeout="900")
    assert "VORDERGRUND" in suffix, (
        "Der Nachsatz, den Frank als EINZIGES ueber den Smoke-Test liest, "
        f"nennt die Vordergrund-Auflage nicht:\n{suffix!r}")
    assert "900" in suffix, (
        f"…und auch nicht das Zeitlimit:\n{suffix!r}")


def test_ohne_smoke_test_bleibt_der_baustein_leer(tmp_path, schale):
    """Gegenprobe: Ohne konfigurierten Befehl darf hier keine Auflage stehen —
    sonst verlangt der Prompt etwas, das es nicht gibt (BL-149)."""
    suffix = _bausteine(tmp_path, schale, ("SMOKE_SUFFIX",), smoke="")
    assert suffix.strip() == "", (
        f"SMOKE_SUFFIX muss leer bleiben, war: {suffix!r}")


# --- (2) Die Selbstpruefung stellt keinen zweiten Lauf daneben ---------------


def _projekt(tmp_path, schale, smoke_rc=0, dauer=0):
    """Wegwerf-Repo mit Arbeit, Zusicherung und einem Smoke-Test.

    `dauer` > 0 macht den Smoke-Test langsam — so laesst er sich als
    HINTERGRUNDLAUF danebenstellen, ohne dass der Test auf ihn wartet.
    """
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "team").mkdir()
    (repo / "team" / schale.lib_name).write_bytes(schale.kit_lib.read_bytes())
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "tests" / "test_bestand.py").write_text(
        "def test_bestand(): pass\n", encoding="utf-8")
    if schale.ist_bash:
        (repo / "smoke.sh").write_text(
            "#!/usr/bin/env bash\n"
            + (f"sleep {dauer}\n" if dauer else "")
            + f"exit {smoke_rc}\n", encoding="utf-8")
        (repo / "smoke.sh").chmod(0o755)
    else:
        (repo / "smoke.ps1").write_text(
            (f"Start-Sleep -Seconds {dauer}\n" if dauer else "")
            + f"exit {smoke_rc}\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "start")
    return repo


def _smoke_befehl(schale):
    return "./smoke.sh" if schale.ist_bash else "./smoke.ps1"


def _selbstpruefung(repo, schale, extra=()):
    """Faehrt team_quittung_selbstpruefung gegen eine Stufe mit Arbeit."""
    return schale.lauf(
        [Schreib("src/modul.py", "y = 2\n"),
         Schreib("tests/test_stufe1_sache.py", "def test_x(): pass\n"),
         *extra,
         Ruf("team_quittung_selbstpruefung", "ralph", "1")],
        cwd=repo, lib=repo / "team" / schale.lib_name,
        env={"TEAM_SMOKE_TEST": _smoke_befehl(schale),
             "TEAM_TEST_ORDNER": "tests/"})


def _verlange_prozesstabelle_mit_argumenten(schale):
    """Die Erkennung braucht eine Prozesstabelle, die KOMMANDOZEILEN zeigt.

    BL-159, der Wirt entscheidet: Unter Linux liefert `ps -eo args=` sie, und
    das ist die Bahn, auf der das Kit in bash betrieben wird. Die MSYS-`ps`
    von Git for Windows kennt `-o` nicht und zeigt nur den Programmpfad ohne
    Argumente — dort ist ein Parallellauf nicht feststellbar, und die
    Bibliothek faellt bewusst auf das bisherige Verhalten zurueck (lieber
    keine Erkennung als eine falsche). Windows wird vom Kit ueber die
    pwsh-Bahn bedient; dort traegt `Win32_Process` die Kommandozeile, und die
    Faelle unten laufen.

    Ein stiller Uebersprung liest sich am Ende wie ein bestandener Nachweis —
    deshalb mit Grund.
    """
    if not schale.ist_bash:
        return
    probe = subprocess.run([BASH or "bash", "-c", "ps -eo args= 2>/dev/null"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    if not probe.stdout.strip():
        pytest.skip(
            "Die `ps` dieses Wirts zeigt keine Kommandozeilen (MSYS/Git for "
            "Windows kennt `-o` nicht). Ein Parallellauf ist auf der "
            "bash-Bahn dieses Wirts nicht feststellbar; die Bibliothek faellt "
            "dort auf das bisherige Verhalten zurueck. Der Fall laeuft unter "
            "Linux und — auf demselben Wirt — auf der pwsh-Bahn.")


def _hintergrundlauf(repo, schale):
    """Startet den Verifikationsbefehl als eigenen Prozess — die Feldlage.

    Die Kommandozeile MUSS den konfigurierten Befehl woertlich enthalten; das
    ist die Spur, an der die Selbstpruefung ihn erkennt.
    """
    if schale.ist_bash:
        befehl = [BASH or "bash", "./smoke.sh"]
    else:
        befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-Command",
                  "& './smoke.ps1'"]
    return subprocess.Popen(befehl, cwd=str(repo),
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)


def test_ein_laufender_verifikationslauf_ergibt_UNBEKANNT(tmp_path, schale):
    """Der gefaehrliche Befund: Die Selbstpruefung darf keinen zweiten Lauf
    danebenstellen — und im Zweifel NICHT 'rot' behaupten."""
    _verlange_prozesstabelle_mit_argumenten(schale)
    repo = _projekt(tmp_path, schale, smoke_rc=0, dauer=30)
    prozess = _hintergrundlauf(repo, schale)
    try:
        # Dem Kind Zeit geben, wirklich in der Prozesstabelle zu stehen.
        for _ in range(50):
            if prozess.poll() is None:
                break
            time.sleep(0.1)
        ergebnis = _selbstpruefung(repo, schale)
    finally:
        prozess.kill()
        prozess.wait()

    assert ergebnis.returncode != 0, (
        "Bei laufendem Verifikationslauf darf NICHT automatisch quittiert "
        "werden.")
    assert "UNBEKANNT" in ergebnis.stderr, (
        "Die Selbstpruefung muss den Fall BENENNEN. Eine, die im Zweifel "
        "'rot' behauptet, ist schlimmer als eine, die schweigt — sie schickt "
        f"den Menschen mit einer konkreten, falschen Faehrte los.\n{ergebnis.stderr}")
    assert "BL-61" not in ergebnis.stderr, (
        "Der BL-61-Text schickt den Menschen zur Ursachensuche im Testaufbau. "
        "Genau das war im Feld die falsche Faehrte — der Baum war gruen.\n"
        + ergebnis.stderr)
    assert "ist ROT" not in ergebnis.stderr, (
        "Es darf kein roter Baum behauptet werden.\n" + ergebnis.stderr)


def test_ohne_parallellauf_bleibt_ein_roter_baum_rot(tmp_path, schale):
    """Erste Gegenrichtung. Ohne sie waere der Fix gruen, indem die
    Selbstpruefung gar nichts mehr prueft."""
    repo = _projekt(tmp_path, schale, smoke_rc=1)
    ergebnis = _selbstpruefung(repo, schale)
    assert ergebnis.returncode != 0
    assert "ist ROT" in ergebnis.stderr, (
        "Ein wirklich roter Baum muss weiterhin als rot gemeldet werden.\n"
        + ergebnis.stderr)
    assert "BL-61" in ergebnis.stderr, (
        "…mitsamt der Pruefreihenfolge, die es dafuer gibt.\n" + ergebnis.stderr)


def test_ohne_parallellauf_wird_gruen_weiterhin_quittiert(tmp_path, schale):
    """Zweite Gegenrichtung, die wichtigere: Die Automatik, fuer die es
    BL-110 gibt, muss erhalten bleiben."""
    repo = _projekt(tmp_path, schale, smoke_rc=0)
    ergebnis = _selbstpruefung(repo, schale)
    assert ergebnis.returncode == 0, (
        "Ein gruener Baum ohne Parallellauf muss weiterhin automatisch "
        f"quittiert werden.\n{ergebnis.stderr}")
    assert "Alle drei Prüfungen bestanden" in ergebnis.stderr


def test_die_erkennung_nennt_die_gefundene_zeile(tmp_path, schale):
    """Ein Fehlalarm — ein Dauerlaeufer, der den Befehl in seiner
    Kommandozeile traegt — muss in einem Blick als solcher erkennbar sein
    statt als Raetsel."""
    _verlange_prozesstabelle_mit_argumenten(schale)
    repo = _projekt(tmp_path, schale, smoke_rc=0, dauer=30)
    prozess = _hintergrundlauf(repo, schale)
    try:
        for _ in range(50):
            if prozess.poll() is None:
                break
            time.sleep(0.1)
        ergebnis = _selbstpruefung(repo, schale)
    finally:
        prozess.kill()
        prozess.wait()
    assert "Gefunden:" in ergebnis.stderr, (
        "Die Meldung nennt die gefundene Kommandozeile nicht — ein Fehlalarm "
        f"waere damit nicht diagnostizierbar.\n{ergebnis.stderr}")
    assert _smoke_befehl(schale) in ergebnis.stderr


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

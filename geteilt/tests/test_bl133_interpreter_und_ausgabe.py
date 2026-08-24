#!/usr/bin/env python3
r"""BL-133: Der Windows-Lauf war rot, und keiner der 68 Fehlschlaege kam aus
dem Kit — schon wieder.

⚠️ Feldbefund, dieselbe Windows-Maschine wie BL-113 und BL-122…BL-132. Der
Lauf im Zielprojekt meldete `68 failed, 436 passed`. 65 dieser Fehlschlaege
trugen woertlich dieselbe Zeile:

    Python was not found; run without arguments to install from the
    Microsoft Store, or disable this shortcut from Settings > Apps > …

Das ist der Fund aus BL-131, und er war abgetragen. Nur eben nicht ueberall.
BL-131 hat DREI Orte gezaehlt (Bibliothek, Konfigurationsvorlage, Installer)
und dort auch geheilt. Der Name stand aber an vier weiteren:

  1. DIE ENTRYPOINTS. `team-status.sh` fuenfmal, `vollautomatik.sh` dreimal.
     Beide sourcen `team/lib.sh` und haetten `$TEAM_PYTHON` gehabt. Die
     Wirkung war ungleich: Im Statusskript wurden aus Betraegen LEERE
     Zeichenketten ("real via API abgerechnet:  USD") — nicht null, nicht
     Fehler, leer. In `vollautomatik.sh` sass der Aufruf in `budget_ok`; der
     Store-Alias endet mit 49, also ungleich 0, und das las die Bedingung als
     "Deckel nicht ueberschritten". Der Lauf lief weiter, und zwar genau dann,
     wenn er haette anhalten sollen. Zusicherung: der erweiterte
     `test_bl131_python_name_ist_maschinensache.py`.

  2. DER HARNISCH. `lib.sh` nimmt den Namen aus `team.config.sh`. Der Harnisch
     ist aber kein installiertes Projekt: Er sourct die Bibliothek direkt, und
     dann greift deren POSIX-Default `python3`. Fuer die zwei Werkzeugzeilen
     loeste `werkzeug_wert()` das laengst auf — fuer die dreizehn Aufrufe IN
     der Bibliothek hatte es niemand nachgezogen. Zusicherung: unten.

  3. DIE UMGEBUNG NEUN EINZELNER TESTDATEIEN. Sie bauten ihr `env` weiter
     selbst und setzten den Suchpfad auf zwei feste POSIX-Verzeichnisse (usr
     und bin). Unter Windows liegt dort nichts — kein git, kein python, keine
     Agenten-CLI. `basis_umgebung()` gab es zu dem Zeitpunkt schon; der
     Sammeltest aus BL-130 hat diese fuenfte Annahme nur nicht gekannt.
     Zusicherung: das erweiterte `VERBOTEN` in
     `test_bl130_harnisch_plattformannahmen.py` — woertlich zitiert wird das
     Muster hier bewusst NICHT, sonst meldete der Waechter diese Datei, und
     er haette recht.

  4. DIE KONFIGURATION EINES GELEBTEN PROJEKTS. Der bitterste Teil, weil ihn
     kein Test der Welt im Kit gefunden haette: `--update` fasst
     `team.config.*` bewusst nicht an (Projektdaten). Ein Projekt, das VOR
     BL-122/BL-131 eingerichtet wurde, traegt darin `python3` — die Vorlagen
     hatten damals gar keinen Platzhalter, es gab nichts zu fuellen. Diese
     Projekte bekommen die Heilung also nie, auf KEINER Bahn: Im Feldprojekt
     war `team.config.ps1` genauso betroffen wie `team.config.sh`, und die
     pwsh-Bahn ist dort die einzige, die benutzt wird. Zusicherung: unten.

UND EIN ZWEITER, EIGENSTAENDIGER FUND: DIE AUSGABE DER WERKZEUGE
    Drei Fehlschlaege trugen nicht "Python was not found", sondern ein
    Ersatzzeichen mitten im Wort:

        assert 'an Frank übergeben' in '… an Frank �bergeben …'

    Gelesen und geschrieben wird in `beutebuch.py`, `kosten.py` und
    `zitat_lint.py` ueberall mit ausdruecklichem `encoding="utf-8"` (das ist
    BL-113 und BL-129). Fuer stdout/stderr galt weiter Pythons Default, und
    der ist unter Windows die ANSI-Codepage der Maschine — hier cp1252. Der
    Statuswert verliess das Werkzeug damit als cp1252-Bytes, der Aufrufer
    liest UTF-8, und aus dem Umlaut wurde U+FFFD.

    Die Wirkung war kein Zeichenfehler, sondern ein FALSCHES URTEIL:
    `frank.sh` verglich den zurueckgegebenen Status mit "an Frank uebergeben",
    fand keine Uebereinstimmung und meldete "Kein Fund mit Status 'an Frank
    uebergeben' — nichts zu tun." Vor einem Beutebuch, in dem genau der stand.
    Die Fixphase lief an jedem uebergebenen Fund vorbei — dieselbe Wirkung wie
    BL-1, aus einer voellig anderen Richtung.

WARUM DIESE ZUSICHERUNGEN AM VERHALTEN HAENGEN UND NICHT AM QUELLTEXT
    Anders als BL-126, BL-129, BL-130 und BL-131: Diese hier fallen auch auf
    einem Linux-Wirt, wenn jemand sie zurueckdreht. Ein Werkzeug, das seine
    Ausgabe nicht in UTF-8 schreibt, ist ueberall falsch — es faellt dort nur
    nicht auf, weil die Locale zufaellig schon UTF-8 ist. Wo eine Zusicherung
    am Verhalten haengen KANN, haengt sie am Verhalten.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import conftest
from conftest import PYTHON_BEFEHL, basis_umgebung, kit_pfad

WURZEL = Path(__file__).resolve().parents[2]

# Ein Wort mit Umlaut, das im Kit wirklich vorkommt und ueber die Werkzeuge
# laeuft: der Statuswert, an dem Franks Fixphase haengt.
UMLAUT_WORT = "übergeben"


def _quelle(*kandidaten):
    for kandidat in kandidaten:
        pfad = WURZEL / kandidat
        if pfad.is_file():
            return pfad
    pytest.skip(f"keine der Quellen liegt in dieser Ablage: {kandidaten}")


# --- 2. Der Harnisch traegt den Namen der Maschine ---------------------------

def test_basis_umgebung_nennt_einen_startbaren_interpreter():
    """Im Feld traegt `team.config.sh` den Namen, im Test der Harnisch.

    Ohne diesen Wert faellt `lib.sh` auf ihren POSIX-Default zurueck, und
    dreizehn Funktionen — darunter `team_promise_in`, `team_result_is_429`
    und die Budget-Summen — antworten mit einer leeren Zeichenkette und
    Exit 49.
    """
    umgebung = basis_umgebung()
    assert "TEAM_PYTHON" in umgebung, (
        "basis_umgebung() nennt TEAM_PYTHON nicht — lib.sh nimmt dann ihren "
        "eigenen Default 'python3', und der ist unter Windows der Store-Alias")
    probe = subprocess.run(
        [umgebung["TEAM_PYTHON"], "-c", "import sys; print(sys.version_info[0])"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert probe.returncode == 0 and probe.stdout.strip() == "3", (
        f"'{umgebung['TEAM_PYTHON']}' startet auf diesem Wirt nicht als "
        f"Python 3.\nSTDOUT: {probe.stdout!r}\nSTDERR: {probe.stderr!r}")


def test_die_isolation_gegen_fremde_team_werte_bleibt_bestehen(monkeypatch):
    """Gegenprobe zu BL-130: TEAM_PYTHON ist eine Angabe ueber die MASCHINE
    und damit die einzige erlaubte Ausnahme. Faellt die Isolation im Ganzen,
    lenken die TEAM_*-Werte der Wirtssitzung jeden Test mit."""
    monkeypatch.setenv("TEAM_BUDGET_USD", "999")
    monkeypatch.setenv("TEAM_SMOKE_TEST", "./nicht-dieser-test.sh")
    umgebung = basis_umgebung()
    assert "TEAM_BUDGET_USD" not in umgebung
    assert "TEAM_SMOKE_TEST" not in umgebung


def test_die_bibliothek_rechnet_unter_dieser_umgebung_wirklich(tmp_path):
    """Die Wirkung statt der Einstellung: eine Funktion, die ueber
    `$TEAM_PYTHON` laeuft, muss eine ZAHL liefern.

    Vorher kam hier eine leere Zeichenkette — und die trug sich als leeres
    Feld bis in die Kostenanzeige durch, wo sie wie ein Projekt ohne Ausgaben
    aussah.
    """
    conftest.verlange_bash()
    log = tmp_path / "stufe-1.json"
    log.write_text('{"total_cost_usd": 1.2345, "is_error": false}',
                   encoding="utf-8")
    ergebnis = conftest.Schale("bash").lauf(
        conftest.Ausgabe("team_summe_cost_usd", log), cwd=tmp_path)
    assert ergebnis.returncode == 0, ergebnis.stderr
    # Verglichen wird der WERT, nicht seine Schreibweise: Die Funktion gibt
    # zehn Nachkommastellen aus, und wie viele es sind, ist nicht der
    # Gegenstand dieses Tests. Ein Test, der die Stellenzahl mitprueft, wird
    # beim naechsten Formatwechsel rot und behauptet dann einen Fund, den es
    # nicht gibt.
    assert ergebnis.stdout.strip(), (
        "team_summe_cost_usd hat gar nichts ausgegeben — dann lief der "
        f"Interpreter nicht.\nSTDERR: {ergebnis.stderr!r}")
    assert float(ergebnis.stdout.strip()) == pytest.approx(1.2345), (
        "team_summe_cost_usd hat nicht gerechnet.\n"
        f"STDOUT: {ergebnis.stdout!r}\nSTDERR: {ergebnis.stderr!r}")


# --- Der zweite Fund: die Ausgabe der Werkzeuge ------------------------------

# BL-153: Die Liste stand hier als ABSCHRIFT — drei Namen, von Hand gepflegt.
# Das ist genau die Bauart, die `kit-readme-pruefen.py` in seinem Kopf als
# Fehler beschreibt: Ein Waechter, der eine Abschrift prueft, veraltet mit ihr.
# Beim vierten Werkzeug (`kit_meldung.py`) waere die Zusicherung stillschweigend
# an ihm vorbeigelaufen — und genau dieses Werkzeug gibt Prosa mit Umlauten aus.
# Geprueft wird deshalb die GATTUNG: jedes Werkzeug, das im Ordner liegt.
def _werkzeuge():
    ordner = kit_pfad("tools")
    if not ordner.is_dir():
        return ("beutebuch.py",)   # der Name, an dem der Skip unten greift
    return tuple(sorted(p.name for p in ordner.glob("*.py")))


WERKZEUGE = _werkzeuge()


@pytest.mark.parametrize("werkzeug", WERKZEUGE)
def test_werkzeug_schreibt_utf8_auch_in_fremder_locale(werkzeug, tmp_path):
    """Der Nachweis am Verhalten — und er laeuft auf JEDEM Wirt.

    Die Locale wird gestellt: `PYTHONIOENCODING=cp1252` erzeugt genau den
    Zustand, den ein deutsches Windows von sich aus herstellt. Ohne den
    Fix schreibt das Werkzeug den Umlaut dann als cp1252-Byte, und der
    Aufrufer — der UTF-8 liest — bekommt U+FFFD.

    Geprueft wird das Werkzeug ALS PROZESS, nicht als Import: Die Umstellung
    passiert beim Start, und ein Import im laufenden pytest wuerde sie an
    dessen bereits umgelenkten Stroemen vorbeilaufen lassen.
    """
    pfad = kit_pfad("tools", werkzeug)
    if not pfad.is_file():
        pytest.skip(f"{werkzeug} liegt in dieser Ablage nicht")
    skript = (
        "import runpy, sys\n"
        f"sys.argv = ['{werkzeug}']\n"
        f"print({UMLAUT_WORT!r})\n"
        f"print({UMLAUT_WORT!r}, file=sys.stderr)\n")
    umgebung = basis_umgebung(PYTHONIOENCODING="cp1252")
    ergebnis = subprocess.run(
        [PYTHON_BEFEHL, "-c",
         f"import sys; sys.path.insert(0, {str(pfad.parent)!r}); "
         f"import {pfad.stem}; " + skript.replace("\n", "; ").rstrip("; ")],
        capture_output=True, env=umgebung)
    assert ergebnis.returncode == 0, ergebnis.stderr.decode("utf-8", "replace")
    for strom, rohdaten in (("stdout", ergebnis.stdout),
                            ("stderr", ergebnis.stderr)):
        assert UMLAUT_WORT.encode("utf-8") in rohdaten, (
            f"{werkzeug} schreibt auf {strom} nicht in UTF-8. Der Aufrufer "
            f"liest UTF-8 und bekommt ein Ersatzzeichen mitten im Wort; "
            f"`frank.sh` vergleicht damit Status-Werte, die nicht mehr gleich "
            f"sind (BL-133).\nRoh: {rohdaten!r}")


def test_beutebuch_liefert_den_statuswert_unversehrt(tmp_path):
    """Der Feldfall selbst, end-to-end ueber die Prozessgrenze.

    Genau hier riss es: `frank.sh` fragt `beutebuch.py first <status>`, und die
    Antwort muss BYTEGLEICH der Wert aus dem Buch sein. Ein Ersatzzeichen an
    der Stelle des Umlauts macht aus "Fund gefunden" ein "nichts zu tun".
    """
    beutebuch = kit_pfad("tools", "beutebuch.py")
    if not beutebuch.is_file():
        pytest.skip("beutebuch.py liegt in dieser Ablage nicht")
    status = f"an Frank {UMLAUT_WORT}"
    buch = tmp_path / "beutebuch.md"
    buch.write_text(
        "# Beutebuch\n\n## Funde\n\n"
        "### HM-1 — Beispielfund\n"
        f"- **Status**: {status}\n"
        "- **Reproducer-Test**: `tests/test_hm1_x.py`\n"
        "- Betrifft `src/app.py`\n", encoding="utf-8")

    ergebnis = subprocess.run(
        [PYTHON_BEFEHL, str(beutebuch), "--pfad", str(buch), "list"],
        capture_output=True, env=basis_umgebung(PYTHONIOENCODING="cp1252"))
    assert ergebnis.returncode == 0, ergebnis.stderr.decode("utf-8", "replace")
    ausgabe = ergebnis.stdout.decode("utf-8", "replace")
    assert status in ausgabe, (
        "Der Statuswert kommt nicht unversehrt an. Damit findet die Fixphase "
        f"den uebergebenen Fund nicht mehr (BL-133).\nBekommen: {ausgabe!r}")


# --- 4. Was --update nicht anfasst, muss es trotzdem ansehen -----------------

def test_beide_installer_pruefen_den_konfigurierten_interpreter():
    """Bauart BL-109 (.gitignore-Abgleich), auf denselben Fall angewandt.

    "--update fasst team.config.* nicht an" ist richtig — die Datei traegt
    Projektdaten. "--update sieht sie gar nicht an" war es nicht: Ein Projekt
    von vor BL-122/BL-131 zeigt darin auf einen Interpreter, den es auf der
    Maschine nicht gibt, und jedes Update meldete Erfolg.

    Gefordert werden beide Haelften: dass der Abgleich existiert UND dass er
    im Update-Pfad aufgerufen wird. Eine Funktion, die niemand ruft, ist die
    Bauart Zusicherung, die BL-127 gefunden hat.
    """
    faelle = (
        (_quelle("bash/install.sh"), r"python_abgleich\(\)\s*\{",
         r"^\s*python_abgleich\b"),
        (_quelle("pwsh/install.ps1"), r"function Python-Abgleich\s*\{",
         r"^\s*Python-Abgleich\b"),
    )
    for quelle, definition, aufruf in faelle:
        text = quelle.read_text(encoding="utf-8-sig")
        assert re.search(definition, text, re.M), (
            f"{quelle.name} kennt keinen Abgleich des konfigurierten "
            "Interpreters (BL-133)")
        assert re.search(aufruf, text, re.M), (
            f"{quelle.name} definiert den Abgleich, ruft ihn aber nicht — "
            "eine Pruefung, die nie laeuft, ist keine")


def test_der_abgleich_startet_den_interpreter_statt_ihn_zu_suchen():
    """Die Lehre aus BL-122, hier zum dritten Mal: `command -v` FINDET den
    Store-Alias. Nur ein echter Start entlarvt ihn."""
    text = _quelle("bash/install.sh").read_text(encoding="utf-8")
    block = re.search(r"python_abgleich\(\)\s*\{.*?\n\}", text, re.S)
    assert block, "python_abgleich() ist in install.sh nicht mehr auffindbar"
    assert "version_info" in block.group(0), (
        "der Abgleich prueft nur die Existenz, nicht den Start — dann meldet "
        "er den Store-Alias als in Ordnung (BL-122/BL-133)")


@pytest.mark.parametrize("konfig,zeile", [
    ("team.config.sh",
     'TEAM_KOSTEN_TOOL="${TEAM_KOSTEN_TOOL:-python3 team/tools/kosten.py}"'),
    ("team.config.sh",
     'TEAM_PYTHON="${TEAM_PYTHON:-pythonXY}"\n'
     'TEAM_KOSTEN_TOOL="${TEAM_KOSTEN_TOOL:-$TEAM_PYTHON team/tools/kosten.py}"'),
    ("team.config.ps1",
     "$TEAM_KOSTEN_TOOL    = Team-Wert 'TEAM_KOSTEN_TOOL'    "
     "'python3 team/tools/kosten.py'"),
])
def test_der_abgleich_liest_den_namen_aus_beiden_konfigformaten(
        tmp_path, konfig, zeile):
    """Der Name steht in den beiden Bahnen verschieden da — und in der .sh
    sogar auf zwei Arten, je nachdem ob das Projekt die TEAM_PYTHON-Zeile
    schon hat. Ein Abgleich, der nur eine Schreibweise kennt, meldet bei den
    anderen "kein Interpretername auffindbar" und damit gar nichts."""
    conftest.verlange_bash()
    quelle = _quelle("bash/install.sh").read_text(encoding="utf-8")
    block = re.search(r"python_aus_config\(\)\s*\{.*?\n\}", quelle, re.S)
    assert block, "python_aus_config() ist in install.sh nicht auffindbar"

    datei = tmp_path / konfig
    datei.write_text(zeile + "\n", encoding="utf-8")
    ergebnis = subprocess.run(
        [conftest.BASH, "-c",
         block.group(0) + f'\npython_aus_config "{datei}"\n'],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=basis_umgebung())
    erwartet = "pythonXY" if "pythonXY" in zeile else "python3"
    assert ergebnis.stdout.strip() == erwartet, (
        f"aus {konfig} wurde '{ergebnis.stdout.strip()}' gelesen, erwartet "
        f"war '{erwartet}'\nSTDERR: {ergebnis.stderr}")

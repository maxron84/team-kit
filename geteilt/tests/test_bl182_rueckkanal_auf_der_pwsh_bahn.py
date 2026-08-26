#!/usr/bin/env python3
"""BL-182: Der Rueckkanal Feld -> Kit war auf der pwsh-Bahn seit Tag 1 tot.

WAS IM FELD PASSIERT IST
    `Feld B` (Windows 11, einbahnig pwsh) wollte 2026-08-25 zum ersten Mal
    ueberhaupt eine Meldung anlegen. JEDES Verb brach ab:

        The expression after '&' in a pipeline element produced an object
        that was not valid. It must result in a command name, a script
        block, or a CommandInfo object.

    `pwsh/entry/kit-melden.ps1` rief `& $TEAM_PYTHON team/tools/kit_meldung.py`
    auf. `TEAM_PYTHON` gibt es NUR auf der bash-Bahn (team.config.sh, lib.sh);
    auf dieser Bahn war die Variable leer, und `&` auf eine leere Zeichenkette
    bricht ab. Weil alle fuenf Verben (`neu`, `pruefen`, `senden`,
    `issue-link`, `kit-pfad`) durch diese eine Zeile laufen, war der gesamte
    Rueckkanal unerreichbar — und zwar, seit es die Bahn gibt.

DIE ZWEITE HAELFTE, GEFUNDEN BEIM BELEGEN DER ERSTEN
    Nach dem Fix lief `neu`, aber `kit-pfad` meldete weiterhin

        Kein Kit gefunden — weder TEAM_KIT_PFAD noch die ueblichen Ablagen.

    obwohl `TEAM_KIT_PFAD` in `team.config.ps1` eingetragen war. Ursache ist
    die MODULGRENZE: Die Konfiguration wird von `lib.psm1` dot-gesourct, und
    was nicht in deren `Export-ModuleMember -Variable`-Liste steht, sieht ein
    Entrypoint nicht. `TEAM_KIT_PFAD` stand nicht darin.

    Auf der bash-Bahn kann dieser Fehler nicht existieren — `source` legt
    alles in dieselbe Shell, es gibt keine Grenze, an der etwas verloren geht.
    Der Fund ist damit dieselbe Gattung wie BL-145: „gruen bedeutet auf den
    beiden Bahnen verschieden viel". Und er hat ausgerechnet den Wert
    getroffen, den BL-153 eingefuehrt hat, damit der Rueckkanal ueberhaupt
    weiss, wo das Kit liegt.

WAS DIESER TEST PRUEFT
    (1) QUELLTEXT — kit-melden.ps1 nennt `$TEAM_PYTHON` nicht mehr. Laeuft auf
        JEDEM Wirt, auch ohne pwsh.
    (2) DIE GATTUNG STATT DER STELLE — jeder Wert, den `team.config.ps1`
        setzt, steht in der Exportliste von `lib.psm1`. Das ist der Riegel,
        der den NAECHSTEN Fall dieser Art faengt, nicht nur diesen. Er ist
        heute fehlalarmfrei: 27 Werte in der Konfiguration, 27 exportiert.
    (3) VERHALTEN — dieselbe Liste noch einmal am LAUFENDEN Modul, ueber
        `(Get-Module).ExportedVariables`. Ein Riegel am Quelltext beweist,
        dass der Name in einer Liste steht; erst das Modul beweist, dass der
        WERT ankommt.
    (4) END-TO-END — alle fuenf Verben gegen ein Fixture-Projekt. Der Fund war
        ein Laufzeitfehler; ein Test, der nur Text liest, haette ihn in drei
        Monaten nicht gesehen.
    (5) GEGENPROBE — der alte Aufruf muss WIRKLICH scheitern. Ohne sie bliebe
        offen, ob (4) etwas absichert oder nur beschreibt, was ohnehin gilt.
"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import (kit_pfad, ueberspringe_ohne_bahn, verlange_pwsh,
                      werkzeug_wert)

REPO_ROOT = Path(__file__).resolve().parents[2]

MELDEN_PS1 = REPO_ROOT / "kit-melden.ps1"
if not MELDEN_PS1.is_file():
    MELDEN_PS1 = REPO_ROOT / "pwsh" / "entry" / "kit-melden.ps1"

KONFIG_PS1 = REPO_ROOT / "team.config.ps1"
if not KONFIG_PS1.is_file():
    KONFIG_PS1 = REPO_ROOT / "pwsh" / "entry" / "team.config.ps1"


def _lies(pfad):
    return pfad.read_text(encoding="utf-8-sig")


# --- (1) Quelltext ------------------------------------------------------------


def test_kit_melden_nennt_keine_bash_variable_mehr():
    """`TEAM_PYTHON` ist ein Wert der bash-Bahn und darf hier nicht vorkommen.

    Der Riegel steht bewusst auf dem NAMEN und nicht auf `& $`: Wer die Zeile
    beim naechsten Umbau wieder von `kit-melden.sh` herueberkopiert, kopiert
    genau diesen Namen mit.
    """
    ueberspringe_ohne_bahn("pwsh")
    assert MELDEN_PS1.is_file(), f"kit-melden.ps1 nicht gefunden ({MELDEN_PS1})"
    ohne_kommentar = "\n".join(
        z for z in _lies(MELDEN_PS1).splitlines() if not z.lstrip().startswith("#"))
    assert "TEAM_PYTHON" not in ohne_kommentar, (
        "BL-182: `$TEAM_PYTHON` gibt es nur auf der bash-Bahn (team.config.sh, "
        "lib.sh). Auf dieser Bahn ist die Variable leer, und `&` auf eine leere "
        "Zeichenkette bricht mit \"must result in a command name\" ab — fuer "
        "JEDES Verb. Der pwsh-Weg ist die Werkzeugzeile aus der Konfiguration "
        "(`$TEAM_MELDUNG_TOOL`), zerlegt von `Team-Werkzeug`.")


def test_die_werkzeugzeile_steht_in_der_konfiguration():
    """Die Gegenrichtung: Man darf (1) nicht durch Loeschen gruen machen."""
    ueberspringe_ohne_bahn("pwsh")
    text = _lies(KONFIG_PS1)
    assert re.search(r"\$TEAM_MELDUNG_TOOL\s*=", text), (
        "team.config.ps1 setzt TEAM_MELDUNG_TOOL nicht — dann hat der "
        "Rueckkanal auf dieser Bahn keinen Interpreter, und wir sind wieder "
        "bei BL-182.")
    assert "Team-Werkzeug $TEAM_MELDUNG_TOOL" in _lies(MELDEN_PS1), (
        "kit-melden.ps1 benutzt die Werkzeugzeile nicht ueber Team-Werkzeug — "
        "PowerShell uebergibt eine Zeichenkette sonst als EIN Argument.")


def test_die_vorlage_traegt_den_platzhalter():
    """Nur an der KIT-Vorlage pruefbar — in der Installation ist er gefuellt.

    Die Marke wird zur Laufzeit zusammengesetzt und nicht woertlich getippt:
    Stufe 3 des Selbsttests sucht nach ungefuellten Platzhaltern in der
    ausgelieferten Ablage und meldete eine woertlich zitierte Marke als
    Befund. `test_bl153_rueckkanal_meldung.py` loest es seit langem so.
    """
    ueberspringe_ohne_bahn("pwsh")
    if KONFIG_PS1.parent.name != "entry":
        pytest.skip("installierte Ablage — der Platzhalter ist hier gefuellt, "
                    "und das ist genau richtig")
    marke = "".join(("{{", "PYTHON", "}}"))
    text = _lies(KONFIG_PS1)
    assert re.search(r"\$TEAM_MELDUNG_TOOL\s*=.*" + re.escape(marke), text), (
        f"TEAM_MELDUNG_TOOL traegt den {marke}-Platzhalter nicht — dann haengt "
        "der Interpreter am Namen der BAUZEIT statt an dem der Maschine "
        "(BL-131), und beide Installer haben nichts einzusetzen.")


# --- (2) Die Gattung: kein Wert bleibt an der Modulgrenze liegen --------------


def _konfigurationswerte():
    return set(re.findall(r"^\$(TEAM_[A-Z0-9_]+)\s*=", _lies(KONFIG_PS1), re.M))


def _exportliste():
    lib = _lies(kit_pfad("lib.psm1"))
    # rpartition, nicht split: `Export-ModuleMember` steht weiter oben auch im
    # Kopfkommentar, und ein Riegel, der den Kommentar liest, prueft nichts.
    _, treffer, schwanz = lib.rpartition("Export-ModuleMember")
    assert treffer, "lib.psm1 hat keine Export-ModuleMember-Zeile"
    return set(re.findall(r"'(TEAM_[A-Z0-9_]+)'", schwanz))


def test_jeder_konfigurationswert_steht_in_der_exportliste():
    """Der eigentliche Riegel — er faengt den NAECHSTEN Fall, nicht diesen.

    `TEAM_KIT_PFAD` stand in team.config.ps1 und kam trotzdem nie an. Ein Test
    auf genau diesen Namen haette den Fund beschrieben; dieser hier beschreibt
    die REGEL: Was die Konfiguration setzt, muss die Modulgrenze ueberleben.
    Auf der bash-Bahn gibt es diese Grenze nicht — der Fund ist dort
    strukturell unsichtbar, und deshalb faellt er ohne Riegel wieder an.
    """
    ueberspringe_ohne_bahn("pwsh")
    fehlt = sorted(_konfigurationswerte() - _exportliste())
    assert not fehlt, (
        "BL-182: Diese Werte setzt team.config.ps1, aber lib.psm1 exportiert "
        "sie nicht — ein Entrypoint sieht sie deshalb LEER, ohne jede "
        "Fehlermeldung:\n  " + "\n  ".join(fehlt)
        + "\nJeder Name gehoert in die Export-ModuleMember-Liste von lib.psm1.")


def test_das_laufende_modul_reicht_die_werte_wirklich_durch(tmp_path):
    """(3) Dasselbe am Modul statt am Text.

    Ein Name in einer Liste ist noch kein Wert an der Aufrufstelle. Diese
    Sonde laedt das ECHTE lib.psm1 mit einer Konfiguration, die jeden Wert
    belegt, und liest zurueck, was drueben ankommt.
    """
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    namen = sorted(_konfigurationswerte())
    projekt = tmp_path / "projekt"
    (projekt / "team").mkdir(parents=True)
    shutil.copy(kit_pfad("lib.psm1"), projekt / "team" / "lib.psm1")
    zeilen = [f'${n} = "wert-{n}"' for n in namen]
    # BL-113: PowerShell-Quelltext traegt ein BOM — auch eine Fixture-Datei,
    # sonst praepariert sich der Test seinen eigenen roten Fall (BL-134).
    (projekt / "team.config.ps1").write_text(
        "\n".join(zeilen) + "\n", encoding="utf-8-sig", newline="\n")
    sonde = ("Import-Module ./team/lib.psm1 -Force 3>$null; "
             + "; ".join(f'Write-Output ("{n}=[" + ${n} + "]")' for n in namen))
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", sonde],
        cwd=projekt, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"
    verloren = [n for n in namen if f"{n}=[wert-{n}]" not in r.stdout]
    assert not verloren, (
        "BL-182: Diese Werte hat die Konfiguration gesetzt, und an der "
        "Aufrufstelle sind sie LEER — sie ueberleben die Modulgrenze nicht:\n  "
        + "\n  ".join(verloren) + f"\nAusgabe der Sonde:\n{r.stdout}")


# --- (4) Alle fuenf Verben, end-to-end ---------------------------------------


KIT_NAME = "ein-kit"


def _baue_kit(tmp_path):
    """Eine Ablage, die kit_meldung.py als Kit erkennen MUSS.

    ABSICHTLICH gestellt statt REPO_ROOT: In der INSTALLIERTEN Ablage ist
    REPO_ROOT das PROJEKT und kein Kit — der Fall waere dort rot statt
    uebersprungen, und die Zwei-Marken-Regel (`BL-153`) weist ihn zu Recht ab.
    Dieselbe zwei Marken wie in test_bl153_rueckkanal_meldung.py.
    """
    kit = tmp_path / KIT_NAME
    for marke in ("bootstrap/CLAUDE.md.vorlage", "geteilt/tools/kosten.py"):
        p = kit / marke
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8", newline="\n")
    (kit / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [2.13.1] — 2026-08-25\n",
        encoding="utf-8", newline="\n")
    return kit


def _fixture_projekt(tmp_path):
    """Ein projektfoermiger Baum, wie ihn kit-melden.ps1 erwartet.

    Das Skript macht `Set-Location $PSScriptRoot`, also muss `team/` als
    Geschwister-Unterordner daneben liegen — dieselbe Bauart wie in
    test_bl142_notizen_bleiben_ein_array.py.
    """
    kit = _baue_kit(tmp_path)
    projekt = tmp_path / "feldprojekt"
    (projekt / "team" / "tools").mkdir(parents=True)
    (projekt / "plans").mkdir()
    shutil.copy(MELDEN_PS1, projekt / "kit-melden.ps1")
    shutil.copy(kit_pfad("lib.psm1"), projekt / "team" / "lib.psm1")
    shutil.copy(kit_pfad("tools", "kit_meldung.py"),
                projekt / "team" / "tools" / "kit_meldung.py")
    (projekt / "team.config.ps1").write_text(
        '$TEAM_PROJEKT = "Pruefprojekt"\n'
        '$TEAM_PLAN_ORDNER = "plans/"\n'
        f'$TEAM_KIT_PFAD = "{kit.as_posix()}"\n'
        '$TEAM_MELDUNG_TOOL = "'
        + werkzeug_wert("team/tools/kit_meldung.py") + '"\n',
        encoding="utf-8-sig", newline="\n")
    return projekt


def _melden(projekt, *args):
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./kit-melden.ps1",
         *args],
        cwd=projekt, capture_output=True, text=True, encoding="utf-8",
        errors="replace")


# Der Wortlaut aus dem Feld. Er ist der Beleg dafuer, dass der Aufruf ueberhaupt
# nicht stattgefunden hat — nicht, dass er etwas Falsches getan haette.
ABBRUCH = "must result in a command name"


def test_kein_verb_stirbt_mehr_am_leeren_interpreter(tmp_path):
    """Alle fuenf, weil im Feld alle fuenf betroffen waren.

    `senden` laeuft hier bewusst OHNE `--ja`: Es muss die Bestaetigungsfrage
    erreichen und daran scheitern (BL-153) — nicht schon an der Aufrufzeile.
    Ein Test, der `senden` auslaesst, laesst das Verb ungeprueft, das als
    einziges nach aussen wirkt.
    """
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    projekt = _fixture_projekt(tmp_path)
    entwurf = "plans/kit-meldungen/entwurf.md"
    (projekt / "plans" / "kit-meldungen").mkdir(parents=True)
    (projekt / entwurf).write_text("# Ein Titel\n\nEin Satz.\n",
                                   encoding="utf-8", newline="\n")
    for argumente in (["kit-pfad"], ["neu", "--titel", "Ein Fund am Kit"],
                      ["pruefen", entwurf], ["issue-link", entwurf],
                      ["senden", entwurf]):
        r = _melden(projekt, *argumente)
        aus = r.stdout + r.stderr
        assert ABBRUCH not in aus, (
            f"BL-182 ist zurueck — `{argumente[0]}` hat das Werkzeug gar nicht "
            f"erreicht:\n{aus}")


def test_kit_pfad_findet_das_kit_das_die_konfiguration_nennt(tmp_path):
    """Die zweite Haelfte, an ihrer Wirkung gemessen.

    Vor dem Fix meldete `kit-pfad` "Kein Kit gefunden — weder TEAM_KIT_PFAD
    noch die ueblichen Ablagen" GENAU DANN, wenn der Wert eingetragen war. Eine
    Diagnose, die das Gegenteil ihrer Lage behauptet, schickt den Melder auf
    die Suche nach einem Fehler, den er nicht hat.
    """
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    projekt = _fixture_projekt(tmp_path)
    r = _melden(projekt, "kit-pfad")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, f"Exit {r.returncode}:\n{aus}"
    assert "TEAM_KIT_PFAD" not in r.stderr, (
        "kit-pfad verlangt den Wert, den die Konfiguration bereits traegt — "
        f"er kommt an der Aufrufstelle nicht an:\n{aus}")
    assert KIT_NAME in r.stdout, (
        f"kit-pfad nennt das Kit aus der Konfiguration nicht:\n{aus}")


def test_neu_legt_die_meldung_im_projekt_ab(tmp_path):
    """Das Verb, mit dem im Feld alles anfaengt — und das dort nie lief."""
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    projekt = _fixture_projekt(tmp_path)
    r = _melden(projekt, "neu", "--titel", "Der Installer schreibt CRLF")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, f"Exit {r.returncode}:\n{aus}"
    # ABSICHTLICH die GANZE Ausgabe, nicht die letzte Zeile: `neu` gibt genau
    # einen Pfad aus, und wer ihn wegliest, tut das so. Siehe den Test darunter.
    ziel = projekt / r.stdout.strip().replace("\\", "/")
    assert ziel.is_file(), f"neu hat keinen Pfad ausgegeben, den es gibt:\n{aus}"
    assert ziel.parent.name == "kit-meldungen", (
        f"Die Meldung liegt nicht unter <plan>/kit-meldungen: {ziel}")


def test_neu_gibt_den_pfad_allein_aus(tmp_path):
    """Die dritte Haelfte von BL-182 — an ihrer Wirkung gemessen.

    `kit-melden.ps1` war der EINZIGE der zehn Entrypoints ohne
    `-DisableNameChecking`. Ohne den Schalter schreibt Import-Module eine
    WARNING ueber "unapproved verbs" nach STDOUT (nicht stderr), mit
    ANSI-Farbcode, VOR der Nutzausgabe. Bei den neun anderen waere das
    Kosmetik; hier ist stdout ein PFAD, den ein Aufrufer weiterverwendet.

    Gesehen hat es nie jemand: Der Aufruf brach eine Zeile spaeter ohnehin ab.
    So sammeln sich in einer nie gelaufenen Datei mehrere Fehler an, und der
    erste verdeckt die anderen.
    """
    verlange_pwsh()
    ueberspringe_ohne_bahn("pwsh")
    projekt = _fixture_projekt(tmp_path)
    r = _melden(projekt, "neu", "--titel", "Nur der Pfad")
    assert r.returncode == 0, f"Exit {r.returncode}:\n{r.stdout}{r.stderr}"
    zeilen = [z for z in r.stdout.splitlines() if z.strip()]
    assert len(zeilen) == 1, (
        "stdout traegt mehr als den Pfad — ein Aufrufer, der ihn wegliest, "
        f"bekommt Beifang:\n{zeilen}")
    assert "\x1b[" not in r.stdout, (
        f"stdout traegt ANSI-Steuerzeichen: {r.stdout!r}")


def test_jeder_entrypoint_importiert_ohne_namenspruefung():
    """Die Gattung statt der Stelle — hier war es 9 zu 1.

    Ein Schalter, den neun von zehn Dateien tragen, ist keine Vorliebe mehr,
    sondern die Bauform dieser Bahn. Der Riegel haelt sie fest, damit die
    zehnte Datei nicht wieder die Ausnahme wird.
    """
    ueberspringe_ohne_bahn("pwsh")
    ordner = MELDEN_PS1.parent
    fehlt = []
    for p in sorted(ordner.glob("*.ps1")):
        for zeile in _lies(p).splitlines():
            if zeile.lstrip().startswith("#") or "Import-Module" not in zeile:
                continue
            if "lib.psm1" in zeile and "-DisableNameChecking" not in zeile:
                fehlt.append(p.name)
    assert not fehlt, (
        "BL-182: Diese Entrypoints importieren lib.psm1 ohne "
        "-DisableNameChecking und schreiben deshalb eine WARNING nach "
        "STDOUT, vor ihre eigene Ausgabe:\n  " + "\n  ".join(fehlt))


# --- (5) Gegenprobe -----------------------------------------------------------


def test_gegenprobe_der_alte_aufruf_scheitert_wirklich():
    """Ohne diesen Fall wuesste niemand, ob (4) ueberhaupt etwas absichert.

    Er stellt die alte Zeile nach: eine nicht gesetzte Variable hinter `&`.
    """
    verlange_pwsh()
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command",
         "& $TEAM_GIBTSNICHT team/tools/kit_meldung.py kit-pfad"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode != 0, "Der alte Aufruf laeuft durch — die Sonde trifft nicht."
    assert ABBRUCH in (r.stdout + r.stderr), (
        "Der Gegenbeweis greift nicht mehr: `&` auf eine leere Variable bricht "
        f"hier anders ab als im Feld.\n{r.stdout}\n{r.stderr}")

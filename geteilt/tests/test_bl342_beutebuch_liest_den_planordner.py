#!/usr/bin/env python3
"""BL-342: `beutebuch.py` las den Planordner nicht — bei einem anderen
`TEAM_PLAN_ORDNER` fand es still keinen Fund, und die Fix-Phase hatte nichts
zu tun.

DER BEFUND (Beifang der Triage, 2026-10-17)
    Das Werkzeug verdrahtete `plans/beutebuch.md` und `plans/beutebuch-archiv.md`.
    Den Schalter `--pfad` gibt es, aber kein Aufrufer uebergibt ihn
    (`TEAM_BEUTEBUCH_TOOL` in beiden Konfigurationen). Fehlte die Datei, lieferte
    es eine leere Liste statt eines Fehlers. Mit einem anderen Planordner meldet
    Frank dann „nichts zu tun" und der Sweep „keine neuen Funde" — genau der
    stille Pfad aus `BL-1`, nur eine Ebene hoeher. `kosten.py`, `kit_meldung.py`
    und `schreibzone.py` lesen `TEAM_PLAN_ORDNER` seit `BL-209`; beide
    Konfigurationen exportieren ihn dafuer.

    Gemessen an einer Wegwerf-Installation mit Planordner `docs/plans`:
    `test_bl324` (drei Faelle), `test_bl47` (zwei) und `test_bl114` (einer)
    rot, auch ohne Rollenumgebung. Der Waechter fuer genau diese Gattung
    (`test_bl1`) uebersprang sich, sobald `plans/beutebuch.md` fehlte.

DER FIX
    Beide Pfade kommen aus `TEAM_PLAN_ORDNER`, mit `plans` als Rueckfall —
    dieselbe Regel wie `plan_ordner()` in `kosten.py`. Ein fehlendes Beutebuch
    wird auf stderr GEMELDET. Als Warnung und nicht als Fehler: Ausgabe und
    Exit bleiben die eines leeren Buchs, weil die Rollen beides auswerten —
    `redteam.sh` liest `next-id` unter `set -e`, `redteam.ps1` ruft `.Trim()`
    auf die Ausgabe, `frank.*` und die Vollautomatik werten `first`/`list` an
    Exit und stdout aus. Ein neuer Exit-Code haette jede dieser Stellen
    gebrochen, statt sie aufzuklaeren.

WAS HIER GEPRUEFT WIRD
    Am Werkzeug: Buch und Archiv liegen im Planordner, ohne ihn gilt `plans`,
    ein fehlendes Buch wird gemeldet — mit derselben Ausgabe und demselben Exit
    wie ein leeres. An der Konfiguration, beide Bahnen: Wer sie sourct, landet
    mit `TEAM_BEUTEBUCH_TOOL` im konfigurierten Ordner (im Kit an der Vorlage
    mit `docs/plans`, in einer Installation am eingetragenen Wert).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, PYTHON_BEFEHL, kit_pfad, verlange_bash,
                      verlange_pwsh)

WURZEL = Path(__file__).resolve().parents[2]
TOOL = kit_pfad("tools", "beutebuch.py")

# Zusammengesetzt, nicht geschrieben (test_bl131, test_bl163): Stufe 3 von
# kit-test.sh meldet jede installierte Datei mit einer ungefuellten Marke.
MARKE_PLAN = "".join(("{{", "PLAN_ORDNER", "}}"))
MARKE_PYTHON = "".join(("{{", "PYTHON", "}}"))

STATUS = "an Frank übergeben"
BUCH = (
    "# Beutebuch\n\n"
    "## Funde\n\n"
    "### HM-4 — Fund im eigenen Planordner\n"
    "- **Angreifer**: Harry\n"
    f"- **Status**: {STATUS}\n"
    "- **Reproducer-Test**: `tests/test_hm4_planordner.py`\n"
)
ARCHIV = (
    "### HM-9 — Archivierter Fund\n"
    "- **Status**: erledigt (Frank-Fix, abc1234)\n"
)
LEERES_BUCH = "# Beutebuch\n\n## Funde\n"


def _projekt(tmp_path):
    """Ein Projekt mit dem Werkzeug unter team/tools/ — wie im Feld."""
    projekt = tmp_path / "projekt"
    (projekt / "team" / "tools").mkdir(parents=True)
    shutil.copy(TOOL, projekt / "team" / "tools" / "beutebuch.py")
    return projekt


def _schreibe(pfad, text):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(text, encoding="utf-8", newline="\n")


def _umgebung(plan_ordner=None):
    """Die Umgebung des Aufrufs — der Planordner ausdruecklich gesetzt oder
    ausdruecklich entfernt, nie geerbt (Kit-BL-328)."""
    umgebung = {k: v for k, v in os.environ.items() if k != "TEAM_PLAN_ORDNER"}
    if plan_ordner is not None:
        umgebung["TEAM_PLAN_ORDNER"] = plan_ordner
    return umgebung


def _werkzeug(projekt, *argumente, plan_ordner=None):
    """Ruft das Werkzeug aus einem FREMDEN Arbeitsverzeichnis — ein
    versehentlich cwd-relativer Pfad fiele sonst nicht auf (Bauart BL-1)."""
    fremd = projekt.parent / "woanders"
    fremd.mkdir(exist_ok=True)
    return subprocess.run(
        [sys.executable, str(projekt / "team" / "tools" / "beutebuch.py"),
         *argumente],
        cwd=fremd, env=_umgebung(plan_ordner), capture_output=True, text=True,
        encoding="utf-8", errors="replace")


# --- Das Werkzeug ---------------------------------------------------------------

def test_das_werkzeug_liest_den_planordner(tmp_path):
    """Der Befund: ein Fund in `docs/plans/beutebuch.md`, gesucht wurde in
    `plans/`. Der Wert so, wie `team.config.sh` ihn exportiert — mit
    abschliessendem Schraegstrich."""
    projekt = _projekt(tmp_path)
    _schreibe(projekt / "docs" / "plans" / "beutebuch.md", BUCH)
    liste = _werkzeug(projekt, "list", plan_ordner="docs/plans/")
    assert liste.returncode == 0, liste.stderr
    assert liste.stdout.strip() == f"HM-4\t{STATUS}", (
        "beutebuch.py liest den konfigurierten Planordner nicht — Frank meldet "
        "dann 'nichts zu tun', obwohl ein Fund auf ihn wartet (Kit-BL-342).\n"
        f"stdout: {liste.stdout!r}\nstderr: {liste.stderr}")
    erster = _werkzeug(projekt, "first", STATUS, plan_ordner="docs/plans/")
    assert erster.returncode == 0 and erster.stdout.strip() == "HM-4", (
        f"`first` findet den Fund nicht: {erster.stdout!r} {erster.stderr}")


def test_das_archiv_liegt_im_selben_ordner(tmp_path):
    """Buch und Archiv bilden zusammen den Nummernraum (Stufe 91). Ein Archiv
    ausserhalb des Planordners liesse `next-id` eine vergebene Nummer neu
    vergeben."""
    projekt = _projekt(tmp_path)
    _schreibe(projekt / "docs" / "plans" / "beutebuch.md", BUCH)
    _schreibe(projekt / "docs" / "plans" / "beutebuch-archiv.md", ARCHIV)
    naechste = _werkzeug(projekt, "next-id", plan_ordner="docs/plans")
    assert naechste.stdout.strip() == "HM-10", (
        "next-id sieht das Archiv im Planordner nicht und vergaebe eine "
        f"Nummer doppelt (Kit-BL-342): {naechste.stdout!r} {naechste.stderr}")
    alle = _werkzeug(projekt, "list", "--alle", plan_ordner="docs/plans")
    assert "HM-9\t" in alle.stdout, alle.stdout + alle.stderr


@pytest.mark.parametrize("plan_ordner", [None, "", "plans", "plans/"])
def test_ohne_planordner_gilt_plans(tmp_path, plan_ordner):
    """Der Rueckfall — dieselbe Regel wie `plan_ordner()` in kosten.py: nicht
    gesetzt oder leer heisst `plans`."""
    projekt = _projekt(tmp_path)
    _schreibe(projekt / "plans" / "beutebuch.md", BUCH)
    liste = _werkzeug(projekt, "list", plan_ordner=plan_ordner)
    assert liste.returncode == 0, liste.stderr
    assert liste.stdout.strip() == f"HM-4\t{STATUS}", liste.stdout + liste.stderr
    assert "Kit-BL-342" not in liste.stderr, (
        f"Ein vorhandenes Buch darf keine Warnung ausloesen: {liste.stderr}")


def test_ein_fehlendes_beutebuch_wird_gemeldet(tmp_path):
    """Die zweite Haelfte: Leer zu antworten, als waere nichts gefunden, ist
    der stille Pfad. Die Meldung nennt den Pfad und woher er kommt."""
    projekt = _projekt(tmp_path)
    (projekt / "docs" / "plans").mkdir(parents=True)
    liste = _werkzeug(projekt, "list", plan_ordner="docs/plans/")
    assert "docs/plans/beutebuch.md" in liste.stderr, (
        "Ein fehlendes Beutebuch wird nicht gemeldet — das Werkzeug antwortet "
        "wie fuer ein leeres Buch, und die Rolle meldet 'nichts zu tun' "
        f"(Kit-BL-342).\nstderr: {liste.stderr!r}")
    assert "TEAM_PLAN_ORDNER" in liste.stderr and "Kit-BL-342" in liste.stderr, (
        f"Die Meldung sagt nicht, woher der Pfad kommt: {liste.stderr!r}")


@pytest.mark.parametrize("befehl", [
    pytest.param(("list",), id="list"),
    pytest.param(("list", "--alle"), id="list-alle"),
    pytest.param(("count",), id="count"),
    pytest.param(("next-id",), id="next-id"),
    pytest.param(("first", STATUS), id="first"),
    pytest.param(("lint",), id="lint"),
    pytest.param(("dateien", "HM-1"), id="dateien"),
    pytest.param(("reproducer", "HM-1"), id="reproducer"),
    pytest.param(("set", "HM-1", "erledigt"), id="set"),
    pytest.param(("archiviere", "--dry-run"), id="archiviere"),
])
def test_die_meldung_aendert_weder_ausgabe_noch_exit(tmp_path, befehl):
    """Warnung, kein Fehler: Die Rollen werten Exit und stdout aus — unter
    `set -e` (`redteam.sh`), mit `.Trim()` auf die Ausgabe (`redteam.ps1`),
    ueber `first`-Exit-Codes (`frank.*`, Vollautomatik). Gegen ein leeres Buch
    verglichen, unterscheidet sich ein fehlendes NUR durch die Meldung."""
    fehlt = _projekt(tmp_path / "fehlt")
    leer = _projekt(tmp_path / "leer")
    _schreibe(leer / "docs" / "plans" / "beutebuch.md", LEERES_BUCH)
    ohne = _werkzeug(fehlt, *befehl, plan_ordner="docs/plans")
    mit = _werkzeug(leer, *befehl, plan_ordner="docs/plans")
    assert (ohne.returncode, ohne.stdout) == (mit.returncode, mit.stdout), (
        "Ein fehlendes Buch aendert Exit oder Ausgabe — die Rollen brechen "
        f"daran (Kit-BL-342).\nfehlt: {ohne.returncode} {ohne.stdout!r}\n"
        f"leer:  {mit.returncode} {mit.stdout!r}")
    assert "Kit-BL-342" in ohne.stderr, (
        f"`{' '.join(befehl)}` meldet das fehlende Buch nicht: {ohne.stderr!r}")
    assert "Kit-BL-342" not in mit.stderr, (
        f"Ein vorhandenes, leeres Buch ist kein fehlendes: {mit.stderr!r}")


# --- Die Konfiguration: wie die Rollen das Werkzeug wirklich rufen --------------

def _ist_kit():
    return (WURZEL / "bootstrap" / "CLAUDE.md.vorlage").is_file()


def _konfiguration(tmp_path, bahn):
    """Ein Projekt mit der Konfiguration DIESER Ablage.

    Im Kit die Vorlage, gefuellt wie vom Installer mit Planordner `docs/plans`
    (nur die zwei Marken, die der Aufruf braucht). In einer Installation die
    eingetragene Konfiguration, wie sie ist — dort gilt der Planordner, den
    der Mensch beim Einrichten gewaehlt hat."""
    name = "team.config.sh" if bahn == "bash" else "team.config.ps1"
    projekt = _projekt(tmp_path)
    if _ist_kit():
        vorlage = WURZEL / bahn / "entry" / name
        text = vorlage.read_text(encoding="utf-8-sig")
        text = text.replace(MARKE_PLAN, "docs/plans").replace(
            MARKE_PYTHON, PYTHON_BEFEHL)
        kodierung = "utf-8" if bahn == "bash" else "utf-8-sig"
        (projekt / name).write_text(text, encoding=kodierung, newline="\n")
    else:
        if not (WURZEL / name).is_file():
            pytest.skip(f"{name} liegt in dieser Ablage nicht")
        shutil.copy(WURZEL / name, projekt / name)
    return projekt


def _ohne_projektwerte():
    """Planordner und Werkzeugzeile kommen aus der KONFIGURATION, nicht aus
    der Sitzung, in der die Suite laeuft."""
    return {k: v for k, v in os.environ.items()
            if k not in ("TEAM_PLAN_ORDNER", "TEAM_BEUTEBUCH_TOOL",
                         "TEAM_BEUTEBUCH")}


BASH_KONFIG = 'source ./team.config.sh && printf "%s" "$TEAM_PLAN_ORDNER"'
BASH_LISTE = 'source ./team.config.sh && $TEAM_BEUTEBUCH_TOOL list'
# Wie Team-Werkzeug in lib.psm1: die Werkzeugzeile an Leerraum zerlegen.
# Rohe Zeichenketten — der regulaere Ausdruck traegt einen Rueckstrich (BL-327).
PWSH_KONFIG = r". ./team.config.ps1; [Console]::Out.Write($TEAM_PLAN_ORDNER)"
PWSH_LISTE = (r". ./team.config.ps1; "
              r"$teile = @($TEAM_BEUTEBUCH_TOOL -split '\s+' | Where-Object { $_ }); "
              r"$rest = @(); if ($teile.Count -gt 1) { $rest = $teile[1..($teile.Count - 1)] }; "
              r"& $teile[0] @($rest + @('list')); exit $LASTEXITCODE")


def _schale(bahn, befehl, projekt):
    if bahn == "bash":
        aufruf = [BASH, "-c", befehl]
    else:
        aufruf = ["pwsh", "-NoProfile", "-NonInteractive", "-Command", befehl]
    return subprocess.run(aufruf, cwd=projekt, env=_ohne_projektwerte(),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=120)


# Als Tupel: Eine Liste, die mit "bash" beginnt, haelt der Waechter aus BL-130
# zu Recht fuer einen Aufruf ueber den WSL-Launcher (wie in test_bl324).
BAHNEN = ("bash", "pwsh")


@pytest.mark.parametrize("bahn", BAHNEN)
def test_die_konfiguration_fuehrt_das_werkzeug_in_den_planordner(tmp_path, bahn):
    """Der Weg der Rollen: Konfiguration laden, `TEAM_BEUTEBUCH_TOOL` rufen —
    ohne `--pfad`. Im Kit mit `docs/plans`, also genau dem Fall, den keine
    Stufe des Selbsttests installiert."""
    (verlange_bash if bahn == "bash" else verlange_pwsh)()
    projekt = _konfiguration(tmp_path, bahn)
    ordner = _schale(bahn, BASH_KONFIG if bahn == "bash" else PWSH_KONFIG,
                     projekt)
    assert ordner.returncode == 0 and ordner.stdout.strip(), (
        f"Die Konfiguration nennt keinen Planordner:\n{ordner.stdout}\n"
        f"{ordner.stderr}")
    _schreibe(projekt / ordner.stdout.strip() / "beutebuch.md", BUCH)
    liste = _schale(bahn, BASH_LISTE if bahn == "bash" else PWSH_LISTE,
                    projekt)
    assert liste.returncode == 0, liste.stdout + liste.stderr
    assert f"HM-4\t{STATUS}" in liste.stdout, (
        f"Mit Planordner {ordner.stdout.strip()!r} findet "
        "TEAM_BEUTEBUCH_TOOL den eingetragenen Fund nicht — die Fix-Phase "
        f"haette nichts zu tun (Kit-BL-342).\nstdout: {liste.stdout!r}\n"
        f"stderr: {liste.stderr}")

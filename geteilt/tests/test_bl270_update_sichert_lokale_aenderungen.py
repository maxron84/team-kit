#!/usr/bin/env python3
"""BL-270 (mit BL-139 und BL-237): Das Update sagt, was es an Aenderungen im
Projekt ersetzt, und sichert sie vorher.

DER FELDBEFUND (`Feld B`, 2026-09-17, zweimal am selben Tag)
    Ein `--update` hat drei bewusst gesetzte Stellen ueberschrieben: einen
    ueber Fund, Fix und Reproducer eingebauten Waechter in `team/lib.psm1`,
    den ausgefuellten Commit-Entscheid in `rolle-architekt.md` (dort stand
    danach wieder der ungefuellte Platzhalter, die Rueckkehr von `BL-139`) und eine
    Projektausnahme im Briefing der bauenden Rolle. Gemeldet wurde nichts —
    fuer die Briefings KONNTE die alte Pruefung nichts melden, weil eine
    gerenderte Datei immer von der Kit-Fassung abweicht.

DIE PROBE
    Das Update merkt sich in `team/.kit-stand`, was es geschrieben hat. Eine
    seither geaenderte Kit-Datei wird gesichert (`backups/update-<zeit>/`) und
    namentlich gemeldet; eine unveraenderte meldet nichts, auch wenn das Kit
    sie neu ausliefert. Ohne Liste wird einmal alles gesichert.

BL-237 nebenbei: Derselbe Projektaufbau traegt die Probe fuer den
Schreibzonen-Hinweis im Statusbericht beider Bahnen.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, verlange_bash, verlange_pwsh

REPO_ROOT = Path(__file__).resolve().parents[2]
for _tools in (REPO_ROOT / "geteilt" / "tools", REPO_ROOT / "team" / "tools"):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kit_stand  # noqa: E402

INSTALL_SH = REPO_ROOT / "bash" / "install.sh"
INSTALL_PS1 = REPO_ROOT / "pwsh" / "install.ps1"


def _git(ziel, *args):
    return subprocess.run(["git", "-C", str(ziel), *args], check=True,
                          capture_output=True, text=True, encoding="utf-8")


def _projekt(tmp_path):
    ziel = tmp_path / "projekt"
    ziel.mkdir()
    _git(ziel, "init", "-q")
    _git(ziel, "config", "user.email", "t@l")
    _git(ziel, "config", "user.name", "T")
    return ziel


def _bash_install(ziel, *extra):
    if not INSTALL_SH.is_file():
        pytest.skip("install.sh liegt nur im Kit")
    r = subprocess.run([BASH, str(INSTALL_SH), str(ziel), "--nicht-interaktiv",
                        "--ohne-selbsttest", *extra], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def _pwsh_install(ziel, *extra):
    if not INSTALL_PS1.is_file():
        pytest.skip("install.ps1 liegt nur im Kit")
    r = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File",
                        str(INSTALL_PS1), str(ziel), "-NichtInteraktiv",
                        "-OhneSelbsttest", *extra], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


@pytest.fixture(scope="module")
def _bash_vorlage(tmp_path_factory):
    """EINE Erstinstallation je Bahn fuer alle Faelle — jeder Fall bekommt
    eine Kopie. Ein Installerlauf kostet rund eine halbe Minute."""
    verlange_bash()
    ziel = _projekt(tmp_path_factory.mktemp("bash"))
    rc, aus = _bash_install(ziel)
    assert rc == 0, aus[-1500:]
    return ziel


@pytest.fixture(scope="module")
def _pwsh_vorlage(tmp_path_factory):
    verlange_pwsh()
    ziel = _projekt(tmp_path_factory.mktemp("pwsh"))
    rc, aus = _pwsh_install(ziel, "-NurPwsh")
    assert rc == 0, aus[-1500:]
    return ziel


def _kopie(vorlage, tmp_path):
    ziel = tmp_path / "projekt"
    shutil.copytree(vorlage, ziel, symlinks=True)
    return ziel


def _anhaengen(pfad, text):
    with open(pfad, "a", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _sicherungen(ziel):
    return sorted(p.relative_to(ziel).as_posix()
                  for p in (ziel / "backups").rglob("*") if p.is_file())


# --- Die Pruefsumme ------------------------------------------------------------

def test_zeilenende_und_bom_sind_keine_aenderung(tmp_path):
    """Ein Checkout mit core.autocrlf ist keine Aenderung im Projekt."""
    a, b, c = tmp_path / "a", tmp_path / "b", tmp_path / "c"
    a.write_bytes(b"zeile 1\nzeile 2\n")
    b.write_bytes(b"\xef\xbb\xbfzeile 1\r\nzeile 2\r\n")
    c.write_bytes(b"zeile 1\nzeile 3\n")
    assert kit_stand.pruefsumme(a) == kit_stand.pruefsumme(b)
    assert kit_stand.pruefsumme(a) != kit_stand.pruefsumme(c)


# --- bash -------------------------------------------------------------------------

def test_bash_eine_geaenderte_kit_datei_wird_gesichert_und_genannt(
        tmp_path, _bash_vorlage):
    ziel = _kopie(_bash_vorlage, tmp_path)
    assert (ziel / "team" / ".kit-stand").is_file(), (
        "Die Erstinstallation schreibt keine Pruefsummenliste")
    _anhaengen(ziel / "team" / "tools" / "beutebuch.py", "# eigener Waechter\n")
    _anhaengen(ziel / "team" / "prompts" / "rolle-ralph.md", "Projektausnahme\n")
    rc, aus = _bash_install(ziel, "--update")
    assert rc == 0, aus[-1500:]
    assert "Kit-BL-270" in aus and "Im Projekt geaendert" in aus, aus[-2500:]
    assert "team/tools/beutebuch.py" in aus
    assert "team/prompts/rolle-ralph.md" in aus, (
        "Ein gerendertes Briefing faellt nicht mehr durch die Pruefung — "
        "genau dort lagen zwei der drei Feldfaelle")
    gesichert = _sicherungen(ziel)
    assert any(s.endswith("team/tools/beutebuch.py") for s in gesichert), gesichert
    assert any(s.endswith("team/prompts/rolle-ralph.md") for s in gesichert), (
        f"Beide Dateien gehoeren in die Sicherung, nicht nur die letzte "
        f"(unter Windows hing ein \\r am Pfad):\n{gesichert}")
    alt = next(p for p in (ziel / "backups").rglob("beutebuch.py"))
    assert "# eigener Waechter" in alt.read_text(encoding="utf-8")
    assert "# eigener Waechter" not in (
        ziel / "team" / "tools" / "beutebuch.py").read_text(encoding="utf-8")


def test_bash_ein_update_ohne_aenderung_meldet_nichts(tmp_path, _bash_vorlage):
    """Gegenrichtung (BL-14): Eine Kit-Neuerung allein ist keine Aenderung im
    Projekt — die Meldung kommt nur, wenn sie etwas bedeutet."""
    ziel = _kopie(_bash_vorlage, tmp_path)
    rc, aus = _bash_install(ziel, "--update")
    assert rc == 0, aus[-1500:]
    assert "Im Projekt geaendert" not in aus and "Erstes Update" not in aus, aus
    assert not (ziel / "backups").exists() or not _sicherungen(ziel)


def test_bash_ohne_liste_wird_einmal_alles_gesichert(tmp_path, _bash_vorlage):
    ziel = _kopie(_bash_vorlage, tmp_path)
    (ziel / "team" / ".kit-stand").unlink()
    rc, aus = _bash_install(ziel, "--update")
    assert rc == 0, aus[-1500:]
    assert "Erstes Update mit Pruefsummenliste" in aus, aus[-2500:]
    assert any(s.endswith("team/lib.sh") for s in _sicherungen(ziel))
    assert (ziel / "team" / ".kit-stand").is_file(), (
        "Nach dem Update muss die Liste da sein, sonst sichert jedes "
        "weitere Update wieder alles")


def test_bash_ein_platzhalter_ist_kein_commit_entscheid(tmp_path, _bash_vorlage):
    """BL-139 kehrte zurueck: Stand der Platzhalter einmal im Briefing, rettete
    jedes Update ihn als "Entscheid" weiter."""
    ziel = _kopie(_bash_vorlage, tmp_path)
    briefing = ziel / "team" / "prompts" / "rolle-architekt.md"
    zeilen = briefing.read_text(encoding="utf-8").splitlines(keepends=True)
    # Zusammengesetzt, nicht ausgeschrieben: Schritt 3 des Selbsttests haelt
    # jede ausgeschriebene Marke in einer Testdatei fuer einen ungefuellten
    # Platzhalter (BL-163).
    marke = "".join(("{{", "COMMIT_ENTSCHEID", "}}"))
    zeilen = [(f"**Committen:** {marke}\n"
               if z.startswith("**Committen:**") else z) for z in zeilen]
    briefing.write_text("".join(zeilen), encoding="utf-8")
    rc, aus = _bash_install(ziel, "--update")
    assert rc == 0, aus[-1500:]
    commit = [z for z in briefing.read_text(encoding="utf-8").splitlines()
              if z.startswith("**Committen:**")]
    assert commit and "{{" not in commit[0], commit


# --- pwsh -------------------------------------------------------------------------

def test_pwsh_eine_geaenderte_kit_datei_wird_gesichert_und_genannt(
        tmp_path, _pwsh_vorlage):
    ziel = _kopie(_pwsh_vorlage, tmp_path)
    if not (ziel / "team" / ".kit-stand").is_file():
        pytest.skip("kein Python fuer den pwsh-Installer — ohne Liste keine Probe")
    _anhaengen(ziel / "team" / "lib.psm1", "# eigener Waechter\r\n")
    rc, aus = _pwsh_install(ziel, "-Update")
    assert rc == 0, aus[-1500:]
    assert "Kit-BL-270" in aus and "team/lib.psm1" in aus, aus[-2500:]
    assert any(s.endswith("team/lib.psm1") for s in _sicherungen(ziel))


# --- BL-237: der Hinweis im Statusbericht ------------------------------------------

def test_bash_der_status_nennt_fremdes_in_der_schreibzone(tmp_path, _bash_vorlage):
    ziel = _kopie(_bash_vorlage, tmp_path)
    (ziel / "plans" / "pruefskript.py").write_text("print(1)\n", encoding="utf-8")
    r = subprocess.run([BASH, "./team-status.sh"], cwd=ziel, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    aus = r.stdout + r.stderr
    assert "Schreibzone" in aus and "plans/pruefskript.py" in aus, aus[-2000:]
    assert "NICHT im Pruefumfang" in aus and "Kit-BL-237" in aus


def test_pwsh_der_status_nennt_fremdes_in_der_schreibzone(tmp_path, _pwsh_vorlage):
    ziel = _kopie(_pwsh_vorlage, tmp_path)
    (ziel / "plans" / "gestaltung.md").write_text("verbindlich\n",
                                                  encoding="utf-8")
    r = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File",
                        "./team-status.ps1"], cwd=ziel, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    aus = r.stdout + r.stderr
    assert "Schreibzone" in aus and "plans/gestaltung.md" in aus, aus[-2000:]

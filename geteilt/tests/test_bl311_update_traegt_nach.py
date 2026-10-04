#!/usr/bin/env python3
"""BL-311: Das Update traegt Neues aus der Kit-Fassung selbst nach — nur echte
Widersprueche bleiben beim Menschen.

DER ANLASS (`Feld F`, 2026-10-04)
    Nach einem Update standen drei Handgriffe im Bericht: eine fehlende
    `.gitignore`-Zeile, zwei fehlende Konfigurationswerte, eine CLAUDE.md mit
    178 abweichenden Zeilen. Der Mensch fragte, warum das nicht automatisch
    geschieht. Die Antwort war richtig und unbefriedigend: Eine fehlende
    Zeile kann eine bewusst entfernte sein — unterscheiden liess sich das
    nicht, weil niemand wusste, was die Kit-Fassung beim letzten Mal war.

DIE REGEL
    `team/.kit-basis/` haelt die Kit-Seite vom letzten Update. NEU seit damals
    wird eingetragen; damals schon da und im Projekt weg heisst bewusst
    entfernt und wird nur gemeldet. Die CLAUDE.md geht durch einen
    Dreiwege-Abgleich: ohne Konflikt eingearbeitet und gesichert, mit Konflikt
    unangetastet und ein Vorschlag daneben. Der Abgleich von Hand am selben Tag
    (Basis 2026-09-26, Projekt, Kit-Fassung) ergab drei Konfliktstellen bei
    rund achtzig neuen Zeilen.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if Path(_tools).is_dir():
        sys.path.insert(0, str(_tools))
        break
import kit_basis  # noqa: E402

TOOL = kit_pfad("tools", "kit_basis.py")


def _marke(name):
    """Ein Installer-Platzhalter, zur Laufzeit zusammengesetzt — woertlich in
    einer Testdatei meldete ihn der Selbsttest als ungefuellt (BL-163)."""
    return "{" * 2 + name + "}" * 2


def _kit(tmp_path, fragment, sh="", ps1=""):
    kit = tmp_path / "kit"
    (kit / "bootstrap").mkdir(parents=True)
    (kit / "bash" / "entry").mkdir(parents=True)
    (kit / "pwsh" / "entry").mkdir(parents=True)
    (kit / "bootstrap" / "gitignore.fragment").write_text(fragment, encoding="utf-8")
    if sh:
        (kit / "bash" / "entry" / "team.config.sh").write_text(sh, encoding="utf-8")
    if ps1:
        (kit / "pwsh" / "entry" / "team.config.ps1").write_text(ps1, encoding="utf-8-sig")
    return kit


def _basis(projekt, name, text):
    pfad = projekt / "team" / ".kit-basis" / name
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(text, encoding="utf-8")


# --- .gitignore -------------------------------------------------------------------

FRAGMENT_ALT = "# Laufzeit\n.team-logs/\n.team-focus-harry\n"
FRAGMENT_NEU = FRAGMENT_ALT + "# BL-242: Protokolle. NIE versionieren.\n.team-protokolle/\n"


def test_eine_neue_zeile_wird_eingetragen_eine_entfernte_nicht(tmp_path, capsys):
    kit = _kit(tmp_path, FRAGMENT_NEU)
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    # .team-focus-harry hat das Projekt bewusst entfernt: Sie stand in der Basis.
    (projekt / ".gitignore").write_text("node_modules/\n.team-logs/\n", encoding="utf-8")
    _basis(projekt, "gitignore.fragment", FRAGMENT_ALT)
    assert kit_basis.gitignore(str(projekt), str(kit)) == 0
    text = (projekt / ".gitignore").read_text(encoding="utf-8")
    assert ".team-protokolle/" in text.split("\n"), text
    assert "# BL-242: Protokolle. NIE versionieren." in text, "der Kommentar gehoert dazu"
    assert ".team-focus-harry" not in text, (
        "Eine Zeile, die beim letzten Update schon in der Vorlage stand und im "
        "Projekt fehlt, ist bewusst entfernt — sie kommt nicht zurueck (BL-109).")
    assert "Kit-BL-311" in capsys.readouterr().out


def test_ohne_basis_wird_nichts_eingetragen(tmp_path):
    """Ein Projekt aus der Zeit davor: Ob eine Zeile neu oder entfernt ist, ist
    nicht entscheidbar — dann bleibt es beim Melden wie bisher."""
    kit = _kit(tmp_path, FRAGMENT_NEU)
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    (projekt / ".gitignore").write_text(".team-logs/\n", encoding="utf-8")
    kit_basis.gitignore(str(projekt), str(kit))
    assert (projekt / ".gitignore").read_text(encoding="utf-8") == ".team-logs/\n"


def test_crlf_bleibt_crlf(tmp_path):
    kit = _kit(tmp_path, FRAGMENT_NEU)
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    (projekt / ".gitignore").write_bytes(b".team-logs/\r\n.team-focus-harry\r\n")
    _basis(projekt, "gitignore.fragment", FRAGMENT_ALT)
    kit_basis.gitignore(str(projekt), str(kit))
    roh = (projekt / ".gitignore").read_bytes()
    assert b".team-protokolle/\r\n" in roh and b"\n" not in roh.replace(b"\r\n", b"")


# --- Konfiguration ----------------------------------------------------------------

SH = ('TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-./smoke.sh}"\n'
      '# Wie lange der Test laufen darf.\n'
      'TEAM_SMOKE_TEST_TIMEOUT="${TEAM_SMOKE_TEST_TIMEOUT:-600}"\n'
      '\n'
      '# BL-300: Die Zielstand-Pruefung (optional).\n'
      'TEAM_ZIELSTAND_PRUEFUNG="${TEAM_ZIELSTAND_PRUEFUNG:-}"\n'
      '\n'
      'TEAM_KIT_PFAD="${TEAM_KIT_PFAD:-' + _marke("KIT_PFAD") + '}"\n'
      'TEAM_FIX_PRAEFIX="${TEAM_FIX_PRAEFIX:-fix}"\n')
PS1 = ("$TEAM_SMOKE_TEST = Team-Wert 'TEAM_SMOKE_TEST' './smoke.ps1'\n"
       "# BL-300: Die Zielstand-Pruefung (optional).\n"
       "$TEAM_ZIELSTAND_PRUEFUNG = Team-Wert 'TEAM_ZIELSTAND_PRUEFUNG' ''\n"
       "$TEAM_FIX_PRAEFIX = Team-Wert 'TEAM_FIX_PRAEFIX' 'fix'\n")


def test_ein_neuer_wert_kommt_an_seine_stelle_ein_entfernter_nicht(tmp_path, capsys):
    kit = _kit(tmp_path, FRAGMENT_ALT, sh=SH, ps1=PS1)
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    # Das Projekt hat TEAM_SMOKE_TEST_TIMEOUT bewusst geloescht (stand in der
    # Basis); TEAM_ZIELSTAND_PRUEFUNG ist neu; TEAM_KIT_PFAD traegt einen
    # Platzhalter — Maschinensache, nicht eintragbar.
    (projekt / "team.config.sh").write_text(
        'TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-pytest -q}"\n'
        'TEAM_FIX_PRAEFIX="${TEAM_FIX_PRAEFIX:-fix(uat)}"\n', encoding="utf-8")
    (projekt / "team.config.ps1").write_bytes(
        b"\xef\xbb\xbf$TEAM_SMOKE_TEST = Team-Wert 'TEAM_SMOKE_TEST' 'pytest -q'\n"
        b"$TEAM_FIX_PRAEFIX = Team-Wert 'TEAM_FIX_PRAEFIX' 'fix(uat)'\n")
    _basis(projekt, "konfig-schluessel",
           "sh TEAM_SMOKE_TEST\nsh TEAM_SMOKE_TEST_TIMEOUT\nsh TEAM_FIX_PRAEFIX\n"
           "ps1 TEAM_SMOKE_TEST\nps1 TEAM_FIX_PRAEFIX\n")
    assert kit_basis.konfig(str(projekt), str(kit)) == 0
    sh = (projekt / "team.config.sh").read_text(encoding="utf-8").split("\n")
    assert sh[0].endswith("pytest -q}\""), "der Projektwert bleibt"
    assert 'TEAM_ZIELSTAND_PRUEFUNG="${TEAM_ZIELSTAND_PRUEFUNG:-}"' in sh
    assert "# BL-300: Die Zielstand-Pruefung (optional)." in sh
    assert sh.index("# BL-300: Die Zielstand-Pruefung (optional).") > 0 and \
        sh.index('TEAM_ZIELSTAND_PRUEFUNG="${TEAM_ZIELSTAND_PRUEFUNG:-}"') < \
        sh.index('TEAM_FIX_PRAEFIX="${TEAM_FIX_PRAEFIX:-fix(uat)}"'), (
        "Der neue Wert gehoert hinter seinen Vorgaenger in der Vorlage, nicht ans Ende")
    assert not any("TEAM_SMOKE_TEST_TIMEOUT" in z for z in sh), "bewusst entfernt"
    assert not any("TEAM_KIT_PFAD" in z for z in sh), (
        "Ein Platzhalter ist Projekt- oder Maschinensache — den meldet BL-200")
    roh = (projekt / "team.config.ps1").read_bytes()
    assert roh.startswith(b"\xef\xbb\xbf"), "das BOM der .ps1 bleibt (BL-113)"
    assert b"$TEAM_ZIELSTAND_PRUEFUNG = Team-Wert 'TEAM_ZIELSTAND_PRUEFUNG' ''" in roh
    assert "Kit-BL-311" in capsys.readouterr().out


def test_ohne_basis_bleibt_die_konfiguration_unangetastet(tmp_path):
    kit = _kit(tmp_path, FRAGMENT_ALT, sh=SH)
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    vorher = 'TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-pytest -q}"\n'
    (projekt / "team.config.sh").write_text(vorher, encoding="utf-8")
    kit_basis.konfig(str(projekt), str(kit))
    assert (projekt / "team.config.sh").read_text(encoding="utf-8") == vorher


# --- CLAUDE.md --------------------------------------------------------------------

BASIS = "# CLAUDE.md\n\n## Regeln\n\nRegel A.\n\nRegel B.\n\n## Ende\n"
KIT_NEU = "# CLAUDE.md\n\n## Regeln\n\nRegel A.\n\nRegel A2, neu im Kit.\n\nRegel B.\n\n## Ende\n"


def _claude_lage(tmp_path, projekt_text, basis=BASIS, crlf=False):
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    roh = projekt_text.replace("\n", "\r\n") if crlf else projekt_text
    (projekt / "CLAUDE.md").write_bytes(roh.encode("utf-8"))
    if basis is not None:
        _basis(projekt, "CLAUDE.md", basis)
    neu = tmp_path / "abgleich" / "CLAUDE.md"
    neu.parent.mkdir()
    neu.write_text(KIT_NEU, encoding="utf-8")
    return projekt, neu


def _claude(projekt, neu, tmp_path, kit=None):
    return kit_basis.claude(str(projekt), str(kit or tmp_path / "kein-kit"), str(neu),
                            str(projekt / "backups" / "update-1"),
                            str(neu.parent), "ps1")


def test_eine_neue_kit_regel_wird_eingearbeitet_die_eigene_bleibt(tmp_path, capsys):
    eigen = BASIS.replace("Regel B.\n", "Regel B.\n\nEigene Projektregel.\n")
    projekt, neu = _claude_lage(tmp_path, eigen, crlf=True)
    assert _claude(projekt, neu, tmp_path) == 0
    roh = (projekt / "CLAUDE.md").read_bytes()
    text = roh.decode("utf-8")
    assert "Regel A2, neu im Kit." in text and "Eigene Projektregel." in text, text
    assert "\r\n" in text and "\n" not in text.replace("\r\n", ""), "CRLF bleibt"
    sicherung = projekt / "backups" / "update-1" / "CLAUDE.md"
    assert sicherung.read_bytes() == eigen.replace("\n", "\r\n").encode("utf-8"), (
        "Die alte Fassung liegt Byte fuer Byte in der Sicherung")
    basis = (projekt / "team" / ".kit-basis" / "CLAUDE.md").read_text(encoding="utf-8")
    assert basis == KIT_NEU, "die Basis rueckt auf die aufgenommene Kit-Fassung vor"
    assert "eingearbeitet" in capsys.readouterr().out


def test_ein_konflikt_laesst_die_datei_stehen_und_legt_einen_vorschlag(tmp_path, capsys):
    """Kit und Projekt aendern dieselbe Stelle: nichts uebernehmen, nicht
    raten. Die Basis bleibt stehen — das naechste Update bietet die Regel
    noch einmal an."""
    eigen = BASIS.replace("Regel A.\n\nRegel B.", "Regel A.\n\nUnsere Regel B, umformuliert.")
    projekt, neu = _claude_lage(tmp_path, eigen)
    assert _claude(projekt, neu, tmp_path) == kit_basis.OFFEN
    assert (projekt / "CLAUDE.md").read_text(encoding="utf-8") == eigen
    vorschlag = (neu.parent / "CLAUDE.md.vorschlag").read_text(encoding="utf-8")
    assert "<<<<<<< Projekt" in vorschlag and ">>>>>>> Kit-Fassung jetzt" in vorschlag
    basis = (projekt / "team" / ".kit-basis" / "CLAUDE.md").read_text(encoding="utf-8")
    assert basis == BASIS
    aus = capsys.readouterr().out
    assert "Copy-Item" in aus and "Konflikt" in aus, aus


def test_ohne_neue_kit_regel_ist_nichts_zu_tun(tmp_path, capsys):
    """Die Gegenprobe zur Meldung: Weicht die CLAUDE.md nur durch eigene
    Anpassungen ab, gibt es nichts abzugleichen — und das wird so gesagt,
    statt "bitte abgleichen" zu verlangen (BL-14)."""
    projekt, neu = _claude_lage(tmp_path, BASIS + "\nEigene Regel.\n", basis=KIT_NEU)
    assert _claude(projekt, neu, tmp_path) == 0
    assert (projekt / "CLAUDE.md").read_text(encoding="utf-8") == BASIS + "\nEigene Regel.\n"
    assert "keine neue Regel" in capsys.readouterr().out


def test_ohne_basis_und_ohne_kit_geschichte_meldet_der_installer_wie_bisher(tmp_path):
    projekt, neu = _claude_lage(tmp_path, BASIS, basis=None)
    assert _claude(projekt, neu, tmp_path) == kit_basis.OHNE_BASIS
    assert (projekt / "CLAUDE.md").read_text(encoding="utf-8") == BASIS


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@l", "-c",
                    "user.name=T", *args], check=True, capture_output=True)


def test_ohne_basis_wird_geschaetzt_und_nur_vorgeschlagen(tmp_path, capsys):
    """Das erste Update eines Projekts aus der Zeit davor: Die Basis kommt aus
    der Geschichte des Kits — die Fassung, die der Datei am naechsten liegt,
    mit den Werten des Projekts gerendert. Geschrieben wird dann nichts."""
    kit = tmp_path / "kit"
    (kit / "bootstrap").mkdir(parents=True)
    _git(kit, "init", "-q")
    vorlage = kit / "bootstrap" / "CLAUDE.md.vorlage"
    kopf = "# CLAUDE.md — " + _marke("PROJEKTNAME")
    vorlage.write_text(BASIS.replace("# CLAUDE.md", kopf), encoding="utf-8")
    _git(kit, "add", "-A")
    _git(kit, "commit", "-q", "-m", "alt")
    vorlage.write_text(KIT_NEU.replace("# CLAUDE.md", kopf), encoding="utf-8")
    _git(kit, "commit", "-q", "-am", "neu")
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    eigen = BASIS.replace("# CLAUDE.md", "# CLAUDE.md — feld") + "\nEigene Regel.\n"
    (projekt / "CLAUDE.md").write_text(eigen, encoding="utf-8")
    neu = tmp_path / "abgleich" / "CLAUDE.md"
    neu.parent.mkdir()
    neu.write_text(KIT_NEU.replace("# CLAUDE.md", "# CLAUDE.md — feld"), encoding="utf-8")
    assert _claude(projekt, neu, tmp_path, kit=kit) == kit_basis.OFFEN
    assert (projekt / "CLAUDE.md").read_text(encoding="utf-8") == eigen
    vorschlag = (neu.parent / "CLAUDE.md.vorschlag").read_text(encoding="utf-8")
    assert "Regel A2, neu im Kit." in vorschlag and "Eigene Regel." in vorschlag
    basis = (projekt / "team" / ".kit-basis" / "CLAUDE.md").read_text(encoding="utf-8")
    assert basis == eigen.replace("\nEigene Regel.\n", ""), (
        "Abgelegt wird die GESCHAETZTE Basis, damit das naechste Update weiss, "
        "wovon es ausgeht — nicht die jetzige Fassung")
    assert "vermutlich" in capsys.readouterr().out


# --- schreiben ----------------------------------------------------------------------

def test_schreiben_legt_die_drei_teile_ab(tmp_path):
    kit = _kit(tmp_path, FRAGMENT_NEU, sh=SH, ps1=PS1)
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    gerendert = tmp_path / "CLAUDE.md"
    gerendert.write_bytes(b"\xef\xbb\xbf# CLAUDE\r\n")
    assert kit_basis.basis_schreiben(str(projekt), str(kit), str(gerendert)) == 0
    basis = projekt / "team" / ".kit-basis"
    assert (basis / "gitignore.fragment").read_text(encoding="utf-8") == FRAGMENT_NEU
    assert (basis / "CLAUDE.md").read_bytes() == b"# CLAUDE\n", "ohne BOM, mit LF"
    schluessel = (basis / "konfig-schluessel").read_text(encoding="utf-8").split("\n")
    assert "sh TEAM_ZIELSTAND_PRUEFUNG" in schluessel and \
        "ps1 TEAM_ZIELSTAND_PRUEFUNG" in schluessel
    assert "{{" not in "".join(p.read_text(encoding="utf-8") for p in basis.iterdir()), (
        "Kein Platzhalter in der Basis — der Selbsttest sucht sie im ganzen "
        "Projekt (Stufe 3)")


def test_das_werkzeug_laeuft_als_programm(tmp_path):
    r = subprocess.run([sys.executable, str(TOOL), "gitignore", "--ziel",
                        str(tmp_path), "--kit", str(tmp_path)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode == 0, r.stderr
    r = subprocess.run([sys.executable, str(TOOL), "quatsch"], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 2 and "unbekanntes Verb" in r.stderr


# --- Durch den Installer, auf beiden Bahnen -----------------------------------------

INSTALL_SH = REPO_ROOT / "bash" / "install.sh"
INSTALL_PS1 = REPO_ROOT / "pwsh" / "install.ps1"
ABSCHNITT_0 = ("## 0. Für Menschen         Zehn Sätze ohne Fachkürzel: Frage, gebaut,\n"
               "##                         Überraschung, Kosten, offen (Kit-BL-243)\n")


def _installer(bahn, ziel, *extra):
    if bahn == "bash":
        from conftest import BASH, verlange_bash
        verlange_bash()
        if not INSTALL_SH.is_file():
            pytest.skip("install.sh liegt nur im Kit")
        befehl = [BASH, str(INSTALL_SH), str(ziel), "--nicht-interaktiv",
                  "--ohne-selbsttest", *extra]
    else:
        from conftest import verlange_pwsh
        verlange_pwsh()
        if not INSTALL_PS1.is_file():
            pytest.skip("install.ps1 liegt nur im Kit")
        befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(INSTALL_PS1),
                  str(ziel), "-NichtInteraktiv", "-OhneSelbsttest", *extra]
    r = subprocess.run(befehl, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout + r.stderr


def _ohne(pfad, *weg, bom=None):
    roh = pfad.read_bytes()
    hat_bom = roh.startswith(b"\xef\xbb\xbf") if bom is None else bom
    text = roh.decode("utf-8-sig")
    for w in weg:
        assert w in text, (pfad.name, w)
        text = text.replace(w, "")
    pfad.write_bytes((b"\xef\xbb\xbf" if hat_bom else b"") + text.encode("utf-8"))


@pytest.mark.parametrize("bahn", ("bash", "pwsh"))
def test_das_update_traegt_neues_nach_und_laesst_entferntes_weg(tmp_path, bahn):
    """Die Feldlage in klein: Das Projekt wurde mit einer Kit-Fassung
    installiert, der drei Dinge fehlten — eine .gitignore-Zeile, ein
    Konfigurationswert, ein Abschnitt der Abschluss-Gliederung. Nachgestellt,
    indem sie in Projekt UND Basis fehlen. Dazu hat das Projekt eine
    .gitignore-Zeile bewusst entfernt (nur im Projekt) und eine eigene Regel."""
    ziel = tmp_path / "projekt"
    ziel.mkdir()
    for args in (("init", "-q"), ("config", "user.email", "t@l"),
                 ("config", "user.name", "T")):
        subprocess.run(["git", "-C", str(ziel), *args], check=True, capture_output=True)
    rc, aus = _installer(bahn, ziel)
    assert rc == 0, aus[-2000:]
    basis = ziel / "team" / ".kit-basis"
    for name in ("CLAUDE.md", "gitignore.fragment", "konfig-schluessel"):
        assert (basis / name).is_file(), f"Die Erstinstallation legt {name} nicht ab"
    assert (basis / "CLAUDE.md").read_text(encoding="utf-8") == \
        (ziel / "CLAUDE.md").read_text(encoding="utf-8").replace("\r\n", "\n")

    # --- die aeltere Kit-Fassung nachstellen ---------------------------------
    _ohne(ziel / ".gitignore", ".team-protokolle/\n", ".team-focus-harry\n")
    _ohne(basis / "gitignore.fragment", ".team-protokolle/\n")
    for cfg, zeile in (("team.config.sh",
                        'TEAM_ZIELSTAND_PRUEFUNG="${TEAM_ZIELSTAND_PRUEFUNG:-}"\n'),
                       ("team.config.ps1",
                        "$TEAM_ZIELSTAND_PRUEFUNG = Team-Wert 'TEAM_ZIELSTAND_PRUEFUNG' ''\n")):
        if (ziel / cfg).is_file():
            _ohne(ziel / cfg, zeile)
    _ohne(basis / "konfig-schluessel", "sh TEAM_ZIELSTAND_PRUEFUNG\n",
          "ps1 TEAM_ZIELSTAND_PRUEFUNG\n")
    _ohne(ziel / "CLAUDE.md", ABSCHNITT_0)
    _ohne(basis / "CLAUDE.md", ABSCHNITT_0)
    with open(ziel / "CLAUDE.md", "a", encoding="utf-8") as fh:
        fh.write("\nEigene Projektregel dieses Projekts.\n")
    subprocess.run(["git", "-C", str(ziel), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(ziel), "commit", "-qm", "projektstand"],
                   check=True, capture_output=True)

    rc, aus = _installer(bahn, ziel, "--update" if bahn == "bash" else "-Update")
    assert rc == 0, aus[-3000:]
    gitignore = (ziel / ".gitignore").read_text(encoding="utf-8").split("\n")
    assert ".team-protokolle/" in gitignore, f"neue Zeile nicht eingetragen:\n{aus[-3000:]}"
    assert ".team-focus-harry" not in gitignore, (
        "Die bewusst entfernte Zeile ist zurueckgekommen — die stand schon in "
        "der Basis (BL-109)")
    for cfg in ("team.config.sh", "team.config.ps1"):
        if (ziel / cfg).is_file():
            assert "TEAM_ZIELSTAND_PRUEFUNG" in (ziel / cfg).read_text(encoding="utf-8-sig"), (
                f"{cfg}: der neue Wert fehlt\n{aus[-3000:]}")
    claude = (ziel / "CLAUDE.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert ABSCHNITT_0 in claude, f"die neue Kit-Regel fehlt\n{aus[-3000:]}"
    assert "Eigene Projektregel dieses Projekts." in claude, "die eigene Regel ist weg"
    gesichert = list((ziel / "backups").glob("update-*/CLAUDE.md"))
    assert gesichert and "Eigene Projektregel" in gesichert[0].read_text(encoding="utf-8"), (
        "Die alte CLAUDE.md muss vor dem Einarbeiten gesichert sein")
    assert "Kit-BL-311" in aus and "eingearbeitet" in aus, aus[-3000:]
    assert (basis / "CLAUDE.md").read_text(encoding="utf-8").count("## 0. Für Menschen") == 1, (
        "Die Basis rueckt auf die aufgenommene Kit-Fassung vor")

    # --- Gegenprobe: ein zweites Update hat nichts nachzutragen (BL-14) -------
    subprocess.run(["git", "-C", str(ziel), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(ziel), "commit", "-qm", "nach dem update"],
                   check=True, capture_output=True)
    rc, aus2 = _installer(bahn, ziel, "--update" if bahn == "bash" else "-Update")
    assert rc == 0, aus2[-2000:]
    assert "eingetragen" not in aus2 and "eingearbeitet" not in aus2, aus2[-3000:]
    assert "keine neue Regel" in aus2, aus2[-3000:]
    assert (ziel / "CLAUDE.md").read_text(encoding="utf-8").replace("\r\n", "\n") == claude

#!/usr/bin/env python3
"""Reproduktions-/Regressionstest fuer BL-147: Ein `--update` ohne Schalter
legte die zweite Bahn dazu — auch in ein Projekt, das nie eine wollte.

Gedacht war es als Rueckweg aus einer Abwahl (`BL-119`: "ein Update macht
das Projekt wieder vollstaendig"). Im Feld ist das Routine-Update aber der
Normalfall, und der Normalfall will keine zweite Bahn.

    Feld A, 2026-08-22: Ein Routine-Update legte 21 pwsh-Dateien in ein
    reines Bash-Projekt (19 Entrypoints, `team/lib.psm1`, `team/redteam.ps1`).
    Untracked, unbestellt. Weil sie im Baum lagen, fuhr die Testsuite ab da
    eine Bahn mit, die dort niemand faehrt — `conftest.bahnen_in_der_ablage`
    entscheidet an der ANWESENHEIT der Dateien.

Der Fix dreht die Vorbelegung um: Die ABLAGE sagt, welche Bahn ein Projekt
faehrt, nicht der Schalter, den beim Update gerade niemand tippt. Der
Rueckweg bleibt, er wird nur ausdruecklich (`--beide-bahnen`) — derselbe
Schnitt wie bei der Abwahl selbst: Er kommt vom Anwender, nie vom Installer.

WORAN ERKANNT WIRD, IST DER KERN
    An den Dateien, die das KIT ausliefert — nicht an der Endung. Ein
    projekteigenes `deploy.ps1` ist keine pwsh-Bahn, und ein `build.sh` macht
    aus einem Windows-Projekt kein zweibahniges. Eine Endungs-Heuristik haette
    im Feld an genau dieser Stelle vorbeigelesen und die Bahn wieder
    dazugelegt, die der Fix fernhalten soll.

DIE ARBEITSTEILUNG DIESER DATEI
    Den LAUF fuehrt `kit-test.sh` Stufe 8 (installieren, aktualisieren,
    nachsehen) — dort gehoert er hin, weil er echte Installationen braucht.
    Hier steht die Zusicherung am QUELLTEXT, fuer BEIDE Bahnen: Auf einer
    Maschine ohne PowerShell kann der Lauf die pwsh-Fassung nicht pruefen
    (`BL-117`-Lage), ein statischer Vergleich laeuft ueberall.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _installer(name):
    """Der Installer beider Bahnen liegt im KIT, nicht im Projekt — ein
    installiertes Projekt traegt ihn gar nicht. Fehlt er, wird
    uebersprungen statt falsch gruen gemeldet."""
    for kandidat in (REPO_ROOT / "bash" / "install.sh", REPO_ROOT / "pwsh" / "install.ps1"):
        if kandidat.name == name and kandidat.is_file():
            return kandidat.read_text(encoding="utf-8-sig")
    pytest.skip(f"{name} liegt hier nicht (installiertes Projekt statt Kit-Ablage)")


def test_bash_update_erkennt_die_einbahnige_ablage():
    quelle = _installer("install.sh")
    assert "bahn_liegt_da bash && ! bahn_liegt_da pwsh" in quelle, (
        "Der --update-Pfad muss die Bahn der Ablage ERKENNEN. Ohne die "
        "Erkennung ist die Vorbelegung wieder 'beide' — und ein "
        "Routine-Update legt der Ablage die Bahn dazu, die sie nie hatte "
        "(BL-147).")
    assert "bahn_liegt_da pwsh && ! bahn_liegt_da bash" in quelle, (
        "Die Erkennung muss in BEIDE Richtungen greifen. Sonst bekommt ein "
        "Windows-Projekt beim Update .sh-Dateien dazu — derselbe Fehler, nur "
        "spiegelbildlich (BL-147).")


def test_pwsh_update_erkennt_die_einbahnige_ablage():
    """Dieselbe Zusicherung auf der anderen Bahn. Sie wiegt dort schwerer:
    Ein Windows-Projekt OHNE bash ist der Normalfall, fuer den die pwsh-Bahn
    ueberhaupt gebaut ist."""
    quelle = _installer("install.ps1")
    assert re.search(r"\$hatBash\s*=\s*Test-BahnLiegtDa 'bash'", quelle), (
        "Der -Update-Pfad muss die Bahn der Ablage ERKENNEN (BL-147).")
    assert re.search(r"\$hatPwsh\s*=\s*Test-BahnLiegtDa 'pwsh'", quelle), (
        "Die Erkennung muss in BEIDE Richtungen greifen (BL-147).")


def test_die_erkennung_entscheidet_nicht_an_der_endung():
    """Der Kern des Fundes. Eine Endungs-Heuristik ist verlockend und falsch:
    Sie haelt ein projekteigenes deploy.ps1 fuer eine pwsh-Bahn und legt dem
    Projekt daraufhin die 19 Kit-Dateien dazu, die BL-147 fernhalten soll."""
    bash_quelle = _installer("install.sh")
    koerper = bash_quelle.split("bahn_liegt_da() {", 1)[1].split("\n}", 1)[0]
    assert "bash/entry" in koerper and "pwsh/entry" in koerper, (
        "bahn_liegt_da() muss nach den Dateien fragen, die das KIT "
        "ausliefert (bash/entry, pwsh/entry) — nicht nach einer Endung "
        "(BL-147).")

    pwsh_quelle = _installer("install.ps1")
    p_koerper = pwsh_quelle.split("function Get-KitBahnDateien", 1)[1].split("\n}", 1)[0]
    assert "entry" in p_koerper, (
        "Get-KitBahnDateien muss nach den Kit-Dateien fragen, nicht nach "
        "einer Endung (BL-147).")


def test_der_rueckweg_bleibt_und_ist_ausdruecklich():
    """BL-119 bleibt gueltig: Die Abwahl darf keine Einbahnstrasse sein. Sie
    ist jetzt nur nicht mehr die Vorbelegung — ohne diesen Schalter waere aus
    dem einen Fehler der andere geworden."""
    bash_quelle = _installer("install.sh")
    assert "--beide-bahnen)     BEIDE_BAHNEN=1 ;;" in bash_quelle, (
        "Ohne --beide-bahnen ist die Abwahl einer Bahn endgueltig — genau die "
        "Einbahnstrasse, gegen die BL-119 gebaut wurde (BL-147).")
    assert '[ "$BEIDE_BAHNEN" -eq 1 ] && [ -n "$NUR_BAHN" ]' in bash_quelle, (
        "--beide-bahnen und --nur-* widersprechen einander und muessen sich "
        "ausschliessen, statt still die eine Absicht zu gewinnen.")

    pwsh_quelle = _installer("install.ps1")
    assert "[switch]$BeideBahnen" in pwsh_quelle, (
        "Der Rueckweg fehlt auf der pwsh-Bahn (BL-147/BL-119).")
    assert "if ($BeideBahnen -and $NurBahn)" in pwsh_quelle, (
        "-BeideBahnen und -Nur* muessen sich ausschliessen (BL-147).")


def test_die_reste_meldung_zeigt_nur_auf_kit_dateien():
    """Die Meldung 'Abgewaehlte Bahn liegt noch da' endet mit einem
    `git rm`-Vorschlag. Zaehlte sie nach Endung, stuende dort irgendwann die
    Datei eines Projekts — ein Rat des Installers, fremde Arbeit zu loeschen
    (Lehre BL-12, nur andersherum)."""
    bash_quelle = _installer("install.sh")
    block = bash_quelle.split('RESTE=""', 1)[1].split("if [ -n \"$RESTE\" ]", 1)[0]
    assert "$KIT" in block and '"$ZIEL"/*' not in block, (
        "Die Reste-Meldung muss ueber die Kit-Dateien laufen, nicht ueber "
        "den Inhalt des Zielordners (BL-147).")

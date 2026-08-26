#!/usr/bin/env python3
"""BL-178: Den Block „Bitte von Hand abgleichen" hatte NUR `install.sh`.

WAS DER BLOCK TUT UND WARUM ER NICHT KOSMETIK IST
    Doku-Dateien tragen Projektanpassungen (gefuellte TODOs, eigene
    Abschnitte) und werden vom Update deshalb NICHT ueberschrieben. Der Mensch
    muss aber erfahren, dass sich die Kit-Fassung geaendert hat — sonst laufen
    die REGELN im Projekt der Mechanik hinterher. Das ist genau die Haelfte
    des `BL-4`-Fehlers.

    Verglichen wird die MIT DENSELBEN WERTEN gerenderte Kit-Vorlage gegen die
    installierte Datei; die gerenderte Fassung bleibt liegen, und der Hinweis
    nennt einen Befehl zum Nachsehen.

WAS FEHLTE
    In `install.ps1` gab es davon NICHTS. `grep -c 'Bitte von Hand
    abgleichen'` lieferte `install.sh` 1 und `install.ps1` 0; die drei
    aehnlich klingenden Bloecke dort (Gitignore-, Gitattributes-,
    Python-Abgleich) sind andere Pruefungen. Auf einer reinen pwsh-Ablage —
    unter Windows der Normalfall — bekam die Meldung also niemand je zu
    sehen.

    Es ist dieselbe Gattung wie `BL-145` („gruen bedeutet auf den beiden
    Bahnen verschieden viel"), nur bei den REGELN statt bei den Tests. Der
    Feldbeleg lag schon vor: `Feld B` ist pwsh-only, ist mehrfach
    aktualisiert worden und hat diese Meldung nie bekommen — ein Teil der
    Antwort darauf, warum die kaputte `CLAUDE.md` dort so lange unbemerkt
    blieb (`BL-177`).

WAS DIESER TEST PRUEFT
    (1) GLEICHSTAND — beide Installer haben den Block, vergleichen dieselben
        zwei Paare und sagen beide, dass eine Abweichung bei `CLAUDE.md`
        NORMAL ist. Ohne diesen Satz ist der Block eine Warnung, die man
        wegklickt (`BL-14`).
    (2) DIE VIER AUFLAGEN der Portierung, je einzeln: in den TEMP-Bereich
        rendern (nicht ins Projekt — eine uncommittete Datei ausserhalb der
        Whitelist sieht fuer den Read-Only-Guard aus wie ein Regelbruch), die
        Zeilenenden ausnehmen, einen auf DIESER Bahn ausfuehrbaren Befehl
        nennen (ein `diff`-Aufruf, den Windows nicht kennt, ist die Bauart
        `BL-44`), und die Abweichung einordnen.
    (3) VERHALTEN — `Abgleich-Unterschiede` wird ueber den Syntaxbaum aus der
        ECHTEN Datei geholt und in echtem PowerShell gefahren: CRLF gegen LF
        ist KEIN Unterschied, eine geaenderte Zeile schon. Ein Test gegen
        einen nachgebauten Zwilling bewiese etwas ueber den Zwilling
        (`BL-142`).

    Der Lauf des Installers selbst gehoert nicht hierher, sondern in
    `kit-test.ps1` Schritt 5 — dort liegt ohnehin eine Installation, gegen
    die ein `-Update` faehrt.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import verlange_pwsh  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO_ROOT / "bash" / "install.sh"
INSTALL_PS1 = REPO_ROOT / "pwsh" / "install.ps1"

UEBERSCHRIFT = "Bitte von Hand abgleichen"


def _lies(pfad):
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt in dieser Ablage nicht")
    return pfad.read_text(encoding="utf-8-sig")


def _pwsh_block():
    """Der Abgleich-Block aus install.ps1 — von der Ueberschrift bis zum
    naechsten Kopf. Nur dieser Ausschnitt wird befragt; ein Riegel ueber die
    ganze Datei traefe die drei anderen `*-Abgleich`-Bloecke mit."""
    text = _lies(INSTALL_PS1)
    start = text.index(UEBERSCHRIFT)
    rest = text[start:]
    ende = rest.find('Kopf "Selbsttest"')
    return rest[:ende if ende > 0 else len(rest)]


# --- (1) Gleichstand der Bahnen ---------------------------------------------


@pytest.mark.parametrize("datei", [INSTALL_SH, INSTALL_PS1])
def test_beide_installer_haben_den_block(datei):
    """Der Fund selbst, in einer Zeile.

    Gemessen war er als `grep -c`: install.sh 1, install.ps1 0.
    """
    assert UEBERSCHRIFT in _lies(datei), (
        f"BL-178: {datei.name} hat den Block [{UEBERSCHRIFT}] nicht. Auf "
        "dieser Bahn erfaehrt ein Projekt dann nie, dass ihm Regeln aus einer "
        "neueren Kit-Fassung fehlen — die Mechanik ist aktualisiert, die "
        "Regeln sind es nicht (die Haelfte von BL-4).")


@pytest.mark.parametrize("datei", [INSTALL_SH, INSTALL_PS1])
@pytest.mark.parametrize("vorlage", ["bootstrap/TEAM.md",
                                     "bootstrap/CLAUDE.md.vorlage"])
def test_beide_vergleichen_dieselben_zwei_paare(datei, vorlage):
    """Ein Paar, das nur eine Bahn vergleicht, ist auf der anderen blind."""
    text = _lies(datei)
    # install.ps1 schreibt den Pfad mit Schraegstrich wie install.sh; ein
    # Rueckstrich waere hier kein Fehler, deshalb wird beides akzeptiert.
    varianten = (vorlage, vorlage.replace("/", "\\"))
    assert any(v in text for v in varianten), (
        f"{datei.name} vergleicht {vorlage} nicht — dann bleibt genau diese "
        "Datei beim Update unbemerkt veraltet.")


@pytest.mark.parametrize("datei", [INSTALL_SH, INSTALL_PS1])
def test_beide_ordnen_die_abweichung_ein(datei):
    """Ohne diesen Satz ist der Block eine Warnung, die man wegklickt.

    Bei `CLAUDE.md` ist eine Abweichung der NORMALFALL — sie traegt
    Projektarbeit. Wer das nicht danebenliest, haelt den Befund fuer Rauschen
    und sieht beim naechsten Mal nicht mehr hin (`BL-14`).
    """
    text = _lies(datei)
    assert re.search(r"CLAUDE\.md ist eine Abweichung normal", text), (
        f"{datei.name} sagt nicht, dass eine Abweichung bei CLAUDE.md normal "
        "ist.")
    assert "BL-4" in text, (
        f"{datei.name} nennt nicht, worauf es statt dessen ankommt — dass "
        "REGELN aus der neuen Kit-Fassung fehlen koennten.")


# --- (2) Die vier Auflagen der Portierung ------------------------------------


def test_die_gerenderte_vorlage_landet_im_temp_bereich():
    """Auflage 1: NICHT ins Projekt rendern.

    Eine uncommittete Datei ausserhalb der Whitelist sieht fuer den
    Read-Only-Guard aus wie ein Regelbruch — der Installer wuerde dem Projekt
    also einen Befund hinterlassen, den er selbst erzeugt hat.
    """
    block = _pwsh_block()
    assert "GetTempPath" in block, (
        "Der Abgleich rendert nicht in den TEMP-Bereich. Wohin sonst er "
        "rendert, ist fast egal — ins PROJEKT darf es nicht sein.")
    assert not re.search(r"Join-Path\s+\$Ziel\s+\$gerendert", block), (
        "Die gerenderte Vorlage wird ins Zielprojekt geschrieben.")


def test_der_genannte_befehl_ist_auf_dieser_bahn_ausfuehrbar():
    """Auflage 3: kein `diff`.

    Ein Befehl, den Windows nicht kennt, ist die Bauart `BL-44` —
    angekuendigt, aber nicht am wirksamen Ort ausfuehrbar. Es ist derselbe
    Fehler, den die bash-Fassung schon einmal gemacht hat (`diff <(…)` als
    Platzhalter fuer „die mit deinen Werten gerenderte Vorlage").
    """
    # Ohne Kommentarzeilen: Der Block BEGRUENDET, warum hier kein `diff`
    # steht, und nennt das Wort dabei. Ein Riegel, der die Begruendung fuer
    # den Verstoss haelt, zwaenge dazu, die Begruendung zu loeschen.
    block = "\n".join(z for z in _pwsh_block().splitlines()
                      if not z.lstrip().startswith("#"))
    assert not re.search(r"\bdiff\b", block), (
        "Der pwsh-Abgleich nennt `diff` — das gibt es auf einer nackten "
        "Windows-Maschine nicht. Der genannte Befehl muss dort laufen, wo er "
        "genannt wird (BL-44).")
    assert "Compare-Object" in block, (
        "Der Block nennt keinen Vergleichsbefehl, den der Anwender kopieren "
        "kann — dann verlangt der Hinweis genau die Arbeit, die er abnehmen "
        "wollte.")


def test_der_vergleich_liegt_in_einer_eigenen_funktion():
    """Damit Auflage 2 (Zeilenenden) UEBERPRUEFBAR ist und nicht nur behauptet.

    Inline im Update-Pfad waere sie nur zu belegen, indem man den ganzen
    Installer faehrt — und ein Nachweis, der Minuten kostet, wird nicht
    gefahren.
    """
    text = _lies(INSTALL_PS1)
    assert "function Abgleich-Unterschiede" in text, (
        "Abgleich-Unterschiede fehlt — dann haengt die Zusicherung ueber die "
        "Zeilenenden wieder an einem Kommentar.")
    assert "Abgleich-Unterschiede $gerendert $installiert" in text, (
        "Der Block benutzt die Funktion nicht. So liesse sich der Test oben "
        "gruen halten, waehrend der Installer etwas anderes tut.")


# --- (3) Verhalten: die ECHTE Funktion, in echtem PowerShell ------------------


def _sonde(tmp_path, links, rechts):
    # In der INSTALLIERTEN Ablage gibt es install.ps1 nicht — die Installer
    # bleiben im Kit. Ohne diesen Uebersprung waere der Fall dort ROT statt
    # uebersprungen, und genau diese Bauart hat im Selbsttest schon zweimal je
    # einen Zwanzig-Minuten-Rundlauf gekostet (Vorflug-Pruefung im Backlog).
    _lies(INSTALL_PS1)
    skript = f"""
$ErrorActionPreference = 'Stop'
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           '{INSTALL_PS1.as_posix()}', [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq 'Abgleich-Unterschiede' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw 'Abgleich-Unterschiede nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text
$u = Abgleich-Unterschiede '{links.as_posix()}' '{rechts.as_posix()}'
Write-Output ("UNTERSCHIEDE=" + $u.Count)
"""
    p = tmp_path / "sonde.ps1"
    p.write_text(skript, encoding="utf-8-sig", newline="\n")
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"
    m = re.search(r"UNTERSCHIEDE=(\d+)", r.stdout)
    assert m, f"Sonde gab keine Zahl aus:\n{r.stdout}{r.stderr}"
    return int(m.group(1))


REGELTEXT = ("# CLAUDE.md\n"
             "\n"
             "Die Rollen schreiben nur in ihre Schreibzone.\n"
             "Der Smoke-Test steht in team.config.ps1.\n")


def test_crlf_gegen_lf_ist_kein_unterschied(tmp_path):
    """Auflage 2, an ihrer Wirkung gemessen.

    Eine VOR `BL-137` unter Windows installierte Datei traegt CRLF, die frisch
    gerenderte LF. Ohne Ausnahme meldete der Abgleich dann JEDE Zeile als
    abgewichen und stellte den Anwender vor eine Inhaltsaenderung, die keine
    ist — ein stiller Fehler, gegen einen lauten Fehlalarm getauscht.
    """
    verlange_pwsh()
    lf = tmp_path / "gerendert.md"
    crlf = tmp_path / "installiert.md"
    lf.write_bytes(REGELTEXT.encode("utf-8"))
    crlf.write_bytes(REGELTEXT.replace("\n", "\r\n").encode("utf-8"))
    assert _sonde(tmp_path, lf, crlf) == 0, (
        "BL-178/BL-137: Derselbe Text mit anderen Zeilenenden gilt als "
        "abgewichen. Dann meldet der Abgleich bei jeder vor BL-137 "
        "installierten Datei ALLE Zeilen, und der echte Befund geht darin "
        "unter.")


def test_eine_geaenderte_regel_faellt_sehr_wohl_auf(tmp_path):
    """Die Gegenrichtung — ohne sie waere der Fall oben auch gruen, wenn der
    Vergleich ueberhaupt nichts mehr faende (Bauart BL-14)."""
    verlange_pwsh()
    alt = tmp_path / "gerendert.md"
    neu = tmp_path / "installiert.md"
    alt.write_bytes(REGELTEXT.encode("utf-8"))
    neu.write_bytes(
        (REGELTEXT + "Neue Regel aus einer neueren Kit-Fassung.\n")
        .replace("\n", "\r\n").encode("utf-8"))
    assert _sonde(tmp_path, alt, neu) == 1, (
        "Eine hinzugekommene Regel wird nicht als Abweichung gemeldet — "
        "genau dafuer gibt es den Block.")

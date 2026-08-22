#!/usr/bin/env python3
"""BL-142: `--rollen-abschluss` mit BEIDEN Notizen brach immer ab — also genau
bei dem Aufruf, den die Doku vorgibt.

WAS IM FELD PASSIERT IST
    `Feld B`, Closeout der ersten Kaskade, erster echter
    Kostenabschluss eines Projekts:

        Method invocation failed because [System.Char] does not contain a
        method named 'StartsWith'.
        Unbekannter Modus 'K'

    Das 'K' ist das erste Zeichen der ZWEITEN Notiz. Wer der Doku folgt, kann
    seine Kaskade nicht abschliessen und weicht auf einen Direktaufruf von
    kosten.py aus.

DIE URSACHE IST EINE SPRACHREGEL, KEIN TIPPFEHLER
    In `Status-RollenAbschluss` stand zweimal (und in `Status-AkteurAbschluss`
    ein drittes Mal):

        $rest = if ($rest.Count -gt 1) { @($rest[1..($rest.Count - 1)]) }
                else { @() }

    Der `@(...)`-Ausdruck erzeugt ein Array — aber die Rueckgabe aus einem
    if-BLOCK laeuft durch die Ausgabepipeline, und die entpackt ein
    EINELEMENTIGES Array zu seinem Element. Bei genau zwei Notizen wurde
    `$rest` damit zum String.

    Der Fehlermodus ist keiner, den man beim Lesen sieht: Ein String HAT eine
    Count-Property mit Wert 1, die Bedingung `$rest.Count` traegt also weiter.
    Erst `$rest[0]` liefert dann einen [Char] statt einer Zeichenkette.

WARUM ES NIEMAND VORHER TRAF
    Die drei Faelle laufen auseinander, und nur einer ist kaputt:

        zwei Notizen, kein Schalter   -> String  (KAPUTT)
        eine Notiz                    -> $null, laeuft aber durch
        zwei Notizen + --addieren     -> Object[], funktioniert

    Die vorhandenen Faelle benutzten entweder eine Notiz oder haengten einen
    Schalter an. Genau der dokumentierte Aufruf war der ungetestete.

WAS DIESER TEST PRUEFT
    Drei Ebenen, und die dritte ist die, die den Fix ueberhaupt gueltig macht:

      (1) QUELLTEXT — das Idiom `$x = if (...) { @(...) }` steht nicht mehr in
          team-status.ps1. Laeuft auf JEDEM Wirt, auch ohne pwsh, und ist der
          Riegel gegen die Rueckkehr beim naechsten Umbau.
      (2) VERHALTEN der Hilfsfunktion — `Rest-Ohne-Erstes` wird aus der ECHTEN
          Datei ueber den Syntaxbaum geholt und in echtem PowerShell gefahren.
          Kein nachgebauter Zwilling: Ein Test gegen eine Kopie beweist etwas
          ueber die Kopie.
      (3) GEGENBEWEIS — dieselbe Sonde mit dem ALTEN Idiom muss einen String
          liefern. Ohne ihn bliebe offen, ob (2) etwas absichert oder nur
          beschreibt, was in PowerShell ohnehin gilt (Bauart BL-14).

    Dazu der Aufruf selbst, end-to-end gegen ein Fixture-Projekt: genau die
    Form aus der Doku, zwei Notizen, kein Modus-Schalter.

WARUM DER QUELLTEXT-RIEGEL NUR team-status.ps1 LIEST
    Das Kit hat fuenf weitere `$x = if (...) { @(...) }` (kit-einrichten.ps1,
    team-test.ps1, install.ps1, pruefe-windows.ps1). Alle liefern in BEIDEN
    Zweigen ein dreielementiges Literal — ein Array mit drei Elementen wird von
    der Pipeline nicht entpackt, und benutzt werden sie ohnehin nur in
    `foreach`. Sie sind gepruefte Ausnahmen, keine uebersehenen Faelle.

    Statisch unterscheiden liesse sich das nicht: Ob ein Ausdruck EINELEMENTIG
    werden kann, weiss man erst zur Laufzeit. Ein Riegel ueber alle .ps1 waere
    darum vier Fehlalarme lang, und ein Riegel mit Fehlalarmen wird
    stillgelegt. Er sitzt deshalb dort, wo Argumente ZERLEGT werden — die eine
    Stelle im Kit, an der Listen laufend kuerzer werden und die Einelementigkeit
    der Normalfall ist.

DIESE DATEI BRAUCHT pwsh
    Der Fehler kann auf der bash-Bahn nicht existieren — er ist eine Regel der
    PowerShell-Ausgabepipeline. Ohne pwsh wird UEBERSPRUNGEN, mit Grund und
    sichtbar in der Doppelbahn-Quote; nur (1) laeuft ueberall.
"""
import re
import shutil
import subprocess
from pathlib import Path

from conftest import (entrypoint_pfad, kit_pfad, ueberspringe_ohne_bahn,
                      verlange_pwsh, werkzeug_wert)

REPO_ROOT = Path(__file__).resolve().parents[2]

STATUS_PS1 = entrypoint_pfad("team-status.ps1")

# `$name = if (` als Zuweisung. Der Regex FINDET nur den Anfang — ob der
# Ausdruck ein Array liefert, entscheidet _spanne() weiter unten.
#
# Das `(?:^|;)` ist nicht Kosmetik, sondern von der Gegenprobe erzwungen: Zwei
# der drei Originalstellen standen als ZWEITE Anweisung hinter einem Semikolon
#
#     $notiz = $rest[0]; $rest = if ($rest.Count -gt 1) { … } else { @() }
#
# und ein Riegel, der nur den Zeilenanfang kennt, haette genau eine von drei
# gefunden. Aufgefallen beim Zurueckdrehen einer einzelnen Stelle — nicht beim
# Lesen.
IF_ZUWEISUNG = re.compile(r"(?:^|;)[ \t]*\$\w+\s*=\s*if\s*\(", re.MULTILINE)

# Wortgrenze noetig: `$elseWert` faengt auch mit "else" an.
FORTSETZUNG = re.compile(r"\s*(else\s*if|elseif|else)\b")


def _quelltext():
    return STATUS_PS1.read_text(encoding="utf-8-sig")


def _spanne(text, start):
    """Der Text des if-AUSDRUCKS ab `start`, inklusive aller else-Zweige.

    Warum klammergenau und nicht "die naechsten drei Zeilen": Der erste
    Entwurf nahm ein Zeilenfenster und schlug bei

        $modus = if ($rest.Count) { $rest[0] } else { '' }
        if ($modus -and $modus -notin @('--addieren', '--ersetzen')) {

    an — das `@(` gehoert der FOLGEZEILE. Eine Zusicherung, die an der
    richtigen Stelle rot wird und an zwei falschen mit, ist keine.
    """
    i, tiefe, gesehen = start, 0, False
    while i < len(text):
        c = text[i]
        if c == "{":
            tiefe += 1
            gesehen = True
        elif c == "}":
            tiefe -= 1
            if tiefe == 0 and gesehen:
                m = FORTSETZUNG.match(text, i + 1)
                if not m:
                    return text[start:i + 1]
                i = m.end() - 1          # weiter im else-Zweig
        i += 1
    return text[start:]


def test_kein_array_aus_einem_if_block_mehr():
    """(1) Quelltext — laeuft auf jedem WIRT, auch ohne pwsh installiert.

    Braucht aber die pwsh-Bahn in der ABLAGE: In einem mit --nur-bash
    installierten Projekt gibt es team-status.ps1 nicht, und ein Test, der eine
    fehlende Bahn liest, ist genau der Fall aus BL-129. Der erste Entwurf hatte
    diesen Uebersprung nicht und legte den Selbsttest in Stufe 8 lahm — dort,
    wo eine einbahnige Ablage gebaut und ihre Testsuite gefahren wird.
    """
    ueberspringe_ohne_bahn("pwsh")
    assert STATUS_PS1.is_file(), f"team-status.ps1 nicht gefunden ({STATUS_PS1})"
    text = _quelltext()
    treffer = []
    for m in IF_ZUWEISUNG.finditer(text):
        if "@(" not in _spanne(text, m.start()):
            continue          # liefert einen Skalar — voellig in Ordnung
        treffer.append(f"{STATUS_PS1.name}:{text.count(chr(10), 0, m.start()) + 1}")
    assert not treffer, (
        "BL-142: Ein Array aus einem if-BLOCK zuzuweisen entpackt den "
        "einelementigen Fall zum Element. Betroffen:\n  "
        + "\n  ".join(treffer)
        + "\nStattdessen eine Funktion mit `return ,$array` benutzen "
          "(Rest-Ohne-Erstes) oder das if als ANWEISUNG schreiben.")


def test_die_drei_stellen_benutzen_den_helfer():
    """Die Gegenrichtung zu (1): Der Helfer muss auch wirklich gerufen werden.

    Ohne diese Zusicherung liesse sich (1) dadurch gruen machen, dass jemand
    die Zeilen loescht statt sie zu reparieren.
    """
    ueberspringe_ohne_bahn("pwsh")
    text = _quelltext()
    assert "function Rest-Ohne-Erstes" in text, "die Hilfsfunktion fehlt"
    # Untergrenze, keine feste Zahl: BL-142 nannte DREI Stellen (zwei in
    # Status-RollenAbschluss fuer Notiz und Bau-Notiz, eine in
    # Status-AkteurAbschluss), BL-143 hat als vierte Status-ArchitektAbschluss
    # dazugebracht. Eine exakte Zahl waere hier eine Zusicherung ueber die
    # GROESSE der Datei und muesste bei jedem neuen Wrapper nachgezogen werden —
    # sie wuerde rot, wo nichts kaputt ist. Was zaehlt, ist die Untergrenze
    # zusammen mit dem Riegel oben: Der verbietet das alte Idiom ueberall,
    # diese Zeile verhindert, dass man ihn durch LOESCHEN gruen macht.
    stellen = text.count("Rest-Ohne-Erstes $rest")
    assert stellen >= 3, (
        "BL-142 nannte DREI Stellen: zwei in Status-RollenAbschluss (Notiz "
        f"und Bau-Notiz), eine in Status-AkteurAbschluss. Gefunden: {stellen}")
    assert re.search(r"return\s*,", text), (
        "Rest-Ohne-Erstes muss mit dem UNAEREN KOMMA zurueckgeben — sonst "
        "entpackt die Pipeline die Rueckgabe der FUNKTION, und der Fehler "
        "ist nur umgezogen.")


def _pwsh(skript):
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", skript],
        capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_rest_ohne_erstes_liefert_immer_ein_array():
    """(2) Verhalten der ECHTEN Funktion, aus der echten Datei geholt."""
    verlange_pwsh()
    # Ueber den Syntaxbaum statt per Textsuche: Ein Regex, der die Funktion aus
    # der Datei schneidet, bricht am naechsten Kommentar mit geschweifter
    # Klammer — und zwar so, dass es wie ein Kit-Defekt aussieht.
    sonde = f"""
$ErrorActionPreference = 'Stop'
$pfad = '{STATUS_PS1.as_posix()}'
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           $pfad, [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq 'Rest-Ohne-Erstes' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw 'Rest-Ohne-Erstes nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text

# Der Fall aus dem Feld: zwei Notizen, nach dem ersten Abschneiden bleibt EINE.
$zwei = Rest-Ohne-Erstes @('Rollen-Notiz', 'Kaskade 1 gebaut')
Write-Output ("zwei:  typ=" + $zwei.GetType().Name + " count=" + $zwei.Count +
              " erstes=" + $zwei[0].GetType().Name)
$eins = Rest-Ohne-Erstes @('nur eine')
Write-Output ("eins:  typ=" + $eins.GetType().Name + " count=" + $eins.Count)
$drei = Rest-Ohne-Erstes @('a', 'b', 'c')
Write-Output ("drei:  typ=" + $drei.GetType().Name + " count=" + $drei.Count)
$leer = Rest-Ohne-Erstes @()
Write-Output ("leer:  typ=" + $leer.GetType().Name + " count=" + $leer.Count)
"""
    r = _pwsh(sonde)
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"
    aus = r.stdout
    # Der Kern: einelementig bleibt ARRAY, und sein Element bleibt STRING.
    assert "zwei:  typ=Object[] count=1 erstes=String" in aus, (
        "BL-142: der einelementige Rest ist wieder zum String entpackt — "
        f"dann liefert $rest[0] einen [Char]. Ausgabe:\n{aus}")
    assert "eins:  typ=Object[] count=0" in aus, aus
    assert "drei:  typ=Object[] count=2" in aus, aus
    assert "leer:  typ=Object[] count=0" in aus, aus


def test_gegenbeweis_das_alte_idiom_entpackt_wirklich():
    """(3) Ohne diesen Fall wuesste niemand, ob (2) ueberhaupt etwas absichert."""
    verlange_pwsh()
    sonde = """
$rest = @('Rollen-Notiz', 'Kaskade 1 gebaut')
$rest = $rest[1..($rest.Count - 1)]      # nach dem ersten Abschneiden
# Genau die Zeile, die BL-142 ausgeloest hat:
$alt = if ($rest.Count -gt 1) { @($rest[1..($rest.Count - 1)]) } else { @($rest) }
Write-Output ("alt: typ=" + $alt.GetType().Name)
"""
    r = _pwsh(sonde)
    assert r.returncode == 0, r.stderr
    assert "alt: typ=String" in r.stdout, (
        "Der Gegenbeweis greift nicht mehr: Das alte Idiom liefert hier kein "
        "String. Entweder hat sich PowerShell geaendert oder die Sonde trifft "
        f"den Fall nicht. Ausgabe:\n{r.stdout}")


# --- Der Aufruf aus der Doku, end-to-end -------------------------------------

def _fixture_repo(tmp_path):
    """Dieselbe Bauart wie test_stufe51_akteur_cli.py, nur fuer die pwsh-Bahn:
    die drei Dateien, die der Entrypoint braucht, plus ein leeres Ledger.
    team-status.ps1 macht `Set-Location $PSScriptRoot`, also muss team/ als
    Geschwister-Unterordner danebenliegen."""
    (tmp_path / "team" / "tools").mkdir(parents=True)
    shutil.copy(STATUS_PS1, tmp_path / "team-status.ps1")
    shutil.copy(kit_pfad("lib.psm1"), tmp_path / "team" / "lib.psm1")
    shutil.copy(kit_pfad("tools", "kosten.py"),
                tmp_path / "team" / "tools" / "kosten.py")
    # BL-113: PowerShell-Quelltext traegt ein BOM. Auch eine Fixture-Datei —
    # sonst praepariert sich der Test seinen eigenen roten Fall (BL-134).
    (tmp_path / "team.config.ps1").write_text(
        '$TEAM_BEUTEBUCH_TOOL = "' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
        '$TEAM_KOSTEN_TOOL = "' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        '$TEAM_DOMAENEN = "produkt"\n',
        encoding="utf-8-sig")
    (tmp_path / ".budget-ledger").write_text(
        "# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    (tmp_path / ".ralph-plan").write_text("plans/ralph-kaskade-1-produkt.md\n")
    (tmp_path / ".team-logs").mkdir()
    (tmp_path / ".ralph-logs").mkdir()
    return tmp_path


def test_rollen_abschluss_mit_beiden_notizen_laeuft_durch(tmp_path):
    """Der Aufruf, den TEAM.md vorgibt: zwei Notizen, KEIN Modus-Schalter.

    Das ist der Fall, den vorher niemand fuhr — die vorhandenen Faelle hatten
    entweder eine Notiz oder einen angehaengten Schalter.
    """
    verlange_pwsh()
    repo = _fixture_repo(tmp_path)
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./team-status.ps1",
         "--rollen-abschluss", "1", "produkt",
         "Rollen-Notiz", "Kaskade 1 gebaut"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    aus = r.stdout + r.stderr
    assert "does not contain a method named 'StartsWith'" not in aus, (
        f"BL-142 ist zurueck — der Rest ist wieder ein String:\n{aus}")
    assert "Unbekannter Modus" not in aus, (
        "BL-142 ist zurueck: Das erste ZEICHEN der zweiten Notiz wird als "
        f"Modus gelesen.\n{aus}")
    assert r.returncode == 0, f"Exit {r.returncode}:\n{aus}"

    ledger = (repo / ".budget-ledger").read_text(encoding="utf-8")
    # Beide Zeilen, mit je EIGENER Notiz (BL-34) — der Aufruf schreibt zwei.
    assert "Rollen-Notiz" in ledger, f"Rollen-Notiz fehlt im Ledger:\n{ledger}"
    assert "Kaskade 1 gebaut" in ledger, f"Bau-Notiz fehlt im Ledger:\n{ledger}"

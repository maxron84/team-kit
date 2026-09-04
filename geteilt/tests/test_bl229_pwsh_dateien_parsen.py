#!/usr/bin/env python3
"""BL-229: Ein zitiertes `#>` in einem Block-Kommentar hat `lib.psm1`
zerlegt — und damit die GANZE pwsh-Bahn, unbemerkt.

WIE DER FUND ENTSTAND
    Beim Einreihen zweier Feldmeldungen fiel die Suite mit 98 roten Faellen
    auf — alle auf der pwsh-Bahn, keiner auf der bash-Bahn. Die Sonde aus
    `test_bl182` sagte, dass JEDER Konfigurationswert die Modulgrenze nicht
    ueberlebt. Der Grund lag eine Ebene tiefer: `Import-Module` scheiterte,
    weil `pwsh/lib.psm1` nicht mehr parste.

    Der Kopfkommentar von `Team-HilfeKopf` (aus BL-223) zitierte die beiden
    Zeichen, zwischen denen ein Block-Kommentar steht — im Fliesstext, in
    Backticks. PowerShell kennt in einem Block-Kommentar keine Maskierung:
    Das zitierte Endezeichen SCHLIESST den Kommentar an Ort und Stelle. Alles
    darunter wurde Code, und die naechste Prosazeile war ein Syntaxfehler
    (`Unexpected token 'auf'`).

WARUM ES NIEMAND SAH
    Der Fix zu BL-223 wurde mit `bash bash/kit-test.sh` abgenommen — die
    bash-Bahn ist von einem kaputten `lib.psm1` nicht betroffen. Auf einem
    Wirt OHNE pwsh ueberspringen die pwsh-Faelle mit Begruendung; rot wird
    nichts. Der Schaden ist damit auf genau den Maschinen sichtbar, auf denen
    die Bahn benutzt wird, und dort ist er total: KEINE Rolle, kein
    Entrypoint, kein Werkzeug der pwsh-Bahn laeuft mit einem Modul, das nicht
    laedt.

WAS DIESER TEST PRUEFT
    Die GATTUNG, nicht das eine Zeichenpaar: JEDE ausgelieferte
    PowerShell-Datei muss vom PowerShell-PARSER angenommen werden. Das ist
    die billigste denkbare Zusicherung — sie braucht keinen Lauf, kein Repo,
    keinen Modellaufruf — und sie faengt jeden Syntaxbruch, nicht nur diesen.

    Gemessen wird mit `[System.Management.Automation.Language.Parser]`, also
    mit demselben Parser, der die Datei spaeter auch ausfuehrt. Ein
    `Import-Module` waere der schaerfere Test, fuehrt aber Code aus; hier
    genuegt und gehoert die reine Syntax.
"""
import json
import subprocess
from pathlib import Path

import pytest

from conftest import verlange_pwsh

REPO_ROOT = Path(__file__).resolve().parents[2]

# Der Parser bekommt die Dateiliste ueber eine Datei statt ueber die
# Kommandozeile: Pfade mit Leerzeichen sind unter Windows der Normalfall, und
# eine zerlegte Argumentliste haette genau hier ihren stillen Fehlerfall.
SONDE = r"""
$ErrorActionPreference = 'Stop'
$dateien = Get-Content -LiteralPath $args[0] -Encoding UTF8
$befunde = @()
foreach ($d in $dateien) {
    if (-not $d) { continue }
    $fehler = $null
    [System.Management.Automation.Language.Parser]::ParseFile($d, [ref]$null, [ref]$fehler) | Out-Null
    if ($fehler -and $fehler.Count) {
        $befunde += [ordered]@{
            datei = $d
            zeile = $fehler[0].Extent.StartLineNumber
            text  = $fehler[0].Message
        }
    }
}
$befunde | ConvertTo-Json -Compress -AsArray
"""


def _pwsh_dateien():
    gefunden = sorted(
        p for muster in ("*.ps1", "*.psm1")
        for p in REPO_ROOT.rglob(muster)
        if ".git" not in p.parts
    )
    if not gefunden:
        pytest.skip("keine PowerShell-Dateien in dieser Ablage")
    return gefunden


def test_jede_powershell_datei_parst(tmp_path):
    """Der Fund selbst — und jeder kuenftige Syntaxbruch derselben Gattung."""
    verlange_pwsh()
    dateien = _pwsh_dateien()
    liste = tmp_path / "dateien.txt"
    liste.write_text("\n".join(str(p) for p in dateien) + "\n", encoding="utf-8")
    skript = tmp_path / "sonde.ps1"
    skript.write_text(SONDE, encoding="utf-8-sig")

    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(skript), str(liste)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"

    befunde = json.loads(r.stdout.strip() or "[]")
    assert not befunde, (
        "Diese PowerShell-Dateien parsen nicht — auf der pwsh-Bahn laeuft "
        "damit nichts, was sie braucht:\n  "
        + "\n  ".join(f"{b['datei']}:{b['zeile']} — {b['text']}" for b in befunde))


def test_die_sonde_wuerde_einen_bruch_auch_melden(tmp_path):
    """Gegenprobe: Ein Waechter, der nie rot wird, sichert nichts ab
    (Bauart BL-14). Nachgestellt wird GENAU der Fund — ein zitiertes
    Endezeichen mitten im Block-Kommentar."""
    verlange_pwsh()
    kaputt = tmp_path / "kaputt.psm1"
    # Der Kommentar wird aus Teilen gebaut, damit DIESE Datei nicht selbst das
    # Zeichenpaar traegt, um das es geht. Nachgestellt wird der Fund
    # ZEICHENGENAU: Das zitierte Endezeichen schliesst den Kommentar, und die
    # naechste Prosazeile beginnt mit einer VARIABLEN — erst dort ist es ein
    # Syntaxfehler. (Eine Zeile aus lauter blanken Woertern waere fuer
    # PowerShell ein Kommandoaufruf und parste klaglos; genau deshalb ist der
    # Fund im Feld so lange unbemerkt geblieben.)
    ende = "#" + ">"
    anfang = "<" + "#"
    kaputt.write_text(
        f"{anfang}\n  Gelesen wird der `{anfang} … {ende}`-Block.\n"
        f"  $PSCommandPath zeigt auf das Modul, nicht auf das Skript.\n{ende}\n"
        "function Team-Beispiel { 'x' }\n",
        encoding="utf-8-sig")

    liste = tmp_path / "dateien.txt"
    liste.write_text(str(kaputt) + "\n", encoding="utf-8")
    skript = tmp_path / "sonde.ps1"
    skript.write_text(SONDE, encoding="utf-8-sig")

    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(skript), str(liste)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"
    assert json.loads(r.stdout.strip() or "[]"), (
        "Die Sonde meldet einen vorsaetzlich zerlegten Block-Kommentar NICHT "
        "— dann sichert der Test oben nichts ab.")

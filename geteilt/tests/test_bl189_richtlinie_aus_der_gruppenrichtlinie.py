#!/usr/bin/env python3
"""BL-189: Die einzige Abhilfe, die das Kit für die Ausführungsrichtlinie
nannte, ist die eine, die gegen eine Gruppenrichtlinie nicht gewinnen kann.

WAS GEMESSEN WURDE
    `kit-einrichten.ps1` prüfte vorbildlich den **effektiven** Wert und nannte
    bei `Restricted`/`AllSigned` als Abhilfe

        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

    wortgleich in `doku/einrichtung.md` Abschnitt 2 und in der Fehlertabelle.

    Die Rangfolge der Bereiche lautet aber

        MachinePolicy > UserPolicy > Process > CurrentUser > LocalMachine

    — **`CurrentUser` ist der zweitniedrigste.** Auf einer domänenverwalteten
    Maschine setzt der Befehl seinen Bereich zwar, ändert am effektiven Wert
    **nichts** und quittiert mit `PermissionDenied` /
    `ExecutionPolicyOverride`.

DER SCHADEN IST EINE SCHLEIFE
    Der nächste Lauf meldet daraufhin **exakt denselben Fehler**: Das Werkzeug
    sagt „tu X", X meldet rot, das Werkzeug sagt wieder „tu X". Auch
    `-ExecutionPolicy Bypass` am Aufruf hilft nicht — das ist Bereich
    `Process` und verliert ebenfalls.

    Ausgerechnet die Diagnose-Sorgfalt, die das Kit im `:keinpwsh`-Zweig jedes
    `.cmd`-Aufrufers betreibt („Das ist KEIN Fehler des Kits"), fehlte hier:
    Das Symptom war richtig benannt, die Abhilfe auf dieser Maschine nicht
    ausführbar, und **nichts sagte das**.

DIE GEGENRICHTUNG, GLEICHER URSPRUNG
    Steht die Richtlinie per GPO auf `Unrestricted`, läuft alles — aber der
    Setz-Befehl aus Abschnitt 2 wirft dieselbe rote Wand, **ohne dass
    irgendetwas kaputt ist**. Wer der Doku folgt, bekommt einen Fehler beim
    Befolgen einer Anweisung, die er gar nicht gebraucht hätte. Deshalb steht
    `Get-ExecutionPolicy -List` dort jetzt **vor** dem Setz-Befehl.

WARUM DIESE DATEI DIE FUNKTION FÄHRT UND NICHT DIE MASCHINE MISST
    Der Eintrag verlangt die Fallunterscheidung ausdrücklich als Funktion, die
    eine **Bereichsliste entgegennimmt statt selbst zu messen** — nur so sind
    beide Zweige nachweisbar, ohne dass ein Test eine echte Gruppenrichtlinie
    braucht. Gefahren wird die **echte** Funktion aus der **echten** Datei
    (`ParseFile` + `Invoke-Expression`, Bauart `BL-142`), nicht ein Nachbau.

AUSDRÜCKLICH NICHT AUFGENOMMEN
    Ein Umgehungsweg (`-Command`-Rohr, MotW entfernen, `Unblock-File`
    pauschal). Auf einer verwalteten Maschine ist die Richtlinie eine
    **Vorgabe**, kein Hindernis; ein Kit, das sie umgeht, macht seinen
    Anwender zum Regelbrecher. Ein eigener Fall hält das fest.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import nur_code, verlange_pwsh  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
EINRICHTEN = REPO_ROOT / "pwsh" / "kit-einrichten.ps1"
DOKU = REPO_ROOT / "doku" / "einrichtung.md"

FUNKTION = "Richtlinien-Abhilfe"


def _lies(pfad):
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt in dieser Ablage nicht (nur im Kit)")
    return pfad.read_text(encoding="utf-8-sig")


# --- (1) Die Fallunterscheidung, GEFAHREN ------------------------------------

def _abhilfe(tmp_path, bereiche, effektiv="Restricted"):
    """Fährt die echte Funktion mit einer gestellten Bereichsliste.

    `bereiche` ist eine Liste aus (Scope, ExecutionPolicy) — genau die Form,
    die `Get-ExecutionPolicy -List` liefert.
    """
    _lies(EINRICHTEN)
    verlange_pwsh()
    eintraege = ", ".join(
        "[pscustomobject]@{ Scope = '%s'; ExecutionPolicy = '%s' }" % (s, p)
        for s, p in bereiche)
    skript = f"""
$ErrorActionPreference = 'Stop'
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
           '{EINRICHTEN.as_posix()}', [ref]$null, [ref]$null)
$fn = $ast.FindAll({{ $args[0] -is
        [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $args[0].Name -eq '{FUNKTION}' }}, $true) | Select-Object -First 1
if (-not $fn) {{ throw '{FUNKTION} nicht im Syntaxbaum gefunden' }}
Invoke-Expression $fn.Extent.Text
$liste = @({eintraege})
$r = {FUNKTION} -Effektiv '{effektiv}' -Bereiche $liste
Write-Output '--- ABHILFE ---'
$r | ForEach-Object {{ Write-Output $_ }}
"""
    p = tmp_path / "sonde-richtlinie.ps1"
    p.write_text(skript, encoding="utf-8-sig", newline="\n")
    r = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"Sonde scheiterte:\n{r.stdout}\n{r.stderr}"
    assert "--- ABHILFE ---" in r.stdout, f"Sonde gab nichts aus:\n{r.stdout}"
    return r.stdout.split("--- ABHILFE ---", 1)[1]


GPO_HART = [("MachinePolicy", "Restricted"),
            ("UserPolicy", "Undefined"),
            ("Process", "Bypass"),
            ("CurrentUser", "Undefined"),
            ("LocalMachine", "Undefined")]

NUR_LOKAL = [("MachinePolicy", "Undefined"),
             ("UserPolicy", "Undefined"),
             ("Process", "Undefined"),
             ("CurrentUser", "Undefined"),
             ("LocalMachine", "Restricted")]


def test_gpo_fall_nennt_die_it_und_nicht_den_benutzerbefehl(tmp_path):
    """Der Fund selbst. Steht der harte Wert in `MachinePolicy`, ist
    `Set-ExecutionPolicy -Scope CurrentUser` kein Ratschlag, sondern eine
    Schleife: Der Befehl quittiert rot, und der nächste Lauf sagt dasselbe."""
    text = _abhilfe(tmp_path, GPO_HART)
    assert "Set-ExecutionPolicy" not in text or "wuerde hier mit" in text, (
        "BL-189: Die Abhilfe empfiehlt weiter den Befehl, der gegen eine "
        f"Gruppenrichtlinie nicht gewinnen kann:\n{text}")
    assert re.search(r"IT\b", text), (
        "BL-189: Die Meldung sagt nicht, dass das kein Benutzerbefehl aendern "
        f"kann. Genau diese Auskunft fehlte:\n{text}")
    assert "MachinePolicy" in text, (
        "BL-189: Die Meldung nennt den Bereich nicht, aus dem der harte Wert "
        f"kommt — dann ist sie nicht nachvollziehbar:\n{text}")


def test_lokaler_fall_nennt_weiter_den_benutzerbefehl(tmp_path):
    """Die Gegenrichtung. Ohne Gruppenrichtlinie ist `-Scope CurrentUser` die
    **richtige** Auskunft und muss stehen bleiben — ein Fix, der sie überall
    entfernte, hätte den häufigeren Fall verschlechtert."""
    text = _abhilfe(tmp_path, NUR_LOKAL)
    assert "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned" in text, (
        "BL-189: Der lokale Fall hat seine Abhilfe verloren. Hier IST sie "
        f"ausfuehrbar:\n{text}")
    assert "IT" not in text, (
        "BL-189: Der lokale Fall verweist an die IT, obwohl der Anwender das "
        f"selbst kann:\n{text}")


def test_die_funktion_misst_nicht_selbst(tmp_path):
    """Der Riegel, der die Gegenprobe überhaupt erst möglich macht.

    Misst die Funktion selbst, ist der GPO-Zweig auf einer nicht verwalteten
    Maschine unerreichbar — und damit unbewiesen. Genau das verlangt der
    Eintrag: eine Bereichsliste **entgegennehmen** statt messen.
    """
    text = _lies(EINRICHTEN)
    anfang = text.index(f"function {FUNKTION}")
    ende = text.index("\n}\n", anfang)
    # Kommentare raus: Der Block ERKLAERT die Bereichsliste und nennt dabei
    # Get-ExecutionPolicy — das ist die Begruendung, nicht die Messung.
    koerper = nur_code(text[anfang:ende])
    assert "Get-ExecutionPolicy" not in koerper, (
        "BL-189: Die Funktion misst selbst. Dann laesst sich der "
        "Gruppenrichtlinien-Zweig nur auf einer verwalteten Maschine fahren.")
    assert "-Bereiche" in koerper or "$Bereiche" in koerper, (
        "BL-189: Die Funktion nimmt keine Bereichsliste entgegen.")


def test_die_meldung_zeigt_die_bereichsliste(tmp_path):
    """`Get-ExecutionPolicy -List` gehört in die Meldung. Ohne sie steht der
    Anwender vor einem Befehl, der auf seiner Maschine nicht wirken kann, und
    sieht nicht warum."""
    text = _lies(EINRICHTEN)
    stelle = text.index("Ausfuehrungsrichtlinie ist")
    umfeld = text[max(0, stelle - 2000):stelle + 500]
    assert "Get-ExecutionPolicy -List" in umfeld, (
        "BL-189: Die Fehlerstelle gibt die Bereichsliste nicht aus.")


# --- (2) Die Doku ------------------------------------------------------------

def test_abschnitt_zwei_zeigt_zuerst_die_liste():
    """Die harmlose Gegenrichtung: Steht die GPO auf `Unrestricted`, läuft
    alles — aber der Setz-Befehl wirft trotzdem eine rote Wand. Wer der Doku
    folgt, bekommt dann einen Fehler beim Befolgen einer Anweisung, die er gar
    nicht gebraucht hätte."""
    text = _lies(DOKU)
    abschnitt = text[text.index("### 2. Die Ausführungsrichtlinie"):]
    abschnitt = abschnitt[:abschnitt.index("### 3.")]
    assert "Get-ExecutionPolicy -List" in abschnitt, (
        "BL-189: Abschnitt 2 nennt die Bereichsliste nicht.")
    assert abschnitt.index("Get-ExecutionPolicy -List") < abschnitt.index(
        "Set-ExecutionPolicy"), (
        "BL-189: Der Setz-Befehl steht VOR der Liste. Dann tippt ihn auch, wer "
        "ihn nicht braucht — und bekommt eine rote Wand ohne Defekt.")
    assert "MachinePolicy" in abschnitt, (
        "BL-189: Abschnitt 2 unterscheidet die beiden Faelle nicht.")


def test_fehlertabelle_fuehrt_den_gpo_fall_als_eigene_zeile():
    """Die Fehlertabelle ist die Stelle, an der jemand mit dem Symptom in der
    Hand nachschlägt. Steht dort nur die eine Abhilfe, führt sie in dieselbe
    Schleife wie vorher das Werkzeug."""
    text = _lies(DOKU)
    zeilen = [z for z in text.splitlines()
              if z.startswith("|") and "running scripts is disabled" in z]
    assert zeilen, "BL-189: Die Zeile zum Symptom fehlt in der Fehlertabelle."
    gpo = [z for z in text.splitlines()
           if z.startswith("|") and "MachinePolicy" in z]
    assert gpo, (
        "BL-189: Die Fehlertabelle kennt den Gruppenrichtlinien-Fall nicht. "
        "Wer mit dem Symptom nachschlaegt, bekommt weiter den Befehl, der auf "
        "seiner Maschine nicht wirkt.")


def test_kein_umgehungsweg_wird_genannt():
    """Auf einer verwalteten Maschine ist die Richtlinie eine **Vorgabe**, kein
    Hindernis. Ein Kit, das sie umgeht, macht seinen Anwender zum
    Regelbrecher — der Eintrag schließt das ausdrücklich aus."""
    verboten = [
        ("Unblock-File", "pauschales Entfernen der Mark-of-the-Web"),
        ("-ExecutionPolicy Unrestricted", "Umgehung per Aufrufschalter"),
    ]
    for pfad in (EINRICHTEN, DOKU):
        text = _lies(pfad)
        for muster, warum in verboten:
            for treffer in re.finditer(re.escape(muster), text):
                nummer = text.count("\n", 0, treffer.start()) + 1
                zeile = text.splitlines()[nummer - 1]
                # Eine Nennung, die den Weg AUSSCHLIESST, ist erlaubt und
                # sogar erwuenscht — verboten ist die EMPFEHLUNG.
                if any(w in zeile for w in ("nicht", "NICHT", "verliert",
                                            "hilft nicht", "absichtlich")):
                    continue
                pytest.fail(
                    f"BL-189: {pfad.name}:{nummer} empfiehlt einen "
                    f"Umgehungsweg ({warum}):\n  {zeile.strip()}")

"""BL-122: Auf der pwsh-Bahn ist ein Exit-Code != 0 ein WERT, keine Ausnahme.

WARUM DIESER TEST EXISTIERT
    Auf einer echten Windows-Maschine brach `kit-einrichten.ps1` in der
    Uebergabe an `install.ps1` ab. Die Meldung nannte `python3.exe` und sah
    aus wie ein fehlendes Python. Es war keines: Der Interpreter lag als
    python.exe da, und der Code sucht python3, python UND py der Reihe nach.

    Was wirklich passierte: Unter Windows liegen in
    %LOCALAPPDATA%\\Microsoft\\WindowsApps App-Execution-Aliase namens
    python.exe und python3.exe. Get-Command gibt sie klaglos zurueck; gestartet
    starten sie keinen Interpreter, sondern oeffnen den Microsoft Store und
    enden mit Exit-Code 9009. Genau dafuer war die Kandidatenschleife gebaut —
    sie prueft die Antwort, nicht den Namen. Nur kam sie nicht dazu.

    Seit PowerShell 7.4 ist $PSNativeCommandUseErrorActionPreference
    standardmaessig $true. Ein NATIVER Befehl mit Exit-Code != 0 loest damit
    einen Fehler nach $ErrorActionPreference aus — und `install.ps1` steht auf
    'Stop'. Der Platzhalter warf also einen TERMINIERENDEN Fehler, bevor die
    naechste Zeile lief. `2>$null` half nicht: Die Meldung kommt von
    PowerShell, nicht vom Programm.

WAS DARAN DIE EIGENTLICHE LEHRE IST
    Die ganze pwsh-Bahn ist fuer den klassischen Vertrag geschrieben:
    aufrufen, $LASTEXITCODE lesen, entscheiden. Unter 7.4 war jede dieser
    Entscheidungen unerreichbar, sobald der Aufrufer auf 'Stop' stand:

      * Team-ClaudeSchreiben liest den Exit-Code der Agenten-CLI. Daran haengen
        die 429-Mechanik, der Abo-nach-Key-Fallback und die Ergebnispruefung.
        JEDER normale CLI-Fehler haette den Lauf gerissen statt ihn zu
        behandeln — die teuerste Stelle im ganzen Kit.
      * `git rev-parse` in install.ps1 traegt die freundliche Meldung
        "ist kein Git-Repository" samt Exit 2. Sie war tot.
      * Die Selbstverifikation (py_compile, pytest) meldet Befunde ueber
        $LASTEXITCODE. Ein roter Testlauf haette den Installer abgebrochen,
        statt ihn rot abschliessen zu lassen.

    Und das war unter Linux nicht messbar — nicht weil die Plattform anders
    ist (die Praeferenz gilt ueberall), sondern weil dort jeder dieser Aufrufe
    GELINGT. Geprueft worden ist immer nur der glueckliche Pfad. Unter Windows
    macht der Store-Platzhalter aus dem gluecklichen Pfad einen Fehlerpfad —
    und legt damit frei, was die ganze Zeit unerreichbar war.

    Dieselbe Familie wie BL-113: eine Zusicherung, die unter pwsh 7 auf Linux
    vollstaendig gruen war und auf dem Ziel an der ersten Datei scheiterte.

WAS DER TEST PRUEFT
    Dass jede ausfuehrbare Datei der pwsh-Bahn die Praeferenz ausdruecklich
    festnagelt. Nicht, dass sie irgendwo steht: dass sie in JEDER Datei steht,
    die einen nativen Befehl aufrufen kann. Eine neue Rolle, die den Pin
    vergisst, faellt hier auf — nicht erst auf einer Windows-Maschine.
"""
from pathlib import Path
from conftest import ueberspringe_ohne_beide_bahnen

WURZEL = Path(__file__).resolve().parents[2]
PIN = "$PSNativeCommandUseErrorActionPreference = $false"

# Beide Ablagen: die installierte (Wurzel, team/) und die des Kits (pwsh/).
# Ein nicht passendes Muster liefert einfach nichts.
MUSTER = ("*.ps1", "team/*.ps1", "team/*.psm1", "scripts/*.ps1", "entry/*.ps1",
          "pwsh/*.ps1", "pwsh/*.psm1", "pwsh/entry/*.ps1", "pwsh/scripts/*.ps1")

# team.config.ps1 ist reine Wertzuweisung und ruft nichts auf. Sie steht hier
# namentlich, damit die Ausnahme eine Begruendung hat statt eines Musters.
OHNE_PIN_ERLAUBT = {"team.config.ps1"}


def _dateien():
    treffer = []
    for m in MUSTER:
        treffer.extend(sorted(p for p in WURZEL.glob(m) if p.is_file()))
    return treffer


def test_jede_pwsh_datei_nagelt_die_exitcode_semantik_fest():
    ueberspringe_ohne_beide_bahnen()
    dateien = [p for p in _dateien() if p.name not in OHNE_PIN_ERLAUBT]
    assert dateien, "keine PowerShell-Dateien gefunden — Muster stimmt nicht mehr"
    ohne = [p.relative_to(WURZEL).as_posix()
            for p in dateien if PIN not in p.read_text(encoding="utf-8-sig")]
    assert not ohne, (
        "Ohne '" + PIN + "' macht PowerShell 7.4 aus jedem Exit-Code != 0 "
        "eines nativen Befehls einen Fehler nach $ErrorActionPreference. "
        "Jede Zeile, die danach $LASTEXITCODE liest, ist dann unerreichbar — "
        "einschliesslich der 429-Mechanik: " + ", ".join(ohne))


def test_die_python_suche_fragt_plattformgerecht():
    """Unter Windows zuerst python, sonst zuerst python3.

    python.org und `winget install Python.Python.3.x` legen python.exe und den
    py-Launcher an, KEIN python3.exe — was dort als python3 gefunden wird, ist
    meist der Store-Platzhalter. Unter Linux ist es umgekehrt: python fehlt
    oder zeigt auf Python 2. Eine feste Reihenfolge kann nur eine der beiden
    Plattformen richtig bedienen.
    """
    ueberspringe_ohne_beide_bahnen()
    treffer = [p for p in _dateien()
               if "python3" in p.read_text(encoding="utf-8-sig")
               and "Get-Command" in p.read_text(encoding="utf-8-sig")]
    assert treffer, "keine Datei mit Python-Suche gefunden — Muster stimmt nicht mehr"
    fehlend = []
    for p in treffer:
        text = p.read_text(encoding="utf-8-sig")
        if "'python3', 'python', 'py'" in text or '"python3", "python", "py"' in text:
            if "$IsWindows" not in text:
                fehlend.append(p.relative_to(WURZEL).as_posix())
    assert not fehlend, (
        "Feste Kandidatenreihenfolge ohne Plattformfall — unter Windows wird "
        "damit zuerst der Store-Platzhalter python3.exe befragt: "
        + ", ".join(fehlend))

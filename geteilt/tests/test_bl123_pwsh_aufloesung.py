"""BL-123: Die .cmd-Aufrufer loesen `pwsh` auf, statt es vorauszusetzen.

WARUM DIESER TEST EXISTIERT
    Auf einer echten Windows-Maschine meldete `team-test.cmd`:

        'pwsh' is not recognized as an internal or external command,
        operable program or batch file.

    Jede der neun .cmd-Dateien rief `pwsh` blank auf. Steht PowerShell 7 nicht
    im PATH GENAU DIESER cmd-Sitzung, ist das die einzige Auskunft, die der
    Anwender bekommt — eine Meldung ueber cmd, nicht ueber das Kit. Sie nennt
    weder die Ursache noch den Ausweg, und sie sieht aus wie eine kaputte
    Installation.

WAS DARAN DIE EIGENTLICHE LEHRE IST
    Das Kit kennt diese Falle bereits und hat sie an anderer Stelle geloest:
    `Team-ClaudeBefehl` in lib.psm1 loest `claude` ueber Get-Command auf und
    meldet den Fehlschlag mit eigenem Wortlaut, weil eine gescheiterte
    Aufloesung sonst wie ein Auth-Fehler aussieht. Fuer den Interpreter, der
    die ganze Bahn traegt, galt dieselbe Lehre nicht — obwohl er die
    empfindlichere Stelle ist: Wer `claude` nicht findet, hat ein Kit, das
    laeuft und sich beschwert. Wer `pwsh` nicht findet, hat gar nichts.

    Die drei haeufigsten Ursachen sind alle KEIN fehlendes PowerShell 7:
    eine cmd-Sitzung, die vor der Installation offen war; ein per MSI
    installiertes pwsh, dessen PATH-Eintrag die laufende Shell nicht erreicht
    hat; und der Klassiker, dass jemand `powershell` (5.1) fuer dasselbe haelt.

WAS DER TEST PRUEFT
    Zweierlei, und beides muss zusammen gelten: dass KEINE .cmd `pwsh` blank
    aufruft, und dass jede von ihnen einen Ausweg nennt, wenn die Aufloesung
    scheitert. Eine Aufloesung ohne Meldung waere nur eine leisere Fassung
    desselben Fehlers.
"""
import re
from pathlib import Path
from conftest import ueberspringe_ohne_beide_bahnen

WURZEL = Path(__file__).resolve().parents[2]

# Beide Ablagen: die installierte (Wurzel) und die des Kits (pwsh/entry/).
MUSTER = ("*.cmd", "pwsh/entry/*.cmd")

# Ein blanker Aufruf: 'pwsh' am Zeilenanfang, ohne vorangehende Aufloesung.
BLANK = re.compile(r"^\s*pwsh(\.exe)?\s", re.IGNORECASE | re.MULTILINE)


def _dateien():
    treffer = []
    for m in MUSTER:
        treffer.extend(sorted(p for p in WURZEL.glob(m) if p.is_file()))
    return treffer


def test_keine_cmd_ruft_pwsh_blank_auf():
    ueberspringe_ohne_beide_bahnen()
    dateien = _dateien()
    assert dateien, "keine .cmd-Dateien gefunden — Muster stimmt nicht mehr"
    blank = [p.relative_to(WURZEL).as_posix()
             for p in dateien if BLANK.search(p.read_text(encoding="ascii"))]
    assert not blank, (
        "Diese .cmd rufen pwsh blank auf. Fehlt PowerShell 7 im PATH der "
        "cmd-Sitzung, ist 'is not recognized as an internal or external "
        "command' die einzige Auskunft, die der Anwender bekommt: "
        + ", ".join(blank))


def test_jede_cmd_nennt_einen_ausweg():
    """Aufloesen genuegt nicht — der Fehlschlag muss sagen, was zu tun ist.

    Sonst ist die Aufloesung nur eine leisere Fassung desselben Fehlers: Der
    Aufrufer endet still, und der Anwender weiss noch weniger als vorher.
    """
    ueberspringe_ohne_beide_bahnen()
    dateien = _dateien()
    ohne = []
    for p in dateien:
        text = p.read_text(encoding="ascii")
        if "TEAM_PWSH" not in text:
            continue                      # keine Aufloesung -> anderer Test
        if "winget install" not in text or "Microsoft.PowerShell" not in text:
            ohne.append(p.relative_to(WURZEL).as_posix())
    assert not ohne, (
        "Aufloesung ohne Ausweg: Diese .cmd erkennen ein fehlendes pwsh, "
        "nennen aber nicht, wie man es bekommt: " + ", ".join(ohne))

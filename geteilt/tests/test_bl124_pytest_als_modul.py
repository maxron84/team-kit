"""BL-124: pytest wird als MODUL gesucht, nicht nur als Befehl im PATH.

WARUM DIESER TEST EXISTIERT
    Auf einer echten Windows-Maschine war pytest installiert, und
    `team-test.cmd` meldete weiterhin "pytest nicht gefunden".

    Der Grund ist derselbe wie bei `pwsh` (BL-123) und beim Store-Platzhalter
    (BL-122): gesucht wurde ein NAME im PATH, statt die Faehigkeit zu proben.
    `pip install pytest` legt die ausfuehrbare Datei in ein Scripts- bzw.
    bin-Verzeichnis, das oft nicht im PATH steht — bei `--user` warnt pip beim
    Installieren sogar ausdruecklich davor. Das Modul ist dann da und
    importierbar; der Befehl ist es nicht.

WAS DARAN DAS PEINLICHE IST
    Das Kit hat den Zustand selbst erzeugt. `team-test.sh` empfahl woertlich
    `pip install --user pytest` — also genau die Installationsart, deren
    Zielverzeichnis typischerweise fehlt — und meldete danach "pytest nicht
    gefunden", zusammen mit derselben Empfehlung noch einmal. Ein Anwender,
    der ihr folgt, landet in einer Schleife, aus der die Meldung nicht
    herausfuehrt.

    Die zweite, leisere Haelfte: Ein `pytest` im PATH kann zu einer ANDEREN
    Python-Installation gehoeren als das Python, unter dem `team/tools/`
    laeuft. Dann laufen die Tests unter einem anderen Interpreter als der
    Code, den sie pruefen — gruen, und trotzdem ohne Aussage. Der Modulaufruf
    ueber denselben Interpreter schliesst beides zugleich aus.

WAS DER TEST PRUEFT
    Dass keine Datei des Kits pytest allein ueber den PATH-Namen sucht, ohne
    vorher den Modulweg versucht zu haben. Ein Fallback auf den blanken Befehl
    ist erlaubt und sinnvoll — aber erst als ZWEITER Versuch.
"""
import re
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]

# Dateien, die pytest aufrufen oder seine Anwesenheit pruefen. Beide Ablagen.
MUSTER = ("team-test.sh", "team-test.ps1",
          "bash/entry/team-test.sh", "pwsh/entry/team-test.ps1",
          "bash/install.sh", "pwsh/install.ps1",
          "bash/kit-einrichten.sh", "pwsh/kit-einrichten.ps1",
          "pwsh/kit-test.ps1")

MODULWEG = re.compile(r"-m\s+pytest")


def _dateien():
    return [WURZEL / m for m in MUSTER if (WURZEL / m).is_file()]


def test_wer_pytest_sucht_versucht_zuerst_den_modulweg():
    dateien = _dateien()
    assert dateien, "keine der erwarteten Dateien gefunden — Muster stimmt nicht mehr"
    ohne = []
    for p in dateien:
        text = p.read_text(encoding="utf-8-sig")
        nennt_pytest = "pytest" in text
        # Eine Datei, die pytest nur im Fliesstext erwaehnt, ist nicht gemeint.
        prueft = ("command -v pytest" in text
                  or "Get-Command pytest" in text
                  or re.search(r"^\s*(exec\s+)?&?\s*pytest\s", text, re.MULTILINE))
        if nennt_pytest and prueft and not MODULWEG.search(text):
            ohne.append(p.relative_to(WURZEL).as_posix())
    assert not ohne, (
        "Diese Dateien suchen pytest nur als Befehl im PATH. Bei einer "
        "--user-Installation steht sein bin-Verzeichnis dort oft nicht — das "
        "Modul ist da, der Befehl nicht, und die Meldung lautet trotzdem "
        "'nicht gefunden': " + ", ".join(ohne))


def test_kein_hinweis_empfiehlt_nur_den_user_weg():
    """`pip install --user pytest` allein ist der Rat, der das Problem macht.

    Er darf vorkommen — aber nicht als einziger Weg, ohne ein Wort darueber,
    dass sein Zielverzeichnis im PATH fehlen kann.
    """
    schlecht = []
    for p in _dateien():
        text = p.read_text(encoding="utf-8-sig")
        if "install --user pytest" not in text:
            continue
        if "PATH" not in text:
            schlecht.append(p.relative_to(WURZEL).as_posix())
    assert not schlecht, (
        "Empfiehlt `pip install --user pytest`, ohne die PATH-Falle zu "
        "nennen — genau die Schleife, aus der die alte Meldung nicht "
        "herausfuehrte: " + ", ".join(schlecht))

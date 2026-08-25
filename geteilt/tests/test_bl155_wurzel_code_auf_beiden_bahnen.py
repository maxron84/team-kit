#!/usr/bin/env python3
"""BL-155: Die Wurzel-Code-Pruefung aus `BL-52` gab es nur auf der bash-Bahn.

WAS GEFEHLT HAT
    `install.sh` meldet beim `--update` ungepruefen Code in der Projektwurzel
    ("Ungeprueft in der Wurzel: main.py") und nennt `TEAM_WEITERER_CODE` als
    Abhilfe. Auf der pwsh-Bahn gab es diesen Hinweis nicht. Ein einbahnig-pwsh
    installiertes Bestandsprojekt — also genau die Lage, fuer die die pwsh-Bahn
    ueberhaupt gebaut ist — erfuhr damit NIE, dass sein Einstiegspunkt in der
    Wurzel ausserhalb des Pruefumfangs liegt.

    Das war keine ungepruefte Haelfte wie bei `BL-146`, sondern eine fehlende:
    Es gab nichts auszufuehren.

DER TEURE TEIL IST NICHT DIE MELDUNG, SONDERN DIE AUSNAHMELISTE
    In `install.sh` stand bis `BL-154` eine ABSCHRIFT der Entrypoints — 24
    Namen, von Hand gepflegt. Sie war ab dem naechsten neuen Entrypoint falsch,
    und zwar auf die unangenehme Art: Das Kit meldete seine EIGENE Datei als
    "ungepruefen Projektcode". Eine Warnung, die in jedem gruenen Projekt
    erscheint, erzieht zum Wegsehen (`BL-14`) — und genau daneben stand der
    Hinweis auf echten Wurzel-Code, den man dann mit uebersieht.

    `BL-154` hat die Liste durch eine Messung ersetzt: Was in `bash/entry/`
    oder `pwsh/entry/` liegt, ist ein Entrypoint des Kits. Die pwsh-Fassung
    musste dieselbe Regel nehmen — eine zweite Liste dort waere die Abschrift
    gewesen, nur umgezogen. Dieser Test haelt das fest.

DIE ARBEITSTEILUNG DIESER DATEI
    Den LAUF fuehrt `kit-test.sh` Stufe 7: Dort steht ein echtes
    Bestandsprojekt mit `main.py` in der Wurzel, und beide Installer fahren
    ihr Update darauf. Hier steht die Zusicherung am QUELLTEXT, fuer BEIDE
    Bahnen — auf einer Maschine ohne PowerShell kann der Lauf die pwsh-Fassung
    nicht pruefen (`BL-117`-Lage), ein statischer Vergleich laeuft ueberall.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _installer(name):
    """Der Installer beider Bahnen liegt im KIT, nicht im Projekt — ein
    installiertes Projekt traegt ihn gar nicht. Fehlt er, wird uebersprungen
    statt falsch gruen gemeldet (dieselbe Bauart wie in BL-147)."""
    pfad = REPO_ROOT / ("bash" if name.endswith(".sh") else "pwsh") / name
    if not pfad.is_file():
        pytest.skip(f"{name} liegt hier nicht (installiertes Projekt statt Kit-Ablage)")
    return pfad.read_text(encoding="utf-8-sig")


def test_bash_meldet_ungepruefen_wurzel_code():
    """Die Bahn, auf der es den Hinweis schon gab — als Anker fuer den
    Vergleich. Faellt er, ist nicht die Portierung schuld."""
    quelle = _installer("install.sh")
    assert "Ungeprueft in der Wurzel:" in quelle
    assert "TEAM_WEITERER_CODE" in quelle


def test_pwsh_meldet_ungepruefen_wurzel_code():
    """Der Fund selbst: Der Hinweis existiert auf der pwsh-Bahn ueberhaupt.

    Geprueft wird auf denselben Wortlaut, nicht auf eine sinngemaesse
    Entsprechung. Der Grund ist nicht Aesthetik: `kit-test.sh` greppt nach
    dieser Zeichenkette, und ein Projekt, das den einen Wortlaut kennt und den
    anderen nicht, hat zwei Fehlermeldungen fuer einen Befund.
    """
    quelle = _installer("install.ps1")
    assert "Ungeprueft in der Wurzel:" in quelle, (
        "install.ps1 kennt die Wurzel-Code-Pruefung aus BL-52 nicht. Ein "
        "einbahnig-pwsh installiertes Bestandsprojekt erfaehrt damit nie, "
        "dass sein Einstiegspunkt in der Wurzel ausserhalb des Pruefumfangs "
        "liegt (BL-155).")
    assert "Pruefumfang endet an" in quelle, (
        "die Ueberschrift des Hinweises fehlt — der Befund steht dann ohne "
        "seine Begruendung da")
    assert "TEAM_WEITERER_CODE" in quelle, (
        "der Hinweis nennt die Abhilfe nicht. Ein Befund ohne Abhilfe ist "
        "eine Warnung, die man wegklickt (BL-14).")


def test_pwsh_haengt_den_hinweis_an_den_update_pfad():
    """Der Hinweis gehoert ins Update und nirgendwo sonst.

    Bei der Erstinstallation wird `TEAM_WEITERER_CODE` gefragt und in die
    Konfiguration geschrieben — dort ist der Befund also schon behandelt.
    Beim Update wird die Konfiguration bewusst NICHT angefasst, und nur dort
    kann der Wert aus einer aelteren Kit-Version noch fehlen. Ein Hinweis bei
    jeder Erstinstallation waere Rauschen.
    """
    quelle = _installer("install.ps1")
    stelle = quelle.index("Ungeprueft in der Wurzel:")
    davor = quelle[:stelle]
    assert "Bestand in der Schreibzone (BL-51)" in davor, (
        "Der BL-52-Hinweis steht nicht im Update-Pfad. Er gehoert direkt "
        "hinter den BL-51-Block — beides sind Befunde, die nur beim Update "
        "ueberhaupt sichtbar werden.")


@pytest.mark.parametrize("name,belege", [
    # bash (BL-154): fragt das Kit ueber Dateisystem-Tests auf entry/
    ("install.sh", ('"$KIT/bash/entry/$NAME"', '"$KIT/pwsh/entry/$NAME"')),
    # pwsh (BL-155): dieselbe Regel, nicht eine zweite Liste
    ("install.ps1", (r"bash\entry\$($f.Name)", r"pwsh\entry\$($f.Name)")),
])
def test_die_entrypoints_werden_gemessen_statt_abgeschrieben(name, belege):
    """Die Lehre aus BL-154, jetzt auf beiden Bahnen zugesichert.

    Beide Installer entscheiden "ist das ein Entrypoint des Kits?" daran, dass
    die Datei in `bash/entry/` oder `pwsh/entry/` LIEGT. Das kann nicht
    veralten, weil es keine zweite Liste mehr gibt. Eine handgepflegte Liste
    an dieser Stelle ist ab dem naechsten neuen Entrypoint falsch — und meldet
    dann die eigene Datei des Kits als ungepruefen Projektcode.
    """
    quelle = _installer(name)
    for beleg in belege:
        assert beleg in quelle, (
            f"{name} entscheidet nicht mehr ueber bash/entry/ und pwsh/entry/, "
            f"ob eine Datei ein Entrypoint des Kits ist ({beleg} fehlt). Wenn "
            "hier wieder eine Namensliste steht, ist BL-154 zurueck: Das Kit "
            "meldet seine eigenen Dateien als ungepruefen Projektcode, und der "
            "echte Fund daneben geht darin unter.")


def test_pwsh_traegt_keine_abgeschriebene_entrypoint_liste():
    """Die Gegenprobe zum Fall darueber: nicht nur die Messung ist da, es ist
    auch keine Liste danebengeblieben.

    Gesucht wird nach drei Entrypoint-Namen in EINER Zeile — die Form, in der
    eine solche Liste immer geschrieben wird. Ein einzelner Name ist harmlos
    (`team.config.ps1` kommt zu Recht oft vor), drei nebeneinander sind eine
    Aufzaehlung.
    """
    quelle = _installer("install.ps1")
    namen = [p.name for p in (REPO_ROOT / "pwsh" / "entry").glob("*.ps1")]
    for zeile in quelle.splitlines():
        treffer = [n for n in namen if n in zeile]
        assert len(treffer) < 3, (
            "In install.ps1 steht eine Aufzaehlung von Entrypoint-Namen "
            f"({', '.join(treffer)}). Genau die hat BL-154 auf der bash-Bahn "
            f"abgeschafft:\n    {zeile.strip()}")


def test_pwsh_nennt_die_konfiguration_die_das_projekt_wirklich_hat():
    """Ein Detail, an dem die pwsh-Fassung besser ist als ihr Vorbild — und
    genau deshalb festgehalten.

    Die bash-Fassung nennt in der Abhilfe fest `team.config.sh`. In einer
    einbahnig-pwsh installierten Ablage gibt es diese Datei nicht: Die Abhilfe
    verwiese dort auf eine Datei, die der Leser nicht findet. Die pwsh-Fassung
    nimmt die Quelle, aus der sie die Werte tatsaechlich gelesen hat.
    """
    quelle = _installer("install.ps1")
    stelle = quelle.index("Ungeprueft in der Wurzel:")
    block = quelle[stelle:stelle + 1400]
    assert "$konfQuelle" in block, (
        "Die Abhilfe nennt eine fest verdrahtete Konfigurationsdatei. In "
        "einer einbahnigen Ablage ist das ein Verweis ins Leere.")
    assert "Team-Wert 'TEAM_WEITERER_CODE'" in block, (
        "Die Abhilfe zeigt die Schreibweise der bash-Konfiguration auch dann, "
        "wenn das Projekt eine team.config.ps1 hat — dort ist sie falsch.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

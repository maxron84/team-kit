#!/usr/bin/env python3
"""BL-225 — die Einrichtungsanleitung nennt dieselbe Zahl wie das README und
hatte keinen Wächter.

`doku/einrichtung.md` sagt in der Übersichtstabelle **ganz oben**, wie viele
Dateien `install.sh` in ein Zielprojekt legt. Am 2026-09-03 stand dort **136**,
während der Installer **189** schrieb — 53 Dateien Unterschied, in der ersten
Bildschirmhöhe der Anleitung, die ein neuer Nutzer zuerst liest.

`kit-readme-pruefen.py` prüfte die Zahl seit jeher — aber nur im README, weil
es `--readme` bekommt und sonst nichts. Dieselbe Gattung eine Datei weiter war
unbewacht. Das ist `BL-198`/`BL-224` ein drittes Mal: Der Wächter deckt ab, wo
man ihn hingeschickt hat.

WARUM NUR DIE DATEIZAHL UND NUR DIESE DATEI. Der Belegstand in
`einrichtung.md` nennt **absichtlich historische** Testzahlen (»160 der 487
Tests fielen«). Die Testzahl-Gattung dort mitzuprüfen hieße, an einer
richtigen Stelle rot zu schlagen — und ein Wächter, der das tut, wird
abgeschaltet statt befolgt (`BL-14`). Der lebende CHANGELOG-Teil und der
Backlog nennen ihrerseits Dateizahlen aus anderem Anlass und bleiben deshalb
ebenfalls draußen. Eine Gattung, eine Datei, beides benannt.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
PRUEFER = WURZEL / "geteilt" / "kit-readme-pruefen.py"
ANLEITUNG = WURZEL / "doku" / "einrichtung.md"

pytestmark = pytest.mark.skipif(
    not PRUEFER.is_file(),
    reason="kit-readme-pruefen.py liegt nur im Kit, nicht in der Installation")

DATEIZAHL = re.compile(r"(\d+) Dateien\b")


def _mini_kit(tmp_path, readme, anleitung=None):
    """Ein Kit im Kleinen. Der Prüfer leitet seine Nachbardateien aus dem
    Elternverzeichnis seines eigenen Ortes ab — ein Test am echten
    `doku/einrichtung.md` könnte die Regel nur bestätigen, indem er sie
    verstümmelt."""
    (tmp_path / "geteilt").mkdir()
    (tmp_path / "plans").mkdir()
    (tmp_path / "doku").mkdir()
    ziel = tmp_path / "geteilt" / "kit-readme-pruefen.py"
    ziel.write_text(PRUEFER.read_text(encoding="utf-8"), encoding="utf-8",
                    newline="\n")
    kopf = "| Nr | Was | Woher | Status |\n|---|---|---|---|\n"
    (tmp_path / "plans" / "backlog-archiv.md").write_text(
        kopf + "| BL-1 | x | y | **erledigt** |\n",
        encoding="utf-8", newline="\n")
    (tmp_path / "plans" / "backlog.md").write_text(
        kopf + "| BL-7 | x | y | **offen.** |\n",
        encoding="utf-8", newline="\n")
    (tmp_path / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    if anleitung is not None:
        (tmp_path / "doku" / "einrichtung.md").write_text(
            anleitung, encoding="utf-8", newline="\n")
    return ziel


def _readme(dateien):
    return ("Kit mit 7 Tests, `BL-1`…`BL-7`, 1 Archiv-Einträge, "
            "1 offene Einträge.\n"
            f"Danach liegen {dateien} Dateien im Zielprojekt.\n")


def _lauf(pruefer, *argumente):
    return subprocess.run([sys.executable, str(pruefer), *argumente],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


# --- (1) Der Fund selbst -----------------------------------------------------


def test_eine_falsche_dateizahl_in_der_anleitung_wird_rot(tmp_path):
    """Der Kern des Eintrags: Das README stimmt, die Anleitung nicht — und
    genau so lag es im Feld."""
    pruefer = _mini_kit(tmp_path, _readme(189),
                        anleitung="`install.sh` legt die 136 Dateien ab.\n")
    ergebnis = _lauf(pruefer, "--dateien", "189")
    assert ergebnis.returncode != 0, (
        "Eine veraltete Dateizahl in der Einrichtungsanleitung blieb "
        f"unbemerkt, obwohl das README richtig war.\n{ergebnis.stdout}")


def test_der_befund_nennt_die_datei(tmp_path):
    """Ohne den Dateinamen sucht der Mensch im README — und findet dort eine
    richtige Zahl."""
    pruefer = _mini_kit(tmp_path, _readme(189),
                        anleitung="`install.sh` legt die 136 Dateien ab.\n")
    ergebnis = _lauf(pruefer, "--dateien", "189")
    assert "einrichtung.md" in ergebnis.stderr, (
        f"Der Befund sagt nicht, WELCHE Datei falsch liegt.\n{ergebnis.stderr}")


def test_die_gegenrichtung_dieselbe_zahl_bleibt_gruen(tmp_path):
    """Ohne sie wäre ein Wächter, der immer rot ist, ein grüner Weg."""
    pruefer = _mini_kit(tmp_path, _readme(189),
                        anleitung="`install.sh` legt die 189 Dateien ab.\n")
    ergebnis = _lauf(pruefer, "--dateien", "189")
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}{ergebnis.stderr}"
    assert "einrichtung.md" in ergebnis.stdout, (
        "Die Erfolgszeile sagt nicht, dass sie die zweite Stelle mitgeprüft "
        f"hat — dann weiß niemand, wie weit die Zusicherung reicht.\n"
        f"{ergebnis.stdout}")


# --- (2) Was dort ausdrücklich NICHT geprüft wird ----------------------------


def test_eine_historische_testzahl_in_der_anleitung_bleibt_gruen(tmp_path):
    """Die Gegenprobe gegen den Fehlalarm, und sie ist der eigentliche
    Entwurfsentscheid.

    Der Belegstand in `einrichtung.md` nennt dated Testzahlen: »160 der 487
    Tests fielen«. Würde dort auch die Testzahl-Gattung geprüft, schlüge der
    Wächter an einer **richtigen** Stelle rot an — und wird dann abgeschaltet
    statt befolgt (`BL-14`).
    """
    pruefer = _mini_kit(
        tmp_path, _readme(189),
        anleitung=("`install.sh` legt die 189 Dateien ab.\n"
                   "Am 20.08.2026 fielen 160 der 487 Tests.\n"))
    # `--faelle 7` passt zum Mini-README: Der Fall soll an der ANLEITUNG
    # fallen oder gar nicht, nicht an einer Zahl, die er nicht prüfen will.
    ergebnis = _lauf(pruefer, "--dateien", "189", "--faelle", "7")
    assert ergebnis.returncode == 0, (
        "Eine historische Testzahl in der Anleitung wurde als Behauptung über "
        f"heute gelesen.\n{ergebnis.stdout}{ergebnis.stderr}")


def test_eine_fehlende_dateizahl_in_der_anleitung_ist_kein_befund(tmp_path):
    """Ob die Anleitung die Zahl überhaupt nennen will, ist ihre Entscheidung.
    Ein falscher WERT ist rot, eine fehlende Zusicherung nicht — dieselbe
    Trennung wie in `BL-198`."""
    pruefer = _mini_kit(tmp_path, _readme(189),
                        anleitung="Hier steht keine Zahl.\n")
    ergebnis = _lauf(pruefer, "--dateien", "189")
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}{ergebnis.stderr}"
    assert "einrichtung.md" not in ergebnis.stdout, (
        "Die Erfolgszeile führt die Anleitung als geprüft auf, obwohl dort "
        "keine Zahl stand — dieselbe Falschaussage wie in `BL-198`.")


def test_ohne_dateizahl_argument_wird_dort_nichts_geprueft(tmp_path):
    """Kein Sollwert, keine Behauptung. Der Prüfer rechnet die Dateizahl
    ausdrücklich NICHT selbst nach — sie entsteht erst bei einer echten
    Installation, und eine Zahl aus dem Repo wäre wieder eine Abschrift."""
    pruefer = _mini_kit(tmp_path, _readme(189),
                        anleitung="`install.sh` legt die 136 Dateien ab.\n")
    ergebnis = _lauf(pruefer)
    assert ergebnis.returncode == 0, (
        "Ohne gemessenen Sollwert wurde trotzdem eine Zahl beurteilt.\n"
        f"{ergebnis.stdout}{ergebnis.stderr}")


# --- (3) Die Zusicherung darf nicht lautlos verschwinden --------------------


def test_die_anleitung_nennt_die_dateizahl_ueberhaupt():
    """Sonst wäre der Wächter dort wirkungslos, ohne dass es auffällt — die
    Gattung, gegen die `BL-198` geschrieben ist."""
    if not ANLEITUNG.is_file():
        pytest.skip("doku/ liegt nur im Kit, nicht in der Installation")
    text = ANLEITUNG.read_text(encoding="utf-8")
    assert DATEIZAHL.search(text), (
        "`doku/einrichtung.md` nennt keine Dateizahl mehr. Entweder ist die "
        "Zusicherung absichtlich weg — dann gehört dieser Fall mit ihr weg —, "
        "oder sie ist beim Umformulieren verlorengegangen.")


def test_die_pruefliste_bleibt_eng_und_benannt():
    """Eine Ausnahmeliste, die wächst, ohne dass jemand hinsieht, ist eine
    Erlaubnis mit unbekanntem Umfang."""
    text = PRUEFER.read_text(encoding="utf-8")
    marke = re.search(r"^DATEIZAHL_MITGEPRUEFT = \((.*?)\)", text, re.M)
    assert marke, "DATEIZAHL_MITGEPRUEFT ist verschwunden."
    assert marke.group(1).count(",") <= 1, (
        "Die Liste ist gewachsen. Jede weitere Datei braucht ihren Grund im "
        "Kommentar darüber und eine Gegenprobe gegen Fehlalarme — sonst ist "
        "sie eine Erlaubnis mit unbekanntem Umfang.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

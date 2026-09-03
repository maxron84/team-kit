#!/usr/bin/env python3
"""BL-198 — der README-Wächter deckte die Testzahlen ab, aber nicht die zwei
Backlog-Zahlen daneben — und meldete trotzdem „alle Zahlen sind gemessen".

`geteilt/kit-readme-pruefen.py` prüft drei Gattungen richtig: Testfälle,
Testdateien, installierte Dateien. Zwei weitere Zahlen im selben README
behaupten dasselbe über dasselbe Kit und wurden von **niemandem** gemessen: die
Spanne `BL-1`…`BL-<N>` und die Zahl der Archiv-Einträge.

NICHT VERMUTET, SONDERN EINGETRETEN: Am 2026-08-26 kam `BL-196` dazu, das
README nannte weiter `BL-195`, und alle drei Doku-Wächter blieben grün.
Gefunden wurde es beim Eintragen von `BL-197` — von Hand, nicht vom Wächter.

DIE SCHÄRFERE HÄLFTE IST DIE SCHLUSSZEILE. `main()` hängt jede Zahlenprüfung an
ein `if a.<zahl> is not None`, druckte am Ende aber **unbedingt** „alle Zahlen
sind gemessen". Ohne Argumente — also bei jedem Aufruf von Hand — lief keine
einzige Zahlenprüfung, und die Erfolgszeile behauptete trotzdem, alle seien
gemessen. Das ist die Gattung von `BL-145`: Zwei Aufrufwege desselben Skripts
sichern verschieden viel zu, und beide melden dasselbe Grün.

UND DER TEIL, DER DIE DRIFT ERST SICHTBAR MACHT: `kit-test.ps1` prüft das
README wie `kit-test.sh`. Solange nur die bash-Bahn nachrechnet, hängt die
Aktualität dieser Zahlen an einem Lauf, den auf einer pwsh-Maschine niemand
fahren kann.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
PRUEFER = WURZEL / "geteilt" / "kit-readme-pruefen.py"
README = WURZEL / "README.md"

pytestmark = pytest.mark.skipif(
    not PRUEFER.is_file(),
    reason="kit-readme-pruefen.py liegt nur im Kit, nicht in der Installation")


def _lauf(readme=None, *argumente):
    befehl = [sys.executable, str(PRUEFER)]
    if readme:
        befehl += ["--readme", str(readme)]
    befehl += list(argumente)
    return subprocess.run(befehl, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _messwerte():
    """Die zwei Zahlen, wie der Prüfer sie selbst ableitet — hier NOCH EINMAL
    unabhängig gerechnet. Ein Test, der dieselbe Funktion fragt, prüft nur,
    dass sie sich selbst gleicht."""
    zeile = re.compile(r"(?m)^\| BL-(\d+) ")
    archiv_datei = WURZEL / "plans" / "backlog-archiv.md"
    backlog_datei = WURZEL / "plans" / "backlog.md"
    if not archiv_datei.is_file() or not backlog_datei.is_file():
        pytest.skip("der Backlog des Kits liegt hier nicht")
    archiv = zeile.findall(archiv_datei.read_text(encoding="utf-8"))
    offen = zeile.findall(backlog_datei.read_text(encoding="utf-8"))
    return len(archiv), max(int(n) for n in archiv + offen)


# --- (1) Die zwei Zahlen werden mitgemessen ----------------------------------


def test_die_beiden_backlog_zahlen_stimmen():
    """Der Normalfall, und zugleich der Beleg, dass das README aktuell ist."""
    ergebnis = _lauf()
    assert ergebnis.returncode == 0, (
        f"{ergebnis.stdout}\n{ergebnis.stderr}")
    archiv, hoechste = _messwerte()
    assert f"{archiv} Archiv-Einträge" in ergebnis.stdout
    assert f"BL-{hoechste}" in ergebnis.stdout


def test_eine_veraltete_bl_spanne_wird_rot(tmp_path):
    """Der Fall, an dem der Eintrag hängt: `BL-196` kam dazu, das README nannte
    weiter `BL-195`, und alles blieb grün."""
    archiv, hoechste = _messwerte()
    text = README.read_text(encoding="utf-8")
    gefaelscht = re.sub(r"`BL-1`(\s*(?:…|\.\.\.|bis)\s*)`BL-\d+`",
                        lambda m: f"`BL-1`{m.group(1)}`BL-{hoechste - 1}`",
                        text, count=1)
    assert gefaelscht != text, "im README steht keine BL-Spanne mehr"
    kopie = tmp_path / "README.md"
    kopie.write_text(gefaelscht, encoding="utf-8")
    ergebnis = _lauf(kopie)
    assert ergebnis.returncode != 0, (
        "Eine um eins zu niedrige BL-Spanne blieb unbemerkt — genau der Fall, "
        "der den Eintrag ausgelöst hat.")
    assert "BL-Nummer" in ergebnis.stderr


def test_eine_veraltete_archivzahl_wird_rot(tmp_path):
    archiv, _ = _messwerte()
    text = README.read_text(encoding="utf-8")
    gefaelscht = text.replace(f"({archiv} Einträge)", f"({archiv - 1} Einträge)")
    assert gefaelscht != text, "im README steht keine Archivzahl mehr"
    kopie = tmp_path / "README.md"
    kopie.write_text(gefaelscht, encoding="utf-8")
    ergebnis = _lauf(kopie)
    assert ergebnis.returncode != 0, (
        "Eine falsche Archivzahl blieb unbemerkt.")
    assert "Archiv-Einträge" in ergebnis.stderr


def test_die_gegenrichtung_das_unveraenderte_readme_bleibt_gruen(tmp_path):
    """Ohne sie wäre ein Wächter, der ALLES rot meldet, ein grüner Weg."""
    kopie = tmp_path / "README.md"
    kopie.write_text(README.read_text(encoding="utf-8"), encoding="utf-8")
    ergebnis = _lauf(kopie)
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}\n{ergebnis.stderr}"


def test_beide_gattungen_werden_einzeln_erkannt(tmp_path):
    """Die zwei Zahlen sind zwei Gattungen und kein Paar: Wer nur eine prüft
    und beide meldet, hat die zweite nur mitgetragen."""
    archiv, hoechste = _messwerte()
    text = README.read_text(encoding="utf-8")
    kopie = tmp_path / "README.md"
    # Nur die Archivzahl verfälschen — die Spanne bleibt richtig.
    kopie.write_text(text.replace(f"({archiv} Einträge)", "(1 Einträge)"),
                     encoding="utf-8")
    nur_archiv = _lauf(kopie)
    assert nur_archiv.returncode != 0
    assert "BL-Nummer" not in nur_archiv.stderr, (
        "Eine falsche Archivzahl darf die BL-Spanne nicht mitreißen — sonst "
        "sagt der Befund nicht, WAS nicht stimmt.")


# --- (2) Die Erfolgszeile sagt, was sie geprüft hat --------------------------


def test_ohne_zahlenargumente_wird_nichts_behauptet(tmp_path):
    """Der Kern des Eintrags. Vorher stand hier unbedingt „alle Zahlen sind
    gemessen" — auch bei einem Aufruf, bei dem KEINE Zahlenprüfung lief."""
    kopie = tmp_path / "README.md"
    kopie.write_text(README.read_text(encoding="utf-8"), encoding="utf-8")
    ergebnis = _lauf(kopie, "--ohne-backlog-zahlen")
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "alle Zahlen sind gemessen" not in ergebnis.stdout, (
        "Die Erfolgszeile behauptet weiter, alle Zahlen seien gemessen — bei "
        f"einem Aufruf, der keine einzige geprüft hat.\n{ergebnis.stdout}")
    assert "KEINE Zahl geprüft" in ergebnis.stdout, (
        "…und sie sagt auch nicht, dass sie nichts geprüft hat. Ein Aufrufweg, "
        f"der weniger zusichert, muss es sagen (BL-145).\n{ergebnis.stdout}")


def test_mit_argumenten_nennt_die_zeile_die_gattungen(tmp_path):
    kopie = tmp_path / "README.md"
    kopie.write_text(README.read_text(encoding="utf-8"), encoding="utf-8")
    ergebnis = _lauf(kopie, "--faelle", "1005", "--testdateien", "115")
    assert "Gemessen und deckungsgleich" in ergebnis.stdout or \
           ergebnis.returncode != 0
    if ergebnis.returncode == 0:
        assert "Testfälle" in ergebnis.stdout and "Testdateien" in ergebnis.stdout


# --- (3) Beide Selbsttests rechnen nach --------------------------------------


def test_beide_selbsttests_pruefen_das_readme():
    """Solange nur die bash-Bahn nachrechnet, hängt die Aktualität dieser
    Zahlen an einem Lauf, den auf einer pwsh-Maschine niemand fahren kann —
    der Rest von `BL-145`."""
    for pfad in (WURZEL / "bash" / "kit-test.sh",
                 WURZEL / "pwsh" / "kit-test.ps1"):
        if not pfad.is_file():
            pytest.skip("die Selbsttests liegen nur im Kit")
        text = pfad.read_text(encoding="utf-8")
        assert "kit-readme-pruefen" in text, (
            f"{pfad.name} prüft das README nicht — die Zahlen veralten dort "
            "lautlos (BL-198).")
        assert "Gegenprobe" in text or "gegenprobe" in text, (
            f"{pfad.name} fährt keine Gegenprobe. Ein Wächter, der nie rot "
            "wird, sichert nichts ab (BL-14).")


# --- (4) Wo die zwei Zahlen EINGEFORDERT werden dürfen -----------------------
#
# Im vollen Suite-Lauf zusammengestoßen: Der Leerfall („die Zahl steht
# überhaupt nicht mehr da") ist eine Aussage über das README DES KITS. Das
# Werkzeug wird aber ausdrücklich auch auf fremde Dateien gerichtet — beide
# Selbsttests fahren ihre Gegenproben an einer KOPIE, `test_bl180…` an einem
# Fixture aus zwei Zeilen. Dort ist eine fehlende Kit-Zahl der Normalfall.
#
# Ein Wächter, der an einer RICHTIGEN Datei rot schlägt, wird abgeschaltet
# statt befolgt — genau die Bauart, die `BL-180` abgestellt hat, und sie war
# hier ohne Absicht wiederhergestellt.


def _mini_kit(tmp_path, readme, hoechste=42, archiv=3):
    """Ein vollständiges Kit im Kleinen: Prüfer, Backlog, Archiv, README.

    Nur so lässt sich die Gegenrichtung überhaupt prüfen — der Prüfer leitet
    seine Sollwerte aus `KIT/plans/` ab, und `KIT` ist das Elternverzeichnis
    seines eigenen Ortes. Ein Test gegen das echte README könnte die Regel nur
    bestätigen, indem er das echte README verstümmelt.
    """
    (tmp_path / "geteilt").mkdir()
    (tmp_path / "plans").mkdir()
    ziel = tmp_path / "geteilt" / "kit-readme-pruefen.py"
    ziel.write_text(PRUEFER.read_text(encoding="utf-8"), encoding="utf-8",
                    newline="\n")
    kopf = "| Nr | Titel |\n|---|---|\n"
    (tmp_path / "plans" / "backlog-archiv.md").write_text(
        kopf + "".join(f"| BL-{n} | erledigt |\n" for n in range(1, archiv + 1)),
        encoding="utf-8", newline="\n")
    (tmp_path / "plans" / "backlog.md").write_text(
        kopf + f"| BL-{hoechste} | offen |\n", encoding="utf-8", newline="\n")
    (tmp_path / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    return ziel


def _mini_lauf(pruefer, *argumente):
    return subprocess.run([sys.executable, str(pruefer), *argumente],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def test_ein_fremdes_readme_ohne_die_zwei_zahlen_bleibt_gruen(tmp_path):
    """Der Fall, den beide Selbsttests und `test_bl180…` täglich fahren."""
    fremd = tmp_path / "fremd.md"
    fremd.write_text("Das Kit hat 100 Tests.\n", encoding="utf-8", newline="\n")
    ergebnis = _lauf(fremd, "--faelle", "100")
    assert ergebnis.returncode == 0, (
        "Eine fremde Datei wird angemahnt, weil sie die Backlog-Zahlen des "
        f"Kits nicht nennt — an einer richtigen Stelle rot (BL-180).\n"
        f"{ergebnis.stdout}{ergebnis.stderr}")


def test_und_die_schlusszeile_nennt_dann_keine_ungepruefte_zahl(tmp_path):
    """Die andere Hälfte: nicht behaupten, was nicht dastand."""
    fremd = tmp_path / "fremd.md"
    fremd.write_text("Das Kit hat 100 Tests.\n", encoding="utf-8", newline="\n")
    ergebnis = _lauf(fremd, "--faelle", "100")
    assert "Archiv-Einträge" not in ergebnis.stdout, (
        "Die Erfolgszeile führt die Archivzahl als »gemessen« auf, obwohl sie "
        f"in der Datei gar nicht vorkam (BL-198).\n{ergebnis.stdout}")
    assert "höchste Nummer" not in ergebnis.stdout


def test_am_readme_des_kits_bleibt_die_fehlende_zahl_rot(tmp_path):
    """Die Gegenrichtung, und ohne sie wäre die Lockerung oben ein Loch:
    Verschwindet die Zusicherung aus dem README DES KITS, muss es rot werden."""
    pruefer = _mini_kit(tmp_path, "Ein Kit mit 7 Tests.\n")
    ergebnis = _mini_lauf(pruefer, "--faelle", "7")
    assert ergebnis.returncode != 0, (
        "Ein README des Kits ohne BL-Spanne und ohne Archivzahl bleibt grün — "
        f"eine Zusicherung, die verschwindet, fällt nicht auf.\n"
        f"{ergebnis.stdout}")
    assert "BL-Nummer" in ergebnis.stderr and "Archiv" in ergebnis.stderr


def test_und_dasselbe_mini_kit_mit_beiden_zahlen_ist_gruen(tmp_path):
    """Sonst prüfte der Fall darüber nur, dass ein Mini-Kit immer rot ist.

    Seit `BL-224` verlangt das README DES KITS eine dritte selbst gemessene
    Zahl — die der offenen Einträge. Das Fixture steht hier für „ein
    vollständiges Kit-README"; es muss deshalb mitwachsen, wenn der Vertrag
    wächst. Der Fall darüber (fehlende Zahl bleibt rot) prüft die
    Gegenrichtung und bleibt unberührt.
    """
    pruefer = _mini_kit(
        tmp_path,
        "Ein Kit mit 7 Tests, `BL-1`…`BL-42`, 3 Archiv-Einträge, "
        "1 offene Einträge.\n")
    ergebnis = _mini_lauf(pruefer, "--faelle", "7")
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}{ergebnis.stderr}"
    assert "Gemessen und deckungsgleich" in ergebnis.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

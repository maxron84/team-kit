#!/usr/bin/env python3
"""BL-224 — zwei nachrechenbare Zahlen im README, die niemand nachrechnete.

Gefunden am 2026-09-03 beim Pflegen der Doku, von Hand und nicht vom Wächter:

  * »Offen sind 4 Einträge« — offen waren **fünf**.
  * »`Feld A`…`Feld D`« an **drei** Stellen (README, CHANGELOG-Kopf,
    Backlog-Kopf), obwohl es `Feld E` seit dem 2026-08-24 gibt.

Das ist die Bauform von `BL-198` ein zweites Mal: `kit-readme-pruefen.py`
deckte die Gattungen ab, die es kannte — Testfälle, Testdateien, installierte
Dateien, Archivzahl, BL-Spanne — und meldete darüber hinaus nichts. Beide
Zahlen hier sind aus dem Repo ableitbar und waren es bis dahin nicht.

WARUM DIE OFFEN-ZAHL NICHT DIE ZEILENZAHL IST. In `plans/backlog.md` stehen
auch abgetragene Zeilen, die noch nicht ins Archiv verschoben sind — am
Fundtag 13 von 18. Wer die Zeilen zählt, misst etwas anderes als das, was das
README behauptet. Gelesen wird deshalb das **Merkwort** am Anfang der
Statusspalte.

UND WARUM DAS MERKWORT UND NICHT DIE PROSA. Drei Zellen begannen mit »Befund 1
erledigt …, Befund 2 bleibt offen« bzw. »Teile (1) und (2) erledigt …«. Für
einen Leser ist das klar, für einen Zähler nicht: Ein `"offen" in zelle` zählt
jede Zelle mit, die das Wort irgendwo erwähnt. Solche Zellen werden deshalb
**namentlich als unentscheidbar gemeldet** statt geraten (`BL-160`).

DER FUND BEIM ERSTEN LAUF, der die Regel geschärft hat: Der Wächter schlug im
CHANGELOG an — in einer **abgeschlossenen Version**. Dort beschreibt der Satz
den Stand von damals; eine geschnittene Version ist eingefroren wie das
Archiv. Ein Wächter, der verlangt, Historie umzuschreiben, wird abgeschaltet
statt befolgt (`BL-14`). Mitgeprüft wird deshalb nur der **lebende** Teil:
Kopf und `[Unreleased]`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
PRUEFER = WURZEL / "geteilt" / "kit-readme-pruefen.py"
README = WURZEL / "README.md"
BACKLOG = WURZEL / "plans" / "backlog.md"

pytestmark = pytest.mark.skipif(
    not PRUEFER.is_file(),
    reason="kit-readme-pruefen.py liegt nur im Kit, nicht in der Installation")


def _lauf(pruefer, readme=None, *argumente):
    befehl = [sys.executable, str(pruefer)]
    if readme:
        befehl += ["--readme", str(readme)]
    return subprocess.run(befehl + list(argumente), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def _offen_von_hand():
    """Die Zahl NOCH EINMAL unabhängig gerechnet. Ein Test, der dieselbe
    Funktion fragt, prüft nur, dass sie sich selbst gleicht."""
    if not BACKLOG.is_file():
        pytest.skip("der Backlog des Kits liegt hier nicht")
    offen = 0
    for zeile in BACKLOG.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*BL-\d+\s*\|", zeile):
            continue
        zelle = zeile.rstrip().rstrip("|").rsplit("|", 1)[-1]
        wort = zelle.strip().lstrip("* ").split(" ")[0].strip("*.,;:—–-").lower()
        assert wort in ("offen", "teilweise", "erledigt", "abgetragen",
                        "verworfen", "zurückgestellt"), (
            f"»{zeile[:40]}…« beginnt mit »{wort}« — die Statusspalte muss mit "
            "einem Merkwort beginnen, sonst ist die Offen-Zahl geraten.")
        if wort in ("offen", "teilweise"):
            offen += 1
    return offen


def _mini_kit(tmp_path, readme, backlog_zeilen, changelog=None):
    """Ein Kit im Kleinen: Prüfer, Backlog, Archiv, README — und auf Wunsch
    ein CHANGELOG. Nur so ist die Gegenrichtung prüfbar: Der Prüfer leitet
    seine Sollwerte aus `KIT/plans/` ab, und `KIT` ist das Elternverzeichnis
    seines eigenen Ortes. Ein Test am echten Backlog könnte die Regel nur
    bestätigen, indem er ihn verstümmelt."""
    (tmp_path / "geteilt").mkdir()
    (tmp_path / "plans").mkdir()
    ziel = tmp_path / "geteilt" / "kit-readme-pruefen.py"
    ziel.write_text(PRUEFER.read_text(encoding="utf-8"), encoding="utf-8",
                    newline="\n")
    kopf = "| Nr | Was | Woher | Status |\n|---|---|---|---|\n"
    (tmp_path / "plans" / "backlog-archiv.md").write_text(
        kopf + "| BL-1 | x | y | **erledigt** |\n",
        encoding="utf-8", newline="\n")
    (tmp_path / "plans" / "backlog.md").write_text(
        kopf + "".join(backlog_zeilen), encoding="utf-8", newline="\n")
    (tmp_path / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    if changelog is not None:
        (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8",
                                               newline="\n")
    return ziel


def _zeile(nr, status):
    return f"| BL-{nr} | Was | Woher | {status} |\n"


# Ein Mini-README, das alle EINGEFORDERTEN Zusicherungen trägt, damit ein Fall
# nicht an einer Zahl scheitert, die er gar nicht prüfen will.
def _mini_readme(offen, hoechste, extra=""):
    """`hoechste` muss zur höchsten Nummer im Mini-Backlog passen. Sonst
    fiele der Fall an der BL-Spanne statt an dem, was er prüfen will — und ein
    Fall, der aus dem falschen Grund rot ist, sichert nichts ab."""
    return (f"Kit mit 7 Tests, `BL-1`…`BL-{hoechste}`, 1 Archiv-Einträge.\n"
            f"Offen sind {offen} Einträge.\n" + extra)


# --- (1) Der Normalfall am echten README ------------------------------------


def test_beide_neuen_gattungen_stehen_in_der_erfolgszeile():
    """Und zugleich der Beleg, dass das README des Kits aktuell ist."""
    ergebnis = _lauf(PRUEFER)
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}\n{ergebnis.stderr}"
    assert f"{_offen_von_hand()} offene Einträge" in ergebnis.stdout
    assert "Feld-Kürzel bis" in ergebnis.stdout


def test_die_neuen_gattungen_brauchen_kein_argument():
    """Das ist die Doppelbahn-Zusicherung dieses Eintrags (`BL-208`).

    `kit-test.ps1` und `kit-test.sh` rufen den Prüfer mit verschiedenen
    Argumenten auf. Solange die zwei Zahlen der Prüfer SELBST misst — wie die
    Archivzahl und die BL-Spanne seit `BL-198` —, erben beide Selbsttests die
    Prüfung, ohne dass eine Bahn nachgezogen werden muss. Ein Schalter hier
    wäre genau die Drift, die `BL-208` aufgedeckt hat.
    """
    ergebnis = _lauf(PRUEFER)
    assert ergebnis.returncode == 0
    assert "offene Einträge" in ergebnis.stdout
    assert "Feld-Kürzel" in ergebnis.stdout


# --- (2) Gegenproben: jede Gattung einzeln zurückgedreht ---------------------


def test_eine_veraltete_offen_zahl_wird_rot(tmp_path):
    """Der Fall, an dem der Eintrag hängt."""
    offen = _offen_von_hand()
    text = README.read_text(encoding="utf-8")
    gefaelscht = text.replace(f"Offen sind {offen} Einträge",
                              f"Offen sind {offen - 1} Einträge")
    assert gefaelscht != text, "im README steht keine Offen-Zahl mehr"
    kopie = tmp_path / "README.md"
    kopie.write_text(gefaelscht, encoding="utf-8")
    ergebnis = _lauf(PRUEFER, kopie)
    assert ergebnis.returncode != 0, (
        "Eine um eins zu niedrige Offen-Zahl blieb unbemerkt — genau der "
        "Fall, der den Eintrag ausgelöst hat.")
    assert "offene Backlog-Einträge" in ergebnis.stderr


def test_eine_zu_kurze_feld_spanne_wird_rot(tmp_path):
    text = README.read_text(encoding="utf-8")
    gefaelscht = re.sub(r"`Feld A`(\s*…\s*)`Feld [A-Z]`",
                        lambda m: f"`Feld A`{m.group(1)}`Feld B`", text)
    assert gefaelscht != text, "im README steht keine Feld-Spanne mehr"
    kopie = tmp_path / "README.md"
    kopie.write_text(gefaelscht, encoding="utf-8")
    ergebnis = _lauf(PRUEFER, kopie)
    assert ergebnis.returncode != 0, (
        "Eine Spanne, die vor dem höchsten Kürzel endet, blieb unbemerkt — "
        "sie schließt ein Feld aus dem Beleg aus.")
    assert "Spanne" in ergebnis.stderr


def test_ein_undefiniertes_feld_kuerzel_wird_rot(tmp_path):
    """Die andere Richtung derselben Gattung: ein Kürzel, das die
    Herkunftstabelle gar nicht kennt — ein Tippfehler oder ein Feld, dessen
    Zeile jemand zu schreiben vergessen hat."""
    kopie = tmp_path / "README.md"
    kopie.write_text(README.read_text(encoding="utf-8")
                     + "\nEin Beleg aus `Feld Z`.\n", encoding="utf-8")
    ergebnis = _lauf(PRUEFER, kopie)
    assert ergebnis.returncode != 0
    assert "`Feld Z`" in ergebnis.stderr


def test_die_gegenrichtung_das_unveraenderte_readme_bleibt_gruen(tmp_path):
    """Ohne sie wäre ein Wächter, der ALLES rot meldet, ein grüner Weg
    (`BL-14`)."""
    kopie = tmp_path / "README.md"
    kopie.write_text(README.read_text(encoding="utf-8"), encoding="utf-8")
    ergebnis = _lauf(PRUEFER, kopie)
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}\n{ergebnis.stderr}"


# --- (3) Die Zahl kommt aus der Statusspalte, nicht aus der Zeilenzahl -------


def test_abgetragene_zeilen_im_backlog_zaehlen_nicht_mit(tmp_path):
    """Der Kern der Messung. Am Fundtag standen 18 Zeilen im Backlog, von
    denen 13 »erledigt« waren — wer Zeilen zählt, nennt 18 und meint 5."""
    pruefer = _mini_kit(tmp_path, _mini_readme(1, 9), [
        _zeile(7, "**offen.** Noch zu tun."),
        _zeile(8, "**erledigt 2026-09-03 — alles gebaut.**"),
        _zeile(9, "**erledigt 2026-09-03.** Hier steht das Wort offen in der "
                  "Prosa, und es darf nicht mitzählen."),
    ])
    ergebnis = _lauf(pruefer)
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}{ergebnis.stderr}"
    assert "1 offene Einträge" in ergebnis.stdout, (
        "Gezählt wurde nicht die Statusspalte — entweder die Zeilen oder ein "
        f"»offen« aus der Prosa.\n{ergebnis.stdout}")


def test_teilweise_zaehlt_als_offen(tmp_path):
    """`BL-206` ist der Anlass: Befund 1 erledigt, Befund 2 offen. An dem
    Eintrag hängt noch Arbeit, also ist er offen."""
    pruefer = _mini_kit(tmp_path, _mini_readme(2, 9), [
        _zeile(7, "**offen.**"),
        _zeile(8, "**teilweise** — Befund 1 erledigt, Befund 2 bleibt offen."),
        _zeile(9, "**erledigt 2026-09-03.**"),
    ])
    ergebnis = _lauf(pruefer)
    assert ergebnis.returncode == 0, f"{ergebnis.stdout}{ergebnis.stderr}"
    assert "2 offene Einträge" in ergebnis.stdout


# --- (4) Unentscheidbar wird gemeldet, nicht geraten -------------------------


def test_eine_zelle_ohne_merkwort_wird_namentlich_gemeldet(tmp_path):
    pruefer = _mini_kit(tmp_path, _mini_readme(1, 8), [
        _zeile(7, "**offen.**"),
        _zeile(8, "**Befund 1 erledigt, Befund 2 bleibt offen.**"),
    ])
    ergebnis = _lauf(pruefer)
    assert ergebnis.returncode != 0, (
        "Eine Zelle, die mit keinem Merkwort beginnt, wurde stillschweigend "
        f"eingeordnet — dann ist die Zahl geraten.\n{ergebnis.stdout}")
    assert "BL-8" in ergebnis.stderr, (
        "Der Befund nennt den Eintrag nicht beim Namen — dann weiß niemand, "
        f"welche Zelle gemeint ist (`BL-160`).\n{ergebnis.stderr}")


def test_bei_unentscheidbarer_zelle_wird_keine_zahl_behauptet(tmp_path):
    """Die schärfere Hälfte, dieselbe wie in `BL-198`: nicht behaupten, was
    nicht gemessen wurde. Eine Summe mit Löchern ist keine Messung."""
    pruefer = _mini_kit(tmp_path, _mini_readme(1, 8), [
        _zeile(7, "**offen.**"),
        _zeile(8, "**Befund 1 erledigt, Befund 2 bleibt offen.**"),
    ])
    ergebnis = _lauf(pruefer)
    assert "offene Einträge" not in ergebnis.stdout, (
        "Die Erfolgszeile führt die Offen-Zahl als »gemessen« auf, obwohl eine "
        f"Zelle nicht einzuordnen war.\n{ergebnis.stdout}")


# --- (5) Wo die Zahl eingefordert werden darf (die BL-180-Lockerung) --------


def test_ein_fremdes_readme_ohne_die_offen_zahl_bleibt_gruen(tmp_path):
    """Beide Selbsttests fahren ihre Gegenproben an einer KOPIE, `BL-180` an
    einem Fixture aus zwei Zeilen. Dort ist eine fehlende Kit-Zahl der
    Normalfall — und ein Wächter, der an einer richtigen Datei rot schlägt,
    wird abgeschaltet statt befolgt."""
    fremd = tmp_path / "fremd.md"
    fremd.write_text("Das Kit hat 100 Tests.\n", encoding="utf-8", newline="\n")
    ergebnis = _lauf(PRUEFER, fremd, "--faelle", "100")
    assert ergebnis.returncode == 0, (
        f"{ergebnis.stdout}{ergebnis.stderr}")
    assert "offene Einträge" not in ergebnis.stdout, (
        "Die Erfolgszeile führt eine Zahl auf, die in der Datei nicht vorkam.")


def test_am_readme_des_kits_bleibt_die_fehlende_offen_zahl_rot(tmp_path):
    """Die Gegenrichtung, und ohne sie wäre die Lockerung darüber ein Loch:
    Verschwindet die Zusicherung aus dem README DES KITS, muss es rot werden."""
    pruefer = _mini_kit(
        tmp_path,
        "Kit mit 7 Tests, `BL-1`…`BL-7`, 1 Archiv-Einträge.\n",
        [_zeile(7, "**offen.**")])
    ergebnis = _lauf(pruefer, None, "--faelle", "7")
    assert ergebnis.returncode != 0, (
        "Ein README des Kits ohne Offen-Zahl bleibt grün — eine Zusicherung, "
        f"die verschwindet, fällt nicht auf.\n{ergebnis.stdout}")
    assert "offene Backlog-Einträge" in ergebnis.stderr


# --- (6) Die mitgeprüften Dateien — und wo die Prüfung endet ----------------


def test_der_lebende_teil_des_changelogs_wird_mitgeprueft(tmp_path):
    """Dieselbe Zeile steht in README, CHANGELOG und Backlog-Kopf. Genau das
    ist die Abschrift, die gemeinsam veraltet — am 2026-09-03 an allen drei
    Stellen gleichzeitig."""
    pruefer = _mini_kit(
        tmp_path,
        _mini_readme(1, 7, "| **`Feld A`** | x |\n| **`Feld B`** | y |\n"),
        [_zeile(7, "**offen.**")],
        changelog="# Changelog\n\nKürzel `Feld A`…`Feld A`.\n\n"
                  "## [Unreleased]\n\nNoch nichts.\n")
    ergebnis = _lauf(pruefer)
    assert ergebnis.returncode != 0, (
        "Eine veraltete Spanne im CHANGELOG-Kopf blieb unbemerkt.")
    assert "CHANGELOG.md" in ergebnis.stderr


def test_eine_geschnittene_version_wird_nicht_mitgeprueft(tmp_path):
    """Die Gegenrichtung, und sie ist der eigentliche Entwurfsentscheid.

    Beim ersten Lauf schlug der Wächter in einer ABGESCHLOSSENEN Version an —
    berechtigt gelesen und trotzdem falsch: Dort beschreibt der Satz den Stand
    von damals. Eine geschnittene Version ist eingefroren wie das Archiv. Ein
    Wächter, der verlangt, Historie umzuschreiben, wird abgeschaltet statt
    befolgt (`BL-14`).
    """
    pruefer = _mini_kit(
        tmp_path,
        _mini_readme(1, 7, "| **`Feld A`** | x |\n| **`Feld B`** | y |\n"),
        [_zeile(7, "**offen.**")],
        changelog="# Changelog\n\nKürzel `Feld A`…`Feld B`.\n\n"
                  "## [Unreleased]\n\nNoch nichts.\n\n"
                  "## [2.13.1] — 2026-08-25\n\nDamals: `Feld A`…`Feld A`.\n")
    ergebnis = _lauf(pruefer)
    assert ergebnis.returncode == 0, (
        "Der Wächter verlangt, eine geschnittene Version umzuschreiben.\n"
        f"{ergebnis.stdout}{ergebnis.stderr}")


def test_auch_ein_rueckblick_im_lebenden_teil_zaehlt_als_behauptung(tmp_path):
    """Der bewusst getragene Preis, beim ersten Lauf am eigenen Text
    eingetreten: Der CHANGELOG-Eintrag zu `BL-224` beschrieb die alte, falsche
    Spanne — in der Spannenform — und machte den Wächter rot.

    Die Auflösung ist NICHT, den Wächter aufzuweichen. Er müsste dann erraten,
    ob eine Spanne den heutigen Vorrat behauptet oder einen vergangenen
    beschreibt, und ein Wächter, der rät, ist keiner. Wer zurückblickt,
    schreibt es aus (»endete bei `Feld D`«). Dieser Fall hält die Entscheidung
    fest, damit sie beim nächsten Rotwerden nicht neu verhandelt wird.
    """
    pruefer = _mini_kit(
        tmp_path,
        _mini_readme(1, 7, "| **`Feld A`** | x |\n| **`Feld B`** | y |\n"),
        [_zeile(7, "**offen.**")],
        changelog="# Changelog\n\n## [Unreleased]\n\n"
                  "Frueher stand hier `Feld A`…`Feld A`, das war falsch.\n")
    ergebnis = _lauf(pruefer)
    assert ergebnis.returncode != 0, (
        "Eine Spanne im lebenden Teil blieb unbemerkt, weil sie wie ein "
        "Rückblick klingt — dann hängt der Wächter an einer Wortwahl.")
    assert "RUECKBLICK" in ergebnis.stderr, (
        "Der Befund nennt den Ausweg nicht. Wer hier rot wird, hat meist "
        f"wirklich zurückgeblickt und muss wissen, wie es geht.\n{ergebnis.stderr}")


def test_das_archiv_wird_gar_nicht_geprueft():
    """Dieselbe Erwägung eine Datei weiter: Im Backlog-Archiv ist eine alte
    Spanne die Historie eines abgetragenen Eintrags."""
    text = PRUEFER.read_text(encoding="utf-8")
    marke = re.search(r"^MITGEPRUEFT = \((.*?)\)", text, re.M)
    assert marke, "MITGEPRUEFT ist verschwunden — was wird noch geprüft?"
    assert "backlog-archiv" not in marke.group(1), (
        "Das Archiv steht in der Prüfliste. Eine alte Spanne ist dort richtig, "
        "und ein Wächter, der an einer richtigen Stelle rot schlägt, wird "
        "abgeschaltet statt befolgt (`BL-14`).")


# --- (7) Die Konvention steht dort, wo sie befolgt werden muss --------------


def test_der_backlog_nennt_die_konvention_selbst():
    """Eine Formvorschrift, die nur im Prüfer steht, findet erst, wer rot
    geworden ist. Sie gehört in die Datei, die sie einhalten muss."""
    if not BACKLOG.is_file():
        pytest.skip("der Backlog des Kits liegt hier nicht")
    text = BACKLOG.read_text(encoding="utf-8")
    for wort in ("Merkwort", "offen", "teilweise", "erledigt"):
        assert wort in text, (
            f"Der Backlog-Kopf nennt »{wort}« nicht — die Konvention, an der "
            "die Offen-Zahl hängt, steht dann nur im Prüfer.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

#!/usr/bin/env python3
"""BL-184: `zitat_lint.py` übersah die natürlichste deutsche
Vorbedingungs-Bauform — also genau den Fall, als dessen Gegenprobe es gedacht
ist.

DER FUND
    Die Zeile

        **Vorbedingung für den ersten Bump:** `BL-6` muss vorher erledigt sein

    in einem Abschluss-Protokoll wurde nach dem Abtragen von `BL-6` **nicht**
    gemeldet: Exit 0, gezielt auf die Datei angesetzt, nachgemessen statt
    vermutet. Das Werkzeug ist die maschinelle Gegenprobe zu einer Pflichtzeile,
    die das Kit selbst verlangt — und es schwieg ausgerechnet bei dem Zitierer,
    der beim Vorbereiten der Auslieferung gelesen wird. **Wo es schweigt,
    entsteht der Eindruck, es sei geprüft worden.**

    In derselben Sitzung schlug es fünfmal an, wo nichts war.

DIE WURZEL IST DIESELBE FÜR BEIDE FEHLERRICHTUNGEN
    Das Werkzeug beurteilte **Absätze nach Stichwörtern** statt **Sätze nach
    Bezug**. Ein Zukunftswort irgendwo im Absatz ließ jede Nummer darin als
    offenes Zitat gelten; und der echte Fall stand allein in seinem Satz, ohne
    ein Wort aus der schmalen Liste.

WAS AUSDRÜCKLICH NICHT GETAN WURDE
    Die Wortliste aufblähen. Das war laut Werkzeugkopf schon einmal die
    falsche Antwort: Das bloße Wort „offen" brachte drei Fehltreffer im
    eigenen Roadmap-Dokument des Kits. Die Vorbedingungs-Wendungen stehen
    deshalb als **eigenes, engeres Muster** daneben — sie benennen eine
    Abhängigkeit und kommen in Rückblicken kaum vor.

GEMESSEN AM EIGENEN KORPUS DES KITS
    Absatzweise meldete der Lint über die Statusfelder von `plans/backlog.md`
    **29** Zeilen — reines Rauschen, weshalb der Backlog überhaupt ausgenommen
    war. Satzweise und feldweise sind es **0**, und der Feldfall wird gefangen.
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import kit_pfad  # noqa: E402

WERKZEUG = kit_pfad("tools", "zitat_lint.py")

pytestmark = pytest.mark.skipif(
    not WERKZEUG.is_file(), reason="zitat_lint.py liegt in dieser Ablage nicht")

BACKLOG = ("| Nr | Was | Woher | Status |\n"
           "|---|---|---|---|\n"
           "| BL-6 | Die Version steht an drei Orten | Architekt | "
           "**erledigt (Stufe 5).** Ein Test haelt sie zusammen |\n"
           "| BL-9 | Noch nicht angefasst | Architekt | **offen** |\n")


def _lauf(tmp_path, *dateien, backlog=BACKLOG):
    (tmp_path / "backlog.md").write_text(backlog, encoding="utf-8", newline="\n")
    return subprocess.run(
        [sys.executable, str(WERKZEUG),
         "--backlog", str(tmp_path / "backlog.md"),
         "--archiv", str(tmp_path / "kein-archiv.md"), *map(str, dateien)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})


def _datei(tmp_path, text, name="protokoll.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


# --- Die Bauform, die gefehlt hat --------------------------------------------


@pytest.mark.parametrize("zeile", [
    "**Vorbedingung für den ersten Bump:** `BL-6` muss vorher erledigt sein.",
    "Der Bump setzt `BL-6` voraus.",
    "Solange `BL-6` nicht abgetragen ist, bleibt der Bump liegen.",
    "Die Auslieferung muss warten, bis `BL-6` erledigt ist — Vorbedingung.",
])
def test_die_vorbedingungs_bauform_wird_gemeldet(tmp_path, zeile):
    """Der Fund selbst, in seinen vier natürlichen Schreibweisen."""
    p = _datei(tmp_path, "# Abschluss\n\n" + zeile + "\n")
    r = _lauf(tmp_path, p)
    assert r.returncode == 3, (
        f"BL-184: {zeile!r} geht durch — das Werkzeug schweigt bei dem Fall, "
        f"für den es gebaut wurde.\n{r.stdout}{r.stderr}")
    assert "BL-6" in r.stderr


def test_ein_rueckblick_in_derselben_bauform_ist_kein_befund(tmp_path):
    """Die Gegenrichtung — ohne sie wäre das Muster nur breiter, nicht besser.

    Ein Lint mit Fehlalarmen wird abgeschaltet statt befolgt (`BL-14`), und
    genau daran ist die erste Fassung der Wortliste schon einmal gescheitert.
    """
    p = _datei(tmp_path, "# Abschluss\n\nDie Vorbedingung war `BL-6`, und sie "
                         "ist mit Stufe 5 erfüllt.\n")
    r = _lauf(tmp_path, p)
    assert r.returncode == 0, (
        f"Ein ausdrücklicher Rückblick wird als offenes Zitat gemeldet:\n"
        f"{r.stdout}{r.stderr}")


# --- Bezug statt Absatz ------------------------------------------------------


def test_ein_zukunftswort_im_nachbarsatz_zaehlt_nicht_mehr(tmp_path):
    """Der ergiebigste Einzelschritt gegen die Fehltreffer.

    Absatzweise gelesen färbt das „wartet auf" im ersten Satz den zweiten mit
    ein — und `BL-6` gilt als offen zitiert, obwohl der Satz das Gegenteil
    sagt. Im meldenden Projekt sind so fünf Fehltreffer in einer Sitzung
    entstanden.
    """
    p = _datei(tmp_path,
               "# Abschluss\n\n"
               "Die Auslieferung wartet auf `BL-9`. "
               "`BL-6` ist mit Stufe 5 abgetragen.\n")
    r = _lauf(tmp_path, p)
    assert r.returncode == 0, (
        f"Der Nachbarsatz färbt noch ab:\n{r.stdout}{r.stderr}")


def test_im_selben_satz_zaehlt_es_sehr_wohl(tmp_path):
    """Ohne diesen Fall wäre der Test darüber auch grün, wenn der Lint gar
    nichts mehr fände."""
    p = _datei(tmp_path, "# Abschluss\n\nDie Auslieferung wartet auf `BL-6`.\n")
    r = _lauf(tmp_path, p)
    assert r.returncode == 3, f"{r.stdout}{r.stderr}"


@pytest.mark.parametrize("satz", [
    "Der Bump wartet auf `BL-6` — z. B. wegen der Metadaten.",
    "Der Bump wartet auf `BL-6`, d. h. er kann noch nicht raus.",
])
def test_eine_abkuerzung_zerschneidet_den_satz_nicht(tmp_path, satz):
    """Ein zu früh abgeschnittener Satz verliert genau den Treffer, den dieser
    Eintrag einklagt. `z. B.` und `d. h.` sind in dieser Doku alltäglich."""
    p = _datei(tmp_path, "# Abschluss\n\n" + satz + "\n")
    r = _lauf(tmp_path, p)
    assert r.returncode == 3, (
        f"Die Abkürzung hat den Satz zerschnitten:\n{r.stdout}{r.stderr}")


# --- Der Backlog prüft seine eigenen Statusfelder ----------------------------


def test_ein_statusfeld_das_einen_erledigten_punkt_als_offen_fuehrt(tmp_path):
    """Ein Statusfeld, das einen Auslöser nennt, ist maschinell dieselbe
    Aussage wie ein Plan-Zitat — und veraltet genauso still."""
    backlog = BACKLOG + ("| BL-11 | Etwas anderes | Architekt | **offen.** "
                         "Wartet auf `BL-6` |\n")
    r = _lauf(tmp_path, backlog=backlog)
    assert r.returncode == 3, (
        f"Das Statusfeld wird nicht geprüft:\n{r.stdout}{r.stderr}")
    assert "Statusfeld" in r.stderr, r.stderr


def test_eine_zeile_zitiert_sich_nicht_selbst(tmp_path):
    """Sonst meldete jeder erledigte Eintrag sich selbst — der Lint wäre ab
    dem ersten Abtragen dauerhaft rot."""
    backlog = ("| Nr | Was | Woher | Status |\n|---|---|---|---|\n"
               "| BL-6 | Etwas | Architekt | **erledigt.** `BL-6` wartet auf "
               "nichts mehr |\n")
    r = _lauf(tmp_path, backlog=backlog)
    assert r.returncode == 0, (
        f"Die Zeile meldet ihre eigene Nummer:\n{r.stdout}{r.stderr}")


def test_der_backlog_des_kits_bleibt_ruhig():
    """Die Messung, die den Umbau rechtfertigt.

    Absatzweise gelesen meldete der Lint über die Statusfelder von
    `plans/backlog.md` **29** Zeilen — reines Rauschen, und der Grund, warum
    der Backlog überhaupt vom Lint ausgenommen war. Feldweise und satzweise
    muss er still sein, sonst ist mit dem Rauschen auch die Zusicherung weg.
    """
    wurzel = Path(__file__).resolve().parents[2]
    backlog = wurzel / "plans" / "backlog.md"
    # Der Uebersprung muss am KIT haengen, nicht am Dateinamen. In einer
    # INSTALLIERTEN Ablage liegt an derselben Stelle der Backlog des
    # PROJEKTS — eine frische Vorlage ohne eine einzige BL-Zeile. Der Lint
    # meldet darueber folgerichtig einen Fehler, und dieser Fall wurde dann
    # ROT statt uebersprungen: Er prueft eine Zusicherung ueber den Backlog
    # des Kits an einer Datei, die gar nicht dessen Backlog ist.
    #
    # Gefunden hat das der erste vollstaendige Lauf von kit-test.ps1 nach
    # BL-145 — er starb an dieser einen Zeile, und zwar in Schritt 4, nach
    # 19 Minuten Suite.
    if not backlog.is_file() or not (wurzel / "bootstrap").is_dir():
        pytest.skip("kein Kit-Backlog in dieser Ablage (nur im Kit)")
    r = subprocess.run(
        [sys.executable, str(WERKZEUG)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(wurzel),
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    assert r.returncode == 0, (
        "Der Lint schlägt über dem eigenen Backlog des Kits an. Entweder ist "
        "ein Zitat wirklich veraltet — dann gehört es richtiggestellt — oder "
        f"der Schnitt ist zu grob geraten:\n{r.stdout}{r.stderr}")


def test_die_ausgabe_erinnert_an_die_reihenfolge(tmp_path):
    """Der Fund ist so entstanden: erster Lauf Exit 0, und das sah aus wie
    „geprüft". Vor dem Abtragen steht der Eintrag noch als offen im Backlog,
    und der Lint meldet folgerichtig nichts."""
    p = _datei(tmp_path, "# Abschluss\n\nNichts Besonderes.\n")
    r = _lauf(tmp_path, p)
    assert r.returncode == 0
    assert "Abtragen zuerst" in r.stdout, (
        f"Der grüne Lauf sagt nicht, wann er überhaupt etwas aussagt:\n{r.stdout}")

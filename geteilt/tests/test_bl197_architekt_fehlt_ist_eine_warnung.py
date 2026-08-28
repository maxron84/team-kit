#!/usr/bin/env python3
"""Regressionstest fuer BL-197, Teil (1): Eine nummerierte Kaskade mit
ralph-Zeile und ohne architekt-Zeile ist eine WARNUNG, keine Notiz am Rand.

WARUM DIE SCHWERE HIER NICHT KOSMETIK IST. Der Kontostand (`--budget`) zeigt
auf BEIDEN Bahnen ausschliesslich `[WARNUNG]`-Zeilen -- `bash/entry/team-
status.sh` filtert auf `*WARNUNG*`, `pwsh/entry/team-status.ps1` auf dasselbe
Muster. Ein `[Hinweis]` erscheint dort also NIE. Die Einstufung entscheidet
damit nicht zwischen zwei Etiketten, sondern zwischen *unsichtbar* und
*sichtbar*.

DER FELDBELEG (Feld E, 2026-08-26, gemessen statt geschaetzt): Zwei regulaere,
produktive Sitzungen EINES Tages -- 36,22 USD und 7,68 USD, zusammen 43,90 USD
Abo-Gegenwert -- standen nie im Ledger. Gerettet wurden sie durch einen Zufall:
Die Transkripte lagen noch da. Der Regelfall ist ein anderer.

DAS ARGUMENT FUER DIE HOCHSTUFUNG ist woertlich dasselbe, das `ralph-fehlt`
schon traegt: dort *"gebaut wurde immer, wenn gesweept wurde"*, hier
*"geplant wurde immer, wenn gebaut wurde"* -- ohne Aushaertung gaebe es nichts
zu bauen.

DIE FALLE GEHOERT VON ANFANG AN MITGEBAUT, und sie ist der Grund fuer die
Buendelung: Ein unter einer aelteren Kit-Fassung gewachsenes Ledger, in dem
der Architekt nie gebucht hat, wuerde sonst auf einen Schlag N Warnungen
erzeugen -- dauerhaft unaufloesbar, weil die Transkripte laengst weg sind. Das
ist der Fehlermodus aus BL-14 selbst: Eine Warnung, die immer erscheint, ist
keine.

Netz-/CLI-frei gegen temporaere Fixtures -- nie das echte Ledger.
"""
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

KOSTEN_PY = kit_pfad("tools", "kosten.py")

KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"


def _run(*args):
    ergebnis = subprocess.run(
        [sys.executable, str(KOSTEN_PY), "ledger-pruefen", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return ergebnis.returncode, ergebnis.stdout.strip()


def _ledger(tmp_path, *zeilen):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(KOPF + "".join(z + "\n" for z in zeilen), encoding="utf-8")
    return pfad


def _zeile(kaskade, usd, rolle):
    return (f"2026-08-01 | {kaskade} | {usd:.4f} | abo | produkt | "
            f"{rolle} | Testzeile")


def _leere_logs(tmp_path):
    """Zwei Log-Ordner OHNE archiv/ -- so bleiben P1b und P3 stumm und der
    Test sieht genau die Pruefung, die er meint."""
    for name in (".ralph-logs", ".team-logs"):
        (tmp_path / name).mkdir()
    return ["--ralph-logs", str(tmp_path / ".ralph-logs"),
            "--team-logs", str(tmp_path / ".team-logs")]


def _einzige_warnung(out):
    """Die eine Warnung holen -- mit lesbarer Zusicherung statt StopIteration.

    Ein `next(...)` ueber einen leeren Generator stirbt als RuntimeError, und
    eine Gegenprobe, deren Fehlermeldung den Befund nicht nennt, kostet beim
    Zurueckdrehen genau die Minuten, die sie sparen soll.
    """
    warnungen = [z for z in out.splitlines() if z.startswith("[WARNUNG]")]
    assert len(warnungen) == 1, (
        f"erwartet genau EINE [WARNUNG]-Zeile, bekam {len(warnungen)}:\n{out}")
    return warnungen[0]


def _voll(kaskade):
    """Eine rundum gebuchte Kaskade: alle drei Quellen."""
    return (_zeile(kaskade, 2.1621, "ralph"),
            _zeile(kaskade, 1.0969, "roles"),
            _zeile(kaskade, 6.1614, "architekt"))


def _ohne_architekt(kaskade):
    return (_zeile(kaskade, 2.1621, "ralph"),
            _zeile(kaskade, 1.0969, "roles"))


# --- Die vier Gegenproben, die der Eintrag woertlich verlangt ----------------
#
# Sie stehen hier einzeln und nicht als ein Fall ueber alles: Der Eintrag
# verlangt sie "jeder einzeln zurueckgedreht", und ein Sammelfall bliebe gruen,
# wenn eine der vier Haelften aufhoerte zu arbeiten.

def test_eine_von_sieben_kaskaden_erzeugt_GENAU_EINE_warnung(tmp_path):
    """Gegenprobe 1: Kaskaden 1-7, nur 7 fehlt die architekt-Zeile.

    Erwartet: GENAU EINE Warnung, und sie nennt die 7 namentlich. Eine
    Warnung, die die betroffene Kaskade nicht nennt, zwingt zum Nachzaehlen
    von Hand -- also zu genau der Arbeit, die das Werkzeug abnehmen soll.
    """
    zeilen = []
    for k in range(1, 7):
        zeilen.extend(_voll(str(k)))
    zeilen.extend(_ohne_architekt("7"))
    pfad = _ledger(tmp_path, *zeilen)

    rc, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    warnungen = [z for z in out.splitlines() if z.startswith("[WARNUNG]")]
    assert rc == 4, out
    assert len(warnungen) == 1, f"erwartet 1 Warnung, bekam {len(warnungen)}:\n{out}"
    assert "1 nummerierte Kaskade(n)" in warnungen[0], warnungen[0]
    assert ": 7." in warnungen[0], (
        f"die betroffene Kaskade muss NAMENTLICH dastehen: {warnungen[0]}")


def test_vollstaendig_gebuchtes_ledger_SCHWEIGT(tmp_path):
    """Gegenprobe 2 -- die Gegenrichtung, ohne die der Fix wertlos waere.

    Ein Waechter, der immer anschlaegt, ist keine Meldung (BL-14). Wird diese
    Richtung nicht mitgefahren, wird ein Fix der Gattung gruen, indem er
    schlicht IMMER warnt.
    """
    zeilen = []
    for k in range(1, 8):
        zeilen.extend(_voll(str(k)))
    pfad = _ledger(tmp_path, *zeilen)

    rc, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    assert rc == 0, out
    assert "[WARNUNG]" not in out, out
    assert "keine Befunde" in out, out


def test_benannte_kaskade_bleibt_hinweis(tmp_path):
    """Gegenprobe 3: `post-7` mit ralph und ohne architekt bleibt Hinweis.

    Benannte Kaskaden sind per Konvention Out-of-Loop-Fixserien NACH dem Lauf
    -- dort gab es keine Aushaertung, das Fehlen ist korrekt. Dieselbe
    Unterscheidung und derselbe Grund wie in BL-14 fuer `ralph-fehlt`.
    """
    pfad = _ledger(tmp_path, *_ohne_architekt("post-7"))

    rc, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    assert rc == 0, out
    assert "[WARNUNG]" not in out, out
    assert "keine architekt-Zeile" in out, out


def test_sechs_von_sieben_erzeugen_EINE_warnung_nicht_sechs(tmp_path):
    """Gegenprobe 4 -- das gewachsene Feld-Ledger, und der eigentliche Grund
    fuer die Buendelung.

    Ein Ledger aus der Zeit vor BL-165, in dem der Architekt nie gebucht hat,
    darf nicht auf einen Schlag N dauerhaft unaufloesbare Warnungen erzeugen.
    Sechs Zeilen `[WARNUNG]` untereinander erzieht zum Wegsehen -- und der
    Kontostand druckt sie ungefiltert alle.
    """
    zeilen = []
    for k in range(1, 7):
        zeilen.extend(_ohne_architekt(str(k)))
    zeilen.extend(_voll("7"))
    pfad = _ledger(tmp_path, *zeilen)

    rc, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    warnungen = [z for z in out.splitlines() if z.startswith("[WARNUNG]")]
    assert rc == 4, out
    assert len(warnungen) == 1, (
        f"sechs betroffene Kaskaden muessen EINE Warnung ergeben, nicht "
        f"{len(warnungen)}:\n{out}")
    assert "6 nummerierte Kaskade(n)" in warnungen[0], warnungen[0]
    for k in range(1, 7):
        assert str(k) in warnungen[0], (
            f"Kaskade {k} fehlt in der Sammelwarnung: {warnungen[0]}")


# --- Die Abgrenzungen, die der Fix nicht mitreissen darf ---------------------

def test_kaskade_ohne_ralph_zeile_geht_nicht_in_die_warnung(tmp_path):
    """Nur eine architekt-Zeile heisst: geplant, aber nie gelaufen.

    Dafuer fehlt nichts. Ohne diese Grenze meldete das Werkzeug jede frisch
    geplante Kaskade -- wieder BL-14.
    """
    pfad = _ledger(tmp_path, _zeile("2", 6.1614, "architekt"))

    rc, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    assert rc == 0, out
    assert "keine Befunde" in out, out


def test_fehlende_roles_zeile_bleibt_hinweis(tmp_path):
    """Der Nachbarbefund darf nicht mit hochgestuft werden: Ein Lauf ohne Red
    Team ist moeglich, das Fehlen der roles-Zeile bleibt ein Hinweis."""
    pfad = _ledger(tmp_path,
                    _zeile("1", 2.1621, "ralph"),
                    _zeile("1", 6.1614, "architekt"))

    rc, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    assert rc == 0, out
    assert "[WARNUNG]" not in out, out
    assert "keine roles-Zeile" in out, out


def test_die_warnung_nennt_den_nachtrage_befehl(tmp_path):
    """Eine Warnung ohne Ausweg ist eine Beschwerde.

    Der Betrag muss erst GEMESSEN werden, also sind es zwei Befehle -- und
    genau das muss dastehen, sonst sucht der Leser den ersten selbst.
    """
    pfad = _ledger(tmp_path, *_ohne_architekt("3"))

    _, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    warnung = _einzige_warnung(out)
    assert "sitzung-messen" in warnung, warnung
    assert "--architekt-abschluss" in warnung, warnung
    assert "--kaskade" in warnung, warnung


def test_kaskaden_stehen_numerisch_sortiert_in_der_warnung(tmp_path):
    """10 darf nicht vor 2 stehen. Eine Aufzaehlung, die man nicht der Reihe
    nach lesen kann, wird nicht gelesen (dieselbe Zusicherung wie fuer die
    Befundliste selbst in BL-13)."""
    zeilen = []
    for k in ("2", "10", "3"):
        zeilen.extend(_ohne_architekt(k))
    pfad = _ledger(tmp_path, *zeilen)

    _, out = _run("--pfad", str(pfad), *_leere_logs(tmp_path))

    warnung = _einzige_warnung(out)
    genannt = warnung.split(":", 1)[1]
    assert genannt.index("2") < genannt.index("3") < genannt.index("10"), warnung


# --- Die Bahn-Gegenprobe, die dem Fund seine WIRKUNG gibt --------------------

@pytest.mark.parametrize("bahn,datei,muster", [
    ("bash", "bash/entry/team-status.sh", "grep '^\\[WARNUNG\\]'"),
    ("pwsh", "pwsh/entry/team-status.ps1", "-like '`[WARNUNG`]*'"),
])
def test_kontostand_zeigt_warnungen_auf_beiden_bahnen(bahn, datei, muster):
    """Der Grund, warum die Schwere ueberhaupt zaehlt -- an der Quelle belegt.

    Vorher zeigte der Kontostand die Zeile NICHT, und genau das ist der Fund.
    Faellt einer der beiden Filter weg oder wird er auf `[Hinweis]` erweitert,
    sagt dieser Fall es -- im ersten Fall waere BL-197 wirkungslos, im zweiten
    kehrte das Rauschen zurueck, gegen das BL-14 gebaut wurde.
    """
    wurzel = Path(__file__).resolve().parents[2]
    pfad = wurzel / datei
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt hier nicht (Bahn {bahn} abgewaehlt "
                    f"oder installierte Ablage statt Kit)")
    text = pfad.read_text(encoding="utf-8")
    assert muster in text, (
        f"{datei} filtert die Ledger-Befunde nicht mehr auf [WARNUNG] — "
        f"entweder ist BL-197 wirkungslos geworden oder der Kontostand "
        f"zeigt jetzt auch Hinweise (BL-14).")
    assert "Hinweis]" not in text.split("Ledger-Konsistenz")[-1][:400], (
        f"{datei} zeigt im Kontostand jetzt auch [Hinweis]-Zeilen — das ist "
        f"die Falle aus BL-14, gegen die die zwei Schweregrade gebaut sind.")


# --- Teil (2): der Ausloeser liegt dort, wo er entsteht ----------------------
#
# Die Bauart ist die aus BL-193, und sie ist dort teuer gelernt worden: den
# ABSATZ schneiden, nicht den Abschnitt, und die Faelle ZAEHLEN statt suchen.
# `--architekt-abschluss` und `--kaskade` stehen in derselben Datei schon aus
# anderem Grund; ein Fall ueber den ganzen Abschnitt bliebe gruen, wenn man den
# neuen Satz wieder herausnaehme. Das hat bei BL-193 und BL-195 je einen Anlauf
# gekostet.

def _briefing():
    wurzel = Path(__file__).resolve().parents[2]
    for kandidat in (wurzel / "geteilt" / "prompts" / "rolle-architekt.md",
                     wurzel / "team" / "prompts" / "rolle-architekt.md"):
        if kandidat.is_file():
            return kandidat.read_text(encoding="utf-8")
    pytest.skip("rolle-architekt.md liegt hier nicht")


def _sequenz_absatz():
    """Der EINE Absatz der Scharfschalt-Sequenz, der den Abschluss traegt."""
    t = _briefing()
    marke = "Letzter Schritt der Sequenz"
    assert marke in t, (
        "BL-197 (2): Die Scharfschalt-Sequenz traegt den Kostenabschluss "
        "nicht mehr. Damit haengt er wieder an einer Erinnerung statt an "
        "einem Ereignis — genau der Zustand, an dem im Feld an EINEM Tag "
        "43,90 USD verloren gingen.")
    anfang = t.index(marke)
    ende = t.index("**Die erste Kaskade eines Projekts", anfang)
    return t[anfang:ende]


def test_die_scharfschalt_sequenz_traegt_den_kostenabschluss():
    """Der Kern von Teil (2): der Abschluss haengt an einem EREIGNIS.

    Die Scharfschalt-Sequenz ist schon heute eine Pflicht-Ausgabe — *"am Ende
    jeder Aushaertung immer automatisch"*. Haengt der Kostenabschluss als
    letzter Schritt daran, wird aus einer Erinnerung ein Ausloeser.
    """
    absatz = _sequenz_absatz()
    assert "sitzung-messen" in absatz, (
        "BL-197 (2): Der Betrag muss erst GEMESSEN werden — ohne den ersten "
        "Befehl steht der Leser vor einem <USD>, das er nicht kennt.")
    assert "--architekt-abschluss" in absatz, (
        "BL-197 (2): Der Buchungsbefehl fehlt im Absatz.")
    assert "--kaskade" in absatz, (
        "BL-197 (2): Ohne --kaskade landet die Buchung auf der falschen "
        "Kaskade oder gar keiner.")


def test_der_absatz_nennt_die_gemessene_groessenordnung():
    """Eine Auflage ohne Preisschild wird als Formalie gelesen.

    43,90 USD an einem Tag, gemessen statt geschaetzt — das ist das Argument,
    das die Rolle im entscheidenden Moment ueberzeugt, nicht die Regel.
    """
    absatz = _sequenz_absatz()
    assert "43,90" in absatz, (
        "BL-197 (2): Der Feldbetrag fehlt. Ohne ihn ist der Schritt eine "
        "Formalie unter vielen.")


def test_der_absatz_ersetzt_die_bl165_regel_ausdruecklich_NICHT():
    """Die Gegenrichtung, und der Eintrag verlangt sie woertlich.

    Die Regel sagt das WARUM, die Sequenz das WANN. Wer die Sequenz als Ersatz
    liest, nimmt die Begruendung heraus — und eine Auflage ohne Begruendung
    ist die erste, die beim Kuerzen faellt.
    """
    absatz = _sequenz_absatz()
    assert "Kit-BL-165" in absatz, (
        "BL-197 (2): Der Absatz nennt die Vorbeugungsregel nicht.")
    assert "ersetzt die Regel" in absatz and "nicht" in absatz, (
        "BL-197 (2): Der Absatz sagt nicht, dass er die BL-165-Regel NICHT "
        "ersetzt.")

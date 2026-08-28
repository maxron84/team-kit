#!/usr/bin/env python3
"""Regressionstest fuer BL-208: Beide Selbsttests halten ALLE DREI
Zahlen-Gattungen des READMEs — und der Pruefer sagt, gegen welchen Koerper er
gemessen hat.

DER BEFUND, gemessen beim Nachholen des ausstehenden `bash bash/kit-test.sh`
(2026-08-28): `BL-198` Teil (3) hat den README-Schritt auf die pwsh-Bahn
gebracht und dort ZWEI Gattungen geschlossen — Testfaelle und Testdateien. Die
dritte, die Zahl der ausgelieferten Dateien, blieb ungeprueft: `--dateien` kam
in `pwsh/kit-test.ps1` **nullmal** vor, in `bash/kit-test.sh` dreimal. Die
pwsh-Fassung zog die Zeile `Fertig — <N> Dateien geschrieben` aus dem Log und
DRUCKTE sie als Erfolgsmeldung, ohne sie gegen das README zu halten.

DIE FOLGE WAR MESSBAR: Die Dateizahl im README stand auf 169, waehrend der
Installer 175 schrieb — sechs Dateien lang veraltet, und der Selbsttest der
anderen Bahn meldete in derselben Zeit gruen. Das ist die Gattung von `BL-145`
(*gruen bedeutet auf den beiden Bahnen verschieden viel*), wieder aufgetaucht
an genau der Stelle, die `BL-198` einen Tag zuvor geschlossen hatte.

DER ZWEITE BEFUND HAT DIESELBE WURZEL — die Zahl der Testfaelle ist
KOERPERABHAENGIG. In der Kit-Ablage sind es (Stand 2026-08-28) 1054, in einer
frischen Installation 1053. Die Differenz ist genau EIN Fall:
`test_kit_pruefer_ueberlebt_eine_cp1252_ausgabe` ist ueber `geteilt/kit-*.py`
parametrisiert — zwei Pruefer im Kit; in einer Installation gibt es `geteilt/`
nicht, und der Rueckfallwert `("(keiner)",)` liefert einen Parameter. Beide
Selbsttests messen die INSTALLATION und haben damit recht; das README trug die
KIT-Zahl. Nirgends stand, dass die beiden Koerper verschieden zaehlen.

WAS HIER GEPRUEFT WIRD UND WAS NICHT: Der end-zu-end-Beleg der pwsh-Bahn
braucht PowerShell 7 auf demselben Wirt. Diese Faelle pruefen den QUELLTEXT
beider Selbsttests gegeneinander — dieselbe Bauform, mit der `BL-178` seinen
Gleichstand haelt. Was sie NICHT ersetzen, steht im Backlog benannt.
"""
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
BASH = WURZEL / "bash" / "kit-test.sh"
PWSH = WURZEL / "pwsh" / "kit-test.ps1"
PRUEFER = WURZEL / "geteilt" / "kit-readme-pruefen.py"


def _lies(pfad, was):
    if not pfad.is_file():
        pytest.skip(f"{was} liegt hier nicht (Bahn abgewaehlt oder "
                    f"installierte Ablage statt Kit-Ablage)")
    return pfad.read_text(encoding="utf-8")


# --- Teil (1): die dritte Gattung, auf BEIDEN Bahnen ------------------------

def test_beide_selbsttests_reichen_die_dateizahl_an_den_pruefer_durch():
    """Der Kern des Eintrags, und er ist als ZAHL nachpruefbar.

    Vorher: bash dreimal `--dateien`, pwsh nullmal. Ein Gleichstand, den man
    zaehlen kann, ist einem nachgelesenen vorzuziehen — das ist die Lehre aus
    `BL-154`.
    """
    bash = _lies(BASH, "kit-test.sh")
    pwsh = _lies(PWSH, "kit-test.ps1")
    assert "--dateien" in bash, (
        "kit-test.sh reicht die Dateizahl nicht mehr durch.")
    assert "--dateien" in pwsh, (
        "kit-test.ps1 reicht die Dateizahl NICHT an den README-Pruefer durch "
        "— von den drei Zahlen-Gattungen prueft diese Bahn dann wieder nur "
        "zwei und meldet trotzdem dasselbe Gruen (BL-145/BL-198).")


def test_die_pwsh_bahn_haelt_die_dateizahl_statt_sie_nur_zu_drucken():
    """Die Unterscheidung, an der der Fund haengt.

    `Fertig — 175 Dateien geschrieben` als Erfolgsmeldung auszugeben ist keine
    Pruefung. Die Zahl muss in eine Variable und von dort in den Vergleich.
    """
    pwsh = _lies(PWSH, "kit-test.ps1")
    assert "GeschriebenIst" in pwsh, (
        "kit-test.ps1 haelt die Dateizahl des Installers nicht in einer "
        "Variablen — sie wird dann wieder nur gedruckt.")
    assert re.search(r"GeschriebenIst\s*=\s*\[int\]", pwsh), (
        "kit-test.ps1 liest die Dateizahl nicht als ZAHL aus dem Log; ein "
        "Vergleich gegen einen Textschnipsel prueft nichts.")


def test_die_pwsh_bahn_faehrt_die_gegenprobe_zur_dateizahl():
    """Ein Waechter, der nie rot wird, sichert nichts ab (Bauart `BL-14`).

    Ohne diesen Fall bliebe der Zusatz eine Behauptung: Die Gegenprobe ist
    das, was ihn erst gueltig macht — und sie fehlte auf dieser Bahn genauso
    wie die Pruefung selbst.
    """
    pwsh = _lies(PWSH, "kit-test.ps1")
    assert "verfälschte Dateizahl wird rot" in pwsh, (
        "kit-test.ps1 dreht die Dateizahl nicht zurueck — die neue Pruefung "
        "ist damit unbelegt.")


def test_die_pwsh_bahn_meldet_eine_unlesbare_dateizahl_statt_zu_schweigen():
    """Die Falle, die der Fix selbst aufstellen wuerde.

    Ist die Zahl aus dem Log nicht lesbar, darf der Schritt nicht einfach
    weniger pruefen und trotzdem gruen melden — genau der Zustand, gegen den
    dieser Eintrag geschrieben ist. Er sagt es dann laut.
    """
    pwsh = _lies(PWSH, "kit-test.ps1")
    assert "UNGEPRUEFT (BL-208)" in pwsh, (
        "kit-test.ps1 schweigt, wenn die Dateizahl nicht lesbar war — dann "
        "prueft es zwei von drei Gattungen und sieht wie drei aus.")


# --- Teil (2): der Pruefer nennt seinen Massstab -----------------------------

def test_der_pruefer_sagt_gegen_welchen_koerper_gemessen_wurde():
    """Ein Satz, der diesen Eintrag ueberfluessig gemacht haette.

    Der Pruefer nimmt die Zahlen vom AUFRUFER entgegen. Er kann nicht wissen,
    ob sie aus dem Kit oder aus einer Installation stammen — und die beiden
    zaehlen verschieden. Seit `BL-198` nennt die Schlusszeile die geprueften
    GATTUNGEN; der KOERPER fehlte.
    """
    text = _lies(PRUEFER, "kit-readme-pruefen.py")
    assert "INSTALLATION" in text, (
        "kit-readme-pruefen.py sagt nicht, gegen welchen Koerper gemessen "
        "wird. Wer von Hand nachmisst, misst im Kit und liegt daneben — "
        "genau so kam die falsche Zahl ins README.")
    assert "zählen verschieden" in text or "zaehlen verschieden" in text, (
        "kit-readme-pruefen.py sagt nicht, dass Kit-Ablage und Installation "
        "verschieden zaehlen.")


def test_der_hinweis_erscheint_nur_wenn_wirklich_gemessen_wurde():
    """Die Gegenrichtung, und sie ist die Lehre aus `BL-198` selbst.

    Ein Aufruf ohne Zahlen prueft keine einzige Zahl. Erschiene der
    Massstab-Satz auch dort, waere er wieder die Falschaussage, gegen die
    `BL-198` geschrieben wurde — nur eine Zeile tiefer.
    """
    text = _lies(PRUEFER, "kit-readme-pruefen.py")
    block = text[text.index("if gemessen:"):]
    block = block[:block.index("return 0")]
    zweige = block.split("else:")
    assert len(zweige) == 2, "die Schlusszeile hat ihre zwei Zweige verloren"
    assert "Maßstab" in zweige[0], (
        "der Massstab-Satz steht nicht im gemessen-Zweig")
    assert "Maßstab" not in zweige[1], (
        "der Massstab-Satz erscheint auch OHNE gemessene Zahl — dann "
        "behauptet er eine Messung, die nicht stattgefunden hat (BL-198).")


# --- Gleichstand, soweit ohne PowerShell 7 belegbar --------------------------

def test_beide_selbsttests_pruefen_dieselben_drei_gattungen():
    """Der Gleichstand, um den es geht — an der Quelle gemessen statt
    nachgelesen.

    Was diese Faelle NICHT leisten: den end-zu-end-Beleg der pwsh-Bahn. Der
    braucht PowerShell 7 auf demselben Wirt und steht im Backlog benannt neben
    der Gegenprobe aus `BL-178` und der Wurzel-Code-Pruefung aus `BL-155`.
    """
    bash = _lies(BASH, "kit-test.sh")
    pwsh = _lies(PWSH, "kit-test.ps1")
    for schalter in ("--faelle", "--testdateien", "--dateien"):
        assert schalter in bash and schalter in pwsh, (
            f"{schalter} fehlt auf einer der beiden Bahnen — dann sichert "
            f"'gruen' dort weniger zu als hier (BL-145).")

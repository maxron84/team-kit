#!/usr/bin/env python3
r"""BL-135: Die pwsh-Bahn rechnete in der OEM-Codepage der Konsole.

⚠️ Feldbefund, dieselbe Windows-Maschine wie BL-113 und BL-122…BL-134.
Gefunden von `kit-test.ps1` Schritt 6 — und zwar erst, NACHDEM BL-134 den
Schritt davor repariert hatte. Bis dahin stieg der Selbsttest in Schritt 5
aus und hat Schritt 6 nie erreicht.

`[Console]::OutputEncoding` ist unter Windows die OEM-Codepage der Konsole
(auf der Fundmaschine 850, nicht 1252 — das ist noch einmal eine andere als
die aus BL-133). PowerShell benutzt sie fuer ZWEIERLEI:

BEIM SCHREIBEN — die harmlose Haelfte.
    Die Rollen melden mit `[Console]::Out.WriteLine` (Aufrufkonvention Punkt
    5). cp850 kennt keinen Geviertstrich; .NET ersetzt ihn beim Kodieren
    still durch einen Bindestrich. Aus

        [ralph] DRY-RUN — kein Claude-Aufruf.

    wurde im umgelenkten Log

        [ralph] DRY-RUN - kein Claude-Aufruf.

    Kein Fehler, keine Meldung — ein anderes Zeichen. Der Selbsttest suchte
    nach der Zeile mit Geviertstrich und fand sie nicht.

BEIM LESEN — die Haelfte, an der eine ENTSCHEIDUNG haengt.
    PowerShell dekodiert die Ausgabe NATIVER Prozesse mit derselben Kodierung.
    Die Werkzeuge unter `team/tools/` schreiben seit BL-133 ausdruecklich
    UTF-8. Als cp850 gelesen wird aus dem Umlaut in "ueberholt" (U+00FC) das
    Zeichenpaar U+251C U+255D — zwei Rahmenzeichen. Der Filter in
    `vollautomatik.ps1`

        Where-Object { $_ -and $_ -notmatch 'erledigt|ueberholt' }

    trifft dann nicht mehr. Ein ueberholter Fund bleibt in der Liste der
    OFFENEN Arbeit stehen, und die Fixphase arbeitet an etwas, das erledigt
    ist. `erledigt` ist reines ASCII und funktionierte die ganze Zeit; nur der
    Umlaut fiel durch. Genau die Bauart Fehler, die niemand sieht: kein
    Abbruch, keine Meldung, nur eine Entscheidung, die anders ausfaellt.

WARUM DAS NICHT DIE SCHULD VON BL-133 IST
    Naheliegender Verdacht, und er ist falsch. Vor BL-133 schrieben die
    Werkzeuge cp1252; als cp850 gelesen wurde aus dem Umlaut U+00B3. Auch kein
    Treffer. Der Pfad war vorher kaputt und danach — nur mit einem anderen
    falschen Zeichen. Was BL-133 geaendert hat: Die Werkzeugseite spricht jetzt
    EINDEUTIG UTF-8, und damit ist die Lesesseite ueberhaupt erst reparierbar.
    Zwei Enden einer Leitung; eines allein festzuziehen genuegt nie.

WARUM AM VERHALTEN UND NICHT AM QUELLTEXT
    Anders als BL-126, BL-129 bis BL-131: Dieser Test faellt auf JEDEM Wirt,
    wenn jemand die Zeile entfernt — die Kodierung wird hier GESTELLT und
    nicht vorausgesetzt. Ein Test, der auf eine cp850-Konsole wartet, liefe
    genau einmal, naemlich auf der Maschine, auf der der Fund schon gemacht
    ist.
"""
import re
import subprocess
from pathlib import Path

import pytest

from conftest import PYTHON_BEFEHL, basis_umgebung, kit_pfad

WURZEL = Path(__file__).resolve().parents[2]

# Der Umlaut, an dem es haengt, und seine cp850-Fehldeutung. Bewusst als
# Codepoints und nicht als Literal: Diese Datei wuerde die Zeichen sonst
# selbst durch jede Werkzeugkette schleifen, die sie gerade pruefen soll.
UMLAUT = "ü"                    # ü
CP850_TRUEMMER = "├╝"      # ├╝ — die UTF-8-Bytes, als cp850 gelesen
GEVIERTSTRICH = "—"             # —

LIB_PSM1 = kit_pfad("lib.psm1")


def _pwsh(skript, tmp_path, name="probe.ps1"):
    """Faehrt ein pwsh-Skript und gibt dessen ROHE Bytes zurueck.

    Roh, nicht dekodiert: Der Gegenstand dieses Tests IST die Kodierung.
    subprocess im Textmodus laufen zu lassen legte die Frage in Pythons Hand
    und beantwortete sie damit, statt sie zu messen. (Der Schalter wird hier
    bewusst nicht ausgeschrieben — der Sammeltest aus BL-130 durchsucht diese
    Dateien nach genau dieser Zeichenfolge und haette recht damit.)

    Die Datei traegt ein BOM — dieselbe Regel wie fuer jede .ps1 im Kit
    (BL-113). Ohne BOM liest Windows PowerShell 5.1 die Sonderzeichen in der
    ANSI-Codepage, und dieser Test praeparierte sich seinen eigenen Befund
    (die Lehre aus BL-134).
    """
    pfad = tmp_path / name
    pfad.write_bytes(b"\xef\xbb\xbf" + skript.encode("utf-8"))
    return subprocess.run(["pwsh", "-NoProfile", "-File", str(pfad)],
                          capture_output=True, cwd=str(tmp_path),
                          env=basis_umgebung())


def _pwsh_vorhanden():
    from shutil import which
    return which("pwsh") is not None and LIB_PSM1.is_file()


pytestmark = pytest.mark.skipif(
    not _pwsh_vorhanden(),
    reason="pwsh-Bahn nicht verfuegbar (pwsh oder team/lib.psm1 fehlt)")


# --- Die Leseseite: die Haelfte mit der Entscheidung -------------------------

def test_werkzeugausgabe_kommt_mit_umlaut_an(tmp_path):
    """Der Kern des Fundes, an der Stelle, an der er Geld kostet.

    Nachgestellt wird der Filter aus `vollautomatik.ps1`: Eine Zeile aus
    `beutebuch.py list` mit Status "ueberholt" MUSS von
    `-notmatch 'erledigt|ueberholt'` erwischt werden. Wird sie es nicht, gilt
    ein abgeschlossener Fund weiter als offene Arbeit.

    Die Konsolen-Codepage wird GESTELLT (850), damit der Test nicht nur auf
    der Fundmaschine etwas beweist.
    """
    beutebuch = kit_pfad("tools", "beutebuch.py")
    if not beutebuch.is_file():
        pytest.skip("beutebuch.py liegt in dieser Ablage nicht")

    buch = tmp_path / "beutebuch.md"
    buch.write_text(
        "# Beutebuch\n\n## Funde\n\n"
        f"### HM-1 {GEVIERTSTRICH} Alter Fund\n"
        f"- **Status**: {UMLAUT}berholt\n"
        "- **Reproducer-Test**: `tests/test_hm1.py`\n"
        "- Betrifft `src/app.py`\n", encoding="utf-8")

    skript = f"""$ErrorActionPreference = 'Stop'
# Die Fundlage herstellen: eine Konsole in der OEM-Codepage.
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(850)
Import-Module '{LIB_PSM1.as_posix()}' -Force -DisableNameChecking
$roh = & {PYTHON_BEFEHL} '{beutebuch.as_posix()}' --pfad '{buch.as_posix()}' list
$zeile = [string]$roh
$muster = 'erledigt|' + [char]0x00FC + 'berholt'
[Console]::Out.WriteLine('CODEPOINTS=' + (($zeile.ToCharArray() | ForEach-Object {{ [int]$_ }}) -join ','))
[Console]::Out.WriteLine('OFFEN=' + ($zeile -notmatch $muster))
"""
    ergebnis = _pwsh(skript, tmp_path)
    ausgabe = ergebnis.stdout.decode("utf-8", "replace")
    assert "OFFEN=" in ausgabe, (
        f"die Probe lief nicht durch:\n{ausgabe}\n"
        f"{ergebnis.stderr.decode('utf-8', 'replace')}")

    codepoints = [int(z) for z in
                  ausgabe.split("CODEPOINTS=")[1].splitlines()[0].split(",")]
    zeile = "".join(chr(c) for c in codepoints)
    assert CP850_TRUEMMER not in zeile, (
        "Die Werkzeugausgabe kommt in der OEM-Codegepage an: Aus dem Umlaut "
        f"sind zwei Rahmenzeichen geworden ({CP850_TRUEMMER!r}). lib.psm1 "
        "muss [Console]::OutputEncoding auf UTF-8 stellen (BL-135).\n"
        f"Angekommen: {zeile!r}")
    assert f"{UMLAUT}berholt" in zeile, (
        f"der Statuswert kommt nicht unversehrt an: {zeile!r}")
    assert "OFFEN=False" in ausgabe, (
        "Ein Fund mit Status 'ueberholt' gilt weiter als OFFENE ARBEIT — die "
        "Fixphase arbeitet dann an etwas, das erledigt ist (BL-135).")


# --- Die Schreibseite -------------------------------------------------------

def test_rollenmeldung_ueberlebt_die_umlenkung(tmp_path):
    """Was `[Console]::Out.WriteLine` schreibt, muss in der Datei ankommen.

    cp850 kennt keinen Geviertstrich und ersetzt ihn beim Kodieren still durch
    einen Bindestrich — kein Fehler, keine Meldung, ein anderes Zeichen. Genau
    daran ist `kit-test.ps1` Schritt 6 gescheitert; im Betrieb trifft es jede
    Rollenmeldung mit Umlaut in `vollautomatik-*.log`.
    """
    skript = f"""$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(850)
Import-Module '{LIB_PSM1.as_posix()}' -Force -DisableNameChecking
[Console]::Out.WriteLine('[ralph] DRY-RUN {GEVIERTSTRICH} kein Claude-Aufruf.')
[Console]::Error.WriteLine('[ralph] {UMLAUT}berholt')
"""
    ergebnis = _pwsh(skript, tmp_path)
    assert GEVIERTSTRICH.encode("utf-8") in ergebnis.stdout, (
        "Der Geviertstrich hat die Umlenkung nicht ueberlebt — cp850 hat ihn "
        "durch einen Bindestrich ersetzt (BL-135).\n"
        f"Roh: {ergebnis.stdout!r}")
    assert UMLAUT.encode("utf-8") in ergebnis.stderr, (
        "Der Umlaut auf stderr kam nicht als UTF-8 an (BL-135).\n"
        f"Roh: {ergebnis.stderr!r}")


def test_kein_bom_vor_der_ersten_ausgabezeile(tmp_path):
    """Die Gegenprobe zur Abhilfe.

    `UTF8Encoding($true)` waere hier falsch: Das ist eine Kodierung fuer einen
    STROM, nicht fuer eine Datei. Mit BOM stuende `\\ufeff` vor der ersten
    Zeile jeder Rolle — und im Log vor der ersten Zeile jedes Laufs.
    """
    skript = f"""$ErrorActionPreference = 'Stop'
Import-Module '{LIB_PSM1.as_posix()}' -Force -DisableNameChecking
[Console]::Out.WriteLine('erste Zeile')
"""
    ergebnis = _pwsh(skript, tmp_path)
    assert not ergebnis.stdout.startswith(b"\xef\xbb\xbf"), (
        "Die Ausgabe beginnt mit einem BOM. Eine Stromkodierung traegt keines "
        f"(BL-135).\nRoh: {ergebnis.stdout[:20]!r}")
    assert ergebnis.stdout.startswith(b"erste Zeile"), \
        f"unerwarteter Anfang: {ergebnis.stdout[:30]!r}"


# --- Die Zusicherung am Ort, an dem sie gilt --------------------------------

def test_die_bibliothek_setzt_es_und_nicht_die_entrypoints():
    """Warum in `lib.psm1` und nicht in jedem Entrypoint: Die Bibliothek ist
    die eine Stelle, die JEDE Rolle durchlaeuft.

    Stuende die Zeile in den Entrypoints, muesste sie neunmal dastehen — und
    die zehnte Datei, die jemand hinzufuegt, vergisst sie. Das ist dieselbe
    Ueberlegung, aus der die Python-Werkzeuge ihre Stroeme selbst umstellen,
    statt sich auf ein `PYTHONIOENCODING` des Aufrufers zu verlassen
    (BL-133).
    """
    quelle = LIB_PSM1.read_text(encoding="utf-8-sig")
    assert "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)" in quelle, (
        "lib.psm1 stellt die Ausgabekodierung nicht auf UTF-8 — dann gilt die "
        "OEM-Codepage der Konsole (BL-135)")
    assert "$OutputEncoding = [System.Text.UTF8Encoding]::new($false)" in quelle, (
        "lib.psm1 stellt die Kodierung fuer die Gegenrichtung nicht — ein "
        "Argument mit Umlaut geht dann in der alten Codepage an die Werkzeuge")


def _dateien(muster):
    """Beide Ablagen in einer Liste — die installierte (Wurzel) und die des
    Kits (pwsh/). Ein nicht passendes Muster liefert einfach nichts."""
    treffer = []
    for m in muster:
        treffer.extend(sorted(p for p in WURZEL.glob(m) if p.is_file()))
    return treffer


# Der Ausdruck, mit dem eine pwsh-Datei die Ausgabe eines Prozesses AUFFAENGT:
# `$x = & befehl …` oder eine Umlenkung in eine Datei, die danach gelesen wird.
_FAENGT_AUF = re.compile(r"^\s*\$\w+\s*=\s*&\s|\*>\s*\$|2>&1")
_IMPORTIERT_LIB = re.compile(r"Import-Module\s+\S*lib\.psm1", re.I)
_SETZT_KODIERUNG = "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)"


def test_wer_prozessausgabe_auffaengt_liest_sie_als_utf8():
    """Die Empfaengerseite desselben Fundes — eine Leitung hat zwei Enden.

    Genau daran ist der Selbsttest beim fuenften Anlauf gescheitert, NACHDEM
    die Schreibseite gefixt war: `kit-test.ps1` faengt einen kompletten
    Vollautomatik-Lauf auf und vergleicht ihn mit Mustern, in denen Umlaute
    und Geviertstriche stehen. Die Rollen schrieben korrekt UTF-8; der
    auffangende Prozess dekodierte weiter cp850, und aus "ueber RALPH_CAP"
    wurde ein Rahmenzeichenpaar. Die Pruefung fiel, obwohl der Lauf richtig
    war.

    Wer `lib.psm1` importiert, erbt die Einstellung — das sind alle
    Entrypoints, und deshalb ist das PRODUKT nicht betroffen
    (`vollautomatik.ps1` importiert, bevor es in `Rolle-Starten` auffaengt).
    Wer sie NICHT importiert und trotzdem auffaengt, muss sie selbst setzen.
    """
    quellen = _dateien(("pwsh/*.ps1", "pwsh/entry/*.ps1", "pwsh/scripts/*.ps1",
                        "*.ps1", "scripts/*.ps1"))
    if not quellen:
        pytest.skip("keine pwsh-Dateien in dieser Ablage")
    funde = []
    for pfad in quellen:
        text = pfad.read_text(encoding="utf-8-sig")
        if _IMPORTIERT_LIB.search(text) or _SETZT_KODIERUNG in text:
            continue
        if any(_FAENGT_AUF.search(z.split("#", 1)[0])
               for z in text.splitlines()):
            funde.append(pfad.relative_to(WURZEL).as_posix())
    assert not funde, (
        "Diese Dateien fangen Prozessausgabe auf, ohne sie als UTF-8 zu "
        "lesen, und importieren auch lib.psm1 nicht. Unter Windows gilt dann "
        "die OEM-Codepage der Konsole, und jeder Vergleich mit einem Muster "
        "aus Umlauten oder Geviertstrichen schlaegt fehl (BL-135):\n  "
        + "\n  ".join(funde))

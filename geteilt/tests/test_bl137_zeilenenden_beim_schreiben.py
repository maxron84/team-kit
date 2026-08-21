#!/usr/bin/env python3
r"""BL-137: BL-129 hat EINE Schreibstelle geheilt. Es waren fuenf.

⚠️ Feldbefund, dieselbe Windows-Maschine wie BL-113 und BL-122…BL-136.
Aufgefallen beim ersten Lauf von `bash/kit-test.sh` auf dieser Maschine: Mitten
in Schritt 4 stand, zwischen den Punkten der Testlaeufe, eine Zeile von Git

    warning: in the working copy of 'team.config.sh',
             CRLF will be replaced by LF the next time Git touches it

— und zwar fuer genau acht Dateien einer frischen Installation: die beiden
Konfigurationen und die sechs Rollen-Briefings. Gemessen im Wegwerf-Repo des
laufenden Selbsttests:

    team.config.sh                 181 Wagenruecklaeufe
    team.config.ps1                157
    team/prompts/rolle-*.md (6x)    33 je Datei
    ralph.sh, team/lib.sh            0
    .gitattributes                   0

Die Trennlinie ist scharf und nennt den Taeter: Betroffen ist AUSSCHLIESSLICH,
was durch `fuelle()` gelaufen ist — die Routine, die die Platzhalter ersetzt.
Wer nur kopiert wurde, ist heil geblieben.

DIE URSACHE, ZWEIMAL DIESELBE ZEILE
    `Path.write_text()` oeffnet im Textmodus mit `newline=None`. Der uebersetzt
    beim Schreiben JEDES `"\n"` in `os.linesep`, unter Windows also in
    `"\r\n"`. Nicht die geaenderte Zeile allein: `fuelle()` liest die Datei
    ganz, ersetzt und schreibt sie ganz zurueck — also bekommt jede Zeile ihr
    Byte, auch die, an der nie ein Platzhalter stand.

    Es ist zeichengleich der Fehler aus BL-129. Dort war es
    `os.fdopen(fd, "w")` in `kosten.py`, hier `write_text` in `install.sh` und
    in `beutebuch.py` — dieselbe Schicht, dieselbe Vorgabe, dasselbe Byte.
    BL-129 hat die Stelle geheilt, an der der Fund gemacht wurde, und nicht
    nach ihren Geschwistern gesucht. Das ist die Bauart von BL-131 und BL-133:
    ein Fund, der als Einzelstelle behandelt wird, obwohl er ein Muster ist.

WARUM ES TROTZDEM NICHT SOFORT GEKNALLT HAT
    Weil die Wirkung eine Schicht weiter unten abgefangen wird: Git-Bash unter
    MSYS entfernt die Wagenrueclaeufe beim `source`, die Werte in
    `team.config.sh` kommen also richtig an. Genau deshalb hat der Selbsttest
    511 Faelle gruen gemeldet, waehrend Git danebenstand und die Verletzung
    ansagte. Ein Fehler, den die naechste Schicht repariert, ist keiner, der
    weg ist — er ist einer, der auf eine Schicht wartet, die es nicht tut.

    Die wartende Schicht heisst Commit. Vor BL-136 trug kein Zielprojekt eine
    `.gitattributes`; eine unter Windows installierte `team.config.sh` ging
    also MIT CRLF ins Repo, und der naechste Klon auf einer POSIX-Maschine
    bekam sie zurueck, wie sie eingecheckt war. Dort greift MSYS nicht.

DIE DRITTE STELLE: beutebuch.py
    `beutebuch.py` schreibt an drei Stellen dieselbe Art: `archiviere`
    schreibt aktives Buch und Archiv neu, `set` schreibt das aktive Buch neu.
    Alle drei lesen mit `read_text` (universal newlines, also `\n` im
    Speicher) und schreiben mit `write_text` (Uebersetzung, also `\r\n` auf
    der Platte). Ein einziges `beutebuch.py set HM-1 erledigt` auf einer
    Windows-Maschine ruesst damit das GANZE Beutebuch um.

    Anders als bei den Konfigurationen faengt hier nichts auf: Die Datei liegt
    unter dem Plan-Ordner, dessen Name konfigurierbar ist — das
    `.gitattributes`-Fragment aus BL-136 kann sie nicht mit einer festen Regel
    treffen und tut es nicht (nachgemessen im Feldprojekt: `attr/` leer). Was
    `beutebuch.py` schreibt, wird also genau so eingecheckt.

WARUM DER pwsh-INSTALLER DEN FEHLER NIE HATTE
    `install.ps1` schreibt ueber `[System.IO.File]::WriteAllText`, und das
    uebersetzt keine Zeilenenden. Die Bahn, um die es auf dieser Maschine
    ueberhaupt ging, ist die saubere; getroffen hat es die, von der alle
    annahmen, sie laufe ohnehin nur unter Linux. Dieselbe Annahme wie in
    BL-131 und BL-133, nur andersherum.

WARUM `newline=""` UND NICHT `write_text(..., newline=...)`
    Den Parameter hat `write_text` erst seit Python 3.10. Das Kit verlangt 3.8
    (`kit-einrichten.sh`, `finde_python()`), und ein Installer, der auf einer
    Maschine mit 3.9 mit `TypeError` abbricht, ist schlimmer als der Fehler,
    den er beheben soll. `p.open("w", ..., newline="")` gibt es seit 3.4.

WARUM DER ABGLEICH MITZIEHEN MUSSTE
    `--update` rendert die Kit-Fassung von TEAM.md/CLAUDE.md frisch und
    vergleicht sie gegen die installierte. Nach diesem Fix ist die frische
    LF und eine vor dem Fix installierte CRLF — `diff` haette dann JEDE Zeile
    als abgewichen gemeldet und den Anwender vor eine Inhaltsaenderung
    gestellt, die keine ist. Ein stiller Fehler, gegen einen lauten Fehlalarm
    getauscht, ist kein Fortschritt. `--strip-trailing-cr` vergleicht den
    Inhalt und ueberlaesst die Zeilenenden der Regel, die dafuer da ist.

WARUM HIER VERHALTEN UND QUELLTEXT NEBENEINANDER STEHEN
    Dieselbe Ueberlegung wie in BL-129: Unter Linux ist `os.linesep` schon
    `"\n"`, ein reiner Verhaltenstest waere also auf der Maschine, auf der
    das Kit meistens gebaut wird, auch OHNE den Fix gruen. Er wuerde den
    Rueckfall genau dort nicht melden, wo er entsteht. Die Verhaltenstests
    beweisen die Wirkung dort, wo sie messbar ist; die Quelltext-
    Zusicherungen halten die Stelle auch auf einem Wirt fest, der den
    Unterschied nicht sehen kann.
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT, kit_pfad

BEUTEBUCH_PY = kit_pfad("tools", "beutebuch.py")

VORLAGE = (
    "# Beutebuch — Fixture\n"
    "\n"
    "## Funde\n"
)
ARCHIV_KOPF = (
    "# Beutebuch-Archiv — Fixture\n"
    "\n"
    "## Funde\n"
)


def _block(nr, status):
    return (
        f"### HM-{nr} — Fund Nr. {nr}\n"
        f"- **Angreifer**: Marv\n"
        f"- **Status**: {status}\n"
        f"- **Reproschritte**:\n"
        f"  1. Schritt eins fuer Fund {nr}.\n"
        f"- **Erwartung**: …\n"
        f"- **Realität**: …\n"
    )


def _lege_an(pfad, kopf, bloecke):
    """Legt eine Fixture-Datei BYTEGENAU mit LF an.

    Bewusst `write_bytes`: `write_text` traegt hier denselben Fehler wie der
    Prueflung — die Fixture haette dann schon CRLF, und der Test wuerde
    messen, was er selbst hineingeschrieben hat, statt was das Werkzeug
    schreibt. (Genau so beim ersten Entwurf passiert.)
    """
    inhalt = kopf + "\n" + "\n\n".join(bloecke) + "\n" if bloecke else kopf
    pfad.write_bytes(inhalt.encode("utf-8"))
    assert pfad.read_bytes().count(b"\r") == 0, "Fixture selbst schon verdorben"
    return pfad


def _run(*args):
    ergebnis = subprocess.run(
        [sys.executable, str(BEUTEBUCH_PY), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return ergebnis.returncode, ergebnis.stdout, ergebnis.stderr


def _cr(pfad):
    return Path(pfad).read_bytes().count(b"\r")


def _quelle(kit_relativ):
    """Liest eine Datei, die es NUR in der Kit-Ablage gibt."""
    pfad = REPO_ROOT / kit_relativ
    if not pfad.is_file():
        pytest.skip(f"{kit_relativ} liegt nur in der Kit-Ablage")
    return pfad.read_text(encoding="utf-8")


# --------------------------------------------------------------- Verhalten
def test_set_laesst_das_beutebuch_bei_lf(tmp_path):
    """Ein Statuswechsel schreibt die Datei GANZ neu — also ganz mit LF."""
    aktiv = _lege_an(tmp_path / "aktiv.md", VORLAGE,
                     [_block(1, "offen"), _block(2, "offen")])
    rc, _, err = _run("--pfad", str(aktiv), "set", "HM-1", "erledigt (Frank-Fix, abc)")
    assert rc == 0, err
    assert _cr(aktiv) == 0, (
        f"beutebuch.py set hat {_cr(aktiv)} Wagenruecklaeufe hinterlassen — "
        "write_text uebersetzt unter Windows jedes \\n"
    )
    assert "erledigt (Frank-Fix, abc)" in aktiv.read_text(encoding="utf-8")


def test_archiviere_laesst_beide_dateien_bei_lf(tmp_path):
    """Beim Archivieren werden ZWEI Dateien neu geschrieben, nicht eine."""
    aktiv = _lege_an(tmp_path / "aktiv.md", VORLAGE,
                     [_block(1, "offen"), _block(2, "erledigt (Frank-Fix, abc)")])
    archiv = _lege_an(tmp_path / "archiv.md", ARCHIV_KOPF, [])
    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv),
                        "archiviere")
    assert rc == 0, err
    assert out.split() == ["HM-2"], out
    assert _cr(aktiv) == 0, f"aktives Buch: {_cr(aktiv)} Wagenruecklaeufe"
    assert _cr(archiv) == 0, f"Archiv: {_cr(archiv)} Wagenruecklaeufe"


def test_ein_bestehendes_crlf_buch_wird_geheilt_statt_vererbt(tmp_path):
    """Der Rueckweg fuer Buecher, die vor diesem Fix entstanden sind.

    `read_text` liest unter universal newlines, `\r\n` kommt also als `\n` im
    Speicher an. Wer danach ohne Uebersetzung schreibt, legt die Datei
    normalisiert ab — der Fix repariert Altbestand beim ersten Schreiben mit,
    ohne dass jemand eine Wanderung anstossen muss.
    """
    aktiv = tmp_path / "aktiv.md"
    inhalt = VORLAGE + "\n" + _block(1, "offen")
    aktiv.write_bytes(inhalt.replace("\n", "\r\n").encode("utf-8"))
    assert _cr(aktiv) > 0, "Fixture sollte hier absichtlich CRLF tragen"
    rc, _, err = _run("--pfad", str(aktiv), "set", "HM-1", "erledigt")
    assert rc == 0, err
    assert _cr(aktiv) == 0, "das alte CRLF ist mitgeschleppt worden"


# ------------------------------------------------------------- Quelltext
def test_die_werkzeuge_schreiben_ohne_uebersetzung():
    """Kein `write_text` in den Werkzeugen — es traegt die Vorgabe des Wirts.

    Die Zusicherung steht am Quelltext, weil ein Verhaltenstest unter Linux
    auch ohne den Fix gruen ist (BL-129, dieselbe Begruendung).
    """
    verdaechtig = []
    for name in ("beutebuch.py", "kosten.py", "zitat_lint.py"):
        pfad = kit_pfad("tools", name)
        if not pfad.is_file():
            continue
        # Ueber den Syntaxbaum und nicht ueber den Text: Der erste Entwurf
        # suchte `.write_text(` per Regex und schlug an der Stelle an, die
        # den Fehler ERKLAERT — im Docstring von `_schreibe()`. Ein Waechter,
        # der seine eigene Begruendung fuer einen Verstoss haelt, zwingt dazu,
        # die Begruendung zu loeschen. Der Baum kennt nur echte Aufrufe.
        baum = ast.parse(pfad.read_text(encoding="utf-8"))
        for knoten in ast.walk(baum):
            if (isinstance(knoten, ast.Call)
                    and isinstance(knoten.func, ast.Attribute)
                    and knoten.func.attr == "write_text"):
                verdaechtig.append(f"{name}:{knoten.lineno}")
    assert not verdaechtig, (
        "write_text() uebersetzt unter Windows jedes \\n zu \\r\\n und schreibt "
        "die Datei GANZ neu — auch die Zeilen, die niemand angefasst hat.\n"
        "Stattdessen: with pfad.open(\"w\", encoding=\"utf-8\", newline=\"\") "
        "as fh: fh.write(...)\n  " + "\n  ".join(verdaechtig)
    )


def test_der_bash_installer_schreibt_ohne_uebersetzung():
    """`fuelle()` ist die Stelle, an der die acht Dateien verdorben wurden."""
    text = _quelle("bash/install.sh")
    assert not re.search(r"\.write_text\s*\(", text), (
        "bash/install.sh benutzt wieder write_text — das ist die Stelle, an "
        "der team.config.sh 181 Wagenruecklaeufe bekommen hat."
    )
    treffer = re.findall(r'\.open\(\s*"w"[\s\S]{0,300}?newline=""', text)
    assert len(treffer) >= 2, (
        "Erwartet werden ZWEI Schreibstellen mit newline=\"\" — die "
        "Erstinstallation und der Update-Pfad haben je eine eigene "
        "Fuell-Routine. Gefunden: " + str(len(treffer))
    )


def test_der_pwsh_installer_bleibt_bei_writealltext():
    """Die pwsh-Bahn hatte den Fehler nie — das soll so bleiben.

    `Set-Content` und `Out-File` haengen sich an die Zeilenende-Vorgabe der
    Sitzung; `WriteAllText` schreibt die Zeichenkette, wie sie ist.
    """
    text = _quelle("pwsh/install.ps1")
    assert "[System.IO.File]::WriteAllText" in text
    for verboten in ("Set-Content", "Out-File"):
        assert verboten not in text, (
            f"{verboten} in install.ps1 — es entscheidet ueber Zeilenenden "
            "und Kodierung nach Sitzungsvorgabe statt nach der Kit-Regel."
        )


def test_der_abgleich_vergleicht_zeilenende_unabhaengig():
    """Sonst tauscht der Fix einen stillen Fehler gegen einen Fehlalarm."""
    text = _quelle("bash/install.sh")
    aufrufe = []
    for nr, zeile in enumerate(text.splitlines(), 1):
        blank = zeile.strip()
        if blank.startswith("#") or not re.search(r"(?<![\w-])diff\b", blank):
            continue
        # `git … diff` ist etwas anderes: Es vergleicht gegen den Index und
        # richtet sich nach .gitattributes — das ist genau die Schicht, die
        # die Zeilenenden regeln SOLL.
        if re.search(r"(?<![\w-])git\b[^|;]*?(?<![\w-])diff\b", blank):
            continue
        aufrufe.append(f"{nr}: {blank}")
    assert aufrufe, "kein diff-Aufruf mehr in install.sh gefunden"
    ohne_flagge = [z for z in aufrufe if "--strip-trailing-cr" not in z]
    assert not ohne_flagge, (
        "Ein Abgleich ohne --strip-trailing-cr meldet nach diesem Fix JEDE "
        "Zeile einer vor dem Fix installierten Datei als abgewichen. Das gilt "
        "auch fuer den Befehl, den die Meldung dem Anwender zum Nachsehen "
        "nennt — sonst sieht er dort ein anderes Bild als der Installer:\n  "
        + "\n  ".join(ohne_flagge)
    )

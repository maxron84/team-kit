#!/usr/bin/env python3
r"""BL-136: Die Regel gegen `bad interpreter` schuetzte das Kit — nicht die
Projekte.

⚠️ Feldbefund, dieselbe Windows-Maschine wie BL-113 und BL-122…BL-135.
Aufgefallen beim Committen des Feldprojekts: Git meldete fuer jede Datei

    warning: in the working copy of 'team/lib.psm1',
             LF will be replaced by CRLF the next time Git touches it

Das Kit-Repo traegt seit Langem eine `.gitattributes` mit `* text=auto eol=lf`,
und ihr Kopf nennt den Grund ausdruecklich: Unter Git for Windows ist
`core.autocrlf=true` der Auslieferungswert, ein Klon landet dann mit CRLF im
Arbeitsbaum, die erste Zeile jedes Skripts endet auf einem Wagenruecklauf, und
bash sucht einen Interpreter, dessen Name auf genau dieses unsichtbare Zeichen
endet:

    bash: ./ralph.sh: /usr/bin/env: bad interpreter: No such file or directory

Nur: Diese Datei liegt im KIT. Kein Installer hat je eine in ein Zielprojekt
gelegt — es gab dafuer nicht einmal eine Vorlage. Die Regel schuetzte damit
genau den Ort nicht, an dem das Kit im Feld laeuft.

WARUM ES SO LANGE UNBEMERKT BLIEB
    Der Fall entsteht NICHT bei der Installation. Der Installer schreibt seine
    Dateien mit LF, und unmittelbar danach laeuft alles. Er entsteht beim
    naechsten KLON oder CHECKOUT — also spaeter, meist auf einer anderen
    Maschine, und mit einer Fehlermeldung, die nach einer kaputten
    Installation aussieht statt nach einer Zeileneinstellung. Zwischen Ursache
    und Wirkung liegen Tage und ein Rechnerwechsel.

    Dazu kommt: Auf einem POSIX-Wirt ist `core.autocrlf` per Default `false`.
    Wer das Kit unter Linux entwickelt und dort testet, sieht den Fall nie —
    dieselbe Blindstelle wie bei BL-126, BL-129 bis BL-131.

WARUM DAS FRAGMENT SICH ZURUECKHAELT
    Das Kit-Repo schreibt `* text=auto eol=lf` — fuer sich selbst richtig, als
    Vorlage falsch: Das gaelte fuer den Code des Projekts mit, und ob der LF
    oder CRLF traegt, ist die Entscheidung des Projekts. Geregelt werden die
    Dateiarten, die das Kit MITBRINGT. Dieselbe Zurueckhaltung, die
    `gitignore.fragment` seit jeher uebt ("das Kit bringt KEINE
    stack-spezifischen Eintraege in dein Projekt").

WARUM DIE ZUSICHERUNGEN HIER AM QUELLTEXT HAENGEN
    Wie bei BL-126, BL-129 und BL-130: Der Fall ist auf dem Wirt, auf dem die
    Suite meistens laeuft, gar nicht herstellbar — `core.autocrlf` steht dort
    auf `false`, und ein Test muesste die Git-Konfiguration der Maschine
    umstellen, um etwas zu beweisen. Geprueft wird deshalb, dass die VORLAGE
    das Richtige sagt und dass BEIDE Installer sie auf BEIDEN Wegen
    (Erstinstallation und Update) anfassen.
"""
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
FRAGMENT = WURZEL / "bootstrap" / "gitattributes.fragment"

# Die Marke, an der die Installer erkennen, ob der Block schon dasteht.
MARKE = "T.E.A.M.-Zeilenenden"


def _quelle(*kandidaten):
    for kandidat in kandidaten:
        pfad = WURZEL / kandidat
        if pfad.is_file():
            return pfad
    pytest.skip(f"keine der Quellen liegt in dieser Ablage: {kandidaten}")


def _regeln():
    """Die Regelzeilen des Fragments, ohne Kommentare und Leerzeilen."""
    if not FRAGMENT.is_file():
        pytest.skip("bootstrap/gitattributes.fragment liegt nur in der Kit-Ablage")
    return [z.strip() for z in FRAGMENT.read_text(encoding="utf-8").splitlines()
            if z.strip() and not z.lstrip().startswith("#")]


# --- Die Vorlage ------------------------------------------------------------

def test_das_fragment_traegt_die_marke():
    """Ohne sie kann kein Installer entscheiden, ob der Block schon dasteht —
    und ergaenzte ihn bei jedem Lauf erneut."""
    if not FRAGMENT.is_file():
        pytest.skip("bootstrap/gitattributes.fragment liegt nur in der Kit-Ablage")
    assert MARKE in FRAGMENT.read_text(encoding="utf-8"), (
        f"das Fragment nennt '{MARKE}' nicht — die Erkennung der Installer "
        "haengt an dieser Marke")


def test_die_shell_bahn_bekommt_lf():
    """Der Kern des Fundes: Ohne diese Zeile endet jede Shebang-Zeile unter
    Windows auf einem Wagenruecklauf, und der Aufruf stirbt mit
    'bad interpreter'."""
    regeln = _regeln()
    assert any(re.match(r"\*\.sh\s+text\s+eol=lf$", r) for r in regeln), (
        "das Fragment erzwingt fuer .sh kein LF (BL-136):\n  "
        + "\n  ".join(regeln))


def test_die_shims_bekommen_crlf():
    """Die Gegenrichtung, und sie gehoert dazu: `.cmd` liest der
    Kommandozeileninterpreter WAEHREND der Ausfuehrung zeilenweise. Bei reinem
    LF verhalten sich `goto` und Labels unzuverlaessig — sporadisch, und es
    sieht nach einem Logikfehler aus."""
    regeln = _regeln()
    for endung in ("cmd", "bat"):
        assert any(re.match(rf"\*\.{endung}\s+text\s+eol=crlf$", r)
                   for r in regeln), (
            f"das Fragment erzwingt fuer .{endung} kein CRLF (BL-136)")


def test_die_shim_regel_steht_hinter_der_sammelregel():
    """In .gitattributes gewinnt die SPAETERE Zeile. Stuende `team/**` hinter
    `*.cmd`, bekaeme eine .cmd unter team/ wieder LF — die Ausnahme waere
    stillschweigend aufgehoben."""
    regeln = _regeln()
    if not any(r.startswith("team/**") for r in regeln):
        pytest.skip("das Fragment fuehrt keine team/**-Sammelregel")
    sammel = max(i for i, r in enumerate(regeln) if r.startswith("team/**"))
    for endung in ("cmd", "bat"):
        shim = [i for i, r in enumerate(regeln) if r.startswith(f"*.{endung}")]
        assert shim and min(shim) > sammel, (
            f"die *.{endung}-Regel steht VOR der Sammelregel und wird von ihr "
            "ueberschrieben (spaetere Zeile gewinnt)")


def test_das_fragment_greift_nicht_auf_den_projektcode_ueber():
    """Die Zurueckhaltung, die `gitignore.fragment` seit jeher uebt.

    `* text=auto eol=lf` ist im Kit-Repo richtig und als Vorlage falsch: Es
    gaelte fuer den Code des Projekts mit, und ob der LF oder CRLF traegt, ist
    nicht die Entscheidung des Teams.
    """
    regeln = _regeln()
    uebergriffig = [r for r in regeln if r.split()[0] in ("*", "**")]
    assert not uebergriffig, (
        "Das Fragment regelt die Zeilenenden des GANZEN Projekts. Es darf nur "
        "die Dateiarten regeln, die das Kit mitbringt (BL-136):\n  "
        + "\n  ".join(uebergriffig))


# --- Die Installer ----------------------------------------------------------

def test_beide_installer_kennen_den_abgleich():
    """Beide Bahnen, beide Wege. Ein Abgleich, den nur ein Installer fuehrt,
    ist die Doppelbahn-Drift, gegen die der gemeinsame Harnisch steht."""
    faelle = (
        (_quelle("bash/install.sh"),
         r"^gitattributes_abgleich\(\)\s*\{",
         r"^\s*gitattributes_abgleich\s+ergaenzen\s*$",
         r"^\s*gitattributes_abgleich\s+melden\s*$"),
        (_quelle("pwsh/install.ps1"),
         r"^function Gitattributes-Abgleich\s*\{",
         r"^\s*Gitattributes-Abgleich\s+ergaenzen\s*$",
         r"^\s*Gitattributes-Abgleich\s+melden\s*$"),
    )
    for quelle, definition, ergaenzen, melden in faelle:
        text = quelle.read_text(encoding="utf-8-sig")
        assert re.search(definition, text, re.M), (
            f"{quelle.name} kennt keinen .gitattributes-Abgleich (BL-136)")
        assert re.search(ergaenzen, text, re.M), (
            f"{quelle.name} legt bei der ERSTINSTALLATION keine "
            ".gitattributes an — dann bleibt der Fall genau da, wo er war")
        assert re.search(melden, text, re.M), (
            f"{quelle.name} sieht die Datei beim UPDATE nicht an. Jedes vor "
            "BL-136 eingerichtete Projekt bekaeme die Regel damit nie: "
            "dieselbe Luecke, an der BL-133 haengt")


def test_der_abgleich_ergaenzt_nur_bei_der_erstinstallation():
    """Die Datei gehoert dem Projekt (Bauart BL-109). Beim Update wird
    gemeldet, nicht geschrieben — eine fehlende Zeile kann eine bewusst
    entfernte sein."""
    quelle = _quelle("bash/install.sh").read_text(encoding="utf-8")
    block = re.search(r"gitattributes_abgleich\(\)\s*\{.*?\n\}", quelle, re.S)
    assert block, "gitattributes_abgleich() ist nicht mehr auffindbar"
    rumpf = block.group(0)
    schreibend = re.search(r'^\s*cat .*>> "\$ZIEL/\.gitattributes"', rumpf, re.M)
    assert schreibend, "der Abgleich schreibt gar nichts — dann wirkt er nie"
    davor = rumpf[:schreibend.start()]
    assert '"$1" = "ergaenzen"' in davor, (
        "der Abgleich schreibt, ohne vorher auf den Modus zu pruefen — dann "
        "faellt er auch beim Update ueber eine Projektdatei her (BL-109)")


def test_die_meldung_nennt_das_neu_einlesen():
    """Ohne `add --renormalize` wirkt der Nachtrag erst beim naechsten Klon.

    Genau daran ist der Fund gross geworden: Die Regel war im Kit-Repo seit
    Langem da und die Wirkung trotzdem erst eine Maschine spaeter sichtbar.
    Eine Abhilfe, die den zweiten Schritt verschweigt, erzeugt denselben
    Abstand zwischen Ursache und Wirkung noch einmal.
    """
    for kandidat in ("bash/install.sh", "pwsh/install.ps1"):
        pfad = WURZEL / kandidat
        if not pfad.is_file():
            continue
        text = pfad.read_text(encoding="utf-8-sig")
        assert "add --renormalize" in text, (
            f"{kandidat} nennt `git add --renormalize` nicht — der Nachtrag "
            "wirkt sonst erst beim naechsten Klon (BL-136)")

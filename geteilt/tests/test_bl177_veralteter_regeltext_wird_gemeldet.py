#!/usr/bin/env python3
"""BL-177: Ein Projekt, das VOR BL-139/BL-140 eingezogen ist, behaelt seinen
kaputten Regeltext — und kein Update sagt das je.

DIE LUECKE, DIE BL-175 AUSGEWIESEN HAT
    `BL-139` hat die bahnabhaengigen Stellen der VORLAGEN auf Platzhalter
    gestellt, `BL-140` die Backlognummern auf `Kit-`. Beides wirkt beim
    RENDERN — also erst bei der naechsten ERSTINSTALLATION. Ein Projekt, das
    vorher eingezogen ist, behaelt seine `CLAUDE.md` unveraendert, und das
    Update fasst sie zu Recht nicht an: Sie traegt Projektarbeit.

    `TEAM.md` liess sich mit `BL-175` einfach nachziehen, weil sie keine
    Projektarbeit traegt. Bei `CLAUDE.md` geht das NICHT — und damit bleibt
    genau der Zustand stehen, gegen den `BL-139` gebaut wurde.

WARUM DAS NICHT VON SELBST AUFFAELLT
    Ein totes `ralph.sh` scheitert sichtbar. Eine falsch benannte
    Konfiguration nicht: Der Regeltext schickt jede Rolle nach
    `team.config.sh`, um `TEAM_SMOKE_TEST` nachzutragen, waehrend
    `team/lib.psm1` `team.config.ps1` liest. Der Wert wird eingetragen und nie
    gelesen — kein Abbruch, keine Meldung, der Wert wirkt einfach nicht.

    Feldbeleg (`Feld B`, `--nur-pwsh`, 2026-08-25): 4 verschiedene tote Pfade
    und 7 blanke Kit-Backlognummern in `CLAUDE.md`, ueber mehrere Updates
    hinweg — niemandem gemeldet. Jede Rolle hatte diesen Text im Systemprompt.

WAS DER FIX IST
    Beide Installer melden den Zustand beim Update: welche Pfade tot sind,
    welche Nummern blank, und die Zuordnung fuer DIESE Ablage. **Repariert
    wird nicht automatisch** (Lehre `BL-12`) — in `CLAUDE.md` steckt fremde
    Arbeit, und ein Installer, der darin ersetzt, ueberschreibt sie.

DIE ARBEITSTEILUNG DIESER DATEI
    Wie bei `BL-147`: Den LAUF fuehrt `kit-test.sh`; hier steht die
    Zusicherung am QUELLTEXT, fuer BEIDE Bahnen. Auf einer Maschine ohne
    PowerShell laesst sich die pwsh-Fassung nicht fahren (`BL-117`-Lage), ein
    statischer Vergleich laeuft ueberall.

    Dazu kommt hier eine Zusicherung, die KEINE Shell braucht und trotzdem
    das Verhalten trifft: Die Erkennungsregeln sind reine Textarbeit, also
    werden sie an echten Regeltexten nachgerechnet.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Zusammengesetzt statt geschrieben — dieselbe Erwaegung wie in test_bl139:
# Stufe 3 des Selbsttests sucht in JEDER ausgelieferten Datei nach uebrig
# gebliebenen Platzhaltern, und ein Test, der die Marke literal nennt, meldet
# sich selbst als ungefuellt.
MARKEN = tuple("".join(("{{", n, "}}"))
               for n in ("RUF", "ENDUNG", "KONFIG", "LIB", "REDTEAM"))


def _installer(name):
    """Der Installer liegt im KIT, nicht im Projekt — ein installiertes
    Projekt traegt ihn gar nicht. Fehlt er, wird uebersprungen statt falsch
    gruen gemeldet (Bauart aus test_bl147)."""
    kandidat = REPO_ROOT / ("bash" if name.endswith(".sh") else "pwsh") / name
    if not kandidat.is_file():
        pytest.skip(f"{name} liegt hier nicht (installiertes Projekt statt Kit-Ablage)")
    return kandidat.read_text(encoding="utf-8-sig")


# --------------------------------------------------------- Quelltext-Seite
@pytest.mark.parametrize("installer,funktion", [
    ("install.sh", "melde_veralteten_regeltext"),
    ("install.ps1", "Melde-VeraltetenRegeltext"),
])
def test_beide_installer_melden_den_veralteten_regeltext(installer, funktion):
    quelle = _installer(installer)
    assert funktion in quelle, (
        f"{installer} muss den veralteten Regeltext melden ({funktion}). "
        "Ohne die Meldung bleibt ein Projekt, das vor BL-139 eingezogen ist, "
        "dauerhaft mit toten Pfaden im Systemprompt jeder Rolle stehen — und "
        "NICHTS sagt es (BL-177).")
    # Der Aufruf, nicht nur die Definition: Eine Funktion, die niemand ruft,
    # ist eine Zusicherung, die niemand einloest (Bauart BL-119).
    assert quelle.count(funktion) >= 2, (
        f"{installer} definiert {funktion}, ruft sie aber nirgends auf.")


@pytest.mark.parametrize("installer", ["install.sh", "install.ps1"])
def test_die_zwei_bahnen_region_wird_ausgenommen(installer):
    """Ohne diese Ausnahme meldet der Waechter in JEDER einbahnigen Ablage
    einen Fehlalarm — der Ablage-Block nennt beide Bahnen mit Absicht. Ein
    Waechter mit Fehlalarm wird abgeschaltet, nicht befolgt (BL-143)."""
    quelle = _installer(installer)
    assert "Installiert mit dem **T.E.A.M.-Starterkit**. Ablage:" in quelle, (
        f"{installer} schneidet die Zwei-Bahnen-Region nicht aus. Sie nennt "
        "beide Bahnen mit Absicht; wer sie mitprueft, meldet in jeder "
        "einbahnigen Ablage einen Fehler, den es nicht gibt (BL-177).")


@pytest.mark.parametrize("installer", ["install.sh", "install.ps1"])
def test_der_waechter_repariert_nicht_von_selbst(installer):
    """Gegenrichtung: Der Fix darf nicht zu einem Installer fuehren, der
    CLAUDE.md selbst umschreibt. Dort steckt Projektarbeit — genau der Fall,
    an dem BL-12 einen 12-USD-Fix verloren hat."""
    quelle = _installer(installer)
    assert "BL-12" in quelle, (
        f"{installer} muss die Nicht-Reparatur an BL-12 festmachen, damit "
        "beim naechsten Umbau niemand 'das koennte der Installer doch gleich "
        "miterledigen' denkt.")


def test_die_blanken_nummern_kommen_aus_der_vorlage_nicht_aus_einer_liste():
    """Eine fest verdrahtete Nummernliste waere ab der naechsten neuen Nummer
    falsch (BL-154). Massstab ist die Vorlage selbst."""
    for installer in ("install.sh", "install.ps1"):
        quelle = _installer(installer)
        assert "CLAUDE.md.vorlage" in quelle, (
            f"{installer} muss die Kit-Nummern aus der VORLAGE lesen, nicht "
            "aus einer Liste im Installer — sonst veraltet der Waechter mit "
            "der naechsten Nummer (BL-154).")


# ------------------------------------------------------- Erkennungs-Seite
# Die Erkennung ist reine Textarbeit. Sie laesst sich hier nachrechnen, ohne
# eine Shell zu starten — und genau das macht sie auf jedem Wirt pruefbar.
PFAD = re.compile(r"(?<![\w/.\\-])(\./|\.\\)?"
                  r"((?:team/)?[A-Za-z0-9_.-]+\.(?:sh|ps1|psm1|cmd))")


def _ohne_region(text):
    auf = "Installiert mit dem **T.E.A.M.-Starterkit**. Ablage:"
    zu = "**Der `team/`-Ordner gehört der Infrastruktur"
    i = text.find(auf)
    if i < 0:
        return text
    j = text.find(zu, i)
    return text[:i] + (text[j:] if j >= 0 else "")


def test_die_vorlage_selbst_wuerde_den_waechter_nicht_ausloesen():
    """Die Gegenprobe, die den Waechter erst gueltig macht: Die AKTUELLE
    Vorlage darf keine blanke Kit-Nummer und keinen festen Bahnpfad tragen.
    Taete sie es, meldete der Waechter in jeder FRISCHEN Installation etwas —
    und waere ab dem ersten Tag Rauschen."""
    vorlage = REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage"
    if not vorlage.is_file():
        pytest.skip("Vorlage liegt hier nicht (installiertes Projekt)")
    text = _ohne_region(vorlage.read_text(encoding="utf-8-sig"))

    blank = sorted({m.group(1) for m in
                    re.finditer(r"(?<!Kit-)\b((?:BL|HM)-\d+)\b", text)})
    assert not blank, (
        "Die Vorlage traegt blanke Backlognummern: " + ", ".join(blank)
        + ". Blank gelesen meinen sie den Backlog des ZIELPROJEKTS — dort "
        "steht etwas anderes oder gar nichts (BL-140).")

    fest = sorted({m.group(2) for m in PFAD.finditer(text)
                   if m.group(2) not in ("install.sh", "install.ps1")})
    assert not fest, (
        "Die Vorlage nennt feste Bahnpfade statt Platzhalter: "
        + ", ".join(fest) + ". Sie gehoeren auf " + "/".join(MARKEN)
        + " (BL-139) — sonst rendert schon die naechste einbahnige "
        "Installation wieder tote Pfade.")


def test_der_waechter_findet_genau_die_stellen_die_das_feld_hatte():
    """Der Reproducer, an echtem Text statt an einer Attrappe: Ein Regeltext
    in der Fassung VOR BL-139 muss anschlagen, die reparierte nicht.

    Gebaut wird die alte Fassung aus der heutigen, indem die Platzhalterwerte
    der pwsh-Bahn auf die bash-Bahn zurueckgedreht werden — genau der
    Unterschied, den eine `--nur-pwsh`-Ablage von vor BL-139 hatte."""
    vorlage = REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage"
    if not vorlage.is_file():
        pytest.skip("Vorlage liegt hier nicht (installiertes Projekt)")
    roh = vorlage.read_text(encoding="utf-8-sig")

    pwsh = {MARKEN[0]: ".\\", MARKEN[1]: ".cmd", MARKEN[2]: "team.config.ps1",
            MARKEN[3]: "team/lib.psm1", MARKEN[4]: "team/redteam.ps1"}
    bash = {MARKEN[0]: "./", MARKEN[1]: ".sh", MARKEN[2]: "team.config.sh",
            MARKEN[3]: "team/lib.sh", MARKEN[4]: "team/redteam.sh"}

    def rendere(werte):
        text = roh
        for marke, wert in werte.items():
            text = text.replace(marke, wert)
        return _ohne_region(text)

    # Eine pwsh-Ablage: Was die bash-Bahn nennt, liegt dort NICHT.
    vorhanden_pwsh = {"team.config.ps1", "team/lib.psm1", "team/redteam.ps1"}

    def tot(text):
        return sorted({m.group(2) for m in PFAD.finditer(text)
                       if m.group(2) not in ("install.sh", "install.ps1")
                       and not m.group(2).endswith((".cmd", ".ps1", ".psm1"))
                       and m.group(2) not in vorhanden_pwsh})

    alt, neu = tot(rendere(bash)), tot(rendere(pwsh))
    assert alt, (
        "Der Reproducer greift nicht mehr: Eine mit bash-Werten gerenderte "
        "Vorlage muesste in einer pwsh-Ablage tote Pfade nennen. Tut sie das "
        "nicht, prueft dieser Test seit dem letzten Umbau nichts.")
    assert not neu, (
        "Mit den Werten DIESER Ablage gerendert bleiben tote Pfade stehen: "
        + ", ".join(neu) + " — dann fehlt in der Vorlage ein Platzhalter.")

#!/usr/bin/env python3
"""BL-139: In einer einbahnigen Ablage nannten die REGELTEXTE die andere Bahn —
und schickten damit jede Rolle an Dateien, die es dort nicht gibt.

DER FELDBEFUND
    `duke-itam-2026`, mit `--nur-pwsh` installiert. `CLAUDE.md` nannte **14**
    verschiedene `.sh`-Pfade, KEINER davon existierte; `TEAM.md` kam auf 23
    Nennungen. Gemessen, nicht vermutet:

        for f in $(grep -oE '[A-Za-z0-9_./-]+\\.sh' CLAUDE.md | sort -u); do
            test -e "$f" || echo FEHLT $f
        done          ->  14 von 14 fehlend

DIE TEUERSTE STELLE IST NICHT DIE AUFFAELLIGSTE
    Ein `./ralph.sh`, das es nicht gibt, scheitert sichtbar. `team.config.sh`
    nicht: Der Regeltext schickte jede Rolle dorthin, um `TEAM_SMOKE_TEST`,
    `TEAM_WEITERER_CODE` oder `TEAM_DOMAENEN` nachzutragen — waehrend
    `team/lib.psm1` `team.config.ps1` liest und das in seiner eigenen Warnung
    auch so sagt. **Zwei einander widersprechende Anweisungen im selben
    Systemprompt.** Wer der Regel folgt, legt eine Datei an, die nie gelesen
    wird: kein Abbruch, keine Meldung, der Wert wirkt einfach nicht. Bei
    `TEAM_SMOKE_TEST` heisst das, dass das Team ohne Sicherheitsnetz
    weiterlaeuft und in jedem Prompt "kein Smoke-Test konfiguriert" meldet,
    obwohl gerade einer eingetragen wurde.

WAS DER FIX IST
    Die Vorlagen tragen an den bahnabhaengigen Stellen Platzhalter (RUF,
    ENDUNG, KONFIG, LIB, REDTEAM — in doppelten geschweiften Klammern), die
    beide Installer beim Rendern fuellen. Vorbelegt ist die bash-Bahn: In der
    zweibahnigen Ablage — dem Default — bleibt der Text Byte fuer Byte der von
    vorher, nur eine Abwahl aendert etwas.

ZWEI REGIONEN BLEIBEN ABSICHTLICH LITERAL
    Die Zwei-Bahnen-Tabelle in `TEAM.md` ("Befehle im Ueberblick") und der
    Ablage-Block in `CLAUDE.md` STELLEN die Bahnen GEGENUEBER — dort ist es
    ihre Aufgabe, beide zu nennen. Dieser Test blendet genau diese zwei
    Regionen aus und prueft alles andere. Sie an ihren Ueberschriften zu
    erkennen statt an Zeilennummern ist Absicht: Zeilennummern verschieben
    sich beim naechsten Absatz, und eine Ausnahme, die dann die falsche Stelle
    schuetzt, faellt niemandem auf.

WAS DIESER TEST PRUEFT
    In einer INSTALLATION: Jeder Pfad, den CLAUDE.md oder TEAM.md ausserhalb
    dieser Regionen nennt, liegt auch wirklich da. Das ist genau der Lauf, der
    den Fund gefunden hat. Ohne ihn wandert dieselbe Luecke beim naechsten
    Vorlagen-Umbau zurueck.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Zusammengesetzt statt geschrieben: Stufe 3 des Selbsttests sucht in JEDER
# ausgelieferten Datei nach uebrig gebliebenen Platzhaltern, und ein Test, der
# die Marke literal nennt, meldet sich selbst als ungefuellt. Dieselbe Loesung
# wie in test_bl131 — und aus demselben Grund `"".join(...)` statt `+`: Der
# Compiler faltet benachbarte String-LITERALE zu einer Konstanten zusammen, die
# im .pyc dann doch wieder vollstaendig dasteht.
MARKEN = tuple("".join(("{{", n, "}}"))
               for n in ("RUF", "ENDUNG", "KONFIG", "LIB", "REDTEAM"))

# Zwei-Bahnen-Regionen, an ihrem Text erkannt.
SCHUTZ = {
    "TEAM.md": ("## Befehle im Überblick",
                "werden auf beiden Wegen identisch aufgerufen."),
    "CLAUDE.md": ("Installiert mit dem **T.E.A.M.-Starterkit**. Ablage:",
                  "**Der `team/`-Ordner gehört der Infrastruktur"),
}

# Ein Pfad, den der Text als Datei DIESES Projekts nennt. Kit-Pfade
# (`<kit-pfad>/bash/install.sh`, `team-auth-setup.sh`) sind ausgenommen: Sie
# liegen im Kit bzw. global, nicht im Zielprojekt, und ihre Abwesenheit ist
# keine Aussage ueber die Bahn.
# Der PUNKT muss in beide Teile: in die Zeichenklasse, sonst zerfaellt
# `team.config.sh` in ein `config.sh`, das es nirgends gibt — und in die
# Vorausschau nach hinten, sonst faengt derselbe Treffer mitten im Namen an.
# Der erste Entwurf hatte ihn in keinem von beiden und meldete zehn tote Pfade,
# die alle derselbe lebende waren.
PFAD = re.compile(r"(?<![\w/.\\-])(\./|\.\\)?"
                  r"((?:team/)?[A-Za-z0-9_.-]+\.(?:sh|ps1|psm1|cmd))")
KIT_PFADE = ("install.sh", "install.ps1", "team-auth-setup.sh",
             "team-auth-setup.ps1", "team-init.sh", "team-init.ps1")


def _ohne_schutzregionen(name, text):
    anfang, ende = SCHUTZ[name]
    if anfang not in text:
        return text
    i = text.index(anfang)
    j = text.index(ende, i) if ende in text[i:] else len(text)
    return text[:i] + text[j:]


def _tote_pfade(datei):
    text = _ohne_schutzregionen(datei.name,
                                datei.read_text(encoding="utf-8-sig"))
    tot = []
    for m in PFAD.finditer(text):
        rel = m.group(2)
        if rel.split("/")[-1] in KIT_PFADE:
            continue
        if not (REPO_ROOT / rel).exists():
            zeile = text.count("\n", 0, m.start()) + 1
            tot.append(f"{datei.name}:{zeile} — {m.group(0)}")
    return tot


def _regeltexte():
    return [p for p in (REPO_ROOT / "CLAUDE.md", REPO_ROOT / "TEAM.md")
            if p.is_file()]


def test_jeder_genannte_pfad_liegt_auch_da():
    dateien = _regeltexte()
    if not dateien:
        pytest.skip("keine gerenderten Regeltexte — das Kit-Repo selbst")
    tot = [z for d in dateien for z in _tote_pfade(d)]
    assert not tot, (
        "BL-139: Diese Pfade nennt der Regeltext, und es gibt sie hier nicht. "
        "Jede Rolle hat diesen Text im Systemprompt:\n  " + "\n  ".join(tot)
        + "\n\nDie bahnabhaengigen Stellen der Vorlage gehoeren auf "
        + "/".join(MARKEN) + ".")


def test_die_konfiguration_die_der_regeltext_nennt_wird_auch_gelesen():
    """Die teuerste Stelle, eigens geprueft.

    Ein toter Entrypoint scheitert sichtbar. Eine falsch benannte Konfiguration
    nicht: Der Wert wird eingetragen und nie gelesen. Genau dieser Fall stand
    im Feld in JEDEM Systemprompt.
    """
    dateien = _regeltexte()
    if not dateien:
        pytest.skip("keine gerenderten Regeltexte — das Kit-Repo selbst")
    falsch = []
    for datei in dateien:
        text = _ohne_schutzregionen(datei.name,
                                    datei.read_text(encoding="utf-8-sig"))
        for m in re.finditer(r"team\.config\.(sh|ps1)", text):
            if not (REPO_ROOT / m.group(0)).is_file():
                zeile = text.count("\n", 0, m.start()) + 1
                falsch.append(f"{datei.name}:{zeile} — {m.group(0)}")
    assert not falsch, (
        "BL-139: Der Regeltext verlangt Eintraege in einer Konfiguration, die "
        "es hier nicht gibt. Der Fehlermodus ist STILL — der Wert wird "
        "eingetragen und nie gelesen:\n  " + "\n  ".join(falsch))


def test_die_zwei_bahnen_regionen_sind_noch_da():
    """Gegenrichtung: Die Ausnahme darf nicht dadurch gruen werden, dass jemand
    die Region umbenennt — dann pruefte der Test sie zwar mit, aber die
    Absicht der Region waere verloren und niemand saehe es."""
    for datei in _regeltexte():
        anfang, ende = SCHUTZ[datei.name]
        text = datei.read_text(encoding="utf-8-sig")
        assert anfang in text and ende in text, (
            f"{datei.name}: Die Zwei-Bahnen-Region ist nicht mehr auffindbar "
            f"({anfang!r} / {ende!r}). Entweder ist sie weg — dann gehoert die "
            "Ausnahme hier geloescht — oder sie wurde umbenannt und dieser "
            "Test schuetzt seit dem Umbau die falsche Stelle.")
    if not _regeltexte():
        pytest.skip("keine gerenderten Regeltexte — das Kit-Repo selbst")

#!/usr/bin/env python3
"""BL-140: Die Regeltexte zitierten den Kit-Backlog blank — und verletzten damit
genau die Regel, die sie selbst aufstellen.

DIE REGEL, DIE IN DENSELBEN DATEIEN STEHT
    `CLAUDE.md` schreibt vor: "Verweist eine Zeile auf den Backlog eines
    ANDEREN Projekts, wird sie als `Kit-BL-<N>` geschrieben, nie als blankes
    `BL-<N>`. Der Nummernraum ist sonst doppelt belegt."

    In derselben Datei standen dann bare Verweise auf Kit-Eintraege: `BL-52`,
    `BL-51`, `BL-20`/`BL-25`, `BL-30`, `BL-115`, `HM-32`.

WAS DAS IM FELD BEDEUTET
    Ein frisches Projekt faengt seinen eigenen Backlog bei `BL-1` an, waehrend
    der Regeltext im selben Repo unter `BL-1` eine Kit-Feldlehre meint. Die
    Frage "darf mein erster Eintrag BL-1 heissen?" liess sich aus den
    Regeltexten NICHT beantworten, weil beide Lesarten dort belegt waren.
    Wer nachschlaegt — Mensch oder Rolle — landet im falschen Dokument oder
    findet nichts und haelt den Verweis fuer veraltet.

WARUM DER FIX NICHT MECHANISCH IST
    Der Backlog-Eintrag nennt ihn "mechanisch und einmalig". Er ist es nicht,
    und das hat beim Abtragen zwei Faelle gezeigt, die ein blindes
    Such-und-Ersetze KAPUTT gemacht haette:

      * `HM-7` und `AX-3` im Glossar von TEAM.md sind FORMATBEISPIELE fuer die
        Nummerierung im Beutebuch des ZIELPROJEKTS ("Traegt eine Nummer
        (`HM-7`)"). Ein `Kit-`-Praefix waere dort schlicht falsch.
      * `BL-120` im Architekten-Briefing meint WEDER das Kit NOCH das
        Zielprojekt: `Kit-BL-116` nennt als Quelle das Feldprojekt
        `Feld A` und dessen dortiges `BL-120`. Das Kit-`BL-120` ist das
        FAQ-Geruest — aus einem richtigen Verweis waere ein falscher geworden.

    Daraus folgt die Regel, die dieser Lint durchsetzt, und sie hat DREI
    Sorten statt zwei:

        blank         mein Backlog (der des Zielprojekts)
        Kit-BL-<N>    der Backlog des Kits
        <Projekt>     ein DRITTES Projekt wird BENANNT, nicht praefigiert

WAS DIESER TEST PRUEFT (Fassung seit BL-148)
    Kein blanker `BL-<N>`/`HM-<N>`, der ins Leere zeigt. Die drei Sorten oben
    sind jetzt MASCHINELL unterscheidbar, statt durch eine Liste angenaehert
    zu werden:

        (b) Die Zeile NENNT ein Projekt (in Backticks) -> kein Fund, ueberall.
        (a) Die Nummer steht im EIGENEN Backlog/Beutebuch des Projekts
            -> kein Fund, aber NUR in Projekttexten (siehe unten).
        (c) Alles andere -> Fund.

    Dazu die Ausnahmeliste, die bleibt, weil sie eine VIERTE Sorte traegt, die
    keine Regel erkennen kann: das FORMATBEISPIEL im Glossar ("Traegt eine
    Nummer (`HM-7`)"). Jede Ausnahme mit Grund — eine Ausnahmeliste ohne
    Gruende waere eine Liste von Verstoessen mit Amnestie.

WARUM (a) NICHT IN VORLAGEN GILT — der Kern von BL-148
    Ein Feldprojekt meldete: Der Lint verbietet dort genau die Schreibweise,
    die seine eigene Regel als richtig erklaert. Gemessen 24 Fundstellen in
    der projekteigenen `CLAUDE.md`; acht meinten wirklich den Kit-Backlog und
    waren nachzuziehen, drei nannten ein drittes Projekt beim Namen, die
    uebrigen DREIZEHN meinten den eigenen Backlog des Projekts — bei zweien
    stand das woertlich im Satz. Die Ausnahmeliste laesst sich dagegen nicht
    aufruesten: Sie steht in `team/tests/`, und `--update` ueberschreibt das.

    Die Trennung, die den Fall loest, ist nicht "Kit gegen Installation",
    sondern VORLAGE gegen PROJEKTTEXT:

        Vorlage      bootstrap/*, */prompts/rolle-*.md
                     Wird in ein FREMDES Projekt geliefert. Dort heisst blank
                     "der Backlog DIESES Projekts" — und der existiert zur
                     Lintzeit nicht. Eine blanke Nummer darf hier also NIE
                     gegen einen Backlog aufgeloest werden, auch nicht gegen
                     den des Kits. Genau das war BL-140.

        Projekttext  CLAUDE.md / TEAM.md in der Wurzel
                     Gehoert dem Projekt, das sie liest. Hier ist blank die
                     erste Sorte, und (a) kann sie belegen.

    Im Kit-Repo gibt es keine Projekttexte (kein CLAUDE.md, kein TEAM.md in
    der Wurzel) — dort aendert BL-148 also nichts, und das ist beabsichtigt.
"""
import re
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

# Blanke Nummer: nicht durch "Kit-" praefigiert. Der Bindestrich davor ist
# nicht-Wort, `\b` greift also auch mitten in "Kit-BL-52" — die Vorausschau
# nach hinten ist der eigentliche Filter.
BLANK = re.compile(r"(?<!Kit-)\b(BL|HM|AX)-\d+")

# Jede Ausnahme mit Grund. Schluessel ist (Dateiname, gefundene Nummer).
AUSNAHMEN = {
    ("TEAM.md", "HM-7"):
        "Formatbeispiel im Glossar: zeigt, wie eine Fundnummer im Beutebuch "
        "DIESES Projekts aussieht. Ein Kit-Praefix waere hier falsch.",
    ("TEAM.md", "AX-3"):
        "Formatbeispiel im Glossar, wie HM-7 — Axels Ermittlungsakte.",
    # BL-148: Die Ausnahme fuer rolle-architekt.md/BL-120 stand hier und ist
    # WEGGEFALLEN — nicht vergessen, sondern ueberfluessig geworden. Sie war
    # die Handarbeit fuer genau die dritte Sorte, die Sorte (b) jetzt
    # maschinell erkennt: Die Zeile nennt `Feld A` in Backticks. Dass sie
    # ersatzlos verschwinden konnte, ist der Beleg, dass die Regel traegt —
    # und der Test unten haelt genau das fest.
}


def _ausgelieferte_texte():
    """Alles, was das Kit an Regeltext in ein Projekt legt.

    Zwei Ablagen: Im Kit liegen die Vorlagen unter bootstrap/ und die
    Briefings unter geteilt/prompts/; in einer Installation sind daraus
    CLAUDE.md/TEAM.md in der Wurzel und team/prompts/ geworden.
    """
    treffer = []
    for kandidat in (REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage",
                     REPO_ROOT / "CLAUDE.md",
                     REPO_ROOT / "bootstrap" / "TEAM.md",
                     REPO_ROOT / "TEAM.md",
                     REPO_ROOT / "bootstrap" / "roadmap-skizzen.md"):
        if kandidat.is_file():
            treffer.append(kandidat)
    prompts = kit_pfad("prompts")
    if prompts.is_dir():
        treffer.extend(sorted(prompts.glob("rolle-*.md")))
    return treffer


# BL-148, Sorte (b): Die Zeile nennt ein Projekt. Erkannt wird ein Name IN
# BACKTICKS, und diese Anforderung ist Absicht — sie macht die Sorte greppbar,
# statt sie zu erraten. Zwei Schreibweisen, beide aus dem Feld belegt:
#
#     `Feld A`              das anonymisierte Kuerzel der Kit-Doku
#     `website-maxron-de`   ein Repo-Name (klein, mit Bindestrich, ohne Punkt)
#
# Der fehlende Punkt trennt Projektnamen von Dateinamen: `team-status.sh` und
# `roadmap-skizzen.md` sind keine Projekte. Grossbuchstaben trennen sie von
# Nummern: `Kit-BL-116` faellt nicht darunter.
#
# Der bewusst getragene Preis: Die Regel wirkt auf die ZEILE, nicht auf die
# Nummer. Steht in derselben Zeile ein Projektname UND ein blanker Verweis auf
# den Kit-Backlog, geht letzterer durch. Eine Aufloesung je Nummer waere nur
# mit Satzverstaendnis moeglich; die Zeile ist die groesste Einheit, die sich
# ohne Raterei pruefen laesst.
PROJEKT_IN_BACKTICKS = re.compile(
    r"`(Feld [A-Z]\d?|[a-z0-9]+(?:-[a-z0-9]+)+)`")


def _nennt_ein_projekt(zeile):
    return bool(PROJEKT_IN_BACKTICKS.search(zeile))


# Vorlagen: alles, was das Kit in ein FREMDES Projekt liefert. Fuer sie gilt
# Sorte (a) NICHT — siehe der Kopf dieser Datei.
def _ist_vorlage(datei):
    teile = datei.parts
    return "bootstrap" in teile or "prompts" in teile


def _eigene_nummern(wurzel=None):
    """Alle Nummern, die im EIGENEN Backlog/Beutebuch des Projekts stehen.

    Gelesen wird aus der Konfiguration, nicht geraten: `team.config.sh` bzw.
    `team.config.ps1` nennen TEAM_BACKLOG und TEAM_BEUTEBUCH. Fehlt beides
    (Kit-Ablage), bleibt die Menge leer — und dann ist Sorte (a) wirkungslos,
    genau wie beabsichtigt.
    """
    wurzel = wurzel or REPO_ROOT
    kandidaten = []
    for konf, muster in ((wurzel / "team.config.sh",
                          r'^(?:TEAM_BACKLOG|TEAM_BEUTEBUCH)="\$\{[^:]+:-([^}]*)\}"'),
                         (wurzel / "team.config.ps1",
                          r"^\$(?:TEAM_BACKLOG|TEAM_BEUTEBUCH)\s*=.*'([^']*)'\s*$")):
        if not konf.is_file():
            continue
        text = konf.read_text(encoding="utf-8-sig")
        kandidaten += re.findall(muster, text, re.MULTILINE)
        break
    if not kandidaten:
        # Kein team.config in dieser Ablage — die dokumentierten Vorgabewerte.
        kandidaten = ["plans/backlog.md", "plans/beutebuch.md"]
    nummern = set()
    for rel in kandidaten:
        datei = wurzel / rel
        if datei.is_file():
            nummern.update(m.group(0) for m in
                           BLANK.finditer(datei.read_text(encoding="utf-8-sig")))
    return nummern


def _funde(dateien, eigene):
    """Die eigentliche Regel, als eine Funktion — damit die Gegenproben sie
    gegen eine gebaute Ablage fahren koennen statt gegen das echte Repo."""
    funde = []
    for datei in dateien:
        text = datei.read_text(encoding="utf-8-sig")
        zeilen = text.splitlines()
        vorlage = _ist_vorlage(datei)
        for m in BLANK.finditer(text):
            nummer = m.group(0)
            if (datei.name, nummer) in AUSNAHMEN:
                continue
            nr = text.count("\n", 0, m.start()) + 1
            zeile = zeilen[nr - 1] if nr <= len(zeilen) else ""
            if _nennt_ein_projekt(zeile):
                continue                       # Sorte (b), ueberall
            if not vorlage and nummer in eigene:
                continue                       # Sorte (a), nur in Projekttexten
            funde.append(f"{datei.name}:{nr} — {nummer}: {zeile.strip()[:80]}")
    return funde


def test_kein_blanker_verweis_auf_einen_fremden_backlog():
    dateien = _ausgelieferte_texte()
    if not dateien:
        pytest.skip("keine ausgelieferten Regeltexte in dieser Ablage")
    funde = _funde(dateien, _eigene_nummern())
    assert not funde, (
        "BL-140/BL-148: Diese Verweise zeigen ins Leere. Eine blanke Nummer "
        "meint den Backlog DIESES Projekts — dort steht sie nicht. Drei Wege "
        "hinaus: `Kit-` davor, wenn der Kit-Backlog gemeint ist; den NAMEN des "
        "dritten Projekts in Backticks in dieselbe Zeile, wenn es ein drittes "
        "ist; oder den Eintrag im eigenen Backlog anlegen:\n  "
        + "\n  ".join(funde))


def test_jede_ausnahme_ist_noch_da_und_traegt_einen_grund():
    """Die Gegenrichtung. Ohne sie waere die Ausnahmeliste eine Einbahnstrasse:
    Ein geloeschter Satz laesst seinen Eintrag als stille Erlaubnis zurueck, und
    die naechste blanke Nummer an derselben Stelle faellt niemandem mehr auf.
    """
    dateien = {d.name: d.read_text(encoding="utf-8-sig")
               for d in _ausgelieferte_texte()}
    if not dateien:
        pytest.skip("keine ausgelieferten Regeltexte in dieser Ablage")
    verwaist = []
    for (name, nummer), grund in AUSNAHMEN.items():
        assert len(grund) > 40, f"Ausnahme {name}/{nummer} ohne echten Grund"
        if name not in dateien:
            continue          # andere Ablage, andere Dateien
        if not re.search(rf"(?<!Kit-)\b{re.escape(nummer)}\b", dateien[name]):
            verwaist.append(f"{name}/{nummer}")
    assert not verwaist, (
        "Diese Ausnahmen zeigen ins Leere — die Stelle gibt es nicht mehr. "
        "Eintrag loeschen, sonst erlaubt er lautlos die naechste:\n  "
        + "\n  ".join(verwaist))


def test_die_regel_steht_auch_im_regeltext():
    """Ein Lint, der eine Regel durchsetzt, die nirgends geschrieben steht,
    erzieht niemanden — er ueberrascht nur beim naechsten Textumbau."""
    for kandidat in (REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage",
                     REPO_ROOT / "CLAUDE.md"):
        if not kandidat.is_file():
            continue
        text = kandidat.read_text(encoding="utf-8-sig")
        assert "Kit-BL-" in text, (
            f"{kandidat.name} stellt die Kit-BL-Regel auf, benutzt sie aber "
            "selbst kein einziges Mal — genau der Zustand, den BL-140 "
            "beschreibt.")
        return
    pytest.skip("keine CLAUDE.md in dieser Ablage")


# --- BL-148: die Gegenproben, die die neue Regel erst gueltig machen ----------
# Gefahren gegen GEBAUTE Ablagen, nicht gegen das echte Repo. Der Grund ist der
# Fund selbst: Die Regel muss sich in einer INSTALLATION anders verhalten als
# im Kit, und das Kit-Repo kann diese Haelfte nicht zeigen — dort gibt es keine
# Projekttexte. Ein Test, der nur die eigene Ablage kennt, haette BL-148 nicht
# gefunden und wuerde ihn auch nicht fangen.

def _installation(tmp_path, claude_text, backlog_text):
    """Eine Ablage, wie sie nach einer Installation aussieht."""
    (tmp_path / "plans").mkdir(parents=True, exist_ok=True)
    (tmp_path / "CLAUDE.md").write_text(claude_text, encoding="utf-8")
    (tmp_path / "plans" / "backlog.md").write_text(backlog_text, encoding="utf-8")
    (tmp_path / "team.config.sh").write_text(
        'TEAM_PLAN_ORDNER="${TEAM_PLAN_ORDNER:-plans/}"\n'
        'TEAM_BACKLOG="${TEAM_BACKLOG:-plans/backlog.md}"\n'
        'TEAM_BEUTEBUCH="${TEAM_BEUTEBUCH:-plans/beutebuch.md}"\n',
        encoding="utf-8")
    return tmp_path / "CLAUDE.md"


EIGENER_BACKLOG = """# Backlog — Feldprojekt

| Nr | Was |
|---|---|
| BL-1 | der erste eigene Eintrag |
| BL-115 | hier entstanden |
"""


def test_eigene_nummer_im_projekttext_ist_kein_fund(tmp_path):
    """Sorte (a), der Feldfall. Dreizehn der 24 Fundstellen waren von dieser
    Art — bei zweien stand woertlich im Satz, dass die Nummer HIER entstanden
    ist."""
    datei = _installation(
        tmp_path,
        "Die Lehre ist hier als `BL-115` entstanden, siehe `BL-1`.\n",
        EIGENER_BACKLOG)
    assert _funde([datei], _eigene_nummern(tmp_path)) == []


def test_eine_nummer_die_es_im_eigenen_backlog_NICHT_gibt_bleibt_rot(tmp_path):
    """Die Gegenprobe, die der Backlog-Eintrag ausdruecklich verlangt.

    Ohne sie waere der Lint nur noch hoeflich: Er wuerde jede blanke Nummer
    durchwinken und genau den Zustand herstellen, gegen den BL-140 steht.
    """
    datei = _installation(
        tmp_path,
        "Das steht in `BL-52` — gemeint ist aber der Kit-Backlog.\n",
        EIGENER_BACKLOG)
    funde = _funde([datei], _eigene_nummern(tmp_path))
    assert len(funde) == 1 and "BL-52" in funde[0], funde


def test_in_einer_vorlage_gilt_sorte_a_nicht(tmp_path):
    """Die Zusicherung von BL-140, unangetastet.

    Dieselbe Nummer, derselbe Satz — aber in einer Datei, die in ein FREMDES
    Projekt geliefert wird. Dort heisst blank "der Backlog DIESES Projekts",
    und der existiert zur Lintzeit nicht. Wuerde (a) hier greifen, loeste der
    Lint die Nummer gegen den Backlog des KITS auf und erlaubte genau den
    Verweis, den BL-140 verboten hat.
    """
    (tmp_path / "bootstrap").mkdir(parents=True)
    datei = tmp_path / "bootstrap" / "CLAUDE.md.vorlage"
    datei.write_text("Die Lehre ist hier als `BL-115` entstanden.\n",
                     encoding="utf-8")
    funde = _funde([datei], {"BL-115"})
    assert len(funde) == 1 and "BL-115" in funde[0], (
        "Sorte (a) greift in einer Vorlage — damit ist BL-140 wieder offen: "
        f"{funde}")


@pytest.mark.parametrize("zeile,warum", [
    ("Feld-Fall `BL-120` im `Feld A`.", "das anonymisierte Kuerzel der Kit-Doku"),
    ("Dort ist es `BL-7`, siehe `website-maxron-de`.", "ein Repo-Name"),
])
def test_eine_zeile_die_ein_projekt_nennt_ist_kein_fund(tmp_path, zeile, warum):
    """Sorte (b), und sie gilt AUCH in Vorlagen — ein benanntes drittes Projekt
    ist fuer jeden Leser eindeutig, egal wo der Text landet."""
    (tmp_path / "prompts").mkdir(parents=True)
    datei = tmp_path / "prompts" / "rolle-architekt.md"
    datei.write_text(zeile + "\n", encoding="utf-8")
    assert _funde([datei], set()) == [], warum


@pytest.mark.parametrize("zeile", [
    "Der Befehl `team-status.sh` meldet `BL-30`.",
    "Siehe `roadmap-skizzen.md` zu `BL-30`.",
    "Kit-BL-116 verweist auf `BL-30`.",
])
def test_ein_dateiname_ist_kein_projektname(tmp_path, zeile):
    """Die Gegenprobe zu Sorte (b). Ohne sie waere jede Zeile mit einem
    Bindestrich in Backticks eine Freikarte — und davon gibt es im Kit
    hunderte."""
    (tmp_path / "prompts").mkdir(parents=True)
    datei = tmp_path / "prompts" / "rolle-frank.md"
    datei.write_text(zeile + "\n", encoding="utf-8")
    assert len(_funde([datei], set())) == 1, (
        f"'{zeile}' wurde als Projektnennung gelesen — Sorte (b) ist zu weit.")


def test_die_architekten_ausnahme_ist_wirklich_ueberfluessig():
    """Der Beleg fuer BL-148 an der Stelle, an der er zaehlt.

    Die Ausnahme fuer `rolle-architekt.md`/`BL-120` ist geloescht worden, weil
    Sorte (b) sie ersetzt. Faellt der Satz im Briefing irgendwann anders aus —
    etwa ohne die Backticks um `Feld A` —, muss dieser Test rot werden und
    nicht der grosse Lint, denn dort saehe es nach einem neuen Fund aus statt
    nach einer Regel, die ihren Fall verloren hat.
    """
    briefing = kit_pfad("prompts", "rolle-architekt.md")
    if not briefing.is_file():
        pytest.skip("rolle-architekt.md nicht in dieser Ablage")
    treffer = [z for z in briefing.read_text(encoding="utf-8-sig").splitlines()
               if BLANK.search(z)]
    assert treffer, "im Briefing steht keine blanke Nummer mehr — Test anpassen"
    ohne_projekt = [z for z in treffer if not _nennt_ein_projekt(z)]
    assert not ohne_projekt, (
        "Eine blanke Nummer im Architekten-Briefing nennt kein Projekt mehr. "
        "Entweder die Zeile nachziehen (Projektname in Backticks) oder die "
        "Ausnahme wieder eintragen:\n  " + "\n  ".join(ohne_projekt))


def test_ein_projektname_OHNE_backticks_bleibt_ein_fund(tmp_path):
    """Die Backtick-Pflicht ist eine Entscheidung, kein Versehen.

    Ohne sie muesste die Regel einen Projektnamen aus freier Prosa erkennen,
    und dafuer gibt es kein tragfaehiges Muster: `website-maxron-de` und
    `rollen-agnostisch` haben dieselbe Gestalt — klein, mit Bindestrich. Eine
    Regel, die beide nimmt, waere eine Freikarte fuer jede zweite Zeile des
    Kits; eine, die beide ablehnt, verloere die dritte Sorte ganz.

    Backticks aufloesen das, weil sie im Kit ohnehin Hausstil sind (`Feld A`,
    `Kit-BL-116`) und weil der Fix eine Sekunde kostet und den Text besser
    macht: Ein Projektname in Backticks ist greppbar, ein Wort in Prosa nicht.

    Gemessen am echten Feldprojekt (`Feld A`, 25 blanke Verweise in seiner
    CLAUDE.md): Die neue Regel raeumt 14 davon ohne jede Aenderung ab. Von den
    verbleibenden elf brauchen ZWEI nur diese Backticks; die anderen neun sind
    echte Funde — acht meinen den Kit-Backlog, einer zeigt ins Leere.
    """
    (tmp_path / "prompts").mkdir(parents=True)
    datei = tmp_path / "prompts" / "rolle-frank.md"
    datei.write_text("Erprobt in website-maxron-de: `BL-27`.\n", encoding="utf-8")
    funde = _funde([datei], set())
    assert len(funde) == 1, (
        "Ein Projektname ohne Backticks wurde als Sorte (b) gelesen. Dann "
        "waere auch 'rollen-agnostisch' eine Projektnennung — die Regel haette "
        f"keine Trennschaerfe mehr: {funde}")

#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (Kit-Werkzeug, von beiden Bahnen aus aufrufbar)
"""Prueft die nachrechenbaren Zusicherungen des README gegen die Wirklichkeit.

WARUM ES DIESES WERKZEUG GIBT
    Das README traegt Zahlen und Pfade, die sich wie Zusicherungen lesen, aber
    keine Mechanik hinter sich hatten. Zweimal ist genau daran etwas verrottet:

      * "62 Testdateien" und "369 Tests" standen im README, waehrend es 65 und
        476 waren. Daraufhin bekam kit-test.sh einen Waechter — der aber nur
        ZWEI feste Formulierungen kannte. Die dritte Stelle, freie Prosa mit
        "369 Regressionstests", stand danach noch Wochen falsch da.
      * `bash scripts/team-auth-setup.sh` stand als Befehl im README. Diesen
        Pfad gibt es nicht; das Skript liegt unter `bash/scripts/`. Der
        vorhandene Pfad-Waechter war NEGATIV formuliert (er verbot den alten
        Autorenmaschinen-Pfad) und konnte einen neuen falschen nicht sehen.

    Die Lehre aus beidem ist dieselbe: Ein Waechter, der eine ABSCHRIFT prueft,
    veraltet mit ihr. Geprueft wird deshalb die GATTUNG — jede Zahl, die eine
    Testzahl behauptet, und jeder Pfad, der auf das Repo zeigt.

WAS GEPRUEFT WIRD
    (1) Jede Zahl vor Regressionstests/Tests/Faelle/Testfaelle — auch die im
        Badge — gegen die gemessene Fallzahl.
    (2) Jede Zahl vor Testdateien gegen die gemessene Dateizahl.
    (3) Jede Zahl vor Dateien gegen das, was der Installer geschrieben hat.
    (4) Jeder Pfad, den das README nennt, gegen das Dateisystem des Kits.
    (5) Die Zahl der OFFENEN Backlog-Eintraege gegen die Statusspalte von
        `plans/backlog.md`.
    (6) Jedes genannte Feld-Kuerzel gegen die Herkunftstabelle des README —
        und jede Spanne `Feld A`…`Feld N` gegen das hoechste vergebene.

WARUM (5) UND (6) DAZUGEKOMMEN SIND (BL-224)
    Beim Pflegen der Doku am 2026-09-03 standen beide Gattungen falsch da, und
    kein Waechter hat es gemerkt:

      * "Offen sind 4 Eintraege" — offen waren fuenf.
      * `Feld A`…`Feld D` an DREI Stellen (README, CHANGELOG, Backlog-Kopf),
        obwohl es `Feld E` seit dem 2026-08-24 gibt.

    Beide sind nachrechenbar, beide sind es bis dahin nicht geworden. Das ist
    die Bauform von BL-198 ein zweites Mal: Der Waechter deckte die Gattungen
    ab, die er kannte, und meldete darueber hinaus nichts.

    (6) prueft ausdruecklich AUCH `CHANGELOG.md` und `plans/backlog.md`, wenn
    das README des Kits geprueft wird — dieselbe Zeile steht in allen dreien,
    und genau das ist die Abschrift, die gemeinsam veraltet. NICHT geprueft
    wird `plans/backlog-archiv.md`: Dort ist eine alte Spanne die HISTORIE
    eines abgetragenen Eintrags und kein Fehler; ein Waechter, der an einer
    richtigen Stelle rot schlaegt, wird abgeschaltet statt befolgt (BL-14).

    Die Messwerte kommen von aussen (kit-test.sh misst sie an einer FRISCHEN
    Installation). Ohne sie prueft das Werkzeug nur die Pfade — es rechnet
    bewusst nichts selbst nach, denn eine Zahl aus dem Repo waere wieder eine
    Abschrift statt einer Messung.

WARUM DIE PFADPRUEFUNG EINE AUSNAHMELISTE HAT
    Das README nennt zwei Ablagen nebeneinander: die des KITS (bash/, pwsh/,
    geteilt/ …) und die eines ZIELPROJEKTS (team/lib.sh, ./vollautomatik.sh).
    Die zweite Sorte existiert hier zu Recht nicht. Ein Waechter, der sie
    anmahnt, schlaegt an einer richtigen Stelle rot — und wird abgeschaltet
    statt befolgt. Die Regeln unten sind deshalb eng gefasst und benannt.
"""
import argparse
import re
import sys
from pathlib import Path

# BL-158: stdout/stderr ausdruecklich auf UTF-8 stellen — dieselbe Zeile, die
# `team/tools/*.py` seit BL-133 tragen, hier aber vergessen. Pythons Default
# fuer einen NICHT-Terminal-Strom ist die ANSI-Codepage der Maschine (auf einem
# deutschen Windows cp1252), und dieses Werkzeug gibt auf seiner ERFOLGS-Spur
# ein Haekchen aus. Ohne die Umstellung stirbt es also genau dann, wenn alles
# in Ordnung ist — mit UnicodeEncodeError und Exit 1. `kit-test.sh` liest das
# als "Das README steht gegen die frische Installation" und bricht ab: eine
# Kit-Meldung, die etwas voellig anderes behauptet als das, was passiert ist.
#
# Der BL-133-Waechter hat das nicht gesehen, weil er die GATTUNG
# `team/tools/*.py` prueft — und diese Datei liegt in `geteilt/`, weil der
# Installer sie nicht ins Zielprojekt kopiert. Zwei Gattungen, ein Fehler.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        # Ein umgelenkter Strom (pytest-capture) ist kein TextIOWrapper.
        pass

KIT = Path(__file__).resolve().parents[1]

# --- Zahlen -----------------------------------------------------------------
# BL-180: Eine UNQUALIFIZIERTE Zahl ist eine Aussage ueber das KIT.
#
# Der Waechter prueft absichtlich die GATTUNG statt einer Liste von Stellen —
# ein drittes "369 Regressionstests" in freier Prosa war wochenlang unbemerkt
# veraltet. Diese Strenge hat aber eine blinde Stelle gehabt: Die
# Herkunftstabelle des README beschreibt FREMDE Projekte, und deren Zahlen
# sind voellig legitime ANDERE Zahlen. Der Eintrag zu einem Feldprojekt nannte
# "86 Tests" — die Tests jenes Projekts —, der Waechter las sie als Behauptung
# ueber das Kit und schlug rot an. `kit-test.sh` Stufe 3 brach daran ab, nach
# rund 45 Minuten Laufzeit: Ein Selbsttest, der an einer RICHTIGEN Angabe
# stirbt, ist teurer als einer, der gar nicht prueft.
#
# Die naheliegende Loesung waere gewesen, die Tabelle als Region auszunehmen.
# Sie ist die schlechtere: Sie blendet aus, statt zu schaerfen, und die
# naechste fremde Zahl ausserhalb der Tabelle faellt wieder durch. Stattdessen
# muss eine Zahl ueber ein fremdes Projekt ihren TRAEGER nennen — und der
# Waechter prueft weiter JEDE unqualifizierte Zahl.
#
# Zwei Schreibweisen gelten als qualifiziert:
#
#     86 Projekt-Tests          Traeger als Praefix am Nomen
#     86 Tests in Feld E        Traeger direkt dahinter
#
# Das Praefix faellt schon durch `\d+\s+Tests` heraus (zwischen Zahl und Nomen
# steht ein Wort); der Nachsatz braucht den Ausschluss unten. "des Kits" zaehlt
# ausdruecklich NICHT als fremder Traeger — sonst liesse sich der Waechter mit
# drei Woertern abschalten.
TRAEGER = (r"(?:\s+(?:in|aus|von|im|des|der|jenes|dieses|eines)\s+"
           r"(?!Kits?\b)[`\w.\-ÄÖÜäöüß]+)")

# Reihenfolge in der Alternative zaehlt: "Regressionstests" vor "Tests", sonst
# bliebe der laengere Begriff ungeprueft.
FAELLE = [
    re.compile(r"(\d+)\s+(?:Regressionstests|Testfälle|Tests|Fälle)\b"
               r"(?!" + TRAEGER + r")"),
    re.compile(r"badge/Regressionstests-(\d+)-"),
]
TESTDATEIEN = [re.compile(r"(\d+)\s+Testdateien\b")]
DATEIEN = [re.compile(r"(\d+)\s+Dateien\b")]

# BL-198: Zwei weitere Zahlen im selben README behaupten dasselbe ueber
# dasselbe Kit und wurden von NIEMANDEM gemessen — die Spanne der vergebenen
# Backlog-Nummern und die Zahl der abgetragenen Eintraege. Eingetreten, nicht
# vermutet: Am 2026-08-26 kam BL-196 dazu, das README nannte weiter BL-195,
# und alle drei Doku-Waechter blieben gruen.
#
# Beide Sollzahlen kommen aus dem REPO und nicht aus einer Installation: Der
# Backlog des Kits wird nicht mitinstalliert.
#
# Die Spanne ist an ihrem ANFANG erkennbar und nicht an ihrem Wortlaut: Ein
# Feldbeleg nennt Spannen wie `BL-158`…`BL-168`, und die gehoeren ihrem Feld,
# nicht dem Kit (BL-180). Nur eine Spanne, die bei `BL-1` beginnt, ist eine
# Aussage ueber den Nummernraum des Kits.
HOECHSTE_BL = [re.compile(
    r"`BL-1`\s*(?:…|\.\.\.|bis|–|-)\s*`BL-(\d+)`")]
ARCHIV = [re.compile(r"backlog-archiv\.md\)[^\n]{0,60}?\((\d+) Einträge\)"),
          re.compile(r"(\d+)\s+Archiv-Einträge\b")]

# BL-224: Wie viele Eintraege OFFEN sind. Auch das ist eine Aussage ueber das
# Kit und stand am 2026-09-03 auf 4, waehrend es fuenf waren.
#
# Der Sollwert kommt aus der Statusspalte von `plans/backlog.md` und nicht aus
# der Zeilenzahl: In derselben Tabelle stehen abgetragene Zeilen, die noch
# nicht ins Archiv verschoben sind — am Fundtag 13 von 18. Wer die Zeilen
# zaehlt, misst etwas anderes als das, was das README behauptet.
OFFEN = [re.compile(r"Offen sind (\d+) Einträge\b"),
         re.compile(r"(\d+)\s+offene\s+(?:Backlog-)?Einträge\b")]

# Das Merkwort am Anfang der Statuszelle. Kleingeschrieben, ohne Fettmarken
# und ohne Satzzeichen — mehr Form wird nicht verlangt, damit die Regel eine
# gewachsene Tabelle nicht umschreibt (der Rest der Zelle bleibt freie Prosa).
STATUS_OFFEN = ("offen", "teilweise")
STATUS_ZU = ("erledigt", "abgetragen", "verworfen", "zurückgestellt")

# --- Feld-Kuerzel -----------------------------------------------------------
# Die Herkunftstabelle des README ist die einzige Stelle, an der ein Kuerzel
# DEFINIERT wird. Alles andere zitiert sie.
FELD_ZEILE = re.compile(r"^\|\s*\*\*`Feld ([A-Z]\d?)`\*\*\s*\|", re.M)
FELD_NENNUNG = re.compile(r"`Feld ([A-Z]\d?)`")
# Eine Spanne erkennt man an ihrem ANFANG — `Feld A`. Dieselbe Ueberlegung wie
# bei HOECHSTE_BL: Nur eine Spanne, die bei A beginnt, redet ueber den ganzen
# Vorrat an Kuerzeln.
FELD_SPANNE = re.compile(
    r"`Feld A`\s*(?:…|\.\.\.|bis|–|-)\s*`Feld ([A-Z]\d?)`")

# Wo dieselbe Zeile sonst noch steht. Das Archiv fehlt hier mit Absicht — dort
# ist eine alte Spanne die Historie eines abgetragenen Eintrags.
MITGEPRUEFT = ("CHANGELOG.md", "plans/backlog.md")

# Beim ersten Lauf sofort eingetreten, und die Meldung war BERECHTIGT und
# trotzdem falsch: Der CHANGELOG nennt `Feld A`…`Feld D` in einer
# ABGESCHLOSSENEN Version — dort beschreibt der Satz den Stand von damals.
# Eine geschnittene Version ist eingefroren wie das Archiv; wer sie nachzieht,
# schreibt Historie um. Geprueft wird deshalb nur der LEBENDE Teil: Kopf und
# `[Unreleased]`, also alles vor der ersten Versionsueberschrift.
VERSION_UEBERSCHRIFT = re.compile(r"^## \[\d", re.M)

# BL-225: Die Dateizahl einer frischen Installation steht nicht nur im README.
# `doku/einrichtung.md` nennt sie in der Uebersichtstabelle ganz oben — und
# stand am 2026-09-03 auf 136, waehrend der Installer 189 schrieb. 53 Dateien
# Unterschied, in der ersten Bildschirmhoehe der Einrichtungsanleitung.
#
# Warum NUR die Dateizahl und NUR diese Datei: Der Belegstand in
# `einrichtung.md` nennt absichtlich HISTORISCHE Testzahlen ("160 der 487
# Tests fielen") — die Testzahl-Gattung dort mitzupruefen hiesse, an einer
# richtigen Stelle rot zu schlagen (BL-14). Und der lebende CHANGELOG-Teil wie
# der Backlog nennen ihrerseits Dateizahlen aus anderem Anlass. Geprueft wird
# deshalb genau eine Gattung in genau einer weiteren Datei, und beides ist hier
# benannt statt gewachsen.
DATEIZAHL_MITGEPRUEFT = ("doku/einrichtung.md",)


def lebender_teil(name, text):
    """Der Teil einer Datei, der noch geschrieben wird (BL-224)."""
    if name != "CHANGELOG.md":
        return text
    m = VERSION_UEBERSCHRIFT.search(text)
    return text[:m.start()] if m else text

# --- Pfade ------------------------------------------------------------------
PFAD_ENDUNG = re.compile(r"\.(?:sh|ps1|psm1|py|md|cmd|webp|svg)$")

# Jede Regel sagt, WARUM der Pfad hier nicht existieren muss. Eine Ausnahme
# ohne Grund waere eine Erlaubnis mit unbekanntem Umfang.
UEBERSPRUNGEN = (
    ("~",   "liegt im Home des Anwenders, nicht im Repo"),
    ("<",   "Platzhalter-Syntax wie <kit>/bash/install.sh"),
    ("./",  "Entrypoint eines ZIELPROJEKTS — im Kit liegt er unter bash/entry/"),
    ("../", "Schwester-Repo ausserhalb des Kits"),
    ("team/",  "Namensraum eines ZIELPROJEKTS — im Kit heisst er geteilt/ bzw. bash/"),
    ("team\\", "dasselbe auf der pwsh-Bahn"),
)


def _pfad_tokens(text):
    """Alles, was im README wie ein Pfad aussieht: Backticks und Link-Ziele."""
    tok = set()
    for m in re.finditer(r"`([^`\n]+)`", text):
        for wort in m.group(1).split():
            # Nur Randzeichen, NICHT den Punkt: sonst wird aus "./ralph.sh"
            # ein "/ralph.sh" und die ./-Regel unten greift nie. Ein
            # nachgestellter Punkt faellt ohnehin durch PFAD_ENDUNG.
            wort = wort.strip("(),;:")
            if "/" in wort and PFAD_ENDUNG.search(wort):
                tok.add(wort)
    for m in re.finditer(r"\]\(([^)\s]+)\)", text):
        ziel = m.group(1).split("#")[0]
        if ziel and not ziel.startswith(("http://", "https://", "mailto:")):
            tok.add(ziel)
    return tok


def pruefe_pfade(text):
    fehler = []
    for tok in sorted(_pfad_tokens(text)):
        if "*" in tok:
            continue  # ein Glob beschreibt eine Menge, keinen Pfad
        if any(tok.startswith(p) for p, _ in UEBERSPRUNGEN):
            continue
        if not (KIT / tok).exists():
            fehler.append(f"README nennt `{tok}` — im Kit gibt es das nicht.")
    return fehler


# Der BL-180-Hinweis passt nur auf ZAEHLBARES ("86 Testfälle in Feld E"). Fuer
# die Spanne der Backlog-Nummern ergaebe er Kauderwelsch, und ein Hinweis, der
# nicht zur Meldung passt, wird ueberlesen wie eine Warnung, die immer kommt.
FREMD_HINWEIS = (
    "    Gemeint war die Zahl eines FREMDEN Projekts? Dann muss sie ihren "
    "Träger nennen — »86 Projekt-{was}« oder »86 {was} in Feld E« (BL-180). "
    "Eine unqualifizierte Zahl ist eine Aussage über das Kit.")


def pruefe_zahlen(text, soll, muster, was, fremd_hinweis=True, verlangt=True,
                  quelle="README"):
    """Prueft jede Zahl der Gattung; `verlangt` steuert nur den LEERFALL.

    BL-198/BL-180, im Selbsttest zusammengestossen: Der Leerfall ("die Zahl
    steht ueberhaupt nicht mehr da") ist eine Aussage ueber das README DES
    KITS. Das Werkzeug wird aber ausdruecklich auch auf FREMDE Dateien
    gerichtet — `--readme` auf eine Gegenprobe-Kopie, auf ein Fixture, auf ein
    Zielprojekt. Dort ist eine fehlende Kit-Zahl kein Befund, sondern der
    Normalfall, und ein Waechter, der an einer richtigen Datei rot schlaegt,
    wird abgeschaltet statt befolgt (Bauart BL-180).

    Ein FALSCHER Wert bleibt ueberall rot — daran aendert der Schalter nichts.
    Rueckgabe: (fehler, gesehen), damit der Aufrufer nicht behaupten muss,
    etwas gemessen zu haben, das gar nicht dastand.
    """
    fehler, gesehen = [], 0
    for rx in muster:
        for m in rx.finditer(text):
            gesehen += 1
            if int(m.group(1)) != soll:
                # Der zitierte Fund wird auf EINE Zeile normalisiert: Die
                # Spanne darf im README ueber einen Zeilenumbruch laufen, und
                # eine Fehlermeldung mit eingebettetem Umbruch liest sich wie
                # zwei Befunde.
                meldung = (f"{quelle} behauptet {m.group(1)} {was}, gemessen "
                           f"sind {soll} (»{' '.join(m.group(0).split())}«).")
                if fremd_hinweis:
                    meldung += "\n" + FREMD_HINWEIS.format(was=was)
                fehler.append(meldung)
    if gesehen == 0 and verlangt:
        fehler.append(f"{quelle} nennt die {was} ueberhaupt nicht mehr — "
                      f"eine Zusicherung, die verschwindet, faellt nicht auf.")
    return fehler, gesehen


def backlog_zahlen():
    """Die zwei Zahlen, die aus dem REPO kommen und nicht aus einer Installation.

    Der Backlog des Kits wird nicht mitinstalliert — wer diese Sollwerte an
    einer frischen Installation messen wollte, faende nichts. Sie werden
    deshalb hier abgeleitet, in einer Zeile je Gattung, statt in beiden
    Selbsttests noch einmal (BL-198).

    Rueckgabe: (archiv_eintraege, hoechste_bl) — je None, wenn die Datei fehlt.
    """
    zeile = re.compile(r"^\| BL-(\d+) ", re.M)
    archiv_datei = KIT / "plans" / "backlog-archiv.md"
    backlog_datei = KIT / "plans" / "backlog.md"
    archiv = hoechste = None
    nummern = []
    if archiv_datei.is_file():
        treffer = zeile.findall(archiv_datei.read_text(encoding="utf-8"))
        archiv = len(treffer)
        nummern += [int(n) for n in treffer]
    if backlog_datei.is_file():
        nummern += [int(n) for n in
                    zeile.findall(backlog_datei.read_text(encoding="utf-8"))]
    if nummern:
        hoechste = max(nummern)
    return archiv, hoechste


def backlog_offen():
    """Wie viele Eintraege in `plans/backlog.md` offen sind (BL-224).

    Gelesen wird das MERKWORT am Anfang der Statusspalte, nicht die Prosa
    dahinter — `offen`, `teilweise`, `erledigt`. Alles andere ist
    UNENTSCHEIDBAR und wird namentlich gemeldet, statt geraten: Eine Zelle wie
    "Befund 1 erledigt …, Befund 2 bleibt offen" ist fuer einen Leser klar und
    fuer einen Zaehler nicht, und ein Zaehler, der sich hier auf ein `in`
    verlaesst, zaehlt jede Zelle mit, die das Wort irgendwo erwaehnt.

    Die Statuszelle ist die LETZTE der Zeile. Steht ausgerechnet in ihr ein
    `|`, faellt der Eintrag in den unentscheidbaren Zweig — laut und mit Namen.
    Das ist die gewollte Richtung: lieber eine Meldung zu viel als eine Zahl,
    die aus einer verrutschten Spalte stammt (BL-160).

    Rueckgabe: (offen, unentscheidbar) — (None, []), wenn die Datei fehlt.
    """
    datei = KIT / "plans" / "backlog.md"
    if not datei.is_file():
        return None, []
    offen, unentscheidbar = 0, []
    for zeile in datei.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(BL-\d+)\s*\|", zeile)
        if not m:
            continue
        zelle = zeile.rstrip().rstrip("|").rsplit("|", 1)[-1]
        wort = zelle.strip().lstrip("*_ ").split(" ")[0].strip("*.,;:—–-").lower()
        if wort in STATUS_OFFEN:
            offen += 1
        elif wort not in STATUS_ZU:
            unentscheidbar.append(m.group(1))
    return offen, unentscheidbar


def feld_kuerzel():
    """Die Kuerzel, die die Herkunftstabelle des README DEFINIERT (BL-224)."""
    datei = KIT / "README.md"
    if not datei.is_file():
        return set()
    return set(FELD_ZEILE.findall(datei.read_text(encoding="utf-8")))


def pruefe_feldkuerzel(text, definiert, quelle):
    """Jede Nennung gegen die Tabelle, jede Spanne gegen das hoechste Kuerzel.

    Ohne Definitionen wird NICHT geprueft — eine fremde Datei neben einem Kit
    ohne Herkunftstabelle ist kein Befund (dieselbe Lockerung wie bei den
    Backlog-Zahlen, BL-180). Der Leerfall selbst wird vom Aufrufer geprueft.
    """
    if not definiert:
        return []
    hoechstes = max(definiert)
    fehler = []
    for kuerzel in sorted(set(FELD_NENNUNG.findall(text))):
        if kuerzel not in definiert:
            fehler.append(
                f"{quelle} nennt `Feld {kuerzel}` — die Herkunftstabelle des "
                f"README kennt nur {', '.join('`Feld ' + k + '`' for k in sorted(definiert))}.")
    for ende in set(FELD_SPANNE.findall(text)):
        if ende != hoechstes:
            fehler.append(
                f"{quelle} nennt die Spanne »`Feld A`…`Feld {ende}`«, vergeben "
                f"sind Kürzel bis `Feld {hoechstes}` — eine Spanne, die zu "
                f"frueh endet, schliesst ein Feld aus dem Beleg aus.\n"
                "    War ein RUECKBLICK gemeint? Dann ausschreiben (»endete "
                "bei `Feld D`«) statt der Spannenform: Im lebenden Text ist "
                "eine Spanne ab `Feld A` immer eine Aussage ueber HEUTE, und "
                "ein Waechter, der das erraten muesste, raet (BL-224).")
    return fehler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default=str(KIT / "README.md"))
    ap.add_argument("--faelle", type=int)
    ap.add_argument("--testdateien", type=int)
    ap.add_argument("--dateien", type=int)
    # BL-198: Die zwei Backlog-Zahlen misst der Pruefer SELBST, sonst muesste
    # jeder Aufrufer sie ableiten und jeder koennte es anders. Ein Schalter
    # dagegen bleibt: `--ohne-backlog-zahlen` fuer den Fall, dass der Backlog
    # nicht danebenliegt (eine installierte Ablage).
    ap.add_argument("--ohne-backlog-zahlen", action="store_true")
    a = ap.parse_args()

    text = Path(a.readme).read_text(encoding="utf-8")
    # NUR am README des Kits ist eine FEHLENDE Zusicherung ein Befund; ein
    # falscher WERT bleibt ueberall rot (BL-198/BL-180). Die Unterscheidung
    # braucht seit BL-224 auch der Feld-Kuerzel-Teil, deshalb steht sie hier
    # oben statt im Backlog-Block.
    ist_kit_readme = (Path(a.readme).resolve() == (KIT / "README.md").resolve())
    fehler = pruefe_pfade(text)
    gemessen = []
    # Die drei gemessenen Gattungen VERLANGT der Aufrufer selbst: Wer
    # `--faelle` uebergibt, sagt damit, dass diese Datei die Zahl tragen soll.
    # Die zwei Backlog-Zahlen misst der Pruefer dagegen ungefragt — sie duerfen
    # deshalb nur dort eingefordert werden, wo sie hingehoeren (siehe unten).
    if a.faelle is not None:
        neu, _ = pruefe_zahlen(text, a.faelle, FAELLE, "Testfälle")
        fehler += neu
        gemessen.append(f"{a.faelle} Testfälle")
    if a.testdateien is not None:
        neu, _ = pruefe_zahlen(text, a.testdateien, TESTDATEIEN, "Testdateien")
        fehler += neu
        gemessen.append(f"{a.testdateien} Testdateien")
    if a.dateien is not None:
        neu, _ = pruefe_zahlen(text, a.dateien, DATEIEN, "installierten Dateien")
        fehler += neu
        gemessen.append(f"{a.dateien} installierte Dateien")
        # BL-225: dieselbe Zahl, eine Datei weiter. `verlangt=False` — ein
        # FALSCHER Wert ist rot, ein fehlender ist es nicht: Ob die Anleitung
        # die Zahl ueberhaupt nennen will, ist ihre Entscheidung.
        if ist_kit_readme:
            for weiterer in DATEIZAHL_MITGEPRUEFT:
                pfad = KIT / weiterer
                if pfad.is_file():
                    neu, gesehen = pruefe_zahlen(
                        pfad.read_text(encoding="utf-8"), a.dateien, DATEIEN,
                        "installierten Dateien", verlangt=False,
                        quelle=weiterer)
                    fehler += neu
                    if gesehen:
                        gemessen.append(f"dieselbe Zahl in {weiterer}")
    if not a.ohne_backlog_zahlen:
        # NUR am README des Kits ist eine FEHLENDE Backlog-Zahl ein Befund.
        # `--readme` zeigt regelmaessig woanders hin: auf die Gegenprobe-Kopie
        # beider Selbsttests, auf ein Fixture, auf ein Zielprojekt. Ein
        # falscher WERT bleibt auch dort rot — das ist die Zusicherung, auf
        # die es ankommt (BL-198); nur das Einfordern entfaellt (BL-180).
        archiv, hoechste = backlog_zahlen()
        if archiv is not None:
            neu, gesehen = pruefe_zahlen(text, archiv, ARCHIV,
                                         "Archiv-Einträge",
                                         verlangt=ist_kit_readme)
            fehler += neu
            # Nur nennen, was WIRKLICH dastand: Eine Erfolgszeile, die eine
            # nicht vorhandene Zahl als "gemessen" auffuehrt, ist dieselbe
            # Falschaussage, gegen die dieser Eintrag geschrieben ist.
            if gesehen:
                gemessen.append(f"{archiv} Archiv-Einträge")
        if hoechste is not None:
            neu, gesehen = pruefe_zahlen(text, hoechste, HOECHSTE_BL,
                                         "als höchste vergebene BL-Nummer",
                                         fremd_hinweis=False,
                                         verlangt=ist_kit_readme)
            fehler += neu
            if gesehen:
                gemessen.append(f"höchste Nummer BL-{hoechste}")
        # BL-224, die dritte selbst gemessene Zahl. Sie kommt aus der
        # Statusspalte und nicht aus der Zeilenzahl: In `plans/backlog.md`
        # stehen auch abgetragene Zeilen, die noch nicht ins Archiv
        # verschoben sind.
        offen, unentscheidbar = backlog_offen()
        if unentscheidbar and ist_kit_readme:
            # Erst melden, was nicht zaehlbar war — sonst prueft der naechste
            # Block eine Zahl gegen eine Summe mit Loechern.
            fehler.append(
                "Die Statusspalte von `plans/backlog.md` ist bei "
                + ", ".join(unentscheidbar)
                + " nicht entscheidbar: Die Zelle muss mit einem Merkwort "
                  "beginnen (`offen`, `teilweise`, `erledigt`), danach darf "
                  "jede Prosa stehen. Geraten wird hier nicht (BL-224).")
        elif offen is not None and not unentscheidbar:
            neu, gesehen = pruefe_zahlen(text, offen, OFFEN,
                                         "offene Backlog-Einträge",
                                         fremd_hinweis=False,
                                         verlangt=ist_kit_readme)
            fehler += neu
            if gesehen:
                gemessen.append(f"{offen} offene Einträge")

    # BL-224: Die Feld-Kuerzel. Sie haengen an keinem Schalter — die
    # Herkunftstabelle des README definiert sie, und wer sie zitiert, zitiert
    # eine Abschrift. Am 2026-09-03 stand `Feld A`…`Feld D` an drei Stellen,
    # obwohl es `Feld E` seit dem 2026-08-24 gibt.
    definiert = feld_kuerzel()
    fehler += pruefe_feldkuerzel(text, definiert, "README")
    if ist_kit_readme:
        if not definiert and FELD_NENNUNG.search(text):
            fehler.append(
                "Das README nennt Feld-Kürzel, aber die Herkunftstabelle gibt "
                "keine her — der Sollwert ist damit unlesbar, und ein "
                "ungeprüftes Kürzel ist schlimmer als ein gemeldetes.")
        for weiterer in MITGEPRUEFT:
            pfad = KIT / weiterer
            if pfad.is_file():
                fehler += pruefe_feldkuerzel(
                    lebender_teil(weiterer,
                                  pfad.read_text(encoding="utf-8")),
                    definiert, weiterer)
        if definiert:
            gemessen.append(f"Feld-Kürzel bis `Feld {max(definiert)}`")

    if fehler:
        for f in fehler:
            print(f"  ✗ {f}", file=sys.stderr)
        return 1
    # BL-198, die schaerfere Haelfte: Die Schlusszeile sagt, WAS sie geprueft
    # hat. Vorher stand hier unbedingt "alle Zahlen sind gemessen" — auch bei
    # einem Aufruf ohne Argumente, bei dem KEINE einzige Zahlenpruefung lief.
    # Das ist die Gattung von BL-145: Zwei Aufrufwege desselben Skripts sichern
    # verschieden viel zu und melden dasselbe Gruen.
    # BL-208: Und die Schlusszeile sagt jetzt auch, GEGEN WAS gemessen wurde.
    # Der Prüfer nimmt die Zahlen vom Aufrufer entgegen und kann von sich aus
    # nicht wissen, ob sie aus dem Kit oder aus einer Installation stammen —
    # und die beiden zählen VERSCHIEDEN. Gemessen am 2026-08-28: Kit-Ablage
    # 1054 Fälle, frische Installation 1053. Die Differenz ist genau ein Fall
    # (`test_kit_pruefer_ueberlebt_eine_cp1252_ausgabe` ist über
    # `geteilt/kit-*.py` parametrisiert; in einer Installation gibt es
    # `geteilt/` nicht). Wer von Hand nachmisst, misst im Kit und liegt um
    # eins daneben — genau so kam die falsche Zahl ins README.
    print("✓ README: alle genannten Pfade existieren.")
    if gemessen:
        print("  Gemessen und deckungsgleich: " + ", ".join(gemessen) + ".")
        print("  Maßstab sind die Zahlen des AUFRUFERS; die Selbsttests messen "
              "an einer\n  frischen INSTALLATION, nicht an der Kit-Ablage — "
              "die beiden zählen verschieden (BL-208).")
    else:
        print("  KEINE Zahl geprüft — dieser Aufruf sichert nur die Pfade zu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteilter Zustandscode, bewusst nicht portiert)
"""zitat_lint.py — meldet Plandateien, die einen ERLEDIGTEN Backlog-Eintrag
als offene Frage zitieren (BL-50, Stufe 2).

Der Closeout pflegt den Backlog; nichts pflegte die Stellen, die ihn ZITIEREN.
Die Kandidatenliste, aus der die naechste Kaskade gewaehlt wird, begruendet
ihre offenen Fragen mit Backlog-Nummern — und veraltet still in dem Moment, in
dem der zitierte Eintrag erledigt wird. Der Fehler schlaegt an der teuersten
Stelle zu: beim Vorlegen der Kandidaten, also nachdem der Architekt eine Option
formuliert hat, die es nicht mehr gibt.

Feld-Beleg: Ein Kandidat begruendete sich mit "`Hurt.knockout()` wartet auf
einen Ausloeser (`BL-80`)" — `BL-80` stand da seit drei Kaskaden im Archiv,
abgetragen mit ausfuehrlicher Begruendung.

WARUM DIESER LINT SO SCHMAL IST

Ein roher Lauf ueber alle `BL-<N>`-Referenzen hatte im Probelauf ~40 %
Trefferquote (sechs von zehn Markierungen waren legitime Rueckblicke:
Verweistabellen, Statuskorrekturen, Meldezeilen). Roh ausgeliefert waere er die
Falle aus BL-14 — eine Warnung, die bei jedem Aufruf erscheint und zum
Wegsehen erzieht. Deshalb zwei Beschraenkungen, beide aus dem Probelauf:

  1. **Nur Zitate in ZUKUNFTSFORM.** Gemeldet wird eine Referenz nur, wenn im
     selben Absatz ein Wort steht, das eine noch offene Erwartung ausdrueckt
     ("wartet auf", "offen", "noch nicht", "sobald", "geplant", "fehlt").
     Ein Rueckblick ("erledigt mit BL-80", "siehe BL-80") faellt heraus.
  2. **`Kit-BL-<N>` wird uebersprungen.** Der Nummernraum ist zwischen Kit und
     Feldprojekten geteilt; ohne diese Regel meldete der Probelauf prompt die
     frisch geschriebene Meldezeile "gemeldet ans Kit als `BL-49`" als
     veraltetes Zitat, weil er die Kit-Nummer im Projekt-Backlog nachschlug.

Aufruf:
  zitat_lint.py [--backlog DATEI] [--archiv DATEI] [PLANDATEI...]

Exit 0 = nichts gefunden · 3 = Befunde (auf stderr) · 1 = Bedienfehler.
Bewusst KEIN harter Blocker: Der Lint urteilt ueber Prosa.
"""
import os
import re
import sys
from pathlib import Path

# BL-133: Die AUSGABE dieses Werkzeugs ist UTF-8 — unabhaengig von der Locale
# des Wirts.
#
# Gelesen und geschrieben wird hier ueberall mit ausdruecklichem
# `encoding="utf-8"` (BL-113, BL-129). Fuer stdout/stderr galt weiter Pythons
# Default, und der ist unter Windows die ANSI-Codepage der Maschine — auf einem
# deutschen System cp1252. Ein "an Frank uebergeben" verliess das Werkzeug
# damit als cp1252-Bytes; jeder Aufrufer im Kit liest UTF-8 und bekam an der
# Stelle des Umlauts ein Ersatzzeichen. Der Vergleich mit dem Statuswert aus
# dem Beutebuch schlug dann fehl, und `frank.sh` meldete "Kein Fund mit Status
# 'an Frank uebergeben'" — vor einem Beutebuch, in dem genau der stand.
#
# Warum hier und nicht per PYTHONIOENCODING: Das muesste jeder Aufrufer setzen
# (lib.sh, lib.psm1, die Entrypoints, der Harnisch, der Mensch auf der
# Kommandozeile). Eine Zusicherung, die an fuenf Stellen wiederholt werden
# muss, ist eine, die eine Stelle vergisst.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        # Ein umgelenkter Strom (pytest-capture) ist kein TextIOWrapper. Er
        # ist dann auch nicht das Problem, gegen das dieser Block steht.
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKLOG = REPO_ROOT / "plans" / "backlog.md"
ARCHIV = REPO_ROOT / "plans" / "backlog-archiv.md"

# `BL-12`, nicht `Kit-BL-12` — das Lookbehind haelt fremde Nummernraeume drau3en.
REFERENZ_RE = re.compile(r"(?<!Kit-)\bBL-(\d+)\b")
# Der Status ist das LETZTE Feld einer Backlog-Zeile. Codespans koennen ein
# `|` enthalten (BL-16), deshalb werden sie vor dem Zerlegen maskiert.
ZEILE_RE = re.compile(r"^\|\s*BL-(\d+)\s*\|")
ERLEDIGT_RE = re.compile(r"\*\*(erledigt|überholt|teilweise erledigt)", re.I)

# Wendungen, die eine NOCH OFFENE Erwartung ausdruecken. Nur in ihrer Naehe
# wird ein Zitat ueberhaupt bewertet (siehe Kopf).
#
# Die Liste ist bewusst SCHMAL und aus einem Fehlschlag entstanden: Ein erster
# Anlauf enthielt das blosse Wort "offen" und meldete daraufhin drei
# Rueckblicke im eigenen Roadmap-Dokument des Kits ("die beiden Entscheide,
# die offen waren", "Offen geblieben: …" ueber eine laengst gebaute Sache) —
# also genau die ~40-%-Trefferquote, die BL-50 als Grund nennt, diesen Lint
# NICHT roh auszuliefern. Lieber ein Befund weniger als eine Warnung, die man
# wegsieht (BL-14): Was hier durchrutscht, faellt spaetestens beim naechsten
# Vorlegen auf; eine Dauerwarnung faellt nie wieder auf.
ZUKUNFT = (
    "wartet auf", "wartet noch", "noch nicht", "noch offen", "bleibt offen",
    "ist offen", "steht aus", "ausstehend", "blockiert", "sobald",
    "erst wenn", "fehlt noch", "sind offen",
)
# Mit WORTGRENZEN, nicht als blosse Teilzeichenkette: Ohne \b traf "steht aus"
# das Wort "entsteht aus" und meldete prompt einen Rueckblick im eigenen
# Roadmap-Dokument. Ein Lint, der an seiner eigenen Doku falsch anschlaegt,
# hat schon verloren.
ZUKUNFT_RE = re.compile(
    "|".join(r"\b" + re.escape(w) + r"\b" for w in ZUKUNFT), re.I)

# BL-184: Die VORBEDINGUNGS-Bauform — als eigenes, engeres Muster neben der
# Wortliste, ausdruecklich NICHT als weiterer Eintrag darin.
#
# Der Fund: Die Zeile "**Vorbedingung fuer den ersten Bump:** `BL-6` muss
# vorher erledigt sein" wurde nach dem Abtragen von `BL-6` NICHT gemeldet —
# Exit 0, gezielt auf die Datei angesetzt, nachgemessen statt vermutet. Das ist
# die natuerlichste deutsche Bauform fuer eine offene Abhaengigkeit, und sie
# stand in einem Abschluss-Protokoll, also genau in dem Dokument, das beim
# Vorbereiten der Auslieferung gelesen wird.
#
# WARUM NICHT EINFACH DIE WORTLISTE ERWEITERN: Das war laut Werkzeugkopf schon
# einmal die falsche Antwort — das blosse Wort "offen" brachte drei
# Fehltreffer im eigenen Roadmap-Dokument. Diese Wendungen sind dagegen
# spezifisch: Sie benennen eine Abhaengigkeit, und in einem RUECKBLICK kommen
# sie kaum vor. Als Regex und nicht als Wortliste, weil zwischen "muss" und
# "erledigt sein" der Bezug steht, der die Wendung ueberhaupt ausmacht.
# AUSDRUECKLICH NICHT das blosse Wort "Vorbedingung": Der erste Entwurf hatte
# es, und der eigene Gegenprobe-Fall dieses Tests fiel sofort darueber — "Die
# Vorbedingung WAR `BL-6`, und sie ist mit Stufe 5 erfuellt" ist ein
# Rueckblick und wurde als offenes Zitat gemeldet. Dieselbe Falle wie damals
# beim blossen "offen", nur eine Runde spaeter. Gemeldet wird deshalb nur die
# KONSTRUKTION, in der die Abhaengigkeit noch aussteht; der Feldfall
# ("Vorbedingung fuer den ersten Bump: `BL-6` muss vorher erledigt sein")
# traegt sie ohnehin mit "muss … erledigt sein".
VORBEDINGUNG_RE = re.compile(
    r"\bmuss\b[^.!?]{0,80}?"
    r"\b(?:erledigt|abgetragen|behoben|fertig)\s+(?:sein|ist)\b"
    r"|\bsetzt\b[^.!?]{0,80}?\bvoraus\b"
    r"|\bsolange\b[^.!?]{0,80}?\bnicht\b"
    r"|\bh(?:ae|ä)ngt\s+(?:an|von)\b",
    re.I)

# Abkuerzungen, deren Punkt KEIN Satzende ist. Ohne sie zerschneidet der
# Satzsplitter "z. B." und "d. h." mitten im Bezug — und ein zu frueh
# abgeschnittener Satz verliert genau den Treffer, den BL-184 einklagt.
_ABK = r"(?<!\bz)(?<!\bB)(?<!\bd)(?<!\bh)(?<!\bu)(?<!\ba)(?<!\bs)(?<!\bggf)" \
       r"(?<!\bbzw)(?<!\bca)(?<!\bvgl)(?<!\bNr)(?<!\bAbs)(?<!\bevtl)"

# Satzgrenze: Punkt/Ruf/Frage + Leerraum, ODER ein neuer Listenpunkt.
# Listenpunkte zaehlen mit, weil eine Aufzaehlung in Markdown genau die
# Einheit ist, in der eine Aussage steht — ein Absatz kann zehn davon tragen.
SATZ_RE = re.compile(_ABK + r"[.!?]\s+|\n(?=\s*(?:[-*+]|\d+\.)\s)|\n(?=#)")


def saetze(absatz):
    """Der Absatz, zerlegt in Saetze — die Einheit, in der der BEZUG gilt.

    BL-184, der ergiebigste Einzelschritt: Bewertet wurde bis hierher der
    ABSATZ. Ein Zukunftswort irgendwo darin liess jede Nummer im selben Absatz
    als offenes Zitat gelten — im meldenden Projekt fuenf Fehltreffer in einer
    Sitzung. Umgekehrt half der weite Radius dem echten Fall nicht: Der stand
    allein in seinem Satz und hatte kein Wort aus der Liste bei sich.

    Das Werkzeug beurteilte damit Absaetze nach Stichwoertern statt Saetze
    nach Bezug. Beide Fehlerrichtungen haben dieselbe Wurzel, und dieser
    Schnitt behebt beide.
    """
    teile = [t.strip() for t in SATZ_RE.split(absatz)]
    return [t for t in teile if t]


def _felder(zeile):
    """Tabellenfelder einer Backlog-Zeile, mit maskierten Codespan-Pipes."""
    ohne_code = re.sub(r"`[^`]*`",
                       lambda m: m.group(0).replace("|", "\x00"), zeile)
    ohne_code = ohne_code.replace("\\|", "\x00")
    return [f.strip() for f in ohne_code.strip().strip("|").split("|")]


def status_je_nummer(*pfade):
    """{"12": "**erledigt** …"} ueber Backlog UND Archiv — beide zusammen
    bilden den vollstaendigen Nummernraum."""
    stand = {}
    for pfad in pfade:
        if not pfad or not os.path.isfile(pfad):
            continue
        for zeile in open(pfad, encoding="utf-8"):
            treffer = ZEILE_RE.match(zeile)
            if not treffer:
                continue
            felder = _felder(zeile)
            stand[treffer.group(1)] = felder[-1] if felder else ""
    return stand


def absaetze(text):
    """(startzeile, text) je Absatz — die Einheit, in der 'Zukunftsform'
    beurteilt wird. Ein Absatz endet an einer Leerzeile."""
    puffer, start = [], 1
    for nr, zeile in enumerate(text.splitlines(), 1):
        if zeile.strip():
            if not puffer:
                start = nr
            puffer.append(zeile)
        elif puffer:
            yield start, "\n".join(puffer)
            puffer = []
    if puffer:
        yield start, "\n".join(puffer)


def _offene_erwartung(satz):
    """Sagt dieser Satz eine noch offene Erwartung aus?"""
    return bool(ZUKUNFT_RE.search(satz) or VORBEDINGUNG_RE.search(satz))


def _befunde_im_text(text, stand, zeilennr_start=1, ausser=None):
    """Veraltete Zitate in einem Textstueck — SATZWEISE (BL-184)."""
    befunde = []
    for zeilennr, absatz in absaetze(text):
        for satz in saetze(absatz):
            if not _offene_erwartung(satz):
                continue
            for nummer in sorted(set(REFERENZ_RE.findall(satz))):
                if ausser and nummer == ausser:
                    continue        # eine Zeile zitiert sich nicht selbst
                status = stand.get(nummer)
                if status and ERLEDIGT_RE.search(status):
                    befunde.append((zeilennr + zeilennr_start - 1, nummer,
                                    status[:60], satz.strip()[:120]))
    return befunde


def pruefe_datei(pfad, stand):
    """Liste (zeilennr, nummer, status, satzauszug) der veralteten Zitate."""
    return _befunde_im_text(Path(pfad).read_text(encoding="utf-8"), stand)


def pruefe_backlog(pfad, stand):
    """Die STATUSFELDER des Backlogs — sie sind Zitate wie jedes andere.

    BL-184, zweiter Teil. Der Backlog war vom Lint ausgenommen, und das aus
    gutem Grund: Eine Tabellenzeile ist EIN Absatz, sie traegt ein Dutzend
    Nummern und fast immer ein Zukunftswort. Absatzweise gelesen meldete er
    hier 29 Zeilen — reines Rauschen.

    Ein Statusfeld, das einen Ausloeser nennt („nach K2 entscheiden", „faellig
    vor X"), ist maschinell aber dieselbe Aussage wie ein Plan-Zitat, und es
    veraltet genauso still. Gelesen wird deshalb **nur das Statusfeld** und
    darin **nur der Satz**, und die eigene Nummer der Zeile zaehlt nicht mit.
    """
    befunde = []
    if not pfad or not os.path.isfile(pfad):
        return befunde
    for nr, zeile in enumerate(open(pfad, encoding="utf-8"), 1):
        treffer = ZEILE_RE.match(zeile)
        if not treffer:
            continue
        felder = _felder(zeile)
        if not felder:
            continue
        for zeilennr, nummer, status, auszug in _befunde_im_text(
                felder[-1], stand, nr, ausser=treffer.group(1)):
            befunde.append((nr, nummer, status, auszug))
    return befunde


def main(argv):
    backlog, archiv, dateien = str(BACKLOG), str(ARCHIV), []
    i = 0
    while i < len(argv):
        if argv[i] == "--backlog" and i + 1 < len(argv):
            backlog, i = argv[i + 1], i + 2
        elif argv[i] == "--archiv" and i + 1 < len(argv):
            archiv, i = argv[i + 1], i + 2
        elif argv[i].startswith("--"):
            print(f"FEHLER: unbekanntes Argument '{argv[i]}'", file=sys.stderr)
            return 1
        else:
            dateien.append(argv[i])
            i += 1

    stand = status_je_nummer(backlog, archiv)
    if not stand:
        print(f"FEHLER: kein Backlog unter '{backlog}' lesbar.", file=sys.stderr)
        return 1

    if not dateien:
        plan_ordner = Path(backlog).parent
        dateien = [str(p) for p in sorted(plan_ordner.glob("*.md"))
                   if p.name not in (Path(backlog).name, Path(archiv).name)]

    gesamt = 0
    for datei in dateien:
        for zeilennr, nummer, status, auszug in pruefe_datei(datei, stand):
            gesamt += 1
            print(f"{datei}:{zeilennr}: zitiert BL-{nummer} als offene Frage, "
                  f"Status ist aber '{status}'", file=sys.stderr)
            print(f"    … {auszug} …", file=sys.stderr)
    # BL-184: Der Backlog prueft jetzt seine EIGENEN Statusfelder mit — sie
    # veralten genauso still wie ein Plan-Zitat.
    for zeilennr, nummer, status, auszug in pruefe_backlog(backlog, stand):
        gesamt += 1
        print(f"{backlog}:{zeilennr}: das Statusfeld nennt BL-{nummer} als "
              f"offenen Punkt, Status ist aber '{status}'", file=sys.stderr)
        print(f"    … {auszug} …", file=sys.stderr)
    if gesamt:
        print(f"-- {gesamt} veraltete(s) Zitat(e). Der Lint urteilt ueber "
              f"Prosa: Ein bewusster Rueckblick ist kein Befund, dann die "
              f"Zukunftsform aus dem Satz nehmen.", file=sys.stderr)
        return 3
    # BL-184: Die Reihenfolge gehoert in die Ausgabe, nicht nur in den Kopf.
    # Der Lint liest die STATUSFELDER des Backlogs — vor dem Abtragen
    # aufgerufen, stehen die erledigten Eintraege dort noch als offen, und er
    # meldet folgerichtig nichts. Genau so ist der Fund entstanden: erster
    # Lauf Exit 0, und das sah aus wie „geprueft".
    print("✓ Keine veralteten Zitate. (Abtragen zuerst, linten danach — vor "
          "dem Abtragen steht der Eintrag noch als offen im Backlog, und "
          "dieser Lauf sagt dann nichts aus.)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

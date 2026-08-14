#!/usr/bin/env python3
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


def pruefe_datei(pfad, stand):
    """Liste (zeilennr, nummer, status, absatzauszug) der veralteten Zitate."""
    befunde = []
    text = Path(pfad).read_text(encoding="utf-8")
    for zeilennr, absatz in absaetze(text):
        if not ZUKUNFT_RE.search(absatz):
            continue
        for nummer in sorted(set(REFERENZ_RE.findall(absatz))):
            status = stand.get(nummer)
            if status and ERLEDIGT_RE.search(status):
                befunde.append((zeilennr, nummer, status[:60],
                                absatz.strip()[:120]))
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
    if gesamt:
        print(f"-- {gesamt} veraltete(s) Zitat(e). Der Lint urteilt ueber "
              f"Prosa: Ein bewusster Rueckblick ist kein Befund, dann die "
              f"Zukunftsform aus dem Satz nehmen.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

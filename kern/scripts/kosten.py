#!/usr/bin/env python3
"""Zentrale Kosten-Summierung fuer die T.E.A.M.-Skripte (siehe CLAUDE.md,
Anhang A). Wird von team-lib.sh (team_kosten_summe/team_kosten_split/
team_ledger_summe) aufgerufen, um die frueher doppelt/dreifach gepflegte
Python-Summierung aus vollautomatik.sh und team-status.sh zu buendeln.

Nutzung:
    kosten.py summe [--split] [--since EPOCH] DIR...
                                        Summe total_cost_usd ueber *.json in
                                        den angegebenen Log-Ordnern. Mit
                                        --split getrennt nach "abo<TAB>api"
                                        (api = Dateiname enthaelt
                                        "-api-fallback", siehe team_claude
                                        in team-lib.sh). Mit --since EPOCH nur
                                        Logs, deren mtime >= EPOCH ist (Kosten
                                        EINES Laufs statt lebenslang — Basis der
                                        Pro-Lauf-Deckel-Durchsetzung, BL-18).
    kosten.py ledger [PFAD] [--domaene website|team] [--rolle ROLLE]
              [--kaskade N] [--split] [--anzahl]
                                        Summe der usd-Spalte aus der
                                        committeten .budget-ledger (Default
                                        ".budget-ledger"; Kommentarzeilen "#"
                                        und Leerzeilen werden ignoriert).
                                        Zeilen im erweiterten 7-Feld-Schema
                                        (datum|kaskade|usd|auth|domaene|rolle|
                                        notiz, BL-29) koennen mit --domaene/
                                        --rolle gefiltert werden. Altzeilen im
                                        5-Feld-Schema (ohne domaene/rolle)
                                        zaehlen bei einem gesetzten Filter
                                        NIE mit — sie sind "unzugeordnet".
                                        --kaskade filtert zusaetzlich auf eine
                                        einzelne Kaskaden-Nummer (Feld 2, in
                                        JEDEM Schema vorhanden) — genutzt von
                                        team-status.sh, um zu erkennen, ob fuer
                                        die aktive Kaskade bereits eine echte
                                        Architekt-Zeile (Stufe 43) vorliegt.
                                        --split gibt statt der Summe die
                                        usd-Spalte nach auth-Bucket getrennt
                                        aus: "abo<TAB>api<TAB>gemischt"
                                        (BL-17-Restpunkt/BL-29-"1b", Kaskade
                                        16/Stufe 53). Bucket-Regel: auth=="abo"
                                        -> abo, auth=="api" -> api, JEDER
                                        andere Wert (v. a. "abo/api", aber
                                        auch unbekannte/leere/Altzeilen-Werte)
                                        -> gemischt. Es gilt immer
                                        abo+api+gemischt == Summe ohne --split
                                        (kein geratener Split). Kombinierbar
                                        mit --domaene/--rolle/--kaskade.
                                        --anzahl gibt statt der Summe die
                                        ANZAHL der (gefilterten) Treffer aus
                                        (HM-46): eine echte Zeile mit usd=0
                                        ist am Summenwert "0.0000" NICHT von
                                        "kein Treffer" zu unterscheiden — nur
                                        die Trefferanzahl beantwortet
                                        "existiert eine Zeile?" zuverlaessig.
    kosten.py architekt-schaetzung --since REF [--repo DIR] [PFAD...]
                                        A2-Live-Schaetzung (BL-28, Kaskade 13/
                                        Stufe 42) fuer die Architekt-Rolle, die
                                        (anders als Ralph/Frank/Axel/Harry/Marv)
                                        nicht ueber team_claude laeuft und daher
                                        keine total_cost_usd-JSONs schreibt.
                                        Proxy: Zeilen-Churn (git diff --numstat
                                        REF..HEAD) ueber PFAD... (Default
                                        "plans" "CLAUDE.md") mal Eichfaktor
                                        ARCHITEKT_USD_PRO_CHURN_ZEILE. Bewusst
                                        eine GROBE Groessenordnung, kein exakter
                                        Wert (siehe Stufe 43: A1 ersetzt sie
                                        beim Kaskaden-Abschluss durch den
                                        echten Konsolenwert). --repo zeigt auf
                                        ein anderes Arbeitsverzeichnis (Tests).
    kosten.py architekt-abschluss --usd USD --domaene website|team
              [--kaskade N] [--notiz TEXT] [--pfad PFAD] [--repo DIR]
                                        A1-Ersetzung (BL-28, Kaskade 13/
                                        Stufe 43): haengt die ECHTE
                                        Architekt-Ledger-Zeile an (auth=api,
                                        rolle=architekt) fuer die Kaskade, die
                                        der Strippenzieher aus der Anthropic-
                                        Konsole abliest. Ohne --kaskade wird
                                        die Nummer aus .ralph-plan abgeleitet
                                        (Muster "ralph-kaskade-<N>-..."). Ein
                                        zweiter Aufruf fuer dieselbe Kaskade
                                        ERSETZT die vorhandene Architekt-Zeile
                                        dieser Kaskade statt sie zu
                                        verdoppeln — Schaetzung (A2, nie
                                        persistiert) und echter Wert zaehlen
                                        so nie doppelt. USD wird validiert
                                        (endliche, nicht-negative Zahl); bei
                                        ungueltiger Eingabe bricht das Tool
                                        sauber ab, OHNE die Ledger zu
                                        veraendern (Lehre aus BL-23/HM-17:
                                        keine rohe Interpolation). Duenner
                                        Alias auf akteur-abschluss mit
                                        --rolle architekt --auth api
                                        vorbelegt (BL-33, Stufe 50) —
                                        bleibt unveraendert, rueckwaerts-
                                        kompatibel.
    kosten.py akteur-abschluss --usd USD --domaene website|team
              --rolle ROLLE --auth abo|api
              [--kaskade N] [--notiz TEXT] [--pfad PFAD] [--repo DIR]
                                        Rollen-agnostische A1-Ersetzung
                                        (BL-33, Kaskade 15/Stufe 50): wie
                                        architekt-abschluss, aber fuer JEDE
                                        interaktiv (ausserhalb team_claude)
                                        arbeitende Rolle, die selbst keine
                                        total_cost_usd-JSONs schreibt (z. B.
                                        Frank im Abomodus). --rolle und
                                        --auth sind Pflicht. Ersetzt bei
                                        einem zweiten Aufruf NUR die Zeile
                                        DERSELBEN Rolle DERSELBEN Kaskade —
                                        Zeilen anderer Rollen der gleichen
                                        Kaskade (z. B. Architekt) bleiben
                                        unangetastet. A2-Live-Schaetzung
                                        bleibt bewusst architekt-spezifisch.
    kosten.py rollen-abschluss --kaskade N --domaene website|team
              [--notiz TEXT] [--logs DIR...] [--pfad PFAD] [--repo DIR]
              [--archivieren]
                                        Kaskadenscharfe Rollenkosten
                                        (BL-17-Restpunkt/BL-29-"1b", Kaskade
                                        16/Stufe 54): summiert die .team-logs
                                        (Default; --logs uebersteuerbar fuer
                                        Tests) abo/api-getrennt und haengt
                                        EINE rolle=roles-Zeile fuer die
                                        angegebene Kaskade an (usd=abo+api,
                                        auth="abo"/"api"/"abo/api" je nach
                                        Split; Kaskadenschaerfe schlaegt
                                        Abo/API-Schaerfe je Rollenzeile,
                                        Strippenzieher-Entscheid). Ein
                                        zweiter Aufruf fuer dieselbe Kaskade
                                        ERSETZT die vorhandene roles-Zeile
                                        dieser Kaskade, Zeilen anderer Rollen
                                        (ralph/architekt/…) bleiben
                                        unangetastet. Mit --archivieren
                                        verschiebt rollen-abschluss NACH
                                        erfolgreicher Ledgerzeile EXAKT die
                                        gezaehlten .team-logs/*.json nach
                                        .team-logs/archiv/ — atomar im selben
                                        Prozess, kein Zwei-Schritt-Race mehr
                                        zwischen Zaehlung und Archivierung
                                        (HM-39/AX-4). Ohne das Flag (Default,
                                        z. B. reine Test-/Auswertungslaeufe)
                                        wird nichts verschoben. Nur die
                                        team-status.sh-Oberflaeche
                                        (--rollen-abschluss) setzt das Flag.
                                        Nur manueller Kaskaden-Abschluss,
                                        laeuft NICHT in vollautomatik.sh.
"""
import contextlib
import fcntl
import glob
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import date

# Eichfaktor (BL-28, Kaskade 13/Stufe 42). Grundlage: die Architekten-Session
# vom 2026-07-12 (Kaskade-12-Aushaertung + Budget-Modell-Doku +
# Kaskade-13-Aushaertung, Commits 06c2fe9..0c842fb) kostete laut
# Anthropic-Konsole ~16 USD. Der Zeilen-Churn derselben Commits ueber
# plans/** + CLAUDE.md (git diff --numstat 06c2fe9^..0c842fb -- plans/
# CLAUDE.md) ergab 1045 Zeilen (74+18 CLAUDE.md, 4+3 plans/backlog.md, 77+0
# plans/beutebuch.md, 292+0 plans/ermittlungsakten/AX-3.md, 212+0
# plans/ralph-kaskade-12-auth-startwarnung.md, 199+0
# plans/ralph-kaskade-13-architekt-kosten.md, 166+0 plans/roadmap-skizzen.md).
# Faktor = 16 USD / 1045 Zeilen. Bewusst grobe Groessenordnung, keine exakte
# Abrechnung (siehe Stufe 42/43 in plans/ralph-kaskade-13-architekt-kosten.md).
ARCHITEKT_USD_PRO_CHURN_ZEILE = 16.0 / 1045


def team_log_dateien(dirs, since=None):
    """Liefert die *.json-Kandidatendateien aus dirs EINMAL als Liste (nicht-
    rekursiver glob, wie log_kosten() es bisher inline machte). Basis fuer den
    HM-39/AX-4-Fix: Zaehlen und Archivieren muessen dieselbe, einmal
    geglobbte Liste S1 verwenden statt zweier getrennter Snapshots zu
    unterschiedlichen Zeitpunkten (Race, siehe rollen-abschluss unten)."""
    files = []
    for d in dirs:
        for datei in glob.glob(os.path.join(d, "*.json")):
            if since is not None:
                try:
                    if os.path.getmtime(datei) < since:
                        continue
                except OSError:
                    continue
            files.append(datei)
    return files


def _datei_kosten(datei):
    """Liest total_cost_usd aus EINER Datei. Gibt (kosten, ok) zurueck --
    ok=False bei jedem Parse-Fehler (abgeschnittenes/kaputtes JSON, leere
    Datei, defektes Encoding, unerwartetes Schema). HM-41: vorher trug eine
    nicht-parsebare Datei STILL 0.0 zur Summe bei und war von einer echten
    $0-Datei nicht mehr unterscheidbar -- Aufrufer, die wissen muessen,
    WELCHE Dateien tatsaechlich gezaehlt wurden (z. B. um nur diese zu
    archivieren), brauchen dafuer dieses ok-Flag.
    HM-44: ein negativer oder nicht-endlicher Wert (NaN/Infinity -- JSON
    erlaubt beides ueber Pythons json-Modul) gilt EBENFALLS als ok=False,
    genau wie ein Parse-Fehler -- sonst saldiert eine einzelne manipulierte
    oder korrumpierte Datei echte Kosten aus anderen Dateien unbemerkt weg,
    solange die GESAMTSUMME am Ende nicht-negativ bleibt. Die Pruefung
    gehoert auf die Ebene der einzelnen Datei, nicht erst auf die fertige
    Summe (dort wird sie in rollen_abschluss()/akteur_abschluss() geprueft,
    aber die ungeprueften Aufrufer team_kosten_summe/-split/-seit sehen sie
    nie)."""
    try:
        kosten = json.load(open(datei)).get("total_cost_usd", 0) or 0
        if not math.isfinite(kosten) or kosten < 0:
            return 0.0, False
        return kosten, True
    except Exception:
        return 0.0, False


def log_kosten(dirs, split=False, since=None, files=None, return_geparst=False):
    """Summiert total_cost_usd. Ohne files: globbt dirs selbst (bisheriges
    Verhalten, unveraendert fuer summe/--budget/since-Aufrufer). Mit files:
    rechnet NUR ueber die uebergebene Liste, ohne erneut zu globben — der
    HM-39-Fix uebergibt hier die bei T1 einmal gefasste Liste, damit Zaehlen
    und spaeteres Archivieren garantiert dieselbe Dateimenge sehen.
    return_geparst=True (HM-41) liefert zusaetzlich die Teilmenge der
    Kandidaten, die tatsaechlich erfolgreich als JSON gelesen werden konnte
    -- NUR diese Teilmenge darf ein Aufrufer archivieren, sonst verschwindet
    eine nicht-parsebare, aber bereits bezahlte Datei spurlos im Archiv."""
    abo = 0.0
    api = 0.0
    geparst = []
    kandidaten = files if files is not None else team_log_dateien(dirs, since=since)
    for datei in kandidaten:
        kosten, ok = _datei_kosten(datei)
        if not ok:
            continue
        geparst.append(datei)
        if "-api-fallback" in os.path.basename(datei):
            api += kosten
        else:
            abo += kosten
    ergebnis = (abo, api) if split else (abo + api)
    if return_geparst:
        return ergebnis, geparst
    return ergebnis


def _archiviere_dateien(files):
    """Verschiebt GENAU die uebergebene Dateiliste nach <verzeichnis>/archiv/
    (nicht den Ordnerinhalt zum Aufrufzeitpunkt — das war der HM-39/AX-4-Race:
    ein zwischen Zaehlung und Archivierung neu entstandenes File landete
    bisher ungezaehlt trotzdem im Archiv und war fortan aus jeder Summe
    verschwunden). os.replace() ist atomar innerhalb desselben Dateisystems;
    bereits verschwundene/parallel bewegte Dateien werden toleriert."""
    verschoben = []
    for f in files:
        archiv = os.path.join(os.path.dirname(f), "archiv")
        os.makedirs(archiv, exist_ok=True)
        ziel = os.path.join(archiv, os.path.basename(f))
        try:
            os.replace(f, ziel)
            verschoben.append(ziel)
        except OSError:
            pass
    return verschoben


def ledger_zeilen(pfad=".budget-ledger"):
    """Liest .budget-ledger zeilenweise ein und liefert Dicts mit usd/auth/
    domaene/rolle/notiz. Altzeilen im urspruenglichen 5-Feld-Schema (datum |
    kaskade | usd | auth | notiz) haben domaene=None und rolle=None -- sie
    werden bei einem Domaenen-/Rollen-Filter NIE mitgezaehlt (BL-29:
    "unzugeordnet" statt stillschweigend zugeschlagen)."""
    if not os.path.isfile(pfad):
        return
    with open(pfad) as fh:
        for zeile in fh:
            zeile = zeile.strip()
            if not zeile or zeile.startswith("#"):
                continue
            felder = [f.strip() for f in zeile.split("|")]
            if len(felder) < 3:
                continue
            try:
                usd = float(felder[2])
            except ValueError:
                continue
            if len(felder) >= 7:
                domaene, rolle, notiz = felder[4], felder[5], felder[6]
            else:
                domaene, rolle = None, None
                notiz = felder[4] if len(felder) > 4 else ""
            yield {
                "usd": usd,
                "auth": felder[3] if len(felder) > 3 else "",
                "domaene": domaene,
                "rolle": rolle,
                "kaskade": felder[1],
                "notiz": notiz,
            }


def ledger_summe(pfad=".budget-ledger", domaene=None, rolle=None, kaskade=None):
    total = 0.0
    for zeile in ledger_zeilen(pfad):
        if domaene is not None and zeile["domaene"] != domaene:
            continue
        if rolle is not None and zeile["rolle"] != rolle:
            continue
        if kaskade is not None and zeile["kaskade"] != str(kaskade):
            continue
        total += zeile["usd"]
    return total


def ledger_anzahl(pfad=".budget-ledger", domaene=None, rolle=None, kaskade=None):
    """Wie ledger_summe(), aber liefert die ANZAHL der gefilterten Treffer
    statt ihrer usd-Summe (HM-46): eine echte, per akteur_abschluss()
    gebuchte Zeile mit usd=0.0000 ist am Summenwert "0.0000" nicht von "kein
    Treffer fuer diesen Filter" zu unterscheiden -- nur die Trefferanzahl
    beantwortet die Existenzfrage zuverlaessig."""
    anzahl = 0
    for zeile in ledger_zeilen(pfad):
        if domaene is not None and zeile["domaene"] != domaene:
            continue
        if rolle is not None and zeile["rolle"] != rolle:
            continue
        if kaskade is not None and zeile["kaskade"] != str(kaskade):
            continue
        anzahl += 1
    return anzahl


def ledger_split(pfad=".budget-ledger", domaene=None, rolle=None, kaskade=None):
    """Wie ledger_summe(), aber die usd-Spalte nach auth-Bucket getrennt
    (BL-17-Restpunkt/BL-29-"1b", Stufe 53): (abo, api, gemischt). Eine Zeile
    zaehlt NUR bei auth=="abo" zu abo, NUR bei auth=="api" zu api, sonst
    (v. a. "abo/api", aber auch jeder unbekannte/leere Wert und Altzeilen)
    zu gemischt -- damit gilt immer abo+api+gemischt == ledger_summe(...) mit
    denselben Filtern (kein geratener Split, keine verlorenen Betraege)."""
    abo = 0.0
    api = 0.0
    gemischt = 0.0
    for zeile in ledger_zeilen(pfad):
        if domaene is not None and zeile["domaene"] != domaene:
            continue
        if rolle is not None and zeile["rolle"] != rolle:
            continue
        if kaskade is not None and zeile["kaskade"] != str(kaskade):
            continue
        if zeile["auth"] == "abo":
            abo += zeile["usd"]
        elif zeile["auth"] == "api":
            api += zeile["usd"]
        else:
            gemischt += zeile["usd"]
    return abo, api, gemischt


def git_churn(seit, pfade, repo="."):
    """Zeilen-Churn (hinzugefuegt + geloescht) aus `git diff --numstat seit..
    HEAD -- pfade...` im Verzeichnis repo. Binaerdateien (numstat liefert "-"
    statt Zahlen) werden ignoriert. Wirft RuntimeError, wenn git scheitert
    (z. B. seit ist keine bekannte Referenz) — kein stillschweigendes 0."""
    cmd = ["git", "diff", "--numstat", seit, "--", *pfade]
    ergebnis = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    if ergebnis.returncode != 0:
        raise RuntimeError(
            f"git diff fehlgeschlagen ({' '.join(cmd)}): "
            f"{ergebnis.stderr.strip()}"
        )
    churn = 0
    for zeile in ergebnis.stdout.splitlines():
        felder = zeile.split("\t")
        if len(felder) < 2:
            continue
        hinzu, weg = felder[0], felder[1]
        if hinzu == "-" or weg == "-":
            continue
        try:
            churn += int(hinzu) + int(weg)
        except ValueError:
            continue
    return churn


def architekt_schaetzung(seit, pfade=("plans", "CLAUDE.md"), repo="."):
    churn = git_churn(seit, pfade, repo=repo)
    return churn, churn * ARCHITEKT_USD_PRO_CHURN_ZEILE


def kaskade_aus_plan(repo="."):
    """Leitet die Kaskaden-Nummer aus der Zeiger-Datei .ralph-plan ab (Muster
    "ralph-kaskade-<N>-..." im Dateinamen). None, wenn die Datei fehlt oder
    das Muster nicht passt — der Aufrufer verlangt dann ein explizites
    --kaskade."""
    pfad = os.path.join(repo, ".ralph-plan")
    if not os.path.isfile(pfad):
        return None
    inhalt = open(pfad).read().strip()
    treffer = re.search(r"ralph-kaskade-(\d+)-", inhalt)
    return treffer.group(1) if treffer else None


@contextlib.contextmanager
def _ledger_lock(pfad):
    """Interprozess-Sperre um den Lesen+Schreiben-Kritikbereich von
    _ledger_zeile_setzen() (HM-48): ein `flock` auf eine feste Lock-Datei
    neben dem Ledger, EX-gehalten fuer die volle Read-Modify-Write-Spanne.
    Serialisiert konkurrierende kosten.py-Prozesse (egal ob direkt oder ueber
    team-status.sh/team-lib.sh aufgerufen) unabhaengig vom Aufrufer, statt
    sich auf eine Sperre der Shell-Seite (team_lock()) zu verlassen, die
    ohnehin nicht fuer alle drei Abschluss-Kommandos genutzt wurde."""
    lock_pfad = pfad + ".lock"
    fd = os.open(lock_pfad, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _ledger_zeile_setzen(zeile_neu, match_fn, pfad=".budget-ledger"):
    """Gemeinsame atomare Schreiblogik fuer akteur_abschluss()/
    rollen_abschluss() (Stufe 54 — vermeidet zwei divergierende
    Atomizitaets-Implementierungen, HM-35/HM-36-Klasse). Haengt zeile_neu an
    und ersetzt dabei jede bestehende Nicht-Kommentar-Zeile, fuer die
    match_fn(felder) True liefert (felder = die "|"-getrennten, gestrippten
    Werte der Zeile). Treffen MEHR ALS EINE bestehende Zeile auf match_fn zu,
    wird NICHTS geschrieben und stattdessen ValueError geworfen (HM-47) --
    .budget-ledger enthaelt real bereits mehrere eigenstaendige Zeilen
    derselben Kaskade/Rolle (z. B. spaeter nachgetragene Restlogs), und ein
    "ersetzt alle Treffer"-Verhalten wuerde solche Zeilen kommentarlos
    verschlucken statt nur die eine gemeinte Buchung zu korrigieren. Schreibt
    sonst atomar per Temp-Datei + os.replace(). Gibt True zurueck, wenn eine
    vorhandene Zeile ersetzt wurde, sonst False (neu angelegt)."""
    with _ledger_lock(pfad):
        bestehend = []
        if os.path.isfile(pfad):
            with open(pfad) as fh:
                bestehend = fh.readlines()

        treffer = 0
        for rohzeile in bestehend:
            stripped = rohzeile.strip()
            if not stripped or stripped.startswith("#"):
                continue
            felder = [f.strip() for f in stripped.split("|")]
            if match_fn(felder):
                treffer += 1
        if treffer > 1:
            raise ValueError(
                f"{treffer} bestehende Zeilen in '{pfad}' passen auf dieselbe "
                "Kaskade/Rolle -- Ersetzung ist mehrdeutig, es wird NICHTS "
                "geschrieben. Bei mehreren legitim koexistierenden Zeilen (z. B. "
                "nachgetragener Restlog) die betroffene Zeile stattdessen von "
                "Hand in .budget-ledger korrigieren.")

        behalten = []
        ersetzt = False
        for rohzeile in bestehend:
            stripped = rohzeile.strip()
            if not stripped or stripped.startswith("#"):
                behalten.append(rohzeile)
                continue
            felder = [f.strip() for f in stripped.split("|")]
            if match_fn(felder):
                ersetzt = True
                continue
            behalten.append(rohzeile)

        if behalten and not behalten[-1].endswith("\n"):
            behalten[-1] += "\n"
        behalten.append(zeile_neu)

        ziel_verzeichnis = os.path.dirname(os.path.abspath(pfad)) or "."
        fd, tmp_pfad = tempfile.mkstemp(
            prefix=".budget-ledger.", suffix=".tmp", dir=ziel_verzeichnis)
        try:
            with os.fdopen(fd, "w") as fh:
                fh.writelines(behalten)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_pfad, pfad)
        except BaseException:
            if os.path.exists(tmp_pfad):
                os.remove(tmp_pfad)
            raise

        return ersetzt


def _sanitize_pipe_feld(wert):
    """Haertet einen einzelnen Ledger-Feldwert gegen `|`/CR/LF (HM-36/HM-38):
    ein `|` wuerde das 7-Feld-Schema um zusaetzliche Spalten erweitern, ein
    Zeilenumbruch eine zweite, frei erfundene Zeile erzeugen. Gemeinsamer
    Helfer fuer akteur_abschluss() UND rollen_abschluss(), damit die Haertung
    nicht pro Funktion einzeln (und wie bei HM-38 unvollstaendig) dupliziert
    wird."""
    wert = str(wert).strip() if wert else ""
    return wert.replace("|", "/").replace("\r", " ").replace("\n", " ").strip()


def akteur_abschluss(usd, domaene, kaskade, rolle, auth, notiz="",
                      pfad=".budget-ledger"):
    """A1-Ersetzung, rollen-agnostisch (BL-33, Stufe 50): haengt eine echte
    Ledger-Zeile fuer <rolle>/<kaskade> an. Existiert bereits eine Zeile
    DERSELBEN Rolle DERSELBEN Kaskade (7-Feld-Schema), wird sie ERSETZT statt
    verdoppelt -- Idempotenz bei mehrfachem Aufruf, ohne die Zeile einer
    ANDEREN Rolle derselben Kaskade zu beruehren (z. B. Frank- und
    Architekt-Zeile der gleichen Kaskade koexistieren). Wirft ValueError bei
    ungueltigen Eingaben, OHNE die Datei anzufassen. Gibt True zurueck, wenn
    eine vorhandene Zeile ersetzt wurde, sonst False (neu angelegt)."""
    if domaene not in ("website", "team"):
        raise ValueError(
            f"domaene muss 'website' oder 'team' sein, nicht '{domaene}'")
    if auth not in ("abo", "api"):
        raise ValueError(f"auth muss 'abo' oder 'api' sein, nicht '{auth}'")
    rolle = _sanitize_pipe_feld(rolle)
    if not rolle:
        raise ValueError("rolle darf nicht leer sein")
    if not math.isfinite(usd) or usd < 0:
        raise ValueError(f"usd muss eine endliche, nicht-negative Zahl sein, "
                          f"nicht '{usd}'")
    kaskade = _sanitize_pipe_feld(kaskade)
    if not kaskade:
        raise ValueError(
            "kaskade konnte nicht ermittelt werden (--kaskade angeben oder "
            ".ralph-plan pruefen)")

    notiz_sauber = _sanitize_pipe_feld(notiz)
    zeile_neu = (f"{date.today().isoformat()} | {kaskade} | {usd:.4f} | "
                 f"{auth} | {domaene} | {rolle} | {notiz_sauber}\n")

    def match_fn(felder):
        return len(felder) >= 7 and felder[1] == kaskade and felder[5] == rolle

    return _ledger_zeile_setzen(zeile_neu, match_fn, pfad)


def architekt_abschluss(usd, domaene, kaskade, notiz="", pfad=".budget-ledger"):
    """Duenner, rueckwaertskompatibler Alias auf akteur_abschluss() mit
    rolle=architekt/auth=api (unveraendertes Verhalten seit Stufe 43)."""
    return akteur_abschluss(usd, domaene, kaskade, rolle="architekt",
                             auth="api", notiz=notiz, pfad=pfad)


def rollen_abschluss(kaskade, abo, api, domaene="team", notiz="",
                      pfad=".budget-ledger"):
    """Kaskadenscharfe Rollenkosten (BL-17-Restpunkt/BL-29-"1b", Kaskade
    16/Stufe 54): haengt EINE rolle=roles-Ledger-Zeile fuer die
    .team-logs-Kosten (Harry/Marv/Frank/Axel) EINER Kaskade an. usd = abo +
    api; auth = "abo" (api==0), "api" (abo==0), sonst "abo/api" —
    Strippenzieher-Entscheid: Kaskadenschaerfe schlaegt Abo/API-Schaerfe je
    Rollenzeile, der gemischte Fall ist erwartet und wird ehrlich als
    "abo/api" ausgewiesen (kein geratener Split). notiz wird um den exakten
    Split ergaenzt, analog der bestehenden roles-total-Zeile. Ein zweiter
    Aufruf fuer DIESELBE Kaskade ERSETZT die vorhandene rolle=roles-Zeile
    dieser Kaskade, Zeilen anderer Rollen (ralph/architekt/…) bleiben
    unangetastet. Wirft ValueError bei ungueltigen Eingaben, OHNE die Datei
    anzufassen. Gibt True zurueck, wenn eine vorhandene Zeile ersetzt wurde,
    sonst False (neu angelegt)."""
    if domaene not in ("website", "team"):
        raise ValueError(
            f"domaene muss 'website' oder 'team' sein, nicht '{domaene}'")
    if not math.isfinite(abo) or abo < 0:
        raise ValueError(f"abo muss eine endliche, nicht-negative Zahl sein, "
                          f"nicht '{abo}'")
    if not math.isfinite(api) or api < 0:
        raise ValueError(f"api muss eine endliche, nicht-negative Zahl sein, "
                          f"nicht '{api}'")
    kaskade = _sanitize_pipe_feld(kaskade)
    if not kaskade:
        raise ValueError(
            "kaskade konnte nicht ermittelt werden (--kaskade angeben oder "
            ".ralph-plan pruefen)")

    usd = abo + api
    if api == 0:
        auth = "abo"
    elif abo == 0:
        auth = "api"
    else:
        auth = "abo/api"

    notiz_sauber = _sanitize_pipe_feld(notiz)
    split_hinweis = f"abo {abo:.4f} / api {api:.4f}"
    notiz_voll = f"{notiz_sauber} — {split_hinweis}" if notiz_sauber \
        else split_hinweis
    zeile_neu = (f"{date.today().isoformat()} | {kaskade} | {usd:.4f} | "
                 f"{auth} | {domaene} | roles | {notiz_voll}\n")

    def match_fn(felder):
        return len(felder) >= 7 and felder[1] == kaskade and felder[5] == "roles"

    return _ledger_zeile_setzen(zeile_neu, match_fn, pfad)


def _main(argv):
    if not argv:
        print("Nutzung: kosten.py summe [--split] DIR... | ledger [PFAD]",
              file=sys.stderr)
        return 1

    befehl, rest = argv[0], argv[1:]

    if befehl == "summe":
        split = False
        since = None
        while rest:
            if rest[0] == "--split":
                split = True
                rest = rest[1:]
            elif rest[0] == "--since":
                if len(rest) < 2:
                    print("Fehler: --since braucht einen EPOCH-Wert",
                          file=sys.stderr)
                    return 1
                try:
                    since = float(rest[1])
                except ValueError:
                    print(f"Fehler: --since-Wert '{rest[1]}' ist keine Zahl",
                          file=sys.stderr)
                    return 1
                rest = rest[2:]
            else:
                break
        if split:
            abo, api = log_kosten(rest, split=True, since=since)
            print(f"{abo:.4f}\t{api:.4f}")
        else:
            print(f"{log_kosten(rest, since=since):.4f}")
        return 0

    if befehl == "ledger":
        pfad = None
        domaene = None
        rolle = None
        kaskade = None
        split = False
        anzahl = False
        i = 0
        while i < len(rest):
            if rest[i] == "--split":
                split = True
                i += 1
            elif rest[i] == "--anzahl":
                anzahl = True
                i += 1
            elif rest[i] == "--domaene":
                if i + 1 >= len(rest):
                    print("Fehler: --domaene braucht einen Wert (website|team)",
                          file=sys.stderr)
                    return 1
                domaene = rest[i + 1]
                i += 2
            elif rest[i] == "--rolle":
                if i + 1 >= len(rest):
                    print("Fehler: --rolle braucht einen Wert", file=sys.stderr)
                    return 1
                rolle = rest[i + 1]
                i += 2
            elif rest[i] == "--kaskade":
                if i + 1 >= len(rest):
                    print("Fehler: --kaskade braucht einen Wert", file=sys.stderr)
                    return 1
                kaskade = rest[i + 1]
                i += 2
            elif not rest[i].startswith("--") and pfad is None:
                pfad = rest[i]
                i += 1
            else:
                print(f"Fehler: unbekanntes Argument '{rest[i]}'", file=sys.stderr)
                return 1
        if domaene is not None and domaene not in ("website", "team"):
            print(f"Fehler: --domaene muss 'website' oder 'team' sein, nicht "
                  f"'{domaene}'", file=sys.stderr)
            return 1
        if anzahl:
            print(ledger_anzahl(pfad or '.budget-ledger', domaene=domaene,
                                 rolle=rolle, kaskade=kaskade))
        elif split:
            abo, api, gemischt = ledger_split(
                pfad or '.budget-ledger', domaene=domaene, rolle=rolle,
                kaskade=kaskade)
            print(f"{abo:.4f}\t{api:.4f}\t{gemischt:.4f}")
        else:
            print(f"{ledger_summe(pfad or '.budget-ledger', domaene=domaene, rolle=rolle, kaskade=kaskade):.4f}")
        return 0

    if befehl == "architekt-schaetzung":
        seit = None
        repo = "."
        pfade = []
        i = 0
        while i < len(rest):
            if rest[i] == "--since":
                if i + 1 >= len(rest):
                    print("Fehler: --since braucht eine Git-Referenz",
                          file=sys.stderr)
                    return 1
                seit = rest[i + 1]
                i += 2
            elif rest[i] == "--repo":
                if i + 1 >= len(rest):
                    print("Fehler: --repo braucht einen Pfad", file=sys.stderr)
                    return 1
                repo = rest[i + 1]
                i += 2
            else:
                pfade.append(rest[i])
                i += 1
        if not seit:
            print("Fehler: --since REF ist Pflicht", file=sys.stderr)
            return 1
        try:
            _, usd = architekt_schaetzung(seit, pfade=pfade or ("plans", "CLAUDE.md"),
                                           repo=repo)
        except RuntimeError as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 1
        print(f"{usd:.4f}")
        return 0

    if befehl in ("architekt-abschluss", "akteur-abschluss"):
        usd_raw = None
        domaene = None
        kaskade = None
        rolle = "architekt" if befehl == "architekt-abschluss" else None
        auth = "api" if befehl == "architekt-abschluss" else None
        notiz = ""
        pfad = ".budget-ledger"
        repo = "."
        i = 0
        while i < len(rest):
            if rest[i] == "--usd":
                if i + 1 >= len(rest):
                    print("Fehler: --usd braucht einen Wert", file=sys.stderr)
                    return 1
                usd_raw = rest[i + 1]
                i += 2
            elif rest[i] == "--domaene":
                if i + 1 >= len(rest):
                    print("Fehler: --domaene braucht einen Wert (website|team)",
                          file=sys.stderr)
                    return 1
                domaene = rest[i + 1]
                i += 2
            elif rest[i] == "--kaskade":
                if i + 1 >= len(rest):
                    print("Fehler: --kaskade braucht einen Wert", file=sys.stderr)
                    return 1
                kaskade = rest[i + 1]
                i += 2
            elif befehl == "akteur-abschluss" and rest[i] == "--rolle":
                if i + 1 >= len(rest):
                    print("Fehler: --rolle braucht einen Wert", file=sys.stderr)
                    return 1
                rolle = rest[i + 1]
                i += 2
            elif befehl == "akteur-abschluss" and rest[i] == "--auth":
                if i + 1 >= len(rest):
                    print("Fehler: --auth braucht einen Wert (abo|api)",
                          file=sys.stderr)
                    return 1
                auth = rest[i + 1]
                i += 2
            elif rest[i] == "--notiz":
                if i + 1 >= len(rest):
                    print("Fehler: --notiz braucht einen Wert", file=sys.stderr)
                    return 1
                notiz = rest[i + 1]
                i += 2
            elif rest[i] == "--pfad":
                if i + 1 >= len(rest):
                    print("Fehler: --pfad braucht einen Wert", file=sys.stderr)
                    return 1
                pfad = rest[i + 1]
                i += 2
            elif rest[i] == "--repo":
                if i + 1 >= len(rest):
                    print("Fehler: --repo braucht einen Pfad", file=sys.stderr)
                    return 1
                repo = rest[i + 1]
                i += 2
            else:
                print(f"Fehler: unbekanntes Argument '{rest[i]}'", file=sys.stderr)
                return 1

        if usd_raw is None:
            print("Fehler: --usd USD ist Pflicht", file=sys.stderr)
            return 1
        try:
            usd = float(usd_raw)
        except ValueError:
            print(f"Fehler: --usd-Wert '{usd_raw}' ist keine Zahl", file=sys.stderr)
            return 1
        if domaene is None:
            print("Fehler: --domaene website|team ist Pflicht", file=sys.stderr)
            return 1
        if befehl == "akteur-abschluss":
            if not rolle:
                print("Fehler: --rolle ist Pflicht", file=sys.stderr)
                return 1
            if auth is None:
                print("Fehler: --auth abo|api ist Pflicht", file=sys.stderr)
                return 1
        if kaskade is None:
            kaskade = kaskade_aus_plan(repo)

        ledger_pfad = pfad if os.path.isabs(pfad) or repo == "." \
            else os.path.join(repo, pfad)
        try:
            ersetzt = akteur_abschluss(usd, domaene, kaskade, rolle, auth,
                                        notiz=notiz, pfad=ledger_pfad)
        except ValueError as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 1
        aktion = "ersetzt" if ersetzt else "angelegt"
        print(f"{rolle.capitalize()}-Zeile Kaskade {kaskade} ({domaene}) "
              f"{aktion}: {usd:.4f} USD")
        return 0

    if befehl == "rollen-abschluss":
        kaskade = None
        domaene = None
        notiz = ""
        logs = None
        pfad = ".budget-ledger"
        repo = "."
        archivieren = False
        i = 0
        while i < len(rest):
            if rest[i] == "--kaskade":
                if i + 1 >= len(rest):
                    print("Fehler: --kaskade braucht einen Wert", file=sys.stderr)
                    return 1
                kaskade = rest[i + 1]
                i += 2
            elif rest[i] == "--domaene":
                if i + 1 >= len(rest):
                    print("Fehler: --domaene braucht einen Wert (website|team)",
                          file=sys.stderr)
                    return 1
                domaene = rest[i + 1]
                i += 2
            elif rest[i] == "--notiz":
                if i + 1 >= len(rest):
                    print("Fehler: --notiz braucht einen Wert", file=sys.stderr)
                    return 1
                notiz = rest[i + 1]
                i += 2
            elif rest[i] == "--logs":
                logs = []
                i += 1
                while i < len(rest) and not rest[i].startswith("--"):
                    logs.append(rest[i])
                    i += 1
            elif rest[i] == "--pfad":
                if i + 1 >= len(rest):
                    print("Fehler: --pfad braucht einen Wert", file=sys.stderr)
                    return 1
                pfad = rest[i + 1]
                i += 2
            elif rest[i] == "--repo":
                if i + 1 >= len(rest):
                    print("Fehler: --repo braucht einen Pfad", file=sys.stderr)
                    return 1
                repo = rest[i + 1]
                i += 2
            elif rest[i] == "--archivieren":
                archivieren = True
                i += 1
            else:
                print(f"Fehler: unbekanntes Argument '{rest[i]}'", file=sys.stderr)
                return 1

        if domaene is None:
            print("Fehler: --domaene website|team ist Pflicht", file=sys.stderr)
            return 1
        if kaskade is None:
            kaskade = kaskade_aus_plan(repo)
        if not logs:
            logs = [".team-logs"]

        ledger_pfad = pfad if os.path.isabs(pfad) or repo == "." \
            else os.path.join(repo, pfad)
        # EIN Snapshot S1 fuer Zaehlen UND (optionales) Archivieren — der
        # HM-39/AX-4-Fix. Eine Datei, die NACH diesem glob() neu in logs
        # entsteht, ist weder in S1 noch in der Archiv-Menge; sie bleibt
        # liegen und wird vom naechsten rollen-abschluss korrekt erfasst.
        files = team_log_dateien(logs)
        (abo, api), geparst = log_kosten(logs, split=True, files=files,
                                          return_geparst=True)
        # HM-41/HM-44: nur Dateien, die log_kosten() auch tatsaechlich als
        # gueltig gewertet hat, duerfen archiviert werden -- eine
        # nicht-parsebare ODER eine mit negativem/nicht-endlichem
        # total_cost_usd (0.0 gezaehlt, aber ggf. ein realer, bereits
        # bezahlter Aufruf bzw. ein manipulierter Wert) bleibt liegen statt
        # spurlos im Archiv zu verschwinden.
        nicht_geparst = [f for f in files if f not in geparst]
        for datei in nicht_geparst:
            print(f"Warnung: '{datei}' konnte nicht als JSON gelesen werden "
                  f"oder enthaelt ein unplausibles total_cost_usd (negativ "
                  f"oder nicht-endlich) -- die Datei fehlt in dieser Summe "
                  f"und bleibt UNARCHIVIERT liegen", file=sys.stderr)
        # HM-43: files leer + abo==api==0 ist von "diese Kaskade hatte
        # wirklich keine Team-Kosten" nicht zu unterscheiden, wenn .team-logs
        # bereits archiviert wurde (z. B. durch einen frueheren
        # --archivieren-Lauf) -- team_log_dateien() globbt bewusst nicht
        # rekursiv und sieht archiv/ daher nie. Ohne diese Warnung wurde
        # genau das bei Kaskade 17 real gebucht und war nur per Zufall aus
        # einem Abschluss-Doc rekonstruierbar (siehe Beutebuch HM-43).
        if not files and abo == 0.0 and api == 0.0:
            archiv_belegt = any(
                glob.glob(os.path.join(d, "archiv", "*.json")) for d in logs
            )
            print(
                "Warnung: keine Log-Dateien in "
                f"{', '.join(logs)} gefunden -- es wird 0.0000 USD gebucht. "
                "Pruefe VOR dem Buchen, ob diese Kaskade wirklich keine "
                "Team-Kosten hatte oder ob die Logs bereits archiviert "
                "wurden (siehe .team-logs/archiv/)"
                + (" -- Archiv enthaelt bereits Dateien!" if archiv_belegt else "")
                + ".",
                file=sys.stderr,
            )
        try:
            ersetzt = rollen_abschluss(kaskade, abo, api, domaene,
                                        notiz=notiz, pfad=ledger_pfad)
        except ValueError as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 1
        aktion = "ersetzt" if ersetzt else "angelegt"
        archiv_hinweis = ""
        if archivieren:
            verschoben = _archiviere_dateien(geparst)
            archiv_hinweis = f", {len(verschoben)} Log(s) archiviert"
            if nicht_geparst:
                archiv_hinweis += (f", {len(nicht_geparst)} nicht-parsebare "
                                    f"Log(s) NICHT archiviert")
        print(f"Roles-Zeile Kaskade {kaskade} ({domaene}) {aktion}: "
              f"{abo + api:.4f} USD (abo {abo:.4f} / api {api:.4f})"
              f"{archiv_hinweis}")
        return 0

    print(f"Unbekannter Befehl: {befehl}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))

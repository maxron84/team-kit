#!/usr/bin/env python3
"""Zentrale Kosten-Summierung fuer die T.E.A.M.-Skripte (siehe CLAUDE.md,
Anhang A). Wird von team/lib.sh (team_kosten_summe/team_kosten_split/
team_ledger_summe) aufgerufen, um die frueher doppelt/dreifach gepflegte
Python-Summierung aus vollautomatik.sh und team-status.sh zu buendeln.

Nutzung:
    kosten.py summe [--split] [--since EPOCH] DIR...
                                        Summe total_cost_usd ueber *.json in
                                        den angegebenen Log-Ordnern. Mit
                                        --split getrennt nach "abo<TAB>api"
                                        (api = Dateiname enthaelt
                                        "-api-fallback", siehe team_claude
                                        in team/lib.sh). Mit --since EPOCH nur
                                        Logs, deren mtime >= EPOCH ist (Kosten
                                        EINES Laufs statt lebenslang — Basis der
                                        Pro-Lauf-Deckel-Durchsetzung, BL-18).
    kosten.py ledger [PFAD] [--domaene <domaene>] [--rolle ROLLE]
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
    kosten.py architekt-abschluss --usd USD --domaene <domaene>
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
    kosten.py akteur-abschluss --usd USD --domaene <domaene>
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
    kosten.py rollen-abschluss --kaskade N --domaene <domaene>
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
                                        Strippenzieher-Entscheid). Steht fuer
                                        die Kaskade schon eine roles-Zeile,
                                        BRICHT der Aufruf AB und nennt Alt-,
                                        Neu- und Summenwert (BL-5) —
                                        --addieren bucht den Nachlauf dazu,
                                        --ersetzen korrigiert eine falsche
                                        Altzeile. Zeilen anderer Rollen
                                        (ralph/architekt/…) bleiben immer
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
    kosten.py ralph-abschluss  … (Argumente wie rollen-abschluss)
                                        BL-4: identischer Mechanismus fuer
                                        Ralphs BAUKOSTEN — Quelle .ralph-logs
                                        statt .team-logs, Zielzeile
                                        rolle=ralph statt roles. Bis dahin
                                        landeten Ralphs Kosten in KEINER
                                        Ledger-Zeile: --rollen-abschluss
                                        ledgert per Definition nur .team-logs,
                                        und der Bash-Helfer
                                        team_logs_archivieren() hatte im
                                        ganzen Kit keinen Aufrufer. Weil
                                        .ralph-logs/ per .gitignore nicht ins
                                        Git geht, verlor ein frischer Clone
                                        die gesamte Bau-Kostenhistorie —
                                        genau das, wogegen die Ledger gebaut
                                        wurde (im Feld: 2,1621 von 9,4204
                                        USD). Bewusst ein eigener Verb mit
                                        eigener Zeile statt einer Sammelzeile:
                                        Die Trennung Bau <-> Sweep/Fix ist die
                                        Kennzahl, an der das Fehlen ueberhaupt
                                        auffiel. Die EINE Bedienhandlung
                                        stellt team-status.sh
                                        --rollen-abschluss her, das beide
                                        Verben nacheinander aufruft.
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
# --- Domaenen (projektdefiniert, T.E.A.M.-Starterkit) -------------------------
# Die Domaene trennt Produktarbeit von Team-Infrastrukturarbeit im Ledger.
# WELCHE Namen gelten, bestimmt das Projekt ueber TEAM_DOMAENEN in
# team.config.sh (Leer- oder Kommaliste) — das Werkzeug schreibt keine vor.
# Ohne Konfiguration gilt der neutrale Default unten. Bestehende Ledger-Zeilen
# mit anderen Domaenen bleiben LESBAR (die Validierung greift nur beim
# SCHREIBEN); wer sie weiter beschreiben will, traegt sie in TEAM_DOMAENEN ein.
DEFAULT_DOMAENEN = ("produkt", "team")


def erlaubte_domaenen():
    roh = os.environ.get("TEAM_DOMAENEN", "").replace(",", " ").split()
    return tuple(roh) if roh else DEFAULT_DOMAENEN


def pruefe_domaene(domaene):
    """Wirft ValueError, wenn die Domaene nicht konfiguriert ist."""
    erlaubt = erlaubte_domaenen()
    if domaene not in erlaubt:
        raise ValueError(
            f"domaene muss eine von {'/'.join(erlaubt)} sein, nicht "
            f"'{domaene}' (konfigurierbar ueber TEAM_DOMAENEN in team.config.sh)")


def domaenen_hinweis():
    return "|".join(erlaubte_domaenen())


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
    nie).
    BL-46: Ein ERSATZZETTEL (team_versuch == "verworfen", geschrieben von
    team_versuch_sichern in lib.sh, wenn ein Aufruf ein 0-Byte-Log
    hinterlaesst) traegt total_cost_usd = null. Er zaehlt NICHT als 0.0 mit --
    genau diese stille Null war der Fund: 47 Minuten Laufzeit fielen aus
    jeder Summe heraus und die Stufe erschien als die billigste der Kaskade,
    obwohl sie als teuerste angesetzt war. ok=False heisst hier "Kosten
    unbekannt", nicht "kaputt"; wer beides unterscheiden muss, fragt
    _ist_verworfener_versuch()."""
    try:
        data = json.load(open(datei))
        if isinstance(data, dict) and data.get("team_versuch") == "verworfen":
            return 0.0, False
        kosten = data.get("total_cost_usd", 0)
        if kosten is None:
            return 0.0, False
        kosten = kosten or 0
        if not math.isfinite(kosten) or kosten < 0:
            return 0.0, False
        return kosten, True
    except Exception:
        return 0.0, False


def _ist_verworfener_versuch(datei):
    """True, wenn die Datei ein Ersatzzettel ueber einen verworfenen Versuch
    ist (BL-46). Der Zettel ist KEIN Kostenbeleg -- er haelt fest, dass ein
    bezahlter Anlauf stattfand, dessen Kosten niemand kennt."""
    try:
        data = json.load(open(datei))
    except Exception:
        return False
    return isinstance(data, dict) and data.get("team_versuch") == "verworfen"


def verworfene_versuche(dirs=None, files=None, since=None):
    """Liste (datei, dauer_s) der Ersatzzettel unter dirs bzw. in files.
    dauer_s ist None, wenn der Zettel keine Dauer traegt -- geschaetzt wird
    NICHTS, sichtbar gemacht schon (BL-46)."""
    kandidaten = files if files is not None \
        else team_log_dateien(dirs or [], since=since)
    treffer = []
    for datei in kandidaten:
        if not _ist_verworfener_versuch(datei):
            continue
        try:
            dauer = json.load(open(datei)).get("team_dauer_s")
        except Exception:
            dauer = None
        treffer.append((datei, dauer))
    return treffer


def verworfen_hinweis(treffer):
    """Einzeiler ueber verworfene Versuche -- oder None, wenn es keine gibt."""
    if not treffer:
        return None
    dauern = [d for _, d in treffer if isinstance(d, (int, float))]
    zeit = f", zusammen {sum(dauern) // 60} min" if dauern else ""
    return (f"Hinweis: {len(treffer)} verworfener Versuch(e){zeit}, Kosten "
            f"UNBEKANNT -- nicht in dieser Summe enthalten und bewusst nicht "
            f"geschaetzt (BL-46): "
            + ", ".join(os.path.basename(f) for f, _ in treffer))


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


# --- Ledger-Konsistenz (Roadmap-Skizze D) ------------------------------------
# WARUM es das gibt: Die Kostenmechanik ist die einzige Stelle im Kit, deren
# Fehler STILL sind. Einen Code-Fehler zeigt der Smoke-Test; eine fehlende
# Ledger-Zeile zeigt niemand. BL-1, BL-4 und BL-5 sind alle drei NICHT durch
# ein Werkzeug aufgefallen, sondern dadurch, dass ein Mensch den gedruckten
# Bericht neben das Ledger hielt -- dreimal dasselbe Muster: Ein Bericht, der
# seine Kennzahl aus derselben Quelle zieht wie das, was er pruefen soll,
# bestaetigt einen Fehler, statt ihn zu zeigen. Er zieht seine Gegenkennzahl
# deshalb aus einer ANDEREN Quelle als das Ledger: aus den archivierten
# Rohlogs.
#
# WAS ES BEWUSST NICHT TUT -- und warum: Die Skizze sah den Vergleich "Zeile
# gegen ihre archivierten Rohlogs" JE KASKADE vor. Das ist mit der heutigen
# Ablage nicht ehrlich beantwortbar: Die Log-Dateinamen tragen keine
# Kaskadennummer (stufe-<n>-<ts>.json, harry-<ts>.json,
# frank-<HM>-v<n>-<ts>.json), und das Archiv ist EIN flacher Ordner je Quelle.
# Eine Zuordnung liesse sich nur ueber mtime-Fenster raten -- und geraten wird
# in der Kostenmechanik nichts. Ein Archiv je Kaskade (archiv/kaskade-<n>/)
# waere der saubere Weg, haette aber lauf_kosten() in vollautomatik.sh
# gebrochen: Das globbt .ralph-logs/archiv NICHT-rekursiv und misst den
# Pro-Lauf-Deckel damit auch gegen Geld, das eine Abschluss-Stufe INNERHALB
# des Laufs schon weggeraeumt hat (BL-55). Der Rohlog-Vergleich laeuft
# deshalb je QUELLE statt je Kaskade -- Archivordner und Ledger-Rolle
# entsprechen einander eindeutig, ohne dass irgendetwas zugeordnet werden
# muss. BL-4 (ralph-Zeile fehlte ganz) und BL-5 (Altwert ueberschrieben)
# haette beides genau so angeschlagen.

# Rollen OHNE Rohlog. Die architekt-Zeile ist eine gemessene Schaetzung aus
# dem Sitzungstranskript, ihr entspricht keine Log-Datei. Sie darf deshalb in
# KEINEN Rohlog-Topf wandern: Im Ursprungsprojekt traegt sie 275 USD und haette
# jede echte Untergebuchung maskiert.
LEDGER_OHNE_ROHLOG = ("architekt",)

# Log-Ordner-Attribut -> die Ledger-Rollen, die daraus gespeist werden.
# None bedeutet "alle uebrigen Rollen des Ledgers" (ausser denen anderer
# Ordner und ausser LEDGER_OHNE_ROHLOG).
#
# BL-13: Hier stand eine 1:1-Abbildung roles <-> .team-logs. Die ist falsch,
# sobald ein Projekt eine weitere Rolle SEPARAT bucht — und genau dafuer
# existiert `akteur-abschluss --rolle <X>`. Real: redteam.sh, frank.sh,
# axel.sh und vollautomatik.sh setzen ALLE LOG_DIR=".team-logs", waehrend das
# Ursprungsprojekt Franks Out-of-Loop-Arbeit als eigene `frank`-Zeile bucht
# (17,00 USD). P3 meldete dieses Geld als "archiviert, aber nie gebucht" —
# eine strukturell unaufloesbare Warnung, denn nachbuchen kann man nichts, was
# bereits gebucht IST. Die Rollenmenge wird deshalb aus dem Ledger abgeleitet
# statt festverdrahtet.
LEDGER_ROHQUELLEN = (("ralph_logs", ("ralph",)), ("team_logs", None))
LEDGER_QUELLEN = ("ralph", "roles", "architekt")

# BL-19: Vorspann der Notiz je Zielrolle von `rollen-abschluss`. EIN
# Bedienaufruf (team-status.sh --rollen-abschluss) schreibt zwei Zeilen mit
# demselben Notiztext; der Vorspann sagt, WELCHE Kosten die jeweilige Zeile
# traegt, auch wenn der Text nur zur anderen passt. Unbekannte Rollen
# bekommen ihren eigenen Namen als Vorspann — die Zuordnung fehlt nie.
ROLLEN_VORSPANN = {
    "roles": "Rollen",   # .team-logs: Harry/Marv/Frank/Axel (Sweeps + Fixe)
    "ralph": "Bau",      # .ralph-logs: Ralphs Baustufen
}

# Toleranz des Rohlog-Vergleichs: Jede Ledger-Zeile ist auf 4 Stellen
# gerundet, ueber viele Kaskaden summiert sich das. Absolut 0.01 USD plus 1 %
# haelt Rundung und von Hand auf glatte Werte nachgetragene Altzeilen
# draussen, ohne einen echten Verlust zu verstecken (im Feld: 2.1621 USD).
LEDGER_TOLERANZ_ABS = 0.01
LEDGER_TOLERANZ_REL = 0.01


def _kaskade_key(kaskade):
    """Sortierschluessel: numerische Kaskaden numerisch (sonst steht 10 vor 2),
    benannte danach alphabetisch -- kaskade_aus_plan() laesst beides zu."""
    return (0, int(kaskade), "") if kaskade.isdigit() else (1, 0, kaskade)


def _befund(code, schwere, text):
    return {"code": code, "schwere": schwere, "text": text}


def ledger_pruefen(pfad=".budget-ledger", ralph_logs=".ralph-logs",
                    team_logs=".team-logs", aktuelle_kaskade=None):
    """Prueft das Ledger auf Vollstaendigkeit und liefert eine Liste von
    Befunden (Dicts mit code/schwere/text). schwere ist "warnung" (sehr
    wahrscheinlich verlorenes Geld -- der Aufrufer sollte Exit != 0 setzen)
    oder "hinweis" (kann legitim sein, wird nur gezeigt).

    Drei Pruefungen:

    P1 Vollstaendigkeit je Kaskade -- traegt jede Kaskade eine Zeile je
       Quelle (ralph/roles/architekt)? Eine Kaskade MIT roles-, aber OHNE
       ralph-Zeile ist der BL-4-Fall und damit eine Warnung: Gebaut wurde
       immer, wenn gesweept wurde. Umgekehrt ist eine fehlende roles- oder
       architekt-Zeile nur ein Hinweis -- ein Lauf ohne Red Team und eine
       Kaskade, in der der Architekt nichts abzurechnen hatte, sind moeglich.
       Kaskaden mit AUSSCHLIESSLICH einer architekt-Zeile bleiben ganz
       aussen vor: Das ist eine geplante, noch nicht gelaufene Kaskade.
       Altzeilen im 5-Feld-Schema (rolle=None, BL-29) haben keine Quelle und
       werden nicht bewertet, sondern gezaehlt gemeldet.

    P2 Abgeschlossen, aber unarchiviert -- liegen in .ralph-logs/.team-logs
       noch *.json, obwohl die aktuelle Kaskade bereits gebucht ist? Genau
       die Lage, in der ein zweiter --rollen-abschluss den Altwert
       ueberschrieben hat (BL-5). Unarchivierte Logs waehrend einer OFFENEN
       Kaskade sind dagegen der Normalzustand und ergeben keinen Befund.

    P3 Rohlog-Gegenprobe je Log-Ordner -- ist die Summe der archivierten
       Rohlogs GROESSER als die Summe der zugehoerigen Ledger-Zeilen? Dann ist
       bezahlte Arbeit archiviert, aber nie (oder zu klein) gebucht worden.
       Nur diese Richtung ist ein Befund: Fehlt umgekehrt das Archiv
       (frischer Clone -- die Log-Ordner sind gitignoriert), ist das Ledger
       erwartungsgemaess groesser, und genau dafuer existiert es.
       Ein Ordner kann MEHRERE Ledger-Rollen speisen (BL-13): .ralph-logs
       gehoert Ralph allein, .team-logs dagegen jeder Rolle mit Rohlog --
       redteam.sh, frank.sh, axel.sh und vollautomatik.sh protokollieren alle
       dorthin. Welche Rollen gezaehlt wurden, nennt der Befund ausdruecklich.
    """
    befunde = []
    if not os.path.isfile(pfad):
        return [_befund("kein-ledger", "hinweis",
                         f"Kein Ledger unter '{pfad}' -- es wurde noch nie "
                         f"ein Abschluss gebucht.")]

    zeilen = list(ledger_zeilen(pfad))
    ordner = {"ralph_logs": ralph_logs, "team_logs": team_logs}

    # --- P1 -----------------------------------------------------------------
    je_kaskade = {}
    ohne_quelle = 0
    for zeile in zeilen:
        if zeile["rolle"] is None:
            ohne_quelle += 1
            continue
        je_kaskade.setdefault(zeile["kaskade"], set()).add(zeile["rolle"])
    if ohne_quelle:
        befunde.append(_befund(
            "altzeilen", "hinweis",
            f"{ohne_quelle} Ledger-Zeile(n) im alten 5-Feld-Schema ohne "
            f"Domaene/Rolle -- sie zaehlen als 'unzugeordnet' und koennen "
            f"nicht auf Vollstaendigkeit geprueft werden (BL-29)."))
    for kaskade in sorted(je_kaskade, key=_kaskade_key):
        vorhanden = je_kaskade[kaskade]
        if not vorhanden & {"ralph", "roles"}:
            continue    # geplant, aber nie gelaufen -- nichts zu erwarten
        fehlend = [q for q in LEDGER_QUELLEN if q not in vorhanden]
        if "ralph" in fehlend:
            # BL-14: Nur bei NUMMERIERTEN Kaskaden ist die fehlende
            # ralph-Zeile eine Warnung -- dort gilt "wo gesweept wurde, wurde
            # auch gebaut". Benannte Kaskaden (`post-20`, `roles-post-k13`)
            # sind per Konvention Out-of-Loop-Buchungen: eine Fixserie NACH
            # dem Lauf, in der Ralph gar nicht gebaut hat. Dort ist das Fehlen
            # korrekt, die Warnung dauerhaft unaufloesbar, und sie erscheint
            # bei JEDEM --budget. Genau das erzieht zum Wegsehen, gegen das
            # die zwei Schweregrade ueberhaupt gebaut wurden.
            nummeriert = kaskade.isdigit()
            befunde.append(_befund(
                "ralph-fehlt", "warnung" if nummeriert else "hinweis",
                f"Kaskade {kaskade}: keine ralph-Zeile, obwohl eine "
                f"roles-Zeile steht. " + (
                    f"Die Baukosten des Loops sind nicht gebucht "
                    f"(BL-4-Muster) -- nachtragen mit `./team-status.sh "
                    f"--rollen-abschluss {kaskade} <domaene>`."
                    if nummeriert else
                    "Benannte Kaskade -- bei einer Out-of-Loop-Fixserie hat "
                    "Ralph nicht gebaut, dann ist das korrekt.")))
        for quelle in fehlend:
            if quelle == "ralph":
                continue
            befunde.append(_befund(
                f"{quelle}-fehlt", "hinweis",
                f"Kaskade {kaskade}: keine {quelle}-Zeile. Legitim, wenn "
                + ("kein Red Team lief" if quelle == "roles" else
                    "der Architekt fuer diese Kaskade nichts abzurechnen "
                    "hatte") + " -- sonst fehlt der Abschluss."))

    # --- P2 -----------------------------------------------------------------
    if aktuelle_kaskade is not None and aktuelle_kaskade in je_kaskade:
        alle_offen = team_log_dateien([ralph_logs, team_logs])
        # BL-46: Ein unarchiviertes Log, das gar kein Kostenbeleg IST
        # (Ersatzzettel ueber einen verworfenen Versuch, oder eine kaputte
        # Datei), begruendet keinen Verdacht auf verlorenes Geld. Im Feld
        # meldete P2 danach DAUERHAFT falschen Alarm und schlug zwei Ursachen
        # vor, von denen keine zutraf -- samt der Abhilfe `--ersetzen`, die
        # nach BL-5 den Altwert vernichtet. Ein Waechter, der beim ersten
        # Befolgen Geld kostet und sich nie abstellen laesst, erzieht zum
        # Wegsehen (dieselbe Falle wie BL-14). Deshalb getrennt bewerten.
        rest_offen = [f for f in alle_offen if _ist_verworfener_versuch(f)
                      or not _datei_kosten(f)[1]]
        offen = [f for f in alle_offen if f not in rest_offen]
        if rest_offen:
            verworfen = [f for f in rest_offen if _ist_verworfener_versuch(f)]
            befunde.append(_befund(
                "unarchiviert-ohne-beleg", "hinweis",
                f"{len(rest_offen)} unarchivierte(s) Log(s) in "
                f"{ralph_logs}/{team_logs} sind KEIN Kostenbeleg "
                f"({len(verworfen)} verworfene(r) Versuch(e), "
                f"{len(rest_offen) - len(verworfen)} nicht lesbar) -- kein "
                f"Hinweis auf verlorenes Geld, kein Grund fuer einen zweiten "
                f"Abschluss. Ein Ersatzzettel wird beim naechsten "
                f"`--rollen-abschluss --archivieren` mit weggeraeumt; eine "
                f"nicht lesbare Datei bleibt liegen und gehoert von Hand "
                f"angesehen (BL-46)."))
        if offen:
            befunde.append(_befund(
                "unarchiviert", "warnung",
                f"Kaskade {aktuelle_kaskade} ist bereits gebucht "
                f"({len(je_kaskade[aktuelle_kaskade])} Zeile(n)), aber es "
                f"liegen {len(offen)} unarchivierte Log(s) in "
                f"{ralph_logs}/{team_logs}. Entweder lief danach noch eine "
                f"Rolle (dann `--rollen-abschluss ... --addieren`), oder der "
                f"Abschluss lief ohne --archivieren (dann zaehlt dieselbe "
                f"Arbeit doppelt). Nicht einfach erneut abschliessen: Der "
                f"Default ueberschreibt nicht, aber ein --ersetzen hier "
                f"verliert den Altwert (BL-5)."))

    # --- P3 -----------------------------------------------------------------
    # BL-13: Die Rollenmenge je Ordner wird aus dem Ledger abgeleitet, nicht
    # festverdrahtet. Fest zugeordnete Rollen (ralph) gehoeren ihrem Ordner,
    # LEDGER_OHNE_ROHLOG (architekt) gehoert keinem, alles Uebrige faellt in
    # den Rest-Topf (.team-logs) -- denn dorthin protokollieren redteam.sh,
    # frank.sh, axel.sh und vollautomatik.sh gleichermassen.
    vorhandene_rollen = {z["rolle"] for z in zeilen if z["rolle"]}
    fest_zugeordnet = {r for _, rollen in LEDGER_ROHQUELLEN if rollen
                       for r in rollen}
    for ordner_attr, rollen in LEDGER_ROHQUELLEN:
        if rollen is None:
            rollen = tuple(sorted(vorhandene_rollen - fest_zugeordnet
                                  - set(LEDGER_OHNE_ROHLOG)))
        if not rollen:
            continue
        archiv = os.path.join(ordner[ordner_attr], "archiv")
        if not os.path.isdir(archiv):
            continue
        roh = log_kosten([archiv])
        gebucht = sum(ledger_summe(pfad, rolle=r) for r in rollen)
        differenz = roh - gebucht
        toleranz = max(LEDGER_TOLERANZ_ABS, roh * LEDGER_TOLERANZ_REL)
        if differenz > toleranz:
            # Der Befund nennt die gezaehlten Rollen ausdruecklich: Ein Mensch
            # muss die Zahl nachrechnen koennen, und genau dieses Nachrechnen
            # hat BL-1, BL-4 und BL-5 ueberhaupt erst gefunden.
            benannt = "/".join(rollen)
            befunde.append(_befund(
                f"{rollen[0]}-untergebucht", "warnung",
                f"Quelle '{benannt}': archivierte Rohlogs in {archiv} ergeben "
                f"{roh:.4f} USD, die Ledger-Zeilen der Rolle(n) {benannt} nur "
                f"{gebucht:.4f} USD -- {differenz:.4f} USD sind archiviert, "
                f"aber nie gebucht. So sahen BL-4 (Zeile fehlte ganz) und "
                f"BL-5 (Altwert ueberschrieben) im Feld aus."))
    return befunde


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
    team-status.sh/team/lib.sh aufgerufen) unabhaengig vom Aufrufer, statt
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


def _ledger_zeile_setzen(zeile_neu, match_fn, pfad=".budget-ledger",
                          merge_fn=None):
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
    vorhandene Zeile ersetzt wurde, sonst False (neu angelegt).

    merge_fn (BL-5, optional): wird mit den Feldern der EINEN bestehenden
    Treffer-Zeile aufgerufen und liefert die Zeile, die stattdessen
    geschrieben wird -- so kann der Aufrufer den Altwert BERUECKSICHTIGEN
    (addieren) oder den Vorgang ABBRECHEN (ValueError werfen), statt ihn
    blind zu ueberschreiben. Der Aufruf passiert INNERHALB des Ledger-Locks
    und VOR jedem Schreibzugriff: Wirft merge_fn, bleibt die Datei
    unangetastet. Ohne merge_fn bleibt das Verhalten unveraendert
    (Ersetzen) — akteur_abschluss() braucht genau das, weil dort ein
    absoluter, extern gemessener USD-Wert uebergeben wird."""
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
        zeile_final = zeile_neu
        for rohzeile in bestehend:
            stripped = rohzeile.strip()
            if not stripped or stripped.startswith("#"):
                behalten.append(rohzeile)
                continue
            felder = [f.strip() for f in stripped.split("|")]
            if match_fn(felder):
                ersetzt = True
                # BL-5: Vor JEDEM Schreibzugriff -- wirft merge_fn, bleibt
                # die Datei unangetastet (Temp-Datei ist noch nicht angelegt).
                if merge_fn is not None:
                    zeile_final = merge_fn(felder)
                continue
            behalten.append(rohzeile)

        if behalten and not behalten[-1].endswith("\n"):
            behalten[-1] += "\n"
        behalten.append(zeile_final)

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
    pruefe_domaene(domaene)
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
                      pfad=".budget-ledger", bestand="abbrechen",
                      rolle="roles"):
    """Kaskadenscharfe Rollenkosten (BL-17-Restpunkt/BL-29-"1b", Kaskade
    16/Stufe 54): haengt EINE rolle=roles-Ledger-Zeile fuer die
    .team-logs-Kosten (Harry/Marv/Frank/Axel) EINER Kaskade an. usd = abo +
    api; auth = "abo" (api==0), "api" (abo==0), sonst "abo/api" —
    Strippenzieher-Entscheid: Kaskadenschaerfe schlaegt Abo/API-Schaerfe je
    Rollenzeile, der gemischte Fall ist erwartet und wird ehrlich als
    "abo/api" ausgewiesen (kein geratener Split). notiz wird um den exakten
    Split ergaenzt und traegt voran den Rollenbezug ("Rollen: …" / "Bau: …",
    BL-19), analog der bestehenden roles-total-Zeile. Zeilen anderer
    Rollen (ralph/architekt/…) bleiben immer unangetastet. Wirft ValueError
    bei ungueltigen Eingaben, OHNE die Datei anzufassen. Gibt True zurueck,
    wenn eine vorhandene Zeile angefasst wurde, sonst False (neu angelegt).

    rolle (BL-4): Zielrolle der Zeile. "roles" (Default) fuer die
    .team-logs-Kosten von Harry/Marv/Frank/Axel, "ralph" fuer die
    .ralph-logs-Baukosten. Bewusst ZWEI Zeilen statt einer gemeinsamen:
    Die Trennung Bau <-> Sweep/Fix ist die Kennzahl, an der im Feld
    ueberhaupt auffiel, dass Ralph fehlte.

    bestand (BL-5) — was passiert, wenn fuer DIESE Kaskade schon eine
    Zeile dieser Rolle steht:

      "abbrechen" (Default)  ValueError, Datei unangetastet. Die Meldung
                             nennt Alt-, Neu- und Summenwert.
      "addieren"             Neuer Wert wird auf den Altwert ADDIERT.
      "ersetzen"             Altes Verhalten: Altwert wird ueberschrieben.

    WARUM der Default nicht mehr "ersetzen" ist: Der uebergebene Wert wird
    aus den NOCH NICHT ARCHIVIERTEN Logs gezaehlt. Weil ein Abschluss mit
    --archivieren die gezaehlten Logs anschliessend wegraeumt, sieht jeder
    weitere Aufruf eine DISJUNKTE Restmenge — ein Nachlauf (z. B. Frank
    laeuft nach dem Closeout noch) ergibt also einen KLEINEREN Wert, der die
    groessere Altbuchung ueberschrieben und geloescht hat. Real eingetreten
    (Feld-Kaskade 1: 1,0969 wurde durch 2,4114 ersetzt, Differenz nur per
    Hand rekonstruierbar). Fuer disjunkte Mengen ist ADDIEREN die richtige
    Verknuepfung, nicht Ersetzen — Ersetzen war aus akteur_abschluss()
    uebernommen, wo der Aufrufer einen absoluten, extern gemessenen Wert
    liefert und Ersetzen deshalb korrekt ist. Der Default bricht trotzdem
    lieber ab, statt automatisch zu addieren: Ohne --archivieren zaehlen
    zwei Aufrufe DIESELBEN Logs, dann waere Addieren eine Doppelbuchung.
    Die Entscheidung gehoert damit dem Menschen, nicht der Heuristik."""
    pruefe_domaene(domaene)
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

    rolle = _sanitize_pipe_feld(rolle)
    if not rolle:
        raise ValueError("rolle darf nicht leer sein")

    notiz_sauber = _sanitize_pipe_feld(notiz)
    split_hinweis = f"abo {abo:.4f} / api {api:.4f}"
    # BL-19: Vorspann JE ZIELROLLE. team-status.sh --rollen-abschluss ruft
    # dieses Verb zweimal mit DEMSELBEN Notiztext auf (roles + ralph, BL-4) —
    # ein Text kann aber hoechstens eine der beiden Zeilen beschreiben. Im
    # Feld trug Ralphs Zeile ueber vier Baustufen deshalb die Notiz
    # "Harry/Marv-Sweeps + Frank HM-6". Das ist keine Kosmetik: Die Ledger ist
    # die maschinelle Wahrheit fuer ein kalt startendes Architekt-Ich, und
    # dieses Feld ist die einzige Prosa-Spur je Zeile. Ein Rueckfall obendrein
    # — genau diese Beschwerde stand schon in Feld-BL-5, der BL-4-Fix hat sie
    # strukturell wieder eingebaut.
    # Strippenzieher-Entscheid 2026-08-02: der Vorspann entsteht HIER, aus der
    # Zielrolle, nicht aus einem zweiten Bedienparameter — die Bedienung
    # bleibt einhaendig (ein Notiztext), und auch ein direkter kosten.py-
    # Aufruf bekommt die Zuordnung, ohne sie mitschreiben zu muessen.
    vorspann = ROLLEN_VORSPANN.get(rolle, rolle.capitalize())
    notiz_voll = f"{vorspann}: {notiz_sauber} — {split_hinweis}" \
        if notiz_sauber else f"{vorspann} — {split_hinweis}"
    zeile_neu = (f"{date.today().isoformat()} | {kaskade} | {usd:.4f} | "
                 f"{auth} | {domaene} | {rolle} | {notiz_voll}\n")

    def match_fn(felder):
        return len(felder) >= 7 and felder[1] == kaskade and felder[5] == rolle

    if bestand not in ("abbrechen", "addieren", "ersetzen"):
        raise ValueError(
            f"bestand muss 'abbrechen', 'addieren' oder 'ersetzen' sein, "
            f"nicht '{bestand}'")
    if bestand == "ersetzen":
        return _ledger_zeile_setzen(zeile_neu, match_fn, pfad)

    def alt_usd(felder):
        """USD-Feld der bestehenden Zeile. Nur Feld 2 wird gelesen — ein
        maschinengeschriebener Zahlwert. Der abo/api-Split der Altzeile wird
        BEWUSST NICHT aus der Notiz zurueckgeparst: Notizen werden real von
        Hand korrigiert (Feld-Kaskade 1), ein Parser darauf waere die
        naechste stille Fehlerquelle."""
        try:
            wert = float(felder[2])
        except (IndexError, ValueError):
            raise ValueError(
                f"Die bestehende {rolle}-Zeile der Kaskade {kaskade} hat kein "
                f"lesbares USD-Feld ({felder[2] if len(felder) > 2 else '—'}). "
                "Es wird NICHTS geschrieben — die Zeile von Hand pruefen.")
        if not math.isfinite(wert) or wert < 0:
            raise ValueError(
                f"Die bestehende {rolle}-Zeile der Kaskade {kaskade} traegt "
                f"einen unplausiblen Wert ({wert}). Es wird NICHTS "
                "geschrieben — die Zeile von Hand pruefen.")
        return wert

    def merge_fn(felder):
        alt = alt_usd(felder)
        if bestand == "abbrechen":
            raise ValueError(
                f"Fuer Kaskade {kaskade} steht bereits eine {rolle}-Zeile ueber "
                f"{alt:.4f} USD. Dieser Aufruf wuerde sie durch {usd:.4f} USD "
                f"ERSETZEN und die Differenz verlieren. Es wird NICHTS "
                f"geschrieben.\n"
                f"  Nachlauf (weitere Rolle lief nach dem Abschluss): "
                f"--addieren  -> {alt + usd:.4f} USD\n"
                f"  Korrektur (die Altzeile war falsch):              "
                f"--ersetzen  -> {usd:.4f} USD\n"
                f"  Wurde seit der Altzeile NICHT archiviert, zaehlen beide "
                f"Aufrufe dieselben Logs — dann ist --ersetzen richtig.")
        summe = alt + usd
        # auth der Summenzeile: nur wenn Alt- und Neuanteil dieselbe
        # Auth-Art tragen, bleibt sie erhalten — sonst ehrlich "abo/api".
        alt_auth = felder[3] if len(felder) > 3 else ""
        auth_summe = auth if alt_auth == auth else "abo/api"
        notiz_summe = (f"{notiz_voll} (addiert auf Bestand {alt:.4f} USD, "
                       f"auth {alt_auth or '—'})")
        # rolle NICHT hart verdrahten: Ein --addieren auf die ralph-Zeile
        # haette sie sonst in eine zweite roles-Zeile verwandelt und die
        # Baukosten damit erneut unsichtbar gemacht — genau der BL-4-Fehler,
        # nur eine Ebene tiefer. Beim manuellen Durchlauf aufgefallen,
        # nicht von den Tests (die pruefen je Rolle nur einen Modus).
        return (f"{date.today().isoformat()} | {kaskade} | {summe:.4f} | "
                f"{auth_summe} | {domaene} | {rolle} | {notiz_summe}\n")

    return _ledger_zeile_setzen(zeile_neu, match_fn, pfad, merge_fn=merge_fn)


def _main(argv):
    if not argv:
        print("Nutzung: kosten.py summe [--split] DIR... | ledger [PFAD] | "
              "ledger-pruefen [--pfad P] [--kaskade N]",
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
        # BL-46: Dies ist der STILLE Pfad -- Live-Kontostand, --budget und die
        # Pro-Lauf-/Pro-Stufe-Deckel lesen hier. Ein verworfener Versuch trug
        # bisher 0.0000 bei und war von "hat nichts gekostet" nicht zu
        # unterscheiden. Die Zahl auf stdout bleibt unveraendert (Aufrufer
        # parsen sie); der Hinweis geht nach stderr, damit die Luecke sichtbar
        # ist, ohne einen einzigen Aufrufer zu brechen.
        hinweis = verworfen_hinweis(verworfene_versuche(rest, since=since))
        if hinweis:
            print(hinweis, file=sys.stderr)
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
                    print("Fehler: --domaene braucht einen Wert (siehe TEAM_DOMAENEN)",
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
        # LESEPFAD: keine Validierung. Ein Ledger kann historische Zeilen mit
        # Domaenen enthalten, die heute nicht mehr konfiguriert sind — die muss
        # man weiterhin filtern und summieren koennen. Ein unbekannter Filter
        # liefert schlicht 0. Validiert wird nur beim SCHREIBEN.
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

    # Skizze D: Konsistenzpruefung. Exit 4 (nicht 1) bei Warnbefunden --
    # 1 bleibt dem Bedienfehler vorbehalten, damit ein Aufrufer "Werkzeug
    # falsch benutzt" von "Ledger unvollstaendig" unterscheiden kann. Bewusst
    # KEIN hartes Gate im Closeout: Eine Kaskade mit legitim fehlender Zeile
    # duerfte sonst nicht abschliessen, und ein Gate, das man regelmaessig
    # umgehen muss, wird umgangen. Der Befund laeuft stattdessen bei jedem
    # --budget ungefragt mit.
    if befehl == "ledger-pruefen":
        pfad = ".budget-ledger"
        repo = "."
        ralph_logs = ".ralph-logs"
        team_logs = ".team-logs"
        kaskade = None
        i = 0
        while i < len(rest):
            if rest[i] == "--pfad":
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
            elif rest[i] == "--ralph-logs":
                if i + 1 >= len(rest):
                    print("Fehler: --ralph-logs braucht einen Pfad",
                          file=sys.stderr)
                    return 1
                ralph_logs = rest[i + 1]
                i += 2
            elif rest[i] == "--team-logs":
                if i + 1 >= len(rest):
                    print("Fehler: --team-logs braucht einen Pfad",
                          file=sys.stderr)
                    return 1
                team_logs = rest[i + 1]
                i += 2
            elif rest[i] == "--kaskade":
                if i + 1 >= len(rest):
                    print("Fehler: --kaskade braucht einen Wert",
                          file=sys.stderr)
                    return 1
                kaskade = rest[i + 1]
                i += 2
            else:
                print(f"Fehler: unbekanntes Argument '{rest[i]}'",
                      file=sys.stderr)
                return 1

        ledger_pfad = pfad if os.path.isabs(pfad) or repo == "." \
            else os.path.join(repo, pfad)
        if kaskade is None:
            kaskade = kaskade_aus_plan(repo)
        befunde = ledger_pruefen(ledger_pfad, ralph_logs=ralph_logs,
                                  team_logs=team_logs,
                                  aktuelle_kaskade=kaskade)
        warnungen = [b for b in befunde if b["schwere"] == "warnung"]
        if not befunde:
            print("Ledger konsistent: keine Befunde.")
            return 0
        for b in befunde:
            marke = "WARNUNG" if b["schwere"] == "warnung" else "Hinweis"
            print(f"[{marke}] {b['text']}")
        print(f"-- {len(warnungen)} Warnung(en), "
              f"{len(befunde) - len(warnungen)} Hinweis(e).")
        return 4 if warnungen else 0

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
                    print("Fehler: --domaene braucht einen Wert (siehe TEAM_DOMAENEN)",
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
            print("Fehler: --domaene <domaene> ist Pflicht", file=sys.stderr)
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

    # BL-4: ralph-abschluss ist derselbe Mechanismus mit anderer Quelle und
    # anderer Zielzeile — .ralph-logs statt .team-logs, rolle=ralph statt
    # roles. Bewusst ein eigener Verb statt einer Erweiterung von
    # rollen-abschluss: zwei getrennte Ledger-Zeilen halten die Trennung
    # Bau <-> Sweep/Fix, an der im Feld ueberhaupt auffiel, dass Ralph fehlte.
    # Die EINE Bedienhandlung stellt team-status.sh --rollen-abschluss her,
    # das beide Verben nacheinander aufruft.
    if befehl in ("rollen-abschluss", "ralph-abschluss"):
        ist_ralph = befehl == "ralph-abschluss"
        rolle_ziel = "ralph" if ist_ralph else "roles"
        logs_default = ".ralph-logs" if ist_ralph else ".team-logs"
        kaskade = None
        domaene = None
        notiz = ""
        logs = None
        pfad = ".budget-ledger"
        repo = "."
        archivieren = False
        bestand = "abbrechen"   # BL-5: nie stillschweigend ueberschreiben
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
                    print("Fehler: --domaene braucht einen Wert (siehe TEAM_DOMAENEN)",
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
            elif rest[i] == "--addieren":
                bestand = "addieren"
                i += 1
            elif rest[i] == "--ersetzen":
                bestand = "ersetzen"
                i += 1
            else:
                print(f"Fehler: unbekanntes Argument '{rest[i]}'", file=sys.stderr)
                return 1

        if domaene is None:
            print("Fehler: --domaene <domaene> ist Pflicht", file=sys.stderr)
            return 1
        if kaskade is None:
            kaskade = kaskade_aus_plan(repo)
        if not logs:
            logs = [logs_default]

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
        # BL-46: Ein Ersatzzettel ueber einen verworfenen Versuch ist gerade
        # KEIN Kostenbeleg -- er kann nicht doppelt zaehlen, und liegen zu
        # bleiben hilft ihm nicht: Im Feld hat genau das den Dauer-Fehlalarm
        # von ledger-pruefen erzeugt, ohne dass es einen dokumentierten Weg
        # heraus gab. Er wird deshalb MIT archiviert und dabei benannt. Nur
        # wirklich unlesbare Dateien bleiben liegen (dort koennte echtes,
        # bezahltes Geld drinstehen) -- und die Meldung nennt jetzt den Weg
        # heraus, statt den Menschen mit der Datei allein zu lassen.
        verworfen_liste = [f for f in nicht_geparst
                           if _ist_verworfener_versuch(f)]
        kaputt = [f for f in nicht_geparst if f not in verworfen_liste]
        for datei, dauer in verworfene_versuche(files=verworfen_liste):
            zeit = f"{dauer} s" if isinstance(dauer, (int, float)) else "unbekannter Dauer"
            print(f"Hinweis: '{datei}' ist ein verworfener Versuch ({zeit}, "
                  f"Kosten UNBEKANNT) -- er fehlt in dieser Summe und wird "
                  f"nicht geschaetzt. Der Betrag dieser Kaskade ist damit "
                  f"nachweislich UNVOLLSTAENDIG (BL-46).", file=sys.stderr)
        for datei in kaputt:
            print(f"Warnung: '{datei}' konnte nicht als JSON gelesen werden "
                  f"oder enthaelt ein unplausibles total_cost_usd (negativ "
                  f"oder nicht-endlich) -- die Datei fehlt in dieser Summe "
                  f"und bleibt UNARCHIVIERT liegen. Weg heraus: Inhalt "
                  f"ansehen; steht ein echter Betrag darin, ihn mit "
                  f"`akteur-abschluss` nachbuchen, sonst die Datei von Hand "
                  f"nach {os.path.join(os.path.dirname(datei) or '.', 'archiv')}/ "
                  f"verschieben", file=sys.stderr)
        # HM-43: files leer + abo==api==0 ist von "diese Kaskade hatte
        # wirklich keine Team-Kosten" nicht zu unterscheiden, wenn .team-logs
        # bereits archiviert wurde (z. B. durch einen frueheren
        # --archivieren-Lauf) -- team_log_dateien() globbt bewusst nicht
        # rekursiv und sieht archiv/ daher nie. Ohne diese Warnung wurde
        # genau das bei Kaskade 17 real gebucht und war nur per Zufall aus
        # einem Abschluss-Doc rekonstruierbar (siehe Beutebuch HM-43).
        # Nichts zu addieren ist ein No-Op, keine Buchung: Beim Nachlauf einer
        # EINZELNEN Rolle ist die jeweils andere Quelle regulaer leer (Frank
        # laeuft nach, Ralph nicht). Ohne diesen Zweig schrieb --addieren dort
        # "+0.0000" und ueberschrieb dabei Datum und Notiz der bestehenden
        # Zeile mit dem Text des fremden Nachlaufs — plus einer Warnung, die
        # in genau diesem Fall in die Irre fuehrt. Beim manuellen Durchlauf
        # aufgefallen. Nur im addieren-Modus: Ohne bestehende Zeile ist die
        # 0.0000-Buchung samt HM-43-Warnung weiterhin richtig.
        if bestand == "addieren" and not files and abo == 0.0 and api == 0.0:
            print(f"{rolle_ziel.capitalize()}-Zeile Kaskade {kaskade} "
                  f"({domaene}) unveraendert: nichts hinzuzufuegen "
                  f"(keine neuen Logs in {', '.join(logs)}).")
            return 0
        if not files and abo == 0.0 and api == 0.0:
            archiv_belegt = any(
                glob.glob(os.path.join(d, "archiv", "*.json")) for d in logs
            )
            print(
                "Warnung: keine Log-Dateien in "
                f"{', '.join(logs)} gefunden -- es wird 0.0000 USD gebucht. "
                "Pruefe VOR dem Buchen, ob diese Kaskade wirklich keine "
                "Kosten hatte oder ob die Logs bereits archiviert "
                f"wurden (siehe {logs_default}/archiv/)"
                + (" -- Archiv enthaelt bereits Dateien!" if archiv_belegt else "")
                + ".",
                file=sys.stderr,
            )
        try:
            angefasst = rollen_abschluss(kaskade, abo, api, domaene,
                                          notiz=notiz, pfad=ledger_pfad,
                                          bestand=bestand, rolle=rolle_ziel)
        except ValueError as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 1
        if not angefasst:
            aktion = "angelegt"
        else:
            aktion = "addiert" if bestand == "addieren" else "ersetzt"
        archiv_hinweis = ""
        if archivieren:
            verschoben = _archiviere_dateien(geparst + verworfen_liste)
            archiv_hinweis = f", {len(verschoben)} Log(s) archiviert"
            if verworfen_liste:
                archiv_hinweis += (f" (davon {len(verworfen_liste)} verworfene"
                                    f"(r) Versuch(e) ohne Kostenbeleg)")
            if kaputt:
                archiv_hinweis += (f", {len(kaputt)} nicht-parsebare "
                                    f"Log(s) NICHT archiviert")
        # Bei "addiert" ist abo+api der ZUGANG, nicht der neue Zeilenwert —
        # das Vorzeichen macht den Unterschied sichtbar (BL-5).
        betrag = f"{'+' if aktion == 'addiert' else ''}{abo + api:.4f}"
        print(f"{rolle_ziel.capitalize()}-Zeile Kaskade {kaskade} "
              f"({domaene}) {aktion}: "
              f"{betrag} USD (abo {abo:.4f} / api {api:.4f})"
              f"{archiv_hinweis}")
        return 0

    print(f"Unbekannter Befehl: {befehl}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))

#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteilter Zustandscode, bewusst nicht portiert)
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
              [--auth abo|api] [--kaskade N] [--notiz TEXT] [--pfad PFAD]
              [--repo DIR]
                                        A1-Ersetzung (BL-28, Kaskade 13/
                                        Stufe 43): haengt die ECHTE
                                        Architekt-Ledger-Zeile an
                                        (rolle=architekt, auth VORBELEGT mit
                                        abo — BL-143) fuer die Kaskade, die
                                        der Stakeholder aus der Anthropic-
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
                                        --rolle architekt vorbelegt (BL-33,
                                        Stufe 50).

                                        BL-143: --auth war hier FEST "api"
                                        und buchte damit gegen die eigene
                                        Regel ("keine Rolle ist mehr fest
                                        api"); im Feld landeten 16,3990 USD
                                        Abo-Gegenwert in der Zeile "real via
                                        API abgerechnet". Jetzt vorbelegt mit
                                        "abo" und ueberschreibbar, fuer den
                                        Architekten, der wirklich ueber einen
                                        API-Key gearbeitet hat. Die
                                        Erfolgsmeldung NENNT die Achse —
                                        ohne sie liest sich ein Fehlgriff
                                        nicht.
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
                                        Stakeholder-Entscheid). Steht fuer
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
import glob
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date

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

# Dateisperren sind das EINZIGE plattformabhaengige Stueck dieser Datei
# (BL-125). `fcntl` gibt es unter Windows nicht, `msvcrt` nicht unter Linux.
# Ein UNGESCHUETZTES `import fcntl` auf Modulebene macht dabei nicht nur die
# Sperre unbrauchbar, sondern die GANZE Datei: Unter Windows scheiterte damit
# jeder Import von kosten.py — also jeder Kostenpfad der pwsh-Bahn
# (--akteur-abschluss, --rollen-abschluss, --ralph-abschluss) und die
# Sammlung von 21 Testdateien, die kosten.py importieren. Ein Modul, das ein
# Betriebssystem nicht laden kann, faellt am lautesten und an der am
# wenigsten aussagekraeftigen Stelle: beim Programmstart.
#
# Deshalb werden beide Module WEICH geladen, und die Entscheidung faellt
# erst dort, wo wirklich gesperrt wird (_lock_belegen). Fehlt beides, ist
# das ein benannter Fehler an der richtigen Stelle — und es wird bewusst
# NICHTS ungesichert geschrieben (HM-48).
try:
    import fcntl  # POSIX
except ModuleNotFoundError:  # pragma: no cover - plattformabhaengig
    fcntl = None
try:
    import msvcrt  # Windows
except ModuleNotFoundError:  # pragma: no cover - plattformabhaengig
    msvcrt = None

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
# Dateien, in die anderswo geloeschte Zeilen nur UMZIEHEN (BL-32).
_IST_ARCHIVDATEI = re.compile(r"(^|/)[^/]*archiv[^/]*\.md$", re.I)


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
        data = json.load(open(datei, encoding="utf-8-sig"))
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
        data = json.load(open(datei, encoding="utf-8-sig"))
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
            with open(datei, encoding="utf-8-sig") as fh:
                dauer = json.load(fh).get("team_dauer_s")
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
    with open(pfad, encoding="utf-8") as fh:
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
                    team_logs=".team-logs", aktuelle_kaskade=None, repo="."):
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

    # --- P1b (BL-27) --------------------------------------------------------
    # P1 winkt jede Kaskade ohne ralph/roles-Zeile als "geplant, aber nie
    # gelaufen" durch. Eine GEBAUTE Kaskade mit vergessenem Rollenabschluss
    # sieht genauso aus — im Feld lagen so 33,89 USD ungebucht in den
    # gitignorierten Logordnern, und der Waechter meldete null Warnungen.
    # Das Unterscheidungsmerkmal lag daneben: Eine geplante Kaskade hat KEINE
    # unarchivierten Rohlogs, eine vergessene hat welche.
    #
    # Das ALTER der Logs ist das Merkmal, nicht ihre blosse Anwesenheit:
    # Unarchivierte Logs waehrend eines laufenden Baus sind der Normalzustand
    # (dafuer steht die Gegenprobe in test_bl13) — eine Warnung darauf waere
    # die Falle aus BL-14 und erschiene bei jedem --budget mitten im Lauf.
    # Ein Log, das AELTER ist als der Beginn der aktuellen Kaskade, kann
    # dagegen nicht zu ihr gehoeren: Es stammt aus einem Durchgang, den
    # niemand abgeschlossen hat. Genau so lag der Feldfall — beim Closeout der
    # Kaskade 13 lagen die Logs der Kaskade 12 noch da.
    #
    # Ist der Beginn nicht ermittelbar (keine Plandatei, kein Git), wird NICHT
    # geraten: kein Befund. Ersatzzettel und unlesbare Dateien zaehlen nicht
    # mit (BL-46) — sonst kehrt der Dauer-Fehlalarm durch die Hintertuer
    # zurueck, den P2 dort abgestellt hat.
    if aktuelle_kaskade is not None and \
            not je_kaskade.get(aktuelle_kaskade, set()) & {"ralph", "roles"}:
        beleg_offen = [f for f in team_log_dateien([ralph_logs, team_logs])
                       if not _ist_verworfener_versuch(f)
                       and _datei_kosten(f)[1]]
        _, zu_alt = logs_vor_kaskadenbeginn(beleg_offen, aktuelle_kaskade, repo)
        if zu_alt:
            summe_offen = sum(_datei_kosten(f)[0] for f, _ in zu_alt)
            befunde.append(_befund(
                "abschluss-fehlt", "warnung",
                f"{len(zu_alt)} unarchivierte(s) Log(s) ueber "
                f"{summe_offen:.4f} USD in {ralph_logs}/{team_logs} sind "
                f"AELTER als der Beginn der Kaskade {aktuelle_kaskade} — sie "
                f"gehoeren zu einem frueheren Durchgang, fuer den kein "
                f"Rollenabschluss gebucht ist. Eine geplante Kaskade hat keine "
                f"Rohlogs; hier wurde gebaut und nicht abgeschlossen "
                f"(BL-27-Muster). Nachtragen mit `./team-status.sh "
                f"--rollen-abschluss <jene Kaskade> <domaene>`."))

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


def turn_profil(dirs, files=None):
    """(anzahl_laeufe, gesamt_turns, [(datei, turns, usd), …]) aus den
    num_turns-Feldern der Rohlogs — absteigend nach Turns.

    BL-37 (c): Das Turn-Profil ist die DIAGNOSE eines Planfehlers. Im Feld lief
    eine als "die einfachere Zustandsmaschine" mit 3,0 USD angesetzte Stufe auf
    5,90 USD — ihr Profil waren 87 Turns in 13 Minuten, waehrend die TEUREREN
    Nachbarstufen mit 47/57 Turns ueber 17 Minuten liefen. Viele kurze Turns =
    Nacharbeit (der Schnitt war falsch), wenige lange = Urteilsarbeit (der
    Schnitt war richtig). Die Zahl steht in jedem Log und wurde bis hierher
    nirgends ausgewertet."""
    if files is None:
        files = team_log_dateien(dirs)
    zeilen = []
    for datei in files:
        try:
            data = json.load(open(datei, encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        turns = data.get("num_turns")
        if not isinstance(turns, int) or turns < 0:
            continue
        kosten, ok = _datei_kosten(datei)
        zeilen.append((datei, turns, kosten if ok else None))
    zeilen.sort(key=lambda z: z[1], reverse=True)
    return len(zeilen), sum(z[1] for z in zeilen), zeilen


def kaskade_beginn(kaskade, repo="."):
    """Epoch-Zeitstempel des Commits, der die PLANDATEI der Kaskade angelegt
    hat — der maschinell verfuegbare Beginn eines Laufs. None, wenn keine
    Plandatei oder kein Git-Repo gefunden wird.

    Warum die Plandatei und nicht der erste Stufen-Commit: Sie entsteht bei
    der Scharfschaltung, also VOR der ersten Stufe, und traegt die Nummer im
    Namen. Ein Stufen-Commit ist an nichts erkennbar, was ein Werkzeug lesen
    koennte.

    BL-45: Gebraucht wird das fuer den Zeitraum-Abgleich beim Buchen —
    `--rollen-abschluss` bucht schlicht ALLES, was im Logordner liegt, unter
    der genannten Nummer. Im Feld lag dort ein Axel-Lauf ueber 4,2560 USD aus
    einer Out-of-Loop-Fixrunde, die NACH dem Abschluss der Kaskade 27 und VOR
    dem ersten Commit der Kaskade 28 stattfand — er gehoert zu keiner der
    beiden und waere still falsch beschriftet in die K28-Zeile gelaufen.
    Auffallen konnte das nur einem Menschen, der die Zeitstempel von Hand
    gegen den Kaskadenbeginn haelt."""
    if not kaskade:
        return None
    muster = os.path.join(repo, "plans", f"ralph-kaskade-{kaskade}-*.md")
    treffer = sorted(glob.glob(muster))
    if not treffer:
        return None
    relativ = os.path.relpath(treffer[0], repo)
    try:
        ergebnis = subprocess.run(
            ["git", "-C", repo, "log", "--diff-filter=A", "--format=%ct",
             "--", relativ],
            capture_output=True, text=True, check=False)
    except OSError:
        return None
    zeilen = [z for z in ergebnis.stdout.split() if z.isdigit()]
    if not zeilen:
        return None
    return int(zeilen[-1])   # aeltester Add-Commit


def logs_vor_kaskadenbeginn(files, kaskade, repo="."):
    """(beginn, [(datei, mtime), …]) fuer alle Logs, die AELTER sind als der
    Beginn der zu buchenden Kaskade (BL-45). Leere Liste, wenn der Beginn
    nicht ermittelbar ist — dann wird nicht geraten."""
    beginn = kaskade_beginn(kaskade, repo)
    if beginn is None:
        return None, []
    zu_alt = []
    for datei in files:
        try:
            mtime = os.path.getmtime(datei)
        except OSError:
            continue
        if mtime < beginn:
            zu_alt.append((datei, mtime))
    return beginn, sorted(zu_alt, key=lambda p: p[1])


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
        # BL-32 (b): Reine DATEIROTATION ist kein Churn. Zeilen, die aus dem
        # aktiven Dokument ins Archiv wandern, sind ein Werkzeugaufruf und kein
        # Gedanke — im Feld sprang der Schaetzer nach einer Beutebuch-Rotation
        # von 2.456 Zeilen auf 43,68 USD fuer eine Sitzung, in der niemand
        # nachgedacht hatte. Die Archivdateien fallen deshalb heraus; die
        # Loeschung im Aktivdokument bleibt drin (sie ist von einer echten
        # Streichung nicht unterscheidbar, und Untertreiben ist hier der
        # kleinere Fehler).
        if len(felder) > 2 and _IST_ARCHIVDATEI.search(felder[2]):
            continue
        try:
            churn += int(hinzu) + int(weg)
        except ValueError:
            continue
    return churn


def architekt_schaetzung(seit, pfade=("plans", "CLAUDE.md"), repo="."):
    churn = git_churn(seit, pfade, repo=repo)
    return churn, churn * ARCHITEKT_USD_PRO_CHURN_ZEILE


# --- BL-141: Sitzungskosten MESSEN statt schaetzen -------------------------
#
# architekt_schaetzung() oben rechnet Zeilen-Churn mal Eichfaktor. Das misst
# die GROESSE DES DIFFS, nicht die Arbeit: Eine Sitzung mit viel Lesen, Pruefen
# und Gegenproben und wenig geschriebenem Text wird systematisch unterschaetzt,
# eine Prosa-Sitzung ueberschaetzt. Im Feld (Feld B, Kaskade 1) meldete
# die Zeile 7,6861 USD; die Messung aus dem Sitzungstranskript ergab 11,7582 —
# 35 % zu niedrig.
#
# Das Architekten-Briefing verlangt die Transkript-Messung ausdruecklich, aber
# KEIN Werkzeug des Kits konnte sie. Also schrieb sich jeder Architekt das
# Skript neu, oder er nahm die Churn-Zahl und buchte sie als gemessen.
#
# DIE DREI FALLEN, ALLE DREI IM FELD GETRETEN
#
#   (1) Ueber die NACHRICHTEN-ID deduplizieren. Eine Antwort erzeugt mehrere
#       Transkriptzeilen mit DERSELBEN usage-Angabe. Wer Zeilen zaehlt,
#       ueberschaetzt grob — im Feld 172 rohe Saetze, nach Dedup 76.
#   (2) Cache-Write nach LAUFZEIT trennen. 1h kostet das 2,0-Fache des Inputs,
#       5m nur das 1,25-Fache. Das Transkript gibt beide getrennt her.
#   (3) Den Basispreis am MODELL festmachen und sagen, wenn die ID unbekannt
#       ist. Eine stille Annahme ist hier teurer als eine Luecke.
PREIS_VIELFACHE = {
    # Nur der BASISPREIS haengt am Modell; diese vier Verhaeltnisse gelten
    # modelluebergreifend. Gegengeprueft an der Preistabelle des Anbieters
    # (Opus 5: 5 USD Input / 25 USD Output je Mio Token) UND an acht
    # headless-Laeufen des Kits, deren abgerechnete total_cost_usd sich damit
    # reproduzieren liessen.
    "output":         5.00,
    "cache_write_1h": 2.00,
    "cache_write_5m": 1.25,
    "cache_read":     0.10,
}

# USD je 1 Mio INPUT-Token, nach Modell-ID. Laengster Praefix gewinnt, damit
# datierte Varianten (claude-opus-5-20260101) und Plattform-Praefixe
# (anthropic.claude-opus-5 auf Bedrock) mitlaufen, ohne die Tabelle zu
# verdoppeln.
PREIS_INPUT_USD_PRO_MTOK = {
    "claude-fable-5":   10.00,
    "claude-mythos-5":  10.00,
    "claude-opus-5":     5.00,
    "claude-opus-4-8":   5.00,
    "claude-opus-4-7":   5.00,
    "claude-opus-4-6":   5.00,
    "claude-opus-4-5":   5.00,
    # BL-166: stand bis 2026-08-26 auf 3.00 — dem Satz der Vorgaenger-
    # Generation. Weil `sonnet` der Default aller Loop-Rollen ist
    # (TEAM_MODEL_LOOP), betraf der falsche Satz die MEHRHEIT aller gemessenen
    # Token jeder Installation: Im meldenden Projekt schlug die Selbsteichung
    # in 9 von 9 abgerechneten Laeufen fehl, 25–33 % daneben, und das Werkzeug
    # verweigerte regelkonform jede Buchung. Kein stiller Fehler — die Eichung
    # tat genau, was sie soll; der Schaden war die Blockade.
    "claude-sonnet-5":   2.00,
    "claude-sonnet-4-6": 3.00,
    "claude-sonnet-4-5": 3.00,
    "claude-haiku-4-5":  1.00,
}


def modell_basispreis(modell_id):
    """Basispreis je Mio Input-Token, oder None bei unbekannter ID.

    None ist ein Ergebnis, kein Fehler: Der Aufrufer weist die unbekannte ID
    aus, statt einen Preis zu raten. Eine geratene Zahl waere hier genau der
    Fehler, den BL-141 abtraegt — sie sieht aus wie eine Messung.
    """
    if not modell_id:
        return None
    kern = str(modell_id).split(".")[-1]        # Bedrock: anthropic.claude-...
    treffer = [n for n in PREIS_INPUT_USD_PRO_MTOK if kern.startswith(n)]
    if not treffer:
        return None
    return PREIS_INPUT_USD_PRO_MTOK[max(treffer, key=len)]


def _tokenkuebel():
    return {"input": 0, "output": 0, "cache_read": 0,
            "cache_write_5m": 0, "cache_write_1h": 0}


def _usage_addieren(kuebel, usage):
    kuebel["input"] += usage.get("input_tokens", 0) or 0
    kuebel["output"] += usage.get("output_tokens", 0) or 0
    kuebel["cache_read"] += usage.get("cache_read_input_tokens", 0) or 0
    erstellung = usage.get("cache_creation") or {}
    if erstellung:
        kuebel["cache_write_5m"] += erstellung.get("ephemeral_5m_input_tokens", 0) or 0
        kuebel["cache_write_1h"] += erstellung.get("ephemeral_1h_input_tokens", 0) or 0
    else:
        # Aeltere Transkripte tragen nur die Summe. Konservativ als 5m buchen:
        # Das ist der GUENSTIGERE Satz, die Zahl faellt also eher zu niedrig
        # aus als zu hoch — und eine zu niedrige gebuchte Zahl faellt beim
        # Abgleich auf, eine zu hohe wird geglaubt.
        kuebel["cache_write_5m"] += usage.get("cache_creation_input_tokens", 0) or 0


def _modelusage_kuebel(u, cache_art):
    """Token-Kuebel aus einem `modelUsage`-Eintrag eines headless-Logs.

    BL-152. Bewusst NICHT `_usage_addieren`: Die beiden Strukturen sehen sich
    aehnlich und kommen aus verschiedenen Quellen.

        Transkript  `usage`       snake_case, Cache-Erstellung nach Laufzeit
                                  aufgeschluesselt (`cache_creation`)
        headless    `modelUsage`  camelCase, Cache-Erstellung als EINE Summe

    Zusammengelegt sah das nach Sparsamkeit aus und war ein stiller
    Leserfehler: Jeder Schluessel ging ins Leere, jeder Kuebel blieb 0, und
    die Eichung konnte nie bestehen. Zwei Leser fuer zwei Formate sind hier
    billiger als eine Funktion, die beide zu kennen behauptet.

    `cache_art` sagt, als welche Laufzeit die Cache-Erstellung gebucht wird —
    die Angabe fehlt in dieser Struktur, siehe die Begruendung in
    `preise_nachrechnen`.
    """
    kuebel = _tokenkuebel()
    kuebel["input"] = u.get("inputTokens", 0) or 0
    kuebel["output"] = u.get("outputTokens", 0) or 0
    kuebel["cache_read"] = u.get("cacheReadInputTokens", 0) or 0
    kuebel[cache_art] = u.get("cacheCreationInputTokens", 0) or 0
    return kuebel


def sitzung_messen(pfade):
    """Liest Transkripte und gibt (je_modell, antworten, doppelt) zurueck.

    je_modell bildet die Modell-ID auf einen Token-Kuebel ab. Getrennt gehalten,
    weil eine Sitzung das Modell wechseln kann und der Basispreis daran haengt —
    ein gemeinsamer Kuebel waere mit dem ersten Wechsel falsch.
    """
    gesehen = set()
    je_modell = {}
    antworten = doppelt = 0
    for pfad in pfade:
        with open(pfad, encoding="utf-8") as f:
            for zeile in f:
                try:
                    d = json.loads(zeile)
                except ValueError:
                    continue                     # halbe Zeile am Dateiende
                nachricht = d.get("message")
                if not isinstance(nachricht, dict):
                    continue
                usage = nachricht.get("usage")
                if not usage:
                    continue
                # Falle (1): ueber die Nachrichten-ID, nicht ueber die Zeile.
                kennung = (nachricht.get("id") or d.get("requestId")
                           or d.get("uuid"))
                if kennung in gesehen:
                    doppelt += 1
                    continue
                gesehen.add(kennung)
                antworten += 1
                modell = nachricht.get("model") or "unbekannt"
                _usage_addieren(je_modell.setdefault(modell, _tokenkuebel()),
                                usage)
    return je_modell, antworten, doppelt


def kosten_aus_tokens(kuebel, basispreis):
    """USD fuer einen Token-Kuebel bei gegebenem Basispreis je Mio Input."""
    gesamt = kuebel["input"] / 1_000_000 * basispreis
    for art, faktor in PREIS_VIELFACHE.items():
        gesamt += kuebel[art] / 1_000_000 * basispreis * faktor
    return gesamt


def sitzung_kosten(je_modell):
    """(gesamt_usd, zeilen, unbekannte_modelle).

    Unbekannte Modelle gehen NICHT in die Summe ein und werden namentlich
    zurueckgegeben. Der Aufrufer muss sie nennen; eine Summe, die stillschweigend
    Teile auslaesst, ist schlimmer als gar keine.
    """
    gesamt = 0.0
    zeilen = []
    unbekannt = []
    for modell, kuebel in sorted(je_modell.items()):
        preis = modell_basispreis(modell)
        if preis is None:
            unbekannt.append(modell)
            continue
        usd = kosten_aus_tokens(kuebel, preis)
        gesamt += usd
        zeilen.append((modell, preis, kuebel, usd))
    return gesamt, zeilen, unbekannt


def _slug_locker(name):
    """Vergleichsform eines Ordnernamens: klein, jede Nicht-Alphanumerik zu "-".

    BL-186: Die Kodierung der CLI ist an den Raendern nicht exakt vorhersagbar.
    Auf DIESER Maschine liegen nebeneinander `C--Users-…-team-kit` und
    `c--Users-…-duke-itam-2026` — derselbe Wirt, dasselbe Laufwerk, einmal
    gross und einmal klein geschrieben. Der Grund ist der Aufrufer: Der
    Laufwerksbuchstabe kommt aus dem Arbeitsverzeichnis des Prozesses, und
    das schreibt nicht jeder Starter gleich. Ein Werkzeug, das den Ordnernamen
    ZEICHENGENAU nachbaut, ist damit vom Zufall abhaengig.
    """
    return re.sub(r"[^a-z0-9]+", "-", name.lower())


def projekt_ordnername(voll):
    """Der Ordnername, den die Agenten-CLI aus einem ABSOLUTEN Pfad bildet.

    Eigene Funktion, weil sie sich auf JEDEM Wirt pruefen laesst: Ein Test darf
    die Windows-Form nicht erst herstellen muessen, um sie zu befragen —
    genau daran ist der Fund drei Monate lang vorbeigelaufen. Der DOPPELPUNKT
    des Laufwerks ist der Punkt: Er ist unter Windows Teil jedes absoluten
    Pfades, blieb aber stehen, und damit zeigte der Name garantiert ins Leere.

    BL-191 (Nachtrag zu BL-186): Hier stand `voll.replace(os.sep, "-")` —
    und `os.sep` ist der Trenner des WIRTS, nicht der des uebergebenen Pfades.
    Der Fix zu BL-186 entstand auf einer Windows-Maschine, dort ist `os.sep`
    der Backslash und die elf Faelle waren gruen. Auf jedem POSIX-Wirt blieb
    der Backslash eines Windows-Pfades stehen, und drei der Faelle fielen —
    ausgerechnet die drei, die diese Funktion als „auf JEDEM Wirt pruefbar"
    ausweisen. Genau die Gattung BL-145, die BL-186 schliessen wollte, hat den
    Fix seiner eigenen Pruefung erwischt. Beide Trenner stehen deshalb
    woertlich da: Diese Funktion bildet einen FREMDEN Namen nach, sie darf den
    eigenen Wirt gar nicht befragen.
    """
    return (voll.replace("\\", "-").replace("/", "-")
                .replace(":", "-").replace("_", "-"))


def transkripte_aus_projekt(projektpfad):
    """ALLE CLI-Transkripte zu einem Projektpfad, das juengste zuerst.

    Die Agenten-CLI legt Transkripte unter ~/.claude/projects/<slug>/<id>.jsonl
    ab, wobei <slug> der Projektpfad mit Bindestrichen statt Trennzeichen ist.
    Die Kodierung ist VERLUSTBEHAFTET: Sowohl "/" als auch "_" werden zu "-",
    zwei verschiedene Projekte koennen also denselben Ordner ergeben. Das ist
    nicht zu reparieren (die Umkehrung ist mehrdeutig) — deshalb gibt diese
    Funktion die Pfade zurueck, die sie gelesen hat, und der Aufrufer DRUCKT
    sie. Wer die Zahl bucht, sieht dann, woher sie stammt.

    BL-186: Unter Windows fand diese Funktion NIE ein Transkript, und zwar
    lautlos — leeres Ergebnis, Exit 0, kein Fehler. `voll.replace(os.sep, "-")`
    ersetzt den Trenner `\\`, laesst aber den DOPPELPUNKT des Laufwerks stehen:
    Gesucht wurde `C:-Users-…`, der Ordner heisst `C--Users-…`. Das traf den
    einzigen Befehl, den das Architekten-Briefing fuer die Frage „woher kommt
    <USD>?" nennt — wer der Meldung „kein Transkript gefunden" glaubt,
    schliesst daraus, es gebe nichts zu buchen, und die Architektenkosten
    bleiben strukturell unerfasst.

    Gesucht wird deshalb in zwei Stufen: erst der zeichengenaue Name (schnell,
    auf POSIX unveraendert), dann ein Vergleich ueber `_slug_locker` gegen die
    vorhandenen Ordner. Die zweite Stufe ist der Riegel gegen die naechste
    Abweichung in der Kodierung — sie kostet ein `listdir` und nur dann, wenn
    die erste nichts gefunden hat.
    """
    wurzel = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    voll = os.path.abspath(os.path.expanduser(projektpfad))
    name = projekt_ordnername(voll)
    ordner = os.path.join(wurzel, name)
    if not os.path.isdir(ordner):
        ordner = None
        if os.path.isdir(wurzel):
            gesucht = _slug_locker(name)
            for d in sorted(os.listdir(wurzel)):
                if (os.path.isdir(os.path.join(wurzel, d))
                        and _slug_locker(d) == gesucht):
                    ordner = os.path.join(wurzel, d)
                    break
    if not ordner:
        return []
    dateien = [os.path.join(ordner, d) for d in os.listdir(ordner)
               if d.endswith(".jsonl")]
    # BL-186, zweiter Teil: Frueher stand hier `max(…, key=getmtime)` — EIN
    # Transkript, waehrend Docstring und Nutzungszeile im Plural sprachen.
    # Erstreckt sich eine Kaskade ueber mehrere Sitzungen (der Normalfall,
    # sobald Planung und Closeout getrennt laufen), mass der Aufruf
    # stillschweigend nur die letzte. Die Auswahl trifft jetzt der AUFRUFER,
    # und er sagt, was er weggelassen hat.
    return sorted(dateien, key=os.path.getmtime, reverse=True)


def preise_nachrechnen(logs):
    """Rechnet die headless-Logs mit DEMSELBEN Code nach und vergleicht.

    Das ist die Gegenprobe, die die Messung erst gueltig macht. Die Logs des
    Kits (.ralph-logs/*.json, .team-logs/*.json) tragen BEIDES: dieselbe
    usage-Struktur wie das Transkript UND den abgerechneten `total_cost_usd`,
    je Modell aufgeschluesselt in `modelUsage`. Das sind fertige Eichpunkte —
    ohne sie waere die Preistabelle eine Behauptung.

    Weicht die Rechnung ab, ist die Tabelle veraltet, und das WERKZEUG SAGT DAS,
    statt eine falsche Zahl zu buchen. Genau diese Richtung ist der Punkt: Der
    teure Fehler ist nicht die falsche Zahl, sondern die falsche Zahl, die wie
    eine Messung aussieht.

    Rueckgabe: Liste von (pfad, gemeldet_usd, gerechnet_usd, abweichung_relativ)
    — nur fuer Logs, die BEIDE Angaben tragen. Ein Log ohne modelUsage ist
    kein Befund, sondern nur kein Eichpunkt.
    """
    befunde = []
    for pfad in logs:
        try:
            with open(pfad, encoding="utf-8") as f:
                d = json.load(f)
        except (ValueError, OSError):
            continue
        gemeldet = d.get("total_cost_usd")
        nutzung = d.get("modelUsage")
        if gemeldet is None or not isinstance(nutzung, dict) or not nutzung:
            continue
        # BL-152: Die beiden Kuebel-Formate haben VERSCHIEDENE HERKUNFT und
        # duerfen nicht in eine Funktion gezwaengt werden. `_usage_addieren`
        # liest die `usage`-Struktur des TRANSKRIPTS (snake_case); hier steht
        # `modelUsage` aus dem headless-Log, und das traegt camelCase. Der
        # Leser fragte bis hierher nach `input_tokens`, wo `inputTokens`
        # stand — jeder Kuebel blieb auf 0, `gerechnet` wurde 0.0000, und die
        # Abweichung war IMMER exakt 100 %, unabhaengig davon, ob die Tabelle
        # stimmte. Die Warnung zeigte also genau dorthin, wo der Fehler nicht
        # war, und riet von einer Buchung ab, die in Ordnung gewesen waere.
        #
        # Nachgemessen an 920 abgerechneten Laeufen aus vier Feldprojekten:
        # mit den richtigen Schluesseln reproduzieren ALLE 920 den
        # abgerechneten Betrag auf ein Promille; mit den alten war es keiner.
        nenner = gemeldet if gemeldet else 1.0
        abweichungen = []
        for art in ("cache_write_1h", "cache_write_5m"):
            gerechnet = 0.0
            vollstaendig = True
            for modell, u in nutzung.items():
                preis = modell_basispreis(modell)
                if preis is None:
                    vollstaendig = False
                    break
                gerechnet += kosten_aus_tokens(_modelusage_kuebel(u, art), preis)
            if not vollstaendig:
                break
            abweichungen.append((abs(gerechnet - gemeldet) / nenner, gerechnet))
        if not vollstaendig:
            continue
        # Die KLEINERE der beiden Abweichungen zaehlt — und das ist keine
        # Nachsicht, sondern die Beseitigung einer Unbekannten, die diese
        # Funktion gar nicht beobachten kann.
        #
        # `modelUsage` traegt die Cache-Erstellung als EINE Summe, ohne die
        # 5m/1h-Aufteilung, die das Transkript hergibt. Die beiden Saetze
        # unterscheiden sich (Faktor 2,00 gegen 1,25), also braucht es eine
        # Annahme. Gemessen an denselben 920 Laeufen zerfaellt das sauber in
        # zwei Gruppen:
        #
        #     808 Abo-Laeufe          1h trifft, 5m nicht
        #     112 API-Fallback-Laeufe 110 mal 5m, 2 mal 1h
        #
        # Eine FESTE Annahme ist damit fuer eine der beiden Gruppen immer
        # falsch: "immer 1h" haette 110 von 920 Laeufen als "Preistabelle
        # veraltet" gemeldet — ein leiserer Fehlalarm als vorher, aber
        # derselbe Fehler. Ein Waechter mit Fehlalarmen wird abgeschaltet
        # (Bauart BL-14).
        #
        # Die Erkennung an der Laufart festzumachen (der Dateiname traegt
        # "-api-fallback") waere die naheliegende Alternative und ist
        # nachweislich schlechter: 2 der 112 Fallback-Laeufe rechnen mit 1h ab.
        #
        # Der Waechter bleibt dadurch scharf, ebenfalls gemessen: Eine um 5 %
        # verstellte Preistabelle wird bei 920 von 920 Laeufen erkannt, eine um
        # 20 % verstellte bei 907. Die Annahme betrifft nur EINEN Kuebel; der
        # Basispreis, um den es bei einer Preisaenderung geht, steckt in allen.
        rel, gerechnet = min(abweichungen)
        befunde.append((pfad, gemeldet, gerechnet, rel))
    return befunde


def preis_diagnose(logs):
    """WELCHER Basispreis liegt wie weit daneben? — aus EINMODELL-Laeufen.

    BL-166, der wichtigere Teil. Die Eichung wusste bereits, dass etwas nicht
    stimmt, und verweigerte regelkonform die Buchung. Sie sagte aber nicht,
    WAS nicht stimmt — und liess den Betreiber damit vor einer Tabelle stehen,
    die er von Hand gegen die Preisseite des Anbieters abgleichen musste, ohne
    zu wissen, welche Zeile. Ein Werkzeug, das einen Fehler erkennt und ihn
    nicht benennen kann, verschiebt die Arbeit nur.

    DIE RECHNUNG IST EXAKT, NICHT GESCHAETZT: Die Gesamtkosten sind in `preis`
    LINEAR (jeder Kuebel wird mit `preis * faktor` multipliziert). Der
    implizite Satz ist also `gemeldet / kosten_aus_tokens(kuebel, 1.0)` — die
    Rechnung mit Basispreis 1.0 liefert genau die Summe der Faktoren.

    NUR EINMODELL-LAEUFE: Trägt ein Log zwei Modelle, ist die Aufteilung des
    abgerechneten Betrags auf die beiden Saetze unterbestimmt — jede Zuweisung
    waere geraten. Eine geratene Zahl ist hier genau der Fehler, den BL-141
    abtraegt: Sie sieht aus wie eine Messung.

    Rueckgabe: {modell: (implizit_min, implizit_max, tabelle, anzahl)}. Zwei
    Werte, weil `modelUsage` die Cache-Erstellung als EINE Summe fuehrt und
    die 5m/1h-Annahme offenbleibt (siehe `preise_nachrechnen`) — die Spanne
    sagt ehrlich, wie genau die Aussage ist.
    """
    je_modell = {}
    for pfad in logs:
        try:
            with open(pfad, encoding="utf-8") as f:
                d = json.load(f)
        except (ValueError, OSError):
            continue
        gemeldet = d.get("total_cost_usd")
        nutzung = d.get("modelUsage")
        if not gemeldet or not isinstance(nutzung, dict) or len(nutzung) != 1:
            continue
        modell, u = next(iter(nutzung.items()))
        saetze = []
        for art in ("cache_write_1h", "cache_write_5m"):
            einheiten = kosten_aus_tokens(_modelusage_kuebel(u, art), 1.0)
            if einheiten > 0:
                saetze.append(gemeldet / einheiten)
        if saetze:
            je_modell.setdefault(modell, []).extend(saetze)

    ergebnis = {}
    for modell, saetze in je_modell.items():
        ergebnis[modell] = (min(saetze), max(saetze),
                            modell_basispreis(modell), len(saetze) // 2)
    return ergebnis


# Wieviel Abweichung noch Rundung ist. Die acht Feld-Laeufe reproduzierten auf
# 4e-16 genau; ein Promille ist dagegen sehr grosszuegig und trifft trotzdem
# jede echte Preisaenderung, weil die in Sprüngen von 20 % und mehr kommt.
PREIS_TOLERANZ = 0.001


def logs_einsammeln(repo="."):
    """Alle headless-Logs des Projekts, archivierte eingeschlossen."""
    treffer = []
    for ordner in (".ralph-logs", ".team-logs"):
        wurzel = os.path.join(repo, ordner)
        if not os.path.isdir(wurzel):
            continue
        for pfad, _, dateien in os.walk(wurzel):
            treffer.extend(os.path.join(pfad, d) for d in sorted(dateien)
                           if d.endswith(".json"))
    return sorted(treffer)


def kaskade_aus_plan(repo="."):
    """Leitet die Kaskaden-Nummer aus der Zeiger-Datei .ralph-plan ab (Muster
    "ralph-kaskade-<N>-..." im Dateinamen). None, wenn die Datei fehlt oder
    das Muster nicht passt — der Aufrufer verlangt dann ein explizites
    --kaskade."""
    pfad = os.path.join(repo, ".ralph-plan")
    if not os.path.isfile(pfad):
        return None
    inhalt = open(pfad, encoding="utf-8").read().strip()
    treffer = re.search(r"ralph-kaskade-(\d+)-", inhalt)
    return treffer.group(1) if treffer else None


# Wartefrist der Ledger-Sperre auf der Windows-Bahn (BL-125). POSIX `flock`
# wartet von sich aus unbegrenzt; die Windows-Bytebereichssperre kennt kein
# blockierendes Warten mit offenem Ende, das sich unterbrechen liesse
# (msvcrt.LK_LOCK wartet stur 10 Sekunden und wirft dann), also wird hier
# selbst gepollt. 30 Sekunden sind grosszuegig gegen den echten kritischen
# Bereich — Lesen, Zeile ersetzen, Temp-Datei schreiben, os.replace, also
# Millisekunden — und kurz genug, dass ein haengengebliebener Prozess einen
# Lauf nicht unbemerkt stillstehen laesst.
_LEDGER_LOCK_FRIST_S = 30.0
_LEDGER_LOCK_TAKT_S = 0.02


def _lock_belegen(fd, lock_pfad):
    """Belegt die Sperre exklusiv — POSIX per `flock`, Windows per
    Bytebereichssperre auf Byte 0 derselben Lock-Datei. Beide Wege sperren
    handle-bezogen, also auch zwischen zwei Threads DESSELBEN Prozesses
    (der Fall, den test_hm48_ledger_lock_race.py stellt).

    Fehlt beides, wird NICHT ungesichert weitergeschrieben: Der Aufrufer
    bekommt einen Fehler an der Stelle, an der die Zusicherung endet."""
    if fcntl is not None:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return
    if msvcrt is not None:
        frist = time.monotonic() + _LEDGER_LOCK_FRIST_S
        while True:
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                if time.monotonic() >= frist:
                    raise OSError(
                        f"Ledger-Sperre '{lock_pfad}' war "
                        f"{int(_LEDGER_LOCK_FRIST_S)} Sekunden lang von einem "
                        "anderen Prozess gehalten — es wurde NICHTS "
                        "geschrieben. Laeuft noch ein zweiter "
                        "Abschluss-Aufruf? Wenn nicht, ist die Lock-Datei "
                        "verwaist und kann von Hand entfernt werden.")
                time.sleep(_LEDGER_LOCK_TAKT_S)
    raise OSError(
        "Kein Sperrmechanismus verfuegbar (weder fcntl noch msvcrt). Der "
        "Ledger wird bewusst NICHT ohne Sperre geschrieben: Zwei "
        "ueberlappende Abschluss-Aufrufe koennten sich sonst gegenseitig "
        "eine gerade geschriebene Zeile herausreissen (HM-48).")


def _lock_freigeben(fd):
    """Gegenstueck zu _lock_belegen(). Auf beiden Bahnen faellt die Sperre
    zwar auch mit dem os.close() weg; sie wird trotzdem ausdruecklich
    freigegeben, damit die Freigabe an einer greppbaren Stelle steht."""
    if fcntl is not None:
        fcntl.flock(fd, fcntl.LOCK_UN)
    elif msvcrt is not None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)


@contextlib.contextmanager
def _ledger_lock(pfad):
    """Interprozess-Sperre um den Lesen+Schreiben-Kritikbereich von
    _ledger_zeile_setzen() (HM-48): eine exklusive Sperre auf eine feste
    Lock-Datei neben dem Ledger, gehalten fuer die volle
    Read-Modify-Write-Spanne. Serialisiert konkurrierende kosten.py-Prozesse
    (egal ob direkt oder ueber team-status.sh/team/lib.sh aufgerufen)
    unabhaengig vom Aufrufer, statt sich auf eine Sperre der Shell-Seite
    (team_lock()) zu verlassen, die ohnehin nicht fuer alle drei
    Abschluss-Kommandos genutzt wurde.

    WELCHER Mechanismus das ist, entscheidet _lock_belegen() zur Laufzeit
    (BL-125) — die Zusicherung ist auf beiden Bahnen dieselbe."""
    lock_pfad = pfad + ".lock"
    fd = os.open(lock_pfad, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        _lock_belegen(fd, lock_pfad)
    except BaseException:
        # Nicht belegt heisst: nicht freigeben. Ein LOCK_UN/LK_UNLCK auf
        # eine nie gehaltene Sperre ist auf der Windows-Bahn selbst ein
        # Fehler und wuerde die eigentliche Ursache verdecken.
        os.close(fd)
        raise
    try:
        yield
    finally:
        _lock_freigeben(fd)
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
            with open(pfad, encoding="utf-8") as fh:
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
            # BL-129: newline="" UND encoding. Ohne newline="" uebersetzt der
            # Textmodus jedes "\n" in os.linesep — unter Windows also in
            # "\r\n". Damit bekaeme JEDE Zeile des Ledgers ein CR-Byte, die
            # Kopfzeile eingeschlossen, und zwar bei jedem Schreibzugriff neu.
            # Genau dieses Byte ist der Schaden, gegen den HM-36/HM-37/HM-38
            # die Feldwerte sanitisieren: Beim naechsten Einlesen unter
            # universal newlines wird es als Zeilenumbruch gelesen und
            # zerlegt die Zeile. Die Sanitisierung deckt den Fall nicht ab,
            # weil das CR dort nicht aus einem Feldwert kommt, sondern aus der
            # Plattform — sie greift eine Schicht zu frueh.
            # Ohne encoding gilt die Locale-Kodierung des Wirts; auf einem
            # deutschen Windows ist das cp1252, und ein Umlaut in einer Notiz
            # macht aus dem Ledger entweder Mojibake oder einen
            # UnicodeDecodeError beim naechsten Lesen (Bauart BL-125).
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
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


def _alt_usd_lesen(felder, rolle, kaskade):
    """USD-Feld einer bestehenden Ledger-Zeile. Gemeinsamer Helfer fuer
    akteur_abschluss() und rollen_abschluss() (BL-25): Beide muessen den
    Altwert kennen, bevor sie ihn ueberschreiben duerfen, und beide duerfen
    bei einem unlesbaren Feld NICHTS schreiben. Nur Feld 2 wird gelesen — ein
    maschinengeschriebener Zahlwert. Der abo/api-Split der Altzeile wird
    BEWUSST NICHT aus der Notiz zurueckgeparst: Notizen werden real von Hand
    korrigiert (Feld-Kaskade 1), ein Parser darauf waere die naechste stille
    Fehlerquelle."""
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


def akteur_abschluss(usd, domaene, kaskade, rolle, auth, notiz="",
                      pfad=".budget-ledger", bestand="abbrechen"):
    """A1-Ersetzung, rollen-agnostisch (BL-33, Stufe 50): haengt eine echte
    Ledger-Zeile fuer <rolle>/<kaskade> an. Eine bestehende Zeile DERSELBEN
    Rolle DERSELBEN Kaskade (7-Feld-Schema) wird nach `bestand` behandelt;
    die Zeile einer ANDEREN Rolle derselben Kaskade bleibt immer unberuehrt
    (z. B. Frank- und Architekt-Zeile der gleichen Kaskade koexistieren).
    Wirft ValueError bei ungueltigen Eingaben, OHNE die Datei anzufassen.
    Gibt True zurueck, wenn eine vorhandene Zeile angefasst wurde, sonst
    False (neu angelegt).

    bestand (BL-25) — symmetrisch zu rollen_abschluss() (BL-5):

      "abbrechen" (Default)  ValueError, Datei unangetastet. Die Meldung
                             nennt Alt-, Neu- und Summenwert.
      "addieren"             Neuer Wert wird auf den Altwert ADDIERT.
      "ersetzen"             Altes Verhalten: Altwert wird ueberschrieben.

    WARUM der Default nicht mehr "ersetzen" ist: Ein Akteur, der ueber
    mehrere Sitzungen an einer Kaskade arbeitet (Aushaertung vormittags,
    Closeout abends), bucht zwangslaeufig zweimal — und der zweite Aufruf
    loeschte den ersten Wert wortlos. Im Feld sind so 5,5515 USD aus einem
    Ledger verschwunden (Feld A, Kaskade 9). Der Default bricht ab
    statt zu addieren, weil ein Wiederholungsaufruf mit denselben Zahlen
    (Vertipper, zweiter Anlauf) sonst verdoppeln wuerde — dieselbe
    Symmetrieueberlegung, die BL-5 fuer rollen_abschluss angestellt hat.

    Anders als dort ist hier "ersetzen" der Korrektur-, nicht der
    Normalfall: Der uebergebene Wert ist ein extern GEMESSENER Absolutwert
    (Transkript, Konsolenausgabe), kein aus Restlogs gezaehlter Zuwachs."""
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

    if bestand not in ("abbrechen", "addieren", "ersetzen"):
        raise ValueError(
            f"bestand muss 'abbrechen', 'addieren' oder 'ersetzen' sein, "
            f"nicht '{bestand}'")
    if bestand == "ersetzen":
        return _ledger_zeile_setzen(zeile_neu, match_fn, pfad)

    def merge_fn(felder):
        alt = _alt_usd_lesen(felder, rolle, kaskade)
        if bestand == "abbrechen":
            raise ValueError(
                f"Fuer Kaskade {kaskade} steht bereits eine {rolle}-Zeile ueber "
                f"{alt:.4f} USD. Dieser Aufruf wuerde sie durch {usd:.4f} USD "
                f"ERSETZEN und die Differenz verlieren. Es wird NICHTS "
                f"geschrieben.\n"
                f"  Folgesitzung (dieselbe Rolle arbeitete erneut an dieser "
                f"Kaskade): --addieren  -> {alt + usd:.4f} USD\n"
                f"  Korrektur (die Altzeile war eine Fehlmessung):            "
                f"  --ersetzen  -> {usd:.4f} USD")
        summe = alt + usd
        alt_auth = felder[3] if len(felder) > 3 else ""
        auth_summe = auth if alt_auth == auth else "abo/api"
        notiz_summe = (f"{notiz_sauber} (addiert auf Bestand {alt:.4f} USD, "
                       f"auth {alt_auth or '—'})") if notiz_sauber else \
            (f"addiert auf Bestand {alt:.4f} USD, auth {alt_auth or '—'}")
        return (f"{date.today().isoformat()} | {kaskade} | {summe:.4f} | "
                f"{auth_summe} | {domaene} | {rolle} | {notiz_summe}\n")

    return _ledger_zeile_setzen(zeile_neu, match_fn, pfad, merge_fn=merge_fn)


def architekt_abschluss(usd, domaene, kaskade, notiz="", pfad=".budget-ledger",
                         bestand="abbrechen"):
    """Duenner, rueckwaertskompatibler Alias auf akteur_abschluss() mit
    rolle=architekt/auth=api. `bestand` wird durchgereicht (BL-25) — der
    Architekt ist die Rolle, die am haeufigsten zweimal an derselben Kaskade
    bucht."""
    return akteur_abschluss(usd, domaene, kaskade, rolle="architekt",
                             auth="api", notiz=notiz, pfad=pfad,
                             bestand=bestand)


def rollen_abschluss(kaskade, abo, api, domaene="team", notiz="",
                      pfad=".budget-ledger", bestand="abbrechen",
                      rolle="roles"):
    """Kaskadenscharfe Rollenkosten (BL-17-Restpunkt/BL-29-"1b", Kaskade
    16/Stufe 54): haengt EINE rolle=roles-Ledger-Zeile fuer die
    .team-logs-Kosten (Harry/Marv/Frank/Axel) EINER Kaskade an. usd = abo +
    api; auth = "abo" (api==0), "api" (abo==0), sonst "abo/api" —
    Stakeholder-Entscheid: Kaskadenschaerfe schlaegt Abo/API-Schaerfe je
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
    # Stakeholder-Entscheid 2026-08-02: der Vorspann entsteht HIER, aus der
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

    def merge_fn(felder):
        alt = _alt_usd_lesen(felder, rolle, kaskade)
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

    if befehl == "turns":
        # BL-37 (c): Turn-Profil des Laufs — die Diagnose, ob der Stufenschnitt
        # stimmte. Viele kurze Turns = Nacharbeit, wenige lange = Urteilsarbeit.
        dirs = [a for a in rest if not a.startswith("--")] or [".ralph-logs"]
        anzahl, gesamt, zeilen = turn_profil(dirs)
        if not anzahl:
            print("Keine Logs mit num_turns gefunden.")
            return 0
        print(f"{anzahl} Lauf/Laeufe, {gesamt} Turns "
              f"(Schnitt {gesamt / anzahl:.1f}).")
        for datei, turns, usd in zeilen:
            betrag = f"{usd:.4f} USD" if usd is not None else "Kosten unbekannt"
            print(f"  {turns:4d} Turns  {betrag:>18}  {os.path.basename(datei)}")
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
                                  aktuelle_kaskade=kaskade, repo=repo)
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

    if befehl == "sitzung-messen":
        # BL-141: der Weg, den das Architekten-Briefing verlangt und den bis
        # hierher kein Werkzeug des Kits gehen konnte.
        pfade = []
        projekt = None
        alle = False
        i = 0
        while i < len(rest):
            if rest[i] == "--projekt":
                if i + 1 >= len(rest):
                    print("Fehler: --projekt braucht einen Pfad", file=sys.stderr)
                    return 1
                projekt = rest[i + 1]
                i += 2
            elif rest[i] == "--alle":
                alle = True
                i += 1
            else:
                pfade.append(rest[i])
                i += 1
        if projekt:
            gefunden = transkripte_aus_projekt(projekt)
            if not gefunden:
                print(f"Fehler: kein Transkript zu {projekt} gefunden",
                      file=sys.stderr)
                return 1
            # BL-186: `sitzung-messen` misst EINE Sitzung — das bleibt der
            # Default. Neu ist, dass der Rest nicht mehr verschwiegen wird:
            # Eine Kaskade laeuft regelmaessig ueber mehrere Sitzungen, und
            # wer das nicht weiss, bucht zu wenig und merkt es nie.
            if alle:
                pfade = gefunden
            else:
                pfade = gefunden[:1]
                if len(gefunden) > 1:
                    print(f"  ! {len(gefunden)} Transkripte zu diesem Projekt, "
                          f"gemessen wird das ZULETZT geaenderte. Erstreckt "
                          f"sich die Kaskade ueber mehrere Sitzungen, fehlen "
                          f"{len(gefunden) - 1} davon — dann --alle nehmen "
                          f"oder die Transkripte einzeln benennen.",
                          file=sys.stderr)
        if not pfade:
            print("Nutzung: kosten.py sitzung-messen "
                  "(--projekt PFAD [--alle] | TRANSKRIPT...)",
                  file=sys.stderr)
            return 1

        # ZUERST die Gegenprobe, dann die Zahl. Andersherum liest der Mensch
        # die Summe und ueberblaettert die Warnung darunter.
        befunde = preise_nachrechnen(logs_einsammeln("."))
        schief = [b for b in befunde if b[3] > PREIS_TOLERANZ]
        if befunde:
            if schief:
                print(f"  ! Preistabelle stimmt nicht mehr: {len(schief)} von "
                      f"{len(befunde)} nachgerechneten Laeufen weichen ab.",
                      file=sys.stderr)
                for pfad, gemeldet, gerechnet, rel in schief[:3]:
                    print(f"      {os.path.basename(pfad)}: abgerechnet "
                          f"{gemeldet:.4f}, gerechnet {gerechnet:.4f} "
                          f"({rel * 100:.1f} % daneben)", file=sys.stderr)
                # BL-166: sagen, WELCHER Satz danebenliegt. Ohne diese Zeilen
                # steht der Betreiber vor einer Tabelle mit elf Saetzen und
                # weiss nur, dass einer davon falsch ist.
                for modell, (lo, hi, tabelle, n) in sorted(
                        preis_diagnose(logs_einsammeln(".")).items()):
                    if tabelle is None:
                        continue
                    if lo <= tabelle <= hi:
                        continue            # dieser Satz traegt
                    naeher = lo if abs(lo - tabelle) < abs(hi - tabelle) else hi
                    weite = (naeher - tabelle) / tabelle * 100
                    spanne = (f"{lo:.2f}" if abs(hi - lo) < 0.005
                              else f"{lo:.2f}–{hi:.2f}")
                    belege = f"{n} Einmodell-Lauf" if n == 1 else \
                             f"{n} Einmodell-Laeufen"
                    print(f"      {modell}: Tabelle {tabelle:.2f}, "
                          f"abgerechnet entspricht {spanne} USD/Mio Input "
                          f"({weite:+.0f} %, aus {belege})", file=sys.stderr)
                print("    Die Zahl unten ist damit UNGEEICHT. Preistabelle in "
                      "kosten.py nachziehen, bevor du sie buchst.",
                      file=sys.stderr)
            else:
                print(f"  ✓ Preistabelle geeicht an {len(befunde)} "
                      f"abgerechneten Laeufen dieses Projekts")
        else:
            print("  ! Keine abgerechneten Laeufe zum Eichen gefunden — die "
                  "Zahl unten ruht allein auf der Preistabelle.",
                  file=sys.stderr)

        je_modell, antworten, doppelt = sitzung_messen(pfade)
        if not antworten:
            print("Fehler: keine Nutzungsdaten im Transkript", file=sys.stderr)
            return 1
        gesamt, zeilen, unbekannt = sitzung_kosten(je_modell)
        for pfad in pfade:
            print(f"  gelesen: {pfad}")
        print(f"  Antworten: {antworten}  (Duplikate verworfen: {doppelt})")
        for modell, preis, kuebel, usd in zeilen:
            print(f"    {modell}  ({preis:.2f} USD/Mio Input)")
            for art in ("input", "output", "cache_read",
                        "cache_write_5m", "cache_write_1h"):
                print(f"      {art:<15} {kuebel[art]:>12,} Tok")
            print(f"      {'= Summe':<15} {usd:>12.4f} USD")
        for modell in unbekannt:
            print(f"  ! Modell '{modell}' steht nicht in der Preistabelle — "
                  f"seine Token sind in der Summe NICHT enthalten.",
                  file=sys.stderr)
        print(f"  GESAMT: {gesamt:.4f} USD")
        print("  Im Abo ist das ein Abo-Gegenwert, kein abgerechneter Betrag.")
        print(f"  Buchen: team-status --akteur-abschluss architekt abo "
              f"{gesamt:.4f} <domaene> \"<notiz>\"")
        print("  Erst NACH dem letzten Schritt messen — mittendrin gemessen "
              "untertreibt der Wert systematisch.")
        return 2 if (schief or unbekannt) else 0

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
        # BL-143: Hier stand `"api" if befehl == "architekt-abschluss"`. Der
        # Alias buchte damit FEST die API-Achse — gegen die Regel, die seit der
        # Abo-Umstellung in CLAUDE.md und im Architekten-Briefing steht: "Auch
        # Axel und Der Architekt laufen Abo-first — KEINE Rolle ist mehr fest
        # api", und der Architektenwert sei "als Abo-Gegenwert zu buchen und NIE
        # stillschweigend als abgerechneter Betrag auszugeben".
        #
        # Im Feld (Feld B, Kaskade 1) landeten so 16,3990 USD in der
        # Zeile "real via API abgerechnet" des Kontostands — echtes Geld, das
        # nie geflossen ist. Gemerkt hat es niemand beim Buchen, sondern erst
        # beim Lesen der geschriebenen Ledger-Zeile: Die Erfolgsmeldung nannte
        # die Auth-Achse nicht (siehe unten, dieselbe BL-Nummer).
        #
        # Vorbelegung statt Festlegung: --auth bleibt ueberschreibbar, damit ein
        # Architekt, der TATSAECHLICH ueber einen API-Key gearbeitet hat, das
        # sagen kann. Der haeufige Fall ist die Vorgabe, der seltene der Schalter.
        auth = "abo" if befehl == "architekt-abschluss" else None
        notiz = ""
        pfad = ".budget-ledger"
        repo = "."
        bestand = "abbrechen"   # BL-25: nie stillschweigend ueberschreiben
        i = 0
        while i < len(rest):
            if rest[i] == "--addieren":
                bestand = "addieren"
                i += 1
            elif rest[i] == "--ersetzen":
                bestand = "ersetzen"
                i += 1
            elif rest[i] == "--usd":
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
            elif rest[i] == "--auth":   # BL-143: beide Befehle, nicht nur akteur
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
                                        notiz=notiz, pfad=ledger_pfad,
                                        bestand=bestand)
        except ValueError as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 1
        if not ersetzt:
            aktion = "angelegt"
        else:
            aktion = "addiert" if bestand == "addieren" else "ersetzt"
        # BL-143: Die Achse GEHOERT in die Meldung. Vorher las sich ein
        # Fehlgriff nicht — "Architekt-Zeile Kaskade 1 (produkt) angelegt:
        # 16.3990 USD" ist wahr und verschweigt genau das Feld, in dem der
        # Fehler sass. Die Roles-/Ralph-Zeilen nennen ihre Achse laengst
        # ("abo 4.5571 / api 0.0000"); ausgerechnet diese nicht.
        print(f"{rolle.capitalize()}-Zeile Kaskade {kaskade} ({domaene}) "
              f"{aktion}: {usd:.4f} USD ({auth})")
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
        # BL-45: Zeitraum-Abgleich VOR dem Buchen. Kein Abbruch — der Mensch
        # entscheidet, ob er trennt (`--kaskade` fuer einen eigenen
        # Out-of-Loop-Eintrag) oder die Notiz anpasst. Nur Sichtbarkeit, wo
        # bisher geschwiegen wurde; dieselbe Bauart wie die Startwarnung aus
        # BL-27. Deckt zugleich den zweiten Befund aus BL-27 ab: Logs aus
        # mehr als einem Lauf werden hier benannt, statt still der falschen
        # Kaskade zugeschlagen zu werden.
        _beginn, _zu_alt = logs_vor_kaskadenbeginn(files, kaskade, repo)
        if _zu_alt:
            from datetime import datetime as _dt
            print(f"Hinweis: {len(_zu_alt)} Log(s) sind AELTER als der Beginn "
                  f"der Kaskade {kaskade} "
                  f"({_dt.fromtimestamp(_beginn).isoformat(timespec='minutes')}) "
                  f"und werden trotzdem unter dieser Nummer gebucht:",
                  file=sys.stderr)
            for datei, mtime in _zu_alt[:5]:
                print(f"  {datei} ({_dt.fromtimestamp(mtime).isoformat(timespec='minutes')})",
                      file=sys.stderr)
            if len(_zu_alt) > 5:
                print(f"  … und {len(_zu_alt) - 5} weitere", file=sys.stderr)
            print("  Gehoeren sie zu einer Out-of-Loop-Runde zwischen zwei "
                  "Kaskaden, gehoeren sie unter eine eigene benannte Nummer "
                  "(`--kaskade vor-N`) — sonst traegt diese Kaskade fremde "
                  "Kosten (BL-45).", file=sys.stderr)

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

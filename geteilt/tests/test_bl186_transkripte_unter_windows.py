#!/usr/bin/env python3
"""BL-186: `kosten.py sitzung-messen --projekt` fand unter Windows NIE ein
Transkript — leeres Ergebnis, kein Fehler, Exit 0.

WARUM DAS TEUER IST UND NICHT NUR AERGERLICH
    `sitzung-messen --projekt` ist der EINZIGE Befehl, den das
    Architekten-Briefing fuer die Frage „woher kommt <USD>?" nennt. Wer der
    Meldung „kein Transkript gefunden" glaubt, schliesst daraus, es gebe
    nichts zu buchen — und die Architektenkosten bleiben strukturell
    unerfasst. Es ist die Waechter-ueber-leerem-Ergebnis-Bauform, vor der das
    Kit an anderer Stelle selbst warnt.

DIE URSACHE IST EIN ZEICHEN
    `transkripte_aus_projekt()` bildete den Ordnernamen mit
    `voll.replace(os.sep, "-").replace("_", "-")`. Das ersetzt unter Windows
    den Trenner `\\`, laesst aber den DOPPELPUNKT des Laufwerks stehen:

        gesucht:  C:-Users-adm-...-projekt
        vorhanden: C--Users-adm-...-projekt

    Auf einem POSIX-Wirt kann der Fehler nicht auftreten — dort hat kein
    absoluter Pfad einen Doppelpunkt. Wieder die Gattung BL-145: „gruen
    bedeutet auf den beiden Wirten verschieden viel".

UND EINE ZWEITE ABWEICHUNG, DIE ERST DAS FELD ZEIGT
    Auf der Maschine, auf der dieser Test entstanden ist, liegen nebeneinander

        C--Users-adm-mronzani-source-repos-team-kit
        c--Users-adm-mronzani-source-repos-duke-itam-2026

    — derselbe Wirt, dasselbe Laufwerk, einmal gross und einmal klein. Der
    Laufwerksbuchstabe kommt aus dem Arbeitsverzeichnis des aufrufenden
    Prozesses, und das schreibt nicht jeder Starter gleich. Ein zeichengenauer
    Nachbau ist damit vom Zufall abhaengig; deshalb sucht die Funktion in zwei
    Stufen — erst exakt, dann ueber eine lockere Vergleichsform.

DER ZWEITE, PLATTFORMUNABHAENGIGE TEIL
    Die Funktion lieferte per `max(…, key=getmtime)` nur das ZULETZT
    geaenderte Transkript, waehrend Docstring und Nutzungszeile im Plural
    sprachen. Erstreckt sich eine Kaskade ueber mehrere Sitzungen — der
    Normalfall, sobald Planung und Closeout getrennt laufen —, mass der Aufruf
    stillschweigend nur die letzte und untertrieb den Wert. Die Auswahl trifft
    jetzt der Aufrufer, und er SAGT, was er weggelassen hat.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import kit_pfad  # noqa: E402

WERKZEUG = kit_pfad("tools", "kosten.py")

pytestmark = pytest.mark.skipif(
    not WERKZEUG.is_file(), reason="kosten.py liegt in dieser Ablage nicht")

sys.path.insert(0, str(WERKZEUG.parent))


def _kosten():
    import importlib
    modul = importlib.import_module("kosten")
    return importlib.reload(modul)


# --- Der Ordnername, auf JEDEM Wirt pruefbar ---------------------------------


@pytest.mark.parametrize("voll,verboten", [
    (r"C:\Users\adm_mronzani\source\repos\projekt", ":"),
    (r"D:\arbeit\mein_projekt", ":"),
    ("/home/wernher/mein_projekt", ":"),
])
def test_der_ordnername_traegt_keinen_doppelpunkt(voll, verboten):
    """Der Fund in einem Zeichen — und er laeuft auch auf Linux.

    Genau das ist der Punkt: Der Fehler lag drei Monate in einer Funktion, die
    jeder Wirt lesen kann, und wurde nur deshalb nicht gefunden, weil ihn
    niemand OHNE Windows-Pfad befragt hat.
    """
    name = _kosten().projekt_ordnername(voll)
    assert verboten not in name, (
        f"BL-186: `{voll}` ergibt `{name}` — der Doppelpunkt des Laufwerks "
        "steht noch drin. Die CLI schreibt an dieser Stelle einen "
        "Bindestrich, der Ordner wird also nie gefunden.")
    assert "\\" not in name and "/" not in name and "_" not in name, (
        f"`{voll}` ergibt `{name}` — es steht noch ein Trennzeichen darin.")


def test_der_windows_name_trifft_die_echte_form():
    """Die Form, die auf der Maschine wirklich liegt — woertlich nachgestellt."""
    name = _kosten().projekt_ordnername(
        r"C:\Users\adm_mronzani\source\repos\team-kit")
    assert name == "C--Users-adm-mronzani-source-repos-team-kit", (
        f"Gebildet wurde `{name}`. Erwartet ist die Form, die die Agenten-CLI "
        "auf einer Windows-Maschine wirklich anlegt — mit ZWEI Bindestrichen "
        "nach dem Laufwerksbuchstaben (einer fuer den Doppelpunkt, einer fuer "
        "den Trenner).")


# --- Die Suche, gegen eine gestellte Ablage ----------------------------------


def _stelle_ablage(tmp_path, monkeypatch, ordnername, anzahl=1):
    """Ein ~/.claude/projects mit EINEM Projektordner und n Transkripten."""
    heim = tmp_path / "heim"
    ziel = heim / ".claude" / "projects" / ordnername
    ziel.mkdir(parents=True)
    for i in range(anzahl):
        p = ziel / f"sitzung-{i}.jsonl"
        # Eine echte Transkriptzeile, nicht `{}`: Ohne Nutzungsdaten bricht
        # `sitzung-messen` vor der Ausgabe ab, und der Test wuerde die
        # Auswahl pruefen, ohne dass je eine stattgefunden hat. Die
        # Nachrichten-ID ist je Datei verschieden — sonst verwirft die
        # Duplikaterkennung genau das, was hier gezaehlt werden soll.
        p.write_text(json.dumps({"message": {
            "id": f"msg-{i}", "model": "claude-sonnet-5",
            "usage": {"input_tokens": 100, "output_tokens": 10}}}) + "\n",
            encoding="utf-8", newline="\n")
        # Aelter = kleinerer mtime, damit die Reihenfolge pruefbar ist.
        os.utime(p, (1_700_000_000 + i * 60, 1_700_000_000 + i * 60))
    monkeypatch.setenv("HOME", str(heim))
    monkeypatch.setenv("USERPROFILE", str(heim))
    return ziel


def test_findet_den_ordner_unter_dem_echten_namen(tmp_path, monkeypatch):
    projekt = tmp_path / "arbeit" / "mein_projekt"
    projekt.mkdir(parents=True)
    k = _kosten()
    _stelle_ablage(tmp_path, monkeypatch,
                   k.projekt_ordnername(str(projekt.resolve())))
    assert len(k.transkripte_aus_projekt(str(projekt))) == 1


def test_findet_den_ordner_auch_bei_abweichender_schreibweise(tmp_path,
                                                              monkeypatch):
    """Die zweite Stufe der Suche.

    Auf der Fundmaschine liegen Ordner desselben Laufwerks in beiden
    Schreibweisen nebeneinander. Ein zeichengenauer Nachbau haengt damit davon
    ab, wie der aufrufende Prozess sein Arbeitsverzeichnis geschrieben hat —
    das ist kein Zustand, auf den eine Kostenmessung sich stuetzen darf.
    """
    projekt = tmp_path / "arbeit" / "mein_projekt"
    projekt.mkdir(parents=True)
    k = _kosten()
    verdreht = k.projekt_ordnername(str(projekt.resolve())).upper()
    if verdreht == k.projekt_ordnername(str(projekt.resolve())):
        pytest.skip("Pfad hat keine Buchstaben, deren Schreibweise abweichen kann")
    _stelle_ablage(tmp_path, monkeypatch, verdreht)
    assert k.transkripte_aus_projekt(str(projekt)), (
        "Der Ordner liegt da, nur anders geschrieben — und die Messung "
        "meldet trotzdem 'kein Transkript gefunden'.")


def test_ein_projekt_ohne_ordner_bleibt_leer(tmp_path, monkeypatch):
    """Die Gegenrichtung: Die lockere Suche darf nicht IRGENDETWAS finden.

    Ohne diesen Fall koennte die zweite Stufe den Ordner eines fremden
    Projekts liefern — und dann bucht jemand fremde Kosten.
    """
    k = _kosten()
    _stelle_ablage(tmp_path, monkeypatch, "ein-ganz-anderes-projekt")
    (tmp_path / "arbeit").mkdir(exist_ok=True)
    assert k.transkripte_aus_projekt(str(tmp_path / "arbeit")) == []


# --- Der Plural --------------------------------------------------------------


def test_alle_transkripte_das_juengste_zuerst(tmp_path, monkeypatch):
    projekt = tmp_path / "arbeit" / "projekt"
    projekt.mkdir(parents=True)
    k = _kosten()
    _stelle_ablage(tmp_path, monkeypatch,
                   k.projekt_ordnername(str(projekt.resolve())), anzahl=3)
    gefunden = k.transkripte_aus_projekt(str(projekt))
    assert len(gefunden) == 3, (
        "BL-186: Die Funktion liefert wieder nur EIN Transkript. Eine Kaskade "
        "ueber mehrere Sitzungen wird damit stillschweigend untertrieben.")
    zeiten = [os.path.getmtime(p) for p in gefunden]
    assert zeiten == sorted(zeiten, reverse=True), (
        f"Nicht nach Aenderungszeit sortiert: {gefunden}")


# --- Der Befehl selbst -------------------------------------------------------


def _lauf(tmp_path, heim, *args, cwd=None):
    umgebung = dict(os.environ)
    umgebung["HOME"] = str(heim)
    umgebung["USERPROFILE"] = str(heim)
    umgebung["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(WERKZEUG), "sitzung-messen", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=umgebung, cwd=str(cwd or tmp_path))


def test_der_befehl_verschweigt_die_uebrigen_sitzungen_nicht(tmp_path,
                                                             monkeypatch):
    """Der eigentliche Schaden des zweiten Teils war die STILLE.

    `sitzung-messen` misst weiterhin EINE Sitzung — das ist sein Name und
    bleibt der Default. Neu ist, dass der Aufruf sagt, was er nicht gemessen
    hat, und den Ausweg nennt. Eine Messung, die zu wenig liefert und dazu
    schweigt, ist schlimmer als eine, die abbricht.
    """
    projekt = tmp_path / "arbeit" / "projekt"
    projekt.mkdir(parents=True)
    k = _kosten()
    ziel = _stelle_ablage(tmp_path, monkeypatch,
                          k.projekt_ordnername(str(projekt.resolve())),
                          anzahl=4)
    heim = ziel.parents[2]
    r = _lauf(tmp_path, heim, "--projekt", str(projekt))
    aus = r.stdout + r.stderr
    assert "4 Transkripte" in aus, (
        f"Der Aufruf nennt die uebrigen drei Sitzungen nicht:\n{aus}")
    assert "--alle" in aus, f"Der Ausweg wird nicht genannt:\n{aus}"


def test_alle_nimmt_wirklich_alle(tmp_path, monkeypatch):
    projekt = tmp_path / "arbeit" / "projekt"
    projekt.mkdir(parents=True)
    k = _kosten()
    ziel = _stelle_ablage(tmp_path, monkeypatch,
                          k.projekt_ordnername(str(projekt.resolve())),
                          anzahl=3)
    heim = ziel.parents[2]
    r = _lauf(tmp_path, heim, "--projekt", str(projekt), "--alle")
    gelesen = [z for z in (r.stdout + r.stderr).splitlines() if "gelesen:" in z]
    assert len(gelesen) == 3, (
        f"--alle hat {len(gelesen)} statt 3 Transkripte gelesen:\n"
        f"{r.stdout}{r.stderr}")


def test_die_nutzungszeile_nennt_den_schalter():
    """Ein Schalter, den die Hilfe nicht nennt, existiert fuer den Anwender nicht."""
    r = subprocess.run(
        [sys.executable, str(WERKZEUG), "sitzung-messen"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert "--alle" in (r.stdout + r.stderr), (
        f"Die Nutzungszeile nennt --alle nicht:\n{r.stdout}{r.stderr}")

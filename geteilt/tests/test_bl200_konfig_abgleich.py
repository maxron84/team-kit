#!/usr/bin/env python3
"""BL-200 — ein `--update` trägt neue Konfigurationswerte nicht ins Feldprojekt
nach und liefert damit Fixes aus, die es im selben Zug wieder aufhebt.

Der Grundsatz *„`--update` fasst `team.config.*` nicht an"* ist richtig; die
Datei trägt Projektwerte. Es gab aber **keinen Schritt, der die
SCHLÜSSELMENGE abgleicht**: Ein Wert, den die Vorlage neu einführt, erreichte
eine bestehende Installation nie — und wurde auch nicht gemeldet.

GEMESSEN IM FELD (`Feld B`, 2026-08-27), nicht vermutet: Nach dem Update
fehlten in `team.config.ps1` **vier** Werte, die die Vorlage inzwischen setzt.
`TEAM_MELDUNG_TOOL` (`BL-182`) ist dabei **hart** — `Team-Werkzeug ''` läuft in
`& $null` und bricht ab, für JEDES Verb des Rückkanals. Das Update hat den Fix
also ausgeliefert und den Fehler mit **wörtlich derselben Meldung**
wiederhergestellt, nur eine Zeile tiefer.

Der Eintrag hat drei Teile, und diese Datei sichert alle drei:

  (1) `konfig_abgleich` meldet die fehlenden Werte **namentlich**, mit der
      kopierbaren Zeile daneben — und ein hart abbrechender Wert bekommt einen
      ROTEN Befund statt eines gelben Hinweises.
  (2) Die GATTUNG: Was ein Entrypoint oder die Bibliothek liest, steht in der
      Vorlagen-Konfiguration — und die Schlüsselmengen beider Bahnen sind
      deckungsgleich, bis auf begründete Ausnahmen.
  (3) Die kopierbaren Zeilen in `python_abgleich` nennen `TEAM_MELDUNG_TOOL`.

Die Gegenprobe ist der Teil, ohne den es keine Meldung ist: Dieselbe
Installation **vollständig** muss schweigen.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, ueberspringe_ohne_bahn

WURZEL = Path(__file__).resolve().parents[2]

VORLAGE = {
    "bash": WURZEL / "bash" / "entry" / "team.config.sh",
    "pwsh": WURZEL / "pwsh" / "entry" / "team.config.ps1",
}
INSTALLER = {
    "bash": WURZEL / "bash" / "install.sh",
    "pwsh": WURZEL / "pwsh" / "install.ps1",
}

MUSTER = {
    "bash": re.compile(r"(?m)^(TEAM_[A-Z0-9_]+)="),
    "pwsh": re.compile(r"(?m)^\$(TEAM_[A-Z0-9_]+)\s*="),
}

# Die begruendeten Ausnahmen vom Gleichstand. Wer eine Ausnahme fuehrt,
# schreibt den Grund daneben — sonst sehen eine bewusste und eine vergessene
# Portierung gleich aus (dieselbe Erwaegung wie `@pytest.mark.nur_bash`).
AUSNAHMEN = {
    "TEAM_PYTHON": (
        "bash",
        "Die bash-Bahn ruft `\"$TEAM_PYTHON\" team/tools/…` direkt auf — die "
        "Wortzerlegung der Shell erledigt den Rest. PowerShell uebergibt eine "
        "Zeichenkette als EIN Argument und braucht deshalb fertige "
        "Werkzeugzeilen statt eines Interpreternamens."),
    "TEAM_MELDUNG_TOOL": (
        "pwsh",
        "Das Gegenstueck zur Zeile darueber: Weil die pwsh-Bahn ganze "
        "Werkzeugzeilen braucht, hat sie fuer kit_meldung.py eine eigene "
        "(BL-182). Die bash-Bahn kommt mit TEAM_PYTHON aus."),
}


def _schluessel(bahn):
    datei = VORLAGE[bahn]
    if not datei.is_file():
        pytest.skip(f"{datei.name} liegt nur im Kit")
    return set(MUSTER[bahn].findall(datei.read_text(encoding="utf-8")))


# --- (2) Die Gattung: dieselben Werte auf beiden Bahnen ----------------------


def test_die_schluesselmengen_beider_bahnen_sind_deckungsgleich():
    """`BL-126` sichert bisher nur, dass beide Dateien GESCHRIEBEN werden —
    nicht, dass sie dasselbe SETZEN. Genau in dieser Lücke ist der Feldfall
    entstanden."""
    bash_keys, pwsh_keys = _schluessel("bash"), _schluessel("pwsh")
    nur_bash = bash_keys - pwsh_keys
    nur_pwsh = pwsh_keys - bash_keys
    unerklaert = []
    for name in sorted(nur_bash | nur_pwsh):
        wo = "bash" if name in nur_bash else "pwsh"
        if AUSNAHMEN.get(name, (None,))[0] != wo:
            unerklaert.append(f"{name} (nur in der {wo}-Vorlage)")
    assert not unerklaert, (
        "Die beiden Konfigurations-Vorlagen setzen verschiedene Werte, und für "
        "diese steht kein Grund in AUSNAHMEN:\n  " + "\n  ".join(unerklaert)
        + "\nEntweder gehört der Wert in beide Vorlagen — oder die Ausnahme "
          "gehört benannt und begründet (BL-200).")


def test_jede_ausnahme_gilt_noch():
    """Eine Ausnahmeliste, die niemand nachprüft, wird zur Erlaubnis mit
    unbekanntem Umfang. Steht ein Name wieder in BEIDEN Vorlagen, gehört er
    hier heraus."""
    bash_keys, pwsh_keys = _schluessel("bash"), _schluessel("pwsh")
    veraltet = [n for n in AUSNAHMEN if n in bash_keys and n in pwsh_keys]
    assert not veraltet, (
        "Diese Namen stehen inzwischen in BEIDEN Vorlagen — die Ausnahme ist "
        f"überholt und gehört aus AUSNAHMEN gestrichen: {veraltet}")


def test_was_die_bibliothek_ohne_rueckfall_liest_steht_in_der_vorlage(schale):
    """Der Riegel für den NÄCHSTEN Wert, nicht für diesen.

    Ein `$TEAM_*`, das die Bibliothek liest, ohne einen eigenen Default zu
    setzen, muss aus der Konfiguration kommen — sonst ist es im Feld leer, und
    ob das gnädig oder hart ausgeht, entscheidet der Zufall.
    """
    lib = schale.kit_lib.read_text(encoding="utf-8")
    vorlage = _schluessel(schale.name)
    if schale.ist_bash:
        # Ein `${NAME:-wert}` TRAEGT seinen Rueckfall an der Lesestelle —
        # das ist die bash-Schreibweise fuer einen Umgebungsschalter
        # (TEAM_DRY_RUN, TEAM_LOCK_HELD) und kein Projektwert.
        gelesen = set(re.findall(r"\$\{?(TEAM_[A-Z0-9_]+)\b", lib))
        mit_default = set(re.findall(r"\$\{(TEAM_[A-Z0-9_]+):-", lib))
    else:
        # Auf der pwsh-Bahn tragen die Umgebungsschalter ein `$env:` und
        # fallen deshalb gar nicht erst in `gelesen`.
        gelesen = set(re.findall(r"\$(TEAM_[A-Z0-9_]+)\b", lib))
        mit_default = set(re.findall(r"Team-Default '(TEAM_[A-Z0-9_]+)'", lib))
    # Was die Bibliothek selbst ABLEITET oder als LAUFZEITZUSTAND fuehrt,
    # kommt nicht aus der Konfiguration. `$script:TEAM_LAST_COST` ist kein
    # Projektwert, sondern das Ergebnis des letzten Aufrufs — ein Riegel,
    # der ihn einfordert, meldet dauerhaft etwas Richtiges als Fehler und
    # wird nach BL-14 weggesehen.
    abgeleitet = set(re.findall(
        r"(?m)^\s*(?:\$(?:script:|env:)?)?(TEAM_[A-Z0-9_]+)\s*=",
        lib))
    offen = sorted(gelesen - mit_default - abgeleitet - vorlage)
    assert not offen, (
        f"{schale.lib_name} liest diese Werte, setzt keinen eigenen Default "
        "und die Vorlagen-Konfiguration nennt sie nicht — im Feld sind sie "
        "damit leer, ohne dass es jemand merkt (BL-200):\n  "
        + "\n  ".join(offen))


# --- (1) Der Abgleich meldet namentlich, und Hartes rot ----------------------


def test_beide_installer_gleichen_die_schluesselmenge_ab(schale):
    datei = INSTALLER[schale.name]
    if not datei.is_file():
        pytest.skip(f"{datei.name} liegt nur im Kit")
    text = datei.read_text(encoding="utf-8")
    for was, muster in (("die Abgleich-Funktion", r"[Kk]onfig[-_][Aa]bgleich"),
                        ("den Aufruf im Update-Pfad", r"[Kk]onfig[-_][Aa]bgleich\b"),
                        ("die Fundnummer", r"BL-200")):
        assert re.search(muster, text), (
            f"{datei.name} hat {was} nicht — ein neuer Konfigurationswert "
            "erreicht eine bestehende Installation damit weiter nie (BL-200).")
    assert "_TOOL" in text, (
        f"{datei.name} unterscheidet den harten Fall nicht. Ein Wert, der ohne "
        "Inhalt abbricht, ist kein gelber Hinweis — die Installation ist "
        "danach nicht unvollständig, sondern kaputt.")


@pytest.mark.nur_bash(
    "Fährt install.sh gegen eine präparierte Installation. Das pwsh-Gegenstück "
    "trägt dieselbe Funktion und wird von kit-test.ps1 gefahren; ein zweiter "
    "Installer-Lauf hier kostete Minuten für dieselbe Zusicherung.")
def test_ein_fehlender_wert_wird_namentlich_gemeldet(tmp_path):
    """Der Feldfall: Aus `team.config.ps1` fehlt `TEAM_MELDUNG_TOOL`.

    Geprüft wird die FUNKTION, nicht der ganze Installer-Lauf: Sie ist die
    Stelle, an der der Befund entsteht, und ein voller `--update` bräuchte
    eine echte Installation.
    """
    if not BASH or not INSTALLER["bash"].is_file():
        pytest.skip("install.sh oder bash fehlt")
    ziel = tmp_path / "projekt"
    ziel.mkdir()
    for bahn in ("bash", "pwsh"):
        if not VORLAGE[bahn].is_file():
            pytest.skip("die Vorlagen liegen nur im Kit")
    # Die installierte Konfiguration ist die Vorlage OHNE eine Zeile.
    for bahn, name in (("bash", "team.config.sh"), ("pwsh", "team.config.ps1")):
        zeilen = VORLAGE[bahn].read_text(encoding="utf-8").splitlines(True)
        behalten = [z for z in zeilen
                    if not re.match(r"^\$?TEAM_MELDUNG_TOOL[\s=]", z)]
        (ziel / name).write_text("".join(behalten), encoding="utf-8")

    ausgabe = _konfig_abgleich(ziel)
    assert "TEAM_MELDUNG_TOOL" in ausgabe, (
        "Der fehlende Wert wird nicht NAMENTLICH gemeldet — dann weiß niemand, "
        f"was nachzutragen ist (BL-200).\n{ausgabe}")
    assert "kit_meldung.py" in ausgabe, (
        "Die kopierbare Zeile fehlt. Ein Befund ohne den Nachtrag daneben "
        f"verlangt genau die Arbeit, die er abnehmen wollte (BL-44).\n{ausgabe}")
    assert "bricht der Aufruf ab" in ausgabe, (
        "Ein Wert, der ohne Inhalt hart abbricht, muss als solcher benannt "
        f"werden statt als gelber Hinweis.\n{ausgabe}")


@pytest.mark.nur_bash("Gegenrichtung zum Fall darüber, derselbe Aufruf.")
def test_eine_vollstaendige_konfiguration_schweigt(tmp_path):
    """Ohne diese Richtung ist der Fix eine Warnung, die immer erscheint — und
    die erzieht zum Wegsehen (`BL-14`)."""
    if not BASH or not INSTALLER["bash"].is_file():
        pytest.skip("install.sh oder bash fehlt")
    ziel = tmp_path / "projekt"
    ziel.mkdir()
    for bahn, name in (("bash", "team.config.sh"), ("pwsh", "team.config.ps1")):
        if not VORLAGE[bahn].is_file():
            pytest.skip("die Vorlagen liegen nur im Kit")
        (ziel / name).write_text(VORLAGE[bahn].read_text(encoding="utf-8"),
                                 encoding="utf-8")
    ausgabe = _konfig_abgleich(ziel)
    assert "fehlt" not in ausgabe, (
        f"Eine vollständige Konfiguration darf nichts melden.\n{ausgabe}")
    assert "alle Werte der Vorlage sind da" in ausgabe, (
        f"…und soll das auch sagen.\n{ausgabe}")


def _konfig_abgleich(ziel):
    """Ruft `konfig_abgleich` aus install.sh gegen <ziel> auf.

    Der Installer wird dafür gesourct und NICHT ausgeführt: Er bricht ohne
    Argumente ab, und ein vollständiger Lauf legte ein Projekt an. Möglich ist
    das, weil die Funktionen oben im Skript stehen — dieselbe Eigenschaft, die
    `BL-127` erzwungen hat.
    """
    skript = (
        'KIT="$1"; ZIEL="$2"\n'
        'gruen() { echo "$@"; }; gelb() { echo "$@"; }; rot() { echo "$@"; }\n'
        # Nur den Funktionsteil einlesen: Alles ab dem Argument-Parser wuerde
        # laufen wollen.
        'eval "$(sed -n "/^konfig_schluessel()/,/^}$/p;'
        '/^konfig_vorlagenzeile()/,/^}$/p;'
        '/^konfig_abgleich()/,/^}$/p" "$KIT/bash/install.sh")"\n'
        'konfig_abgleich\n')
    return subprocess.run(
        [BASH, "-c", skript, "bash", str(WURZEL), str(ziel)],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace").stdout


# --- (3) Der Nebenbefund ------------------------------------------------------


def test_die_kopierbaren_zeilen_nennen_das_dritte_werkzeug(schale):
    """`TEAM_MELDUNG_TOOL` ist seit `BL-182` die dritte Zeile derselben Bauart
    und fehlte in beiden Installern."""
    datei = INSTALLER[schale.name]
    if not datei.is_file():
        pytest.skip(f"{datei.name} liegt nur im Kit")
    text = datei.read_text(encoding="utf-8")
    for werkzeug in ("TEAM_BEUTEBUCH_TOOL", "TEAM_KOSTEN_TOOL",
                     "TEAM_MELDUNG_TOOL"):
        assert f"'{werkzeug}'" in text or f"{werkzeug}=" in text, (
            f"{datei.name} nennt {werkzeug} nicht in den kopierbaren Zeilen "
            "des Interpreter-Abgleichs (BL-200).")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

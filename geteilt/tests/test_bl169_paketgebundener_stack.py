#!/usr/bin/env python3
"""Regressionstest fuer BL-169: Die ausgelieferten Ordner-Defaults machen
Reproducer-Tests in jedem paketgebundenen Stack unausfuehrbar — und zwar STUMM.

DER BEFUND (Feld E, 2026-08-23, vom Architekten beim Aushaerten der ERSTEN
Kaskade gefunden — durch Lesen der Kopplung, BEVOR ein Lauf startete):
`src/` + `tests/` traegt, solange der Testlaeufer die Dateien am PFAD findet
(pytest). Es traegt NICHT, sobald er sie am PAKET findet. Dart/Flutter sammelt
ausschliesslich innerhalb des Pakets und ausschliesslich unterhalb von `test/`;
liegt das Paket unter `src/`, liegt der vom Kit vorgesehene Testordner
AUSSERHALB davon. Dieselbe Bauart bei Cargo, Go und Gradle.

DIE ZWEITE HAELFTE IST VOM ORDNER UNABHAENGIG und wiegt schwerer: Der Laeufer
nimmt nur Dateien mit einem bestimmten NAMENSMUSTER — `_test.dart`, `_test.go`.
Die Kit-Konvention `test_hm<nr>_<stichwort>.py` buchstabengetreu auf Dart
uebertragen ergibt `test_hm36_foo.dart`, einen Namen, den der Laeufer ignoriert.

DIE FOLGE IST IN BEIDEN HAELFTEN DIESELBE und schlimmer als ein Fehler: Franks
regelkonform abgelegter Reproducer wird nie ausgefuehrt, der Smoke-Test bleibt
gruen, das Beutebuch zeigt einen Fund mit Reproducer — geprueft wird nichts.
Dasselbe Zeitfenster wie `BL-149`: Getroffen wird ausschliesslich der ERSTLAUF.
Hat ein Projekt seine Ordner einmal richtig gesetzt, ist der Default fuer immer
unsichtbar, und ein laufendes Projekt kann den Fehler gar nicht mehr erleben.

DIE ZWEI WEGE DES EINTRAGS, und beide sind gebaut:
  (1) Der Installer meldet den erkannten Stack gegen die Vorgabewerte — GEMELDET,
      NICHT REPARIERT. Der Stack steht als freie Prosa da ("Flutter Dart
      sqlite"); ein Installer, der daraus stillschweigend Ordner umschreibt,
      raet. Dieselbe Entscheidung wie in `BL-200`.
  (2) Wo der Stack unbekannt bleibt, steht die Kopplung im Kommentar der
      ausgelieferten Konfiguration: *Der Testordner muss dort liegen, wo der
      Laeufer sucht, und der Dateiname so heissen, dass er ihn nimmt.*

WAS DIESE FAELLE NICHT LEISTEN: die vom Eintrag verlangte Gegenprobe am
LAEUFER — eine frische Installation fuer einen paketgebundenen Stack, in der
der konfigurierte Smoke-Test die Reproducer-Datei nachweislich AUSFUEHRT. Die
braucht Dart/Cargo/Go auf dem Wirt. Sie steht im Backlog benannt offen.
"""
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]

INSTALLER = [("bash", "bash/install.sh"), ("pwsh", "pwsh/install.ps1")]
KONFIGS = [("bash", "bash/entry/team.config.sh"),
           ("pwsh", "pwsh/entry/team.config.ps1")]


def _lies(rel, was):
    pfad = WURZEL / rel
    if not pfad.is_file():
        pytest.skip(f"{was} liegt hier nicht (Bahn abgewaehlt oder "
                    f"installierte Ablage statt Kit-Ablage)")
    return pfad.read_text(encoding="utf-8")


# --- Weg (1): der Installer meldet den erkannten Stack ----------------------

@pytest.mark.parametrize("bahn,rel", INSTALLER)
def test_der_installer_kennt_die_paketgebundenen_stacks(bahn, rel):
    """Alle vier Gattungen, die der Eintrag namentlich nennt.

    Eine Liste, die nur Dart kennt, faengt den gemeldeten Fall und laesst die
    drei danebenliegenden stehen — der Eintrag nennt sie ausdruecklich als
    dieselbe Bauart.
    """
    text = _lies(rel, rel)
    for stack in ("dart", "flutter", "cargo", "rust", "gradle"):
        assert stack in text.lower(), (
            f"{rel} erkennt '{stack}' nicht — dieser Stack laeuft dann in den "
            f"stummen Fall (BL-169).")


@pytest.mark.parametrize("bahn,rel", INSTALLER)
def test_die_meldung_nennt_die_richtigen_werte_statt_nur_zu_warnen(bahn, rel):
    """Eine Warnung ohne Ausweg ist eine Beschwerde.

    Der Leser sitzt im Interview und hat gerade geantwortet; er braucht die
    zwei Ordner UND das Namensmuster, nicht die Aufforderung, selbst zu
    suchen.
    """
    text = _lies(rel, rel)
    assert "lib/" in text and "_test.dart" in text, (
        f"{rel} nennt fuer Dart/Flutter nicht beide Haelften (Ordner UND "
        f"Namensmuster). Die zweite wiegt laut Eintrag schwerer.")
    assert "_test.go" in text, (
        f"{rel} nennt das Go-Namensmuster nicht.")


@pytest.mark.parametrize("bahn,rel", INSTALLER)
def test_der_installer_repariert_NICHT_von_selbst(bahn, rel):
    """Die Bauentscheidung, und sie ist dieselbe wie in `BL-200`.

    Der Stack ist freie Prosa. Ein Installer, der daraus Ordner umschreibt,
    raet — und ueberschreibt womoeglich eine bewusste Antwort. Gemeldet wird,
    repariert nicht; und die Meldung sagt das selbst, sonst wartet der Leser
    auf eine Aenderung, die nicht kommt.
    """
    text = _lies(rel, rel)
    assert "Geändert wird hier nichts" in text, (
        f"{rel} sagt nicht, dass es NICHTS aendert — der Leser haelt die "
        f"Meldung dann fuer eine erledigte Korrektur.")


@pytest.mark.parametrize("bahn,rel", INSTALLER)
def test_die_meldung_nennt_die_stumme_folge(bahn, rel):
    """Der Grund, warum dieser Fall ueberhaupt teuer ist.

    Ein falscher Ordner allein klaenge nach Kosmetik. Dass der Reproducer nie
    laeuft, der Smoke-Test aber GRUEN bleibt, ist der eigentliche Schaden —
    das Beutebuch zeigt dann einen Fund mit Reproducer, und geprueft wird
    nichts.
    """
    text = _lies(rel, rel)
    assert "NIE ausgeführt" in text or "NIE ausgefuehrt" in text, (
        f"{rel} nennt die Folge nicht.")
    assert "bleibt grün" in text or "bleibt gruen" in text, (
        f"{rel} sagt nicht, dass der Smoke-Test dabei GRUEN bleibt — genau "
        f"das macht den Fall stumm.")


# --- Weg (2): die Kopplung steht in der ausgelieferten Konfiguration --------

@pytest.mark.parametrize("bahn,rel", KONFIGS)
def test_die_konfiguration_erklaert_die_kopplung(bahn, rel):
    """Fuer den Stack, den der Installer NICHT erkennt.

    Weg (1) hilft dem erkannten Stack, Weg (2) dem unerkannten. Der Eintrag
    verlangt ausdruecklich beides, nicht eines davon.
    """
    text = _lies(rel, rel)
    block = text[text.index("Test-Ordner"):][:2200]
    assert "Kit-BL-169" in block, (
        f"{rel}: Der Kommentar am Testordner nennt die Kopplung nicht.")
    assert "PFAD" in block and "aket" in block, (
        f"{rel}: Der Kommentar unterscheidet nicht zwischen Pfad- und "
        f"Paketsuche — das ist die ganze Kopplung.")
    assert "_test.dart" in block or "_test.go" in block, (
        f"{rel}: Der Kommentar nennt die zweite Haelfte nicht (das "
        f"Namensmuster), und die wiegt laut Eintrag schwerer als der Ordner.")


# --- Gleichstand -------------------------------------------------------------

def test_beide_bahnen_melden_dasselbe():
    """Sonst sichert eine Bahn weniger zu als die andere (`BL-145`)."""
    texte = [_lies(rel, rel) for _, rel in INSTALLER]
    for satz in ("Kit-BL-169", "Geändert wird hier nichts",
                 "_test.dart", "Programmcode:"):
        assert all(satz in t for t in texte), (
            f"„{satz}“ steht nur in EINEM der beiden Installer.")

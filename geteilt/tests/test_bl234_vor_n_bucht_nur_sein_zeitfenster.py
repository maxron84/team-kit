#!/usr/bin/env python3
"""BL-234: `--rollen-abschluss vor-N` buchte IMMER den gesamten unarchivierten
Bestand — der BL-221-Riegel greift bei benannten Nummern nicht.

WAS IM FELD PASSIERT IST
    `Feld E`, nach dem Lauf der Kaskade 15. `--budget` meldete korrekt drei
    unarchivierte Altlogs ueber 3,2621 USD und nannte den dokumentierten
    Ausweg: *„gehoeren sie unter eine eigene benannte Nummer
    (`--kaskade vor-N`)"*. Der Anwender folgte dieser Anweisung woertlich.

    Gebucht wurden **alle 14** unarchivierten Logs — die drei Altlogs PLUS
    die kompletten Laufkosten der gerade abgeschlossenen Kaskade: 17,68 USD
    unter der falschen Nummer, kommentarlos, und die Rohlogs im selben Zug
    archiviert. Der Zustand danach ist genau der, den `BL-221` verhindern
    soll: Die Kosten stehen falsch UND die Belege sind weggeraeumt.

WARUM DER RIEGEL NICHT GRIFF
    `logs_vor_kaskadenbeginn()` haelt die Zeitmarke jedes Logs gegen den
    BEGINN EINER KASKADE. Eine benannte Nummer wie `vor-15` hat keinen — es
    gibt keine Plandatei, an der er sich festmachen liesse. `kaskade_beginn`
    gibt None, die Liste bleibt leer, `if _zu_alt:` ist falsch, und damit gilt
    JEDES Log als zugehoerig. **Der Schutz fehlte ausgerechnet in dem Fall,
    fuer den `vor-N` erfunden wurde** — der Kommentar ueber dem Riegel
    beschreibt diesen Fall sogar woertlich.

WARUM EIN DOKU-SATZ NICHT GENUEGT
    Die Anweisung, die in die Falle fuehrt, ist bereits die KORREKTUR-
    anweisung eines anderen Riegels. Und die Reihenfolge macht es schlimmer:
    Die BL-221-Warnung erscheint NACH dem Lauf, also genau dann, wenn die
    frischen Laufkosten unarchiviert daneben liegen — der empfohlene Befehl
    trifft immer den unguenstigsten Zeitpunkt.

WARUM DAS FENSTER NUR EINE KANTE HAT
    Die obere Kante ist der Beginn der Kaskade N: dieselbe Quelle wie beim
    BL-221-Riegel, die Commit-Zeit der Plandatei, sekundengenau. Die untere
    (das Ende der letzten gebuchten Kaskade) stuende nur im Ledger, und dort
    steht ein DATUM ohne Uhrzeit — im Feldfall endete der Frank-Lauf um 23:07
    und die Kaskade begann um 23:18 am SELBEN Tag. Eine Kante mit
    Tagesaufloesung wuerde richtige Logs anschlagen oder falsche durchlassen;
    geraten wird hier nicht. Die obere Kante allein haette den Feldfall
    vollstaendig gefangen: elf der vierzehn Logs liegen NACH dem Beginn von
    Kaskade 15.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      verlange_pwsh, werkzeug_wert)

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"

STUNDE = 3600


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True)


def _repo(tmp_path, plan_nummer="15"):
    """Projekt mit scharfgeschalteter Kaskade N — der Beginn ist die
    Commit-Zeit der Plandatei, also eine echte, maschinell lesbare Marke."""
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@l")
    _git(tmp_path, "config", "user.name", "T")
    (tmp_path / "plans").mkdir()
    if plan_nummer is not None:
        (tmp_path / "plans" / f"ralph-kaskade-{plan_nummer}-produkt.md"
         ).write_text("# Plan\n", encoding="utf-8")
    else:
        (tmp_path / "plans" / "liesmich.md").write_text("x\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "scharf")
    (tmp_path / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    (tmp_path / ".team-logs").mkdir()
    return tmp_path


def _beginn(repo, nummer="15"):
    beginn = kosten.kaskade_beginn(nummer, str(repo))
    assert beginn is not None, (
        "Die Vorbedingung dieses Tests haelt nicht: Der Kaskadenbeginn ist "
        "nicht ermittelbar, damit wuerde jeder Fall unten stumm gruen.")
    return beginn


def _log(repo, name, usd, mtime):
    datei = repo / ".team-logs" / name
    datei.write_text(json.dumps({"total_cost_usd": usd}), encoding="utf-8")
    os.utime(datei, (mtime, mtime))
    return datei


def _feldlage(repo):
    """Die Lage aus dem Feld: drei Altlogs vor dem Kaskadenbeginn, elf Logs
    des gerade gelaufenen Baus danach."""
    beginn = _beginn(repo)
    for i in range(3):
        _log(repo, f"alt-{i}.json", 1.0874, beginn - 2 * STUNDE + i)
    for i in range(11):
        _log(repo, f"neu-{i}.json", 1.3200, beginn + STUNDE + i)
    return beginn


def _buche(repo, kaskade, *zusatz, verb="rollen-abschluss"):
    return subprocess.run(
        [sys.executable, str(KOSTEN_PY), verb,
         "--kaskade", kaskade, "--domaene", "produkt",
         "--logs", str(repo / ".team-logs"),
         "--pfad", str(repo / ".budget-ledger"), "--repo", str(repo),
         "--archivieren", *zusatz],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))


def _zeilen(repo):
    return list(kosten.ledger_zeilen(str(repo / ".budget-ledger")))


def _archiviert(repo):
    return sorted(p.name for p in
                  (repo / ".team-logs" / "archiv").glob("*.json")) \
        if (repo / ".team-logs" / "archiv").is_dir() else []


# --- Der Fall aus dem Feld ---------------------------------------------------

def test_vor_n_bucht_nicht_den_ganzen_bestand(tmp_path):
    """Der Kern: 14 Logs liegen da, drei gehoeren zu `vor-15`."""
    repo = _repo(tmp_path)
    _feldlage(repo)
    r = _buche(repo, "vor-15")
    assert r.returncode != 0, (
        "BL-234 ist zurueck: `vor-15` hat den gesamten unarchivierten Bestand "
        f"anstandslos gebucht.\n{r.stdout}")
    assert not _zeilen(repo), \
        "eine abgebrochene Buchung darf keine Ledger-Zeile hinterlassen"


def test_der_abbruch_raeumt_die_belege_NICHT_weg(tmp_path):
    """Die zweite Haelfte des Schadens, und die irreversible.

    Im Feld standen die Kosten falsch UND die Rohlogs waren archiviert — ein
    zweiter Aufruf fand sie nicht mehr. Erst entscheiden, dann archivieren
    (dieselbe Reihenfolge, die BL-221 erzwungen hat).
    """
    repo = _repo(tmp_path)
    _feldlage(repo)
    _buche(repo, "vor-15")
    assert not _archiviert(repo), (
        "Der Abbruch hat Rohlogs archiviert — damit ist der Zustand danach "
        "schlechter als vorher, weil der zweite Aufruf sie nicht mehr findet.")


def test_die_meldung_nennt_die_zahl_den_zeitpunkt_und_den_weg(tmp_path):
    """Eine Warnung, die den Weg heraus nicht nennt, ist eine Sackgasse — und
    genau in diese Lage hat die BL-221-Warnung hier gefuehrt."""
    repo = _repo(tmp_path)
    _feldlage(repo)
    r = _buche(repo, "vor-15")
    assert "11 Log(s)" in r.stderr, (
        f"Die Meldung nennt die Anzahl der nicht zugehoerigen Logs nicht:\n"
        f"{r.stderr}")
    assert "--kaskade 15" in r.stderr, (
        "Die Meldung sagt nicht, wohin die Logs gehoeren. Der Anwender ist "
        f"hier gelandet, weil er einer Anweisung gefolgt ist.\n{r.stderr}")
    assert "--auch-neuere" in r.stderr, (
        f"Die benannte Uebersteuerung fehlt in der Meldung.\n{r.stderr}")
    assert "WARNUNG" in r.stderr, (
        "Der Befund muss von den gutartigen [Hinweis]-Zeilen jedes Laufs "
        f"unterscheidbar sein (die Lehre aus BL-221).\n{r.stderr}")


# --- Gegenrichtungen: ohne sie waere der Riegel eine Sperre ------------------

def test_nur_altlogs_werden_anstandslos_gebucht(tmp_path):
    """Der Normalfall der Konvention: eine Out-of-Loop-Runde VOR dem Lauf
    gebucht, es liegt nichts Juengeres daneben."""
    repo = _repo(tmp_path)
    beginn = _beginn(repo)
    for i in range(3):
        _log(repo, f"alt-{i}.json", 1.0874, beginn - 2 * STUNDE + i)
    r = _buche(repo, "vor-15")
    assert r.returncode == 0, r.stderr
    zeilen = _zeilen(repo)
    assert len(zeilen) == 1 and zeilen[0]["kaskade"] == "vor-15"
    assert abs(zeilen[0]["usd"] - 3.2622) < 0.001, zeilen[0]


def test_auch_neuere_bucht_nach_ausdruecklicher_ansage(tmp_path):
    """Ein Riegel ohne benannte Uebersteuerung ist eine Sackgasse. Es gibt
    legitime Faelle — etwa eine Runde, die bewusst ueber den Kaskadenbeginn
    hinweg gelaufen ist."""
    repo = _repo(tmp_path)
    _feldlage(repo)
    r = _buche(repo, "vor-15", "--auch-neuere")
    assert r.returncode == 0, r.stderr
    zeilen = _zeilen(repo)
    assert len(zeilen) == 1 and zeilen[0]["kaskade"] == "vor-15"
    assert "Hinweis" in r.stderr, (
        "Auf `--auch-neuere` hin bleibt der Befund stehen — nur nicht mehr "
        f"als Abbruch.\n{r.stderr}")


def test_eine_numerische_nummer_bleibt_unberuehrt(tmp_path):
    """Der Riegel gilt NUR benannten Nummern. Eine echte Kaskade bucht ihre
    eigenen Logs; dort wacht der BL-221-Riegel in der anderen Richtung."""
    repo = _repo(tmp_path)
    beginn = _beginn(repo)
    for i in range(11):
        _log(repo, f"neu-{i}.json", 1.3200, beginn + STUNDE + i)
    r = _buche(repo, "15")
    assert r.returncode == 0, r.stderr
    zeilen = _zeilen(repo)
    assert len(zeilen) == 1 and zeilen[0]["kaskade"] == "15"


def test_ohne_plandatei_wird_nicht_geraten(tmp_path):
    """Ist die Kaskade N noch nicht scharfgeschaltet, gibt es keine Marke —
    dann wird gebucht statt gewarnt. Ein Waechter, der bei fehlender
    Information warnt, warnt immer (dieselbe Regel wie in `kaskade_beginn`).
    """
    repo = _repo(tmp_path, plan_nummer=None)
    jetzt = os.path.getmtime(repo / ".budget-ledger")
    for i in range(4):
        _log(repo, f"log-{i}.json", 1.0, jetzt + i)
    r = _buche(repo, "vor-15")
    assert r.returncode == 0, r.stderr
    assert len(_zeilen(repo)) == 1


def test_ein_beliebiger_name_ist_keine_vorlauf_runde(tmp_path):
    """`vor-N` ist die Konvention, an der die Nummer N haengt. Ein anderer
    Name sagt ueber den Zeitraum nichts — und ein Riegel, der daraus etwas
    ableitet, haette geraten."""
    assert kosten.kaskade_vorlauf_von("nachtrag") is None
    assert kosten.kaskade_vorlauf_von("15") is None
    assert kosten.kaskade_vorlauf_von("vor-15") == 15
    repo = _repo(tmp_path)
    beginn = _beginn(repo)
    _log(repo, "neu.json", 2.0, beginn + STUNDE)
    r = _buche(repo, "nachtrag")
    assert r.returncode == 0, r.stderr


def test_ralph_abschluss_traegt_denselben_riegel(tmp_path):
    """Die EINE Bedienhandlung ruft BEIDE Verben — im Feld sind beide Zeilen
    falsch gebucht worden. Ein Riegel an nur einem laesst die Haelfte des
    Schadens stehen (Bauart BL-4)."""
    repo = _repo(tmp_path)
    beginn = _beginn(repo)
    (repo / ".ralph-logs").mkdir()
    for i in range(5):
        datei = repo / ".ralph-logs" / f"stufe-{i}.json"
        datei.write_text(json.dumps({"total_cost_usd": 2.1730}),
                         encoding="utf-8")
        os.utime(datei, (beginn + STUNDE + i,) * 2)
    r = subprocess.run(
        [sys.executable, str(KOSTEN_PY), "ralph-abschluss",
         "--kaskade", "vor-15", "--domaene", "produkt",
         "--logs", str(repo / ".ralph-logs"),
         "--pfad", str(repo / ".budget-ledger"), "--repo", str(repo),
         "--archivieren"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))
    assert r.returncode != 0, r.stdout
    assert not _zeilen(repo)


# --- Weg (3): die Erfolgsmeldung ist sprechend ------------------------------

def test_die_erfolgsmeldung_nennt_die_gebuchte_zeitspanne(tmp_path):
    """Unabhaengig vom Riegel nuetzlich, und im Feld die Stelle, an der es
    aufgefallen waere.

    `9 Log(s) archiviert` ist von `3 Log(s) archiviert` nur an der Zahl zu
    unterscheiden. Aufgefallen ist die Fehlbuchung nur, weil der Mensch die
    erwartete Summe aus der Warnung noch im Kopf hatte — wer die Meldung
    ueberblaettert, merkt nichts, und die Belege sind dann schon archiviert.
    """
    repo = _repo(tmp_path)
    beginn = _beginn(repo)
    for i in range(3):
        _log(repo, f"alt-{i}.json", 1.0874, beginn - 2 * STUNDE + i * 600)
    r = _buche(repo, "vor-15")
    assert r.returncode == 0, r.stderr
    assert "Logs von " in r.stdout and " bis " in r.stdout, (
        "Die Erfolgsmeldung nennt die gebuchte Zeitspanne nicht — damit ist "
        f"eine Fehlzuordnung aus ihr nicht erkennbar.\n{r.stdout}")


def test_ohne_logs_steht_keine_erfundene_spanne(tmp_path):
    """Gegenrichtung zu Weg (3): Eine Spanne ueber null Dateien gibt es
    nicht, und eine erfundene waere schlimmer als keine."""
    repo = _repo(tmp_path)
    r = _buche(repo, "vor-15")
    assert r.returncode == 0, r.stderr
    assert "Logs von " not in r.stdout, r.stdout


# --- Die Durchreiche, ohne die der Fix nicht ankommt (Lehre aus BL-143) ------

def _fixture_bahn(tmp_path, bahn):
    """Die Feldlage auf BEIDEN Kostenquellen.

    `--rollen-abschluss` ist EINE Bedienhandlung und ruft ZWEI Verben (BL-4);
    im Feld sind auch beide Zeilen falsch gebucht worden. Ein `.ralph-logs`,
    das hier leer bliebe, wuerde das zweite Verb mit 0.0000 USD durchlaufen
    lassen und den Nachweis an einer BL-5-Bestandsmeldung scheitern — gemessen
    waere dann nicht die Durchreiche, sondern das Fixture.
    """
    repo = _repo(tmp_path)
    beginn = _feldlage(repo)
    (repo / ".ralph-logs").mkdir()
    for i in range(5):
        datei = repo / ".ralph-logs" / f"stufe-{i}.json"
        datei.write_text(json.dumps({"total_cost_usd": 2.1730}),
                         encoding="utf-8")
        os.utime(datei, (beginn + STUNDE + i,) * 2)
    (repo / "team" / "tools").mkdir(parents=True)
    shutil.copy(kit_pfad("tools", "kosten.py"),
                repo / "team" / "tools" / "kosten.py")
    if bahn == "bash":
        shutil.copy(entrypoint_pfad("team-status.sh"), repo / "team-status.sh")
        shutil.copy(kit_pfad("lib.sh"), repo / "team" / "lib.sh")
        (repo / "team.config.sh").write_text(
            'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n', encoding="utf-8")
    else:
        shutil.copy(entrypoint_pfad("team-status.ps1"), repo / "team-status.ps1")
        shutil.copy(kit_pfad("lib.psm1"), repo / "team" / "lib.psm1")
        (repo / "team.config.ps1").write_text(
            '$TEAM_BEUTEBUCH_TOOL = "' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            '$TEAM_KOSTEN_TOOL = "' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            '$TEAM_DOMAENEN = "produkt"\n', encoding="utf-8-sig")
    return repo


def _pruefe_wrapper(repo, r_ohne, r_mit):
    assert r_ohne.returncode != 0, (
        "Der Wrapper hat den Riegel nicht erreicht — `vor-N` bucht durch ihn "
        f"hindurch den ganzen Bestand.\n{r_ohne.stdout}{r_ohne.stderr}")
    assert r_mit.returncode == 0, (
        "`--auch-neuere` ist unterwegs verlorengegangen. Ein Schalter, den "
        "kosten.py kennt und der Wrapper wegwirft, ist der Fehler aus "
        f"BL-143.\n{r_mit.stdout}{r_mit.stderr}")
    assert [z for z in _zeilen(repo) if z["kaskade"] == "vor-15"], \
        "nach --auch-neuere muss die Zeile unter vor-15 stehen"


def test_bash_wrapper_reicht_auch_neuere_durch(tmp_path):
    verlange_bash()
    repo = _fixture_bahn(tmp_path, "bash")
    ohne = subprocess.run(
        [BASH, "./team-status.sh", "--rollen-abschluss", "vor-15", "produkt"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    mit = subprocess.run(
        [BASH, "./team-status.sh", "--rollen-abschluss", "vor-15", "produkt",
         "Rollen", "Bau", "--auch-neuere"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    _pruefe_wrapper(repo, ohne, mit)


def test_pwsh_wrapper_reicht_auch_neuere_durch(tmp_path):
    verlange_pwsh()
    repo = _fixture_bahn(tmp_path, "pwsh")
    ohne = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./team-status.ps1",
         "--rollen-abschluss", "vor-15", "produkt"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    mit = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./team-status.ps1",
         "--rollen-abschluss", "vor-15", "produkt", "Rollen", "Bau",
         "--auch-neuere"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    _pruefe_wrapper(repo, ohne, mit)


@pytest.mark.parametrize("datei", ["team-status.sh", "team-status.ps1"])
def test_die_nutzungszeile_nennt_den_schalter(datei):
    """Ein Schalter, den die Bedienung nicht nennt, ist fuer den Menschen
    nicht da — und er landet hier in einer Lage, in der er ihn braucht.

    Fehlt die Datei, wird UEBERSPRUNGEN statt rot: In einer einbahnig
    installierten Ablage gibt es das Gegenstueck nicht.
    """
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht (Bahn abgewaehlt)")
    assert "--auch-neuere" in pfad.read_text(encoding="utf-8"), (
        f"{datei} nennt `--auch-neuere` nicht.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

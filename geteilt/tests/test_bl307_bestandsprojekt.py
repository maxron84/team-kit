#!/usr/bin/env python3
"""BL-307: Der erste Update-Selbsttest eines Bestandsprojekts war rot — und
keiner der roten Faelle war ein Defekt des Projekts.

DER BEFUND (`Feld F`, 2026-10-04)
    Das erste `-Update` nach BL-243 und BL-266 endete mit zwei roten Faellen:
    (a) test_bl5 buchte `--kaskade 1` in ein Wegwerf-Ledger, und der
        BL-266-Riegel hielt die frischen Logs gegen den Beginn der Kaskade 2
        DES PROJEKTS, in dem die Suite lief. `kosten.py` las den Plan aus dem
        Arbeitsverzeichnis statt aus dem Projekt des Ledgers — BL-226 hatte
        genau diese Regel schon aufgestellt, fuer einen anderen Riegel.
    (b) test_bl219 suchte den neuen Abschnitt 0 (BL-243) in der CLAUDE.md DES
        PROJEKTS: in einer Datei, die das Update nicht anfasst und eine Zeile
        darueber zum Handabgleich gemeldet hatte.
    In einer Sandbox mit Vorgeschichte (30 Kaskaden, Ledger, Logs, CLAUDE.md
    und Konfiguration in aelterer Fassung) waren es 43 Faelle in 19 Dateien,
    25 der Bauart (a) und 18 der Bauart (b). In einer frischen Installation:
    keiner — deshalb hat der Selbsttest nie etwas gesehen.

DIE PROBE
    (a) am Verhalten: dieselbe Buchung und dieselbe Pruefung, einmal mit dem
        Ledger im Projekt (die Riegel greifen), einmal mit dem Ledger daneben
        (sie greifen nicht).
    (b) an `conftest.quelle` und am Quelltext der Suite: Keine Testdatei
        faellt von einer Vorlage auf die Projektdatei zurueck.
    Die Wirkung im Ganzen prueft der Selbsttest mit einem gealterten Projekt
    (`geteilt/kit-projekt-altern.py`, Schritt 5c bzw. 6c).
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

import conftest
from conftest import kit_pfad

KOSTEN_PY = kit_pfad("tools", "kosten.py")
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"
STUNDE = 3600


def _git(repo, *args, zeit=None):
    umgebung = dict(os.environ)
    if zeit is not None:
        stempel = f"@{int(zeit)} +0000"
        umgebung.update(GIT_AUTHOR_DATE=stempel, GIT_COMMITTER_DATE=stempel)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@l",
                    "-c", "user.name=T", *args], check=True,
                   capture_output=True, env=umgebung)


def _projekt(tmp_path, *kaskaden):
    """Ein Projekt mit Vorgeschichte: Kaskade N scharfgeschaltet zum Zeitpunkt
    t (Commit-Zeit der Plandatei), `.ralph-plan` auf der letzten."""
    projekt = tmp_path / "projekt"
    (projekt / "plans").mkdir(parents=True)
    _git(projekt, "init", "-q")
    for nummer, zeit in kaskaden:
        rel = f"plans/ralph-kaskade-{nummer}-produkt.md"
        (projekt / rel).write_text("# Plan\n", encoding="utf-8")
        _git(projekt, "add", "--", rel)
        _git(projekt, "commit", "-q", "-m", f"scharf {nummer}", zeit=zeit)
    (projekt / ".ralph-plan").write_text(
        f"plans/ralph-kaskade-{kaskaden[-1][0]}-produkt.md\n", encoding="utf-8")
    return projekt


def _kosten(projekt, *args):
    return subprocess.run(
        [sys.executable, str(KOSTEN_PY), *args], cwd=projekt,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))


# --- (a) Der Plan gehoert zum Projekt des Ledgers ---------------------------

def test_der_fensterriegel_nimmt_den_plan_aus_dem_projekt_des_ledgers(tmp_path):
    """Der Feldfall in klein: Kaskade 2 laeuft im Projekt, gebucht wird
    `--kaskade 1` mit einem frischen Log."""
    jetzt = time.time()
    projekt = _projekt(tmp_path, ("1", jetzt - 48 * STUNDE),
                       ("2", jetzt - 24 * STUNDE))
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "harry.json").write_text(json.dumps({"total_cost_usd": 1.0969}),
                                     encoding="utf-8")
    fremd = tmp_path / "fremd"
    fremd.mkdir()
    (fremd / "ledger").write_text(KOPF, encoding="utf-8")

    daneben = _kosten(projekt, "rollen-abschluss", "--kaskade", "1",
                      "--domaene", "produkt", "--logs", str(logs),
                      "--pfad", str(fremd / "ledger"))
    assert daneben.returncode == 0, (
        "Ein Ledger AUSSERHALB des Projekts wurde gegen dessen Plandateien "
        "gehalten — die Kaskade 2 des umgebenden Projekts hat die Buchung "
        f"blockiert (Kit-BL-307):\n{daneben.stderr}")

    # Gegenprobe: Liegt das Ledger IM Projekt, ist es dessen Kaskade 2, und
    # der Riegel aus BL-266 greift wie gebaut. `--trotzdem` nimmt nur den
    # Plan-Abgleich aus BL-220 heraus (der Closeout von 1 wird nachgeholt,
    # waehrend 2 laeuft) — der Fensterriegel hat seine eigene Uebersteuerung.
    (projekt / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    drin = _kosten(projekt, "rollen-abschluss", "--kaskade", "1",
                   "--domaene", "produkt", "--logs", str(logs), "--trotzdem")
    assert drin.returncode != 0 and "JUENGER" in drin.stderr, (
        "Mit dem Ledger im Projekt muss der BL-266-Riegel weiter greifen — "
        f"sonst haette dieser Fix ihn abgeschaltet.\n{drin.stdout}{drin.stderr}")


def test_die_ledgerpruefung_nimmt_den_plan_aus_dem_projekt_des_ledgers(tmp_path):
    """Dieselbe Regel fuer `ledger-pruefen`: Zeiger und Plandateien kommen aus
    dem Projekt des geprueften Ledgers (P1b, BL-280)."""
    t28 = time.time() - 20 * STUNDE
    projekt = _projekt(tmp_path, ("28", t28), ("29", t28 + 10 * STUNDE))
    (projekt / ".ralph-logs").mkdir()
    (projekt / ".team-logs").mkdir()
    log = projekt / ".ralph-logs" / "stufe-1.json"
    log.write_text(json.dumps({"total_cost_usd": 2.0}), encoding="utf-8")
    os.utime(log, (t28 + STUNDE,) * 2)
    fremd = tmp_path / "fremd"
    fremd.mkdir()
    (fremd / "ledger").write_text(KOPF, encoding="utf-8")
    log_args = ("--ralph-logs", str(projekt / ".ralph-logs"),
                "--team-logs", str(projekt / ".team-logs"))

    daneben = _kosten(projekt, "ledger-pruefen", "--pfad",
                      str(fremd / "ledger"), *log_args)
    assert "Kaskade 28" not in daneben.stdout, (
        "Ein Ledger AUSSERHALB des Projekts wurde gegen dessen Plandateien "
        f"gehalten (Kit-BL-307):\n{daneben.stdout}")

    (projekt / ".budget-ledger").write_text(KOPF, encoding="utf-8")
    drin = _kosten(projekt, "ledger-pruefen", *log_args)
    assert drin.returncode == 4 and "Kaskade 28" in drin.stdout, (
        "Mit dem Ledger im Projekt muss die Pruefung die ausgefallene "
        f"Kaskade 28 weiter melden (BL-280).\n{drin.stdout}")


# --- (b) Projektdateien sind keine Ersatzquelle -----------------------------

def test_quelle_ueberspringt_die_vorlage_einer_projektdatei_im_projekt(
        tmp_path, monkeypatch):
    """Im Projekt gibt es die Vorlage nicht, wohl aber die Projektdatei — und
    die ist KEIN Ersatz: sichtbar uebersprungen, mit Grund."""
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE.md\n", encoding="utf-8")
    monkeypatch.setattr(conftest, "REPO_ROOT", tmp_path)
    with pytest.raises(pytest.skip.Exception, match="Kit-BL-307"):
        conftest.quelle("bootstrap/CLAUDE.md.vorlage")
    with pytest.raises(pytest.skip.Exception, match="team.config.ps1"):
        conftest.quelle("pwsh/entry/team.config.ps1")
    # Eine fehlende Datei der INFRASTRUKTUR bleibt ein Befund.
    with pytest.raises(AssertionError):
        conftest.quelle("geteilt/prompts/rolle-x.md", "team/prompts/rolle-x.md")
    # Und im Kit wird die Vorlage gelesen.
    vorlage = tmp_path / "bootstrap" / "CLAUDE.md.vorlage"
    vorlage.parent.mkdir()
    vorlage.write_text("# Vorlage\n", encoding="utf-8")
    assert conftest.quelle("bootstrap/CLAUDE.md.vorlage") == vorlage


# Die Rueckfall-Schreibweisen, die bis BL-307 in 12 Dateien standen. Die
# Muster sind zusammengesetzt, damit diese Datei sich nicht selbst findet.
_V, _P = "CLAUDE.md" + ".vorlage", "CLAUDE.md"
RUECKFAELLE = (
    re.compile(r'"bootstrap/' + re.escape(_V) + r'",\s*"' + re.escape(_P) + '"'),
    re.compile(r'\("bootstrap",\s*"' + re.escape(_V) + r'"\),\s*\("'
               + re.escape(_P) + r'",?\)'),
    re.compile(r'REPO_ROOT / "' + re.escape(_P) + r'" if'),
    re.compile(r'"(?:bash|pwsh)/entry/team\.config\.(?:sh|ps1)",\s*'
               r'"team\.config\.(?:sh|ps1)"'),
)
# Ausnahmen mit Grund. test_bl15 liest die Projektdatei mit Absicht: Dort
# prueft es die FORM der Zeilen, die es gibt (BL-194 verdreht sie im
# Selbsttest); ob die Zeile DASTEHT, ueberspringt es im Projekt selbst.
AUSNAHMEN = {"test_bl15_reproducer_zeile_ankertauglich.py"}


def test_keine_testdatei_faellt_auf_die_projektdatei_zurueck():
    """Die Bauart (b) an der Quelle: Wer eine Regel der Vorlage pruefen will,
    nimmt `conftest.quelle` — ohne Projektdatei als zweiten Kandidaten."""
    funde, getroffen = [], set()
    for datei in sorted(Path(__file__).parent.glob("test_*.py")):
        text = datei.read_text(encoding="utf-8")
        for muster in RUECKFAELLE:
            for m in muster.finditer(text):
                if datei.name in AUSNAHMEN:
                    getroffen.add(datei.name)
                    continue
                zeile = text.count("\n", 0, m.start()) + 1
                funde.append(f"{datei.name}:{zeile} — {m.group(0)}")
    verwaist = sorted(AUSNAHMEN - getroffen)
    assert not verwaist, (
        f"Diese Ausnahmen zeigen ins Leere — Eintrag loeschen, sonst erlaubt "
        f"er lautlos den naechsten Rueckfall: {verwaist}")
    assert not funde, (
        "Diese Stellen fallen von der Vorlage auf die Projektdatei zurueck — "
        "gruen in jeder frischen Installation, rot in jedem Bestandsprojekt, "
        "dessen Datei aelter ist als die Regel (Kit-BL-307). "
        "`conftest.quelle(<vorlage>)` nehmen:\n  " + "\n  ".join(funde))


def test_die_alterung_des_selbsttests_traegt():
    """Das Werkzeug fuer die Konfiguration "Bestandsprojekt" prueft ohne
    Argument, ob seine Annahmen noch stimmen — ein Umbau von Plan-Praefix
    oder Bibliotheks-Default faellt hier auf, nicht erst nach einer Stunde."""
    werkzeug = conftest.REPO_ROOT / "geteilt" / "kit-projekt-altern.py"
    if not werkzeug.is_file():
        pytest.skip("Kit-Werkzeug — liegt nur im Kit")
    r = subprocess.run([sys.executable, str(werkzeug)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0 and "Kit-BL-307" in r.stdout, r.stdout + r.stderr


def test_die_alterung_greift(tmp_path):
    """Gegenprobe zum Werkzeug: Nach dem Lauf HAT das Projekt eine
    Vorgeschichte — sonst prueft der Selbsttest wieder eine frische
    Installation und bleibt gruen aus dem falschen Grund."""
    werkzeug = conftest.REPO_ROOT / "geteilt" / "kit-projekt-altern.py"
    if not werkzeug.is_file():
        pytest.skip("Kit-Werkzeug — liegt nur im Kit")
    projekt = tmp_path / "projekt"
    (projekt / "team").mkdir(parents=True)
    _git(projekt, "init", "-q")
    for name in ("lib.sh", "lib.psm1"):
        (projekt / "team" / name).write_bytes(kit_pfad(name).read_bytes())
    (projekt / "CLAUDE.md").write_text("# frisch\n", encoding="utf-8")
    (projekt / "team.config.sh").write_text(
        'TEAM_ROLE_BUDGET_USD="${TEAM_ROLE_BUDGET_USD:-20}"\n'
        'TEAM_SMOKE_TEST="${TEAM_SMOKE_TEST:-./smoke.sh}"\n', encoding="utf-8")
    r = subprocess.run([sys.executable, str(werkzeug), str(projekt)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
    sys.path.insert(0, str(KOSTEN_PY.parent))
    import kosten
    assert kosten.kaskade_beginn("30", str(projekt)) is not None, (
        "Keine Kaskade mit Commit-Zeit — der Kaskadenverlauf fehlt")
    assert "Bestandsprojekt" in (projekt / "CLAUDE.md").read_text(encoding="utf-8")
    cfg = (projekt / "team.config.sh").read_text(encoding="utf-8")
    assert "TEAM_ROLE_BUDGET_USD" not in cfg, "Rueckfall-Wert nicht entfernt"
    assert "TEAM_SMOKE_TEST" in cfg, (
        "Eine Antwort des Installers wurde entfernt — die hat jedes Projekt")

#!/usr/bin/env python3
"""BL-237, BL-242, BL-278, BL-194: die Werkzeuge der achten Welle, am
Verhalten geprueft.

BL-237 (`Feld B`) schreibzone.py
    Im Plan-Ordner lagen nach elf Kaskaden neun fremde Dateien, vier davon
    ausfuehrbar und nie gesweept. Genannt wird, was weder Team-Artefakt noch
    im Bestandsvermerk ist.

BL-242 (`Feld B`) protokolle.py
    Die Architekten-Sitzung war die einzige Rolle ohne Protokoll. `ablegen`
    holt die Protokolle ins Projekt — aber nie in einen versionierten Ordner.

BL-278 (`Feld B`) prozesse.py
    "Verwaiste pwsh-Prozesse" war viermal die Diagnose und nie wahr. Ein
    Kandidat braucht drei Merkmale, und abgeraeumt wird nichts.

BL-194 (Kit) kit-marken-verdrehen.py
    Die dritte Konfiguration des Selbsttests: Eine Verdrehung, die nichts
    trifft, ist ein Fehler — sonst prueft der Schritt nichts.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if Path(_tools).is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402
import prozesse  # noqa: E402
import schreibzone  # noqa: E402

PROTOKOLLE_PY = kit_pfad("tools", "protokolle.py")


# --- BL-237 -------------------------------------------------------------------

def _plan(tmp_path, dateien):
    for rel in dateien:
        p = tmp_path / "plans" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n", encoding="utf-8")
    return tmp_path


def test_team_artefakte_und_bestand_bleiben_ungenannt(tmp_path):
    wurzel = _plan(tmp_path, [
        "beutebuch.md", "backlog.md", "roadmap-skizzen.md",
        "team-kaskade-3-thema.md", "kaskade-3-abschluss.md",
        "ermittlungsakten/AX-1.md", "kit-meldungen/entwurf.md",
        "gestaltungsvertrag.md", "pruefen/regeln.py"])
    treffer = schreibzone.befunde(str(wurzel), "plans/",
                                  ["gestaltungsvertrag.md"], [])
    assert [t[0] for t in treffer] == ["plans/pruefen/regeln.py"], treffer
    assert treffer[0][1] is True and treffer[0][2] is False, (
        "Ein Skript in der Schreibzone ist ausfuehrbar und ausserhalb des "
        "Pruefumfangs — genau der hineingewachsene BL-52-Fall")


def test_ein_skript_im_pruefumfang_bekommt_keinen_zusatz(tmp_path):
    wurzel = _plan(tmp_path, ["pruefen/regeln.py"])
    treffer = schreibzone.befunde(str(wurzel), "plans", [], ["plans/pruefen"])
    assert treffer == [("plans/pruefen/regeln.py", True, True)], treffer


def test_eine_leere_schreibzone_schweigt(tmp_path):
    wurzel = _plan(tmp_path, ["beutebuch.md", "backlog.md"])
    assert schreibzone.befunde(str(wurzel), "plans", [], []) == []


# --- BL-242 -------------------------------------------------------------------

def _antwort(mid, minuten):
    zeit = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc) + timedelta(
        minutes=minuten)
    return json.dumps({"type": "assistant",
                       "timestamp": kosten.zeitpunkt_text(zeit),
                       "message": {"id": mid, "model": "claude-opus-5",
                                   "usage": {"input_tokens": 1_000_000,
                                             "output_tokens": 0}}})


def _ablage(tmp_path, gitignore=True):
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    subprocess.run(["git", "-C", str(projekt), "init", "-q"], check=True)
    if gitignore:
        (projekt / ".gitignore").write_text(".team-protokolle/\n",
                                            encoding="utf-8")
    heim = tmp_path / "heim"
    ordner = (heim / ".claude" / "projects"
              / kosten.projekt_ordnername(str(projekt.resolve())))
    ordner.mkdir(parents=True)
    (ordner / "s1.jsonl").write_text(_antwort("a", 0) + "\n", encoding="utf-8")
    unter = ordner / "s1" / "subagents" / "agent-1.jsonl"
    unter.parent.mkdir(parents=True)
    unter.write_text(_antwort("b", 1) + "\n", encoding="utf-8")
    return projekt, heim, ordner


def _ablegen(projekt, heim):
    umgebung = dict(os.environ, HOME=str(heim), USERPROFILE=str(heim))
    umgebung.pop("TEAM_PREISE", None)
    r = subprocess.run([sys.executable, str(PROTOKOLLE_PY), "ablegen"],
                       cwd=projekt, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=umgebung)
    return r.returncode, r.stdout + r.stderr


def test_ablegen_holt_sitzung_und_subagent_und_schreibt_den_index(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    rc, aus = _ablegen(projekt, heim)
    assert rc == 0, aus
    ziel = projekt / ".team-protokolle"
    assert (ziel / "s1.jsonl").is_file()
    assert (ziel / "s1" / "subagents" / "agent-1.jsonl").is_file()
    index = (ziel / "index.md").read_text(encoding="utf-8")
    assert "10.0000" in index and "Subagent" in index, index
    assert "Nicht versioniert" in index or "nicht versioniert" in index.lower()

    rc, aus = _ablegen(projekt, heim)               # idempotent
    assert rc == 0 and "0 neu, 0 aktualisiert" in aus, aus
    with open(ordner / "s1.jsonl", "a", encoding="utf-8") as fh:
        fh.write(_antwort("c", 2) + "\n")
    rc, aus = _ablegen(projekt, heim)
    assert "1 aktualisiert" in aus, aus
    assert "15.0000" in (ziel / "index.md").read_text(encoding="utf-8")


def test_ohne_gitignore_wird_nichts_abgelegt(tmp_path):
    """Die Sicherheitsauflage der Meldung: In einem Protokoll steht alles, was
    je in eine Sitzung eingefuegt wurde. Ein versionierter Ablageort ist ein
    Vorfall, keine Ordnungsfrage."""
    projekt, heim, _ = _ablage(tmp_path, gitignore=False)
    rc, aus = _ablegen(projekt, heim)
    assert rc == 1 and "Kit-BL-242" in aus, aus
    assert not (projekt / ".team-protokolle").exists()


def test_die_gitignore_vorlage_nimmt_den_ordner_heraus():
    vorlage = REPO_ROOT / "bootstrap" / "gitignore.fragment"
    if not vorlage.is_file():
        pytest.skip("Vorlage liegt nur im Kit")
    zeilen = vorlage.read_text(encoding="utf-8").splitlines()
    assert ".team-protokolle/" in zeilen, (
        "Ohne die Zeile in der Vorlage traegt --update sie nie in ein "
        "Bestandsprojekt ein — und protokolle.py legt dort nichts ab")


# --- BL-278 -------------------------------------------------------------------

WURZEL = os.path.abspath("C:/repo/projekt" if os.name == "nt" else "/repo/projekt")


def _p(pid, ppid, name, befehl="", start="2026-10-03T10:00:00+02:00"):
    return {"pid": pid, "ppid": ppid, "name": name, "pfad": "",
            "befehl": befehl, "start": start}


def test_ein_kandidat_braucht_alle_drei_merkmale():
    unter = f"pwsh -File {WURZEL}/ralph.ps1"
    tabelle = [
        _p(10, 999, "pwsh.exe", unter),                       # Kandidat
        _p(11, 999, "Code.exe", f"{WURZEL}/x"),               # GUI: keine Huelle
        _p(12, 20, "pwsh.exe", unter),                        # Eltern leben
        _p(13, 999, "pwsh.exe", "pwsh -File C:/fremd/x.ps1"),  # fremdes Repo
        _p(20, 4, "Code.exe", "", "2026-10-03T09:00:00+02:00"),
    ]
    treffer = prozesse.urteilen(tabelle, WURZEL)
    assert [e["pid"] for e, _ in treffer] == [10], treffer


def test_eine_wiederverwendete_eltern_pid_ist_kein_elternprozess():
    """Unter Windows bleibt die alte Eltern-PID stehen und kann einem
    JUENGEREN Prozess gehoeren — dann lebt der echte Elternprozess nicht."""
    tabelle = [_p(10, 30, "pwsh.exe", f"pwsh {WURZEL}/a.ps1",
                  "2026-10-03T10:00:00+02:00"),
               _p(30, 4, "notepad.exe", "", "2026-10-03T11:00:00+02:00")]
    assert [e["pid"] for e, _ in prozesse.urteilen(tabelle, WURZEL)] == [10]


def test_der_bericht_nennt_menge_merkmale_und_raeumt_nichts_ab(capsys):
    rc = prozesse.pruefen([_p(10, 999, "pwsh.exe", f"pwsh {WURZEL}/a.ps1")],
                          WURZEL, prozesse.HUELLEN)
    aus = capsys.readouterr().out
    assert rc == 3
    assert "Geprueft: 1 Prozesse" in aus and "Kit-BL-278" in aus
    assert "keine Beweise" in aus and "nach eigener Pruefung" in aus, aus
    quelle = Path(prozesse.__file__).read_text(encoding="utf-8")
    for verboten in ("os.kill", "taskkill", "signal."):
        assert verboten not in quelle, (
            f"prozesse.py enthaelt {verboten!r} — das Werkzeug raeumt nicht "
            f"ab, es nennt den Befehl (Kit-BL-278)")


def test_die_erhebung_findet_den_eigenen_prozess():
    try:
        tabelle = prozesse.erheben()
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        pytest.skip(f"keine Prozesstabelle auf diesem Wirt: {exc}")
    assert any(e.get("pid") == os.getpid() for e in tabelle), (
        "Die Erhebung kennt nicht einmal den eigenen Prozess")


# --- BL-194 -------------------------------------------------------------------

def test_eine_verdrehung_die_nichts_trifft_ist_ein_fehler(tmp_path):
    werkzeug = REPO_ROOT / "geteilt" / "kit-marken-verdrehen.py"
    if not werkzeug.is_file():
        pytest.skip("Kit-Werkzeug")
    (tmp_path / "plans").mkdir()
    for name in ("CLAUDE.md", "plans/beutebuch.md", "team.config.sh",
                 "team.config.ps1"):
        (tmp_path / name).write_text("nichts\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(werkzeug), str(tmp_path)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode == 1 and "Kit-BL-194" in r.stderr, r.stderr

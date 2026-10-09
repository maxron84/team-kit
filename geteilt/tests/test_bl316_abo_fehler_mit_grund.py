#!/usr/bin/env python3
"""BL-316: Jeder Fehler eines Abo-Aufrufs hiess „Timeout/Limit/429?" und lief in
den API-Fallback — auch eine abgelaufene Anmeldung und eine Ablehnung durch
die Schutzregeln des Modells.

WAS GEMELDET WURDE (`Feld B`, 2026-09-30, Nachtrag 2026-10-09)
    (1) Mitten in einer Vollautomatik lief die Abo-Anmeldung ab: `result` =
        *„Failed to authenticate: OAuth session expired and could not be
        refreshed"*. Der Fallback schloss die Stufe ueber die API ab, die
        naechsten beiden scheiterten im Abo nach einem Turn und liefen ganz
        ueber die API — rund 12,5 USD fuer ein Neu-Anmelden.
    (2) Marvs Sweep ueber Sicherheitscode: *„API Error: … safeguards flagged
        this message … Details: [cyber]"*. Der Fallback half (5,86 USD, zwei
        Funde) — aber die Zeile nannte Timeout oder Limit.

DIE ZUSICHERUNGEN
    - Abgelaufene Anmeldung: KEIN Fallback, mit oder ohne Schluessel, sondern
      der Pausen-Exit 42 — mit einer Zeile, die das Neu-Anmelden nennt.
    - Schutzregeln: der Fallback bleibt, aber benannt.
    - Jeder andere Fehler: die Zeile nennt den Grund aus `result`, nicht
      „Timeout/Limit/429?".
    - Die Regel steht in kosten.py (bash ruft sie) und in PowerShell (pwsh) —
      beide werden gegen DIESELBEN Faelle gehalten.

DIE CLI IST EIN STUB, DER SCHLUESSEL EIN WEGWERF
    Der Stub antwortet im Abo mit dem Fehler-JSON und — erkennbar am gesetzten
    `ANTHROPIC_API_KEY` — im Fallback mit einem Erfolg. HOME und APPDATA
    zeigen in den Testordner: Der echte Schluessel einer Maschine darf nie in
    einen Test geraten.
"""
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import Ausgabe, kit_pfad  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")
for _tools in (Path(__file__).resolve().parents[2] / "geteilt" / "tools",
               kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

ANMELDUNG = {"is_error": True, "num_turns": 71, "total_cost_usd": 2.5,
             "result": "Failed to authenticate: OAuth session expired and "
                       "could not be refreshed"}
SCHUTZREGELN = {"is_error": True, "num_turns": 7, "total_cost_usd": 0.47,
                "result": "API Error: Sonnet 5's safeguards flagged this "
                          "message. Our safeguards can sometimes flag "
                          "legitimate cybersecurity work. Apply to the Cyber "
                          "Verification Program to reduce these interruptions. "
                          "Details: `[cyber]`"}
SONSTIG = {"is_error": True, "num_turns": 3, "total_cost_usd": 0.1,
           "result": "Request timed out after 600s"}
ERFOLG = {"is_error": False, "subtype": "success", "num_turns": 5,
          "total_cost_usd": 1.0, "result": "fertig"}

FAELLE = [
    (ANMELDUNG, "anmeldung"),
    ({"is_error": True, "result": 'API Error: 401 {"type":"error","error":'
      '{"type":"authentication_error","message":"OAuth token has expired."}}'},
     "anmeldung"),
    ({"is_error": True, "result": "", "api_error_status": 401}, "anmeldung"),
    ({"is_error": True, "result": "Invalid API key · Please run /login"},
     "anmeldung"),
    (SCHUTZREGELN, "schutzregeln cyber"),
    ({"is_error": True, "result": "API Error: Claude Code is unable to respond "
      "to this request, which appears to violate our Usage Policy."},
     "schutzregeln"),
    # Gegenrichtungen: kein Fehler, oder die Meldung steht nur ZITIERT im Text.
    ({"is_error": False, "result": "Failed to authenticate: OAuth session "
      "expired"}, ""),
    ({"is_error": True, "result": "Beim Lesen fiel mir auf: Failed to "
      "authenticate wird im Code abgefangen."}, ""),
    ({"is_error": True, "result": "You've hit your session limit · resets 3pm"},
     ""),
    (SONSTIG, ""),
]


# --- Die Regel, an allen drei Stellen ---------------------------------------

@pytest.mark.parametrize("daten,grund", FAELLE)
def test_die_regel_in_kosten_py(daten, grund):
    assert kosten.abo_fehlergrund(daten) == grund


@pytest.mark.parametrize("daten,grund", FAELLE)
def test_die_regel_in_beiden_bibliotheken(tmp_path, schale, daten, grund):
    """Dieselben Faelle in bash (ruft kosten.py) und pwsh (eigene Fassung) —
    zwei Fassungen einer Regel driften sonst auseinander (BL-154)."""
    repo = _repo(tmp_path, schale)
    log = repo / "abo.json"
    log.write_text(json.dumps(daten), encoding="utf-8")
    r = schale.lauf([Ausgabe("team_abo_fehlergrund", str(log))], cwd=repo,
                    lib=repo / "team" / schale.lib_name)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == grund, (r.stdout, r.stderr)


def test_ein_unlesbares_log_hat_keinen_grund(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    (repo / "kaputt.json").write_text("{abgeschnitten", encoding="utf-8")
    r = schale.lauf([Ausgabe("team_abo_fehlergrund", str(repo / "kaputt.json"))],
                    cwd=repo, lib=repo / "team" / schale.lib_name)
    assert r.stdout.strip() == ""


# --- team_claude, am lebenden Objekt -----------------------------------------

def _repo(tmp_path, schale):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    schale.lib_kopieren(repo)
    shutil.copy(KOSTEN_PY, repo / "team" / "tools" / "kosten.py")
    return repo


def _stub(ordner, schale, abo, api):
    """Antwortet im Abo mit `abo`, im Fallback (Schluessel gesetzt) mit `api`
    und zaehlt seine Aufrufe."""
    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / "abo.json").write_text(json.dumps(abo), encoding="utf-8")
    (ordner / "api.json").write_text(json.dumps(api), encoding="utf-8")
    if not schale.ist_bash and os.name == "nt":
        stub = ordner / "claude.cmd"
        stub.write_text(
            "@echo off\r\n"
            "echo x>>\"%~dp0aufrufe\"\r\n"
            "if defined ANTHROPIC_API_KEY (type \"%~dp0api.json\") else "
            "(type \"%~dp0abo.json\")\r\n", encoding="utf-8")
    else:
        stub = ordner / "claude"
        stub.write_text(
            "#!/bin/sh\n"
            "d=\"$(dirname \"$0\")\"\n"
            "echo x >> \"$d/aufrufe\"\n"
            "if [ -n \"$ANTHROPIC_API_KEY\" ]; then cat \"$d/api.json\"; "
            "else cat \"$d/abo.json\"; fi\n", encoding="utf-8", newline="\n")
        stub.chmod(0o755)
    return stub


class _ClaudeUndGrund:
    """team_claude rufen, Exit-Code merken, dann team_pause_grund melden."""

    def __init__(self, out):
        self.out = str(out)

    def bash(self):
        return (f"team_claude probe sonnet '{self.out}' prompt; _rc=$?\n"
                "echo \"PAUSE=[$(team_pause_grund)]\"\n_team_rc=$_rc\n")

    def pwsh(self):
        return (f"$rc = [int](team_claude probe sonnet '{self.out}' prompt)\n"
                "Write-Output \"PAUSE=[$(team_pause_grund)]\"\n"
                "$script:TeamRc = $rc\n")


def _lauf(tmp_path, schale, abo, api=ERFOLG, schluessel=True):
    repo = _repo(tmp_path, schale)
    stub = _stub(tmp_path / "cli", schale, abo, api)
    heim = tmp_path / "heim"
    appdata = tmp_path / "appdata"
    for ablage in (heim / ".config" / "claude-team", appdata / "claude-team"):
        ablage.mkdir(parents=True)
        if schluessel:
            (ablage / "api-key").write_text("sk-test-nur-fuer-den-stub\n",
                                            encoding="utf-8")
    out = repo / ".team-logs" / "probe-1.json"
    out.parent.mkdir()
    r = schale.lauf([_ClaudeUndGrund(out)], cwd=repo,
                    lib=repo / "team" / schale.lib_name,
                    env={"TEAM_CLAUDE_BIN": str(stub), "HOME": str(heim),
                         "USERPROFILE": str(heim), "APPDATA": str(appdata),
                         "AUTH_MODE": "abo", "TEAM_AUTH_USER": "abo",
                         "TEAM_429_MAX_WARTEN": "0",
                         "TEAM_429_MAX_RETRIES": "0"})
    aufrufe = tmp_path / "cli" / "aufrufe"
    anzahl = len(aufrufe.read_text().split()) if aufrufe.is_file() else 0
    fallback = out.parent / "probe-1-api-fallback.json"
    return r, anzahl, fallback


@pytest.mark.parametrize("schluessel", [True, False])
def test_abgelaufene_anmeldung_haelt_an_statt_ueber_die_api(tmp_path, schale,
                                                             schluessel):
    """Der Feldfall. Gegen den alten Stand gemessen: Mit Schluessel lief der
    Fallback (zweiter CLI-Aufruf, Exit 0) — und jede weitere Stufe danach."""
    r, aufrufe, fallback = _lauf(tmp_path, schale, ANMELDUNG,
                                 schluessel=schluessel)
    aus = r.stdout + r.stderr
    assert r.returncode == 42, (
        f"Eine abgelaufene Anmeldung muss den Lauf anhalten (Exit 42), "
        f"Exit war {r.returncode}.\n{aus}")
    assert aufrufe == 1 and not fallback.exists(), (
        f"Es lief ein API-Fallback ({aufrufe} CLI-Aufrufe) — der Rest des "
        f"Laufs ginge so ueber die API.\n{aus}")
    assert "Kit-BL-316" in aus and "/login" in aus, aus
    assert "Timeout/Limit/429?" not in aus
    assert "PAUSE=[Abo-Anmeldung abgelaufen" in r.stdout, (
        "team_pause_grund nennt den Grund nicht — die Rolle meldete dann "
        f"wieder 'Session-Limit'.\n{r.stdout}")


def test_schutzregeln_behalten_den_fallback_aber_benannt(tmp_path, schale):
    """Der Nachtrag: Der Fallback hat dort geholfen und bleibt — die Zeile
    nennt jetzt den Grund statt Timeout oder Limit."""
    r, aufrufe, fallback = _lauf(tmp_path, schale, SCHUTZREGELN)
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    assert aufrufe == 2 and fallback.exists(), aus
    assert "Schutzregeln" in aus and "(cyber)" in aus, aus
    assert "Timeout/Limit/429?" not in aus


def test_jeder_andere_fehler_nennt_seinen_grund(tmp_path, schale):
    """Mindestens die Meldung korrigieren (Vorschlag der Meldung): Der Grund
    aus `result` steht in der Zeile, die der Mensch liest."""
    r, aufrufe, fallback = _lauf(tmp_path, schale, SONSTIG)
    aus = r.stdout + r.stderr
    assert r.returncode == 0 and aufrufe == 2 and fallback.exists(), aus
    assert "Request timed out after 600s" in aus, aus
    assert "Timeout/Limit/429?" not in aus


def test_ein_limit_heisst_weiter_session_limit(tmp_path, schale):
    """Gegenrichtung fuer team_pause_grund: Der 429-Pfad nennt weiter das
    Session-Limit samt Reset."""
    limit = {"is_error": True, "num_turns": 0, "total_cost_usd": 0,
             "result": "You've hit your session limit · resets 3pm"}
    r, _aufrufe, _fallback = _lauf(tmp_path, schale, limit, api=limit,
                                   schluessel=False)
    assert r.returncode == 42, r.stdout + r.stderr
    assert "PAUSE=[Session-Limit (Reset:" in r.stdout, r.stdout


# --- Der Abschlussbericht ----------------------------------------------------

def test_der_bericht_zaehlt_fallbacks_mit_grund_und_betrag(tmp_path):
    """Die Kostenachse verrutschte still: Die Zeile stand danach unter `api`,
    ohne Grund."""
    logs = tmp_path / ".team-logs"
    logs.mkdir()
    (logs / "marv-1.json").write_text(json.dumps(SCHUTZREGELN), encoding="utf-8")
    (logs / "marv-1-api-fallback.json").write_text(
        json.dumps(dict(ERFOLG, total_cost_usd=5.86)), encoding="utf-8")
    (logs / "harry-1.json").write_text(json.dumps(ERFOLG), encoding="utf-8")
    zeilen = kosten.fallback_bericht([str(logs)])
    assert len(zeilen) == 1, zeilen
    assert "marv-1.json" in zeilen[0] and "Schutzregeln" in zeilen[0]
    assert "(cyber)" in zeilen[0] and "5.8600 USD" in zeilen[0], zeilen


def test_ohne_fallback_bleibt_der_bericht_leer(tmp_path):
    logs = tmp_path / ".team-logs"
    logs.mkdir()
    (logs / "harry-1.json").write_text(json.dumps(ERFOLG), encoding="utf-8")
    assert kosten.fallback_bericht([str(logs)]) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

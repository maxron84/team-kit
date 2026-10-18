#!/usr/bin/env python3
"""BL-326: Ein abgebrochener Rollenaufruf hinterliess seine halbe Arbeit im
Arbeitsbaum und kein Kostenlog — und der Wiederanlauf baute ungeprueft darauf
weiter.

WAS IM FELD PASSIERT IST (`Feld F`, 2026-10-10, pwsh/win32)
    Eine Vollautomatik wurde mitten in einer Ralph-Stufe beendet; ihr Log
    endet nach „Auth-Modus: abo". Dieselbe Startzeile am Morgen nahm die
    Stufe wieder auf, und der neue Ralph uebernahm zwei Dateien, die der
    abgebrochene schon geaendert hatte, und committete sie mit. Richtig war
    das nur, weil der erste Aufruf zufaellig richtig angefangen hatte. Und
    das Kostenlog fehlte: Die pwsh-Bahn schrieb es erst nach dem Ende der
    CLI, die bash-Bahn legte es durch die Umlenkung beim Start leer an. Im
    Ledger fehlten 0,3661 USD, kein Pruefer zeigte die Luecke.

DIE ZUSICHERUNGEN
    - Vor JEDEM CLI-Aufruf (auch vor dem API-Fallback) steht ein Stub im Log:
      `team_versuch: "abgebrochen"`, Rolle, Start, Sitzungskennung; dieselbe
      Kennung geht als `--session-id` an die CLI. Ein abgebrochener Aufruf
      hinterlaesst genau diesen Stub.
    - `kosten.py` zaehlt ihn wie den Ersatzzettel aus BL-46: Kosten
      UNBEKANNT, nie 0.0, und der Hinweis nennt Kennung und Messweg.
    - Wiederanlauf: Stub und schmutziger Baum halten mit Exit 42 an, ein
      sauberer Baum laeuft weiter. Ein Stub haelt hoechstens einmal an.

DIE ATTRAPPE DER CLI SCHLAEFT
    Abgebrochen wird wie im Feld: Die Attrappe meldet ihren Start und
    schlaeft, dann wird die ganze Prozessgruppe abgeschossen — kein Trap,
    kein Aufraeumen, wie bei einem geschlossenen Fenster.
"""
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (BASH, RufCode, basis_umgebung, kit_pfad,  # noqa: E402
                      nur_code, verlange_bash, verlange_pwsh)

REPO_ROOT = Path(__file__).resolve().parents[2]
KOSTEN = kit_pfad("tools", "kosten.py")
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

SITZUNG = "0f8fad5b-d9cb-469f-a165-70867728950e"
ABO_FEHLER = {"is_error": True, "num_turns": 3, "total_cost_usd": 0.1,
              "result": "Request timed out after 600s"}
ERFOLG = {"is_error": False, "subtype": "success", "num_turns": 2,
          "total_cost_usd": 0.5, "result": "fertig"}


def _stub_datei(ordner, name, rolle="ralph", sitzung=SITZUNG,
                start="2026-10-10T21:47:12", **mehr):
    """Ein Stub, wie ihn der Aufruf vorab schreibt."""
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / name
    daten = {"is_error": True, "result": "", "total_cost_usd": None,
             "team_versuch": "abgebrochen", "team_rolle": rolle,
             "team_start": start, "session_id": sitzung}
    daten.update(mehr)
    pfad.write_text(json.dumps(daten), encoding="utf-8")
    return pfad


def _echtes_log(ordner, name, usd):
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / name
    pfad.write_text(json.dumps({"is_error": False, "subtype": "success",
                                "num_turns": 4, "total_cost_usd": usd}),
                    encoding="utf-8")
    return pfad


def _kosten(*args, cwd):
    return subprocess.run([sys.executable, str(KOSTEN), *args], cwd=str(cwd),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


# --- kosten.py: Kosten UNBEKANNT, nie 0.0 ------------------------------------

def test_die_summe_nennt_den_stub_mit_kennung_und_messweg(tmp_path):
    logs = tmp_path / ".ralph-logs"
    stub = _stub_datei(logs, "stufe-7-20261010-214712.json")
    _echtes_log(logs, "stufe-6-20261010-200000.json", 1.0)
    r = _kosten("summe", str(logs), cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "1.0000", (
        "die Zahl auf stdout bleibt, was sie war — Aufrufer parsen sie")
    for erwartet in ("UNBEKANNT", SITZUNG, "sitzung-messen", stub.name):
        assert erwartet in r.stderr, (
            f"Der Hinweis auf den abgebrochenen Aufruf nennt '{erwartet}' "
            f"nicht — ohne ihn ist die Luecke wieder still (BL-326):\n"
            f"{r.stderr}")


def test_ein_stub_allein_ist_keine_stille_null(tmp_path):
    """Der Feldfall in der Summe: Nur der abgebrochene Aufruf liegt da.
    0.0000 ohne Hinweis ist von „hat nichts gekostet" nicht zu
    unterscheiden (BL-46)."""
    logs = tmp_path / ".team-logs"
    _stub_datei(logs, "frank-HM-3-v1-20261010-214712.json", rolle="frank")
    r = _kosten("summe", str(logs), cwd=tmp_path)
    assert r.stdout.strip() == "0.0000", r.stdout
    assert "UNBEKANNT" in r.stderr, (
        f"Ein Stub allein summiert still zu 0.0000:\n{r.stderr}")


def test_die_marke_entscheidet_nicht_die_zahl(tmp_path):
    """`abgebrochen` heisst Kosten unbekannt — auch dann, wenn im Stub
    versehentlich eine Zahl stuende. Gezaehlt wird er nie, schon gar nicht
    als 0.0."""
    logs = tmp_path / ".ralph-logs"
    ohne = _stub_datei(logs, "stufe-1-a.json")
    mit_null = _stub_datei(logs, "stufe-1-b.json", total_cost_usd=0.0)
    assert kosten._datei_kosten(str(ohne)) == (0.0, False)
    assert kosten._datei_kosten(str(mit_null)) == (0.0, False), (
        "Ein Stub mit 0.0 zaehlt als belegte Null — genau die stille Null, "
        "die BL-46 abgestellt hat.")


def test_der_abschluss_archiviert_den_stub_und_nennt_die_sitzung(tmp_path):
    """Der Stub ist kein Kostenbeleg und kann nicht doppelt zaehlen — er
    wird wie der Ersatzzettel mitarchiviert, und der Abschluss sagt, mit
    welcher Kennung sich die Luecke nachmessen laesst."""
    logs = tmp_path / ".ralph-logs"
    stub = _stub_datei(logs, "stufe-7-20261010-214712.json")
    _echtes_log(logs, "stufe-6-20261010-200000.json", 1.5)
    (tmp_path / "plans").mkdir()
    ledger = tmp_path / ".budget-ledger"
    ledger.write_text("", encoding="utf-8")
    r = _kosten("ralph-abschluss", "--kaskade", "29", "--domaene", "produkt",
                "--archivieren", "--pfad", str(ledger), cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "konnte nicht als JSON gelesen werden" not in r.stderr, (
        f"Der Stub ist lesbar — 'nicht lesbar' ist die falsche Diagnose:\n"
        f"{r.stderr}")
    assert not stub.exists() and (logs / "archiv" / stub.name).is_file(), (
        "der Stub muss mit archiviert werden, sonst bleibt er als "
        "Dauer-Verdachtsfall liegen (BL-46)")
    assert SITZUNG in r.stderr and "sitzung-messen" in r.stderr, r.stderr


def test_ledger_pruefen_nennt_den_stub_nicht_unlesbar(tmp_path):
    logs = tmp_path / ".ralph-logs"
    _stub_datei(logs, "stufe-7-20261010-214712.json")
    ledger = tmp_path / ".budget-ledger"
    ledger.write_text(
        "2026-10-10 | 29 | 12.0000 | abo | produkt | ralph | Bau: K29\n"
        "2026-10-10 | 29 | 6.0000 | abo | produkt | architekt | Plan: K29\n",
        encoding="utf-8")
    r = _kosten("ledger-pruefen", "--pfad", str(ledger), "--kaskade", "29",
                "--ralph-logs", str(logs), "--team-logs",
                str(tmp_path / ".team-logs"), cwd=tmp_path)
    assert r.returncode == 0, r.stdout
    assert "KEIN Kostenbeleg" in r.stdout, r.stdout
    assert "1 nicht lesbar" not in r.stdout and "abgebrochen" in r.stdout, (
        f"Ein abgebrochener Aufruf ist lesbar — der Waechter muss ihn als "
        f"solchen nennen:\n{r.stdout}")


# --- Der CLI-Aufruf: Stub vorher, Kennung an die CLI --------------------------

def _q_bash(wert):
    return "'" + str(wert).replace("'", "'\\''") + "'"


def _q_pwsh(wert):
    return "'" + str(wert).replace("'", "''") + "'"


def _attrappe(ordner, schale, abo=None, api=None):
    """Eine CLI, die ihre Argumente festhaelt und dann je Modus antwortet
    (`abo.json`/`api.json` liegt daneben) oder ihren Start meldet und
    schlaeft. Den Modus erkennt sie wie test_bl316 am Schluessel."""
    ordner.mkdir(parents=True, exist_ok=True)
    for modus, antwort in (("abo", abo), ("api", api)):
        if antwort is not None:
            (ordner / f"{modus}.json").write_text(json.dumps(antwort),
                                                  encoding="utf-8")
    if schale.ist_bash:
        stub = ordner / "claude-attrappe"
        stub.write_text(
            "#!/bin/sh\n"
            "d=\"$(dirname \"$0\")\"\n"
            "echo \"$*\" >> \"$d/aufrufe\"\n"
            "if [ -n \"$ANTHROPIC_API_KEY\" ]; then modus=api; else modus=abo; fi\n"
            "if [ -f \"$d/$modus.json\" ]; then cat \"$d/$modus.json\"; exit 0; fi\n"
            ": > \"$d/gestartet-$modus\"\n"
            "sleep 60\n", encoding="utf-8", newline="\n")
        stub.chmod(0o755)
        return stub.as_posix()
    stub = ordner / "claude-attrappe.ps1"
    stub.write_text(
        "$d = $PSScriptRoot\n"
        "Add-Content -LiteralPath (Join-Path $d 'aufrufe') -Value ($args -join ' ') -Encoding utf8\n"
        "$modus = if ($env:ANTHROPIC_API_KEY) { 'api' } else { 'abo' }\n"
        "$antwort = Join-Path $d \"$modus.json\"\n"
        "if (Test-Path -LiteralPath $antwort) { Get-Content -Raw -LiteralPath $antwort; exit 0 }\n"
        "New-Item -ItemType File -Force -Path (Join-Path $d \"gestartet-$modus\") | Out-Null\n"
        "Start-Sleep -Seconds 60\n"
        "exit 0\n", encoding="utf-8-sig", newline="\n")
    return str(stub)


def _aufrufe(ordner):
    datei = ordner / "aufrufe"
    if not datei.is_file():
        return []
    return [z for z in datei.read_text(encoding="utf-8-sig").splitlines() if z]


def _kennung(aufruf):
    treffer = re.search(r"--session-id (\S+)", aufruf)
    return treffer.group(1) if treffer else None


def _ist_uuid(text):
    try:
        return str(uuid.UUID(str(text))) == str(text).lower()
    except ValueError:
        return False


def _repo(tmp_path, schale):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    schale.lib_kopieren(repo)
    shutil.copy(KOSTEN, repo / "team" / "tools" / "kosten.py")
    (repo / ".team-logs").mkdir()
    return repo


def _umgebung(tmp_path, cli, schluessel=False):
    heim = tmp_path / "heim"
    appdata = tmp_path / "appdata"
    for ablage in (heim / ".config" / "claude-team", appdata / "claude-team"):
        ablage.mkdir(parents=True, exist_ok=True)
        if schluessel:
            (ablage / "api-key").write_text("sk-test-nur-fuer-die-attrappe\n",
                                            encoding="utf-8")
    return basis_umgebung(TEAM_CLAUDE_BIN=cli, HOME=str(heim),
                          USERPROFILE=str(heim), APPDATA=str(appdata),
                          AUTH_MODE="abo", TEAM_429_MAX_WARTEN="0",
                          TEAM_429_MAX_RETRIES="0")


def _team_claude_befehl(schale, repo, out):
    lib = repo / "team" / schale.lib_name
    if schale.ist_bash:
        return [BASH, "-c", f"source {_q_bash(lib.as_posix())}\n"
                            f"team_claude probe sonnet {_q_bash(out)} prompt\n"]
    return ["pwsh", "-NoProfile", "-NonInteractive", "-Command",
            f"Import-Module {_q_pwsh(lib)} -Force -DisableNameChecking\n"
            f"$rc = [int](team_claude probe sonnet {_q_pwsh(out)} prompt)\n"
            "exit $rc\n"]


def _abschiessen(proc):
    """Die ganze Prozessgruppe, ohne Vorwarnung — wie ein geschlossenes
    Fenster. Kein Trap laeuft, kein Abschlussschritt."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGKILL)
    proc.communicate(timeout=30)


def _bis_gestartet(marke, proc, frist=90):
    ende = time.time() + frist
    while time.time() < ende:
        if marke.exists():
            return
        if proc.poll() is not None:
            aus, fehler = proc.communicate()
            pytest.fail(f"Der Aufruf endete, bevor die Attrappe startete "
                        f"(Exit {proc.returncode}):\n{aus}\n{fehler}")
        time.sleep(0.1)
    _abschiessen(proc)
    pytest.fail(f"Die Attrappe hat ihren Start nicht gemeldet: {marke}")


def _starte(schale, repo, out, umgebung):
    zusatz = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
              if os.name == "nt" else {"start_new_session": True})
    return subprocess.Popen(_team_claude_befehl(schale, repo, out), cwd=repo,
                            env=umgebung, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            encoding="utf-8", errors="replace",
                            stdin=subprocess.DEVNULL, **zusatz)


def test_ein_abgebrochener_aufruf_hinterlaesst_seinen_stub(tmp_path, schale):
    """Der Feldfall: Der Lauf endet, waehrend die CLI arbeitet. Danach liegt
    im Log der Stub — mit der Kennung, die die CLI bekommen hat — und
    `kosten.py` nennt ihn als Luecke. Vorher: bash ein leeres Log, pwsh gar
    keins."""
    repo = _repo(tmp_path, schale)
    cli_ordner = tmp_path / "cli"
    cli = _attrappe(cli_ordner, schale)
    out = repo / ".team-logs" / "probe-1.json"
    proc = _starte(schale, repo, out, _umgebung(tmp_path, cli))
    _bis_gestartet(cli_ordner / "gestartet-abo", proc)
    _abschiessen(proc)

    assert out.is_file() and out.stat().st_size > 0, (
        f"{schale.name}: Nach dem Abbruch gibt es kein Log des Aufrufs — "
        f"seine Kosten fallen aus jeder Summe (BL-326).")
    stub = json.loads(out.read_text(encoding="utf-8"))
    assert stub.get("team_versuch") == "abgebrochen", stub
    assert stub.get("team_rolle") == "probe", stub
    assert stub.get("team_start"), stub
    assert stub.get("total_cost_usd") is None and stub.get("is_error") is True
    sitzung = stub.get("session_id")
    assert _ist_uuid(sitzung), f"keine Sitzungskennung im Stub: {stub}"
    aufrufe = _aufrufe(cli_ordner)
    assert len(aufrufe) == 1 and _kennung(aufrufe[0]) == sitzung, (
        f"Die CLI hat nicht die Kennung des Stubs bekommen:\n{aufrufe}\n{stub}")
    assert sorted(p.name for p in out.parent.glob("*.json")) == [out.name], (
        "Die Nebendatei der CLI endet auf .json — kosten.py liest sie dann "
        "als eigenes Kostenlog.")

    r = _kosten("summe", str(out.parent), cwd=repo)
    assert "UNBEKANNT" in r.stderr and sitzung in r.stderr, r.stderr


def test_der_abschluss_ersetzt_den_stub_durch_das_ergebnis(tmp_path, schale):
    """Der Normalfall darf sich nicht aendern: Am Ende steht das Ergebnis
    der CLI im Log, kein Stub, keine Nebendatei — und die CLI hat ihre
    Kennung bekommen."""
    repo = _repo(tmp_path, schale)
    cli_ordner = tmp_path / "cli"
    cli = _attrappe(cli_ordner, schale, abo=ERFOLG)
    out = repo / ".team-logs" / "probe-1.json"
    r = schale.lauf([RufCode("team_claude", "probe", "sonnet", str(out),
                             "prompt")],
                    cwd=repo, lib=repo / "team" / schale.lib_name,
                    env=_umgebung(tmp_path, cli))
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(out.read_text(encoding="utf-8")) == ERFOLG
    rest = sorted(p.name for p in out.parent.iterdir())
    assert rest == [out.name], f"Reste neben dem Log: {rest}"
    aufrufe = _aufrufe(cli_ordner)
    assert len(aufrufe) == 1 and _ist_uuid(_kennung(aufrufe[0])), (
        f"{schale.name}: Die CLI bekommt keine --session-id — das Transkript "
        f"eines abgebrochenen Aufrufs ist dann nicht zu finden:\n{aufrufe}")


def test_auch_der_api_fallback_steht_vorher_als_stub_im_log(tmp_path, schale):
    """Stub vor JEDEM Aufruf: Der Abo-Versuch scheitert, der API-Fallback
    laeuft — und wird abgebrochen. Sein Log ist der Stub, mit eigener
    Kennung; das Log des Abo-Versuchs traegt dessen Ergebnis."""
    repo = _repo(tmp_path, schale)
    cli_ordner = tmp_path / "cli"
    cli = _attrappe(cli_ordner, schale, abo=ABO_FEHLER)
    out = repo / ".team-logs" / "probe-1.json"
    proc = _starte(schale, repo, out, _umgebung(tmp_path, cli, schluessel=True))
    _bis_gestartet(cli_ordner / "gestartet-api", proc)
    _abschiessen(proc)

    assert json.loads(out.read_text(encoding="utf-8")) == ABO_FEHLER, (
        "Das Log des Abo-Versuchs muss sein Ergebnis tragen, nicht den Stub")
    fallback = out.parent / "probe-1-api-fallback.json"
    assert fallback.is_file() and fallback.stat().st_size > 0, (
        f"{schale.name}: Der abgebrochene API-Fallback hat kein Log "
        f"hinterlassen (BL-326).")
    stub = json.loads(fallback.read_text(encoding="utf-8"))
    assert stub.get("team_versuch") == "abgebrochen", stub
    aufrufe = _aufrufe(cli_ordner)
    assert len(aufrufe) == 2, aufrufe
    erste, zweite = (_kennung(a) for a in aufrufe)
    assert _ist_uuid(erste) and _ist_uuid(zweite) and erste != zweite, (
        f"Jeder Versuch braucht seine eigene Kennung: {aufrufe}")
    assert stub.get("session_id") == zweite, (stub, aufrufe)


@pytest.mark.parametrize("datei,aufruf", [("lib.sh", '"$TEAM_CLAUDE_BIN" -p'),
                                          ("lib.psm1", "& $Claude -p")])
def test_die_cli_wird_an_genau_einer_stelle_gerufen(datei, aufruf):
    """Der Riegel gegen den Rueckbau, auch fuer die pwsh-Haelfte, die hier
    nicht faehrt: EIN Aufruf je Bahn, und er reicht die Kennung weiter.
    Vorher stand der Aufruf in bash viermal da (Abo, Fallback, zweimal 429)."""
    pfad = kit_pfad(datei)
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    code = nur_code(pfad.read_text(encoding="utf-8-sig")).splitlines()
    stellen = [z for z in code if aufruf in z]
    assert len(stellen) == 1, (
        f"{datei}: die CLI wird an {len(stellen)} Stellen gerufen — jede "
        f"weitere Stelle schreibt keinen Stub (BL-326):\n" + "\n".join(stellen))
    assert "--session-id" in stellen[0], stellen[0]


# --- Der Wiederanlauf ------------------------------------------------------------

def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True)


def _projekt(tmp_path, schale):
    """Ein sauberer Arbeitsbaum mit Bibliothek und einer getrackten Datei."""
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    schale.lib_kopieren(repo)
    (repo / "src" / "daten.txt").write_text("alt\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-qm", "start"]):
        _git(repo, *befehl)
    return repo


def _wiederanlauf(repo, schale):
    return schale.lauf([RufCode("team_wiederanlauf_pruefen")], cwd=repo,
                       lib=repo / "team" / schale.lib_name)


def test_stub_und_schmutziger_baum_halten_mit_42(tmp_path, schale):
    """Der Feldfall beim Wiederanlauf: Die halbe Arbeit des abgebrochenen
    Aufrufs liegt im Baum. Der Lauf nennt Rolle, Sitzung und Pfad und haelt
    an — der Mensch sichtet, statt dass die naechste Rolle sie uebernimmt."""
    repo = _projekt(tmp_path, schale)
    _stub_datei(repo / ".ralph-logs", "stufe-7-20261010-214712.json")
    (repo / "src" / "daten.txt").write_text("halb\n", encoding="utf-8")
    r = _wiederanlauf(repo, schale)
    aus = r.stdout + r.stderr
    assert r.returncode == 42, (
        f"{schale.name}: Stub und schmutziger Baum muessen anhalten "
        f"(Exit {r.returncode}):\n{aus}")
    for erwartet in ("ralph", SITZUNG, "src/daten.txt", "Kit-BL-326"):
        assert erwartet in aus, f"'{erwartet}' fehlt in der Meldung:\n{aus}"


def test_stub_und_sauberer_baum_laufen_weiter(tmp_path, schale):
    """Nichts liegengeblieben: weiter. Der Stub bleibt als Kostenluecke
    stehen, und das wird gesagt."""
    repo = _projekt(tmp_path, schale)
    stub = _stub_datei(repo / ".team-logs", "frank-HM-3-v1-20261010-214712.json",
                       rolle="frank")
    r = _wiederanlauf(repo, schale)
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    assert "Kit-BL-326" in aus and "UNBEKANNT" in aus and "frank" in aus, (
        f"{schale.name}: Der saubere Wiederanlauf nennt die Kostenluecke "
        f"nicht:\n{aus}")
    daten = json.loads(stub.read_text(encoding="utf-8"))
    assert daten.get("team_versuch") == "abgebrochen", (
        "der Stub bleibt — er ist der einzige Beleg der Luecke")


def test_ein_stub_haelt_hoechstens_einmal_an(tmp_path, schale):
    """Der Mensch hat gesichtet und startet dieselbe Zeile neu — der alte
    Stub darf ihn kein zweites Mal anhalten. Der Vermerk steht im Stub, und
    dessen Zeitstempel bleibt der des Aufrufs (die Fenster der
    Kostenwerkzeuge haengen daran)."""
    repo = _projekt(tmp_path, schale)
    stub = _stub_datei(repo / ".team-logs", "axel-HM-9-20261010-214712.json",
                       rolle="axel")
    damals = time.time() - 7200
    os.utime(stub, (damals, damals))
    (repo / "src" / "neu.txt").write_text("halb\n", encoding="utf-8")
    erst = _wiederanlauf(repo, schale)
    assert erst.returncode == 42, erst.stdout + erst.stderr
    zweit = _wiederanlauf(repo, schale)
    assert zweit.returncode == 0, (
        f"{schale.name}: Derselbe Stub haelt ein zweites Mal an:\n"
        f"{zweit.stdout}{zweit.stderr}")
    daten = json.loads(stub.read_text(encoding="utf-8"))
    assert daten.get("team_versuch") == "abgebrochen", daten
    assert daten.get("team_gesichtet"), f"kein Vermerk im Stub: {daten}"
    assert abs(stub.stat().st_mtime - damals) < 1.0, (
        "Der Vermerk hat den Zeitstempel des Stubs verschoben — er faellt "
        "damit in ein falsches Kostenfenster.")


def test_ohne_stub_bleibt_der_wiederanlauf_still(tmp_path, schale):
    """Gegenprobe: Ein schmutziger Baum allein, ein Ersatzzettel aus BL-46,
    ein echtes Log und ein ARCHIVIERTER Stub halten nichts an und sagen
    nichts — sonst meldete sich die Pruefung bei jedem Start."""
    repo = _projekt(tmp_path, schale)
    logs = repo / ".ralph-logs"
    _echtes_log(logs, "stufe-6-20261010-200000.json", 1.0)
    (logs / "stufe-5-20261009.json").write_text(json.dumps(
        {"is_error": True, "result": "", "total_cost_usd": None,
         "team_versuch": "verworfen", "team_dauer_s": 60}), encoding="utf-8")
    _stub_datei(logs / "archiv", "stufe-4-20261008.json")
    (repo / "src" / "daten.txt").write_text("von Hand\n", encoding="utf-8")
    r = _wiederanlauf(repo, schale)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "BL-326" not in r.stdout + r.stderr, r.stdout + r.stderr


# --- Am lebenden Objekt: ralph und die Vollautomatik --------------------------

@pytest.mark.parametrize("schmutzig", [True, False])
def test_ralph_prueft_vor_dem_ersten_aufruf(tmp_path, schale, schmutzig):
    """Einzel- und Halbautomatik starten ralph direkt. Mit liegengebliebener
    Arbeit kostet der Start keinen Aufruf; mit sauberem Baum geht es weiter
    bis zur CLI (hier die Falle, die laut scheitert)."""
    import test_bl301_stufe_ohne_planblock as h
    repo, falle = h._projekt(tmp_path, schale, 29)
    _stub_datei(repo / ".ralph-logs", "stufe-29-20261010-214712.json")
    if schmutzig:
        (repo / "src" / "app.py").write_text("x = 2\n", encoding="utf-8")
    r = h._ralph(repo, schale, falle)
    aus = r.stdout + r.stderr
    assert "Kit-BL-326" in aus, aus
    if schmutzig:
        assert r.returncode == 42, aus
        assert h.FALLE not in aus, (
            f"{schale.name}: ralph hat trotz liegengebliebener Arbeit die CLI "
            f"gerufen.\n{aus}")
        assert "src/app.py" in aus, aus
    else:
        assert h.FALLE in aus, (
            f"{schale.name}: Mit sauberem Baum muss ralph weiterlaufen.\n{aus}")


@pytest.mark.parametrize("schmutzig", [True, False])
@pytest.mark.parametrize("bahn", ("bash", "pwsh"))
def test_die_vollautomatik_prueft_vor_phase_1(tmp_path, bahn, schmutzig):
    """Der Feldfall war eine Vollautomatik. Ihr Start prueft, bevor die
    erste Rolle laeuft — hier der erste Haken der gemeinsamen Startpruefung
    (BL-330, BL-333, BL-336)."""
    if bahn == "bash":
        verlange_bash()
        import test_bl217_phasen_zeiger as h
        repo = h._projekt(tmp_path)
        lauf = lambda: h._lauf(repo)  # noqa: E731
    else:
        verlange_pwsh()
        import test_bl241_fixphase_hat_einen_eigenen_einstieg as h
        repo = h._pwsh_projekt(tmp_path)
        lauf = lambda: h._pwsh(repo, "vollautomatik.ps1")  # noqa: E731
    _stub_datei(repo / ".ralph-logs", "stufe-5-20261010-214712.json")
    if schmutzig:
        (repo / "src").mkdir(exist_ok=True)
        (repo / "src" / "halbe-arbeit.py").write_text("x = 1\n",
                                                      encoding="utf-8")
    r = lauf()
    aus = r.stdout + r.stderr
    assert "Kit-BL-326" in aus, aus
    if schmutzig:
        assert r.returncode == 42, aus
        assert "STUB ralph" not in aus and "=== PHASE 1" not in aus, (
            f"{bahn}: Die Vollautomatik hat trotz liegengebliebener Arbeit "
            f"eine Rolle gestartet.\n{aus}")
        assert "src/" in aus, aus
    else:
        assert r.returncode == 0, aus
        assert "STUB ralph" in aus, aus


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

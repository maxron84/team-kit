#!/usr/bin/env python3
"""BL-285: Auf der bash-Bahn lasen `harry.sh` und `marv.sh` den Grundauftrag
VOR dem Laden von `team.config.sh` — ein Wert aus der Datei kam nie an.

WAS IM FELD PASSIERT IST (`Feld F`, 2026-09-27)
    Der Architekt setzte, wie Kopfkommentar und Doku es verlangen, einen
    projektspezifischen Grundauftrag in `team.config.sh` UND
    `team.config.ps1`, zeichengleich. Danach war `test_bl117` (der
    Lauf-Vergleich beider Bahnen) genau fuer `[harry]` und `[marv]` rot: Die
    bash-Bahn setzte den stackneutralen Default ab, die pwsh-Bahn den
    konfigurierten Grundauftrag.

WARUM
    `export AUFTRAG="${TEAM_REDTEAM_AUFTRAG_HARRY:-<Default>}"` stand vor
    `source ./team/redteam.sh` — und erst redteam.sh laedt die Bibliothek und
    damit die Konfiguration. Der Wert konnte nur aus der PROZESSUMGEBUNG
    kommen. Die pwsh-Wrapper importieren das Modul vor dem Lesen und waren nie
    betroffen.

WARUM DIE KIT-TESTS ES NICHT ZEIGTEN
    Im Kit ist der Wert leer, beide Bahnen fallen auf denselben Default, und
    `BL-117` ist gruen. Ein Test, der den Grundauftrag ueber die UMGEBUNG
    setzt, geht am Fehler vorbei, weil die Umgebung ja ankommt. Dieser Test
    setzt ihn deshalb IN DER DATEI und raeumt die Umgebung aus.

BEIFANG BEIM BAUEN, und er hat Geld gekostet
    Die erste Fassung dieses Tests startete auf der pwsh-Bahn dreimal die
    ECHTE CLI statt der Attrappe (zusammen rund 0,31 USD): Die Bibliothek las
    `TEAM_CLAUDE_BIN` dort nur aus der Konfiguration, nicht aus der Umgebung —
    anders als bash (`${TEAM_CLAUDE_BIN:-claude}`). Behoben ist das in
    `lib.psm1` (Fall unten). Der Test verlaesst sich trotzdem nicht darauf:
    Die Attrappe steht IN der Konfiguration, und ein `claude` vorne im PATH
    bricht laut ab, falls die Aufloesung doch beim Suchpfad landet.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (Variable, entrypoint_aufruf,  # noqa: E402
                      entrypoint_pfad, kopiere_team_namensraum, pfad_voran,
                      werkzeug_wert)
from test_bl117_prompt_gleichstand_am_lauf import (ANTWORT, BASH_STUB,  # noqa: E402
                                                   PWSH_STUB)

GRUNDAUFTRAG = "PROJEKT-GRUNDAUFTRAG-BL285: pruefe die Spielskripte"
FALLE = "ECHTE-CLI-GESUCHT-BL285"


def _falle(tmp_path):
    """Ein `claude` im Suchpfad, das laut scheitert statt zu arbeiten."""
    ordner = tmp_path / "falle"
    ordner.mkdir()
    sh = ordner / "claude"
    sh.write_text(f"#!/usr/bin/env bash\necho {FALLE} >&2\nexit 99\n",
                  encoding="utf-8", newline="\n")
    sh.chmod(0o755)
    (ordner / "claude.cmd").write_text(
        f"@echo off\r\necho {FALLE} 1>&2\r\nexit /b 99\r\n", encoding="utf-8")
    return ordner


def _stub(tmp_path, schale):
    """Die Attrappe und der Wert, unter dem die Bahn sie findet."""
    if schale.name == "bash":
        stub = tmp_path / "claude-stub.sh"
        stub.write_text(BASH_STUB.format(antwort=ANTWORT), encoding="utf-8",
                        newline="\n")
        stub.chmod(0o755)
        return stub.as_posix()
    stub = tmp_path / "claude-stub.ps1"
    stub.write_text(PWSH_STUB.format(antwort=ANTWORT), encoding="utf-8-sig",
                    newline="\n")
    return str(stub)


def _projekt(tmp_path, schale, rolle, stub_wert):
    repo = tmp_path / "repo"
    for ordner in ("src", "tests", "plans"):
        (repo / ordner).mkdir(parents=True, exist_ok=True)
    wrapper = entrypoint_pfad(f"{rolle}{schale.endung}")
    if not wrapper.is_file():
        pytest.skip(f"{wrapper.name} liegt in dieser Ablage nicht")
    shutil.copy(wrapper, repo / wrapper.name)
    kopiere_team_namensraum(repo / "team")
    schale.config_schreiben(repo, {
        "TEAM_DOMAENEN": "produkt",
        "TEAM_PRODUKTIVCODE": "src/",
        "TEAM_TEST_ORDNER": "tests/",
        "TEAM_PLAN_ORDNER": "plans/",
        "TEAM_BEUTEBUCH": "plans/beutebuch.md",
        "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
        "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
        "TEAM_CLAUDE_BIN": stub_wert,
        # Die bash-Bahn erwartet die Whitelists aus der Konfiguration (die
        # installierte team.config.sh leitet sie aus den Ordnern ab).
        "TEAM_WHITELIST_REDTEAM": "^(tests/|plans/)",
        "TEAM_WHITELIST_AXEL": "^plans/",
        # DER Fall: der Grundauftrag steht IN DER DATEI.
        f"TEAM_REDTEAM_AUFTRAG_{rolle.upper()}": GRUNDAUFTRAG,
    })
    (repo / "plans" / "beutebuch.md").write_text(
        "# Beutebuch\n\n## Funde\n", encoding="utf-8", newline="\n")
    (repo / "src" / "app.py").write_text("print('hallo')\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-qm", "fixture"]):
        subprocess.run(["git", *befehl], cwd=repo, check=True,
                       capture_output=True)
    return repo


def _fahre(repo, schale, rolle, tmp_path, stub_wert):
    fang = tmp_path / f"prompt-{rolle}.txt"
    if schale.name == "bash":
        befehl = entrypoint_aufruf(repo / f"{rolle}.sh")
    else:
        befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                  str(repo / f"{rolle}.ps1")]
    umgebung = dict(os.environ)
    umgebung["PATH"] = pfad_voran(_falle(tmp_path), umgebung)
    # Die Umgebung wird AUSGERAEUMT — sonst misst der Test die Umgebung, und
    # die kam auch vorher schon an.
    for weg in ("TEAM_REDTEAM_FOCUS", "TEAM_REDTEAM_AUFTRAG_HARRY",
                "TEAM_REDTEAM_AUFTRAG_MARV", "ANTHROPIC_API_KEY", "AUTH_MODE"):
        umgebung.pop(weg, None)
    umgebung.update(TEAM_PROMPT_FANG=str(fang), TEAM_AUTH_MODE="abo",
                    TEAM_LOCK_HELD="1", TEAM_CLAUDE_BIN=stub_wert)
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    assert FALLE not in r.stderr + r.stdout, (
        f"Die {schale.name}-Bahn hat die ECHTE CLI gesucht statt der Attrappe "
        f"— dieser Test haette Geld gekostet.\n{r.stdout}\n{r.stderr}")
    if not fang.is_file():
        pytest.fail(f"{rolle} hat auf der {schale.name}-Bahn keinen Prompt "
                    f"abgesetzt (Exit {r.returncode}).\n{r.stdout}\n{r.stderr}")
    return fang.read_text(encoding="utf-8")


@pytest.mark.parametrize("rolle", ["harry", "marv"])
def test_der_grundauftrag_aus_der_datei_kommt_im_prompt_an(tmp_path, schale,
                                                          rolle):
    stub_wert = _stub(tmp_path, schale)
    repo = _projekt(tmp_path, schale, rolle, stub_wert)
    prompt = _fahre(repo, schale, rolle, tmp_path, stub_wert)
    assert GRUNDAUFTRAG in prompt, (
        f"{rolle} ({schale.name}): Der Grundauftrag steht in "
        f"team.config{schale.endung}, kommt aber nicht im Prompt an — die "
        f"Rolle sweept mit dem stackneutralen Default, ohne jedes Signal "
        f"(BL-285).\n--- Prompt (Anfang) ---\n{prompt[:1500]}")


@pytest.mark.parametrize("rolle", ["harry", "marv"])
def test_der_wrapper_laedt_die_konfiguration_vor_dem_auftrag(rolle):
    """Dieselbe Zusicherung am Quelltext — billig, und sie nennt die Zeile."""
    pfad = entrypoint_pfad(f"{rolle}.sh")
    if not pfad.is_file():
        pytest.skip(f"{rolle}.sh liegt in dieser Ablage nicht")
    zeilen = pfad.read_text(encoding="utf-8").splitlines()
    auftrag = [i for i, z in enumerate(zeilen) if z.startswith("export AUFTRAG=")]
    laden = [i for i, z in enumerate(zeilen)
             if "team.config.sh" in z and "source" in z
             and not z.lstrip().startswith("#")]
    assert auftrag, "Wrapper-Aufbau unerwartet — Test nachziehen"
    assert laden and laden[0] < auftrag[0], (
        f"{rolle}.sh liest den Grundauftrag VOR dem Laden der Konfiguration "
        f"(BL-285).")


def test_pwsh_liest_die_cli_auch_aus_der_umgebung(tmp_path, schale):
    """Der Beifang: Ohne Zeile in der Konfiguration gilt die UMGEBUNG — auf
    beiden Bahnen. Vorher fiel pwsh hier auf das `claude` im PATH zurueck."""
    lib = schale.lib_kopieren(tmp_path)
    ziel = "C:/nirgends/attrappe-bl285"
    r = schale.lauf([Variable("TEAM_CLAUDE_BIN")], cwd=tmp_path, lib=lib,
                    env={"TEAM_CLAUDE_BIN": ziel})
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == ziel, (
        f"{schale.name}: TEAM_CLAUDE_BIN aus der Umgebung kommt nicht an "
        f"({r.stdout.strip()!r}) — die Bahn ruft dann das `claude` aus dem "
        f"PATH, also die echte CLI (BL-285).")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

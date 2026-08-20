#!/usr/bin/env python3
"""BL-52: Der Sweep-Auftrag endete am Produktivcode-Ordner — Einstiegspunkte in
der Repo-Wurzel sah das Red Team nie.

Beobachtet an einer fremden, gewachsenen Codebasis (Project-Family-ERP,
2026-08-11, nur analysiert): `main.py` in der Wurzel ist der Einstiegspunkt der
gesamten GUI, `bin/build.py` erzeugt das ausgelieferte Binaer — beide ausserhalb
von `src/`, beide bei Default-Konfiguration dauerhaft ungeprueft. Das ist KEINE
Guard-Luecke (die Whitelist ist positiv, ausserhalb von Test- und Plan-Ordner
ist jede Aenderung eine Verletzung), sondern eine PRUEFUMFANGS-Luecke — und sie
ist still: Ein Sweep, der src/ sauber meldet, sieht aus wie ein Sweep, der das
Projekt sauber gemeldet hat.

Geprueft wird am echten Prompt: harry.sh laeuft mit gestubbter CLI, die den
Prompt wegschreibt. Ein Test gegen den Skript-Quelltext haette die Kopplung
"Variable gesetzt ⇒ steht im Auftrag" nicht gezeigt.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_aufruf, kopiere_team_namensraum,
                      pfad_voran)

WURZEL = Path(__file__).resolve().parents[2]
HARRY = WURZEL / "harry.sh"


def _konfig(schluessel):
    """Liest einen Wert aus der INSTALLIERTEN team.config.sh — die Ordnernamen
    bestimmt das Zielprojekt, nicht dieser Test."""
    return subprocess.run(
        [BASH, "-c", f'source "{WURZEL}/team.config.sh"; printf "%s" "${schluessel}"'],
        capture_output=True, text=True).stdout


def _neutrale_config():
    """team.config.sh mit LEEREN Defaults fuer die Bestandswerte — die Config
    benutzt `${VAR:-default}`, eine leere Umgebungsvariable faellt also auf den
    Projektwert zurueck. Ohne das koennte die Gegenprobe fuer das frisch
    angelegte Projekt in einem Bestandsprojekt nicht hergestellt werden."""
    text = (WURZEL / "team.config.sh").read_text(encoding="utf-8")
    zeilen = []
    for zeile in text.splitlines(True):
        for name in ("TEAM_WEITERER_CODE", "TEAM_TEST_ORDNER_BESTAND",
                     "TEAM_PLAN_ORDNER_BESTAND"):
            if zeile.startswith(name + "="):
                zeile = f'{name}="${{{name}:-}}"\n'
        zeilen.append(zeile)
    return "".join(zeilen)


def _prompt(tmp_path, zusatz_env):
    """Faehrt harry.sh mit gestubbter CLI und liefert den Prompt zurueck, den
    die Rolle wirklich bekommen haette."""
    if not HARRY.is_file():
        pytest.skip("harry.sh liegt nur in der INSTALLIERTEN Ablage "
                    "(im Kit unter bash/entry/ bzw. pwsh/entry/) — geprueft wird via kit-test.sh")
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(HARRY, repo / "harry.sh")
    (repo / "team.config.sh").write_text(_neutrale_config(), encoding="utf-8")
    kopiere_team_namensraum(repo / "team")
    beutebuch = _konfig("TEAM_BEUTEBUCH")
    for ordner in (_konfig("TEAM_PLAN_ORDNER"), _konfig("TEAM_TEST_ORDNER"),
                   _konfig("TEAM_PRODUKTIVCODE")):
        (repo / ordner).mkdir(parents=True, exist_ok=True)
    shutil.copy(WURZEL / beutebuch, repo / beutebuch)
    (repo / _konfig("TEAM_PRODUKTIVCODE") / "app.py").write_text(
        "print('hallo')\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@localhost"],
                   ["config", "user.name", "Test"], ["add", "-A"],
                   ["commit", "-qm", "fixture"]):
        subprocess.run(["git", "-C", str(repo)] + befehl, check=True)

    dump = tmp_path / "prompt.txt"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "claude"
    ergebnis = json.dumps({
        "subtype": "success", "is_error": False, "total_cost_usd": 0.1,
        "result": "fertig <promise>REDTEAM_SWEEP_COMPLETE</promise>"})
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f'printf "%s\\n" "$@" >> "{dump}"\n'
        f"cat <<'JSON'\n{ergebnis}\nJSON\n", encoding="utf-8")
    stub.chmod(0o755)

    env = dict(os.environ)
    env.update({"PATH": pfad_voran(bin_dir, env), "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    env.update(zusatz_env)
    lauf = subprocess.run(entrypoint_aufruf("./harry.sh"), cwd=repo, env=env,
                          capture_output=True, text=True)
    assert lauf.returncode == 0, lauf.stderr
    return dump.read_text(encoding="utf-8")


def test_weiterer_code_steht_im_pruefauftrag(tmp_path):
    """Der Feldfall: Einstiegspunkt und Build-Ordner liegen neben src/."""
    text = _prompt(tmp_path, {"TEAM_WEITERER_CODE": "main.py bin/"})
    prod = _konfig("TEAM_PRODUKTIVCODE")
    assert f"unter {prod} sowie main.py bin/" in text, (
        "der Sweep-Auftrag nennt den Code ausserhalb des Produktivcode-Ordners "
        f"nicht:\n{text}")


def test_weiterer_code_bleibt_tabu(tmp_path):
    """Der Pruefumfang waechst, die Schreibrechte NICHT: Was mitgeprueft wird,
    muss in derselben Zeile tabu bleiben — sonst liest sich die Erweiterung als
    Erlaubnis."""
    text = _prompt(tmp_path, {"TEAM_WEITERER_CODE": "main.py bin/"})
    prod = _konfig("TEAM_PRODUKTIVCODE")
    assert f"NIEMALS Produktivcode ({prod}** und main.py bin/)" in text, (
        f"die eiserne Regel deckt den zusaetzlichen Code nicht:\n{text}")


def test_ohne_zusatz_bleibt_der_auftrag_wortgleich(tmp_path):
    """Gegenprobe fuer das frisch angelegte Projekt: Ist der Wert leer, darf
    kein Rest der Erweiterung im Prompt stehen — kein haengendes 'sowie', kein
    leeres 'und'."""
    text = _prompt(tmp_path, {"TEAM_WEITERER_CODE": ""})
    prod = _konfig("TEAM_PRODUKTIVCODE")
    assert f"unter {prod} (" in text, f"Scope-Zeile beschaedigt:\n{text}"
    assert "sowie" not in text, f"Rest der Erweiterung im Prompt:\n{text}"
    assert f"NIEMALS Produktivcode ({prod}**)" in text, (
        f"eiserne Regel beschaedigt:\n{text}")


def test_axel_teilt_den_pruefumfang():
    """Axel liest denselben Code — was fuer Harry und Marv tabu ist, ist es
    fuer ihn auch. Sonst waere die Grenze rollenabhaengig."""
    text = (WURZEL / "axel.sh").read_text(encoding="utf-8") \
        if (WURZEL / "axel.sh").is_file() else ""
    if not text:
        pytest.skip("axel.sh liegt nur in der INSTALLIERTEN Ablage")
    assert "TEAM_WEITERER_CODE" in text, (
        "axel.sh kennt den erweiterten Pruefumfang nicht")
    assert "AXEL_TABU" in text


def test_frank_darf_den_fund_dort_reparieren_wo_er_liegt():
    """Findet das Red Team etwas ausserhalb des Produktivcode-Ordners, muss
    Franks Auftrag den Ort nennen duerfen — sonst repariert er am falschen
    Platz oder gar nicht."""
    pfad = WURZEL / "frank.sh"
    if not pfad.is_file():
        pytest.skip("frank.sh liegt nur in der INSTALLIERTEN Ablage")
    text = pfad.read_text(encoding="utf-8")
    assert "TEAM_WEITERER_CODE" in text, (
        "frank.sh kennt nur den Produktivcode-Ordner")
    assert "FIX_ORTE" in text


def test_config_erklaert_dass_der_wert_keine_rechte_gibt():
    """Die gefaehrlichste Fehllesung: 'mitgeprueft' als 'darf geschrieben
    werden'. Die Config muss das ausdruecklich ausschliessen."""
    text = (WURZEL / "team.config.sh").read_text(encoding="utf-8")
    assert "TEAM_WEITERER_CODE" in text
    assert "PRÜFUMFANG, nicht die Schreibrechte" in text, (
        "team.config.sh trennt Pruefumfang und Schreibrechte nicht ausdruecklich")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

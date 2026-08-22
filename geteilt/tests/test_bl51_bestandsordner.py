#!/usr/bin/env python3
"""BL-51: Der Plan-Ordner wird ungeprueft zur Schreibzone der Read-Only-Rollen —
in einer gewachsenen Codebasis ist er meist schon anderweitig belegt.

Die Whitelist von Guard Linie 3 ist POSITIV: Harry und Marv duerfen
Test- und Plan-Ordner schreiben, Axel den Plan-Ordner. Zeigt der Plan-Ordner auf
ein bereits belegtes Verzeichnis, bekommen die drei ausdruecklich als Read-Only
gefuehrten Rollen Schreib- und Loeschrecht auf Bestandsdokumente, OHNE dass der
Guard je anschlaegt — die Pfade stehen ja auf der Whitelist. Der Schnappschuss
aus BL-16 faengt das nicht auf: Er nimmt eine Rolle nur fuer Pfade aus der
Haftung, die beim Rollenstart schon schmutzig waren; committete
Bestandsdokumente sind sauber und damit ungeschuetzt.

Beobachtet an Feld C (2026-08-11, nur analysiert): zehn fachliche
Dokumente in plans/, darunter die Architektur- und die Refactoring-Planung.

Was hier geprueft wird, ist die PROMPT-Auflage — die Mechanik kann es nicht:
Der Guard laesst die Rolle in ihrer Schreibzone gewaehren. Die harte Variante
bleibt der eigene, leere Plan-Ordner; dafuer warnt der Installer (kit-test.sh,
Schritt 6).
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

BESTAND = "bestand-architektur.md bestand-refactoring-plan.md"


def _konfig(schluessel):
    return subprocess.run(
        [BASH, "-c", f'source "{WURZEL}/team.config.sh"; printf "%s" "${schluessel}"'],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def _neutrale_config():
    """team.config.sh mit LEEREN Defaults fuer die drei Bestandswerte.

    Notwendig, weil die Config `${VAR:-default}` benutzt: Eine leere
    Umgebungsvariable faellt auf den Default zurueck. In einem Projekt, das
    wirklich einen Bestand fuehrt, koennte die Gegenprobe 'ohne Bestand kein
    Block' sonst gar nicht hergestellt werden — sie wuerde dort rot, ohne dass
    etwas kaputt waere. Die Fixture setzt den Ausgangszustand selbst."""
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
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert lauf.returncode == 0, lauf.stderr
    return dump.read_text(encoding="utf-8")


def test_bestand_wird_im_prompt_als_fremdes_eigentum_benannt(tmp_path):
    text = _prompt(tmp_path, {"TEAM_PLAN_ORDNER_BESTAND": BESTAND})
    assert "BESTAND — NICHT DEIN EIGENTUM" in text, (
        f"der Sweep-Auftrag nennt den Bestand nicht:\n{text}")
    for datei in BESTAND.split():
        assert datei in text, f"{datei} fehlt im Auftrag:\n{text}"


def test_die_regel_gilt_auch_fuer_das_nicht_aufgezaehlte(tmp_path):
    """Die Aufzaehlung ist gekuerzt (der Installer schreibt hoechstens zwoelf
    Namen) und veraltet, sobald jemand eine Datei hinzulegt. Ohne den
    verallgemeinernden Satz waere sie eine Erlaubnis fuer alles Uebrige."""
    text = _prompt(tmp_path, {"TEAM_PLAN_ORDNER_BESTAND": BESTAND})
    assert "NUR NEUE Dateien" in text, f"die Auflage fehlt:\n{text}"
    assert "auch nicht, was in dieser Aufzählung fehlt" in text, (
        f"die Regel gilt nur fuer die aufgezaehlten Dateien:\n{text}")


def test_der_prompt_sagt_dass_der_guard_hier_nicht_greift(tmp_path):
    """Die Rolle muss wissen, dass sie hier ohne Netz arbeitet — sonst liest
    sie das Ausbleiben einer Guard-Meldung als Erlaubnis."""
    text = _prompt(tmp_path, {"TEAM_PLAN_ORDNER_BESTAND": BESTAND})
    assert "Der Guard" in text and "gewähren" in text, (
        f"der Prompt verschweigt, dass der Guard hier nicht anschlaegt:\n{text}")


def test_test_ordner_bestand_wird_ebenso_genannt(tmp_path):
    """Eine Etage tiefer derselbe Fehler: In einer Bestandscodebasis liegt im
    Test-Ordner eine gewachsene Suite, und ein Reproducer, der eine bestehende
    Testdatei ueberschreibt statt danebenzulegen, ist derselbe Uebergriff."""
    text = _prompt(tmp_path, {"TEAM_TEST_ORDNER_BESTAND": "test_scanner.py conftest.py"})
    assert "BESTAND — NICHT DEIN EIGENTUM" in text
    assert "test_scanner.py conftest.py" in text, (
        f"der Bestand des Test-Ordners fehlt:\n{text}")


def test_ohne_bestand_kein_block(tmp_path):
    """Gegenprobe fuer das frisch angelegte Projekt: Der Normalfall ist der
    leere Ordner. Ein Block, der immer erscheint, verbraucht Aufmerksamkeit
    ohne Anlass (BL-14)."""
    text = _prompt(tmp_path, {"TEAM_PLAN_ORDNER_BESTAND": "",
                              "TEAM_TEST_ORDNER_BESTAND": ""})
    assert "BESTAND" not in text, f"Bestandsblock ohne Bestand:\n{text}"


def test_axel_bekommt_dieselbe_auflage():
    """Axels einzige Schreibzone IST der Plan-Ordner — fuer ihn ist die Regel
    am schaerfsten."""
    pfad = WURZEL / "axel.sh"
    if not pfad.is_file():
        pytest.skip("axel.sh liegt nur in der INSTALLIERTEN Ablage")
    text = pfad.read_text(encoding="utf-8")
    assert "TEAM_PLAN_ORDNER_BESTAND" in text, (
        "axel.sh kennt den Bestand im Plan-Ordner nicht")
    assert "BESTAND — NICHT DEIN EIGENTUM" in text
    assert "auch nicht,\nwas in dieser Aufzählung fehlt" in text or \
           "auch nicht, was in dieser Aufzählung fehlt" in text.replace("\n", " "), (
        "die verallgemeinernde Regel fehlt in axel.sh")


def test_config_traegt_beide_werte_und_nennt_die_harte_variante():
    text = (WURZEL / "team.config.sh").read_text(encoding="utf-8")
    assert "TEAM_PLAN_ORDNER_BESTAND" in text
    assert "TEAM_TEST_ORDNER_BESTAND" in text
    assert "PROMPT-Auflage, keine Mechanik" in text, (
        "die Config verschweigt, dass der Guard das nicht erzwingt")
    assert "eigenen, leeren Plan-Ordner" in text, (
        "der Ausweg (eigener leerer Ordner) steht nicht dort, wo der Wert steht")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

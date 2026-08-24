#!/usr/bin/env python3
"""BL-47: Ein Sweep ohne Fund war von einem abgebrochenen Sweep nicht zu
unterscheiden — und die Commit-Botschaft behauptete in beiden Faellen Funde.

Feld K29 (2026-08-10): Marvs Sweep lief 9 Minuten, kostete 3,1418 USD und
committete EINE Datei — ein 112-zeiliges Sondenskript, keine Beutebuch-Zeile.
Die Commit-Botschaft lautete trotzdem "… — neue Funde/Reproducer", das
Protokoll "[marv] Funde committet. Uebergabe an Frank."

Inhaltlich war das Nichtfinden richtig (Marv lief nach Harry ueber denselben
Bereich). Der Fund ist die UNUNTERSCHEIDBARKEIT: Aus Protokoll und Commit
laesst sich "geprueft, nichts gefunden" nicht von "nie fertig geworden"
trennen — beides kostet gleich viel und sieht gleich aus. Eine read-only-Rolle
hat weder Statuswechsel noch Produktivdiff, an dem es sonst auffiele.

Die Zahl lag vor: NEXT_ID vor dem Sweep gegen next-id danach. Sie wurde nur nie
ausgewertet. Dieser Test faehrt die WIRKLICHE Bedienoberflaeche (harry.sh mit
gestubbter CLI) und liest die echte Commit-Botschaft aus dem Repo.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_aufruf, kit_pfad,
                      kopiere_team_namensraum, pfad_voran)

WURZEL = Path(__file__).resolve().parents[2]
HARRY = WURZEL / "harry.sh"

FUND_BLOCK = """
### HM-{nr} — Testfund
- **Angreifer**: Harry
- **Schweregrad**: klein
- **Status**: an Frank übergeben
- **Reproschritte**: 1. …
- **Erwartung**: …
- **Realität**: …
- **Reproducer-Test**: `tests/test_hm{nr}_stichwort.py`
"""


def _fund(feld):
    """Fundblock, dessen Nummer ERST im Fixture eingesetzt wird (BL-62).

    Fest verdrahtete Nummern machten diesen Test davon abhaengig, dass das
    Beutebuch des ZIELPROJEKTS leer ist: `_fixture()` kopiert das echte
    Beutebuch herein, und `redteam.sh` zaehlt neue Funde ueber `next-id`
    vorher/nachher. Ein angehaengter `HM-1`, den es dort laengst gibt, erhoeht
    die naechste freie Nummer nicht — der Sweep meldet korrekt "keine neuen
    Funde", und der Test faellt um, obwohl die Mechanik stimmt. Im Feld
    (Feld A, Beutebuch bis HM-100) sind daran zwei Gegenproben nach einem
    Kit-Update rot geworden."""
    return FUND_BLOCK.replace("{nr}", "{" + feld + "}")


def _konfig(schluessel):
    """Liest einen Wert aus der INSTALLIERTEN team.config.sh — die Ordnernamen
    bestimmt das Zielprojekt, nicht dieser Test."""
    return subprocess.run(
        [BASH, "-c", f'source "{WURZEL}/team.config.sh"; printf "%s" "${schluessel}"'],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def _fixture(tmp_path, stub_body):
    """Wegwerf-Repo mit gestubbter CLI. stub_body ist der Bash-Rumpf, mit dem
    die 'Rolle' ihre Seiteneffekte im Arbeitsbaum hinterlaesst."""
    if not HARRY.is_file():
        pytest.skip("harry.sh liegt nur in der INSTALLIERTEN Ablage "
                    "(im Kit unter bash/entry/ bzw. pwsh/entry/) — geprueft wird via kit-test.sh")
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(HARRY, repo / "harry.sh")
    shutil.copy(WURZEL / "team.config.sh", repo / "team.config.sh")
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

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "claude"
    ergebnis = json.dumps({
        "subtype": "success", "is_error": False, "total_cost_usd": 3.1418,
        "result": "fertig <promise>REDTEAM_SWEEP_COMPLETE</promise>"})
    # BL-62: Die Fundnummern kommen aus dem kopierten Beutebuch, nicht aus
    # dem Test — sonst haengt er an der Annahme "Zielprojekt hat keine Funde".
    naechste = subprocess.run(
        [sys.executable, "team/tools/beutebuch.py", "next-id"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    nr1 = int(naechste.split("-")[-1] or 1)
    stub.write_text("#!/usr/bin/env bash\n"
                    + stub_body.format(tests=_konfig("TEAM_TEST_ORDNER"),
                                       beutebuch=beutebuch,
                                       nr1=nr1, nr2=nr1 + 1)
                    + f"\ncat <<'JSON'\n{ergebnis}\nJSON\n", encoding="utf-8")
    stub.chmod(0o755)
    return repo, bin_dir


def _sweep(tmp_path, stub_body):
    repo, bin_dir = _fixture(tmp_path, stub_body)
    env = dict(os.environ)
    env.update({"PATH": pfad_voran(bin_dir, env), "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    ergebnis = subprocess.run(entrypoint_aufruf("./harry.sh"), cwd=repo, env=env,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    botschaft = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--pretty=%s"],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    return ergebnis, botschaft


def test_sonde_ohne_fund_behauptet_keine_funde(tmp_path):
    """Die Feldlage exakt: eine Sondendatei committet, null Beutebuch-Zeilen."""
    ergebnis, botschaft = _sweep(
        tmp_path, 'printf "x\\n" > "{tests}_probe.py"')
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "keine neuen Funde" in botschaft, (
        f"die Commit-Botschaft behauptet weiter Funde: {botschaft!r}")
    assert "neue Funde/Reproducer" not in botschaft
    assert "Geprüft, KEINE neuen Funde" in ergebnis.stdout, (
        f"das Protokoll trennt die beiden Faelle nicht:\n{ergebnis.stdout}")
    assert "Keine Übergabe an Frank" in ergebnis.stdout, (
        "ohne Fund gibt es nichts zu uebergeben — die alte Zeile behauptete "
        "die Uebergabe trotzdem")
    assert "Funde committet" not in ergebnis.stdout


def test_echter_fund_wird_gezaehlt(tmp_path):
    """Gegenprobe: Mit Fund muss die Zahl stimmen und die Uebergabe stehen —
    sonst haette dieser Fix den Normalfall stumm gemacht."""
    ergebnis, botschaft = _sweep(
        tmp_path,
        "cat >> {beutebuch} <<'EOF'\n" + _fund("nr1") + "\nEOF")
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "1 neuer Fund" in botschaft, f"Botschaft: {botschaft!r}"
    assert "Übergabe an Frank" in ergebnis.stdout


def test_zwei_funde_werden_gezaehlt(tmp_path):
    doppelt = _fund("nr1") + _fund("nr2")
    ergebnis, botschaft = _sweep(
        tmp_path, "cat >> {beutebuch} <<'EOF'\n" + doppelt + "\nEOF")
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "2 neue Funde" in botschaft, f"Botschaft: {botschaft!r}"


def test_auftrag_verlangt_wegwerf_skripte_zu_entsorgen():
    """Zweiter Teil desselben Vorfalls: Die Read-Only-Regel ERLAUBT
    Wegwerf-Skripte, verpflichtete aber nie zum Wegwerfen. Die Sonde blieb in
    tests/ liegen — kein Reproducer, in keinem Fundblock referenziert, und
    trotzdem im Geltungsbereich der Zusicherung, die die Kaskade gerade
    errichtet hatte."""
    text = (kit_pfad("redteam.sh")).read_text(encoding="utf-8")
    assert "LÖSCHST du wieder" in text, (
        "der Sweep-Auftrag verlangt das Wegwerfen nicht")
    assert "test_hm<Nr>_<stichwort>" in text, (
        "die Alternative — als Reproducer benennen — fehlt")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

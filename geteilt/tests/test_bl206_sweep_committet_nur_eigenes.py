#!/usr/bin/env python3
"""BL-206 — der Commit-Block des Red-Team-Sweeps umging den Fremdfilter.

`redteam.sh`/`redteam.ps1` haben am Ende des Sweeps `git add <beutebuch>
<testordner>` gefahren. `git add` auf einen ORDNER nimmt jede untracked Datei
darin mit — auch eine fremde, die schon vor dem Rollenstart im Baum lag. Sie
landete damit unter der Sweep-Botschaft ("docs(beute): Marv-Sweep … — 1 neuer
Fund"), also unter einer Urheberschaft, die nicht stimmt.

Das ist eine Auslassung, kein Entwurf: `team_guard_verify` und
`team_rollback_rolle` rufen beide `team_fremd_ausfiltern`. Der Commit-Block war
die DRITTE Stelle mit derselben Zustaendigkeit und die einzige ohne den Filter
— woertlich die Bauform von BL-114, wo der `git clean` eingeschraenkt war und
das `git reset --hard` daneben nicht. Zwei Stellen wurden nachgezogen, diese
nicht.

Feldbeleg (`Feld B`, 2026-08-28): Beim Start einer Sitzung lag ein fremder
Reproducer-Test untracked im Testordner. Gut ausgegangen ist es nur, weil der
Fixer den Fund ohnehin bearbeitete und die Datei regulaer mitnahm — nicht,
weil der Guard sie geschuetzt haette.

DIESE DATEI FAEHRT BEIDE RICHTUNGEN, und das ist der Punkt: Ein Fix, der nur
die erste prueft, wird gruen, indem gar nichts mehr committet wird. Der Sweep
SOLL Reproducer und Beutebuch-Zeilen committen — genau das ist sein Beitrag.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (BASH, Ausgabe, Git, Ruf, Schreib, entrypoint_aufruf,
                      kit_pfad, kopiere_team_namensraum, pfad_voran)

WURZEL = Path(__file__).resolve().parents[2]
HARRY = WURZEL / "harry.sh"

FREMD = "# Reproducer eines fremden Schreibers, lag vor dem Rollenstart da\n"


def _git(repo, *args):
    ergebnis = subprocess.run(["git", *args], cwd=str(repo),
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    assert ergebnis.returncode == 0, ergebnis.stderr
    return ergebnis.stdout.strip()


# --- (1) Die Bibliothek, auf beiden Bahnen -----------------------------------
# Der Filter gehoert dorthin, wo Guard und Rollback ihn auch holen. Eine
# Funktion, die beide Bahnen teilen, kann nicht wieder auseinanderlaufen.


def _repo(tmp_path, schale):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "plans").mkdir()
    (repo / "team").mkdir()
    (repo / "plans" / "beutebuch.md").write_text("# Beutebuch\n",
                                                 encoding="utf-8")
    # Der Testordner ist GETRACKT — so sieht er in jedem gewachsenen Projekt
    # aus. Waere er leer und untracked, meldete `git status --porcelain` ihn
    # als EINEN Eintrag "tests/", und der Fremdfilter erklaerte dann (bewusst
    # konservativ, BL-114) auch die eigene neue Datei darin fuer fremd. Der
    # Test pruefte dann eine Ordner-Eigenheit statt der Unterscheidung, um die
    # es hier geht.
    (repo / "tests" / "test_bestand.py").write_text(
        "def test_bestand(): pass\n", encoding="utf-8")
    (repo / "team" / schale.lib_name).write_bytes(schale.kit_lib.read_bytes())
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "start")
    return repo


def _eigene_pfade(repo, schale, schritte):
    """`team_eigene_pfade` NACH `team_guard_begin`, in EINEM Prozess.

    Der Schnappschuss liegt in Shell-Variablen (siehe conftest-Kopf); ein
    zweiter Prozess saehe ihn leer und spraeche jeden Pfad frei — der Test
    waere gruen und wertlos.
    """
    ergebnis = schale.lauf(
        [Ruf("team_guard_begin"), *schritte,
         Ausgabe("team_eigene_pfade", "plans/beutebuch.md", "tests/")],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)
    return ergebnis, [z.strip() for z in ergebnis.stdout.splitlines() if z.strip()]


def test_fremde_untracked_datei_gehoert_nicht_zum_sweep(tmp_path, schale):
    """Der Anlassfall: fremder Reproducer, untracked, vor dem Rollenstart."""
    repo = _repo(tmp_path, schale)
    (repo / "tests" / "test_fremd_reproducer.py").write_text(
        FREMD, encoding="utf-8")

    ergebnis, pfade = _eigene_pfade(repo, schale, [
        Schreib("tests/test_hm7_eigener.py", "def test_hm7(): pass\n"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "tests/test_fremd_reproducer.py" not in pfade, (
        "Die fremde Datei steht in der Liste der zu stagenden Pfade — sie "
        "landet damit unter der Sweep-Botschaft, also unter einer "
        "Urheberschaft, die nicht stimmt (BL-206).\n"
        f"Liste war: {pfade}")
    # Beide Richtungen in EINEM Lauf: Ein Filter, der schlicht alles
    # aussortiert, waere sonst gruen.
    assert "tests/test_hm7_eigener.py" in pfade, (
        "Der eigene Reproducer fehlt — der Fix waere gruen geworden, indem "
        f"gar nichts mehr committet wird. Liste war: {pfade}")


def test_der_uebersprung_wird_gemeldet_statt_verschwiegen(tmp_path, schale):
    """Ein stilles Auslassen waere die Fehlerrichtung von BL-160: Wer den
    Sweep-Commit liest, soll wissen, dass hier fremde Arbeit lag."""
    repo = _repo(tmp_path, schale)
    (repo / "tests" / "test_fremd_reproducer.py").write_text(
        FREMD, encoding="utf-8")

    ergebnis, _ = _eigene_pfade(repo, schale, [
        Schreib("tests/test_hm7_eigener.py", "def test_hm7(): pass\n"),
    ])

    assert "tests/test_fremd_reproducer.py" in ergebnis.stderr, (
        "Der Uebersprung muss auf stderr genannt werden — sonst ist er von "
        "'da war nichts' nicht zu unterscheiden.\n" + ergebnis.stderr)
    assert "BL-206" in ergebnis.stderr, (
        "Die Meldung muss die Fundnummer nennen, sonst sucht der Mensch die "
        "Vorgeschichte.")


def test_eigener_reproducer_bleibt_teil_des_sweeps(tmp_path, schale):
    """Die eigentliche Absicherung. Ohne sie waere ein Filter, der ALLES
    aussortiert, ein gruener Weg — und der Sweep haette aufgehoert, seinen
    Beitrag zu committen."""
    repo = _repo(tmp_path, schale)

    ergebnis, pfade = _eigene_pfade(repo, schale, [
        Schreib("tests/test_hm7_eigener.py", "def test_hm7(): pass\n"),
        Schreib("plans/beutebuch.md", "# Beutebuch\n\n### HM-7 — Fund\n"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "tests/test_hm7_eigener.py" in pfade, (
        f"Der eigene Reproducer fehlt in der Liste: {pfade}")
    assert "plans/beutebuch.md" in pfade, (
        f"Die eigene Beutebuch-Zeile fehlt in der Liste: {pfade}")


def test_ein_sauberer_baum_ergibt_eine_leere_liste(tmp_path, schale):
    """Kein Fund, keine Aenderung: nichts zu stagen — und kein Commit."""
    repo = _repo(tmp_path, schale)
    ergebnis, pfade = _eigene_pfade(repo, schale, [])
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert pfade == [], f"erwartet leer, war: {pfade}"


def test_untracked_ordner_wird_bis_zur_datei_aufgeloest(tmp_path, schale):
    """`git status --porcelain` meldet einen untracked ORDNER als EINEN
    Eintrag mit Schraegstrich. Wer den staged, hat wieder den Ordner
    adressiert statt der Datei — der Fix waere keiner. Deshalb
    `--untracked-files=all`."""
    repo = _repo(tmp_path, schale)
    ergebnis, pfade = _eigene_pfade(repo, schale, [
        Schreib("tests/unterordner/test_hm8_tief.py", "def test_hm8(): pass\n"),
    ])
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "tests/unterordner/test_hm8_tief.py" in pfade, (
        f"der Ordner wurde nicht bis zur Datei aufgeloest: {pfade}")
    assert "tests/unterordner/" not in pfade


# --- (2) Derselbe Fall am echten Sweep ---------------------------------------
# Die Bibliotheksfunktion kann richtig sein und trotzdem nicht aufgerufen
# werden. Diese Haelfte faehrt die WIRKLICHE Bedienoberflaeche und liest den
# echten Commit aus dem Repo.


def _konfig(schluessel):
    return subprocess.run(
        [BASH, "-c",
         f'source "{WURZEL}/team.config.sh"; printf "%s" "${schluessel}"'],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace").stdout


def _sweep_fixture(tmp_path, stub_body):
    if not HARRY.is_file():
        pytest.skip("harry.sh liegt nur in der INSTALLIERTEN Ablage "
                    "(im Kit unter bash/entry/) — geprueft wird via kit-test.sh")
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(HARRY, repo / "harry.sh")
    shutil.copy(WURZEL / "team.config.sh", repo / "team.config.sh")
    kopiere_team_namensraum(repo / "team")
    beutebuch = _konfig("TEAM_BEUTEBUCH")
    tests = _konfig("TEAM_TEST_ORDNER")
    for ordner in (_konfig("TEAM_PLAN_ORDNER"), tests,
                   _konfig("TEAM_PRODUKTIVCODE")):
        (repo / ordner).mkdir(parents=True, exist_ok=True)
    shutil.copy(WURZEL / beutebuch, repo / beutebuch)
    (repo / _konfig("TEAM_PRODUKTIVCODE") / "app.py").write_text(
        "print('hallo')\n", encoding="utf-8")
    # Getrackter Bestand im Testordner — siehe Begruendung in _repo().
    (repo / tests / "test_bestand.py").write_text(
        "def test_bestand(): pass\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@localhost"],
                   ["config", "user.name", "Test"], ["add", "-A"],
                   ["commit", "-qm", "fixture"]):
        subprocess.run(["git", "-C", str(repo)] + befehl, check=True,
                       capture_output=True)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    ergebnis = json.dumps({
        "subtype": "success", "is_error": False, "total_cost_usd": 1.5,
        "result": "fertig <promise>REDTEAM_SWEEP_COMPLETE</promise>"})
    naechste = subprocess.run(
        [sys.executable, "team/tools/beutebuch.py", "next-id"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace").stdout.strip()
    nr = int(naechste.split("-")[-1] or 1)
    stub = bin_dir / "claude"
    stub.write_text("#!/usr/bin/env bash\n"
                    + stub_body.format(tests=tests, beutebuch=beutebuch, nr=nr)
                    + f"\ncat <<'JSON'\n{ergebnis}\nJSON\n", encoding="utf-8")
    stub.chmod(0o755)
    return repo, bin_dir, tests, beutebuch


def _sweep(tmp_path, stub_body, fremd_datei=None):
    repo, bin_dir, tests, beutebuch = _sweep_fixture(tmp_path, stub_body)
    if fremd_datei:
        (repo / fremd_datei).parent.mkdir(parents=True, exist_ok=True)
        (repo / fremd_datei).write_text(FREMD, encoding="utf-8")
    env = dict(os.environ)
    env.update({"PATH": pfad_voran(bin_dir, env), "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    lauf = subprocess.run(entrypoint_aufruf("./harry.sh"), cwd=repo, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    committet = subprocess.run(
        ["git", "-C", str(repo), "show", "--name-only", "--pretty=format:"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace").stdout.split()
    return repo, lauf, committet, tests, beutebuch


NUR_BASH = pytest.mark.nur_bash(
    "Faehrt den bash-Entrypoint harry.sh Ende-zu-Ende. Die Bibliotheksseite "
    "desselben Funds laeuft oben auf BEIDEN Bahnen; das pwsh-Gegenstueck des "
    "Sweeps ruft dieselbe Funktion an derselben Stelle.")


@NUR_BASH
def test_sweep_committet_die_fremde_datei_nicht(tmp_path):
    """Der Feldfall am laufenden Sweep: fremder Reproducer untracked im
    Testordner, der Sweep legt seinen eigenen daneben."""
    tests = _konfig("TEAM_TEST_ORDNER")
    repo, lauf, committet, tests, _ = _sweep(
        tmp_path,
        'printf "def test_hm{nr}(): pass\n" > "{tests}test_hm{nr}_eigen.py"',
        fremd_datei=f"{tests}test_fremd_reproducer.py")
    assert lauf.returncode == 0, lauf.stderr
    fremd = f"{tests}test_fremd_reproducer.py"
    assert fremd not in committet, (
        "Die fremde Datei steht im Sweep-Commit — unter einer Urheberschaft, "
        f"die nicht stimmt (BL-206). Committet wurde: {committet}")
    assert (repo / fremd).read_text(encoding="utf-8") == FREMD, (
        "Die fremde Datei muss unangetastet im Baum liegen bleiben.")


@NUR_BASH
def test_sweep_committet_den_eigenen_reproducer_weiterhin(tmp_path):
    """Die Gegenprobe, ohne die der Fix keiner ist: Der Sweep SOLL seine
    Reproducer committen — genau das ist sein Beitrag."""
    tests = _konfig("TEAM_TEST_ORDNER")
    repo, lauf, committet, tests, _ = _sweep(
        tmp_path,
        'printf "def test_hm{nr}(): pass\\n" > "{tests}test_hm{nr}_eigen.py"',
        fremd_datei=f"{tests}test_fremd_reproducer.py")
    assert lauf.returncode == 0, lauf.stderr
    eigen = [p for p in committet if p.startswith(tests) and "eigen" in p]
    assert eigen, (
        "Der eigene Reproducer fehlt im Sweep-Commit — der Fix ist gruen "
        f"geworden, indem gar nichts mehr committet wird. Committet: {committet}")


@NUR_BASH
def test_sweep_committet_die_beutebuch_zeile_weiterhin(tmp_path):
    """Zweite Gegenprobe: die Beutebuch-Zeile der Rolle."""
    fund = ("\n### HM-{nr} — Testfund\n"
            "- **Angreifer**: Harry\n- **Schweregrad**: klein\n"
            "- **Status**: an Frank übergeben\n- **Reproschritte**: 1. …\n"
            "- **Erwartung**: …\n- **Realität**: …\n"
            "- **Reproducer-Test**: `tests/test_hm{nr}_stichwort.py`\n")
    repo, lauf, committet, _, beutebuch = _sweep(
        tmp_path, "cat >> {beutebuch} <<'EOF'" + fund + "EOF",
        fremd_datei=None)
    assert lauf.returncode == 0, lauf.stderr
    assert beutebuch in committet, (
        f"Die Beutebuch-Zeile fehlt im Sweep-Commit: {committet}")


# --- (3) Solange Befund 2 offen ist: die Handregel steht in der Vorlage -------


def test_die_vorlage_warnt_vor_handarbeit_waehrend_eines_laufs():
    """Befund 2 der Meldung ist eine Entwurfsfrage und liegt als Frage bei:
    Ein Pfad, den es beim Rollenstart nicht gab, faellt im Rollback IMMER in
    den Loesch-Zweig — auch wenn er inzwischen committet ist. Solange das
    offen ist, gehoert die Handregel in die Vorlage und nicht ins Feld:
    `--update` schreibt `TEAM.md` neu (BL-58), eine nur lokal notierte Regel
    ist beim naechsten Update still weg.
    """
    for kandidat in (WURZEL / "TEAM.md", WURZEL / "bootstrap" / "TEAM.md"):
        if kandidat.is_file():
            text = kandidat.read_text(encoding="utf-8")
            break
    else:
        pytest.skip("TEAM.md liegt weder installiert noch unter bootstrap/")
    assert "Während ein Lauf läuft" in text, (
        "TEAM.md sagt nicht, dass Handarbeit waehrend eines Laufs in diesem "
        "Arbeitsbaum nichts zu suchen hat (BL-206, Befund 2).")
    assert "auch wenn du es committet hast" in text, (
        "Der Kern des Befunds fehlt: Ein Commit WAEHREND des Laufs schuetzt "
        "nicht. Ohne diesen Satz liest sich der Abschnitt wie eine Wiederholung "
        "von 'zuerst committen'.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

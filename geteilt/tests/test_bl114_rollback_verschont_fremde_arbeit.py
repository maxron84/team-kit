#!/usr/bin/env python3
"""BL-114 — der Rollback eines Rollenlaufs darf nur die eigene Arbeit treffen.

`frank.sh` (und `frank.ps1`) rollten auf ZWEI Pfaden — Session-Limit und
Fehlversuch — mit einem unbeschraenkten `git reset --hard "$START_HASH"` plus
`git clean -fd` zurueck. `axel` und `redteam` hatten ihren `git clean` zwar auf
Test-/Plan-Ordner eingeschraenkt, ihr `git reset --hard` daneben aber nicht.

Der Kopf des Read-Only-Guards in der Bibliothek beschreibt woertlich die
Gegenregel: "Bei Verletzung wird NUR jeder einzelne Verletzer-Pfad
zurueckgesetzt — niemals blanko `git reset --hard`/`clean -fd`. (Lektion
2026-07-10: ein blindes reset+clean loeschte einmal die gesamte uncommittete
Team-Infrastruktur. Nie wieder.)" Die Lehre war also am GUARD angewandt und am
AUFRUFER nicht — `team_guard_verify` arbeitet chirurgisch und kennt seit BL-16
sogar den Ausgangszustand des Arbeitsbaums, waehrend zwei Zeilen weiter alles
weggeworfen wurde, was der Guard gerade geschont hatte.

Betroffen war jede uncommittete Arbeit im Zielprojekt, nicht nur die der
Rolle: eine parallele Sitzung, eine Handaenderung, eine noch nicht committete
Closeout-Ausgabe des Architekten.

Der Test faehrt beide Haelften, und das ist Absicht:

  * Die SCHONUNG (fremde Aenderung, fremde neue Datei, Laufzeitartefakte
    ueberleben) — dafuer wurde der Fix gebaut.
  * Die WIRKSAMKEIT (eigener Commit, eigene Aenderung, eigene neue Datei,
    eigene Loeschung sind zurueckgenommen) — ohne sie waere ein Rollback, der
    gar nichts tut, ein gruener Weg. Genau so entsteht die naechste Lehre.

Alles gegen ein temporaeres Wegwerf-Repo, nie gegen den echten Arbeitsbaum.
"""
import subprocess
from pathlib import Path

import pytest

from conftest import Git, Loeschen, Ordner, Ruf, Schreib

FREMD_INHALT = "Arbeit einer parallelen Sitzung\n"
ORIGINAL = "original\n"


def _git(repo, *args):
    ergebnis = subprocess.run(["git", *args], cwd=str(repo),
                              capture_output=True, text=True)
    assert ergebnis.returncode == 0, ergebnis.stderr
    return ergebnis.stdout.strip()


def _repo(tmp_path, schale):
    """Wegwerf-Repo mit Produktivcode, Plan-Ordner und einer Fremddatei."""
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "plans").mkdir()
    (repo / "src" / "app.py").write_text(ORIGINAL, encoding="utf-8")
    (repo / "src" / "hilf.py").write_text(ORIGINAL, encoding="utf-8")
    (repo / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (repo / "team").mkdir()
    (repo / "team" / schale.lib_name).write_bytes(schale.kit_lib.read_bytes())
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "start")
    return repo


def _lauf(repo, schale, schritte):
    start = _git(repo, "rev-parse", "HEAD")
    ergebnis = schale.lauf(
        [Ruf("team_guard_begin"), *schritte,
         Ruf("team_rollback_rolle", "frank", start)],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)
    return start, ergebnis


# ------------------------------------------------------------------ Schonung
def test_fremde_uncommittete_aenderung_ueberlebt(tmp_path, schale):
    """Der Anlassfall: eine Datei, die beim Rollenstart schon schmutzig war."""
    repo = _repo(tmp_path, schale)
    (repo / "CHANGELOG.md").write_text(FREMD_INHALT, encoding="utf-8")

    start, ergebnis = _lauf(repo, schale, [
        Schreib("src/app.py", "fix der rolle\n"),
        Git("add", "-A"),
        Git("commit", "-q", "-m", "fix(uat): HM-1"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert (repo / "CHANGELOG.md").read_text(encoding="utf-8") == FREMD_INHALT, (
        "Die fremde uncommittete Arbeit wurde vom Rollback verworfen — genau "
        "der Verlust, gegen den BL-114 gebaut wurde."
    )


def test_fremde_neue_datei_ueberlebt(tmp_path, schale):
    """Die Closeout-Ausgabe des Architekten liegt untracked im Baum."""
    repo = _repo(tmp_path, schale)
    (repo / "plans" / "kaskade-39-abschluss.md").write_text(
        FREMD_INHALT, encoding="utf-8")

    start, ergebnis = _lauf(repo, schale, [
        Schreib("src/app.py", "fix der rolle\n"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    akte = repo / "plans" / "kaskade-39-abschluss.md"
    assert akte.is_file(), "Die fremde neue Datei wurde entfernt."
    assert akte.read_text(encoding="utf-8") == FREMD_INHALT


def test_laufzeitartefakte_ueberleben(tmp_path, schale):
    """BL-24/BL-4: In .team-logs liegen die Kostenlogs DIESES Aufrufs. Sie zu
    loeschen waere ein selbstverschuldeter Verlust der Kostenhistorie —
    ausgeloest ausgerechnet vom Aufraeumer."""
    repo = _repo(tmp_path, schale)
    (repo / ".team-logs").mkdir()
    (repo / ".team-logs" / "frank.json").write_text('{"x":1}', encoding="utf-8")

    start, ergebnis = _lauf(repo, schale, [
        Schreib("src/app.py", "fix der rolle\n"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert (repo / ".team-logs" / "frank.json").is_file(), (
        "Das Kostenlog des laufenden Aufrufs wurde geloescht."
    )


# --------------------------------------------------------------- Wirksamkeit
def test_eigener_commit_wird_zurueckgenommen(tmp_path, schale):
    repo = _repo(tmp_path, schale)

    start, ergebnis = _lauf(repo, schale, [
        Schreib("src/app.py", "fix der rolle\n"),
        Git("add", "-A"),
        Git("commit", "-q", "-m", "fix(uat): HM-1"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert _git(repo, "rev-parse", "HEAD") == start, (
        "HEAD steht nicht mehr auf dem Startstand — der Commit der Rolle lebt."
    )
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == ORIGINAL, (
        "Die committete Aenderung der Rolle steht weiter im Baum."
    )


def test_eigene_neue_datei_wird_entfernt(tmp_path, schale):
    """Auch AUSSERHALB des Produktivordners — die Reichweite von HM-29, die
    `git clean -fd` ohne Pfadeinschraenkung hatte."""
    repo = _repo(tmp_path, schale)

    start, ergebnis = _lauf(repo, schale, [
        Schreib("src/neu.py", "neu\n"),
        Schreib("wegwerf-sonde.py", "sonde\n"),
        Ordner("wegwerf-ordner"),
        Schreib("wegwerf-ordner/inhalt.txt", "x\n"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert not (repo / "src" / "neu.py").exists()
    assert not (repo / "wegwerf-sonde.py").exists(), (
        "Eine neue Datei ausserhalb des Produktivordners hat den Rollback "
        "ueberlebt — die HM-29-Reichweite ist verloren gegangen."
    )
    assert not (repo / "wegwerf-ordner").exists(), (
        "BL-24: Ein untracked VERZEICHNIS wird als EIN Eintrag gemeldet und "
        "muss rekursiv verschwinden."
    )


def test_eigene_loeschung_wird_wiederhergestellt(tmp_path, schale):
    """Ein Rollback, der nur wegnimmt, ist keiner."""
    repo = _repo(tmp_path, schale)

    start, ergebnis = _lauf(repo, schale, [
        Loeschen("src/hilf.py"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert (repo / "src" / "hilf.py").is_file(), (
        "Die von der Rolle geloeschte Datei ist nicht zurueckgekommen."
    )
    assert (repo / "src" / "hilf.py").read_text(encoding="utf-8") == ORIGINAL


# ------------------------------------------------- beides im selben Lauf
def test_schonung_und_wirksamkeit_gleichzeitig(tmp_path, schale):
    """Der realistische Fall: fremde Arbeit UND eigener Fehlversuch im selben
    Baum. Nur hier faellt auf, wenn die Trennung nur einzeln funktioniert."""
    repo = _repo(tmp_path, schale)
    (repo / "CHANGELOG.md").write_text(FREMD_INHALT, encoding="utf-8")
    (repo / "plans" / "closeout.md").write_text(FREMD_INHALT, encoding="utf-8")

    start, ergebnis = _lauf(repo, schale, [
        Schreib("src/app.py", "fix der rolle\n"),
        Schreib("src/neu.py", "neu\n"),
        Git("add", "-A"),
        Git("commit", "-q", "-m", "fix(uat): HM-1"),
    ])

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert (repo / "CHANGELOG.md").read_text(encoding="utf-8") == FREMD_INHALT
    assert (repo / "plans" / "closeout.md").read_text(encoding="utf-8") == FREMD_INHALT
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == ORIGINAL
    assert not (repo / "src" / "neu.py").exists()
    assert _git(repo, "rev-parse", "HEAD") == start


# ------------------------------------------------- kein blanker Rollback mehr
@pytest.mark.parametrize("skript", [
    "bash/entry/frank.sh", "bash/entry/axel.sh", "bash/redteam.sh",
    "pwsh/entry/frank.ps1", "pwsh/entry/axel.ps1", "pwsh/redteam.ps1",
])
def test_kein_einstiegsskript_rollt_mehr_blanko_zurueck(skript):
    """Der Waechter gegen den Rueckfall — und gegen die halbe Reparatur.

    Der Eintrag nannte urspruenglich nur `frank.sh`; betroffen waren beide
    Bahnen und drei Rollen. Ein Fix in einer Fassung erzeugt genau die Drift,
    vor der BL-112 warnt, deshalb steht hier jede Datei einzeln.
    """
    wurzel = Path(__file__).resolve().parents[2]
    name = Path(skript).name
    # Drei Ablagen, nicht zwei: Im Kit steht der Pfad wie oben angegeben
    # (bash/, pwsh/). Im installierten Projekt liegen die Entrypoints flach
    # in der Wurzel, lib und redteam aber unter team/ — genau diese dritte
    # Moeglichkeit fehlte hier und liess zwei Faelle STILL uebersprungen
    # durchgehen, statt sie zu pruefen.
    for kandidat in (wurzel / skript, wurzel / name, wurzel / "team" / name):
        if kandidat.is_file():
            pfad = kandidat
            break
    else:
        pytest.skip(f"{skript} liegt in dieser Ablage nicht vor")
    for zeile in pfad.read_text(encoding="utf-8-sig").splitlines():
        rumpf = zeile.strip()
        if rumpf.startswith("#"):               # Kommentare duerfen es nennen
            continue
        assert "reset --hard" not in rumpf, (
            f"{skript}: blanker Rollback wieder eingezogen — {rumpf}"
        )
        assert "clean -fd" not in rumpf, (
            f"{skript}: pauschales Aufraeumen wieder eingezogen — {rumpf}"
        )


# ---------------------------------------------------- der ganze Lauf, echt
def test_frank_lauf_verschont_fremde_arbeit(tmp_path):
    """Der Fall aus dem Feld, end-to-end: `frank.sh` mit gestubbter CLI.

    Die Bibliotheksfunktion oben ist bewiesen — dass das EINSTIEGSSKRIPT sie
    auch aufruft, ist eine zweite Aussage. Genau dort lag der Fehler: Der
    Guard arbeitete chirurgisch, der Aufrufer zwei Zeilen weiter nicht.

    Erzwungen wird der Fehlversuchspfad, indem der Stub eine gueltige
    Kostenantwort OHNE Promise liefert — Frank findet dann weder Promise noch
    Commit, zaehlt den Versuch und rollt zurueck.

    Nur Bash und nur in der INSTALLIERTEN Ablage: `frank.sh` liegt im Kit
    unter `entry/` und ist dort ohne Installation nicht lauffaehig; gefahren
    wird der Fall in `kit-test.sh`.
    """
    import json
    import os
    import shutil

    wurzel = Path(__file__).resolve().parents[2]
    frank = wurzel / "frank.sh"
    if not frank.is_file():
        pytest.skip("frank.sh liegt nur in der INSTALLIERTEN Ablage "
                    "(im Kit unter bash/entry/ bzw. pwsh/entry/) — geprueft wird via kit-test.sh")

    def konfig(schluessel):
        return subprocess.run(
            ["bash", "-c",
             f'source "{wurzel}/team.config.sh"; printf "%s" "${schluessel}"'],
            capture_output=True, text=True).stdout

    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(frank, repo / "frank.sh")
    shutil.copy(wurzel / "team.config.sh", repo / "team.config.sh")
    shutil.copytree(wurzel / "team", repo / "team")
    beutebuch = konfig("TEAM_BEUTEBUCH")
    produktiv = konfig("TEAM_PRODUKTIVCODE")
    (repo / produktiv).mkdir(parents=True, exist_ok=True)
    (repo / produktiv / "app.py").write_text(ORIGINAL, encoding="utf-8")
    (repo / beutebuch).parent.mkdir(parents=True, exist_ok=True)
    (repo / beutebuch).write_text(
        "# Beutebuch\n\n## Funde\n\n"
        "### HM-1 — Beispielfund\n"
        "- **Angreifer**: Harry\n"
        "- **Status**: an Frank übergeben\n"
        "- **Reproducer-Test**: `tests/test_hm1_x.py`\n"
        f"- Betrifft `{produktiv}/app.py`\n",
        encoding="utf-8")
    (repo / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@localhost"],
                   ["config", "user.name", "Test"], ["add", "-A"],
                   ["commit", "-qm", "fixture"]):
        subprocess.run(["git", "-C", str(repo)] + befehl, check=True)

    # Die unbeteiligte uncommittete Arbeit — beide Bauarten aus dem Feldfall.
    (repo / "CHANGELOG.md").write_text(FREMD_INHALT, encoding="utf-8")
    (repo / "kaskade-39-abschluss.md").write_text(FREMD_INHALT, encoding="utf-8")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "claude"
    antwort = json.dumps({"subtype": "success", "is_error": False,
                          "total_cost_usd": 0.1,
                          "result": "ich habe nichts geschafft"})
    stub.write_text(f"#!/usr/bin/env bash\ncat <<'JSON'\n{antwort}\nJSON\n",
                    encoding="utf-8")
    stub.chmod(0o755)

    env = dict(os.environ)
    env.update({"PATH": f"{bin_dir}:{env['PATH']}", "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    lauf = subprocess.run(["./frank.sh"], cwd=repo, env=env,
                          capture_output=True, text=True)

    assert lauf.returncode == 1, (
        f"erwartet war der Fehlversuchspfad (Exit 1), kam {lauf.returncode}:\n"
        f"{lauf.stdout}\n{lauf.stderr}"
    )
    assert "Rollback" in lauf.stderr, "der Rollback-Pfad wurde nicht genommen"
    assert (repo / "CHANGELOG.md").read_text(encoding="utf-8") == FREMD_INHALT, (
        "Die uncommittete fremde Änderung an CHANGELOG.md hat den Fehlversuch "
        "NICHT ueberlebt — das ist der Feldfall, wegen dem BL-114 entstand."
    )
    assert (repo / "kaskade-39-abschluss.md").is_file(), (
        "Die uncommittete Closeout-Datei wurde vom Rollback entfernt."
    )

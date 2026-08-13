#!/usr/bin/env python3
"""Fixture-Test fuer die Bedienoberflaeche `team-status.sh --akteur-abschluss`
(BL-33, Kaskade 15/Stufe 51).

Stufe 50 hat den Python-Kern (`kosten.py akteur-abschluss`) rollen-agnostisch
gemacht (siehe test_stufe50_akteur_abschluss.py). Stufe 51 legt die
Bedienoberflaeche obendrauf: `team-status.sh --akteur-abschluss <rolle>
<auth> <USD> <domaene> ["<notiz>"]` reicht die Werte ueber den neuen
team/lib.sh-Wrapper `team_akteur_abschluss` als eigene argv-Elemente durch
(kein `python3 -c` mit roher Interpolation — BL-23/HM-17).

Netz-/CLI-frei: team-status.sh/team/lib.sh/team/tools/kosten.py werden in ein
temporaeres Arbeitsverzeichnis kopiert und dort gegen ein isoliertes
Fixture-".budget-ledger" ausgefuehrt (kein Bezug zur echten .budget-ledger
des Repos, kein echter Claude-Aufruf).
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel

sys.path.insert(0, str(REPO_ROOT / "team" / "tools"))
import kosten  # noqa: E402

import os as _os
_dom = _os.environ.get("TEAM_DOMAENEN", "").replace(",", " ").split()
DOMAENE = _dom[0] if _dom else "produkt"   # Starterkit: projektneutral



def _fixture_repo(tmp_path):
    """Kopiert die drei benoetigten Dateien in ein isoliertes Arbeitsverzeichnis
    und legt ein leeres Fixture-Ledger an. team-status.sh macht `cd
    "$(dirname "$0")"`, daher muss team/tools/kosten.py als Geschwister-Unterordner
    mitkopiert werden."""
    (tmp_path / "team" / "tools").mkdir(parents=True)
    shutil.copy(REPO_ROOT / "team-status.sh", tmp_path / "team-status.sh")
    shutil.copy(REPO_ROOT / "team" / "lib.sh", tmp_path / "team" / "lib.sh")
    shutil.copy(REPO_ROOT / "team" / "tools" / "kosten.py",
                tmp_path / "team" / "tools" / "kosten.py")
    # team.config.sh mit neutralen Werten — lib.sh sourct sie aus ../
    (tmp_path / "team.config.sh").write_text(
        'TEAM_BEUTEBUCH_TOOL="python3 team/tools/beutebuch.py"\n'
        'TEAM_KOSTEN_TOOL="python3 team/tools/kosten.py"\n'
        f'TEAM_DOMAENEN="{DOMAENE} team"\nexport TEAM_DOMAENEN\n')
    (tmp_path / ".budget-ledger").write_text(
        "# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    (tmp_path / ".ralph-plan").write_text(
        "plans/ralph-kaskade-15-akteur-kosten.md\n")
    return tmp_path


def _run(tmp_path, *args):
    result = subprocess.run(
        ["bash", "./team-status.sh", "--akteur-abschluss", *args],
        cwd=tmp_path, capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def test_vollstaendiger_aufruf_traegt_korrekte_zeile_ein(tmp_path):
    repo = _fixture_repo(tmp_path)
    rc, out, err = _run(repo, "frank", "abo", "12.34", DOMAENE, "Fix-Serie K15")
    assert rc == 0, err
    assert "angelegt" in out

    ledger = repo / ".budget-ledger"
    zeilen = list(kosten.ledger_zeilen(str(ledger)))
    frank_zeilen = [z for z in zeilen if z["rolle"] == "frank"]
    assert len(frank_zeilen) == 1
    assert frank_zeilen[0]["usd"] == 12.34
    assert frank_zeilen[0]["auth"] == "abo"
    assert frank_zeilen[0]["domaene"] == DOMAENE
    assert frank_zeilen[0]["kaskade"] == "15"
    assert frank_zeilen[0]["notiz"] == "Fix-Serie K15"


def test_zweiter_aufruf_ersetzt_statt_verdoppelt(tmp_path):
    repo = _fixture_repo(tmp_path)
    _run(repo, "frank", "abo", "10", DOMAENE, "erster Versuch")
    rc, out, err = _run(repo, "frank", "abo", "15.5", DOMAENE, "korrigiert")
    assert rc == 0, err
    assert "ersetzt" in out

    ledger = repo / ".budget-ledger"
    frank_zeilen = [z for z in kosten.ledger_zeilen(str(ledger)) if z["rolle"] == "frank"]
    assert len(frank_zeilen) == 1
    assert frank_zeilen[0]["usd"] == 15.5


def test_aufruf_ohne_notiz_funktioniert(tmp_path):
    repo = _fixture_repo(tmp_path)
    rc, out, err = _run(repo, "frank", "api", "3.5", "team")
    assert rc == 0, err
    assert "angelegt" in out


def test_fehlende_argumente_zeigen_nutzungshinweis_und_aendern_ledger_nicht(tmp_path):
    repo = _fixture_repo(tmp_path)
    inhalt = (repo / ".budget-ledger").read_text()
    rc, _out, err = _run(repo, "frank", "abo")
    assert rc != 0
    assert "Nutzung" in err
    assert "--akteur-abschluss" in err
    assert (repo / ".budget-ledger").read_text() == inhalt


def test_ohne_jegliche_argumente_zeigt_nutzungshinweis(tmp_path):
    repo = _fixture_repo(tmp_path)
    inhalt = (repo / ".budget-ledger").read_text()
    rc, _out, err = _run(repo)
    assert rc != 0
    assert "Nutzung" in err
    assert (repo / ".budget-ledger").read_text() == inhalt


if __name__ == "__main__":
    failures = []
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                try:
                    fn(Path(td))
                    print(f"OK   {name}")
                except AssertionError as e:
                    failures.append(name)
                    print(f"FAIL {name}: {e}")
    if failures:
        sys.exit(1)
    print("gruen — BL-33 (Stufe 51) verifiziert: team-status.sh --akteur-abschluss korrekt.")

#!/usr/bin/env python3
"""Fixture-Test fuer die A2-Live-Schaetzung der Architekt-Kosten (BL-28,
Kaskade 13/Stufe 42).

Der Architekt laeuft interaktiv ausserhalb von team_claude und schreibt keine
total_cost_usd-JSONs -- anders als Ralph/Frank/Axel/Harry/Marv gibt es fuer ihn
also keine geloggte Kostenbasis. Proxy: Zeilen-Churn (git diff --numstat) ueber
plans/** + CLAUDE.md seit einer Referenz, multipliziert mit dem dokumentierten
Eichfaktor ARCHITEKT_USD_PRO_CHURN_ZEILE (team/tools/kosten.py). Bewusst eine grobe
Groessenordnung -- Stufe 43 ersetzt sie beim Kaskaden-Abschluss durch den
echten Konsolenwert.

Netz-frei, aber CLI-lastig: baut ein eigenes temporaeres Git-Repo mit
bekanntem Churn auf (kein Bezug zum echten website-maxron-de-Repo) und ruft
team/tools/kosten.py per subprocess dagegen auf.
"""
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = kit_pfad("tools", "kosten.py")

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def _bauen_fixture_repo(tmp_path):
    repo = tmp_path / "fixture-repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")

    (repo / "plans").mkdir()
    (repo / "CLAUDE.md").write_text("Zeile 1\nZeile 2\n")
    (repo / "plans" / "foo.md").write_text("Plan-Zeile 1\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "initial")
    ref = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
        check=True,
    ).stdout.strip()

    # bekannter Churn: CLAUDE.md +2/-1 (Zeile 2 ersetzt, Zeile 3 neu) = 3,
    # plans/foo.md +2 (zwei neue Zeilen) = 2 -> Gesamt-Churn 5.
    (repo / "CLAUDE.md").write_text("Zeile 1\nZeile 2 geaendert\nZeile 3\n")
    (repo / "plans" / "foo.md").write_text("Plan-Zeile 1\nPlan-Zeile 2\nPlan-Zeile 3\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "aenderung")

    return repo, ref


def _run_schaetzung(repo, ref, *extra_args):
    result = subprocess.run(
        [sys.executable, str(KOSTEN_PY), "architekt-schaetzung",
         "--since", ref, "--repo", str(repo), *extra_args],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def test_schaetzung_ist_churn_mal_eichfaktor(tmp_path):
    repo, ref = _bauen_fixture_repo(tmp_path)
    rc, out, _ = _run_schaetzung(repo, ref, "plans", "CLAUDE.md")
    assert rc == 0
    erwartet = 5 * kosten.ARCHITEKT_USD_PRO_CHURN_ZEILE
    # CLI rundet auf 4 Nachkommastellen (":.4f") -> Toleranz statt Exaktheit.
    assert abs(float(out) - erwartet) < 5e-5


def test_git_churn_direkt_exakt_reproduzierbar(tmp_path):
    repo, ref = _bauen_fixture_repo(tmp_path)
    churn, usd = kosten.architekt_schaetzung(ref, pfade=("plans", "CLAUDE.md"),
                                              repo=str(repo))
    assert churn == 5
    assert usd == 5 * kosten.ARCHITEKT_USD_PRO_CHURN_ZEILE


def test_ohne_since_bricht_sauber_ab(tmp_path):
    repo, _ref = _bauen_fixture_repo(tmp_path)
    rc, _out, err = _run_schaetzung(repo, "")
    assert rc == 1
    assert "since" in err.lower()


def test_ungueltige_referenz_bricht_sauber_ab(tmp_path):
    repo, _ref = _bauen_fixture_repo(tmp_path)
    rc, _out, err = _run_schaetzung(repo, "nicht-existierende-referenz")
    assert rc == 1
    assert "git diff fehlgeschlagen" in err.lower()


def test_eichprobe_session_churn_mal_faktor_ergibt_16_usd():
    # Dokumentierte Eichbasis (Kommentar in team/tools/kosten.py): Session-Churn
    # 1045 Zeilen * Faktor ~= 16 USD (Toleranz fuer Rundung).
    session_churn = 1045
    ergebnis = session_churn * kosten.ARCHITEKT_USD_PRO_CHURN_ZEILE
    assert abs(ergebnis - 16.0) < 0.01

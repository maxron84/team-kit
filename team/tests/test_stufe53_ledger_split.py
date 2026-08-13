#!/usr/bin/env python3
"""Fixture-Test fuer den Ledger-Abo/API-Split (BL-17-Restpunkt/BL-29-"1b",
Kaskade 16/Stufe 53).

`kosten.py ledger --split` und der `team/lib.sh`-Wrapper `team_ledger_split`
liefern die usd-Spalte der .budget-ledger nach auth-Bucket getrennt
("abo<TAB>api<TAB>gemischt") statt nur der Gesamtsumme. Bucket-Regel: NUR
auth=="abo" zaehlt zu abo, NUR auth=="api" zu api, ALLES andere (v. a.
"abo/api", aber auch Altzeilen ohne auth-Wert) zu gemischt -- damit gilt
immer abo+api+gemischt == ledger_summe() (kein geratener Split, keine
verlorenen Betraege).

Netz-/CLI-frei gegen ein temporaeres Fixture-Ledger (nie die echte
.budget-ledger) -- Muster wie test_stufe44_domaenen_status.py/
test_stufe50_akteur_abschluss.py.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = REPO_ROOT / "team" / "tools" / "kosten.py"
TEAM_LIB = REPO_ROOT / "team" / "lib.sh"

sys.path.insert(0, str(REPO_ROOT / "team" / "tools"))
import kosten  # noqa: E402

FIXTURE_LEDGER = """\
# datum | kaskade | usd | auth | domaene | rolle | notiz
2026-07-10 | 1 | 2.0000 | abo
2026-07-11 | 5 | 3.0000 | abo | team | ralph | reine Abo-Zeile
2026-07-11 | 5 | 1.5000 | api | team | ralph | reine API-Zeile
2026-07-12 | 16 | 4.2500 | abo/api | team | roles | gemischte Rollen-Zeile
2026-07-12 | 16 | 0.7500 | api | website | frank | Website-Fix
"""


def _run(*args):
    result = subprocess.run(
        [sys.executable, str(KOSTEN_PY), *args],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _fixture_ledger(tmp_path, inhalt=FIXTURE_LEDGER):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text(inhalt)
    return pfad


def test_split_summiert_sich_exakt_auf_die_gesamtsumme(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, out, err = _run("ledger", str(ledger), "--split")
    assert rc == 0, err
    abo, api, gemischt = (float(x) for x in out.split("\t"))
    rc2, summe_out, err2 = _run("ledger", str(ledger))
    assert rc2 == 0, err2
    summe = float(summe_out)
    assert round(abo + api + gemischt, 4) == round(summe, 4)


def test_split_buckets_korrekt_zugeordnet(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, out, err = _run("ledger", str(ledger), "--split")
    assert rc == 0, err
    abo, api, gemischt = (float(x) for x in out.split("\t"))
    # reine abo-Zeilen: 2.0 (Altzeile) + 3.0 = 5.0
    assert abo == 5.0
    # reine api-Zeilen: 1.5 + 0.75 = 2.25
    assert api == 2.25
    # abo/api-Zeile (gemischt): 4.25 -- Altzeile hat KEIN auth != "abo"/"api",
    # sie ist "abo" und zaehlt daher bereits oben mit
    assert gemischt == 4.25


def test_altzeile_ohne_auth_wert_landet_in_gemischt(tmp_path):
    ledger = _fixture_ledger(tmp_path, inhalt=(
        "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"
        "2026-07-10 | 1 | 2.0000 | unbekannt\n"
    ))
    rc, out, err = _run("ledger", str(ledger), "--split")
    assert rc == 0, err
    abo, api, gemischt = (float(x) for x in out.split("\t"))
    assert (abo, api, gemischt) == (0.0, 0.0, 2.0)


def test_split_respektiert_domaene_filter(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    rc, out, err = _run("ledger", str(ledger), "--split", "--domaene", "team")
    assert rc == 0, err
    abo, api, gemischt = (float(x) for x in out.split("\t"))
    # team-Zeilen: 3.0 abo, 1.5 api, 4.25 gemischt (Altzeile ohne domaene
    # zaehlt beim gesetzten Filter NICHT mit -- "unzugeordnet")
    assert (abo, api, gemischt) == (3.0, 1.5, 4.25)


def test_ledger_split_python_funktion_direkt(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    abo, api, gemischt = kosten.ledger_split(str(ledger))
    summe = kosten.ledger_summe(str(ledger))
    assert round(abo + api + gemischt, 4) == round(summe, 4)
    assert abo == 5.0
    assert api == 2.25
    assert gemischt == 4.25


def test_team_ledger_split_wrapper(tmp_path):
    ledger = _fixture_ledger(tmp_path)
    result = subprocess.run(
        ["bash", "-c", f'source "{TEAM_LIB}"; team_ledger_split "{ledger}"'],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    abo, api, gemischt = (float(x) for x in result.stdout.strip().split("\t"))
    assert (abo, api, gemischt) == (5.0, 2.25, 4.25)


def test_team_status_budget_kopfzeilen_summieren_sich_auf_gesamt():
    # Rechenprobe gegen das echte Repo (Regressionsschutz, wie in
    # test_stufe44_domaenen_status.py): die drei Kostenzeilen (API + Abo +
    # gemischt) muessen sich exakt auf die "Gesamt"-Zeile summieren.
    result = subprocess.run(
        ["./team-status.sh", "--budget"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    zeilen = {}
    for zeile in result.stdout.splitlines():
        if "real via API abgerechnet" in zeile:
            zeilen["api"] = float(zeile.split(":")[-1].split()[0])
        elif "Abo-Gegenwert" in zeile:
            zeilen["abo"] = float(zeile.split(":")[-1].split()[0])
        elif "gemischt (Ledger" in zeile:
            zeilen["gemischt"] = float(zeile.split(":")[-1].split()[0])
        elif "Gesamt (Basis + laufend)" in zeile:
            zeilen["gesamt"] = float(zeile.split(":")[-1].split()[0])
    assert set(zeilen) == {"api", "abo", "gemischt", "gesamt"}
    assert round(zeilen["api"] + zeilen["abo"] + zeilen["gemischt"], 4) == \
        round(zeilen["gesamt"], 4)

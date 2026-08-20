#!/usr/bin/env python3
"""BL-19: `--rollen-abschluss` schrieb EINE Notiz wortgleich in ZWEI Zeilen
mit verschiedener Bedeutung.

Aus dem Feld zurueckgespielt (platformer, Architekt-Closeout K3, 2026-08-02).
team-status.sh ruft seit BL-4 beide Verben in einer Schleife mit demselben
--notiz auf: `rollen-abschluss` bucht .team-logs (Harry/Marv/Frank/Axel),
`ralph-abschluss` bucht .ralph-logs (Ralphs Baukosten). Es gibt aber nur EINEN
Notiztext, und der beschreibt zwangslaeufig hoechstens eine der beiden Zeilen.
Real:

    --rollen-abschluss 3 produkt "Harry/Marv-Sweeps + Frank HM-6, K3"
    -> roles 2.4085  "Harry/Marv-Sweeps + Frank HM-6, K3"   (richtig)
    -> ralph 6.3851  "Harry/Marv-Sweeps + Frank HM-6, K3"   (vier Baustufen!)

Keine Kosmetik: Die Ledger ist laut CLAUDE.md die maschinelle Wahrheit fuer
ein kalt startendes Architekt-Ich, und dieses Feld ist die einzige Prosa-Spur
je Zeile. Und es ist ein RUECKFALL — genau diese Beschwerde stand schon in
Feld-BL-5 ueber die K1-Zeile; der BL-4-Fix hat sie strukturell wieder
eingebaut.

Strippenzieher-Entscheid 2026-08-02: Vorspann JE ZIELROLLE in kosten.py
("Rollen: …" / "Bau: …"), kein zweiter Bedienparameter — die Bedienung bleibt
einhaendig, und auch der direkte kosten.py-Aufruf bekommt die Zuordnung.

Netz-/CLI-frei gegen temporaere Fixtures — nie die echte .budget-ledger.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, kit_pfad, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = kit_pfad("tools", "kosten.py")
TEAM_LIB = kit_pfad("lib.sh")

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

FELD_NOTIZ = "Harry/Marv-Sweeps + Frank HM-6, K3"


def _entrypoint(name):
    """Wurzel (Installation) oder entry/ (Kit) — siehe BL-6."""
    for kandidat in (REPO_ROOT / name,
                     REPO_ROOT / "bash" / "entry" / name,
                     REPO_ROOT / "pwsh" / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


TEAM_STATUS = _entrypoint("team-status.sh")


def _run(*args):
    ergebnis = subprocess.run(
        [sys.executable, str(KOSTEN_PY), *args], capture_output=True, text=True)
    return ergebnis.returncode, ergebnis.stdout.strip(), ergebnis.stderr.strip()


def _log(verzeichnis, name, usd):
    verzeichnis.mkdir(parents=True, exist_ok=True)
    (verzeichnis / name).write_text(json.dumps({"total_cost_usd": usd}))
    return verzeichnis


def _ledger(tmp_path):
    pfad = tmp_path / "fixture-ledger"
    pfad.write_text("# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    return pfad


def _notiz(ledger, rolle):
    treffer = [z for z in kosten.ledger_zeilen(str(ledger))
               if z["rolle"] == rolle]
    assert len(treffer) == 1, f"genau eine {rolle}-Zeile erwartet: {treffer}"
    return treffer[0]["notiz"]


def test_bau_und_rollenzeile_tragen_verschiedene_vorspaenge(tmp_path):
    """Der Feldfehler: derselbe Text, zweimal, ohne Zuordnung."""
    ledger = _ledger(tmp_path)
    team_logs = _log(tmp_path / "team-logs", "harry.json", 2.4085)
    ralph_logs = _log(tmp_path / "ralph-logs", "stufe-1.json", 6.3851)

    for verb, logs in (("rollen-abschluss", team_logs),
                       ("ralph-abschluss", ralph_logs)):
        rc, _out, err = _run(verb, "--kaskade", "3", "--domaene", "produkt",
                             "--logs", str(logs), "--pfad", str(ledger),
                             "--notiz", FELD_NOTIZ, "--archivieren")
        assert rc == 0, err

    roles_notiz = _notiz(ledger, "roles")
    ralph_notiz = _notiz(ledger, "ralph")

    assert roles_notiz.startswith("Rollen: ")
    assert ralph_notiz.startswith("Bau: ")
    assert roles_notiz != ralph_notiz, (
        "BL-19: Zwei Zeilen mit verschiedener Bedeutung duerfen keine "
        "wortgleiche Herkunftsangabe tragen")
    # Der Text des Menschen bleibt vollstaendig erhalten — der Vorspann
    # ergaenzt ihn, er ersetzt ihn nicht.
    assert FELD_NOTIZ in roles_notiz
    assert FELD_NOTIZ in ralph_notiz


def test_split_hinweis_bleibt_erhalten(tmp_path):
    """Der Vorspann sitzt VOR der Notiz, der Abo/API-Split bleibt hinten —
    sonst faellt eine seit Stufe 54 gelesene Angabe still weg."""
    ledger = _ledger(tmp_path)
    logs = _log(tmp_path / "ralph-logs", "stufe-1.json", 6.3851)
    rc, _out, err = _run("ralph-abschluss", "--kaskade", "3",
                         "--domaene", "produkt", "--logs", str(logs),
                         "--pfad", str(ledger), "--notiz", FELD_NOTIZ)
    assert rc == 0, err
    notiz = _notiz(ledger, "ralph")
    assert notiz == f"Bau: {FELD_NOTIZ} — abo 6.3851 / api 0.0000"


def test_ohne_notiz_steht_der_vorspann_allein(tmp_path):
    """Auch ohne Text des Menschen sagt die Zeile, welche Kosten sie traegt."""
    ledger = _ledger(tmp_path)
    logs = _log(tmp_path / "team-logs", "marv.json", 1.0)
    rc, _out, err = _run("rollen-abschluss", "--kaskade", "3",
                         "--domaene", "produkt", "--logs", str(logs),
                         "--pfad", str(ledger))
    assert rc == 0, err
    assert _notiz(ledger, "roles") == "Rollen — abo 1.0000 / api 0.0000"


def test_fremde_rolle_bekommt_ihren_namen_als_vorspann(tmp_path):
    """Projekte buchen eigene Rollen separat (BL-13: `frank`). Auch dort darf
    die Zuordnung nicht fehlen — Fallback ist der Rollenname selbst."""
    ledger = _ledger(tmp_path)
    kosten.rollen_abschluss("3", abo=1.0, api=0.0, domaene="produkt",
                            notiz="Out-of-Loop-Fix", pfad=str(ledger),
                            rolle="frank")
    assert _notiz(ledger, "frank").startswith("Frank: ")


def test_addieren_behaelt_den_vorspann(tmp_path):
    """Der Nachlauf (BL-5, --addieren) schreibt die Zeile neu — auch die
    Summenzeile muss ihre Herkunft behalten."""
    ledger = _ledger(tmp_path)
    logs = _log(tmp_path / "ralph-logs", "stufe-1.json", 2.0)
    _run("ralph-abschluss", "--kaskade", "3", "--domaene", "produkt",
         "--logs", str(logs), "--pfad", str(ledger), "--archivieren")
    _log(logs, "stufe-2.json", 0.5)
    rc, _out, err = _run("ralph-abschluss", "--kaskade", "3",
                         "--domaene", "produkt", "--logs", str(logs),
                         "--pfad", str(ledger), "--archivieren", "--addieren",
                         "--notiz", "Nachlauf")
    assert rc == 0, err
    assert _notiz(ledger, "ralph").startswith("Bau: Nachlauf")


@pytest.mark.skipif(TEAM_STATUS is None,
                    reason="team-status.sh nicht gefunden")
def test_die_eine_bedienhandlung_trennt_die_herkunft(tmp_path):
    """Der Weg, auf dem der Fehler im Feld entstand: EIN Aufruf, zwei Zeilen.
    Genau hier muss die Trennung ankommen, nicht nur in der Bibliothek."""
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    shutil.copy(TEAM_LIB, repo / "team" / "lib.sh")
    shutil.copy(KOSTEN_PY, repo / "team" / "tools" / "kosten.py")
    # Eigene Minimalkonfiguration statt der ausgelieferten: Im Kit-Repo steht
    # in team.config.sh noch der ungefuellte Domaenen-Platzhalter, an dem
    # die Domaenenpruefung scheitert. Der Test soll BL-19 pruefen, nicht
    # die Installation.
    (repo / "team.config.sh").write_text(
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n'
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n',
        encoding="utf-8")
    _log(repo / ".team-logs", "harry.json", 2.4085)
    _log(repo / ".ralph-logs", "stufe-1.json", 6.3851)
    (repo / ".budget-ledger").write_text(
        "# datum | kaskade | usd | auth | domaene | rolle | notiz\n")
    # BL-34: Die Bau-Notiz wird aus dem Plannamen abgeleitet, wenn der Mensch
    # keine zweite angibt. Ohne .ralph-plan bliebe die Zeile ehrlich
    # unbeschriftet ("Bau — abo …"); geprueft werden soll hier aber der
    # Regelfall eines laufenden Projekts.
    (repo / "plans").mkdir()
    (repo / "plans" / "ralph-kaskade-3-kamera.md").write_text("# Plan\n")
    (repo / ".ralph-plan").write_text("plans/ralph-kaskade-3-kamera.md\n")
    ziel = repo / "team-status.sh"
    shutil.copy(TEAM_STATUS, ziel)
    ziel.chmod(0o755)

    ergebnis = subprocess.run(
        [BASH, str(ziel), "--rollen-abschluss", "3", "produkt", FELD_NOTIZ],
        capture_output=True, text=True, cwd=str(repo),
        env=dict(os.environ, TEAM_DOMAENEN="produkt"))
    assert ergebnis.returncode == 0, ergebnis.stderr

    ledger = repo / ".budget-ledger"
    assert _notiz(ledger, "roles").startswith("Rollen: ")
    assert _notiz(ledger, "ralph").startswith("Bau: ")
    # BL-34: Der Vorspann allein reichte nicht — der TEXT dahinter war im Feld
    # zweimal der des Red Teams. Er darf auf der Bau-Zeile nicht mehr stehen.
    assert "Harry" not in _notiz(ledger, "ralph")
    assert "K3" in _notiz(ledger, "ralph")
    # Die Betraege bleiben unangetastet — BL-19 war nie ein Rechenfehler.
    zeilen = {z["rolle"]: z["usd"] for z in kosten.ledger_zeilen(str(ledger))}
    assert zeilen["roles"] == pytest.approx(2.4085)
    assert zeilen["ralph"] == pytest.approx(6.3851)

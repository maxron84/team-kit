#!/usr/bin/env python3
"""BL-16: Der Guard schrieb jede schmutzige Datei der laufenden Rolle zu.

Aus dem Feld zurueckgespielt (dort BL-8, team-kit_project_platformer,
Kaskade 2). `team_guard_verify` bildete die Verletzerliste aus
`git diff --name-only $HASH HEAD` plus `git status --porcelain` — es gab
KEINEN Ausgangszustand. Die Funktion wusste nicht, was beim Rollenstart bereits
schmutzig war, und lastete jeden fremden Schreiber (parallele Sitzung,
Handaenderung, abgebrochenes Werkzeug) der Rolle an. Folge doppelt:

  (a) Axels KORREKTE Ermittlung zaehlte als "Aufruf fehlgeschlagen" — dritte
      Stagnation, Lauf gestoppt, obwohl die Akte fertig geschrieben war.
  (b) Fremde, unbeteiligte Arbeit wurde chirurgisch, aber hart zurueckgerollt.

Zwei Entscheide (Strippenzieher, 2026-08-02):
  Ebene 1 — Zuschreibung: team_guard_begin haelt einen Schnappschuss mit
      BLOB-HASHES. Was beim Start schon schmutzig war UND es unveraendert
      geblieben ist, gehoert nicht der Rolle. Der Hash ist noetig, damit eine
      Rolle nicht freikommt, die eine ohnehin schmutzige Datei anfasst.
  Ebene 2 — Urteil: Liegt das Ergebnis der Rolle vor, kassiert der Guard den
      UEBERGRIFF, nicht die Arbeit (team_guard_urteil).

Alles gegen ein temporaeres Wegwerf-Repo, nie gegen den echten Arbeitsbaum.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import BASH, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]
TEAM_LIB = kit_pfad("lib.sh")
WHITELIST = "^(plans/)"


def _bash(skript, cwd):
    return subprocess.run(
        [BASH, "-c", skript],
        cwd=cwd,
        env={"HOME": str(Path.home()), "PATH": "/usr/local/bin:/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )


def _repo(tmp_path):
    """Wegwerf-Repo mit einem committeten Produktivcode- und einem plans/-Pfad."""
    repo = tmp_path / "repo"
    (repo / "plans").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("original\n", encoding="utf-8")
    (repo / "plans" / "beutebuch.md").write_text("# Beutebuch\n", encoding="utf-8")
    for befehl in (
        "git init -q",
        "git config user.email test@example.invalid",
        "git config user.name Test",
        "git add -A",
        "git commit -q -m start",
    ):
        ergebnis = _bash(befehl, repo)
        assert ergebnis.returncode == 0, ergebnis.stderr
    return repo


def _lauf(repo, mutation):
    """team_guard_begin, dann <mutation>, dann team_guard_verify — wie im Skript.

    Mit `set -euo pipefail`, weil die Rollen-Skripte so laufen: Eine Funktion,
    die nur ohne strikte Optionen durchkommt, ist im Ernstfall wertlos.
    """
    skript = (
        "set -euo pipefail\n"
        f'source "{TEAM_LIB}"\n'
        "team_guard_begin\n"
        f"{mutation}\n"
        f"if team_guard_verify harry '{WHITELIST}'; then echo URTEIL=sauber; "
        "else echo URTEIL=verletzung; fi\n"
    )
    return _bash(skript, repo)


def test_vorab_schmutzige_fremdarbeit_wird_nicht_angelastet(tmp_path):
    """Der Kern von BL-16: Was vor dem Rollenstart schmutzig war, bleibt fremd."""
    repo = _repo(tmp_path)
    (repo / "src" / "app.py").write_text("fremde arbeit\n", encoding="utf-8")

    ergebnis = _lauf(repo, ":")  # die Rolle tut nichts

    assert "URTEIL=sauber" in ergebnis.stdout, ergebnis.stderr
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "fremde arbeit\n", (
        "Die fremde Arbeit wurde zurueckgerollt — genau der Datenverlust aus dem Feld."
    )
    assert "nicht dieser Rolle zugeschrieben" in ergebnis.stderr


def test_vorab_schmutzige_datei_bleibt_belastbar_wenn_die_rolle_sie_anfasst(tmp_path):
    """Gegenrichtung: Der Schnappschuss darf kein Freibrief sein.

    Ein reiner Pfadvergleich wuerde hier durchwinken. Deshalb haelt der
    Schnappschuss Blob-Hashes: Der Inhalt hat sich geaendert, also war es die
    Rolle.
    """
    repo = _repo(tmp_path)
    (repo / "src" / "app.py").write_text("fremde arbeit\n", encoding="utf-8")

    ergebnis = _lauf(repo, "printf 'rolle war hier\\n' > src/app.py")

    assert "URTEIL=verletzung" in ergebnis.stdout, ergebnis.stderr
    assert "src/app.py" in ergebnis.stderr
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "original\n", (
        "Der Uebergriff wurde nicht auf den Startstand zurueckgerollt."
    )


def test_guard_bleibt_scharf_bei_sauberem_start(tmp_path):
    """Regression: Ohne Vorbelastung urteilt der Guard wie bisher."""
    repo = _repo(tmp_path)

    ergebnis = _lauf(repo, "printf 'neu\\n' > src/neu.py")

    assert "URTEIL=verletzung" in ergebnis.stdout, ergebnis.stderr
    assert not (repo / "src" / "neu.py").exists(), "Neu entstandener Pfad blieb liegen."
    assert "DIESE ROLLE hat die folgenden Pfade" in ergebnis.stderr


def test_whitelist_pfade_bleiben_erlaubt(tmp_path):
    """Regression: Die Rolle darf in plans/ schreiben, auch neu."""
    repo = _repo(tmp_path)

    ergebnis = _lauf(repo, "printf 'fund\\n' >> plans/beutebuch.md")

    assert "URTEIL=sauber" in ergebnis.stdout, ergebnis.stderr
    assert "fund" in (repo / "plans" / "beutebuch.md").read_text(encoding="utf-8")


def test_begin_warnt_laut_bei_schmutzigem_baum(tmp_path):
    """Der Lauf soll nicht blind starten (Entscheid: warnen, nicht abbrechen)."""
    repo = _repo(tmp_path)
    (repo / "src" / "app.py").write_text("fremde arbeit\n", encoding="utf-8")

    ergebnis = _bash(
        f'set -euo pipefail\nsource "{TEAM_LIB}"\nteam_guard_begin\necho FERTIG',
        repo,
    )

    assert "FERTIG" in ergebnis.stdout, ergebnis.stderr
    assert "NICHT sauber" in ergebnis.stderr
    assert "src/app.py" in ergebnis.stderr
    assert "bitte committen" in ergebnis.stderr


def test_begin_schweigt_bei_sauberem_baum(tmp_path):
    """Eine Warnung, die immer erscheint, erzieht zum Wegsehen."""
    repo = _repo(tmp_path)

    ergebnis = _bash(
        f'set -euo pipefail\nsource "{TEAM_LIB}"\nteam_guard_begin\necho FERTIG',
        repo,
    )

    assert "FERTIG" in ergebnis.stdout, ergebnis.stderr
    assert "NICHT sauber" not in ergebnis.stderr


def test_meldung_trennt_die_beiden_faelle_sprachlich(tmp_path):
    """Diagnose-Lehre aus dem Feld: Der Uebergriff wurde der falschen Rolle
    zugeschrieben, weil die Pfadliste im Log neben ihrem Namen stand."""
    repo = _repo(tmp_path)
    (repo / "src" / "app.py").write_text("fremde arbeit\n", encoding="utf-8")

    ergebnis = _lauf(repo, "printf 'neu\\n' > src/neu.py")

    assert "DIESE ROLLE hat die folgenden Pfade" in ergebnis.stderr
    assert "NICHT angelastet" in ergebnis.stderr
    fremd_block = ergebnis.stderr.split("NICHT angelastet", 1)[1]
    assert "src/app.py" in fremd_block, "Fremdpfad steht nicht im Fremd-Block."
    verletzer_block = ergebnis.stderr.split("DIESE ROLLE", 1)[1].split("NICHT angelastet")[0]
    assert "src/neu.py" in verletzer_block, "Verletzerpfad steht nicht im Verletzer-Block."


@pytest.mark.parametrize(
    "uebergriff, ergebnis, erwartet_rc, erwarteter_text",
    [
        (0, 0, 0, ""),                       # kein Uebergriff — nichts zu urteilen
        (0, 1, 0, ""),
        (1, 1, 0, "kassiert"),               # Ebene 2: Arbeit geleistet
        (1, 0, 1, "gescheitert"),            # Uebergriff ohne Ergebnis
    ],
)
def test_guard_urteil(tmp_path, uebergriff, ergebnis, erwartet_rc, erwarteter_text):
    repo = _repo(tmp_path)
    lauf = _bash(
        f'set -euo pipefail\nsource "{TEAM_LIB}"\n'
        f"if team_guard_urteil axel {uebergriff} {ergebnis}; then echo RC=0; else echo RC=1; fi",
        repo,
    )
    assert f"RC={erwartet_rc}" in lauf.stdout, lauf.stderr
    if erwarteter_text:
        assert erwarteter_text in lauf.stderr, lauf.stderr


# Im Kit liegen die Entrypoints unter entry/, in der Installation in der Wurzel.
GUARD_SKRIPTE = {
    "axel": ("axel.sh", "bash/entry/axel.sh"),
    "redteam": ("bash/redteam.sh", "team/redteam.sh",),
}


@pytest.mark.parametrize("skript", sorted(GUARD_SKRIPTE))
def test_rollen_skripte_urteilen_ueber_das_ergebnis(skript):
    """Ebene 2 muss in den Aufrufern verdrahtet sein.

    Der alte Reflex — Guard-Verletzung wird sofort zum Fehlschlag — darf nicht
    zurueckkommen: Genau er hat im Feld den Lauf gestoppt.
    """
    for kandidat in GUARD_SKRIPTE[skript]:
        if (REPO_ROOT / kandidat).is_file():
            break
    else:
        raise AssertionError(f"{skript}: keine der Quellen existiert: {GUARD_SKRIPTE[skript]}")
    text = (REPO_ROOT / kandidat).read_text(encoding="utf-8")
    assert "GUARD_UEBERGRIFF=0" in text, f"{skript} merkt sich den Uebergriff nicht"
    assert "team_guard_urteil" in text, f"{skript} faellt kein Ergebnis-Urteil"
    assert '[ "$RC" -eq 0 ] && RC=1' not in text, (
        f"{skript} uebersetzt einen Guard-Uebergriff wieder sofort in einen Fehlschlag"
    )


if __name__ == "__main__":
    import inspect
    import tempfile

    fehler = []
    for name, fn in list(globals().items()):
        if not (name.startswith("test_") and callable(fn)):
            continue
        params = inspect.signature(fn).parameters
        if "uebergriff" in params or "skript" in params:
            continue  # parametrisiert — nur unter pytest
        try:
            with tempfile.TemporaryDirectory() as td:
                fn(Path(td)) if "tmp_path" in params else fn()
            print(f"OK   {name}")
        except AssertionError as e:
            fehler.append(name)
            print(f"FAIL {name}: {e}")
    if fehler:
        sys.exit(1)
    print("gruen — BL-16 verifiziert: Zuschreibung belegt, Guard bleibt scharf.")

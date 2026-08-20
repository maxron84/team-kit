#!/usr/bin/env python3
"""Regressionstest fuer die Rollen-Briefings (Kaskade 22, Stufe 90).

Belegt: fuenf kurze Briefing-Dateien ersetzen die frueh im Prompt stehende
Zeile "Rolle siehe CLAUDE.md — lies sie zuerst." (ein zusaetzlicher
Voll-Read von CLAUDE.md pro Rollenaufruf). team_briefing() liest sie aus
und faellt bei fehlender/leerer Datei exakt auf die alte Zeile zurueck
(Selbstbezugs-Risiko dieser Kaskade — ein Fehler hier darf keinen Lauf
lahmlegen). Rein netz-/CLI-frei ueber subprocess + bash -c gegen ein
temporaeres Fixture-Verzeichnis, nie gegen die echten prompts/-Dateien.
"""
import subprocess
import sys
import re
from pathlib import Path

from conftest import BASH, kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = kit_pfad("lib.sh")
PROMPTS_DIR = kit_pfad("prompts")

ROLLEN = ("ralph", "harry", "marv", "frank", "axel")


def _produktivcode():
    """Liest TEAM_PRODUKTIVCODE aus team.config.sh — das Kit ist stackagnostisch,
    die Guard-Grenze heisst in jedem Projekt anders."""
    cfg = REPO_ROOT / "team.config.sh"
    if cfg.exists():
        m = re.search(r'TEAM_PRODUKTIVCODE="\$\{TEAM_PRODUKTIVCODE:-([^}]*)\}"',
                      cfg.read_text(encoding="utf-8"))
        if m and m.group(1) and "{{" not in m.group(1):
            return m.group(1)
    return None


PRODUKTIVCODE = _produktivcode()
KERNGRENZEN = {
    "ralph": "keine Features aus späteren Stufen",
    "harry": PRODUKTIVCODE,
    "marv": PRODUKTIVCODE,
    "frank": "Dreisatz",
    "axel": PRODUKTIVCODE,
}
SKRIPTE = {
    "ralph.sh": "team_briefing ralph",
    "team/redteam.sh": 'team_briefing "$ROLLE"',
    "frank.sh": "team_briefing frank",
    "axel.sh": "team_briefing axel",
}
EISERNE_REGEL_ZEILEN = {
    "team/redteam.sh": ("EISERNE REGEL", "<promise>REDTEAM_SWEEP_COMPLETE</promise>"),
    "axel.sh": ("EISERNE REGEL", "<promise>AXEL_CASE_COMPLETE</promise>"),
    "frank.sh": ("Franks Dreisatz", "<promise>FRANK_FIX_COMPLETE</promise>"),
    "ralph.sh": ("<promise>STUFE_${STUFE}_COMPLETE</promise>",),
}


def _run(bash_script, cwd):
    env = {"HOME": str(Path.home()), "PATH": "/usr/bin:/bin"}
    result = subprocess.run(
        [BASH, "-c", bash_script],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    return result


def test_fuenf_briefing_dateien_existieren_und_sind_kurz():
    for rolle in ROLLEN:
        datei = PROMPTS_DIR / f"rolle-{rolle}.md"
        assert datei.exists(), f"Briefing fehlt: {datei}"
        zeilen = datei.read_text(encoding="utf-8").splitlines()
        assert len(zeilen) <= 45, (
            f"rolle-{rolle}.md hat {len(zeilen)} Zeilen (Limit 45)"
        )


def test_jedes_briefing_nennt_seine_kerngrenze():
    for rolle, kerngrenze in KERNGRENZEN.items():
        if kerngrenze is None:
            # Kit-Repo ohne gefuellte team.config.sh: die Guard-Grenze steht
            # dort noch als Platzhalter. Im installierten Projekt greift die
            # Pruefung wieder.
            continue
        text = (PROMPTS_DIR / f"rolle-{rolle}.md").read_text(encoding="utf-8")
        assert kerngrenze in text, (
            f"rolle-{rolle}.md nennt die Kerngrenze nicht woertlich: {kerngrenze!r}"
        )


def test_team_briefing_liefert_dateiinhalt(tmp_path):
    fixture_prompts = tmp_path / "team" / "prompts"
    fixture_prompts.mkdir(parents=True)
    (fixture_prompts / "rolle-testrolle.md").write_text(
        "Zeile eins\nZeile zwei\n", encoding="utf-8"
    )
    result = _run(f'source "{TEAM_LIB}"; team_briefing testrolle', cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "Zeile eins\nZeile zwei\n"


def test_team_briefing_fallback_bei_fehlender_datei(tmp_path):
    result = _run(f'source "{TEAM_LIB}"; team_briefing unbekannt', cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Rolle siehe CLAUDE.md — lies sie zuerst."


def test_team_briefing_fallback_bei_leerer_datei(tmp_path):
    fixture_prompts = tmp_path / "team" / "prompts"
    fixture_prompts.mkdir(parents=True)
    (fixture_prompts / "rolle-leer.md").write_text("", encoding="utf-8")
    result = _run(f'source "{TEAM_LIB}"; team_briefing leer', cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Rolle siehe CLAUDE.md — lies sie zuerst."


def test_rollen_skripte_rufen_team_briefing_auf():
    for skript, aufruf in SKRIPTE.items():
        text = (REPO_ROOT / skript).read_text(encoding="utf-8")
        assert aufruf in text, f"{skript} ruft {aufruf!r} nicht (mehr) auf"
        assert "Rolle siehe CLAUDE.md — lies sie zuerst" not in text, (
            f"{skript} enthaelt noch die alte Inline-Zeile statt team_briefing"
        )


def test_eiserne_regel_und_promise_zeilen_bleiben_erhalten():
    for skript, marker in EISERNE_REGEL_ZEILEN.items():
        text = (REPO_ROOT / skript).read_text(encoding="utf-8")
        for teil in marker:
            assert teil in text, f"{skript} hat {teil!r} verloren"


if __name__ == "__main__":
    import inspect

    failures = []
    for name, fn in list(globals().items()):
        if not (name.startswith("test_") and callable(fn)):
            continue
        params = inspect.signature(fn).parameters
        try:
            if "tmp_path" in params:
                import tempfile

                with tempfile.TemporaryDirectory() as td:
                    fn(Path(td))
            else:
                fn()
            print(f"OK   {name}")
        except AssertionError as e:
            failures.append(name)
            print(f"FAIL {name}: {e}")
    if failures:
        sys.exit(1)
    print("gruen — Stufe 90 verifiziert: Briefings vollstaendig, Fallback greift, Guards unangetastet.")

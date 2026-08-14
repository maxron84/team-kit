#!/usr/bin/env python3
"""BL-20/BL-21/BL-31/BL-39/BL-43/BL-44: Was das Red Team ueberhaupt sucht.

BL-20 — Der ausgelieferte Grundauftrag beschrieb eine statische Website
("Statische Site — kein Server", inline-Handler, `target=_blank`). In jedem
anderen Stack behauptete er damit etwas SACHLICH FALSCHES ueber das
Zielprojekt, und ein Modell uebernimmt das als Tatsache. Feld-Beleg
(pygame-Spiel): Sweep ueber vier neue Baustufen mit pfadnehmendem Datei-Leser
— 0,4567 USD, NULL Funde; derselbe Code mit passendem Fokus — 1,0247 USD, ein
Fund.

BL-21 — Alle Auftraege des Kits waren adversarisch. Was der GEWOEHNLICHE Pfad
kostet, fragte keiner: Im Feld zog ein Spiel 42 % CPU-Last bei 103 gruenen
Tests. Die Dimension fehlt unabhaengig vom Stack.

BL-31 — `TEAM_REDTEAM_FOCUS` ist eine Umgebungsvariable ohne Verfallsdatum. Im
Feld lief ein Sweep mit dem Fokus der Vorkaskade und prueft pflichtgemaess das
Falsche: 7,62 USD, beide Funde am falschen Ort. Gegenprobe im selben Closeout
mit passendem Fokus: 3,11 USD, zwei Treffer.

BL-39 — Zwei Fragen fehlten in jedem Auftrag: Kontrollfluss statt Rumpfvergleich
(`return` → `break`) und die Durchzaehlung mitbenutzter Bedingungen.

BL-43/BL-44 — Die Bauform des Fokus (Naehte zum Bestand statt neuer Mechanik)
und die Auflage, Pruefpunkte in den STRING zu schreiben statt in die
Uebergabenachricht.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _quelle(*kandidaten):
    for kandidat in kandidaten:
        pfad = REPO_ROOT / kandidat
        if pfad.is_file():
            return pfad
    raise AssertionError(f"keine der Quellen existiert: {kandidaten}")


def _entrypoint(name):
    for kandidat in (REPO_ROOT / name, REPO_ROOT / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


# --- BL-20: keine Technologie-Behauptung im Default -------------------------

TECHNOLOGIE_WOERTER = [
    "HTML", "CSS", "JS", "target=_blank", "rel=noopener", "Statische Site",
    "Schutz-Header", "Alt-Texte", "prefers-reduced-motion",
]


@pytest.mark.parametrize("rolle", ["harry", "marv"])
def test_default_auftrag_behauptet_keine_technologie(rolle):
    """Eine falsche Behauptung ueber das Zielprojekt ist schlimmer als eine
    unspezifische Anweisung — das Modell uebernimmt sie als Tatsache."""
    pfad = _entrypoint(f"{rolle}.sh")
    assert pfad is not None, f"{rolle}.sh nicht gefunden"
    text = pfad.read_text(encoding="utf-8")
    # Nur die AUFTRAG-Zeile pruefen: Die Kommentare darueber duerfen den
    # Feldfall ruhig beim Namen nennen, sie landen in keinem Prompt.
    auftrag = [z for z in text.splitlines() if z.startswith("export AUFTRAG=")]
    assert len(auftrag) == 1, "genau eine AUFTRAG-Zuweisung erwartet"
    gefunden = [w for w in TECHNOLOGIE_WOERTER if w in auftrag[0]]
    assert not gefunden, (
        f"{rolle}.sh behauptet weiter einen Stack: {gefunden}")


@pytest.mark.parametrize("rolle", ["harry", "marv"])
def test_projekt_uebersteuerung_ist_vorgesehen(rolle):
    """Die Anpassung gehoert in team.config.sh — sie ueberlebt --update;
    eine Aenderung im Skript nicht (BL-12)."""
    text = _entrypoint(f"{rolle}.sh").read_text(encoding="utf-8")
    assert f"TEAM_REDTEAM_AUFTRAG_{rolle.upper()}" in text
    config = _quelle("entry/team.config.sh", "team.config.sh").read_text(
        encoding="utf-8")
    assert f"TEAM_REDTEAM_AUFTRAG_{rolle.upper()}" in config


def test_kaskadenfokus_schlaegt_beide(monkeypatch):
    """Rangfolge: TEAM_REDTEAM_FOCUS (dieser Lauf) > Projektauftrag > Default."""
    text = _entrypoint("harry.sh").read_text(encoding="utf-8")
    auftrag = [z for z in text.splitlines() if z.startswith("export AUFTRAG=")][0]
    assert auftrag.index("TEAM_REDTEAM_FOCUS") < auftrag.index(
        "TEAM_REDTEAM_AUFTRAG_HARRY")


# --- BL-21: die fehlende Dimension ------------------------------------------

def test_marv_fragt_nach_den_kosten_des_gewoehnlichen_pfades():
    auftrag = [z for z in _entrypoint("marv.sh").read_text(
        encoding="utf-8").splitlines() if z.startswith("export AUFTRAG=")][0]
    assert "GEWOEHNLICHE" in auftrag or "gewoehnliche" in auftrag
    assert "asymptotisch" in auftrag, (
        "ohne Schwelle liefert Marv zwanzig Mikro-Optimierungen — "
        "'das ginge schneller' ist unbegrenzt")


# --- BL-39: die zwei Fragen im Sweep-Prompt ---------------------------------

def test_sweep_prompt_fragt_nach_kontrollfluss_und_mitbenutzung():
    text = (REPO_ROOT / "team" / "redteam.sh").read_text(encoding="utf-8")
    assert "Kontrollfluss" in text
    assert "break" in text and "return" in text, \
        "die Klasse muss am Beispiel benannt sein, sonst wird sie nicht erkannt"
    assert "mitbenutzt" in text


# --- BL-31: der Fokus verfaellt mit dem Stand -------------------------------

def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "team" / "prompts").mkdir()
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "plans").mkdir()
    shutil.copy(REPO_ROOT / "team" / "lib.sh", repo / "team" / "lib.sh")
    shutil.copy(REPO_ROOT / "team" / "redteam.sh", repo / "team" / "redteam.sh")
    shutil.copy(_entrypoint("harry.sh"), repo / "harry.sh")
    for werkzeug in ("beutebuch.py", "kosten.py"):
        shutil.copy(REPO_ROOT / "team" / "tools" / werkzeug,
                    repo / "team" / "tools" / werkzeug)
    for briefing in (REPO_ROOT / "team" / "prompts").glob("*.md"):
        shutil.copy(briefing, repo / "team" / "prompts" / briefing.name)
    (repo / "team.config.sh").write_text(
        'TEAM_PROJEKT="fixture"\n'
        'TEAM_PRODUKTIVCODE="src/"\nTEAM_TEST_ORDNER="tests/"\n'
        'TEAM_PLAN_ORDNER="plans/"\n'
        'TEAM_BEUTEBUCH="plans/beutebuch.md"\n'
        'TEAM_ERMITTLUNGSAKTEN="plans/ermittlungsakten"\n'
        'TEAM_BEUTEBUCH_TOOL="python3 team/tools/beutebuch.py"\n'
        'TEAM_KOSTEN_TOOL="python3 team/tools/kosten.py"\n'
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n'
        'TEAM_WHITELIST_REDTEAM="^(tests/|plans/)"\n'
        'TEAM_WHITELIST_AXEL="^plans/"\n'
        'TEAM_ROLE_BUDGET_USD="5"\nTEAM_ROLE_HARDCAP_USD="10"\n',
        encoding="utf-8")
    (repo / "plans" / "beutebuch.md").write_text(
        "# Beutebuch\n\n## Vorlage\n\n### HM-<Nr> — <Titel>\n"
        "- **Status**: offen\n\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (repo / ".gitignore").write_text(
        ".team-logs/\n.harry-state\n.team-focus-harry\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo


def _sweep(repo, fokus=None):
    """Faehrt harry.sh gegen eine CLI-Attrappe, die den Prompt mitschreibt."""
    bin_dir = repo / "bin"
    bin_dir.mkdir(exist_ok=True)
    # Ausserhalb des Repos: Der Guard raeumt neue Dateien im Arbeitsbaum
    # inzwischen wirklich weg (BL-24) — eine Mitschrift im Repo waere nach dem
    # Lauf geloescht.
    dump = repo.parent / "prompt.txt"
    ergebnis = json.dumps({
        "subtype": "success", "is_error": False, "total_cost_usd": 0.1,
        "result": "fertig <promise>REDTEAM_SWEEP_COMPLETE</promise>"})
    stub = bin_dir / "claude"
    stub.write_text("#!/usr/bin/env bash\n"
                    f'printf "%s\\n" "$@" > "{dump}"\n'
                    f"cat <<'JSON'\n{ergebnis}\nJSON\n", encoding="utf-8")
    stub.chmod(0o755)
    env = dict(os.environ)
    env.update({"PATH": f"{bin_dir}:{env['PATH']}", "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    if fokus is not None:
        env["TEAM_REDTEAM_FOCUS"] = fokus
    else:
        env.pop("TEAM_REDTEAM_FOCUS", None)
    lauf = subprocess.run(["./harry.sh"], cwd=repo, env=env,
                          capture_output=True, text=True)
    return lauf, (dump.read_text(encoding="utf-8") if dump.exists() else "")


def _neuer_commit(repo, name):
    (repo / "src" / name).write_text("y = 2\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", name],
                   check=True, capture_output=True)


def test_fokus_gilt_fuer_seinen_lauf(tmp_path):
    repo = _repo(tmp_path)
    lauf, prompt = _sweep(repo, fokus="Leveldesign der Kaskade 10")
    assert lauf.returncode == 0, lauf.stderr
    assert "Leveldesign der Kaskade 10" in prompt


def test_alter_fokus_verfaellt_beim_naechsten_stand(tmp_path):
    """Der Feldfall: Der Fokus der Kaskade 10 lenkte den Sweep der Kaskade 11."""
    repo = _repo(tmp_path)
    _sweep(repo, fokus="Leveldesign der Kaskade 10")
    _neuer_commit(repo, "neu.py")
    lauf, prompt = _sweep(repo, fokus=None)
    assert lauf.returncode == 0, lauf.stderr
    assert "Leveldesign der Kaskade 10" not in prompt, \
        "der Fokus der Vorkaskade lenkt weiter — genau der Feldfall"
    assert "VERFALLEN" in lauf.stderr, \
        "das Verwerfen muss laut geschehen, nicht still"


def test_ohne_je_gesetzten_fokus_bleibt_alles_still(tmp_path):
    repo = _repo(tmp_path)
    lauf, _ = _sweep(repo, fokus=None)
    assert lauf.returncode == 0, lauf.stderr
    assert "VERFALLEN" not in lauf.stderr


# --- BL-43/BL-44: die Bauform des Fokus in der Regel ------------------------

@pytest.mark.parametrize("traeger", [
    ("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md"),
    ("team/prompts/rolle-architekt.md",),
], ids=["Regeldatei", "rolle-architekt"])
def test_regel_gibt_die_bauform_des_fokus_vor(traeger):
    """BL-43: DASS der Fokus gesetzt wird, regelt BL-31 — WIE er gebaut wird,
    stand nirgends. Beide Traeger, sonst wirkt es nicht."""
    text = _quelle(*traeger).read_text(encoding="utf-8")
    assert "Verträge berührt das Neue" in text, \
        "die tragende Frage fehlt: nicht 'was ist neu', sondern welche "\
        "bestehenden Verträge das Neue berührt"


@pytest.mark.parametrize("traeger", [
    ("bootstrap/CLAUDE.md.vorlage", "CLAUDE.md"),
    ("team/prompts/rolle-architekt.md",),
], ids=["Regeldatei", "rolle-architekt"])
def test_regel_verlangt_pruefpunkte_im_string(traeger):
    """BL-44: Was in der Uebergabenachricht steht, erreicht das Red Team nie."""
    text = _quelle(*traeger).read_text(encoding="utf-8")
    assert "sollte noch jemand prüfen" in text
    assert "nie" in text and "Nachricht" in text

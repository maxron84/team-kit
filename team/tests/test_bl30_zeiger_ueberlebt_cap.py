#!/usr/bin/env python3
"""BL-30: Der Hard-Cap einer read-only-Rolle vernichtete die Quittung, nicht
die Arbeit.

Die Kit-Begruendung fuer den sofortigen Hard-Cap bei Harry/Marv lautete, es
gehe "nichts Bezahltes verloren", weil sie read-only sind. Das stimmt fuer die
FUNDE — die liegen uncommittet im Baum —, aber nicht fuer den Zustandszeiger.

Im Feld (Closeout K11): Marvs Sweep meldete `is_error: false`,
`subtype: success`, Promise gesetzt und zwei sauber formatierte Funde — und
wurde danach wegen 6,52 >= 5,00 als "ECHTER Fehler" abgebrochen. `.marv-state`
blieb stehen; ein Neustart haette dieselben 22 Commits ein zweites Mal geprueft
und ein zweites Mal bezahlt. Bei einer read-only-Rolle ist der Zustandszeiger
das EINZIGE, was der Deckel ueberhaupt beschaedigen kann — die Regel schuetzte
nicht, was sie zu schuetzen glaubte.

Abgrenzung, ausdruecklich: Das ist kein Aufweichen des Read-Only-Guards und
keine Soft-Cap-Ausweitung. Der Deckel bleibt voll wirksam; er verhindert den
NAECHSTEN Aufruf. Es geht allein darum, ob ein nachweislich erfolgreicher
Aufruf seinen Zeiger behalten darf.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _entrypoint(name):
    for kandidat in (REPO_ROOT / name, REPO_ROOT / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


HARRY = _entrypoint("harry.sh")
pytestmark = pytest.mark.skipif(
    HARRY is None or not (REPO_ROOT / "team" / "redteam.sh").is_file(),
    reason="harry.sh/redteam.sh nicht gefunden")

BEUTEBUCH = """# Beutebuch

## Vorlage

### HM-<Nr> — <Titel>
- **Status**: offen

"""


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "team" / "prompts").mkdir()
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "plans").mkdir()
    shutil.copy(REPO_ROOT / "team" / "lib.sh", repo / "team" / "lib.sh")
    shutil.copy(REPO_ROOT / "team" / "redteam.sh", repo / "team" / "redteam.sh")
    shutil.copy(HARRY, repo / "harry.sh")
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
    (repo / "plans" / "beutebuch.md").write_text(BEUTEBUCH, encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (repo / ".gitignore").write_text(".team-logs/\n.harry-state\n",
                                     encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                       capture_output=True)
    return repo


def _lauf(repo, kosten, mit_promise=True):
    """Faehrt harry.sh gegen eine CLI-Attrappe mit vorgegebenen Kosten."""
    bin_dir = repo / "bin"
    bin_dir.mkdir(exist_ok=True)
    ergebnis = json.dumps({
        "subtype": "success", "is_error": False, "total_cost_usd": kosten,
        "result": ("fertig <promise>REDTEAM_SWEEP_COMPLETE</promise>"
                   if mit_promise else "abgebrochen")})
    stub = bin_dir / "claude"
    stub.write_text("#!/usr/bin/env bash\ncat <<'JSON'\n" + ergebnis + "\nJSON\n",
                    encoding="utf-8")
    stub.chmod(0o755)
    env = dict(os.environ)
    env.update({"PATH": f"{bin_dir}:{env['PATH']}", "AUTH_MODE": "api",
                "ANTHROPIC_API_KEY": "sk-ant-dummy", "TEAM_LOCK_HELD": "1"})
    return subprocess.run(["./harry.sh"], cwd=repo, env=env,
                          capture_output=True, text=True)


def test_erfolgreicher_sweep_ueber_cap_behaelt_seinen_zeiger(tmp_path):
    """Der Feldfall: Promise da, Log sauber, nur zu teuer."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, 6.52)
    assert lauf.returncode == 0, lauf.stderr
    assert (repo / ".harry-state").is_file(), \
        "der Zustandszeiger fehlt — der naechste Lauf prueft dieselben Commits erneut"
    assert "BL-30" in lauf.stderr
    assert "gedeckelt" in lauf.stderr, \
        "die Ueberschreitung muss im Protokoll stehen, nicht verschwinden"


def test_ueberschreitung_ohne_ergebnis_bricht_weiterhin_ab(tmp_path):
    """Die Abgrenzung: Ohne Quittung bleibt es beim Abbruch — der Deckel wird
    nicht aufgeweicht, nur seine paradoxe Nebenwirkung entfaellt."""
    repo = _repo(tmp_path)
    lauf = _lauf(repo, 6.52, mit_promise=False)
    assert lauf.returncode != 0
    assert not (repo / ".harry-state").is_file()


def test_lauf_unter_cap_bleibt_unveraendert(tmp_path):
    repo = _repo(tmp_path)
    lauf = _lauf(repo, 1.20)
    assert lauf.returncode == 0, lauf.stderr
    assert (repo / ".harry-state").is_file()
    assert "BL-30" not in lauf.stderr, \
        "unter dem Cap darf keine Cap-Meldung erscheinen (BL-14)"

#!/usr/bin/env python3
"""BL-18: `--budget` behauptete "nicht im Gesamt enthalten" — auch dann, wenn
die Architekten-Zeile sehr wohl enthalten war.

Aus dem Feld zurueckgespielt (platformer, Architekt-Closeout K3, 2026-08-02).
team-status.sh druckte den Zusatz UNBEDINGT, obwohl team_architekt_stand zwei
Modi hat:

  geschaetzt  Wert aus der A2-Churn-Schaetzung, steht in KEINER Ledger-Zeile
              -> der Zusatz stimmt.
  echt        Wert aus einer Ledger-Zeile DIESER Kaskade, und die summiert
              team_kontostand_gesamt mit -> der Zusatz ist FALSCH.

Der Modus schaltet ausgerechnet beim Kaskaden-Abschluss um, also genau in dem
Moment, in dem die Zahl abgelesen und weitergegeben wird. Im Feld: Anzeige
"Architekt (echt, nicht im Gesamt enthalten): 9.7000" bei "Gesamt: 71.5706" —
der beim Wort genommene Kontostand waere 81.27 statt 71.57 gewesen, 13 % zu
viel.

Zweiter Teil desselben Befunds: Der Architekt-Wert ist KASKADENSCHARF, jede
andere Zeile des Blocks kumuliert lebenslang. Die Beschriftung muss den
Bezugsrahmen nennen ("K3"), sonst liest man ihn als Lebenszeit-Summe.

Geprueft wird die WIRKLICH GERENDERTE Ausgabe von `--budget` gegen ein
temporaeres Fixture-Repo — nie gegen die echte .budget-ledger. Beide Modi,
also inklusive Gegenprobe im Modus "geschaetzt".
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
KOSTEN_PY = REPO_ROOT / "team" / "tools" / "kosten.py"
TEAM_LIB = REPO_ROOT / "team" / "lib.sh"

sys.path.insert(0, str(REPO_ROOT / "team" / "tools"))
import kosten  # noqa: E402


def _entrypoint(name):
    """Entrypoints liegen in der Installation in der Wurzel, im Kit unter
    entry/ (BL-6). Der Test soll in BEIDEN Ablagen laufen — er baut sein
    Repo ohnehin selbst und kopiert die Datei nur hinein."""
    for kandidat in (REPO_ROOT / name, REPO_ROOT / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


TEAM_STATUS = _entrypoint("team-status.sh")

# Nachgebaute Feldlage: zwei Architekt-Zeilen (eine davon aus der LAUFENDEN
# Kaskade 3) neben den Rollen-/Bau-Zeilen. Summe aller Zeilen: 54.2706.
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"
ZEILEN_OHNE_ARCHITEKT_K3 = (
    "2026-08-01 | 2 | 20.0000 | api | produkt | architekt | K2 Architekt\n"
    "2026-08-02 | 3 | 24.5706 | abo | produkt | roles | K3 Rollen\n"
)
ARCHITEKT_K3 = "2026-08-02 | 3 | 9.7000 | api | produkt | architekt | K3\n"

LEDGER_ECHT = KOPF + ZEILEN_OHNE_ARCHITEKT_K3 + ARCHITEKT_K3
LEDGER_GESCHAETZT = KOPF + ZEILEN_OHNE_ARCHITEKT_K3


def _repo(tmp_path, ledger_inhalt):
    """Minimales Wegwerf-Projekt, in dem `--budget` laufen kann. Bewusst OHNE
    git: team_architekt_schaetzung faellt dann auf 0.0000 zurueck, der
    geschaetzte Modus wird dadurch deterministisch."""
    repo = tmp_path / "repo"
    (repo / "team" / "tools").mkdir(parents=True)
    (repo / "plans").mkdir()
    shutil.copy(TEAM_LIB, repo / "team" / "lib.sh")
    shutil.copy(KOSTEN_PY, repo / "team" / "tools" / "kosten.py")
    # Eigene Minimalkonfiguration statt der ausgelieferten: Im Kit-Repo steht
    # in team.config.sh noch der ungefuellte Domaenen-Platzhalter. Eine
    # Domaene heisst ausserdem: kein Domaenenblock (BL-9), die Ausgabe
    # bleibt schmal und eindeutig.
    (repo / "team.config.sh").write_text(
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n'
        'TEAM_KOSTEN_TOOL="python3 team/tools/kosten.py"\n'
        'TEAM_BEUTEBUCH_TOOL="python3 team/tools/beutebuch.py"\n',
        encoding="utf-8")
    (repo / ".budget-ledger").write_text(ledger_inhalt, encoding="utf-8")
    (repo / "plans" / "ralph-kaskade-3-test.md").write_text(
        "# Kaskade 3\n", encoding="utf-8")
    (repo / ".ralph-plan").write_text(
        "plans/ralph-kaskade-3-test.md\n", encoding="utf-8")
    ziel = repo / "team-status.sh"
    shutil.copy(TEAM_STATUS, ziel)
    ziel.chmod(0o755)
    return repo


def _budget(repo):
    ergebnis = subprocess.run(
        ["bash", str(repo / "team-status.sh"), "--budget"],
        capture_output=True, text=True, cwd=str(repo),
        env={"HOME": str(Path.home()), "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    assert ergebnis.returncode == 0, ergebnis.stderr
    return ergebnis.stdout


def _zeile_mit(ausgabe, marker):
    treffer = [z for z in ausgabe.splitlines() if marker in z]
    assert len(treffer) == 1, f"genau eine Zeile mit '{marker}' erwartet: {treffer}"
    return treffer[0]


def _betrag(zeile):
    return float(re.search(r":\s*([0-9.]+)\s*USD", zeile).group(1))


pytestmark = pytest.mark.skipif(
    TEAM_STATUS is None, reason="team-status.sh nicht gefunden")


def test_echte_architekt_zeile_wird_als_enthalten_ausgewiesen(tmp_path):
    """Der Feldfehler selbst: Bei gebuchter Zeile darf die Anzeige NICHT zum
    Weiteraddieren einladen."""
    ausgabe = _budget(_repo(tmp_path, LEDGER_ECHT))
    zeile = _zeile_mit(ausgabe, "Architekt")

    assert "echt" in zeile
    assert "nicht im Gesamt enthalten" not in zeile, (
        "BL-18: Die Zeile IST in der Gesamtsumme — der alte Zusatz liess sie "
        "ein zweites Mal addieren (im Feld 81.27 statt 71.57 USD)")
    assert "im Gesamt enthalten" in zeile


def test_gesamt_enthaelt_die_architekt_zeile_wirklich(tmp_path):
    """Die Beschriftung ist nur dann richtig, wenn die Summe sich auch so
    verhaelt — deshalb wird nachgerechnet statt nur der Text geprueft."""
    repo = _repo(tmp_path, LEDGER_ECHT)
    ausgabe = _budget(repo)
    gesamt = _betrag(_zeile_mit(ausgabe, "Gesamt (Basis + laufend)"))
    architekt = _betrag(_zeile_mit(ausgabe, "Architekt"))

    ledger = str(repo / ".budget-ledger")
    assert gesamt == pytest.approx(kosten.ledger_summe(ledger))
    assert gesamt == pytest.approx(54.2706)
    assert architekt == pytest.approx(9.7000)
    # Kern der Falschanzeige: Wer den Zusatz beim Wort nimmt, addiert.
    assert gesamt + architekt != pytest.approx(kosten.ledger_summe(ledger))


def test_geschaetzter_wert_bleibt_ausserhalb_des_gesamt(tmp_path):
    """Gegenprobe: Ohne gebuchte Zeile stammt der Wert aus der A2-Schaetzung,
    steht in keiner Ledger-Zeile — der alte Zusatz war HIER richtig und muss
    erhalten bleiben."""
    repo = _repo(tmp_path, LEDGER_GESCHAETZT)
    ausgabe = _budget(repo)
    zeile = _zeile_mit(ausgabe, "Architekt")

    assert "geschätzt" in zeile
    assert "nicht im Gesamt enthalten" in zeile
    gesamt = _betrag(_zeile_mit(ausgabe, "Gesamt (Basis + laufend)"))
    assert gesamt == pytest.approx(
        kosten.ledger_summe(str(repo / ".budget-ledger")))
    assert gesamt == pytest.approx(44.5706)


def test_beschriftung_nennt_den_bezugsrahmen(tmp_path):
    """Zweiter Teil des Befunds: Der Architekt-Wert gilt fuer EINE Kaskade,
    jede andere Zeile des Blocks lebenslang. Ohne Rahmen liest man 9.70 als
    Lebenszeit-Summe des Architekten (real waren es 29.70)."""
    repo = _repo(tmp_path, LEDGER_ECHT)
    ausgabe = _budget(repo)

    assert "K3" in _zeile_mit(ausgabe, "Architekt"), \
        "die Kaskade, fuer die der Wert gilt, muss dranstehen"
    assert "lebenslang" in _zeile_mit(ausgabe, "Gesamt (Basis + laufend)")
    # Und die Zahl ist wirklich nur die der Kaskade, nicht die Lebenssumme.
    ledger = str(repo / ".budget-ledger")
    assert _betrag(_zeile_mit(ausgabe, "Architekt")) == pytest.approx(9.7000)
    assert kosten.ledger_summe(ledger, rolle="architekt") == \
        pytest.approx(29.7000)


def _bash(skript, cwd):
    return subprocess.run(
        ["bash", "-c", skript], cwd=cwd, capture_output=True, text=True,
        env={"HOME": str(Path.home()), "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )


def test_team_architekt_kaskade_liest_die_nummer_aus_der_plan_datei(tmp_path):
    repo = _repo(tmp_path, LEDGER_ECHT)
    ergebnis = _bash(
        'source ./team/lib.sh; team_architekt_kaskade "$@"', str(repo))
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert ergebnis.stdout.strip() == "3"


def test_team_architekt_kaskade_bleibt_ohne_nummer_leer_und_still(tmp_path):
    """Benannte Kaskaden ("post-20") und frische Projekte haben keine Nummer.
    Die Funktion muss dann leer ausgeben und darf den Aufrufer unter set -e
    NICHT wegreissen — die Beschriftung laesst den Rahmen dann einfach weg."""
    repo = _repo(tmp_path, LEDGER_ECHT)
    (repo / ".ralph-plan").write_text("plans/roles-post-k13.md\n",
                                      encoding="utf-8")
    ergebnis = _bash(
        'set -e; source ./team/lib.sh; k="$(team_architekt_kaskade)"; '
        'echo "rc=$? wert=[$k]"', str(repo))
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "rc=0 wert=[]" in ergebnis.stdout

    ausgabe = _budget(repo)
    zeile = _zeile_mit(ausgabe, "Architekt")
    assert "K" not in zeile.split("(")[0].replace("Architekt", ""), \
        f"ohne erkennbare Kaskade darf kein Rahmen behauptet werden: {zeile}"

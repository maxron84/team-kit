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

from conftest import Ausgabe, BASH, FangUndMelde, kit_pfad, werkzeug_wert

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


def _entrypoint(name):
    """Entrypoints liegen in der Installation in der Wurzel, im Kit unter
    entry/ (BL-6). Der Test soll in BEIDEN Ablagen laufen — er baut sein
    Repo ohnehin selbst und kopiert die Datei nur hinein."""
    for kandidat in (REPO_ROOT / name,
                     REPO_ROOT / "bash" / "entry" / name,
                     REPO_ROOT / "pwsh" / "entry" / name):
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


def _repo(tmp_path, ledger_inhalt, schale=None):
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
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n',
        encoding="utf-8")
    (repo / ".budget-ledger").write_text(ledger_inhalt, encoding="utf-8")
    (repo / "plans" / "ralph-kaskade-3-test.md").write_text(
        "# Kaskade 3\n", encoding="utf-8")
    (repo / ".ralph-plan").write_text(
        "plans/ralph-kaskade-3-test.md\n", encoding="utf-8")
    ziel = repo / "team-status.sh"
    shutil.copy(TEAM_STATUS, ziel)
    ziel.chmod(0o755)
    # Die Bash-Artefakte oben bleiben immer liegen: In dieser Datei starten
    # mehrere Tests `./team-status.sh` und brauchen sie unabhaengig von der
    # geprueften Bahn. Die pwsh-Fassung kommt additiv dazu, statt sie zu
    # ersetzen.
    if schale is not None and not schale.ist_bash:
        schale.lib_kopieren(repo)
        schale.config_schreiben(repo, {
            "TEAM_DOMAENEN": "produkt",
            "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
            "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
        })
    return repo


def _status(repo, *argumente):
    ergebnis = subprocess.run(
        [BASH, str(repo / "team-status.sh"), *argumente],
        capture_output=True, text=True, cwd=str(repo),
        env={"HOME": str(Path.home()), "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    assert ergebnis.returncode == 0, ergebnis.stderr
    return ergebnis.stdout


def _budget(repo):
    return _status(repo, "--budget")


def _momentaufnahme(repo):
    """Die zweite Ansicht derselben Kennzahl (`./team-status.sh` ohne Argument),
    Block "Kosten (lebenslang kumuliert)"."""
    return _status(repo)


def _zeile_mit(ausgabe, marker):
    treffer = [z for z in ausgabe.splitlines() if marker in z]
    assert len(treffer) == 1, f"genau eine Zeile mit '{marker}' erwartet: {treffer}"
    return treffer[0]


def _betrag(zeile):
    return float(re.search(r":\s*([0-9.]+)\s*USD", zeile).group(1))


def _label(zeile):
    """Beschriftung ohne Einrückung und Spaltenauffüllung — die beiden
    Ansichten setzen den Betrag verschieden breit."""
    return re.search(r"(Architekt.*?\))", zeile).group(1)


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


def test_momentaufnahme_zeigt_dieselbe_kennzahl_wie_budget(tmp_path):
    """Nachzug zu BL-18: Die Momentaufnahme zeigte die reine A2-Schaetzung
    ("Architekt (geschätzt, A2)") direkt ueber "Gesamt-Kontostand (inkl.
    Ledger)" — nach dem Buchen also eine Schaetzung neben einer Summe, welche
    die ECHTE Zeile bereits enthaelt: dieselbe Einladung zum Doppeladdieren,
    nur im anderen Block. Zwei Ansichten derselben Kennzahl duerfen nicht
    auseinanderlaufen."""
    repo = _repo(tmp_path, LEDGER_ECHT)
    zeile = _zeile_mit(_momentaufnahme(repo), "Architekt")

    assert "echt" in zeile
    assert "K3" in zeile
    assert "nicht im Gesamt enthalten" not in zeile
    assert "im Gesamt enthalten" in zeile
    assert _betrag(zeile) == pytest.approx(9.7000)
    assert "geschätzt, A2" not in zeile, (
        "die alte, modusblinde Beschriftung darf nicht ueberleben")


def test_beide_ansichten_beschriften_die_kennzahl_wortgleich(tmp_path):
    """Der eigentliche Schutz: EINE Quelle fuer beide Ansichten. Divergenz
    zwischen zwei Anzeigen derselben Zahl war der Befund."""
    for nr, ledger_inhalt in enumerate((LEDGER_ECHT, LEDGER_GESCHAETZT)):
        repo = _repo(tmp_path / f"fall{nr}", ledger_inhalt)
        aus_budget = _zeile_mit(_budget(repo), "Architekt")
        aus_status = _zeile_mit(_momentaufnahme(repo), "Architekt")
        assert _label(aus_budget) == _label(aus_status), \
            f"Beschriftung laeuft auseinander:\n  {aus_budget}\n  {aus_status}"
        assert _betrag(aus_budget) == pytest.approx(_betrag(aus_status))


def _lib(schale, repo):
    return repo / "team" / schale.lib_name


def test_team_architekt_kaskade_liest_die_nummer_aus_der_plan_datei(tmp_path, schale):
    repo = _repo(tmp_path, LEDGER_ECHT, schale)
    ergebnis = schale.lauf(Ausgabe("team_architekt_kaskade"), cwd=repo,
                           lib=_lib(schale, repo))
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert ergebnis.stdout.strip() == "3"


def test_team_architekt_kaskade_bleibt_ohne_nummer_leer_und_still(tmp_path, schale):
    """Benannte Kaskaden ("post-20") und frische Projekte haben keine Nummer.
    Die Funktion muss dann leer ausgeben und darf den Aufrufer unter `set -e`
    NICHT wegreissen — die Beschriftung laesst den Rahmen dann einfach weg.

    Hier stand bis BL-111 `strikt="abbruch"` statt der vollen Strenge, und
    der Grund war ein echter: Die damalige Absicherung (`| head -1`) trug
    gegen `set -e`, aber NICHT gegen `set -o pipefail` — dort schlug der leere
    `grep` durch und riss den Aufrufer doch weg. Der Test nannte deshalb die
    Stufe, fuer die die Zusicherung wirklich galt, statt eine breitere zu
    behaupten; der Rest wurde ein eigener Backlog-Eintrag statt einer stillen
    Verschaerfung.

    Seit BL-111 haelt `{ … ; } || true` den Rueckgabewert auf 0, und zwar
    unter jeder Stufe. Deshalb faehrt dieser Test jetzt `strikt=True` — das
    ist die Gegenprobe zum Fix, nicht nur eine schaerfere Einstellung: Mit der
    alten lib.sh faellt er.
    """
    repo = _repo(tmp_path, LEDGER_ECHT, schale)
    (repo / ".ralph-plan").write_text("plans/roles-post-k13.md\n",
                                      encoding="utf-8")
    ergebnis = schale.lauf(FangUndMelde("team_architekt_kaskade"), cwd=repo,
                           lib=_lib(schale, repo), strikt=True)
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "rc=0 wert=[]" in ergebnis.stdout

    ausgabe = _budget(repo)
    zeile = _zeile_mit(ausgabe, "Architekt")
    assert "K" not in zeile.split("(")[0].replace("Architekt", ""), \
        f"ohne erkennbare Kaskade darf kein Rahmen behauptet werden: {zeile}"

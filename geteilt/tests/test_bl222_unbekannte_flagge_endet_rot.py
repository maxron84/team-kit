#!/usr/bin/env python3
"""BL-222: `team-status` nahm JEDE unbekannte Flagge als Statusabfrage
entgegen und meldete Exit 0.

WAS IM FELD PASSIERT IST
    `Feld E`, Kostenabschluss einer Kaskade. Gerufen wurde
    `./team-status.sh --hilfe`; erwartet war eine Nutzungszeile oder
    wenigstens "unbekannte Option". Bekommen: die normale Statusausgabe —
    Kaskadenstand, Beutebuch, Kostenblock, letzte Commits — und Exit 0.
    Gegenprobe mit `--voelliger-unsinn-xyz`: dasselbe.

    Der Dispatcher war eine if/elif-Kette ueber "${1:-}" und endete mit einem
    blanken `else status_einmal`. Gemeint war "ohne Argument zeige den
    Status"; gefangen hat es jedes Argument, das keinem Zweig entsprach.

WARUM DAS SCHWERER WIEGT ALS EINE FEHLENDE HILFE
    Alle schreibenden Verben dieses Skripts sind KOSTENBUCHUNGEN, und ihre
    Namen sind lang und leicht zu verfehlen: --rollen-abschluss,
    --architekt-abschluss, --akteur-abschluss, --ledger-pruefen. Ein
    fehlendes `s`, ein deutsches `ss`, `--ledger-pruefe` — es bucht NICHTS,
    druckt eine plausibel aussehende Statusausgabe und endet mit 0. Wer das
    in einer Sequenz oder aus einem Skript ruft, sieht Zeilen vorbeiziehen
    und hakt den Schritt ab.

    Dieselbe Ausgangslage wie BL-165 ("Eine Sitzung ohne Closeout bucht ihre
    Kosten selbst" — im Feld 43,90 USD Abo-Gegenwert an einem Tag), nur
    meldet das Werkzeug diesmal aktiv Erfolg.

    Das Skript konnte es an anderer Stelle laengst besser:
    `status_rollen_abschluss` weist einen unbekannten Buchungsmodus namentlich
    zurueck. Die Zurueckweisung existierte als Muster; sie fehlte nur auf der
    obersten Ebene, wo sie am meisten truege.

WAS DIESER TEST PRUEFT
    Der EXIT-CODE ist die Zusicherung, nicht der Text: Er ist das, was ein
    aufrufendes Skript auswerten kann (dieselbe Trennung wie bei
    `geraet.sh --pruefen` — Text fuer den Menschen, Code fuer den Aufrufer).
    Dazu die Gegenrichtung, ohne die der Fix Schaden anrichtet: Der
    ARGUMENTLOSE Aufruf bleibt die Momentaufnahme, davon haengen die
    Bedienanleitung und die Abschlussausgabe der Vollautomatik ab.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      verlange_pwsh, werkzeug_wert)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Die Verben, deren Vertippen Geld kostet — jedes hier einmal knapp daneben.
FAST_RICHTIG = ["--rollen-abschlus", "--ledger-pruefe", "--akteur-abschluss-",
                "--architekt-abschluß"]


def _projekt(tmp_path, bahn):
    (tmp_path / "team" / "tools").mkdir(parents=True)
    shutil.copy(kit_pfad("tools", "kosten.py"),
                tmp_path / "team" / "tools" / "kosten.py")
    if bahn == "bash":
        shutil.copy(entrypoint_pfad("team-status.sh"), tmp_path / "team-status.sh")
        shutil.copy(kit_pfad("lib.sh"), tmp_path / "team" / "lib.sh")
        (tmp_path / "team.config.sh").write_text(
            'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            'TEAM_KOSTEN_TOOL="' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n', encoding="utf-8")
    else:
        shutil.copy(entrypoint_pfad("team-status.ps1"), tmp_path / "team-status.ps1")
        shutil.copy(kit_pfad("lib.psm1"), tmp_path / "team" / "lib.psm1")
        # BL-113/BL-134: PowerShell-Quelltext traegt ein BOM, auch als Fixture.
        (tmp_path / "team.config.ps1").write_text(
            '$TEAM_BEUTEBUCH_TOOL = "' + werkzeug_wert('team/tools/beutebuch.py') + '"\n'
            '$TEAM_KOSTEN_TOOL = "' + werkzeug_wert('team/tools/kosten.py') + '"\n'
            '$TEAM_DOMAENEN = "produkt"\n', encoding="utf-8-sig")
    return tmp_path


def _bash(repo, *args):
    return subprocess.run([BASH, "./team-status.sh", *args], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def _pwsh(repo, *args):
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", "./team-status.ps1",
         *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace")


# --- Der Fall aus dem Feld ---------------------------------------------------

def test_bash_unbekannte_flagge_endet_rot(tmp_path):
    repo = _projekt(tmp_path, "bash")
    r = _bash(repo, "--voelliger-unsinn-xyz")
    assert r.returncode != 0, (
        "BL-222 ist zurueck: eine erfundene Flagge meldet Erfolg.\n" + r.stdout)
    assert "--voelliger-unsinn-xyz" in r.stderr, \
        "die Meldung muss nennen, WAS nicht erkannt wurde"
    assert "--rollen-abschluss" in r.stderr, \
        "und was es stattdessen gibt — sonst raet der Bediener weiter"


@pytest.mark.parametrize("flagge", FAST_RICHTIG)
def test_bash_vertipptes_buchungsverb_endet_rot(tmp_path, flagge):
    """Der eigentliche Schaden: Ein Tippfehler in einem Buchungsverb bucht
    nichts und sah bisher aus wie ein gelungener Schritt."""
    repo = _projekt(tmp_path, "bash")
    r = _bash(repo, flagge)
    assert r.returncode != 0, (
        f"'{flagge}' hat gebucht wie ein Statusaufruf und Erfolg gemeldet.\n"
        + r.stdout)


def test_bash_hilfe_antwortet_mit_dem_dateikopf(tmp_path):
    repo = _projekt(tmp_path, "bash")
    for schalter in ("--hilfe", "--help", "-h"):
        r = _bash(repo, schalter)
        assert r.returncode == 0, f"{schalter}: {r.stderr}"
        assert "Aufruf:" in r.stdout, f"{schalter} druckt keinen Kopf"
        assert "--rollen-abschluss" in r.stdout, (
            f"{schalter} nennt die schreibenden Verben nicht — genau deshalb "
            "erfaehrt ein neuer Anwender nie, dass es sie gibt")


def test_bash_ohne_argument_bleibt_die_momentaufnahme(tmp_path):
    """DIE Gegenprobe. `./team-status.sh` ohne Argument steht in der
    Bedienanleitung und am Ende jedes Vollautomatik-Laufs — ein Riegel, der
    auch DAS faengt, waere schlimmer als der Fund."""
    repo = _projekt(tmp_path, "bash")
    r = _bash(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip(), "die Momentaufnahme darf nicht verstummen"


def test_bash_bekannte_flagge_laeuft_weiter(tmp_path):
    """Zweite Gegenprobe: Der Riegel darf keinen erkannten Zweig verschlucken."""
    repo = _projekt(tmp_path, "bash")
    r = _bash(repo, "--altlast", "3")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Altlast" in r.stdout


# --- Dieselben Zusicherungen auf der pwsh-Bahn -------------------------------

def test_pwsh_unbekannte_flagge_endet_rot(tmp_path):
    verlange_pwsh()
    repo = _projekt(tmp_path, "pwsh")
    r = _pwsh(repo, "--voelliger-unsinn-xyz")
    assert r.returncode != 0, r.stdout
    assert "--voelliger-unsinn-xyz" in (r.stderr + r.stdout)


def test_pwsh_hilfe_antwortet_mit_dem_dateikopf(tmp_path):
    verlange_pwsh()
    repo = _projekt(tmp_path, "pwsh")
    for schalter in ("--hilfe", "--help", "-h"):
        r = _pwsh(repo, schalter)
        assert r.returncode == 0, f"{schalter}: {r.stderr}"
        assert "Aufruf:" in r.stdout, f"{schalter} druckt keinen Kopf"


def test_pwsh_ohne_argument_bleibt_die_momentaufnahme(tmp_path):
    verlange_pwsh()
    repo = _projekt(tmp_path, "pwsh")
    r = _pwsh(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip()


# --- Gleichstand der Bahnen, statisch ----------------------------------------

@pytest.mark.parametrize("datei", ["team-status.sh", "team-status.ps1"])
def test_beide_bahnen_kennen_die_hilfe_und_den_riegel(datei):
    """`BL-155`/`BL-156` waren beide von derselben Gattung: eine fehlende
    Haelfte, kein ungeprueftes Stueck Bau. Ein Riegel, den nur eine Bahn hat,
    ist derselbe Fund noch einmal — und auf Windows ist die einbahnige
    pwsh-Ablage der Normalfall (BL-178).

    Fehlt die Datei selbst, wird UEBERSPRUNGEN statt rot: In einer einbahnig
    installierten Ablage gibt es das Gegenstueck nicht, und ein roter Fall
    dort beweist nichts ueber das Kit."""
    pfad = Path(entrypoint_pfad(datei))
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht (einbahnig installiert)")
    text = pfad.read_text(encoding="utf-8-sig")
    assert "--hilfe" in text, f"{datei} kennt --hilfe nicht"
    assert "Unbekannte Option" in text, (
        f"{datei} hat keinen Zweig, der eine unbekannte Option zurueckweist")
    assert "BL-222" in text, (
        f"{datei} nennt die Herkunft des Riegels nicht — ohne sie ist er beim "
        "naechsten Umbau eine unmotivierte Zeile")

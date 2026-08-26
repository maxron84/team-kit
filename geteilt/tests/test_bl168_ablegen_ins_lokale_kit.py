#!/usr/bin/env python3
"""BL-168 + BL-187: Der Rückkanal hatte ein Werkzeug für den Weg, den niemand
geht — und keins für den, den alle gehen.

DIE LAGE, DIE NIEMAND BEDIENT HAT
    `senden` legt einen Pull Request an und braucht dafür ein angemeldetes
    `gh`. Ohne das fällt es auf einen Issue-Link zurück, den ein Mensch von
    Hand anklickt. Genau das ist der Normalfall beim **Betreiber des Kits
    selbst**: Er hat das Repo geklont daneben liegen (`TEAM_KIT_PFAD` zeigt
    darauf), aber `gh auth status` ist auf der Maschine nicht angemeldet.

    Die Folge war messbar: Im meldenden Projekt sind **acht** Funde von Hand
    ins lokale Kit getippt worden, an `kit-melden` vorbei. Damit war auch die
    Redaktionsprüfung umgangen — die einzige Stelle, an der ein Projektname
    auffällt, BEVOR er in einem öffentlichen Repo steht.

DREI GRENZEN, UND JEDE HAT EINEN GRUND
    1. KEIN PUSH. Owner zu sein löst die Frage der ZUSTÄNDIGKEIT, nicht die
       der VERÖFFENTLICHUNG.
    2. KEINE `BL-`NUMMER. Die vergibt der Maintainer beim Triage; sonst wäre
       der Nummernraum ein Wettlauf zwischen Meldern, die voneinander nichts
       wissen (`plans/meldungen/README.md`). Wie teuer das wird, zeigt
       `BL-188`.
    3. REDAKTIONSPRÜFUNG ALS VORBEDINGUNG, nicht als Empfehlung.

    Dazu kommt: pfadgenau committen. Der Kit-Arbeitsbaum kann alles Mögliche
    enthalten, und ein `git add -A` nähme fremde Arbeit mit (Lehre `BL-12`).

DER ZWEITE, KLEINERE TEIL VON BL-168
    Der Kommentarkopf jeder frisch angelegten Meldung nennt den Aufruf mit dem
    BLANKEN Dateinamen. `pruefen` löste ihn ausschließlich gegen das
    Arbeitsverzeichnis auf — von der Projektwurzel aus liegt die Datei aber
    unter `<plan-ordner>/kit-meldungen/`. **Die Vorlage nannte einen Befehl,
    den sie selbst nicht lauffähig machte.**

BL-187: `senden` LIEF SEHENDEN AUGES IN DEN FALSCHEN WEG
    Das Werkzeug erkannte den Owner-Fall längst — es nutzte ihn nur, um den
    Fork zu überspringen, und legte danach trotzdem einen PR gegen das eigene
    Repo an. Die Prüfung steht jetzt VOR der Bestätigungsfrage.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import kit_pfad  # noqa: E402

WERKZEUG = kit_pfad("tools", "kit_meldung.py")

pytestmark = pytest.mark.skipif(
    not WERKZEUG.is_file(), reason="kit_meldung.py liegt in dieser Ablage nicht")


def lauf(*args, umgebung=None, cwd=None, eingabe=None):
    env = dict(os.environ)
    env["USER"] = env["USERNAME"] = "pruefkonto"
    env.pop("TEAM_KIT_PFAD", None)
    env.pop("TEAM_PROJEKT", None)
    env.pop("TEAM_FELD_KUERZEL", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(umgebung or {})
    return subprocess.run([sys.executable, str(WERKZEUG), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", input=eingabe, env=env,
                          cwd=str(cwd) if cwd else None)


def _git(kit, *args):
    return subprocess.run(["git", "-C", str(kit), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def baue_kit(wurzel):
    """Ein Kit-Repo mit den zwei Marken — und einer fremden, uncommitteten Datei.

    Die fremde Datei ist der eigentliche Prüfkörper: Ein `git add -A` im Kit
    nähme sie mit, und dann committet ein Meldewerkzeug fremde Arbeit.
    """
    kit = wurzel / "kit"
    for marke in ("bootstrap/CLAUDE.md.vorlage", "geteilt/tools/kosten.py"):
        p = kit / marke
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8", newline="\n")
    (kit / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [2.13.1] — 2026-08-25\n", encoding="utf-8",
        newline="\n")
    _git(kit, "init", "-q")
    _git(kit, "config", "user.email", "pruef@example.invalid")
    _git(kit, "config", "user.name", "Pruefkonto")
    _git(kit, "add", "-A")
    _git(kit, "commit", "-q", "-m", "kit")
    (kit / "fremde-arbeit.txt").write_text("nicht mitnehmen\n",
                                           encoding="utf-8", newline="\n")
    return kit


SAUBER = """# Ein Fund am Kit

- **Art**: Fehler am Kit
- **Feldkürzel**: Feld X
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn

## Was passiert ist

Der Hergang, kurz und vollständig.

## Wo es steckt

In der Fuell-Routine.
"""


def _projekt(tmp_path, text=SAUBER, name="2026-08-26-ein-fund.md"):
    ordner = tmp_path / "projekt" / "plans" / "kit-meldungen"
    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / name).write_text(text, encoding="utf-8", newline="\n")
    return tmp_path / "projekt", ordner, name


def _global(projekt, ordner, kit):
    return ["--projektwurzel", str(projekt), "--meldungen", str(ordner),
            "--kit", str(kit)]


# --- ablegen -----------------------------------------------------------------


def test_ablegen_bringt_die_meldung_in_den_eingangskorb(tmp_path):
    """Die Gegenprobe, die BL-168 verlangt: vom Entwurf bis ins Kit, ohne eine
    Zeile von Hand — und ohne `gh`."""
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    r = lauf(*_global(projekt, ordner, kit), "ablegen", name)
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"
    ziel = kit / "plans" / "meldungen" / name
    assert ziel.is_file(), f"Nichts im Eingangskorb:\n{r.stdout}{r.stderr}"
    assert ziel.read_text(encoding="utf-8") == SAUBER, "Text verändert"


def test_ablegen_nimmt_keine_fremde_arbeit_mit(tmp_path):
    """DIE Zusicherung, an der ein `git add -A` scheitern würde.

    Der Kit-Arbeitsbaum gehört dem Maintainer. Ein Meldewerkzeug, das ihn
    mitcommittet, macht aus einer Meldung einen fremden Commit — Lehre `BL-12`.
    """
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    assert lauf(*_global(projekt, ordner, kit), "ablegen", name).returncode == 0
    dateien = _git(kit, "show", "--name-only", "--format=", "HEAD").stdout.split()
    assert dateien == [f"plans/meldungen/{name}"], (
        f"Der Commit hat mehr als die Meldung mitgenommen: {dateien}")
    offen = _git(kit, "status", "--porcelain").stdout
    assert "fremde-arbeit.txt" in offen, (
        "Die fremde Datei ist nicht mehr uncommittet — sie wurde eingesammelt.")


def test_ablegen_pusht_nicht(tmp_path):
    """Zuständigkeit ist nicht Veröffentlichung.

    Geprüft wird an der Wirkung, nicht am Quelltext: Das Fixture-Kit hat gar
    keinen Remote. Ein `git push` darin müsste scheitern — und `ablegen` endet
    trotzdem mit 0, weil es keinen versucht.
    """
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    r = lauf(*_global(projekt, ordner, kit), "ablegen", name)
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"
    assert not _git(kit, "remote").stdout.strip(), "Fixture hat einen Remote"
    aus = r.stdout + r.stderr
    assert "NICHT gepusht" in aus or "nicht gepusht" in aus, (
        f"Der Aufruf sagt nicht, dass er nicht gepusht hat:\n{aus}")


def test_ablegen_schreibt_keine_bl_nummer(tmp_path):
    """Die Nummer vergibt der Maintainer — sonst ist der Nummernraum ein
    Wettlauf zwischen Meldern, die voneinander nichts wissen (`BL-188`)."""
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    lauf(*_global(projekt, ordner, kit), "ablegen", name)
    text = (kit / "plans" / "meldungen" / name).read_text(encoding="utf-8")
    assert "BL-" not in text, (
        f"Die abgelegte Meldung trägt eine BL-Nummer:\n{text}")


def test_die_redaktionspruefung_ist_vorbedingung(tmp_path):
    """Kein Hinweis, ein Tor. Was hier durchgeht, ist gleich öffentlich."""
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(
        tmp_path, SAUBER + "\nAufgerufen in /home/wernher/projekt.\n")
    r = lauf(*_global(projekt, ordner, kit), "ablegen", name)
    assert r.returncode == 4, (
        f"Eine Meldung mit Redaktionsbefund ist durchgegangen:\n{r.stdout}{r.stderr}")
    assert not (kit / "plans" / "meldungen" / name).exists(), (
        "Trotz Abbruch liegt sie im Eingangskorb.")


def test_trotzdem_ist_der_bewusste_weg_daran_vorbei(tmp_path):
    """Ein Tor ohne Schlüssel wird umgangen statt benutzt — dann tippt der
    Melder wieder von Hand, und das war der Ausgangszustand."""
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(
        tmp_path, SAUBER + "\nAufgerufen in /home/wernher/projekt.\n")
    r = lauf(*_global(projekt, ordner, kit), "ablegen", name, "--trotzdem")
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"
    assert (kit / "plans" / "meldungen" / name).is_file()


def test_ohne_lokales_kit_sagt_ablegen_was_stattdessen_geht(tmp_path):
    """Ein Abbruch ohne Ausweg schickt den Melder zurück zur Handarbeit."""
    projekt, ordner, name = _projekt(tmp_path)
    r = lauf("--projektwurzel", str(projekt), "--meldungen", str(ordner),
             "--kit", str(tmp_path / "gibtsnicht"), "ablegen", name,
             umgebung={"HOME": str(tmp_path), "USERPROFILE": str(tmp_path)})
    assert r.returncode == 3, f"{r.stdout}{r.stderr}"
    assert "TEAM_KIT_PFAD" in r.stderr and "senden" in r.stderr, (
        f"Der Abbruch nennt keinen Ausweg:\n{r.stderr}")


def test_zweimal_ablegen_aendert_nichts(tmp_path):
    """Ein Melder ruft das zweimal auf, und beim zweiten Mal soll nichts
    Überraschendes passieren."""
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    assert lauf(*_global(projekt, ordner, kit), "ablegen", name).returncode == 0
    vorher = _git(kit, "rev-parse", "HEAD").stdout.strip()
    r = lauf(*_global(projekt, ordner, kit), "ablegen", name)
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"
    assert _git(kit, "rev-parse", "HEAD").stdout.strip() == vorher, (
        "Der zweite Aufruf hat einen zweiten Commit erzeugt.")


# --- pruefen: der blanke Name aus der Vorlage --------------------------------


def test_pruefen_findet_die_datei_am_blanken_namen(tmp_path):
    """Der Befehl, den die Vorlage SELBST nennt, muss laufen.

    Von der Projektwurzel aus liegt die Meldung unter
    `<plan-ordner>/kit-meldungen/`. Wurde nur gegen das Arbeitsverzeichnis
    aufgelöst, meldete der eigene Vorlagentext „gibt es nicht" — korrekt
    gemeldet, aber nicht das, was der Anwender wollte.
    """
    projekt, ordner, name = _projekt(tmp_path)
    r = lauf("--projektwurzel", str(projekt), "--meldungen", str(ordner),
             "pruefen", name, cwd=projekt)
    assert r.returncode == 0, (
        f"Der blanke Name aus der Vorlage wurde nicht aufgelöst:\n"
        f"{r.stdout}{r.stderr}")


def test_ein_getippter_pfad_gewinnt_gegen_den_meldungsordner(tmp_path):
    """CWD zuerst — sonst greift das Werkzeug an einer Datei vorbei, die der
    Anwender vor der Nase hat."""
    projekt, ordner, name = _projekt(tmp_path)
    daneben = tmp_path / "daneben"
    daneben.mkdir()
    (daneben / name).write_text(SAUBER + "\nToken ghp_abcdefghijklmnopqrstuvwx\n",
                                encoding="utf-8", newline="\n")
    r = lauf("--projektwurzel", str(projekt), "--meldungen", str(ordner),
             "pruefen", name, cwd=daneben)
    assert r.returncode == 4, (
        "Der Pfad im Arbeitsverzeichnis hat nicht gewonnen — geprüft wurde "
        f"die andere Datei:\n{r.stdout}{r.stderr}")


# --- Das Feldkürzel ----------------------------------------------------------


def test_neu_traegt_das_feldkuerzel_ein(tmp_path):
    """BL-168, vierter Teil: Das Kürzel lebte nur im Kit-README — also
    außerhalb der Installation, die es nennen müsste."""
    kit = baue_kit(tmp_path)
    r = lauf("--projektwurzel", str(tmp_path), "--meldungen",
             str(tmp_path / "m"), "--kit", str(kit), "--kuerzel", "Feld X",
             "neu", "--titel", "Irgendein Fund")
    assert r.returncode == 0, r.stderr
    text = Path(r.stdout.strip()).read_text(encoding="utf-8")
    assert "**Feldkürzel**: Feld X" in text, (
        f"Das Kürzel steht nicht in der Meldung:\n{text[:400]}")


def test_ohne_kuerzel_bleibt_ein_todo_stehen(tmp_path):
    """Ein leeres Feld sieht aus wie ein beantwortetes.

    Der TODO-Text ist zugleich der Grund, warum die Redaktionsprüfung dann
    anschlägt — sie sucht `TODO`. Das ist Absicht: unbeantwortet soll auffallen.
    """
    kit = baue_kit(tmp_path)
    r = lauf("--projektwurzel", str(tmp_path), "--meldungen",
             str(tmp_path / "m"), "--kit", str(kit),
             "neu", "--titel", "Ohne Kuerzel")
    assert r.returncode == 0, r.stderr
    text = Path(r.stdout.strip()).read_text(encoding="utf-8")
    assert "TEAM_FELD_KUERZEL" in text, (
        f"Der Hinweis nennt die Stelle nicht, an der man es einträgt:\n{text[:400]}")


@pytest.mark.parametrize("datei", ["bash/entry/team.config.sh",
                                   "pwsh/entry/team.config.ps1"])
def test_beide_konfigurationen_kennen_das_kuerzel(datei):
    """Gleichstand der Bahnen — ein Wert, den nur eine Bahn kennt, ist der Fall
    `BL-142`/`BL-145` in neuer Gestalt."""
    p = Path(__file__).resolve().parents[2] / datei
    if not p.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    assert "TEAM_FELD_KUERZEL" in p.read_text(encoding="utf-8-sig"), (
        f"{datei} kennt TEAM_FELD_KUERZEL nicht — dann bleibt das Kürzel auf "
        "dieser Bahn im Kit-README, also außerhalb der Installation.")


@pytest.mark.parametrize("datei", ["bash/entry/kit-melden.sh",
                                   "pwsh/entry/kit-melden.ps1"])
def test_beide_wrapper_reichen_das_kuerzel_durch(datei):
    """Ein Wert in der Konfiguration, den der Wrapper nicht durchreicht, wirkt
    nicht — dieselbe Bauart wie `BL-182`."""
    p = Path(__file__).resolve().parents[2] / datei
    if not p.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = p.read_text(encoding="utf-8-sig")
    assert "--kuerzel" in text and "TEAM_FELD_KUERZEL" in text, (
        f"{datei} reicht das Feldkürzel nicht durch.")


# --- BL-187: senden erkennt den Owner ----------------------------------------


def stelle_gh(tmp_path, konto):
    """Ein `gh`, das ein bestimmtes Konto meldet und jeden Aufruf mitschreibt.

    Das Protokoll ist der eigentliche Beleg: Steht am Ende weder `fork` noch
    `pr create` darin, hat NICHTS nach außen gewirkt.
    """
    bin_ordner = tmp_path / "bin"
    bin_ordner.mkdir(exist_ok=True)
    protokoll = tmp_path / "gh-aufrufe.txt"
    skript = (
        "#!/bin/sh\n"
        f'echo "$@" >> "{protokoll}"\n'
        'case "$1 $2" in\n'
        '  "auth status") exit 0 ;;\n'
        f'  "api user") echo "{konto}"; exit 0 ;;\n'
        "esac\n"
        "exit 0\n")
    (bin_ordner / "gh").write_text(skript, encoding="utf-8", newline="\n")
    (bin_ordner / "gh").chmod(0o755)
    return bin_ordner, protokoll


def _modul():
    """Das Werkzeug als MODUL — fuer die Faelle, die auf jedem Wirt laufen muessen.

    Der `gh`-Platzhalter der Faelle darunter ist ein sh-Skript und wird unter
    Windows nicht gefunden: `CreateProcess` haengt nur `.exe` an, nicht die
    Eintraege aus PATHEXT. Ein Uebersprung waere hier aber teuer — BL-187 ist
    ein Fund AUS der Windows-Bahn, und seine Zusicherung darf nicht
    ausgerechnet dort ungeprueft bleiben. Deshalb wird die Entscheidung hier
    im Prozess gefahren; die Faelle mit dem Platzhalter bleiben als
    End-zu-End-Beleg daneben stehen.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("kit_meldung_probe", WERKZEUG)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.mark.parametrize("konto,erwartet", [
    ("maxron84", "maxron84"),   # der Eigentuemer
    ("jemand-anderes", None),   # ein fremder Nutzer
    ("", None),                 # gh antwortet, aber leer
])
def test_die_owner_erkennung_urteilt_richtig(monkeypatch, konto, erwartet):
    """Die Entscheidung selbst, auf jedem Wirt.

    Der leere Fall ist kein Zierrat: Antwortet `gh` mit einer leeren Zeile,
    waere `"" == "".split("/")[0]` fuer ein Repo ohne Schraegstrich wahr — und
    das Werkzeug hielte jeden fuer den Eigentuemer.
    """
    m = _modul()

    def gefaelscht(*a, **kw):
        return subprocess.CompletedProcess(a, 0, konto + "\n", "")

    monkeypatch.setattr(m.subprocess, "run", gefaelscht)
    assert m._eigenes_repo("maxron84/team-kit") == erwartet


def test_ohne_gh_wird_niemand_zum_eigentuemer_erklaert(monkeypatch):
    """Aus einer nicht beantwortbaren Frage darf keine Aussage werden.

    Sonst schickt ein fehlendes `gh` jeden fremden Nutzer auf den Owner-Weg,
    den er nicht gehen kann.
    """
    m = _modul()

    def kaputt(*a, **kw):
        raise OSError("gh gibt es hier nicht")

    monkeypatch.setattr(m.subprocess, "run", kaputt)
    assert m._eigenes_repo("maxron84/team-kit") is None


def test_senden_bricht_beim_owner_ab_und_nennt_ablegen(tmp_path, monkeypatch,
                                                       capsys):
    """Die WIRKUNG der Erkennung, ebenfalls auf jedem Wirt.

    Vorher lief `senden` sehenden Auges weiter: Es kannte den Fall, nutzte ihn
    aber nur, um den Fork zu ueberspringen, und legte danach einen PR gegen das
    eigene Repo an.
    """
    m = _modul()
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    monkeypatch.setattr(m, "_eigenes_repo", lambda repo: "maxron84")
    monkeypatch.setattr(m, "_gh_bereit", lambda: (True, ""))

    def darf_nicht(*a, **kw):
        raise AssertionError("Es wurde doch ein Pull Request angelegt.")

    monkeypatch.setattr(m, "_pr_anlegen", darf_nicht)
    a = m.argparse.Namespace(
        projektwurzel=str(projekt), meldungen=str(ordner), kit=str(kit),
        projekt=None, kuerzel=None, repo=None,
        datei=str(ordner / name), ja=True, trotzdem=False)
    assert m.verb_senden(a) == 3
    fehler = capsys.readouterr().err
    assert "ablegen" in fehler and "Eigentümer" in fehler, fehler


@pytest.mark.skipif(os.name == "nt", reason="der gh-Platzhalter ist ein sh-Skript")
def test_der_owner_bekommt_den_ablegen_weg_statt_eines_prs(tmp_path):
    """BL-187: Das Werkzeug ERKANNTE den Fall längst — es nutzte ihn nur, um
    den Fork zu überspringen, und legte danach trotzdem einen PR an."""
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    bin_ordner, protokoll = stelle_gh(tmp_path, "maxron84")
    r = lauf(*_global(projekt, ordner, kit), "senden",
             str(ordner / name), "--ja",
             umgebung={"PATH": f"{bin_ordner}{os.pathsep}{os.environ['PATH']}"})
    assert r.returncode == 3, f"{r.stdout}{r.stderr}"
    assert "ablegen" in r.stderr, (
        f"Der Abbruch nennt den richtigen Weg nicht:\n{r.stderr}")
    getan = protokoll.read_text(encoding="utf-8") if protokoll.exists() else ""
    assert "fork" not in getan and "pr create" not in getan, (
        f"Es ist doch etwas nach außen gegangen:\n{getan}")


@pytest.mark.skipif(os.name == "nt", reason="der gh-Platzhalter ist ein sh-Skript")
def test_ein_fremder_nutzer_geht_weiter_den_pr_weg(tmp_path):
    """Die Gegenrichtung, ohne die der Fall oben auch grün wäre, wenn `senden`
    für JEDEN abbräche — und dann hätte ein fremder Nutzer keinen Weg mehr."""
    kit = baue_kit(tmp_path)
    projekt, ordner, name = _projekt(tmp_path)
    bin_ordner, protokoll = stelle_gh(tmp_path, "jemand-anderes")
    r = lauf(*_global(projekt, ordner, kit), "senden",
             str(ordner / name), "--ja",
             umgebung={"PATH": f"{bin_ordner}{os.pathsep}{os.environ['PATH']}"})
    getan = protokoll.read_text(encoding="utf-8") if protokoll.exists() else ""
    assert "ablegen" not in r.stderr, (
        "Ein fremder Nutzer wird auf den Owner-Weg geschickt, den er nicht "
        f"gehen kann:\n{r.stderr}")
    assert "fork" in getan, (
        f"Der PR-Weg wurde gar nicht erst begonnen:\n{getan}\n{r.stderr}")

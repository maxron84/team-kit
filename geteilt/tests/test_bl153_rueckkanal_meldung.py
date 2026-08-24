"""BL-153 — der Rueckkanal Feld -> Kit ist ein Werkzeug, keine Konvention mehr.

WAS DIESER TEST ABSICHERT UND WARUM
    Bis einschliesslich 2.12.0 war der Rueckweg reine Prosa an drei Stellen, und er nannte den
    Pfad `~/Source/team-kit` — die Ablage EINER Maschine. Wer woandershin
    geklont hatte, bekam eine Anweisung, die ins Leere zeigt; ein fremder
    Nutzer ohnehin. Seit BL-153 gibt es `kit_meldung.py`, und mit ihm vier
    Zusicherungen, die alle Geld oder Vertrauen kosten, wenn sie kippen:

    1. SENDEN IST EINE MENSCHLICHE HANDLUNG. Ein Pull Request wirkt nach
       aussen und laesst sich nicht zurueckholen. Die Meldung schreibt eine
       Rolle, die gerade eine FREMDE, private Codebasis gelesen hat. Ohne
       ausdrueckliche Bestaetigung — und ohne Terminal, an dem gefragt werden
       koennte — darf nichts rausgehen. Das ist dieselbe Trennung wie
       "Finder != Fixer", angewandt auf den Rueckkanal.

    2. DIE REDAKTIONSPRUEFUNG IST EIN GATE, KEIN HINWEIS. Was sie durchlaesst,
       ist gleich oeffentlich. Sie sucht deshalb auch den PROJEKTNAMEN: Das
       Kit fuehrt seine eigenen Feldbelege aus genau diesem Grund unter
       `Feld A`…`Feld D` statt unter Namen (siehe README, Abschnitt Herkunft).

    3. SIE MELDET ALLE GRUENDE EINER ZEILE, NICHT DEN ERSTEN. Der erste
       Entwurf brach nach dem ersten Treffer je Zeile ab. In der Zeile
       "… Token ghp_… Das Projekt <name> lief …" meldet dann die
       Schluesselregel zuerst und der Projektname faellt erst im zweiten
       Durchgang auf. Eine Pruefung, die man dreimal fahren muss, um alles zu
       sehen, erzieht dazu, nach dem ersten Mal zu senden.

    4. EIN KIT WIRD AN ZWEI MARKEN ERKANNT, NICHT AN EINER. Ein Ordner mit
       `plans/backlog.md` ist ein x-beliebiges Projekt MIT T.E.A.M.-
       Installation — genau das, wovon der Rueckkanal wegzeigt. Wuerde das
       Werkzeug ihn fuer das Kit halten, meldete es einen Kit-Fehler in den
       Backlog des meldenden Projekts zurueck.

WARUM DIE ZUSICHERUNGEN AM VERHALTEN HAENGEN
    Alle vier laufen als Prozess gegen gebaute Ablagen unter tmp_path, nicht
    gegen das eigene Repo. Ein Test, der nur die eigene Ablage kennt, ist die
    Bauart, die BL-148 nicht gefunden haette.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import REPO_ROOT, kit_pfad  # noqa: E402

WERKZEUG = kit_pfad("tools", "kit_meldung.py")

pytestmark = pytest.mark.skipif(
    not WERKZEUG.is_file(),
    reason="kit_meldung.py liegt in dieser Ablage nicht")


def lauf(*args, umgebung=None, eingabe=None, cwd=None):
    env = dict(os.environ)
    # Der Kontoname des Wirts wuerde sonst in jeder Testmeldung anschlagen und
    # die Faelle unten von der Maschine abhaengig machen.
    env["USER"] = "pruefkonto"
    env["USERNAME"] = "pruefkonto"
    env.pop("TEAM_KIT_PFAD", None)
    env.pop("TEAM_PROJEKT", None)
    env.update(umgebung or {})
    return subprocess.run([sys.executable, str(WERKZEUG), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          input=eingabe, env=env, cwd=cwd)


def baue_kit(wurzel):
    """Eine Ablage, die das Werkzeug als Kit erkennen MUSS."""
    kit = wurzel / "kit"
    for marke in ("bootstrap/CLAUDE.md.vorlage", "geteilt/tools/kosten.py"):
        p = kit / marke
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    (kit / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [2.13.0] — 2026-08-23\n",
        encoding="utf-8")
    return kit


# --- neu ----------------------------------------------------------------------


def test_neu_legt_entwurf_an_und_nennt_seinen_pfad(tmp_path):
    kit = baue_kit(tmp_path)
    r = lauf("--projektwurzel", str(tmp_path), "--meldungen",
             str(tmp_path / "meldungen"), "--kit", str(kit),
             "neu", "--titel", "Der Installer schreibt CRLF")
    assert r.returncode == 0, r.stderr
    ziel = Path(r.stdout.strip())
    assert ziel.is_file(), "neu hat keinen Pfad ausgegeben, den es gibt"
    text = ziel.read_text(encoding="utf-8")
    for pflicht in ("## Was passiert ist", "## Wo es steckt",
                    "## Warum das jede Installation trifft"):
        assert pflicht in text, f"Die Vorlage fragt {pflicht!r} nicht ab"


def test_neu_traegt_die_kit_version_ein(tmp_path):
    """Ohne sie ist jede Meldung eine Zeitreise.

    Der Empfaenger kann sonst nicht unterscheiden, ob der Fund einen Fehler
    beschreibt, den er letzte Woche behoben hat.
    """
    kit = baue_kit(tmp_path)
    r = lauf("--projektwurzel", str(tmp_path), "--meldungen",
             str(tmp_path / "m"), "--kit", str(kit),
             "neu", "--titel", "Irgendwas")
    assert r.returncode == 0, r.stderr
    assert "2.13.0" in Path(r.stdout.strip()).read_text(encoding="utf-8")


def test_neu_ueberschreibt_keinen_vorhandenen_entwurf(tmp_path):
    kit = baue_kit(tmp_path)
    argv = ["--projektwurzel", str(tmp_path), "--meldungen",
            str(tmp_path / "m"), "--kit", str(kit),
            "neu", "--titel", "Derselbe Titel"]
    assert lauf(*argv).returncode == 0
    zweiter = lauf(*argv)
    assert zweiter.returncode != 0, (
        "Der zweite Aufruf hat den ersten Entwurf ueberschrieben — "
        "Arbeit, die niemand wiederbekommt.")


# --- pruefen ------------------------------------------------------------------


SAUBER = """# Der Installer schreibt CRLF in die Konfiguration

- **Art**: Fehler am Kit
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn

## Was passiert ist

Nach dem Einzug trug jede Zeile der Konfiguration einen Wagenruecklauf.

## Wo es steckt

In der Fuell-Routine, die die Datei ganz liest und ganz zurueckschreibt.
"""


def schreib(tmp_path, text, name="meldung.md"):
    ordner = tmp_path / "m"
    ordner.mkdir(parents=True, exist_ok=True)
    p = ordner / name
    p.write_text(text, encoding="utf-8")
    return p


def test_saubere_meldung_ist_gruen(tmp_path):
    p = schreib(tmp_path, SAUBER)
    r = lauf("--projektwurzel", str(tmp_path), "pruefen", str(p))
    assert r.returncode == 0, f"Fehlalarm auf einer sauberen Meldung:\n{r.stderr}"


@pytest.mark.parametrize("zeile,erwartet", [
    ("Aufgerufen in /home/wernher/projekt.", "absoluter Pfad"),
    (r"Aufgerufen in C:\Users\Wernher\projekt.", "absoluter Windows-Pfad"),
    ("Log ging an wernher@firma.example.", "E-Mail"),
    ("Mit ghp_abcdefghijklmnopqrstuvwx probiert.", "GitHub-Token"),
    ("Der Schluessel sk-ant-api03-xxxxxxxxxxxx stand im Log.", "API-Schlüssel"),
    ("Noch nicht ausgefuellt: TODO", "Vorlage"),
])
def test_redaktion_faengt_was_ins_projekt_zurueckzeigt(tmp_path, zeile, erwartet):
    p = schreib(tmp_path, SAUBER + "\n" + zeile + "\n")
    r = lauf("--projektwurzel", str(tmp_path), "pruefen", str(p))
    assert r.returncode == 4, (
        f"{zeile!r} ist durchgegangen — das landet gleich in einem "
        f"oeffentlichen Repo.\nSTDERR: {r.stderr}")
    assert erwartet in r.stderr, r.stderr


def test_redaktion_faengt_den_projektnamen(tmp_path):
    """Das Kit fuehrt Feldbelege unter `Feld A`…`Feld D`, nicht unter Namen.

    Dieselbe Disziplin gilt fuer fremde Meldungen — sonst steht der Name eines
    privaten Projekts in einem oeffentlichen Repo, weil eine Rolle ihn
    beilaeufig erwaehnt hat.
    """
    p = schreib(tmp_path, SAUBER + "\nDas Projekt Waschbaerbau lief vorher gruen.\n")
    r = lauf("--projektwurzel", str(tmp_path), "--projekt", "Waschbaerbau",
             "pruefen", str(p))
    assert r.returncode == 4, r.stderr
    assert "Feld A" in r.stderr, (
        "Der Befund nennt die Regel nicht, gegen die er anschlaegt — "
        "ein Lint ohne Begruendung wird abgeschaltet statt befolgt.")


def test_alle_gruende_einer_zeile_nicht_nur_der_erste(tmp_path):
    """Die Lehre, die den ersten Entwurf verworfen hat.

    Mit `break` nach dem ersten Treffer verdeckt der auffaelligste Befund die
    leiseren, und der Melder haelt nach einer Runde fuer erledigt, was zwei
    Funde hatte.
    """
    zeile = "Token ghp_abcdefghijklmnopqrstuvwx, Projekt Waschbaerbau, gruen."
    p = schreib(tmp_path, SAUBER + "\n" + zeile + "\n")
    r = lauf("--projektwurzel", str(tmp_path), "--projekt", "Waschbaerbau",
             "pruefen", str(p))
    assert r.returncode == 4
    treffer = [z for z in r.stderr.splitlines() if z.strip().startswith("✗")]
    assert len(treffer) == 1, "Erwartet wird EINE Zeile mit MEHREREN Gruenden"
    assert "GitHub-Token" in treffer[0] and "Feld A" in treffer[0], (
        f"Nur ein Grund gemeldet, der andere bleibt verdeckt:\n{treffer[0]}")


def test_kurze_woerter_werden_nicht_zur_freikarte(tmp_path):
    """Ein zweibuchstabiger Projektname darf keinen Regex bauen, der ueberall passt.

    Sonst ist jede Meldung rot, und ein Lint, der immer rot ist, erzieht zum
    Wegsehen — dieselbe Lehre wie beim Ledger-Konsistenzcheck (Skizze D).
    """
    p = schreib(tmp_path, SAUBER)
    r = lauf("--projektwurzel", str(tmp_path), "--projekt", "ab", "pruefen", str(p))
    assert r.returncode == 0, r.stderr


# --- senden -------------------------------------------------------------------


def stelle_gh(tmp_path):
    """Ein `gh`, das angemeldet meldet und JEDEN Aufruf mitschreibt.

    Ohne ihn faellt `senden` schon an der Vorbedingung auf den Issue-Link
    zurueck und erreicht die Bestaetigungsfrage nie — der Test waere gruen,
    ohne das Tor geprueft zu haben. Das Protokoll ist der eigentliche Beleg:
    Steht am Ende nur `auth status` darin, hat NICHTS nach aussen gewirkt.
    """
    bin_ordner = tmp_path / "bin"
    bin_ordner.mkdir(exist_ok=True)
    protokoll = tmp_path / "gh-aufrufe.txt"
    gh = bin_ordner / "gh"
    gh.write_text(
        "#!/bin/sh\n"
        f'echo "$@" >> "{protokoll}"\n'
        'case "$1 $2" in "auth status") exit 0 ;; esac\n'
        "exit 0\n", encoding="utf-8")
    gh.chmod(0o755)
    return bin_ordner, protokoll


@pytest.mark.skipif(os.name == "nt",
                    reason="der gh-Platzhalter ist ein sh-Skript")
def test_senden_geht_ohne_bestaetigung_und_ohne_terminal_nicht_raus(tmp_path):
    """DIE tragende Zusicherung dieses Werkzeugs.

    Headless gibt es niemanden, der eine Rueckfrage beantwortet. Ein Werkzeug,
    das in dieser Lage trotzdem sendet, veroeffentlicht Text ueber fremden
    Privatcode — und das laesst sich nicht zurueckholen.
    """
    p = schreib(tmp_path, SAUBER)
    bin_ordner, protokoll = stelle_gh(tmp_path)
    r = lauf("--projektwurzel", str(tmp_path), "senden", str(p), eingabe="",
             umgebung={"PATH": f"{bin_ordner}{os.pathsep}{os.environ['PATH']}"})
    assert r.returncode != 0, (
        "senden ist ohne --ja und ohne Terminal durchgelaufen.")
    assert "--ja" in r.stderr, (
        "Der Abbruch sagt nicht, wie man es richtig macht.")
    getan = protokoll.read_text(encoding="utf-8") if protokoll.exists() else ""
    assert "fork" not in getan and "pr create" not in getan, (
        f"Es ist doch etwas nach aussen gegangen:\n{getan}")


@pytest.mark.skipif(os.name == "nt",
                    reason="der gh-Platzhalter ist ein sh-Skript")
def test_ein_nein_an_der_rueckfrage_sendet_nichts(tmp_path):
    """Die Frage muss eine echte Frage sein.

    Eine Rueckfrage, deren Nein nichts aendert, ist Theater — und sie erzieht
    dazu, blind zu bestaetigen.
    """
    p = schreib(tmp_path, SAUBER)
    bin_ordner, protokoll = stelle_gh(tmp_path)
    r = lauf("--projektwurzel", str(tmp_path), "senden", str(p), eingabe="n\n",
             umgebung={"PATH": f"{bin_ordner}{os.pathsep}{os.environ['PATH']}"})
    assert r.returncode != 0
    getan = protokoll.read_text(encoding="utf-8") if protokoll.exists() else ""
    assert "fork" not in getan and "pr create" not in getan, (
        f"Trotz Abbruch ist etwas nach aussen gegangen:\n{getan}")


@pytest.mark.skipif(os.name == "nt",
                    reason="der gh-Platzhalter ist ein sh-Skript")
def test_ohne_gh_faellt_senden_auf_den_issue_link_zurueck(tmp_path):
    """Ein fremder Nutzer ohne `gh` darf nicht abgewiesen werden.

    Er hat vielleicht nur einen Browser und ein Konto. Wer ihn hier stehen
    laesst, bekommt seine Meldung nie — und die Datei muss liegen bleiben,
    damit die Arbeit nicht verloren ist.
    """
    p = schreib(tmp_path, SAUBER)
    leer = tmp_path / "leeres-bin"
    leer.mkdir()
    r = lauf("--projektwurzel", str(tmp_path), "senden", str(p), "--ja",
             umgebung={"PATH": str(leer)})
    assert r.returncode == 3, r.stderr
    assert "issues/new?" in r.stdout, "Kein Ausweg angeboten."
    assert p.exists(), "Die Meldung ist weg — die Arbeit auch."


def test_senden_bricht_bei_redaktionsbefunden_ab_auch_mit_ja(tmp_path):
    """--ja bestaetigt das SENDEN, nicht die Befunde.

    Wer die Redaktionspruefung uebergehen will, sagt das ausdruecklich
    (--trotzdem). Zwei Absichten, zwei Schalter.
    """
    p = schreib(tmp_path, SAUBER + "\nAufgerufen in /home/wernher/projekt.\n")
    r = lauf("--projektwurzel", str(tmp_path), "senden", str(p), "--ja")
    assert r.returncode == 4, (
        f"Eine Meldung mit Redaktionsbefund ging raus.\nSTDERR: {r.stderr}")


def test_senden_meldet_eine_datei_die_es_nicht_gibt(tmp_path):
    r = lauf("--projektwurzel", str(tmp_path), "senden",
             str(tmp_path / "gibtsnicht.md"), "--ja")
    assert r.returncode == 1


# --- Kit finden ---------------------------------------------------------------


def test_ein_projekt_mit_team_installation_ist_kein_kit(tmp_path):
    """Die Zwei-Marken-Regel, und warum sie zwei Marken braucht.

    Ein Ordner mit `plans/backlog.md` ist ein x-beliebiges Projekt MIT
    T.E.A.M. — genau das, wovon der Rueckkanal wegzeigt. Haelt das Werkzeug
    ihn fuer das Kit, meldet es einen Kit-Fehler in den Backlog des meldenden
    Projekts zurueck, und dort bleibt er liegen.
    """
    falsch = tmp_path / "nur-ein-projekt"
    (falsch / "plans").mkdir(parents=True)
    (falsch / "plans" / "backlog.md").write_text("# Backlog", encoding="utf-8")
    (falsch / "team").mkdir()
    r = lauf("--kit", str(falsch), "kit-pfad")
    assert r.returncode == 3, (
        f"Ein Projekt wurde fuer das Kit gehalten:\n{r.stdout}{r.stderr}")
    assert str(falsch) in r.stderr, (
        "Der Fehlschlag nennt den Pfad nicht, der abgelehnt wurde — und ein "
        "ausdruecklich getippter --kit darf auch NICHT still auf ein anderes "
        "Kit ausweichen, sonst arbeitet das Werkzeug gegen eines, das niemand "
        "gemeint hat.")


def test_ausdruecklicher_pfad_schlaegt_die_umgebung(tmp_path):
    """Sonst kann niemand eine falsche Vermutung uebersteuern."""
    kit = baue_kit(tmp_path)
    anderer = tmp_path / "anderes"
    (anderer / "bootstrap").mkdir(parents=True)
    (anderer / "bootstrap" / "CLAUDE.md.vorlage").write_text("x", encoding="utf-8")
    (anderer / "geteilt" / "tools").mkdir(parents=True)
    (anderer / "geteilt" / "tools" / "kosten.py").write_text("x", encoding="utf-8")
    r = lauf("--kit", str(kit), "kit-pfad",
             umgebung={"TEAM_KIT_PFAD": str(anderer)})
    assert r.returncode == 0, r.stderr
    assert str(kit) in r.stdout and str(anderer) not in r.stdout


def test_fehlendes_kit_ist_kein_abbruch_sondern_ein_hinweis(tmp_path):
    """Melden muss auch ohne lokales Kit gehen.

    Ein fremder Nutzer hat es womoeglich gar nicht als Repo liegen — nur die
    Installation. Wer ihn hier abweist, bekommt seine Meldung nie.
    """
    r = lauf("--kit", str(tmp_path / "gibtsnicht"), "kit-pfad",
             umgebung={"HOME": str(tmp_path)})
    assert r.returncode == 3
    assert "TEAM_KIT_PFAD" in r.stderr, "Der Hinweis nennt den Ausweg nicht."


# --- issue-link ---------------------------------------------------------------


def test_issue_link_ist_vorbefuellt_und_zeigt_aufs_kit(tmp_path):
    p = schreib(tmp_path, SAUBER)
    r = lauf("--projektwurzel", str(tmp_path), "issue-link", str(p))
    assert r.returncode == 0, r.stderr
    url = r.stdout.strip()
    assert url.startswith("https://github.com/maxron84/team-kit/issues/new?")
    assert "title=Der+Installer+schreibt+CRLF" in url


def test_ueberlange_meldung_wird_mit_ansage_gekuerzt(tmp_path):
    """Jenseits von rund 8 kB Query antworten Server mit 414.

    Gekuerzt wird deshalb — aber mit ANSAGE, sonst haelt der Empfaenger eine
    halbe Meldung fuer die ganze.
    """
    p = schreib(tmp_path, SAUBER + "\n" + ("Sehr ausfuehrlich. " * 1000))
    r = lauf("--projektwurzel", str(tmp_path), "issue-link", str(p))
    assert r.returncode == 0, r.stderr
    assert "gek%C3%BCrzt" in r.stdout, (
        "Die Kuerzung ist stillschweigend passiert.")


# --- Die Konfiguration, auf beiden Bahnen ------------------------------------

MARKE = "".join(("{{", "KIT_PFAD", "}}"))


@pytest.mark.parametrize("datei", ["bash/entry/team.config.sh",
                                   "pwsh/entry/team.config.ps1"])
def test_beide_konfigurationen_tragen_den_kit_pfad(datei):
    """Der Fund unter dem Fund.

    Das installierte Projekt wusste NIRGENDS, wo das Kit liegt — `TEAM_KIT_PFAD`
    gab es nur im Launcher auf der Kit-Seite. Die Anweisung zum Melden nannte
    deshalb einen festen Pfad, und der stimmte auf genau einer Maschine.
    """
    p = REPO_ROOT / datei
    if not p.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = p.read_text(encoding="utf-8-sig")
    assert "TEAM_KIT_PFAD" in text and MARKE in text, (
        f"{datei} traegt den Kit-Pfad nicht — das Werkzeug ist dann auf Raten "
        f"angewiesen, und ein fremder Nutzer bekommt eine Anweisung ins Leere.")


@pytest.mark.parametrize("datei,muster", [
    ("bash/install.sh", r'\("\{\{KIT_PFAD\}\}", kit_pfad\)'),
    ("pwsh/install.ps1", r"'\{\{KIT_PFAD\}\}'\s*=\s*\$KIT"),
])
def test_beide_installer_fuellen_den_platzhalter(datei, muster):
    """Gleichstand der Bahnen — die Klasse BL-142/BL-144.

    Ein Platzhalter, den nur eine Bahn fuellt, steht auf der anderen woertlich
    in der ausgelieferten Konfiguration. Der Suchlauf in kit-test.sh faende das,
    aber kit-test.ps1 faehrt diesen Schritt nicht (BL-145) — also haengt die
    Zusicherung hier am Quelltext, wo sie auf jedem Wirt greift.
    """
    p = REPO_ROOT / datei
    if not p.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht")
    text = p.read_text(encoding="utf-8-sig")
    assert re.search(muster, text), (
        f"{datei} fuellt {MARKE} nicht — die andere Bahn tut es, und diese "
        f"liefert den Platzhalter woertlich aus.")


def test_bash_installer_fuellt_in_beiden_routinen():
    """Der Update-Pfad hat eine EIGENE Fuell-Routine.

    Genau diese Doppelung hat schon BL-113, BL-119 und BL-137 je einmal
    gekostet: Ein neuer Platzhalter landete in der Erstinstallation und fehlte
    im Update, und ein zurueckgeholtes team.config.ps1 war halb fertig.
    """
    p = REPO_ROOT / "bash/install.sh"
    if not p.is_file():
        pytest.skip("install.sh liegt in dieser Ablage nicht")
    treffer = re.findall(r'\("\{\{KIT_PFAD\}\}", kit_pfad\)',
                         p.read_text(encoding="utf-8"))
    assert len(treffer) == 2, (
        f"{len(treffer)} Fuellung(en) statt zwei — install.sh hat zwei "
        f"Routinen (Erstinstallation und Update), und beide brauchen sie.")

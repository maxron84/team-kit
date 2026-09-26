#!/usr/bin/env python3
"""BL-263: Die Ordner des Stakeholders — Rohmaterial nur lesen, `.obsidian/` gar nicht.

`TEAM_ROHMATERIAL_ORDNER` (Default `raw/ Clippings/`) ist der Eingang des
Menschen: Dort legt er Rohmaterial ab, das das T.E.A.M. verarbeitet —
Notizen und Vorlagen in `raw/`, Web-Clippings in `Clippings/`. Die Ordner sind
bewusst NICHT versioniert (gitignore-Fragment), und das hat eine Kehrseite, die
diese Datei festnagelt: Git sieht sie nicht — also auch der Guard nicht.

Wie knapp das ist, zeigt BL-24. Dort ueberlebte ein manueller Input-Ordner
namens `raw/` einen Harry-Sweep nur, weil der Rollback an Verzeichnissen
scheiterte ("dort ein Gluecksfall"). Seit dem Fix haette er ihn geloescht.

Zugesichert wird, auf BEIDEN Bahnen:
  (1) Ein Schreibzugriff in eine Rohmaterial-Zone wird GEMELDET und zaehlt als
      Uebergriff — der Schnappschuss ersetzt, was Git hier nicht sieht. Das
      gilt auch fuer eine Zone, die erst waehrend des Laufs auftaucht: Das Kit
      legt nur `raw/` an, `Clippings/` entsteht, sobald jemand etwas ablegt.
  (2) NICHTS in einer Zone wird geloescht oder zurueckgesetzt: nicht, wenn der
      Guard nebenan eine echte Verletzung zurueckrollt, und nicht, wenn eine
      Rolle Material mit `git add -f` committet hat.
  (3) `.obsidian/` wird KOMPLETT ignoriert — Obsidian schreibt dort bei jedem
      Klick. Weder angelastet noch zurueckgerollt noch gemeldet, auch in einem
      Projekt, dem die Zeile im .gitignore fehlt.
  (4) Die Einstiege ohne Guard-Abgleich (Ralph, Frank) pruefen die Zonen selbst.

Gegenprobe gefahren: Ohne die Ausnahme in team_pfade_zuruecksetzen fallen die
beiden `git add -f`-Faelle (die Datei ist weg), ohne den Abgleich in
team_guard_verify faellt test_schreibzugriff_wird_gemeldet_und_bleibt_liegen,
ohne TEAM_GUARD_IGNORIERT fallen die beiden `.obsidian/`-Faelle ohne
gitignore-Zeile.
"""
import re
import subprocess
from pathlib import Path

import pytest

from conftest import (Git, Loeschen, Ordner, Ruf, RufMarke, Schreib,
                      entrypoint_pfad, werkzeug_wert)

WURZEL = Path(__file__).resolve().parents[2]
WHITELIST = "^(tests/|plans/)"
MATERIAL = "Mitschrift vom Kundentermin\n"
CLIPPING = "# Artikel\nausgeschnitten\n"


def _git(repo, *befehl):
    return subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout.strip()


def _repo(tmp_path, schale, zonen=("raw", "Clippings"), konfig=None,
          ignoriert=("raw", "Clippings", ".obsidian")):
    """Ein Projekt wie nach dem Einzug: Zonen im .gitignore, darin Material
    des Stakeholders, das NICHT committet ist — so, wie es im Feld liegt."""
    repo = tmp_path / "repo"
    for ordner in ("team", "src", "tests", "plans", *zonen):
        (repo / ordner).mkdir(parents=True, exist_ok=True)
    schale.lib_kopieren(repo)
    werte = {
        "TEAM_DOMAENEN": "produkt",
        "TEAM_PRODUKTIVCODE": "src/",
        "TEAM_TEST_ORDNER": "tests/",
        "TEAM_PLAN_ORDNER": "plans/",
        "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
        "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
    }
    werte.update(konfig or {})
    schale.config_schreiben(repo, werte)
    (repo / ".gitignore").write_text("".join(f"/{o}/\n" for o in ignoriert),
                                     encoding="utf-8")
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    if zonen:
        erste = repo / zonen[0]
        (erste / "notiz.md").write_text(MATERIAL, encoding="utf-8")
        (erste / "tabellen").mkdir()
        (erste / "tabellen" / "preise.csv").write_text("a;1\n", encoding="utf-8")
    if "Clippings" in zonen:
        (repo / "Clippings" / "artikel.md").write_text(CLIPPING, encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        _git(repo, *befehl)
    for zone in zonen:
        assert not _git(repo, "ls-files", zone), f"Vorbedingung: {zone}/ ist unversioniert"
    return repo


def _guard(schale, repo, mutation):
    """Guard-Runde wie in test_bl24: Schnappschuss, Mutation als 'Rolle',
    Abgleich — alles in EINER Shell, weil der Schnappschuss dort lebt."""
    return schale.lauf(
        [Ruf("team_guard_begin"), *mutation,
         RufMarke("team_guard_verify", "harry", WHITELIST, marke="GUARD_OK")],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)


# --- (1) Melden statt schweigen ------------------------------------------------


def test_schreibzugriff_wird_gemeldet_und_bleibt_liegen(tmp_path, schale):
    """Der Kern: Git sieht die Zone nicht, der Schnappschuss schon. Gemeldet
    wird mit Pfad ab der Wurzel — geloescht wird nichts, denn ob die Rolle oder
    der Mensch geschrieben hat, ist nicht zu unterscheiden."""
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Schreib("raw/zusammenfassung.md", "neu\n")])
    assert "GUARD_OK" not in ergebnis.stdout, (
        "Ein Schreibzugriff in die Rohmaterial-Zone zaehlt nicht als Uebergriff "
        "— der Guard sieht den ignorierten Ordner nicht, und der Schnappschuss "
        "greift nicht.\n" + ergebnis.stderr)
    assert "ÜBERGRIFF in der Rohmaterial-Zone" in ergebnis.stderr
    assert re.search(r"neu:\s+raw/zusammenfassung\.md", ergebnis.stderr), ergebnis.stderr
    assert (repo / "raw" / "zusammenfassung.md").exists(), (
        "Die neue Datei in der Zone ist weg — dort wird nie geloescht (BL-263).")
    assert (repo / "raw" / "notiz.md").read_text(encoding="utf-8") == MATERIAL


def test_clippings_ist_ebenfalls_zone(tmp_path, schale):
    """Die zweite Zone des Defaults: Web-Clippings des Stakeholders."""
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Schreib("Clippings/artikel.md", "umgeschrieben\n")])
    assert "GUARD_OK" not in ergebnis.stdout, ergebnis.stderr
    assert re.search(r"geändert:\s+Clippings/artikel\.md", ergebnis.stderr), ergebnis.stderr
    assert (repo / "Clippings" / "artikel.md").exists()


def test_eine_zone_die_waehrend_des_laufs_auftaucht_wird_gemeldet(tmp_path, schale):
    """Das Kit legt Clippings/ nicht an — die Zone kann also mitten im Lauf
    entstehen. Sie wird trotzdem gemeldet, und nichts darin verschwindet."""
    repo = _repo(tmp_path, schale, zonen=("raw",))
    assert not (repo / "Clippings").exists(), "Vorbedingung"
    ergebnis = _guard(schale, repo, [Schreib("Clippings/neu.md", CLIPPING)])
    assert "GUARD_OK" not in ergebnis.stdout, ergebnis.stderr
    assert re.search(r"neu:\s+Clippings/neu\.md", ergebnis.stderr), ergebnis.stderr
    assert (repo / "Clippings" / "neu.md").read_text(encoding="utf-8") == CLIPPING


def test_geaendert_und_entfernt_werden_gemeldet_und_nicht_zurueckgedreht(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Schreib("raw/notiz.md", "ueberschrieben, laenger\n"),
                                     Loeschen("raw/tabellen/preise.csv")])
    assert "GUARD_OK" not in ergebnis.stdout
    assert re.search(r"geändert:\s+raw/notiz\.md", ergebnis.stderr), ergebnis.stderr
    assert re.search(r"entfernt:\s+raw/tabellen/preise\.csv", ergebnis.stderr), ergebnis.stderr
    # Gemeldet, nicht zurueckgedreht: Die Zone hat keine Fassung in Git, aus
    # der sich etwas wiederherstellen liesse — und raten waere schlimmer.
    assert (repo / "raw" / "notiz.md").read_text(encoding="utf-8") == "ueberschrieben, laenger\n"


def test_unveraenderte_zonen_sind_kein_uebergriff(tmp_path, schale):
    """Gegenprobe zu (1): Lesen ist erlaubt und darf nicht rot werden."""
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Schreib("tests/test_neu.py", "t\n")])
    assert "GUARD_OK" in ergebnis.stdout, ergebnis.stderr
    assert "Rohmaterial-Zone" not in ergebnis.stderr


def test_fehlende_zonen_brechen_unter_strikten_optionen_nichts_ab(tmp_path, schale):
    """Ein Projekt ohne Zonen (oder vor dem Update) darf keinen Rollenlauf
    verlieren: `set -euo pipefail` bzw. StrictMode sind hier an."""
    repo = _repo(tmp_path, schale, zonen=())
    ergebnis = _guard(schale, repo, [Schreib("plans/notiz.md", "p\n")])
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "GUARD_OK" in ergebnis.stdout, ergebnis.stderr


def test_abgleich_ohne_startstand_meldet_statt_zu_schweigen(tmp_path, schale):
    """Ohne Schnappschuss liesse sich jede Datei als 'neu' melden — oder gar
    nichts. Beides waere falsch; die Pruefung sagt, dass sie nicht lief."""
    repo = _repo(tmp_path, schale)
    ergebnis = schale.lauf([RufMarke("team_raw_pruefen", "ralph", marke="SAUBER")],
                           cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)
    assert "SAUBER" in ergebnis.stdout
    assert "kein Startstand erfasst" in ergebnis.stderr


def test_die_konfigurierten_ordner_gelten_nicht_der_default(tmp_path, schale):
    """TEAM_ROHMATERIAL_ORDNER ist ein Konfigwert: Die Zonen folgen ihm —
    auch ohne abschliessenden Schraegstrich."""
    repo = _repo(tmp_path, schale, zonen=("eingang",), ignoriert=("eingang",),
                 konfig={"TEAM_ROHMATERIAL_ORDNER": "eingang"})
    ergebnis = _guard(schale, repo, [Schreib("eingang/neu.md", "x\n")])
    assert re.search(r"neu:\s+eingang/neu\.md", ergebnis.stderr), ergebnis.stderr
    assert (repo / "eingang" / "neu.md").exists()


# --- (2) Nie loeschen ------------------------------------------------------------


def test_rollback_einer_echten_verletzung_laesst_die_zonen_stehen(tmp_path, schale):
    """Der Guard rollt eine Verletzung in src/ zurueck — die Zonen daneben
    bleiben Stueck fuer Stueck, wie sie waren."""
    repo = _repo(tmp_path, schale)
    _guard(schale, repo, [Schreib("src/boese.py", "x\n")])
    assert not (repo / "src" / "boese.py").exists(), "Gegenprobe: der Rollback lief"
    assert (repo / "raw" / "notiz.md").read_text(encoding="utf-8") == MATERIAL
    assert (repo / "raw" / "tabellen" / "preise.csv").exists()
    assert (repo / "Clippings" / "artikel.md").read_text(encoding="utf-8") == CLIPPING


def test_mit_git_add_f_committetes_rohmaterial_bleibt_liegen(tmp_path, schale):
    """Der eine Weg, auf dem eine Zone doch in eine Pfadliste geraet: Die Rolle
    committet Material am .gitignore vorbei. Ohne Ausnahme faellt der Pfad in
    den Loesch-Zweig — `rm -rf` auf das Material des Stakeholders."""
    repo = _repo(tmp_path, schale)
    ergebnis = _guard(schale, repo, [Git("add", "-f", "raw/notiz.md"),
                                     Git("commit", "-q", "-m", "rohmaterial mitgenommen")])
    assert "GUARD_OK" not in ergebnis.stdout, "das Committen der Zone ist ein Uebergriff"
    assert (repo / "raw" / "notiz.md").read_text(encoding="utf-8") == MATERIAL, (
        "Der Guard hat Rohmaterial des Stakeholders geloescht (BL-263).")
    assert "NICHT angefasst" in ergebnis.stderr
    assert "AUSGENOMMEN die Rohmaterial-Zone" in ergebnis.stderr, (
        "Die Vollzugsmeldung behauptet einen vollstaendigen Rollback, obwohl "
        "die Zone bewusst stehen blieb — die BL-24-Bauart.")
    assert not _git(repo, "ls-files", "raw"), (
        "Die Datei steht noch im Index: Der naechste Commit versionierte die "
        "Zone, die unversioniert sein soll.")


def test_rollback_der_rolle_verschont_committetes_rohmaterial(tmp_path, schale):
    """Dasselbe fuer team_rollback_rolle (Frank, Axel, Red Team bei Exit 42):
    HEAD wandert zurueck, das Material bleibt auf der Platte."""
    repo = _repo(tmp_path, schale)
    start = _git(repo, "rev-parse", "HEAD")
    ergebnis = schale.lauf(
        [Ruf("team_guard_begin"),
         Git("add", "-f", "Clippings/artikel.md"),
         Git("commit", "-q", "-m", "rohmaterial mitgenommen"),
         Schreib("src/app.py", "x = 2\n"),
         Ruf("team_rollback_rolle", "frank", start)],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)
    assert _git(repo, "rev-parse", "HEAD") == start, ergebnis.stderr
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "x = 1\n", \
        "Gegenprobe: der Rest des Rollbacks lief"
    assert (repo / "Clippings" / "artikel.md").exists(), (
        "team_rollback_rolle hat Rohmaterial des Stakeholders geloescht (BL-263).\n"
        + ergebnis.stderr)


# --- (3) .obsidian/ komplett ignoriert -------------------------------------------


@pytest.mark.parametrize("mit_zeile", [True, False], ids=["mit_gitignore_zeile", "ohne_gitignore_zeile"])
def test_obsidian_wird_im_guard_komplett_ignoriert(tmp_path, schale, mit_zeile):
    """Obsidian schreibt waehrend eines Laufs in seine Arbeitsflaeche. Das ist
    weder ein Uebergriff noch etwas, das zurueckgerollt wird — auch nicht in
    einem Projekt, dem die Zeile im .gitignore fehlt (vor dem Update angelegt)."""
    ignoriert = ("raw", "Clippings", ".obsidian") if mit_zeile else ("raw", "Clippings")
    repo = _repo(tmp_path, schale, ignoriert=ignoriert)
    ergebnis = _guard(schale, repo, [Schreib(".obsidian/workspace.json", "{}\n")])
    assert "GUARD_OK" in ergebnis.stdout, (
        "Obsidians Arbeitsflaeche wurde einer Rolle angelastet (BL-263).\n" + ergebnis.stderr)
    assert (repo / ".obsidian" / "workspace.json").exists(), (
        "Der Guard hat die Arbeitsflaeche des Stakeholders zurueckgerollt.")
    assert "Rohmaterial-Zone" not in ergebnis.stderr, "`.obsidian/` wird nicht ueberwacht"


def test_rollback_der_rolle_laesst_obsidian_stehen(tmp_path, schale):
    repo = _repo(tmp_path, schale, ignoriert=("raw", "Clippings"))
    start = _git(repo, "rev-parse", "HEAD")
    ergebnis = schale.lauf(
        [Ruf("team_guard_begin"),
         Ordner(".obsidian/plugins"),
         Schreib(".obsidian/plugins/data.json", "{}\n"),
         Schreib("src/app.py", "x = 2\n"),
         Ruf("team_rollback_rolle", "frank", start)],
        cwd=repo, lib=repo / "team" / schale.lib_name, strikt=True)
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "x = 1\n", \
        "Gegenprobe: der Rest des Rollbacks lief"
    assert (repo / ".obsidian" / "plugins" / "data.json").exists(), (
        "team_rollback_rolle hat die Arbeitsflaeche des Stakeholders geloescht.\n"
        + ergebnis.stderr)


# --- (4) Die Einstiege ohne Guard-Abgleich ---------------------------------------


@pytest.mark.parametrize("rolle", ["ralph", "frank"])
def test_einstiege_ohne_guard_abgleich_pruefen_die_zonen(rolle, schale):
    """Ralph hat keinen Guard, Frank nur den Schnappschuss — beide schreiben
    mit bypassPermissions. Ohne eigenen Abgleich bliebe ein Uebergriff dort
    unsichtbar. Die Dateien schreibt `--update` neu, daher gilt der Test auch
    in einer aktualisierten Installation."""
    skript = entrypoint_pfad(schale.entrypoint(rolle))
    if not skript.is_file():
        pytest.skip(f"{skript.name} liegt hier nicht (Bahn abgewaehlt)")
    text = skript.read_text(encoding="utf-8-sig")
    assert "team_raw_pruefen" in text, (
        f"{skript.name} prueft die Rohmaterial-Zonen nicht (BL-263).")
    if rolle == "ralph":
        assert "team_raw_begin" in text, (
            f"{skript.name} nimmt keinen Startstand der Zonen — ohne ihn meldet "
            "der Abgleich nur 'nicht geprueft'.")


def test_bibliothek_setzt_die_zonen_als_default(schale):
    """Auch ein Projekt, dessen team.config.* vor BL-263 entstand (`--update`
    fasst sie nicht an), bekommt die Zonen — ueber den Bibliotheks-Default."""
    quelle = schale.kit_lib.read_text(encoding="utf-8-sig")
    treffer = re.search(schale.default_muster("TEAM_ROHMATERIAL_ORDNER"), quelle, re.M)
    assert treffer, f"{schale.lib_name} setzt keinen Default fuer TEAM_ROHMATERIAL_ORDNER"
    assert treffer.group(1) == "raw/ Clippings/"
    assert re.search(r"TEAM_GUARD_IGNORIERT ?= ?'\^\\\.obsidian", quelle), (
        f"{schale.lib_name} nimmt `.obsidian/` nicht vom Guard aus.")


# --- Auslieferung: Regeltext, Fragment, Installer (nur in der Kit-Ablage) --------


def _kit_datei(*teile):
    pfad = WURZEL.joinpath(*teile)
    if not pfad.is_file():
        pytest.skip(f"{'/'.join(teile)} liegt nur in der Kit-Ablage — "
                    "eine Installation traegt die Vorlage nicht mit")
    return pfad.read_text(encoding="utf-8")


def test_das_fragment_nimmt_alle_drei_ordner_aus_der_versionierung():
    zeilen = _kit_datei("bootstrap", "gitignore.fragment").splitlines()
    for zeile in ("/raw/", "/Clippings/", "/.obsidian/"):
        assert zeile in zeilen, (
            f"Das gitignore-Fragment nimmt {zeile} nicht heraus (BL-263).")


def test_die_regeldatei_nennt_die_zonen_fuer_jede_rolle():
    text = _kit_datei("bootstrap", "CLAUDE.md.vorlage")
    assert "## Rohmaterial des Stakeholders — nur lesen" in text
    assert "**Jede Rolle liest dort nur.**" in text
    assert "TEAM_ROHMATERIAL_ORDNER" in text
    assert "**`.obsidian/` ist tabu.**" in text


def test_beide_konfigurationen_tragen_den_wert():
    """test_bl200 haelt die Schluesselmengen gleich; hier geht es um den WERT."""
    bash = _kit_datei("bash", "entry", "team.config.sh")
    pwsh = _kit_datei("pwsh", "entry", "team.config.ps1")
    assert 'TEAM_ROHMATERIAL_ORDNER="${TEAM_ROHMATERIAL_ORDNER:-raw/ Clippings/}"' in bash
    assert "$TEAM_ROHMATERIAL_ORDNER = Team-Wert 'TEAM_ROHMATERIAL_ORDNER' 'raw/ Clippings/'" in pwsh


@pytest.mark.parametrize("installer", [("bash", "install.sh"), ("pwsh", "install.ps1")])
def test_beide_installer_legen_nur_raw_an(installer):
    """raw/ ist Teil der Auslieferung; Clippings/ und .obsidian/ erzeugt das
    Kit nie — sie tauchen auf, sobald der Stakeholder sie benutzt. Der
    Gleichstand der Baeume (kit-test.sh, Stufe 11) prueft das Ergebnis; hier
    steht, dass es gewollt ist."""
    text = _kit_datei(*installer)
    assert re.search(r"""(mkdir -p "\$ZIEL/raw"|Join-Path \$Ziel 'raw')""", text), (
        f"{installer[1]} legt raw/ nicht an (BL-263).")
    assert not re.search(r"""(mkdir -p "\$ZIEL/(clippings|Clippings|\.obsidian)"|"""
                         r"""Join-Path \$Ziel '(clippings|Clippings|\.obsidian)')""", text), (
        f"{installer[1]} legt Clippings/ oder .obsidian/ an — die erzeugt das Kit nicht.")

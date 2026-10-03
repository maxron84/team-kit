#!/usr/bin/env python3
"""BL-236, BL-271, BL-206 (2), BL-274: Der Rollback und die Commit-Stellen
behandeln fremde Arbeit als fremd — auch die, die WAEHREND eines Laufs
entsteht.

BL-236 (`Feld B`, 2026-09-07)
    Der Rollback der Fixphase setzte HEAD hart auf den beim Start gemerkten
    Commit und warf einen Doku-Commit weg, den eine zweite Sitzung
    waehrenddessen angelegt hatte. Jetzt haelt er an und gibt den Fall an den
    Menschen, sobald ein Commit seit dem Start nicht die Kennung des Laufs
    traegt (bei Frank die Fundnummer; `-` = die Rolle committet nie).

BL-271 (2) / BL-206 (2) (`Feld B`)
    Der Rollback setzte einen beim Start schon schmutzigen Pfad auf den
    Start-COMMIT zurueck — die fremde, uncommittete Arbeit daran war weg. Der
    Schnappschuss legt die Blobs jetzt ab, und der Rollback stellt den Stand
    VOR der Rolle wieder her.

BL-274 (`Feld B`)
    Axel, Frank und Ralphs Auffangpfad stagten blanko (`git add <ordner>`,
    `git add -A`). `team_eigene_stagen` staged namentlich, was der Lauf
    angefasst hat.
"""
import subprocess

from conftest import Git, Ruf, Schreib


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True,
                          encoding="utf-8").stdout.strip()


def _repo(tmp_path, schale):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "plans").mkdir()
    (repo / "team").mkdir()
    (repo / "team" / schale.lib_name).write_bytes(schale.kit_lib.read_bytes())
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "plans" / "notizen.md").write_text("alt\n", encoding="utf-8")
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"], ["add", "-A"],
                   ["commit", "-q", "-m", "start"]):
        _git(repo, *befehl)
    return repo


def _lauf(repo, schale, schritte):
    return schale.lauf(schritte, cwd=repo,
                       lib=repo / "team" / schale.lib_name, strikt=False)


# --- BL-236 ---------------------------------------------------------------------

def test_ein_fremder_commit_haelt_den_rollback_an(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    start = _git(repo, "rev-parse", "HEAD")
    r = _lauf(repo, schale, [
        Ruf("team_guard_begin"),
        Schreib("src/app.py", "x = 2  # Franks Fix\n"),
        Git("commit", "-qam", "fix(uat): Grenze (HM-7)"),
        Schreib("plans/fundliste.md", "von Hand\n"),
        Git("add", "plans/fundliste.md"),
        Git("commit", "-qm", "docs: Fundliste von Hand"),
        Ruf("team_rollback_rolle", "frank", start, "HM-7")])
    assert "ROLLBACK ANGEHALTEN" in r.stderr and "Kit-BL-236" in r.stderr, r.stderr
    assert "Fundliste von Hand" in r.stderr, r.stderr
    log = _git(repo, "log", "--format=%s")
    assert "docs: Fundliste von Hand" in log, (
        f"{schale.name}: Der fremde Commit ist aus der Historie verschwunden "
        f"(BL-236).\n{log}")
    assert (repo / "plans" / "fundliste.md").exists()


def test_nur_eigene_commits_werden_zurueckgerollt(tmp_path, schale):
    """Gegenrichtung: Der Rollback funktioniert weiter, wenn alles eigen ist."""
    repo = _repo(tmp_path, schale)
    start = _git(repo, "rev-parse", "HEAD")
    _lauf(repo, schale, [
        Ruf("team_guard_begin"),
        Schreib("src/app.py", "x = 2\n"),
        Git("commit", "-qam", "fix(uat): Grenze (HM-7)"),
        Ruf("team_rollback_rolle", "frank", start, "HM-7")])
    assert _git(repo, "rev-parse", "HEAD") == start
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "x = 1\n"


def test_eine_rolle_ohne_eigene_commits_haelt_bei_jedem_an(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    start = _git(repo, "rev-parse", "HEAD")
    r = _lauf(repo, schale, [
        Ruf("team_guard_begin"),
        Schreib("plans/von-hand.md", "x\n"),
        Git("add", "plans/von-hand.md"),
        Git("commit", "-qm", "docs: von Hand"),
        Ruf("team_rollback_rolle", "axel", start, "-")])
    assert "ROLLBACK ANGEHALTEN" in r.stderr, r.stderr
    assert "docs: von Hand" in _git(repo, "log", "--format=%s")


# --- BL-271 (2) / BL-206 (2) -------------------------------------------------

def test_eine_vorab_schmutzige_datei_geht_auf_den_stand_vor_der_rolle(tmp_path,
                                                                      schale):
    repo = _repo(tmp_path, schale)
    (repo / "plans" / "notizen.md").write_text("alt\nMENSCH, uncommittet\n",
                                               encoding="utf-8")
    start = _git(repo, "rev-parse", "HEAD")
    r = _lauf(repo, schale, [
        Ruf("team_guard_begin"),
        Schreib("plans/notizen.md", "die Rolle hat alles ersetzt\n"),
        Ruf("team_rollback_rolle", "frank", start, "HM-7")])
    text = (repo / "plans" / "notizen.md").read_text(encoding="utf-8")
    assert text == "alt\nMENSCH, uncommittet\n", (
        f"{schale.name}: Die uncommittete fremde Arbeit ist weg — der Rollback "
        f"hat den Start-COMMIT zurueckgeholt (BL-271).\n{r.stderr}")
    assert "Kit-BL-271" in r.stderr, r.stderr


# --- BL-274 -----------------------------------------------------------------------

def test_stagen_nimmt_nur_eigenes(tmp_path, schale):
    repo = _repo(tmp_path, schale)
    (repo / "plans" / "closeout-entwurf.md").write_text("Architekt, uncommittet\n",
                                                        encoding="utf-8")
    _lauf(repo, schale, [
        Ruf("team_guard_begin"),
        Schreib("plans/ermittlungsakten/AX-1.md", "# AX-1\n"),
        Ruf("team_eigene_stagen", "plans/")])
    gestaged = _git(repo, "diff", "--cached", "--name-only")
    assert "plans/ermittlungsakten/AX-1.md" in gestaged, gestaged
    assert "closeout-entwurf.md" not in gestaged, (
        f"{schale.name}: Die uncommittete Closeout-Ausgabe des Architekten "
        f"wurde mitgestaged (BL-274).\n{gestaged}")


def test_die_aufrufer_stagen_nicht_mehr_blanko():
    """Die drei Stellen aus der Meldung, am Quelltext beider Bahnen."""
    from pathlib import Path
    from conftest import entrypoint_pfad
    for datei, verboten in (("axel.sh", 'git add "$TEAM_PLAN_ORDNER"'),
                            ("frank.sh", 'git add "$TEAM_BEUTEBUCH"'),
                            ("ralph.sh", "git add -A"),
                            ("axel.ps1", "git add $TEAM_PLAN_ORDNER"),
                            ("frank.ps1", "git add $TEAM_BEUTEBUCH"),
                            ("ralph.ps1", "git add -A")):
        pfad = Path(entrypoint_pfad(datei))
        if not pfad.is_file():
            continue
        code = "\n".join(z for z in pfad.read_text(encoding="utf-8-sig").splitlines()
                         if not z.lstrip().startswith("#")
                         and "nie 'git add -A'" not in z)
        assert verboten not in code, f"{datei} staged weiter blanko (BL-274)"

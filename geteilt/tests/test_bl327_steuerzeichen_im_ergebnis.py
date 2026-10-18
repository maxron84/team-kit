#!/usr/bin/env python3
r"""BL-327: Auf dem Weg in die Datei werden Backslash-Escapes zu Steuerzeichen.

WAS IM FELD PASSIERT IST (`Feld F`, 2026-10-11 und 2026-10-16)
    Frank schrieb in zwei Fixen eine Zusicherung wie
    `assert not re.search(r"..._name\b", text)`. In der Datei stand danach an
    Stelle von `\b` das Byte 0x08: Das Muster verlangt ein Backspace im
    geprueften Text, trifft nie und kann nie mehr rot werden. Keine Probe des
    Teams schlug an. Fuenf Tage spaeter setzte Franks letzter Docs-Commit ein
    BEL ins CHANGELOG (`.\abnahme.cmd` ueber einen Python-String), und die
    Vollautomatik meldete "beendet" auf einem roten HEAD (`BL-341`). Im Kit
    selbst stand dieselbe Bauart im Archiv, Eintrag `BL-234`: zweimal 0x08,
    wo in `REFERENZ_RE` ein `\b` stand.

WAS GEBAUT IST
    1. `team/tools/steuerzeichen.py` - EINE Pruefung fuer beide Bahnen: Bytes
       unter 0x20 ausser Tab und LF sind verboten, ein CR nur direkt vor
       einem LF erlaubt. Gemeldet wird Datei:Zeile, das Byte und das
       wahrscheinliche Escape. Binaer (ein NUL in den ersten 8000 Bytes)
       wird uebersprungen.
    2. Die SCHREIBENDEN Rollen rufen sie nach dem Rollenaufruf: Frank ueber
       START_HASH..HEAD, Ralph ueber die Commits der Stufe. Ein Fund wird zum
       eigenen Ausgang 45 - kein Rollback und kein Fehlversuch, die Arbeit
       bleibt stehen, aber der Lauf meldet sich nicht als fertig.
    3. Ein Kit-Test ueber die eigenen versionierten Dateien. Er laeuft nur im
       Kit: In einer Installation urteilte er sonst ueber das ganze
       Feldprojekt (der Fehlermodus aus `BL-340`).
    4. Ein Satz im Briefing von Ralph und Frank.

WIE DIE STEUERZEICHEN IN DIESE DATEI KOMMEN: GAR NICHT
    Jedes Byte, das ein Fall braucht, entsteht zur Laufzeit aus seiner Zahl
    (`bytes([0x08])`). Stuende eines hier im Quelltext, waere der Kit-Test
    unten an seinem eigenen Pruefling rot - und wer die Datei ueber einen
    Heredoc schreibt, erzeugte genau die Bauart, die sie finden soll.

WARUM `BASH` HIER NICHT IMPORTIERT WIRD
    Der Harnisch ueberspringt ein Modul GANZ, das `BASH` importiert, sobald
    die Bash fehlt (`conftest.pytest_collection_modifyitems`). Die Faelle zum
    Werkzeug und die pwsh-Zwillinge brauchen keine Bash; der eine Fall, der
    sie braucht, fragt `verlange_bash()` selbst.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conftest  # noqa: E402
from conftest import (entrypoint_pfad, kit_pfad,  # noqa: E402
                      kopiere_team_namensraum, pfad_voran, verlange_bash,
                      werkzeug_wert)

WURZEL = Path(__file__).resolve().parents[2]
WERKZEUG = kit_pfad("tools", "steuerzeichen.py")

# Die Bytes, aus ihrer Zahl gebaut (siehe Kopf).
NUL, BEL, BS, TAB, LF, VT, FF, CR, ESC = (
    bytes([n]) for n in (0x00, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x1B))


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout.strip()


def _repo(tmp_path, dateien=None):
    """Ein Wegwerf-Repo mit einem ersten Commit. `core.autocrlf` ist aus,
    damit die Bytes so im Repo stehen, wie der Fall sie schreibt - auch auf
    einem Windows-Wirt, dessen Git CRLF umsetzt."""
    repo = tmp_path / "repo"
    repo.mkdir()
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"],
                   ["config", "core.autocrlf", "false"]):
        _git(repo, *befehl)
    (repo / "README.md").write_bytes(b"# Projekt" + LF)
    for name, inhalt in (dateien or {}).items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_bytes(inhalt)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "start")
    return repo


def _pruefe(cwd, *args):
    if not WERKZEUG.is_file():
        pytest.fail(f"{WERKZEUG.name} fehlt - die Pruefung aus BL-327 ist nicht "
                    f"gebaut ({WERKZEUG}).")
    return subprocess.run([sys.executable, str(WERKZEUG), *args], cwd=str(cwd),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


# --- (1) Die Regel, am Werkzeug ----------------------------------------------

def test_ein_backspace_in_einer_geaenderten_testdatei_nennt_datei_und_zeile(tmp_path):
    """Der Feldfall: Aus der Wortgrenze wurde 0x08, die Zusicherung kann nie
    mehr rot werden. Die Meldung muss den Ort nennen - sonst sucht der Mensch
    mit `cat -A` durch jede Datei des Commits."""
    sauber = (b"import re" + LF + LF + b"def test_name():" + LF
              + rb'    assert not re.search(r"alt_name\b", "neu_name")' + LF)
    repo = _repo(tmp_path, {"tests/test_name.py": sauber})
    (repo / "tests" / "test_name.py").write_bytes(
        sauber.replace(rb"\b", BS))
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 3, (
        f"Ein Backspace in einer geaenderten Testdatei bleibt unbemerkt "
        f"(BL-327).\n{r.stdout}\n{r.stderr}")
    assert "tests/test_name.py:4:" in r.stdout, (
        f"Die Meldung nennt Datei und Zeile nicht.\n{r.stdout}")
    assert "0x08" in r.stdout and r"\b" in r.stdout, (
        f"Die Meldung nennt das Byte oder sein wahrscheinliches Escape nicht."
        f"\n{r.stdout}")


def test_eine_crlf_datei_geht_durch(tmp_path):
    """Ein CR direkt vor dem LF ist ein Windows-Zeilenende, kein Escape."""
    repo = _repo(tmp_path)
    (repo / "windows.txt").write_bytes(b"erste" + CR + LF + b"zweite" + CR + LF)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 0, (
        f"Eine Datei mit CRLF gilt als Fund - dann waere jede unter Windows "
        f"geschriebene Datei rot.\n{r.stdout}\n{r.stderr}")


def test_ein_einzelnes_cr_mitten_im_text_wird_gefunden(tmp_path):
    """Der Nachtrag der Meldung: Aus `.\\run.cmd` wurde ein CR mitten in der
    Zeile. Die Regel "ausser Tab, LF und CR" haette ihn durchgelassen."""
    repo = _repo(tmp_path)
    (repo / "pfad.md").write_bytes(b"Aufruf: `." + CR + b"un.cmd`" + LF
                                   + b"weiter" + LF)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 3, f"{r.stdout}\n{r.stderr}"
    assert "pfad.md:1:" in r.stdout and "0x0D" in r.stdout, r.stdout
    assert r"\r" in r.stdout, r.stdout


def test_ein_cr_am_dateiende_wird_gefunden(tmp_path):
    """Auch am Dateiende steht ein CR allein: Es folgt kein LF."""
    repo = _repo(tmp_path)
    (repo / "ende.md").write_bytes(b"eins" + LF + b"zwei" + CR)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 3, f"{r.stdout}\n{r.stderr}"
    assert "ende.md:2:" in r.stdout, r.stdout


def test_eine_binaerdatei_wird_uebersprungen(tmp_path):
    repo = _repo(tmp_path)
    (repo / "bild.bin").write_bytes(b"KOPF" + NUL + BEL + BS + CR + b"rest")
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 0, (
        f"Eine Binaerdatei wurde als Text gelesen.\n{r.stdout}\n{r.stderr}")


@pytest.mark.parametrize("stelle,erwartet", [(7999, 0), (8000, 3)],
                         ids=["nul_in_den_ersten_8000", "nul_dahinter"])
def test_binaer_heisst_ein_nul_in_den_ersten_8000_bytes(tmp_path, stelle,
                                                       erwartet):
    """Dieselbe Grenze, an der git eine Datei fuer den Diff als binaer zaehlt.
    Ein NUL dahinter macht die Datei nicht binaer - dann ist es selbst ein
    Steuerzeichen."""
    repo = _repo(tmp_path)
    (repo / "lang.txt").write_bytes(b"a" * stelle + NUL + b"b" + LF)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == erwartet, f"{r.stdout}\n{r.stderr}"
    if erwartet:
        assert "lang.txt:1:" in r.stdout and "0x00" in r.stdout, r.stdout


def test_tab_und_lf_sind_erlaubt(tmp_path):
    """Die Kehrseite, und sie ist der blinde Fleck: Ein Tab und ein LF sind
    erlaubt - also sieht die Regel ein `\\t`, das zum Tabulator wurde, nicht."""
    repo = _repo(tmp_path)
    (repo / "Makefile").write_bytes(b"alle:" + LF + TAB + b"echo ok" + LF)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"


@pytest.mark.parametrize("byte,escape", [
    (0x07, r"\a"), (0x08, r"\b"), (0x0B, r"\v"), (0x0C, r"\f"),
    (0x0D, r"\r"), (0x1B, r"\e"), (0x01, r"\1"),
], ids=["BEL", "BS", "VT", "FF", "CR", "ESC", "oktal"])
def test_das_wahrscheinliche_escape_wird_genannt(tmp_path, byte, escape):
    """Die Spur zurueck zur Stelle im Code, die das Zeichen geschrieben hat."""
    repo = _repo(tmp_path)
    (repo / "f.txt").write_bytes(b"vor" + bytes([byte]) + b"nach" + LF)
    r = _pruefe(repo, "pruefen", "f.txt")
    assert r.returncode == 3, f"{r.stdout}\n{r.stderr}"
    assert f"0x{byte:02X}" in r.stdout and escape in r.stdout, r.stdout


def test_die_meldung_benennt_den_blinden_fleck(tmp_path):
    """Benennen statt wegdiskutieren: Wer den Fund liest, soll wissen, dass
    ein `\\t` und ein `\\n` durchgehen."""
    repo = _repo(tmp_path)
    (repo / "f.txt").write_bytes(b"x" + BEL + LF)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 3, r.stdout
    assert "Tabulator" in r.stdout and "Zeilenumbruch" in r.stdout, r.stdout


# --- (2) Der Ausweg fuer Absicht ---------------------------------------------

def test_eine_fixture_mit_absicht_steht_in_gitattributes(tmp_path):
    """Eine Datei, die Steuerzeichen ABSICHTLICH traegt (hier ANSI-Farben),
    braucht einen ausdruecklichen Ausweg. Er steht versioniert in
    .gitattributes und ist im Diff sichtbar - und die Pruefung sagt, dass sie
    ihn genommen hat, statt still zu schweigen."""
    farbe = ESC + b"[31mrot" + ESC + b"[0m" + LF
    repo = _repo(tmp_path, {".gitattributes":
                            b"tests/fixtures/*.txt steuerzeichen-erlaubt" + LF})
    (repo / "tests" / "fixtures").mkdir(parents=True)
    (repo / "tests" / "fixtures" / "farbe.txt").write_bytes(farbe)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 0, (
        f"Die erlaubte Fixture zaehlt als Fund.\n{r.stdout}\n{r.stderr}")
    assert "farbe.txt" in r.stdout and "steuerzeichen-erlaubt" in r.stdout, (
        f"Der Ausweg wird still genommen - dann sieht niemand, dass er "
        f"benutzt wurde.\n{r.stdout}")


def test_ohne_den_eintrag_ist_dieselbe_fixture_ein_fund(tmp_path):
    """Gegenprobe zum Ausweg: Er gilt nur, wo er steht."""
    repo = _repo(tmp_path)
    (repo / "farbe.txt").write_bytes(ESC + b"[31mrot" + LF)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 3, r.stdout
    assert "farbe.txt:1:" in r.stdout and r"\e" in r.stdout, r.stdout


def test_ein_binary_attribut_zaehlt_wie_git_es_zaehlt(tmp_path):
    """`binary` in .gitattributes macht die Datei auch fuer git binaer."""
    repo = _repo(tmp_path, {".gitattributes": b"*.dat binary" + LF})
    (repo / "werte.dat").write_bytes(b"x" + BEL + BS + b"y")
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"


# --- (3) Was geprueft wird -----------------------------------------------------

def test_seit_prueft_die_commits_im_committeten_stand(tmp_path):
    """Frank und Ralph werden ueber ihre COMMITS geurteilt. Ein Arbeitsbaum,
    der den Fehler schon nicht mehr traegt, spricht den Commit nicht frei;
    eine geloeschte Datei ist kein Fehler; was vor dem Bereich lag, gehoert
    nicht dazu."""
    repo = _repo(tmp_path, {"alt.md": b"vorher" + BS + LF,
                            "weg.txt": b"geht" + LF})
    start = _git(repo, "rev-parse", "HEAD")
    (repo / "CHANGELOG.md").write_bytes(
        b"# Changelog" + LF + b"- Aufruf `." + BEL + b"bnahme.cmd`" + LF)
    _git(repo, "rm", "-q", "weg.txt")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "docs")
    (repo / "CHANGELOG.md").write_bytes(
        b"# Changelog" + LF + rb"- Aufruf `.\abnahme.cmd`" + LF)
    r = _pruefe(repo, "pruefen", "--seit", start)
    assert r.returncode == 3, f"{r.stdout}\n{r.stderr}"
    assert "CHANGELOG.md:2:" in r.stdout and "0x07" in r.stdout, r.stdout
    assert "alt.md" not in r.stdout, (
        f"Ein Byte VOR dem Bereich wird dem Bereich angelastet.\n{r.stdout}")
    sauber = _pruefe(repo, "pruefen")
    assert sauber.returncode == 0, (
        f"Der reparierte Arbeitsbaum gilt weiter als Fund.\n{sauber.stdout}")


def test_versioniert_prueft_alle_versionierten_dateien(tmp_path):
    repo = _repo(tmp_path, {"alt.md": b"vorher" + BS + LF})
    (repo / "neu.md").write_bytes(b"lose" + BS + LF)
    r = _pruefe(repo, "pruefen", "--versioniert")
    assert r.returncode == 3, f"{r.stdout}\n{r.stderr}"
    assert "alt.md:1:" in r.stdout, r.stdout
    assert "neu.md" not in r.stdout, (
        f"Eine unversionierte Datei zaehlt zu den versionierten.\n{r.stdout}")


def test_benannte_dateien_auch_ausserhalb_von_git(tmp_path):
    """Ein Werkzeug fuer beide Bahnen und jedes Projekt: Wer Dateien nennt,
    braucht kein Git."""
    (tmp_path / "frei.txt").write_bytes(b"a" + FF + b"b" + LF)
    r = _pruefe(tmp_path, "pruefen", "frei.txt")
    assert r.returncode == 3, f"{r.stdout}\n{r.stderr}"
    assert "frei.txt:1:" in r.stdout and r"\f" in r.stdout, r.stdout


def test_ein_sauberer_stand_meldet_sich_als_sauber(tmp_path):
    repo = _repo(tmp_path)
    (repo / "neu.md").write_bytes("Umlaute: äöü — Gedankenstrich".encode("utf-8") + LF)
    r = _pruefe(repo, "pruefen")
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"


def test_die_bedienung(tmp_path):
    """Hilfe mit Exit 0, Bedienfehler mit Exit 2 - nie ein Traceback und nie
    ein stilles Ja (`BL-223`, `BL-329`)."""
    hilfe = _pruefe(tmp_path, "--hilfe")
    assert hilfe.returncode == 0, hilfe.stderr
    assert "steuerzeichen-erlaubt" in hilfe.stdout, hilfe.stdout
    assert "Tabulator" in hilfe.stdout, (
        f"Die Hilfe nennt den blinden Fleck nicht.\n{hilfe.stdout}")
    for args in (("pruefen", "--unsinn"), ("pruefen", "--seit"), (),
                 ("pruefen", "--seit", "HEAD", "--versioniert")):
        r = _pruefe(tmp_path, *args)
        assert r.returncode == 2, f"{args}: {r.returncode}\n{r.stdout}{r.stderr}"
        assert "Traceback" not in r.stderr, r.stderr


# --- (4) Das Kit selbst ------------------------------------------------------

def test_das_kit_traegt_keine_steuerzeichen():
    """Die Regel gilt auch fuer das Kit - es hatte die Bauart selbst, im
    Archiv, Eintrag `BL-234`, und kein Waechter bemerkte sie.

    NUR IM KIT, mit derselben Marke wie `test_bl267`: Alles unter
    `geteilt/tests/` wird nach `team/tests/` mitinstalliert. Dort urteilte
    dieser Fall ueber das ganze Feldprojekt, und ein fremdes Steuerzeichen
    machte die Suite des Projekts rot - der Fehlermodus, an dem in `Feld F`
    eine Abnahme verworfen wurde (`BL-340`). Im Projekt pruefen Frank und
    Ralph das, was sie schreiben; dieser Fall prueft das Kit.
    """
    if not (WURZEL / "bootstrap" / "CLAUDE.md.vorlage").is_file():
        pytest.skip("installierte Ablage - dieser Fall prueft das Kit, nicht "
                    "das Projekt (Kit-BL-327)")
    if subprocess.run(["git", "-C", str(WURZEL), "rev-parse", "--git-dir"],
                      capture_output=True).returncode != 0:
        pytest.skip("Kit ohne Git-Ablage - die versionierten Dateien sind "
                    "nicht bestimmbar")
    r = _pruefe(WURZEL, "pruefen", "--versioniert")
    assert r.returncode == 0, (
        f"Das Kit traegt Steuerzeichen in versionierten Dateien (BL-327):\n"
        f"{r.stdout}\n{r.stderr}")


# --- (5) Die schreibenden Rollen ---------------------------------------------

FALLE = "ECHTE-CLI-GESUCHT-BL327"

BEUTEBUCH = """# Beutebuch

## Funde

### HM-1 — Der Ton fehlt
- **Angreifer**: Harry
- **Schweregrad**: klein
- **Status**: an Frank übergeben
- **Reproschritte**: 1. `ton()` aufrufen
- **Erwartung**: 1
- **Realität**: 0
- **Betrifft**: `src/app.py`
- **Reproducer-Test**: `tests/test_hm1_ton.py`
"""

PLAN = """# Kaskade 1 — Ton
RALPH_CAP=1

## Stufe 1 — Ton pruefen
"""

# Die Attrappe der Agenten-CLI arbeitet wie die Rolle im Feld: Sie legt die
# Dateien ab, die der Fall vorbereitet hat, und committet sie. Die Bytes
# stehen in diesen Dateien, nicht im Skript - so tun beide Bahnen dasselbe.
FRANK_BASH = """#!/usr/bin/env bash
# Wie Frank im Feldfall aus Kit-BL-341: erst der Fix, dann der Docs-Commit.
set -e
a="$BL327_ARBEIT"
cp "$a/app.py" src/app.py
cp "$a/test_hm1_ton.py" tests/test_hm1_ton.py
git add src/app.py tests/test_hm1_ton.py >&2
git commit -q -m 'fix(uat): Ton repariert (HM-1)' >&2
cp "$a/CHANGELOG.md" CHANGELOG.md
"{python}" team/tools/beutebuch.py set HM-1 'erledigt (Frank-Fix, abc1234)' >&2
git add CHANGELOG.md plans/beutebuch.md >&2
git commit -q -m 'docs: CHANGELOG und Status (HM-1)' >&2
cat <<'TEAMJSON'
{antwort}
TEAMJSON
"""

FRANK_PWSH = """param()
# Wie Frank im Feldfall aus Kit-BL-341: erst der Fix, dann der Docs-Commit.
$a = $env:BL327_ARBEIT
Copy-Item -LiteralPath (Join-Path $a 'app.py') -Destination 'src/app.py' -Force
Copy-Item -LiteralPath (Join-Path $a 'test_hm1_ton.py') -Destination 'tests/test_hm1_ton.py' -Force
& git add src/app.py tests/test_hm1_ton.py 2>&1 | Out-Null
& git commit -q -m 'fix(uat): Ton repariert (HM-1)' 2>&1 | Out-Null
Copy-Item -LiteralPath (Join-Path $a 'CHANGELOG.md') -Destination 'CHANGELOG.md' -Force
& '{python}' team/tools/beutebuch.py set HM-1 'erledigt (Frank-Fix, abc1234)' 2>&1 | Out-Null
& git add CHANGELOG.md plans/beutebuch.md 2>&1 | Out-Null
& git commit -q -m 'docs: CHANGELOG und Status (HM-1)' 2>&1 | Out-Null
Write-Output @'
{antwort}
'@
exit 0
"""

RALPH_BASH = """#!/usr/bin/env bash
# Wie Ralph: Stufe 1 bauen, genau ein Commit.
set -e
cp "$BL327_ARBEIT/test_stufe1.py" tests/test_stufe1.py
git add tests/test_stufe1.py >&2
git commit -q -m 'feat(stufe1): Ton geprueft' >&2
cat <<'TEAMJSON'
{antwort}
TEAMJSON
"""

RALPH_PWSH = """param()
# Wie Ralph: Stufe 1 bauen, genau ein Commit.
Copy-Item -LiteralPath (Join-Path $env:BL327_ARBEIT 'test_stufe1.py') -Destination 'tests/test_stufe1.py' -Force
& git add tests/test_stufe1.py 2>&1 | Out-Null
& git commit -q -m 'feat(stufe1): Ton geprueft' 2>&1 | Out-Null
Write-Output @'
{antwort}
'@
exit 0
"""


def _antwort(promise):
    """Das Minimum, an dem `team_bewerte_ergebnis` einen Erfolg erkennt - mit
    dem Promise der Rolle im `result`."""
    return json.dumps({"subtype": "success", "is_error": False,
                       "stop_reason": "end_turn", "num_turns": 3,
                       "result": f"Fertig. <promise>{promise}</promise>",
                       "total_cost_usd": 0.0}, ensure_ascii=False)


def _falle(tmp_path):
    """Ein `claude` im Suchpfad, das laut scheitert statt zu arbeiten."""
    ordner = tmp_path / "falle"
    ordner.mkdir()
    sh = ordner / "claude"
    sh.write_text(f"#!/usr/bin/env bash\necho {FALLE} >&2\nexit 99\n",
                  encoding="utf-8", newline="\n")
    sh.chmod(0o755)
    (ordner / "claude.cmd").write_text(
        f"@echo off\r\necho {FALLE} 1>&2\r\nexit /b 99\r\n", encoding="utf-8")
    return ordner


def _stub(tmp_path, schale, bash_text, pwsh_text, promise):
    """Die Attrappe und der Wert, unter dem die Bahn sie findet."""
    werte = {"python": conftest.PYTHON_BEFEHL, "antwort": _antwort(promise)}
    if schale.name == "bash":
        stub = tmp_path / "claude-stub.sh"
        stub.write_text(bash_text.format(**werte), encoding="utf-8",
                        newline="\n")
        stub.chmod(0o755)
        return stub.as_posix()
    stub = tmp_path / "claude-stub.ps1"
    stub.write_text(pwsh_text.format(**werte), encoding="utf-8-sig",
                    newline="\n")
    return str(stub)


def _projekt(tmp_path, schale, rolle, stub_wert):
    repo = tmp_path / "repo"
    for ordner in ("src", "tests", "plans"):
        (repo / ordner).mkdir(parents=True, exist_ok=True)
    wrapper = entrypoint_pfad(f"{rolle}{schale.endung}")
    if not wrapper.is_file():
        pytest.skip(f"{wrapper.name} liegt in dieser Ablage nicht")
    shutil.copy(wrapper, repo / wrapper.name)
    kopiere_team_namensraum(repo / "team")
    schale.config_schreiben(repo, {
        "TEAM_DOMAENEN": "produkt", "TEAM_PRODUKTIVCODE": "src/",
        "TEAM_TEST_ORDNER": "tests/", "TEAM_PLAN_ORDNER": "plans/",
        "TEAM_BEUTEBUCH": "plans/beutebuch.md",
        "TEAM_BEUTEBUCH_TOOL": werkzeug_wert("team/tools/beutebuch.py"),
        "TEAM_KOSTEN_TOOL": werkzeug_wert("team/tools/kosten.py"),
        "TEAM_CLAUDE_BIN": stub_wert,
        # Was die installierte Konfiguration sonst mitbringt und die Prompts
        # auf der bash-Bahn unter `set -u` verlangen.
        "TEAM_CHANGELOG": "CHANGELOG.md", "TEAM_BACKLOG": "plans/backlog.md",
        "TEAM_ROADMAP": "plans/roadmap.md",
        "TEAM_ERMITTLUNGSAKTEN": "plans/ermittlungsakten",
        "TEAM_FEAT_PRAEFIX": "feat", "TEAM_FIX_PRAEFIX": "fix(uat)",
    })
    (repo / "src" / "app.py").write_bytes(b"def ton():" + LF + b"    return 0" + LF)
    (repo / "CHANGELOG.md").write_bytes(
        b"# Changelog" + LF + LF + b"## [Unreleased]" + LF + LF + b"### Fixes" + LF)
    (repo / "plans" / "beutebuch.md").write_bytes(BEUTEBUCH.encode("utf-8"))
    (repo / "plans" / "ralph-kaskade-1-ton.md").write_bytes(PLAN.encode("utf-8"))
    (repo / ".ralph-plan").write_bytes(b"plans/ralph-kaskade-1-ton.md" + LF)
    (repo / ".ralph-state").write_bytes(b"1" + LF)
    (repo / ".gitignore").write_bytes(
        b".team-logs/" + LF + b".ralph-logs/" + LF + b".frank-attempts" + LF
        + b".ralph-state" + LF + b".team-loop.lock" + LF)
    for befehl in (["init", "-q"], ["config", "user.email", "t@l"],
                   ["config", "user.name", "T"],
                   ["config", "core.autocrlf", "false"], ["add", "-A"],
                   ["commit", "-qm", "fixture"]):
        subprocess.run(["git", *befehl], cwd=repo, check=True,
                       capture_output=True)
    return repo


def _arbeit(tmp_path, mit_steuerzeichen):
    """Was die Rolle schreibt. Das Steuerzeichen ist das BEL aus dem Feldfall
    - `.\\abnahme.cmd` ueber einen Python-String - und entsteht hier aus
    seiner Zahl."""
    arbeit = tmp_path / "arbeit"
    arbeit.mkdir()
    pfad = (b"`." + BEL + b"bnahme.cmd`") if mit_steuerzeichen \
        else rb"`.\abnahme.cmd`"
    (arbeit / "app.py").write_bytes(b"def ton():" + LF + b"    return 1" + LF)
    (arbeit / "test_hm1_ton.py").write_bytes(
        b"from src.app import ton" + LF + LF + LF + b"def test_ton():" + LF
        + b"    assert ton() == 1" + LF)
    (arbeit / "CHANGELOG.md").write_bytes(
        b"# Changelog" + LF + LF + b"## [Unreleased]" + LF + LF + b"### Fixes" + LF
        + LF + b"- **Ton repariert** (HM-1). Abnahme ueber " + pfad + b"." + LF)
    stufe = (b"Ton" + BEL) if mit_steuerzeichen else rb"Ton\b"
    (arbeit / "test_stufe1.py").write_bytes(
        b"import re" + LF + LF + LF + b"def test_ton():" + LF
        + b'    text = "Tonleiter"' + LF
        + b'    assert re.search(r"' + stufe + b'", text) is None' + LF)
    return arbeit


def _fahre(repo, schale, rolle, tmp_path, stub_wert, arbeit):
    if schale.name == "bash":
        befehl = [conftest.BASH or "bash", str(repo / f"{rolle}.sh")]
    else:
        befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                  str(repo / f"{rolle}.ps1")]
    umgebung = dict(os.environ)
    umgebung["PATH"] = pfad_voran(_falle(tmp_path), umgebung)
    for weg in ("ANTHROPIC_API_KEY", "TEAM_REDTEAM_FOCUS", "TEAM_SMOKE_TEST",
                "TEAM_SMOKE_TEST_SCHNELL", "TEAM_WEITERER_CODE"):
        umgebung.pop(weg, None)
    umgebung.update(AUTH_MODE="abo", TEAM_LOCK_HELD="1",
                    TEAM_CLAUDE_BIN=stub_wert, BL327_ARBEIT=str(arbeit))
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    assert FALLE not in r.stdout + r.stderr, (
        f"Die {schale.name}-Bahn hat die ECHTE CLI gesucht statt der "
        f"Attrappe.\n{r.stdout}\n{r.stderr}")
    return r


def _frank(tmp_path, schale, mit_steuerzeichen):
    stub = _stub(tmp_path, schale, FRANK_BASH, FRANK_PWSH, "FRANK_FIX_COMPLETE")
    repo = _projekt(tmp_path, schale, "frank", stub)
    start = _git(repo, "rev-parse", "HEAD")
    r = _fahre(repo, schale, "frank", tmp_path, stub,
               _arbeit(tmp_path, mit_steuerzeichen))
    return repo, start, r


def _ralph(tmp_path, schale, mit_steuerzeichen):
    stub = _stub(tmp_path, schale, RALPH_BASH, RALPH_PWSH, "STUFE_1_COMPLETE")
    repo = _projekt(tmp_path, schale, "ralph", stub)
    start = _git(repo, "rev-parse", "HEAD")
    r = _fahre(repo, schale, "ralph", tmp_path, stub,
               _arbeit(tmp_path, mit_steuerzeichen))
    return repo, start, r


def test_frank_wird_rot_wenn_sein_ergebnis_ein_steuerzeichen_traegt(tmp_path,
                                                                   schale):
    """Der Feldfall aus `BL-341`: Der Fix ist richtig, der Dreisatz komplett,
    und der Docs-Commit danach traegt ein BEL. `frank.*` meldete "Dreisatz
    verifiziert" - jetzt ist der Schritt rot und nennt Datei und Zeile.
    Kein Rollback, kein Fehlversuch: Die Arbeit ist reparierbar."""
    repo, start, r = _frank(tmp_path, schale, mit_steuerzeichen=True)
    ausgabe = r.stdout + r.stderr
    assert r.returncode == 45, (
        f"{schale.name}: Frank meldet einen Fix mit Steuerzeichen nicht als "
        f"eigenen Ausgang (Exit {r.returncode}, erwartet 45, BL-327).\n{ausgabe}")
    assert "CHANGELOG.md:7:" in ausgabe and "0x07" in ausgabe, (
        f"Die Meldung nennt Datei und Zeile nicht.\n{ausgabe}")
    neu = _git(repo, "log", "--format=%s", f"{start}..HEAD").splitlines()
    assert len(neu) == 2, (
        f"Die Arbeit wurde zurueckgerollt - sie ist reparierbar, ein Rollback "
        f"wirft einen bezahlten Fix weg (BL-214).\n{neu}\n{ausgabe}")
    assert "erledigt" in (repo / "plans" / "beutebuch.md").read_text(
        encoding="utf-8"), "Der Fund steht nicht mehr auf erledigt."
    assert not (repo / ".frank-attempts").exists(), (
        "Ein Steuerzeichen zaehlt als Fehlversuch - der Fix ist aber gelandet.")


def test_frank_ohne_steuerzeichen_bleibt_gruen(tmp_path, schale):
    """Die Gegenrichtung: Eine Pruefung, die immer anschlaegt, ist keine."""
    repo, start, r = _frank(tmp_path, schale, mit_steuerzeichen=False)
    assert r.returncode == 0, (
        f"{schale.name}: Ein sauberer Fix ist nicht mehr gruen.\n"
        f"{r.stdout}\n{r.stderr}")
    assert "Dreisatz verifiziert" in r.stdout, r.stdout


def test_ralph_wird_rot_wenn_seine_stufe_ein_steuerzeichen_traegt(tmp_path,
                                                                schale):
    """Die Stufe ist gebaut und committet; der Commit traegt ein Steuerzeichen
    in einer Testdatei. Ralph schaltet weiter - die Arbeit zaehlt, ein Neubau
    waere bezahlte Arbeit zum zweiten Mal - und haelt mit 45 an."""
    repo, start, r = _ralph(tmp_path, schale, mit_steuerzeichen=True)
    ausgabe = r.stdout + r.stderr
    assert r.returncode == 45, (
        f"{schale.name}: Ralph meldet eine Stufe mit Steuerzeichen nicht als "
        f"eigenen Ausgang (Exit {r.returncode}, erwartet 45, BL-327).\n{ausgabe}")
    assert "tests/test_stufe1.py:6:" in ausgabe and "0x07" in ausgabe, ausgabe
    assert (repo / ".ralph-state").read_text(encoding="utf-8").strip() == "2", (
        "Die Stufe ist gebaut und committet - der Zustand muss weiterstehen, "
        "sonst baut der Neustart sie ein zweites Mal.")
    assert _git(repo, "log", "--format=%s", f"{start}..HEAD") \
        == "feat(stufe1): Ton geprueft", "Der Commit der Stufe ist weg."


def test_ralph_ohne_steuerzeichen_bleibt_gruen(tmp_path, schale):
    repo, start, r = _ralph(tmp_path, schale, mit_steuerzeichen=False)
    assert r.returncode == 0, (
        f"{schale.name}: Eine saubere Stufe ist nicht mehr gruen.\n"
        f"{r.stdout}\n{r.stderr}")
    assert "Feierabend" in r.stdout, r.stdout


# --- (6) Die Orchestrierung liest den Ausgang --------------------------------

def _quelle(name):
    pfad = entrypoint_pfad(name)
    if not pfad.is_file():
        pytest.skip(f"{name} liegt in dieser Ablage nicht")
    return pfad.read_text(encoding="utf-8-sig")


@pytest.mark.parametrize("rolle", ["ralph", "frank"])
def test_die_vollautomatik_haelt_beim_ausgang_45_an(tmp_path, rolle):
    """Ohne diesen Fall waere 45 fuer Frank ein Fehlversuch (`*`), und die
    Fix-Phase liefe weiter bis "beendet" - genau der Ausgang aus `BL-341`."""
    verlange_bash()
    import test_bl217_phasen_zeiger as phasen
    repo = phasen._projekt(tmp_path)
    stub = repo / f"{rolle}.sh"
    stub.write_text(f'#!/usr/bin/env bash\necho "STUB {rolle}"\nexit 45\n',
                    encoding="utf-8")
    stub.chmod(0o755)
    r = phasen._lauf(repo)
    assert r.returncode == 45, (
        f"Die Vollautomatik reicht den Ausgang 45 von {rolle} nicht durch "
        f"(Exit {r.returncode}).\n{r.stdout}\n{r.stderr}")
    assert "Kit-BL-327" in r.stdout, r.stdout
    assert "Vollautomatik beendet" not in r.stdout, r.stdout
    if rolle == "ralph":
        assert "PHASE Red Team" not in r.stdout, r.stdout
    else:
        assert "Frank-Fehlversuch" not in r.stdout, r.stdout


@pytest.mark.parametrize("datei", ["vollautomatik.sh", "vollautomatik.ps1"])
def test_beide_orchestratoren_kennen_den_ausgang(datei):
    """Ein eigener Exit-Code nuetzt nichts, wenn ihn niemand liest (BL-143).
    Die pwsh-Fassung ist hier nur am Quelltext pruefbar."""
    code = conftest.nur_code(_quelle(datei))
    if datei.endswith(".sh"):
        assert re.search(r"-eq 45\b", code) and re.search(r"^\s*45\)", code, re.M), (
            f"{datei} behandelt den Ausgang 45 nicht fuer Ralph und Frank.")
    else:
        assert re.search(r"-eq 45\b", code) and re.search(r"^\s*45 \{", code, re.M), (
            f"{datei} behandelt den Ausgang 45 nicht fuer Ralph und Frank.")
    assert "exit 45" in code, f"{datei} reicht den Ausgang 45 nicht durch."


@pytest.mark.parametrize("datei", ["halbautomatik.sh", "halbautomatik.ps1"])
def test_die_halbautomatik_deutet_den_ausgang(datei):
    code = conftest.nur_code(_quelle(datei))
    assert re.search(r"^\s*45[) ]", code, re.M) and "Kit-BL-327" in code, (
        f"{datei} deutet den Ausgang 45 als 'Fehler' - der Mensch baut neu "
        f"statt die Bytes zu reparieren.")


@pytest.mark.parametrize("datei", ["frank.sh", "frank.ps1", "ralph.sh",
                                   "ralph.ps1"])
def test_beide_bahnen_rufen_die_pruefung(datei):
    """Die pwsh-Haelfte ist auf dieser Maschine nicht gefahren - der Fall
    haelt wenigstens fest, dass sie gebaut ist."""
    code = conftest.nur_code(_quelle(datei))
    assert "team_steuerzeichen_pruefen" in code and "exit 45" in code, (
        f"{datei} ruft die Steuerzeichen-Pruefung nicht oder kennt den "
        f"Ausgang 45 nicht (BL-327).")


# --- (7) Der Satz im Briefing ------------------------------------------------

@pytest.mark.parametrize("rolle", ["ralph", "frank"])
def test_das_briefing_nennt_werkzeug_und_pruefung(rolle):
    """Der blinde Fleck der Regel (`\\t`, `\\n`) ist nur mit dem Satz zu
    schliessen: Text mit Backslashes geht ueber das Werkzeug zum Bearbeiten
    von Dateien in die Datei, und vor dem Commit laeuft die Pruefung."""
    text = kit_pfad("prompts", f"rolle-{rolle}.md").read_text(encoding="utf-8")
    flach = " ".join(text.split())
    assert "Werkzeug zum Bearbeiten von Dateien" in flach, (
        f"rolle-{rolle}.md nennt das Werkzeug zum Bearbeiten nicht (BL-327).")
    assert "Heredoc" in flach, f"rolle-{rolle}.md nennt den Weg nicht, der es kaputt macht."
    assert "team/tools/steuerzeichen.py pruefen" in flach and "Kit-BL-327" in flach, (
        f"rolle-{rolle}.md nennt die Pruefung vor dem Commit nicht (BL-327).")
    assert len(text.splitlines()) <= 45, f"rolle-{rolle}.md reisst das Limit."


def test_das_regel_inventar_traegt_die_neue_regel():
    """Die Regel steht in zwei Briefings - und nur das Inventar haelt sie
    gegen die naechste Straffung fest (`BL-335`: so ging Franks Absatz aus
    `BL-167` zwanzig Minuten nach dem Einbau wieder verloren)."""
    pfad = WURZEL / "doku" / "regel-inventar.md"
    if not pfad.is_file():
        pytest.skip("doku/ liegt nur im Kit")
    normen = [z for z in pfad.read_text(encoding="utf-8").splitlines()
              if "| NORM |" in z]
    for traeger in ("rolle-ralph", "rolle-frank"):
        eigene = [z for z in normen if f"| {traeger} |" in z]
        assert any("Bearbeiten von Dateien" in z for z in eigene), (
            f"Das Regel-Inventar fuehrt die Schreibregel aus BL-327 nicht mit "
            f"Traeger {traeger}.")
        assert any("steuerzeichen.py pruefen" in z for z in eigene), (
            f"Das Regel-Inventar fuehrt die Pruefung vor dem Commit nicht mit "
            f"Traeger {traeger}.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

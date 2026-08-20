#!/usr/bin/env python3
"""Fixture-Test fuer das Beutebuch-Archiv (Kaskade 22/Stufe 91, Baustein C).

`team/tools/beutebuch.py archiviere [--dry-run]` verschiebt jeden `### HM-<Nr>`-
Block mit Status `erledigt`/`ueberholt` woertlich vom aktiven Buch ans Ende
des Archivs; `next-id` wird archiv-bewusst (Maximum ueber beide Dateien).
Netz-/CLI-frei gegen temporaere Fixture-Dateien -- niemals gegen das echte
plans/beutebuch.md/plans/beutebuch-archiv.md. Muster wie
tests/test_stufe54_rollen_abschluss.py (--pfad/--archiv-pfad statt
Modul-Konstanten).
"""
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
BEUTEBUCH_PY = kit_pfad("tools", "beutebuch.py")

# Beide Ablagen: im Kit liegen die Werkzeuge unter geteilt/tools, im
# installierten Projekt unter team/tools. Ohne diese Fallunterscheidung
# scheitert schon der IMPORT — und ein Sammelfehler sieht schlimmer aus
# als der Layout-Unterschied, der er ist.
for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import beutebuch  # noqa: E402

VORLAGE = """# Beutebuch — Fixture

## Vorlage

```markdown
### HM-<Nr> — <Kurztitel>
- **Angreifer**: Harry | Marv
- **Status**: offen
```

## Funde
"""

ARCHIV_KOPF = """# Beutebuch-Archiv — Fixture

## Funde
"""


def _block(nr, status, angreifer="Marv"):
    return (
        f"### HM-{nr} — Fund Nr. {nr}\n"
        f"- **Angreifer**: {angreifer}\n"
        f"- **Status**: {status}\n"
        f"- **Reproschritte**:\n"
        f"  1. Schritt eins fuer Fund {nr}.\n"
        f"- **Erwartung**: …\n"
        f"- **Realität**: …\n"
    )


def _aktiv(tmp_path, bloecke, name="aktiv.md"):
    pfad = tmp_path / name
    inhalt = VORLAGE + "\n" + "\n\n".join(bloecke) + "\n"
    pfad.write_text(inhalt, encoding="utf-8")
    return pfad


def _archiv(tmp_path, bloecke=(), name="archiv.md"):
    pfad = tmp_path / name
    if bloecke:
        inhalt = ARCHIV_KOPF + "\n" + "\n\n".join(bloecke) + "\n"
    else:
        inhalt = ARCHIV_KOPF
    pfad.write_text(inhalt, encoding="utf-8")
    return pfad


def _run(*args):
    result = subprocess.run(
        [sys.executable, str(BEUTEBUCH_PY), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.returncode, result.stdout, result.stderr


def test_next_id_ist_maximum_ueber_aktiv_und_archiv(tmp_path):
    aktiv = _aktiv(tmp_path, [_block(1, "offen"), _block(2, "erledigt (Frank-Fix, abc)")])
    archiv = _archiv(tmp_path, [_block(5, "erledigt (Frank-Fix, def)")])
    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "next-id")
    assert rc == 0, err
    assert out.strip() == "HM-6"


def test_next_id_hoechste_nummer_nur_im_archiv(tmp_path):
    aktiv = _aktiv(tmp_path, [_block(1, "offen")])
    archiv = _archiv(tmp_path, [_block(9, "erledigt")])
    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "next-id")
    assert rc == 0, err
    assert out.strip() == "HM-10"


def test_archiviere_verschiebt_nur_erledigt_und_ueberholt(tmp_path):
    aktiv = _aktiv(tmp_path, [
        _block(1, "offen"),
        _block(2, "erledigt (Frank-Fix, abc)"),
        _block(3, "an Frank übergeben"),
        _block(4, "überholt (Strippenzieher-Entscheid)"),
        _block(5, "an Axel übergeben"),
        _block(6, "Fix-Plan liegt vor"),
    ])
    archiv = _archiv(tmp_path)
    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "archiviere")
    assert rc == 0, err
    verschoben = out.split()
    assert sorted(verschoben) == ["HM-2", "HM-4"]

    aktiv_ids = [hm for hm, _, _ in beutebuch.parse(aktiv)]
    archiv_ids = [hm for hm, _, _ in beutebuch.parse(archiv)]
    assert sorted(aktiv_ids) == ["HM-1", "HM-3", "HM-5", "HM-6"]
    assert sorted(archiv_ids) == ["HM-2", "HM-4"]


def test_zweiter_aufruf_ist_no_op(tmp_path):
    aktiv = _aktiv(tmp_path, [_block(1, "offen"), _block(2, "erledigt")])
    archiv = _archiv(tmp_path)
    _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "archiviere")
    nach_erstem_lauf_aktiv = aktiv.read_text(encoding="utf-8")
    nach_erstem_lauf_archiv = archiv.read_text(encoding="utf-8")

    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "archiviere")
    assert rc == 0, err
    assert out.strip() == ""
    assert aktiv.read_text(encoding="utf-8") == nach_erstem_lauf_aktiv
    assert archiv.read_text(encoding="utf-8") == nach_erstem_lauf_archiv


def test_vorlage_block_bleibt_im_aktiven_buch(tmp_path):
    aktiv = _aktiv(tmp_path, [_block(1, "erledigt")])
    archiv = _archiv(tmp_path)
    _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "archiviere")
    aktiv_text = aktiv.read_text(encoding="utf-8")
    assert "## Vorlage" in aktiv_text
    assert "### HM-<Nr> — <Kurztitel>" in aktiv_text


def test_dry_run_aendert_keine_datei(tmp_path):
    aktiv = _aktiv(tmp_path, [_block(1, "erledigt"), _block(2, "offen")])
    archiv = _archiv(tmp_path)
    vor_aktiv = aktiv.read_text(encoding="utf-8")
    vor_archiv = archiv.read_text(encoding="utf-8")

    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv),
                         "archiviere", "--dry-run")
    assert rc == 0, err
    assert out.strip() == "HM-1"
    assert aktiv.read_text(encoding="utf-8") == vor_aktiv
    assert archiv.read_text(encoding="utf-8") == vor_archiv


def test_verschobener_block_ist_byte_gleich_zum_original(tmp_path):
    text = _block(3, "erledigt (Frank-Fix, xyz789)")
    aktiv = _aktiv(tmp_path, [_block(1, "offen"), text, _block(2, "offen")])
    archiv = _archiv(tmp_path)
    _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "archiviere")

    original_core = "\n".join(text.splitlines())
    archiv_bloecke = beutebuch.bloecke(archiv)
    assert len(archiv_bloecke) == 1
    assert "\n".join(archiv_bloecke[0]["core"]) == original_core


def test_liste_mit_alle_bezieht_archiv_ein(tmp_path):
    aktiv = _aktiv(tmp_path, [_block(1, "offen")])
    archiv = _archiv(tmp_path, [_block(2, "erledigt")])

    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "list")
    assert rc == 0, err
    assert out.strip() == "HM-1\toffen"

    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "list", "--alle")
    assert rc == 0, err
    zeilen = out.strip().splitlines()
    assert zeilen == ["HM-1\toffen", "HM-2\terledigt"]


def test_first_count_set_bleiben_auf_aktivem_buch_beschraenkt(tmp_path):
    aktiv = _aktiv(tmp_path, [_block(1, "offen")])
    archiv = _archiv(tmp_path, [_block(2, "an Frank übergeben")])

    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv),
                         "first", "an Frank übergeben")
    assert rc == 1, out

    rc, out, err = _run("--pfad", str(aktiv), "--archiv-pfad", str(archiv), "set",
                         "HM-1", "erledigt (Frank-Fix, test123)")
    assert rc == 0, err
    assert "- **Status**: erledigt (Frank-Fix, test123)" in aktiv.read_text(encoding="utf-8")
    assert "an Frank übergeben" in archiv.read_text(encoding="utf-8")


def test_echtes_beutebuch_list_laeuft_fehlerfrei(tmp_path):
    """Regressionsbeleg: list parst das echte (Kaskade-22-archivierte) Buch
    fehlerfrei. Kein Inhalts-Snapshot -- Stufe 93 archiviert real alle bis
    dahin erledigten/ueberholten Funde, wodurch die Liste erwartbar leer
    wird; das ist der korrekte, gruene Zustand, keine Regression."""
    rc, out, err = _run("list")
    assert rc == 0, err

#!/usr/bin/env python3
"""BL-272 und BL-291: `sitzung-messen` erkennt einen Rollen-Lauf an seiner
HERKUNFT, nicht an der Zahl seiner Prompts — und waehlt mit `--projekt` die
juengste SITZUNG statt des juengsten Transkripts.

BL-272 (`Feld B`, 2026-09-17)
    Der Schutz aus BL-251 warnte bei genau einem echten Nutzer-Prompt: *„die
    Signatur eines headless gefahrenen ROLLEN-Laufs … NICHT buchen"*. Beim
    ersten Closeout nach dem Update traf das eine INTERAKTIVE Sitzung — ein
    umfangreicher Auftrag in einem Prompt, danach Stunden autonomer Arbeit,
    rund 8 USD. Der Schaden ist die Umkehrung des Ursprungsfunds: eine
    ausgelassene Buchung, und die faellt nirgends auf.

BL-291 (`Feld F`, 2026-09-29)
    Die Scharfschalt-Sequenz stellte den Kostenabschluss der Sitzung hinter
    den Start. Laeuft die Vollautomatik erst, schreibt jeder Rollen-Lauf sein
    Transkript in dieselbe Ablage, und `--projekt` nahm das zuletzt
    geaenderte — einen Rollen-Lauf. Die Planungskosten fielen weg.

DAS MERKMAL, an echten Ablagen gemessen
    Ein Rollen-Lauf beginnt mit dem Briefing des Kits (`# Briefing — Ralph
    (Bau-Loop)` usw.) und traegt `entrypoint: sdk-cli`; eine interaktive
    Sitzung beginnt mit einem Menschensatz und traegt z. B. `claude-vscode`.
    In `Feld F`: 185 Rollen-Laeufe, alle mit beidem. Der Briefing-Kopf zaehlt
    zuerst — ein Rollen-Lauf, der aus einer laufenden Sitzung heraus
    gestartet wird, erbt deren `entrypoint`.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

for _tools in (Path(__file__).resolve().parents[2] / "geteilt" / "tools",
               kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")


def _transkript(pfad, text, eingang=None, ein=1000, mtime=None):
    satz = {"type": "user", "message": {"role": "user", "content": [
        {"type": "text", "text": text}]}}
    if eingang:
        satz["entrypoint"] = eingang
    antwort = {"type": "assistant", "message": {
        "id": f"m-{pfad.stem}", "model": "claude-sonnet-5",
        "usage": {"input_tokens": ein, "output_tokens": 0,
                  "cache_read_input_tokens": 0,
                  "cache_creation": {"ephemeral_5m_input_tokens": 0,
                                     "ephemeral_1h_input_tokens": 0}}}}
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(satz) + "\n" + json.dumps(antwort) + "\n",
                    encoding="utf-8")
    if mtime is not None:
        os.utime(pfad, (mtime, mtime))
    return pfad


ROLLE = "# Briefing — Ralph (Bau-Loop)\n\n**Wer ich bin:** Ralph"
MENSCH = "Update verifizieren, danach die Kaskade abschliessen."


# --- Das Merkmal ----------------------------------------------------------

@pytest.mark.parametrize("text,eingang,erwartet", [
    (ROLLE, "sdk-cli", True),
    (ROLLE, "claude-vscode", True),     # geerbter entrypoint: Kopf gewinnt
    (MENSCH, "sdk-cli", True),
    (MENSCH, "claude-vscode", False),   # der BL-272-Feldfall
    (MENSCH, "cli", False),
    (MENSCH, None, None),               # verraet nichts: nicht raten
    ("# Briefing — Der Architekt (Planung, interaktiv)", "claude-vscode", False),
])
def test_die_herkunft(tmp_path, text, eingang, erwartet):
    t = _transkript(tmp_path / "t.jsonl", text, eingang)
    assert kosten.ist_rollenlauf(str(t)) is erwartet


# --- Die Bedienoberflaeche -------------------------------------------------

def _ablage(tmp_path):
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    heim = tmp_path / "heim"
    ordner = heim / ".claude" / "projects" / kosten.projekt_ordnername(
        str(projekt.resolve()))
    return projekt, heim, ordner


def _messen(projekt, heim, *zusatz):
    umgebung = dict(os.environ, HOME=str(heim), USERPROFILE=str(heim))
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "sitzung-messen",
                        "--projekt", ".", *zusatz], cwd=projekt,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=umgebung)
    return r.returncode, r.stdout, r.stderr


def test_eine_interaktive_ein_prompt_sitzung_wird_gebucht(tmp_path):
    """BL-272, der Feldfall: ein Auftrag, ein Prompt — und eine Sitzung."""
    projekt, heim, ordner = _ablage(tmp_path)
    _transkript(ordner / "sitzung.jsonl", MENSCH, "claude-vscode")
    rc, out, err = _messen(projekt, heim)
    assert "NICHT buchen" not in err, (
        f"Eine interaktive Sitzung mit EINEM Auftrag wird als Rollen-Lauf "
        f"abgewiesen — die Buchung faellt aus (BL-272).\n{err}")
    assert "team-status --akteur-abschluss" in out, out


def test_projekt_waehlt_die_sitzung_statt_der_juengeren_rollen_laeufe(tmp_path):
    """BL-291, der Feldfall: Die Planungssitzung ist aelter als die Rollen-
    Laeufe, die die Vollautomatik danach geschrieben hat."""
    projekt, heim, ordner = _ablage(tmp_path)
    import time
    jetzt = time.time()
    _transkript(ordner / "planung.jsonl", MENSCH, "claude-vscode", ein=7000,
                mtime=jetzt - 3600)
    _transkript(ordner / "ralph-1.jsonl", ROLLE, "sdk-cli", mtime=jetzt - 600)
    _transkript(ordner / "ralph-2.jsonl", ROLLE, "sdk-cli", mtime=jetzt - 60)
    rc, out, err = _messen(projekt, heim)
    assert "planung.jsonl" in out + err, (
        f"Gemessen wurde nicht die Planungssitzung (BL-291).\n{out}\n{err}")
    assert "2 juengere(r) Rollen-Lauf/Laeufe uebersprungen" in err, err
    assert "NICHT buchen" not in err


def test_alle_zaehlt_die_rollen_laeufe_nicht_doppelt(tmp_path):
    """Mit --alle lief die Summe sonst ueber Laeufe, die `--rollen-abschluss`
    schon gebucht hat."""
    projekt, heim, ordner = _ablage(tmp_path)
    _transkript(ordner / "planung.jsonl", MENSCH, "claude-vscode", ein=7000)
    _transkript(ordner / "ralph.jsonl", ROLLE, "sdk-cli", ein=999000)
    rc, out, err = _messen(projekt, heim, "--alle")
    assert "1 Rollen-Lauf/Laeufe der Ablage NICHT mitgezaehlt" in err, err
    assert "ralph.jsonl" not in out, out


def test_eine_unklare_herkunft_fragt_statt_zu_verbieten(tmp_path):
    """BL-272, Vorschlag 3: Wo das Transkript nichts verraet, wird gefragt,
    nicht verboten — die Buchungszeile bleibt stehen."""
    projekt, heim, ordner = _ablage(tmp_path)
    _transkript(ordner / "alt.jsonl", MENSCH, None)
    rc, out, err = _messen(projekt, heim)
    assert "BL-272" in err and "NICHT buchen" not in err, err
    assert "team-status --akteur-abschluss" in out, out


def test_ein_echter_rollen_lauf_ohne_sitzung_bleibt_ein_verbot(tmp_path):
    """Gegenrichtung: Liegt NUR ein Rollen-Lauf da, gilt das BL-251-Verbot
    unveraendert — die Buchungszeile eines fremden Laufs wird kopiert und
    ausgefuehrt."""
    projekt, heim, ordner = _ablage(tmp_path)
    _transkript(ordner / "ralph.jsonl", ROLLE, "sdk-cli")
    rc, out, err = _messen(projekt, heim)
    assert "NICHT buchen" in err, err
    assert "team-status --akteur-abschluss" not in out, out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

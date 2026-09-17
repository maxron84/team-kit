#!/usr/bin/env python3
"""BL-251/BL-252: Die zwei Wege, auf denen der Kostenabschluss einer Sitzung
falsch wird — einmal zu viel, einmal zu wenig.

BL-251 — ZU VIEL: `sitzung-messen --projekt .` trifft im Closeout mit hoher
Wahrscheinlichkeit einen bereits gebuchten ROLLEN-Lauf.
    `--projekt` waehlt das ZULETZT GEAENDERTE Transkript der Projektablage. In
    dieselbe Ablage schreibt aber JEDER headless gefahrene Rollen-Lauf sein
    Transkript, und die sind unmittelbar davor ueber `--rollen-abschluss`
    schon gebucht worden. Ausgezaehlt im Feld: 379 Transkripte, davon 324
    Rollen-Laeufe gegen 55 interaktive — 85 Prozent der Kandidaten sind die
    falschen, und zeitlich ist es schlimmer als der Schnitt, weil ein Closeout
    direkt auf einen Lauf folgt (im Fenster der letzten Kaskade 14 zu 2).

    AUFFALLEN KANN ES NIRGENDS: Es entstehen zwei fuer sich plausible Zeilen
    mit VERSCHIEDENER Rolle; der Kollisionsschutz von `--akteur-abschluss`
    schlaegt nur bei derselben Rolle plus Kaskade an, `--ledger-pruefen`
    schweigt mangels Rohlog, `--budget` zeigt eine plausible Summe.

    Die Unterscheidung ist maschinell trivial und an 379 Transkripten
    gemessen: Ein Rollen-Lauf hat genau EINEN echten Nutzer-Prompt, eine
    interaktive Sitzung mehrere. Der Abzug ist der ganze Trick — beim Zaehlen
    die `type: user`-Saetze ueberspringen, deren `content` ein `tool_result`
    traegt. Ohne ihn zaehlt dieselbe Messung 26 bis 194 statt 1 bis 7, und die
    Trennung verschwindet.

BL-252 — ZU WENIG: Eine gebuchte Sitzung, die weiterlaeuft, verliert ihren
Zuwachs lautlos.
    Der Kostenabschluss misst eine Sitzung an ihrem Transkript, und das kennt
    keinen Schnitt: Es waechst weiter, solange das Fenster offen ist. Vier
    gemessene Faelle: 76,3394 gegen 9,4989 gebucht (Differenz 66,84 — die
    komplette Aushaertung einer Kaskade), 39,4740 gegen 12,8224 (26,65),
    20,7386 gegen 17,4638 (3,27), dazu der Ursprungsfall aus `BL-165` mit
    43,90 ueber zwei Sitzungen.

    Die Regel im Architekten-Briefing (nach einem gebuchten Closeout eine NEUE
    Sitzung) ist richtig und reicht nicht: Sie hat im Feld an EINEM Tag zweimal
    nicht gegriffen, bei jemandem, der sie zitieren konnte. Ein Closeout hat
    einen Ausloeser, das Weiterarbeiten hat keinen — also bekommt es hier
    einen.

WAS DIESER TEST PRUEFT
    Beide Richtungen, am Verhalten, gegen gebaute Transkripte: Die Warnung
    erscheint im Fall, fuer den sie gebaut ist — UND sie erscheint nicht im
    Normalfall. Eine Meldung, die immer kommt, ist keine (BL-14).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if Path(_tools).is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")


def _antwort(mid, ein=0, aus=0, lesen=0, modell="claude-opus-5"):
    """Eine Assistenten-Zeile, wie die Agenten-CLI sie schreibt."""
    return json.dumps({"type": "assistant", "message": {
        "id": mid, "model": modell,
        "usage": {"input_tokens": ein, "output_tokens": aus,
                  "cache_read_input_tokens": lesen,
                  "cache_creation": {"ephemeral_5m_input_tokens": 0,
                                     "ephemeral_1h_input_tokens": 0}}}})


def _prompt(text="mach mal"):
    """Ein Satz, den ein Mensch getippt hat."""
    return json.dumps({"type": "user", "message": {
        "role": "user", "content": [{"type": "text", "text": text}]}})


def _werkzeug_antwort():
    """Ein `type: user`-Satz, den KEIN Mensch getippt hat — die Zeile, an der
    die Zaehlung ohne Abzug scheitert."""
    return json.dumps({"type": "user", "message": {
        "role": "user", "content": [{"type": "tool_result",
                                     "content": "ok", "tool_use_id": "t1"}]}})


def _transkript(pfad, prompts, antworten=1, lesen=0):
    zeilen = []
    for i in range(prompts):
        zeilen.append(_prompt(f"Auftrag {i}"))
        zeilen.append(_werkzeug_antwort())
        zeilen.append(_werkzeug_antwort())
    for i in range(antworten):
        zeilen.append(_antwort(f"m{i}", ein=1000, lesen=lesen))
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    return pfad


# --- Die Messung selbst -------------------------------------------------------

def test_rollenlauf_hat_genau_einen_echten_prompt(tmp_path):
    """Die Signatur, auf der alles steht."""
    t = _transkript(tmp_path / "rolle.jsonl", prompts=1)
    assert kosten.echte_nutzer_prompts([t]) == 1


def test_interaktive_sitzung_hat_mehrere(tmp_path):
    t = _transkript(tmp_path / "sitzung.jsonl", prompts=5)
    assert kosten.echte_nutzer_prompts([t]) == 5


def test_werkzeug_antworten_zaehlen_nicht_mit(tmp_path):
    """Der Abzug IST die Trennung. Ohne ihn zaehlte dieselbe Datei 3 statt 1 —
    im Feld 26 bis 194 statt 1 bis 7, und die Trennung verschwand ganz."""
    t = _transkript(tmp_path / "rolle.jsonl", prompts=1)
    roh = sum(1 for z in t.read_text(encoding="utf-8").splitlines()
              if json.loads(z).get("type") == "user")
    assert roh == 3, "der Aufbau des Falles stimmt nicht mehr"
    assert kosten.echte_nutzer_prompts([t]) == 1


def test_eine_halbe_zeile_am_dateiende_kippt_die_zaehlung_nicht(tmp_path):
    """Ein Transkript einer LAUFENDEN Sitzung endet regelmaessig mitten in der
    Zeile — genau dann wird gemessen."""
    t = _transkript(tmp_path / "offen.jsonl", prompts=2)
    with open(t, "a", encoding="utf-8") as f:
        f.write('{"type": "user", "mess')
    assert kosten.echte_nutzer_prompts([t]) == 2


# --- Die Bedienoberflaeche ----------------------------------------------------

def _cli(cwd, *args, heim=None):
    umgebung = dict(os.environ)
    if heim:
        umgebung["HOME"] = str(heim)
        umgebung["USERPROFILE"] = str(heim)
    r = subprocess.run([sys.executable, str(KOSTEN_PY), *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=umgebung)
    return r.returncode, r.stdout, r.stderr


def _ablage(tmp_path, projekt, prompts):
    """Eine Transkript-Ablage, wie die Agenten-CLI sie anlegt."""
    heim = tmp_path / "heim"
    ordner = heim / ".claude" / "projects" / kosten.projekt_ordnername(
        str(projekt.resolve()))
    _transkript(ordner / "abc.jsonl", prompts=prompts)
    return heim


def test_warnt_wenn_projekt_einen_rollenlauf_trifft(tmp_path):
    """Der Fund selbst."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    heim = _ablage(tmp_path, projekt, prompts=1)
    rc, out, err = _cli(projekt, "sitzung-messen", "--projekt", ".", heim=heim)
    assert "ROLLEN-Laufs" in err, f"keine Warnung:\n{err}"
    assert "BL-251" in err
    assert "NICHT buchen" in err, (
        "Die Buchungszeile eines fremden Laufs ist der teuerste Satz, den "
        "dieses Werkzeug drucken kann — sie wird kopiert und ausgefuehrt.")
    assert "team-status --akteur-abschluss" not in out, (
        "der fertige Buchungsbefehl darf hier NICHT dastehen")
    assert rc == 0, err


def test_schweigt_bei_einer_interaktiven_sitzung(tmp_path):
    """Gegenrichtung: Eine Meldung, die immer kommt, ist keine (BL-14)."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    heim = _ablage(tmp_path, projekt, prompts=4)
    rc, out, err = _cli(projekt, "sitzung-messen", "--projekt", ".", heim=heim)
    assert "ROLLEN-Laufs" not in err, f"Fehlalarm:\n{err}"
    assert "team-status --akteur-abschluss" in out, (
        "die Buchungszeile fehlt — das ist der Zweck des Befehls")


def test_nennt_die_zahl_der_kandidaten(tmp_path):
    """Richtung (3) der Meldung: sagen, worunter gewaehlt wurde. Bei genau
    einem Kandidaten stand bis hierher gar nichts da."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    heim = _ablage(tmp_path, projekt, prompts=4)
    _, _, err = _cli(projekt, "sitzung-messen", "--projekt", ".", heim=heim)
    assert "gewaehlt: 1 von 1" in err, err


def test_ein_benanntes_transkript_wird_nicht_bevormundet(tmp_path):
    """Wer das Transkript ausdruecklich nennt, hat die Wahl schon getroffen —
    die Warnung haengt an `--projekt`, nicht an der Zahl allein."""
    t = _transkript(tmp_path / "eins.jsonl", prompts=1)
    _, out, err = _cli(tmp_path, "sitzung-messen", str(t))
    assert "ROLLEN-Laufs" not in err, err
    assert "team-status --akteur-abschluss" in out


# --- BL-252 -------------------------------------------------------------------

def test_lange_sitzung_wird_benannt(tmp_path):
    """Die teuersten Zeilen des Projekts waren die Sitzungen, die nach ihrer
    Buchung weiterliefen. Beide Zahlen liegen ohnehin vor."""
    t = _transkript(tmp_path / "lang.jsonl", prompts=3,
                    antworten=kosten.LANGE_SITZUNG_ANTWORTEN + 1)
    _, _, err = _cli(tmp_path, "sitzung-messen", str(t))
    assert "Lange Sitzung" in err, err
    assert "BL-252" in err


def test_kurze_sitzung_bleibt_unbehelligt(tmp_path):
    t = _transkript(tmp_path / "kurz.jsonl", prompts=3, antworten=5)
    _, _, err = _cli(tmp_path, "sitzung-messen", str(t))
    assert "Lange Sitzung" not in err, f"Fehlalarm:\n{err}"


def test_die_messung_sagt_selbst_dass_die_naechste_kaskade_eine_neue_braucht(tmp_path):
    t = _transkript(tmp_path / "s.jsonl", prompts=3, antworten=5)
    _, out, _ = _cli(tmp_path, "sitzung-messen", str(t))
    assert "NEUE Sitzung" in out, out


def test_die_buchung_sagt_es_auch(tmp_path):
    """Die Buchung ist der EINZIGE Zeitpunkt, an dem sicher jemand hinsieht.
    Die Regel stand bis hierher nur im Briefing — und hat im Feld an einem Tag
    zweimal nicht gegriffen."""
    ledger = tmp_path / ".budget-ledger"
    rc, out, err = _cli(tmp_path, "architekt-abschluss", "--usd", "12.3456",
                        "--domaene", "produkt", "--kaskade", "7",
                        "--pfad", str(ledger))
    assert rc == 0, err
    assert "NEUE Sitzung" in out, out
    assert "BL-252" in out


def test_eine_rollenbuchung_bekommt_den_satz_nicht(tmp_path):
    """Gegenrichtung: Der Satz gilt der gemessenen Architekten-Sitzung. An
    einer Rollenzeile waere er falsch — die Rolle hat kein Fenster."""
    ledger = tmp_path / ".budget-ledger"
    rc, out, err = _cli(tmp_path, "akteur-abschluss", "--rolle", "frank",
                        "--usd", "1.0", "--domaene", "produkt", "--auth", "abo",
                        "--kaskade", "7", "--pfad", str(ledger))
    assert rc == 0, err
    assert "NEUE Sitzung" not in out, out

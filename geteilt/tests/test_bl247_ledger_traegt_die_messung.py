#!/usr/bin/env python3
"""BL-247, BL-252, BL-298, BL-279, BL-193 (Weg 2), BL-305: Das Ledger traegt
die MESSUNG hinter einem Betrag, nicht nur den Betrag — und damit findet ein
Werkzeug, was bis hierher nur ein Mensch fand, der die Transkript-Ablage von
Hand gegen das Ledger hielt.

BL-247 (`Feld B`, 2026-09-16)
    Gemessen werden Token je Modell und Sorte, gebucht wurde EINE Zahl:
    Dollar. Stand ein Preis falsch (BL-166), war jede vorher gebuchte Zeile
    dauerhaft falsch und nicht nachrechenbar. Jetzt traegt eine gemessene
    Buchung ein achtes Feld mit den Token; die Dollarspalte bleibt, was sie
    war, und eine Zeile ohne das Feld ist erkennbar dollargeboren.

BL-252 (`Feld B`) / BL-298 (`Feld E`)
    Eine gebuchte Sitzung, die weiterlief, verlor ihren Zuwachs lautlos (vier
    gemessene Faelle, bis 66,84 USD) — und die Rueckrechnung "Rohwert minus
    bereits gebucht" ergab im Feld -27,07 USD, weil die Zeile zwei
    Transkripte trug. Jetzt steht je Buchung eine Quelle mit Kennung und
    Fensterende in der Zeile, und `sitzung-messen` misst den Zuwachs selbst.

BL-279 (`Feld B`) / BL-193 Weg 2 (`Feld E`)
    273,83 USD Architektenkosten fehlten in einem Closeout, eine
    Aushaertungssitzung war strukturell nicht buchbar — und kein Werkzeug
    zeigte es. `sitzungen-pruefen` haelt jede Sitzung der Ablage gegen das
    Ledger; `--von/--bis` zerlegen ein Transkript.

BL-305 (Kit-Repo, 2026-10-03)
    Die Agenten-CLI schreibt den Verbrauch eines Subagenten in ein eigenes
    Transkript neben dem der Sitzung; keine Messung hat es je gelesen.
"""
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
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
T0 = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
MIO = 1_000_000      # Input-Token; bei claude-opus-5 genau 5 USD


@pytest.fixture(autouse=True)
def _saubere_umgebung(monkeypatch, tmp_path):
    for name in ("TEAM_PREISE", "TEAM_DOMAENEN"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)


def _zeit(minuten):
    return kosten.zeitpunkt_text(T0 + timedelta(minutes=minuten))


def _antwort(mid, minuten, ein=MIO, modell="claude-opus-5"):
    return json.dumps({"type": "assistant", "timestamp": _zeit(minuten),
                       "message": {"id": mid, "model": modell, "usage": {
                           "input_tokens": ein, "output_tokens": 0,
                           "cache_read_input_tokens": 0,
                           "cache_creation": {"ephemeral_5m_input_tokens": 0,
                                              "ephemeral_1h_input_tokens": 0}}}})


def _prompt(text, minuten):
    return json.dumps({"type": "user", "timestamp": _zeit(minuten),
                       "entrypoint": "cli", "message": {
                           "role": "user",
                           "content": [{"type": "text", "text": text}]}})


def _alter(pfad, stunden):
    zeit = time.time() - stunden * 3600
    os.utime(pfad, (zeit, zeit))


def _sitzung(pfad, antworten, start=0, stunden=3):
    """Eine interaktive Sitzung: je Minute eine Antwort zu 5 USD."""
    zeilen = [_prompt(f"Auftrag {i}", start) for i in range(2)]
    zeilen += [_antwort(f"{pfad.stem}-m{i}", start + i) for i in range(antworten)]
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    _alter(pfad, stunden)
    return pfad


def _ablage(tmp_path):
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    heim = tmp_path / "heim"
    ordner = (heim / ".claude" / "projects"
              / kosten.projekt_ordnername(str(projekt.resolve())))
    ordner.mkdir(parents=True)
    return projekt, heim, ordner


def _cli(projekt, heim, *args):
    umgebung = dict(os.environ)
    umgebung["HOME"] = str(heim)
    umgebung["USERPROFILE"] = str(heim)
    r = subprocess.run([sys.executable, str(KOSTEN_PY), *args], cwd=projekt,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=umgebung)
    return r.returncode, r.stdout, r.stderr


def _buchen(projekt, heim, usd, *extra, kaskade="7"):
    return _cli(projekt, heim, "akteur-abschluss", "--rolle", "architekt",
                "--auth", "abo", "--usd", usd, "--domaene", "produkt",
                "--kaskade", kaskade, *extra)


def _zeilen(projekt):
    return list(kosten.ledger_zeilen(str(projekt / ".budget-ledger")))


def _buchungszeilen(out):
    return [z for z in out.splitlines() if "Buchen:" in z]


def _wert(zeile, schalter):
    return zeile.split(f"{schalter} ")[1].split()[0]


# --- BL-247: die Token stehen in der Zeile ---------------------------------------

def test_die_gedruckte_buchungszeile_legt_die_token_ab(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "aaaa1111-sitzung.jsonl", antworten=2)
    rc, out, err = _cli(projekt, heim, "sitzung-messen", "--projekt", ".")
    assert rc == 0, err
    zeile = _buchungszeilen(out)
    assert len(zeile) == 1, out
    assert "--transkript aaaa1111-sitzung" in zeile[0], zeile[0]
    betrag = zeile[0].split(" abo ")[1].split()[0]
    assert betrag == "10.0000"
    rc, out, err = _buchen(projekt, heim, betrag, "--transkript",
                           _wert(zeile[0], "--transkript"),
                           "--bis", _wert(zeile[0], "--bis"))
    assert rc == 0, err
    assert "Kit-BL-247" in out
    z = _zeilen(projekt)[0]
    assert z["usd"] == 10.0
    assert kosten.zeilen_basis(z["meta"]) == "token"
    quelle = z["meta"]["quellen"][0]
    assert quelle["transkript"] == "aaaa1111-sitzung"
    assert quelle["tokens"] == {"claude-opus-5": {"input": 2 * MIO}}
    assert quelle["preise"] == {"claude-opus-5": 5.0}
    assert "usd_gemessen" not in quelle, (
        "Betrag und Nachmessung decken sich — die Buchungszeile traegt das "
        "Fenster der Messung, die ihn gedruckt hat")
    assert kosten.ledger_summe(str(projekt / ".budget-ledger")) == 10.0


def test_ohne_messung_bleibt_die_sieben_feld_zeile(tmp_path):
    """Gegenrichtung: Eine Buchung von Hand traegt nichts, was die sieben
    Felder nicht tragen — sie bleibt die Zeile von gestern."""
    ledger = tmp_path / "ledger"
    kosten.akteur_abschluss(1.5, "produkt", "3", "architekt", "abo",
                            notiz="von Hand", pfad=str(ledger))
    roh = [z for z in ledger.read_text(encoding="utf-8").splitlines() if z]
    assert len(roh[0].split("|")) == 7, roh
    assert kosten.zeilen_basis(_zeilen_aus(ledger)[0]["meta"]) == "dollar"


def _zeilen_aus(ledger):
    return list(kosten.ledger_zeilen(str(ledger)))


def test_abweichender_betrag_wird_mit_der_messung_abgelegt(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "aaaa2222.jsonl", antworten=1)
    rc, out, err = _buchen(projekt, heim, "7.0000", "--transkript", "aaaa2222",
                           "--bis", _zeit(10))
    assert rc == 0, err
    assert "Im Fenster gemessen: 5.0000" in err, err
    assert _zeilen(projekt)[0]["meta"]["quellen"][0]["usd_gemessen"] == 5.0


# --- BL-252 / BL-298: der Zuwachs ------------------------------------------------

def test_messung_nach_der_buchung_nennt_nur_den_zuwachs(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    t = _sitzung(ordner / "bbbb2222.jsonl", antworten=2)
    rc, _, err = _buchen(projekt, heim, "10.0000", "--transkript", "bbbb2222",
                         "--bis", _zeit(5))
    assert rc == 0, err
    with open(t, "a", encoding="utf-8") as f:       # die Sitzung lief weiter
        f.write(_antwort("bbbb2222-spaet", 10) + "\n")

    rc, out, err = _cli(projekt, heim, "sitzung-messen", str(t))
    assert "GESAMT: 15.0000" in out, out + err
    assert "schon gebucht: 10.0000 USD" in out, out
    assert "ZUWACHS seither: 5.0000 USD" in out, out
    zeile = _buchungszeilen(out)
    assert len(zeile) == 1 and " abo 5.0000 " in zeile[0], (
        f"Die Buchungszeile muss den ZUWACHS tragen, nicht die Summe "
        f"(Kit-BL-298):\n{out}")
    assert _wert(zeile[0], "--von") == _zeit(5)

    rc, _, err = _buchen(projekt, heim, "5.0000", "--transkript", "bbbb2222",
                         "--von", _zeit(5), "--bis", _wert(zeile[0], "--bis"),
                         "--addieren")
    assert rc == 0, err
    z = _zeilen(projekt)[0]
    assert z["usd"] == 15.0
    assert [q["usd"] for q in z["meta"]["quellen"]] == [10.0, 5.0], (
        "Der Zuwachs JEDER Buchung gehoert lesbar in die Zeile (Kit-BL-298)")

    rc, out, _ = _cli(projekt, heim, "sitzung-messen", str(t))
    assert "Kein Zuwachs" in out and not _buchungszeilen(out), out


def test_ohne_buchung_kommt_kein_buchungsstand(tmp_path):
    """Gegenrichtung (BL-14): Eine ungebuchte Sitzung bekommt die normale
    Buchungszeile, ohne Rede von einem Bestand."""
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "bbbb3333.jsonl", antworten=1)
    rc, out, err = _cli(projekt, heim, "sitzung-messen", "--projekt", ".")
    assert rc == 0, err
    assert "schon gebucht" not in out and "ZUWACHS" not in out
    assert " abo 5.0000 " in _buchungszeilen(out)[0]


def test_addieren_auf_eine_altzeile_haelt_beide_anteile_lesbar(tmp_path):
    """Der Feldfall aus BL-298, nachgestellt: 34,7619 aus einem fruehen
    Transkript (Altzeile, ohne Beleg), 9,4753 aus dem zweiten."""
    ledger = tmp_path / "ledger"
    ledger.write_text("2026-08-25 | 5 | 34.7619 | abo | produkt | architekt | "
                      "Closeout K5\n", encoding="utf-8")
    kosten.akteur_abschluss(9.4753, "produkt", "5", "architekt", "abo",
                            pfad=str(ledger), bestand="addieren",
                            quelle={"transkript": "t2", "bis": _zeit(1)})
    z = _zeilen_aus(ledger)[0]
    assert round(z["usd"], 4) == 44.2372
    assert [(bool(q.get("ohne_beleg")), q["usd"])
            for q in z["meta"]["quellen"]] == [(True, 34.7619), (False, 9.4753)]
    gebucht = sum(q["usd"] for _, q in kosten.gebuchte_quellen(str(ledger), "t2"))
    assert gebucht == 9.4753, (
        "Der Subtrahend der Rueckrechnung ist, was aus DIESEM Transkript "
        "gebucht ist — nicht die ganze Zeile")


# --- BL-116 als Riegel ----------------------------------------------------------

def test_dasselbe_fenster_zweimal_bricht_ab(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "cccc3333.jsonl", antworten=2)
    rc, _, err = _buchen(projekt, heim, "10.0000", "--transkript", "cccc3333",
                         "--bis", _zeit(5))
    assert rc == 0, err
    vorher = (projekt / ".budget-ledger").read_text(encoding="utf-8")
    rc, _, err = _buchen(projekt, heim, "10.0000", "--transkript", "cccc3333",
                         "--bis", _zeit(5), kaskade="8")
    assert rc == 1 and "Kit-BL-116" in err, err
    assert (projekt / ".budget-ledger").read_text(encoding="utf-8") == vorher, (
        "Der Fall aus BL-116: zwei Closeouts, ein Transkript — dieselben "
        "Antworten stuenden zweimal im Ledger")


def test_eine_korrektur_derselben_zeile_ist_keine_doppelbuchung(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "cccc4444.jsonl", antworten=2)
    assert _buchen(projekt, heim, "9.0000", "--transkript", "cccc4444",
                   "--bis", _zeit(5))[0] == 0
    rc, _, err = _buchen(projekt, heim, "10.0000", "--transkript", "cccc4444",
                         "--bis", _zeit(5), "--ersetzen")
    assert rc == 0, err
    assert _zeilen(projekt)[0]["usd"] == 10.0


# --- BL-279: das Zeitfenster -------------------------------------------------------

def test_die_haelften_ergeben_das_ganze(tmp_path):
    t = tmp_path / "s.jsonl"
    zeilen = [_antwort(f"m{i}", i, ein=100_000 * (i + 1)) for i in range(6)]
    # Eine Antwort, deren Saetze ueber die Grenze reichen: Ihr erster Satz
    # liegt davor, ihr Duplikat danach. Sie gehoert in GENAU eine Haelfte.
    zeilen.insert(2, _antwort("grenze", 2, ein=777_000))
    zeilen.append(_antwort("grenze", 4, ein=777_000))
    t.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    mitte = T0 + timedelta(minutes=3)

    def usd(**fenster):
        return kosten.sitzung_kosten(
            kosten.sitzung_messen([str(t)], **fenster)[0])[0]

    vorne, hinten, ganz = usd(bis=mitte), usd(von=mitte), usd()
    assert vorne > 0 and hinten > 0
    assert abs(vorne + hinten - ganz) < 1e-9, (vorne, hinten, ganz)


def test_fenster_auf_der_kommandozeile(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    t = _sitzung(ordner / "dddd1111.jsonl", antworten=4)
    rc, out, err = _cli(projekt, heim, "sitzung-messen", str(t),
                        "--von", _zeit(1), "--bis", _zeit(3))
    assert rc == 0, err
    assert "Fenster:" in out and "GESAMT: 10.0000" in out, out


def test_zeitpunkt_ohne_zone_ist_ortszeit():
    ort = datetime(2026, 9, 20, 10, 0).astimezone()
    assert kosten.zeitpunkt_lesen("2026-09-20 10:00") == ort.astimezone(timezone.utc)
    assert kosten.zeitpunkt_lesen("2026-09-20T08:00:00.000Z") == T0
    with pytest.raises(ValueError):
        kosten.zeitpunkt_lesen("gestern")


# --- BL-279 / BL-193 Weg 2: der Lueckenfinder --------------------------------------

def _pruefen(projekt, heim):
    return _cli(projekt, heim, "sitzungen-pruefen", "--seit", "2026-01-01")


def test_lueckenfinder_meldet_genau_die_ungebuchte_aushaertung(tmp_path):
    """Die Gegenprobe aus BL-193: zwei Transkripte, das aeltere ist die
    Aushaertung und steht in keiner Zeile — genau dieses eine wird gemeldet."""
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "dddd4444-aushaertung.jsonl", antworten=2, stunden=5)
    _sitzung(ordner / "eeee5555-closeout.jsonl", antworten=1, start=600,
             stunden=2)
    assert _buchen(projekt, heim, "5.0000", "--transkript", "eeee5555-closeout",
                   "--bis", _zeit(700))[0] == 0
    rc, out, err = _pruefen(projekt, heim)
    assert rc == 3, out + err
    zeilen = {z.split()[5]: z for z in out.splitlines()
              if z.startswith("  20")}
    assert "NICHT gebucht" in zeilen["dddd4444"], out
    assert "NICHT" not in zeilen["eeee5555"] and "gebucht (" in zeilen["eeee5555"]
    assert "dddd4444-aushaertung.jsonl" in out.split("NICHT gebucht, zusammen")[1]

    # Gegenrichtung: Ist beides gebucht, schweigt er.
    assert _buchen(projekt, heim, "10.0000", "--transkript",
                   "dddd4444-aushaertung", "--bis", _zeit(100),
                   "--addieren")[0] == 0
    rc, out, err = _pruefen(projekt, heim)
    assert rc == 0, out + err
    assert "NICHT gebucht" not in out and "Keine Luecke" in out


def test_lueckenfinder_nennt_den_zuwachs(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    t = _sitzung(ordner / "ffff1111.jsonl", antworten=2)
    assert _buchen(projekt, heim, "10.0000", "--transkript", "ffff1111",
                   "--bis", _zeit(5))[0] == 0
    with open(t, "a", encoding="utf-8") as f:
        f.write(_antwort("ffff1111-spaet", 10) + "\n")
    _alter(t, 1)
    rc, out, err = _pruefen(projekt, heim)
    assert rc == 3, out + err
    assert "ZUWACHS" in out and "+5.0000 USD" in out, out


def test_rollenlaeufe_sind_keine_luecke(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    rolle = ordner / "ffff6666.jsonl"
    rolle.write_text(json.dumps({"type": "user", "entrypoint": "sdk-cli",
                                 "message": {"role": "user",
                                             "content": "Auftrag"}})
                     + "\n" + _antwort("r1", 0) + "\n", encoding="utf-8")
    _alter(rolle, 1)
    rc, out, err = _pruefen(projekt, heim)
    assert rc == 0, out + err
    assert "1 Rollen-Lauf" in out and "ffff6666" not in out


def test_ein_altes_ledger_ohne_kennung_ist_kein_dauerfehlalarm(tmp_path):
    """BL-14: Ein Bestandsledger traegt keine Kennungen. Eine Warnung ueber
    jede alte Sitzung bei jedem Aufruf waere die, die man abschaltet."""
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "gggg7777.jsonl", antworten=1)
    (projekt / ".budget-ledger").write_text(
        f"{date.today().isoformat()} | 6 | 12.0000 | abo | produkt | "
        f"architekt | Closeout K6\n", encoding="utf-8")
    rc, out, err = _pruefen(projekt, heim)
    assert rc == 0, out + err
    assert "ohne Zuordnung" in out and "NICHT gebucht" not in out


def test_die_laufende_sitzung_ist_keine_luecke(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    t = _sitzung(ordner / "hhhh9999.jsonl", antworten=1)
    os.utime(t, None)                  # eben noch geschrieben
    rc, out, err = _pruefen(projekt, heim)
    assert rc == 0, out + err
    assert "laeuft noch" in out


# --- BL-305: Subagenten ---------------------------------------------------------

def test_subagenten_zaehlen_mit(tmp_path):
    projekt, heim, ordner = _ablage(tmp_path)
    _sitzung(ordner / "iiii8888.jsonl", antworten=1)
    unter = ordner / "iiii8888" / "subagents" / "agent-x1.jsonl"
    unter.parent.mkdir(parents=True)
    unter.write_text(_antwort("sub-1", 1) + "\n", encoding="utf-8")
    rc, out, err = _cli(projekt, heim, "sitzung-messen", "--projekt", ".")
    assert rc == 0, err
    assert "GESAMT: 10.0000" in out, (
        f"Der Subagent fehlt in der Summe (Kit-BL-305):\n{out}")
    assert "agent-x1.jsonl" in out and "Subagent" in out


def test_ohne_subagenten_bleibt_die_messung_gleich(tmp_path):
    t = _sitzung(tmp_path / "jjjj.jsonl", antworten=1)
    assert kosten.sitzungs_dateien(str(t)) == [str(t)]


# --- Rollen- und Bauzeilen ---------------------------------------------------------

def test_rollen_abschluss_schreibt_die_token_der_logs(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "harry-1.json").write_text(json.dumps({
        "total_cost_usd": 1.25, "modelUsage": {"claude-sonnet-5": {
            "inputTokens": 1000, "outputTokens": 200,
            "cacheReadInputTokens": 5000, "cacheCreationInputTokens": 300}}}),
        encoding="utf-8")
    (logs / "marv-1.json").write_text(json.dumps({"total_cost_usd": 0.75}),
                                      encoding="utf-8")
    ledger = tmp_path / "ledger"
    r = subprocess.run([sys.executable, str(KOSTEN_PY), "rollen-abschluss",
                        "--kaskade", "vor-3", "--domaene", "produkt",
                        "--logs", str(logs), "--pfad", str(ledger)],
                       cwd=tmp_path, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr
    z = _zeilen_aus(ledger)[0]
    assert z["usd"] == 2.0
    quelle = z["meta"]["quellen"][0]
    assert quelle["tokens"] == {"claude-sonnet-5": {
        "input": 1000, "output": 200, "cache_read": 5000, "cache_write": 300}}
    assert quelle["logs"] == 2 and quelle["ohne_tokens"] == 1
    assert kosten.zeilen_basis(z["meta"]) == "gemischt"


# --- Die Kennung im Ledger ----------------------------------------------------------

def test_ein_pipe_in_der_notiz_ist_kein_meta_feld():
    felder = [f.strip() for f in
              "2026-09-20 | 7 | 1.0 | abo | produkt | architekt | a | b".split("|")]
    assert kosten._meta_lesen(felder) is None


def test_handkorrektur_der_dollarspalte_wird_genannt(tmp_path):
    ledger = tmp_path / "ledger"
    meta = json.dumps({"v": 2, "quellen": [{"usd": 10.0, "transkript": "x",
                                             "bis": _zeit(1)}]})
    zeile = "2026-09-20 | 7 | {usd} | abo | produkt | architekt | von Hand | {meta}\n"
    ledger.write_text(zeile.format(usd="12.0000", meta=meta), encoding="utf-8")
    pruefe = lambda: {b["code"] for b in kosten.ledger_pruefen(  # noqa: E731
        str(ledger), ralph_logs=str(tmp_path / "r"),
        team_logs=str(tmp_path / "t"), repo=str(tmp_path))}
    assert "quellen-weichen-ab" in pruefe()
    ledger.write_text(zeile.format(usd="10.0000", meta=meta), encoding="utf-8")
    assert "quellen-weichen-ab" not in pruefe()

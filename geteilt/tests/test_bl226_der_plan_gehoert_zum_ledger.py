#!/usr/bin/env python3
"""BL-226 — die Plan-Gegenprobe aus `BL-220` las den Plan des ARBEITS-
VERZEICHNISSES statt den des Projekts, dessen Ledger geschrieben wird.

DER FELDFALL, eingetreten beim ersten `--update` nach der Auslieferung:
In einem Projekt mit laufender Kaskade (`.ralph-plan` → Kaskade 13) fielen
**25 fremde Testfälle** aus sieben Dateien — `test_bl4`, `test_bl5`,
`test_bl19`, `test_stufe54`, `test_hm39`, `test_hm41`, `test_hm44`. Keiner
davon hat mit `BL-220` etwas zu tun: Sie buchen in ein **Wegwerf-Ledger unter
`/tmp`** und übergeben dabei die Kaskadennummer ihres Szenarios (1, 3, 16).
Gegengehalten wurde der Plan des Projekts, in dem pytest zufällig lief.

    Fehler: .ralph-plan sagt Kaskade 13, uebergeben wurde 16 -- nicht gebucht

Zwei Dinge, die nichts miteinander zu tun haben. **Der Plan gehört zu dem
Projekt, dessen Ledger geschrieben wird** — liegt das Ledger woanders, gibt es
keinen Sollwert und damit keine Gegenprobe. Im echten Closeout ändert das
nichts: Dort liegt `.budget-ledger` neben `.ralph-plan`, und die Zusicherung
aus `BL-220` gilt unverändert.

WARUM DER SELBSTTEST DAS NICHT SEHEN KONNTE — und was daran geändert wurde.
`kit-test.sh` installiert in ein **frisches** Wegwerf-Repo. Dort gibt es keine
`.ralph-plan`, keinen `.ralph-state`, kein gewachsenes Ledger. Ein Fix, der
Projektzustand liest, war damit strukturell ungeprüft: In der Installation
grün, im Feldprojekt rot. Seit `BL-226` fährt Schritt 4 die Suite ein zweites
Mal, mit gesetztem `.ralph-plan` und `.ralph-state` — die Gattung, nicht dieser
eine Fall.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import kit_pfad

KOSTEN_PY = kit_pfad("tools", "kosten.py")
LEDGER_KOPF = ("# Datum | Kaskade | USD | Auth | Domaene | Rolle | Notiz\n"
               "2026-08-01 | 1 | 1.0000 | abo | produkt | architekt | Start\n")


def _ledger(ordner):
    p = ordner / ".budget-ledger"
    p.write_text(LEDGER_KOPF, encoding="utf-8")
    return p


def _logs(ordner, usd=2.0):
    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / "harry-20260901-100000.json").write_text(
        json.dumps({"total_cost_usd": usd}), encoding="utf-8")
    return ordner


def _plan(ordner, nummer):
    """Ein Projekt mit laufender Kaskade: Zeiger plus Plandatei."""
    (ordner / "plans").mkdir(parents=True, exist_ok=True)
    datei = f"plans/ralph-kaskade-{nummer}-etwas.md"
    (ordner / datei).write_text("# Plan\n", encoding="utf-8")
    (ordner / ".ralph-plan").write_text(datei + "\n", encoding="utf-8")


def _run(cwd, *args):
    ergebnis = subprocess.run([sys.executable, str(KOSTEN_PY),
                               "rollen-abschluss", *args],
                              cwd=str(cwd), capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    return ergebnis.returncode, ergebnis.stdout, ergebnis.stderr


# --- (1) Der Feldfall ------------------------------------------------------


def test_fremdes_ledger_wird_nicht_gegen_den_eigenen_plan_gehalten(tmp_path):
    """Der Fund. Ein Prozess läuft in einem Projekt mit laufender Kaskade und
    bucht in ein Ledger **anderswo** — genau die Lage von 25 Testfällen."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    _plan(projekt, 13)
    fremd = tmp_path / "woanders"
    fremd.mkdir()
    ledger = _ledger(fremd)
    logs = _logs(fremd / "team-logs")

    rc, _out, err = _run(projekt, "--kaskade", "16", "--domaene", "produkt",
                         "--logs", str(logs), "--pfad", str(ledger))
    assert rc == 0, (
        "Der Plan des Arbeitsverzeichnisses wurde gegen ein fremdes Ledger "
        f"gehalten — der Feldfehler.\n{err}")
    assert "16" in ledger.read_text(encoding="utf-8")


def test_und_die_meldung_taucht_dabei_gar_nicht_erst_auf(tmp_path):
    """Nicht nur der Exit-Code: Eine Warnung, die hier erschiene, wäre
    ebenfalls falsch und würde zum Wegsehen erziehen (`BL-14`)."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    _plan(projekt, 13)
    fremd = tmp_path / "woanders"
    fremd.mkdir()
    rc, out, err = _run(projekt, "--kaskade", "16", "--domaene", "produkt",
                        "--logs", str(_logs(fremd / "team-logs")),
                        "--pfad", str(_ledger(fremd)))
    assert rc == 0
    assert "BL-220" not in err and "BL-220" not in out


# --- (2) Die Zusicherung aus BL-220 gilt unverändert weiter -----------------


def test_liegt_das_ledger_neben_dem_plan_greift_die_gegenprobe(tmp_path):
    """Die Gegenrichtung, und ohne sie wäre der Fix eine Abschaltung: Im
    echten Closeout liegt `.budget-ledger` neben `.ralph-plan`."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    _plan(projekt, 13)
    ledger = _ledger(projekt)
    logs = _logs(projekt / "team-logs")

    vorher = ledger.read_text(encoding="utf-8")
    rc, _out, err = _run(projekt, "--kaskade", "59", "--domaene", "produkt",
                         "--logs", str(logs), "--pfad", str(ledger))
    assert rc != 0, (
        "Die Stufennummer statt der Kaskadennummer wurde gebucht — die "
        "Zusicherung aus `BL-220` ist weg.")
    assert "BL-220" in err
    assert ledger.read_text(encoding="utf-8") == vorher, (
        "Trotz Abbruch wurde geschrieben.")


def test_dieselbe_lage_mit_relativem_pfad(tmp_path):
    """Der Normalfall aus `TEAM.md`: aufgerufen im Projekt, ohne `--pfad`
    irgendwohin. Der Wrapper übergibt einen relativen Pfad."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    _plan(projekt, 13)
    _ledger(projekt)
    logs = _logs(projekt / "team-logs")
    rc, _out, err = _run(projekt, "--kaskade", "59", "--domaene", "produkt",
                         "--logs", str(logs), "--pfad", ".budget-ledger")
    assert rc != 0 and "BL-220" in err, (
        f"Mit relativem --pfad greift die Gegenprobe nicht mehr.\n{err}")


def test_die_richtige_nummer_bucht_weiterhin(tmp_path):
    """Sonst prüfte der Fall darüber nur, dass irgendetwas rot ist."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    _plan(projekt, 13)
    ledger = _ledger(projekt)
    rc, _out, err = _run(projekt, "--kaskade", "13", "--domaene", "produkt",
                         "--logs", str(_logs(projekt / "team-logs")),
                         "--pfad", ".budget-ledger")
    assert rc == 0, err
    assert "| 13 |" in ledger.read_text(encoding="utf-8")


def test_trotzdem_uebersteuert_weiterhin(tmp_path):
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    _plan(projekt, 13)
    ledger = _ledger(projekt)
    rc, _out, err = _run(projekt, "--kaskade", "59", "--domaene", "produkt",
                         "--logs", str(_logs(projekt / "team-logs")),
                         "--pfad", ".budget-ledger", "--trotzdem")
    assert rc == 0, err


def test_eine_benannte_kaskade_wird_nie_gegen_den_plan_gehalten(tmp_path):
    """`vor-10` & Co. werden bewusst gesetzt — sie sind keine Verwechslung
    mit einer Stufennummer."""
    projekt = tmp_path / "projekt"
    projekt.mkdir()
    _plan(projekt, 13)
    ledger = _ledger(projekt)
    rc, _out, err = _run(projekt, "--kaskade", "vor-10", "--domaene", "produkt",
                         "--logs", str(_logs(projekt / "team-logs")),
                         "--pfad", ".budget-ledger")
    assert rc == 0, err


# --- (3) Die Gattung, nicht dieser eine Fall -------------------------------


def test_der_selbsttest_faehrt_die_suite_mit_laufender_kaskade():
    """Die eigentliche Lehre. Solange `kit-test.sh` die Suite nur in einer
    FRISCHEN Installation fährt, ist jeder Fix, der Projektzustand liest,
    strukturell ungeprüft — grün in der Wegwerf-Installation, rot im Feld."""
    pfad = Path(__file__).resolve().parents[2] / "bash" / "kit-test.sh"
    if not pfad.is_file():
        pytest.skip("der Selbsttest liegt nur im Kit, nicht in der Installation")
    text = pfad.read_text(encoding="utf-8")
    assert ".ralph-plan" in text and ".ralph-state" in text, (
        "`kit-test.sh` setzt keinen Kaskadenzustand mehr. Dann läuft die Suite "
        "wieder ausschliesslich gegen ein frisches Repo — die Lücke, durch die "
        "`BL-220` ins Feld gekommen ist.")
    assert "BL-226" in text, (
        "Der Grund für den zweiten Lauf steht nicht mehr daneben. Ein Schritt "
        "ohne Begründung wird beim nächsten Aufräumen gestrichen.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

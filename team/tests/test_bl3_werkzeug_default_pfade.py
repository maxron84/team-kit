"""BL-3 — die Default-Pfade der Werkzeuge muessen von Tests beruehrt werden.

`BL-1` rutschte durch 132 gruene Tests, weil saemtliche Werkzeug-Tests mit
--pfad auf Fixtures arbeiten. Der Default-Pfad — der einzige, den die
Rollen-Skripte je benutzen — war ungeprueft.

Das Audit des Closeouts (Kaskade 1) ergab: `kosten.py` hat NICHT denselben
Fehler, weil es seine Pfade gar nicht aus __file__ ableitet, sondern
arbeitsverzeichnis-relativ vorhaelt (".budget-ledger"). Das ist nur deshalb
korrekt, weil JEDER Entrypoint als zweite Zeile ins Skriptverzeichnis wechselt.
Diese Invariante war bisher nirgends festgehalten — faellt sie, meldet
`kosten.py` still 0.0000 USD statt zu scheitern, und die Budget-Durchsetzung
wird blind (dieselbe Klasse wie BL-55).

Die Tests pinnen daher beides: die Invariante und das stille Verhalten.
"""
import shutil
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent.parent
KOSTEN = WURZEL / "team" / "tools" / "kosten.py"

# datum | kaskade | usd | auth | domaene | rolle | notiz
LEDGER_ZEILE = "2026-01-01 | 1 | 2.5000 | abo | produkt | roles | Fixture\n"

# Die Entrypoints liegen im installierten Projekt in der Wurzel, im Kit-Repo
# unter entry/. redteam.sh ist kein Entrypoint des Menschen, wechselt aber
# ebenfalls und wird deshalb mitgeprueft.
ENTRYPOINTS = (
    "ralph", "frank", "axel", "harry", "marv",
    "vollautomatik", "halbautomatik", "team-status", "team-test",
)


def _finde(name):
    """Sucht einen Entrypoint in beiden Ablagen (Projektwurzel und Kit-entry/)."""
    for kandidat in (WURZEL / name, WURZEL / "entry" / name):
        if kandidat.is_file():
            return kandidat
    return None


def test_jeder_entrypoint_wechselt_ins_skriptverzeichnis(schale):
    """Die Invariante, auf der die relativen Default-Pfade von kosten.py ruhen.

    Ohne sie haengt jede Kostenzahl davon ab, aus welchem Verzeichnis der
    Mensch das Skript gestartet hat — und kosten.py meldet dann still 0.0000
    statt zu scheitern.

    Der Test laeuft auf BEIDEN Bahnen gegen dasselbe Versprechen, aber gegen
    zwei Schreibweisen: `cd "$(dirname "$0")"` bzw. `Set-Location $PSScriptRoot`.
    Die Zuordnung steht in der Schale (schale.wechsel_ins_skriptverzeichnis),
    nicht hier — sonst muesste jeder statische Test seine eigene
    Uebersetzungstabelle fuehren, und die erste, die jemand vergisst, ist eine
    stille Luecke im Windows-Zweig.
    """
    idiom = schale.wechsel_ins_skriptverzeichnis
    gefunden = 0
    for rumpf in ENTRYPOINTS:
        pfad = _finde(schale.entrypoint(rumpf))
        if pfad is None:
            continue
        gefunden += 1
        assert idiom in pfad.read_text(encoding="utf-8"), (
            f"{schale.entrypoint(rumpf)} wechselt nicht ins Skriptverzeichnis "
            f"({idiom!r} fehlt) — relative Werkzeug-Pfade werden damit vom "
            f"Aufrufort abhaengig"
        )
    assert gefunden >= len(ENTRYPOINTS) - 1, (
        f"nur {gefunden} Entrypoints ({schale.name}) gefunden — Ablage geaendert?"
    )


def test_kosten_liest_das_ledger_ohne_pfadangabe_aus_dem_arbeitsverzeichnis(tmp_path):
    """Der Default-Pfad ".budget-ledger" muss im Projektverzeichnis greifen."""
    projekt = tmp_path / "projekt"
    (projekt / "team" / "tools").mkdir(parents=True)
    shutil.copy(KOSTEN, projekt / "team" / "tools" / "kosten.py")
    (projekt / ".budget-ledger").write_text(LEDGER_ZEILE, encoding="utf-8")

    ergebnis = subprocess.run(
        [sys.executable, "team/tools/kosten.py", "ledger"],
        cwd=projekt, capture_output=True, text=True, check=True,
    )
    assert ergebnis.stdout.strip() == "2.5000"


def test_fehlendes_ledger_meldet_still_null(tmp_path):
    """Dokumentiert die scharfe Kante — bewusst kein Fehler, aber eine Falle.

    Ein fehlendes Ledger ist am Tag 1 legitim (der Installer legt es leer an),
    deshalb ist die stille Null richtig. Sie ist aber ununterscheidbar von
    "aus dem falschen Verzeichnis gestartet". Wer diese Erwartung aendert,
    soll hier stolpern und den Test bewusst mitziehen.
    """
    leeres = tmp_path / "ohne-ledger"
    leeres.mkdir()

    ergebnis = subprocess.run(
        [sys.executable, str(KOSTEN), "ledger"],
        cwd=leeres, capture_output=True, text=True, check=True,
    )
    assert ergebnis.stdout.strip() == "0.0000"
    assert ergebnis.returncode == 0

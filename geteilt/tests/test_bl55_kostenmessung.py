#!/usr/bin/env python3
"""Fixture-Tests für BL-55 — die zwei Kostenmess-Löcher aus dem Kaskade-22-Lauf.

Beide Funde stammen aus dem realen `vollautomatik.sh`-Lauf vom 2026-08-01, dessen
Abschlussbericht 6,1644 USD druckte, während tatsächlich 26,4183 USD ausgegeben
worden waren.

**Fund 1 — Durchsetzung A wird blind, sobald mitten im Lauf archiviert wird.**
`lauf_kosten()` zählte nur `.ralph-logs`/`.team-logs`. Die (bis dahin
vorgeschriebene) Kostenabschluss-Stufe *innerhalb* des Laufs schob die Rohlogs per
`team_logs_archivieren` nach `<dir>/archiv/` — womit 20,25 USD bereits
ausgegebenes Geld aus der Pro-Lauf-Durchsetzung verschwanden, und zwar genau vor
der offenen Fix-Phase (bis zu 12 Frank/Axel-Runden). Der Deckel war ab da
faktisch zurückgesetzt.

**Fund 2 — `TEAM_LAST_COST` sah nur den letzten Versuch.**
In Stufe 93 scheiterte der Abo-Aufruf nach 1,6806 USD; der API-Fallback kostete
0,3984. Gemeldet und gegen den 5-USD-Pro-Stufe-Cap geprüft wurden nur die 0,3984.
Ein Fehlversuch war damit gratis — und der Cap umgehbar: 4,9 USD Abo-Fehlversuch
plus 4,9 USD API meldeten 4,9 gegen einen 5-USD-Deckel.

Netz- und CLI-frei: getestet werden die Bash-Helfer über `subprocess`+`bash -c`
gegen temporäre Fixture-Verzeichnisse — nie gegen die echten Logs oder die echte
`.budget-ledger`.
"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

from conftest import BASH, basis_umgebung, entrypoint_pfad, kit_pfad, werkzeug_wert

REPO_ROOT = Path(__file__).resolve().parents[2]  # team/tests/ -> Repo-Wurzel
TEAM_LIB = kit_pfad("lib.sh")
VOLLAUTOMATIK = entrypoint_pfad("vollautomatik.sh")

# Die Regeldatei heisst in der INSTALLATION `CLAUDE.md`; im Kit liegt sie als
# `bootstrap/CLAUDE.md.vorlage` — dieselbe Datei, einen Installationsschritt
# frueher. Geprueft wird die Regel, nicht der Dateiname.
REGELDATEI = (REPO_ROOT / "CLAUDE.md" if (REPO_ROOT / "CLAUDE.md").is_file()
              else REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage")

# BL-133-Bauart: Der Harnisch sagt der Bibliothek, wie das Werkzeug auf DIESER
# Maschine und in DIESER Ablage heisst — im Feld tut das team.config.sh. Ohne
# das stirbt jede Funktion, die $TEAM_KOSTEN_TOOL anfasst, unter `set -u` an
# einer "unbound variable", sobald lib.sh ohne danebenliegende Konfiguration
# gesourct wird (also immer in der Kit-Ablage).
KOSTEN_WERT = werkzeug_wert(str(kit_pfad("tools", "kosten.py")
                                .relative_to(REPO_ROOT)).replace("\\", "/"))


def _bash(code):
    """Führt Bash-Code mit geladener team/lib.sh aus und liefert stdout (getrimmt)."""
    result = subprocess.run(
        [BASH, "-c", f'set -euo pipefail; source "{TEAM_LIB}"; {code}'],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        env=basis_umgebung(TEAM_KOSTEN_TOOL=KOSTEN_WERT),
    )
    assert result.returncode == 0, f"bash schlug fehl: {result.stderr}"
    return result.stdout.strip()


def _log(pfad, usd, alter_sekunden=0):
    """Schreibt ein Claude-Log-Fixture; alter_sekunden setzt die mtime zurück."""
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps({"total_cost_usd": usd, "is_error": False}))
    if alter_sekunden:
        vergangen = time.time() - alter_sekunden
        os.utime(pfad, (vergangen, vergangen))
    return pfad


# --- Fund 2: TEAM_LAST_COST zählt alle Versuche eines Aufrufs ------------------

def test_summe_cost_usd_addiert_alle_versuche(tmp_path):
    abo = _log(tmp_path / "stufe-93.json", 1.6806)
    fallback = _log(tmp_path / "stufe-93-api-fallback.json", 0.3984)

    summe = float(_bash(f'team_summe_cost_usd "{abo}" "{fallback}"'))

    assert abs(summe - 2.0790) < 1e-6, (
        f"Die Kosten eines Aufrufs sind Abo-Fehlversuch + API-Fallback = 2.0790, "
        f"nicht {summe}. Sonst ist ein teurer Fehlversuch gratis (BL-55)."
    )


def test_summe_cost_usd_toleriert_fehlende_und_kaputte_logs(tmp_path):
    gut = _log(tmp_path / "gut.json", 2.5)
    kaputt = tmp_path / "kaputt.json"
    kaputt.write_text("{kein json")
    fehlt = tmp_path / "gibtsnicht.json"

    summe = float(_bash(f'team_summe_cost_usd "{gut}" "{kaputt}" "{fehlt}"'))

    assert abs(summe - 2.5) < 1e-9, (
        "Ein unlesbares oder fehlendes Log darf die Summe nicht sprengen — der "
        "Budget-Check laeuft sonst in einen harten Fehler statt in eine Zahl."
    )


def test_team_claude_setzt_last_cost_aus_allen_versuchen():
    quelle = TEAM_LIB.read_text(encoding="utf-8")
    koerper = quelle[quelle.index("team_claude() {"):quelle.index("# team_promise_in")]

    assert "team_extract_cost_usd" not in koerper, (
        "team_claude darf TEAM_LAST_COST nicht mehr aus EINER Datei lesen — "
        "der gescheiterte Vorversuch faellt sonst wieder aus Meldung und "
        "Budget-Pruefung heraus (BL-55, Fund 2)."
    )
    assert koerper.count('versuch_logs+=("$out")') == 3, (
        "Jeder der drei claude-Aufrufe (Abo, API-Fallback, 429-Retry) muss sein "
        "Log in versuch_logs eintragen."
    )
    assert koerper.count('team_summe_cost_usd "${versuch_logs[@]}"') == 2, (
        "Beide TEAM_LAST_COST-Zuweisungen (Pausen-Pfad und Normalpfad) muessen "
        "ueber die Summe aller Versuche laufen."
    )
    assert 'TEAM_LAST_OUT="$out"' in koerper, (
        "TEAM_LAST_OUT muss das FINALE Log bleiben — die Promise-Pruefung haengt "
        "daran (HM-20)."
    )


# --- Fund 1: Durchsetzung A ueberlebt eine Archivierung mitten im Lauf --------

def test_kosten_seit_findet_die_im_lauf_archivierten_logs(tmp_path):
    """Wird mitten im Lauf archiviert, muss das Geld weiterhin gezaehlt werden —
    historische Archiv-Logs frueherer Kaskaden aber nicht."""
    logs = tmp_path / "ralph-logs"
    archiv = logs / "archiv"

    _log(logs / "stufe-94.json", 0.4)                       # noch aktiv
    _log(archiv / "stufe-87.json", 3.2)                     # in diesem Lauf archiviert
    _log(archiv / "stufe-88.json", 4.0)                     # in diesem Lauf archiviert
    _log(archiv / "stufe-9-alt.json", 99.0, alter_sekunden=90 * 86400)  # alte Kaskade

    seit = int(time.time()) - 3600
    summe = float(_bash(f'team_kosten_seit "{seit}" "{logs}" "{archiv}"'))

    assert abs(summe - 7.6) < 1e-6, (
        f"Erwartet 7.6 (0.4 aktiv + 3.2 + 4.0 im Lauf archiviert), erhalten {summe}. "
        "Ohne die Archivpfade faellt bereits ausgegebenes Geld mitten im Lauf aus "
        "der Pro-Lauf-Durchsetzung (BL-55, Fund 1)."
    )
    assert summe < 99.0, (
        "Das Archiv-Log einer frueheren Kaskade darf NICHT mitzaehlen — der "
        "mtime-Filter ist die einzige Trennlinie."
    )


def test_lauf_kosten_nennt_beide_archivpfade():
    quelle = VOLLAUTOMATIK.read_text(encoding="utf-8")
    zeile = next(z for z in quelle.splitlines() if z.startswith("lauf_kosten()"))

    for pfad in (".ralph-logs", ".team-logs", ".ralph-logs/archiv", ".team-logs/archiv"):
        assert pfad in zeile, (
            f"lauf_kosten() (Durchsetzung A) muss {pfad} zaehlen, sonst wird der "
            f"Pro-Lauf-Deckel durch eine Archivierung mitten im Lauf blind (BL-55)."
        )


def test_kontostand_gesamt_zaehlt_das_archiv_nicht_mit():
    """Gegenprobe: Kennzahl B darf das Archiv NICHT sehen — dort ist dasselbe Geld
    bereits ueber die .budget-ledger-Zeile erfasst (BL-17). Sonst zaehlt es doppelt."""
    quelle = TEAM_LIB.read_text(encoding="utf-8")
    koerper = quelle[quelle.index("team_kontostand_gesamt() {"):]
    koerper = koerper[:koerper.index("\n}")]

    assert "archiv" not in koerper, (
        "team_kontostand_gesamt (Anzeige B) darf die Archivpfade nicht summieren — "
        "sie sind bereits als Ledger-Zeile gebucht (BL-17-Doppelzaehlung)."
    )


def test_kein_kostenabschluss_mehr_in_einer_ralph_stufe():
    """Die Regel, die den Fund ueberhaupt ausgeloest hat: der Kostenabschluss
    gehoert in den Architekten-Closeout nach dem Lauf."""
    claude_md = REGELDATEI.read_text(encoding="utf-8")
    # T.E.A.M.-Starterkit: zusaetzlich Markdown-Hervorhebungen entfernen. Ohne
    # das scheitert die Pruefung an einem **nie** mitten im Satz, obwohl die
    # Regel woertlich dasteht — ein Fehlalarm, kein Regelverstoss.
    normalisiert = re.sub(r"[*_`]", "", claude_md)
    normalisiert = re.sub(r"\s+", " ", normalisiert)

    # T.E.A.M.-Starterkit: Der urspruengliche Test verlangte EINEN woertlichen
    # Satz aus der CLAUDE.md des Feldprojekts. Fuer eine Vorlage, die in fremden
    # Projekten anders formuliert sein darf, wird stattdessen die SUBSTANZ
    # geprueft: Closeout nach dem Lauf UND ausdrueckliches Verbot in der Stufe.
    hat_closeout = "Closeout" in normalisiert
    hat_verbot = any(
        wort in normalisiert for wort in ("NIEMALS in eine", "nie in einer", "niemals in einer")
    )
    hat_stufenbezug = any(
        wort in normalisiert for wort in ("Ralph-Stufe", "Loop-Stufe", "Loop-Stufe.")
    )
    assert hat_closeout and hat_verbot and hat_stufenbezug, (
        "CLAUDE.md muss den Kostenabschluss ausdruecklich aus der Bau-Stufe "
        "heraushalten und in den Closeout nach dem Lauf verweisen (BL-55). "
        f"Gefunden: closeout={hat_closeout} verbot={hat_verbot} stufe={hat_stufenbezug}"
    )


if __name__ == "__main__":
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        test_summe_cost_usd_addiert_alle_versuche(Path(d) / "a")
        test_summe_cost_usd_toleriert_fehlende_und_kaputte_logs(Path(d) / "b")
        test_kosten_seit_findet_die_im_lauf_archivierten_logs(Path(d) / "c")
    test_team_claude_setzt_last_cost_aus_allen_versuchen()
    test_lauf_kosten_nennt_beide_archivpfade()
    test_kontostand_gesamt_zaehlt_das_archiv_nicht_mit()
    test_kein_kostenabschluss_mehr_in_einer_ralph_stufe()
    print("gruen — BL-55 verifiziert: Archiv-Blindheit und Fehlversuchs-Kosten geschlossen.")
    sys.exit(0)

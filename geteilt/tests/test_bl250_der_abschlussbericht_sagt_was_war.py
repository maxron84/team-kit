#!/usr/bin/env python3
"""BL-250, BL-254 (3), BL-259 (3), BL-240, BL-299: Der Abschlussbericht der
Vollautomatik sagt, was im Lauf war — nicht nur, was er gekostet hat.

BL-250 (`Feld B`)  Ein verfallener Red-Team-Fokus war nur eine Logzeile mitten
                   im Lauf; der Bericht schwieg, und ein Sweep ohne Auftrag sah
                   aus wie ein gegluekter.
BL-254 (3)         Nach jeder Rolle, die das Beutebuch anfassen durfte, laeuft
                   `beutebuch.py lint` — ohne Abbruch, der Befund steht im
                   Bericht.
BL-259 (3)         Ein Fund auf `offen` ist fuer die Fix-Phase unsichtbar; der
                   Bericht zaehlt ihn.
BL-240             Betrag und Turn-Aufzaehlung beschreiben dieselbe Menge (alle
                   Rollen DIESES Laufs), dazu eine Zeile fuer die Kaskade.
BL-299             Die Abdeckungszeilen der Sweeps stehen im Bericht.

Gefahren gegen Stub-Rollen auf beiden Bahnen (Fixture aus BL-241).
"""
import json
import os

import test_bl241_fixphase_hat_einen_eigenen_einstieg as h
from conftest import verlange_bash, verlange_pwsh

BUCH = """# Beutebuch

## Funde

### HM-1 — Gesichtet, aber nie uebergeben

- **Status**: offen
- **Fundstelle**: `src/app.py`
- **Reproducer-Test**: `tests/test_hm1_app.py`

### HM-2 — Ohne Pflichtzeile

- **Status**: an Frank übergeben
- **Fundstelle**: `src/app.py`
"""


def _sweep_stub(rolle, bahn):
    """Ein Sweep, der seine Fokus-Lage protokolliert, eine Abdeckungszeile
    meldet und mit 0 endet — so, wie es redteam.* im Ernstfall tut."""
    log = json.dumps({"subtype": "success", "result":
                      "Geprueft.\nABDECKUNG 1: geprüft, ohne Befund\n"
                      "ABDECKUNG 2: nicht geprüft — keine Zeit\n"
                      "<promise>REDTEAM_SWEEP_COMPLETE</promise>",
                      "total_cost_usd": 0.5, "num_turns": 9},
                     ensure_ascii=False)
    if bahn == "bash":
        return (f'#!/usr/bin/env bash\necho "STUB {rolle}"\n'
                f'printf "VERFALLEN — Grundauftrag\\n-\\n" > .team-logs/fokus-{rolle}.txt\n'
                f"cat > .team-logs/{rolle}-20991231-000000.json <<'J'\n{log}\nJ\n"
                f"exit 0\n")
    return (f"[Console]::Out.WriteLine('STUB {rolle}')\n"
            f"Set-Content -Path .team-logs/fokus-{rolle}.txt "
            f"-Value \"VERFALLEN — Grundauftrag`n-\" -Encoding utf8\n"
            f"Set-Content -Path .team-logs/{rolle}-20991231-000000.json "
            f"-Value @'\n{log}\n'@ -Encoding utf8\n"
            f"exit 0\n")


def _lage(repo, bahn):
    (repo / "plans" / "beutebuch.md").write_text(BUCH, encoding="utf-8")
    for rolle in ("harry", "marv"):
        datei = repo / f"{rolle}.{'sh' if bahn == 'bash' else 'ps1'}"
        datei.write_text(_sweep_stub(rolle, bahn),
                         encoding="utf-8" if bahn == "bash" else "utf-8-sig",
                         newline="\n")
        if bahn == "bash":
            datei.chmod(0o755)


def _pruefe(aus):
    assert "Red Team: harry — Fokus VERFALLEN" in aus, aus          # BL-250
    assert "Red Team: marv — Fokus VERFALLEN" in aus, aus
    assert "ABDECKUNG 2: nicht geprüft — keine Zeit" in aus, aus    # BL-299
    assert "Beutebuch nach harry" in aus and "Kit-BL-254" in aus, aus
    assert "1 Fund(e) stehen auf 'offen'" in aus, aus               # BL-259
    assert "alle Rollen DIESES Laufs" in aus, aus                   # BL-240
    assert "Lauf/Laeufe" in aus and "harry-20991231-000000.json" in aus, (
        "Die Turn-Aufzaehlung nennt die Rollen-Laeufe dieses Laufs nicht "
        f"(BL-240).\n{aus}")


def test_bash_der_bericht_sagt_was_war(tmp_path):
    verlange_bash()
    repo = h._bash_projekt(tmp_path)
    _lage(repo, "bash")
    r = h._bash(repo, "vollautomatik.sh")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    _pruefe(aus)


def test_pwsh_der_bericht_sagt_was_war(tmp_path):
    verlange_pwsh()
    repo = h._pwsh_projekt(tmp_path)
    _lage(repo, "pwsh")
    r = h._pwsh(repo, "vollautomatik.ps1")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    _pruefe(aus)


def test_ohne_besonderheiten_bleibt_der_bericht_ruhig(tmp_path):
    """Gegenrichtung: Eine Meldung, die immer kommt, ist keine (BL-14)."""
    verlange_bash()
    repo = h._bash_projekt(tmp_path)
    r = h._bash(repo, "vollautomatik.sh")
    aus = r.stdout + r.stderr
    assert r.returncode == 0, aus
    for laut in ("Kit-BL-254", "Kit-BL-259", "Fokus VERFALLEN", "Abdeckung"):
        assert laut not in aus, f"{laut} ohne Anlass:\n{aus}"

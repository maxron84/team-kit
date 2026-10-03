#!/usr/bin/env python3
"""BL-304: Der Lauf-Deckel liegt ueber dem Soft-Cap einer Rolle (Entscheid
des Owners, 2026-10-03).

Mit `BL-286` stiegen die Rollen-Caps auf 20/40 USD, der Default des
Lauf-Deckels `TEAM_BUDGET_USD` blieb bei 15. Damit stoppte ein teurer
Einzelaufruf von Ralph, Harry oder Marv in der Regel am LAUF-Deckel statt am
Rollen-Cap — die Rangfolge war umgekehrt, und `BL-286` hat das nur benannt.
Der Owner hat entschieden: Der Lauf-Deckel steigt mit, Default 50 USD.

Der Wert steht in vier Entrypoints (Voll- und Halbautomatik je Bahn). Dieser
Test haelt sie gegeneinander und gegen den Soft-Cap der Bibliotheken —
stellt jemand nur eine Stelle um, wird er rot.
"""
import re

import pytest

from conftest import entrypoint_pfad, kit_pfad

DEFAULT = "50"

STELLEN = {
    "vollautomatik.sh": r'^TEAM_BUDGET_USD="\$\{TEAM_BUDGET_USD:-(\d+)\}"$',
    "vollautomatik.ps1": r"^\$budgetUsd = if \(\$env:TEAM_BUDGET_USD\) "
                         r"\{ \$env:TEAM_BUDGET_USD \} else \{ '(\d+)' \}$",
    "halbautomatik.sh": r"^\s+empfehlung=(\d+)$",
    "halbautomatik.ps1": r"^\s+\$empfehlung = '(\d+)'$",
}


@pytest.mark.parametrize("datei", sorted(STELLEN))
def test_der_default_des_lauf_deckels(datei):
    pfad = entrypoint_pfad(datei)
    if not pfad.is_file():
        pytest.skip(f"{datei} liegt in dieser Ablage nicht (Bahn abgewaehlt)")
    treffer = re.findall(STELLEN[datei], pfad.read_text(encoding="utf-8-sig"),
                         re.M)
    assert treffer == [DEFAULT], (
        f"{datei}: Default des Lauf-Deckels ist {treffer}, erwartet "
        f"[{DEFAULT!r}] (BL-304).")


@pytest.mark.parametrize("lib,muster", [
    ("lib.sh", r'^TEAM_ROLE_BUDGET_USD="\$\{TEAM_ROLE_BUDGET_USD:-(\d+)\}"'),
    ("lib.psm1", r"TEAM_ROLE_BUDGET_USD\s*=.*?'(\d+)'"),
])
def test_der_lauf_deckel_liegt_ueber_dem_soft_cap(lib, muster):
    pfad = kit_pfad(lib)
    if not pfad.is_file():
        pytest.skip(f"{lib} liegt in dieser Ablage nicht (Bahn abgewaehlt)")
    treffer = re.search(muster, pfad.read_text(encoding="utf-8-sig"), re.M)
    assert treffer, f"Soft-Cap-Default in {lib} nicht gefunden"
    assert float(DEFAULT) > float(treffer.group(1)), (
        f"Der Lauf-Deckel ({DEFAULT}) liegt nicht ueber dem Soft-Cap einer "
        f"Rolle ({treffer.group(1)}) — ein teurer Einzelaufruf stoesst dann "
        f"zuerst an den Lauf-Deckel (BL-304).")

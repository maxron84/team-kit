#!/usr/bin/env python3
"""BL-297: Wer den Soft-Cap ueber den Hard-Cap hob, schaltete Franks und Axels
Airbag still ab.

WAS IM FELD PASSIERT IST (`Feld E`, 2026-08-24, dritte Kaskade)
    Eine UI-Stufe brach am Soft-Cap (5) ab; der Stakeholder hob ihn auf 20 —
    der Weg, den die Regeldatei selbst nennt. `team_budget_check` prueft den
    Hard-Cap aber nur bei `hard > soft`: Bei 20/10 greift er NIE mehr, fuer
    genau die beiden iterierenden Rollen, fuer die er erfunden wurde (bei
    ihnen ist der Soft-Cap nur ein Hinweis, `HM-32`). Kein Hinweis beim
    Start, keine Zeile im Status — aufgefallen nur, weil vorher jemand in den
    Quelltext sah. Gemeldet am 2026-08-24, triagiert erst am 2026-10-03.

WAS GEBAUT IST
    Die Bibliothek warnt beim Laden, sobald Hard <= Soft gilt, auf beiden
    Bahnen; die Regeldatei-Vorlage nennt die Kopplung.
"""
import sys
from pathlib import Path

from conftest import REPO_ROOT, Variable


def _laden(schale, tmp_path, soft, hard):
    lib = schale.lib_kopieren(tmp_path)
    return schale.lauf([Variable("TEAM_ROLE_HARDCAP_USD")], cwd=tmp_path,
                       lib=lib, env={"TEAM_ROLE_BUDGET_USD": soft,
                                     "TEAM_ROLE_HARDCAP_USD": hard})


def test_soft_ueber_hard_wird_laut(tmp_path, schale):
    r = _laden(schale, tmp_path, "20", "10")
    assert "BL-297" in r.stderr and "KEINEN harten Abbruch" in r.stderr, (
        f"{schale.name}: Soft-Cap 20 ueber Hard-Cap 10 — Frank und Axel haben "
        f"keinen Airbag mehr, und die Bibliothek schweigt.\n{r.stderr}")


def test_gleichstand_ist_ebenso_wirkungslos(tmp_path, schale):
    """`hard > soft` ist die Bedingung — bei Gleichstand greift er auch nicht."""
    r = _laden(schale, tmp_path, "15", "15")
    assert "BL-297" in r.stderr, r.stderr


def test_die_defaults_bleiben_still(tmp_path, schale):
    r = _laden(schale, tmp_path, "20", "40")
    assert "BL-297" not in r.stderr, r.stderr


def test_die_regeldatei_nennt_die_kopplung():
    vorlage = REPO_ROOT / "bootstrap" / "CLAUDE.md.vorlage"
    if not vorlage.is_file():
        import pytest
        pytest.skip("die Vorlage liegt nur im Kit")
    assert "Kit-BL-297" in vorlage.read_text(encoding="utf-8")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))

#!/usr/bin/env python3
"""BL-262: Beide Selbsttests verstellen dieselben Werte — in BEIDEN Konfigurationen.

Der Befund (Meldung 2026-09-26): `bash/kit-test.sh` Stufe 5 (`BL-58`, die Suite
unter angepasster Konfiguration) verstellte nur `team.config.sh`. Das Gegenstueck
in `pwsh/kit-test.ps1` Schritt 6 verstellt seit 2026-08-26 beide und begruendet
es selbst: "Ein Wert, der nur in team.config.sh angehoben wird, laesst die
pwsh-Bahn auf dem Auslieferungsstand." Am selben Tag kam der Gleichstandstest
aus `BL-117`, der die Prompts beider Bahnen am Lauf vergleicht — und Franks
Prompt traegt den Commit-Praefix. Auf jedem Wirt mit bash UND pwsh 7 stand in
Stufe 5 damit `fix(qa)` gegen `fix(uat)`, der Fall wurde rot, und der Selbsttest
brach ab, bevor die Stufen 6-11 liefen. Ohne pwsh ueberspringt sich der Fall:
Die Luecke war genau dort unsichtbar, wo sie nicht zuschlug.

Die Bauart ist die von `BL-144`/`BL-208`: eine Bahn nachgezogen, die andere
nicht. Deshalb prueft diese Datei nicht nur die bash-Fassung, sondern den
GLEICHSTAND der beiden Wertelisten — damit die naechste Aenderung an einer
Liste die andere nicht wieder zuruecklaesst.

Wie BL-208 liest sie die Quelltexte der Selbsttests. Die liegen nur in der
Kit-Ablage; in einer Installation ueberspringt sie sich mit Begruendung.
"""
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]
BASH = WURZEL / "bash" / "kit-test.sh"
PWSH = WURZEL / "pwsh" / "kit-test.ps1"


def _lies(pfad, was):
    if not pfad.is_file():
        pytest.skip(f"{was} liegt hier nicht (Installation statt Kit-Ablage — "
                    "die Selbsttests werden nicht mitinstalliert)")
    return pfad.read_text(encoding="utf-8-sig")


def _bash_paare(text):
    block = re.search(r"^KONFIG_PAARE=\((.*?)^\)", text, re.S | re.M)
    assert block, ("kit-test.sh fuehrt keine Werteliste KONFIG_PAARE mehr — "
                   "dann laesst sich der Gleichstand nicht pruefen.")
    return {tuple(e.split("=", 1)) for e in re.findall(r'"([^"]+)"', block.group(1))}


def _pwsh_paare(text):
    zeilen = re.findall(r"@\{\s*Sh\s*=\s*'([^']+)';\s*ShNeu\s*=\s*'([^']*)';"
                        r"\s*Ps\s*=\s*'([^']+)';\s*PsNeu\s*=\s*'([^']*)'\s*\}", text)
    assert zeilen, "kit-test.ps1 fuehrt keine $paare-Liste mehr."
    return ({(sh, shneu) for sh, shneu, _, _ in zeilen},
            {(ps, psneu) for _, _, ps, psneu in zeilen})


def test_beide_selbsttests_verstellen_dieselben_paare():
    bash = _bash_paare(_lies(BASH, "kit-test.sh"))
    pwsh_sh, pwsh_ps = _pwsh_paare(_lies(PWSH, "kit-test.ps1"))
    assert bash == pwsh_sh, (
        "Die beiden Selbsttests verstellen verschiedene Werte in team.config.sh:\n"
        f"  nur kit-test.sh:  {sorted(bash - pwsh_sh)}\n"
        f"  nur kit-test.ps1: {sorted(pwsh_sh - bash)}")
    assert pwsh_sh == pwsh_ps, (
        "kit-test.ps1 verstellt in team.config.sh und team.config.ps1 "
        "verschiedene Werte — dann laufen die Bahnen schon im Selbsttest "
        "auseinander.")


def test_die_bash_fassung_verstellt_auch_die_pwsh_konfiguration():
    """Der Befund selbst: Die Werteliste allein genuegt nicht, sie muss auf
    team.config.ps1 ANGEWANDT und dort nachkontrolliert werden."""
    text = _lies(BASH, "kit-test.sh")
    stufe = re.search(r'kopf "5/11.*?kopf "6/11', text, re.S)
    assert stufe, "Stufe 5 von kit-test.sh ist nicht auffindbar."
    stufe = stufe.group(0)
    assert stufe.count('"$ZIEL/team.config.ps1"') >= 2, (
        "kit-test.sh Stufe 5 verstellt team.config.ps1 nicht (oder prueft die "
        "Anpassung dort nicht nach) — auf einem Wirt mit pwsh wird dann der "
        "Prompt-Gleichstand aus BL-117 rot (BL-262).")

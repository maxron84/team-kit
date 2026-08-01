"""TEAM.md ist der menschliche Einstiegspunkt.

Regressionsschutz fuer die Luecke, die beim Abnahmegespraech auffiel: Die
kritische Guard-Warnung ("erst committen, dann starten") stand nur in der
Terminal-Ausgabe des Installers — und die scrollt weg. Genau der Fehler, den
Planungsregel 5 fuer den Abschlussbericht behebt.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEAM_MD = REPO_ROOT / "TEAM.md"


def _text():
    if not TEAM_MD.exists():
        return None
    return TEAM_MD.read_text(encoding="utf-8")


def test_team_md_existiert_im_projekt():
    """Im installierten Projekt muss TEAM.md in der Wurzel liegen."""
    if not (REPO_ROOT / "team.config.sh").exists():
        return  # Kit-Repo selbst, nicht installiert
    assert TEAM_MD.exists(), (
        "TEAM.md fehlt — der Mensch haette keinen Einstiegspunkt und faende "
        "die Guard-Warnung nirgends."
    )


def test_guard_warnung_steht_ganz_oben():
    """Die teuerste Warnung des Kits darf nicht im Fliesstext untergehen."""
    t = _text()
    if t is None:
        return
    kopf = t[:1200]
    assert "committen" in kopf.lower(), (
        "Die Commit-vor-Guard-Warnung muss im Kopfbereich von TEAM.md stehen."
    )
    assert "Guard" in kopf, "Der Grund (Read-Only-Guard) muss dabeistehen."


def test_exit_codes_erklaert():
    """42 ist kein Fehler — die haeufigste Verwechslung im Betrieb."""
    t = _text()
    if t is None:
        return
    assert "42" in t and "Session-Limit" in t, (
        "TEAM.md muss Exit 42 als Pause erklaeren, nicht als Absturz."
    )
    for code in ("`0`", "`1`", "`3`", "`42`"):
        assert code in t, f"Exit-Code {code} fehlt in TEAM.md"


def test_closeout_als_pflicht_benannt():
    """Ohne Closeout sind die Architekt-Kosten strukturell unerfasst."""
    t = _text()
    if t is None:
        return
    assert "architekt-abschluss" in t, "Closeout-Befehl fehlt in TEAM.md"
    assert "Pflicht" in t, "Closeout muss als Pflicht gekennzeichnet sein"


def test_keine_offenen_platzhalter():
    """Nach dem Installieren darf kein {{...}} mehr sichtbar sein."""
    t = _text()
    if t is None:
        return
    if not (REPO_ROOT / "team.config.sh").exists():
        return
    import re
    offen = re.findall(r"\{\{[A-Za-z0-9_]+\}\}", t)
    assert not offen, f"Ungefuellte Platzhalter in TEAM.md: {sorted(set(offen))}"

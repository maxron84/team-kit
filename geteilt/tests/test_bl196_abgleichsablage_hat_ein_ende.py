#!/usr/bin/env python3
"""BL-196 — die Abgleichsablage aus `BL-178` bleibt liegen, und niemand sagt,
dass sie weggeworfen werden darf.

Beide Installer rendern für den Block „Bitte von Hand abgleichen" die
Kit-Fassung der abweichenden Dateien in ein Wegwerf-Verzeichnis
(`$TMPDIR/team-kit-abgleich-*`) und nennen im Hinweis den Vergleichsbefehl
darauf. Aufgeräumt wird **nur, wenn nichts abweicht**; weicht etwas ab — und
bei `CLAUDE.md` ist das laut demselben Block ausdrücklich der **Normalfall** —,
bleibt das Verzeichnis stehen. Das ist so gewollt: Der Anwender soll den
genannten Befehl noch ausführen können.

Nur endet die Zusage dort. **Kein Satz sagte, dass die Ablage danach
entbehrlich ist**, kein Lauf entfernte eine ältere, und der Hinweis nannte sie
nicht als temporär. GEMESSEN, NICHT VERMUTET: Nach einem Arbeitstag mit
Selbsttest-Läufen und Update-Proben lagen **elf** solcher Verzeichnisse in
`%TEMP%` — kein Platzproblem (36–60 KB je Stück), ein Ordnungsproblem.

Ein Verzeichnis, dessen Lebensdauer niemand benennt, wird entweder nie
gelöscht oder im falschen Moment — nämlich bevor der Anwender den Vergleich
gefahren hat. Bauart `BL-44`: ein Hinweis, der eine Handlung ankündigt, ohne
ihren Rahmen zu nennen.

AUSDRÜCKLICH NICHT geprüft wird hier, dass die Ablage sofort nach dem Rendern
verschwindet. Sie ist die einzige Stelle, an der der Anwender die Kit-Fassung
sehen kann, und der Block ist genau dafür gebaut (`BL-4`, zweite Hälfte).
"""
import re
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]

INSTALLER = {"bash": WURZEL / "bash" / "install.sh",
             "pwsh": WURZEL / "pwsh" / "install.ps1"}
SELBSTTEST = {"bash": WURZEL / "bash" / "kit-test.sh",
              "pwsh": WURZEL / "pwsh" / "kit-test.ps1"}

# Der Loeschbefehl, den die jeweilige Bahn nennen MUSS — in ihrer eigenen
# Schreibweise. Ein `rm -rf`, das Windows nicht kennt, waere die Bauart BL-44
# ein zweites Mal: angekuendigt, aber nicht am wirksamen Ort ausfuehrbar.
LOESCHBEFEHL = {"bash": "rm -rf", "pwsh": "Remove-Item"}


def _text(pfad):
    if not pfad.is_file():
        pytest.skip(f"{pfad.name} liegt nur im Kit")
    return pfad.read_text(encoding="utf-8")


# --- (1) Der Hinweis sagt, was mit der Ablage geschieht ----------------------


def test_der_hinweis_nennt_die_ablage_als_kopie(schale):
    """Ohne diesen Satz ist jede weitere Mechanik Rätselraten."""
    text = _text(INSTALLER[schale.name])
    assert "KOPIE zum Nachlesen" in text, (
        f"{INSTALLER[schale.name].name} sagt nicht, dass die gerenderte "
        "Kit-Fassung eine Kopie zum Nachlesen ist. Wer das nicht weiß, hält "
        "sie für einen Teil seines Projekts (BL-196).")
    assert "Temp" in text, (
        "…und auch nicht, dass sie im Temp-Bereich liegt.")


def test_der_hinweis_nennt_den_loeschbefehl_dieser_bahn(schale):
    """Kopierfertig und in der richtigen Schreibweise — sonst verlangt der
    Hinweis genau die Arbeit, die er abnehmen wollte (`BL-44`)."""
    text = _text(INSTALLER[schale.name])
    befehl = LOESCHBEFEHL[schale.name]
    # Der Befehl muss im Abgleich-Block stehen, nicht irgendwo im Skript.
    block = re.search(
        r"(?s)Bei CLAUDE\.md ist eine Abweichung normal.{0,2000}",
        text)
    assert block, "der Abgleich-Block ist nicht mehr auffindbar"
    assert befehl in block.group(0), (
        f"Der Hinweis nennt keinen {befehl}-Befehl für die Ablage. Ein "
        "Verzeichnis, dessen Lebensdauer niemand benennt, wird entweder nie "
        "gelöscht oder im falschen Moment (BL-196).")
    assert "abgleich" in block.group(0).lower(), (
        "…und der Befehl zeigt nicht auf die Abgleichsablage.")


def test_kein_installer_loescht_die_ablage_vorzeitig(schale):
    """Die Gegenrichtung, und sie ist die wichtigere: Die Ablage ist die
    EINZIGE Stelle, an der der Anwender die Kit-Fassung sehen kann. Wer sie
    sofort nach dem Rendern entfernt, nimmt dem Block seinen Zweck (`BL-4`)."""
    text = _text(INSTALLER[schale.name])
    # Aufgeraeumt werden darf NUR im Zweig "nichts weicht ab".
    if schale.ist_bash:
        aufraeumen = re.findall(r"(?m)^\s*rmdir \"\$ABGLEICH_DIR\"", text)
    else:
        aufraeumen = re.findall(
            r"(?m)^\s*Remove-Item -LiteralPath \$abgleichDir", text)
    assert len(aufraeumen) <= 1, (
        "Die Ablage wird an mehr als einer Stelle entfernt — eine davon "
        "trifft den Anwender, bevor er verglichen hat (BL-196/BL-4).")


# --- (2) Der Selbsttest hinterlässt keine Ablage -----------------------------


def test_beide_selbsttests_raeumen_ihre_ablagen_weg(schale):
    """`kit-test.sh` tut das nach jedem der beiden Update-Läufe ausdrücklich;
    der pwsh-Bahn fehlte es — der Rest von `BL-145`, an derselben Stelle wie
    `BL-198` Teil (3)."""
    text = _text(SELBSTTEST[schale.name])
    assert "team-kit-abgleich" in text, (
        f"{SELBSTTEST[schale.name].name} kennt die Abgleichsablage nicht und "
        "kann sie deshalb auch nicht wegräumen — je Selbsttest-Lauf bleibt "
        "eines liegen (BL-196).")
    befehl = LOESCHBEFEHL[schale.name]
    assert befehl in text, (
        f"{SELBSTTEST[schale.name].name} entfernt nichts.")


def test_das_aufraeumen_hat_eine_schranke_gegen_falsche_pfade(schale):
    """Ein `rm -rf` / `Remove-Item -Recurse` auf einen falsch geparsten Pfad
    ist teurer als der liegen gebliebene Ordner. `kit-test.sh` hält das seit
    Langem fest ("`dirname ''` ergäbe `.`"); die pwsh-Bahn braucht dieselbe
    Schranke."""
    text = _text(SELBSTTEST[schale.name])
    stelle = text.find("team-kit-abgleich")
    umfeld = text[max(0, stelle - 1500):stelle + 1500]
    assert re.search(r"team-kit-abgleich-[^\s\"']*[*+\[]", umfeld) or \
           "case " in umfeld or "Test-Path" in umfeld, (
        "Das Aufräumen prüft den Pfad nicht, bevor es rekursiv löscht — genau "
        "die Zeile, die man einmal richtig schreibt und nie wieder ansieht.")


def test_der_selbsttest_meldet_wenn_er_nichts_wegraeumen_konnte(schale):
    """Die Gegenrichtung des Aufräumens: Erkennt der Lauf KEINE Ablage, ist
    entweder der Block nicht gelaufen oder das Muster veraltet — und dann
    räumt dieser Teil still gar nichts weg, während er grün aussieht."""
    text = _text(SELBSTTEST[schale.name])
    stelle = text.find("team-kit-abgleich")
    umfeld = text[max(0, stelle - 800):stelle + 2000]
    assert ("kein Abgleich-Verzeichnis erkannt" in umfeld
            or "weggeräumt" in umfeld or "weggeraeumt" in umfeld), (
        "Ein Aufräumen, das nichts findet, sieht genauso aus wie eines, das "
        "aufgeräumt hat (BL-196).")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

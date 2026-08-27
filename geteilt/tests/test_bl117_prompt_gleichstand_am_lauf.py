#!/usr/bin/env python3
"""BL-117: Der Prompt-Gleichstand war am QUELLTEXT bewiesen, nicht am LAUF.

WAS `BL-112` ABDECKT UND WAS ES OFFEN LIESS
    [`test_bl112_prompt_gleichstand.py`](test_bl112_prompt_gleichstand.py)
    vergleicht die **Prosa** beider Bahnen, nachdem jede Variableneinsetzung
    zu einem Platzhalter geworden ist. Das trifft den Fall, für den `BL-112`
    geschrieben wurde — jemand schärft eine Feldlehre in nur einer Fassung
    nach — und lässt genau eine Lücke, die der Eintrag wörtlich benennt:

        „Setzen die beiden Bahnen in denselben Platzhalter VERSCHIEDENE
         WERTE ein … sind die Prompts verschieden und der Test bleibt grün."

    Ein anders abgeleiteter Ordnername, eine Fallunterscheidung, die nur eine
    Seite kennt, ein `team.config.ps1`, das einen Wert anders vorbelegt — jede
    dieser Abweichungen steuert zwei verschiedene Agenten, und der
    Quelltext-Vergleich sieht sie nicht. **Diese Hälfte kann nur ein Lauf
    zeigen**, und dafür braucht es beide Shells auf einer Maschine.

    `BL-163` ist der erste **gemessene** Fall dieser Gattung gewesen: derselbe
    Platzhalter, zwei Werte (`C:/…` gegen `C:\\…`). Er traf `team.config.*`
    statt eines Rollen-Prompts — dieselbe Mechanik, anderer Adressat.

WIE HIER GEMESSEN WIRD
    Ein Stub tritt an die Stelle der CLI und schreibt sein `-p`-Argument in
    eine Datei, statt zu arbeiten. Beide Bahnen fahren **dieselbe Rolle** im
    **selben** Wegwerf-Projekt, und die zwei Prompt-Dateien werden zeichenweise
    verglichen. Die Ausnahmeliste aus `BL-112` wird **mitbenutzt**, samt ihrer
    Begründungspflicht — eine zweite Liste danebenzustellen hieße, zwei Orte
    zu pflegen, an denen Drift verschwinden kann.

    Eingehängt wird der Stub über `TEAM_CLAUDE_BIN` (`BL-173`). Vor diesem
    Eintrag hätte es dafür einen PATH-Trick gebraucht, der auf einer Maschine
    mit echter CLI im PATH wirtsabhängig ist.

WARUM DER PWSH-STUB EINE `.ps1` IST UND KEIN `.cmd`
    Gemessen wird, **was die Bahn übergibt**. Ein `.cmd` bekäme den Prompt
    über eine Kommandozeile, die `cmd.exe` neu zerlegt — mehrzeiliger Text mit
    Anführungszeichen überlebt das nicht, und das Messgerät würde den Befund
    erzeugen, den es messen soll. `& <pfad.ps1>` bindet die Argumente dagegen
    unverändert. Die Transportkodierung eines echten `.cmd`-Shims ist eine
    andere Frage als die dieses Eintrags.

WO DIESER TEST LÄUFT
    Nur in einer **installierten** Ablage mit **beiden** Bahnen — die
    Entrypoints liegen im Kit unter `bash/entry/` bzw. `pwsh/entry/` und sind
    dort nicht lauffähig. Gefahren wird er damit von `kit-test.sh` (Stufe 4/5)
    und von `kit-test.ps1`, sobald `BL-145` dessen Umfang angeglichen hat.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import (BASH, entrypoint_aufruf, kopiere_team_namensraum,  # noqa: E402
                      ueberspringe_ohne_beide_bahnen, verlange_pwsh)
from test_bl112_prompt_gleichstand import AUSNAHMEN, kanon  # noqa: E402

WURZEL = Path(__file__).resolve().parents[2]

# Die Rollen, die einen Prompt zusammensetzen. `harry` und `marv` teilen sich
# redteam.*; `axel`, `frank` und `ralph` bauen ihren eigenen. Das sind genau
# die vier Prompt-Bloecke, die BL-112 am Quelltext vergleicht.
ROLLEN = ["harry", "marv", "axel", "frank"]

# Was der Stub als Antwort liefert: das Minimum, an dem `team_bewerte_ergebnis`
# einen sauberen Erfolg erkennt (is_error false UND subtype success), mit einem
# nicht leeren `result` — ein leeres gilt dem Kit als stiller Fehlschlag.
ANTWORT = json.dumps({
    "subtype": "success", "is_error": False, "stop_reason": "end_turn",
    "result": "Stub-Antwort: nichts gefunden.", "total_cost_usd": 0.0,
}, ensure_ascii=False)


def _verlange_installierte_ablage():
    fehlend = [n for n in ("harry.sh", "harry.ps1", "team.config.sh",
                           "team.config.ps1")
               if not (WURZEL / n).is_file()]
    if fehlend:
        pytest.skip(
            "Der Lauf-Vergleich braucht eine INSTALLIERTE Ablage mit beiden "
            f"Bahnen; hier fehlen: {', '.join(fehlend)}. Im Kit liegen die "
            "Entrypoints unter bash/entry/ und pwsh/entry/ und sind dort "
            "nicht lauffaehig — gefahren wird das ueber kit-test.sh.")


def _konfig(schluessel):
    """Liest einen Wert aus der installierten `team.config.sh`.

    Die Ordnernamen bestimmt das Zielprojekt, nicht dieser Test — dieselbe
    Erwaegung wie in `test_bl47`.
    """
    return subprocess.run(
        [BASH, "-c",
         f'source "{WURZEL}/team.config.sh"; printf "%s" "${schluessel}"'],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace").stdout


BASH_STUB = """#!/usr/bin/env bash
# Schreibt das Argument nach -p in die Fangdatei und antwortet mit dem Stub.
ziel="$TEAM_PROMPT_FANG"
vorher=""
for a in "$@"; do
    if [ "$vorher" = "-p" ]; then printf '%s' "$a" > "$ziel"; fi
    vorher="$a"
done
cat <<'TEAMJSON'
{antwort}
TEAMJSON
"""

PWSH_STUB = """param()
# Schreibt das Argument nach -p in die Fangdatei und antwortet mit dem Stub.
$vorher = ''
foreach ($a in $args) {{
    if ($vorher -eq '-p') {{
        [System.IO.File]::WriteAllText($env:TEAM_PROMPT_FANG, $a,
            (New-Object System.Text.UTF8Encoding($false)))
    }}
    $vorher = $a
}}
Write-Output @'
{antwort}
'@
exit 0
"""


FUND = """
### HM-{nr} — Testfund fuer den Lauf-Vergleich
- **Angreifer**: Harry
- **Schweregrad**: klein
- **Status**: {status}
- **Reproschritte**: 1. Nichts tun
- **Erwartung**: nichts
- **Realität**: nichts
- **Reproducer-Test**: `{test}`
"""


def _funde_anlegen(repo, beutebuch):
    """Gibt `axel` und `frank` etwas zu tun.

    Beide Rollen enden mit Exit 3 („nichts zu tun"), wenn kein Fund mit ihrem
    Status im Beutebuch steht — und dann entsteht **kein Prompt**. Ein Test,
    der das übersieht, vergleicht zwei nicht vorhandene Dateien und wäre die
    teuerste Bauform: grün, ohne etwas gemessen zu haben. `_fahre` bricht
    deshalb ab, statt Leeres zurückzugeben.

    Die Nummern kommen aus `next-id` des **echten** Beutebuchs (`BL-62`): Fest
    verdrahtete Nummern brechen, sobald das Zielprojekt eigene Funde
    mitbringt.
    """
    werkzeug = _konfig("TEAM_BEUTEBUCH_TOOL").split()
    roh = subprocess.run(werkzeug + ["next-id"], cwd=repo, check=True,
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace").stdout.strip()
    nr = int(roh.lstrip("HM-") or "1")
    test_ordner = _konfig("TEAM_TEST_ORDNER").rstrip("/")
    text = beutebuch.read_text(encoding="utf-8")
    for versatz, status in ((0, "an Axel übergeben"),
                            (1, "an Frank übergeben")):
        text += FUND.format(
            nr=nr + versatz, status=status,
            test=f"{test_ordner}/test_hm{nr + versatz}_probe.py")
    beutebuch.write_text(text, encoding="utf-8", newline="\n")


def _projekt(tmp_path):
    """Ein Wegwerf-Projekt, in dem BEIDE Bahnen dieselbe Rolle fahren können."""
    repo = tmp_path / "repo"
    repo.mkdir()
    for name in ("team.config.sh", "team.config.ps1"):
        shutil.copy(WURZEL / name, repo / name)
    for rolle in ROLLEN:
        for endung in (".sh", ".ps1"):
            quelle = WURZEL / f"{rolle}{endung}"
            if quelle.is_file():
                shutil.copy(quelle, repo / f"{rolle}{endung}")
    kopiere_team_namensraum(repo / "team")

    beutebuch = _konfig("TEAM_BEUTEBUCH")
    for ordner in (_konfig("TEAM_PLAN_ORDNER"), _konfig("TEAM_TEST_ORDNER"),
                   _konfig("TEAM_PRODUKTIVCODE")):
        if ordner:
            (repo / ordner).mkdir(parents=True, exist_ok=True)
    shutil.copy(WURZEL / beutebuch, repo / beutebuch)
    (repo / _konfig("TEAM_PRODUKTIVCODE") / "app.py").write_text(
        "print('hallo')\n", encoding="utf-8", newline="\n")
    akten = _konfig("TEAM_ERMITTLUNGSAKTEN")
    if akten:
        (repo / akten).mkdir(parents=True, exist_ok=True)
    _funde_anlegen(repo, repo / beutebuch)

    for befehl in (["init", "-q"], ["config", "user.email", "t@localhost"],
                   ["config", "user.name", "Test"], ["add", "-A"],
                   ["commit", "-qm", "fixture"]):
        subprocess.run(["git", *befehl], cwd=repo, check=True,
                       capture_output=True)
    return repo


def _umgebung(repo, fang):
    u = dict(os.environ)
    # Der Fokus ist eine Umgebungsvariable ohne Verfallsdatum (BL-31) — steht
    # er beim Aufruf, wandert er in den Prompt und der Vergleich misst ihn mit.
    # Genommen wird die LEERE Lage, weil sie die ausgelieferte ist.
    for weg in ("TEAM_REDTEAM_FOCUS", "ANTHROPIC_API_KEY", "AUTH_MODE"):
        u.pop(weg, None)
    u["TEAM_PROMPT_FANG"] = str(fang)
    u["TEAM_AUTH_MODE"] = "abo"
    # Hauskonvention der Rollen-Tests: Die Sperre wird als bereits gehalten
    # gemeldet. Sie ist nicht der Gegenstand dieses Tests, und ohne die
    # Konvention legte jeder Lauf eine Sperre in der Wegwerf-Ablage an.
    #
    # Bis BL-190 stand hier ein zweiter Grund: Unter Git for Windows gibt es
    # kein `flock`, und `team_lock` brach dort mit "eine andere Pipeline laeuft
    # bereits" ab, bevor ein Prompt entstand. Das ist behoben — der Ersatzweg
    # sperrt ueber einen Ordner. Der Grund steht hier trotzdem, weil er erklaert,
    # warum die Konvention aelter ist als dieser Test.
    u["TEAM_LOCK_HELD"] = "1"
    return u


def _fahre(repo, rolle, bahn, tmp_path):
    """Fährt eine Rolle auf einer Bahn und gibt den gefangenen Prompt zurück."""
    fang = tmp_path / f"prompt-{rolle}-{bahn}.txt"
    if bahn == "bash":
        stub = tmp_path / "claude-stub.sh"
        stub.write_text(BASH_STUB.format(antwort=ANTWORT),
                        encoding="utf-8", newline="\n")
        stub.chmod(0o755)
        befehl = entrypoint_aufruf(repo / f"{rolle}.sh")
    else:
        stub = tmp_path / "claude-stub.ps1"
        stub.write_text(PWSH_STUB.format(antwort=ANTWORT),
                        encoding="utf-8-sig", newline="\n")
        befehl = ["pwsh", "-NoProfile", "-NonInteractive", "-File",
                  str(repo / f"{rolle}.ps1")]

    umgebung = _umgebung(repo, fang)
    umgebung["TEAM_CLAUDE_BIN"] = str(stub)
    r = subprocess.run(befehl, cwd=repo, env=umgebung, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=300)
    if not fang.is_file():
        pytest.fail(
            f"Die {bahn}-Bahn hat fuer '{rolle}' keinen Prompt abgesetzt "
            f"(Exit {r.returncode}). Ohne Prompt misst dieser Test nichts.\n"
            f"--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}")
    return fang.read_text(encoding="utf-8")


def _vergleichbar(text):
    """Prosa stehen lassen, Bahnunterschiede ausgleichen.

    Benutzt `kanon` aus `BL-112` mit **derselben** Ausnahmeliste. Die
    Platzhalter-Zusammenfassung dort greift hier nicht mehr — im gefangenen
    Prompt sind die Werte ja bereits eingesetzt —, die Ausnahmen aber schon,
    und die sind der Punkt.
    """
    return kanon(text.splitlines(), ausnahmen=AUSNAHMEN)


# --- Der Lauf-Vergleich ------------------------------------------------------

@pytest.mark.parametrize("rolle", ROLLEN)
def test_beide_bahnen_setzen_denselben_prompt_ab(rolle, tmp_path):
    """Die Zusicherung, die `BL-112` nicht geben konnte.

    Sie ist bewusst **zeichenweise**: Ein Prompt, der sich in einem Ordnernamen
    unterscheidet, steuert zwei verschiedene Agenten — auch wenn die Prosa
    dieselbe ist.
    """
    _verlange_installierte_ablage()
    ueberspringe_ohne_beide_bahnen()
    verlange_pwsh()
    repo = _projekt(tmp_path)
    links = _vergleichbar(_fahre(repo, rolle, "bash", tmp_path))
    rechts = _vergleichbar(_fahre(repo, rolle, "pwsh", tmp_path))
    if links == rechts:
        return
    import difflib
    diff = "\n".join(difflib.unified_diff(
        links, rechts, fromfile=f"{rolle}.sh", tofile=f"{rolle}.ps1",
        lineterm=""))
    pytest.fail(
        f"BL-117: Die beiden Bahnen setzen fuer '{rolle}' VERSCHIEDENE "
        "Prompts ab. Der Quelltext-Vergleich (BL-112) sieht das nicht — er "
        "vergleicht die Prosa, nachdem jede Einsetzung ein Platzhalter "
        "geworden ist.\n\nIst der Unterschied LEGITIM (jede Bahn nennt ihre "
        "eigene Datei), gehoert er mit Begruendung in AUSNAHMEN in "
        f"test_bl112_prompt_gleichstand.py.\n\n{diff}")


def test_der_stub_faengt_ueberhaupt_etwas(tmp_path):
    """Der Riegel gegen einen Test, der nichts misst.

    Fängt der Stub nichts, wäre der Vergleich zweier leerer Zeichenketten
    grün — die teuerste Bauform eines Tests, weil sie wie ein Nachweis
    aussieht. `_fahre` bricht deshalb ab, statt Leeres zurückzugeben; dieser
    Fall sichert zusätzlich, dass der Fang nicht nur existiert, sondern das
    Briefing wirklich enthält.
    """
    _verlange_installierte_ablage()
    ueberspringe_ohne_beide_bahnen()
    repo = _projekt(tmp_path)
    prompt = _fahre(repo, "harry", "bash", tmp_path)
    assert len(prompt) > 500, (
        f"Der gefangene Prompt ist nur {len(prompt)} Zeichen lang — das ist "
        "kein zusammengesetzter Rollen-Prompt.")
    assert "Beutebuch" in prompt or "beutebuch" in prompt, (
        "Im gefangenen Prompt steht kein Briefing-Text. Dann vergleicht "
        "dieser Test zwei Huellen.")

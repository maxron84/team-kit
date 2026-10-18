#!/usr/bin/env python3
"""BL-338: Der Abschlussbericht der Vollautomatik zitierte sich selbst als
„letzte 3 Zeilen" und nannte den eigenen Lauf „läuft gerade".

WAS GEMELDET WURDE (`Feld G`, 2026-10-17, Kaskaden 4 bis 6)
    Unter „Vollautomatik (letzte 3 Zeilen: …)" standen zwei Commit-Zeilen aus
    dem Bericht selbst und zuletzt dessen eigene Ueberschrift. Im selben
    Bericht stand „Pipeline: 🟢 läuft gerade (Lock gehalten)" — gemeint war
    der Lauf, der den Bericht schreibt; am Ende eines Laufs liest sich das wie
    ein haengender Prozess. Von Hand nach dem Lauf aufgerufen, zeigte
    `team-status` beides richtig.

DIE MECHANIK
    `vollautomatik.sh` leitet ihre ganze Ausgabe per `tee` ins Lauf-Log und
    ruft am Ende `team-status.sh`. Das nimmt das juengste Lauf-Log — das
    eigene, gerade wachsende — und zeigt dessen letzte drei Zeilen; die
    Pipeline-Zeile sieht die Sperre des Aufrufers. Auf der pwsh-Bahn dasselbe:
    `Rolle-Starten` haengt jede Zeile des Kindprozesses sofort ans Lauf-Log.
    Die Fixphase faehrt die Vollautomatik und erbt beides.

DER FIX (Wortlaut vom Owner)
    Haelt der Aufrufer die Sperre (`TEAM_LOCK_HELD=1`, exportiert vom
    Sperrinhaber), steht dort „🟢 dieser Lauf (Sperre gehalten vom
    Aufrufer)". Die Vollautomatik nennt `team-status` ihr eigenes Lauf-Log
    (`TEAM_LAUF_LOG`, nur fuer diesen einen Aufruf); ist es das juengste,
    entfaellt der Abschnitt. `TEAM_LOCK_HELD` allein reicht dafuer nicht: Die
    Halbautomatik setzt es auch, und in ihrem Status-Menue ist das juengste
    Log das eines frueheren Laufs — genau das, was man dort sehen will.

WARUM DIE BESTEHENDEN END-ZU-END-TESTS ES NICHT SAHEN
    `test_bl256` kopiert `team-status.sh` gar nicht mit, `test_bl217`,
    `test_bl241` und `test_bl210` setzen einen Stub dafuer ein. Hier laeuft
    der ECHTE Bericht hinter Stub-Rollen.

DIE GEGENPROBEN
    Ausserhalb eines Laufs, waehrend ein fremder Prozess die Sperre haelt:
    weiter „läuft gerade" und die drei Zeilen. Und der Fall der Halbautomatik:
    Sperre beim Aufrufer, aber kein eigenes Lauf-Log — „dieser Lauf" UND die
    drei Zeilen des frueheren Laufs.
"""
import os
import shutil
import subprocess

import pytest

from conftest import (BASH, entrypoint_pfad, kit_pfad, verlange_bash,
                      verlange_pwsh, werkzeug_wert)

ROLLEN = ("ralph", "harry", "marv", "frank", "axel")
WERKZEUGE = ("kosten.py", "beutebuch.py", "schreibzone.py")
BERICHT = "=== ABSCHLUSSBERICHT ==="
DIESER_LAUF = "🟢 dieser Lauf (Sperre gehalten vom Aufrufer)"
LAEUFT = "läuft gerade"
ABSCHNITT = "Vollautomatik (letzte 3 Zeilen"

# Ein frueherer Lauf: vier Zeilen, damit auffaellt, wenn mehr als drei kommen.
ALTES_LOG = "vollautomatik-20261017-171420.log"
ALTE_ZEILEN = ("[17:30:01] Phase 3: Marv fertig",
               "[17:31:02] Phase 4: Frank — nichts zu tun",
               "[17:31:03] Dieser Lauf: 1.2345 USD",
               "[17:31:04] Vollautomatik beendet.")


def _umgebung(**zusatz):
    """Die Sitzung, in der die Suite laeuft, bringt weder Sperre noch Lauf-Log
    mit — im Rollenlauf ist TEAM_LOCK_HELD=1 exportiert (Kit-BL-328)."""
    umgebung = {k: v for k, v in os.environ.items()
                if k not in ("TEAM_LOCK_HELD", "TEAM_LAUF_LOG",
                             "TEAM_VOLLAUTOMATIK_AB_PHASE")}
    umgebung["TEAM_BUDGET_USD"] = "99"
    umgebung.update(zusatz)
    return umgebung


def _git(repo, *befehl):
    subprocess.run(["git", "-C", str(repo), *befehl], check=True,
                   capture_output=True)


def _grundgeruest(repo):
    """Was beide Bahnen brauchen: Git, Ordner, die drei Werkzeuge des
    Berichts und ein Kaskadenzeiger."""
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@l")
    _git(repo, "config", "user.name", "T")
    (repo / "team" / "tools").mkdir(parents=True)
    for ordner in ("plans", ".ralph-logs", ".team-logs"):
        (repo / ordner).mkdir()
    for werkzeug in WERKZEUGE:
        shutil.copy(kit_pfad("tools", werkzeug),
                    repo / "team" / "tools" / werkzeug)
    (repo / ".ralph-plan").write_text("plans/ralph-kaskade-1-produkt.md\n",
                                      encoding="utf-8")
    (repo / ".ralph-state").write_text("5\n", encoding="utf-8")


def _einchecken(repo):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    return repo


def _altes_log(repo):
    (repo / ".team-logs" / ALTES_LOG).write_text(
        "\n".join(ALTE_ZEILEN) + "\n", encoding="utf-8", newline="\n")


def _bericht(ergebnis):
    ausgabe = ergebnis.stdout
    assert BERICHT in ausgabe, (
        f"Der Lauf kam nicht bis zum Abschlussbericht (Exit "
        f"{ergebnis.returncode}):\n{ausgabe[-3000:]}\n{ergebnis.stderr[-2000:]}")
    return ausgabe.split(BERICHT, 1)[1]


def _pruefe_bericht(bericht):
    assert DIESER_LAUF in bericht, (
        "Die Pipeline-Zeile des Abschlussberichts nennt den eigenen Lauf nicht "
        f"als solchen (Kit-BL-338):\n{bericht[:2500]}")
    assert LAEUFT not in bericht, (
        "Der Abschlussbericht meldet den eigenen Lauf als 'läuft gerade' — am "
        f"Ende eines Laufs liest sich das wie ein haengender Prozess "
        f"(Kit-BL-338):\n{bericht[:2500]}")
    assert ABSCHNITT not in bericht, (
        "Der Abschlussbericht zitiert sein eigenes, gerade wachsendes Lauf-Log "
        f"als 'letzte 3 Zeilen' (Kit-BL-338):\n{bericht[-2500:]}")


def _pruefe_alte_zeilen(ausgabe):
    assert f"{ABSCHNITT}: {ALTES_LOG})" in ausgabe, (
        f"Der Abschnitt des frueheren Laufs fehlt:\n{ausgabe[-2500:]}")
    for zeile in ALTE_ZEILEN[-3:]:
        assert zeile in ausgabe, f"{zeile!r} fehlt:\n{ausgabe[-2500:]}"
    assert ALTE_ZEILEN[0] not in ausgabe, ausgabe[-2500:]


# --- bash -------------------------------------------------------------------------

def _bash_projekt(tmp_path):
    """Minimalprojekt wie in test_bl217 — aber mit dem ECHTEN Bericht."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _grundgeruest(repo)
    shutil.copy(kit_pfad("lib.sh"), repo / "team" / "lib.sh")
    for name in ("vollautomatik.sh", "fixphase.sh", "team-status.sh"):
        shutil.copy(entrypoint_pfad(name), repo / name)
    # Die CLI, nach deren Version der Bericht fragt, gibt es hier nicht —
    # sonst riefe der Test eine echte `claude --version` (BL-264).
    (repo / "team.config.sh").write_text(
        'TEAM_KOSTEN_TOOL="' + werkzeug_wert("team/tools/kosten.py") + '"\n'
        'TEAM_BEUTEBUCH_TOOL="' + werkzeug_wert("team/tools/beutebuch.py") + '"\n'
        'TEAM_DOMAENEN="produkt"\nexport TEAM_DOMAENEN\n'
        'TEAM_PLAN_ORDNER="plans/"\nexport TEAM_PLAN_ORDNER\n'
        'TEAM_CLAUDE_BIN="claude-gibt-es-hier-nicht"\n',
        encoding="utf-8", newline="\n")
    for rolle in ROLLEN:
        code = 3 if rolle in ("harry", "marv", "frank") else 0
        pfad = repo / f"{rolle}.sh"
        pfad.write_text(f'#!/usr/bin/env bash\necho "STUB {rolle}"\nexit {code}\n',
                        encoding="utf-8", newline="\n")
        pfad.chmod(0o755)
    return _einchecken(repo)


def _bash(repo, *befehl, **zusatz):
    return subprocess.run([BASH, *befehl], cwd=repo, env=_umgebung(**zusatz),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=300)


@pytest.mark.parametrize("einstieg", ("vollautomatik.sh", "fixphase.sh"))
def test_bash_der_bericht_zitiert_sich_nicht(tmp_path, einstieg):
    """Der Feldfall, auf beiden Tueren zur Fixphase. Gegen den alten Stand rot
    (Triage: fuenf von fuenf Laeufen)."""
    verlange_bash()
    repo = _bash_projekt(tmp_path)
    ergebnis = _bash(repo, f"./{einstieg}")
    assert ergebnis.returncode == 0, ergebnis.stdout[-3000:] + ergebnis.stderr
    _pruefe_bericht(_bericht(ergebnis))


# Ein fremder Prozess haelt die Sperre ueber den Sperrordner (BL-190) — der
# Weg, den es auf jedem Wirt gibt, mit oder ohne flock. Seine Ausgabe geht
# nach /dev/null, sonst hielte er die Leitung des Tests offen.
BASH_FREMDE_SPERRE = "\n".join((
    "mkdir .team-loop.lock.d",
    "sleep 60 >/dev/null 2>&1 &",
    "halter=$!",
    'echo "$halter" > .team-loop.lock.d/pid',
    "./team-status.sh",
    "rc=$?",
    'kill "$halter" 2>/dev/null',
    "exit $rc",
))


def test_bash_gegenprobe_ausserhalb_eines_laufs(tmp_path):
    """Von Hand aufgerufen, waehrend ein fremder Lauf die Sperre haelt: Hier
    stimmt „läuft gerade", und die drei Zeilen sind die des juengsten Logs."""
    verlange_bash()
    repo = _bash_projekt(tmp_path)
    _altes_log(repo)
    ergebnis = _bash(repo, "-c", BASH_FREMDE_SPERRE)
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    assert f"🟢 {LAEUFT}" in ergebnis.stdout, ergebnis.stdout
    assert DIESER_LAUF not in ergebnis.stdout, ergebnis.stdout
    _pruefe_alte_zeilen(ergebnis.stdout)


def test_bash_im_status_menue_der_halbautomatik(tmp_path):
    """Die Halbautomatik haelt die Sperre und ruft den Bericht aus ihrem Menue
    (TEAM_LOCK_HELD=1, kein eigenes Lauf-Log): „dieser Lauf" — und der
    Abschnitt bleibt, denn das juengste Log ist das eines frueheren Laufs."""
    verlange_bash()
    repo = _bash_projekt(tmp_path)
    _altes_log(repo)
    ergebnis = _bash(repo, "./team-status.sh", TEAM_LOCK_HELD="1")
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    assert DIESER_LAUF in ergebnis.stdout, ergebnis.stdout
    assert LAEUFT not in ergebnis.stdout, ergebnis.stdout
    _pruefe_alte_zeilen(ergebnis.stdout)


# --- pwsh -------------------------------------------------------------------------

def _pwsh_projekt(tmp_path):
    """Dasselbe Projekt fuer die pwsh-Bahn (Bauart test_bl241), mit dem
    ECHTEN team-status.ps1."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _grundgeruest(repo)
    shutil.copy(kit_pfad("lib.psm1"), repo / "team" / "lib.psm1")
    for name in ("vollautomatik.ps1", "fixphase.ps1", "team-status.ps1"):
        shutil.copy(entrypoint_pfad(name), repo / name)
    # BL-113: PowerShell-Quelltext traegt ein BOM, auch als Fixture (BL-134).
    (repo / "team.config.ps1").write_text(
        '$TEAM_KOSTEN_TOOL = "' + werkzeug_wert("team/tools/kosten.py") + '"\n'
        '$TEAM_BEUTEBUCH_TOOL = "' + werkzeug_wert("team/tools/beutebuch.py") + '"\n'
        '$TEAM_DOMAENEN = "produkt"\n$env:TEAM_DOMAENEN = "produkt"\n'
        "$TEAM_PLAN_ORDNER = 'plans/'\n$env:TEAM_PLAN_ORDNER = 'plans/'\n"
        "$TEAM_CLAUDE_BIN = 'claude-gibt-es-hier-nicht'\n",
        encoding="utf-8-sig", newline="\n")
    for rolle in ROLLEN:
        code = 3 if rolle in ("harry", "marv", "frank") else 0
        (repo / f"{rolle}.ps1").write_text(
            f"[Console]::Out.WriteLine('STUB {rolle}')\nexit {code}\n",
            encoding="utf-8-sig", newline="\n")
    return _einchecken(repo)


def _pwsh(repo, skript, **zusatz):
    return subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-File",
                           f"./{skript}"], cwd=repo, env=_umgebung(**zusatz),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=300)


@pytest.mark.parametrize("einstieg", ("vollautomatik.ps1", "fixphase.ps1"))
def test_pwsh_der_bericht_zitiert_sich_nicht(tmp_path, einstieg):
    """Dasselbe auf der pwsh-Bahn. „läuft gerade" war dort sicher nur unter
    Windows rot (FileShare wird unter Linux nicht durchgesetzt); rot ist
    gegen den alten Stand auf jedem Wirt die fehlende Zeile „dieser Lauf" und
    der Abschnitt, den `Rolle-Starten` zeilenweise ins eigene Log schreibt."""
    verlange_pwsh()
    repo = _pwsh_projekt(tmp_path)
    ergebnis = _pwsh(repo, einstieg)
    assert ergebnis.returncode == 0, ergebnis.stdout[-3000:] + ergebnis.stderr
    _pruefe_bericht(_bericht(ergebnis))


def test_pwsh_das_eigene_log_bleibt_nicht_in_der_sitzung_stehen(tmp_path):
    """TEAM_LAUF_LOG gilt nur fuer den einen Aufruf des Berichts. Startet eine
    pwsh-Sitzung das Skript direkt — `fixphase.ps1` tut das mit `&` —, bliebe
    eine `$env:`-Variable sonst stehen, und der naechste Bericht von Hand
    liesse den Abschnitt des eben beendeten Laufs weg (die Falle aus
    Kit-BL-284)."""
    verlange_pwsh()
    repo = _pwsh_projekt(tmp_path)
    befehl = ("& ./vollautomatik.ps1 | Out-Null; "
              "[Console]::Out.WriteLine('NACHHER=[' + $env:TEAM_LAUF_LOG + ']')")
    ergebnis = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive",
                               "-Command", befehl], cwd=repo, env=_umgebung(),
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=300)
    assert BERICHT in ergebnis.stdout, ergebnis.stdout[-3000:] + ergebnis.stderr
    assert "NACHHER=[]" in ergebnis.stdout, (
        "TEAM_LAUF_LOG bleibt nach dem Lauf in der Sitzung stehen (Kit-BL-338):"
        f"\n{ergebnis.stdout[-1500:]}")


def _winpid_sperre(repo):
    """Eine fremde Sperre, die die pwsh-Bahn auswerten kann: der Sperrordner
    mit `winpid` eines lebenden Prozesses (BL-199) — hier der Testprozess."""
    ordner = repo / ".team-loop.lock.d"
    ordner.mkdir()
    (ordner / "winpid").write_text(f"{os.getpid()}\n", encoding="utf-8")


def test_pwsh_gegenprobe_ausserhalb_eines_laufs(tmp_path):
    verlange_pwsh()
    repo = _pwsh_projekt(tmp_path)
    _altes_log(repo)
    _winpid_sperre(repo)
    ergebnis = _pwsh(repo, "team-status.ps1")
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    assert f"🟢 {LAEUFT}" in ergebnis.stdout, ergebnis.stdout
    assert DIESER_LAUF not in ergebnis.stdout, ergebnis.stdout
    _pruefe_alte_zeilen(ergebnis.stdout)


def test_pwsh_im_status_menue_der_halbautomatik(tmp_path):
    verlange_pwsh()
    repo = _pwsh_projekt(tmp_path)
    _altes_log(repo)
    ergebnis = _pwsh(repo, "team-status.ps1", TEAM_LOCK_HELD="1")
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    assert DIESER_LAUF in ergebnis.stdout, ergebnis.stdout
    assert LAEUFT not in ergebnis.stdout, ergebnis.stdout
    _pruefe_alte_zeilen(ergebnis.stdout)

#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (Kit-Werkzeug, von beiden Bahnen aus aufrufbar)
"""Laesst eine Wegwerf-Installation ALTERN — fuer die Konfiguration
"Bestandsprojekt" des Selbsttests (Kit-BL-307).

WARUM
    Alle anderen Laeufe des Selbsttests fahren die Suite in einer FRISCHEN
    Installation. Dort ist jede Projektdatei die aktuelle Vorlage, es gibt
    keine Kaskade, kein Ledger, keinen Log. Zwei Gattungen von Fehlern sind
    damit nur im Feld zu finden, und beide trafen den ersten Update-Selbsttest
    eines Bestandsprojekts (`Feld F`, 2026-10-04):
      - Ein Werkzeug liest den Zustand des PROJEKTS, in dem der Test laeuft,
        statt seiner Fixture — der Kaskadenbeginn kam aus den Plandateien des
        Projekts, die Logs aus dem Wegwerf-Ordner des Tests (BL-226, BL-307).
      - Ein Test sucht eine neue Regel in einer Projektdatei, die das Update
        bewusst nicht anfasst (CLAUDE.md, Konfiguration).
    In einer Sandbox mit Vorgeschichte waren das 43 Faelle; in einer frischen
    Installation keiner.

WAS GEALTERT WIRD
    - Kaskaden 1..30 scharfgeschaltet: je eine Plandatei, eingecheckt mit einer
      Commit-Zeit in der Vergangenheit; `.ralph-plan` zeigt auf die letzte,
      `.ralph-state` steht mitten im Lauf.
    - Ein Ledger mit Historie, archivierte Logs im Fenster jeder gebuchten
      Kaskade, je ein offener Log der laufenden.
    - Die CLAUDE.md in der Fassung eines Projekts, das sie seit Monaten von
      Hand pflegt: nur der Kopf mit den Projekt-Spezifika.
    - Die Konfigurationen ohne jeden Wert, fuer den die Bibliothek einen
      Rueckfall hat (BL-200) — so sieht sie in einem Projekt aus, das vor
      diesen Werten installiert wurde.
    Ein Schritt, der nichts trifft, ist ein Fehler (Exit 1): Sonst liefe die
    Suite gegen eine frische Installation und waere gruen, ohne etwas geprueft
    zu haben.

NUTZUNG
    kit-projekt-altern.py                  prueft, ob die Annahmen noch tragen
    kit-projekt-altern.py <installierte-ablage> [--plan-ordner plans]
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

KASKADEN = 30
TAG = 86400
PRAEFIX = "ralph-kaskade-"
KOPF = "# datum | kaskade | usd | auth | domaene | rolle | notiz\n"
# Die Antworten des Installers und die Angabe ueber die Maschine bleiben
# stehen — sie hat jedes Projekt, egal wie alt.
BLEIBT = {"TEAM_SMOKE_TEST", "TEAM_PYTHON"}
CLAUDE_MD = ("# CLAUDE.md — {projekt}\n\n---\n\n## Projekt-Spezifika\n\n"
             "Ein Bestandsprojekt: Diese Datei entstand vor Monaten aus der "
             "Vorlage\nund wird seither von Hand gepflegt (Kit-BL-307).\n")


def _git(ziel, *args, zeit=None):
    umgebung = dict(os.environ)
    if zeit is not None:
        stempel = f"@{int(zeit)} +0000"
        umgebung.update(GIT_AUTHOR_DATE=stempel, GIT_COMMITTER_DATE=stempel)
    return subprocess.run(
        ["git", "-C", str(ziel), "-c", "user.email=bestand@team-kit.local",
         "-c", "user.name=Bestand", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=umgebung)


def _bibliotheks_rueckfaelle(ziel):
    """Die Werte, fuer die eine der Bibliotheken einen eigenen Default setzt
    (Vertrag Punkt 6 in conftest.py) — lesbar aus team/ der Ablage."""
    namen = set()
    for datei, muster in (("lib.sh", r'^([A-Z][A-Z0-9_]*)="\$\{\1:-'),
                          ("lib.psm1", r"^\$([A-Z][A-Z0-9_]*) = Team-Default '\1'")):
        pfad = ziel / "team" / datei
        if pfad.is_file():
            namen |= set(re.findall(muster, pfad.read_text(encoding="utf-8-sig"),
                                    flags=re.M))
    return namen - BLEIBT


def _konfiguration_altern(pfad, rueckfaelle):
    """Entfernt die Zeilen der Rueckfall-Werte — nur, wo der Name sonst nicht
    in der Datei vorkommt (ein abgeleiteter Wert verloere seine Quelle)."""
    roh = pfad.read_bytes()
    bom = roh.startswith(b"\xef\xbb\xbf")
    zeilen = roh.decode("utf-8-sig").splitlines(keepends=True)
    weg = []
    for name in sorted(rueckfaelle):
        treffer = [i for i, z in enumerate(zeilen)
                   if re.search(rf"\b{name}\b", z) and not z.lstrip().startswith("#")]
        if len(treffer) == 1 and re.match(rf"^\$?{name}\s*=", zeilen[treffer[0]]):
            weg.append(treffer[0])
    for i in sorted(weg, reverse=True):
        del zeilen[i]
    pfad.write_bytes((b"\xef\xbb\xbf" if bom else b"")
                     + "".join(zeilen).encode("utf-8"))
    return len(weg)


def altern(ziel, plan="plans"):
    fehler = []
    if _git(ziel, "rev-parse", "--is-inside-work-tree").returncode != 0:
        return [f"{ziel} ist kein Git-Arbeitsbaum — ohne Commit-Zeiten gibt es "
                f"keinen Kaskadenbeginn"]
    jetzt = time.time()

    def beginn(n):
        return jetzt - (KASKADEN + 11 - n) * TAG

    # --- Kaskadenverlauf ------------------------------------------------------
    (ziel / plan).mkdir(parents=True, exist_ok=True)
    for n in range(1, KASKADEN + 1):
        rel = f"{plan}/{PRAEFIX}{n}-bestand.md"
        (ziel / rel).write_text(f"# Kaskade {n}\n", encoding="utf-8")
        _git(ziel, "add", "--", rel)
        if _git(ziel, "commit", "-q", "-m", f"Kaskade {n} scharf", "--", rel,
                zeit=beginn(n)).returncode != 0:
            fehler.append(f"Plandatei der Kaskade {n} nicht eingecheckt")
            break
    (ziel / ".ralph-plan").write_text(f"{plan}/{PRAEFIX}{KASKADEN}-bestand.md\n",
                                      encoding="utf-8")
    (ziel / ".ralph-state").write_text("7\n", encoding="ascii")

    ledger = ziel / ".budget-ledger"
    text = ledger.read_text(encoding="utf-8") if ledger.is_file() else KOPF
    for n in range(1, KASKADEN):
        datum = time.strftime("%Y-%m-%d", time.gmtime(beginn(n)))
        text += "".join(f"{datum} | {n} | {usd:.4f} | abo | produkt | {rolle} | "
                        f"Bestand\n" for rolle, usd in
                        (("architekt", 2.5), ("ralph", 4.0), ("roles", 1.5)))
    ledger.write_text(text, encoding="utf-8")
    for ordner, rolle in ((".ralph-logs", "stufe"), (".team-logs", "harry")):
        archiv = ziel / ordner / "archiv"
        archiv.mkdir(parents=True, exist_ok=True)
        for n in range(1, KASKADEN):
            log = archiv / f"{rolle}-k{n}.json"
            log.write_text(json.dumps({"total_cost_usd": 1.25}), encoding="utf-8")
            os.utime(log, (beginn(n) + 3600,) * 2)
        offen = ziel / ordner / f"{rolle}-k{KASKADEN}.json"
        offen.write_text(json.dumps({"total_cost_usd": 1.25}), encoding="utf-8")
        os.utime(offen, (beginn(KASKADEN) + 3600,) * 2)

    # --- Projektdateien in aelterer Fassung -----------------------------------
    claude = ziel / "CLAUDE.md"
    if not claude.is_file():
        fehler.append("CLAUDE.md fehlt — die Ablage ist keine Installation")
    else:
        claude.write_text(CLAUDE_MD.format(projekt=ziel.name), encoding="utf-8")
    rueckfaelle = _bibliotheks_rueckfaelle(ziel)
    if not rueckfaelle:
        fehler.append("keine Bibliotheks-Rueckfaelle gefunden — team/lib.* "
                      "umgebaut? Dann altert die Konfiguration nicht mehr")
    for cfg in ("team.config.sh", "team.config.ps1"):
        pfad = ziel / cfg
        if pfad.is_file() and not _konfiguration_altern(pfad, rueckfaelle):
            fehler.append(f"{cfg}: kein Rueckfall-Wert entfernt")

    _git(ziel, "add", "-A")
    if _git(ziel, "commit", "-q", "-m", "chore: Bestandsprojekt (Kit-BL-307)",
            zeit=jetzt - TAG).returncode != 0:
        fehler.append("Endstand nicht eingecheckt")
    return fehler


def selbstpruefung():
    """Ohne Ziel: Tragen die Annahmen noch? Das Praefix muss eines sein, an dem
    kosten.py den Kaskadenbeginn erkennt, und beide Bibliotheken muessen
    Rueckfaelle in der erwarteten Schreibweise setzen."""
    kit = Path(__file__).resolve().parents[1]
    fehlt = []
    kosten = (kit / "geteilt" / "tools" / "kosten.py").read_text(encoding="utf-8")
    if f'"{PRAEFIX}"' not in kosten:
        fehlt.append(f"kosten.py: Plan-Praefix {PRAEFIX!r} unbekannt")
    for datei, muster in (("bash/lib.sh", r'^([A-Z][A-Z0-9_]*)="\$\{\1:-'),
                          ("pwsh/lib.psm1", r"^\$([A-Z][A-Z0-9_]*) = Team-Default '\1'")):
        if not re.search(muster, (kit / datei).read_text(encoding="utf-8-sig"),
                         flags=re.M):
            fehlt.append(f"{datei}: kein Rueckfall in der erwarteten Schreibweise")
    if fehlt:
        print("Diese Annahmen tragen nicht mehr — die Alterung im Selbsttest "
              "griffe ins Leere (Kit-BL-307):", file=sys.stderr)
        for f in fehlt:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("✓ Plan-Praefix und Bibliotheks-Rueckfaelle tragen die Alterung "
          "(Kit-BL-307).")
    return 0


def main(argv):
    if not argv:
        return selbstpruefung()
    ziel = Path(argv[0]).resolve()
    plan = "plans"
    if len(argv) >= 3 and argv[1] == "--plan-ordner":
        plan = argv[2].strip("/")
    fehler = altern(ziel, plan)
    if fehler:
        print("Die Alterung hat nicht gegriffen — dann prueft dieser Schritt "
              "nichts mehr (Kit-BL-307):", file=sys.stderr)
        for f in fehler:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"Gealtert: {KASKADEN} Kaskaden mit Vorgeschichte, Ledger und Logs, "
          f"CLAUDE.md von Hand gepflegt, Konfiguration ohne Rueckfall-Werte.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (Kit-Werkzeug, von beiden Bahnen aus aufrufbar)
"""Verdreht in einer Wegwerf-Installation die SPRACHMARKEN — fuer die dritte
Konfiguration des Selbsttests (Kit-BL-194).

WARUM
    Der Selbsttest faehrt die Suite zweimal: mit den Auslieferungswerten und
    mit angepassten Reglern (Caps, Praefixe, Domaenen). Beide Konfigurationen
    sind Python. Die ganze Gattung "eine Annahme des Kits, die stillschweigend
    Python heisst" war damit nur im Feld zu finden: `BL-171` (zwei
    Zusicherungen verdrahteten `.py` und `strict=True`) fiel erst in einem
    Dart-Projekt auf — als Sockel von sechs bis sieben dauerhaft roten
    Faellen, also dort, wo die Suite als Signal wertlos wird.

WAS VERDREHT WIRD
    Nur die Marken, nicht der Interpreter — die billige Bauform aus `BL-194`,
    und sie faengt die Gattung "Literal statt Konfigurationswert":
      - das Reproducer-Muster in CLAUDE.md und im Beutebuch:
        `test_hm<nr>_<stichwort>.py` -> `hm<nr>_<stichwort>_test.dart`
      - die strict-Schreibweise in CLAUDE.md: `strict=True` -> ein Satz in
        der Sprache eines Test-Pakets ohne strikte Erwartung
      - der Smoke-Befehl in beiden Konfigurationen: `dart test`
    Eine Ersetzung, die nichts trifft, ist ein Fehler (Exit 1): Sonst liefe
    die Suite gegen eine unveraenderte Installation und waere gruen, ohne
    etwas geprueft zu haben.

NUTZUNG
    kit-marken-verdrehen.py                  prueft die Vorlagen des Kits
    kit-marken-verdrehen.py <installierte-ablage> [--plan-ordner plans]
"""
import re
import sys
from pathlib import Path

# BL-133: Die Ausgabe ist UTF-8 — unabhaengig von der Locale des Wirts. Unter
# einem deutschen Windows schriebe Python sonst cp1252, und jeder Aufrufer im
# Kit liest UTF-8.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

MUSTER_ALT = "test_hm<nr>_<stichwort>.py"
MUSTER_NEU = "hm<nr>_<stichwort>_test.dart"
STRICT_ALT = "`strict=True`"
STRICT_NEU = ("`skip:` — das Test-Paket kennt keine strikte Erwartung, also "
              "wird kein roter Reproducer abgelegt")
SMOKE_NEU = "dart test"


def _ersetzen(pfad, alt, neu, fehler):
    text = pfad.read_text(encoding="utf-8-sig")
    if alt not in text:
        fehler.append(f"{pfad.name}: {alt!r} nicht gefunden")
        return
    roh = pfad.read_bytes()
    bom = roh.startswith(b"\xef\xbb\xbf")
    neu_text = text.replace(alt, neu)
    pfad.write_bytes((b"\xef\xbb\xbf" if bom else b"") + neu_text.encode("utf-8"))


def _smoke(pfad, muster, ersatz, fehler):
    text = pfad.read_text(encoding="utf-8-sig")
    neu, n = re.subn(muster, ersatz, text, count=1, flags=re.M)
    if not n:
        fehler.append(f"{pfad.name}: TEAM_SMOKE_TEST-Zeile nicht gefunden")
        return
    bom = pfad.read_bytes().startswith(b"\xef\xbb\xbf")
    pfad.write_bytes((b"\xef\xbb\xbf" if bom else b"") + neu.encode("utf-8"))


def vorlagen_pruefen(kit):
    """Ohne Ziel: Stehen die Marken, die verdreht werden sollen, noch in den
    Vorlagen des Kits? Wird eine davon umformuliert, faellt das hier auf —
    nicht erst, wenn der Selbsttest nach einer Viertelstunde abbricht."""
    fehlt = []
    for rel, marken in (("bootstrap/CLAUDE.md.vorlage", (MUSTER_ALT, STRICT_ALT)),
                        ("bootstrap/beutebuch.md", (MUSTER_ALT,))):
        text = (kit / rel).read_text(encoding="utf-8-sig")
        fehlt += [f"{rel}: {m!r}" for m in marken if m not in text]
    for rel, muster in (("bash/entry/team.config.sh", r"^TEAM_SMOKE_TEST="),
                        ("pwsh/entry/team.config.ps1", r"^\$TEAM_SMOKE_TEST\s*=")):
        if not re.search(muster, (kit / rel).read_text(encoding="utf-8-sig"),
                         flags=re.M):
            fehlt.append(f"{rel}: TEAM_SMOKE_TEST-Zeile")
    if fehlt:
        print("Diese Marken fehlen in den Vorlagen — die Verdrehung im "
              "Selbsttest griffe ins Leere (Kit-BL-194):", file=sys.stderr)
        for f in fehlt:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("✓ Alle verdrehbaren Marken stehen in den Vorlagen (Kit-BL-194).")
    return 0


def main(argv):
    if not argv:
        return vorlagen_pruefen(Path(__file__).resolve().parents[1])
    ziel = Path(argv[0])
    plan = "plans"
    if len(argv) >= 3 and argv[1] == "--plan-ordner":
        plan = argv[2].strip("/")
    fehler = []
    _ersetzen(ziel / "CLAUDE.md", MUSTER_ALT, MUSTER_NEU, fehler)
    _ersetzen(ziel / "CLAUDE.md", STRICT_ALT, STRICT_NEU, fehler)
    _ersetzen(ziel / plan / "beutebuch.md", MUSTER_ALT, MUSTER_NEU, fehler)
    _smoke(ziel / "team.config.sh", r'^TEAM_SMOKE_TEST=.*$',
           f'TEAM_SMOKE_TEST="${{TEAM_SMOKE_TEST:-{SMOKE_NEU}}}"', fehler)
    _smoke(ziel / "team.config.ps1", r"^\$TEAM_SMOKE_TEST\s*=.*$",
           f"$TEAM_SMOKE_TEST = Team-Wert 'TEAM_SMOKE_TEST' '{SMOKE_NEU}'",
           fehler)
    if fehler:
        print("Die Verdrehung hat nicht gegriffen — dann prueft dieser Schritt "
              "nichts mehr (Kit-BL-194):", file=sys.stderr)
        for f in fehler:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"Marken verdreht: {MUSTER_NEU}, keine strict-Schreibweise, "
          f"Smoke-Befehl '{SMOKE_NEU}' — in CLAUDE.md, Beutebuch und beiden "
          f"Konfigurationen.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

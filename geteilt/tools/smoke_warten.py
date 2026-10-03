#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteiltes Werkzeug, von beiden Bahnen aus aufrufbar)
"""smoke_warten.py — der Zwei-Schritt-Weg fuer eine Suite, die laenger laeuft
als die Hoechstfrist des Agenten-Werkzeugs (Kit-BL-273, Kit-BL-281).

DIE LAGE
    Die Vordergrund-Regel (Kit-BL-201) sagt: den Smoke-Test im VORDERGRUND
    fahren und das Zeitlimit des Werkzeugs auf TEAM_SMOKE_TEST_TIMEOUT stellen.
    Die Frist des Werkzeugs ist aber eine OBERGRENZE (im Feld 600 000 ms), und
    darueber schiebt das Werkzeug den Befehl SELBST in den Hintergrund — genau
    der vierte Ausgang, vor dem die Regel warnt. Gemessen: 417 bis 947 s auf
    praktisch demselben Stand, vier von sieben Laeufen ueber der Grenze.

    Der Ausweg, den ein Feld seit einem halben Jahr ohne vierten Ausgang
    faehrt, hat zwei Schritte — und der zweite ist der, an dem es im Feld
    trotzdem schiefging: Frank schob die WARTESCHLEIFE ebenfalls in den
    Hintergrund und wartete auf deren Benachrichtigung (2,01 USD fuer nichts).
    Nur der Testlauf gehoert in den Hintergrund; der Warteruf laeuft im
    Vordergrund, und sein Exit-Code wird gelesen.

AUFRUF
    smoke_warten.py start [--befehl CMD]
        Startet den Smoke-Test (Default: TEAM_SMOKE_TEST) abgekoppelt im
        Hintergrund. Ausgabe nach .team-logs/smoke-<id>.log, Exit-Code nach
        .team-logs/smoke-<id>.rc, sobald er fertig ist. Druckt die <id>.
    smoke_warten.py warten [--max SEK] [<id>]
        Wartet im VORDERGRUND bis zu SEK Sekunden (Default 540 — unter der
        ueblichen Werkzeugfrist von 600 s) auf das Ende des juengsten (oder
        des genannten) Laufs. Fertig: druckt das Ende der Ausgabe und endet
        mit dem Exit-Code des Smoke-Tests. Laeuft noch: endet mit 75 — dann
        `warten` erneut im Vordergrund aufrufen.

Exit 75 heisst immer "laeuft noch", nie "rot". 2 = Bedienfehler.
"""
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

ORDNER = Path(".team-logs")
LAEUFT_NOCH = 75


def _lauf(log, rc_datei, befehl):
    """Der abgekoppelte Teil: Befehl fahren, Exit-Code ablegen."""
    with open(log, "w", encoding="utf-8", errors="replace") as aus:
        try:
            ergebnis = subprocess.run(befehl, shell=True, stdout=aus,
                                      stderr=subprocess.STDOUT)
            code = ergebnis.returncode
        except OSError as exc:
            aus.write(f"\n[smoke_warten] Start gescheitert: {exc}\n")
            code = 127
    tmp = Path(str(rc_datei) + ".tmp")
    tmp.write_text(f"{code}\n", encoding="utf-8")
    os.replace(tmp, rc_datei)
    return 0


def start(befehl):
    if not befehl:
        print("Fehler: kein Smoke-Test bekannt (TEAM_SMOKE_TEST ist leer, "
              "--befehl fehlt).", file=sys.stderr)
        return 2
    ORDNER.mkdir(exist_ok=True)
    kennung = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    log = ORDNER / f"smoke-{kennung}.log"
    rc_datei = ORDNER / f"smoke-{kennung}.rc"
    argv = [sys.executable, os.path.abspath(__file__), "_lauf", str(log),
            str(rc_datei), befehl]
    optionen = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, close_fds=True)
    if os.name == "nt":
        optionen["creationflags"] = (subprocess.CREATE_NEW_PROCESS_GROUP
                                     | subprocess.DETACHED_PROCESS)
    else:
        optionen["start_new_session"] = True
    subprocess.Popen(argv, **optionen)
    print(kennung)
    print(f"[smoke_warten] Smoke-Test laeuft im Hintergrund: {befehl}",
          file=sys.stderr)
    print(f"[smoke_warten] Jetzt IM VORDERGRUND: smoke_warten.py warten "
          f"(so oft, bis es nicht mehr mit {LAEUFT_NOCH} endet).",
          file=sys.stderr)
    return 0


def _juengster():
    kandidaten = sorted(ORDNER.glob("smoke-*.log"))
    return kandidaten[-1].name[len("smoke-"):-len(".log")] if kandidaten else None


def warten(kennung, maximal):
    kennung = kennung or _juengster()
    if not kennung:
        print("Fehler: kein Smoke-Lauf gefunden — zuerst "
              "`smoke_warten.py start`.", file=sys.stderr)
        return 2
    log = ORDNER / f"smoke-{kennung}.log"
    rc_datei = ORDNER / f"smoke-{kennung}.rc"
    if not log.exists():
        print(f"Fehler: kein Lauf mit der Kennung {kennung}.", file=sys.stderr)
        return 2
    frist = time.monotonic() + maximal
    while not rc_datei.exists():
        if time.monotonic() >= frist:
            print(f"[smoke_warten] Laeuft noch ({kennung}) — `warten` erneut "
                  f"IM VORDERGRUND aufrufen (Exit {LAEUFT_NOCH} heisst nicht "
                  f"rot).", file=sys.stderr)
            return LAEUFT_NOCH
        time.sleep(1)
    code = int(rc_datei.read_text(encoding="utf-8").strip() or "1")
    zeilen = log.read_text(encoding="utf-8", errors="replace").splitlines()
    for z in zeilen[-40:]:
        print(z)
    print(f"[smoke_warten] Fertig: Exit {code} ({'gruen' if code == 0 else 'ROT'}).",
          file=sys.stderr)
    return code


def main(argv):
    if not argv or argv[0] in ("--hilfe", "--help", "-h"):
        print(__doc__)
        return 0 if argv else 2
    verb, rest = argv[0], argv[1:]
    if verb == "_lauf" and len(rest) == 3:
        return _lauf(*rest)
    if verb == "start":
        befehl = os.environ.get("TEAM_SMOKE_TEST", "")
        if "--befehl" in rest:
            stelle = rest.index("--befehl")
            befehl = rest[stelle + 1] if stelle + 1 < len(rest) else ""
        return start(befehl)
    if verb == "warten":
        maximal = 540.0
        if "--max" in rest:
            stelle = rest.index("--max")
            try:
                maximal = float(rest[stelle + 1])
            except (IndexError, ValueError):
                print("Fehler: --max braucht Sekunden", file=sys.stderr)
                return 2
            rest = rest[:stelle] + rest[stelle + 2:]
        return warten(rest[0] if rest else None, maximal)
    print(f"Fehler: unbekanntes Verb '{verb}' — start | warten", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Die Bahn-Kennung — jede Skriptdatei sagt in Zeile 1, wo sie hingehoert.

WARUM DIESER TEST EXISTIERT
    Das Kit faehrt seit der nativen Windows-Unterstuetzung auf zwei Bahnen: `bash`
    und `pwsh`. Die Trennung war bis hierher nur an der DATEIENDUNG
    abzulesen, und das reicht an drei Stellen nicht:

    1. `entry/` listet 29 Dateien alphabetisch verschraenkt — `axel.cmd`,
       `axel.ps1`, `axel.sh`, `frank.cmd`, … Wer den Ordner oeffnet, sieht
       keine zwei Bahnen, sondern einen Haufen.
    2. Die Namensgleichheit `ralph.sh` <-> `ralph.ps1` <-> `ralph.cmd` ist
       die Kopplung, auf der die Doppelbahn-Testbahn ruht (siehe
       `conftest.py`). Sie stand als Absichtserklaerung im Bauplan und
       wurde von nichts geprueft.
    3. Geteilter Code war von bahn-gebundenem Code nicht zu unterscheiden.
       `team/tools/kosten.py` ist BEWUSST nicht portiert — der
       pwsh-Bahn ist eine zweite Orchestrierung, kein zweiter
       Zustandscode. Diese Entscheidung stand in der Doku und in keiner
       Datei.

    Die Kopfzeile macht alle drei Punkte greppbar:

        # Bahn: bash  | Gegenstueck: ralph.ps1
        # Bahn: pwsh  | Gegenstueck: ralph.sh
        # Bahn: beide | Gegenstueck: keines (geteilter Zustandscode, …)

WARUM ASCII UND WARUM DIESE ZEICHEN
    Dieselbe Zeile steht in `.sh`, `.ps1`, `.psm1`, `.cmd` und `.py`. Eine
    Batch-Datei liest der Kommandozeileninterpreter in der OEM-Codepage der
    Maschine (850 oder 437, je nach Geraet) — ASCII ist das einzige, was
    dort ueberall dasselbe bedeutet (`BL-113`, `test_bl113_bom_regel.py`).
    Deshalb `|` statt Geviertstrich und `Gegenstueck` statt `Gegenstück`:
    EIN Suchmuster findet die Zeile in jeder Datei des Kits.

WARUM "keines" EINEN GRUND BRAUCHT
    Uebernommen von `@pytest.mark.nur_bash` in `conftest.py`: Wer eine
    Datei bewusst ohne Gegenstueck fuehrt, schreibt den Grund daneben. Eine
    fehlende Portierung und eine vergessene Portierung sehen sonst gleich
    aus — und die vergessene faellt erst auf der Zielmaschine auf.

WAS IM KIT ANDERS GEPRUEFT WIRD ALS IM PROJEKT
    Im KIT wird rekursiv gesucht: Jede neue `.sh`/`.ps1`/`.psm1`/`.cmd`
    muss die Zeile tragen, sonst ist die Zusicherung "vollstaendig
    klassifiziert" nach der ersten neuen Datei nur noch eine Behauptung.
    Im INSTALLIERTEN Projekt wird die Namensliste des Kits geprueft und
    sonst nichts — dort liegen fremde Skripte, virtuelle Umgebungen und
    der Code des Anwenders. Fuer die ist dieser Test nicht zustaendig
    (dieselbe Erwaegung wie in `test_bl113_bom_regel.py`).
"""
import re
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]

MUSTER = re.compile(
    r"^(?:#|rem) Bahn: (bash|pwsh|beide) \| Gegenstueck: (.+?)\s*$")

# Innerhalb der ersten drei Zeilen: hinter Shebang (.sh/.py) oder hinter
# `@echo off` (.cmd) ist Platz, davor steht in .ps1 nur das BOM.
KOPF_ZEILEN = 3

BAHN_JE_ENDUNG = {".sh": "bash", ".ps1": "pwsh", ".psm1": "pwsh",
                  ".cmd": "pwsh"}

# Was das Kit ausliefert — Basisnamen ohne Endung, Ablage-unabhaengig.
ENTRYPOINTS = ("ralph", "frank", "axel", "harry", "marv", "vollautomatik",
               "halbautomatik", "team-status", "team-test", "team.config")
KIT_INTERN = ("install", "kit-test", "kit-einrichten", "pruefe-windows",
              "team-init", "team-auth-setup", "lib", "redteam")

# Beide Ablagen: im Kit unter geteilt/, im installierten Projekt unter
# team/. Aufgeloest wird zur Laufzeit — eine leere Liste waere ein
# stiller Totalausfall und keine gruene Zusicherung.
GETEILT = ("tools/beutebuch.py", "tools/kosten.py", "tools/zitat_lint.py")
GETEILT_ABLAGEN = ("geteilt", "team")

AUSGENOMMEN = {".git", "__pycache__", ".pytest_cache", "node_modules",
               ".venv", "venv"}


def _ist_kit():
    """Kit-Repo oder installiertes Projekt? Beides traegt dieselben Tests."""
    return (WURZEL / "bash").is_dir() and (WURZEL / "pwsh").is_dir()


def _kit_dateien():
    for p in sorted(WURZEL.rglob("*")):
        if not p.is_file() or p.suffix not in BAHN_JE_ENDUNG:
            continue
        if AUSGENOMMEN & set(p.relative_to(WURZEL).parts):
            continue
        yield p


def _projekt_dateien():
    namen = set(ENTRYPOINTS) | set(KIT_INTERN)
    for muster in ("*.sh", "*.ps1", "*.cmd", "team/*.sh", "team/*.ps1",
                   "team/*.psm1"):
        for p in sorted(WURZEL.glob(muster)):
            if p.is_file() and p.name[:-len(p.suffix)] in namen:
                yield p


def _dateien():
    return list(_kit_dateien() if _ist_kit() else _projekt_dateien())


def _kennung(p):
    """(bahn, gegenstueck) aus dem Kopf — oder None, wenn keine Zeile da ist."""
    roh = p.read_bytes().lstrip(b"\xef\xbb\xbf").decode("utf-8", "replace")
    for zeile in roh.replace("\r\n", "\n").split("\n")[:KOPF_ZEILEN]:
        treffer = MUSTER.match(zeile)
        if treffer:
            return treffer.group(1), treffer.group(2)
    return None


def _rel(p):
    return p.relative_to(WURZEL).as_posix()


def _geteilte_dateien():
    """Die geteilten Werkzeuge in der Ablage, die gerade vorliegt."""
    for rel in GETEILT:
        for ablage in GETEILT_ABLAGEN:
            p = WURZEL / ablage / rel
            if p.is_file():
                yield p
                break


def _gegenstueck_pfad(p, name):
    """Wo das Gegenstueck liegt — die Ablage entscheidet, nicht der Name.

    Im installierten Projekt liegen beide Bahnen nebeneinander in der
    Wurzel, das Gegenstueck ist ein Geschwister. Im Kit liegt es im
    GESPIEGELTEN Bahn-Ordner: `bash/entry/ralph.sh` hat seines in
    `pwsh/entry/ralph.ps1`, `bash/lib.sh` seines in `pwsh/lib.psm1`.
    Gespiegelt wird nur das erste Pfadsegment — der Rest des Pfades ist
    in beiden Bahnen identisch, und genau das ist die Zusicherung.
    """
    kandidaten = [p.parent / name]
    teile = list(p.relative_to(WURZEL).parts)
    if teile and teile[0] in ("bash", "pwsh"):
        teile[0] = "pwsh" if teile[0] == "bash" else "bash"
        kandidaten.append(WURZEL.joinpath(*teile[:-1], name))
    for k in kandidaten:
        if k.is_file():
            return k
    return None


def test_jede_skriptdatei_traegt_eine_bahn_kennung():
    dateien = _dateien()
    assert dateien, "keine Skriptdateien gefunden — die Muster stimmen nicht mehr"
    ohne = [_rel(p) for p in dateien if _kennung(p) is None]
    assert not ohne, (
        "Ohne Bahn-Kennung ist die Zugehoerigkeit einer Datei nur an ihrer "
        "Endung abzulesen. Erwartet in einer der ersten "
        f"{KOPF_ZEILEN} Zeilen: `# Bahn: <bash|pwsh|beide> | Gegenstueck: "
        "<datei|keines (grund)>` — fehlt in: " + ", ".join(ohne))


def test_geteilte_werkzeuge_sind_als_geteilt_ausgewiesen():
    """Der Zustandscode liegt auf BEIDEN Bahnen in denselben Dateien.

    Ledger, Beutebuch und Kostenrechnung sind nicht portiert, und das ist
    ein Entscheid, kein Rest. Traegt eine dieser Dateien eines Tages
    `Bahn: bash`, hat jemand angefangen, sie als bash-eigen zu behandeln —
    der erste Schritt zu einem zweiten Zustandscode.
    """
    dateien = list(_geteilte_dateien())
    assert dateien, ("keines der geteilten Werkzeuge gefunden — die "
                     "Ablagen-Liste stimmt nicht mehr")
    for p in dateien:
        rel = _rel(p)
        kennung = _kennung(p)
        assert kennung is not None, f"{rel}: keine Bahn-Kennung"
        assert kennung[0] == "beide", (
            f"{rel} ist geteilter Zustandscode und muss `Bahn: beide` "
            f"tragen, steht aber auf `{kennung[0]}`")


def test_bahn_passt_zur_dateiendung():
    schlecht = []
    for p in _dateien():
        kennung = _kennung(p)
        if kennung and kennung[0] != BAHN_JE_ENDUNG[p.suffix]:
            schlecht.append(f"{_rel(p)} sagt {kennung[0]}, "
                            f"ist aber {BAHN_JE_ENDUNG[p.suffix]}")
    assert not schlecht, (
        "Eine Kennung, die der Endung widerspricht, ist schlimmer als keine: "
        + "; ".join(schlecht))


def test_gegenstueck_existiert_und_liegt_auf_der_anderen_bahn():
    """Die Namensgleichheit, auf der die Doppelbahn koppelt — geprueft.

    `.cmd` zeigt bewusst auf die `.sh` und nicht auf die gleichnamige
    `.ps1`: Die Batch-Datei ist ein Shim auf ihre `.ps1` (dieselbe Bahn),
    ihr Gegenstueck auf der ANDEREN Bahn ist die `.sh`.
    """
    schlecht = []
    for p in _dateien():
        kennung = _kennung(p)
        if kennung is None:
            continue
        bahn, gegenstueck = kennung
        if gegenstueck.startswith("keines"):
            continue
        ziel = _gegenstueck_pfad(p, gegenstueck)
        if ziel is None:
            schlecht.append(f"{_rel(p)} nennt `{gegenstueck}` — weder "
                            f"daneben noch in der Spiegel-Bahn zu finden")
            continue
        ziel_kennung = _kennung(ziel)
        if ziel_kennung and ziel_kennung[0] == bahn:
            schlecht.append(f"{_rel(p)} und ihr Gegenstueck `{gegenstueck}` "
                            f"stehen beide auf Bahn `{bahn}`")
    assert not schlecht, "; ".join(schlecht)


def test_gegenstueck_paare_sind_wechselseitig():
    """Wenn A auf B zeigt, zeigt B auf A — sonst ist ein Paar halb gepflegt.

    Gilt fuer `.sh` <-> `.ps1`/`.psm1`. `.cmd` ist ausgenommen: Die Batch-
    Datei zeigt auf dieselbe `.sh` wie ihre `.ps1`, und die `.sh` kann
    nicht auf zwei Dateien zeigen.
    """
    schlecht = []
    for p in _dateien():
        if p.suffix == ".cmd":
            continue
        kennung = _kennung(p)
        if kennung is None or kennung[1].startswith("keines"):
            continue
        ziel = _gegenstueck_pfad(p, kennung[1])
        if ziel is None:
            continue  # bereits vom Nachbartest gemeldet
        zurueck = _kennung(ziel)
        if zurueck and zurueck[1] != p.name:
            schlecht.append(f"{_rel(p)} -> {kennung[1]}, aber {kennung[1]} "
                            f"-> {zurueck[1]}")
    assert not schlecht, (
        "Halb gepflegte Paare: " + "; ".join(schlecht))


def test_fehlendes_gegenstueck_traegt_einen_grund():
    """`keines` ohne Begruendung sieht aus wie eine vergessene Portierung."""
    schlecht = []
    for p in _dateien():
        kennung = _kennung(p)
        if kennung is None or not kennung[1].startswith("keines"):
            continue
        if not re.match(r"^keines \(.+\)$", kennung[1]):
            schlecht.append(_rel(p))
    assert not schlecht, (
        "Ein fehlendes Gegenstueck ist entweder ein Entscheid oder ein Rest. "
        "Welches von beidem, gehoert in die Klammer — genau wie der Grund in "
        "`@pytest.mark.nur_bash`: " + ", ".join(schlecht))


def test_die_kennung_ist_reines_ascii():
    """Sonst bedeutet sie in einer `.cmd` je nach Codepage etwas anderes."""
    schlecht = []
    for p in _dateien():
        roh = p.read_bytes().lstrip(b"\xef\xbb\xbf").decode("utf-8", "replace")
        for zeile in roh.replace("\r\n", "\n").split("\n")[:KOPF_ZEILEN]:
            if MUSTER.match(zeile) and not zeile.isascii():
                schlecht.append(_rel(p))
    assert not schlecht, (
        "Nicht-ASCII in der Bahn-Kennung: " + ", ".join(schlecht))


def test_beide_bahnen_sind_besetzt():
    """Eine Gegenprobe gegen den stillen Totalausfall der Muster.

    Faende `_dateien()` eines Tages nur noch eine Bahn — weil ein Ordner
    umgezogen ist, ein Muster nicht mehr passt oder die Endungstabelle
    veraltet —, waeren alle Tests oben gruen und die Zusicherung leer.
    """
    bahnen = {k[0] for k in (_kennung(p) for p in _dateien()) if k}
    assert {"bash", "pwsh"} <= bahnen, (
        f"nur diese Bahnen gefunden: {sorted(bahnen) or 'keine'}")

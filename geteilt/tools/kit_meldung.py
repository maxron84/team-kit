#!/usr/bin/env python3
# Bahn: beide | Gegenstueck: keines (geteilter Zustandscode, bewusst nicht portiert)
"""Rückkanal Feld → Kit: einen Fund am T.E.A.M. selbst ans Kit melden.

WARUM ES DIESES WERKZEUG GIBT
    Der Rückkanal war bis einschließlich 2.12.0 reine Konvention. Drei Stellen
    sagten, wohin ein Kit-Fund gehört (die Backlog-Vorlage, das Briefing des
    Architekten, der Statuswert „ans Kit gemeldet"), und
    `plans/roadmap-skizzen.md` hielt
    ausdrücklich fest, warum es dafür kein Werkzeug gab: „Bei einem Menschen
    und zwei Repos wäre jede Automatisierung teurer als das Problem. Das ändert
    sich ab dem dritten Feldprojekt — dann neu bewerten." Mit `Feld D` ist der
    Auslöser gefallen.

    Zwei Dinge haben die Konvention getragen, die es nicht mehr gibt:

    1. DER PFAD WAR FEST VERDRAHTET. Die Anweisung nannte `~/Source/team-kit` —
       die Ablage EINER Maschine. Wer woandershin geklont hat, bekam eine
       Anweisung, die ins Leere zeigt; ein fremder Nutzer ohnehin. Seit BL-153
       steht der Pfad in `team.config.*`, und dieses Werkzeug sucht zusätzlich
       die üblichen Orte ab.
    2. EINE MELDUNG IM FELD HAT EINE VERFALLSZEIT. Sie endet beim nächsten
       `--update`. Das ist keine Theorie: `BL-42` wurde im Feld gefunden,
       lokal gefixt, blieb im Kit-Backlog liegen — und das Update vom
       2026-08-14 hat den Feldfix überschrieben, worauf dasselbe Projekt
       denselben Fund ein zweites Mal melden musste (`BL-58`). Deshalb legt
       dieses Werkzeug die Meldung IMMER als Datei ab, auch wenn das Kit
       gerade nicht erreichbar ist. Verloren geht nichts.

WARUM DER LOOP SCHREIBT, ABER DER MENSCH SENDET
    Dieselbe Trennung wie „Finder ≠ Fixer", angewandt auf den Rückkanal:
    `neu` und `pruefen` laufen automatisch — eine Rolle darf einen Fund
    erkennen, ausformulieren und ablegen. `senden` nicht.

    Ein Pull Request ist eine nach außen wirkende Handlung, die sich nicht
    zurückholen lässt, und die Meldung schreibt eine Rolle, die gerade eine
    FREMDE, private Codebasis gelesen hat. Pfade, Hostnamen, Projektnamen und
    Schnipsel wandern sonst ungefiltert in ein öffentliches Repo. Das Kit
    anonymisiert seine eigenen Feldprojekte nicht ohne Grund hinter `Feld A`…
    `Feld D`; dieselbe Disziplin wird hier erzwungen statt empfohlen —
    `senden` prüft vorher und verlangt eine Bestätigung.

AUFRUFE
  kit_meldung.py neu --titel "…" [--nummer BL-153] [--art fehler|luecke|idee]
                                 → legt einen Meldungsentwurf nach Vorlage an
                                   und gibt seinen Pfad aus
  kit_meldung.py pruefen [DATEI …]
                                 → Redaktionsprüfung: absolute Pfade, Benutzer-
                                   und Rechnernamen, E-Mail, schlüsselartige
                                   Zeichenketten, der eigene Projektname und
                                   offene TODO-Marken der Vorlage.
                                   Exit 4 = Befunde (auf stderr), Exit 0 = sauber
  kit_meldung.py senden DATEI [--ja] [--repo user/repo]
                                 → Pull Request gegen das Kit-Repo, über `gh`.
                                   Ohne `gh`: druckt einen vorbefüllten
                                   Issue-Link, die Datei bleibt liegen
  kit_meldung.py issue-link DATEI [--repo user/repo]
                                 → nur den Link, ohne etwas zu senden
  kit_meldung.py kit-pfad        → wo dieses Werkzeug das Kit vermutet, und
                                   woher es den Pfad hat (Diagnose)

GLOBALE FLAGS (vor allem für Fixture-Tests)
  --projektwurzel ORDNER   statt der aus der Lage dieser Datei abgeleiteten
  --meldungen ORDNER       Ablage der Entwürfe statt <plan-ordner>/kit-meldungen
  --kit ORDNER             das Kit-Repo statt der Suchkaskade
  --projekt NAME           Projektname für die Redaktionsprüfung
"""
import argparse
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import date
from pathlib import Path

# BL-133: Die AUSGABE dieses Werkzeugs ist UTF-8 — unabhaengig von der Locale
# des Wirts. Ausfuehrliche Begruendung in beutebuch.py; sie gilt hier woertlich,
# und ein Werkzeug, das Prosa mit Umlauten ausgibt, ist der Fall, fuer den sie
# geschrieben wurde.
for _strom in (sys.stdout, sys.stderr):
    try:
        _strom.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass

# Diese Datei liegt in team/tools/ — zwei Ebenen unter der Projektwurzel.
# Dieselbe Herleitung wie in beutebuch.py, und aus demselben Grund: ein .parent
# zu wenig ergibt einen Pfad, den es nie gibt, und das Werkzeug meldet still
# "nichts gefunden" (BL-1).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

KIT_REPO_DEFAULT = "maxron84/team-kit"

# Woran ein Kit-Repo erkennbar ist. Zwei Marken, nicht eine: Ein Ordner, der
# zufaellig `plans/backlog.md` traegt, ist ein x-beliebiges Projekt mit
# T.E.A.M.-Installation — genau das, wovon dieses Werkzeug wegzeigt.
KIT_MARKEN = ("bootstrap/CLAUDE.md.vorlage", "geteilt/tools/kosten.py")

VORLAGE = """# {titel}

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      {ruf}kit-melden{endung} pruefen  {dateiname}
      {ruf}kit-melden{endung} senden   {dateiname}

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: {art}
- **Kit-Version**: {version}
- **Bahn**: {bahn}
- **Plattform**: {plattform}
- **Lage des Projekts**: TODO — z. B. „Greenfield, Linux, bash-Bahn, Python"

## Was passiert ist

TODO — der Hergang. Was wurde aufgerufen, was war zu erwarten, was kam
stattdessen? Wörtliche Fehlermeldungen sind Gold wert; bitte gekürzt auf die
Zeilen, die zur Sache gehören.

## Wo es steckt

TODO — welche Datei des Kits, welche Funktion, welche Regel. Wenn du es weißt:
`team/lib.sh`, `bash/entry/ralph.sh`, eine Regel aus `CLAUDE.md`. Wenn nicht,
reicht der Hergang oben.

## Warum das jede Installation trifft

TODO — der Satz, der diese Meldung vom Projektbug trennt. Steckt der Fehler in
`team/`, in einem Entrypoint oder in einer Regel aus `CLAUDE.md`/`TEAM.md`,
dann trifft er jede weitere Installation, und dieses Projekt repariert ihn bei
jedem Update aufs Neue.

## Was ich schon versucht habe

TODO — auch Fehlschläge sind Information. Wenn du im Projekt schon lokal
gefixt hast: bitte den Fix beschreiben (er hat eine Verfallszeit — sie endet
beim nächsten `--update`, siehe `BL-42`/`BL-58`).
"""


# --- Kit finden ---------------------------------------------------------------


def _ist_kit(p):
    return p.is_dir() and all((p / m).exists() for m in KIT_MARKEN)


def kit_finden(explizit=None):
    """Wo liegt das Kit? Gibt (Pfad|None, Herkunft) zurueck.

    Die Kaskade ist dieselbe wie in `scripts/team-init.sh`. Zwei Sorten
    Vorgabe werden dabei UNTERSCHIEDLICH behandelt, und der Unterschied ist
    Absicht:

      `--kit` ist getippte Absicht. Zeigt der Pfad nicht auf ein Kit, ist das
      ein Bedienfehler — und still woanders weiterzusuchen waere die
      schlimmste Antwort darauf: Das Werkzeug arbeitete dann gegen ein Kit,
      das der Aufrufer nie gemeint hat, und sagte es ihm nicht.

      `TEAM_KIT_PFAD` steht in einer Konfiguration, die ein Update bewusst
      nicht anfasst. Sie darf veralten (das Kit wurde verschoben), und dann
      ist Weitersuchen genau richtig — mit Ansage, damit der Wert irgendwann
      korrigiert wird.
    """
    if explizit:
        p = Path(explizit).expanduser()
        if _ist_kit(p):
            return p, "--kit"
        return None, f"--kit zeigt nicht auf ein Kit: {p}"

    kandidaten = []
    aus_umgebung = os.environ.get("TEAM_KIT_PFAD")
    if aus_umgebung:
        p = Path(aus_umgebung).expanduser()
        if _ist_kit(p):
            return p, "$TEAM_KIT_PFAD"
        print(f"Hinweis: TEAM_KIT_PFAD zeigt auf {p}, dort liegt kein Kit — "
              f"es wird weitergesucht. Bitte den Wert in team.config.* "
              f"nachziehen.", file=sys.stderr)
    heim = Path.home()
    kandidaten += [
        (heim / "Source" / "team-kit", "übliche Ablage ~/Source/team-kit"),
        (heim / "source" / "team-kit", "übliche Ablage ~/source/team-kit"),
        (heim / "team-kit", "übliche Ablage ~/team-kit"),
    ]
    for pfad, woher in kandidaten:
        if _ist_kit(pfad):
            return pfad, woher
    return None, "weder TEAM_KIT_PFAD noch die üblichen Ablagen"


def kit_repo_ermitteln(kit, vorgabe=None):
    """Gegen welches GitHub-Repo geht die Meldung?

    Bevorzugt das `origin` des lokal liegenden Kits — wer einen Fork geklont
    hat, meldet sonst gegen ein Repo, mit dem seine Installation nichts zu tun
    hat. Faellt zurueck auf die Vorgabe bzw. das Original.
    """
    if vorgabe:
        return vorgabe
    if kit:
        url = _git(kit, "remote", "get-url", "origin")
        if url:
            m = re.search(r"[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?$", url.strip())
            if m:
                return m.group(1)
    return KIT_REPO_DEFAULT


def _git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", str(cwd)] + list(args),
                           capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return ""
    return r.stdout if r.returncode == 0 else ""


# --- Redaktionspruefung -------------------------------------------------------

# Jede Regel sagt, WAS sie sucht und WARUM das in einem oeffentlichen Repo
# nichts verloren hat. Eine Regel ohne Begruendung wird beim ersten Fehlalarm
# geloescht statt verstanden.
BEFUNDE = [
    (re.compile(r"(?<![\w~])/(?:home|Users|root)/[\w.-]+"),
     "absoluter Pfad ins Benutzerverzeichnis — verrät den Kontonamen"),
    (re.compile(r"[A-Za-z]:\\+Users\\+[\w.-]+", re.I),
     "absoluter Windows-Pfad — verrät den Kontonamen"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"),
     "E-Mail-Adresse"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
     "sieht aus wie ein API-Schlüssel"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}\b"),
     "sieht aus wie ein GitHub-Token"),
    (re.compile(r"\bhttps?://(?!github\.com|docs\.|www\.)[\w.-]*"
                r"(?:intern|internal|local|corp|lan)\b[\w./-]*", re.I),
     "interne URL"),
    (re.compile(r"\bTODO\b"),
     "unausgefüllte Stelle der Vorlage — bitte ergänzen oder Abschnitt löschen"),
]


def redaktion_pruefen(text, projekt=None, rechner=None, benutzer=None):
    """Liefert eine Liste (zeilennr, zeile, grund).

    Bewusst zeilenweise und mit der Fundstelle im Klartext: Ein Lint, der nur
    "3 Befunde" meldet, wird abgeschaltet statt befolgt.
    """
    regeln = list(BEFUNDE)
    # Die drei dynamischen Regeln stehen nicht in der Liste oben, weil sie von
    # der Maschine abhaengen, auf der geprueft wird — und weil ein leerer Wert
    # sonst zu einem Regex wuerde, der auf JEDE Zeile passt.
    if projekt and len(projekt) >= 3:
        regeln.append((re.compile(re.escape(projekt), re.I),
                       "Name deines Projekts — das Kit führt Feldbelege unter "
                       "`Feld A`…`Feld D`, nicht unter Namen"))
    if rechner and len(rechner) >= 4:
        regeln.append((re.compile(re.escape(rechner), re.I),
                       "Name deines Rechners"))
    if benutzer and len(benutzer) >= 3:
        regeln.append((re.compile(rf"\b{re.escape(benutzer)}\b", re.I),
                       "dein Kontoname"))

    funde = []
    for nr, zeile in enumerate(text.splitlines(), 1):
        # ALLE zutreffenden Regeln je Zeile, nicht die erste. Mit einem `break`
        # verdeckt der auffaelligste Befund die leiseren: In der Zeile
        # "… Token ghp_… Das Projekt geheimprojekt lief …" meldet die
        # Schluesselregel zuerst, und der Projektname faellt erst im zweiten
        # Durchgang auf. Eine Pruefung, die man dreimal fahren muss, um alles
        # zu sehen, erzieht dazu, nach dem ersten Mal zu senden.
        gruende = [g for rx, g in regeln if rx.search(zeile)]
        if gruende:
            funde.append((nr, zeile.strip(), " · ".join(gruende)))
    return funde


# --- Verben -------------------------------------------------------------------


def _slug(titel):
    s = titel.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:60] or "meldung").rstrip("-")


def _meldungsordner(a):
    if a.meldungen:
        return Path(a.meldungen)
    plan = os.environ.get("TEAM_PLAN_ORDNER", "plans").rstrip("/")
    return Path(a.projektwurzel or REPO_ROOT) / plan / "kit-meldungen"


def _kit_version(kit):
    """Die Version, gegen die gemeldet wird — aus dem CHANGELOG des Kits.

    Ohne sie ist jede Meldung eine Zeitreise: Der Empfaenger weiss nicht, ob
    der Fund einen Fehler beschreibt, den er letzte Woche behoben hat.
    """
    if not kit:
        return "unbekannt (Kit nicht gefunden)"
    ch = kit / "CHANGELOG.md"
    if not ch.exists():
        return "unbekannt"
    for zeile in ch.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+\[(\d+\.\d+\.\d+)\]", zeile)
        if m:
            return m.group(1)
    return "unveröffentlicht (Unreleased)"


def verb_neu(a):
    kit, _ = kit_finden(a.kit)
    ordner = _meldungsordner(a)
    ordner.mkdir(parents=True, exist_ok=True)
    name = f"{date.today().isoformat()}-{_slug(a.titel)}.md"
    ziel = ordner / name
    if ziel.exists():
        print(f"Es gibt schon einen Entwurf: {ziel}", file=sys.stderr)
        return 1

    bahn = "pwsh" if os.name == "nt" else "bash"
    ruf = ".\\" if bahn == "pwsh" else "./"
    endung = ".cmd" if bahn == "pwsh" else ".sh"
    text = VORLAGE.format(
        titel=a.titel,
        art={"fehler": "Fehler am Kit", "luecke": "Lücke in der Doku",
             "idee": "Idee / Verbesserung"}.get(a.art, a.art),
        version=_kit_version(kit),
        bahn=bahn,
        plattform=sys.platform,
        dateiname=name,
        ruf=ruf,
        endung=endung,
    )
    if a.nummer:
        text = text.replace("- **Art**:", f"- **Bezug**: {a.nummer}\n- **Art**:", 1)
    # BL-137: newline="" — kein Textmodus, der unter Windows jedes \n uebersetzt.
    with ziel.open("w", newline="", encoding="utf-8") as fh:
        fh.write(text)
    print(ziel)
    return 0


def verb_pruefen(a):
    dateien = [Path(d) for d in a.dateien] or sorted(_meldungsordner(a).glob("*.md"))
    if not dateien:
        print("Keine Meldung zu prüfen.", file=sys.stderr)
        return 3
    projekt = a.projekt or os.environ.get("TEAM_PROJEKT")
    try:
        import socket
        rechner = socket.gethostname()
    except Exception:
        rechner = None
    benutzer = os.environ.get("USER") or os.environ.get("USERNAME")

    gesamt = 0
    for d in dateien:
        if not d.exists():
            print(f"  ✗ {d} gibt es nicht.", file=sys.stderr)
            gesamt += 1
            continue
        funde = redaktion_pruefen(d.read_text(encoding="utf-8"),
                                  projekt, rechner, benutzer)
        for nr, zeile, grund in funde:
            kurz = zeile if len(zeile) <= 90 else zeile[:87] + "…"
            print(f"  ✗ {d.name}:{nr} — {grund}\n      {kurz}", file=sys.stderr)
        gesamt += len(funde)
    if gesamt:
        print(f"\n{gesamt} Stelle(n) vor dem Senden ansehen. Das ist kein "
              f"Urteil, sondern eine Vorlage zum Gegenlesen.", file=sys.stderr)
        return 4
    print("✓ Redaktion: nichts gefunden, was ins Projekt zurückzeigt.")
    return 0


def _gh_bereit():
    try:
        r = subprocess.run(["gh", "auth", "status"],
                           capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return False, "`gh` ist nicht installiert."
    if r.returncode != 0:
        return False, "`gh` ist da, aber nicht angemeldet — `gh auth login`."
    return True, ""


def _issue_link(repo, datei):
    text = datei.read_text(encoding="utf-8")
    titel = text.splitlines()[0].lstrip("# ").strip() or datei.stem
    # GitHub nimmt lange Query-Strings entgegen, aber nicht beliebig lange:
    # jenseits von rund 8 kB antworten Server mit 414. Gekuerzt wird mit
    # ANSAGE, damit niemand eine halbe Meldung fuer die ganze haelt.
    rumpf = text
    grenze = 6000
    if len(rumpf) > grenze:
        rumpf = (rumpf[:grenze]
                 + "\n\n*(hier gekürzt — die vollständige Meldung liegt als "
                   "Datei im meldenden Projekt)*")
    q = urllib.parse.urlencode({"title": titel, "body": rumpf})
    return f"https://github.com/{repo}/issues/new?{q}"


def verb_issue_link(a):
    datei = Path(a.datei)
    if not datei.exists():
        print(f"{datei} gibt es nicht.", file=sys.stderr)
        return 1
    kit, _ = kit_finden(a.kit)
    print(_issue_link(kit_repo_ermitteln(kit, a.repo), datei))
    return 0


def verb_senden(a):
    datei = Path(a.datei)
    if not datei.exists():
        print(f"{datei} gibt es nicht.", file=sys.stderr)
        return 1

    # Die Redaktionspruefung ist KEINE Empfehlung: Was hier durchgeht, ist
    # gleich oeffentlich. Uebersteuern geht, aber nur ausdruecklich.
    a.dateien = [str(datei)]
    if verb_pruefen(a) == 4 and not a.trotzdem:
        print("\nAbgebrochen. Nach dem Nachbessern erneut, oder --trotzdem, "
              "wenn die Befunde bewusst so stehen bleiben.", file=sys.stderr)
        return 4

    kit, woher = kit_finden(a.kit)
    repo = kit_repo_ermitteln(kit, a.repo)
    bereit, grund = _gh_bereit()
    if not bereit:
        print(f"{grund}\n\nOhne `gh` geht der kurze Weg über ein Issue — der "
              f"Link ist vorbefüllt, ein GitHub-Konto im Browser genügt:\n",
              file=sys.stderr)
        print(_issue_link(repo, datei))
        print(f"\nDie Meldung bleibt als Datei liegen: {datei}", file=sys.stderr)
        return 3

    zweig = f"meldung/{datei.stem}"
    zielname = f"plans/meldungen/{datei.name}"
    print(f"Kit-Repo:  {repo}")
    print(f"Datei:     {zielname}")
    print(f"Zweig:     {zweig}")
    print(f"Kit lokal: {kit or '— nicht gefunden —'} ({woher})")
    if not a.ja:
        if not sys.stdin.isatty():
            print("\nNicht bestätigt und kein Terminal da. Ein Pull Request "
                  "ist nach außen wirksam und wird nicht ungefragt gesendet — "
                  "erneut mit --ja aufrufen.", file=sys.stderr)
            return 1
        if input("\nPull Request jetzt anlegen? [j/N] ").strip().lower() \
                not in ("j", "ja", "y", "yes"):
            print("Nichts gesendet.", file=sys.stderr)
            return 3

    return _pr_anlegen(repo, zweig, zielname, datei)


def _pr_anlegen(repo, zweig, zielname, datei):
    import shutil
    import tempfile

    def lauf(*args, **kw):
        r = subprocess.run(list(args), capture_output=True, text=True,
                           encoding="utf-8", **kw)
        if r.returncode != 0:
            print(f"  ✗ {' '.join(args[:3])} …\n{r.stderr.strip()}",
                  file=sys.stderr)
        return r

    r = lauf("gh", "api", "user", "--jq", ".login")
    if r.returncode != 0:
        return 1
    konto = r.stdout.strip()

    # Wer das Repo selbst besitzt, braucht keinen Fork — und bekaeme auch
    # keinen: `gh repo fork` auf das eigene Repo schlaegt fehl. Das ist kein
    # Randfall, sondern der Normalfall fuer den Maintainer, dessen eigene
    # Feldprojekte denselben Weg gehen sollen wie die fremden.
    if konto == repo.split("/")[0]:
        quelle, kopf = repo, zweig
    else:
        # Ein Fork ist idempotent: Gibt es ihn schon, sagt gh das und endet
        # mit 0.
        if lauf("gh", "repo", "fork", repo, "--clone=false").returncode != 0:
            print("Fork fehlgeschlagen — ohne ihn geht kein PR von außen.",
                  file=sys.stderr)
            return 1
        quelle, kopf = f"{konto}/{repo.split('/')[-1]}", f"{konto}:{zweig}"

    tmp = Path(tempfile.mkdtemp(prefix="team-kit-meldung-"))
    try:
        # --depth 1: Geklont wird, um EINE Datei anzulegen. Die Historie des
        # Kits ist gross und wird dafuer nicht gebraucht.
        if lauf("gh", "repo", "clone", quelle, str(tmp / "arbeit"), "--",
                "--depth", "1").returncode != 0:
            return 1
        arbeit = tmp / "arbeit"
        if lauf("git", "-C", str(arbeit), "checkout", "-b", zweig).returncode != 0:
            return 1
        ziel = arbeit / zielname
        ziel.parent.mkdir(parents=True, exist_ok=True)
        with ziel.open("w", newline="", encoding="utf-8") as fh:
            fh.write(datei.read_text(encoding="utf-8"))
        titel = datei.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        for args in (("add", zielname),
                     ("commit", "-m", f"meldung: {titel}")):
            if lauf("git", "-C", str(arbeit), *args).returncode != 0:
                return 1
        if lauf("git", "-C", str(arbeit), "push", "-u", "origin",
                zweig).returncode != 0:
            return 1
        r = lauf("gh", "pr", "create", "--repo", repo,
                 "--head", kopf,
                 "--title", f"Meldung: {titel}",
                 "--body-file", zielname, cwd=str(arbeit))
        if r.returncode != 0:
            return 1
        print("\n✓ Pull Request angelegt:")
        print(r.stdout.strip())
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def verb_kit_pfad(a):
    kit, woher = kit_finden(a.kit)
    if kit:
        print(f"{kit}\n  gefunden über: {woher}")
        print(f"  meldet gegen:  {kit_repo_ermitteln(kit, a.repo)}")
        return 0
    print(f"Kein Kit gefunden — {woher}.\n"
          "Trag den Pfad in team.config.sh bzw. team.config.ps1 als "
          "TEAM_KIT_PFAD ein — oder setz ihn für einen Aufruf in die Umgebung.\n"
          "Melden geht auch ohne: `neu` legt die Datei an, `senden` fällt auf "
          "einen Issue-Link zurück.", file=sys.stderr)
    return 3


def main():
    ap = argparse.ArgumentParser(
        description="Rückkanal Feld → Kit: einen Fund am T.E.A.M. selbst melden.")
    ap.add_argument("--projektwurzel")
    ap.add_argument("--meldungen")
    ap.add_argument("--kit")
    ap.add_argument("--projekt")
    ap.add_argument("--repo")
    sub = ap.add_subparsers(dest="verb", required=True)

    p = sub.add_parser("neu", help="Meldungsentwurf anlegen")
    p.add_argument("--titel", required=True)
    p.add_argument("--nummer", help="Bezug, z. B. der eigene Backlog-Eintrag")
    p.add_argument("--art", default="fehler",
                   choices=("fehler", "luecke", "idee"))
    p.set_defaults(fn=verb_neu)

    p = sub.add_parser("pruefen", help="Redaktionsprüfung (Exit 4 = Befunde)")
    p.add_argument("dateien", nargs="*")
    p.set_defaults(fn=verb_pruefen)

    p = sub.add_parser("senden", help="Pull Request anlegen (fragt vorher)")
    p.add_argument("datei")
    p.add_argument("--ja", action="store_true", help="ohne Rückfrage senden")
    p.add_argument("--trotzdem", action="store_true",
                   help="auch bei Redaktionsbefunden senden")
    p.set_defaults(fn=verb_senden)

    p = sub.add_parser("issue-link", help="vorbefüllten Issue-Link ausgeben")
    p.add_argument("datei")
    p.set_defaults(fn=verb_issue_link)

    p = sub.add_parser("kit-pfad", help="wo liegt das Kit? (Diagnose)")
    p.set_defaults(fn=verb_kit_pfad)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())

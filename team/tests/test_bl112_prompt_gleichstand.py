#!/usr/bin/env python3
"""BL-112 — die Briefings sind geteilt, der ZUSAMMENGESETZTE Prompt ist es nicht.

Der Plan zur Doppelbahn stuetzte sich auf die Feststellung, die
driftgefaehrlichste Flaeche sei "konstruktionsbedingt bereits single-source":
`team_briefing` liest `team/prompts/rolle-*.md`, und die 340 Zeilen Briefing
gelten damit fuer beide Zweige. Das stimmt — und ist die halbe Wahrheit. Der
Prompt, der die Rolle wirklich erreicht, entsteht erst im Einstiegsskript, und
diese Prosa steht ZWEIMAL im Repo: einmal in `.sh`, einmal in `.ps1`.

Wer eine Feldlehre nachschaerft und nur eine Fassung anfasst, bekommt zwei
Zweige, die VERSCHIEDENE Agenten steuern. Kein Test schlug an: Beide Zweige
laufen gruen, die Prompts sind nur nicht mehr dieselben. Das war die letzte
Stelle, an der Drift unsichtbar blieb — ueberall sonst greift die Doppelbahn.

WAS DIESER TEST PRUEFT UND WAS NICHT

Verglichen wird der Prompt-QUELLTEXT beider Zweige, nachdem die reine
SYNTAX herausgerechnet ist: `PROMPT="…"` gegen `@"…"@`, und jede Form der
Variablen-Einsetzung (`${VAR}`, `$VAR`, `$(…)`, `$($…)`) wird zu einem
einzigen Platzhalter. Uebrig bleibt die Prosa — also genau das, was ein Mensch
schreibt und was in einer Fassung nachgeschaerft wird.

NICHT geprueft wird, ob die eingesetzten WERTE gleich sind. Das kann nur ein
Lauf zeigen, und dafuer braucht es beide Shells auf derselben Maschine; der
Fall ist als eigener Backlog-Eintrag ausgewiesen statt hier behauptet.

DIE AUSNAHMELISTE IST DER HEIKLE TEIL

Ein zeichenweiser Vergleich schlaegt auch auf LEGITIME Zweigunterschiede an —
`SMOKE_ZEILE` nennt im Bash-Zweig `team.config.sh` und im PowerShell-Zweig
`team.config.ps1`, und das ist richtig so. Ohne Ausnahmeliste waere der Test am
ersten Tag rot und wuerde abgeschaltet statt gelesen (BL-14). Mit einer Liste
ohne Begruendungspflicht wuerde sie zur Sammelstelle, hinter der die echte
Drift verschwindet. Deshalb traegt jede Ausnahme ihren Grund, UND es gibt eine
Probe, die eine nicht mehr gebrauchte Ausnahme meldet.

Stand beim Bau (2026-08-20): noch keine Drift eingetreten — alle vier
Prompt-Bloecke und alle fuenf Prosa-Variablen waren zeichengleich. Der Test
startet also gruen, und jede spaetere Abweichung ist ihm zuzuschreiben.
"""
import io
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[2]

# (bash-Text, powershell-Text, Grund) — der Grund ist Pflicht, siehe Kopf.
AUSNAHMEN = [
    ("team.config.sh", "team.config.ps1",
     "Jeder Zweig nennt seine eigene Konfigurationsdatei. Ein Prompt, der "
     "unter Windows auf team.config.sh zeigt, schickt den Menschen zu einer "
     "Datei, die dort nicht liegt."),
]


def _quelle(*kandidaten):
    """Kit-Ablage (entry/, team/) oder installierte Ablage (Wurzel)."""
    for kandidat in kandidaten:
        pfad = WURZEL / kandidat
        if pfad.is_file():
            return pfad
    return None


def _lies(pfad):
    # utf-8-sig, weil .ps1/.psm1 ein BOM tragen muessen (BL-113).
    return io.open(pfad, encoding="utf-8-sig").read().splitlines()


# --------------------------------------------------------------- Extraktion
def bash_block(pfad, name):
    """Alle Zuweisungen NAME="…" der Datei, auch mehrzeilige, in Reihenfolge."""
    zeilen = _lies(pfad)
    bloecke, i = [], 0
    while i < len(zeilen):
        m = re.match(r"^\s*" + re.escape(name) + r'="(.*)$', zeilen[i])
        if not m:
            i += 1
            continue
        rest, block = m.group(1), []
        if rest.endswith('"') and not rest.endswith('\\"'):
            bloecke.append([rest[:-1]])
            i += 1
            continue
        block.append(rest)
        i += 1
        while i < len(zeilen):
            if zeilen[i].rstrip().endswith('"'):
                block.append(zeilen[i].rstrip()[:-1])
                i += 1
                break
            block.append(zeilen[i])
            i += 1
        bloecke.append(block)
    return bloecke


def ps_block(pfad, name):
    """Dasselbe fuer PowerShell: Here-String @"…"@ oder einzeilige Zuweisung."""
    zeilen = _lies(pfad)
    bloecke, i = [], 0
    here = re.compile(r"^\s*\$" + re.escape(name) + r'\s*=\s*@"\s*$')
    einzeln = re.compile(r"^\s*\$" + re.escape(name) + r"\s*=\s*[\"'](.*)[\"'].*$")
    while i < len(zeilen):
        if here.match(zeilen[i]):
            i += 1
            block = []
            while i < len(zeilen) and not zeilen[i].startswith('"@'):
                block.append(zeilen[i])
                i += 1
            bloecke.append(block)
            i += 1
            continue
        m = einzeln.match(zeilen[i])
        if m:
            bloecke.append([m.group(1)])
        i += 1
    return bloecke


def kanon(zeilen, ausnahmen=AUSNAHMEN):
    """Syntax heraus, Prosa stehen lassen.

    Die Klammer-Zaehlung ist noetig statt eines Regex: Der Bash-Zweig setzt
    Bestandsordner mit `${VAR:+ (${A}: ${B})}` ein, also VERSCHACHTELT, und
    der PowerShell-Zweig rechnet dasselbe vorher in `$planTeil` aus. Erst das
    Zusammenfassen benachbarter Platzhalter macht beide Formen vergleichbar —
    ohne es meldete der Vergleich einen Unterschied, wo keiner ist, und genau
    solche Falschmeldungen kosten den Test seine Glaubwuerdigkeit.
    """
    aus = []
    for z in zeilen:
        z = z.replace("\r", "")
        for bash_text, ps_text, _grund in ausnahmen:
            z = z.replace(bash_text, ps_text)
        erg, i, n = [], 0, len(z)
        while i < n:
            if z[i] == "$" and i + 1 < n and z[i + 1] in "{(":
                auf = z[i + 1]
                zu = "}" if auf == "{" else ")"
                tiefe, j = 0, i + 1
                while j < n:
                    if z[j] == auf:
                        tiefe += 1
                    elif z[j] == zu:
                        tiefe -= 1
                        if tiefe == 0:
                            break
                    j += 1
                erg.append("§")
                i = j + 1
                continue
            if z[i] == "$" and i + 1 < n and (z[i + 1].isalpha() or z[i + 1] == "_"):
                j = i + 1
                while j < n and (z[j].isalnum() or z[j] == "_"):
                    j += 1
                erg.append("§")
                i = j
                continue
            erg.append(z[i])
            i += 1
        z = re.sub(r"§+", "§", "".join(erg))
        z = re.sub(r"\s+", " ", z).strip()
        if z:
            aus.append(z)
    return aus


# ------------------------------------------------------------- die Pruefobjekte
ROLLEN = [
    ("redteam", ("team/redteam.sh", "team/redteam.sh"),
     ("team/redteam.ps1", "team/redteam.ps1"), 25),
    ("ralph", ("entry/ralph.sh", "ralph.sh"), ("entry/ralph.ps1", "ralph.ps1"), 8),
    ("frank", ("entry/frank.sh", "frank.sh"), ("entry/frank.ps1", "frank.ps1"), 15),
    ("axel", ("entry/axel.sh", "axel.sh"), ("entry/axel.ps1", "axel.ps1"), 12),
]

PROSA = [
    ("redteam", ("team/redteam.sh",), ("team/redteam.ps1",), "SCOPE_LINE", "scopeLine"),
    ("redteam", ("team/redteam.sh",), ("team/redteam.ps1",),
     "KONTROLLFLUSS_ZEILE", "kontrollflussZeile"),
    ("redteam", ("team/redteam.sh",), ("team/redteam.ps1",),
     "BESTAND_ZEILE", "bestandZeile"),
    ("bibliothek", ("team/lib.sh",), ("team/lib.psm1",), "SMOKE_ZEILE", "SMOKE_ZEILE"),
    ("bibliothek", ("team/lib.sh",), ("team/lib.psm1",), "SMOKE_SUFFIX", "SMOKE_SUFFIX"),
]


def _paar(sh_kandidaten, ps_kandidaten):
    sh = _quelle(*sh_kandidaten)
    ps = _quelle(*ps_kandidaten)
    if sh is None or ps is None:
        pytest.skip(f"Zweig unvollstaendig: {sh_kandidaten} / {ps_kandidaten}")
    return sh, ps


@pytest.mark.parametrize("rolle,sh_pfade,ps_pfade,mindestzeilen", ROLLEN)
def test_prompt_block_ist_in_beiden_zweigen_derselbe(rolle, sh_pfade, ps_pfade,
                                                     mindestzeilen):
    sh, ps = _paar(sh_pfade, ps_pfade)
    a = kanon([z for b in bash_block(sh, "PROMPT") for z in b])
    b = kanon([z for x in ps_block(ps, "prompt") for z in x])

    # Ohne diese beiden Zeilen waere der Test stumm gruen, sobald die
    # Extraktion ins Leere greift — die BL-22-Falle. Zwei leere Listen sind
    # gleich, und niemand merkt es.
    assert len(a) >= mindestzeilen, (
        f"{rolle}: aus dem Bash-Zweig kamen nur {len(a)} Prompt-Zeilen — die "
        f"Extraktion greift ins Leere, der Vergleich waere wertlos."
    )
    assert len(b) >= mindestzeilen, (
        f"{rolle}: aus dem PowerShell-Zweig kamen nur {len(b)} Prompt-Zeilen."
    )

    assert a == b, (
        f"Der Prompt der Rolle '{rolle}' laeuft zwischen den Zweigen "
        f"auseinander — beide Zweige laufen gruen, steuern aber verschiedene "
        f"Agenten:\n" + _bericht(a, b)
    )


@pytest.mark.parametrize("wo,sh_pfade,ps_pfade,bash_name,ps_name", PROSA)
def test_prosa_variablen_sind_in_beiden_zweigen_dieselben(wo, sh_pfade, ps_pfade,
                                                          bash_name, ps_name):
    """Die Prompt-Bloecke setzen diese Variablen nur EIN — ihre Prosa steht
    daneben und liefe sonst ungeprueft auseinander. `SMOKE_ZEILE` liegt dabei
    in der Bibliothek, nicht im Einstiegsskript: Der Backlog-Eintrag hatte nur
    die vier Einstiegsskripte im Blick."""
    sh, ps = _paar(sh_pfade, ps_pfade)
    a = [kanon(b) for b in bash_block(sh, bash_name)]
    b = [kanon(x) for x in ps_block(ps, ps_name)]
    assert a, f"{wo}/{bash_name}: im Bash-Zweig nichts gefunden"
    assert b, f"{wo}/{ps_name}: im PowerShell-Zweig nichts gefunden"
    assert len(a) == len(b), (
        f"{wo}/{bash_name}: {len(a)} Zuweisungen im Bash-Zweig, {len(b)} im "
        f"PowerShell-Zweig — eine Fallunterscheidung fehlt auf einer Seite."
    )
    for nr, (x, y) in enumerate(zip(a, b), 1):
        assert x == y, (
            f"{wo}/{bash_name}, Zuweisung {nr} laeuft auseinander:\n"
            + _bericht(x, y)
        )


def test_jede_ausnahme_wird_noch_gebraucht():
    """Die Probe gegen die Sammelstelle.

    Eine Ausnahmeliste ohne Verfallsdatum waechst, und hinter jeder unnoetigen
    Ausnahme kann echte Drift verschwinden. Hier faellt eine Ausnahme auf, die
    nichts mehr rettet: Ohne sie muesste irgendein Vergleich rot werden.
    """
    for ausnahme in AUSNAHMEN:
        ohne = [a for a in AUSNAHMEN if a is not ausnahme]
        gebraucht = False
        for _rolle, sh_pfade, ps_pfade, _min in ROLLEN:
            sh, ps = _quelle(*sh_pfade), _quelle(*ps_pfade)
            if sh is None or ps is None:
                continue
            a = kanon([z for b in bash_block(sh, "PROMPT") for z in b], ohne)
            b = kanon([z for x in ps_block(ps, "prompt") for z in x], ohne)
            gebraucht = gebraucht or a != b
        for _wo, sh_pfade, ps_pfade, n1, n2 in PROSA:
            sh, ps = _quelle(*sh_pfade), _quelle(*ps_pfade)
            if sh is None or ps is None:
                continue
            a = [kanon(x, ohne) for x in bash_block(sh, n1)]
            b = [kanon(x, ohne) for x in ps_block(ps, n2)]
            gebraucht = gebraucht or a != b
        assert gebraucht, (
            f"Die Ausnahme {ausnahme[0]!r} -> {ausnahme[1]!r} rettet keinen "
            f"Vergleich mehr und gehoert gestrichen. Begruendet war sie mit: "
            f"{ausnahme[2]}"
        )


def test_der_vergleich_wuerde_drift_wirklich_melden():
    """Die Gegenprobe zum Vergleich selbst.

    Ohne sie koennte `kanon()` eines Tages alles auf dieselbe leere Liste
    abbilden und der Test bliebe stumm gruen — dieselbe Bauart, gegen die
    oben die Mindestzeilenzahl steht.
    """
    sh = _quelle("entry/frank.sh", "frank.sh")
    ps = _quelle("entry/frank.ps1", "frank.ps1")
    if sh is None or ps is None:
        pytest.skip("frank-Paar in dieser Ablage nicht vollstaendig")
    a = kanon([z for b in bash_block(sh, "PROMPT") for z in b])
    b = kanon([z for x in ps_block(ps, "prompt") for z in x])
    assert a == b, "Voraussetzung entfallen: frank ist bereits abgewichen"

    # Eine nachgeschaerfte Feldlehre in NUR EINER Fassung.
    verdreht = list(a)
    verdreht[0] = verdreht[0] + " NEU: und zwar sofort."
    assert verdreht != b, (
        "Der Vergleich meldet eine nachtraeglich eingefuegte Zeile nicht — "
        "dann meldet er auch keine echte Drift."
    )


def _bericht(a, b):
    import difflib
    return "\n".join(list(difflib.unified_diff(
        a, b, fromfile="bash-Zweig", tofile="powershell-Zweig", lineterm=""))[:40])

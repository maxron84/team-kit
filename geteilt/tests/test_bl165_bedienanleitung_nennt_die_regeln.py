#!/usr/bin/env python3
"""BL-165, BL-183, BL-164, BL-167, BL-170 — was in der Bedienanleitung fehlte.

Fünf Funde, ein gemeinsamer Nenner: **Die Regel gab es, nur nicht dort, wo sie
gebraucht wird.** Jeder einzelne war im Code, in einem Test, im Archiv oder im
Kommentarkopf sauber festgehalten — also ausschließlich an Orten, die der
Mensch im Zielprojekt nicht liest.

`BL-165` — DIE SITZUNGS-INVARIANTE HAT ZWEI HÄLFTEN
    „Genau EINE Buchung je Sitzung — nicht null und nicht zwei."
    `BL-116` löste die eine Hälfte (zwei Closeouts messen dasselbe Transkript
    zweimal). Die andere war **nirgends** dokumentiert, auch nicht im
    Briefing: `sitzung-messen` liest das zuletzt geänderte Transkript, also
    die laufende Sitzung. Eine Sitzung, die **nicht** bucht, wird deshalb
    **nie** gemessen — die Kosten sind nicht „später fällig", sie sind weg.

    **Der Kit-eigene Rat erzeugt die Lücke, die er nicht benannte:** „nach
    einem gebuchten Closeout eine neue Sitzung für die nächste Kaskade". Wer
    dem folgt, plant K(N+1) in einer Sitzung, die selbst nichts bucht.
    `TEAM.md` nennt die Größenordnung selbst: rund 16 USD pro Session.

    Beide Hälften zeigen in **entgegengesetzte** Richtungen. Wer nur `BL-116`
    kennt, bucht aus Vorsicht seltener — und verliert Sitzungen.

`BL-183` — `--watch` STAND IN KEINER BEDIENANLEITUNG
    Der einzige Live-Modus war nur im Kommentarkopf des Skripts dokumentiert.
    Die wörtliche Frage eines Stakeholders nach zwei Kaskaden: *„Ich sehe
    wieder kein Monitoring, das ist weil ich noch kein Update vom Kit
    herausgefahren habe, korrekt?"* — **die Vermutung war falsch, und das ist
    der Punkt.** Es fehlte nichts, es war nur nicht auffindbar.

`BL-164` — EIN VERWEIS AUF EIN WERKZEUG, DAS DER LESER NICHT HAT
    `TEAM.md` schickte den Anwender zu `team-auth-setup.sh`; der Installer
    legt es nicht ins Projekt, und der Fundort stand nirgends. Wer den Key
    hinterlegen will und das Werkzeug nicht findet, greift zu genau dem
    `export`, vor dem der Absatz zwei Zeilen darüber warnt — der Verweis
    leitete ins **Gegenteil** seiner Absicht. Die Lehre dahinter ist teuer
    belegt: ein ~13,8-USD-Leerlauf-Lauf, vollständig über API, weil ein
    `.bashrc`-Key das Abo-first-Design still aushebelte.

`BL-167` — DIE GEGENPROBE OHNE ZEITPUNKT PRÜFT ZUVERLÄSSIG NICHTS
    „Ändert eine Stufe einen zentralen Wert" trifft auf die **einführende**
    Stufe zu — dort ist die Probe wertlos, solange kein Verbraucher existiert.
    Sie meldet trotzdem grün.

`BL-170` — DER PLATZHALTER IN RALPHS EISERNEN GRENZEN
    Die Smoke-Test-Marke stand auch in `rolle-ralph.md`, **in Backticks** und
    **unter den eisernen Grenzen** — in der Auszeichnung und an der Position,
    an der sonst ein ausführbarer Befehl steht.

    Ihr Name steht hier bewusst NICHT ausgeschrieben: Schritt 3 von
    `kit-test.sh` durchsucht die installierte Ablage nach ungefüllten
    Platzhaltern und meldet jede Datei, in der einer steht — auch eine, die
    ihn nur **zitiert**. Diese Datei hat den Schritt beim ersten Entwurf rot
    gemacht. Wo die Marke gebraucht wird, steht sie zusammengesetzt.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO_ROOT = Path(__file__).resolve().parents[2]


def _lies(*teile):
    p = REPO_ROOT.joinpath(*teile)
    if not p.is_file():
        pytest.skip(f"{p.name} liegt in dieser Ablage nicht")
    return p.read_text(encoding="utf-8-sig")


def _team_md():
    """Die Bedienanleitung — im Kit die Vorlage, im Projekt die gerenderte."""
    for teile in (("bootstrap", "TEAM.md"), ("TEAM.md",)):
        p = REPO_ROOT.joinpath(*teile)
        if p.is_file():
            return p.read_text(encoding="utf-8-sig")
    pytest.skip("keine TEAM.md in dieser Ablage")


# --- BL-165: beide Hälften der Invariante ------------------------------------


def test_die_invariante_steht_in_der_bedienanleitung():
    """Sie stand in Briefing, Regel-Inventar, Test und Archiv — nur nicht dort,
    wo der Mensch sie liest."""
    t = _team_md()
    assert re.search(r"genau einmal", t, re.I), (
        "BL-165: TEAM.md nennt die Sitzungs-Invariante nicht. Sie stand "
        "ausschließlich an Orten, die der Anwender nicht liest.")


def test_die_teure_haelfte_steht_dabei():
    """Nicht-buchen ist UNNACHHOLBAR — und genau das sagte kein Dokument.

    `TEAM.md` sagte nur „bleibt strukturell unerfasst", und zwar im
    Zusammenhang des Closeouts. Dass es unwiederbringlich ist, sagte der Satz
    nicht — und ohne diese Hälfte bucht man aus Vorsicht seltener.
    """
    t = _team_md()
    assert re.search(r"unwiederbringlich|nicht .später fällig|sind \*\*weg\*\*",
                     t, re.I), (
        "BL-165: TEAM.md sagt nicht, dass eine nicht gebuchte Sitzung "
        "dauerhaft verloren ist.")


def test_der_messumfang_ist_offengelegt():
    """Ein Anwender kann sonst nicht wissen, dass nur die LAUFENDE Sitzung
    gemessen wird — und vermutet naheliegenderweise eine Gesamtmessung."""
    t = _team_md()
    assert re.search(r"zuletzt geänderte", t), (
        "BL-165: TEAM.md legt den Messumfang von `sitzung-messen` nicht offen.")


def test_das_briefing_nennt_den_fall_den_sein_eigener_rat_erzeugt():
    """Das Briefing rät zu einer neuen Sitzung je Kaskade — und erzeugte damit
    genau die Sitzung, die nichts bucht."""
    t = _lies("geteilt", "prompts", "rolle-architekt.md")
    assert "Kit-BL-165" in t and "--kaskade" in t, (
        "Das Architekten-Briefing sagt nicht, dass eine reine Planungssitzung "
        "ihre Kosten selbst bucht.")


def _bl193_absatz():
    """Der **eine** Absatz, der die Regel trägt — nicht der ganze Abschnitt.

    Der erste Entwurf dieser Fälle prüfte den ganzen Punkt 2 auf `--addieren`
    und `Pfad`. Beides steht dort schon aus anderem Grund (`--addieren` für
    den Nachlauf einer Rolle), und drei von drei Gegenproben blieben grün. Die
    Zusicherung gilt dem Absatz, also wird der Absatz geschnitten.
    """
    t = _lies("geteilt", "prompts", "rolle-architekt.md")
    anfang = t.index("Kit-BL-193")
    # Rueckwaerts bis zum Satzanfang der Regel, vorwaerts bis zum naechsten
    # Absatz von Punkt 2 (er beginnt mit "Der erste Befehl bucht").
    anfang = t.rindex("**\u201e", 0, anfang)
    ende = t.index("Der erste Befehl bucht", anfang)
    return t[anfang:ende]


def test_der_closeout_nennt_die_zweite_architekten_sitzung():
    """`BL-193` — der Rückweg, dort wo jemand nachschlägt.

    `BL-165` hat die **Vorbeugung** gebracht: Eine reine Planungssitzung bucht
    ihre Kosten selbst. Die Meldung aus dem Feld kam gegen die Fassung davor —
    und sie zeigt eine zweite Hälfte, die auch mit der Regel offen bleibt.

    **Wer beim Closeout steht, hat die Aushärtung schon hinter sich.** War sie
    nicht gebucht, hilft ihm die Vorbeugungsregel nicht mehr; er braucht den
    **Rückweg**, und der muss an Punkt 2 des Closeout-Abschnitts stehen. Dort
    stand bis dahin „meine eigene Sitzung" — im Closeout-Kontext eindeutig die
    Closeout-Sitzung. Die Aushärtungs-Sitzung derselben Kaskade wurde an
    **keiner** Stelle erwähnt.

    Der Abschnitt kannte die verwandte Falle bereits, aber nur in der
    **anderen** Richtung: „Ein Closeout je Sitzung" warnt vor **zwei**
    Buchungen aus **einer** Sitzung (`BL-116`). Der umgekehrte Fall — **eine**
    Kaskade über **mehrere** Sitzungen, von denen nur die letzte gemessen wird
    — fehlte. Im Feld waren das 10,65 USD, 39 % der Architektenkosten einer
    Kaskade.
    """
    absatz = _bl193_absatz()
    assert "--addieren" in absatz, (
        "BL-193: Der Rueckweg fehlt. Die Faehigkeit ist da "
        "(sitzung-messen <pfad>), sie braucht nur einen Aufrufer im Ablauf.")
    assert "Pfad" in absatz, (
        "BL-193: Ohne den Hinweis auf den PFAD bleibt nur `--projekt .`, und "
        "das liest genau die falsche Sitzung.")
    assert "Aushärtung" in absatz, (
        "BL-193: Der Absatz benennt die zweite Sitzung nicht.")


def test_der_closeout_warnt_vor_der_doppelbuchung():
    """Die Gegenrichtung, und sie ist der Grund, warum der Rückweg nicht
    einfach „immer nachbuchen" heißen darf.

    Wurde die Aushärtung an ihrem Ende gebucht (`BL-165`), steckt sie bereits
    im Ledger. Ein Rückweg ohne diese Unterscheidung erzeugte genau den
    Schaden, den `BL-116` beschreibt — denselben Betrag zweimal.
    """
    absatz = _bl193_absatz()
    assert re.search(r"nicht\*{0,2}\s+noch einmal", absatz), (
        "BL-193: Der Rueckweg sagt nicht, wann er NICHT gilt. Dann bucht er "
        "den Betrag ein zweites Mal (BL-116).")
    assert "Kit-BL-165" in absatz, (
        "BL-193: Der Absatz verweist nicht auf die Vorbeugungsregel. Ohne sie "
        "liest sich der Rueckweg wie 'immer nachbuchen'.")


# --- BL-183: --watch ---------------------------------------------------------


def test_watch_steht_in_der_bedienanleitung():
    """In der BEFEHLSTABELLE, nicht irgendwo in der Prosa.

    Die Tabelle ist der Ort, an dem ein Anwender nachsieht, was es gibt — ein
    Modus, der nur in einem Absatz erwähnt wird, ist nur halb auffindbar, und
    genau darum ging es bei diesem Fund.
    """
    t = _team_md()
    in_tabelle = [z for z in t.splitlines()
                  if z.startswith("|") and "--watch" in z]
    assert in_tabelle, (
        "BL-183: `--watch` steht in keiner Zeile der Befehlstabelle von "
        "TEAM.md.")
    assert "--watch" in t, (
        "BL-183: `team-status --watch` steht in keiner Bedienanleitung. Der "
        "einzige Live-Modus war nur im Kommentarkopf des Skripts dokumentiert "
        "— ein Stakeholder hielt das Monitoring daraufhin für nicht "
        "installiert. Es fehlte nichts, es war nur nicht auffindbar.")


def test_watch_sagt_auch_was_es_nicht_kann():
    """Ein Beobachter, der die Historie überschreibt, ist genau dann nutzlos,
    wenn man wissen will, was in den letzten Minuten passiert ist."""
    t = _team_md()
    stelle = t[t.index("--watch"):t.index("--watch") + 1600]
    assert re.search(r"neu|nicht an", stelle), (
        "TEAM.md sagt nicht, dass --watch neu zeichnet statt anzuhängen.")


@pytest.mark.parametrize("skript,ruf", [
    ("bash/entry/team-status.sh", "--watch"),
    ("pwsh/entry/team-status.ps1", "--watch"),
])
def test_der_modus_gibt_es_auf_beiden_bahnen(skript, ruf):
    """Ein in der Anleitung genannter Modus, den eine Bahn nicht hat, ist
    schlimmer als ein undokumentierter."""
    p = REPO_ROOT / skript
    if not p.is_file():
        pytest.skip(f"{skript} liegt in dieser Ablage nicht")
    assert ruf in p.read_text(encoding="utf-8-sig"), (
        f"{skript} kennt {ruf} nicht, TEAM.md nennt es aber.")


# --- BL-164: der Auth-Key -----------------------------------------------------


def test_der_handweg_zum_api_key_steht_da():
    """Ein Dokument, das ein Werkzeug nennt, das der Leser nicht hat, muss den
    Weg OHNE dieses Werkzeug zeigen."""
    t = _team_md()
    # Der AUSFUEHRBARE Befehl, nicht nur das Wort "Handweg": Ein Dokument, das
    # einen Weg ankuendigt und ihn nicht zeigt, ist die Bauart BL-44.
    assert "install -m 600" in t, (
        "BL-164: TEAM.md nennt keinen Weg, den Key ohne das nicht "
        "mitinstallierte Skript zu hinterlegen — und wer ihn nicht findet, "
        "greift zu genau dem `export`, vor dem der Absatz warnt.")


def test_das_skript_wird_mit_vollem_fundort_genannt():
    """Der Skriptname allein zeigt ins Leere: Der Installer legt die Datei
    nicht ins Projekt."""
    t = _team_md()
    if "team-auth-setup" not in t:
        return                      # gar nicht genannt ist auch in Ordnung
    assert re.search(r"scripts[/\\]team-auth-setup", t), (
        "BL-164: TEAM.md nennt `team-auth-setup`, aber nicht seinen Fundort "
        "im Kit — im Projekt gibt es die Datei nicht.")


# --- BL-167: der Zeitpunkt der Gegenprobe ------------------------------------


def test_die_regel_nennt_den_zeitpunkt():
    t = _lies("bootstrap", "CLAUDE.md.vorlage")
    assert "Verbraucher" in t, (
        "BL-167: Die Regel [Zentrale Werte gehören gegengeprobt] nennt keinen "
        "Zeitpunkt. In der EINFÜHRENDEN Stufe prüft die Probe zuverlässig "
        "nichts — und meldet trotzdem grün.")


def test_das_kriterium_ist_maschinell_pruefbar():
    """Der Teil, der ohne Planvorsatz wirkt: Weniger oder gleich viele rote
    Stellen als Textsuch-Fundstellen heißt, dass nichts geprüft wurde."""
    t = _lies("bootstrap", "CLAUDE.md.vorlage")
    assert re.search(r"weniger oder gleich viele", t), (
        "BL-167: Das nachprüfbare Kriterium fehlt — dann hängt die Regel "
        "wieder am Vorsatz des Planenden.")


@pytest.mark.parametrize("briefing", ["rolle-architekt.md", "rolle-ralph.md"])
def test_die_briefings_kennen_das_kriterium(briefing):
    """Der Architekt schneidet die Stufen — bei ihm entscheidet sich, in
    welcher die Probe landet. Ralph baut sie ein und merkt es als Erster.

    **Frank steht bewusst NICHT in dieser Liste.** Sein Briefing lag bereits
    bei 45 Zeilen, dem harten Limit aus `test_stufe90_briefings.py` — und das
    Limit ist keine Formsache: Ein Briefing liegt in JEDEM Prompt seiner
    Rolle, jede Zeile wird bei jedem Aufruf bezahlt. Der Eintrag verlangt
    ausdrücklich das Architekten-Briefing; Franks Absatz nennt die Zahlen
    ohnehin. Ein Zusatz, der eine andere Zusicherung bricht, ist keiner.
    """
    t = _lies("geteilt", "prompts", briefing)
    assert "Kit-BL-167" in t, (
        f"{briefing} nennt den Zeitpunkt der Gegenprobe nicht.")


@pytest.mark.parametrize("briefing", ["ralph", "harry", "marv", "frank", "axel"])
def test_die_loop_briefings_bleiben_unter_dem_limit(briefing):
    """Dieselbe Zusicherung wie in `test_stufe90_briefings.py`, hier als
    Frühwarnung an der Stelle, an der Regeln in Briefings wandern.

    Sie ist bei genau diesem Abtrag eingesprungen: Eine Ergänzung an Frank
    hätte das Limit gerissen, und der Fehlschlag wäre erst im vollen
    Suitenlauf aufgefallen.
    """
    p = REPO_ROOT / "geteilt" / "prompts" / f"rolle-{briefing}.md"
    if not p.is_file():
        pytest.skip(f"rolle-{briefing}.md liegt in dieser Ablage nicht")
    n = len(p.read_text(encoding="utf-8").splitlines())
    assert n <= 45, (
        f"rolle-{briefing}.md hat {n} Zeilen (Limit 45). Ein Briefing liegt "
        "in JEDEM Prompt seiner Rolle — jede Zeile wird bei jedem Aufruf "
        "bezahlt.")


# --- BL-170: kein Platzhalter in den eisernen Grenzen ------------------------


def test_ralphs_grenzen_tragen_keinen_befehls_platzhalter():
    """Backticks sind die Auszeichnung, an der eine Instanz einen ausführbaren
    Befehl erkennt. Einen Platzhalter darum zu legen, der leer werden darf,
    ist dieselbe Klasse Fehler wie ein nicht-leerer Default (`BL-149`)."""
    t = _lies("geteilt", "prompts", "rolle-ralph.md")
    marke = "".join(("{{", "SMOKE_TEST", "}}"))
    assert f"`{marke}`" not in t, (
        f"BL-170: {marke} steht in rolle-ralph.md wieder in Backticks. Ohne "
        "konfigurierten Smoke-Test rendert das zu einem TODO-Satz, der unter "
        "den EISERNEN GRENZEN wie ein Befehl aussieht — und daneben sagt "
        "SMOKE_ZEILE im selben Prompt das Gegenteil.")


@pytest.mark.parametrize("installer,muster", [
    ("bash/install.sh", r"\{\{SMOKE_TEST_GRENZE\}\}"),
    ("pwsh/install.ps1", r"\{\{SMOKE_TEST_GRENZE\}\}"),
])
def test_beide_installer_fuellen_die_neue_weiche(installer, muster):
    """Ein Platzhalter, den nur eine Bahn füllt, steht auf der anderen wörtlich
    im ausgelieferten Briefing (Klasse `BL-142`/`BL-145`)."""
    p = REPO_ROOT / installer
    if not p.is_file():
        pytest.skip(f"{installer} liegt in dieser Ablage nicht")
    assert re.search(muster, p.read_text(encoding="utf-8-sig")), (
        f"{installer} füllt die Weiche nicht — dann liefert diese Bahn den "
        "Platzhalter wörtlich aus.")


def test_die_bash_fassung_fuellt_in_BEIDEN_routinen():
    """`install.sh` hat zwei Füll-Routinen (Erstinstallation und Update).

    Genau diese Doppelung hat `BL-113`, `BL-119` und `BL-137` je einmal
    gekostet: Ein neuer Platzhalter landete in der einen und fehlte in der
    anderen.
    """
    p = REPO_ROOT / "bash" / "install.sh"
    if not p.is_file():
        pytest.skip("install.sh liegt in dieser Ablage nicht")
    n = len(re.findall(r'\("\{\{SMOKE_TEST_GRENZE\}\}"',
                       p.read_text(encoding="utf-8")))
    assert n == 2, (
        f"{n} Füllung(en) statt zwei — der Update-Pfad hat eine eigene "
        "Routine, und sie braucht den Platzhalter genauso.")

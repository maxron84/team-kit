#!/usr/bin/env python3
"""BL-141: Die Architekten-Kostenzeile war ein Zeilen-Churn-Proxy und lag im
Feld 35 % zu niedrig — obwohl die Daten fuer eine exakte Messung auf der Platte
lagen.

DER FELDBEFUND
    `Feld B`, Kaskade 1. Die Zeile meldete **7,6861 USD**; die Messung
    aus dem Sitzungstranskript ergab **11,7582 USD**.

    `architekt_schaetzung()` rechnet `git_churn(...) * EICHFAKTOR`. Das misst
    die GROESSE DES DIFFS, nicht die Arbeit: Eine Sitzung mit viel Lesen,
    Pruefen und Gegenproben und wenig geschriebenem Text wird systematisch
    unterschaetzt, eine Prosa-Sitzung ueberschaetzt.

    Das Architekten-Briefing verlangt die Transkript-Messung ausdruecklich —
    aber KEIN Werkzeug des Kits konnte sie. Also schrieb sich jeder Architekt
    das Skript neu, oder er nahm die Churn-Zahl und buchte sie als gemessen.

DIE DREI FALLEN, ALLE DREI IM FELD GETRETEN
    (1) DEDUPLIZIEREN ueber die Nachrichten-ID. Eine Antwort erzeugt mehrere
        Transkriptzeilen mit DERSELBEN usage-Angabe. Im Feld: 172 rohe Saetze,
        nach Dedup 76. Wer Zeilen zaehlt, ueberschaetzt um mehr als das Doppelte.
    (2) CACHE-WRITE NACH LAUFZEIT trennen. 1h kostet das 2,0-Fache des Inputs,
        5m nur das 1,25-Fache. Das Transkript gibt beide getrennt her.
    (3) BASISPREIS AM MODELL festmachen — und sagen, wenn die ID unbekannt ist.

WARUM DIE SELBSTPRUEFUNG DER EIGENTLICHE INHALT IST
    Eine Preistabelle im Quelltext ist eine Behauptung. Die headless-Logs des
    Kits tragen BEIDES: dieselbe usage-Struktur wie das Transkript UND den
    abgerechneten `total_cost_usd`, je Modell aufgeschluesselt in `modelUsage`.
    Das sind fertige Eichpunkte.

    `preise_nachrechnen()` rechnet sie mit DEMSELBEN Code nach. Weicht das
    Ergebnis ab, ist die Tabelle veraltet, und das Werkzeug SAGT DAS, statt
    eine falsche Zahl zu buchen. Der teure Fehler ist nicht die falsche Zahl —
    es ist die falsche Zahl, die wie eine Messung aussieht.

WAS DIESER TEST PRUEFT
    Alles am Verhalten, gegen gebaute Transkripte und Logs mit BEKANNTEN
    Werten. Kein Netz, keine echte Sitzung: Ein Test, der ein echtes Transkript
    braucht, laeuft genau auf der Maschine, auf der er geschrieben wurde.
"""
import json
import subprocess
import sys
from pathlib import Path

from conftest import kit_pfad

REPO_ROOT = Path(__file__).resolve().parents[2]

for _tools in (REPO_ROOT / "geteilt" / "tools", kit_pfad("tools")):
    if _tools.is_dir():
        sys.path.insert(0, str(_tools))
        break
import kosten  # noqa: E402

KOSTEN_PY = kit_pfad("tools", "kosten.py")


def _satz(mid, modell="claude-opus-5", ein=0, aus=0, lesen=0, w5=0, w1=0):
    """Eine Transkriptzeile, wie die Agenten-CLI sie schreibt."""
    return json.dumps({"type": "assistant", "message": {
        "id": mid, "model": modell,
        "usage": {"input_tokens": ein, "output_tokens": aus,
                  "cache_read_input_tokens": lesen,
                  "cache_creation": {"ephemeral_5m_input_tokens": w5,
                                     "ephemeral_1h_input_tokens": w1}}}})


# --- Falle 1: die Deduplikation ---------------------------------------------

def test_dieselbe_nachricht_zaehlt_einmal(tmp_path):
    """Der Fall, der im Feld die groesste Einzelabweichung erzeugt haette.

    Drei Zeilen, EINE Nachricht. Wer Zeilen zaehlt, bucht das Dreifache.
    """
    t = tmp_path / "s.jsonl"
    t.write_text("\n".join([_satz("msg_1", ein=1000, aus=100)] * 3) + "\n",
                 encoding="utf-8")
    je_modell, antworten, doppelt = kosten.sitzung_messen([str(t)])
    assert antworten == 1, "die Nachricht wurde mehrfach gezaehlt"
    assert doppelt == 2, f"erwartet 2 verworfene Duplikate, ist {doppelt}"
    assert je_modell["claude-opus-5"]["input"] == 1000, je_modell


def test_verschiedene_nachrichten_zaehlen_einzeln(tmp_path):
    """Gegenrichtung: Die Deduplikation darf nicht zu viel wegwerfen.

    Ohne diesen Fall waere ein Fix, der ALLES verwirft, gruen — und die
    gebuchte Zahl waere null statt zu hoch.
    """
    t = tmp_path / "s.jsonl"
    t.write_text("\n".join(_satz(f"msg_{i}", ein=1000) for i in range(4)) + "\n",
                 encoding="utf-8")
    je_modell, antworten, doppelt = kosten.sitzung_messen([str(t)])
    assert (antworten, doppelt) == (4, 0)
    assert je_modell["claude-opus-5"]["input"] == 4000


# --- Falle 2: die zwei Cache-Laufzeiten -------------------------------------

def test_cache_write_wird_nach_laufzeit_getrennt(tmp_path):
    """1h kostet das 2,0-Fache, 5m das 1,25-Fache. Wer beides in einen Topf
    wirft, liegt je nach Mischung um bis zu 60 % daneben."""
    t = tmp_path / "s.jsonl"
    t.write_text(_satz("m", w5=1_000_000, w1=1_000_000) + "\n", encoding="utf-8")
    je_modell, _, _ = kosten.sitzung_messen([str(t)])
    k = je_modell["claude-opus-5"]
    assert k["cache_write_5m"] == 1_000_000
    assert k["cache_write_1h"] == 1_000_000
    # 1 Mio zu 1,25x5 + 1 Mio zu 2,0x5 = 6,25 + 10,00
    assert abs(kosten.kosten_aus_tokens(k, 5.00) - 16.25) < 1e-9


def test_altes_transkript_ohne_aufschluesselung_zaehlt_konservativ(tmp_path):
    """Aeltere Transkripte tragen nur die Summe. Konservativ als 5m buchen:
    Das ist der GUENSTIGERE Satz, die Zahl faellt also eher zu niedrig aus.
    Eine zu niedrige gebuchte Zahl faellt beim Abgleich auf — eine zu hohe
    wird geglaubt."""
    t = tmp_path / "s.jsonl"
    t.write_text(json.dumps({"message": {"id": "m", "model": "claude-opus-5",
                 "usage": {"cache_creation_input_tokens": 1_000_000}}}) + "\n",
                 encoding="utf-8")
    je_modell, _, _ = kosten.sitzung_messen([str(t)])
    k = je_modell["claude-opus-5"]
    assert (k["cache_write_5m"], k["cache_write_1h"]) == (1_000_000, 0)


# --- Falle 3: der Basispreis am Modell --------------------------------------

def test_basispreis_haengt_am_modell_und_toleriert_varianten():
    assert kosten.modell_basispreis("claude-opus-5") == 5.00
    assert kosten.modell_basispreis("claude-sonnet-5") == 3.00
    assert kosten.modell_basispreis("claude-haiku-4-5") == 1.00
    # Datierte Variante und Plattform-Praefix duerfen die Tabelle nicht
    # verdoppeln muessen.
    assert kosten.modell_basispreis("claude-opus-4-8-20260101") == 5.00
    assert kosten.modell_basispreis("anthropic.claude-sonnet-5") == 3.00
    # Laengster Praefix gewinnt — sonst faenge "claude-opus-4-5" auch
    # "claude-opus-4-8" ab, je nach Reihenfolge im dict.
    assert kosten.modell_basispreis("claude-opus-4-6") == 5.00


def test_unbekanntes_modell_wird_genannt_statt_geraten(tmp_path):
    """Der Kern der Ehrlichkeit: Eine geratene Zahl sieht aus wie eine Messung.

    Die Token des unbekannten Modells duerfen NICHT stillschweigend in die
    Summe wandern und das Modell muss namentlich zurueckkommen.
    """
    assert kosten.modell_basispreis("claude-zukunft-9") is None
    je_modell = {"claude-opus-5": dict(kosten._tokenkuebel(), input=1_000_000),
                 "claude-zukunft-9": dict(kosten._tokenkuebel(), input=9_000_000)}
    gesamt, zeilen, unbekannt = kosten.sitzung_kosten(je_modell)
    assert unbekannt == ["claude-zukunft-9"]
    assert abs(gesamt - 5.00) < 1e-9, (
        "die Token des unbekannten Modells sind in die Summe gewandert")
    assert [z[0] for z in zeilen] == ["claude-opus-5"]


def test_mehrere_modelle_werden_je_eigenem_preis_gerechnet():
    """Eine Sitzung kann das Modell wechseln, und der Basispreis haengt daran.
    Ein gemeinsamer Token-Kuebel waere mit dem ersten Wechsel falsch."""
    je_modell = {"claude-opus-5": dict(kosten._tokenkuebel(), input=1_000_000),
                 "claude-haiku-4-5": dict(kosten._tokenkuebel(), input=1_000_000)}
    gesamt, zeilen, unbekannt = kosten.sitzung_kosten(je_modell)
    assert not unbekannt
    assert abs(gesamt - 6.00) < 1e-9, f"5.00 + 1.00 erwartet, ist {gesamt}"


# --- Die Selbstpruefung, die das Werkzeug erst gueltig macht -----------------

def _log(pfad, usd, nutzung):
    """Ein headless-Log mit Eichpunkt.

    BL-152: Die `nutzung` hier traegt camelCase, weil ein echtes `modelUsage`
    das tut — `inputTokens`, nicht `input_tokens`. Bis dahin stand hier
    snake_case, also die Sprache des LESERS statt die des Logs. Alle vier
    Faelle waren gruen, und sie haben damit einen Leserfehler FESTGESCHRIEBEN:
    `preise_nachrechnen` fragte nach snake_case, im Feld stand camelCase, jeder
    Kuebel blieb 0 und die Eichung meldete bei jedem Lauf 100 % Abweichung.

    Die Lehre gehoert hierher, weil sie an dieser Zeile haengt: Ein Test, der
    sein Testmaterial im Dialekt des Codes schreibt, prueft den Code gegen sich
    selbst. Das Format eines Fixtures muss aus der QUELLE kommen, nicht aus dem
    Leser. Dieselbe Bauart wie in BL-143.

    Die Gegenprobe dazu steht in `test_bl152_eichung_liest_das_log_format.py`:
    Dort ist das Fixture aus echten abgerechneten Laeufen genommen.
    """
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps({"total_cost_usd": usd, "modelUsage": nutzung}),
                    encoding="utf-8")


def test_stimmige_preistabelle_wird_bestaetigt(tmp_path):
    """Ein Log, dessen abgerechneter Betrag die Tabelle reproduziert."""
    # 1 Mio Input + 1 Mio Output bei 5,00 USD/Mio Input = 5,00 + 25,00
    _log(tmp_path / ".ralph-logs" / "a.json", 30.00,
         {"claude-opus-5": {"inputTokens": 1_000_000,
                            "outputTokens": 1_000_000}})
    befunde = kosten.preise_nachrechnen(kosten.logs_einsammeln(str(tmp_path)))
    assert len(befunde) == 1, befunde
    assert befunde[0][3] < kosten.PREIS_TOLERANZ, (
        f"stimmige Tabelle als abweichend gemeldet: {befunde[0]}")


def test_veraltete_preistabelle_wird_erkannt(tmp_path):
    """Die Gegenprobe. Ohne sie waere die Selbstpruefung ein Ornament.

    Derselbe Lauf, aber der Anbieter hat den Preis geaendert — das Log meldet
    45 USD, die Tabelle rechnet 30. Genau dieser Fall muss anschlagen, sonst
    bucht das Werkzeug jahrelang mit einer toten Tabelle weiter.
    """
    _log(tmp_path / ".team-logs" / "b.json", 45.00,
         {"claude-opus-5": {"inputTokens": 1_000_000,
                            "outputTokens": 1_000_000}})
    befunde = kosten.preise_nachrechnen(kosten.logs_einsammeln(str(tmp_path)))
    assert len(befunde) == 1
    assert befunde[0][3] > kosten.PREIS_TOLERANZ, (
        "eine um 50 % falsche Tabelle wurde nicht bemerkt")


def test_log_ohne_eichpunkt_ist_kein_befund(tmp_path):
    """Ein Log ohne modelUsage ist kein Fehler, sondern nur kein Eichpunkt.

    Wuerde es als Befund zaehlen, meldete das Werkzeug bei jedem aelteren
    Projekt eine veraltete Preistabelle — ein Waechter mit Fehlalarmen wird
    stillgelegt (Bauart BL-14).
    """
    (tmp_path / ".ralph-logs").mkdir(parents=True)
    (tmp_path / ".ralph-logs" / "alt.json").write_text(
        json.dumps({"total_cost_usd": 1.23, "num_turns": 5}), encoding="utf-8")
    assert kosten.preise_nachrechnen(kosten.logs_einsammeln(str(tmp_path))) == []


def test_unbekanntes_modell_im_log_ist_kein_befund(tmp_path):
    """Sonst meldete ein neues Modell im Log eine 'veraltete Preistabelle',
    obwohl die vorhandenen Eintraege stimmen. Die Luecke gehoert an die
    Sitzungsmessung gemeldet, nicht an die Eichung."""
    _log(tmp_path / ".ralph-logs" / "c.json", 99.00,
         {"claude-zukunft-9": {"inputTokens": 1_000_000}})
    assert kosten.preise_nachrechnen(kosten.logs_einsammeln(str(tmp_path))) == []


# --- Die Bedienoberflaeche ---------------------------------------------------

def _cli(cwd, *args):
    r = subprocess.run([sys.executable, str(KOSTEN_PY), *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout, r.stderr


def test_cli_meldet_summe_und_dedup(tmp_path):
    t = tmp_path / "s.jsonl"
    t.write_text("\n".join([_satz("m1", ein=1_000_000, aus=1_000_000),
                            _satz("m1", ein=1_000_000, aus=1_000_000),
                            _satz("m2", lesen=1_000_000)]) + "\n",
                 encoding="utf-8")
    rc, out, err = _cli(tmp_path, "sitzung-messen", str(t))
    assert "Antworten: 2" in out, out
    assert "Duplikate verworfen: 1" in out, out
    # m1: 5 + 25 = 30 ; m2: 1 Mio cache_read zu 0,1x5 = 0,50
    assert "GESAMT: 30.5000 USD" in out, out
    assert "Abo-Gegenwert" in out, "der Wert wird als abgerechnet ausgegeben"
    assert rc == 0, err


def test_cli_bricht_bei_veralteter_preistabelle_nicht_still_ab(tmp_path):
    """Der Fall, der BL-141 traegt: Die Zahl kommt trotzdem, aber sie ist als
    UNGEEICHT markiert und der Exit-Code sagt es auch."""
    _log(tmp_path / ".ralph-logs" / "b.json", 45.00,
         {"claude-opus-5": {"inputTokens": 1_000_000,
                            "outputTokens": 1_000_000}})
    t = tmp_path / "s.jsonl"
    t.write_text(_satz("m1", ein=1_000_000) + "\n", encoding="utf-8")
    rc, out, err = _cli(tmp_path, "sitzung-messen", str(t))
    assert "Preistabelle stimmt nicht mehr" in err, err
    assert "UNGEEICHT" in err, err
    assert "GESAMT:" in out, "die Zahl fehlt ganz — gemeldet, nicht verschluckt"
    assert rc == 2, f"ein ungeeichter Lauf muss sich im Exit-Code zeigen: {rc}"


def test_cli_quittiert_eine_stimmige_tabelle_ausdruecklich(tmp_path):
    """Gegenrichtung: Eine Meldung, die immer erscheint, ist keine (BL-14)."""
    _log(tmp_path / ".ralph-logs" / "a.json", 30.00,
         {"claude-opus-5": {"inputTokens": 1_000_000,
                            "outputTokens": 1_000_000}})
    t = tmp_path / "s.jsonl"
    t.write_text(_satz("m1", ein=1_000_000) + "\n", encoding="utf-8")
    rc, out, err = _cli(tmp_path, "sitzung-messen", str(t))
    assert "Preistabelle geeicht an 1" in out, out
    assert "stimmt nicht mehr" not in err, err
    assert rc == 0, err


def test_churn_zeile_heisst_nicht_mehr_geschaetzt():
    """BL-141, Mindestmass: Der alte Text liess offen, WORAUS geschaetzt wurde,
    und lud im Feld dazu ein, die Zahl fuer eine Messung zu halten."""
    lib = kit_pfad("lib.sh")
    if not lib.is_file():
        return
    text = lib.read_text(encoding="utf-8")
    assert "Churn-Proxy" in text, "die Beschriftung ist nicht nachgezogen"
    assert "\\tgeschätzt" not in text, (
        "die alte Beschriftung steht noch — sie behauptet eine Schaetzung, "
        "ohne zu sagen, woraus")

#!/usr/bin/env python3
"""Regel-Inventar gegen die Regeldatei-Vorlage prüfen (A.10, BL-56).

Der Sicherheitsgurt vor dem Umbau: A.10 verlangt, JEDE Aussage der Regeldatei
als NORM (geltendes Recht), HERLEITUNG (warum) oder HISTORIE (wann gebaut) zu
klassifizieren — und einen dauerhaften Test, der zwei Dinge sichert:

  1. Jedes NORM-Zitat kommt wörtlich in der Regeldatei vor.
  2. Jeder Abschnitt der Regeldatei ist im Inventar vertreten.

Damit verbietet der Gurt keine Änderung, er macht sie SICHTBAR: Wer eine Regel
umformuliert oder streicht, bekommt hier rot und muss die Inventarzeile
BENANNT nachziehen, statt sie stillschweigend verschwinden zu lassen. Genau
das hat im Feld gehalten, als BL-55 eine Regel bewusst umkehrte (A.10).

Kit-only: Der Prüfer liegt in der Kit-Wurzel, die der Installer nicht kopiert.
Er bewacht die VORLAGE, nicht die installierte CLAUDE.md — ein Feldprojekt darf
seine Regeln umformulieren (so hält es test_bl55 ausdrücklich fest), die Vorlage
darf es nicht unbemerkt.

Aufruf:  python3 kit-regelinventar.py [--zeige-fehlende]
Exit:    0 = grün, 1 = Inventar und Regeldatei stehen auseinander
"""

import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent
REGELDATEI = WURZEL / "bootstrap" / "CLAUDE.md.vorlage"
INVENTAR = WURZEL / "doku" / "regel-inventar.md"

KLASSEN = ("NORM", "HERLEITUNG", "HISTORIE")

# Traeger = die Datei, die eine Aussage AUSLIEFERT. Solange alles in der
# Regeldatei stand, war die Spalte ueberfluessig; mit dem Dreischnitt (BL-56)
# wandern Regeln in die Rollen-Briefings, und ohne Traeger-Spalte ginge jede
# verschobene NORM rot — der Gurt wuerde den Umbau blockieren, statt ihn
# sichtbar zu machen. Die Spalte macht den Wechsel zu dem, was A.10 verlangt:
# einer BENANNT nachgezogenen Inventarzeile.
TRAEGER = {
    "Regeldatei": REGELDATEI,
    "TEAM.md": WURZEL / "bootstrap" / "TEAM.md",
    "rolle-architekt": WURZEL / "team" / "prompts" / "rolle-architekt.md",
    "rolle-ralph": WURZEL / "team" / "prompts" / "rolle-ralph.md",
    "rolle-harry": WURZEL / "team" / "prompts" / "rolle-harry.md",
    "rolle-marv": WURZEL / "team" / "prompts" / "rolle-marv.md",
    "rolle-frank": WURZEL / "team" / "prompts" / "rolle-frank.md",
    "rolle-axel": WURZEL / "team" / "prompts" / "rolle-axel.md",
}


def normalisiere(text):
    """Vergleichsform für Zitate.

    Drei Eingriffe, jeder aus einem realen Fehlalarm heraus:
    - Blockquote-Marker entfernen: Die halbe Regeldatei steht in `> `-Blöcken;
      ein Zitat müsste sonst die Zeilenumbrüche des Originals mitführen.
    - Betonungszeichen entfernen: Ein `**nie**` mitten im Satz ließe sonst ein
      wörtlich richtiges Zitat scheitern (dieselbe Vorsichtsmaßnahme wie in
      test_bl55_kostenmessung.py).
    - Whitespace kollabieren: Der Zeilenumbruch des Originals ist Satzform,
      keine Aussage.
    """
    text = re.sub(r"(?m)^[ \t]*>[ \t]?", "", text)
    text = re.sub(r"[*_`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def abschnitte_der_regeldatei(text):
    """Alle `## `-Überschriften — ohne die in ```-Blöcken.

    Die Regeldatei zeigt die Gliederung des Abschluss-Docs als Codeblock; deren
    `## 1. Ist-Stand`-Zeilen sind Beispieltext, keine Abschnitte. Wer den Fence
    nicht auswertet, verlangt für sie Inventarzeilen, die es nie geben wird.
    """
    gefunden, im_fence = [], False
    for zeile in text.splitlines():
        if zeile.lstrip().startswith("```"):
            im_fence = not im_fence
            continue
        if not im_fence and zeile.startswith("## "):
            gefunden.append(zeile[3:].strip())
    return gefunden


def lies_inventar(text):
    """Tabellenzeilen `| Abschnitt | Klasse | Träger | Zitat |` einlesen."""
    eintraege = []
    for nr, zeile in enumerate(text.splitlines(), 1):
        if not zeile.startswith("|"):
            continue
        felder = [f.strip() for f in zeile.strip().strip("|").split("|")]
        if len(felder) != 4:
            continue
        abschnitt, klasse, traeger, zitat = felder
        if klasse not in KLASSEN:
            continue  # Kopf- und Trennzeilen
        eintraege.append({"zeile": nr, "abschnitt": abschnitt,
                          "klasse": klasse, "traeger": traeger,
                          "zitat": zitat})
    return eintraege


def main():
    zeige_fehlende = "--zeige-fehlende" in sys.argv

    for pfad in (REGELDATEI, INVENTAR):
        if not pfad.is_file():
            print(f"✗ fehlt: {pfad.relative_to(WURZEL)}", file=sys.stderr)
            return 1

    regeltext = REGELDATEI.read_text(encoding="utf-8")
    inventartext = INVENTAR.read_text(encoding="utf-8")

    eintraege = lies_inventar(inventartext)
    if not eintraege:
        print("✗ Inventar enthält keine auswertbaren Zeilen", file=sys.stderr)
        return 1

    fehler = []

    # Träger einmal einlesen und normalisiert vorhalten.
    inhalt = {}
    for name, pfad in TRAEGER.items():
        if pfad.is_file():
            inhalt[name] = normalisiere(pfad.read_text(encoding="utf-8"))

    # 1. Jedes NORM-Zitat muss wörtlich in SEINEM Träger stehen.
    normen = [e for e in eintraege if e["klasse"] == "NORM"]
    for e in normen:
        traeger = e["traeger"]
        if traeger not in TRAEGER:
            fehler.append(
                f"unbekannter Träger „{traeger}\" (Inventar Z. {e['zeile']}) — "
                f"erlaubt: {', '.join(sorted(TRAEGER))}")
            continue
        if traeger not in inhalt:
            fehler.append(f"Träger-Datei fehlt: "
                          f"{TRAEGER[traeger].relative_to(WURZEL)}")
            continue
        if normalisiere(e["zitat"]) not in inhalt[traeger]:
            fehler.append(
                f"NORM-Zitat steht nicht (mehr) in „{traeger}\" "
                f"(Inventar Z. {e['zeile']}, Abschnitt „{e['abschnitt']}\"):\n"
                f"      {e['zitat'][:120]}")

    # 2. Jeder Abschnitt der Regeldatei muss im Inventar vorkommen.
    #    Verglichen wird normalisiert: Überschriften tragen doppelte
    #    Leerzeichen und Betonungen (`**und**`), die byte-genau abzutippen
    #    nur Fehlalarme erzeugt. Gemeldet wird die Originalschreibweise.
    echte = {normalisiere(a): a for a in abschnitte_der_regeldatei(regeltext)}
    inventarisiert = {normalisiere(e["abschnitt"]): e["abschnitt"]
                      for e in eintraege}
    for schluessel, original in echte.items():
        if schluessel not in inventarisiert:
            fehler.append(f"Abschnitt ohne Inventarzeile: „{original}\"")

    # 3. Gegenrichtung: ein Inventar-Abschnitt, den es nicht mehr gibt, ist
    #    eine Leiche — sie täuscht Abdeckung vor, die keine ist.
    for schluessel in sorted(set(inventarisiert) - set(echte)):
        fehler.append(f"Inventar nennt einen Abschnitt, den die Regeldatei "
                      f"nicht (mehr) hat: „{inventarisiert[schluessel]}\"")

    if fehler:
        print(f"✗ Regel-Inventar und Regeldatei stehen auseinander "
              f"({len(fehler)} Befund(e)):", file=sys.stderr)
        for f in fehler:
            print(f"    · {f}", file=sys.stderr)
        print("\n  Das ist KEIN Verbot der Änderung — es verlangt, die "
              "betroffene\n  Inventarzeile benannt nachzuziehen (A.10).",
              file=sys.stderr)
        return 1

    verteilung = {k: sum(1 for e in eintraege if e["klasse"] == k)
                  for k in KLASSEN}
    print(f"✓ Regel-Inventar deckt {len(echte)} Abschnitte, "
          f"{len(eintraege)} Aussagen "
          f"(NORM {verteilung['NORM']}, HERLEITUNG {verteilung['HERLEITUNG']}, "
          f"HISTORIE {verteilung['HISTORIE']}) — alle NORM-Zitate wörtlich "
          f"belegt.")
    if zeige_fehlende:
        # Beidseitig normalisiert vergleichen — sonst zählt jeder Abschnitt
        # mit Betonung oder doppeltem Leerzeichen in der Überschrift null,
        # und die Diagnose meldet Lücken, die es nicht gibt.
        for schluessel, original in sorted(echte.items()):
            n = sum(1 for e in eintraege
                    if normalisiere(e["abschnitt"]) == schluessel)
            print(f"    {n:2d}  {original}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

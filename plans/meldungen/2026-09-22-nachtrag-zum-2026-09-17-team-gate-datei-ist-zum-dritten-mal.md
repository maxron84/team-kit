# Nachtrag zum 2026-09-17: TEAM_GATE_DATEI ist zum dritten Mal aufgetreten, und die Gattung laesst sich in zwoelf Zeilen pruefen

- **Bezug**: BL-94
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python und Electron,
  30 Kaskaden gebaut, rund 260 Testdateien.

## Was passiert ist

Dies ist ein Nachtrag zur Meldung vom 2026-09-17
(`2026-09-17-team-gate-datei-wird-nicht-exportiert-die-gate-meldung-aus-b.md`).
Der Hergang steht dort und wird hier nicht wiederholt. Neu sind drei Dinge:
der **dritte Vorfall**, der **bezifferte Schaden** und eine **Gattungsprüfung,
die ausgeführt ist**.

**Der dritte Vorfall.** Der Abschlussbericht ist am 2026-09-22 am Ende der
Kaskade 30 erneut an derselben Stelle abgestürzt — nach dem Ende der Kaskade 25
und dem der Kaskade 26. Für dieses Projekt ist es damit kein Einzelfall mehr,
sondern das Verhalten jedes roten Laufs.

## Warum der Schaden größer ist als eine fehlende Zeile

Die Meldung vom 17.09. beschreibt den Absturz. Was sie noch nicht beziffern
konnte, ist die **Entscheidung**, die dem Menschen dadurch fehlt.

Die Gate-Datei dieses Laufs trug elf Zeilen. Gelesen hat sie niemand — der
Bericht bricht ja vor der Ausgabe ab. Nachträglich von Hand gelesen, sagen
sie geschlossen dasselbe:

    ... | ralph (stufe152) | tests/test_stufe1_smoke.py::test_version_ist_gesetzt
          (pre-existing, .venv-Paketmetadaten 0.14.0 hinter pyproject.toml /
          _version.py 0.15.0 zurueck; Stufe 152 beruehrt keine Versionsdateien)

Alle elf Zeilen nennen **zwei vorbestehende** Fehlschläge: einen
Versionsvergleich, der an einem nicht nachgezogenen `pip install -e .` hängt,
und einen bekannten Flake unter Parallellast. **Keiner** davon stammt aus dem
Lauf, der hier abbricht. Die Rollen haben das pflichtgemäß in jede Zeile
geschrieben — `BL-256` funktioniert also genau wie gebaut.

**Nur kommt es nicht an.** Der Mensch sieht `GATE ROT`, Exit 44, keinen
Testnamen und keinen Dateinamen, und muss den Baum von Hand nachfahren, um zu
erfahren, was die Rollen bereits aufgeschrieben hatten. Die Zeile, die
`BL-256` kostbar macht — *„vorbestehend, unberührt von dieser Stufe"* — ist
genau die, die der Absturz verschluckt. **Der Fehler entwertet damit nicht den
Bericht, sondern die Mechanik, die er berichten soll.**

Erschwerend: Ein Flake unter Parallellast (in unserem Feldbacklog erfasst,
nicht im Kit-Backlog) setzt die Gate-Datei, **ohne dass etwas kaputt ist**.
Der Mensch bekommt dann einen abgestürzten Bericht über ein rotes Gate, das
keines sein müsste.

## Wo es steckt

Unverändert wie am 17.09.: `pwsh/lib.psm1`:317 setzt

    $TEAM_GATE_DATEI = Team-Default 'TEAM_GATE_DATEI' '.team-gate-rot'

und die Liste in `Export-ModuleMember -Function * -Variable @( … )` führt den
Namen nicht. `pwsh/entry/vollautomatik.ps1`:546 und :552 lesen ihn.
Am 2026-09-22 im Kit-Arbeitsbaum nachgesehen: **der Fix ist dort noch nicht
eingebaut** — die Meldung vom 17.09. ist angekommen, die Zeile fehlt
weiterhin.

## Warum das jede Installation trifft

Der Fehler steckt in `pwsh/lib.psm1` und `pwsh/entry/vollautomatik.ps1`, also
im Kit. Auf der bash-Bahn gibt es die Modulgrenze nicht (`source` legt alles in
dieselbe Shell), der Fund ist dort strukturell unsichtbar — dieselbe Lage, die
der Kommentar zu `BL-182` drei Zeilen über der Lücke bereits beschreibt.

## Der eigentliche Vorschlag: die GATTUNG prüfen, nicht den Fall

`BL-182` hat dieselbe Bauform schon einmal abgestellt, für `TEAM_KIT_PFAD`.
Die **Gattung** blieb offen, und sie ist über `BL-256` zurückgekehrt. Sie wird
wiederkehren, sobald die nächste Modulvariable dazukommt — **lautlos**, weil
PowerShell eine nicht exportierte Variable zu `$null` auflöst, statt zu klagen.
Ein Test, der nur `TEAM_GATE_DATEI` prüft, beweist nach der Achse **Menge**
nichts über die Menge.

Die Prüfung ist billig. Hier ist sie vollständig — kein Platzhalter, so
ausgeführt:

    import re, glob, os

    def ohne_kommentare(pfad):
        # Bewusst konservativ: ein Kommentar HINTER Code bleibt stehen. Zu
        # wenig wegschneiden erzeugt hoechstens einen Fehlalarm, zu viel
        # dagegen ein falsches Gruen -- und das ist der Ausgang, den diese
        # Pruefung gerade verhindern soll.
        txt = re.sub(r'<#.*?#>', '', open(pfad, encoding='utf-8').read(), flags=re.S)
        return chr(10).join(z for z in txt.split(chr(10))
                            if not z.lstrip().startswith('#'))

    lib = open('pwsh/lib.psm1', encoding='utf-8').read()
    i = lib.rindex('Export-ModuleMember')        # rindex: Zeile 16 ist ein Kommentar
    exportiert = set(re.findall(r"'([A-Za-z_0-9]+)'", lib[i:lib.index(chr(10) + ')', i)]))

    fehlend = []
    for f in glob.glob('pwsh/entry/*.ps1') + glob.glob('pwsh/scripts/*.ps1'):
        if os.path.basename(f).startswith('team.config'):
            continue
        for v in set(re.findall(r'\$(TEAM_[A-Z_0-9]+)', ohne_kommentare(f))):
            if v not in exportiert:
                fehlend.append((os.path.basename(f), v))
    assert not fehlend, fehlend

**In beide Richtungen gemessen, nicht nur behauptet** — die Frage vor jeder
Zusicherung ist ja, *womit sie ROT wird*:

| Stand | Exportliste | Ergebnis |
|---|---|---|
| Kit-Arbeitsbaum vom 2026-09-22, unverändert | 47 Namen | **1 Treffer**: `TEAM_GATE_DATEI` in `vollautomatik.ps1` |
| dieselbe Kopie, nur die eine Zeile ergänzt | 48 Namen | **grün** |

Die Gattung ist damit heute sonst geschlossen: Der Test wird mit dem
Einzeiler-Fix grün und bleibt es, bis jemand die nächste Variable vergisst.
Das ist der Punkt.

**Zwei Fallen, beide beim Bauen selbst aufgelaufen** — sie sind der Grund,
warum diese Meldung den Test ausformuliert statt ihn nur vorzuschlagen:

1. **`rindex`, nicht `index`.** `lib.psm1` erwähnt `Export-ModuleMember` in
   Zeile 16 in einem Kommentar. Die erste Fassung fand diese Erwähnung, las
   den halben Modulkopf als Exportliste, kam auf 81 statt 47 Namen — und
   meldete **grün**. Eine Gegenprobe, die die eigene Doku mitliest, ist eine
   Probe der Achse Menge, die ihre Menge falsch bildet.
2. **Kommentare ausblenden** (oben `ohne_kommentare()`). Ohne das meldet die
   Pruefung `$TEAM_PYTHON` in
   `pwsh/entry/kit-melden.ps1`:65 — eine Erwähnung in dem Kommentar, der
   **genau diesen Fund für `BL-182` beschreibt**. Der Test würde also an der
   Dokumentation seines eigenen Anlasses rot. Die Bauform ist uns im Feld
   teuer geworden: Unser Geheimnis-Scanner löste an einem einzigen Tag
   viermal aus, jedes Mal an der **Beschreibung** einer Bauform, und jede
   Runde entstand beim Dokumentieren der vorigen — zuletzt meldete er den
   Satz, der erklärt, wie man es richtig schreibt. Unsere Regel daraus: **am
   Zeilenmuster erweitern, nie am Pfad ausschließen** — ein Ausschluss für
   `kit-melden.ps1` machte die Datei blind.

## Was ich schon versucht habe

Projektlokal die eine Zeile in die Exportliste eingetragen, mit einem
Kommentar, der auf diese Meldung zeigt. Der Fix hat die bekannte Verfallszeit
(`BL-42`/`BL-58`) — er steht auf unserer Nachpflege-Liste für das nächste
`--update`.

Belegt ist er auf der Achse **Ausführung**, mit Kontrollgruppe: nach dem
Import liefert `$TEAM_GATE_DATEI` im Entrypoint `.team-gate-rot`, während die
nicht exportierte Kontrollvariable `$TEAM_GUARD_HASH` unverändert `$null`
bleibt — der Export wirkt also gezielt und nicht pauschal. Anschließend den
Codepfad aus `vollautomatik.ps1`:542-553 nachgespielt: elf Zeilen Fundliste
und der Dateiname kommen an, der Satz hat kein Loch mehr.

**Der Fix im Kit bleibt eine Zeile.** Was wir uns wünschen, ist der Test
darüber.

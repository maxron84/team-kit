# kosten.py sitzung-messen --projekt findet auf Windows nie ein Transkript

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-08-26-kosten-py-sitzung-messen-projekt-findet-auf-windows-nie-ein.md
      .\kit-melden.cmd senden   2026-08-26-kosten-py-sitzung-messen-projekt-findet-auf-windows-nie-ein.md

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn (`--nur-pwsh`), Python +
  Electron, dritte Kaskade abgeschlossen

## Was passiert ist

Im Architekten-Closeout gehoert die eigene Sitzung gebucht. Das Briefing nennt
dafuer genau einen Befehl, und der Uebergabezettel der Kaskade hatte ihn als
Pflichtschritt notiert:

```
python team/tools/kosten.py sitzung-messen --projekt .
Fehler: kein Transkript zu . gefunden
```

Mit absolutem Pfad dasselbe:

```
python team/tools/kosten.py sitzung-messen --projekt C:/.../<projekt>
Fehler: kein Transkript zu C:/.../<projekt> gefunden
```

Die Transkripte **sind** da — 36 Dateien im Projektordner unter
`~/.claude/projects/`, darunter die Sitzung, die den Befehl gerade absetzt.

**Der Exit-Code ist dabei 0.** Der Aufruf sieht also nicht nach einem Fehler
aus, sondern nach „nichts zu messen".

## Wo es steckt

`team/tools/kosten.py`, Funktion `transkripte_aus_projekt()`:

```python
voll = os.path.abspath(os.path.expanduser(projektpfad))
ordner = os.path.join(wurzel, voll.replace(os.sep, "-").replace("_", "-"))
```

Ersetzt werden nur Trennzeichen und Unterstrich. Auf Windows bleibt damit
zweierlei stehen, was die CLI beim Anlegen des Ordners umschreibt:

1. **Der Doppelpunkt des Laufwerks.** Die CLI macht aus `C:\` den Praefix
   `c--`; die Funktion erzeugt `C:-`.
2. **Die Grossschreibung des Laufwerksbuchstabens.** Die CLI schreibt `c`,
   die Funktion `C`.

Gesucht wird also `C:-Users-...`, der Ordner heisst `c--Users-...`. Auf
Linux/macOS faellt das nicht auf, weil dort kein Doppelpunkt im Pfad steht.

## Warum das jede Installation trifft

Es steckt in `team/tools/kosten.py`, also im Kit selbst, und trifft **jede**
Windows-Installation — unabhaengig von Projekt, Bahn und Modell. Betroffen ist
kein Randweg, sondern der einzige Befehl, den das Architekten-Briefing fuer die
Frage „woher kommt `<USD>`?" nennt.

**Die Bauform ist die gefaehrlichere Haelfte:** Das Ergebnis ist eine leere
Liste, keine Ausnahme. Die Meldung lautet „kein Transkript gefunden" und liest
sich wie eine Aussage ueber die Welt, ist aber eine ueber einen falsch
gebildeten Pfad. Wer ihr glaubt, schliesst daraus, es gebe nichts zu buchen,
und die Architektenkosten bleiben **strukturell unerfasst** — genau der
Zustand, den der Kostenabschluss verhindern soll. Das Kit warnt an anderer
Stelle ausdruecklich vor Waechtern, die ueber einem leeren Ergebnis gruen
melden; hier ist einer.

**Zweiter Punkt, unabhaengig vom Betriebssystem:** Die Funktion liefert per
`max(dateien, key=os.path.getmtime)` nur das **zuletzt geaenderte** Transkript,
ihr Docstring und die Nutzungszeile sprechen aber im Plural. Erstreckt sich
eine Kaskade ueber mehrere Sitzungen — der Normalfall, sobald Planung und
Closeout getrennt laufen —, misst der Aufruf stillschweigend nur die letzte.

## Was ich schon versucht habe

- `--projekt .` und `--projekt <absoluter Pfad>`: beide Male dieselbe leere
  Meldung.
- **Umgehung, die traegt:** die Transkriptpfade direkt uebergeben
  (`sitzung-messen <datei> <datei>`). Das funktioniert einwandfrei, die
  Eichung an den abgerechneten headless-Laeufen meldet gruen.
- Die Zuordnung, welches Transkript zu welcher Sitzung gehoert, war dann
  Handarbeit. Ein Hinweis, der anderen Zeit spart: **die Zeitstempel in den
  Transkripten sind UTC**, die Commit-Zeiten lokal. Erst nach dieser
  Umrechnung liessen sich die headless-Rollensitzungen des Laufs (eine je
  Stufe und je Rolle, hier 11 Stueck) von den interaktiven Architektensitzungen
  trennen — beide liegen im selben Ordner, und nur die interaktiven duerfen als
  Architektenkosten gebucht werden.

**Vorschlag:** Den Slug so bilden, wie die CLI ihn bildet — Laufwerksbuchstaben
kleinschreiben und den Doppelpunkt wie ein Trennzeichen behandeln. Und wenn der
Ordner fehlt, die Meldung um den **gesuchten Pfad** ergaenzen; dann steht der
Fehler in der Meldung selbst.

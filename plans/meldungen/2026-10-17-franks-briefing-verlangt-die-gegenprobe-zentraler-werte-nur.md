# Franks Briefing verlangt die Gegenprobe zentraler Werte nur bei geaendertem Wert und dann eine gruene Suite

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-17-franks-briefing-verlangt-die-gegenprobe-zentraler-werte-nur.md
      ./kit-melden.sh ablegen  2026-10-17-franks-briefing-verlangt-die-gegenprobe-zentraler-werte-nur.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-17-franks-briefing-verlangt-die-gegenprobe-zentraler-werte-nur.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-16
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; vierte Kaskade, ein Mensch und die Rollen in einem Arbeitsbaum

## Was passiert ist

In zwei Kaskaden in Folge hat Frank einen Fund aus Fremddaten mit einer neuen
Längengrenze gefixt: einer Konstante, deren Verbraucher im selben Fix entsteht.
Beide Male lief keine Gegenprobe gegen zwei fremde Werte.

- **Dritte Kaskade:** eine Grenze von 18 Ziffern für Versionszahlen aus der
  Ausgabe von Detect It Easy. Die Quittung erwähnt keine Probe. Im Closeout
  nachgeholt: Grenze auf 4 → drei Tests inhaltlich rot. Grenze auf 100000 → nur
  der Test, der den Code-Stand der Berichte prüft.
- **Vierte Kaskade:** eine Grenze von 30 Zeichen für Zahl-Token, die ein
  Vorfilter aus dem Dekompilat liest. Franks Quittung wörtlich: „Eine
  Gegenprobe mit zwei fremden Werten war nicht nötig, weil `_MAX_ZIFFERN` eine
  neue Konstante ist, die vorher nichts las.“ Im Closeout nachgeholt: Grenze auf
  10000 → 2 Tests rot. Grenze auf 5 → 11 rot. Die Textsuche findet den Namen in
  keinem Test. Die Probe hat also Kopplungen gezeigt, die ohne sie niemand
  kennt.

Beide Fixe sind richtig. Es fehlt jeweils der Nachweis, welche Tests an der
Grenze hängen.

## Wo es steckt

`team/prompts/rolle-frank.md`, Absatz „Wenn mein Fix einen zentralen Wert
ändert …“. Zwei Stellen widersprechen der Regel in `CLAUDE.md` („Zentrale Werte
gehören gegengeprobt, nicht gegrept“):

1. **„ändert“.** Ein neu eingeführter Wert fällt heraus, auch wenn sein
   Verbraucher im selben Fix entsteht. Die Regel sagt das Gegenteil („WANN sie
   gehört dazu“, Kit-BL-167): Die Probe gehört dorthin, wo der Wert einen
   Verbraucher hat. Bei einem Fix fallen Einführung und Verbraucher zusammen.
   Franks Begründung folgt dem Wortlaut seines Briefings.
2. **„Suite beide Male grün“.** Die Regel zählt die **roten** Stellen: Findet
   das Verstellen weniger oder gleich viele rote Stellen, als die Textsuche
   Fundstellen nennt, hat es nichts geprüft. Halten die Tests eines Fixes das
   Verhalten an der Grenze fest, werden sie beim Verstellen rot, und das ist
   der Beleg. Wer „beide Male grün“ wörtlich nimmt, muss die Tests aufweichen
   oder die Probe weglassen.

## Warum das jede Installation trifft

Das Briefing ist Kit-Text, jede Installation trägt denselben Wortlaut. Eine
Grenze gegen Fremddaten ist der häufigste neue zentrale Wert in einem Fix:
Beide Feldfälle hier sind solche Grenzen, und das Red Team erzeugt genau diese
Funde. Ohne Probe bleibt unbekannt, welche Tests beim nächsten Verstellen an
unerwarteter Stelle rot werden.

## Was ich schon versucht habe

Projektseitig fährt der Architekt die Gegenprobe im Closeout nach, in beiden
Kaskaden mit Zahlen im Abschluss-Doc. Lokal geändert ist nichts; das Briefing
gehört dem Kit.

Vorschlag für den Absatz in `rolle-frank.md`:

> **Führt mein Fix einen zentralen Wert ein oder ändert er einen** (Konstante,
> Default, Schwellwert, Grenze), fahre ich ihn probeweise auf zwei fremde Werte,
> einen höheren und einen niedrigeren. Je Verstellung zähle ich die roten Tests
> und schreibe die Zahl in den Commit-Text; danach setze ich den Wert
> nachweislich zurück. Findet das Verstellen nicht mehr rote Stellen, als die
> Textsuche nach Name und Wert nennt, hat es nichts geprüft — dann fehlt ein
> Test, der die Grenze festhält.

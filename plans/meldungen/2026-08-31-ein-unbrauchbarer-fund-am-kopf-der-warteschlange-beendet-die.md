# Ein unbrauchbarer Fund am Kopf der Warteschlange beendet die ganze Fix-Phase — die dahinter liegenden Funde werden nie gesehen

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, sechste Kaskade

## Was passiert ist

Am Ende eines Vollautomatik-Laufs standen **zwei** frische Funde auf
`an Frank übergeben` — einer von Harry, einer von Marv. Dem Harry-Fund fehlte
die seit `BL-15` pflichtige `- **Reproducer-Test**:`-Zeile. Die Fix-Phase
protokollierte:

```
[HM-23] keine `- **Reproducer-Test**:`-Zeile (Pflicht seit BL-15) — ohne sie kennt niemand den Namen, unter dem die Absicherung entstehen soll.
[frank] HM-23 ist als Auftrag unbrauchbar (siehe oben) — KEIN Aufruf, kein Fehlversuch.
  Der Fundblock gehört nachgebessert (Harry/Marv/Architekt), dann erneut starten.
Runde 1: nichts mehr zu tun — Fix-Phase beendet.
```

Der **zweite** Fund war formal einwandfrei und wäre sofort fixbar gewesen. Er
wurde nie betrachtet. Der anschließende Abschlussbericht führte ihn unter
`an Frank übergeben 2` auf — ohne Warnung, ohne Hinweis darauf, dass die
Fix-Phase gar nicht bis zu ihm gekommen war. Gelesen hat sich der Lauf wie ein
sauberer Abschluss: „nichts mehr zu tun".

## Wo es steckt

Zwei Stellen greifen ineinander:

1. `frank.ps1` (Zeilen ~42–66, gleichlautend in der bash-Bahn): Der Auftrag
   wird über `beutebuch first 'an Frank übergeben'` geholt — das liefert
   **immer** den ersten Treffer der Datei. Fällt der Lint darauf durch, endet
   die Rolle mit `exit 3`. Es gibt keinen Weg, den nächsten Kandidaten zu
   holen.
2. `vollautomatik.ps1` (Phase 4, Zeilen ~279–309): `exit 3` setzt `$getan = 0`,
   und `if ($getan -eq 0) { … "nichts mehr zu tun" … break }`. Damit ist
   „unbrauchbarer Auftrag" für die Schleife nicht vom Zustand „Warteschlange
   leer" unterscheidbar.

`exit 3` trägt beide Bedeutungen: „nichts zu tun" (Zeile 48) und
„Auftrag unbrauchbar" (Zeile 66). Die Schleife kann sie nicht trennen, weil
sie denselben Code sieht.

## Warum das jede Installation trifft

Der Fehler steckt in `frank.*` und `vollautomatik.*`, also im Kit selbst. Er
tritt in jedem Lauf auf, in dem ein Sweep einen formal unvollständigen Fund
committet — und genau dafür existiert der Lint. Die Kombination ist damit kein
Ausnahmefall, sondern der vorgesehene Betriebszustand:

- Der Lint **soll** unvollständige Funde abweisen (`BL-15`).
- Sweeps schreiben ihre Funde **ohne** Gegenlesen ins Beutebuch.
- Also steht früher oder später ein solcher Fund im Beutebuch, und ab dann ist
  jeder Fund **hinter** ihm für die Automatik unsichtbar — dauerhaft, denn
  `first` liefert bei jedem weiteren Lauf wieder denselben Kopf.

Verschärfend: Der Fund am Kopf war ein **mittlerer**, der blockierte ein
weiterer **mittlerer**. Wäre der blockierte ein kritischer gewesen, hätte der
Lauf einen kritischen Fund stillschweigend übersprungen und trotzdem
„Fix-Phase beendet" gemeldet.

## Zweiter, kleinerer Befund derselben Kaskade

`beutebuch.py lint` prüft auf **Vorhandensein** der `Reproducer-Test`-Zeile,
nicht auf ihre **Eindeutigkeit**. Im selben Lauf hatte der zweite Sweep die
fehlende Zeile des ersten Fundes bemerkt und nachgetragen — aber an das Ende
**seines eigenen** Fundblocks. Der Block trug damit zwei
`- **Reproducer-Test**:`-Zeilen (eine davon mit dem Testnamen eines fremden
Fundes), und `lint` meldete für **beide** Funde: sauber für den einen (er hat
ja eine Zeile), unbrauchbar für den anderen (dort fehlt sie weiter). Ein
`lint`, der eine zweite Zeile im selben Block meldet, hätte die Fehlablage
sofort gezeigt.

## Lösungsrichtungen

1. **Eigener Exit-Code für „unbrauchbar".** `frank.*` gibt für den
   Lint-Fehlschlag z. B. `exit 5` statt `exit 3`. Die Schleife behandelt ihn
   wie einen Fehlversuch (kein `break`), zählt ihn aber in die
   Stagnations-Bremse — der Lauf dreht dann höchstens `TEAM_FIX_MAX_STAGNATION`
   Runden leer und meldet den Fund benannt, statt ihn zu verschweigen.
2. **`first` überspringt unbrauchbare Köpfe.** `beutebuch.py first <status>`
   bekommt ein `--lint-ok`, das nur Funde liefert, die den Lint bestehen.
   Damit arbeitet die Fix-Phase die Warteschlange zu Ende und lässt allein die
   defekten Blöcke liegen. Der Abschlussbericht sollte sie dann ausdrücklich
   nennen.
3. **Der Abschlussbericht wird ehrlich.** Unabhängig von 1./2.: Beendet die
   Fix-Phase mit `an Frank übergeben > 0` im Beutebuch, gehört das als Warnung
   in den Bericht — „2 Funde bleiben offen" ist eine andere Aussage als
   „nichts mehr zu tun".
4. **`lint` meldet doppelte `Reproducer-Test`-Zeilen** in einem Fundblock.

Die Richtungen 1 und 2 schließen einander nicht aus; 2 allein ändert nichts
daran, dass `exit 3` zwei Bedeutungen trägt.

## Was ich schon versucht habe

Im Projekt von Hand nachgebessert: Die fehlplatzierte `Reproducer-Test`-Zeile
in den richtigen Fundblock verschoben, danach `lint` für beide Funde sauber,
`first 'an Frank übergeben'` liefert wieder einen brauchbaren Auftrag. Das ist
eine Reparatur der **Daten**, kein Fix des Kits — beim nächsten unvollständig
geschriebenen Fund tritt derselbe Ablauf erneut ein.

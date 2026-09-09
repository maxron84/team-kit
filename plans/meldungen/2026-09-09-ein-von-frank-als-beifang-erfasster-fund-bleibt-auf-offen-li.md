# Ein von Frank als Beifang erfasster Fund bleibt auf offen liegen und die Fixphase meldet nichts zu tun

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst mit
  Electron-Oberfläche, ~630 Tests, fünfzehnte Kaskade

## Was passiert ist

In der Fixphase eines Vollautomatik-Laufs hat Frank beim Fixen eines
Red-Team-Fundes einen **zweiten, gleichartigen Fund an einer anderen Stelle**
bemerkt. Er hat sich regelkonform verhalten — **Finder ≠ Fixer** — und den
Beifang als eigenen Fund ins Beutebuch eingetragen, mit vollständigen
Reproschritten, Schweregrad und reservierter Reproducer-Testdatei.

Der neue Fund bekam dabei den Status `offen`.

Die Fixphase fragt aber ausschließlich nach `an Frank übergeben` bzw.
`Fix-Plan liegt vor`. Der frisch eingetragene Fund war damit für sie
unsichtbar, und der Lauf endete mit:

```
[frank] Kein Fund mit Status 'an Frank übergeben' / 'Fix-Plan liegt vor' — nichts zu tun.
Runde 3: nichts mehr zu tun — Fix-Phase beendet.
```

**Die Runde war ohnehin leer** — derselbe Lauf hätte den Fund ohne jede
Mehrkosten mitgenommen. Stattdessen blieb ein fixbarer Fund mittlerer Schwere
liegen, und der Lauf sah aus wie ein sauberer Abschluss.

Nachgestellt im Closeout, beide Aufrufe auf demselben Stand:

```
beutebuch.py list                        → der Fund steht da, Status 'offen'
beutebuch.py first 'an Frank übergeben'  → findet ihn NICHT (leer)
```

Nach `beutebuch.py set <Nr> 'an Frank übergeben'` liefert `first` ihn sofort.
Es ist also kein Parser- oder Kodierungsproblem, sondern schlicht der Status.

## Wo es steckt

Zwei Stellen, die zusammen die Lücke bilden:

1. **`team/prompts/rolle-frank.md`** kennt den Fall nicht. Das Briefing
   beschreibt Franks Dreisatz für den Fund, an dem er arbeitet; für einen
   **neu entdeckten** Fund gibt es keine Anweisung — insbesondere keine, mit
   welchem Status er einzutragen ist.
2. **Der Beutezug-Dreisatz in `CLAUDE.md`** weist Schritt 3 (`Status auf
   'an Frank übergeben' setzen`) ausdrücklich **Harry und Marv** zu. Er ist
   Teil des *Beutezugs*. Für einen Fund, den **Frank** erfasst, ist damit
   niemand zuständig — die Statuskette hat für diesen Weg keinen Eintrag.

Die Fixphasen-Schleife selbst verhält sich korrekt; sie fragt genau das ab,
was dokumentiert ist.

## Warum das jede Installation trifft

Beifang ist kein Sonderfall, sondern der **Normalfall** beim Fixen: Wer eine
fehlerhafte Bauform an einer Stelle korrigiert, sieht dieselbe Bauform an der
nächsten. Genau dafür gibt es die Regel „Finder ≠ Fixer" — und wer sie befolgt,
verliert den Fund an den Status `offen`.

Die Bauform ist dieselbe wie in `BL-115` (dort: eine von Hand geschriebene
Statuszeile, die auf keinen Wert der Kette passt): **Der Fund ist in `list`
sichtbar, für `first` unsichtbar, und nichts weist auf den Widerspruch hin.**
Der Abschlussbericht zählt ihn unter „offen" — neben womöglich anderen, längst
bekannten offenen Funden, sodass die Zahl unauffällig bleibt.

Besonders unangenehm ist die Richtung des Fehlers: Er trifft **die
regelkonforme Rolle**. Hätte Frank den Beifang einfach mitgefixt (Regelbruch),
wäre nichts liegen geblieben.

## Was ich schon versucht habe

Im Projekt lokal aufgelöst durch `beutebuch.py set <Nr> 'an Frank übergeben'`
im Closeout — das ist Handarbeit nach dem Lauf und hat eine Verfallszeit, weil
sie beim nächsten Lauf wieder anfällt.

**Vorschläge, in der Reihenfolge meiner Präferenz:**

1. **Franks Briefing ergänzen**: Einen Beifang trägt er mit Status
   `an Frank übergeben` ein, nicht `offen`. Billigste Lösung, keine
   Code-Änderung, und sie greift schon in derselben Fixphase — die
   Auslauf-Bremse sorgt dafür, dass die Schleife nicht endlos wird.
2. **`beutebuch.py` beim Anlegen eines Fundes durch eine *fixende* Rolle den
   Status vorbelegen**, statt ihn auf `offen` zu lassen.
3. **Den Abschlussbericht schärfen**: „offen" als Zahl ist zu stumpf. Ein
   Fund, der **in diesem Lauf** entstanden und nicht bearbeitet worden ist,
   gehört als eigene Zeile in den Bericht — sonst verschwindet er zwischen
   den bekannten Altfällen.

Punkt 3 ist unabhängig vom Rest nützlich; er ist die Gegenrichtung zu
`BL-31`/dem verfallenen Fokus, der aus demselben Grund unbemerkt blieb: Was
mitten im Lauf protokolliert wird, liest niemand.

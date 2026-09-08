# Die Fixphase hat keinen Einzeleinstieg - wer nur fixen will, zahlt zwei Sweeps oder ruft Frank ohne Axel

- **Art**: Verbesserungsvorschlag
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (zwölf Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 500 Tests.

## Was passiert ist

Nach einer Handabnahme lagen **drei** Funde mit Status `an Frank übergeben` im
Beutebuch — außerhalb einer Kaskade, der Bau war längst abgeschlossen
(`.ralph-state` über `RALPH_CAP`). Gesucht war genau das, was Phase 4 tut:
Frank fixt der Reihe nach, eskaliert nach drei Fehlversuchen selbst an Axel,
Axel liefert die Akte, Frank holt den Fund mit `Fix-Plan liegt vor` zurück,
weiter zum nächsten.

**Diese Kette ist im Kit vorhanden und funktioniert — sie ist nur nicht
erreichbar, ohne alles davor mitzubezahlen.** Es gibt drei Wege, und keiner
passt:

1. **`vollautomatik`** fährt zuerst Phase 1 (Ralph — hier sofort „Feierabend",
   also billig) und dann die **Phasen 2 und 3: zwei bezahlte Red-Team-Sweeps**.
   Die kosten nicht nur Geld, sie erzeugen **neue Funde** und verschieben damit
   genau das Ziel, das man gerade abräumen wollte.
2. **`frank` von Hand** nimmt laut eigenem Kopfkommentar *„EINEN Fund pro
   Aufruf"* und endet mit Exit 3, sobald keiner mehr für ihn dasteht. Ruft man
   ihn in einer Schleife, fehlt **Axel**: Nach drei Fehlversuchen setzt Frank
   den Fund selbst auf `an Axel übergeben` — und findet ihn beim nächsten
   Aufruf nicht mehr. Die Schleife endet dann mit „nichts zu tun", während ein
   Fall auf Axel wartet. Das sieht wie ein sauberer Abschluss aus.
3. **Den Phasen-Zeiger von Hand setzen.** Er ist die einzige Quelle für die
   Startphase (`$abPhase` wird nur dort gesetzt), verlangt aber eine zweite
   Zeile mit der exakten „Lage" (`.ralph-plan` + `.ralph-state`) und wird sonst
   verworfen. Eine interne Zustandsdatei von Hand zu schreiben ist kein Weg,
   den man einem Anwender empfiehlt.

**`TEAM_VOLLAUTOMATIK_AB_PHASE` sieht wie die Lösung aus und ist keine.** Der
Name verspricht „ab Phase N", die Doku im Skriptkopf sagt aber nur *„1 wirkt wie
`--von-vorn`"*, und der Code prüft ausschließlich auf `'1'`. Ein gesetztes
`TEAM_VOLLAUTOMATIK_AB_PHASE=4` wird **still ignoriert** — der Lauf beginnt bei
Phase 1 und fährt die Sweeps. Das ist die unangenehmste Eigenschaft dieses
Befunds: Der naheliegende Griff führt lautlos zum teuersten Ergebnis.

## Wo es steckt

`vollautomatik.ps1` / `vollautomatik.sh`:

- die Auswertung von `TEAM_VOLLAUTOMATIK_AB_PHASE` (Vergleich gegen `'1'`),
- `Phasen-Zeiger-Lesen` als einzige Quelle von `$abPhase`,
- Phase 4 selbst (die Frank↔Axel-Schleife samt Stagnations-Bremse), die als
  Block genau das kann, was gebraucht wird.

Betroffen ist außerdem der Skriptkopf: Er nennt `TEAM_VOLLAUTOMATIK_AB_PHASE`
unter `Env:`, also unter den Stellschrauben, ohne zu sagen, dass jeder andere
Wert als `1` wirkungslos ist.

## Warum das jede Installation trifft

**Out-of-Loop-Funde zwischen zwei Kaskaden sind der Normalfall, nicht die
Ausnahme.** Sie entstehen bei jeder Handabnahme, bei jedem UAT, bei jedem
Closeout — das Kit hat für sie eigens Franks Dreisatz, den Status
`an Frank übergeben` und mit `--kaskade vor-N` sogar eine eigene Kostenzeile.
Für das **Abarbeiten** mehrerer solcher Funde gibt es dagegen keinen Weg außer
den drei oben.

Die stille Variante ist die teure: Wer `frank` in eine Schleife setzt — der
naheliegendste Griff —, bekommt eine Fixphase **ohne Axel**. Fälle, die Frank
dreimal nicht knacken konnte, bleiben liegen, und die Schleife meldet dabei
„nichts zu tun". Genau für diese Fälle gibt es Axel.

## Was ich schon versucht habe

- **`TEAM_VOLLAUTOMATIK_AB_PHASE=4` gesetzt** — wirkungslos, siehe oben; im Code
  nachgelesen statt geraten.
- **Den Phasen-Zeiger** als Weg **verworfen**: Eine interne Zustandsdatei von
  Hand zu schreiben, ist keine Bedienung.
- **Lokal gelöst** mit einem kleinen Projektskript, das ausschließlich die
  regulären Entrypoints aufruft und die Kette nachbildet: `frank` aufrufen; bei
  Exit `5`/`42`/`43` abbrechen; danach das Beutebuch fragen, ob ein Fall auf
  Axel wartet, und nur dann `axel` rufen; sind weder für Frank noch für Axel
  Funde da, ist die Phase beendet. Das kostet keinen Sweep und ruft das starke
  Modell nur, wenn wirklich ein Fall dafür vorliegt. **Bewusst ohne Lauf-Deckel
  und ohne Stagnations-Bremse** — beides gehört in das Kit, nicht in ein
  Projektskript, und ist der Grund für diese Meldung.

**Vorschlag, zwei Größen:**

- **Klein:** `TEAM_VOLLAUTOMATIK_AB_PHASE` das tun lassen, was sein Name sagt —
  Werte `2`, `3`, `4` als Startphase akzeptieren (die Werte, die der
  Phasen-Zeiger ohnehin kennt). Ein unbekannter Wert sollte abbrechen statt
  still auf Phase 1 zu fallen.
- **Größer und aus meiner Sicht der eigentliche Punkt:** ein eigener
  Entrypoint (`fixphase`), der Phase 4 mitsamt Lauf-Deckel, Stagnations-Bremse
  und Abschlussbericht fährt. Die Rolle „mehrere offene Funde abarbeiten, ohne
  eine Kaskade zu starten" ist im Kit heute die einzige Team-Tätigkeit ohne
  eigenen Aufrufer — `ralph`, `harry`, `marv`, `frank` und `axel` haben je
  einen.

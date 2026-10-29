# Suite über der Frist: `smoke_warten warten` meldet ein fremdes Grün, Suiten laufen doppelt, die 75-%-Warnung kommt nie

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-29-waechst-die-suite-ueber-die-frist-verliert-jede-rolle-zehn-m.md
      .\kit-melden.cmd ablegen  2026-10-29-waechst-die-suite-ueber-die-frist-verliert-jede-rolle-zehn-m.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-29-waechst-die-suite-ueber-die-frist-verliert-jede-rolle-zehn-m.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler im Werkzeug (falsches Grün) und Lücke in einer Regel (`Kit-BL-232`, `Kit-BL-273`)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; fünfte Kaskade, fünf Stufen. Viele Tests starten echte Unterprozesse (Wegwerf-Repos, Testläufe darin)

## Was passiert ist

In einer Kaskade lief die Suite plötzlich bis zu 45 Minuten statt 3 (369 auf 442 Tests).
`TEAM_SMOKE_TEST_TIMEOUT` stand auf 600 s, `TEAM_SMOKE_TEST_SCHNELL` war leer. Die Logs von
`smoke_warten` zeigen den Verlauf: nach Stufe 3 4:40, Stufe 4 19:04, Stufe 5 25:48, in der
Fixphase 30:31, 27:39, 33:30 und 45:09. Die Ursache lag an der Maschine, nicht an den neuen Tests:
Ein Python-Start dauerte zeitweise über eine Sekunde statt Millisekunden; in einer Nachmessung mit
gemischtem Zustand brauchte dieselbe Suite 14 Minuten, die neuen Tests davon 2. Für das Kit zählt
nicht der Grund, sondern dass die Suite ab Stufe 4 über der Frist lag. Folgen:

1. **Ein falsches Grün.** Beim ersten von fünf Fixen startete Frank Reproducer und volle Suite in
   einem Vordergrundbefehl mit der Höchstfrist des Werkzeugs (600 s). Nach zehn Minuten schob das
   Werkzeug ihn in den Hintergrund. Frank rief darauf `smoke_warten.py warten` auf, ohne vorher
   `start` gerufen zu haben. `warten` nahm das jüngste Log unter `.team-logs/`: Ralphs Suite aus der
   letzten Stufe, also vor Franks Änderung (423 passed, 25:48). Es meldete „Fertig: Exit 0
   (gruen)“, und Frank committete. Seine eigene Suite endete im Hintergrund mit `425 passed,
   2 skipped, 1 error`: Der Stolperdraht der Suite hatte den Commit gesehen, den Frank währenddessen
   gemacht hatte. Ein `| tail -6` im Befehl machte daraus Exit 0, und als die Benachrichtigung kam,
   hielt Frank sie für „derselbe Lauf“. Der Fix selbst war in Ordnung (die Suite im nächsten Fix
   war grün), aber geprüft hatte die Verifikation nichts.
2. **Zwei Suiten gleichzeitig, zweimal.** In Stufe 4 schob das Werkzeug Ralphs Vordergrundlauf
   nach 10 Minuten in den Hintergrund. Eine Minute später startete Ralph mit
   `smoke_warten start` eine zweite Suite daneben. Die zweite wurde rot, weil Ralph währenddessen
   `CHANGELOG.md` schrieb (Stolperdraht); erst die Wiederholung war grün. Beim zweiten Fix tat
   Frank dasselbe: fünf Sekunden nach dem Verschieben `smoke_warten start`. Zwei Suiten
   nebeneinander verfälschen außerdem die Zeiten.
3. **Zehn Minuten im Vordergrund verloren, viermal.** In vier von fünf Fixen startete Frank die
   Suite zuerst im Vordergrund: zweimal mit `timeout 590 <smoke-test>`, wie es der Prompt verlangt,
   zweimal mit der Höchstfrist des Werkzeugs (die Fälle 1 und 2). Erst danach nahm er den
   Zwei-Schritt-Weg. Vorher wählen konnte er nicht: Der Prompt nennt die Frist, aber nicht, wie
   lange die Suite zuletzt lief.
4. **Die 75-%-Warnung kam nie.** Sie steht nur in `team_quittung_selbstpruefung`, und die läuft
   nur im vierten Ausgang (Sitzung ohne Promise). In diesem Lauf kam jede Stufe und jeder Fix
   mit Promise. Die volle Suite am Phasenende fährt die Vollautomatik nur, wenn
   `TEAM_SMOKE_TEST_SCHNELL` gesetzt ist. Im Normalfall misst der Loop die Suite also nie
   selbst, und der Abschlussbericht nennt ihre Dauer nicht. Aufgefallen ist es erst dem
   Menschen beim Lesen der Logs.

Nebenbefund zu Fall 1: Headless kam die Benachrichtigung doch (CLI 2.1.311). Die CLI wartete nach
Franks Schlusswort acht Minuten auf den Hintergrundlauf und weckte die Sitzung dann mit der
Benachrichtigung. Die Ergebniszeile zählt danach nur diesen letzten Abschnitt: 1 Turn, 3,5 s, bei
28 Antworten über 20 Minuten. Die Kosten gelten für die ganze Sitzung. Das Turn-Profil im
Abschlussbericht stimmt für solche Läufe nicht, und die Annahme hinter Exit 43 („die
Benachrichtigung kommt nie“) gilt hier nicht mehr.

## Wo es steckt

- `team/tools/smoke_warten.py warten` ohne Kennung: `_juengster()` nimmt das jüngste
  `smoke-*.log` im Ordner, egal wer es wann gestartet hat; keine Prüfung gegen den Aufrufer oder
  den Stand des Baums.
- `team/tools/smoke_warten.py start`: prüft nicht, ob schon eine Suite läuft.
- `team/lib.sh` und `team/lib.psm1`, `SMOKE_ZEILE` und `SMOKE_SUFFIX`: erst Vordergrund, den
  Zwei-Schritt-Weg erst, wenn die Höchstfrist des Werkzeugs nicht reicht; keine Angabe, wie lange
  die Suite zuletzt lief.
- `team/lib.sh` und `team/lib.psm1`, `team_quittung_selbstpruefung`: die Warnung aus
  `Kit-BL-232` (Punkt 4) steht nur dort.
- `vollautomatik.*`: volle Suite am Phasenende nur mit `TEAM_SMOKE_TEST_SCHNELL`.

## Warum das jede Installation trifft

Jede Suite wächst. Die Frist ist ein Default des Kits, Werkzeug und Warnung sitzen im Kit, und der
Prompt kommt aus dem Kit. Ohne gesetzte Schnellstufe merkt in keinem Projekt etwas, dass die Suite
die Frist reißt, solange jede Rolle ihr Promise liefert — also gerade dann, wenn alles gut läuft.
Und sobald zwei Rollen nacheinander `smoke_warten` benutzen, liegt für die zweite schon ein
fremdes Grün bereit.

## Was ich schon versucht habe

Im Projekt nichts geändert; die Regeln gehören dem Kit. Die Dauer je Test misst der Closeout,
danach entscheidet der Mensch zwischen schnelleren Tests und `TEAM_SMOKE_TEST_SCHNELL`.

Vorschlag, ohne Anspruch:

1. `warten` ohne Kennung nimmt nur einen Lauf, den diese Rolle gestartet hat (etwa: `start` legt
   die Kennung für den Rollenaufruf ab), sonst Exit 2 mit „zuerst `start`“.
2. `start` lehnt ab oder wartet, solange noch eine Suite desselben Projekts läuft.
3. Die Dauer jedes Suite-Laufs steht ohnehin im Log von `smoke_warten` („… passed in X s“). Den
   jüngsten Wert in den Prompt geben; liegt er über der Frist, gleich den Zwei-Schritt-Weg
   nennen statt erst den Vordergrund.
4. Die Warnung dorthin, wo jeder Lauf vorbeikommt: Abschlussbericht und Stufenende, gespeist aus
   denselben Logs.

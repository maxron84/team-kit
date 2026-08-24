# Gegenprobe zentraler Werte gehoert in die verbrauchende Stufe, nicht in die einfuehrende

- **Art**: Fehler am Kit (Regel unvollständig)
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, paketgebundener
  UI-Stack (Dart/Flutter), zweite gebaute Kaskade, ~90 Tests

## Was passiert ist

Die Regel aus `CLAUDE.md` — *„Zentrale Werte gehören gegengeprobt, nicht
gegrept"* — verlangt, dass eine Stufe, die einen zentralen Wert ändert, ihn
probeweise auf zwei fremde Werte setzt, die Suite laufen lässt und danach
nachweislich zurücksetzt.

Der Plan der Kaskade schrieb diese Gegenprobe in die Stufe, die die
Wertabbildung **einführte** (eine Enum-Abbildung von Bedientexten auf
Datenbankwerte, abgesichert durch `CHECK`-Constraints des Schemas). Der Loop
führte sie dort regelkonform durch und dokumentierte das Ergebnis im
Commit-Text — mit einer Zahl, die die Probe selbst entwertet:

> „Gegenprobe zur Wertabbildung durchgefuehrt: die fuenf Werte zweimal auf
> fremde Werte gesetzt […]. Beide Male genau 2 rote Stellen (die eigene
> Wertabbildungs-Test-Gruppe) — deckungsgleich mit dem grep-Befund, dass die
> Abbildung noch keinen Verbraucher hat."

Zum Zeitpunkt dieser Stufe gab es die Kopplung noch gar nicht: Der einzige
Verbraucher der Abbildung — der Code, der die Werte in die Datenbank schreibt —
entstand drei Stufen später. Die Gegenprobe konnte deshalb **per Konstruktion**
nichts finden, was die Textsuche nicht auch fand. Sie meldete trotzdem Vollzug,
und der Commit-Text las sich wie eine bestandene Prüfung.

Im Closeout wurde dieselbe Probe nachgeholt, nachdem der Verbraucher existierte:

| Probe | rote Tests |
|---|---|
| in der einführenden Stufe, alle fünf Werte verstellt (zwei Varianten) | **2** |
| im Closeout, alle fünf Werte verstellt (Variante A) | **11** |
| im Closeout, alle fünf Werte verstellt (Variante B) | **11** |
| im Closeout, **nur** zwei der fünf Werte verstellt | **10**, über 7 Testdateien |

Die Textsuche nach den fünf Werten findet 8 Dateien. Das Verstellen von nur
zwei Werten macht Tests in 7 Dateien rot — darunter drei, die die Textsuche
**nicht** nennt (der App-Einstiegstest und zwei Reproducer-Tests des Red
Teams). Die Kopplung ist real und weiter verzweigt als sichtbar. Die Probe zum
frühen Zeitpunkt hat davon nichts gesehen.

## Wo es steckt

In der Regel selbst, `CLAUDE.md`, Abschnitt „Kaskaden-Planungsregeln", Block
*„Zentrale Werte gehören gegengeprobt, nicht gegrept"*. Der Satz lautet dort:

> „Ändert eine Stufe einen **zentralen Wert** (Konstante, Default, Schwellwert,
> Balancing-Zahl), verlangt ihre **Verifikation** ausdrücklich die Gegenprobe […]"

„Ändert eine Stufe einen zentralen Wert" trifft auf die **einführende** Stufe zu
— dort wird der Wert schließlich angelegt. Genau dort ist die Probe aber
wertlos, solange kein anderer Code ihn liest. Die Regel nennt keinen Zeitpunkt
und keine Bedingung; sie ist an dieser Stelle unvollständig, nicht falsch.

Mitbetroffen ist das Briefing des Architekten (`team/prompts/rolle-architekt.md`),
das die Regel beim Stufenschnitt anwendet, ohne den Zeitpunkt zu prüfen.

## Warum das jede Installation trifft

Die Regel steht in `CLAUDE.md` und wird von jeder Installation übernommen. Der
Fehlermodus ist derselbe, den die Regel eigentlich verhindern soll, nur eine
Ebene höher: **eine Verifikation, die zuverlässig grün ist, ohne etwas geprüft
zu haben** — und die ihre eigene Wirkungslosigkeit als Bestätigung ausgibt
(„deckungsgleich mit dem grep-Befund" liest sich wie ein Erfolg, ist aber der
Beweis, dass die Probe nichts konnte).

Er trifft besonders zuverlässig bei sauber geschnittenen Kaskaden: Wer Logik
und Verbraucher trennt — was gute Praxis ist und vom Kit an anderer Stelle
ausdrücklich empfohlen wird —, legt die Probe fast zwangsläufig in die falsche
Stufe. Je besser der Stufenschnitt, desto verlässlicher greift der Fehler.

Zusätzlich fällt er nie auf: Der Commit-Text dokumentiert eine durchgeführte
Probe, der Smoke-Test ist grün, das Abschluss-Doc verzeichnet eine erfüllte
Pflicht. Nur wer die genannte Zahl gegen den Aufbau der Kaskade hält, sieht den
Widerspruch — im Feld ist das erst im Closeout aufgefallen, und auch dort nur,
weil der Commit-Text die Zahl **2** ehrlich mitgeteilt hat.

## Vorschlag

Die Regel um den Zeitpunkt ergänzen, sinngemäß:

> Die Gegenprobe gehört in die Stufe, in der der Wert einen **Verbraucher**
> hat — nicht in die, die ihn einführt. Fallen beide auseinander, wandert die
> Probe in die spätere Stufe, und die einführende Stufe verweist darauf.
> Ergibt die Probe **weniger oder gleich viele** rote Stellen, als die
> Textsuche Fundstellen nennt, hat sie nichts geprüft: Das ist kein
> bestandenes Ergebnis, sondern der Hinweis, dass sie zu früh lief.

Das zweite Kriterium ist wichtiger als das erste, weil es maschinell prüfbar
ist und keinen Planvorsatz braucht: Die Zahl aus der Probe gegen die Zahl aus
`grep` — steht die Probe nicht darüber, war sie umsonst.

## Was ich schon versucht habe

Nichts lokal gepatcht — die Regel ist Kit-Eigentum, und ein lokaler Eingriff in
`CLAUDE.md` hätte die bekannte Verfallszeit beim nächsten `--update`
(`BL-42`/`BL-58`). Im Projekt ist stattdessen festgehalten, dass der Architekt
den Zeitpunkt beim Aushärten künftig ausdrücklich in die betroffene Stufe
schreibt, bis die Kit-Regel nachgezogen ist.

Die Gegenprobe selbst wurde im Closeout nachgeholt (außerhalb des Loops, ohne
Commit, Rückbau nachgewiesen, Suite danach wieder grün) — die Zahlen oben
stammen aus diesem Nachholen.

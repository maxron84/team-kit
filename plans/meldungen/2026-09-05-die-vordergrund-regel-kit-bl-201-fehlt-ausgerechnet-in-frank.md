# Die Vordergrund-Regel (Kit-BL-201) fehlt ausgerechnet in Franks Briefing

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Flutter/Dart-Stack;
  gewachsen über 13 Kaskaden, Suite bei ~570 Tests, ein voller Suitenlauf
  dauert rund 2:40 Minuten.

## Was passiert ist

Ein einzelner Fund (`hoch`, UI-Fix an einem Bildschirm) ging an Frank und
kostete **16,09 USD in drei Versuchen** — 97, 145 und 70 Turns. Zum Vergleich:
Die fünf Frank-Läufe der unmittelbar davorliegenden Kaskade kosteten
**zusammen 6,25 USD**, jeder im ersten Versuch.

Die ersten zwei Versuche endeten ohne Promise. Ihr `result`-Feld sagt wörtlich,
woran:

```
v1: "I'll hold here until the smoke-test monitor notifies me of completion."
v2: "Waiting for the full `flutter test` run to finish before continuing
     with the rest of Frank's Dreisatz (CHANGELOG + beutebuch status + commit)."
```

Beide Logs tragen dabei `subtype: success` und `is_error: false`.

Das ist **exakt die vierte Fehlerklasse**, die das Kit selbst beschreibt und
gegen die es `Kit-BL-201` eingeführt hat: Eine bauende Rolle startet den
Smoke-Test als Hintergrund-Task oder Monitor und wartet auf eine
Benachrichtigung, die headless nie kommt. **13,13 USD von 16,09 USD** — 82 %
der Kosten dieses einen Fundes — sind in den zwei Leerläufen verbrannt. Der
dritte Versuch, der den Fix dann lieferte, kostete 2,96 USD; das ist die
normale Größenordnung dieses Projekts.

## Wo es steckt

In `team/prompts/rolle-frank.md`. Die Regel steht **wörtlich gleichlautend** in
vier der sechs Briefings:

| Briefing | `Kit-BL-201`-Absatz vorhanden? |
|---|---|
| `rolle-ralph.md` | ja |
| `rolle-harry.md` | ja |
| `rolle-marv.md` | ja |
| `rolle-axel.md` | ja |
| `rolle-frank.md` | **nein** |
| `rolle-architekt.md` | nein — arbeitet interaktiv, für ihn gilt sie nicht |

Der fehlende Absatz ist dieser (Wortlaut aus `rolle-ralph.md`):

> **Lange Befehle laufen im VORDERGRUND** (`Kit-BL-201`): nie als
> Hintergrund-Task, kein Wakeup, kein Monitor — headless kommt keine
> Benachrichtigung, wer darauf wartet endet ohne Quittung, und das Log meldet
> trotzdem `subtype: success`. Der Neustart wirft dann fertige, bezahlte Arbeit
> weg (19,47 USD im Feld). Dauert ein Lauf zu lange, erhöhe ich das Zeitlimit
> auf `TEAM_SMOKE_TEST_TIMEOUT` aus `team.config.sh`, statt auszuweichen.

Erschwerend: `rolle-frank.md` erwähnt den Smoke-Test **überhaupt nicht** —
weder den Befehl noch dass er zu laufen hat. Eine Textsuche nach
`vordergrund|hintergrund|monitor|wakeup|smoke|test|analyze` liefert in dieser
Datei null Treffer.

## Warum das jede Installation trifft

Die Auslassung trifft **die Rolle mit der höchsten Dichte an langen
Testläufen**. Franks Dreisatz verlangt in Schritt 1 ausdrücklich eine
Gegenprobe:

> Dann die **Gegenprobe**: Ohne meinen Fix muss dieser Test **rot** werden —
> geprüft, nicht vermutet.

Das sind **mindestens zwei** volle Suitenläufe pro Fix — einer mit, einer ohne
Fix —, in der Praxis mehr. Ralph fährt je Stufe einen. Harry, Marv und Axel
sind read-only und fahren im Regelfall gar keinen. **Die einzige Rolle, deren
eigener Dreisatz das Verdoppeln langer Läufe vorschreibt, ist genau die, der
die Regel dagegen fehlt.**

Der Fehler ist damit kein Zufall der Verteilung, sondern eine Auslassung an
der teuersten möglichen Stelle. Er trifft jede Installation, in der ein
Suitenlauf länger dauert als die Geduld des Modells — bei uns ab rund zwei
Minuten reproduzierbar, und er wird mit jedem Test schlimmer.

Dazu kommt: Der Fall ist **von außen unsichtbar**. Beide Fehlläufe melden
`subtype: success` und `is_error: false`; die Fixphase startet einfach den
nächsten Versuch. Aufgefallen ist es hier nur, weil beim Kostenabschluss die
Summe nicht zum Umfang des Fixes passte.

## Was ich schon versucht habe

Nichts gepatcht. Der Fix ist offensichtlich — denselben Absatz nach
`rolle-frank.md` übernehmen —, aber er hat im Feld die bekannte Verfallszeit
(`BL-42`/`BL-58`): `team/prompts/*.md` überlebt kein `install.sh --update`.
Ein lokaler Fix müsste nach jedem Update erneut gesetzt werden, und genau
dieses Nachziehen ist im Feld schon einmal vergessen worden.

**Vorschlag für das Kit — zwei Teile:**

1. Den `Kit-BL-201`-Absatz nach `rolle-frank.md` übernehmen, wörtlich wie in
   den vier anderen Briefings.
2. Eine Gegenprobe, die das Auseinanderlaufen künftig meldet: Der Absatz ist
   in fünf Briefings byte-gleich; ein Team-Test, der genau das prüft, hätte die
   Lücke ohne Feldschaden gefunden. Das Kit hat für byte-gleiche Bausteine
   bereits einen Präzedenzfall — im Feld liegt dieselbe Zusicherung neunmal
   identisch in neun Testdateien und wird über die Prüfsumme verglichen.

**Zur Einordnung des Betrags:** Der Regel-Absatz nennt selbst 19,47 USD als
Feldschaden. Dieser Fall liegt mit 13,13 USD in derselben Größenordnung — an
**einem** Fund, in **einem** Vormittag.

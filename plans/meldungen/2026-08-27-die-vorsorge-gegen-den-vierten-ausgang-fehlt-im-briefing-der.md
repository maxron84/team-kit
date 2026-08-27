# Die Vorsorge gegen den vierten Ausgang fehlt im Briefing der bauenden Rolle

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt im vierten Kaskadenlauf, Windows,
  pwsh-Bahn, Python + Electron, rund 120 Tests, Suitenlaufzeit gut zwei Minuten.

## Was passiert ist

Die bauende Rolle hat eine Stufe vollständig gebaut und ist dann in den
vierten Ausgang gelaufen (`BL-41`). Im Lauf-Log steht als `result` wörtlich:

```
I'll wait for the background suite run to finish (a system notification
will arrive automatically) rather than polling further.
```

Sie hat den Smoke-Test also als **Hintergrund-Task** gestartet und auf eine
Benachrichtigung gewartet, die es headless nicht gibt. Das Log meldet sich
selbst als Erfolg (`subtype: success`, `is_error: false`, `stop_reason:
end_turn`, 59 Turns), gibt aber kein Promise. Kosten der verlorenen Sitzung:
1,93 USD.

**Das ist genau der Fall, den `BL-41` beschreibt — und die Regelquelle des Kits
kennt auch die Vorsorge dagegen.** In der `CLAUDE.md`-Vorlage steht unter der
vierten Fehlerklasse:

> „Vorbeugend gilt für jede bauende Rolle: Der Smoke-Test läuft im
> **Vordergrund**, nie als Hintergrund-Task und nie mit einem Wakeup darauf."

**Im Briefing der bauenden Rolle steht dieser Satz nicht.** `rolle-ralph.md`
umfasst 39 Zeilen und enthält keinen Treffer für „Vordergrund", „Hintergrund",
„Wakeup", „Monitor" oder „43".

## Wo es steckt

In der Bootstrap-Vorlage des Rollen-Briefings der bauenden Rolle
(`bootstrap/prompts/rolle-ralph.md` bzw. der entsprechende Pfad im Kit) — dort
fehlt die Auflage.

Die Regel selbst steht in der `CLAUDE.md`-Vorlage im Abschnitt „Loop-Mechanik &
Auth". Dieser Abschnitt beginnt mit dem Hinweis, dass das meiste daran die
Shell erledige und nicht die Rolle („Hier stehen deshalb nur die Sätze, nach
denen eine Rolle **handelt**"). Die eine Auflage, die tatsächlich an die Rolle
gerichtet ist, steht damit inmitten von Auth- und Cap-Mechanik, die sie
ausdrücklich nicht betrifft.

## Warum das jede Installation trifft

Das Kit kennt den vierten Ausgang als **Nachsorge**: `BL-41` erkennt ihn
zuverlässig, meldet ihn sauber und gibt dem Menschen eine Prüfreihenfolge. Was
fehlt, ist die **Vorsorge an der Stelle, an der er entsteht** — im Prompt der
Rolle, die den Smoke-Test aufruft.

Die Doku-Hygiene-Regel des Kits sieht die Briefings ausdrücklich als den Weg
vor, auf dem eine Rolle ihre Auflagen erhält („Rollen-Briefings statt
Volltext"). Eine Auflage, die nur in der Regelquelle steht, verlässt sich
darauf, dass die Rolle sie in einem Abschnitt findet, der ihr sagt, er betreffe
sie größtenteils nicht.

Der Fall ist zudem nicht selten: Die Nachsorge-Meldung selbst nennt „viermal im
Feld, 19,47 USD" — das Kit weiß also, dass er wiederkehrt. Jede Wiederholung
kostet eine bezahlte Sitzung und eine Handquittierung.

## Was die Diagnose zusätzlich erschwert hat (Nebenbefund)

Die Selbstprüfung meldete im selben Atemzug:

```
✗ .venv/…/python.exe -m pytest -q ist ROT.
```

**Der Baum war nicht rot.** Im Vordergrund nachgemessen: alle Tests grün, gut
zwei Minuten Laufzeit. Die Selbstprüfung hat den unfertigen Hintergrundlauf —
also dieselbe Ursache — als roten Smoke-Test gewertet.

Die anschließende Prüfreihenfolge für den Menschen bietet daraufhin zwei
Zweige an, die **beide einen roten Baum voraussetzen**:

- „Sind ausschließlich die von DIESER Stufe neu angelegten Testdateien rot →
  Testaufbau reparieren"
- „Ist BESTEHENDER Testbestand rot → die Stufe hat etwas gebrochen, neu bauen"

Der zweite hätte hier eine fertige, bezahlte Stufe weggeworfen. Aufgelöst hat
den Fall das Feld `result` im Lauf-Log — das die Anleitung nicht erwähnt.

**Vorschlag:** Wenn die Selbstprüfung ohnehin den vierten Ausgang erkennt, könnte
sie ihre eigene Rot-Meldung relativieren („Der Smoke-Test wurde möglicherweise
nie zu Ende geführt — im Vordergrund nachmessen, bevor du den Befund
verwendest") und den Menschen auf `result` im Log hinweisen. Das ist der
schnellste Weg zur richtigen Diagnose und kostet eine Zeile.

## Was ich schon versucht habe

Nichts repariert — der Fund steckt in der Kit-Infrastruktur, nicht im Projekt,
und ein lokaler Eingriff ins Briefing hätte beim nächsten `--update` eine
Verfallszeit (`BL-42`/`BL-58`).

Diagnostiziert wurde so:

1. `git log` und `git status` — die Arbeit war vollständig, aber uncommittet.
2. Smoke-Test im **Vordergrund** — grün, entgegen der Meldung.
3. Das Lauf-Log gelesen; `result` nannte die Ursache wörtlich.
4. Die Stufe von Hand quittiert (committet, Zustandszähler weitergeschaltet),
   danach lief die Kaskade normal weiter.
5. Gegenprobe im Briefing der Rolle nach den einschlägigen Stichwörtern —
   kein Treffer.

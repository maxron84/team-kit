# Der Team-Test zu fremden Backlog-Nummern liest das Beutebuch-Archiv nicht und wird nach jedem Archivieren rot

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-29-der-team-test-zu-fremden-backlog-nummern-liest-das-beutebuch.md
      .\kit-melden.cmd ablegen  2026-09-29-der-team-test-zu-fremden-backlog-nummern-liest-das-beutebuch.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-29-der-team-test-zu-fremden-backlog-nummern-liest-das-beutebuch.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-12)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Vier Kaskaden sind gelaufen, das Beutebuch wurde nach der dritten zum ersten Mal
  archiviert.

## Was passiert ist

Nach dem Closeout der dritten Kaskade hat das Projekt sein Beutebuch mit `beutebuch.py archiviere`
archiviert, wie es die Doku-Hygiene verlangt (Punkt 3: archivieren, sobald die Liste überwiegend
abgeschlossen ist). Der nächste Lauf von `team-test` war rot:

```
AssertionError: BL-140/BL-148: Diese Verweise zeigen ins Leere. Eine blanke Nummer meint den
Backlog DIESES Projekts — dort steht sie nicht. …
    CLAUDE.md:77 — HM-9: …
    CLAUDE.md:89 — HM-18: …
1 failed, 12 passed
```

Beide Verweise sind richtig. Sie zeigen auf eigene Funde des Projekts, die im Archiv stehen, und
die Schreibweise folgt der Notationstabelle in `CLAUDE.md`: blank heißt „mein Backlog". Aufgefallen
ist das erst an einem Handprobentag, weil die Team-Tests sonst nur nach einem Kit-Update laufen. Der
Smoke-Test des Projekts ist davon nicht berührt.

Dazu kommt ein zweiter, leiserer Effekt. `CLAUDE.md` zitiert einen dritten archivierten Fund. Er
wird heute nur deshalb nicht gemeldet, weil zwei Funde im aktiven Beutebuch ihn im Fließtext
erwähnen. Werden diese beiden archiviert, wird auch er rot. Ob ein Verweis als gültig gilt, hängt
also davon ab, ob irgendein anderer Fund ihn zufällig nennt.

## Wo es steckt

`team/tests/test_bl140_fremde_backlognummern.py`, Funktion `_eigene_nummern()`. Sie liest
`TEAM_BACKLOG` und `TEAM_BEUTEBUCH` aus `team.config.*` (Vorgabe: `plans/backlog.md`,
`plans/beutebuch.md`) und nimmt **jede** Fundstelle einer Nummer darin als eigene. Das Archiv
(`ARCHIV` in `team/tools/beutebuch.py`, Vorgabe `plans/beutebuch-archiv.md`) liest sie nicht.

Das Gegenstück ist `beutebuch.py archiviere`: Es verschiebt jeden erledigten Block wörtlich ins
Archiv. Genau die Nummern, die zitierfähig bleiben sollen, fallen damit aus der Menge des Tests.
Die Nummernvergabe im selben Werkzeug (`_next_id`) liest das Archiv schon mit, der Test nicht.

## Warum das jede Installation trifft

Jedes Projekt, das die Doku-Hygiene befolgt und eigene Funde in `CLAUDE.md` oder einem anderen
Regeltext zitiert, bekommt nach dem ersten Archivieren einen roten Team-Test, obwohl kein Verweis
falsch ist. Der Druck, ihn grün zu machen, zeigt in die falsche Richtung: Man setzt `Kit-` vor einen
richtigen eigenen Verweis, und dann ist er falsch. Oder man löscht ihn.

## Was ich schon versucht habe

Lokal nichts geändert. Der Test bleibt rot, und der Backlog-Eintrag des Projekts hält den Grund
fest. Er nennt die Nummern absichtlich nicht in der Form, die der Test sucht, sonst würde er sie
selbst zu eigenen machen, und der Test würde grün, ohne dass etwas behoben ist. Das ist derselbe
zweite Effekt, nur absichtlich vermieden.

Vorschläge fürs Kit, in dieser Reihenfolge:
1. `_eigene_nummern()` liest das Beutebuch-Archiv mit, auf demselben Weg, den `_next_id` schon
   nimmt.
2. Als eigen zählt nur eine Nummer, die einen Block eröffnet (`### HM-<N>`) oder eine
   Backlog-Zeile trägt (`| BL-<N> |`), nicht jede Erwähnung. Sonst hängt das Urteil an fremdem
   Fließtext.
3. Gegenprobe als Fixture: Ein archivierter Fund, den ein Regeltext zitiert, bleibt grün. Eine
   Nummer, die nirgends steht, bleibt rot. Eine, die nur im Fließtext eines anderen Funds
   vorkommt, ist ebenfalls rot.

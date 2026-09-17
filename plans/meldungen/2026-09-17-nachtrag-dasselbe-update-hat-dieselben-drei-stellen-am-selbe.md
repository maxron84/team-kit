# Nachtrag: dasselbe Update hat dieselben drei Stellen am selben Tag ein zweites Mal ueberschrieben

- **Bezug**: BL-16
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst plus
  Electron-Oberfläche, rund 1170 Tests, 24 gebaute Kaskaden.

## Was passiert ist

Dies ist ein **Nachtrag** zur Meldung *„Das Update überschreibt projektlokale
Anpassungen ersatzlos und sagt nicht welche"* vom selben Tag. Er bringt keinen
neuen Mechanismus, sondern einen Messwert, der die Dringlichkeit ändert.

Die gemeldete Fassung war am Vormittag geschrieben. **Wenige Stunden später hat
das nächste `--update` exakt dieselben drei Stellen erneut überschrieben:**

1. `team_smoke_test_xdist_verfuegbar` in `team/lib.psm1` — ersatzlos gelöscht,
   samt der Aufrufstelle in `team_quittung_selbstpruefung`.
2. Die projektlokale Smoke-Test-Ausnahme in `team/prompts/rolle-ralph.md`.
3. Dieselbe Ausnahme in `team/prompts/rolle-frank.md`.

Es ist derselbe Befund, dieselben Dateien, dieselbe Reihenfolge. Nur der
Platzhalter (`BL-139`) blieb diesmal ausgefüllt.

**Was der Nachtrag hinzufügt, ist der Abstand.** Die erste Meldung argumentierte
mit drei Vorfällen über die Lebensdauer des Projekts — eine Preistabelle, vier
Konfigurationswerte, dann drei Stellen. Der vierte Vorfall kam am **selben Tag**
wie die Meldung über den dritten. Der lokale Fix hat damit nicht die
angenommene Verfallszeit „bis zum nächsten Update", sondern praktisch die eines
Arbeitstags.

**Wieder war es das Gate, das es gefunden hat**, nicht ein Mensch und kein
Sweep: Der Reproducer zum ursprünglichen Fund (`HM-110`) wurde rot. Die beiden
Briefing-Verluste hätte kein Test gefunden — Prompt-Text ist nicht prüfbar, und
gemerkt hätte man sie erst an einer Rolle, die in den vierten Ausgang läuft.

## Wo es steckt

Unverändert im Update-Verb, wie in der Hauptmeldung beschrieben: Es ersetzt
`team/lib.*` und `team/prompts/rolle-*.md` durch die Kit-Fassung, ohne zu
prüfen oder zu melden, dass die ersetzte Fassung abwich.

## Warum das jede Installation trifft

Die Hauptmeldung begründet das bereits. Der Nachtrag schärft nur die
Folgenabschätzung: Wer eine Anpassung an einer Kit-Datei vornimmt, die sich
**nicht** konfigurieren lässt, verliert sie beim nächsten Update — und
„nächstes Update" kann derselbe Tag sein. Ein Feldprojekt, das dem Kit dicht
folgt, repariert dieselben Stellen also mehrfach, ohne dass ihm irgendetwas
sagt, dass es nötig ist.

**Der Vorschlag der Hauptmeldung bleibt unverändert und wird durch diesen
Vorfall gestützt:** keine Ausnahmeliste, sondern ein Hinweis am Ende des
Update-Laufs — *„diese N Dateien wichen ab und wurden ersetzt, Sicherung unter
…"*. Er hätte hier vier Stunden Verzögerung und einen roten Baum gespart.

## Was ich schon versucht habe

Wie beim letzten Mal alle drei lokal wiederhergestellt, mit Nachweis: Der
`HM-110`-Reproducer ist wieder grün, die Briefings sind byte-genau die Fassung
von vor dem Update (das Update hatte dort **nur** gelöscht, nichts ergänzt —
`git checkout <vor-update> -- <briefing>` stellt sie deshalb vollständig her,
ohne eine Neuerung zu verlieren).

Für die beiden Briefings ist das inzwischen die dritte Wiederherstellung. Sie
lassen sich nicht in die Projektkonfiguration verschieben, weil das Kit die
Briefings als Ganzes ausliefert — genau die Lücke, die die Hauptmeldung
beschreibt.

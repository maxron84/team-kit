# Die Suite ist laenger als die Vordergrundgrenze der bauenden Rolle - die Auflage Smoke-Test im Vordergrund ist nicht erfuellbar

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python plus Electron. Fünf
  gebaute Kaskaden, 25 Stufen, ~200 Tests. Verifikationsbefehl ist ein blankes
  `pytest -q` über die ganze Suite.

## Was passiert ist

Die Testsuite dieses Projekts ist über die Kaskaden auf **149–220 s** gewachsen.
Die Vordergrundgrenze des Agenten-Werkzeugs liegt bei **120 s**. Damit ist die
Auflage aus dem Rollen-Briefing — *„Der Smoke-Test läuft im **Vordergrund**, nie
als Hintergrund-Task und nie mit einem Wakeup darauf"* — für diese Rolle
**nicht mehr erfüllbar**.

Die Rolle steht vor der Wahl zwischen einer Regelverletzung und einem
Werkzeug-Timeout. Sie wählt in **drei von drei** Fällen dieselbe Verletzung. Aus
den Lauf-Logs eines einzigen Laufs am 2026-08-28, wörtlich aus dem Feld
`result`:

| Rolle, Aufruf | Kosten | `result` |
|---|---|---|
| Ralph, letzte Stufe | 2,3607 | *„kicked off the full test suite in the background since it's taking longer than the 2-minute foreground limit. I'll continue once it reports back"* |
| Frank, Fund X Versuch 1 | 1,3935 | *„Waiting on the full smoke-test suite to finish before committing"* |
| Frank, Fund X Versuch 2 | 1,1938 | *„Waiting for the background pytest run to finish"* |
| | **4,9480 USD** | |

Alle drei landen im **vierten Ausgang** (Exit 43, `BL-41`): Das Log meldet sich
als `subtype: success`, das Promise fehlt. Bei Ralph kostete das eine
Handquittierung. Bei Frank ist es teurer: Seine beiden Versuche wurden per
**Rollback** verworfen und als Fehlversuche gezählt, dazu zwei Stagnationsrunden
auf die Auslauf-Bremse — **obwohl der Fix inhaltlich fertig war**. Der
erfolgreiche dritte Versuch unterscheidet sich sachlich nicht vom ersten. Das
sind 32 % der Rollenkosten dieses Laufs für null Erkenntnis.

**Der zweite Schaden ist subtiler und gefährlicher.** Ralphs Hintergrund-pytest
lief noch, als die `BL-41`-Selbstprüfung **ihre eigene** Suite startete. Zwei
gleichzeitige pytest-Läufe kollidieren (bei uns: SQLite-Dateien, Ports,
Electron-`userData`). Die Selbstprüfung meldete daraufhin:

```
    ✗ <Verifikationsbefehl> ist ROT.
      Das gehört an den Menschen: Erst prüfen, WO — sind ausschließlich die von
      DIESER Stufe neu angelegten Testdateien rot, ist der Testaufbau der
      wahrscheinlichere Schuldige als der Produktivcode (BL-61).
```

Der Baum war **grün** (`199 passed`, allein gefahren, im Closeout nachgemessen).
Die Selbstprüfung hat einen roten Baum diagnostiziert, den es nicht gibt — und
zwar mit einer Meldung, die den Menschen ausdrücklich zur Ursachensuche im
Testaufbau schickt. Wer ihr geglaubt und die Stufe neu gebaut hätte, hätte
2,36 USD bezahlte, fertige Arbeit weggeworfen.

## Wo es steckt

Zwei Stellen, beide im Kit:

1. **Die Auflage** — die Regel „Smoke-Test im Vordergrund" in den
   Loop-Rollen-Briefings (`team/prompts/rolle-*.md`) und in der
   `CLAUDE.md`-Vorlage, Abschnitt „Session-Limit (429) — die dritte
   Fehlerklasse", Absatz zur vierten Fehlerklasse. Sie verlangt etwas, das die
   Rolle bei einer Suite über der Werkzeuggrenze nicht leisten kann.
2. **Die `BL-41`-Selbstprüfung** in der Bibliothek (`team/lib.psm1` /
   `team/lib.sh`, der Block, der nach fehlendem Promise den
   `TEAM_SMOKE_TEST` selbst ausführt). Sie startet den Verifikationsbefehl
   bedingungslos ein zweites Mal, ohne zu prüfen, ob bereits ein Lauf läuft.

## Warum das jede Installation trifft

**Jede Suite wächst.** Die Grenze ist keine Eigenschaft dieses Projekts, sondern
des Agenten-Werkzeugs; die Suite überschreitet sie irgendwann in jedem Projekt,
das lange genug gebaut wird. Ab diesem Tag wird jede bauende Rolle
regelmäßig in den vierten Ausgang laufen — und die Kosten fallen dort an, wo sie
am wenigsten auffallen: als Frank-Fehlversuche mit Rollback, die wie
inhaltliches Scheitern aussehen.

**Der Fund ist nicht neu, nur diesmal messbar.** `Kit-BL-201` hat dieselbe
Bauform bereits zweimal adressiert — beim ersten Mal für eine Rolle, beim
zweiten Mal (Nachtrag aus diesem Feld) verschärft auf alle fünf
Loop-Briefings. Beide Male war die Antwort **eine schärfere Auflage**. Das hier
ist der Beleg, dass Schärfe nicht hilft: Es ist kein Disziplinproblem. Eine
Auflage, die die Rolle nicht einhalten *kann*, erzeugt genau das Verhalten, das
sie verbieten soll.

`Kit-BL-204`/`Kit-BL-205` (Franks Fixphase) grenzen daran an, treffen aber die
Bedienbarkeit der Fixphase, nicht die Erfüllbarkeit der Auflage.

## Was ich schon versucht habe

**Lokal nichts** — und das ist Absicht. Beide Stellen liegen in `team/` bzw. in
einem Rollen-Briefing; ein Eingriff hier hätte eine Verfallszeit beim nächsten
`--update` (Feldbefund `BL-16` dieses Projekts: `--update` schreibt
Entrypoints, `team/` und `TEAM.md` neu).

**Diagnostiziert ist es vollständig:** Die Selbstprüfung wurde von Hand
gegengeprobt, indem die Suite allein gefahren wurde — `199 passed in 182,89 s`,
Exit 0, sauberer Arbeitsbaum. Damit ist belegt, dass die rote Meldung aus der
Kollision der beiden Läufe stammt und nicht aus dem Code.

## Zwei Richtungen, die ich vorschlagen würde

Sie sind unabhängig; die zweite ist die billigere und schließt den
gefährlicheren der beiden Schäden.

1. **Die Auflage erfüllbar machen.** Der Verifikationsbefehl braucht ein
   eigenes, konfigurierbares Zeitlimit, das die Rolle im Vordergrund ausschöpfen
   darf — z. B. ein `TEAM_SMOKE_TEST_TIMEOUT` in `team.config`, das im
   Rollen-Briefing **beim Namen genannt** wird („dein Verifikationsbefehl darf
   bis zu N Sekunden im Vordergrund laufen; nutze das Zeitlimit deines
   Werkzeugs"). Solange die Rolle nur „Vordergrund, sonst nichts" liest, sieht
   sie eine 120-s-Wand und weicht aus.
2. **Die Selbstprüfung darf keinen zweiten Lauf danebenstellen.** Läuft bereits
   ein Verifikationslauf (Sperrdatei, Prozessprüfung), ist das Ergebnis
   „unbekannt", **nicht** „rot" — und die `BL-41`-Meldung an den Menschen sollte
   diesen Fall benennen. Eine Selbstprüfung, die im Zweifel „rot" behauptet,
   ist schlimmer als eine, die schweigt: Sie schickt den Menschen mit einer
   konkreten, falschen Fährte los.

Für Vorschlag 2 wäre ein Regressionstest in **beide** Richtungen sinnvoll —
sonst wird der Fix grün, indem die Selbstprüfung gar nichts mehr prüft.

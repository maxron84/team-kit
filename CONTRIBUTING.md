# Mitmachen

Danke, dass du dir die Mühe machst. Dieses Repo lebt von Funden aus echten
Läufen — die schwersten Fehler des Kits (`BL-1`, `BL-4`, `BL-5`) kamen alle aus
einem Feldprojekt, und alle drei lagen zwischenzeitlich nur dort.

## Der kürzeste Weg: eine Meldung

Wenn dir an der **Team-Infrastruktur** etwas auffällt — in `team/`, in einem
Entrypoint in der Projektwurzel oder in einer Regel aus `CLAUDE.md`/`TEAM.md` —,
dann trifft dasselbe jede weitere Installation. Aus deinem installierten
Projekt heraus geht das in einem Befehl:

```bash
./kit-melden.sh neu --titel "Kurz, was schiefging"
$EDITOR plans/kit-meldungen/<datum>-<slug>.md     # ausfüllen
./kit-melden.sh pruefen                            # Redaktionsprüfung
./kit-melden.sh senden plans/kit-meldungen/<datum>-<slug>.md
```

Unter Windows ohne WSL dasselbe mit `.\kit-melden.cmd`.

`senden` legt einen Pull Request an, der **eine neue Datei** unter
`plans/meldungen/` hinzufügt und sonst nichts anfasst. Das ist Absicht — siehe
unten. Ohne `gh` bekommst du stattdessen einen vorbefüllten Issue-Link; ein
GitHub-Konto im Browser genügt.

Kein T.E.A.M. installiert, oder der Fund kommt von woanders? Dann ist ein
[Issue](https://github.com/maxron84/team-kit/issues/new) genauso richtig.

## Was in eine Meldung gehört

Die Vorlage fragt es ab, aber der Kern ist:

1. **Der Hergang.** Was wurde aufgerufen, was war zu erwarten, was kam.
2. **Wo es steckt**, wenn du es weißt. Wenn nicht, reicht der Hergang.
3. **Warum das jede Installation trifft** — der Satz, der die Kit-Meldung vom
   Projektbug trennt.
4. **Die Lage deines Projekts**: Plattform, Bahn (bash oder pwsh), Greenfield
   oder Bestand, ungefähre Größe.

## Was NICHT hineingehört

**Deine Meldung landet in einem öffentlichen Repo.** Sie wird von einem
Agenten geschrieben, der gerade deine private Codebasis gelesen hat — Pfade,
Rechnernamen, Projektnamen und Schnipsel wandern sonst ungefiltert mit.

Deshalb: keine absoluten Pfade, keine Benutzer- oder Rechnernamen, keine
Schlüssel, kein Produktivcode. **Auch der Name deines Projekts nicht** — dieses
Repo führt seine Feldbelege aus genau diesem Grund unter `Feld A`…`Feld D`
statt unter Namen; für den Beleg zählt die *Lage* eines Projekts, nicht sein
Name. Deine Meldung bekommt beim Triage denselben Schutz.

`./kit-melden.sh pruefen` sucht die häufigsten Ausrutscher und weigert sich,
darüber hinwegzugehen, ohne dass du es ausdrücklich sagst (`--trotzdem`). Es
liest aber nicht mit: Die Verantwortung bleibt bei dir.

## Warum eine eigene Datei statt eines Eintrags im Backlog

`plans/backlog.md` ist **eine** Datei, und jede Meldung hinge an derselben
Stelle. Zwei gleichzeitige Meldungen wären ein garantierter Merge-Konflikt, und
der `BL-n`-Nummernraum wäre ein Wettlauf. Die Nummer vergibt deshalb der
Maintainer beim Triage; deine Meldung braucht keine.

Was aus einer Meldung wird, steht danach in `plans/backlog.md` und — wenn sie
abgetragen ist — in [`CHANGELOG.md`](CHANGELOG.md) und
[`plans/backlog-archiv.md`](plans/backlog-archiv.md), mit deiner Meldung als
Beleg.

## Sprache

Das Repo ist durchgehend deutsch — Doku, Briefings, Werkzeugmeldungen.
**Englische Meldungen sind trotzdem willkommen**: Sie werden beim Triage
übernommen und normalisiert. Lieber eine englische Meldung als keine.

Eine **englische Fassung des Kits** ist beschlossen und nicht gebaut; was sie
kostet und welche Fragen vorher zu entscheiden sind, steht als Skizze G in
[`plans/roadmap-skizzen.md`](plans/roadmap-skizzen.md). Bis dahin gilt für
Code-Beiträge dieselbe Regel wie für alles andere: Wortlaut auf Deutsch, weil
das Regel-Inventar **wörtlich** zitiert und zeichengenau geprüft wird.

## Pull Requests mit Code

Auch willkommen, mit drei Bitten:

- **Ein Fix braucht seinen Test.** Im Kit wird jede Feldlehre ein Test; das ist
  der Grund, warum dieselbe Klasse Fehler nicht zweimal auftaucht.
- **Beide Bahnen im Blick.** Trägt eine Datei `# Bahn: bash | Gegenstueck:
  <datei>.ps1`, dann gibt es sie zweimal. Wenn du die zweite Bahn nicht fahren
  kannst, sag das im PR — eine ungeprüfte Hälfte ist in Ordnung, solange sie
  als ungeprüft benannt ist. Stillschweigend halb ist der teure Fall
  (`BL-144`).
- **Nachweis ist `bash bash/kit-test.sh`**, nicht `kit-test.ps1` und nicht
  `pytest team/tests` im Kit-Repo (das schlägt erwartungsgemäß fehl, weil die
  Tests die *installierte* Ablage voraussetzen). `kit-test.sh` installiert das
  Kit in ein Wegwerf-Repo und fährt dort die volle Suite — zweimal, einmal mit
  den Auslieferungswerten und einmal mit angepasster Konfiguration.

Ändert dein PR eine **Regel** der Vorlage, zieh die betroffene Zeile in
[`doku/regel-inventar.md`](doku/regel-inventar.md) nach; Schritt 9 des
Selbsttests prüft das und wird sonst rot.

## Lizenz

[MIT](LICENSE). Mit deinem Beitrag stellst du ihn unter dieselbe Lizenz —
inbound = outbound. Kein CLA, keine Unterschrift.

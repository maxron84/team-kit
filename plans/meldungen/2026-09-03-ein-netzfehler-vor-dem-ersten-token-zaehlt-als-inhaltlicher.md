# Ein Netzfehler vor dem ersten Token zaehlt als inhaltlicher Fehlversuch und schiebt den Fund Richtung Axel

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-03-ein-netzfehler-vor-dem-ersten-token-zaehlt-als-inhaltlicher.md
      .\kit-melden.cmd ablegen  2026-09-03-ein-netzfehler-vor-dem-ersten-token-zaehlt-als-inhaltlicher.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-03-ein-netzfehler-vor-dem-ersten-token-zaehlt-als-inhaltlicher.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, neun
  Kaskaden gelaufen. Firmennetz mit Pflicht-Proxy: direkter Egress auf 443 wird
  verworfen.

## Was passiert ist

Die Fixer-Rolle wurde auf einen Fund angesetzt, ohne dass der Firmenproxy in
der Umgebung stand. Abo-Aufruf **und** API-Fallback endeten beide so:

```
API Error: Connection refused — a firewall or proxy may be blocking it
           (ConnectionRefused)
terminal_reason: api_error
num_turns     : 0
total_cost_usd: 0.0000
```

Null Turns, null Kosten — kein Modell hat den Fund je gesehen. Die Rolle
wertete das trotzdem als **inhaltlichen Fehlversuch**: Rollback, und der
Fehlversuchszähler bekam einen Eintrag für diesen Fund.

Nach drei solchen Netzaussetzern stünde der Fund auf `an Axel übergeben` — die
teuerste Rolle des Teams, angesetzt auf ein Problem, das nie ein Modell erreicht
hat. Der Zähler misst dann eine Rollenleistung, die es nicht gab.

## Wo es steckt

In der Fixer-Rolle des Entrypoints (`frank.*`), an der Stelle, die den
Fehlversuchszähler fortschreibt.

**Die Unterscheidung existiert dort bereits — sie ist nur zu eng gezogen.** Der
Zweig, der das Session-Limit behandelt (Exit 42), nimmt den Zähler ausdrücklich
aus, mit genau der richtigen Begründung: *„kein inhaltlicher Fehlversuch, die
Rolle kam nie zum Zug."* Ein `ConnectionRefused` mit **0 Turns und 0.0000 USD**
ist exakt dieselbe Klasse — er fällt aber in den generischen Exit 1 und wird
gezählt.

## Warum das jede Installation trifft

Der Fehler sitzt im Entrypoint, nicht im Projekt: Jede Installation hinter
einem Proxy, in einem VPN mit Aussetzern oder mit kurzem Netzabriss zählt
Fehlversuche, die keine sind — und eskaliert dadurch früher auf die teuerste
Rolle.

Es ist zudem die **dritte** Variante desselben Musters aus diesem Feld: Eine
Klasse von Ausgängen, die die Rolle nicht zu verantworten hat, wird wie ein
inhaltlicher Fehler behandelt. Die beiden anderen sind das Session-Limit
(bereits gelöst, Exit 42) und der Ausgang „Sitzung beendet, Auftrag
unquittiert" (gemeldet, dort ist die Auswertung zwischen bauender und fixender
Rolle asymmetrisch). Ein gemeinsamer Begriff wäre vermutlich sauberer als drei
Einzelzweige: **Was 0 Turns und 0.0000 USD kostet, ist nie ein inhaltlicher
Fehlversuch.** Das ist maschinell prüfbar und trifft alle drei Fälle.

## Was ich schon versucht habe

Kein Eingriff in den Entrypoint — der Fund sitzt im Kit und hielte lokal nur
bis zum nächsten `--update`. Lokal wurde ausschließlich der Zählerstand
repariert, weil er eine Leistung maß, die es nicht gab.

**Betriebshinweis als Behelf, mit Beleg:** Rollenläufe auf dieser Maschine
immer mit gesetztem Proxy starten. Der folgende Kaskadenlauf fuhr zehn
Rollenaufrufe mit Proxy und hatte **keinen einzigen** 0-Token-Netzfehlversuch;
der Lauf davor hatte zwei. Der Behelf trägt also — er ist nur Handdisziplin,
und genau deshalb bleibt die Meldung fällig.

**Anmerkung zur Beweislage:** Die Rohlogs zu den beiden ursprünglichen
Fehlversuchen sind inzwischen weg (Logordner sind gitignoriert und werden beim
Kostenabschluss zusätzlich archiviert). Die Zahlen oben stammen aus dem
Backlog-Eintrag, der sie beim Auftreten festgehalten hat.

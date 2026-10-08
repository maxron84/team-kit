# Abgelaufene Abo-Anmeldung faellt als Limit in den API-Fallback, und der Rest des Laufs zahlt ueber die API

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-30-abgelaufene-abo-anmeldung-faellt-als-limit-in-den-api-fallba.md
      .\kit-melden.cmd ablegen  2026-09-30-abgelaufene-abo-anmeldung-faellt-als-limit-in-den-api-fallba.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-30-abgelaufene-abo-anmeldung-faellt-als-limit-in-den-api-fallba.md   # sonst: Pull Request

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
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python mit Electron-Oberfläche; Vollautomatik-Lauf mit elf Stufen über rund sieben Stunden, Loop-Rollen Abo-first mit hinterlegtem API-Schlüssel

## Was passiert ist

Mitten in einem Vollautomatik-Lauf lief die Abo-Anmeldung der CLI ab. Die
Ralph-Stufe, die gerade arbeitete, brach nach 71 Turns und 43 Minuten ab. Ihr
Rohlog trägt `is_error: true` und im Feld `result` wörtlich:

> Failed to authenticate: OAuth session expired and could not be refreshed

Der Loop meldete dazu:

> [ralph] Abo-Aufruf fehlgeschlagen (Timeout/Limit/429?) — einmaliger API-Fallback.

Der API-Aufruf setzte auf dem uncommitteten Stand fort und schloss die Stufe
ab. Die **nächsten beiden Stufen** begannen wieder im Abo, scheiterten dort
nach **einem Turn und 0 USD** mit demselben Wortlaut und liefen dann ganz über
die API. Echt abgerechnet wurden so rund 12,5 USD. Ohne einen Abbruch aus
anderem Grund wäre jede weitere Stufe des Laufs denselben Weg gegangen. Eine
Probe zwei Stunden später ohne API-Schlüssel (`claude -p … --model haiku`)
lief im Abo durch: Es war kein Limit, sondern die Anmeldung.

## Wo es steckt

`team/lib.psm1`, `team_claude`, der Zweig mit dem Text *Abo-Aufruf
fehlgeschlagen (Timeout/Limit/429?) — einmaliger API-Fallback* (bei uns um
Zeile 1965). Jeder Fehler eines Abo-Aufrufs landet dort gleich. Die Ursache
steht nur im `result`-Feld des Rohlogs.

## Warum das jede Installation trifft

Der Fallback ist aufruf-lokal gebaut, weil ein Limit vorübergeht: Der nächste
Aufruf versucht es wieder im Abo. Eine abgelaufene Anmeldung geht **nicht** von
selbst vorüber. Jeder weitere Aufruf scheitert im Abo sofort, und der Lauf
wechselt faktisch dauerhaft auf die API, ohne dass eine Zeile das sagt. Die
Meldung nennt dabei Timeout oder Limit als Grund. Wer das Log liest, sucht dann
das Kontingent, nicht die Anmeldung.

Zwei Folgen, die jede Installation mit hinterlegtem API-Schlüssel trifft:

1. **Echtes Geld für Stunden, in denen ein Mensch nur hätte neu anmelden
   müssen.** Das Anmelden ist Menschenarbeit wie das Warten auf ein
   Session-Limit, für das es den Pausen-Exit 42 gibt.
2. **Die Kostenachse verrutscht still.** Die Stufen stehen danach unter
   `api`, der Abschlussbericht zeigt keinen Grund.

## Vorschlag

Den Wortlaut erkennen (`Failed to authenticate`, `OAuth session expired`) und
als eigene Klasse behandeln: in der Meldung den Grund nennen und den Lauf
**anhalten** statt den Rest über die API zu fahren, analog zu Exit 42, mit
einer Zeile, was zu tun ist (neu anmelden, dann denselben Lauf erneut
starten). Mindestens aber die Meldung korrigieren: Der Grund aus `result`
gehört in die Zeile, die der Mensch liest.

## Was ich schon versucht habe

Nichts am Kit geändert. Der Lauf wurde aus anderem Grund nach der dritten
betroffenen Stufe angehalten (Exit 43); vor dem Neustart ist die Anmeldung
per Probe geprüft worden. Im Projekt steht der Fall im Backlog.

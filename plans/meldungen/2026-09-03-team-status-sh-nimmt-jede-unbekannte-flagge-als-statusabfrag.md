# team-status.sh nimmt jede unbekannte Flagge als Statusabfrage entgegen und meldet Erfolg

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-09-03-team-status-sh-nimmt-jede-unbekannte-flagge-als-statusabfrag.md
      ./kit-melden.sh ablegen  2026-09-03-team-status-sh-nimmt-jede-unbekannte-flagge-als-statusabfrag.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-09-03-team-status-sh-nimmt-jede-unbekannte-flagge-als-statusabfrag.md   # sonst: Pull Request

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
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, kompilierte Sprache mit
  eigenem Test-Runner (nicht Python), dreizehn Kaskaden gebaut, rund 563 Tests,
  gut 180 abgerechnete headless-Laeufe im Bestand

## Was passiert ist

Beim Kostenabschluss einer Kaskade wollte ich die Bedienhinweise sehen und rief:

```
./team-status.sh --hilfe
```

Erwartet: eine Nutzungszeile, oder wenigstens „unbekannte Option".
Bekommen: die **normale Statusausgabe** — Kaskadenstand, Beutebuch,
Kostenblock, letzte Commits — und **Exit `0`**.

Gegengeprobt mit einer Zeichenkette, die niemand versehentlich tippt:

```
./team-status.sh --voelliger-unsinn-xyz ; echo "exit=$?"
```

Dasselbe: volle Statusausgabe, `exit=0`. Es gibt keine Flagge, die das Skript
zurückweist.

## Wo es steckt

`team-status.sh`, der Dispatcher ganz am Dateiende. Er ist eine
`if`/`elif`-Kette über `"${1:-}"` — `--budget`, `--akteur-abschluss`,
`--rollen-abschluss`, `--ledger-pruefen`, `--altlast`,
`--beutebuch-archivieren`, `--watch` — und endet mit:

```sh
else
    status_einmal
fi
```

Dieses `else` ist als „ohne Argument zeige den Status" gemeint, fängt aber
**jedes** Argument, das keinem Zweig entspricht — auch jedes, das mit `--`
beginnt.

Bemerkenswert: Das Skript kann es besser und tut es an anderer Stelle
bereits. In derselben Datei steht für den Buchungsmodus

```sh
*) echo "Unbekannter Modus '$modus' — erlaubt: --addieren, --ersetzen" >&2
```

Die Zurückweisung existiert also als Muster; sie fehlt nur auf der obersten
Ebene, wo sie am meisten trüge.

## Warum das jede Installation trifft

Der Fehler steckt in einem Entrypoint des Kits, nicht in Projektcode — jede
Installation hat dieselbe Kette.

**Der Schaden ist nicht die fehlende Hilfe, sondern das falsche Erfolgssignal.**
Alle schreibenden Verben dieses Skripts sind Kostenbuchungen, und ihre Namen
sind lang und leicht zu verfehlen: `--rollen-abschluss`,
`--architekt-abschluss`, `--akteur-abschluss`, `--ledger-pruefen`. Ein Tippfehler
in einem davon — ein fehlendes `s`, ein deutsches `ß`, `--ledger-pruefe` —
bucht **nichts**, druckt eine plausibel aussehende Statusausgabe und endet mit
`0`. Wer das im Rahmen einer Sequenz oder in einem Skript aufruft, sieht
Zeilen vorbeiziehen und hakt den Schritt ab.

Genau dafür gibt es in diesem Kit bereits eine Lehre: `Kit-BL-165` („Eine
Sitzung ohne Closeout bucht ihre Kosten selbst") entstand daraus, dass
Kosten unbemerkt nie im Ledger landeten — im Feld waren das an einem Tag
43,90 USD Abo-Gegenwert. Ein stillschweigend ignoriertes Buchungsverb ist
derselbe Ausgang über einen anderen Weg, und diesmal meldet das Werkzeug
sogar aktiv Erfolg.

Dazu kommt der gewöhnliche Fall: `--hilfe`, `--help` und `-h` sind das Erste,
was ein neuer Anwender tippt. Er bekommt eine Ausgabe, die aussieht, als wäre
sie die Antwort, und erfährt nie, dass es sieben weitere Verben gibt.

## Was ich schon versucht habe

Nichts lokal repariert — der Fix gehört ins Kit, nicht in eine Kopie, die bei
jedem Update wieder überschrieben wird.

Vorschlag, zwei Zeilen an derselben Stelle:

```sh
elif [ "${1:-}" = "--hilfe" ] || [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    status_nutzung
elif [ "${1:-}" != "" ]; then
    echo "Unbekannte Option '${1}' — erlaubt: --budget, --akteur-abschluss," \
         "--rollen-abschluss, --ledger-pruefen, --altlast," \
         "--beutebuch-archivieren, --watch, --hilfe" >&2
    exit 2
else
    status_einmal
fi
```

Der Kern ist die **zweite** Bedingung: Das argumentlose `status_einmal` bleibt
erhalten (davon hängen `./team-status.sh` in der Bedienanleitung und die
Abschlussausgabe der Vollautomatik ab), aber ein nicht erkanntes Argument
endet mit einem Exit ungleich `0`. Der Exit-Code ist dabei wichtiger als der
Text: Er ist das, was ein aufrufendes Skript auswerten kann — dieselbe
Trennung, die `geraet.sh --pruefen` nach `Feld E`s `CF-34` bekommen hat
(Text für den Menschen, Code für den Aufrufer).

Die Bahn-Parität wäre mitzuziehen: `team-status.ps1` hat vermutlich dieselbe
Bauform.

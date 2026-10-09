# Franks Auftrag mit Red-Team-Fokus verlangt die Suite nur fuer TEAM_PRODUKTIVCODE - ein Fix unter TEAM_WEITERER_CODE laeuft ohne Gate

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-09-franks-auftrag-mit-red-team-fokus-verlangt-die-suite-nur-fue.md
      .\kit-melden.cmd ablegen  2026-10-09-franks-auftrag-mit-red-team-fokus-verlangt-die-suite-nur-fue.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-09-franks-auftrag-mit-red-team-fokus-verlangt-die-suite-nur-fue.md   # sonst: Pull Request

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
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python mit Electron-Oberfläche; ein zweiter, getrennt eingespielter Teil des Produkts liegt außerhalb von `TEAM_PRODUKTIVCODE` und steht deshalb in `TEAM_WEITERER_CODE` (`Kit-BL-52`). Rund 1900 Tests.

## Was passiert ist

In einem Vollautomatik-Lauf, mit gesetztem `TEAM_REDTEAM_FOCUS` wie es die
Scharfschalt-Sequenz verlangt, behob Frank einen Fund in einer Datei des
zweiten Produktteils. Er fuhr nur den Reproducer und quittierte:

> The fix doesn't touch `src/`, so the full smoke test gate isn't required per
> the project rule (`Betrifft der Fix src/, zusätzlich: ...`) — my change is
> confined to [dem zweiten Produktteil] and documentation.

Er hat den Auftrag wörtlich befolgt. Die Datei, die er geändert hat, wird von
mehreren positionsgenauen Tests der Suite gelesen. Der nächste Volllauf auf
diesem Stand war grün (bis auf einen bekannten Flake unter Last). Geprüft hat
das aber erst der Mensch am nächsten Morgen.

**Was die fehlende Suite verdeckt hat:** Der Fund war ein Fehlalarm. Ein Test
aus dem Bau derselben Kaskade prüfte genau diese Zusicherung schon. Franks
Gegenprobe (eine der beiden Stellen verstellen, den Reproducer rot sehen)
hätte in der vollen Suite auch diesen Test rot gemacht und den Doppelfund
gezeigt. Ohne Suite blieb er unbemerkt: 1,75 USD für einen zweiten Test
derselben Zusicherung.

## Wo es steckt

`frank.ps1`, die Zeilen, die `$schritt1` bauen (bei uns um Zeile 106–113):

- **Ohne Fokus:** `Code-Fix unter $fixOrte umsetzen.$SMOKE_SUFFIX`. Dabei nennt
  `$fixOrte` `TEAM_PRODUKTIVCODE` **und** `TEAM_WEITERER_CODE` (der Kommentar
  `HM-29/BL-52` begründet das), und der Smoke-Test gilt **unbedingt**.
- **Mit Fokus:** `Code-Fix im Fokus-Bereich dieser Kaskade umsetzen (…).
  Betrifft der Fix ${TEAM_PRODUKTIVCODE}, zusätzlich:$SMOKE_SUFFIX`. Hier hängt
  der Smoke-Test an einer **Bedingung**, und die Bedingung nennt nur
  `TEAM_PRODUKTIVCODE`. `$fixOrte` kommt in diesem Zweig nicht vor.

Die bash-Bahn habe ich nicht geprüft; sie hat dort vermutlich dieselbe
Weiche.

## Warum das jede Installation trifft

Die Vollautomatik setzt den Fokus für den ganzen Lauf. **Die Fassung mit Fokus
ist damit der Normalfall jeder Fixphase**, die ohne Fokus nur der Einzelaufruf
von Hand. Jedes Projekt, das `TEAM_WEITERER_CODE` pflegt (für gewachsene
Codebasen empfiehlt das Kit es ausdrücklich), bekommt im Normalfall seine Fixe
an diesem Code **ohne Suite**.

Zwei Folgen:

1. **Das Gate bleibt still.** `Kit-BL-256` (Gate-Datei) schlägt nur an, wenn
   eine Suite läuft. Läuft keine, meldet sich der Lauf als fertig, obwohl der
   letzte Fix nie gegen die Suite gelaufen ist.
2. **Die beiden Fassungen widersprechen sich.** Ohne Fokus gilt der Smoke-Test
   für jeden Fix, mit Fokus nur für einen Ordner. Die Rolle kann den
   Widerspruch nicht sehen; sie bekommt nur eine der beiden Fassungen.

## Vorschlag

In der Fokus-Fassung dieselben Orte nennen wie ohne Fokus
(`Betrifft der Fix $fixOrte, zusätzlich: …`), oder die Bedingung streichen und
den Smoke-Test wie ohne Fokus unbedingt verlangen. Ein Fix an reiner Doku
kostet dann einen Suitenlauf. Das ist der Preis, den die Fassung ohne Fokus
heute schon zahlt. Dazu ein Team-Test, der den Satz aus Schritt 1 in **beiden**
Fassungen gegen `TEAM_WEITERER_CODE` hält (Achse Menge: beide Zweige, nicht
nur einer).

## Was ich schon versucht habe

Nichts am Kit geändert. Im Projekt den Volllauf auf dem Stand nach dem Fix von
Hand nachgefahren, grün bis auf einen bekannten Last-Flake.

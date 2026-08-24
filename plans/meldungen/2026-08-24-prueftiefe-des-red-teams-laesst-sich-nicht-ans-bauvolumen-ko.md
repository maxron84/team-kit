# Prueftiefe des Red Teams laesst sich nicht ans Bauvolumen koppeln - ein zweiter Sweep ueber denselben Bau ist gesperrt

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-08-24-prueftiefe-des-red-teams-laesst-sich-nicht-ans-bauvolumen-ko.md
      ./kit-melden.sh senden   2026-08-24-prueftiefe-des-red-teams-laesst-sich-nicht-ans-bauvolumen-ko.md

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Verbesserungsvorschlag
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter. Drei
  Kaskaden gebaut und abgeschlossen, alle Rollen im Abomodus.

## Was passiert ist

Im Closeout der dritten Kaskade habe ich zum ersten Mal die **Prüftiefe je
gebauter Zeile** über alle bisherigen Läufe gerechnet:

| | gebaute Zeilen (Produktiv + Test) | Sweep-Turns (Harry + Marv) | Turns je 1 000 Zeilen | Funde |
|---|---|---|---|---|
| Kaskade 1 | 988 | 56 | 57 | 3 |
| Kaskade 2 | 2 950 | 57 | 19 | 2 |
| Kaskade 3 | 3 959 | 79 | 20 | 2 |

Der Sweep läuft **einmal je Lauf**, unabhängig davon, ob 1 000 oder 4 000
Zeilen entstanden sind. Seit Kaskade 2 liegt die Prüfdichte bei rund einem
Drittel des Werts der ersten Kaskade.

Zwei Lesarten sind beide plausibel — der Code ist besser geworden (die Pläne
gießen frühere Funde inzwischen ausdrücklich in Zusicherungen), oder es wird
schlicht weniger tief gesucht. **Beide sagen dasselbe über die Mechanik: Es
gibt keine Stellschraube.** Der Stakeholder hat daraufhin entschieden, die
Prüftiefe an das Bauvolumen zu koppeln — und dabei stellte sich heraus, dass
genau das mit dem heutigen Kit nicht geht.

## Wo es steckt

Zwei Stellen, die zusammen die Kopplung verhindern:

1. **`vollautomatik.sh`** ruft die Sweeps in einer festen Schleife auf:
   `for rolle in harry marv; do ./"$rolle".sh; …; done`. Es gibt keine
   Env-Variable für eine zweite Runde — anders als bei den Fix-Runden, die mit
   `TEAM_MAX_RUNDEN` und `TEAM_FIX_MAX_STAGNATION` gleich zwei Stellschrauben
   haben.

2. **`team/redteam.sh`** sperrt einen zweiten Durchgang ohnehin:

   ```
   HEAD_HASH="$(git rev-parse HEAD)"
   LAST="$( [ -f "$STATE_FILE" ] && cat "$STATE_FILE" || echo "" )"
   if [ "$LAST" = "$HEAD_HASH" ]; then
       echo "[$ROLLE] Kein neuer Commit seit letztem Sweep …"
       exit 3
   fi
   ```

   Ein sofortiger zweiter `./harry.sh` meldet „nichts zu tun" und kostet
   nichts, weil er nichts tut. Die Sperre ist **richtig** — sie verhindert, dass
   derselbe Bereich zweimal geprüft und zweimal bezahlt wird (`BL-30` nennt
   genau diesen Fall). Sie macht aber zugleich jede Form von zweitem
   Prüfdurchgang unmöglich, auch einen gewollten.

**Die Prüftiefe ist damit die einzige Größe des Loops, die sich nicht regeln
lässt.** Budget: regelbar. Fix-Runden: regelbar. Stagnation: regelbar. Modell:
regelbar. Prüftiefe: nicht.

## Warum das jede Installation trifft

Die feste Schleife und die Sweep-Marke werden vom Kit ausgeliefert. Der Effekt
skaliert mit dem Erfolg des Loops: Je länger ein Projekt läuft, desto größer
werden die Kaskaden — und desto dünner wird der Sweep je Zeile, ohne dass sich
irgendwo eine Zahl ändert, die jemand beobachtet. Der Statusbericht zeigt
Kosten und Fundzahl, aber nichts, was die beiden ins Verhältnis zum
Bauvolumen setzt.

Besonders unangenehm: Ein dünner werdender Sweep **sieht aus wie Erfolg**. Die
Fundzahl sinkt, und „weniger Funde" liest sich wie „besserer Code". Ohne die
dritte Spalte ist beides nicht zu unterscheiden.

## Was ich schon versucht habe

- **Zweiter Sweep von Hand**: `./harry.sh` direkt nach dem Lauf. Exit 3, wie
  erwartet — die Sweep-Marke steht auf `HEAD`.
- **Verworfen: die Marke zurücksetzen.** Das umgeht eine Sperre, die es aus
  gutem Grund gibt, und liefert obendrein wenig: gleicher Bereich, gleicher
  Prompt, gleiches Modell → im Wesentlichen dieselbe Ausbeute. Was Tiefe
  brächte, wäre ein zweiter Durchgang mit **anderem Blickwinkel**, nicht
  derselbe noch einmal.
- **Lokal umgesetzt, was ohne Kit-Änderung geht:** eine Planungsregel für den
  Architekten — über ~2 500 gebaute Zeilen wird die Kaskade in **zwei Läufe**
  geteilt. Das ergibt zwei Sweeps mit je eigenem Fokus über je eine Hälfte und
  ist mit der heutigen Mechanik der einzige Weg zu einem zweiten Durchgang. Er
  ist sogar der bessere: Zwei Fokus-Strings über zwei Hälften sehen mehr als
  zweimal derselbe über das Ganze. Aber es ist eine **Prosa-Auflage in einer
  Projektdatei** — sie hängt an meiner Disziplin, nicht an einer Mechanik, und
  überlebt kein `--update`.

**Vorschläge, in aufsteigendem Aufwand:**

1. **Sichtbar machen, bevor man es regelt.** Eine Zeile im Abschlussbericht:
   Sweep-Turns je 1 000 gebauter Zeilen, neben der Fundzahl. Das ist die
   Kennzahl, die den Verfall überhaupt erst zeigt — bei uns ist er drei
   Kaskaden lang unbemerkt geblieben, weil ihn niemand ausgerechnet hat.
2. **Eine Warnschwelle**, analog zur Budget-Warnung bei 80 %: Liegt das
   Bauvolumen eines Laufs über einem konfigurierbaren Wert
   (`TEAM_SWEEP_MAX_ZEILEN`?), sagt der Lauf es beim Sweep — „4 000 Zeilen mit
   einem Durchgang geprüft".
3. **Ein zweiter Durchgang mit anderem Blickwinkel**, wenn die Schwelle
   überschritten ist: derselbe Bereich, aber ein zweiter Fokus-String
   (`TEAM_REDTEAM_FOCUS_2`?), der die Sweep-Marke ausdrücklich ignorieren darf.
   Die Sperre bliebe für den Normalfall unangetastet; sie würde nur für einen
   **benannten, bezahlten** zweiten Durchgang aufgehoben.

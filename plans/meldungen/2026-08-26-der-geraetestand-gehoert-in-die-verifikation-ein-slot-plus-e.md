# Der Gerätestand gehört in die Verifikation — ein Slot plus Exit-Code-Vertrag statt eines Merksatzes

- **Art**: Verbesserungsvorschlag (kein Fehler — nichts im Kit ist kaputt, es
  fehlt eine Stelle)
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Bestand, Linux, bash-Bahn, Dart/Flutter mit
  Android-Ziel, sechs Kaskaden gebaut, ~7.000 Zeilen Produktivcode, 277 Tests

## Worum es geht

Das Kit hat ein Sicherheitsnetz fuer die Frage „ist der Code richtig?"
(`TEAM_SMOKE_TEST`) und eine ausgearbeitete Regel dagegen, dass sich dieses Netz
den Erfolg selbst einrichtet („Der Smoke-Test darf keine Umgebung setzen, die
die Doku nicht nennt").

Es hat **keine** Stelle fuer die Frage **„ist das, was ich von Hand pruefe,
ueberhaupt das, was ich gebaut habe?"**

Bei einem Projekt, dessen Verifikationsziel ein Geraet ist, ist das eine eigene
Fehlerklasse. Der Smoke-Test kann sie prinzipiell nicht sehen: Er laeuft im
Host, das Artefakt liegt auf dem Geraet.

## Der Fall, aus dem der Vorschlag kommt

Vor der entscheidenden Handpruefung einer Kaskade lag auf dem Emulator noch der
Bau von **vor** dieser Kaskade. Nichts deutete darauf hin: Die App startete, das
Profil war da, sie sah benutzbar aus. Die Handpruefung sollte eine
Verhaltensfrage entscheiden („liegt es an der Wortwahl oder an der Skala?") und
haette am alten Mechanismus gemessen — mit dem Ergebnis „die Skala ist schuld"
fuer eine Wortwahl, die nie geprueft war. Ein falsches Ergebnis, das eine ganze
Folgekaskade begruendet haette.

Daneben lag ein Zwilling unter der alten `applicationId` aus
`flutter create`, im Launcher gleich benannt, mit eigenem Icon. Wer das falsche
Symbol antippt, misst eine App von vor sechs Kaskaden.

Beides ist headless unsichtbar und faellt ohne Versionsvergleich nicht auf.

## Was der Merksatz nicht geleistet hat

Erste Reaktion war ein projekteigenes Skript plus eine Zeile in der
Regeldatei: „**Vor jeder Handpruefung aufrufen.**"

Das ist genau die Bauart, von der das Kit an anderer Stelle schon weiss, dass
sie nicht traegt: **ein Vermerk, der an keiner Mechanik haengt.** Im Backlog
dieses Projekts stehen dafuer zwei dokumentierte Vorlaeufer — ein Eintrag „faellig
vor dem Start der naechsten Kaskade" blieb liegen, weil der Start ohne ihn
erfolgte, und ein anderer wurde eigens dafuer aufgeschrieben, dass er liegen
bleibt, und blieb danach eine weitere Kaskade liegen.

Der Merksatz haengt daran, dass ein Mensch im richtigen Moment daran denkt. Er
hat hier genau einmal funktioniert, naemlich als er neu war.

Der Stakeholder hat daraus die staerkere Regel gemacht: **nicht** „vor der
Handpruefung", sondern **„nach jeder Aenderung an buildbarem Code, von der Rolle
selbst, die sie gemacht hat"**. Damit haengt sie an einer Handlung, die
tatsaechlich stattfindet, statt an einer Erinnerung.

## Warum das kein Android-Thema ist

Der Satz „das Artefakt, das ich von Hand pruefe, ist nicht das Artefakt, das ich
gerade gebaut habe" enthaelt nichts Android-spezifisches. Er trifft jedes
Projekt mit einem Schritt zwischen Bau und Pruefung:

- iOS (Simulator/Geraet, dieselbe Mechanik, anderes Werkzeug)
- Firmware und Embedded (geflashter Stand gegen gebauten Stand)
- Desktop-Installer (installierte Version gegen gebaute)
- Container-Images (laufender Tag gegen gebauten Digest — derselbe Fehler, und
  `:latest` macht ihn zum Normalfall)
- jede Web-App mit Deploy-Schritt (ausgelieferter Build gegen HEAD)

Ueberall ist die Frage dieselbe und die Antwort ein anderes Werkzeug. Das ist
genau der Zuschnitt, den das Kit bei `TEAM_SMOKE_TEST` schon hat: **Das Kit
kennt die Frage und die Vertragsform, das Projekt liefert den Befehl.**

## Vorschlag

Vier Teile, der zweite ist der wichtigste.

**1. Ein Slot in `team.config.sh`, leer als Default.**

```sh
# Befehl, der prueft, ob das Deploy-Ziel den gebauten Stand traegt.
# Leer = dieses Projekt hat keinen Schritt zwischen Bau und Pruefung.
TEAM_ZIELSTAND_CHECK="${TEAM_ZIELSTAND_CHECK:-}"
TEAM_ZIELSTAND_HERSTELLEN="${TEAM_ZIELSTAND_HERSTELLEN:-}"
```

Leer bedeutet leer: Wer keinen Deploy-Schritt hat, merkt von der Sache nichts.
Wie bei `TEAM_WEITERER_CODE` ist der leere Wert in einem frischen Projekt zu
Recht leer — und in einem gewachsenen der Unterschied zwischen „geprueft" und
„sieht geprueft aus".

**2. Der Exit-Code-Vertrag — der Teil, der ohne das Kit nicht entsteht.**

| Exit | heisst |
|---|---|
| `0` | Ziel traegt den gebauten Stand, keine Altlasten — nichts zu tun |
| `1` | weicht ab **oder** Altlasten vorhanden — `TEAM_ZIELSTAND_HERSTELLEN` faellig |
| `3` | **nicht pruefbar** (kein Werkzeug, kein Geraet, mehrdeutig) |

Diesen Vertrag zu definieren ist der eigentliche Ertrag. Unser eigenes Skript
gab in seiner ersten Fassung **immer `0`** zurueck; der Befund stand
ausschliesslich als deutscher Fliesstext auf dem Bildschirm („`-> WEICHT AB.`").
Eine Regel, die daran haengt, haengt an einer Wortwahl — jede Automatik haette
Prosa greppen muessen. Wir haben die drei Codes lokal nachgezogen und beide
Pfade gegengeprobt. Aber: **Jedes Projekt wuerde diese Codes anders erfinden**,
und dann trifft die Regel im naechsten Projekt auf ein Skript mit anderer
Semantik. Genau das ist die Sorte Festlegung, fuer die es ein Kit gibt.

Wichtig ist die Trennung von `1` und `3`. „Kein Geraet angeschlossen" ist
**kein** Erfolg und **kein** Handlungsbedarf, sondern **„die Pruefung hat nicht
stattgefunden"**. Wird das mit `0` verwechselt, entsteht derselbe Schaden wie
bei einem gruenen Test ueber nie ausgefuehrtem Code: Es sieht geprueft aus, weil
ein Befehl gelaufen ist.

**3. Die Regel in die Rollen-Briefings — und zwar rollenscharf.**

Nur die **interaktiven** Rollen: Der Architekt (im Ausnahmefall), Frank, der
Mensch. Sie fahren den Check nach jeder eigenen Aenderung an buildbarem Code
selbst und handeln nach dem Code; Exit `3` gehoert in die Antwort an den
Menschen, nicht in die Ablage.

**Nicht die headless-Rollen.** Ralph laeuft ohne garantiertes Geraet — dort
wuerde ein Exit `3` eine sonst gruene Stufe zum Fehlschlag machen, und ein
`flutter build` je Stufe kostet Zeit fuer nichts. Harry, Marv und Axel aendern
ohnehin nichts Buildbares. Fuer den Loop bleibt der Smoke-Test das Netz; der
Zielstand wird **nach** dem Lauf hergestellt, von der Rolle, die als Naechste
etwas aendert, oder vom Menschen vor der Handpruefung.

Dazu gehoert eine Definition, was „buildbarer Code" ist — bei uns: was das
Artefakt veraendert (`lib/`, `pubspec.yaml`, `android/`, Assets), **nicht**
Plan-Dokumente, CHANGELOG, Backlog, Beutebuch oder `team/`. Dort einen Bau
anzustossen kostet Zeit und beweist nichts.

**4. Eine Zeile im Statusbericht.** Ist `TEAM_ZIELSTAND_CHECK` gesetzt, gehoert
sein Ergebnis dorthin, wo der Mensch ohnehin hinsieht — samt „nicht pruefbar"
als eigener Zustand. Das ist der Unterschied zwischen einer Regel, an die man
sich erinnern muss, und einem Zustand, den man sieht.

## Was der Vorschlag nicht kann, damit er nicht mehr verspricht als er haelt

Das Kit kann **nicht** pruefen, ob eine Rolle den Check wirklich gefahren hat.
Punkt 3 ist eine Prompt-Auflage, keine Mechanik — dieselbe Kategorie wie die
Read-Only-Regel fuer Harry und Marv, und mit derselben Grenze. Der Gewinn liegt
in den Punkten 1, 2 und 4: Der Befehl hat einen Ort, sein Ergebnis eine
verlaessliche Form, und der Zustand ist sichtbar. Das ist deutlich mehr als ein
Merksatz, aber es ist kein Guard.

Ebenso: Ein Versionsvergleich beweist, dass **Version und Build-Nummer**
uebereinstimmen. Er beweist nicht, dass das Artefakt bitgleich ist. Fuer die
Klasse Fehler, um die es hier geht — „der Stand ist eine Kaskade alt" —
genuegt das; wer mehr braucht, vergleicht Hashes, und das gehoert dann ins
Projektskript, nicht in den Vertrag.

## Was ich schon getan habe

Lokal vollstaendig gebaut, und zwar in der Form, die dieser Vorschlag
verallgemeinert:

- Das projekteigene Pruefskript liefert jetzt die drei Exit-Codes oben. Beide
  neuen Pfade gegengeprobt: `0` am aktuellen Emulator, `1` mit kuenstlich
  abweichender gebauter Version in einer Wegwerf-Kopie, ohne Geraet oder Repo
  anzufassen. Der Fliesstext blieb unveraendert — er ist fuer den Menschen.
- Die Regel steht in der Regeldatei des Projekts, rollenscharf, mit der
  Definition von „buildbarer Code" und mit der ausdruecklichen Auflage, Exit `3`
  zu **melden** statt zu verschweigen.
- Kein Aufrufer war betroffen; das Skript wird bisher nur von Menschen und aus
  der Doku aufgerufen.

Der Punkt „Zeile im Statusbericht" fehlt hier bewusst: Er liegt in
`team-status.sh`, also im Kit, und ein lokaler Eingriff dort haette die bekannte
Verfallszeit beim naechsten `--update`.

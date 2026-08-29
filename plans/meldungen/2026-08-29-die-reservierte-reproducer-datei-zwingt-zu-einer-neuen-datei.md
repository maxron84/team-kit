# Die reservierte Reproducer-Datei zwingt zu einer neuen Datei, auch wenn der Nachweis in eine bestehende gehoert

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter mit SQLite;
  acht gebaute Kaskaden, rund 38 Funde im Beutebuch, alle über den regulären
  Beutezug-Dreisatz.

## Was passiert ist

Ein Closeout-Fund (`HM-36`) verlangte einen Versionsbump und dazu das
**Nachziehen einer bestehenden Sperrklinken-Testdatei**. Der eigene Backlog
führt dazu seit drei Kaskaden eine Auflage: Jede Kaskade mit Nutzerwirkung legt
sonst eine weitere fast identische Versionstestdatei an; die Empfehlung lautet,
**eine** Datei zu führen und die Vorgänger zu löschen.

Der Fundblock trug regelkonform eine reservierte Reproducer-Zeile mit einem
**neuen** Dateinamen unter der Fundnummer. Frank hat daraufhin beides getan:

1. die bestehende Sammeldatei ausgebaut (die Konsolidierung, die die
   Backlog-Auflage verlangt), **und**
2. die reservierte Datei angelegt (die der Fundblock nennt).

Ergebnis: zwei Dateien mit **identischem Testnamen** und identischer Logik. Der
`diff` beider Dateien ohne Kommentarzeilen nannte genau zwei Unterschiede — einen
im Meldungstext und diesen:

```
Sammeldatei:      expect(build, greaterThanOrEqualTo(5));
reservierte Datei: expect(build, greaterThanOrEqualTo(6));
```

Die schwächere Bedingung stand in der Datei, deren Kopfkommentar behauptete, den
Nachweis der aktuellen Kaskade zu führen. Wer der Konsolidierungs-Auflage folgt
und das Duplikat löscht, lässt die stärkere Bedingung **still** verschwinden:
Der Test bleibt grün, die Zusicherung ist weg, der Kommentar sagt weiterhin, sie
sei da. Aufgefallen ist es erst beim Abnehmen des Fixes durch den Architekten,
über einen `diff` der beiden Dateien — nicht durch einen roten Test.

## Wo es steckt

**Nicht in der Mechanik.** `team_diff_beruehrt_fund` (`bash/lib.sh:1210`) prüft,
ob **irgendeine** im Fundblock backtick-referenzierte Datei im Diff vorkommt —
eine **bestehende** Datei genügt ihm vollständig. Der Anker hat den Fix, der die
Zeile später auf die Sammeldatei umbog, anstandslos akzeptiert.

Es steckt in der **Vorlage und der Regel**:

- `bootstrap/beutebuch.md` und `bootstrap/CLAUDE.md.vorlage` zeigen im
  Fund-Format ausschließlich die Bauform `test/hm<nr>_<stichwort>_test.dart` —
  also immer eine **neue** Datei unter der Fundnummer.
- Der Absatz „Reproducer-Tests nach der Fund-Nummer benennen" verstärkt das mit
  einer guten Begründung (Auffindbarkeit in beide Richtungen), nennt aber keinen
  Fall, in dem der Nachweis in eine bestehende Datei gehört.
- `geteilt/prompts/rolle-frank.md` sagt nichts darüber, ob Frank die
  Reproducer-Zeile **ändern** darf.

Damit reserviert der Finder einen Dateinamen zu einem Zeitpunkt, an dem er noch
nicht wissen kann, ob eine bestehende Datei der bessere Ort ist — und Frank
findet später keine Regel, die ihm das Umbiegen erlaubt. Er gehorcht beiden
Auflagen auf die einzige Art, die ihm offensteht: mit dem Duplikat.

## Warum das jede Installation trifft

Die Regel steht in der ausgelieferten `CLAUDE.md`-Vorlage und in der
Beutebuch-Vorlage; sie gilt damit in jedem Projekt ab dem ersten Fund. Der Fall
selbst ist keine Ausnahme, sondern der **Normalfall bei jeder wiederkehrenden
Zusicherung** — Versionsstände, Schema-Versionen, Sperrklinken, Manifest- und
Konfigurationszusagen. Solche Funde treten mehrfach über die Lebenszeit eines
Projekts auf, und jedes Mal ist die richtige Antwort, die **bestehende** Datei
nachzuziehen, statt eine weitere anzulegen.

Der Schaden ist zudem von der Bauart, die das Kit an anderer Stelle ausdrücklich
bekämpft: Er ist **still**. Das Duplikat ist grün, das Beutebuch zeigt einen
Fund mit Reproducer, und die schwächere Bedingung fällt erst beim nächsten
Aufräumen unbemerkt aus der Suite. Dieselbe Familie wie `BL-15`
(Backtick-Regel), `BL-28` (`strict`-Marker) und `BL-169` (Namensmuster des
Läufers): Der Nachweis sieht aus, als sei er da.

## Was ich schon versucht habe

**Lokal repariert, aber nur den Einzelfall** — als eigener Fund im Beutebuch
(`HM-38`), von Frank im ersten Versuch gebaut: Duplikat gelöscht,
Build-Bedingung in der Sammeldatei nachgezogen, Reproducer-Zeile des
ursprünglichen Fundes auf die Sammeldatei umgebogen. Gegenprobe gefahren (die
Build-Nummer probeweise gesenkt: vorher grün, nachher rot). Das behebt die
Instanz, nicht die Ursache — der nächste Fund derselben Bauart läuft wieder in
dieselbe Wahl.

**Vorschlag, klein und ohne neues Verhalten:**

1. **Vorlage**: Im Fund-Format neben der Bauform `test/hm<nr>_…` einen zweiten
   zulässigen Fall nennen — *„oder der Pfad einer **bestehenden** Datei, wenn
   der Nachweis dorthin gehört"*. Der Substanz-Anker trägt das bereits.
2. **Franks Briefing**: Einen Satz, der ihm das Umbiegen ausdrücklich erlaubt —
   *„Gehört der Nachweis in eine bestehende Datei, ziehe diese nach und biege
   die Reproducer-Zeile des Fundes darauf um, statt eine zweite Datei
   anzulegen; quittiere die Änderung im Fundblock."* Ohne diesen Satz ist die
   reservierte Zeile für ihn eine Anweisung, keine Vorauswahl.
3. **Optional, deckt den Rest**: Ein Hinweis für den Finder, die
   Reproducer-Zeile bei einer **wiederkehrenden** Zusicherung von vornherein
   auf die bestehende Datei zu setzen. Wer den Fund schreibt, weiß in aller
   Regel, ob es dort schon eine gibt.

Die drei sind unabhängig voneinander baubar. Wer nur eines baut, baue (2) — es
trifft den Moment, in dem die Entscheidung tatsächlich fällt.

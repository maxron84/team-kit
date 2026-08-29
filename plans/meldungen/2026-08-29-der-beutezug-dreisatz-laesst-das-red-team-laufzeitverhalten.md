# Der Beutezug-Dreisatz laesst das Red Team Laufzeitverhalten herleiten statt belegen

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: Feld E
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, kompilierte Sprache mit
  eigenem Test-Runner (nicht Python), ~10 Kaskaden gebaut, rund 460 Tests

## Was passiert ist

Ein Read-Only-Red-Team-Lauf meldete einen Fund, dessen Kern die Behauptung
war, eine Sprachkonstruktion mit **verzögerter Initialisierung** (im Zielprojekt
`late`, vergleichbar mit `lazy`/`Lazy<T>`/`@cached_property` anderswo) laufe
bereits beim **Anlegen** des umgebenden Objekts. Der Fund war daraus sauber
hergeleitet, mit Zeilennummern, Klassendoku-Zitat und einem plausiblen
Angriffspfad — er las sich wie ein gutes Stück Arbeit.

Die Konstruktion initialisiert jedoch erst beim **ersten Lesezugriff**, und
der einzige Lesezugriff stand bereits innerhalb des Schutzzweigs. Der Fund
beschrieb damit ein Verhalten, das es nicht gibt.

Aufgefallen ist es erst dem Fixer, beim Nachprüfen vor dem Fix. Er hat es
korrekt widerlegt, dokumentiert — und die Stelle danach trotzdem gehärtet.
Kosten laut den archivierten Rollenlogs: **zwei Fix-Versuche, 50 + 53 Turns,
3,72 USD**. Die drei *echten* Funde derselben Kaskade kosteten zusammen
**2,89 USD**. Der Fehlalarm war damit die teuerste Einzelposition der ganzen
Rollenphase.

## Wo es steckt

In der Regel selbst, nicht im Code:

- `CLAUDE.md`, Abschnitt „Harry & Marv — Read-Only Red Team", **Der
  Beutezug-Dreisatz**
- `team/prompts/rolle-harry.md` und `team/prompts/rolle-marv.md`, jeweils
  „Mein Dreisatz (Beutezug)"

Der Dreisatz verlangt vom Finder Reproschritte, Erwartung, Realität und die
reservierte Reproducer-Zeile. Er verlangt **nirgends**, dass eine behauptete
**Sprachsemantik** vor dem Eintrag ausprobiert wird. Für alles andere ist das
richtig — der Finder soll lesen und angreifen, nicht bauen (`Finder ≠ Fixer`).
Bei einer Sprachkonstruktion ist Lesen aber genau die Methode, die versagt:
Die Semantik steht nicht im gelesenen Code, sondern in der Sprachspezifikation,
und ein Wegwerf-Test hätte sie in fünf Minuten entschieden.

**Die benachbarte Regel gibt es bereits, sie deckt nur die andere Rolle ab.**
Dasselbe Projekt führt eine Auflage an den **Architekten**: Nennt eine
Vertragszeile eine Sprachkonstruktion, wird sie vor dem Schreiben gegriffen.
Sie entstand aus demselben Fehlertyp — gedeckt war damit der **Plan**, nie der
**Fund**.

## Warum das jede Installation trifft

Die Regel steht in `CLAUDE.md` und in zwei Rollen-Briefings unter `team/` —
also in Dateien, die jede Installation mitbringt und die ein `--update`
überschreibt. Jedes Feldprojekt hat damit dieselbe Lücke, und jedes bezahlt
sie einzeln: Ein Fehlalarm dieser Bauart ist für den Fixer nicht billiger als
ein echter Fund, weil er die Ursache erst widerlegen muss, bevor er nichts zu
tun hat.

Der Fehlertyp ist zudem **nicht sprachgebunden**. Kandidaten mit demselben
Muster gibt es überall: verzögerte Initialisierung (`lazy`, `Lazy<T>`,
`@cached_property`), die Reihenfolge von `finally` gegen `return`, ob `assert`
im Auslieferungsbau überhaupt läuft, wann ein `async`-Rumpf zu laufen beginnt,
die Lebensdauer eines UI-Zustandsobjekts. Alle fünf sind Stellen, an denen ein
sorgfältiger Leser eine falsche, aber gut begründete Aussage trifft.

## Was ich schon versucht habe

Lokal umgesetzt und in Betrieb (Entscheid des Stakeholders nach Abwägung von
drei Varianten):

**Eine vierte Zeile im Beutezug-Dreisatz** — sinngemäß: *Behauptet ein Fund
das Laufzeitverhalten einer Sprachkonstruktion, wird es vor dem Eintrag mit
einem Wegwerf-Test belegt, nicht aus der Sprachsemantik hergeleitet. Der Test
wird nicht abgelegt; er ist die Probe, nicht das Ergebnis.* Dazu derselbe
Punkt in beiden Red-Team-Briefings.

**Die zwei verworfenen Varianten, mit ihrem Grund** — sie sind für die Triage
womöglich nützlicher als die gewählte:

1. *Beim Fixer ansetzen* („ein Fund, dessen Ursache sich als widerlegt
   erweist, wird als widerlegt quittiert statt vorsorglich gehärtet"). Billiger
   im Normalfall, greift aber erst **nach** dem ersten bezahlten Versuch — im
   gemessenen Fall hätte es Versuch 2 erspart, Versuch 1 nicht.
2. *Nichts ändern* und den Fehlalarm als Preis des Read-Only-Prinzips buchen.
   Vertretbar bei einem Fall in zehn Kaskaden; verworfen, weil der Preis pro
   Fall über dem eines echten Fundes liegt.

Der gewählte Ort ist der teuerste (er kostet jeden Sweep Turns, auch wenn
nichts zu belegen ist) und der einzige, der **vor** der Übergabe greift.

**Beifang, der eine eigene Prüfung wert sein könnte:** Beide Briefings nannten
den Reproducer-Pfad in Python-Konvention (`test/test_<name>.py`) und
verlangten einen roten Test mit `xfail(strict=True)`. In einem Projekt mit
anderem Test-Runner trägt beides nicht — die Datei wird vom Runner
**stillschweigend nie eingesammelt**, und ein striktes Fehlschlag-Attribut
existiert dort nicht. Die `CLAUDE.md` desselben Projekts beschreibt bereits
die richtige Handhabung; die Briefings widersprachen ihr. Lokal angeglichen.
Für das Kit wäre die Frage, ob diese zwei Stellen aus `team.config.sh`
abgeleitet werden können, statt eine Sprache fest anzunehmen.

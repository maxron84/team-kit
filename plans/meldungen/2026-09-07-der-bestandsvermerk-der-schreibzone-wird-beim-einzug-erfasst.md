# Der Bestandsvermerk der Schreibzone wird beim Einzug erfasst und altert danach still - was das Projekt SPAETER dort ablegt, sieht niemand

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Greenfield beim Einzug, inzwischen elf gebaute
  Kaskaden, rund 460 Tests, knapp 50 Funde; Windows, pwsh-Bahn, Python plus
  Electron-Oberfläche.

## Was passiert ist

Der Stakeholder fragte beiläufig, warum eine gerade erzeugte Abnahme-Sammlung
im Plan-Ordner liegt. Beim Nachsehen fanden sich dort **neun** Dateien, die
keine Pläne sind — darunter vier ausführbare Prüfskripte (zusammen 79 KB
PowerShell) und ein Gestaltungsvertrag, den der Stakeholder ausdrücklich als
**verbindliche Richtlinie** deklariert hatte.

Alle neun lagen damit in der **Schreibzone der Read-Only-Rollen**: Die
Whitelist deckt Test- und Plan-Ordner ab, und der Bestandsvermerk war **leer**.
Die Rollen durften sie also ändern und löschen, ohne dass der Guard anschlägt —
und die Prompts nannten sie nicht als fremdes Eigentum, weil sie im Vermerk
nicht stehen.

**Der Vermerk war nicht falsch, er war veraltet.** Beim Einzug war der
Plan-Ordner leer, und `leer` war die richtige Antwort. Die neun Dateien sind
danach entstanden, über elf Kaskaden hinweg, eine nach der anderen.

## Wo es steckt

`BL-51` ist erledigt (Release 2.6.0) und hat den Einzug abgedeckt: Der
Installer prüft Plan- und Test-Ordner nach dem Interview auf Inhalt, nennt die
Dateien und vermerkt den Bestand. Der Statuseintrag benennt die verbleibende
Grenze aber selbst, wörtlich:

> `--update` urteilt **nur** über den Config-Vermerk, nie über den Ordner.

Genau dort sitzt der Fall. Zwischen zwei Aufrufen von `--update` kann sich der
Ordner beliebig füllen; niemand vergleicht ihn je wieder mit dem Vermerk. Für
ein Greenfield-Projekt ist der Effekt am größten, weil der Vermerk dort **leer**
beginnt und leer bleibt, während der Ordner sich füllt.

**Dasselbe Muster hat `TEAM_WEITERER_CODE`**, mit der umgekehrten Folge: Die
vier Prüfskripte standen nicht darin und wurden deshalb **nie** gesweept — der
`BL-52`-Fall, nur eben nicht beim Einzug entstanden, sondern hineingewachsen.
Ein Ordner, der beim Einzug nicht existierte, kann in keiner Einzugsprüfung
auffallen.

## Warum das jede Installation trifft

Beides sind **Einmal-Werte, die mit dem Projekt altern**, und beide altern
lautlos:

- Was in der Schreibzone landet, wird stillschweigend Freiwild — je länger das
  Team arbeitet, desto mehr.
- Was an Code außerhalb des Produktivordners entsteht, fällt stillschweigend
  aus dem Prüfumfang. Ein sauberer Sweep liest sich dann wie ein sauberes
  Projekt.

Der zweite Punkt ist der gefährlichere, weil er die **Aussage** des Sweeps
verfälscht statt nur eine Datei zu gefährden.

Aufgefallen ist es hier durch eine beiläufige Frage nach der Ordnerstruktur —
nicht durch ein Werkzeug, nicht durch einen Sweep, nicht durch `--update`.
Wäre die Frage nicht gekommen, stünde der Gestaltungsvertrag weiter im
Freiwild und die 79 KB weiter außerhalb jedes Sweeps.

## Was ich schon versucht habe

Im Projekt gelöst, wie es die Config selbst als harte Variante nennt: Die neun
Dateien sind in einen **eigenen Ordner außerhalb der Schreibzone** gezogen, und
dieser Ordner steht jetzt im Prüfumfang. Damit sind sie geprüft und tabu
zugleich. Das löst diesen Fall, aber nicht den nächsten — der Vermerk altert
weiter, nur eben ab einem leeren Ordner.

Vorschlag, falls er hilft, und ausdrücklich **ohne** Guard-Mechanik (die
Begründung aus `BL-51` trägt weiter: Auf der Whitelist kann der Guard nicht
urteilen): Der Statusbericht — die Stelle, an der ohnehin täglich hingesehen
wird — nennt beiläufig, was in der Schreibzone liegt und **weder** ein
Team-Artefakt (Beutebuch, Backlog, Roadmap, Kaskadenpläne, Abschlussprotokolle,
Ermittlungsakten) **noch** im Bestandsvermerk verzeichnet ist. Ein Hinweis,
kein Abbruch, keine Meinung darüber, ob die Datei dort hingehört — nur die
Feststellung, dass sie niemandem gehört. Dieselbe Zeile könnte melden, wenn im
Repo ausführbare Dateien außerhalb von Produktivordner und Prüfumfang liegen.

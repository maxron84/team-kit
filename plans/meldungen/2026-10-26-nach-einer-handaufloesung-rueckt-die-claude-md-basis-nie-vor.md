# Nach einer Handaufloesung rueckt die CLAUDE.md-Basis nie vor - jedes Update legt dieselben Konflikte erneut vor

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-26-nach-einer-handaufloesung-rueckt-die-claude-md-basis-nie-vor.md
      .\kit-melden.cmd ablegen  2026-10-26-nach-einer-handaufloesung-rueckt-die-claude-md-basis-nie-vor.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-26-nach-einer-handaufloesung-rueckt-die-claude-md-basis-nie-vor.md   # sonst: Pull Request

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
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, CLAUDE.md mit gut tausend Zeilen und vielen
  Projektregeln. Zweites Update seit `BL-311`. Gefunden beim Update vom 2026-10-26 auf `84a7e81`.

## Was passiert ist

Das erste Update mit `BL-311` lief am 2026-10-08. Eine Basis gab es noch nicht. `kit_basis.py`
schätzte sie aus der Kit-Geschichte und legte die Schätzung unter `team/.kit-basis/CLAUDE.md` ab.
Es gab einen Vorschlag mit neun Konfliktstellen. Die Stellen wurden von Hand aufgelöst und die
CLAUDE.md committet, so wie der Installer es sagt: „Ansehen, Konflikte aufloesen, dann
uebernehmen". Die Basis blieb dabei die geschätzte alte Fassung.

Beim Update vom 2026-10-26 brachte die Vorlage genau zwei neue Absätze (`BL-316`, `BL-315`).
Gemeldet wurden aber **elf** Konfliktstellen, und die Datei blieb unangetastet. Gegen die richtige
Basis lief derselbe Abgleich anders: Als Basis diente die Kit-Fassung von `1052429`, mit denselben
Werten gerendert. Ein Absatz ging sauber hinein, an einer Stelle blieb ein echter Konflikt. Die
übrigen zehn Stellen waren die Handentscheidungen vom 2026-10-08, ein zweites Mal vorgelegt.

## Wo es steckt

`geteilt/tools/kit_basis.py`, `claude()`. Bei einem Konflikt (Exit 10) setzt die Funktion die
Basis nicht neu. Das ist richtig, solange der Konflikt offen ist. Aber auch danach setzt nichts
mehr die Basis, wenn der Mensch den Vorschlag aufgelöst und übernommen hat. Laut Docstring rückt
die Basis nur vor, wenn das Projekt die Kit-Fassung aufgenommen hat. Erkennen kann das aber nur ein
konfliktfreier Dreiwege-Abgleich. Eine Stelle, die das Projekt bewusst anders formuliert, ist nie
konfliktfrei. Der Installer nennt nur den Schritt `Copy-Item <vorschlag> CLAUDE.md`.

## Warum das jede Installation trifft

Jede Stelle, an der ein Projekt bewusst anders formuliert als die Kit-Fassung, kommt bei jedem
weiteren Update wieder, und zwar als Konflikt. Echte neue Regeln stehen dann in derselben Liste.
Hier war es eine Stelle von elf. Nach dem zweiten oder dritten Update liest man die Liste als
Rauschen und übersieht genau diese eine (Bauart `BL-14`). Projekte, deren erste Basis geschätzt
wurde, trifft es sofort.

## Was ich schon versucht habe

Im Projekt habe ich die Basis von Hand nachgezogen, nachdem die CLAUDE.md abgeglichen war:
`kit_basis.py schreiben --ziel . --kit <kit> --claude <gerenderte Kit-Fassung aus der
Abgleichsablage>`. Das nächste Update vergleicht damit gegen `84a7e81`.

Vorschlag: Bei einem Konflikt legt `claude()` die gerenderte Kit-Fassung als ausstehende Basis
neben die Basis. Das nächste Update übernimmt sie als Basis, wenn die CLAUDE.md seit dem Vorschlag
geändert wurde und keine Konfliktmarken mehr trägt. Einfacher, aber auf Vertrauen gebaut: Der
Installer nennt den `schreiben --claude`-Aufruf als zweiten Schritt neben dem `Copy-Item`.

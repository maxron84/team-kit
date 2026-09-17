# Das Update ueberschreibt projektlokale Anpassungen ersatzlos und sagt nicht welche

- **Bezug**: BL-16
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst plus
  Electron-Oberfläche, rund 1165 Tests, 24 gebaute Kaskaden.

## Was passiert ist

Ein `--update` hat drei Stellen überschrieben, die dieses Projekt bewusst
gesetzt hatte. **Keine davon wurde gemeldet** — das Update lief durch, der
Commit heißt `chore: T.E.A.M. aktualisiert`, und erst die Verifikation am
nächsten Tag hat die drei gefunden.

**1. Ein Wächter in `team/lib.psm1` war ersatzlos gelöscht.** Das Projekt hatte
ihn über den regulären Weg eingebaut: Ein Red-Team-Fund, ein Fix des Fixers, ein
Reproducer-Test dazu. Er prüft, ob `pytest-xdist` verfügbar ist, bevor die
Selbstprüfung einen `TEAM_SMOKE_TEST` mit `-n`/`--dist` startet — fehlt das
Paket, bricht pytest am Kommandozeilenparser ab, und die Selbstprüfung, die nur
`$LASTEXITCODE` liest, kann das von einem echten Regressions-Rot nicht
unterscheiden. Das Kit hat für denselben Fall an anderer Stelle einen Wächter;
dieser zentrale Aufrufer hatte keinen, deshalb der lokale Einbau.

**2. Ein Rollen-Briefing trug wieder seinen Platzhalter.** In
`team/prompts/rolle-architekt.md` stand nach dem Update erneut
`{{COMMIT_ENTSCHEID}}` statt der ausgefüllten Regel. **Das ist die Rückkehr von
`BL-139`**, das in diesem Projekt als behoben geführt wird.

**3. Aus einem zweiten Briefing war eine Projektregel entfernt.** Betroffen ist
die Ausnahme, mit der dieses Projekt seinen Smoke-Test fährt; dazu eine eigene
Meldung, weil der Grund ein anderer ist (dort geht es um den neuen Rat, nicht um
das Überschreiben).

**Gefunden hat 1. nicht ein Mensch und kein Sweep, sondern das Gate des
Projekts:** Der Reproducer-Test zum ursprünglichen Fund wurde rot — er ist ein
echter Ausführungstest, der eine frische, xdist-lose Umgebung anlegt und die
Funktion in der Bibliothek aufruft. **Ohne diesen Test wäre der Verlust
unbemerkt geblieben**, denn ein fehlender Wächter fällt genau dann auf, wenn es
zu spät ist.

## Wo es steckt

- Im Update-Verb selbst. Es ersetzt Kit-Dateien (`team/lib.*`,
  `team/prompts/rolle-*.md`) durch die Fassung des Kits, ohne zu prüfen oder zu
  melden, ob die ersetzte Fassung vom Kit abwich.
- Bei Punkt 2 zusätzlich in der Platzhalter-Ersetzung: Das Update spielt die
  **Vorlage** ein statt der ausgefüllten Datei, obwohl beim Einrichten einmal
  ausgefüllt wurde. Das ist `BL-139` ein zweites Mal.

## Warum das jede Installation trifft

`team/` und die Rollen-Briefings gehören dem Kit — genau deshalb repariert jedes
Feldprojekt solche Verluste bei jedem Update erneut. **In diesem Projekt ist es
jetzt der dritte Vorfall**: einmal eine Preistabelle, einmal vier
Konfigurationswerte, jetzt drei Stellen auf einmal. Zwei davon waren zuvor
schon einzeln gemeldet worden.

**Was hier hilft, ist keine Ausnahmeliste, sondern eine Meldung.** Das Update
weiß, welche Dateien es ersetzt, und es kann sehen, dass die vorhandene Fassung
von der eigenen abweicht. Ein Hinweis am Ende des Laufs — *„diese N Dateien
wichen ab und wurden ersetzt, Sicherung unter …"* — würde den ganzen Fall
auflösen: Der Mensch sieht sofort, was er nachziehen muss, statt es am nächsten
roten Gate zu erfahren oder gar nicht.

**Die Gegenprobe, welche Anpassung überlebt, ist in diesem Projekt eindeutig
und stützt denselben Vorschlag:** Die Projektkonfiguration wurde **nicht**
angefasst, sämtliche Werte dort stehen unverändert. Was in der Konfiguration
steht, überlebt; was als Patch im Kit-Code steht, wird gefressen. Das ist die
richtige Arbeitsteilung — sie versagt nur, wenn die Anpassung sich **nicht**
konfigurieren lässt, und dann braucht es die Meldung.

## Was ich schon versucht habe

Alle drei lokal wiederhergestellt und committet, mit Nachweis: Der Reproducer zu
Punkt 1 ist danach wieder grün, die Team-Regressionstests bleiben grün (504
bestanden). **Der Fix hat die bekannte Verfallszeit** — er steht in denselben
Kit-Dateien und wird beim nächsten `--update` erneut überschrieben. Genau
deshalb diese Meldung statt nur eines lokalen Commits.

# Update-Selbsttest im Bestandsprojekt rot - 15 Preis-Tests lesen TEAM_PREISE des Projekts, test_bl314 liest bash/install.sh

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-08-update-selbsttest-im-bestandsprojekt-rot-15-preis-tests-lese.md
      .\kit-melden.cmd ablegen  2026-10-08-update-selbsttest-im-bestandsprojekt-rot-15-preis-tests-lese.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-08-update-selbsttest-im-bestandsprojekt-rot-15-preis-tests-lese.md   # sonst: Pull Request

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
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn (einbahnige Ablage), rund 37 Kaskaden,
  projektlokale Preise nach `Kit-BL-211`. Update am 2026-10-08 auf den Stand `1052429`.

## Was passiert ist

Der Selbsttest am Ende des Updates endete mit 16 failed, 741 passed und 1111 skipped (8:44 min).
Der Installer hat richtig gemeldet, dass das den Stand der Suite bewertet und nicht das Update.
Alle 16 roten Fälle sind Testaufbau, das Projekt ist nicht betroffen:

**(a) 15 Preis-Fälle.** Betroffen sind `test_bl141`, `test_bl152` (5), `test_bl166` (5),
`test_bl211::test_ohne_uebersteuerung_gilt_die_kit_tabelle`, `test_bl218` (2) und `test_bl302`:

```
>       assert kosten.modell_basispreis("claude-sonnet-5") == 2.00
E       AssertionError: assert 3.0 == 2.0
```

Seit `Kit-BL-238` liest `kosten.py` `TEAM_PREISE` aus `team.config.*` der Projektwurzel, wenn die
Umgebung ihn nicht kennt. Das Projekt setzt dort bewusst `claude-sonnet-5=3.00`, wie
`Kit-BL-211` es vorsieht. Die Tests isolieren nur die Umgebung, nicht die Konfigurationsdatei.
`test_ohne_uebersteuerung_gilt_die_kit_tabelle` zeigt den Kern: Ohne Übersteuerung in der
Umgebung gilt eben doch die des Projekts. Das ist dieselbe Gattung wie bei `Kit-BL-307`, wo
Tests CLAUDE.md und Konfiguration des Projekts lasen.

**(b) `test_bl314_blanke_nummer_wird_belegt_nicht_behauptet.py::test_der_waechter_behauptet_die_zuordnung_nicht_mehr`:**

```
>       quelle = (REPO_ROOT / "bash" / "install.sh").read_text(encoding="utf-8-sig")
E       FileNotFoundError: [Errno 2] No such file or directory: '…\\bash\\install.sh'
```

In einer installierten Ablage gibt es keine Installer. Der Fall braucht den Skip „installierte
Ablage", den etwa `test_bl267` hat. Laut Commit wurde `Kit-BL-314` nur auf der bash-Bahn und nur
im Kit-Checkout gefahren.

## Wo es steckt

(a) In den sechs genannten Testdateien unter `geteilt/tests/`, zusammen mit dem
Konfig-Rückfall in `kosten.py` (`Kit-BL-238`). (b) In
`geteilt/tests/test_bl314_blanke_nummer_wird_belegt_nicht_behauptet.py`.

## Warum das jede Installation trifft

(a) trifft jedes Projekt mit projektlokalen Preisen, und `Kit-BL-211` empfiehlt sie
ausdrücklich. (b) trifft jede installierte Ablage. Ein roter Update-Selbsttest, „ohne dass etwas
kaputt war", ist genau das, was `Kit-BL-307` abstellen sollte. Er stumpft ab und verdeckt den Tag,
an dem wirklich etwas kaputt ist.

## Was ich schon versucht habe

Am Kit nichts. Die Vorschläge:

- (a): Die betroffenen Tests setzen das Arbeitsverzeichnis auf `tmp_path` oder schalten den
  Konfig-Rückfall ausdrücklich ab.
- (b): einen Skip in der installierten Ablage.
- Die Bestandsprojekt-Konfiguration des Selbsttests (`Kit-BL-307`) bekommt projektlokale
  `TEAM_PREISE`. Dann wäre (a) vor dem Feld aufgefallen.

Nachgemessen: Der Smoke-Test des Projekts sammelt `team/tests` nicht ein (`testpaths`), das
Gate der Kaskaden ist also nicht betroffen.

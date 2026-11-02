# Franks Quittung prüft den CHANGELOG-Eintrag nicht — drei von fünf Fixen landeten unter einer veröffentlichten Version

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-02-franks-quittung-prueft-den-changelog-eintrag-nicht-drei-von.md
      .\kit-melden.cmd ablegen  2026-11-02-franks-quittung-prueft-den-changelog-eintrag-nicht-drei-von.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-02-franks-quittung-prueft-den-changelog-eintrag-nicht-drei-von.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: HM-32, HM-35, HM-36
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, nur pwsh-Bahn; ein XML-Workflow und ein Python-Prüfwerkzeug mit pytest-Suite (rund 430 Tests). Dritte Kaskade, die erste nach einer veröffentlichten Version.

## Was passiert ist

In der Fix-Phase einer Vollautomatik hat Frank fünf Funde je im ersten Versuch
behoben, und die Vollautomatik meldete fünfmal „erledigt (Dreisatz
verifiziert)". Beim Closeout stand der CHANGELOG-Eintrag von **drei** der fünf
Fixe nicht im `[Unreleased]`-Block, sondern unter der schon veröffentlichten
Version: `## [0.1.0]` → `### Fixes`. Die beiden anderen standen richtig, oben im
`[Unreleased]`-Block.

Die Ausgangslage: Beim Schnitt von 0.1.0 wurde der `[Unreleased]`-Block
geleert, er hatte danach keine Unterüberschrift. Die erste Überschrift
`### Fixes` der Datei stand damit unter `## [0.1.0]`. Franks Prompt sagt
„unter '## [Unreleased]' → '### Fixes' den Fix eintragen". Drei der fünf Läufe
haben offenbar die Überschrift gesucht und die der alten Version gefunden.

Die Folge: Ralph liest vor jeder Stufe nur den `[Unreleased]`-Block und hätte
die drei Fixe dort nicht gesehen. Die nächsten Release-Notes hätten sie nicht
enthalten, die schon veröffentlichten dagegen drei Fixe, die nie in dieser
Version waren.

## Wo es steckt

- **`frank.ps1`, Erfolgsprüfung nach dem Lauf** (Zeilen 211–215): verlangt
  Promise, einen `fix(uat)`-Commit, den Status `erledigt`,
  `team_diff_beruehrt_fund` und `team_reproducer_liegt_vor`. Ob es einen
  CHANGELOG-Eintrag gibt und wo er steht, prüft sie nicht. „Dreisatz
  verifiziert" behauptet damit einen Schritt, den niemand geprüft hat.
- **Franks Prompt, Schritt 3** (`frank.ps1` Zeile 141, gleichlautend
  `team/prompts/rolle-frank.md` Zeile 22): `### Fixes` als Ziel ist mehrdeutig,
  sobald der `[Unreleased]`-Block keine solche Überschrift hat, eine ältere
  Version aber schon.
- Die bash-Bahn (`frank.sh`) habe ich nicht nachgesehen; vermutlich dieselbe
  Prüfung.

## Warum das jede Installation trifft

Jedes Projekt, das eine Version schneidet und den `[Unreleased]`-Block dabei
leert — Keep a Changelog legt genau das nahe —, hat danach eine Überschrift
`### Fixes` nur noch unter einer Version. Ab dann hängt es am Modell, wohin der
nächste Fix-Eintrag geht, und kein Werkzeug merkt es. Auffallen kann es erst
beim nächsten Release oder wenn Ralph einen schon behobenen Fehler neu baut.

## Was ich schon versucht habe

Im Projekt: die drei Einträge von Hand in den `[Unreleased]`-Block verschoben
und dort die Überschrift `### Fixes` angelegt, damit der nächste Fix-Lauf sie
findet. Am Kit nichts. Zwei kleine Vorschläge, einer genügt:

- **Prüfung:** Die Erfolgsprüfung verlangt, dass die Fundnummer im
  `[Unreleased]`-Block vorkommt (zwischen `## [Unreleased]` und der nächsten
  Zeile, die mit `## [` beginnt), und meldet sonst „CHANGELOG-Eintrag fehlt im
  [Unreleased]-Block" — als Fehlversuch oder wenigstens als Warnung.
- **Prompt:** „im `[Unreleased]`-Block eintragen; fehlt dort `### Fixes`, lege
  die Überschrift dort an — nie unter einer Versionsnummer". Dazu im Briefing
  des Architekten beim Versionsschnitt: die leere Überschrift `### Fixes` im
  `[Unreleased]`-Block stehen lassen.

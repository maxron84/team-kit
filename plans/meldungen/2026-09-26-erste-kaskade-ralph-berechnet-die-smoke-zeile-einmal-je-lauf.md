# Erste Kaskade: Ralph berechnet die Smoke-Zeile einmal je Lauf - die Stufen nach Stufe 1 bauen ohne Smoke-Test

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-26-erste-kaskade-ralph-berechnet-die-smoke-zeile-einmal-je-lauf.md
      .\kit-melden.cmd ablegen  2026-09-26-erste-kaskade-ralph-berechnet-die-smoke-zeile-einmal-je-lauf.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-26-erste-kaskade-ralph-berechnet-die-smoke-zeile-einmal-je-lauf.md   # sonst: Pull Request

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
- **Bahn**: pwsh (beide Bahnen installiert, beide geprüft)
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, beide Bahnen; Spielskript-Stack
  ohne eigene Testinfrastruktur — der Smoke-Test entsteht erst in Stufe 1 der
  ersten Kaskade, in Python/pytest.

## Was passiert ist

Aufgefallen beim Aushärten der **ersten** Kaskade, bevor ein Lauf startete —
beim Nachlesen, wie der in Stufe 1 gebaute Smoke-Test in die Prompts der
Folgestufen kommt. Antwort: im selben Lauf gar nicht.

1. `ralph.sh` sourct `team/lib.sh` **einmal** und läuft danach in `while true`
   über alle Stufen bis `RALPH_CAP`. `SMOKE_ZEILE` und `SMOKE_SUFFIX` entstehen
   beim Laden der Bibliothek (Block `if [ -n "${TEAM_SMOKE_TEST:-}" ]`), und
   `TEAM_SMOKE_TEST` selbst wird danach nie neu gelesen. Die pwsh-Bahn ist
   gleich gebaut: `ralph.ps1` importiert `lib.psm1` einmal, `$SMOKE_ZEILE`
   entsteht beim Import, danach `while ($true)`.
2. Trägt Stufe 1 den Befehl regelkonform in `team.config.*` ein, bekommen die
   Stufen 2…N **desselben Laufs** weiter die Zeile *„(Kein Smoke-Test
   konfiguriert — Schritt entfällt. Das Team arbeitet ohne Sicherheitsnetz …)"*.
   Die Vollautomatik ruft Ralph einmal für die ganze Bauphase — betroffen ist
   also jede Folgestufe der ersten Kaskade.
3. Dasselbe trifft die BL-41-Selbstprüfung (`team_quittung_selbstpruefung`): Sie
   liest `TEAM_SMOKE_TEST` aus derselben Ladezeit und scheitert in den
   Folgestufen an *„Kein TEAM_SMOKE_TEST konfiguriert"*. Eine fertige Stufe ohne
   Quittung kann der Loop dort also nicht selbst quittieren, sondern hält an.
4. `team/prompts/rolle-ralph.md` trägt `{{SMOKE_TEST_GRENZE}}` (BL-170) als beim
   Installieren gerenderten, statischen Satz *„noch KEIN Smoke-Test konfiguriert
   … bis dahin entfaellt der Schritt, und ich erfinde keinen Befehl"*.
   `team_briefing` liest die Datei zwar je Stufe neu, aber neu **gerendert** wird
   sie erst von `--update`. Bis dahin — auch in der zweiten Kaskade —
   widerspricht Ralphs Briefing der Konfiguration.

Nicht gelaufen, also kein Kostenbeleg: Die Lücke wurde vor dem ersten Lauf
umgangen (siehe unten).

## Wo es steckt

- `bash/lib.sh`: `SMOKE_ZEILE`/`SMOKE_SUFFIX` werden beim Laden gebaut;
  `team_quittung_selbstpruefung` liest `TEAM_SMOKE_TEST` aus derselben Ladezeit.
- `bash/entry/ralph.sh`: einmaliges `source`, danach die Stufenschleife.
- die pwsh-Gegenstücke (`lib.psm1`, `ralph.ps1`): dieselbe Bauform.
- `geteilt/prompts/rolle-ralph.md` über `{{SMOKE_TEST_GRENZE}}`: statisch
  gerendert, erst `--update` rendert neu.
- Architekten-Briefing, „Die erste Kaskade eines Projekts — Sonderregeln",
  Punkt 1: Er schreibt genau den Ablauf vor, der die Lücke öffnet.

## Warum das jede Installation trifft

Jedes frische Projekt beginnt ohne Smoke-Test, und das Architekten-Briefing
verlangt, dass Stufe 1 der ersten Kaskade ihn baut. „Eintrag in Stufe 1" plus
„ein Ralph-Aufruf für alle Stufen" erzeugt die Lücke deterministisch in der
**ersten** Kaskade jedes Projekts — genau dort, wo das Team laut eigener Zeile
ohnehin schon ohne Sicherheitsnetz läuft. Wie `BL-149` und `BL-170` trifft sie
nur diese eine Kaskade und ist danach unsichtbar: Wer sie verpasst, sieht
später nichts mehr davon.

## Was ich schon versucht habe

**Umgangen, nicht behoben.** Der Architekt hat den Befehl schon bei der
Aushärtung eingetragen, in **beiden** `team.config.*`, also vor seinem Bau.
Stufe 1 startet damit rot (pytest ohne Tests endet mit Exit 5), und genau das
ist ihr Auftrag. Die Briefing-Zeile in `team/prompts/rolle-ralph.md` hat er so
gesetzt, wie der Installer sie für einen konfigurierten Befehl rendert:
*„Der Smoke-Test (`<befehl>`) muss gruen sein, bevor die Stufe fertig ist."*
Ein späteres `--update` rendert dieselbe Zeile; die Umgehung verfällt also
nicht schädlich. Vorher geprüft: Die Vollautomatik fährt den Smoke-Test nicht
vorab, sie liest das Gate erst am Ende — ein roter Startzustand blockiert den
Lauf also nicht.

**Vorschläge** (der Maintainer entscheidet):

- Die Smoke-Werte je Stufe neu ableiten: in der Stufenschleife `team.config.*`
  neu lesen und `SMOKE_ZEILE`/`SMOKE_SUFFIX` neu bauen. `team_briefing` könnte
  die Grenze bei der Gelegenheit zur Laufzeit rendern statt der Installer.
- Oder die Sonderregel umdrehen, wie hier umgangen: Der Architekt trägt den
  Befehl bei der Aushärtung ein, Stufe 1 baut ihn. Dann muss das Briefing auch
  das Neu-Rendern von `rolle-ralph.md` nennen.
- Nachweis-Idee: ein Test, der einen Plan mit zwei Stufen fährt, in Stufe 1
  `TEAM_SMOKE_TEST` in die Konfiguration schreibt und prüft, dass der Prompt von
  Stufe 2 den Befehl nennt. Gegenprobe: Neuableitung ausbauen → Test rot.

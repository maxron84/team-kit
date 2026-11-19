# Ein Fund, der den Menschen braucht, hat im Loop keinen Ausgang

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-19-ein-fund-der-den-menschen-braucht-hat-im-loop-keinen-ausgang.md
      .\kit-melden.cmd ablegen  2026-11-19-ein-fund-der-den-menschen-braucht-hat-im-loop-keinen-ausgang.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-19-ein-fund-der-den-menschen-braucht-hat-im-loop-keinen-ausgang.md   # sonst: Pull Request

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
- **Feldkürzel**: keins eingetragen — bitte vergeben (dasselbe Projekt wie die Meldungen vom 2026-11-06)
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn; Workflow-XML einer MFT-Software mit Prüfkette in Python; kein Zugriff der Rollen auf das Zielsystem, Laufzeitbelege kommen nur als Joblog eines Handlaufs

## Was passiert ist

Eine Vollautomatik mit sieben Baustufen, zwei Sweeps und acht Funden. Zwei der
Funde brauchten etwas, das nur der Mensch liefern kann — einen Entscheid oder
einen Lauf am Zielsystem. Für beide hat die Fix-Phase keinen Ausgang:

1. **Fund A (Entscheid fehlt).** Der Finder schrieb in die Reproducer-Zeile
   selbst `(nicht angelegt; Entscheid des Stakeholders nötig)`, setzte den
   Status aber regelkonform auf `an Frank übergeben`. Frank suchte den Entscheid,
   fand ihn zu Recht nicht und setzte den Status auf `an Mensch eskaliert` —
   ohne Commit, ohne Reproducer, ohne Promise. `frank.ps1` meldete dreimal
   „die im Fundblock reservierte Reproducer-Datei existiert nach dem Fix NICHT"
   und rollte zurück (0,24 + 0,07 + 0,04 USD), danach ging der Fund an Axel.
   Axel brauchte 9,61 USD (93 Turns) und fand einen **Ersatzanker**, der ohne
   den Menschen auskam; seine Akte begründet ausdrücklich, warum sie ohne
   Rückfrage auskommen *musste*: `axel.ps1` erkennt nur `Fix-Plan liegt vor` an,
   und `frank.ps1` nimmt genau diesen Status vorrangig — eine Akte, die auf eine
   Antwort wartet, ließe Frank sofort wieder scheitern und hielte die übrigen
   sechs Funde dahinter fest. Ohne den Ersatzanker wäre der Fund nach Axel beim
   Menschen gelandet, nachdem die Loop-Rollen rund 10 USD verbraucht hatten.
2. **Fund B (Lauf am Zielsystem fehlt).** Frank fixte, was ohne Lauf ging
   (Doku-Abschnitt, Test, Commit), setzte den Status auf `an Mensch eskaliert`
   und gab bewusst kein Promise: „HM-… ist nicht erledigt, ich gebe das Promise
   deshalb nicht aus … Zum Weitermachen braucht es das Joblog dieser Probe."
   Die Vollautomatik las das als vierten Ausgang:

   ```
   [frank] STUFE FERTIG, QUITTUNG FEHLT (Kit-BL-41) — HM-56 hat kein <promise>FRANK_FIX_COMPLETE</promise> gegeben.
   ⚠ Fix fertig, Quittung fehlt (Kit-BL-41/Kit-BL-214) — Lauf gestoppt. NICHT neu starten, bevor die von Frank genannten Prüfungen gelaufen sind.
   ```

   Die Diagnose trifft nicht zu: Frank hat nicht auf einen Hintergrund-Task
   gewartet, sondern absichtlich eskaliert. Der Lauf stand still, ein weiterer
   Fund lag noch in der Warteschlange. Der Architekt prüfte von Hand (3,30 USD
   Abo-Gegenwert), stellte fest, dass der Kern belegt war, setzte den Fund auf
   erledigt, und der Mensch startete die Fix-Phase neu.

## Wo es steckt

- **Übergabe:** Das Ausschlusskriterium in `CLAUDE.md` („Harry & Marv",
  „Ausschlusskriterium für die Übergabe") kennt nur Funde, deren Reproduktion
  eine Messreihe ist. Ein Fund, dessen *Fix* einen Entscheid oder eine Angabe
  des Menschen braucht, geht trotzdem an Frank. `beutebuch.py lint` sieht die
  Reproducer-Zeile mit „Entscheid … nötig" oder „braucht erst die Probe" neben
  `an Frank übergeben` und schweigt.
- **Frank:** Das Briefing (`team/prompts/rolle-frank.md`) und `frank.ps1`
  haben keine Quittungsform für „braucht den Menschen". Die Status-Kette in
  `CLAUDE.md` nennt `an Mensch eskaliert` nur nach Axel; Frank benutzt ihn
  trotzdem (beide Male), und dann gibt es Promise oder kein Promise — kein
  Promise ist mit Exit 43 belegt.
- **Axel:** `axel.ps1` setzt nach der Akte immer `Fix-Plan liegt vor`; einen
  Ausgang „Akte liegt vor, wartet auf den Menschen", den `frank.ps1` übergeht,
  gibt es nicht.

## Warum das jede Installation trifft

Jedes Projekt, dessen Laufzeit die Rollen nicht selbst erreichen (Server,
Gerät, fremdes System), erzeugt solche Funde: Das Red Team fragt zu Recht nach
Belegen, die nur ein Handlauf liefert. Die Mechanik steckt in `frank.ps1`,
`axel.ps1`, `beutebuch.py` und der Regel in `CLAUDE.md`, nicht im Projekt.

## Was ich schon versucht habe

Nichts am Kit geändert. Im Projekt: Fund A hat Axel gelöst (Ersatzanker),
Fund B hat der Architekt nach dem Stopp von Hand abgeschlossen. Vorschläge,
nach Aufwand:

1. **Lint-Warnung:** `beutebuch.py lint` warnt, wenn die Reproducer- oder
   Stand-Zeile „Entscheid", „Probe" oder „Stakeholder … nötig" nennt und der
   Status `an Frank übergeben` lautet — der Finder entscheidet dann bewusst.
2. **Zweite Quittungsform für Frank**, wie `STUFE_N_UEBERSPRUNGEN` für Ralph
   (`Kit-BL-255`): `<promise>FRANK_BRAUCHT_MENSCH</promise>` gilt nur mit Status
   `an Mensch eskaliert` und einer Zeile, *was* fehlt; die Fix-Phase nimmt den
   nächsten Fund, statt mit Exit 43 zu stoppen, und der Abschlussbericht zählt
   solche Funde getrennt.
3. **Axel-Ausgang** „wartet auf den Menschen", den `frank.ps1` überspringt.

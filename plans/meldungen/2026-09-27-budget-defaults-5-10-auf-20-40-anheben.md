# Budget-Defaults 5/10 auf 20/40 anheben

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-27-budget-defaults-5-10-auf-20-40-anheben.md
      .\kit-melden.cmd ablegen  2026-09-27-budget-defaults-5-10-auf-20-40-anheben.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-27-budget-defaults-5-10-auf-20-40-anheben.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Änderungswunsch am Kit — Default-Werte (Entscheid des Owners), kein Fehler
- **Kit-Version**: 2.13.1
- **Bahn**: beide (`team.config.sh` und `team.config.ps1`)
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, Spielskript-Stack mit Prüfwerkzeug in
  Python; zwei Kaskaden gelaufen, alle Rollen im Abo.

## Was passiert ist

Der Owner hat entschieden, die Kit-Defaults `TEAM_ROLE_BUDGET_USD` (Soft-Cap)
und `TEAM_ROLE_HARDCAP_USD` (Hard-Cap) von **5/10** auf **20/40** USD
anzuheben. In diesem Feldprojekt sind die Werte schon lokal gesetzt, in beiden
`team.config.*` zeichengleich. `./team-test` ist danach auf der pwsh-Bahn grün:
1032 passed, 414 skipped.

Die Zahlen aus diesem Projekt, damit der Maintainer sie beim Triage neben die
anderer Felder legen kann:

| Rolle | Aufrufe | USD je Aufruf |
|---|---|---|
| Ralph (Stufen) | 8 | 1,04 – 2,75 |
| Harry | 2 | 1,47 – 2,13 |
| Marv | 2 | 1,17 – 1,69 |
| Frank | 8 Fixe, alle im ersten Versuch | 0,67 – 1,24 |

Kein Aufruf hat den Soft-Cap von 5 USD erreicht. **Die Begründung für die neuen
Werte liefert dieses Projekt also nicht**, sie ist ein Entscheid des Owners. Aus
diesem Feld spricht aber auch nichts dagegen.

## Wo es steckt

- `team.config.sh` / `team.config.ps1` (Vorlagen des Installers), Abschnitt
  „Budget": `TEAM_ROLE_BUDGET_USD`, `TEAM_ROLE_HARDCAP_USD`.
- `team/lib.sh` / `team/lib.psm1`: die Fallback-Defaults samt Kommentar
  („Default 5", „Default 10").
- `CLAUDE.md`-Vorlage: Abschnitt Axel (gerenderter Wert plus „Default 5 USD" /
  „Default 10 USD") und Abschnitt „Kostenkontrolle".
- Tests, die Default-Werte prüfen, falls es welche gibt.

## Warum das jede Installation trifft

Die Defaults gelten für jede neue Installation und für jede, die die Werte nicht
selbst gesetzt hat.

Eine Folge sollte der Maintainer bewusst mittragen: **Für Ralph, Harry und Marv
ist der Soft-Cap der einzige Deckel** (sofortiger Hard-Cap beim Soft-Wert). Mit
20 USD liegt er über dem Default des Lauf-Deckels (`TEAM_BUDGET_USD`, 15). Ein
einzelner entgleister Aufruf dieser drei Rollen wird dann in der Regel erst vom
Lauf-Deckel gestoppt, nicht mehr vom Rollen-Cap. Für Frank und Axel ändert sich
weniger: Ihr Soft-Cap ist ohnehin nur ein Hinweis, und der Hard-Cap von 40 USD
bleibt ein Airbag gegen Endlosschleifen. Er passt zur Feld-Lehre `Kit-HM-32`,
nach der zu tiefe Caps bezahlte Arbeit per Rollback wegwerfen.

## Was ich schon versucht habe

Lokal gesetzt, siehe oben. Das hält nur bis zum nächsten `--update`, falls das
Update die Werte in `team.config.*` überschreibt. Sonst bleibt es bis dahin ein
lokaler Sonderweg.

**Vorschlag:** Defaults in Konfigurationsvorlagen, Bibliotheken und
`CLAUDE.md`-Vorlage auf 20/40 setzen. Die Folge für den Lauf-Deckel entweder
hinnehmen und in `CLAUDE.md` („Kostenkontrolle") so benennen, oder den Default
von `TEAM_BUDGET_USD` mit anheben.
**Nachweis:** Ein frisch installiertes Projekt zeigt in `team.config.*` und in
der gerenderten `CLAUDE.md` 20/40. `team-test` ist auf beiden Bahnen grün.
**Gegenprobe:** Ein Test, der die Defaults beider Bahnen gegeneinander hält, wird
rot, wenn nur eine Bahn umgestellt ist.

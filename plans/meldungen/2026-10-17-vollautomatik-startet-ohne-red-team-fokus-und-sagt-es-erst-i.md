# Vollautomatik startet ohne Red-Team-Fokus und sagt es erst im Abschlussbericht

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-17-vollautomatik-startet-ohne-red-team-fokus-und-sagt-es-erst-i.md
      ./kit-melden.sh ablegen  2026-10-17-vollautomatik-startet-ohne-red-team-fokus-und-sagt-es-erst-i.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-17-vollautomatik-startet-ohne-red-team-fokus-und-sagt-es-erst-i.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-17
- **Art**: Lücke im Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; vierte Kaskade, ein Mensch und die Rollen in einem Arbeitsbaum

## Was passiert ist

Die Scharfschalt-Sequenz des Architekten startete die Vollautomatik am Ende
einer Kette von Bedingungen:

```bash
test -z "$(git status --porcelain)" \
  && test "$(cat .ralph-state)" = <erste Stufe> \
  && grep -qE '<Architekten-Zeile der Kaskade>' .budget-ledger \
  && TEAM_REDTEAM_FOCUS='…' ./vollautomatik.sh
```

Die Buchung der Aushärtung fehlte im Ledger. An dieser Bedingung hält die
Kette an, ohne etwas auszugeben. Gelaufen ist die Vollautomatik trotzdem,
22 Sekunden nach dem Ledger-Commit, ohne `TEAM_REDTEAM_FOCUS` in der Umgebung.
Wie sie gestartet wurde, steht nirgends; belegt ist nur, dass die Variable beim
ersten Sweep leer war.

- Sechs Stufen bauten in 22 Minuten, je im ersten Anlauf.
- Erst beim Start der Sweeps meldete jede Rolle:

  ```
  [harry] Der zuletzt gesetzte Fokus gehört zu einem anderen Stand (<hash>) — VERFALLEN (Kit-BL-31).
    Dieser Sweep läuft mit dem Grundauftrag. Für eine gezielte Prüfung TEAM_REDTEAM_FOCUS neu setzen.
  ```

- Beide Sweeps liefen mit dem Grundauftrag. Die zwölf Nähte, die der Plan für
  den Fokus benannt hatte, griff keiner gezielt an.
- Der Abschlussbericht sagt es korrekt („Red Team: harry — Fokus VERFALLEN —
  Grundauftrag“), aber erst nach dem Lauf.

Der Grundauftrag fand trotzdem einen Fund. Die Nähte hat der Architekt im
Closeout nachgeprüft, soweit sie sich am echten Material prüfen lassen. Das
kostet Zeit des starken Modells statt zweier Sweeps auf dem günstigen.

## Wo es steckt

- **`vollautomatik.sh`** prüft beim Start Deckel und Phasen, aber nicht, ob
  `TEAM_REDTEAM_FOCUS` gesetzt ist.
- **`team/redteam.sh`** behandelt den fehlenden Fokus erst beim Start des Sweeps
  (Kit-BL-31, Kit-BL-250). Da ist der Bau fertig, und der Mensch sieht nicht
  mehr zu.
- **`CLAUDE.md`**, Kaskaden-Planungsregel 4: „Der Fokus wird bei JEDER Kaskade
  gesetzt … ein fehlender lässt ihn ohne Schwerpunkt laufen.“ Die Regel steht
  da. Durchgesetzt wird sie nirgends, auch nicht im einzigen Moment, in dem ein
  Mensch dabei ist: beim Start.

## Warum das jede Installation trifft

Jede Installation startet die Vollautomatik von Hand, mit einer langen
Umgebungsvariable für den Fokus. Fehlt sie, merkt das niemand vor dem Ende des
Laufs: Je nach Kaskade sind das Minuten oder Stunden. Eine stille Kette aus
Bedingungen davor macht es wahrscheinlicher, nicht seltener: Hält sie an, liegt
der Neustart ohne die Variable nahe.

## Was ich schon versucht habe

Projektseitig meldet die Startsequenz des Architekten künftig jede Bedingung,
an der sie anhält, statt still abzubrechen.

Vorschlag fürs Kit:

1. **Fokusprüfung beim Start.** Stehen Red-Team-Phasen an und ist
   `TEAM_REDTEAM_FOCUS` leer, bricht die Vollautomatik vor dem Bau ab. Die
   Meldung zeigt, wie man den Fokus setzt. Ausdrücklich ohne Fokus fährt sie mit
   einem Schalter, etwa `TEAM_REDTEAM_OHNE_FOKUS=1`. Ist der Fokus wortgleich zu
   dem der vorigen Kaskade (Kit-BL-284), dieselbe Prüfung.
2. **In denselben Startschritt gehört die Prüfung aus der Meldung
   „Vollautomatik startet trotz ungebuchter Planungssitzung der Kaskade“**
   (2026-10-12). Auch hier fehlte die Buchung der Aushärtung. `sitzungen-pruefen`
   sah sie nicht, weil die jüngste Sitzung 15 Minuten lang als laufend gilt
   (Meldung vom 2026-10-13). Ein Commit mit der Nachricht „… gebucht“ kam
   deshalb ohne Buchung durch.

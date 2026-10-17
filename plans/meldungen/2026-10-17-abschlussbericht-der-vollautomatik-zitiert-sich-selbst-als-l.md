# Abschlussbericht der Vollautomatik zitiert sich selbst als letzte drei Laufzeilen

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-17-abschlussbericht-der-vollautomatik-zitiert-sich-selbst-als-l.md
      ./kit-melden.sh ablegen  2026-10-17-abschlussbericht-der-vollautomatik-zitiert-sich-selbst-als-l.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-17-abschlussbericht-der-vollautomatik-zitiert-sich-selbst-als-l.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-23
- **Art**: Fehler am Kit (Anzeige, kein falsches Ergebnis)
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; sechste Kaskade, Vollautomatik

## Was passiert ist

Der Abschlussbericht am Ende jeder Vollautomatik enthält den Abschnitt „Vollautomatik (letzte 3
Zeilen: …)“. Dort sollen die letzten Zeilen des Laufs stehen. Es stehen dort aber die Zeilen, die der
Bericht selbst gerade geschrieben hat, und zuletzt seine eigene Überschrift. Wörtlich aus dem Lauf-Log
(Hashes gekürzt):

```
  ──────── Letzte Commits ────────
    50a447f feat(stufe39): …
    …
  ──────── Vollautomatik (letzte 3 Zeilen: vollautomatik-20261017-171420.log) ────────
        feb5f79 feat(stufe38): …
        af0f3d8 feat(stufe37): …
      ──────── Vollautomatik (letzte 3 Zeilen: vollautomatik-20261017-171420.log) ────────
════════════════════════════════════════════════════════
```

Dasselbe Bild in den drei letzten Läufen desselben Projekts (Kaskaden 4, 5 und 6). Im selben Bericht
steht außerdem `Pipeline: 🟢 läuft gerade (Lock gehalten)` — gemeint ist der Lauf, der den Bericht
schreibt. Ruft man `./team-status.sh` nach dem Lauf im Terminal auf, ist beides richtig: Die drei
Zeilen enden dort mit `Vollautomatik beendet.`, und die Pipeline ist idle.

## Wo es steckt

- `vollautomatik.sh` leitet die ganze Ausgabe ins Lauf-Log: `exec > >(tee -a "$LAUF_LOG") 2>&1`
  (Kommentar dazu: „team-status liest die letzten Zeilen“). Am Ende: `log "=== ABSCHLUSSBERICHT ==="`,
  dann `./team-status.sh || true`.
- `team-status.sh`, Statusanzeige: Das neueste `vollautomatik-*.log` ist während des Berichts genau
  dieses Lauf-Log; `tail -n 3 "$letzte_lauf"` liest also, was `tee` von der laufenden Anzeige schon
  hineingeschrieben hat.

## Warum das jede Installation trifft

Beides steckt in Entrypoints des Kits, nicht im Projekt. Jeder Abschlussbericht jeder Installation
zeigt an dieser Stelle sich selbst. Schaden richtet das nicht an — die Zahlen des Laufs folgen direkt
danach —, aber der Abschnitt zeigt im wichtigsten Bericht nichts über den Lauf, und „läuft gerade“
liest sich am Ende eines Laufs wie ein hängender Prozess.

## Was ich schon versucht habe

Nichts lokal geändert: Beide Dateien gehören dem Kit. Zwei mögliche Wege, beide klein:

- `vollautomatik.sh` setzt für den Aufruf eine Variable (etwa `TEAM_STATUS_IM_LAUF=1`), und
  `team-status.sh` lässt dann den Abschnitt „letzte 3 Zeilen“ weg und schreibt statt „läuft gerade“
  „dieser Lauf“.
- Oder `vollautomatik.sh` liest die letzten Zeilen **vor** `=== ABSCHLUSSBERICHT ===` und reicht sie
  durch.

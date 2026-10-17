# Eine Hintergrundmeldung nach dem Stufenende ersetzt das Ergebnis im Rollenlog

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-17-eine-hintergrundmeldung-nach-dem-stufenende-ersetzt-das-erge.md
      ./kit-melden.sh ablegen  2026-10-17-eine-hintergrundmeldung-nach-dem-stufenende-ersetzt-das-erge.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-17-eine-hintergrundmeldung-nach-dem-stufenende-ersetzt-das-erge.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-20
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; fünfte Kaskade mit zehn Stufen, Vollautomatik

## Was passiert ist

In einer Stufe der Vollautomatik rief Ralph ein Python-Skript per Heredoc auf (`python3 - <<'EOF' …`),
das nicht zurückkam. Das Bash-Werkzeug der Agenten-CLI schob es nach seiner Frist selbst in den
Hintergrund:

```
Command did not complete within its 120s timeout and was moved to the background (ID: …).
… If it is still running after 10m in the background, it will be stopped and you will be notified.
```

Ralph baute die Stufe fertig, committete und schloss mit `<promise>STUFE_34_COMPLETE</promise>`.
Die Sitzung endete damit aber nicht. Sie wartete auf den Hintergrund-Task, bis die CLI ihn nach zehn
Minuten stoppte, und beantwortete dessen Meldung als zweite Antwort. Zeiten aus dem Transkript (UTC):

| Zeit | Ereignis |
|---|---|
| 11:39:22 | Stufe beginnt |
| 11:42:52 | Befehl wird in den Hintergrund geschoben |
| 11:46:09 | Antwort mit Promise, Stufe fertig und committet |
| 11:52:52 | Meldung des Hintergrund-Tasks (Zehn-Minuten-Grenze) |
| 11:52:55 | zweite Antwort: „Die Hintergrundmeldung betrifft nur den ersten Probelauf … Stufe 34 ist unverändert fertig. … `<promise>STUFE_34_COMPLETE</promise>`“ |

`claude -p --output-format json` gibt nur das **letzte** Ergebnisobjekt aus. Das Rollenlog der Stufe
trägt deshalb:

```
"result_index": 1, "num_turns": 1, "duration_ms": 3523, "duration_api_ms": 207297,
"usage": { "output_tokens": 181, … }, "total_cost_usd": 1.1271…
```

- **Das Promise stand nur im Log, weil die Rolle es in der zweiten Antwort wiederholt hat.** Ohne die
  Wiederholung hätte der Loop eine fertige, committete Stufe als Exit 43 gemeldet („Sitzung beendet,
  Auftrag unquittiert“).
- Der Abschlussbericht führt die Stufe im Turn-Profil als `1 Turns 1.1271 USD`, neben 18 bis 35 Turns
  aller anderen Stufen desselben Laufs. Turns, Dauer und Token gehören zur zweiten Antwort, die Kosten
  zur ganzen Sitzung.
- Knapp sieben Minuten lag die Sitzung nach dem Promise offen, nur um auf die Meldung zu warten.

## Wo es steckt

- `team/lib.sh`, `team_claude()`: `"$TEAM_CLAUDE_BIN" -p … --output-format json "$@" > "$out"` — die
  Datei hält das letzte Ergebnis der Sitzung, nicht das der Stufe.
- `team/lib.sh`, `team_promise_in()`: liest ausschließlich `data["result"]` aus dieser Datei.
- Turn-Profil des Abschlussberichts und die Rückrechnung in `team/tools/kosten.py` lesen `num_turns`,
  `duration_ms` und `usage` aus derselben Datei; `total_cost_usd` deckt dagegen die ganze Sitzung. Die
  Eichung der Abo-Messung an den Rohlogs zählt so einen Lauf als „reproduziert sich nicht“.

## Warum das jede Installation trifft

Jede bauende Rolle kann einen Befehl über die Frist des Werkzeugs bringen; dann verschiebt die CLI ihn
selbst (Kit-BL-273). Die Auflage „Smoke im Vordergrund“ verhindert das nur für den Testlauf, nicht für
jeden anderen Befehl. Kommt die Meldung nach dem Ergebnis, hängt das Urteil des Loops über die ganze
Stufe am Wortlaut einer beiläufigen zweiten Antwort, und Turn-Profil und Rückrechnung zeigen eine Stufe,
die es so nicht gab.

## Was ich schon versucht habe

Nichts am Kit. Im Projekt war das Urteil richtig, weil die Rolle das Promise wiederholt hat; der Closeout
hat Stufe und Commit nachgeprüft (Code, Tests, Kanarien). Vorschläge:

1. Die Ausgabe als `--output-format stream-json` sichern oder alle Ergebnisobjekte der Sitzung behalten,
   und das Promise in **jedem** davon suchen.
2. Turns, Dauer und Token über alle Ergebnisse summieren; ein Ergebnis mit `result_index > 0` im
   Abschlussbericht als „Antwort auf eine späte Hintergrundmeldung“ ausweisen.
3. Im Briefing der bauenden Rolle: Hat das Werkzeug einen Befehl in den Hintergrund geschoben, stoppt die
   Rolle ihn ausdrücklich, bevor sie quittiert. Hier hieß es in der zweiten Antwort „Er wurde gestoppt“,
   tatsächlich lief er bis zur Zehn-Minuten-Grenze der CLI.

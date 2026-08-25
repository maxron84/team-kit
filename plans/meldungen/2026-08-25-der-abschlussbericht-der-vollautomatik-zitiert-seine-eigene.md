# Der Abschlussbericht der Vollautomatik zitiert seine eigene Ausgabe

- **Art**: Fehler am Kit (kosmetisch, aber informationsvernichtend)
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter, fuenfte
  gebaute Kaskade

## Was passiert ist

`vollautomatik.sh` schreibt sein Lauf-Log nach `.team-logs/vollautomatik-*.log`
und druckt am Ende den Statusbericht **in dasselbe Log**. Der Bericht endet mit
einem Abschnitt, der die letzten drei Zeilen des juengsten Lauf-Logs zeigt —
also seine eigenen letzten drei Zeilen.

So sieht das Ende des Logs eines regulaeren Laufs aus (gekuerzt, aber
woertlich):

```
  ──────── Letzte Commits ────────
    <hash> docs: …
    <hash> fix(uat): …
    <hash> docs(beute): …
    <hash> feat(stufeN): …
    <hash> feat(stufeN-1): …
  ──────── Vollautomatik (letzte 3 Zeilen: vollautomatik-<stempel>.log) ────────
        <hash> feat(stufeN): …
        <hash> feat(stufeN-1): …
      ──────── Vollautomatik (letzte 3 Zeilen: vollautomatik-<stempel>.log) ────────
════════════════════════════════════════════════════════
```

Die Ueberschrift des Abschnitts steht **innerhalb** des Abschnitts, und die
beiden Zeilen darueber sind woertlich dieselben, die zwei Zeilen weiter oben
schon unter „Letzte Commits" stehen. Der Abschnitt traegt damit **null**
Information — er zeigt nicht den Lauf, sondern sich selbst beim Zeigen.

## Wo es steckt

`team-status.sh`, in der Bericht-Funktion:

```
    local letzte_lauf; letzte_lauf="$(ls -t .team-logs/vollautomatik-*.log … | head -1 …)"
    if [ -n "$letzte_lauf" ]; then
        echo "  ──────── Vollautomatik (letzte 3 Zeilen: $(basename "$letzte_lauf")) ────────"
        tail -n 3 "$letzte_lauf" | sed 's/^/    /'
    fi
```

`ls -t | head -1` waehlt das **juengste** Log. Wird der Bericht von
`vollautomatik.sh` als Abschluss des eigenen Laufs gerufen und dessen Ausgabe
in ebendieses Log geschrieben, ist das juengste Log das gerade entstehende —
und `tail -n 3` liest die Zeilen, die der Bericht selbst Sekundenbruchteile
vorher geschrieben hat.

**Der Abschnitt funktioniert richtig, wenn man `./team-status.sh` von Hand
aufruft** (dann ist das juengste Log ein abgeschlossener frueherer Lauf). Er
versagt genau in der Lage, fuer die er offensichtlich gedacht ist: als Ausblick
auf den laufenden bzw. gerade beendeten Lauf.

## Warum das jede Installation trifft

Der Bericht am Ende von `vollautomatik.sh` ist die **einzige** Zusammenfassung,
die ein Mensch nach einem headless-Lauf zu sehen bekommt, und
`plans/`-Abschlussdokumente zitieren ihn. Der Abschnitt sieht aus, als
beantworte er „was ist im Lauf passiert?", beantwortet aber „was habe ich
gerade selbst gedruckt?". Wer ihn liest, ohne es zu bemerken, haelt den
Berichtsschwanz fuer Lauf-Fortschritt — und wer es bemerkt, hat den Platz
trotzdem verloren.

Betroffen ist jede Installation, die `vollautomatik.sh` benutzt; das Verhalten
haengt an nichts Projektspezifischem.

## Was ich schon versucht habe

Nichts lokal gefixt — `team-status.sh` ist unveraendert.

Drei Moeglichkeiten, in aufsteigender Muehe:

1. **Das eigene Log ausnehmen.** Laeuft der Bericht innerhalb eines Laufs,
   kennt der Aufrufer den Pfad seines Logs; er koennte ihn als Variable
   durchreichen, und der Abschnitt waehlt dann das juengste Log **ausser**
   diesem — oder entfaellt ganz.
2. **Den Abschnitt beim Lauf-Abschluss weglassen.** Innerhalb eines Laufs ist
   er per Konstruktion redundant: Alles, was er zeigen koennte, steht bereits
   weiter oben im selben Bericht.
3. **Selbstzitate filtern.** `tail` um die Berichtszeilen bereinigen
   (Trennlinien, `════`) — die schwaechste Loesung, weil sie das Symptom
   behandelt und beim naechsten Umformatieren des Berichts wieder bricht.

Aus meiner Sicht ist (2) die ehrlichste: Der Abschnitt hat innerhalb eines
Laufs keine Aufgabe.

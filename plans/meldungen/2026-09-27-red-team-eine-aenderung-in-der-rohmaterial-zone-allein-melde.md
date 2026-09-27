# Red Team: eine Aenderung in der Rohmaterial-Zone allein meldet 'zurueckgerollt wurde nur der Grenzuebertritt' - zurueckgerollt wurde nichts

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-27-red-team-eine-aenderung-in-der-rohmaterial-zone-allein-melde.md
      .\kit-melden.cmd ablegen  2026-09-27-red-team-eine-aenderung-in-der-rohmaterial-zone-allein-melde.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-27-red-team-eine-aenderung-in-der-rohmaterial-zone-allein-melde.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit — eine Meldung behauptet einen Vollzug, den es nicht gab
- **Kit-Version**: 2.13.1
- **Bahn**: beide (derselbe Ablauf in `team/lib.sh` und `team/lib.psm1`, gelesen); beobachtet in einem Vollautomatik-Lauf
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, beide Bahnen; Spielskript-Stack,
  erste Kaskade gelaufen (4 Stufen, 2 Sweeps, 2 Fixe).

## Was passiert ist

Während der Vollautomatik hat der Stakeholder so, wie es vorgesehen ist, Material in die
Rohmaterial-Zone gelegt: ein Web-Clipping (während einer Ralph-Stufe) und eine
Notizdatei, die er über mehrere Rollenläufe hinweg weiterschrieb. Die
Zonen-Prüfung aus BL-263 hat das richtig erkannt und nichts angefasst. Bei Ralph
und Frank steht danach nur der Zonen-Block. Bei Harry folgt eine zweite Zeile:

```
[harry] ÜBERGRIFF in der Rohmaterial-Zone (raw/ Clippings/) — sie gehört dem Stakeholder, jede Rolle liest dort nur:
  geändert:  raw/<notizdatei>.md
  Nichts davon wurde angefasst (BL-263). Stammt eine Änderung nicht vom Stakeholder, hat die Rolle die Zone verletzt — von Hand prüfen.
[harry] Guard-Übergriff kassiert, Ergebnis zählt — die Arbeit ist geleistet, zurückgerollt wurde nur der Grenzübertritt.
```

Zurückgerollt wurde nichts. Außerhalb der Whitelist hatte Harry keinen Pfad
geändert: Im Log steht keine `GUARD-VERLETZUNG`-Zeile und keine
Vollzugsmeldung. Die Zone selbst wird nach BL-263 nie zurückgesetzt. Die letzte
Zeile widerspricht also der vorletzten („Nichts davon wurde angefasst").

## Wo es steckt

`team_guard_verify` bezieht die Zone mit ein (Kommentar zu BL-263: „Ein Übergriff dort
zählt wie jeder andere, nur ohne Rollback"). Bleibt die Pfadliste leer, gibt
die Funktion den Befund der Zone zurück:

- bash: `team/lib.sh`, `team_guard_verify`: `[ -z "$roh" ] && return "$raw_rc"`
- pwsh: `team/lib.psm1`, `team_guard_verify`: `if (-not $roh.Count) { return $rawSauber }`

Der Aufrufer (`team/redteam.sh`/`.ps1`, ebenso `axel.sh`/`.ps1`) setzt daraufhin
den Übergriff auf 1. `team_guard_urteil` hat für diesen Fall nur einen Text, und
zwar den mit Rollback. Unterscheiden kann es nicht, weil `team_guard_verify`
„Pfad zurückgerollt" und „nur die Zone hat sich geändert" mit demselben
Rückgabewert meldet.

Ralph und Frank rufen `team_raw_pruefen` direkt auf und werten das Ergebnis
nicht als Übergriff (`|| true` bzw. `| Out-Null`). Dieselbe Handlung des
Stakeholders wird also je nach Rolle verschieden eingestuft. Ob das gewollt ist,
kann ich nicht beurteilen. Der falsche Vollzugstext ist es sicher nicht.

## Warum das jede Installation trifft

Material in `raw/` oder `Clippings/` abzulegen, während ein Lauf arbeitet, ist
der vorgesehene Gebrauch der Zone und kein Randfall. Jede Installation, deren
Stakeholder während eines Sweeps etwas ablegt oder weiterschreibt, bekommt
diese Zeile. Sie behauptet einen Vollzug, den es nicht gab. Genau das hat
BL-24 für die Vollzugsmeldung des Guards abgestellt, und der Kommentar dort
nennt die Regel schon: „Die Vollzugsmeldung darf nicht mehr behaupten, als
geschehen ist."

Bei Axel wiegt es schwerer. Fehlt dort das Ergebnis, lautet die Meldung
„Guard-Übergriff UND kein vollständiges Ergebnis". Die Notiz des Stakeholders
wird dann zur Hälfte der Begründung für einen gescheiterten Aufruf.

Dazu kommt eine weichere Folge: Der Lauf dauerte gut eine Stunde, und im Log
standen fünf ÜBERGRIFF-Blöcke, alle ausgelöst vom Stakeholder selbst. Eine
Warnung, die bei normalem Gebrauch regelmäßig kommt, erzieht dazu, sie zu
überlesen.

## Was ich schon versucht habe

Lokal habe ich nichts geändert: Es sind Kit-Dateien, und ein lokaler Fix verfiele
beim nächsten `--update`. Im Closeout geprüft: Die Zeitstempel beider Dateien
liegen in den gemeldeten Rollenläufen, der Stakeholder hat beide selbst
angelegt, und keine Rolle hat in die Zone geschrieben.

**Vorschlag:** `team_guard_verify` meldet den Fall „nur die Zone" getrennt,
z. B. mit Rückgabe 2 statt 1. `team_guard_urteil` sagt dann, was tatsächlich
war: „Rohmaterial-Zone verändert (siehe oben), nichts zurückgerollt. Stammt die
Änderung vom Stakeholder, ist nichts zu tun."
**Nachweis:** `test_bl16_guard_zuschreibung` um den Fall „Zone geändert,
Whitelist sauber" erweitern und den Meldungstext prüfen, auf beiden Bahnen.
**Gegenprobe:** mit dem alten Rückgabewert meldet der Test wieder
„zurückgerollt".

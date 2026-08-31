# Der Abbruchbericht meldet 'Keine offenen Funde', wenn die Red-Team-Phase nie erreicht wurde — und schlaegt den Closeout einer ungeprueften Kaskade vor

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python-Dienst plus
  Electron-Oberfläche, siebte Kaskade, Beutebuch mit 25 abgeschlossenen Funden.

## Was passiert ist

Ein Vollautomatik-Lauf wurde vom Pro-Lauf-Deckel gestoppt, und zwar
**unmittelbar nachdem Ralph seinen Feierabend gemeldet hatte** — also sauber
zwischen Phase 1 (Bau) und der Phase Red Team, ohne Rollback:

```
Ralph: Stufe <letzte+1> liegt über RALPH_CAP=<cap> — Feierabend.
LAUF-BUDGET erreicht: dieser Lauf 24.7341 USD >= Deckel 24 USD — harter Stopp
--- WIE ES WEITERGEHT (Budget-Deckel) ---
Keine offenen Funde — nur der Closeout fehlt:
  .\team-status.cmd --rollen-abschluss <N> <domaene>
Ganzen Lauf fortsetzen: .\vollautomatik.cmd (nimmt den Faden am Zeigerstand auf)
```

**Beide Hälften dieses Vorschlags sind irreführend, und sie verstärken
einander.**

### (a) „Keine offenen Funde" ist wahr und trotzdem falsch

Zu diesem Zeitpunkt waren Harry und Marv **nie gelaufen**. Der Bericht liest
das Beutebuch, findet dort nichts mit offenem Status und schließt daraus auf
„fertig". Er kann **„es gibt keine Funde, weil nicht gesucht wurde"** nicht von
**„es gibt keine Funde, weil nichts zu finden war"** unterscheiden — und er
sagt den Unterschied auch nicht dazu.

Wer dem Vorschlag folgt, schreibt ein Abschlussprotokoll, das eine
**ungeprüfte** Kaskade als geprüft ausweist.

**Das ist hier keine Theorie.** Der Lauf wurde stattdessen neu gestartet, die
Red-Team-Phase lief nach, und **Marv fand einen echten Fund** (Schweregrad
mittel): Ein in derselben Kaskade neu gebauter Wächter, der laut Vertrag *jedes*
Bedienelement gegen zwei Gestaltungswerte prüfen sollte, enumerierte nur drei
der vier vertraglich genannten Element-Gattungen. Wäre dem Bericht gefolgt
worden, wäre dieser Fund nie gefunden und die Kaskade als geprüft geschlossen
worden.

### (b) Der `<N>`-Platzhalter lädt zur Stufennummer ein

Der vorgeschlagene Befehl wird wörtlich mit `<N>` gedruckt. Die letzte Zahl,
die unmittelbar darüber im Log steht, ist die **Stufennummer** (aus
`RALPH_CAP=<cap>` und „Stufe <n> abgeschlossen"). Genau sie wurde eingesetzt —
und das Werkzeug hat sie widerspruchslos als **Kaskadennummer** gebucht: zwei
Ledger-Zeilen unter einer Kaskade, die es nicht gibt.

Das ist der Fall aus der Meldung *„rollen-abschluss nimmt jede Zahl als
Kaskadennummer"* (2026-08-30) — hier zum ersten Mal beobachtet, wie der
Abbruchbericht ihn aktiv **herbeiführt**. Die beiden Meldungen hängen also
zusammen: Die eine beschreibt die fehlende Plausibilitätsprüfung, diese hier
beschreibt, wer die falsche Zahl anbietet.

### Verschärfend: die Null-Zeile

Weil die Log-Ablage der Rollen leer war — genau deshalb, weil die Sweeps nie
liefen —, wurde die `roles`-Zeile mit **0.0000 USD** gebucht. Eine solche Zeile
liest sich ein halbes Jahr später als *„die Rollen haben nichts gekostet"* und
**nicht** als *„die Rollen sind nie gelaufen"*. Der Unterschied ist genau der,
den (a) verschweigt — er pflanzt sich also bis in den Kostenbericht fort.

## Wo es steckt

In der Vollautomatik der jeweiligen Bahn, im Zweig „WIE ES WEITERGEHT
(Budget-Deckel)" — in dieser Ablage `vollautomatik.ps1`, in der Bash-Bahn die
entsprechende Stelle in `vollautomatik.sh`.

**Die nötige Information liegt vor, sie wird nur nicht benutzt:**

1. **Der erreichte Phasenstand ist der Vollautomatik bekannt** — sie führt die
   Phasenkette selbst aus und weiß, ob sie Phase Red Team betreten hat. Der
   Bericht fragt stattdessen das Beutebuch, also die **falsche** Quelle: Das
   Beutebuch beantwortet „gibt es offene Funde?", nicht „wurde gesucht?".
2. **Die Kaskadennummer steht in `.ralph-plan`** (im Dateinamen des Plans) und
   ist dem Bericht ebenfalls bekannt — er druckt trotzdem `<N>`.

## Warum das jede Installation trifft

Der Text steht in einem Entrypoint des Kits, nicht im Produktivcode eines
Projekts. **Jede** Installation, deren Lauf am Deckel vor der Red-Team-Phase
endet, bekommt denselben Satz — und der Deckel greift bauartbedingt dann, wenn
eine Kaskade teurer war als geplant, also gerade bei den Läufen, die eine
Prüfung am nötigsten hätten.

Der Fehler ist besonders unangenehm, weil er **in Richtung „fertig" irrt**. Ein
Werkzeug, das fälschlich „noch nicht fertig" meldet, kostet eine Nachfrage; ein
Werkzeug, das fälschlich „fertig" meldet, beendet den Vorgang. Die einzige
Instanz, die den Widerspruch bemerken könnte, ist ein Mensch, der sich erinnert,
dass die Sweeps im Log fehlen — und genau der liest den Abbruchbericht, um sich
das Erinnern zu sparen.

## Was ich schon versucht habe

- **Nichts lokal gepatcht.** Der Fehler steckt in einem Entrypoint des Kits;
  ein lokaler Fix verfiele beim nächsten `--update`.
- **Die Folgen im Projekt repariert:** Beide falsch gebuchten Ledger-Zeilen
  tragen jetzt die richtige Kaskadennummer, die Null-Zeile wurde nach dem
  nachgeholten Lauf per `--addieren` auf den echten Betrag gezogen und trägt
  eine Notiz, die den Sachverhalt ausspricht. `--ledger-pruefen` meldet
  0 Warnungen.
- **Beobachtung zur Erkennung:** `--ledger-pruefen` hat den nachgelagerten
  Zustand zuverlässig gemeldet („Kaskade bereits gebucht, aber es liegen
  unarchivierte Logs"). Es meldet damit die **Folge**, nicht die Ursache — und
  auch nur, weil danach doch noch Rollen liefen. Wäre der Lauf nach dem
  Abbruchbericht endgültig geschlossen worden, hätte **nichts** angeschlagen:
  Ledger stimmig, Logs archiviert, Beutebuch ohne offene Funde.

## Vorschlag

Zwei kleine, voneinander unabhängige Änderungen:

1. **Den Satz am Phasenstand ausrichten**, statt am Beutebuch. Etwa:
   *„Abbruch vor Phase Red Team — Harry und Marv sind für diese Kaskade nicht
   gelaufen. `Keine offenen Funde` heißt hier `nicht gesucht`. Erst
   `.\vollautomatik.cmd` fortsetzen, dann den Closeout."* Nur wenn die
   Fixphase wirklich durchlaufen wurde, ist „nur der Closeout fehlt" richtig.
2. **Die Kaskadennummer einsetzen** statt `<N>` zu drucken.

## Querverweis

Gleicher Bericht, anderes Symptom: die Feld-E-Meldung vom 2026-08-29
(*„vollautomatik.sh nimmt nach Abbruch nicht die abgebrochene Phase auf"*)
beschreibt die **Wiederaufnahme**; diese hier beschreibt den
**Wahrheitsgehalt** des Satzes. Und die Meldung vom 2026-08-30
(*„rollen-abschluss nimmt jede Zahl als Kaskadennummer"*) beschreibt die
fehlende Plausibilitätsprüfung, für die dieser Bericht die falsche Zahl
liefert.

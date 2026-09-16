# Der Ledger bucht Dollar, gemessen werden Token -- die Basis hat ein Verfallsdatum, das Messergebnis nicht

- **Art**: Verbesserungsvorschlag (kein Fehler — die Buchungen stimmen; sie
  sind nur nicht nachrechenbar)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst
  plus Electron-Oberfläche, rund 1000 Tests, 22 gebaute Kaskaden, Ledger mit
  75 Zeilen über acht Wochen. Auth durchgehend Abo, Modelle `sonnet` für die
  Loop-Rollen und `opus` für Architekt und Forensiker.

## Was passiert ist

**Nichts ist kaputtgegangen — das ist der Punkt.** `kosten.py sitzung-messen`
zählt je Modell **fünf** Größen und druckt sie auch aus:

```
claude-opus-5  (5.00 USD/Mio Input)
  input                    684 Tok
  output               292,612 Tok
  cache_read       110,531,284 Tok
  cache_write_5m             0 Tok
  cache_write_1h     1,200,125 Tok
  = Summe              74.5856 USD
```

In den Ledger geht davon **eine einzige Zahl**: `74.5856`. Die fünf
Token-Sorten, das Modell und der Preisstand, mit dem multipliziert wurde, sind
nach der Buchung **weg**. Die Umrechnung ist damit unumkehrbar, und zwar in
dem Moment, in dem sie am wenigsten kostet, sie mitzuschreiben.

**Im Abo ist der gebuchte Betrag ohnehin schon eine Ableitung.** Die
Ledger-Zeilen dieses Projekts tragen den Vermerk *Abo-Gegenwert* — es ist
niemandem etwas abgerechnet worden. Gebucht wird eine **Bewertung von Token zu
API-Preisen**. Die eigentliche Messgröße ist also längst der Token; der Dollar
ist bereits die abgeleitete Größe — nur die, die gespeichert wird.

## Wo es steckt

- `team/tools/kosten.py` — misst alle fünf Sorten je Modell, gibt aber nur die
  Dollar-Summe an den Aufrufer weiter.
- Das Ledger-Format selbst (`.budget-ledger`): `Datum | Kaskade | Betrag |
  Auth | Domäne | Akteur | Notiz`. Es gibt **kein** Feld für Token, keines für
  das Modell und keines für den Preisstand.
- `--rollen-abschluss`, `--architekt-abschluss`, `--budget`, `--ledger-pruefen`
  — alle rechnen auf der Dollar-Spalte.
- Die Preistabelle (`TEAM_PREISE`, seit `BL-211` aus der Projektkonfiguration
  übersteuerbar) ist der Wechselkurs, und sie hat **kein Gültigkeitsdatum**.

## Warum das jede Installation trifft

**Das Feld hat schon bewiesen, was ein falscher Wechselkurs anrichtet.** In
diesem Projekt war der Kit-Basispreis für `claude-sonnet-5` mit 2.00 statt
3.00 USD/Mio Input hinterlegt — durchgehend **33,3 % zu niedrig**. Die
Selbsteichung schlug an 126 von 128 abgerechneten Läufen fehl und **blockierte
jede Architekten-Buchung**, bis der Wert korrigiert war; ein Kit-Update hat den
lokalen Patch später wieder überbügelt (`BL-166`, `BL-211`, lokal `BL-22`).

**Mit Token als Basis wäre das eine Neuberechnung gewesen. Mit Dollar als
Basis ist es ein Datenverlust.** Jede vor der Korrektur gebuchte Zeile ist
dauerhaft falsch, und **niemand kann sie nachrechnen** — die Tokenzahlen, aus
denen sie entstand, stehen nirgends. Dasselbe gilt für jede künftige
Preisänderung eines Anbieters, und Preise ändern sich häufiger als
Ledger-Formate.

**Zwei weitere Stellen, an denen die fehlende Basis heute schon weh tut:**

1. **Der Ledger sagt nicht, welches Modell die Kosten verursacht hat.** Eine
   Zeile über 36,90 USD ist ohne Modell- und Preisstand keine wiederholbare
   Aussage. Vergleiche über mehrere Kaskaden hinweg — die Hauptnutzung des
   Ledgers — vergleichen damit stillschweigend Äpfel mit Birnen, sobald ein
   Modellwechsel oder eine Preisanpassung dazwischenliegt. Ein Modellwechsel
   ist im Kit ein Einzeiler (`TEAM_MODEL_LOOP`), also der Normalfall.
2. **Der Abo-Gegenwert ist der einzige Wert, den das Kit über Abo-Nutzung
   überhaupt bilden kann** — und er ist die Größe, die am stärksten von der
   Preisliste abhängt, weil ihr nie eine Rechnung gegenübersteht.

## Was vorgeschlagen wird

**Kern: Token sind die gebuchte Basis, Dollar eine jederzeit neu berechenbare
Ableitung.**

1. **Token je Sorte und je Modell in die Ledger-Zeile**, nicht als Summe:
   `input`, `output`, `cache_read`, `cache_write_5m`, `cache_write_1h` tragen
   **verschiedene** Preisfaktoren — eine zusammengezählte Tokenzahl ist
   genauso wenig rückrechenbar wie der heutige Dollarwert. Fünf Zahlen je
   Modell, nicht eine.
2. **Dollar bleiben sichtbar, aber als Ableitung**, gerechnet aus den Token
   und einer Preisliste **mit Gültigkeitsdatum**. Jede Ausgabe nennt, welchen
   Preisstand sie benutzt hat.
3. **Berechnungsgrundlage sind bei Drittanbietern immer die jeweils aktuell
   geltenden API-Preislisten, nicht die Abopreise.** Das ist heute schon die
   gelebte Praxis (*Abo-Gegenwert*), aber nirgends als Regel festgeschrieben.
4. **Für selbstgehostete Modelle eine Verbrauchskostenpauschale je Mio Token**
   (Strom, Verschleiß, anteilige Hardware) — eine Näherung, die genau deshalb
   funktioniert, weil sie auf Token rechnet. Auf Dollar-Basis gäbe es dafür
   überhaupt keinen Anknüpfungspunkt: Ein lokal laufendes Modell bekommt nie
   eine Rechnung.
5. **Jede Auflösung muss beide Richtungen können** — je Sitzung, je Akteur, je
   Kaskade, in Summe, und einzeln bis auf den einzelnen Aufruf hinunter.

**Geltungsbereich, ausdrücklich eng gefasst (Entscheid des meldenden
Strippenziehers):** Das gilt **ab dem erstbesten neuen Projekt**.
**Bestandsprojekte werden NICHT nachgerüstet** — deren Token sind nicht mehr
zu beschaffen, eine Migration würde also Zahlen erfinden, und ihr Ledger
funktioniert ja.

**Genau daraus folgt die einzige Auflage, die diese Meldung dem Kit machen
möchte: Das Format braucht eine Kennung.** Solange beide Sorten Ledger
nebeneinander im Feld stehen, muss jedes Werkzeug einer Zeile ansehen können,
ob sie token- oder dollargeboren ist — sonst summiert `--budget` zwei
Datenformate zu einer Zahl, und das ist wieder genau die Bauform, mit der der
2.00-gegen-3.00-Fehler so lange unsichtbar geblieben ist: **ein in sich
stimmiger Bericht über eine Datei mit zwei Wahrheiten.** Eine
Format-/Versionsmarke je Zeile ist billig, solange es die zweite Sorte noch
nicht gibt.

## Was ich schon versucht habe

Nichts davon ist lokal gebaut — die Meldung kommt **vor** einer Umsetzung,
weil das Ledger-Format dem Kit gehört und ein lokaler Vorgriff beim nächsten
`--update` wieder überbügelt würde (`BL-42`/`BL-58`; in diesem Projekt genau
so passiert mit dem Preis-Patch, siehe oben).

Was dieses Projekt beisteuern kann, ist der **Beleg, dass die Rohdaten
vorhanden sind**: Die fünf Sorten stehen in jeder `sitzung-messen`-Ausgabe,
und die Rollen-Logs (`.ralph-logs/`, `.team-logs/`) enthalten sie ebenfalls
je Aufruf. Der Schritt ist also **Mitschreiben**, nicht Messen — der teure
Teil ist längst gebaut.

**Ein Hinweis zur Reihenfolge:** Wenn das Kit die Umstellung macht, dann
zuerst das **Schreiben** (Token mitbuchen, Dollar weiter wie heute ausgeben)
und erst danach das **Rechnen** (Dollar aus Token ableiten). Nach dem ersten
Schritt existiert die Basis; der zweite ist dann jederzeit nachholbar und
gegen die alten Zeilen prüfbar — ein Umbau in einem Zug hat diese Gegenprobe
nicht.

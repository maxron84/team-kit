# rollen-abschluss bricht HALB ab und meldet, es habe gar nicht gehandelt - die ralph-Haelfte ist gebucht und archiviert

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (zwölf Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 480 Tests.

## Was passiert ist

Kostenabschluss einer Kaskade, regulärer Aufruf:

```
.\team-status.cmd --rollen-abschluss <N> <domaene> "<notiz-rollen>" "<notiz-bau>"
```

**Antwort (gekürzt auf die Sache):**

```
WARNUNG: 3 Log(s) sind AELTER als der Beginn der Kaskade <N> (<zeitpunkt>)
  -- es wird NICHTS gebucht und NICHTS archiviert:
  .team-logs\frank-<fund>-v1-<stempel>.json (<zeit>)
  .team-logs\frank-<fund>-v2-<stempel>.json (<zeit>)
  .team-logs\frank-<fund>-v1-<stempel>.json (<zeit>)
  Gehoeren sie zu einer Out-of-Loop-Runde zwischen zwei Kaskaden, gehoeren sie
  unter eine eigene benannte Nummer (`--kaskade vor-N`) - sonst traegt diese
  Kaskade fremde Kosten (BL-45).
  Gehoeren sie doch zu dieser Kaskade, bucht `--auch-aeltere` sie mit (BL-221).
```

Die Prüfung selbst ist **richtig und wertvoll** — die drei Logs stammten
tatsächlich aus einer Out-of-Loop-Runde zwischen zwei Kaskaden, und ich hätte
sie ohne diese Warnung mit einer erklärenden Notiz unter der falschen Nummer
gebucht.

**Falsch ist der Satz „es wird NICHTS gebucht und NICHTS archiviert".** Er gilt
nur für die `roles`-Hälfte. Die `ralph`-Hälfte war zu diesem Zeitpunkt bereits
**gebucht** und `.ralph-logs` bereits **archiviert**.

Sichtbar wird das erst beim zweiten Aufruf — nachdem man, der Empfehlung
folgend, die drei Fremdlogs beiseitegelegt hat:

```
Warnung: keine Log-Dateien in .ralph-logs gefunden -- es wird 0.0000 USD gebucht.
Fehler: Fuer Kaskade <N> steht bereits eine ralph-Zeile ueber <betrag> USD.
  Dieser Aufruf wuerde sie durch 0.0000 USD ERSETZEN und die Differenz verlieren.
  Es wird NICHTS geschrieben.
    Nachlauf: --addieren  -> <betrag> USD
    Korrektur: --ersetzen -> 0.0000 USD
```

Man steht also vor einer Kollisionsmeldung über eine Zeile, die man nach der
ersten Meldung gar nicht geschrieben haben kann, und vor einem leeren
Log-Ordner, dessen Inhalt nach derselben Meldung noch dort liegen müsste.

Symmetrisch verhält sich der zweite Aufruf übrigens genauso: Er meldet für die
`ralph`-Hälfte „Es wird NICHTS geschrieben" und schreibt die `roles`-Zeile.

## Wo es steckt

In der Abschluss-Routine hinter `--rollen-abschluss` (`team/tools/kosten.py`,
die Verzweigung, die `roles` und `ralph` als zwei Ledger-Zeilen bucht und beide
Log-Ordner archiviert). Die beiden Quellen werden **nacheinander und unabhängig
voneinander** abgearbeitet; der Abbruchtext ist aber im Singular für den ganzen
Aufruf formuliert.

Der Kern ist nicht die Reihenfolge, sondern die **Aussage**: Ein Befund an einer
Quelle beendet die Verarbeitung dieser Quelle und meldet das als Aussage über
den gesamten Aufruf.

## Warum das jede Installation trifft

Die Altersprüfung ist neu genug (`BL-221`), dass sie fast jede gewachsene
Installation irgendwann trifft — Out-of-Loop-Fixe zwischen zwei Kaskaden sind
der Normalfall, nicht die Ausnahme. Und der Text ist unmissverständlich: Wer
„NICHTS gebucht und NICHTS archiviert" liest, hat keinen Anlass, das Ledger
gegenzuprüfen.

**Der gutartige Ausgang ist Glück, nicht Konstruktion.** Hier hat der
Kollisionsschutz zugeschlagen und die 0,0000-Ersetzung abgefangen. Ohne ihn —
oder mit einem `--ersetzen`, das man in dieser Lage für den richtigen Griff
halten könnte, weil das Werkzeug ihn selbst als „die Altzeile war falsch"
anbietet — wäre die bereits gebuchte Bau-Zeile durch 0,0000 überschrieben
worden. Die Hilfe zur Auswahl legt das sogar nahe: *„Wurde seit der Altzeile
NICHT archiviert, zaehlen beide Aufrufe dieselben Logs — dann ist --ersetzen
richtig."* Hier **wurde** archiviert, aber genau das kann man nach der ersten
Meldung nicht wissen.

## Was ich schon versucht habe

- **Ledger und Archiv gegengeprüft**, statt der Meldung zu glauben — daher der
  Befund. Beide Zeilen stehen am Ende korrekt, weil ich den zweiten Aufruf nicht
  mit `--ersetzen` beantwortet habe.
- **Getrennte Buchung gefahren**, wie die Warnung sie vorschlägt: Fremdlogs
  beiseitelegen, Kaskade regulär abschließen, Fremdlogs zurücklegen, dann unter
  `--kaskade vor-N` buchen. Das funktioniert und erzeugt saubere Zeilen —
  einschließlich einer ehrlichen `0.0000`-Bau-Zeile für die Out-of-Loop-Runde.
- **Kein lokaler Fix**, weil der Befund in `team/` sitzt.

**Zwei Richtungen, unabhängig voneinander nützlich:**

- **(a) Der Text.** Die Meldung sagt, für welche Quelle sie gilt („für die
  roles-Hälfte wird nichts gebucht") und ob die andere schon durch ist. Das
  allein hätte den ganzen Irrweg vermieden.
- **(b) Das Verhalten.** Beide Quellen erst prüfen, dann buchen — ein Befund an
  einer Quelle hält den ganzen Aufruf an, bevor irgendetwas geschrieben oder
  archiviert wird. Das entspräche dem, was der Text heute schon behauptet.

**(b) ist die eigentliche Reparatur**, (a) allein macht die Halbheit nur
sichtbar statt harmlos.

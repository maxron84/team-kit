# kosten.py sitzung-messen laeuft ueber den dokumentierten Direktaufruf ungeeicht - TEAM_PREISE erreicht es nur ueber die Shell-Konfiguration

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (zwölf Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 480 Tests.

## Was passiert ist

Im Closeout wollte ich die Architektensitzung messen. Das Briefing der Rolle
nennt dafür einen **Direktaufruf**:

```
python3 team/tools/kosten.py sitzung-messen --projekt .
```

Ergebnis:

```
  ! Preistabelle stimmt nicht mehr: 159 von 161 nachgerechneten Laeufen weichen ab.
      <lauf-a>.json: abgerechnet 0.6739, gerechnet 0.4499 (33.2 % daneben)
      <lauf-b>.json: abgerechnet 1.0022, gerechnet 0.6688 (33.3 % daneben)
      <lauf-c>.json: abgerechnet 1.3884, gerechnet 0.9262 (33.3 % daneben)
    Die Zahl unten ist damit UNGEEICHT. Preistabelle in kosten.py nachziehen
    (oder TEAM_PREISE setzen), bevor du sie buchst.
```

Die Abweichung ist bei **allen** Läufen konstant (Faktor 1,5) und damit
eindeutig ein Tabellensatz, kein Streuungsproblem — das Werkzeug erkennt das
auch richtig und schlägt selbst eine `TEAM_PREISE`-Zeile vor.

Derselbe Aufruf, nur mit vorangestelltem `TEAM_PREISE=<modell>=<satz>`:

```
  ✓ Preistabelle geeicht an 161 abgerechneten Laeufen dieses Projekts
```

**Gleiche Sitzung, gleiche Ausgabezahl, gegensätzliche Buchbarkeit.** Die Regel
im Briefing ist eindeutig (*ungeeicht → nicht buchen*), also blockiert der
dokumentierte Aufruf den Kostenabschluss, für den er dokumentiert ist.

## Wo es steckt

Nicht in der Preistabelle — die ist im Projekt korrekt gesetzt. `TEAM_PREISE`
wird ausschließlich von der **Shell-Konfiguration** (`team.config.ps1`,
analog `team.config.sh`) in die Umgebung exportiert. Ein Direktaufruf von
`team/tools/kosten.py` lädt diese Datei nie und sieht die Variable deshalb
nicht.

Betroffen sind damit zwei Stellen zugleich:

1. **Das Rollen-Briefing des Architekten** (`team/prompts/rolle-architekt.md`)
   nennt den Direktaufruf als *den* Weg — an zwei Stellen, einmal in der
   Scharfschalt-Sequenz und einmal unter „Woher `<USD>` kommt".
2. **`kosten.py` selbst** liest `TEAM_PREISE` nur aus der Umgebung und hat
   keinen Rückfallweg auf die Konfigurationsdatei des Projekts, obwohl es sie
   über `--projekt .` bereits kennt.

## Warum das jede Installation trifft

Jede Installation, die ihre Preistabelle über `TEAM_PREISE` pflegt — also genau
der Weg, den `Kit-BL-211` eingeführt hat —, bekommt beim dokumentierten Aufruf
eine ungeeichte Zahl. Die Fehlermeldung zeigt dabei **auf die Preistabelle**,
während der Fehler im **Aufrufweg** sitzt: Sie empfiehlt, `kosten.py`
nachzuziehen oder `TEAM_PREISE` zu setzen — beides ist im Projekt bereits
geschehen.

Die wahrscheinliche Reaktion ist deshalb, den korrekten Wert **ein zweites Mal**
in `kosten.py` zu patchen. Genau dieser Patch ist der, den das nächste
`--update` überbügelt (bekannt als `BL-42`/`BL-58`), und man landet in der
Schleife, aus der `Kit-BL-211` herausführen sollte.

**Der stille Ausgang ist der schlimmere Fall:** Wer die Warnung überliest, bucht
eine um den Tabellenfaktor verschobene Zahl ins Ledger — hier wären es 33 %
gewesen. Die Selbsteichung, die das verhindern soll, hat korrekt angeschlagen;
sie wird nur an einer Stelle ausgelöst, an der sie nicht muss.

## Was ich schon versucht habe

- **Ursache verifiziert:** Der konstante Faktor 1,5 über alle 159 Läufe
  entspricht exakt dem Verhältnis zwischen dem Satz in der eingebauten Tabelle
  und dem in der Projekt-Konfiguration hinterlegten. Kein Streuungs-, sondern
  ein Versatzbefund — das Werkzeug klassifiziert selbst korrekt.
- **Umgehung, lokal, ohne Änderung am Kit:** `TEAM_PREISE` beim Aufruf
  voranstellen. Damit meldet dieselbe Messung „geeicht an 161 Läufen". Kein
  Patch an `kosten.py` — bewusst nicht, siehe oben.
- **Nicht versucht:** den Wrapper zu nehmen. Für `sitzung-messen` gibt es
  keinen; die anderen Verben laufen über den Statuswrapper und sind deshalb
  nicht betroffen. Das ist auch der Grund, warum der Fehler ausgerechnet hier
  auftritt.

**Zwei Reparaturrichtungen, beide klein:**

- **(a)** `kosten.py` liest die Projekt-Konfiguration selbst, wenn `--projekt`
  gegeben ist, und nimmt `TEAM_PREISE` daraus, falls die Umgebung schweigt.
- **(b)** Das Briefing nennt den Aufruf über den Wrapper statt direkt — oder
  `sitzung-messen` bekommt einen, wie die übrigen Verben.

**(a) ist die tragfähigere**, weil sie auch den Aufruf von Hand deckt; **(b)**
allein würde die Meldung nur seltener machen. Eine dritte Möglichkeit wäre, die
Diagnosezeile um den Satz zu ergänzen, dass eine gesetzte, aber nicht geladene
Projekt-Konfiguration dieselbe Meldung erzeugt — das würde den Irrweg schon
abkürzen.

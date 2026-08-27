# Ein Update traegt neue Konfigurationswerte nicht ins Feldprojekt nach — der Rueckkanal war danach wieder tot

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-08-27-ein-update-traegt-neue-konfigurationswerte-nicht-ins-feldpro.md
      .\kit-melden.cmd ablegen  2026-08-27-ein-update-traegt-neue-konfigurationswerte-nicht-ins-feldpro.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-08-27-ein-update-traegt-neue-konfigurationswerte-nicht-ins-feldpro.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1 + `[Unreleased]` (Stand 2026-08-27, aus dem lokal liegenden Kit aktualisiert)
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Greenfield, Windows 11, **einbahnig pwsh** (`--nur-pwsh`), Python + Electron, vier geplante Kaskaden. Die Installation stammt aus der Zeit vor `BL-153`.

## Was passiert ist

`--update` lief durch und meldete Erfolg. Der anschließende Regressionslauf war
rot — **ein** Fall von 390:

```
FAILED team/tests/test_bl182_rueckkanal_auf_der_pwsh_bahn.py::test_die_werkzeugzeile_steht_in_der_konfiguration
AssertionError: team.config.ps1 setzt TEAM_MELDUNG_TOOL nicht — dann hat der
Rueckkanal auf dieser Bahn keinen Interpreter, und wir sind wieder bei BL-182.
```

Der Fall beschreibt die Lage genau. Der Rückkanal war nach dem Update wieder
tot, mit **wörtlich derselben** Meldung wie vor `BL-182` — nur eine Zeile
weiter unten, weil der Fix den `& $TEAM_PYTHON`-Aufruf durch
`Team-Werkzeug $TEAM_MELDUNG_TOOL` ersetzt hat und nun `Team-Werkzeug` auf eine
leere Zeichenkette läuft:

```
.\kit-melden.cmd kit-pfad

The expression after '&' in a pipeline element produced an object that was not
valid. It must result in a command name, a script block, or a CommandInfo object.
At <projekt>/team/lib.psm1:146 char:7
+     & $befehl @($rest + $Argumente)
```

Ein Abgleich der Schlüsselmengen zeigte, dass **vier** Werte fehlen, die die
Vorlage `pwsh/entry/team.config.ps1` inzwischen setzt:

| fehlender Wert | eingeführt mit | Wirkung im Feld |
|---|---|---|
| `TEAM_MELDUNG_TOOL` | `BL-182` | **hart** — `& ''` bricht ab, jedes Verb des Rückkanals |
| `TEAM_KIT_PFAD` | `BL-153` | still — `--kit ''`, das Werkzeug fällt auf seine eigene Suche zurück |
| `TEAM_FELD_KUERZEL` | `BL-168` | still — `--kuerzel ''`, jede Meldung ohne Kürzel |
| `TEAM_CLAUDE_BIN` | `BL-173` | gnädig — `lib.psm1` fällt auf `'claude'` zurück |

Die drei stillen Werte fehlten seit Wochen, ohne dass irgendetwas darauf
hinwies. Aufgefallen sind sie erst beim Nachsehen wegen des vierten.

## Wo es steckt

Im Installer (`pwsh/install.ps1`, `--Update`; die bash-Bahn ist bauartgleich).
Der Grundsatz *„`-Update` fasst `team.config.*` nicht an"* ist richtig — die
Datei trägt Projektwerte, die kein Update überschreiben darf. Aber es gibt
**keinen Schritt, der die Schlüsselmenge abgleicht**: Ein Wert, den die Vorlage
neu einführt, erreicht eine bestehende Installation nie und wird auch nicht
gemeldet.

Der Schnitt, der hier fehlt, existiert im Haus bereits — `Python-Abgleich`
(`BL-133`) ist wörtlich derselbe Gedanke, nur für **einen** Wert:

> *„`-Update` fasst `team.config.*` nicht an" ist richtig; „sieht sie gar nicht
> an" war es nicht. […] Gemeldet, nicht repariert: Die Konfiguration trägt
> Projektdaten, und der Nachtrag steht als kopierbare Zeile daneben.*

Nebenbefund an genau dieser Funktion: Die kopierbaren Zeilen, die sie ausgibt,
nennen `TEAM_BEUTEBUCH_TOOL` und `TEAM_KOSTEN_TOOL` — `TEAM_MELDUNG_TOOL` ist
seit `BL-182` die dritte Zeile derselben Bauart und fehlt dort ebenfalls.

## Warum das jede Installation trifft

**Jeder künftige Fix, der einen neuen Konfigurationswert einführt, ist im Feld
ab dem Update ein Regress statt eines Fixes.** Der neue Code liest den Wert,
die bestehende Konfiguration setzt ihn nicht — und welche Wirkung das hat,
entscheidet der Zufall: hart (`BL-182`), still (`BL-153`, `BL-168`) oder gnädig
(`BL-173`). Die stille Klasse ist die teure: Sie sieht wie Betrieb aus.

`BL-182` ist dafür der schärfste Beleg. Der Fix ist im Kit vollständig gebaut
und mit fünf Prüfrichtungen belegt; im Feld hat das Update ihn ausgeliefert und
den Fehler **im selben Zug wiederhergestellt**. Gefangen hat das ausschließlich
die Gegenrichtung des mitgelieferten Falls („man darf (1) nicht durch Löschen
grün machen") — und die gibt es nur, weil dieser eine Fund sie zufällig
brauchte. Für `BL-153`, `BL-168` und `BL-173` existiert nichts Vergleichbares,
und genau diese drei sind hier unbemerkt geblieben.

Der Riegel `test_jeder_konfigurationswert_steht_in_der_exportliste` prüft
bereits eine Richtung dieser Gattung: *was die Konfiguration setzt, muss die
Modulgrenze überleben*. Die Gegenrichtung — *was die Vorlage setzt, muss die
Installation haben* — ist ungeprüft, und sie ist die, die im Feld zuschlägt.

## Vorschlag

1. **`Konfig-Abgleich` statt `Python-Abgleich`** — dieselbe Bauform, über die
   ganze Schlüsselmenge: `--Update` vergleicht die `$TEAM_*`-Namen der Vorlage
   mit denen der installierten Konfiguration und **meldet die fehlenden
   namentlich, mit der kopierbaren Zeile daneben**. Reparieren wäre die
   schlechtere Antwort — der Installer kennt die Werte dieses Projekts nicht,
   und `TEAM_KIT_PFAD` etwa ist Maschinensache.
   Für einen Wert, der **ohne** Inhalt hart abbricht (`TEAM_MELDUNG_TOOL`), ist
   ein roter Befund angemessen, nicht nur ein gelber Hinweis: Er ist nach dem
   Update nicht *unvollständig*, sondern *kaputt*.
2. **Ein Fall der Gattung**, damit der nächste neue Wert nicht wieder auf ein
   zufällig passendes Nachbarrätsel angewiesen ist: Jeder `$TEAM_*`, den ein
   Entrypoint oder `lib.psm1`/`lib.sh` **liest** und der keinen eigenen
   Rückfall hat, steht in der Vorlagen-Konfiguration — und die
   Schlüsselmengen beider Bahnen sind deckungsgleich (`BL-126` sichert bisher
   nur, dass **beide Dateien geschrieben** werden, nicht, dass sie **dasselbe
   setzen**).
3. Die kopierbaren Zeilen in `Python-Abgleich` um `TEAM_MELDUNG_TOOL`
   ergänzen.

## Was ich schon versucht habe

Lokal repariert, indem die vier Zeilen aus der Vorlage von Hand nachgetragen
und für diese Maschine gefüllt wurden (`TEAM_KIT_PFAD` bewusst **relativ**, weil
Kit und Projekt hier als Geschwister liegen und ein absoluter Pfad einen
Benutzernamen in eine committete Datei trüge). Danach: alle fünf Verben des
Rückkanals laufen, `kit-pfad` findet das Kit über `--kit`, die Suite ist grün.

Der lokale Fix hat **keine** Verfallszeit im Sinne von `BL-42`/`BL-58` — genau
weil `--update` die Datei nicht anfasst. Er behebt aber nur die vier bekannten
Werte; der **nächste** neu eingeführte Wert erzeugt denselben Fall wieder.

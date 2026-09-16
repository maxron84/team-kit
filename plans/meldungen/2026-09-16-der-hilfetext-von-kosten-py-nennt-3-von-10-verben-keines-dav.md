# Der Hilfetext von kosten.py nennt 3 von 10 Verben - keines davon ist ein Abschluss-Verb

- **Bezug**: BL-44
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst
  plus Electron-Oberfläche, rund 1000 Tests, 23 gebaute Kaskaden, Ledger mit
  79 Zeilen über acht Wochen.

## Was passiert ist

`kosten.py` ohne Argumente aufgerufen antwortet:

```
Nutzung: kosten.py summe [--split] DIR... | ledger [PFAD] | ledger-pruefen [--pfad P] [--kaskade N]
```

**Das sind drei Verben. Das Werkzeug kennt zehn.** Ausgezählt am Dispatch:

| genannt | nicht genannt |
|---|---|
| `summe` | `turns` |
| `ledger` | `sitzung-messen` |
| `ledger-pruefen` | `architekt-schaetzung` |
| | `architekt-abschluss` |
| | `akteur-abschluss` |
| | `rollen-abschluss` |
| | `ralph-abschluss` |

**Die Auswahl ist ausgerechnet die ungünstigste:** Die drei genannten sind
Abfragen, die sieben verschwiegenen enthalten **jedes einzelne buchende Verb**
— also genau das, was ein Closeout braucht und was ohne Buchung still
unterbleibt.

Die einzige andere Quelle für diese Verben sind die Rollen-Briefings. Wer ohne
geladenes Briefing arbeitet — ein Mensch am Terminal, eine Instanz, die das
Briefing nicht gelesen hat —, findet den Kostenabschluss nicht und hält ihn für
nicht vorhanden.

## Wo es steckt

- `geteilt/tools/kosten.py`:2073 — die Nutzungszeile im `_main`, von Hand
  geschrieben.
- Dieselbe Bauform ein zweites Mal in derselben Datei: `geteilt/tools/kosten.py`:2301,
  die Nutzungszeile für `sitzung-messen` selbst.

## Warum das jede Installation trifft

**Es ist kein Einzelfall mehr, sondern ein Muster — und das ist der Grund für
diese Meldung.** Dieselbe Bauform war schon einmal im Feld: `kit-melden` kannte
sein eigenes Verb `ablegen` im Hilfetext nicht (gemeldet am 2026-09-03). Zwei
Werkzeuge, derselbe Hergang: **Ein Verb wird ergänzt, die Nutzungszeile
nicht.**

Der Unterschied zwischen beiden ist zugleich der Fix: `kit_meldung.py` benutzt
`argparse` mit Unterbefehlen und **kann** seinen Hilfetext gar nicht mehr
veralten lassen — er wird aus der Registrierung erzeugt:

```
kit_meldung.py: {neu,pruefen,ablegen,senden,issue-link,kit-pfad}
```

`kosten.py` dagegen verzweigt über eine Kette `if befehl == "…"` und schreibt
seine Nutzungszeile daneben als Zeichenkette. **Damit ist die Zeile keine
Auskunft über das Werkzeug, sondern eine Behauptung darüber** — und sie war
schon falsch, als das vierte Verb dazukam.

**Warum das mehr als Kosmetik ist:** Die Bauform *„das buchende Verb ist nicht
auffindbar"* hat in diesem Projekt schon einmal fast **140,58 USD** aus dem
Ledger fallen lassen (der Fall, aus dem `BL-165` entstanden ist). Ein Hilfetext,
der die Abschluss-Verben verschweigt, arbeitet derselben Lücke zu.

## Was vorgeschlagen wird

**Die Nutzungszeile aus der Verb-Liste erzeugen, statt sie danebenzuschreiben.**
Zwei Wege, je nach gewünschtem Umbauumfang:

1. **Klein und sofort:** Eine Konstante `VERBEN = (...)` am Kopf des Moduls, die
   Nutzungszeile setzt sich daraus zusammen, und der Dispatch prüft gegen
   dieselbe Liste. Dann ist ein neues Verb ohne Eintrag in der Liste schlicht
   unerreichbar — der Fehler wird laut statt still.
2. **Gründlich:** `argparse` mit Unterbefehlen, wie `kit_meldung.py` es schon
   macht. Dann entfällt die Frage dauerhaft, und `--help` je Verb kommt gratis
   dazu.

**Dazu ein Regressionstest in der Gattungsform**, sonst hält der Fix nur bis
zum nächsten Verb: Der Test liest die Verben aus dem Dispatch und verlangt,
dass **jedes** in der Nutzungszeile vorkommt. Ein Test, der die heutigen zehn
Namen aufzählt, ist genau der Stellvertreter, der beim elften wieder grün
bleibt.

## Was ich schon versucht habe

Lokal nichts — der Fund sitzt in `geteilt/tools/`, ein Patch hätte sein
Verfallsdatum beim nächsten `--update` (`BL-42`/`BL-58`).

**Die bash-Bahn ist mitgeprüft, soweit sie hier prüfbar ist:** Dieses Projekt
fährt ausschließlich die pwsh-Bahn, `kosten.py` liegt aber in `geteilt/` und
ist für beide Bahnen dieselbe Datei — die Nutzungszeile trifft damit beide
Bahnen unverändert. Ein bahnabhängiger Unterschied ist an dieser Stelle
konstruktiv ausgeschlossen.

# Die Fixphase Frank-Axel gibt es nur als Innenteil der Vollautomatik — kein eigener Einstieg

- **Art**: Fehlende Bedienbarkeit (UX)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkuerzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, vierte
  gebaute Kaskade

## Was passiert ist

Am 2026-08-27 wurden acht Red-Team-Funde ausserhalb eines Vollautomatik-Laufs
abgearbeitet. Das kostete **17 Handstarts** von `.\frank.cmd` — jeder einzelne
vom Menschen getippt, jeder mit Wartezeit davor und Ergebnispruefung danach:

| Fund | Aufrufe | Ausgang |
|---|---|---|
| HM-16 | 1 | gefixt |
| HM-17 | 3 | v1/v2 Fehlversuch, v3 gefixt |
| HM-13 | 1 | gefixt |
| HM-19 | 2 | v1 Fehlversuch, v2 gefixt |
| HM-10 | 1 | gefixt |
| HM-14 | 1 | gefixt |
| HM-15 | 4 | v1/v3 Fehlversuch, v2 abgebrochen, dann gefixt |
| HM-18 | 3 | v1/v2 Fehlversuch, v3 gefixt |

Die Mechanik, die genau das automatisiert, **existiert bereits** — als Phase 4
in `pwsh/entry/vollautomatik.ps1`: Rundenzaehler (`TEAM_MAX_RUNDEN`),
Axel-Eskalation nur wenn ein Fall auf ihn wartet, Rueckkehr zu Frank ueber den
Status `Fix-Plan liegt vor`, Auslauf-Bremse (`TEAM_FIX_MAX_STAGNATION`),
Budget-Pruefung mit Kulanzband, Abbruch-Bericht. Sie ist aber nur erreichbar,
indem man den **ganzen** Lauf startet — also Phase 1 (Ralph) und die
Red-Team-Phasen gleich mit.

Am deutlichsten wird die Luecke im Abbruch-Bericht des Kits selbst
(`vollautomatik.ps1`, `Abbruch-Bericht`). Er raet woertlich:

```
Fixphase fortsetzen:  .\frank.cmd   (ein Fund je Aufruf)
```

Das Werkzeug empfiehlt dem Menschen die Handkurbel — zwanzig Zeilen unterhalb
der Schleife, die dieselbe Arbeit selbstaendig faehrt.

## Wo es steckt

- `pwsh/entry/vollautomatik.ps1` (Phase 4, Fix-Runden) und das bash-Gegenstueck
  — die Schleife ist dort **eingebettet**, nicht aufrufbar.
- `pwsh/entry/frank.ps1` / `axel.ps1`: bewusst „ein Fund je Aufruf", Exit 0 =
  gefixt, 3 = nichts zu tun, 1 = Fehlversuch, 42 = Session-Limit. Diese
  Exit-Codes sind bereits genau der Vertrag, den eine Schleife braucht — es
  fehlt nur der Aufrufer.
- `Abbruch-Bericht` in derselben Datei: nennt die Handkurbel als Weiterweg.

**Vorschlag:** Die Fix-Runden aus Phase 4 in eine eigene Funktion der
Bibliothek ziehen (`team_fixphase`) und zwei Aufrufer bedienen — die
Vollautomatik wie bisher, und einen eigenen Einstieg, etwa
`.\frank.cmd --auto` oder `.\fixphase.cmd`. Kein neues Verhalten, sondern
derselbe Code mit einer zweiten Tuer. Der Abbruch-Bericht nennt dann den neuen
Einstieg statt der Handkurbel.

Zwei Dinge sollte der eigene Einstieg von der Vollautomatik erben, weil sie
genau die Schaeden verhindern, die die Handarbeit teuer machen: die
**Auslauf-Bremse** (sonst dreht die Schleife an einem unloesbaren Fund leer)
und die **Budget-Pruefung je Runde**.

## Warum das jede Installation trifft

Der Fall „Sweep war gestern, heute nur noch die Funde abarbeiten" ist der
Normalfall jeder Installation, sobald ein Projekt aus der ersten Kaskade heraus
ist. Ein Fund kommt auch dann herein, wenn gerade kein Lauf ansteht: aus einer
Handpruefung, aus der Abnahme, aus dem Betrieb. Fuer diesen Fall bietet das Kit
heute nur die Einzelkurbel — und der Mensch bezahlt die Wiederanlauf-Reibung
mit Aufmerksamkeit, also mit genau der Ressource, die das Kit schonen will.

Die Vollautomatik als Ersatz zu starten ist kein Weiterweg: Sie beginnt bei
Ralph und wuerde nach einem abgeschlossenen Stufenbogen erst bauen und
sweepen, bevor sie die offenen Funde erreicht.

## Was ich schon versucht habe

Nichts lokal gebaut — die Schleife gehoert ins Kit, ein Eingriff in `team/`
haette ein Verfallsdatum beim naechsten `--update`. In der Praxis lief die
Fixphase deshalb als Handarbeit: `.\frank.cmd`, Ausgabe lesen, bei Exit != 0
erneut, und bei Bedarf `.\axel.cmd` dazwischen — also die Schleife aus Phase 4,
von Hand nachgespielt.

**Wichtiger Zusammenhang zu den Fehlversuchen oben:** Sie haben ihre eigene,
getrennt gemeldete Ursache (`BL-201`, vierter Ausgang: Frank startet den
Smoke-Test als Hintergrund-Task und wartet headless auf eine Benachrichtigung,
die nie kommt). Der Zusammenhang ist trotzdem wichtig, weil er die Kosten
erklaert: Eine Automatik haette die neun betroffenen Aufrufe **selbstaendig**
wiederholt statt den Menschen neun Mal an die Tastatur zu holen — sie behebt
die Ursache nicht, aber sie nimmt ihr die Reibung.

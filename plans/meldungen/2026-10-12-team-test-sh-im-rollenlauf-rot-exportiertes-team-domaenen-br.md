# team-test.sh im Rollenlauf rot: exportiertes TEAM_DOMAENEN bricht die Kit-Tests

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-12-team-test-sh-im-rollenlauf-rot-exportiertes-team-domaenen-br.md
      ./kit-melden.sh ablegen  2026-10-12-team-test-sh-im-rollenlauf-rot-exportiertes-team-domaenen-br.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-12-team-test-sh-im-rollenlauf-rot-exportiertes-team-domaenen-br.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-2
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; pwsh nicht installiert; erste Kaskade

## Was passiert ist

Der Plan der ersten Kaskade verlangte in Stufe 1: „`./team-test.sh` grün". Ralph
fuhr den Befehl in seinem Rollenlauf und meldete 42 Fehlschläge (von 1221) als
„schon vor dieser Stufe rot", geprüft per `git stash` gegen den Stand davor. Er
hat `team/` richtigerweise nicht angefasst.

Außerhalb des Loops ist dieselbe Suite auf demselben Stand grün (vor und nach
dem Lauf gemessen, Exit 0).

Die Ursache ist isoliert: `team.config.sh` exportiert `TEAM_DOMAENEN` („die
Python-Werkzeuge lesen sie aus der Umgebung"). Im Rollenlauf steht die
Variable deshalb in der Umgebung jeder Shell, die die Rolle öffnet. Mehrere
Kit-Tests buchen in ihren Fixtures auf die Domäne `team`, und `kosten.py`
weist das dann ab:

```
$ TEAM_DOMAENEN=produkt python3 -m pytest -q team/tests/test_stufe43_architekt_abschluss.py
E       AssertionError: Fehler: domaene muss eine von produkt sein, nicht 'team' (konfigurierbar ueber TEAM_DOMAENEN in team.config.sh)
8 failed, 3 passed

$ python3 -m pytest -q team/tests/test_stufe43_architekt_abschluss.py
11 passed

$ TEAM_DOMAENEN=produkt python3 -m pytest -q team/tests/test_stufe54_rollen_abschluss.py
5 failed, 2 passed
```

`TEAM_PLAN_ORDNER=plans/`, `TEAM_PREISE=`, `TEAM_LOCK_HELD=1` und `CLAUDECODE=1`
allein ändern an diesen Tests nichts.

Die ganze Suite mit den drei Werten, die `team.config.sh` exportiert
(`TEAM_PLAN_ORDNER=plans/ TEAM_DOMAENEN=produkt TEAM_PREISE= ./team-test.sh`),
ergibt 39 Fehlschläge in 10 Dateien, alle rund um Ledger-Buchungen:
`test_stufe43_architekt_abschluss.py` (8), `test_bl5_rollen_abschluss_bestand.py` (7),
`test_stufe54_rollen_abschluss.py` (5), `test_hm38_…`, `test_hm39_…`, `test_hm47_…` (je 4),
`test_hm41_…`, `test_hm48_…`, `test_bl125_…` (je 2), `test_hm44_…` (1). Die drei
übrigen der 42 aus dem Rollenlauf ließen sich außerhalb des Loops nicht
nachstellen.

## Wo es steckt

In den Kit-Tests unter `team/tests/`, die `kosten.py`-Buchungen mit der Domäne
`team` fahren, ohne `TEAM_DOMAENEN` für ihre Unterprozesse festzulegen (etwa
`test_stufe43_architekt_abschluss.py`, `test_stufe54_rollen_abschluss.py`).
Auslöser ist das `export TEAM_DOMAENEN` in `team.config.sh`, das für die
Werkzeuge gewollt ist.

## Warum das jede Installation trifft

Jedes Projekt mit einer eigenen Domänenliste ohne `team` — der in
`team.config.sh` empfohlene Normalfall („KEINE eigene Domäne für die Arbeit am
T.E.A.M. selbst") — bekommt in jedem Rollenlauf eine rote Kit-Suite. Eine
bauende Rolle, die `./team-test.sh` fährt (etwa weil der Plan der ersten
Kaskade eine Wurzel-Konfiguration von pytest ausschließen will), sieht
dutzende falsche Fehlschläge. Im besten Fall meldet sie sie als vorbestehend,
wie hier. Im schlechtesten repariert sie `team/` oder hält ihre eigene Stufe
für kaputt.

## Was ich schon versucht habe

Nichts lokal gefixt, `team/` ist unverändert. Zwei naheliegende Wege für das
Kit: Die Kit-Tests setzen `TEAM_DOMAENEN` für ihre Unterprozesse selbst (etwa
in `team/tests/conftest.py`); oder `team-test.sh` entfernt die von
`team.config.sh` exportierten Projektwerte, bevor es pytest startet. Der erste
Weg schützt auch einen direkten Aufruf von `python3 -m pytest team/tests`.

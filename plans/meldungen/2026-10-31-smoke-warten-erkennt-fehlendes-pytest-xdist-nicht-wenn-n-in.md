# smoke_warten erkennt fehlendes pytest-xdist nicht, wenn -n in addopts der Projektkonfiguration steht

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-31-smoke-warten-erkennt-fehlendes-pytest-xdist-nicht-wenn-n-in.md
      .\kit-melden.cmd ablegen  2026-10-31-smoke-warten-erkennt-fehlendes-pytest-xdist-nicht-wenn-n-in.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-31-smoke-warten-erkennt-fehlendes-pytest-xdist-nicht-wenn-n-in.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; achte Kaskade, rund 500 Tests. Das Produkt steuert ein lokales Sprachmodell über einen lokalen Server

## Was passiert ist

Eine Kaskade hat die Suite parallel gestellt: `addopts = "-n auto --dist loadgroup"` in
`pyproject.toml`, dazu pytest-xdist. Der Smoke-Test bleibt `python -m pytest -q tests`, also
ohne `-n` im Befehl.

Harry fand im Sweep: Fehlt pytest-xdist im Interpreter (frische Maschine, neues venv), bricht
pytest schon am Parser ab (`unrecognized arguments: -n …`, Exit 4, kein Test läuft). Die Prüfung
aus `Kit-BL-320` sieht das nicht: Sie sucht `-n`/`--dist` nur in den Wörtern des Befehls. Der
Befund an der Umgebung bleibt aus, und die Selbstprüfung des vierten Ausgangs meldet wieder
„rot“ und schickt in den Produktivcode. Das ist der Feldfall, gegen den `Kit-BL-320` gebaut ist,
nur kommt das `-n` jetzt aus der Konfiguration statt aus dem Befehl.

## Wo es steckt

`team/tools/smoke_warten.py`, `umgebung(befehl)`: Die Optionen kommen nur aus `_teile(befehl)`;
ohne Treffer gibt die Funktion `0` zurück, die Probe auf xdist läuft nie. Aufgerufen über
`team_smoke_umgebung_befund` (`team/lib.sh`) und die pwsh-Entsprechung, jeweils mit dem Befehl
allein; das Arbeitsverzeichnis ist dort die Projektwurzel.

## Warum das jede Installation trifft

`smoke_warten.py` ist eine geteilte Kit-Datei beider Bahnen. Jedes Projekt, das xdist über die
Konfiguration einschaltet statt im Befehl, hat die Lücke — und das ist der übliche Weg, weil der
dokumentierte Befehl dann kurz bleibt. Den lokalen Fix nimmt das nächste `--update` wieder
heraus (nach `Kit-BL-270` gesichert und gemeldet, danach aber nicht mehr aktiv).

## Was ich schon versucht habe

Lokal gefixt (Frank, ein Versuch). Startet der Befehl pytest und trägt er selbst kein `-n`,
liest `umgebung(befehl, wurzel=None)` die `addopts` aus der Konfiguration in `wurzel` (Default:
Arbeitsverzeichnis): `pyproject.toml` (`[tool.pytest.ini_options]`, Text oder Liste, über
`tomllib`), `pytest.ini` und `tox.ini` (`[pytest]`), `setup.cfg` (`[tool:pytest]`). Lesefehler
zählen als „keine Optionen“. Rund 30 Zeilen, keine neue Abhängigkeit. Drei Reproducer-Tests mit
einer Interpreter-Attrappe ohne xdist: `addopts` in `pyproject.toml` bzw. `pytest.ini` ergibt
den Befund, `addopts` ohne `-n` keinen.

Offen, ohne Anspruch:

- `tomllib` gibt es erst ab Python 3.11; davor fällt `pyproject.toml` still weg.
- pytest liest nur **eine** Konfigurationsdatei und dazu `PYTEST_ADDOPTS`; der Fix liest alle
  vier Dateien und keine Umgebungsvariable. Steht `-o addopts=` im Befehl, meldet er nach dem
  Code einen Befund, obwohl pytest ohne `-n` liefe.

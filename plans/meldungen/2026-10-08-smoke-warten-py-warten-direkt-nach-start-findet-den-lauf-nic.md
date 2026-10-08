# smoke_warten.py warten direkt nach start findet den Lauf nicht - die Logdatei legt erst das abgekoppelte Kind an

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-08-smoke-warten-py-warten-direkt-nach-start-findet-den-lauf-nic.md
      .\kit-melden.cmd ablegen  2026-10-08-smoke-warten-py-warten-direkt-nach-start-findet-den-lauf-nic.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-08-smoke-warten-py-warten-direkt-nach-start-findet-den-lauf-nic.md   # sonst: Pull Request

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
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python-Dienst mit Electron-Oberfläche,
  Projekt-Python in einem venv. Gefunden beim Kontrolllauf nach dem Update vom 2026-10-08.

## Was passiert ist

`test_bl232_verifikation_waechst_mit.py::test_warten_meldet_laeuft_noch_dann_den_exitcode` ist
mit dem venv-Interpreter reproduzierbar rot (2 von 2) und mit dem System-Python grün:

```
>       assert zwischen.returncode == 75, zwischen.stderr
E       AssertionError: Fehler: kein Smoke-Lauf gefunden — zuerst `smoke_warten.py start`.
E       assert 2 == 75
```

`start` endete mit 0, das sofort folgende `warten` mit 2 („Bedienfehler").

## Wo es steckt

`geteilt/tools/smoke_warten.py`: `start()` startet `sys.executable smoke_warten.py _lauf …`
abgekoppelt und kehrt sofort zurück. Die Logdatei `smoke-<id>.log` legt erst `_lauf()` im Kind
an (`open(log, "w")`). `warten()` ohne Kennung sucht den jüngsten Lauf über
`.team-logs/smoke-*.log` und endet mit 2, solange die Datei fehlt. Mit Kennung meldet es „kein
Lauf mit der Kennung" und endet ebenfalls mit 2.

Unter Windows ist das `python.exe` eines venv ein Starter, der den Basis-Interpreter als weiteren
Prozess startet. Das Kind braucht deshalb spürbar länger, und der Wettlauf geht zuverlässig
verloren. Unter Last, etwa neben einem laufenden Testlauf, kann er auch mit dem System-Python
verloren gehen.

## Warum das jede Installation trifft

Briefings, Laufzeit-Bausteine und Regeldatei nennen `start`, dann sofort `warten`, als den
Zwei-Schritt-Weg (`Kit-BL-273`/`Kit-BL-281`). Endet `warten` mit 2 und der Aufforderung
„zuerst `start`", liegt für eine Rolle ein zweites `start` nahe. Dann laufen zwei Suiten
nebeneinander, und es kommt genau zu der Kollision, vor der `Kit-BL-207` warnt.

## Was ich schon versucht habe

Am Kit nichts geändert. Vorschlag: `start()` legt die Logdatei (leer) selbst an, bevor es das Kind
startet. Das Kind schreibt sie dann nur noch voll. Alternativ toleriert `warten()` mit bekannter
Kennung eine noch fehlende Datei für einige Sekunden. Die Projekt-Warteschleife
(`until grep … "$LOG"`) hat das Problem nicht, weil sie auf eine fehlende Datei einfach weiter
wartet. Das Projekt bleibt deshalb vorerst bei seinem eigenen Zwei-Schritt-Verfahren, und seine
Regeldatei verweist auf diese Meldung.

# test_bl326 haengt unter Windows auf der bash-Bahn - taskkill /T erreicht den MSYS-Enkel der Attrappe nicht

- **Bezug**: BL-326 (gebaut 2026-10-18, `a8b8605`), BL-127
- **Art**: Fehler (Testharnisch, nicht Produktcode)
- **Kit-Version**: 2.13.1 (Quellstand `530e942`, Code wie `84a7e81`)
- **Bahn**: die `[bash]`-Fälle der Suite unter Git Bash; gefunden mit `pwsh -File pwsh/kit-test.ps1`
- **Plattform**: win32
- **Feldkürzel**: — (kein Feldprojekt)
- **Lage des Projekts**: kein Projekt — `kit-test.ps1` im Kit-Repo (eigener Worktree, bereinigte Umgebung ohne `CLAUDE*` und `TEAM_*`) auf der Windows-11-Maschine mit Git Bash und pwsh 7.6 nebeneinander. Das ist die pwsh-Prüfung der Bauten vom 2026-10-18.

## Was passiert ist

`kit-test.ps1` endet nach 67 Minuten mit „Selbstverifikation NICHT grün“ (Exit 1). Es gibt fünf
rote Zeilen: Schritt 2 (BL-127), Schritt 4 (Suite), Schritt 6 dreimal (BL-58, BL-194, BL-307).
Alle fünf kommen aus demselben Suite-Ergebnis:

```
FAILED team/tests/test_bl326_abgebrochener_rollenaufruf.py::test_ein_abgebrochener_aufruf_hinterlaesst_seinen_stub[bash]
FAILED team/tests/test_bl326_abgebrochener_rollenaufruf.py::test_auch_der_api_fallback_steht_vorher_als_stub_im_log[bash]
2 failed, 1623 passed, 504 skipped
```

Beide Male `subprocess.TimeoutExpired` in `_abschiessen()`: Nach `taskkill /F /T` wartet
`proc.communicate(timeout=30)` 30 s lang auf geschlossene Pipes. Alle übrigen Schritte sind grün:
Platzhalter, README-Zahlen, Update-Pfad, Abwahl einer Bahn, Trockenlauf der Rollen.

## Wo es steckt

`geteilt/tests/test_bl326_abgebrochener_rollenaufruf.py`: der Windows-Zweig von `_abschiessen()`
zusammen mit der bash-Attrappe aus `_attrappe()`, die nach der Startmarke `sleep 60` ruft.

Nachgestellt ohne Kit: `bash.exe -c '<attrappe>'` mit `CREATE_NEW_PROCESS_GROUP` und Pipes wie in
`_starte()`, danach `taskkill /F /T` wie in `_abschiessen()`.

- Windows sieht den Baum `bash.exe` (Starter von Git) → `bash.exe` (MSYS) → `sh.exe` (Attrappe).
  `taskkill` beendet alle drei.
- Das `sleep.exe` der Attrappe hängt nicht in diesem Baum. Seine Eltern-PID zeigt auf einen
  Prozess, den es nicht mehr gibt (Fork-Nachbildung von MSYS). Es überlebt `taskkill /T` und hält
  die geerbten Pipes offen, bis es nach 60 s von selbst endet. `communicate()` läuft vorher in den
  Timeout.

Unter Linux greift `os.killpg` die ganze Sitzung, deshalb ist der Fall auf der Bau-Maschine grün.

## Gegenprobe

In einer Kopie des Wegwerf-Projekts, das `kit-test.ps1` zur Ansicht liegen lässt, ist nur
`_abschiessen()` geändert: Unter Windows wartet es nach `taskkill` auf das Prozessende
(`proc.wait(timeout=30)`) und schließt danach die Pipes, statt auf ihr Ende zu warten.

| `_abschiessen()` | `test_bl326_abgebrochener_rollenaufruf.py` |
|---|---|
| wie geliefert | 2 failed, 27 passed (nur die zwei `[bash]`-Fälle rot) |
| wartet auf das Prozessende | 29 passed |

Damit ist belegt: Der Produktcode von BL-326 arbeitet unter Windows auf beiden Bahnen richtig
(Stub vor dem Aufruf, Stub des API-Fallbacks mit eigener Kennung). Rot ist nur das Aufräumen des
Tests. Die `[pwsh]`-Fälle von BL-326 waren schon unverändert grün, ebenso alle übrigen Fälle der
Datei (Wiederanlauf mit Exit 42, Prüfung vor Phase 1, eine Fundstelle für den CLI-Aufruf).

## Nebenbefund: Schritt 2 meldet ein rotes Ergebnis als „nicht gefahren“ (BL-127)

`kit-test.ps1` Schritt 2: „der Installer hat seine Regressionstests wirklich gefahren (BL-127) —
erwartet 'True', ist 'False'“. Gefahren hat er sie. Das Installer-Log zeigt „2 failed, 1623
passed …“ und „Regressionstests nicht vollstaendig gruen“. Die Prüfung sucht nur die Zeile
„Regressionstests gruen“ und liest damit „rot“ als „übersprungen“.

`kit-test.sh` (Schritt 2) prüft dieselbe Zeile und ist schärfer: „Der Installer hat seine
Regressionstests NICHT gefahren“, danach `exit 1`. Ein einziger roter Test beendet dort den ganzen
Selbsttest in Schritt 2, mit einer Meldung, die auf einen übersprungenen Selbsttest zeigt. Wer ihr
folgt, sucht an der falschen Stelle. Hergeleitet aus dem Quelltext, auf dieser Maschine nicht
gefahren.

## Vorschlag

1. `_abschiessen()`: Unter Windows auf das Prozessende warten und die Pipes schließen, wie in der
   Gegenprobe. Alternative, ungeprüft: Die Attrappe wartet ohne MSYS-Kindprozess, etwa mit
   `exec sleep 60`.
2. Schritt 2 in beiden Selbsttests: „gefahren“ und „grün“ getrennt prüfen, etwa an der
   Zusammenfassungszeile von pytest. Rot bleibt rot, heißt aber nicht mehr „nicht gefahren“.
3. Zu erwägen: ein Hinweis im Harnisch für künftige Tests, die unter Windows einen Prozessbaum
   mit Git Bash beenden. `taskkill /T` erreicht MSYS-Enkel nicht.

## Was ich schon versucht habe

- Die Ursache ist am Nachbau belegt (Prozessbaum vor und nach `taskkill`).
- Die Gegenprobe lief in einer Kopie (Tabelle oben). Am Kit ist nichts geändert, gebaut wird auf
  der Linux-Maschine.

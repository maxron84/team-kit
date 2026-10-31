# AMD Radeon Software bremst unter Windows jeden Python-Start, die Suite läuft bis zum Zehnfachen

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-31-amd-radeon-software-bremst-unter-windows-jeden-python-start.md
      .\kit-melden.cmd ablegen  2026-10-31-amd-radeon-software-bremst-unter-windows-jeden-python-start.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-31-amd-radeon-software-bremst-unter-windows-jeden-python-start.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Lücke in der Doku (Einrichtung Windows nativ, `TEAM.md` „Wenn etwas schiefgeht“); Vorschlag für eine Warnung in `team-status`
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; rund 500 Tests, viele davon mit eigenen Python-Prozessen. AMD-Prozessor mit eingebauter Grafik (AMD-Treiber samt AMD Software), das Bild macht eine NVIDIA-Karte

## Was passiert ist

Über mehrere Tage starteten Python-Prozesse zeitweise langsam: 0,35–1,5 s je Start statt
1–4 ms. Die Suite brauchte dadurch 55 statt 5½ Minuten; Rollen rissen Fristen, und die Meldung
„Wächst die Suite über die Frist, verliert jede Rolle zehn Minuten“ (2026-10-29) nannte nur „die
Ursache lag an der Maschine“. Zwei frühere Deutungen waren falsch: Cloudschutz von Defender und
„nur im IDE-Terminal schnell“ — kurze schnelle Phasen kamen überall vor.

Die Ursache ist AMD Software (`RadeonSoftware.exe`). Sie führt `python.exe` in ihrer
Spieleliste (`%LOCALAPPDATA%\AMD\CN\gmdb.blb`) als „Python 3.12 (64-bit)“, Art KI-Anwendung,
und verbucht jeden Start als Spielstart. Belege:

1. Eine Defender-Aufzeichnung: Defender prüfte `python.exe` 51 ms lang. `RadeonSoftware.exe`
   öffnete `gmdb.blb` 136-mal, und zwar genau während der Python-Starts.
2. Eine Gegenprobe in derselben Sitzung: Mit laufender Radeon Software dauerten 33 Starts 33 s
   (je 0,7–1,5 s), beendet 1 s (je 1–4 ms). Nach einem Neustart der Software war es erst schnell,
   später wieder langsam.

## Wo es steckt

Nicht im Code des Kits, sondern auf der Maschine. Die Kit-Doku zu Windows nativ und
`TEAM.md` („Wenn etwas schiefgeht“) erwähnen es aber nicht, und die Symptome, die das Kit
meldet, zeigen auf die Tests des Projekts statt auf die Maschine: Frist des Smoke-Tests, vierter
Ausgang, Rollen, die auf die Suite warten.

## Warum das jede Installation trifft

Betroffen ist jede Windows-Maschine mit AMD-Grafiktreiber und AMD Software — auch dann, wenn nur
der Prozessor eine AMD-Grafik eingebaut hat und eine andere Karte das Bild macht, wie hier. Für
lokale Modelle ist so eine Maschine typisch. Das Kit startet für jedes Werkzeug
(`team/tools/*.py`) einen Python-Prozess, und viele Projekt-Suiten tun das je Test. Eine Sekunde
je Start vervielfacht sich dann.

## Was ich schon versucht habe

- Den Autostart abgeschaltet: in der Aufgabenplanung die Aufgaben `StartCN` und `StartDVR`
  deaktiviert. Nach dem Neustart läuft die Software nicht mehr.
- Wenn sie doch läuft (nach einem AMD-Update oder weil jemand AMD Software geöffnet hat):
  `Stop-Process -Name RadeonSoftware, cncmd`.
- Nicht ausprobiert: AMD Software als „Nur Treiber“ neu installieren. Grafik- und Chipsatztreiber
  blieben dabei erhalten.

Vorschlag, ohne Anspruch:

- In die Einrichtung für Windows nativ und in `TEAM.md` („Wenn etwas schiefgeht“) ein Absatz:
  Symptom (Python-Start über eine halbe Sekunde, Suite ein Vielfaches langsamer), Prüfung
  (`Get-Process RadeonSoftware`), Abhilfe (beenden, Autostart aus oder nur den Treiber installieren).
- `team-status` (pwsh-Bahn) warnt, wenn `RadeonSoftware` läuft, und nennt die Abhilfe.

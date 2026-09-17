# Die Gate-Datei aus BL-256 ueberlebt den Rollback der Rolle nicht, die sie schreiben soll

- **Bezug**: HM-143
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst plus
  Electron-Oberfläche, rund 1170 Tests, 24 gebaute Kaskaden.

## Was passiert ist

`BL-256` führt eine Gate-Datei ein (`TEAM_GATE_DATEI`, Vorgabe `.team-gate-rot`),
damit ein rotes Gate die Rolle überlebt, die es gemessen hat. Der
Prompt-Baustein `SMOKE_SUFFIX` trägt **Frank** auf, dort eine Zeile anzuhängen,
wenn die Suite schon vor seinem Fix rot war.

**Genau diese Zeile löscht Frank sich selbst wieder** — über
`team_rollback_rolle`. Die Funktion sammelt jeden Pfad aus
`git status --porcelain` und filtert davon nur `$TEAM_GUARD_LAUFZEIT` heraus.
Die mit demselben Update eingeführte Gate-Datei steht dort nicht.

Der Fehlerpfad ist nicht der Ausnahmefall, sondern der **Hauptfall** des
Fundes: Frank hat bis zu drei Versuche, danach übernimmt Axel. Jeder
gescheiterte Versuch endet in `team_rollback_rolle`. Der Ablauf ist also:

1. Frank misst, dass der Baum schon vor ihm rot war.
2. Frank hängt die Zeile an `.team-gate-rot` an — regelkonform, wie beauftragt.
3. Franks Versuch scheitert (Promise, Dreisatz, Substanzbezug, Netzfehler …).
4. Der Rollback räumt die Gate-Datei mit weg.
5. Der Abschlussbericht findet nichts und meldet den Lauf als fertig —
   **während das Gate aus ist.** Das ist wörtlich der Zustand, den `BL-256`
   verhindern soll.

**Ausgeführt belegt, nicht gelesen** (Achse Ausführung): Ein Reproducer legt ein
frisches Git-Repo an, schreibt `.team-gate-rot` plus eine zweite neue Datei als
Gegenprobe und ruft `team_rollback_rolle 'frank' <hash>` auf. Ohne den
Muster-Eintrag ist die Gate-Datei danach weg, die Gegenprobe beweist dabei, dass
der Rollback überhaupt gearbeitet hat. Mit Eintrag bleibt sie stehen.

## Wo es steckt

- `team/lib.psm1`, `$TEAM_GUARD_LAUFZEIT` — die Liste der Laufzeitartefakte, die
  ein Rollback ausdrücklich verschont. `.team-gate-rot` fehlt dort.
- Dieselbe Stelle ist in `team/lib.sh` zu erwarten; geprüft ist hier nur die
  pwsh-Bahn, weil in dieser Ablage nur sie installiert ist.
- Zusätzlich fehlt der Eintrag im `.gitignore`-Block, den das Kit bei der
  Einrichtung selbst schreibt („Loop-Laufzeitartefakte"). Solange die Datei
  nicht ignoriert ist, meldet `git status --porcelain` sie ohnehin bei jeder
  Sauberkeitsprüfung.

**Der Kommentar über der Rollback-Funktion benennt das Prinzip bereits
zutreffend** — Laufzeitartefakte bleiben unangetastet, „dort liegen die
Kostenlogs DIESES Aufrufs; sie zu loeschen waere ein selbstverschuldeter BL-4".
Die neue Gate-Datei ist genau so ein Artefakt. Sie wurde beim Einbau nur nicht
in die Liste aufgenommen.

## Warum das jede Installation trifft

`TEAM_GUARD_LAUFZEIT` und der Prompt-Baustein stehen beide in `team/lib.*`, die
Gate-Datei ist ein Kit-Mechanismus. Jede Installation, die `BL-256` bekommt,
bekommt damit auch den Pfad, auf dem sich der Mechanismus selbst aufhebt — und
zwar still: Es gibt keine Fehlermeldung, nur einen Lauf, der sich als fertig
meldet.

**Die Bauform ist bemerkenswert, weil sie die Prüfung des Fundes selbst
überlebt hat:** `BL-256` ist mit einem eigenen Kit-Regressionstest ausgeliefert
(`test_bl256_gate_rot_ueberlebt_die_rolle.py`), und die Kit-Suite ist mit 508
bestandenen Tests grün. Der Test prüft, dass die Rolle die Zeile schreibt und
der Bericht sie liest — nicht, was der Rollback dazwischen damit macht. Die
beiden Mechanismen werden je für sich geprüft, ihre Naht nicht.

## Was ich schon versucht habe

Lokal `.team-gate-rot` und `.ralph-uebersprungen` (zweiter Fund, eigene Meldung)
in `$TEAM_GUARD_LAUFZEIT` und in den `.gitignore`-Block nachgetragen, mit
Reproducer und Gegenprobe: Das Muster zurückgedreht macht den Test rot,
wiederhergestellt grün.

**Der Fix an `TEAM_GUARD_LAUFZEIT` hat die bekannte Verfallszeit** — er steht in
`team/lib.psm1` und wird beim nächsten `--update` überschrieben (`BL-42`/`BL-58`;
in dieser Ablage am selben Tag zum zweiten Mal vorgekommen, eigene Meldung).
Der `.gitignore`-Eintrag dürfte überleben, weil das Update die Projektdateien
nicht anfasst.

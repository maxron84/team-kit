# schreibzone.py hält das Beutebuch-Archiv des Kits für eine fremde Datei

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-11-02-schreibzone-py-haelt-das-beutebuch-archiv-des-kits-fuer-eine.md
      .\kit-melden.cmd ablegen  2026-11-02-schreibzone-py-haelt-das-beutebuch-archiv-des-kits-fuer-eine.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-11-02-schreibzone-py-haelt-das-beutebuch-archiv-des-kits-fuer-eine.md   # sonst: Pull Request

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
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; rund 770 Tests

## Was passiert ist

Das Beutebuch war über ein 32K-Fenster gewachsen; der Architekt hat es mit `beutebuch.py
archiviere` rotiert. Danach meldete der Statusbericht am Ende der nächsten Vollautomatik:

```
  Im Plan-Ordner, weder Team-Artefakt noch Bestand (Kit-BL-237):
    · plans/beutebuch-archiv.md
    Read-Only-Rollen duerfen hier schreiben und loeschen. Gehoert es dem Projekt: in TEAM_PLAN_ORDNER_BESTAND eintragen …
```

Die Datei hat das Kit selbst angelegt, nicht das Projekt.

## Wo es steckt

`team/tools/schreibzone.py`: `TEAM_ARTEFAKTE` nennt `backlog-archiv.md`, aber nicht
`beutebuch-archiv.md`. Den Namen legt `team/tools/beutebuch.py` fest (`ARCHIV`, Vorgabe
`<Planordner>/beutebuch-archiv.md`, abweichend über `--archiv-pfad`).

## Warum das jede Installation trifft

Jedes Projekt, das sein Beutebuch archiviert (Doku-Hygiene, Regel 3), bekommt den Hinweis nach jedem
Lauf, und er sagt das Falsche: Die Datei gehört dem Team. Solange sie in keiner der beiden Listen
steht, gilt sie für die Read-Only-Rollen als freie Schreibzone, obwohl dort nur abgeschlossene Funde
liegen.

## Was ich schon versucht habe

- Im Projekt ruhiggestellt: `beutebuch-archiv.md` in `TEAM_PLAN_ORDNER_BESTAND` (beide
  `team.config.*`). Danach schweigt `schreibzone.py pruefen` (Exit 0), und die Rollen lassen die
  Datei laut Prompt in Ruhe. Am Kit nichts geändert.
- Vorschlag, ohne Anspruch: `beutebuch-archiv.md` in `TEAM_ARTEFAKTE` aufnehmen, am besten aus
  demselben Namen wie in `beutebuch.py`, damit beide nicht wieder auseinanderlaufen. Ob das Archiv
  für die Read-Only-Rollen beschreibbar bleibt, entscheidet der Maintainer; neue Funde gehören ans
  Ende des aktiven Beutebuchs (`Kit-BL-254`), nie ins Archiv.

# Der Hilfetext von kit-melden kennt das Verb ablegen nicht - also genau den Weg, den der Owner gehen soll

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-03-der-hilfetext-von-kit-melden-kennt-das-verb-ablegen-nicht-al.md
      .\kit-melden.cmd ablegen  2026-09-03-der-hilfetext-von-kit-melden-kennt-das-verb-ablegen-nicht-al.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-03-der-hilfetext-von-kit-melden-kennt-das-verb-ablegen-nicht-al.md   # sonst: Pull Request

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
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python + Electron, neun
  Kaskaden gelaufen, rund 400 Tests. Der Strippenzieher dieses Feldes ist
  zugleich Owner des Kits — für ihn ist `ablegen` der vorgesehene Weg, nicht
  `senden`.

## Was passiert ist

Beim Abarbeiten des Backlogs sollten zwei fertige Meldungen ins Kit. Die
Projektregel nennt dafür ausdrücklich `kit-melden … ablegen`. Beim Nachsehen im
Werkzeug stand das Verb dort aber nicht:

```
  Aufruf:
    .\kit-melden.cmd neu --titel "…"     Entwurf nach Vorlage anlegen
    .\kit-melden.cmd pruefen             Redaktionspruefung (Exit 4 = Befunde)
    .\kit-melden.cmd senden <datei>      Pull Request — fragt vorher
    .\kit-melden.cmd issue-link <datei>  nur den vorbefuellten Link
    .\kit-melden.cmd kit-pfad            wo liegt das Kit? (Diagnose)
```

Fünf Verben. Das Python-Werkzeug dahinter kennt **sechs** — `ablegen` ist
vorhanden, funktioniert einwandfrei und hat einen ausführlichen, gut
begründeten Docstring. Nur der Kopfkommentar des pwsh-Wrappers, den ein Mensch
zuerst liest, weiß nichts davon.

Erschwerend: Die Ausgabe von `neu` nennt `ablegen` in ihrem Hinweisblock. Wer
also über `neu` einsteigt, findet es; wer die Datei öffnet, um zu sehen, was
das Werkzeug kann, findet es nicht.

## Wo es steckt

Im Kopfkommentar von `kit-melden.ps1` (Abschnitt „Aufruf:"). Der
`WARUM SENDEN EINE EIGENE HANDLUNG IST`-Absatz direkt darunter beschreibt
weiterhin nur die Trennung `neu`/`pruefen` gegen `senden` und erwähnt `ablegen`
ebenfalls nicht — obwohl `ablegen` seine eigenen, strengeren Grenzen hat (kein
Push, keine `BL-`Nummer, Redaktionsprüfung als Vorbedingung).

**Auf der bash-Bahn bitte mitprüfen** (`kit-melden.sh`): Das Feld, das diese
Meldung schreibt, fährt nur die pwsh-Bahn und kann die andere nicht beurteilen.

## Warum das jede Installation trifft

Es ist der Rest einer bereits abgetragenen Aufgabe. `BL-187` hielt fest, dass
der Rückkanal nur einen Weg kennt — den Pull Request — und dass der für den
Owner der falsche ist. Der Eintrag steht im Archiv als abgetragen; nachgezogen
wurden Rollen-Briefing, `bootstrap/TEAM.md` und `bootstrap/CLAUDE.md.vorlage`.
Der Hilfetext des Werkzeugs selbst blieb stehen.

Damit trifft es jede Installation, deren Nutzer das Werkzeug über seine eigene
Hilfe erschließt: Sie finden `senden` und damit den Pull Request — also genau
den Weg, von dem `BL-187` festgestellt hat, dass er hier der falsche ist. Ein
Owner, der einen PR gegen sein eigenes Repo anlegt, reviewt und merged seine
eigene Meldung.

## Was ich schon versucht habe

Nichts gefixt — der Fund sitzt im Kit, und ein lokaler Eingriff hielte nur bis
zum nächsten `--update`. Die beiden fälligen Meldungen sind über `ablegen`
eingegangen, nachdem das Verb im Python-Werkzeug gefunden war; der Weg selbst
funktioniert also tadellos. Es fehlt ausschließlich sein Eintrag im Hilfetext.

**Vorschlag:** Die Verbliste um `ablegen` ergänzen und in einem Halbsatz sagen,
wann man es nimmt — „liegt das Kit lokal daneben (`TEAM_KIT_PFAD`), ist
`ablegen` der Weg; `senden` ist für Melder ohne Kit-Repo". Das ist derselbe
Satz, den die Ausgabe von `neu` schon sagt.

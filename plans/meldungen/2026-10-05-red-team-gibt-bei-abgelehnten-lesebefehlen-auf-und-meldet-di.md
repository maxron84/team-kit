# Red Team gibt bei abgelehnten Lesebefehlen auf und meldet die Stelle trotzdem als geprueft

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-05-red-team-gibt-bei-abgelehnten-lesebefehlen-auf-und-meldet-di.md
      .\kit-melden.cmd ablegen  2026-10-05-red-team-gibt-bei-abgelehnten-lesebefehlen-auf-und-meldet-di.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-05-red-team-gibt-bei-abgelehnten-lesebefehlen-auf-und-meldet-di.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-45)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Acht Kaskaden, Harry und Marv sweepen nach jedem Lauf mit einem Fokus aus nummerierten
  Punkten.

## Was passiert ist

Marv wollte im Sweep die Diffs zweier Werkzeugdateien lesen, die zwei Fixe des Vorlaufs geändert
hatten. Ein Punkt seines Fokus nannte genau diese Auswertung. Die CLI lehnte drei Aufrufe ab, alle
drei stehen in `permission_denials` seines Logs:

- `cd <projekt> && git diff <von>..HEAD -- <datei1> <datei2>; grep …`
- `Set-Location <projekt>; git diff <von>..HEAD -- <datei1> <datei2>; Select-String …`
- `git -C <projekt> diff <von>..HEAD -- <datei1> <datei2>`

Die Allowlist erlaubt `Bash(git diff:*)`. `git diff <von>..HEAD -- <datei1> <datei2>` ohne `-C`
und ohne `cd` wäre durchgegangen, die Shell stand ohnehin in der Wurzel. Marv hat es nicht
versucht. In seinem `result` steht: Der Diff „blieb ungelesen, weil der Befehl Rückfrage verlangte
und ich nicht ausweichen wollte“. Seine Zeile `ABDECKUNG 4` für genau diesen Punkt lautet
trotzdem „geprüft, ohne Befund“. `redteam.ps1` meldete „Geprüft, keine neuen Funde … Sauber“, der
Abschlussbericht übernahm die Abdeckungszeile. Aufgefallen ist die Lücke nur, weil der Architekt
das `result` selbst gelesen hat.

Harry hatte im selben Lauf drei abgelehnte `cd …&&`-Ketten und kam über Read und Grep an dieselben
Stellen. Die Ablehnung allein ist also nicht das Problem, sondern die Lesart „nicht ausweichen“.

## Wo es steckt

- `team/redteam.ps1`, Prompt des Sweeps: „Lehnt die CLI ein Edit oder Write im Beutebuch oder im
  Test-Ordner ab, weiche NICHT auf Bash aus“. Für abgelehnte **Lesebefehle** sagt der Prompt
  nichts. Ein Modell überträgt das Ausweichverbot dann auf jeden abgelehnten Aufruf.
- `team/lib.psm1`, `team_allowed_tools`: Die Allowlist nennt die erlaubten Formen
  (`git diff:*`, `git log:*`, `git show:*`, Read, Grep, Glob), der Prompt nennt sie der Rolle nicht.
  Dass `git -C … diff` oder ein vorangestelltes `cd` daran scheitert, erfährt die Rolle erst durch
  die Ablehnung.
- `team/redteam.ps1`, Form der Abdeckungszeile (`Kit-BL-299`): `Fund HM-<Nr> | geprüft, ohne Befund
  | nicht geprüft — <Grund>`. Für „teilweise geprüft, diese Dateien blieben ungelesen“ gibt es keine
  Form, also wählt die Rolle „geprüft“.

## Warum das jede Installation trifft

Prompt, Allowlist und Abdeckungszeile kommen aus dem Kit. Jede Rolle, die beim Lesen einmal `cd`
oder `-C` benutzt, läuft in dieselbe Ablehnung, und jede, die das Ausweichverbot wörtlich nimmt,
lässt die Stelle liegen. Die Abdeckungszeile meldet sie dann als geprüft. Das ist derselbe
Fehlermodus wie bei den abgelehnten Schreibversuchen (`Kit-BL-292`): eine Lücke, die als sauberer
Sweep aussieht.

## Was ich schon versucht habe

Im Projekt steht seit diesem Lauf ein Satz im Grundauftrag beider Rollen (`TEAM_REDTEAM_AUFTRAG_*`
in `team.config.ps1`): Lehnt die CLI einen Lesebefehl ab, nimm die erlaubte Form (`git diff`,
`git log`, `git show` ohne `-C` und ohne `cd`), sonst Read, Grep und Glob; was trotzdem ungelesen
bleibt, nennt die Abdeckungszeile als ungelesen statt als geprüft. Ob das wirkt, zeigt erst der
nächste Sweep. Vorschläge fürs Kit:

1. Im Prompt von `redteam.ps1` neben dem Satz zu Edit/Write einen Satz zu Lesebefehlen, mit den
   erlaubten Formen aus `team_allowed_tools`.
2. Eine vierte Form der Abdeckungszeile, etwa `teilweise geprüft — ungelesen: <Dateien>`, und im
   Abschlussbericht dieselbe Hervorhebung wie bei „nicht geprüft“.
3. `kosten.py verweigert` meldet heute nur abgelehnte Schreibversuche im erlaubten Bereich. Eine
   Zeile „N Lesebefehle abgelehnt“ im Bericht des Sweeps würde den Menschen auf das `result`
   schicken, statt dass er es nur findet, wenn er es von sich aus liest.

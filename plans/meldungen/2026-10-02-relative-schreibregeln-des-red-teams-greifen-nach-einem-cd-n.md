# Relative Schreibregeln des Red Teams greifen nach einem cd nicht mehr, und der Sweep meldet trotzdem keine Funde

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-02-relative-schreibregeln-des-red-teams-greifen-nach-einem-cd-n.md
      .\kit-melden.cmd ablegen  2026-10-02-relative-schreibregeln-des-red-teams-greifen-nach-einem-cd-n.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-02-relative-schreibregeln-des-red-teams-greifen-nach-einem-cd-n.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-29)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Sechs Kaskaden sind gelaufen. Der Produktivcode liegt in einem Unterordner der Wurzel,
  Plan- und Testordner liegen in der Wurzel.

## Was passiert ist

Zwei Fehler, die erst zusammen Schaden anrichten.

**1. Die Schreibregeln hängen am Arbeitsverzeichnis der Shell.** Harry und Marv laufen mit
`--permission-mode default` und der Allowlist aus `team_allowed_tools`. Ihre Schreibregeln sind
relativ: `Edit(plans/**) Write(plans/**) Edit(tests/**) Write(tests/**)`. Im Sweep nach einer
Kaskade lehnte die CLI ihre Schreibversuche ab: Harry wollte nach `tests/` schreiben und das
Beutebuch ändern, Marv das Beutebuch ändern. Die Meldung lautete jeweils „Claude requested
permissions to write to … but you haven't granted it yet". Die CLI war Claude Code 2.1.285, am
Vortag aktualisiert. Der letzte Sweep ohne Ablehnung lief noch mit 2.1.283.

Eine Probe mit Haiku, `--permission-mode default` und derselben Allowlist, gestartet in der
Projektwurzel:
- ohne `cd`: `Write` nach `tests/` und `plans/` geht durch;
- nach einem erlaubten `cd <Unterordner> && cat …` wird `Write` nach `tests/` abgelehnt;
- nach einem `cd` zurück in die Wurzel geht es wieder durch.

Die relativen Regeln werden also gegen das aktuelle Arbeitsverzeichnis der Shell aufgelöst, nicht
gegen das Projekt. Wer im Sweep in den Ordner mit dem Produktivcode wechselt, um dort zu lesen,
verliert damit seine Schreibrechte. Ein zweiter Fall bleibt ungeklärt: Laut Transkript stand Marvs
Shell wieder in der Wurzel, als ein `Edit` mit absolutem Windows-Pfad abgelehnt wurde. Die Probe
mit seiner Reihenfolge lief durch.

**2. Der Sweep gilt trotzdem als sauber.** Beide Rollen hatten je zwei Funde. Sie beschrieben sie
vollständig, legten sie aber nur im `result` ihres Logs ab. `team/redteam.ps1` meldete
„Geprüft, keine neuen Funde … Sauber, nichts zu committen", die Fixphase „nichts zu tun" und der
Abschlussbericht „(keine Funde)". Das Log trug die Ablehnungen in `permission_denials`. Gelesen hat
sie niemand, bis der Architekt im Abschluss die Logs von Hand öffnete. Vier Funde wären sonst
verloren gewesen.

## Wo es steckt

- `team/lib.psm1`, `team_allowed_tools`: baut die Schreibregeln aus `TEAM_PLAN_ORDNER` und
  `TEAM_TEST_ORDNER` nur in relativer Form. Dieselbe Liste bekommt Axel (nur der Plan-Ordner).
- `team/redteam.ps1`: urteilt über einen Sweep nur nach dem Diff des Beutebuchs. Die Liste
  `permission_denials` im Ergebnis-JSON der Rolle wertet es nicht aus.
- Die Bash-Bahn führt vermutlich dieselbe Allowlist. Geprüft habe ich das nicht, dieses Projekt
  fährt nur die pwsh-Bahn.

## Warum das jede Installation trifft

Die Allowlist erzeugt das Kit für jede Installation. Jede Rolle mit Schreibregeln verliert sie,
sobald sie ihre Shell in einen Unterordner wechselt, und das ist bei Produktivcode in einem
Unterordner der Normalfall beim Lesen. Die Ablehnung ist für die Rolle sichtbar, für den Menschen
nicht: Der Bericht sagt „sauber", und die Funde stehen nur in einem Log, das niemand öffnet.

## Was ich schon versucht habe

**Lokale Umgehung, seit dem 2026-10-01 im Feld.** Sie verfällt beim nächsten `-Update`, das
`team/lib.psm1` überschreibt.
- `team_allowed_tools` holt die Schreibregeln aus einer neuen Hilfsfunktion `team_schreibregeln`.
  Sie gibt jede Regel zweimal aus, relativ und absolut. Die absolute Form ist
  `Edit(//<laufwerk>/<pfad-zum-projekt>/plans/**)`, unter Windows also mit kleinem Laufwerksbuchstaben
  und Schrägstrichen statt `C:\…`. Einschränkung: Ein Leerzeichen im Projektpfad verträgt die
  leerzeichengetrennte Liste in keiner der beiden Formen.
- Der Grundauftrag beider Red-Team-Rollen endet mit einem Satz: Lehnt die CLI ein Edit oder Write
  ab, weicht die Rolle nicht auf Bash oder PowerShell aus. Sie schreibt jeden Fundblock vollständig,
  samt Reproducer-Zeile, in ihre Abschlussantwort, und der Architekt trägt ihn ein.

**Belege.** Fünf Haiku-Proben in einem Klon mit derselben CLI: ohne `cd` erlaubt, nach `cd` in die
Wurzel erlaubt, nach `cd` in den Unterordner relativ abgelehnt und absolut erlaubt. Mit der
erzeugten Liste gingen nach `cd` in den Unterordner `Edit` am Beutebuch und `Write` nach `tests/`
durch. Der nächste echte Sweep am 2026-10-02 lief mit der Umgehung: Harry und Marv trugen je drei
Funde selbst ins Beutebuch ein, und `permission_denials` nannte nur abgelehnte Bash-Aufrufe, kein
Edit und kein Write. Die Team-Tests liefen danach mit einem bekannten, schon vorher roten Test und
sonst grün.

**Vorschläge fürs Kit**, in dieser Reihenfolge:
1. `team_allowed_tools` gibt die Schreibregeln absolut aus, zusätzlich zur relativen Form oder
   statt ihr. Dazu ein Team-Test, der beide Formen für Plan- und Testordner in der Liste findet.
   Ein Leerzeichen im Projektpfad bekommt eine klare Meldung, statt die Liste still zu zerlegen.
2. `team/redteam.ps1` liest `permission_denials` aus dem Ergebnis-JSON der Rolle. Steht dort ein
   `Edit` oder `Write`, gilt der Sweep nicht als sauber: Der Lauf meldet den abgelehnten
   Schreibversuch, und der Abschlussbericht sagt, dass Funde nur im `result` stehen können. Dasselbe
   gilt sinngemäß für Axel.
3. Den Satz über den Rückfall in die Abschlussantwort in die Red-Team-Briefings des Kits
   übernehmen, damit eine Ablehnung nie wieder Funde kostet, auch wenn 1 und 2 einmal versagen.

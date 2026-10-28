# Lokale Stufen im Team: Weg für eine Stufe, die ein Programm baut, und zwei Lücken, die sie sichtbar macht

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-28-lokale-stufen-im-team-weg-fuer-eine-stufe-die-ein-programm-b.md
      .\kit-melden.cmd ablegen  2026-10-28-lokale-stufen-im-team-weg-fuer-eine-stufe-die-ein-programm-b.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-28-lokale-stufen-im-team-weg-fuer-eine-stufe-die-ein-programm-b.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: Backlog des Feldprojekts, Einträge 11 und 12; Nachtrag zur Meldung vom 2026-10-27 („Ein Red-Team-Fund ändert über Franks Fix einen Vertragswert …“)
- **Art**: Lücke im Ablauf (Loop, Ledger-Prüfung, Konsistenz-Check) und in einer Regel (`CLAUDE.md`, Verifikationskette)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python. Ein Programm im Produktivcode lässt ein lokales Sprachmodell (32K-Fenster) einen Bauschritt machen: Auftrag samt roter Abnahmetests, Änderung, Smoke-Test, Commit. Dritte Kaskade, eine Stufe, erstmals von diesem Programm gebaut

## Was passiert ist

**1. Eine Stufe, die ein Programm baut, hat im Loop keinen Platz.** Die Stufe trug statt eines
Promise einen Block mit Bauauftrag (zu ändernde Datei, Abnahmetest). Der Mensch rief das Programm
von Hand vor der Vollautomatik; es baute im ersten Versuch und committete `feat(stufe1): …` mit
Trailern (Versuche, Sekunden, Token). Danach setzte der Mensch `.ralph-state` von Hand weiter,
Ralph hatte Feierabend, Harry und Marv sweepten bis zum lokalen Commit, Frank fixte drei Funde.
Das trug — aber an drei Nähten von Hand:

- Den Bau startet der Mensch, und er schaltet den Zustand weiter; der Loop kennt keine Stufe ohne
  Promise. Ein Promise braucht es dort auch nicht: Das Programm weiß selbst, ob die Tests grün
  sind (Exit 0 und ein neuer Commit).
- Die Baukosten sind lokal (Sekunden, Token), nicht USD. Eine Zeile mit 0,0000 USD gäbe sie
  falsch wieder; ohne Zeile meldet `--ledger-pruefen` im Closeout:
  `[WARNUNG] Kaskade 3: keine ralph-Zeile, obwohl eine roles-Zeile steht. Die Baukosten des Loops
  sind nicht gebucht (Kit-BL-4-Muster)` (Exit 4). Ein richtiger Zustand erscheint so in jedem
  Closeout einer solchen Kaskade als Warnung.
- Die Abnahmequelle liegt unter `plans/<plan>/stufe-<N>/tests/`. Der Konsistenz-Check meldet sie
  als „weder Team-Artefakt noch Bestand“ (`Kit-BL-237`); laut Guard dürften Harry und Marv sie
  ändern, nur ihr Prompt verbietet es. Jede weitere lokale Stufe bringt eine weitere.

**2. Grün in der Agenten-Sitzung, rot im Terminal des Menschen.** In den Sitzungen der
Agenten-CLI ist Strg+C für den Sitzungsprozess abgeschaltet, und jedes Kind erbt das. Eine
Lebensprüfung im Produktivcode nutzte `os.kill(pid, 0)`; unter Windows ist `0` der Wert von
`CTRL_C_EVENT`, der Aufruf schickt also ein Strg+C in die eigene Konsole. Die Suite war in jedem
Lauf aller Rollen grün. Im Terminal des Menschen brach der Smoke-Test bei 60 % ohne Ergebniszeile
ab, und pwsh beendete die ganze Befehlszeile mit Exit 1. Gefunden hat es erst eine Probe des
Architekten in einer eigenen Konsole mit eingeschaltetem Strg+C. Die Regel „Der Smoke-Test darf
keine Umgebung setzen, die die Doku nicht nennt“ greift hier nicht: Nicht der Befehl setzt die
Umgebung, sondern die Sitzung.

**3. Nachtrag: dasselbe Muster wie in der Meldung vom 2026-10-27, zweites Mal.** Ein Sweep-Fund
behauptete, was ein Befehl ausgibt (`git check-ignore` erkenne einen Ordner mit Muster `/ordner/*`
nicht), und kennzeichnete es korrekt als „nicht ausgeführt“. Frank setzte die Erwartung um: Der
Prüfpfad, den der Plan festlegte, wurde umgestellt, dazu ein Test. Die Gegenprobe im Closeout
zeigte: Der neue Test war schon vor dem Fix grün — die Behauptung stimmt nicht (Git 2.55 meldet
den Ordner als ignoriert). Diesmal harmlos, die Umstellung ändert nichts; aber wieder hat eine
ungeprüfte Annahme einen Planvertrag umgestellt, und erst die Gegenprobe des Architekten hat es
gezeigt.

## Wo es steckt

- Zu 1: der Loop (`ralph.sh`, Vollautomatik), `kosten.py ledger-pruefen`, der Konsistenz-Check
  in `team-status`, der Guard der Read-Only-Rollen.
- Zu 2: `CLAUDE.md`, Abschnitt „Projekt-Spezifika“, Absatz zur Verifikationskette.
- Zu 3: `CLAUDE.md`, Beutezug-Dreisatz Punkt 3 und Übergabe an Frank; Franks Briefing.

## Warum das jede Installation trifft

Zu 1: Jedes Projekt, in dem ein Programm statt eines Agenten eine Stufe baut, stößt auf dieselben
drei Nähte. Zu 2: Jede Installation auf Windows, deren Code ein Konsolenereignis auslösen kann,
prüft in den Rollen eine Umgebung, die der Mensch nicht hat. Zu 3: Die Regeln gelten in jedem
Projekt; der zweite Feldfall zeigt, dass die Gegenprobe im Closeout das einzige Netz ist.

## Was ich schon versucht habe

Im Projekt nichts an `team/` oder an den Regeln geändert — sie gehören dem Kit. Die lokale Stufe
lief von Hand, die Ledger-Warnung steht begründet im Abschluss-Protokoll, die Konsole wie im
Terminal des Menschen fährt der Architekt im Closeout selbst (eigene Konsole, Strg+C wieder
eingeschaltet, darin pwsh). Vorschläge, ohne Anspruch:

- **Programm-Stufe:** Eine Stufe mit Bauauftrag ruft ein konfigurierbares Programm statt
  `team_claude()`; Exit 0 plus neuer Commit ist die Quittung, jeder andere Exit hält den Loop mit
  dem Bericht des Programms an.
- **Ledger:** eine Einheit oder Kennzeichnung „lokal“; `--ledger-pruefen` nimmt eine fehlende
  Bau-Zeile hin, wenn alle Stufen der Kaskade Programm-Stufen waren.
- **Abnahmequellen** unter `plans/` als bekannte Art im Konsistenz-Check, für Harry und Marv
  per Guard gesperrt.
- **Konsole des Menschen:** ein Werkzeug, das den Smoke-Test einmal in einer frischen Konsole
  mit eingeschaltetem Strg+C fährt (Windows: neue Konsole, `SetConsoleCtrlHandler(NULL, FALSE)`),
  etwa im Closeout oder in `team-test`; dazu ein Satz in der Verifikationskette, dass der Zustand
  der Konsole zur Umgebung gehört.
- **Zu 3:** Frank fährt seinen neuen Test vor dem Commit gegen den Stand ohne Fix; ist er dort
  schon grün, prüft er nichts, und die Prämisse des Funds geht zurück an den Architekten.

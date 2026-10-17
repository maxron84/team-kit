# Ralph baut acht Stufen auf einem Plan, der nicht committet ist - gewarnt wird erst beim Red Team

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-16-ralph-baut-acht-stufen-auf-einem-plan-der-nicht-committet-is.md
      ./kit-melden.sh ablegen  2026-10-16-ralph-baut-acht-stufen-auf-einem-plan-der-nicht-committet-is.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-16-ralph-baut-acht-stufen-auf-einem-plan-der-nicht-committet-is.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-12
- **Art**: Lücke im Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; dritte Kaskade, ein Mensch und die Rollen in einem Arbeitsbaum

## Was passiert ist

Die Vollautomatik startete, während die Ausgabe der Aushärtung noch
uncommittet im Arbeitsbaum lag. Die aktive Plan-Datei, auf die `.ralph-plan`
zeigte, war **untracked**. Dazu waren `roadmap-skizzen.md`, `backlog.md` und
`beutebuch.md` geändert; im Beutebuch stand ein Fund des Architekten aus der
Sichtung.

- **Ralphs Phase warnte nicht.** Sie lief acht Stufen lang, 23 Minuten, mit
  acht Commits. Die erste Warnung erschien beim Start von Harry:

  ```
  [guard] WARNUNG: Der Arbeitsbaum ist beim Rollenstart NICHT sauber:
    plans/beutebuch.md
    plans/roadmap-skizzen.md
    plans/team-kaskade-N-….md
  [guard] Diese Pfade werden der Rolle nicht angelastet, solange sie unverändert bleiben.
  [guard] Zwei schreibende Instanzen auf einem Arbeitsbaum sind trotzdem unzulässig — bitte committen.
  ```

  Dieselbe Warnung stand danach vor jedem Frank-Lauf. Der Lauf ging jedes Mal
  weiter.
- **Ralph hat es in Stufe 1 selbst quittiert:** „`plans/backlog.md` hatte schon
  Änderungen des Architekten, die noch nicht committet waren. Sie sind mit im
  Commit.“ Und: „Für die Klon-Probe habe ich kurz `git stash` benutzt.“
  - Die untracked Plan-Datei trägt danach die Änderungszeit genau dieses
    Moments. Der Stash hat sie also mitgenommen.
  - Für die Dauer der Probe lag der aktive Plan nicht im Arbeitsbaum.
- **Harrys Sweep-Commit** heißt „2 neue Funde“, trägt aber drei Fundblöcke.
  Der dritte war der uncommittete Fund des Architekten; er kam unter Harrys
  Botschaft ins Git.
- **Nach dem Lauf** lag die Plan-Datei weiterhin nicht im Git. Der Closeout hat
  sie nachgetragen.

Schaden ist keiner entstanden, alles ließ sich zuordnen. Das ging aber nur,
weil Ralph es in seine Quittung geschrieben hat.

## Wo es steckt

- **`ralph.sh` (Entrypoint):** Die Stufe zieht nur `team_stufen_schnappschuss`
  (BL-274), ohne die Warnung aus `team_guard_begin`. Die Warnung haben
  `team/redteam.sh` und `frank.sh`. Es fehlt also ausgerechnet die Phase, die
  als erste und am längsten läuft.
- **Keine Planprüfung beim Start:** Weder `vollautomatik.sh` noch `ralph.sh`
  prüft, ob die Plan-Datei aus `.ralph-plan` im Index liegt und dem HEAD
  entspricht. Die Prüfung wäre billig und eindeutig:
  `git ls-files --error-unmatch <plan>` und `git diff --quiet HEAD -- <plan>`.
- **`team/prompts/rolle-ralph.md`** verbietet `git add -A` (BL-274), sagt aber
  nichts zu `git stash`. Ein Stash nimmt fremde, uncommittete Arbeit aus dem
  Baum. Schlägt das `pop` fehl, liegt sie im Stash, wo niemand sie sucht.

## Warum das jede Installation trifft

Jede Aushärtung endet mit Handarbeit des Menschen: Commit, Buchung, Zeiger,
Start. Fällt der Commit aus, startet die Vollautomatik trotzdem.

Den Rest kann der Fremdfilter nicht lösen; BL-271 benennt das als Fall (a):
Eine Datei, die Mensch und Rolle beide anfassen, gilt als die der Rolle.
Verhindern lässt sich das nur noch beim Start. Die Meldung vom 2026-10-12
(„Vollautomatik startet trotz ungebuchter Planungssitzung der Kaskade“) zielt
auf dieselbe Startphase. Eine Startprüfung trüge beide Fälle.

## Was ich schon versucht habe

Projektseitig hat der Closeout Plan und Roadmap nachcommittet. Die
Scharfschalt-Sequenz startet künftig nur bei sauberem Baum.

Vorschlag fürs Kit:

1. **Planprüfung beim Start.** Die Vollautomatik bricht ab, wenn die Plan-Datei
   aus `.ralph-plan` untracked ist oder vom HEAD abweicht; ebenso `ralph.sh`
   beim Einzelaufruf. Die Meldung nennt den Pfad und den Commit-Befehl. Ein
   Plan, der nicht im Git liegt, ist nach dem Lauf als Grundlage der Commits
   nicht mehr belegbar.
2. **Warnung beim Start der Ralph-Phase,** einmal, aus `team_guard_begin`.
3. **`rolle-ralph.md`:** „Kein `git stash`: Fremde, uncommittete Arbeit bleibt,
   wo sie ist.“ Für eine Klon-Probe genügt
   `git ls-files -z -co --exclude-standard`, das den Arbeitsbaum so kopiert,
   wie er ist.

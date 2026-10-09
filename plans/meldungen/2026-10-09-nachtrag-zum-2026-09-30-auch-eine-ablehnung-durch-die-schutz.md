# Nachtrag zum 2026-09-30: auch eine Ablehnung durch die Schutzregeln des Modells laeuft als Timeout/Limit in den API-Fallback

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-09-nachtrag-zum-2026-09-30-auch-eine-ablehnung-durch-die-schutz.md
      .\kit-melden.cmd ablegen  2026-10-09-nachtrag-zum-2026-09-30-auch-eine-ablehnung-durch-die-schutz.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-09-nachtrag-zum-2026-09-30-auch-eine-ablehnung-durch-die-schutz.md   # sonst: Pull Request

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
- **Lage des Projekts**: Bestand, Windows, pwsh-Bahn, Python mit Electron-Oberfläche; Loop-Rollen Abo-first mit hinterlegtem API-Schlüssel. Die Kaskade baute eine Sperre gegen private Schlüssel in einer Ablage, das Red Team prüfte also Sicherheitscode.

## Was passiert ist

Dies ist ein Nachtrag zur Meldung vom 2026-09-30
(`2026-09-30-abgelaufene-abo-anmeldung-faellt-als-limit-in-den-api-fallba.md`).
Dort war die Ursache eine abgelaufene Anmeldung. Hier ist es eine **zweite
Ursache**, die im Log genauso aussieht.

Marvs Sweep startete im Abo und endete nach 7 Turns, 44 Sekunden und
0,47 USD. Das Rohlog trägt `is_error: true` und im Feld `result`:

> API Error: Sonnet 5's safeguards flagged this message. […] can sometimes
> flag legitimate cybersecurity work. Apply to the Cyber Verification Program
> to reduce these interruptions. […] Details: `[cyber]`

Der Loop meldete wie im ersten Fall:

> [marv] Abo-Aufruf fehlgeschlagen (Timeout/Limit/429?) — einmaliger API-Fallback.

Der Fallback fuhr denselben Auftrag über die API zu Ende: 53 Turns,
**5,86 USD echt abgerechnet**, zwei Funde.

## Wo es steckt

Dieselbe Stelle wie im ersten Fall: `team/lib.psm1`, `team_claude`, der Zweig
mit dem Text *Abo-Aufruf fehlgeschlagen (Timeout/Limit/429?)*. Auch nach dem
Update vom 2026-10-08 unverändert.

## Warum das jede Installation trifft

Anders als die abgelaufene Anmeldung hat der Fallback hier **geholfen**. Der
Fehler ist deshalb nicht der Fallback, sondern die Meldung:

1. **Sie nennt die falsche Ursache.** Wer *Timeout/Limit* liest, sucht das
   Kontingent. Die Ablehnung durch die Schutzregeln steht nur im Rohlog.
2. **Es trifft gerade die Rollen, deren Arbeit Sicherheitscode ist.** Harry
   und Marv lesen Angriffswege, und jede Kaskade mit Sicherheitsbezug kann
   denselben Sweep wieder auslösen. Ob der API-Weg dann durchkommt, ist nicht
   zugesichert. Hier kam er mit demselben Auftrag durch.
3. **Die Kostenachse verrutscht still**, wie im ersten Fall: Die Zeile steht
   danach als `abo/api`, ohne Grund.

## Vorschlag

Den Vorschlag des ersten Falls verallgemeinern: **den Grund aus `result` in
die Zeile schreiben**, die der Mensch liest. Beide Wortlaute sind stabil
(`Failed to authenticate` bzw. `safeguards flagged` mit `[cyber]`). Daraus
folgen zwei verschiedene Behandlungen:

- **Anmeldung abgelaufen:** anhalten (siehe erster Fall).
- **Ablehnung durch Schutzregeln:** den Fallback behalten, aber benannt
  (*Ablehnung durch die Schutzregeln (cyber) — einmaliger API-Fallback*), im
  Abschlussbericht getrennt zählen und in `TEAM.md` einen Satz zu dem
  Programm ergänzen, das die Meldung selbst nennt, für Projekte, deren Red
  Team regelmäßig Sicherheitscode prüft.

## Was ich schon versucht habe

Nichts am Kit geändert. Im Projekt nur verbucht: Der Sweep lief über die API,
die Kosten stehen dort.

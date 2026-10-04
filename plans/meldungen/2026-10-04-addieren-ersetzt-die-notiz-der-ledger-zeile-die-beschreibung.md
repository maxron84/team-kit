# --addieren ersetzt die Notiz der Ledger-Zeile, die Beschreibung des Laufs geht verloren

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-04-addieren-ersetzt-die-notiz-der-ledger-zeile-die-beschreibung.md
      .\kit-melden.cmd ablegen  2026-10-04-addieren-ersetzt-die-notiz-der-ledger-zeile-die-beschreibung.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-04-addieren-ersetzt-die-notiz-der-ledger-zeile-die-beschreibung.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-44)
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Sieben Kaskaden sind gelaufen, die achte ist geplant. Das Ledger hat rund 25 Zeilen,
  die Architekten-Zeile jeder Kaskade entsteht aus mehreren Sitzungen.

## Was passiert ist

Im Abschluss einer Kaskade kam ein Nachlauf mit `--akteur-abschluss roles … --addieren` auf die
Rollen-Zeile. Danach trug die Zeile nur noch die Notiz des Nachtrags. Die Beschreibung des Laufs
(„Rollen: K7 …, Harry und Marv je 3 Sweeps, Frank …“) war weg, Zahlen und Quellen stimmten. Der
Architekt hat die Prosa von Hand wiederhergestellt; `--ledger-pruefen` meldet so etwas nicht, denn
es prüft Beträge gegen Rohlogs, keinen Text.

Im Ledger des Projekts stehen danach:

- **Elf Zeilen, die nur die Notiz der letzten Buchung tragen**: die Architekten-Zeilen aller sieben
  Kaskaden, die Rollen-Zeilen von drei und eine Bau-Zeile. Bei einer Architekten-Zeile, die aus fünf
  bis acht Sitzungen zusammenkommt, beschreibt die Notiz danach nur noch die letzte, etwa „Rest
  Abschluss K5 … nachgemessen in der Sitzung zur Auswahl von K6 (addiert auf Bestand 237.1844 USD,
  auth abo)“. Die Transkripte stehen weiter in der JSON-Spalte, was in den Sitzungen geschah, nicht.
- **Vier Zeilen mit doppeltem Vorspann**: „Rollen: Rollen: …“ und „Bau: Bau: …“. Das passiert,
  wenn die übergebene Notiz selbst schon mit dem Vorspann beginnt, wie es das Briefing für die
  beiden Notizen des Rollen-Abschlusses nahelegt.

Das Briefing des Architekten nennt die Notizen „die einzige Prosa-Spur je Ledger-Zeile“. Genau
diese Spur geht beim Normalfall „Folgesitzung an derselben Kaskade“ verloren.

## Wo es steckt

- `team/tools/kosten.py`, `akteur_abschluss`, innere Funktion `merge_fn`: `notiz_summe` entsteht aus
  `notiz_sauber` (der neuen Notiz) und dem Zusatz „(addiert auf Bestand …, auth …)“. Die Notiz der
  Altzeile in `felder` wird nicht gelesen.
- `team/tools/kosten.py`, `rollen_abschluss`, innere Funktion `merge_fn`: dasselbe mit
  `notiz_voll`.
- `team/tools/kosten.py`, `rollen_abschluss`: `notiz_voll = f"{vorspann}: {notiz_sauber} — …"`,
  ohne zu prüfen, ob `notiz_sauber` schon mit `vorspann` beginnt (`ROLLEN_VORSPANN`).

Stand: Kit-Update vom 2026-10-04, die Stellen stehen dort unverändert.

## Warum das jede Installation trifft

`--addieren` ist laut Briefing der Normalfall für eine Folgesitzung an derselben Kaskade, und
jeder Nachlauf einer Rolle kommt so ins Ledger. Jede Installation, die eine Kaskade in mehr als
einer Sitzung plant oder abschließt, verliert so die Beschreibung aller Sitzungen außer der
letzten. Nichts meldet das: Beträge, Quellen und `--ledger-pruefen` bleiben stimmig.

## Was ich schon versucht habe

Nichts am Kit. Im Projekt hat der Architekt die Prosa der Rollen- und Bau-Zeile einer Kaskade von
Hand nachgezogen. Für die Architekten-Zeilen ist die alte Prosa nur noch in der Git-Historie des
Ledgers. Vorschläge:

1. Beim Addieren die alte Notiz behalten und die neue anhängen, etwa
   `<alt>; <neu> (addiert auf Bestand …)`. Wird die Zeile zu lang, ist das ein eigener Befund.
   Abschneiden wäre wieder stiller Verlust.
2. Den Vorspann nur setzen, wenn die Notiz nicht schon mit ihm beginnt.
3. Den vorhandenen Test schärfen: `test_modus_bleibt_hinter_beiden_texten_erkennbar` in
   `team/tests/test_bl34_zwei_notiztexte.py` addiert „Nachlauf Frank“ auf „Sweeps“ und verlangt
   nur „addiert auf Bestand“ in der Notiz. Verlangt er zusätzlich „Sweeps“, wird er heute rot. Für
   den Vorspann fehlt ein Test mit einer Notiz, die schon mit „Rollen:“ beginnt.

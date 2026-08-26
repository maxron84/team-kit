# Meldungen aus dem Feld

Hier landen Meldungen fremder Nutzer als **je eine Datei** — angelegt von
`./kit-melden.sh senden` im meldenden Projekt, angekommen als Pull Request.

**Warum eine Datei je Meldung und kein Eintrag in `../backlog.md`:** Der
Backlog ist eine Datei, und jede Meldung hinge an derselben Stelle. Zwei
gleichzeitige Meldungen wären ein garantierter Merge-Konflikt, und der
`BL-n`-Nummernraum wäre ein Wettlauf zwischen Leuten, die voneinander nichts
wissen. Die Nummer vergibt der Maintainer beim Triage.

**Der Weg einer Meldung:**

1. Sie kommt als PR an und wird hier abgelegt — wörtlich, wie gemeldet.
2. Beim Triage bekommt sie eine `BL-n` und eine Zeile in
   [`../backlog.md`](../backlog.md), die auf sie zeigt.
3. Ist sie abgetragen, steht das im [CHANGELOG](../../CHANGELOG.md) und im
   [Archiv](../backlog-archiv.md). Die Datei hier bleibt als Beleg liegen.

Eine Meldung wird **nicht** umgeschrieben. Was der Melder gesehen hat, ist der
Wert; die Einordnung passiert im Backlog, nicht in seinem Text.

---

## Der Owner meldet anders — ohne Pull Request

Der oben beschriebene Weg gilt fuer **fremde** Nutzer. Der Owner betreibt
selbst Feldprojekte, und fuer ihn ist ein Pull Request gegen das **eigene**
Repo Leerlauf: Er wuerde seine eigene Meldung reviewen und mergen. Entscheid
des Owners, 2026-08-26:

> Pull Requests sollen nur von **fremden** Kit-Nutzern kommen. Vom Owner
> reichen **normale Backlog-Eintraege**.

**Konkret fuer ein Feldprojekt des Owners:**

1. Meldung wie gewohnt anlegen (`neu`) und redaktionell pruefen (`pruefen`) —
   die Datei bleibt der Beleg, woertlich wie gesehen.
2. Sie **direkt hier** ablegen und im Aufwasch eine `BL-n`-Zeile in
   [`../backlog.md`](../backlog.md) schreiben, die auf sie zeigt. Der
   Triage-Schritt entfaellt, weil Melder und Maintainer dieselbe Person sind.
3. **Kein `senden`, kein Zweig, kein PR, kein Issue.**

**Warum das eine Regel braucht und nicht dem Augenmass ueberlassen bleibt:**
Ohne sie erzeugt jedes Owner-Feldprojekt PRs und Zweige am eigenen Repo. Das
Ergebnis waere eine Vorgangs-Historie, die keine Vorgaenge abbildet — der Owner
nennt es *„Data Pollution"*. Die Nummernvergabe uebernimmt dabei der Owner
selbst und **prueft sie gegen das Archiv**, nicht nur gegen
[`../backlog.md`](../backlog.md); nach einer Rotation liegen belegte Nummern
sonst ausserhalb der Sichtweite (siehe `BL-188`).

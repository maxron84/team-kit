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

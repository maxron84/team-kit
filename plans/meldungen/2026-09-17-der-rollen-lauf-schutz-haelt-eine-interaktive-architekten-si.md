# Der Rollen-Lauf-Schutz haelt eine interaktive Architekten-Sitzung fuer einen Rollen-Lauf

- **Bezug**: BL-90
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python-Dienst plus
  Electron-Oberfläche, 24 gebaute Kaskaden, rund 390 Transkripte in der Ablage.

## Was passiert ist

Das Update bringt den Schutz aus `BL-251` mit: `sitzung-messen` zählt die echten
Nutzer-Prompts eines Transkripts und warnt, wenn es die Signatur eines headless
gefahrenen Rollen-Laufs trägt — **genau ein** Nutzer-Prompt. **Der Schutz ist
richtig und dieses Projekt hat ihn selbst gemeldet.** Er schließt eine Lücke,
die hier real aufgetreten ist.

**Beim ersten Closeout nach dem Update hat er einen Fehlalarm ausgelöst.**
Die Architekten-Sitzung, die den Closeout fährt, bekam wörtlich:

    ! Dieses Transkript hat genau EINEN echten Nutzer-Prompt — das ist die
      Signatur eines headless gefahrenen ROLLEN-Laufs, nicht die einer
      interaktiven Sitzung.
    NICHT buchen: Dieser Lauf traegt die Signatur eines Rollen-Laufs …

**Die Messung ist korrekt, die Schlussfolgerung nicht.** Es war eine interaktive
Sitzung. Der Mensch hatte **einen** umfangreichen Auftrag erteilt (sinngemäß
*„Update verifizieren, danach die Kaskade abschließen"*), und die Sitzung hat
ihn danach autonom abgearbeitet — Verifikation, drei Heilungen, Abschlussdoc,
Backlog, Meldungen. Ein Prompt, mehrere Stunden Arbeit, in diesem Fall rund
8 USD Abo-Gegenwert.

**Der Schaden ist die Umkehrung des ursprünglichen Fundes.** `BL-251` verhindert
eine **Doppel**buchung; hier führt derselbe Mechanismus zu einer **Nicht**buchung
— und damit zu genau der strukturellen Lücke, vor der das Architekten-Briefing
an anderer Stelle ausdrücklich warnt (*„Ohne diesen Schritt sind meine Kosten
strukturell unerfasst"*). Wer der Meldung folgt, bucht den Closeout nicht.

## Wo es steckt

- `geteilt/tools/kosten.py`, in der Heuristik von `echte_nutzer_prompts` bzw.
  der Auswertung, die daraus `NICHT buchen` ableitet.
- Der Kommentar dort nennt die Eichung selbst: *an 379 Transkripten nachgezählt
  … die 1 gehörte ausschließlich Rollen-Läufen — kein Grenzfall.*

**Die Eichung ist nicht falsch, sie ist zu schmal.** Der Grenzfall existiert; er
war in der Eichmenge nur nicht vertreten, weil die interaktiven Sitzungen dieses
Projekts bis dahin im Dialog geführt wurden — mehrere Prompts, mehrere Runden.
Sobald der Mensch einen Auftrag in **einem** Prompt erteilt, fällt die Sitzung
in dieselbe Klasse wie ein Rollen-Lauf.

## Warum das jede Installation trifft

Die Heuristik steht in einem Werkzeug von `geteilt/` und entscheidet über den
Kostenabschluss jeder Installation. Der Fehlalarm tritt nicht bei einer exotischen
Bedienung auf, sondern bei der **sparsamsten**: Ein Mensch, der seinen Auftrag
vollständig in einem Prompt formuliert, ist der Normalfall, auf den
Agenten-Bedienung zuläuft — nicht die Ausnahme. Die Klasse wird also wachsen,
nicht schrumpfen.

**Vorschlag:** Die Prompt-Zahl allein trennt die beiden Fälle nicht. Was sie
trennt, steht ebenfalls im Transkript und ist robuster:

1. **Die Herkunft des Auftrags.** Ein Rollen-Lauf bekommt seinen Auftrag aus dem
   Rollen-Prompt des Kits — dessen Wortlaut kennt das Kit selbst und kann darauf
   prüfen. Ein menschlicher Auftrag sieht anders aus.
2. **Der Berechtigungsmodus.** Rollen laufen headless unter
   `bypassPermissions`; eine interaktive Sitzung in aller Regel nicht.
3. **Hilfsweise die Tonlage der Warnung.** Solange die Unterscheidung unsicher
   ist, sollte aus `NICHT buchen` ein *„prüfe, ob dieser Lauf über
   `--rollen-abschluss` schon gebucht ist"* werden. Die Falschrichtung ist
   asymmetrisch: Eine Doppelbuchung fällt beim Ledger-Prüfen auf, eine
   ausgelassene Buchung fällt **nirgends** auf — das ist der Kern des
   ursprünglichen Fundes.

## Was ich schon versucht habe

Kein lokaler Patch — der Fund sitzt in einem Werkzeug des Kits und hätte die
bekannte Verfallszeit; derselbe Closeout hat am selben Tag drei solche
Verfallsfälle aufräumen müssen.

**Der Behelf, der hier weiterhin trägt**, stammt aus der ursprünglichen Meldung:
im Closeout nicht die Projektablage messen lassen, sondern das eigene Transkript
über seinen **Pfad** benennen. Dann greift die Warnung nicht, und die Zahl
stimmt. Als Gedächtnisregel im Projekt hinterlegt.

**Gefunden wurde der Fall nur durch Ausführen** — im Diff des Updates war nichts
zu sehen, die Zeilen lesen sich vollkommen plausibel. Das ist die Art Fund, die
ein Quelltext-Review strukturell nicht liefert.

# Gegenlesen von Fixer-Fixes mit Gegenprobe und Mutationsprobe

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-09-28-gegenlesen-von-fixer-fixes-mit-gegenprobe-und-mutationsprobe.md
      .\kit-melden.cmd ablegen  2026-09-28-gegenlesen-von-fixer-fixes-mit-gegenprobe-und-mutationsprobe.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-09-28-gegenlesen-von-fixer-fixes-mit-gegenprobe-und-mutationsprobe.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: ein Backlog-Eintrag des Feldprojekts (dort BL-10)
- **Art**: Idee / Verbesserung
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins — vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows, pwsh-Bahn, Spielskript-Stack mit Prüfwerkzeug in
  Python. Drei Kaskaden sind gelaufen. Auf die dritte folgte eine lange Handprobe des Stakeholders
  mit 45 Frank-Fixen außerhalb des Loops.

## Was passiert ist

Nach der dritten Kaskade lief außerhalb des Loops eine enge Schleife:
1. Der Stakeholder testet im Spiel.
2. Der Architekt ordnet die Beobachtung ein und schreibt den Fund.
3. Frank fixt.
4. Der Architekt liest gegen.

Es waren 45 Fixe, jeder im ersten Versuch, jeder mit grünem Reproducer und grüner Suite. Sechs davon
hatten trotzdem eine Lücke, die kein Test zeigte. Daraus wurden fünf Nachschliff-Funde. Gefunden hat
sie das Gegenlesen gegen die Zusagen des Funds, zusammen mit drei billigen Proben:

1. **Gegenprobe:** Den Stand vor dem Fix in ein Wegwerf-Verzeichnis holen
   (`git archive <vor-commit> | tar -x -C <tmp>`), die neuen Tests hineinkopieren und laufen
   lassen. Sie müssen rot sein, sonst prüfen sie nichts.
2. **Mutationsprobe:** Im Wegwerf-Verzeichnis mit dem Stand nach dem Fix jede Zusicherung
   einzeln brechen: den Fehler wieder einbauen, eine Reihenfolge vertauschen oder eine Bedingung
   entfernen. Dann die ganze Suite laufen lassen. Für jede Mutation muss der zuständige Test rot
   werden.
3. **Probe an der Wirklichkeit:** Ein Werkzeug mit echter Eingabe laufen lassen und über den
   Aufruf, den die Doku nennt, einschließlich umgeleiteter Ausgabe.

Die fünf Fälle, ohne Projektdetails:

- Ein Fix verlängerte den Prüfbereich eines bestehenden Tests. Der suchte danach per `find` nur das
  erste Vorkommen und prüfte eine Reihenfolge nur noch für das erste von zwei Objekten. Die
  Mutationsprobe am zweiten Objekt blieb grün.
- Ein Fund verlangte „Y erst anlegen, wenn X gilt". Der Fix legte Y sofort an und schaltete es nur
  später scharf, und der Test prüfte nur das Scharfschalten. Aufgefallen ist das beim Lesen gegen
  die Zusage. Eine Kopie mit dem richtigen Ablauf zeigte dann, dass genau zwei Tests eine überholte
  Struktur festschrieben.
- Zwei sichtbare Zusagen eines Funds, ein Zwischenstatus und eine Verzögerung, standen nicht in
  seiner Reproducer-Anforderung. Beim Bau fielen sie still durch, und zwar in zwei verschiedenen
  Fixen.
- Ein Test prüfte einen Log-Filter mit selbst gebautem Eingabeformat. Im echten Log steht vor dem
  Schlüsselwort ein Sonderzeichen (U+27A5), und dort erkannte der Filter die Zeile nicht.
- Ein Test prüfte die Filterfunktion, nicht den dokumentierten Aufruf auf der Kommandozeile. Der
  stürzte ab, sobald die Ausgabe umgeleitet wurde (cp1252, `UnicodeEncodeError`). Er endete dann
  mit dem Exit-Code, der sonst „Befund" bedeutet.

Die letzten beiden sind genau der Fehlermodus, den `CLAUDE.md` unter „Die Verifikationskette darf
sich den Erfolg nicht selbst einrichten" beschreibt. Die Regel stand im Prompt und hat trotzdem nicht
gegriffen, denn der Test las sich regelkonform.

Einmal legte der Architekt außerdem selbst fest, was der Nutzer sieht, weil ihm der Stakeholder einen
Parameter überlassen hatte. Der Stakeholder verwarf das Ergebnis nach dem Bau. Das kostete zwei
Fixer-Runden und eine dritte für den Umbau. Eine Rückfrage in drei Sätzen hätte es vorher geklärt.

## Wo es steckt

- `team/prompts/rolle-architekt.md`: Das Briefing kennt das Gegenlesen von Fixen außerhalb des
  Loops nicht. Es verlangt nur, vor jedem Entwurf die Frank-Fix-Zeilen abzugleichen. Im Feld hat der
  Architekt jeden Fix gegengelesen, weil es sonst niemand tut. Eine Methode dafür steht nirgends, und
  ohne Methode liest man Diffs und Testnamen. Die Tests sind aber per Konstruktion grün, weil Franks
  Dreisatz sie grün verlangt. Vorschlag: Gegenlesen jedes Fixes mit Gegenprobe und Mutationsprobe,
  bei Werkzeugen dazu die Probe an der Wirklichkeit.
- Dieselbe Datei, dort, wo der Architekt Funde schreibt. Zwei Sätze fehlen:
  - Die Reproducer-Anforderung nennt jede sichtbare Zusage des Funds.
  - Sie nennt Zusicherungen, keine Testnamen. „Test X bleibt grün" steht nur dort, wo X zum neuen
    Ablauf passt. Im Feld schrieb genau so eine Auflage die alte Struktur fest und zwang Frank,
    einen überholten Ablauf stehen zu lassen.
- Dieselbe Datei: Legt ein Fund fest, was der Nutzer sieht, legt der Architekt den Ablauf vor dem
  Fixer-Lauf dem Stakeholder in Klartext vor. Das gilt auch, wenn ihm ein Parameter überlassen ist.
- Optional `team/prompts/rolle-frank.md`: ein Satz dazu, Testeingaben aus einer echten Quelle zu
  nehmen (etwa eine Fixture aus einem echten Log) und den Aufruf so zu testen, wie die Doku ihn
  nennt.

## Warum das jede Installation trifft

Die Fixer-Schleife außerhalb des Loops hat keinen Red-Team-Sweep, das einzige Gegengewicht ist das
Gegenlesen des Architekten. Im Feld hätten ohne die Proben 6 von 45 Fixen (13 %) als erledigt
gegolten, alle mit grüner Suite. Die Proben kosten je einen Suitenlauf, lokal zwei Sekunden. Ein
Nachschliff-Fix kostete 0,6 bis 2,0 USD und ohne die Proben eine weitere Runde Handprobe beim
Stakeholder.

## Was ich schon versucht habe

Der Architekt hat die Proben ab der Mitte der Handprobe bei jedem Fix gefahren:
- die Gegenprobe gegen den Vor-Commit,
- je Zusicherung eine Mutation in einer Kopie,
- bei Werkzeugen den echten Eingang und den echten Aufruf über eine Pipe.

Alle fünf Nachschliff-Funde kamen aus diesem Gegenlesen, bevor der Stakeholder den Fix im Spiel
sah. Im Feld steht die Arbeitsweise als Backlog-Eintrag. Ein Fix am Kit ist nicht nötig, es geht um
eine Ergänzung der Briefings.

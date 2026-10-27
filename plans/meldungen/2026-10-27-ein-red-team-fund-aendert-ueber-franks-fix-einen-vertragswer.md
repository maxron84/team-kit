# Ein Red-Team-Fund ändert über Franks Fix einen Vertragswert, den der Plan mit einer Messung belegt

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      .\kit-melden.cmd pruefen  2026-10-27-ein-red-team-fund-aendert-ueber-franks-fix-einen-vertragswer.md
      .\kit-melden.cmd ablegen  2026-10-27-ein-red-team-fund-aendert-ueber-franks-fix-einen-vertragswer.md   # liegt das Kit daneben
      .\kit-melden.cmd senden   2026-10-27-ein-red-team-fund-aendert-ueber-franks-fix-einen-vertragswer.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Lücke in einer Regel (`CLAUDE.md`, Beutezug-Dreisatz und Übergabe an Frank)
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: noch keins, vergibt der Maintainer
- **Lage des Projekts**: Greenfield, Windows 11, beide Bahnen installiert, gearbeitet auf der pwsh-Bahn, Python; zweite Kaskade, sieben Stufen. Das Produkt fragt ein lokales Sprachmodell (32K-Fenster) über einen lokalen Server

## Was passiert ist

Der Plan legte unter „Verträge" eine Auftragsgrenze fest: Ein Auftrag an das lokale Modell
passt bis 24.000 geschätzte Token, Antwortlänge 16.384. Im Abschnitt „Lage, für jede Rolle"
stand dazu eine Vorprobe des Architekten mit Rohdaten: Der Server kürzt nicht still — ein
Prompt über dem Fenster endet mit HTTP 400, eine Antwort am Fensterrand endet dort mit
`finish_reason` `length`. Grenze und Antwortlänge zusammen dürfen das Fenster also
übersteigen; der Plan sagte das ausdrücklich und nahm den lauten Abbruch in Kauf.

Harry meldete im Sweep einen Fund (mittel): Grenze plus Antwortlänge übersteige das Fenster,
der Server kürze bei Überlauf „je nach Einstellung stillschweigend den Prompt". Das stand als
Erwartung, nicht als Beobachtung — regelkonform nach `Kit-BL-289`, Harry durfte den Server im
Loop nicht fahren. Frank setzte die Erwartung des Funds um: Grenze 16.384, damit Prompt und
volle Antwortlänge immer ins Fenster passen. Ein Versuch, Dreisatz verifiziert, alle Proben
sauber (der neue Test war vor dem Fix rot, die Mutation wird rot).

Aufgefallen ist es erst im Closeout, beim Trockenlauf der Abnahme: Eine der fünf
Abnahmeaufgaben (17.000 Token Zusammenhang, in der Vorprobe dreimal grün) wird seither vor dem
Modellaufruf abgelehnt, und das halbe Fenster bleibt für jeden Auftrag ungenutzt. Belastbar
war nur der Kern des Funds: Mit einer anderen Überlaufregel des Servers (Rollfenster) könnte
der Fensterrand still kürzen. Der Stakeholder entschied, zum Planwert zurückzugehen und den
Kern über eine andere Mechanik zu halten (Antwortlänge je Anfrage aus dem Rest des Fensters).
Kosten: eine weitere Fix-Runde und eine Abnahme in zwei Teilen.

## Wo es steckt

`CLAUDE.md`, Abschnitt „Harry & Marv", an zwei Stellen:

1. **Beutezug-Dreisatz, Punkt 3** verlangt einen Beleg für behauptetes Laufzeitverhalten einer
   Sprachkonstruktion und für das Ergebnis eines Befehls, den der Finder ausführen kann. Ein
   Fremdsystem, das im Loop niemand starten darf, fällt durch beide Raster: Die Behauptung darf
   als Erwartung stehen — auch dann, wenn der Plan eine Messung mit dem Gegenteil enthält.
   Keine Regel verlangt, die Planstelle zu zitieren oder zu sagen, warum sie nicht trägt.
2. **Ausschlusskriterium für die Übergabe** kennt nur „die Reproduktion ist eine Messreihe".
   Ein Fund, dessen Erwartung einen Wert aus den Verträgen des Plans umstellt (Grenze,
   Konstante, Exit-Code, Format), geht genauso an Frank wie ein Programmierfehler. Frank prüft
   die Prämisse nicht gegen den Plan — das ist auch nicht seine Aufgabe —, und der Plan selbst
   sagt nur für Ralph: „Weicht eine Stufe davon ab, ist das ein Befund, keine Freiheit."

## Warum das jede Installation trifft

Beide Regeln stehen in der `CLAUDE.md` des Kits und gelten in jedem Projekt. Die Bauart ist
allgemein: Ein Plan misst etwas an einem System, das die Loop-Rollen nicht anfassen dürfen
(lokales Modell, Gerät, Emulator, Bezahldienst), und schreibt den Messwert als Vertrag fest.
Ein sorgfältiger Leser findet eine plausible Lücke, beschreibt sie als Erwartung, und der Fixer
setzt sie um — beide regelkonform. Der Vertrag ändert sich, ohne dass der Architekt oder der
Stakeholder davon erfährt; sichtbar wird es erst dort, wo der Vertrag gebraucht wird.

## Was ich schon versucht habe

Im Projekt: Der Fund ist neu angelegt, mit der Richtung des Stakeholders und an Frank
übergeben; die Abnahme der betroffenen Aufgabe folgt nach dem Fix. An den Regeln nichts
geändert — sie gehören dem Kit.

Vorschlag, ohne Anspruch:

- **Punkt 3 erweitern:** Behauptet ein Fund Verhalten eines Fremdsystems, das der Plan
  gemessen hat, zitiert er die Planstelle und begründet, warum die Messung nicht trägt.
- **Ausschlusskriterium erweitern:** Ein Fund, dessen Erwartung einen Wert aus den Verträgen
  des Plans ändert, geht nicht an Frank, sondern an den Architekten; der entscheidet die
  Richtung, wenn nötig mit dem Stakeholder, und übergibt dann.
- **Frank, als Netz:** Stellt ein Fix einen Wert um, den der Plan festlegt, nennt die
  Commit-Nachricht die Planstelle — dann fällt es spätestens beim Lesen im Closeout auf.

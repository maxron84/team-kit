# Kopplungs-Obergrenze im Architekten-Briefing hat keine Messvorschrift und ist damit inert

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-08-24-kopplungs-obergrenze-im-architekten-briefing-hat-keine-messv.md
      ./kit-melden.sh senden   2026-08-24-kopplungs-obergrenze-im-architekten-briefing-hat-keine-messv.md

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Art**: Fehler am Kit
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter. Drei
  Kaskaden gebaut, rund 4 000 Zeilen Produktiv- und Testcode, alle Rollen im
  Abomodus.

## Was passiert ist

Das Briefing des Architekten nennt als Erfahrungswert für den Stufenschnitt:

> Der Kostentreiber ist die **Zahl gleichzeitig zu erfüllender Kopplungen**,
> nicht die Schwierigkeit des Gedankens — ab etwa drei gekoppelten Ansprüchen
> teile ich die Stufe.

Beim Aushärten der dritten Kaskade (acht Stufen) habe ich diese Auflage
umgesetzt, indem ich die **Umsetzungs-Punkte** je Stufe gezählt und in **allen
acht** Stufen auf exakt drei gehalten habe. Formal war die Regel damit
lückenlos erfüllt.

Im Lauf kostete eine der acht Stufen dann das Vierfache des Medians und brach
die Vollautomatik am Soft-Cap ab:

| | geänderte Bestandsdateien | Zeilen | Turns | Kosten |
|---|---|---|---|---|
| Median der übrigen sieben Stufen | 3 | 359 | 51 | 1,88 USD |
| die Ausreißer-Stufe | **8** | **942** | **132** | **7,70 USD** |

Beide Stufen hatten **drei** Umsetzungs-Punkte.

## Wo es steckt

`team/prompts/rolle-architekt.md`, Abschnitt „Beim Ansetzen der Stufen gelten
drei Erfahrungswerte" — der zweite Erfahrungswert. Die Regel nennt eine Zahl
(„etwa drei"), aber **nicht, woran sie zu messen ist**. Der Architekt zählt
deshalb das, was er ohnehin schreibt: Aufzählungspunkte.

Das ist eine Metrik, die der Planschreiber durch **Umformatieren** erfüllt.
Drei Aufzählungspunkte können einen Einzeiler oder einen halben Bildschirm
meinen; die Zahl ist eine Formatierungsentscheidung, keine Eigenschaft der
geplanten Arbeit. Eine Obergrenze, die sich durch Umformatieren einhalten
lässt, begrenzt nichts.

## Warum das jede Installation trifft

Die Regel steht im ausgelieferten Rollen-Briefing und ist damit in jeder
Installation dieselbe. Sie ist außerdem **selbstbestätigend**: Der Architekt,
der sie befolgt, sieht in seinem eigenen Plan überall Dreien und schließt
daraus, dass er richtig geschnitten hat. Der Widerspruch fällt erst im
Closeout auf, wenn die Kosten je Stufe nebeneinanderstehen — also nachdem der
Lauf bezahlt ist. Bei uns hat er zusätzlich den Lauf zerschnitten (Soft-Cap
mitten in der Kaskade), was einen zweiten Aufruf und einen zweiten
Pro-Lauf-Deckel nach sich zog.

Die Regel selbst ist richtig — Kopplung **ist** der Kostentreiber, das
bestätigt unser Zahlenbild. Ihr fehlt nur der Satz, der sie messbar macht.

## Was ich schon versucht habe

Im Closeout die tatsächlich vorhersagekräftigen Größen aus den Rohlogs gegen
den Plan gehalten. Beide korrelieren deutlich besser mit Turns und Kosten als
die Zahl der Aufzählungspunkte:

1. **Zahl der Bestandsdateien, die eine Stufe ändern muss** (nicht: neu
   anlegt). Bei uns: Median 3, Ausreißer 8.
2. **Umfang in Zeilen.** Unterhalb ~550 Zeilen kosteten die Stufen 1,5–1,8
   USD, darüber stieg es überproportional (565 → 2,69; 606 → 3,30;
   942 → 7,70).

Größe 1 kennt der Architekt beim Aushärten näherungsweise, weil er ohnehin
weiß, welche Dateien eine Stufe anfasst — sie taugt daher als Messvorschrift,
Größe 2 eher als Plausibilitätsprobe.

**Vorschlag für die Regel:** den Erfahrungswert um einen Satz ergänzen, der
sagt, woran gezählt wird — etwa: *„Gezählt werden die **bestehenden Dateien**,
die die Stufe ändern muss, nicht die Aufzählungspunkte, die ich schreibe. Mehr
als fünf → teilen."* Zusätzlich hilfreich wäre eine Zeile im
Abschluss-Protokoll-Gerüst (Abschnitt 2), die Kosten je Stufe **gegen** diese
Zahl stellt; dann schließt sich die Rückkopplung am selben Ort, an dem die
Regel gilt.

**Lokal umgesetzt** ist bisher nur die Selbstverpflichtung im
Abschluss-Protokoll dieser Kaskade („je Stufe nenne ich die Bestandsdateien,
die sie ändern muss; mehr als fünf → teilen"). Das ist Prosa in einem
Projektdokument und überlebt kein `--update`; die Regel selbst habe ich nicht
angefasst.

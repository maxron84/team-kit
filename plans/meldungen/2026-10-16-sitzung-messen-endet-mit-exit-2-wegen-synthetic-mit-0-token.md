# sitzung-messen endet mit Exit 2 wegen <synthetic> mit 0 Token - das Briefing liest das als nicht buchen

<!--
  Meldung an das T.E.A.M.-Kit. Ausfüllen, dann:

      ./kit-melden.sh pruefen  2026-10-16-sitzung-messen-endet-mit-exit-2-wegen-synthetic-mit-0-token.md
      ./kit-melden.sh ablegen  2026-10-16-sitzung-messen-endet-mit-exit-2-wegen-synthetic-mit-0-token.md   # liegt das Kit daneben
      ./kit-melden.sh senden   2026-10-16-sitzung-messen-endet-mit-exit-2-wegen-synthetic-mit-0-token.md   # sonst: Pull Request

  REDAKTIONSREGEL: Diese Datei landet in einem ÖFFENTLICHEN Repo. Sie soll
  einen Fehler am KIT beschreiben, nicht dein Projekt. Keine absoluten Pfade,
  keine Benutzer- oder Rechnernamen, kein Produktivcode. Wenn du dein Projekt
  erwähnen musst, beschreibe seine LAGE (Plattform, Bahn, Greenfield oder
  Bestand, ungefähre Größe) — das Kit führt seine Feldbelege aus genau diesem
  Grund unter `Feld A`…`Feld D` statt unter Namen. `pruefen` sucht die
  häufigsten Ausrutscher, aber es liest nicht mit.
-->

- **Bezug**: BL-13
- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: bash
- **Plattform**: linux
- **Feldkürzel**: noch keins vergeben
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Python; dritte Kaskade

## Was passiert ist

Im Closeout war eine Aushärtungs-Sitzung nachzubuchen; `sitzungen-pruefen`
nannte sie „NICHT gebucht“. `sitzung-messen <pfad>` druckte, gekürzt:

```
  ! Modell '<synthetic>' steht nicht in der Preistabelle — seine Token sind in der Summe NICHT enthalten.
  ...
  GESAMT: 19.8467 USD
  Buchen: team-status --akteur-abschluss architekt abo 19.8467 <domaene> "<notiz>" --transkript … --bis …
```

Dann endete es mit **Exit 2**. Das Transkript enthält zwei Einträge mit
`"model": "<synthetic>"`, beide mit 0 in jedem Token-Feld. Die Summe ist also
vollständig, und der Exit-Code sagt das Gegenteil.

`<synthetic>` ist kein Modell. Die Agenten-CLI trägt den Namen für Nachrichten
ein, die sie selbst erzeugt, ohne API-Aufruf, etwa Abbruch- oder
Fehlermeldungen. Er kann in jedem längeren Transkript stehen.

## Wo es steckt

- **`team/tools/kosten.py`, Verb `sitzung-messen`:** endet mit
  `return 2 if (schief or unbekannt) else 0`. Ein unbekanntes Modell zählt
  dort wie eine ungeeichte Preistabelle, auch ohne einen einzigen Token.
  `sitzungen-pruefen` nennt dieselben Einträge „ohne Preis, nicht im Betrag:
  <synthetic>“.
- **`team/prompts/rolle-architekt.md`:** „Meldet es ‚Preistabelle stimmt nicht
  mehr‘, ist die Zahl **ungeeicht** und ich buche sie nicht … Exit `2` heißt
  genau das.“ Wer nach dem Exit-Code handelt, bucht die Sitzung nicht. Das ist
  genau die Lücke, gegen die `Kit-BL-165` und `Kit-BL-197` gebaut sind.

## Warum das jede Installation trifft

Jedes Transkript kann `<synthetic>`-Einträge tragen, und der Architekt misst je
Kaskade mindestens zwei Sitzungen. In diesem Projekt war in drei Kaskaden
hintereinander die Aushärtung beim Start nicht gebucht. Ob Exit 2 dabei
mitgespielt hat, ist nicht belegt. Exit-Code und Briefingsatz zusammen laden
aber genau dazu ein.

## Was ich schon versucht habe

Ich habe die Token der beiden `<synthetic>`-Einträge nachgezählt (0), trotz
Exit 2 gebucht und das im Abschluss-Doc begründet.

Vorschlag fürs Kit:

- Einträge ohne Token nicht als unbekanntes Modell zählen, oder `<synthetic>`
  mit Preis 0 in die Tabelle aufnehmen.
- Exit 2 nur, wenn wirklich Token ohne Preis bleiben; die Meldung nennt dann
  deren Zahl.

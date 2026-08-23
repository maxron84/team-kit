# Backlog — {{PROJEKTNAME}}

Aufgaben, die keine eigene Kaskade rechtfertigen: kleine Verbesserungen,
technische Schulden, Ideen. Frank trägt hier ein, was ihm beim Fixen auffällt,
aber nicht in seinen Auftrag gehört.

> **Fund am T.E.A.M. selbst statt an diesem Projekt?** Dann gehört er
> **zusätzlich** ins Kit zurück — sonst trifft derselbe Fehler jede weitere
> Installation, und dieses Projekt repariert ihn bei jedem Update aufs Neue.
> Erkennungsmerkmal: Der Fehler steckt in `team/`, in einem Entrypoint
> (`{{RUF}}*{{ENDUNG}}` in der Wurzel) oder in einer Regel aus
> `CLAUDE.md`/`TEAM.md` — nicht in deinem Produktivcode.
>
> ```
> {{RUF}}kit-melden{{ENDUNG}} neu --titel "Kurz, was schiefging"
> {{RUF}}kit-melden{{ENDUNG}} pruefen        # Redaktionsprüfung
> {{RUF}}kit-melden{{ENDUNG}} senden <datei> # Pull Request — fragt vorher
> ```
>
> **Status hier auf „ans Kit gemeldet (…)" setzen**, damit sichtbar bleibt,
> ob der Rückkanal wirklich bedient wurde. Die drei bisher schwersten
> Kit-Fehler (`BL-1`, `BL-4`, `BL-5`) kamen alle auf diesem Weg — und alle
> drei lagen zwischenzeitlich nur im Feldprojekt.
>
> **Ein Eintrag mit fertigem Fix im Feld hat eine Verfallszeit** — sie endet
> beim nächsten `--update`. `BL-42` wurde gemeldet, blieb liegen, und das
> Update überschrieb den lokalen Fix; dasselbe Projekt musste denselben Fund
> ein zweites Mal melden (`BL-58`). Deshalb legt `kit-melden` die Meldung
> immer auch als Datei ab: verloren geht sie dann nicht.

| Nr | Was | Woher | Status |
|---|---|---|---|

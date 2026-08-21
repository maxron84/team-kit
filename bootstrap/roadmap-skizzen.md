# Roadmap-Skizzen — {{PROJEKTNAME}}

Ungehärtete Stränge. Ziel, grober Umfang, Bezug, offene Fragen — **ohne**
Stufennummern, **ohne** Cap (Kaskaden-Planungsregel 1).

Erst wenn der Strippenzieher einen Strang zur nächsten Kaskade freigibt, härtet
der Architekt ihn zu einem eigenen Plan `ralph-kaskade-N-….md` aus.

---

## Skizze 1: Verifikationsfähigkeit herstellen

> **Vom Starterkit angelegt.** Steht unten bei „Stand" noch ein TODO, ist dieser
> Strang die **erste Kaskade** — vor jedem Feature. Ist der Befehl bereits
> gesetzt, kann die Skizze ersatzlos gestrichen werden.

- **Ziel**: Ein einziger Befehl sagt verlässlich, ob das Projekt heil ist.
- **Stand**: `{{SMOKE_TEST}}`
- **Umfang**: So klein wie möglich — baut/parst das Projekt, laufen die
  vorhandenen Tests, sind die offensichtlichen Verweise intakt. Kein
  Vollausbau, kein Coverage-Ziel.
- **Bezug**: Ralph schließt **keine** Stufe ohne grünen Smoke-Test ab, Frank
  verifiziert keinen Fix. Bis dieser Strang gebaut ist, arbeitet das gesamte
  Team ohne Sicherheitsnetz und meldet das in jedem Prompt.
- **Danach**: Den Befehl in `{{KONFIG}}` bei `TEAM_SMOKE_TEST` eintragen —
  er wirkt sofort in allen Rollen, ohne Neuinstallation.
- **Offene Fragen**: Welcher Befehl deckt am meisten ab, ohne langsam zu werden?

---

## Skizze 2: <dein erster fachlicher Strang>

- **Ziel**: <was am Ende funktionieren soll>
- **Umfang**: <grob>
- **Bezug**: <warum jetzt>
- **Offene Fragen**: <was vor der Aushärtung geklärt sein muss>

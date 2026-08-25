# Soft-Cap ueber den Hard-Cap heben schaltet den Airbag still ab

- **Art**: Fehler am Kit
- **Kit-Version**: 2.12.0
- **Bahn**: bash
- **Plattform**: linux
- **Lage des Projekts**: Greenfield, Linux, bash-Bahn, Dart/Flutter (Android-Ziel),
  dritte Kaskade, ~1.900 Zeilen Produktivcode

## Was passiert ist

Eine UI-Stufe kostete 7,70 USD und wurde vom Soft-Cap (Default 5) abgebrochen,
nachdem der Commit bereits lag:

```
Ralph: Stufe 16 hat 7.6966568000 USD gekostet.
SOFT-CAP UEBERSCHRITTEN (Ralph Stufe 16): 7.70 USD >= Soft-Cap 5.00 USD.
Ralph endete mit Fehler (1) — Vollautomatik stoppt, Mensch gefragt.
```

Der Stakeholder entschied daraufhin, den Soft-Cap projektweit auf 20 USD zu
heben — genau der Weg, den `CLAUDE.md` selbst nennt („Uebersteuerung je
Lauf/Rolle bleibt moeglich (`TEAM_ROLE_BUDGET_USD` … fuer die Schwellen)").

**Haette ich nur das getan, was verlangt war, waere der Airbag von Frank und
Axel still verschwunden.** `TEAM_ROLE_BUDGET_USD=20` bei unveraendertem
`TEAM_ROLE_HARDCAP_USD=10` heisst nicht „der Hard-Cap greift jetzt zuerst",
sondern „der Hard-Cap greift nie mehr". Aufgefallen ist es nur, weil ich vor der
Aenderung in `team_budget_check()` nachgesehen habe. Nichts im Kit haette
gewarnt: kein Hinweis beim Start, keine Zeile im Statusbericht, keine Meldung
beim Ueberschreiten.

## Wo es steckt

`team/lib.sh`, Funktion `team_budget_check()`:

```python
if hard is not None and hard > soft and cost >= hard:
    ... sys.exit(3)   # HARD-CAP
if cost >= soft:
    ... sys.exit(2)   # SOFT-CAP
```

Die Bedingung `hard > soft` ist als Rueckwaertskompatibilitaet gedacht und im
Kopf der Funktion auch so dokumentiert („der neue Zustand 3 tritt nur auf, wenn
ein sinnvolles hard-limit (> soft-limit) uebergeben wird"). Sie hat aber eine
zweite, undokumentierte Wirkung: Sobald ein Projekt den Soft-Cap ueber den
Hard-Cap hebt, faellt Zustand 3 lautlos aus.

Fuer Ralph, Harry und Marv ist das harmlos — sie rufen ohne Hard-Limit auf und
behandeln Zustand 2 selbst als hart. Fuer Frank und Axel ist es der ganze
Unterschied: Sie behandeln Zustand 2 ausdruecklich als **weich** (Hinweis, kein
Rollback, Fix bleibt gueltig — so gewollt seit `HM-32`). Ohne Zustand 3 haben
die beiden iterierenden Rollen, fuer die der Hard-Cap ueberhaupt erfunden
wurde, keine Obergrenze mehr.

Beteiligt ist auch die Regeltextseite: `CLAUDE.md` beschreibt Soft- und
Hard-Cap als zwei unabhaengig uebersteuerbare Zahlen („`TEAM_ROLE_BUDGET_USD` /
`TEAM_ROLE_HARDCAP_USD` fuer die Schwellen") und nennt die Kopplung nicht.
Wer nur die Regeldatei liest — also jede Rolle, denn sie liegt im Systemprompt —
haelt das Heben einer der beiden Zahlen fuer eine vollstaendige Handlung.

## Warum das jede Installation trifft

Der Fehler steckt in `team/lib.sh` und in einer Regel aus `CLAUDE.md`, nicht in
Produktivcode.

Er trifft besonders zuverlaessig, weil der Auslöser der Normalfall ist: Der
Kit-Default 5 USD ist fuer UI-Arbeit knapp, das Anheben des Soft-Caps ist der
dokumentierte Weg, und der Wunsch lautet in der Praxis „hebe den Soft-Cap", nie
„hebe beide Caps". Jede Installation, die den Soft-Cap ueber 10 hebt, verliert
dabei den Hard-Cap — und merkt es erst, wenn Frank oder Axel in eine
Endlosschleife laufen, also genau in dem Fall, fuer den der Airbag da ist.

Dazu kommt: `Kit-HM-32` hat den Soft-Cap eingefuehrt, weil ein zu tiefer Cap
bezahlte Arbeit per Rollback wegwirft und die Kosten VERVIELFACHT. Der Rat
„lieber grosszuegig ansetzen" steht im Kit selbst — er fuehrt also direkt in
diese Falle.

## Vorschlag

Drei Moeglichkeiten, aufsteigend im Aufwand:

1. **Klemmen statt ignorieren**: Ist `hard <= soft`, dann `hard = soft`
   verwenden. Der Airbag geht nie verloren; er faellt im schlechtesten Fall mit
   dem Soft-Cap zusammen. Nachteil: fuer Frank/Axel entfaellt damit still das
   weiche Fenster — das waere derselbe Fehler in der anderen Richtung.
2. **Lautstark meldern** (bevorzugt): Beim Sourcen der Konfiguration einmal
   pruefen und, wenn `TEAM_ROLE_HARDCAP_USD <= TEAM_ROLE_BUDGET_USD`, eine
   Warnung ausgeben, die die Folge benennt — nicht „Werte inkonsistent", sondern
   „Hard-Cap ist wirkungslos, Frank und Axel laufen ohne Obergrenze". Dazu eine
   Zeile im Statusbericht, damit der Zustand sichtbar bleibt und nicht nur
   einmal durchrauscht.
3. **Ein Verhaeltnis statt einer zweiten Zahl**: den Hard-Cap als Faktor auf den
   Soft-Cap definieren (Default 2,0) und die absolute Zahl nur als
   Uebersteuerung behalten. Dann kann er per Konstruktion nicht darunter
   rutschen. Groesserer Eingriff, aber die Klasse Fehler verschwindet.

Unabhaengig von der Wahl: Die Kopplung gehoert in den Regeltext. Ein Satz
genuegt — „wer den Soft-Cap hebt, muss den Hard-Cap darueber halten, sonst
schaltet er ihn ab" — an der Stelle, an der `CLAUDE.md` die beiden Zahlen als
uebersteuerbar beschreibt.

## Was ich schon versucht habe

Nichts umgangen, sondern lokal beides gehoben: `TEAM_ROLE_BUDGET_USD=20` und
`TEAM_ROLE_HARDCAP_USD=40` in `team.config.sh`, also das Verhaeltnis 2:1 der
Kit-Defaults erhalten. Gegengeprobt durch Sourcen der Konfiguration
(`soft=20 hard=40`).

Dazu die Kopplung im lokalen Regeltext festgehalten — an beiden Stellen, an
denen `CLAUDE.md` die Caps nennt (Axel-Sektion und `## Kostenkontrolle`),
mitsamt der Begruendung, warum der Hard-Cap mitwandern muss.

**Der lokale Teil an `team.config.sh` ist unkritisch** — das ist die
Projektkonfiguration, sie ueberlebt ein `--update`. **Der Teil an `CLAUDE.md`
hat die bekannte Verfallszeit** (`BL-42`/`BL-58`): Er wird beim naechsten
`install.sh --update` ueberschrieben, und dann steht die Kopplung nirgends mehr,
waehrend die Konfiguration sie weiter voraussetzt. Genau deshalb diese Meldung.

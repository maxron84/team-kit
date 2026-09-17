# Beutebuch — Harry & Marv

Jeder Fund des Read-Only Red Teams landet hier (Beutezug-Dreisatz, siehe
[CLAUDE.md](../CLAUDE.md)). Finder ≠ Fixer: Übergabe an Frank.

**Status-Kette**: `offen` → `an Frank übergeben` → (bei Scheitern)
`an Axel übergeben` → `Fix-Plan liegt vor` → `erledigt (Frank-Fix, <commit>)`

## Vorlage

```markdown
### HM-<Nr> — <Kurztitel>
- **Angreifer**: Harry | Marv
- **Schweregrad**: kritisch | hoch | mittel | klein
- **Status**: offen
- **Reproschritte**:
  1. …
- **Erwartung**: …
- **Realität**: …
- **Reproducer-Test**: `{{TEST_ORDNER}}test_hm<nr>_<stichwort>.py`
```

> Diesen Vorlage-Block **nicht löschen**. Harry und Marv richten ihre Funde
> daran aus; ohne ihn divergieren die Formate ab dem zweiten Sweep und die
> Zustandsmaschine findet die Status-Zeilen nicht mehr.

> **Ein neuer Fundblock wird ans ENDE geschrieben, nie zwischen zwei
> bestehende** (`Kit-BL-254`). Im Feld landete ein regelkonformer Beifang-Fund
> mitten im Block seines Vorgängers — zwischen dessen vorletztem Absatz und
> seiner `Reproducer-Test`-Zeile. Danach endete der fremde Fund **ohne**
> Pflichtzeile, der neue trug am Ende eine **fremde**, kein Zeichen ging
> verloren, und der Diff sah aus wie Routine.
>
> **Kein Guard kann das sehen** — er urteilt über Schreibzonen, und die Lage
> eines Anhangs ist eine Frage der *Struktur*, nicht des Pfades. Die Folge ist
> dieselbe wie bei einer fehlenden `Reproducer-Test`-Zeile: Der Substanz-Anker
> bricht, und Franks regelkonformer Fix wird still zurückgerollt.
>
> **Gegenprobe, wenn doch etwas verrutscht ist:**
> `python3 team/tools/beutebuch.py lint` **ohne Fundnummer** prüft jeden Block,
> `--alle` bezieht das Archiv mit ein. Nach einer Reparatur die **Multimenge** der
> Zeilen vorher/nachher vergleichen, nicht den Diff — der zeigt einen
> verschobenen Block als gelöscht plus neu.

> **Die `Reproducer-Test`-Zeile ist Pflicht — und der Pfad gehört in Backticks.**
> Zwei Regeln, die zusammen gelten müssen, sonst wirkt keine von beiden:
>
> 1. **Immer ausfüllen**, auch wenn die Datei **noch nicht existiert**. Der
>    Eintrag ist keine Quittung über getane Arbeit, sondern eine
>    **Reservierung**: Er sagt Frank, wie seine Testdatei heißen soll.
>
>    **Zulässig ist auch der Pfad einer BESTEHENDEN Datei** — dann, wenn der
>    Nachweis dorthin gehört. Bei einer **wiederkehrenden** Zusicherung
>    (Versionsstände, Schema-Versionen, Sperrklinken, Manifest- und
>    Konfigurationszusagen) ist das der Normalfall, und wer den Fund schreibt,
>    weiß in aller Regel, ob es dort schon eine Datei gibt. Der Substanz-Anker
>    trägt beides: Ihm genügt **irgendeine** backtick-referenzierte Datei im
>    Diff. Frank darf die Zeile später auf eine bestehende Datei umbiegen und
>    quittiert das im Fundblock (`Kit-BL-216`) — steht hier von vornherein die
>    richtige Datei, erspart das ihm die Wahl zwischen zwei Auflagen, die er
>    sonst nur mit einem Duplikat erfüllen kann.
> 2. **Immer in Backticks.** Der Substanz-Anker `team_diff_beruehrt_fund`
>    besteht nur, wenn Franks Diff eine im Fund-Block **backtick-referenzierte**
>    Datei berührt; `DATEI_RE` liest ausschließlich Backtick-Pfade. Ein Pfad
>    ohne Backticks ist für den Anker unsichtbar.
>
> **Warum das keine Formalie ist:** Eine neue Testdatei ist per Definition nie
> vorab referenziert. Ohne diese Zeile wird Franks regelkonform benannter Fix
> systematisch **zurückgerollt** — bei grünem Smoke-Test und gültigem Promise,
> also ohne jedes Fehlersignal. Im Feld kostete genau das an einem einzigen Fund
> 9 Frank-Versuche, 3 Axel-Akten und 12,00 USD, ohne dass eine Zeile Code
> überlebte. Beim nächsten Fund stand die Zeile — der Fix ging in **einem**
> Versuch durch.

## Funde
